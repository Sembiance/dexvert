#!/usr/bin/env python3
# Vibe coded by Codex
"""Decode Fujitsu Movie RIFF/FJMV files. See fujitsuMovie.txt."""
import argparse
import json
import math
from pathlib import Path
import struct
import sys

class FormatError(ValueError):
    pass
class Unsupported(FormatError):
    pass

def require(ok, message):
    if not ok:
        raise FormatError(message)

def u16(b, p=0):
    return struct.unpack_from('<H', b, p)[0]
def u32(b, p=0):
    return struct.unpack_from('<I', b, p)[0]
def words(b):
    return list(struct.unpack('<%dH' % (len(b)//2), b))

class Reader:
    def __init__(self, data):
        self.data, self.pos = data, 0
    def take(self, n):
        require(0 <= n <= len(self.data)-self.pos, 'Truncated codec operand stream')
        p=self.pos; self.pos+=n
        return self.data[p:self.pos]
    def byte(self):
        return self.take(1)[0]
    def word(self):
        return u16(self.take(2))
    def dword(self):
        return u32(self.take(4))

PARTITIONS={1:(8,8),2:(8,4),3:(4,8),5:(4,4),6:(4,2)}
def avg555(a,b):
    return (((a&0x7bdf)+(b&0x7bdf))>>1)|0x421

def decode92(data,w,h,palette,reference,initial=None):
    n=w*h//64
    require(len(data)>=n+2,'Truncated Fujitsu92 header')
    size=u16(data,n)
    require(n+2+size<=len(data),'Truncated Fujitsu92 primary stream')
    r=Reader(data[n+2:n+2+size]); secondary=data[n+2+size:]; nibble=0
    out=list(initial) if initial is not None else [0]*(w*h)
    pending=[]
    def fill(x,y,rw,rh,color):
        for yy in range(y,y+rh):
            out[yy*w+x:yy*w+x+rw]=[color]*rw
    for bi,mode in enumerate(data[:n]):
        bx=(bi%(w//8))*8; by=(bi//(w//8))*8; base=by*w+bx
        nextpending=[]
        if mode==0:
            for y in range(8):
                out[base+y*w:base+y*w+8]=[palette[v] for v in r.take(8)]
        elif mode%10 in PARTITIONS and mode//10 in (0,1,2):
            rw,rh=PARTITIONS[mode%10]
            for x in range(bx,bx+8,rw):
                for y in range(by,by+8,rh):
                    v=r.byte()
                    if mode>=20:
                        fill(x,y,rw,rh,palette[v]); continue
                    dx=(v>>4)&7; dy=v&7
                    if v&128: dx=-dx
                    if v&8: dy=-dy
                    if mode<10: dy-=rh+7
                    source=out if mode<10 else reference
                    for yy in range(rh):
                        p=((by if mode<10 else y)+yy+dy)*w+(bx if mode<10 else x)+dx
                        require(0<=p and p+rw<=w*h,'Motion vector outside image')
                        out[(y+yy)*w+x:(y+yy)*w+x+rw]=source[p:p+rw]
        elif mode==28:
            require(nibble//2<len(secondary),'Missing subdivision nibble')
            flags4=(secondary[nibble//2]>>(4 if nibble%2==0 else 0))&15; nibble+=1
            flags2=r.word()
            for q,(x,y) in enumerate(((0,0),(0,4),(4,0),(4,4))):
                if flags4&(8>>q):
                    fill(bx+x,by+y,4,4,palette[r.byte()])
                else:
                    for t,(xx,yy) in enumerate(((0,0),(0,2),(2,0),(2,2))):
                        if flags2&(0x8000>>(q*4+t)):
                            fill(bx+x+xx,by+y+yy,2,2,palette[r.byte()])
                        else:
                            for v in range(2):
                                for u in range(2):
                                    out[(by+y+yy+v)*w+bx+x+xx+u]=palette[r.byte()]
        elif mode in (35,42,55):
            bits= {35:2,42:3,55:1}[mode]
            rw,rh=(8,4) if mode==42 else (4,4)
            tiles=[(x,y) for x in range(0,8,rw) for y in range(0,8,rh)]
            maskbytes=rw*rh*bits//8
            masks=[int.from_bytes(r.take(maskbytes),'little') for _ in tiles]
            for (x,y),mask in zip(tiles,masks):
                pal=[palette[v] for v in r.take(1<<bits)]
                for yy in range(rh):
                    for xx in range(rw):
                        out[(by+y+yy)*w+bx+x+xx]=pal[mask&((1<<bits)-1)]; mask>>=bits
        elif mode in (91,92):
            flags=r.dword() if mode==92 else 0
            for y in range(8):
                for x in range(y%2,8,2):
                    out[base+y*w+x]=palette[r.byte()]
            bit=31
            for y in range(8):
                for x in range(1-y%2,8,2):
                    p=base+y*w+x
                    if flags&(1<<bit): out[p]=palette[r.byte()]
                    elif x==7: nextpending.append(y)
                    else: out[p]=avg555(out[p-1] if p else 0,out[p+1])
                    bit-=1
        else:
            raise Unsupported('Unknown Fujitsu92 block mode %d'%mode)
        for row in pending:
            p=base+row*w-1
            out[p]=avg555(out[p-1],out[p+1])
        pending=nextpending
    return out, (r.pos,size,(nibble+1)//2,len(secondary))

RSHIFT=(-20,-16,-14,-13,-11,-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,0,0,1,2,3,4,5,6,7,8,9,10,11,13,14,16,20)
GRSHIFT=(20,17,15,13,12,10,9,8,7,6,5,4,3,2,1,0,0,-1,-2,-3,-4,-5,-6,-7,-8,-9,-10,-12,-13,-15,-17,-20)
BSHIFT=(-25,-21,-18,-16,-15,-13,-11,-10,-9,-8,-6,-5,-4,-3,-2,-1,1,2,3,4,5,6,8,9,10,11,13,15,16,18,21,25)
GBSHIFT=(10,8,7,6,6,5,4,4,3,3,2,2,2,1,1,0,0,-1,-1,-2,-2,-2,-3,-3,-4,-4,-5,-6,-6,-7,-8,-10)
def clip5(x): return max(0,min(31,x))
YUV_LUT=[((clip5(y+GRSHIFT[v])//2+clip5(y+GBSHIFT[u])//2)<<10)|(clip5(y+RSHIFT[v])<<5)|clip5(y+BSHIFT[u]) for u in range(32) for v in range(32) for y in range(32)]

def decode93(data,w,h,reference,selector=1,chroma=None,frame=1):
    r=Reader(data); sizes=[r.dword() for _ in range(5 if selector else 3)]
    skip=r.take(sizes[0]); auxiliary=r.take(sizes[1]); stream=r.take(sizes[2])
    n=w*h//16
    require(not skip or len(skip)>=(n+7)//8,'Short luminance skip bitmap')
    if auxiliary:raise Unsupported('Nonempty FY auxiliary luminance streams are not implemented')
    out=list(reference)+[0]*(w*4+32)
    commands=[]; s=Reader(stream)
    for i in range(n):
        if skip and skip[i//8]&(128>>(i%8)):
            commands.append(None);continue
        head=s.byte();mode=head>>5;out[i*16]=head&31
        commands.append((mode,s.take((1,5,3,3,2,5,11,3)[mode]-1)))
    for i,cmd in enumerate(commands):
        if cmd is None:continue
        mode,b=cmd;p=i*16; a=out[p];right=out[p+16];below=out[p+w*4];diag=out[p+w*4+16]
        t=out[p:p+16]
        if mode in (0,1,7):
            rb=(right+diag)//2;bd=(below+diag)//2
            if mode==7:
                z=u16(b);t[2]=z>>10;t[8]=(z>>5)&31;t[10]=z&31
            else:
                t[2]=(a+right)//2;t[8]=(a+below)//2;t[10]=(t[8]+rb)//2
            t[1]=(a+t[2])//2;t[3]=(t[2]+right)//2
            t[4]=(a+t[8])//2;t[12]=(t[8]+below)//2
            t[9]=(t[8]+t[10])//2;t[11]=(t[10]+rb)//2
            t[6]=(t[2]+t[10])//2;t[14]=(t[10]+bd)//2
            t[5]=(a+t[10])//2;t[15]=(t[10]+diag)//2
            t[7]=((t[2]+rb) if mode==7 else (right+t[10]))//2
            t[13]=((t[8]+bd) if mode==7 else (below+t[10]))//2
            if mode==1:
                z=u32(b)
                for j in range(15,0,-1):
                    t[j]=clip5(t[j]+(0,1,2,-1)[z&3]);z>>=2
        elif mode in (2,3,5):
            z=int.from_bytes(b,'little');bits=2 if mode==5 else 1
            pal=[a,clip5(a+(1 if mode!=3 else -1)),clip5(a+2),clip5(a-1)]
            for j in range(15,0,-1):
                t[j]=pal[z&((1<<bits)-1)];z>>=bits
        elif mode==4:
            source=p-b[0]*16
            require(source>=0,'Luminance backward reference before image')
            t[1:]=out[source+1:source+16]
        elif mode==6:
            for group in range(5):
                z=u16(b,group*2)
                t[group*3+1:group*3+4]=[z>>10,(z>>5)&31,z&31]
        out[p:p+16]=t
    require(s.pos==len(stream),'Unconsumed luminance operands')
    if selector==1:
        planes=[]
        for k in range(2):
            packed=r.take(sizes[3+k]);values=[]
            for p in range(0,len(packed),3):
                z=int.from_bytes(packed[p:p+3],'big')
                values.extend(((z>>19)&31,(z>>13)&31,(z>>7)&31,(z>>1)&31))
            require(len(values)>=n,'Short chroma plane');planes.append(values[:n])
    else:
        planes=[list(r.take(n)),list(r.take(n))] if frame%2 else chroma
    require(planes is not None,'Missing chroma reference')
    pixels=[0]*(w*h)
    for i in range(n):
        bx=(i%(w//4))*4;by=(i//(w//4))*4
        u,v=planes[0][i],planes[1][i]
        require(u<32 and v<32,'Chroma value outside five-bit range')
        lut=YUV_LUT[(u*32+v)*32:(u*32+v+1)*32]
        for y in range(4):
            pixels[(by+y)*w+bx:(by+y)*w+bx+4]=[lut[z] for z in out[i*16+y*4:i*16+y*4+4]]
    return pixels,out[:w*h],planes,r.pos

def decode_rle(data,w,h,reference):
    r=Reader(data);mode=r.byte();require(mode in (0,1),'Unknown RLE frame mode')
    count=r.dword();out=[]
    require(count<=w*h*2,'Excessive RLE command count')
    for _ in range(count):
        c=r.byte()
        if mode==0:
            if c<=128: out.extend(words(r.take((c+1)*2)))
            else: out.extend([r.word()]*(257-c))
        elif c==0:
            n=r.byte();out.extend([r.word()]*n)
        elif c<128: out.extend(reference[len(out):len(out)+c])
        else: out.extend(words(r.take((c&127)*2)))
        require(len(out)<=w*h,'RLE output exceeds dimensions')
    require(len(out)==w*h,'RLE output does not fill frame')
    return out,r.pos

VQ_DELTAS=tuple(g*1024+r*32+b for g in range(2,-3,-1) for r in range(2,-3,-1) for b in range(2,-3,-1))+(3072,-3072,96)
def add555(*values, bias=16):
    return sum(clip5(sum((v>>s)&31 for v in values)-bias)<<s for s in (0,5,10))
def pairadd(a,b,bias):
    z=((a[0]|a[1]<<16)+(b[0]|b[1]<<16)-bias*0x10001)&0xffffffff
    return [z&65535,z>>16]

def decode_vq(data,w,h,reference,books):
    r=Reader(data);header=r.take(4)
    if any(header[:3]) or header[3]&0xf0:raise Unsupported('Unsupported WVQ packet header extension')
    for k in range(4):
        if header[3]&(1<<k):
            n=r.dword();require(n<=2048 and n%8==0,'Invalid WVQ codebook length')
            v=words(r.take(n));books[k][:len(v)]=v
    size=r.dword();stream=Reader(r.take(size));out=[0]*(w*h);basepair=[0,0]
    def vector(k):
        p=stream.byte()*4
        return books[k][p:p+4]
    for by in range(0,h,4):
        for bx in range(0,w,4):
            c=stream.byte();inter=bool(c&128);sat=bool(c&32)
            if inter:
                base=vector(2) if c&16 else [0x3def if sat else 0x4210]*4
            else:
                if c&64:
                    a=stream.byte()
                    if a&128:
                        delta=VQ_DELTAS[a&127]&65535
                        basepair=pairadd(basepair,[delta,delta],0)
                    else:
                        value=(a<<8)|stream.byte();basepair=[value,value]
                if c&16:
                    v=vector(0)
                    if sat:base=[add555(basepair[j%2],v[j]) for j in range(4)]
                    else:base=pairadd(basepair,v[:2],0x4210)+pairadd(basepair,v[2:],0x4210)
                else:base=basepair*2
            for q,(x,y) in enumerate(((0,0),(2,0),(0,2),(2,2))):
                residual=vector(3 if inter else 1) if c&(8>>q) else None
                for yy in range(2):
                    p=(by+y+yy)*w+bx+x
                    if sat:
                        for xx in range(2):
                            vals=[base[q]]
                            if inter: vals.append(reference[p+xx])
                            if residual is not None:vals.append(residual[yy*2+xx])
                            out[p+xx]=add555(*vals,bias=16*(len(vals)-1))
                    else:
                        vals=[base[q],base[q]]
                        if inter: vals=pairadd(vals,reference[p:p+2],0x4210)
                        if residual is not None:vals=pairadd(vals,residual[yy*2:yy*2+2],0x4210)
                        out[p:p+2]=vals
    require(stream.pos==size,'Unconsumed WVQ block commands')
    return out,r.pos

CODECS={b'FF02':'92',b'FS00':'92',b'FS02':'92',b'FS04':'92',b'FY00':'93',b'FY02':'93',b'FY04':'93',b'FV02':'vq',b'AN10':'rle'}
TAGS={b'cftc',b'ver ',b'info',b'tdir',b'bhdr',b'bctl',b'shdr',b'sctl',b'bmov',b'tsnd',b'mdib'}

class Movie:
    """Parse before opening the destination; all addressing uses explicit tables."""
    def __init__(self,data):
        self.data=data;self.warnings=[];self.chunks=[];self.frames=[];self.audio=b'';self.audio_rate=0
        if len(data)<20 or data[:4]!=b'RIFF' or data[8:16]!=b'FJMVcftc':
            raise Unsupported('Not a Fujitsu Movie RIFF/FJMV file with a cftc directory')
        self.check(u32(data,4)+8==len(data),'RIFF length differs from physical file length')
        p=12
        while p+8<=len(data):
            tag=data[p:p+4];size=u32(data,p+4)
            if tag not in TAGS:raise Unsupported('Unsupported FJMV chunk '+repr(tag))
            end=p+8+size;payload=data[p+8:min(end,len(data))]
            self.chunks.append((tag,p,size,payload))
            if end>len(data):
                self.warn('Truncated %s chunk at byte %d'%(tag.decode(),p));p=len(data);break
            p=end
        self.check(p==len(data),'Incomplete final chunk header')
        bytag={t:[(p,n,d) for tt,p,n,d in self.chunks if tt==t] for t in TAGS}
        def single(t,minimum,exact=False):
            require(len(bytag[t])==1,'Expected exactly one '+t.decode()+' chunk')
            d=bytag[t][0][2];require(len(d)>=minimum,'Truncated '+t.decode()+' chunk')
            if exact and len(d)!=minimum:raise Unsupported('Unsupported '+t.decode()+' header extension')
            return d
        ver=single(b'ver ',6,True)
        if u32(ver) not in (1,257) or u16(ver,4)!=0:raise Unsupported('Unsupported FJMV version')
        self.version=u32(ver)
        bh=single(b'bhdr',34)
        if bh[28:32] not in CODECS:raise Unsupported('Unsupported FJMV video codec '+repr(bh[28:32]))
        self.codec=bh[28:32].decode();self.family=CODECS[bh[28:32]];self.track=u16(bh)
        self.check(u16(bh,2)==0,'Nonzero bhdr sequence')
        if bh[4:8] not in (b'vdeo',b'anim') or u32(bh,24)!=16 or u32(bh,12)!=1:
            raise Unsupported('Unsupported video track representation')
        self.width=u16(bh,16);self.height=u16(bh,18)
        require(0<self.width<=8192 and 0<self.height<=8192,'Invalid or excessive video dimensions')
        if (u16(bh,20),u16(bh,22))!=(self.width,self.height):
            raise Unsupported('Independent nominal and display dimensions are not implemented')
        keycount=u16(bh,32);require(len(bh)==75+2*keycount,'Invalid keyframe table/name length')
        self.keys=words(bh[34:34+2*keycount]);self.keyset=set(self.keys)
        require(self.keys and self.keys[0]==1 and self.keys==sorted(self.keyset),'Invalid keyframe table')
        self.video_name=bh[34+2*keycount:].split(b'\0')[0].decode('cp932','replace')
        self.metadata={};info=single(b'info',224,True)
        for name,start,size in [('title',0,41),('created',41,23),('creator',64,41),('modified',105,23),('editor',128,41),('copyright',169,41)]:
            self.metadata[name]=info[start:start+size].split(b'\0')[0].decode('cp932','replace')
        self.check(u32(info,210)==len(data),'info file length mismatch')
        if u16(info,216)!=1 or u16(info,220)>1:raise Unsupported('Multiple video or audio tracks are not implemented')
        self.check(u16(info,218)==self.track,'info video track ID mismatch')
        self.check(u16(info,220)==len(bytag[b'shdr']),'info audio track count mismatch')
        lookup={p:(t,n,d) for t,p,n,d in self.chunks}
        def index_entries(d,start):
            require((len(d)-start)%16==0,'Invalid chunk directory length')
            for q in range(start,len(d),16):
                t,n,tr,seq,off=struct.unpack_from('<4sIHHI',d,q)
                target=lookup.get(off)
                self.check(target is not None and target[:2]==(t,n),'Directory entry does not match chunk at byte %d'%off)
                if target and t in (b'bhdr',b'bctl',b'shdr',b'sctl',b'bmov',b'tsnd',b'mdib') and len(target[2])>=4:
                    self.check(target[2][:4]==struct.pack('<HH',tr,seq),'Directory ID/sequence mismatch at byte %d'%off)
        toc=single(b'cftc',4);self.check(u32(toc)==0,'Nonzero cftc reserved value');index_entries(toc,4)
        self.check((len(toc)-4)//16==len(self.chunks),'cftc entry count mismatch')
        td=single(b'tdir',2);require(len(td)==2+16*u16(td),'Invalid track directory length');index_entries(td,2)
        self.check(u16(td)==u16(info,216)+u16(info,220),'Track directory count mismatch')
        for q in range(2,len(td),16):self.check(td[q:q+4] in (b'bhdr',b'shdr'),'Unexpected track-directory entry')
        video_first={};next_frame=1
        for pos,n,d in bytag[b'bmov']:
            video_first[pos]=next_frame
            if len(d)>=18:next_frame+=u16(d,16)
        for tag,entrysize in ((b'bctl',8),(b'sctl',10)):
            if not bytag[tag]:continue
            d=single(tag,6);require(len(d)==6+entrysize*u16(d,4),'Invalid '+tag.decode()+' length')
            header_tag=b'bhdr' if tag==b'bctl' else b'shdr'
            self.check(u16(d,2)==0,'Nonzero control-table sequence')
            if bytag[header_tag]:self.check(u16(d)==u16(bytag[header_tag][0][2]),'Control-table track mismatch')
            for q in range(6,len(d),entrysize):
                off=u32(d,q);target=lookup.get(off)
                self.check(target is not None and target[0]==(b'bmov' if tag==b'bctl' else b'tsnd'),'Invalid control-table chunk offset')
                if target and len(target[2])>=4:
                    self.check(u16(d,q+entrysize-2)==u16(target[2],2),'Control-table sequence mismatch')
                    if tag==b'sctl':self.check(u32(d,q+4)==target[1],'Sound control-table size mismatch')
                    else:self.check(u16(d,q+4)==video_first.get(off),'Video control-table first frame mismatch')
        frame=0;lastkey=1;time_adjustment=0
        for pos,size,d in bytag[b'bmov']:
            if len(d)<22:self.warn('Truncated bmov header at byte %d'%pos);continue
            require(u16(d)==self.track,'Unexpected bmov track')
            w,h=u16(d,8),u16(d,10);x,y=struct.unpack_from('<hh',d,12)
            if (w,h)!=(self.width,self.height) or (x,y)!=(-32768,-32768):
                raise Unsupported('Variable image dimensions or positioned frames are not implemented')
            count=u16(d,16);rate=u32(d,18);require(rate>0,'Zero video frame rate')
            base=22+8*count;require(base<=len(d),'Truncated bmov frame table')
            previous_end=0
            for i in range(count):
                off,n=struct.unpack_from('<II',d,22+8*i);frame+=1
                if frame in self.keyset:lastkey=frame
                self.check(off==previous_end,'Noncontiguous frame payload at frame %d'%frame)
                previous_end=off+n
                packet=d[base+off:min(base+off+n,len(d))] if base+off<=len(d) else b''
                if self.family!='92' and len(packet)>=20:
                    if any(packet[1:20]) or (packet[0] not in (0,1) if self.family=='93' else packet[0]!=0):
                        raise Unsupported('Unsupported per-frame codec extension')
                self.check(len(packet)==n,'Truncated frame %d'%frame)
                timestamp=u32(d,4)+(i*10000)//rate+time_adjustment
                if self.frames and timestamp<=self.frames[-1][0]:
                    shift=self.frames[-1][0]+max(1,10000//self.frames[-1][1])-timestamp
                    time_adjustment+=shift;timestamp+=shift
                    self.warn('Regressing timestamp at frame %d: shifted this and subsequent video frames by %d ms'%(frame,shift))
                self.frames.append((timestamp,rate,frame-lastkey,packet))
            self.check(base+previous_end==len(d),'bmov data length mismatch at byte %d'%pos)
        require(self.frames,'No video frames')
        self.check(frame==u32(bh,8),'Video frame count differs from bhdr')
        self.check(all(k<=frame for k in self.keys),'Keyframe table extends beyond video')
        require(all(a[0]<b[0] for a,b in zip(self.frames,self.frames[1:])),'Overlapping or reversed frame timestamps')
        self.duration_ms=self.frames[-1][0]+max(1,10000//self.frames[-1][1])
        self.check(u16(info,214)==(self.duration_ms+999)//1000,'info whole-second video duration mismatch')
        self.tick_ms=math.gcd(self.duration_ms,*(f[0] for f in self.frames)) or 1
        self.tick_count=self.duration_ms//self.tick_ms
        if bytag[b'shdr']:
            sh=single(b'shdr',93,True)
            if sh[4:8]!=b'snd ' or u32(sh,16)!=1:raise Unsupported('Unsupported audio track representation')
            self.audio_rate=u32(sh,8);require(0<self.audio_rate<=384000,'Invalid audio rate')
            aid=u16(sh);self.audio_header={'rate':self.audio_rate,'sample_count':u32(sh,12),'name':sh[20:28].split(b'\0')[0].decode('cp932','replace'),'sound_id':u32(sh,28),'length':u32(sh,32),'loop_start':u32(sh,36),'loop_length':u32(sh,40),'frequency':u16(sh,44),'frequency_adjust':struct.unpack_from('<h',sh,46)[0],'base_note':sh[48],'reserved':sh[49:52].hex(),'track_name':sh[52:93].split(b'\0')[0].decode('cp932','replace')}
            self.check(u16(sh,2)==0,'Nonzero shdr sequence')
            self.check(not any(sh[49:52]),'Nonzero sound-descriptor reserved bytes')
            self.check(u16(info,222)==aid,'info audio track ID mismatch')
            if u32(sh,36) or u32(sh,40):raise Unsupported('Looped sound tracks are not implemented')
            pcm=bytearray();lut=bytes(128+(v&127)*(1 if v&128 else -1) for v in range(256))
            rawcount=0
            for pos,n,d in bytag[b'tsnd']:
                if len(d)<8:self.warn('Truncated tsnd header');continue
                require(u16(d)==aid,'Unexpected audio track ID');start=(u32(d,4)*self.audio_rate)//1000
                require(start<=self.audio_rate*86400,'Excessive audio timestamp')
                if start>len(pcm):pcm.extend(b'\x80'*(start-len(pcm)))
                audio=d[8:].translate(lut);rawcount+=len(audio)
                if start<len(pcm):self.warn('Overlapping audio chunks; later chunk replaces overlap')
                pcm[start:start+len(audio)]=audio
            self.check(rawcount==u32(sh,12)==u32(sh,32),'Audio sample count mismatch')
            self.audio=bytes(pcm)
        elif bytag[b'tsnd']:raise Unsupported('Sound data without an audio header')
        else:self.check(u16(info,222)==0,'Nonzero absent-audio track ID')
        self.poster=None;self.posters=[]
        for pos,n,d in bytag[b'mdib']:
            try:
                require(len(d)>=58 and d[4:6]==b'BM','Invalid mdib bitmap')
                self.poster=d[4:]
                self.posters.append(self.read_poster(self.poster))
            except Unsupported:raise
            except (FormatError,struct.error) as e:self.warn('Damaged mdib resource: '+str(e))
    def read_poster(self,b):
        self.check(u32(b,2)==len(b),'Embedded bitmap size mismatch')
        self.check(u32(b,6)==0,'Nonzero embedded bitmap reserved fields')
        if u32(b,14)!=40:raise Unsupported('Unsupported mdib DIB header')
        size,w,h,planes,bits,compression,raster_size,xppm,yppm,colors,important=struct.unpack_from('<IiiHHIIiiII',b,14)
        if planes!=1 or bits!=8 or compression!=0:raise Unsupported('Unsupported mdib bitmap representation')
        require(0<w<=8192 and 0<abs(h)<=8192,'Invalid poster dimensions')
        count=colors or 256;require(0<count<=256,'Invalid poster palette size')
        palette_end=54+4*count;require(palette_end<=len(b),'Truncated poster palette')
        palette=[bytes((b[p+2],b[p+1],b[p])) for p in range(54,palette_end,4)]
        stride=(w+3)&~3;offset=u32(b,10)
        if offset<palette_end:
            self.warn('Embedded bitmap pixel offset overlaps its color table; using the complete table boundary')
            offset=palette_end
        self.check(raster_size in (0,stride*abs(h)),'Embedded bitmap raster size mismatch')
        self.check(important<=count,'Embedded bitmap important-color count exceeds palette')
        require(offset+stride*abs(h)<=len(b),'Truncated poster raster')
        self.check(offset+stride*abs(h)==len(b),'Trailing embedded bitmap bytes')
        rows=[]
        for y in range(abs(h)):
            row=y if h<0 else abs(h)-1-y
            indices=b[offset+row*stride:offset+row*stride+w]
            require(all(i<count for i in indices),'Poster palette index out of range')
            rows.append(b''.join(palette[i] for i in indices))
        self.poster_rgb=b''.join(rows)
        return {'width':w,'height':abs(h),'top_down':h<0,'bits':bits,'palette_entries':count,'important_colors':important,'x_pixels_per_meter':xppm,'y_pixels_per_meter':yppm,'declared_pixel_offset':u32(b,10),'used_pixel_offset':offset,'row_stride':stride}
    def warn(self,message):
        if message not in self.warnings:self.warnings.append(message)
    def check(self,ok,message):
        if not ok:self.warn(message)
    def decoded(self):
        align=8 if self.family in ('92','rle') else 4
        w=(self.width+align-1)//align*align;h=(self.height+align-1)//align*align
        reference=[0]*(w*h);initial=[0]*(w*h);chroma=None;palette=None;books=[[0]*1024 for _ in range(4)];good=0;lost=False
        for j,(timestamp,rate,local,f) in enumerate(self.frames):
            try:
                if local==0:lost=False
                require(not lost,'Reference keyframe is damaged')
                if self.family=='92':
                    if local==0:require(len(f)>=512,'Truncated palette');palette=words(f[:512]);f=f[512:]
                    require(palette is not None,'Missing palette')
                    out,usage=decode92(f,w,h,palette,reference,initial)
                    consumed,size,nibbles,remaining=usage
                    require(size-consumed==2 and nibbles==remaining,'Invalid Fujitsu92 stream lengths')
                else:
                    require(len(f)>=20,'Missing frame extension')
                    selector=f[0]
                    if any(f[1:20]) or (selector not in (0,1) if self.family=='93' else selector!=0):
                        raise Unsupported('Unsupported per-frame codec extension')
                    offset=20
                    if local==0:
                        if j==0:
                            self.palette_flags=f[offset:offset+256];offset+=256
                        self.inverse_palette=f[offset:offset+4096];offset+=4096
                        self.rgb_palette=f[offset:offset+1024];offset+=1024
                    require(len(f)>=offset,'Truncated frame palette tables');f=f[offset:]
                    if self.family=='93':out,lum,chroma,used=decode93(f,w,h,reference,selector,chroma,local+1)
                    elif self.family=='vq':out,used=decode_vq(f,w,h,reference,books)
                    else:out,used=decode_rle(f,w,h,reference)
                    require(used==len(f),'Unexpected bytes after codec packet')
                if local==0:reference=lum if self.family=='93' else out
                initial=out;good+=1
            except Unsupported:raise
            except (FormatError,IndexError,struct.error) as e:
                self.warn('Frame %d: %s; holding the last decodable frame'%(j+1,e))
                if local==0:lost=True
                out=initial
            yield timestamp,out,w
        require(good>0,'No complete video frame could be decoded')

import zlib
RGB555=tuple(bytes((((v>>5)&31)*255//31,((v>>10)&31)*255//31,(v&31)*255//31)) for v in range(65536))
def png_frame(pixels,stride,w,h):
    def chunk(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
    raw=b''.join(b'\0'+b''.join(RGB555[p] for p in pixels[y*stride:y*stride+w]) for y in range(h))
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,3))+chunk(b'IEND',b'')

def riff_chunk(t,b):return t+struct.pack('<I',len(b))+b+(b'\0' if len(b)%2 else b'')
def riff_list(t,b):return riff_chunk(b'LIST',t+b)

def avi_header(movie):
    w,h=movie.width,movie.height;scale=movie.tick_ms;rate=1000;n=movie.tick_count;audio=bool(movie.audio)
    avih=struct.pack('<14I',scale*1000,0,0,0x110,n,0,1+audio,w*h*3,w,h,0,0,0,0)
    vh=struct.pack('<4s4sIHH8I4h',b'vids',b'MPNG',0,0,0,0,scale,rate,0,n,w*h*3,0xffffffff,0,0,0,w,h)
    vf=struct.pack('<IiiHH4sIiiII',40,w,h,1,24,b'MPNG',w*h*3,0,0,0,0)
    streams=riff_list(b'strl',riff_chunk(b'strh',vh)+riff_chunk(b'strf',vf))
    if audio:
        ar=movie.audio_rate
        ah=struct.pack('<4s4sIHH8I4h',b'auds',b'\0'*4,0,0,0,0,1,ar,0,len(movie.audio),ar,0xffffffff,1,0,0,0,0)
        af=struct.pack('<HHIIHH',1,1,ar,ar,1,8)
        streams+=riff_list(b'strl',riff_chunk(b'strh',ah)+riff_chunk(b'strf',af))
    return riff_list(b'hdrl',riff_chunk(b'avih',avih)+streams)

def convert(input_file,output_file,verbose=False):
    src=Path(input_file);dst=Path(output_file)
    require(src.resolve()!=dst.resolve(),'Input and output paths must differ')
    movie=Movie(src.read_bytes())
    # Decode once before creating the destination. Unsupported/malformed packets
    # are identified without leaving a new output file behind.
    for _ in movie.decoded():pass
    header=avi_header(movie);index=[];audio_pos=0
    with dst.open('wb') as out:
        out.write(b'RIFF\0\0\0\0AVI '+header)
        movi=out.tell();out.write(b'LIST\0\0\0\0movi');origin=movi+8
        def write_chunk(tag,payload,flags=16):
            offset=out.tell()-origin
            require(out.tell()+len(payload)+len(index)*16+32<0xffffffff,'AVI exceeds the 4 GiB classic RIFF limit')
            out.write(riff_chunk(tag,payload));index.append(struct.pack('<4sIII',tag,flags,offset,len(payload)))
        slot=0
        for timestamp,pixels,stride in movie.decoded():
            target=timestamp//movie.tick_ms
            while slot<target:write_chunk(b'00dc',b'',0);slot+=1
            last_png=png_frame(pixels,stride,movie.width,movie.height)
            write_chunk(b'00dc',last_png);slot+=1
            if movie.audio:
                end=min(len(movie.audio),((timestamp+movie.tick_ms)*movie.audio_rate)//1000)
                if end>audio_pos:write_chunk(b'01wb',movie.audio[audio_pos:end]);audio_pos=end
        while slot<movie.tick_count-1:write_chunk(b'00dc',b'',0);slot+=1
        if slot<movie.tick_count:write_chunk(b'00dc',last_png);slot+=1
        if audio_pos<len(movie.audio):write_chunk(b'01wb',movie.audio[audio_pos:])
        end=out.tell();out.seek(movi+4);out.write(struct.pack('<I',end-movi-8));out.seek(end)
        out.write(riff_chunk(b'idx1',b''.join(index)));size=out.tell();out.seek(4);out.write(struct.pack('<I',size-8))
    dst.chmod(dst.stat().st_mode|0o440)
    if verbose:
        report=dst.with_name(dst.name+'.json')
        report.write_text(json.dumps({'format':'FJMV','codec':movie.codec,'width':movie.width,'height':movie.height,'frames':len(movie.frames),'duration_ms':movie.duration_ms,'audio_rate':movie.audio_rate,'audio_samples':len(movie.audio),'audio_header':getattr(movie,'audio_header',None),'metadata':movie.metadata,'posters':movie.posters,'warnings':movie.warnings,'chunks':[{'tag':t.decode(),'offset':p,'size':n} for t,p,n,d in movie.chunks]},ensure_ascii=False,indent=2)+'\n')
        report.chmod(report.stat().st_mode|0o440)
    return movie

def main():
    parser=argparse.ArgumentParser(description='Convert Fujitsu Movie FJMV video and audio to lossless PNG/PCM AVI.')
    parser.add_argument('inputFile');parser.add_argument('outputFile')
    parser.add_argument('-verbose','--verbose',action='store_true',help='also write outputFile.json diagnostics')
    args=parser.parse_args()
    try:
        movie=convert(args.inputFile,args.outputFile,args.verbose)
        for warning in movie.warnings:print('Warning: '+warning,file=sys.stderr)
        if args.verbose:print('%d frames, %dx%d, %s, %d Hz audio'%(len(movie.frames),movie.width,movie.height,movie.codec,movie.audio_rate),file=sys.stderr)
    except (OSError,ValueError,struct.error) as e:
        print('fujitsuMovie: '+str(e),file=sys.stderr);return 1
    return 0

if __name__=='__main__':
    sys.exit(main())

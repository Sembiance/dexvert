# Vibe coded by Codex
"""MacDraw-wrapped QuickDraw PICT playback, with Deark bitmap extraction.

PICT opcodes are decoded here, never inferred from Deark diagnostic output.
Screen QuickDraw commands are rendered; printer-specific alternate descriptions
remain preserved and explicitly identified. See macDraw.txt for limitations.
"""
from __future__ import annotations

import base64
from collections import Counter
from functools import lru_cache
import hashlib
import math
from pathlib import Path
import struct
import subprocess
import tempfile

import macDrawText as mt


OLD_COLORS = {30:'#ffffff',33:'#000000',69:'#ffff00',137:'#ff00ff',
              205:'#ff0000',273:'#00ffff',341:'#00ff00',409:'#0000ff'}
BITMAP_OPS = (0x90,0x91,0x98,0x99,0x9a,0x9b)


def rgb(raw):
    return '#' + ''.join(f'{v >> 8:02x}' for v in struct.unpack('>3H',raw))


def nonempty(box):
    return box[2]>box[0] and box[3]>box[1]


@lru_cache(maxsize=128)
def deark_bitmap(picture):
    """Extract exactly one independently framed bitmap, in an isolated folder."""
    with tempfile.TemporaryDirectory(prefix='macDraw-pict-') as directory:
        root=Path(directory);source=root/'bitmap.pict';source.write_bytes(picture)
        try:
            run=subprocess.run(['deark','-m','pict','-od',str(root),str(source)],
                               stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                               timeout=60,check=False)
        except FileNotFoundError as exc:
            raise ValueError('deark is required for embedded PICT bitmaps but was not found on PATH') from exc
        except subprocess.TimeoutExpired as exc:
            raise ValueError('deark exceeded its 60-second bitmap extraction limit') from exc
        diagnostics=run.stdout.decode('utf-8',errors='replace')
        files=sorted(p for p in root.iterdir() if p!=source)
        if run.returncode or len(files)!=1 or files[0].suffix.lower()!='.png' or 'Error:' in diagnostics:
            raise ValueError('deark did not extract exactly one PNG: '+diagnostics.strip()[:1500])
        png=files[0].read_bytes()
        if len(png)<33 or png[:16]!=b'\x89PNG\r\n\x1a\n\0\0\0\rIHDR':
            raise ValueError('deark returned an invalid PNG header')
        width,height=struct.unpack_from('>2I',png,16)
        warnings=[line for line in diagnostics.splitlines() if 'Warning:' in line]
        return png,width,height,tuple(warnings)


class Decoder:
    def __init__(self,data,api,fonts,recover,require_complete):
        self.data=data;self.api=api;self.fonts=fonts or mt.default_fonts()
        self.recover=recover;self.strict=require_complete;self.pos=522
        self.version=api.wrapped_pict_version(data)
        self.issues=[];self.reported=set();self.objects=[];self.counts=Counter();self.comments=Counter()
        self.saved_rect=(0,0,0,0);self.last_line=(0,0);self.last_text=(0,0);self.line_batch=None
        self.frame=struct.unpack_from('>4h',data,514)
        self.s=dict(fg='#000000',bg='#ffffff',pen=(1,1),pen_mode=8,
                    pen_pattern=b'\xff'*8,fill_pattern=b'\xff'*8,bg_pattern=bytes(8),
                    oval=(0,0),font=0,face=0,size=12,text_mode=1,space_extra=0,
                    char_extra=0,ratio=(1,1,1,1),hfrac=0x8000,
                    origin=(0,0),clip=(self.frame,),font_names={})
        self.picture=dict(version=self.version,frame=self.frame,
                          declared_size=struct.unpack_from('>H',data,512)[0],
                          playback='QuickDraw screen commands; printer alternatives are preserved')

    def fail(self,message):
        raise self.api.FormatError(f'0x{self.pos:x}: PICT {message}')

    def take(self,n):
        if n<0 or self.pos+n>len(self.data):self.fail(f'truncated operand ({n} bytes required)')
        a=self.pos;self.pos+=n;return self.data[a:self.pos]

    def unpack(self,fmt):
        return struct.unpack('>'+fmt,self.take(struct.calcsize('>'+fmt)))

    def one(self,fmt):return self.unpack(fmt)[0]

    def issue(self,start,length,code,detail,recovery=False,key=None):
        code=('recovery_' if recovery else '')+'pict_'+code
        token=(code,key)
        if token in self.reported:return
        self.reported.add(token)
        if self.strict:raise self.api.UnsupportedError(f'0x{start:x}: {detail}. No SVG written in strict mode.')
        self.issues.append(self.api.Issue(start,length,code,detail))

    def state(self,**values):
        if any(self.s.get(k)!=v for k,v in values.items()):
            self.line_batch=None;self.s=dict(self.s,**values)

    def region(self):
        start=self.pos;size=self.one('H')
        if size<10 or size%2:self.fail('invalid region size')
        raw=self.take(size-2);box=struct.unpack_from('>4h',raw)
        if size==10:return (box,) if nonempty(box) else ()
        words=struct.unpack('>'+str((size-10)//2)+'h',raw[8:])
        at=0;active=set();rects=[];previous=None
        while at<len(words):
            y=words[at];at+=1
            if y==32767:
                if at!=len(words) or active:self.fail('region has trailing words or unclosed runs')
                return tuple(rects)
            if previous is not None:
                if y<previous:self.fail('region scan lines are not ordered')
                xs=sorted(active)
                if len(xs)%2:self.fail('region has an odd boundary count')
                for l,r in zip(xs[::2],xs[1::2]):
                    if y>previous and r>l:rects.append((previous,l,y,r))
            changes=[]
            while at<len(words) and words[at]!=32767:changes.append(words[at]);at+=1
            if at==len(words) or changes!=sorted(set(changes)):self.fail('invalid region transition row')
            at+=1;active.symmetric_difference_update(changes);previous=y
        self.pos=start;self.fail('missing region terminator')

    def add(self,kind,start,**fields):
        self.line_batch=None
        if kind in ('lines','shape'):
            self.issue(start,self.pos-start,'vector_rasterization',
                       'SVG geometry reproduces QuickDraw paths and pen sizes; exact historical raster coverage is not certified')
            if self.s['pen_mode'] not in (0,1,8,9):
                self.issue(start,self.pos-start,'pen_transfer',f'Pen mode {self.s["pen_mode"]} uses SVG overpainting; destination bitwise/arithmetic effects are unresolved',key=self.s['pen_mode'])
            if fields.get('family')==8 and fields.get('verb')==0:
                self.issue(start,self.pos-start,'region_frame','Region framing uses SVG scan-band outlines; shared interior edges may be visible')
        f=dict(native_pict=True,pict_kind=kind,state=self.s,**fields)
        o=self.api.Object(start,{'text':1,'lines':2,'shape':4,'bitmap':11}.get(kind,4),(),f,end=self.pos)
        self.objects.append(o)
        return o

    def line(self,start,a,b):
        self.last_line=b
        if min(self.s['pen'])<=0:return
        if self.line_batch is None:
            self.line_batch=self.add('lines',start,segments=[])
        self.line_batch.fields['segments'].append((a,b));self.line_batch.end=self.pos

    def text(self,start,point,raw):
        self.last_text=point
        family=self.s['font'];name=self.s['font_names'].get(family)
        if name is not None:
            named={s.family for s in self.fonts.strikes.values() if s.name.casefold()==name.casefold()}
            family=min(named) if len(named)==1 else -1
        m=self.fonts.resolve(family,self.s['size'],self.s['face']&127)
        if mt.is_substituted(family,m.strike.family):
            self.issue(start,self.pos-start,'font_substitution',
                       f'PICT font {name or self.s["font"]!r} unavailable; substituted bundled Geneva',key=(family,name))
        if name and any(ord(c)>127 for c in name):
            self.issue(start,self.pos-start,'text_encoding','Original font/script encoding is unavailable; text uses the declared MacRoman/Geneva fallback',key=name)
        if self.s['face']&128:self.issue(start,self.pos-start,'text_face','Unresolved high text-face bit; ordinary style bits retained')
        self.text_mode(start)
        ratio=self.s['ratio']
        if ratio[2]==0 or ratio[3]==0:self.fail('zero text-scale denominator')
        sx,sy=ratio[1]/ratio[3],ratio[0]/ratio[2]
        if sx<=0 or sy<=0:self.fail('nonpositive text scaling ratio')
        self.issue(start,self.pos-start,'text_metrics',
                   'PICT text uses bundled classic bitmap font metrics at saved positions; original outline/fractional metrics and font provenance are unavailable')
        x,y=point
        layout=mt.Layout(m,(y-m.ascent,x,y+m.descent,x+m.width(raw)),m.ascent+m.descent,[(x,y,raw)])
        self.add('text',start,point=point,text_bytes=raw,metrics=m,scale=(sx,sy),
                 text_layout=layout,font_id=family,font_index=self.s['font'],face=self.s['face'],font_name=name)
        self.state(hfrac=0x8000)

    def text_mode(self,start):
        if self.s['text_mode'] not in (0,1,3):
            self.issue(start,2,'text_transfer',f'Text transfer mode {self.s["text_mode"]} uses SVG overpainting; destination bitwise effects are not reproduced',key=self.s['text_mode'])

    def bitmap(self,start,opcode):
        direct=opcode in (0x9a,0x9b)
        if direct:self.take(4)
        rowword=self.one('H');row=rowword&0x3fff;bounds=self.unpack('4h')
        pixmap=bool(rowword&0x8000);depth=1;packing=0;components=1
        if not row or not nonempty(bounds):self.fail('invalid bitmap rowBytes or bounds')
        if pixmap:
            pm=self.unpack('HHIIIHHHHIII')
            version,packing,packsize,hres,vres,ptype,depth,components,component_size,plane,table,reserved=pm
            if not direct:
                seed,flags,last=self.unpack('IHH');count=0 if last==65535 else last+1
                self.take(count*8)
        if direct and not pixmap:self.fail('DirectBits requires a PixMap')
        src=self.unpack('4h');dst=self.unpack('4h');mode=self.one('H')
        mask=self.region() if opcode&1 else None
        pixel_start=self.pos;height=bounds[2]-bounds[0]
        if opcode in (0x90,0x91) or row<8 or packing==1:self.take(row*height)
        elif packing==2:
            if depth!=32 or row%4:self.fail('drop-pad packing requires 32-bit pixels and an aligned row')
            self.take(row*3//4*height)
        else:
            for _ in range(height):self.take(self.one('H' if row>250 else 'B'))
        end=self.pos
        if not nonempty(src) or not nonempty(dst):return
        if depth not in (1,2,4,8,16,32) or packing>4:
            self.issue(start,end-start,'bitmap_encoding',f'Unsupported PICT pixel depth {depth} / packing {packing}; bounded bitmap omitted',True,key=(depth,packing));return
        # A complete miniature v2 PICT containing only this bitmap and its
        # colors avoids output-number guessing when Deark omits other records.
        payload=self.data[start+(1 if self.version==1 else 2):end]
        prefix=bytes(512)+struct.pack('>H4h',0,*bounds)+b'\x00\x11\x02\xff'
        prefix+=struct.pack('>HhHII4hI',0x0c00,-2,0,72*65536,72*65536,*bounds,0)
        for code,color in ((0x1a,self.s['fg']),(0x1b,self.s['bg'])):
            prefix+=struct.pack('>H3H',code,*(int(color[i:i+2],16)*257 for i in (1,3,5)))
        record=struct.pack('>H',opcode)+payload
        miniature=prefix+record+bytes(len(record)%2)+b'\0\xff'
        try:
            png,width,height,warnings=deark_bitmap(miniature)
            if (width,height)!=(bounds[3]-bounds[1],bounds[2]-bounds[0]):
                raise ValueError(f'extracted dimensions {width}x{height} disagree with PixMap bounds')
        except (ValueError,OSError) as error:
            self.issue(start,end-start,'bitmap_decode',str(error)+'; bitmap omitted',True,key=str(error));return
        for warning in warnings:self.issue(start,end-start,'bitmap_warning',warning,key=warning)
        if mode not in (0,1):
            self.issue(start,end-start,'bitmap_transfer',f'Bitmap mode {mode} uses source-copy fallback; destination bitwise/arithmetic effects are unresolved',key=mode)
        if mode==1 and (pixmap or self.s['fg']!='#000000' or self.s['bg']!='#ffffff'):
            self.issue(start,end-start,'color_or','Color srcOr uses SVG multiply blending, which is not identical to QuickDraw bitwise color composition')
        self.add('bitmap',start,bounds=bounds,src=src,dst=dst,mode=mode,mask=mask,
                 png=png,pixel_offset=pixel_start,pixel_length=end-pixel_start,depth=depth,packing=packing)

    def command(self,code,start):
        if code==0:return
        if code==1:self.state(clip=self.region());return
        if code in (2,9,10):self.state(**{ {2:'bg_pattern',9:'pen_pattern',10:'fill_pattern'}[code]:self.take(8)});return
        if code in (3,5,8,13,21,22):
            key={3:'font',5:'text_mode',8:'pen_mode',13:'size',21:'hfrac',22:'char_extra'}[code]
            val=self.one('H' if code in (3,21) else 'h')
            if code==13:
                if not 0<=val<=4096:self.fail('invalid point size')
                if val==0:val=12  # Declared classic system-font-size environment.
            self.state(**{key:val});return
        if code==4:self.state(face=self.one('B'));return
        if code==6:self.state(space_extra=self.one('i')/65536);return
        if code in (7,11):self.state(**{('pen' if code==7 else 'oval'):self.unpack('2h')});return
        if code==12:
            dh,dv=self.unpack('2h');x,y=self.s['origin'];self.state(origin=(x-dh,y-dv));return
        if code in (14,15):
            value=self.one('I')
            if value not in OLD_COLORS:self.issue(start,self.pos-start,'old_color',f'Unrecognized QuickDraw color constant {value}; black fallback',key=value)
            self.state(**{('fg' if code==14 else 'bg'):OLD_COLORS.get(value,'#000000')});return
        if code==16:self.state(ratio=self.unpack('4h'));return
        if code==17:
            marker=self.take(1 if self.version==1 else 2)
            if marker!=(b'\x01' if self.version==1 else b'\x02\xff'):self.fail('invalid repeated version marker')
            return
        if code in (18,19,20):
            ptype=self.one('H');pattern=self.take(8)
            if ptype==0:paint=pattern
            elif ptype==2:paint=rgb(self.take(6))
            else:self.fail('indexed PixPat layout is outside the implemented profile')
            self.state(**{{18:'bg_pattern',19:'pen_pattern',20:'fill_pattern'}[code]:paint});return
        if code in (26,27):self.state(**{('fg' if code==26 else 'bg'):rgb(self.take(6))});return
        if code in (28,30):return
        if code in (29,31):
            self.take(6);self.issue(start,self.pos-start,'color_effect','Highlight/arithmetic color state is preserved; ordinary QuickDraw paints are used');return
        if 32<=code<=35:
            a=self.unpack('2h')[::-1] if code in (32,34) else self.last_line
            if code in (32,33):b=self.unpack('2h')[::-1]
            else:
                dx,dy=self.unpack('2b');b=(self.api.signed16(a[0]+dx),self.api.signed16(a[1]+dy))
            self.line(start,a,b);return
        if 40<=code<=43:
            x,y=self.last_text
            if code==40:y,x=self.unpack('2h')
            else:
                if code in (41,43):x=self.api.signed16(x+self.one('B'))
                if code in (42,43):y=self.api.signed16(y+self.one('B'))
            raw=self.take(self.one('B'));self.text(start,(x,y),raw);return
        if code in (44,45,46):
            size=self.one('H');raw=self.take(size)
            if code==44:
                if size<3 or raw[2]!=size-3:self.fail('invalid font-name length')
                family=struct.unpack_from('>H',raw)[0];names=dict(self.s['font_names']);names[family]=raw[3:].decode('mac_roman')
                self.state(font_names=names)
            elif code==45:
                if size!=8:self.fail('invalid lineJustify size')
                inter,total=struct.unpack('>2i',raw)
                self.state(char_extra=inter/65536)
                if inter or total:self.issue(start,self.pos-start,'line_justify','Script Manager line justification uses declared intercharacter spacing; fractional font-width distribution remains approximate')
            elif any(raw):self.issue(start,self.pos-start,'glyph_state','Outline/fractional glyph state uses the bundled bitmap font environment')
            return
        if 0x30<=code<=0x8f:
            family=code>>4;verb=code&7;same=bool(code&8)
            if family in (3,4,5,6):
                shape=self.saved_rect if same else self.unpack('4h')
                if not same and verb<=4:self.saved_rect=shape
                angles=self.unpack('2h') if family==6 else None
            elif family==7:
                if same:
                    self.issue(start,self.pos-start,'same_poly_region','SamePoly/SameRgn are marked unimplemented by Apple; zero-length opcode preserved without drawing');return
                size=self.one('H')
                if size<10 or (size-10)%4:self.fail('invalid polygon extent')
                box=self.unpack('4h');shape=tuple(self.unpack('2h')[::-1] for _ in range((size-10)//4))
                angles=None
            else:
                if same:
                    self.issue(start,self.pos-start,'same_poly_region','SamePoly/SameRgn are marked unimplemented by Apple; zero-length opcode preserved without drawing');return
                shape=self.region()
                angles=None
            if verb<=4:self.add('shape',start,family=family,verb=verb,shape=shape,angles=angles)
            return
        if code in BITMAP_OPS:self.bitmap(start,code);return
        if code in (0xa0,0xa1):
            kind=self.one('H');raw=self.take(self.one('H')) if code==0xa1 else b'';self.comments[kind]+=1
            if kind in (150,154,160,161,163,164,165,180,181,182,190,191,192,193,194,195,196,200,201,202):
                self.issue(start,self.pos-start,'printer_alternatives',
                           'Printer comments contain alternate text, curve, line, rotation or PostScript descriptions; SVG uses the QuickDraw screen commands and preserves all comment bytes')
            elif kind not in (100,130,131,140,141,142,143,151,152,153,155,156):
                self.issue(start,self.pos-start,'comment_metadata','Application/private picture comments are preserved; screen QuickDraw ignores their payload',key=kind)
            return
        if code==0xc00:
            raw=self.take(24);self.picture['extended_header']=raw.hex()
            version=struct.unpack_from('>h',raw)[0]
            if raw[:4]==b'\xff'*4:
                l,t,r,b=(v/65536 for v in struct.unpack_from('>4i',raw,4))
                self.picture['header_record']=dict(version=-1,source_frame=(t,l,b,r),reserved=raw[20:].hex())
            elif version==-2:
                reserved,hres,vres,t,l,b,r,tail=struct.unpack_from('>HII4hI',raw,2)
                self.picture['header_record']=dict(version=-2,h_resolution=hres/65536,v_resolution=vres/65536,source_frame=(t,l,b,r),reserved=[reserved,tail])
            else:
                self.issue(start,self.pos-start,'header_version',f'Unknown PICT header version {version}; initial frame retained');return
            source=self.picture['header_record']['source_frame']
            if tuple(source)!=self.frame:
                self.issue(start,self.pos-start,'header_mapping','Nonmatching PICT header source and initial frames require resolution-aware playback; initial frame used without remapping')
            return
        if code in (0x8200,0x8201):
            self.take(self.one('I'));self.issue(start,self.pos-start,'quicktime','QuickTime drawing opcode omitted; embedded movie transformation/codec is unsupported',True);return
        # Apple defines exact skip lengths for reserved opcodes. Undefined
        # low opcodes 0x17..0x19 deliberately fail without guessing a boundary.
        if 0x24<=code<=0x27 or code==0x2f or 0x92<=code<=0x97 or 0x9c<=code<=0x9f or 0xa2<=code<=0xaf:
            self.take(self.one('H'));return
        if 0xb0<=code<=0xcf or 0x8000<=code<=0x80ff:return
        if 0xd0<=code<=0xfe or code>=0x8100:self.take(self.one('I'));return
        if 0x100<=code<=0x7fff:self.take(2*(code>>8));return
        self.fail(f'unknown opcode {code:#06x}; its operand length is not established')

    def parse(self):
        ended=False;omitted=None
        while self.pos<len(self.data):
            if self.version==2 and self.pos%2:
                at=self.pos
                if self.take(1)!=b'\0':self.issue(at,1,'alignment','PICT word-alignment byte is nonzero; opcode boundaries retained',True)
            start=self.pos
            try:
                code=self.one('B' if self.version==1 else 'H');self.counts[code]+=1
                if code==255:ended=True;break
                self.command(code,start)
            except self.api.FormatError as error:
                if isinstance(error,self.api.UnsupportedError) or not self.recover or not self.objects:raise
                self.issue(start,len(self.data)-start,'omitted_suffix',str(error)+'; stopped without searching for another opcode',True)
                omitted=start;self.pos=len(self.data);break
        if not ended and omitted is None:
            if not self.recover or not self.objects:self.fail('missing EndPic opcode')
            self.issue(self.pos,0,'missing_end','PICT reaches EOF without an EndPic opcode; complete preceding drawing commands retained',True)
        spans=[(0,512,'macdraw_pict_wrapper'),(512,10,'pict_size_and_frame')]
        stream_end=omitted if omitted is not None else self.pos
        if stream_end>522:spans.append((522,stream_end-522,'pict_framed_opcodes'))
        if omitted is not None:spans.append((omitted,len(self.data)-omitted,'recovery_uninterpreted_bytes'))
        elif self.pos<len(self.data):
            spans.append((self.pos,len(self.data)-self.pos,'pict_inactive_trailing_storage'))
            self.issue(self.pos,len(self.data)-self.pos,'trailing_storage','Bytes after EndPic are preserved as inactive storage; their save-history meaning is not established')
        if not nonempty(self.frame):self.issue(514,8,'empty_frame','Empty picture frame produces a one-pixel canvas')
        self.picture.update(end_offset=stream_end,opcode_counts={f'{k:04x}':v for k,v in sorted(self.counts.items())},
                            comment_counts={str(k):v for k,v in sorted(self.comments.items())},
                            vector_objects=sum(o.fields['pict_kind']!='bitmap' for o in self.objects),
                            bitmap_objects=sum(o.fields['pict_kind']=='bitmap' for o in self.objects))
        header=dict(native_format='MacDraw-wrapped PICT',picture=self.picture,
                    text_environment_override=dict(mt.TEXT_ENVIRONMENT,profile='QuickDraw PICT saved text positions with bundled bitmap metrics'),
                    metadata_limitations_override=[
                        'The 512-byte MacDraw print/editor export wrapper is preserved; not every preference bit is decoded.',
                        'PICT screen drawing is distinct from native editable MacDraw records. Printer comments and private application data remain preserved.',
                        'SVG continuous geometry cannot certify identical QuickDraw pixel coverage.'])
        doc=self.api.Document(self.data,f'PICT:{self.version}',header,self.objects,spans,self.issues,sum(self.counts.values()))
        doc.audit();return doc


def parse(data,api,*,fonts=None,recover=False,require_complete=False):
    if api.wrapped_pict_version(data) is None:
        raise api.FormatError('Expected a recognized MacDraw-wrapped PICT signature and version marker')
    return Decoder(data,api,fonts,recover,require_complete).parse()


def render(renderer,parent,obj):
    import sys
    api=sys.modules[type(renderer).__module__];E=api.element;n=api.number
    f=obj.fields;s=f['state'];kind=f['pict_kind']
    if not hasattr(renderer,'pict_clips'):renderer.pict_clips={};renderer.pict_paints={};renderer.pict_glyphs={}

    def region_path(rects):
        return ' '.join(f'M{n(l)} {n(t)}H{n(r)}V{n(b)}H{n(l)}Z' for t,l,b,r in rects if nonempty((t,l,b,r)))

    def clip(rects):
        if rects not in renderer.pict_clips:
            ident='pict-clip-'+str(len(renderer.pict_clips));renderer.pict_clips[rects]=ident
            definition=E(renderer.defs,'clipPath',id=ident,clipPathUnits='userSpaceOnUse')
            E(definition,'path',d=region_path(rects),shape_rendering='crispEdges')
        return 'url(#'+renderer.pict_clips[rects]+')'

    def paint(pattern,scale=(1,1)):
        if isinstance(pattern,str):return pattern
        if pattern==b'\xff'*8:return s['fg']
        if not any(pattern):return s['bg']
        key=(pattern,s['fg'],s['bg'],scale)
        if key not in renderer.pict_paints:
            ident='pict-pattern-'+str(len(renderer.pict_paints));renderer.pict_paints[key]=ident
            definition=E(renderer.defs,'pattern',id=ident,width=8,height=8,patternUnits='userSpaceOnUse')
            if scale!=(1,1):definition.set('patternTransform',f'scale({n(1/scale[0])} {n(1/scale[1])})')
            E(definition,'rect',width=8,height=8,fill=s['bg'])
            E(definition,'path',d=mt.pixel_path({(x,y) for y,row in enumerate(pattern) for x in range(8) if row&(128>>x)}),fill=s['fg'],shape_rendering='crispEdges')
        return 'url(#'+renderer.pict_paints[key]+')'

    xorigin,yorigin=s['origin']
    outer=E(parent,'g',data_source_offset=obj.offset,data_pict_kind=kind)
    if xorigin or yorigin:outer.set('transform',f'translate({n(xorigin)} {n(yorigin)})')
    group=E(outer,'g',clip_path=clip(s['clip']))
    penh,penw=s['pen']
    if kind=='bitmap':
        if f['mask'] is not None:group=E(group,'g',clip_path=clip(f['mask']))
        st,sl,sb,sr=f['src'];dt,dl,db,dr=f['dst'];bt,bl,bb,br=f['bounds']
        if f['mode']==1:group.set('style','mix-blend-mode:multiply')
        viewport=E(group,'svg',x=n(dl),y=n(dt),width=n(dr-dl),height=n(db-dt),
                   viewBox=' '.join(n(v) for v in (sl,st,sr-sl,sb-st)),preserveAspectRatio='none',overflow='hidden')
        image=E(viewport,'image',x=n(bl),y=n(bt),width=n(br-bl),height=n(bb-bt),
                preserveAspectRatio='none',image_rendering='pixelated')
        image.set('{'+api.XLINK+'}href','data:image/png;base64,'+base64.b64encode(f['png']).decode('ascii'))
        return
    if kind=='text':
        m=f['metrics'];x,y=f['point'];sx,sy=f['scale'];raw=f['text_bytes']
        E(group,'title').text=''.join(c for c in raw.decode('mac_roman') if ord(c)>=32 or c in '\r\n\t')
        group=E(group,'g',transform=f'translate({n(x)} {n(y)}) scale({n(sx)} {n(sy)})',
                data_font_name=f.get('font_name') or m.strike.name,data_font_family=f['font_id'],
                data_rendered_font_family=m.strike.family,data_font_size=m.size,
                data_font_sha256=m.strike.digest)
        if s['text_mode']==0:
            E(group,'rect',x=0,y=-m.ascent,width=n(m.width(raw)),height=m.ascent+m.descent,fill=s['bg'])
        spacing=bool(s['space_extra'] or s['char_extra']);at=0
        chunks=[bytes([c]) for c in raw] if spacing else [raw[i:i+34] for i in range(0,len(raw),34)]
        for chunk in chunks:
            key=(m.strike.digest,m.face,chunk,s['fg'],s['bg'],s['text_mode'])
            if key not in renderer.pict_glyphs:
                ident='pict-text-'+str(len(renderer.pict_glyphs));renderer.pict_glyphs[key]=ident
                black,white=m.pixels(chunk);definition=E(renderer.defs,'g',id=ident,shape_rendering='crispEdges')
                # srcOr treats white interiors as transparent; srcCopy paints
                # the background. srcBic erases the source glyph ink.
                if white and s['text_mode']==0:E(definition,'path',d=mt.pixel_path(white),fill=s['bg'])
                if black:E(definition,'path',d=mt.pixel_path(black),fill=s['bg'] if s['text_mode']==3 else s['fg'])
            use=E(group,'use',transform=f'translate({n(at)} 0) scale({n(m.numer/256)})')
            use.set('{'+api.XLINK+'}href','#'+renderer.pict_glyphs[key])
            at+=m.width(chunk)
            if spacing:at+=s['space_extra'] if chunk==b' ' else s['char_extra'] if chunk!=b'\r' else 0
        return
    if kind=='lines':
        if penw<=0 or penh<=0:return
        parts=[];previous=None
        for a,b in f['segments']:
            if a!=previous:parts.append(f'M{n(a[0]/penw+.5)} {n(a[1]/penh+.5)}')
            parts.append(f'L{n(b[0]/penw+.5)} {n(b[1]/penh+.5)}');previous=b
        E(group,'path',d=' '.join(parts),fill='none',stroke=paint(s['pen_pattern'],(penw,penh)),stroke_width=1,
          stroke_linecap='square',stroke_linejoin='bevel',transform=f'scale({n(penw)} {n(penh)})')
        return
    family=f['family'];verb=f['verb'];shape=f['shape']
    if verb==0 and (penw<=0 or penh<=0):return
    pattern=s['bg_pattern'] if verb==2 else s['fill_pattern'] if verb==4 else s['pen_pattern']
    color='#ffffff' if verb==3 else paint(pattern)
    if verb==3:group.set('style','mix-blend-mode:difference')
    elif s['pen_mode'] in (9,1) and verb in (0,1):group.set('style','mix-blend-mode:multiply')
    attrs=dict(fill=color,stroke='none')
    if family in (3,4,5,6):
        t,l,b,r=shape
        if not nonempty(shape):return
        if verb==0:
            attrs=dict(fill='none',stroke=color,stroke_width=n(max(penw,penh)))
            # FrameRect paints entirely inside its rectangle and supports
            # independent horizontal and vertical pen thicknesses.
            if family==3:
                d=region_path((shape,))
                if r-l>2*penw and b-t>2*penh:d+=' '+region_path(((t+penh,l+penw,b-penh,r-penw),))
                E(group,'path',d=d,fill=color,fill_rule='evenodd',shape_rendering='crispEdges');return
            pw,ph=penw,penh;l+=pw/2;r-=pw/2;t+=ph/2;b-=ph/2
            if r<=l or b<=t:return
        if family in (3,4):
            if family==4:
                oh,ow=s['oval'];attrs.update(rx=n(max(0,min(ow/2,(r-l)/2))),ry=n(max(0,min(oh/2,(b-t)/2))))
            E(group,'rect',x=n(l),y=n(t),width=n(r-l),height=n(b-t),**attrs)
        elif family==5:E(group,'ellipse',cx=n((l+r)/2),cy=n((t+b)/2),rx=n((r-l)/2),ry=n((b-t)/2),**attrs)
        else:
            start,sweep=f['angles'];sweep=max(-360,min(360,sweep));cx=(l+r)/2;cy=(t+b)/2;rx=(r-l)/2;ry=(b-t)/2
            if not sweep:return
            # QuickDraw angles describe rays from the center, not the usual
            # parametric ellipse angle: intersect each ray with the ellipse.
            def point(angle):
                theta=math.radians(angle);dx=math.sin(theta);dy=-math.cos(theta)
                factor=1/math.sqrt((dx/rx)**2+(dy/ry)**2)
                return cx+dx*factor,cy+dy*factor
            if abs(sweep)==360:E(group,'ellipse',cx=n(cx),cy=n(cy),rx=n(rx),ry=n(ry),**attrs);return
            a=point(start);z=point(start+sweep)
            path=f'M{n(a[0])} {n(a[1])} A{n(rx)} {n(ry)} 0 {int(abs(sweep)>180)} {int(sweep>0)} {n(z[0])} {n(z[1])}'
            if verb!=0:path+=f'L{n(cx)} {n(cy)}Z'
            E(group,'path',d=path,**attrs)
    elif family==7:
        if not shape:return
        if verb==0:attrs=dict(fill='none',stroke=color,stroke_width=n(max(penw,penh)),stroke_linejoin='bevel')
        d='M'+' L'.join(f'{n(x)} {n(y)}' for x,y in shape)
        # FramePoly traces the stored vertices, closing only when the last
        # vertex equals the first. Filled polygons close implicitly.
        if verb!=0:d+='Z'
        E(group,'path',d=d,fill_rule='evenodd',**attrs)
    else:
        if verb==0:attrs=dict(fill='none',stroke=color,stroke_width=n(max(penw,penh)))
        E(group,'path',d=region_path(shape),shape_rendering='crispEdges',**attrs)

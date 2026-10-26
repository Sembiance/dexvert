#!/usr/bin/env python3
# Vibe coded by Codex
"""Decode Lotus ScreenCam SCM movies. See screenCamVideo.txt for scope."""
from __future__ import annotations

import argparse
import collections
import dataclasses
import io
import json
import math
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import threading
import zlib
import contextlib

sys.dont_write_bytecode = True
VERSIONS = {b"1.0", b"2.0", b"2.1", b"3.0", b"3.1"}
ENTRY = struct.Struct("<HIIIII")


class FormatError(Exception):
    """Recognized but malformed ScreenCam data."""


class Unsupported(FormatError):
    """A recognized feature that cannot be faithfully converted."""


class NotScreenCam(FormatError):
    pass


class Reader:
    def __init__(self, data, base=0):
        self.data, self.pos, self.base = data, 0, base

    def take(self, n):
        if n < 0 or self.pos + n > len(self.data):
            raise FormatError(f"Truncated field at 0x{self.base + self.pos:x} (need {n} bytes)")
        v = self.data[self.pos:self.pos+n]
        self.pos += n
        return v

    def byte(self):
        return self.take(1)[0]

    def u16(self):
        return struct.unpack("<H", self.take(2))[0]

    def word(self, signed=False):
        v = self.byte()
        if v == 255:
            v = self.u16()
            return v - 65536 if signed and v >= 32768 else v
        return v - 256 if signed and v >= 128 else v

    def size(self):
        b = self.byte()
        v = b & 63
        for _ in range(b >> 6):
            v = (v << 8) | self.byte()
        return v


@dataclasses.dataclass
class Entry:
    kind: int
    ident: int
    offset: int
    size: int
    start: int
    duration: int


class Movie:
    def __init__(self, data):
        self.data = data
        self.warnings = []
        if len(data) < 11 or data[:7] != b"\x80SCMOVv" or data[10] != 0:
            raise NotScreenCam("Not a Lotus ScreenCam SCM movie (signature mismatch)")
        self.version = data[7:10].decode("ascii", "replace")
        if data[7:10] not in VERSIONS:
            raise Unsupported(f"Unsupported ScreenCam version {self.version}")
        if len(data) < 560:
            raise FormatError("ScreenCam header is truncated")
        self.flags, off, size, self.duration, legacy, self.width, self.height = struct.unpack_from("<HIIIHHH", data, 14)
        if self.flags not in (5, 7):
            raise Unsupported(f"Unsupported header flags 0x{self.flags:04x}")
        self.codepage = struct.unpack_from("<H", data, 36)[0]
        if size % 22:
            raise FormatError("Directory length is not a multiple of 22")
        if off < 560 or off+size > len(data):
            raise FormatError(f"Truncated directory: needs bytes {off}..{off+size}, file has {len(data)}; stream boundaries unavailable")
        if not (0 < self.width <= 16384 and 0 < self.height <= 16384):
            raise FormatError("Invalid screen dimensions")
        self.entries = [Entry(*ENTRY.unpack_from(data, p)) for p in range(off, off+size, 22)]
        self.byid = {}
        for e in self.entries:
            if e.ident in self.byid:
                raise FormatError(f"Duplicate object ID {e.ident}")
            if e.size and (e.offset < 560 or e.offset+e.size > len(data)):
                raise FormatError(f"Object {e.ident}, type {e.kind}, extends outside file")
            self.byid[e.ident] = e
        self.directory_offset, self.directory_size = off, size
        self.segments = []
        self.audio = []
        for e in self.entries:
            if e.kind == 1:
                if e.duration == 0:
                    self.warnings.append(f"Ignored inactive zero-duration screen descriptor {e.ident}")
                    continue
                if e.size != 102:
                    raise Unsupported(f"Screen descriptor size {e.size}, expected 102")
                d = self.payload(e)
                tick = struct.unpack_from("<I", d, 40)[0]
                w, h = struct.unpack_from("<HH", d, 46)
                initial, body, thumb, trim, length, original = struct.unpack_from("<IIIIII", d, 78)
                if trim:
                    raise Unsupported("Nonzero source trim requires unverified editing semantics")
                init = self.object(initial, 3)
                main = self.object(body, 4)
                self.segments.append((e, tick, w, h, init, main, trim, length, original))
            elif e.kind == 2:
                if e.size != 20:
                    raise Unsupported(f"Audio descriptor size {e.size}")
                d = self.payload(e)
                rate, bits, channels, codec, ref = struct.unpack_from("<HHH4sI", d, 6)
                self.audio.append((e, rate, bits, channels, codec, self.object(ref, 5)))
            elif e.kind not in {3, 4, 5, 13, 14, 21, 26}:
                raise Unsupported(f"Unsupported directory object type {e.kind}")
        self.segments.sort(key=lambda s:s[0].start)
        for previous, current in zip(self.segments, self.segments[1:]):
            if current[0].start < previous[0].start + previous[0].duration:
                raise Unsupported("Overlapping screen segments are not implemented")
        if not self.segments:
            raise FormatError("No active screen track")
        if not any(s[4].size or s[5].size for s in self.segments):
            raise FormatError("Screen track has no recorded graphics commands")
        self.inspect_auxiliary()

    def inspect_auxiliary(self):
        """Account for auxiliary objects and unreferenced physical file ranges."""
        self.metadata = []
        self.thumbnails = []
        for e in self.entries:
            if e.kind in (14, 26):
                fields = []
                r = Reader(self.payload(e), e.offset)
                try:
                    while r.pos < len(r.data):
                        tag, size = struct.unpack('<HI', r.take(6))
                        value = r.take(size)
                        fields.append({'tag':tag, 'bytes':size, 'hex':value.hex()})
                        if tag == 0:
                            if size or r.pos != len(r.data):
                                raise FormatError('Invalid metadata terminator')
                            break
                    else:
                        raise FormatError('Metadata lacks its terminator')
                except FormatError as error:
                    self.warnings.append(f'Ancillary object {e.ident}: {error}')
                self.metadata.append({'id':e.ident, 'type':e.kind, 'fields':fields})
            elif e.kind in (13, 21):
                info = {'id':e.ident, 'type':e.kind, 'bytes':e.size}
                data = self.payload(e)
                if data:
                    if e.kind == 13 and len(data) >= 12:
                        w,h,stride,depth,planes,reserved = struct.unpack_from('<6H',data)
                        colors = 1 << depth if depth <= 8 else 0
                        logical = 12 + colors*3 + stride*h
                        info.update(width=w,height=h,depth=depth,planes=planes,
                                    row_bytes=stride,logical_bytes=logical,
                                    allocation_tail=max(0,len(data)-logical))
                        if logical > len(data):
                            self.warnings.append(f'Thumbnail {e.ident} has no complete pixel array; movie graphics are independent')
                    elif e.kind == 21 and data[:2] == b'BM' and len(data) >= 54:
                        size, pixels = struct.unpack_from('<I4xI',data,2)
                        header,w,h,planes,depth,compression = struct.unpack_from('<IiiHHI',data,14)
                        info.update(width=w,height=h,depth=depth,planes=planes,
                                    compression=compression,pixel_offset=pixels,
                                    header_bytes=header,declared_bytes=size)
                        if size > len(data) or pixels > len(data):
                            self.warnings.append(f'Thumbnail {e.ident} is truncated')
                    else:
                        self.warnings.append(f'Thumbnail {e.ident} has an unrecognized ancillary layout')
                self.thumbnails.append(info)
        spans = sorted([(0,560),(self.directory_offset,self.directory_offset+self.directory_size)] +
                       [(e.offset,e.offset+e.size) for e in self.entries if e.size])
        self.unreferenced = []
        end = 0
        for start,stop in spans:
            if start > end:self.unreferenced.append([end,start])
            end = max(end,stop)
        if end < len(self.data):self.unreferenced.append([end,len(self.data)])
        if self.unreferenced:
            self.warnings.append('Unreferenced bytes outside directory objects are not interpreted')

    def payload(self, e):
        return self.data[e.offset:e.offset+e.size]

    def object(self, ident, kind):
        e = self.byid.get(ident)
        if e is None or e.kind != kind:
            raise FormatError(f"Missing type-{kind} object ID {ident}")
        return e

    def packets(self, e):
        pos, end = e.offset, e.offset + e.size
        while pos < end:
            if pos+6 > end:
                raise FormatError(f"Truncated packet at 0x{pos:x}")
            tick, size = struct.unpack_from("<IH", self.data, pos)
            if not size or pos+6+size > end:
                raise FormatError(f"Invalid packet size {size} at 0x{pos:x}")
            yield tick, self.data[pos+6:pos+6+size], pos+6
            pos += 6+size


class BlockCache:
    """ScreenCam's 128-slot, 49152-byte, compacting LRU block store."""
    def __init__(self):
        self.data = [b""] * 128
        self.offset = [0] * 128
        self.order = list(range(128))
        self.free = [(0, 49152)]

    def release(self, idx):
        if self.data[idx]:
            self.free.append((self.offset[idx], (len(self.data[idx])+3)&~3))
            merged = []
            for p,n in sorted(self.free):
                if merged and merged[-1][0]+merged[-1][1] == p:
                    merged[-1] = (merged[-1][0], merged[-1][1]+n)
                else:
                    merged.append((p,n))
            self.free = merged
            self.data[idx] = b""

    def read(self, r):
        tag = r.byte()
        if tag & 128:
            idx = tag & 127
            if not self.data[idx]:
                raise FormatError(f"Reference to empty bitmap cache slot {idx}")
        else:
            size = (tag << 8) | r.byte()
            payload = r.take(size)
            k = 127
            while k and not self.data[self.order[k-1]]:
                k -= 1
            idx = self.order[k]
            self.release(idx)
            self.data[idx] = payload
            need = (size+3)&~3
            for k,(p,n) in enumerate(self.free):
                if n >= need:
                    self.offset[idx] = p+n-need
                    if n == need:
                        del self.free[k]
                    else:
                        self.free[k] = (p,n-need)
                    break
            else:
                used = need
                evict = False
                for other in self.order:
                    if other == idx:
                        continue
                    n = (len(self.data[other])+3)&~3
                    if used+n+4 > 49152:
                        evict = True
                    if evict:
                        self.data[other] = b""
                    else:
                        self.offset[other] = used
                        used += n
                self.offset[idx] = 0
                self.free = [(used,49152-used)]
        self.order.remove(idx)
        self.order.insert(0,idx)
        return self.data[idx]


def unrle(data):
    r = Reader(data)
    out = bytearray()
    while r.pos < len(data):
        tag = r.byte()
        if tag & 128:
            out.extend(bytes([r.byte()]) * (tag & 127))
        else:
            out.extend(r.take(tag))
    return out


class Decoder:
    """Exact bytecode parser; rendering receives expanded, typed commands."""
    def __init__(self, emit=None):
        self.emit = emit or (lambda *a:None)
        self.counts = collections.Counter()
        self.reset()

    def reset(self):
        self.coords = [[0,0], [0,0], [0,0,0,0]]
        self.coord_cache = [[[0]*len(v) for _ in range(128)] for v in self.coords]
        self.color_value = [0]*4
        self.color_cache = [[0]*4 for _ in range(128)]
        self.blocks = BlockCache()
        self.bitmap = bytearray()
        self.poly = None
        self.region = None
        self.palette = [(0,0,0,0)]*256

    def coordinate(self, r, kind=0):
        c = r.byte()
        if c & 128:
            delta = self.coord_cache[kind][c&127]
        else:
            mask = r.byte() if kind == 2 else c
            raw = bytes(r.byte() if mask & (1<<i) else 0 for i in range(len(self.coords[kind])*2))
            delta = list(struct.unpack('<'+'h'*len(self.coords[kind]),raw))
            if kind == 2:
                for i,flag in enumerate([4,2,1]):
                    if c & flag:
                        delta[i] |= 256
                for i,flag in enumerate([64,32,16,8]):
                    if c & flag:
                        delta[i] = -delta[i]
                idx = (((delta[0]&3)*4+(delta[1]&3))*4+(delta[2]&3))*2+(delta[3]&1)
            else:
                if c & 16:
                    delta[0] |= 256
                if c & 32:
                    delta[0] = -delta[0]
                if c & 64:
                    delta[1] = -delta[1]
                idx = ((delta[0]&15)<<3)|(delta[1]&7)
            self.coord_cache[kind][idx] = delta
        result = [a+b for a,b in zip(self.coords[kind],delta)]
        self.coords[kind] = result
        return result[:]

    def rectangle(self, r):
        x,y,w,h = self.coordinate(r,2)
        return [x,y,x+w,y+h]

    def color(self, r, gdi=True):
        c = r.byte()
        if c & 128:
            delta = self.color_cache[c&127]
        else:
            delta = [r.byte() if c & (1<<i) else 0 for i in range(4)]
            idx = ((((delta[2]&0xcf)|(delta[0]>>2))>>3)|(delta[1]&0xe1))>>1
            self.color_cache[idx] = delta
        v = [(a+b)&255 for a,b in zip(self.color_value,delta)]
        self.color_value = v
        if gdi:
            return v[2] | (v[1]<<8) | (v[0]<<16) | (v[3]<<24)
        return bytes(v)

    def dib(self, r, op):
        compression = r.word() if op == 0x46 else 0
        tag, count, w = r.word(), r.word(), r.word()
        depth, indexed = tag&127, not(tag&128)
        if depth not in (1,2,4,8,16,24,32) or not w:
            raise Unsupported(f"DIB depth {depth}, width {w}")
        stride = (((w*4+7)//8+3)//2)&~1 if depth==2 else ((w*depth+31)//32)*4
        h = r.word() if compression else len(self.bitmap)//stride
        if compression not in (0,1,2,3):
            raise Unsupported(f"DIB compression {compression}")
        if indexed:
            colors = r.take(count)
        elif compression == 3:
            colors = r.take(12)
        else:
            colors = b''.join(self.color(r,False) for _ in range(count))
        pixels = self.bitmap
        if compression == 0:
            # The player derives height by integer division and leaves any tail unused.
            pixels = pixels[:stride*h]
            if self.emit is not None:
                # Vertical differences use unsigned byte addition, independently by column.
                import numpy as np
                a = np.frombuffer(pixels,dtype=np.uint8).reshape(h,stride)
                pixels = np.cumsum(a,axis=0,dtype=np.uint8).tobytes()
                if depth == 2:
                    a = np.frombuffer(pixels,dtype=np.uint8)
                    v = np.empty(a.size*2,dtype=np.uint8)
                    v[0::2] = ((a>>6)<<4)|((a>>4)&3)
                    v[1::2] = (((a>>2)&3)<<4)|(a&3)
                    pixels = v.tobytes()
                    depth = 4
        self.emit(0x100, [w,h,depth,compression,int(indexed),count,op,len(colors)], colors+pixels)

    def packet(self, data, offset=0):
        r = Reader(data,offset)
        while r.pos < len(data):
            at = r.pos
            op = r.byte()
            repeat = r.byte() if op&128 else 1
            op &= 127
            if not repeat:
                raise FormatError(f"Zero opcode repeat at 0x{offset+at:x}")
            for _ in range(repeat):
                self.counts[op] += 1
                a, blob = [], b''
                if op in (0,1):
                    a = self.coordinate(r)
                    if op == 0: a += [r.byte()]
                elif op == 2:
                    a = self.coordinate(r,2)+self.coordinate(r)+[r.byte()]
                elif op in (3,4):
                    a = self.coordinate(r,2)+[r.byte() if op==3 else 0xf0]
                elif op in (5,6,7):
                    a = self.coordinate(r,2)+self.coordinate(r,2)+[r.byte()]
                elif op == 8:
                    a = self.coordinate(r,2)+self.coordinate(r)
                elif op == 9:
                    n = r.word(); a = self.coordinate(r)+[n]; blob = r.take(n)
                elif op == 10:
                    a = self.coordinate(r); flags = r.byte(); a += [flags]
                    a += self.rectangle(r) if flags&128 else [0]*4
                    n = r.word(); a += [n]
                    if flags&64: a += [r.word(True) for _ in range(n)]
                    blob = r.take(n)
                elif op in (11,12,14):
                    a = self.rectangle(r)+self.rectangle(r)
                elif op in (13,20,52):
                    a = self.rectangle(r)
                elif op in (15,32,34):
                    a = self.coordinate(r)
                elif op == 16:
                    a = self.coordinate(r)+self.coordinate(r)
                elif op in (17,22,23):
                    a = self.coordinate(r)+[self.color(r)]
                    if op == 23: a += [r.word()]
                elif op in (18,19,73):
                    if self.poly is None:
                        n = r.word()
                        counts = [r.word() for _ in range(n)] if op==73 else [n]
                        self.poly = (counts,[])
                    counts, pts = self.poly
                    end = min(sum(counts), ((len(pts)//256)+1)*256)
                    while len(pts) < end: pts.append(self.coordinate(r))
                    if len(pts) == sum(counts):
                        a = [len(counts)]+counts+[v for pt in pts for v in pt]
                        self.poly = None
                    else:
                        continue
                elif op == 21:
                    a = self.rectangle(r)+self.coordinate(r,1)
                elif op in (24,25):
                    a = [self.color(r)]
                elif op in (26,27,28,29,30,48,50,65):
                    a = [r.word()]
                elif op == 31:
                    v = r.byte(); a = [v>>4,v&7]
                elif op in (33,35):
                    a = self.coordinate(r,1)
                elif op in (36,37):
                    a = [r.word() if op==36 else 0]+self.coordinate(r,1)+[self.color(r)]
                elif op in (38,41,44,45,53,54,55,57):
                    if op == 53: a = self.coordinate(r,1)
                elif op in (39,42,46):
                    a = [r.byte()]
                elif op == 40:
                    a = [r.word(),self.color(r),r.word(True)]
                elif op == 43:
                    a = [2,self.color(r),r.word()]
                elif op == 47:
                    a = [r.word(True) for _ in range(5)]
                    n = r.word(); a += [n]; blob = r.take(8+n)
                elif op == 49:
                    a = [r.word(),r.word()]
                elif op == 51:
                    lo,hi = r.word(),r.word()
                    if not 0 <= lo <= hi < 256: raise FormatError("Invalid palette range")
                    blob = b''.join(self.color(r,False) for _ in range(hi-lo+1))
                    a = [lo,hi]
                elif op in (56,74):
                    a = self.coordinate(r,2)+[r.word()]
                    if op == 74: a += [r.word()]
                    blob = bytes(self.bitmap)
                elif op == 58:
                    a = [r.u16(),r.u16()]
                elif op == 59:
                    self.reset()
                elif op == 61:
                    mode = r.word(); a=[mode]
                    if mode in (0,1): a += self.rectangle(r)
                    elif mode != 2: raise Unsupported(f"Saved-screen mode {mode}")
                elif op in (66,67,68):
                    if op == 67: self.allocation = r.size()
                    if op != 68: self.bitmap = bytearray()
                    self.bitmap.extend(unrle(self.blocks.read(r)))
                    if len(self.bitmap)>268435456: raise FormatError("Bitmap exceeds 256 MiB resource limit")
                    continue
                elif op in (69,70):
                    self.dib(r,op)
                    continue
                elif op in (71,72):
                    if self.region is None: self.region=(r.word(),[])
                    n,rects = self.region
                    end = min(n,((len(rects)//128)+1)*128)
                    while len(rects)<end:rects.append(self.rectangle(r))
                    if len(rects)==n:
                        a=[n]+[v for rect in rects for v in rect]; self.region=None
                    else: continue
                else:
                    raise Unsupported(f"Unknown graphics opcode 0x{op:02x} at 0x{offset+at:x}")
                self.emit(op,a,blob)


def audit(path):
    movie = Movie(Path(path).read_bytes())
    counts = collections.Counter()
    movie.stream_limits = {}
    movie.source_duration = movie.duration
    for segment in movie.segments:
        dec = Decoder()
        for e in segment[4:6]:
            base = None
            for tick,data,offset in movie.packets(e):
                if base is None:base=tick
                try:
                    dec.packet(data,offset)
                except Unsupported:
                    raise
                except FormatError as error:
                    if e.kind != 4:raise
                    stop=segment[0].start+((tick-base)&0xffffffff)-segment[6]
                    if stop<=segment[0].start:raise
                    movie.stream_limits[e.ident]=offset
                    movie.duration=min(movie.duration,stop)
                    movie.warnings.append(f'Partial recovery ends at {stop} ms: {error}')
                    counts.update(dec.counts)
                    return movie,counts
        counts.update(dec.counts)
    return movie, counts


def chunk(tag, payload):
    return tag+struct.pack('<I',len(payload))+payload+b'\0'*(len(payload)&1)


class AVI:
    """RIFF AVI, lossless ZMBV, 1 ms ticks, PCM, indexed dropped-frame holds."""
    def __init__(self, file, width, height, duration, audio=None):
        self.file = file
        self.width,self.height,self.duration = width,height,duration
        self.audio = audio
        self.tick = 0
        self.audio_sample = 0
        self.index = bytearray()
        self.frames = 0
        self.video_size = 0
        file.write(b'RIFF\0\0\0\0AVI ')
        avih = struct.pack('<14I',1000,0,0,0x110,duration,0,1+bool(audio),width*height*4,width,height,0,0,0,0)
        strh = struct.pack('<4s4sIHH8I4h',b'vids',b'ZMBV',0,0,0,0,1,1000,0,duration,width*height*4,0xffffffff,0,0,0,width,height)
        strf = struct.pack('<IiiHH4sIiiII',40,width,height,1,32,b'ZMBV',width*height*4,0,0,0,0)
        hdrl = chunk(b'avih',avih)+chunk(b'LIST',b'strl'+chunk(b'strh',strh)+chunk(b'strf',strf))
        if audio:
            rate,bits,channels,pcm = audio
            align = bits//8*channels
            count = len(pcm)//align
            ash = struct.pack('<4s4sIHH8I4h',b'auds',bytes(4),0,0,0,0,align,rate*align,0,count,rate*align,0xffffffff,align,0,0,0,0)
            af = struct.pack('<HHIIHH',1,channels,rate,rate*align,align,bits)
            hdrl += chunk(b'LIST',b'strl'+chunk(b'strh',ash)+chunk(b'strf',af))
        file.write(chunk(b'LIST',b'hdrl'+hdrl))
        self.list_start=file.tell();file.write(b'LIST\0\0\0\0movi');self.movi=self.list_start+8

    def write_chunk(self, tag, data, flags=0):
        pos=self.file.tell()-self.movi
        if pos+len(data)>0xffff0000:
            raise Unsupported('Output exceeds the 4 GiB AVI 1.0 limit')
        self.file.write(chunk(tag,data))
        self.index.extend(struct.pack('<4sIII',tag,flags,pos,len(data)))

    def holds(self, n):
        if n:
            if self.file.tell()+len(self.index)+24*n>0xffff0000:
                raise Unsupported('Output exceeds the 4 GiB AVI 1.0 limit')
            start=self.file.tell()-self.movi
            self.file.write((b'00dc'+bytes(4))*n)
            self.index.extend(b''.join(struct.pack('<4sIII',b'00dc',0,start+8*i,0) for i in range(n)))
            self.tick+=n

    def audio_until(self, ms):
        if not self.audio:return
        rate,bits,channels,pcm=self.audio;align=bits//8*channels
        end=min(len(pcm)//align,ms*rate//1000)
        if end>self.audio_sample:
            self.write_chunk(b'01wb',pcm[self.audio_sample*align:end*align],0x10)
            self.audio_sample=end

    def frame(self, ms, data, key):
        if ms<self.tick or ms>=self.duration:return
        while self.tick<ms:
            end=min(ms,((self.tick//1000)+1)*1000)
            self.holds(end-self.tick);self.audio_until(end)
        self.write_chunk(b'00dc',data,0x10 if key else 0)
        self.tick+=1;self.frames+=1;self.video_size+=len(data)

    def finish(self):
        while self.tick<self.duration:
            end=min(self.duration,((self.tick//1000)+1)*1000)
            self.holds(end-self.tick);self.audio_until(end)
        self.audio_until(self.duration)
        end=self.file.tell();self.file.seek(self.list_start+4);self.file.write(struct.pack('<I',end-self.movi));self.file.seek(end)
        self.file.write(chunk(b'idx1',self.index));end=self.file.tell()
        if end>0xffffffff:raise Unsupported('Output exceeds the 4 GiB AVI 1.0 limit')
        self.file.seek(4);self.file.write(struct.pack('<I',end-8));self.file.seek(end)


def prepare_audio(movie):
    if not movie.audio:return None
    formats={(a[1],a[2],a[3]) for a in movie.audio}
    if len(formats)!=1:raise Unsupported('Audio segments change sample format; resampling is not implemented')
    rate,bits,channels=formats.pop()
    if bits not in (8,16) or channels not in (1,2) or not rate:
        raise Unsupported(f'PCM audio format {rate} Hz/{bits} bits/{channels} channels')
    align=bits//8*channels
    size=(movie.duration*rate//1000)*align
    if size>536870912:raise Unsupported('Audio exceeds 512 MiB resource limit')
    pcm=bytearray(bytes([128 if bits==8 else 0])*size)
    previous_end=0
    for e,_,_,_,codec,obj in sorted(movie.audio,key=lambda a:a[0].start):
        if codec not in (b'NONE',bytes(4),b'\x01\0\0\0'):
            raise Unsupported(f'Audio compression tag {codec.hex()} is not yet implemented')
        src=movie.payload(obj)
        if codec==b'\x01\0\0\0':
            if (rate,bits,channels)!=(11025,8,1):
                raise Unsupported('VocalTec codec requires 11025 Hz, 8-bit mono output')
            src=decode_vocaltec(src)
        off=e.start*rate//1000*align
        limit=(e.start+e.duration)*rate//1000*align
        if off<previous_end:raise Unsupported('Overlapping audio segments require mixing')
        end=min(off+len(src)//align*align,limit,size)
        if end>off:pcm[off:end]=src[:end-off]
        previous_end=end
    return rate,bits,channels,bytes(pcm)


IMA_STEPS = (7,8,9,10,11,12,13,14,16,17,19,21,23,25,28,31,34,37,41,45,
             50,55,60,66,73,80,88,97,107,118,130,143,157,173,190,209,230,253,
             279,307,337,371,408,449,494,544,598,658,724,796,876,963,1060,
             1166,1282,1411,1552,1707,1878,2066,2272,2499,2749,3024,3327,
             3660,4026,4428,4871,5358,5894,6484,7132,7845,8630,9493,10442,
             11487,12635,13899,15289,16818,18500,20350,22385,24623,27086,
             29794,32767)
IMA_INDEX = (-1,-1,-1,-1,2,4,6,8)


def decode_vocaltec(data, sixteen=False):
    """VocalTec's IMA variant: 256-byte blocks, HIGH nibble first."""
    result=bytearray()
    for off in range(0,len(data),256):
        block=data[off:off+256]
        if len(block)<4:break
        predictor,index=struct.unpack_from('<hB',block)
        if index>88:raise FormatError(f'Invalid ADPCM step index {index} at audio offset {off+2}')
        values=[predictor]
        for b in block[4:]:
            for n in (b>>4,b&15):
                step=IMA_STEPS[index]
                diff=(step>>3)+(step if n&4 else 0)+(step>>1 if n&2 else 0)+(step>>2 if n&1 else 0)
                predictor=max(-32768,min(32767,predictor+(-diff if n&8 else diff)))
                index=max(0,min(88,index+IMA_INDEX[n&7]))
                values.append(predictor)
        if sixteen:result.extend(struct.pack('<'+'h'*len(values),*values))
        else:result.extend((v>>8)+128 for v in values)
    return bytes(result)


class Renderer:
    def __init__(self, directory=None):
        self.temp=None
        self.xvfb=None
        self.proc=None
        self.error=b''
        exe=Path(__file__).resolve().with_name('screenCamVideoRender.exe')
        if not exe.exists():raise Unsupported(f'Missing rendering helper: {exe}')
        wine=shutil.which('wine64') or shutil.which('wine')
        if not wine:raise Unsupported('Wine is required to render the recorded Windows GDI operations')
        xvfb=shutil.which('Xvfb')
        if not xvfb:raise Unsupported('Xvfb is required for the isolated GDI renderer')
        env=os.environ.copy();env['WINEDEBUG']='-all'
        # A private prefix prevents conversion from changing the user's Wine setup.
        self.temp=tempfile.TemporaryDirectory(prefix='screencam-render-')
        env['WINEPREFIX']=str(Path(self.temp.name)/'wine');env['WINEARCH']='win64'
        rd,wr=os.pipe()
        self.xvfb=subprocess.Popen([xvfb,'-displayfd',str(wr),'-screen','0','1280x1024x24','-nolisten','tcp'],pass_fds=(wr,),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        os.close(wr)
        with os.fdopen(rd,'rb') as fd:
            display=fd.readline().strip().decode()
        if not display:raise FormatError('Could not start Xvfb')
        env['DISPLAY']=':'+display
        self.env=env
        self.proc=subprocess.Popen([wine,str(exe)],env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        def collect():
            self.error=self.proc.stderr.read()
        self.thread=threading.Thread(target=collect,daemon=True);self.thread.start()

    def emit(self, op, args=(), data=b''):
        values=struct.pack('<'+'I'*len(args),*(x&0xffffffff for x in args))
        try:
            self.proc.stdin.write(struct.pack('<III',len(values)+len(data),op,len(args)))
            self.proc.stdin.write(values)
            if data:self.proc.stdin.write(data)
        except BrokenPipeError:
            self.thread.join(timeout=1)
            raise FormatError('Renderer failed: '+self.error.decode(errors='replace')[-2000:]) from None

    def read(self,n):
        v=bytearray()
        while len(v)<n:
            b=self.proc.stdout.read(n-len(v))
            if not b:
                self.thread.join(timeout=1)
                raise FormatError('Renderer stopped: '+self.error.decode(errors='replace')[-2000:])
            v.extend(b)
        return bytes(v)

    def capture(self,key):
        self.emit(0x102,[int(key)]);self.proc.stdin.flush()
        n=struct.unpack('<I',self.read(4))[0]
        if n>268435456:raise FormatError('Invalid renderer response')
        return self.read(n)

    def close(self):
        if self.proc:
            with contextlib.suppress(OSError):self.proc.stdin.close()
            try:self.proc.wait(timeout=10)
            except subprocess.TimeoutExpired:self.proc.kill();self.proc.wait()
            self.thread.join(timeout=2)
        if hasattr(self,'env'):
            ws=shutil.which('wineserver')
            if ws:subprocess.run([ws,'-k'],env=self.env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        if self.xvfb:self.xvfb.terminate();self.xvfb.wait()
        if self.temp:self.temp.cleanup()

    def __enter__(self):return self
    def __exit__(self,*exc):self.close()


def convert(input_file, output_file, verbose=False, renderer=None):
    source=Path(input_file);dest=Path(output_file)
    if source.resolve()==dest.resolve():raise FormatError('Input and output must be different files')
    movie,counts=audit(source)
    pcm=prepare_audio(movie)
    if any((s[2],s[3])!=(movie.width,movie.height) for s in movie.segments):
        raise Unsupported('Screen dimensions change within the movie')
    if not movie.duration:raise FormatError('Movie duration is zero')
    owned=renderer is None
    if owned:renderer=Renderer()
    tmp=None
    stats={}
    try:
        with tempfile.NamedTemporaryFile(prefix='.'+dest.name+'.',suffix='.tmp',dir=dest.parent,delete=False) as output:
            tmp=Path(output.name)
            avi=AVI(output,movie.width,movie.height,movie.duration,pcm)
            compressor=None
            last_key=-10000
            for e,tick,w,h,initial,body,trim,length,original in movie.segments:
                renderer.emit(0x101,[w,h]);dec=Decoder(renderer.emit)
                for ts,data,offset in movie.packets(initial):dec.packet(data,offset)
                limit=movie.stream_limits.get(body.ident,len(movie.data)+1)
                packets=iter(p for p in movie.packets(body) if p[2]<limit);first=next(packets,None)
                if first is None:continue
                base=first[0]
                pending=first
                while pending is not None:
                    ts,data,offset=pending
                    relative=(ts-base)&0xffffffff
                    ms=e.start+relative-trim
                    if ms>=min(movie.duration,e.start+e.duration):break
                    dec.packet(data,offset)
                    pending=next(packets,None)
                    while pending is not None and pending[0]==ts:
                        dec.packet(pending[1],pending[2]);pending=next(packets,None)
                    if ms<e.start:continue
                    key=compressor is None or ms-last_key>=5000 or relative==0
                    raw=renderer.capture(key)
                    if not raw:continue
                    if key:compressor=zlib.compressobj(6);last_key=ms
                    encoded=(b'\x01\x00\x01\x01\x08\x10\x10' if key else b'\x00')+compressor.compress(raw)+compressor.flush(zlib.Z_SYNC_FLUSH)
                    avi.frame(ms,encoded,key)
            if avi.frames==0:raise FormatError('No displayable frames were recovered')
            # Explicit terminal pictures prevent readers from extrapolating the
            # last sparse update's duration or discarding a one-picture movie.
            for ms in (movie.duration-2,movie.duration-1):
                if ms < avi.tick:continue
                raw=renderer.capture(True)
                compressor=zlib.compressobj(6)
                encoded=b'\x01\x00\x01\x01\x08\x10\x10'+compressor.compress(raw)+compressor.flush(zlib.Z_SYNC_FLUSH)
                avi.frame(ms,encoded,True)
            avi.finish()
            stats={'version':movie.version,'width':movie.width,'height':movie.height,'duration_ms':movie.duration,'source_duration_ms':movie.source_duration,'stored_frames':avi.frames,'audio':bool(pcm),'warnings':movie.warnings,'opcodes':dict(sorted(counts.items()))}
        os.chmod(tmp,0o664);os.replace(tmp,dest);tmp=None
        if verbose:
            details = dict(stats,metadata=movie.metadata,thumbnails=movie.thumbnails,
                           unreferenced_ranges=movie.unreferenced,
                           objects=[dataclasses.asdict(e) for e in movie.entries])
            log=dest.with_name(dest.name+'.json');log.write_text(json.dumps(details,indent=2)+'\n');os.chmod(log,0o664)
        return stats
    finally:
        if tmp is not None:tmp.unlink(missing_ok=True)
        if owned:renderer.close()


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('inputFile')
    ap.add_argument('outputFile')
    ap.add_argument('-verbose','--verbose',action='store_true')
    args = ap.parse_args()
    try:
        stats=convert(args.inputFile,args.outputFile,args.verbose)
        for warning in stats['warnings']:
            print(f'screenCamVideo: warning: {warning}',file=sys.stderr)
        if args.verbose:print(json.dumps(stats,indent=2))
    except (FormatError,OSError,ImportError) as exc:
        print(f'screenCamVideo: {exc}',file=sys.stderr)
        sys.exit(1)

#!/usr/bin/env python3
# Vibe coded by Codex
"""Decode Hiroshi Toda's MOV2 (FM Towns MOVE / Ugoku Zansu) movies.

Only the requested AVI is created unless -verbose is supplied. See the adjacent
format specification for byte layouts, compatibility choices, and limitations.
The image decoder and lossless PNG-in-AVI writer use Python's standard library.
"""
from __future__ import annotations

import argparse
import array
import collections
import dataclasses
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys
import zlib

WIDTH, HEIGHT, STRIDE = 320, 240, 640
BUFFER_SIZE = STRIDE * HEIGHT
KNOWN_BLOCKS = {0x0222, 0x1222, 0x1422, 0x2222, 0x2422, 0x3010, 0x3110, 0xF000}


class FormatError(Exception):
    """Unrecognized or unsupported input; never create an output for this."""


class Damaged(Exception):
    """A bounded record cannot be decoded further."""


class Reader:
    __slots__ = ('data', 'pos', 'base')

    def __init__(self, data, base=0):
        self.data, self.pos, self.base = data, 0, base

    def take(self, n):
        if n < 0 or self.pos + n > len(self.data):
            raise Damaged(f'truncated field at 0x{self.base + self.pos:x}: '
                          f'need {n} bytes, have {len(self.data) - self.pos}')
        p = self.pos
        self.pos += n
        return self.data[p:self.pos]

    def u8(self):
        if self.pos >= len(self.data):
            raise Damaged(f'truncated byte at 0x{self.base + self.pos:x}')
        n = self.data[self.pos]
        self.pos += 1
        return n

    def u16(self):
        if self.pos + 2 > len(self.data):
            raise Damaged(f'truncated word at 0x{self.base + self.pos:x}')
        n = struct.unpack_from('<H', self.data, self.pos)[0]
        self.pos += 2
        return n

    def u32(self):
        if self.pos + 4 > len(self.data):
            raise Damaged(f'truncated dword at 0x{self.base + self.pos:x}')
        n = struct.unpack_from('<I', self.data, self.pos)[0]
        self.pos += 4
        return n

    def length(self):
        n = self.u8()
        if n == 255:
            n = self.u16()
            if n == 65535:
                n = self.u32()
        return n


@dataclasses.dataclass
class Block:
    kind: int
    offset: int
    size: int
    available: int


@dataclasses.dataclass
class Frame:
    number: int
    offset: int
    size: int
    scroll_x: int
    scroll_y: int
    wait: int
    loop: int
    sounds: tuple
    blocks: list


class Movie:
    def __init__(self, data, source=None):
        self.data = data
        self.source = Path(source) if source is not None else None
        self.warnings = []
        self._warnings = set()
        self.frames = []
        self.block_counts = collections.Counter()
        self.byte_ranges = []
        self.decode_errors = 0
        self.trailer = None
        if data[:4] != b'MOV2':
            raise FormatError('not an FM Towns MOV2 movie (missing MOV2 signature)')
        if len(data) < 256:
            raise FormatError('MOV2 signature, but the 256-byte header is truncated')
        (self.depth, self.data_size, self.frame_count, w, h, stride,
         self.main_wait) = struct.unpack_from('<7I', data, 4)
        if (self.depth, w, h, stride) != (16, WIDTH, HEIGHT, STRIDE):
            raise FormatError(f'unsupported MOV2 layout: {w}x{h}, {self.depth} bits, '
                              f'{stride} bytes/row; supported layout is 320x240/16/640')
        self.rect = struct.unpack_from('<4H', data, 32)
        if self.rect == (0, 0, 0, 0):
            self.rect = (0, 0, WIDTH-1, HEIGHT-1)
        x0, y0, x1, y1 = self.rect
        if not (0 <= x0 <= x1 < WIDTH and 0 <= y0 <= y1 < HEIGHT):
            self.warn('invalid display rectangle; using the complete 320x240 canvas')
            self.rect = (0, 0, WIDTH-1, HEIGHT-1)
        self.timing_mode = data[150] & 1
        if data[150] & 0xfe:
            self.warn('unassigned timing-mode bits are set; only bit 0 is defined')
        if any(data[54:56]) or any(data[151:256]):
            self.warn('nonzero reserved header bytes have no defined playback operation')
        self.fm_name = self.name(data[40:48], '.FMB')
        self.pcm_name = self.name(data[56:64], '.PMB')
        self.fm_instruments = list(data[48:54])
        self.pcm_instruments = list(data[64:72])
        self.pan = [max(-64, min(63, n)) for n in struct.unpack_from('<14b', data, 136)]
        self.snd_names = []
        self.snd_capacities = []
        for i in range(8):
            field = data[72 + i*8:80 + i*8]
            self.snd_names.append(self.name(field, '.SND') if field[0] else '')
            self.snd_capacities.append(0 if field[0] else struct.unpack_from('<I', field, 4)[0])
            if not field[0] and any(field[1:4]):
                self.warn(f'SND buffer {i} has nonzero unused name-prefix bytes')
        self.byte_ranges.append((0, 256, 'main_header'))
        declared_end = 256 + self.data_size
        end = min(declared_end, len(data))
        if declared_end > len(data):
            self.warn(f'truncated movie body: declared end 0x{declared_end:x}, '
                      f'physical end 0x{len(data):x}')
        p = 256
        # Follow lengths, never scan for plausible frame signatures.
        while p < end:
            if end-p < 32:
                self.byte_ranges.append((p, end, 'truncated_frame_header'))
                self.warn(f'{end-p} bytes of an incomplete frame header at 0x{p:x}')
                break
            num, size, sx, sy, wait, loop = struct.unpack_from('<II4H', data, p)
            sounds = tuple(tuple(data[p+k:p+k+4]) for k in (16, 20, 24, 28))
            frame = Frame(num, p, size, sx, sy, wait, loop, sounds, [])
            if num != len(self.frames):
                self.warn(f'frame at 0x{p:x} has page {num}; sequential index is {len(self.frames)}')
            self.byte_ranges.append((p, p+32, 'frame_header'))
            body_end = min(p+32+size, end)
            if p+32+size > end:
                self.warn(f'page {num}: declared frame payload extends beyond the movie body')
            r = Reader(memoryview(data)[p+32:body_end], p+32)
            try:
                if size:
                    count = r.u16()
                    self.byte_ranges.append((p+32, p+34, 'block_count'))
                    for _ in range(count):
                        start = r.base+r.pos
                        kind, length = struct.unpack('<HI', r.take(6))
                        self.byte_ranges.append((start, start+6, 'block_header'))
                        available = min(length, len(r.data)-r.pos)
                        block = Block(kind, r.base+r.pos, length, available)
                        frame.blocks.append(block)
                        self.block_counts[kind] += 1
                        self.byte_ranges.append((block.offset, block.offset+available,
                                                 f'block_{kind:04x}'))
                        if kind not in KNOWN_BLOCKS:
                            self.warn(f'unknown MOV2 extension block 0x{kind:04x}; '
                                      'skipped using its declared length')
                        r.pos += available
                        if available != length:
                            raise Damaged(f'truncated block 0x{kind:04x} at 0x{block.offset:x}')
                    if r.pos != len(r.data):
                        self.byte_ranges.append((r.base+r.pos, body_end, 'unused_frame_tail'))
                        self.warn(f'{len(r.data)-r.pos} unused frame bytes at 0x{r.base+r.pos:x}')
            except Damaged as exc:
                self.warn(str(exc))
                # Includes partially consumed fields; contiguous coverage is audited separately.
                self.byte_ranges.append((r.base+r.pos, body_end, 'truncated_block_fields'))
            self.frames.append(frame)
            p += 32+size
        if len(self.frames) != self.frame_count:
            self.warn(f'header declares {self.frame_count} frames; recovered {len(self.frames)}')
        if declared_end < len(data):
            tail = data[declared_end:]
            self.trailer = {'offset': declared_end, 'length': len(tail),
                            'sha256': hashlib.sha256(tail).hexdigest()}
            if len(tail) >= 32:
                num, size = struct.unpack_from('<II', tail)
                self.trailer.update(page=num, declared_payload_size=size,
                                    available_payload_size=len(tail)-32)
            self.byte_ranges.append((declared_end, len(data), 'outside_declared_movie'))
            self.warn(f'{len(tail)} trailing bytes outside the declared movie body at '
                      f'0x{declared_end:x}; not played')
        if not self.frames:
            raise FormatError('identified MOV2, but no recoverable frame exists')
        self.has_zero_wait = any(self.main_wait+f.wait == 0 for f in self.frames)
        self.has_sound_events = any(any(e[0] for e in f.sounds) for f in self.frames)
        self.has_loops = any(f.loop for f in self.frames)

    @staticmethod
    def name(field, extension):
        name = field.split(b'\0', 1)[0].decode('cp932', errors='replace')
        return name + extension if name else ''

    def warn(self, msg):
        if msg not in self._warnings:
            self._warnings.add(msg)
            self.warnings.append(msg)

    def validate(self):
        """Parse all image operands before opening the output."""
        for frame in self.frames:
            for block in frame.blocks:
                try:
                    for _ in operations(self.data, block):
                        pass
                except Damaged as exc:
                    self.decode_errors += 1
                    self.warn(f'page {frame.number}: {exc}; retaining complete earlier operations')

    def schedule(self, legacy=False, limit=10_000_000):
        """One movie traversal, with its finite internal FOR/NEXT loops."""
        stack = []
        index = emitted = 0
        while index < len(self.frames):
            if emitted >= limit:
                raise FormatError(f'expanded playback exceeds the {limit:,}-frame safety limit')
            f = self.frames[index]
            yield index
            emitted += 1
            control = f.loop
            if 0 < control < 0x8000:
                if not stack or stack[-1][0] != index:
                    if len(stack) >= 8:
                        self.warn(f'page {f.number}: loop nesting exceeds eight; extra start ignored')
                    else:
                        stack.append([index, control if legacy else control-1])
            elif control >= 0x8000:
                if not stack:
                    self.warn(f'page {f.number}: unmatched loop end ignored')
                elif stack[-1][1]:
                    stack[-1][1] -= 1
                    index = stack[-1][0]
                    continue
                else:
                    stack.pop()
            index += 1
        if stack:
            self.warn('unterminated loop start at end of movie; no backward jump invented')

    def metadata(self):
        return {
            'format': 'FM Towns MOV2 / MOVE / Ugoku Zansu',
            'input_bytes': len(self.data), 'declared_body_bytes': self.data_size,
            'declared_frames': self.frame_count, 'recovered_frames': len(self.frames),
            'canvas': [WIDTH, HEIGHT], 'display_rectangle': self.rect,
            'main_wait_ticks': self.main_wait, 'timing_mode': self.timing_mode,
            'zero_delay_present': self.has_zero_wait,
            'fmb': self.fm_name, 'pmb': self.pcm_name, 'snd': self.snd_names,
            'snd_buffer_capacities': self.snd_capacities,
            'fm_instruments': self.fm_instruments, 'pcm_instruments': self.pcm_instruments,
            'pan': self.pan, 'reserved_header_hex': self.data[151:256].hex(),
            'blocks': {f'{k:04x}': v for k, v in self.block_counts.items()},
            'trailer': self.trailer, 'warnings': self.warnings,
            'byte_ranges': self.byte_ranges,
            'frames': [dataclasses.asdict(f) for f in self.frames],
        }


def operations(data, block):
    """Yield bounded drawing operations; no pixel-content heuristics."""
    if block.kind not in KNOWN_BLOCKS or not block.available:
        return
    r = Reader(memoryview(data)[block.offset:block.offset+block.available], block.offset)
    kind = block.kind

    def runs(unit, style, pattern=None):
        for _ in range(r.u16()):
            high = r.u16() << 16
            count = r.u16()
            for _ in range(count):
                address = high + r.u16()
                length = r.length()
                size = length * unit
                if address & 1 or address + size > BUFFER_SIZE:
                    raise Damaged(f'invalid image write at 0x{r.base+r.pos:x}: '
                                  f'address {address}, length {size}')
                if style == 'literal':
                    yield ('literal', address, r.take(size))
                else:
                    value = r.take(unit) if pattern is None else pattern
                    yield ('fill', address, value, length)

    if kind in (0x1222, 0x1422):
        unit = 2 if kind == 0x1222 else 4
        for _ in range(r.u16()):
            value = r.take(unit)
            yield from runs(unit, 'fill', value)
    elif kind in (0x0222, 0x2222, 0x2422):
        yield from runs(4 if kind == 0x2422 else 2,
                        'fill' if kind == 0x0222 else 'literal')
    elif kind in (0x3010, 0x3110):
        count = r.u16() if kind == 0x3010 else 300
        for i in range(count):
            dest = r.u32() if kind == 0x3010 else (i//20)*16*STRIDE + (i%20)*32
            x, y = r.u16(), r.u16()
            if dest & 1 or dest//STRIDE > HEIGHT-16 or (dest%STRIDE)//2 > WIDTH-16:
                raise Damaged(f'invalid motion destination {dest} at 0x{r.base+r.pos:x}')
            if x > WIDTH-16 or y > HEIGHT-16:
                raise Damaged(f'invalid motion source ({x},{y}) at 0x{r.base+r.pos:x}')
            yield ('motion', dest, y*STRIDE+x*2)
    elif kind == 0xF000:
        channel, length = r.u32(), r.u32()
        if channel >= 8:
            raise Damaged(f'invalid SND buffer {channel}')
        yield ('sound', channel, bytes(r.take(length)))
    if r.pos != len(r.data):
        raise Damaged(f'{len(r.data)-r.pos} unconsumed bytes in block 0x{kind:04x} '
                      f'at 0x{r.base+r.pos:x}')


class Decoder:
    def __init__(self, movie, legacy=False):
        self.movie = movie
        self.legacy = legacy
        self.buffer = bytearray(BUFFER_SIZE)

    def frame(self, index):
        f = self.movie.frames[index]
        previous = bytes(self.buffer)
        sound_updates = []
        for block in f.blocks:
            try:
                for op in operations(self.movie.data, block):
                    kind, address = op[:2]
                    if kind == 'fill':
                        pixels = bytes(op[2]) * op[3]
                        self.buffer[address:address+len(pixels)] = pixels
                    elif kind == 'literal':
                        self.buffer[address:address+len(op[2])] = op[2]
                    elif kind == 'motion':
                        src = op[2]
                        for y in range(16):
                            d, s = address+y*STRIDE, src+y*STRIDE
                            self.buffer[d:d+32] = previous[s:s+32]
                    else:
                        sound_updates.append(op[1:])
            except Damaged:
                # Already diagnosed by validate(); complete earlier operations survive.
                pass
        display = self.buffer
        if self.legacy and (f.scroll_x or f.scroll_y):
            x, y = f.scroll_x, f.scroll_y
            if x < WIDTH and y < HEIGHT:
                display = b''.join(
                    self.buffer[((row+y)%HEIGHT)*STRIDE+x*2:((row+y)%HEIGHT+1)*STRIDE] +
                    self.buffer[((row+y)%HEIGHT)*STRIDE:((row+y)%HEIGHT)*STRIDE+x*2]
                    for row in range(HEIGHT))
            else:
                self.movie.warn(f'page {f.number}: invalid legacy scroll ignored')
        x0, y0, x1, y1 = self.movie.rect
        cropped = b''.join(display[y*STRIDE+x0*2:y*STRIDE+(x1+1)*2]
                           for y in range(y0, y1+1))
        return cropped, sound_updates


# Bit 15 is the hardware transparency bit. A standalone movie has a black
# underlay; RGB is preserved for opaque pixels. The encoders clear bit 15.
RGB_TABLE = tuple(bytes((((v >> 5) & 31)*255//31,
                         ((v >> 10) & 31)*255//31, (v & 31)*255//31))
                  if not v & 0x8000 else b'\0\0\0' for v in range(65536))


def png_image(pixels, width, height):
    words = array.array('H', pixels)
    if sys.byteorder != 'little':
        words.byteswap()
    rgb = b''.join(map(RGB_TABLE.__getitem__, words))
    raw = b''.join(b'\0'+rgb[y*width*3:(y+1)*width*3] for y in range(height))

    def chunk(kind, payload):
        return (struct.pack('>I', len(payload)) + kind + payload +
                struct.pack('>I', zlib.crc32(kind+payload)))
    return (b'\x89PNG\r\n\x1a\n' +
            chunk(b'IHDR', struct.pack('>2I5B', width, height, 8, 2, 0, 0, 0)) +
            chunk(b'IDAT', zlib.compress(raw, 6)) + chunk(b'IEND', b''))


def riff_chunk(kind, payload):
    return kind + struct.pack('<I', len(payload)) + payload + bytes(len(payload) & 1)


class AviWriter:
    """RIFF AVI 1.0, lossless PNG video and optional stereo PCM audio."""
    def __init__(self, stream, width, height, ticks, rate, audio_rate=0):
        self.stream, self.index = stream, bytearray()
        self.width, self.height, self.ticks, self.rate = width, height, ticks, rate
        self.audio_rate = audio_rate
        self.video_count = self.audio_samples = self.max_packet = 0
        header = self.header()
        stream.write(b'RIFF\0\0\0\0AVI ' + header)
        self.movi_header = stream.tell()
        stream.write(b'LIST\0\0\0\0movi')
        self.movi_base = self.movi_header + 8

    def header(self):
        avih = struct.pack('<14I', round(1_000_000/self.rate), 0, 0, 0x110,
                           self.ticks, 0, 2 if self.audio_rate else 1,
                           self.max_packet, self.width, self.height, 0, 0, 0, 0)
        strh = struct.pack('<4s4sIHH8I4h', b'vids', b'MPNG', 0, 0, 0,
                           0, 1, self.rate, 0, self.ticks, self.max_packet,
                           0xffffffff, 0, 0, 0, self.width, self.height)
        strf = struct.pack('<IiiHH4sIiiII', 40, self.width, self.height, 1, 24,
                           b'MPNG', self.width*self.height*3, 0, 0, 0, 0)
        video = riff_chunk(b'LIST', b'strl'+riff_chunk(b'strh', strh)+riff_chunk(b'strf', strf))
        audio = b''
        if self.audio_rate:
            sh = struct.pack('<4s4sIHH8I4h', b'auds', bytes(4), 0, 0, 0, 0,
                             4, self.audio_rate*4, 0, self.audio_samples,
                             65536, 0xffffffff, 4, 0, 0, 0, 0)
            sf = struct.pack('<HHIIHH', 1, 2, self.audio_rate, self.audio_rate*4, 4, 16)
            audio = riff_chunk(b'LIST', b'strl'+riff_chunk(b'strh', sh)+riff_chunk(b'strf', sf))
        return riff_chunk(b'LIST', b'hdrl'+riff_chunk(b'avih', avih)+video+audio)

    def packet(self, kind, data, keyframe=False):
        pos = self.stream.tell()
        if pos+len(data)+len(self.index)+32 >= 0xfffffff0:
            raise FormatError('output exceeds AVI 1.0 4-GiB limit')
        self.stream.write(riff_chunk(kind, data))
        self.index.extend(struct.pack('<4sIII', kind, 0x10 if keyframe else 0,
                                      pos-self.movi_base, len(data)))
        self.max_packet = max(self.max_packet, len(data))

    def video(self, png, duration):
        if duration <= 0:
            return
        self.packet(b'00dc', png, bool(png))
        self.video_count += 1
        # AVI's empty video chunks explicitly repeat the last decoded image.
        empty = b'00dc\0\0\0\0'
        for _ in range(duration-1):
            pos = self.stream.tell()
            self.stream.write(empty)
            self.index.extend(struct.pack('<4sIII', b'00dc', 0, pos-self.movi_base, 0))
        self.video_count += duration-1

    def audio(self, pcm):
        if pcm:
            self.packet(b'01wb', pcm, True)
            self.audio_samples += len(pcm)//4

    def finish(self):
        if self.video_count != self.ticks:
            raise FormatError(f'internal timeline mismatch: {self.video_count} != {self.ticks}')
        end_movi = self.stream.tell()
        self.stream.write(riff_chunk(b'idx1', self.index))
        end = self.stream.tell()
        if end >= 0x100000000:
            raise FormatError('output exceeds AVI 1.0 4-GiB limit')
        self.stream.seek(4)
        self.stream.write(struct.pack('<I', end-8))
        self.stream.seek(12)
        self.stream.write(self.header())
        self.stream.seek(self.movi_header+4)
        self.stream.write(struct.pack('<I', end_movi-self.movi_header-8))
        self.stream.seek(end)


def companion(movie, name):
    if not name or movie.source is None:
        return None
    # DOS companion names are basenames. Never follow a name into another folder.
    if '/' in name or '\\' in name or ':' in name or name.startswith('.'):
        movie.warn(f'invalid companion basename {name!r}')
        return None
    matches = [p for p in movie.source.parent.iterdir()
               if p.is_file() and p.name.casefold() == name.casefold()]
    if len(matches) == 1:
        return matches[0]
    movie.warn(f'missing companion {name}' if not matches else f'ambiguous companion {name}')
    return None


class Audio:
    """Audio availability is explicit; absent instruments cannot be synthesized."""
    def __init__(self, movie):
        self.movie = movie
        self.available = False
        self.missing = []
        self.unsupported = []
        for name in [movie.fm_name, movie.pcm_name, *movie.snd_names]:
            if name:
                path = companion(movie, name)
                if path is None:
                    self.missing.append(name)
                else:
                    self.unsupported.append(name)
        if self.unsupported:
            movie.warn('external sound rendering is not implemented for: ' +
                       ', '.join(self.unsupported))
        if movie.has_sound_events:
            movie.warn('sound commands are parsed, but this export has no audio: '
                       'external FM/PCM synthesis is not yet implemented and/or sound assets are missing')
        if movie.block_counts[0xF000]:
            movie.warn('embedded SND upload blocks are parsed but audio rendering is not implemented')


def convert(input_file, output_file, *, verbose=False, zero_wait_fps=10,
            legacy=False, max_frames=10_000_000):
    source, output = Path(input_file), Path(output_file)
    if source.resolve() == output.resolve():
        raise FormatError('input and output must be different files')
    if output.exists():
        raise FormatError(f'output already exists: {output}; choose a new path')
    sidecar = Path(str(output)+'.json')
    if verbose and sidecar.exists():
        raise FormatError(f'metadata output already exists: {sidecar}')
    if zero_wait_fps not in (10, 15, 30, 60):
        raise FormatError('zero-wait rate must be 10, 15, 30, or 60 fps')
    if max_frames < 1:
        raise FormatError('maximum frame count must be positive')
    # Reject unrelated signatures without reading a potentially enormous file.
    with source.open('rb') as f:
        prefix = f.read(256)
        if prefix[:4] != b'MOV2':
            raise FormatError('not an FM Towns MOV2 movie (missing MOV2 signature)')
        if len(prefix) < 256:
            raise FormatError('MOV2 signature, but the 256-byte header is truncated')
        if (struct.unpack_from('<I', prefix, 4)[0],
                *struct.unpack_from('<3I', prefix, 16)) != (16, WIDTH, HEIGHT, STRIDE):
            raise FormatError('unsupported MOV2 image layout; expected 320x240/16/640')
        data = prefix + f.read()
    movie = Movie(data, source)
    movie.validate()
    audio = Audio(movie)
    rate = math.lcm(60, zero_wait_fps)
    schedule = array.array('I', movie.schedule(legacy, max_frames))
    durations = [((movie.main_wait+movie.frames[i].wait)*rate//60
                  if movie.main_wait+movie.frames[i].wait else rate//zero_wait_fps)
                 for i in schedule]
    if movie.has_zero_wait:
        movie.warn(f'zero-delay frames use the explicit export policy {zero_wait_fps} fps; '
                   'the speed of an early unsynchronized player is not recoverable')
    if legacy:
        movie.warn('legacy compatibility selected: scroll offsets enabled; loop count means extra repeats')
    if not legacy and any(f.scroll_x or f.scroll_y for f in movie.frames):
        movie.warn('legacy scroll fields are retained but ignored by the 1993 playback profile; '
                   'use --legacy-player to reproduce early-player scrolling')
    # Before-display timing holds the preceding image during the new frame's
    # delay. One terminal tick makes the final display event visible in an AVI.
    terminal = rate//60 if movie.timing_mode == 0 else 0
    ticks = sum(durations) + terminal
    if ticks > 0xffffffff or ticks * 24 > 0xffff0000:
        raise FormatError('expanded timeline exceeds AVI 1.0 index limits')
    x0, y0, x1, y1 = movie.rect
    width, height = x1-x0+1, y1-y0+1
    decoder = Decoder(movie, legacy)
    last = png_image(bytes(width*height*2), width, height)
    previous_png = None
    # Cache cyclic transitions only for movies with loops. Input-state hashes
    # prevent incorrect reuse of a delta frame after a different predecessor.
    cache = collections.OrderedDict()
    cache_bytes = 0
    png_cache = collections.OrderedDict()
    stats = {'output': str(output), 'expanded_source_frames': len(schedule),
             'avi_frames': ticks, 'avi_rate': rate, 'duration_seconds': ticks/rate,
             'width': width, 'height': height, 'audio': False,
             'zero_wait_fps': zero_wait_fps, 'player_profile': '1991' if legacy else '1993',
             'missing_sound_assets': audio.missing, 'unsupported_sound_assets': audio.unsupported}
    created_output = False
    try:
        with output.open('xb') as stream:
            created_output = True
            os.fchmod(stream.fileno(), 0o664)
            avi = AviWriter(stream, width, height, ticks, rate)
            for position, (i, duration) in enumerate(zip(schedule, durations)):
                if movie.timing_mode == 0:
                    avi.video(last if previous_png != last else b'', duration)
                    previous_png = last
                key = (i, hashlib.blake2b(decoder.buffer, digest_size=16).digest()) if movie.has_loops else None
                if key is not None and key in cache:
                    state, png = cache[key]
                    decoder.buffer[:] = state
                    cache.move_to_end(key)
                else:
                    pixels, updates = decoder.frame(i)
                    digest = hashlib.blake2b(pixels, digest_size=16).digest()
                    png = png_cache.get(digest)
                    if png is None:
                        png = png_image(pixels, width, height)
                        png_cache[digest] = png
                        if len(png_cache) > 128:
                            png_cache.popitem(last=False)
                    if key is not None:
                        state = bytes(decoder.buffer)
                        cache[key] = (state, png)
                        cache_bytes += len(state)+len(png)
                        while cache_bytes > 64*1024*1024:
                            _, (old_state, old_png) = cache.popitem(last=False)
                            cache_bytes -= len(old_state)+len(old_png)
                last = png
                if movie.timing_mode == 1:
                    if position == len(schedule)-1:
                        # An explicit final packet gives AVI remuxers an exact
                        # endpoint even when they discard empty repeat chunks.
                        avi.video(png if previous_png != png else b'', duration-1)
                        avi.video(png, 1)
                    else:
                        avi.video(png if previous_png != png else b'', duration)
                    previous_png = png
            if terminal:
                avi.video(last, terminal)
            avi.finish()
    except BaseException:
        if created_output and output.exists():
            output.unlink()
        raise
    stats['output_bytes'] = output.stat().st_size
    stats['warnings'] = movie.warnings
    if verbose:
        meta = movie.metadata()
        meta['conversion'] = stats
        with sidecar.open('x', encoding='utf-8') as f:
            os.fchmod(f.fileno(), 0o664)
            json.dump(meta, f, ensure_ascii=False, indent=2)
            f.write('\n')
    return stats


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('inputFile')
    p.add_argument('outputFile')
    p.add_argument('-verbose', '--verbose', action='store_true',
                   help='also write outputFile.json with byte ranges and diagnostics')
    p.add_argument('--zero-wait-fps', type=int, default=10, choices=(10, 15, 30, 60),
                   help='explicit rate for zero-delay frames (default: 10)')
    p.add_argument('--legacy-player', action='store_true',
                   help='enable 1991 scrolling and extra-repeat loop semantics')
    p.add_argument('--max-frames', type=int, default=10_000_000,
                   help='maximum expanded source frames; refuse larger timelines before writing')
    args = p.parse_args(argv)
    try:
        result = convert(args.inputFile, args.outputFile, verbose=args.verbose,
                         zero_wait_fps=args.zero_wait_fps, legacy=args.legacy_player,
                         max_frames=args.max_frames)
    except (OSError, FormatError, ValueError, MemoryError) as exc:
        print(f'fmTownsMovieVideo: {exc}', file=sys.stderr)
        return 1
    for warning in result['warnings']:
        print(f'warning: {warning}', file=sys.stderr)
    if args.verbose:
        print(f"{result['width']}x{result['height']}, {result['duration_seconds']:.3f}s, "
              f"{result['expanded_source_frames']} frames -> {args.outputFile}")
    return 0


if __name__ == '__main__':
    sys.exit(main())

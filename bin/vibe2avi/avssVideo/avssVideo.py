#!/usr/bin/env python3
# Vibe coded by Codex
# SPDX-License-Identifier: LGPL-2.1-or-later
"""Intel DVI / AVSS version 3 to AVI (RTV 2.0/2.1 and adpcm4e).

This is a deliberately bounded implementation, not a decoder for every AVSS
codec. See avssVideo.txt for the exact support boundary and unresolved fields.
Python 3.10+ and an ffmpeg executable are required; no third-party Python modules.
The vector codebooks are format constants published by FFmpeg/NihAV (Konstantin
Shishkov). Decoding was also checked against Intel's AVSTOAVI and AVKALG.H.
"""

from __future__ import annotations

import argparse
from array import array
from collections import Counter
from dataclasses import dataclass, field
from functools import lru_cache, reduce
import hashlib
import json
import operator
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import wave


class AVSSError(Exception):
    """A recognized but unusable or unsupported AVSS file."""


class NotAVSS(AVSSError):
    """The identifying signatures do not match."""


class Unsupported(AVSSError):
    """A positively identified feature needs another decoder."""


def u16(data, offset=0):
    return struct.unpack_from('<H', data, offset)[0]


def u32(data, offset=0):
    return struct.unpack_from('<I', data, offset)[0]


def s16(data, offset=0):
    return struct.unpack_from('<h', data, offset)[0]


def cstring(data):
    return bytes(data).split(b'\0', 1)[0].decode('ascii', 'backslashreplace')


def xor32(data):
    return reduce(operator.xor, struct.unpack('<' + 'I' * (len(data) // 4), data), 0)


@dataclass
class Stream:
    number: int
    kind: int
    subtype: int
    flags: int
    maximum: int
    name: str
    headers: list = field(default_factory=list)
    algorithm: int | str = ''
    width: int = 0
    height: int = 0
    packets: list = field(default_factory=list)


@dataclass
class Packet:
    tick: int
    offset: int
    size: int
    available: int


class AVSS:
    """Length-directed parser; never searches the file for apparent sync bytes."""

    def __init__(self, data: bytes):
        self.data = data
        self.warnings = []
        self.ranges = []
        self.streams = []
        self.frames = []
        self.unsupported = []
        self._parse()

    def warn(self, message):
        if message not in self.warnings:
            self.warnings.append(message)

    def region(self, offset, size, label, status='metadata'):
        if offset < 0 or size < 0 or offset + size > len(self.data):
            raise AVSSError(f'{label}: range {offset:#x}+{size:#x} is outside the file')
        if size:
            self.ranges.append(dict(offset=offset, size=size, label=label, status=status))

    def get(self, offset, size, label):
        if offset < 0 or size < 0 or offset + size > len(self.data):
            raise AVSSError(f'{label}: truncated at {offset:#x}, need {size} bytes')
        return self.data[offset:offset + size]

    def _parse(self):
        b = self.data
        if b[:4] != b'IVDV':
            raise NotAVSS('not Intel DVI/AVSS: missing IVDV signature')
        if len(b) < 12:
            raise AVSSError('truncated DVI standard header')
        std_size, std_version = struct.unpack_from('<HH', b, 4)
        base = 12 if std_size == 1 else std_size
        if base < 12 or b[base:base + 4] != b'SSVA':
            raise NotAVSS('not the target AVSS container: missing SSVA signature')
        if std_version != 1 or base != 12:
            raise Unsupported(f'DVI header version {std_version}, size {std_size}')
        a = self.get(base, 120, 'AVL header')
        if (u16(a, 4), u16(a, 6)) != (120, 3):
            raise Unsupported('only the 120-byte AVL version 3 header is implemented')
        self.region(0, 12, 'DVI standard header')
        self.region(base, 120, 'AVL version 3 header')
        self.annotation = u32(b, 8)
        self.groups, self.labels = u16(a, 8), u32(a, 32)
        self.group_size, self.group_offset = u16(a, 10), u32(a, 12)
        self.label_size, self.label_offset = u16(a, 40), u32(a, 36)
        self.seq_offset, self.seq_size = u32(a, 44), u16(a, 48)
        self.frame_count = u32(a, 52)
        self.fixed_frame_size = u32(a, 56)
        self.first_frame, self.end_frame = u32(a, 60), u32(a, 64)
        self.header_size, self.directory_size = u16(a, 68), u16(a, 70)
        self.directory_offset = u32(a, 72)
        self.fps = u16(a, 78)
        self.update = u32(a, 80)
        self.free_block = u32(a, 84)
        self.stream_count, stream_offset = u16(a, 22), u32(a, 24)
        self.pool_offset = u32(a, 28)
        if (u16(a, 18), u16(a, 20), u16(a, 50), u16(a, 76)) != (44, 3, 3, 3):
            raise Unsupported('unsupported stream, frame, or directory header revision')
        if not self.stream_count or self.stream_count > 100:
            raise AVSSError('invalid stream count')
        if not 1 <= self.fps <= 1000:
            raise AVSSError('no valid declared frame rate; refusing to invent one')
        if self.header_size != 12 + 4 * self.stream_count or self.directory_size != 4:
            raise Unsupported('unsupported frame header or directory entry size')
        if self.first_frame < 132 or self.first_frame > len(b):
            raise AVSSError('invalid first frame offset')
        if self.frame_count > (len(b) - self.first_frame) // self.header_size + 1:
            self.warn('declared frame count cannot fit; recover only length-delimited frames')
        for count, size, offset, name in [
            (self.groups, self.group_size, self.group_offset, 'stream groups'),
            (self.labels, self.label_size, self.label_offset, 'labels'),
        ]:
            if count:
                self.region(offset, count * size, name, 'unresolved')
                self.unsupported.append(f'{name} are not implemented')
        if self.free_block:
            self.unsupported.append('free-block editing chain is not implemented')
        for i in range(self.stream_count):
            offset = stream_offset + i * 44
            sh = self.get(offset, 44, 'stream header')
            if sh[:4] != b'MRTS':
                raise AVSSError(f'stream {i}: missing MRTS tag')
            self.region(offset, 44, f'stream {i} header')
            st = Stream(i, u16(sh, 4), u16(sh, 6), u32(sh, 16),
                        u32(sh, 20), cstring(sh[28:44]))
            count, sub_offset = u16(sh, 8), u32(sh, 24)
            if not count:
                raise AVSSError(f'stream {i} has no substream descriptions')
            seen = set()
            for j in range(count):
                if sub_offset in seen:
                    raise AVSSError('cyclic substream header chain')
                seen.add(sub_offset)
                prefix = self.get(sub_offset, 8, 'substream prefix')
                size, version = u16(prefix, 4), u16(prefix, 6)
                if size < 104:
                    raise Unsupported('unsupported short substream header')
                sub = self.get(sub_offset, size, 'substream header')
                st.headers.append(dict(offset=sub_offset, size=size, version=version,
                                       raw=sub.hex(), frame_count=u32(sub, 96)))
                self.region(sub_offset, size, f'stream {i} substream {j} header')
                pad = (-size) & 3
                if pad:
                    self.region(sub_offset + size, pad, 'substream storage alignment')
                if st.kind == 3 and prefix[:4] == b'GMIC' and size >= 132:
                    st.width, st.height = u16(sub, 108), u16(sub, 110)
                    st.algorithm = u16(sub, 128)
                    if (size, version) not in ((132, 3), (136, 4)):
                        self.unsupported.append(f'video substream revision {version}, size {size}')
                    if not st.width or not st.height or st.width * st.height > 16777216:
                        raise AVSSError('invalid video dimensions')
                    if st.algorithm not in (200, 201) or st.subtype != 13:
                        self.unsupported.append(f'stream {i}: video algorithm {st.algorithm}, '
                                                f'subtype {st.subtype}; only RTV 2.0/2.1 YVU is implemented')
                    if any(sub[104:108]) or any(sub[112:120]):
                        self.unsupported.append('positioned, cropped, or drop-phrase video is not implemented')
                elif st.kind == 2 and prefix[:4] == b'IDUA' and size >= 162:
                    st.algorithm = cstring(sub[120:136])
                    if st.subtype != 0:
                        self.unsupported.append(f'audio subtype {st.subtype} is not implemented')
                    if (size, version) not in ((162, 4), (168, 5)):
                        self.unsupported.append(f'audio substream revision {version}, size {size}')
                    if u32(sub, 152):
                        self.unsupported.append('nonzero audio starting-frame offset is not implemented')
                    if (u16(sub, 144), u16(sub, 146)) != (100, 100):
                        self.unsupported.append('non-default audio channel volume is not implemented')
                else:
                    self.unsupported.append(f'stream {i}: type {st.kind}, tag {prefix[:4]!r}')
                sub_offset = u32(sub, 100)
                if j + 1 < count and not sub_offset:
                    raise AVSSError('substream chain ends before its declared count')
            if count != 1:
                self.unsupported.append('midstream substream-description changes are not implemented')
            self.streams.append(st)
        if self.seq_size:
            self.region(self.seq_offset, self.seq_size, 'video sequence header', 'unresolved')
            self.unsupported.append('codec-specific video sequence header is not decoded')
        self._frames()
        for st in self.streams:
            if st.kind == 2 and any(p.size for p in st.packets) and st.algorithm != 'adpcm4e':
                self.unsupported.append(f'stream {st.number}: audio algorithm {st.algorithm!r} '
                                        'has no verified decoder (dvaud44 packet/channel timing unresolved)')
        if self.annotation and self.annotation <= len(b):
            self.region(self.annotation, len(b) - self.annotation, 'unstructured annotation')
        elif self.annotation:
            self.warn('annotation offset is beyond the truncated file')
        self._directory()
        self._coverage()

    def _frames(self):
        pos = self.first_frame
        previous = 0
        # FrameCount and per-stream lengths are authoritative for sequential reads.
        # An inconsistent EndOfFrameOffset alone cannot truncate a valid last frame.
        stops = [len(self.data)] + [x for x in
                 (self.directory_offset, self.seq_offset, self.annotation)
                 if x >= self.first_frame and x]
        limit = min(stops)
        for tick in range(self.frame_count):
            if pos + self.header_size > limit:
                self.warn(f'truncated frame header at tick {tick}; retained {len(self.frames)} complete headers')
                break
            hdr = self.get(pos, self.header_size, 'frame header')
            number, prev, check = struct.unpack_from('<III', hdr)
            sizes = struct.unpack_from('<' + 'I' * self.stream_count, hdr, 12)
            valid_checksum = xor32(hdr) == 0x46524D48
            if not valid_checksum:
                self.warn(f'frame {tick}: header checksum mismatch')
            if number != tick:
                self.warn(f'frame record {tick}: stored number {number}; using record order')
            if prev not in (0, previous):
                self.warn(f'frame {tick}: invalid previous-frame link')
            self.region(pos, self.header_size, f'frame {tick} header')
            self.frames.append(dict(tick=tick, number=number, offset=pos,
                                    checksum_valid=valid_checksum, sizes=list(sizes)))
            previous = pos
            pos += self.header_size
            truncated = False
            for st, size in zip(self.streams, sizes):
                available = min(size, max(0, limit - pos))
                st.packets.append(Packet(tick, pos, size, available))
                self.region(min(pos, limit), available, f'frame {tick} stream {st.number} payload',
                            'compressed' if st.algorithm in (200, 201, 'adpcm4e') else 'unresolved')
                if size > st.maximum:
                    self.warn(f'stream {st.number}: packet exceeds declared maximum')
                if available != size:
                    self.warn(f'frame {tick} stream {st.number}: truncated payload')
                    truncated = True
                pos += size
            if self.fixed_frame_size and pos - previous != self.fixed_frame_size:
                self.warn('fixed frame size disagrees with packet sizes')
            if truncated:
                pos = limit
                break
        self.actual_end = pos
        if self.end_frame != pos:
            self.warn(f'EndOfFrameOffset {self.end_frame:#x} differs from parsed end {pos:#x}')

    def _directory(self):
        if not self.directory_offset:
            return
        offset = self.directory_offset
        if offset >= len(self.data):
            self.warn('frame directory is absent beyond the truncated file')
            return
        stop = min([len(self.data)] + [x for x in (self.annotation, self.seq_offset)
                                      if x > offset])
        count = min(self.frame_count, (stop - offset) // 4)
        if count < self.frame_count:
            self.warn('truncated frame directory')
        self.region(offset, count * 4, 'frame directory')
        for i in range(count):
            entry = u32(self.data, offset + i * 4)
            if i < len(self.frames) and entry & 0x7FFFFFFF != self.frames[i]['offset']:
                self.warn(f'directory entry {i} disagrees with sequential frame offset')
        tail = offset + count * 4
        if stop - tail == 4 and u32(self.data, tail) == self.actual_end:
            self.region(tail, 4, 'optional directory end-of-data sentinel')

    def _coverage(self):
        pos = 0
        gaps = []
        for region in sorted(self.ranges, key=lambda r: r['offset']):
            if region['offset'] < pos:
                raise AVSSError(f'overlapping structures at {region["offset"]:#x}')
            if region['offset'] > pos:
                gaps.append((pos, region['offset'] - pos))
            pos = region['offset'] + region['size']
        if pos < len(self.data):
            gaps.append((pos, len(self.data) - pos))
        for offset, size in gaps:
            self.region(offset, size, 'unassigned bytes', 'unresolved')
            self.warn(f'unassigned byte range {offset:#x}..{offset + size:#x}')
        self.ranges.sort(key=lambda r: r['offset'])

    def payload(self, packet):
        return self.data[packet.offset:packet.offset + packet.available]

    def require_supported(self):
        if self.unsupported:
            raise Unsupported('; '.join(dict.fromkeys(self.unsupported)))
        if not self.frames:
            raise AVSSError('no recoverable frame records')

    def audit(self):
        return dict(size=len(self.data), sha256=hashlib.sha256(self.data).hexdigest(),
                    frame_rate=self.fps, declared_frames=self.frame_count,
                    parsed_frames=len(self.frames), warnings=self.warnings,
                    unsupported=list(dict.fromkeys(self.unsupported)),
                    byte_accounting=sum(r['size'] for r in self.ranges),
                    semantic_completeness=False,
                    streams=[dict(number=s.number, type=s.kind, subtype=s.subtype,
                                  algorithm=s.algorithm, width=s.width, height=s.height,
                                  name=s.name, headers=s.headers,
                                  payload_bytes=sum(p.available for p in s.packets))
                             for s in self.streams], ranges=self.ranges)


# Format constants, not values learned from individual input files.
SYMBOLS = bytes.fromhex(
    '01028103048205068384070885090a0b0c0d0e860f108788111213148915168a1718'
    '8b191a8c1b1c8d1d1e8e1f208f212290232425262728292a2b2c2d2e2f303132'
    '333435363738393a3b3c3d3e3f404142434445464748494a4b4c4d4e4f50515253'
    '5455565758595a5b5c5d5e5f606162636465666768696a6b6c6d6e6f7071727374'
    '75767778797a7b7c7d7e7f')

# DELTA_TABLES is filled below with the four normative 256-byte codebooks.
DELTA_TABLES = (
    bytes.fromhex(
        '808084847c7c7f85817b857f7b818c8c7474838d7d738d83737d778989778977'
        '77898c95746b958c6b747c908470907c708496966a6a82987e689882687e97a2'
        '695ea2975e69a2a25e5e8ba3755da38b5d7571958f6b95716b8f789d88639d78'
        '63887fa78159a77f5981a4b15c4fb1a44f5c96b16a4fb1964f6ab2b24e4e659b'
        '9b659b65659b89b4774cb4894c776aa3965da36a5d9673ac8d54ac73548db4c3'
        '4c3dc3b43d4ca4c35c3dc3a43d5cc4c43c3c96c66a3ac6963a6a7cba8446ba7c'
        '46845baba555ab5b55a563b49d4cb4634c9d86ca7a36ca86367ab6d74a29d7b6'
        '294ac8d73829d7c82938a4d85c28d8a4285c6cc1943fc16c3f94d9d927278080'
    ),
    bytes.fromhex(
        '808085857b7b7e878279877e79828f8f7171848f7c718f84717c758b8b758b75'
        '758b8e9a72669a8e66727b93856d937b6d859b9b6565829d7e639d82637e9ba8'
        '6558a89b5865a9a957578daa7356aa8d56736e999267996e679276a28a5ea276'
        '5e8a7faf8151af7f5181abba5546baab46559abb6645bb9a4566bbbb454560a0'
        'a060a06060a08bbe7542be8b427566aa9a56aa66569a70b5904bb5704b90becf'
        '4231cfbe3142abd05530d0ab3055d1d12f2f9ad3662dd39a2d667bc5853bc57b'
        '3b8554b4ac4cb4544cac5ebea242be5e42a287d87928d8872879c0e84018e8c0'
        '1840d5e82b18e8d5182babe95517e9ab175568cd9833cd683398eaea16168080'
    ),
    bytes.fromhex(
        '808086867a7a7e888278887e788292926e6e85927b6e92856e7b738d8d738d73'
        '738d919e6f629e91626f7997876997796987a0a0606083a27d5ea2835e7da0b0'
        '6050b0a05060b1b14f4f8fb2714eb28f4e716b9e95629e6b629574a98c57a974'
        '578c7fb88148b87f4881b4c54c3bc5b43b4c9fc6613ac69f3a61c6c63a3a59a7'
        'a759a75959a78dca7336ca8d367361b29f4eb2614e9f6dbf9341bf6d4193cadf'
        '3621dfca2136b3df4d21dfb3214de1e11f1f9fe3611de39f1d617ad3862dd37a'
        '2d864cbeb442be4c42b457caa936ca5736a988e97817e9881778ccfb3405fbcc'
        '0534e6fb1a05fbe6051ab4fd4c03fdb4034c63dc9d24dc63249dfefe02028080'
    ),
    bytes.fromhex(
        '8080878779797e898277897e778295956b6b86967a6a96866a7a709090709070'
        '709094a46c5ca4945c6c789b88659b786588a6a65a5a83a97d57a983577da6b9'
        '5a47b9a6475ababa464692bc6e44bc92446e67a3995da3675d9972b08e50b072'
        '508e7fc3813dc37f3d81bed2422ed2be2e42a5d45b2cd4a52c5bd4d42c2c52ae'
        'ae52ae5252ae8fd87128d88f28715bbba545bb5b45a569cb9735cb693597d8f0'
        '2810f0d81028bdf1430ff1bd0f43f3f30d0da5f65b0af6a50a5b78e2881ee278'
        '1e8842c9be37c94237be4fd8b128d84f28b18afd7603fd8a0376dbff2501ffdb'
        '0125f9ff0701fff90107beff4201ffbe01425eeda213ed5e13a2ffff01018080'
    ),
)


class Bits:
    def __init__(self, data):
        self.data = data
        self.pos = 0

    def bit(self):
        if self.pos >= len(self.data) * 8:
            raise AVSSError('truncated RTV entropy bitstream')
        value = (self.data[self.pos >> 3] >> (self.pos & 7)) & 1
        self.pos += 1
        return value


@lru_cache(maxsize=128)
def code_groups(extra):
    if len(extra) != 8 or max(extra) > 15:
        raise Unsupported('RTV code description exceeds the supported 15 suffix bits')
    bases = []
    total = 0
    for n in extra:
        bases.append(total)
        total += 1 << n
    if total < len(SYMBOLS):
        raise AVSSError('RTV code table does not describe all 143 symbols')
    return bases


class RTV:
    def __init__(self, stream, warn, frame_header_size=None):
        self.stream = stream
        self.warn = warn
        self.frame_header_size = frame_header_size
        self.planes = None
        self.shape = None
        self.stats = Counter()

    def decode(self, data, tick):
        if not data or len(data) == 16 and u32(data, 4) == 128:
            if data and u16(data) not in (200, 201):
                raise AVSSError('repeat frame has incorrect codec id')
            if self.planes is None:
                raise AVSSError('repeat frame has no previous image')
            self.stats['repeat_frames'] += 1
            return self.expand()
        if len(data) < 32:
            raise AVSSError('truncated RTV header')
        alg, flags = u16(data), u16(data, 2)
        if alg not in (200, 201):
            raise Unsupported(f'RTV algorithm changed to {alg}')
        if flags & ~4:
            raise Unsupported(f'RTV generic flags {flags:#x}')
        extra_flags, quant = u16(data, 16), u16(data, 18)
        if extra_flags & ~0x10C or quant > 15:
            raise Unsupported(f'RTV flags {extra_flags:#x} / quantizer {quant}')
        if bool(extra_flags & 4) != bool(flags & 4):
            raise AVSSError('contradictory RTV intra-frame flags')
        display_h, display_w = u16(data, 12), u16(data, 14)
        if (display_w, display_h) != (self.stream.width, self.stream.height):
            raise Unsupported('RTV dimensions change relative to the substream description')
        if display_w % 4 or display_h % 4:
            raise Unsupported('RTV nominal dimensions are not aligned for YVU410')
        w = display_w // (2 if extra_flags & 256 else 1)
        h = display_h // (2 if extra_flags & 8 else 1)
        if w % 8 or h % 4 or not w or not h:
            raise Unsupported(f'RTV coded dimensions {w}x{h} are not aligned for YVU410')
        if self.shape and self.shape != (w, h) and not flags & 4:
            raise AVSSError('predictive frame changes coded dimensions')
        size = (u32(data, 4) + 7) // 8
        if size < 32:
            raise AVSSError('invalid RTV bit length')
        if size > len(data):
            self.warn(f'frame {tick}: truncated declared RTV data; attempting pixel recovery')
        tail = data[size:]
        if tail:
            if (len(tail) == self.frame_header_size and len(tail) % 4 == 0
                    and xor32(tail) == 0x46524D48):
                self.stats['embedded_source_frame_headers'] += 1
            else:
                self.warn(f'frame {tick}: {len(tail)} undecoded bytes after the RTV bitstream')
                self.stats['unresolved_trailer_bytes'] += len(tail)
        br = Bits(data[32:min(size, len(data))])
        extras = bytes(data[24:32])
        bases = code_groups(extras)
        intra = bool(flags & 4)
        if not intra and self.planes is None:
            raise AVSSError('predictive frame has no reference image')
        planes = []
        for plane, (pw, ph) in enumerate(((w, h), (w // 4, h // 4), (w // 4, h // 4))):
            table = DELTA_TABLES[(quant >> (0 if plane == 0 else 2)) & 3]
            out = bytearray(pw * ph) if intra else bytearray(self.planes[plane])
            for y in range(ph):
                x = 0
                while x < pw:
                    group = 0
                    while br.bit():
                        group += 1
                        if group == 8:
                            raise AVSSError('invalid RTV prefix')
                    suffix = 0
                    for _ in range(extras[group]):
                        suffix = (suffix << 1) | br.bit()
                    ordinal = bases[group] + suffix
                    if ordinal >= 143:
                        raise AVSSError('undefined RTV entropy symbol')
                    symbol = SYMBOLS[ordinal]
                    if symbol >= 128:
                        run = (symbol - 128) * 2
                        if x + run > pw:
                            raise AVSSError('RTV zero run crosses the scanline')
                        if intra:
                            out[y * pw + x:y * pw + x + run] = (
                                out[(y - 1) * pw + x:(y - 1) * pw + x + run]
                                if y else b'\x80' * run)
                        x += run
                    else:
                        for component in (0, 1):
                            delta = table[2 * symbol + component] - 128
                            index = y * pw + x
                            value = ((out[index - pw] if y else 128) + delta
                                     if intra else out[index] + ((3 * delta) >> 2))
                            out[index] = max(0, min(255, value))
                            x += 1
            planes.append(out)
        unused = len(br.data) * 8 - br.pos
        if unused > 31:
            self.warn(f'frame {tick}: {unused} unused coded bits (more than word alignment)')
        self.stats['entropy_bits'] += br.pos
        self.stats['alignment_bits'] += unused
        self.stats['intra_frames' if intra else 'predicted_frames'] += 1
        self.planes, self.shape = planes, (w, h)
        return self.expand()

    def expand(self):
        # Honor the two reduction flags via exact replication into the declared grid.
        w, h = self.shape
        dw, dh = self.stream.width, self.stream.height
        result = []
        for i in (0, 2, 1):  # AVSS Y,V,U -> rawvideo Y,U,V
            div = 1 if i == 0 else 4
            sw, sh, tw, th = w // div, h // div, dw // div, dh // div
            plane = self.planes[i]
            if (sw, sh) == (tw, th):
                result.append(bytes(plane))
                continue
            out = bytearray()
            for row in range(sh):
                src = plane[row * sw:(row + 1) * sw]
                line = bytes(v for v in src for _ in range(tw // sw))
                out.extend(line * (th // sh))
            result.append(bytes(out))
        return b''.join(result)


IMA_STEPS = (7,8,9,10,11,12,13,14,16,17,19,21,23,25,28,31,34,37,41,45,50,
             55,60,66,73,80,88,97,107,118,130,143,157,173,190,209,230,253,279,
             307,337,371,408,449,494,544,598,658,724,796,876,963,1060,1166,1282,
             1411,1552,1707,1878,2066,2272,2499,2749,3024,3327,3660,4026,4428,
             4871,5358,5894,6484,7132,7845,8630,9493,10442,11487,12635,13899,
             15289,16818,18500,20350,22385,24623,27086,29794,32767)
INDEX_CHANGE = (-1,-1,-1,-1,2,4,6,8)


class ADPCM4E:
    def __init__(self):
        self.states = None
        self.rate = None
        self.channels = None
        self.blocks = 0

    def word(self, value, channel):
        pred, index = self.states[channel]
        samples = []
        for shift in (12, 8, 4, 0):
            nibble = (value >> shift) & 15
            signed = (2 * (nibble & 7) + 1) * (-1 if nibble & 8 else 1)
            # Intel's multiply-and-arithmetic-shift rule, not IMA's split shifts.
            pred = ((pred + ((signed * IMA_STEPS[index]) >> 3) + 32768) & 65535) - 32768
            index = max(0, min(88, index + INDEX_CHANGE[nibble & 7]))
            samples.append(pred)
        self.states[channel] = (pred, index)
        return samples

    def decode(self, data):
        if not data:
            return b''
        if len(data) < 8:
            raise AVSSError('truncated ADPCM4E packet header')
        if data[2] != 255 or data[3] not in (1, 3):
            raise Unsupported('unsupported ADPCM4E packet discriminator')
        channels = 1 if data[3] == 1 else 2
        rate = u16(data, 4)
        if not rate:
            raise AVSSError('zero ADPCM sample rate')
        if self.rate is not None and (rate, channels) != (self.rate, self.channels):
            raise Unsupported('midstream audio rate/channel changes')
        self.rate, self.channels = rate, channels
        if u16(data, 6):
            raise Unsupported('nonzero ADPCM4E reserved header word')
        n = u16(data)
        if len(data) != n + 8 or n % (32 * channels):
            raise AVSSError('ADPCM4E size is not a whole set of 32-byte channel blocks')
        if not n:
            return b''
        pcm = array('h')
        for start in range(8, len(data), 32 * channels):
            words = struct.unpack_from('<' + 'H' * 16 * channels, data, start)
            decoded = [[] for _ in range(channels)]
            if self.states is not None:
                for ch in range(channels):
                    decoded[ch].extend(self.word(words[ch], ch))
            else:
                self.states = [(0, 0)] * channels
            for ch in range(channels):
                seed = words[channels + ch]
                index = seed & 127
                if index > 88:
                    raise AVSSError('ADPCM4E predictor step index exceeds 88')
                pred = (seed & 0xFF80)
                if pred >= 32768:
                    pred -= 65536
                self.states[ch] = (pred, index)
            for row in range(2, 16):
                for ch in range(channels):
                    decoded[ch].extend(self.word(words[row * channels + ch], ch))
            for group in zip(*decoded):
                pcm.extend(group)
            self.blocks += 1
        if sys.byteorder != 'little':
            pcm.byteswap()
        return pcm.tobytes()


def convert(input_file, output_file):
    source, destination = Path(input_file), Path(output_file)
    if source.resolve() == destination.resolve():
        raise AVSSError('input and output must be different files')
    # Identify and reject unsupported features before creating any output file.
    movie = AVSS(source.read_bytes())
    movie.require_supported()
    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        raise AVSSError('ffmpeg executable not found on PATH')
    if not destination.parent.is_dir():
        raise AVSSError('output directory does not exist')
    statistics = {}
    # Temporary files disappear on any failure; existing destinations remain intact.
    with tempfile.TemporaryDirectory(prefix='avss-') as temporary:
        tmp = Path(temporary)
        inputs = []
        maps = []
        for st in movie.streams:
            if st.kind == 3:
                decoder = RTV(st, movie.warn, movie.header_size)
                raw = tmp / f'video-{st.number}.yuv'
                frames_written = 0
                recovered = 0
                with raw.open('wb') as out:
                    for packet in st.packets:
                        try:
                            frame = decoder.decode(movie.payload(packet), packet.tick)
                            recovered += 1
                        except Unsupported:
                            raise
                        except AVSSError as exc:
                            movie.warn(f'frame {packet.tick}: {exc}')
                            if decoder.planes is None:
                                # Explicit error concealment, never a guessed codec or boundary.
                                frame = (b'\x10' * (st.width * st.height)
                                         + b'\x80' * (st.width * st.height // 8))
                                movie.warn(f'frame {packet.tick}: black placeholder until an intact intra frame')
                            else:
                                frame = decoder.expand()
                                movie.warn(f'frame {packet.tick}: repeated last intact image')
                        out.write(frame)
                        frames_written += 1
                if not recovered:
                    raise AVSSError('no video images could be decoded')
                statistics[f'video_{st.number}'] = dict(decoder.stats, frames=frames_written)
                maps += ['-map', f'{len(inputs)}:v:0']
                inputs.append((raw, ['-f', 'rawvideo', '-pixel_format', 'yuv410p',
                                     '-video_size', f'{st.width}x{st.height}',
                                     '-framerate', str(movie.fps)]))
            elif st.kind == 2 and any(p.size for p in st.packets):
                decoder = ADPCM4E()
                audio = bytearray()
                for packet in st.packets:
                    try:
                        audio.extend(decoder.decode(movie.payload(packet)))
                    except Unsupported:
                        raise
                    except AVSSError as exc:
                        # Stop this track at the last complete block; no invented sample counts.
                        movie.warn(f'audio frame {packet.tick}: {exc}; audio ends here')
                        break
                if not audio or decoder.rate is None:
                    movie.warn(f'stream {st.number}: no audio samples could be decoded')
                    continue
                wav = tmp / f'audio-{st.number}.wav'
                with wave.open(str(wav), 'wb') as out:
                    out.setnchannels(decoder.channels)
                    out.setsampwidth(2)
                    out.setframerate(decoder.rate)
                    out.writeframes(audio)
                statistics[f'audio_{st.number}'] = dict(rate=decoder.rate, channels=decoder.channels,
                                                      samples=len(audio)//(2*decoder.channels),
                                                      blocks=decoder.blocks)
                maps += ['-map', f'{len(inputs)}:a:0']
                inputs.append((wav, []))
            elif st.kind == 2:
                movie.warn(f'stream {st.number}: declared audio track contains no samples')
        if not inputs:
            raise AVSSError('no media streams to write')
        args = [ffmpeg, '-nostdin', '-hide_banner', '-loglevel', 'error', '-y']
        for path, options in inputs:
            args += options + ['-i', str(path)]
        args += maps
        if any(st.kind == 3 for st in movie.streams):
            # Convert the documented 5:4 pixel aspect to square pixels, losslessly
            # encode the resulting raster; no additional temporal resampling.
            args += ['-vf', 'scale=iw*5/4:ih:flags=neighbor,setsar=1',
                     '-c:v', 'ffv1', '-level', '3', '-pix_fmt', 'yuv444p']
        args += ['-c:a', 'pcm_s16le', '-f', 'avi']
        descriptor, tempname = tempfile.mkstemp(prefix='.' + destination.name + '.',
                                               suffix='.tmp', dir=destination.parent)
        os.close(descriptor)
        try:
            run = subprocess.run(args + [tempname], capture_output=True, text=True)
            if run.returncode:
                raise AVSSError('AVI muxing failed: ' + run.stderr.strip())
            os.chmod(tempname, 0o664)
            os.replace(tempname, destination)
        finally:
            if os.path.exists(tempname):
                os.unlink(tempname)
    return movie, statistics


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('inputFile')
    parser.add_argument('outputFile', nargs='?')
    parser.add_argument('--inspect', action='store_true', help='print the container byte audit as JSON; do not convert')
    args = parser.parse_args(argv)
    try:
        if args.inspect:
            print(json.dumps(AVSS(Path(args.inputFile).read_bytes()).audit(), indent=2))
            return 0
        if not args.outputFile:
            parser.error('outputFile is required unless --inspect is used')
        movie, stats = convert(args.inputFile, args.outputFile)
        for warning in movie.warnings:
            print('warning: ' + warning, file=sys.stderr)
        print(json.dumps(dict(output=args.outputFile, streams=stats)), file=sys.stderr)
        return 0
    except (AVSSError, OSError, struct.error, ValueError) as exc:
        print(f'avssVideo: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

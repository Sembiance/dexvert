#!/usr/bin/env python3
# Vibe coded by Codex
"""Decode the accelerated RLE profile of Gold Disk / Astound Animation.

Usage: astoundAnimation.py inputFile outputFile
Requires Python 3.10+ and ffmpeg on PATH; no third-party Python packages.
See astoundAnimation.txt for the supported profile and remaining uncertainties.
"""
from __future__ import annotations

import argparse
import collections
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib


class FormatError(Exception):
    """Malformed target format, or not enough data to recover it."""


class Unsupported(FormatError):
    """Not the supported accelerated format, or an unimplemented feature."""


class InteractivePlayback(Unsupported):
    """Playback needs a partial preview to produce a finite AVI."""


@dataclass
class Node:
    tag: str
    start: int
    end: int
    value: object

    def fields(self):
        return {n.tag: n.value for n in self.value}


CONTAINERS = set('GDAW RSRC VERS PREF PALT BKGD SWND SEEN FRAM BKEV TMEV CREV '
                 'SNEV PTEV PLEV MKEV DSEV PATH PRTK PTIN ACTR'.split())
RAW = {'RLE4', 'RLE8'}
# Explicit field allowlists prevent silently accepting a different GDAW profile.
SCHEMA = {
    'VERS': 'dwvr pscr dwdt nndn',
    'PREF': 'wdzz tzpi wdac ptex ptan nndn',
    'PALT': 'psnm wdvr wdne tdpe nndn',
    'BKGD': 'byty psnm pspl wdrn byrt wd#f wd#t dw4o dw4s dw8o dw8s nndn',
    'SWND': 'wdty psnm dwfs tzfd nndn',
    'SEEN': 'psnm wdnf wdnn nndn FRAM',
    'BKEV': 'wdif psnm byal nnhi nndn',
    'TMEV': 'wdif wddy nnhi nnen nndn',
    'CREV': 'wdif nnhi nnsh nnan ptpx nndn',
    'SNEV': 'wdif nnhi wdty pssn nnlp nndn',
    'PTEV': 'wdif nnhi psnm nndn',
    'PLEV': 'wdif nnhi byty wddy nnws nnwv nnml nnmr nnak wdvk nnbf psmt wdcn nndn',
    'MKEV': 'wdif psnm nnhi nndn',
    'DSEV': 'wdif wdty dwti pstc pt1r pt1b nndn',
    'ACTR': 'psnm pspl wdkd nnel wdek ptex wdal dwtc dwbc rctr wdmc rccr '
            'wdnc wdnw wdwp wdnl wdlp nndn',
    'PTIN': 'wdfn psnm psst ptbs ptof wdsh wdsf wdia wdig wdik tdie tdel nndn',
    'GDAW': 'RSRC VERS PREF SEEN',
    'RSRC': 'RLE4 RLE8 PALT BKGD SWND ACTR',
    'FRAM': 'BKEV TMEV CREV SNEV PTEV PLEV MKEV DSEV PATH',
    'PATH': 'PRTK', 'PRTK': 'PTIN',
}
SCHEMA = {key: set(value.split()) for key, value in SCHEMA.items()}


def u16(data, pos=0):
    return struct.unpack_from('<H', data, pos)[0]


def u32(data, pos=0):
    return struct.unpack_from('<I', data, pos)[0]


def parse(data, warnings, begin=0, end=None, parent=None, depth=0):
    """Walk declared lengths only. Never search for a plausible next tag."""
    if depth > 32:
        raise FormatError('excessive chunk nesting')
    end = len(data) if end is None else end
    nodes = []
    pos = begin
    while pos < end:
        start = pos
        if end - pos < 4:
            warnings.append(f'truncated tag at 0x{pos:x}; {end-pos} bytes unrecoverable')
            break
        try:
            tag = data[pos:pos + 4].decode('ascii')
        except UnicodeDecodeError as exc:
            raise FormatError(f'invalid tag at 0x{pos:x}') from exc
        pos += 4
        if parent and tag not in SCHEMA[parent]:
            raise Unsupported(f'unsupported {parent}/{tag!r} at 0x{start:x}')
        prefix = tag[:2]
        if tag in CONTAINERS or tag in RAW or prefix in ('tz', 'td'):
            if pos + 4 > end:
                warnings.append(f'truncated length for {tag} at 0x{start:x}')
                break
            size = u32(data, pos)
            pos += 4
            limit = pos + size
            if limit > end:
                warnings.append(f'{tag} at 0x{start:x} truncated by {limit-end} bytes')
                limit = end
            if tag in CONTAINERS:
                value = parse(data, warnings, pos, limit, tag, depth + 1)
            else:
                value = data[pos:limit]
            pos = limit
        elif prefix == 'ps':
            if pos == end:
                warnings.append(f'truncated {tag} string at 0x{start:x}')
                break
            size = data[pos]
            pos += 1
            limit = min(end, pos + size)
            if limit < pos + size:
                warnings.append(f'truncated {tag} string at 0x{start:x}')
            value = data[pos:limit].decode('cp1252', errors='surrogateescape')
            pos = limit
        elif prefix in ('by', 'wd', 'dw', 'pt', 'rc'):
            fmt = {'by': '<B', 'wd': '<H', 'dw': '<I', 'pt': '<hh', 'rc': '<hhhh'}[prefix]
            size = struct.calcsize(fmt)
            if pos + size > end:
                warnings.append(f'truncated {tag} scalar at 0x{start:x}')
                break
            value = struct.unpack_from(fmt, data, pos)
            if len(value) == 1:
                value = value[0]
            pos += size
        elif prefix == 'nn':
            value = None
        else:
            raise Unsupported(f'unsupported tag {tag!r} at 0x{start:x}')
        nodes.append(Node(tag, start, pos, value))
    return nodes


# PKWARE DCL fixed code lengths, in repeat-count / length representation.
# Independently implemented from the format described in Mark Adler's blast.c.
LIT_LENGTHS = [
    11,124,8,7,28,7,188,13,76,4,10,8,12,10,12,10,8,23,8,9,7,6,7,8,7,6,55,8,23,
    24,12,11,7,9,11,12,6,7,22,5,7,24,6,11,9,6,7,22,7,11,38,7,9,8,25,11,8,11,
    9,12,8,12,5,38,5,38,5,11,7,5,6,21,6,10,53,8,7,24,10,27,44,253,253,253,252,
    252,252,13,12,45,12,45,12,61,12,45,44,173]
LEN_BASE = [3,2,4,5,6,7,8,9,10,12,16,24,40,72,136,264]
LEN_EXTRA = [0,0,0,0,0,0,0,0,1,2,3,4,5,6,7,8]


def huffman_table(repetitions):
    lengths = []
    for byte in repetitions:
        lengths.extend([byte & 15] * ((byte >> 4) + 1))
    counts = [lengths.count(n) for n in range(14)]
    symbols = sorted(range(len(lengths)), key=lambda n: (lengths[n], n))
    return counts, symbols


LIT_TABLE = huffman_table(LIT_LENGTHS)
LEN_TABLE = huffman_table([2,35,36,53,38,23])
DIST_TABLE = huffman_table([2,20,53,230,247,151,248])


def explode(data, expected):
    """Decode one independent DCL block; validate all bytes and the EOS code."""
    if expected > 512 * 1024 * 1024:
        raise FormatError('DCL block exceeds the 512 MiB resource limit')
    pos = buffer = available = 0

    def bits(count):
        nonlocal pos, buffer, available
        while available < count:
            if pos == len(data):
                raise FormatError('truncated DCL bitstream')
            buffer |= data[pos] << available
            available += 8
            pos += 1
        value = buffer & ((1 << count) - 1)
        buffer >>= count
        available -= count
        return value

    def symbol(table):
        counts, symbols = table
        code = first = index = 0
        for length in range(1, 14):
            code |= bits(1) ^ 1
            count = counts[length]
            if code < first + count:
                return symbols[index + code - first]
            index += count
            first = (first + count) << 1
            code <<= 1
        raise FormatError('invalid DCL Huffman code')

    literal_mode, dictionary = bits(8), bits(8)
    if literal_mode not in (0, 1) or dictionary not in (4, 5, 6):
        raise FormatError('invalid DCL header')
    output = bytearray()
    while True:
        if bits(1):
            code = symbol(LEN_TABLE)
            count = LEN_BASE[code] + bits(LEN_EXTRA[code])
            if count == 519:
                break
            extra = 2 if count == 2 else dictionary
            distance = (symbol(DIST_TABLE) << extra) + bits(extra) + 1
            if distance > len(output):
                raise FormatError('DCL back reference before start')
            if count <= distance:
                output += output[-distance:len(output) - distance + count]
            else:
                pattern = output[-distance:]
                output += (pattern * ((count + distance - 1) // distance))[:count]
        else:
            output.append(symbol(LIT_TABLE) if literal_mode else bits(8))
        if len(output) > expected:
            raise FormatError('DCL expansion exceeds declared size')
    if len(output) != expected or pos != len(data):
        raise FormatError('DCL expanded size or compressed size mismatch')
    return bytes(output)


def decompress_blocks(data):
    output = bytearray()
    blocks = []
    pos = 0
    while pos < len(data):
        if len(data) - pos < 8:
            raise FormatError('truncated DCL block descriptor')
        compressed, expanded = struct.unpack_from('<II', data, pos)
        pos += 8
        if compressed > len(data) - pos:
            raise FormatError('truncated DCL block payload')
        output += explode(data[pos:pos + compressed], expanded)
        blocks.append({'compressed': compressed, 'expanded': expanded})
        pos += compressed
    return bytes(output), blocks


def apply_rle(data, depth, canvas, width, height):
    """Windows BI_RLE4/BI_RLE8, bottom row first; skipped pixels persist."""
    x = y = pos = 0
    commands = collections.Counter()
    while pos + 2 <= len(data):
        count, value = data[pos:pos + 2]
        pos += 2
        if count:
            commands['run'] += 1
            pixels = (bytes([value]) * count if depth == 8 else
                      (bytes([value >> 4, value & 15]) * ((count + 1) // 2))[:count])
        elif value == 0:
            commands['end_line'] += 1
            x = 0
            y += 1
            continue
        elif value == 1:
            commands['end_bitmap'] += 1
            if pos != len(data):
                raise FormatError(f'{len(data)-pos} bytes after RLE end marker')
            return dict(commands)
        elif value == 2:
            if pos + 2 > len(data):
                raise FormatError('truncated RLE displacement')
            commands['delta'] += 1
            x += data[pos]
            y += data[pos + 1]
            pos += 2
            continue
        else:
            commands['literal'] += 1
            count = value
            length = count if depth == 8 else (count + 1) // 2
            if pos + length + (length & 1) > len(data):
                raise FormatError('truncated RLE literal or alignment byte')
            raw = data[pos:pos + length]
            pos += length + (length & 1)
            commands['alignment_bytes'] += length & 1
            pixels = (raw if depth == 8 else
                      bytes(v for byte in raw for v in (byte >> 4, byte & 15))[:count])
        if x + count > width or y >= height:
            raise FormatError(f'RLE write outside {width}x{height} at ({x},{y})')
        offset = y * width + x
        canvas[offset:offset + count] = pixels
        x += count
    raise FormatError('RLE stream has no end marker')


SYSTEM16 = [(0,0,0),(128,0,0),(0,128,0),(128,128,0),(0,0,128),(128,0,128),
            (0,128,128),(128,128,128),(192,192,192),(255,0,0),(0,255,0),
            (255,255,0),(0,0,255),(255,0,255),(0,255,255),(255,255,255)]
SYSTEM_LOW = SYSTEM16[:7] + [(192,192,192),(192,220,192),(166,202,240)]
SYSTEM_HIGH = [(255,251,240),(160,160,164)] + SYSTEM16[7:8] + SYSTEM16[9:]
# Gold Disk's built-in System palette, confirmed in the original player binary.
# Its 236 middle entries exclude duplicates of the reserved system colors.
SYSTEM_CENTER_HEX = (
    'ffffccffff99ffff66ffff33ffff00ffccffffccccffcc99ffcc66ffcc33ffcc00ff99ffff99ccff9999ff9966ff9933'
    'ff9900ff66ffff66ccff6699ff6666ff6633ff6600ff33ffff33ccff3399ff3366ff3333ff3300ff00ffff00ccff0099'
    'ff0066ff0033ccffffccffccccff99ccff66ccff33ccff00ccccffcccccccccc99cccc66cccc33cccc00cc99ffcc99cc'
    'cc9999cc9966cc9933cc9900cc66ffcc66cccc6699cc6666cc6633cc6600cc33ffcc33cccc3399cc3366cc3333cc3300'
    'cc00ffcc00cccc0099cc0066cc003399ffff99ffcc99ff9999ff6699ff3399ff0099ccff99cccc99cc9999cc6699cc33'
    '99cc009999ff9999cc9999999999669999339999009966ff9966cc9966999966669966339966009933ff9933cc993399'
    '9933669933339933009900ff9900cc99009999006699003366ffff66ffcc66ff9966ff6666ff3366ff0066ccff66cccc'
    '66cc9966cc6666cc3366cc006699ff6699cc6699996699666699336699006666ff6666cc666699666666666633666600'
    '6633ff6633cc6633996633666633336633006600ff6600cc66009966006666003366000033ffff33ffcc33ff9933ff66'
    '33ff3333ff0033ccff33cccc33cc9933cc6633cc3333cc003399ff3399cc3399993399663399333399003366ff3366cc'
    '3366993366663366333366003333ff3333cc3333993333663333333333003300ff3300cc33009933006633003300ffff'
    '00ffcc00ff9900ff6600ff3300ccff00cccc00cc9900cc6600cc330099ff0099cc0099990099660099330066ff0066cc'
    '0066990066660066330033ff0033cc003399003366003333ee0000dd0000aa0000880000770000550000440000220000'
    '00ee0000dd0000bb0000aa000088000077000055000044000022000000ee0000dd0000bb0000aa000088000077000055'
    '000044000022eeeeeeddddddbbbbbbaaaaaa888888777777555555444444222222111111'
)


def system_palette(depth):
    if depth == 4:
        return SYSTEM16
    center = bytes.fromhex(SYSTEM_CENTER_HEX)
    return SYSTEM_LOW + [tuple(center[i:i + 3]) for i in range(0, len(center), 3)] + SYSTEM_HIGH


def inspect_bmp(data):
    if len(data) < 54 or data[:2] != b'BM':
        raise FormatError('damaged preview BMP header')
    if u32(data, 14) != 40:
        raise Unsupported('unsupported preview BMP header')
    size, offset = u32(data, 2), u32(data, 10)
    width, height, planes, depth, compression, image_size, xppm, yppm, colors, important = \
        struct.unpack_from('<iiHHIIiiII', data, 18)
    if planes != 1 or width < 1 or height == 0:
        raise FormatError('invalid preview BMP dimensions/planes')
    if depth not in (4, 8) or compression != 0:
        raise Unsupported('unsupported preview BMP encoding')
    entries = colors or (1 << depth)
    stride = ((width * depth + 31) // 32) * 4
    if offset != 54 + 4 * entries or len(data) != offset + stride * abs(height):
        raise FormatError('preview BMP extent mismatch')
    # Some writers put zero in the optional image-size member.
    if size != len(data) or image_size not in (0, stride * abs(height)):
        raise FormatError('preview BMP size mismatch')
    return {'width': width, 'height': height, 'depth': depth, 'palette_entries': entries,
            'reserved': list(struct.unpack_from('<HH', data, 6)),
            'pixels_per_meter': [xppm, yppm], 'important_colors': important}


@dataclass
class Wave:
    rate: int
    channels: int
    bits: int
    pcm: bytes
    metadata: list

    @property
    def duration(self):
        return Fraction(len(self.pcm), self.rate * self.channels * (self.bits // 8))


def read_wave(data, warnings, name):
    if len(data) < 12 or data[:4] != b'RIFF' or data[8:12] != b'WAVE':
        raise Unsupported(f'{name}: embedded sound is not RIFF/WAVE')
    limit = u32(data, 4) + 8
    if limit != len(data):
        warnings.append(f'{name}: RIFF length {limit}, actual {len(data)}; reading available chunks')
    pos = 12
    fmt = pcm = None
    metadata = []
    while pos + 8 <= len(data):
        tag, size = data[pos:pos + 4], u32(data, pos + 4)
        start = pos
        pos += 8
        value = data[pos:min(pos + size, len(data))]
        if len(value) < size:
            warnings.append(f'{name}: truncated WAV {tag!r}')
        metadata.append({'tag': tag.decode('ascii', errors='backslashreplace'),
                         'offset': start, 'declared_size': size, 'actual_size': len(value)})
        if tag == b'fmt ':
            if len(value) < 16:
                raise FormatError(f'{name}: truncated WAVEFORMAT')
            code, channels, rate, byte_rate, align, bits = struct.unpack_from('<HHIIHH', value)
            if code != 1 or channels not in (1, 2) or bits not in (8, 16) or not rate:
                raise Unsupported(f'{name}: unsupported WAV codec/channels/depth {code}/{channels}/{bits}')
            if align != channels * bits // 8 or byte_rate != rate * align:
                raise FormatError(f'{name}: invalid PCM alignment or byte rate')
            if len(value) not in (16, 18) or (len(value) == 18 and u16(value, 16)):
                raise Unsupported(f'{name}: unsupported extended WAVEFORMAT')
            fmt = (rate, channels, bits)
        elif tag == b'data':
            pcm = value if pcm is None else pcm + value
        elif tag == b'LIST':
            if value[:4] != b'INFO':
                raise Unsupported(f'{name}: unsupported WAV LIST type')
            info = []
            q = 4
            while q + 8 <= len(value):
                key, n = value[q:q + 4], u32(value, q + 4)
                q += 8
                if q + n > len(value):
                    raise FormatError(f'{name}: truncated INFO value')
                info.append({'tag': key.decode('ascii'), 'bytes_hex': value[q:q+n].hex(),
                             'text': value[q:q+n].rstrip(b'\0').decode('cp1252', errors='backslashreplace')})
                q += n
                if n & 1:
                    if q == len(value):
                        raise FormatError(f'{name}: missing INFO alignment byte')
                    info[-1]['alignment_byte'] = value[q]
                    q += 1
            if q != len(value):
                raise FormatError(f'{name}: incomplete INFO tag')
            metadata[-1]['info'] = info
        elif tag != b'JUNK':
            raise Unsupported(f'{name}: unrecognized WAV metadata {tag!r}')
        pos += len(value)
        if size & 1 and pos < len(data):
            metadata[-1]['alignment_byte'] = data[pos]
            pos += 1
    if pos != len(data):
        warnings.append(f'{name}: {len(data)-pos} incomplete trailing WAV bytes')
    if fmt is None or pcm is None:
        raise FormatError(f'{name}: WAV lacks format or samples')
    align = fmt[1] * fmt[2] // 8
    if len(pcm) % align:
        warnings.append(f'{name}: dropping incomplete PCM sample')
        pcm = pcm[:len(pcm) // align * align]
    return Wave(*fmt, pcm, metadata)


def png_indexed(canvas, width, height, palette):
    def chunk(tag, payload):
        return struct.pack('>I', len(payload)) + tag + payload + struct.pack('>I', zlib.crc32(tag + payload))
    rows = b''.join(b'\0' + canvas[y * width:(y + 1) * width] for y in range(height - 1, -1, -1))
    colors = bytes(c for rgb in palette for c in rgb)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 3, 0, 0, 0))
            + chunk(b'PLTE', colors) + chunk(b'IDAT', zlib.compress(rows, 6)) + chunk(b'IEND', b''))


def tree_audit(nodes):
    output = []
    for node in nodes:
        record = {'tag': node.tag, 'start': node.start, 'end': node.end}
        if isinstance(node.value, list):
            record['children'] = tree_audit(node.value)
        elif isinstance(node.value, bytes):
            record['payload_bytes'] = len(node.value)
            record['sha256'] = hashlib.sha256(node.value).hexdigest()
        else:
            record['value'] = node.value
        output.append(record)
    return output


class Movie:
    def __init__(self, data):
        # Positive identification precedes resource allocation or any output.
        if len(data) < 24 or data[:4] != b'GDAW' or data[8:12] != b'RSRC' or data[16:20] not in (b'RLE4', b'RLE8'):
            raise Unsupported('not a GDAW accelerated RLE4/RLE8 animation')
        self.data = data
        self.warnings = []
        self.linearization_reason = None
        self.root = parse(data, self.warnings)
        if len(self.root) != 1 or self.root[0].tag != 'GDAW':
            raise FormatError('extra data outside the GDAW root')
        top = self.root[0].value
        def one(tag):
            found = [n for n in top if n.tag == tag]
            if len(found) != 1:
                raise FormatError(f'exactly one {tag} chunk required')
            return found[0]
        self.version = one('VERS').fields()
        if self.version.get('dwvr') not in (0x10A1A, 0x20000):
            raise Unsupported(f'unsupported format version {self.version.get("dwvr")}')
        pref = one('PREF').fields()
        if pref.get('wdzz') != 0x707A or pref.get('wdac') not in (1, 2):
            raise Unsupported('unsupported acceleration/compression profile')
        self.depth = 4 if pref['wdac'] == 1 else 8
        self.width, self.height = pref['ptex']
        if not (0 < self.width <= 16384 and 0 < self.height <= 16384) or self.width * self.height > 32_000_000:
            raise FormatError('invalid or excessive canvas dimensions')
        if pref.get('ptan', (0, 0)) != (0, 0):
            raise Unsupported('nonzero animation anchor is not implemented')
        self.preview = None
        self.preview_info = None
        try:
            self.preview, blocks = decompress_blocks(pref['tzpi'])
            self.preview_info = {'blocks': blocks, 'bmp': inspect_bmp(self.preview)}
        except Unsupported:
            raise
        except (FormatError, KeyError) as exc:
            self.warnings.append(f'preview could not be recovered: {exc}')
        self.scene = one('SEEN')
        scene = self.scene.fields()
        self.frame_count = scene['wdnf']
        if not 1 <= self.frame_count <= 65535:
            raise FormatError('invalid scene frame count')
        if scene.get('wdnn') != 1:
            raise Unsupported('scene wdnn other than 1 is not implemented')
        self.events = collections.defaultdict(list)
        fram = [n for n in self.scene.value if n.tag == 'FRAM']
        if len(fram) != 1:
            raise FormatError('scene must contain one FRAM chunk')
        self.path = []
        for node in fram[0].value:
            if node.tag == 'PATH':
                self.path.extend(node.value)
                continue
            event = node.fields()
            frame = event.get('wdif', 0)
            if not 1 <= frame <= self.frame_count:
                self.warnings.append(f'{node.tag} at invalid frame {frame}; event omitted')
                continue
            self.events[frame].append((node.tag, event))
        self.palettes = {'System': system_palette(self.depth)}
        self.sounds = {}
        self.sound_audit = {}
        self.backgrounds = {}
        self.records = []
        self.raw_chunks = []
        resources = [n for c in top if c.tag == 'RSRC' for n in c.value]
        for node in resources:
            m = node.fields() if isinstance(node.value, list) else None
            if node.tag in RAW:
                if int(node.tag[-1]) != self.depth:
                    raise Unsupported('RLE depth does not match wdac')
                self.raw_chunks.append((node.start + 8, node.end))
            elif node.tag == 'PALT':
                if m.get('wdvr') != 0x300 or m.get('wdne') != 236 or len(m['tdpe']) != 944:
                    raise Unsupported('unsupported logical palette layout')
                colors = [tuple(m['tdpe'][i:i + 3]) for i in range(0, 944, 4)]
                flags = m['tdpe'][3::4]
                if any(flag != 4 for flag in flags):
                    raise Unsupported('unsupported palette-entry flags')
                self.palettes[m['psnm']] = SYSTEM_LOW + colors + SYSTEM_HIGH
            elif node.tag == 'BKGD':
                if m.get('byty') != ord('r'):
                    raise Unsupported('non-accelerated background')
                records = []
                current = None
                for f in node.value:
                    if f.tag == 'byrt':
                        if f.value != ord('r'):
                            raise Unsupported('unsupported raster record type')
                        current = {'background': m['psnm']}
                        records.append(current)
                    elif f.tag in ('wd#f', 'wd#t', 'dw4o', 'dw4s', 'dw8o', 'dw8s'):
                        if current is None:
                            raise FormatError('raster field before byrt')
                        current[f.tag] = f.value
                if len(records) != m.get('wdrn', 0):
                    self.warnings.append(f'background {m["psnm"]}: record count mismatch')
                self.backgrounds[m['psnm']] = m
                self.records.extend(records)
            elif node.tag == 'SWND':
                if m.get('wdty') not in (0x0077, 0x7677):
                    raise Unsupported('non-WAV SWND resource')
                try:
                    wave, blocks = decompress_blocks(m['tzfd'])
                    if len(wave) != m['dwfs']:
                        self.warnings.append(f'{m["psnm"]}: sound file size mismatch')
                    self.sounds[m['psnm']] = read_wave(wave, self.warnings, m['psnm'])
                    self.sound_audit[m['psnm']] = {
                        'blocks': blocks, 'expanded_bytes': len(wave),
                        'sha256': hashlib.sha256(wave).hexdigest(),
                        'riff_chunks': self.sounds[m['psnm']].metadata}
                except Unsupported:
                    raise
                except (FormatError, KeyError) as exc:
                    self.warnings.append(f'{m.get("psnm")}: corrupt audio omitted: {exc}')
            elif node.tag == 'ACTR':
                self.validate_actor(node)
        self.validate_paths()
        self.validate_events()
        self.frames = self.decode_frames()

    def validate_actor(self, node):
        m = node.fields()
        if m.get('wdkd') != 0x7874 or m.get('wdek') != 0x7874 or 'nnel' not in m:
            raise Unsupported('only accelerated text hotspot actor metadata is supported')
        counts = collections.Counter(n.tag for n in node.value)
        for field, count in [('wdmc', 'rccr'), ('wdnw', 'wdwp'), ('wdnl', 'wdlp')]:
            if m.get(field) != counts[count]:
                raise FormatError(f'actor {field} count mismatch')
        # The RLE surface already contains the text; these are hit-test metrics.
        if m.get('pspl') != 'System' or m.get('wdal') != 0:
            raise Unsupported('unsupported text hotspot palette or alignment')

    def validate_paths(self):
        for track in self.path:
            for node in track.value:
                m = node.fields()
                if m.get('wdfn') != 1 or m.get('ptof') != (0, 0) or m.get('wdsh') or m.get('wdsf'):
                    raise Unsupported('unsupported accelerated hotspot trajectory')
                if m.get('wdia') != 0x7073 or m.get('wdig') != 0x210:
                    raise Unsupported('unsupported hotspot interaction')
                action = parse(m['tdie'], [], parent='FRAM')
                if len(action) != 1 or action[0].tag != 'PLEV' or action[0].fields().get('byty') != ord('e'):
                    raise Unsupported('only a stop-play hotspot action is supported')
                cells = [f.value for f in node.value if f.tag == 'tdel']
                if len(cells) != self.frame_count:
                    raise FormatError('hotspot element count differs from scene length')
                for cell in cells:
                    if len(cell) != 8:
                        raise Unsupported('unsupported hotspot element size')
                    dx, dy, cel, flags = struct.unpack('<hhHH', cell)
                    if (dx, dy, cel) != (0, 0, 1) or flags not in (1, 2):
                        raise Unsupported('unsupported hotspot element encoding')

    def validate_events(self):
        for frame, events in self.events.items():
            for tag, m in events:
                if tag == 'BKEV':
                    if m.get('psnm') not in self.backgrounds or m.get('byal') != ord('z'):
                        raise Unsupported('unsupported background event/reference/alignment')
                elif tag == 'TMEV' and not 1 <= m.get('wddy', 0) <= 1000:
                    raise Unsupported('unsupported frame rate')
                elif tag == 'CREV' and m.get('ptpx') != (0, 0):
                    raise Unsupported('moving pointer events are not implemented')
                elif tag == 'PTEV' and m.get('psnm') not in self.palettes:
                    raise FormatError(f'palette {m.get("psnm")!r} not found')
                elif tag == 'SNEV':
                    if m.get('wdty') not in (0x7677, 0x6C6B):
                        raise Unsupported('unsupported sound event type')
                    name = m.get('pssn')
                    # A named resource takes precedence over the fallback kill selector.
                    if name and name not in self.sounds:
                        self.warnings.append(f'frame {frame}: missing/corrupt sound {name!r}; silence used')
                elif tag == 'DSEV':
                    if m.get('wdty') != 0x6670 or m.get('dwti') != 0 or m.get('pstc') != '':
                        raise Unsupported('nonzero or unsupported dissolve/fade event')
                elif tag == 'PLEV' and m.get('byty') not in (ord('p'), ord('l'), ord('e')):
                    raise Unsupported('unsupported play-control operation')
        if not any(t == 'TMEV' for t, m in self.events[1]):
            raise Unsupported('initial playback rate is not explicitly specified')

    def decode_frames(self):
        """Build the directed raster graph, including all non-played edges."""
        edges = {}
        spans = []
        self.rle_audit = []
        for r in self.records:
            try:
                source, target = r['wd#f'], r['wd#t']
                start, size = r[f'dw{self.depth}o'], r[f'dw{self.depth}s']
            except KeyError as exc:
                raise FormatError('incomplete raster record') from exc
            if not 1 <= source <= self.frame_count or not 1 <= target <= self.frame_count:
                raise FormatError('raster graph frame outside scene')
            if not any(a <= start and start + size <= b for a, b in self.raw_chunks):
                # Recover an explicitly addressed, truncated stream only if its start is in the chunk.
                limits = [b for a, b in self.raw_chunks if a <= start < b]
                if not limits:
                    raise FormatError('raster reference outside RLE chunk')
                size = min(limits) - start
                self.warnings.append(f'truncated raster {source}->{target}')
            data = self.data[start:start + size]
            if (source, target) in edges and edges[source, target] != data:
                raise Unsupported('multiple differing RLE records for one graph edge')
            edges[source, target] = data
            spans.append((start, start + size))
            entry = {'from': source, 'to': target, 'start': start, 'end': start + size}
            try:
                entry['commands'] = apply_rle(data, self.depth, bytearray(self.width * self.height), self.width, self.height)
            except FormatError as exc:
                entry['error'] = str(exc)
                self.warnings.append(f'raster {source}->{target}: {exc}; decoded prefix retained')
            self.rle_audit.append(entry)
        for a, b in self.raw_chunks:
            cursor = a
            for start, end in sorted(set(spans)):
                if not a <= start < b:
                    continue
                if start != cursor:
                    raise Unsupported(f'unaccounted or overlapping RLE bytes at 0x{cursor:x}')
                cursor = end
            if cursor != b:
                raise Unsupported(f'unreferenced RLE tail at 0x{cursor:x}')
        frames = {}
        pending = set(range(1, self.frame_count + 1))
        while pending:
            progressed = False
            for target in sorted(pending):
                if (target, target) in edges:
                    source = target
                    canvas = bytearray(self.width * self.height)
                else:
                    sources = sorted(s for s, t in edges if t == target and s in frames)
                    if not sources:
                        continue
                    source = sources[0]
                    canvas = bytearray(frames[source])
                try:
                    apply_rle(edges[source, target], self.depth, canvas, self.width, self.height)
                except FormatError:
                    pass  # Diagnostic was recorded by the validation pass.
                frames[target] = bytes(canvas)
                pending.remove(target)
                progressed = True
            if not progressed:
                raise FormatError(f'raster frames are unreachable from any keyframe: {sorted(pending)[:12]}')
        # Verify alternate encodings and return/loop edges, not just forward playback.
        self.graph_mismatches = []
        for (source, target), data in edges.items():
            canvas = bytearray(self.width * self.height) if source == target else bytearray(frames[source])
            try:
                apply_rle(data, self.depth, canvas, self.width, self.height)
            except FormatError:
                continue
            if canvas != frames[target]:
                mismatch = {'from': source, 'to': target,
                            'different_pixels': sum(a != b for a, b in zip(canvas, frames[target]))}
                self.graph_mismatches.append(mismatch)
                self.warnings.append(f'alternate raster edge {source}->{target} differs from keyframe reconstruction')
        self.edges = edges
        return frames

    def timeline(self, linearize=None, max_seconds=3600):
        """Prefer normal playback; automatically linearize unexportable interaction.

        True forces linearization. False requests strict playback for callers
        that need to inspect whether an autonomous export is possible.
        """
        self.linearization_reason = None
        if linearize is not None:
            if linearize:
                self.linearization_reason = 'linearization explicitly requested'
            return self._timeline(linearize, max_seconds)
        try:
            return self._timeline(False, max_seconds)
        except InteractivePlayback as exc:
            self.linearization_reason = str(exc)
            self.warnings.append('Automatic partial preview: ' + str(exc))
            return self._timeline(True, max_seconds)

    def _timeline(self, linearize, max_seconds):
        markers = {m['psnm']: f for f, events in self.events.items() for t, m in events if t == 'MKEV'}
        unsupported = []
        for f, events in self.events.items():
            for t, m in events:
                if t != 'PLEV':
                    continue
                interactive = any(k in m for k in ('nnml', 'nnmr', 'nnak', 'wdvk'))
                infinite = m.get('byty') == ord('l') and m.get('wdcn') == 65534
                audio_driven = 'nnwv' in m
                if interactive:
                    unsupported.append(f'mouse/key wait at frame {f}')
                if infinite:
                    unsupported.append(f'infinite loop at frame {f}')
                if audio_driven:
                    unsupported.append(f'audio-completion loop at frame {f}')
        if unsupported and not linearize:
            raise InteractivePlayback('; '.join(unsupported))
        rate = next(m['wddy'] for t, m in self.events[1] if t == 'TMEV')
        palette = 'System'
        frame = 1
        elapsed = Fraction(0)
        audio = None
        sound_start = Fraction(0)
        sound_loop = False
        segments = []
        loops = {}
        visits = 0
        while 1 <= frame <= self.frame_count:
            visits += 1
            if visits > 1_000_000 or elapsed > max_seconds:
                raise Unsupported(f'playback exceeds export limit ({max_seconds} seconds); increase --max-seconds')
            events = self.events[frame]
            for tag, m in events:
                if tag == 'TMEV':
                    rate = m['wddy']
                elif tag == 'PTEV':
                    palette = m['psnm']
                elif tag == 'SNEV':
                    name = m.get('pssn')
                    audio = name if name in self.sounds else None
                    sound_start = elapsed
                    sound_loop = 'nnlp' in m
            # Pause is tested after the ordinary display interval. Its timer or
            # wave completion competes with that interval, so it extends the hold.
            duration = Fraction(1, rate)
            jump = None
            stop = False
            for tag, m in events:
                if tag != 'PLEV':
                    continue
                kind = m['byty']
                if kind == ord('p'):
                    conditions = []
                    if m.get('wddy', 0):
                        conditions.append(Fraction(m['wddy'], 10))
                    if 'nnws' in m:
                        if not audio:
                            conditions.append(Fraction(0))
                        elif not sound_loop:
                            remaining = self.sounds[audio].duration - (elapsed - sound_start)
                            conditions.append(max(Fraction(0), remaining))
                        elif not conditions and not linearize:
                            raise InteractivePlayback(f'frame {frame}: waiting for looping WAV cannot finish')
                    # Enabled completion conditions are alternatives. Zero time
                    # disables the timer rather than immediately ending the wait.
                    hold = min(conditions) if conditions else Fraction(0)
                    duration = max(duration, hold)
                elif kind == ord('l'):
                    if linearize:
                        continue
                    target = markers.get(m.get('psmt'))
                    if target is None or target >= frame:
                        raise FormatError(f'frame {frame}: invalid loop marker')
                    remaining = loops.setdefault(frame, m.get('wdcn', 0))
                    if remaining:
                        loops[frame] -= 1
                        jump = target
                elif kind == ord('e'):
                    stop = True
            segments.append({'frame': frame, 'palette': palette, 'start': elapsed, 'duration': duration,
                             'sound': audio, 'sound_offset': elapsed - sound_start, 'sound_loop': sound_loop})
            elapsed += duration
            if stop:
                break
            frame = jump if jump is not None else frame + 1
        if linearize:
            self.warnings.append('PARTIAL PREVIEW: loop branches bypassed; mouse/key waits receive no extra hold')
        return segments, elapsed

    def audit(self, segments=None, duration=None):
        result = {'input_bytes': len(self.data), 'sha256': hashlib.sha256(self.data).hexdigest(),
                  'profile': 'GDAW accelerated RLE', 'depth': self.depth,
                  'width': self.width, 'height': self.height, 'source_frames': self.frame_count,
                  'complete_format_reverse_engineering': False,
                  'partial_preview': self.linearization_reason is not None,
                  'linearization_reason': self.linearization_reason,
                  'limitations': ['metadata meanings not all proven; see astoundAnimation.txt',
                                  'AVI cannot preserve interactive user input'],
                  'tree': tree_audit(self.root), 'preview': self.preview_info,
                  'sounds': self.sound_audit, 'rle_records': self.rle_audit,
                  'alternate_edge_mismatches': self.graph_mismatches, 'warnings': self.warnings}
        if segments is not None:
            result['duration_seconds'] = float(duration)
            result['timeline'] = [{k: str(v) if isinstance(v, Fraction) else v for k, v in s.items()} for s in segments]
        return result


def run_ffmpeg(args, **kwargs):
    result = subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin'] + args,
                            stderr=subprocess.PIPE, **kwargs)
    if result.returncode:
        raise FormatError('ffmpeg: ' + result.stderr.decode('utf-8', errors='replace').strip())
    return result.stdout


def round_fraction(value):
    return (2 * value.numerator + value.denominator) // (2 * value.denominator)


def render(movie, segments, duration, destination, work):
    """Lossless FFV1 video and PCM audio; millisecond AVI video time base."""
    ticks = 1000
    paths = {}
    concat = []
    last_tick = 0
    for s in segments:
        frame, palette = s['frame'], s['palette']
        key = (frame, palette)
        if key not in paths:
            name = f'frame-{len(paths):06d}.png'
            pixels = movie.frames[frame]
            # A custom palette is always 8-bit; 4-bit streams use SYSTEM16.
            pal = movie.palettes[palette] if movie.depth == 8 else SYSTEM16
            (work / name).write_bytes(png_indexed(pixels, movie.width, movie.height, pal))
            paths[key] = name
        end_tick = round_fraction((s['start'] + s['duration']) * ticks)
        count = end_tick - last_tick
        if count <= 0:
            raise Unsupported('frame interval cannot be represented on the 1 ms AVI time base')
        concat.extend([f"file '{paths[key]}'", 'option framerate 1000', f'duration {count / ticks:.3f}'])
        last_tick = end_tick
    concat[-1] = f'duration {float(concat[-1].split()[1]) - 0.001:.3f}'
    concat.extend([f"file '{paths[segments[-1]['frame'], segments[-1]['palette']]}'", 'option framerate 1000'])
    script = work / 'frames.ffconcat'
    script.write_text('ffconcat version 1.0\n' + '\n'.join(concat) + '\n')
    # Resample once per resource, then place/replace each sound on its exact
    # event time. ffmpeg's resampler preserves pitch for nonstandard source rates.
    rate, channels = 44100, 2
    sound_cache = {}
    used = {s['sound'] for s in segments if s['sound']}
    for name in used:
        wave = movie.sounds[name]
        pcm = run_ffmpeg(['-f', 'u8' if wave.bits == 8 else 's16le', '-ar', str(wave.rate),
                          '-ac', str(wave.channels), '-i', 'pipe:0', '-f', 's16le',
                          '-ar', str(rate), '-ac', str(channels), 'pipe:1'],
                         input=wave.pcm, stdout=subprocess.PIPE)
        sound_cache[name] = pcm
    audio_path = work / 'audio.pcm'
    with audio_path.open('wb') as stream:
        last_sample = 0
        for s in segments:
            end_sample = round_fraction((s['start'] + s['duration']) * rate)
            count = end_sample - last_sample
            name = s['sound']
            if name and sound_cache[name]:
                data = sound_cache[name]
                samples = len(data) // 4
                offset = round_fraction(s['sound_offset'] * rate)
                if s['sound_loop']:
                    offset %= samples
                    first = data[offset * 4:]
                    length = count * 4
                    piece = (first + data * max(0, (length - len(first) + len(data) - 1) // len(data)))[:length]
                else:
                    piece = data[min(offset, samples) * 4:min(offset + count, samples) * 4]
                    piece += b'\0' * (count * 4 - len(piece))
            else:
                piece = b'\0' * (count * 4)
            stream.write(piece)
            last_sample = end_sample
    output = work / 'encoded.avi'
    args = ['-y', '-safe', '0', '-f', 'concat', '-i', str(script)]
    if movie.sounds:
        args += ['-f', 's16le', '-ar', str(rate), '-ac', str(channels), '-i', str(audio_path)]
    args += ['-map', '0:v:0']
    if movie.sounds:
        args += ['-map', '1:a:0', '-c:a', 'pcm_s16le']
    args += ['-c:v', 'ffv1', '-level', '3', '-pix_fmt', 'bgr0',
             '-fps_mode', 'vfr', '-t', f'{last_tick / ticks:.3f}', '-f', 'avi', str(output)]
    run_ffmpeg(args, stdout=subprocess.DEVNULL)
    # Do not expose a partial output. Replace atomically on the output filesystem.
    os.chmod(output, 0o664)
    os.replace(output, destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('inputFile', type=Path)
    parser.add_argument('outputFile', type=Path)
    parser.add_argument('--linearize-interactive', action='store_true',
                        default=None,
                        help='force partial preview; automatic when interactive playback prevents normal export')
    parser.add_argument('--max-seconds', type=int, default=3600, help='maximum export duration (default: 3600)')
    parser.add_argument('--audit-json', type=Path, help='write a structural/decoding audit after successful conversion')
    args = parser.parse_args()
    try:
        if args.inputFile.resolve() == args.outputFile.resolve():
            raise FormatError('input and output paths must differ')
        movie = Movie(args.inputFile.read_bytes())
        segments, duration = movie.timeline(args.linearize_interactive, args.max_seconds)
        if not shutil.which('ffmpeg'):
            raise FormatError('ffmpeg is required on PATH')
        if not args.outputFile.parent.is_dir():
            raise FormatError('output directory does not exist')
        with tempfile.TemporaryDirectory(prefix='.astound-', dir=args.outputFile.parent) as directory:
            render(movie, segments, duration, args.outputFile, Path(directory).resolve())
        if args.audit_json:
            args.audit_json.write_text(json.dumps(movie.audit(segments, duration), indent=2) + '\n')
            args.audit_json.chmod(0o664)
        for warning in movie.warnings:
            print('warning: ' + warning, file=sys.stderr)
        print(f'{args.outputFile}: {movie.width}x{movie.height}, {len(segments)} frame visits, '
              f'{float(duration):.3f} seconds, {len(movie.sounds)} WAV resources')
        return 0
    except (FormatError, OSError, KeyError, struct.error, ValueError) as exc:
        print(f'astoundAnimation: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

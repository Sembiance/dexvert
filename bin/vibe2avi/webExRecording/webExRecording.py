#!/usr/bin/env python3
# Vibe coded by Codex
"""Decode the WOTF 0x0600 desktop/G.723.1 profile to lossless TSCC/PCM AVI.

This is an independently implemented, deliberately limited WRF decoder. See
webExRecording.txt for the supported grammar and remaining semantic unknowns.
Dependencies: numpy, Pillow, PyAV (tested with 18.0.0). No vendor binaries used.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import io
import itertools
import json
import os
from pathlib import Path
import shutil
import struct
import sys
from fractions import Fraction
import zlib


class FormatError(Exception):
    """A structurally damaged recording."""


class Unsupported(Exception):
    """A different format or an unimplemented feature; never silently ignored."""


def need(condition, message):
    if not condition:
        raise FormatError(message)


def supported(condition, message):
    if not condition:
        raise Unsupported(message)


def unpack(fmt, data, offset=0):
    size = struct.calcsize('<' + fmt)
    need(offset >= 0 and offset + size <= len(data), 'truncated ' + fmt + ' field')
    return struct.unpack_from('<' + fmt, data, offset)


def inflate(data, expected=None):
    """WebEx's six-byte gzip header, raw DEFLATE, CRC32 and ISIZE."""
    need(len(data) >= 14, 'truncated WebEx gzip member')
    need(data[:3] == b'\x1f\x8b\x08', 'damaged compressed-member signature/method')
    supported(data[3] == 0, 'unsupported compressed-member flags')
    crc, size = unpack('II', data, len(data) - 8)
    need(size <= 128 * 1024 * 1024, 'decompressed member exceeds resource limit')
    if expected is not None:
        need(size == expected, 'conflicting decompressed lengths')
    dec = zlib.decompressobj(-15)
    try:
        result = dec.decompress(data[6:-8], size + 1)
    except zlib.error as exc:
        raise FormatError('invalid DEFLATE stream: ' + str(exc)) from exc
    need(dec.eof and not dec.unused_data and not dec.unconsumed_tail,
         'incomplete DEFLATE stream or trailing compressed bytes')
    need(len(result) == size, 'decompressed length mismatch')
    need(zlib.crc32(result) == crc, 'compressed-member CRC32 mismatch')
    return result


def messages(data):
    pos = 0
    while pos < len(data):
        need(len(data) - pos >= 9, 'truncated screen command')
        size, = unpack('I', data, pos + 1)
        need(size >= 9 and pos + size <= len(data), 'invalid screen-command length')
        yield data[pos:pos + size]
        pos += size


class Recording:
    def __init__(self, path):
        self.path = Path(path)
        with self.path.open('rb') as f:
            head = f.read(36)
            supported(head[:4] == b'WOTF', 'not a WOTF recording')
            need(len(head) == 36, 'truncated WOTF header')
            self.header = unpack('9I', head)
            supported(self.header[1] == 0x600, 'unsupported WOTF version 0x%x' % self.header[1])
            self.data = head + f.read()
        self.warnings = []
        self.counts = collections.Counter()
        self.command_counts = collections.Counter()
        self.records = []
        self.blocks = []
        self.coverage = []
        self.width = self.height = 0
        self.duration = 0
        self.audio_frames = 0
        self.audio_tables = collections.Counter()
        self.metadata = []
        self._scan()

    def warning(self, text):
        if text not in self.warnings:
            self.warnings.append(text)

    def cover(self, start, end, kind):
        self.coverage.append((start, end, kind))

    def _scan(self):
        d = self.data
        _, _, size, duration, legacy_counter, flags, segments, nblocks, lengths = self.header
        if size != len(d):
            self.warning('Header file size differs from physical file size; using bounded physical records.')
        supported(flags == 0, 'unsupported nonzero file control flags')
        title_len, description_len = lengths & 65535, lengths >> 16
        pos = 36
        need(pos + title_len + description_len <= len(d), 'truncated title/description')
        self.title = d[pos:pos + title_len].decode('latin1')
        pos += title_len
        self.description = d[pos:pos + description_len].decode('latin1')
        pos += description_len
        if segments:
            capacity, reserved = unpack('II', d, pos)
            supported(reserved == 0, 'unsupported segment-table flags')
            need(capacity <= len(d) - pos - 8, 'truncated segment table')
            table = d[pos + 8:pos + 8 + capacity]
            q = 0
            for _ in range(max(0, segments - 1)):
                n, begin, offset = unpack('BII', table, q)
                need(q + 9 + n <= len(table), 'truncated segment name')
                self.metadata.append({'segment_start': begin, 'segment_offset': offset,
                                      'name': table[q + 9:q + 9 + n].decode('latin1')})
                q += 9 + n
            supported(not any(table[q:]), 'unsupported nonzero segment-table slack')
            pos += 8 + capacity
        self.cover(0, pos, 'file header, text and segment table')
        tm = 0
        while pos < len(d):
            if len(d) - pos < 36:
                self.warning('Truncated block header at 0x%x; recovered preceding blocks.' % pos)
                self.cover(pos, len(d), 'damaged block tail')
                break
            supported(d[pos] == 7, 'unsupported outer block type 0x%02x at 0x%x' % (d[pos], pos))
            centiseconds, length = unpack('II', d, pos + 1)
            supported(d[pos + 9] == 1 and d[pos + 10] in (0, 1) and not any(d[pos + 11:pos + 36]),
                      'unsupported block control fields at 0x%x' % pos)
            block_start = pos
            end = pos + 36 + length
            if end > len(d):
                self.warning('Truncated block at 0x%x; recovering complete records.' % pos)
                end = len(d)
            self.blocks.append({'offset': pos, 'bytes': length, 'duration_cs': centiseconds,
                                'refresh': d[pos + 10], 'time_ms': tm})
            self.cover(pos, pos + 36, 'block header')
            pos += 36
            while pos < end:
                if end - pos < 5:
                    self.warning('Truncated timed-record header at 0x%x.' % pos)
                    self.cover(pos, end, 'damaged record tail')
                    pos = end
                    break
                tag = d[pos]
                kind = tag & 15
                supported(kind in (1, 2), 'unsupported timed-record type %d at 0x%x' % (kind, pos))
                delta, low = unpack('HH', d, pos + 1)
                length = low | ((tag >> 4) << 16)
                tm += delta
                stop = pos + 5 + length
                if stop > end:
                    self.warning('Truncated timed-record payload at 0x%x; skipped to declared block end.' % pos)
                    self.cover(pos, end, 'damaged record payload')
                    pos = end
                    break
                self.records.append((pos, tm, kind, pos + 5, stop))
                self.counts[kind] += 1
                self.cover(pos, stop, 'screen record' if kind == 1 else 'audio record')
                pos = stop
            need(pos > block_start, 'block did not advance')
        if len(self.blocks) != nblocks:
            self.warning('Header block count differs from parsed block count.')
        # Centisecond block summaries are rounded separately; child delays are
        # the precise millisecond playback clock, including the terminal delay.
        self.duration = max(tm, duration * 10)
        prev = 0
        for start, stop, _ in self.coverage:
            need(start == prev and stop >= start, 'internal byte-coverage discontinuity')
            prev = stop
        need(prev == len(d), 'internal byte-coverage gap')

    def payload(self, rec):
        pos, tm, kind, start, stop = rec
        b = self.data[start:stop]
        if kind == 1:
            raw, = unpack('I', b)
            b = inflate(b[4:], raw) if raw else b[4:]
        return b

    def audio(self, b, audit=False):
        """Parse audio batches and per-time-slot channel descriptors."""
        result = []
        tables = []
        pos = 0
        duration = 0
        while pos < len(b):
            magic, size, slots, ms, flags = unpack('5H', b, pos)
            need(magic == 0xabcd and size >= 10 + 2 * slots and pos + size <= len(b),
                 'invalid audio batch header')
            supported(flags == 0, 'unsupported audio batch flags')
            supported(slots > 0 and ms == slots * 30, 'unsupported audio slot timing')
            batch = b[pos:pos + size]
            # The legacy table is serialized but ignored by Cisco's sequential
            # playback path; its entries can be stale or outside the batch.
            table = batch[10:10 + slots * 2]
            tables.append(table.hex())
            q = 10 + slots * 2
            for _ in range(slots):
                channels, = unpack('H', batch, q)
                supported(channels == 1, 'multiple audio channels per slot are not implemented')
                channel, codec, n, offset, reserved = unpack('5H', batch, q + 2)
                supported(channel == 0 and codec == 1 and reserved == 0,
                          'unsupported audio channel/codec/descriptor flags')
                need(offset == 2 + channels * 10 and q + offset + n <= size,
                     'invalid audio frame offset/length')
                frame = batch[q + offset:q + offset + n]
                need(bool(frame), 'empty G.723.1 frame')
                expected = (24, 20, 4, 1)[frame[0] & 3]
                need(n == expected, 'G.723.1 mode disagrees with frame length')
                result.append(frame)
                q += offset + n
            need(q == size, 'unaccounted bytes in audio batch')
            duration += ms
            pos += size
        if audit:
            self.audio_frames += len(result)
            self.audio_tables.update(tables)
        return duration, result

    def preflight(self):
        screen = Screen()
        self.good = []
        self.command_limits = {}
        for rec in self.records:
            applied = 0
            try:
                b = self.payload(rec)
                if rec[2] == 1:
                    # Validate all framing first. Preserve a successfully
                    # applied prefix if a later command is damaged.
                    cmds = list(messages(b))
                    for m in cmds:
                        screen.apply(m)
                        self.command_counts[m[0]] += 1
                        applied += 1
                else:
                    self.audio(b, audit=True)
                self.good.append(rec)
            except (FormatError, OSError, ValueError) as exc:
                self.warning('Damaged record at 0x%x: %s' % (rec[0], exc))
                if applied:
                    self.good.append(rec)
            self.command_limits[rec[0]] = applied
        need(screen.canvas is not None and screen.draws > 0, 'no recoverable video drawing commands')
        self.width, self.height = screen.size
        self.metadata.extend(screen.metadata)
        return self


class Screen:
    def __init__(self):
        self.canvas = None
        self.size = (0, 0)
        self.bitmaps = {}
        self.regions = {}
        self.colors = {}
        self.brushes = {}
        self.cursors = {}
        self.cursor = None
        self.pointer = (0, 0)
        self.dirty = []
        self.draws = 0
        self.metadata = []

    def dimensions(self, w, h):
        need(0 < w <= 16384 and 0 < h <= 16384 and w * h <= 32_000_000,
             'invalid or excessive desktop dimensions')
        supported(self.canvas is None or self.size == (w, h), 'dynamic desktop dimensions are not implemented')
        if self.canvas is None:
            self.size = (w, h)
            self.canvas = np.zeros((h, w, 3), dtype=np.uint8)
            self.dirty.append((0, 0, w, h))

    @staticmethod
    def dib(b, w, h, depth):
        supported(depth in (16, 24, 32), 'unsupported bitmap bit depth %d' % depth)
        stride = ((w * depth + 31) // 32) * 4
        need(len(b) == stride * h, 'DIB data length disagrees with dimensions/stride')
        if depth == 16:
            v = np.frombuffer(b, dtype='<u2').reshape(h, stride // 2)[:, :w][::-1]
            # Windows BI_RGB 16-bit DIBs use RGB555, not RGB565.
            channels = [(v >> shift) & 31 for shift in (10, 5, 0)]
            return np.stack([(c << 3) | (c >> 2) for c in channels], axis=2).astype(np.uint8)
        a = np.frombuffer(b, dtype=np.uint8).reshape(h, stride)[:, :w * (depth // 8)]
        return a.reshape(h, w, depth // 8)[::-1, :, 2::-1].copy()

    def pointer_rect(self):
        if self.cursor is None or self.canvas is None:
            return None
        hx, hy, and_mask, xor_mask = self.cursor
        x, y = self.pointer[0] - hx, self.pointer[1] - hy
        h, w = and_mask.shape
        return (max(0, x), max(0, y), min(self.size[0], x + w), min(self.size[1], y + h))

    def pointer_dirty(self):
        r = self.pointer_rect()
        if r and r[0] < r[2] and r[1] < r[3]:
            self.dirty.append(r)

    def picture(self):
        out = self.canvas.copy()
        r = self.pointer_rect()
        if r and r[0] < r[2] and r[1] < r[3]:
            hx, hy, am, xm = self.cursor
            ox, oy = self.pointer[0] - hx, self.pointer[1] - hy
            l, t, right, bottom = r
            sx, sy = l - ox, t - oy
            region = out[t:bottom, l:right]
            region[:] = (region & am[sy:sy + bottom - t, sx:sx + right - l, None]) ^ xm[sy:sy + bottom - t, sx:sx + right - l]
        return out

    def blit(self, source, x, y, w, h, region, rop, fg=None, bg=None, brush=None):
        need(self.canvas is not None, 'drawing before desktop size')
        need(region in self.regions, 'missing clipping region %r' % (region,))
        supported(rop in (0xcc, 0xf0), 'unsupported raster operation 0x%02x' % rop)
        for l, t, r, b in self.regions[region]:
            l, t, r, b = max(l, x, 0), max(t, y, 0), min(r, x + w, self.size[0]), min(b, y + h, self.size[1])
            if l >= r or t >= b:
                continue
            if rop == 0xcc:
                need(source is not None and source.shape[0] >= h and source.shape[1] >= w,
                     'source bitmap smaller than blit rectangle')
                self.canvas[t:b, l:r] = source[t - y:b - y, l - x:r - x]
            else:
                ox, oy, style, hatch, color, pattern = brush
                supported(style in (0, 2, 3), 'unsupported brush style %d' % style)
                if style == 0:
                    self.canvas[t:b, l:r] = color
                else:
                    yy, xx = np.ogrid[t:b, l:r]
                    xx, yy = (xx - ox) % 8, (yy - oy) % 8
                    if style == 3:
                        raster = pattern
                    else:
                        supported(hatch <= 5, 'unsupported hatch style')
                        # Fixed DIB rows from the reference CTSBrush2Pattern
                        # renderer, indexed by the standard HS_* enumeration.
                        rasters = ('ff00ff00ff00ff00', 'aaaaaaaaaaaaaaaa',
                                   '8040201008040201', '0102040810204080',
                                   '101010ff10101010', '8142241881422418')
                        raster = bytes.fromhex(rasters[hatch])
                    bits = np.unpackbits(np.frombuffer(raster, dtype=np.uint8)).reshape(8, 8)[::-1]
                    mask = bits[yy, xx]
                    # Reference monochrome expansion: 1 selects the drawing
                    # foreground; 0 selects the brush's own stored RGB color.
                    self.canvas[t:b, l:r] = np.where(mask[..., None], fg, color)
            self.dirty.append((l, t, r, b))
        self.draws += 1

    def apply(self, m):
        typ = m[0]
        owner, = unpack('I', m, 5)
        p = m[9:]
        fixed = {2: 4, 12: 1, 20: 4, 25: 0, 26: 1, 27: 1,
                 32: 16, 34: 4, 42: 10, 51: 21, 53: 23, 147: 6}
        if typ in fixed:
            need(len(p) == fixed[typ], 'wrong command 0x%02x length' % typ)
        if typ == 2:
            self.dimensions(*unpack('HH', p))
        elif typ == 31:
            bank, w, h, bpp, n, index, codec = unpack('BHHBIBB', p)
            need(w > 0 and h > 0 and w * h <= 32_000_000, 'invalid bitmap dimensions')
            need(len(p) == 12 + n, 'bitmap payload length mismatch')
            b = p[12:]
            supported(codec in (0, 1, 2), 'unsupported bitmap compression %d' % codec)
            if codec == 1:
                need(bpp == 24, 'JPEG bitmap has inconsistent bit depth')
                need(b[:2] == b'\xff\xd8' and b[-2:] == b'\xff\xd9', 'invalid JPEG SOI/EOI boundaries')
                with Image.open(io.BytesIO(b)) as im:
                    need(im.format == 'JPEG' and im.size == (w, h), 'JPEG dimensions/type disagree with bitmap header')
                    im.load()
                    bitmap = np.array(im.convert('RGB'))
            else:
                if codec == 2:
                    b = inflate(b, ((w * bpp + 31) // 32) * 4 * h)
                bitmap = self.dib(b, w, h, bpp)
            self.bitmaps[(owner, bank, index)] = bitmap
        elif typ == 30:
            index, n = unpack('BH', p)
            need(len(p) == 3 + n * 8, 'region rectangle count mismatch')
            rects = [unpack('hhhh', p, 3 + i * 8) for i in range(n)]
            need(all(l <= r and t <= b for l, t, r, b in rects), 'inverted clipping rectangle')
            self.regions[(owner, index)] = rects
        elif typ == 34:
            self.colors[(owner, p[0])] = tuple(p[1:4])
        elif typ == 32:
            index, ox, oy, style, hatch = p[:5]
            supported(style in (0, 2, 3), 'unsupported brush style %d' % style)
            supported(style != 2 or hatch <= 5, 'unsupported hatch style')
            self.brushes[(owner, index)] = (ox, oy, style, hatch, tuple(p[5:8]), p[8:16])
        elif typ == 53:
            task, dc, index, bank, x, y, w, h, rop, fg, bg, sx, sy, table, region = unpack('HHBBhhhhBBBhhBB', p)
            supported(dc == 0 and table == 0, 'offscreen drawing/indexed color tables are not implemented')
            supported(rop == 0xcc, 'only SRCCOPY memory blits are implemented')
            need((owner, bank, index) in self.bitmaps, 'missing cached bitmap')
            need(w >= 0 and h >= 0 and sx >= 0 and sy >= 0, 'negative source extent')
            bitmap = self.bitmaps[(owner, bank, index)]
            self.blit(bitmap[sy:sy + h, sx:sx + w], x, y, w, h, (owner, region), rop)
        elif typ == 51:
            task, dc, x, y, w, h, rop, fg, bg, brush, pattern_w, pattern_h, table, region, flags = unpack('HHhhhhBBBBbbBBB', p)
            supported(dc == 0 and flags == 0 and table == 0, 'unsupported pattern-blit target/flags')
            supported(rop == 0xf0, 'only PATCOPY pattern blits are implemented')
            need(w >= 0 and h >= 0, 'negative pattern-blit extent')
            need((owner, brush) in self.brushes and (owner, fg) in self.colors and (owner, bg) in self.colors, 'missing brush/color cache entry')
            # Pattern dimensions are used by the unsupported indexed/color
            # brush variants, not as an offset for solid or 8x8 mono brushes.
            self.blit(None, x, y, w, h, (owner, region), rop, self.colors[(owner, fg)], self.colors[(owner, bg)], self.brushes[(owner, brush)])
        elif typ in (36, 37):
            index, hx, hy, w, h = unpack('BHHHH', p)
            need(0 < w <= 512 and 0 < h <= 512, 'invalid cursor dimensions')
            stride = ((w + 15) // 16) * 2
            size = stride * h
            color_stride = ((w * 24 + 31) // 32) * 4
            need(len(p) == 9 + size + (size if typ == 36 else color_stride * h), 'cursor plane size mismatch')
            a = np.frombuffer(p[9:9 + size], dtype=np.uint8).reshape(h, stride)
            am = (np.unpackbits(a, axis=1)[:, :w] * 255)[::-1].copy()
            b = p[9 + size:]
            if typ == 36:
                a = np.frombuffer(b, dtype=np.uint8).reshape(h, stride)
                xm = np.repeat((np.unpackbits(a, axis=1)[:, :w] * 255)[::-1, :, None], 3, axis=2)
            else:
                xm = self.dib(b, w, h, 24)
            self.cursors[(owner, typ - 10, index)] = (hx, hy, am, xm)
        elif typ in (26, 27):
            self.pointer_dirty()
            need((owner, typ, p[0]) in self.cursors, 'missing cursor cache entry')
            self.cursor = self.cursors[(owner, typ, p[0])]
            self.pointer_dirty()
        elif typ == 20:
            self.pointer_dirty()
            self.pointer = unpack('hh', p)
            self.pointer_dirty()
        elif typ == 25:
            self.pointer_dirty()
            # A system cursor is an OS resource, not a bitmap embedded in WRF.
            # Use the conventional monochrome arrow; this is an explicit
            # presentation choice, not a decoded pixel-perfect OS resource.
            shape = ('X', 'XX', 'X.X', 'X..X', 'X...X', 'X....X', 'X.....X',
                     'X......X', 'X.......X', 'X........X', 'X.....XXXXX',
                     'X..X..X', 'X.X X..X', 'XX  X..X', 'X    X..X', '     X..X', '      XX')
            am = np.full((32, 32), 255, dtype=np.uint8)
            xm = np.zeros((32, 32, 3), dtype=np.uint8)
            for y, row in enumerate(shape):
                for x, c in enumerate(row):
                    if c != ' ':
                        am[y, x] = 0
                        xm[y, x] = 255 if c == '.' else 0
            self.cursor = (0, 0, am, xm)
            self.pointer_dirty()
        elif typ == 12:
            supported(p[0] in (0, 1), 'unsupported cache-control command')
            # These notifications select/announce the sharing cache. In the
            # reference playback callback, 0 and 1 do not erase display pixels.
        elif typ == 42:
            task, dc, action, w, h, flags = unpack('HHBhhB', p)
            supported(action == 3 and task == 0 and dc == 0 and w == 0 and h == 0 and flags == 0,
                      'offscreen memory-DC operations are not implemented')
            # Action 3 destroys offscreen DCs; none can exist in this profile.
        elif typ == 1:
            event, name_len, extra_len = unpack('BBH', p)
            need(len(p) == 4 + name_len + extra_len, 'ASCE metadata length mismatch')
            supported(event in (9, 10), 'unsupported ASCE event')
            self.metadata.append({'owner': owner, 'asce_event': event,
                                  'name': p[4:4 + name_len].decode('latin1'),
                                  'extension': p[4 + name_len:].hex()})
        elif typ == 16:
            n, = unpack('H', p)
            need(len(p) == n + 2, 'capability blob length mismatch')
            self.metadata.append({'capability_blob': p[2:].hex(), 'owner': owner})
        elif typ == 147:
            command, parameter, value = unpack('BBI', p)
            supported(command in (9, 11, 147), 'unsupported sharing control command')
            self.metadata.append({'owner': owner, 'control': command, 'parameter': parameter, 'value': value})
        else:
            raise Unsupported('unimplemented screen opcode 0x%02x' % typ)


def chunk(tag, b):
    return tag + struct.pack('<I', len(b)) + b + (b'\0' if len(b) & 1 else b'')


def avi_template(w, h):
    """In-memory codec descriptor for PyAV's decoder-only TSCC remux stream."""
    main = struct.pack('<14I', 1000, 0, 0, 0x10, 1, 0, 1, 0, w, h, 0, 0, 0, 0)
    stream = struct.pack('<4s4sIHH8I4h', b'vids', b'TSCC', 0, 0, 0, 0, 1, 1000, 0, 1, 0, 0xffffffff, 0, 0, 0, w, h)
    bitmap = struct.pack('<IiiHH4sIiiII', 40, w, h, 1, 24, b'TSCC', w * h * 3, 0, 0, 0, 0)
    body = b'AVI ' + chunk(b'LIST', b'hdrl' + chunk(b'avih', main) +
                          chunk(b'LIST', b'strl' + chunk(b'strh', stream) + chunk(b'strf', bitmap)))
    body += chunk(b'LIST', b'movi' + chunk(b'00dc', zlib.compress(b'\0\1')))
    return av.open(io.BytesIO(chunk(b'RIFF', body)))


def tscc(picture, rects):
    """Lossless 24-bit TSCC: absolute RLE spans/deltas, independently zlib'd."""
    height, width, _ = picture.shape
    rows = {}
    for l, t, r, b in rects:
        for y in range(max(0, t), min(height, b)):
            if l < r:
                rows.setdefault(y, []).append((max(0, l), min(width, r)))
    out = bytearray()
    cy, cx = height - 1, 0
    for y in sorted(rows, reverse=True):
        intervals = []
        for l, r in sorted(rows[y]):
            if intervals and l <= intervals[-1][1]:
                intervals[-1] = (intervals[-1][0], max(r, intervals[-1][1]))
            else:
                intervals.append((l, r))
        if y < cy and cx:
            out += b'\0\0'
            cy -= 1
            cx = 0
        for l, r in intervals:
            dx, dy = l - cx, cy - y
            while dx or dy:
                ax, ay = min(255, dx), min(255, dy)
                out += bytes((0, 2, ax, ay))
                dx -= ax
                dy -= ay
            cy, cx = y, l
            raw = picture[y, l:r, ::-1].tobytes()
            count = r - l
            at = 0
            while count:
                n = min(255, count)
                if n < 3:
                    for _ in range(n):
                        out.append(1)
                        out += raw[at:at + 3]
                        at += 3
                else:
                    out += bytes((0, n))
                    out += raw[at:at + n * 3]
                    at += n * 3
                count -= n
            cx = r
    out += b'\0\1'
    return zlib.compress(out, 6)


def make_audio(recording):
    if not recording.audio_frames:
        return None
    output = np.zeros(recording.duration * 8, dtype=np.int16)
    decoder = av.CodecContext.create('g723_1', 'r')
    decoder.sample_rate = 8000
    decoder.layout = 'mono'
    previous = None
    for rec in recording.good:
        if rec[2] != 2:
            continue
        duration, frames = recording.audio(recording.payload(rec))
        if not frames:
            continue
        samples = []
        for b in frames:
            try:
                decoded = decoder.decode(av.Packet(b))
                pcm = np.concatenate([f.to_ndarray().reshape(-1) for f in decoded])
                need(len(pcm) == 240, 'unexpected G.723.1 decoder output length')
            except (av.FFmpegError, FormatError) as exc:
                recording.warning('Damaged G.723.1 frame at record 0x%x: %s; 30 ms silence substituted.' % (rec[0], exc))
                pcm = np.zeros(240, dtype=np.int16)
            samples.append(pcm)
        pcm = np.concatenate(samples)
        end = rec[1] * 8
        start = max(0, end - duration * 8) if previous is None else previous
        need(end >= start, 'audio packet endpoints are not monotonic')
        # Explicit clock-conversion policy: fit complete decoded packets between
        # successive recorded endpoints. This prevents accumulating clock drift
        # and does not guess codec framing, sample rate, or packet boundaries.
        count = end - start
        if count:
            positions = (np.arange(count, dtype=np.float64) + .5) * len(pcm) / count - .5
            output[start:end] = np.rint(np.interp(positions, np.arange(len(pcm)), pcm)).astype(np.int16)
        previous = end
    return output


def convert(recording, output_path, verbose=False):
    audio = make_audio(recording)
    screen = Screen()
    screen.dimensions(recording.width, recording.height)
    destination = io.BytesIO()
    template = avi_template(*screen.size)
    mux = av.open(destination, 'w', format='avi')
    video = mux.add_stream_from_template(template.streams.video[0], opaque=True)
    sound = mux.add_stream('pcm_s16le', rate=8000) if audio is not None else None
    if sound is not None:
        sound.layout = 'mono'
    audio_pos = 0
    frames_written = 0
    last_key = -60000
    last_video = -1

    def write_audio(until):
        nonlocal audio_pos
        if sound is None:
            return
        limit = min(len(audio), max(0, until * 8))
        while audio_pos < limit:
            n = min(8000, limit - audio_pos)
            frame = av.AudioFrame(format='s16', layout='mono', samples=n)
            frame.sample_rate = 8000
            frame.pts = audio_pos
            frame.time_base = Fraction(1, 8000)
            frame.planes[0].update(audio[audio_pos:audio_pos + n].astype('<i2', copy=False).tobytes())
            for packet in sound.encode(frame):
                mux.mux(packet)
            audio_pos += n

    def write_video(tm, force=False):
        nonlocal frames_written, last_key, last_video
        if not screen.dirty and not force:
            return
        if tm <= last_video:
            return
        write_audio(tm)
        key = tm - last_key >= 60000
        rects = [(0, 0, *screen.size)] if key else screen.dirty
        payload = tscc(screen.picture(), rects)
        packet = av.Packet(payload)
        packet.stream = video
        packet.pts = packet.dts = tm
        packet.time_base = Fraction(1, 1000)
        packet.is_keyframe = key
        mux.mux(packet)
        if key:
            last_key = tm
        screen.dirty.clear()
        frames_written += 1
        last_video = tm

    current = 0
    try:
        for rec in recording.good:
            if rec[1] > current:
                write_video(current)
                current = rec[1]
            if rec[2] == 1:
                try:
                    for m in itertools.islice(messages(recording.payload(rec)), recording.command_limits[rec[0]]):
                        screen.apply(m)
                except (FormatError, OSError, ValueError) as exc:
                    recording.warning('Recovered drawing failure at 0x%x: %s' % (rec[0], exc))
        write_video(current)
        # One final hold packet explicitly establishes AVI stream duration.
        final = max(recording.duration, current + 1)
        write_video(final - 1, force=True)
        write_audio(final)
        if sound is not None:
            for packet in sound.encode():
                mux.mux(packet)
    finally:
        mux.close()
        template.close()
    # No named intermediate files, and the destination is opened only after
    # parsing, rendering and muxing have succeeded.
    destination.seek(0)
    with Path(output_path).open('wb') as f:
        shutil.copyfileobj(destination, f, 1024 * 1024)
        os.fchmod(f.fileno(), os.fstat(f.fileno()).st_mode | 0o440)
    return frames_written, destination.tell()


def audit_report(recording, frame_count):
    return {'input_bytes': len(recording.data), 'sha256': hashlib.sha256(recording.data).hexdigest(),
            'structural_byte_coverage': sum(b - a for a, b, _ in recording.coverage),
            'semantic_completeness': False,
            'limitations': ['Header word at 0x10 and several control/reserved fields have unresolved meanings.',
                            'Capability negotiation payloads are length-checked and retained as opaque metadata.',
                            'ASCE/control parameters and the legacy audio-table generation rule remain partly unresolved.',
                            'System pointer uses a conventional arrow rather than an OS-specific resource.',
                            'Hatch masks follow the reference Mac player; platform parity has not been visually verified.',
                            'Audio is resampled to successive recorded packet endpoints.'],
            'header_words': recording.header, 'size': [recording.width, recording.height],
            'duration_ms': recording.duration, 'video_packets_written': frame_count,
            'audio_frames_decoded': recording.audio_frames, 'record_counts': dict(recording.counts),
            'command_counts': {'0x%02x' % k: v for k, v in sorted(recording.command_counts.items())},
            'blocks': recording.blocks, 'byte_ranges': recording.coverage,
            'legacy_audio_tables': dict(recording.audio_tables), 'metadata': recording.metadata,
            'warnings': recording.warnings}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('inputFile')
    parser.add_argument('outputFile')
    parser.add_argument('-verbose', '--verbose', action='store_true', help='also write OUTPUT.avi.json byte/record audit')
    args = parser.parse_args(argv)
    try:
        source, output = Path(args.inputFile), Path(args.outputFile)
        supported(source.resolve() != output.resolve() and
                  not (output.exists() and source.samefile(output)),
                  'input and output must be different files')
        recording = Recording(source)
        global np, Image, av
        import numpy as np
        from PIL import Image
        import av
        recording.preflight()
        frames, size = convert(recording, output, args.verbose)
        if args.verbose:
            report = Path(str(output) + '.json')
            report.write_text(json.dumps(audit_report(recording, frames), indent=2) + '\n')
            report.chmod(report.stat().st_mode | 0o440)
        for warning in recording.warnings:
            print('warning: ' + warning, file=sys.stderr)
        print('%s: %dx%d, %.3f seconds, %d video updates, %s' %
              (output, recording.width, recording.height, recording.duration / 1000,
               frames, '8 kHz mono PCM audio' if recording.audio_frames else 'no audio'), file=sys.stderr)
        return 0
    except (Unsupported, FormatError, OSError, ImportError, ValueError) as exc:
        print('webExRecording: ' + str(exc), file=sys.stderr)
        return 1
    except Exception as exc:
        print('webExRecording: conversion failed: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

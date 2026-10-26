#!/usr/bin/env python3
# Vibe coded by Codex
"""Convert headerless 2048-byte PlayStation STR/MDEC v2/v3 streams to AVI.

Python standard library + the ffmpeg executable. See mdecVideoStream.txt for
byte layout, codec tables, recovery policy, and information absent from a rip.
"""
from __future__ import annotations

import argparse
import array
import collections
from dataclasses import dataclass, field
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys

SECTOR = 2048
PAYLOAD = 2016
MAGIC = b"\x60\x01\x01\x80"
HEADER = struct.Struct("<IHHIIHHIHHI")

# MPEG-1 intra AC codebook: (prefix, zero run, absolute level).
# This is format data, not executable code copied from another decoder.
AC_CODES = (
    ("11", 0, 1),
    ("0100", 0, 2),
    ("00101", 0, 3),
    ("0000110", 0, 4),
    ("00100110", 0, 5),
    ("00100001", 0, 6),
    ("0000001010", 0, 7),
    ("000000011101", 0, 8),
    ("000000011000", 0, 9),
    ("000000010011", 0, 10),
    ("000000010000", 0, 11),
    ("0000000011010", 0, 12),
    ("0000000011001", 0, 13),
    ("0000000011000", 0, 14),
    ("0000000010111", 0, 15),
    ("00000000011111", 0, 16),
    ("00000000011110", 0, 17),
    ("00000000011101", 0, 18),
    ("00000000011100", 0, 19),
    ("00000000011011", 0, 20),
    ("00000000011010", 0, 21),
    ("00000000011001", 0, 22),
    ("00000000011000", 0, 23),
    ("00000000010111", 0, 24),
    ("00000000010110", 0, 25),
    ("00000000010101", 0, 26),
    ("00000000010100", 0, 27),
    ("00000000010011", 0, 28),
    ("00000000010010", 0, 29),
    ("00000000010001", 0, 30),
    ("00000000010000", 0, 31),
    ("000000000011000", 0, 32),
    ("000000000010111", 0, 33),
    ("000000000010110", 0, 34),
    ("000000000010101", 0, 35),
    ("000000000010100", 0, 36),
    ("000000000010011", 0, 37),
    ("000000000010010", 0, 38),
    ("000000000010001", 0, 39),
    ("000000000010000", 0, 40),
    ("011", 1, 1),
    ("000110", 1, 2),
    ("00100101", 1, 3),
    ("0000001100", 1, 4),
    ("000000011011", 1, 5),
    ("0000000010110", 1, 6),
    ("0000000010101", 1, 7),
    ("000000000011111", 1, 8),
    ("000000000011110", 1, 9),
    ("000000000011101", 1, 10),
    ("000000000011100", 1, 11),
    ("000000000011011", 1, 12),
    ("000000000011010", 1, 13),
    ("000000000011001", 1, 14),
    ("0000000000010011", 1, 15),
    ("0000000000010010", 1, 16),
    ("0000000000010001", 1, 17),
    ("0000000000010000", 1, 18),
    ("0101", 2, 1),
    ("0000100", 2, 2),
    ("0000001011", 2, 3),
    ("000000010100", 2, 4),
    ("0000000010100", 2, 5),
    ("00111", 3, 1),
    ("00100100", 3, 2),
    ("000000011100", 3, 3),
    ("0000000010011", 3, 4),
    ("00110", 4, 1),
    ("0000001111", 4, 2),
    ("000000010010", 4, 3),
    ("000111", 5, 1),
    ("0000001001", 5, 2),
    ("0000000010010", 5, 3),
    ("000101", 6, 1),
    ("000000011110", 6, 2),
    ("0000000000010100", 6, 3),
    ("000100", 7, 1),
    ("000000010101", 7, 2),
    ("0000111", 8, 1),
    ("000000010001", 8, 2),
    ("0000101", 9, 1),
    ("0000000010001", 9, 2),
    ("00100111", 10, 1),
    ("0000000010000", 10, 2),
    ("00100011", 11, 1),
    ("0000000000011010", 11, 2),
    ("00100010", 12, 1),
    ("0000000000011001", 12, 2),
    ("00100000", 13, 1),
    ("0000000000011000", 13, 2),
    ("0000001110", 14, 1),
    ("0000000000010111", 14, 2),
    ("0000001101", 15, 1),
    ("0000000000010110", 15, 2),
    ("0000001000", 16, 1),
    ("0000000000010101", 16, 2),
    ("000000011111", 17, 1),
    ("000000011010", 18, 1),
    ("000000011001", 19, 1),
    ("000000010111", 20, 1),
    ("000000010110", 21, 1),
    ("0000000011111", 22, 1),
    ("0000000011110", 23, 1),
    ("0000000011101", 24, 1),
    ("0000000011100", 25, 1),
    ("0000000011011", 26, 1),
    ("0000000000011111", 27, 1),
    ("0000000000011110", 28, 1),
    ("0000000000011101", 29, 1),
    ("0000000000011100", 30, 1),
    ("0000000000011011", 31, 1),
)

DC_CHROMA = ('00', '01', '10', '110', '1110', '11110', '111110',
             '1111110', '11111110')
DC_LUMA = ('100', '00', '01', '101', '110', '1110', '11110',
           '111110', '1111110')


class FormatError(Exception):
    """Input is foreign, unsupported, or has no recoverable picture."""


class Damaged(Exception):
    """Recognized stream data is damaged."""


def lookup(entries, width):
    table = [None] * (1 << width)
    for code, *value in entries:
        n = len(code)
        start = int(code, 2) << (width - n)
        table[start:start + (1 << (width - n))] = [(n, *value)] * (1 << (width - n))
    return table


AC_LOOKUP = lookup((*AC_CODES, ('000001', -1, 0), ('10', -2, 0)), 16)
DC_LOOKUPS = [lookup([(s, n) for n, s in enumerate(t)], 8)
              for t in (DC_CHROMA, DC_LUMA)]


class Bits:
    """MSB first within little-endian 16-bit words; never consumes guard bytes."""
    def __init__(self, data):
        if len(data) & 1:
            raise Damaged('odd compressed byte count')
        swapped = bytearray(data)
        swapped[0::2], swapped[1::2] = swapped[1::2], swapped[0::2]
        self.data = swapped + b'\0' * 4
        self.limit = len(data) * 8
        self.pos = 64

    def peek(self, n):
        i = self.pos >> 3
        return (int.from_bytes(self.data[i:i + 4], 'big') >>
                (32 - (self.pos & 7) - n)) & ((1 << n) - 1)

    def take(self, n):
        if self.pos + n > self.limit:
            raise Damaged(f'compressed data ends at bit {self.pos}, need {n} bits')
        value = self.peek(n)
        self.pos += n
        return value


def audit_picture(data, width, height):
    """Parse every DC, AC, escape, EOB, trailer and alignment bit."""
    if len(data) < 8:
        raise Damaged('missing BS header')
    words, magic, quant, version = struct.unpack_from('<4H', data)
    if magic != 0x3800 or not 1 <= quant <= 63 or version not in (2, 3):
        raise Damaged('invalid BS header')
    bits = Bits(data)
    dc_count = ((width + 15) // 16) * ((height + 15) // 16) * 6
    predictors = [0, 0, 0]
    codes = dc_bits = ac_bits = ac_count = escapes = 0
    for block in range(dc_count):
        start = bits.pos
        if version == 2:
            bits.take(10)
        else:
            component = min(block % 6, 2)
            token = DC_LOOKUPS[component == 2][bits.peek(8)]
            if token is None:
                raise Damaged(f'invalid DC prefix at bit {bits.pos}')
            n, size = token
            bits.take(n)
            value = bits.take(size)
            if size and not value & (1 << (size - 1)):
                value -= (1 << size) - 1
            predictors[component] += 4 * value
            if not -512 <= predictors[component] <= 511:
                raise Damaged(f'DC predictor out of range at bit {bits.pos}')
        dc_bits += bits.pos - start
        codes += 1
        coefficient = 0
        while True:
            start = bits.pos
            token = AC_LOOKUP[bits.peek(16)]
            if token is None:
                raise Damaged(f'invalid AC prefix at bit {bits.pos}')
            n, run, level = token
            bits.take(n)
            codes += 1
            if run == -2:
                ac_bits += bits.pos - start
                break
            if run == -1:
                run = bits.take(6)
                level = bits.take(10)
                # All 10-bit escape levels are syntax values, including zero.
                escapes += 1
            else:
                bits.take(1)  # Sign, with 1 meaning negative.
            coefficient += run + 1
            if coefficient > 63:
                raise Damaged(f'AC run crosses the block at bit {bits.pos}')
            ac_count += 1
            ac_bits += bits.pos - start
    entropy_end = bits.pos
    trailer = bits.take(10)
    issues = []
    if trailer != (511 if version == 2 else 1023):
        issues.append('incorrect ten-bit frame trailer')
    alignment_bits = bits.limit - bits.pos
    nonzero = 0
    while bits.pos < bits.limit:
        n = min(16, bits.limit - bits.pos)
        nonzero += bits.take(n).bit_count()
    if alignment_bits > 31 or nonzero:
        issues.append('noncanonical bitstream tail after frame trailer')
    expected_words = ((codes + 63) // 64) * 32
    if words != expected_words:
        issues.append(f'MDEC word count {words}, expected {expected_words}')
    return dict(version=version, quantizer=quant, mdec_codes=codes,
                mdec_dma_words=words, expected_dma_words=expected_words,
                dc_codes=dc_count, ac_codes=ac_count, escapes=escapes,
                dc_bits=dc_bits, ac_and_eob_bits=ac_bits,
                entropy_end_bit=entropy_end, trailer=trailer,
                alignment_bits=alignment_bits, nonzero_alignment_bits=nonzero,
                issues=issues)


def xa_prefix_valid(data):
    """Exact four-bit XA group redundancy and parameter grammar, no scoring."""
    if len(data) != SECTOR:
        return False
    for p in range(0, SECTOR, 128):
        group = data[p:p + 16]
        if group[:4] != group[4:8] or group[8:12] != group[12:16]:
            return False
        if any(x >> 4 > 3 or x & 15 > 12 for x in group):
            return False
    return True


@dataclass
class Picture:
    number: int
    header: tuple
    parts: dict = field(default_factory=dict)
    sectors: list = field(default_factory=list)
    issues: list = field(default_factory=list)
    data: bytes | None = None
    audit: dict | None = None


@dataclass
class Stream:
    width: int
    height: int
    pictures: list
    audio: list
    audit: dict
    warnings: list


def basic_header(data):
    if len(data) < 32 or data[:4] != MAGIC:
        return None
    h = HEADER.unpack_from(data)
    _, index, total, number, length, width, height, command, quant, version, reserved = h
    if not (0 < total <= 65535 and index < total and 8 <= length <= total * PAYLOAD
            and 0 < width <= 4096 and 0 < height <= 4096
            and command >> 16 == 0x3800 and 1 <= quant <= 63):
        return None
    return h


def parse_stream(path):
    """Recognition precedes allocation of any output file or invoking ffmpeg."""
    with path.open('rb') as source:
        first = source.read(SECTOR)
        h = basic_header(first)
        if h is None:
            raise FormatError('not a supported 2048-byte STR stream at offset zero')
        if h[9] not in (2, 3) or h[10] != 0:
            raise FormatError('unsupported STR video variant (version or reserved field)')
        # A complete sector plus its duplicated BS header is strong identification.
        # A noninitial first chunk needs another consistent STR header as evidence.
        if not (h[1] == 0 and len(first) >= 40 and first[20:28] == first[32:40]):
            confirmed = False
            for _ in range(64):
                candidate = source.read(SECTOR)
                other = basic_header(candidate)
                if other and other[5:7] == h[5:7] and other[9] in (2, 3):
                    confirmed = True
                    break
            if not confirmed:
                raise FormatError('cannot corroborate the first STR header')
        source.seek(0)
        raw = source.read()

    width, height = h[5:7]
    pictures = []
    current = None
    audio = []
    warnings = []
    spans = []
    counts = collections.Counter()
    padding_histogram = collections.Counter()
    for sector, start in enumerate(range(0, len(raw), SECTOR)):
        data = raw[start:start + SECTOR]
        if data[:4] == MAGIC and len(data) >= 32:
            head = HEADER.unpack_from(data)
            if head[9] not in (2, 3):
                raise FormatError(f'unsupported BS version {head[9]} at sector {sector}')
            if head[10] != 0:
                raise FormatError(f'unsupported STR extension at sector {sector}')
            if basic_header(data) is None:
                warnings.append(f'sector {sector}: malformed video header; ignored')
                counts['damaged_bytes'] += len(data)
                spans.append(dict(offset=start, size=len(data), kind='damaged_video_header'))
                continue
            if head[5:7] != (width, height):
                raise FormatError('changing picture dimensions are not supported')
            number = head[3]
            if current is None or number != current.number:
                if current is not None and number <= current.number:
                    raise FormatError('multiple sequences or nonincreasing frame numbers')
                current = Picture(number, head)
                pictures.append(current)
            if head[:1] + head[2:] != current.header[:1] + current.header[2:]:
                current.issues.append(f'sector {sector}: conflicting repeated frame header')
            part = head[1]
            if part in current.parts:
                current.issues.append(f'sector {sector}: duplicate chunk {part}; first retained')
            else:
                current.parts[part] = data[32:]
            current.sectors.append(sector)
            used = min(len(data) - 32, max(0, head[4] - part * PAYLOAD))
            pad = data[32 + used:]
            padding_histogram.update(pad)
            counts['str_header_bytes'] += 32
            counts['bs_bytes'] += used
            counts['sector_padding_bytes'] += len(pad)
            counts['video_sectors'] += 1
            spans.append(dict(offset=start, size=len(data), kind='video',
                              frame=number, chunk=part, payload_bytes=used,
                              padding_bytes=len(pad)))
        elif len(data) == SECTOR and not any(data):
            # A zero sector is also a syntactically silent XA prefix. The rip
            # contains no submode flag to distinguish these two meanings.
            counts['zero_sector_bytes'] += SECTOR
            counts['zero_sectors'] += 1
            spans.append(dict(offset=start, size=SECTOR, kind='zero_fill_or_silent_xa'))
        elif xa_prefix_valid(data):
            audio.append((sector, data))
            counts['xa_parameter_bytes'] += 16 * 16
            counts['xa_sample_bytes'] += 16 * 112
            counts['xa_sectors'] += 1
            spans.append(dict(offset=start, size=SECTOR, kind='xa_4bit_prefix'))
        else:
            # Once format is proven, salvage other frames without magic searches
            # or treating unrecognized bytes as invented audio samples.
            counts['damaged_bytes'] += len(data)
            warnings.append(f'sector {sector}: {len(data)} unrecognized/truncated bytes; ignored')
            spans.append(dict(offset=start, size=len(data), kind='unrecognized_or_truncated'))

    frame_audits = []
    for pic in pictures:
        head = pic.header
        needed = (head[4] + PAYLOAD - 1) // PAYLOAD
        missing = sorted(set(range(needed)) - pic.parts.keys())
        info = dict(number=pic.number, sectors=pic.sectors, declared_bytes=head[4],
                    declared_chunks=head[2], issues=pic.issues)
        if missing:
            pic.issues.append(f'missing required chunks {missing}')
        else:
            payload = b''.join(pic.parts[i] for i in range(needed))[:head[4]]
            if len(payload) < head[4]:
                pic.issues.append('truncated compressed frame')
            elif payload[:8] != struct.pack('<IHH', head[7], head[8], head[9]):
                pic.issues.append('sector/BS header mismatch')
            else:
                try:
                    pic.audit = audit_picture(payload, width, height)
                    pic.data = payload
                    pic.issues.extend(pic.audit['issues'])
                    info['bitstream'] = pic.audit
                except Damaged as exc:
                    pic.issues.append(str(exc))
        if len(pic.parts) != head[2]:
            pic.issues.append('incomplete sector allocation (may affect only padding)')
        info['decoded'] = pic.data is not None
        for issue in pic.issues:
            warnings.append(f'frame {pic.number}: {issue}')
        frame_audits.append(info)

    if not any(pic.data for pic in pictures):
        raise FormatError('recognized STR stream, but no complete decodable video frame survives')
    # Limit a malicious frame-number jump; no dense allocation precedes this.
    if pictures[-1].number - pictures[0].number + 1 > max(1000, len(pictures) * 10):
        raise FormatError('frame-number gaps exceed the recovery resource limit')
    byte_keys = ('str_header_bytes', 'bs_bytes', 'sector_padding_bytes',
                 'zero_sector_bytes', 'xa_parameter_bytes', 'xa_sample_bytes', 'damaged_bytes')
    accounted = sum(counts[k] for k in byte_keys)
    if accounted != len(raw):
        raise AssertionError('internal byte accounting error')
    audit = dict(input_bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
                 accounted_bytes=accounted, all_bytes_classified=not counts['damaged_bytes'],
                 counts=dict(counts), width=width, height=height,
                 sector_padding_histogram={f'{k:02x}': v for k, v in sorted(padding_histogram.items())},
                 sectors=spans, frames=frame_audits)
    return Stream(width, height, pictures, audio, audit, warnings)


def black_picture(width, height):
    blocks = ((width + 15) // 16) * ((height + 15) // 16)
    bits = ('000000000010' * 2 + '100000000010' * 4) * blocks + '0111111111'
    bits += '0' * (-len(bits) % 32)
    data = b''.join(struct.pack('<H', int(bits[i:i + 16], 2))
                    for i in range(0, len(bits), 16))
    return struct.pack('<4H', ((blocks * 12 + 63) // 64) * 32, 0x3800, 1, 2) + data


def timeline_pictures(stream):
    previous = black_picture(stream.width, stream.height)
    by_number = {pic.number: pic for pic in stream.pictures}
    result = []
    concealed = []
    for number in range(stream.pictures[0].number, stream.pictures[-1].number + 1):
        pic = by_number.get(number)
        if pic is not None and pic.data is not None:
            previous = pic.data
        else:
            concealed.append(number)
        result.append(previous)
    return result, concealed


def decode_xa_prefix(data, channels):
    """Decode 16 groups; reset predictor because preceding groups may be lost."""
    filters = ((0, 0), (60, 0), (115, -52), (98, -55))
    history = [[0, 0] for _ in range(channels)]
    samples = array.array('h')
    for offset in range(0, SECTOR, 128):
        group = data[offset:offset + 128]
        units = []
        for unit in range(8):
            parameter = group[unit if unit < 4 else unit + 4]
            shift = parameter & 15
            a, b = filters[parameter >> 4]
            hist = history[unit % channels]
            output = []
            for n in range(28):
                nibble = (group[16 + 4 * n + unit // 2] >> ((unit & 1) * 4)) & 15
                signed = nibble - 16 if nibble >= 8 else nibble
                value = ((signed << 12) >> shift) + ((a * hist[0] + b * hist[1] + 32) >> 6)
                value = max(-32768, min(32767, value))
                hist[1], hist[0] = hist[0], value
                output.append(value)
            units.append(output)
        if channels == 2:
            for unit in range(0, 8, 2):
                for left, right in zip(units[unit], units[unit + 1]):
                    samples.extend((left, right))
        else:
            for unit in units:
                samples.extend(unit)
    if sys.byteorder != 'little':
        samples.byteswap()
    return samples.tobytes()


def make_audio(stream, frames, options):
    if not stream.audio:
        return b'', None
    rate, channels = options.xa_rate, options.xa_channels
    align = channels * 2
    first_sector = stream.audio[0][0]
    full_samples = 18 * 224 // channels
    surviving_samples = 16 * 224 // channels
    pcm = bytearray()
    last_start = -1
    placements = []
    for sector, data in stream.audio:
        # Timestamp is a caller-supplied physical-clock policy, not file metadata.
        start = round((Fraction(sector - first_sector, 1) / options.sector_rate
                       + options.audio_offset) * rate)
        end_surviving = start + surviving_samples
        end_packet = start + full_samples
        if start < last_start + full_samples and last_start >= 0:
            raise FormatError('XA packets overlap under the selected audio/sector clock; '
                              'supply --xa-rate, --xa-channels and --sector-rate')
        last_start = start
        if end_packet <= 0:
            continue
        if len(pcm) < end_packet * align:
            pcm.extend(b'\0' * (end_packet * align - len(pcm)))
        decoded = decode_xa_prefix(data, channels)
        if end_surviving > 0:
            clipped = max(0, -start) * align
            pcm[max(0, start) * align:end_surviving * align] = decoded[clipped:]
        placements.append(dict(sector=sector, start_sample=start,
                               decoded_sample_frames=surviving_samples,
                               missing_sample_frames=full_samples - surviving_samples))
    video_samples = math.ceil(Fraction(len(frames), 1) / options.fps * rate)
    if len(pcm) < video_samples * align:
        pcm.extend(b'\0' * (video_samples * align - len(pcm)))
    info = dict(sample_rate=rate, channels=channels, bits_per_code=4,
                sample_frames=len(pcm) // align, sector_rate=str(options.sector_rate),
                first_audio_offset_seconds=str(options.audio_offset),
                missing_groups_per_packet=2, predictor_recovery='reset each surviving prefix',
                gap_recovery='silence', placements=placements,
                metadata_source='explicit command-line settings or documented defaults')
    return bytes(pcm), info


def chunk(tag, data):
    return tag + struct.pack('<I', len(data)) + data + b'\0' * (len(data) & 1)


def list_chunk(tag, data):
    return chunk(b'LIST', tag + data)


def avi_stream_header(kind, handler, scale, rate, length, buffer_size, sample_size, width=0, height=0):
    return struct.pack('<4s4sIHHIIIIIIIIhhhh', kind, handler, 0, 0, 0, 0,
                       scale, rate, 0, length, buffer_size, 0xffffffff, sample_size,
                       0, 0, width, height)


def packet_avi(frames, width, height, fps, pcm, audio_rate, channels):
    """AVI with native MDEC packets and decoded PCM, built entirely in memory."""
    align = channels * 2
    has_audio = bool(pcm)
    vstrh = avi_stream_header(b'vids', b'MDEC', fps.denominator, fps.numerator,
                              len(frames), max(map(len, frames)), 0, width, height)
    vstrf = struct.pack('<IiiHH4sIiiII', 40, width, height, 1, 24, b'MDEC',
                       width * height * 3, 0, 0, 0, 0)
    streams = list_chunk(b'strl', chunk(b'strh', vstrh) + chunk(b'strf', vstrf))
    if has_audio:
        astrh = avi_stream_header(b'auds', b'\0' * 4, align, audio_rate * align,
                                  len(pcm) // align, 8192, align)
        astrf = struct.pack('<HHIIHH', 1, channels, audio_rate, audio_rate * align, align, 16)
        streams += list_chunk(b'strl', chunk(b'strh', astrh) + chunk(b'strf', astrf))
    main = struct.pack('<14I', round(1000000 / fps), 0, 0, 0x110, len(frames),
                       0, 1 + has_audio, 0, width, height, 0, 0, 0, 0)
    hdrl = list_chunk(b'hdrl', chunk(b'avih', main) + streams)
    movi = bytearray()
    index = bytearray()

    def add(tag, data):
        index.extend(struct.pack('<4sIII', tag, 0x10, len(movi) + 4, len(data)))
        movi.extend(chunk(tag, data))

    audio_pos = 0
    for n, frame in enumerate(frames):
        add(b'00dc', frame)
        if has_audio:
            end = min(len(pcm), round(Fraction(n + 1, 1) / fps * audio_rate) * align)
            if end > audio_pos:
                add(b'01wb', pcm[audio_pos:end])
                audio_pos = end
    # Preserve audio after the last picture instead of cutting it off.
    while audio_pos < len(pcm):
        end = min(audio_pos + 8192 * align, len(pcm))
        add(b'01wb', pcm[audio_pos:end])
        audio_pos = end
    body = b'AVI ' + hdrl + list_chunk(b'movi', movi) + chunk(b'idx1', index)
    if len(body) >= 0xffffffff:
        raise FormatError('in-memory AVI exceeds the 4 GiB RIFF limit')
    return chunk(b'RIFF', body)


def finish_pipe_avi(data):
    """Finalize the RIFF lengths and index that a nonseekable ffmpeg pipe lacks."""
    if data[:4] != b'RIFF' or data[8:12] != b'AVI ':
        raise FormatError('ffmpeg did not return an AVI')
    out = bytearray(data)
    stream_headers = []
    main_offset = None
    movi = None

    def headers(start, end):
        nonlocal main_offset
        p = start
        while p + 8 <= end:
            tag, size = struct.unpack_from('<4sI', out, p)
            if p + 8 + size > end:
                raise FormatError('invalid ffmpeg AVI header length')
            if tag == b'avih':
                main_offset = p + 8
            elif tag == b'strh':
                stream_headers.append(p + 8)
            elif tag == b'LIST':
                headers(p + 12, p + 8 + size)
            p += 8 + size + (size & 1)

    p = 12
    while p + 12 <= len(out):
        tag, size = struct.unpack_from('<4sI', out, p)
        if tag == b'LIST' and out[p + 8:p + 12] == b'movi':
            movi = p
            break
        if p + 8 + size > len(out):
            raise FormatError('truncated ffmpeg AVI header')
        if tag == b'LIST' and out[p + 8:p + 12] == b'hdrl':
            headers(p + 12, p + 8 + size)
        p += 8 + size + (size & 1)
    if movi is None or main_offset is None or not stream_headers:
        raise FormatError('ffmpeg AVI lacks headers or movie data')
    p = movi + 12
    index = bytearray()
    lengths = [0] * len(stream_headers)
    while p + 8 <= len(out):
        tag, size = struct.unpack_from('<4sI', out, p)
        end = p + 8 + size + (size & 1)
        if end > len(out):
            raise FormatError('truncated ffmpeg AVI packet')
        if tag[2:] in (b'dc', b'db', b'wb') and tag[:2].isdigit():
            stream = int(tag[:2])
            if stream >= len(lengths):
                raise FormatError('invalid ffmpeg AVI stream number')
            sample_size = struct.unpack_from('<I', out, stream_headers[stream] + 44)[0]
            lengths[stream] += size // sample_size if sample_size else 1
            index.extend(struct.pack('<4sIII', tag, 0x10, p - movi - 8, size))
        elif tag != b'JUNK':
            raise FormatError(f'unexpected ffmpeg AVI movie chunk {tag!r}')
        p = end
    if p != len(out):
        raise FormatError('unaccounted ffmpeg AVI tail')
    struct.pack_into('<I', out, movi + 4, len(out) - movi - 8)
    struct.pack_into('<I', out, main_offset + 12, 0x110)
    struct.pack_into('<I', out, main_offset + 16, lengths[0])
    for offset, length in zip(stream_headers, lengths):
        struct.pack_into('<I', out, offset + 32, length)
    out.extend(chunk(b'idx1', index))
    if len(out) - 8 >= 0xffffffff:
        raise FormatError('encoded AVI exceeds the 4 GiB RIFF limit')
    struct.pack_into('<I', out, 4, len(out) - 8)
    return out


def convert(input_path, output_path, options):
    if input_path.resolve() == output_path.resolve():
        raise FormatError('input and output paths must differ')
    if output_path.exists():
        raise FormatError('output already exists; choose a new filename')
    if options.verbose and Path(str(output_path) + '.audit.json').exists():
        raise FormatError('verbose audit output already exists; choose a new filename')
    if not output_path.parent.is_dir():
        raise FormatError('output directory does not exist')
    stream = parse_stream(input_path)
    frames, concealed = timeline_pictures(stream)
    pcm, audio_info = make_audio(stream, frames, options)
    ffmpeg = shutil.which(options.ffmpeg)
    if not ffmpeg:
        raise FormatError('ffmpeg executable was not found')
    if stream.audio:
        stream.warnings.append('XA subheaders and 2 of 18 audio groups per packet are absent; '
                               'audio uses explicit/default settings and silence for lost groups')
    stream.warnings.append(f'no stored frame rate: using {options.fps} fps')
    if concealed:
        stream.warnings.append(f'{len(concealed)} damaged/missing frames concealed by hold/black')
    for warning in stream.warnings[:20]:
        print(f'warning: {warning}', file=sys.stderr)
    if len(stream.warnings) > 20:
        print(f'warning: {len(stream.warnings) - 20} more issues (use -verbose)', file=sys.stderr)
    source_avi = packet_avi(frames, stream.width, stream.height, options.fps,
                            pcm, options.xa_rate, options.xa_channels)
    command = [ffmpeg, '-hide_banner', '-loglevel', 'error', '-nostdin', '-xerror',
               '-f', 'avi', '-c:v', 'mdec', '-i', 'pipe:0', '-map', '0:v:0', '-map', '0:a?',
               '-c:v', 'ffv1', '-level', '3', '-g', '1', '-slicecrc', '1',
               '-vf', 'scale=in_range=full:out_range=full:in_color_matrix=bt601,format=bgr0',
               '-pix_fmt', 'bgr0', '-threads', '2',
               '-c:a', 'pcm_s16le', '-fps_mode', 'passthrough', '-f', 'avi', 'pipe:1']
    result = subprocess.run(command, input=source_avi, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, check=False)
    if result.returncode:
        raise FormatError('ffmpeg failed: ' + result.stderr.decode('utf-8', 'replace').strip())
    final_avi = finish_pipe_avi(result.stdout)
    # Only now create the final output. No temporary media, indexes, metadata,
    # or Python cache files are written by the default command.
    created = False
    try:
        with output_path.open('xb') as target:
            created = True
            target.write(final_avi)
            target.flush()
            os.fchmod(target.fileno(), os.fstat(target.fileno()).st_mode | 0o440)
    except BaseException:
        if created:
            output_path.unlink(missing_ok=True)
        raise
    stream.audit.update(fps=str(options.fps), video_frames=len(frames),
                        concealed_frames=concealed, audio=audio_info,
                        warnings=stream.warnings, output_bytes=len(final_avi),
                        output_video_codec='FFV1 level 3', output_pixel_format='bgr0',
                        output_audio_codec='PCM signed 16-bit' if pcm else None)
    if options.verbose:
        audit_path = Path(str(output_path) + '.audit.json')
        with audit_path.open('x', encoding='utf-8') as target:
            json.dump(stream.audit, target, indent=2)
            target.write('\n')
            os.fchmod(target.fileno(), os.fstat(target.fileno()).st_mode | 0o440)
        print(f'{len(frames)} frames, {stream.width}x{stream.height}; '
              f'{stream.audit["accounted_bytes"]} input bytes accounted for; {audit_path}',
              file=sys.stderr)


def positive_fraction(value):
    try:
        result = Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise argparse.ArgumentTypeError('expected a positive number or fraction') from exc
    if result <= 0 or result > 1000000:
        raise argparse.ArgumentTypeError('must be positive and at most 1000000')
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('inputFile', type=Path)
    parser.add_argument('outputFile', type=Path)
    parser.add_argument('-verbose', '--verbose', action='store_true',
                        help='also write outputFile.audit.json with byte/bit accounting')
    parser.add_argument('--fps', type=positive_fraction, default=Fraction(15),
                        help='external frame rate; default 15, not inferred from bytes')
    parser.add_argument('--xa-rate', type=int, choices=(18900, 37800), default=37800,
                        help='missing XA sample-rate setting (default 37800)')
    parser.add_argument('--xa-channels', type=int, choices=(1, 2), default=2,
                        help='missing XA channel-mode setting (default stereo)')
    parser.add_argument('--sector-rate', type=positive_fraction, default=Fraction(150),
                        help='external physical-sector clock for XA placement (default 150/s)')
    parser.add_argument('--audio-offset', type=Fraction, default=Fraction(0),
                        help='seconds from first video frame to first XA packet (default 0)')
    parser.add_argument('--ffmpeg', default='ffmpeg', help='ffmpeg executable name or path')
    options = parser.parse_args(argv)
    try:
        convert(options.inputFile, options.outputFile, options)
    except (FormatError, OSError, ValueError, MemoryError) as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print('error: interrupted', file=sys.stderr)
        return 130
    return 0


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
# Vibe coded by Codex
"""KSV1 -> AVI (original MPEG-4 video, decoded 16-bit PCM audio).

Uses only Python's standard library. See kheopsStudioVideo.txt for the format,
including the distinction between established layout and unresolved semantics.
"""

import argparse
from array import array
from collections import Counter
from dataclasses import dataclass, field
from fractions import Fraction
import json
import mmap
import os
from pathlib import Path
import struct
import sys

sys.dont_write_bytecode = True
U32 = struct.Struct('<I')
CHUNK = struct.Struct('<I2sBB')
APC = struct.Struct('<12sIIiiI')


class FormatError(ValueError):
    """Unrecognized, unsupported, or unrecoverable input; no output is created."""


class Bits:
    def __init__(self, data):
        self.data = data
        self.pos = 0

    def get(self, count):
        if self.pos + count > 8 * len(self.data):
            raise FormatError('Truncated MPEG-4 header')
        result = 0
        for _ in range(count):
            result = (result << 1) | ((self.data[self.pos >> 3] >> (7 - (self.pos & 7))) & 1)
            self.pos += 1
        return result

    def marker(self):
        if self.get(1) != 1:
            raise FormatError('Invalid MPEG-4 marker bit')


def start_codes(data):
    """MPEG-4 byte-aligned start-code syntax, not a container resync search."""
    offset = 0
    while True:
        offset = data.find(b'\x00\x00\x01', offset)
        if offset < 0 or offset + 3 >= len(data):
            return
        yield offset, data[offset + 3]
        offset += 4


def parse_vol(data):
    """Read the standard rectangular VOL fields needed for lossless remuxing."""
    bits = Bits(data)
    bits.get(1)  # random_accessible_vol
    object_type = bits.get(8)
    version = 1
    if bits.get(1):
        version = bits.get(4)
        bits.get(3)  # video_object_layer_priority
    aspect = bits.get(4)
    aspect_ratios = {1: (1, 1), 2: (12, 11), 3: (10, 11), 4: (16, 11), 5: (40, 33)}
    sar = (bits.get(8), bits.get(8)) if aspect == 15 else aspect_ratios.get(aspect)
    if not sar or not all(sar):
        raise FormatError('Unsupported MPEG-4 aspect ratio')
    if bits.get(1):
        bits.get(2)  # chroma_format
        bits.get(1)  # low_delay
        if bits.get(1):  # vbv_parameters
            bits.get(15); bits.marker()
            bits.get(15); bits.marker()
            bits.get(15); bits.marker()
            bits.get(3); bits.get(11); bits.marker()
            bits.get(15); bits.marker()
    shape = bits.get(2)
    if shape == 3 and version != 1:
        bits.get(4)
    if shape != 0:
        raise FormatError('Only rectangular MPEG-4 video objects can be written to this AVI profile')
    bits.marker()
    resolution = bits.get(16)
    if not resolution:
        raise FormatError('Zero MPEG-4 time increment resolution')
    bits.marker()
    fixed = bits.get(1)
    increment = bits.get(max(1, (resolution - 1).bit_length())) if fixed else None
    bits.marker()
    width = bits.get(13)
    bits.marker()
    height = bits.get(13)
    bits.marker()
    if not width or not height:
        raise FormatError('Zero MPEG-4 dimensions')
    return dict(width=width, height=height, resolution=resolution, increment=increment,
                sar=sar, object_type=object_type, version=version)


@dataclass
class VideoPacket:
    offset: int
    size: int
    key: bool


@dataclass
class AudioPart:
    offset: int
    size: int


@dataclass
class Movie:
    width: int
    height: int
    rate: Fraction
    header: dict
    packets: list = field(default_factory=list)
    audio: list = field(default_factory=list)
    audio_header: dict = field(default_factory=dict)
    audio_samples: int = 0
    warnings: list = field(default_factory=list)
    coverage: Counter = field(default_factory=Counter)
    spans: list = field(default_factory=list)
    vol: dict = field(default_factory=dict)
    blocks: int = 0

    def warn(self, message):
        if message not in self.warnings:
            self.warnings.append(message)

    def account(self, start, end, kind, detailed):
        if end > start:
            self.coverage[kind] += end - start
            if detailed:
                self.spans.append(dict(offset=start, length=end-start, kind=kind))

    def summary(self):
        return dict(header=self.header, video=dict(width=self.width, height=self.height,
                    frame_rate=str(self.rate), frames=len(self.packets),
                    seconds=float(len(self.packets) / self.rate), vol=self.vol),
                    audio=dict(self.audio_header, output_sample_frames=self.audio_samples),
                    blocks=self.blocks, byte_coverage=dict(self.coverage),
                    warnings=self.warnings, byte_ranges=self.spans)


def parse(data, detailed=False):
    """Walk declared container bounds. Never guess offsets or scan for chunks."""
    length = len(data)
    if length < 4 or data[:4] != b'KSV1':
        raise FormatError('Not Kheops Studio Video: expected KSV1 signature')
    if length < 64:
        raise FormatError('KSV1 header is truncated; no media can be recovered')
    mode, descriptor, depth, width, height, declared_size, declared_frames, revision, ticks, legacy, buffer_size = \
        struct.unpack_from('<HBBHHII4sHHI', data, 4)
    if mode not in (0, 0x100):
        raise FormatError(f'Unsupported KSV1 header mode 0x{mode:04x}')
    if descriptor not in (0, 0xb0):
        raise FormatError(f'Unsupported KSV1 audio descriptor 0x{descriptor:02x}')
    if revision not in (b'\0\0\0\0', b'V200') or depth != 16 or legacy != 2:
        raise FormatError('Unsupported KSV1 header profile (revision, pixel depth, or legacy field)')
    header = dict(mode=mode, audio_descriptor=descriptor, pixel_depth=depth,
                  width=width, height=height, declared_size=declared_size,
                  declared_frames=declared_frames, revision=revision.hex(),
                  frame_ticks=ticks, legacy_field=legacy, frame_buffer_size=buffer_size,
                  copyright=data[32:64].decode('latin-1'))
    movie = Movie(width, height, Fraction(200, ticks) if ticks else Fraction(0), header)
    movie.account(0, 64, 'file_header', detailed)
    if data[32:64] != b'Copyright Kheops Studio         ':
        movie.warn('Noncanonical copyright text; it has no media decoding role')
    if buffer_size != width * height * 2:
        movie.warn('Frame-buffer size differs from width * height * 2')
    offset = 64
    terminator = False
    audio_started = False
    outer_padding = 0
    last_vop_time = None
    vop_seconds = 0
    while offset < length:
        if length - offset < 4:
            movie.account(offset, length, 'truncated_block_header', detailed)
            movie.warn(f'Truncated block header at 0x{offset:x}; salvaged preceding media')
            break
        size = U32.unpack_from(data, offset)[0]
        if size == 0:
            movie.account(offset, offset + 4, 'end_marker', detailed)
            offset += 4
            terminator = True
            if offset < length:
                movie.account(offset, length, 'unexpected_trailing_data', detailed)
                movie.warn(f'{length-offset} unexpected bytes follow the end marker')
            break
        movie.account(offset, offset + 4, 'block_header', detailed)
        if size < 4:
            movie.account(offset + 4, length, 'unrecoverable_tail', detailed)
            movie.warn(f'Invalid block size at 0x{offset:x}; cannot locate subsequent blocks without guessing')
            break
        end = min(offset + size, length)
        if offset + size > length:
            movie.warn(f'Truncated final block at 0x{offset:x}; recovering bounded payloads')
        cursor = offset + 4
        video_before = len(movie.packets)
        movie.blocks += 1
        while cursor < end:
            if end - cursor < 8:
                movie.account(cursor, end, 'truncated_chunk_header', detailed)
                movie.warn(f'Truncated chunk header at 0x{cursor:x}')
                break
            chunk_size, tag, flags, extra = CHUNK.unpack_from(data, cursor)
            movie.account(cursor, cursor + 8, 'chunk_header', detailed)
            if chunk_size < 8:
                movie.account(cursor + 8, end, 'unrecoverable_block_tail', detailed)
                movie.warn(f'Invalid chunk size at 0x{cursor:x}; skipped remainder of its block')
                break
            if tag not in (b'XV', b'AA'):
                raise FormatError(f'Unsupported KSV1 chunk {tag!r} at 0x{cursor:x}; no output written')
            if flags != 0 or extra > 3:
                raise FormatError(f'Unsupported {tag.decode()} flags {flags:02x} {extra:02x} at 0x{cursor:x}')
            declared_end = cursor + chunk_size
            payload_end = min(declared_end, end)
            start = cursor + 8
            truncated = declared_end > end
            if truncated:
                movie.warn(f'Truncated {tag.decode()} chunk at 0x{cursor:x}')
            if tag == b'XV':
                payload = data[start:payload_end]
                vops = []
                for pos, code in start_codes(payload):
                    if 0x20 <= code <= 0x2f:
                        try:
                            vol = parse_vol(payload[pos+4:])
                        except FormatError as exc:
                            movie.warn(f'Invalid VOL at 0x{start+pos:x}: {exc}')
                            continue
                        if movie.vol and (vol['width'], vol['height'], vol['sar']) != \
                                (movie.vol['width'], movie.vol['height'], movie.vol['sar']):
                            raise FormatError('Changing MPEG-4 dimensions/aspect ratio is unsupported in one AVI stream')
                        movie.vol = vol
                    elif code == 0xb6:
                        vops.append(pos)
                if len(vops) > 1:
                    raise FormatError('Multiple MPEG-4 VOPs in one XV chunk are unsupported')
                if vops and vops[0] + 4 < len(payload):
                    pos = vops[0]
                    key = (payload[pos+4] >> 6) == 0
                    movie.packets.append(VideoPacket(start, len(payload), key))
                    if movie.vol:
                        try:
                            bits = Bits(payload[pos+4:])
                            coding = bits.get(2)
                            if coding == 2:
                                raise FormatError('B-VOP reordering is outside the supported KSV1 profile')
                            seconds = 0
                            while bits.get(1):
                                seconds += 1
                            vop_seconds += seconds
                            bits.marker()
                            resolution = movie.vol['resolution']
                            clock = bits.get(max(1, (resolution-1).bit_length()))
                            bits.marker()
                            stamp = vop_seconds * resolution + clock
                            if last_vop_time is not None and stamp <= last_vop_time:
                                movie.warn('MPEG-4 internal timestamps reset; AVI uses KSV frame order and frame ticks')
                            last_vop_time = stamp
                        except FormatError as exc:
                            if 'B-VOP' in str(exc):
                                raise
                            movie.warn(f'Malformed VOP timing at 0x{start+pos:x}; using KSV frame timing')
                else:
                    movie.warn(f'No complete MPEG-4 VOP header in XV at 0x{cursor:x}; repeating previous picture')
                # Preserve exactly the declared MPEG-4 payload, including any
                # encoder/muxer stuffing already incorporated into its size.
                movie.account(start, payload_end, 'mpeg4_payload_with_included_stuffing', detailed)
            else:
                if not audio_started:
                    if payload_end - start < 32:
                        movie.account(start, payload_end, 'truncated_apc_header', detailed)
                        movie.warn('APC header is truncated; cannot recover this audio track')
                        cursor = end
                        break
                    magic, samples, sample_rate, left, right, stereo = APC.unpack_from(data, start)
                    if magic != b'CRYO_APC1.20':
                        raise FormatError('Unsupported audio payload: expected CRYO_APC1.20')
                    if not sample_rate or stereo not in (0, 1):
                        raise FormatError('Invalid APC sample rate or channel flag')
                    movie.audio_header = dict(declared_sample_frames=samples, sample_rate=sample_rate,
                                              channels=stereo+1, predictor_left=left, predictor_right=right)
                    movie.account(start, start + 32, 'apc_header', detailed)
                    start += 32
                    audio_started = True
                # AA's last flag byte counts padding bytes, unlike XV's byte.
                valid_end = payload_end if truncated else max(start, payload_end - extra)
                if not truncated and extra > payload_end - start:
                    movie.warn(f'Audio padding exceeds payload at 0x{cursor:x}')
                movie.audio.append(AudioPart(start, valid_end-start))
                movie.account(start, valid_end, 'apc_adpcm_and_final_buffer_fill', detailed)
                movie.account(valid_end, payload_end, 'audio_alignment', detailed)
            aligned_end = min(cursor + ((chunk_size + 3) & ~3), end)
            if aligned_end > payload_end:
                pad = data[payload_end:aligned_end]
                outer_padding += len(pad)
                movie.account(payload_end, aligned_end, 'external_alignment', detailed)
                if tag == b'XV':
                    expected = bytes([chunk_size & 3]) + bytes(max(0, 3-(chunk_size & 3)))
                    if pad != expected:
                        movie.warn(f'Noncanonical external video alignment at 0x{payload_end:x}')
            cursor = aligned_end
        if len(movie.packets) == video_before:
            movie.packets.append(VideoPacket(0, 0, False))
        offset = end
    if not movie.vol or not any(p.size and p.key for p in movie.packets):
        raise FormatError('KSV1 contains no recoverable MPEG-4 VOL and intra picture')
    if not terminator:
        movie.warn('Missing four-byte end marker; recovered all bounded media')
    if (width, height) != (movie.vol['width'], movie.vol['height']):
        movie.warn('Container dimensions disagree with MPEG-4 VOL; using VOL dimensions')
        movie.width, movie.height = movie.vol['width'], movie.vol['height']
    if not movie.rate:
        if not movie.vol.get('increment'):
            raise FormatError('Neither KSV frame ticks nor fixed VOL timing is usable')
        movie.rate = Fraction(movie.vol['resolution'], movie.vol['increment'])
        movie.warn('Zero KSV frame ticks; recovered timing from fixed MPEG-4 VOL rate')
    if len(movie.packets) != declared_frames:
        movie.warn(f'Header declares {declared_frames} pictures; recovered {len(movie.packets)} frame slots')
    expected_size = length if mode == 0x100 else length - outer_padding
    if declared_size != expected_size:
        movie.warn(f'Declared file size {declared_size} differs from mode-accounted size {expected_size}')
    if bool(movie.audio_header) != bool(descriptor):
        movie.warn('Audio descriptor disagrees with actual AA chunks; using the chunks')
    if movie.audio_header:
        available = sum(part.size for part in movie.audio) * 2 // movie.audio_header['channels']
        declared = movie.audio_header['declared_sample_frames']
        movie.audio_samples = min(declared, available)
        movie.audio_header['available_sample_frames'] = available
        movie.audio_header['final_buffer_fill_sample_frames'] = max(0, available-declared)
        if available < declared:
            movie.warn(f'APC declares {declared} sample frames but only {available} are present; keeping available audio')
    assert sum(movie.coverage.values()) == length, 'Internal byte-accounting error'
    return movie


# IMA APC uses the multiplication form of the IMA difference, high nibble first.
STEP = (7,8,9,10,11,12,13,14,16,17,19,21,23,25,28,31,34,37,41,45,50,55,60,
        66,73,80,88,97,107,118,130,143,157,173,190,209,230,253,279,307,337,371,
        408,449,494,544,598,658,724,796,876,963,1060,1166,1282,1411,1552,1707,
        1878,2066,2272,2499,2749,3024,3327,3660,4026,4428,4871,5358,5894,6484,
        7132,7845,8630,9493,10442,11487,12635,13899,15289,16818,18500,20350,
        22385,24623,27086,29794,32767)
INDEX = (-1,-1,-1,-1,2,4,6,8)
DIFF = tuple(tuple((((2*(n&7)+1)*s) >> 3) * (-1 if n&8 else 1) for n in range(16)) for s in STEP)
NEXT = tuple(tuple(max(0,min(88,i+INDEX[n&7])) for n in range(16)) for i in range(89))


def decode_audio(data, movie):
    """Yield little-endian PCM blocks, with continuous state across AA chunks."""
    info = movie.audio_header
    channels = info['channels']
    predictors = [info['predictor_left'], info['predictor_right']]
    indices = [0, 0]
    remaining = movie.audio_samples * channels
    for part in movie.audio:
        pcm = array('h')
        # Decode final buffer fill as well; only declared samples are emitted.
        for value in data[part.offset:part.offset+part.size]:
            for channel, nibble in ((0, value >> 4), (channels-1, value & 15)):
                index = indices[channel]
                predictor = predictors[channel] + DIFF[index][nibble]
                predictor = max(-32768, min(32767, predictor))
                indices[channel] = NEXT[index][nibble]
                predictors[channel] = predictor
                if remaining:
                    pcm.append(predictor)
                    remaining -= 1
        if sys.byteorder != 'little':
            pcm.byteswap()
        if pcm:
            yield pcm.tobytes()


def riff_chunk(tag, data):
    return tag + U32.pack(len(data)) + data + b'\0' * (len(data) & 1)


def riff_list(tag, data):
    return riff_chunk(b'LIST', tag + data)


class AVIWriter:
    """Seekable AVI with idx1 and OpenDML indices, including AVIX segmentation."""
    INDEX_CAPACITY = 256
    SEGMENT_LIMIT = 1024 * 1024 * 1024

    def __init__(self, file, movie, segment_limit=None):
        self.file = file
        self.movie = movie
        self.limit = segment_limit or self.SEGMENT_LIMIT
        self.streams = 2 if movie.audio_header and movie.audio_samples else 1
        self.super = [[] for _ in range(self.streams)]
        self.super_positions = []
        self.segment_number = 0
        self.global_frames = 0
        self.global_audio = 0
        self._start_segment(first=True)

    def _headers(self):
        movie = self.movie
        rate, scale = movie.rate.numerator, movie.rate.denominator
        max_video = max(p.size for p in movie.packets)
        avih = struct.pack('<14I', round(1_000_000 * scale/rate), 0, 0, 0x110,
                           len(movie.packets), 0, self.streams, max_video,
                           movie.width, movie.height, 0, 0, 0, 0)
        data = riff_chunk(b'avih', avih)
        for stream in range(self.streams):
            if stream == 0:
                # Generic MPEG-4 identification avoids falsely implying an old
                # Xvid encoder build and triggering decoder bug workarounds.
                sh = struct.pack('<4s4sIHH8I4h', b'vids', b'MP4V', 0, 0, 0, 0,
                                 scale, rate, 0, len(movie.packets), max_video, 0xffffffff, 0,
                                 0, 0, movie.width, movie.height)
                sf = struct.pack('<IiiHH4sIiiII', 40, movie.width, movie.height, 1, 24,
                                 b'MP4V', movie.width*movie.height*3, 0, 0, 0, 0)
                extra = b''
                sar = movie.vol['sar']
                if sar != (1, 1):
                    dar = Fraction(movie.width*sar[0], movie.height*sar[1])
                    if max(dar.numerator, dar.denominator) > 65535:
                        raise FormatError('Display aspect ratio does not fit AVI vprp')
                    aspect = (dar.numerator << 16) | dar.denominator
                    values = [0,0,round(float(movie.rate)),movie.width,movie.height,
                              aspect,movie.width,movie.height,1,
                              movie.height,movie.width,movie.height,movie.width,0,0,0,0]
                    extra = riff_chunk(b'vprp', struct.pack('<17I', *values))
            else:
                info = movie.audio_header
                block = info['channels']*2
                sh = struct.pack('<4s4sIHH8I4h', b'auds', b'\0'*4, 0, 0, 0, 0,
                                 block, info['sample_rate']*block, 0, movie.audio_samples,
                                 65536, 0xffffffff, block, 0, 0, 0, 0)
                sf = struct.pack('<HHIIHH', 1, info['channels'], info['sample_rate'],
                                 info['sample_rate']*block, block, 16)
                extra = b''
            chunk_id = b'00dc' if stream == 0 else b'01wb'
            index = struct.pack('<HBBI4s3I', 4, 0, 0, 0, chunk_id, 0, 0, 0) + bytes(16*self.INDEX_CAPACITY)
            stream_data = riff_chunk(b'strh', sh) + riff_chunk(b'strf', sf) + extra
            # Absolute location of the superindex payload within initial hdrl.
            self.super_positions.append(12 + 12 + len(data) + 12 + len(stream_data) + 8)
            data += riff_list(b'strl', stream_data + riff_chunk(b'indx', index))
        data += riff_list(b'odml', riff_chunk(b'dmlh', U32.pack(len(movie.packets)) + bytes(244)))
        return riff_list(b'hdrl', data)

    def _start_segment(self, first=False):
        self.riff_start = self.file.tell()
        self.file.write(b'RIFF\0\0\0\0' + (b'AVI ' if first else b'AVIX'))
        if first:
            self.file.write(self._headers())
        self.movi_start = self.file.tell()
        self.file.write(b'LIST\0\0\0\0movi')
        self.entries = [[] for _ in range(self.streams)]
        self.legacy = []
        self.durations = [0]*self.streams

    def _patch32(self, offset, value):
        end = self.file.tell()
        self.file.seek(offset)
        self.file.write(U32.pack(value))
        self.file.seek(end)

    def _finish_segment(self):
        self._patch32(self.movi_start+4, self.file.tell()-self.movi_start-8)
        for stream, entries in enumerate(self.entries):
            if not entries:
                continue
            chunk_id = b'00dc' if stream == 0 else b'01wb'
            base = self.movi_start+8
            payload = struct.pack('<HBBI4sQI', 2, 0, 1, len(entries), chunk_id, base, 0)
            payload += b''.join(struct.pack('<II', off-base, size) for off, size in entries)
            index_offset = self.file.tell()
            index_chunk = riff_chunk(b'ix00' if stream == 0 else b'ix01', payload)
            self.file.write(index_chunk)
            self.super[stream].append((index_offset, len(index_chunk), self.durations[stream]))
            if len(self.super[stream]) > self.INDEX_CAPACITY:
                raise FormatError('AVI exceeds the supported 256 OpenDML segments')
        if self.segment_number == 0:
            self.file.write(riff_chunk(b'idx1', b''.join(self.legacy)))
        self._patch32(self.riff_start+4, self.file.tell()-self.riff_start-8)

    def write(self, stream, payload, key=True):
        size = len(payload)
        if size >= 0x80000000:
            raise FormatError('An AVI packet must be smaller than 2 GiB')
        pending_index_size = sum(len(e) for e in self.entries)*24 + 256
        if self.file.tell()-self.riff_start+size+8+pending_index_size > self.limit and any(self.entries):
            self._finish_segment()
            self.segment_number += 1
            self._start_segment()
        position = self.file.tell()
        tag = b'00dc' if stream == 0 else b'01wb'
        self.file.write(tag + U32.pack(size))
        self.file.write(payload)
        if size & 1:
            self.file.write(b'\0')
        self.entries[stream].append((position+8, size | (0 if key else 0x80000000)))
        if self.segment_number == 0:
            self.legacy.append(struct.pack('<4sIII', tag, 0x10 if key else 0,
                                           position-(self.movi_start+8), size))
        duration = 1 if stream == 0 else size//(self.movie.audio_header['channels']*2)
        self.durations[stream] += duration
        if stream == 0:
            self.global_frames += 1
        else:
            self.global_audio += duration

    def close(self):
        self._finish_segment()
        end = self.file.tell()
        for position, entries in zip(self.super_positions, self.super):
            self.file.seek(position+4)
            self.file.write(U32.pack(len(entries)))
            self.file.seek(position+24)
            for entry in entries:
                self.file.write(struct.pack('<QII', *entry))
        self.file.seek(end)
        assert self.global_frames == len(self.movie.packets)
        if self.streams == 2:
            assert self.global_audio == self.movie.audio_samples


def write_movie(data, movie, output, segment_limit=None):
    """Re-interleave continuous audio by presentation time, removing prebuffering."""
    avi = AVIWriter(output, movie, segment_limit)
    audio = iter(decode_audio(data, movie)) if avi.streams == 2 else iter(())
    pending = b''
    pending_at = 0
    emitted = 0
    block = movie.audio_header.get('channels', 0)*2
    sample_rate = movie.audio_header.get('sample_rate', 0)

    def audio_through(target):
        nonlocal pending, pending_at, emitted
        target = min(target, movie.audio_samples)
        while emitted < target:
            if pending_at == len(pending):
                pending = next(audio, b'')
                pending_at = 0
                if not pending:
                    raise FormatError('Audio decoder produced fewer samples than expected')
            take = min((target-emitted)*block, len(pending)-pending_at, 262144)
            avi.write(1, pending[pending_at:pending_at+take])
            pending_at += take
            emitted += take//block

    for index, packet in enumerate(movie.packets):
        avi.write(0, data[packet.offset:packet.offset+packet.size], packet.key)
        if avi.streams == 2:
            target = (index+1)*sample_rate*movie.rate.denominator//movie.rate.numerator
            audio_through(target)
    if avi.streams == 2:
        audio_through(movie.audio_samples)
        # Exhaust the decoder so every final-fill nibble is accounted for too.
        for _ in audio:
            pass
    avi.close()


def convert(input_file, output_file, verbose=False):
    source, destination = Path(input_file), Path(output_file)
    if source.resolve() == destination.resolve():
        raise FormatError('Input and output must be different files')
    if destination.exists():
        raise FormatError(f'Output already exists: {destination}; choose a new path or remove it explicitly')
    with source.open('rb') as input_stream:
        if os.fstat(input_stream.fileno()).st_size < 4:
            raise FormatError('Not Kheops Studio Video: file is shorter than its signature')
        with mmap.mmap(input_stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
            movie = parse(data, detailed=verbose)
            if len(movie.packets) > 0xffffffff or movie.audio_samples > 0xffffffff:
                raise FormatError('Stream duration exceeds AVI/OpenDML 32-bit stream length')
            created = False
            try:
                # No scratch files, elementary streams, or sidecars are created.
                with destination.open('xb') as output:
                    created = True
                    write_movie(data, movie, output)
                    output.flush()
                    os.fchmod(output.fileno(), os.fstat(output.fileno()).st_mode | 0o440)
            except BaseException:
                if created:
                    destination.unlink(missing_ok=True)
                raise
    for warning in movie.warnings:
        print('Warning: '+warning, file=sys.stderr)
    if verbose:
        audit = destination.with_name(destination.name+'.json')
        with audit.open('x', encoding='utf-8') as stream:
            json.dump(movie.summary(), stream, indent=2)
            stream.write('\n')
            os.fchmod(stream.fileno(), os.fstat(stream.fileno()).st_mode | 0o440)
        print(f'{len(movie.packets)} frames, {movie.rate} fps, {movie.audio_samples} audio sample frames; {audit}',
              file=sys.stderr)
    return movie


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('inputFile', help='KSV1 input file (extension is not used for recognition)')
    parser.add_argument('outputFile', help='new AVI output path; existing files are preserved')
    parser.add_argument('-verbose', '--verbose', action='store_true',
                        help='also write outputFile.json with byte ranges and diagnostics')
    args = parser.parse_args(argv)
    try:
        convert(args.inputFile, args.outputFile, args.verbose)
    except (FormatError, OSError, ValueError, struct.error) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

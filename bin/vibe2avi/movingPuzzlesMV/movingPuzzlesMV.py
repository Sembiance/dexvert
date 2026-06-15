#!/usr/bin/env python3
# Vibe coded by Codex
import os
import struct
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


class FormatError(Exception):
    pass


def u16(data, off):
    if off + 2 > len(data):
        raise FormatError("unexpected end of data")
    return struct.unpack_from("<H", data, off)[0]


def u32(data, off):
    if off + 4 > len(data):
        raise FormatError("unexpected end of data")
    return struct.unpack_from("<I", data, off)[0]


@dataclass
class Atom:
    tag: bytes
    payload: bytes
    start: int
    size: int


@dataclass
class Track:
    header: bytes
    atoms: dict


@dataclass
class ParsedMV:
    data: bytes
    header_size: int
    movie_header: bytes
    video: Track
    palette: Track
    width: int
    height: int
    stride: int
    fps: int
    frame_count: int
    codec: bytes
    palette_rgbs: list
    frame_palette_indices: list
    video_offsets: list
    video_sizes: list
    palette_offsets: list
    palette_sizes: list


class BitReaderMSB:
    def __init__(self, data):
        self.data = data
        self.byte_pos = 0
        self.bits = 0
        self.bit_count = 0
        self.total_bits = 0

    def read(self, count):
        while self.bit_count < count:
            if self.byte_pos >= len(self.data):
                raise FormatError("LZSS packet ended inside a token")
            self.bits = (self.bits << 8) | self.data[self.byte_pos]
            self.byte_pos += 1
            self.bit_count += 8
        self.bit_count -= count
        self.total_bits += count
        value = (self.bits >> self.bit_count) & ((1 << count) - 1)
        self.bits &= (1 << self.bit_count) - 1
        return value

    def used_bytes(self):
        return (self.total_bits + 7) // 8


def parse_atom_table(data):
    if len(data) < 4:
        raise FormatError("file is too small")
    header_size = u32(data, 0)
    if header_size < 4 or header_size > len(data):
        raise FormatError("invalid header size")
    pos = 4
    movie_header = None
    tracks = []
    current = None
    while pos < header_size:
        if pos + 8 > header_size:
            raise FormatError("truncated atom header")
        size = u32(data, pos)
        tag = data[pos + 4:pos + 8]
        if size < 8 or pos + size > header_size:
            raise FormatError(f"invalid atom size for {tag!r}")
        payload = data[pos + 8:pos + size]
        if tag == b"dhvm":
            if movie_header is not None:
                raise FormatError("duplicate movie header")
            movie_header = payload
        elif tag == b"dhrt":
            current = Track(payload, {})
            tracks.append(current)
        else:
            if current is None:
                raise FormatError(f"atom {tag!r} appears before a track header")
            if tag in current.atoms:
                raise FormatError(f"duplicate atom {tag!r} in track")
            current.atoms[tag] = payload
        pos += size
    if pos != header_size:
        raise FormatError("header atom table does not end on header boundary")
    if movie_header is None:
        raise FormatError("missing movie header")
    if len(tracks) != 2:
        raise FormatError("expected exactly video and palette tracks")
    return header_size, movie_header, tracks


def parse_sample_sizes(payload):
    if len(payload) < 12 or u32(payload, 0) != 0:
        raise FormatError("invalid sample-size table")
    count = u32(payload, 4)
    default_size = u32(payload, 8)
    if default_size == 0:
        expected = 12 + count * 4
        if len(payload) != expected:
            raise FormatError("variable sample-size table length mismatch")
        return [u32(payload, 12 + i * 4) for i in range(count)]
    if count == 0:
        return [default_size]
    if len(payload) != 12:
        raise FormatError("fixed sample-size table has trailing data")
    return [default_size] * count


def parse_sample_size_fields(payload):
    if len(payload) < 12 or u32(payload, 0) != 0:
        raise FormatError("invalid sample-size table")
    return u32(payload, 4), u32(payload, 8)


def parse_chunk_offsets(payload):
    if len(payload) < 8 or u32(payload, 0) != 0:
        raise FormatError("invalid chunk-offset table")
    count = u32(payload, 4)
    if len(payload) != 8 + count * 4:
        raise FormatError("chunk-offset table length mismatch")
    return [u32(payload, 8 + i * 4) for i in range(count)]


def parse_sample_to_chunk(payload):
    if len(payload) < 8 or u32(payload, 0) != 0:
        raise FormatError("invalid sample-to-chunk table")
    count = u32(payload, 4)
    if len(payload) != 8 + count * 8:
        raise FormatError("sample-to-chunk table length mismatch")
    entries = [(u32(payload, 8 + i * 8), u32(payload, 12 + i * 8)) for i in range(count)]
    if not entries or entries[0][0] != 0:
        raise FormatError("sample-to-chunk table must start at chunk 0")
    last = -1
    for first_chunk, samples_per_chunk in entries:
        if first_chunk <= last or samples_per_chunk == 0:
            raise FormatError("invalid sample-to-chunk entry")
        last = first_chunk
    return entries


def expand_sample_offsets(chunks, sizes, stc):
    offsets = []
    sample_index = 0
    entry_index = 0
    for chunk_index, chunk_offset in enumerate(chunks):
        while entry_index + 1 < len(stc) and stc[entry_index + 1][0] <= chunk_index:
            entry_index += 1
        samples_per_chunk = stc[entry_index][1]
        pos = chunk_offset
        for _ in range(samples_per_chunk):
            if sample_index >= len(sizes):
                break
            offsets.append(pos)
            pos += sizes[sample_index]
            sample_index += 1
    if sample_index != len(sizes):
        raise FormatError("sample-to-chunk table does not account for every sample")
    return offsets


def parse_track_tables(track):
    required = [b"sfoc", b"pmsc", b"ziss", b"ruds", b"rcsd", b"csds", b"yeks"]
    for tag in required:
        if tag not in track.atoms:
            raise FormatError(f"missing track atom {tag!r}")
    chunks = parse_chunk_offsets(track.atoms[b"sfoc"])
    stc = parse_sample_to_chunk(track.atoms[b"pmsc"])
    count, default_size = parse_sample_size_fields(track.atoms[b"ziss"])
    if default_size != 0 and count == 0:
        sample_count = 0
        for chunk_index in range(len(chunks)):
            entry = stc[0]
            for candidate in stc:
                if candidate[0] <= chunk_index:
                    entry = candidate
                else:
                    break
            sample_count += entry[1]
        sizes = [default_size] * sample_count
    else:
        sizes = parse_sample_sizes(track.atoms[b"ziss"])
    offsets = expand_sample_offsets(chunks, sizes, stc)
    return offsets, sizes


def validate_common_tables(track, sample_count):
    ruds = track.atoms[b"ruds"]
    if len(ruds) < 8 or u32(ruds, 0) != 0:
        raise FormatError("invalid duration table")
    duration_count = u32(ruds, 4)
    if duration_count == 0 or len(ruds) != 8 + duration_count * 8:
        raise FormatError("duration table length mismatch")
    rcsd = track.atoms[b"rcsd"]
    if len(rcsd) != 16 or u32(rcsd, 0) != 0 or u32(rcsd, 4) != 1:
        raise FormatError("invalid sample-description table")
    csds = track.atoms[b"csds"]
    if len(csds) != 16 or u32(csds, 0) != 0 or u32(csds, 4) != 1:
        raise FormatError("invalid codec-specific-description table")
    keys = track.atoms[b"yeks"]
    if len(keys) < 8 or u32(keys, 0) != 0:
        raise FormatError("invalid keyframe table")
    key_count = u32(keys, 4)
    if len(keys) != 8 + key_count * 4:
        raise FormatError("keyframe table length mismatch")
    last = -1
    for i in range(key_count):
        key = u32(keys, 8 + i * 4)
        if key <= last or key >= sample_count:
            raise FormatError("invalid keyframe index")
        last = key


def parse_duration_entries(track):
    ruds = track.atoms[b"ruds"]
    if len(ruds) < 8 or u32(ruds, 0) != 0:
        raise FormatError("invalid duration table")
    count = u32(ruds, 4)
    if count == 0 or len(ruds) != 8 + count * 8:
        raise FormatError("duration table length mismatch")
    return [(u32(ruds, 8 + i * 8), u32(ruds, 12 + i * 8)) for i in range(count)]


def parse_mv(path):
    data = Path(path).read_bytes()
    header_size, movie_header, tracks = parse_atom_table(data)
    if len(movie_header) != 30:
        raise FormatError("invalid movie header length")
    if u32(movie_header, 0) != 0x00419014 or u32(movie_header, 4) != 90:
        raise FormatError("unsupported movie header")
    if u32(movie_header, 12) != 0 or u32(movie_header, 16) != 1 or u32(movie_header, 20) != 0:
        raise FormatError("unsupported movie header fields")
    if u16(movie_header, 24) != 2:
        raise FormatError("expected two tracks")

    video, palette = tracks
    if len(video.header) != 46:
        raise FormatError("invalid video track header length")
    if len(palette.header) != 32:
        raise FormatError("invalid palette track header length")
    fps = u32(video.header, 4)
    frame_count = u32(video.header, 8)
    if fps <= 0 or frame_count <= 0:
        raise FormatError("invalid frame rate or frame count")
    if u32(movie_header, 8) != frame_count * 90 // fps:
        raise FormatError("movie duration does not match video track")
    if video.header[24:28] != b"tdiv":
        raise FormatError("first track is not video")
    width = u16(video.header, 32)
    height = u16(video.header, 34)
    if width <= 0 or height <= 0:
        raise FormatError("invalid video dimensions")
    if video.header[36:46] != b"\x01\x00\x00\x00\x00\x00\x01\x00\xff\xff":
        raise FormatError("unsupported video descriptor fields")
    if palette.header[24:28] != b"tlap":
        raise FormatError("second track is not a palette")
    if palette.header[28:32] != b"\x01\x00\x00\x00":
        raise FormatError("unsupported palette descriptor fields")
    if u32(palette.header, 16) != 1024:
        raise FormatError("palette track must describe a 1024-byte palette")

    video_offsets, video_sizes = parse_track_tables(video)
    palette_offsets, palette_sizes = parse_track_tables(palette)
    if len(video_sizes) != frame_count or len(video_offsets) != frame_count:
        raise FormatError("video sample count mismatch")
    if not palette_sizes or any(size != 1024 for size in palette_sizes):
        raise FormatError("expected 1024-byte palette samples")
    validate_common_tables(video, frame_count)
    validate_common_tables(palette, 1)
    codec = video.atoms[b"rcsd"][8:12]
    if codec not in (b"sszl", b" elr"):
        raise FormatError(f"unsupported video codec tag {codec!r}")
    if palette.atoms[b"rcsd"][8:12] != b"\x00\x00\x00\x00":
        raise FormatError("unsupported palette sample description")

    ranges = []
    for offset, size in zip(palette_offsets + video_offsets, palette_sizes + video_sizes):
        if size < 0 or offset < header_size or offset + size > len(data):
            raise FormatError("sample range lies outside file")
        ranges.append((offset, offset + size))
    ranges.sort()
    if not ranges or ranges[0][0] != header_size:
        raise FormatError("media data does not begin at header size")
    pos = header_size
    for start, end in ranges:
        if start != pos:
            raise FormatError("gap or overlap in media sample data")
        pos = end
    if pos != len(data):
        raise FormatError("media samples do not account for the whole file")

    palette_rgbs = []
    for palette_offset in palette_offsets:
        palette_bytes = data[palette_offset:palette_offset + 1024]
        palette_rgb = []
        for i in range(256):
            b, g, r, _ = palette_bytes[i * 4:i * 4 + 4]
            palette_rgb.append((r, g, b))
        palette_rgbs.append(palette_rgb)
    frame_palette_indices = []
    for sample_index, duration in parse_duration_entries(palette):
        if sample_index >= len(palette_rgbs) or duration == 0:
            raise FormatError("invalid palette duration entry")
        frame_palette_indices.extend([sample_index] * duration)
    if len(frame_palette_indices) != frame_count:
        raise FormatError("palette durations do not cover the video duration")

    return ParsedMV(
        data=data,
        header_size=header_size,
        movie_header=movie_header,
        video=video,
        palette=palette,
        width=width,
        height=height,
        stride=(width + 3) & ~3,
        fps=fps,
        frame_count=frame_count,
        codec=codec,
        palette_rgbs=palette_rgbs,
        frame_palette_indices=frame_palette_indices,
        video_offsets=video_offsets,
        video_sizes=video_sizes,
        palette_offsets=palette_offsets,
        palette_sizes=palette_sizes,
    )


def decode_lzss_packet(packet, frame, stride, height):
    if len(packet) < 4:
        raise FormatError("truncated LZSS packet header")
    offset_bits = packet[0] >> 4
    length_bits = packet[0] & 0x0F
    if offset_bits == 0 or length_bits == 0:
        raise FormatError("unsupported LZSS packet header")
    reader = BitReaderMSB(packet[4:])
    out_len = stride * height
    pos = 0
    while pos < out_len:
        flag = reader.read(1)
        if flag:
            frame[pos] = reader.read(8)
            pos += 1
        else:
            offset = reader.read(offset_bits)
            length = reader.read(length_bits) + 2
            if pos + length > out_len:
                raise FormatError("LZSS token overruns frame buffer")
            if offset == 0:
                pos += length
            else:
                src = pos - (1 << offset_bits) + offset
                if src < 0:
                    raise FormatError("LZSS back-reference before frame start")
                for _ in range(length):
                    frame[pos] = frame[src]
                    pos += 1
                    src += 1
    if reader.used_bytes() != len(packet) - 4:
        raise FormatError("LZSS packet has unused bytes")


def decode_rle_packet(packet, frame):
    if len(packet) < 2 or packet[0] != 1 or packet[1] not in (0, 1):
        raise FormatError("unsupported RLE packet header")
    inter = packet[1] == 1
    out_len = len(frame)
    pos = 0
    i = 2
    while pos < out_len:
        if i >= len(packet):
            raise FormatError("RLE packet ended before the frame buffer was filled")
        code = packet[i]
        i += 1
        signed = code if code < 128 else code - 256
        if signed == 0:
            raise FormatError("RLE zero-length command")
        if signed > 0:
            if i >= len(packet) or pos + signed > out_len:
                raise FormatError("RLE repeat command overruns packet or frame")
            value = packet[i]
            i += 1
            if inter:
                for _ in range(signed):
                    frame[pos] = (frame[pos] + value) & 0xFF
                    pos += 1
            else:
                frame[pos:pos + signed] = bytes([value]) * signed
                pos += signed
        else:
            count = -signed
            if i + count > len(packet) or pos + count > out_len:
                raise FormatError("RLE literal command overruns packet or frame")
            if inter:
                for value in packet[i:i + count]:
                    frame[pos] = (frame[pos] + value) & 0xFF
                    pos += 1
            else:
                frame[pos:pos + count] = packet[i:i + count]
                pos += count
            i += count
    if i != len(packet):
        raise FormatError("RLE packet has unused bytes")


def frame_to_rgb(frame, parsed, frame_index):
    row_bytes = parsed.width * 3
    rgb = bytearray(row_bytes * parsed.height)
    palette_rgb = parsed.palette_rgbs[parsed.frame_palette_indices[frame_index]]
    out = 0
    for y in range(parsed.height):
        src = y * parsed.stride
        for x in range(parsed.width):
            r, g, b = palette_rgb[frame[src + x]]
            rgb[out] = r
            rgb[out + 1] = g
            rgb[out + 2] = b
            out += 3
    return rgb


def decode_frames(parsed):
    frame = bytearray(parsed.stride * parsed.height)
    for frame_index, (offset, size) in enumerate(zip(parsed.video_offsets, parsed.video_sizes)):
        packet = parsed.data[offset:offset + size]
        if parsed.codec == b"sszl":
            decode_lzss_packet(packet, frame, parsed.stride, parsed.height)
        elif parsed.codec == b" elr":
            decode_rle_packet(packet, frame)
        else:
            raise FormatError("unsupported codec")
        yield frame_to_rgb(frame, parsed, frame_index)


def convert(input_file, output_file):
    parsed = parse_mv(input_file)
    out_path = Path(output_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=out_path.name + ".", suffix=".tmp.avi", dir=str(out_path.parent or Path(".")))
    os.close(fd)
    os.unlink(tmp_name)
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{parsed.width}x{parsed.height}",
        "-r",
        str(parsed.fps),
        "-i",
        "-",
        "-an",
        "-c:v",
        "ffv1",
        tmp_name,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for rgb in decode_frames(parsed):
            proc.stdin.write(rgb)
        proc.stdin.close()
        if proc.wait() != 0:
            raise FormatError("ffmpeg failed while writing AVI")
        os.chmod(tmp_name, 0o664)
        os.replace(tmp_name, out_path)
    except Exception:
        try:
            if proc.stdin and not proc.stdin.closed:
                proc.stdin.close()
        except BrokenPipeError:
            pass
        proc.wait()
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        try:
            if out_path.exists():
                out_path.unlink()
        except OSError:
            pass
        raise


def main(argv):
    if len(argv) != 3:
        print("usage: movingPuzzlesMV.py <inputFile> <outputFile>", file=sys.stderr)
        return 2
    try:
        convert(argv[1], argv[2])
    except (FormatError, OSError, subprocess.SubprocessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

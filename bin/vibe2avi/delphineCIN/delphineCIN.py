#!/usr/bin/env python3
# Vibe coded by Codex
"""Convert Delphine Software International CIN video files to AVI."""

from __future__ import annotations

import os
import struct
import sys
import tempfile
from dataclasses import dataclass
from typing import BinaryIO


MAGIC = 0x55AA0000
FRAME_MARKER = 0xAA55AA55
FPS = 12
AUDIO_SAMPLE_RATE = 22050
VIDEO_TYPES = {9, 34, 35, 36, 37, 38, 39}
NO_AUDIO_TYPE = 0xFF
AUDIO_TYPE_DPCM = 1


class CinError(Exception):
    pass


@dataclass(frozen=True)
class FileHeader:
    max_video_frame_size: int
    width: int
    height: int
    audio_field: int
    audio_bits: int
    audio_stereo: int
    audio_frame_size: int


@dataclass(frozen=True)
class FrameInfo:
    offset: int
    video_type: int
    audio_type: int
    palette_type: int
    palette_count: int
    palette_size: int
    video_size: int
    audio_size: int
    payload_offset: int


def u16s(value: int) -> int:
    return struct.unpack("<h", struct.pack("<H", value))[0]


def read_file(path: str) -> bytes:
    try:
        with open(path, "rb") as f:
            return f.read()
    except OSError as exc:
        raise CinError(f"cannot read input: {exc}") from exc


def parse_cin(data: bytes) -> tuple[FileHeader, list[FrameInfo]]:
    if len(data) < 36:
        raise CinError("file is too small")
    magic, max_video, width, height, audio_field, audio_bits, audio_stereo, audio_frame_size = struct.unpack_from(
        "<IIHHIBBH", data, 0
    )
    if magic != MAGIC:
        raise CinError("missing Delphine CIN signature")
    if width == 0 or height == 0 or width > 4096 or height > 4096:
        raise CinError("invalid image dimensions")
    if max_video != width * height:
        raise CinError("declared maximum video frame size does not match width*height")

    header = FileHeader(max_video, width, height, audio_field, audio_bits, audio_stereo, audio_frame_size)
    frames: list[FrameInfo] = []
    pos = 20
    saw_audio = False
    saw_no_audio = False

    while pos < len(data):
        if pos + 16 > len(data):
            raise CinError(f"truncated frame header at byte {pos}")
        video_type, audio_type, pal_raw, video_size, audio_size, marker = struct.unpack_from("<BBHIII", data, pos)
        if marker != FRAME_MARKER:
            raise CinError(f"bad frame marker at byte {pos + 12}")
        if video_type not in VIDEO_TYPES:
            raise CinError(f"unsupported video frame type {video_type} at byte {pos}")
        if audio_type == AUDIO_TYPE_DPCM:
            saw_audio = True
        elif audio_type == NO_AUDIO_TYPE:
            saw_no_audio = True
            if audio_size != 0:
                raise CinError(f"no-audio frame has nonzero audio payload at byte {pos}")
        else:
            raise CinError(f"unsupported audio frame type {audio_type} at byte {pos}")

        pal_signed = u16s(pal_raw)
        palette_type = 1 if pal_signed < 0 else 0
        palette_count = -pal_signed if pal_signed < 0 else pal_signed
        if palette_count > 256:
            raise CinError(f"palette update has too many colors at byte {pos}")
        palette_size = palette_count * (4 if palette_type else 3)
        if video_size > max_video:
            raise CinError(f"video payload exceeds declared maximum at byte {pos}")
        payload_offset = pos + 16
        payload_size = palette_size + video_size + audio_size
        if payload_offset + payload_size > len(data):
            raise CinError(f"truncated frame payload at byte {payload_offset}")

        frames.append(
            FrameInfo(
                pos,
                video_type,
                audio_type,
                palette_type,
                palette_count,
                palette_size,
                video_size,
                audio_size,
                payload_offset,
            )
        )
        pos = payload_offset + payload_size

    if not frames:
        raise CinError("file has no frames")
    if saw_audio and saw_no_audio:
        raise CinError("mixed audio and no-audio frame types")
    if saw_audio:
        if not (audio_field == 11025 and audio_bits == 16 and audio_stereo == 1 and audio_frame_size == 3676):
            raise CinError("unsupported audio header variant")
    else:
        if any(frame.audio_size for frame in frames):
            raise CinError("unexpected audio payload in silent file")
    return header, frames


def decode_rle(src: bytes, dst_size: int) -> bytearray:
    out = bytearray()
    pos = 0
    while pos < len(src) and len(out) < dst_size:
        code = src[pos]
        pos += 1
        if code & 0x80:
            if pos >= len(src):
                raise CinError("truncated RLE repeat")
            out.extend([src[pos]] * (code - 0x7F))
            pos += 1
        else:
            count = code + 1
            if pos + count > len(src):
                raise CinError("truncated RLE literal")
            out.extend(src[pos : pos + count])
            pos += count
    if pos != len(src):
        raise CinError("RLE payload has unconsumed bytes")
    if len(out) != dst_size:
        raise CinError("RLE payload did not produce a full bitmap")
    return out


def decode_huffman(src: bytes, dst_limit: int, require_full: bool) -> bytearray:
    if len(src) < 15:
        raise CinError("truncated Huffman table")
    table = src[:15]
    pos = 15
    out = bytearray()
    while pos < len(src) and len(out) < dst_limit:
        code = src[pos]
        pos += 1
        if (code >> 4) == 15:
            if pos >= len(src):
                raise CinError("truncated Huffman high-nibble escape")
            b = src[pos]
            pos += 1
            out.append(((code << 4) & 0xFF) | (b >> 4))
            code = b & 15
        else:
            out.append(table[code >> 4])
            code &= 15
        if len(out) >= dst_limit:
            break
        if code == 15:
            if pos >= len(src):
                break
            out.append(src[pos])
            pos += 1
        else:
            out.append(table[code])
    if pos != len(src):
        raise CinError("Huffman payload has unconsumed bytes")
    if require_full and len(out) != dst_limit:
        raise CinError("Huffman payload did not produce a full bitmap")
    return out


def decode_lzss(src: bytes, dst_size: int) -> bytearray:
    out = bytearray()
    pos = 0
    while pos < len(src) and len(out) < dst_size:
        code = src[pos]
        pos += 1
        for bit in range(8):
            if pos >= len(src) or len(out) >= dst_size:
                break
            if code & (1 << bit):
                out.append(src[pos])
                pos += 1
            else:
                if pos + 2 > len(src):
                    raise CinError("truncated LZSS command")
                cmd = src[pos] | (src[pos + 1] << 8)
                pos += 2
                offset = cmd >> 4
                count = (cmd & 15) + 2
                if len(out) < offset + 1:
                    raise CinError("LZSS back-reference before start")
                for _ in range(count):
                    if len(out) >= dst_size:
                        break
                    out.append(out[len(out) - offset - 1])
    if pos != len(src):
        raise CinError("LZSS payload has unconsumed bytes")
    if len(out) != dst_size:
        raise CinError("LZSS payload did not produce a full bitmap")
    return out


def decode_video(frame_type: int, src: bytes, previous: bytearray, bitmap_size: int) -> bytearray:
    if frame_type == 9:
        current = decode_rle(src, bitmap_size)
    elif frame_type == 34:
        current = decode_rle(src, bitmap_size)
        apply_delta(current, previous)
    elif frame_type == 35:
        current = decode_rle(decode_huffman(src, bitmap_size, False), bitmap_size)
    elif frame_type == 36:
        current = decode_rle(decode_huffman(src, bitmap_size, False), bitmap_size)
        apply_delta(current, previous)
    elif frame_type == 37:
        current = decode_huffman(src, bitmap_size, True)
    elif frame_type == 38:
        current = decode_lzss(src, bitmap_size)
    elif frame_type == 39:
        current = decode_lzss(src, bitmap_size)
        apply_delta(current, previous)
    else:
        raise CinError(f"unsupported video frame type {frame_type}")
    return current


def apply_delta(current: bytearray, previous: bytearray) -> None:
    for i, old in enumerate(previous):
        current[i] = (current[i] + old) & 0xFF


DELTA16 = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, -30210, -27853, -25680, -23677, -21829, -20126, -18556, -17108, -15774, -14543, -13408, -12362, -11398,
    -10508, -9689, -8933, -8236, -7593, -7001, -6455, -5951, -5487, -5059, -4664, -4300, -3964, -3655, -3370, -3107,
    -2865, -2641, -2435, -2245, -2070, -1908, -1759, -1622, -1495, -1379, -1271, -1172, -1080, -996, -918, -847,
    -781, -720, -663, -612, -564, -520, -479, -442, -407, -376, -346, -319, -294, -271, -250, -230,
    -212, -196, -181, -166, -153, -141, -130, -120, -111, -102, -94, -87, -80, -74, -68, -62,
    -58, -53, -49, -45, -41, -38, -35, -32, -30, -27, -25, -23, -21, -20, -18, -17,
    -15, -14, -13, -12, -11, -10, -9, -8, -7, -6, -5, -4, -3, -2, -1, 0,
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
    17, 18, 20, 21, 23, 25, 27, 30, 32, 35, 38, 41, 45, 49, 53, 58,
    62, 68, 74, 80, 87, 94, 102, 111, 120, 130, 141, 153, 166, 181, 196, 212,
    230, 250, 271, 294, 319, 346, 376, 407, 442, 479, 520, 564, 612, 663, 720, 781,
    847, 918, 996, 1080, 1172, 1271, 1379, 1495, 1622, 1759, 1908, 2070, 2245, 2435, 2641, 2865,
    3107, 3370, 3655, 3964, 4300, 4664, 5059, 5487, 5951, 6455, 7001, 7593, 8236, 8933, 9689, 10508,
    11398, 12362, 13408, 14543, 15774, 17108, 18556, 20126, 21829, 23677, 25680, 27853, 30210, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
]


def clip_i16(value: int) -> int:
    return max(-32768, min(32767, value))


def decode_audio(src: bytes, state: dict[str, int | bool]) -> bytes:
    if not src:
        return b""
    pos = 0
    samples = bytearray()
    delta = int(state["delta"])
    if state["first"]:
        if len(src) < 2:
            raise CinError("initial audio packet is too small")
        delta = struct.unpack_from("<h", src, 0)[0]
        samples.extend(struct.pack("<h", delta))
        pos = 2
        state["first"] = False
    while pos < len(src):
        delta = clip_i16(delta + DELTA16[src[pos]])
        samples.extend(struct.pack("<h", delta))
        pos += 1
    state["delta"] = delta
    return bytes(samples)


def fourcc(value: str) -> bytes:
    return value.encode("ascii")


def pad2(size: int) -> bytes:
    return b"\0" if size & 1 else b""


class AviWriter:
    def __init__(self, path: str, width: int, height: int, frame_count: int, has_audio: bool, max_video_chunk: int):
        self.path = path
        self.width = width
        self.height = height
        self.frame_count = frame_count
        self.has_audio = has_audio
        self.max_video_chunk = max_video_chunk
        self.audio_bytes = 0
        self.index: list[tuple[bytes, int, int, int]] = []
        self.f: BinaryIO | None = None
        self.riff_size_pos = 0
        self.hdrl_size_pos = 0
        self.avih_pos = 0
        self.vstrh_pos = 0
        self.astrh_pos = 0
        self.movi_list_start = 0
        self.movi_data_start = 0

    def __enter__(self) -> "AviWriter":
        self.f = open(self.path, "wb")
        self._write_headers()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.f is not None:
            if exc_type is None:
                self._finalize()
            self.f.close()

    @property
    def file(self) -> BinaryIO:
        if self.f is None:
            raise RuntimeError("AVI writer is not open")
        return self.f

    def _start_chunk(self, chunk_id: bytes) -> int:
        f = self.file
        f.write(chunk_id)
        pos = f.tell()
        f.write(b"\0\0\0\0")
        return pos

    def _finish_chunk(self, size_pos: int) -> int:
        f = self.file
        end = f.tell()
        size = end - size_pos - 4
        f.seek(size_pos)
        f.write(struct.pack("<I", size))
        f.seek(end)
        f.write(pad2(size))
        return size

    def _start_list(self, list_type: bytes) -> int:
        f = self.file
        f.write(b"LIST")
        pos = f.tell()
        f.write(b"\0\0\0\0")
        f.write(list_type)
        return pos

    def _finish_list(self, size_pos: int) -> int:
        f = self.file
        end = f.tell()
        size = end - size_pos - 4
        f.seek(size_pos)
        f.write(struct.pack("<I", size))
        f.seek(end)
        return size

    def _write_headers(self) -> None:
        f = self.file
        f.write(b"RIFF")
        self.riff_size_pos = f.tell()
        f.write(b"\0\0\0\0")
        f.write(b"AVI ")

        self.hdrl_size_pos = self._start_list(b"hdrl")
        self.avih_pos = self._start_chunk(b"avih")
        f.write(b"\0" * 56)
        self._finish_chunk(self.avih_pos)

        self._write_video_stream_header()
        if self.has_audio:
            self._write_audio_stream_header()
        self._finish_list(self.hdrl_size_pos)

        self.movi_list_start = self._start_list(b"movi")
        self.movi_data_start = f.tell()

    def _write_video_stream_header(self) -> None:
        f = self.file
        strl = self._start_list(b"strl")
        self.vstrh_pos = self._start_chunk(b"strh")
        f.write(b"\0" * 56)
        self._finish_chunk(self.vstrh_pos)

        strf = self._start_chunk(b"strf")
        row_size = ((self.width * 24 + 31) // 32) * 4
        image_size = row_size * self.height
        f.write(
            struct.pack(
                "<IiiHHIIiiII",
                40,
                self.width,
                self.height,
                1,
                24,
                0,
                image_size,
                0,
                0,
                0,
                0,
            )
        )
        self._finish_chunk(strf)
        self._finish_list(strl)

    def _write_audio_stream_header(self) -> None:
        f = self.file
        strl = self._start_list(b"strl")
        self.astrh_pos = self._start_chunk(b"strh")
        f.write(b"\0" * 56)
        self._finish_chunk(self.astrh_pos)

        strf = self._start_chunk(b"strf")
        block_align = 2
        f.write(
            struct.pack(
                "<HHIIHH",
                1,
                1,
                AUDIO_SAMPLE_RATE,
                AUDIO_SAMPLE_RATE * block_align,
                block_align,
                16,
            )
        )
        self._finish_chunk(strf)
        self._finish_list(strl)

    def write_video(self, dib: bytes) -> None:
        self._write_data_chunk(b"00db", dib, 0x10)

    def write_audio(self, pcm: bytes) -> None:
        if not pcm:
            return
        self.audio_bytes += len(pcm)
        self._write_data_chunk(b"01wb", pcm, 0x10)

    def _write_data_chunk(self, chunk_id: bytes, payload: bytes, flags: int) -> None:
        f = self.file
        offset = f.tell() - self.movi_data_start
        f.write(chunk_id)
        f.write(struct.pack("<I", len(payload)))
        f.write(payload)
        f.write(pad2(len(payload)))
        self.index.append((chunk_id, flags, offset, len(payload)))

    def _finalize(self) -> None:
        f = self.file
        self._finish_list(self.movi_list_start)
        idx_pos = self._start_chunk(b"idx1")
        for chunk_id, flags, offset, size in self.index:
            f.write(chunk_id)
            f.write(struct.pack("<III", flags, offset, size))
        self._finish_chunk(idx_pos)

        end = f.tell()
        f.seek(self.avih_pos + 4)
        row_size = ((self.width * 24 + 31) // 32) * 4
        f.write(
            struct.pack(
                "<IIIIIIIIIIIIII",
                int(1_000_000 / FPS),
                AUDIO_SAMPLE_RATE * 2 if self.has_audio else row_size * self.height * FPS,
                0,
                0x10,
                self.frame_count,
                0,
                2 if self.has_audio else 1,
                max(self.max_video_chunk, 2 * AUDIO_SAMPLE_RATE),
                self.width,
                self.height,
                0,
                0,
                0,
                0,
            )
        )

        f.seek(self.vstrh_pos + 4)
        f.write(
            struct.pack(
                "<4s4sIHHIIIIIIIIhhhh",
                fourcc("vids"),
                fourcc("DIB "),
                0,
                0,
                0,
                0,
                1,
                FPS,
                0,
                self.frame_count,
                self.max_video_chunk,
                0xFFFFFFFF,
                0,
                0,
                0,
                self.width,
                self.height,
            )
        )
        if self.has_audio:
            f.seek(self.astrh_pos + 4)
            f.write(
                struct.pack(
                    "<4s4sIHHIIIIIIIIhhhh",
                    fourcc("auds"),
                    b"\0\0\0\0",
                    0,
                    0,
                    0,
                    0,
                    2,
                    AUDIO_SAMPLE_RATE * 2,
                    0,
                    self.audio_bytes // 2,
                    AUDIO_SAMPLE_RATE * 2,
                    0xFFFFFFFF,
                    2,
                    0,
                    0,
                    0,
                    0,
                )
            )

        f.seek(self.riff_size_pos)
        f.write(struct.pack("<I", end - 8))
        f.seek(end)


def apply_palette(palette: list[tuple[int, int, int]], palette_type: int, payload: bytes, count: int) -> None:
    if palette_type == 0:
        for i in range(count):
            r, g, b = payload[i * 3 : i * 3 + 3]
            palette[i] = (r, g, b)
    else:
        pos = 0
        for _ in range(count):
            index = payload[pos]
            r, g, b = payload[pos + 1 : pos + 4]
            palette[index] = (r, g, b)
            pos += 4


def pal8_to_bgr24(bitmap: bytearray, palette: list[tuple[int, int, int]], width: int, height: int) -> bytes:
    row_pad = (4 - (width * 3) % 4) % 4
    out = bytearray()
    for y in range(height):
        base = y * width
        for index in bitmap[base : base + width]:
            r, g, b = palette[index]
            out.extend((b, g, r))
        if row_pad:
            out.extend(b"\0" * row_pad)
    return bytes(out)


def convert(input_path: str, output_path: str) -> None:
    data = read_file(input_path)
    header, frames = parse_cin(data)
    has_audio = any(frame.audio_type == AUDIO_TYPE_DPCM for frame in frames)
    bitmap_size = header.width * header.height
    row_size = ((header.width * 24 + 31) // 32) * 4
    max_video_chunk = row_size * header.height

    out_dir = os.path.dirname(os.path.abspath(output_path)) or "."
    os.makedirs(out_dir, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix=".delphineCIN.", suffix=".avi", dir=out_dir)
    os.close(fd)

    previous = bytearray(bitmap_size)
    palette = [(0, 0, 0)] * 256
    audio_state: dict[str, int | bool] = {"first": True, "delta": 0}
    try:
        with AviWriter(tmp_path, header.width, header.height, len(frames), has_audio, max_video_chunk) as avi:
            for frame in frames:
                payload = data[frame.payload_offset : frame.payload_offset + frame.palette_size + frame.video_size + frame.audio_size]
                palette_payload = payload[: frame.palette_size]
                video_payload = payload[frame.palette_size : frame.palette_size + frame.video_size]
                audio_payload = payload[frame.palette_size + frame.video_size :]
                apply_palette(palette, frame.palette_type, palette_payload, frame.palette_count)
                current = decode_video(frame.video_type, video_payload, previous, bitmap_size)
                avi.write_video(pal8_to_bgr24(current, palette, header.width, header.height))
                previous = current
                if has_audio:
                    if frame.audio_type != AUDIO_TYPE_DPCM:
                        raise CinError("silent frame in audio file")
                    avi.write_audio(decode_audio(audio_payload, audio_state))
        os.chmod(tmp_path, 0o664)
        os.replace(tmp_path, output_path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: delphineCIN.py <inputFile> <outputFile>", file=sys.stderr)
        return 2
    try:
        convert(argv[1], argv[2])
    except CinError as exc:
        print(f"delphineCIN: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"delphineCIN: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

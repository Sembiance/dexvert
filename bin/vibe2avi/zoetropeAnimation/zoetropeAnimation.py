#!/usr/bin/env python3
# Vibe coded by Codex
"""Convert Zoetrope Animation RIFF/VRUN files to uncompressed AVI."""

from __future__ import annotations

import os
import struct
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


class ZoetropeError(Exception):
    pass


@dataclass
class Frame:
    palette: list[tuple[int, int, int]]
    rgb: bytes


@dataclass
class Animation:
    width: int
    height: int
    depth: int
    delay_jiffies: int
    frames: list[Frame]


def be16(data: bytes, offset: int) -> int:
    return struct.unpack_from(">H", data, offset)[0]


def be32(data: bytes, offset: int) -> int:
    return struct.unpack_from(">I", data, offset)[0]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ZoetropeError(message)


def decode_full_vrun_plane(data: bytes, width_bytes: int, height: int) -> tuple[bytearray, int]:
    """Decode mode 1: full byte-vertical RLE into a cleared bitplane."""
    pos = 0
    plane = bytearray(width_bytes * height)
    for x in range(width_bytes):
        require(pos < len(data), "truncated full-plane column")
        op_count = data[pos]
        pos += 1
        y = 0
        for _ in range(op_count):
            require(pos < len(data), "truncated full-plane op")
            code = data[pos]
            pos += 1
            if code & 0x80:
                count = code & 0x7F
                require(pos + count <= len(data), "truncated full-plane literal")
                for value in data[pos : pos + count]:
                    require(y < height, "full-plane literal exceeds image height")
                    plane[y * width_bytes + x] = value
                    y += 1
                pos += count
            else:
                count = code
                require(pos < len(data), "truncated full-plane run")
                value = data[pos]
                pos += 1
                require(y + count <= height, "full-plane run exceeds image height")
                for _ in range(count):
                    plane[y * width_bytes + x] = value
                    y += 1
        require(y == height, "full-plane column did not fill image height")
    return plane, pos


def decode_delta_vrun_plane(
    data: bytes, previous: bytearray, width_bytes: int, height: int
) -> tuple[bytearray, int]:
    """Decode mode 2: byte-vertical delta applied to the previous bitplane."""
    pos = 0
    plane = bytearray(previous)
    for x in range(width_bytes):
        require(pos < len(data), "truncated delta-plane column")
        op_count = data[pos]
        pos += 1
        y = 0
        for _ in range(op_count):
            require(pos < len(data), "truncated delta-plane op")
            code = data[pos]
            pos += 1
            if code == 0:
                require(pos + 2 <= len(data), "truncated delta-plane same run")
                count = data[pos]
                value = data[pos + 1]
                pos += 2
                require(y + count <= height, "delta-plane same run exceeds image height")
                for _ in range(count):
                    plane[y * width_bytes + x] = value
                    y += 1
            elif code & 0x80:
                count = code & 0x7F
                require(pos + count <= len(data), "truncated delta-plane literal")
                require(y + count <= height, "delta-plane literal exceeds image height")
                for value in data[pos : pos + count]:
                    plane[y * width_bytes + x] = value
                    y += 1
                pos += count
            else:
                y += code
                require(y <= height, "delta-plane skip exceeds image height")
    return plane, pos


def decode_partial_full_vrun_plane(data: bytes, width_bytes: int, height: int) -> tuple[bytearray, int]:
    """Decode a mode 1 plane until an EOF-truncated stream runs out."""
    pos = 0
    plane = bytearray(width_bytes * height)
    for x in range(width_bytes):
        if pos >= len(data):
            return plane, pos
        op_count = data[pos]
        pos += 1
        y = 0
        for _ in range(op_count):
            if pos >= len(data):
                return plane, pos
            code = data[pos]
            pos += 1
            if code & 0x80:
                count = code & 0x7F
                available = min(count, len(data) - pos, height - y)
                for value in data[pos : pos + available]:
                    plane[y * width_bytes + x] = value
                    y += 1
                pos += available
                if available != count:
                    return plane, pos
            else:
                count = code
                if pos >= len(data):
                    return plane, pos
                value = data[pos]
                pos += 1
                available = min(count, height - y)
                for _ in range(available):
                    plane[y * width_bytes + x] = value
                    y += 1
                if available != count:
                    return plane, pos
    return plane, pos


def decode_partial_delta_vrun_plane(
    data: bytes, previous: bytearray, width_bytes: int, height: int
) -> tuple[bytearray, int]:
    """Decode a mode 2 plane until an EOF-truncated stream runs out."""
    pos = 0
    plane = bytearray(previous)
    for x in range(width_bytes):
        if pos >= len(data):
            return plane, pos
        op_count = data[pos]
        pos += 1
        y = 0
        for _ in range(op_count):
            if pos >= len(data):
                return plane, pos
            code = data[pos]
            pos += 1
            if code == 0:
                if pos + 2 > len(data):
                    return plane, pos
                count = data[pos]
                value = data[pos + 1]
                pos += 2
                available = min(count, height - y)
                for _ in range(available):
                    plane[y * width_bytes + x] = value
                    y += 1
                if available != count:
                    return plane, pos
            elif code & 0x80:
                count = code & 0x7F
                available = min(count, len(data) - pos, height - y)
                for value in data[pos : pos + available]:
                    plane[y * width_bytes + x] = value
                    y += 1
                pos += available
                if available != count:
                    return plane, pos
            else:
                y += code
                if y > height:
                    return plane, pos
    return plane, pos


def decode_palette(payload: bytes) -> list[tuple[int, int, int]]:
    palette: list[tuple[int, int, int]] = []
    for i in range(32):
        color = be16(payload, 0x30 + i * 2)
        palette.append(
            (
                ((color >> 8) & 0xF) * 17,
                ((color >> 4) & 0xF) * 17,
                (color & 0xF) * 17,
            )
        )
    return palette


def chunky_rgb(
    planes: list[bytearray],
    palette: list[tuple[int, int, int]],
    width: int,
    height: int,
    depth: int,
) -> bytes:
    width_bytes = width // 8
    rgb = bytearray(width * height * 3)
    out = 0
    for y in range(height):
        row = y * width_bytes
        for x in range(width):
            bit = 7 - (x & 7)
            byte_index = row + (x >> 3)
            color_index = 0
            for plane_index in range(depth):
                color_index |= ((planes[plane_index][byte_index] >> bit) & 1) << plane_index
            r, g, b = palette[color_index]
            rgb[out : out + 3] = bytes((r, g, b))
            out += 3
    return bytes(rgb)


def read_offsets(data: bytes, frame_count: int) -> list[int]:
    table_end = 0x40 + frame_count * 4
    require(table_end <= len(data), "truncated frame offset table")
    offsets = [be32(data, 0x40 + i * 4) for i in range(frame_count)]
    if frame_count and all(offset == 0 for offset in offsets):
        offsets = []
        offset = table_end
        for _ in range(frame_count):
            require(offset + 8 <= len(data), "truncated sequential VRUN frame")
            require(data[offset : offset + 4] == b"VRUN", "missing sequential VRUN tag")
            size = be32(data, offset + 4)
            require(offset + 8 + size <= len(data), "truncated sequential VRUN payload")
            offsets.append(offset)
            offset += 8 + size
    else:
        require(all(offset >= table_end for offset in offsets), "frame offset overlaps header")
        require(offsets == sorted(offsets), "frame offsets are not sorted")
    return offsets


def parse_zoetrope(path: Path) -> Animation:
    data = path.read_bytes()
    require(len(data) >= 0x40, "file is too small")
    require(data[:4] == b"RIFF", "missing RIFF magic")
    require(data[8:12] == b"\x00\x00\x00\x00", "unexpected header reserved field")

    width = be16(data, 0x0C)
    height = be16(data, 0x0E)
    depth = be16(data, 0x10)
    reserved_12 = be16(data, 0x12)
    frame_count = be16(data, 0x14)
    delay_jiffies = be16(data, 0x16)
    repeated_frame_count = be16(data, 0x18)

    require(width > 0 and height > 0, "invalid dimensions")
    require(width % 8 == 0, "width is not byte aligned")
    require(1 <= depth <= 5, "unsupported bitplane depth")
    require(reserved_12 == 0, "unexpected header word at 0x12")
    require(frame_count > 0, "empty animation")
    require(
        repeated_frame_count in (0, frame_count),
        "secondary frame-count field is not zero or the primary frame count",
    )
    require(data[0x1A:0x40] == b"\x00" * 0x26, "non-zero reserved header bytes")

    offsets = read_offsets(data, frame_count)
    width_bytes = width // 8
    previous = [bytearray(width_bytes * height) for _ in range(depth)]
    frames: list[Frame] = []

    for frame_index, offset in enumerate(offsets):
        require(offset + 8 <= len(data), f"frame {frame_index} points past EOF")
        require(data[offset : offset + 4] == b"VRUN", f"frame {frame_index} missing VRUN tag")
        chunk_size = be32(data, offset + 4)
        payload_end = offset + 8 + chunk_size
        truncated_at_eof = payload_end > len(data)
        if truncated_at_eof:
            require(frame_index == len(frames), f"frame {frame_index} VRUN payload is truncated")
            payload = data[offset + 8 :]
        else:
            payload = data[offset + 8 : payload_end]
        require(len(payload) >= 0x70, f"frame {frame_index} VRUN payload too small")
        require(payload[0:4] == b"\x00\x00\x00\x00", f"frame {frame_index} bad VRUN reserved dword")
        require(be16(payload, 4) == width, f"frame {frame_index} width mismatch")
        require(be16(payload, 6) == height, f"frame {frame_index} height mismatch")
        require(be16(payload, 8) == depth, f"frame {frame_index} depth mismatch")
        require(be16(payload, 10) == 0, f"frame {frame_index} bad VRUN reserved word")
        require(payload[0x20:0x30] == b"\x00" * 0x10, f"frame {frame_index} bad VRUN reserved bytes")

        descriptors = [struct.unpack_from(">HH", payload, 0x0C + i * 4) for i in range(5)]
        for plane_index in range(depth, 5):
            require(
                descriptors[plane_index] == (0, 0),
                f"frame {frame_index} has data for unused plane {plane_index}",
            )

        pos = 0x70
        current: list[bytearray] = []
        for plane_index in range(depth):
            mode, plane_size = descriptors[plane_index]
            plane_is_truncated = truncated_at_eof and pos + plane_size > len(payload)
            if plane_is_truncated:
                plane_data = payload[pos:]
            else:
                require(pos + plane_size <= len(payload), f"frame {frame_index} plane {plane_index} is truncated")
                plane_data = payload[pos : pos + plane_size]
            pos += plane_size
            if mode == 1:
                if plane_is_truncated:
                    plane, used = decode_partial_full_vrun_plane(plane_data, width_bytes, height)
                else:
                    plane, used = decode_full_vrun_plane(plane_data, width_bytes, height)
            elif mode == 2:
                if plane_is_truncated:
                    plane, used = decode_partial_delta_vrun_plane(
                        plane_data, previous[plane_index], width_bytes, height
                    )
                else:
                    plane, used = decode_delta_vrun_plane(plane_data, previous[plane_index], width_bytes, height)
            else:
                raise ZoetropeError(f"frame {frame_index} plane {plane_index} has unsupported mode {mode}")
            if not plane_is_truncated:
                require(
                    len(plane_data) - used <= 3,
                    f"frame {frame_index} plane {plane_index} has too many alignment bytes",
                )
            current.append(plane)
        if truncated_at_eof:
            require(pos >= len(payload), f"frame {frame_index} has bytes past truncated frame")
        else:
            require(pos == len(payload), f"frame {frame_index} has unaccounted VRUN payload bytes")

        palette = decode_palette(payload)
        frames.append(Frame(palette=palette, rgb=chunky_rgb(current, palette, width, height, depth)))
        previous = current
        if truncated_at_eof:
            break

    effective_delay = delay_jiffies or 4
    return Animation(width=width, height=height, depth=depth, delay_jiffies=effective_delay, frames=frames)


def riff_chunk(tag: bytes, payload: bytes) -> bytes:
    padding = b"\x00" if len(payload) & 1 else b""
    return tag + struct.pack("<I", len(payload)) + payload + padding


def riff_list(list_type: bytes, payload: bytes) -> bytes:
    return riff_chunk(b"LIST", list_type + payload)


def write_avi(animation: Animation, output_path: Path) -> None:
    width = animation.width
    height = animation.height
    frame_count = len(animation.frames)
    frame_interval_us = round(animation.delay_jiffies * 1_000_000 / 60)
    frame_payloads: list[bytes] = []
    row_bytes = ((width * 3 + 3) // 4) * 4
    padding = b"\x00" * (row_bytes - width * 3)

    for frame in animation.frames:
        dib = bytearray()
        for y in range(height - 1, -1, -1):
            row = frame.rgb[y * width * 3 : (y + 1) * width * 3]
            for x in range(width):
                r, g, b = row[x * 3 : x * 3 + 3]
                dib.extend((b, g, r))
            dib.extend(padding)
        frame_payloads.append(bytes(dib))

    suggested_buffer = max(len(payload) for payload in frame_payloads)
    avih = struct.pack(
        "<IIIIIIIIII4I",
        frame_interval_us,
        suggested_buffer * 60 // animation.delay_jiffies,
        0,
        0x10,
        frame_count,
        0,
        1,
        suggested_buffer,
        width,
        height,
        0,
        0,
        0,
        0,
    )
    strh = struct.pack(
        "<4s4sIHHIIIIIIIIhhhh",
        b"vids",
        b"DIB ",
        0,
        0,
        0,
        0,
        animation.delay_jiffies,
        60,
        0,
        frame_count,
        suggested_buffer,
        0xFFFFFFFF,
        0,
        0,
        0,
        width,
        height,
    )
    strf = struct.pack(
        "<IiiHHIIiiII",
        40,
        width,
        height,
        1,
        24,
        0,
        row_bytes * height,
        2835,
        2835,
        0,
        0,
    )
    hdrl = riff_list(
        b"hdrl",
        riff_chunk(b"avih", avih)
        + riff_list(b"strl", riff_chunk(b"strh", strh) + riff_chunk(b"strf", strf)),
    )

    movi_payload = bytearray()
    index_entries = bytearray()
    movi_data_start = 4
    for payload in frame_payloads:
        chunk_start = len(movi_payload)
        movi_payload.extend(riff_chunk(b"00db", payload))
        index_entries.extend(
            struct.pack("<4sIII", b"00db", 0x10, movi_data_start + chunk_start, len(payload))
        )

    movi = riff_list(b"movi", bytes(movi_payload))
    idx1 = riff_chunk(b"idx1", bytes(index_entries))
    riff_payload = b"AVI " + hdrl + movi + idx1
    output_path.write_bytes(b"RIFF" + struct.pack("<I", len(riff_payload)) + riff_payload)


def convert(input_file: Path, output_file: Path) -> None:
    animation = parse_zoetrope(input_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{output_file.name}.", suffix=".tmp", dir=str(output_file.parent))
    os.close(fd)
    tmp_path = Path(tmp_name)
    try:
        write_avi(animation, tmp_path)
        os.chmod(tmp_path, 0o664)
        os.replace(tmp_path, output_file)
        os.chmod(output_file, 0o664)
    except Exception:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: zoetropeAnimation.py <inputFile> <outputFile>", file=sys.stderr)
        return 2
    input_file = Path(argv[1])
    output_file = Path(argv[2])
    try:
        convert(input_file, output_file)
    except Exception as exc:
        print(f"zoetropeAnimation: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

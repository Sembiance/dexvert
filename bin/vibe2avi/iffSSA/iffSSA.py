#!/usr/bin/env python3
# Vibe coded by Codex
"""
Convert ClariSSA / proDAD Super Smooth Animation IFF files to uncompressed AVI.
"""

from __future__ import annotations

import os
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


FPS = 25
FORM_TYPES = {b"SSA ", b"SSA5", b"SSAd"}
FRAME_CHUNKS = {b"DSCR", b"COST", b"BEST", b"DAST", b"SPST", b"dscr"}


class SSAError(Exception):
    pass


@dataclass
class Chunk:
    chunk_id: bytes
    data: bytes


@dataclass
class Frame:
    dscr: bytes
    cost: bytes | None
    best: bytes | None
    dast: bytes | None
    spst: bytes | None
    lower_dscr: bytes | None = None


@dataclass
class Animation:
    form_type: bytes
    width: int
    height: int
    planes: int
    mode: int
    frame_count: int
    anim_header: bytes
    frames: list[Frame]


def u16be(data: bytes, off: int = 0) -> int:
    return struct.unpack_from(">H", data, off)[0]


def u32be(data: bytes, off: int = 0) -> int:
    return struct.unpack_from(">I", data, off)[0]


def pad2(size: int) -> int:
    return size + (size & 1)


def fail(message: str) -> None:
    raise SSAError(message)


def parse_frame_chunks(data: bytes, start: int, end: int) -> list[Chunk] | None:
    pos = start
    chunks: list[Chunk] = []
    while pos < end:
        if pos + 8 > end:
            return None
        chunk_id = data[pos : pos + 4]
        if chunk_id not in FRAME_CHUNKS:
            return None
        size = u32be(data, pos + 4)
        dstart = pos + 8
        dend = dstart + size
        next_pos = dend + (size & 1)
        if dend > end or next_pos > end:
            return None
        chunks.append(Chunk(chunk_id, data[dstart:dend]))
        pos = next_pos
    return chunks if pos == end else None


def parse_dlta_form(data: bytes, pos: int, size: int) -> tuple[Frame, int]:
    if data[pos : pos + 4] != b"FORM" or data[pos + 8 : pos + 12] != b"DLTA":
        fail(f"expected FORM DLTA at offset {pos}")

    next_form = data.find(b"FORM", pos + 1)
    if next_form < 0:
        next_form = len(data)
    candidates = [pos + 8 + size, pos + 12 + size, next_form]
    for end in candidates:
        if end < pos + 12 or end > len(data):
            continue
        chunks = parse_frame_chunks(data, pos + 12, end)
        if chunks is None:
            continue
        if not chunks:
            return (
                Frame(
                    dscr=b"\0\0\0\0\0\0",
                    cost=None,
                    best=None,
                    dast=None,
                    spst=None,
                    lower_dscr=b"",
                ),
                end + ((end - pos - 8) & 1),
            )
        seen: dict[bytes, bytes] = {}
        order = []
        for chunk in chunks:
            if chunk.chunk_id in seen:
                fail(f"duplicate {chunk.chunk_id.decode('ascii')} chunk at offset {pos}")
            seen[chunk.chunk_id] = chunk.data
            order.append(chunk.chunk_id)
        if order[0:1] == [b"dscr"]:
            if len(order) != 1 or len(seen[b"dscr"]) != 4:
                fail(f"bad lowercase dscr frame at offset {pos}")
            return (
                Frame(
                    dscr=b"\0\0\0\0\0\0",
                    cost=None,
                    best=None,
                    dast=None,
                    spst=None,
                    lower_dscr=seen[b"dscr"],
                ),
                end + ((end - pos - 8) & 1),
            )
        if order[0:1] != [b"DSCR"]:
            fail(f"FORM DLTA at offset {pos} does not start with DSCR")
        if len(seen[b"DSCR"]) not in (6, 10):
            fail(f"unsupported DSCR length at offset {pos}")
        return (
            Frame(
                dscr=seen[b"DSCR"],
                cost=seen.get(b"COST"),
                best=seen.get(b"BEST"),
                dast=seen.get(b"DAST"),
                    spst=seen.get(b"SPST"),
                    lower_dscr=None,
                ),
            end + ((end - pos - 8) & 1),
        )
    fail(f"bad FORM DLTA size at offset {pos}")


def parse_animation(path: Path) -> Animation:
    data = path.read_bytes()
    if len(data) < 20 or data[:4] != b"FORM":
        fail("not an IFF FORM file")
    form_type = data[8:12]
    if form_type not in FORM_TYPES:
        fail("unsupported FORM type")

    pos = 12
    if data[pos : pos + 4] != b"ANIM":
        if data[pos : pos + 4] == b"MDHD":
            fail("project/edit file, not an animation")
        fail("missing ANIM chunk")
    anim_size = u32be(data, pos + 4)
    if anim_size not in (26, 44, 92):
        fail("unsupported ANIM header length")
    anim_start = pos + 8
    anim_end = anim_start + anim_size
    if anim_end > len(data):
        fail("truncated ANIM chunk")
    anim_header = data[anim_start:anim_end]
    vals = [u16be(anim_header, i) for i in range(0, len(anim_header), 2)]
    if vals[0:4] != [0x0104, 0x0400, 0, 0]:
        fail("unexpected ANIM signature fields")
    width, height, planes, mode, frame_count = vals[4], vals[5], vals[6], vals[8], vals[10]
    if width <= 0 or height <= 0 or planes <= 0 or planes > 8 or frame_count <= 0:
        fail("invalid ANIM dimensions")
    if vals[9] != 0:
        fail("unexpected non-zero ANIM reserved fields")
    pos = anim_end + (anim_size & 1)

    frames: list[Frame] = []
    ssad_pool: bytes | None = None
    ssad_pool_pos = 0
    while pos < len(data) and (len(frames) < frame_count or (form_type == b"SSAd" and ssad_pool is None)):
        if pos + 12 > len(data):
            fail(f"trailing bytes at offset {pos}")
        chunk_id = data[pos : pos + 4]
        size = u32be(data, pos + 4)
        if chunk_id != b"FORM":
            fail(f"unexpected top-level chunk at offset {pos}")
        form_name = data[pos + 8 : pos + 12]
        if form_name == b"DLTA":
            frame, next_pos = parse_dlta_form(data, pos, size)
            frames.append(frame)
            pos = next_pos
        elif form_name == b"BEST":
            end = pos + 8 + size
            if end > len(data):
                fail("truncated top-level FORM BEST")
            if form_type != b"SSAd":
                fail("top-level FORM BEST is only supported for SSAd")
            if ssad_pool is not None:
                fail("duplicate top-level FORM BEST")
            ssad_pool = data[pos + 12 : end]
            pos = end + (size & 1)
        else:
            fail(f"unsupported top-level FORM {form_name!r}")

    if len(frames) != frame_count:
        fail(f"ANIM declares {frame_count} frames but file contains {len(frames)}")

    if form_type == b"SSAd":
        if ssad_pool is None:
            fail("SSAd file has no shared FORM BEST data pool")
        split_frames: list[Frame] = []
        for frame in frames:
            if len(frame.dscr) != 10:
                fail("SSAd frame DSCR does not contain shared data sizes")
            if frame.best is not None or frame.dast is not None:
                fail("SSAd frame unexpectedly contains inline image chunks")
            best_size = u16be(frame.dscr, 4)
            dast_size = u32be(frame.dscr, 6)
            end_best = ssad_pool_pos + best_size
            end_dast = end_best + dast_size
            if end_dast > len(ssad_pool):
                fail("SSAd shared image data overrun")
            split_frames.append(
                Frame(
                    dscr=frame.dscr,
                    cost=frame.cost,
                    best=ssad_pool[ssad_pool_pos:end_best],
                    dast=ssad_pool[end_best:end_dast],
                    spst=frame.spst,
                    lower_dscr=frame.lower_dscr,
                )
            )
            ssad_pool_pos = end_dast
        if ssad_pool_pos != len(ssad_pool):
            fail("unused bytes remain in SSAd shared image data")
        frames = split_frames
    else:
        for frame in frames:
            if frame.lower_dscr is not None:
                continue
            if len(frame.dscr) != 6:
                fail("non-SSAd DSCR length must be 6")

    return Animation(form_type, width, height, planes, mode, frame_count, anim_header, frames)


class WordReader:
    def __init__(self, data: bytes) -> None:
        if len(data) & 1:
            fail("DAST chunk has odd length")
        self.data = data
        self.pos = 0

    def read(self) -> int:
        if self.pos + 2 > len(self.data):
            fail("DAST word stream underflow")
        val = u16be(self.data, self.pos)
        self.pos += 2
        return val

    def done(self) -> bool:
        return self.pos == len(self.data)


class PlaneWriter:
    def __init__(self, planes: list[bytearray], rowbytes: int, height: int, field: int) -> None:
        self.planes = planes
        self.rowbytes = rowbytes
        self.height = height
        self.first_line = 0
        self.virtual_height = height
        self.virtual_size = rowbytes * self.virtual_height
        self.plane = 0
        self.cursor = 0

    def end_plane(self) -> None:
        self.plane += 1
        self.cursor = 0

    def skip(self, byte_count: int) -> None:
        if byte_count < 0:
            fail("negative output skip")
        if self.plane >= len(self.planes):
            fail("output skip past final bitplane")
        if self.cursor + byte_count > self.virtual_size:
            fail("output skip overruns bitplane")
        self.cursor += byte_count

    def write_word(self, value: int) -> None:
        if self.plane >= len(self.planes):
            fail("output write past final bitplane")
        if self.cursor == self.virtual_size:
            self.end_plane()
        if self.plane >= len(self.planes):
            fail("output write past final bitplane")
        plane = self.planes[self.plane]
        if self.cursor + 2 > self.virtual_size:
            self.end_plane()
            if self.plane >= len(self.planes):
                fail("output write past final bitplane")
            plane = self.planes[self.plane]
        virtual_row = self.cursor // self.rowbytes
        col = self.cursor % self.rowbytes
        actual_row = self.first_line + virtual_row
        if actual_row < self.height and col + 1 < self.rowbytes:
            off = actual_row * self.rowbytes + col
            plane[off] = (value >> 8) & 0xFF
            plane[off + 1] = value & 0xFF
        self.cursor += 2

    def copy_words(self, reader: WordReader, count: int) -> None:
        for _ in range(count):
            self.write_word(reader.read())

    def repeat_word(self, reader: WordReader, count: int) -> None:
        value = reader.read()
        for _ in range(count):
            self.write_word(value)


def decode_ssa(best: bytes, dast: bytes, planes: list[bytearray], rowbytes: int, height: int, field: int) -> None:
    reader = WordReader(dast)
    writer = PlaneWriter(planes, rowbytes, height, field)
    pos = 0
    while pos < len(best):
        op = best[pos]
        pos += 1
        if op & 1:
            fail(f"invalid odd SSA opcode 0x{op:02x}")
        if op == 0x00:
            writer.end_plane()
        elif op == 0x02:
            if pos >= len(best):
                fail("truncated SSA 0x02 opcode")
            writer.skip((best[pos] + 1) * 2)
            pos += 1
        elif op == 0x04:
            writer.skip(reader.read() * 2)
        elif op in (0x06, 0x08):
            if pos >= len(best):
                fail("truncated SSA copy opcode")
            count = best[pos] * 2 + (2 if op == 0x06 else 3)
            pos += 1
            writer.copy_words(reader, count)
        elif op in (0x0A, 0x0C):
            if pos >= len(best):
                fail("truncated SSA repeat opcode")
            count = best[pos] * 2 + (2 if op == 0x0A else 3)
            pos += 1
            writer.repeat_word(reader, count)
        elif 0x0E <= op <= 0x1C:
            writer.copy_words(reader, ((op - 0x0E) // 2) + 1)
        elif 0x1E <= op <= 0x2A:
            writer.repeat_word(reader, ((op - 0x1E) // 2) + 2)
        elif 0x2C <= op <= 0x3A:
            writer.skip((((op - 0x2C) // 2) + 1) * 2)
        elif 0x3C <= op <= 0x9C:
            if pos >= len(best):
                fail("truncated SSA skip-copy opcode")
            writer.skip(best[pos])
            pos += 1
            writer.copy_words(reader, ((op - 0x3C) // 2) + 1)
        elif 0x9E <= op <= 0xDC:
            if pos >= len(best):
                fail("truncated SSA skip-repeat opcode")
            writer.skip(best[pos])
            pos += 1
            writer.repeat_word(reader, ((op - 0x9E) // 2) + 1)
        else:
            fail(f"unsupported SSA opcode 0x{op:02x}")
    if not reader.done():
        fail("unused DAST data after SSA decode")


def decode_rle(best: bytes, dast: bytes, planes: list[bytearray], rowbytes: int, height: int, field: int) -> None:
    reader = WordReader(dast)
    writer = PlaneWriter(planes, rowbytes, height, field)
    pos = 0
    while pos < len(best):
        op = best[pos]
        pos += 1
        if op == 0x00:
            if reader.pos + 2 <= len(reader.data):
                skip = u16be(reader.data, reader.pos)
                remaining = len(writer.planes[writer.plane]) - writer.cursor if writer.plane < len(writer.planes) else -1
                if skip == 0 or 0 < skip <= remaining:
                    reader.pos += 2
                    if skip == 0:
                        writer.end_plane()
                    else:
                        writer.skip(skip)
                else:
                    writer.end_plane()
            else:
                writer.end_plane()
        elif 0x01 <= op <= 0xEF:
            skip = best[pos] if pos < len(best) else 0
            if pos < len(best):
                pos += 1
            writer.skip(skip)
            writer.copy_words(reader, op)
        elif 0xF0 <= op <= 0xFF:
            skip = best[pos] if pos < len(best) else 0
            if pos < len(best):
                pos += 1
            writer.skip(skip)
            writer.repeat_word(reader, 256 - op)
        else:
            fail(f"unsupported RLE opcode 0x{op:02x}")


def parse_cost(cost: bytes, palette: list[tuple[int, int, int]]) -> None:
    pos = 0
    while pos < len(cost):
        if pos + 2 > len(cost):
            fail("truncated COST block header")
        table_tag = cost[pos]
        count = cost[pos + 1] + 1
        if table_tag != 2:
            fail("unsupported COST table tag")
        pos += 2
        for _ in range(count):
            if pos + 6 > len(cost):
                fail("truncated COST entry")
            index = u16be(cost, pos)
            unused = cost[pos + 2]
            if unused != 0:
                fail("non-zero COST colour high byte")
            if index >= len(palette):
                fail("palette index out of range")
            palette[index] = (cost[pos + 3], cost[pos + 4], cost[pos + 5])
            pos += 6
    if pos != len(cost):
        fail("unused COST bytes")


def mode_is_ham(mode: int) -> bool:
    return bool(mode & 0x0800)


def build_palette_array(palette: list[tuple[int, int, int]], planes: int) -> list[tuple[int, int, int]]:
    out = list(palette)
    if planes == 6:
        for idx in range(32, 64):
            if out[idx] == (0, 0, 0):
                r, g, b = out[idx - 32]
                out[idx] = (r // 2, g // 2, b // 2)
    return out


def planes_to_bgr(
    planes: list[bytearray],
    width: int,
    height: int,
    rowbytes: int,
    palette: list[tuple[int, int, int]],
    bitplanes: int,
    mode: int,
) -> bytes:
    try:
        import numpy as np
    except Exception:
        return planes_to_bgr_plain(planes, width, height, rowbytes, palette, bitplanes, mode)

    plane_arr = np.stack(
        [np.frombuffer(planes[i], dtype=np.uint8).reshape(height, rowbytes) for i in range(bitplanes)]
    )
    bits = np.unpackbits(plane_arr, axis=2, bitorder="big")[:, :, :width]
    vals = np.zeros((height, width), dtype=np.uint16)
    for bit in range(bitplanes):
        vals |= (bits[bit].astype(np.uint16) << bit)

    pal = build_palette_array(palette, bitplanes)
    if mode_is_ham(mode) and bitplanes in (6, 8):
        rgb = np.empty((height, width, 3), dtype=np.uint8)
        data_bits = 4 if bitplanes == 6 else 6
        direct_count = 1 << data_bits
        for y in range(height):
            last = [0, 0, 0]
            for x in range(width):
                val = int(vals[y, x])
                command = val >> data_bits
                data_val = val & (direct_count - 1)
                if command == 0:
                    last = list(pal[data_val])
                else:
                    comp = data_val * 17 if bitplanes == 6 else ((data_val << 2) | (data_val >> 4))
                    if command == 1:
                        last[2] = comp
                    elif command == 2:
                        last[0] = comp
                    else:
                        last[1] = comp
                rgb[y, x] = last
        bgr = rgb[:, :, ::-1]
    else:
        pal_np = np.array(pal, dtype=np.uint8)
        bgr = pal_np[vals][:, :, ::-1]
    return bgr.tobytes()


def planes_to_bgr_plain(
    planes: list[bytearray],
    width: int,
    height: int,
    rowbytes: int,
    palette: list[tuple[int, int, int]],
    bitplanes: int,
    mode: int,
) -> bytes:
    pal = build_palette_array(palette, bitplanes)
    out = bytearray(width * height * 3)
    ham = mode_is_ham(mode) and bitplanes in (6, 8)
    data_bits = 4 if bitplanes == 6 else 6
    data_mask = (1 << data_bits) - 1
    for y in range(height):
        last = [0, 0, 0]
        for x in range(width):
            byte_off = y * rowbytes + (x >> 3)
            mask = 0x80 >> (x & 7)
            val = 0
            for bit in range(bitplanes):
                if planes[bit][byte_off] & mask:
                    val |= 1 << bit
            if ham:
                command = val >> data_bits
                data_val = val & data_mask
                if command == 0:
                    last = list(pal[data_val])
                else:
                    comp = data_val * 17 if bitplanes == 6 else ((data_val << 2) | (data_val >> 4))
                    if command == 1:
                        last[2] = comp
                    elif command == 2:
                        last[0] = comp
                    else:
                        last[1] = comp
                r, g, b = last
            else:
                r, g, b = pal[val]
            off = (y * width + x) * 3
            out[off : off + 3] = bytes((b, g, r))
    return bytes(out)


def field_to_progressive_bgr(frame_data: bytes, width: int, height: int, field_code: int) -> bytes:
    if height < 2:
        return frame_data
    try:
        import numpy as np
    except Exception:
        return frame_data

    arr = np.frombuffer(frame_data, dtype=np.uint8).reshape(height, width, 3)
    if field_code == 1:
        chosen = arr[0::2]
    elif field_code == 2:
        chosen = arr[1::2]
    else:
        return frame_data
    doubled = np.repeat(chosen, 2, axis=0)
    if doubled.shape[0] < height:
        doubled = np.concatenate([doubled, doubled[-1:]], axis=0)
    return doubled[:height].copy().tobytes()


def avi_write_header(f, width: int, height: int, frame_count: int, frame_size: int) -> dict[str, int]:
    positions: dict[str, int] = {}

    def chunk(tag: bytes, payload: bytes) -> None:
        f.write(tag)
        f.write(struct.pack("<I", len(payload)))
        f.write(payload)
        if len(payload) & 1:
            f.write(b"\0")

    def list_start(kind: bytes) -> int:
        f.write(b"LIST")
        pos = f.tell()
        f.write(b"\0\0\0\0")
        f.write(kind)
        return pos

    def list_end(pos: int) -> None:
        end = f.tell()
        f.seek(pos)
        f.write(struct.pack("<I", end - pos - 4))
        f.seek(end)

    f.write(b"RIFF")
    positions["riff_size"] = f.tell()
    f.write(b"\0\0\0\0AVI ")

    hdrl = list_start(b"hdrl")
    avih = struct.pack(
        "<IIIIIIIIIIIIII",
        1_000_000 // FPS,
        frame_size * FPS,
        0,
        0x10,
        frame_count,
        0,
        1,
        frame_size,
        width,
        height,
        0,
        0,
        0,
        0,
    )
    chunk(b"avih", avih)

    strl = list_start(b"strl")
    strh = struct.pack(
        "<4s4sIHHIIIIIIIIhhhh",
        b"vids",
        b"DIB ",
        0,
        0,
        0,
        0,
        1,
        FPS,
        0,
        frame_count,
        frame_size,
        0xFFFFFFFF,
        0,
        0,
        0,
        width,
        height,
    )
    chunk(b"strh", strh)
    strf = struct.pack(
        "<IiiHHIIiiII",
        40,
        width,
        -height,
        1,
        24,
        0,
        frame_size,
        0,
        0,
        0,
        0,
    )
    chunk(b"strf", strf)
    list_end(strl)
    list_end(hdrl)

    positions["movi_list_start"] = f.tell()
    movi_size_pos = list_start(b"movi")
    positions["movi_size"] = movi_size_pos
    positions["movi_data_start"] = f.tell()
    return positions


def avi_finish(f, positions: dict[str, int], index: list[tuple[int, int]]) -> None:
    idx_payload = bytearray()
    for offset, size in index:
        idx_payload += struct.pack("<4sIII", b"00db", 0x10, offset, size)
    f.write(b"idx1")
    f.write(struct.pack("<I", len(idx_payload)))
    f.write(idx_payload)
    if len(idx_payload) & 1:
        f.write(b"\0")

    end = f.tell()
    f.seek(positions["movi_size"])
    f.write(struct.pack("<I", end - positions["movi_size"] - 4 - (8 + len(idx_payload))))
    f.seek(positions["riff_size"])
    f.write(struct.pack("<I", end - 8))
    f.seek(end)


def convert(input_path: Path, output_path: Path) -> None:
    anim = parse_animation(input_path)
    rowbytes = ((anim.width + 15) // 16) * 2
    plane_size = rowbytes * anim.height
    frame_buffers = [[bytearray(plane_size) for _ in range(anim.planes)] for _ in range(2)]
    display_buffer = 0
    palette: list[tuple[int, int, int]] = [(0, 0, 0)] * 256
    frame_size = anim.width * anim.height * 3

    temp_path = output_path.with_name(output_path.name + ".tmp")
    if temp_path.exists():
        temp_path.unlink()

    written = 0
    with temp_path.open("wb") as f:
        positions = avi_write_header(f, anim.width, anim.height, anim.frame_count, frame_size)
        index: list[tuple[int, int]] = []
        for frame in anim.frames:
            method = frame.dscr[0]
            if frame.lower_dscr is not None:
                method = 0
            if method not in (0, 1, 3):
                fail(f"unsupported frame coding method {method}")
            if frame.cost is not None:
                parse_cost(frame.cost, palette)

            has_image = frame.best is not None or frame.dast is not None
            if has_image:
                if frame.best is None:
                    fail("image frame has DAST without BEST")
                if frame.dast is None:
                    frame_dast = b""
                else:
                    frame_dast = frame.dast
                buffer_mask = frame.dscr[1] & 0x03
                target_buffers = []
                if buffer_mask & 0x01:
                    target_buffers.append(0)
                if buffer_mask & 0x02:
                    target_buffers.append(1)
                if not target_buffers:
                    fail("image frame does not select a display buffer")
                if method == 1:
                    for target in target_buffers:
                        decode_ssa(frame.best, frame_dast, frame_buffers[target], rowbytes, anim.height, frame.dscr[1])
                else:
                    for target in target_buffers:
                        decode_rle(frame.best, frame_dast, frame_buffers[target], rowbytes, anim.height, frame.dscr[1])
                display_buffer = target_buffers[0]

            planes = frame_buffers[display_buffer]
            frame_data = planes_to_bgr(planes, anim.width, anim.height, rowbytes, palette, anim.planes, anim.mode)
            if (frame.dscr[1] & 0x03) in (1, 2):
                frame_data = field_to_progressive_bgr(frame_data, anim.width, anim.height, frame.dscr[1] & 0x03)
            chunk_start = f.tell()
            f.write(b"00db")
            f.write(struct.pack("<I", len(frame_data)))
            f.write(frame_data)
            if len(frame_data) & 1:
                f.write(b"\0")
            index.append((chunk_start - positions["movi_data_start"], len(frame_data)))
            written += 1
        if written != anim.frame_count:
            fail("internal frame count mismatch")
        avi_finish(f, positions, index)

    os.chmod(temp_path, 0o664)
    os.replace(temp_path, output_path)
    os.chmod(output_path, 0o664)


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: iffSSA.py <inputFile> <outputFile>", file=sys.stderr)
        return 2
    input_path = Path(argv[1])
    output_path = Path(argv[2])
    try:
        if output_path.exists():
            output_path.unlink()
        convert(input_path, output_path)
        return 0
    except Exception as exc:
        temp_path = output_path.with_name(output_path.name + ".tmp")
        try:
            if output_path.exists():
                output_path.unlink()
            if temp_path.exists():
                temp_path.unlink()
        except OSError:
            pass
        print(f"iffSSA: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

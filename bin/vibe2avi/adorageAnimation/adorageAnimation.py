#!/usr/bin/env python3
# Vibe coded by Codex
import os
import struct
import sys


MAGIC = b"FEE_Anim_V1.0"

COPY_WORDS = {
    0x14: 1, 0x18: 2, 0x1C: 3,
    0x34: 4, 0x38: 5, 0x3C: 6, 0x40: 7, 0x44: 8, 0x48: 9,
    0x6C: 10, 0x74: 11, 0x7C: 12, 0x84: 13,
    0x8C: 14, 0x94: 15, 0x9C: 16,
}

REPEAT_WORDS = {
    0x14: 1,
    0x4C: 2, 0x50: 3, 0x54: 4, 0x58: 5, 0x5C: 6, 0x60: 7,
    0x64: 8, 0x68: 9, 0x70: 10, 0x78: 11, 0x80: 12,
    0x88: 13, 0x90: 14, 0x98: 15, 0xA0: 16,
}


class FormatError(Exception):
    pass


def be16(buf, off):
    if off + 2 > len(buf):
        raise FormatError("unexpected EOF reading u16")
    return int.from_bytes(buf[off:off + 2], "big")


def be32(buf, off):
    if off + 4 > len(buf):
        raise FormatError("unexpected EOF reading u32")
    return int.from_bytes(buf[off:off + 4], "big")


def read_block(buf, off, name):
    size = be16(buf, off)
    off += 2
    end = off + size
    if end > len(buf):
        raise FormatError(f"{name} block exceeds file")
    return buf[off:end], end


def parse_file(buf):
    magic, off = read_block(buf, 0, "magic")
    if magic != MAGIC:
        raise FormatError("not an Adorage FEE animation")
    fmt, off = read_block(buf, off, "format")
    if len(fmt) != 14:
        raise FormatError(f"unsupported format block length {len(fmt)}")
    display_w = be16(fmt, 0)
    display_h = be16(fmt, 2)
    if fmt[4] != 0 or fmt[10] != 0:
        raise FormatError("reserved dimension separator is non-zero")
    depth = fmt[5]
    coded_w = be16(fmt, 6)
    coded_h = be16(fmt, 8)
    if not (1 <= depth <= 8):
        raise FormatError(f"unsupported bit depth {depth}")
    if display_w < 1 or display_h < 1 or coded_w < display_w or coded_h < display_h:
        raise FormatError("invalid display/coded dimensions")

    pal_block, off = read_block(buf, off, "palette")
    expected_pal_len = 1 + (1 << depth) * 3
    if len(pal_block) != expected_pal_len:
        raise FormatError(f"palette block length {len(pal_block)} != {expected_pal_len}")
    if pal_block[0] != depth:
        raise FormatError("palette bit depth does not match format block")
    palette = [tuple(pal_block[1 + i * 3:1 + i * 3 + 3]) for i in range(1 << depth)]

    if off + 24 > len(buf):
        raise FormatError("missing stream header")
    stream_header = [be32(buf, off + i * 4) for i in range(6)]
    off += 24
    frame_count = stream_header[2]
    chunk_count = stream_header[3]
    if frame_count < 1 or chunk_count < 1:
        raise FormatError("empty animation")
    if stream_header[5] != 1:
        raise FormatError("unsupported stream header version")

    chunks = []
    for _ in range(chunk_count):
        if off + 4 > len(buf):
            raise FormatError("truncated chunk table")
        size = be32(buf, off)
        off += 4
        end = off + size
        if end > len(buf):
            raise FormatError("chunk exceeds file")
        chunks.append(buf[off:end])
        off = end
    if off != len(buf):
        raise FormatError("trailing bytes after final chunk")

    plane_chunks = sum(1 for c in chunks if len(c) != 16)
    repeat_frames = sum(1 for c in chunks if len(c) == 16)
    if any(len(c) < 12 for c in chunks):
        raise FormatError("chunk smaller than minimum payload")
    if plane_chunks % depth:
        raise FormatError("plane chunk count is not divisible by bit depth")
    derived_frames = plane_chunks // depth + repeat_frames
    if derived_frames != frame_count:
        raise FormatError(f"derived frame count {derived_frames} != header {frame_count}")

    return {
        "display_w": display_w, "display_h": display_h,
        "coded_w": coded_w, "coded_h": coded_h,
        "depth": depth, "palette": palette,
        "stream_header": stream_header, "chunks": chunks,
        "frame_count": frame_count,
    }


def write_plane(plane, pos, data):
    if pos < 0 or pos + len(data) > len(plane):
        raise FormatError("RLE write outside bitplane")
    plane[pos:pos + len(data)] = data


def decode_rle(payload, plane):
    s = payload[10:]
    off = 0
    while True:
        if off + 2 > len(s):
            raise FormatError("RLE stream has no terminator")
        op = s[off]
        count = s[off + 1]
        off += 2
        if op == 0x00:
            if count != 0:
                raise FormatError("invalid RLE terminator count")
            if off != len(s):
                raise FormatError("trailing bytes after RLE terminator")
            return

        reps = count + 1
        if op in COPY_WORDS:
            words = COPY_WORDS[op]
            pos = 0
            for idx in range(reps):
                skip = be16(s, off)
                off += 2
                pos = skip if idx == 0 else pos + skip
                nbytes = words * 2
                if off + nbytes > len(s):
                    raise FormatError("truncated copy opcode")
                write_plane(plane, pos, s[off:off + nbytes])
                off += nbytes
                pos += nbytes
        elif op in REPEAT_WORDS:
            words = REPEAT_WORDS[op]
            pos = 0
            for idx in range(reps):
                skip = be16(s, off)
                off += 2
                pos = skip if idx == 0 else pos + skip
                if off + 2 > len(s):
                    raise FormatError("truncated repeat opcode")
                word = s[off:off + 2]
                off += 2
                data = word * words
                write_plane(plane, pos, data)
                pos += len(data)
        elif op in (0x04, 0x0C):
            extra_words = 2 if op == 0x04 else 3
            pos = 0
            for idx in range(reps):
                skip = be16(s, off)
                off += 2
                pos = skip if idx == 0 else pos + skip
                if off + 2 > len(s):
                    raise FormatError("truncated double-copy lengths")
                len_a = s[off] * 2 + extra_words
                len_b = s[off + 1] * 2 + extra_words
                off += 2
                nbytes = len_a * 2
                if off + nbytes > len(s):
                    raise FormatError("truncated first double-copy run")
                write_plane(plane, pos, s[off:off + nbytes])
                off += nbytes
                pos += nbytes
                skip = be16(s, off)
                off += 2
                pos += skip
                nbytes = len_b * 2
                if off + nbytes > len(s):
                    raise FormatError("truncated second double-copy run")
                write_plane(plane, pos, s[off:off + nbytes])
                off += nbytes
                pos += nbytes
        elif op in (0x08, 0x10):
            extra_words = 2 if op == 0x08 else 3
            pos = 0
            for idx in range(reps):
                skip = be16(s, off)
                off += 2
                pos = skip if idx == 0 else pos + skip
                if off + 6 > len(s):
                    raise FormatError("truncated first double-repeat run")
                len_a = s[off] * 2 + extra_words
                len_b = s[off + 1] * 2 + extra_words
                off += 2
                word_a = s[off:off + 2]
                word_b = s[off + 2:off + 4]
                off += 4
                data = (word_a + word_b) * (len_a // 2) + (word_a if len_a & 1 else b"")
                write_plane(plane, pos, data)
                pos += len(data)
                skip = be16(s, off)
                off += 2
                pos += skip
                if off + 4 > len(s):
                    raise FormatError("truncated second double-repeat run")
                word_a = s[off:off + 2]
                word_b = s[off + 2:off + 4]
                off += 4
                data = (word_a + word_b) * (len_b // 2) + (word_a if len_b & 1 else b"")
                write_plane(plane, pos, data)
                pos += len(data)
        elif op in (0x20, 0x24, 0x2C):
            pos = be16(s, off)
            off += 2
            nbytes = (count + 1) * 4 + (2 if op == 0x2C else 0)
            if off + nbytes > len(s):
                raise FormatError("truncated singular copy")
            write_plane(plane, pos, s[off:off + nbytes])
            off += nbytes
        elif op in (0x28, 0x30):
            pos = be16(s, off)
            off += 2
            if off + 4 > len(s):
                raise FormatError("truncated pair repeat")
            pair = s[off:off + 4]
            off += 4
            write_plane(plane, pos, pair * (count + 1))
        else:
            raise FormatError(f"unknown RLE opcode 0x{op:02X}")


class AviWriter:
    def __init__(self, path, width, height, frames, fps=25):
        self.path = path
        self.width = width
        self.height = height
        self.frames = frames
        self.fps = fps
        self.stride = ((width * 3 + 3) // 4) * 4
        self.image_size = self.stride * height
        self.movi_start = None
        self.index = []
        self.fp = open(path, "wb")
        self._write_header_placeholder()

    def _write_header_placeholder(self):
        w, h, fps, frames = self.width, self.height, self.fps, self.frames
        microsec = int(1000000 / fps)
        avih = struct.pack(
            "<IIIIIIIIIIIIII",
            microsec, self.image_size * fps, 0, 0x10, frames, 0, 1,
            self.image_size, w, h, 0, 0, 0, 0,
        )
        strh = struct.pack(
            "<4s4sIHHIIIIIIIIiiii",
            b"vids", b"DIB ", 0, 0, 0, 0, 1, fps, 0, frames,
            self.image_size, 0xFFFFFFFF, 0, 0, 0, w, h,
        )
        strf = struct.pack(
            "<IiiHHIIiiII",
            40, w, -h, 1, 24, 0, self.image_size, 0, 0, 0, 0,
        )
        hdrl_data = (
            self._chunk(b"avih", avih) +
            self._list(b"strl", self._chunk(b"strh", strh) + self._chunk(b"strf", strf))
        )
        self.fp.write(b"RIFF\0\0\0\0AVI ")
        self.fp.write(self._list(b"hdrl", hdrl_data))
        self.movi_start = self.fp.tell()
        self.fp.write(b"LIST\0\0\0\0movi")

    @staticmethod
    def _chunk(tag, data):
        return tag + struct.pack("<I", len(data)) + data + (b"\0" if len(data) & 1 else b"")

    @staticmethod
    def _list(tag, data):
        return b"LIST" + struct.pack("<I", len(data) + 4) + tag + data

    def write_frame(self, data):
        if len(data) != self.image_size:
            raise FormatError("internal AVI frame size mismatch")
        chunk_start = self.fp.tell()
        self.fp.write(b"00db")
        self.fp.write(struct.pack("<I", len(data)))
        self.fp.write(data)
        if len(data) & 1:
            self.fp.write(b"\0")
        self.index.append((chunk_start - (self.movi_start + 8), len(data)))

    def close(self):
        idx = bytearray()
        for offset, size in self.index:
            idx += struct.pack("<4sIII", b"00db", 0x10, offset, size)
        self.fp.write(b"idx1")
        self.fp.write(struct.pack("<I", len(idx)))
        self.fp.write(idx)
        file_size = self.fp.tell()
        self.fp.seek(4)
        self.fp.write(struct.pack("<I", file_size - 8))
        self.fp.seek(self.movi_start + 4)
        movi_size = file_size - self.movi_start - 8 - len(idx) - 8
        self.fp.write(struct.pack("<I", movi_size))
        self.fp.close()


def planes_to_bgr(planes, meta, writer):
    w = meta["display_w"]
    h = meta["display_h"]
    coded_w = meta["coded_w"]
    depth = meta["depth"]
    palette = meta["palette"]
    row_bytes = ((coded_w + 15) // 16) * 2
    out = bytearray()
    for y in range(h):
        row_start = y * row_bytes
        row = bytearray()
        for xb in range((w + 7) // 8):
            vals = [plane[row_start + xb] for plane in planes]
            for bit in range(8):
                x = xb * 8 + bit
                if x >= w:
                    break
                mask = 0x80 >> bit
                idx = 0
                for p, value in enumerate(vals):
                    if value & mask:
                        idx |= 1 << p
                r, g, b = palette[idx]
                row.extend((b, g, r))
        row.extend(b"\0" * (writer.stride - len(row)))
        out.extend(row)
    writer.write_frame(bytes(out))


def convert(input_path, output_path):
    with open(input_path, "rb") as f:
        meta = parse_file(f.read())
    row_bytes = ((meta["coded_w"] + 15) // 16) * 2
    plane_size = row_bytes * meta["coded_h"]
    planes = [bytearray(plane_size) for _ in range(meta["depth"])]
    writer = AviWriter(output_path, meta["display_w"], meta["display_h"], meta["frame_count"])
    plane_index = 0
    frames_written = 0
    try:
        for chunk_no, chunk in enumerate(meta["chunks"]):
            if len(chunk) == 16:
                if chunk[:10] != b"\0" * 10 or chunk[10] != 0x20 or chunk[11] != 0:
                    raise FormatError(f"unsupported repeat-frame chunk at {chunk_no}")
                planes_to_bgr(planes, meta, writer)
                frames_written += 1
                continue
            if len(chunk) == 12:
                if chunk[4:] != b"\0" * 8:
                    raise FormatError(f"unsupported skip-plane chunk at {chunk_no}")
            else:
                if len(chunk) < 18:
                    raise FormatError(f"compressed chunk {chunk_no} too short")
                if chunk[4:10] != b"\0" * 6:
                    raise FormatError(f"compressed chunk {chunk_no} has non-zero loader fields")
                decode_rle(chunk, planes[plane_index])
            plane_index += 1
            if plane_index == meta["depth"]:
                plane_index = 0
                planes_to_bgr(planes, meta, writer)
                frames_written += 1
        if frames_written != meta["frame_count"]:
            raise FormatError(f"wrote {frames_written} frames, expected {meta['frame_count']}")
    except Exception:
        writer.fp.close()
        try:
            os.unlink(output_path)
        except FileNotFoundError:
            pass
        raise
    writer.close()


def main(argv):
    if len(argv) != 3:
        print("usage: adorageAnimation.py <inputFile> <outputFile>", file=sys.stderr)
        return 2
    try:
        convert(argv[1], argv[2])
        os.chmod(argv[2], 0o664)
        return 0
    except FormatError as exc:
        print(f"error: {exc}", file=sys.stderr)
        try:
            os.unlink(argv[2])
        except FileNotFoundError:
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

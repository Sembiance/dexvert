#!/usr/bin/env python3
# Vibe coded by Codex
import os
import struct
import sys
from dataclasses import dataclass
from pathlib import Path


class VaxlError(Exception):
    pass


@dataclass(frozen=True)
class Frame:
    palette: tuple
    bmap: bytes
    samp: bytes


@dataclass(frozen=True)
class VaxlFile:
    width: int
    height: int
    planes: int
    sample_rate: int
    samples_per_frame: int
    frames: tuple
    vxhd_size: int
    cols_size: int


def be16(data, offset):
    return int.from_bytes(data[offset:offset + 2], "big")


def be32(data, offset):
    return int.from_bytes(data[offset:offset + 4], "big")


def le_chunk(fourcc, payload):
    if len(fourcc) != 4:
        raise ValueError("fourcc must be four bytes")
    pad = b"\0" if len(payload) & 1 else b""
    return fourcc + struct.pack("<I", len(payload)) + payload + pad


def avi_list(list_type, payload):
    return le_chunk(b"LIST", list_type + payload)


def require(condition, message):
    if not condition:
        raise VaxlError(message)


def read_chunk(data, offset):
    require(offset + 8 <= len(data), f"truncated chunk header at 0x{offset:x}")
    chunk_id = data[offset:offset + 4]
    size = be32(data, offset + 4)
    payload_start = offset + 8
    payload_end = payload_start + size
    require(payload_end <= len(data), f"chunk {chunk_id!r} at 0x{offset:x} overruns file")
    next_offset = payload_end
    if size & 1:
        require(next_offset < len(data), f"missing IFF pad byte after {chunk_id!r}")
        require(data[next_offset] == 0, f"non-zero IFF pad byte after {chunk_id!r}")
        next_offset += 1
    return chunk_id, data[payload_start:payload_end], next_offset, payload_end


def parse_palette(payload):
    require(len(payload) in (32, 64), f"unsupported COLS size {len(payload)}")
    colors = []
    for offset in range(0, len(payload), 2):
        word = be16(payload, offset)
        require((word & 0xf000) == 0, f"COLS word {offset // 2} has non-RGB4 high bits")
        colors.append((
            ((word >> 8) & 0x0f) * 17,
            ((word >> 4) & 0x0f) * 17,
            (word & 0x0f) * 17,
        ))
    require(len(colors) >= 16, "HAM6 decoding requires at least 16 base colors")
    return tuple(colors)


def validate_pad(chunk_id, payload, payload_end, what):
    require(chunk_id == b"PAD0", f"expected {what} PAD0, got {chunk_id!r}")
    require(all(byte == 0 for byte in payload), f"{what} PAD0 contains non-zero bytes")
    require(payload_end % 512 == 0, f"{what} PAD0 does not end on a 512-byte boundary")


def parse_vaxl(path):
    data = Path(path).read_bytes()
    require(len(data) >= 512, "file is too small for a VAXL stream")
    require(data[:4] == b"FORM", "missing FORM signature")
    require(data[8:12] == b"VAXL", "FORM type is not VAXL")
    require(be32(data, 4) == len(data) - 8, "FORM size does not match file length")

    offset = 12
    chunk_id, vxhd, offset, payload_end = read_chunk(data, offset)
    require(chunk_id == b"VXHD", f"expected VXHD, got {chunk_id!r}")
    require(len(vxhd) in (28, 30), f"unsupported VXHD size {len(vxhd)}")

    width = be16(vxhd, 8)
    height = be16(vxhd, 10)
    planes = be16(vxhd, 12)
    require(width == 144 and height == 103, f"unsupported frame size {width}x{height}")
    require(planes == 6, f"unsupported bitplane count {planes}")
    require(be16(vxhd, 14) == 0, "unsupported VXHD plane flags")
    require(be16(vxhd, 16) == 0x0800 and be16(vxhd, 18) == 0, "unsupported VXHD HAM marker")
    sample_rate = be16(vxhd, 20)
    require(sample_rate > 0, "VXHD sample rate is zero")

    if len(vxhd) == 28:
        require(vxhd[:8] == b"\0" * 8, "unsupported 28-byte VXHD prefix")
        require(vxhd[22:28] == b"\0\0\0@\0\7", "unsupported 28-byte VXHD suffix")
        cols_size = 64
    else:
        require(vxhd[:2] == b"\0\0" and be16(vxhd, 2) == 1, "unsupported 30-byte VXHD prefix")
        require(vxhd[22:30] == b"\0@\0\7\0\0\x32\0", "unsupported 30-byte VXHD suffix")
        cols_size = 32

    chunk_id, payload, offset, payload_end = read_chunk(data, offset)
    validate_pad(chunk_id, payload, payload_end, "initial")

    row_bytes = ((width + 15) // 16) * 2
    bmap_size = row_bytes * height * planes
    frames = []
    samples_per_frame = None

    while offset < len(data):
        chunk_id, tmcd, offset, _ = read_chunk(data, offset)
        require(chunk_id == b"TMCD", f"expected TMCD at frame {len(frames)}, got {chunk_id!r}")
        require(tmcd == b"\0\0\0\0\0\0\0\5", f"unsupported TMCD payload at frame {len(frames)}")

        chunk_id, cols_payload, offset, _ = read_chunk(data, offset)
        require(chunk_id == b"COLS", f"expected COLS at frame {len(frames)}, got {chunk_id!r}")
        require(len(cols_payload) == cols_size, f"unexpected COLS size at frame {len(frames)}")
        palette = parse_palette(cols_payload)

        chunk_id, bmap, offset, _ = read_chunk(data, offset)
        require(chunk_id == b"BMAP", f"expected BMAP at frame {len(frames)}, got {chunk_id!r}")
        require(len(bmap) == bmap_size, f"unexpected BMAP size at frame {len(frames)}")

        chunk_id, samp, offset, _ = read_chunk(data, offset)
        require(chunk_id == b"SAMP", f"expected SAMP at frame {len(frames)}, got {chunk_id!r}")
        require(len(samp) > 0, f"empty SAMP at frame {len(frames)}")
        if samples_per_frame is None:
            samples_per_frame = len(samp)
        require(len(samp) == samples_per_frame, f"SAMP size changed at frame {len(frames)}")
        frames.append(Frame(palette, bmap, samp))

        if offset == len(data):
            break
        chunk_id, payload, offset, payload_end = read_chunk(data, offset)
        validate_pad(chunk_id, payload, payload_end, f"frame {len(frames) - 1}")

    require(frames, "file contains no complete frames")
    return VaxlFile(width, height, planes, sample_rate, samples_per_frame, tuple(frames), len(vxhd), cols_size)


BIT_VALUES = [
    tuple(((byte >> (7 - bit)) & 1) << plane for bit in range(8))
    for plane in range(6)
    for byte in range(256)
]


def plane_bits(plane, byte):
    return BIT_VALUES[plane * 256 + byte]


def decode_ham6_to_bgr(vaxl, frame):
    width = vaxl.width
    height = vaxl.height
    planes = vaxl.planes
    row_bytes = ((width + 15) // 16) * 2
    bmp_stride = ((width * 3 + 3) // 4) * 4
    out = bytearray(bmp_stride * height)
    palette = frame.palette
    bmap = frame.bmap

    for source_y in range(height):
        dest = (height - 1 - source_y) * bmp_stride
        current_r, current_g, current_b = palette[0]
        for byte_x in range(row_bytes):
            plane_offsets = [(plane * height + source_y) * row_bytes + byte_x for plane in range(planes)]
            parts = [plane_bits(plane, bmap[plane_offsets[plane]]) for plane in range(planes)]
            for bit in range(8):
                x = byte_x * 8 + bit
                if x >= width:
                    break
                code = parts[0][bit] | parts[1][bit] | parts[2][bit] | parts[3][bit] | parts[4][bit] | parts[5][bit]
                command = code >> 4
                value = (code & 0x0f) * 17
                if command == 0:
                    current_r, current_g, current_b = palette[code & 0x0f]
                elif command == 1:
                    current_b = value
                elif command == 2:
                    current_r = value
                else:
                    current_g = value
                out[dest:dest + 3] = bytes((current_b, current_g, current_r))
                dest += 3
    return bytes(out)


def riff_header(vaxl, frame_size, audio_size):
    frames = len(vaxl.frames)
    fps_scale = 5
    fps_rate = 60
    video_rate_bytes = frame_size * fps_rate // fps_scale
    max_bytes_per_sec = video_rate_bytes + vaxl.sample_rate

    avih = struct.pack(
        "<IIIIIIIIIIIIII",
        1_000_000 * fps_scale // fps_rate,
        max_bytes_per_sec,
        0,
        0x10,
        frames,
        0,
        2,
        max(frame_size, vaxl.samples_per_frame),
        vaxl.width,
        vaxl.height,
        0,
        0,
        0,
        0,
    )

    vstrh = struct.pack(
        "<4s4sIHHIIIIIIIIhhhh",
        b"vids",
        b"DIB ",
        0,
        0,
        0,
        0,
        fps_scale,
        fps_rate,
        0,
        frames,
        frame_size,
        0xffffffff,
        0,
        0,
        0,
        vaxl.width,
        vaxl.height,
    )
    vstrf = struct.pack(
        "<IiiHHIIiiII",
        40,
        vaxl.width,
        vaxl.height,
        1,
        24,
        0,
        frame_size,
        0,
        0,
        0,
        0,
    )
    video_strl = avi_list(b"strl", le_chunk(b"strh", vstrh) + le_chunk(b"strf", vstrf))

    astrh = struct.pack(
        "<4s4sIHHIIIIIIIIhhhh",
        b"auds",
        b"\0\0\0\0",
        0,
        0,
        0,
        0,
        1,
        vaxl.sample_rate,
        0,
        audio_size,
        vaxl.samples_per_frame,
        0xffffffff,
        1,
        0,
        0,
        0,
        0,
    )
    astrf = struct.pack("<HHIIHH", 1, 1, vaxl.sample_rate, vaxl.sample_rate, 1, 8)
    audio_strl = avi_list(b"strl", le_chunk(b"strh", astrh) + le_chunk(b"strf", astrf))

    return avi_list(b"hdrl", le_chunk(b"avih", avih) + video_strl + audio_strl)


def signed_to_unsigned_pcm(payload):
    return bytes((byte ^ 0x80) for byte in payload)


def write_avi(vaxl, output_path):
    bmp_stride = ((vaxl.width * 3 + 3) // 4) * 4
    frame_size = bmp_stride * vaxl.height
    audio_size = sum(len(frame.samp) for frame in vaxl.frames)
    hdrl = riff_header(vaxl, frame_size, audio_size)

    movi_data_size = 0
    for frame in vaxl.frames:
        movi_data_size += 8 + frame_size + (frame_size & 1)
        movi_data_size += 8 + len(frame.samp) + (len(frame.samp) & 1)
    idx1_size = len(vaxl.frames) * 2 * 16
    riff_size = 4 + len(hdrl) + 12 + movi_data_size + 8 + idx1_size

    with open(output_path, "wb") as out:
        out.write(b"RIFF")
        out.write(struct.pack("<I", riff_size))
        out.write(b"AVI ")
        out.write(hdrl)
        out.write(b"LIST")
        out.write(struct.pack("<I", 4 + movi_data_size))
        out.write(b"movi")
        movi_start = out.tell()

        index = []
        for frame in vaxl.frames:
            offset = out.tell() - movi_start
            video = decode_ham6_to_bgr(vaxl, frame)
            out.write(b"00db")
            out.write(struct.pack("<I", len(video)))
            out.write(video)
            if len(video) & 1:
                out.write(b"\0")
            index.append((b"00db", 0x10, offset, len(video)))

            offset = out.tell() - movi_start
            audio = signed_to_unsigned_pcm(frame.samp)
            out.write(b"01wb")
            out.write(struct.pack("<I", len(audio)))
            out.write(audio)
            if len(audio) & 1:
                out.write(b"\0")
            index.append((b"01wb", 0, offset, len(audio)))

        out.write(b"idx1")
        out.write(struct.pack("<I", idx1_size))
        for chunk_id, flags, offset, size in index:
            out.write(struct.pack("<4sIII", chunk_id, flags, offset, size))


def convert(input_path, output_path):
    vaxl = parse_vaxl(input_path)
    output = Path(output_path)
    tmp = output.with_name(f".{output.name}.tmp")
    if tmp.exists():
        tmp.unlink()
    try:
        write_avi(vaxl, tmp)
        os.chmod(tmp, 0o664)
        os.replace(tmp, output)
        os.chmod(output, 0o664)
    except Exception:
        if tmp.exists():
            tmp.unlink()
        raise


def main(argv):
    if len(argv) != 3:
        print("usage: iffVAXL.py <inputFile> <outputFile>", file=sys.stderr)
        return 2
    try:
        convert(argv[1], argv[2])
    except VaxlError as exc:
        print(f"iffVAXL: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"iffVAXL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

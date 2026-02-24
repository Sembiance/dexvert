#!/usr/bin/env python3
import struct
import sys
import zlib


CUSTOM_HEADER_SIZE = 20
FORMAT_BC1 = 3
FORMAT_BC3 = 4
MAX_DIMENSION = 16384


def _usage() -> str:
    return "Usage: dds2png.py <inputFile> <outputFile>"


def _rgb565_to_rgb888(value: int) -> tuple[int, int, int]:
    r = (value >> 11) & 0x1F
    g = (value >> 5) & 0x3F
    b = value & 0x1F
    return ((r << 3) | (r >> 2), (g << 2) | (g >> 4), (b << 3) | (b >> 2))


def _lerp8(a: int, b: int, wa: int, wb: int, denom: int) -> int:
    return (a * wa + b * wb) // denom


def _bc1_palette(c0: int, c1: int, allow_transparent: bool) -> list[tuple[int, int, int, int]]:
    r0, g0, b0 = _rgb565_to_rgb888(c0)
    r1, g1, b1 = _rgb565_to_rgb888(c1)

    if c0 > c1 or not allow_transparent:
        c2 = (
            _lerp8(r0, r1, 2, 1, 3),
            _lerp8(g0, g1, 2, 1, 3),
            _lerp8(b0, b1, 2, 1, 3),
            255,
        )
        c3 = (
            _lerp8(r0, r1, 1, 2, 3),
            _lerp8(g0, g1, 1, 2, 3),
            _lerp8(b0, b1, 1, 2, 3),
            255,
        )
    else:
        c2 = (
            _lerp8(r0, r1, 1, 1, 2),
            _lerp8(g0, g1, 1, 1, 2),
            _lerp8(b0, b1, 1, 1, 2),
            255,
        )
        c3 = (0, 0, 0, 0)

    return [(r0, g0, b0, 255), (r1, g1, b1, 255), c2, c3]


def _decode_bc1(data: bytes, width: int, height: int, allow_transparent: bool) -> bytes:
    block_w = (width + 3) // 4
    block_h = (height + 3) // 4
    out = bytearray(width * height * 4)
    offset = 0

    for by in range(block_h):
        for bx in range(block_w):
            if offset + 8 > len(data):
                raise ValueError("BC1 stream ended early")
            c0, c1, indices = struct.unpack_from("<HHI", data, offset)
            offset += 8
            palette = _bc1_palette(c0, c1, allow_transparent)

            for py in range(4):
                y = by * 4 + py
                if y >= height:
                    continue
                for px in range(4):
                    x = bx * 4 + px
                    if x >= width:
                        continue
                    idx = (indices >> (2 * (4 * py + px))) & 0x3
                    r, g, b, a = palette[idx]
                    p = (y * width + x) * 4
                    out[p] = r
                    out[p + 1] = g
                    out[p + 2] = b
                    out[p + 3] = a

    return bytes(out)


def _bc3_alpha_table(a0: int, a1: int) -> list[int]:
    if a0 > a1:
        return [
            a0,
            a1,
            _lerp8(a0, a1, 6, 1, 7),
            _lerp8(a0, a1, 5, 2, 7),
            _lerp8(a0, a1, 4, 3, 7),
            _lerp8(a0, a1, 3, 4, 7),
            _lerp8(a0, a1, 2, 5, 7),
            _lerp8(a0, a1, 1, 6, 7),
        ]

    return [
        a0,
        a1,
        _lerp8(a0, a1, 4, 1, 5),
        _lerp8(a0, a1, 3, 2, 5),
        _lerp8(a0, a1, 2, 3, 5),
        _lerp8(a0, a1, 1, 4, 5),
        0,
        255,
    ]


def _bc3_color_palette(c0: int, c1: int) -> list[tuple[int, int, int]]:
    r0, g0, b0 = _rgb565_to_rgb888(c0)
    r1, g1, b1 = _rgb565_to_rgb888(c1)
    c2 = (
        _lerp8(r0, r1, 2, 1, 3),
        _lerp8(g0, g1, 2, 1, 3),
        _lerp8(b0, b1, 2, 1, 3),
    )
    c3 = (
        _lerp8(r0, r1, 1, 2, 3),
        _lerp8(g0, g1, 1, 2, 3),
        _lerp8(b0, b1, 1, 2, 3),
    )
    return [(r0, g0, b0), (r1, g1, b1), c2, c3]


def _decode_bc3(data: bytes, width: int, height: int) -> bytes:
    block_w = (width + 3) // 4
    block_h = (height + 3) // 4
    out = bytearray(width * height * 4)
    offset = 0

    for by in range(block_h):
        for bx in range(block_w):
            if offset + 16 > len(data):
                raise ValueError("BC3 stream ended early")

            a0 = data[offset]
            a1 = data[offset + 1]
            alpha_bits = int.from_bytes(data[offset + 2 : offset + 8], "little")
            c0, c1, color_bits = struct.unpack_from("<HHI", data, offset + 8)
            offset += 16

            alpha_table = _bc3_alpha_table(a0, a1)
            color_table = _bc3_color_palette(c0, c1)

            for py in range(4):
                y = by * 4 + py
                if y >= height:
                    continue
                for px in range(4):
                    x = bx * 4 + px
                    if x >= width:
                        continue
                    i = 4 * py + px
                    ci = (color_bits >> (2 * i)) & 0x3
                    ai = (alpha_bits >> (3 * i)) & 0x7
                    r, g, b = color_table[ci]
                    a = alpha_table[ai]
                    p = (y * width + x) * 4
                    out[p] = r
                    out[p + 1] = g
                    out[p + 2] = b
                    out[p + 3] = a

    return bytes(out)


def _png_chunk(chunk_type: bytes, payload: bytes) -> bytes:
    crc = zlib.crc32(chunk_type)
    crc = zlib.crc32(payload, crc) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + chunk_type + payload + struct.pack(">I", crc)


def _full_mip_chain_size(width: int, height: int, block_bytes: int) -> int:
    total = 0
    w = width
    h = height
    while True:
        bw = max(1, (w + 3) // 4)
        bh = max(1, (h + 3) // 4)
        total += bw * bh * block_bytes
        if w == 1 and h == 1:
            break
        w = max(1, w >> 1)
        h = max(1, h >> 1)
    return total


def _write_png(path: str, width: int, height: int, rgba: bytes) -> None:
    if len(rgba) != width * height * 4:
        raise ValueError("RGBA buffer has wrong length")

    raw = bytearray()
    stride = width * 4
    # Source textures use bottom-up row order; PNG expects top-down.
    for y in range(height - 1, -1, -1):
        raw.append(0)  # filter method 0
        row_start = y * stride
        raw.extend(rgba[row_start : row_start + stride])

    compressed = zlib.compress(bytes(raw), level=9)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)  # RGBA8

    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(_png_chunk(b"IHDR", ihdr))
        f.write(_png_chunk(b"IDAT", compressed))
        f.write(_png_chunk(b"IEND", b""))


def _parse_custom_texture(data: bytes) -> tuple[int, int, int, bytes]:
    if data.startswith(b"DDS "):
        raise ValueError("Standard DDS detected; this converter only supports the custom sample0 format")
    if len(data) < CUSTOM_HEADER_SIZE:
        raise ValueError("File too small for custom texture header")

    width, height, fmt, top_mip_size, _unknown = struct.unpack_from("<IIIII", data, 0)
    if width == 0 or height == 0:
        raise ValueError("Invalid dimensions in header")
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise ValueError(f"Dimensions too large ({width}x{height}) for this format")
    if fmt not in (FORMAT_BC1, FORMAT_BC3):
        raise ValueError(f"Unsupported format id {fmt}; expected 3 (BC1) or 4 (BC3)")
    if top_mip_size == 0:
        raise ValueError("Invalid top mip size 0")

    expected_top = ((width + 3) // 4) * ((height + 3) // 4) * (8 if fmt == FORMAT_BC1 else 16)
    if top_mip_size != expected_top:
        raise ValueError(
            f"Header top mip size mismatch ({top_mip_size} != expected {expected_top})"
        )

    block_bytes = 8 if fmt == FORMAT_BC1 else 16
    expected_payload_size = _full_mip_chain_size(width, height, block_bytes)
    payload = data[CUSTOM_HEADER_SIZE:]
    if len(payload) != expected_payload_size:
        raise ValueError(
            f"Payload size mismatch ({len(payload)} != expected {expected_payload_size})"
        )

    return width, height, fmt, payload[:top_mip_size]


def convert(input_path: str, output_path: str) -> None:
    with open(input_path, "rb") as f:
        src = f.read()

    width, height, fmt, top_mip = _parse_custom_texture(src)
    if fmt == FORMAT_BC1:
        rgba = _decode_bc1(top_mip, width, height, allow_transparent=True)
    else:
        rgba = _decode_bc3(top_mip, width, height)

    _write_png(output_path, width, height, rgba)


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(_usage(), file=sys.stderr)
        return 2

    input_path = argv[1]
    output_path = argv[2]
    try:
        convert(input_path, output_path)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

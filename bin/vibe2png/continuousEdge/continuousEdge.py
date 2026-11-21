# Vibe coded by Claude
# Vibe coded by Codex
# Continuous Edge Graphics (CEG) to PNG converter
# Decodes Edsun Laboratories CEG bitmap files

import argparse
import sys
import os
import struct
from PIL import Image

MAGIC = b'Edsun CEG'
HEADER_SIZE = 1000
PALETTE_OFFSET = 0xC9

EGA_PALETTE = [
    (0, 0, 0), (0, 0, 170), (0, 170, 0), (0, 170, 170),
    (170, 0, 0), (170, 0, 170), (170, 85, 0), (170, 170, 170),
    (85, 85, 85), (85, 85, 255), (85, 255, 85), (85, 255, 255),
    (255, 85, 85), (255, 85, 255), (255, 255, 85), (255, 255, 255),
]


def read_ceg(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()

    if len(data) < HEADER_SIZE:
        raise ValueError("File too small for CEG header")
    if data[2:11] != MAGIC:
        raise ValueError(f"Invalid magic: expected 'Edsun CEG', got {data[2:11]!r}")

    w = struct.unpack_from('<H', data, 0x67)[0]
    h = struct.unpack_from('<H', data, 0x69)[0]
    flags = data[0x66]

    expected = w * h + HEADER_SIZE
    if len(data) != expected:
        raise ValueError(f"Size mismatch: file is {len(data)}, expected {expected} for {w}x{h}")

    return data, w, h, flags


def decode_ceg_mode(stream, w, h):
    img = Image.new('RGB', (w, h))
    palette = {}

    # Parse stream resolving colors with progressive palette state
    # entries: ('p', color) for palette pixel, ('b', color) for BF pixel,
    #          ('e', weight) for edge, ('u', 0) for unknown
    entries = []
    i = 0
    last_pal_color = (0, 0, 0)
    while i < len(stream):
        b = stream[i]
        if b == 0xBF and i + 4 < len(stream):
            r, g, b2, idx = stream[i + 1], stream[i + 2], stream[i + 3], stream[i + 4]
            palette[idx] = (r, g, b2)
            for _ in range(5):
                entries.append(('b', last_pal_color))
            i += 5
        else:
            if b in palette:
                color = palette[b]
                entries.append(('p', color))
                last_pal_color = color
            elif 0xC0 <= b <= 0xDF:
                entries.append(('e', b - 0xC0))
            else:
                entries.append(('u', (0, 0, 0)))
            i += 1

    total = w * h
    for row in range(h):
        rs = row * w
        scanline = entries[rs:rs + w]
        colors = [None] * w

        # Pass 1: fill palette and BF pixels
        row_last_pal = (0, 0, 0)
        for col in range(w):
            t, d = scanline[col]
            if t == 'p':
                colors[col] = d
                row_last_pal = d
            elif t == 'b':
                colors[col] = row_last_pal
            elif t == 'u':
                colors[col] = (0, 0, 0)

        # Pass 2: fill edge pixels by interpolation
        col = 0
        while col < w:
            t, d = scanline[col]
            if t == 'e':
                left_c = (0, 0, 0)
                for k in range(col - 1, -1, -1):
                    if colors[k] is not None:
                        left_c = colors[k]
                        break
                right_c = (0, 0, 0)
                end = col
                while end < w:
                    if scanline[end][0] != 'e':
                        if colors[end] is not None:
                            right_c = colors[end]
                        break
                    end += 1

                while col < w and scanline[col][0] == 'e':
                    wt = scanline[col][1]
                    wf = wt / 32.0
                    r = int(left_c[0] * wf + right_c[0] * (1 - wf) + 0.5)
                    g = int(left_c[1] * wf + right_c[1] * (1 - wf) + 0.5)
                    b2 = int(left_c[2] * wf + right_c[2] * (1 - wf) + 0.5)
                    colors[col] = (min(r, 255), min(g, 255), min(b2, 255))
                    col += 1
                continue
            col += 1

        for col in range(w):
            img.putpixel((col, row), colors[col] or (0, 0, 0))

    return img


def decode_ega_edge_mode(stream, w, h):
    img = Image.new('RGB', (w, h))

    for row in range(h):
        offset = row * w
        scanline = stream[offset:offset + w]
        colors = [None] * w

        for col in range(w):
            b = scanline[col]
            if b <= 0x0F:
                colors[col] = EGA_PALETTE[b]

        col = 0
        while col < w:
            b = scanline[col]
            if 0xC0 <= b <= 0xDF:
                left_c = (0, 0, 0)
                for k in range(col - 1, -1, -1):
                    if colors[k] is not None:
                        left_c = colors[k]
                        break
                right_c = (0, 0, 0)
                end = col
                while end < w:
                    if not (0xC0 <= scanline[end] <= 0xDF):
                        if colors[end] is not None:
                            right_c = colors[end]
                        break
                    end += 1

                while col < w and 0xC0 <= scanline[col] <= 0xDF:
                    weight = scanline[col] - 0xC0
                    wf = weight / 32.0
                    r = int(left_c[0] * wf + right_c[0] * (1 - wf) + 0.5)
                    g = int(left_c[1] * wf + right_c[1] * (1 - wf) + 0.5)
                    b2 = int(left_c[2] * wf + right_c[2] * (1 - wf) + 0.5)
                    colors[col] = (min(r, 255), min(g, 255), min(b2, 255))
                    col += 1
                continue
            col += 1

        for col in range(w):
            img.putpixel((col, row), colors[col] or (0, 0, 0))

    return img


LINE_COLORS_8 = [
    (255, 255, 255), (255, 85, 85), (85, 255, 85), (85, 85, 255),
    (255, 255, 85), (255, 85, 255), (85, 255, 255), (255, 170, 85),
]


def decode_line_art_mode(stream, w, h):
    img = Image.new('RGB', (w, h))

    from collections import Counter
    weight_counts = Counter()
    for b in stream:
        if b != 0:
            weight_counts[b & 0x1F] += 1
    dominant_weight = weight_counts.most_common(1)[0][0] if weight_counts else 1
    if dominant_weight == 0:
        dominant_weight = 1

    for row in range(h):
        offset = row * w
        for col in range(w):
            b = stream[offset + col]
            if b == 0:
                continue
            color_idx = (b >> 5) & 7
            weight = b & 0x1F
            base = LINE_COLORS_8[color_idx]
            if weight >= dominant_weight:
                alpha = 255
            elif weight == 0:
                alpha = 255
            else:
                alpha = max(weight * 255 // dominant_weight, 64)
            r = base[0] * alpha // 255
            g = base[1] * alpha // 255
            b2 = base[2] * alpha // 255
            img.putpixel((col, row), (r, g, b2))

    return img


def decode_advanced8(stream, w, h, palette_bytes):
    """Decode Advanced-8 with a fixed header palette (CEG mode 13)."""
    palette = list(struct.iter_unpack('BBB', palette_bytes))
    blank = len(palette)
    palette.append((0, 0, 0))
    pixels = bytearray()

    for row in range(h):
        start = row * w
        # Blanking supplies black for lookahead and register history at the edges.
        line = [blank, *stream[start:start + w], blank, blank]
        old = new = palette[blank]
        for prev, code, nxt, after in zip(line, line[1:], line[2:], line[3:]):
            prev_mix = 0xC0 <= prev <= 0xDF
            next_mix = 0xC0 <= nxt <= 0xDF
            after_mix = 0xC0 <= after <= 0xDF

            if 0xC0 <= code <= 0xDF:
                weight = code - 0xC0
                if not prev_mix and not next_mix:
                    # A single mix supplies the trailing edge of a thin line.
                    if after_mix:
                        weight = 31 - weight
                    else:
                        old, new = new, palette[nxt]
            else:
                # A color between two mixes replaces only the new register.
                if not (prev_mix and next_mix):
                    old = new
                new = palette[code]
                if not next_mix:
                    weight = 0
                elif after_mix and not prev_mix:
                    weight = 31  # Hold the old color before a run of mixes.
                else:
                    weight = nxt - 0xC0

            pixels.extend((a * (31 - weight) + b * weight + 16) // 31
                          for a, b in zip(new, old))

    # The CEG/DAC applies gamma 2.3 after mixing the linear palette colors.
    gamma = bytes(round(255 * (n / 255) ** (1 / 2.3)) for n in range(256))
    return Image.frombytes('RGB', (w, h), bytes(pixels.translate(gamma)))


def decode_ceg_no_edge_mode(stream, w, h):
    palette = {}
    i = 0
    while i < len(stream):
        b = stream[i]
        if b == 0xBF and i + 4 < len(stream):
            palette[stream[i + 4]] = (stream[i + 1], stream[i + 2], stream[i + 3])
            i += 5
        else:
            i += 1

    if len(palette) < 20:
        return decode_grayscale_mode(stream, w, h)

    img = Image.new('RGB', (w, h))
    pal = {}
    entries = []
    i = 0
    last_pal = (0, 0, 0)
    while i < len(stream):
        b = stream[i]
        if b == 0xBF and i + 4 < len(stream):
            pal[stream[i + 4]] = (stream[i + 1], stream[i + 2], stream[i + 3])
            for _ in range(5):
                entries.append(last_pal)
            i += 5
        else:
            if b in pal:
                c = pal[b]
                entries.append(c)
                last_pal = c
            else:
                entries.append(last_pal)
            i += 1

    for row in range(h):
        rs = row * w
        last = (0, 0, 0)
        for col in range(w):
            idx = rs + col
            if idx < len(entries):
                c = entries[idx]
                if c != (0, 0, 0) or col == 0:
                    last = c
                img.putpixel((col, row), c)
    return img


def decode_grayscale_mode(stream, w, h):
    vals = sorted(stream)
    n = len(vals)
    lo = vals[n * 2 // 100]
    hi = vals[n * 98 // 100]
    spread = hi - lo if hi > lo else 1

    img = Image.new('L', (w, h))
    for row in range(h):
        offset = row * w
        for col in range(w):
            v = stream[offset + col]
            img.putpixel((col, row), max(0, min(255, (v - lo) * 255 // spread)))
    return img


def detect_mode(stream, flags):
    if flags == 0x0D:
        return 'advanced8'

    has_edge_support = bool(flags & 0x02)
    has_bf_support = bool(flags & 0x08)

    has_bf = 0xBF in set(stream)

    if has_bf and has_bf_support and has_edge_support:
        return 'ceg'

    if has_bf and has_bf_support and not has_edge_support:
        return 'ceg_no_edge'

    vals = set(stream)
    non_zero = vals - {0}
    if not non_zero:
        return 'grayscale'

    low_range = all(v <= 0x0F or 0xC0 <= v <= 0xDF for v in non_zero)
    if low_range and any(0xC0 <= v <= 0xDF for v in non_zero):
        return 'ega_edge'

    has_color_structure = any(v > 0x1F and (v >> 5) > 0 for v in non_zero)
    if has_color_structure:
        return 'line_art'

    return 'grayscale'


def convert_ceg(filepath, output_path):
    data, w, h, flags = read_ceg(filepath)
    stream = data[HEADER_SIZE:]

    mode = detect_mode(stream, flags)

    if mode == 'advanced8':
        palette_bytes = data[PALETTE_OFFSET:PALETTE_OFFSET + 256 * 3]
        img = decode_advanced8(stream, w, h, palette_bytes)
    elif mode == 'ceg':
        img = decode_ceg_mode(stream, w, h)
    elif mode == 'ceg_no_edge':
        img = decode_ceg_no_edge_mode(stream, w, h)
    elif mode == 'ega_edge':
        img = decode_ega_edge_mode(stream, w, h)
    elif mode == 'line_art':
        img = decode_line_art_mode(stream, w, h)
    else:
        img = decode_grayscale_mode(stream, w, h)

    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    img.save(output_path, format='PNG')
    return [output_path]


def main():
    parser = argparse.ArgumentParser(description='Convert a CEG image to PNG.')
    parser.add_argument('input_file', help='path to the source CEG file')
    parser.add_argument('output_path', help='exact path for the output PNG')
    args = parser.parse_args()

    try:
        convert_ceg(args.input_file, args.output_path)
        print(args.output_path)
    except (ValueError, OSError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

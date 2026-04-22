# Vibe coded by Claude
# Continuous Edge Graphics (CEG) to PNG converter
# Decodes Edsun Laboratories CEG bitmap files

import sys
import os
import struct
from PIL import Image

MAGIC = b'Edsun CEG'
HEADER_SIZE = 1000

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


def apply_crt_simulate(img):
    import numpy as np
    if img.mode == 'L':
        img = img.convert('RGB')

    arr = np.array(img, dtype=np.float32)

    # Vertical gaussian blur (sigma ~1.4) to simulate CRT beam overlap.
    # This is the main effect that smooths the horizontal banding from
    # per-scanline palette redefinition.
    vk = np.array([1, 6, 15, 20, 15, 6, 1], dtype=np.float32)
    vk /= vk.sum()
    pad = len(vk) // 2
    h, w, c = arr.shape
    padded = np.pad(arr, ((pad, pad), (0, 0), (0, 0)), mode='edge')
    out = np.zeros_like(arr)
    for ki, kw in enumerate(vk):
        out += padded[ki:ki + h, :, :] * kw

    # Light horizontal softness to simulate phosphor dot pitch
    hk = np.array([1, 2, 1], dtype=np.float32)
    hk /= hk.sum()
    hpad = len(hk) // 2
    padded = np.pad(out, ((0, 0), (hpad, hpad), (0, 0)), mode='edge')
    out2 = np.zeros_like(out)
    for ki, kw in enumerate(hk):
        out2 += padded[:, ki:ki + w, :] * kw

    return Image.fromarray(np.clip(out2, 0, 255).astype(np.uint8))


def convert_ceg(filepath, output_dir, crt_simulate=False):
    data, w, h, flags = read_ceg(filepath)
    stream = data[HEADER_SIZE:]

    mode = detect_mode(stream, flags)
    basename = os.path.splitext(os.path.basename(filepath))[0]

    if mode == 'ceg':
        img = decode_ceg_mode(stream, w, h)
    elif mode == 'ceg_no_edge':
        img = decode_ceg_no_edge_mode(stream, w, h)
    elif mode == 'ega_edge':
        img = decode_ega_edge_mode(stream, w, h)
    elif mode == 'line_art':
        img = decode_line_art_mode(stream, w, h)
    else:
        img = decode_grayscale_mode(stream, w, h)

    out_path = os.path.join(output_dir, f"{basename}.png")
    img.save(out_path)
    outputs = [out_path]

    if crt_simulate:
        crt_img = apply_crt_simulate(img)
        crt_path = os.path.join(output_dir, f"{basename}_crt.png")
        crt_img.save(crt_path)
        outputs.append(crt_path)

    return outputs


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    flags = [a for a in sys.argv[1:] if a.startswith('--')]
    crt_simulate = '--crtSimulate' in flags

    if len(args) != 2:
        print(f"Usage: {sys.argv[0]} [--crtSimulate] <inputFile> <outputDir>",
              file=sys.stderr)
        sys.exit(1)

    input_file, output_dir = args

    if not os.path.isfile(input_file):
        print(f"Error: input file '{input_file}' not found", file=sys.stderr)
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    try:
        outputs = convert_ceg(input_file, output_dir,
                              crt_simulate=crt_simulate)
        for p in outputs:
            print(p)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

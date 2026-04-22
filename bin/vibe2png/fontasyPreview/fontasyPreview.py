# Vibe coded by Claude
"""
Fontasy Preview (.PV) file converter.
Converts PV clip art preview files to PNG images.

Usage: fontasyPreview.py <inputFile> <outputDir>
"""

import struct
import sys
import os
from PIL import Image


def decompress_row(data, pos, width):
    """Decompress RLE-encoded row data.

    RLE scheme: 0x55 NN VV = repeat byte VV, NN times.
    All other bytes are literal.

    Returns (decompressed_bytes, new_pos)
    """
    row = []
    while len(row) < width and pos < len(data):
        if data[pos] == 0x55 and pos + 2 < len(data):
            count = data[pos + 1]
            value = data[pos + 2]
            row.extend([value] * count)
            pos += 3
        else:
            row.append(data[pos])
            pos += 1
    return bytes(row[:width]), pos


def decode_pv_image(img_data):
    """Decode a single image from PV data.

    Returns list of (width, row_bytes) tuples, one per scanline.
    Returns None if image data is invalid.
    """
    if len(img_data) < 2:
        return None

    height_raw = struct.unpack_from('<H', img_data, 0)[0]
    if height_raw == 0:
        return None
    if height_raw > 500:
        return None

    pos = 2
    raw_rows = []

    while pos + 1 < len(img_data):
        row_width = img_data[pos]
        sb = img_data[pos + 1]
        pos += 2

        row_data, pos = decompress_row(img_data, pos, row_width)
        raw_rows.append((row_width, sb, row_data))

    if not raw_rows:
        return None

    img_width = max((w for w, sb, rd in raw_rows if sb == 0), default=0)
    if img_width == 0:
        img_width = max(w for w, sb, rd in raw_rows)
    if img_width == 0:
        return None

    result = []
    for w, sb, rd in raw_rows:
        if sb == 0:
            result.append((w, rd))
        else:
            if w > img_width and img_width > 0:
                num_subrows = w // img_width
                for i in range(num_subrows):
                    sub = rd[i * img_width:(i + 1) * img_width]
                    if len(sub) < img_width:
                        sub = sub + bytes([sb] * (img_width - len(sub)))
                    result.append((img_width, sub))
                remainder = w % img_width
                if remainder > 0:
                    sub = rd[num_subrows * img_width:]
                    if len(sub) < img_width:
                        sub = sub + bytes([sb] * (img_width - len(sub)))
                    result.append((img_width, sub))
            else:
                result.append((w, rd))

    if len(result) > height_raw:
        result = result[:height_raw]

    return result


def render_image(rows):
    """Convert decoded rows to a PIL Image (monochrome)."""
    if not rows:
        return None

    max_w = max(w for w, rd in rows)
    if max_w == 0:
        return None

    height = len(rows)
    width_px = max_w * 8

    img = Image.new('1', (width_px, height), 1)
    pixels = img.load()

    for y, (w, rd) in enumerate(rows):
        for x_byte in range(min(w, max_w)):
            if x_byte < len(rd):
                byte_val = rd[x_byte]
                for bit in range(8):
                    px = x_byte * 8 + bit
                    if px < width_px and (byte_val & (0x80 >> bit)):
                        pixels[px, y] = 0

    return img


def decode_pv_file(filepath):
    """Decode a .PV file, returning list of PIL Images.

    Returns None if the file is not a valid PV file.
    """
    with open(filepath, 'rb') as f:
        data = f.read()

    if len(data) < 4 or data[:3] != b'PVV':
        return None

    image_count = data[3]
    if image_count == 0:
        return None

    if len(data) < 4 + image_count * 4:
        return None

    offsets = []
    for i in range(image_count):
        off = struct.unpack_from('<I', data, 4 + i * 4)[0]
        if off == 0 or off >= len(data):
            return None
        offsets.append(off)

    if offsets[0] != 0x194:
        return None

    images = []
    for idx in range(image_count):
        start = offsets[idx]
        end = offsets[idx + 1] if idx + 1 < image_count else len(data)
        img_data = data[start:end]

        rows = decode_pv_image(img_data)
        if rows:
            img = render_image(rows)
            images.append(img)
        else:
            images.append(None)

    return images


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(input_file):
        print(f"Error: input file '{input_file}' not found", file=sys.stderr)
        sys.exit(1)

    images = decode_pv_file(input_file)
    if images is None:
        print(f"Error: '{input_file}' is not a valid Fontasy Preview (.PV) file", file=sys.stderr)
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    base = os.path.splitext(os.path.basename(input_file))[0]
    saved = 0
    for idx, img in enumerate(images):
        if img is not None:
            out_path = os.path.join(output_dir, f"{base}_{idx:03d}.png")
            img.save(out_path)
            saved += 1

    print(f"Extracted {saved} images from {len(images)} entries in {input_file}")


if __name__ == '__main__':
    main()

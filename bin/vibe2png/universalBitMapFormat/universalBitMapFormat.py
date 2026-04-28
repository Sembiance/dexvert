#!/usr/bin/env python3
# Vibe coded by Claude

"""Universal BitMap Format (UBF92a) to PNG converter."""

import sys
import os
import struct

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow is required. Install with: pip install Pillow", file=sys.stderr)
    sys.exit(1)

MAGIC = b"UBF92a"

FLAG_CONV_TABLE = 0x01
FLAG_PALETTE    = 0x02
FLAG_RLE        = 0x04
FLAG_LZH        = 0x08

# ─── LZHUF decompressor (LZSS + adaptive Huffman) ───
# Ported from LZHUF.C / LZH.PAS by Haruhiko Okumura / Haruyasu Yoshizaki

N         = 256
F         = 60
THRESHOLD = 2
N_CHAR    = 256 - THRESHOLD + F
T         = N_CHAR * 2 - 1
R         = T - 1
MAX_FREQ  = 0x8000

D_CODE = [
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,
    0x02,0x02,0x02,0x02,0x02,0x02,0x02,0x02,0x02,0x02,0x02,0x02,0x02,0x02,0x02,0x02,
    0x03,0x03,0x03,0x03,0x03,0x03,0x03,0x03,0x03,0x03,0x03,0x03,0x03,0x03,0x03,0x03,
    0x04,0x04,0x04,0x04,0x04,0x04,0x04,0x04,0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,
    0x06,0x06,0x06,0x06,0x06,0x06,0x06,0x06,0x07,0x07,0x07,0x07,0x07,0x07,0x07,0x07,
    0x08,0x08,0x08,0x08,0x08,0x08,0x08,0x08,0x09,0x09,0x09,0x09,0x09,0x09,0x09,0x09,
    0x0A,0x0A,0x0A,0x0A,0x0A,0x0A,0x0A,0x0A,0x0B,0x0B,0x0B,0x0B,0x0B,0x0B,0x0B,0x0B,
    0x0C,0x0C,0x0C,0x0C,0x0D,0x0D,0x0D,0x0D,0x0E,0x0E,0x0E,0x0E,0x0F,0x0F,0x0F,0x0F,
    0x10,0x10,0x10,0x10,0x11,0x11,0x11,0x11,0x12,0x12,0x12,0x12,0x13,0x13,0x13,0x13,
    0x14,0x14,0x14,0x14,0x15,0x15,0x15,0x15,0x16,0x16,0x16,0x16,0x17,0x17,0x17,0x17,
    0x18,0x18,0x19,0x19,0x1A,0x1A,0x1B,0x1B,0x1C,0x1C,0x1D,0x1D,0x1E,0x1E,0x1F,0x1F,
    0x20,0x20,0x21,0x21,0x22,0x22,0x23,0x23,0x24,0x24,0x25,0x25,0x26,0x26,0x27,0x27,
    0x28,0x28,0x29,0x29,0x2A,0x2A,0x2B,0x2B,0x2C,0x2C,0x2D,0x2D,0x2E,0x2E,0x2F,0x2F,
    0x30,0x31,0x32,0x33,0x34,0x35,0x36,0x37,0x38,0x39,0x3A,0x3B,0x3C,0x3D,0x3E,0x3F,
]

D_LEN = [
    0x03,0x03,0x03,0x03,0x03,0x03,0x03,0x03,0x03,0x03,0x03,0x03,0x03,0x03,0x03,0x03,
    0x03,0x03,0x03,0x03,0x03,0x03,0x03,0x03,0x03,0x03,0x03,0x03,0x03,0x03,0x03,0x03,
    0x04,0x04,0x04,0x04,0x04,0x04,0x04,0x04,0x04,0x04,0x04,0x04,0x04,0x04,0x04,0x04,
    0x04,0x04,0x04,0x04,0x04,0x04,0x04,0x04,0x04,0x04,0x04,0x04,0x04,0x04,0x04,0x04,
    0x04,0x04,0x04,0x04,0x04,0x04,0x04,0x04,0x04,0x04,0x04,0x04,0x04,0x04,0x04,0x04,
    0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,
    0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,
    0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,
    0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,0x05,
    0x06,0x06,0x06,0x06,0x06,0x06,0x06,0x06,0x06,0x06,0x06,0x06,0x06,0x06,0x06,0x06,
    0x06,0x06,0x06,0x06,0x06,0x06,0x06,0x06,0x06,0x06,0x06,0x06,0x06,0x06,0x06,0x06,
    0x06,0x06,0x06,0x06,0x06,0x06,0x06,0x06,0x06,0x06,0x06,0x06,0x06,0x06,0x06,0x06,
    0x07,0x07,0x07,0x07,0x07,0x07,0x07,0x07,0x07,0x07,0x07,0x07,0x07,0x07,0x07,0x07,
    0x07,0x07,0x07,0x07,0x07,0x07,0x07,0x07,0x07,0x07,0x07,0x07,0x07,0x07,0x07,0x07,
    0x07,0x07,0x07,0x07,0x07,0x07,0x07,0x07,0x07,0x07,0x07,0x07,0x07,0x07,0x07,0x07,
    0x08,0x08,0x08,0x08,0x08,0x08,0x08,0x08,0x08,0x08,0x08,0x08,0x08,0x08,0x08,0x08,
]


class LZHDecoder:
    def __init__(self, data):
        self.data = data
        self.pos = 0
        self.getbuf = 0
        self.getlen = 0
        self.freq = [0] * (T + 1)
        self.prnt = [0] * (T + N_CHAR)
        self.son = [0] * T
        self.text_buf = bytearray(N + F - 1)
        self.output = bytearray()

    def _getc(self):
        if self.pos >= len(self.data):
            return 0
        b = self.data[self.pos]
        self.pos += 1
        return b

    def _get_bit(self):
        while self.getlen <= 8:
            self.getbuf = (self.getbuf | (self._getc() << (8 - self.getlen))) & 0xFFFF
            self.getlen += 8
        result = (self.getbuf >> 15) & 1
        self.getbuf = (self.getbuf << 1) & 0xFFFF
        self.getlen -= 1
        return result

    def _get_byte(self):
        while self.getlen <= 8:
            self.getbuf = (self.getbuf | (self._getc() << (8 - self.getlen))) & 0xFFFF
            self.getlen += 8
        result = (self.getbuf >> 8) & 0xFF
        self.getbuf = (self.getbuf << 8) & 0xFFFF
        self.getlen -= 8
        return result

    def _start_huff(self):
        for i in range(N_CHAR):
            self.freq[i] = 1
            self.son[i] = i + T
            self.prnt[i + T] = i
        i = 0
        j = N_CHAR
        while j <= R:
            self.freq[j] = self.freq[i] + self.freq[i + 1]
            self.son[j] = i
            self.prnt[i] = j
            self.prnt[i + 1] = j
            i += 2
            j += 1
        self.freq[T] = 0xFFFF
        self.prnt[R] = 0

    def _reconst(self):
        j = 0
        for i in range(T):
            if self.son[i] >= T:
                self.freq[j] = (self.freq[i] + 1) >> 1
                self.son[j] = self.son[i]
                j += 1

        i = 0
        j = N_CHAR
        while j < T:
            f = self.freq[i] + self.freq[i + 1]
            self.freq[j] = f
            k = j - 1
            while f < self.freq[k]:
                k -= 1
            k += 1
            for m in range(j, k, -1):
                self.freq[m] = self.freq[m - 1]
            self.freq[k] = f
            for m in range(j, k, -1):
                self.son[m] = self.son[m - 1]
            self.son[k] = i
            i += 2
            j += 1

        for i in range(T):
            k = self.son[i]
            self.prnt[k] = i
            if k < T:
                self.prnt[k + 1] = i

    def _update(self, c):
        if self.freq[R] == MAX_FREQ:
            self._reconst()
        c = self.prnt[c + T]
        while True:
            self.freq[c] += 1
            k = self.freq[c]
            l = c + 1
            if k > self.freq[l]:
                while k > self.freq[l + 1]:
                    l += 1
                self.freq[c] = self.freq[l]
                self.freq[l] = k

                i = self.son[c]
                self.prnt[i] = l
                if i < T:
                    self.prnt[i + 1] = l

                j = self.son[l]
                self.son[l] = i

                self.prnt[j] = c
                if j < T:
                    self.prnt[j + 1] = c
                self.son[c] = j

                c = l
            c = self.prnt[c]
            if c == 0:
                break

    def _decode_char(self):
        c = self.son[R]
        while c < T:
            c = self.son[c + self._get_bit()]
        c -= T
        self._update(c)
        return c

    def _decode_position(self):
        i = self._get_byte()
        c = D_CODE[i] << 6
        j = D_LEN[i] - 2
        while j > 0:
            j -= 1
            i = ((i << 1) | self._get_bit()) & 0xFFFF
        return c | (i & 0x3F)

    def decode(self):
        textsize = (self._getc() | (self._getc() << 8) |
                    (self._getc() << 16) | (self._getc() << 24))
        if textsize == 0:
            return bytearray()

        self._start_huff()
        for i in range(N - F):
            self.text_buf[i] = 0x20
        r = N - F
        count = 0

        while count < textsize:
            c = self._decode_char()
            if c < 256:
                self.output.append(c)
                self.text_buf[r] = c
                r = (r + 1) & (N - 1)
                count += 1
            else:
                pos = self._decode_position()
                i = (r - pos - 1) & (N - 1)
                j = c - 255 + THRESHOLD
                for k in range(j):
                    c = self.text_buf[(i + k) & (N - 1)]
                    self.output.append(c)
                    self.text_buf[r] = c
                    r = (r + 1) & (N - 1)
                    count += 1

        return self.output


# ─── VGA palette conversion ───

def vga6_to_rgb8(val):
    return (val << 2) | (val >> 4)


# ─── UBF parser ───

def parse_ubf(filepath):
    with open(filepath, "rb") as f:
        data = f.read()

    if len(data) < 10:
        raise ValueError("File too small to be UBF")

    magic = data[0:6]
    if magic != MAGIC:
        raise ValueError(f"Not a UBF file (bad magic: {magic!r})")

    num_chars = data[6]
    char_width = data[7]
    char_height = data[8]
    flags = data[9]

    if num_chars == 0 or char_width == 0 or char_height == 0:
        raise ValueError("Invalid UBF: zero dimension in header")

    has_conv = bool(flags & FLAG_CONV_TABLE)
    has_pal = bool(flags & FLAG_PALETTE)
    has_rle = bool(flags & FLAG_RLE)
    has_lzh = bool(flags & FLAG_LZH)

    if has_rle:
        raise ValueError("RLE compression not supported (disabled in format spec)")

    offset = 10

    conv_table = None
    if has_conv:
        if offset + num_chars > len(data):
            raise ValueError("File truncated in conversion table")
        conv_table = data[offset:offset + num_chars]
        offset += num_chars

    palette = None
    if has_pal:
        if offset + 768 > len(data):
            raise ValueError("File truncated in palette")
        raw_pal = data[offset:offset + 768]
        offset += 768
        palette = []
        for i in range(256):
            r = vga6_to_rgb8(raw_pal[i * 3])
            g = vga6_to_rgb8(raw_pal[i * 3 + 1])
            b = vga6_to_rgb8(raw_pal[i * 3 + 2])
            palette.append((r, g, b))

    expected_size = num_chars * char_width * char_height
    compressed_data = data[offset:]

    if has_lzh:
        if len(compressed_data) < 4:
            raise ValueError("File truncated in LZH data")
        decoder = LZHDecoder(compressed_data)
        pixel_data = decoder.decode()
    else:
        pixel_data = bytearray(compressed_data)

    if len(pixel_data) != expected_size:
        raise ValueError(
            f"Pixel data size mismatch: got {len(pixel_data)}, "
            f"expected {expected_size} ({num_chars}x{char_width}x{char_height})")

    return {
        "num_chars": num_chars,
        "char_width": char_width,
        "char_height": char_height,
        "flags": flags,
        "conv_table": conv_table,
        "palette": palette,
        "pixel_data": pixel_data,
        "file_size": len(data),
        "header_size": 10,
        "conv_table_size": num_chars if has_conv else 0,
        "palette_size": 768 if has_pal else 0,
        "compressed_size": len(compressed_data),
    }


# ─── Renderer ───

def render_ubf(ubf, chars_per_row=16, spacing=1):
    num_chars = ubf["num_chars"]
    cw = ubf["char_width"]
    ch = ubf["char_height"]
    palette = ubf["palette"]
    pixel_data = ubf["pixel_data"]

    if palette is None:
        palette = [(i, i, i) for i in range(256)]

    cols = min(num_chars, chars_per_row)
    rows = (num_chars + chars_per_row - 1) // chars_per_row
    img_w = cols * (cw + spacing) + spacing
    img_h = rows * (ch + spacing) + spacing

    img = Image.new("RGB", (img_w, img_h), (0, 0, 0))
    pixels = img.load()

    for ci in range(num_chars):
        col = ci % chars_per_row
        row = ci // chars_per_row
        xo = spacing + col * (cw + spacing)
        yo = spacing + row * (ch + spacing)

        base = ci * cw * ch
        for x in range(cw):
            for y in range(ch):
                idx = pixel_data[base + x * ch + y]
                pixels[xo + x, yo + y] = palette[idx]

    return img


# ─── Main ───

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(input_file):
        print(f"Error: Input file not found: {input_file}", file=sys.stderr)
        sys.exit(1)

    try:
        ubf = parse_ubf(input_file)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    basename = os.path.splitext(os.path.basename(input_file))[0]
    img = render_ubf(ubf)
    output_path = os.path.join(output_dir, f"{basename}.png")
    img.save(output_path)

    flags_str = []
    if ubf["flags"] & FLAG_CONV_TABLE:
        flags_str.append("ConvTable")
    if ubf["flags"] & FLAG_PALETTE:
        flags_str.append("Palette")
    if ubf["flags"] & FLAG_LZH:
        flags_str.append("LZH")
    print(f"Saved: {output_path}")
    print(f"  {ubf['num_chars']} chars, {ubf['char_width']}x{ubf['char_height']}px, "
          f"flags=[{', '.join(flags_str)}]")
    print(f"  File: {ubf['file_size']} bytes = "
          f"{ubf['header_size']} hdr + "
          f"{ubf['conv_table_size']} conv + "
          f"{ubf['palette_size']} pal + "
          f"{ubf['compressed_size']} data")


if __name__ == "__main__":
    main()

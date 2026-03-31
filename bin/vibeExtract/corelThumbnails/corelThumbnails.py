#!/usr/bin/env python3
# Vibe coded by Claude
#
# unCorelThumbnails.py - Extract thumbnail images from CorelDRAW _THUMBNAIL_ streams
#
# Usage: unCorelThumbnails.py <inputFile> <outputDir>
#
# Extracts each thumbnail record from a Corel Thumbnails Archive file and writes
# them as PNG files. PSC (PaintShop script) files are copied as-is.

import struct
import sys
import os
import shutil
import zlib


# ---------------------------------------------------------------------------
# CDRCOMP1 decompressor (Huffman + LZSS, 8192-byte sliding window)
# Reverse-engineered from CDRFLT40.DLL (Corel ArtShow 5, 1994)
# ---------------------------------------------------------------------------

class BitReader:
    """MSB-first bitstream reader with 16-bit lookahead buffer."""

    def __init__(self, data):
        self.data = data
        self.pos = 0
        self.bitbuf = 0
        self.cur_byte = 0
        self.cur_bits = 0
        self._consume(16)

    def _next_byte(self):
        if self.pos < len(self.data):
            b = self.data[self.pos]
            self.pos += 1
            return b
        return 0

    def _consume(self, n):
        self.bitbuf = (self.bitbuf << n) & 0xFFFF
        while n > self.cur_bits:
            n -= self.cur_bits
            self.bitbuf |= (self.cur_byte << n) & 0xFFFF
            self.cur_byte = self._next_byte()
            self.cur_bits = 8
        self.cur_bits -= n
        self.bitbuf |= (self.cur_byte >> self.cur_bits) & ((1 << n) - 1)

    def read(self, n):
        val = (self.bitbuf >> (16 - n)) & ((1 << n) - 1)
        self._consume(n)
        return val

    def read_unary(self):
        """Read a unary-coded value: 3-bit base; if all-ones (7), extend."""
        bb = self.bitbuf
        top3 = (bb >> 13) & 7
        if top3 < 7:
            self._consume(3)
            return top3
        cl = 7
        mask = 0x1000
        while bb & mask:
            cl += 1
            mask >>= 1
        self._consume(cl - 3)
        return cl


def _build_huffman(code_lengths, num_symbols):
    """Build a canonical Huffman lookup table from code lengths."""
    if num_symbols == 0:
        return {}
    max_bits = max((code_lengths[i] for i in range(num_symbols)), default=0)
    if max_bits == 0:
        return {}
    bit_counts = [0] * (max_bits + 1)
    for i in range(num_symbols):
        if code_lengths[i] > 0:
            bit_counts[code_lengths[i]] += 1
    next_code = [0] * (max_bits + 2)
    code = 0
    for b in range(1, max_bits + 1):
        code = (code + bit_counts[b - 1]) << 1
        next_code[b] = code
    table = {}
    for sym in range(num_symbols):
        b = code_lengths[sym]
        if b > 0:
            table[(next_code[b], b)] = sym
            next_code[b] += 1
    return table


def _decode_huffman(reader, table):
    """Decode one symbol from the bitstream using the Huffman table."""
    code = 0
    for b in range(1, 20):
        code = (code << 1) | reader.read(1)
        if (code, b) in table:
            return table[(code, b)]
    raise ValueError("Invalid Huffman code in CDRCOMP1 stream")


def _read_code_length_tree(reader, num_symbols, max_bits, zero_fill_at):
    """Read a code-length Huffman tree definition.

    Returns (lengths_array, fill_code_or_None).
    If fill_code is not None, the tree is degenerate -- all symbols decode
    to fill_code.
    """
    actual_count = reader.read(max_bits)
    lengths = [0] * num_symbols

    if actual_count == 0:
        fill_code = reader.read(max_bits)
        return lengths, fill_code

    i = 0
    while i < actual_count:
        cl = reader.read_unary()
        lengths[i] = cl
        i += 1
        if i == zero_fill_at and i < actual_count:
            zfill = reader.read(2)
            for _ in range(zfill):
                if i < actual_count:
                    lengths[i] = 0
                    i += 1
    return lengths, None


def _read_main_tree(reader, cl_table, cl_fill, num_symbols):
    """Read the main literal/length Huffman tree via CL-Huffman decoding.

    CL symbol meanings:
        0    -> one zero
        1    -> read 4 bits + 3 zeros
        2    -> read 9 bits + 20 zeros
        3+   -> code length = symbol - 2
    """
    MAX_SYMS = 0x201  # 513
    cl = [0] * MAX_SYMS

    if num_symbols == 0:
        fill = reader.read(9)
        return cl, fill

    i = 0
    while i < num_symbols:
        if cl_fill is not None:
            s = cl_fill
        else:
            s = _decode_huffman(reader, cl_table)
        if s == 0:
            i += 1
        elif s == 1:
            i += reader.read(4) + 3
        elif s == 2:
            i += reader.read(9) + 20
        else:
            cl[i] = s - 2
            i += 1
    return cl, None


def cdrcomp1_decompress(compressed_data, expected_size):
    """Decompress a CDRCOMP1 bitstream.

    Parameters
    ----------
    compressed_data : bytes
        Raw compressed bytes (after the 12-byte CDRCOMP1 header).
    expected_size : int
        Expected uncompressed output size.

    Returns
    -------
    bytes
        Decompressed data.
    """
    reader = BitReader(compressed_data)
    output = bytearray(expected_size)
    window = bytearray(0x2000)  # 8192-byte sliding window (matches DLL)
    pos = 0
    win_pos = 0
    window_mask = 0x1FFF

    while pos < expected_size:
        block_count = reader.read(16)
        if block_count == 0:
            break

        # Code-length Huffman tree (19 symbols, 5-bit count, zero-fill at index 3)
        cl_lengths, cl_fill = _read_code_length_tree(reader, 19, 5, 3)
        if cl_fill is not None:
            cl_table = None
        else:
            cl_table = _build_huffman(cl_lengths, 19)

        # Main literal/length Huffman tree (up to 513 symbols)
        num_lit = reader.read(9)
        lit_lengths, lit_fill = _read_main_tree(reader, cl_table, cl_fill, num_lit)
        if lit_fill is not None:
            lit_table = None
        else:
            lit_table = _build_huffman(lit_lengths, 0x201)

        # Distance Huffman tree (14 symbols, 4-bit count, no zero-fill)
        dist_lengths, dist_fill = _read_code_length_tree(reader, 14, 4, 0xFFFF)
        if dist_fill is not None:
            dist_table = None
        else:
            dist_table = _build_huffman(dist_lengths, 14)

        # Decode block_count symbols
        for _ in range(block_count):
            if pos >= expected_size:
                break

            sym = lit_fill if lit_table is None else _decode_huffman(reader, lit_table)

            if sym <= 0xFF:
                # Literal byte
                output[pos] = sym
                window[win_pos] = sym
                pos += 1
                win_pos = (win_pos + 1) & window_mask
            else:
                # Back-reference: length = sym - 253
                length = sym - 253

                # Decode distance
                if dist_table is not None:
                    dc = _decode_huffman(reader, dist_table)
                elif dist_fill is not None:
                    dc = dist_fill
                else:
                    dc = 0

                if dc == 0:
                    distance = 0
                else:
                    extra = reader.read(dc - 1) if dc > 1 else 0
                    distance = (1 << (dc - 1)) + extra

                src = (win_pos - distance - 1) & window_mask
                for _ in range(length):
                    if pos >= expected_size:
                        break
                    b = window[src]
                    output[pos] = b
                    window[win_pos] = b
                    pos += 1
                    win_pos = (win_pos + 1) & window_mask
                    src = (src + 1) & window_mask

    return bytes(output[:pos])


# ---------------------------------------------------------------------------
# Halftone palette generation (6x6x6 RGB cube + 20 extras = 236 entries)
# ---------------------------------------------------------------------------

def build_halftone_palette():
    """Build the 236-entry halftone palette used by CorelDRAW type-5 8bpp thumbnails.

    Indices 0-215: 6x6x6 RGB color cube
        R = (i % 6) * 0x33
        G = ((i // 6) % 6) * 0x33
        B = (i // 36) * 0x33

    Indices 216-235: 20 extra system/gray colors.
    """
    palette = []
    # 6x6x6 color cube (216 entries) -- stored as BGR to match file convention
    for i in range(216):
        b = (i % 6) * 0x33
        g = ((i // 6) % 6) * 0x33
        r = (i // 36) * 0x33
        palette.append((b, g, r))
    # 20 extra entries -- system/gray ramp (BGR order)
    extras = [
        (0, 0, 0), (0, 0, 128), (0, 128, 0), (0, 128, 128),
        (128, 0, 0), (128, 0, 128), (128, 128, 0), (192, 192, 192),
        (192, 220, 192), (240, 202, 166), (240, 251, 255), (164, 160, 160),
        (128, 128, 128), (0, 0, 255), (0, 255, 0), (0, 255, 255),
        (255, 0, 0), (255, 0, 255), (255, 255, 0), (255, 255, 255),
    ]
    palette.extend(extras)
    return palette


# ---------------------------------------------------------------------------
# PNG writer (minimal, no dependencies beyond zlib)
# ---------------------------------------------------------------------------

def _png_chunk(chunk_type, data):
    """Build a PNG chunk: length + type + data + CRC."""
    out = struct.pack('>I', len(data)) + chunk_type + data
    out += struct.pack('>I', zlib.crc32(chunk_type + data) & 0xFFFFFFFF)
    return out


def write_png(path, width, height, bpp, pixels, palette_rgb=None):
    """Write a PNG file using only the standard library.

    Parameters
    ----------
    path : str
        Output file path.
    width, height : int
        Image dimensions.
    bpp : int
        8 (indexed) or 24 (RGB).
    pixels : bytes
        Raw pixel data (top-down row order from Corel).
    palette_rgb : list of (r, g, b) or None
        Palette for 8bpp images.
    """
    if bpp == 8:
        color_type = 3  # indexed
        bit_depth = 8
    else:
        color_type = 2  # RGB
        bit_depth = 8

    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n')

        # IHDR
        ihdr = struct.pack('>IIBBBBB', width, height, bit_depth, color_type, 0, 0, 0)
        f.write(_png_chunk(b'IHDR', ihdr))

        # PLTE (indexed only) - palette data is BGR, PNG needs RGB
        if bpp == 8 and palette_rgb:
            plte = bytearray()
            for b, g, r in palette_rgb:
                plte += bytes((r, g, b))
            f.write(_png_chunk(b'PLTE', bytes(plte)))

        # IDAT - add filter byte (0 = None) before each row, then deflate
        stride = width if bpp == 8 else width * 3
        raw = bytearray()
        for y in range(height - 1, -1, -1):
            raw.append(0)  # filter type: None
            row_start = y * stride
            if bpp == 24:
                # Pixel data is BGR, PNG needs RGB
                for x in range(width):
                    px = row_start + x * 3
                    raw.extend((pixels[px + 2], pixels[px + 1], pixels[px]))
            else:
                raw.extend(pixels[row_start:row_start + stride])
        f.write(_png_chunk(b'IDAT', zlib.compress(bytes(raw))))

        # IEND
        f.write(_png_chunk(b'IEND', b''))


# ---------------------------------------------------------------------------
# Thumbnail archive parser
# ---------------------------------------------------------------------------

def extract_thumbnails(input_path, output_dir):
    """Extract all thumbnails from a Corel _THUMBNAIL_ archive file.

    Parameters
    ----------
    input_path : str
        Path to the input _THUMBNAIL_ file.
    output_dir : str
        Directory to write extracted PNG files.
    """
    basename = os.path.basename(input_path)

    with open(input_path, 'rb') as f:
        data = f.read()

    # Check for PSC (PaintShop script) files
    if data[:4] == b'PSC ':
        os.makedirs(output_dir, exist_ok=True)
        out_path = os.path.join(output_dir, basename + '.psc')
        shutil.copy2(input_path, out_path)
        print(f"  Copied PSC file: {out_path}")
        return

    # Validate file header
    if len(data) < 8:
        print(f"  WARNING: File too small ({len(data)} bytes), skipping")
        return
    file_header = struct.unpack_from('<I', data, 0)[0]
    if file_header != 0:
        print(f"  WARNING: Unexpected file header 0x{file_header:08X}, skipping")
        return

    os.makedirs(output_dir, exist_ok=True)
    halftone_pal = None  # lazily built

    pos = 4  # skip 4-byte file header
    index = 0

    while pos < len(data) - 76:
        # ---- 76-byte image metadata header ----
        thumb_type = struct.unpack_from('<H', data, pos + 0x00)[0]
        width      = struct.unpack_from('<H', data, pos + 0x02)[0]
        height     = struct.unpack_from('<H', data, pos + 0x06)[0]
        bpp        = struct.unpack_from('<H', data, pos + 0x22)[0]
        pos += 76

        # ---- 2-byte separator + 2-byte data type ----
        separator  = struct.unpack_from('<H', data, pos)[0]
        data_type  = struct.unpack_from('<H', data, pos + 2)[0]
        pos += 4

        # ---- Type-specific palette data ----
        palette = None

        if data_type == 4:
            # Custom palette: uint16 count + count*3 bytes RGB
            palette_count = struct.unpack_from('<H', data, pos)[0]
            pos += 2
            palette = []
            for i in range(palette_count):
                r = data[pos]
                g = data[pos + 1]
                b = data[pos + 2]
                pos += 3
                palette.append((r, g, b))
            # Pad to 256 if needed
            while len(palette) < 256:
                palette.append((0, 0, 0))

        elif data_type == 5:
            # Halftone palette: uint16 subtype (0x00EC = 236)
            palette_subtype = struct.unpack_from('<H', data, pos)[0]
            pos += 2
            if halftone_pal is None:
                halftone_pal = build_halftone_palette()
            palette = list(halftone_pal)
            while len(palette) < 256:
                palette.append((0, 0, 0))

        elif data_type == 0:
            # No palette (24-bit)
            pass

        else:
            print(f"  WARNING: Unknown data type {data_type} at record {index}, skipping")
            block_size = struct.unpack_from('<I', data, pos)[0]
            pos += 4 + block_size
            index += 1
            continue

        # ---- 4-byte uint32 CDRCOMP1 block size ----
        block_size = struct.unpack_from('<I', data, pos)[0]
        pos += 4

        # ---- CDRCOMP1 block ----
        block_data = data[pos:pos + block_size]
        pos += block_size

        # Parse CDRCOMP1 header or handle raw uncompressed data
        if len(block_data) >= 8 and block_data[:8] == b'CDRCOMP1':
            # Compressed data
            uncomp_size = struct.unpack_from('<I', block_data, 8)[0]
            compressed = block_data[12:]
            try:
                pixels = cdrcomp1_decompress(compressed, uncomp_size)
            except Exception as e:
                print(f"  WARNING: Decompression failed for record {index}: {e}")
                index += 1
                continue
            if len(pixels) != uncomp_size:
                print(f"  WARNING: Record {index} decompressed to {len(pixels)} bytes, "
                      f"expected {uncomp_size}")
        else:
            # Raw uncompressed pixel data (no CDRCOMP1 header)
            pixels = block_data

        # Write PNG
        out_name = f"{index:04d}.png"
        out_path = os.path.join(output_dir, out_name)

        if bpp == 8 and palette is not None:
            write_png(out_path, width, height, 8, pixels, palette)
        elif bpp == 24:
            write_png(out_path, width, height, 24, pixels)
        else:
            print(f"  WARNING: Unsupported bpp={bpp} with data_type={data_type} "
                  f"for record {index}, skipping")
            index += 1
            continue

        print(f"  [{index:4d}] {width}x{height} {bpp}bpp type={data_type} -> {out_name}")
        index += 1

    print(f"  Extracted {index} thumbnail(s) from {basename}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>")
        print()
        print("Extract thumbnail images from CorelDRAW _THUMBNAIL_ archive streams.")
        print("Each thumbnail is saved as a PNG file.")
        print("PSC (PaintShop script) files are copied as-is.")
        sys.exit(1)

    input_path = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(input_path):
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    print(f"Extracting: {input_path}")
    print(f"Output dir: {output_dir}")
    print()

    extract_thumbnails(input_path, output_dir)

    print()
    print("Done.")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
ILBM to PNG converter.

Supports:
- Standard indexed color (1-8 bitplanes)
- HAM6 (Hold-And-Modify, 6 bitplanes)
- HAM8 (Hold-And-Modify, 8 bitplanes)
- EHB (Extra Half-Brite, 6 bitplanes, 32 colors)
- 24-bit and 32-bit true color
- PBM (Packed Bitmap / chunky) format
- ACBM (Amiga Contiguous Bitmap) format
- ByteRun1 (PackBits) compression
- VDAT compression
- Transparency masking
- OCS 4-bit palette detection and expansion
- SHAM (Sliced HAM) per-line palette
- CTBL/BEAM per-line color tables
- PCHG (Palette Change) with optional Huffman compression
- DCTV mode
- HAM-E mode
- Amiga aspect ratio correction (CAMG-based)
- RGBN/RGB8 direct color formats
- FCY! container variant
- Palette-only files (swatch generation)
"""

import struct
import sys
import os
from PIL import Image


# ---------- helpers ----------

def read_u8(data, off):
    return data[off]

def read_u16(data, off):
    return struct.unpack_from('>H', data, off)[0]

def read_i16(data, off):
    return struct.unpack_from('>h', data, off)[0]

def read_u32(data, off):
    return struct.unpack_from('>I', data, off)[0]

def read_i32(data, off):
    return struct.unpack_from('>i', data, off)[0]

def fourcc(data, off):
    return data[off:off+4]

def clamp(v, lo=0, hi=255):
    return max(lo, min(hi, v))


# ---------- ByteRun1 decompression ----------

def decompress_byterun1(data, expected_size):
    """Decompress ByteRun1 (PackBits) compressed data."""
    out = bytearray()
    pos = 0
    length = len(data)
    while pos < length and len(out) < expected_size:
        n = data[pos]
        pos += 1
        if n < 128:
            # literal: copy next n+1 bytes
            count = n + 1
            end = min(pos + count, length)
            out.extend(data[pos:end])
            pos = end
        elif n > 128:
            # repeat: next byte repeated (257-n) times
            if pos >= length:
                break
            count = 257 - n
            out.extend(bytes([data[pos]]) * count)
            pos += 1
        # n == 128: NOP
    # Pad if we didn't get enough data
    if len(out) < expected_size:
        out.extend(b'\x00' * (expected_size - len(out)))
    return bytes(out[:expected_size])


# ---------- VDAT decompression ----------

def decompress_vdat(body_data, width, height, num_planes):
    """Decompress VDAT (vertical data) compressed body.

    VDAT uses sub-chunks within the BODY, one per bitplane. Each VDAT
    sub-chunk has split command/value streams and outputs 16-bit words
    vertically (column-first).
    """
    bytes_per_plane_row = ((width + 15) // 16) * 2
    row_stride = bytes_per_plane_row * num_planes
    frame_buf = bytearray(row_stride * height)

    pos = 0
    plane = 0
    while pos < len(body_data) - 8 and plane < num_planes:
        chunk_id = body_data[pos:pos + 4]
        chunk_len = read_u32(body_data, pos + 4)
        chunk_data_start = pos + 8
        chunk_data_end = min(chunk_data_start + chunk_len, len(body_data))

        if chunk_id != b'VDAT':
            pos = (chunk_data_end + 1) & ~1
            continue

        if chunk_data_start + 2 > chunk_data_end:
            plane += 1
            pos = (chunk_data_end + 1) & ~1
            continue

        # First 2 bytes: byte offset to values section (from chunk data start)
        val_offset_bytes = read_u16(body_data, chunk_data_start)

        # Commands: from chunk_data_start + 2 to chunk_data_start + val_offset_bytes
        cmd_start = chunk_data_start + 2
        cmd_end = chunk_data_start + val_offset_bytes
        if cmd_end > chunk_data_end:
            cmd_end = chunk_data_end

        # Values: 16-bit words from chunk_data_start + val_offset_bytes to chunk_data_end
        val_pos = chunk_data_start + val_offset_bytes

        cmd_pos = cmd_start

        def read_value():
            nonlocal val_pos
            if val_pos + 2 > chunk_data_end:
                return -1
            v = read_u16(body_data, val_pos)
            val_pos += 2
            return v

        # Output words vertically per column
        words_per_row = bytes_per_plane_row // 2
        col = 0
        row = 0

        while col < words_per_row:
            if row >= height:
                row = 0
                col += 1
                if col >= words_per_row:
                    break

            # Read next command
            if cmd_pos >= cmd_end:
                break
            b = body_data[cmd_pos]
            cmd_pos += 1

            if b == 0:
                # Long literal: count from values, then read count literal values
                count = read_value()
                if count < 0:
                    break
                for _ in range(count):
                    word = read_value()
                    if word < 0 or col >= words_per_row:
                        break
                    off = row * row_stride + plane * bytes_per_plane_row + col * 2
                    if off + 2 <= len(frame_buf):
                        frame_buf[off] = (word >> 8) & 0xFF
                        frame_buf[off + 1] = word & 0xFF
                    row += 1
                    if row >= height:
                        row = 0
                        col += 1
            elif b == 1:
                # Long RLE: count from values, then one value to repeat
                count = read_value()
                if count < 0:
                    break
                word = read_value()
                if word < 0:
                    break
                hi = (word >> 8) & 0xFF
                lo = word & 0xFF
                for _ in range(count):
                    if col >= words_per_row:
                        break
                    off = row * row_stride + plane * bytes_per_plane_row + col * 2
                    if off + 2 <= len(frame_buf):
                        frame_buf[off] = hi
                        frame_buf[off + 1] = lo
                    row += 1
                    if row >= height:
                        row = 0
                        col += 1
            elif b < 128:
                # Short RLE: repeat next value b times
                word = read_value()
                if word < 0:
                    break
                hi = (word >> 8) & 0xFF
                lo = word & 0xFF
                for _ in range(b):
                    if col >= words_per_row:
                        break
                    off = row * row_stride + plane * bytes_per_plane_row + col * 2
                    if off + 2 <= len(frame_buf):
                        frame_buf[off] = hi
                        frame_buf[off + 1] = lo
                    row += 1
                    if row >= height:
                        row = 0
                        col += 1
            else:
                # Short literal: (256 - b) literal values
                count = 256 - b
                for _ in range(count):
                    word = read_value()
                    if word < 0 or col >= words_per_row:
                        break
                    off = row * row_stride + plane * bytes_per_plane_row + col * 2
                    if off + 2 <= len(frame_buf):
                        frame_buf[off] = (word >> 8) & 0xFF
                        frame_buf[off + 1] = word & 0xFF
                    row += 1
                    if row >= height:
                        row = 0
                        col += 1

        plane += 1
        pos = (chunk_data_end + 1) & ~1

    return bytes(frame_buf)


# ---------- RGBN/RGB8 decompression ----------

def decompress_rgbn(body_data, width, height, is_rgb8):
    """Decode RGBN (13-bit) or RGB8 (25-bit) direct color format."""
    pixels = []
    pos = 0
    total_pixels = width * height

    while len(pixels) < total_pixels and pos < len(body_data):
        if is_rgb8:
            if pos + 4 > len(body_data):
                break
            n = read_u32(body_data, pos)
            pos += 4
            r = (n >> 24) & 0xFF
            g = (n >> 16) & 0xFF
            b = (n >> 8) & 0xFF
            count = n & 0x7F
        else:
            if pos + 2 > len(body_data):
                break
            n = read_u16(body_data, pos)
            pos += 2
            r = ((n >> 12) & 0xF) * 17
            g = ((n >> 8) & 0xF) * 17
            b = ((n >> 4) & 0xF) * 17
            count = n & 0x07

        if count == 0:
            if pos >= len(body_data):
                break
            c2 = body_data[pos]
            pos += 1
            if c2 == 0:
                if pos + 2 > len(body_data):
                    break
                count = read_u16(body_data, pos)
                pos += 2
            else:
                count = c2

        for _ in range(count):
            if len(pixels) < total_pixels:
                pixels.append((r, g, b))

    # Pad if needed
    while len(pixels) < total_pixels:
        pixels.append((0, 0, 0))

    return pixels


# ---------- Planar conversion ----------

def planar_to_chunky(data, width, height, num_planes, has_mask=False):
    """Convert interleaved planar bitplane data to chunky pixel indices.

    Standard ILBM layout per scanline:
        plane0_row | plane1_row | ... | planeN_row | [mask_row]
    Each plane row is word-aligned: ((width + 15) // 16) * 2 bytes.
    """
    bytes_per_plane_row = ((width + 15) // 16) * 2
    total_planes = num_planes + (1 if has_mask else 0)
    row_stride = bytes_per_plane_row * total_planes

    pixels = []
    mask_values = [] if has_mask else None

    for y in range(height):
        row_offset = y * row_stride
        row_pixels = []
        row_mask = [] if has_mask else None

        for byte_idx in range(bytes_per_plane_row):
            for bit in range(8):
                x = byte_idx * 8 + bit
                if x >= width:
                    break
                pixel = 0
                for plane in range(num_planes):
                    plane_byte_off = row_offset + plane * bytes_per_plane_row + byte_idx
                    if plane_byte_off < len(data):
                        if data[plane_byte_off] & (0x80 >> bit):
                            pixel |= (1 << plane)
                row_pixels.append(pixel)

                if has_mask:
                    mask_byte_off = row_offset + num_planes * bytes_per_plane_row + byte_idx
                    m = 0
                    if mask_byte_off < len(data):
                        if data[mask_byte_off] & (0x80 >> bit):
                            m = 255  # opaque
                    row_mask.append(m)

        pixels.append(row_pixels)
        if has_mask:
            mask_values.append(row_mask)

    return pixels, mask_values


def acbm_to_interleaved(abit_data, width, height, num_planes):
    """Convert ACBM (contiguous bitplane) to standard interleaved layout."""
    bytes_per_plane_row = ((width + 15) // 16) * 2
    plane_size = bytes_per_plane_row * height
    row_stride = bytes_per_plane_row * num_planes

    out = bytearray(row_stride * height)
    for plane in range(num_planes):
        for y in range(height):
            src_off = plane * plane_size + y * bytes_per_plane_row
            dst_off = y * row_stride + plane * bytes_per_plane_row
            src_end = min(src_off + bytes_per_plane_row, len(abit_data))
            if src_off < len(abit_data):
                chunk = abit_data[src_off:src_end]
                out[dst_off:dst_off+len(chunk)] = chunk
    return bytes(out)


# ---------- HAM-E detection and decoding ----------

HAME_BYTE_MAGIC = [0xa2, 0xf5, 0x84, 0xdc, 0x6d, 0xb0, 0x7f]

def get_hame_nibble(data, row_offset, x, bytes_per_plane_row, num_planes, palette):
    """Get HAME nibble using palette-based RGBI extraction.

    Extracts the pixel index, looks up the palette color, then extracts
    4-bit RGBI value: R(bit3) G(bit2) B(bit1) I(bit0).
    """
    idx = get_bitplane_pixel(data, row_offset, x, bytes_per_plane_row, num_planes)
    if idx >= len(palette):
        return 0
    r, g, b = palette[idx]
    rgb = (r << 16) | (g << 8) | b
    return ((rgb >> 20) & 8) | ((rgb >> 13) & 4) | ((rgb >> 6) & 2) | ((rgb >> 4) & 1)

def get_hame_byte(data, row_offset, x, bytes_per_plane_row, num_planes, palette):
    """Extract a HAM-E byte from two consecutive RGBI nibbles."""
    hi = get_hame_nibble(data, row_offset, x * 2, bytes_per_plane_row, num_planes, palette)
    lo = get_hame_nibble(data, row_offset, x * 2 + 1, bytes_per_plane_row, num_planes, palette)
    return (hi << 4) | lo

def is_hame(data, row_offset, width, bytes_per_plane_row, num_planes, palette):
    """Check if a line contains the HAM-E magic signature using palette-based RGBI."""
    if width < 16 or num_planes < 4 or not palette:
        return False, False
    for i in range(7):
        byte_val = get_hame_byte(data, row_offset, i, bytes_per_plane_row, num_planes, palette)
        if byte_val != HAME_BYTE_MAGIC[i]:
            return False, False
    mode_byte = get_hame_byte(data, row_offset, 7, bytes_per_plane_row, num_planes, palette)
    if mode_byte == 0x18:  # HAM-E
        return True, True
    elif mode_byte == 0x14:  # REG
        return True, False
    return False, False

def decode_hame(data, width, height, bytes_per_plane_row, num_planes, palette,
                interlaced=False):
    """Decode HAM-E image to RGB pixels.

    Args:
        interlaced: If True, odd/even lines use separate palette banks (0 and 256).
    """
    row_stride = bytes_per_plane_row * num_planes
    out_width = width // 2  # HAM-E halves effective width
    rgb_pixels = []
    hame_palette = [0] * 512  # 2 banks of 256 colors (packed RGB ints)
    palette_length = [0, 0]  # Track accumulated palette entries per bank
    palette_bank = 0
    hame_mode = False

    for y in range(height):
        row_offset = y * row_stride
        # For interlaced mode, odd lines use second palette bank (offset 256)
        pal_offset = 256 if interlaced and (y & 1) != 0 else 0

        is_def, is_ham = is_hame(data, row_offset, width, bytes_per_plane_row, num_planes, palette)

        if is_def:
            # Palette definition line
            hame_mode = is_ham
            # Accumulate palette entries (each def line adds 64 colors)
            bank_idx = pal_offset >> 8  # 0 or 1
            write_offset = pal_offset + palette_length[bank_idx]
            for c in range(64):
                idx = 8 + c * 3
                if idx + 2 < out_width:
                    r = get_hame_byte(data, row_offset, idx, bytes_per_plane_row, num_planes, palette)
                    g = get_hame_byte(data, row_offset, idx + 1, bytes_per_plane_row, num_planes, palette)
                    b = get_hame_byte(data, row_offset, idx + 2, bytes_per_plane_row, num_planes, palette)
                    hame_palette[write_offset + c] = (r << 16) | (g << 8) | b
            palette_length[bank_idx] = (palette_length[bank_idx] + 64) & 0xFF
            rgb_pixels.append([(0, 0, 0)] * out_width)
        elif hame_mode:
            row = []
            rgb = 0
            for x in range(out_width):
                c = get_hame_byte(data, row_offset, x, bytes_per_plane_row, num_planes, palette)
                mode_bits = c >> 6
                val = c & 0x3F
                if mode_bits == 0:
                    if val < 60:
                        rgb = hame_palette[pal_offset + palette_bank + val]
                    else:
                        palette_bank = (val - 60) << 6
                elif mode_bits == 1:  # blue
                    rgb = (val << 2) | (rgb & 0xFFFF00)
                elif mode_bits == 2:  # red
                    rgb = (val << 18) | (rgb & 0x00FFFF)
                else:  # green
                    rgb = (val << 10) | (rgb & 0xFF00FF)
                row.append(((rgb >> 16) & 0xFF, (rgb >> 8) & 0xFF, rgb & 0xFF))
            rgb_pixels.append(row)
        else:
            # REG mode - direct palette lookup
            row = []
            for x in range(out_width):
                c = get_hame_byte(data, row_offset, x, bytes_per_plane_row, num_planes, palette)
                rgb = hame_palette[pal_offset + c]
                row.append(((rgb >> 16) & 0xFF, (rgb >> 8) & 0xFF, rgb & 0xFF))
            rgb_pixels.append(row)

    return rgb_pixels, out_width


# ---------- DCTV detection and decoding ----------

DCTV_MAX_WIDTH = 2048

def get_bitplane_pixel(data, row_offset, x, bytes_per_plane_row, num_planes):
    """Extract pixel index from planar data."""
    byte_idx = x // 8
    bit = 7 - (x % 8)
    pixel = 0
    for plane in range(num_planes):
        off = row_offset + plane * bytes_per_plane_row + byte_idx
        if off < len(data) and (data[off] >> bit) & 1:
            pixel |= (1 << plane)
    return pixel

def get_dctv_value(data, row_offset, x, bytes_per_plane_row, num_planes, palette):
    """Get the DCTV 7-bit value from bitplane data via palette lookup.

    Returns a value in format 0I0R0B0G (bits 6,4,2,0):
    - I = intensity bit (bit 4 of blue component)
    - R = MSB of red component
    - B = MSB of blue component
    - G = MSB of green component
    """
    idx = get_bitplane_pixel(data, row_offset, x, bytes_per_plane_row, num_planes)
    if idx >= len(palette):
        return 0
    r, g, b = palette[idx]
    rgb = (r << 16) | (g << 8) | b
    return ((rgb << 2) & 0x40) | ((rgb >> 19) & 0x10) | ((rgb >> 5) & 4) | ((rgb >> 15) & 1)

def is_dctv(data, row_offset, width, bytes_per_plane_row, num_planes, palette):
    """Check if a line contains the DCTV LFSR signature."""
    if width < 256 or num_planes < 2 or not palette:
        return False
    # First pixel's I bit (bit 6 of DCTV value) must be 0
    if get_dctv_value(data, row_offset, 0, bytes_per_plane_row, num_planes, palette) >> 6 != 0:
        return False
    # Check LFSR sequence against I bits of pixels 1-255
    r = 0x7d
    for x in range(1, 256):
        dv = get_dctv_value(data, row_offset, x, bytes_per_plane_row, num_planes, palette)
        if (dv >> 6) == (r & 1):
            return False
        if (r & 1) != 0:
            r ^= (0xc3 << 1)
        r >>= 1
    return True

def decode_dctv(data, width, height, num_planes, palette, resolution):
    """Decode DCTV image to RGB pixels."""
    bytes_per_plane_row = ((width + 15) // 16) * 2
    row_stride = bytes_per_plane_row * num_planes

    # Determine interlace mode
    if resolution == 'amiga1x2':
        interlace = 0
        height -= 1
    else:
        # Amiga1x1 (interlaced) - both first two lines must have LFSR signature
        if height > 1 and is_dctv(data, row_stride, width, bytes_per_plane_row, num_planes, palette):
            interlace = 1
            height -= 2
        else:
            # Second line has no signature - not a valid DCTV image in interlace mode
            return None, 0

    chroma = [0] * DCTV_MAX_WIDTH
    rgb_pixels = []
    content_offset = row_stride << interlace

    for y in range(height):
        odd = (y >> interlace) & 1
        rgb = (0, 0, 0)
        o = 0
        p = 0
        row = []
        for x in range(width):
            if (x & 1) == odd:
                n1 = get_dctv_value(data, content_offset, x, bytes_per_plane_row, num_planes, palette)
                if x + 1 < width:
                    n2 = get_dctv_value(data, content_offset, x + 1, bytes_per_plane_row, num_planes, palette)
                    n = (n1 << 1) | n2
                else:
                    n = 0

                i_val = (o + n) >> 1
                if i_val <= 64:
                    i_val = 0
                elif i_val >= 224:
                    i_val = 255
                else:
                    i_val = (i_val - 64) * 8 // 5

                u = n + p - (o << 1)
                if u < 0:
                    u += 3
                u >>= 2
                if ((x + 1) & 2) == 0:
                    u = -u

                chroma_offset = (x & ~1) | (y & interlace)
                if chroma_offset < DCTV_MAX_WIDTH:
                    v = chroma[chroma_offset] if y > interlace else 0
                    chroma[chroma_offset] = u
                    if odd == 0:
                        u = v
                        v = chroma[chroma_offset]
                else:
                    v = 0

                p = o
                o = n

                # YUV to RGB conversion (truncate towards zero like C)
                r_val = clamp(i_val + int(v * 4655 / 2560))
                b_val = clamp(i_val + int(u * 8286 / 2560))
                g_val = clamp(i_val - int((v * 2372 + u * 1616) / 2560))
                rgb = (r_val, g_val, b_val)

            row.append(rgb)
        rgb_pixels.append(row)
        content_offset += row_stride

    return rgb_pixels, height


# ---------- PCHG decoding ----------

class PchgDecoder:
    """Decode PCHG (Palette Change) chunk with optional Huffman compression."""

    def __init__(self, data):
        self.data = data
        self.pos = 0
        self.ocs = True
        self.start_line = 0
        self.line_count = 0
        self.have_palette_change = None
        self.tree_offset = 0
        self.tree_last_offset = 0
        self.compressed = False
        # Bit reader state
        self.bits = 0

    def _read_byte(self):
        if self.pos >= len(self.data):
            return -1
        b = self.data[self.pos]
        self.pos += 1
        return b

    def _read_bit(self):
        if (self.bits & 0x7f) == 0:
            if self.pos >= len(self.data):
                return -1
            self.bits = self.data[self.pos] << 1 | 1
            self.pos += 1
        else:
            self.bits <<= 1
        return (self.bits >> 8) & 1

    def _read_huffman(self):
        offset = self.tree_last_offset
        while True:
            bit = self._read_bit()
            if bit == 0:
                offset -= 2
                if offset < self.tree_offset:
                    return -1
                if (self.data[offset] & 0x81) == 1:
                    return self.data[offset + 1]
            elif bit == 1:
                hi = self.data[offset]
                lo = self.data[offset + 1]
                if hi < 0x80:
                    return lo
                offset += ((hi - 0x100) << 8) | lo
                if offset < self.tree_offset:
                    return -1
            else:
                return -1

    def _unpack_byte(self):
        return self._read_huffman() if self.compressed else self._read_byte()

    def init(self):
        if len(self.data) < 20 or self.data[0] != 0:
            return False

        # Flags byte at offset 3: bit 0 = OCS (12-bit), bit 1 = non-OCS (24-bit)
        flag_bits = self.data[3] & 3
        if flag_bits == 1:
            self.ocs = True
        elif flag_bits == 2:
            self.ocs = False
        else:
            return False

        self.start_line = read_u16(self.data, 4)
        self.line_count = read_u16(self.data, 6)
        have_len = ((self.line_count + 31) // 32) * 4
        self.have_palette_change = bytearray(have_len)

        compression = self.data[1]
        if compression == 0:
            # Uncompressed
            self.pos = 20
            if self.pos + have_len > len(self.data):
                return False
            self.have_palette_change[:] = self.data[self.pos:self.pos + have_len]
            self.pos += have_len
            self.compressed = False
        elif compression == 1:
            # Huffman compressed
            self.tree_offset = 28
            if self.tree_offset > len(self.data):
                return False
            tree_length = read_u32(self.data, 20)
            if tree_length < 2 or tree_length > 1022:
                return False
            self.pos = self.tree_offset + tree_length
            self.tree_last_offset = self.pos - 2
            # Decompress line mask
            for i in range(have_len):
                b = self._read_huffman()
                if b < 0:
                    return False
                self.have_palette_change[i] = b
            self.compressed = True
        else:
            return False
        return True

    def apply_line_palette(self, palette, y):
        """Apply palette changes for line y. Modifies palette in-place."""
        y_adj = y - self.start_line
        if y_adj < 0 or y_adj >= self.line_count:
            return
        if (self.have_palette_change[y_adj >> 3] >> (~y_adj & 7) & 1) == 0:
            return

        count = self._unpack_byte()
        if count < 0:
            return
        count2 = self._unpack_byte()
        if count2 < 0:
            return

        if self.ocs:
            # OCS mode: count changes for regs 0-15, count2 for regs 16-31
            self._set_ocs_colors(palette, 0, count)
            self._set_ocs_colors(palette, 16, count2)
        else:
            # Non-OCS: 16-bit change count, then 6 bytes per change
            total = (count << 8) | count2
            for _ in range(total):
                if self._unpack_byte() != 0:  # padding byte, must be 0
                    return
                c = self._unpack_byte()
                if c < 0:
                    return
                self._unpack_byte()  # discarded byte
                r = self._unpack_byte()
                if r < 0:
                    return
                b = self._unpack_byte()
                if b < 0:
                    return
                g = self._unpack_byte()
                if g < 0:
                    return
                while len(palette) <= c:
                    palette.append((0, 0, 0))
                palette[c] = (r, g, b)

    def _set_ocs_colors(self, palette, pal_offset, count):
        """Set OCS 12-bit colors: each change is 2 bytes (reg+red, green+blue)."""
        for _ in range(count):
            rr = self._unpack_byte()
            if rr < 0:
                return
            gb = self._unpack_byte()
            if gb < 0:
                return
            reg = pal_offset + (rr >> 4)
            r4 = rr & 0xF
            g4 = (gb >> 4) & 0xF
            b4 = gb & 0xF
            color = (r4 * 0x11, g4 * 0x11, b4 * 0x11)
            while len(palette) <= reg:
                palette.append((0, 0, 0))
            palette[reg] = color


# ---------- Main decoder class ----------

class ILBMDecoder:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.num_planes = 0
        self.masking = 0
        self.compression = 0
        self.transparent_color = 0
        self.x_aspect = 0
        self.y_aspect = 0
        self.page_width = 0
        self.page_height = 0

        self.palette = []  # list of (r, g, b) tuples
        self.num_colors = 0
        self.bmhd_pad1 = 0

        self.camg = 0
        self.has_camg = False

        self.body_data = None
        self.abit_data = None  # for ACBM

        self.form_type = None  # b'ILBM', b'PBM ', b'ACBM', b'RGBN', b'RGB8'

        # Multi-palette data
        self.sham_data = None
        self.ctbl_data = None
        self.ctbl_colors = 0
        self.pchg_data = None
        self.rast_data = None

        # PLTP (Plane-To-Pixel) mapping
        self.pltp_data = None

    def decode_file(self, filepath):
        """Read and decode an IFF/ILBM file, return a PIL Image."""
        with open(filepath, 'rb') as f:
            data = f.read()
        return self.decode(data)

    def decode(self, data):
        """Decode IFF/ILBM data and return PIL Image."""
        if len(data) < 12:
            raise ValueError("File too small for IFF format")

        container = fourcc(data, 0)
        if container not in (b'FORM', b'FCY!'):
            raise ValueError(f"Not an IFF file (got {container!r})")

        form_length = read_u32(data, 4)
        self.form_type = fourcc(data, 8)

        # Handle wrapped containers (DPST, ANIM)
        offset = 8
        if self.form_type == b'DPST':
            # Skip DPST header, find inner FORM
            if len(data) > 52 and fourcc(data, 44) == b'FORM':
                offset = 52
                self.form_type = fourcc(data, offset)
        elif self.form_type == b'ANIM':
            # Skip to first FORM inside ANIM
            if len(data) > 20 and fourcc(data, 20) == b'FORM':
                # Recurse into inner FORM
                inner_end = 20 + read_u32(data, 24) + 8
                self.form_type = fourcc(data, 28)
                offset = 28

        if self.form_type not in (b'ILBM', b'PBM ', b'ACBM', b'RGBN', b'RGB8'):
            raise ValueError(f"Unsupported IFF type: {self.form_type!r}")

        # Parse chunks
        end = min(8 + form_length, len(data))
        self._parse_chunks(data, offset + 4, end)

        # Some files (e.g. Atari ST) append chunks after the FORM container
        if end < len(data) - 7:
            self._parse_chunks(data, end, len(data))

        return self._render()

    def _parse_chunks(self, data, offset, end):
        """Parse all IFF chunks."""
        while offset < end - 7:
            chunk_id = fourcc(data, offset)
            if offset + 4 >= end:
                break
            chunk_len = read_u32(data, offset + 4)
            chunk_data_start = offset + 8
            chunk_end = chunk_data_start + chunk_len

            # Validate
            if chunk_end > end:
                chunk_end = end
                chunk_len = end - chunk_data_start

            chunk_data = data[chunk_data_start:chunk_end]

            if chunk_id == b'BMHD':
                self._parse_bmhd(chunk_data)
            elif chunk_id == b'CMAP':
                self._parse_cmap(chunk_data)
            elif chunk_id == b'CAMG':
                self._parse_camg(chunk_data)
            elif chunk_id == b'BODY':
                self.body_data = chunk_data
            elif chunk_id == b'ABIT':
                self.abit_data = chunk_data
            elif chunk_id == b'SHAM':
                self.sham_data = chunk_data
            elif chunk_id in (b'CTBL', b'BEAM'):
                self.ctbl_data = chunk_data
            elif chunk_id == b'PCHG':
                self.pchg_data = chunk_data
            elif chunk_id == b'RAST':
                self.rast_data = chunk_data
            elif chunk_id == b'PLTP':
                self.pltp_data = chunk_data
            # Skip unknown chunks

            # Advance to next chunk (word-aligned per IFF spec)
            next_aligned = (chunk_end + 1) & ~1
            # Some files don't pad chunks properly; if aligned pos has no valid
            # chunk ID but unaligned does, use unaligned
            if next_aligned != chunk_end and next_aligned < end - 7:
                aligned_id = data[next_aligned:next_aligned + 4]
                if not aligned_id.isalpha() and chunk_end < end - 7:
                    unaligned_id = data[chunk_end:chunk_end + 4]
                    if unaligned_id.isalpha():
                        next_aligned = chunk_end
            offset = next_aligned

    def _parse_bmhd(self, data):
        """Parse BMHD (Bitmap Header) chunk."""
        if len(data) < 20:
            return
        self.width = read_u16(data, 0)
        self.height = read_u16(data, 2)
        # x, y offsets at 4, 6 (ignored)
        self.num_planes = read_u8(data, 8)
        self.masking = read_u8(data, 9)
        self.compression = read_u8(data, 10)
        self.bmhd_pad1 = read_u8(data, 11)
        self.transparent_color = read_u16(data, 12)
        self.x_aspect = read_u8(data, 14)
        self.y_aspect = read_u8(data, 15)
        self.page_width = read_u16(data, 16)
        self.page_height = read_u16(data, 18)

    def _parse_cmap(self, data):
        """Parse CMAP (Color Map) chunk."""
        self.num_colors = len(data) // 3
        self.palette = []
        for i in range(self.num_colors):
            r = data[i * 3]
            g = data[i * 3 + 1]
            b = data[i * 3 + 2]
            self.palette.append((r, g, b))

    def _parse_camg(self, data):
        """Parse CAMG (Amiga viewport mode) chunk."""
        if len(data) >= 4:
            self.camg = read_u32(data, 0)
            self.has_camg = True

    def _is_ocs_palette(self):
        """Check if palette uses only 4-bit color values (OCS Amiga)."""
        if self.bmhd_pad1 == 0x80:
            return False
        if self.num_colors > 32:
            return False
        for r, g, b in self.palette:
            if (r & 0x0F) != 0 or (g & 0x0F) != 0 or (b & 0x0F) != 0:
                return False
        return True

    def _fixup_palette(self):
        """Expand OCS 4-bit palette to full 8-bit."""
        if not self.palette:
            return
        if self._is_ocs_palette():
            self.palette = [
                ((r & 0xF0) | (r >> 4), (g & 0xF0) | (g >> 4), (b & 0xF0) | (b >> 4))
                for r, g, b in self.palette
            ]

    def _detect_mode(self):
        """Detect display mode: returns 'ham6', 'ham8', 'ehb', 'dctv', 'hame', or 'normal'."""
        is_ham = (self.camg & 0x800) != 0
        is_ehb = (self.camg & 0x80) != 0

        if is_ham:
            if self.num_planes in (5, 6):
                return 'ham6'
            elif self.num_planes in (7, 8):
                return 'ham8'
        elif self.num_planes == 6 and (is_ehb or self.num_colors == 32):
            return 'ehb'

        # Auto-detect HAM6 without CAMG
        if not self.has_camg:
            if self.num_planes == 6 and self.num_colors == 16:
                return 'ham6'

        return 'normal'

    def _get_resolution(self):
        """Determine Amiga resolution scaling from CAMG and aspect ratio."""
        # First check CAMG-based resolution
        if self.has_camg:
            res = self._camg_resolution()
            if res is not None:
                return res

        # Fall back to aspect ratio
        return self._aspect_resolution()

    def _aspect_resolution(self):
        """Determine resolution from xAspect/yAspect in BMHD."""
        xa = self.x_aspect
        ya = self.y_aspect
        if xa <= 0 or ya <= 0:
            return (1, 1)
        if xa > ya * 6:
            return (8, 1)
        if xa > ya * 3:
            return (4, 1)
        if xa * 2 > ya * 3:
            return (2, 1)
        if ya > xa * 3:
            return (1, 4)
        if ya * 2 > xa * 3:
            return (1, 2)
        return (1, 1)

    def _camg_resolution(self):
        """Determine resolution from CAMG mode bits."""
        camg = self.camg

        # Determine monitor type from bits 16-31
        monitor = camg & ~0xEFFF

        if monitor in (0, 0x11000, 0x21000, 0x71000, 0xC1000, 0xD1000):
            # 15 kHz modes (NTSC, PAL, etc.)
            relevant = camg & 0x802C
            log = 0
        elif monitor == 0x41000:
            return (1, 1)  # A2024
        elif monitor in (0x51000, 0x81000, 0xB1000, 0xE1000):
            # 24 kHz modes
            relevant = camg & 0x802C
            log = -1
        elif monitor in (0x31000, 0x61000):
            # 31 kHz modes
            relevant = camg & 0x8025
            log = -1
        elif monitor in (0x91000, 0xA1000):
            # 30 kHz modes
            relevant = camg & 0x8205
            log = 0
        else:
            return None  # Unknown monitor

        # Horizontal resolution
        h_bits = relevant & 0x8220
        if h_bits == 0:
            pass
        elif h_bits == 0x8000:
            log += 1
        elif h_bits == 0x8020:
            log += 2
        elif h_bits == 0x0200:
            log -= 1
        else:
            return None

        # Vertical resolution
        v_bits = relevant & 0xD
        if v_bits == 0:
            pass
        elif v_bits == 4:
            log -= 1
        elif v_bits == 5:
            log -= 2
        elif v_bits == 8:
            log += 1
        else:
            return None

        # Map log to resolution scaling
        # Matches recoil's SetScaledSize: doubles width/height as needed.
        if log == 0:
            return (1, 1)
        elif log == -1:
            return (2, 1)
        elif log == -2:
            return (4, 1)
        elif log == -3:
            return (8, 1)
        elif log == 1:
            return (1, 2)
        elif log == 2:
            return (1, 4)
        return (1, 1)

    def _get_multipalette(self):
        """Build per-line palette from SHAM/CTBL/PCHG/RAST data.

        Returns a dict: line_number -> list of (r,g,b) palette entries,
        or None if no multi-palette.
        """
        if self.sham_data is not None:
            return self._decode_sham()
        elif self.ctbl_data is not None:
            return self._decode_ctbl()
        elif self.pchg_data is not None:
            return self._decode_pchg_palette()
        elif self.rast_data is not None:
            return self._decode_rast()
        return None

    def _decode_sham(self):
        """Decode SHAM per-line palette."""
        data = self.sham_data
        if len(data) < 4:
            return None

        # Version check
        version = read_u16(data, 0)
        if version != 0:
            return None

        pal_data = data[2:]
        num_entries = len(pal_data) // 2

        if num_entries == self.height * 16:
            # Per-line palette (16 colors per line)
            palettes = {}
            for y in range(self.height):
                pal = list(self.palette)  # copy base palette
                for c in range(16):
                    off = (y * 16 + c) * 2
                    if off + 2 > len(pal_data):
                        break
                    val = read_u16(pal_data, off)
                    r4 = (val >> 8) & 0xF
                    g4 = (val >> 4) & 0xF
                    b4 = val & 0xF
                    color = ((r4 << 4) | r4, (g4 << 4) | g4, (b4 << 4) | b4)
                    if c < len(pal):
                        pal[c] = color
                    else:
                        while len(pal) <= c:
                            pal.append((0, 0, 0))
                        pal[c] = color
                palettes[y] = pal
            return palettes
        elif num_entries == (self.height // 2) * 16:
            # Per-2-lines palette (interlaced SHAM)
            palettes = {}
            for y in range(self.height):
                pal = list(self.palette)
                stripe = y // 2
                for c in range(16):
                    off = (stripe * 16 + c) * 2
                    if off + 2 > len(pal_data):
                        break
                    val = read_u16(pal_data, off)
                    r4 = (val >> 8) & 0xF
                    g4 = (val >> 4) & 0xF
                    b4 = val & 0xF
                    color = ((r4 << 4) | r4, (g4 << 4) | g4, (b4 << 4) | b4)
                    if c < len(pal):
                        pal[c] = color
                    else:
                        while len(pal) <= c:
                            pal.append((0, 0, 0))
                        pal[c] = color
                palettes[y] = pal
            return palettes
        return None

    def _decode_ctbl(self):
        """Decode CTBL/BEAM per-line color table."""
        data = self.ctbl_data
        if not data or self.height == 0:
            return None

        num_words = len(data) // 2
        colors_per_line = num_words // self.height
        if colors_per_line == 0 or colors_per_line > 32:
            return None

        palettes = {}
        for y in range(self.height):
            pal = list(self.palette)
            for c in range(colors_per_line):
                off = (y * colors_per_line + c) * 2
                if off + 2 > len(data):
                    break
                val = read_u16(data, off)
                r4 = (val >> 8) & 0xF
                g4 = (val >> 4) & 0xF
                b4 = val & 0xF
                color = ((r4 << 4) | r4, (g4 << 4) | g4, (b4 << 4) | b4)
                if c < len(pal):
                    pal[c] = color
                else:
                    while len(pal) <= c:
                        pal.append((0, 0, 0))
                    pal[c] = color
            palettes[y] = pal
        return palettes

    def _decode_pchg_palette(self):
        """Decode PCHG palette changes into per-line palettes."""
        decoder = PchgDecoder(self.pchg_data)
        if not decoder.init():
            return None

        palettes = {}
        current_pal = list(self.palette)
        for y in range(self.height):
            decoder.apply_line_palette(current_pal, y)
            palettes[y] = list(current_pal)
        return palettes

    def _decode_rast(self):
        """Decode RAST per-line palette (Atari ST/STE format)."""
        data = self.rast_data
        if not data or self.height == 0:
            return None

        num_colors = 1 << self.num_planes
        entry_size = 2 + num_colors * 2  # 2-byte line number + colors * 2-byte ST color
        num_entries = len(data) // entry_size
        if num_entries == 0:
            return None

        # Check if STE palette (has extended bits)
        is_ste = False
        for i in range(num_entries):
            off = i * entry_size + 2
            for c in range(num_colors):
                co = off + c * 2
                if co + 2 > len(data):
                    break
                if (data[co] & 8) != 0 or (data[co + 1] & 0x88) != 0:
                    is_ste = True
                    break
            if is_ste:
                break

        # Check if line numbers are meaningful (sequential) or all zeros
        # Some files (e.g. NEOchrome RST data) have no per-entry line numbers
        has_line_nums = False
        for i in range(min(num_entries, self.height)):
            off = i * entry_size
            line_num = read_u16(data, off)
            if line_num != 0:
                has_line_nums = True
                break

        def _read_pal(off):
            pal = []
            for c in range(num_colors):
                co = off + c * 2
                if co + 2 > len(data):
                    pal.append((0, 0, 0))
                else:
                    pal.append(self._st_color(data[co], data[co + 1], is_ste))
            return pal

        palettes = {}
        last_pal = list(self.palette)

        if has_line_nums:
            # Build per-line palette lookup (entries may not be sorted by Y)
            line_map = {}
            for i in range(num_entries):
                off = i * entry_size
                line_num = read_u16(data, off)
                if line_num not in line_map:
                    line_map[line_num] = off + 2
            for y in range(self.height):
                if y in line_map:
                    last_pal = _read_pal(line_map[y])
                palettes[y] = list(last_pal)
        else:
            # Sequential mode: entry i = line i (no line number field)
            for y in range(self.height):
                if y < num_entries:
                    off = y * entry_size + 2  # Skip the 2-byte zero field
                    last_pal = _read_pal(off)
                palettes[y] = list(last_pal)
        return palettes

    @staticmethod
    def _st_color(r_byte, gb_byte, is_ste):
        """Convert Atari ST/STE color word to (r, g, b) tuple."""
        if is_ste:
            # STE 4096 colors: xxxxrRRR gGGGbBBB -> RRRr GGGg BBBb (4-bit each)
            r4 = ((r_byte & 7) << 1) | ((r_byte >> 3) & 1)
            g4 = (((gb_byte >> 4) & 7) << 1) | ((gb_byte >> 7) & 1)
            b4 = ((gb_byte & 7) << 1) | ((gb_byte >> 3) & 1)
            return (r4 * 17, g4 * 17, b4 * 17)
        else:
            # ST 512 colors: xxxx0RRR 0GGG0BBB (3-bit each)
            r3 = r_byte & 7
            g3 = (gb_byte >> 4) & 7
            b3 = gb_byte & 7
            # 3-bit to 8-bit expansion: val << 5 | val << 2 | val >> 1
            return (
                (r3 << 5) | (r3 << 2) | (r3 >> 1),
                (g3 << 5) | (g3 << 2) | (g3 >> 1),
                (b3 << 5) | (b3 << 2) | (b3 >> 1),
            )

    def _render(self):
        """Render the decoded ILBM data to a PIL Image."""
        # Handle palette-only files
        if self.width == 0 or self.height == 0:
            return self._render_palette_swatch()

        # Generate default grayscale palette if no CMAP present
        if not self.palette and self.num_planes <= 8:
            num_colors = 1 << self.num_planes
            self.palette = []
            for c in range(num_colors):
                v = c * 255 // num_colors
                self.palette.append((v, v, v))
            self.num_colors = num_colors

        # Fix palette
        self._fixup_palette()

        # Get resolution scaling
        x_scale, y_scale = self._get_resolution()

        # Determine display mode
        mode = self._detect_mode()

        # Get multi-palette if any
        multi_pal = self._get_multipalette()

        # Handle RGBN/RGB8 format
        if self.form_type in (b'RGBN', b'RGB8'):
            is_rgb8 = self.form_type == b'RGB8'
            if self.body_data:
                pixels = decompress_rgbn(self.body_data, self.width, self.height, is_rgb8)
                return self._create_rgb_image(pixels, self.width, self.height, x_scale, y_scale)
            raise ValueError("No BODY data for RGBN/RGB8")

        # Decompress body
        has_mask = self.masking == 1
        bytes_per_plane_row = ((self.width + 15) // 16) * 2

        if self.form_type == b'PBM ':
            return self._render_pbm(x_scale, y_scale)

        if self.form_type == b'ACBM':
            if self.abit_data is None:
                raise ValueError("No ABIT chunk in ACBM file")
            unpacked = acbm_to_interleaved(self.abit_data, self.width, self.height, self.num_planes)
        elif self.body_data is not None:
            if self.compression == 0:
                unpacked = self.body_data
            elif self.compression == 1:
                total_planes = self.num_planes + (1 if has_mask else 0)
                expected = bytes_per_plane_row * total_planes * self.height
                unpacked = decompress_byterun1(self.body_data, expected)
            elif self.compression == 2:
                unpacked = decompress_vdat(self.body_data, self.width, self.height, self.num_planes)
                has_mask = False  # VDAT doesn't interleave mask
            else:
                raise ValueError(f"Unsupported compression type: {self.compression}")
        else:
            raise ValueError("No BODY/ABIT data")

        # Check for DCTV
        if (mode == 'normal' and self.num_planes <= 4
                and self.width >= 256 and self.width <= DCTV_MAX_WIDTH
                and self.height >= 3 and multi_pal is None):
            if is_dctv(unpacked, 0, self.width, bytes_per_plane_row, self.num_planes, self.palette):
                res_str = 'amiga1x2' if y_scale == 2 else 'amiga1x1'
                dctv_pixels, dctv_height = decode_dctv(unpacked, self.width, self.height,
                                                        self.num_planes, self.palette, res_str)
                if dctv_pixels is not None:
                    if res_str == 'amiga1x2':
                        y_scale = 2
                    return self._create_rgb_image_2d(dctv_pixels, self.width, dctv_height,
                                                      x_scale, y_scale)

        # Check for HAM-E
        if mode == 'normal' and self.num_planes == 4 and self.width >= 400 and multi_pal is None:
            is_def, _ = is_hame(unpacked, 0, self.width, bytes_per_plane_row,
                                self.num_planes, self.palette)
            if is_def:
                # interlaced=True when y_scale==1 (AmigaHame2x1)
                hame_interlaced = (y_scale == 1)
                hame_pixels, hame_width = decode_hame(unpacked, self.width, self.height,
                                                       bytes_per_plane_row, self.num_planes,
                                                       self.palette,
                                                       interlaced=hame_interlaced)
                # HAM-E resolution: halved width absorbs resolution adjustment
                if y_scale == 2:
                    # Amiga1x2: output at (width/2, height) with 1x1 pixels
                    hame_x_scale, hame_y_scale = 1, 1
                else:
                    # Amiga1x1: output at (width, height) with 2x1 pixels
                    hame_x_scale, hame_y_scale = 2, 1
                return self._create_rgb_image_2d(hame_pixels, hame_width, self.height,
                                                  hame_x_scale, hame_y_scale)

        # Standard planar conversion
        # Pass has_mask to planar_to_chunky so it skips the mask plane correctly,
        # but discard the mask data (recoil ignores transparency masks)
        pixel_indices, mask_data = planar_to_chunky(unpacked, self.width, self.height,
                                                     self.num_planes, has_mask)
        mask_data = None  # Discard mask - match recoil behavior

        # Handle 16-bit deep images (no palette)
        if self.num_planes == 16 and self.num_colors == 0:
            return self._render_16bit(pixel_indices, x_scale, y_scale)

        # Handle 24/32 bit
        if self.num_planes >= 24:
            return self._render_truecolor(pixel_indices, x_scale, y_scale)

        # Handle HAM
        if mode in ('ham6', 'ham8'):
            return self._render_ham(pixel_indices, mode, multi_pal, x_scale, y_scale)

        # Handle EHB
        if mode == 'ehb':
            self._expand_ehb_palette()

        # Handle standard indexed
        return self._render_indexed(pixel_indices, mask_data, multi_pal, x_scale, y_scale)

    def _render_pbm(self, x_scale, y_scale):
        """Render PBM (Packed Bitmap / chunky) format."""
        if self.body_data is None:
            raise ValueError("No BODY data")

        # PBM stores pixels as sequential bytes (chunky format)
        if self.compression == 0:
            raw = self.body_data
        elif self.compression == 1:
            # PBM rows are padded to even bytes
            row_bytes = self.width
            if row_bytes % 2:
                row_bytes += 1
            expected = row_bytes * self.height
            raw = decompress_byterun1(self.body_data, expected)
        else:
            raise ValueError(f"Unsupported PBM compression: {self.compression}")

        # Fix palette
        self._fixup_palette()

        # Create image
        out_w = self.width * x_scale
        out_h = self.height * y_scale
        img = Image.new('P' if self.palette else 'L', (out_w, out_h))

        if self.palette:
            flat_pal = []
            for r, g, b in self.palette:
                flat_pal.extend([r, g, b])
            while len(flat_pal) < 768:
                flat_pal.extend([0, 0, 0])
            img.putpalette(flat_pal)

        row_bytes = self.width
        if row_bytes % 2:
            row_bytes += 1

        for y in range(self.height):
            for x in range(self.width):
                off = y * row_bytes + x
                if off < len(raw):
                    val = raw[off]
                else:
                    val = 0
                for sy in range(y_scale):
                    for sx in range(x_scale):
                        img.putpixel((x * x_scale + sx, y * y_scale + sy), val)

        return img

    def _render_palette_swatch(self):
        """Render palette-only file as a swatch image."""
        if not self.palette:
            return Image.new('RGB', (1, 1), (0, 0, 0))

        # Don't apply OCS expansion for swatches - use raw CMAP values
        n = len(self.palette)

        if n <= 256:
            img = Image.new('P', (n, 1))
            flat_pal = []
            for r, g, b in self.palette:
                flat_pal.extend([r, g, b])
            while len(flat_pal) < 768:
                flat_pal.extend([0, 0, 0])
            img.putpalette(flat_pal[:768])
            for i in range(n):
                img.putpixel((i, 0), i)
        else:
            # Too many colors for palette mode, use RGB
            img = Image.new('RGB', (n, 1))
            for i in range(n):
                img.putpixel((i, 0), self.palette[i])
        return img

    def _expand_ehb_palette(self):
        """Expand palette for EHB mode (add half-brightness copies)."""
        base_count = min(len(self.palette), 32)
        # Ensure we have at least 32 entries
        while len(self.palette) < 32:
            self.palette.append((0, 0, 0))

        # Add half-brightness versions
        for i in range(32):
            r, g, b = self.palette[i]
            half = (r >> 1, g >> 1, b >> 1)
            if i + 32 < len(self.palette):
                self.palette[i + 32] = half
            else:
                self.palette.append(half)

    def _build_pltp_remap(self):
        """Build a 16-bit lookup table from PLTP (Plane-To-Pixel) chunk.

        PLTP contains pairs of (channel, bit_position) for each bitplane,
        defining how standard planar indices should be remapped.
        Returns a 65536-entry lookup table, or None if no PLTP.
        """
        if self.pltp_data is None or len(self.pltp_data) < self.num_planes * 2:
            return None

        # Parse PLTP: for each plane, (channel, bit_pos)
        mapping = []
        for plane in range(self.num_planes):
            channel = self.pltp_data[plane * 2]
            bit_pos = self.pltp_data[plane * 2 + 1]
            mapping.append((channel, bit_pos))

        # Find unique channels and assign byte positions (highest channel = MSB)
        channels = sorted(set(ch for ch, _ in mapping), reverse=True)
        if len(channels) > 2:
            return None  # Only support 1-2 channel PLTP for now
        ch_to_byte = {ch: i for i, ch in enumerate(channels)}

        # Check if mapping is identity (standard order) - no remap needed
        is_identity = True
        for plane in range(self.num_planes):
            ch, bit = mapping[plane]
            byte_pos = ch_to_byte[ch]
            out_bit = byte_pos * 8 + bit
            if out_bit != plane:
                is_identity = False
                break
        if is_identity:
            return None

        # Build lookup table
        lut = [0] * 65536
        for val in range(65536):
            out = 0
            for plane in range(self.num_planes):
                if val & (1 << plane):
                    ch, bit = mapping[plane]
                    byte_pos = ch_to_byte[ch]
                    out |= 1 << (byte_pos * 8 + bit)
            lut[val] = out
        return lut

    def _render_16bit(self, pixel_indices, x_scale, y_scale):
        """Render 16-bit deep image as I;16 grayscale."""
        out_w = self.width * x_scale
        out_h = self.height * y_scale

        # Apply PLTP bit remapping if present
        pltp_lut = self._build_pltp_remap()

        img = Image.new('I;16', (out_w, out_h))

        for y in range(self.height):
            for x in range(self.width):
                val = pixel_indices[y][x] & 0xFFFF
                if pltp_lut is not None:
                    val = pltp_lut[val]
                for sy in range(y_scale):
                    for sx in range(x_scale):
                        img.putpixel((x * x_scale + sx, y * y_scale + sy), val)

        return img

    def _render_truecolor(self, pixel_indices, x_scale, y_scale):
        """Render 24/32-bit true color image."""
        out_w = self.width * x_scale
        out_h = self.height * y_scale
        img = Image.new('RGB', (out_w, out_h))

        for y in range(self.height):
            for x in range(self.width):
                idx = pixel_indices[y][x]
                # In ILBM 24-bit: planes 0-7 = R, 8-15 = G, 16-23 = B
                r = (idx >> 0) & 0xFF
                g = (idx >> 8) & 0xFF
                b = (idx >> 16) & 0xFF
                # Recoil swaps byte order: r is low bits, b is high bits
                rgb = (r, g, b)
                for sy in range(y_scale):
                    for sx in range(x_scale):
                        img.putpixel((x * x_scale + sx, y * y_scale + sy), rgb)

        return img

    def _render_ham(self, pixel_indices, mode, multi_pal, x_scale, y_scale):
        """Render HAM6 or HAM8 image."""
        out_w = self.width * x_scale
        out_h = self.height * y_scale
        img = Image.new('RGB', (out_w, out_h))

        hold_bits = 4 if mode == 'ham6' else 6
        hold_mask = (1 << hold_bits) - 1

        for y in range(self.height):
            # Get palette for this line
            if multi_pal and y in multi_pal:
                pal = multi_pal[y]
            else:
                pal = self.palette

            # Start each line with palette[0]
            if pal:
                r, g, b = pal[0]
            else:
                r, g, b = 0, 0, 0

            for x in range(self.width):
                c = pixel_indices[y][x]
                cmd = c >> hold_bits
                data = c & hold_mask

                if cmd == 0:
                    # Load from palette
                    if data < len(pal):
                        r, g, b = pal[data]
                    else:
                        r, g, b = 0, 0, 0
                elif cmd == 1:
                    # Modify blue
                    b = (data << (8 - hold_bits)) & 0xFF
                    b |= b >> hold_bits
                elif cmd == 2:
                    # Modify red
                    r = (data << (8 - hold_bits)) & 0xFF
                    r |= r >> hold_bits
                elif cmd == 3:
                    # Modify green
                    g = (data << (8 - hold_bits)) & 0xFF
                    g |= g >> hold_bits

                for sy in range(y_scale):
                    for sx in range(x_scale):
                        img.putpixel((x * x_scale + sx, y * y_scale + sy), (r, g, b))

        return img

    def _render_indexed(self, pixel_indices, mask_data, multi_pal, x_scale, y_scale):
        """Render standard indexed color image."""
        out_w = self.width * x_scale
        out_h = self.height * y_scale

        if multi_pal:
            # Per-line palette means we need RGB output
            img = Image.new('RGB', (out_w, out_h))

            for y in range(self.height):
                pal = multi_pal.get(y, self.palette)
                for x in range(self.width):
                    idx = pixel_indices[y][x]
                    if idx < len(pal):
                        r, g, b = pal[idx]
                    else:
                        r, g, b = 0, 0, 0

                    pixel = (r, g, b)

                    for sy in range(y_scale):
                        for sx in range(x_scale):
                            img.putpixel((x * x_scale + sx, y * y_scale + sy), pixel)
            return img

        # Standard palette mode
        has_transparency = mask_data is not None
        if has_transparency:
            img = Image.new('RGBA', (out_w, out_h))
        else:
            img = Image.new('P', (out_w, out_h))
            # Set palette
            flat_pal = []
            max_colors = max(1 << self.num_planes, len(self.palette))
            for i in range(min(256, max_colors)):
                if i < len(self.palette):
                    flat_pal.extend(self.palette[i])
                else:
                    flat_pal.extend([0, 0, 0])
            while len(flat_pal) < 768:
                flat_pal.extend([0, 0, 0])
            img.putpalette(flat_pal[:768])

        for y in range(self.height):
            for x in range(self.width):
                idx = pixel_indices[y][x]
                if has_transparency:
                    if idx < len(self.palette):
                        r, g, b = self.palette[idx]
                    else:
                        r, g, b = 0, 0, 0
                    a = mask_data[y][x]
                    pixel = (r, g, b, a)
                else:
                    pixel = idx

                for sy in range(y_scale):
                    for sx in range(x_scale):
                        img.putpixel((x * x_scale + sx, y * y_scale + sy), pixel)

        return img

    def _create_rgb_image(self, pixels_flat, width, height, x_scale, y_scale):
        """Create RGB image from flat list of (r,g,b) tuples."""
        out_w = width * x_scale
        out_h = height * y_scale
        img = Image.new('RGB', (out_w, out_h))

        for y in range(height):
            for x in range(width):
                idx = y * width + x
                if idx < len(pixels_flat):
                    r, g, b = pixels_flat[idx]
                else:
                    r, g, b = 0, 0, 0
                for sy in range(y_scale):
                    for sx in range(x_scale):
                        img.putpixel((x * x_scale + sx, y * y_scale + sy), (r, g, b))

        return img

    def _create_rgb_image_2d(self, pixels_2d, width, height, x_scale, y_scale):
        """Create RGB image from 2D list of (r,g,b) tuples."""
        out_w = width * x_scale
        out_h = height * y_scale
        img = Image.new('RGB', (out_w, out_h))

        for y in range(min(height, len(pixels_2d))):
            row = pixels_2d[y]
            for x in range(min(width, len(row))):
                r, g, b = row[x]
                for sy in range(y_scale):
                    for sx in range(x_scale):
                        px = x * x_scale + sx
                        py = y * y_scale + sy
                        if px < out_w and py < out_h:
                            img.putpixel((px, py), (r, g, b))

        return img


# ---------- CLI ----------

def convert_file(input_path, output_path=None):
    """Convert an ILBM file to PNG."""
    if output_path is None:
        base = os.path.splitext(input_path)[0]
        output_path = base + '.png'

    decoder = ILBMDecoder()
    try:
        img = decoder.decode_file(input_path)
        img.save(output_path, 'PNG')
        return True
    except Exception as e:
        print(f"Error converting {input_path}: {e}", file=sys.stderr)
        return False


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input.iff> [output.png]", file=sys.stderr)
        print(f"       {sys.argv[0]} --batch <input_dir> <output_dir>", file=sys.stderr)
        sys.exit(1)

    if sys.argv[1] == '--batch':
        if len(sys.argv) < 4:
            print("Usage: --batch <input_dir> <output_dir>", file=sys.stderr)
            sys.exit(1)
        input_dir = sys.argv[2]
        output_dir = sys.argv[3]
        os.makedirs(output_dir, exist_ok=True)

        success = 0
        fail = 0
        for name in sorted(os.listdir(input_dir)):
            input_path = os.path.join(input_dir, name)
            if not os.path.isfile(input_path):
                continue
            base = os.path.splitext(name)[0]
            output_path = os.path.join(output_dir, base + '.png')
            if convert_file(input_path, output_path):
                success += 1
            else:
                fail += 1

        print(f"Converted {success} files, {fail} failures")
    else:
        input_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else None
        if not convert_file(input_path, output_path):
            sys.exit(1)


if __name__ == '__main__':
    main()

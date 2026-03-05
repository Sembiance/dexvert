# Vibe coded by Claude
"""
cpt2png - Convert Corel Photo-Paint 7/8 CPT files to PNG

Supports CPT7FILE format version 1 and 5:
  - Variable-bit-width (VBW) compression (type 5)
  - LZW compression (type 2)
  - Raw/uncompressed tiles (type 1)
  - Fill tiles (type 4) - constant color
  - Inter-row delta filter (type 3)
  - DWORD-aligned scanline stride (Windows BMP convention)
  - 24bpp RGB and 8bpp grayscale images
  - Tiled image layout with arbitrary tile sizes
  - Multiple tile table formats (mid24, le32) with auto-detection
  - Multi-layer files: Block[2] object layer with alpha from Block[4]

Block offset table at file offset 0x13C:
  Block[0] at 0x13C - Background/mask layer (block type 1)
  Block[2] at 0x144 - Object RGB layer (block type 8) or mask (type 2)
  Block[4] at 0x14C - Object alpha mask (block type 4) or thumbnail (type 16)
  Block[6] at 0x154 - Thumbnail (block type 16)

Block type stored at block+0x18:
  1 = Background, 2 = Mask, 4 = Alpha, 8 = Object RGB, 16 = Thumbnail

The VBW decompressor reverse-engineered from CNSFlt80.dll function 0x102af4b0.
Delta filter reverse-engineered from 0x10254b50.
Fill tile handler from 0x1025398e / 0x10253a90.
Tile table format discovery from analysis of 96 sample files.

Usage:
    python cpt2png.py input.cpt [output.png]
"""

import struct
import sys
import os


def _build_sign_extend_tables():
    """Build sign extension lookup tables.

    The VBW compressor packs signed delta values in two's complement at
    reduced bit widths. These tables sign-extend N-bit values back to 8 bits.

    For N-bit values, bit N-1 is the sign bit:
      - If set: pad upper bits with 1s (negative value)
      - If clear: pad upper bits with 0s (positive value)

    Matches the table initialization at 0x102aeda0 in CNSFlt80.dll.
    """
    tables = {}
    for bit_pos in range(8):
        bit_width = bit_pos + 1
        table = bytearray(256)
        threshold = 1 << bit_pos

        for val in range(1 << bit_width):
            if val & threshold:
                # Sign bit set: sign extend with 1s
                result = (0xFF << (bit_pos + 1)) | val
            else:
                # Sign bit clear: mask to lower bits
                mask = (0xFF >> (8 - bit_pos)) if bit_pos > 0 else 0
                result = mask & val
            table[val] = result & 0xFF

        tables[bit_width] = table
    return tables


_SIGN_TABLES = _build_sign_extend_tables()


def decompress_vbw(compressed_data, output_size):
    """Variable-bit-width decompressor.

    Replicates the function at 0x102af4b0 in CNSFlt80.dll.

    The bitstream format:
    - 8-bit header per chunk: bits[4:0] = count-1, bits[7:5] = bit_width_code
    - code 0: output 'count' zero bytes
    - code 1-7: extract 'count' signed values of (code+1) bits each,
                sign-extend to 8 bits via lookup table

    The bit accumulator holds up to 32 bits, refilling one byte at a time
    from the source when available bits go negative.
    """
    output = bytearray(output_size)
    src = bytes(compressed_data)
    src_pos = 0
    dst_pos = 0

    # Load initial 4 bytes into accumulator (little-endian)
    acc = 0
    init_bytes = min(4, len(src))
    for i in range(init_bytes):
        acc |= src[i] << (i * 8)
    src_pos = init_bytes
    bits_avail = 24  # 32 loaded minus 8 for first header extraction

    def extract_bits(n):
        nonlocal acc, src_pos, bits_avail
        mask = (1 << n) - 1
        value = acc & mask
        acc >>= n
        bits_avail -= n
        # Refill when bits go negative (matching assembly's jns check)
        while bits_avail < 0:
            shift = bits_avail + 8
            if src_pos < len(src):
                new_byte = src[src_pos]
                src_pos += 1
                acc |= new_byte << shift
                bits_avail = shift
            else:
                bits_avail = 0
                break
        return value

    while dst_pos < output_size:
        header = extract_bits(8)
        count = (header & 0x1F) + 1
        bw_code = (header >> 5) & 0x07

        if bw_code == 0:
            # Zero fill (output bytes are already 0 in bytearray)
            dst_pos = min(dst_pos + count, output_size)
        else:
            bit_width = bw_code + 1  # 2-8 bits per value
            sign_table = _SIGN_TABLES[bit_width]

            for _ in range(count):
                if dst_pos >= output_size:
                    break
                raw_val = extract_bits(bit_width)
                output[dst_pos] = sign_table[raw_val]
                dst_pos += 1

    return bytes(output)


def decompress_lzw(compressed_data, output_size):
    """LZW decompressor for CPT comp_type=2.

    LZW with variable code width starting at 9 bits, LSB-first bit ordering.
    Clear code = 256, End code = 257.
    Initial dictionary entries 0-255 are single bytes.

    The CPT LZW variant uses "early" code size bumping: the code width
    increases when next_code reaches max_code - 1 (one entry before the
    dictionary is full), rather than at max_code. This matches the TIFF
    LZW convention.
    """
    src = bytes(compressed_data)
    output = bytearray(output_size)
    dst_pos = 0

    # Bit reader
    bit_pos = 0

    def read_bits(n):
        nonlocal bit_pos
        byte_pos = bit_pos >> 3
        bit_off = bit_pos & 7
        # Read enough bytes (up to 4)
        val = 0
        for i in range(4):
            idx = byte_pos + i
            if idx < len(src):
                val |= src[idx] << (i * 8)
        val >>= bit_off
        val &= (1 << n) - 1
        bit_pos += n
        return val

    CLEAR_CODE = 256
    END_CODE = 257
    FIRST_CODE = 258

    code_size = 9
    next_code = FIRST_CODE
    max_code = 1 << code_size

    # Dictionary: maps code -> bytes
    dictionary = {}
    for i in range(256):
        dictionary[i] = bytes([i])

    prev_entry = None

    while dst_pos < output_size:
        code = read_bits(code_size)

        if code == CLEAR_CODE:
            code_size = 9
            next_code = FIRST_CODE
            max_code = 1 << code_size
            dictionary = {}
            for i in range(256):
                dictionary[i] = bytes([i])
            prev_entry = None
            continue

        if code == END_CODE:
            break

        if code in dictionary:
            entry = dictionary[code]
        elif code == next_code and prev_entry is not None:
            entry = prev_entry + prev_entry[0:1]
        else:
            # Invalid code - stop decoding
            break

        # Write entry to output
        write_len = min(len(entry), output_size - dst_pos)
        output[dst_pos:dst_pos + write_len] = entry[:write_len]
        dst_pos += write_len

        # Add to dictionary
        if prev_entry is not None and next_code < 65536:
            dictionary[next_code] = prev_entry + entry[0:1]
            next_code += 1
            if next_code >= max_code - 1 and code_size < 16:
                code_size += 1
                max_code = 1 << code_size

        prev_entry = entry

    return bytes(output)


def apply_prediction_filter(data, stride, channels):
    """Apply prediction filter: H-delta first row + V-delta all rows.

    Matches delta_type=3 (mode 3) in PhotoPnt.exe prediction filter at 0x87D390.
    The filter works in two phases:

    Phase 1 - Per-channel horizontal cumulative sum for FIRST ROW only:
      for x in [channels .. stride): byte[x] += byte[x - channels]
      This reconstructs pixel values from per-channel deltas.

    Phase 2 - Inter-row vertical cumulative sum for ALL remaining rows:
      for each row y >= 1: row[y][x] += row[y-1][x]
      Each row is added to the fully decoded previous row.

    The encoder applies: vertical delta (subtract prev row) then horizontal
    delta (subtract prev channel) to row 0 only. The decoder reverses this.
    """
    result = bytearray(data)
    total = len(data)
    if stride <= 0 or total < stride:
        return bytes(result)

    # Phase 1: Per-channel horizontal cumsum for first row
    for x in range(channels, stride):
        result[x] = (result[x] + result[x - channels]) & 0xFF

    # Phase 2: Inter-row vertical cumsum for all remaining rows
    num_rows = total // stride
    for y in range(1, num_rows):
        row_start = y * stride
        prev_start = (y - 1) * stride
        for x in range(stride):
            result[row_start + x] = (
                result[row_start + x] + result[prev_start + x]
            ) & 0xFF

    return bytes(result)


def _read_mid24(data, off):
    """Read a mid24 value: bytes[1] | (bytes[2] << 8) | (bytes[3] << 16).

    This encoding stores a 24-bit value in bytes 1-3 of a 4-byte word,
    with byte 0 used for other purposes or padding.
    Backward compatible with mid16 since byte[3] is 0 for values < 65536.
    """
    return data[off + 1] | (data[off + 2] << 8) | (data[off + 3] << 16)


def _read_le32(data, off):
    """Read a standard little-endian 32-bit value."""
    return struct.unpack_from("<I", data, off)[0]


def _try_tile_table(data, start, num_tiles, reader, file_size, lenient=False):
    """Validate a potential tile table at 'start' using the given reader.

    Each tile table entry is 8 bytes: (offset, size).
    Each pointed-to tile must start with a valid (comp_type, delta_type) header.
    In lenient mode, skip comp/delta validation (for raw/headerless tiles).

    Tiles whose offset is within the file but whose stated size extends past
    EOF are accepted (truncated file support). Tiles whose offset is entirely
    beyond EOF are skipped rather than causing rejection, allowing partial
    decode of truncated files.

    Returns True if all tiles validate successfully.
    """
    valid_count = 0
    for i in range(num_tiles):
        entry_off = start + i * 8
        if entry_off + 8 > file_size or entry_off < 0:
            return False
        tile_off = reader(data, entry_off)
        tile_size = reader(data, entry_off + 4)
        if tile_off < 0x100 or tile_size < 4:
            return False
        # Tile starts beyond EOF: skip (truncated file) rather than reject
        if tile_off >= file_size:
            continue
        # Tile starts within file but extends past EOF: accept (truncated)
        if not lenient:
            td = data[tile_off:tile_off + 4]
            comp = struct.unpack_from("<H", td, 0)[0]
            delta = struct.unpack_from("<H", td, 2)[0]
            if comp not in (0, 1, 2, 4, 5) or delta not in (0, 3):
                return False
        valid_count += 1
    # Require at least one valid tile to accept the table
    return valid_count > 0


# Tile table end marker: a fill tile (comp=4) with specific fill data
# that appears immediately after the tile table in 0xFD0-type files.
_TILE_TABLE_MARKER = bytes([
    0x04, 0x00, 0x00, 0x00,  # comp=4, delta=0
    0x05, 0x00, 0x05, 0x00,  # fill data
    0x00, 0x00, 0x00, 0x00,
    0xFF, 0xFF, 0xFF, 0x00,
])


def _find_tile_table(data, block0_off, num_tiles, file_size):
    """Find the tile table within block0, returning (table_offset, reader_func).

    Strategy:
    1. Use b0+0x44 discriminator for known formats
    2. Use block header size formula: table at b0 + b0[0x20] + 0x3C
    3. Search for the tile-table-end marker
    4. Brute-force search starting from each valid tile header
    5. Fall back to exhaustive brute-force within block0

    Returns (abs_offset, reader) or (None, None) if not found.
    """
    b0_044 = struct.unpack_from("<I", data, block0_off + 0x44)[0]

    # Step 1: Known b0_044 -> (relative_offset, format) mapping.
    # Determined by analysis of 96 sample files.
    known_map = {
        0x01D1: (0x88, _read_mid24),
        0x01D9: (0xC4, _read_mid24),
        0x03D9: (0xD0, _read_mid24),
        0x07D0: (0xA4, _read_le32),
    }

    if b0_044 in known_map:
        rel_off, reader = known_map[b0_044]
        abs_off = block0_off + rel_off
        if _try_tile_table(data, abs_off, num_tiles, reader, file_size):
            return abs_off, reader

    # Step 2: Block header size formula.
    # The value at block+0x20 is the block header/data size. The tile table
    # follows at a fixed 0x3C-byte offset after this position.
    # Works for all b0_044 formats (0xFD0, 0xFD8, 0x07D0, 0x01D9, etc).
    if block0_off + 0x24 <= file_size:
        header_size = struct.unpack_from("<I", data, block0_off + 0x20)[0]
        if 0 < header_size < file_size:
            formula_off = block0_off + header_size + 0x3C
            table_size = num_tiles * 8
            if formula_off + table_size <= file_size:
                for reader in (_read_le32, _read_mid24):
                    if _try_tile_table(
                        data, formula_off, num_tiles, reader, file_size
                    ):
                        return formula_off, reader
                # Lenient: accept raw/headerless tiles (v10, some v1 files)
                for reader in (_read_le32, _read_mid24):
                    if _try_tile_table(
                        data, formula_off, num_tiles, reader, file_size,
                        lenient=True,
                    ):
                        return formula_off, reader

    # Step 3: Search for the tile-table-end marker (legacy fallback).
    # In 0xFD0-type files, the marker appears right after the tile table.
    table_size = num_tiles * 8
    search_start = 0
    while True:
        pos = data.find(_TILE_TABLE_MARKER, search_start)
        if pos == -1:
            break
        # The table should end right at this marker position
        candidate = pos - table_size
        if candidate >= block0_off:
            if _try_tile_table(data, candidate, num_tiles, _read_le32, file_size):
                return candidate, _read_le32
            if _try_tile_table(data, candidate, num_tiles, _read_mid24, file_size):
                return candidate, _read_mid24
        search_start = pos + 1

    # Step 4: For each valid tile header in block0, check if a table ends
    # right before it (with the first table entry pointing to that tile).
    block1_off = file_size
    if 0x148 <= len(data):
        b1 = struct.unpack_from("<I", data, 0x144)[0]
        if 0 < b1 < file_size:
            block1_off = b1

    potential_tiles = []
    for off in range(block0_off + 0x50, block1_off - 4, 2):
        comp = struct.unpack_from("<H", data, off)[0]
        delta = struct.unpack_from("<H", data, off + 2)[0]
        if comp in (1, 2, 4, 5) and delta in (0, 3):
            potential_tiles.append(off)

    for first_tile_off in potential_tiles:
        candidate = first_tile_off - table_size
        if candidate < block0_off:
            continue
        for reader in [_read_le32, _read_mid24]:
            if _try_tile_table(data, candidate, num_tiles, reader, file_size):
                first_off = reader(data, candidate)
                if first_off == first_tile_off:
                    return candidate, reader

    # Step 5: Exhaustive brute-force within block0 range
    search_end = block1_off - table_size
    for reader in [_read_le32, _read_mid24]:
        for start in range(block0_off + 0x14, search_end, 4):
            if _try_tile_table(data, start, num_tiles, reader, file_size):
                return start, reader

    return None, None


def decode_fill_tile(tile_data, tile_w, tile_h, channels):
    """Decode a fill tile (comp_type=4).

    Fill tiles store a constant pixel value. The tile layout is:
      [0:2]  comp_type (4)
      [2:4]  delta_type (0)
      [4:8]  sub-tile info (2x LE16: tile counts for fill pattern)
      [8:12] reserved/zero
      [12:16] fill color as packed BGR(A) + padding

    The fill color bytes are at offset 12 from the tile start (offset 8
    from the fill data start). For 24bpp: B, G, R at bytes 12-14.
    For 8bpp: gray value at byte 12.

    From CNSFlt80.dll at 0x10253a90: reads 3 DWORDs from tile_data+4
    and uses the third DWORD (at tile_data+12) as the fill pattern.
    """
    total_bytes = tile_w * tile_h * channels
    output = bytearray(total_bytes)

    # Fill color starts at offset 12 from tile start (8 bytes into fill data)
    color_off = 12
    if len(tile_data) >= color_off + channels:
        fill_bytes = tile_data[color_off:color_off + channels]
    else:
        fill_bytes = b'\x00' * channels

    # Fill each pixel with the constant value
    pixel = bytes(fill_bytes[:channels])
    for i in range(0, total_bytes, channels):
        end = min(i + channels, total_bytes)
        output[i:end] = pixel[:end - i]

    return bytes(output)


def _find_block_tile_table(data, block_off, num_tiles, file_size):
    """Find tile table within any block (Block[0], Block[2], Block[4], etc.).

    First tries the standard _find_tile_table strategy (which uses b0+0x44
    discriminator and marker search). Then falls back to checking known
    relative offsets and brute-force search within the block.

    Returns (abs_offset, reader) or (None, None) if not found.
    """
    # Try standard discovery first
    table_off, reader = _find_tile_table(data, block_off, num_tiles, file_size)
    if table_off is not None:
        return table_off, reader

    # Try known relative offsets for block headers
    for rel_off in (0xC4, 0xD0, 0x88, 0xA4):
        abs_off = block_off + rel_off
        if abs_off + num_tiles * 8 <= file_size:
            for rdr in (_read_le32, _read_mid24):
                if _try_tile_table(data, abs_off, num_tiles, rdr, file_size):
                    return abs_off, rdr

    # Brute-force search within the block's header area
    b_20 = struct.unpack_from("<I", data, block_off + 0x20)[0] \
        if block_off + 0x24 <= file_size else 0x200
    search_end = block_off + max(b_20, 0x400)
    table_size = num_tiles * 8
    for rdr in (_read_le32, _read_mid24):
        for start in range(block_off + 0x14,
                           min(search_end, file_size - table_size), 4):
            if _try_tile_table(data, start, num_tiles, rdr, file_size):
                return start, rdr

    return None, None


def _block_has_fill_tiles(data, block_off, file_size):
    """Check if a block's tile table contains any fill tiles (comp_type=4).

    Fill tiles explicitly encode a constant color value, indicating the
    background color was intentionally set (e.g. black fill tiles mean a
    genuinely black background, not a transparent/empty one).

    Returns True if at least one fill tile is found, False otherwise.
    """
    if block_off + 0x14 > file_size:
        return False

    width = struct.unpack_from("<I", data, block_off + 0x00)[0]
    height = struct.unpack_from("<I", data, block_off + 0x04)[0]
    tile_w = struct.unpack_from("<I", data, block_off + 0x08)[0]
    tile_h = struct.unpack_from("<I", data, block_off + 0x0C)[0]

    if width == 0 or height == 0 or tile_w == 0 or tile_h == 0:
        return False

    num_tiles_x = (width + tile_w - 1) // tile_w
    num_tiles_y = (height + tile_h - 1) // tile_h
    num_tiles = num_tiles_x * num_tiles_y

    table_off, reader = _find_block_tile_table(
        data, block_off, num_tiles, file_size
    )
    if table_off is None:
        return False

    for tile_idx in range(num_tiles):
        entry_off = table_off + tile_idx * 8
        tile_off = reader(data, entry_off)
        tile_size = reader(data, entry_off + 4)
        if tile_size < 4 or tile_off + tile_size > file_size:
            continue
        comp_type = struct.unpack_from("<H", data, tile_off)[0]
        if comp_type == 4:
            return True

    return False


def _decode_block_tiles(data, block_off, file_size):
    """Decode all tiles from a block and return assembled pixel data.

    Returns (width, height, channels, pixel_bytes) or None on failure.
    pixel_bytes is in RGB order for 3-channel, grayscale for 1-channel.

    Tile scanlines use DWORD-aligned stride (padded to 4-byte boundary),
    matching the Windows BMP/DIB convention used by Corel Photo-Paint.
    """
    if block_off + 0x14 > file_size:
        return None

    width = struct.unpack_from("<I", data, block_off + 0x00)[0]
    height = struct.unpack_from("<I", data, block_off + 0x04)[0]
    tile_w = struct.unpack_from("<I", data, block_off + 0x08)[0]
    tile_h = struct.unpack_from("<I", data, block_off + 0x0C)[0]
    bpp = struct.unpack_from("<I", data, block_off + 0x10)[0]
    is_1bit = (bpp == 1)
    channels = 1 if is_1bit else bpp // 8

    if width == 0 or height == 0 or tile_w == 0 or tile_h == 0:
        return None
    if not is_1bit and channels not in (1, 2, 3, 4):
        return None
    if width > 100000 or height > 100000:
        return None

    num_tiles_x = (width + tile_w - 1) // tile_w
    num_tiles_y = (height + tile_h - 1) // tile_h
    num_tiles = num_tiles_x * num_tiles_y

    table_off, reader = _find_block_tile_table(
        data, block_off, num_tiles, file_size
    )
    if table_off is None:
        return None

    img = bytearray(width * height * channels)

    for tile_idx in range(num_tiles):
        tx = tile_idx % num_tiles_x
        ty = tile_idx // num_tiles_x
        tw_visible = min(tile_w, width - tx * tile_w)
        th_visible = min(tile_h, height - ty * tile_h)

        entry_off = table_off + tile_idx * 8
        tile_off = reader(data, entry_off)
        tile_size = reader(data, entry_off + 4)
        if tile_size < 4 or tile_off >= file_size:
            continue
        # Clamp tile_size to available data (truncated file support)
        actual_size = min(tile_size, file_size - tile_off)

        tile_data = data[tile_off:tile_off + actual_size]
        comp_type = struct.unpack_from("<H", tile_data, 0)[0]
        delta_type = struct.unpack_from("<H", tile_data, 2)[0]
        compressed = tile_data[4:]

        # Scanline stride is DWORD-aligned (padded to 4-byte boundary).
        # This matches Windows BMP/DIB convention used by Corel.
        if is_1bit:
            stride = ((tile_w + 31) // 32) * 4
        else:
            scanline_bytes = tile_w * channels
            stride = (scanline_bytes + 3) & ~3
        total_decompressed = stride * tile_h

        try:
            if comp_type == 5:
                decompressed = decompress_vbw(compressed, total_decompressed)
            elif comp_type == 2:
                decompressed = decompress_lzw(compressed, total_decompressed)
            elif comp_type == 0:
                # comp=0: raw uncompressed tile with no header.
                # The 00 00 00 00 at tile start is pixel data, not a header.
                # tile_size equals the raw data size exactly.
                decompressed = tile_data[:total_decompressed]
                if len(decompressed) < total_decompressed:
                    decompressed += b"\x00" * (
                        total_decompressed - len(decompressed)
                    )
            elif comp_type == 1:
                decompressed = compressed[:total_decompressed]
                if len(decompressed) < total_decompressed:
                    decompressed += b"\x00" * (
                        total_decompressed - len(decompressed)
                    )
            elif comp_type == 4:
                decompressed = decode_fill_tile(
                    tile_data, tile_w, tile_h, channels
                )
            else:
                # Unknown comp_type: treat entire tile as raw pixel data
                # (no header). Handles headerless tiles in v10 and some v1.
                decompressed = tile_data[:total_decompressed]
                if len(decompressed) < total_decompressed:
                    decompressed += b"\x00" * (
                        total_decompressed - len(decompressed)
                    )
                delta_type = 0  # Raw tiles have no delta filter
        except Exception:
            continue

        if delta_type == 3:
            decompressed = apply_prediction_filter(decompressed, stride, channels)

        # For 1-bit images, unpack bits to bytes (1 byte per pixel).
        # BMP convention: MSB first within each byte, white=1 black=0.
        if is_1bit:
            unpacked = bytearray(tile_w * th_visible)
            for y in range(th_visible):
                row_off = y * stride
                for x in range(tw_visible):
                    byte_idx = row_off + (x >> 3)
                    bit_idx = 7 - (x & 7)
                    if byte_idx < len(decompressed):
                        bit = (decompressed[byte_idx] >> bit_idx) & 1
                        unpacked[y * tile_w + x] = 255 if bit else 0
            for y in range(th_visible):
                for x in range(tw_visible):
                    px_x = tx * tile_w + x
                    py_y = ty * tile_h + y
                    if px_x < width and py_y < height:
                        img[py_y * width + px_x] = unpacked[y * tile_w + x]
            continue

        # Row-based tile assembly: copy decompressed rows into the image
        # with BGR->RGB channel swapping done in bulk per row.
        px_x = tx * tile_w
        py_y = ty * tile_h
        row_pixels = tw_visible * channels

        if channels == 1:
            # Grayscale: direct row copy (no channel swap needed)
            for y in range(th_visible):
                src_start = y * stride
                dst_start = (py_y + y) * width + px_x
                img[dst_start:dst_start + tw_visible] = (
                    decompressed[src_start:src_start + tw_visible]
                )
        elif channels == 3:
            # BGR -> RGB: swap B and R channels per row using a temp buffer
            for y in range(th_visible):
                src_start = y * stride
                dst_start = ((py_y + y) * width + px_x) * 3
                row = bytearray(
                    decompressed[src_start:src_start + row_pixels]
                )
                # Swap B and R in-place: row[0::3] <-> row[2::3]
                row[0::3], row[2::3] = row[2::3], row[0::3]
                img[dst_start:dst_start + row_pixels] = row
        elif channels == 4:
            # BGRA -> RGBA: swap B and R channels per row
            for y in range(th_visible):
                src_start = y * stride
                dst_start = ((py_y + y) * width + px_x) * 4
                row = bytearray(
                    decompressed[src_start:src_start + row_pixels]
                )
                row[0::4], row[2::4] = row[2::4], row[0::4]
                img[dst_start:dst_start + row_pixels] = row
        elif channels == 2:
            # 16bpp gray+alpha: direct row copy (no channel swap)
            for y in range(th_visible):
                src_start = y * stride
                dst_start = ((py_y + y) * width + px_x) * 2
                img[dst_start:dst_start + row_pixels] = (
                    decompressed[src_start:src_start + row_pixels]
                )

    return width, height, channels, bytes(img)


def _flip_vertical(width, height, channels, pixel_data):
    """Flip image vertically (BMP bottom-up to top-down).

    CPT tiles use BMP/DIB storage order where row 0 is the bottom of the
    image. PNG and standard display use top-down order. This flips the
    row order for correct output.
    """
    row_bytes = width * channels
    result = bytearray(len(pixel_data))
    for y in range(height):
        src_start = y * row_bytes
        dst_start = (height - 1 - y) * row_bytes
        result[dst_start:dst_start + row_bytes] = (
            pixel_data[src_start:src_start + row_bytes]
        )
    return bytes(result)


def _composite_object(canvas, canvas_w, canvas_h, out_ch,
                      obj_pixels, obj_w, obj_h, obj_ch,
                      obj_x, obj_y, alpha_data, alpha_w, alpha_h,
                      opacity=100):
    """Composite an object layer onto the canvas using alpha blending.

    All pixel data is in BMP order (bottom-up). Positions are signed
    integers allowing objects to extend beyond canvas bounds.
    Handles both RGB (3ch) and grayscale (1ch) objects.
    opacity is layer opacity as percentage (0-100), stored at block+0x64.

    Uses Pillow for fast alpha compositing when available.
    """
    from PIL import Image

    # Compute visible region (clip to canvas bounds)
    ox_start = max(0, -obj_x)
    oy_start = max(0, -obj_y)
    ox_end = min(obj_w, canvas_w - obj_x)
    oy_end = min(obj_h, canvas_h - obj_y)
    if ox_start >= ox_end or oy_start >= oy_end:
        return

    vis_w = ox_end - ox_start
    vis_h = oy_end - oy_start
    cx_start = obj_x + ox_start
    cy_start = obj_y + oy_start

    # Build the object RGB image for the visible region
    if obj_ch >= 3:
        # Extract visible rows of RGB data
        obj_rgb = bytearray(vis_w * vis_h * 3)
        src_row_bytes = obj_w * obj_ch
        for y in range(vis_h):
            soy = oy_start + y
            src_start = soy * src_row_bytes + ox_start * obj_ch
            dst_start = y * vis_w * 3
            obj_rgb[dst_start:dst_start + vis_w * 3] = (
                obj_pixels[src_start:src_start + vis_w * 3]
            )
        obj_img = Image.frombytes("RGB", (vis_w, vis_h), bytes(obj_rgb))
    else:
        # Grayscale: extract visible rows and convert via Pillow
        obj_gray = bytearray(vis_w * vis_h)
        for y in range(vis_h):
            soy = oy_start + y
            src_start = soy * obj_w + ox_start
            dst_start = y * vis_w
            obj_gray[dst_start:dst_start + vis_w] = (
                obj_pixels[src_start:src_start + vis_w]
            )
        obj_img = Image.frombytes("L", (vis_w, vis_h), bytes(obj_gray))
        obj_img = obj_img.convert("RGB")

    # Build alpha channel for the visible region
    if alpha_data is not None:
        # Extract visible rows from alpha mask
        alpha_vis = bytearray(vis_w * vis_h)
        for y in range(vis_h):
            soy = oy_start + y
            if soy < alpha_h:
                a_start = soy * alpha_w + ox_start
                a_end = min(a_start + vis_w, soy * alpha_w + alpha_w)
                copy_w = a_end - a_start
                d_start = y * vis_w
                alpha_vis[d_start:d_start + copy_w] = (
                    alpha_data[a_start:a_end]
                )
        if opacity < 100:
            opacity_f = opacity / 100.0
            for i in range(len(alpha_vis)):
                alpha_vis[i] = int(alpha_vis[i] * opacity_f + 0.5)
        alpha_img = Image.frombytes("L", (vis_w, vis_h), bytes(alpha_vis))
    else:
        # No alpha mask: non-black pixels get full opacity
        obj_img_l = obj_img.convert("L")
        alpha_vis = bytearray(obj_img_l.tobytes())
        for i in range(len(alpha_vis)):
            alpha_vis[i] = 255 if alpha_vis[i] > 0 else 0
        if opacity < 100:
            opacity_f = opacity / 100.0
            for i in range(len(alpha_vis)):
                alpha_vis[i] = int(alpha_vis[i] * opacity_f + 0.5)
        alpha_img = Image.frombytes("L", (vis_w, vis_h), bytes(alpha_vis))

    obj_img.putalpha(alpha_img)

    # Extract the canvas region as RGBA (alpha=255 for background)
    canvas_region = bytearray(vis_w * vis_h * 3)
    canvas_row_bytes = canvas_w * out_ch
    for y in range(vis_h):
        cy = cy_start + y
        src_start = cy * canvas_row_bytes + cx_start * out_ch
        dst_start = y * vis_w * 3
        canvas_region[dst_start:dst_start + vis_w * 3] = (
            canvas[src_start:src_start + vis_w * 3]
        )

    bg_img = Image.frombytes("RGB", (vis_w, vis_h), bytes(canvas_region))
    bg_img.putalpha(Image.new("L", (vis_w, vis_h), 255))

    # Pillow alpha_composite does the blend in C
    result = Image.alpha_composite(bg_img, obj_img)

    # Write result back to canvas (RGB only, row-based)
    result_data = result.tobytes()
    for y in range(vis_h):
        cy = cy_start + y
        dst_start = cy * canvas_row_bytes + cx_start * out_ch
        src_start = y * vis_w * 4  # RGBA output from alpha_composite
        # Extract RGB from RGBA row
        row_rgba = result_data[src_start:src_start + vis_w * 4]
        # Strip alpha: take RGB bytes only
        row_rgb = bytearray(vis_w * 3)
        row_rgb[0::3] = row_rgba[0::4]
        row_rgb[1::3] = row_rgba[1::4]
        row_rgb[2::3] = row_rgba[2::4]
        canvas[dst_start:dst_start + vis_w * 3] = row_rgb


def _apply_palette(pixels, w, h, palette):
    """Convert 8-bit palette indices to 24-bit RGB using a color palette."""
    num_entries = len(palette) // 3
    rgb = bytearray(w * h * 3)
    for i in range(w * h):
        idx = pixels[i] if i < len(pixels) else 0
        if idx < num_entries:
            rgb[i * 3] = palette[idx * 3]
            rgb[i * 3 + 1] = palette[idx * 3 + 1]
            rgb[i * 3 + 2] = palette[idx * 3 + 2]
    return bytes(rgb)


def decode_cpt7(filename):
    """Decode a CPT7 file and return (width, height, channels, pixel_data).

    pixel_data is in RGB byte order for 3-channel, grayscale for 1-channel.

    The block offset table at 0x13C contains entries at 8-byte intervals.
    Each entry is a 4-byte LE32 file offset to a block header. Blocks
    are organized as:
      - Background (type 1): canvas base layer
      - Object pairs: RGB/gray (type 8) + alpha mask (type 4)
      - Thumbnail (type 16): ignored

    Object layers are composited onto the background in order, each
    blended using its associated alpha mask.
    """
    with open(filename, "rb") as f:
        data = f.read()

    magic = data[:8]
    if len(data) < 0x150 or magic not in (b"CPT7FILE", b"CPT9FILE"):
        raise ValueError("Not a CPT7FILE or CPT9FILE")
    is_cpt9 = (magic == b"CPT9FILE")

    version = struct.unpack_from("<I", data, 8)[0]
    if version not in (1, 5, 6, 10, 14):
        raise ValueError(
            f"Unsupported CPT version {version}"
        )

    file_size = len(data)

    # V10: paletted format with color palette before block offset table
    palette = None
    block_table_off = 0x13C
    if is_cpt9 and 0x38 <= file_size:
        # CPT9FILE stores block table offset explicitly at 0x34
        cpt9_table_off = struct.unpack_from("<I", data, 0x34)[0]
        if cpt9_table_off > 0 and cpt9_table_off < file_size:
            block_table_off = cpt9_table_off
    if version == 10:
        palette_size = struct.unpack_from("<I", data, 0x0C)[0]
        if palette_size > 0 and 0x13C + palette_size < file_size:
            palette = data[0x13C:0x13C + palette_size]
            if not is_cpt9:
                block_table_off = 0x13C + palette_size

    # Block offset table
    block0_off = struct.unpack_from("<I", data, block_table_off)[0]
    if block0_off == 0 or block0_off >= file_size:
        raise ValueError("No valid block 0")

    # Canvas dimensions from Block[0]
    canvas_w = struct.unpack_from("<I", data, block0_off + 0x00)[0]
    canvas_h = struct.unpack_from("<I", data, block0_off + 0x04)[0]
    canvas_bpp = struct.unpack_from("<I", data, block0_off + 0x10)[0]
    canvas_ch = 1 if canvas_bpp == 1 else canvas_bpp // 8

    if canvas_w == 0 or canvas_h == 0:
        raise ValueError("Invalid image dimensions")
    if canvas_ch not in (1, 2, 3, 4):
        raise ValueError(f"Unsupported bpp={canvas_bpp}")

    # Read block entries from the offset table.
    # Entries are at 8-byte intervals starting at 0x13C.
    # blocks_count at offset 0x28 limits how many entries to read.
    blocks_count = struct.unpack_from("<I", data, 0x28)[0]
    max_blocks = min(blocks_count, 16)
    blocks = []
    for i in range(max_blocks):
        addr = block_table_off + i * 8
        if addr + 4 > file_size:
            break
        off = struct.unpack_from("<I", data, addr)[0]
        if off == 0 or off + 0x20 >= file_size:
            continue
        bw = struct.unpack_from("<I", data, off + 0x00)[0]
        bh = struct.unpack_from("<I", data, off + 0x04)[0]
        bbpp = struct.unpack_from("<I", data, off + 0x10)[0]
        btype = struct.unpack_from("<I", data, off + 0x18)[0]
        bch = 1 if bbpp == 1 else bbpp // 8
        if bw == 0 or bh == 0 or bch == 0:
            continue
        if btype not in (1, 2, 4, 8, 16):
            continue
        # Detect "fnio" sub-header (CPT9FILE object blocks)
        has_fnio = (off + 0x4C <= file_size and
                    data[off + 0x48:off + 0x4C] == b'fnio')
        # Layer opacity: +0x70 with fnio, +0x64 without
        bopacity = 100
        if btype == 8:
            if has_fnio and off + 0x74 <= file_size:
                bopacity = struct.unpack_from("<I", data, off + 0x70)[0]
                if bopacity > 100:
                    bopacity = 100
            elif not has_fnio and off + 0x68 <= file_size:
                bopacity = struct.unpack_from("<I", data, off + 0x64)[0]
                if bopacity > 100:
                    bopacity = 100
        blocks.append({
            "idx": i, "off": off, "w": bw, "h": bh,
            "ch": bch, "type": btype, "opacity": bopacity,
            "has_fnio": has_fnio,
        })

    # Find object pairs: (type 8 RGB/gray, type 4 alpha)
    # Objects appear after the background (type 1), paired sequentially.
    object_pairs = []
    i = 0
    while i < len(blocks):
        blk = blocks[i]
        if blk["type"] == 8 and blk["ch"] in (1, 3):
            alpha_blk = None
            if i + 1 < len(blocks) and blocks[i + 1]["type"] == 4:
                alpha_blk = blocks[i + 1]
                i += 1
            object_pairs.append((blk, alpha_blk))
        i += 1

    if object_pairs:
        # Multi-layer: composite objects onto background
        out_ch = 3
        # Decode background from Block[0]
        bg_result = _decode_block_tiles(data, block0_off, file_size)
        if bg_result is not None and palette is not None and bg_result[2] == 1:
            bgw, bgh, _, bg_idx = bg_result
            bg_result = (bgw, bgh, 3, _apply_palette(bg_idx, bgw, bgh, palette))
        canvas = bytearray(b"\xff" * (canvas_w * canvas_h * out_ch))
        if bg_result is not None:
            bgw, bgh, bgch, bg_pixels = bg_result
            # Check if background has explicit fill tiles (comp_type=4).
            # Fill tiles with color (0,0,0) indicate a genuinely black
            # background, not a transparent canvas. Without fill tiles,
            # an all-zero background typically means transparent (paper
            # color = white in Corel Photo-Paint).
            bg_has_fills = _block_has_fill_tiles(data, block0_off, file_size)
            use_bg = bg_has_fills or any(b != 0 for b in bg_pixels)
            if use_bg:
                if bgch >= 3 and bgw == canvas_w:
                    # Fast path: same width, direct row copy (RGB to RGB)
                    row_bytes = canvas_w * 3
                    for py in range(canvas_h):
                        si = py * bgw * bgch
                        di = py * canvas_w * out_ch
                        canvas[di:di + row_bytes] = (
                            bg_pixels[si:si + row_bytes]
                        )
                elif bgch >= 3:
                    row_bytes = min(bgw, canvas_w) * 3
                    for py in range(canvas_h):
                        si = py * bgw * bgch
                        di = py * canvas_w * out_ch
                        canvas[di:di + row_bytes] = (
                            bg_pixels[si:si + row_bytes]
                        )
                else:
                    # Grayscale -> RGB expansion
                    for py in range(canvas_h):
                        for px in range(canvas_w):
                            si = py * bgw + px
                            di = (py * canvas_w + px) * out_ch
                            v = bg_pixels[si]
                            canvas[di] = canvas[di + 1] = canvas[di + 2] = v

        # Composite each object layer in order
        for obj_blk, alpha_blk in object_pairs:
            obj_result = _decode_block_tiles(
                data, obj_blk["off"], file_size
            )
            if obj_result is None:
                continue

            obj_w, obj_h, obj_ch, obj_pixels = obj_result
            if palette is not None and obj_ch == 1:
                obj_pixels = _apply_palette(obj_pixels, obj_w, obj_h, palette)
                obj_ch = 3
            if obj_blk.get("has_fnio"):
                # CPT9FILE fnio sub-header: position at +0x4C (x) and +0x58 (y)
                obj_x = struct.unpack_from(
                    "<i", data, obj_blk["off"] + 0x4C
                )[0]
                obj_y = struct.unpack_from(
                    "<i", data, obj_blk["off"] + 0x58
                )[0]
            else:
                obj_x = struct.unpack_from(
                    "<i", data, obj_blk["off"] + 0x44
                )[0]
                obj_y = struct.unpack_from(
                    "<i", data, obj_blk["off"] + 0x50
                )[0]

            # Decode alpha mask if available
            alpha_data = None
            alpha_w = alpha_h = 0
            if alpha_blk is not None:
                alpha_result = _decode_block_tiles(
                    data, alpha_blk["off"], file_size
                )
                if alpha_result is not None:
                    alpha_w, alpha_h, _, alpha_data = alpha_result

            _composite_object(
                canvas, canvas_w, canvas_h, out_ch,
                obj_pixels, obj_w, obj_h, obj_ch,
                obj_x, obj_y, alpha_data, alpha_w, alpha_h,
                opacity=obj_blk["opacity"],
            )

        return canvas_w, canvas_h, out_ch, _flip_vertical(
            canvas_w, canvas_h, out_ch, bytes(canvas)
        )

    # Single-layer: decode directly from Block[0]
    result = _decode_block_tiles(data, block0_off, file_size)
    if result is None:
        raise ValueError("Could not decode tile data from Block[0]")

    w, h, ch, pixels = result
    if palette is not None and ch == 1:
        pixels = _apply_palette(pixels, w, h, palette)
        ch = 3

    # Check for type=2 mask block (transparency mask for single-layer images).
    # When present, combine RGB pixels with the mask to produce RGBA output.
    mask_blk = None
    for blk in blocks:
        if blk["type"] == 2:
            mask_blk = blk
            break

    if mask_blk is not None and ch == 3:
        mask_result = _decode_block_tiles(
            data, mask_blk["off"], file_size
        )
        if mask_result is not None:
            mw, mh, _, mask_data = mask_result
            # Build RGBA output
            rgba = bytearray(w * h * 4)
            for y in range(h):
                for x in range(w):
                    si = (y * w + x) * 3
                    di = (y * w + x) * 4
                    rgba[di] = pixels[si]
                    rgba[di + 1] = pixels[si + 1]
                    rgba[di + 2] = pixels[si + 2]
                    if x < mw and y < mh:
                        rgba[di + 3] = mask_data[y * mw + x]
                    else:
                        rgba[di + 3] = 255
            return w, h, 4, _flip_vertical(w, h, 4, bytes(rgba))

    return w, h, ch, _flip_vertical(w, h, ch, pixels)


def save_png(filename, width, height, channels, pixel_data):
    """Save pixel data as PNG using PIL/Pillow."""
    from PIL import Image

    if channels == 3:
        img = Image.frombytes("RGB", (width, height), pixel_data)
    elif channels == 1:
        img = Image.frombytes("L", (width, height), pixel_data)
    elif channels == 4:
        img = Image.frombytes("RGBA", (width, height), pixel_data)
    elif channels == 2:
        img = Image.frombytes("LA", (width, height), pixel_data)
    else:
        raise ValueError(f"Unsupported channel count: {channels}")

    img.save(filename)


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} input.cpt [output.png]")
        sys.exit(1)

    input_file = sys.argv[1]
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        output_file = os.path.splitext(input_file)[0] + ".png"

    try:
        width, height, channels, pixels = decode_cpt7(input_file)
        save_png(output_file, width, height, channels, pixels)
        mode = {1: "grayscale", 2: "gray+alpha", 3: "RGB", 4: "RGBA"}.get(channels, f"{channels}ch")
        print(f"Converted {input_file} -> {output_file} ({width}x{height}, {mode})")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

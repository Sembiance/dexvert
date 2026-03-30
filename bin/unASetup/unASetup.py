#!/usr/bin/env python3
# Vibe coded by Claude
#
# unASetup.py - ASetup / Eschalon Setup Installer Archive (.ARV) extractor
#
# Usage: python3 unASetup.py <inputFile> <outputDir>
#
# Extracts files from ASetup Installer Archive (.ARV) files.
# Supports both stored (uncompressed) and LZHUF-compressed files.
# LZHUF = Yoshizaki's adaptive Huffman + LZSS compression.

import struct
import sys
import os
import zlib


def read_u8(data, offset):
    return data[offset]


def read_u16le(data, offset):
    return struct.unpack_from('<H', data, offset)[0]


def read_u32le(data, offset):
    return struct.unpack_from('<I', data, offset)[0]


def dos_datetime_to_str(dt):
    """Convert a packed DOS date/time u32 to a human-readable string."""
    if dt == 0:
        return "0000-00-00 00:00:00"
    time_part = dt & 0xFFFF
    date_part = (dt >> 16) & 0xFFFF
    sec = (time_part & 0x1F) * 2
    minute = (time_part >> 5) & 0x3F
    hour = (time_part >> 11) & 0x1F
    day = date_part & 0x1F
    month = (date_part >> 5) & 0x0F
    year = ((date_part >> 9) & 0x7F) + 1980
    return f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{sec:02d}"


def crc32_jamcrc(data):
    """Compute CRC-32/JAMCRC (same as CRC-32 without final inversion)."""
    return zlib.crc32(data) & 0xFFFFFFFF ^ 0xFFFFFFFF ^ 0xFFFFFFFF
    # Actually: JAMCRC = CRC32 without final NOT = crc32(data) XOR 0xFFFFFFFF
    # zlib.crc32 returns the standard CRC-32 (with final NOT applied).
    # JAMCRC = standard_crc32 XOR 0xFFFFFFFF? No...
    # Standard CRC-32 = init=0xFFFFFFFF, final XOR=0xFFFFFFFF
    # JAMCRC = init=0xFFFFFFFF, final XOR=0x00000000
    # So JAMCRC = ~standard_crc32 (bitwise NOT)
    # But zlib.crc32 returns unsigned, so:


def compute_jamcrc(data):
    """Compute CRC-32/JAMCRC."""
    # JAMCRC = bitwise NOT of standard CRC-32
    std_crc = zlib.crc32(data) & 0xFFFFFFFF
    return std_crc ^ 0xFFFFFFFF


# ---------------------------------------------------------------------------
# LZHUF decompression (Yoshizaki's adaptive Huffman + LZSS)
# ---------------------------------------------------------------------------

# Constants
_N_CHAR = 287          # 256 literals + 1 EOF (256) + 30 match-length codes (257-286)
_T = _N_CHAR * 2 - 1  # 573 total tree nodes
_R = _T - 1           # 572, root of the Huffman tree
_MAX_FREQ = 0x8000     # tree reconstruction threshold
_N = 4096             # ring buffer size
_F = 32               # max match length (codes 257-286 => lengths 3-32)
_THRESHOLD = 2        # minimum useful match length

# Custom d_code table (256 bytes) - maps 8-bit position byte to upper bits
_D_CODE = (
    [0] * 32 + [1] * 16 + [2] * 16 + [3] * 16 +
    [4] * 8 + [5] * 8 + [6] * 8 + [7] * 8 +
    [8] * 8 + [9] * 8 + [10] * 8 + [11] * 8 +
    [12] * 4 + [13] * 4 + [14] * 4 + [15] * 4 +
    [16] * 4 + [17] * 4 + [18] * 4 + [19] * 4 +
    [20] * 4 + [21] * 4 + [22] * 4 + [23] * 4 +
    [24] * 2 + [25] * 2 + [26] * 2 + [27] * 2 +
    [28] * 2 + [29] * 2 + [30] * 2 + [31] * 2 +
    [32] * 2 + [33] * 2 + [34] * 2 + [35] * 2 +
    [36] * 2 + [37] * 2 + [38] * 2 + [39] * 2 +
    [40] * 2 + [41] * 2 + [42] * 2 + [43] * 2 +
    [44] * 2 + [45] * 2 + [46] * 2 + [47] * 2 +
    list(range(48, 64))
)

# Custom d_len table (256 bytes) - number of lower bits for each position range
_D_LEN = (
    [3] * 32 + [4] * 48 + [5] * 64 + [6] * 48 + [7] * 48 + [8] * 16
)


def deobfuscate_xor(data, initial_key=0x56):
    """Undo XOR-chain obfuscation used by some ASetup versions.
    state starts at initial_key; each byte: plain = cipher ^ state; state = plain.
    Known keys: 0x56 ('V', most common), 0xAB (bitwise complement variant)."""
    state = initial_key
    out = bytearray(data)
    for i in range(len(out)):
        plain = out[i] ^ state
        out[i] = plain
        state = plain
    return bytes(out)


def decompress_lzhuf(compressed_data, original_size):
    """Decompress LZHUF (adaptive Huffman + LZSS) compressed data.

    Args:
        compressed_data: bytes of compressed data
        original_size: expected size of decompressed output

    Returns:
        bytes of decompressed data

    Raises:
        ValueError: if decompression encounters an error
    """
    # --- Bit reader state ---
    src = compressed_data
    src_len = len(src)
    src_pos = 0
    bit_buf = 0
    bit_count = 0

    def get_byte():
        """Read next byte from compressed stream."""
        nonlocal src_pos
        if src_pos >= src_len:
            return 0
        b = src[src_pos]
        src_pos += 1
        return b

    def get_bit():
        """Read a single bit (MSB first)."""
        nonlocal bit_buf, bit_count
        if bit_count == 0:
            bit_buf = get_byte()
            bit_count = 8
        bit_count -= 1
        result = (bit_buf >> bit_count) & 1
        return result

    # --- Adaptive Huffman tree (follows Yoshizaki's lzhuf.c) ---
    freq = [0] * (_T + 1)
    prnt = [0] * (_T + _N_CHAR)
    son = [0] * _T

    def start_huff():
        """Initialize the adaptive Huffman tree."""
        # Leaf nodes
        for i in range(_N_CHAR):
            freq[i] = 1
            son[i] = i + _T
            prnt[i + _T] = i
        # Internal nodes: pair adjacent children bottom-up
        i = 0
        j = _N_CHAR
        while j <= _R:
            freq[j] = freq[i] + freq[i + 1]
            son[j] = i
            prnt[i] = j
            prnt[i + 1] = j
            i += 2
            j += 1
        freq[_T] = 0xFFFF
        prnt[_R] = 0

    def reconst():
        """Reconstruct the Huffman tree when frequencies overflow."""
        # Collect leaf nodes, halving their frequencies
        j = 0
        for i in range(_T):
            if son[i] >= _T:
                freq[j] = (freq[i] + 1) // 2
                son[j] = son[i]
                j += 1
        # Rebuild internal nodes
        i = 0
        j_idx = _N_CHAR
        while j_idx < _T:
            k = i + 1
            f = freq[i] + freq[k]
            freq[j_idx] = f
            # Find proper position (insertion sort by frequency)
            k2 = j_idx - 1
            while f < freq[k2]:
                k2 -= 1
            k2 += 1
            # Shift entries up to make room
            count = j_idx - k2
            if count > 0:
                freq[k2 + 1:k2 + 1 + count] = freq[k2:k2 + count]
                son[k2 + 1:k2 + 1 + count] = son[k2:k2 + count]
            freq[k2] = f
            son[k2] = i
            i += 2
            j_idx += 1
        # Update parent pointers
        for i in range(_T):
            k = son[i]
            prnt[k] = i
            if k < _T:
                prnt[k + 1] = i

    def update(c):
        """Update the Huffman tree for character c."""
        if freq[_R] == _MAX_FREQ:
            reconst()
        c = prnt[c + _T]
        while True:
            freq[c] += 1
            k = freq[c]
            # Swap with next node if frequency order is violated
            l = c + 1
            if k > freq[l]:
                while k > freq[l]:
                    l += 1
                l -= 1
                freq[c] = freq[l]
                freq[l] = k
                i = son[c]
                prnt[i] = l
                if i < _T:
                    prnt[i + 1] = l
                j = son[l]
                son[l] = i
                prnt[j] = c
                if j < _T:
                    prnt[j + 1] = c
                son[c] = j
                c = l
            c = prnt[c]
            if c == 0:
                break

    def decode_char():
        """Decode one character from the Huffman tree."""
        c = son[_R]
        while c < _T:
            c += get_bit()   # select left (c) or right (c+1) child
            c = son[c]       # follow to child node
        update(c - _T)
        return c - _T

    def decode_position():
        """Decode a match position from the stream."""
        # Read 8 bits through the bit buffer for the lookup
        i = 0
        for _ in range(8):
            i = (i << 1) | get_bit()
        # Use lookup tables for upper bits and bit-length
        c = _D_CODE[i] << 6
        j = _D_LEN[i] - 2
        # Read remaining lower bits
        while j > 0:
            i = (i << 1) | get_bit()
            j -= 1
        return c | (i & 0x3F)

    # --- Main decompression loop ---
    start_huff()

    # Initialize ring buffer with spaces (0x20)
    text_buf = bytearray(b'\x20' * (_N + _F - 1))
    r = _N - _T  # initial position = 4096 - 573 = 3523 (0xDC3)

    output = bytearray()
    count = 0

    while count < original_size:
        c = decode_char()
        if c == 256:
            # EOF marker
            break
        if c < 256:
            # Literal byte
            output.append(c)
            text_buf[r] = c
            r = (r + 1) & (_N - 1)
            count += 1
        else:
            # Match: length is (code - 254), position from stream
            match_len = c - 254  # codes 257-286 => lengths 3-32
            match_pos = decode_position()
            match_pos = (r - match_pos - 1) & (_N - 1)
            for k in range(match_len):
                c = text_buf[(match_pos + k) & (_N - 1)]
                output.append(c)
                text_buf[r] = c
                r = (r + 1) & (_N - 1)
                count += 1
                if count >= original_size:
                    break

    return bytes(output)


def parse_arcv(filepath):
    """Parse an ARCV archive file and return header info and block list."""
    with open(filepath, 'rb') as f:
        data = f.read()

    if len(data) < 14 or data[:4] != b'ARCV':
        raise ValueError(f"Not an ARCV file: {filepath}")

    archive = {
        'magic': 'ARCV',
        'version': read_u16le(data, 4),
        'header_size': read_u16le(data, 6),
        'disk_count': read_u16le(data, 8),
        'reserved': read_u16le(data, 10),
        'volume_number': read_u16le(data, 12),
        'blocks': [],
        'file_size': len(data),
    }

    pos = archive['header_size']

    while pos < len(data):
        if pos + 4 > len(data) or data[pos:pos + 4] != b'BLCK':
            # Try to find the next BLCK marker (handles edge cases)
            next_blck = data.find(b'BLCK', pos)
            if next_blck == -1:
                break
            pos = next_blck

        block = {}
        block['offset'] = pos
        block['version'] = read_u16le(data, pos + 4)
        block['header_size'] = read_u16le(data, pos + 6)
        block['method'] = read_u32le(data, pos + 8)
        block['compressed_size'] = read_u32le(data, pos + 12)

        # Derive name_len from header_size (more reliable than the raw byte)
        derived_name_len = block['header_size'] - 45
        raw_name_len = read_u8(data, pos + 16)

        # Use derived length if it's reasonable, otherwise fall back to raw byte
        if 0 < derived_name_len <= 260:
            name_len = derived_name_len
        else:
            name_len = raw_name_len

        # Read filename and strip null bytes and trailing garbage
        raw_name = data[pos + 17:pos + 17 + name_len]
        null_idx = raw_name.find(b'\x00')
        if null_idx >= 0:
            raw_name = raw_name[:null_idx]
        block['filename'] = raw_name.decode('ascii', errors='replace')
        n = name_len

        block['original_size'] = read_u32le(data, pos + 17 + n)
        block['compressed_size_dup'] = read_u32le(data, pos + 21 + n)
        block['attributes'] = read_u32le(data, pos + 25 + n)
        block['datetime'] = read_u32le(data, pos + 29 + n)
        block['datetime_str'] = dos_datetime_to_str(block['datetime'])

        block['ver_minor1'] = read_u16le(data, pos + 33 + n)
        block['ver_major1'] = read_u16le(data, pos + 35 + n)
        block['ver_minor2'] = read_u16le(data, pos + 37 + n)
        block['ver_major2'] = read_u16le(data, pos + 39 + n)
        block['crc'] = read_u32le(data, pos + 41 + n)

        block['data_offset'] = pos + block['header_size']
        data_end = block['data_offset'] + block['compressed_size']

        if data_end > len(data):
            # Multi-volume: compressed data extends past this file
            block['data'] = data[block['data_offset']:]
            block['truncated'] = True
        else:
            block['data'] = data[block['data_offset']:data_end]
            block['truncated'] = False

        block['is_stored'] = (block['compressed_size'] == block['original_size']
                              and not block['truncated'])

        archive['blocks'].append(block)
        pos = min(data_end, len(data))

    archive['bytes_accounted'] = pos
    return archive


def extract_arcv(input_path, output_dir):
    """Extract files from an ARCV archive."""
    archive = parse_arcv(input_path)

    ver_major = archive['version'] >> 8
    ver_minor = archive['version'] & 0xFF
    print(f"ARCV version {ver_major}.{ver_minor}")
    print(f"Volume {archive['volume_number']} of {archive['disk_count']}")
    print(f"Archive size: {archive['file_size']} bytes")
    print(f"Files: {len(archive['blocks'])}")
    print()

    os.makedirs(output_dir, exist_ok=True)

    extracted = 0
    skipped = 0

    for block in archive['blocks']:
        filename = block['filename']
        # Sanitize path separators
        safe_name = filename.replace('\\', os.sep).replace('/', os.sep)

        # Create subdirectories if needed
        out_path = os.path.join(output_dir, safe_name)
        out_dir = os.path.dirname(out_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        ver_str = ""
        if block['ver_major1'] or block['ver_minor1']:
            ver_str = f" v{block['ver_major1']}.{block['ver_minor1']}"
            if block['ver_major2'] or block['ver_minor2']:
                ver_str += f".{block['ver_major2']}.{block['ver_minor2']}"

        status = ""

        if block.get('truncated'):
            status = "TRUNCATED (multi-volume, data continues in next file)"
            skipped += 1
        elif block['is_stored']:
            # File is stored without compression - extract directly
            with open(out_path, 'wb') as f:
                f.write(block['data'])

            # Verify CRC
            computed_crc = compute_jamcrc(block['data'])
            if computed_crc == block['crc']:
                status = "OK"
            else:
                status = f"CRC MISMATCH (expected 0x{block['crc']:08X}, got 0x{computed_crc:08X})"
            extracted += 1
        else:
            # Compressed file - attempt LZHUF decompression
            # Try direct first, then with known XOR keys
            decompressed = None
            decomp_error = ""
            attempts = [
                ("direct", block['data']),
                ("xor-0x56", deobfuscate_xor(block['data'], 0x56)),
                ("xor-0xAB", deobfuscate_xor(block['data'], 0xAB)),
            ]
            for attempt, payload in attempts:
                try:
                    result = decompress_lzhuf(payload, block['original_size'])
                    if len(result) == block['original_size']:
                        decompressed = result
                        break
                except Exception as e:
                    decomp_error = str(e)

            if decompressed is not None and len(decompressed) == block['original_size']:
                # Decompression succeeded and produced expected size
                with open(out_path, 'wb') as f:
                    f.write(decompressed)

                # Verify CRC-32/JAMCRC on the COMPRESSED data
                computed_crc = compute_jamcrc(block['data'])
                if computed_crc == block['crc']:
                    status = "OK (decompressed)"
                else:
                    status = (f"DECOMPRESSED, CRC MISMATCH on compressed data "
                              f"(expected 0x{block['crc']:08X}, "
                              f"got 0x{computed_crc:08X})")
                extracted += 1
            else:
                # Decompression failed or produced wrong size - save raw data
                if decompressed is not None:
                    reason = (f"size mismatch: got {len(decompressed)}, "
                              f"expected {block['original_size']}")
                else:
                    reason = decomp_error

                with open(out_path + '.compressed', 'wb') as f:
                    f.write(block['data'])

                # Write metadata
                with open(out_path + '.meta', 'w') as f:
                    f.write(f"filename={block['filename']}\n")
                    f.write(f"original_size={block['original_size']}\n")
                    f.write(f"compressed_size={block['compressed_size']}\n")
                    f.write(f"method=0x{block['method']:08X}\n")
                    f.write(f"crc=0x{block['crc']:08X}\n")
                    f.write(f"datetime={block['datetime_str']}\n")
                    f.write(f"attributes=0x{block['attributes']:08X}\n")
                    if block['ver_major1'] or block['ver_minor1']:
                        f.write(f"version={block['ver_major1']}.{block['ver_minor1']}")
                        f.write(f".{block['ver_major2']}.{block['ver_minor2']}\n")
                    f.write(f"decompress_error={reason}\n")

                status = f"COMPRESSED (decompression failed: {reason})"
                skipped += 1

        comp_ratio = block['compressed_size'] / block['original_size'] if block['original_size'] > 0 else 0
        print(f"  {filename:30s} {block['original_size']:>10d} -> {block['compressed_size']:>10d} "
              f"({comp_ratio:.1%}) {block['datetime_str']}{ver_str}  [{status}]")

    print()
    print(f"Extracted: {extracted} files")
    if skipped:
        print(f"Skipped:   {skipped} files (decompression failed or truncated)")
        print(f"           Compressed data saved as .compressed files with .meta metadata")

    leftover = archive['file_size'] - archive['bytes_accounted']
    if leftover != 0:
        print(f"WARNING: {leftover} unaccounted bytes at end of archive")


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>")
        print()
        print("Extracts files from ASetup Installer Archive (.ARV) files.")
        print("Supports both stored and LZHUF-compressed files.")
        sys.exit(1)

    input_path = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(input_path):
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    try:
        extract_arcv(input_path, output_dir)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

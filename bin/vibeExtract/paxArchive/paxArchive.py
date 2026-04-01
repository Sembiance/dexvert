#!/usr/bin/env python3
# Vibe coded by Claude
"""
PAX Archive Extractor for GEM-View (Atari ST)

Extracts files from .PAX archives created by GEM-View's LZF0/LZFG compression.
The compression uses LZSS with adaptive Huffman coding (LZH variant).

Usage: python3 paxArchive.py <inputFile> <outputDir>
"""

import sys
import os
import struct
from datetime import datetime


# ---------------------------------------------------------------------------
# CRC-16 (polynomial 0x8005, reflected as 0xA001)
# ---------------------------------------------------------------------------

def _build_crc16_table():
    table = []
    for i in range(256):
        crc = i
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
        table.append(crc & 0xFFFF)
    return table

_CRC16_TABLE = _build_crc16_table()

def crc16(data, init=0):
    crc = init & 0xFFFF
    for b in data:
        idx = (crc ^ b) & 0xFF
        crc = (crc >> 8) ^ _CRC16_TABLE[idx]
    return crc & 0xFFFF


# ---------------------------------------------------------------------------
# Bit reader – reads from a byte buffer, MSB first
# ---------------------------------------------------------------------------

class BitReader:
    def __init__(self, data):
        self.data = data
        self.pos = 0        # byte position
        self.bit_buf = 0    # 32-bit buffer
        self.bits_left = 0  # bits remaining in buffer

    def _refill(self):
        """Load up to 4 bytes into the bit buffer."""
        while self.bits_left <= 24 and self.pos < len(self.data):
            self.bit_buf = ((self.bit_buf << 8) | self.data[self.pos]) & 0xFFFFFFFF
            self.bits_left += 8
            self.pos += 1

    def get_bits(self, n):
        """Read n bits (1-16) from the stream, MSB first."""
        while self.bits_left < n:
            if self.pos < len(self.data):
                self.bit_buf = ((self.bit_buf << 8) | self.data[self.pos]) & 0xFFFFFFFF
                self.bits_left += 8
                self.pos += 1
            else:
                # Pad with zeros at end of stream
                self.bit_buf = (self.bit_buf << 8) & 0xFFFFFFFF
                self.bits_left += 8
        self.bits_left -= n
        result = (self.bit_buf >> self.bits_left) & ((1 << n) - 1)
        self.bit_buf &= (1 << self.bits_left) - 1 if self.bits_left > 0 else 0
        return result

    @property
    def bytes_consumed(self):
        """Total bytes consumed from the input so far."""
        return self.pos


# ---------------------------------------------------------------------------
# Adaptive Huffman tree
# ---------------------------------------------------------------------------

class HuffmanTree:
    """
    Adaptive Huffman tree matching the LZFG compressor (Atari ST).

    Leaf nodes: indices 0 .. (num_symbols-1)
    Internal nodes: indices num_symbols .. (2*num_symbols-2)
    Root: index (2*num_symbols-2)

    Tree is rebuilt from frequency counts using a two-queue merge
    that exactly matches the original Atari ST implementation order.
    """

    def __init__(self, num_symbols, max_update):
        self.num_symbols = num_symbols
        self.total_nodes = 2 * num_symbols - 1
        self.max_update = max_update

        # Node arrays
        self.son0 = [0] * self.total_nodes   # child for bit=0
        self.son1 = [0] * self.total_nodes   # child for bit=1
        self.freq = [0] * self.total_nodes

        # Initialize leaf nodes with freq=1
        for i in range(num_symbols):
            self.freq[i] = 1

        # Adaptive rebuild tracking
        self.decode_count = 0
        self.rebuild_threshold = max(num_symbols // 2, 1)

        # Build initial tree
        self._build_tree()

    def _build_tree(self, build_freqs=None):
        """
        Build Huffman tree from frequency counts.

        Matches the original Atari ST LZFG algorithm exactly:
        - Uses build_freqs for tree construction (pre-halving freqs during rebuild)
        - Leaves with freq <= 1 go into a 'low' queue in descending index order
        - Leaves with freq > 1 go into a 'high' queue sorted by (freq, index)
        - Both queues are concatenated into a single sequential leaf buffer
        - Merge picks smallest from leaf buffer or internal node queue;
          ties favor the leaf buffer (matching original 'bhi' comparison)
        """
        n = self.num_symbols
        SENTINEL = 0x7FFF

        if build_freqs is None:
            build_freqs = [self.freq[i] for i in range(n)]

        # Separate into low-freq (<=1) and high-freq (>1)
        # Low-freq: descending index order (matching original right-to-left scan)
        low_entries = []
        high_entries = []
        for i in range(n - 1, -1, -1):
            if build_freqs[i] <= 1:
                low_entries.append((build_freqs[i], i))
            else:
                high_entries.append((build_freqs[i], i))

        # High-freq entries sorted by (freq, index) — matches original qsort
        high_entries.sort()

        # Concatenate into single leaf buffer: low first, then high
        # This matches the original memory layout where both share one buffer
        leaf_buf = low_entries + high_entries

        # Internal node queue (filled during construction, naturally freq-sorted)
        int_q = []
        leaf_idx = 0

        def _pop_smallest():
            nonlocal leaf_idx
            lf = leaf_buf[leaf_idx][0] if leaf_idx < len(leaf_buf) else SENTINEL
            nf = int_q[0][0] if int_q else SENTINEL

            # Original: if leaf_freq <= internal_freq, take from leaf buffer
            if lf <= nf:
                entry = leaf_buf[leaf_idx]
                leaf_idx += 1
                return entry
            return int_q.pop(0)

        # Build internal nodes
        node_idx = n
        while node_idx < self.total_nodes:
            f1, c1 = _pop_smallest()
            f2, c2 = _pop_smallest()

            combined = f1 + f2
            self.son0[node_idx] = c1
            self.son1[node_idx] = c2
            self.freq[node_idx] = combined

            int_q.append((combined, node_idx))
            node_idx += 1

        self.root = self.total_nodes - 1

    def decode(self, bit_reader):
        """Decode one symbol from the bit stream."""
        node = self.root

        # Traverse tree until we reach a leaf
        while node >= self.num_symbols:
            bit = bit_reader.get_bits(1)
            if bit:
                node = self.son1[node]
            else:
                node = self.son0[node]

        symbol = node

        # Update frequency
        self.freq[symbol] += 1

        # Check if rebuild needed (original checks old_count >= threshold AFTER increment)
        self.decode_count += 1
        if self.decode_count > self.rebuild_threshold:
            # Save pre-halving frequencies for tree building
            # (original pushes original freq to sort buffer, then halves stored freq)
            orig_freqs = [self.freq[i] for i in range(self.num_symbols)]

            # Halve frequencies > 1 (with rounding up) for future tracking
            for i in range(self.num_symbols):
                if self.freq[i] > 1:
                    self.freq[i] = (self.freq[i] + 1) // 2

            # Build tree using original (pre-halving) frequencies
            self._build_tree(orig_freqs)

            # Double the threshold, capped at max_update
            self.rebuild_threshold = min(self.rebuild_threshold * 2, self.max_update)
            self.decode_count = 0

        return symbol


# ---------------------------------------------------------------------------
# LZH Decompressor
# ---------------------------------------------------------------------------

def lzh_decompress(compressed_data, uncompressed_size):
    """
    Decompress LZH (LZSS + adaptive Huffman) compressed data.

    Returns (decompressed_bytes, bytes_consumed) tuple.
    """
    if uncompressed_size == 0:
        return b'', 0

    reader = BitReader(compressed_data)

    # --- Read bitstream header (58 bits) ---
    n1 = reader.get_bits(4)          # dic_bits_hi (typically 15)
    n2 = reader.get_bits(4)          # dic_bits_lo (typically 11)
    threshold_adj = reader.get_bits(5)  # typically 1
    num_entries = reader.get_bits(10)   # typically 254
    map_bits = reader.get_bits(3)       # typically 3 (= min match length)
    pos_update = reader.get_bits(16)    # typically 8192
    len_update = reader.get_bits(16)    # typically 4096

    # Derived parameters
    threshold = (1 << n1) - threshold_adj   # dictionary window size (32767)
    max_match = num_entries + map_bits - 1  # max match length (256)
    dic_size = threshold + max_match        # total dictionary size (33023)
    num_code_syms = (1 << (n1 - n2)) + 256  # code tree symbols (272)

    # --- Initialize dictionary with spaces ---
    dictionary = bytearray(b'\x20' * dic_size)

    # --- Create Huffman trees ---
    code_tree = HuffmanTree(num_code_syms, pos_update)
    length_tree = HuffmanTree(num_entries, len_update)

    # --- Decompress ---
    output = bytearray()
    dict_pos = 0
    remaining = uncompressed_size

    while remaining > 0:
        # Decode symbol from code tree
        symbol = code_tree.decode(reader)

        if symbol < 256:
            # Literal byte
            dictionary[dict_pos] = symbol
            if dict_pos < max_match:
                dictionary[dict_pos + threshold] = symbol
            dict_pos += 1
            remaining -= 1

            # Flush dictionary when full
            if dict_pos >= threshold:
                output.extend(dictionary[:threshold])
                dict_pos = 0
        else:
            # Back-reference
            pos_upper = symbol - 256
            position = (pos_upper << n2) | reader.get_bits(n2)

            length_sym = length_tree.decode(reader)
            match_length = length_sym + map_bits

            # Calculate source position (circular)
            source = (dict_pos - position - match_length) % threshold
            if source < 0:
                source += threshold

            # Handle potential overlap by reading source first
            if (source < dict_pos and source + match_length > dict_pos):
                # Overlap: copy source to temp buffer
                temp = bytearray(match_length)
                for j in range(match_length):
                    temp[j] = dictionary[(source + j) % dic_size]
                src_data = temp
                src_offset = 0
            else:
                src_data = dictionary
                src_offset = source

            # Copy match
            for j in range(match_length):
                byte = src_data[src_offset + j]
                dictionary[dict_pos] = byte
                if dict_pos < max_match:
                    dictionary[dict_pos + threshold] = byte
                dict_pos += 1
                remaining -= 1

                # Flush dictionary when full
                if dict_pos >= threshold:
                    output.extend(dictionary[:threshold])
                    dict_pos = 0

                if remaining <= 0:
                    break

    # Flush remaining data in dictionary
    if dict_pos > 0:
        output.extend(dictionary[:dict_pos])

    return bytes(output[:uncompressed_size]), reader.pos


# ---------------------------------------------------------------------------
# PAX Archive Parser
# ---------------------------------------------------------------------------

MAGIC = b'LZF0'

def decode_tos_date(date_word):
    """Decode TOS/DOS date format: bits 15-9=year-1980, 8-5=month, 4-0=day."""
    year = ((date_word >> 9) & 0x7F) + 1980
    month = (date_word >> 5) & 0x0F
    day = date_word & 0x1F
    return year, month, day

def decode_tos_time(time_word):
    """Decode TOS/DOS time format: bits 15-11=hour, 10-5=minute, 4-0=seconds/2."""
    hour = (time_word >> 11) & 0x1F
    minute = (time_word >> 5) & 0x3F
    second = (time_word & 0x1F) * 2
    return hour, minute, second


def parse_pax_archive(data):
    """
    Parse a PAX archive file and yield entry tuples.

    Yields: (filename, file_size, ftime, fdate, attrib, code_type,
             header_crc, first_bytes, compressed_data, entry_offset)
    """
    pos = 0
    while pos < len(data):
        # Find next LZF0 magic
        idx = data.find(MAGIC, pos)
        if idx == -1:
            break

        entry_offset = idx

        # Verify we have enough data for the fixed header (30 bytes minimum)
        if idx + 30 > len(data):
            break

        # Parse fixed header (28 bytes + 2 bytes for filename length)
        magic = data[idx:idx+4]
        assert magic == MAGIC

        first_bytes = data[idx+4:idx+8]
        file_size = struct.unpack('>I', data[idx+8:idx+12])[0]
        ftime = struct.unpack('>H', data[idx+12:idx+14])[0]
        fdate = struct.unpack('>H', data[idx+14:idx+16])[0]
        attrib = struct.unpack('>H', data[idx+16:idx+18])[0]
        head_len = struct.unpack('>H', data[idx+18:idx+20])[0]
        header_crc = struct.unpack('>H', data[idx+20:idx+22])[0]
        pad1 = data[idx+22]
        code_type = chr(data[idx+23])
        reserved = struct.unpack('>I', data[idx+24:idx+28])[0]
        pad2 = data[idx+28]
        fname_len = data[idx+29]

        # Read filename
        fname_start = idx + 30
        fname_end = fname_start + fname_len
        if fname_end > len(data):
            break
        filename_raw = data[fname_start:fname_end]
        # Strip null terminator
        filename = filename_raw.rstrip(b'\x00').decode('latin-1')

        # Find compressed data extent (until next LZF0 or EOF)
        comp_start = fname_end
        next_magic = data.find(MAGIC, comp_start)
        if next_magic == -1:
            comp_end = len(data)
        else:
            comp_end = next_magic
        compressed_data = data[comp_start:comp_end]

        yield (filename, file_size, ftime, fdate, attrib, code_type,
               header_crc, first_bytes, compressed_data, entry_offset)

        pos = comp_end


def extract_pax(input_path, output_dir):
    """Extract all files from a PAX archive."""
    with open(input_path, 'rb') as f:
        data = f.read()

    archive_name = os.path.basename(input_path)
    print(f"Extracting: {archive_name} ({len(data)} bytes)")
    print()

    os.makedirs(output_dir, exist_ok=True)

    entry_count = 0
    error_count = 0

    for (filename, file_size, ftime, fdate, attrib, code_type,
         header_crc, first_bytes, compressed_data, entry_offset) in parse_pax_archive(data):

        entry_count += 1

        # Decode timestamp
        year, month, day = decode_tos_date(fdate)
        hour, minute, second = decode_tos_time(ftime)
        try:
            timestamp = datetime(year, max(month, 1), max(day, 1),
                                 hour, minute, min(second, 59))
            ts_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            ts_str = f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"

        # Convert Atari ST path separators to OS path
        os_filename = filename.replace('\\', os.sep)

        print(f"  [{entry_count:3d}] {filename}")
        print(f"        Size: {file_size:>10d}  Compressed: {len(compressed_data):>10d}"
              f"  Date: {ts_str}  Attr: 0x{attrib:04X}  Type: {code_type}")

        # Decompress
        bytes_consumed = len(compressed_data)
        try:
            if code_type == 'L':
                decompressed, bytes_consumed = lzh_decompress(compressed_data, file_size)
            elif code_type == 'N':
                decompressed = compressed_data[:file_size]
                bytes_consumed = file_size
            elif code_type == 'F':
                print(f"        ERROR: Huffman-only mode not implemented")
                error_count += 1
                continue
            else:
                print(f"        ERROR: Unknown compression type '{code_type}'")
                error_count += 1
                continue
        except Exception as e:
            print(f"        ERROR: Decompression failed: {e}")
            error_count += 1
            continue

        # Verify CRC over decompressed output (matching original Atari ST behavior)
        computed_crc = crc16(decompressed)
        if computed_crc != header_crc:
            print(f"        WARNING: CRC mismatch! Header: 0x{header_crc:04X}"
                  f"  Computed: 0x{computed_crc:04X}")

        # Verify size
        if len(decompressed) != file_size:
            print(f"        WARNING: Size mismatch! Expected {file_size},"
                  f" got {len(decompressed)}")

        # Verify first 4 bytes match header preview
        if file_size >= 4 and decompressed[:4] != first_bytes:
            print(f"        WARNING: First-bytes mismatch!"
                  f" Header: {first_bytes.hex()}"
                  f"  Actual: {decompressed[:4].hex()}")

        # Write output file
        out_path = os.path.join(output_dir, os_filename)
        out_dir = os.path.dirname(out_path)
        os.makedirs(out_dir, exist_ok=True)

        with open(out_path, 'wb') as f:
            f.write(decompressed)

        # Set file modification time
        try:
            ts = datetime(year, max(month, 1), max(day, 1),
                          hour, minute, min(second, 59))
            mtime = ts.timestamp()
            os.utime(out_path, (mtime, mtime))
        except (ValueError, OSError):
            pass

    print()
    print(f"Done: {entry_count} entries extracted"
          f"{f', {error_count} errors' if error_count else ''}")

    return error_count == 0


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(input_file):
        print(f"Error: '{input_file}' not found")
        sys.exit(1)

    success = extract_pax(input_file, output_dir)
    sys.exit(0 if success else 1)

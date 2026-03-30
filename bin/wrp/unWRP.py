#!/usr/bin/env python3
# Vibe coded by Claude

"""
unWRP.py - Amiga Warp Disk Image (.WRP) extractor

Extracts Amiga Disk File (.ADF) images and any extra data blocks from
Warp v1.1 compressed disk images.

Usage: unWRP.py <inputFile> <outputDir>

Warp was a disk compression tool for the Amiga, storing floppy disk images
as compressed track data using LZW, Huffman, and/or RLE compression.
"""

import sys
import os
import struct
from pathlib import Path


# --- Constants ---

MAGIC = b"Warp v1.1\x00"
MAGIC_LEN = 10
HEADER_LEN = 26
SIDE_TOP = b"TOP\x00"
SIDE_BOT = b"BOT\x00"
SIDE_NONE = b"\xff\xff\xff\xff"

TRACKS_PER_DISK = 80
SIDES_PER_TRACK = 2
SECTORS_PER_SIDE = 11
BYTES_PER_SECTOR = 512
SECTOR_EXTRA = 16  # extra bytes per sector in decompressed track data

HALF_TRACK_DATA = SECTORS_PER_SIDE * BYTES_PER_SECTOR           # 5632
HALF_TRACK_RAW = SECTORS_PER_SIDE * (BYTES_PER_SECTOR + SECTOR_EXTRA)  # 5808
ADF_SIZE = TRACKS_PER_DISK * SIDES_PER_TRACK * HALF_TRACK_DATA  # 901120

ALGO_RAW = 0         # raw copy, no compression
ALGO_Z_COMPRESS = 1  # LZW (Unix Z-compress) + RLE
ALGO_ARC_SQUEEZE = 2 # ARC Squeeze (Huffman) + RLE
ALGO_RLE = 3         # RLE only

EOF_PAD_BYTE = 0x1A  # CP/M-style EOF padding sometimes appended


# --- CRC16 ---

def _make_crc16_table():
    """Build the CRC16 lookup table (polynomial 0xA001, reflected)."""
    table = [0] * 256
    for i in range(256):
        k = i
        for _ in range(8):
            if k & 1:
                k = (k >> 1) ^ 0xA001
            else:
                k >>= 1
        table[i] = k
    return table

_CRC16_TABLE = _make_crc16_table()

def crc16(data):
    """Compute WRP CRC16 over a bytes-like object."""
    crc = 0
    for b in data:
        crc = _CRC16_TABLE[(crc ^ b) & 0xFF] ^ (crc >> 8)
    return crc & 0xFFFF


# --- RLE decoder (0x90-escape scheme) ---

def rle_decode(data):
    """
    Decode 0x90-based RLE stream.

    Encoding:
      - Normal byte: output as-is, remember as 'last byte'
      - 0x90 (escape): enter repeat mode
        - followed by 0x00: output literal 0x90
        - followed by N (1..255): output last byte N-1 more times
    """
    output = bytearray()
    state = 0  # bits 0-7: last byte, bit 8: in-repeat-mode flag
    for byte in data:
        count = 0
        if state & 0x100:
            # In repeat mode: byte is the repeat count
            if byte == 0:
                # Escape for literal 0x90
                state = 0x90
                count = 1
            else:
                state &= 0xFF
                count = byte - 1
        elif byte == 0x90:
            # Enter repeat mode
            state |= 0x100
        else:
            state = byte
            count = 1
        for _ in range(count):
            output.append(state & 0xFF)
    return bytes(output)


# --- LZW decompressor (Unix Z-compress compatible) ---

def decompress_lzw(data, maxbits=12, block_compress=True):
    """
    Decompress LZW data in the Unix 'compress' format.

    This is the same algorithm as Unix compress(1), with codes read
    LSB-first in groups of n_bits bytes at a time.

    Args:
        data: compressed byte stream (without the header byte)
        maxbits: maximum code size in bits (always 12 for WRP)
        block_compress: if True, code 256 is a clear code
    """
    if not data:
        return b""

    CLEAR_CODE = 256
    FIRST_FREE = 257 if block_compress else 256
    maxmaxcode = 1 << maxbits

    # LZW tables
    tab_prefix = [0] * maxmaxcode
    tab_suffix = [0] * maxmaxcode
    for i in range(256):
        tab_suffix[i] = i

    # Bit reader state
    n_bits = 9
    maxcode = (1 << n_bits) - 1
    free_ent = FIRST_FREE
    clear_flg = 0

    buf = bytearray(maxbits)
    offset_bits = 0
    size_bits = 0
    inpos = 0
    insize = len(data)
    output = bytearray()

    def getcode():
        nonlocal n_bits, maxcode, free_ent, clear_flg, offset_bits, size_bits, inpos, insize

        if clear_flg > 0 or offset_bits >= size_bits or free_ent > maxcode:
            if free_ent > maxcode:
                n_bits += 1
                if n_bits == maxbits:
                    maxcode = maxmaxcode
                else:
                    maxcode = (1 << n_bits) - 1
            if clear_flg > 0:
                n_bits = 9
                maxcode = (1 << n_bits) - 1
                clear_flg = 0

            # Read up to n_bits bytes into the buffer
            sz = 0
            while sz < n_bits and insize > 0:
                buf[sz] = data[inpos]
                inpos += 1
                insize -= 1
                sz += 1
            if sz == 0:
                return -1

            offset_bits = 0
            size_bits = (sz << 3) - (n_bits - 1)

        r_off = offset_bits
        bits = n_bits
        bp = r_off >> 3
        r_off &= 7

        # Assemble code from buffer bytes (LSB first)
        code = buf[bp] >> r_off
        bp += 1
        bits -= 8 - r_off
        shift = 8 - r_off

        if bits >= 8:
            code |= buf[bp] << shift
            bp += 1
            shift += 8
            bits -= 8

        if bits > 0:
            code |= (buf[bp] & ((1 << bits) - 1)) << shift

        offset_bits += n_bits
        return code

    # Read first code
    code = getcode()
    if code == -1:
        return bytes(output)

    finchar = oldcode = code
    output.append(finchar & 0xFF)

    while True:
        code = getcode()
        if code == -1:
            break

        if code == CLEAR_CODE and block_compress:
            for i in range(256):
                tab_prefix[i] = 0
            clear_flg = 1
            free_ent = FIRST_FREE - 1
            code = getcode()
            if code == -1:
                break

        incode = code
        stack = []

        # Handle KwKwK special case
        if code >= free_ent:
            if code > free_ent:
                break  # corrupt data
            stack.append(finchar)
            code = oldcode

        # Walk the chain to build the string
        while code >= 256:
            stack.append(tab_suffix[code])
            code = tab_prefix[code]

        finchar = tab_suffix[code]
        stack.append(finchar)

        # Output in forward order (stack is reversed)
        while stack:
            output.append(stack.pop())

        # Add new table entry
        if free_ent < maxmaxcode:
            tab_prefix[free_ent] = oldcode
            tab_suffix[free_ent] = finchar
            free_ent += 1

        oldcode = incode

    return bytes(output)


# --- ARC Squeeze (Huffman) decompressor ---

def decompress_squeeze(data):
    """
    Decompress ARC Squeeze (Huffman) encoded data.

    Format:
      - uint16 LE: number of tree nodes
      - node[0..numnodes-1]: pairs of int16 LE (left, right children)
        Negative values are leaf nodes: decoded symbol = -(value + 1)
        Special end-of-file symbol = 256 (SPEOF)
      - Bit stream of Huffman codes (LSB first)
    """
    SPEOF = 256
    NUMVALS = 257

    bitbuf = 0
    bitnum = 0
    inpos = 0

    def getbits(nbits):
        nonlocal bitbuf, bitnum, inpos
        while bitnum < nbits:
            if inpos >= len(data):
                return None
            bitbuf |= data[inpos] << bitnum
            inpos += 1
            bitnum += 8
        x = bitbuf & ((1 << nbits) - 1)
        bitbuf >>= nbits
        bitnum -= nbits
        return x

    # Read number of Huffman tree nodes
    numnodes = getbits(16)
    if numnodes is None:
        return None
    if numnodes >= 0x8000:
        numnodes -= 0x10000
    if numnodes < 0 or numnodes >= NUMVALS:
        return None

    # Read Huffman tree (binary tree stored as flat array)
    # Default: both children point to SPEOF (for possible empty tree)
    node = [0] * (2 * NUMVALS)
    node[0] = -(SPEOF + 1)
    node[1] = -(SPEOF + 1)

    for i in range(numnodes * 2):
        v = getbits(16)
        if v is None:
            return None  # truncated tree
        if v >= 0x8000:
            v -= 0x10000
        node[i] = v

    # Decode the bitstream using the Huffman tree
    output = bytearray()
    while True:
        i = 0
        while i >= 0:
            bit = getbits(1)
            if bit is None:
                return bytes(output)  # end of data
            i = node[2 * i + bit]

        symbol = -(i + 1)
        if symbol == SPEOF:
            break
        output.append(symbol & 0xFF)

    return bytes(output)


# --- Record parsing ---

class WrpRecord:
    """A single record (track half) from a WRP file."""
    __slots__ = ("offset", "track", "side", "version", "reserved",
                 "algo", "crc", "data_size", "data")

    def __init__(self, offset, header_bytes, data):
        self.offset = offset
        self.track = (header_bytes[10] << 8) | header_bytes[11]
        self.side = header_bytes[12:16]
        self.version = (header_bytes[16] << 8) | header_bytes[17]
        self.reserved = header_bytes[18]
        self.algo = header_bytes[19]
        self.crc = (header_bytes[20] << 8) | header_bytes[21]
        self.data_size = struct.unpack(">I", header_bytes[22:26])[0]
        self.data = data

    @property
    def side_name(self):
        if self.side == SIDE_TOP:
            return "TOP"
        elif self.side == SIDE_BOT:
            return "BOT"
        elif self.side == SIDE_NONE:
            return "NONE"
        return self.side.hex()

    @property
    def is_track_data(self):
        """True if this record contributes to the disk image."""
        return (self.side in (SIDE_TOP, SIDE_BOT) and
                0 <= self.track <= 79)

    @property
    def is_extra_data(self):
        """True if this is a non-track (FFFF) data block."""
        return self.track == 0xFFFF

    @property
    def disk_offset(self):
        """Byte offset in the ADF image, or -1 for non-track records."""
        if not self.is_track_data:
            return -1
        side_idx = 0 if self.side == SIDE_TOP else 1
        return (self.track * SIDES_PER_TRACK + side_idx) * HALF_TRACK_DATA

    @property
    def algo_name(self):
        names = {0: "raw", 1: "lzw+rle", 2: "squeeze+rle", 3: "rle"}
        return names.get(self.algo, f"unknown({self.algo})")


def parse_records(file_data):
    """
    Parse all WRP records from file data.

    Handles:
      - Normal sequential records
      - 0x1A EOF padding at end of file
      - Misaligned records (searches for next magic if expected position invalid)

    Returns list of WrpRecord objects and list of warning strings.
    """
    records = []
    warnings = []
    pos = 0
    fsize = len(file_data)

    while pos + HEADER_LEN <= fsize:
        magic = file_data[pos:pos + MAGIC_LEN]

        if magic != MAGIC:
            # Check for trailing padding (0x1A EOF markers and/or 0x00 fill)
            remaining = file_data[pos:]
            if all(b in (EOF_PAD_BYTE, 0x00) for b in remaining):
                break

            # Try to find next valid record (handles misaligned files)
            next_pos = file_data.find(MAGIC, pos)
            if next_pos >= 0 and next_pos + HEADER_LEN <= fsize:
                gap = next_pos - pos
                warnings.append(
                    f"Skipped {gap} byte(s) at offset {pos} to reach "
                    f"next record at {next_pos}"
                )
                pos = next_pos
                continue
            break

        header = file_data[pos:pos + HEADER_LEN]
        data_size = struct.unpack(">I", header[22:26])[0]
        data_end = pos + HEADER_LEN + data_size
        available = min(data_size, fsize - pos - HEADER_LEN)

        if available < data_size:
            warnings.append(
                f"Record at offset {pos} truncated: expected {data_size} "
                f"bytes, only {available} available"
            )

        rec_data = file_data[pos + HEADER_LEN:pos + HEADER_LEN + available]
        records.append(WrpRecord(pos, header, rec_data))
        pos = data_end

    return records, warnings


# --- Decompression ---

def decompress_record(record):
    """
    Decompress a single WRP record.

    Returns decompressed bytes, or None on error.
    Raises ValueError with description on unrecoverable errors.
    """
    data = record.data

    if record.algo == ALGO_RAW:
        # Raw data, no compression or RLE
        return bytes(data)

    elif record.algo == ALGO_Z_COMPRESS:
        # LZW (Unix compress) + RLE
        if len(data) < 1:
            return None
        maxbits_byte = data[0]
        if maxbits_byte != 12:
            raise ValueError(
                f"Unexpected LZW maxbits byte: 0x{maxbits_byte:02X} "
                f"(expected 0x0C)"
            )
        lzw_result = decompress_lzw(data[1:], maxbits=12, block_compress=True)
        return rle_decode(lzw_result)

    elif record.algo == ALGO_ARC_SQUEEZE:
        # ARC Squeeze (Huffman) + RLE
        huff_result = decompress_squeeze(data)
        if huff_result is None:
            return None
        return rle_decode(huff_result)

    elif record.algo == ALGO_RLE:
        # RLE only
        return rle_decode(data)

    else:
        raise ValueError(f"Unknown compression algorithm: {record.algo}")


# --- Main extraction logic ---

def extract_wrp(input_path, output_dir):
    """
    Extract a WRP file to output directory.

    Produces:
      - <basename>.adf: the reconstructed Amiga disk image (901120 bytes)
      - <basename>_extra_N.bin: any non-track data blocks (if present)
    """
    input_path = Path(input_path)
    output_dir = Path(output_dir)

    if not input_path.is_file():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        return False

    file_data = input_path.read_bytes()

    if len(file_data) < HEADER_LEN:
        print(f"Error: file too small ({len(file_data)} bytes)", file=sys.stderr)
        return False

    if file_data[:MAGIC_LEN] != MAGIC:
        # Some files start with a FFFF record; check if it still has valid magic
        if file_data[:MAGIC_LEN] != MAGIC:
            print("Error: not a Warp v1.1 disk image", file=sys.stderr)
            return False

    # Parse all records
    records, warnings = parse_records(file_data)

    if not records:
        print("Error: no valid records found", file=sys.stderr)
        return False

    for w in warnings:
        print(f"Warning: {w}", file=sys.stderr)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    basename = input_path.stem

    # Initialize blank ADF image
    adf = bytearray(ADF_SIZE)
    has_track_data = False
    extra_blocks = []
    crc_errors = 0
    decompress_errors = 0

    for rec in records:
        # Decompress the record
        try:
            decompressed = decompress_record(rec)
        except ValueError as e:
            print(f"Warning: record at offset {rec.offset} "
                  f"(track={rec.track}, side={rec.side_name}): {e}",
                  file=sys.stderr)
            decompress_errors += 1
            continue

        if decompressed is None:
            print(f"Warning: failed to decompress record at offset "
                  f"{rec.offset} (track={rec.track}, side={rec.side_name}, "
                  f"algo={rec.algo_name})",
                  file=sys.stderr)
            decompress_errors += 1
            continue

        # Verify CRC
        computed_crc = crc16(decompressed)
        if computed_crc != rec.crc:
            print(f"Warning: CRC mismatch at offset {rec.offset} "
                  f"(track={rec.track}, side={rec.side_name}): "
                  f"computed=0x{computed_crc:04X}, "
                  f"expected=0x{rec.crc:04X}",
                  file=sys.stderr)
            crc_errors += 1

        if rec.is_track_data:
            # Place first 5632 bytes into ADF at the correct position
            dst_offset = rec.disk_offset
            chunk = decompressed[:HALF_TRACK_DATA]
            adf[dst_offset:dst_offset + len(chunk)] = chunk
            has_track_data = True
        elif rec.is_extra_data:
            extra_blocks.append(decompressed)

    # Write ADF output
    if has_track_data:
        adf_path = output_dir / f"{basename}.adf"
        adf_path.write_bytes(bytes(adf))
        print(f"Extracted: {adf_path} ({ADF_SIZE} bytes)")
    else:
        print("Warning: no track data found, no ADF written", file=sys.stderr)

    # Write extra data blocks
    for i, block in enumerate(extra_blocks):
        extra_path = output_dir / f"{basename}_extra_{i}.bin"
        extra_path.write_bytes(block)
        print(f"Extracted: {extra_path} ({len(block)} bytes)")

    # Summary
    track_count = sum(1 for r in records if r.is_track_data)
    extra_count = sum(1 for r in records if r.is_extra_data)
    print(f"Done: {len(records)} records "
          f"({track_count} track, {extra_count} extra)")
    if crc_errors:
        print(f"  {crc_errors} CRC error(s)")
    if decompress_errors:
        print(f"  {decompress_errors} decompression error(s)")

    return True


# --- Entry point ---

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>")
        print()
        print("Extract an Amiga Warp Disk Image (.WRP) file.")
        print("Outputs a standard .ADF disk image and any extra data blocks.")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    success = extract_wrp(input_file, output_dir)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

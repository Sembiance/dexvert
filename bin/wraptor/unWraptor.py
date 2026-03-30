#!/usr/bin/env python3
# Vibe coded by Claude
#
# unWraptor.py - Extract files from Wraptor (.wra/.wr3) archives
#
# Wraptor is a compression/archiving utility by Bill Lucier (1995) for
# Commodore 64/128 GEOS, using an LZSS compression variant.
#
# Usage: unWraptor.py <inputFile> <outputDir>

import sys
import os
import struct


class BitReader:
    """Read bits MSB-first from a byte stream."""

    def __init__(self, data, offset=0):
        self.data = data
        self.byte_pos = offset
        self.bit_pos = 7  # MSB first

    def get_bits(self, n):
        result = 0
        for _ in range(n):
            if self.byte_pos >= len(self.data):
                raise EOFError("Unexpected end of compressed data")
            bit = (self.data[self.byte_pos] >> self.bit_pos) & 1
            result = (result << 1) | bit
            self.bit_pos -= 1
            if self.bit_pos < 0:
                self.bit_pos = 7
                self.byte_pos += 1
        return result

    def get_byte_position(self):
        """Current byte position (rounded up if mid-byte)."""
        if self.bit_pos < 7:
            return self.byte_pos + 1
        return self.byte_pos


def decompress_partial(data, offset):
    """Like decompress() but returns partial data on truncation instead of raising."""
    reader = BitReader(data, offset)
    buffer = bytearray()
    read_bitsize = 8

    try:
        while True:
            type_bit = reader.get_bits(1)
            if type_bit == 0:
                byte_val = reader.get_bits(8)
                buffer.append(byte_val)
            else:
                dict_offset = reader.get_bits(read_bitsize)
                if dict_offset == 0:
                    flag = reader.get_bits(1)
                    if flag == 0:
                        break
                    else:
                        read_bitsize += 1
                else:
                    rep_length = reader.get_bits(5)
                    for i in range(rep_length):
                        src_idx = dict_offset - 1 + i
                        if src_idx < len(buffer):
                            buffer.append(buffer[src_idx])
                        else:
                            buffer.append(0)
    except EOFError:
        pass  # Return what we have

    end_pos = reader.get_byte_position()
    return bytes(buffer), end_pos


SIGNATURE = b'\xff\x42\x4c\xff'

TYPE_SEQ = 1
TYPE_PRG = 2
TYPE_USR = 3
TYPE_GEOS = 4

TYPE_NAMES = {TYPE_SEQ: "SEQ", TYPE_PRG: "PRG", TYPE_USR: "USR", TYPE_GEOS: "GEOS"}

GEOS_STRUCTURE_SEQ = 0
GEOS_STRUCTURE_VLIR = 1

GEOS_TYPE_NAMES = {
    0: "Non-GEOS", 1: "BASIC", 2: "Assembler", 3: "Data file",
    4: "System File", 5: "Desk Accessory", 6: "Application",
    7: "Application Data", 8: "Font File", 9: "Printer Driver",
    10: "Input Driver", 11: "Disk Driver", 12: "System Boot File",
    13: "Temporary", 14: "Auto-Execute File",
}


def decompress(data, offset):
    """
    Decompress LZSS data starting at the given offset.

    Algorithm: Wraptor LZSS variant
    - read_bitsize starts at 8 (dictionary offset width)
    - Control bit 0: literal byte (8 bits)
    - Control bit 1: dictionary reference (read_bitsize bits for offset)
      - offset=0, next bit 0: EOF
      - offset=0, next bit 1: increase read_bitsize by 1
      - offset>0: read 5-bit length, copy from buffer[offset-1]

    Returns (decompressed_bytes, end_byte_position).
    """
    reader = BitReader(data, offset)
    buffer = bytearray()
    read_bitsize = 8

    while True:
        type_bit = reader.get_bits(1)

        if type_bit == 0:
            byte_val = reader.get_bits(8)
            buffer.append(byte_val)
        else:
            dict_offset = reader.get_bits(read_bitsize)

            if dict_offset == 0:
                flag = reader.get_bits(1)
                if flag == 0:
                    break  # EOF
                else:
                    read_bitsize += 1
            else:
                rep_length = reader.get_bits(5)
                for i in range(rep_length):
                    src_idx = dict_offset - 1 + i
                    if src_idx < len(buffer):
                        buffer.append(buffer[src_idx])
                    else:
                        buffer.append(0)

    end_pos = reader.get_byte_position()
    return bytes(buffer), end_pos


def find_entries(data):
    """Find all FF 42 4C FF signature offsets in the data."""
    entries = []
    i = 0
    while i <= len(data) - 4:
        if data[i:i + 4] == SIGNATURE:
            entries.append(i)
            i += 4
        else:
            i += 1
    return entries


def parse_entry_header(data, offset):
    """
    Parse the header of a Wraptor entry.

    Returns (name, file_type, compressed_data_offset).
    """
    pos = offset + 4  # Skip signature
    null_pos = data.index(0, pos)
    name = data[pos:null_pos].decode('latin-1')
    pos = null_pos + 1
    file_type = data[pos]
    pos += 1
    return name, file_type, pos


def sanitize_filename(name):
    """Make a filename safe for the local filesystem."""
    safe = name.replace('/', '_').replace('\\', '_').replace(':', '_')
    safe = safe.replace('\x00', '').strip()
    if not safe:
        safe = "unnamed"
    return safe


def make_unique_path(base_dir, filename):
    """Create a unique file path, appending _N if needed."""
    path = os.path.join(base_dir, filename)
    if not os.path.exists(path):
        return path
    base, ext = os.path.splitext(filename)
    n = 2
    while True:
        path = os.path.join(base_dir, f"{base}_{n}{ext}")
        if not os.path.exists(path):
            return path
        n += 1


def build_geos_dir_entry(name, header_bytes, info_block, is_vlir):
    """
    Build a 30-byte GEOS directory entry from Wraptor metadata.

    Layout (same as bytes $02-$1F of a C64 directory entry):
      $00:     C64 file type (from info block byte $42)
      $01-$02: Track/sector of first data sector (placeholder 01/01)
      $03-$12: Filename padded with $A0 (16 bytes)
      $13-$14: Track/sector of info block (placeholder 01/02)
      $15:     GEOS file structure
      $16:     GEOS file type
      $17:     Year
      $18:     Month
      $19:     Day
      $1A:     Hour
      $1B:     Minute
      $1C-$1D: File size in sectors (lo/hi)
    """
    entry = bytearray(30)

    # C64 file type from info block (byte $44, offset $42 in our data)
    if len(info_block) > 0x42:
        entry[0] = info_block[0x42]
    else:
        entry[0] = 0x83  # USR with lock bit

    # Placeholder T/S for first data
    entry[1] = 0x01
    entry[2] = 0x01

    # Filename (16 bytes, padded with $A0)
    name_bytes = name.encode('latin-1', errors='replace')[:16]
    for i in range(16):
        if i < len(name_bytes):
            entry[3 + i] = name_bytes[i]
        else:
            entry[3 + i] = 0xA0

    # Placeholder T/S for info block
    entry[19] = 0x01
    entry[20] = 0x02

    # GEOS metadata from header
    entry[21] = header_bytes[0]  # structure
    entry[22] = header_bytes[1]  # GEOS type
    entry[23] = header_bytes[2]  # year
    entry[24] = header_bytes[3]  # month
    entry[25] = header_bytes[4]  # day
    entry[26] = header_bytes[5]  # hour
    entry[27] = header_bytes[6]  # minute
    entry[28] = header_bytes[7]  # size lo
    entry[29] = header_bytes[8]  # size hi

    return bytes(entry)


def extract_geos_file(name, decompressed, output_dir, verbose=True):
    """
    Extract a GEOS file from decompressed data.

    Output format: CVT (Convert 2.5) compatible.
    For Sequential GEOS: dir_entry + info_block + file_data
    For VLIR GEOS: dir_entry + info_block + record_table + record_data
    """
    if len(decompressed) < 9:
        if verbose:
            print(f"  WARNING: GEOS data too short ({len(decompressed)} bytes)")
        return None

    # Parse 9-byte header
    header = decompressed[:9]
    structure = header[0]
    geos_type = header[1]

    # Info block (254 bytes, without T/S link)
    info_start = 9
    info_end = info_start + 254
    if info_end > len(decompressed):
        info_block = decompressed[info_start:] + bytes(info_end - len(decompressed))
    else:
        info_block = decompressed[info_start:info_end]

    # Build directory entry
    dir_entry = build_geos_dir_entry(name, header, info_block,
                                     structure == GEOS_STRUCTURE_VLIR)

    # Build CVT file
    cvt_data = bytearray()

    # Directory entry (30 bytes)
    cvt_data.extend(dir_entry)

    # Info block (254 bytes)
    cvt_data.extend(info_block)

    if structure == GEOS_STRUCTURE_VLIR:
        # VLIR: record table (254 bytes) + record data
        rec_start = info_end
        rec_end = rec_start + 254
        if rec_end > len(decompressed):
            rec_table = decompressed[rec_start:] + bytes(rec_end - len(decompressed))
        else:
            rec_table = decompressed[rec_start:rec_end]

        cvt_data.extend(rec_table)

        # Record data (everything after the record table)
        data_start = rec_end
        if data_start < len(decompressed):
            cvt_data.extend(decompressed[data_start:])
    else:
        # Sequential: file data follows info block directly
        data_start = info_end
        if data_start < len(decompressed):
            cvt_data.extend(decompressed[data_start:])

    # Determine extension and write
    safe_name = sanitize_filename(name)
    ext = ".cvt"
    out_path = make_unique_path(output_dir, safe_name + ext)
    with open(out_path, 'wb') as f:
        f.write(cvt_data)

    struct_name = "VLIR" if structure == GEOS_STRUCTURE_VLIR else "Sequential"
    gtype_name = GEOS_TYPE_NAMES.get(geos_type, f"0x{geos_type:02X}")
    date_str = f"{1900 + header[2]}/{header[3]:02d}/{header[4]:02d}"

    if verbose:
        print(f"  -> {os.path.basename(out_path)} "
              f"(GEOS {struct_name} {gtype_name}, {date_str}, "
              f"{len(cvt_data)} bytes)")

    return out_path


def extract_standard_file(name, file_type, decompressed, output_dir, verbose=True):
    """Extract a non-GEOS file (PRG, SEQ, USR)."""
    safe_name = sanitize_filename(name)

    # Check if USR file contains GEOS data
    if file_type == TYPE_USR and len(decompressed) >= 9:
        geos_structure = decompressed[0]
        geos_type_val = decompressed[1]
        # Check for GEOS signature: info block ID bytes at offset 9
        has_info = (len(decompressed) > 11 and
                    decompressed[9] == 0x03 and
                    decompressed[10] == 0x15)

        if geos_type_val != 0 and has_info:
            # This is a GEOS file stored as USR type
            return extract_geos_file(name, decompressed, output_dir, verbose)

        # Non-GEOS USR with GEOS-style header (9 bytes of metadata)
        if (geos_structure in (0, 1) and geos_type_val == 0 and
                all(decompressed[i] < 100 for i in range(2, 7))):
            # Has 9-byte header with non-GEOS type: extract raw data after header
            file_data = decompressed[9:]
            ext = ".usr"
            out_path = make_unique_path(output_dir, safe_name + ext)
            with open(out_path, 'wb') as f:
                f.write(file_data)
            if verbose:
                print(f"  -> {os.path.basename(out_path)} "
                      f"(USR non-GEOS, {len(file_data)} bytes)")
            return out_path

    # Standard extraction
    ext_map = {TYPE_SEQ: ".seq", TYPE_PRG: ".prg", TYPE_USR: ".usr"}
    ext = ext_map.get(file_type, ".bin")

    out_path = make_unique_path(output_dir, safe_name + ext)
    with open(out_path, 'wb') as f:
        f.write(decompressed)

    type_name = TYPE_NAMES.get(file_type, f"type={file_type}")
    extra = ""
    if file_type == TYPE_PRG and len(decompressed) >= 2:
        load_addr = decompressed[0] | (decompressed[1] << 8)
        extra = f", load=${load_addr:04X}"

    if verbose:
        print(f"  -> {os.path.basename(out_path)} ({type_name}{extra}, "
              f"{len(decompressed)} bytes)")

    return out_path


def extract_wraptor(input_file, output_dir, verbose=True):
    """Extract all files from a Wraptor archive."""
    with open(input_file, 'rb') as f:
        data = f.read()

    if len(data) < 4:
        print(f"Error: File too small ({len(data)} bytes)")
        return []

    # Find all entry signatures
    entries = find_entries(data)
    if not entries:
        print("Error: No Wraptor signatures found")
        return []

    os.makedirs(output_dir, exist_ok=True)

    if verbose:
        print(f"Archive: {input_file} ({len(data)} bytes)")
        print(f"Found {len(entries)} file(s)")
        print()

    extracted = []

    for idx, offset in enumerate(entries):
        next_offset = entries[idx + 1] if idx + 1 < len(entries) else len(data)

        try:
            name, file_type, comp_start = parse_entry_header(data, offset)
        except (ValueError, IndexError) as e:
            if verbose:
                print(f"  Entry {idx}: Error parsing header at 0x{offset:04X}: {e}")
            continue

        if verbose:
            type_name = TYPE_NAMES.get(file_type, f"type={file_type}")
            print(f"  [{idx + 1}/{len(entries)}] \"{name}\" ({type_name})")

        # Decompress
        try:
            decompressed, end_pos = decompress(data, comp_start)
        except EOFError:
            # Truncated data - try to salvage partial decompression
            try:
                decompressed, end_pos = decompress_partial(data, comp_start)
                if verbose:
                    print(f"    WARNING: Truncated compressed data, "
                          f"salvaged {len(decompressed)} bytes")
            except Exception:
                if verbose:
                    print(f"    ERROR: Cannot decompress (truncated data)")
                continue
        except (IndexError, Exception) as e:
            if verbose:
                print(f"    ERROR decompressing: {e}")
            continue

        # Verify CRC position (2 bytes after compressed stream)
        crc_end = end_pos + 2
        if crc_end > next_offset + 2:
            if verbose:
                print(f"    WARNING: CRC extends beyond entry boundary")

        # Extract based on type
        try:
            if file_type == TYPE_GEOS:
                path = extract_geos_file(name, decompressed, output_dir, verbose)
            else:
                path = extract_standard_file(name, file_type, decompressed,
                                             output_dir, verbose)
            if path:
                extracted.append(path)
        except Exception as e:
            if verbose:
                print(f"    ERROR extracting: {e}")

    if verbose:
        print()
        print(f"Extracted {len(extracted)} file(s) to {output_dir}")

    return extracted


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>")
        print()
        print("Extract files from a Wraptor (.wra/.wr3) archive.")
        print("  PRG/SEQ/USR files are extracted as raw C64 files.")
        print("  GEOS files are extracted in CVT (Convert 2.5) format.")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(input_file):
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)

    extract_wraptor(input_file, output_dir)


if __name__ == '__main__':
    main()

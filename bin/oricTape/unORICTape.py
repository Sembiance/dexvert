#!/usr/bin/env python3
# Vibe coded by Claude

"""
unORICTape.py - Extract individual files from ORIC tape (.tap/.dat) container images.

Usage: python3 unORICTape.py <inputFile> <outputDir>

Each file entry in the tape image is extracted as a standalone .tap file containing
its sync sequence, header, filename, and data. Gap/junk bytes (if any) are extracted
as .bin files. The sum of all extracted file sizes equals the input file size exactly.
"""

import sys
import os


def parse_tape(data):
    """
    Parse an ORIC tape image sequentially, returning a list of entries.

    Each entry is a dict with at minimum:
        kind:  'file' or 'gap'
        start: byte offset in input (inclusive)
        end:   byte offset in input (exclusive)

    File entries additionally contain header info, name, type, etc.
    Every byte in the input is covered by exactly one entry.
    """
    entries = []
    pos = 0

    while pos < len(data):
        # If current byte is not a sync byte, accumulate gap bytes
        if data[pos] != 0x16:
            gap_start = pos
            while pos < len(data) and data[pos] != 0x16:
                pos += 1
            entries.append({'kind': 'gap', 'start': gap_start, 'end': pos})
            continue

        # Found sync byte(s) - potential file entry start
        entry_start = pos

        # Count consecutive 0x16 sync bytes
        while pos < len(data) and data[pos] == 0x16:
            pos += 1
        sync_count = pos - entry_start

        # Must be followed by 0x24 end-of-sync marker
        if pos >= len(data) or data[pos] != 0x24:
            entries.append({'kind': 'gap', 'start': entry_start, 'end': pos})
            continue
        pos += 1  # consume 0x24

        # Must have 9-byte header
        if pos + 9 > len(data):
            entries.append({'kind': 'gap', 'start': entry_start, 'end': len(data)})
            pos = len(data)
            continue
        header = list(data[pos:pos + 9])
        pos += 9

        # Read null-terminated filename (max 15 chars + null = 16 bytes for field)
        name_bytes = bytearray()
        name_valid = True
        name_field_len = 0
        while True:
            if pos >= len(data):
                name_valid = False
                break
            b = data[pos]
            pos += 1
            name_field_len += 1
            if b == 0x00:
                break
            if name_field_len > 16:
                name_valid = False
                break
            name_bytes.append(b)

        if not name_valid:
            # Invalid name - treat entire entry so far as gap
            entries.append({'kind': 'gap', 'start': entry_start, 'end': pos})
            continue

        name = name_bytes.decode('ascii', errors='replace')

        # Determine file type and data size from header
        type_byte = header[2]
        auto_byte = header[3]

        data_start = pos

        if type_byte in (0x00, 0x80):
            # BASIC (0x00) or Machine code / memory block (0x80)
            file_type = 'BASIC' if type_byte == 0x00 else 'MEM'
            end_addr = header[4] * 256 + header[5]
            start_addr = header[6] * 256 + header[7]
            expected_size = end_addr - start_addr + 1
            if expected_size < 0:
                expected_size = 0

            actual_size = min(expected_size, len(data) - pos)
            pos += actual_size

            entries.append({
                'kind': 'file',
                'start': entry_start,
                'end': pos,
                'file_type': file_type,
                'sync_count': sync_count,
                'header': header,
                'name': name,
                'auto_byte': auto_byte,
                'start_addr': start_addr,
                'end_addr': end_addr,
                'data_size': actual_size,
                'expected_size': expected_size,
                'truncated': actual_size < expected_size,
            })

        elif type_byte == 0x40:
            # Array types - subtype from reserved bytes
            if header[1] == 0xFF:
                file_type = 'STRING_ARRAY'
                elem_size = 3
            elif header[1] == 0x00 and header[0] == 0x80:
                file_type = 'INT_ARRAY'
                elem_size = 2
            elif header[1] == 0x00 and header[0] == 0x00:
                file_type = 'REAL_ARRAY'
                elem_size = 5
            else:
                file_type = 'UNKNOWN_ARRAY'
                elem_size = 1

            size_of_array = header[6] * 256 + header[7]
            num_elements = (size_of_array - 6) // elem_size if size_of_array >= 6 else 0
            descriptor_size = num_elements * elem_size

            if file_type == 'STRING_ARRAY':
                # Descriptors: 3 bytes each [length, addr_lo, addr_hi]
                # Must read descriptors to sum string lengths
                string_data_total = 0
                scan_pos = pos
                for _ in range(num_elements):
                    if scan_pos + 3 <= len(data):
                        string_data_total += data[scan_pos]
                        scan_pos += 3
                expected_size = descriptor_size + string_data_total
            else:
                expected_size = descriptor_size

            start_addr = header[4] * 256 + header[5]
            actual_size = min(expected_size, len(data) - pos)
            pos += actual_size

            entries.append({
                'kind': 'file',
                'start': entry_start,
                'end': pos,
                'file_type': file_type,
                'sync_count': sync_count,
                'header': header,
                'name': name,
                'auto_byte': auto_byte,
                'start_addr': start_addr,
                'end_addr': None,
                'data_size': actual_size,
                'expected_size': expected_size,
                'truncated': actual_size < expected_size,
            })

        else:
            # Unknown type flag - no data to read (can't determine size)
            entries.append({
                'kind': 'file',
                'start': entry_start,
                'end': pos,
                'file_type': f'UNKNOWN(0x{type_byte:02X})',
                'sync_count': sync_count,
                'header': header,
                'name': name,
                'auto_byte': auto_byte,
                'start_addr': None,
                'end_addr': None,
                'data_size': 0,
                'expected_size': 0,
                'truncated': False,
            })

    return entries


def sanitize_filename(name):
    """Replace characters that are unsafe for filesystem use."""
    out = []
    for ch in name:
        if ch in '/\\:*?"<>|\x00':
            out.append('_')
        elif 32 <= ord(ch) < 127:
            out.append(ch)
        else:
            out.append(f'_x{ord(ch):02X}_')
    return ''.join(out).strip() or 'UNNAMED'


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(input_path):
        print(f"Error: File not found: {input_path}")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    with open(input_path, 'rb') as f:
        data = f.read()

    file_size = len(data)
    basename = os.path.splitext(os.path.basename(input_path))[0]

    print(f"Input: {input_path} ({file_size} bytes)")
    print(f"Output: {output_dir}/")
    print()

    entries = parse_tape(data)

    # Verify complete byte coverage with no gaps or overlaps
    total_covered = 0
    prev_end = 0
    for e in entries:
        if e['start'] != prev_end:
            print(f"ERROR: Coverage discontinuity at offset 0x{prev_end:X} "
                  f"(next entry starts at 0x{e['start']:X})")
            sys.exit(1)
        total_covered += e['end'] - e['start']
        prev_end = e['end']

    if total_covered != file_size:
        print(f"ERROR: Covered {total_covered} bytes but file is {file_size} bytes")
        sys.exit(1)

    # Extract each entry
    file_count = 0
    gap_count = 0

    for entry in entries:
        raw = data[entry['start']:entry['end']]
        size = len(raw)

        if entry['kind'] == 'gap':
            gap_count += 1
            out_name = f"{basename}_{entry['start']:06X}_gap.bin"
            out_path = os.path.join(output_dir, out_name)
            with open(out_path, 'wb') as f:
                f.write(raw)
            print(f"  GAP    offset=0x{entry['start']:06X}  size={size:6d}"
                  f"  -> {out_name}")
        else:
            file_count += 1
            safe_name = sanitize_filename(entry['name'])
            out_name = f"{basename}_{entry['start']:06X}_{safe_name}.tap"
            out_path = os.path.join(output_dir, out_name)
            with open(out_path, 'wb') as f:
                f.write(raw)

            hdr = entry['header']
            hdr_hex = ' '.join(f'{b:02X}' for b in hdr)
            ft = entry['file_type']
            auto_str = "auto" if entry['auto_byte'] != 0x00 else "    "
            trunc = " TRUNCATED!" if entry.get('truncated') else ""

            if entry.get('end_addr') is not None:
                addr = f"${entry['start_addr']:04X}-${entry['end_addr']:04X}"
            elif entry.get('start_addr') is not None:
                addr = f"${entry['start_addr']:04X}         "
            else:
                addr = "              "

            print(f"  FILE   offset=0x{entry['start']:06X}  size={size:6d}"
                  f"  {ft:14s} \"{entry['name']}\""
                  f"  sync={entry['sync_count']}"
                  f"  {auto_str}  {addr}"
                  f"  data={entry['data_size']}{trunc}"
                  f"  -> {out_name}")

    print()
    print(f"Done: {file_count} file(s), {gap_count} gap(s), "
          f"{total_covered} of {file_size} bytes extracted.")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# Vibe coded by Claude
#
# qt-flatt.py - QuickTime Movie Flattener
# Native Linux replacement for QT-FLATT.EXE (Pierre Duhem, 1999)
#
# Handles MacBinary II wrapped QuickTime movies:
#   - moov atom in resource fork (classic Mac two-fork style)
#   - moov atom at end of data fork (unoptimized single-fork)
#   - already-flat movies (moov before mdat)
#
# Output: a flat .mov file with moov before mdat and corrected chunk offsets.

import struct
import sys
import os


def read_macbinary(data):
    """Parse MacBinary II header. Returns (data_fork, resource_fork, filename) or None."""
    if len(data) < 128:
        return None

    # MacBinary II validation
    if data[0] != 0:
        return None
    fname_len = data[1]
    if fname_len == 0 or fname_len > 63:
        return None

    # Check for MacBinary II signature at byte 122
    if data[122] != 0x81 or data[123] != 0x81:
        return None

    fname = data[2:2 + fname_len].decode('ascii', errors='replace')
    data_fork_len = struct.unpack('>I', data[83:87])[0]
    rsrc_fork_len = struct.unpack('>I', data[87:91])[0]

    df_start = 128
    df_end = df_start + data_fork_len
    rf_start = df_start + ((data_fork_len + 127) & ~127)
    rf_end = rf_start + rsrc_fork_len

    if df_end > len(data):
        return None

    data_fork = data[df_start:df_end]
    resource_fork = data[rf_start:rf_end] if rf_end <= len(data) else b''

    return data_fork, resource_fork, fname


def parse_atoms(data):
    """Parse top-level QuickTime atoms. Returns list of (offset, size, type, atom_data)."""
    atoms = []
    pos = 0
    while pos + 8 <= len(data):
        size = struct.unpack('>I', data[pos:pos + 4])[0]
        atype = data[pos + 4:pos + 8]

        if size == 0:
            # Atom extends to end of data
            actual_size = len(data) - pos
            atoms.append((pos, actual_size, atype, data[pos:]))
            break
        elif size == 1:
            # 64-bit extended size
            if pos + 16 > len(data):
                break
            ext_size = struct.unpack('>Q', data[pos + 8:pos + 16])[0]
            atoms.append((pos, ext_size, atype, data[pos:pos + ext_size]))
            pos += ext_size
        else:
            if size < 8:
                break
            atoms.append((pos, size, atype, data[pos:pos + size]))
            pos += size

    return atoms


def extract_moov_from_rsrc(rsrc_data):
    """Extract moov atom data from a Mac resource fork."""
    if len(rsrc_data) < 16:
        return None

    rf_data_off, rf_map_off, rf_data_len, rf_map_len = struct.unpack('>IIII', rsrc_data[:16])

    if rf_map_off + 28 > len(rsrc_data):
        return None

    type_list_off = struct.unpack('>H', rsrc_data[rf_map_off + 24:rf_map_off + 26])[0]
    tl_base = rf_map_off + type_list_off

    if tl_base + 2 > len(rsrc_data):
        return None

    num_types = struct.unpack('>h', rsrc_data[tl_base:tl_base + 2])[0] + 1

    for i in range(num_types):
        te_off = tl_base + 2 + i * 8
        if te_off + 8 > len(rsrc_data):
            continue

        rtype = rsrc_data[te_off:te_off + 4]
        ref_off = struct.unpack('>H', rsrc_data[te_off + 6:te_off + 8])[0]

        if rtype == b'moov':
            rref_base = tl_base + ref_off
            if rref_base + 8 > len(rsrc_data):
                continue

            res_data_off_bytes = rsrc_data[rref_base + 5:rref_base + 8]
            res_data_off = struct.unpack('>I', b'\x00' + res_data_off_bytes)[0]
            actual_off = rf_data_off + res_data_off

            if actual_off + 4 > len(rsrc_data):
                continue

            res_len = struct.unpack('>I', rsrc_data[actual_off:actual_off + 4])[0]
            moov_raw = rsrc_data[actual_off + 4:actual_off + 4 + res_len]
            return moov_raw

    return None


def adjust_stco(moov_data, delta):
    """Recursively find stco/co64 atoms in moov and adjust chunk offsets by delta."""
    result = bytearray(moov_data)
    _adjust_stco_recursive(result, 0, len(result), delta)
    return bytes(result)


def _adjust_stco_recursive(data, start, end, delta):
    """Walk atom tree and adjust stco/co64 entries."""
    pos = start
    while pos + 8 <= end:
        size = struct.unpack('>I', data[pos:pos + 4])[0]
        atype = bytes(data[pos + 4:pos + 8])

        if size < 8 or pos + size > end:
            break

        # Container atoms - recurse into them
        if atype in (b'moov', b'trak', b'mdia', b'minf', b'stbl', b'edts',
                     b'dinf', b'udta', b'clip', b'matt', b'kmat', b'load',
                     b'imap', b'tref'):
            _adjust_stco_recursive(data, pos + 8, pos + size, delta)

        elif atype == b'stco':
            # 32-bit chunk offset table
            num_entries = struct.unpack('>I', data[pos + 12:pos + 16])[0]
            for i in range(num_entries):
                off = pos + 16 + i * 4
                if off + 4 > end:
                    break
                old_val = struct.unpack('>I', data[off:off + 4])[0]
                new_val = old_val + delta
                struct.pack_into('>I', data, off, new_val)

        elif atype == b'co64':
            # 64-bit chunk offset table
            num_entries = struct.unpack('>I', data[pos + 12:pos + 16])[0]
            for i in range(num_entries):
                off = pos + 16 + i * 8
                if off + 8 > end:
                    break
                old_val = struct.unpack('>Q', data[off:off + 8])[0]
                new_val = old_val + delta
                struct.pack_into('>Q', data, off, new_val)

        pos += size


def flatten_movie(input_path, output_path):
    """Flatten a QuickTime movie file."""
    with open(input_path, 'rb') as f:
        raw_data = f.read()

    # Try MacBinary first
    mb = read_macbinary(raw_data)
    if mb is not None:
        data_fork, rsrc_fork, orig_name = mb
        print(f"  MacBinary II file, original name: {orig_name}")
        print(f"  Data fork: {len(data_fork)} bytes, Resource fork: {len(rsrc_fork)} bytes")
    else:
        # Treat as raw QuickTime file
        data_fork = raw_data
        rsrc_fork = b''
        print(f"  Raw QuickTime file: {len(data_fork)} bytes")

    # Parse atoms in data fork
    atoms = parse_atoms(data_fork)
    atom_types = {a[2]: a for a in atoms}

    moov_data = None
    mdat_data = None
    moov_source = None

    # Find mdat
    for offset, size, atype, adata in atoms:
        if atype == b'mdat':
            mdat_data = adata
            break

    if mdat_data is None:
        print("  ERROR: No mdat atom found in data fork")
        return False

    # Find moov - check data fork first, then resource fork
    for offset, size, atype, adata in atoms:
        if atype == b'moov':
            moov_data = adata
            moov_source = 'data fork'
            break

    if moov_data is None and len(rsrc_fork) > 0:
        rsrc_moov = extract_moov_from_rsrc(rsrc_fork)
        if rsrc_moov is not None:
            moov_data = rsrc_moov
            moov_source = 'resource fork'

    if moov_data is None:
        print("  ERROR: No moov atom found")
        return False

    print(f"  moov source: {moov_source} ({len(moov_data)} bytes)")
    print(f"  mdat: {len(mdat_data)} bytes")

    # Check if mdat has a proper size header or uses size=0
    mdat_orig_size = struct.unpack('>I', mdat_data[:4])[0]
    if mdat_orig_size == 0:
        # Rewrite mdat header with actual size
        mdat_data = struct.pack('>I', len(mdat_data)) + mdat_data[4:]
        print(f"  Fixed mdat size=0 -> {len(mdat_data)}")

    # Build free atom for padding (optional, for alignment)
    # Collect any other top-level atoms that aren't moov/mdat (like free, wide, skip)
    other_atoms = b''
    for offset, size, atype, adata in atoms:
        if atype not in (b'moov', b'mdat', b'free', b'skip', b'wide'):
            other_atoms += adata

    # Calculate the offset adjustment for stco/co64
    # In the original file, stco offsets are relative to the beginning of the data fork.
    # In the flat output, the layout will be: moov + mdat
    # So chunk offsets need to shift by: (size_of_moov) - (original_mdat_offset_in_data_fork)

    # Find original mdat offset in data fork
    orig_mdat_offset = 0
    for offset, size, atype, adata in atoms:
        if atype == b'mdat':
            orig_mdat_offset = offset
            break

    # In the output file: mdat starts after moov (and any other atoms)
    new_mdat_offset = len(moov_data) + len(other_atoms)
    delta = new_mdat_offset - orig_mdat_offset

    print(f"  Original mdat offset in data fork: {orig_mdat_offset}")
    print(f"  New mdat offset in output: {new_mdat_offset}")
    print(f"  stco adjustment delta: {delta:+d}")

    # Adjust chunk offsets in moov
    adjusted_moov = adjust_stco(moov_data, delta)

    # Write the flattened file
    with open(output_path, 'wb') as f:
        f.write(adjusted_moov)
        if other_atoms:
            f.write(other_atoms)
        f.write(mdat_data)

    output_size = len(adjusted_moov) + len(other_atoms) + len(mdat_data)
    print(f"  Output: {output_path} ({output_size} bytes)")
    return True


def main():
    if len(sys.argv) < 2:
        print("QT-Flattener - Converter for Macintosh QuickTime files")
        print("Native Linux replacement for QT-FLATT.EXE")
        print()
        print(f"Usage: {sys.argv[0]} <input_file> [output_file]")
        print()
        print("The input file can be:")
        print("  - A MacBinary II wrapped QuickTime movie")
        print("  - A raw (unoptimized) QuickTime .mov file")
        print()
        print("If no output file is specified, writes to <input_basename>.mov")
        sys.exit(1)

    input_path = sys.argv[1]
    if not os.path.isfile(input_path):
        print(f"Error: file not found: {input_path}")
        sys.exit(1)

    if len(sys.argv) >= 3:
        output_path = sys.argv[2]
    else:
        base = os.path.splitext(os.path.basename(input_path))[0]
        output_dir = os.path.dirname(input_path) or '.'
        output_path = os.path.join(output_dir, base + '.mov')
        # Avoid overwriting input
        if os.path.abspath(output_path) == os.path.abspath(input_path):
            output_path = os.path.join(output_dir, base + '_flat.mov')

    print(f"Handling file {input_path}.")
    if not flatten_movie(input_path, output_path):
        sys.exit(1)
    print("Done.")


if __name__ == '__main__':
    main()

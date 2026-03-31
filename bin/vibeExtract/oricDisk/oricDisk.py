#!/usr/bin/env python3
# Vibe coded by Claude

"""
unORICDisk.py - Extract files from ORIC DSK disk images.

Supports ORICDISK (plain) and MFM_DISK (MFM-encoded) container formats,
and Sedoric, OricDOS, and FTDOS filesystems.

Usage: python3 unORICDisk.py <inputFile> <outputDir>
"""

import os
import struct
import sys


def parse_mfm_track(track_data):
    """Parse an MFM-encoded track and extract sectors.

    Returns a list of (track_id, side, sector_num, sector_data) tuples.
    """
    sectors = []
    i = 0
    length = len(track_data)
    while i < length - 10:
        # Look for address mark: A1 A1 A1 FE
        if (track_data[i] == 0xA1 and track_data[i + 1] == 0xA1
                and track_data[i + 2] == 0xA1 and track_data[i + 3] == 0xFE):
            if i + 7 >= length:
                break
            track_id = track_data[i + 4]
            side = track_data[i + 5]
            sector_num = track_data[i + 6]
            size_code = track_data[i + 7]
            sector_size = 128 << size_code
            # Find data mark: A1 A1 A1 FB
            j = i + 10  # skip past address field + CRC
            while j < length - 4:
                if (track_data[j] == 0xA1 and track_data[j + 1] == 0xA1
                        and track_data[j + 2] == 0xA1 and track_data[j + 3] == 0xFB):
                    data_start = j + 4
                    data_end = data_start + sector_size
                    if data_end <= length:
                        sector_data = bytes(track_data[data_start:data_end])
                    else:
                        sector_data = bytes(track_data[data_start:]) + b'\x00' * (data_end - length)
                    sectors.append((track_id, side, sector_num, sector_data))
                    i = data_end + 2  # skip past CRC
                    break
                j += 1
            else:
                i += 1
                continue
            continue
        i += 1
    return sectors


def load_disk(filename):
    """Load a DSK file and return a disk sector map.

    Returns:
        disk: dict mapping (encoded_track, sector_num) -> sector_data (bytes)
        sig: signature string (b"ORICDISK" or b"MFM_DISK")
        sides: number of sides
        tracks_per_side: tracks per side
        sectors_per_track: sectors per track (ORICDISK only, 0 for MFM)
    """
    with open(filename, 'rb') as f:
        data = f.read()

    if len(data) < 256:
        print(f"Error: File too small ({len(data)} bytes)", file=sys.stderr)
        sys.exit(1)

    sig = data[0:8]
    sides = struct.unpack_from('<I', data, 8)[0]
    tracks_per_side = struct.unpack_from('<I', data, 12)[0]
    field3 = struct.unpack_from('<I', data, 16)[0]

    if sig not in (b'ORICDISK', b'MFM_DISK'):
        print(f"Error: Unknown signature: {sig!r}", file=sys.stderr)
        sys.exit(1)

    disk = {}

    if sig == b'ORICDISK':
        spt = field3
        offset = 256
        total_tracks = sides * tracks_per_side
        for raw_idx in range(total_tracks):
            if raw_idx < tracks_per_side:
                encoded_track = raw_idx
            else:
                encoded_track = 0x80 | (raw_idx - tracks_per_side)
            for s in range(spt):
                end = offset + 256
                if end > len(data):
                    break
                disk[(encoded_track, s + 1)] = data[offset:end]
                offset += 256
        return disk, sig, sides, tracks_per_side, spt

    else:  # MFM_DISK
        total_tracks = sides * tracks_per_side
        if total_tracks == 0:
            return disk, sig, sides, tracks_per_side, 0
        bpt = (len(data) - 256) // total_tracks
        if bpt == 0:
            return disk, sig, sides, tracks_per_side, 0

        for raw_idx in range(total_tracks):
            offset = 256 + raw_idx * bpt
            raw_track = data[offset:offset + bpt]
            sectors = parse_mfm_track(raw_track)

            if raw_idx < tracks_per_side:
                encoded_track = raw_idx
            else:
                encoded_track = 0x80 | (raw_idx - tracks_per_side)

            for (track_id, side, sector_num, sector_data) in sectors:
                disk[(encoded_track, sector_num)] = sector_data

        return disk, sig, sides, tracks_per_side, 0


def get_sector(disk, track, sector):
    """Get a sector's data from the disk. Returns bytes or empty bytes."""
    return disk.get((track, sector), b'')


def decode_sedoric_track(track_ref, tracks_per_side):
    """Decode a Sedoric/OricDOS track reference to encoded track key."""
    # Track refs 0-0x7F are side 0, 0x80-0xFF are side 1
    # Our disk keys already use this encoding
    return track_ref


def decode_ftdos_track(track_ref, tracks_per_side):
    """Decode a FTDOS contiguous track reference to encoded track key."""
    if track_ref < tracks_per_side:
        return track_ref
    else:
        return 0x80 | (track_ref - tracks_per_side)


def detect_filesystem(disk, tracks_per_side):
    """Detect the filesystem type on the disk.

    Returns: 'SEDORIC', 'ORICDOS', 'FTDOS', or 'UNKNOWN'
    """
    # Standard probe locations
    probes = [
        (0, 1, 0x40, 8),
        (4, 17, 0x40, 8),
        (2, 11, 0xC8, 8),
        (0, 2, 0x22, 8),
    ]
    for (track, sector, offset, size) in probes:
        d = get_sector(disk, track, sector)
        if len(d) > offset + size:
            probe_str = d[offset:offset + size]
            if b'SEDORIC' in probe_str:
                return 'SEDORIC'
            if b'Oric DOS' in probe_str:
                return 'ORICDOS'

    # Check for Sedoric bitmap signature at T20 S2
    bm = get_sector(disk, 20, 2)
    if len(bm) >= 16 and bm[0] == 0xFF and bm[1] == 0x00:
        # Verify it looks like a bitmap (track count and sectors/track fields)
        track_count = bm[6]
        spt = bm[7]
        if 0 < track_count <= 128 and 0 < spt <= 19:
            return 'SEDORIC'

    # Check for FTDOS directory at T20 S2
    dir_sec = get_sector(disk, 20, 2)
    if len(dir_sec) >= 24:
        flag = dir_sec[6]
        if flag in (0x55, 0x4C):
            # Check for dot separator at offset 15 (flag + 8-byte name + dot)
            if dir_sec[15] == 0x2E:
                return 'FTDOS'

    return 'UNKNOWN'


def sanitize_filename(name):
    """Sanitize a filename for the host filesystem."""
    # Replace/remove invalid characters
    invalid = '<>:"/\\|?*'
    result = []
    for ch in name:
        if ch in invalid or ord(ch) < 32:
            result.append('_')
        else:
            result.append(ch)
    s = ''.join(result).strip()
    if not s:
        s = 'UNNAMED'
    return s


def extract_sedoric(disk, tracks_per_side, output_dir):
    """Extract files from a Sedoric filesystem."""

    # Read system sector (T20 S1)
    sys_sec = get_sector(disk, 20, 1)
    if sys_sec:
        has_colors = len(sys_sec) > 0x09 and sys_sec[0x09] == 0x1B
        if has_colors:
            disk_name = sys_sec[0x0D:0x1E].decode('ascii', errors='replace').rstrip()
        else:
            disk_name = sys_sec[0x09:0x1E].decode('ascii', errors='replace').rstrip()
        # Clean non-printable chars
        disk_name = ''.join(c if 32 <= ord(c) < 127 else '' for c in disk_name).strip()
        if disk_name:
            print(f"  Disk name: {disk_name}")

    # Read bitmap (T20 S2)
    bm = get_sector(disk, 20, 2)
    if bm and len(bm) >= 16:
        free_secs = struct.unpack_from('<H', bm, 2)[0]
        file_count = struct.unpack_from('<H', bm, 4)[0]
        print(f"  Free sectors: {free_secs}, Files: {file_count}")

    # Read directory chain starting at T20 S4
    dir_track, dir_sector = 20, 4
    files_extracted = 0

    while True:
        d = get_sector(disk, dir_track, dir_sector)
        if not d or len(d) < 16:
            break

        next_track = d[0]
        next_sector = d[1]

        # Parse entries starting at offset 0x10
        pos = 0x10
        while pos + 16 <= 256:
            entry = d[pos:pos + 16]
            if entry[0] == 0x00:
                # End of entries in this sector
                break

            name_bytes = entry[0:9]
            ext_bytes = entry[9:12]
            desc_track = entry[12]
            desc_sector = entry[13]
            # entry[14] = total sectors (data + descriptor)
            # entry[15] = flags

            name = name_bytes.decode('ascii', errors='replace').rstrip()
            ext = ext_bytes.decode('ascii', errors='replace').rstrip()

            if ext:
                full_name = f"{name}.{ext}"
            else:
                full_name = name

            # Read descriptor
            file_data = read_sedoric_file(disk, desc_track, desc_sector, tracks_per_side)
            if file_data is not None:
                safe_name = sanitize_filename(full_name)
                out_path = os.path.join(output_dir, safe_name)
                # Handle duplicate names
                counter = 1
                base_name = safe_name
                while os.path.exists(out_path):
                    name_part, _, ext_part = base_name.rpartition('.')
                    if name_part:
                        safe_name = f"{name_part}_{counter}.{ext_part}"
                    else:
                        safe_name = f"{base_name}_{counter}"
                    out_path = os.path.join(output_dir, safe_name)
                    counter += 1

                with open(out_path, 'wb') as f:
                    f.write(file_data)
                print(f"    {full_name} ({len(file_data)} bytes)")
                files_extracted += 1

            pos += 16

        if next_track == 0:
            break
        dir_track = next_track
        dir_sector = next_sector

    return files_extracted


def read_sedoric_file(disk, desc_track, desc_sector, tracks_per_side):
    """Read file data from Sedoric descriptor chain."""
    desc = get_sector(disk, desc_track, desc_sector)
    if not desc or len(desc) < 12:
        return None

    sig = desc[2]
    if sig != 0xFF:
        return None

    flags = desc[3]
    start_addr = struct.unpack_from('<H', desc, 4)[0]
    end_addr = struct.unpack_from('<H', desc, 6)[0]
    # exec_addr = struct.unpack_from('<H', desc, 8)[0]
    data_sectors = struct.unpack_from('<H', desc, 10)[0]

    # Calculate expected file size
    if end_addr > start_addr:
        file_size = end_addr - start_addr
    else:
        file_size = data_sectors * 256

    # Collect sector references from descriptor chain
    sector_refs = []
    current_desc = desc
    current_desc_track = desc_track
    current_desc_sector = desc_sector
    first_desc = True

    while True:
        if first_desc:
            pair_start = 12  # First descriptor: pairs start at offset 0x0C
            first_desc = False
        else:
            pair_start = 2  # Continuation: pairs start at offset 0x02

        i = pair_start
        while i + 1 < 256 and len(sector_refs) < data_sectors:
            ref_track = current_desc[i]
            ref_sector = current_desc[i + 1]
            if ref_track == 0 and ref_sector == 0:
                break
            sector_refs.append((ref_track, ref_sector))
            i += 2

        if len(sector_refs) >= data_sectors:
            break

        next_t = current_desc[0]
        next_s = current_desc[1]
        if next_t == 0:
            break

        current_desc = get_sector(disk, next_t, next_s)
        if not current_desc or len(current_desc) < 4:
            break
        current_desc_track = next_t
        current_desc_sector = next_s

    # Read all data sectors
    raw_data = bytearray()
    for (ref_track, ref_sector) in sector_refs:
        # Track reference uses Sedoric encoding (0x80 for side 1)
        sector_data = get_sector(disk, ref_track, ref_sector)
        if sector_data:
            raw_data.extend(sector_data)
        else:
            raw_data.extend(b'\x00' * 256)

    # Trim to actual file size
    if file_size > 0 and file_size <= len(raw_data):
        return bytes(raw_data[:file_size])
    return bytes(raw_data)


def extract_oricdos(disk, tracks_per_side, output_dir):
    """Extract files from an OricDOS filesystem."""

    # Read system sector (T0 S1)
    sys_sec = get_sector(disk, 0, 1)
    if not sys_sec or len(sys_sec) < 0x2D:
        print("  Error: Cannot read OricDOS system sector", file=sys.stderr)
        return 0

    dir_sector = sys_sec[0x12]
    dir_track = sys_sec[0x13]
    free_secs = struct.unpack_from('<H', sys_sec, 0x14)[0]
    busy_secs = struct.unpack_from('<H', sys_sec, 0x16)[0]
    disk_name = sys_sec[0x18:0x2D].decode('ascii', errors='replace').rstrip()
    disk_name = ''.join(c if 32 <= ord(c) < 127 else '' for c in disk_name).strip()

    if disk_name:
        print(f"  Disk name: {disk_name}")
    print(f"  Free sectors: {free_secs}, Busy: {busy_secs}")

    files_extracted = 0

    while True:
        d = get_sector(disk, dir_track, dir_sector)
        if not d or len(d) < 3:
            break

        next_track = d[0]
        next_sector = d[1]

        # Parse entries starting at offset 3
        pos = 3
        while pos + 16 <= 256:
            entry = d[pos:pos + 16]
            if entry[0] == 0x00:
                break

            name = entry[0:6].decode('ascii', errors='replace').rstrip()
            ext = entry[6:9].decode('ascii', errors='replace').rstrip()
            num_sectors = struct.unpack_from('<H', entry, 9)[0]
            first_sector = entry[0x0B]
            first_track = entry[0x0C]
            # last_sector = entry[0x0D]
            # last_track = entry[0x0E]
            flags = entry[0x0F]

            if ext:
                full_name = f"{name}.{ext}"
            else:
                full_name = name

            # Read file data by following sector chain
            file_data = read_oricdos_file(disk, first_track, first_sector, num_sectors)
            if file_data is not None:
                safe_name = sanitize_filename(full_name)
                out_path = os.path.join(output_dir, safe_name)
                counter = 1
                base_name = safe_name
                while os.path.exists(out_path):
                    name_part, _, ext_part = base_name.rpartition('.')
                    if name_part:
                        safe_name = f"{name_part}_{counter}.{ext_part}"
                    else:
                        safe_name = f"{base_name}_{counter}"
                    out_path = os.path.join(output_dir, safe_name)
                    counter += 1

                with open(out_path, 'wb') as f:
                    f.write(file_data)
                print(f"    {full_name} ({len(file_data)} bytes)")
                files_extracted += 1

            pos += 16

        if next_track == 0 and next_sector == 0:
            break
        dir_track = next_track
        dir_sector = next_sector

    return files_extracted


def read_oricdos_file(disk, start_track, start_sector, max_sectors):
    """Read file data from OricDOS linked sector chain."""
    file_data = bytearray()
    track = start_track
    sector = start_sector
    start_addr = 0
    end_addr = 0
    exec_addr = 0
    sectors_read = 0
    first_sector = True

    while sectors_read < max_sectors + 10:  # safety margin
        sec_data = get_sector(disk, track, sector)
        if not sec_data or len(sec_data) < 3:
            break

        next_track = sec_data[0]
        next_sector = sec_data[1]
        data_count = sec_data[2]

        if first_sector and data_count == 0xFF:
            # Header sector
            if len(sec_data) >= 11:
                start_addr = struct.unpack_from('<H', sec_data, 4)[0]
                end_addr = struct.unpack_from('<H', sec_data, 6)[0]
                exec_addr = struct.unpack_from('<H', sec_data, 8)[0]
                actual_count = sec_data[10]
                data_offset = 11
                file_data.extend(sec_data[data_offset:data_offset + actual_count])
            first_sector = False
        else:
            # Regular data sector
            if data_count > 0 and data_count != 0xFF:
                data_offset = 3
                file_data.extend(sec_data[data_offset:data_offset + data_count])
            elif data_count == 0 and first_sector:
                # No header, raw data
                file_data.extend(sec_data[3:])
            else:
                data_offset = 3
                file_data.extend(sec_data[data_offset:data_offset + data_count])
            first_sector = False

        sectors_read += 1

        if next_track == 0 and next_sector == 0:
            break
        track = next_track
        sector = next_sector

    return bytes(file_data)


def extract_ftdos(disk, tracks_per_side, output_dir):
    """Extract files from an FTDOS filesystem."""

    # Read bitmap/system at T20 S1
    bm = get_sector(disk, 20, 1)
    if bm and len(bm) >= 0x100:
        disk_name = bm[0xF8:0x100].decode('ascii', errors='replace').rstrip()
        disk_name = ''.join(c if 32 <= ord(c) < 127 else '' for c in disk_name).strip()
        if disk_name:
            print(f"  Disk name: {disk_name}")

    # Try directory at T20 S2, then fall back to T7 S2
    dir_locations = [(20, 2), (7, 2), (3, 2)]
    files_extracted = 0

    extracted_names = set()

    for dir_track, dir_sector in dir_locations:
        d = get_sector(disk, dir_track, dir_sector)
        if not d or len(d) < 24:
            continue

        # Check if this looks like an FTDOS directory
        first_flag = d[6]
        if first_flag not in (0x55, 0x4C, 0x00):
            continue

        while True:
            pos = 6
            while pos + 18 <= 256:
                flag = d[pos]
                if flag == 0x00:
                    break
                if flag not in (0x55, 0x4C):
                    pos += 18
                    continue

                name = d[pos + 1:pos + 9].decode('ascii', errors='replace').rstrip()
                dot = d[pos + 9]
                ext = d[pos + 10:pos + 13].decode('ascii', errors='replace').rstrip()
                # type_byte = d[pos + 13]
                sector_count = struct.unpack_from('<H', d, pos + 14)[0]
                first_track_ref = d[pos + 16]
                first_sector_ref = d[pos + 17]

                if dot == 0x2E and ext:
                    full_name = f"{name}.{ext}"
                elif name:
                    full_name = name
                else:
                    pos += 18
                    continue

                # Skip if we already extracted this file from another directory copy
                if full_name in extracted_names:
                    pos += 18
                    continue
                extracted_names.add(full_name)

                # Read file data - FTDOS stores raw sector data contiguously
                file_data = read_ftdos_file(
                    disk, first_track_ref, first_sector_ref,
                    sector_count, tracks_per_side
                )
                if file_data is not None:
                    safe_name = sanitize_filename(full_name)
                    out_path = os.path.join(output_dir, safe_name)
                    counter = 1
                    base_name = safe_name
                    while os.path.exists(out_path):
                        name_part, _, ext_part = base_name.rpartition('.')
                        if name_part:
                            safe_name = f"{name_part}_{counter}.{ext_part}"
                        else:
                            safe_name = f"{base_name}_{counter}"
                        out_path = os.path.join(output_dir, safe_name)
                        counter += 1

                    with open(out_path, 'wb') as f:
                        f.write(file_data)
                    print(f"    {full_name} ({len(file_data)} bytes)")
                    files_extracted += 1

                pos += 18

            # Follow directory chain
            next_track = d[0]
            next_sector = d[1]
            if next_track == 0 and next_sector == 0:
                break
            d = get_sector(disk, next_track, next_sector)
            if not d or len(d) < 24:
                break

    return files_extracted


def read_ftdos_file(disk, first_track_ref, first_sector_ref, sector_count, tracks_per_side):
    """Read file data from FTDOS contiguous sectors."""
    file_data = bytearray()

    # Determine sectors per track by checking the disk
    # Find max sector number in track 0
    spt = 17  # default
    for s in range(1, 20):
        if (0, s) in disk:
            spt = max(spt, s)

    track = first_track_ref
    sector = first_sector_ref

    for _ in range(sector_count):
        encoded_track = decode_ftdos_track(track, tracks_per_side)
        sec_data = get_sector(disk, encoded_track, sector)
        if sec_data:
            file_data.extend(sec_data)
        else:
            file_data.extend(b'\x00' * 256)

        # Advance to next sector sequentially
        sector += 1
        if sector > spt:
            sector = 1
            track += 1

    return bytes(file_data)


def extract_raw_sectors(disk, tracks_per_side, sides, output_dir):
    """Dump all non-empty sectors as raw data for unknown filesystems."""
    raw_dir = os.path.join(output_dir, '_raw_sectors')
    os.makedirs(raw_dir, exist_ok=True)

    sector_count = 0
    for (track, sector_num) in sorted(disk.keys()):
        data = disk[(track, sector_num)]
        if all(b == 0 for b in data):
            continue  # Skip empty sectors
        fname = f"T{track:03d}_S{sector_num:02d}.bin"
        with open(os.path.join(raw_dir, fname), 'wb') as f:
            f.write(data)
        sector_count += 1

    print(f"    Dumped {sector_count} non-empty raw sectors to _raw_sectors/")
    return sector_count


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(input_file):
        print(f"Error: Input file not found: {input_file}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    print(f"Loading: {input_file}")

    disk, sig, sides, tracks_per_side, spt = load_disk(input_file)

    sig_str = sig.decode('ascii', errors='replace')
    print(f"  Format: {sig_str}")
    print(f"  Sides: {sides}, Tracks/side: {tracks_per_side}", end="")
    if spt > 0:
        print(f", Sectors/track: {spt}")
    else:
        print(f", Total sectors loaded: {len(disk)}")

    # Detect filesystem
    fs_type = detect_filesystem(disk, tracks_per_side)
    print(f"  Filesystem: {fs_type}")

    # Extract files
    files_extracted = 0
    if fs_type == 'SEDORIC':
        files_extracted = extract_sedoric(disk, tracks_per_side, output_dir)
    elif fs_type == 'ORICDOS':
        files_extracted = extract_oricdos(disk, tracks_per_side, output_dir)
    elif fs_type == 'FTDOS':
        files_extracted = extract_ftdos(disk, tracks_per_side, output_dir)

    if files_extracted == 0 and fs_type != 'UNKNOWN':
        print("  No files found in filesystem, dumping raw sectors...")
        extract_raw_sectors(disk, tracks_per_side, sides, output_dir)
    elif fs_type == 'UNKNOWN':
        print("  Unknown filesystem, dumping raw sectors...")
        extract_raw_sectors(disk, tracks_per_side, sides, output_dir)
    else:
        print(f"  Extracted {files_extracted} file(s)")


if __name__ == '__main__':
    main()

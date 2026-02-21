# Vibe coded by Claude
"""
unvise.py - Extract files from Installer VISE archives (Mac OS)

Usage: python3 unvise.py <inputFile> <outputDir>

Supports Installer VISE versions 2.x through 3.x (format versions 0x80010201-0x8001030d).
Decompression based on reverse-engineering by the ScummVM project (elasota, 2022).
"""

import sys
import os
import struct
import zlib

# Deobfuscation table for VISE 3.x compression
# Source: ScummVM common/compression/vise.cpp (GPLv3)
DEOBFUSCATION_TABLE = bytes([
    0x6a, 0xb7, 0x36, 0xec, 0x15, 0xd9, 0xc8, 0x73, 0xe8, 0x38, 0x9a, 0xdf, 0x21, 0x25, 0xd0, 0xcc,
    0xfd, 0xdc, 0x16, 0xd7, 0xe3, 0x43, 0x05, 0xc5, 0x8f, 0x48, 0xda, 0xf2, 0x3f, 0x10, 0x23, 0x6c,
    0x77, 0x7c, 0xf9, 0xa0, 0xa3, 0xe9, 0xed, 0x46, 0x8b, 0xd8, 0xac, 0x54, 0xce, 0x2d, 0x19, 0x5e,
    0x6d, 0x7d, 0x87, 0x5d, 0xfa, 0x5b, 0x9b, 0xe0, 0xc7, 0xee, 0x9f, 0x52, 0xa9, 0xb9, 0x0a, 0xd1,
    0xfe, 0x78, 0x76, 0x4a, 0x3d, 0x44, 0x5a, 0x96, 0x90, 0x1f, 0x26, 0x9d, 0x58, 0x1b, 0x8e, 0x57,
    0x59, 0xc3, 0x0b, 0x6b, 0xfc, 0x1d, 0xe6, 0xa2, 0x7f, 0x92, 0x4f, 0x40, 0xb4, 0x06, 0x72, 0x4d,
    0xf4, 0x34, 0xaa, 0xd2, 0x49, 0xad, 0xef, 0x22, 0x1a, 0xb5, 0xba, 0xbf, 0x29, 0x68, 0x89, 0x93,
    0x3e, 0x32, 0x04, 0xf5, 0xde, 0xe1, 0x6f, 0xfb, 0x67, 0xe4, 0x7e, 0x08, 0xaf, 0xf0, 0xab, 0x41,
    0x82, 0xea, 0x50, 0x0f, 0x2a, 0xc6, 0x35, 0xb3, 0xa8, 0xca, 0xe5, 0x4c, 0x45, 0x8a, 0x97, 0xae,
    0xd6, 0x66, 0x27, 0x53, 0xc9, 0x1c, 0x3c, 0x03, 0x99, 0xc1, 0x09, 0x2e, 0x69, 0x37, 0x8d, 0x2f,
    0x60, 0xc2, 0xa6, 0x18, 0x4e, 0x7a, 0xb8, 0xcf, 0xa7, 0x3a, 0x17, 0xd5, 0x9e, 0xf1, 0x84, 0x51,
    0x0d, 0xa4, 0x64, 0xc4, 0x1e, 0xb1, 0x30, 0x98, 0xbb, 0x79, 0x01, 0xf6, 0x62, 0x0e, 0xb2, 0x63,
    0x91, 0xcb, 0xff, 0x80, 0x71, 0xe7, 0xd4, 0x00, 0xdb, 0x75, 0x2c, 0xbd, 0x39, 0x33, 0x94, 0xbc,
    0x8c, 0x3b, 0xb6, 0x20, 0x85, 0x24, 0x88, 0x2b, 0x70, 0x83, 0x6e, 0x7b, 0x9c, 0xbe, 0x14, 0x47,
    0x65, 0x4b, 0x56, 0x81, 0xf8, 0x12, 0x11, 0x28, 0xeb, 0x55, 0x74, 0xa1, 0x31, 0xf7, 0xb0, 0x13,
    0x86, 0xdd, 0x5f, 0x42, 0xd3, 0x02, 0x61, 0x95, 0x0c, 0x5c, 0xa5, 0xcd, 0xc0, 0x07, 0xe2, 0xf3,
])


def deobfuscate(raw):
    """Undo VISE byte-swap + substitution cipher obfuscation."""
    data = bytearray(raw)
    # Step 1: swap adjacent byte pairs
    for i in range(1, len(data), 2):
        data[i], data[i - 1] = data[i - 1], data[i]
    # Step 2: substitution cipher
    for i in range(len(data)):
        data[i] = DEOBFUSCATION_TABLE[data[i]]
    return bytes(data)


def decompress_vise(raw, expected_size):
    """Deobfuscate and decompress a VISE compressed stream."""
    if expected_size == 0:
        return b''
    deobf = deobfuscate(raw)
    dec = zlib.decompressobj(-zlib.MAX_WBITS)
    result = dec.decompress(deobf, expected_size + 4096)
    if len(result) != expected_size:
        raise ValueError(f"Decompressed size {len(result)} != expected {expected_size}")
    return result


def safe_filename(name):
    """Sanitize a Mac filename for use on modern filesystems."""
    # Mac used : as path separator; replace with _
    name = name.replace(':', '_')
    # Replace other problematic characters
    for ch in '/\\<>"|?*':
        name = name.replace(ch, '_')
    # Remove control characters
    name = ''.join(c for c in name if ord(c) >= 32)
    if not name:
        name = '_unnamed_'
    return name


def parse_svct_header(data):
    """Parse the 44-byte SVCT header. Returns (version, cvct_offset, segment)."""
    if len(data) < 44:
        raise ValueError("File too small for SVCT header")
    magic = data[0:4]
    if magic != b'SVCT':
        raise ValueError(f"Not a VISE file (magic: {magic!r})")
    segment = struct.unpack('>I', data[4:8])[0]
    version = struct.unpack('>I', data[16:20])[0]
    cvct_offset = struct.unpack('>I', data[36:40])[0]
    return version, cvct_offset, segment


def scan_catalog_markers(data, cvct_offset):
    """Scan the catalog section for DVCT/FVCT/PACK/INDN markers."""
    catalog_start = cvct_offset + 20  # skip CVCT header
    markers = []
    i = 0
    catalog_data = data[catalog_start:]
    while i < len(catalog_data) - 3:
        tag = catalog_data[i:i + 4]
        if tag in (b'DVCT', b'FVCT', b'PACK', b'INDN'):
            markers.append((catalog_start + i, tag))
            i += 4
        else:
            i += 1
    return markers


def detect_fvct_layout(data, markers, version):
    """Detect the FVCT entry layout for the given version.

    Returns (file_data_size, name_len_offset, position_offset) where offsets
    are relative to the start of the file data block (after the 4-byte magic).
    """
    # ScummVM known layouts
    ver_minor = version & 0xFFFF
    if ver_minor <= 0x0301:
        return 120, 118, 96

    # For later versions, try to auto-detect by finding position_in_archive
    cvct_offset = struct.unpack('>I', data[36:40])[0]

    for i, (offset, tag) in enumerate(markers):
        if tag != b'FVCT':
            continue
        # Find the next marker to determine entry size
        next_offset = markers[i + 1][0] if i + 1 < len(markers) else len(data)
        entry_size = next_offset - offset
        entry = data[offset:next_offset]
        fd = entry[4:]  # skip magic

        # Read comp/uncomp sizes from known positions (consistent across versions)
        if len(fd) < 80:
            continue
        comp_data = struct.unpack('>I', fd[64:68])[0]
        uncomp_data = struct.unpack('>I', fd[68:72])[0]

        # Skip entries with no data (they may be placeholders)
        if comp_data == 0 and uncomp_data == 0:
            continue

        # Search for position_in_archive value in the entry
        # It should be a value >= 44 and < cvct_offset
        for pos_off in range(80, min(len(fd) - 4, 140)):
            val = struct.unpack('>I', fd[pos_off:pos_off + 4])[0]
            if 44 <= val < cvct_offset:
                # Verify: does data at this position look like compressed data?
                if val + comp_data <= len(data):
                    # Found a plausible position_in_archive
                    # Now find name_len: scan backwards from end for the name
                    for nl_off in range(pos_off + 4, min(len(fd) - 1, pos_off + 40)):
                        nl = fd[nl_off]
                        if 0 < nl < 64:
                            name_start = nl_off + 1
                            # Check if there might be extra bytes before the name
                            # (name could be at end of entry)
                            for name_actual_start in range(name_start, min(name_start + 60, len(fd) - nl)):
                                name_bytes = fd[name_actual_start:name_actual_start + nl]
                                try:
                                    name = name_bytes.decode('mac_roman')
                                    # Valid name: mostly printable, no nulls in middle
                                    if (sum(1 for c in name if c.isprintable()) > len(name) * 0.7
                                            and '\x00' not in name):
                                        # Verify with decompression
                                        raw = data[val:val + min(comp_data, len(data) - val)]
                                        if comp_data > 0 and uncomp_data > 0 and len(raw) == comp_data:
                                            try:
                                                decompress_vise(raw, uncomp_data)
                                                # Compute file_data_size
                                                fds = name_actual_start + nl - 0  # everything before name end, minus magic
                                                return entry_size - 4 - nl, nl_off, pos_off
                                            except:
                                                pass
                                        else:
                                            return entry_size - 4 - nl, nl_off, pos_off
                                except:
                                    pass

    # Fallback: use ScummVM layout
    return 120, 118, 96


def parse_catalog(data, version, cvct_offset):
    """Parse the CVCT catalog and return (directories, files, pack_entries)."""
    num_entries = struct.unpack('>H', data[cvct_offset + 16:cvct_offset + 18])[0]
    ver_minor = version & 0xFFFF

    directories = []
    files = []
    pack_entries = []

    # Determine DVCT extra bytes
    if ver_minor >= 0x0300:
        dvct_extra = 6
    else:
        dvct_extra = 0

    # For versions we fully understand, use sequential parsing (ScummVM approach)
    if ver_minor in (0x0201, 0x0202, 0x0300, 0x0301):
        pos = cvct_offset + 20
        for entry_idx in range(num_entries):
            if pos + 4 > len(data):
                break
            magic = data[pos:pos + 4]

            if magic == b'DVCT':
                ddata = data[pos + 4:pos + 4 + 78]
                containing_dir = struct.unpack('>H', ddata[68:70])[0]
                name_len = ddata[76]
                name_start = pos + 4 + 78 + dvct_extra
                name = data[name_start:name_start + name_len].decode('mac_roman', errors='replace')
                directories.append({
                    'name': name,
                    'containing_dir': containing_dir,
                })
                pos = name_start + name_len

            elif magic == b'FVCT':
                fd = data[pos + 4:pos + 4 + 120]
                ftype = fd[40:44].decode('mac_roman', errors='replace')
                fcreator = fd[44:48].decode('mac_roman', errors='replace')
                comp_data = struct.unpack('>I', fd[64:68])[0]
                uncomp_data = struct.unpack('>I', fd[68:72])[0]
                comp_rsrc = struct.unpack('>I', fd[72:76])[0]
                uncomp_rsrc = struct.unpack('>I', fd[76:80])[0]
                containing_dir = struct.unpack('>H', fd[92:94])[0]
                data_segment = struct.unpack('>H', fd[94:96])[0]
                archive_pos = struct.unpack('>I', fd[96:100])[0]
                name_len = fd[118]
                name_start = pos + 4 + 120
                name = data[name_start:name_start + name_len].decode('mac_roman', errors='replace')
                files.append({
                    'name': name,
                    'type': ftype,
                    'creator': fcreator,
                    'comp_data': comp_data,
                    'uncomp_data': uncomp_data,
                    'comp_rsrc': comp_rsrc,
                    'uncomp_rsrc': uncomp_rsrc,
                    'containing_dir': containing_dir,
                    'data_segment': data_segment,
                    'archive_pos': archive_pos,
                })
                pos = name_start + name_len

            elif magic == b'PACK':
                # Scan forward for next known marker
                scan = pos + 4
                while scan < len(data) - 4:
                    tag = data[scan:scan + 4]
                    if tag in (b'DVCT', b'FVCT', b'PACK', b'INDN'):
                        break
                    scan += 1
                pack_entries.append(data[pos:scan])
                pos = scan

            else:
                # Unknown entry type, try scanning forward
                scan = pos + 1
                while scan < len(data) - 4:
                    tag = data[scan:scan + 4]
                    if tag in (b'DVCT', b'FVCT', b'PACK', b'INDN'):
                        break
                    scan += 1
                pos = scan

    else:
        # For other versions, use marker-based scanning
        markers = scan_catalog_markers(data, cvct_offset)
        if not markers:
            print(f"  Warning: No catalog markers found", file=sys.stderr)
            return directories, files, pack_entries

        for i, (offset, tag) in enumerate(markers):
            next_offset = markers[i + 1][0] if i + 1 < len(markers) else len(data)
            entry = data[offset:next_offset]
            entry_size = next_offset - offset

            if tag == b'DVCT':
                # Try to extract directory name from the entry
                fd = entry[4:]
                name_len_76 = fd[76] if len(fd) > 76 else 0
                # Try multiple extra byte counts
                best_name = None
                for extra in [0, 2, 4, 6, 8, 10, 12, 14, 16]:
                    name_off = 78 + extra
                    if name_off + name_len_76 <= len(fd) and 0 < name_len_76 < 64:
                        try:
                            name = fd[name_off:name_off + name_len_76].decode('mac_roman', errors='replace')
                            printable = sum(1 for c in name if c.isprintable()) / max(len(name), 1)
                            # Verify total size matches
                            expected = 4 + 78 + extra + name_len_76
                            if expected == entry_size and printable > 0.7:
                                best_name = name
                                break
                        except:
                            pass
                if best_name is None and name_len_76 > 0 and name_len_76 < 64:
                    # Fallback: try without size verification
                    for extra in [6, 14, 0, 8]:
                        name_off = 78 + extra
                        if name_off + name_len_76 <= len(fd):
                            try:
                                name = fd[name_off:name_off + name_len_76].decode('mac_roman', errors='replace')
                                printable = sum(1 for c in name if c.isprintable()) / max(len(name), 1)
                                if printable > 0.7:
                                    best_name = name
                                    break
                            except:
                                pass

                containing_dir = struct.unpack('>H', fd[68:70])[0] if len(fd) > 70 else 0
                directories.append({
                    'name': best_name or f'_dir_{len(directories)}',
                    'containing_dir': containing_dir,
                })

            elif tag == b'FVCT':
                fd = entry[4:]
                if len(fd) < 80:
                    continue

                ftype = fd[40:44].decode('mac_roman', errors='replace')
                fcreator = fd[44:48].decode('mac_roman', errors='replace')
                comp_data = struct.unpack('>I', fd[64:68])[0]
                uncomp_data = struct.unpack('>I', fd[68:72])[0]
                comp_rsrc = struct.unpack('>I', fd[72:76])[0]
                uncomp_rsrc = struct.unpack('>I', fd[76:80])[0]

                # Find position_in_archive by scanning for plausible values
                archive_pos = 0
                for pos_off in [96, 100, 104, 108, 92, 88]:
                    if pos_off + 4 <= len(fd):
                        val = struct.unpack('>I', fd[pos_off:pos_off + 4])[0]
                        if 44 <= val < cvct_offset and val + comp_data + comp_rsrc <= cvct_offset + 1024:
                            archive_pos = val
                            break

                # Find containing_dir near the position field
                containing_dir = 0
                for cd_off in [92, 96, 100, 88]:
                    if cd_off + 2 <= len(fd):
                        val = struct.unpack('>H', fd[cd_off:cd_off + 2])[0]
                        if val <= len(directories) + 100:
                            containing_dir = val
                            break

                # Find name: scan from end of entry for readable text
                name = f'_file_{len(files)}'
                for nl_off in [118, 122, 126, 130, 114]:
                    if nl_off < len(fd):
                        nl = fd[nl_off]
                        if 0 < nl < 64:
                            # Search for the name at various positions after name_len
                            for gap in range(0, 60, 2):
                                ns = nl_off + 1 + gap
                                if ns + nl <= len(fd):
                                    try:
                                        candidate = fd[ns:ns + nl].decode('mac_roman', errors='replace')
                                        printable = sum(1 for c in candidate if c.isprintable()) / max(len(candidate), 1)
                                        if printable > 0.7 and '\x00' not in candidate:
                                            name = candidate
                                            break
                                    except:
                                        pass
                            if name != f'_file_{len(files)}':
                                break

                # Segment number (if available)
                data_segment = 1
                for seg_off in [94, 96, 100]:
                    if seg_off + 2 <= len(fd):
                        sv = struct.unpack('>H', fd[seg_off:seg_off + 2])[0]
                        if 1 <= sv <= 20:
                            data_segment = sv
                            break

                files.append({
                    'name': name,
                    'type': ftype,
                    'creator': fcreator,
                    'comp_data': comp_data,
                    'uncomp_data': uncomp_data,
                    'comp_rsrc': comp_rsrc,
                    'uncomp_rsrc': uncomp_rsrc,
                    'containing_dir': containing_dir,
                    'data_segment': data_segment,
                    'archive_pos': archive_pos,
                })

            elif tag == b'PACK':
                pack_entries.append(entry)

    # Build full paths for directories
    for d in directories:
        if d['containing_dir'] == 0:
            d['full_path'] = d['name']
        else:
            parent_idx = d['containing_dir'] - 1
            if 0 <= parent_idx < len(directories):
                d['full_path'] = os.path.join(directories[parent_idx].get('full_path', ''), d['name'])
            else:
                d['full_path'] = d['name']

    # Build full paths for files
    for f in files:
        if f['containing_dir'] == 0:
            f['full_path'] = f['name']
        else:
            parent_idx = f['containing_dir'] - 1
            if 0 <= parent_idx < len(directories):
                f['full_path'] = os.path.join(directories[parent_idx].get('full_path', ''), f['name'])
            else:
                f['full_path'] = f['name']

    return directories, files, pack_entries


def write_file(out_path, data_bytes, rsrc_bytes):
    """Write data fork and/or resource fork for a file."""
    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    extracted_data = False
    extracted_rsrc = False

    if data_bytes is not None:
        with open(out_path, 'wb') as fh:
            fh.write(data_bytes)
        extracted_data = True

    if rsrc_bytes is not None:
        with open(out_path + '.rsrc', 'wb') as fh:
            fh.write(rsrc_bytes)
        extracted_rsrc = True

    return extracted_data, extracted_rsrc


def extract_files(data, files, output_dir, current_segment=1):
    """Extract all files, handling shared compressed blobs.

    When multiple files share the same archive_pos, they are packed into a
    single compressed blob. The decompressed blob contains all data forks
    concatenated (in catalog order), followed by all resource forks concatenated.
    In this case, comp_data is the compressed blob size and comp_rsrc is the
    total uncompressed blob size.

    Single files use the standard layout: data fork compressed at archive_pos
    (comp_data bytes -> uncomp_data bytes), resource fork compressed at
    archive_pos + comp_data (comp_rsrc bytes -> uncomp_rsrc bytes).
    """
    from collections import OrderedDict

    # Group files by archive_pos, preserving catalog order within each group
    # Only include files on the current segment
    groups = OrderedDict()
    skipped_segments = 0
    for i, f in enumerate(files):
        seg = f.get('data_segment', 1)
        if seg != current_segment and seg != 0:
            skipped_segments += 1
            continue
        pos = f['archive_pos']
        if pos not in groups:
            groups[pos] = []
        groups[pos].append((i, f))

    if skipped_segments > 0:
        print(f"  Skipped {skipped_segments} files on other segments", file=sys.stderr)

    success_data = 0
    success_rsrc = 0
    fail_count = 0

    # Cache decompressed shared blobs
    blob_cache = {}

    for pos, group in groups.items():
        if len(group) == 1:
            # Single file - standard layout
            idx, f = group[0]
            name = f['name']
            full_path = f.get('full_path', name)
            safe_path = os.path.join(*[safe_filename(p) for p in full_path.split(os.sep)])
            out_path = os.path.join(output_dir, safe_path)

            data_bytes = None
            rsrc_bytes = None

            comp_data = f['comp_data']
            uncomp_data = f['uncomp_data']
            comp_rsrc = f['comp_rsrc']
            uncomp_rsrc = f['uncomp_rsrc']

            # Data fork
            if comp_data > 0 and uncomp_data > 0:
                raw = data[pos:pos + comp_data]
                if len(raw) == comp_data:
                    try:
                        data_bytes = decompress_vise(raw, uncomp_data)
                    except Exception as e:
                        print(f"  Warning: Failed to decompress data fork of '{name}': {e}", file=sys.stderr)

            # Resource fork (at pos + comp_data)
            if comp_rsrc > 0 and uncomp_rsrc > 0:
                rsrc_pos = pos + comp_data
                raw = data[rsrc_pos:rsrc_pos + comp_rsrc]
                if len(raw) == comp_rsrc:
                    try:
                        rsrc_bytes = decompress_vise(raw, uncomp_rsrc)
                    except Exception as e:
                        print(f"  Warning: Failed to decompress resource fork of '{name}': {e}", file=sys.stderr)

            ed, er = write_file(out_path, data_bytes, rsrc_bytes)
            if ed:
                success_data += 1
            if er:
                success_rsrc += 1
            if not ed and not er and (uncomp_data > 0 or uncomp_rsrc > 0):
                fail_count += 1
        else:
            # Shared blob - multiple files packed into one compressed stream
            # comp_data = compressed blob size, comp_rsrc = total uncompressed size
            first_f = group[0][1]
            comp_size = first_f['comp_data']
            total_uncomp = first_f['comp_rsrc']

            # Decompress the shared blob
            blob = None
            if comp_size > 0:
                raw = data[pos:pos + comp_size]
                if len(raw) == comp_size:
                    try:
                        blob = decompress_vise(raw, total_uncomp)
                    except Exception as e:
                        print(f"  Warning: Failed to decompress shared blob at 0x{pos:x}: {e}",
                              file=sys.stderr)

            if blob is None:
                # All files in this group fail
                for idx, f in group:
                    fail_count += 1
                continue

            # Split blob: data forks first (in order), then resource forks (in order)
            blob_off = 0
            data_chunks = []
            for idx, f in group:
                ud = f['uncomp_data']
                if ud > 0:
                    data_chunks.append(blob[blob_off:blob_off + ud])
                    blob_off += ud
                else:
                    data_chunks.append(None)

            rsrc_chunks = []
            for idx, f in group:
                ur = f['uncomp_rsrc']
                if ur > 0:
                    rsrc_chunks.append(blob[blob_off:blob_off + ur])
                    blob_off += ur
                else:
                    rsrc_chunks.append(None)

            # Write each file
            for j, (idx, f) in enumerate(group):
                name = f['name']
                full_path = f.get('full_path', name)
                safe_path = os.path.join(*[safe_filename(p) for p in full_path.split(os.sep)])
                out_path = os.path.join(output_dir, safe_path)

                ed, er = write_file(out_path, data_chunks[j], rsrc_chunks[j])
                if ed:
                    success_data += 1
                if er:
                    success_rsrc += 1
                if not ed and not er and (f['uncomp_data'] > 0 or f['uncomp_rsrc'] > 0):
                    fail_count += 1

    return success_data, success_rsrc, fail_count


def parse_indn(data, cvct_offset):
    """Parse the INDN disk name table at the end of the file."""
    # Search for INDN marker after the CVCT section
    pos = cvct_offset
    while pos < len(data) - 4:
        if data[pos:pos + 4] == b'INDN':
            break
        pos += 1
    else:
        return None

    indn_start = pos
    result = {'offset': indn_start, 'disks': []}
    pos += 4  # skip magic

    if pos >= len(data):
        return result

    unknown_byte = data[pos]
    pos += 1
    if pos >= len(data):
        return result

    disk_count = data[pos]
    pos += 1

    for _ in range(disk_count):
        if pos >= len(data):
            break
        name_len = data[pos]
        pos += 1
        if pos + name_len > len(data):
            break
        disk_name = data[pos:pos + name_len].decode('mac_roman', errors='replace')
        pos += name_len
        # 6 bytes of disk info follow
        disk_info = data[pos:pos + 6] if pos + 6 <= len(data) else b''
        pos += 6
        result['disks'].append({'name': disk_name, 'info': disk_info})

    return result


def version_string(version):
    """Convert a VISE version code to a human-readable string."""
    major = (version >> 8) & 0xFF
    minor = version & 0xFF
    if version == 0x80010202:
        return f"{major}.{minor:02d} (Installer VISE 3.5 Lite)"
    elif version == 0x80010300:
        return f"{major}.{minor:02d} (Installer VISE 3.6 Lite)"
    return f"{major}.{minor:02d}"


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    with open(input_file, 'rb') as fh:
        data = fh.read()

    # Parse header
    version, cvct_offset, segment = parse_svct_header(data)
    ver_minor = version & 0xFFFF

    print(f"VISE Archive: {os.path.basename(input_file)}")
    print(f"  Version: 0x{version:08x} ({version_string(version)})")
    print(f"  Segment: {segment}")
    print(f"  CVCT offset: 0x{cvct_offset:x} ({cvct_offset})")
    print(f"  File size: {len(data)} bytes")

    if segment > 1:
        print(f"  Note: This is segment {segment} of a multi-segment archive.")
        print(f"  Segment files contain only data; catalog is in segment 1.")
        sys.exit(0)

    # Verify CVCT magic
    if data[cvct_offset:cvct_offset + 4] != b'CVCT':
        print(f"  Error: CVCT magic not found at offset 0x{cvct_offset:x}", file=sys.stderr)
        sys.exit(1)

    num_entries = struct.unpack('>H', data[cvct_offset + 16:cvct_offset + 18])[0]
    print(f"  Catalog entries: {num_entries}")

    # Parse catalog
    directories, files, pack_entries = parse_catalog(data, version, cvct_offset)

    print(f"  Directories: {len(directories)}")
    print(f"  Files: {len(files)}")
    if pack_entries:
        print(f"  Package entries: {len(pack_entries)}")

    if not files:
        print("  No files found to extract.", file=sys.stderr)
        sys.exit(1)

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Print file listing
    for i, f in enumerate(files):
        name = f['name']
        ftype = f['type']
        fcreator = f['creator']
        uncomp_data = f['uncomp_data']
        uncomp_rsrc = f['uncomp_rsrc']
        full_path = f.get('full_path', name)

        status_parts = []
        if uncomp_data > 0:
            status_parts.append(f"data:{uncomp_data}")
        if uncomp_rsrc > 0:
            status_parts.append(f"rsrc:{uncomp_rsrc}")
        status = ', '.join(status_parts) if status_parts else 'empty'

        print(f"  [{i + 1}/{len(files)}] {full_path} ({ftype}/{fcreator}) [{status}]")

    # Extract files (handles both single and shared blob layouts)
    success_data, success_rsrc, fail_count = extract_files(data, files, output_dir, segment)

    # Parse INDN
    indn = parse_indn(data, cvct_offset)
    if indn and indn['disks']:
        print(f"\n  Disk names:")
        for disk in indn['disks']:
            print(f"    {disk['name']}")

    print(f"\nExtraction complete:")
    print(f"  Data forks extracted: {success_data}")
    print(f"  Resource forks extracted: {success_rsrc}")
    if fail_count:
        print(f"  Failed: {fail_count}")


if __name__ == '__main__':
    main()

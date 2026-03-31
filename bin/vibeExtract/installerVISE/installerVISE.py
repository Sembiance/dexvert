# Vibe coded by Claude
"""
unvise.py - Extract files from Installer VISE archives (Mac OS)

Usage: python3 unvise.py <inputFile> <outputDir>

Supports Installer VISE versions 1.x through 3.x.
Handles both standalone VISE files and self-extracting installers (SVCT at offset 128).
Decompression based on reverse-engineering by the ScummVM project (elasota, 2022).
"""

import sys
import os
import struct
import zlib
import json
from collections import OrderedDict

# Deobfuscation table for VISE compression
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

# FVCT field offsets (relative to file_data start, i.e., byte 4 of entry)
# These are consistent across all known versions (v1.01 through v3.11)
FVCT_TYPE = 40          # 4 bytes: Mac OS file type
FVCT_CREATOR = 44       # 4 bytes: Mac OS creator code
FVCT_FINDER_FLAGS = 48  # 2 bytes: Finder flags (fdFlags)
FVCT_CREATION_DATE = 56 # 4 bytes: creation date (seconds since 1904-01-01)
FVCT_MOD_DATE = 60      # 4 bytes: modification date (seconds since 1904-01-01)
FVCT_COMP_DATA = 64     # 4 bytes: compressed data fork size
FVCT_UNCOMP_DATA = 68   # 4 bytes: uncompressed data fork size
FVCT_COMP_RSRC = 72     # 4 bytes: compressed resource fork size
FVCT_UNCOMP_RSRC = 76   # 4 bytes: uncompressed resource fork size
FVCT_CONTAINING_DIR = 92 # 2 bytes: parent directory index (1-based, 0=root)
FVCT_DATA_SEGMENT = 94  # 2 bytes: segment number containing file data
FVCT_ARCHIVE_POS = 96   # 4 bytes: byte offset of compressed data
FVCT_NAME_LEN = 118     # 1 byte: length of file name
# Name is always the LAST name_len bytes of the entry (for all versions)

# DVCT field offsets (relative to directory_data start, i.e., byte 4 of entry)
DVCT_CONTAINING_DIR = 68 # 2 bytes: parent directory index
DVCT_NAME_LEN = 76      # 1 byte: length of directory name
# Name is always the LAST name_len bytes of the entry (for all versions)


def byte_swap(raw):
    """Swap adjacent byte pairs (first step of VISE deobfuscation)."""
    data = bytearray(raw)
    for i in range(1, len(data), 2):
        data[i], data[i - 1] = data[i - 1], data[i]
    return bytes(data)


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
    """Deobfuscate and decompress a VISE compressed stream.

    Some small files (URL bookmarks, etc.) have a 1-byte prefix (0x01) before
    the actual deflate stream. If standard decompression fails, we retry after
    skipping the first byte.
    """
    if expected_size == 0:
        return b''
    deobf = deobfuscate(raw)
    try:
        dec = zlib.decompressobj(-zlib.MAX_WBITS)
        result = dec.decompress(deobf, expected_size)
        if len(result) == expected_size:
            return result
        raise ValueError(f"Decompressed size {len(result)} != expected {expected_size}")
    except Exception as first_err:
        # Retry with 1-byte prefix skip. Some files (URL bookmarks, etc.) have a
        # 1-byte prefix before the deflate stream, and the stored block within has
        # BFINAL=0 with trailing junk. Limiting output to expected_size makes the
        # decompressor stop before hitting the invalid trailing data.
        if len(deobf) > 1:
            try:
                dec2 = zlib.decompressobj(-zlib.MAX_WBITS)
                result2 = dec2.decompress(deobf[1:], expected_size)
                if len(result2) == expected_size:
                    return result2
            except Exception:
                pass
        raise first_err


def safe_filename(name):
    """Sanitize a Mac filename for use on modern filesystems."""
    name = name.replace(':', '_')
    for ch in '/\\<>"|?*':
        name = name.replace(ch, '_')
    name = ''.join(c for c in name if ord(c) >= 32)
    if not name:
        name = '_unnamed_'
    return name


def _crc16_xmodem(data):
    """Calculate CRC-16/XMODEM (polynomial 0x1021) for MacBinary II header."""
    crc = 0
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc


def build_macbinary(filename, ftype, fcreator, finder_flags, creation_date,
                    mod_date, data_fork, rsrc_fork):
    """Build a MacBinary II format file.

    Args:
        filename: Mac filename (str, max 63 chars)
        ftype: 4-char file type string
        fcreator: 4-char creator string
        finder_flags: 16-bit Finder flags
        creation_date: Mac epoch seconds (uint32, seconds since 1904-01-01)
        mod_date: Mac epoch seconds (uint32, seconds since 1904-01-01)
        data_fork: bytes of data fork (or b'' if none)
        rsrc_fork: bytes of resource fork (or b'' if none)

    Returns:
        Complete MacBinary II file as bytes.
    """
    # Encode filename (max 63 bytes in MacBinary)
    name_bytes = filename.encode('mac_roman', errors='replace')[:63]
    name_len = len(name_bytes)

    # Build 128-byte header
    header = bytearray(128)
    header[0] = 0                           # +0: old version number (must be 0)
    header[1] = name_len                    # +1: name length
    header[2:2 + name_len] = name_bytes     # +2: filename (63 bytes max, null-padded)
    header[65:69] = ftype.encode('mac_roman', errors='replace')[:4].ljust(4, b'\x00')     # +65: type
    header[69:73] = fcreator.encode('mac_roman', errors='replace')[:4].ljust(4, b'\x00')  # +69: creator
    header[73] = (finder_flags >> 8) & 0xFF # +73: Finder flags high byte
    # +74: zero (must be 0 for MacBinary)
    # +75-78: icon position (0,0)
    # +79-80: folder ID (0)
    # +81: protected flag (0)
    # +82: zero (must be 0)
    data_len = len(data_fork)
    rsrc_len = len(rsrc_fork)
    struct.pack_into('>I', header, 83, data_len)    # +83: data fork length
    struct.pack_into('>I', header, 87, rsrc_len)    # +87: resource fork length
    struct.pack_into('>I', header, 91, creation_date)   # +91: creation date
    struct.pack_into('>I', header, 95, mod_date)        # +95: modification date
    # +99-100: comment length (0)
    header[101] = finder_flags & 0xFF       # +101: Finder flags low byte
    # +102-109: reserved
    # +110-113: reserved
    # +114-115: reserved
    header[122] = 0x81                      # +122: MacBinary II version (129)
    header[123] = 0x81                      # +123: minimum version to read (129)
    # +124-125: CRC-16/XMODEM of bytes 0-123
    crc = _crc16_xmodem(header[:124])
    struct.pack_into('>H', header, 124, crc)

    # Build complete file: header + data fork (padded) + rsrc fork (padded)
    parts = [bytes(header)]
    if data_len > 0:
        parts.append(data_fork)
        pad = (128 - (data_len % 128)) % 128
        if pad:
            parts.append(b'\x00' * pad)
    if rsrc_len > 0:
        parts.append(rsrc_fork)
        pad = (128 - (rsrc_len % 128)) % 128
        if pad:
            parts.append(b'\x00' * pad)

    return b''.join(parts)


def find_svct_offset(data):
    """Find the SVCT header in a file. Returns offset, or -1 if not found.

    VISE archives may be standalone (SVCT at offset 0) or embedded in
    self-extracting installers (SVCT typically at offset 128).
    """
    if len(data) >= 44 and data[0:4] == b'SVCT':
        return 0
    idx = data.find(b'SVCT')
    if idx >= 0 and idx + 44 <= len(data):
        return idx
    return -1


def parse_svct_header(data):
    """Parse the 44-byte SVCT header. Returns (version, cvct_offset, segment).

    data should start at the SVCT header (already offset-adjusted).
    """
    if len(data) < 44:
        raise ValueError("File too small for SVCT header")
    magic = data[0:4]
    if magic != b'SVCT':
        raise ValueError(f"Not a VISE file (magic: {magic!r})")
    segment = struct.unpack('>I', data[4:8])[0]
    version = struct.unpack('>I', data[16:20])[0]
    cvct_offset = struct.unpack('>I', data[36:40])[0]
    return version, cvct_offset, segment


def find_cvct_offset(data, claimed_offset):
    """Find the actual CVCT position in the data.

    First checks the claimed offset from the SVCT header. If CVCT magic isn't
    there, searches the data for a valid CVCT header.

    Returns (actual_offset, shift) where shift = actual - claimed.
    Returns (None, 0) if no CVCT is found.
    """
    # Check claimed position first
    if (claimed_offset + 4 <= len(data)
            and data[claimed_offset:claimed_offset + 4] == b'CVCT'):
        return claimed_offset, 0

    # Search for CVCT in the data
    pos = 44  # skip past SVCT header at minimum
    while pos < len(data) - 20:
        idx = data.find(b'CVCT', pos)
        if idx < 0:
            break
        # Validate: check that it looks like a real CVCT header
        if idx + 20 <= len(data):
            num_entries = struct.unpack('>H', data[idx + 16:idx + 18])[0]
            # Real catalogs have a reasonable entry count
            if 0 < num_entries < 5000:
                return idx, idx - claimed_offset
        pos = idx + 1

    return None, 0


def scan_catalog_markers(data, cvct_offset):
    """Scan the catalog section for DVCT/FVCT/PACK/INDN markers.

    Returns list of (offset, tag) tuples.
    """
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


def _is_phantom_size(n):
    """Check if n matches a phantom entry's characteristic size value.

    Phantom entries have size values that look like two packed 16-bit fields
    misread as one 32-bit value. The pattern is N * 65536 + M where N is a
    small integer (1-8) and M is small (0-8). Also matches exact powers of 2
    >= 0x8000 (32768).
    """
    if n < 0x8000:
        return False
    # N * 65536 + M, where N is small (1-8) and M is small (0-4)
    # This catches 0x10000, 0x10001, 0x10004, 0x20001, 0x40001, 0x40002, etc.
    low = n & 0xFFFF
    high = n >> 16
    if 1 <= high <= 8 and low <= 8:
        return True
    # Exact power of 2 (0x8000, etc.)
    if (n & (n - 1)) == 0:
        return True
    return False


def _is_phantom_entry(comp_data, uncomp_data, comp_rsrc, uncomp_rsrc):
    """Detect phantom/package FVCT entries based on their size field patterns.

    Phantom entries have characteristic packed-16-bit values in their size fields
    (e.g. comp_data=0x40001, uncomp_data=0x10001). These look like two 16-bit
    fields being misread as one 32-bit field. Real files never have both
    comp_data and uncomp_data set to these magic values.
    """
    if comp_data == 0 or uncomp_data == 0:
        return False
    # Both comp_data and uncomp_data are phantom-like values
    if _is_phantom_size(comp_data) and _is_phantom_size(uncomp_data):
        return True
    return False


def parse_fvct_entry(entry, cvct_offset=0, allow_post_catalog=False):
    """Parse an FVCT entry of any size. entry includes the 4-byte magic.

    cvct_offset is used to validate archive_pos (should be < cvct_offset).
    allow_post_catalog: if True, allow archive_pos >= cvct_offset (for v3.11+).
    Returns a dict with file metadata, or None if invalid.
    """
    entry_size = len(entry)
    fd = entry[4:]  # file data (everything after magic)
    if len(fd) < 120:
        return None

    name_len = fd[FVCT_NAME_LEN]
    # v10.80/v11.00 have name_length at +120 instead of +118
    if (name_len == 0 or name_len > 63) and len(fd) > 120:
        name_len = fd[120]
    if name_len == 0 or name_len > 63 or name_len > len(fd):
        return None

    # Name is the last name_len bytes of the entry
    name_bytes = entry[entry_size - name_len:]
    try:
        name = name_bytes.decode('mac_roman', errors='replace')
    except:
        return None

    # Validate name: should be mostly printable (real Mac filenames are ~100%)
    printable = sum(1 for c in name if c.isprintable()) / max(len(name), 1)
    if printable < 0.7 or '\x00' in name:
        return None

    ftype_raw = fd[FVCT_TYPE:FVCT_TYPE + 4]
    fcreator_raw = fd[FVCT_CREATOR:FVCT_CREATOR + 4]
    ftype = ftype_raw.decode('mac_roman', errors='replace')
    fcreator = fcreator_raw.decode('mac_roman', errors='replace')
    finder_flags = struct.unpack('>H', fd[FVCT_FINDER_FLAGS:FVCT_FINDER_FLAGS + 2])[0]
    creation_date = struct.unpack('>I', fd[FVCT_CREATION_DATE:FVCT_CREATION_DATE + 4])[0]
    mod_date = struct.unpack('>I', fd[FVCT_MOD_DATE:FVCT_MOD_DATE + 4])[0]
    comp_data = struct.unpack('>I', fd[FVCT_COMP_DATA:FVCT_COMP_DATA + 4])[0]
    uncomp_data = struct.unpack('>I', fd[FVCT_UNCOMP_DATA:FVCT_UNCOMP_DATA + 4])[0]
    comp_rsrc = struct.unpack('>I', fd[FVCT_COMP_RSRC:FVCT_COMP_RSRC + 4])[0]
    uncomp_rsrc = struct.unpack('>I', fd[FVCT_UNCOMP_RSRC:FVCT_UNCOMP_RSRC + 4])[0]
    containing_dir = struct.unpack('>H', fd[FVCT_CONTAINING_DIR:FVCT_CONTAINING_DIR + 2])[0]
    data_segment = struct.unpack('>H', fd[FVCT_DATA_SEGMENT:FVCT_DATA_SEGMENT + 2])[0]
    archive_pos = struct.unpack('>I', fd[FVCT_ARCHIVE_POS:FVCT_ARCHIVE_POS + 4])[0]

    # Filter phantom/package entries: these are installer action references, not
    # extractable files. They have characteristic magic size values that are
    # powers of 2 or powers of 2 plus 1 (e.g. 0x10001, 0x20001, 0x40001).
    if _is_phantom_entry(comp_data, uncomp_data, comp_rsrc, uncomp_rsrc):
        return None

    # Validate: compressed sizes should be reasonable (< 50 MB)
    if comp_data > 50_000_000 or comp_rsrc > 50_000_000:
        return None

    # Validate: archive_pos should be within data area (before catalog)
    # Exception: v3.11 stores some file data after the catalog
    if cvct_offset > 0 and archive_pos > 0:
        if archive_pos >= cvct_offset:
            if not allow_post_catalog:
                return None

    # Validate: segment number should be reasonable
    if data_segment > 100:
        return None

    return {
        'name': name,
        'type': ftype,
        'creator': fcreator,
        'finder_flags': finder_flags,
        'creation_date': creation_date,
        'mod_date': mod_date,
        'comp_data': comp_data,
        'uncomp_data': uncomp_data,
        'comp_rsrc': comp_rsrc,
        'uncomp_rsrc': uncomp_rsrc,
        'containing_dir': containing_dir,
        'data_segment': data_segment,
        'archive_pos': archive_pos,
    }


def parse_dvct_entry(entry):
    """Parse a DVCT entry of any size. entry includes the 4-byte magic.

    Returns a dict with directory metadata, or None if invalid.
    """
    entry_size = len(entry)
    dd = entry[4:]  # directory data
    if len(dd) < 78:
        return None

    name_len = dd[DVCT_NAME_LEN]
    # v10.80/v11.00 have name_length at +78 instead of +76
    if (name_len == 0 or name_len > 63) and len(dd) > 78:
        name_len = dd[78]
    if name_len == 0 or name_len > 63 or name_len > len(dd):
        return None

    # Name is the last name_len bytes of the entry
    name_bytes = entry[entry_size - name_len:]
    try:
        name = name_bytes.decode('mac_roman', errors='replace')
    except:
        name = f'_dir_'

    containing_dir = struct.unpack('>H', dd[DVCT_CONTAINING_DIR:DVCT_CONTAINING_DIR + 2])[0]

    return {
        'name': name,
        'containing_dir': containing_dir,
    }


def decompress_catalog_v312(data, cvct_offset):
    """Decompress the v3.12+ compressed catalog blob.

    v3.12+ catalogs have a 80-byte preamble (type tags + offset table) followed
    by a compressed blob. The blob uses byte-swap only (no substitution cipher)
    + raw deflate, unlike file data which uses the full deobfuscation pipeline.

    Some archives have an uncompressed catalog (blob starts with a known marker
    like FVCT/DVCT/PACK). In that case, return the raw blob data directly.

    Returns the decompressed catalog data, or None on failure.
    """
    blob_size = struct.unpack('>I', data[cvct_offset + 4:cvct_offset + 8])[0]
    blob_start = cvct_offset + 20 + 80  # skip CVCT header (20) + preamble (80)
    if blob_start + blob_size > len(data):
        return None
    blob = data[blob_start:blob_start + blob_size]
    # Check if catalog is already uncompressed (starts with a known marker)
    _KNOWN_MARKERS = (b'DVCT', b'FVCT', b'PACK', b'INDN', b'BBrd', b'CODE',
                      b'BDIR', b'PROJ', b'DfIL')
    if len(blob) >= 4 and blob[:4] in _KNOWN_MARKERS:
        return blob
    swapped = byte_swap(blob)
    try:
        dec = zlib.decompressobj(-zlib.MAX_WBITS)
        return dec.decompress(swapped)
    except Exception:
        return None


def _parse_decompressed_catalog(cat_data, cvct_offset, directories, files, pack_entries):
    """Scan decompressed catalog data for markers and parse entries."""
    markers = []
    i = 0
    while i < len(cat_data) - 3:
        tag = cat_data[i:i + 4]
        if tag in (b'DVCT', b'FVCT', b'PACK', b'INDN', b'BBrd', b'CODE',
                   b'BDIR', b'PROJ', b'DfIL'):
            markers.append((i, tag))
            i += 4
        else:
            i += 1

    for mi, (offset, tag) in enumerate(markers):
        next_off = markers[mi + 1][0] if mi + 1 < len(markers) else len(cat_data)
        entry = cat_data[offset:next_off]

        if tag == b'DVCT':
            parsed = parse_dvct_entry(entry)
            if parsed:
                directories.append(parsed)
        elif tag == b'FVCT':
            parsed = parse_fvct_entry(entry, cvct_offset, allow_post_catalog=True)
            if parsed:
                files.append(parsed)
        elif tag == b'PACK':
            pack_entries.append(entry)


def parse_catalog(data, version, cvct_offset):
    """Parse the CVCT catalog and return (directories, files, pack_entries)."""
    num_entries = struct.unpack('>H', data[cvct_offset + 16:cvct_offset + 18])[0]
    ver_minor = version & 0xFFFF

    directories = []
    files = []
    pack_entries = []

    # For well-understood versions, use sequential parsing (exact byte-level layout)
    # v0.01/v1.01/v2.01/v2.02 use 0 extra DVCT bytes; v3.00/v3.01 use 6
    if ver_minor in (0x0001, 0x0101, 0x0201, 0x0202, 0x0300, 0x0301):
        dvct_extra = 6 if ver_minor >= 0x0300 else 0
        pos = cvct_offset + 20
        for entry_idx in range(num_entries):
            if pos + 4 > len(data):
                break
            magic = data[pos:pos + 4]

            if magic == b'DVCT':
                dd = data[pos + 4:pos + 4 + 78]
                containing_dir = struct.unpack('>H', dd[68:70])[0]
                name_len = dd[76]
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
                finder_flags = struct.unpack('>H', fd[48:50])[0]
                creation_date = struct.unpack('>I', fd[56:60])[0]
                mod_date = struct.unpack('>I', fd[60:64])[0]
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
                # Skip phantom/package entries and non-printable names
                name_printable = sum(1 for c in name if c.isprintable()) / max(len(name), 1)
                if name_printable >= 0.7 and not _is_phantom_entry(comp_data, uncomp_data, comp_rsrc, uncomp_rsrc):
                    files.append({
                        'name': name,
                        'type': ftype,
                        'creator': fcreator,
                        'finder_flags': finder_flags,
                        'creation_date': creation_date,
                        'mod_date': mod_date,
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
                scan = pos + 4
                while scan < len(data) - 4:
                    tag = data[scan:scan + 4]
                    if tag in (b'DVCT', b'FVCT', b'PACK', b'INDN'):
                        break
                    scan += 1
                pack_entries.append(data[pos:scan])
                pos = scan

            else:
                scan = pos + 1
                while scan < len(data) - 4:
                    tag = data[scan:scan + 4]
                    if tag in (b'DVCT', b'FVCT', b'PACK', b'INDN'):
                        break
                    scan += 1
                pos = scan

    elif ver_minor >= 0x030c:
        # v3.12+: catalog is always compressed (byte-swap + raw deflate, no substitution)
        cat_data = decompress_catalog_v312(data, cvct_offset)
        if cat_data is None:
            print(f"  Warning: Failed to decompress v3.12+ catalog", file=sys.stderr)
            return directories, files, pack_entries

        _parse_decompressed_catalog(cat_data, cvct_offset, directories, files, pack_entries)

    else:
        # For v3.02-v3.11, try marker-based scanning first. If no FVCT/DVCT
        # markers are found, the catalog may be compressed (v3.08+ introduced
        # compressed catalogs alongside uncompressed ones).
        # Allow post-catalog archive_pos when catalog is near the start
        # (catalog-first layout) or for v3.11+ which stores data after catalog.
        allow_post = ver_minor >= 0x030b or cvct_offset < 4096
        markers = scan_catalog_markers(data, cvct_offset)
        has_fvct_dvct = any(tag in (b'FVCT', b'DVCT') for _, tag in markers)

        if has_fvct_dvct:
            for i, (offset, tag) in enumerate(markers):
                next_offset = markers[i + 1][0] if i + 1 < len(markers) else len(data)
                entry = data[offset:next_offset]

                if tag == b'DVCT':
                    parsed = parse_dvct_entry(entry)
                    if parsed:
                        directories.append(parsed)
                elif tag == b'FVCT':
                    parsed = parse_fvct_entry(entry, cvct_offset, allow_post_catalog=allow_post)
                    if parsed:
                        files.append(parsed)
                elif tag == b'PACK':
                    pack_entries.append(entry)

        # If marker scan found 0 files, try decompression as fallback.
        # This handles cases where FVCT/DVCT patterns appear as false
        # positives in compressed catalog data.
        if not files and not has_fvct_dvct or (not files and num_entries > 1):
            cat_data = decompress_catalog_v312(data, cvct_offset)
            if cat_data is not None:
                directories.clear()
                pack_entries.clear()
                _parse_decompressed_catalog(cat_data, cvct_offset, directories, files, pack_entries)

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


def write_file(out_path, data_bytes, rsrc_bytes, file_meta=None):
    """Write a file, using MacBinary II format when a resource fork exists.

    If rsrc_bytes is provided, writes a single MacBinary II file containing
    both forks. Otherwise writes the data fork as a plain file.

    file_meta should be a dict with keys: name, type, creator, finder_flags,
    creation_date, mod_date. Defaults are used if not provided.
    """
    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    extracted_data = False
    extracted_rsrc = False

    if rsrc_bytes is not None:
        # Write as MacBinary II (both forks in one file)
        meta = file_meta or {}
        mb = build_macbinary(
            filename=meta.get('name', os.path.basename(out_path)),
            ftype=meta.get('type', '\x00\x00\x00\x00'),
            fcreator=meta.get('creator', '\x00\x00\x00\x00'),
            finder_flags=meta.get('finder_flags', 0),
            creation_date=meta.get('creation_date', 0),
            mod_date=meta.get('mod_date', 0),
            data_fork=data_bytes or b'',
            rsrc_fork=rsrc_bytes,
        )
        with open(out_path, 'wb') as fh:
            fh.write(mb)
        extracted_data = data_bytes is not None
        extracted_rsrc = True
    elif data_bytes is not None:
        # Plain file (data fork only)
        with open(out_path, 'wb') as fh:
            fh.write(data_bytes)
        extracted_data = True

    # Set file mtime to original modification date
    if (extracted_data or extracted_rsrc) and file_meta:
        mod_date = file_meta.get('mod_date', 0)
        if mod_date > 0:
            import datetime
            mac_epoch = datetime.datetime(1904, 1, 1)
            try:
                dt = mac_epoch + datetime.timedelta(seconds=mod_date)
                ts = dt.timestamp()
                os.utime(out_path, (ts, ts))
            except (OverflowError, ValueError, OSError):
                pass

    return extracted_data, extracted_rsrc


def _mac_date_to_iso(mac_seconds):
    """Convert Mac epoch timestamp (seconds since 1904-01-01) to ISO string."""
    if mac_seconds == 0:
        return None
    import datetime
    mac_epoch = datetime.datetime(1904, 1, 1)
    try:
        dt = mac_epoch + datetime.timedelta(seconds=mac_seconds)
        return dt.strftime('%Y-%m-%dT%H:%M:%S')
    except (OverflowError, ValueError):
        return None


def _build_file_meta(f, has_data, has_rsrc):
    """Build a metadata dict for one file for _metadata.json output."""
    meta = {
        'type': f.get('type', ''),
        'creator': f.get('creator', ''),
    }
    finder_flags = f.get('finder_flags', 0)
    if finder_flags:
        meta['finder_flags'] = finder_flags
    cdate = _mac_date_to_iso(f.get('creation_date', 0))
    if cdate:
        meta['creation_date'] = cdate
    mdate = _mac_date_to_iso(f.get('mod_date', 0))
    if mdate:
        meta['modification_date'] = mdate
    if has_data:
        meta['data_fork_size'] = f.get('uncomp_data', 0)
    if has_rsrc:
        meta['rsrc_fork_size'] = f.get('uncomp_rsrc', 0)
        meta['format'] = 'macbinary'
    return meta


def extract_files(data, files, output_dir, current_segment=1):
    """Extract all files, handling shared compressed blobs.

    When multiple files share the same archive_pos, they are packed into a
    single compressed blob. The decompressed blob contains all data forks
    concatenated (in catalog order), followed by all resource forks concatenated.
    comp_data = compressed blob size, comp_rsrc = total uncompressed size.

    Single files use the standard layout: data fork compressed at archive_pos
    (comp_data bytes -> uncomp_data bytes), resource fork compressed at
    archive_pos + comp_data (comp_rsrc bytes -> uncomp_rsrc bytes).

    Returns (success_data, success_rsrc, fail_count, file_metadata) where
    file_metadata is a dict keyed by relative output path with type/creator/etc.
    """
    # Group files by archive_pos, preserving catalog order within each group
    data_len = len(data)
    groups = OrderedDict()
    skipped_segments = 0
    no_data_count = 0
    for i, f in enumerate(files):
        seg = f.get('data_segment', 1)
        if seg != current_segment and seg != 0:
            skipped_segments += 1
            continue
        # Files with uncomp sizes but zero comp sizes have no data in this archive
        has_uncomp = f['uncomp_data'] > 0 or f['uncomp_rsrc'] > 0
        has_comp = f['comp_data'] > 0 or f['comp_rsrc'] > 0
        if has_uncomp and not has_comp:
            no_data_count += 1
            continue
        pos = f['archive_pos']
        # If the compressed data extends beyond the file, it's on a missing segment
        total_comp = f['comp_data'] + f.get('comp_rsrc', 0)
        if pos + total_comp > data_len and total_comp > 0:
            skipped_segments += 1
            continue
        if pos not in groups:
            groups[pos] = []
        groups[pos].append((i, f))

    # For shared blob groups with mixed segments, prefer current_segment files
    for pos in list(groups.keys()):
        group = groups[pos]
        if len(group) > 1:
            has_cur = any(f.get('data_segment', 1) == current_segment for _, f in group)
            has_zero = any(f.get('data_segment', 1) == 0 for _, f in group)
            if has_cur and has_zero:
                filtered = [(i, f) for i, f in group if f.get('data_segment', 1) == current_segment]
                removed = len(group) - len(filtered)
                groups[pos] = filtered
                no_data_count += removed

    if skipped_segments > 0:
        print(f"  Skipped {skipped_segments} files on other segments", file=sys.stderr)
    if no_data_count > 0:
        print(f"  Skipped {no_data_count} files with no data in archive", file=sys.stderr)

    success_data = 0
    success_rsrc = 0
    fail_count = 0
    file_metadata = {}

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

            ed, er = write_file(out_path, data_bytes, rsrc_bytes, f)
            if ed or er:
                file_metadata[safe_path] = _build_file_meta(f, ed, er)
            if ed:
                success_data += 1
            if er:
                success_rsrc += 1
            if not ed and not er and (uncomp_data > 0 or uncomp_rsrc > 0):
                fail_count += 1
        else:
            # Shared blob - multiple files packed into one compressed stream
            first_f = group[0][1]
            comp_size = first_f['comp_data']
            total_uncomp = first_f['comp_rsrc']

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

            for j, (idx, f) in enumerate(group):
                name = f['name']
                full_path = f.get('full_path', name)
                safe_path = os.path.join(*[safe_filename(p) for p in full_path.split(os.sep)])
                out_path = os.path.join(output_dir, safe_path)

                ed, er = write_file(out_path, data_chunks[j], rsrc_chunks[j], f)
                if ed or er:
                    file_metadata[safe_path] = _build_file_meta(f, ed, er)
                if ed:
                    success_data += 1
                if er:
                    success_rsrc += 1
                if not ed and not er and (f['uncomp_data'] > 0 or f['uncomp_rsrc'] > 0):
                    fail_count += 1

    return success_data, success_rsrc, fail_count, file_metadata


def parse_indn(data, cvct_offset):
    """Parse the INDN disk name table at the end of the file."""
    pos = cvct_offset
    while pos < len(data) - 4:
        if data[pos:pos + 4] == b'INDN':
            break
        pos += 1
    else:
        return None

    indn_start = pos
    result = {'offset': indn_start, 'disks': []}
    pos += 4

    if pos >= len(data):
        return result
    pos += 1  # unknown byte
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
        full_data = fh.read()

    # Find SVCT header (may be at offset 0 or embedded at offset 128+)
    svct_off = find_svct_offset(full_data)
    if svct_off < 0:
        print(f"Error: No SVCT header found in {input_file}", file=sys.stderr)
        sys.exit(1)

    # Slice data so all offsets are relative to SVCT header
    data = full_data[svct_off:]

    # Parse header
    version, cvct_offset, segment = parse_svct_header(data)
    ver_minor = version & 0xFFFF

    print(f"VISE Archive: {os.path.basename(input_file)}")
    print(f"  Version: 0x{version:08x} ({version_string(version)})")
    print(f"  Segment: {segment}")
    if svct_off > 0:
        print(f"  SVCT offset: {svct_off} (self-extracting)")
    print(f"  CVCT offset: 0x{cvct_offset:x} ({cvct_offset})")
    print(f"  File size: {len(full_data)} bytes")

    if segment > 1:
        print(f"  Note: This is segment {segment} of a multi-segment archive.")
        print(f"  Segment files contain only data; catalog is in segment 1.")
        sys.exit(0)

    # Verify CVCT magic (with fallback search if not at claimed offset)
    actual_cvct, pos_shift = find_cvct_offset(data, cvct_offset)
    if actual_cvct is None:
        print(f"  Error: CVCT magic not found at offset 0x{cvct_offset:x}", file=sys.stderr)
        sys.exit(1)
    if pos_shift != 0:
        print(f"  Note: CVCT found at 0x{actual_cvct:x} (claimed 0x{cvct_offset:x}, shift={pos_shift:+d})")
        cvct_offset = actual_cvct

    num_entries = struct.unpack('>H', data[cvct_offset + 16:cvct_offset + 18])[0]
    print(f"  Catalog entries: {num_entries}")

    # Parse catalog
    directories, files, pack_entries = parse_catalog(data, version, cvct_offset)

    # Adjust archive positions if CVCT was at a different offset than claimed
    if pos_shift != 0:
        for f in files:
            f['archive_pos'] += pos_shift

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

    # Extract files
    success_data, success_rsrc, fail_count, file_metadata = extract_files(data, files, output_dir, segment)

    # Write _metadata.json
    if file_metadata:
        meta_path = os.path.join(output_dir, '_metadata.json')
        with open(meta_path, 'w') as fh:
            json.dump(file_metadata, fh, indent=2, ensure_ascii=False)
        print(f"  Metadata written to _metadata.json ({len(file_metadata)} files)")

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

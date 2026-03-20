#!/usr/bin/env python3
# Vibe coded by Claude
"""
unred.py - Extract files from RED (Knowledge Dynamics) archives.

Usage: unred.py <inputFile> <outputDir>

Supports compression schemes 1 (uncompressed) and 11 (LH5 with segmented CRCs).
See redArchive-spec.txt for full format documentation.
"""

import struct
import sys
import os
import io
import re
import datetime

from lhafile.lhafile import lzhlib, LhaInfo


# ---------------------------------------------------------------------------
# CRC-16/IBM-3740 (poly=0x1021, init=0xFFFF, refin=False, refout=False, xorout=0x0000)
# ---------------------------------------------------------------------------

def _build_crc_table():
    table = []
    for i in range(256):
        crc = i << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1
            crc &= 0xFFFF
        table.append(crc)
    return table

_CRC_TABLE = _build_crc_table()


def crc16(data: bytes) -> int:
    """Compute CRC-16/IBM-3740 over *data*."""
    crc = 0xFFFF
    for b in data:
        crc = _CRC_TABLE[((crc >> 8) ^ b) & 0xFF] ^ ((crc << 8) & 0xFFFF)
    return crc


# ---------------------------------------------------------------------------
# Case-insensitive file lookup
# ---------------------------------------------------------------------------

def _build_dir_listing(directory: str) -> dict[str, str]:
    """Return a map of lowercased filenames to actual filenames in *directory*."""
    try:
        return {f.lower(): f for f in os.listdir(directory)}
    except OSError:
        return {}


def find_file_ci(directory: str, name: str,
                 _cache: dict[str, dict[str, str]] = {}) -> str | None:
    """Find *name* in *directory* case-insensitively.

    Returns the full path, or None if not found.
    """
    key = os.path.realpath(directory)
    if key not in _cache:
        _cache[key] = _build_dir_listing(directory)
    actual = _cache[key].get(name.lower())
    if actual is not None:
        return os.path.join(directory, actual)
    return None


# ---------------------------------------------------------------------------
# INSTALL.DAT parser — maps archive entry names to real output filenames
# ---------------------------------------------------------------------------

def parse_install_dat(dat_path: str) -> dict[str, dict[str, str]]:
    """Parse an INSTALL.DAT script and extract the filename mapping.

    Returns a dict keyed by lowercased library filename (e.g.
    ``"timetrek.002"``) whose values are dicts mapping archive entry
    names to real output filenames (e.g. ``{"0": "TIMETREK.GRP", ...}``).

    Handles two known INSTALL.DAT dialects:
      - ``@F <id> @S <size> @O <filename>`` / ``@F <id> @A <filename>``
      - ``@File <archiveName> @Out <path>``
    """
    with open(dat_path, 'r', errors='replace') as f:
        text = f.read()

    result: dict[str, dict[str, str]] = {}
    current_lib: str | None = None
    current_map: dict[str, str] = {}

    for line in text.splitlines():
        stripped = line.strip()

        # @BeginLib TIMETREK.001
        m = re.match(r'@BeginLib\s+(\S+)', stripped, re.IGNORECASE)
        if m:
            current_lib = m.group(1).lower()
            current_map = result.get(current_lib, {})
            continue

        # @EndLib
        if re.match(r'@EndLib\b', stripped, re.IGNORECASE):
            if current_lib is not None:
                result[current_lib] = current_map
            current_lib = None
            continue

        if current_lib is None:
            continue

        # Dialect 1: @F <id> @S <size> @O <filename>  (start of a file)
        m = re.match(
            r'@F\s+(\S+)\s+@S\s+\d+\s+@O\s+(\S+)', stripped, re.IGNORECASE)
        if m:
            current_map[m.group(1)] = m.group(2)
            continue

        # Dialect 1: @F <id> @A <filename>  (append / continuation)
        m = re.match(r'@F\s+(\S+)\s+@A\s+(\S+)', stripped, re.IGNORECASE)
        if m:
            current_map[m.group(1)] = m.group(2)
            continue

        # Dialect 2: @File <archiveName> @Out <path>[\<basename>]
        m = re.match(r'@File\s+(\S+)\s+@Out\s+(\S+)', stripped,
                     re.IGNORECASE)
        if m:
            entry_name = m.group(1)
            out_path = m.group(2)
            # Extract the basename from a path like \@Opt1230Dir\CLMODE.EXE
            out_name = out_path.rsplit('\\', 1)[-1]
            # Only map if the output name differs from the archive name
            # (or always map — it's harmless to map to itself)
            current_map[entry_name] = out_name
            continue

    return result


def load_filename_map(input_path: str) -> dict[str, str]:
    """Try to find and parse INSTALL.DAT next to *input_path*.

    Returns a dict mapping archive entry names to real output filenames
    for the library matching *input_path*, or an empty dict if no
    INSTALL.DAT was found or it doesn't cover this library.
    """
    input_dir = os.path.dirname(os.path.abspath(input_path))
    dat_path = find_file_ci(input_dir, 'install.dat')
    if dat_path is None:
        return {}

    lib_name = os.path.basename(input_path).lower()
    all_libs = parse_install_dat(dat_path)
    mapping = all_libs.get(lib_name, {})
    if mapping:
        print(f'Using filename map from {os.path.basename(dat_path)} '
              f'({len(mapping)} entries for {os.path.basename(input_path)})')
    return mapping


# ---------------------------------------------------------------------------
# DOS date/time helpers
# ---------------------------------------------------------------------------

def dos_datetime(raw: int) -> datetime.datetime:
    """Decode a 32-bit little-endian DOS date/time value.

    Low 16 bits  = time  (2-second resolution)
    High 16 bits = date
    """
    time_val = raw & 0xFFFF
    date_val = (raw >> 16) & 0xFFFF
    sec = (time_val & 0x1F) * 2
    minute = (time_val >> 5) & 0x3F
    hour = (time_val >> 11) & 0x1F
    day = date_val & 0x1F
    month = (date_val >> 5) & 0x0F
    year = ((date_val >> 9) & 0x7F) + 1980
    try:
        return datetime.datetime(year, month, day, hour, minute, sec)
    except ValueError:
        return datetime.datetime(1980, 1, 1)


# ---------------------------------------------------------------------------
# Segment de-framing for scheme 11
# ---------------------------------------------------------------------------

SEGMENT_DATA_SIZE = 4094     # payload bytes per segment
SEGMENT_TOTAL_SIZE = 4096    # payload + 2 byte CRC


def strip_segment_crcs(comp_data: bytes, verify: bool = True,
                       truncated: bool = False) -> bytes:
    """Remove per-segment big-endian CRC-16 checksums from scheme-11 data.

    Each full segment is 4094 bytes of compressed data followed by a 2-byte
    big-endian CRC-16/IBM-3740 of those 4094 bytes.  The last segment may be
    shorter.

    If *truncated* is True, the data was cut off at a volume boundary and
    the trailing partial chunk is raw LH5 data (not a proper segment with
    a CRC suffix).

    Returns the raw LH5 bitstream with all CRCs removed.
    """
    lh5_data = bytearray()
    pos = 0
    seg_num = 0
    while pos < len(comp_data):
        if pos + SEGMENT_TOTAL_SIZE <= len(comp_data):
            seg_payload = comp_data[pos:pos + SEGMENT_DATA_SIZE]
            seg_crc_stored = struct.unpack_from('>H', comp_data, pos + SEGMENT_DATA_SIZE)[0]
            if verify:
                seg_crc_calc = crc16(seg_payload)
                if seg_crc_stored != seg_crc_calc:
                    print(f'  WARNING: segment {seg_num} CRC mismatch: '
                          f'stored=0x{seg_crc_stored:04X} calc=0x{seg_crc_calc:04X}')
            lh5_data.extend(seg_payload)
            pos += SEGMENT_TOTAL_SIZE
        else:
            remaining = len(comp_data) - pos
            if truncated:
                # Volume-boundary cut: all remaining bytes are raw LH5 data.
                lh5_data.extend(comp_data[pos:pos + remaining])
            elif remaining > 2:
                seg_payload = comp_data[pos:pos + remaining - 2]
                seg_crc_stored = struct.unpack_from('>H', comp_data, pos + remaining - 2)[0]
                if verify:
                    seg_crc_calc = crc16(seg_payload)
                    if seg_crc_stored != seg_crc_calc:
                        print(f'  WARNING: segment {seg_num} (last) CRC mismatch: '
                              f'stored=0x{seg_crc_stored:04X} calc=0x{seg_crc_calc:04X}')
                lh5_data.extend(seg_payload)
            elif remaining > 0:
                # Edge case: <=2 bytes remaining (just CRC, no payload)
                pass
            pos += remaining
        seg_num += 1
    return bytes(lh5_data)


# ---------------------------------------------------------------------------
# LH5 decompression (via lhafile's C extension)
# ---------------------------------------------------------------------------

def decompress_lh5(lh5_data: bytes, original_size: int) -> bytes:
    """Decompress raw LH5 bitstream to *original_size* bytes."""
    info = LhaInfo()
    info.compress_type = b'-lh5-'
    info.compress_size = len(lh5_data)
    info.file_size = original_size

    fin = io.BytesIO(lh5_data)
    fout = io.BytesIO()

    session = lzhlib.LZHDecodeSession(fin, fout, info)
    while not session.do_next():
        pass

    fout.seek(0)
    return fout.read()


# ---------------------------------------------------------------------------
# RED archive header parsing
# ---------------------------------------------------------------------------

HEADER_SIZE = 41
SIGNATURE = b'RR'


def parse_entry(data: bytes, offset: int):
    """Parse one RED archive entry header at *offset*.

    Returns a dict with all header fields, or None if there is no valid
    entry at this position.
    """
    if offset + HEADER_SIZE > len(data):
        return None

    sig = data[offset:offset + 2]
    if sig != SIGNATURE:
        return None

    version = data[offset + 2]
    hdr_size = data[offset + 3]
    dos_dt_raw = struct.unpack_from('<I', data, offset + 4)[0]
    comp_size = struct.unpack_from('<I', data, offset + 8)[0]
    decomp_size = struct.unpack_from('<I', data, offset + 12)[0]
    crc_comp = struct.unpack_from('<H', data, offset + 16)[0]
    crc_decomp = struct.unpack_from('<H', data, offset + 18)[0]
    frag_num = struct.unpack_from('<H', data, offset + 20)[0]
    is_last_frag = struct.unpack_from('<H', data, offset + 22)[0]
    comp_scheme = struct.unpack_from('<H', data, offset + 24)[0]
    filename_raw = data[offset + 26:offset + 39]
    hdr_crc_stored = struct.unpack_from('>H', data, offset + 39)[0]

    # Verify header CRC (covers bytes 2..38, stored big-endian at 39..40)
    hdr_crc_calc = crc16(data[offset + 2:offset + 39])
    if hdr_crc_stored != hdr_crc_calc:
        print(f'  WARNING: header CRC mismatch at offset {offset}: '
              f'stored=0x{hdr_crc_stored:04X} calc=0x{hdr_crc_calc:04X}')

    # Decode filename (null-terminated within 13-byte field)
    filename = filename_raw.split(b'\x00')[0].decode('ascii', errors='replace')

    return {
        'offset': offset,
        'version': version,
        'hdr_size': hdr_size,
        'dos_datetime_raw': dos_dt_raw,
        'datetime': dos_datetime(dos_dt_raw),
        'comp_size': comp_size,
        'decomp_size': decomp_size,
        'crc_comp': crc_comp,
        'crc_decomp': crc_decomp,
        'frag_num': frag_num,
        'is_last_frag': is_last_frag,
        'comp_scheme': comp_scheme,
        'filename': filename,
        'filename_raw': filename_raw,
        'hdr_crc': hdr_crc_stored,
        'data_offset': offset + hdr_size,
    }


def iter_entries(data: bytes):
    """Yield all entry dicts from a RED archive.

    In multi-volume archives the last entry's compressed data may extend
    past EOF (the remainder lives in the next volume).  Such entries are
    yielded with ``'truncated': True`` and their ``comp_size`` is clamped
    to what is actually available.  No further entries are yielded after a
    truncated one.
    """
    offset = 0
    while offset < len(data):
        entry = parse_entry(data, offset)
        if entry is None:
            if offset < len(data):
                print(f'WARNING: {len(data) - offset} trailing bytes at offset {offset}')
            break

        data_end = entry['data_offset'] + entry['comp_size']
        if data_end > len(data):
            # Entry's compressed data overflows this volume file.
            entry['truncated'] = True
            entry['comp_size_available'] = len(data) - entry['data_offset']
            yield entry
            break  # no more entries in this volume
        else:
            entry['truncated'] = False
            entry['comp_size_available'] = entry['comp_size']
            yield entry
            offset = data_end


# ---------------------------------------------------------------------------
# Multi-volume helpers
# ---------------------------------------------------------------------------

def next_volume_path(path: str) -> str | None:
    """Return the path of the next volume file, or None if not found.

    Handles numeric extensions like .001 -> .002 -> .003, preserving
    zero-padding width.  Searches case-insensitively.
    """
    base, ext = os.path.splitext(path)
    if not ext:
        return None
    try:
        num = int(ext[1:])
        width = len(ext) - 1          # e.g. '.001' -> width 3
        next_name = f'{os.path.basename(base)}.{num + 1:0{width}d}'
        return find_file_ci(os.path.dirname(os.path.abspath(path)), next_name)
    except (ValueError, IndexError):
        pass
    return None


def gather_split_lh5(input_path: str, data: bytes, entry: dict) -> bytes:
    """Collect and de-segment compressed data for a split file.

    Each volume's fragment is independently segmented (4094+2 CRC).  This
    function strips segment CRCs from each fragment separately, then
    concatenates the raw LH5 bitstream fragments.

    *entry* must be the frag=1 header from the current volume.
    Returns the combined raw LH5 bitstream ready for decompression.
    """
    lh5_chunks = []

    # First fragment (may be truncated at volume boundary)
    avail = min(entry['comp_size'], len(data) - entry['data_offset'])
    frag_data = data[entry['data_offset']:entry['data_offset'] + avail]
    is_truncated = entry.get('truncated', False)
    lh5_chunks.append(strip_segment_crcs(frag_data, truncated=is_truncated))

    if entry['is_last_frag']:
        return b''.join(lh5_chunks)

    # Walk continuation volumes
    vol_path = input_path
    while True:
        vol_path = next_volume_path(vol_path)
        if vol_path is None:
            print(f'  WARNING: next volume not found after '
                  f'{os.path.basename(input_path)}')
            break

        with open(vol_path, 'rb') as f:
            vol_data = f.read()

        cont = parse_entry(vol_data, 0)
        if cont is None or cont['frag_num'] < 2:
            print(f'  WARNING: expected continuation fragment in '
                  f'{os.path.basename(vol_path)}')
            break

        cont_avail = min(cont['comp_size'],
                         len(vol_data) - cont['data_offset'])
        frag_data = vol_data[cont['data_offset']:
                              cont['data_offset'] + cont_avail]
        lh5_chunks.append(strip_segment_crcs(frag_data))
        print(f'           + {os.path.basename(vol_path)} '
              f'fragment {cont["frag_num"]} ({cont_avail} bytes)')

        if cont['is_last_frag']:
            break

    return b''.join(lh5_chunks)


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------

def extract_entry(data: bytes, entry: dict,
                  comp_data: bytes | None = None) -> bytes:
    """Extract (decompress) the file data for one entry.

    If *comp_data* is supplied it is used directly (for split-file
    reassembly); otherwise the payload is read from *data*.
    """
    if comp_data is None:
        comp_data = data[entry['data_offset']:
                         entry['data_offset'] + entry['comp_size']]
    scheme = entry['comp_scheme']

    if scheme == 1:
        # Uncompressed
        result = comp_data
    elif scheme == 11:
        # LH5 compressed with segmented CRCs
        lh5_data = strip_segment_crcs(comp_data)
        result = decompress_lh5(lh5_data, entry['decomp_size'])
    else:
        raise ValueError(f'Unknown compression scheme {scheme} '
                         f'for file "{entry["filename"]}"')

    # Verify decompressed size
    if len(result) != entry['decomp_size']:
        print(f'  WARNING: size mismatch for "{entry["filename"]}": '
              f'got {len(result)}, expected {entry["decomp_size"]}')

    # Verify decompressed data CRC
    crc_calc = crc16(result)
    if crc_calc != entry['crc_decomp']:
        print(f'  WARNING: decompressed CRC mismatch for "{entry["filename"]}": '
              f'calc=0x{crc_calc:04X} stored=0x{entry["crc_decomp"]:04X}')

    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) != 3:
        print(f'Usage: {sys.argv[0]} <inputFile> <outputDir>')
        sys.exit(1)

    input_path = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(input_path):
        print(f'Error: input file not found: {input_path}')
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    with open(input_path, 'rb') as f:
        data = f.read()

    print(f'Reading {input_path} ({len(data)} bytes)')

    name_map = load_filename_map(input_path)

    entry_num = 0
    extracted = 0
    skipped = 0
    for entry in iter_entries(data):
        entry_num += 1
        scheme_str = {1: 'stored', 11: 'LH5'}.get(entry['comp_scheme'],
                                                     f'scheme={entry["comp_scheme"]}')
        real_name = name_map.get(entry['filename'])
        display_name = (f'{entry["filename"]} -> {real_name}'
                        if real_name else entry['filename'])
        out_name = real_name or entry['filename']

        # Classify: continuation fragment (orphan), first fragment
        # (needs gathering), truncated, or complete file.
        is_continuation = entry['frag_num'] >= 2
        is_truncated = entry['truncated']
        is_first_frag = (not is_continuation and not is_truncated
                         and (entry['frag_num'] == 1
                              or not entry['is_last_frag']))
        is_complete = (not is_continuation and not is_truncated
                       and not is_first_frag)

        # Skip orphan continuation fragments (their first fragment lives
        # in a previous volume which should be processed instead).
        if is_continuation:
            skipped += 1
            print(f'  [{entry_num:3d}] {display_name:<25s}  '
                  f'{"":>10s}  '
                  f'{entry["datetime"].strftime("%Y-%m-%d %H:%M:%S")}  '
                  f'{scheme_str}  ** SKIPPED (continuation fragment '
                  f'{entry["frag_num"]})')
            continue

        # Skip entries whose compressed data is truncated at the volume
        # boundary.  The compressed stream cannot be reconstructed from
        # a single volume when the data is split mid-segment.
        if is_truncated:
            skipped += 1
            print(f'  [{entry_num:3d}] {display_name:<25s}  '
                  f'{"":>10s}  '
                  f'{entry["datetime"].strftime("%Y-%m-%d %H:%M:%S")}  '
                  f'{scheme_str}  ** SKIPPED (truncated at volume '
                  f'boundary)')
            continue

        if is_complete:
            # Normal, non-split file — extract directly.
            print(f'  [{entry_num:3d}] {display_name:<25s}  '
                  f'{entry["decomp_size"]:>10d}  '
                  f'{entry["datetime"].strftime("%Y-%m-%d %H:%M:%S")}  '
                  f'{scheme_str}')
            file_data = extract_entry(data, entry)
        else:
            # First fragment of a split file (not truncated) — gather
            # continuation data from subsequent volumes.
            print(f'  [{entry_num:3d}] {display_name:<25s}  '
                  f'{entry["decomp_size"]:>10d}  '
                  f'{entry["datetime"].strftime("%Y-%m-%d %H:%M:%S")}  '
                  f'{scheme_str}  (multi-volume)')
            if entry['comp_scheme'] == 11:
                lh5_data = gather_split_lh5(input_path, data, entry)
                file_data = decompress_lh5(lh5_data, entry['decomp_size'])
                # Verify
                crc_calc = crc16(file_data)
                if len(file_data) != entry['decomp_size']:
                    print(f'  WARNING: size mismatch for '
                          f'"{display_name}": got {len(file_data)}, '
                          f'expected {entry["decomp_size"]}')
                if crc_calc != entry['crc_decomp']:
                    print(f'  WARNING: decompressed CRC mismatch for '
                          f'"{display_name}": calc=0x{crc_calc:04X} '
                          f'stored=0x{entry["crc_decomp"]:04X}')
            elif entry['comp_scheme'] == 1:
                # Stored split file — just concatenate raw data
                chunks = []
                avail = min(entry['comp_size'],
                            len(data) - entry['data_offset'])
                chunks.append(data[entry['data_offset']:
                                    entry['data_offset'] + avail])
                file_data = b''.join(chunks)
            else:
                raise ValueError(f'Unknown compression scheme '
                                 f'{entry["comp_scheme"]}')

        # Write to output directory — fall back to archive name on collision
        out_path = os.path.join(output_dir, out_name)
        if os.path.exists(out_path) and out_name != entry['filename']:
            print(f'           collision: {out_name} already exists, '
                  f'using archive name {entry["filename"]}')
            out_name = entry['filename']
            out_path = os.path.join(output_dir, out_name)
        with open(out_path, 'wb') as f:
            f.write(file_data)

        # Set file modification time from DOS datetime
        try:
            ts = entry['datetime'].timestamp()
            os.utime(out_path, (ts, ts))
        except (OSError, OverflowError, ValueError):
            pass

        extracted += 1

    print(f'\nExtracted {extracted} entries to {output_dir}/'
          + (f' ({skipped} split entries skipped)' if skipped else ''))


if __name__ == '__main__':
    main()

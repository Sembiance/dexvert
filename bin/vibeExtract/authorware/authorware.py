#!/usr/bin/env python3
# Vibe coded by Codex
"""
Authorware Packaged/Library File Extractor (.app/.apr/.apw/.asw/.aas/.a3m/.a3w/.a4p/.a5p/.a6p/.a7p/.a4r/.a5r/.a6r/.a7r/.exe)

Extracts images, text, scripts, and raw data from Macromedia Authorware
packaged files (ACRS), library files (PCRS), v3 files (WCRS/A3M),
and compiled Windows PE executables with appended PCRS data (including
payloads whose EXE wrappers have already been stripped).

Usage: python3 authorware.py <inputFile> <outputDir> [--report] [--deep]
"""

import sys
import os
import struct
import zlib
import re
import hashlib
import math
import json
import argparse

import authorware_pig
import authorware_cursor
import authorware_animation

ICON_TYPE_NAMES = {
    0x01: "FileProperties",
    0x02: "IconNames",
    0x03: "ColorPalette",
    0x04: "Calculation",
    0x05: "Script",
    0x06: "RawData",
    0x07: "LibraryPaths",
    0x09: "NamedElements",
    0x0A: "Variables",
    0x0B: "PropertyDescriptions",
    0x0C: "Interaction",
    0x0D: "Conditional",
    0x0E: "FunctionDoc",
    0x0F: "ConditionalBranch",
    0x10: "Target",
    0x11: "Motion",
    0x13: "ButtonResponse",
    0x14: "HotSpotResponse",
    0x15: "Navigate",
    0x16: "Framework",
    0x17: "Decision",
    0x18: "CursorResource",
    0x19: "FontTable",
    0x1A: "CursorData",
    0x1B: "TextInput",
    0x1C: "LookupTable",
    0x1D: "LibraryIndex",
    0x1E: "LibraryLayout",
    0x1F: "Erase",
    0x21: "MovieReference",
    0x22: "InteractionResponse",
    0x23: "LibraryRefs",
    0x24: "Expression",
    0x25: "Display",
    0x26: "MapGroup",
    0x27: "Wait",
    0x28: "RichText",
    0x29: "Reference",
    0x33: "AnimationPath",
    0x34: "PIG",
    0x35: "DIB",
    0x36: "SoundHeader",
    0x37: "SoundData",
    0x38: "AnimationFrames",
    0x3A: "DisplayText",
    0x3B: "EmbeddedMedia",
    0x3C: "StreamingAudio",
    0x39: "MediaLink",
    0x3E: "BMP",
    0xFFFD: "PluginPIG",
}

# Types that contain meaningful text to extract
TEXT_TYPES = {0x02, 0x05, 0x07, 0x09, 0x0A, 0x0B, 0x0E, 0x23, 0x24, 0x28, 0x3A}


def write_output(output_dir, name, content):
    """Write a new file, never replacing another entry or an existing output."""
    name = os.path.basename(name.replace('\\', '/'))
    stem, extension = os.path.splitext(name)
    payload = content.encode('utf-8') if isinstance(content, str) else content
    suffix = 1
    while True:
        candidate = name if suffix == 1 else f'{stem}_{suffix}{extension}'
        try:
            with open(os.path.join(output_dir, candidate), 'xb') as output:
                output.write(payload)
            return candidate
        except FileExistsError:
            suffix += 1


def read_header(data):
    """Parse the 64-byte file header."""
    if len(data) < 64:
        raise ValueError("File too small for header")
    if data[:4] not in (b'ACRS', b'PCRS', b'WCRS', b'WPCR', b'WPLI'):
        raise ValueError(f"Invalid magic: {data[:4]!r} (expected b'ACRS', b'PCRS', b'WCRS', b'WPCR', or b'WPLI')")
    if data[4:8] != bytes(byte ^ 0xFF for byte in data[:4]):
        raise ValueError("Invalid secondary magic")

    hdr = {}
    hdr['magic'] = data[:4].decode('ascii')
    # Detect big-endian: if LE format_version > 255, file is big-endian (e.g. a3m Mac files)
    le_ver = struct.unpack_from('<I', data, 0x20)[0]
    endian = '>' if le_ver > 255 else '<'
    hdr['big_endian'] = (endian == '>')
    hdr['encoder_version'] = struct.unpack_from(f'{endian}I', data, 0x08)[0]
    hdr['flags'] = struct.unpack_from(f'{endian}i', data, 0x0C)[0]
    hdr['format_version'] = struct.unpack_from(f'{endian}I', data, 0x20)[0]
    hdr['file_size'] = struct.unpack_from(f'{endian}I', data, 0x24)[0]
    hdr['uncompressed_size'] = struct.unpack_from(f'{endian}I', data, 0x28)[0]
    hdr['table_total_size'] = struct.unpack_from(f'{endian}I', data, 0x2C)[0]
    hdr['entry_count'] = struct.unpack_from(f'{endian}I', data, 0x30)[0]
    hdr['table_offset'] = struct.unpack_from(f'{endian}I', data, 0x34)[0]
    hdr['table_size'] = struct.unpack_from(f'{endian}I', data, 0x38)[0]
    hdr['data_end'] = struct.unpack_from(f'{endian}I', data, 0x3C)[0]

    # Detect EXE-appended format: PCRS data originally appended to an EXE file.
    # The EXE stub has been stripped but header offsets still reference it.
    # Distinguished from segment files (which also have file_size > len(data))
    # by table_offset pointing beyond 0x6A (segments always have table_offset=0x6A).
    hdr['base_offset'] = 0
    if (hdr['magic'] == 'PCRS' and hdr['file_size'] > len(data)
            and hdr['table_offset'] != 0x6A
            and hdr['table_offset'] - (hdr['file_size'] - len(data)) == 0x6A):
        hdr['base_offset'] = hdr['file_size'] - len(data)
        hdr['table_offset'] = 0x6A
        hdr['file_size'] = len(data)

    return hdr


def read_entries(data, hdr):
    """Parse the entry table (ACRS 30-byte records)."""
    entries = []
    table_off = hdr['table_offset']
    base = hdr.get('base_offset', 0)
    for i in range(hdr['entry_count']):
        off = table_off + i * 30
        if off + 30 > len(data):
            break
        entry = {}
        entry['id'] = struct.unpack_from('<H', data, off)[0]
        entry['icon_type'] = struct.unpack_from('<H', data, off + 4)[0]
        entry['flags'] = struct.unpack_from('<H', data, off + 6)[0]
        entry['comp_size'] = struct.unpack_from('<I', data, off + 8)[0]
        entry['decomp_size'] = struct.unpack_from('<I', data, off + 12)[0]
        entry['storage_type'] = struct.unpack_from('<H', data, off + 16)[0]
        entry['flags2'] = struct.unpack_from('<H', data, off + 18)[0]
        entry['data_offset'] = struct.unpack_from('<I', data, off + 24)[0] - base
        entry['parent'] = struct.unpack_from('<h', data, off + 28)[0]
        entries.append(entry)
    return entries


def read_entries_pcrs(data, hdr):
    """Parse the entry table for PCRS library files (10-byte records).

    PCRS entries use a compact format without entry IDs or parent fields.
    Compressed sizes are derived from gaps between consecutive data offsets.
    """
    entries = []
    table_off = hdr['table_offset']
    base = hdr.get('base_offset', 0)
    for i in range(hdr['entry_count']):
        off = table_off + i * 10
        if off + 10 > len(data):
            break
        entry = {}
        entry['data_offset'] = struct.unpack_from('<I', data, off)[0] - base
        entry['decomp_size'] = struct.unpack_from('<I', data, off + 4)[0]
        entry['icon_type'] = data[off + 8]
        # PCRS uses 2=raw, 3=zlib; normalize to ACRS convention (1=raw, 2=zlib)
        entry['storage_type'] = data[off + 9] - 1
        entry['id'] = i + 1  # auto-assign sequential IDs
        entry['flags'] = 0
        entry['flags2'] = 0
        entry['parent'] = 0
        entries.append(entry)

    # Compute comp_size from gaps between sorted data offsets
    by_offset = sorted(range(len(entries)), key=lambda j: entries[j]['data_offset'])
    for k, idx in enumerate(by_offset):
        if entries[idx]['storage_type'] == 1:
            # Uncompressed (normalized): comp_size = decomp_size
            entries[idx]['comp_size'] = entries[idx]['decomp_size']
        elif k + 1 < len(by_offset):
            entries[idx]['comp_size'] = entries[by_offset[k + 1]]['data_offset'] - entries[idx]['data_offset']
        else:
            # Last entry: use remaining file data
            entries[idx]['comp_size'] = len(data) - entries[idx]['data_offset']

    return entries


def pe_overlay_offset(data):
    """Find the end of a PE's on-disk headers and sections, without executing it."""
    if len(data) < 64 or data[:2] != b'MZ':
        raise ValueError("Truncated or invalid DOS executable header")
    pe = struct.unpack_from('<I', data, 0x3C)[0]
    if pe < 64 or pe + 24 > len(data):
        raise ValueError("Truncated or invalid PE header offset")
    if data[pe:pe + 4] != b'PE\x00\x00':
        raise ValueError("Unsupported executable header (expected Windows PE)")

    section_count = struct.unpack_from('<H', data, pe + 6)[0]
    optional_size = struct.unpack_from('<H', data, pe + 20)[0]
    optional = pe + 24
    section_table = optional + optional_size
    section_table_end = section_table + section_count * 40
    if not section_count or optional_size < 64 or section_table_end > len(data):
        raise ValueError("Truncated or invalid PE section table")
    if struct.unpack_from('<H', data, optional)[0] not in (0x10B, 0x20B):
        raise ValueError("Unsupported PE optional header")

    # SizeOfHeaders has the same offset in PE32 and PE32+.
    overlay = struct.unpack_from('<I', data, optional + 60)[0]
    if not section_table_end <= overlay <= len(data):
        raise ValueError("Invalid PE header size")
    for i in range(section_count):
        section = section_table + i * 40
        size, offset = struct.unpack_from('<II', data, section + 16)
        if size:
            if offset < section_table_end or offset + size > len(data):
                raise ValueError("PE section data is outside the file")
            overlay = max(overlay, offset + size)
    return overlay


def load_authorware(data):
    """Return an Authorware byte stream and its normalized header.

    Compiled PE runtimes append table-first PCRS data with absolute EXE
    offsets. Search only the overlay: runtime code contains magic strings
    too. Bound the payload by its declared file end before rebasing, so
    trailing executable data does not change the inferred base offset.
    """
    if data[:2] != b'MZ':
        return data, read_header(data)

    search_from = pe_overlay_offset(data)
    signature = b'PCRS\xaf\xbc\xad\xac'
    while True:
        offset = data.find(signature, search_from)
        if offset < 0:
            break
        search_from = offset + len(signature)
        if offset + 64 > len(data):
            continue

        version, file_end = struct.unpack_from('<II', data, offset + 0x20)
        table_total, count, table_offset = struct.unpack_from('<III', data, offset + 0x2C)
        if (version not in (5, 6) or not count
                or table_offset != offset + 0x6A
                or not table_offset <= file_end <= len(data)
                or table_total < count * 10
                or table_offset + table_total > file_end):
            continue

        payload = data[offset:file_end]
        hdr = read_header(payload)
        if count * 30 > table_total:
            entries = read_entries_pcrs(payload, hdr)
        else:
            entries = read_entries(payload, hdr)

        # Reject signature lookalikes with invalid entry tables, rather than
        # treating arbitrary overlay bytes as an Authorware project.
        data_start = hdr['table_offset'] + table_total
        valid = True
        for entry in entries:
            if entry['comp_size'] == 0 and entry['decomp_size'] == 0:
                continue
            if (entry['storage_type'] not in (1, 2)
                    or entry['comp_size'] < 0
                    or entry['data_offset'] < data_start
                    or entry['data_offset'] + entry['comp_size'] > len(payload)):
                valid = False
                break
        if valid:
            hdr['exe_offset'] = offset
            return payload, hdr

    raise ValueError("No valid appended Authorware PCRS payload found in PE executable")


def detect_icon_type(entry_data, entry_size=0):
    """Auto-detect icon type from data signatures (for WCRS files with no type field)."""
    if not entry_data or len(entry_data) < 4:
        return 0x06  # RawData
    if len(entry_data) >= 6 and entry_data[2:6] == b'PIG\x00':
        return 0x34  # PIG
    if entry_data[:2] == b'BM':
        return 0x3E  # BMP
    if entry_data[:4] == b'FORM':
        return 0x3C  # StreamingAudio (AIFF)
    if entry_data[:4] == b'RIFF':
        return 0x3C  # StreamingAudio (WAV)
    if (not entry_size or entry_size == len(entry_data)) and parse_sound_header(entry_data):
        return 0x36  # PCM metadata, not inferred from sample byte averages
    # Check for BITMAPINFOHEADER in both LE and BE
    for endian in ('<', '>'):
        hdr_size = struct.unpack_from(f'{endian}I', entry_data, 0)[0]
        if hdr_size == 40 and len(entry_data) >= 40:
            w = struct.unpack_from(f'{endian}i', entry_data, 4)[0]
            h = abs(struct.unpack_from(f'{endian}i', entry_data, 8)[0])
            planes = struct.unpack_from(f'{endian}H', entry_data, 12)[0]
            bpp = struct.unpack_from(f'{endian}H', entry_data, 14)[0]
            if 0 < w < 10000 and 0 < h < 10000 and planes == 1 and bpp in (1, 4, 8, 16, 24, 32):
                return 0x35  # DIB
    return 0x06  # RawData


def read_entries_wcrs(data, hdr):
    """Parse the entry table for WCRS/A3M files (16-byte records, no icon type).

    WCRS (Authorware 3.x Windows) and A3M (Authorware 3.x Mac) entries
    have no icon type field. Types are auto-detected from data signatures.
    A3M uses big-endian byte order.
    """
    endian = '>' if hdr.get('big_endian') else '<'
    entries = []
    table_off = hdr['table_offset']
    # Star's -5 variant leaves the ID fields unused. Like its offset-only
    # -4 variant, references address one-based table positions. WCRS can
    # share the flag value but stores real IDs and must not use this rule.
    ordinal_ids = (hdr['magic'] in ('WPCR', 'WPLI')
                   and hdr['flags'] & 0xFFFFFFFF == 0xFFFFFFFB)
    for i in range(hdr['entry_count']):
        off = table_off + i * 16
        if off + 16 > len(data):
            break
        entry = {}
        entry['id'] = i + 1 if ordinal_ids else struct.unpack_from(f'{endian}H', data, off)[0]
        entry['storage_type'] = struct.unpack_from(f'{endian}H', data, off + 2)[0]
        entry['data_offset'] = struct.unpack_from(f'{endian}I', data, off + 8)[0]
        entry['decomp_size'] = struct.unpack_from(f'{endian}I', data, off + 12)[0]
        entry['comp_size'] = entry['decomp_size']  # WCRS is always uncompressed
        entry['icon_type'] = 0  # unknown, will be detected from data
        entry['flags'] = 0
        entry['flags2'] = 0
        entry['parent'] = 0
        # Normalize storage type to 1 (raw) for all WCRS entries
        entry['storage_type'] = 1
        entries.append(entry)

    # Auto-detect icon types from data signatures
    for entry in entries:
        if entry['comp_size'] == 0 and entry['decomp_size'] == 0:
            continue
        off = entry['data_offset']
        sz = entry['decomp_size']
        if off + sz <= len(data):
            entry['icon_type'] = detect_icon_type(data[off:off + min(sz, 64)], sz)

    return entries


def read_entries_wcrs_v2(data, hdr):
    """Parse the entry table for WCRS v2 files (10-byte records at end of file).

    Authorware 2.x Windows packaged files use a compact entry format:
    id(2) + data_offset(4) + decomp_size(4) = 10 bytes per entry.
    The entry table is located at file_size - table_total_size.
    No icon type or storage type fields; types are auto-detected.
    """
    entries = []
    table_off = hdr['file_size'] - hdr['table_total_size']
    for i in range(hdr['entry_count']):
        off = table_off + i * 10
        if off + 10 > len(data):
            break
        entry = {}
        entry['id'] = struct.unpack_from('<H', data, off)[0]
        entry['data_offset'] = struct.unpack_from('<I', data, off + 2)[0]
        entry['decomp_size'] = struct.unpack_from('<I', data, off + 6)[0]
        entry['comp_size'] = entry['decomp_size']  # v2 is always uncompressed
        entry['icon_type'] = 0  # will be auto-detected
        entry['storage_type'] = 1  # always raw
        entry['flags'] = 0
        entry['flags2'] = 0
        entry['parent'] = 0
        entries.append(entry)

    # Auto-detect icon types from data signatures
    for entry in entries:
        if entry['comp_size'] == 0 and entry['decomp_size'] == 0:
            continue
        off = entry['data_offset']
        sz = entry['decomp_size']
        if off + sz <= len(data):
            entry['icon_type'] = detect_icon_type(data[off:off + min(sz, 64)], sz)

    return entries


def read_entries_wpcr(data, hdr):
    """Parse the entry table for WPCR files (4-byte offset-only records).

    Authorware 1.x packaged files with flags 0xFFFFFFFC use a minimal
    entry format: just a list of uint32 data offsets. Entry sizes are
    computed from gaps between consecutive offsets. The value at position
    entry_count in the offset array is the end-of-data marker (= file_size).
    No entry IDs, icon types, or storage type fields exist.
    """
    entries = []
    table_off = hdr['table_offset']
    ec = hdr['entry_count']

    # Read ec data offsets
    offsets = []
    for i in range(ec):
        off = table_off + i * 4
        if off + 4 > len(data):
            break
        offsets.append(struct.unpack_from('<I', data, off)[0])

    # Read end marker (value at position ec)
    end_off = table_off + ec * 4
    if end_off + 4 <= len(data):
        end_marker = struct.unpack_from('<I', data, end_off)[0]
    else:
        end_marker = hdr['file_size']

    # Compute sizes from gaps
    for i, doff in enumerate(offsets):
        next_off = offsets[i + 1] if i + 1 < len(offsets) else end_marker
        dsz = next_off - doff
        entry = {}
        entry['id'] = i + 1  # auto-assign sequential IDs
        entry['data_offset'] = doff
        entry['decomp_size'] = dsz
        entry['comp_size'] = dsz
        entry['icon_type'] = 0  # will be auto-detected
        entry['storage_type'] = 1  # always raw
        entry['flags'] = 0
        entry['flags2'] = 0
        entry['parent'] = 0
        entries.append(entry)

    # Auto-detect icon types from data signatures
    for entry in entries:
        if entry['comp_size'] == 0 and entry['decomp_size'] == 0:
            continue
        off = entry['data_offset']
        sz = entry['decomp_size']
        if off + sz <= len(data):
            entry['icon_type'] = detect_icon_type(data[off:off + min(sz, 64)], sz)

    return entries


def decompress_entry(data, entry):
    """Decompress an entry's data."""
    off = entry['data_offset']
    comp_size = entry['comp_size']

    if comp_size == 0 and entry['decomp_size'] == 0:
        return None  # empty placeholder entry

    if off < 0 or comp_size < 0 or entry['decomp_size'] < 0 or off + comp_size > len(data):
        return None

    if entry['storage_type'] == 1:
        return data[off:off + comp_size]
    elif entry['storage_type'] == 2:
        try:
            obj = zlib.decompressobj()
            result = obj.decompress(data[off:off + comp_size], entry['decomp_size'] + 1)
            if not obj.eof or len(result) != entry['decomp_size']:
                return None
            return result
        except zlib.error:
            return None
    return None


def dib_endian(dib_data):
    """Detect if a DIB BITMAPINFOHEADER is big-endian or little-endian.

    Returns '>' for big-endian, '<' for little-endian.
    """
    if len(dib_data) < 40:
        return '<'
    be_hdr = struct.unpack_from('>I', dib_data, 0)[0]
    le_hdr = struct.unpack_from('<I', dib_data, 0)[0]
    if be_hdr == 40 and le_hdr != 40:
        return '>'
    return '<'


def swap_dib_to_le(dib_data):
    """Convert a big-endian BITMAPINFOHEADER to little-endian.

    Swaps the 40-byte header fields. Palette (RGBQUAD) and pixel data
    for <= 8bpp are byte-oriented and don't need swapping.
    """
    if len(dib_data) < 40:
        return dib_data
    # Read all 40-byte header fields in BE
    fields = struct.unpack_from('>IiiHHIIiiII', dib_data, 0)
    # Repack in LE
    le_header = struct.pack('<IiiHHIIiiII', *fields)
    return le_header + dib_data[40:]


def dib_fields(data):
    """Validate a bitmap header before using its sizes or interpreting pixels."""
    if len(data) < 40:
        return None
    fields = struct.unpack_from(dib_endian(data) + 'IiiHHIIiiII', data)
    size, width, height, planes, bpp, compression, image_size, _, _, colors, _ = fields
    if (size not in (40, 52, 56, 108, 124) or size > len(data)
            or not 0 < width < 10000 or not 0 < abs(height) < 10000
            or planes != 1 or bpp not in (1, 4, 8, 16, 24, 32)
            or (bpp <= 8 and colors > 1 << bpp)
            or compression not in (0, 1, 2, 3, 4, 6)
            or (compression == 1 and bpp != 8)
            or (compression == 2 and bpp != 4)
            or (compression == 4 and bpp != 1)
            or (compression in (3, 6) and bpp not in (16, 32))):
        return None
    return fields


def decode_bitmap_rle(data, width, height, bpp):
    """Decode RLE8, RLE4, or Authorware's byte-run encoded 1-bit bitmap.

    The 1-bit variant uses RLE8 packets over packed bytes, with compression
    code 4. It is not the JPEG data denoted by code 4 in modern BMP files.
    """
    stride = ((width * bpp + 31) // 32) * 4
    if stride * height > 256 * 1024 * 1024:
        return None
    pixels = bytearray(stride * height)
    capacity = stride if bpp in (1, 8) else stride * 2
    x = y = offset = 0

    def put(values):
        nonlocal x
        if y >= height or x + len(values) > capacity:
            return False
        if bpp in (1, 8):
            start = y * stride + x
            pixels[start:start + len(values)] = bytes(values)
        else:
            for index, value in enumerate(values, x):
                byte = y * stride + index // 2
                if index & 1:
                    pixels[byte] = (pixels[byte] & 0xF0) | value
                else:
                    pixels[byte] = (pixels[byte] & 0x0F) | value << 4
        x += len(values)
        return True

    while offset + 2 <= len(data):
        count, value = data[offset:offset + 2]
        offset += 2
        if count:
            values = ([value >> 4, value & 15] * ((count + 1) // 2))[:count] if bpp == 4 else [value] * count
            if not put(values):
                return None
        elif value == 0:
            x = 0
            y += 1
            if y == height:
                return bytes(pixels)
        elif value == 1:
            return bytes(pixels)
        elif value == 2:
            if offset + 2 > len(data):
                return None
            dx, dy = data[offset:offset + 2]
            offset += 2
            x += dx
            y += dy
            if x > capacity or y >= height:
                return None
        else:
            length = (value + 1) // 2 if bpp == 4 else value
            padded = (length + 1) & ~1
            if offset + padded > len(data):
                return None
            literal = data[offset:offset + length]
            values = [((literal[i // 2] >> 4) if i % 2 == 0 else (literal[i // 2] & 15))
                      for i in range(value)] if bpp == 4 else literal
            if not put(values):
                return None
            offset += padded
    required = (width + 7) // 8 if bpp == 1 else width
    if y == height - 1 and x >= required:
        return bytes(pixels)
    return None


def normalize_dib(dib_data, shared_palette=None, embedded_palette=None):
    """Build a complete, validated DIB, supplying an external palette if needed."""
    fields = dib_fields(dib_data)
    if fields is None:
        return None
    size, width, height, planes, bpp, compression, image_size, xpm, ypm, colors, important = fields
    if dib_endian(dib_data) == '>':
        dib_data = swap_dib_to_le(dib_data)
    stride = ((width * bpp + 31) // 32) * 4
    pixel_size = stride * abs(height)
    if pixel_size > 256 * 1024 * 1024:
        return None
    color_count = (colors or (1 << bpp)) if bpp <= 8 else 0
    palette_size = color_count * 4
    mask_size = (16 if compression == 6 else 12) if compression in (3, 6) and size == 40 else 0
    header_end = size + mask_size
    if len(dib_data) < header_end:
        return None
    needed_pixels = image_size if compression in (1, 2, 4) else pixel_size
    external = shared_palette is not None and len(shared_palette) >= palette_size and palette_size > 0
    if embedded_palette is None:
        embedded_palette = not (external and len(dib_data) < header_end + palette_size + needed_pixels)
    if palette_size and not embedded_palette:
        if not external:
            return None
        palette = shared_palette[:palette_size]
        start = header_end
    else:
        palette = dib_data[header_end:header_end + palette_size]
        if len(palette) != palette_size:
            return None
        start = header_end + palette_size
    # A palette-less RLE stream can accidentally decode when its first bytes
    # are mistaken for a palette. Require room for the declared pixel stream.
    if start + needed_pixels > len(dib_data):
        return None
    if compression in (1, 2, 4):
        stream = dib_data[start:start + image_size] if image_size else dib_data[start:]
        pixels = decode_bitmap_rle(stream, width, abs(height), bpp)
        if pixels is None:
            return None
        header = bytearray(dib_data[:header_end])
        struct.pack_into('<II', header, 16, 0, len(pixels))
        return bytes(header) + palette + pixels
    if start + pixel_size > len(dib_data):
        return None
    # Preserve existing valid data and metadata, including any trailing content.
    return dib_data[:header_end] + palette + dib_data[start:]


def make_bmp_from_dib(dib_data, shared_palette=None):
    """Create a BMP only when the palette and pixel data can be recovered."""
    dib_data = normalize_dib(dib_data, shared_palette)
    if dib_data is None:
        return None
    fields = dib_fields(dib_data)
    size, _, _, _, bpp, compression, _, _, _, colors, _ = fields
    palette_size = ((colors or (1 << bpp)) * 4) if bpp <= 8 else 0
    masks = (16 if compression == 6 else 12) if compression in (3, 6) and size == 40 else 0
    return struct.pack('<2sIHHI', b'BM', 14 + len(dib_data), 0, 0,
                       14 + size + palette_size + masks) + dib_data


def extract_pig_palette(pig_data, before=None, colors=None, minimum=False):
    """Read a PIG palette record (tag 0x56), at its actual variable offset.

    A record contains tag:uint16, total_size:uint32, count:uint32, followed
    by count RGBQUADs. WIN and MAC containers can both hold these records.
    """
    if pig_data[2:6] != b'PIG\x00':
        return None
    end = len(pig_data) if before is None else min(before, len(pig_data))
    found = None
    for endian, marker in (('<', b'\x56\x00'), ('>', b'\x00\x56')):
        offset = 14
        while True:
            offset = pig_data.find(marker, offset, end)
            if offset < 0:
                break
            if offset + 10 <= end:
                length, count = struct.unpack_from(endian + 'II', pig_data, offset + 2)
                if (0 < count <= 256 and length == 10 + count * 4
                        and offset + length <= end
                        and (colors is None or colors == count or (minimum and count >= colors))):
                    palette = pig_data[offset + 10:offset + length]
                    if all(palette[i] == 0 for i in range(3, len(palette), 4)):
                        if found is None or offset > found[0]:
                            found = (offset, palette)
            offset += 2
    return found[1] if found else None


def find_best_dib_in_pig(pig_data, *, with_offset=False):
    """Find a valid DIB, optionally returning its original PIG byte offset."""
    candidates = []
    offsets = sorted({match.start() for pattern in (b'\x28\x00\x00\x00', b'\x00\x00\x00\x28')
                      for match in re.finditer(re.escape(pattern), pig_data)})
    for offset in offsets:
        fields = dib_fields(pig_data[offset:])
        if fields is None:
            continue
        size, w, h, planes, bpp, compression, image_size, _, _, colors, _ = fields
        end = len(pig_data)
        # Bitmap record 0x65 has a 58-byte prefix before the DIB header.
        record = offset - 58
        if record >= 14:
            for endian, marker in (('<', b'\x65\x00'), ('>', b'\x00\x65')):
                if pig_data[record:record + 2] == marker:
                    length = struct.unpack_from(endian + 'I', pig_data, record + 2)[0]
                    if offset + size <= record + length <= len(pig_data):
                        end = record + length
        count = (colors or (1 << bpp)) if bpp <= 8 else 0
        palette = extract_pig_palette(pig_data, before=offset, colors=count, minimum=bpp == 8) if count else None
        embedded = False if palette is not None and bpp in (4, 8) else None
        dib = normalize_dib(pig_data[offset:end], palette, embedded)
        # Some legacy 0x65 lengths exclude the embedded RGBQUAD table.
        if dib is None and palette is None and count and end + count * 4 <= len(pig_data):
            dib = normalize_dib(pig_data[offset:end + count * 4])
        if dib is not None:
            candidates.append((bpp, offset, dib))
    if not candidates:
        return None
    _, offset, dib = max(candidates, key=lambda item: item[0])
    return (offset, dib) if with_offset else dib


def extract_pig_dimensions(pig_data):
    """Compute width/height from the signed bounding rectangle in a PIG."""
    if len(pig_data) < 0x22:
        return None, None
    if pig_data[2:5] != b'PIG':
        return None, None
    platform = pig_data[6:9]
    if platform in (b'WIN', b'MAC'):
        endian = '>' if struct.unpack_from('<I', pig_data, 14)[0] > 65535 else '<'
        left, top, right, bottom = authorware_pig.rectangle(pig_data, 0x1A, endian)
        w, h = right - left, bottom - top
        if 0 < w < 10000 and 0 < h < 10000:
            return w, h
    return None, None


def extract_text_from_entry(entry_data, icon_type):
    """Extract readable text from an entry's data."""
    if icon_type == 0x28:
        # Rich text: font table + text content
        if len(entry_data) < 10:
            return None
        text_offset = struct.unpack_from('<H', entry_data, 8)[0]
        if text_offset >= len(entry_data):
            text_offset = 10

        # Extract font names from header area
        font_section = entry_data[10:text_offset]
        fonts = [s.decode('ascii', errors='replace') for s in font_section.split(b'\x00') if s and all(32 <= b < 127 for b in s)]

        # Extract text from text area
        text_section = entry_data[text_offset:]
        texts = extract_printable_strings(text_section, min_len=3)

        lines = []
        if fonts:
            lines.append("Fonts: " + ", ".join(fonts))
            lines.append("")
        if texts:
            lines.append("Text content:")
            for t in texts:
                lines.append("  " + t)
        return "\n".join(lines) if lines else None

    elif icon_type in (0x02, 0x07, 0x23):
        # Null-separated name/path lists
        parts = entry_data.split(b'\x00')
        strings = []
        for p in parts:
            try:
                s = p.decode('ascii')
                if s and all(32 <= ord(c) < 127 for c in s):
                    strings.append(s)
            except (UnicodeDecodeError, ValueError):
                pass
        return "\n".join(strings) if strings else None

    elif icon_type in (0x0A, 0x0B):
        # Variable/property names - null-separated
        parts = entry_data.split(b'\x00')
        strings = []
        for p in parts:
            try:
                s = p.decode('ascii')
                if s and len(s) >= 2 and all(32 <= ord(c) < 127 for c in s):
                    strings.append(s)
            except (UnicodeDecodeError, ValueError):
                pass
        return "\n".join(strings) if strings else None

    elif icon_type in (0x05, 0x09, 0x0E, 0x24, 0x3A):
        # Script/expression
        strings = extract_printable_strings(entry_data, min_len=3)
        return "\n".join(strings) if strings else None

    return None


def extract_printable_strings(data, min_len=3):
    """Extract sequences of printable ASCII characters from binary data."""
    strings = []
    cur = []
    for b in data:
        if 32 <= b < 127:
            cur.append(chr(b))
        else:
            if len(cur) >= min_len:
                strings.append(''.join(cur))
            cur = []
    if len(cur) >= min_len:
        strings.append(''.join(cur))
    return strings


def valid_gif_codes(data, code_size, expected):
    """Validate GIF LZW codes without allocating the decoded image."""
    if not 2 <= code_size <= 8:
        return False
    clear = 1 << code_size
    lengths = [1] * clear + [0, 0]
    bits = code_size + 1
    bit = count = previous = 0
    while bit + bits <= len(data) * 8:
        start = bit // 8
        code = int.from_bytes(data[start:start + 3], 'little') >> (bit & 7) & ((1 << bits) - 1)
        bit += bits
        if code == clear:
            lengths = [1] * clear + [0, 0]
            bits = code_size + 1
            previous = 0
            continue
        if code == clear + 1:
            return count == expected
        if code < len(lengths):
            length = lengths[code]
        elif code == len(lengths) and previous:
            length = previous + 1
        else:
            return False
        count += length
        if count > expected:
            return False
        if previous and len(lengths) < 4096:
            lengths.append(previous + 1)
            if len(lengths) == 1 << bits and bits < 12:
                bits += 1
        previous = length
    return False


def embedded_image_end(data, offset, kind):
    """Find a complete image, rejecting signature fragments in PIG metadata."""
    if kind == 'png':
        pos = offset + 8
        first = True
        saw_data = False
        while pos + 12 <= len(data):
            length = struct.unpack_from('>I', data, pos)[0]
            tag = data[pos + 4:pos + 8]
            end = pos + 12 + length
            if end > len(data) or (first and (tag != b'IHDR' or length != 13)):
                return None
            checksum = struct.unpack_from('>I', data, pos + 8 + length)[0]
            if zlib.crc32(data[pos + 4:pos + 8 + length]) & 0xFFFFFFFF != checksum:
                return None
            saw_data |= tag == b'IDAT'
            if tag == b'IEND':
                return end if length == 0 and saw_data else None
            first = False
            pos = end
        return None
    if kind == 'gif':
        if offset + 13 > len(data):
            return None
        packed = data[offset + 10]
        pos = offset + 13 + (3 * (1 << ((packed & 7) + 1)) if packed & 0x80 else 0)
        frames = 0
        while pos < len(data):
            tag = data[pos]
            pos += 1
            if tag == 0x3B:
                return pos if frames else None
            if tag == 0x21:
                if pos >= len(data):
                    return None
                pos += 1  # extension label
                image_size = None
            elif tag == 0x2C:
                if pos + 10 > len(data):
                    return None
                width, height = struct.unpack_from('<HH', data, pos + 4)
                packed = data[pos + 8]
                pos += 9 + (3 * (1 << ((packed & 7) + 1)) if packed & 0x80 else 0)
                if pos >= len(data) or width == 0 or height == 0:
                    return None
                code_size = data[pos]
                pos += 1
                image_size = width * height
            else:
                return None
            blocks = []
            while pos < len(data):
                size = data[pos]
                pos += 1
                if not size:
                    break
                if pos + size > len(data):
                    return None
                blocks.append(data[pos:pos + size])
                pos += size
            else:
                return None
            if image_size is not None:
                if not valid_gif_codes(b''.join(blocks), code_size, image_size):
                    return None
                frames += 1
        return None
    if kind == 'jpeg':
        pos = offset + 2
        saw_frame = saw_scan = False
        while pos < len(data):
            if data[pos] != 0xFF:
                return None
            while pos < len(data) and data[pos] == 0xFF:
                pos += 1
            if pos >= len(data):
                return None
            marker = data[pos]
            pos += 1
            if marker == 0xD9:
                return pos if saw_frame and saw_scan else None
            if marker in (0, 0xD8) or pos + 2 > len(data):
                return None
            length = struct.unpack_from('>H', data, pos)[0]
            if length < 2 or pos + length > len(data):
                return None
            if marker in (0xC0, 0xC1, 0xC2):
                if length < 8:
                    return None
                height, width = struct.unpack_from('>HH', data, pos + 3)
                saw_frame = width > 0 and height > 0
            pos += length
            if marker == 0xDA:
                saw_scan = True
                while pos < len(data):
                    pos = data.find(b'\xFF', pos)
                    if pos < 0 or pos + 1 >= len(data):
                        return None
                    next_byte = data[pos + 1]
                    if next_byte == 0 or 0xD0 <= next_byte <= 0xD7:
                        pos += 2
                    else:
                        break
        return None
    return None


def find_embedded_image_in_pig(pig_data):
    """Extract the first complete GIF, JPEG or PNG, excluding PIG trailers."""
    signatures = ((b'GIF87a', 'gif'), (b'GIF89a', 'gif'),
                  (b'\x89PNG\r\n\x1a\n', 'png'), (b'\xff\xd8\xff', 'jpeg'))
    candidates = sorted((match.start(), kind) for signature, kind in signatures
                        for match in re.finditer(re.escape(signature), pig_data))
    for offset, kind in candidates:
        end = embedded_image_end(pig_data, offset, kind)
        if end is not None:
            return kind, pig_data[offset:end]
    return None


def extract_pig_text(pig_data):
    """Extract text/script content from a PIG entry that contains it."""
    if len(pig_data) < 14 or pig_data[2:5] != b'PIG':
        return None

    # PIG entries can contain Authorware script code and styled text
    # Look for substantial text content after the image data area
    strings = extract_printable_strings(pig_data, min_len=4)

    # Filter out common non-text patterns
    meaningful = []
    for s in strings:
        # Skip PIG header strings and common palette patterns
        if s in ('PIG', 'WIN', 'MAC', '001'):
            continue
        if len(set(s)) <= 2 and len(s) > 4:
            continue  # repetitive pattern
        meaningful.append(s)

    return "\n".join(meaningful) if meaningful else None


def parse_sound_header(data):
    """Read the packed 48/50-byte PCM descriptor, including its true byte count.

    The rate is a little-endian double (48 bytes) or x87 extended value
    (50 bytes). The later integer field is BYTE rate, not sample rate.
    These descriptors are little-endian even in the observed Mac containers.
    """
    if (len(data) not in (48, 50) or data[:4] not in (b'\x03\x00\x00\x00', b'\x03\x00\x00\x10')
            or data[20:24] != b'\x01\x00\x3c\x00'):
        return None
    channels, bits = data[24], data[26]
    align = struct.unpack_from('<H', data, len(data) - 12)[0]
    byte_rate = struct.unpack_from('<I', data, len(data) - 10)[0]
    if (not 1 <= channels <= 32 or bits not in (8, 16)
            or data[25] != bits or align != channels * (bits // 8) or not byte_rate):
        return None
    if len(data) == 48:
        rate = struct.unpack_from('<d', data, 28)[0]
    else:
        exponent = struct.unpack_from('<H', data, 36)[0]
        if exponent & 0x8000 or exponent & 0x7FFF == 0x7FFF:
            return None
        try:
            rate = math.ldexp(int.from_bytes(data[28:36], 'little') / 2**63,
                              (exponent & 0x7FFF) - 16383)
        except OverflowError:
            return None
    if rate == 0:
        rate = byte_rate / align  # some older descriptors leave the float unset
    if not math.isfinite(rate) or not 1000 <= rate <= 384000:
        return None
    return {'byte_count': struct.unpack_from('<I', data, 6)[0],
            'sample_rate': round(rate), 'bits_per_sample': bits,
            'channels': channels, 'block_align': align}


def sound_data_groups(data, entries, legacy=False):
    """Associate PCM chunks with descriptors, in entry order rather than by ID.

    Legacy tables can have all-zero IDs and can put the descriptor after
    its chunks. Only an exact match to the declared length authorizes a WAV.
    Unknown blocks remain binary instead of being guessed to be 8-bit PCM.
    """
    headers = {}
    for index, entry in enumerate(entries):
        if entry['decomp_size'] not in (48, 50):
            continue
        block = decompress_entry(data, entry)
        header = parse_sound_header(block) if block is not None else None
        if header and header['byte_count']:
            headers[index] = header
    groups, consumed, unresolved = {}, set(), []
    for index, header in headers.items():
        expected = header['byte_count']
        if expected % header['block_align']:
            unresolved.append(index)
            continue
        for backward in (False, True):
            order = range(index - 1, -1, -1) if backward else range(index + 1, len(entries))
            remaining, members = expected, []
            for candidate in order:
                entry = entries[candidate]
                length = entry['decomp_size']
                if (candidate in headers or entry['icon_type'] not in (0x06, 0x37)
                        or not 0 < length <= remaining):
                    break
                # Full continuation blocks have the observed storage chunk
                # sizes. Small neighboring metadata must not become samples.
                if length < remaining and (not backward or members) and length not in (4096, 65536):
                    break
                members.append(candidate)
                remaining -= length
                if not remaining:
                    break
            if not remaining:
                if backward:
                    members.reverse()
                groups[index] = {**header, 'members': members}
                consumed.update(members)
                break
        else:
            unresolved.append(index)
    if legacy and unresolved:
        # Edited legacy projects can move whole audio runs away from their
        # descriptor and insert unrelated entries between 64 KiB chunks.
        # Match only a unique, unclaimed run with the exact final-block size;
        # ambiguous or overlapping associations remain binary.
        proposals = {}
        for index in unresolved:
            header = headers[index]
            expected = header['byte_count']
            if expected % header['block_align']:
                continue
            full_count, tail_size = divmod(expected, 65536)
            if not tail_size:
                continue  # no distinct final block to establish a boundary
            eligible = [k for k, e in enumerate(entries) if k not in consumed and k not in headers
                        and e['icon_type'] in (0x06, 0x37) and e['storage_type'] == 1]
            options = []
            for tail in eligible:
                if entries[tail]['decomp_size'] != tail_size:
                    continue
                full = [k for k in eligible if k < tail and entries[k]['decomp_size'] == 65536]
                if len(full) >= full_count:
                    options.append((full[-full_count:] if full_count else []) + [tail])
            if len(options) == 1:
                proposals[index] = options[0]
        for index, members in proposals.items():
            if any(set(members).intersection(other) for key, other in proposals.items() if key != index):
                continue
            groups[index] = {**headers[index], 'members': members}
            consumed.update(members)
        unresolved = [index for index in unresolved if index not in groups]
    return groups, consumed, unresolved


def referenced_pcm_groups(data, entries):
    """Read legacy sound-object properties and their ordered resource references.

    Property 0x17 contains a byte count and WAVEFORMAT; 0x18 lists chunk IDs.
    These owners also contain names, expressions and playback settings, so
    retain their original data even after converting the referenced PCM.
    """
    by_id = {}
    for index, entry in enumerate(entries):
        by_id.setdefault(entry['id'], []).append(index)
    owners = {}
    for index, entry in enumerate(entries):
        if entry['icon_type'] != 0x06 or not 0 < entry['id'] < 0x4000:
            continue
        content = decompress_entry(data, entry)
        if content is None:
            continue
        pos, formats, lists = 0, [], []
        while pos + 4 <= len(content):
            tag, length = struct.unpack_from('<HH', content, pos)
            end = pos + 4 + length
            if not tag or end + (length & 1) > len(content):
                break
            if tag == 0x17:
                formats.append(content[pos + 4:end])
            elif tag == 0x18:
                lists.append(content[pos + 4:end])
            pos = end + (length & 1)
        if content[pos:] not in (b'', b'\0\0') or len(formats) != 1 or len(lists) != 1:
            continue
        fmt, refs = formats[0], lists[0]
        if len(fmt) != 26 or fmt[:2] != b'\x01\0' or len(refs) < 4:
            continue
        byte_count = struct.unpack_from('<I', fmt, 6)[0]
        codec, channels, rate, byte_rate, align, bits = struct.unpack_from('<HHIIHH', fmt, 10)
        count = struct.unpack_from('<H', refs)[0]
        end = 2 + 2 * count
        # Some saved lists reserve 128 bytes, with zero-filled unused slots.
        if (codec != 1 or not 1 <= channels <= 32 or bits not in (8, 16)
                or not 1000 <= rate <= 384000 or align != channels * (bits // 8)
                or byte_rate != rate * align or not byte_count or byte_count % align
                or not count or end > len(refs) or len(refs) % 2 or any(refs[end:])):
            continue
        owners[index] = {'byte_count': byte_count, 'sample_rate': rate,
                         'bits_per_sample': bits, 'channels': channels,
                         'block_align': align, 'keep_owner': True,
                         'resource_ids': struct.unpack_from('<' + 'H' * count, refs, 2)}
    groups, consumed, unresolved = {}, set(), []
    for index, owner in owners.items():
        members = []
        valid = len(by_id[entries[index]['id']]) == 1
        for resource_id in owner['resource_ids']:
            candidates = by_id.get(resource_id, [])
            if len(candidates) != 1 or candidates[0] in owners:
                valid = False
                break
            target = candidates[0]
            entry = entries[target]
            content = decompress_entry(data, entry) if entry['icon_type'] in (0x06, 0x37) else None
            if content is None or not content or len(content) != entry['decomp_size']:
                valid = False
                break
            members.append(target)
        if not valid or sum(entries[i]['decomp_size'] for i in members) != owner['byte_count']:
            unresolved.append(index)
            continue
        groups[index] = {**owner, 'members': members}
        consumed.update(members)
    # A successful owner must not hide chunks needed by an unresolved owner.
    for index in unresolved:
        for resource_id in owners[index]['resource_ids']:
            consumed.difference_update(by_id.get(resource_id, []))
    return groups, consumed, unresolved


def make_wav(pcm_data, sample_rate=22050, bits_per_sample=8, channels=1):
    """Create a WAV file from raw PCM data."""
    byte_rate = sample_rate * channels * (bits_per_sample // 8)
    block_align = channels * (bits_per_sample // 8)
    data_size = len(pcm_data)
    padding = b'\x00' if data_size & 1 else b''
    file_size = 36 + data_size + len(padding)

    header = struct.pack('<4sI4s', b'RIFF', file_size, b'WAVE')
    fmt = struct.pack('<4sIHHIIHH', b'fmt ', 16, 1, channels,
                      sample_rate, byte_rate, block_align, bits_per_sample)
    data_hdr = struct.pack('<4sI', b'data', data_size)
    return header + fmt + data_hdr + pcm_data + padding


def find_uncovered_zlib_blocks(data, hdr, entries):
    """Find complete, unique zlib streams in gaps, without a per-byte set."""
    first_data = min((e['data_offset'] for e in entries if e['comp_size'] > 0 and e['data_offset'] > 0),
                     default=hdr['table_offset'])
    regions = [(0, max(0x58, min(first_data, hdr['table_offset']))),
               (hdr['table_offset'], hdr['table_offset'] + hdr['table_total_size'])]
    regions.extend((e['data_offset'], e['data_offset'] + e['comp_size'])
                   for e in entries if e['data_offset'] >= 0 and e['comp_size'] > 0)
    merged = []
    for start, end in sorted(regions):
        start, end = max(0, start), min(len(data), end)
        if end <= start:
            continue
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
        else:
            merged.append((start, end))
    gaps = []
    start = 0
    for low, high in merged:
        if start < low:
            gaps.append((start, low))
        start = high
    if start < len(data):
        gaps.append((start, len(data)))
    seen = set()
    for entry in entries:
        content = decompress_entry(data, entry)
        if content:
            seen.add(hashlib.sha256(content).digest())
    blocks = []
    for start, end in gaps:
        cursor = start
        while cursor + 2 <= end:
            offset = data.find(b'\x78', cursor, end - 1)
            if offset < 0:
                break
            cursor = offset + 1
            if data[offset + 1] not in (0x01, 0x5E, 0x9C, 0xDA):
                continue
            try:
                obj = zlib.decompressobj()
                result = obj.decompress(data[offset:end], 256 * 1024 * 1024)
            except zlib.error:
                continue
            if not obj.eof:
                continue
            consumed = end - offset - len(obj.unused_data)
            cursor = offset + consumed
            digest = hashlib.sha256(result).digest()
            if digest not in seen and any(result):
                blocks.append((offset, consumed, result))
                seen.add(digest)
    return blocks


def read_entry_table(data, hdr):
    """Select an entry layout and reject absent/truncated tables explicitly."""
    table = hdr['table_offset']
    if hdr['magic'] in ('WPCR', 'WPLI') and hdr['flags'] & 0xFFFFFFFF == 0xFFFFFFFC:
        reader, size = read_entries_wpcr, 4
    elif hdr['magic'] in ('WCRS', 'WPCR', 'WPLI') and hdr['format_version'] == 2:
        reader, size = read_entries_wcrs_v2, 10
        table = hdr['file_size'] - hdr['table_total_size']
    elif hdr['magic'] in ('WCRS', 'WPCR', 'WPLI') or hdr.get('big_endian'):
        reader, size = read_entries_wcrs, 16
    elif hdr['magic'] == 'PCRS' and hdr['entry_count'] * 30 > hdr['table_total_size']:
        reader, size = read_entries_pcrs, 10
    else:
        reader, size = read_entries, 30
    end = table + hdr['entry_count'] * size
    if hdr['entry_count'] and (table < 64 or end > len(data)):
        raise ValueError(f'Entry table is incomplete: requires bytes 0x{table:x}..0x{end:x}, file ends at 0x{len(data):x}')
    return reader(data, hdr)


def audio_container_size(data):
    if len(data) >= 12 and data[:4] in (b'RIFF', b'FORM'):
        size = struct.unpack_from('<I' if data[:4] == b'RIFF' else '>I', data, 4)[0] + 8
        return size if size >= 12 else None
    return None


def pad_audio_container(data):
    """Restore an omitted final RIFF/FORM pad byte only when all data exists."""
    expected = audio_container_size(data)
    if expected != len(data) + 1:
        return data
    endian = '<' if data[:4] == b'RIFF' else '>'
    offset = 12
    while offset + 8 <= len(data):
        size = struct.unpack_from(endian + 'I', data, offset + 4)[0]
        end = offset + 8 + size
        if end == len(data) and size & 1:
            return data + b'\x00'
        if end > len(data):
            break
        offset = end + (size & 1)
    return data


def recover_wave(data):
    """Validate WAVE chunks, salvaging complete audio before damaged metadata.

    The caller must preserve the original bytes whenever a repair is made.
    Never shorten an incomplete data chunk and present it as complete audio.
    """
    end = audio_container_size(data)
    if end is None or end > len(data) or data[8:12] != b'WAVE':
        return None
    offset = 12
    has_format = has_data = False
    while offset < end:
        if offset + 8 > end:
            break
        tag = data[offset:offset + 4]
        size = struct.unpack_from('<I', data, offset + 4)[0]
        chunk_end = offset + 8 + size
        if chunk_end > end:
            if tag in (b'fmt ', b'data'):
                return None
            break
        if tag == b'fmt ':
            has_format = size >= 16
        elif tag == b'data':
            has_data = True
        offset = chunk_end + (size & 1)
    if not has_format or not has_data:
        return None
    if offset >= end:
        return data
    # The complete fmt/data chunks are usable; exclude the malformed tail.
    return b'RIFF' + struct.pack('<I', offset - 8) + data[8:offset]


def has_wrapped_mp3_header(data):
    """Recognize Authorware's 36-byte wrapper followed by a Layer III header."""
    if len(data) < 40 or data[:4] != b'\0\0\0\x20':
        return False
    first, second, third = data[36:39]
    return (first == 0xff and second & 0xe0 == 0xe0
            and (second >> 3) & 3 != 1 and (second >> 1) & 3 == 1
            and third >> 4 not in (0, 15) and (third >> 2) & 3 != 3)


def streaming_audio_groups(data, entries):
    """Join RIFF/FORM chunks even when metadata records separate them.

    A known container length delimits a stream. MP3/unknown streams retain
    the consecutive-entry convention, with new ID3 or Authorware MP3 wrapper
    headers starting a file. Wrappers are examined only at entry boundaries.
    """
    groups = {}
    start = previous = None
    chunks = []
    expected = None
    total = 0

    def flush():
        nonlocal start, chunks, expected, total
        if start is not None:
            groups[start] = (pad_audio_container(b''.join(chunks)), len(chunks), expected)
        start, chunks, expected, total = None, [], None, 0

    for index, entry in enumerate(entries):
        if entry['icon_type'] != 0x3C:
            continue
        chunk = decompress_entry(data, entry)
        if chunk is None:
            flush()
            previous = index
            continue
        new_size = audio_container_size(chunk)
        new_header = new_size is not None or chunk[:3] == b'ID3' or has_wrapped_mp3_header(chunk)
        if start is not None and (new_header or (expected is None and index != previous + 1)):
            flush()
        if start is None:
            start, expected = index, new_size
        chunks.append(chunk)
        total += len(chunk)
        previous = index
        if expected is not None and (total >= expected or
                (total + 1 == expected and len(pad_audio_container(b''.join(chunks))) == expected)):
            flush()
    flush()
    return groups


def recover_unindexed_content(data, output_dir):
    """Salvage complete images from a legacy file whose table is missing.

    Without the table the original entry IDs, types and boundaries cannot
    be reconstructed reliably. Emit recovered media only; a copy of the
    entire input is not an extracted resource, even in deep mode.
    """
    count = 0
    offsets = [match.start() - 2 for match in re.finditer(re.escape(b'PIG\x00'), data)
               if match.start() >= 2 and data[match.start() + 4:match.start() + 8] in (b'WIN\x00', b'MAC\x00')]
    for index, offset in enumerate(offsets):
        end = offsets[index + 1] if index + 1 < len(offsets) else len(data)
        block = data[offset:end]
        dib = find_best_dib_in_pig(block)
        bmp = make_bmp_from_dib(dib) if dib is not None else None
        if bmp:
            fname = write_output(output_dir, f'recovered_0x{offset:06x}_PIG.bmp', bmp)
        else:
            embedded = find_embedded_image_in_pig(block)
            if embedded is None:
                continue
            extension, content = embedded
            fname = write_output(output_dir, f'recovered_0x{offset:06x}_PIG.{extension}', content)
        print(f'  Recovered complete image at 0x{offset:x} -> {fname}')
        count += 1
    return count


def main():
    parser = argparse.ArgumentParser(description='Extract Authorware resources, PIG pictures and APNG animations.')
    parser.add_argument('inputFile')
    parser.add_argument('outputDir')
    parser.add_argument('--report', action='store_true', help='Write a self-contained HTML review report')
    parser.add_argument('--deep', action='store_true',
                        help='Include SVG metadata, write manifest JSON files and retain original PIG, DIB, animation resources, cursor tables, project roots, font tables and sound headers')
    args = parser.parse_args()
    input_file, output_dir = args.inputFile, args.outputDir
    make_report = args.report

    with open(input_file, 'rb') as f:
        data = f.read()
    source_hash = hashlib.sha256(data).hexdigest()

    try:
        data, hdr = load_authorware(data)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    try:
        entries = read_entry_table(data, hdr)
    except ValueError as exc:
        if hdr['file_size'] > len(data) and hdr['magic'] in ('WPCR', 'WPLI', 'WCRS'):
            os.makedirs(output_dir, exist_ok=True)
            print(f"Warning: {exc}; recovering available content", file=sys.stderr)
            count = recover_unindexed_content(data, output_dir)
            print(f"Extracted {count} items to {output_dir} (incomplete input)")
            sys.exit(2)
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    # Exclusive output names let the report include only files from this run,
    # even when the destination already contains earlier extractions.
    report_existing = set(os.listdir(output_dir)) if make_report else set()

    print(f"File: {input_file}")
    if 'exe_offset' in hdr:
        print(f"  Executable payload offset: 0x{hdr['exe_offset']:x}")
    print(f"  Format version: {hdr['format_version']}")
    print(f"  Entry count: {hdr['entry_count']}")
    print(f"  Entry table offset: 0x{hdr['table_offset']:x}")
    print(f"  File size: {hdr['file_size']}")
    print()

    extracted_count = 0
    audio_groups = streaming_audio_groups(data, entries)
    legacy_audio = hdr['magic'] in ('WPCR', 'WPLI', 'WCRS') or hdr.get('big_endian', False)
    pcm_groups, pcm_members, unresolved_pcm = sound_data_groups(data, entries, legacy=legacy_audio)
    property_pcm_members = set()
    # Explicit-ID Star APP/APR tables share the WCRS property layout. The
    # ordinal-ID Star variants use separate packed sound descriptors.
    if (hdr['magic'] == 'WCRS' or (hdr['magic'] in ('WPCR', 'WPLI')
                                  and hdr['flags'] == -1)):
        property_groups, property_pcm_members, property_unresolved = referenced_pcm_groups(data, entries)
        legacy_pcm_indices = set(pcm_groups) | pcm_members
        for index, group in property_groups.items():
            if index in legacy_pcm_indices or legacy_pcm_indices.intersection(group['members']):
                property_unresolved.append(index)
                property_pcm_members.difference_update(group['members'])
                pcm_members.difference_update(group['members'])
                continue
            pcm_groups[index] = group
        unresolved_pcm.extend(property_unresolved)
    incomplete_audio = len(unresolved_pcm)
    for index in unresolved_pcm:
        print(f"Warning: PCM descriptor at entry index {index} (ID {entries[index]['id']}) "
              'could not be matched to complete audio; entries preserved as binary', file=sys.stderr)
    # Detect segment files (header file_size > actual data length)
    is_segment = hdr['file_size'] > len(data)
    skipped_segment = 0
    decompression_failures = 0
    pig_context = authorware_pig.Context(sys.modules[__name__], data, entries)
    cursor_endian = '>' if hdr.get('big_endian') else '<'
    cursor_tables = authorware_cursor.referenced_tables(pig_context, cursor_endian)
    cursor_results = []
    animation_results = []
    animation_consumed = set()
    pig_results = []
    pigs_by_index = {}
    dib_results = []
    rendered_dibs = {}
    rendered_font_tables = set()

    def save_pig(content, prefix, entry_id, index):
        """Write the picture and make the sole raw-export decision for this PIG."""
        result = authorware_pig.render_pig(content, pig_context, deep=args.deep, prefer_png=True)
        svg = result.pop('svg')
        png = result.pop('png', None)
        picture, extension, mime = (png, 'png', 'image/png') if png is not None else (svg, 'svg', 'image/svg+xml')
        result.update(id=entry_id, index=index, key=str(index),
                      pig_sha256=hashlib.sha256(content).hexdigest())
        if pig_context.display_pictures is not None and isinstance(index, int):
            result['display_objects'] = pig_context.display_pictures.get(index, [])
        count = 0
        if picture:
            platform = result.get('platform', 'unknown')
            fname = write_output(output_dir, f'{prefix}_{platform}.{extension}', picture)
            result['file'] = fname
            rendered_font_tables.update(result.get('rendered_font_tables', []))
            for dib_index in result.get('rendered_dibs', []):
                rendered_dibs.setdefault(dib_index, []).append({'id': entry_id, 'index': index, 'file': fname})
            print(f'  PIG entry {entry_id}: {extension.upper()} {result["status"]} -> {fname}')
            count = 1
            if make_report:
                import base64
                result['preview'] = f'data:{mime};base64,' + base64.b64encode(picture).decode('ascii')
        # Handling and rendering fidelity are separate: any processed drawing
        # keeps its diagnostics, but its original is needed only in deep mode.
        if args.deep or not result['handled']:
            fname = write_output(output_dir, f'{prefix}.bin', content)
            reason = 'Original PIG retained by --deep' if args.deep else 'Original PIG retained; drawing could not be handled'
            result.update(raw_file=fname, raw_export='deep' if args.deep else 'unhandled', raw_reason=reason)
            print(f'  PIG entry {entry_id}: {reason} -> {fname}')
            count += 1
        else:
            reason = ('Original PIG omitted; picture conversion complete' if result['status'] == 'converted'
                      else 'Original PIG omitted; drawing handled with limitations (see diagnostics)')
            result.update(raw_export='omitted', raw_reason=reason)
        pig_results.append(result)
        pigs_by_index[index] = result
        return count

    def pig_bitmap_is_rendered(index, dib_offset):
        """Skip only the bitmap whose owning drawing record reached the picture."""
        picture = pigs_by_index.get(index, {})
        if not picture.get('file'):
            return False
        for record in picture.get('rendered_image_records', []):
            if record['offset'] <= dib_offset < record['offset'] + record['length']:
                picture.update(bitmap_export='rendered_in_picture', bitmap_offset=dib_offset)
                print(f'  PIG entry {picture["id"]}: standalone bitmap omitted; rendered in {picture["file"]}')
                return True
        return False

    # Resolve and write all pictures before deciding which standalone DIBs
    # need a BMP. Entry order and physical order do not establish references.
    for index, entry in enumerate(entries):
        if entry['icon_type'] not in (0x34, 0xFFFD):
            continue
        if is_segment and (entry['data_offset'] >= len(data) or entry['data_offset'] + entry['comp_size'] > len(data)):
            continue
        content = pig_context.entry(index)
        if content and content[2:6] == b'PIG\0':
            name = ICON_TYPE_NAMES.get(entry['icon_type'], 'PIG')
            extracted_count += save_pig(content, f'{entry["id"]:03d}_{name}', entry['id'], index)
    uncovered = find_uncovered_zlib_blocks(data, hdr, entries) if hdr['magic'] == 'ACRS' and not hdr.get('big_endian') else []
    for index, (offset, _, content) in enumerate(uncovered):
        if content[2:6] == b'PIG\0':
            prefix = f'extra_{index:03d}_0x{offset:06x}'
            extracted_count += save_pig(content, f'{prefix}_PIG', prefix, f'offset:{offset}')

    # Animation storage is linked by explicit resource IDs, not table order.
    # Suppress originals only after a complete APNG has been written. Shared
    # blocks needed by a failed conversion remain available as raw resources.
    animation_owners = authorware_animation.referenced_animations(pig_context, cursor_endian)
    animation_preserved = set()
    for index, entry in enumerate(entries):
        if entry['icon_type'] != 0x33:
            continue
        candidates = animation_owners.get(index, [])
        try:
            animation = authorware_animation.render_animation(pig_context, index, candidates)
        except ValueError as exc:
            animation_preserved.update(authorware_animation.referenced_indices(pig_context, candidates))
            animation_results.append({'id': entry['id'], 'index': index, 'status': 'unrendered',
                                      'warnings': [str(exc)]})
            print(f'  Animation entry {entry["id"]}: {exc}; original resources retained')
            continue
        fname = write_output(output_dir, f'{entry["id"]:03d}_Animation.apng', animation.pop('apng'))
        animation.update(id=entry['id'], index=index, file=fname)
        animation_results.append(animation)
        animation_consumed.update(animation['consumed_indices'])
        print(f'  Animation entry {entry["id"]}: {animation["frames"]} frames, '
              f'{animation["width"]}x{animation["height"]} -> {fname}')
        for warning in animation['warnings']:
            print(f'    Warning: {warning}')
        extracted_count += 1
    animation_consumed.difference_update(animation_preserved)

    for entry_index, entry in enumerate(entries):
        if entry_index in pcm_members:
            continue  # written with its descriptor, even when IDs are repeated
        if entry_index in property_pcm_members and not args.deep:
            continue  # explicitly referenced PCM; --deep retains chunk originals
        if entry_index in animation_consumed and not args.deep:
            continue  # descriptor/pixel/mask data successfully exported as APNG
        eid = entry['id']
        icon_type = entry['icon_type']
        type_name = ICON_TYPE_NAMES.get(icon_type, f"Unknown_0x{icon_type:02x}")

        if entry_index == pig_context.project_root_index and not args.deep:
            print(f'  Entry {eid:3d} ({type_name}): internal project root omitted; use --deep to retain')
            continue

        if entry_index in rendered_font_tables and not args.deep:
            print(f'  Entry {eid:3d} ({type_name}): original font/style table omitted; used in PIG SVGs')
            continue

        # Skip entries whose data is beyond or straddles this segment's bounds
        if is_segment and (entry['data_offset'] >= len(data) or entry['data_offset'] + entry['comp_size'] > len(data)):
            skipped_segment += 1
            continue

        entry_data = decompress_entry(data, entry)
        if entry_data is None:
            if entry['comp_size'] == 0 and entry['decomp_size'] == 0:
                continue  # silent skip for empty placeholder entries
            print(f"  Entry {eid:3d} ({type_name}): DECOMPRESS FAILED")
            decompression_failures += 1
            off = entry['data_offset']
            if 0 <= off < len(data) and entry['comp_size'] > 0:
                raw = data[off:off + entry['comp_size']]
                fname = write_output(output_dir, f'{eid:03d}_{type_name}_compressed.bin', raw)
                print(f"  Entry {eid:3d} ({type_name}): compressed bytes preserved -> {fname}")
                extracted_count += 1
            continue

        if entry_index in cursor_tables:
            try:
                cursors = authorware_cursor.decode_table(entry_data, cursor_tables[entry_index], cursor_endian)
            except ValueError as exc:
                print(f'Warning: cursor table entry {eid} could not be converted: {exc}; original retained', file=sys.stderr)
            else:
                for cursor in cursors:
                    png = cursor.pop('png')
                    name = f'{eid:03d}_Cursor_{cursor["cursor_id"]:03d}_{cursor["width"]}x{cursor["height"]}.png'
                    fname = write_output(output_dir, name, png)
                    cursor.update(file=fname, id=eid, index=entry_index)
                    print(f'  Entry {eid:3d}: cursor PNG -> {fname}')
                    if cursor['inverting_pixels']:
                        print(f'    {cursor["inverting_pixels"]} background-inverting pixels rendered black in PNG')
                    extracted_count += 1
                if args.deep:
                    fname = write_output(output_dir, f'{eid:03d}_{type_name}.bin', entry_data)
                    for cursor in cursors:
                        cursor['raw_file'] = fname
                    print(f'  Entry {eid:3d}: original cursor table retained by --deep -> {fname}')
                    extracted_count += 1
                else:
                    print(f'  Entry {eid:3d}: original cursor table omitted; cursors saved as PNG')
                cursor_results.extend(cursors)
                continue

        if entry_index in pcm_groups:
            group = pcm_groups[entry_index]
            chunks = [decompress_entry(data, entries[index]) for index in group['members']]
            start_eid = entries[group['members'][0]]['id']
            rate, bits, channels = group['sample_rate'], group['bits_per_sample'], group['channels']
            if all(chunk is not None for chunk in chunks):
                pcm = b''.join(chunks)
                wav = make_wav(pcm, rate, bits, channels)
                fname = write_output(output_dir, f'{start_eid:05d}_SoundData_{rate}hz_{bits}bit.wav', wav)
                print(f'  Entry {start_eid} (SoundData): WAV {rate}Hz {bits}bit {channels}ch '
                      f'({len(pcm)} PCM bytes, {len(chunks)} chunks) -> {fname}')
                extracted_count += 1
                # Omit the descriptor only after its audio has been written.
                # Failed/unmatched sounds still retain their original header.
                if not args.deep and not group.get('keep_owner'):
                    print(f'  Entry {eid:3d} ({type_name}): original sound header omitted; audio saved as WAV')
                    continue
            else:
                incomplete_audio += 1
                print(f'Warning: PCM audio for entry {eid} is missing or damaged; available chunks preserved', file=sys.stderr)
                for index, chunk in zip(group['members'], chunks):
                    member = entries[index]
                    if chunk is None:
                        offset = member['data_offset']
                        chunk = data[max(0, offset):max(0, offset) + member['comp_size']] if offset >= 0 else b''
                    if chunk:
                        fname = write_output(output_dir, f"{member['id']:05d}_SoundData_chunk_{index}.bin", chunk)
                        print(f'  PCM chunk preserved -> {fname}')
                        extracted_count += 1

        # Keep content exports and raw fallback independently of the SVGs
        # already written. Separate DIB resources follow the policy below.
        count_before = extracted_count

        # Extract based on type
        if icon_type == 0x3E:
            # Full BMP - extract directly
            if len(entry_data) >= 54 and entry_data[:2] == b'BM':
                w = struct.unpack_from('<i', entry_data, 18)[0]
                h = struct.unpack_from('<i', entry_data, 22)[0]
                bpp = struct.unpack_from('<H', entry_data, 28)[0]
                fname = f"{eid:03d}_{type_name}_{w}x{h}_{bpp}bpp.bmp"
                fname = write_output(output_dir, fname, entry_data)
                print(f"  Entry {eid:3d} ({type_name}): BMP {w}x{h} {bpp}bpp -> {fname}")
                extracted_count += 1

        elif icon_type == 0x35:
            info = {'id': eid, 'index': entry_index,
                    'rendered_by': rendered_dibs.get(entry_index, [])}
            dib_results.append(info)
            # Successfully embedded DIBs need no separate export by default.
            # --deep retains the original bytes, including uncropped pixels.
            if not info['rendered_by'] or args.deep:
                raw_name = write_output(output_dir, f'{eid:03d}_{type_name}.bin', entry_data)
                info['raw_file'] = raw_name
                extracted_count += 1
            if info['rendered_by']:
                info['status'] = 'rendered_in_pig'
                info['reason'] = 'Standalone DIB omitted; bitmap embedded in a PIG SVG'
                if args.deep:
                    info['reason'] = 'Standalone BMP omitted; original DIB retained by --deep'
                print(f'  Entry {eid:3d} ({type_name}): {info["reason"]}'
                      + (f' -> {raw_name}' if args.deep else ''))
                continue
            bmp_data = make_bmp_from_dib(entry_data)
            info['palette_source'] = 'self_contained'
            reason = 'Bitmap header, palette or pixels could not be decoded'
            fields = dib_fields(entry_data)
            if bmp_data is None and fields and fields[4] <= 8:
                palette, palette_issue = pig_context.standalone_palette(entry_index)
                if palette is not None:
                    bmp_data = make_bmp_from_dib(entry_data, palette)
                    info['palette_source'] = 'explicit_pig_reference'
                else:
                    reason += '; ' + palette_issue
            if bmp_data:
                de = dib_endian(entry_data)
                w = struct.unpack_from(f'{de}i', entry_data, 4)[0]
                h = struct.unpack_from(f'{de}i', entry_data, 8)[0]
                bpp = struct.unpack_from(f'{de}H', entry_data, 14)[0]
                fname = f"{eid:03d}_{type_name}_{w}x{h}_{bpp}bpp.bmp"
                fname = write_output(output_dir, fname, bmp_data)
                info.update(status='standalone_bmp', file=fname)
                print(f"  Entry {eid:3d} ({type_name}): DIB {w}x{h} {bpp}bpp -> {fname}")
                extracted_count += 1
            else:
                info.pop('palette_source', None)
                info.update(status='raw_only', reason=reason)
                print(f'  Entry {eid:3d} ({type_name}): {reason}; original preserved -> {raw_name}')

        elif icon_type == 0x34:
            # PIG - try to extract embedded bitmap
            if len(entry_data) >= 14 and entry_data[2:5] == b'PIG':
                platform = entry_data[6:9].decode('ascii', errors='replace')
                candidate = find_best_dib_in_pig(entry_data, with_offset=True)

                if candidate:
                    dib_offset, dib_data = candidate
                    if pig_bitmap_is_rendered(entry_index, dib_offset):
                        continue
                    bmp_data = make_bmp_from_dib(dib_data)
                    if bmp_data:
                        de = dib_endian(dib_data)
                        w = struct.unpack_from(f'{de}i', dib_data, 4)[0]
                        h = struct.unpack_from(f'{de}i', dib_data, 8)[0]
                        bpp = struct.unpack_from(f'{de}H', dib_data, 14)[0]
                        fname = f"{eid:03d}_{type_name}_{platform}_{w}x{h}_{bpp}bpp.bmp"
                        fname = write_output(output_dir, fname, bmp_data)
                        print(f"  Entry {eid:3d} ({type_name}): PIG/{platform} {w}x{h} {bpp}bpp -> {fname}")
                        extracted_count += 1
                        continue

                # Check for embedded GIF/JPEG/PNG
                embedded = find_embedded_image_in_pig(entry_data)
                if embedded:
                    img_fmt, img_data = embedded
                    pw, ph = extract_pig_dimensions(entry_data)
                    dim_str = f" {pw}x{ph}" if pw and ph else ""
                    fname = f"{eid:03d}_{type_name}_{platform}{dim_str}.{img_fmt}"
                    fname = write_output(output_dir, fname, img_data)
                    print(f"  Entry {eid:3d} ({type_name}): PIG/{platform}{dim_str} {img_fmt.upper()} ({len(img_data)} bytes) -> {fname}")
                    extracted_count += 1
                    continue

                # Check for text/script content in PIG
                # Preserve decoded multibyte display text in the text export;
                # scanning binary bytes as ASCII loses those characters.
                picture = pigs_by_index.get(entry_index, {})
                pig_text = (picture.get('text') if pig_context.fonts.text_encoding else None) or extract_pig_text(entry_data)
                if pig_text and len(pig_text) > 20:
                    fname = f"{eid:03d}_{type_name}_{platform}_text.txt"
                    fname = write_output(output_dir, fname, pig_text)
                    print(f"  Entry {eid:3d} ({type_name}): PIG/{platform} text ({len(pig_text)} chars) -> {fname}")
                    extracted_count += 1
                    if entry_index not in pigs_by_index:
                        fname = write_output(output_dir, f'{eid:03d}_{type_name}.bin', entry_data)
                        print(f"  Entry {eid:3d} ({type_name}): original PIG preserved -> {fname}")
                        extracted_count += 1
                    continue

                # Save PIG dimensions info
                pw, ph = extract_pig_dimensions(entry_data)
                if pw and ph:
                    print(f"  Entry {eid:3d} ({type_name}): PIG/{platform} {pw}x{ph} (no extractable bitmap)")
                else:
                    print(f"  Entry {eid:3d} ({type_name}): PIG/{platform} ({len(entry_data)} bytes, no extractable content)")

        elif icon_type in TEXT_TYPES:
            # Text-containing types
            text = extract_text_from_entry(entry_data, icon_type)
            if text and len(text.strip()) > 0:
                fname = f"{eid:03d}_{type_name}.txt"
                fname = write_output(output_dir, fname, text)
                print(f"  Entry {eid:3d} ({type_name}): text ({len(text)} chars) -> {fname}")
                extracted_count += 1
            else:
                print(f"  Entry {eid:3d} ({type_name}): {len(entry_data)} bytes (no extractable text)")

        elif icon_type == 0x25:
            # Display icon - extract text content
            strings = extract_printable_strings(entry_data, min_len=3)
            if strings:
                text = "\n".join(strings)
                fname = f"{eid:03d}_{type_name}.txt"
                fname = write_output(output_dir, fname, text)
                print(f"  Entry {eid:3d} ({type_name}): display text ({len(strings)} strings) -> {fname}")
                extracted_count += 1
            else:
                print(f"  Entry {eid:3d} ({type_name}): {len(entry_data)} bytes (no extractable text)")

        elif icon_type == 0xFFFD:
            # Plugin PIG - same handling as regular PIG (0x34)
            if len(entry_data) >= 14 and entry_data[2:5] == b'PIG':
                platform = entry_data[6:9].decode('ascii', errors='replace')
                candidate = find_best_dib_in_pig(entry_data, with_offset=True)
                if candidate:
                    dib_offset, dib_data = candidate
                    if pig_bitmap_is_rendered(entry_index, dib_offset):
                        continue
                    bmp_data = make_bmp_from_dib(dib_data)
                    if bmp_data:
                        de = dib_endian(dib_data)
                        w = struct.unpack_from(f'{de}i', dib_data, 4)[0]
                        h = struct.unpack_from(f'{de}i', dib_data, 8)[0]
                        bpp = struct.unpack_from(f'{de}H', dib_data, 14)[0]
                        fname = f"{eid:03d}_{type_name}_{platform}_{w}x{h}_{bpp}bpp.bmp"
                        fname = write_output(output_dir, fname, bmp_data)
                        print(f"  Entry {eid:3d} ({type_name}): PIG/{platform} {w}x{h} {bpp}bpp -> {fname}")
                        extracted_count += 1
                        continue
                print(f"  Entry {eid:3d} ({type_name}): PIG/{platform} ({len(entry_data)} bytes, no extractable bitmap)")
            else:
                fname = f"{eid:03d}_{type_name}.bin"
                fname = write_output(output_dir, fname, entry_data)
                print(f"  Entry {eid:3d} ({type_name}): {len(entry_data)} bytes -> {fname}")
                extracted_count += 1

        elif icon_type == 0x3B:
            # Embedded media - can contain BMP, 3DMF models, or other data
            if len(entry_data) >= 54 and entry_data[:2] == b'BM':
                w = struct.unpack_from('<i', entry_data, 18)[0]
                h = struct.unpack_from('<i', entry_data, 22)[0]
                bpp = struct.unpack_from('<H', entry_data, 28)[0]
                fname = f"{eid:03d}_{type_name}_{w}x{h}_{bpp}bpp.bmp"
                fname = write_output(output_dir, fname, entry_data)
                print(f"  Entry {eid:3d} ({type_name}): BMP {w}x{h} {bpp}bpp -> {fname}")
            elif entry_data[:4] == b'3DMF':
                fname = f"{eid:03d}_{type_name}.3dmf"
                fname = write_output(output_dir, fname, entry_data)
                print(f"  Entry {eid:3d} ({type_name}): 3DMF model ({len(entry_data)} bytes) -> {fname}")
            elif len(entry_data) > 15 and entry_data[12:15] in (b'FWS', b'CWS'):
                # SWF with 12-byte big-endian wrapper
                swf_data = entry_data[12:]
                fname = f"{eid:03d}_{type_name}.swf"
                fname = write_output(output_dir, fname, swf_data)
                print(f"  Entry {eid:3d} ({type_name}): SWF ({len(swf_data)} bytes) -> {fname}")
            else:
                fname = f"{eid:03d}_{type_name}.bin"
                fname = write_output(output_dir, fname, entry_data)
                print(f"  Entry {eid:3d} ({type_name}): {len(entry_data)} bytes -> {fname}")
            extracted_count += 1

        elif icon_type == 0x37:
            # A type code alone does not specify rate, depth, channels or
            # stream boundaries. Keep unassociated samples losslessly.
            fname = write_output(output_dir, f'{eid:05d}_{type_name}.bin', entry_data)
            print(f'  Entry {eid:3d} ({type_name}): PCM without matched metadata preserved -> {fname}')
            extracted_count += 1

        elif icon_type == 0x3C:
            if entry_index not in audio_groups:
                continue  # this chunk was written with its stream's first entry
            combined, chunks, expected = audio_groups[entry_index]
            if expected is not None and len(combined) < expected:
                incomplete_audio += 1
                print(f"Warning: audio entry {eid} is incomplete ({len(combined)}/{expected} bytes)", file=sys.stderr)
                ext, fmt_name = 'bin', 'incomplete audio'
            elif combined[:4] == b'FORM':
                ext, fmt_name = 'aiff', 'AIFF'
            elif combined[:4] == b'RIFF':
                recovered = recover_wave(combined)
                if recovered is None:
                    incomplete_audio += 1
                    print(f'Warning: audio entry {eid} has invalid WAVE chunks; original preserved', file=sys.stderr)
                    ext, fmt_name = 'bin', 'undecoded audio'
                else:
                    if recovered != combined:
                        original = write_output(output_dir, f'{eid:03d}_{type_name}_original.bin', combined)
                        print(f'  Entry {eid:3d} ({type_name}): damaged WAVE metadata preserved -> {original}')
                        print(f'Warning: audio entry {eid} has damaged trailing WAVE metadata; complete audio recovered', file=sys.stderr)
                        extracted_count += 1
                        incomplete_audio += 1
                        combined = recovered
                    ext, fmt_name = 'wav', 'WAV'
            elif combined[:3] == b'ID3' or (len(combined) > 1 and combined[0] == 0xFF and combined[1] in (0xFB, 0xF3, 0xFA, 0xF2, 0xE2)):
                ext, fmt_name = 'mp3', 'MP3'
            elif has_wrapped_mp3_header(combined):
                combined = combined[0x24:]
                ext, fmt_name = 'mp3', 'MP3'
            else:
                ext, fmt_name = 'bin', 'audio'
            fname = write_output(output_dir, f"{eid:03d}_{type_name}.{ext}", combined)
            print(f"  Entry {eid:3d} ({type_name}): {fmt_name} ({len(combined)} bytes, {chunks} chunks) -> {fname}")
            extracted_count += 1

        else:
            # Other types - save raw decompressed data
            fname = f"{eid:03d}_{type_name}.bin"
            fname = write_output(output_dir, fname, entry_data)
            print(f"  Entry {eid:3d} ({type_name}): {len(entry_data)} bytes -> {fname}")
            extracted_count += 1

        if (extracted_count == count_before and icon_type not in (0x37, 0x3C)
                and entry_index not in pigs_by_index):
            fname = write_output(output_dir, f'{eid:03d}_{type_name}.bin', entry_data)
            print(f"  Entry {eid:3d} ({type_name}): undecoded content preserved -> {fname}")
            extracted_count += 1

    # Extract unique uncovered zlib blocks (only for ACRS files with zlib compression)
    if uncovered:
        print(f"\n  Unreferenced data blocks ({len(uncovered)}):")
        for idx, (off, comp_sz, block_data) in enumerate(uncovered):
            prefix = f"extra_{idx:03d}_0x{off:06x}"

            if block_data[:6] in (b'GIF87a', b'GIF89a'):
                fname = f"{prefix}.gif"
                fname = write_output(output_dir, fname, block_data)
                print(f"    0x{off:06x}: GIF image ({len(block_data)} bytes) -> {fname}")

            elif block_data[:2] == b'BM' and len(block_data) >= 54:
                w = struct.unpack_from('<i', block_data, 18)[0]
                h = struct.unpack_from('<i', block_data, 22)[0]
                bpp = struct.unpack_from('<H', block_data, 28)[0]
                fname = f"{prefix}_BMP_{w}x{h}_{bpp}bpp.bmp"
                fname = write_output(output_dir, fname, block_data)
                print(f"    0x{off:06x}: BMP {w}x{h} {bpp}bpp -> {fname}")

            elif len(block_data) > 6 and block_data[2:5] == b'PIG':
                platform = block_data[6:9].decode('ascii', errors='replace')
                candidate = find_best_dib_in_pig(block_data, with_offset=True)
                if candidate:
                    dib_offset, dib_data = candidate
                    if pig_bitmap_is_rendered(f'offset:{off}', dib_offset):
                        continue
                    bmp_data = make_bmp_from_dib(dib_data)
                    if bmp_data:
                        de = dib_endian(dib_data)
                        w = struct.unpack_from(f'{de}i', dib_data, 4)[0]
                        h = struct.unpack_from(f'{de}i', dib_data, 8)[0]
                        bpp = struct.unpack_from(f'{de}H', dib_data, 14)[0]
                        fname = f"{prefix}_PIG_{platform}_{w}x{h}_{bpp}bpp.bmp"
                        fname = write_output(output_dir, fname, bmp_data)
                        print(f"    0x{off:06x}: PIG/{platform} {w}x{h} {bpp}bpp -> {fname}")
                        extracted_count += 1
                        continue
                # Recognized PIGs already had their raw-export decision above.
                if f'offset:{off}' in pigs_by_index:
                    continue
                # Unrecognized PIG with no extractable bitmap - save raw.
                fname = f"{prefix}_PIG.bin"
                fname = write_output(output_dir, fname, block_data)
                print(f"    0x{off:06x}: PIG/{platform} ({len(block_data)} bytes, no extractable bitmap) -> {fname}")

            elif len(block_data) >= 40 and (struct.unpack_from('<I', block_data, 0)[0] == 40 or struct.unpack_from('>I', block_data, 0)[0] == 40):
                raw_name = write_output(output_dir, f'{prefix}.bin', block_data)
                print(f'    0x{off:06x}: original DIB bytes preserved -> {raw_name}')
                extracted_count += 1
                de = dib_endian(block_data)
                w = struct.unpack_from(f'{de}i', block_data, 4)[0]
                h = abs(struct.unpack_from(f'{de}i', block_data, 8)[0])
                planes = struct.unpack_from(f'{de}H', block_data, 12)[0]
                bpp = struct.unpack_from(f'{de}H', block_data, 14)[0]
                if 0 < w < 10000 and 0 < h < 10000 and planes == 1 and bpp in (1, 4, 8, 16, 24, 32):
                    bmp_data = make_bmp_from_dib(block_data)
                    if bmp_data:
                        fname = f"{prefix}_DIB_{w}x{h}_{bpp}bpp.bmp"
                        fname = write_output(output_dir, fname, bmp_data)
                        print(f"    0x{off:06x}: DIB {w}x{h} {bpp}bpp -> {fname}")
                        extracted_count += 1
                        continue
                # Without unambiguous colors and complete pixels, keep raw only.
                continue

            elif block_data[:4] == b'FORM':
                fname = f"{prefix}.aiff"
                fname = write_output(output_dir, fname, block_data)
                print(f"    0x{off:06x}: AIFF audio ({len(block_data)} bytes) -> {fname}")

            else:
                fname = f"{prefix}.bin"
                fname = write_output(output_dir, fname, block_data)
                print(f"    0x{off:06x}: {len(block_data)} bytes -> {fname}")

            extracted_count += 1

    if args.deep and pig_results:
        manifest = {'source': input_file, 'source_sha256': source_hash,
                    'pictures': [{key: value for key, value in result.items() if key not in ('svg', 'preview')}
                                 for result in pig_results]}
        fname = write_output(output_dir, 'pig_manifest.json', json.dumps(manifest, indent=2) + '\n')
        print(f'  PIG reconstruction details -> {fname}')
        extracted_count += 1
    if args.deep and dib_results:
        manifest = {'source': input_file, 'source_sha256': source_hash, 'dibs': dib_results}
        fname = write_output(output_dir, 'dib_manifest.json', json.dumps(manifest, indent=2) + '\n')
        print(f'  DIB references and export decisions -> {fname}')
        extracted_count += 1
    if args.deep and animation_results:
        manifest = {'source': input_file, 'source_sha256': source_hash, 'animations': animation_results}
        fname = write_output(output_dir, 'animation_manifest.json', json.dumps(manifest, indent=2) + '\n')
        print(f'  Animation reconstruction details -> {fname}')
        extracted_count += 1
    partial_notice = ('Extraction is partial; some content is missing, damaged, or could not be decoded'
                      if skipped_segment or incomplete_audio or decompression_failures else '')
    if make_report:
        from authorware_pig_report import collect_assets, report_html
        names = [name for name in os.listdir(output_dir) if name not in report_existing
                 and os.path.isfile(os.path.join(output_dir, name))]
        assets = collect_assets(output_dir, names, pig_results, dib_results, cursor_results, animation_results)
        fname = write_output(output_dir, 'pig-report.html',
                             report_html(input_file, source_hash, pig_results, assets, partial_notice))
        print(f'  Extraction review -> {fname}')
        extracted_count += 1

    if is_segment and skipped_segment > 0:
        print(f"\n  Segment file: {skipped_segment} entries skipped (data in other segments)")
    print(f"\nExtracted {extracted_count} items to {output_dir}")
    if partial_notice:
        print('Warning: ' + partial_notice, file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()

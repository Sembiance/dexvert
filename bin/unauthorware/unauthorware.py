#!/usr/bin/env python3
# vibe coded by claude code
"""
Authorware Packaged/Library File Extractor (.app/.apr/.apw/.asw/.aas/.a3m/.a3w/.a4p/.a5p/.a6p/.a7p/.a4r/.a5r/.a6r/.a7r)

Extracts images, text, scripts, and raw data from Macromedia Authorware
packaged files (ACRS), library files (PCRS), and v3 files (WCRS/A3M).

Usage: python3 unauthorware.py <inputFile> <outputDir>
"""

import sys
import os
import struct
import zlib

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


def read_header(data):
    """Parse the 64-byte file header."""
    if len(data) < 64:
        raise ValueError("File too small for header")
    if data[:4] not in (b'ACRS', b'PCRS', b'WCRS', b'WPCR', b'WPLI'):
        raise ValueError(f"Invalid magic: {data[:4]!r} (expected b'ACRS', b'PCRS', b'WCRS', b'WPCR', or b'WPLI')")
    if data[4:8] not in (b'\xbe\xbc\xad\xac', b'\xaf\xbc\xad\xac', b'\xa8\xbc\xad\xac', b'\xa8\xaf\xbc\xad', b'\xa8\xaf\xb3\xb6'):
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
    return hdr


def read_entries(data, hdr):
    """Parse the entry table (ACRS 30-byte records)."""
    entries = []
    table_off = hdr['table_offset']
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
        entry['data_offset'] = struct.unpack_from('<I', data, off + 24)[0]
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
    for i in range(hdr['entry_count']):
        off = table_off + i * 10
        if off + 10 > len(data):
            break
        entry = {}
        entry['data_offset'] = struct.unpack_from('<I', data, off)[0]
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


def detect_icon_type(entry_data):
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
    for i in range(hdr['entry_count']):
        off = table_off + i * 16
        if off + 16 > len(data):
            break
        entry = {}
        entry['id'] = struct.unpack_from(f'{endian}H', data, off)[0]
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
            entry['icon_type'] = detect_icon_type(data[off:off + min(sz, 64)])

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
            entry['icon_type'] = detect_icon_type(data[off:off + min(sz, 64)])

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
            entry['icon_type'] = detect_icon_type(data[off:off + min(sz, 64)])

    return entries


def decompress_entry(data, entry):
    """Decompress an entry's data."""
    off = entry['data_offset']
    comp_size = entry['comp_size']

    if comp_size == 0 and entry['decomp_size'] == 0:
        return None  # empty placeholder entry

    if off + comp_size > len(data):
        return None

    if entry['storage_type'] == 1:
        return data[off:off + comp_size]
    elif entry['storage_type'] == 2:
        try:
            obj = zlib.decompressobj()
            result = obj.decompress(data[off:off + comp_size + 256])
            return result[:entry['decomp_size']]
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


def make_bmp_from_dib(dib_data):
    """Create a full BMP file from raw DIB data (BITMAPINFOHEADER + palette + pixels)."""
    if len(dib_data) < 40:
        return None

    # Convert BE DIB to LE if needed
    if dib_endian(dib_data) == '>':
        dib_data = swap_dib_to_le(dib_data)

    hdr_size = struct.unpack_from('<I', dib_data, 0)[0]
    if hdr_size < 40:
        return None

    bpp = struct.unpack_from('<H', dib_data, 14)[0]

    if bpp <= 8:
        colors_used = struct.unpack_from('<I', dib_data, 32)[0]
        if colors_used == 0:
            colors_used = 1 << bpp
        palette_size = colors_used * 4
    else:
        palette_size = 0

    pixel_offset = 14 + hdr_size + palette_size
    file_size = 14 + len(dib_data)

    bmp_header = struct.pack('<2sIHHI', b'BM', file_size, 0, 0, pixel_offset)
    return bmp_header + dib_data


def dib_has_embedded_palette(pig_data, dib_offset):
    """Check if a DIB inside a PIG has its own palette or uses the PIG's shared one.

    PIG entries store a shared 256-color palette at offset 80 for WIN.
    The highest bpp DIB (8bpp) typically omits its own palette and uses
    the shared one, while lower bpp DIBs include their own.
    """
    if dib_offset + 44 > len(pig_data):
        return True  # assume it has one if we can't check
    endian = dib_endian(pig_data[dib_offset:dib_offset + 40])
    bpp = struct.unpack_from(f'{endian}H', pig_data, dib_offset + 14)[0]
    if bpp > 8:
        return False  # no palette needed

    # Check first 4 bytes after header - palette starts with RGBQUAD (B,G,R,0)
    # RLE data starts with run-length encoding (count, value pairs)
    # Heuristic: if 4th byte of first "RGBQUAD" is 0, likely palette
    after = pig_data[dib_offset + 40:dib_offset + 48]
    if len(after) < 8:
        return True

    # For 1bpp/4bpp palettes, the entries should have byte[3]=0 (reserved)
    # and reasonable RGB values. For 8bpp, check if the pixel data is RLE.
    if bpp == 8:
        # 8bpp inside PIG: check if what follows looks like RLE8 or raw pixels
        # RLE8 always starts with a count byte; if it's 0 it's an escape
        # Palette RGBQUAD has reserved byte = 0
        # Key insight: if byte at +43 (4th byte of first quad) is 0 AND
        # byte at +47 is also 0, it's likely a palette.
        # But the PIG shared palette already exists at offset 80, so
        # 8bpp DIBs in PIGs almost always use the shared palette.
        return False
    else:
        # 1bpp and 4bpp: include their own palette
        return True


def calc_dib_size(pig_data, offset, in_pig=False):
    """Calculate the total size of a DIB starting at offset."""
    if offset + 40 > len(pig_data):
        return 0
    endian = dib_endian(pig_data[offset:offset + 40])
    hdr_size = struct.unpack_from(f'{endian}I', pig_data, offset)[0]
    w = struct.unpack_from(f'{endian}i', pig_data, offset + 4)[0]
    h = abs(struct.unpack_from(f'{endian}i', pig_data, offset + 8)[0])
    bpp = struct.unpack_from(f'{endian}H', pig_data, offset + 14)[0]
    img_size = struct.unpack_from(f'{endian}I', pig_data, offset + 20)[0]
    colors_used = struct.unpack_from(f'{endian}I', pig_data, offset + 32)[0]

    if in_pig and not dib_has_embedded_palette(pig_data, offset):
        palette_size = 0
    elif bpp <= 8:
        if colors_used == 0:
            colors_used = 1 << bpp
        palette_size = colors_used * 4
    else:
        palette_size = 0

    if img_size > 0:
        pixel_size = img_size
    else:
        row_stride = ((w * bpp + 31) // 32) * 4
        pixel_size = row_stride * h

    return hdr_size + palette_size + pixel_size


def extract_pig_palette(pig_data):
    """Extract the shared 256-color palette from a WIN PIG entry."""
    if len(pig_data) < 80 + 1024:
        return None
    if pig_data[6:9] != b'WIN':
        return None
    return pig_data[80:80 + 1024]


def find_best_dib_in_pig(pig_data):
    """Find the highest quality embedded BITMAPINFOHEADER in a PIG entry."""
    dibs = []

    i = 0
    while i < len(pig_data) - 40:
        for endian in ('<', '>'):
            hdr_size = struct.unpack_from(f'{endian}I', pig_data, i)[0]
            if hdr_size == 40:
                w = struct.unpack_from(f'{endian}i', pig_data, i + 4)[0]
                h = struct.unpack_from(f'{endian}i', pig_data, i + 8)[0]
                planes = struct.unpack_from(f'{endian}H', pig_data, i + 12)[0]
                bpp = struct.unpack_from(f'{endian}H', pig_data, i + 14)[0]
                if 0 < w < 10000 and 0 < abs(h) < 10000 and planes == 1 and bpp in (1, 4, 8, 16, 24, 32):
                    dib_size = calc_dib_size(pig_data, i, in_pig=True)
                    if dib_size > 0 and i + dib_size <= len(pig_data):
                        has_palette = dib_has_embedded_palette(pig_data, i)
                        dibs.append((i, bpp, dib_size, has_palette))
                break  # don't check other endian if hdr_size == 40
        i += 1

    if not dibs:
        return None

    # Pick the highest bpp DIB that fits
    best = max(dibs, key=lambda x: x[1])
    offset, bpp, size, has_palette = best

    dib_header = pig_data[offset:offset + 40]
    dib_rest = pig_data[offset + 40:offset + size]

    if has_palette:
        # DIB has its own palette embedded - return as-is
        return dib_header + dib_rest
    else:
        # Need to insert the PIG's shared palette
        pig_palette = extract_pig_palette(pig_data)
        if pig_palette:
            return dib_header + pig_palette + dib_rest
        else:
            # No palette available - return raw (won't display correctly)
            return dib_header + dib_rest


def extract_pig_dimensions(pig_data):
    """Extract width/height from a WIN PIG header."""
    if len(pig_data) < 0x22:
        return None, None
    if pig_data[2:5] != b'PIG':
        return None, None
    platform = pig_data[6:9]
    if platform in (b'WIN', b'MAC'):
        # Try LE first, fall back to BE if dimensions look unreasonable
        w = struct.unpack_from('<H', pig_data, 0x1E)[0]
        h = struct.unpack_from('<H', pig_data, 0x20)[0]
        if w > 10000 or h > 10000:
            w = struct.unpack_from('>H', pig_data, 0x1E)[0]
            h = struct.unpack_from('>H', pig_data, 0x20)[0]
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

    elif icon_type in (0x05, 0x24):
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


def find_embedded_image_in_pig(pig_data):
    """Find a GIF, JPEG, or PNG image embedded inside a PIG entry.

    Returns (format, data) tuple or None. Some A5P PIGs embed GIF images
    instead of using BITMAPINFOHEADER sub-images.
    """
    for j in range(0, len(pig_data) - 6):
        if pig_data[j:j+6] in (b'GIF87a', b'GIF89a'):
            return ('gif', pig_data[j:])
        if pig_data[j:j+3] == b'\xff\xd8\xff':
            return ('jpeg', pig_data[j:])
        if pig_data[j:j+4] == b'\x89PNG':
            return ('png', pig_data[j:])
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


def make_wav(pcm_data, sample_rate=22050, bits_per_sample=8, channels=1):
    """Create a WAV file from raw PCM data."""
    byte_rate = sample_rate * channels * (bits_per_sample // 8)
    block_align = channels * (bits_per_sample // 8)
    data_size = len(pcm_data)
    file_size = 36 + data_size

    header = struct.pack('<4sI4s', b'RIFF', file_size, b'WAVE')
    fmt = struct.pack('<4sIHHIIHH', b'fmt ', 16, 1, channels,
                      sample_rate, byte_rate, block_align, bits_per_sample)
    data_hdr = struct.pack('<4sI', b'data', data_size)
    return header + fmt + data_hdr + pcm_data


def find_uncovered_zlib_blocks(data, hdr, entries):
    """Find zlib-compressed blocks not referenced by the entry table.

    Returns list of (file_offset, compressed_size, decompressed_data) tuples
    for blocks that contain unique data (not duplicates of entry data).
    """
    entry_table_bytes = hdr['entry_count'] * 30
    secondary_size = hdr['table_total_size'] - entry_table_bytes

    # Build set of covered byte offsets
    covered = set()
    # Header (0x00-0x3F) + preamble (0x40-0x57)
    for i in range(0x58):
        covered.add(i)
    # Small gap between preamble and first data/table (0x58 to whichever is first)
    first_data = min((e['data_offset'] for e in entries), default=hdr['table_offset'])
    gap_end = min(hdr['table_offset'], first_data)
    for i in range(0x58, min(gap_end, len(data))):
        covered.add(i)
    # Entry table
    for i in range(hdr['table_offset'], hdr['table_offset'] + entry_table_bytes):
        covered.add(i)
    # Secondary table
    sec_start = hdr['table_offset'] + entry_table_bytes
    for i in range(sec_start, sec_start + secondary_size):
        covered.add(i)
    # Entry data regions
    for e in entries:
        for i in range(e['data_offset'], e['data_offset'] + e['comp_size']):
            covered.add(i)

    # Decompress all entry data for duplicate detection
    entry_contents = set()
    for e in entries:
        edata = decompress_entry(data, e)
        if edata:
            entry_contents.add(edata)

    # Scan for uncovered zlib blocks
    blocks = []
    i = 0
    while i < len(data) - 2:
        if i not in covered:
            if data[i] == 0x78 and data[i + 1] in (0x01, 0x5E, 0x9C, 0xDA):
                try:
                    obj = zlib.decompressobj()
                    result = obj.decompress(data[i:])
                    consumed = len(data[i:]) - len(obj.unused_data)
                    # Skip duplicates and trivial all-zero blocks
                    if result not in entry_contents and result != b'\x00' * len(result):
                        blocks.append((i, consumed, result))
                    i += consumed
                    continue
                except zlib.error:
                    pass
        i += 1

    return blocks


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    with open(input_file, 'rb') as f:
        data = f.read()

    hdr = read_header(data)
    if hdr['magic'] in ('WPCR', 'WPLI') and hdr['flags'] & 0xFFFFFFFF == 0xFFFFFFFC:
        # WPCR/WPLI offset-only format: 4-byte offset list
        entries = read_entries_wpcr(data, hdr)
    elif hdr['magic'] in ('WCRS', 'WPCR', 'WPLI') and hdr['format_version'] == 2:
        # Authorware 2.x: 10-byte records at end of file
        entries = read_entries_wcrs_v2(data, hdr)
    elif hdr['magic'] in ('WCRS', 'WPCR', 'WPLI'):
        # WCRS/WPCR/WPLI: 16-byte records
        entries = read_entries_wcrs(data, hdr)
    elif hdr.get('big_endian'):
        # A3M: big-endian ACRS with 16-byte records (same structure as WCRS)
        entries = read_entries_wcrs(data, hdr)
    elif hdr['magic'] == 'PCRS' and hdr['entry_count'] * 30 > hdr['table_total_size']:
        entries = read_entries_pcrs(data, hdr)
    else:
        entries = read_entries(data, hdr)

    os.makedirs(output_dir, exist_ok=True)

    basename = os.path.splitext(os.path.basename(input_file))[0]

    print(f"File: {input_file}")
    print(f"  Format version: {hdr['format_version']}")
    print(f"  Entry count: {hdr['entry_count']}")
    print(f"  Entry table offset: 0x{hdr['table_offset']:x}")
    print(f"  File size: {hdr['file_size']}")
    print()

    extracted_count = 0
    audio_accum = None  # (start_eid, chunks) for combining consecutive 0x3C entries
    # Detect segment files (header file_size > actual data length)
    is_segment = hdr['file_size'] > len(data)
    skipped_segment = 0

    for entry in entries:
        eid = entry['id']
        icon_type = entry['icon_type']
        type_name = ICON_TYPE_NAMES.get(icon_type, f"Unknown_0x{icon_type:02x}")

        # Skip entries whose data is beyond or straddles this segment's bounds
        if is_segment and (entry['data_offset'] >= len(data) or entry['data_offset'] + entry['comp_size'] > len(data)):
            skipped_segment += 1
            continue

        entry_data = decompress_entry(data, entry)
        if entry_data is None:
            if entry['comp_size'] == 0 and entry['decomp_size'] == 0:
                continue  # silent skip for empty placeholder entries
            print(f"  Entry {eid:3d} ({type_name}): DECOMPRESS FAILED")
            continue

        # Extract based on type
        if icon_type == 0x3E:
            # Full BMP - extract directly
            if entry_data[:2] == b'BM':
                w = struct.unpack_from('<i', entry_data, 18)[0]
                h = struct.unpack_from('<i', entry_data, 22)[0]
                bpp = struct.unpack_from('<H', entry_data, 28)[0]
                fname = f"{eid:03d}_{type_name}_{w}x{h}_{bpp}bpp.bmp"
                fpath = os.path.join(output_dir, fname)
                with open(fpath, 'wb') as f:
                    f.write(entry_data)
                print(f"  Entry {eid:3d} ({type_name}): BMP {w}x{h} {bpp}bpp -> {fname}")
                extracted_count += 1

        elif icon_type == 0x35:
            # DIB data - convert to BMP
            bmp_data = make_bmp_from_dib(entry_data)
            if bmp_data:
                de = dib_endian(entry_data)
                w = struct.unpack_from(f'{de}i', entry_data, 4)[0]
                h = struct.unpack_from(f'{de}i', entry_data, 8)[0]
                bpp = struct.unpack_from(f'{de}H', entry_data, 14)[0]
                fname = f"{eid:03d}_{type_name}_{w}x{h}_{bpp}bpp.bmp"
                fpath = os.path.join(output_dir, fname)
                with open(fpath, 'wb') as f:
                    f.write(bmp_data)
                print(f"  Entry {eid:3d} ({type_name}): DIB {w}x{h} {bpp}bpp -> {fname}")
                extracted_count += 1

        elif icon_type == 0x34:
            # PIG - try to extract embedded bitmap
            if len(entry_data) >= 14 and entry_data[2:5] == b'PIG':
                platform = entry_data[6:9].decode('ascii', errors='replace')
                dib_data = find_best_dib_in_pig(entry_data)

                if dib_data:
                    bmp_data = make_bmp_from_dib(dib_data)
                    if bmp_data:
                        de = dib_endian(dib_data)
                        w = struct.unpack_from(f'{de}i', dib_data, 4)[0]
                        h = struct.unpack_from(f'{de}i', dib_data, 8)[0]
                        bpp = struct.unpack_from(f'{de}H', dib_data, 14)[0]
                        fname = f"{eid:03d}_{type_name}_{platform}_{w}x{h}_{bpp}bpp.bmp"
                        fpath = os.path.join(output_dir, fname)
                        with open(fpath, 'wb') as f:
                            f.write(bmp_data)
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
                    fpath = os.path.join(output_dir, fname)
                    with open(fpath, 'wb') as f:
                        f.write(img_data)
                    print(f"  Entry {eid:3d} ({type_name}): PIG/{platform}{dim_str} {img_fmt.upper()} ({len(img_data)} bytes) -> {fname}")
                    extracted_count += 1
                    continue

                # Check for text/script content in PIG
                pig_text = extract_pig_text(entry_data)
                if pig_text and len(pig_text) > 20:
                    fname = f"{eid:03d}_{type_name}_{platform}_text.txt"
                    fpath = os.path.join(output_dir, fname)
                    with open(fpath, 'w') as f:
                        f.write(pig_text)
                    print(f"  Entry {eid:3d} ({type_name}): PIG/{platform} text ({len(pig_text)} chars) -> {fname}")
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
                fpath = os.path.join(output_dir, fname)
                with open(fpath, 'w') as f:
                    f.write(text)
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
                fpath = os.path.join(output_dir, fname)
                with open(fpath, 'w') as f:
                    f.write(text)
                print(f"  Entry {eid:3d} ({type_name}): display text ({len(strings)} strings) -> {fname}")
                extracted_count += 1
            else:
                print(f"  Entry {eid:3d} ({type_name}): {len(entry_data)} bytes (no extractable text)")

        elif icon_type == 0xFFFD:
            # Plugin PIG - same handling as regular PIG (0x34)
            if len(entry_data) >= 14 and entry_data[2:5] == b'PIG':
                platform = entry_data[6:9].decode('ascii', errors='replace')
                dib_data = find_best_dib_in_pig(entry_data)
                if dib_data:
                    bmp_data = make_bmp_from_dib(dib_data)
                    if bmp_data:
                        de = dib_endian(dib_data)
                        w = struct.unpack_from(f'{de}i', dib_data, 4)[0]
                        h = struct.unpack_from(f'{de}i', dib_data, 8)[0]
                        bpp = struct.unpack_from(f'{de}H', dib_data, 14)[0]
                        fname = f"{eid:03d}_{type_name}_{platform}_{w}x{h}_{bpp}bpp.bmp"
                        fpath = os.path.join(output_dir, fname)
                        with open(fpath, 'wb') as f:
                            f.write(bmp_data)
                        print(f"  Entry {eid:3d} ({type_name}): PIG/{platform} {w}x{h} {bpp}bpp -> {fname}")
                        extracted_count += 1
                        continue
                print(f"  Entry {eid:3d} ({type_name}): PIG/{platform} ({len(entry_data)} bytes, no extractable bitmap)")
            else:
                fname = f"{eid:03d}_{type_name}.bin"
                fpath = os.path.join(output_dir, fname)
                with open(fpath, 'wb') as f:
                    f.write(entry_data)
                print(f"  Entry {eid:3d} ({type_name}): {len(entry_data)} bytes -> {fname}")
                extracted_count += 1

        elif icon_type == 0x3B:
            # Embedded media - can contain BMP, 3DMF models, or other data
            if entry_data[:2] == b'BM':
                w = struct.unpack_from('<i', entry_data, 18)[0]
                h = struct.unpack_from('<i', entry_data, 22)[0]
                bpp = struct.unpack_from('<H', entry_data, 28)[0]
                fname = f"{eid:03d}_{type_name}_{w}x{h}_{bpp}bpp.bmp"
                fpath = os.path.join(output_dir, fname)
                with open(fpath, 'wb') as f:
                    f.write(entry_data)
                print(f"  Entry {eid:3d} ({type_name}): BMP {w}x{h} {bpp}bpp -> {fname}")
            elif entry_data[:4] == b'3DMF':
                fname = f"{eid:03d}_{type_name}.3dmf"
                fpath = os.path.join(output_dir, fname)
                with open(fpath, 'wb') as f:
                    f.write(entry_data)
                print(f"  Entry {eid:3d} ({type_name}): 3DMF model ({len(entry_data)} bytes) -> {fname}")
            elif len(entry_data) > 15 and entry_data[12:15] in (b'FWS', b'CWS'):
                # SWF with 12-byte big-endian wrapper
                swf_data = entry_data[12:]
                fname = f"{eid:03d}_{type_name}.swf"
                fpath = os.path.join(output_dir, fname)
                with open(fpath, 'wb') as f:
                    f.write(swf_data)
                print(f"  Entry {eid:3d} ({type_name}): SWF ({len(swf_data)} bytes) -> {fname}")
            else:
                fname = f"{eid:03d}_{type_name}.bin"
                fpath = os.path.join(output_dir, fname)
                with open(fpath, 'wb') as f:
                    f.write(entry_data)
                print(f"  Entry {eid:3d} ({type_name}): {len(entry_data)} bytes -> {fname}")
            extracted_count += 1

        elif icon_type == 0x37:
            # Raw audio data - extract as WAV
            # Look for preceding 0x36 SoundHeader to get sample rate
            sample_rate = 22050  # default
            bits = 8
            channels = 1
            for prev in entries:
                if prev['id'] == eid - 1 and prev['icon_type'] == 0x36:
                    hdr_data = decompress_entry(data, prev)
                    if hdr_data and len(hdr_data) >= 42:
                        sample_rate = struct.unpack_from('<H', hdr_data, 40)[0]
                        if sample_rate == 0:
                            sample_rate = 22050
                        bits = hdr_data[27] if hdr_data[27] in (8, 16) else 8
                        channels = struct.unpack_from('<H', hdr_data, 4)[0]
                        if channels == 0:
                            channels = 1
                    break
            wav_data = make_wav(entry_data, sample_rate, bits, channels)
            fname = f"{eid:03d}_{type_name}_{sample_rate}hz_{bits}bit.wav"
            fpath = os.path.join(output_dir, fname)
            with open(fpath, 'wb') as f:
                f.write(wav_data)
            print(f"  Entry {eid:3d} ({type_name}): WAV {sample_rate}Hz {bits}bit {channels}ch ({len(entry_data)} samples) -> {fname}")
            extracted_count += 1

        elif icon_type == 0x3C:
            # Streaming audio - consecutive 0x3C entries form one file
            # Format varies: AIFF (FORM), WAV (RIFF), MP3 (0xFFFB/0xFFF3/0xFFFA/ID3)
            if audio_accum is None:
                audio_accum = (eid, [entry_data])
            else:
                audio_accum = (audio_accum[0], audio_accum[1] + [entry_data])
            # Check if next entry is also 0x3C; if not, flush now
            next_idx = entries.index(entry) + 1
            if next_idx >= len(entries) or entries[next_idx]['icon_type'] != 0x3C:
                start_eid = audio_accum[0]
                combined = b''.join(audio_accum[1])
                # Detect actual audio format from first chunk
                if combined[:4] == b'FORM':
                    ext, fmt_name = 'aiff', 'AIFF'
                elif combined[:4] == b'RIFF':
                    ext, fmt_name = 'wav', 'WAV'
                elif combined[:3] == b'ID3' or (len(combined) > 1 and combined[0] == 0xFF and combined[1] in (0xFB, 0xF3, 0xFA, 0xF2, 0xE2)):
                    ext, fmt_name = 'mp3', 'MP3'
                elif len(combined) > 0x26 and combined[:4] == b'\x00\x00\x00\x20' and combined[0x24] == 0xFF and (combined[0x25] & 0xE0) == 0xE0:
                    # 36-byte big-endian wrapper with audio metadata, MP3 data at offset 0x24
                    combined = combined[0x24:]
                    ext, fmt_name = 'mp3', 'MP3'
                else:
                    ext, fmt_name = 'bin', 'audio'
                fname = f"{start_eid:03d}_{type_name}.{ext}"
                fpath = os.path.join(output_dir, fname)
                with open(fpath, 'wb') as f:
                    f.write(combined)
                print(f"  Entry {start_eid:3d} ({type_name}): {fmt_name} ({len(combined)} bytes, {len(audio_accum[1])} chunks) -> {fname}")
                extracted_count += 1
                audio_accum = None

        else:
            # Other types - save raw decompressed data
            fname = f"{eid:03d}_{type_name}.bin"
            fpath = os.path.join(output_dir, fname)
            with open(fpath, 'wb') as f:
                f.write(entry_data)
            print(f"  Entry {eid:3d} ({type_name}): {len(entry_data)} bytes -> {fname}")
            extracted_count += 1

    # Extract unique uncovered zlib blocks (only for ACRS files with zlib compression)
    uncovered = find_uncovered_zlib_blocks(data, hdr, entries) if hdr['magic'] == 'ACRS' and not hdr.get('big_endian') else []
    if uncovered:
        print(f"\n  Unreferenced data blocks ({len(uncovered)}):")
        for idx, (off, comp_sz, block_data) in enumerate(uncovered):
            prefix = f"extra_{idx:03d}_0x{off:06x}"

            if block_data[:6] in (b'GIF87a', b'GIF89a'):
                fname = f"{prefix}.gif"
                fpath = os.path.join(output_dir, fname)
                with open(fpath, 'wb') as f:
                    f.write(block_data)
                print(f"    0x{off:06x}: GIF image ({len(block_data)} bytes) -> {fname}")

            elif block_data[:2] == b'BM' and len(block_data) > 14:
                w = struct.unpack_from('<i', block_data, 18)[0]
                h = struct.unpack_from('<i', block_data, 22)[0]
                bpp = struct.unpack_from('<H', block_data, 28)[0]
                fname = f"{prefix}_BMP_{w}x{h}_{bpp}bpp.bmp"
                fpath = os.path.join(output_dir, fname)
                with open(fpath, 'wb') as f:
                    f.write(block_data)
                print(f"    0x{off:06x}: BMP {w}x{h} {bpp}bpp -> {fname}")

            elif len(block_data) > 6 and block_data[2:5] == b'PIG':
                platform = block_data[6:9].decode('ascii', errors='replace')
                dib_data = find_best_dib_in_pig(block_data)
                if dib_data:
                    bmp_data = make_bmp_from_dib(dib_data)
                    if bmp_data:
                        de = dib_endian(dib_data)
                        w = struct.unpack_from(f'{de}i', dib_data, 4)[0]
                        h = struct.unpack_from(f'{de}i', dib_data, 8)[0]
                        bpp = struct.unpack_from(f'{de}H', dib_data, 14)[0]
                        fname = f"{prefix}_PIG_{platform}_{w}x{h}_{bpp}bpp.bmp"
                        fpath = os.path.join(output_dir, fname)
                        with open(fpath, 'wb') as f:
                            f.write(bmp_data)
                        print(f"    0x{off:06x}: PIG/{platform} {w}x{h} {bpp}bpp -> {fname}")
                        extracted_count += 1
                        continue
                # PIG with no extractable bitmap - save raw
                fname = f"{prefix}_PIG.bin"
                fpath = os.path.join(output_dir, fname)
                with open(fpath, 'wb') as f:
                    f.write(block_data)
                print(f"    0x{off:06x}: PIG/{platform} ({len(block_data)} bytes, no extractable bitmap) -> {fname}")

            elif len(block_data) >= 40 and (struct.unpack_from('<I', block_data, 0)[0] == 40 or struct.unpack_from('>I', block_data, 0)[0] == 40):
                de = dib_endian(block_data)
                w = struct.unpack_from(f'{de}i', block_data, 4)[0]
                h = abs(struct.unpack_from(f'{de}i', block_data, 8)[0])
                planes = struct.unpack_from(f'{de}H', block_data, 12)[0]
                bpp = struct.unpack_from(f'{de}H', block_data, 14)[0]
                if 0 < w < 10000 and 0 < h < 10000 and planes == 1 and bpp in (1, 4, 8, 16, 24, 32):
                    bmp_data = make_bmp_from_dib(block_data)
                    if bmp_data:
                        fname = f"{prefix}_DIB_{w}x{h}_{bpp}bpp.bmp"
                        fpath = os.path.join(output_dir, fname)
                        with open(fpath, 'wb') as f:
                            f.write(bmp_data)
                        print(f"    0x{off:06x}: DIB {w}x{h} {bpp}bpp -> {fname}")
                        extracted_count += 1
                        continue
                # Not a valid DIB - save raw
                fname = f"{prefix}.bin"
                fpath = os.path.join(output_dir, fname)
                with open(fpath, 'wb') as f:
                    f.write(block_data)
                print(f"    0x{off:06x}: {len(block_data)} bytes -> {fname}")

            elif block_data[:4] == b'FORM':
                fname = f"{prefix}.aiff"
                fpath = os.path.join(output_dir, fname)
                with open(fpath, 'wb') as f:
                    f.write(block_data)
                print(f"    0x{off:06x}: AIFF audio ({len(block_data)} bytes) -> {fname}")

            else:
                fname = f"{prefix}.bin"
                fpath = os.path.join(output_dir, fname)
                with open(fpath, 'wb') as f:
                    f.write(block_data)
                print(f"    0x{off:06x}: {len(block_data)} bytes -> {fname}")

            extracted_count += 1

    if is_segment and skipped_segment > 0:
        print(f"\n  Segment file: {skipped_segment} entries skipped (data in other segments)")
    print(f"\nExtracted {extracted_count} items to {output_dir}")


if __name__ == '__main__':
    main()

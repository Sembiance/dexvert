# Vibe coded by Codex
"""Root-referenced legacy cursor tables, rendered as transparent PNGs."""

import struct

from authorware_pig import legacy_project_root, png_rgba, word


def referenced_tables(context, endian):
    """Return unambiguous entry indices and their root-declared cursor size.

    Cursor-like bytes alone are insufficient to classify an unrelated entry.
    These slots belong to the recognized legacy root, not every file version.
    """
    roots = context.by_id.get(1, [])
    if len(roots) != 1:
        return {}
    root = context.entry(roots[0]) or b''
    if legacy_project_root(root, endian) is None:
        return {}
    candidates = {}
    for offset, size in ((0x30, 32), (0x34, 16)):
        resource_id = word(root, offset, endian)
        indices = context.by_id.get(resource_id, []) if resource_id else []
        if len(indices) != 1 or indices[0] == roots[0]:
            continue
        index = indices[0]
        if context.entries[index]['icon_type'] not in (0x06, 0x18, 0x1A):
            continue
        candidates.setdefault(index, []).append(size)
    # One entry referenced as two different sizes is not an established layout.
    return {index: sizes[0] for index, sizes in candidates.items() if len(sizes) == 1}


def decode_table(data, size, endian):
    """Validate every record through the terminator before omitting the original.

    Key/length records end with a zero key. The observed allocations include
    unused tails containing old memory rather than zeros; their lengths vary
    even for identical cursor records. Only bytes before the terminator belong
    to the table. Unknown depths, dimensions and record extensions keep their
    raw fallback.
    """
    if size not in (16, 32) or endian not in ('<', '>'):
        raise ValueError('Unsupported cursor table layout')
    cursors = []
    offset = 0
    while offset + 2 <= len(data):
        cursor_id = word(data, offset, endian)
        offset += 2
        if cursor_id == 0:
            if not cursors:
                raise ValueError('Empty cursor table')
            return cursors
        if offset + 2 > len(data):
            raise ValueError('Truncated cursor record length')
        length = word(data, offset, endian)
        offset += 2
        end = offset + length
        if end > len(data) or length < 12:
            raise ValueError('Truncated cursor record')
        record = data[offset:end]
        width, height, planes = struct.unpack_from(endian + '3H', record, 6)
        if (width, height, planes) != (size, size, 1):
            raise ValueError('Unsupported cursor dimensions or bit depth')
        stride = size // 8
        plane_size = stride * size
        minimum = 12 + 2 * plane_size
        if not minimum <= length <= minimum + 32:
            raise ValueError('Incomplete cursor planes or unsupported record extension')
        first = record[12:12 + plane_size]
        second = record[12 + plane_size:minimum]
        rows = []
        inverted = 0
        for y in range(size):
            row = bytearray()
            for x in range(size):
                position = y * stride + x // 8
                mask = 1 << (7 - x % 8)
                a, b = bool(first[position] & mask), bool(second[position] & mask)
                if size == 16:  # QuickDraw bitmap, then mask; top-down rows.
                    color, opaque, invert = (0 if a else 255), b, a and not b
                else:  # Windows AND plane, then XOR plane; top-down rows.
                    color, opaque, invert = (255 if b else 0), not a, a and b
                if invert:
                    # PNG cannot invert the screen beneath a cursor. Keep the
                    # pixel visible as black rather than losing it to alpha.
                    color, opaque = 0, True
                    inverted += 1
                row.extend((color, color, color, 255 if opaque else 0))
            rows.append(row)
        cursors.append({'cursor_id': cursor_id, 'width': size, 'height': size,
                        'inverting_pixels': inverted, 'png': png_rgba(size, size, rows)})
        offset = end + (length & 1)
        if offset > len(data):
            raise ValueError('Truncated cursor record padding')
    raise ValueError('Missing cursor table terminator')

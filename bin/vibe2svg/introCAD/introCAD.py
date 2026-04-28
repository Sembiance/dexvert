# Vibe coded by Claude
# IntroCAD to SVG converter
# Converts IntroCAD vector drawing files to SVG format

import struct
import sys
import os
import math

MAGIC = b'\x00\x12\xD6\x44'

PALETTE = [
    "#0055AA",  # 0  dark blue (Amiga background)
    "#000000",  # 1  black
    "#DD0000",  # 2  red
    "#FF8800",  # 3  orange
    "#0000CC",  # 4  blue
    "#00AA00",  # 5  green
    "#CC00CC",  # 6  magenta
    "#AAAA00",  # 7  dark yellow
    "#00AAAA",  # 8  teal
    "#8800CC",  # 9  purple
    "#CC4400",  # 10 brown-red
    "#448800",  # 11 olive
    "#006688",  # 12 dark cyan
    "#884400",  # 13 brown
    "#880088",  # 14 dark magenta
    "#666666",  # 15 gray
]

DASH_PATTERNS = {
    0: None,
    1: "4,4",
    2: "8,4",
    3: "8,4,2,4",
    4: "2,4",
    5: "2,8",
    6: "12,4,4,4",
}


def decode_mffp(data, offset):
    """Decode a 4-byte Motorola Fast Floating Point value (big-endian on disk)."""
    val = int.from_bytes(data[offset:offset + 4], 'big')
    if val == 0:
        return 0.0
    mantissa = (val >> 8) & 0xFFFFFF
    sign = (val >> 7) & 1
    exponent = val & 0x7F
    result = mantissa * (2.0 ** (exponent - 88))
    if sign:
        result = -result
    return result


def parse_introcad(filepath):
    """Parse an IntroCAD file. Returns list of records or raises ValueError."""
    with open(filepath, 'rb') as f:
        data = f.read()

    if len(data) < 4:
        raise ValueError("File too small")
    if data[:4] != MAGIC:
        raise ValueError("Invalid magic bytes")

    records = []
    offset = 4

    while offset < len(data):
        if offset + 6 > len(data):
            raise ValueError(f"Truncated record header at offset {offset}")

        npoints = data[offset]
        color = data[offset + 1]
        line_style = data[offset + 2]
        fill_flag = data[offset + 3]
        flag_b4 = data[offset + 4]
        flag_b5 = data[offset + 5]

        needed = 6 + npoints * 8
        if offset + needed > len(data):
            raise ValueError(
                f"Truncated coordinate data at offset {offset}: "
                f"need {needed} bytes, have {len(data) - offset}"
            )

        points = []
        for i in range(npoints):
            coff = offset + 6 + i * 8
            x = decode_mffp(data, coff)
            y = -decode_mffp(data, coff + 4)
            points.append((x, y))

        records.append({
            'npoints': npoints,
            'color': color,
            'line_style': line_style,
            'fill_flag': fill_flag,
            'flag_b4': flag_b4,
            'flag_b5': flag_b5,
            'points': points,
        })

        offset += needed

    return records


def records_to_svg(records, margin_pct=0.02):
    """Convert parsed records to SVG string."""
    valid_records = [r for r in records if r['npoints'] > 0 and r['color'] <= 15]

    if not valid_records:
        all_pts = [(x, y) for r in records for (x, y) in r['points']
                   if r['npoints'] > 0 and abs(x) < 1e10 and abs(y) < 1e10]
        if not all_pts:
            return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"></svg>'
        valid_records = [r for r in records if r['npoints'] > 0]

    all_x = []
    all_y = []
    for r in valid_records:
        for x, y in r['points']:
            if abs(x) < 1e10 and abs(y) < 1e10:
                all_x.append(x)
                all_y.append(y)

    if not all_x:
        return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"></svg>'

    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)

    width = max_x - min_x
    height = max_y - min_y

    if width < 1e-6:
        width = 1.0
    if height < 1e-6:
        height = 1.0

    margin_x = width * margin_pct
    margin_y = height * margin_pct
    vb_x = min_x - margin_x
    vb_y = min_y - margin_y
    vb_w = width + 2 * margin_x
    vb_h = height + 2 * margin_y

    svg_w = 800
    svg_h = int(800 * vb_h / vb_w) if vb_w > 0 else 800
    if svg_h < 100:
        svg_h = 100
    if svg_h > 4000:
        svg_h = 4000

    stroke_w = max(width, height) * 0.002

    lines = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
                 f'width="{svg_w}" height="{svg_h}" '
                 f'viewBox="{vb_x} {vb_y} {vb_w} {vb_h}">')
    lines.append(f'<rect x="{vb_x}" y="{vb_y}" width="{vb_w}" height="{vb_h}" fill="white"/>')

    for r in valid_records:
        if r['npoints'] < 1:
            continue

        color_idx = r['color'] % len(PALETTE)
        color = PALETTE[color_idx]
        pts = r['points']
        ls = r['line_style']

        if any(abs(x) > 1e10 or abs(y) > 1e10 for x, y in pts):
            continue

        if r['npoints'] == 1:
            x, y = pts[0]
            r_size = stroke_w * 1.5
            lines.append(f'<circle cx="{x}" cy="{y}" r="{r_size}" fill="{color}"/>')
            continue

        is_closed = (len(pts) >= 3 and
                     abs(pts[0][0] - pts[-1][0]) < 1e-4 and
                     abs(pts[0][1] - pts[-1][1]) < 1e-4)

        points_str = " ".join(f"{x},{y}" for x, y in pts)

        style_parts = [f'fill="none" stroke="{color}"']
        style_parts.append(f'stroke-width="{stroke_w}"')
        style_parts.append('stroke-linecap="round"')
        style_parts.append('stroke-linejoin="round"')

        dash = DASH_PATTERNS.get(ls)
        if dash:
            scaled_dash = ",".join(
                str(float(v) * stroke_w * 3) for v in dash.split(",")
            )
            style_parts.append(f'stroke-dasharray="{scaled_dash}"')

        style = " ".join(style_parts)

        if is_closed:
            lines.append(f'<polygon points="{points_str}" {style}/>')
        else:
            lines.append(f'<polyline points="{points_str}" {style}/>')

    lines.append('</svg>')
    return "\n".join(lines)


def convert(input_path, output_path):
    """Convert an IntroCAD file to SVG."""
    try:
        records = parse_introcad(input_path)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    svg = records_to_svg(records)

    with open(output_path, 'w') as f:
        f.write(svg)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputFile>", file=sys.stderr)
        sys.exit(1)

    convert(sys.argv[1], sys.argv[2])

#!/usr/bin/env python3
# Vibe coded by Claude

import struct
import sys
import math
import os

MAGIC = b'ACW RFW\x00'

DEFAULT_PALETTE_16 = [
    (0x00, 0x00, 0x00),  # 0: black
    (0x00, 0x00, 0xAA),  # 1: dark blue
    (0x00, 0xAA, 0x00),  # 2: green
    (0x00, 0xAA, 0xAA),  # 3: cyan
    (0xAA, 0x00, 0x00),  # 4: red
    (0xAA, 0x00, 0xAA),  # 5: magenta
    (0xAA, 0x55, 0x00),  # 6: brown
    (0xAA, 0xAA, 0xAA),  # 7: light gray
    (0x55, 0x55, 0x55),  # 8: dark gray
    (0x55, 0x55, 0xFF),  # 9: bright blue
    (0x55, 0xFF, 0x55),  # 10: bright green
    (0x55, 0xFF, 0xFF),  # 11: bright cyan
    (0xFF, 0x55, 0x55),  # 12: bright red
    (0xFF, 0x55, 0xFF),  # 13: bright magenta
    (0xFF, 0xFF, 0x55),  # 14: yellow
    (0xFF, 0xFF, 0xFF),  # 15: white
]

VALID_RECORD_TYPES = set(range(0x08, 0x21))


def rgb_hex(palette, idx):
    if idx < 0 or idx >= len(palette):
        idx = 0
    r, g, b = palette[idx]
    return f'#{r:02x}{g:02x}{b:02x}'


def is_valid_record_start(data, pos, end):
    if pos + 12 > end:
        return False
    rtype = struct.unpack_from('<H', data, pos)[0]
    const = struct.unpack_from('<H', data, pos + 2)[0]
    if rtype not in VALID_RECORD_TYPES:
        return False
    if const in (0x0010, 0x0011):
        return True
    if const == 0x0090 and rtype == 0x10:
        return True
    return False


def is_record_start_relaxed(data, pos, end):
    if pos + 12 > end:
        return False
    rtype = struct.unpack_from('<H', data, pos)[0]
    const = struct.unpack_from('<H', data, pos + 2)[0]
    if rtype not in VALID_RECORD_TYPES:
        return False
    if const in (0x0000, 0x0010, 0x0011):
        return True
    if const == 0x0090 and rtype == 0x10:
        return True
    return False


def scan_next_record(data, pos, end):
    for s in range(pos, min(pos + 30000, end - 3)):
        if is_valid_record_start(data, s, end):
            return s
    return end


def parse_pmd(data):
    if len(data) < 0x60 or data[:8] != MAGIC:
        return None

    version = struct.unpack_from('<H', data, 0x0A)[0]
    subtype = struct.unpack_from('<H', data, 0x16)[0]
    font_count = struct.unpack_from('<H', data, 0x3C)[0]
    page_count = struct.unpack_from('<H', data, 0x3E)[0]

    if page_count == 0 or page_count > 200:
        return None

    page_offsets = []
    for i in range(page_count):
        off = struct.unpack_from('<i', data, 0x60 + i * 4)[0]
        page_offsets.append(off)

    font_start = 0x60 + page_count * 4
    fonts = []
    for i in range(font_count):
        name_bytes = data[font_start + i * 32: font_start + (i + 1) * 32]
        name = name_bytes.split(b'\x00')[0].decode('ascii', errors='replace')
        fonts.append(name)

    palette = list(DEFAULT_PALETTE_16)
    if subtype == 0x0210 and version >= 0x19:
        post_font = font_start + font_count * 32
        pal_search_start = post_font + 16
        if pal_search_start + 256 <= len(data):
            for i in range(64):
                r = data[pal_search_start + i * 4]
                g = data[pal_search_start + i * 4 + 1]
                b = data[pal_search_start + i * 4 + 2]
                if i < len(palette):
                    palette[i] = (r, g, b)
                else:
                    palette.append((r, g, b))

    while len(palette) < 64:
        palette.append((0, 0, 0))

    sorted_abs = sorted(set(abs(o) for o in page_offsets))

    pages = []
    for pidx in range(page_count):
        raw_off = page_offsets[pidx]
        abs_off = abs(raw_off)
        is_index = raw_off < 0

        if abs_off >= len(data) or abs_off + 79 > len(data):
            continue

        ne = data.find(b'\x00', abs_off, abs_off + 79)
        if ne < 0:
            continue
        page_name = data[abs_off:ne].decode('ascii', errors='replace')

        rec_start = abs_off + 79
        idx_in_sorted = sorted_abs.index(abs_off)
        if idx_in_sorted + 1 < len(sorted_abs):
            page_end = sorted_abs[idx_in_sorted + 1]
        else:
            page_end = len(data)

        records = parse_records(data, rec_start, page_end)
        pages.append({
            'name': page_name,
            'is_index': is_index,
            'records': records,
        })

    return {
        'version': version,
        'subtype': subtype,
        'fonts': fonts,
        'palette': palette,
        'pages': pages,
        'page_count': page_count,
    }


def record_size(data, pos, end):
    rtype = struct.unpack_from('<H', data, pos)[0]

    if rtype == 0x0B:
        return 74
    if rtype == 0x0D:
        return 40
    if rtype == 0x0E:
        return 72
    if rtype == 0x12:
        return 36
    if rtype == 0x10:
        return 76

    if rtype == 0x0A:
        if pos + 92 > end:
            return end - pos
        str_len = struct.unpack_from('<H', data, pos + 90)[0]
        return 96 + str_len

    if rtype == 0x0C:
        if pos + 76 > end:
            return end - pos
        count = struct.unpack_from('<H', data, pos + 74)[0]
        calc = 80 + count * 4
        if pos + calc <= end:
            return calc
        return end - pos

    if rtype == 0x0F:
        if pos + 150 <= end and is_valid_record_start(data, pos + 150, end):
            return 150
        if pos + 144 <= end and is_valid_record_start(data, pos + 144, end):
            return 144

    nxt = scan_next_record(data, pos + 12, end)
    return nxt - pos


def parse_records(data, start, end):
    records = []
    pos = start
    while pos < end - 4:
        if not is_record_start_relaxed(data, pos, end):
            nxt = scan_next_record(data, pos + 1, end)
            if nxt >= end:
                break
            pos = nxt
            continue

        rtype = struct.unpack_from('<H', data, pos)[0]
        size = record_size(data, pos, end)

        if pos + size > end:
            size = end - pos

        rec_data = data[pos:pos + size]
        rec = parse_record(rtype, rec_data)
        if rec:
            records.append(rec)

        pos += size

    return records


def parse_record(rtype, data):
    if len(data) < 12:
        return None
    if rtype == 0x0B:
        return parse_polygon(data)
    if rtype == 0x0D:
        return parse_rectangle(data)
    if rtype == 0x0E:
        return parse_ellipse(data)
    if rtype == 0x0A:
        return parse_text(data)
    if rtype == 0x0C:
        return parse_curve(data)
    if rtype == 0x0F:
        return parse_arc(data)
    return {'type': rtype}


def parse_style(data, offset):
    if offset + 12 > len(data):
        return {}
    words = struct.unpack_from('<6H', data, offset)
    return {
        'bg_color': words[0],
        'fg_color': words[1],
        'line_style': words[2],
        'fill_bg': words[3],
        'fill_fg': words[4],
        'fill_pattern': words[5],
    }


def parse_polygon(data):
    if len(data) < 74:
        return None
    style = parse_style(data, 12)
    lw = struct.unpack_from('<H', data, 24)[0]
    points = []
    for i in range(12):
        x, y = struct.unpack_from('<HH', data, 26 + i * 4)
        points.append((x, y))
    return {'type': 0x0B, 'style': style, 'line_width': lw, 'points': points}


def parse_rectangle(data):
    if len(data) < 40:
        return None
    style = parse_style(data, 12)
    coords = []
    for i in range(4):
        x, y = struct.unpack_from('<HH', data, 24 + i * 4)
        coords.append((x, y))
    return {'type': 0x0D, 'style': style, 'corners': coords}


def parse_ellipse(data):
    if len(data) < 72:
        return None
    style = parse_style(data, 12)
    cx, cy = struct.unpack_from('<HH', data, 24)
    rx, ry = struct.unpack_from('<HH', data, 28)
    transform = [struct.unpack_from('<d', data, 32 + i * 8)[0] for i in range(4)]
    ox = struct.unpack_from('<i', data, 64)[0]
    oy = struct.unpack_from('<i', data, 68)[0]
    return {
        'type': 0x0E, 'style': style,
        'center': (cx, cy), 'corner': (rx, ry),
        'transform': transform, 'offset': (ox, oy),
    }


def parse_text(data):
    if len(data) < 96:
        return None
    font_idx = struct.unpack_from('<H', data, 12)[0]
    font_size = struct.unpack_from('<H', data, 14)[0]
    color = struct.unpack_from('<H', data, 16)[0]
    transform = [struct.unpack_from('<d', data, 50 + i * 8)[0] for i in range(4)]
    px = struct.unpack_from('<i', data, 82)[0]
    py = struct.unpack_from('<i', data, 86)[0]
    str_len = struct.unpack_from('<H', data, 90)[0]
    text_end = min(96 + str_len - 1, len(data))
    text = data[96:text_end].decode('ascii', errors='replace').rstrip('\x00')
    return {
        'type': 0x0A, 'font_idx': font_idx, 'font_size': font_size,
        'color': color, 'transform': transform, 'position': (px, py), 'text': text,
    }


def parse_curve(data):
    if len(data) < 80:
        return None
    style = parse_style(data, 12)
    lw = struct.unpack_from('<H', data, 28)[0]

    start_cap = [struct.unpack_from('<HH', data, 30 + i * 4) for i in range(5)]
    end_cap = [struct.unpack_from('<HH', data, 50 + i * 4) for i in range(5)]

    count = struct.unpack_from('<H', data, 74)[0]
    points = []
    for i in range(count):
        off = 80 + i * 4
        if off + 4 > len(data):
            break
        x, y = struct.unpack_from('<HH', data, off)
        points.append((x, y))

    return {
        'type': 0x0C, 'style': style, 'line_width': lw,
        'start_cap': start_cap, 'end_cap': end_cap, 'points': points,
    }


def parse_arc(data):
    if len(data) < 40:
        return None
    style = parse_style(data, 12)
    points = []
    off = 24
    while off + 4 <= min(len(data), 70):
        x, y = struct.unpack_from('<HH', data, off)
        if x < 60000 and y < 60000:
            points.append((x, y))
        off += 4

    has_transform = False
    transform = [1.0, 0.0, 0.0, 1.0]
    for scan in range(60, len(data) - 32):
        try:
            d = struct.unpack_from('<d', data, scan)[0]
            if abs(d - 1.0) < 0.0001:
                t = [struct.unpack_from('<d', data, scan + i * 8)[0] for i in range(4)]
                if all(abs(v) < 100 for v in t):
                    transform = t
                    has_transform = True
                    break
        except (struct.error, OverflowError):
            pass

    return {
        'type': 0x0F, 'style': style, 'points': points,
        'transform': transform, 'has_transform': has_transform,
    }


def collect_points(rec):
    pts = []
    rtype = rec.get('type')
    if rtype == 0x0B:
        pts = rec.get('points', [])
    elif rtype == 0x0D:
        pts = rec.get('corners', [])
    elif rtype == 0x0E:
        cx, cy = rec.get('center', (0, 0))
        rx, ry = rec.get('corner', (0, 0))
        ox, oy = rec.get('offset', (0, 0))
        actual_cx = cx + ox
        actual_cy = cy + oy
        rad_x = abs(rx - cx)
        rad_y = abs(ry - cy)
        pts = [(actual_cx - rad_x, actual_cy - rad_y),
               (actual_cx + rad_x, actual_cy + rad_y)]
    elif rtype == 0x0C:
        pts = rec.get('points', [])
    elif rtype == 0x0F:
        pts = rec.get('points', [])
    elif rtype == 0x0A:
        px, py = rec.get('position', (0, 0))
        if px > 0 and py > 0:
            pts = [(px, py)]
    return [(x, y) for x, y in pts if 0 < x < 60000 and 0 < y < 60000]


def compute_bounds(records):
    min_x, min_y = float('inf'), float('inf')
    max_x, max_y = 0, 0

    for rec in records:
        for x, y in collect_points(rec):
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x)
            max_y = max(max_y, y)

    if min_x == float('inf'):
        return 0, 0, 10000, 10000
    margin = max((max_x - min_x) * 0.02, (max_y - min_y) * 0.02, 100)
    return (max(0, min_x - margin), max(0, min_y - margin),
            max_x + margin, max_y + margin)


def escape_xml(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def flip_y(y, canvas_h):
    return canvas_h - y


def render_page_svg(page, palette, fonts):
    records = page['records']
    if not records:
        return None

    min_x, min_y, max_x, max_y = compute_bounds(records)
    width = max_x - min_x
    height = max_y - min_y
    if width <= 0 or height <= 0:
        return None

    svg_w = min(800, width)
    svg_h = svg_w * height / width
    base_stroke = max(width, height) * 0.003

    svg_parts = []
    svg_parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
                     f'viewBox="{min_x:.0f} {min_y:.0f} {width:.0f} {height:.0f}" '
                     f'width="{svg_w:.0f}" height="{svg_h:.0f}">')
    svg_parts.append(f'<rect x="{min_x}" y="{min_y}" width="{width}" height="{height}" fill="white"/>')

    canvas_h = max_y + min_y
    for rec in records:
        svg_el = render_record(rec, palette, fonts, canvas_h, base_stroke)
        if svg_el:
            svg_parts.append(svg_el)

    svg_parts.append('</svg>')
    return '\n'.join(svg_parts)


def get_fill_stroke(style, palette):
    fg_color = style.get('fg_color', 0)
    fill_fg = style.get('fill_fg', 0)
    fill_pattern = style.get('fill_pattern', 0)

    stroke_color = rgb_hex(palette, fg_color)
    if fg_color < len(palette):
        r, g, b = palette[fg_color]
        if r > 240 and g > 240 and b > 240:
            stroke_color = '#000000'

    fill_color = 'none'
    if fill_pattern >= 1:
        fill_color = rgb_hex(palette, fill_fg)
        if fill_fg < len(palette):
            r, g, b = palette[fill_fg]
            if r > 240 and g > 240 and b > 240:
                fill_color = '#000000'

    return stroke_color, fill_color


def render_record(rec, palette, fonts, canvas_h, base_stroke=20):
    rtype = rec.get('type')
    style = rec.get('style', {})

    if rtype == 0x0B:
        points = rec.get('points', [])
        if len(points) < 12:
            return None
        stroke, fill = get_fill_stroke(style, palette)
        x1, y1 = points[10]
        x2, y2 = points[11]
        fy1 = flip_y(y1, canvas_h)
        fy2 = flip_y(y2, canvas_h)
        return f'<line x1="{x1}" y1="{fy1:.0f}" x2="{x2}" y2="{fy2:.0f}" stroke="{stroke}" stroke-width="{base_stroke:.1f}"/>'

    elif rtype == 0x0D:
        corners = rec.get('corners', [])
        if len(corners) < 4:
            return None
        x1, y1 = corners[0]
        x2, y2 = corners[2]
        rx = min(x1, x2)
        ry = min(y1, y2)
        rw = abs(x2 - x1)
        rh = abs(y2 - y1)
        fy1 = flip_y(max(y1, y2), canvas_h)
        stroke, fill = get_fill_stroke(style, palette)
        return f'<rect x="{rx}" y="{fy1:.0f}" width="{rw}" height="{rh}" stroke="{stroke}" stroke-width="{base_stroke:.1f}" fill="{fill}"/>'

    elif rtype == 0x0E:
        cx, cy = rec.get('center', (0, 0))
        corner_x, corner_y = rec.get('corner', (0, 0))
        ox, oy = rec.get('offset', (0, 0))
        transform = rec.get('transform', [1, 0, 0, 1])
        actual_cx = cx + ox
        actual_cy = cy + oy
        rad_x = abs(corner_x - cx)
        rad_y = abs(corner_y - cy)
        if rad_x == 0 and rad_y == 0:
            return None
        fy = flip_y(actual_cy, canvas_h)
        stroke, fill = get_fill_stroke(style, palette)
        t = transform
        has_transform = (len(t) >= 4 and
                         (abs(t[0] - 1.0) > 0.001 or abs(t[1]) > 0.001 or
                          abs(t[2]) > 0.001 or abs(t[3] - 1.0) > 0.001))
        if has_transform:
            return (f'<ellipse cx="0" cy="0" rx="{rad_x}" ry="{rad_y}" '
                    f'stroke="{stroke}" stroke-width="{base_stroke:.1f}" fill="{fill}" '
                    f'transform="matrix({t[0]:.6f},{-t[2]:.6f},{-t[1]:.6f},{t[3]:.6f},{actual_cx:.0f},{fy:.0f})"/>')
        return (f'<ellipse cx="{actual_cx}" cy="{fy:.0f}" rx="{rad_x}" ry="{rad_y}" '
                f'stroke="{stroke}" stroke-width="{base_stroke:.1f}" fill="{fill}"/>')

    elif rtype == 0x0A:
        text = rec.get('text', '')
        if not text:
            return None
        px, py = rec.get('position', (0, 0))
        font_size = rec.get('font_size', 12)
        color = rec.get('color', 0)
        transform = rec.get('transform', [1, 0, 0, 1])
        if font_size == 0:
            font_size = 12
        text_color = rgb_hex(palette, color)
        if color < len(palette):
            r, g, b = palette[color]
            if r > 240 and g > 240 and b > 240:
                text_color = '#000000'
        fy = flip_y(py, canvas_h)
        t = transform
        has_transform = (len(t) >= 4 and
                         (abs(t[0] - 1.0) > 0.001 or abs(t[1]) > 0.001 or
                          abs(t[2]) > 0.001 or abs(t[3] - 1.0) > 0.001))
        scale = font_size * 1.33
        escaped = escape_xml(text)
        if has_transform:
            return (f'<text x="0" y="0" font-size="{scale:.1f}" fill="{text_color}" '
                    f'font-family="sans-serif" '
                    f'transform="translate({px},{fy:.0f}) matrix({t[0]:.4f},{-t[2]:.4f},{-t[1]:.4f},{t[3]:.4f},0,0)">'
                    f'{escaped}</text>')
        return (f'<text x="{px}" y="{fy:.0f}" font-size="{scale:.1f}" fill="{text_color}" '
                f'font-family="sans-serif">{escaped}</text>')

    elif rtype == 0x0C:
        points = rec.get('points', [])
        if not points:
            return None
        stroke, fill = get_fill_stroke(style, palette)
        pts_str = ' '.join(f'{x},{flip_y(y, canvas_h):.0f}' for x, y in points)
        if fill != 'none':
            return f'<polygon points="{pts_str}" stroke="{stroke}" stroke-width="{base_stroke:.1f}" fill="{fill}" fill-rule="evenodd"/>'
        return f'<polyline points="{pts_str}" stroke="{stroke}" stroke-width="{base_stroke:.1f}" fill="none"/>'

    elif rtype == 0x0F:
        return None

    return None


def sanitize_filename(name):
    safe = name.strip().replace(' ', '_')
    safe = ''.join(c for c in safe if c.isalnum() or c in '-_')
    return safe or 'unnamed'


def convert_pmd_to_svg(input_path, output_dir):
    with open(input_path, 'rb') as f:
        data = f.read()

    if data[:8] != MAGIC:
        print(f'Error: {input_path} is not a PMDraw file (bad magic)', file=sys.stderr)
        sys.exit(1)

    pmd = parse_pmd(data)
    if pmd is None:
        print(f'Error: Failed to parse {input_path}', file=sys.stderr)
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    palette = pmd['palette']
    fonts = pmd['fonts']
    written = 0
    used_names = set()

    for page in pmd['pages']:
        if page['is_index']:
            continue
        if not page['records']:
            continue

        svg = render_page_svg(page, palette, fonts)
        if svg is None:
            continue

        base = sanitize_filename(page['name'])
        name = base
        counter = 2
        while name in used_names:
            name = f'{base}_{counter}'
            counter += 1
        used_names.add(name)

        out_path = os.path.join(output_dir, f'{name}.svg')
        with open(out_path, 'w') as f:
            f.write(svg)
        written += 1

    if written == 0:
        print(f'Warning: No renderable content in {input_path}', file=sys.stderr)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f'Usage: {sys.argv[0]} <inputFile> <outputDir>', file=sys.stderr)
        sys.exit(1)

    convert_pmd_to_svg(sys.argv[1], sys.argv[2])

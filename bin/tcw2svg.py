#!/usr/bin/env python3
# Vibe coded by Claude

"""tcw2svg - Convert TurboCAD .tcw drawing files to SVG.

TurboCAD .tcw/.tct/.bin files are OLE2 containers with a 'Contents' stream
that uses a proprietary TLV (Tag-Length-Value) binary format for geometry.

Supported entity types:
  - Lines/polylines with per-entity colors and dash styles
  - Filled polygons (closed polylines with fill pattern)
  - Circles/arcs (4-point center+axis encoding, subtype 0xb3)
  - Text (0f 01 label + 10 06 02/52/53 sub-entities)
"""

import math
import sys
import struct
import argparse
from collections import defaultdict

import olefile
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Circle, Arc, Polygon


def read_contents(filepath):
    """Read the Contents stream from a TCW OLE2 container.
    Returns None for unsupported formats (e.g. raw TurboCAD headers)."""
    with open(filepath, "rb") as f:
        magic = f.read(8)
    if magic[:8] == b"TurboCAD":
        return None  # Old raw TurboCAD format, no OLE2 container
    ole = olefile.OleFileIO(filepath)
    try:
        contents = ole.openstream("Contents").read()
    finally:
        ole.close()
    # v9+ files have tiny Contents with geometry in Graphics/ModelSpace
    # (different encoding, not yet supported)
    if len(contents) < 100:
        return None
    return contents


def _detect_coord_format(data):
    """Detect coordinate format. Returns (float_size, coord_size, marker_byte).
    - Standard f32: marker=0x10, float_size=4, coord_size=10
    - Standard f64: marker=0x10, float_size=8, coord_size=18
    - v7 3D f64:    marker=0x11, float_size=8, coord_size=26 (X+Y+Z)
    """
    if len(data) > 0x0B:
        sub = data[0x0B]
        if sub in (0x07, 0x17):
            return 8, 18, 0x10
        if sub == 0x01:
            # v7 format: 13 11 [X:f64] [Y:f64] [Z:f64]
            return 8, 26, 0x11
    return 4, 10, 0x10


def _parse_styles(data, n):
    """Parse line style definitions: name -> dash pattern list."""
    styles = {}
    i = 0
    while i < n - 4:
        if data[i] == 0x01 and data[i + 1] == 0x01:
            slen = data[i + 2]
            if i + 3 + slen <= n:
                name = data[i + 3 : i + 3 + slen].decode("ascii", errors="replace")
                j = i + 3 + slen
                if j + 3 < n and data[j] == 0x02 and data[j + 1] == 0x06:
                    count = data[j + 2]
                    j += 4
                    pattern = []
                    for _ in range(count):
                        if j < n and data[j] == 0x0A:
                            j += 1
                        if j + 4 <= n:
                            val = struct.unpack_from("<f", data, j)[0]
                            pattern.append(val)
                            j += 4
                    styles[name] = pattern
                    i = j
                    continue
        i += 1
    return styles


def _read_coord_run(data, i, n, float_size, coord_size):
    """Read consecutive 13 10/11 X Y coordinate pairs. Returns (points, new_i)."""
    points = []
    fmt = "<d" if float_size == 8 else "<f"
    min_bytes = coord_size - 1
    while i + min_bytes < n and data[i] == 0x13 and data[i + 1] in (0x10, 0x11):
        x = struct.unpack_from(fmt, data, i + 2)[0]
        y = struct.unpack_from(fmt, data, i + 2 + float_size)[0]
        points.append((x, y))
        i += coord_size
    return points, i


def _is_arc_points(points):
    """Check if 4 points represent arc (center + 3 axis points).
    Returns (cx, cy, radius) or None."""
    if len(points) != 4:
        return None
    cx, cy = points[0]
    dists = [math.hypot(px - cx, py - cy) for px, py in points[1:]]
    if dists[0] == 0:
        return None
    avg = sum(dists) / 3
    if avg == 0:
        return None
    if all(abs(d - avg) / avg < 0.05 for d in dists):
        return (cx, cy, avg)
    return None


def _is_full_circle(points):
    if len(points) != 4:
        return False
    arc = _is_arc_points(points)
    if arc is None:
        return False
    d = math.hypot(points[1][0] - points[2][0], points[1][1] - points[2][1])
    return d < arc[2] * 0.01


def _colorref_to_hex(val):
    """Convert Windows COLORREF (0x00BBGGRR LE) to hex color string.
    Returns None for special values (by-layer, by-block) or black."""
    if val >= 0xFFFFFFF0:
        return None  # by-layer, by-block
    if val == 0:
        return None  # black -> use default (white on dark bg)
    r = val & 0xFF
    g = (val >> 8) & 0xFF
    b = (val >> 16) & 0xFF
    return f"#{r:02x}{g:02x}{b:02x}"


def _is_closed_polyline(points):
    """Check if polyline forms a closed shape (first point ~ last point)."""
    if len(points) < 3:
        return False
    dx = abs(points[0][0] - points[-1][0])
    dy = abs(points[0][1] - points[-1][1])
    # Use a relative tolerance based on the polyline extent
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    extent = max(max(xs) - min(xs), max(ys) - min(ys), 1e-10)
    return (dx + dy) < extent * 0.001


def _parse_v7(data, n, float_size, coord_size):
    """Parse v7 format (13 11 3D coords) by scanning for coordinate runs.
    Groups points between 0x16 (entity end) markers into entities."""
    result = {
        "lines": [], "fills": [], "circles": [], "arcs": [],
        "texts": [], "dash_pattern": None,
    }
    # Collect all coordinate points, splitting on 0x16 entity boundaries
    entity_points = []
    current_points = []
    i = 0
    while i < n:
        if data[i] == 0x16:
            if current_points:
                entity_points.append(current_points)
                current_points = []
            i += 1
        elif i + coord_size - 1 < n and data[i] == 0x13 and data[i + 1] == 0x11:
            points, i = _read_coord_run(data, i, n, float_size, coord_size)
            current_points.extend(points)
        else:
            i += 1
    if current_points:
        entity_points.append(current_points)

    for points in entity_points:
        if len(points) == 4:
            arc = _is_arc_points(points)
            if arc:
                cx, cy, r = arc
                if _is_full_circle(points):
                    result["circles"].append((cx, cy, r, None, None))
                else:
                    a1 = math.degrees(math.atan2(points[1][1] - cy, points[1][0] - cx))
                    a2 = math.degrees(math.atan2(points[2][1] - cy, points[2][0] - cx))
                    result["arcs"].append((cx, cy, r, a1, a2, None))
                continue
        if len(points) >= 2:
            # For single-point runs that were merged, create line segments
            # from consecutive pairs
            result["lines"].append((points, None, False))
    return result


def parse_drawing(data):
    """Parse the binary Contents stream into typed drawing entities."""
    result = {
        "lines": [],      # (points, stroke_color, is_dashed)
        "fills": [],      # (points, fill_color)
        "circles": [],    # (cx, cy, r, stroke_color, fill_color)
        "arcs": [],       # (cx, cy, r, a1, a2, stroke_color)
        "texts": [],      # (x, y, text, height, color)
        "dash_pattern": None,
    }

    i = 0
    n = len(data)
    float_size, coord_size, _coord_marker = _detect_coord_format(data)

    # v7 format uses different entity structure — use simple scan
    if _coord_marker == 0x11:
        return _parse_v7(data, n, float_size, coord_size)

    eof_marker = bytes([0xFF, 0, 0, 0, 0, 0, 0, 0, 0])
    eof_pos = data.rfind(eof_marker)
    if eof_pos >= 0:
        n = eof_pos

    styles = _parse_styles(data, n)
    current_style = "CONTINUOUS"
    current_stroke_color = None  # None means default (white)
    current_fill_color = None
    current_fill_pattern = ""  # "Solid", "None", etc.
    pending_text = None

    while i < n:
        # Style assignment: 04 01 LEN <name>
        if data[i] == 0x04 and i + 2 < n and data[i + 1] == 0x01:
            slen = data[i + 2]
            if i + 3 + slen <= n:
                current_style = data[i + 3 : i + 3 + slen].decode(
                    "ascii", errors="replace"
                )
            i += 3 + slen
            continue

        # Fill pattern: 08 01 LEN <name>
        if data[i] == 0x08 and i + 2 < n and data[i + 1] == 0x01:
            slen = data[i + 2]
            if i + 3 + slen <= n:
                current_fill_pattern = data[i + 3 : i + 3 + slen].decode(
                    "ascii", errors="replace"
                )
            i += 3 + slen
            continue

        # Stroke color: 02 07 CC CC CC CC
        if data[i] == 0x02 and i + 5 < n and data[i + 1] == 0x07:
            val = struct.unpack_from("<I", data, i + 2)[0]
            current_stroke_color = _colorref_to_hex(val)
            i += 6
            continue

        # Fill color: 06 07 CC CC CC CC
        if data[i] == 0x06 and i + 5 < n and data[i + 1] == 0x07:
            val = struct.unpack_from("<I", data, i + 2)[0]
            current_fill_color = _colorref_to_hex(val)
            i += 6
            continue

        # Text label: 0f 01 LEN <text>
        if data[i] == 0x0F and i + 2 < n and data[i + 1] == 0x01:
            slen = data[i + 2]
            if slen > 0 and i + 3 + slen <= n:
                pending_text = data[i + 3 : i + 3 + slen].decode(
                    "ascii", errors="replace"
                )
            else:
                pending_text = None
            i += 3 + max(slen, 0)
            continue

        if data[i] != 0x15:
            i += 1
            continue

        # Entity geometry start (0x15)
        i += 1
        if i >= n:
            break

        next_b = data[i]
        is_dashed = (
            current_style != "CONTINUOUS"
            and current_style in styles
            and bool(styles[current_style])
        )
        stroke_color = current_stroke_color
        fill_color = current_fill_color
        fill_active = current_fill_pattern.lower() not in ("", "none")

        if next_b == 0x13:
            # Direct coordinates: 15 13 10 X Y [13 10 X Y]* 16
            points, i = _read_coord_run(data, i, n, float_size, coord_size)
            _classify_and_add(
                result, points, stroke_color, fill_color, fill_active,
                is_dashed, styles, current_style,
            )
            i = _scan_text_sub_entities(
                data, i, n, result, float_size, coord_size, is_dashed,
                styles, current_style, stroke_color, fill_color, fill_active,
                pending_text, None, None,
            )
            pending_text = None

        elif next_b == 0x10:
            # Sub-entity block
            i += 1
            i = _parse_sub_entity_block(
                data, i, n, result, float_size, coord_size, is_dashed,
                styles, current_style, stroke_color, fill_color, fill_active,
                pending_text,
            )
            pending_text = None

        elif next_b == 0x0E:
            # Group start - clear pending_text (it was an entity name)
            pending_text = None

        elif next_b == 0x1B:
            i += 1 + 1 + float_size * 2 + 4
            pending_text = None

        elif next_b == 0x0C:
            pending_text = None

        elif next_b == 0x01:
            pending_text = None

        else:
            pending_text = None

    return result


def _classify_and_add(result, points, stroke_color, fill_color, fill_active,
                      is_dashed, styles, current_style):
    """Add points as line, circle, arc, or filled polygon depending on geometry."""
    if len(points) == 4:
        arc = _is_arc_points(points)
        if arc:
            cx, cy, r = arc
            if _is_full_circle(points):
                fc = fill_color if fill_active else None
                result["circles"].append((cx, cy, r, stroke_color, fc))
            else:
                a1 = math.degrees(math.atan2(points[1][1] - cy, points[1][0] - cx))
                a2 = math.degrees(math.atan2(points[2][1] - cy, points[2][0] - cx))
                result["arcs"].append((cx, cy, r, a1, a2, stroke_color))
            return

    # Check for filled closed polygon
    if fill_active and _is_closed_polyline(points) and len(points) >= 3:
        result["fills"].append((points, fill_color))
    if len(points) >= 2:
        _add_line(result, points, stroke_color, is_dashed, styles, current_style)


def _add_line(result, points, color, is_dashed, styles, current_style):
    result["lines"].append((points, color, is_dashed))
    if is_dashed and result["dash_pattern"] is None:
        pat = styles[current_style]
        result["dash_pattern"] = (
            tuple(abs(v) for v in pat[:2]) if len(pat) >= 2 else (0.1, 0.05)
        )


def _parse_sub_entity_block(
    data, i, n, result, float_size, coord_size, is_dashed,
    styles, current_style, stroke_color, fill_color, fill_active, pending_text,
):
    """Parse sub-entity block starting after 15 10."""
    text_pos = None
    text_baseline = None
    text_bbox = None

    if i + 2 < n and data[i] == 0x06:
        subtype = data[i + 1]
        i += 3  # skip 06 XX 00

        if subtype == 0xB3:
            points, i = _read_coord_run(data, i, n, float_size, coord_size)
            _classify_and_add(
                result, points, stroke_color, fill_color, fill_active,
                is_dashed, styles, current_style,
            )
        elif subtype == 0xF3:
            points, i = _read_coord_run(data, i, n, float_size, coord_size)
            if len(points) >= 2:
                _add_line(result, points, stroke_color, is_dashed, styles, current_style)
        elif subtype == 0x02:
            points, i = _read_coord_run(data, i, n, float_size, coord_size)
            if points:
                text_pos = points[0]
        elif subtype == 0x52:
            points, i = _read_coord_run(data, i, n, float_size, coord_size)
            if points:
                text_baseline = points[0]
        elif subtype == 0x53:
            points, i = _read_coord_run(data, i, n, float_size, coord_size)
            if len(points) >= 2:
                text_bbox = points
        elif subtype == 0xF2:
            points, i = _read_coord_run(data, i, n, float_size, coord_size)
        else:
            points, i = _read_coord_run(data, i, n, float_size, coord_size)
            if len(points) >= 2:
                _add_line(result, points, stroke_color, is_dashed, styles, current_style)
    else:
        while i < n and data[i] != 0x16:
            if i + 1 < n and data[i] == 0x13 and data[i + 1] in (0x10, 0x11):
                break
            i += 1
        points, i = _read_coord_run(data, i, n, float_size, coord_size)
        if len(points) >= 2:
            _add_line(result, points, stroke_color, is_dashed, styles, current_style)

    # Continue scanning sub-entities, collecting text parts
    i = _scan_text_sub_entities(
        data, i, n, result, float_size, coord_size, is_dashed,
        styles, current_style, stroke_color, fill_color, fill_active,
        pending_text, text_pos, text_baseline, text_bbox,
    )
    return i


def _scan_text_sub_entities(
    data, i, n, result, float_size, coord_size, is_dashed,
    styles, current_style, stroke_color, fill_color, fill_active,
    pending_text, text_pos, text_baseline, text_bbox=None,
):
    """Scan sub-entities, accumulating text position/baseline for font height."""
    while i < n:
        if data[i] == 0x16:
            i += 1
            # Entity type template definitions (e.g. "Text") have 0x12 (property
            # descriptor) right after the 0x16 end marker.  Real display-text
            # entities never do.  Suppress text creation for templates so that
            # entity-class names like "Text"/"Texto"/"Texte" are not rendered.
            if i < n and data[i] == 0x12:
                pending_text = None
            break
        if i + 3 < n and data[i] == 0x10 and data[i + 1] == 0x06:
            subtype = data[i + 2]
            i += 4

            if subtype == 0xB3:
                points, i = _read_coord_run(data, i, n, float_size, coord_size)
                _classify_and_add(
                    result, points, stroke_color, fill_color, fill_active,
                    is_dashed, styles, current_style,
                )
            elif subtype == 0xF3:
                points, i = _read_coord_run(data, i, n, float_size, coord_size)
                if len(points) >= 2:
                    _add_line(result, points, stroke_color, is_dashed, styles, current_style)
            elif subtype == 0x02:
                points, i = _read_coord_run(data, i, n, float_size, coord_size)
                if points and text_pos is None:
                    text_pos = points[0]
            elif subtype == 0x52:
                points, i = _read_coord_run(data, i, n, float_size, coord_size)
                if points and text_baseline is None:
                    text_baseline = points[0]
            elif subtype == 0x53:
                points, i = _read_coord_run(data, i, n, float_size, coord_size)
                if len(points) >= 2 and text_bbox is None:
                    text_bbox = points
            elif subtype == 0xF2:
                points, i = _read_coord_run(data, i, n, float_size, coord_size)
            else:
                points, i = _read_coord_run(data, i, n, float_size, coord_size)
                if len(points) >= 2:
                    _add_line(result, points, stroke_color, is_dashed, styles, current_style)
        elif i + 1 < n and data[i] == 0x13 and data[i + 1] in (0x10, 0x11):
            points, i = _read_coord_run(data, i, n, float_size, coord_size)
            _classify_and_add(
                result, points, stroke_color, fill_color, fill_active,
                is_dashed, styles, current_style,
            )
        else:
            i += 1

    # Create text entity if we have position and text content
    if text_pos and pending_text:
        height = 0.0
        if text_baseline:
            height = abs(text_baseline[1] - text_pos[1])
        # Fallback: use 0x53 bounding box Y-span when baseline gives zero
        if height == 0.0 and text_bbox and len(text_bbox) >= 2:
            ys = [p[1] for p in text_bbox]
            height = max(ys) - min(ys)
        result["texts"].append(
            (text_pos[0], text_pos[1], pending_text, height, stroke_color)
        )

    return i


def _arc_bbox(cx, cy, r, a1_deg, a2_deg):
    """Compute tight bounding box of an arc sweep from a1 to a2 (degrees)."""
    a1 = math.radians(a1_deg)
    a2 = math.radians(a2_deg)
    # Normalize so a2 > a1
    while a2 < a1:
        a2 += 2 * math.pi

    xs = [cx + r * math.cos(a1), cx + r * math.cos(a2)]
    ys = [cy + r * math.sin(a1), cy + r * math.sin(a2)]

    # Check axis-aligned extremes within sweep
    for k in range(5):
        angle = k * math.pi / 2
        # Shift into range
        while angle < a1:
            angle += 2 * math.pi
        if angle <= a2:
            xs.append(cx + r * math.cos(angle))
            ys.append(cy + r * math.sin(angle))

    return min(xs), max(xs), min(ys), max(ys)


def _hide_axes_chrome(ax):
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def render_svg(drawing, output_path):
    """Render parsed drawing to SVG using matplotlib."""
    lines = drawing["lines"]
    fills = drawing["fills"]
    circles = drawing["circles"]
    arcs = drawing["arcs"]
    texts = drawing["texts"]
    dash_pattern = drawing["dash_pattern"]

    # Collect all coordinates for bounding box (include text)
    all_x = []
    all_y = []
    for pts, _, _ in lines:
        for x, y in pts:
            all_x.append(x)
            all_y.append(y)
    for pts, _ in fills:
        for x, y in pts:
            all_x.append(x)
            all_y.append(y)
    for cx, cy, r, _, _ in circles:
        all_x.extend([cx - r, cx + r])
        all_y.extend([cy - r, cy + r])
    for cx, cy, r, a1, a2, _ in arcs:
        x0, x1, y0, y1 = _arc_bbox(cx, cy, r, a1, a2)
        all_x.extend([x0, x1])
        all_y.extend([y0, y1])
    for x, y, _, h, _ in texts:
        all_x.append(x)
        all_y.append(y)
        if h > 0:
            all_y.append(y + h)

    if not all_x:
        fig = plt.figure(figsize=(4.8, 4.8), dpi=96)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_facecolor("#212830")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        _hide_axes_chrome(ax)
        fig.savefig(output_path, format="svg", facecolor="white")
        plt.close(fig)
        return

    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    dx = max_x - min_x
    dy = max_y - min_y
    if dx == 0:
        dx = 1
    if dy == 0:
        dy = 1

    margin_x = dx * 0.05
    margin_y = dy * 0.05
    view_x = min_x - margin_x
    view_y = min_y - margin_y
    view_w = dx + 2 * margin_x
    view_h = dy + 2 * margin_y

    max_size = 4.8
    aspect = view_w / view_h
    if aspect >= 1:
        fig_w, fig_h = max_size, max_size / aspect
    else:
        fig_w, fig_h = max_size * aspect, max_size

    fig = plt.figure(figsize=(fig_w, fig_h), dpi=96)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor("#212830")

    # Filled polygons (render first, underneath strokes)
    for pts, fill_color in fills:
        fc = fill_color or "white"
        poly = Polygon(pts, closed=True, facecolor=fc, edgecolor="none", linewidth=0)
        ax.add_patch(poly)

    # Group lines by (color, is_dashed)
    line_groups = defaultdict(list)
    for pts, color, is_dashed in lines:
        line_groups[(color or "white", is_dashed)].append(pts)

    for (color, is_dashed), group_lines in line_groups.items():
        kwargs = {"colors": color, "linewidths": 0.72}
        if is_dashed and dash_pattern:
            on, off = dash_pattern
            extent = max(view_w, view_h)
            ppu = (max_size * 72) / extent
            kwargs["linestyles"] = [(0, (on * ppu, off * ppu))]
        lc = LineCollection(group_lines, **kwargs)
        ax.add_collection(lc)

    # Circles
    for cx, cy, r, stroke_color, fill_color in circles:
        has_fill = fill_color is not None
        ax.add_patch(
            Circle(
                (cx, cy), r,
                fill=has_fill,
                facecolor=fill_color if has_fill else "none",
                edgecolor=stroke_color or "white",
                linewidth=0.72,
            )
        )

    # Arcs
    for cx, cy, r, a1, a2, color in arcs:
        ax.add_patch(
            Arc(
                (cx, cy), r * 2, r * 2, angle=0, theta1=a1, theta2=a2,
                edgecolor=color or "white", linewidth=0.72, fill=False,
            )
        )

    # Text
    if texts:
        extent = max(view_w, view_h)
        ppu = (max_size * 72) / extent
        for x, y, text, height, color in texts:
            fontsize = height * ppu if height > 0 else 4.0
            fontsize = max(fontsize, 1.0)
            ax.text(
                x, y, text, color=color or "white", fontsize=fontsize,
                fontfamily="sans-serif", verticalalignment="bottom",
            )

    ax.set_xlim(view_x, view_x + view_w)
    ax.set_ylim(view_y, view_y + view_h)
    _hide_axes_chrome(ax)

    fig.savefig(output_path, format="svg", facecolor="white")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(
        description="Convert TurboCAD .tcw drawing files to SVG"
    )
    parser.add_argument("input", help="Input .tcw/.tct/.bin file")
    parser.add_argument("output", help="Output .svg file")
    args = parser.parse_args()

    try:
        contents = read_contents(args.input)
    except Exception as e:
        print(f"Error reading {args.input}: {e}", file=sys.stderr)
        sys.exit(1)

    if contents is None:
        # Unsupported format — produce empty canvas
        drawing = {
            "lines": [], "fills": [], "circles": [], "arcs": [],
            "texts": [], "dash_pattern": None,
        }
    else:
        drawing = parse_drawing(contents)
    render_svg(drawing, args.output)


if __name__ == "__main__":
    main()

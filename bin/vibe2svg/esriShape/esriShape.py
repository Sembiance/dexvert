#!/usr/bin/env python3
# Vibe coded by Claude

"""
esriShape2svg.py - Convert ESRI Shapefile (.shp) to SVG format.

Usage: python3 esriShape2svg.py <input.shp> <output.svg>

Handles shape types: Null (0), Point (1), PolyLine (3), Polygon (5),
MultiPoint (8), PointZ (11).
"""

import struct
import sys


SHAPE_NAMES = {
    0: "Null Shape",
    1: "Point",
    3: "PolyLine",
    5: "Polygon",
    8: "MultiPoint",
    11: "PointZ",
}


def read_header(data):
    """Parse the 100-byte shapefile header."""
    file_code = struct.unpack_from(">i", data, 0)[0]
    if file_code != 9994:
        raise ValueError(f"Invalid shapefile: file code {file_code}, expected 9994")

    file_length = struct.unpack_from(">i", data, 24)[0] * 2  # convert 16-bit words to bytes
    version = struct.unpack_from("<i", data, 28)[0]
    shape_type = struct.unpack_from("<i", data, 32)[0]

    xmin, ymin, xmax, ymax = struct.unpack_from("<4d", data, 36)

    return {
        "file_length": file_length,
        "version": version,
        "shape_type": shape_type,
        "xmin": xmin,
        "ymin": ymin,
        "xmax": xmax,
        "ymax": ymax,
    }


def parse_records(data):
    """Parse all records from the shapefile data, computing sizes from structure."""
    records = []
    offset = 100  # skip header
    file_len = len(data)

    while offset + 8 <= file_len:
        # Record header: 8 bytes
        rec_num = struct.unpack_from(">i", data, offset)[0]
        content_length_words = struct.unpack_from(">i", data, offset + 4)[0]
        content_start = offset + 8

        # Read shape type at start of content
        if content_start + 4 > file_len:
            break

        shape_type = struct.unpack_from("<i", data, content_start)[0]

        # Compute actual content size based on shape structure
        if shape_type == 0:
            # Null shape: just the 4-byte type field
            actual_content_size = 4
            records.append({"type": 0})

        elif shape_type == 1:
            # Point: type(4) + X(8) + Y(8) = 20
            actual_content_size = 20
            if content_start + 20 > file_len:
                break
            x, y = struct.unpack_from("<2d", data, content_start + 4)
            records.append({"type": 1, "x": x, "y": y})

        elif shape_type == 11:
            # PointZ: type(4) + X(8) + Y(8) + Z(8) + M(8) = 36
            actual_content_size = 36
            if content_start + 20 > file_len:
                break
            x, y = struct.unpack_from("<2d", data, content_start + 4)
            records.append({"type": 11, "x": x, "y": y})

        elif shape_type in (3, 5):
            # PolyLine or Polygon
            # type(4) + bbox(32) + NumParts(4) + NumPoints(4) = 44 minimum
            if content_start + 44 > file_len:
                break
            num_parts = struct.unpack_from("<i", data, content_start + 36)[0]
            num_points = struct.unpack_from("<i", data, content_start + 40)[0]
            actual_content_size = 4 + 32 + 4 + 4 + num_parts * 4 + num_points * 16

            parts_offset = content_start + 44
            points_offset = parts_offset + num_parts * 4

            if points_offset + num_points * 16 > file_len:
                break

            parts = list(struct.unpack_from(f"<{num_parts}i", data, parts_offset))

            points = []
            for i in range(num_points):
                px, py = struct.unpack_from("<2d", data, points_offset + i * 16)
                points.append((px, py))

            records.append({
                "type": shape_type,
                "num_parts": num_parts,
                "num_points": num_points,
                "parts": parts,
                "points": points,
            })

        elif shape_type == 8:
            # MultiPoint
            # type(4) + bbox(32) + NumPoints(4) = 40 minimum
            if content_start + 40 > file_len:
                break
            num_points = struct.unpack_from("<i", data, content_start + 36)[0]
            actual_content_size = 4 + 32 + 4 + num_points * 16

            points_offset = content_start + 40
            if points_offset + num_points * 16 > file_len:
                break

            points = []
            for i in range(num_points):
                px, py = struct.unpack_from("<2d", data, points_offset + i * 16)
                points.append((px, py))

            records.append({
                "type": 8,
                "num_points": num_points,
                "points": points,
            })

        else:
            # Unknown shape type - fall back to content_length to skip
            actual_content_size = content_length_words * 2
            records.append({"type": shape_type})

        offset = content_start + actual_content_size

    return records


def escape_xml(s):
    """Escape special XML characters in attribute values."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def build_svg(header, records):
    """Build the SVG string from parsed shapefile data."""
    xmin = header["xmin"]
    ymin = header["ymin"]
    xmax = header["xmax"]
    ymax = header["ymax"]

    # Handle degenerate bounding boxes
    dx = xmax - xmin
    dy = ymax - ymin
    if dx == 0 and dy == 0:
        # Single point or all same location
        dx = 1.0
        dy = 1.0
        xmin -= 0.5
        ymin -= 0.5
        xmax += 0.5
        ymax += 0.5
    elif dx == 0:
        dx = dy
        xmin -= dx / 2
        xmax += dx / 2
    elif dy == 0:
        dy = dx
        ymin -= dy / 2
        ymax += dy / 2

    # Add 2% padding on each side
    pad_x = dx * 0.02
    pad_y = dy * 0.02
    vb_xmin = xmin - pad_x
    vb_ymin = ymin - pad_y
    vb_width = dx + 2 * pad_x
    vb_height = dy + 2 * pad_y

    # SVG dimensions: 800px wide, proportional height
    svg_width = 800
    svg_height = max(1, int(800 * vb_height / vb_width))

    # For Y-flip: we use scale(1,-1) which mirrors around y=0.
    # The viewBox needs to map to the flipped coordinate space.
    # After scale(1,-1), a point at geographic (x, y) renders at SVG (x, -y).
    # So we need the viewBox to cover x in [vb_xmin, vb_xmin+vb_width]
    # and y in [-(vb_ymin+vb_height), -vb_ymin] which is [-ymax-pad_y, -ymin+pad_y].
    flipped_vb_ymin = -(vb_ymin + vb_height)

    # Stroke width and point radius proportional to extent
    extent = max(dx, dy)
    stroke_w = extent * 0.001
    point_r = extent * 0.005

    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{svg_width}" height="{svg_height}" '
        f'viewBox="{vb_xmin} {flipped_vb_ymin} {vb_width} {vb_height}">'
    )
    lines.append(f'<g transform="scale(1,-1)">')

    for rec in records:
        shape_type = rec["type"]

        if shape_type == 0:
            continue

        elif shape_type in (1, 11):
            # Point or PointZ
            x = rec["x"]
            y = rec["y"]
            lines.append(
                f'<circle cx="{x}" cy="{y}" r="{point_r}" '
                f'fill="#cc4444" fill-opacity="0.8" '
                f'stroke="#882222" stroke-width="{stroke_w}"/>'
            )

        elif shape_type == 8:
            # MultiPoint
            for px, py in rec["points"]:
                lines.append(
                    f'<circle cx="{px}" cy="{py}" r="{point_r}" '
                    f'fill="#cc4444" fill-opacity="0.8" '
                    f'stroke="#882222" stroke-width="{stroke_w}"/>'
                )

        elif shape_type == 5:
            # Polygon
            d = build_path_d(rec, close=True)
            if d:
                lines.append(
                    f'<path d="{d}" '
                    f'fill="#4488cc" fill-opacity="0.6" fill-rule="evenodd" '
                    f'stroke="#224466" stroke-width="{stroke_w}"/>'
                )

        elif shape_type == 3:
            # PolyLine
            d = build_path_d(rec, close=False)
            if d:
                lines.append(
                    f'<path d="{d}" '
                    f'fill="none" '
                    f'stroke="#224466" stroke-width="{stroke_w}" '
                    f'stroke-linecap="round" stroke-linejoin="round"/>'
                )

    lines.append("</g>")
    lines.append("</svg>")

    return "\n".join(lines)


def build_path_d(rec, close=True):
    """Build an SVG path 'd' attribute from a Polygon or PolyLine record."""
    parts = rec["parts"]
    points = rec["points"]
    num_points = rec["num_points"]
    num_parts = rec["num_parts"]

    segments = []
    for i in range(num_parts):
        start = parts[i]
        end = parts[i + 1] if i + 1 < num_parts else num_points

        if start >= end:
            continue

        part_points = points[start:end]
        if not part_points:
            continue

        coords = [f"M{part_points[0][0]} {part_points[0][1]}"]
        for px, py in part_points[1:]:
            coords.append(f"L{px} {py}")
        if close:
            coords.append("Z")

        segments.append("".join(coords))

    return "".join(segments)


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.shp> <output.svg>", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    with open(input_path, "rb") as f:
        data = f.read()

    header = read_header(data)
    records = parse_records(data)

    shape_type = header["shape_type"]
    shape_name = SHAPE_NAMES.get(shape_type, f"Unknown ({shape_type})")

    # Count non-null records
    non_null = sum(1 for r in records if r["type"] != 0)
    print(
        f"{input_path}: shape type {shape_type} ({shape_name}), "
        f"{non_null} records",
        file=sys.stderr,
    )

    svg = build_svg(header, records)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
        f.write("\n")

    print(f"Written: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# Vibe coded by Claude

import sys
import struct
import os

EGA_PALETTE = {
    0: "#000000", 1: "#0000AA", 2: "#00AA00", 3: "#00AAAA",
    4: "#AA0000", 5: "#AA00AA", 6: "#AA5500", 7: "#AAAAAA",
    8: "#555555", 9: "#5555FF", 10: "#55FF55", 11: "#55FFFF",
    12: "#FF5555", 13: "#FF55FF", 14: "#FFFF55", 15: "#FFFFFF",
}


def decode_tp_real(data):
    """Decode a Turbo Pascal 6-byte Real48 value."""
    exp = data[0]
    if exp == 0:
        return 0.0
    sign = (data[5] >> 7) & 1
    mantissa_bits = (
        ((data[5] & 0x7F) << 32)
        | (data[4] << 24)
        | (data[3] << 16)
        | (data[2] << 8)
        | data[1]
    )
    mantissa = 1.0 + mantissa_bits / (1 << 39)
    value = mantissa * (2.0 ** (exp - 129))
    if sign:
        value = -value
    return value


def parse_header(data):
    """Parse the 56-byte DCH file header. Returns a dict of header fields."""
    if len(data) < 56:
        return None
    hdr = {}
    hdr["pad"] = data[0:2]
    hdr["format_code"] = struct.unpack_from("<H", data, 2)[0]
    hdr["version"] = struct.unpack_from("<H", data, 4)[0]
    hdr["field_30"] = struct.unpack_from("<H", data, 6)[0]
    hdr["extra"] = data[8:20]
    hdr["reals"] = [decode_tp_real(data[20 + i * 6 : 26 + i * 6]) for i in range(6)]
    return hdr


def has_compact_metadata(data):
    """Check if file uses the compact metadata block (types 3,4,5,10,8,9)
    that ends at offset 244 due to type-9 overstating its length by 6."""
    if len(data) < 250:
        return False
    offset = 56
    expected = [3, 4, 5, 10, 8, 9]
    idx = 0
    while offset + 4 <= len(data) and idx < len(expected):
        rtype = struct.unpack_from("<H", data, offset)[0]
        rlen = struct.unpack_from("<H", data, offset + 2)[0]
        if rlen == 0 or rtype != expected[idx]:
            return False
        offset += 4 + rlen
        idx += 1
    return idx == len(expected)


def find_drawing_start(data, fmt):
    """Find the offset where drawing records begin, after metadata."""
    if has_compact_metadata(data):
        if len(data) > 248:
            rtype = struct.unpack_from("<H", data, 244)[0]
            if rtype in (0x1E, 0x06, 0x0B, 0x11, 0x14):
                return 244
    offset = 56
    while offset + 4 <= len(data):
        rtype = struct.unpack_from("<H", data, offset)[0]
        rlen = struct.unpack_from("<H", data, offset + 2)[0]
        if rlen == 0:
            break
        if rtype in (3, 4, 5, 8, 9, 10, 11, 12, 13, 14, 15, 245):
            offset += 4 + rlen
        else:
            return offset
    return offset


def parse_type30(payload, rlen):
    """Parse a type-30 (0x1E) drawing record payload."""
    if rlen < 30:
        return None
    rec = {}
    rec["flags"] = struct.unpack_from("<H", payload, 0)[0]
    rec["pad_byte2"] = payload[2]
    rec["color"] = payload[3]
    rec["mode"] = struct.unpack_from("<H", payload, 4)[0]
    rec["attr"] = struct.unpack_from("<H", payload, 6)[0]
    rec["line_spacing"] = decode_tp_real(payload[8:14])
    rec["start_x"] = decode_tp_real(payload[14:20])
    rec["start_y"] = decode_tp_real(payload[20:26])
    rec["fill_flag"] = struct.unpack_from("<H", payload, 26)[0]
    rec["n_pairs"] = struct.unpack_from("<H", payload, 28)[0]
    rec["deltas"] = []
    pos = 30
    for _ in range(rec["n_pairs"]):
        if pos + 12 > rlen:
            break
        dx = decode_tp_real(payload[pos : pos + 6])
        dy = decode_tp_real(payload[pos + 6 : pos + 12])
        rec["deltas"].append((dx, dy))
        pos += 12
    return rec


def parse_type20(payload, rlen):
    """Parse a type-20 (0x14) text record payload. Has 8-byte prefix + reals + text."""
    rec = {}
    prefix_len = 8
    pos = prefix_len
    reals = []
    while pos + 6 <= rlen and len(reals) < 7:
        reals.append(decode_tp_real(payload[pos : pos + 6]))
        pos += 6
    rec["reals"] = reals
    rec["text"] = ""
    while pos < rlen:
        strlen = payload[pos]
        pos += 1
        if strlen > 0 and pos + strlen <= rlen:
            candidate = payload[pos : pos + strlen]
            if all(32 <= c <= 126 for c in candidate):
                rec["text"] = candidate.decode("ascii", errors="replace")
                pos += strlen
                break
        break
    return rec


def type30_to_polygon(rec):
    """Convert a type-30 record to a list of (x, y) polygon vertices."""
    points = [(rec["start_x"], rec["start_y"])]
    cx, cy = rec["start_x"], rec["start_y"]
    for dx, dy in rec["deltas"]:
        cx += dx
        cy += dy
        points.append((cx, cy))
    return points


def parse_type11_diagram(payload, rlen, fmt):
    """Parse a type-0x11 line record from diagram format files."""
    rec = {}
    if fmt == 0:
        rec["prefix"] = payload[0:8]
        reals = []
        pos = 8
        while pos + 6 <= rlen:
            reals.append(decode_tp_real(payload[pos : pos + 6]))
            pos += 6
        rec["extra_bytes"] = payload[pos:rlen]
    else:
        rec["prefix"] = payload[0:8]
        reals = []
        pos = 8
        while pos + 6 <= rlen:
            reals.append(decode_tp_real(payload[pos : pos + 6]))
            pos += 6
        rec["extra_bytes"] = payload[pos:rlen]
    rec["reals"] = reals
    return rec


def parse_type13_diagram(payload, rlen):
    """Parse a type-0x13 arc/curve record from diagram format files."""
    rec = {"prefix": payload[0:8]}
    reals = []
    pos = 8
    while pos + 6 <= rlen:
        reals.append(decode_tp_real(payload[pos : pos + 6]))
        pos += 6
    rec["reals"] = reals
    rec["extra_bytes"] = payload[pos:rlen]
    return rec


def parse_type6_group(payload, rlen):
    """Parse a type-6 group name record."""
    rec = {}
    rec["id"] = struct.unpack_from("<H", payload, 0)[0]
    strlen = payload[2]
    rec["name"] = payload[3 : 3 + strlen].decode("ascii", errors="replace")
    return rec


def parse_records(data, start_offset):
    """Parse all records from start_offset. Returns list of (type, record_dict)."""
    records = []
    offset = start_offset
    while offset + 4 <= len(data):
        rtype = struct.unpack_from("<H", data, offset)[0]
        rlen = struct.unpack_from("<H", data, offset + 2)[0]
        if rlen == 0:
            records.append(("terminator", {"offset": offset, "bytes": data[offset : offset + 4]}))
            offset += 4
            break
        if offset + 4 + rlen > len(data):
            break
        payload = data[offset + 4 : offset + 4 + rlen]
        records.append(("raw", {"type": rtype, "len": rlen, "offset": offset, "payload": payload}))
        offset += 4 + rlen
    return records, offset


def convert_clipart(data, hdr):
    """Convert a clipart/mixed file to SVG elements. Handles type-30 plus diagram records."""
    draw_start = find_drawing_start(data, hdr["format_code"])
    records, end_offset = parse_records(data, draw_start)

    polygons = []
    texts = []
    lines_raw = []
    has_diagram = any(
        r[1]["type"] in (0x06, 0x11, 0x13, 0x16, 0x17, 0x21) for r in records if r[0] == "raw"
    )

    for tag, raw in records:
        if tag == "terminator":
            continue
        rtype = raw["type"]
        rlen = raw["len"]
        payload = raw["payload"]

        if rtype == 0x1E:
            rec = parse_type30(payload, rlen)
            if rec:
                pts = type30_to_polygon(rec)
                color = EGA_PALETTE.get(rec["color"], "#000000")
                polygons.append((pts, color, rec))
        elif rtype == 0x21:
            rec = parse_diagram_polygon(payload, rlen, 157)
            if rec and len(rec["points"]) >= 3:
                polygons.append((rec["points"], "#000000", rec))
        elif rtype == 0x14:
            rec = parse_type20(payload, rlen)
            if rec:
                texts.append(rec)
        elif has_diagram and rtype in (0x11, 0x13, 0x16, 0x17, 0x18):
            elem = element_from_record(rtype, payload, rlen, 0)
            if elem:
                if elem["kind"] == "line":
                    lines_raw.append(elem)
                elif elem["kind"] == "multi":
                    for seg in elem["elements"]:
                        lines_raw.append(seg)

    if lines_raw:
        return polygons, texts, lines_raw
    return polygons, texts


def convert_map(data, hdr):
    """Convert a format-157 map/diagram file to SVG elements."""
    draw_start = find_drawing_start(data, 157)
    records, end_offset = parse_records(data, draw_start)

    has_groups = any(
        r[1]["type"] == 0x06 for r in records if r[0] == "raw"
    )
    if has_groups:
        return convert_diagram(data, hdr)

    polygons = []
    texts = []

    for tag, raw in records:
        if tag == "terminator":
            continue
        rtype = raw["type"]
        rlen = raw["len"]
        payload = raw["payload"]

        if rtype == 0x1E:
            rec = parse_type30(payload, rlen)
            if rec:
                pts = type30_to_polygon(rec)
                color = EGA_PALETTE.get(rec["color"], "#000000")
                polygons.append((pts, color, rec))
        elif rtype == 0x14:
            rec = parse_type20(payload, rlen)
            if rec:
                texts.append(rec)

    return polygons, texts


def has_extra_linewidth(rtype, rlen):
    """Check if a diagram record has the extra line_width Real48 field.
    Each record type has a base size (8-byte prefix + N reals). If the actual
    length is 6 bytes more, an extra line_width real is present."""
    base_sizes = {
        0x11: 32,  # line: 8 + 4*6
        0x13: 44,  # arc: 8 + 6*6
        0x17: 44,  # elliptical arc: same
        0x18: 44,  # arc variant: same
        0x16: 44,  # bezier: 8 + 6*6
        0x12: 44,  # ellipse: 8 + 6*6
        0x19: 46,  # symref: 8 + 5*6 + 2(ref) + 6(reserved)
    }
    base = base_sizes.get(rtype)
    if base and rlen == base + 6:
        return True
    return False


def parse_diagram_reals(payload, rlen, fmt, rtype=0):
    """Extract TP Reals from a diagram record payload after the 8-byte prefix.
    Skips the extra line_width Real if present."""
    pos = 8
    if has_extra_linewidth(rtype, rlen):
        pos = 14
    reals = []
    while pos + 6 <= rlen:
        reals.append(decode_tp_real(payload[pos : pos + 6]))
        pos += 6
    return reals


def is_clipart_polygon(rlen):
    """Clipart polygons have 30-byte header; diagram polygons have 24-byte header.
    The 6-byte difference means exactly one of (rlen-30)%12 or (rlen-24)%12 is zero."""
    return (rlen - 30) % 12 == 0


def parse_diagram_polygon(payload, rlen, fmt):
    """Parse a type-0x1E polygon in diagram format (24-byte header variant)."""
    base = 8 if fmt == 0 else 14
    if rlen < base + 16:
        return None
    cx = decode_tp_real(payload[base : base + 6])
    cy = decode_tp_real(payload[base + 6 : base + 12])
    n_verts = struct.unpack_from("<H", payload, base + 14)[0]
    verts_start = base + 16
    points = []
    for i in range(n_verts):
        off = verts_start + i * 12
        if off + 12 > rlen:
            break
        dx = decode_tp_real(payload[off : off + 6])
        dy = decode_tp_real(payload[off + 6 : off + 12])
        points.append((cx + dx, cy + dy))
    return {"cx": cx, "cy": cy, "points": points}


def element_from_record(rtype, payload, rlen, fmt):
    """Parse a single diagram drawing record into a renderable element dict."""
    import math
    pfmt = fmt
    if rtype == 0x21:
        pfmt = 157

    if rtype in (0x1E, 0x21):
        if is_clipart_polygon(rlen):
            rec = parse_type30(payload, rlen)
            if rec:
                pts = type30_to_polygon(rec)
                filled = rec.get("mode") == 2
                return {"kind": "polygon", "points": pts, "filled": filled,
                        "color": EGA_PALETTE.get(rec.get("color", 0), "#000000")}
        else:
            rec = parse_diagram_polygon(payload, rlen, pfmt)
            if rec and len(rec["points"]) >= 3:
                mode = struct.unpack_from("<H", payload, 4)[0]
                filled = mode == 2
                return {"kind": "polygon", "points": rec["points"], "filled": filled}
    elif rtype == 0x11:
        reals = parse_diagram_reals(payload, rlen, pfmt, rtype)
        attr = struct.unpack_from("<H", payload, 6)[0]
        dash = attr in (3, 4, 8)
        if len(reals) >= 4:
            return {"kind": "line", "dash": dash,
                    "x1": reals[0], "y1": reals[1],
                    "x2": reals[0] + reals[2], "y2": reals[1] + reals[3]}
    elif rtype in (0x13, 0x17, 0x18):
        reals = parse_diagram_reals(payload, rlen, pfmt, rtype)
        attr = struct.unpack_from("<H", payload, 6)[0]
        dash = attr in (3, 4, 8)
        if len(reals) >= 6:
            cx, cy, radius = reals[0], reals[1], reals[2]
            if rtype == 0x13:
                start_angle, aspect, sweep = reals[3], reals[4], reals[5]
            else:
                aspect, start_angle, sweep = reals[3], reals[4], reals[5]
            if radius > 0:
                if sweep == 0:
                    sweep = 2 * math.pi
                segs = []
                n_segs = max(12, int(abs(sweep) / 0.15))
                for i in range(n_segs):
                    a1 = start_angle + sweep * i / n_segs
                    a2 = start_angle + sweep * (i + 1) / n_segs
                    segs.append({
                        "kind": "line", "dash": dash,
                        "x1": cx + radius * math.cos(a1),
                        "y1": cy + radius * aspect * math.sin(a1),
                        "x2": cx + radius * math.cos(a2),
                        "y2": cy + radius * aspect * math.sin(a2),
                    })
                return {"kind": "multi", "elements": segs}
    elif rtype == 0x16:
        reals = parse_diagram_reals(payload, rlen, pfmt, rtype)
        if len(reals) >= 6:
            x, y = reals[0], reals[1]
            cx1, cy1 = x + reals[2], y + reals[3]
            cx2, cy2 = x + reals[4], y + reals[5]
            return {"kind": "multi", "elements": [
                {"kind": "line", "x1": x, "y1": y, "x2": cx1, "y2": cy1},
                {"kind": "line", "x1": cx1, "y1": cy1, "x2": cx2, "y2": cy2},
            ]}
    elif rtype == 0x12:
        reals = parse_diagram_reals(payload, rlen, pfmt, rtype)
        if len(reals) >= 4:
            cx, cy, rx, ry = reals[0], reals[1], reals[2], reals[3]
            if rx > 0 and ry > 0:
                segs = []
                for i in range(36):
                    a1 = 2 * math.pi * i / 36
                    a2 = 2 * math.pi * (i + 1) / 36
                    segs.append({
                        "kind": "line",
                        "x1": cx + rx * math.cos(a1),
                        "y1": cy + ry * math.sin(a1),
                        "x2": cx + rx * math.cos(a2),
                        "y2": cy + ry * math.sin(a2),
                    })
                return {"kind": "multi", "elements": segs}
    elif rtype == 0x14:
        rec = parse_type20(payload, rlen)
        if rec and rec.get("text") and len(rec["reals"]) >= 3:
            return {"kind": "text", "x": rec["reals"][1], "y": rec["reals"][2],
                    "text": rec["text"]}
    return None


def transform_element(elem, tx, ty, sx, sy, angle):
    """Apply scale, rotation, translation to an element."""
    import math
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)

    def xform(x, y):
        rx = sx * x
        ry = sy * y
        return rx * cos_a - ry * sin_a + tx, rx * sin_a + ry * cos_a + ty

    if elem["kind"] == "line":
        nx1, ny1 = xform(elem["x1"], elem["y1"])
        nx2, ny2 = xform(elem["x2"], elem["y2"])
        r = {"kind": "line", "x1": nx1, "y1": ny1, "x2": nx2, "y2": ny2}
        if elem.get("dash"):
            r["dash"] = True
        return r
    elif elem["kind"] == "polygon":
        r = {"kind": "polygon", "points": [xform(x, y) for x, y in elem["points"]]}
        if "filled" in elem:
            r["filled"] = elem["filled"]
        if "color" in elem:
            r["color"] = elem["color"]
        return r
    elif elem["kind"] == "text":
        nx, ny = xform(elem["x"], elem["y"])
        return {"kind": "text", "x": nx, "y": ny, "text": elem["text"]}
    elif elem["kind"] == "multi":
        return {"kind": "multi",
                "elements": [transform_element(e, tx, ty, sx, sy, angle) for e in elem["elements"]]}
    return elem


def flatten_elements(elements):
    """Flatten nested multi-elements into flat lists of lines, polygons, texts."""
    lines = []
    polygons = []
    texts = []
    for elem in elements:
        if elem is None:
            continue
        if elem["kind"] == "line":
            lines.append(elem)
        elif elem["kind"] == "polygon":
            color = elem.get("color", "#000000")
            filled = elem.get("filled", False)
            polygons.append((elem["points"], color, {"filled": filled}))
        elif elem["kind"] == "text":
            texts.append(elem)
        elif elem["kind"] == "multi":
            l, p, t = flatten_elements(elem["elements"])
            lines.extend(l)
            polygons.extend(p)
            texts.extend(t)
    return lines, polygons, texts


def convert_diagram(data, hdr):
    """Convert a diagram file to SVG. Handles symbol groups and instances."""
    fmt = hdr["format_code"]
    draw_start = find_drawing_start(data, fmt)
    records, end_offset = parse_records(data, draw_start)

    raw_list = [(r[1]["type"], r[1]["len"], r[1]["payload"])
                for r in records if r[0] == "raw"]

    groups = []
    group_elements = {}
    i = 0
    while i < len(raw_list):
        rtype, rlen, payload = raw_list[i]
        if rtype == 0x06:
            rec = parse_type6_group(payload, rlen)
            group_idx = len(groups) + 1
            groups.append(rec)
            members = []
            for j in range(rec["id"]):
                mi = i + 1 + j
                if mi < len(raw_list):
                    mt, ml, mp = raw_list[mi]
                    elem = element_from_record(mt, mp, ml, fmt)
                    if elem:
                        members.append(elem)
            group_elements[group_idx] = members
            i += 1 + rec["id"]
        else:
            i += 1

    output_elements = []

    i = 0
    while i < len(raw_list):
        rtype, rlen, payload = raw_list[i]
        if rtype == 0x06:
            rec = parse_type6_group(payload, rlen)
            i += 1 + rec["id"]
            continue
        elif rtype == 0x19:
            reals = parse_diagram_reals(payload, rlen, fmt, rtype)
            if len(reals) >= 5:
                px, py = reals[0], reals[1]
                sx, sy = reals[2], reals[3]
                angle = reals[4]
                group_ref = struct.unpack_from("<H", payload, rlen - 2)[0]
                if group_ref in group_elements:
                    for elem in group_elements[group_ref]:
                        output_elements.append(
                            transform_element(elem, px, py, sx, sy, angle))
            i += 1
        else:
            elem = element_from_record(rtype, payload, rlen, fmt)
            if elem:
                output_elements.append(elem)
            i += 1

    if not output_elements and group_elements:
        for gidx in sorted(group_elements.keys()):
            for elem in group_elements[gidx]:
                output_elements.append(elem)

    lines_raw, polygons, texts_elem = flatten_elements(output_elements)
    texts = [{"reals": [0, t["x"], t["y"]], "text": t["text"]} for t in texts_elem]
    return polygons, texts, lines_raw


def polygons_to_svg(polygons, texts, lines_raw=None, flip_y=True):
    """Convert polygon/text/line data to an SVG string."""
    if not polygons and not texts and not (lines_raw and len(lines_raw) > 0):
        return None

    all_x = []
    all_y = []
    for pts, color, rec in polygons:
        for x, y in pts:
            all_x.append(x)
            all_y.append(y)

    if lines_raw:
        for lr in lines_raw:
            all_x.extend([lr["x1"], lr["x2"]])
            all_y.extend([lr["y1"], lr["y2"]])
            if "cx" in lr:
                all_x.append(lr["cx"])
                all_y.append(lr["cy"])

    for trec in texts:
        if trec.get("text") and len(trec["reals"]) >= 3:
            all_x.append(trec["reals"][1])
            all_y.append(trec["reals"][2])

    if not all_x:
        return None

    min_x = min(all_x)
    max_x = max(all_x)
    min_y = min(all_y)
    max_y = max(all_y)

    w = max_x - min_x
    h = max_y - min_y
    if w == 0:
        w = 1
    if h == 0:
        h = 1

    margin = max(w, h) * 0.02
    svg_w = 800
    scale = svg_w / (w + 2 * margin)
    svg_h = int((h + 2 * margin) * scale)
    if svg_h < 1:
        svg_h = 1

    def tx(x):
        return (x - min_x + margin) * scale

    def ty(y):
        if flip_y:
            return (max_y - y + margin) * scale
        return (y - min_y + margin) * scale

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{svg_w}" height="{svg_h}" '
        f'viewBox="0 0 {svg_w} {svg_h}">'
    )
    parts.append(
        f'<rect width="{svg_w}" height="{svg_h}" fill="white"/>'
    )

    for pts, color, rec in polygons:
        points_str = " ".join(f"{tx(x):.2f},{ty(y):.2f}" for x, y in pts)
        filled = rec.get("filled", True) if isinstance(rec, dict) else True
        if filled:
            parts.append(
                f'<polygon points="{points_str}" fill="{color}" stroke="none"/>'
            )
        else:
            parts.append(
                f'<polygon points="{points_str}" fill="none" stroke="{color}" stroke-width="1"/>'
            )

    if lines_raw:
        for lr in lines_raw:
            x1 = tx(lr["x1"])
            y1 = ty(lr["y1"])
            x2 = tx(lr["x2"])
            y2 = ty(lr["y2"])
            if lr.get("dash"):
                parts.append(
                    f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
                    f'stroke="#999999" stroke-width="0.5" stroke-dasharray="4,3"/>'
                )
            else:
                parts.append(
                    f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
                    f'stroke="black" stroke-width="1"/>'
                )

    for trec in texts:
        if trec.get("text") and len(trec["reals"]) >= 3:
            x = tx(trec["reals"][1])
            y = ty(trec["reals"][2])
            text = trec["text"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            parts.append(
                f'<text x="{x:.2f}" y="{y:.2f}" font-size="10" '
                f'font-family="sans-serif" fill="black">{text}</text>'
            )

    parts.append("</svg>")
    return "\n".join(parts)


def verify_all_bytes(data, hdr):
    """Verify we can account for every byte in the file."""
    fmt = hdr["format_code"]
    header_size = 56

    draw_start = find_drawing_start(data, fmt)

    offset = draw_start
    while offset + 4 <= len(data):
        rtype = struct.unpack_from("<H", data, offset)[0]
        rlen = struct.unpack_from("<H", data, offset + 2)[0]
        if rlen == 0:
            offset += 4
            break
        if offset + 4 + rlen > len(data):
            return False, f"Record at {offset} extends past EOF (type={rtype}, len={rlen})"
        offset += 4 + rlen

    if offset != len(data):
        return False, f"Unaccounted bytes: {len(data) - offset} at offset {offset}"
    return True, "OK"


def convert_file(input_path, output_path):
    """Convert a DCH file to SVG."""
    with open(input_path, "rb") as f:
        data = f.read()

    if len(data) < 56:
        print(f"Error: File too small ({len(data)} bytes)", file=sys.stderr)
        return False

    hdr = parse_header(data)
    if hdr is None:
        print("Error: Could not parse header", file=sys.stderr)
        return False

    if hdr["version"] != 2 or hdr["field_30"] != 48:
        print(
            f"Error: Unsupported version/field: version={hdr['version']}, field_30={hdr['field_30']}",
            file=sys.stderr,
        )
        return False

    fmt = hdr["format_code"]

    draw_start = find_drawing_start(data, fmt)
    first_draw_type = None
    if draw_start + 4 <= len(data):
        first_draw_type = struct.unpack_from("<H", data, draw_start)[0]

    has_layer_headers = first_draw_type == 0x0B
    has_diagram_records = first_draw_type in (0x06, 0x11, 0x14)

    if has_layer_headers:
        result = convert_clipart(data, hdr)
        if len(result) == 3:
            polygons, texts, lines_raw = result
            svg = polygons_to_svg(polygons, texts, lines_raw, flip_y=True)
        else:
            polygons, texts = result
            svg = polygons_to_svg(polygons, texts, flip_y=True)
    elif has_diagram_records or fmt in (0, 155, 157):
        polygons, texts, lines_raw = convert_diagram(data, hdr)
        svg = polygons_to_svg(polygons, texts, lines_raw, flip_y=True)
    elif first_draw_type == 0x1E:
        result = convert_clipart(data, hdr)
        if len(result) == 3:
            polygons, texts, lines_raw = result
            svg = polygons_to_svg(polygons, texts, lines_raw, flip_y=True)
        else:
            polygons, texts = result
            svg = polygons_to_svg(polygons, texts, flip_y=True)
    else:
        print(f"Error: Unsupported format code: {fmt}", file=sys.stderr)
        return False

    if svg is None:
        print("Error: No drawable content found", file=sys.stderr)
        return False

    with open(output_path, "w") as f:
        f.write(svg)
    return True


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputFile>", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    if not os.path.isfile(input_path):
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    if not convert_file(input_path, output_path):
        if os.path.exists(output_path):
            os.remove(output_path)
        sys.exit(1)


if __name__ == "__main__":
    main()

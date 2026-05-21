#!/usr/bin/env python3
# Vibe coded by Codex

import base64
import json
import math
import os
import re
import struct
import sys
from pathlib import Path


class VcaError(Exception):
    pass


class UnsupportedVertex(VcaError):
    pass


TEXT_MAGIC = b"SuperScape (c) New Dimension International Ltd.\x00"
VERTEX_ROW_MARKERS = {-32767, -32766, -32759, -32758}
DERIVED_VERTEX_KINDS = {2, 10}
ANGLE_UNITS_PER_TURN = 4096.0
INSTANCE_CUBOID_NON_RENDER_COLORS = {0, 191, 255}
REPRESENTATION_SUFFIX_RE = re.compile(r"(?i)(?:\s*-\s*|\s+)rep\s*\d*\s*$")
FONT_SHAPE_PREFIXES = ("FONT_", "MBEFONT:", "ALPH:")


def u16(data, off):
    if off + 2 > len(data):
        raise VcaError("unexpected end of file while reading u16")
    return struct.unpack_from("<H", data, off)[0]


def i32(data, off):
    if off + 4 > len(data):
        raise VcaError("unexpected end of file while reading i32")
    return struct.unpack_from("<i", data, off)[0]


def parse_container(data):
    if len(data) < 0x160:
        raise VcaError("file is too small for a VCA container")
    if not data.startswith(TEXT_MAGIC):
        raise VcaError("missing SuperScape container signature")
    if data[0xF4:0xF9] != b".VRT\x00":
        raise VcaError("missing VRT archive marker at offset 0xF4")
    count = u16(data, 0x100)
    if count == 0 or count > 64:
        raise VcaError(f"invalid archive member count {count}")
    off = 0x102
    entries = []
    for _ in range(count):
        try:
            end = data.index(0, off)
        except ValueError as exc:
            raise VcaError("unterminated archive member name") from exc
        name_bytes = data[off:end]
        if not name_bytes:
            raise VcaError("empty archive member name")
        try:
            name = name_bytes.decode("ascii")
        except UnicodeDecodeError as exc:
            raise VcaError("non-ASCII archive member name") from exc
        if end + 10 > len(data):
            raise VcaError("truncated archive directory entry")
        flag = data[end + 1]
        start = struct.unpack_from("<I", data, end + 2)[0]
        size = struct.unpack_from("<I", data, end + 6)[0]
        if start < 0x100 or size <= 0 or start + size > len(data):
            raise VcaError(f"archive member {name} points outside the file")
        entries.append({"name": name, "flag": flag, "start": start, "size": size})
        off = end + 10
    spans = sorted((e["start"], e["start"] + e["size"], e["name"]) for e in entries)
    for (a0, a1, an), (b0, _b1, bn) in zip(spans, spans[1:]):
        if a1 > b0:
            raise VcaError(f"archive members overlap: {an} and {bn}")
    if spans[-1][1] != len(data):
        raise VcaError("last archive member does not end at EOF")
    return entries


def member(data, entries, suffix):
    matches = [e for e in entries if e["name"].upper().endswith(suffix)]
    if len(matches) != 1:
        raise VcaError(f"expected exactly one {suffix} member, found {len(matches)}")
    e = matches[0]
    return data[e["start"]:e["start"] + e["size"]], e


def parse_wld_tail_records(tail_words):
    records = []
    p = 0
    if p < len(tail_words) and tail_words[p] == 0:
        p += 1
    while p < len(tail_words):
        kind = tail_words[p]
        if kind == 0xFFFF:
            argument = tail_words[p + 1] if p + 1 < len(tail_words) else None
            records.append({"kind": 0xFFFF, "argument": argument})
            p += 2 if p + 1 < len(tail_words) else 1
            continue
        if p + 1 >= len(tail_words):
            records.append({"kind": kind, "raw_words": tail_words[p:]})
            break
        length = tail_words[p + 1]
        if length < 4 or length % 2:
            records.append({"kind": kind, "raw_words": tail_words[p:]})
            break
        payload_words_count = (length - 4) // 2
        end = p + 2 + payload_words_count
        if end > len(tail_words):
            records.append({"kind": kind, "raw_words": tail_words[p:]})
            break
        payload_words = tail_words[p + 2:end]
        payload = b""
        if payload_words:
            payload = struct.pack("<" + "H" * len(payload_words), *payload_words)
        records.append({
            "kind": kind,
            "length": length,
            "payload_words": payload_words,
            "payload": payload,
        })
        p = end
    return records


def parse_palette(pal):
    default = []
    for i in range(256):
        v = ((i * 37) % 191 + 48) / 255.0
        default.append((v, ((i * 67) % 191 + 48) / 255.0, ((i * 97) % 191 + 48) / 255.0, 1.0))
    pos = pal.find(b"PALT")
    if pos < 0 or pos + 0x12 + 256 * 3 > len(pal):
        return default
    size = u16(pal, pos + 0x0E)
    if size not in (0x0304, 0x0300):
        return default
    start = pos + 0x12
    colors = []
    for i in range(256):
        r, g, b = pal[start + i * 3:start + i * 3 + 3]
        colors.append((r / 255.0, g / 255.0, b / 255.0, 1.0))
    return colors


def parse_wld_instances(wld):
    if not wld.startswith(TEXT_MAGIC):
        raise VcaError("WLD member missing SuperScape signature")
    wrld = wld.find(b"WRLD")
    if wrld != 0xF4:
        raise VcaError(f"WRLD marker is at 0x{wrld:X}, expected 0xF4")
    pos = wrld + 0x0E
    nodes = {}
    order = []
    while pos + 4 <= len(wld):
        typ = u16(wld, pos)
        if typ == 0xFFFF:
            pos += 2
            continue
        length = u16(wld, pos + 2)
        if length < 4 or pos + length > len(wld):
            break
        rec = wld[pos:pos + length]
        if typ == 0x44 and length >= 56:
            object_id = struct.unpack_from("<h", rec, 4)[0]
            first_child = u16(rec, 6)
            next_sibling = u16(rec, 10)
            dims = struct.unpack_from("<iii", rec, 24)
            loc = struct.unpack_from("<iii", rec, 36)
            shape_id = struct.unpack_from("<h", rec, 52)[0]
            rotation = struct.unpack_from("<hhh", rec, 56) if length >= 62 else (0, 0, 0)
            render_flags = u16(rec, 62) if length >= 64 else 0
            tail_words = ()
            if length > 64:
                tail = rec[64:]
                tail_words = struct.unpack_from("<" + "H" * (len(tail) // 2), tail, 0)
            tail_records = parse_wld_tail_records(tail_words)
            item = {
                "pos": pos,
                "length": length,
                "object_id": object_id,
                "first_child": first_child,
                "next_sibling": next_sibling,
                "shape_id": shape_id,
                "dims": dims,
                "loc": loc,
                "rotation": rotation,
                "render_flags": render_flags,
                "tail_words": tail_words,
                "tail_records": tail_records,
            }
            nodes[pos] = item
            order.append(pos)
        pos += length
    if not order:
        return None, []
    root = nodes[order[0]]
    instances = []

    def visit(node, parent_matrix, is_root=False):
        matrix = root_matrix(node["dims"]) if is_root else mat_mul(parent_matrix, local_coord_matrix(node))
        if node["shape_id"] >= 0:
            instances.append({
                "shape_id": node["shape_id"],
                "matrix": mat_mul(matrix, shape_scale_matrix(node)),
                "render_flags": node.get("render_flags", 0),
                "tail_words": node.get("tail_words", ()),
                "tail_records": node.get("tail_records", ()),
            })
        child_pos = node["pos"] + node["first_child"] if node["first_child"] else None
        if child_pos in nodes:
            visit(nodes[child_pos], matrix)
        sibling_pos = node["pos"] + node["next_sibling"] if node["next_sibling"] else None
        if sibling_pos in nodes:
            visit(nodes[sibling_pos], parent_matrix)

    visit(root, identity_matrix(), True)
    return root, instances


def identity_matrix():
    return ((1.0, 0.0, 0.0, 0.0), (0.0, 1.0, 0.0, 0.0), (0.0, 0.0, 1.0, 0.0), (0.0, 0.0, 0.0, 1.0))


def mat_mul(a, b):
    return tuple(
        tuple(sum(a[r][k] * b[k][c] for k in range(4)) for c in range(4))
        for r in range(4)
    )


def mat_apply(m, p):
    x, y, z = p
    return (
        m[0][0] * x + m[0][1] * y + m[0][2] * z + m[0][3],
        m[1][0] * x + m[1][1] * y + m[1][2] * z + m[1][3],
        m[2][0] * x + m[2][1] * y + m[2][2] * z + m[2][3],
    )


def translation_matrix(x, y, z):
    return ((1.0, 0.0, 0.0, x), (0.0, 1.0, 0.0, y), (0.0, 0.0, 1.0, z), (0.0, 0.0, 0.0, 1.0))


def scale_matrix(x, y, z):
    return ((x, 0.0, 0.0, 0.0), (0.0, y, 0.0, 0.0), (0.0, 0.0, z, 0.0), (0.0, 0.0, 0.0, 1.0))


def rotation_matrix(rotation):
    m = identity_matrix()
    for axis, angle_word in enumerate(rotation):
        if angle_word == 0:
            continue
        angle = angle_word * (2.0 * math.pi / ANGLE_UNITS_PER_TURN)
        c = math.cos(angle)
        s = math.sin(angle)
        if axis == 0:
            r = ((1.0, 0.0, 0.0, 0.0), (0.0, c, -s, 0.0), (0.0, s, c, 0.0), (0.0, 0.0, 0.0, 1.0))
        elif axis == 1:
            r = ((c, 0.0, s, 0.0), (0.0, 1.0, 0.0, 0.0), (-s, 0.0, c, 0.0), (0.0, 0.0, 0.0, 1.0))
        else:
            r = ((c, -s, 0.0, 0.0), (s, c, 0.0, 0.0), (0.0, 0.0, 1.0, 0.0), (0.0, 0.0, 0.0, 1.0))
        m = mat_mul(m, r)
    return m


def root_matrix(dims):
    return translation_matrix(-dims[0] / 2.0, -dims[1] / 2.0, -dims[2] / 2.0)


def local_matrix(node):
    dx, dy, dz = node["dims"]
    ox, oy, oz = node["loc"]
    return mat_mul(
        mat_mul(
            mat_mul(translation_matrix(ox + dx / 2.0, oy + dy / 2.0, oz + dz / 2.0), rotation_matrix(node["rotation"])),
            translation_matrix(-dx / 2.0, -dy / 2.0, -dz / 2.0),
        ),
        scale_matrix(dx / 16384.0, dy / 16384.0, dz / 16384.0),
    )


def local_coord_matrix(node):
    dx, dy, dz = node["dims"]
    ox, oy, oz = node["loc"]
    return mat_mul(
        mat_mul(translation_matrix(ox + dx / 2.0, oy + dy / 2.0, oz + dz / 2.0), rotation_matrix(node["rotation"])),
        translation_matrix(-dx / 2.0, -dy / 2.0, -dz / 2.0),
    )


def shape_scale_matrix(node):
    dx, dy, dz = node["dims"]
    return scale_matrix(dx / 16384.0, dy / 16384.0, dz / 16384.0)


def record_start(shp, shap):
    if shap + 0x0E <= len(shp) and u16(shp, shap + 0x0C) == 6 and u16(shp, shap + 0x0E) == 16:
        return shap + 0x0C
    if shap + 0x16 <= len(shp) and u16(shp, shap + 0x14) == 6 and u16(shp, shap + 0x16) == 16:
        return shap + 0x14
    raise VcaError("could not locate the first SHAP record")


def parse_type0_vertices(rec):
    count = u16(rec, 4)
    mode = u16(rec, 6)
    if (len(rec) - 8) % 2:
        raise VcaError(f"vertex record length {len(rec)} has a dangling byte")
    payload_words = (len(rec) - 8) // 2
    out = []
    words = struct.unpack_from("<" + "h" * payload_words, rec, 8)
    p = 0
    row_words = 1 + mode * 3
    while len(out) < count and p < payload_words:
        marker = words[p]
        if marker in VERTEX_ROW_MARKERS:
            if p + row_words > payload_words:
                raise VcaError(f"mode {mode} vertex row overruns its record")
            out.append({"kind": 1, "coord": tuple(words[p + 1:p + 4])})
            p += row_words
        elif marker == 1 or marker in DERIVED_VERTEX_KINDS:
            if p + 4 > payload_words:
                raise VcaError(f"mode {mode} vertex entry overruns its record")
            out.append({"kind": marker, "coord": tuple(words[p + 1:p + 4])})
            p += 4
        else:
            raise VcaError(f"mode {mode} vertex entry {len(out)} has unsupported marker {marker}")
    if len(out) != count or p != payload_words:
        raise VcaError(
            f"mode {mode} vertex record consumed {p} of {payload_words} words for {len(out)} of {count} vertices"
        )
    return 1, out


def parse_type1_edges(rec):
    count = u16(rec, 4)
    if len(rec) != 6 + count * 4:
        return None
    out = []
    p = 6
    for _ in range(count):
        a, b = struct.unpack_from("<HH", rec, p)
        out.append((a, b))
        p += 4
    return out


def parse_type2_faces(rec):
    count = u16(rec, 4)
    faces = []
    p = 6
    for _ in range(count):
        if p + 4 > len(rec):
            raise VcaError("truncated polygon face entry")
        raw_n, material = struct.unpack_from("<HH", rec, p)
        p += 4
        n = raw_n & 0x00FF
        flags = raw_n & 0xFF00
        if n < 1 or n > 64:
            raise VcaError(f"unsupported polygon edge count word 0x{raw_n:04X}")
        if p + n * 2 > len(rec):
            raise VcaError("polygon face entry overruns its record")
        refs = list(struct.unpack_from("<" + "H" * n, rec, p))
        p += n * 2
        faces.append({"flags": flags, "material": material, "refs": refs})
    if p != len(rec):
        raise VcaError("polygon record has trailing structural bytes")
    return faces


def parse_type3_material_table(rec):
    if len(rec) < 4:
        raise VcaError("truncated material/color record")
    return list(rec[4:])


def parse_type8_bitmap(rec):
    height = u16(rec, 4)
    width = u16(rec, 6)
    if width == 0 or height == 0:
        raise VcaError("bitmap record has a zero dimension")
    if len(rec) - 8 != width * height:
        raise VcaError(
            f"bitmap record length {len(rec)} does not match {width} x {height} pixels"
        )
    return {"width": width, "height": height, "pixels": rec[8:]}


def new_group(scale, vertices=None):
    return {
        "scale": scale,
        "vertices": list(vertices or []),
        "edges": [],
        "faces": [],
        "colors": [],
        "material_tables": [],
        "name": None,
        "bitmaps": [],
        "_edge_base": 0,
        "_last_face_range": None,
        "vertex_mode": 1,
    }


def parse_shape_name_record(rec):
    if len(rec) != 38:
        raise VcaError(f"shape metadata record has invalid length {len(rec)}")
    shape_id = struct.unpack_from("<h", rec, 4)[0]
    raw_name = rec[6:38]
    segments = []
    current = bytearray()
    for byte in raw_name:
        if 32 <= byte <= 126:
            current.append(byte)
        else:
            if current.rstrip():
                segments.append(bytes(current).decode("ascii").rstrip())
            current.clear()
    if current.rstrip():
        segments.append(bytes(current).decode("ascii").rstrip())
    name = segments[0] if segments else ""
    return {"shape_id": shape_id, "name": name, "name_segments": segments, "name_raw": raw_name}


def parse_metadata_tail_record(rec):
    typ = u16(rec, 0)
    if typ == 1:
        return parse_shape_name_record(rec)
    if typ == 2 and len(rec) == 6 and u16(rec, 4) == 0:
        return {"shape_id": None, "name": "", "name_segments": [], "terminator": True}
    raise VcaError(f"unsupported SHP metadata tail record type {typ}")


def parse_shp(shp):
    if not shp.startswith(TEXT_MAGIC):
        raise VcaError("SHP member missing SuperScape signature")
    shap = shp.find(b"SHAP")
    if shap != 0xF4:
        raise VcaError(f"SHAP marker is at 0x{shap:X}, expected 0xF4")
    stored_len = struct.unpack_from("<I", shp, 0xF0)[0]
    if stored_len == 0 or stored_len > len(shp):
        raise VcaError("SHP stored length is outside the member")
    if shp[shap:shap + 4] != b"SHAP":
        raise VcaError("missing SHAP stream magic")
    pos = record_start(shp, shap)
    groups = []
    cur = None
    pending_vertices = []
    metadata_tail = False
    shape_names = []

    def flush():
        nonlocal cur
        nonlocal pending_vertices
        if cur and (cur.get("faces") or cur.get("bitmaps")):
            groups.append(cur)
        elif cur and cur.get("vertices"):
            pending_vertices = cur["vertices"]
        cur = None

    while pos < len(shp):
        if pos + 2 > len(shp):
            raise VcaError("dangling byte at end of SHP stream")
        typ = u16(shp, pos)
        if typ == 0xFFFF:
            pos += 2
            continue
        if pos + 4 > len(shp):
            raise VcaError("truncated SHP record header")
        length = u16(shp, pos + 2)
        if length < 4 or pos + length > len(shp):
            raise VcaError(f"record type {typ} has invalid length {length}")
        rec = shp[pos:pos + length]
        pos += length
        if metadata_tail:
            item = parse_metadata_tail_record(rec)
            if not item.get("terminator"):
                shape_names.append(item)
            continue
        if typ == 6:
            if length != 16:
                raise VcaError(f"type 6 transform record has invalid length {length}")
            flush()
            cur = new_group((i32(rec, 4), i32(rec, 8), i32(rec, 12)), pending_vertices)
            if pos + 2 <= len(shp) and u16(shp, pos) == 0xFFFF:
                pos += 2
        elif typ == 0:
            if cur is None:
                cur = new_group((10000, 10000, 10000))
            vertex_mode, new_vertices = parse_type0_vertices(rec)
            if cur.get("edges") or cur.get("faces") or cur.get("colors"):
                scale = cur["scale"]
                flush()
                pending_vertices = new_vertices
                cur = new_group(scale, new_vertices)
                cur["vertex_mode"] = vertex_mode
            else:
                pending_vertices = new_vertices
                cur["vertices"] = list(new_vertices)
                cur["vertex_mode"] = vertex_mode
        elif typ == 1:
            if cur is None:
                continue
            if cur.get("faces") or cur.get("colors"):
                scale = cur["scale"]
                vertices = cur["vertices"]
                vertex_mode = cur.get("vertex_mode", 1)
                flush()
                cur = new_group(scale, vertices)
                cur["vertex_mode"] = vertex_mode
            edges = parse_type1_edges(rec)
            if edges is not None:
                cur["_edge_base"] = len(cur["edges"])
                cur["edges"].extend(edges)
            else:
                flush()
                metadata_tail = True
        elif typ == 2:
            if cur is None:
                raise VcaError("polygon record before transform record")
            edge_base = cur.get("_edge_base", 0)
            face_start = len(cur["faces"])
            for face in parse_type2_faces(rec):
                face["refs"] = [
                    (ref & 0x8000) | ((ref & 0x7FFF) + edge_base)
                    for ref in face["refs"]
                ]
                cur["faces"].append(face)
            cur["_last_face_range"] = (face_start, len(cur["faces"]))
        elif typ == 3:
            if cur is None:
                continue
            table = parse_type3_material_table(rec)
            cur["colors"].extend(table)
            cur["material_tables"].append(table)
            face_range = cur.get("_last_face_range")
            if face_range:
                start, end = face_range
                for face in cur["faces"][start:end]:
                    material_id = face["material"]
                    if 1 <= material_id <= len(table):
                        face["color_index"] = table[material_id - 1]
        elif typ == 8:
            if cur is None:
                cur = new_group((10000, 10000, 10000))
            cur["bitmaps"].append(parse_type8_bitmap(rec))
        elif typ == 7:
            raise VcaError("unsupported SHP type 7 animation/control record")
        elif typ in (4, 9, 10, 11, 13, 16, 18, 32, 130, 282):
            pass
        else:
            raise VcaError(f"unsupported SHP record type {typ}")
    flush()
    if not groups:
        raise VcaError("SHP stream contained no polygon groups")
    for item in shape_names:
        shape_id = item["shape_id"]
        if shape_id == -1:
            continue
        if shape_id < 0 or shape_id >= len(groups):
            raise VcaError(f"shape metadata references missing shape id {shape_id}")
        groups[shape_id]["name"] = item["name"]
        groups[shape_id]["name_segments"] = item["name_segments"]
    return groups


IMPLICIT = {
    0: (0, 0, 0),
    1: (0x4000, 0, 0),
    2: (0, 0, 0x4000),
    3: (0x4000, 0, 0x4000),
    4: (0, 0x4000, 0),
    5: (0x4000, 0x4000, 0),
    6: (0, 0x4000, 0x4000),
    7: (0x4000, 0x4000, 0x4000),
}

FONT_IMPLICIT = {
    0: (0, 0, 0),
    1: (0x4000, 0, 0),
    2: (0, 0x4000, 0),
    3: (0x4000, 0x4000, 0),
    4: (0, 0, 0x4000),
    5: (0x4000, 0, 0x4000),
    6: (0, 0x4000, 0x4000),
    7: (0x4000, 0x4000, 0x4000),
}


def convert_point(raw, scale):
    sx, sy, sz = scale
    x, y, z = raw
    return (
        (x / 16384.0 - 0.5) * (sx / 10000.0),
        (y / 16384.0 - 0.5) * (sy / 10000.0),
        -(z / 16384.0 - 0.5) * (sz / 10000.0),
    )


def rotate_xyz(point, rotation):
    x, y, z = point
    for axis, angle_word in enumerate(rotation):
        if angle_word == 0:
            continue
        angle = angle_word * (2.0 * math.pi / ANGLE_UNITS_PER_TURN)
        c = math.cos(angle)
        s = math.sin(angle)
        if axis == 0:
            y, z = y * c - z * s, y * s + z * c
        elif axis == 1:
            x, z = x * c + z * s, -x * s + z * c
        else:
            x, y = x * c - y * s, x * s + y * c
    return x, y, z


def convert_instance_point(raw, dims, loc, root_dims, rotation=(0, 0, 0)):
    x, y, z = raw
    dx, dy, dz = dims
    ox, oy, oz = loc
    rx, ry, rz = root_dims
    lx = (x / 16384.0 - 0.5) * dx
    ly = (y / 16384.0 - 0.5) * dy
    lz = (z / 16384.0 - 0.5) * dz
    lx, ly, lz = rotate_xyz((lx, ly, lz), rotation)
    wx = ox + dx / 2.0 + lx - rx / 2.0
    wy = oy + dy / 2.0 + ly - ry / 2.0
    wz = oz + dz / 2.0 + lz - rz / 2.0
    return (wx / 10000.0, wy / 10000.0, -wz / 10000.0)


def convert_matrix_point(raw, matrix):
    x, y, z = mat_apply(matrix, raw)
    return (x / 10000.0, y / 10000.0, -z / 10000.0)


def vertex_by_id(idx, vertices):
    return resolve_vertex_by_id_with_implicit(idx, vertices, set(), IMPLICIT)


def font_vertex_by_id(idx, vertices):
    return resolve_vertex_by_id_with_implicit(idx, vertices, set(), FONT_IMPLICIT)


def resolve_vertex_by_id(idx, vertices, stack):
    return resolve_vertex_by_id_with_implicit(idx, vertices, stack, IMPLICIT)


def resolve_vertex_by_id_with_implicit(idx, vertices, stack, implicit):
    if idx >= 8 and idx - 8 < len(vertices):
        if idx in stack:
            raise UnsupportedVertex(f"vertex id {idx} recursively references itself")
        vertex = vertices[idx - 8]
        if isinstance(vertex, dict):
            if vertex["kind"] == 1:
                return vertex["coord"]
            if vertex["kind"] in DERIVED_VERTEX_KINDS:
                a, b, amount = vertex["coord"]
                stack.add(idx)
                pa = resolve_vertex_by_id_with_implicit(a, vertices, stack, implicit)
                pb = resolve_vertex_by_id_with_implicit(b, vertices, stack, implicit)
                stack.remove(idx)
                t = (amount & 0xFFFF) / 65536.0
                return tuple(pa[i] + (pb[i] - pa[i]) * t for i in range(3))
            raise UnsupportedVertex(f"vertex id {idx} uses unsupported kind {vertex['kind']}")
            return vertex["coord"]
        return vertex
    if idx < 8:
        return implicit[idx]
    if idx < len(vertices):
        return vertices[idx]
    raise VcaError(f"edge references missing vertex id {idx}")


def directed_edge(edge_ref, edges):
    idx = edge_ref & 0x7FFF
    if idx >= len(edges):
        raise VcaError(f"face references missing edge id {idx}")
    a, b = edges[idx]
    if edge_ref & 0x8000:
        return b, a
    return a, b


def is_implicit_box_group(group):
    if len(group["faces"]) != 6 or not group["edges"]:
        return False
    refs = [vid for edge in group["edges"] for vid in edge]
    return bool(refs) and max(refs) < 8 and sorted(len(face["refs"]) for face in group["faces"]) == [4] * 6


def is_font_shape_group(group):
    name = (group.get("name") or "").upper()
    return name.startswith(FONT_SHAPE_PREFIXES)


def should_skip_font_face(group, loop, lookup=vertex_by_id):
    if not is_font_shape_group(group) or is_implicit_box_group(group) or not any(vid < 8 for vid in loop):
        return False
    points = [lookup(vid, group["vertices"]) for vid in loop]
    same_z = len({point[2] for point in points}) == 1
    all_implicit = all(vid < 8 for vid in loop)
    return (all_implicit and same_z) or not same_z


def is_helper_instance(group, instance):
    if not is_implicit_box_group(group):
        return False
    tail_words = instance.get("tail_words", ())
    appearance = tail_words[1] if len(tail_words) > 1 else None
    appearance_arg = tail_words[2] if len(tail_words) > 2 else None
    if appearance == 3:
        return True
    if instance.get("render_flags") == 0x8E00 and appearance == 1:
        return True
    return bool(instance.get("render_flags")) and appearance == 0xFFFF and appearance_arg == 0xFFFF


def instance_appearance(instance):
    for record in instance.get("tail_records", ()):
        kind = record.get("kind")
        if kind not in (None, 0xFFFF) and "payload" in record:
            return {"kind": kind, "payload": record["payload"]}
    tail_words = instance.get("tail_words", ())
    if len(tail_words) < 3 or tail_words[0] != 0:
        return None
    kind = tail_words[1]
    length = tail_words[2]
    if length < 4 or length % 2:
        return None
    payload_words = (length - 4) // 2
    if 3 + payload_words > len(tail_words):
        return None
    payload = struct.pack("<" + "H" * payload_words, *tail_words[3:3 + payload_words])
    return {"kind": kind, "payload": payload}


def representation_base_name(name):
    name = (name or "").strip()
    base = name
    while True:
        new_base = REPRESENTATION_SUFFIX_RE.sub("", base).strip()
        if new_base == base:
            break
        base = new_base
    return base.lower(), base != name


def select_static_instances(groups, instances):
    infos = []
    original_bases = set()
    for index, instance in enumerate(instances or []):
        sid = instance["shape_id"]
        name = groups[sid].get("name", "") if 0 <= sid < len(groups) else ""
        base, is_representation = representation_base_name(name)
        infos.append((index, instance, base, is_representation))
        if base and not is_representation:
            original_bases.add(base)
    selected = []
    for _index, instance, base, is_representation in infos:
        if is_representation and base in original_bases:
            continue
        selected.append(instance)
    return selected


def project_polygon(points):
    nx = ny = nz = 0.0
    for (x0, y0, z0), (x1, y1, z1) in zip(points, points[1:] + points[:1]):
        nx += (y0 - y1) * (z0 + z1)
        ny += (z0 - z1) * (x0 + x1)
        nz += (x0 - x1) * (y0 + y1)
    axis = max(range(3), key=lambda i: abs((nx, ny, nz)[i]))
    if axis == 0:
        return [(p[1], p[2]) for p in points]
    if axis == 1:
        return [(p[0], p[2]) for p in points]
    return [(p[0], p[1]) for p in points]


def area2(poly):
    return sum(
        x0 * y1 - x1 * y0
        for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1])
    )


def point_in_triangle(p, a, b, c, orientation):
    def cross(u, v, w):
        return (v[0] - u[0]) * (w[1] - u[1]) - (v[1] - u[1]) * (w[0] - u[0])

    eps = 1e-9
    return (
        orientation * cross(a, b, p) >= -eps
        and orientation * cross(b, c, p) >= -eps
        and orientation * cross(c, a, p) >= -eps
    )


def triangulate_polygon(points):
    if len(points) == 3:
        return [(0, 1, 2)]
    projected = project_polygon(points)
    signed_area = area2(projected)
    if abs(signed_area) < 1e-9:
        return [(0, i, i + 1) for i in range(1, len(points) - 1)]
    orientation = 1.0 if signed_area > 0 else -1.0
    remaining = list(range(len(points)))
    triangles = []
    guard = 0
    while len(remaining) > 3 and guard < len(points) * len(points):
        guard += 1
        clipped = False
        for pos, cur in enumerate(remaining):
            prev_i = remaining[pos - 1]
            next_i = remaining[(pos + 1) % len(remaining)]
            a = projected[prev_i]
            b = projected[cur]
            c = projected[next_i]
            cross = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
            if orientation * cross <= 1e-9:
                continue
            if any(
                point_in_triangle(projected[other], a, b, c, orientation)
                for other in remaining
                if other not in (prev_i, cur, next_i)
            ):
                continue
            triangles.append((prev_i, cur, next_i))
            del remaining[pos]
            clipped = True
            break
        if not clipped:
            return [(0, i, i + 1) for i in range(1, len(points) - 1)]
    if len(remaining) == 3:
        triangles.append(tuple(remaining))
    return triangles


def append_group_mesh(group, palette, positions, colors, indices, transform, material_override=None):
    if group.get("vertex_mode", 1) != 1:
        return
    vertex_lookup = font_vertex_by_id if is_font_shape_group(group) and not is_implicit_box_group(group) else vertex_by_id
    if group["edges"] and group["faces"]:
        for face_i, face in enumerate(group["faces"]):
            if face["material"] >= 0x80:
                continue
            color_index = None
            if material_override is not None:
                material_id = face["material"]
                if 1 <= material_id <= len(material_override):
                    color_index = material_override[material_id - 1]
                    if color_index in INSTANCE_CUBOID_NON_RENDER_COLORS:
                        continue
            loop = []
            for ref in face["refs"]:
                a, _b = directed_edge(ref, group["edges"])
                loop.append(a)
            if should_skip_font_face(group, loop, vertex_lookup):
                continue
            if len(set(loop)) < 3:
                continue
            if color_index is None:
                color_index = face.get("color_index", face["material"] & 0xFF)
            rgba = palette[color_index]
            base = len(positions)
            raw_vertices = []
            for vid in loop:
                try:
                    raw = vertex_lookup(vid, group["vertices"])
                except UnsupportedVertex:
                    raw_vertices = []
                    break
                raw_vertices.append(raw)
            if not raw_vertices:
                continue
            face_positions = [transform(raw) for raw in raw_vertices]
            for pos in face_positions:
                positions.append(pos)
                colors.append(rgba)
            for a, b, c in triangulate_polygon(face_positions):
                indices.extend([base + a, base + b, base + c])
    # Type 8 payloads are validated palette-index bitmaps, but their placement
    # records are not simple billboards. Keep them parsed but do not emit them
    # as geometry until the UV/placement mapping is accounted for.


def append_bitmap_mesh(bitmap, palette, positions, colors, indices, transform):
    width = bitmap["width"]
    height = bitmap["height"]
    pixels = bitmap["pixels"]
    for row in range(height):
        y0 = 0x4000 * (height - row - 1) / height
        y1 = 0x4000 * (height - row) / height
        for col in range(width):
            color_index = pixels[row * width + col]
            if color_index == 0:
                continue
            x0 = 0x4000 * col / width
            x1 = 0x4000 * (col + 1) / width
            rgba = palette[color_index]
            base = len(positions)
            for raw in ((x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0)):
                positions.append(transform(raw))
                colors.append(rgba)
            indices.extend([base, base + 1, base + 2, base, base + 2, base + 3])


def build_mesh(groups, palette, root=None, instances=None):
    positions = []
    colors = []
    indices = []
    if root and instances:
        root_dims = root["dims"]
        used = False
        for inst in select_static_instances(groups, instances):
            sid = inst["shape_id"]
            if sid < 0 or sid >= len(groups):
                continue
            if is_helper_instance(groups[sid], inst):
                continue
            used = True
            if "matrix" in inst:
                transform = lambda raw, inst=inst: convert_matrix_point(raw, inst["matrix"])
            else:
                transform = lambda raw, inst=inst: convert_instance_point(raw, inst["dims"], inst["loc"], root_dims, inst["rotation"])
            appearance = instance_appearance(inst)
            material_override = None
            if appearance and appearance["kind"] == 1 and is_implicit_box_group(groups[sid]):
                material_override = appearance["payload"]
            append_group_mesh(groups[sid], palette, positions, colors, indices, transform, material_override)
        if not used:
            positions.clear()
            colors.clear()
            indices.clear()
    if not indices:
        for group in groups:
            append_group_mesh(
                group,
                palette,
                positions,
                colors,
                indices,
                lambda raw, group=group: convert_point(raw, group["scale"]),
            )
    if not positions or not indices:
        raise VcaError("model produced no renderable triangles")
    return positions, colors, indices


def pad4(blob, byte=b"\x00"):
    return blob + byte * ((4 - len(blob) % 4) % 4)


def make_glb(positions, colors, indices, shape_names=None):
    pos_blob = b"".join(struct.pack("<3f", *p) for p in positions)
    col_blob = b"".join(struct.pack("<4f", *c) for c in colors)
    idx_blob = b"".join(struct.pack("<I", i) for i in indices)
    chunks = []
    offset = 0
    for blob, target in ((pos_blob, 34962), (col_blob, 34962), (idx_blob, 34963)):
        aligned = pad4(blob)
        chunks.append((offset, len(blob), len(aligned), target))
        offset += len(aligned)
    bin_blob = pad4(pos_blob) + pad4(col_blob) + pad4(idx_blob)
    mins = [min(p[i] for p in positions) for i in range(3)]
    maxs = [max(p[i] for p in positions) for i in range(3)]
    gltf = {
        "asset": {"version": "2.0", "generator": "superscapeDo3DObject.py"},
        "extensionsUsed": ["KHR_materials_unlit"],
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0}],
        "meshes": [{
            "primitives": [{
                "attributes": {"POSITION": 0, "COLOR_0": 1},
                "indices": 2,
                "material": 0,
                "mode": 4,
            }]
        }],
        "materials": [{
            "doubleSided": True,
            "pbrMetallicRoughness": {"baseColorFactor": [1, 1, 1, 1], "metallicFactor": 0, "roughnessFactor": 1},
            "extensions": {"KHR_materials_unlit": {}},
        }],
        "buffers": [{"byteLength": len(bin_blob)}],
        "bufferViews": [
            {"buffer": 0, "byteOffset": chunks[0][0], "byteLength": chunks[0][1], "target": chunks[0][3]},
            {"buffer": 0, "byteOffset": chunks[1][0], "byteLength": chunks[1][1], "target": chunks[1][3]},
            {"buffer": 0, "byteOffset": chunks[2][0], "byteLength": chunks[2][1], "target": chunks[2][3]},
        ],
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": len(positions), "type": "VEC3", "min": mins, "max": maxs},
            {"bufferView": 1, "componentType": 5126, "count": len(colors), "type": "VEC4"},
            {"bufferView": 2, "componentType": 5125, "count": len(indices), "type": "SCALAR"},
        ],
    }
    if shape_names:
        gltf["extras"] = {"superscapeShapeNames": shape_names}
    json_blob = pad4(json.dumps(gltf, separators=(",", ":")).encode("utf-8"), b" ")
    total_len = 12 + 8 + len(json_blob) + 8 + len(bin_blob)
    return (
        struct.pack("<4sII", b"glTF", 2, total_len)
        + struct.pack("<I4s", len(json_blob), b"JSON")
        + json_blob
        + struct.pack("<I4s", len(bin_blob), b"BIN\x00")
        + bin_blob
    )


def convert(input_path, output_path):
    data = Path(input_path).read_bytes()
    entries = parse_container(data)
    shp, _shp_entry = member(data, entries, ".SHP")
    pal, _pal_entry = member(data, entries, ".PAL")
    wld, _wld_entry = member(data, entries, ".WLD")
    palette = parse_palette(pal)
    groups = parse_shp(shp)
    root, instances = parse_wld_instances(wld)
    positions, colors, indices = build_mesh(groups, palette, root, instances)
    glb = make_glb(positions, colors, indices, [group.get("name") or "" for group in groups])
    out = Path(output_path)
    tmp = out.with_suffix(out.suffix + ".tmp")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_bytes(glb)
    os.chmod(tmp, 0o664)
    tmp.replace(out)
    os.chmod(out, 0o664)


def main(argv):
    if len(argv) != 3:
        print("usage: superscapeDo3DObject.py <inputFile> <outputFile>", file=sys.stderr)
        return 2
    try:
        convert(argv[1], argv[2])
    except Exception as exc:
        out = Path(argv[2])
        tmp = out.with_suffix(out.suffix + ".tmp")
        if tmp.exists():
            tmp.unlink()
        if out.exists():
            out.unlink()
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

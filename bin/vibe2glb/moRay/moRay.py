#!/usr/bin/env python3
# Vibe coded by Codex
from __future__ import annotations

import base64
import binascii
import json
import math
import os
import re
import struct
import sys
import zlib
from dataclasses import dataclass, field
from pathlib import Path


class MorayError(Exception):
    pass


def u32(data: bytes, off: int) -> int:
    if off + 4 > len(data):
        raise MorayError(f"unexpected EOF reading u32 at 0x{off:x}")
    return struct.unpack_from("<I", data, off)[0]


def u16(data: bytes, off: int) -> int:
    if off + 2 > len(data):
        raise MorayError(f"unexpected EOF reading u16 at 0x{off:x}")
    return struct.unpack_from("<H", data, off)[0]


def f32x3(data: bytes, off: int) -> tuple[float, float, float]:
    if off + 12 > len(data):
        raise MorayError(f"unexpected EOF reading vec3 at 0x{off:x}")
    return struct.unpack_from("<3f", data, off)


def f32x2(data: bytes, off: int) -> tuple[float, float]:
    if off + 8 > len(data):
        raise MorayError(f"unexpected EOF reading vec2 at 0x{off:x}")
    return struct.unpack_from("<2f", data, off)


def fixed_c_string(data: bytes, off: int, size: int, label: str) -> str:
    if off + size > len(data):
        raise MorayError(f"truncated {label} at 0x{off:x}")
    raw = data[off : off + size]
    if b"\0" in raw:
        text, padding = raw.split(b"\0", 1)
        if any(padding):
            raise MorayError(f"{label} has non-zero padding")
    else:
        text = raw
    return text.decode("latin1", "replace")


def align4(value: int) -> int:
    return (value + 3) & ~3


@dataclass
class Polygon:
    material: int
    face_normal: tuple[float, float, float]
    indices: list[int]
    index_flags: list[int]
    normals: list[tuple[float, float, float]]
    texcoords3: list[tuple[float, float, float]]


@dataclass
class ModelBlock:
    vertex_count: int
    polygon_count: int
    vertices: list[tuple[float, float, float]]
    polygons: list[Polygon]


@dataclass
class MaterialInfo:
    name: str
    base_color: tuple[float, float, float, float]
    texture_names: list[str]
    mode: int
    uv_values: tuple[float, float, float]
    layout: str


@dataclass
class MorayModel:
    source_kind: str
    strings: list[str]
    header_words: tuple[int, ...]
    point_count: int
    material_count_hint: int | None
    models: list[ModelBlock]
    raw_trailer_length: int = 0
    texture_pngs: dict[int, bytes] = field(default_factory=dict)
    materials: dict[int, MaterialInfo] = field(default_factory=dict)


def parse_strings(content: bytes) -> list[str]:
    if not content:
        return []
    parts = content.split(b"\0")
    if parts and parts[-1] == b"":
        parts = parts[:-1]
    return [part.decode("latin1", "replace") for part in parts]


def parse_string_table(content: bytes) -> tuple[list[str], dict[int, str]]:
    strings: list[str] = []
    by_offset: dict[int, str] = {}
    cursor = 0
    while cursor < len(content):
        end = content.find(b"\0", cursor)
        if end < 0:
            raise MorayError("STRS chunk is missing its final NUL terminator")
        raw = content[cursor:end]
        text = raw.decode("latin1", "replace")
        strings.append(text)
        by_offset[cursor] = text
        cursor = end + 1
    if not content:
        return [], {}
    return strings, by_offset


def parse_mdls(data: bytes) -> MorayModel:
    if len(data) < 44:
        raise MorayError("MDLS file is shorter than its fixed 44-byte header")
    if data[:4] != b"MDLS":
        raise MorayError("unsupported signature; expected MDLS")

    payload_size = u32(data, 4)
    if payload_size != len(data) - 8:
        raise MorayError(
            f"MDLS payload size mismatch: header says {payload_size}, file has {len(data) - 8}"
        )
    header_words = struct.unpack_from("<9I", data, 8)

    strings: list[str] = []
    string_offsets: dict[int, str] = {}
    mats_content: bytes | None = None
    material_count_hint: int | None = None
    point_count = 0
    models: list[ModelBlock] = []

    off = 44
    seen_chunks = 0
    while off < len(data):
        if off + 8 > len(data):
            raise MorayError(f"truncated top-level chunk header at 0x{off:x}")
        tag = data[off : off + 4]
        size = u32(data, off + 4)
        content_off = off + 8
        content_end = content_off + size
        if content_end > len(data):
            raise MorayError(f"top-level chunk {tag!r} at 0x{off:x} overruns EOF")
        pad_end = align4(content_end)
        if pad_end > len(data):
            raise MorayError(f"top-level chunk {tag!r} padding overruns EOF")
        if any(data[content_end:pad_end]):
            raise MorayError(f"top-level chunk {tag!r} has non-zero alignment padding")

        content = data[content_off:content_end]
        if tag == b"STRS":
            strings, string_offsets = parse_string_table(content)
        elif tag == b"PNTS":
            if size % 16 != 0:
                raise MorayError("PNTS chunk size is not a multiple of 16 bytes")
            point_count += size // 16
        elif tag == b"MATS":
            mats_content = content
        elif tag == b"MOD0":
            models.append(parse_mod0(content, content_off))
        else:
            raise MorayError(f"unknown top-level MDLS chunk {tag!r} at 0x{off:x}")

        seen_chunks += 1
        off = pad_end

    if seen_chunks == 0:
        raise MorayError("MDLS file has no chunks")
    if not models:
        raise MorayError("MDLS file has no MOD0 geometry chunks")
    material_infos: dict[int, MaterialInfo] = {}
    if mats_content is not None:
        material_infos = parse_mdls_mats(mats_content, string_offsets)
        material_count_hint = len(material_infos)
        apply_mdls_lod_filter(models, material_infos, strings)
    return MorayModel(
        "MDLS",
        strings,
        header_words,
        point_count,
        material_count_hint,
        models,
        materials=material_infos,
    )


MDLS_MATERIAL_MODES = {0, 2, 3, 4, 5, 0x23, 0x25}


def mdls_word(data: bytes, offset: int) -> int:
    if offset + 4 > len(data):
        raise MorayError(f"truncated MDLS MATS word at 0x{offset:x}")
    return struct.unpack_from("<I", data, offset)[0]


def mdls_float_from_word(word: int) -> float:
    value = struct.unpack("<f", struct.pack("<I", word))[0]
    if not math.isfinite(value) or abs(value) > 1.0e6:
        raise MorayError("MDLS MATS transform word is not a finite float")
    return value


def mdls_color_from_word(word: int) -> tuple[float, float, float, float]:
    raw = word.to_bytes(4, "little")
    if raw[3] not in (0, 255):
        raise MorayError("MDLS MATS color alpha/control byte is not 0 or 255")
    return (raw[0] / 255.0, raw[1] / 255.0, raw[2] / 255.0, 1.0)


def mdls_offset_name(offset: int, string_offsets: dict[int, str]) -> str | None:
    if offset == 0 and offset not in string_offsets:
        return None
    if offset not in string_offsets:
        raise MorayError(f"MDLS MATS string offset 0x{offset:x} is not present in STRS")
    name = string_offsets[offset]
    return name or None


def mdls_material_texture_names(
    offsets: list[int], string_offsets: dict[int, str]
) -> list[str]:
    names: list[str] = []
    for offset in offsets:
        name = mdls_offset_name(offset, string_offsets)
        if name is not None and name not in names:
            names.append(name)
    return names


def parse_mdls_mats(
    content: bytes, string_offsets: dict[int, str]
) -> dict[int, MaterialInfo]:
    records, tail_offsets = parse_mdls_mats_records(content, string_offsets)
    materials: dict[int, MaterialInfo] = {}
    for index, (layout, mode, color_word, uv_words, texture_offsets) in enumerate(records):
        color = mdls_color_from_word(color_word)
        uv_values = tuple(mdls_float_from_word(word) for word in uv_words)
        texture_names = mdls_material_texture_names(texture_offsets, string_offsets)
        if texture_names:
            name = "/".join(texture_names)
        else:
            name = f"material_{index}"
        materials[index] = MaterialInfo(name, color, texture_names, mode, uv_values, layout)

    for offset in tail_offsets:
        mdls_offset_name(offset, string_offsets)
    return materials


def parse_mdls_mats_records(
    content: bytes, string_offsets: dict[int, str]
) -> tuple[list[tuple[str, int, int, tuple[int, int, int], list[int]]], list[int]]:
    def is_texture_offset(word: int) -> bool:
        return word == 0 or word in string_offsets

    def is_color_word(word: int) -> bool:
        return word.to_bytes(4, "little")[3] in (0, 255)

    def is_float_word(word: int) -> bool:
        try:
            mdls_float_from_word(word)
        except MorayError:
            return False
        return True

    def tail_offsets(pos: int) -> list[int] | None:
        remaining = len(content) - pos
        if remaining >= 28 or remaining % 4:
            return None
        offsets = [mdls_word(content, item_pos) for item_pos in range(pos, len(content), 4)]
        if all(is_texture_offset(offset) for offset in offsets):
            return offsets
        return None

    def variants(pos: int) -> list[tuple[str, int, int, int, tuple[int, int, int], list[int]]]:
        out: list[tuple[str, int, int, int, tuple[int, int, int], list[int]]] = []
        if pos + 36 <= len(content):
            words = [mdls_word(content, pos + i * 4) for i in range(9)]
            if (
                is_texture_offset(words[0])
                and words[1] == 0
                and is_texture_offset(words[2])
                and words[3] in MDLS_MATERIAL_MODES
                and is_color_word(words[4])
                and all(is_float_word(word) for word in words[5:8])
                and words[8] == 0
            ):
                out.append(("pair_sep", 36, words[3], words[4], tuple(words[5:8]), [words[0], words[2]]))
        if pos + 32 <= len(content):
            words = [mdls_word(content, pos + i * 4) for i in range(8)]
            if (
                is_texture_offset(words[0])
                and is_texture_offset(words[1])
                and words[2] in MDLS_MATERIAL_MODES
                and is_color_word(words[3])
                and all(is_float_word(word) for word in words[4:7])
                and words[7] == 0
            ):
                out.append(("pair_a", 32, words[2], words[3], tuple(words[4:7]), [words[0], words[1]]))
            if (
                is_texture_offset(words[0])
                and words[1] in MDLS_MATERIAL_MODES
                and is_color_word(words[2])
                and all(is_float_word(word) for word in words[3:6])
                and words[6] == 0
                and is_texture_offset(words[7])
            ):
                out.append(("pair_b", 32, words[1], words[2], tuple(words[3:6]), [words[0], words[7]]))
        if pos + 28 <= len(content):
            words = [mdls_word(content, pos + i * 4) for i in range(7)]
            if (
                words[0] in MDLS_MATERIAL_MODES
                and is_color_word(words[1])
                and all(is_float_word(word) for word in words[2:5])
                and words[5] == 0
                and is_texture_offset(words[6])
            ):
                out.append(("single", 28, words[0], words[1], tuple(words[2:5]), [words[6]]))
        return out

    from functools import lru_cache

    @lru_cache(maxsize=None)
    def parse_from(pos: int) -> tuple[
        list[tuple[str, int, int, tuple[int, int, int], list[int]]], list[int]
    ] | None:
        if pos == len(content):
            return [], []
        tail = tail_offsets(pos)
        if tail is not None:
            return [], tail
        for layout, size, mode, color_word, uv_words, texture_offsets in variants(pos):
            parsed = parse_from(pos + size)
            if parsed is not None:
                records, tail_values = parsed
                return [(layout, mode, color_word, uv_words, texture_offsets)] + records, tail_values
        return None

    parsed = parse_from(0)
    if parsed is None:
        raise MorayError("MDLS MATS chunk does not match any supported material-record layout")
    return parsed


MDLS_LOD_NAME_RE = re.compile(r"^(.+)_([0-9]+)_[^_].*$")


def mdls_lod_key(material: MaterialInfo | None) -> tuple[str, int] | None:
    if material is None or not material.texture_names:
        return None
    match = MDLS_LOD_NAME_RE.match(material.texture_names[0])
    if match is None:
        return None
    return match.group(1).lower(), int(match.group(2))


def apply_mdls_lod_filter(
    models: list[ModelBlock], materials: dict[int, MaterialInfo], strings: list[str]
) -> None:
    used_materials = {
        polygon.material
        for model in models
        for polygon in model.polygons
        if polygon.material in materials
    }
    lods_by_base: dict[str, set[int]] = {}
    material_lods: dict[int, tuple[str, int]] = {}
    for material_index in used_materials:
        key = mdls_lod_key(materials.get(material_index))
        if key is None:
            continue
        base, lod = key
        material_lods[material_index] = key
        lods_by_base.setdefault(base, set()).add(lod)

    selected_lod = {
        base: min(lods)
        for base, lods in lods_by_base.items()
        if len(lods) > 1
    }
    if not selected_lod:
        return

    removed = 0
    for model in models:
        kept: list[Polygon] = []
        for polygon in model.polygons:
            key = material_lods.get(polygon.material)
            if key is not None and key[0] in selected_lod and key[1] != selected_lod[key[0]]:
                removed += 1
                continue
            kept.append(polygon)
        model.polygons = kept
        model.polygon_count = len(kept)
    strings.append(
        "mdls_lod_filter:"
        + ",".join(f"{base}=LOD{lod}" for base, lod in sorted(selected_lod.items()))
        + f":removed_polygons={removed}"
    )


def face_normal_from_vertices(
    a: tuple[float, float, float],
    b: tuple[float, float, float],
    c: tuple[float, float, float],
) -> tuple[float, float, float]:
    ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
    normal = (uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx)
    return normal_or_face(normal, (0.0, 1.0, 0.0))


def parse_mdl_bang(data: bytes) -> MorayModel:
    if len(data) < 8:
        raise MorayError("MDL! file is shorter than its signature/version fields")
    if data[:4] != b"MDL!":
        raise MorayError("unsupported signature; expected MDL!")
    if u32(data, 4) == 2:
        return parse_mdl_bang_v2(data)
    return parse_mdl_bang_v1(data)


def parse_mdl5(data: bytes) -> MorayModel:
    if len(data) < 64:
        raise MorayError("MDL5 file is shorter than its fixed header")
    if data[:4] != b"MDL\x05":
        raise MorayError("unsupported signature; expected MDL5")
    if data[4] != 1 or data[7] != 0:
        raise MorayError("MDL5 fixed version bytes are not the observed 01/00 pair")

    object_count = u16(data, 5)
    material_count = struct.unpack_from(">H", data, 8)[0]
    if data[10:12] != b"\0\0":
        raise MorayError("MDL5 material-count padding word is non-zero")
    header_words = (data[4], object_count, material_count) + struct.unpack_from("<4I", data, 12)
    if not (1 <= object_count <= 10000):
        raise MorayError(f"MDL5 object count {object_count} is outside the supported range")
    if material_count > 10000:
        raise MorayError(f"MDL5 material count {material_count} is outside the supported range")

    object_offsets = find_mdl5_object_offsets(data, object_count)
    prefix_end = object_offsets[0]
    prefix_records = parse_mdl5_prefix_records(data, 0x1D, prefix_end)

    material_names: list[str] = []
    material_to_index: dict[str, int] = {}
    models: list[ModelBlock] = []
    strings: list[str] = []
    cursor = object_offsets[0]
    for object_index in range(object_count):
        expected_start = object_offsets[object_index]
        if cursor != expected_start:
            raise MorayError(
                f"MDL5 parser expected object {object_index} at 0x{expected_start:x}, "
                f"but stopped at 0x{cursor:x}"
            )
        name, cursor = read_mdl5_string(data, cursor, "MDL5 object name")
        material_name, cursor = read_mdl5_string(data, cursor, "MDL5 object material")
        vertex_count = u16(data, cursor)
        face_count = u16(data, cursor + 2)
        cursor += 4
        if vertex_count == 0 or face_count == 0:
            raise MorayError(f"MDL5 object {name!r} has no polygon geometry")
        if material_name not in material_to_index:
            material_to_index[material_name] = len(material_names)
            material_names.append(material_name)
        material_index = material_to_index[material_name]

        positions_end = cursor + vertex_count * 12
        index_end = positions_end + face_count * 12
        uv_end = index_end + vertex_count * 8
        trailer_end = uv_end + 12
        if trailer_end > len(data):
            raise MorayError(f"MDL5 object {name!r} overruns EOF")
        next_expected = (
            object_offsets[object_index + 1] if object_index + 1 < object_count else trailer_end
        )
        if trailer_end != next_expected:
            raise MorayError(
                f"MDL5 object {name!r} ends at 0x{trailer_end:x}, expected 0x{next_expected:x}"
            )

        vertices = [f32x3(data, cursor + i * 12) for i in range(vertex_count)]
        if not all(all(math.isfinite(value) and abs(value) < 1.0e8 for value in vertex) for vertex in vertices):
            raise MorayError(f"MDL5 object {name!r} contains invalid vertex coordinates")
        cursor = positions_end

        triangles: list[tuple[int, int, int]] = []
        for face_index in range(face_count):
            tri = struct.unpack_from("<3I", data, cursor + face_index * 12)
            if any(index >= vertex_count for index in tri):
                raise MorayError(
                    f"MDL5 object {name!r} face {face_index} references a vertex outside the table"
                )
            triangles.append(tri)
        cursor = index_end

        texcoords = [f32x2(data, cursor + i * 8) for i in range(vertex_count)]
        if not all(all(math.isfinite(value) for value in uv) for uv in texcoords):
            raise MorayError(f"MDL5 object {name!r} contains invalid texture coordinates")
        cursor = uv_end
        object_tail = struct.unpack_from("<3f", data, cursor)
        if not all(math.isfinite(value) for value in object_tail):
            raise MorayError(f"MDL5 object {name!r} has invalid trailer floats")
        cursor = trailer_end

        polygons: list[Polygon] = []
        for tri in triangles:
            face_normal = face_normal_from_vertices(vertices[tri[0]], vertices[tri[1]], vertices[tri[2]])
            polygons.append(
                Polygon(
                    material_index,
                    face_normal,
                    list(tri),
                    [0, 0, 0],
                    [face_normal, face_normal, face_normal],
                    [
                        (texcoords[tri[0]][0], texcoords[tri[0]][1], 0.0),
                        (texcoords[tri[1]][0], texcoords[tri[1]][1], 0.0),
                        (texcoords[tri[2]][0], texcoords[tri[2]][1], 0.0),
                    ],
                )
            )
        models.append(ModelBlock(vertex_count, face_count, vertices, polygons))
        strings.append(f"0x{expected_start:x}:{name}:{material_name}")

    table_materials, material_table_end = parse_mdl5_material_table(data, cursor, material_count)
    for material_name, _texture_path, _scale in table_materials:
        if material_name not in material_to_index:
            material_to_index[material_name] = len(material_names)
            material_names.append(material_name)
    trailer_records, trailer_end = parse_mdl5_animation_trailer(data, material_table_end)
    if trailer_end != len(data):
        raise MorayError(f"MDL5 parser stopped at 0x{trailer_end:x}, file ends at 0x{len(data):x}")

    metadata = (
        len(data),
        object_count,
        material_count,
        prefix_end - 0x1D,
        len(prefix_records),
        len(trailer_records),
        material_table_end - cursor,
        len(data) - material_table_end,
    ) + header_words
    return MorayModel("MDL5 counted mesh scene", material_names + strings + trailer_records, metadata, 0, material_count, models)


def read_mdl5_string(data: bytes, offset: int, label: str) -> tuple[str, int]:
    if offset >= len(data):
        raise MorayError(f"truncated {label} length")
    length = data[offset]
    if not (1 <= length <= 96):
        raise MorayError(f"{label} at 0x{offset:x} has unsupported length {length}")
    start = offset + 1
    end = start + length
    if end > len(data):
        raise MorayError(f"truncated {label} at 0x{offset:x}")
    raw = data[start:end]
    if not all(32 <= value <= 126 for value in raw):
        raise MorayError(f"{label} at 0x{offset:x} contains non-printable bytes")
    return raw.decode("latin1"), end


def mdl5_object_candidate(data: bytes, offset: int) -> tuple[int, int, int] | None:
    try:
        _name, cursor = read_mdl5_string(data, offset, "MDL5 candidate object name")
        _material, cursor = read_mdl5_string(data, cursor, "MDL5 candidate material")
    except MorayError:
        return None
    if cursor + 4 > len(data):
        return None
    vertex_count = u16(data, cursor)
    face_count = u16(data, cursor + 2)
    if not (1 <= vertex_count <= 100000 and 1 <= face_count <= 100000):
        return None
    data_offset = cursor + 4
    end = data_offset + vertex_count * 12 + face_count * 12 + vertex_count * 8 + 12
    if end > len(data):
        return None
    try:
        first_vertex = f32x3(data, data_offset)
    except MorayError:
        return None
    if not all(math.isfinite(value) and abs(value) < 1.0e8 for value in first_vertex):
        return None
    return end, vertex_count, face_count


def find_mdl5_object_offsets(data: bytes, object_count: int) -> list[int]:
    candidates: dict[int, int] = {}
    for offset in range(0x1D, len(data) - 16):
        candidate = mdl5_object_candidate(data, offset)
        if candidate is not None:
            candidates[offset] = candidate[0]
    for start in sorted(candidates):
        offsets = [start]
        cursor = candidates[start]
        while len(offsets) < object_count and cursor in candidates:
            offsets.append(cursor)
            cursor = candidates[cursor]
        if len(offsets) == object_count:
            return offsets
    raise MorayError("MDL5 object table could not be located as a counted contiguous sequence")


def parse_mdl5_prefix_records(data: bytes, offset: int, end: int) -> list[str]:
    records: list[str] = []
    cursor = offset
    while cursor < end:
        name, cursor = read_mdl5_string(data, cursor, "MDL5 prefix scene record")
        if name.lower().startswith("camera"):
            size = 32
        elif name.lower().startswith("omni"):
            size = 28
        else:
            raise MorayError(f"MDL5 prefix record {name!r} has unknown byte size")
        if cursor + size > end:
            raise MorayError(f"MDL5 prefix record {name!r} overruns the object table")
        body = data[cursor : cursor + size]
        if size % 4 or not all(math.isfinite(value) for value in struct.unpack(f"<{size // 4}f", body)):
            raise MorayError(f"MDL5 prefix record {name!r} has invalid float payload")
        records.append(f"prefix:{name}:{size}")
        cursor += size
    if cursor != end:
        raise MorayError("MDL5 prefix parser did not close exactly")
    return records


def parse_mdl5_material_table(
    data: bytes, offset: int, material_count: int
) -> tuple[list[tuple[str, str, tuple[float, float, float]]], int]:
    materials: list[tuple[str, str, tuple[float, float, float]]] = []
    cursor = offset
    for index in range(material_count):
        name, cursor = read_mdl5_string(data, cursor, f"MDL5 material {index} name")
        path, cursor = read_mdl5_string(data, cursor, f"MDL5 material {index} texture path")
        if cursor + 36 > len(data):
            raise MorayError(f"MDL5 material {index} overruns EOF")
        scale = struct.unpack_from("<3f", data, cursor)
        cursor += 12
        tail = data[cursor : cursor + 24]
        cursor += 24
        if not all(math.isfinite(value) for value in scale):
            raise MorayError(f"MDL5 material {index} has invalid scale floats")
        if any(tail):
            raise MorayError(f"MDL5 material {index} has non-zero 24-byte tail")
        materials.append((name, path, scale))
    return materials, cursor


def valid_mdl5_trailer_name_at(data: bytes, offset: int) -> bool:
    if offset == len(data):
        return True
    try:
        _name, _end = read_mdl5_string(data, offset, "MDL5 trailer name")
        return True
    except MorayError:
        return False


def parse_mdl5_animation_trailer(data: bytes, offset: int) -> tuple[list[str], int]:
    records: list[str] = []
    cursor = offset
    while cursor < len(data):
        record_start = cursor
        name, cursor = read_mdl5_string(data, cursor, "MDL5 animation/controller record name")
        if cursor + 20 > len(data):
            raise MorayError(f"MDL5 animation/controller record {name!r} has a truncated header")
        header = struct.unpack_from("<5I", data, cursor)
        options = [
            ("key40", header[0], 40),
            ("key16", header[0], 16),
            ("key28", header[3], 28),
        ]
        chosen: tuple[str, int, int, int] | None = None
        for kind, count, stride in options:
            end = cursor + 20 + count * stride
            if count <= 100000 and end <= len(data) and valid_mdl5_trailer_name_at(data, end):
                chosen = (kind, count, stride, end)
                break
        if chosen is None:
            raise MorayError(f"MDL5 animation/controller record {name!r} has unknown layout")
        kind, count, stride, end = chosen
        payload = data[cursor + 20 : end]
        if len(payload) != count * stride:
            raise MorayError(f"MDL5 animation/controller record {name!r} has an internal size mismatch")
        records.append(f"trailer:0x{record_start:x}:{name}:{kind}:{count}")
        cursor = end
    return records, cursor


def parse_mdl3_archive(data: bytes) -> MorayModel:
    if len(data) < 0x100:
        raise MorayError("MDL3 archive is shorter than its fixed table prefix")
    if data[:4] != b"MDL\x03":
        raise MorayError("unsupported signature; expected MDL3")
    entry_count = u32(data, 4)
    table_end = 0x100 + entry_count * 12
    if entry_count == 0 or table_end > len(data):
        raise MorayError("MDL3 archive entry table does not fit in the file")
    summary_words = struct.unpack_from("<5I", data, 8)
    if any(data[0x1C:0x100]):
        raise MorayError("MDL3 archive fixed header padding is non-zero")

    previous_offset = table_end
    names: list[str] = []
    for index in range(entry_count):
        record_offset = 0x100 + index * 12
        flag, entry_offset, entry_size = struct.unpack_from("<3I", data, record_offset)
        if flag not in (0x40, 0x41):
            raise MorayError(f"MDL3 archive entry {index} has unsupported flag 0x{flag:x}")
        if entry_offset < table_end or entry_offset + entry_size > len(data):
            raise MorayError(f"MDL3 archive entry {index} is outside the file")
        if entry_offset < previous_offset:
            raise MorayError(f"MDL3 archive entry {index} offsets are not sorted")
        name_end = data.find(b"\0", entry_offset, min(entry_offset + entry_size, entry_offset + 128))
        if name_end < 0:
            raise MorayError(f"MDL3 archive entry {index} has no NUL-terminated name")
        raw_name = data[entry_offset:name_end]
        if raw_name and all(32 <= value <= 126 for value in raw_name):
            names.append(raw_name.decode("latin1"))
        previous_offset = entry_offset

    raise MorayError(
        f"MDL3 archive table validated with {entry_count} entries "
        f"({', '.join(names[:5])}); embedded Granny/RAD GRN geometry is not implemented"
    )


MDLC_KEY = b"SoftTronics (C) 1994, Munich, Germany"
MDLC_KEY_PHASES = {
    b"29": 31,
    b"37": 31,
    b"41": 31,
    b"60": 0,
    b"77": 0,
}


@dataclass
class MDL0Record:
    start: int
    end: int
    layout: str
    name: str
    material_name: str
    vertices: list[tuple[float, float, float]]
    normals: list[tuple[float, float, float]]
    texcoords: list[tuple[float, float]]
    triangles: list[tuple[int, int, int]]


def mdl0_size24(data: bytes, offset: int) -> int:
    if offset + 4 > len(data):
        raise MorayError(f"truncated MDL NUL 24-bit chunk size at 0x{offset:x}")
    return data[offset + 1] | (data[offset + 2] << 8) | (data[offset + 3] << 16)


def parse_mdl0(data: bytes) -> MorayModel:
    if len(data) < 32:
        raise MorayError("MDL NUL file is shorter than its fixed prefix")
    if data[:4] != b"MDL\0":
        raise MorayError("unsupported signature; expected MDL NUL")

    try:
        return parse_mdl0_chunked(data)
    except MorayError as chunked_error:
        chunked_reason = str(chunked_error)

    records = scan_mdl0_records(data)
    if not records:
        raise MorayError(
            "MDL NUL header recognized, but no supported object records were found; "
            f"chunked-table parser rejected it: {chunked_reason}"
        )

    models: list[ModelBlock] = []
    strings: list[str] = []
    for material, record in enumerate(records):
        polygons: list[Polygon] = []
        for tri in record.triangles:
            face = face_normal_from_vertices(
                record.vertices[tri[0]], record.vertices[tri[1]], record.vertices[tri[2]]
            )
            polygons.append(
                Polygon(
                    material,
                    face,
                    list(tri),
                    [0, 0, 0],
                    [record.normals[tri[0]], record.normals[tri[1]], record.normals[tri[2]]],
                    [
                        (record.texcoords[tri[0]][0], record.texcoords[tri[0]][1], 0.0),
                        (record.texcoords[tri[1]][0], record.texcoords[tri[1]][1], 0.0),
                        (record.texcoords[tri[2]][0], record.texcoords[tri[2]][1], 0.0),
                    ],
                )
            )
        models.append(ModelBlock(len(record.vertices), len(record.triangles), record.vertices, polygons))
        strings.append(
            f"0x{record.start:x}:layout_{record.layout}:{record.name}:{record.material_name}"
        )

    metadata = (
        len(data),
        u32(data, 4),
        u32(data, 8),
        len(records),
        sum(len(record.vertices) for record in records),
        sum(len(record.triangles) for record in records),
    )
    return MorayModel("MDL NUL object records", strings, metadata, 0, len(records), models)


def parse_mdl0_chunked(data: bytes) -> MorayModel:
    if u32(data, 4) != 0x201:
        raise MorayError("MDL NUL chunked table version word is not 0x201")

    if data[8:12] == b"\x00\x64\x00\x14" and u32(data, 12) == 4:
        vertex_count = u32(data, 16)
        pos = 0x14
        prefix_words = (u32(data, 4), u32(data, 8), u32(data, 12), vertex_count)
    elif data[8:12] == b"\x00\x64\x00\x0a" and u32(data, 12) == 1:
        if data[0x10:0x16] != b"\x00\x14\x04\x00\x00\x00":
            raise MorayError("MDL NUL compact chunked prefix has unknown descriptor")
        vertex_count = u32(data, 0x16)
        pos = 0x1a
        prefix_words = (u32(data, 4), u32(data, 8), u32(data, 12), u32(data, 0x10), vertex_count)
    else:
        raise MorayError("MDL NUL prefix is not a supported chunked-table descriptor")

    if not (3 <= vertex_count <= 100000):
        raise MorayError(f"MDL NUL chunked table has unsupported vertex count {vertex_count}")

    arrays: dict[int, list[tuple[float, ...]]] = {}
    triangles_by_material: list[tuple[int, tuple[int, int, int]]] = []
    strings: list[str] = [f"chunked_vertex_count={vertex_count}"]
    material_count_hint = 1
    saw_index_chunk = False

    while pos < len(data):
        if all(value == 0 for value in data[pos:]):
            strings.append(f"trailing_zero_bytes={len(data) - pos}")
            pos = len(data)
            break

        if pos + 5 > len(data):
            raise MorayError(f"truncated MDL NUL chunk header at 0x{pos:x}")
        tag = data[pos]
        size = mdl0_size24(data, pos)
        flag = data[pos + 4]
        end = pos + 5 + size
        if flag != 0:
            raise MorayError(f"MDL NUL chunk 0x{tag:02x} at 0x{pos:x} has non-zero flag")
        if end > len(data):
            raise MorayError(f"MDL NUL chunk 0x{tag:02x} at 0x{pos:x} overruns EOF")

        if tag in (0x15, 0x16, 0x17, 0x18):
            arrays[tag] = parse_mdl0_array_chunk(data, pos, end, vertex_count)
        elif tag == 0x32:
            triangles_by_material.extend(parse_mdl0_index_chunk(data, pos, end, vertex_count))
            saw_index_chunk = True
            if triangles_by_material:
                material_count_hint = max(material for material, _ in triangles_by_material) + 1
        elif tag == 0x78:
            color_sets = parse_mdl0_color_section(data, pos, end)
            strings.append(f"color_sets={color_sets}")
        elif tag == 0x96:
            texture_name = parse_mdl0_texture_name_chunk(data, pos, end)
            strings.append(f"texture={texture_name}")
        elif tag == 0x97:
            material_names = parse_mdl0_material_section(data, pos, end)
            strings.extend(f"material_texture={name}" for name in material_names)
        else:
            raise MorayError(f"unsupported MDL NUL chunk tag 0x{tag:02x} at 0x{pos:x}")
        pos = end

    if pos != len(data):
        raise MorayError("MDL NUL chunked table did not consume the complete file")
    for tag, label in ((0x15, "position"), (0x16, "normal")):
        if tag not in arrays:
            raise MorayError(f"MDL NUL chunked table is missing the {label} array")
    if not saw_index_chunk:
        raise MorayError("MDL NUL chunked table is missing the index chunk")
    if not triangles_by_material:
        raise MorayError("MDL NUL chunked table has no non-degenerate triangles")

    vertices = [tuple(values[:3]) for values in arrays[0x15]]
    normals = [normal_or_face(tuple(values[:3]), (0.0, 1.0, 0.0)) for values in arrays[0x16]]
    texcoords = [(0.0, 0.0)] * vertex_count
    if 0x18 in arrays:
        texcoords = [(values[0], values[1]) for values in arrays[0x18]]

    polygons: list[Polygon] = []
    for material, tri in triangles_by_material:
        face = face_normal_from_vertices(vertices[tri[0]], vertices[tri[1]], vertices[tri[2]])
        polygons.append(
            Polygon(
                material,
                face,
                list(tri),
                [0, 0, 0],
                [normals[tri[0]], normals[tri[1]], normals[tri[2]]],
                [
                    (texcoords[tri[0]][0], texcoords[tri[0]][1], 0.0),
                    (texcoords[tri[1]][0], texcoords[tri[1]][1], 0.0),
                    (texcoords[tri[2]][0], texcoords[tri[2]][1], 0.0),
                ],
            )
        )

    strings.insert(0, f"triangles={len(polygons)}")
    return MorayModel(
        "MDL NUL chunked tables",
        strings,
        prefix_words + (len(data),),
        vertex_count,
        material_count_hint,
        [ModelBlock(vertex_count, len(polygons), vertices, polygons)],
    )


def parse_mdl0_array_chunk(
    data: bytes, pos: int, end: int, expected_count: int
) -> list[tuple[float, ...]]:
    tag = data[pos]
    count = u32(data, pos + 5)
    dimension = u32(data, pos + 9)
    if count != expected_count:
        raise MorayError(
            f"MDL NUL array chunk 0x{tag:02x} count {count} does not match header count {expected_count}"
        )
    expected_dimension = 2 if tag == 0x18 else 3
    if dimension != expected_dimension:
        raise MorayError(
            f"MDL NUL array chunk 0x{tag:02x} dimension {dimension}, expected {expected_dimension}"
        )
    payload = pos + 13
    expected_end = payload + count * dimension * 4
    if expected_end != end:
        raise MorayError(f"MDL NUL array chunk 0x{tag:02x} byte count is inconsistent")

    values: list[tuple[float, ...]] = []
    for index in range(count):
        item = struct.unpack_from("<" + "f" * dimension, data, payload + index * dimension * 4)
        if not all(math.isfinite(value) and abs(value) < 1.0e10 for value in item):
            raise MorayError(f"MDL NUL array chunk 0x{tag:02x} contains a non-finite value")
        values.append(item)
    return values


def parse_mdl0_index_chunk(
    data: bytes, pos: int, end: int, vertex_count: int
) -> list[tuple[int, tuple[int, int, int]]]:
    group_count = u32(data, pos + 5)
    count_a = u32(data, pos + 9)
    count_b = u32(data, pos + 13)
    if count_a != vertex_count or count_b != vertex_count:
        raise MorayError("MDL NUL index chunk vertex-count copies do not match the array count")

    q = pos + 17
    triangles: list[tuple[int, tuple[int, int, int]]] = []
    for _ in range(group_count):
        if q + 8 > end:
            raise MorayError("MDL NUL index group header overruns its chunk")
        material_page = data[q]
        primitive = data[q + 1]
        material_index = data[q + 2]
        index_width = data[q + 3]
        index_count = u32(data, q + 4)
        q += 8
        if material_page not in (0, 1):
            raise MorayError("MDL NUL index group has an unsupported material page")
        if primitive not in (4, 5, 6):
            raise MorayError(f"MDL NUL index group has unsupported primitive {primitive}")
        if index_width != 2:
            raise MorayError("MDL NUL index group does not use 16-bit indices")
        if q + index_count * 2 > end:
            raise MorayError("MDL NUL index group indices overrun their chunk")
        indices = list(struct.unpack_from("<" + "H" * index_count, data, q))
        q += index_count * 2
        if any(index >= vertex_count for index in indices):
            raise MorayError("MDL NUL index group references a vertex outside the array")

        if primitive == 4:
            if index_count % 3:
                raise MorayError("MDL NUL triangle-list index count is not divisible by 3")
            for i in range(0, index_count, 3):
                add_mdl0_triangle(triangles, material_index, (indices[i], indices[i + 1], indices[i + 2]))
        elif primitive == 5:
            for i in range(index_count - 2):
                if i & 1:
                    tri = (indices[i + 1], indices[i], indices[i + 2])
                else:
                    tri = (indices[i], indices[i + 1], indices[i + 2])
                add_mdl0_triangle(triangles, material_index, tri)
        else:
            for i in range(1, index_count - 1):
                add_mdl0_triangle(triangles, material_index, (indices[0], indices[i], indices[i + 1]))

    if q != end:
        raise MorayError("MDL NUL index chunk has unconsumed bytes")
    return triangles


def add_mdl0_triangle(
    triangles: list[tuple[int, tuple[int, int, int]]],
    material_index: int,
    tri: tuple[int, int, int],
) -> None:
    if tri[0] == tri[1] or tri[1] == tri[2] or tri[0] == tri[2]:
        return
    triangles.append((material_index, tri))


def parse_mdl0_texture_name_chunk(data: bytes, pos: int, end: int) -> str:
    if pos + 8 > end:
        raise MorayError("MDL NUL texture-name chunk is truncated")
    name_length = u16(data, pos + 5)
    name_start = pos + 7
    name_end = name_start + name_length
    if name_end + 1 != end or data[name_end] != 0:
        raise MorayError("MDL NUL texture-name chunk length does not match its NUL string")
    raw = data[name_start:name_end]
    if not raw or not all(32 <= value <= 126 for value in raw):
        raise MorayError("MDL NUL texture-name chunk contains non-printable bytes")
    return raw.decode("latin1")


def parse_mdl0_color_section(data: bytes, pos: int, end: int) -> int:
    color_set_count = u32(data, pos + 5)
    q = pos + 9
    for _ in range(color_set_count):
        if q + 4 > end or data[q : q + 4] != b"COL\x01":
            raise MorayError("MDL NUL color section is missing a COL marker")
        q += 4
        for expected_tag in (1, 3, 4, 5):
            if q + 5 > end:
                raise MorayError("MDL NUL color subchunk is truncated")
            tag = data[q]
            size = mdl0_size24(data, q)
            flag = data[q + 4]
            if tag != expected_tag or size != 12 or flag != 0:
                raise MorayError("MDL NUL color subchunk has an unexpected header")
            values = struct.unpack_from("<3f", data, q + 5)
            if not all(math.isfinite(value) and abs(value) < 1.0e10 for value in values):
                raise MorayError("MDL NUL color subchunk contains a non-finite value")
            q += 17
        if q >= end or data[q] != 0:
            raise MorayError("MDL NUL color record is missing its terminator byte")
        q += 1
    if q != end:
        raise MorayError("MDL NUL color section has unconsumed bytes")
    return color_set_count


def parse_mdl0_material_section(data: bytes, pos: int, end: int) -> list[str]:
    q = pos + 5
    q, texture_names = parse_mdl0_mtl_block(data, q, end)
    if q != end:
        raise MorayError("MDL NUL material section has unconsumed bytes")
    return texture_names


def parse_mdl0_mtl_block(data: bytes, pos: int, limit: int) -> tuple[int, list[str]]:
    if pos + 4 > limit or data[pos : pos + 4] != b"MTL\0":
        raise MorayError(f"MDL NUL material block missing MTL marker at 0x{pos:x}")
    q = pos + 4
    texture_names: list[str] = []

    if q + 5 > limit or data[q] != 1 or mdl0_size24(data, q) != 73 or data[q + 4] != 0:
        raise MorayError("MDL NUL material block is missing its 73-byte property chunk")
    values = struct.unpack_from("<16f", data, q + 5)
    if not all(math.isfinite(value) and abs(value) < 1.0e10 for value in values):
        raise MorayError("MDL NUL material property chunk contains a non-finite float")
    q += 78

    while q < limit and data[q] != 0:
        tag = data[q]
        size = mdl0_size24(data, q)
        flag = data[q + 4]
        chunk_end = q + 5 + size
        if flag != 0 or chunk_end > limit:
            raise MorayError("MDL NUL material subchunk has an invalid header")
        if tag == 2:
            texture_names.append(parse_mdl0_texture_name_chunk(data, q, chunk_end))
        elif tag == 3:
            if size != 64:
                raise MorayError("MDL NUL material matrix chunk is not 64 bytes")
            matrix = struct.unpack_from("<16f", data, q + 5)
            if not all(math.isfinite(value) and abs(value) < 1.0e10 for value in matrix):
                raise MorayError("MDL NUL material matrix chunk contains a non-finite float")
        elif tag == 4:
            count = u32(data, q + 5)
            nested = q + 9
            for _ in range(count):
                nested, nested_names = parse_mdl0_mtl_block(data, nested, chunk_end)
                texture_names.extend(nested_names)
            if nested != chunk_end:
                raise MorayError("MDL NUL material container has unconsumed bytes")
        else:
            raise MorayError(f"unsupported MDL NUL material subchunk 0x{tag:02x}")
        q = chunk_end

    if q < limit:
        q += 1
    return q, texture_names


def scan_mdl0_records(data: bytes) -> list[MDL0Record]:
    candidates: list[MDL0Record] = []
    for offset in range(4, len(data) - 32):
        if not (32 <= data[offset] <= 126):
            continue
        if offset > 0 and 32 <= data[offset - 1] <= 126:
            continue
        for layout in ("A", "B"):
            try:
                candidates.append(parse_mdl0_record_at(data, offset, layout))
            except MorayError:
                pass

    candidates.sort(key=lambda record: (record.start, -(record.end - record.start)))
    records: list[MDL0Record] = []
    cursor = 0
    for record in candidates:
        if record.start < cursor:
            continue
        records.append(record)
        cursor = record.end
    return records


def parse_mdl0_record_at(data: bytes, offset: int, layout: str) -> MDL0Record:
    pos = offset
    name, pos = read_mdl0_string(data, pos, "MDL NUL object name")

    if layout == "A":
        material_name, pos = read_mdl0_string(data, pos, "MDL NUL material name")
        if pos + 12 > len(data):
            raise MorayError("truncated MDL NUL layout A object vector")
        object_values = struct.unpack_from("<3f", data, pos)
        pos += 12
    elif layout == "B":
        if pos + 28 > len(data):
            raise MorayError("truncated MDL NUL layout B object header")
        object_word = u32(data, pos)
        pos += 4
        object_values = struct.unpack_from("<5f", data, pos)
        pos += 20
        material_word = u32(data, pos)
        pos += 4
        material_name, pos = read_mdl0_string(data, pos, "MDL NUL material name")
        # These words are object/material metadata. They vary widely in the
        # terrain-grid samples and are not needed for static triangle output.
    else:
        raise MorayError(f"internal error: unknown MDL NUL layout {layout}")

    if not all(math.isfinite(value) and abs(value) < 1.0e8 for value in object_values):
        raise MorayError("MDL NUL object header contains non-finite values")

    vertex_count = u32(data, pos)
    pos += 4
    if not (3 <= vertex_count <= 100000):
        raise MorayError(f"MDL NUL object has unsupported vertex count {vertex_count}")
    vertex_bytes = vertex_count * 32
    if pos + vertex_bytes + 4 > len(data):
        raise MorayError("MDL NUL vertex table overruns EOF")

    vertices: list[tuple[float, float, float]] = []
    normals: list[tuple[float, float, float]] = []
    texcoords: list[tuple[float, float]] = []
    for index in range(vertex_count):
        values = struct.unpack_from("<8f", data, pos + index * 32)
        if not all(math.isfinite(value) and abs(value) < 1.0e10 for value in values):
            raise MorayError("MDL NUL vertex record contains non-finite values")
        vertices.append((values[0], values[1], values[2]))
        normals.append(normal_or_face((values[3], values[4], values[5]), (0.0, 1.0, 0.0)))
        texcoords.append((values[6], values[7]))
    pos += vertex_bytes

    triangle_count = u32(data, pos)
    pos += 4
    if not (1 <= triangle_count <= 100000):
        raise MorayError(f"MDL NUL object has unsupported triangle count {triangle_count}")
    index_bytes = triangle_count * 6
    if pos + index_bytes > len(data):
        raise MorayError("MDL NUL triangle table overruns EOF")

    triangles: list[tuple[int, int, int]] = []
    max_index = 0
    for triangle_index in range(triangle_count):
        tri = struct.unpack_from("<3H", data, pos + triangle_index * 6)
        if any(index >= vertex_count for index in tri):
            raise MorayError("MDL NUL triangle index is outside the vertex table")
        max_index = max(max_index, *tri)
        triangles.append(tri)
    if max_index < min(vertex_count - 1, 2):
        raise MorayError("MDL NUL triangle table does not reference enough vertices")
    pos += index_bytes

    return MDL0Record(
        offset,
        pos,
        layout,
        name,
        material_name,
        vertices,
        normals,
        texcoords,
        triangles,
    )


def read_mdl0_string(data: bytes, offset: int, label: str) -> tuple[str, int]:
    end = data.find(b"\0", offset, min(len(data), offset + 80))
    if end < 0:
        raise MorayError(f"{label} at 0x{offset:x} is not NUL-terminated")
    raw = data[offset:end]
    if not (1 <= len(raw) <= 64):
        raise MorayError(f"{label} at 0x{offset:x} has unsupported length")
    if not all(32 <= value <= 126 for value in raw):
        raise MorayError(f"{label} at 0x{offset:x} contains non-printable bytes")
    if not any((65 <= value <= 90) or (97 <= value <= 122) for value in raw):
        raise MorayError(f"{label} at 0x{offset:x} does not contain letters")
    return raw.decode("latin1"), end + 1


def decode_mdlc(data: bytes) -> tuple[bytes, bytes, bytes]:
    if len(data) < 12:
        raise MorayError("MDLC file is too short to contain its encoded payload")
    if data[:4] != b"MDLC":
        raise MorayError("unsupported signature; expected MDLC")
    version = data[4:6]
    if version not in MDLC_KEY_PHASES:
        raise MorayError(f"unsupported MDLC version bytes {version!r}")

    encoded = data[6:]
    phase = MDLC_KEY_PHASES[version]
    differenced = bytearray()
    previous = 0
    for index, value in enumerate(encoded):
        if index == 0:
            differenced.append(value)
        else:
            differenced.append(value ^ previous)
        previous = value

    decoded = bytes(
        value ^ MDLC_KEY[(index + phase) % len(MDLC_KEY)]
        for index, value in enumerate(differenced)
    )
    if len(decoded) < 8:
        raise MorayError("decoded MDLC payload is too short")
    wrapper_prefix = decoded[:6]
    inner = b"MDLX" + version + decoded[6:]
    if inner[:6] != b"MDLX" + version:
        raise MorayError("internal MDLC decode error")
    return version, wrapper_prefix, inner


def parse_mdlc(data: bytes) -> MorayModel:
    version, wrapper_prefix, inner = decode_mdlc(data)
    if inner[:4] == b"MDLS" or inner[:4] == b"MDL!" or inner[:4] == b"MDL2":
        return parse_model(inner)
    if inner[:4] == b"MDLX":
        return parse_mdlx(inner, source_kind=f"MDLC-wrapped MDLX{version.decode('ascii', 'replace')}")
    signature = inner[:4].decode("latin1", "replace")
    raise MorayError(f"MDLC decoded to unsupported inner signature {signature!r}")


def parse_mdla(data: bytes) -> MorayModel:
    if len(data) < 0x80:
        raise MorayError("MDLA file is shorter than its observed bitmap wrapper")
    if data[:4] != b"MDLA":
        raise MorayError("unsupported signature; expected MDLA")

    name_end = data.find(b"\0", 4, 32)
    if name_end < 0:
        raise MorayError("MDLA wrapper name is not NUL-terminated")
    wrapper_name = data[4:name_end].decode("latin1", "replace")
    if not wrapper_name.upper().endswith(".WMF"):
        raise MorayError(f"MDLA wrapper name {wrapper_name!r} does not end in .WMF")

    bm_offset = data.find(b"BM", name_end + 1)
    if bm_offset != 0x49:
        raise MorayError(f"MDLA bitmap marker is at 0x{bm_offset:x}, expected 0x49")
    compressed_size = u32(data, bm_offset + 2)
    if compressed_size == 0 or bm_offset + 0x36 + compressed_size != len(data):
        raise MorayError("MDLA compressed payload size does not close at EOF")
    if u16(data, bm_offset + 6) != 0:
        raise MorayError("MDLA bitmap reserved word is non-zero")
    bitmap_word_a = u32(data, bm_offset + 8)
    bitmap_word_b = u16(data, bm_offset + 12)

    dib_offset = bm_offset + 14
    (
        dib_header_size,
        width,
        height,
        planes,
        bits_per_pixel,
        compression,
        image_size,
        x_pixels_per_meter,
        y_pixels_per_meter,
        colors_used,
        colors_important,
    ) = struct.unpack_from("<IiiHHIIiiII", data, dib_offset)
    if dib_header_size != 40:
        raise MorayError(f"MDLA DIB header size is {dib_header_size}, expected 40")
    if width <= 0 or height <= 0:
        raise MorayError("MDLA bitmap dimensions must be positive")
    if planes != 1 or compression != 0:
        raise MorayError("MDLA bitmap must be uncompressed BI_RGB with one plane")
    if bits_per_pixel not in (16, 32):
        raise MorayError(f"MDLA bitmap bit depth {bits_per_pixel} is not supported")
    if any((x_pixels_per_meter, y_pixels_per_meter, colors_used, colors_important)):
        raise MorayError("MDLA DIB trailing metadata words are not zero")

    zlib_offset = dib_offset + dib_header_size
    if data[zlib_offset : zlib_offset + 2] != b"\x78\xda":
        raise MorayError("MDLA compressed bitmap payload does not start with zlib 0x78da")
    try:
        pixel_payload = zlib.decompress(data[zlib_offset:])
    except zlib.error as exc:
        raise MorayError("MDLA zlib bitmap payload did not decompress") from exc
    row_stride = align4(width * bits_per_pixel // 8)
    expected_image_size = row_stride * height
    if image_size != expected_image_size:
        raise MorayError(
            f"MDLA DIB image size {image_size} does not match aligned rows {expected_image_size}"
        )
    if len(pixel_payload) == image_size + 4 and bits_per_pixel == 32:
        pixel_payload = pixel_payload[4:]
    if len(pixel_payload) != image_size:
        raise MorayError(
            f"MDLA decompressed bitmap has {len(pixel_payload)} bytes, expected {image_size}"
        )

    rgba = mdla_bitmap_to_rgba(pixel_payload, width, height, bits_per_pixel, row_stride)
    texture_png = make_png_rgba(width, height, rgba)
    aspect = width / height
    half_w = 0.5 * aspect
    half_h = 0.5
    vertices = [
        (-half_w, -half_h, 0.0),
        (half_w, -half_h, 0.0),
        (half_w, half_h, 0.0),
        (-half_w, half_h, 0.0),
    ]
    normal = (0.0, 0.0, 1.0)
    polygons = [
        Polygon(0, normal, [0, 1, 2], [0, 0, 0], [normal, normal, normal], [(0.0, 1.0, 0.0), (1.0, 1.0, 0.0), (1.0, 0.0, 0.0)]),
        Polygon(0, normal, [0, 2, 3], [0, 0, 0], [normal, normal, normal], [(0.0, 1.0, 0.0), (1.0, 0.0, 0.0), (0.0, 0.0, 0.0)]),
    ]
    metadata = (
        len(data),
        bm_offset,
        compressed_size,
        bitmap_word_a,
        bitmap_word_b,
        width,
        height,
        bits_per_pixel,
        image_size,
        len(texture_png),
    )
    return MorayModel(
        "MDLA compressed bitmap plane",
        [wrapper_name],
        metadata,
        0,
        1,
        [ModelBlock(len(vertices), len(polygons), vertices, polygons)],
        texture_pngs={0: texture_png},
    )


def mdla_bitmap_to_rgba(
    payload: bytes, width: int, height: int, bits_per_pixel: int, row_stride: int
) -> bytes:
    out = bytearray()
    for y in range(height):
        src_y = height - 1 - y
        row = src_y * row_stride
        for x in range(width):
            if bits_per_pixel == 16:
                value = struct.unpack_from("<H", payload, row + x * 2)[0]
                r = ((value >> 10) & 0x1F) * 255 // 31
                g = ((value >> 5) & 0x1F) * 255 // 31
                b = (value & 0x1F) * 255 // 31
                a = 255
            else:
                b, g, r, a = payload[row + x * 4 : row + x * 4 + 4]
                if a == 0:
                    a = 255
            out.extend((r, g, b, a))
    return bytes(out)


def png_chunk(tag: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + tag
        + payload
        + struct.pack(">I", binascii.crc32(tag + payload) & 0xFFFFFFFF)
    )


def make_png_rgba(width: int, height: int, rgba: bytes) -> bytes:
    if len(rgba) != width * height * 4:
        raise MorayError("internal MDLA PNG encoder received the wrong pixel count")
    rows = bytearray()
    stride = width * 4
    for y in range(height):
        rows.append(0)
        rows.extend(rgba[y * stride : y * stride + stride])
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", ihdr)
        + png_chunk(b"IDAT", zlib.compress(bytes(rows)))
        + png_chunk(b"IEND", b"")
    )


def decode_pcx_to_png(data: bytes, label: str) -> bytes:
    if len(data) < 128 + 769:
        raise MorayError(f"{label} is too short to be an 8-bit paletted PCX")
    if data[0] != 0x0A:
        raise MorayError(f"{label} has invalid PCX manufacturer byte")
    if data[2] != 1:
        raise MorayError(f"{label} does not use PCX RLE encoding")
    bits_per_pixel = data[3]
    xmin, ymin, xmax, ymax = struct.unpack_from("<4H", data, 4)
    width = xmax - xmin + 1
    height = ymax - ymin + 1
    if width <= 0 or height <= 0:
        raise MorayError(f"{label} has invalid PCX dimensions")
    color_planes = data[65]
    bytes_per_line = u16(data, 66)
    if bits_per_pixel != 8 or color_planes != 1:
        raise MorayError(f"{label} is not an 8-bit single-plane paletted PCX")
    if bytes_per_line < width:
        raise MorayError(f"{label} PCX bytes_per_line is smaller than image width")
    if data[-769] != 0x0C:
        raise MorayError(f"{label} is missing the 256-color PCX palette marker")

    encoded = data[128:-769]
    expected = bytes_per_line * height
    decoded = bytearray()
    pos = 0
    while pos < len(encoded):
        value = encoded[pos]
        pos += 1
        if value >= 0xC0:
            count = value & 0x3F
            if pos >= len(encoded):
                raise MorayError(f"{label} PCX RLE run is missing its value byte")
            decoded.extend([encoded[pos]] * count)
            pos += 1
        else:
            decoded.append(value)
        if len(decoded) > expected:
            raise MorayError(f"{label} PCX RLE stream expands past the expected image size")
    if len(decoded) != expected:
        raise MorayError(
            f"{label} PCX RLE stream expands to {len(decoded)} bytes, expected {expected}"
        )

    palette = data[-768:]
    rgba = bytearray()
    for y in range(height):
        row = decoded[y * bytes_per_line : y * bytes_per_line + width]
        for index in row:
            base = index * 3
            rgba.extend((palette[base], palette[base + 1], palette[base + 2], 255))
    return make_png_rgba(width, height, bytes(rgba))


def build_texture_index(directory: Path) -> dict[str, Path]:
    index: dict[str, Path] = {}
    for path in directory.rglob("*"):
        if not path.is_file() or path.suffix.lower() != ".pcx":
            continue
        rel = path.relative_to(directory).as_posix()
        keys = {
            rel.lower(),
            rel[: -len(path.suffix)].lower(),
            path.name.lower(),
            path.stem.lower(),
        }
        for key in keys:
            index.setdefault(key, path)
    return index


def find_texture_path(texture_index: dict[str, Path], texture_name: str) -> Path | None:
    normalized = texture_name.replace("\\", "/").lower()
    candidates = [normalized]
    if "." not in Path(normalized).name:
        candidates.append(normalized + ".pcx")
    for candidate in candidates:
        if candidate in texture_index:
            return texture_index[candidate]
    return None


def attach_external_textures(model: MorayModel, input_path: Path) -> None:
    if not model.materials:
        return
    texture_index = build_texture_index(input_path.parent)
    if not texture_index:
        return
    decoded_cache: dict[Path, bytes] = {}
    for material_index, material in model.materials.items():
        for texture_name in material.texture_names:
            texture_path = find_texture_path(texture_index, texture_name)
            if texture_path is None:
                continue
            if texture_path not in decoded_cache:
                if texture_path.suffix.lower() != ".pcx":
                    raise MorayError(f"unsupported external texture format {texture_path.suffix!r}")
                decoded_cache[texture_path] = decode_pcx_to_png(
                    texture_path.read_bytes(),
                    str(texture_path),
                )
            model.texture_pngs[material_index] = decoded_cache[texture_path]
            break


@dataclass
class MDLXInfo:
    version: str
    header_size: int
    viewport_count: int
    scene_start: int


def inspect_mdlx(data: bytes) -> MDLXInfo:
    if len(data) < 30:
        raise MorayError("MDLX file is shorter than its fixed header")
    if data[:4] != b"MDLX":
        raise MorayError("unsupported signature; expected MDLX")
    version_bytes = data[4:6]
    if not all(48 <= value <= 57 for value in version_bytes):
        raise MorayError(f"MDLX version bytes are not ASCII digits: {version_bytes!r}")
    version = version_bytes.decode("ascii")

    header_size = 32 if version == "60" else 30
    if len(data) < header_size:
        raise MorayError(f"MDLX{version} file is shorter than its {header_size}-byte header")
    cursor = header_size

    if version in ("22", "24", "29"):
        viewport_count = 3
        record_overhead = 4
        for index in range(viewport_count):
            end = cursor + 48 + record_overhead
            if end > len(data):
                raise MorayError(f"MDLX{version} viewport record {index} overruns EOF")
            cursor = end
    elif version in ("36", "37"):
        viewport_count = 4
        for index in range(viewport_count):
            if cursor + 54 > len(data):
                raise MorayError(f"MDLX{version} viewport record {index} is truncated")
            name_length = data[cursor + 53]
            end = cursor + 48 + 6 + name_length
            if end > len(data):
                raise MorayError(f"MDLX{version} viewport record {index} name overruns EOF")
            cursor = end
    elif version in ("41", "60"):
        viewport_count = 4
        for index in range(viewport_count):
            if cursor + 55 > len(data):
                raise MorayError(f"MDLX{version} viewport record {index} is truncated")
            name_length = data[cursor + 54]
            end = cursor + 48 + 7 + name_length
            if end > len(data):
                raise MorayError(f"MDLX{version} viewport record {index} name overruns EOF")
            cursor = end
    elif version in ("73", "77"):
        viewport_count = 0
    else:
        raise MorayError(f"unsupported MDLX version {version}")

    return MDLXInfo(version, header_size, viewport_count, cursor)


@dataclass
class MDLXPrimitive:
    offset: int
    type_code: int
    name: str
    scale: tuple[float, float, float]
    rotation_degrees: tuple[float, float, float]
    translation: tuple[float, float, float]


MDLX_PRIMITIVE_TYPES = {
    0x02: "cube",
    0x03: "sphere",
    0x04: "cylinder",
    0x11: "cone",
    0x12: "torus",
    0x16: "disc",
}


def parse_mdlx(data: bytes, source_kind: str | None = None) -> MorayModel:
    info = inspect_mdlx(data)
    primitives = scan_mdlx_primitives(data, info)
    if not primitives:
        raise MorayError(
            f"MDLX{info.version} header and {info.viewport_count} viewport record(s) "
            f"validated through offset 0x{info.scene_start:x}, but no supported "
            "primitive scene records were found"
        )

    models: list[ModelBlock] = []
    strings: list[str] = []
    for material, primitive in enumerate(primitives):
        block = primitive_to_model_block(primitive, material)
        models.append(block)
        strings.append(
            f"0x{primitive.offset:x}:{MDLX_PRIMITIVE_TYPES[primitive.type_code]}:{primitive.name}"
        )

    metadata = (
        len(data),
        int(info.version),
        info.header_size,
        info.viewport_count,
        info.scene_start,
        len(primitives),
    )
    return MorayModel(source_kind or f"MDLX{info.version} scene", strings, metadata, 0, len(primitives), models)


def printable_mdlx_name(raw: bytes) -> bool:
    if not (2 <= len(raw) <= 64):
        return False
    if not any((65 <= value <= 90) or (97 <= value <= 122) for value in raw):
        return False
    allowed = set(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 _.-=#")
    return all(value in allowed for value in raw)


def scan_mdlx_primitives(data: bytes, info: MDLXInfo) -> list[MDLXPrimitive]:
    if info.version in ("60", "73", "77"):
        candidates = scan_mdlx_length_names(data, info.scene_start)
        transform_offsets = (0,)
    else:
        candidates = scan_mdlx_nul_names(data, info.scene_start)
        transform_offsets = (10, 8, 7, 6, 12, 0)

    by_offset: dict[int, MDLXPrimitive] = {}
    for name_offset, body_offset, name in candidates:
        type_code = mdlx_type_before_name(data, info.version, name_offset)
        if type_code is None:
            continue
        transform = read_mdlx_transform(data, body_offset, transform_offsets)
        if transform is None:
            continue
        primitive = MDLXPrimitive(name_offset, type_code, name, *transform)
        existing = by_offset.get(name_offset)
        if existing is None or transform_plausibility_score(primitive) < transform_plausibility_score(existing):
            by_offset[name_offset] = primitive

    return sorted(by_offset.values(), key=lambda primitive: primitive.offset)


def scan_mdlx_length_names(data: bytes, scene_start: int) -> list[tuple[int, int, str]]:
    candidates: list[tuple[int, int, str]] = []
    for name_offset in range(scene_start + 1, len(data)):
        length = data[name_offset - 1]
        if length == 0 or length > 64 or name_offset + length > len(data):
            continue
        raw = data[name_offset : name_offset + length]
        if printable_mdlx_name(raw):
            candidates.append((name_offset, name_offset + length, raw.decode("latin1")))
    return candidates


def scan_mdlx_nul_names(data: bytes, scene_start: int) -> list[tuple[int, int, str]]:
    candidates: list[tuple[int, int, str]] = []
    offset = scene_start
    while offset < len(data):
        if 32 <= data[offset] <= 126:
            end = offset
            while end < len(data) and 32 <= data[end] <= 126:
                end += 1
            if end < len(data) and data[end] == 0:
                raw = data[offset:end]
                if printable_mdlx_name(raw):
                    candidates.append((offset, end + 1, raw.decode("latin1")))
                offset = end + 1
                continue
        offset += 1
    return candidates


def mdlx_type_before_name(data: bytes, version: str, name_offset: int) -> int | None:
    if version in ("60", "73", "77"):
        if name_offset < 4:
            return None
        value = data[name_offset - 4]
        return value if value in MDLX_PRIMITIVE_TYPES else None
    if version in ("36", "37", "41"):
        if name_offset < 3:
            return None
        if name_offset >= 2 and u16(data, name_offset - 2) == 0xFFFF:
            return None
        value = data[name_offset - 3]
        return value if value in MDLX_PRIMITIVE_TYPES else None
    if version in ("22", "24", "29"):
        if name_offset >= 3:
            value = data[name_offset - 3]
            if value in MDLX_PRIMITIVE_TYPES:
                return value
        return None

    start = max(0, name_offset - 12)
    prefix = data[start:name_offset]
    matches: list[tuple[int, int]] = []
    for index, value in enumerate(prefix):
        if value not in MDLX_PRIMITIVE_TYPES:
            continue
        absolute = start + index
        distance = name_offset - absolute
        if distance < 3 or distance > 10:
            continue
        if name_offset >= 2 and u16(data, name_offset - 2) == 0xFFFF:
            continue
        matches.append((distance, value))
    if not matches:
        return None
    matches.sort()
    return matches[0][1]


def read_mdlx_transform(
    data: bytes, body_offset: int, transform_offsets: tuple[int, ...]
) -> tuple[
    tuple[float, float, float],
    tuple[float, float, float],
    tuple[float, float, float],
] | None:
    for relative in transform_offsets:
        off = body_offset + relative
        if off + 48 > len(data):
            continue
        scale = struct.unpack_from("<3f", data, off)
        rotation = struct.unpack_from("<3f", data, off + 12)
        translation_d = struct.unpack_from("<3d", data, off + 24)
        translation = (float(translation_d[0]), float(translation_d[1]), float(translation_d[2]))
        if is_plausible_mdlx_transform(scale, rotation, translation):
            return scale, rotation, translation
    return None


def is_plausible_mdlx_transform(
    scale: tuple[float, float, float],
    rotation: tuple[float, float, float],
    translation: tuple[float, float, float],
) -> bool:
    values = (*scale, *rotation, *translation)
    if not all(math.isfinite(value) for value in values):
        return False
    if any(abs(value) > 1.0e6 for value in translation):
        return False
    if any(abs(value) > 36000.0 for value in rotation):
        return False
    if any(abs(value) < 1.0e-7 or abs(value) > 1.0e5 for value in scale):
        return False
    return True


def transform_plausibility_score(primitive: MDLXPrimitive) -> float:
    scale_score = sum(abs(abs(value) - 1.0) for value in primitive.scale)
    rotation_score = sum(abs(value) for value in primitive.rotation_degrees) / 360.0
    translation_score = sum(abs(value) for value in primitive.translation) / 1000.0
    return scale_score + rotation_score + translation_score


def rotate_xyz(
    point: tuple[float, float, float], degrees: tuple[float, float, float]
) -> tuple[float, float, float]:
    x, y, z = point
    rx, ry, rz = (math.radians(value) for value in degrees)
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    y, z = y * cx - z * sx, y * sx + z * cx
    x, z = x * cy + z * sy, -x * sy + z * cy
    x, y = x * cz - y * sz, x * sz + y * cz
    return x, y, z


def transform_point(
    point: tuple[float, float, float],
    primitive: MDLXPrimitive,
) -> tuple[float, float, float]:
    scaled = (
        point[0] * primitive.scale[0],
        point[1] * primitive.scale[1],
        point[2] * primitive.scale[2],
    )
    rotated = rotate_xyz(scaled, primitive.rotation_degrees)
    return (
        rotated[0] + primitive.translation[0],
        rotated[1] + primitive.translation[1],
        rotated[2] + primitive.translation[2],
    )


def primitive_to_model_block(primitive: MDLXPrimitive, material: int) -> ModelBlock:
    vertices, triangles = make_mdlx_unit_mesh(primitive.type_code)
    transformed = [transform_point(vertex, primitive) for vertex in vertices]
    polygons: list[Polygon] = []
    for tri in triangles:
        face = face_normal_from_vertices(transformed[tri[0]], transformed[tri[1]], transformed[tri[2]])
        polygons.append(
            Polygon(
                material,
                face,
                list(tri),
                [0, 0, 0],
                [face, face, face],
                [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)],
            )
        )
    return ModelBlock(len(transformed), len(polygons), transformed, polygons)


def make_mdlx_unit_mesh(type_code: int) -> tuple[list[tuple[float, float, float]], list[tuple[int, int, int]]]:
    if type_code == 0x02:
        return make_box_mesh()
    if type_code == 0x03:
        return make_sphere_mesh(16, 12)
    if type_code == 0x04:
        return make_cylinder_mesh(24)
    if type_code == 0x11:
        return make_cone_mesh(24)
    if type_code == 0x12:
        return make_torus_mesh(24, 12, 0.75, 0.25)
    if type_code == 0x16:
        return make_disc_mesh(24)
    raise MorayError(f"internal error: unsupported MDLX primitive type 0x{type_code:02x}")


def make_box_mesh() -> tuple[list[tuple[float, float, float]], list[tuple[int, int, int]]]:
    vertices = [
        (-0.5, -0.5, -0.5),
        (0.5, -0.5, -0.5),
        (0.5, 0.5, -0.5),
        (-0.5, 0.5, -0.5),
        (-0.5, -0.5, 0.5),
        (0.5, -0.5, 0.5),
        (0.5, 0.5, 0.5),
        (-0.5, 0.5, 0.5),
    ]
    triangles = [
        (0, 2, 1), (0, 3, 2),
        (4, 5, 6), (4, 6, 7),
        (0, 1, 5), (0, 5, 4),
        (1, 2, 6), (1, 6, 5),
        (2, 3, 7), (2, 7, 6),
        (3, 0, 4), (3, 4, 7),
    ]
    return vertices, triangles


def make_sphere_mesh(segments: int, rings: int) -> tuple[list[tuple[float, float, float]], list[tuple[int, int, int]]]:
    vertices: list[tuple[float, float, float]] = [(0.0, 0.0, 0.5)]
    for ring in range(1, rings):
        phi = math.pi * ring / rings
        z = 0.5 * math.cos(phi)
        radius = 0.5 * math.sin(phi)
        for segment in range(segments):
            theta = 2.0 * math.pi * segment / segments
            vertices.append((radius * math.cos(theta), radius * math.sin(theta), z))
    bottom = len(vertices)
    vertices.append((0.0, 0.0, -0.5))
    triangles: list[tuple[int, int, int]] = []
    for segment in range(segments):
        a = 1 + segment
        b = 1 + ((segment + 1) % segments)
        triangles.append((0, a, b))
    for ring in range(rings - 2):
        row = 1 + ring * segments
        next_row = row + segments
        for segment in range(segments):
            a = row + segment
            b = row + ((segment + 1) % segments)
            c = next_row + segment
            d = next_row + ((segment + 1) % segments)
            triangles.append((a, c, b))
            triangles.append((b, c, d))
    last_row = 1 + (rings - 2) * segments
    for segment in range(segments):
        a = last_row + segment
        b = last_row + ((segment + 1) % segments)
        triangles.append((a, bottom, b))
    return vertices, triangles


def make_cylinder_mesh(segments: int) -> tuple[list[tuple[float, float, float]], list[tuple[int, int, int]]]:
    vertices: list[tuple[float, float, float]] = []
    for z in (-0.5, 0.5):
        for segment in range(segments):
            theta = 2.0 * math.pi * segment / segments
            vertices.append((0.5 * math.cos(theta), 0.5 * math.sin(theta), z))
    bottom_center = len(vertices)
    vertices.append((0.0, 0.0, -0.5))
    top_center = len(vertices)
    vertices.append((0.0, 0.0, 0.5))
    triangles: list[tuple[int, int, int]] = []
    for segment in range(segments):
        n = (segment + 1) % segments
        b0, b1 = segment, n
        t0, t1 = segments + segment, segments + n
        triangles.append((b0, t0, b1))
        triangles.append((b1, t0, t1))
        triangles.append((bottom_center, b1, b0))
        triangles.append((top_center, t0, t1))
    return vertices, triangles


def make_cone_mesh(segments: int) -> tuple[list[tuple[float, float, float]], list[tuple[int, int, int]]]:
    vertices: list[tuple[float, float, float]] = []
    for segment in range(segments):
        theta = 2.0 * math.pi * segment / segments
        vertices.append((0.5 * math.cos(theta), 0.5 * math.sin(theta), -0.5))
    apex = len(vertices)
    vertices.append((0.0, 0.0, 0.5))
    center = len(vertices)
    vertices.append((0.0, 0.0, -0.5))
    triangles: list[tuple[int, int, int]] = []
    for segment in range(segments):
        n = (segment + 1) % segments
        triangles.append((segment, apex, n))
        triangles.append((center, n, segment))
    return vertices, triangles


def make_disc_mesh(segments: int) -> tuple[list[tuple[float, float, float]], list[tuple[int, int, int]]]:
    vertices = [(0.0, 0.0, 0.0)]
    for segment in range(segments):
        theta = 2.0 * math.pi * segment / segments
        vertices.append((0.5 * math.cos(theta), 0.5 * math.sin(theta), 0.0))
    triangles = [(0, 1 + segment, 1 + ((segment + 1) % segments)) for segment in range(segments)]
    return vertices, triangles


def make_torus_mesh(
    major_segments: int, minor_segments: int, major_radius: float, minor_radius: float
) -> tuple[list[tuple[float, float, float]], list[tuple[int, int, int]]]:
    vertices: list[tuple[float, float, float]] = []
    for major in range(major_segments):
        theta = 2.0 * math.pi * major / major_segments
        for minor in range(minor_segments):
            phi = 2.0 * math.pi * minor / minor_segments
            radius = major_radius + minor_radius * math.cos(phi)
            vertices.append(
                (
                    radius * math.cos(theta),
                    radius * math.sin(theta),
                    minor_radius * math.sin(phi),
                )
            )
    triangles: list[tuple[int, int, int]] = []
    for major in range(major_segments):
        next_major = (major + 1) % major_segments
        for minor in range(minor_segments):
            next_minor = (minor + 1) % minor_segments
            a = major * minor_segments + minor
            b = next_major * minor_segments + minor
            c = major * minor_segments + next_minor
            d = next_major * minor_segments + next_minor
            triangles.append((a, b, c))
            triangles.append((c, b, d))
    return vertices, triangles


def parse_mdlz(data: bytes) -> MorayModel:
    if len(data) < 0x128:
        raise MorayError("MDLZ file is shorter than its fixed header")
    if data[:4] != b"MDLZ":
        raise MorayError("unsupported signature; expected MDLZ")

    version = u32(data, 4)
    if version != 14:
        raise MorayError(f"unsupported MDLZ version {version}")
    model_name = fixed_c_string(data, 8, 64, "MDLZ model name")
    declared_length = u32(data, 0x48)
    if declared_length != len(data):
        raise MorayError(
            f"MDLZ length mismatch: header says {declared_length}, file has {len(data)}"
        )

    classic_words = struct.unpack_from("<28I", data, 0x88)
    (
        flags,
        bone_count,
        bone_offset,
        bone_controller_count,
        bone_controller_offset,
        hitbox_count,
        hitbox_offset,
        sequence_count,
        sequence_offset,
        sequence_group_count,
        sequence_group_offset,
        texture_count,
        texture_offset,
        texture_data_offset,
        skin_ref_count,
        skin_family_count,
        skin_offset,
        bodypart_count,
        bodypart_offset,
        attachment_count,
        attachment_offset,
        sound_table,
        sound_offset,
        sound_group_count,
        sound_group_offset,
        transition_count,
        transition_offset,
        classic_reserved,
    ) = classic_words
    if bone_count != 1 or bone_offset != 0x1E4:
        raise MorayError("MDLZ sample has unsupported bone table layout")
    if hitbox_count != 1 or hitbox_offset != 0x260:
        raise MorayError("MDLZ sample has unsupported hitbox table layout")
    if sequence_count != 1 or sequence_offset != 0x2A0:
        raise MorayError("MDLZ sample has unsupported sequence table layout")
    if sequence_group_count != 1 or sequence_group_offset != 0x360:
        raise MorayError("MDLZ sample has unsupported sequence-group table layout")
    if texture_count != 1 or texture_offset != 0x420:
        raise MorayError("MDLZ sample has unsupported texture metadata layout")
    if skin_ref_count != 1 or skin_family_count != 1 or skin_offset != 0x4B0:
        raise MorayError("MDLZ sample has unsupported skin table layout")
    if bodypart_count != 1 or bodypart_offset != 0x3D0:
        raise MorayError("MDLZ sample has unsupported bodypart table layout")
    if attachment_count != 0 or bone_controller_count != 0:
        raise MorayError("MDLZ sample has unsupported controller/attachment tables")
    if classic_reserved != 0:
        raise MorayError("MDLZ classic header reserved word is non-zero")

    extension_count = u32(data, 0xF8)
    if extension_count != 1:
        raise MorayError("MDLZ sample has unsupported extension count")

    vertex_count = u32(data, 0xFC)
    index_count = u32(data, 0x100)
    index_offset = u32(data, 0x104)
    position_offset = u32(data, 0x108)
    normal_offset = u32(data, 0x10C)
    texcoord_offset = u32(data, 0x110)
    reserved_offset = u32(data, 0x114)
    transform_offset = u32(data, 0x118)
    color_offset = u32(data, 0x11C)
    matrix_offset = u32(data, 0x120)
    model_record_offset = u32(data, 0x124)

    if vertex_count == 0 or index_count == 0 or index_count % 3:
        raise MorayError("MDLZ geometry counts are not a non-empty triangle list")
    expected_offsets = {
        "position": position_offset,
        "color": color_offset,
        "transform": transform_offset,
        "normal": normal_offset,
        "texcoord": texcoord_offset,
        "index": index_offset,
        "matrix": matrix_offset,
        "model_record": model_record_offset,
    }
    for label, offset in expected_offsets.items():
        if offset >= len(data):
            raise MorayError(f"MDLZ {label} offset 0x{offset:x} is outside the file")
    if reserved_offset != 0:
        raise MorayError("MDLZ reserved extension offset is non-zero")

    expected_ranges = [
        (position_offset, vertex_count * 16, "position table"),
        (color_offset, vertex_count * 4, "color/attribute table"),
        (transform_offset, vertex_count * 16, "transform/weight table"),
        (normal_offset, vertex_count * 16, "normal table"),
        (texcoord_offset, vertex_count * 8, "texture-coordinate table"),
        (index_offset, index_count * 2, "index table"),
        (matrix_offset, 48, "matrix table"),
    ]
    for offset, size, label in expected_ranges:
        if offset + size > len(data):
            raise MorayError(f"MDLZ {label} overruns EOF")
    sorted_ranges = sorted((offset, offset + size, label) for offset, size, label in expected_ranges)
    for (_, end, label), (next_start, _, next_label) in zip(sorted_ranges, sorted_ranges[1:]):
        if end > next_start:
            raise MorayError(f"MDLZ {label} overlaps {next_label}")

    positions4 = [
        struct.unpack_from("<4f", data, position_offset + i * 16) for i in range(vertex_count)
    ]
    if any(abs(position[3] - 1.0) > 1e-6 for position in positions4):
        raise MorayError("MDLZ position table contains non-1 homogeneous coordinates")
    vertices = [(position[0], position[1], position[2]) for position in positions4]

    colors = [u32(data, color_offset + i * 4) for i in range(vertex_count)]
    if any(color != 0xFFFFFF00 for color in colors):
        raise MorayError("MDLZ color/attribute table contains unsupported values")

    transforms = [
        struct.unpack_from("<4f", data, transform_offset + i * 16) for i in range(vertex_count)
    ]
    if any(not all(math.isfinite(value) for value in transform) for transform in transforms):
        raise MorayError("MDLZ transform/weight table contains non-finite values")

    normals4 = [
        struct.unpack_from("<4f", data, normal_offset + i * 16) for i in range(vertex_count)
    ]
    if any(abs(normal[3] - 1.0) > 1e-6 for normal in normals4):
        raise MorayError("MDLZ normal table contains non-1 homogeneous coordinates")
    normals = [normal_or_face((normal[0], normal[1], normal[2]), (0.0, 1.0, 0.0)) for normal in normals4]

    texcoords = [f32x2(data, texcoord_offset + i * 8) for i in range(vertex_count)]
    indices = [struct.unpack_from("<H", data, index_offset + i * 2)[0] for i in range(index_count)]
    for index_offset_in_table, index in enumerate(indices):
        if index >= vertex_count:
            raise MorayError(
                f"MDLZ index {index_offset_in_table} references vertex {index}, "
                f"but the table has {vertex_count}"
            )

    matrix = struct.unpack_from("<12f", data, matrix_offset)
    if not all(math.isfinite(value) for value in matrix):
        raise MorayError("MDLZ matrix table contains non-finite values")

    model_record_name = fixed_c_string(data, model_record_offset, 32, "MDLZ model record name")
    if model_record_name != model_name.rsplit(".", 1)[0]:
        raise MorayError("MDLZ model record name does not match file model name")
    if any(data[0x128:bone_offset]):
        raise MorayError("MDLZ header-to-bone padding contains non-zero bytes")

    polygons: list[Polygon] = []
    for triangle_index in range(index_count // 3):
        tri = indices[triangle_index * 3 : triangle_index * 3 + 3]
        face_normal = face_normal_from_vertices(vertices[tri[0]], vertices[tri[1]], vertices[tri[2]])
        polygons.append(
            Polygon(
                0,
                face_normal,
                tri,
                [0, 0, 0],
                [normals[tri[0]], normals[tri[1]], normals[tri[2]]],
                [
                    (texcoords[tri[0]][0], texcoords[tri[0]][1], 0.0),
                    (texcoords[tri[1]][0], texcoords[tri[1]][1], 0.0),
                    (texcoords[tri[2]][0], texcoords[tri[2]][1], 0.0),
                ],
            )
        )

    metadata = (
        len(data),
        version,
        flags,
        vertex_count,
        index_count,
        bone_count,
        hitbox_count,
        sequence_count,
        texture_count,
        bodypart_count,
        attachment_offset,
        sound_table,
        sound_offset,
        sound_group_count,
        sound_group_offset,
        transition_count,
        transition_offset,
    )
    return MorayModel(
        "MDLZ",
        [model_name, model_record_name],
        metadata,
        0,
        texture_count,
        [ModelBlock(vertex_count, index_count // 3, vertices, polygons)],
        0,
    )


def parse_utf16le_fixed(data: bytes, off: int, size: int, label: str) -> str:
    if off + size > len(data):
        raise MorayError(f"truncated {label} at 0x{off:x}")
    raw = data[off : off + size]
    if size % 2:
        raise MorayError(f"{label} byte size is not UTF-16 aligned")
    units = struct.unpack_from(f"<{size // 2}H", raw)
    if 0 in units:
        end = units.index(0)
        if any(value != 0 for value in units[end:]):
            raise MorayError(f"{label} has non-zero UTF-16 padding")
        units = units[:end]
    try:
        return struct.pack(f"<{len(units)}H", *units).decode("utf-16le")
    except UnicodeDecodeError as exc:
        raise MorayError(f"{label} is not valid UTF-16LE") from exc


def parse_mdl2(data: bytes) -> MorayModel:
    if len(data) < 0xC8:
        raise MorayError("MDL2 file is shorter than its fixed header and first block header")
    if data[:4] != b"MDL2":
        raise MorayError("unsupported signature; expected MDL2")

    global_bounds = struct.unpack_from("<6f", data, 4)
    mdl2_kind = u32(data, 0x1C)
    if mdl2_kind not in (1, 2, 8):
        raise MorayError(f"MDL2 kind {mdl2_kind} is not supported")

    current_name = parse_utf16le_fixed(data, 0x20, 128, "MDL2 first block name")
    cursor = 0xA0
    block_names: list[str] = []
    models: list[ModelBlock] = []

    while cursor < len(data):
        block_start = cursor
        if cursor + 40 > len(data):
            raise MorayError(f"truncated MDL2 block header at 0x{cursor:x}")
        bounds = struct.unpack_from("<6f", data, cursor)
        vertex_count, index_count, block_word_a, block_word_b = struct.unpack_from(
            "<4I", data, cursor + 24
        )
        if vertex_count == 0:
            raise MorayError(f"MDL2 block at 0x{block_start:x} has zero vertices")
        if index_count == 0:
            raise MorayError(f"MDL2 block at 0x{block_start:x} has zero indices")
        if index_count % 3:
            raise MorayError(
                f"MDL2 block at 0x{block_start:x} has index count {index_count}, "
                "which is not a triangle list"
            )
        if block_word_a not in (1, 2) or block_word_b != 1:
            raise MorayError(
                f"MDL2 block at 0x{block_start:x} has unsupported block words "
                f"{block_word_a}, {block_word_b}"
            )

        cursor += 40
        vertex_bytes = vertex_count * 12
        normal_bytes = vertex_count * 12
        texcoord_bytes = vertex_count * 8
        attr_bytes = vertex_count * 4
        index_bytes = index_count * 4
        mesh_payload_end = cursor + vertex_bytes + normal_bytes + texcoord_bytes + attr_bytes + index_bytes
        if mesh_payload_end > len(data):
            raise MorayError(f"MDL2 block at 0x{block_start:x} overruns EOF")

        vertices = [f32x3(data, cursor + i * 12) for i in range(vertex_count)]
        cursor += vertex_bytes
        normals = [normal_or_face(f32x3(data, cursor + i * 12), (0.0, 1.0, 0.0)) for i in range(vertex_count)]
        cursor += normal_bytes
        texcoords = [f32x2(data, cursor + i * 8) for i in range(vertex_count)]
        cursor += texcoord_bytes

        vertex_words = [u32(data, cursor + i * 4) for i in range(vertex_count)]
        expected_vertex_word = 0 if block_word_a == 2 else 0xFFFFFFFF
        if any(word != expected_vertex_word for word in vertex_words):
            raise MorayError(
                f"MDL2 block at 0x{block_start:x} has unsupported per-vertex attribute words"
            )
        cursor += attr_bytes

        indices = [u32(data, cursor + i * 4) for i in range(index_count)]
        cursor += index_bytes
        if cursor != mesh_payload_end:
            raise MorayError(f"internal MDL2 block size mismatch at 0x{block_start:x}")
        for index_offset, index in enumerate(indices):
            if index >= vertex_count:
                raise MorayError(
                    f"MDL2 block at 0x{block_start:x} index {index_offset} references "
                    f"vertex {index}, but the table has {vertex_count}"
                )

        mins = [min(vertex[axis] for vertex in vertices) for axis in range(3)]
        maxs = [max(vertex[axis] for vertex in vertices) for axis in range(3)]
        for axis in range(3):
            if abs(mins[axis] - bounds[axis]) > 1e-4:
                raise MorayError(f"MDL2 block at 0x{block_start:x} minimum bounds mismatch")
            if abs(maxs[axis] - bounds[axis + 3]) > 1e-4:
                raise MorayError(f"MDL2 block at 0x{block_start:x} maximum bounds mismatch")

        material_index = len(models)
        polygons: list[Polygon] = []
        for triangle_index in range(index_count // 3):
            tri = indices[triangle_index * 3 : triangle_index * 3 + 3]
            face_normal = face_normal_from_vertices(vertices[tri[0]], vertices[tri[1]], vertices[tri[2]])
            polygons.append(
                Polygon(
                    material_index,
                    face_normal,
                    tri,
                    [0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF],
                    [normals[tri[0]], normals[tri[1]], normals[tri[2]]],
                    [
                        (texcoords[tri[0]][0], texcoords[tri[0]][1], 0.0),
                        (texcoords[tri[1]][0], texcoords[tri[1]][1], 0.0),
                        (texcoords[tri[2]][0], texcoords[tri[2]][1], 0.0),
                    ],
                )
            )

        block_names.append(current_name)
        models.append(ModelBlock(vertex_count, index_count // 3, vertices, polygons))

        if block_word_a == 2:
            side_table_bytes = vertex_count * 8
            if cursor + side_table_bytes > len(data):
                raise MorayError(f"MDL2 block at 0x{block_start:x} side tables overrun EOF")
            side_table_a = [u32(data, cursor + i * 4) for i in range(vertex_count)]
            cursor += vertex_count * 4
            side_table_b = [u32(data, cursor + i * 4) for i in range(vertex_count)]
            cursor += vertex_count * 4
            if any(word != 0xFFFFFFFF for word in side_table_a):
                raise MorayError(f"MDL2 block at 0x{block_start:x} first side table is not all 0xffffffff")
            if side_table_b != list(range(vertex_count)):
                raise MorayError(f"MDL2 block at 0x{block_start:x} second side table is not sequential")

        if cursor == len(data):
            break
        current_name = parse_utf16le_fixed(data, cursor, 128, "MDL2 following block name")
        cursor += 128

    if cursor != len(data):
        raise MorayError(f"MDL2 parser stopped at 0x{cursor:x}, file ends at 0x{len(data):x}")
    if not models:
        raise MorayError("MDL2 file has no mesh blocks")

    metadata = (
        len(data),
        mdl2_kind,
        len(models),
        sum(block.vertex_count for block in models),
        sum(block.polygon_count for block in models),
    )
    metadata += tuple(int(math.isfinite(value)) for value in global_bounds)
    return MorayModel("MDL2", block_names, metadata, 0, len(models), models, 0)


def parse_mdl_bang_v1(data: bytes) -> MorayModel:
    if len(data) < 0x102:
        raise MorayError("MDL! v1 file is shorter than the fixed header and bounds block")
    vertex_count, triangle_count = struct.unpack_from("<HH", data, 4)
    material_name_count = data[10]
    header_words = struct.unpack_from("<25H", data, 4)
    cursor = 0x36
    bounds_vertices = [f32x3(data, cursor + i * 12) for i in range(16)]
    cursor += 16 * 12
    radius = struct.unpack_from("<f", data, cursor)[0]
    object_count_hint = u32(data, cursor + 4)
    triangle_count_hint = u32(data, cursor + 8)
    cursor += 12

    material_names: list[str] = []
    for _ in range(material_name_count):
        if cursor >= len(data):
            raise MorayError("truncated MDL! v1 material name length")
        length = data[cursor]
        cursor += 1
        if cursor + length > len(data):
            raise MorayError("truncated MDL! v1 material name")
        material_names.append(data[cursor : cursor + length].decode("latin1", "replace"))
        cursor += length

    render_vertex_bytes = vertex_count * 32
    if cursor + render_vertex_bytes > len(data):
        raise MorayError("MDL! v1 render vertex table overruns EOF")
    vertices: list[tuple[float, float, float]] = []
    normals: list[tuple[float, float, float]] = []
    texcoords: list[tuple[float, float]] = []
    for i in range(vertex_count):
        off = cursor + i * 32
        vertices.append(f32x3(data, off))
        normals.append(normal_or_face(f32x3(data, off + 12), (0.0, 1.0, 0.0)))
        texcoords.append(struct.unpack_from("<2f", data, off + 24))
    cursor += render_vertex_bytes

    face_bytes = triangle_count * 10
    if cursor + face_bytes > len(data):
        raise MorayError("MDL! v1 triangle table overruns EOF")
    raw_faces: list[tuple[int, int, int, int, int]] = []
    for triangle_index in range(triangle_count):
        vals = struct.unpack_from("<5H", data, cursor + triangle_index * 10)
        if vals[4] != 0:
            raise MorayError(f"MDL! v1 triangle {triangle_index} has non-zero reserved field")
        raw_faces.append(vals)
    cursor += face_bytes

    group_count = header_words[2]
    group_bytes = group_count * 15
    if cursor + group_bytes > len(data):
        raise MorayError("MDL! v1 group table overruns EOF")
    face_seen = [False] * triangle_count
    polygons: list[Polygon] = []
    group_tail_words: list[tuple[int, bytes]] = []
    for group_index in range(group_count):
        rec_off = cursor + group_index * 15
        material = data[rec_off] - 1
        object_index = data[rec_off + 1]
        face_start, face_count, vertex_start, vertex_span = struct.unpack_from(
            "<HHHH", data, rec_off + 2
        )
        group_tail_words.append((group_index, data[rec_off + 10 : rec_off + 15]))
        if face_start + face_count > triangle_count:
            raise MorayError(f"MDL! v1 group {group_index} triangle range overruns table")
        if vertex_start + vertex_span > vertex_count:
            raise MorayError(f"MDL! v1 group {group_index} vertex range overruns table")
        for face_index in range(face_start, face_start + face_count):
            face_seen[face_index] = True
            vals = raw_faces[face_index]
            local_indices = [vals[0], vals[1], vals[2]]
            for local_index in local_indices:
                if local_index >= vertex_span:
                    raise MorayError(
                        f"MDL! v1 triangle {face_index} references local vertex {local_index}, "
                        f"but group {group_index} spans {vertex_span}"
                    )
            indices = [vertex_start + local_index for local_index in local_indices]
            material_flag = vals[3] >> 8
            if vals[3] & 0x00FF:
                raise MorayError(
                    f"MDL! v1 triangle {face_index} has non-zero local material byte"
                )
            face_normal = face_normal_from_vertices(
                vertices[indices[0]], vertices[indices[1]], vertices[indices[2]]
            )
            polygons.append(
                Polygon(
                    material,
                    face_normal,
                    indices,
                    [object_index, object_index, object_index],
                    [normals[indices[0]], normals[indices[1]], normals[indices[2]]],
                    [(texcoords[indices[0]][0], texcoords[indices[0]][1], 0.0),
                     (texcoords[indices[1]][0], texcoords[indices[1]][1], 0.0),
                     (texcoords[indices[2]][0], texcoords[indices[2]][1], 0.0)],
                )
            )
    if not all(face_seen):
        raise MorayError("MDL! v1 group table does not cover every triangle")
    cursor += group_bytes

    trailer = data[cursor:]
    # The trailer is scene/object metadata. It is not needed for polygon output,
    # but it is deliberately retained in the parse result for byte accounting.
    object_count_hint = header_words[5]
    triangle_count_hint = u32(data, 0xFE)
    metadata = (
        len(data),
        vertex_count,
        triangle_count,
        material_name_count,
        group_count,
        object_count_hint,
        triangle_count_hint,
        len(trailer),
        sum(1 for _, tail in group_tail_words if any(tail)),
    )
    metadata += tuple(int(abs(v) < 1e39) for triplet in bounds_vertices for v in triplet)
    metadata += (0 if not math.isfinite(radius) else 1,)
    return MorayModel(
        "MDL! v1",
        material_names,
        metadata + header_words,
        0,
        material_name_count,
        [ModelBlock(vertex_count, triangle_count, vertices, polygons)],
        len(trailer),
    )


def parse_mdl_bang_v2(data: bytes) -> MorayModel:
    if len(data) < 120:
        raise MorayError("MDL! v2 file is shorter than its fixed header and bounds block")
    texture_path_flag = u32(data, 8)
    texture_path = data[12:76].split(b"\0", 1)[0].decode("latin1", "replace")
    vertex_count, texcoord_count, triangle_count, normal_count, tag_count = struct.unpack_from(
        "<5I", data, 76
    )
    cursor = 96
    bounds_min = f32x3(data, cursor)
    bounds_max = f32x3(data, cursor + 12)
    cursor += 24

    vertex_bytes = vertex_count * 12
    if cursor + vertex_bytes > len(data):
        raise MorayError("MDL! v2 vertex table overruns EOF")
    vertices = [f32x3(data, cursor + i * 12) for i in range(vertex_count)]
    cursor += vertex_bytes

    texcoord_bytes = texcoord_count * 8
    if cursor + texcoord_bytes > len(data):
        raise MorayError("MDL! v2 texture-coordinate table overruns EOF")
    texcoords = [struct.unpack_from("<2f", data, cursor + i * 8) for i in range(texcoord_count)]
    cursor += texcoord_bytes

    face_bytes = triangle_count * 12
    if cursor + face_bytes > len(data):
        raise MorayError("MDL! v2 triangle table overruns EOF")
    polygons: list[Polygon] = []
    for triangle_index in range(triangle_count):
        vals = struct.unpack_from("<6H", data, cursor + triangle_index * 12)
        indices = [vals[0], vals[1], vals[2]]
        uv_indices = [vals[3], vals[4], vals[5]]
        for index in indices:
            if index >= vertex_count:
                raise MorayError(
                    f"MDL! v2 triangle {triangle_index} references vertex {index}, "
                    f"but the table has {vertex_count}"
                )
        for index in uv_indices:
            if index >= texcoord_count:
                raise MorayError(
                    f"MDL! v2 triangle {triangle_index} references texcoord {index}, "
                    f"but the table has {texcoord_count}"
                )
        face_normal = face_normal_from_vertices(
            vertices[indices[0]], vertices[indices[1]], vertices[indices[2]]
        )
        polygons.append(
            Polygon(
                0,
                face_normal,
                indices,
                [0, 0, 0],
                [face_normal, face_normal, face_normal],
                [(texcoords[uv_indices[0]][0], texcoords[uv_indices[0]][1], 0.0),
                 (texcoords[uv_indices[1]][0], texcoords[uv_indices[1]][1], 0.0),
                 (texcoords[uv_indices[2]][0], texcoords[uv_indices[2]][1], 0.0)],
            )
        )
    cursor += face_bytes

    normal_bytes = normal_count * 12
    if cursor + normal_bytes > len(data):
        raise MorayError("MDL! v2 normal table overruns EOF")
    normals = [f32x3(data, cursor + i * 12) for i in range(normal_count)]
    cursor += normal_bytes

    tag_bytes = tag_count * 56
    if cursor + tag_bytes != len(data):
        raise MorayError(
            f"MDL! v2 tag table size mismatch: expected EOF at 0x{cursor + tag_bytes:x}, "
            f"file ends at 0x{len(data):x}"
        )
    tags: list[str] = []
    for i in range(tag_count):
        off = cursor + i * 56
        tags.append(data[off : off + 32].split(b"\0", 1)[0].decode("latin1", "replace"))

    metadata = (
        len(data),
        texture_path_flag,
        vertex_count,
        texcoord_count,
        triangle_count,
        normal_count,
        tag_count,
    )
    metadata += tuple(int(abs(v) < 1e39) for v in (*bounds_min, *bounds_max))
    return MorayModel(
        "MDL! v2",
        [texture_path] + tags,
        metadata,
        0,
        1,
        [ModelBlock(vertex_count, triangle_count, vertices, polygons)],
        0,
    )


def parse_mod0(content: bytes, absolute_off: int) -> ModelBlock:
    if len(content) < 16:
        raise MorayError(f"MOD0 at 0x{absolute_off:x} is too short")
    vertex_count = u32(content, 0)
    polygon_count = u32(content, 4)
    if vertex_count == 0:
        raise MorayError(f"MOD0 at 0x{absolute_off:x} has zero vertices")

    if content[8:12] != b"VTXS":
        raise MorayError(f"MOD0 at 0x{absolute_off:x} does not start with VTXS")
    vtx_size = u32(content, 12)
    if vtx_size != vertex_count * 12:
        raise MorayError(
            f"VTXS size mismatch in MOD0 at 0x{absolute_off:x}: "
            f"{vtx_size} != {vertex_count} * 12"
        )
    vtx_off = 16
    vtx_end = vtx_off + vtx_size
    if vtx_end > len(content):
        raise MorayError(f"VTXS in MOD0 at 0x{absolute_off:x} overruns MOD0")

    vertices = [f32x3(content, vtx_off + i * 12) for i in range(vertex_count)]
    polygons: list[Polygon] = []
    pos = vtx_end

    for poly_index in range(polygon_count):
        if pos + 8 > len(content):
            raise MorayError(
                f"truncated POLY header {poly_index} in MOD0 at 0x{absolute_off:x}"
            )
        if content[pos : pos + 4] != b"POLY":
            raise MorayError(
                f"expected POLY {poly_index} in MOD0 at absolute 0x{absolute_off + pos:x}"
            )
        poly_size = u32(content, pos + 4)
        poly_content = pos + 8
        poly_end = poly_content + poly_size
        if poly_end > len(content):
            raise MorayError(
                f"POLY {poly_index} in MOD0 at absolute 0x{absolute_off + pos:x} overruns MOD0"
            )

        vertex_per_poly = u32(content, poly_content)
        material = u32(content, poly_content + 4)
        if vertex_per_poly not in (3, 4):
            raise MorayError(
                f"POLY {poly_index} has {vertex_per_poly} vertices; only triangles/quads are supported"
            )
        expected_size = 8 + 12 + vertex_per_poly * 28
        if poly_size != expected_size:
            raise MorayError(
                f"POLY {poly_index} size mismatch: {poly_size} != {expected_size}"
            )

        face_normal = f32x3(content, poly_content + 8)
        cursor = poly_content + 20
        indices: list[int] = []
        index_flags: list[int] = []
        normals: list[tuple[float, float, float]] = []
        texcoords3: list[tuple[float, float, float]] = []
        for _ in range(vertex_per_poly):
            vertex_ref = u32(content, cursor)
            index = vertex_ref & 0xffff
            flags = vertex_ref >> 16
            if index >= vertex_count:
                raise MorayError(
                    f"POLY {poly_index} references vertex {index}, but MOD0 has {vertex_count}"
                )
            indices.append(index)
            index_flags.append(flags)
            normals.append(f32x3(content, cursor + 4))
            texcoords3.append(f32x3(content, cursor + 16))
            cursor += 28

        polygons.append(Polygon(material, face_normal, indices, index_flags, normals, texcoords3))
        pos = poly_end

    if pos != len(content):
        raise MorayError(
            f"MOD0 at 0x{absolute_off:x} has {len(content) - pos} trailing bytes after POLY table"
        )
    return ModelBlock(vertex_count, polygon_count, vertices, polygons)


def normal_or_face(
    normal: tuple[float, float, float], face: tuple[float, float, float]
) -> tuple[float, float, float]:
    length = math.sqrt(normal[0] ** 2 + normal[1] ** 2 + normal[2] ** 2)
    if length > 1e-8:
        return (normal[0] / length, normal[1] / length, normal[2] / length)
    length = math.sqrt(face[0] ** 2 + face[1] ** 2 + face[2] ** 2)
    if length > 1e-8:
        return (face[0] / length, face[1] / length, face[2] / length)
    return (0.0, 1.0, 0.0)


def append_aligned(blob: bytearray, payload: bytes) -> tuple[int, int]:
    offset = len(blob)
    blob.extend(payload)
    while len(blob) % 4:
        blob.append(0)
    return offset, len(payload)


def pack_vec3(values: list[tuple[float, float, float]]) -> bytes:
    return b"".join(struct.pack("<3f", *value) for value in values)


def pack_vec2(values: list[tuple[float, float]]) -> bytes:
    return b"".join(struct.pack("<2f", *value) for value in values)


def material_color(index: int) -> list[float]:
    palette = [
        (0.72, 0.74, 0.78),
        (0.78, 0.55, 0.38),
        (0.42, 0.64, 0.88),
        (0.62, 0.76, 0.45),
        (0.82, 0.62, 0.80),
        (0.86, 0.78, 0.42),
        (0.48, 0.76, 0.72),
        (0.82, 0.48, 0.46),
    ]
    r, g, b = palette[index % len(palette)]
    return [r, g, b, 1.0]


def model_to_glb(model: MorayModel) -> bytes:
    groups: dict[
        int,
        tuple[
            list[tuple[float, float, float]],
            list[tuple[float, float, float]],
            list[tuple[float, float]],
        ],
    ] = {}
    for block in model.models:
        for poly in block.polygons:
            corners = [0, 1, 2] if len(poly.indices) == 3 else [0, 1, 2, 0, 2, 3]
            positions, normals, texcoords = groups.setdefault(poly.material, ([], [], []))
            for corner in corners:
                positions.append(block.vertices[poly.indices[corner]])
                normals.append(normal_or_face(poly.normals[corner], poly.face_normal))
                texcoords.append((poly.texcoords3[corner][0], poly.texcoords3[corner][1]))

    if not groups:
        raise MorayError("no polygons were available for GLB output")

    binary = bytearray()
    buffer_views: list[dict] = []
    accessors: list[dict] = []
    primitives: list[dict] = []
    materials: list[dict] = []
    images: list[dict] = []
    textures: list[dict] = []
    samplers: list[dict] = []
    texture_materials: dict[int, int] = {}

    if model.texture_pngs:
        samplers.append({"magFilter": 9729, "minFilter": 9729, "wrapS": 33071, "wrapT": 33071})
        texture_cache: dict[bytes, int] = {}
        for material_index, png_payload in sorted(model.texture_pngs.items()):
            if png_payload in texture_cache:
                texture_materials[material_index] = texture_cache[png_payload]
                continue
            image_offset, image_length = append_aligned(binary, png_payload)
            image_view = len(buffer_views)
            buffer_views.append(
                {"buffer": 0, "byteOffset": image_offset, "byteLength": image_length}
            )
            image_index = len(images)
            images.append({"bufferView": image_view, "mimeType": "image/png"})
            texture_index = len(textures)
            textures.append({"sampler": 0, "source": image_index})
            texture_cache[png_payload] = texture_index
            texture_materials[material_index] = texture_index

    for material_index in sorted(groups):
        source_material = model.materials.get(material_index)
        has_texture = material_index in texture_materials
        if source_material and not has_texture:
            color = list(source_material.base_color)
        elif has_texture:
            color = [1.0, 1.0, 1.0, 1.0]
        else:
            color = material_color(material_index)
        pbr: dict[str, object] = {
            "baseColorFactor": color,
            "metallicFactor": 0.0,
            "roughnessFactor": 0.75,
        }
        if has_texture:
            pbr["baseColorTexture"] = {"index": texture_materials[material_index]}
        material_name = source_material.name if source_material else f"material_{material_index}"
        material: dict[str, object] = {
            "name": material_name,
            "pbrMetallicRoughness": pbr,
            "doubleSided": True,
        }
        if source_material:
            material["extras"] = {
                "sourceMaterialIndex": material_index,
                "mode": source_material.mode,
                "layout": source_material.layout,
                "baseColorFactorFromMATS": list(source_material.base_color),
                "textureNames": source_material.texture_names,
                "uvValues": list(source_material.uv_values),
            }
        materials.append(material)

    material_to_gltf = {m: i for i, m in enumerate(sorted(groups))}

    for material_index in sorted(groups):
        positions, normals, texcoords = groups[material_index]
        if len(positions) % 3:
            raise MorayError("internal error: triangle stream is not divisible by 3")
        pos_payload = pack_vec3(positions)
        pos_offset, pos_length = append_aligned(binary, pos_payload)
        pos_view = len(buffer_views)
        buffer_views.append({"buffer": 0, "byteOffset": pos_offset, "byteLength": pos_length})
        xs = [p[0] for p in positions]
        ys = [p[1] for p in positions]
        zs = [p[2] for p in positions]
        pos_accessor = len(accessors)
        accessors.append(
            {
                "bufferView": pos_view,
                "componentType": 5126,
                "count": len(positions),
                "type": "VEC3",
                "min": [min(xs), min(ys), min(zs)],
                "max": [max(xs), max(ys), max(zs)],
            }
        )

        normal_payload = pack_vec3(normals)
        normal_offset, normal_length = append_aligned(binary, normal_payload)
        normal_view = len(buffer_views)
        buffer_views.append(
            {"buffer": 0, "byteOffset": normal_offset, "byteLength": normal_length}
        )
        normal_accessor = len(accessors)
        accessors.append(
            {
                "bufferView": normal_view,
                "componentType": 5126,
                "count": len(normals),
                "type": "VEC3",
            }
        )

        texcoord_payload = pack_vec2(texcoords)
        texcoord_offset, texcoord_length = append_aligned(binary, texcoord_payload)
        texcoord_view = len(buffer_views)
        buffer_views.append(
            {"buffer": 0, "byteOffset": texcoord_offset, "byteLength": texcoord_length}
        )
        texcoord_accessor = len(accessors)
        accessors.append(
            {
                "bufferView": texcoord_view,
                "componentType": 5126,
                "count": len(texcoords),
                "type": "VEC2",
            }
        )

        primitives.append(
            {
                "attributes": {
                    "POSITION": pos_accessor,
                    "NORMAL": normal_accessor,
                    "TEXCOORD_0": texcoord_accessor,
                },
                "mode": 4,
                "material": material_to_gltf[material_index],
            }
        )

    gltf = {
        "asset": {"version": "2.0", "generator": "moRay.py"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0}],
        "meshes": [{"name": f"moRay_{model.source_kind}_mesh", "primitives": primitives}],
        "materials": materials,
        "buffers": [{"byteLength": len(binary)}],
        "bufferViews": buffer_views,
        "accessors": accessors,
    }
    if images:
        gltf["images"] = images
        gltf["textures"] = textures
        gltf["samplers"] = samplers
    json_payload = json.dumps(gltf, separators=(",", ":")).encode("utf-8")
    while len(json_payload) % 4:
        json_payload += b" "

    total_length = 12 + 8 + len(json_payload) + 8 + len(binary)
    return (
        b"glTF"
        + struct.pack("<II", 2, total_length)
        + struct.pack("<I4s", len(json_payload), b"JSON")
        + json_payload
        + struct.pack("<I4s", len(binary), b"BIN\0")
        + bytes(binary)
    )


def parse_model(data: bytes) -> MorayModel:
    if data[:4] == b"MDLS":
        return parse_mdls(data)
    if data[:4] == b"MDL!":
        return parse_mdl_bang(data)
    if data[:4] == b"MDL2":
        return parse_mdl2(data)
    if data[:4] == b"MDL\0":
        return parse_mdl0(data)
    if data[:4] == b"MDLC":
        return parse_mdlc(data)
    if data[:4] == b"MDLX":
        return parse_mdlx(data)
    if data[:4] == b"MDLZ":
        return parse_mdlz(data)
    if data[:4] == b"MDLA":
        return parse_mdla(data)
    if data[:4] == b"MDL\x05":
        return parse_mdl5(data)
    if data[:4] == b"MDL\x03":
        return parse_mdl3_archive(data)
    signature = data[:4].decode("latin1", "replace")
    raise MorayError(
        "unsupported signature "
        f"{signature!r}; this converter accepts MDLS, MDL!, MDL2, MDLC wrappers, "
        "supported MDL NUL object records and chunked tables, supported MDLX primitive scene records, "
        "MDLZ Studio models, MDLA compressed bitmap planes, and MDL5 counted mesh scenes"
    )


def convert_file(input_path: Path, output_path: Path) -> MorayModel:
    data = input_path.read_bytes()
    model = parse_model(data)
    attach_external_textures(model, input_path)
    glb = model_to_glb(model)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = output_path.with_name(output_path.name + ".tmp")
    temp_path.write_bytes(glb)
    os.chmod(temp_path, 0o664)
    temp_path.replace(output_path)
    os.chmod(output_path, 0o664)
    return model


def classify_file(path: Path) -> str:
    data = path.read_bytes()[:64]
    if len(data) < 4:
        return "too short to contain a signature"
    if data.startswith(b"00000000: 4d 44 4c 5a"):
        return "ASCII xxd dump of an MDLZ file, not a binary model"
    sig = data[:4]
    if sig == b"MDLS":
        if len(data) >= 12 and u32(path.read_bytes(), 4) == path.stat().st_size - 8:
            return "MDLS chunked polygon model"
        return "MDLS-like data with invalid size header"
    known = {
        b"MDL!": "MDL! polygon model",
        b"MDL2": "MDL2 indexed polygon model",
        b"MDLX": "MDLX procedural scene/model family, header recognized",
        b"MDLC": "MDLC encoded wrapper around an inner model/scene stream",
        b"MDLZ": "MDLZ Studio polygon model",
        b"MDL7": "MDL7 model family, not decoded",
        b"MDLA": "MDLA compressed bitmap plane",
        b"MDL\0": "MDL NUL object-record/chunked-table model family",
        b"MDL\x03": "MDL\\x03 archive of embedded Granny/RAD GRN assets; outer table recognized but GRN geometry is not decoded",
        b"MDL\x05": "MDL\\x05 counted mesh scene",
    }
    return known.get(sig, f"unsupported signature {sig!r}")


def make_report(sample_root: Path, glb_root: Path, report_path: Path, viewer_path: Path) -> None:
    viewer = viewer_path.read_text(encoding="utf-8")
    rows_by_dir: dict[str, list[str]] = {}
    for src in sorted(p for p in sample_root.rglob("*") if p.is_file()):
        rel = src.relative_to(sample_root)
        out = glb_root / rel.with_suffix(rel.suffix + ".glb")
        status = ""
        viewer_html = ""
        try:
            model = convert_file(src, out)
            glb_b64 = base64.b64encode(out.read_bytes()).decode("ascii")
            poly_count = sum(block.polygon_count for block in model.models)
            vertex_count = sum(block.vertex_count for block in model.models)
            status = (
                f"converted: {model.source_kind}, {len(model.models)} block(s), "
                f"{vertex_count} source vertices, {poly_count} polygons"
            )
            viewer_html = (
                '<model-viewer loading="lazy" interaction-prompt="none" '
                'camera-controls="" touch-action="none" '
                f'src="data:model/gltf-binary;base64,{glb_b64}" '
                'shadow-intensity="0" ar-status="not-presenting"></model-viewer>'
            )
        except Exception as exc:
            if out.exists():
                out.unlink()
            status = f"skipped: {classify_file(src)}; {exc}"
        card = (
            '<article class="card">'
            f"<h3>{html_escape(rel.name)}</h3>"
            f'<p class="meta">{html_escape(str(rel))} · {src.stat().st_size} bytes</p>'
            f"<p>{html_escape(status)}</p>"
            f"{viewer_html}"
            "</article>"
        )
        rows_by_dir.setdefault(str(rel.parent), []).append(card)

    sections = []
    for dirname, cards in rows_by_dir.items():
        sections.append(
            f"<section><h2>{html_escape(dirname)}</h2><div class=\"grid\">{''.join(cards)}</div></section>"
        )

    html = f"""<!doctype html>
<!-- Vibe coded by Codex -->
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>moRay conversion report</title>
<script type="module">
{viewer}
</script>
<style>
:root {{ color-scheme: dark; background: #111317; color: #e8eaed; font-family: system-ui, sans-serif; }}
body {{ margin: 0; padding: 24px; background: #111317; }}
h1 {{ margin: 0 0 8px; font-size: 28px; }}
h2 {{ margin: 28px 0 12px; font-size: 20px; color: #f2f4f8; }}
h3 {{ margin: 0 0 6px; font-size: 15px; overflow-wrap: anywhere; }}
p {{ margin: 6px 0; line-height: 1.4; color: #cbd2dc; }}
.meta {{ color: #8e98a8; font-size: 12px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(310px, 1fr)); gap: 14px; }}
.card {{ border: 1px solid #2a303a; background: #181c22; border-radius: 8px; padding: 12px; }}
model-viewer {{ display: block; width: 100%; height: 260px; background: #0b0d10; border-radius: 6px; margin-top: 10px; }}
.summary {{ max-width: 980px; color: #b8c0cc; }}
</style>
</head>
<body>
<h1>moRay conversion report</h1>
<p class="summary">Supported polygon families and supported MDLX primitive scene records are converted. Other signatures and MDLX scene records are listed with skip reasons when their byte layout or geometry semantics were not proven completely.</p>
{''.join(sections)}
</body>
</html>
"""
    report_path.write_text(html, encoding="utf-8")
    os.chmod(report_path, 0o664)


def html_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def main(argv: list[str]) -> int:
    if len(argv) == 6 and argv[1] == "--report":
        make_report(Path(argv[2]), Path(argv[3]), Path(argv[4]), Path(argv[5]))
        return 0
    if len(argv) != 3:
        print("usage: moRay.py <inputFile> <outputFile>", file=sys.stderr)
        print(
            "       moRay.py --report <sampleRoot> <glbOutputDir> <reportHtml> <modelViewerJs>",
            file=sys.stderr,
        )
        return 2
    try:
        convert_file(Path(argv[1]), Path(argv[2]))
        return 0
    except Exception as exc:
        output = Path(argv[2])
        if output.exists():
            output.unlink()
        print(f"moRay.py: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

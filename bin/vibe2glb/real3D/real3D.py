#!/usr/bin/env python3
# Vibe coded by Codex

import json
import math
import os
import struct
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


class Real3DError(Exception):
    pass


@dataclass
class Chunk:
    chunk_id: bytes
    data_offset: int
    size: int


@dataclass
class Mesh:
    name: str
    color: tuple
    positions: list
    indices: list
    smooth_flag: int


def read_c_name(raw: bytes) -> str:
    name = raw.split(b"\0", 1)[0]
    return name.decode("latin-1", "replace")


def parse_form_real(data: bytes) -> tuple:
    if len(data) < 12 or data[:4] != b"FORM" or data[8:12] != b"REAL":
        raise Real3DError("not a FORM REAL file")

    be_size = int.from_bytes(data[4:8], "big")
    le_size = int.from_bytes(data[4:8], "little")
    if be_size == len(data) - 8:
        size_endian = "big"
    elif le_size == len(data) - 8:
        size_endian = "little"
    else:
        raise Real3DError("FORM size does not match file length")

    chunks = []
    offset = 12
    while offset < len(data):
        if offset + 8 > len(data):
            raise Real3DError(f"truncated chunk header at 0x{offset:x}")
        chunk_id = data[offset:offset + 4]
        size = int.from_bytes(data[offset + 4:offset + 8], size_endian)
        payload = offset + 8
        end = payload + size
        if end > len(data):
            raise Real3DError(f"chunk {chunk_id!r} overruns file")
        chunks.append(Chunk(chunk_id, payload, size))
        offset = end + (size & 1)
    if offset != len(data):
        raise Real3DError("IFF padding extends past file end")
    return size_endian, chunks


def validate_rvrs(data: bytes, chunk: Chunk) -> tuple:
    if chunk.size != 12:
        raise Real3DError("RVRS chunk is not 12 bytes")
    payload = data[chunk.data_offset:chunk.data_offset + chunk.size]
    platform = payload[:4]
    if platform in (b"AMIG", b"AMGD"):
        major = int.from_bytes(payload[4:8], "big")
        minor = int.from_bytes(payload[8:12], "big")
    elif platform == b"WIND":
        major = int.from_bytes(payload[4:8], "little")
        minor = int.from_bytes(payload[8:12], "little")
    else:
        raise Real3DError(f"unsupported RVRS platform {platform!r}")
    platform_name = "AMIG" if platform == b"AMGD" else platform.decode("ascii")
    return platform_name, major, minor


def parse_robj_polygon_records(
    robj: bytes,
    material_colors: dict | None = None,
    orient_rectangles_by_normal: bool = False,
) -> list:
    meshes = []
    offset = 0
    pending_material = None
    active_material = None
    active_target = None
    active_used = False

    def activate_binding_for_record(record_name: str, obj_type: int, subtype: int) -> None:
        nonlocal pending_material, active_material, active_target, active_used
        if active_material is not None and (active_used or not is_renderable_amig_record(obj_type, subtype)):
            if is_amig_container_header(obj_type, subtype) and record_name != active_target:
                active_material = None
                active_target = None
                active_used = False
        if pending_material is None:
            return
        material_name, target_name = pending_material
        if record_name == target_name:
            active_material = material_name
            active_target = target_name
            active_used = False
            pending_material = None
        elif is_amig_container_header(obj_type, subtype):
            pending_material = None

    def apply_active_material(mesh: Mesh) -> Mesh:
        nonlocal active_used
        if active_material is None or material_colors is None:
            return mesh
        color = material_colors.get(active_material)
        if color is None:
            return mesh
        active_used = True
        return Mesh(mesh.name, color, mesh.positions, mesh.indices, mesh.smooth_flag)

    def append_mesh(mesh: Mesh) -> None:
        meshes.append(apply_active_material(mesh))

    def bind_material_from_range(start: int, end: int) -> None:
        nonlocal pending_material
        binding = extract_amig_smat_binding(robj, start, end)
        if binding is not None:
            pending_material = binding

    while offset < len(robj):
        if offset + 4 <= len(robj) and is_known_amig_property_tag(robj[offset:offset + 4]):
            offset = parse_amig_property(robj, offset, "ROBJ")
            continue
        if offset + 32 > len(robj):
            if all(value == 0 for value in robj[offset:]):
                break
            raise Real3DError(f"truncated ROBJ record at 0x{offset:x}")

        header = robj[offset:offset + 32]
        name = read_c_name(header[:16])
        obj_type = header[16]
        header_flag = header[17]
        header_zero = header[18]
        subtype = header[19]
        reserved = header[20:32]
        activate_binding_for_record(name, obj_type, subtype)

        if subtype == 29:
            if obj_type not in (4, 5):
                raise Real3DError(f"unsupported polygon object type {obj_type} at ROBJ 0x{offset:x}")
            if header_flag != 0 or header_zero != 0 or reserved != b"\0" * 12:
                raise Real3DError(f"unexpected polygon record header bytes at ROBJ 0x{offset:x}")
            if offset + 56 > len(robj):
                raise Real3DError(f"truncated polygon header at ROBJ 0x{offset:x}")

            material_mode = robj[offset + 32]
            if material_mode != 2:
                raise Real3DError(f"unsupported material mode {material_mode} at ROBJ 0x{offset:x}")
            color = tuple(c / 255.0 for c in robj[offset + 33:offset + 36])
            if robj[offset + 36:offset + 42] != b"\0" * 6:
                raise Real3DError(f"unexpected polygon bytes 36..41 at ROBJ 0x{offset:x}")
            vertex_count = int.from_bytes(robj[offset + 42:offset + 44], "big")
            if robj[offset + 44:offset + 48] != b"\0" * 4:
                raise Real3DError(f"unexpected polygon bytes 44..47 at ROBJ 0x{offset:x}")
            face_count = int.from_bytes(robj[offset + 48:offset + 50], "big")
            if robj[offset + 50:offset + 52] != b"\0" * 2:
                raise Real3DError(f"unexpected polygon bytes 50..51 at ROBJ 0x{offset:x}")
            smooth_flag = int.from_bytes(robj[offset + 52:offset + 56], "big")
            if smooth_flag not in (0, 1):
                raise Real3DError(f"unsupported polygon smooth flag {smooth_flag} at ROBJ 0x{offset:x}")

            record_size = 56 + vertex_count * 24 + face_count * 10
            if offset + record_size > len(robj):
                raise Real3DError(f"polygon record overruns ROBJ at 0x{offset:x}")

            vertex_offset = offset + 56
            positions = []
            for i in range(vertex_count):
                x, y, z = struct.unpack_from(">ddd", robj, vertex_offset + i * 24)
                if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
                    raise Real3DError(f"non-finite vertex in {name!r} at index {i}")
                positions.append((x, y, z))

            face_offset = vertex_offset + vertex_count * 24
            indices = []
            for i in range(face_count):
                a, b, c = struct.unpack_from(">HHH", robj, face_offset + i * 10)
                if max(a, b, c) >= vertex_count:
                    raise Real3DError(f"face index out of range in {name!r} at face {i}")
                face_attr = robj[face_offset + i * 10 + 6:face_offset + i * 10 + 10]
                if face_attr != b"\xff\xff\xff\0":
                    raise Real3DError(f"unsupported face attribute bytes in {name!r} at face {i}")
                indices.extend((a, b, c))

            append_mesh(Mesh(name, color, positions, indices, smooth_flag))
            offset += record_size
        elif subtype == 10 and obj_type in (4, 5):
            record_size, positions, indices, color = parse_amig_rectangle_record(
                robj, offset, name, orient_rectangles_by_normal
            )
            append_mesh(Mesh(name, color, positions, indices, 0))
            offset += record_size
        elif subtype == 10 and obj_type in (12, 13):
            new_offset = parse_amig_mapped_surface_record(robj, offset, name)
            bind_material_from_range(offset, new_offset)
            offset = new_offset
        elif subtype == 33 and obj_type in (4, 5, 12):
            offset = parse_amig_point_light_record(robj, offset, name)
        elif subtype == 11 and obj_type in (4, 5, 13):
            new_offset, mesh = parse_amig_box_record(robj, offset, name)
            append_mesh(mesh)
            offset = new_offset
        elif subtype == 14 and obj_type in (4, 5, 13):
            new_offset, mesh = parse_amig_old_polygon_record(robj, offset, name)
            append_mesh(mesh)
            offset = new_offset
        elif subtype == 15 and obj_type in (4, 5, 13):
            new_offset, mesh = parse_amig_prism_record(robj, offset, name)
            append_mesh(mesh)
            offset = new_offset
        elif subtype == 22 and obj_type in (4, 5, 13):
            new_offset, mesh = parse_amig_ellipsoid_record(robj, offset, name)
            if mesh.indices:
                append_mesh(mesh)
            offset = new_offset
        elif subtype == 22 and obj_type == 12:
            new_offset = parse_amig_mapped_ellipsoid_record(robj, offset, name)
            bind_material_from_range(offset, new_offset)
            offset = new_offset
        elif subtype == 18 and obj_type in (4, 5, 13):
            new_offset, mesh = parse_amig_ellipse_record(robj, offset, name)
            append_mesh(mesh)
            offset = new_offset
        elif subtype in (19, 21, 23, 24) and obj_type in (4, 5, 13):
            new_offset, mesh = parse_amig_two_ring_record(robj, offset, name)
            append_mesh(mesh)
            offset = new_offset
        elif subtype in (19, 21, 23, 24) and obj_type == 12:
            new_offset = parse_amig_mapped_two_ring_record(robj, offset, name)
            bind_material_from_range(offset, new_offset)
            offset = new_offset
        elif subtype == 20 and obj_type in (4, 5, 13):
            new_offset, mesh = parse_amig_cone_record(robj, offset, name)
            if not is_amig_light_helper(name, obj_type):
                append_mesh(mesh)
            offset = new_offset
        elif subtype == 26 and obj_type in (4, 5, 12, 13):
            new_offset, mesh = parse_amig_grid_mesh_record(robj, offset, name)
            append_mesh(mesh)
            offset = new_offset
        elif subtype in (35, 36) and obj_type in (4, 5, 12, 13):
            offset = parse_amig_coordsys_record(robj, offset, name)
        elif subtype == 37 and obj_type in (4, 5, 13):
            offset = parse_amig_vector_marker_record(robj, offset, name)
        elif subtype == 34:
            offset = parse_amig_line_record(robj, offset, name)
        elif subtype == 32:
            offset = parse_amig_nonmesh_record(robj, offset, name)
        elif subtype == 27:
            offset = parse_amig_group_reference_record(robj, offset, name)
        elif subtype == 38:
            offset = parse_amig_material_wrapper_record(robj, offset, name)
        elif obj_type in (8, 9, 10, 11) and header_flag == 0 and header_zero == 0 and subtype == 2:
            offset = parse_amig_container_record(robj, offset, name)
        elif obj_type in (8, 9, 12) and header_flag == 0 and header_zero == 0 and subtype == 28:
            offset = parse_amig_container_record(robj, offset, name)
        elif obj_type in (2, 3) and header_flag == 0 and header_zero == 0 and subtype in (1, 2):
            offset += 32
        else:
            raise Real3DError(
                f"unsupported ROBJ record at 0x{offset:x}: type={obj_type} subtype={subtype}"
            )

    if not meshes:
        raise Real3DError("ROBJ contains no polygon meshes")
    return meshes


def parse_amig_surface_vectors(robj: bytes, offset: int, name: str) -> tuple:
    if offset + 138 > len(robj):
        raise Real3DError(f"surface record overruns ROBJ at 0x{offset:x}")
    if robj[offset + 36:offset + 42] != b"\0" * 6:
        raise Real3DError(f"unexpected surface bytes 36..41 in {name!r} at ROBJ 0x{offset:x}")

    points = []
    for i in range(3):
        x, y, z = struct.unpack_from(">ddd", robj, offset + 42 + i * 24)
        if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
            raise Real3DError(f"non-finite surface point in {name!r}")
        points.append((x, y, z))

    normal = struct.unpack_from(">ddd", robj, offset + 114)
    if not all(math.isfinite(v) for v in normal):
        raise Real3DError(f"non-finite surface normal in {name!r}")
    normal_length = math.sqrt(sum(v * v for v in normal))
    if not 0.0 <= normal_length < 1e6:
        raise Real3DError(f"unsupported surface normal length in {name!r}: {normal_length}")
    return points, normal


def parse_amig_rectangle_record(
    robj: bytes,
    offset: int,
    name: str,
    orient_by_normal: bool = False,
) -> tuple:
    record_size = 138
    points, normal = parse_amig_surface_vectors(robj, offset, name)
    a, b, c = points
    d = tuple(b[i] + c[i] - a[i] for i in range(3))
    positions = [a, b, c, d]
    color = tuple(channel / 255.0 for channel in robj[offset + 33:offset + 36])
    if color == (0.0, 0.0, 0.0):
        color = (0.75, 0.75, 0.75)
    indices = rectangle_indices_for_normal(positions, normal) if orient_by_normal else [0, 2, 1, 1, 2, 3]
    return record_size, positions, indices, color


def parse_amig_mapped_surface_record(robj: bytes, offset: int, name: str) -> int:
    parse_amig_surface_vectors(robj, offset, name)
    smat_offset = offset + 138
    if smat_offset + 4 > len(robj) or robj[smat_offset:smat_offset + 4] != b"SMAT":
        raise Real3DError(f"mapped surface {name!r} missing SMAT footer at ROBJ 0x{offset:x}")
    return parse_amig_property(robj, smat_offset, name)


def parse_amig_point_light_record(robj: bytes, offset: int, name: str) -> int:
    record_size = 66
    if offset + record_size > len(robj):
        raise Real3DError(f"point light record overruns ROBJ at 0x{offset:x}")
    if robj[offset + 16] != 12 and robj[offset + 36:offset + 42] != b"\0" * 6:
        raise Real3DError(f"unexpected point light bytes 36..41 in {name!r} at ROBJ 0x{offset:x}")
    x, y, z = struct.unpack_from(">ddd", robj, offset + 42)
    if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
        raise Real3DError(f"non-finite point light position in {name!r}")
    new_offset = skip_amig_inline_properties(robj, offset + record_size, name)
    if new_offset == len(robj) or looks_like_amig_record_header(robj, new_offset):
        return new_offset
    next_header = find_next_amig_record_header(robj, new_offset)
    return len(robj) if next_header is None else next_header


def parse_amig_vector_marker_record(robj: bytes, offset: int, name: str) -> int:
    record_size = 66
    if offset + record_size > len(robj):
        raise Real3DError(f"AMIG vector marker overruns ROBJ at 0x{offset:x}")
    if robj[offset + 36:offset + 42] != b"\0" * 6:
        raise Real3DError(f"unexpected AMIG vector marker header bytes in {name!r} at ROBJ 0x{offset:x}")
    x, y, z = struct.unpack_from(">ddd", robj, offset + 42)
    if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
        raise Real3DError(f"non-finite AMIG vector marker position in {name!r}")
    return skip_amig_inline_properties(robj, offset + record_size, name)


def parse_amig_coordsys_record(robj: bytes, offset: int, name: str) -> int:
    record_size, values = parse_amig_parametric_values(robj, offset, name, 12)
    for i in range(0, 12, 3):
        vector = values[i:i + 3]
        if math.sqrt(sum(v * v for v in vector)) > 1e6:
            raise Real3DError(f"unsupported AMIG coordsys vector in {name!r}")
    return skip_amig_inline_properties(robj, offset + record_size, name)


def parse_amig_line_record(robj: bytes, offset: int, name: str) -> int:
    if offset + 52 > len(robj):
        raise Real3DError(f"truncated AMIG line record {name!r} at ROBJ 0x{offset:x}")
    if robj[offset + 36:offset + 42] != b"\0" * 6:
        raise Real3DError(f"unexpected AMIG line header bytes in {name!r} at ROBJ 0x{offset:x}")
    count = int.from_bytes(robj[offset + 42:offset + 44], "big")
    if count < 2 or count > 4096:
        raise Real3DError(f"unsupported AMIG line point count {count} in {name!r}")
    vertex_start = 52
    min_end = offset + vertex_start + count * 24
    if min_end > len(robj):
        raise Real3DError(f"AMIG line record {name!r} overruns ROBJ at 0x{offset:x}")
    for i in range(count):
        x, y, z = struct.unpack_from(">ddd", robj, offset + vertex_start + i * 24)
        if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
            raise Real3DError(f"non-finite AMIG line point in {name!r} at index {i}")
    pos = skip_amig_inline_properties(robj, min_end, name)
    if pos == len(robj) or looks_like_amig_record_header(robj, pos):
        return pos
    next_header = find_next_amig_record_header(robj, pos)
    if next_header is not None:
        return next_header
    return len(robj)


def parse_amig_nonmesh_record(robj: bytes, offset: int, name: str) -> int:
    if offset + 42 > len(robj):
        raise Real3DError(f"truncated AMIG nonmesh record {name!r} at ROBJ 0x{offset:x}")
    if robj[offset + 36:offset + 42] != b"\0" * 6:
        raise Real3DError(f"unexpected AMIG nonmesh header bytes in {name!r} at ROBJ 0x{offset:x}")
    next_header = find_next_amig_record_header(robj, offset + 42)
    if next_header is None:
        return len(robj)
    return next_header


def parse_amig_group_reference_record(robj: bytes, offset: int, name: str) -> int:
    if offset + 60 > len(robj):
        raise Real3DError(f"truncated AMIG group reference {name!r} at ROBJ 0x{offset:x}")
    entry_count = int.from_bytes(robj[offset + 42:offset + 44], "big")
    if entry_count not in (1, 2, 8):
        raise Real3DError(f"unsupported AMIG group reference count {entry_count} in {name!r}")
    if entry_count == 8:
        pos = offset + 88
    else:
        pos = offset + 60
    start = pos
    while pos + 4 <= len(robj) and is_known_amig_property_tag(robj[pos:pos + 4]):
        pos = parse_amig_property(robj, pos, name)
    if pos == start:
        raise Real3DError(f"unsupported AMIG group reference payload in {name!r}")
    pos = skip_amig_inline_properties(robj, pos, name)
    if pos != len(robj) and not looks_like_amig_record_header(robj, pos):
        raise Real3DError(f"AMIG group reference {name!r} ended at non-record byte 0x{pos:x}")
    return pos


def parse_amig_material_wrapper_record(robj: bytes, offset: int, name: str) -> int:
    if offset + 36 > len(robj):
        raise Real3DError(f"truncated AMIG material wrapper {name!r} at ROBJ 0x{offset:x}")
    if robj[offset + 32:offset + 36] == b"SMAT":
        return parse_amig_property(robj, offset + 32, name)
    if robj[offset + 32:offset + 36] == b"FKNO":
        next_offset = parse_amig_property(robj, offset + 32, name)
        if next_offset + 4 > len(robj) or robj[next_offset:next_offset + 4] != b"SMAT":
            raise Real3DError(f"AMIG material wrapper {name!r} missing SMAT after FKNO")
        return parse_amig_property(robj, next_offset, name)
    raise Real3DError(f"AMIG material wrapper {name!r} missing SMAT at ROBJ 0x{offset:x}")


def find_next_amig_record_header(robj: bytes, offset: int) -> int | None:
    for pos in range(offset, len(robj) - 31):
        if looks_like_amig_record_header(robj, pos):
            return pos
    return None


def parse_amig_property(robj: bytes, offset: int, name: str) -> int:
    tag = robj[offset:offset + 4]
    if tag == b"VPHS":
        require_finite_amig_doubles(robj, offset + 8, 3, name)
        short_end = finish_amig_property(robj, offset + 32)
        if short_end == len(robj) or is_known_amig_property_tag(robj[short_end:short_end + 4]) or looks_like_amig_record_header(robj, short_end):
            return short_end
        require_finite_amig_doubles(robj, offset + 8, 4, name)
        return finish_amig_property(robj, offset + 40)
    if tag in (b"VSPI", b"VVEL", b"DDIV", b"DDIR", b"VTIM", b"VTIE", b"VTIS", b"VCRE"):
        require_finite_amig_doubles(robj, offset + 8, 3, name)
        return finish_amig_property(robj, offset + 32)
    if tag in (b"VFRQ", b"VMOV", b"VROT", b"VSCA", b"VSHE"):
        require_finite_amig_doubles(robj, offset + 8, 3, name)
        return finish_amig_property(robj, offset + 32)
    if tag == b"VPOS":
        require_finite_amig_doubles(robj, offset + 8, 3, name)
        return finish_amig_property(robj, offset + 32)
    if tag == b"FLSF":
        require_finite_amig_doubles(robj, offset + 8, 1, name)
        if offset + 24 > len(robj) or robj[offset + 16:offset + 24] != b"\0" * 8:
            raise Real3DError(f"AMIG property FLSF tail is not zero in {name!r}")
        return finish_amig_property(robj, offset + 24)
    if tag == b"ILBR":
        if offset + 12 > len(robj):
            raise Real3DError(f"truncated AMIG ILBR property in {name!r}")
        value_a = int.from_bytes(robj[offset + 4:offset + 8], "big")
        value_b = int.from_bytes(robj[offset + 8:offset + 12], "big")
        if value_a > 0x100000 or value_b > 0x100000:
            raise Real3DError(f"invalid AMIG ILBR property in {name!r}")
        return finish_amig_property(robj, offset + 12)
    if tag == b"MCOG":
        require_finite_amig_doubles(robj, offset + 8, 3, name)
        if offset + 40 <= len(robj) and robj[offset + 32:offset + 40] == b"\0" * 8:
            padded = finish_amig_property(robj, offset + 40)
            if padded == len(robj) or is_known_amig_property_tag(robj[padded:padded + 4]) or looks_like_amig_record_header(robj, padded):
                return padded
        return finish_amig_property(robj, offset + 32)
    if tag == b"FMAS":
        require_finite_amig_doubles(robj, offset + 8, 1, name)
        if offset + 24 > len(robj) or robj[offset + 16:offset + 24] != b"\0" * 8:
            raise Real3DError(f"AMIG property FMAS tail is not zero in {name!r}")
        return offset + 24
    if tag == b"FFRI":
        require_finite_amig_doubles(robj, offset + 8, 1, name)
        return offset + 16
    if tag == b"FORC":
        require_finite_amig_doubles(robj, offset + 8, 1, name)
        return finish_amig_property(robj, offset + 16)
    if tag in (b"ITRA", b"ITRF"):
        if offset + 12 > len(robj):
            raise Real3DError(f"truncated AMIG {tag.decode('ascii')} property in {name!r}")
        if offset + 20 <= len(robj) and not (
            is_known_amig_property_tag(robj[offset + 12:offset + 16])
            or looks_like_amig_record_header(robj, offset + 12)
        ):
            return finish_amig_property(robj, offset + 20)
        return finish_amig_property(robj, offset + 12)
    if tag == b"FKNO":
        require_finite_amig_doubles(robj, offset + 8, 1, name)
        if offset + 24 <= len(robj) and robj[offset + 16:offset + 24] == b"\0" * 8:
            return finish_amig_property(robj, offset + 24)
        return finish_amig_property(robj, offset + 16)
    if tag in (b"IFLG", b"IOCT"):
        if offset + 12 > len(robj):
            raise Real3DError(f"truncated AMIG {tag.decode('ascii')} property in {name!r}")
        value_a = int.from_bytes(robj[offset + 4:offset + 8], "big")
        value_b = int.from_bytes(robj[offset + 8:offset + 12], "big")
        if value_a > 0x100000 or value_b > 0x100000:
            raise Real3DError(f"invalid AMIG {tag.decode('ascii')} property in {name!r}")
        return finish_amig_property(robj, offset + 12)
    if tag in (b"ISKE", b"IINH"):
        if offset + 12 > len(robj):
            raise Real3DError(f"truncated AMIG {tag.decode('ascii')} property in {name!r}")
        key_a = int.from_bytes(robj[offset + 4:offset + 8], "big")
        key_b = int.from_bytes(robj[offset + 8:offset + 12], "big")
        if key_a > 65535 or key_b > 65535:
            raise Real3DError(f"invalid AMIG {tag.decode('ascii')} property in {name!r}")
        return finish_amig_property(robj, offset + 12)
    if tag in (b"SMTH", b"SFOR", b"SDEL", b"SCRE", b"SIDE", b"SOBJ", b"SMAT", b"SCOP"):
        if offset + 12 > len(robj):
            raise Real3DError(f"truncated AMIG string property {tag.decode('ascii')} in {name!r}")
        name_len = int.from_bytes(robj[offset + 8:offset + 12], "big")
        value_end = offset + 12 + name_len
        padded_end = value_end + 8
        if name_len == 0 or value_end > len(robj):
            raise Real3DError(f"invalid AMIG string property length in {name!r}")
        value = robj[offset + 12:offset + 12 + name_len]
        if value[-1:] != b"\0":
            raise Real3DError(f"AMIG string property is not NUL terminated in {name!r}")
        if (
            value_end == len(robj)
            or is_known_amig_property_tag(robj[value_end:value_end + 4])
            or looks_like_amig_record_header(robj, value_end)
        ):
            return value_end
        if padded_end <= len(robj) and robj[padded_end - 8:padded_end] == b"\0" * 8:
            return padded_end
        if value_end + 8 <= len(robj):
            tail_a = int.from_bytes(robj[value_end:value_end + 4], "big")
            tail_b = int.from_bytes(robj[value_end + 4:value_end + 8], "big")
            if tail_a <= 0x10000 and tail_b in (0, 1, 0x100, 0x10000, 0x1000000):
                return value_end + 8
        if (
            value_end + 4 <= len(robj)
            and robj[value_end:value_end + 4] == b"\0" * 4
            and (
                value_end + 4 == len(robj)
                or is_known_amig_property_tag(robj[value_end + 4:value_end + 8])
                or looks_like_amig_record_header(robj, value_end + 4)
            )
        ):
            return value_end + 4
        raise Real3DError(f"AMIG string property tail is not zero in {name!r}")
    raise Real3DError(f"unsupported AMIG property tag at ROBJ 0x{offset:x}")


def finish_amig_property(robj: bytes, offset: int) -> int:
    if offset + 4 <= len(robj) and robj[offset:offset + 4] == b"\0" * 4:
        padded = offset + 4
        if (
            padded == len(robj)
            or is_known_amig_property_tag(robj[padded:padded + 4])
            or looks_like_amig_record_header(robj, padded)
        ):
            return padded
    return offset


def skip_amig_inline_properties(robj: bytes, offset: int, name: str) -> int:
    while offset < len(robj):
        if offset + 4 <= len(robj) and is_known_amig_property_tag(robj[offset:offset + 4]):
            offset = parse_amig_property(robj, offset, name)
            continue
        padded = False
        for pad in (2, 4, 8, 12):
            if (
                offset + pad + 4 <= len(robj)
                and robj[offset:offset + pad] == b"\0" * pad
                and (
                    is_known_amig_property_tag(robj[offset + pad:offset + pad + 4])
                    or looks_like_amig_record_header(robj, offset + pad)
                )
            ):
                offset += pad
                padded = True
                break
        if not padded:
            break
    return offset


def is_known_amig_property_tag(tag: bytes) -> bool:
    return tag in (
        b"VPHS", b"VSPI", b"VVEL", b"DDIV", b"DDIR", b"VTIM", b"VTIE", b"VTIS", b"VCRE",
        b"VFRQ", b"VMOV", b"VROT", b"VSCA", b"VSHE", b"VPOS", b"MCOG", b"FMAS", b"FFRI",
        b"FKNO", b"FORC", b"ITRA", b"ITRF", b"IFLG", b"IOCT", b"ISKE", b"IINH", b"ILBR", b"FLSF",
        b"SMTH", b"SFOR", b"SDEL", b"SCRE", b"SCOP",
        b"SIDE", b"SOBJ", b"SMAT",
    )


def is_renderable_amig_record(obj_type: int, subtype: int) -> bool:
    if subtype == 29 and obj_type in (4, 5):
        return True
    if subtype == 10 and obj_type in (4, 5):
        return True
    if subtype in (11, 14, 15, 18, 20, 22, 26) and obj_type in (4, 5, 13):
        return True
    if subtype in (19, 21, 23, 24) and obj_type in (4, 5, 13):
        return True
    return False


def is_amig_container_header(obj_type: int, subtype: int) -> bool:
    return (
        obj_type in (2, 3, 8, 9, 10, 11, 12)
        and subtype in (1, 2, 27, 28, 32)
    )


def is_amig_light_helper(name: str, obj_type: int) -> bool:
    return obj_type == 13 and name.lower().startswith("light_")


def extract_amig_smat_binding(robj: bytes, start: int, end: int) -> tuple | None:
    offset = start
    while offset < end:
        smat = robj.find(b"SMAT", offset, end)
        if smat < 0:
            return None
        property_end = parse_amig_property(robj, smat, "SMAT")
        if property_end <= end:
            name_len = int.from_bytes(robj[smat + 8:smat + 12], "big")
            material = read_c_name(robj[smat + 12:smat + 12 + name_len])
            target = read_c_name(robj[property_end:property_end + 16])
            if material and target and looks_like_amig_record_header(robj, property_end):
                return material, target
        offset = smat + 4
    return None


def parse_amig_container_record(robj: bytes, offset: int, name: str) -> int:
    pos = offset + 32
    while pos + 4 <= len(robj) and is_known_amig_property_tag(robj[pos:pos + 4]):
        pos = parse_amig_property(robj, pos, name)
    if pos == offset + 32:
        raise Real3DError(f"unsupported AMIG container payload in {name!r} at 0x{offset:x}")
    pos = skip_amig_inline_properties(robj, pos, name)
    if pos != len(robj) and not looks_like_amig_record_header(robj, pos):
        raise Real3DError(f"AMIG container {name!r} ended at non-record byte 0x{pos:x}")
    return pos


def require_finite_amig_doubles(data: bytes, offset: int, count: int, name: str) -> None:
    if offset + count * 8 > len(data):
        raise Real3DError(f"truncated AMIG numeric payload in {name!r}")
    for i in range(count):
        value = struct.unpack_from(">d", data, offset + i * 8)[0]
        if not math.isfinite(value):
            raise Real3DError(f"non-finite AMIG numeric payload in {name!r}")


def parse_amig_parametric_values(robj: bytes, offset: int, name: str, count: int, finite_count: int | None = None) -> tuple:
    data_start = 42
    record_size = data_start + count * 8
    if offset + record_size > len(robj):
        raise Real3DError(f"AMIG parametric record overruns ROBJ at 0x{offset:x}")
    if robj[offset + 36:offset + data_start] != b"\0" * (data_start - 36):
        raise Real3DError(f"unexpected AMIG parametric header bytes in {name!r} at ROBJ 0x{offset:x}")
    values = [struct.unpack_from(">d", robj, offset + data_start + i * 8)[0] for i in range(count)]
    checked_values = values if finite_count is None else values[:finite_count]
    if not all(math.isfinite(v) for v in checked_values):
        raise Real3DError(f"non-finite AMIG parametric value in {name!r}")
    return record_size, values


def parse_amig_box_record(robj: bytes, offset: int, name: str) -> tuple:
    record_size = 138
    points, normal = parse_amig_surface_vectors(robj, offset, name)
    a, b, c = points
    d = tuple(b[i] + c[i] - a[i] for i in range(3))
    e = tuple(a[i] + normal[i] for i in range(3))
    f = tuple(b[i] + normal[i] for i in range(3))
    g = tuple(c[i] + normal[i] for i in range(3))
    h = tuple(d[i] + normal[i] for i in range(3))
    positions = [a, b, c, d, e, f, g, h]
    indices = [
        0, 2, 1, 1, 2, 3,
        4, 5, 6, 5, 7, 6,
        0, 1, 4, 1, 5, 4,
        1, 3, 5, 3, 7, 5,
        3, 2, 7, 2, 6, 7,
        2, 0, 6, 0, 4, 6,
    ]
    return offset + record_size, Mesh(name, amig_record_color(robj, offset), positions, indices, 0)


def triangulate_fan(count: int, reverse: bool = False) -> list:
    indices = []
    for i in range(1, count - 1):
        if reverse:
            indices.extend((0, i + 1, i))
        else:
            indices.extend((0, i, i + 1))
    return indices


def parse_amig_old_polygon_record(robj: bytes, offset: int, name: str) -> tuple:
    if offset + 72 > len(robj):
        raise Real3DError(f"truncated AMIG old polygon record {name!r} at ROBJ 0x{offset:x}")
    if robj[offset + 36:offset + 42] != b"\0" * 6:
        raise Real3DError(f"unexpected AMIG old polygon header bytes in {name!r} at ROBJ 0x{offset:x}")
    count = int.from_bytes(robj[offset + 42:offset + 44], "big")
    if count < 3 or count > 4096:
        raise Real3DError(f"unsupported AMIG old polygon point count {count} in {name!r}")
    for i in range(3):
        value = struct.unpack_from(">d", robj, offset + 48 + i * 8)[0]
        if not math.isfinite(value):
            raise Real3DError(f"non-finite AMIG old polygon control value in {name!r}")

    stored_count = count + (3 if robj[offset + 16] == 13 else 0)
    vertex_start = 72
    record_size = vertex_start + stored_count * 24
    if offset + record_size > len(robj):
        raise Real3DError(f"AMIG old polygon {name!r} overruns ROBJ at 0x{offset:x}")
    positions = []
    for i in range(stored_count):
        x, y, z = struct.unpack_from(">ddd", robj, offset + vertex_start + i * 24)
        if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
            raise Real3DError(f"non-finite AMIG old polygon point in {name!r} at index {i}")
        if i < count:
            positions.append((x, y, z))
    new_offset = skip_amig_inline_properties(robj, offset + record_size, name)
    if new_offset != len(robj) and not looks_like_amig_record_header(robj, new_offset):
        raise Real3DError(f"AMIG old polygon {name!r} ended at non-record byte 0x{new_offset:x}")
    contours = split_coordinate_closed_contours(positions, list(range(count)))
    indices = triangulate_planar_contours(positions, contours)
    return new_offset, Mesh(name, amig_record_color(robj, offset), positions, indices, 0)


def parse_amig_prism_record(robj: bytes, offset: int, name: str) -> tuple:
    if offset + 72 > len(robj):
        raise Real3DError(f"truncated AMIG prism record {name!r} at ROBJ 0x{offset:x}")
    if robj[offset + 36:offset + 42] != b"\0" * 6:
        raise Real3DError(f"unexpected AMIG prism header bytes in {name!r} at ROBJ 0x{offset:x}")
    count = int.from_bytes(robj[offset + 42:offset + 44], "big")
    if count < 3 or count > 4096:
        raise Real3DError(f"unsupported AMIG prism point count {count} in {name!r}")
    record_size = 48 + (count + 1) * 24
    if offset + record_size > len(robj):
        raise Real3DError(f"AMIG prism {name!r} overruns ROBJ at 0x{offset:x}")
    extrusion = struct.unpack_from(">ddd", robj, offset + 48)
    if not all(math.isfinite(v) for v in extrusion):
        raise Real3DError(f"non-finite AMIG prism extrusion in {name!r}")
    base = []
    for i in range(count):
        x, y, z = struct.unpack_from(">ddd", robj, offset + 72 + i * 24)
        if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
            raise Real3DError(f"non-finite AMIG prism point in {name!r} at index {i}")
        base.append((x, y, z))
    top = [tuple(point[i] + extrusion[i] for i in range(3)) for point in base]
    positions = base + top
    indices = triangulate_fan(count)
    indices.extend(count + value for value in triangulate_fan(count, reverse=True))
    for i in range(count):
        j = (i + 1) % count
        indices.extend((i, count + i, j, j, count + i, count + j))
    new_offset = skip_amig_inline_properties(robj, offset + record_size, name)
    if new_offset != len(robj) and not looks_like_amig_record_header(robj, new_offset):
        raise Real3DError(f"AMIG prism {name!r} ended at non-record byte 0x{new_offset:x}")
    return new_offset, Mesh(name, amig_record_color(robj, offset), positions, indices, 0)


def parse_amig_ellipsoid_record(robj: bytes, offset: int, name: str) -> tuple:
    try:
        record_size, values = parse_amig_parametric_values(robj, offset, name, 14, finite_count=12)
    except Real3DError:
        smat_offset = robj.find(b"SMAT", offset + 120, min(len(robj), offset + 220))
        if smat_offset >= 0:
            return parse_amig_property(robj, smat_offset, name), Mesh(name, amig_record_color(robj, offset), [], [], 0)
        raise
    has_extended_tail = abs(values[12]) > 1e-9 or abs(values[13]) > 1e-9
    center = tuple(values[0:3])
    axis_u = tuple(values[3:6])
    axis_v = tuple(values[6:9])
    axis_w = tuple(values[9:12])
    for axis in (axis_u, axis_v, axis_w):
        length = math.sqrt(sum(v * v for v in axis))
        if not 1e-9 < length < 1e6:
            raise Real3DError(f"invalid AMIG ellipsoid axis length in {name!r}")
    positions, indices = make_ellipsoid_mesh(center, axis_u, axis_v, axis_w)
    if has_extended_tail:
        next_header = find_next_amig_record_header(robj, offset + record_size)
        if next_header is None:
            raise Real3DError(f"unsupported AMIG ellipsoid trailing values in {name!r}")
        record_end = next_header
    else:
        record_end = offset + record_size
    return skip_amig_inline_properties(robj, record_end, name), Mesh(
        name, amig_record_color(robj, offset), positions, indices, 0
    )


def parse_amig_mapped_ellipsoid_record(robj: bytes, offset: int, name: str) -> int:
    try:
        record_size, values = parse_amig_parametric_values(robj, offset, name, 14)
    except Real3DError:
        smat_offset = robj.find(b"SMAT", offset + 120, min(len(robj), offset + 240))
        if smat_offset < 0:
            raise
        return parse_amig_property(robj, smat_offset, name)
    if abs(values[12]) > math.tau + 1e-3 or abs(values[13]) > math.tau + 1e-3:
        smat_offset = robj.find(b"SMAT", offset + 120, min(len(robj), offset + 180))
        if smat_offset < 0:
            raise Real3DError(f"unsupported AMIG mapped ellipsoid trailing values in {name!r}")
        return parse_amig_property(robj, smat_offset, name)
    return skip_amig_inline_properties(robj, offset + record_size, name)


def parse_amig_ellipse_record(robj: bytes, offset: int, name: str) -> tuple:
    record_size, values = parse_amig_parametric_values(robj, offset, name, 12)
    tail = robj[offset + record_size:offset + record_size + 18]
    if tail == b"\0" * 18:
        record_size += 18
    elif (
        len(tail) == 18
        and tail[:10] in (b"\x02\0" + b"\0" * 8, b"\0" * 10)
        and math.isfinite(struct.unpack_from(">d", tail, 10)[0])
    ):
        angle = struct.unpack_from(">d", tail, 10)[0]
        if not 0.0 <= angle <= math.tau + 1e-3:
            raise Real3DError(f"unsupported AMIG ellipse angular value in {name!r}")
        record_size += 18
    else:
        raise Real3DError(f"unsupported AMIG ellipse tail in {name!r} at ROBJ 0x{offset:x}")
    positions, indices = make_disk_mesh(tuple(values[0:3]), tuple(values[3:6]), tuple(values[6:9]), 0.0, 0.0)
    new_offset = offset + record_size
    return skip_amig_inline_properties(robj, new_offset, name), Mesh(
        name, amig_record_color(robj, offset), positions, indices, 0
    )


def parse_amig_two_ring_record(robj: bytes, offset: int, name: str) -> tuple:
    subtype = robj[offset + 19]
    record_size, values = parse_amig_parametric_values(robj, offset, name, 32, finite_count=30)
    if subtype in (23, 24) or not (math.isfinite(values[30]) and math.isfinite(values[31])):
        if not all(math.isfinite(v) for v in values[:30]):
            raise Real3DError(f"non-finite AMIG ring value in {name!r}")
        start_angle, end_angle = 0.0, math.tau
    else:
        try:
            start_angle, end_angle = validate_wind_angles(values[30], values[31], name)
        except Real3DError:
            start_angle, end_angle = 0.0, math.tau
    positions, indices = make_two_ring_mesh(
        tuple(values[12:15]),
        tuple(values[15:18]),
        tuple(values[18:21]),
        tuple(values[21:24]),
        tuple(values[24:27]),
        tuple(values[27:30]),
        start_angle,
        end_angle,
        cap_ends=True,
    )
    record_end = offset + record_size
    if record_end != len(robj) and not looks_like_amig_record_header(robj, record_end):
        extension = parse_amig_counted_index_extension(robj, record_end, name)
        if extension is not None:
            extension_size, extension_positions, extension_indices = extension
            index_base = len(positions)
            positions.extend(extension_positions)
            indices.extend(index_base + index for index in extension_indices)
            record_end += extension_size
    return skip_amig_inline_properties(robj, record_end, name), Mesh(
        name, amig_record_color(robj, offset), positions, indices, 0
    )


def parse_amig_mapped_two_ring_record(robj: bytes, offset: int, name: str) -> int:
    record_size, _values = parse_amig_parametric_values(robj, offset, name, 32, finite_count=30)
    record_end = offset + record_size
    if record_end != len(robj) and not looks_like_amig_record_header(robj, record_end):
        extension = parse_amig_counted_index_extension(robj, record_end, name)
        if extension is not None:
            record_end += extension[0]
    return skip_amig_inline_properties(robj, record_end, name)


def parse_amig_counted_index_extension(robj: bytes, offset: int, name: str) -> tuple | None:
    if offset + 10 > len(robj):
        return None
    vertex_count = int.from_bytes(robj[offset:offset + 2], "big")
    index_count = int.from_bytes(robj[offset + 2:offset + 4], "big")
    if not (3 <= vertex_count <= 4096 and 3 <= index_count <= 65535):
        return None
    if robj[offset + 4:offset + 10] != b"\xff\xff\0\0\0\0":
        return None
    vertex_start = offset + 10
    index_start = vertex_start + vertex_count * 24
    end = index_start + index_count * 2
    if end > len(robj):
        return None
    positions = []
    for i in range(vertex_count):
        x, y, z = struct.unpack_from(">ddd", robj, vertex_start + i * 24)
        if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
            return None
        positions.append((x, y, z))
    words = [int.from_bytes(robj[index_start + i * 2:index_start + i * 2 + 2], "big") for i in range(index_count)]
    if any(word > vertex_count for word in words):
        return None
    indices = triangulate_legacy_index_stream(words)
    if not indices:
        indices = triangulate_fan(vertex_count)
    return end - offset, positions, indices


def parse_amig_cone_record(robj: bytes, offset: int, name: str) -> tuple:
    record_size, values = parse_amig_parametric_values(robj, offset, name, 23, finite_count=21)
    if math.isfinite(values[21]) and math.isfinite(values[22]):
        try:
            start_angle, end_angle = validate_wind_angles(values[21], values[22], name)
        except Real3DError:
            start_angle, end_angle = 0.0, math.tau
    else:
        start_angle, end_angle = 0.0, math.tau
    top_axis_u = tuple(values[3:6])
    top_axis_v = tuple(values[6:9])
    top_axis_w = tuple(values[9:12])
    top_axis_length = math.sqrt(sum(v * v for axis in (top_axis_u, top_axis_v, top_axis_w) for v in axis))
    if top_axis_length > 1e-9:
        positions, indices = make_two_ring_mesh(
            tuple(values[0:3]),
            top_axis_u,
            top_axis_v,
            tuple(values[12:15]),
            tuple(values[15:18]),
            tuple(values[18:21]),
            start_angle,
            end_angle,
            cap_ends=True,
        )
    else:
        positions, indices = make_cone_mesh(
            tuple(values[0:3]),
            tuple(values[12:15]),
            tuple(values[15:18]),
            tuple(values[18:21]),
            start_angle,
            end_angle,
        )
    return skip_amig_inline_properties(robj, offset + record_size, name), Mesh(
        name, amig_record_color(robj, offset), positions, indices, 0
    )


def parse_amig_grid_mesh_record(robj: bytes, offset: int, name: str) -> tuple:
    record_size = None
    rows = int.from_bytes(robj[offset + 42:offset + 44], "big")
    cols = int.from_bytes(robj[offset + 44:offset + 46], "big")
    vertex_count = rows * cols
    if rows < 2 or cols < 2 or vertex_count > 65535:
        raise Real3DError(f"unsupported AMIG grid dimensions in {name!r}: {rows}x{cols}")
    vertex_start = 54
    size = vertex_start + vertex_count * 24
    if offset + size > len(robj):
        raise Real3DError(f"AMIG grid mesh {name!r} overruns ROBJ at 0x{offset:x}")
    if robj[offset + 36:offset + 42] != b"\0" * 6:
        raise Real3DError(f"unexpected AMIG grid header bytes in {name!r} at ROBJ 0x{offset:x}")
    metadata_a = int.from_bytes(robj[offset + 46:offset + 50], "big")
    metadata_b = int.from_bytes(robj[offset + 50:offset + 54], "big")
    if metadata_a == 0 and metadata_b == 0:
        raise Real3DError(f"AMIG grid mesh {name!r} has empty metadata words")
    positions = []
    for i in range(vertex_count):
        x, y, z = struct.unpack_from(">ddd", robj, offset + vertex_start + i * 24)
        if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
            raise Real3DError(f"non-finite AMIG grid point in {name!r} at index {i}")
        positions.append((x, y, z))
    if rows == 2:
        indices = orient_triangles_outward(triangulate_paired_vertex_strip(positions), positions)
    else:
        indices = []
        for r in range(rows - 1):
            for c in range(cols - 1):
                a = r * cols + c
                b = (r + 1) * cols + c
                cidx = (r + 1) * cols + c + 1
                d = r * cols + c + 1
                indices.extend((a, b, cidx, a, cidx, d))
    record_size = size
    return skip_amig_inline_properties(robj, offset + record_size, name), Mesh(
        name, amig_record_color(robj, offset), positions, indices, 0
    )


def looks_like_amig_record_header(robj: bytes, offset: int) -> bool:
    if offset + 32 > len(robj):
        return False
    if not all((32 <= value < 127) or (160 <= value <= 255) or value == 0 for value in robj[offset:offset + 16]):
        return False
    return robj[offset + 16] in range(2, 16) and robj[offset + 18] == 0 and robj[offset + 19] in range(1, 40)


def amig_record_color(robj: bytes, offset: int) -> tuple:
    color = tuple(channel / 255.0 for channel in robj[offset + 33:offset + 36])
    if color == (0.0, 0.0, 0.0):
        color = (0.75, 0.75, 0.75)
    return color


def parse_real3d_polygon_file(path: Path) -> list:
    data = path.read_bytes()
    if data.startswith(b"object \0"):
        return parse_legacy_object_file(data)

    if data[:4] == b"FORM" and data[8:12] == b"REAL" and data[12:16] == b"INFO":
        try:
            return parse_realinfo_poly_file(data)
        except Real3DError:
            pass

    _size_endian, chunks = parse_form_real(data)
    if not chunks or chunks[0].chunk_id != b"RVRS":
        ids = ", ".join(c.chunk_id.decode("latin-1", "replace") for c in chunks)
        raise Real3DError(f"unsupported chunk layout: {ids}")
    platform, major, _minor = validate_rvrs(data, chunks[0])
    if platform == "WIND":
        if major not in (2, 3):
            raise Real3DError(f"unsupported RVRS version/platform: {platform} {major}")
        robj_chunks = [c for c in chunks if c.chunk_id == b"ROBJ"]
        if len(robj_chunks) != 1:
            raise Real3DError("WIND file does not contain exactly one ROBJ chunk")
        robj = data[robj_chunks[0].data_offset:robj_chunks[0].data_offset + robj_chunks[0].size]
        return parse_wind_robj_records(robj)
    if platform != "AMIG" or major not in (2, 3):
        raise Real3DError(f"unsupported RVRS version/platform: {platform} {major}")

    robj_chunks = [c for c in chunks if c.chunk_id == b"ROBJ"]
    if len(robj_chunks) != 1:
        ids = ", ".join(c.chunk_id.decode("latin-1", "replace") for c in chunks)
        raise Real3DError(f"unsupported chunk layout: {ids}")
    validate_amig_non_geometry_chunks(data, chunks)
    material_colors = parse_amig_material_colors(data, chunks)
    robj = data[robj_chunks[0].data_offset:robj_chunks[0].data_offset + robj_chunks[0].size]
    return parse_robj_polygon_records(robj, material_colors, orient_rectangles_by_normal=not material_colors)


def parse_legacy_object_file(data: bytes) -> list:
    if len(data) < 0x56 or not data.startswith(b"object \0"):
        raise Real3DError("not a legacy object file")
    if not legacy_name_field_ok(data, 8):
        raise Real3DError("legacy object header has invalid object name")

    records = solve_legacy_record_layout(data)
    if records is None:
        raise Real3DError("unsupported legacy object record layout")

    meshes = []
    for record in records:
        kind, offset, name, point_count, index_count, vertex_base, record_size = record
        if kind != "mesh":
            continue
        if not legacy_mesh_is_renderable(data, record):
            continue
        mesh = parse_legacy_mesh_record(data, offset, name, point_count, index_count, vertex_base, record_size)
        if mesh.indices:
            meshes.append(mesh)
    if not meshes:
        raise Real3DError("legacy object contains no supported meshes")
    return meshes


def solve_legacy_record_layout(data: bytes) -> list | None:
    memo = {}

    def solve(offset: int) -> list | None:
        if offset == len(data):
            return []
        if offset in memo:
            return memo[offset]
        options = legacy_record_options(data, offset)
        options.sort(key=lambda item: 0 if item[0] == "mesh" else 1)
        for option in options:
            tail = solve(offset + option[6])
            if tail is not None:
                memo[offset] = [option] + tail
                return memo[offset]
        memo[offset] = None
        return None

    return solve(0x56)


def legacy_record_options(data: bytes, offset: int) -> list:
    options = []

    if legacy_continuation_header_ok(data, offset):
        point_count = int.from_bytes(data[offset + 0x08:offset + 0x0a], "big")
        index_count = int.from_bytes(data[offset + 0x0e:offset + 0x10], "big")
        if 0 < point_count <= 4096 and 0 <= index_count <= 65535:
            for vertex_base in (0xd2, 0xe2, 0x2ca):
                record_size = vertex_base + point_count * 32 + index_count * 2
                next_offset = offset + record_size
                if (
                    next_offset <= len(data)
                    and legacy_next_record_ok(data, next_offset)
                    and legacy_mesh_payload_ok(data, offset, point_count, index_count, vertex_base, record_size)
                ):
                    options.append((
                        "mesh",
                        offset,
                        f"continuation_{offset:x}",
                        point_count,
                        index_count,
                        vertex_base,
                        record_size,
                    ))

    if not legacy_name_field_ok(data, offset):
        return options

    name = read_legacy_name(data, offset)
    if offset + 0x5e <= len(data) and legacy_material_name_ok(data, offset):
        point_count = int.from_bytes(data[offset + 0x56:offset + 0x58], "big")
        index_count = int.from_bytes(data[offset + 0x5c:offset + 0x5e], "big")
        if 0 < point_count <= 4096 and 0 <= index_count <= 65535:
            for vertex_base in (0x120, 0x130, 0x318):
                record_size = vertex_base + point_count * 32 + index_count * 2
                next_offset = offset + record_size
                if (
                    next_offset <= len(data)
                    and legacy_next_record_ok(data, next_offset)
                    and legacy_mesh_payload_ok(data, offset, point_count, index_count, vertex_base, record_size)
                ):
                    options.append(("mesh", offset, name, point_count, index_count, vertex_base, record_size))
    if offset + 0x4e <= len(data) and legacy_next_record_ok(data, offset + 0x4e):
        options.append(("group", offset, name, 0, 0, 0, 0x4e))
    return options


def legacy_name_field_ok(data: bytes, offset: int) -> bool:
    if offset + 19 > len(data) or data[offset] == 0:
        return False
    return all((32 <= value < 127) or value == 0 for value in data[offset:offset + 19])


def legacy_next_record_ok(data: bytes, offset: int) -> bool:
    return offset == len(data) or legacy_name_field_ok(data, offset) or legacy_continuation_header_ok(data, offset)


def legacy_material_name_ok(data: bytes, offset: int) -> bool:
    material_offset = offset + 0x100
    return legacy_name_at_offset_ok(data, material_offset)


def legacy_continuation_header_ok(data: bytes, offset: int) -> bool:
    if offset + 0xc5 > len(data) or data[offset:offset + 4] != b"\x0f\x05\x05\x06":
        return False
    point_count = int.from_bytes(data[offset + 0x08:offset + 0x0a], "big")
    index_count = int.from_bytes(data[offset + 0x0e:offset + 0x10], "big")
    if not (0 < point_count <= 4096 and 0 <= index_count <= 65535):
        return False
    return legacy_name_at_offset_ok(data, offset + 0xb2)


def legacy_name_at_offset_ok(data: bytes, material_offset: int) -> bool:
    if material_offset + 19 > len(data) or data[material_offset] == 0:
        return False
    raw = data[material_offset:material_offset + 19]
    nul = raw.find(b"\0")
    if nul <= 0:
        return False
    return all(32 <= value < 127 for value in raw[:nul])


def read_legacy_name(data: bytes, offset: int) -> str:
    return data[offset:offset + 19].split(b"\0", 1)[0].decode("latin-1", "replace")


def legacy_mesh_payload_ok(
    data: bytes,
    offset: int,
    point_count: int,
    index_count: int,
    vertex_base: int,
    record_size: int,
) -> bool:
    vertex_offset = offset + vertex_base
    index_offset = vertex_offset + point_count * 32
    if index_offset + index_count * 2 != offset + record_size or offset + record_size > len(data):
        return False
    try:
        translation = legacy_mesh_translation(data, offset, vertex_base)
        if not all(math.isfinite(value) and abs(value) < 1e7 for value in translation):
            return False
        for i in range(point_count):
            x, y, z, _extra = struct.unpack_from(">dddd", data, vertex_offset + i * 32)
            if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
                return False
        for i in range(index_count):
            value = int.from_bytes(data[index_offset + i * 2:index_offset + i * 2 + 2], "big")
            if value > point_count:
                return False
    except (struct.error, ValueError):
        return False
    return True


def legacy_mesh_type_code(data: bytes, offset: int, vertex_base: int) -> int:
    code_offset = offset + (0x10 if vertex_base < 0x100 else 0x5e)
    return int.from_bytes(data[code_offset:code_offset + 2], "big")


def legacy_mesh_extra_values(data: bytes, offset: int, point_count: int, vertex_base: int) -> list:
    return [
        struct.unpack_from(">d", data, offset + vertex_base + i * 32 + 24)[0]
        for i in range(point_count)
    ]


def legacy_mesh_is_renderable(data: bytes, record: tuple) -> bool:
    _kind, offset, _name, point_count, index_count, vertex_base, _record_size = record
    type_code = legacy_mesh_type_code(data, offset, vertex_base)
    if type_code == 4 and point_count == 8 and index_count == 19:
        if vertex_base < 0x100:
            return False
        if data[offset + 0x13] == 0:
            return False
    if vertex_base < 0x100:
        extras = legacy_mesh_extra_values(data, offset, point_count, vertex_base)
        if extras and all(abs(value) > 1e12 for value in extras):
            return False
    return True


def legacy_mesh_translation(data: bytes, offset: int, vertex_base: int) -> tuple:
    translation_offset = offset + (0x12 if vertex_base < 0x100 else 0x60)
    return struct.unpack_from(">ddd", data, translation_offset)


def parse_legacy_mesh_record(
    data: bytes,
    offset: int,
    name: str,
    point_count: int,
    index_count: int,
    vertex_base: int,
    record_size: int,
) -> Mesh:
    vertex_offset = offset + vertex_base
    index_offset = vertex_offset + point_count * 32
    if index_offset + index_count * 2 != offset + record_size:
        raise Real3DError(f"legacy mesh {name!r} size equation failed at 0x{offset:x}")

    positions = []
    tx, ty, tz = legacy_mesh_translation(data, offset, vertex_base)
    for i in range(point_count):
        x, y, z, _extra = struct.unpack_from(">dddd", data, vertex_offset + i * 32)
        if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
            raise Real3DError(f"non-finite legacy point in {name!r} at index {i}")
        positions.append((x + tx, y + ty, z + tz))

    words = [int.from_bytes(data[index_offset + i * 2:index_offset + i * 2 + 2], "big") for i in range(index_count)]
    for value in words:
        if value > point_count:
            raise Real3DError(f"legacy mesh {name!r} index {value} exceeds point count {point_count}")

    type_code = legacy_mesh_type_code(data, offset, vertex_base)
    indices = triangulate_legacy_mesh_indices(words, positions, type_code, point_count, index_count)
    return Mesh(name, (0.72, 0.72, 0.72), positions, indices, 0)


def triangulate_legacy_mesh_indices(
    words: list,
    positions: list,
    type_code: int,
    point_count: int,
    index_count: int,
) -> list:
    if type_code == 1:
        contours = legacy_type1_contours(words, positions, point_count, index_count)
        if contours is not None:
            return triangulate_planar_contours(positions, contours)
    paired_surface = triangulate_legacy_paired_surface(words, positions)
    if paired_surface is not None:
        return paired_surface
    if type_code == 2 and point_count == 30 and index_count == 39:
        return triangulate_convex_point_cloud(positions)
    if type_code == 12 and point_count == 24 and index_count == 60:
        return orient_triangles_outward(triangulate_two_legacy_rings(12, cap_ends=False), positions)
    if type_code == 4 and point_count == 8 and index_count == 19:
        return triangulate_legacy_box()
    return triangulate_legacy_index_stream(words)


def legacy_type1_contours(words: list, positions: list, point_count: int, index_count: int) -> list | None:
    if point_count < 3:
        return None
    if index_count == point_count and words == list(range(1, point_count + 1)):
        return [list(range(point_count))]
    if (
        index_count == point_count + 1
        and words[:point_count - 1] == list(range(1, point_count))
        and words[point_count - 1] == 1
        and words[point_count] == point_count
    ):
        return split_legacy_type1_contours(positions, list(range(point_count - 1)))
    return None


def triangulate_legacy_paired_surface(words: list, positions: list) -> list | None:
    runs = split_legacy_index_runs(words)
    pair_runs = []
    cursor = 0
    while cursor < len(runs) and len(runs[cursor]) == 2:
        pair_runs.append(runs[cursor])
        cursor += 1
    if len(pair_runs) < 2:
        return None
    expected = 0
    for pair in pair_runs:
        if pair != [expected, expected + 1]:
            return None
        expected += 2
    if expected != len(positions):
        return None
    for run in runs[cursor:]:
        if run not in ([pair[0] for pair in pair_runs], [pair[1] for pair in pair_runs]):
            return None

    indices = []
    for i in range(len(pair_runs) - 1):
        a, b = pair_runs[i]
        c, d = pair_runs[i + 1]
        indices.extend((a, c, b, b, c, d))
    if (
        len(pair_runs) > 2
        and not points_close(positions[pair_runs[0][0]], positions[pair_runs[-1][0]])
        and not points_close(positions[pair_runs[0][1]], positions[pair_runs[-1][1]])
    ):
        first_a, first_b = pair_runs[0]
        last_a, last_b = pair_runs[-1]
        close_distance = (
            math.dist(positions[first_a], positions[last_a])
            + math.dist(positions[first_b], positions[last_b])
        )
        open_distance = (
            math.dist(positions[pair_runs[0][0]], positions[pair_runs[1][0]])
            + math.dist(positions[pair_runs[0][1]], positions[pair_runs[1][1]])
            + math.dist(positions[pair_runs[-2][0]], positions[pair_runs[-1][0]])
            + math.dist(positions[pair_runs[-2][1]], positions[pair_runs[-1][1]])
        ) / 2.0
        if close_distance <= open_distance * 1.5:
            indices.extend((last_a, first_a, last_b, last_b, first_a, first_b))
    return indices


def triangulate_paired_vertex_strip(positions: list) -> list:
    if len(positions) < 4 or len(positions) % 2 != 0:
        return []
    pair_count = len(positions) // 2
    indices = []
    for i in range(pair_count - 1):
        a = i * 2
        b = a + 1
        c = (i + 1) * 2
        d = c + 1
        indices.extend((a, c, b, b, c, d))
    if pair_count > 2:
        first_a, first_b = 0, 1
        last_a, last_b = (pair_count - 1) * 2, (pair_count - 1) * 2 + 1
        if not points_close(positions[first_a], positions[last_a]) and not points_close(positions[first_b], positions[last_b]):
            close_distance = (
                math.dist(positions[first_a], positions[last_a])
                + math.dist(positions[first_b], positions[last_b])
            )
            open_distance = (
                math.dist(positions[0], positions[2])
                + math.dist(positions[1], positions[3])
                + math.dist(positions[last_a - 2], positions[last_a])
                + math.dist(positions[last_b - 2], positions[last_b])
            ) / 2.0
            if close_distance <= open_distance * 1.5:
                indices.extend((last_a, first_a, last_b, last_b, first_a, first_b))
    return indices


def split_legacy_index_runs(words: list) -> list:
    runs = []
    current = []
    for value in words:
        if value == 0:
            if current:
                runs.append(current)
                current = []
        else:
            current.append(value - 1)
    if current:
        runs.append(current)
    return runs


def split_legacy_type1_contours(positions: list, outline: list) -> list:
    return split_coordinate_closed_contours(positions, outline)


def split_coordinate_closed_contours(positions: list, outline: list) -> list:
    contours = []
    current = []
    for index in outline:
        current.append(index)
        if len(current) > 2 and points_close(positions[current[0]], positions[current[-1]]):
            current.pop()
            contours.append(current)
            current = []
    if current:
        contours.append(current)
    return [contour for contour in contours if len(contour) >= 3]


def triangulate_planar_contours(positions: list, contours: list) -> list:
    contours = [remove_duplicate_outline_points(positions, contour) for contour in contours]
    contours = [contour for contour in contours if len(contour) >= 3]
    if not contours:
        return []
    if len(contours) == 1:
        return triangulate_planar_outline(positions, contours[0])

    all_points = [positions[index] for contour in contours for index in contour]
    normal = newell_normal(all_points)
    axis = max(range(3), key=lambda i: abs(normal[i]))
    projected = {
        index: project_point_2d(positions[index], axis)
        for contour in contours
        for index in contour
    }
    areas = [signed_area_2d([projected[index] for index in contour]) for contour in contours]
    outer_index = max(range(len(contours)), key=lambda i: abs(areas[i]))
    outer = list(contours[outer_index])
    outer_sign = 1.0 if areas[outer_index] >= 0.0 else -1.0
    holes = [list(contour) for i, contour in enumerate(contours) if i != outer_index]

    for hole in holes:
        hole_area = signed_area_2d([projected[index] for index in hole])
        if hole_area * outer_sign > 0.0:
            hole.reverse()
        bridged = bridge_hole_into_outline(outer, hole, projected)
        if bridged is None:
            return triangulate_outline_fan(outer)
        outer = bridged
    return triangulate_planar_outline(positions, outer)


def triangulate_planar_outline(positions: list, outline: list) -> list:
    if len(outline) < 3:
        return []
    outline = remove_duplicate_outline_points(positions, outline)
    if len(outline) < 3:
        return []

    projected = project_outline_points(positions, outline)
    area = signed_area_2d(projected)
    if abs(area) < 1e-9:
        return triangulate_outline_fan(outline)
    winding = 1.0 if area > 0.0 else -1.0

    remaining = list(range(len(outline)))
    triangles = []
    guard = 0
    while len(remaining) > 3 and guard < len(outline) * len(outline):
        guard += 1
        clipped = False
        for pos, current in enumerate(remaining):
            previous = remaining[pos - 1]
            following = remaining[(pos + 1) % len(remaining)]
            if not outline_corner_is_convex(projected[previous], projected[current], projected[following], winding):
                continue
            if any(
                point_in_or_on_triangle(projected[test], projected[previous], projected[current], projected[following], winding)
                for test in remaining
                if test not in (previous, current, following)
                and not point_matches_triangle_vertex(
                    projected[test],
                    projected[previous],
                    projected[current],
                    projected[following],
                )
            ):
                continue
            triangles.extend((outline[previous], outline[current], outline[following]))
            del remaining[pos]
            clipped = True
            break
        if not clipped:
            return triangulate_outline_fan(outline)

    if len(remaining) == 3:
        triangles.extend((outline[remaining[0]], outline[remaining[1]], outline[remaining[2]]))
    return triangles


def remove_duplicate_outline_points(positions: list, outline: list) -> list:
    cleaned = []
    for index in outline:
        if cleaned and points_close(positions[cleaned[-1]], positions[index]):
            continue
        cleaned.append(index)
    if len(cleaned) > 1 and points_close(positions[cleaned[0]], positions[cleaned[-1]]):
        cleaned.pop()
    return cleaned


def points_close(a: tuple, b: tuple) -> bool:
    return sum((a[i] - b[i]) * (a[i] - b[i]) for i in range(3)) < 1e-18


def project_outline_points(positions: list, outline: list) -> list:
    normal = newell_normal([positions[index] for index in outline])
    axis = max(range(3), key=lambda i: abs(normal[i]))
    return [project_point_2d(positions[index], axis) for index in outline]


def project_point_2d(point: tuple, axis: int) -> tuple:
    if axis == 0:
        return point[1], point[2]
    if axis == 1:
        return point[0], point[2]
    return point[0], point[1]


def newell_normal(points: list) -> tuple:
    nx = ny = nz = 0.0
    for i, current in enumerate(points):
        following = points[(i + 1) % len(points)]
        nx += (current[1] - following[1]) * (current[2] + following[2])
        ny += (current[2] - following[2]) * (current[0] + following[0])
        nz += (current[0] - following[0]) * (current[1] + following[1])
    return nx, ny, nz


def signed_area_2d(points: list) -> float:
    area = 0.0
    for i, current in enumerate(points):
        following = points[(i + 1) % len(points)]
        area += current[0] * following[1] - following[0] * current[1]
    return area * 0.5


def outline_corner_is_convex(a: tuple, b: tuple, c: tuple, winding: float) -> bool:
    return cross_2d(a, b, c) * winding > 1e-10


def point_in_or_on_triangle(point: tuple, a: tuple, b: tuple, c: tuple, winding: float) -> bool:
    ab = cross_2d(a, b, point) * winding
    bc = cross_2d(b, c, point) * winding
    ca = cross_2d(c, a, point) * winding
    return ab >= -1e-10 and bc >= -1e-10 and ca >= -1e-10


def point_matches_triangle_vertex(point: tuple, a: tuple, b: tuple, c: tuple) -> bool:
    return point_close_2d(point, a) or point_close_2d(point, b) or point_close_2d(point, c)


def point_close_2d(a: tuple, b: tuple) -> bool:
    return (a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1]) < 1e-18


def cross_2d(a: tuple, b: tuple, c: tuple) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def bridge_hole_into_outline(outer: list, hole: list, projected: dict) -> list | None:
    candidates = []
    for oi, outer_index in enumerate(outer):
        for hi, hole_index in enumerate(hole):
            dist = squared_distance_2d(projected[outer_index], projected[hole_index])
            candidates.append((dist, oi, hi))
    candidates.sort()
    for _dist, oi, hi in candidates:
        if bridge_segment_is_visible(outer, hole, oi, hi, projected):
            return (
                outer[:oi + 1]
                + hole[hi:]
                + hole[:hi + 1]
                + [outer[oi]]
                + outer[oi + 1:]
            )
    return None


def squared_distance_2d(a: tuple, b: tuple) -> float:
    return (a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1])


def bridge_segment_is_visible(outer: list, hole: list, oi: int, hi: int, projected: dict) -> bool:
    a_index = outer[oi]
    b_index = hole[hi]
    a = projected[a_index]
    b = projected[b_index]
    for contour, allowed in ((outer, {a_index}), (hole, {b_index})):
        for i, c_index in enumerate(contour):
            d_index = contour[(i + 1) % len(contour)]
            if c_index in allowed or d_index in allowed:
                continue
            if segments_intersect_2d(a, b, projected[c_index], projected[d_index]):
                return False
    return True


def segments_intersect_2d(a: tuple, b: tuple, c: tuple, d: tuple) -> bool:
    o1 = cross_2d(a, b, c)
    o2 = cross_2d(a, b, d)
    o3 = cross_2d(c, d, a)
    o4 = cross_2d(c, d, b)
    eps = 1e-10
    if (
        min(a[0], b[0]) - eps <= c[0] <= max(a[0], b[0]) + eps
        and min(a[1], b[1]) - eps <= c[1] <= max(a[1], b[1]) + eps
        and abs(o1) <= eps
    ):
        return True
    if (
        min(a[0], b[0]) - eps <= d[0] <= max(a[0], b[0]) + eps
        and min(a[1], b[1]) - eps <= d[1] <= max(a[1], b[1]) + eps
        and abs(o2) <= eps
    ):
        return True
    if (
        min(c[0], d[0]) - eps <= a[0] <= max(c[0], d[0]) + eps
        and min(c[1], d[1]) - eps <= a[1] <= max(c[1], d[1]) + eps
        and abs(o3) <= eps
    ):
        return True
    if (
        min(c[0], d[0]) - eps <= b[0] <= max(c[0], d[0]) + eps
        and min(c[1], d[1]) - eps <= b[1] <= max(c[1], d[1]) + eps
        and abs(o4) <= eps
    ):
        return True
    return (o1 > eps) != (o2 > eps) and (o3 > eps) != (o4 > eps)


def triangulate_outline_fan(outline: list) -> list:
    indices = []
    for i in range(1, len(outline) - 1):
        indices.extend((outline[0], outline[i], outline[i + 1]))
    return indices


def triangulate_two_legacy_rings(ring_count: int, cap_ends: bool) -> list:
    indices = []
    if cap_ends:
        indices.extend(triangulate_fan(ring_count, reverse=True))
        indices.extend(ring_count + value for value in triangulate_fan(ring_count))
    for i in range(ring_count):
        j = (i + 1) % ring_count
        indices.extend((i, j, ring_count + i, j, ring_count + j, ring_count + i))
    return indices


def orient_triangles_outward(indices: list, positions: list) -> list:
    center = (
        sum(point[0] for point in positions) / len(positions),
        sum(point[1] for point in positions) / len(positions),
        sum(point[2] for point in positions) / len(positions),
    )
    oriented = []
    for a, b, c in zip(indices[0::3], indices[1::3], indices[2::3]):
        pa, pb, pc = positions[a], positions[b], positions[c]
        normal = (
            (pb[1] - pa[1]) * (pc[2] - pa[2]) - (pb[2] - pa[2]) * (pc[1] - pa[1]),
            (pb[2] - pa[2]) * (pc[0] - pa[0]) - (pb[0] - pa[0]) * (pc[2] - pa[2]),
            (pb[0] - pa[0]) * (pc[1] - pa[1]) - (pb[1] - pa[1]) * (pc[0] - pa[0]),
        )
        centroid = (
            (pa[0] + pb[0] + pc[0]) / 3.0,
            (pa[1] + pb[1] + pc[1]) / 3.0,
            (pa[2] + pb[2] + pc[2]) / 3.0,
        )
        outward = (
            normal[0] * (centroid[0] - center[0])
            + normal[1] * (centroid[1] - center[1])
            + normal[2] * (centroid[2] - center[2])
        )
        if outward < 0.0:
            oriented.extend((a, c, b))
        else:
            oriented.extend((a, b, c))
    return oriented


def rectangle_indices_for_normal(positions: list, normal: tuple) -> list:
    base = [0, 2, 1, 1, 2, 3]
    if len(positions) != 4 or math.sqrt(sum(value * value for value in normal)) <= 1e-12:
        return base
    pa, pb, pc = positions[0], positions[2], positions[1]
    tri_normal = (
        (pb[1] - pa[1]) * (pc[2] - pa[2]) - (pb[2] - pa[2]) * (pc[1] - pa[1]),
        (pb[2] - pa[2]) * (pc[0] - pa[0]) - (pb[0] - pa[0]) * (pc[2] - pa[2]),
        (pb[0] - pa[0]) * (pc[1] - pa[1]) - (pb[1] - pa[1]) * (pc[0] - pa[0]),
    )
    if sum(tri_normal[i] * normal[i] for i in range(3)) < 0.0:
        return [0, 1, 2, 1, 3, 2]
    return base


def triangulate_legacy_box() -> list:
    return [
        0, 1, 2, 0, 2, 3,
        4, 6, 5, 4, 7, 6,
        0, 4, 1, 1, 4, 5,
        1, 5, 2, 2, 5, 6,
        2, 6, 3, 3, 6, 7,
        3, 7, 0, 0, 7, 4,
    ]


def triangulate_convex_point_cloud(positions: list) -> list:
    if len(positions) < 4:
        return triangulate_fan(len(positions))
    center = (
        sum(point[0] for point in positions) / len(positions),
        sum(point[1] for point in positions) / len(positions),
        sum(point[2] for point in positions) / len(positions),
    )
    max_extent = max(
        max(abs(point[i] - center[i]) for point in positions)
        for i in range(3)
    )
    epsilon = max(1e-7, max_extent * 1e-6)
    faces = []
    seen = set()
    count = len(positions)
    for a in range(count - 2):
        pa = positions[a]
        for b in range(a + 1, count - 1):
            pb = positions[b]
            ab = (pb[0] - pa[0], pb[1] - pa[1], pb[2] - pa[2])
            for c in range(b + 1, count):
                pc = positions[c]
                ac = (pc[0] - pa[0], pc[1] - pa[1], pc[2] - pa[2])
                normal = (
                    ab[1] * ac[2] - ab[2] * ac[1],
                    ab[2] * ac[0] - ab[0] * ac[2],
                    ab[0] * ac[1] - ab[1] * ac[0],
                )
                normal_length = math.sqrt(sum(value * value for value in normal))
                if normal_length <= epsilon:
                    continue
                positive = negative = False
                for p_index, point in enumerate(positions):
                    if p_index in (a, b, c):
                        continue
                    rel = (point[0] - pa[0], point[1] - pa[1], point[2] - pa[2])
                    signed = normal[0] * rel[0] + normal[1] * rel[1] + normal[2] * rel[2]
                    if signed > epsilon:
                        positive = True
                    elif signed < -epsilon:
                        negative = True
                    if positive and negative:
                        break
                if positive and negative:
                    continue
                key = tuple(sorted((a, b, c)))
                if key in seen:
                    continue
                seen.add(key)
                centroid = (
                    (pa[0] + pb[0] + pc[0]) / 3.0,
                    (pa[1] + pb[1] + pc[1]) / 3.0,
                    (pa[2] + pb[2] + pc[2]) / 3.0,
                )
                outward = (
                    normal[0] * (centroid[0] - center[0])
                    + normal[1] * (centroid[1] - center[1])
                    + normal[2] * (centroid[2] - center[2])
                )
                if outward < 0:
                    faces.extend((a, c, b))
                else:
                    faces.extend((a, b, c))
    if not faces:
        return triangulate_fan(len(positions))
    return faces


def triangulate_legacy_index_stream(words: list) -> list:
    runs = []
    current = []
    for value in words:
        if value == 0:
            if current:
                runs.append(current)
                current = []
        else:
            current.append(value - 1)
    if current:
        runs.append(current)

    indices = []
    for run in runs:
        if len(run) >= 3:
            root = run[0]
            for i in range(1, len(run) - 1):
                a, b, c = root, run[i], run[i + 1]
                if len({a, b, c}) == 3:
                    indices.extend((a, b, c))

    pair_runs = [run for run in runs if len(run) == 2]
    for i in range(len(pair_runs) - 1):
        a, b = pair_runs[i]
        c, d = pair_runs[i + 1]
        if len({a, b, c}) == 3:
            indices.extend((a, c, b))
        if len({b, c, d}) == 3:
            indices.extend((b, c, d))
    if len(pair_runs) > 2:
        a, b = pair_runs[-1]
        c, d = pair_runs[0]
        if len({a, b, c}) == 3:
            indices.extend((a, c, b))
        if len({b, c, d}) == 3:
            indices.extend((b, c, d))

    return indices


def validate_amig_non_geometry_chunks(data: bytes, chunks: list) -> None:
    for chunk in chunks[1:]:
        if chunk.chunk_id == b"ROBJ":
            continue
        if chunk.chunk_id == b"RMTR" and chunk.size == 2020:
            payload = data[chunk.data_offset:chunk.data_offset + chunk.size]
            read_c_name(payload[14:30])
            continue
        if chunk.chunk_id == b"RANI" and chunk.size == 1086:
            continue
        if chunk.chunk_id == b"RSET" and chunk.size == 6316:
            continue
        if chunk.chunk_id == b"RSCR" and chunk.size in (188, 220, 252):
            continue
        if chunk.chunk_id == b"RWIN" and chunk.size in (436, 1806, 2438):
            continue
        if chunk.chunk_id == b"RATT" and chunk.size == 2080:
            continue
        if chunk.chunk_id == b"RCOL" and chunk.size == 38:
            continue
        if chunk.chunk_id == b"RGRI" and chunk.size == 166:
            continue
        ids = ", ".join(c.chunk_id.decode("latin-1", "replace") for c in chunks)
        raise Real3DError(f"unsupported chunk layout: {ids}")


def parse_amig_material_colors(data: bytes, chunks: list) -> dict:
    colors_by_id = {}
    for chunk in chunks[1:]:
        if chunk.chunk_id != b"RCOL":
            continue
        payload = data[chunk.data_offset:chunk.data_offset + chunk.size]
        if chunk.size != 38:
            continue
        color_id = payload[37]
        red, green, blue = payload[30], payload[31], payload[32]
        colors_by_id[color_id] = (red / 255.0, green / 255.0, blue / 255.0)

    material_colors = {}
    for chunk in chunks[1:]:
        if chunk.chunk_id != b"RMTR" or chunk.size != 2020:
            continue
        payload = data[chunk.data_offset:chunk.data_offset + chunk.size]
        name = read_c_name(payload[14:30])
        if not name:
            continue
        palette_id = int.from_bytes(payload[54:56], "big")
        if palette_id in colors_by_id:
            material_colors[name] = colors_by_id[palette_id]
            continue
        rgb12 = int.from_bytes(payload[50:52], "big")
        if rgb12 == 0:
            continue
        red = ((rgb12 >> 8) & 0x0f) / 15.0
        green = ((rgb12 >> 4) & 0x0f) / 15.0
        blue = (rgb12 & 0x0f) / 15.0
        material_colors[name] = (red, green, blue)
    return material_colors


def parse_wind_robj_records(robj: bytes) -> list:
    meshes = []
    offset = 0
    while offset < len(robj):
        if offset + 4 <= len(robj) and robj[offset:offset + 4] in (
            b"VPHS", b"VSPI", b"VVEL", b"SMTH", b"SFOR", b"SCRE", b"SDEL",
            b"SIDE", b"SOBJ", b"SMAT", b"IFLG", b"IOCT",
        ):
            offset = parse_wind_standalone_property(robj, offset)
            continue
        if offset + 32 > len(robj):
            if all(value == 0 for value in robj[offset:]):
                break
            raise Real3DError(f"truncated WIND ROBJ record at 0x{offset:x}")
        name = read_c_name(robj[offset:offset + 16])
        obj_type = robj[offset + 16]
        subtype = robj[offset + 18]

        if robj[offset:offset + 4] in (b"VPHS", b"VSPI", b"VVEL", b"SMTH", b"SFOR", b"SCRE", b"SDEL", b"SIDE", b"SOBJ", b"SMAT", b"IFLG", b"IOCT"):
            offset = parse_wind_standalone_property(robj, offset)
        elif obj_type in (2, 3) and subtype in (1, 2):
            offset += 32
        elif obj_type in (8, 9, 10, 11) and subtype == 2:
            offset = parse_wind_container_record(robj, offset, name)
        elif obj_type in (8, 12) and subtype == 28:
            offset = parse_wind_container_record(robj, offset, name)
        elif subtype == 10 and obj_type in (4, 5):
            record_size, positions, indices, color = parse_wind_rectangle_record(robj, offset, name)
            meshes.append(Mesh(name, color, positions, indices, 0))
            offset += record_size
        elif subtype == 10 and obj_type == 12:
            offset = parse_wind_mapped_surface_record(robj, offset, name)
        elif subtype == 33 and obj_type in (4, 5):
            offset = parse_wind_point_light_record(robj, offset, name)
        elif subtype == 11 and obj_type in (4, 5, 13):
            new_offset, mesh = parse_wind_box_record(robj, offset, name)
            meshes.append(mesh)
            offset = new_offset
        elif subtype == 12 and obj_type == 13:
            new_offset, mesh = parse_wind_pyramid_record(robj, offset, name)
            meshes.append(mesh)
            offset = new_offset
        elif subtype == 15 and obj_type == 4:
            new_offset, mesh = parse_wind_prism_record(robj, offset, name)
            meshes.append(mesh)
            offset = new_offset
        elif subtype == 22 and obj_type in (4, 5, 13):
            new_offset, mesh = parse_wind_ellipsoid_record(robj, offset, name)
            meshes.append(mesh)
            offset = new_offset
        elif subtype == 22 and obj_type == 12:
            offset = parse_wind_mapped_ellipsoid_record(robj, offset, name)
        elif subtype == 18 and obj_type in (4, 5):
            new_offset, mesh = parse_wind_ellipse_record(robj, offset, name)
            meshes.append(mesh)
            offset = new_offset
        elif subtype == 19 and obj_type in (4, 5, 13):
            new_offset, mesh = parse_wind_cylinder_record(robj, offset, name)
            meshes.append(mesh)
            offset = new_offset
        elif subtype == 19 and obj_type == 12:
            new_offset, mesh = parse_wind_mapped_cylinder_record(robj, offset, name)
            meshes.append(mesh)
            offset = new_offset
        elif subtype == 20 and obj_type in (4, 5, 13):
            new_offset, mesh = parse_wind_cone_record(robj, offset, name)
            meshes.append(mesh)
            offset = new_offset
        elif subtype == 21 and obj_type in (4, 5, 13):
            new_offset, mesh = parse_wind_cutcone_record(robj, offset, name)
            meshes.append(mesh)
            offset = new_offset
        elif subtype in (23, 24) and obj_type in (4, 5, 13):
            new_offset, mesh = parse_wind_cylinder_record(robj, offset, name)
            meshes.append(mesh)
            offset = new_offset
        elif subtype == 35 and obj_type in (4, 5):
            offset = parse_wind_coordsys_record(robj, offset, name)
        elif subtype == 36 and obj_type in (4, 5):
            offset = parse_wind_viewpoint_record(robj, offset, name)
        elif subtype == 37 and obj_type == 5:
            offset = parse_wind_aimpoint_record(robj, offset, name)
        elif subtype == 38 and obj_type in (12, 13):
            offset = parse_wind_material_wrapper_record(robj, offset, name)
        elif subtype == 34:
            offset = parse_wind_line_record(robj, offset, name)
        elif subtype == 26:
            new_offset, mesh = parse_wind_grid_mesh_record(robj, offset, name)
            meshes.append(mesh)
            offset = new_offset
        elif subtype == 27 and obj_type == 13:
            offset = parse_wind_group_reference_record(robj, offset, name)
        else:
            raise Real3DError(
                f"unsupported WIND ROBJ record at 0x{offset:x}: type={obj_type} subtype={subtype}"
            )

    if not meshes:
        raise Real3DError("WIND ROBJ contains no supported meshes")
    return meshes


def parse_wind_container_record(robj: bytes, offset: int, name: str) -> int:
    pos = offset + 32
    while pos < len(robj):
        tag = robj[pos:pos + 4]
        if tag == b"FSIZ":
            require_finite_wind_doubles(robj, pos + 8, 1, name)
            pos += 16
        elif tag in (b"DDIV", b"DDIR"):
            require_finite_wind_doubles(robj, pos + 8, 3, name)
            pos += 32
        elif tag == b"MCOG":
            require_finite_wind_doubles(robj, pos + 8, 3, name)
            if robj[pos + 32:pos + 40] != b"\0" * 8:
                raise Real3DError(f"WIND container {name!r} MCOG tail is not zero")
            pos += 40
        elif tag == b"SPRV":
            if pos + 20 > len(robj):
                raise Real3DError(f"WIND container {name!r} has truncated SPRV")
            name_len = int.from_bytes(robj[pos + 8:pos + 12], "little")
            size = 20 + name_len
            if name_len == 0 or pos + size > len(robj):
                raise Real3DError(f"WIND container {name!r} has invalid SPRV name length")
            if robj[pos + 12 + name_len - 1] != 0 or robj[pos + size - 8:pos + size] != b"\0" * 8:
                raise Real3DError(f"WIND container {name!r} has invalid SPRV padding")
            pos += size
        elif tag == b"FFRI":
            require_finite_wind_doubles(robj, pos + 8, 1, name)
            pos += 16
        elif tag == b"VSPI":
            require_finite_wind_doubles(robj, pos + 8, 3, name)
            pos += 32
            if pos + 8 <= len(robj) and robj[pos:pos + 8] == b"\0" * 8 and looks_like_wind_record_header(robj, pos + 8):
                pos += 8
        elif tag == b"ICSM":
            if pos + 12 > len(robj):
                raise Real3DError(f"WIND container {name!r} has truncated ICSM")
            if pos + 20 <= len(robj) and robj[pos + 12:pos + 20] == b"\0" * 8:
                pos += 20
            else:
                pos += 12
        elif tag == b"VVEL":
            require_finite_wind_doubles(robj, pos + 8, 3, name)
            pos += 32
        elif tag == b"FMAS":
            require_finite_wind_doubles(robj, pos + 8, 1, name)
            if robj[pos + 16:pos + 24] != b"\0" * 8:
                raise Real3DError(f"WIND container {name!r} FMAS tail is not zero")
            pos += 24
        elif tag in (b"VTIM", b"VTIE", b"VTIS", b"VCRE"):
            require_finite_wind_doubles(robj, pos + 8, 3, name)
            pos += 32
        elif tag == b"ISKE":
            if pos + 12 > len(robj):
                raise Real3DError(f"WIND container {name!r} has truncated ISKE")
            key_a = int.from_bytes(robj[pos + 4:pos + 8], "little")
            key_b = int.from_bytes(robj[pos + 8:pos + 12], "little")
            if key_a > 65535 or key_b > 65535:
                raise Real3DError(f"WIND container {name!r} has invalid ISKE values")
            pos += 12
        elif tag in (b"IFLG", b"IOCT"):
            if pos + 12 > len(robj):
                raise Real3DError(f"WIND container {name!r} has truncated {tag.decode('ascii')}")
            value_a = int.from_bytes(robj[pos + 4:pos + 8], "little")
            value_b = int.from_bytes(robj[pos + 8:pos + 12], "little")
            if value_a > 0x100000 or value_b > 0x100000:
                raise Real3DError(f"WIND container {name!r} has invalid {tag.decode('ascii')} values")
            pos += 12
        elif tag in (b"SMTH", b"SFOR", b"SDEL", b"SCRE", b"SIDE", b"SOBJ"):
            pos = parse_wind_string_property(robj, pos, name)
        elif tag in (b"ITRF", b"ITRA"):
            if pos + 12 > len(robj):
                raise Real3DError(f"WIND container {name!r} has truncated {tag.decode('ascii')}")
            if is_known_wind_property_tag(robj[pos + 12:pos + 16]):
                pos += 12
            else:
                if pos + 20 > len(robj):
                    raise Real3DError(f"WIND container {name!r} has truncated {tag.decode('ascii')}")
                pos += 20
        elif tag == b"FORC":
            require_finite_wind_doubles(robj, pos + 8, 1, name)
            pos += 16
        else:
            break

    if pos == offset + 32:
        raise Real3DError(f"unsupported WIND container payload in {name!r} at 0x{offset:x}")
    return pos


def parse_wind_standalone_property(robj: bytes, offset: int) -> int:
    tag = robj[offset:offset + 4]
    if tag in (b"VSPI", b"VVEL"):
        require_finite_wind_doubles(robj, offset + 8, 3, tag.decode("ascii"))
        return offset + 32
    if tag == b"VPHS":
        require_finite_wind_doubles(robj, offset + 8, 4, "VPHS")
        return offset + 40
    if tag in (b"SMTH", b"SFOR", b"SCRE", b"SDEL", b"SIDE", b"SOBJ"):
        return parse_wind_string_property(robj, offset, tag.decode("ascii"))
    if tag == b"SMAT":
        return parse_wind_smat_property(robj, offset)
    if tag in (b"IFLG", b"IOCT"):
        if offset + 20 <= len(robj) and robj[offset + 4:offset + 20] == b"\0" * 16:
            return offset + 20
        if offset + 12 <= len(robj):
            value_a = int.from_bytes(robj[offset + 4:offset + 8], "little")
            value_b = int.from_bytes(robj[offset + 8:offset + 12], "little")
            if value_a <= 0x100000 and value_b <= 0x100000:
                return offset + 12
        raise Real3DError(f"invalid standalone WIND {tag.decode('ascii')} property at 0x{offset:x}")
    raise Real3DError(f"unsupported WIND property tag at 0x{offset:x}")


def is_known_wind_property_tag(tag: bytes) -> bool:
    return tag in (
        b"FSIZ", b"DDIV", b"DDIR", b"MCOG", b"SPRV", b"FFRI", b"VSPI", b"ICSM",
        b"VVEL", b"FMAS", b"VTIM", b"VTIE", b"VTIS", b"VCRE", b"SMTH", b"SFOR", b"SDEL", b"SCRE",
        b"SIDE", b"SOBJ", b"ITRF", b"ITRA", b"FORC", b"ISKE", b"IFLG", b"IOCT",
    )


def require_finite_wind_doubles(data: bytes, offset: int, count: int, name: str) -> None:
    if offset + count * 8 > len(data):
        raise Real3DError(f"truncated WIND numeric payload in {name!r}")
    for i in range(count):
        value = struct.unpack_from("<d", data, offset + i * 8)[0]
        if not math.isfinite(value):
            raise Real3DError(f"non-finite WIND numeric payload in {name!r}")


def parse_wind_string_property(robj: bytes, offset: int, name: str) -> int:
    if offset + 12 > len(robj):
        raise Real3DError(f"WIND container {name!r} has truncated string property")
    name_len = int.from_bytes(robj[offset + 8:offset + 12], "little")
    end = offset + 12 + name_len
    if name_len == 0 or end > len(robj):
        raise Real3DError(f"WIND container {name!r} has invalid string property length")
    if robj[end - 1] != 0:
        raise Real3DError(f"WIND container {name!r} string property is not NUL terminated")
    if end + 8 <= len(robj) and robj[end:end + 8] == b"\0" * 8:
        next_offset = end + 8
        if (
            next_offset == len(robj)
            or robj[next_offset:next_offset + 4] in (b"FSIZ", b"DDIV", b"DDIR", b"MCOG", b"SPRV", b"FFRI", b"VSPI", b"ICSM", b"VVEL", b"FMAS", b"VTIM", b"VCRE", b"SMTH", b"SFOR", b"SDEL", b"SCRE", b"SIDE", b"SOBJ", b"ITRF", b"ITRA", b"FORC")
            or (
                next_offset + 32 <= len(robj)
                and all((32 <= value < 127) or value == 0 for value in robj[next_offset:next_offset + 16])
                and robj[next_offset + 16] in range(2, 16)
                and robj[next_offset + 18] in range(1, 40)
                and robj[next_offset + 19] == 0
            )
        ):
            return next_offset
    return end


def parse_wind_smat_property(robj: bytes, offset: int) -> int:
    if offset + 20 > len(robj) or robj[offset:offset + 4] != b"SMAT":
        raise Real3DError(f"truncated WIND SMAT property at 0x{offset:x}")
    material_name_len = int.from_bytes(robj[offset + 8:offset + 12], "little")
    end = offset + 20 + material_name_len
    if material_name_len == 0 or end > len(robj):
        raise Real3DError(f"WIND SMAT property has invalid name length at 0x{offset:x}")
    material_name = robj[offset + 12:offset + 12 + material_name_len]
    if material_name[-1:] != b"\0":
        raise Real3DError(f"WIND SMAT property is not NUL terminated at 0x{offset:x}")
    if robj[end - 8:end] != b"\0" * 8:
        raise Real3DError(f"WIND SMAT property is not zero padded at 0x{offset:x}")
    return end


def parse_wind_surface_vectors(robj: bytes, offset: int, name: str) -> tuple:
    data_start = 44 if robj[offset + 40:offset + 44] == b"\0" * 4 else 42
    record_size = data_start + 96
    if offset + record_size > len(robj):
        raise Real3DError(f"WIND surface record overruns ROBJ at 0x{offset:x}")
    if robj[offset + 36:offset + data_start] != b"\0" * (data_start - 36):
        raise Real3DError(f"unexpected WIND surface bytes 36..41 in {name!r} at ROBJ 0x{offset:x}")

    points = []
    for i in range(3):
        x, y, z = struct.unpack_from("<ddd", robj, offset + data_start + i * 24)
        if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
            raise Real3DError(f"non-finite WIND surface point in {name!r}")
        points.append((x, y, z))

    normal = struct.unpack_from("<ddd", robj, offset + data_start + 72)
    if not all(math.isfinite(v) for v in normal):
        raise Real3DError(f"non-finite WIND surface normal in {name!r}")
    normal_length = math.sqrt(sum(v * v for v in normal))
    if not 0.0 <= normal_length < 1e6:
        raise Real3DError(f"unsupported WIND surface normal length in {name!r}: {normal_length}")
    return record_size, points, normal


def parse_wind_rectangle_record(robj: bytes, offset: int, name: str) -> tuple:
    record_size, points, _normal = parse_wind_surface_vectors(robj, offset, name)
    a, b, c = points
    d = tuple(b[i] + c[i] - a[i] for i in range(3))
    color = tuple(channel / 255.0 for channel in robj[offset + 33:offset + 36])
    if color == (0.0, 0.0, 0.0):
        color = (0.75, 0.75, 0.75)
    if offset + record_size + 2 <= len(robj) and robj[offset + record_size:offset + record_size + 2] == b"\0\0":
        next_offset = offset + record_size + 2
        if (
            next_offset == len(robj)
            or (
                next_offset + 32 <= len(robj)
                and all((32 <= value < 127) or value == 0 for value in robj[next_offset:next_offset + 16])
                and robj[next_offset + 16] in range(2, 16)
                and robj[next_offset + 18] in range(1, 40)
                and robj[next_offset + 19] == 0
            )
        ):
            record_size += 2
    return record_size, [a, b, c, d], [0, 2, 1, 1, 2, 3], color


def parse_wind_mapped_surface_record(robj: bytes, offset: int, name: str) -> int:
    surface_size, _points, _normal = parse_wind_surface_vectors(robj, offset, name)
    smat_offset = offset + surface_size
    if smat_offset + 20 > len(robj) or robj[smat_offset:smat_offset + 4] != b"SMAT":
        raise Real3DError(f"WIND mapped surface {name!r} missing SMAT footer at ROBJ 0x{offset:x}")
    material_name_len = int.from_bytes(robj[smat_offset + 8:smat_offset + 12], "little")
    record_size = surface_size + 20 + material_name_len
    if material_name_len == 0 or offset + record_size > len(robj):
        raise Real3DError(f"WIND mapped surface {name!r} has invalid SMAT name length")
    material_name = robj[smat_offset + 12:smat_offset + 12 + material_name_len]
    if material_name[-1:] != b"\0":
        raise Real3DError(f"WIND mapped surface {name!r} SMAT name is not NUL terminated")
    if robj[offset + record_size - 8:offset + record_size] != b"\0" * 8:
        raise Real3DError(f"WIND mapped surface {name!r} SMAT footer is not zero padded")
    return offset + record_size


def parse_wind_point_light_record(robj: bytes, offset: int, name: str) -> int:
    for data_start in (42, 44):
        record_size = data_start + 24
        if offset + record_size > len(robj):
            continue
        if robj[offset + 36:offset + data_start] != b"\0" * (data_start - 36):
            continue
        x, y, z = struct.unpack_from("<ddd", robj, offset + data_start)
        if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
            continue
        if math.sqrt(x * x + y * y + z * z) > 1e9:
            continue
        new_offset = offset + record_size
        if new_offset < len(robj) and robj[new_offset:new_offset + 2] == b"\0\0":
            padded_offset = new_offset + 2
            if padded_offset == len(robj) or looks_like_wind_record_header(robj, padded_offset):
                new_offset = padded_offset
        elif new_offset < len(robj) and robj[new_offset] == 0:
            padded_offset = new_offset + 1
            if padded_offset == len(robj) or looks_like_wind_record_header(robj, padded_offset):
                new_offset = padded_offset
        if new_offset == len(robj) or looks_like_wind_record_header(robj, new_offset):
            return new_offset
    raise Real3DError(f"unsupported WIND point light record {name!r} at 0x{offset:x}")


def parse_wind_box_record(robj: bytes, offset: int, name: str) -> tuple:
    record_size, points, normal = parse_wind_surface_vectors(robj, offset, name)
    a, b, c = points
    d = tuple(b[i] + c[i] - a[i] for i in range(3))
    e = tuple(a[i] + normal[i] for i in range(3))
    f = tuple(b[i] + normal[i] for i in range(3))
    g = tuple(c[i] + normal[i] for i in range(3))
    h = tuple(d[i] + normal[i] for i in range(3))
    positions = [a, b, c, d, e, f, g, h]
    indices = [
        0, 2, 1, 1, 2, 3,
        4, 5, 6, 5, 7, 6,
        0, 1, 4, 1, 5, 4,
        1, 3, 5, 3, 7, 5,
        3, 2, 7, 2, 6, 7,
        2, 0, 6, 0, 4, 6,
    ]
    return offset + record_size, Mesh(name, wind_record_color(robj, offset), positions, indices, 0)


def parse_wind_pyramid_record(robj: bytes, offset: int, name: str) -> tuple:
    record_size, points, apex = parse_wind_surface_vectors(robj, offset, name)
    a, b, c = points
    d = tuple(b[i] + c[i] - a[i] for i in range(3))
    positions = [a, b, c, d, apex]
    indices = [
        0, 2, 1, 1, 2, 3,
        0, 1, 4,
        1, 3, 4,
        3, 2, 4,
        2, 0, 4,
    ]
    return offset + record_size, Mesh(name, wind_record_color(robj, offset), positions, indices, 0)


def parse_wind_prism_record(robj: bytes, offset: int, name: str) -> tuple:
    record_size = 144
    if offset + record_size > len(robj):
        raise Real3DError(f"WIND prism record overruns ROBJ at 0x{offset:x}")
    if robj[offset + 36:offset + 42] != b"\0" * 6 or robj[offset + 44:offset + 48] != b"\0" * 4:
        raise Real3DError(f"unexpected WIND prism header bytes in {name!r} at ROBJ 0x{offset:x}")
    count = int.from_bytes(robj[offset + 42:offset + 44], "little")
    if count != 3:
        raise Real3DError(f"unsupported WIND prism vertex count {count} in {name!r}")
    values = [struct.unpack_from("<d", robj, offset + 48 + i * 8)[0] for i in range(12)]
    if not all(math.isfinite(v) for v in values):
        raise Real3DError(f"non-finite WIND prism value in {name!r}")
    extrusion = tuple(values[0:3])
    if math.sqrt(sum(v * v for v in extrusion)) <= 1e-12:
        raise Real3DError(f"zero WIND prism extrusion vector in {name!r}")
    base = [tuple(values[i:i + 3]) for i in range(3, 12, 3)]
    top = [tuple(point[i] + extrusion[i] for i in range(3)) for point in base]
    positions = base + top
    indices = [
        0, 1, 2,
        3, 5, 4,
        0, 3, 1, 1, 3, 4,
        1, 4, 2, 2, 4, 5,
        2, 5, 0, 0, 5, 3,
    ]
    return offset + record_size, Mesh(name, wind_record_color(robj, offset), positions, indices, 0)


def parse_wind_ellipsoid_payload(robj: bytes, offset: int, name: str, allow_trailing_angles: bool = False) -> tuple:
    data_start = 44 if robj[offset + 40:offset + 44] == b"\0" * 4 else 42
    record_size = data_start + 14 * 8
    if offset + record_size > len(robj):
        raise Real3DError(f"WIND ellipsoid record overruns ROBJ at 0x{offset:x}")
    values = [struct.unpack_from("<d", robj, offset + data_start + i * 8)[0] for i in range(14)]
    if not all(math.isfinite(v) for v in values):
        raise Real3DError(f"non-finite WIND ellipsoid value in {name!r}")
    if allow_trailing_angles:
        if abs(values[12]) > math.tau + 1e-3 or abs(values[13]) > math.tau + 1e-3:
            raise Real3DError(f"unsupported WIND ellipsoid trailing values in {name!r}")
    elif abs(values[12]) > 1e-9 or abs(values[13]) > 1e-9:
        raise Real3DError(f"unsupported WIND ellipsoid trailing values in {name!r}")
    center = tuple(values[0:3])
    axis_u = tuple(values[3:6])
    axis_v = tuple(values[6:9])
    axis_w = tuple(values[9:12])
    for axis in (axis_u, axis_v, axis_w):
        length = math.sqrt(sum(v * v for v in axis))
        if not 1e-9 < length < 1e6:
            raise Real3DError(f"invalid WIND ellipsoid axis length in {name!r}")
    return record_size, center, axis_u, axis_v, axis_w


def parse_wind_ellipsoid_record(robj: bytes, offset: int, name: str) -> tuple:
    record_size, center, axis_u, axis_v, axis_w = parse_wind_ellipsoid_payload(robj, offset, name)
    positions, indices = make_ellipsoid_mesh(center, axis_u, axis_v, axis_w)
    color = tuple(channel / 255.0 for channel in robj[offset + 33:offset + 36])
    if color == (0.0, 0.0, 0.0):
        color = (0.75, 0.75, 0.75)
    return offset + record_size, Mesh(name, color, positions, indices, 0)


def parse_wind_mapped_ellipsoid_record(robj: bytes, offset: int, name: str) -> int:
    record_size, _center, _axis_u, _axis_v, _axis_w = parse_wind_ellipsoid_payload(
        robj, offset, name, allow_trailing_angles=True
    )
    smat_offset = offset + record_size
    if smat_offset + 20 > len(robj) or robj[smat_offset:smat_offset + 4] != b"SMAT":
        raise Real3DError(f"WIND mapped ellipsoid {name!r} missing SMAT footer at ROBJ 0x{offset:x}")
    material_name_len = int.from_bytes(robj[smat_offset + 8:smat_offset + 12], "little")
    total_size = record_size + 20 + material_name_len
    if material_name_len == 0 or offset + total_size > len(robj):
        raise Real3DError(f"WIND mapped ellipsoid {name!r} has invalid SMAT name length")
    material_name = robj[smat_offset + 12:smat_offset + 12 + material_name_len]
    if material_name[-1:] != b"\0":
        raise Real3DError(f"WIND mapped ellipsoid {name!r} SMAT name is not NUL terminated")
    if robj[offset + total_size - 8:offset + total_size] != b"\0" * 8:
        if not (
            offset + total_size + 1 == len(robj)
            and robj[offset + total_size - 8:offset + total_size + 1] == b"\0" * 9
        ):
            raise Real3DError(f"WIND mapped ellipsoid {name!r} SMAT footer is not zero padded")
        total_size += 1
    elif offset + total_size + 1 == len(robj) and robj[offset + total_size] == 0:
        total_size += 1
    return offset + total_size


def parse_wind_parametric_values(robj: bytes, offset: int, name: str, count: int) -> tuple:
    data_start = 44 if robj[offset + 40:offset + 44] == b"\0" * 4 else 42
    record_size = data_start + count * 8
    if offset + record_size > len(robj):
        raise Real3DError(f"WIND parametric record overruns ROBJ at 0x{offset:x}")
    values = [struct.unpack_from("<d", robj, offset + data_start + i * 8)[0] for i in range(count)]
    if not all(math.isfinite(v) for v in values):
        raise Real3DError(f"non-finite WIND parametric value in {name!r}")
    return record_size, values


def parse_wind_ellipse_record(robj: bytes, offset: int, name: str) -> tuple:
    record_size, values = parse_wind_parametric_values(robj, offset, name, 15)
    if abs(values[12]) > 1e-9 or abs(values[13]) > 1e-9:
        raise Real3DError(f"unsupported WIND ellipse trailing values in {name!r}")
    if not 0.0 <= values[14] <= math.tau + 1e-3:
        raise Real3DError(f"unsupported WIND ellipse angular value in {name!r}")
    positions, indices = make_disk_mesh(tuple(values[0:3]), tuple(values[3:6]), tuple(values[6:9]), 0.0, 0.0)
    return offset + record_size, Mesh(name, wind_record_color(robj, offset), positions, indices, 0)


def parse_wind_cylinder_record(robj: bytes, offset: int, name: str) -> tuple:
    record_size, values = parse_wind_parametric_values(robj, offset, name, 32)
    start_angle, end_angle = validate_wind_angles(values[30], values[31], name)
    positions, indices = make_two_ring_mesh(
        tuple(values[12:15]),
        tuple(values[15:18]),
        tuple(values[18:21]),
        tuple(values[21:24]),
        tuple(values[24:27]),
        tuple(values[27:30]),
        start_angle,
        end_angle,
        cap_ends=True,
    )
    return offset + record_size, Mesh(name, wind_record_color(robj, offset), positions, indices, 0)


def parse_wind_mapped_cylinder_record(robj: bytes, offset: int, name: str) -> tuple:
    new_offset, mesh = parse_wind_cylinder_record(robj, offset, name)
    return parse_wind_smat_property(robj, new_offset), mesh


def parse_wind_material_wrapper_record(robj: bytes, offset: int, name: str) -> int:
    if robj[offset + 32:offset + 36] == b"SMAT":
        return parse_wind_smat_property(robj, offset + 32)
    if robj[offset + 32:offset + 36] == b"FKNO":
        if offset + 48 > len(robj):
            raise Real3DError(f"truncated WIND material wrapper FKNO in {name!r}")
        key_value = struct.unpack_from("<d", robj, offset + 40)[0]
        if not math.isfinite(key_value):
            raise Real3DError(f"non-finite WIND material wrapper FKNO in {name!r}")
        return parse_wind_smat_property(robj, offset + 48)
    raise Real3DError(f"WIND material wrapper {name!r} missing SMAT at ROBJ 0x{offset:x}")


def parse_wind_group_reference_record(robj: bytes, offset: int, name: str) -> int:
    if offset + 60 > len(robj):
        raise Real3DError(f"truncated WIND group reference {name!r} at ROBJ 0x{offset:x}")
    if robj[offset + 36:offset + 44] != b"\0" * 8:
        raise Real3DError(f"unexpected WIND group reference header bytes in {name!r}")
    entry_count = int.from_bytes(robj[offset + 44:offset + 46], "little")
    if entry_count == 8:
        if offset + 88 > len(robj):
            raise Real3DError(f"truncated WIND group reference offset table in {name!r}")
        table = [int.from_bytes(robj[offset + 56 + i * 4:offset + 60 + i * 4], "little") for i in range(8)]
        if any(table[i + 1] - table[i] != 8 for i in range(7)):
            raise Real3DError(f"invalid WIND group reference offset table in {name!r}")
        pos = offset + 88
    elif entry_count in (1, 2):
        if robj[offset + 60:offset + 64] == b"VPHS":
            pos = offset + 60
        elif offset + 68 <= len(robj) and robj[offset + 64:offset + 68] == b"VPHS":
            pos = offset + 64
        else:
            raise Real3DError(f"WIND group reference {name!r} missing VPHS")
    else:
        raise Real3DError(f"unsupported WIND group reference count {entry_count} in {name!r}")

    start = pos
    while pos < len(robj):
        tag = robj[pos:pos + 4]
        if tag in (b"SOBJ", b"SIDE"):
            pos = parse_wind_string_property(robj, pos, name)
        elif tag == b"VPHS":
            if pos + 32 > len(robj):
                raise Real3DError(f"truncated WIND group reference VPHS in {name!r}")
            require_finite_wind_doubles(robj, pos + 8, 3, name)
            pos += 32
        else:
            break
    if pos == start:
        raise Real3DError(f"unsupported WIND group reference payload in {name!r}")
    if pos != len(robj) and not looks_like_wind_record_header(robj, pos):
        raise Real3DError(f"WIND group reference {name!r} ended at non-record byte 0x{pos:x}")
    return pos


def parse_wind_aimpoint_record(robj: bytes, offset: int, name: str) -> int:
    for data_start in (42, 44):
        record_size = data_start + 24
        if offset + record_size > len(robj):
            continue
        if robj[offset + 36:offset + data_start] != b"\0" * (data_start - 36):
            continue
        x, y, z = struct.unpack_from("<ddd", robj, offset + data_start)
        if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
            continue
        if math.sqrt(x * x + y * y + z * z) > 1e9:
            continue
        new_offset = offset + record_size
        if new_offset == len(robj) or looks_like_wind_record_header(robj, new_offset):
            return new_offset
    raise Real3DError(f"unsupported WIND aimpoint record {name!r} at 0x{offset:x}")


def parse_wind_viewpoint_record(robj: bytes, offset: int, name: str) -> int:
    record_size, values = parse_wind_parametric_values(robj, offset, name, 12)
    for i in range(0, 12, 3):
        vector = values[i:i + 3]
        if math.sqrt(sum(v * v for v in vector)) > 1e9:
            raise Real3DError(f"unsupported WIND viewpoint vector in {name!r}")
    return offset + record_size


def parse_wind_cone_record(robj: bytes, offset: int, name: str) -> tuple:
    record_size, values = parse_wind_parametric_values(robj, offset, name, 23)
    start_angle, end_angle = validate_wind_angles(values[21], values[22], name)
    positions, indices = make_cone_mesh(
        tuple(values[0:3]),
        tuple(values[12:15]),
        tuple(values[15:18]),
        tuple(values[18:21]),
        start_angle,
        end_angle,
    )
    return offset + record_size, Mesh(name, wind_record_color(robj, offset), positions, indices, 0)


def parse_wind_cutcone_record(robj: bytes, offset: int, name: str) -> tuple:
    record_size, values = parse_wind_parametric_values(robj, offset, name, 32)
    start_angle, end_angle = validate_wind_angles(values[30], values[31], name)
    positions, indices = make_two_ring_mesh(
        tuple(values[12:15]),
        tuple(values[15:18]),
        tuple(values[18:21]),
        tuple(values[21:24]),
        tuple(values[24:27]),
        tuple(values[27:30]),
        start_angle,
        end_angle,
        cap_ends=True,
    )
    return offset + record_size, Mesh(name, wind_record_color(robj, offset), positions, indices, 0)


def parse_wind_coordsys_record(robj: bytes, offset: int, name: str) -> int:
    record_size, values = parse_wind_parametric_values(robj, offset, name, 12)
    for i in range(0, 12, 3):
        vector = values[i:i + 3]
        if math.sqrt(sum(v * v for v in vector)) > 1e6:
            raise Real3DError(f"unsupported WIND coordsys vector in {name!r}")
    return offset + record_size


def validate_wind_angles(start_angle: float, end_angle: float, name: str) -> tuple:
    limit = math.tau + 1e-3
    if abs(start_angle) > limit or abs(end_angle) > limit:
        raise Real3DError(f"unsupported WIND angular span in {name!r}")
    if abs(end_angle) <= 1e-9:
        return 0.0, math.tau
    if end_angle <= start_angle:
        raise Real3DError(f"unsupported WIND angular span in {name!r}")
    return start_angle, end_angle


def wind_record_color(robj: bytes, offset: int) -> tuple:
    color = tuple(channel / 255.0 for channel in robj[offset + 33:offset + 36])
    if color == (0.0, 0.0, 0.0):
        color = (0.75, 0.75, 0.75)
    return color


def point_from_axes(center: tuple, axis_u: tuple, axis_v: tuple, theta: float) -> tuple:
    cu = math.cos(theta)
    sv = math.sin(theta)
    return tuple(center[i] + axis_u[i] * cu + axis_v[i] * sv for i in range(3))


def make_angle_steps(start_angle: float, end_angle: float) -> tuple:
    full = abs((end_angle - start_angle) - math.tau) <= 1e-6
    segments = 32 if full else max(8, int(math.ceil(32 * (end_angle - start_angle) / math.tau)))
    count = segments if full else segments + 1
    angles = [start_angle + (end_angle - start_angle) * i / segments for i in range(count)]
    return angles, full


def make_disk_mesh(center: tuple, axis_u: tuple, axis_v: tuple, start_angle: float, end_angle: float) -> tuple:
    angles, full = make_angle_steps(*validate_wind_angles(start_angle, end_angle, "ellipse"))
    positions = [center]
    positions.extend(point_from_axes(center, axis_u, axis_v, theta) for theta in angles)
    indices = []
    ring_count = len(angles)
    for i in range(ring_count if full else ring_count - 1):
        a = 1 + i
        b = 1 + ((i + 1) % ring_count)
        indices.extend((0, a, b))
    return positions, indices


def make_two_ring_mesh(
    center_a: tuple,
    axis_au: tuple,
    axis_av: tuple,
    center_b: tuple,
    axis_bu: tuple,
    axis_bv: tuple,
    start_angle: float,
    end_angle: float,
    cap_ends: bool,
) -> tuple:
    angles, full = make_angle_steps(start_angle, end_angle)
    positions = []
    positions.extend(point_from_axes(center_a, axis_au, axis_av, theta) for theta in angles)
    positions.extend(point_from_axes(center_b, axis_bu, axis_bv, theta) for theta in angles)
    ring_count = len(angles)
    indices = []
    side_segments = ring_count if full else ring_count - 1
    for i in range(side_segments):
        a = i
        b = (i + 1) % ring_count
        c = ring_count + ((i + 1) % ring_count)
        d = ring_count + i
        indices.extend((a, d, c, a, c, b))

    if cap_ends:
        center_a_index = len(positions)
        positions.append(center_a)
        center_b_index = len(positions)
        positions.append(center_b)
        for i in range(side_segments):
            a = i
            b = (i + 1) % ring_count
            c = ring_count + i
            d = ring_count + ((i + 1) % ring_count)
            indices.extend((center_a_index, b, a))
            indices.extend((center_b_index, c, d))
        if not full:
            indices.extend((0, ring_count, center_b_index, 0, center_b_index, center_a_index))
            last = ring_count - 1
            indices.extend((last, center_a_index, center_b_index, last, center_b_index, ring_count + last))

    return positions, indices


def make_cone_mesh(
    apex: tuple,
    base_center: tuple,
    base_axis_u: tuple,
    base_axis_v: tuple,
    start_angle: float,
    end_angle: float,
) -> tuple:
    angles, full = make_angle_steps(start_angle, end_angle)
    positions = [apex]
    positions.extend(point_from_axes(base_center, base_axis_u, base_axis_v, theta) for theta in angles)
    base_center_index = len(positions)
    positions.append(base_center)
    indices = []
    ring_count = len(angles)
    side_segments = ring_count if full else ring_count - 1
    for i in range(side_segments):
        a = 1 + i
        b = 1 + ((i + 1) % ring_count)
        indices.extend((0, a, b))
        indices.extend((base_center_index, b, a))
    if not full:
        first = 1
        last = ring_count
        indices.extend((0, base_center_index, first, 0, last, base_center_index))
    return positions, indices


def make_ellipsoid_mesh(center: tuple, axis_u: tuple, axis_v: tuple, axis_w: tuple) -> tuple:
    slices = 24
    stacks = 12
    positions = []
    for stack in range(stacks + 1):
        phi = -math.pi / 2 + math.pi * stack / stacks
        cos_phi = math.cos(phi)
        sin_phi = math.sin(phi)
        for slc in range(slices):
            theta = 2 * math.pi * slc / slices
            local_u = cos_phi * math.cos(theta)
            local_v = cos_phi * math.sin(theta)
            local_w = sin_phi
            positions.append(tuple(
                center[i] + axis_u[i] * local_u + axis_v[i] * local_v + axis_w[i] * local_w
                for i in range(3)
            ))

    indices = []
    for stack in range(stacks):
        for slc in range(slices):
            a = stack * slices + slc
            b = stack * slices + (slc + 1) % slices
            c = (stack + 1) * slices + (slc + 1) % slices
            d = (stack + 1) * slices + slc
            indices.extend((a, d, c, a, c, b))
    return positions, indices


def parse_wind_line_record(robj: bytes, offset: int, name: str) -> int:
    variants = []
    if offset + 56 <= len(robj):
        variants.append((56, int.from_bytes(robj[offset + 44:offset + 46], "little")))
    if offset + 52 <= len(robj):
        variants.append((52, int.from_bytes(robj[offset + 42:offset + 44], "little")))

    for vertex_start, count in variants:
        size = vertex_start + count * 24
        if count < 2 or offset + size > len(robj):
            continue
        if vertex_start == 56:
            line_tail = robj[offset + 52:offset + 56]
            has_dimension_tail = (
                int.from_bytes(line_tail[0:2], "little") == 3
                and int.from_bytes(line_tail[2:4], "little") <= 0x0201
            )
            if (
                robj[offset + 36:offset + 44] != b"\0" * 8
                or int.from_bytes(robj[offset + 46:offset + 48], "little") > 0x100
                or (line_tail != b"\0" * 4 and not has_dimension_tail)
            ):
                continue
        elif vertex_start == 52:
            line_tail = robj[offset + 48:offset + 52]
            has_dimension_tail = (
                int.from_bytes(line_tail[0:2], "little") == 3
                and int.from_bytes(line_tail[2:4], "little") <= 0x0201
            )
            if (
                robj[offset + 36:offset + 42] != b"\0" * 6
                or robj[offset + 44:offset + 48] != b"\0" * 4
                or (line_tail != b"\0" * 4 and not has_dimension_tail)
            ):
                continue
        good = True
        for i in range(count):
            x, y, z = struct.unpack_from("<ddd", robj, offset + vertex_start + i * 24)
            if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
                good = False
                break
        if not good:
            continue
        new_offset = offset + size
        if new_offset < len(robj) and robj[new_offset] == 0:
            padded_offset = new_offset + 1
            if padded_offset == len(robj) or looks_like_wind_record_header(robj, padded_offset):
                new_offset = padded_offset
        return new_offset

    raise Real3DError(f"unsupported WIND line record {name!r} at 0x{offset:x}")


def looks_like_wind_record_header(robj: bytes, offset: int) -> bool:
    if offset + 32 > len(robj):
        return False
    if not all((32 <= value < 127) or value == 0 for value in robj[offset:offset + 16]):
        return False
    return robj[offset + 16] in range(2, 16) and robj[offset + 18] in range(1, 40) and robj[offset + 19] == 0


def parse_wind_grid_mesh_record(robj: bytes, offset: int, name: str) -> tuple:
    variants = [
        (56, offset + 44, offset + 46),
        (54, offset + 42, offset + 44),
    ]
    errors = []
    for vertex_start, rows_off, cols_off in variants:
        rows = int.from_bytes(robj[rows_off:rows_off + 2], "little")
        cols = int.from_bytes(robj[cols_off:cols_off + 2], "little")
        vertex_count = rows * cols
        size = vertex_start + vertex_count * 24
        if rows < 2 or cols < 2 or vertex_count > 65535 or offset + size > len(robj):
            errors.append((vertex_start, rows, cols, "invalid dimensions"))
            continue
        positions = []
        good = True
        for i in range(vertex_count):
            x, y, z = struct.unpack_from("<ddd", robj, offset + vertex_start + i * 24)
            if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
                good = False
                break
            positions.append((x, y, z))
        if not good:
            errors.append((vertex_start, rows, cols, "non-finite vertex"))
            continue

        indices = []
        for r in range(rows - 1):
            for c in range(cols - 1):
                a = r * cols + c
                b = (r + 1) * cols + c
                cidx = (r + 1) * cols + c + 1
                d = r * cols + c + 1
                indices.extend((a, b, cidx, a, cidx, d))

        raw_color = robj[offset + 33:offset + 36]
        color = tuple(channel / 255.0 for channel in raw_color)
        if color == (0.0, 0.0, 0.0):
            color = (0.75, 0.75, 0.75)
        return offset + size, Mesh(name, color, positions, indices, 0)

    raise Real3DError(f"unsupported WIND grid mesh {name!r} at 0x{offset:x}: {errors}")


def read_be_u32(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset:offset + 4], "big")


def parse_realinfo_poly_file(data: bytes) -> list:
    if len(data) < 36 or data[:4] != b"FORM" or data[8:12] != b"REAL":
        raise Real3DError("not a REAL/INFO polygon file")
    form_size = read_be_u32(data, 4)
    if form_size not in (len(data) - 8, len(data) - 7):
        raise Real3DError("REAL/INFO FORM size does not match file length")

    top_end = min(8 + form_size, len(data))
    if data[12:16] != b"INFO" or read_be_u32(data, 16) != 8:
        raise Real3DError("REAL/INFO file missing top INFO chunk")
    object_name = read_c_name(data[20:28])
    offset = 28

    if data[offset:offset + 4] != b"FORM" or read_be_u32(data, offset + 4) != 32 or data[offset + 8:offset + 12] != b"OBJT":
        raise Real3DError("REAL/INFO file missing OBJT form")
    objt_inner = offset + 12
    objt_end = offset + 40
    if data[objt_inner:objt_inner + 4] != b"FORM" or data[objt_inner + 8:objt_inner + 12] != b"ORNT":
        raise Real3DError("REAL/INFO file missing ORNT form")
    objt_inner += 8 + read_be_u32(data, objt_inner + 4)
    if data[objt_inner:objt_inner + 4] != b"EXTE" or read_be_u32(data, objt_inner + 4) != 7:
        raise Real3DError("REAL/INFO file missing OBJT EXTE chunk")
    objt_inner += 16
    if objt_inner != objt_end:
        raise Real3DError("OBJT size mismatch")
    offset = objt_end

    if data[offset:offset + 4] != b"FORM" or data[offset + 8:offset + 12] != b"APPR":
        raise Real3DError("REAL/INFO file missing APPR form")
    appr_end = min(offset + 8 + read_be_u32(data, offset + 4), top_end)
    offset += 12
    if data[offset:offset + 4] != b"FORM" or data[offset + 8:offset + 12] != b"POLY":
        raise Real3DError("REAL/INFO file missing POLY form")
    poly_end = min(offset + 8 + read_be_u32(data, offset + 4), appr_end)
    offset += 12

    if data[offset:offset + 4] != b"INFO" or read_be_u32(data, offset + 4) != 1:
        raise Real3DError("POLY missing one-byte INFO chunk")
    offset += 10

    offset = require_form_child(data, offset, b"DETA")
    if data[offset:offset + 4] != b"VERT":
        raise Real3DError("POLY missing VERT chunk")
    vert_size = read_be_u32(data, offset + 4)
    if vert_size == 0 or vert_size % 12 != 0:
        raise Real3DError("VERT chunk size is not a non-zero multiple of 12")
    vertex_count = vert_size // 12
    vertex_data = offset + 8
    vertices = []
    for i in range(vertex_count):
        x, y, z = struct.unpack_from("<iii", data, vertex_data + i * 12)
        vertices.append((float(x), float(y), float(z)))
    offset += 8 + vert_size + (vert_size & 1)

    offset = require_form_child(data, offset, b"TXMS")

    face_indices = []
    source_face_count = 0
    offset, tris, tris_source_count = parse_realinfo_face_form(data, offset, b"TRIS", vertex_count)
    face_indices.extend(tris)
    source_face_count += tris_source_count
    if offset < poly_end and data[offset:offset + 4] == b"FORM" and data[offset + 8:offset + 12] == b"QUAD":
        offset, quads, quad_source_count = parse_realinfo_face_form(data, offset, b"QUAD", vertex_count)
        face_indices.extend(quads)
        source_face_count += quad_source_count

    if data[offset:offset + 4] != b"ATTR":
        raise Real3DError("POLY missing ATTR chunk")
    attr_size = read_be_u32(data, offset + 4)
    if attr_size != source_face_count * 9:
        raise Real3DError("ATTR size does not match converted face count")
    offset += 8 + attr_size + (attr_size & 1)
    if offset not in (poly_end, poly_end + 1):
        raise Real3DError("unaccounted bytes at end of POLY form")

    if not face_indices:
        raise Real3DError("REAL/INFO polygon file contains no faces")
    return [Mesh(object_name or "REAL_INFO_POLY", (0.72, 0.72, 0.72), vertices, face_indices, 0)]


def require_form_child(data: bytes, offset: int, form_type: bytes) -> int:
    if data[offset:offset + 4] != b"FORM" or data[offset + 8:offset + 12] != form_type:
        raise Real3DError(f"missing FORM {form_type.decode('ascii')}")
    size = read_be_u32(data, offset + 4)
    end = offset + 8 + size
    if end > len(data):
        raise Real3DError(f"FORM {form_type.decode('ascii')} overruns file")
    return end + (size & 1)


def parse_realinfo_face_form(data: bytes, offset: int, form_type: bytes, vertex_count: int) -> tuple:
    if data[offset:offset + 4] != b"FORM" or data[offset + 8:offset + 12] != form_type:
        raise Real3DError(f"missing FORM {form_type.decode('ascii')}")
    form_end = offset + 8 + read_be_u32(data, offset + 4)
    inner = offset + 12
    if data[inner:inner + 4] != b"FACE":
        raise Real3DError(f"FORM {form_type.decode('ascii')} missing FACE chunk")
    face_size = read_be_u32(data, inner + 4)
    record_words = 4 if form_type == b"TRIS" else 5
    record_size = record_words * 2
    if face_size == 0 or face_size % record_size != 0:
        raise Real3DError(f"FACE size is invalid in {form_type.decode('ascii')}")
    face_data = inner + 8
    face_end = face_data + face_size
    if face_end > form_end:
        raise Real3DError(f"FACE overruns {form_type.decode('ascii')}")

    indices = []
    entries = face_size // record_size
    for i in range(entries):
        values = struct.unpack_from("<" + "H" * record_words, data, face_data + i * record_size)
        source_indices = values[1:]
        if max(source_indices) >= vertex_count:
            raise Real3DError(f"{form_type.decode('ascii')} face index out of range at face {i}")
        if form_type == b"TRIS":
            indices.extend(source_indices)
        else:
            a, b, c, d = source_indices
            indices.extend((a, b, c, a, c, d))

    maps_offset = face_end + (face_size & 1)
    if data[maps_offset:maps_offset + 4] != b"MAPS":
        raise Real3DError(f"FORM {form_type.decode('ascii')} missing MAPS chunk")
    maps_size = read_be_u32(data, maps_offset + 4)
    maps_end = maps_offset + 8 + maps_size + (maps_size & 1)
    if maps_end != form_end:
        raise Real3DError(f"unaccounted bytes in FORM {form_type.decode('ascii')}")
    return form_end + (read_be_u32(data, offset + 4) & 1), indices, entries


def align4(blob: bytearray) -> None:
    while len(blob) % 4:
        blob.append(0)


def make_glb(meshes: list) -> bytes:
    binary = bytearray()
    buffer_views = []
    accessors = []
    primitives = []
    materials = []

    for mesh in meshes:
        material_index = len(materials)
        materials.append({
            "name": mesh.name or f"material_{material_index}",
            "pbrMetallicRoughness": {
                "baseColorFactor": [mesh.color[0], mesh.color[1], mesh.color[2], 1.0],
                "metallicFactor": 0.0,
                "roughnessFactor": 0.85,
            },
        })

        align4(binary)
        pos_offset = len(binary)
        for x, y, z in mesh.positions:
            binary.extend(struct.pack("<fff", float(x), float(y), float(z)))
        pos_length = len(binary) - pos_offset
        buffer_views.append({"buffer": 0, "byteOffset": pos_offset, "byteLength": pos_length, "target": 34962})
        min_pos = [min(v[i] for v in mesh.positions) for i in range(3)]
        max_pos = [max(v[i] for v in mesh.positions) for i in range(3)]
        pos_accessor = len(accessors)
        accessors.append({
            "bufferView": len(buffer_views) - 1,
            "byteOffset": 0,
            "componentType": 5126,
            "count": len(mesh.positions),
            "type": "VEC3",
            "min": min_pos,
            "max": max_pos,
        })

        align4(binary)
        idx_offset = len(binary)
        for index in mesh.indices:
            binary.extend(struct.pack("<I", index))
        idx_length = len(binary) - idx_offset
        buffer_views.append({"buffer": 0, "byteOffset": idx_offset, "byteLength": idx_length, "target": 34963})
        idx_accessor = len(accessors)
        accessors.append({
            "bufferView": len(buffer_views) - 1,
            "byteOffset": 0,
            "componentType": 5125,
            "count": len(mesh.indices),
            "type": "SCALAR",
        })

        primitives.append({
            "attributes": {"POSITION": pos_accessor},
            "indices": idx_accessor,
            "material": material_index,
            "mode": 4,
        })

    align4(binary)
    gltf = {
        "asset": {"version": "2.0", "generator": "real3D.py"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0, "name": "Real 3D model"}],
        "meshes": [{"primitives": primitives}],
        "materials": materials,
        "buffers": [{"byteLength": len(binary)}],
        "bufferViews": buffer_views,
        "accessors": accessors,
    }

    json_blob = json.dumps(gltf, separators=(",", ":")).encode("utf-8")
    while len(json_blob) % 4:
        json_blob += b" "

    total_length = 12 + 8 + len(json_blob) + 8 + len(binary)
    return (
        b"glTF"
        + struct.pack("<II", 2, total_length)
        + struct.pack("<I4s", len(json_blob), b"JSON")
        + json_blob
        + struct.pack("<I4s", len(binary), b"BIN\0")
        + bytes(binary)
    )


def convert(input_file: Path, output_file: Path) -> None:
    meshes = parse_real3d_polygon_file(input_file)
    glb = make_glb(meshes)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=output_file.name + ".", suffix=".tmp", dir=str(output_file.parent))
    try:
        with os.fdopen(fd, "wb") as tmp:
            tmp.write(glb)
        os.chmod(tmp_name, 0o664)
        os.replace(tmp_name, output_file)
    except Exception:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


def main(argv: list) -> int:
    if len(argv) != 3:
        print("usage: real3D.py <inputFile> <outputFile>", file=sys.stderr)
        return 2
    output = Path(argv[2])
    try:
        if output.exists():
            output.unlink()
        convert(Path(argv[1]), output)
        return 0
    except Exception as exc:
        try:
            if output.exists():
                output.unlink()
        except FileNotFoundError:
            pass
        print(f"real3D.py: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

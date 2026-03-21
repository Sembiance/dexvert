#!/usr/bin/env python3
# Vibe coded by Claude
"""
SIMIS Shape (.s) parser and GLB converter.

Microsoft Train Simulator (MSTS) / Open Rails shape file format.
Binary variant with JINX0s1b header. Contains indexed triangle lists
with global vertex position, normal, and UV arrays.

Format reference: MSTS shape file format spec + Open Rails ShapeFile.cs
"""

import struct
import sys
import os
import math

from glb import GLBBuilder


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

class SIMISMesh:
    def __init__(self):
        self.positions = []
        self.normals = []
        self.triangles = []
        self.uvs = []


class SIMISModel:
    def __init__(self):
        self.meshes = []
        self.name = ""


# ---------------------------------------------------------------------------
# Binary block reader
# ---------------------------------------------------------------------------

JINX_MAGIC = b"JINX0s1b______\r\n"

# Token IDs (u16) for shape-relevant blocks
TK_SHAPE = 0x0047
TK_SHAPE_HEADER = 0x0046
TK_POINTS = 0x0007
TK_POINT = 0x0002
TK_UV_POINTS = 0x0009
TK_UV_POINT = 0x0008
TK_NORMALS = 0x0005
TK_VECTOR = 0x0003
TK_MATRICES = 0x0042
TK_MATRIX = 0x0041
TK_IMAGES = 0x000E
TK_IMAGE = 0x000D
TK_TEXTURES = 0x0010
TK_TEXTURE = 0x000F
TK_LOD_CONTROLS = 0x001F
TK_LOD_CONTROL = 0x0020
TK_DIST_LEVELS = 0x0024
TK_DIST_LEVEL = 0x0025
TK_DIST_LEVEL_HDR = 0x0022
TK_DLEVEL_SEL = 0x0023
TK_HIERARCHY = 0x0043
TK_SUB_OBJECTS = 0x0026
TK_SUB_OBJECT = 0x0027
TK_SUB_OBJECT_HDR = 0x0028
TK_VERTICES = 0x0032
TK_VERTEX = 0x0030
TK_VERTEX_UVS = 0x0031
TK_VERTEX_SETS = 0x0034
TK_VERTEX_SET = 0x0033
TK_PRIMITIVES = 0x0035
TK_PRIM_STATE_IDX = 0x0038
TK_INDEXED_TRILIST = 0x003C
TK_VERTEX_IDXS = 0x003F
TK_NORMAL_IDXS = 0x0006
TK_FLAGS = 0x0040
TK_PRIM_STATES = 0x0037
TK_PRIM_STATE = 0x0036
TK_TEX_IDXS = 0x003D
TK_GEOMETRY_INFO = 0x0029
TK_VOLUMES = 0x0044
TK_SHADER_NAMES = 0x0048
TK_TEX_FILTER_NAMES = 0x004A
TK_LIGHT_MATERIALS = 0x0012
TK_LIGHT_MODEL_CFGS = 0x004F
TK_VTX_STATES = 0x002F
TK_COLOURS = 0x000B
TK_SORT_VECTORS = 0x004C


class Block:
    """A parsed binary block from the JINX stream."""
    __slots__ = ('token_id', 'token_type', 'name', 'data', 'offset', 'end')

    def __init__(self, token_id, token_type, name, data, offset, end):
        self.token_id = token_id
        self.token_type = token_type
        self.name = name
        self.data = data
        self.offset = offset  # start of content data
        self.end = end  # end of this block


def read_block(data, pos):
    """Read a single block header and return a Block object."""
    if pos + 8 > len(data):
        return None
    token_id, token_type = struct.unpack_from('<HH', data, pos)
    content_len = struct.unpack_from('<I', data, pos + 4)[0]
    content_start = pos + 8
    block_end = content_start + content_len

    # Read optional name
    name = ""
    off = content_start
    if off < block_end:
        name_len = data[off]
        off += 1
        if name_len > 0 and off + name_len * 2 <= block_end:
            name = data[off:off + name_len * 2].decode('utf-16-le', errors='replace')
            off += name_len * 2

    return Block(token_id, token_type, name, data, off, block_end)


def iter_children(block, skip=0):
    """Iterate over child blocks within a parent block.

    skip: number of bytes to skip at start of content (e.g., 4 for array count u32).
    """
    pos = block.offset + skip
    while pos + 8 <= block.end:
        child = read_block(block.data, pos)
        if child is None:
            break
        yield child
        pos = child.end


def read_uint(block):
    """Read a u32 from the block's content start."""
    if block.offset + 4 <= block.end:
        return struct.unpack_from('<I', block.data, block.offset)[0]
    return 0


def read_float(block):
    """Read a f32 from the block's content start."""
    if block.offset + 4 <= block.end:
        return struct.unpack_from('<f', block.data, block.offset)[0]
    return 0.0


def read_string(data, pos, end):
    """Read a UTF-16LE string (u16 length + chars)."""
    if pos + 2 > end:
        return "", pos
    slen = struct.unpack_from('<H', data, pos)[0]
    pos += 2
    if pos + slen * 2 > end:
        return "", pos
    s = data[pos:pos + slen * 2].decode('utf-16-le', errors='replace')
    pos += slen * 2
    return s, pos


# ---------------------------------------------------------------------------
# Shape parsing
# ---------------------------------------------------------------------------

def _parse_points(block):
    """Parse points array: u32 count then point child blocks with 3 floats each."""
    points = []
    for child in iter_children(block, skip=4):  # skip count u32
        if child.token_id == TK_POINT and child.offset + 12 <= child.end:
            x, y, z = struct.unpack_from('<3f', child.data, child.offset)
            points.append((x, y, z))
    return points


def _parse_uv_points(block):
    """Parse UV coordinate array."""
    uvs = []
    for child in iter_children(block, skip=4):
        if child.token_id == TK_UV_POINT and child.offset + 8 <= child.end:
            u, v = struct.unpack_from('<2f', child.data, child.offset)
            uvs.append((u, v))
    return uvs


def _parse_normals(block):
    """Parse normal vector array."""
    normals = []
    for child in iter_children(block, skip=4):
        if child.token_id == TK_VECTOR and child.offset + 12 <= child.end:
            x, y, z = struct.unpack_from('<3f', child.data, child.offset)
            normals.append((x, y, z))
    return normals


def _parse_vertex(block, global_points, global_normals, global_uvs):
    """Parse a single vertex block — dereferences global arrays.

    Vertex content: u32 flags, u32 pointIdx, u32 normalIdx, u32 colour1, u32 colour2,
    then child vertex_uvs block.
    """
    off = block.offset
    if off + 20 > block.end:
        return None
    _flags = struct.unpack_from('<I', block.data, off)[0]
    point_idx = struct.unpack_from('<I', block.data, off + 4)[0]
    normal_idx = struct.unpack_from('<I', block.data, off + 8)[0]
    # colour1 at off+12, colour2 at off+16
    # vertex_uvs child block starts after the 20 bytes of inline data

    pos = global_points[point_idx] if point_idx < len(global_points) else (0, 0, 0)
    nrm = global_normals[normal_idx] if normal_idx < len(global_normals) else (0, 0, 1)

    # Parse vertex_uvs child block for UV indices
    uv = (0.0, 0.0)
    for child in iter_children(block, skip=20):
        if child.token_id == TK_VERTEX_UVS and child.offset + 4 <= child.end:
            uv_count = struct.unpack_from('<I', child.data, child.offset)[0]
            if uv_count > 0 and child.offset + 8 <= child.end:
                uv_idx = struct.unpack_from('<I', child.data, child.offset + 4)[0]
                if uv_idx < len(global_uvs):
                    uv = global_uvs[uv_idx]

    return pos, nrm, uv


def _parse_sub_object(block, global_points, global_normals, global_uvs):
    """Parse a sub_object block into an SIMISMesh."""
    local_verts = []  # (pos, normal, uv)
    triangles = []

    for child in iter_children(block):
        if child.token_id == TK_VERTICES:
            for vchild in iter_children(child, skip=4):  # skip count
                if vchild.token_id == TK_VERTEX:
                    v = _parse_vertex(vchild, global_points, global_normals, global_uvs)
                    if v:
                        local_verts.append(v)

        elif child.token_id == TK_PRIMITIVES:
            for pchild in iter_children(child, skip=4):  # skip count
                if pchild.token_id == TK_INDEXED_TRILIST:
                    for tchild in iter_children(pchild):
                        if tchild.token_id == TK_VERTEX_IDXS:
                            total = struct.unpack_from('<I', tchild.data, tchild.offset)[0]
                            off = tchild.offset + 4
                            num_tris = total // 3
                            for _ in range(num_tris):
                                if off + 12 > tchild.end:
                                    break
                                a, b, c = struct.unpack_from('<3I', tchild.data, off)
                                off += 12
                                triangles.extend([a, b, c])

    if not local_verts or not triangles:
        return None

    mesh = SIMISMesh()
    mesh.positions = [v[0] for v in local_verts]
    mesh.normals = [v[1] for v in local_verts]
    mesh.uvs = [v[2] for v in local_verts]
    mesh.triangles = [idx for idx in triangles if idx < len(local_verts)]
    return mesh


def parse_simis(path, verbose=False):
    """Parse a SIMIS shape file."""
    model = SIMISModel()
    model.name = os.path.splitext(os.path.basename(path))[0]

    try:
        with open(path, 'rb') as f:
            data = f.read()
    except Exception as e:
        if verbose:
            print(f"[SIMIS] Error reading: {e}", file=sys.stderr)
        return model

    # Check for SIMISA wrapper or raw JINX
    if data[:8] == b'SIMISA@F':
        # Compressed — decompress with zlib
        import zlib
        decomp_size = struct.unpack_from('<I', data, 8)[0]
        try:
            data = zlib.decompress(data[16:], -15, decomp_size + 1024)
        except Exception:
            try:
                data = zlib.decompress(data[16:])
            except Exception as e:
                if verbose:
                    print(f"[SIMIS] Decompression failed: {e}", file=sys.stderr)
                return model
    elif data[:8] == b'SIMISA@@':
        data = data[16:]  # Skip SIMISA wrapper

    if data[:4] != b'JINX':
        if verbose:
            print("[SIMIS] Not a JINX file", file=sys.stderr)
        return model

    # Skip 16-byte JINX header
    root_block = read_block(data, 16)
    if root_block is None:
        if verbose:
            print("[SIMIS] No root block", file=sys.stderr)
        return model

    # Parse global arrays from shape root
    global_points = []
    global_normals = []
    global_uvs = []

    for child in iter_children(root_block):
        if child.token_id == TK_POINTS:
            global_points = _parse_points(child)
        elif child.token_id == TK_NORMALS:
            global_normals = _parse_normals(child)
        elif child.token_id == TK_UV_POINTS:
            global_uvs = _parse_uv_points(child)
        elif child.token_id == TK_LOD_CONTROLS:
            # Parse first LOD only (highest detail)
            for lod_ctrl in iter_children(child, skip=4):
                if lod_ctrl.token_id == TK_LOD_CONTROL:
                    _parse_lod_control(lod_ctrl, global_points, global_normals,
                                       global_uvs, model, verbose)
                    break
        elif child.token_id == TK_SUB_OBJECTS:
            # Direct sub_objects without LOD wrapping (format variant)
            for so in iter_children(child, skip=4):
                if so.token_id == TK_SUB_OBJECT:
                    mesh = _parse_sub_object(so, global_points, global_normals, global_uvs)
                    if mesh:
                        model.meshes.append(mesh)
                        if verbose:
                            print(f"[SIMIS]   sub_object: {len(mesh.positions)}v "
                                  f"{len(mesh.triangles) // 3}t", file=sys.stderr)

    if verbose:
        total_v = sum(len(m.positions) for m in model.meshes)
        total_t = sum(len(m.triangles) // 3 for m in model.meshes)
        print(f"[SIMIS] {len(model.meshes)} mesh(es), {total_v} verts, {total_t} tris",
              file=sys.stderr)

    return model


def _parse_lod_control(block, points, normals, uvs, model, verbose):
    """Parse a lod_control block — extract first (highest detail) distance level."""
    for child in iter_children(block):
        if child.token_id == TK_DIST_LEVELS:
            for dlevel in iter_children(child, skip=4):
                if dlevel.token_id == TK_DIST_LEVEL:
                    _parse_distance_level(dlevel, points, normals, uvs, model, verbose)
                    return  # Only first (highest detail) distance level


def _parse_distance_level(block, points, normals, uvs, model, verbose):
    """Parse a distance_level block — extract sub_objects."""
    for child in iter_children(block):
        if child.token_id == TK_SUB_OBJECTS:
            for so in iter_children(child, skip=4):
                if so.token_id == TK_SUB_OBJECT:
                    mesh = _parse_sub_object(so, points, normals, uvs)
                    if mesh:
                        model.meshes.append(mesh)
                        if verbose:
                            print(f"[SIMIS]   sub_object: {len(mesh.positions)}v "
                                  f"{len(mesh.triangles) // 3}t", file=sys.stderr)


# ---------------------------------------------------------------------------
# GLB conversion
# ---------------------------------------------------------------------------

def convert_to_glb(model, output_path, verbose=False):
    """Convert a SIMISModel to GLB format."""
    builder = GLBBuilder(verbose=verbose)

    if not model.meshes:
        glb_data = builder.build_glb(generator="poly2glb-simisShape")
        with open(output_path, 'wb') as f:
            f.write(glb_data)
        return

    builder.materials_gltf.append({
        "pbrMetallicRoughness": {
            "baseColorFactor": [0.7, 0.7, 0.7, 1.0],
            "metallicFactor": 0.1,
            "roughnessFactor": 0.8,
        },
        "doubleSided": True,
    })

    for mi, mesh in enumerate(model.meshes):
        if not mesh.positions or not mesh.triangles:
            continue

        has_uvs = mesh.uvs and len(mesh.uvs) == len(mesh.positions)
        has_normals = mesh.normals and len(mesh.normals) == len(mesh.positions)

        # Flat shading for clear visual definition without textures
        gp, gn, gi, gu = [], [], [], []
        for t in range(0, len(mesh.triangles) - 2, 3):
            i0, i1, i2 = mesh.triangles[t], mesh.triangles[t + 1], mesh.triangles[t + 2]
            if max(i0, i1, i2) >= len(mesh.positions):
                continue
            p0, p1, p2 = mesh.positions[i0], mesh.positions[i1], mesh.positions[i2]
            e1 = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
            e2 = (p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2])
            nx = e1[1] * e2[2] - e1[2] * e2[1]
            ny = e1[2] * e2[0] - e1[0] * e2[2]
            nz = e1[0] * e2[1] - e1[1] * e2[0]
            mag = math.sqrt(nx * nx + ny * ny + nz * nz)
            fn = (nx / mag, ny / mag, nz / mag) if mag > 1e-10 else (0, 0, 1)
            fb = len(gp)
            gp.extend([p0, p1, p2])
            gn.extend([fn, fn, fn])
            gi.extend([fb, fb + 1, fb + 2])
            if has_uvs:
                gu.extend([mesh.uvs[i0], mesh.uvs[i1], mesh.uvs[i2]])
        if not has_uvs:
            gu = None

        if not gp:
            continue

        prim = builder.build_primitive(gp, gn, gi, material_idx=0)
        if prim:
            if gu and len(gu) == len(gp):
                uv_data = bytearray()
                for u, v in gu:
                    uv_data += struct.pack('<ff', u, v)
                uv_bv = builder.add_buffer_view(uv_data, target=34962)
                uv_acc = builder.add_accessor(uv_bv, 5126, len(gu), "VEC2")
                prim["attributes"]["TEXCOORD_0"] = uv_acc

            mesh_idx = len(builder.meshes)
            builder.meshes.append({"primitives": [prim]})
            builder.nodes.append({"mesh": mesh_idx})
            builder.scene_nodes.append(len(builder.nodes) - 1)

    glb_data = builder.build_glb(generator="poly2glb-simisShape")
    with open(output_path, 'wb') as f:
        f.write(glb_data)

    if verbose:
        print(f"[SIMIS] GLB written: {output_path} ({len(glb_data) / 1024:.1f} KB)",
              file=sys.stderr)

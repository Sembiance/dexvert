# Vibe coded by Claude
"""
Electric Image 3D (.fac/.fact/.fct) parser and GLB converter.

Parses the IFF-based 3DFL format used by Electric Image Animation System (EIAS).
Supports both direct IFF files and wrapper-format files (FACTEIAM header at 0x41).
See electricImage3D-spec.txt for full format documentation.
"""

import struct
import sys
import os
import math

from glb import (GLBBuilder, ear_clip, merge_polygon_holes,
                 is_convex_polygon, fan_triangulate)


class EI3DModel:
    """Holds parsed data from an Electric Image 3D file."""
    def __init__(self):
        self.groups = []  # list of EI3DGroup


class EI3DGroup:
    """A geometry group (mesh) within the file."""
    def __init__(self):
        self.name = ""
        self.vertices = []   # list of (x, y, z) tuples
        self.normals = []    # list of (nx, ny, nz) tuples (per-vertex)
        self.faces = []      # list of vertex index lists
        self.vertex_count = 0
        self.face_count = 0
        self.color = None    # (r, g, b) floats 0-1, from GATR
        self.mat_color = None  # (r, g, b) floats 0-1, from GMAT refc


def parse_ei3d(filepath, verbose=False):
    """Parse an Electric Image 3D file. Returns an EI3DModel."""
    with open(filepath, 'rb') as f:
        data = f.read()

    model = EI3DModel()

    # Detect format: direct IFF or FACTEIAM wrapper
    if data[0:4] == b'FORM':
        iff_start = 0
    elif len(data) >= 0x84 and data[0x41:0x47] == b'FACTEI':
        # Wrapper format: FACTEIAM or FACTEIBC magic at 0x41
        # FORM always at offset 0x80
        iff_start = 0x80
    else:
        raise ValueError("Not an Electric Image 3D file: "
                         "no FORM header or FACTEI* signature")

    if verbose:
        print(f"[EI3D] File size: {len(data)} bytes, IFF at {hex(iff_start)}",
              file=sys.stderr)

    _parse_iff(data, iff_start, model, verbose)
    return model


def _parse_iff(data, offset, model, verbose):
    """Parse IFF FORM structure."""
    if offset + 12 > len(data):
        return
    tag = data[offset:offset+4]
    if tag != b'FORM':
        return
    form_size = struct.unpack('>I', data[offset+4:offset+8])[0]
    form_type = data[offset+8:offset+12].decode('ascii', errors='replace')

    if verbose:
        print(f"[EI3D] FORM {form_type} ({form_size}B) at {hex(offset)}",
              file=sys.stderr)

    if form_type == '3DFL':
        _parse_children(data, offset + 12, offset + 8 + form_size,
                        model, verbose)
    elif form_type == 'GRUP':
        group = EI3DGroup()
        _parse_group(data, offset + 12, offset + 8 + form_size,
                     group, verbose)
        if group.vertices:
            model.groups.append(group)


def _parse_children(data, start, end, model, verbose):
    """Parse child chunks/FORMs within a container."""
    pos = start
    while pos < end - 8:
        tag = data[pos:pos+4]
        size = struct.unpack('>I', data[pos+4:pos+8])[0]

        if tag == b'FORM':
            form_type = data[pos+8:pos+12].decode('ascii', errors='replace')
            if form_type == 'GRUP':
                group = EI3DGroup()
                _parse_group(data, pos + 12, pos + 8 + size, group, verbose)
                if group.vertices:
                    model.groups.append(group)
            elif form_type in ('FHDR', 'GHDR'):
                _parse_children(data, pos + 12, pos + 8 + size,
                                model, verbose)
            pos += 8 + size
        else:
            pos += 8 + size

        # IFF padding to even boundary
        if pos % 2:
            pos += 1


def _parse_group(data, start, end, group, verbose):
    """Parse a GRUP FORM: extract geometry from child chunks."""
    pos = start
    while pos < end - 8:
        tag = data[pos:pos+4]
        size = struct.unpack('>I', data[pos+4:pos+8])[0]
        chunk_data = data[pos+8:pos+8+size]

        if tag == b'FORM':
            form_type = data[pos+8:pos+12].decode('ascii', errors='replace')
            if form_type == 'GHDR':
                _parse_ghdr(data, pos + 12, pos + 8 + size, group, verbose)
            elif form_type == 'GMAT':
                _parse_gmat(data, pos + 12, pos + 8 + size, group, verbose)
            pos += 8 + size
        elif tag == b'CORD':
            _parse_cord(chunk_data, group, verbose)
            pos += 8 + size
        elif tag == b'DCOR':
            _parse_dcor(chunk_data, group, verbose)
            pos += 8 + size
        elif tag == b'NVRT':
            _parse_nvrt(chunk_data, group, verbose)
            pos += 8 + size
        elif tag == b'ELEM':
            _parse_elem(chunk_data, group, verbose)
            pos += 8 + size
        else:
            pos += 8 + size

        if pos % 2:
            pos += 1


def _parse_ghdr(data, start, end, group, verbose):
    """Parse GHDR children: GINF (counts, name) and GATR (color)."""
    pos = start
    while pos < end - 8:
        tag = data[pos:pos+4]
        size = struct.unpack('>I', data[pos+4:pos+8])[0]
        chunk_data = data[pos+8:pos+8+size]

        if tag == b'GINF' and size >= 8:
            group.vertex_count = struct.unpack('>I', chunk_data[0:4])[0]
            group.face_count = struct.unpack('>I', chunk_data[4:8])[0]
            # Name: u8 length at offset 0x28, followed by ASCII name
            if size > 0x29:
                name_len = chunk_data[0x28]
                if name_len > 0 and 0x29 + name_len <= size:
                    try:
                        group.name = chunk_data[0x29:0x29+name_len].decode(
                            'ascii', errors='replace')
                    except Exception:
                        pass
            if verbose:
                print(f"[EI3D]   GINF: verts={group.vertex_count} "
                      f"faces={group.face_count} name='{group.name}'",
                      file=sys.stderr)

        elif tag == b'GATR' and size >= 6:
            # GATR: offset 2 = 0xFF marker, bytes 3-5 = diffuse RGB
            if chunk_data[2] == 0xFF:
                r = chunk_data[3] / 255.0
                g = chunk_data[4] / 255.0
                b = chunk_data[5] / 255.0
                group.color = (r, g, b)
                if verbose:
                    print(f"[EI3D]   GATR: color=({r:.3f},{g:.3f},{b:.3f})",
                          file=sys.stderr)

        pos += 8 + size
        if pos % 2:
            pos += 1


def _parse_gmat(data, start, end, group, verbose):
    """Parse GMAT FORM: extract refc (diffuse color) for material."""
    pos = start
    while pos < end - 8:
        tag = data[pos:pos+4]
        size = struct.unpack('>I', data[pos+4:pos+8])[0]
        chunk_data = data[pos+8:pos+8+size]

        if tag == b'refc' and size == 32:
            # Color chunk: f64 intensity + f64 R + f64 G + f64 B
            _intensity, r, g, b = struct.unpack('>4d', chunk_data)
            group.mat_color = (r, g, b)
            if verbose:
                print(f"[EI3D]   GMAT refc: ({r:.3f},{g:.3f},{b:.3f})",
                      file=sys.stderr)

        pos += 8 + size
        if pos % 2:
            pos += 1


def _parse_cord(chunk_data, group, verbose):
    """Parse CORD chunk: big-endian f32 XYZ vertex triplets."""
    num_verts = len(chunk_data) // 12
    for i in range(num_verts):
        x, y, z = struct.unpack('>3f', chunk_data[i*12:i*12+12])
        group.vertices.append((x, y, z))
    if verbose:
        print(f"[EI3D]   CORD: {num_verts} vertices", file=sys.stderr)


def _parse_dcor(chunk_data, group, verbose):
    """Parse DCOR chunk: big-endian f64 XYZ vertex triplets."""
    num_verts = len(chunk_data) // 24
    for i in range(num_verts):
        x, y, z = struct.unpack('>3d', chunk_data[i*24:i*24+24])
        group.vertices.append((x, y, z))
    if verbose:
        print(f"[EI3D]   DCOR: {num_verts} vertices (f64)", file=sys.stderr)


def _parse_nvrt(chunk_data, group, verbose):
    """Parse NVRT chunk: big-endian f32 XYZ normal triplets."""
    num_norms = len(chunk_data) // 12
    for i in range(num_norms):
        nx, ny, nz = struct.unpack('>3f', chunk_data[i*12:i*12+12])
        group.normals.append((nx, ny, nz))
    if verbose:
        print(f"[EI3D]   NVRT: {num_norms} normals", file=sys.stderr)


def _parse_elem(chunk_data, group, verbose):
    """Parse ELEM chunk: face element records.

    Three index modes based on vertex count:
      u8  (verts ≤ 255):   6-byte header + u8 indices + 0x00 terminator
      u16 (verts ≤ 65535): 6-byte header + 4×u16 = 14 bytes fixed
      u24 (verts > 65535):  6-byte header + 4×u24 = 18 bytes fixed

    Face record header (6 bytes):
      u8(type) + u8(0x00) + u8(0xFF) + u8(attr0) + u8(attr1) + u8(attr2)
      type: 0x00=triangle, 0x01=quad, 0x02=alt quad

    Polygon metadata: 0x00 0x01 + u32(byte_count) + data (skipped)
    """
    n_verts = len(group.vertices) or group.vertex_count
    if len(chunk_data) < 6 or n_verts == 0:
        group.faces = []
        return

    faces = []

    if n_verts > 65535:
        # u24 mode: 18-byte fixed records
        i = 0
        while i + 6 <= len(chunk_data):
            if (i + 2 < len(chunk_data) and
                    chunk_data[i+2] == 0xFF and
                    chunk_data[i+1] == 0x00 and
                    chunk_data[i] <= 0x0F and
                    i + 18 <= len(chunk_data)):
                indices = []
                for vi in range(4):
                    b0 = chunk_data[i+6+vi*3]
                    b1 = chunk_data[i+7+vi*3]
                    b2 = chunk_data[i+8+vi*3]
                    val = (b0 << 16) | (b1 << 8) | b2
                    if 1 <= val <= n_verts:
                        indices.append(val - 1)
                if len(indices) >= 3:
                    seen = []
                    for idx in indices:
                        if idx not in seen:
                            seen.append(idx)
                    if len(seen) >= 3:
                        faces.append(seen)
                i += 18
            elif (chunk_data[i] == 0x00 and chunk_data[i+1] == 0x01 and
                  i + 6 <= len(chunk_data)):
                nn = struct.unpack('>I', chunk_data[i+2:i+6])[0]
                i = i + 6 + nn
            else:
                i += 2

    elif n_verts > 255:
        # u16 mode: 14-byte fixed records
        i = 0
        while i + 6 <= len(chunk_data):
            if (i + 2 < len(chunk_data) and
                    chunk_data[i+2] == 0xFF and
                    chunk_data[i+1] == 0x00 and
                    chunk_data[i] <= 0x0F and
                    i + 14 <= len(chunk_data)):
                indices = []
                for vi in range(4):
                    val = struct.unpack('>H',
                        chunk_data[i+6+vi*2:i+8+vi*2])[0]
                    if 1 <= val <= n_verts:
                        indices.append(val - 1)
                if len(indices) >= 3:
                    seen = []
                    for idx in indices:
                        if idx not in seen:
                            seen.append(idx)
                    if len(seen) >= 3:
                        faces.append(seen)
                i += 14
            elif (chunk_data[i] == 0x00 and chunk_data[i+1] == 0x01 and
                  i + 6 <= len(chunk_data)):
                nn = struct.unpack('>I', chunk_data[i+2:i+6])[0]
                i = i + 6 + nn
            else:
                i += 2

    else:
        # u8 mode: fixed 10-byte face records + polygon metadata.
        # Face record (10 bytes): 6-byte header + 4 bytes body
        #   Quad: 4 u8 indices (1-based)
        #   Triangle: 3 u8 indices + 0x00 padding
        # Polygon metadata: 00 01 + u32(byte_count) + data
        i = 0
        while i + 6 <= len(chunk_data):
            if (chunk_data[i+2] == 0xFF and
                    chunk_data[i+1] == 0x00 and
                    chunk_data[i] <= 0x0F and
                    i + 10 <= len(chunk_data)):
                # Face record: read 4 bytes at offset 6-9
                indices = []
                for vi in range(4):
                    val = chunk_data[i + 6 + vi]
                    if val >= 1 and val <= n_verts:
                        indices.append(val - 1)
                # Deduplicate (triangles have 0x00 padding as 4th byte)
                if len(indices) >= 3:
                    seen = []
                    for idx in indices:
                        if idx not in seen:
                            seen.append(idx)
                    if len(seen) >= 3:
                        faces.append(seen)
                i += 10
            elif (chunk_data[i] == 0x00 and chunk_data[i+1] == 0x01 and
                  i + 6 <= len(chunk_data)):
                # Polygon metadata: skip
                nn = struct.unpack('>I', chunk_data[i+2:i+6])[0]
                i = i + 6 + nn
            else:
                i += 1

    group.faces = faces
    mode = 'u24' if n_verts > 65535 else ('u16' if n_verts > 255 else 'u8')
    if verbose:
        print(f"[EI3D]   ELEM: {len(faces)} faces ({mode})",
              file=sys.stderr)


def convert_to_glb(model, output_path, verbose=False):
    """Convert an EI3DModel to GLB format."""
    builder = GLBBuilder(verbose=verbose)

    has_geometry = any(g.vertices and g.faces for g in model.groups)
    if not has_geometry:
        glb_data = builder.build_glb(generator="poly2glb-ei3d")
        with open(output_path, 'wb') as f:
            f.write(glb_data)
        return

    # Build materials: prefer GMAT refc, fall back to GATR color
    color_to_mat = {}
    group_mat_indices = []
    for group in model.groups:
        color = group.mat_color or group.color or (0.4, 0.4, 0.4)
        color_key = (round(color[0], 3), round(color[1], 3),
                     round(color[2], 3))
        if color_key not in color_to_mat:
            mat_idx = len(builder.materials_gltf)
            builder.materials_gltf.append({
                "pbrMetallicRoughness": {
                    "baseColorFactor": [color[0], color[1], color[2], 1.0],
                    "metallicFactor": 0.0,
                    "roughnessFactor": 0.8
                },
                "doubleSided": True
            })
            color_to_mat[color_key] = mat_idx
        group_mat_indices.append(color_to_mat[color_key])

    # Build one mesh per group with per-group materials
    total_tris = 0
    gi = 0
    for group in model.groups:
        if not group.vertices or not group.faces:
            gi += 1
            continue
        mi = group_mat_indices[gi] if gi < len(group_mat_indices) else 0
        positions = group.vertices
        has_normals = len(group.normals) == len(group.vertices)

        grp_positions = []
        grp_normals = []
        grp_indices = []

        if has_normals:
            # Smooth shading: shared vertices with per-vertex normals
            for vi in range(len(positions)):
                p = positions[vi]
                n = group.normals[vi]
                grp_positions.append((p[0], p[1], -p[2]))
                grp_normals.append((n[0], n[1], -n[2]))

            for face in group.faces:
                if len(face) < 3:
                    continue
                if any(idx < 0 or idx >= len(positions) for idx in face):
                    continue
                # Reverse winding: EI3D CW → glTF CCW
                rf = list(reversed(face))
                if len(rf) == 4:
                    p = [grp_positions[f] for f in rf]
                    d02 = sum((p[0][k]-p[2][k])**2 for k in range(3))
                    d13 = sum((p[1][k]-p[3][k])**2 for k in range(3))
                    if d02 <= d13:
                        grp_indices.extend([rf[0], rf[1], rf[2],
                                            rf[0], rf[2], rf[3]])
                    else:
                        grp_indices.extend([rf[1], rf[2], rf[3],
                                            rf[1], rf[3], rf[0]])
                else:
                    for ti in range(1, len(rf) - 1):
                        grp_indices.extend([rf[0], rf[ti], rf[ti+1]])
        else:
            # Flat shading: duplicate vertices per face
            for face in group.faces:
                if len(face) < 3:
                    continue
                if any(idx < 0 or idx >= len(positions) for idx in face):
                    continue
                # Reverse winding: EI3D CW → glTF CCW
                rf = list(reversed(face))
                v0, v1, v2 = positions[rf[0]], positions[rf[1]], positions[rf[2]]
                e1 = (v1[0]-v0[0], v1[1]-v0[1], v1[2]-v0[2])
                e2 = (v2[0]-v0[0], v2[1]-v0[1], v2[2]-v0[2])
                nx = e1[1]*e2[2] - e1[2]*e2[1]
                ny = e1[2]*e2[0] - e1[0]*e2[2]
                nz = e1[0]*e2[1] - e1[1]*e2[0]
                nl = math.sqrt(nx*nx + ny*ny + nz*nz)
                if nl > 0:
                    nx /= nl; ny /= nl; nz /= nl
                else:
                    nx, ny, nz = 0, 1, 0
                gn = (nx, ny, -nz)

                if len(rf) == 4:
                    p = [positions[i] for i in rf]
                    gp = [(p[k][0], p[k][1], -p[k][2]) for k in range(4)]
                    d02 = sum((gp[0][k]-gp[2][k])**2 for k in range(3))
                    d13 = sum((gp[1][k]-gp[3][k])**2 for k in range(3))
                    fb = len(grp_positions)
                    grp_positions.extend(gp)
                    grp_normals.extend([gn] * 4)
                    if d02 <= d13:
                        grp_indices.extend([fb, fb+1, fb+2, fb, fb+2, fb+3])
                    else:
                        grp_indices.extend([fb+1, fb+2, fb+3, fb+1, fb+3, fb])
                else:
                    for ti in range(1, len(rf) - 1):
                        fb = len(grp_positions)
                        for vi in [rf[0], rf[ti], rf[ti+1]]:
                            pp = positions[vi]
                            grp_positions.append((pp[0], pp[1], -pp[2]))
                            grp_normals.append(gn)
                        grp_indices.extend([fb, fb+1, fb+2])

        if grp_positions and grp_indices:
            prim = builder.build_primitive(grp_positions, grp_normals,
                                           grp_indices, material_idx=mi)
            if prim:
                total_tris += len(grp_indices) // 3
                mesh_idx = len(builder.meshes)
                builder.meshes.append({"primitives": [prim]})
                node_idx = len(builder.nodes)
                builder.nodes.append({"mesh": mesh_idx})
                builder.scene_nodes.append(node_idx)
        gi += 1

    glb_data = builder.build_glb(generator="poly2glb-ei3d")
    with open(output_path, 'wb') as f:
        f.write(glb_data)

    if verbose:
        print(f"[EI3D] Output: {total_tris} tris", file=sys.stderr)

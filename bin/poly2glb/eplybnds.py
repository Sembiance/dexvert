# Vibe coded by Claude
"""
EPLYBNDS (.ply) parser and GLB converter.

Parses the EPLYBNDS binary mesh format used in game assets.
Supports multiple vertex layouts (32B-52B stride) with positions,
normals, UVs, vertex colors, tangents, and skinning data.

File structure:
  1. Header (32B): "EPLYBNDS" + bbox (6 x f32 LE)
  2. MESH sections (1+): format_flags, tri range, material, name
  3. VERT section (1): vertex_count, stride, vertex data
  4. INDX section (1): index_count, index data (u16 LE)
  5. Optional: ADJA, SHDW, MROR sections (skipped)
"""

import struct
import sys
import os

from glb import GLBBuilder


class EPLYBNDSMesh:
    """A mesh/submesh within the EPLYBNDS file."""
    def __init__(self):
        self.name = ""
        self.flags = 0
        self.tri_start = 0
        self.tri_count = 0
        self.mat_props = b'\x00' * 4
        self.mesh_color = None   # (r, g, b, a) 0-255 from extended header


class EPLYBNDSModel:
    """Holds parsed data from an EPLYBNDS file."""
    def __init__(self):
        self.bbox_min = (0.0, 0.0, 0.0)
        self.bbox_max = (0.0, 0.0, 0.0)
        self.meshes = []          # list of EPLYBNDSMesh
        self.vertex_count = 0
        self.vertex_stride = 0
        self.positions = []       # list of (x, y, z)
        self.normals = []         # list of (nx, ny, nz)
        self.uvs = []             # list of (u, v)
        self.uvs2 = []            # list of (u, v) - second UV set
        self.colors = []          # list of (r, g, b, a) as 0-255
        self.tangents = []        # list of (tx, ty, tz, tw)
        self.bone_weights = []    # list of f32
        self.bone_indices = []    # list of u32
        self.indices = []         # flat list of u16 triangle indices


def parse_eplybnds(filepath, verbose=False):
    """Parse an EPLYBNDS file. Returns an EPLYBNDSModel."""
    with open(filepath, 'rb') as f:
        data = f.read()

    if len(data) < 32 or data[:8] != b'EPLYBNDS':
        raise ValueError("Not an EPLYBNDS file: missing magic header")

    model = EPLYBNDSModel()

    # Parse header: 8B magic + 6 x f32 bbox
    bbox = struct.unpack('<6f', data[8:32])
    model.bbox_min = (bbox[0], bbox[1], bbox[2])
    model.bbox_max = (bbox[3], bbox[4], bbox[5])

    if verbose:
        print(f"[EPLYBNDS] File size: {len(data)} bytes", file=sys.stderr)
        print(f"[EPLYBNDS] BBox min: ({bbox[0]:.3f}, {bbox[1]:.3f}, {bbox[2]:.3f})",
              file=sys.stderr)
        print(f"[EPLYBNDS] BBox max: ({bbox[3]:.3f}, {bbox[4]:.3f}, {bbox[5]:.3f})",
              file=sys.stderr)

    # Known section tags for scanning
    _KNOWN_TAGS = {b'MESH', b'VERT', b'INDX', b'ADJA', b'SHDW', b'MROR'}

    def _scan_to_next_tag(start):
        """Scan forward from start to find the next known section tag."""
        p = start
        while p < len(data) - 3:
            if data[p:p + 4] in _KNOWN_TAGS:
                return p
            p += 1
        return len(data)

    # Parse sections sequentially
    pos = 32

    # Skip optional SKIN section at start of file
    # Format: "SKIN" (4B) + bone_count (u32 LE) + bone_count x (name_len(u8) + name)
    if pos + 8 <= len(data) and data[pos:pos + 4] == b'SKIN':
        bone_count = struct.unpack('<I', data[pos + 4:pos + 8])[0]
        pos += 8
        bone_names = []
        for _bi in range(bone_count):
            if pos >= len(data):
                break
            bn_len = data[pos]
            bn_name = data[pos + 1:pos + 1 + bn_len].decode(
                'ascii', errors='replace')
            bone_names.append(bn_name)
            pos += 1 + bn_len
        if verbose:
            print(f"[EPLYBNDS] SKIN: {bone_count} bones: "
                  f"{', '.join(bone_names[:5])}"
                  f"{'...' if bone_count > 5 else ''}",
                  file=sys.stderr)

    while pos < len(data) - 4:
        tag = data[pos:pos + 4]

        if tag == b'MESH':
            mesh = EPLYBNDSMesh()
            mesh.flags = struct.unpack('<I', data[pos + 4:pos + 8])[0]
            mesh.tri_start = struct.unpack('<I', data[pos + 8:pos + 12])[0]
            mesh.tri_count = struct.unpack('<I', data[pos + 12:pos + 16])[0]
            mesh.mat_props = data[pos + 16:pos + 20]
            # Extended header: mat_props byte[1] in {0x06, 0x07} means 4
            # extra bytes (RGBA mesh color) before name_len
            header_extra = 0
            if mesh.mat_props[1] in (0x06, 0x07):
                header_extra = 4
                cr = data[pos + 20]
                cg = data[pos + 21]
                cb = data[pos + 22]
                ca = data[pos + 23]
                mesh.mesh_color = (cr, cg, cb, ca)
            name_off = pos + 20 + header_extra
            name_len = data[name_off]
            mesh.name = data[name_off + 1:name_off + 1 + name_len].decode(
                'ascii', errors='replace')
            model.meshes.append(mesh)
            if verbose:
                color_str = ""
                if mesh.mesh_color:
                    color_str = (f" color=({mesh.mesh_color[0]},"
                                 f"{mesh.mesh_color[1]},"
                                 f"{mesh.mesh_color[2]},"
                                 f"{mesh.mesh_color[3]})")
                print(f"[EPLYBNDS] MESH: flags={hex(mesh.flags)} "
                      f"tri_start={mesh.tri_start} tri_count={mesh.tri_count} "
                      f"name='{mesh.name}'{color_str}", file=sys.stderr)
            # Advance past name, then scan to next known tag to skip
            # any inter-MESH padding (e.g. 3-byte skinning metadata)
            pos = _scan_to_next_tag(name_off + 1 + name_len)

        elif tag == b'VERT':
            vert_count = struct.unpack('<I', data[pos + 4:pos + 8])[0]
            stride = struct.unpack('<H', data[pos + 8:pos + 10])[0]
            _padding = struct.unpack('<H', data[pos + 10:pos + 12])[0]
            model.vertex_count = vert_count
            model.vertex_stride = stride

            if verbose:
                print(f"[EPLYBNDS] VERT: count={vert_count} stride={stride}",
                      file=sys.stderr)

            _parse_vertices(data, pos + 12, vert_count, stride, model, verbose)
            pos += 12 + vert_count * stride

        elif tag == b'INDX':
            idx_count = struct.unpack('<I', data[pos + 4:pos + 8])[0]
            if verbose:
                print(f"[EPLYBNDS] INDX: count={idx_count}", file=sys.stderr)
            for i in range(idx_count):
                off = pos + 8 + i * 2
                model.indices.append(struct.unpack('<H', data[off:off + 2])[0])
            pos += 8 + idx_count * 2

        elif tag in (b'ADJA', b'SHDW', b'MROR'):
            if verbose:
                print(f"[EPLYBNDS] Skipping trailing section: "
                      f"{tag.decode('ascii', errors='replace')}", file=sys.stderr)
            break  # Stop parsing at optional trailing sections
        else:
            if verbose:
                print(f"[EPLYBNDS] Unknown section at {pos}: "
                      f"{tag.decode('ascii', errors='replace')}", file=sys.stderr)
            break

    if verbose:
        print(f"[EPLYBNDS] Parsed: {len(model.meshes)} meshes, "
              f"{model.vertex_count} vertices, {len(model.indices)} indices",
              file=sys.stderr)

    return model


def _parse_vertices(data, offset, count, stride, model, verbose):
    """Parse vertex data based on stride to determine layout.

    Stride-based layouts (authoritative, flags used only to disambiguate):
      32B: pos(3f) + normal(3f) + uv(2f)
      36B: pos(3f) + normal(3f) + color(4u8) + uv(2f)
      40B non-skinned: pos(3f) + normal(3f) + uv(2f) + uv2(2f)
      40B skinned (flags & 0x1000): pos(3f) + boneW(f32) + boneI(u32) + normal(3f) + uv(2f)
      44B: pos(3f) + normal(3f) + color(4u8) + uv(2f) + uv2(2f)
      48B: pos(3f) + normal(3f) + uv(2f) + tangent(4f)
      52B: pos(3f) + normal(3f) + color(4u8) + uv(2f) + tangent(4f)
    """
    # Determine if any mesh has skinning flag set
    has_skin = any(m.flags & 0x1000 for m in model.meshes)

    for i in range(count):
        base = offset + i * stride
        vdata = data[base:base + stride]

        if len(vdata) < stride:
            break

        if stride == 32:
            # pos(3f) + normal(3f) + uv(2f)
            px, py, pz = struct.unpack('<3f', vdata[0:12])
            nx, ny, nz = struct.unpack('<3f', vdata[12:24])
            u, v = struct.unpack('<2f', vdata[24:32])
            model.positions.append((px, py, pz))
            model.normals.append((nx, ny, nz))
            model.uvs.append((u, v))

        elif stride == 36:
            # pos(3f) + normal(3f) + color(4u8) + uv(2f)
            px, py, pz = struct.unpack('<3f', vdata[0:12])
            nx, ny, nz = struct.unpack('<3f', vdata[12:24])
            cr, cg, cb, ca = struct.unpack('4B', vdata[24:28])
            u, v = struct.unpack('<2f', vdata[28:36])
            model.positions.append((px, py, pz))
            model.normals.append((nx, ny, nz))
            model.colors.append((cr, cg, cb, ca))
            model.uvs.append((u, v))

        elif stride == 40:
            if has_skin:
                # pos(3f) + boneW(f32) + boneI(u32) + normal(3f) + uv(2f)
                px, py, pz = struct.unpack('<3f', vdata[0:12])
                bw = struct.unpack('<f', vdata[12:16])[0]
                bi = struct.unpack('<I', vdata[16:20])[0]
                nx, ny, nz = struct.unpack('<3f', vdata[20:32])
                u, v = struct.unpack('<2f', vdata[32:40])
                model.positions.append((px, py, pz))
                model.normals.append((nx, ny, nz))
                model.uvs.append((u, v))
                model.bone_weights.append(bw)
                model.bone_indices.append(bi)
            else:
                # pos(3f) + normal(3f) + uv(2f) + uv2(2f)
                px, py, pz = struct.unpack('<3f', vdata[0:12])
                nx, ny, nz = struct.unpack('<3f', vdata[12:24])
                u, v = struct.unpack('<2f', vdata[24:32])
                u2, v2 = struct.unpack('<2f', vdata[32:40])
                model.positions.append((px, py, pz))
                model.normals.append((nx, ny, nz))
                model.uvs.append((u, v))
                model.uvs2.append((u2, v2))

        elif stride == 44:
            # pos(3f) + normal(3f) + color(4u8) + uv(2f) + uv2(2f)
            px, py, pz = struct.unpack('<3f', vdata[0:12])
            nx, ny, nz = struct.unpack('<3f', vdata[12:24])
            cr, cg, cb, ca = struct.unpack('4B', vdata[24:28])
            u, v = struct.unpack('<2f', vdata[28:36])
            u2, v2 = struct.unpack('<2f', vdata[36:44])
            model.positions.append((px, py, pz))
            model.normals.append((nx, ny, nz))
            model.colors.append((cr, cg, cb, ca))
            model.uvs.append((u, v))
            model.uvs2.append((u2, v2))

        elif stride == 48:
            # pos(3f) + normal(3f) + uv(2f) + tangent(4f)
            px, py, pz = struct.unpack('<3f', vdata[0:12])
            nx, ny, nz = struct.unpack('<3f', vdata[12:24])
            u, v = struct.unpack('<2f', vdata[24:32])
            tx, ty, tz, tw = struct.unpack('<4f', vdata[32:48])
            model.positions.append((px, py, pz))
            model.normals.append((nx, ny, nz))
            model.uvs.append((u, v))
            model.tangents.append((tx, ty, tz, tw))

        elif stride == 52:
            # pos(3f) + normal(3f) + color(4u8) + uv(2f) + tangent(4f)
            px, py, pz = struct.unpack('<3f', vdata[0:12])
            nx, ny, nz = struct.unpack('<3f', vdata[12:24])
            cr, cg, cb, ca = struct.unpack('4B', vdata[24:28])
            u, v = struct.unpack('<2f', vdata[28:36])
            tx, ty, tz, tw = struct.unpack('<4f', vdata[36:52])
            model.positions.append((px, py, pz))
            model.normals.append((nx, ny, nz))
            model.colors.append((cr, cg, cb, ca))
            model.uvs.append((u, v))
            model.tangents.append((tx, ty, tz, tw))

        else:
            # Unknown stride: extract at least position and normal (24B minimum)
            if stride >= 24:
                px, py, pz = struct.unpack('<3f', vdata[0:12])
                nx, ny, nz = struct.unpack('<3f', vdata[12:24])
                model.positions.append((px, py, pz))
                model.normals.append((nx, ny, nz))
                if stride >= 32:
                    u, v = struct.unpack('<2f', vdata[24:32])
                    model.uvs.append((u, v))
            else:
                if verbose:
                    print(f"[EPLYBNDS] WARNING: unsupported stride {stride}",
                          file=sys.stderr)
                break


def convert_to_glb(model, output_path, verbose=False):
    """Convert an EPLYBNDSModel to GLB format."""
    builder = GLBBuilder(verbose=verbose)

    if not model.positions or not model.indices:
        glb_data = builder.build_glb(generator="poly2glb-eplybnds")
        with open(output_path, 'wb') as f:
            f.write(glb_data)
        return

    has_colors = len(model.colors) == len(model.positions)
    total_tris = 0

    for mi, mesh in enumerate(model.meshes):
        # Extract triangle indices for this mesh
        idx_start = mesh.tri_start * 3
        idx_end = (mesh.tri_start + mesh.tri_count) * 3
        mesh_indices = model.indices[idx_start:idx_end]

        if not mesh_indices:
            continue

        # Validate indices
        max_idx = len(model.positions) - 1
        valid = True
        for idx in mesh_indices:
            if idx > max_idx:
                valid = False
                break
        if not valid:
            if verbose:
                print(f"[EPLYBNDS] Skipping mesh '{mesh.name}': "
                      f"index out of range", file=sys.stderr)
            continue

        # Gather unique vertices used by this mesh and remap
        used_verts = sorted(set(mesh_indices))
        old_to_new = {old: new for new, old in enumerate(used_verts)}

        positions = []
        normals = []
        for vi in used_verts:
            positions.append(model.positions[vi])
            normals.append(model.normals[vi])

        remapped_indices = [old_to_new[idx] for idx in mesh_indices]

        # Determine material color
        if has_colors:
            # Average vertex colors for this mesh as material diffuse
            r_sum, g_sum, b_sum = 0.0, 0.0, 0.0
            color_count = 0
            for vi in used_verts:
                c = model.colors[vi]
                r_sum += c[0]
                g_sum += c[1]
                b_sum += c[2]
                color_count += 1
            if color_count > 0:
                mat_color = (r_sum / color_count / 255.0,
                             g_sum / color_count / 255.0,
                             b_sum / color_count / 255.0)
            else:
                mat_color = (0.5, 0.5, 0.5)
        elif mesh.mesh_color:
            # Use per-mesh embedded color from extended header
            mat_color = (mesh.mesh_color[0] / 255.0,
                         mesh.mesh_color[1] / 255.0,
                         mesh.mesh_color[2] / 255.0)
        else:
            mat_color = (0.5, 0.5, 0.5)

        # Create material
        mat_idx = len(builder.materials_gltf)
        builder.materials_gltf.append({
            "pbrMetallicRoughness": {
                "baseColorFactor": [mat_color[0], mat_color[1],
                                    mat_color[2], 1.0],
                "metallicFactor": 0.0,
                "roughnessFactor": 0.8
            },
            "doubleSided": True
        })

        # Build primitive using the GLBBuilder
        prim = builder.build_primitive(positions, normals,
                                       remapped_indices, material_idx=mat_idx)
        if prim:
            total_tris += len(remapped_indices) // 3
            mesh_idx = len(builder.meshes)
            mesh_name = mesh.name if mesh.name else f"mesh_{mi}"
            builder.meshes.append({
                "name": mesh_name,
                "primitives": [prim]
            })
            node_idx = len(builder.nodes)
            builder.nodes.append({
                "name": mesh_name,
                "mesh": mesh_idx
            })
            builder.scene_nodes.append(node_idx)

    glb_data = builder.build_glb(generator="poly2glb-eplybnds")
    with open(output_path, 'wb') as f:
        f.write(glb_data)

    if verbose:
        print(f"[EPLYBNDS] Output: {total_tris} tris, "
              f"{len(builder.meshes)} meshes", file=sys.stderr)

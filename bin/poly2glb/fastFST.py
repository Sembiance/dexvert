# Vibe coded by Claude
"""
FastFST (.fst) archive parser and GLB converter.

FST files are zlib-compressed archives from Crazy Machines: Elements/Golden Gears.
Contains FMesh entries with 3D geometry (positions, normals, UVs, indices).
"""

import struct
import sys
import os
import math
import zlib

from glb import GLBBuilder


# ---------------------------------------------------------------------------
# DXT texture decoding
# ---------------------------------------------------------------------------

def _decode_rgb565(c):
    r = ((c >> 11) & 0x1F) * 255 // 31
    g = ((c >> 5) & 0x3F) * 255 // 63
    b = (c & 0x1F) * 255 // 31
    return r, g, b


def _decode_dxt1_block(data, offset):
    c0 = struct.unpack_from('<H', data, offset)[0]
    c1 = struct.unpack_from('<H', data, offset + 2)[0]
    bits = struct.unpack_from('<I', data, offset + 4)[0]
    r0, g0, b0 = _decode_rgb565(c0)
    r1, g1, b1 = _decode_rgb565(c1)
    if c0 > c1:
        colors = [(r0,g0,b0,255), (r1,g1,b1,255),
                  ((2*r0+r1)//3,(2*g0+g1)//3,(2*b0+b1)//3,255),
                  ((r0+2*r1)//3,(g0+2*g1)//3,(b0+2*b1)//3,255)]
    else:
        colors = [(r0,g0,b0,255), (r1,g1,b1,255),
                  ((r0+r1)//2,(g0+g1)//2,(b0+b1)//2,255), (0,0,0,0)]
    pixels = []
    for i in range(16):
        pixels.append(colors[(bits >> (i*2)) & 3])
    return pixels


def _decode_dxt5_block(data, offset):
    a0, a1 = data[offset], data[offset+1]
    abits = 0
    for i in range(6):
        abits |= data[offset+2+i] << (i*8)
    if a0 > a1:
        alphas = [a0, a1, (6*a0+a1)//7, (5*a0+2*a1)//7,
                  (4*a0+3*a1)//7, (3*a0+4*a1)//7,
                  (2*a0+5*a1)//7, (a0+6*a1)//7]
    else:
        alphas = [a0, a1, (4*a0+a1)//5, (3*a0+2*a1)//5,
                  (2*a0+3*a1)//5, (a0+4*a1)//5, 0, 255]
    c0 = struct.unpack_from('<H', data, offset+8)[0]
    c1 = struct.unpack_from('<H', data, offset+10)[0]
    bits = struct.unpack_from('<I', data, offset+12)[0]
    r0, g0, b0 = _decode_rgb565(c0)
    r1, g1, b1 = _decode_rgb565(c1)
    colors = [(r0,g0,b0), (r1,g1,b1),
              ((2*r0+r1)//3,(2*g0+g1)//3,(2*b0+b1)//3),
              ((r0+2*r1)//3,(g0+2*g1)//3,(b0+2*b1)//3)]
    pixels = []
    for i in range(16):
        r, g, b = colors[(bits >> (i*2)) & 3]
        a = alphas[(abits >> (i*3)) & 7]
        pixels.append((r, g, b, a))
    return pixels


def _decode_dxt(data, w, h, is_dxt5):
    block_size = 16 if is_dxt5 else 8
    bw = max(1, (w+3)//4)
    bh = max(1, (h+3)//4)
    pixels = [(0,0,0,255)] * (w*h)
    offset = 0
    for by in range(bh):
        for bx in range(bw):
            if is_dxt5:
                block = _decode_dxt5_block(data, offset)
            else:
                block = _decode_dxt1_block(data, offset)
            offset += block_size
            for pi in range(16):
                px = bx*4 + (pi % 4)
                py = by*4 + (pi // 4)
                if px < w and py < h:
                    pixels[py*w+px] = block[pi]
    return pixels


def _pixels_to_png(pixels, w, h):
    """Encode RGBA pixels as minimal PNG."""
    def _chunk(tag, d):
        c = tag + d
        crc = zlib.crc32(c) & 0xFFFFFFFF
        return struct.pack('>I', len(d)) + c + struct.pack('>I', crc)
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)
    raw = bytearray()
    for y in range(h):  # DXT stored top-down in FST archives
        raw.append(0)
        for x in range(w):
            r, g, b, a = pixels[y*w+x]
            raw.extend([r, g, b, a])
    compressed = zlib.compress(bytes(raw), 9)
    return sig + _chunk(b'IHDR', ihdr) + _chunk(b'IDAT', compressed) + _chunk(b'IEND', b'')


def _parse_ftexture(data):
    """Parse FTexture entry. Returns (name, png_bytes) or None."""
    if len(data) < 12:
        return None
    name_len = struct.unpack('<I', data[4:8])[0]
    if name_len > len(data) - 8:
        return None
    name = data[8:8+name_len].decode('ascii', errors='replace')
    mp = 8 + name_len
    if mp + 36 > len(data):
        return None
    meta = [struct.unpack('<I', data[mp+i*4:mp+i*4+4])[0] for i in range(9)]
    fmt_code = meta[6]
    w, h = meta[7], meta[8]
    if w == 0 or h == 0 or w > 4096 or h > 4096:
        return None
    pix_data = data[mp+36:]
    try:
        if fmt_code in (16,):
            # DXT1
            pixels = _decode_dxt(pix_data, w, h, False)
        elif fmt_code in (18, 20):
            # DXT5
            pixels = _decode_dxt(pix_data, w, h, True)
        elif fmt_code == 6:
            # RGBA8 uncompressed (4 bytes per pixel)
            pixels = []
            for i in range(w * h):
                off = i * 4
                if off + 4 <= len(pix_data):
                    r, g, b, a = pix_data[off], pix_data[off+1], pix_data[off+2], pix_data[off+3]
                    pixels.append((r, g, b, a))
                else:
                    pixels.append((0, 0, 0, 255))
        else:
            return None  # Unsupported format (masks, specular, etc.)
        png = _pixels_to_png(pixels, w, h)
        return name, png
    except Exception:
        return None


def _parse_fsimplemodel(data, mesh_names=None):
    """Parse FSimpleModel/FSkeletalModel. Returns list of (mesh_name, shader_name, transform, model_name).
    mesh_names: set of known FMesh names for matching."""
    if len(data) < 12:
        return []
    name_len = struct.unpack('<I', data[4:8])[0]
    model_name = data[8:8+name_len].decode('ascii', errors='replace')
    mp = 8 + name_len

    results = []
    pos = mp
    while pos < len(data) - 8:
        try:
            slen = struct.unpack('<I', data[pos:pos+4])[0]
            if 5 < slen < 200 and pos + 4 + slen <= len(data):
                s = data[pos+4:pos+4+slen].decode('ascii', errors='replace')
                is_mesh_ref = ('Mesh' in s or
                               (mesh_names and s in mesh_names))
                if is_mesh_ref and '\x00' not in s[:slen] and 'Setup' not in s:
                    mesh_name = s
                    # Look for shader name after mesh name
                    npos = pos + 4 + slen
                    shader_name = ''
                    for skip in range(npos, min(npos+20, len(data)-4)):
                        sl2 = struct.unpack('<I', data[skip:skip+4])[0]
                        if 5 < sl2 < 200 and skip + 4 + sl2 <= len(data):
                            s2 = data[skip+4:skip+4+sl2].decode('ascii', errors='replace')
                            if 'Shader' in s2 and '\x00' not in s2[:sl2]:
                                shader_name = s2
                                # After shader: u32(0) + u8 display name + 4x4 matrix
                                tpos = skip + 4 + sl2
                                if tpos + 4 <= len(data) and struct.unpack('<I', data[tpos:tpos+4])[0] == 0:
                                    tpos += 4
                                # Skip u8-prefixed display name
                                if tpos < len(data):
                                    dn_len = data[tpos]
                                    tpos += 1 + dn_len
                                # Read 4x4 matrix (16 f32).
                                # FSkeletalModel has extra u32 before matrix.
                                # Detect: valid matrix has last row ≈ [0,0,0,1]
                                transform = None
                                for mat_skip in (0, 4):
                                    mp2 = tpos + mat_skip
                                    if mp2 + 64 <= len(data):
                                        mat = struct.unpack('<16f',
                                            data[mp2:mp2+64])
                                        # Check last row ≈ [0,0,0,1]
                                        if (abs(mat[12]) < 100 and
                                                abs(mat[13]) < 100 and
                                                abs(mat[14]) < 100 and
                                                abs(mat[15] - 1.0) < 0.01):
                                            transform = mat
                                            break
                                results.append((mesh_name, shader_name, transform, model_name))
                                pos = skip + 4 + sl2 + 80  # advance past shader+display+matrix
                                break
        except Exception:
            pass
        pos += 1
    return results


def _parse_fshader_textures(data, entries):
    """Parse FShaderGraph + FTextureParameterNode to find shader→texture mapping.
    Returns dict: shader_name → texture_name (diffuse)."""
    shader_textures = {}

    # Build index of entries by type+name
    tex_params = {}  # node_name -> texture_name
    shader_nodes = {}  # shader_name -> list of node_names

    for fn, dn, ft, offset, comp_len, grp in entries:
        if ft == 'FTextureParameterNode':
            blob = data[offset:offset+comp_len]
            try:
                md = zlib.decompress(blob) if blob[0] == 0x78 else blob
            except Exception:
                continue
            nl = struct.unpack('<I', md[4:8])[0]
            node_name = md[8:8+nl].decode('ascii', errors='replace')
            # Scan for texture name reference (contains "Diffuse" or "diffuse")
            for pos in range(8+nl, len(md)-8):
                try:
                    sl = struct.unpack('<I', md[pos:pos+4])[0]
                    if 5 < sl < 200 and pos+4+sl <= len(md):
                        s = md[pos+4:pos+4+sl].decode('ascii', errors='replace')
                        if ('Diffuse' in s or 'diffuse' in s or
                                'Texture' in s) and '\x00' not in s[:sl]:
                            tex_params[node_name] = s
                            break
                except Exception:
                    pass

        elif ft == 'FShaderGraph':
            blob = data[offset:offset+comp_len]
            try:
                md = zlib.decompress(blob) if blob[0] == 0x78 else blob
            except Exception:
                continue
            nl = struct.unpack('<I', md[4:8])[0]
            shader_name = md[8:8+nl].decode('ascii', errors='replace')
            # Collect child node references
            nodes = []
            for pos in range(8+nl, len(md)-8):
                try:
                    sl = struct.unpack('<I', md[pos:pos+4])[0]
                    if 5 < sl < 200 and pos+4+sl <= len(md):
                        s = md[pos+4:pos+4+sl].decode('ascii', errors='replace')
                        if s.startswith(shader_name.split('.')[0]) and '\x00' not in s[:sl]:
                            nodes.append(s)
                except Exception:
                    pass
            shader_nodes[shader_name] = nodes

    # Map shader → diffuse texture
    for shader_name, nodes in shader_nodes.items():
        for node in nodes:
            if node in tex_params:
                tex_name = tex_params[node]
                shader_textures[shader_name] = tex_name
                break

    return shader_textures


def _parse_color_constants(data, entries):
    """Parse FColorConstantNode entries. Returns dict: node_name → (r,g,b,a)."""
    colors = {}
    for fn, dn, ft, offset, comp_len, grp in entries:
        if ft != 'FColorConstantNode':
            continue
        try:
            blob = data[offset:offset+comp_len]
            md = zlib.decompress(blob) if blob[0] == 0x78 else blob
            nl = struct.unpack('<I', md[4:8])[0]
            node_name = md[8:8+nl].decode('ascii', errors='replace')
            mp = 8 + nl
            # Find wide-char color name + RGBA
            for off in range(mp, min(mp+40, len(md)-4), 4):
                cc = struct.unpack('<I', md[off:off+4])[0]
                if 1 < cc < 50:
                    valid = True
                    for i in range(cc):
                        c = struct.unpack('<I', md[off+4+i*4:off+8+i*4])[0]
                        if not (32 <= c < 128):
                            valid = False
                            break
                    if valid:
                        rgba_off = off + 4 + cc * 4
                        if rgba_off + 16 <= len(md):
                            r, g, b, a = struct.unpack('<ffff',
                                md[rgba_off:rgba_off+16])
                            colors[node_name] = (r, g, b, a)
                        break
        except Exception:
            pass
    return colors


class FSTModel:
    """Holds parsed data from an FST archive."""
    def __init__(self):
        self.name = ""
        self.meshes = []      # list of FSTMesh
        self.textures = {}    # name -> PNG bytes
        self.normal_maps = {} # name -> PNG bytes
        self.color_tints = {} # mesh_name -> (r, g, b, a)


class FSTMesh:
    """A single FMesh entry."""
    def __init__(self):
        self.name = ""
        self.positions = []   # list of (x, y, z)
        self.normals = []     # list of (nx, ny, nz)
        self.uvs = []         # list of (u, v)
        self.triangles = []   # list of (i0, i1, i2)
        self.texture_name = ""   # FTexture name for diffuse
        self.normal_map_name = ""  # FTexture name for normal map
        self.has_alpha = False     # texture has meaningful alpha


def parse_fst(filepath, verbose=False):
    """Parse an FST archive file. Returns an FSTModel."""
    with open(filepath, 'rb') as f:
        data = f.read()

    model = FSTModel()

    if data[0:4] != b'FAST':
        raise ValueError("Not a FAST archive file")

    num_files = struct.unpack('<I', data[16:20])[0]
    dir_offset = struct.unpack('<I', data[20:24])[0]

    # Parse codec strings + archive name
    pos = 28
    c1_len = struct.unpack('<I', data[pos:pos+4])[0]
    pos += 4 + c1_len
    c2_len = struct.unpack('<I', data[pos:pos+4])[0]
    pos += 4 + c2_len
    nm_len = data[pos]
    model.name = data[pos+1:pos+1+nm_len].decode('ascii', errors='replace')
    pos += 1 + nm_len

    if verbose:
        print(f"[FST] Archive: {model.name}, {num_files} entries, "
              f"dir at {dir_offset}", file=sys.stderr)

    # Parse directory — auto-detect grp_size (4 or 8 bytes)
    entries = _parse_directory(data, dir_offset, num_files)

    # Build mesh→shader→texture mapping + transforms + debris filtering
    mesh_shader = {}   # mesh_name → shader_name
    mesh_transform = {}  # mesh_name → 16-float tuple (4x4 row-major)
    debris_meshes = set()  # mesh names from debris/variant models
    shader_tex = {}    # shader_name → texture_name
    # Collect FMesh entry names for matching
    fmesh_names = set()
    for fn, dn, ft, offset, comp_len, grp in entries:
        if ft == 'FMesh':
            try:
                blob = data[offset:offset+comp_len]
                md2 = zlib.decompress(blob) if blob[0] == 0x78 else blob
                nl2 = struct.unpack('<I', md2[4:8])[0]
                fmesh_names.add(md2[8:8+nl2].decode('ascii', errors='replace'))
            except Exception:
                pass

    all_mesh_names = set()
    all_model_results = []
    for fn, dn, ft, offset, comp_len, grp in entries:
        if ft in ('FSimpleModel', 'FSkeletalModel'):
            try:
                blob = data[offset:offset+comp_len]
                md = zlib.decompress(blob) if blob[0] == 0x78 else blob
                results = _parse_fsimplemodel(md, fmesh_names)
                for mesh_name, shader_name, transform, model_name in results:
                    mesh_shader[mesh_name] = shader_name
                    if transform:
                        mesh_transform[mesh_name] = transform
                    all_mesh_names.add(mesh_name)
                    all_model_results.append((mesh_name, model_name))
            except Exception:
                pass

    # Filter debris and seasonal duplicates
    for mesh_name, model_name in all_model_results:
        if 'Debris' in model_name:
            debris_meshes.add(mesh_name)
        # Skip Winter variant if corresponding Summer mesh exists
        if 'Winter' in mesh_name:
            summer_name = mesh_name.replace('Winter', 'Summer')
            if summer_name in all_mesh_names:
                debris_meshes.add(mesh_name)

    shader_tex = _parse_fshader_textures(data, entries)

    # Parse color constants
    color_constants = _parse_color_constants(data, entries)

    # Parse FDefaultShaderNode for base diffuse colors (textureless meshes)
    for fn, dn, ft, offset, comp_len, grp in entries:
        if ft != 'FDefaultShaderNode':
            continue
        try:
            blob = data[offset:offset+comp_len]
            md = zlib.decompress(blob) if blob[0] == 0x78 else blob
            nl_d = struct.unpack('<I', md[4:8])[0]
            node_name = md[8:8+nl_d].decode('ascii', errors='replace')
            mp_d = 8 + nl_d
            for off_d in range(mp_d, min(mp_d+60, len(md)-4), 4):
                cc = struct.unpack('<I', md[off_d:off_d+4])[0]
                if 1 < cc < 50:
                    valid = True
                    for i in range(cc):
                        c = struct.unpack('<I', md[off_d+4+i*4:off_d+8+i*4])[0]
                        if not (32 <= c < 128):
                            valid = False
                            break
                    if valid:
                        rgba_off = off_d + 4 + cc * 4
                        if rgba_off + 16 <= len(md):
                            r, g, b, a = struct.unpack('<ffff',
                                md[rgba_off:rgba_off+16])
                            if max(r, g, b) > 0.01:
                                color_constants[node_name] = (r, g, b, a)
                        break
        except Exception:
            pass

    # Extract FTexture entries (diffuse + normal maps)
    needed_textures = set(shader_tex.values())
    for fn, dn, ft, offset, comp_len, grp in entries:
        if ft != 'FTexture':
            continue
        blob = data[offset:offset+comp_len]
        try:
            md = zlib.decompress(blob) if blob[0] == 0x78 else blob
            nl_t = struct.unpack('<I', md[4:8])[0]
            tex_name = md[8:8+nl_t].decode('ascii', errors='replace')
            mp_t = 8 + nl_t
            fmt_code = struct.unpack('<I', md[mp_t+24:mp_t+28])[0]

            # Only use DXT5 (fmt 18/20) normal maps — DXT1 has block artifacts
            is_normal = ('Normal' in tex_name and 'Diffuse' not in tex_name
                         and fmt_code in (18, 20))
            is_diffuse = ('Diffuse' in tex_name or
                          tex_name in needed_textures)

            if not (is_diffuse or is_normal):
                continue

            result = _parse_ftexture(md)
            if not result:
                continue
            _, png_bytes = result

            if is_normal:
                model.normal_maps[tex_name] = png_bytes
            else:
                model.textures[tex_name] = png_bytes
                # Check for alpha: DXT5 textures may have transparency
                # Only flag as alpha if there's a MIX of opaque and
                # transparent pixels (not just uniformly low alpha)
                if fmt_code in (18, 20):
                    pix_data = md[mp_t+36:]
                    has_opaque = False
                    has_transparent = False
                    for blk in range(min(128, len(pix_data)//16)):
                        a0 = pix_data[blk*16]
                        a1 = pix_data[blk*16+1]
                        if max(a0, a1) > 200:
                            has_opaque = True
                        if min(a0, a1) < 128:
                            has_transparent = True
                    if has_opaque and has_transparent:
                        model.textures[tex_name + '::alpha'] = True

            if verbose:
                w = struct.unpack('<I', md[mp_t+28:mp_t+32])[0]
                h = struct.unpack('<I', md[mp_t+32:mp_t+36])[0]
                kind = 'Normal' if is_normal else 'Diffuse'
                print(f"[FST]   {kind} '{tex_name}': {w}x{h} "
                      f"({len(png_bytes)}B PNG)",
                      file=sys.stderr)
        except Exception:
            pass

    # Extract and parse FMesh entries
    for fn, dn, ft, offset, comp_len, grp in entries:
        if ft != 'FMesh':
            continue
        try:
            blob = data[offset:offset+comp_len]
            if len(blob) > 0 and blob[0] == 0x78:
                mesh_data = zlib.decompress(blob)
            else:
                mesh_data = blob

            mesh = _parse_fmesh(mesh_data, verbose)
            if mesh and mesh.positions:
                # Skip debris/broken-state meshes
                if mesh.name in debris_meshes:
                    continue
                # Apply transform from FSimpleModel
                xform = mesh_transform.get(mesh.name)
                if xform and any(abs(xform[i] - (1.0 if i % 5 == 0 else 0.0)) > 0.001
                                 for i in range(16)):
                    # Non-identity transform: apply as row-major 4x4
                    new_pos = []
                    for px, py, pz in mesh.positions:
                        nx = px*xform[0] + py*xform[4] + pz*xform[8] + xform[12]
                        ny = px*xform[1] + py*xform[5] + pz*xform[9] + xform[13]
                        nz = px*xform[2] + py*xform[6] + pz*xform[10] + xform[14]
                        new_pos.append((nx, ny, nz))
                    mesh.positions = new_pos
                    # Transform normals (rotation only, no translation)
                    if mesh.normals:
                        new_norm = []
                        for nnx, nny, nnz in mesh.normals:
                            rx = nnx*xform[0] + nny*xform[4] + nnz*xform[8]
                            ry = nnx*xform[1] + nny*xform[5] + nnz*xform[9]
                            rz = nnx*xform[2] + nny*xform[6] + nnz*xform[10]
                            rl = math.sqrt(rx*rx+ry*ry+rz*rz)
                            if rl > 1e-10:
                                new_norm.append((rx/rl, ry/rl, rz/rl))
                            else:
                                new_norm.append((0, 1, 0))
                        mesh.normals = new_norm
                # Map mesh → texture via shader
                shader = mesh_shader.get(mesh.name, '')
                tex = shader_tex.get(shader, '')
                if tex and tex in model.textures:
                    mesh.texture_name = tex
                else:
                    # Try matching by name: find best texture for this mesh.
                    # Mesh name: Prefix.VariantModel.MeshName
                    # Texture:   Prefix.VariantDiffuse
                    # Extract model variant word (e.g., "Aluminium" from
                    # "WeightAluminiumModel") for precise matching.
                    mesh_prefix = mesh.name.split('.')[0]
                    name_parts = mesh.name.split('.')
                    model_part = name_parts[1] if len(name_parts) > 1 else ''
                    # Strip "Model" suffix to get variant identifier
                    variant = (model_part[len(mesh_prefix):]
                               .replace('Model', '')
                               if model_part.startswith(mesh_prefix)
                               else model_part.replace('Model', ''))

                    candidates = []
                    for tname in model.textures:
                        if tname.endswith('::alpha'):
                            continue
                        if 'Diffuse' not in tname:
                            continue
                        tex_prefix = tname.split('.')[0]
                        if mesh_prefix != tex_prefix:
                            continue
                        # Extract texture variant (e.g., "Aluminium"
                        # from "WeightAluminiumDiffuse")
                        tex_base = tname.split('.')[-1]
                        tex_variant = (tex_base[len(mesh_prefix):]
                                       .replace('Diffuse', '')
                                       if tex_base.startswith(mesh_prefix)
                                       else tex_base.replace('Diffuse', ''))
                        # Exact variant match scores highest
                        if variant and variant == tex_variant:
                            candidates.append((2, tname))
                        elif not variant and not tex_variant:
                            candidates.append((2, tname))
                        elif variant and tex_variant and (
                                variant in tex_variant or
                                tex_variant in variant):
                            candidates.append((1, tname))
                        else:
                            candidates.append((0, tname))

                    if candidates:
                        candidates.sort(key=lambda x: -x[0])
                        mesh.texture_name = candidates[0][1]
                # Also find normal map by name pattern
                mesh_prefix = mesh.name.split('.')[0]
                for nname in model.normal_maps:
                    if mesh_prefix == nname.split('.')[0]:
                        mesh.normal_map_name = nname
                        break
                # Check alpha
                if mesh.texture_name:
                    mesh.has_alpha = (mesh.texture_name + '::alpha') in model.textures
                # Store color tint from color/shader constants
                for cc_name, rgba in color_constants.items():
                    cc_prefix = cc_name.split('.')[0]
                    if mesh_prefix == cc_prefix:
                        model.color_tints[mesh.name] = rgba
                        break
                model.meshes.append(mesh)
        except Exception as e:
            if verbose:
                print(f"[FST] Error parsing FMesh {dn}/{fn}: {e}",
                      file=sys.stderr)

    if verbose:
        total_verts = sum(len(m.positions) for m in model.meshes)
        total_tris = sum(len(m.triangles) for m in model.meshes)
        print(f"[FST] Parsed {len(model.meshes)} meshes, "
              f"{total_verts} verts, {total_tris} tris", file=sys.stderr)

    return model


def _parse_directory(data, dir_offset, num_files):
    """Parse FST directory. Auto-detects grp_size (4 or 8 bytes)."""
    # Directory may be zlib-compressed
    dir_data = data[dir_offset:]
    if len(dir_data) > 0 and dir_data[0] == 0x78:
        dir_data = zlib.decompress(dir_data)

    for grp_size in [8, 4]:
        try:
            entries = []
            dpos = 0
            for i in range(num_files):
                if dpos + 4 > len(dir_data):
                    raise IndexError("EOF in directory")
                fn_len = struct.unpack('<I', dir_data[dpos:dpos+4])[0]
                if fn_len > 10000:
                    raise ValueError(f"fn_len {fn_len} too large")
                dpos += 4
                fn = dir_data[dpos:dpos+fn_len].decode('ascii', errors='replace')
                dpos += fn_len

                dn_len = struct.unpack('<I', dir_data[dpos:dpos+4])[0]
                if dn_len > 10000:
                    raise ValueError(f"dn_len {dn_len} too large")
                dpos += 4
                dn = dir_data[dpos:dpos+dn_len].decode('ascii', errors='replace')
                dpos += dn_len

                tl = dir_data[dpos]
                dpos += 1
                ft = dir_data[dpos:dpos+tl].decode('ascii', errors='replace')
                dpos += tl

                offset, comp_len = struct.unpack('<QQ', dir_data[dpos:dpos+16])
                dpos += 16

                grp = struct.unpack('<I', dir_data[dpos:dpos+4])[0]
                dpos += grp_size

                entries.append((fn, dn, ft, offset, comp_len, grp))

            return entries
        except (struct.error, IndexError, ValueError):
            continue

    raise ValueError("Failed to parse FST directory with either grp_size")


def _parse_fmesh(data, verbose=False):
    """Parse an FMesh binary blob. Returns an FSTMesh or None."""
    if len(data) < 12:
        return None

    mesh = FSTMesh()

    # Header: u32(0) + u32(name_len) + name
    name_len = struct.unpack('<I', data[4:8])[0]
    if name_len > len(data) - 8:
        return None
    mesh.name = data[8:8+name_len].decode('ascii', errors='replace')

    # Metadata: 24 bytes after name
    mpos = 8 + name_len
    if mpos + 24 > len(data):
        return None

    vc = struct.unpack('<I', data[mpos+16:mpos+20])[0]
    tc = struct.unpack('<I', data[mpos+20:mpos+24])[0]

    if vc == 0 or tc == 0:
        return None
    if vc > 1000000 or tc > 1000000:
        return None

    # Positions: vc × 12 bytes (f32 LE xyz)
    vstart = mpos + 24
    vend = vstart + vc * 12
    if vend > len(data):
        return None

    for i in range(vc):
        off = vstart + i * 12
        x, y, z = struct.unpack('<fff', data[off:off+12])
        mesh.positions.append((x, y, z))

    # Triangle indices: tc × 3 × u32 LE, directly after positions
    idx_start = vend
    idx_end = idx_start + tc * 12
    if idx_end > len(data):
        return None

    for t in range(tc):
        off = idx_start + t * 12
        i0, i1, i2 = struct.unpack('<III', data[off:off+12])
        if max(i0, i1, i2) < vc:
            mesh.triangles.append((i0, i1, i2))

    # Adjacency block: deterministic structure after triangle indices.
    # Format: u32(adj_count) + adj_count × 12B entries + 24B trailer
    # Trailer[4] = normal_count, Trailer[5] = 0 (terminator)
    # Total size: adj_count * 12 + 28 bytes
    norm_count = 0
    norm_start = None
    if idx_end + 4 <= len(data):
        adj_count = struct.unpack('<I', data[idx_end:idx_end+4])[0]
        if adj_count < 1000:
            adj_block_size = adj_count * 12 + 28
            trailer_start = idx_end + 4 + adj_count * 12
            if trailer_start + 24 <= len(data):
                norm_count = struct.unpack('<I',
                    data[trailer_start+16:trailer_start+20])[0]
                zero_check = struct.unpack('<I',
                    data[trailer_start+20:trailer_start+24])[0]
                if zero_check == 0 and 0 < norm_count < 1000000:
                    norm_start = idx_end + adj_block_size

    # Read nc normals and UVs, then find nc-space triangle indices
    # to correctly map normals/UVs to positions per triangle corner.
    if norm_start is not None and norm_count > 0:
        nc = norm_count

        # Read ALL nc normals
        all_normals = []
        for i in range(nc):
            off = norm_start + i * 12
            if off + 12 <= len(data):
                all_normals.append(struct.unpack('<fff', data[off:off+12]))

        # UVs: after nc normals + 16B header.
        # UV buffer has max(nc, evc) entries (evc from header[2]).
        uv_header_off = norm_start + nc * 12
        all_uvs = []
        uv_data_start = None
        evc_pre = 0
        if uv_header_off + 16 <= len(data):
            evc_pre = struct.unpack('<I', data[uv_header_off+8:uv_header_off+12])[0]
            uv_data_start = uv_header_off + 16
            uv_count = max(nc, evc_pre) if 0 < evc_pre < 1000000 else nc
            for i in range(uv_count):
                off = uv_data_start + i * 8
                if off + 8 <= len(data):
                    all_uvs.append(struct.unpack('<ff', data[off:off+8]))

        # Get evc (expanded UV vertex count) from UV header
        evc = 0
        if uv_header_off + 12 <= len(data):
            evc = struct.unpack('<I', data[uv_header_off+8:uv_header_off+12])[0]

        if (len(all_normals) == nc and len(all_uvs) >= nc and
                uv_data_start is not None):
            # Find nc-space triangle indices after the tangent section.
            #
            # Tangent section structure (two variants):
            #
            # Variant A: Subsection headers present
            #   One or more subsections with header (type, 2, count, 0)
            #   + count*12 bytes of f32 triplet data. Types: 4, 9, 0.
            #   Optional type-7 skin weight block: (7, 1, vc, 0)
            #   + vc*20 bytes + 16 byte trailer.
            #   NC-space indices follow immediately after last subsection.
            #
            # Variant B: No subsection headers (raw tangent float data)
            #   Variable-length raw f32 tangent/binormal vectors.
            #   May contain an embedded type-7 block.
            #   NC-space indices follow the tangent data.
            #
            after_uv = uv_data_start + len(all_uvs) * 8
            nc_tris = None
            scan_off = after_uv  # track position for evc search

            def _validate_nc_block(off):
                """Check if tc triangles at off are valid nc indices."""
                if off + tc * 12 > len(data):
                    return False
                for t in [0, tc//4, tc//2, 3*tc//4, tc-1]:
                    o = off + t * 12
                    if o + 12 > len(data):
                        return False
                    if max(struct.unpack('<III', data[o:o+12])) >= nc:
                        return False
                # Full validation
                for t in range(tc):
                    o = off + t * 12
                    if max(struct.unpack('<III', data[o:o+12])) >= nc:
                        return False
                return True

            # Strategy 1: Parse subsection headers deterministically
            pos = after_uv
            parsed_ok = False
            if pos + 16 <= len(data):
                h = struct.unpack('<IIII', data[pos:pos+16])
                # Check for standard tangent subsection: (type, 2, count, 0)
                if (h[1] == 2 and h[3] == 0 and
                        0 < h[2] < 1000000 and h[0] < 100):
                    # Variant A: parse all standard subsections
                    while pos + 16 <= len(data):
                        sh = struct.unpack('<IIII', data[pos:pos+16])
                        if (sh[1] == 2 and sh[3] == 0 and
                                0 < sh[2] < 1000000 and sh[0] < 100):
                            pos += 16 + sh[2] * 12
                        else:
                            break
                    # Check for type-7 skin weight block: (7, 1, vc, 0)
                    if pos + 16 <= len(data):
                        t7 = struct.unpack('<IIII', data[pos:pos+16])
                        if (t7[0] == 7 and t7[1] == 1 and
                                t7[2] == vc and t7[3] == 0):
                            # Type-7: header(16) + vc*20 data + 16 trailer
                            pos += 16 + vc * 20 + 16
                    # Validate nc indices at pos
                    if _validate_nc_block(pos):
                        nc_tris = [struct.unpack('<III',
                            data[pos+t*12:pos+t*12+12])
                            for t in range(tc)]
                        scan_off = pos
                        parsed_ok = True

            # Strategy 2: Look for type-7 header in raw tangent data
            if not parsed_ok:
                # Search for (7, 1, vc, 0) pattern
                type7_sig = struct.pack('<IIII', 7, 1, vc, 0)
                search_limit = min(len(data) - 16,
                                   after_uv + 1000000)
                t7_pos = data.find(type7_sig, after_uv, search_limit)
                if t7_pos >= 0:
                    # Found type-7: skip header + vc*20 + 16B trailer
                    nc_pos = t7_pos + 16 + vc * 20 + 16
                    if _validate_nc_block(nc_pos):
                        nc_tris = [struct.unpack('<III',
                            data[nc_pos+t*12:nc_pos+t*12+12])
                            for t in range(tc)]
                        scan_off = nc_pos
                        parsed_ok = True

            # Strategy 3: Forward scan for nc-space index block
            # The transition from float tangent data to integer indices
            # is structurally unambiguous: float bit patterns for unit
            # vectors have large u32 values, while indices are < nc.
            if not parsed_ok:
                for scan_off in range(after_uv,
                                      len(data) - tc * 12, 4):
                    if not _validate_nc_block(scan_off):
                        continue
                    nc_tris = [struct.unpack('<III',
                        data[scan_off+t*12:scan_off+t*12+12])
                        for t in range(tc)]
                    break

            if nc_tris:
                # Find evc-space index block (for UVs) — the SECOND
                # index block after the nc-space block.
                # UV header[2] = evc = number of valid UV entries.
                evc = struct.unpack('<I',
                    data[uv_header_off+8:uv_header_off+12])[0]
                evc_tris = None
                if evc > 0 and evc != nc:
                    # Search after the nc block for evc-space indices
                    evc_search_start = scan_off + tc * 12
                    for evc_scan in range(evc_search_start,
                            min(len(data), evc_search_start + nc*100),
                            4):
                        i0, i1, i2 = struct.unpack('<III',
                            data[evc_scan:evc_scan+12])
                        if max(i0, i1, i2) >= evc:
                            continue
                        ok2 = True
                        for t in [0, tc//4, tc//2, tc-1]:
                            off2 = evc_scan + t*12
                            if off2+12 > len(data):
                                ok2 = False; break
                            vals = struct.unpack('<III',
                                data[off2:off2+12])
                            if max(vals) >= evc:
                                ok2 = False; break
                        if ok2:
                            full2 = all(max(struct.unpack('<III',
                                data[evc_scan+t*12:evc_scan+t*12+12])
                                ) < evc for t in range(tc))
                            if full2:
                                evc_tris = [struct.unpack('<III',
                                    data[evc_scan+t*12:evc_scan+t*12+12])
                                    for t in range(tc)]
                                break

                # Build shared-vertex mesh when evc_tris available,
                # otherwise per-triangle-corner fallback.
                compact_pos = list(mesh.positions)
                compact_tris = list(mesh.triangles)
                mesh.positions = []
                mesh.normals = []
                mesh.uvs = []
                mesh.triangles = []

                # Check if shared-vertex build is possible (zero remap conflicts)
                use_shared = False
                evc_to_compact = {}
                evc_to_nc = {}
                if evc_tris:
                    remap_conflicts = 0
                    for t in range(tc):
                        for j in range(3):
                            ei = evc_tris[t][j]
                            ci = compact_tris[t][j]
                            ni = nc_tris[t][j]
                            if ei in evc_to_compact:
                                if evc_to_compact[ei] != ci:
                                    remap_conflicts += 1
                            else:
                                evc_to_compact[ei] = ci
                                evc_to_nc[ei] = ni
                    use_shared = remap_conflicts == 0

                if evc_tris and use_shared:
                    # Build shared vertex buffer indexed by evc
                    max_evc = max(max(t) for t in evc_tris) + 1
                    for i in range(max_evc):
                        ci = evc_to_compact.get(i, 0)
                        ni = evc_to_nc.get(i, 0)
                        mesh.positions.append(
                            compact_pos[ci] if ci < len(compact_pos)
                            else (0, 0, 0))
                        mesh.normals.append(
                            all_normals[ni] if ni < len(all_normals)
                            else (0, 1, 0))
                        if i < len(all_uvs):
                            mesh.uvs.append(all_uvs[i])
                        else:
                            mesh.uvs.append((0, 0))

                    for i0, i1, i2 in evc_tris:
                        if max(i0, i1, i2) < max_evc:
                            mesh.triangles.append((i0, i1, i2))
                else:
                    # Per-triangle-corner: duplicate vertices per triangle
                    # Use evc indices for UVs when available, nc otherwise
                    uv_src = evc_tris if evc_tris else None

                    for t in range(tc):
                        ct = compact_tris[t]
                        nt = nc_tris[t]
                        ut = uv_src[t] if uv_src else nt
                        fb = len(mesh.positions)
                        valid = True
                        for j in range(3):
                            ci, ni, ui = ct[j], nt[j], ut[j]
                            if (ci < len(compact_pos) and ni < nc
                                    and ui < len(all_uvs)):
                                mesh.positions.append(compact_pos[ci])
                                mesh.normals.append(all_normals[ni])
                                mesh.uvs.append(all_uvs[ui])
                            else:
                                valid = False
                        if valid:
                            mesh.triangles.append((fb, fb+1, fb+2))
            else:
                # No nc-space indices found.
                # If evc > nc, try finding evc block directly for UVs
                if evc > 0 and evc != nc:
                    evc_tris_only = None
                    for evc_scan in range(after_uv,
                            min(len(data), after_uv + max(nc, evc)*100 + tc*12),
                            4):
                        i0, i1, i2 = struct.unpack('<III',
                            data[evc_scan:evc_scan+12])
                        if max(i0, i1, i2) >= evc:
                            continue
                        ok3 = True
                        for t in [0, tc//4, tc//2, tc-1]:
                            off3 = evc_scan + t*12
                            if off3+12 > len(data): ok3 = False; break
                            vals = struct.unpack('<III', data[off3:off3+12])
                            if max(vals) >= evc: ok3 = False; break
                        if not ok3:
                            continue
                        full3 = all(max(struct.unpack('<III',
                            data[evc_scan+t*12:evc_scan+t*12+12])
                            ) < evc for t in range(tc))
                        if full3:
                            evc_tris_only = [struct.unpack('<III',
                                data[evc_scan+t*12:evc_scan+t*12+12])
                                for t in range(tc)]
                            break

                    if evc_tris_only:
                        compact_pos = list(mesh.positions)
                        compact_tris = list(mesh.triangles)
                        mesh.positions = []
                        mesh.normals = []
                        mesh.uvs = []
                        mesh.triangles = []
                        for t in range(tc):
                            ct = compact_tris[t]
                            ut = evc_tris_only[t]
                            fb = len(mesh.positions)
                            valid = True
                            for j in range(3):
                                ci = ct[j]
                                ui = ut[j]
                                if ci < len(compact_pos) and ui < len(all_uvs):
                                    mesh.positions.append(compact_pos[ci])
                                    if ci < len(all_normals):
                                        mesh.normals.append(all_normals[ci])
                                    else:
                                        mesh.normals.append((0, 1, 0))
                                    mesh.uvs.append(all_uvs[ui])
                                else:
                                    valid = False
                            if valid:
                                mesh.triangles.append((fb, fb+1, fb+2))
                    else:
                        mesh.normals = list(all_normals[:vc])
                        mesh.uvs = list(all_uvs[:vc])
                else:
                    mesh.normals = list(all_normals[:vc])
                    mesh.uvs = list(all_uvs[:vc])

    if verbose:
        print(f"[FST]   FMesh '{mesh.name}': {vc}v {tc}t "
              f"normals={'yes' if mesh.normals else 'no'} "
              f"uvs={'yes' if mesh.uvs else 'no'}",
              file=sys.stderr)

    return mesh


def convert_to_glb(model, output_path, verbose=False):
    """Convert an FSTModel to GLB format."""
    builder = GLBBuilder(verbose=verbose)

    if not model.meshes:
        glb_data = builder.build_glb(generator="poly2glb-fst")
        with open(output_path, 'wb') as f:
            f.write(glb_data)
        return

    # Build materials: one per unique texture, plus default
    tex_to_mat = {}  # texture_name -> material_idx
    default_mat = len(builder.materials_gltf)
    builder.materials_gltf.append({
        "pbrMetallicRoughness": {
            "baseColorFactor": [0.6, 0.6, 0.6, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.8
        },
        "doubleSided": True
    })

    def _add_png_texture(png_bytes):
        """Add PNG as image+texture in glTF, return texture index."""
        buf_offset = len(builder.buffer_data)
        builder.buffer_data.extend(png_bytes)
        bv_idx = len(builder.buffer_views)
        builder.buffer_views.append({
            "buffer": 0,
            "byteOffset": buf_offset,
            "byteLength": len(png_bytes),
        })
        img_idx = len(builder.images)
        builder.images.append({
            "bufferView": bv_idx,
            "mimeType": "image/png",
        })
        tex_idx = len(builder.textures)
        builder.textures.append({"source": img_idx})
        return tex_idx

    # Add normal map textures
    normal_tex_indices = {}  # name -> glTF texture index
    for nmap_name, png_bytes in model.normal_maps.items():
        normal_tex_indices[nmap_name] = _add_png_texture(png_bytes)

    # Add diffuse textures and build materials
    for tex_name, png_bytes in model.textures.items():
        if tex_name.endswith('::alpha'):
            continue  # skip alpha flag entries
        diffuse_tex_idx = _add_png_texture(png_bytes)

        # Build PBR material
        pbr = {
            "baseColorTexture": {"index": diffuse_tex_idx},
            "metallicFactor": 0.0,
            "roughnessFactor": 0.8
        }

        # Apply color tint from FColorConstantNode
        # Only apply when alpha > 0 (alpha=0 means transparent/special)
        tex_prefix = tex_name.split('.')[0]
        for mesh_name, rgba in model.color_tints.items():
            if tex_prefix in mesh_name:
                r, g, b, a = rgba
                if a > 0.01 and max(r, g, b) > 0.01:
                    pbr["baseColorFactor"] = [
                        min(1.0, r), min(1.0, g), min(1.0, b), 1.0]
                break

        mat = {
            "pbrMetallicRoughness": pbr,
            "doubleSided": True
        }

        # Add normal map if available
        for nmap_name, nmap_tex_idx in normal_tex_indices.items():
            if tex_prefix == nmap_name.split('.')[0]:
                mat["normalTexture"] = {"index": nmap_tex_idx}
                break

        # Alpha transparency for DXT5 textures with alpha
        has_alpha = (tex_name + '::alpha') in model.textures
        if has_alpha:
            mat["alphaMode"] = "BLEND"

        mat_idx = len(builder.materials_gltf)
        builder.materials_gltf.append(mat)
        tex_to_mat[tex_name] = mat_idx

    total_tris = 0
    for mesh in model.meshes:
        if not mesh.positions or not mesh.triangles:
            continue

        has_normals = len(mesh.normals) == len(mesh.positions)

        grp_positions = []
        grp_normals = []
        grp_indices = []

        if has_normals:
            # Shared vertices with per-vertex normals
            grp_positions = list(mesh.positions)
            grp_normals = list(mesh.normals)
            for i0, i1, i2 in mesh.triangles:
                grp_indices.extend([i0, i1, i2])
        else:
            # Flat shading: duplicate vertices per face
            for i0, i1, i2 in mesh.triangles:
                v0 = mesh.positions[i0]
                v1 = mesh.positions[i1]
                v2 = mesh.positions[i2]
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
                fb = len(grp_positions)
                grp_positions.extend([v0, v1, v2])
                grp_normals.extend([(nx, ny, nz)] * 3)
                grp_indices.extend([fb, fb+1, fb+2])

        # Choose material
        mesh_mat = tex_to_mat.get(mesh.texture_name, default_mat)
        # For untextured meshes, check color tints/shader defaults
        if not mesh.texture_name and mesh.name in model.color_tints:
            r, g, b, a = model.color_tints[mesh.name]
            if max(r, g, b) > 0.01:
                tint_key = f'_tint_{r:.2f}_{g:.2f}_{b:.2f}'
                if tint_key not in tex_to_mat:
                    mi = len(builder.materials_gltf)
                    builder.materials_gltf.append({
                        "pbrMetallicRoughness": {
                            "baseColorFactor": [r, g, b, 1.0],
                            "metallicFactor": 0.0,
                            "roughnessFactor": 0.8
                        },
                        "doubleSided": True
                    })
                    tex_to_mat[tint_key] = mi
                mesh_mat = tex_to_mat[tint_key]

        if grp_positions and grp_indices:
            has_uvs = (len(mesh.uvs) == len(mesh.positions) and
                       mesh.texture_name and has_normals)
            prim = builder.build_primitive(grp_positions, grp_normals,
                                           grp_indices, material_idx=mesh_mat)
            # Add UVs to the primitive if we have them
            if prim and has_uvs:
                uv_data = bytearray()
                for u, v in mesh.uvs:
                    uv_data += struct.pack('<ff', u, v)
                uv_bv = builder.add_buffer_view(uv_data, target=34962)
                uv_acc = builder.add_accessor(uv_bv, 5126,
                                               len(mesh.uvs), "VEC2")
                prim["attributes"]["TEXCOORD_0"] = uv_acc
            if prim:
                total_tris += len(grp_indices) // 3
                mesh_idx = len(builder.meshes)
                builder.meshes.append({"primitives": [prim]})
                node_idx = len(builder.nodes)
                builder.nodes.append({"mesh": mesh_idx})
                builder.scene_nodes.append(node_idx)

    glb_data = builder.build_glb(generator="poly2glb-fst")
    with open(output_path, 'wb') as f:
        f.write(glb_data)

    if verbose:
        print(f"[FST] Output: {total_tris} tris, "
              f"{len(model.meshes)} meshes", file=sys.stderr)

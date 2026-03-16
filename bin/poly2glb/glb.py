# Vibe coded by Claude
"""
Generic GLB (glTF 2.0 Binary) file builder.

Provides reusable infrastructure for constructing GLB files from any 3D source:
  - Buffer/accessor management
  - glTF JSON structure assembly
  - GLB binary packaging (header + JSON chunk + BIN chunk)
  - Ear-clipping triangulation for concave polygons
  - Bridge-edge hole merging for multi-loop faces
  - Primitive building (positions + normals + indices)
"""

import struct
import json
import math


class GLBBuilder:
    """Builds a GLB (glTF 2.0 Binary) file.

    Subclass or compose with this to build converter-specific GLB output.
    Manages buffers, accessors, meshes, nodes, materials, textures.
    """

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.buffer_data = bytearray()
        self.buffer_views = []
        self.accessors = []
        self.meshes = []
        self.nodes = []
        self.materials_gltf = []
        self.textures = []
        self.images = []
        self.samplers = []
        self.scene_nodes = []

    def log(self, msg):
        if self.verbose:
            import sys
            print(f"[GLB] {msg}", file=sys.stderr)

    def add_buffer_view(self, data, target=None):
        """Add data to the buffer and create a buffer view. Returns bv index."""
        # Align to 4 bytes
        while len(self.buffer_data) % 4 != 0:
            self.buffer_data.append(0)

        offset = len(self.buffer_data)
        self.buffer_data.extend(data)

        bv = {
            "buffer": 0,
            "byteOffset": offset,
            "byteLength": len(data)
        }
        if target:
            bv["target"] = target

        idx = len(self.buffer_views)
        self.buffer_views.append(bv)
        return idx

    def add_accessor(self, buffer_view, component_type, count, acc_type,
                     min_val=None, max_val=None):
        """Add an accessor. Returns accessor index."""
        acc = {
            "bufferView": buffer_view,
            "componentType": component_type,
            "count": count,
            "type": acc_type
        }
        if min_val is not None:
            acc["min"] = min_val
        if max_val is not None:
            acc["max"] = max_val
        idx = len(self.accessors)
        self.accessors.append(acc)
        return idx

    def add_image_from_data(self, image_data):
        """Add an image from raw bytes (PNG/JPEG). Returns image index."""
        if image_data[:4] == b'\x89PNG':
            mime = "image/png"
        elif image_data[:2] == b'\xff\xd8':
            mime = "image/jpeg"
        else:
            mime = "image/png"

        bv_idx = self.add_buffer_view(image_data)
        idx = len(self.images)
        self.images.append({
            "bufferView": bv_idx,
            "mimeType": mime
        })
        return idx

    def add_texture(self, image_index, sampler_index=0):
        """Add a texture referencing an image. Returns texture index."""
        if not self.samplers:
            self.samplers.append({
                "magFilter": 9729,   # LINEAR
                "minFilter": 9987,   # LINEAR_MIPMAP_LINEAR
                "wrapS": 10497,      # REPEAT
                "wrapT": 10497
            })
        idx = len(self.textures)
        self.textures.append({
            "sampler": sampler_index,
            "source": image_index
        })
        return idx

    def build_primitive(self, positions, normals, indices, material_idx=None):
        """Build a glTF primitive dict from position/normal/index arrays.

        Args:
            positions: list of (x, y, z) tuples
            normals:   list of (nx, ny, nz) tuples (same length as positions)
            indices:   flat list of triangle vertex indices
            material_idx: optional glTF material index

        Returns:
            dict: glTF primitive, or None if empty
        """
        if not positions or not indices:
            return None

        # Calculate bounds
        min_pos = [min(p[i] for p in positions) for i in range(3)]
        max_pos = [max(p[i] for p in positions) for i in range(3)]

        # Write position data
        pos_data = bytearray()
        for p in positions:
            pos_data += struct.pack('<fff', *p)
        pos_bv = self.add_buffer_view(pos_data, target=34962)  # ARRAY_BUFFER

        pos_acc = self.add_accessor(pos_bv, 5126, len(positions), "VEC3",
                                    min_val=min_pos, max_val=max_pos)

        # Write normal data
        norm_data = bytearray()
        for n in normals:
            norm_data += struct.pack('<fff', *n)
        norm_bv = self.add_buffer_view(norm_data, target=34962)

        norm_acc = self.add_accessor(norm_bv, 5126, len(normals), "VEC3")

        # Write index data
        if max(indices) <= 65535:
            idx_data = bytearray()
            for i in indices:
                idx_data += struct.pack('<H', i)
            comp_type = 5123  # UNSIGNED_SHORT
        else:
            idx_data = bytearray()
            for i in indices:
                idx_data += struct.pack('<I', i)
            comp_type = 5125  # UNSIGNED_INT

        idx_bv = self.add_buffer_view(idx_data, target=34963)  # ELEMENT_ARRAY_BUFFER
        idx_acc = self.add_accessor(idx_bv, comp_type, len(indices), "SCALAR")

        prim = {
            "attributes": {
                "POSITION": pos_acc,
                "NORMAL": norm_acc
            },
            "indices": idx_acc,
            "mode": 4  # TRIANGLES
        }

        if material_idx is not None and material_idx >= 0:
            prim["material"] = material_idx

        return prim

    def build_gltf_json(self, generator="poly2glb"):
        """Build the glTF JSON structure from current state."""
        gltf = {
            "asset": {
                "generator": generator,
                "version": "2.0"
            }
        }

        if self.scene_nodes:
            gltf["scenes"] = [{"nodes": self.scene_nodes}]
            gltf["scene"] = 0

        if self.nodes:
            gltf["nodes"] = self.nodes

        if self.meshes:
            gltf["meshes"] = self.meshes

        if self.materials_gltf:
            gltf["materials"] = self.materials_gltf

        if self.accessors:
            gltf["accessors"] = self.accessors

        if self.buffer_views:
            gltf["bufferViews"] = self.buffer_views

        if self.buffer_data:
            padded_size = len(self.buffer_data)
            while padded_size % 4 != 0:
                padded_size += 1
            gltf["buffers"] = [{"byteLength": padded_size}]

        if self.textures:
            gltf["textures"] = self.textures

        if self.images:
            gltf["images"] = self.images

        if self.samplers:
            gltf["samplers"] = self.samplers

        return gltf

    def build_glb(self, generator="poly2glb"):
        """Assemble the final GLB binary from current state.

        Returns:
            bytes: Complete GLB file content
        """
        # Pad buffer to 4-byte alignment
        while len(self.buffer_data) % 4 != 0:
            self.buffer_data.append(0)

        gltf = self.build_gltf_json(generator)
        json_bytes = json.dumps(gltf, separators=(',', ':')).encode('utf-8')

        # Pad JSON to 4-byte alignment
        while len(json_bytes) % 4 != 0:
            json_bytes += b' '

        bin_length = len(self.buffer_data)
        json_length = len(json_bytes)
        total_length = 12 + 8 + json_length + 8 + bin_length

        glb = bytearray()
        # Header
        glb += struct.pack('<I', 0x46546C67)  # 'glTF'
        glb += struct.pack('<I', 2)            # version 2
        glb += struct.pack('<I', total_length)
        # JSON chunk
        glb += struct.pack('<I', json_length)
        glb += struct.pack('<I', 0x4E4F534A)  # 'JSON'
        glb += json_bytes
        # BIN chunk
        glb += struct.pack('<I', bin_length)
        glb += struct.pack('<I', 0x004E4942)  # 'BIN\0'
        glb += self.buffer_data

        return bytes(glb)


# ---------------------------------------------------------------------------
# Geometry utilities (ear-clipping, hole merging, convexity, winding)
# ---------------------------------------------------------------------------

def merge_polygon_holes(outer, holes, positions, face_normal):
    """Merge hole polygons into outer boundary using bridge edges.

    For each hole, find the closest vertex pair between the current boundary
    and the hole, then insert a zero-width bridge connecting them.

    Args:
        outer: list of vertex indices for outer boundary
        holes: list of lists of vertex indices for each hole
        positions: global positions array [(x,y,z), ...]
        face_normal: (nx, ny, nz) face normal for 2D projection

    Returns:
        list of vertex indices for the merged polygon
    """
    ax = abs(face_normal[0])
    ay = abs(face_normal[1])
    az = abs(face_normal[2])
    if ax >= ay and ax >= az:
        u_axis, v_axis = 1, 2
    elif ay >= ax and ay >= az:
        u_axis, v_axis = 0, 2
    else:
        u_axis, v_axis = 0, 1

    def pos2d(idx):
        p = positions[idx]
        return (p[u_axis], p[v_axis])

    def signed_area_2d(ring):
        a = 0
        pts = [pos2d(vi) for vi in ring]
        for j in range(len(pts)):
            k = (j + 1) % len(pts)
            a += pts[j][0] * pts[k][1] - pts[k][0] * pts[j][1]
        return a

    # Ensure outer and holes have opposite winding
    outer_area = signed_area_2d(outer)
    for i in range(len(holes)):
        hole_area = signed_area_2d(holes[i])
        if (outer_area > 0 and hole_area > 0) or \
           (outer_area < 0 and hole_area < 0):
            holes[i] = list(reversed(holes[i]))

    merged = list(outer)

    # Sort holes by rightmost vertex X coord (descending)
    hole_order = sorted(range(len(holes)), key=lambda hi:
        max(pos2d(vi)[0] for vi in holes[hi]), reverse=True)

    for hi in hole_order:
        hole = holes[hi]
        if len(hole) < 3:
            continue

        best_dist = float('inf')
        best_mi = 0
        best_hi = 0
        for mi, mv in enumerate(merged):
            mp = pos2d(mv)
            for hj, hv in enumerate(hole):
                hp = pos2d(hv)
                d = (mp[0]-hp[0])**2 + (mp[1]-hp[1])**2
                if d < best_dist:
                    best_dist = d
                    best_mi = mi
                    best_hi = hj

        rotated_hole = hole[best_hi:] + hole[:best_hi]
        new_merged = (merged[:best_mi + 1] +
                     rotated_hole +
                     [rotated_hole[0]] +
                     [merged[best_mi]] +
                     merged[best_mi + 1:])
        merged = new_merged

    return merged


def ear_clip(fvi, positions, face_normal, bridge_merged=False,
             outer_ring=None, hole_rings=None):
    """Ear-clipping triangulation for concave polygons.

    Args:
        fvi: list of vertex indices forming the polygon
        positions: global positions array [(x,y,z), ...]
        face_normal: (nx, ny, nz) face normal
        bridge_merged: if True, use outer_ring/hole_rings for centroid checks
        outer_ring: original outer boundary indices (for bridge-merged)
        hole_rings: list of hole index lists (for bridge-merged)

    Returns:
        flat list of triangle indices [i0,i1,i2, ...]
    """
    poly = list(fvi)
    result = []
    gn = face_normal

    ax = abs(gn[0])
    ay = abs(gn[1])
    az = abs(gn[2])
    if ax >= ay and ax >= az:
        def proj(idx):
            p = positions[idx]
            return (p[1], p[2])
    elif ay >= ax and ay >= az:
        def proj(idx):
            p = positions[idx]
            return (p[0], p[2])
    else:
        def proj(idx):
            p = positions[idx]
            return (p[0], p[1])

    def cross2d(o, a, b):
        return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])

    def point_in_triangle(p, a, b, c):
        d1 = cross2d(p, a, b)
        d2 = cross2d(p, b, c)
        d3 = cross2d(p, c, a)
        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
        return not (has_neg and has_pos)

    def point_in_polygon(px, py, poly_pts):
        n = len(poly_pts)
        inside = False
        j = n - 1
        for ii in range(n):
            xi, yi = poly_pts[ii]
            xj, yj = poly_pts[j]
            if ((yi > py) != (yj > py)) and \
               (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
                inside = not inside
            j = ii
        return inside

    def segments_intersect(a1, a2, b1, b2):
        d1x, d1y = a2[0]-a1[0], a2[1]-a1[1]
        d2x, d2y = b2[0]-b1[0], b2[1]-b1[1]
        det = d1x*d2y - d1y*d2x
        if abs(det) < 1e-12:
            return False
        dx, dy = b1[0]-a1[0], b1[1]-a1[1]
        t = (dx*d2y - dy*d2x) / det
        u = (dx*d1y - dy*d1x) / det
        return 0.001 < t < 0.999 and 0.001 < u < 0.999

    # Determine winding direction
    area = 0
    pts = [proj(idx) for idx in poly]
    for i in range(len(pts)):
        j = (i + 1) % len(pts)
        area += pts[i][0] * pts[j][1]
        area -= pts[j][0] * pts[i][1]

    if area < 0:
        poly.reverse()

    orig_pts = [proj(idx) for idx in poly]

    # For bridge-merged polygons, pre-compute outer and hole 2D rings
    all_hole_pts_2d = []
    if bridge_merged and outer_ring and hole_rings:
        for hr in hole_rings:
            all_hole_pts_2d.extend([proj(idx) for idx in hr])

    max_iter = len(poly) * len(poly)
    iteration = 0
    i = 0
    last_clip_iter = 0
    while len(poly) > 2 and iteration < max_iter:
        iteration += 1
        n = len(poly)
        if i >= n:
            i = 0

        # Final triangle
        if n == 3:
            p0 = positions[poly[0]]
            p1 = positions[poly[1]]
            p2 = positions[poly[2]]
            e1 = (p1[0]-p0[0], p1[1]-p0[1], p1[2]-p0[2])
            e2 = (p2[0]-p0[0], p2[1]-p0[1], p2[2]-p0[2])
            cx_l = e1[1]*e2[2] - e1[2]*e2[1]
            cy_l = e1[2]*e2[0] - e1[0]*e2[2]
            cz_l = e1[0]*e2[1] - e1[1]*e2[0]
            dot_l = cx_l*gn[0] + cy_l*gn[1] + cz_l*gn[2]
            if dot_l < 0:
                result.extend([poly[0], poly[2], poly[1]])
            else:
                result.extend([poly[0], poly[1], poly[2]])
            poly.clear()
            break

        # Stuck detection
        if iteration - last_clip_iter > n + 1 and n > 3:
            pts_2d = [proj(idx) for idx in poly]
            split_done = False
            best_diag = None
            best_len = float('inf')
            for ai in range(n):
                for bi in range(ai + 2, n):
                    if ai == 0 and bi == n - 1:
                        continue
                    pa = pts_2d[ai]
                    pb = pts_2d[bi]
                    mx = (pa[0] + pb[0]) / 2.0
                    my = (pa[1] + pb[1]) / 2.0
                    if not point_in_polygon(mx, my, pts_2d):
                        continue
                    crosses = False
                    for ei in range(n):
                        ej = (ei + 1) % n
                        if ei in (ai, bi) or ej in (ai, bi):
                            continue
                        pe1 = pts_2d[ei]
                        pe2 = pts_2d[ej]
                        if segments_intersect(pa, pb, pe1, pe2):
                            crosses = True
                            break
                    if not crosses:
                        dlen = (pa[0]-pb[0])**2 + (pa[1]-pb[1])**2
                        if dlen < best_len:
                            best_len = dlen
                            best_diag = (ai, bi)
            if best_diag:
                ai, bi = best_diag
                sub1 = poly[ai:bi+1]
                sub2 = poly[bi:] + poly[:ai+1]
                for sub in (sub1, sub2):
                    if len(sub) >= 3:
                        sub_tris = ear_clip(list(sub), positions, face_normal)
                        result.extend(sub_tris)
                split_done = True
            if not split_done:
                best_ci = -1
                best_cross = float('inf')
                for ci in range(n):
                    cp = pts_2d[(ci-1) % n]
                    cc = pts_2d[ci]
                    cn = pts_2d[(ci+1) % n]
                    cv = abs(cross2d(cp, cc, cn))
                    if cv < best_cross:
                        best_cross = cv
                        best_ci = ci
                if best_ci >= 0:
                    pi = poly[(best_ci-1) % n]
                    ci_v = poly[best_ci]
                    ni = poly[(best_ci+1) % n]
                    p0 = positions[pi]
                    p1 = positions[ci_v]
                    p2 = positions[ni]
                    e1 = (p1[0]-p0[0], p1[1]-p0[1], p1[2]-p0[2])
                    e2 = (p2[0]-p0[0], p2[1]-p0[1], p2[2]-p0[2])
                    cx_f = e1[1]*e2[2] - e1[2]*e2[1]
                    cy_f = e1[2]*e2[0] - e1[0]*e2[2]
                    cz_f = e1[0]*e2[1] - e1[1]*e2[0]
                    dot_f = cx_f*gn[0] + cy_f*gn[1] + cz_f*gn[2]
                    if dot_f < 0:
                        result.extend([pi, ni, ci_v])
                    else:
                        result.extend([pi, ci_v, ni])
                    poly.pop(best_ci)
                    last_clip_iter = iteration
                    continue
            break

        prev_idx = poly[(i - 1) % n]
        curr_idx = poly[i]
        next_idx = poly[(i + 1) % n]

        pp = proj(prev_idx)
        pc = proj(curr_idx)
        pn = proj(next_idx)

        # Check for degenerate edge (bridge edges create duplicate vertices)
        dp = (pp[0]-pc[0])**2 + (pp[1]-pc[1])**2
        dn = (pn[0]-pc[0])**2 + (pn[1]-pc[1])**2
        if dp < 1e-16 or dn < 1e-16:
            poly.pop(i)
            if i >= len(poly):
                i = 0
            continue

        # Check if this is a convex vertex (ear candidate)
        cross = cross2d(pp, pc, pn)
        if cross <= 1e-10:
            i += 1
            continue

        # Check if any other polygon vertex is inside this triangle
        is_ear = True
        for j in range(n):
            if j in ((i-1) % n, i, (i+1) % n):
                continue
            pj = proj(poly[j])
            dj_p = (pj[0]-pp[0])**2 + (pj[1]-pp[1])**2
            dj_c = (pj[0]-pc[0])**2 + (pj[1]-pc[1])**2
            dj_n = (pj[0]-pn[0])**2 + (pj[1]-pn[1])**2
            if dj_p < 1e-16 or dj_c < 1e-16 or dj_n < 1e-16:
                continue
            if point_in_triangle(pj, pp, pc, pn):
                is_ear = False
                break

        # Also check original hole vertices
        if is_ear and all_hole_pts_2d:
            for hp in all_hole_pts_2d:
                dh_p = (hp[0]-pp[0])**2 + (hp[1]-pp[1])**2
                dh_c = (hp[0]-pc[0])**2 + (hp[1]-pc[1])**2
                dh_n = (hp[0]-pn[0])**2 + (hp[1]-pn[1])**2
                if dh_p < 1e-12 or dh_c < 1e-12 or dh_n < 1e-12:
                    continue
                if point_in_triangle(hp, pp, pc, pn):
                    is_ear = False
                    break

        if is_ear:
            cx_t = (pp[0] + pc[0] + pn[0]) / 3.0
            cy_t = (pp[1] + pc[1] + pn[1]) / 3.0
            if not bridge_merged:
                if not point_in_polygon(cx_t, cy_t, orig_pts):
                    i += 1
                    continue

            # Emit triangle with correct winding
            p0 = positions[prev_idx]
            p1 = positions[curr_idx]
            p2 = positions[next_idx]
            e1 = (p1[0]-p0[0], p1[1]-p0[1], p1[2]-p0[2])
            e2 = (p2[0]-p0[0], p2[1]-p0[1], p2[2]-p0[2])
            cx = e1[1]*e2[2] - e1[2]*e2[1]
            cy = e1[2]*e2[0] - e1[0]*e2[2]
            cz = e1[0]*e2[1] - e1[1]*e2[0]
            dot = cx*gn[0] + cy*gn[1] + cz*gn[2]
            if dot < 0:
                result.extend([prev_idx, next_idx, curr_idx])
            else:
                result.extend([prev_idx, curr_idx, next_idx])
            poly.pop(i)
            if i >= len(poly):
                i = 0
            last_clip_iter = iteration
        else:
            i += 1

    return result


def is_convex_polygon(fvi, positions, face_normal):
    """Check if a polygon (given by vertex indices) is convex.

    Args:
        fvi: list of vertex indices
        positions: global positions array
        face_normal: (nx, ny, nz) face normal

    Returns:
        True if convex, False if concave
    """
    n = len(fvi)
    if n <= 3:
        return True

    gn = face_normal
    sign = 0
    for i in range(n):
        p0 = positions[fvi[i]]
        p1 = positions[fvi[(i+1) % n]]
        p2 = positions[fvi[(i+2) % n]]
        e1 = (p1[0]-p0[0], p1[1]-p0[1], p1[2]-p0[2])
        e2 = (p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2])
        cx = e1[1]*e2[2] - e1[2]*e2[1]
        cy = e1[2]*e2[0] - e1[0]*e2[2]
        cz = e1[0]*e2[1] - e1[1]*e2[0]
        d = cx*gn[0] + cy*gn[1] + cz*gn[2]
        if abs(d) > 1e-10:
            if sign == 0:
                sign = 1 if d > 0 else -1
            elif (d > 0 and sign < 0) or (d < 0 and sign > 0):
                return False
    return True


def convex_hull_2d(points):
    """Compute 2D convex hull using Andrew's monotone chain algorithm.

    Args:
        points: iterable of (x, y) tuples

    Returns:
        list of (x, y) tuples forming the convex hull in CCW order
    """
    pts = sorted(set(points))
    if len(pts) <= 2:
        return pts

    def cross(o, a, b):
        return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])

    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def fan_triangulate(fvi, positions, face_normal):
    """Fan triangulation for convex polygons. Returns flat index list."""
    result = []
    gn = face_normal
    for i in range(1, len(fvi) - 1):
        i0, i1, i2 = fvi[0], fvi[i], fvi[i + 1]
        p0 = positions[i0]
        p1 = positions[i1]
        p2 = positions[i2]
        e1 = (p1[0]-p0[0], p1[1]-p0[1], p1[2]-p0[2])
        e2 = (p2[0]-p0[0], p2[1]-p0[1], p2[2]-p0[2])
        cx = e1[1]*e2[2] - e1[2]*e2[1]
        cy = e1[2]*e2[0] - e1[0]*e2[2]
        cz = e1[0]*e2[1] - e1[1]*e2[0]
        dot = cx*gn[0] + cy*gn[1] + cz*gn[2]
        if dot < 0:
            result.extend([i0, i2, i1])
        else:
            result.extend([i0, i1, i2])
    return result

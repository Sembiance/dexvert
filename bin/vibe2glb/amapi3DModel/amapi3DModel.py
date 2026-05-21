#!/usr/bin/env python3
import sys
import struct
import json

def parse_absolute(data, start, end):
    offset = start
    chunks = []
    while offset < end:
        if offset + 4 <= end and data[offset:offset+4].lower() == b'eof ':
            chunks.append(('eof', offset, 4, []))
            offset += 4
            break
            
        if offset + 12 > end:
            break
        name = data[offset:offset+8].decode('ascii', errors='ignore').strip()
        length = struct.unpack('>I', data[offset+8:offset+12])[0]
        sub_chunks = []
        next_offset = offset + 12 + length
        
        name_lower = name.lower()
        if name_lower in ('blokshap', 'blokctrl'):
            sub_chunks, _ = parse_absolute(data, offset+12, min(offset+12+length, end))
        elif name_lower == 'blokgrup':
            if offset + 16 <= end:
                child_count = struct.unpack('>I', data[offset+12:offset+16])[0]
                sub_offset = offset + 16
                for _ in range(child_count):
                    child_sub, next_sub_offset = parse_absolute(data, sub_offset, min(offset+12+length, end))
                    sub_chunks.append(child_sub)
                    sub_offset = next_sub_offset
                next_offset = offset + 12 + length
            
        chunks.append((name, offset, 12 + length, sub_chunks))
        
        if name_lower == 'blokctrl':
            idx1 = data.lower().find(b'eof ', offset + 12 + length, end)
            if idx1 != -1:
                chunks.append(('eof_trail', offset + 12 + length, (idx1 + 4) - (offset + 12 + length), []))
                next_offset = idx1 + 4
                offset = next_offset
                break
        offset = next_offset
    return chunks, offset

def parse_nurb(payload):
    if len(payload) < 24:
        return [], []
    deg_u, deg_v, count_u, count_v, knots_u, knots_v = struct.unpack('>IIIIII', payload[:24])
    eff_cv = 1 if count_v == 0 else count_v
    cand = 36 + count_u * 4 + knots_v * 4
    
    if cand + count_u * eff_cv * 12 > len(payload):
        return [], []
        
    vertices = []
    offset = cand
    for _ in range(count_u * eff_cv):
        x, y, z = struct.unpack('>fff', payload[offset:offset+12])
        vertices.append((x, y, z))
        offset += 12
        
    triangles = []
    if eff_cv > 1:
        for u in range(count_u - 1):
            for v in range(eff_cv - 1):
                i0 = u * eff_cv + v
                i1 = (u + 1) * eff_cv + v
                i2 = (u + 1) * eff_cv + v + 1
                i3 = u * eff_cv + v + 1
                triangles.append((i0, i1, i2))
                triangles.append((i0, i2, i3))
    return vertices, triangles

def parse_tmpi(payload):
    if len(payload) < 4:
        return [], []
    v_count = struct.unpack('>I', payload[:4])[0]
    offset = 4
    vertices = []
    for _ in range(v_count):
        if offset + 12 > len(payload):
            break
        x, y, z = struct.unpack('>fff', payload[offset:offset+12])
        vertices.append((x, y, z))
        offset += 12
        
    if offset + 8 > len(payload):
        return vertices, []
    f_count, idx_count = struct.unpack('>II', payload[offset:offset+8])
    offset += 8
    
    faces = []
    f_idx = 0
    while f_idx < f_count and offset < len(payload):
        if offset + 4 > len(payload):
            break
        vcount = struct.unpack('>I', payload[offset:offset+4])[0]
        offset += 4
        face = []
        for _ in range(vcount):
            if offset + 4 > len(payload):
                break
            v_idx = struct.unpack('>I', payload[offset:offset+4])[0]
            face.append(v_idx)
            offset += 4
        faces.append(face)
        f_idx += 1
        
    triangles = []
    for face in faces:
        if len(face) < 3:
            continue
        if len(face) == 3:
            triangles.append((face[0], face[1], face[2]))
        elif len(face) == 4:
            triangles.append((face[0], face[1], face[2]))
            triangles.append((face[0], face[2], face[3]))
        else:
            triangles.extend(triangulate_polygon_earclip(vertices, face))
    return vertices, triangles

def get_polygon_normal(vertices, indices):
    normal = [0.0, 0.0, 0.0]
    n = len(indices)
    for i in range(n):
        p1 = vertices[indices[i]]
        p2 = vertices[indices[(i + 1) % n]]
        normal[0] += (p1[1] - p2[1]) * (p1[2] + p2[2])
        normal[1] += (p1[2] - p2[2]) * (p1[0] + p2[0])
        normal[2] += (p1[0] - p2[0]) * (p1[1] + p2[1])
    return normal

def get_loops_graph(indices):
    n = len(indices)
    if n < 3:
        return [indices], []
    edges = []
    for i in range(n):
        u = indices[i]
        v = indices[(i + 1) % n]
        edges.append((u, v))
    undirected_counts = {}
    for u, v in edges:
        key = tuple(sorted((u, v)))
        undirected_counts[key] = undirected_counts.get(key, 0) + 1
    bridges = {key for key, count in undirected_counts.items() if count > 1}
    non_bridge_edges = []
    for u, v in edges:
        key = tuple(sorted((u, v)))
        if key not in bridges:
            non_bridge_edges.append((u, v))
    adj = {}
    for u, v in non_bridge_edges:
        adj[u] = v
    loops = []
    visited = set()
    for start in adj:
        if start in visited:
            continue
        loop = []
        curr = start
        while curr not in visited:
            visited.add(curr)
            loop.append(curr)
            curr = adj.get(curr)
            if curr is None or curr == start:
                break
        loops.append(loop)
    return loops, list(bridges)

def get_signed_area_2d(loop_indices, vertices, ax):
    if ax == 0: pts = [(vertices[idx][1], vertices[idx][2]) for idx in loop_indices]
    elif ax == 1: pts = [(vertices[idx][0], vertices[idx][2]) for idx in loop_indices]
    else: pts = [(vertices[idx][0], vertices[idx][1]) for idx in loop_indices]
    area = 0.0
    n = len(pts)
    for i in range(n):
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        area += (p1[0] * p2[1] - p2[0] * p1[1])
    return area * 0.5

def get_oriented_and_reconstructed(indices, vertices, ax):
    loops, bridges = get_loops_graph(indices)
    if not loops:
        return []
        
    if len(loops) == 1:
        l = list(loops[0])
        area = get_signed_area_2d(l, vertices, ax)
        if area < 0: l.reverse()
        return l
        
    areas = []
    for l in loops:
        areas.append(abs(get_signed_area_2d(l, vertices, ax)))
    outer_idx = areas.index(max(areas))
    
    oriented_loops = []
    for i, l in enumerate(loops):
        l_copy = list(l)
        area = get_signed_area_2d(l_copy, vertices, ax)
        if i == outer_idx:
            if area < 0: l_copy.reverse()
        else:
            if area > 0: l_copy.reverse()
        oriented_loops.append(l_copy)
        
    loop_of_vertex = {}
    for idx, l in enumerate(oriented_loops):
        for v in l:
            loop_of_vertex[v] = idx
            
    loop_adj = [[] for _ in range(len(oriented_loops))]
    for u, v in bridges:
        if u in loop_of_vertex and v in loop_of_vertex:
            idx_u = loop_of_vertex[u]
            idx_v = loop_of_vertex[v]
            if idx_u != idx_v:
                loop_adj[idx_u].append((u, v, idx_v))
                loop_adj[idx_v].append((v, u, idx_u))
                
    children = [[] for _ in range(len(oriented_loops))]
    visited = {outer_idx}
    queue = [outer_idx]
    while queue:
        curr = queue.pop(0)
        for u, v, nxt in loop_adj[curr]:
            if nxt not in visited:
                visited.add(nxt)
                children[curr].append((u, v, nxt))
                queue.append(nxt)
                
    def traverse(loop_idx, entry_v):
        l = oriented_loops[loop_idx]
        idx_entry = l.index(entry_v)
        l_rot = l[idx_entry:] + l[:idx_entry]
        
        child_map = {}
        for u, v, child_idx in children[loop_idx]:
            child_map.setdefault(u, []).append((v, child_idx))
            
        path = []
        for curr_v in l_rot:
            path.append(curr_v)
            if curr_v in child_map:
                for child_v, child_idx in child_map[curr_v]:
                    child_path = traverse(child_idx, child_v)
                    path.extend(child_path)
                    path.append(child_v)
                    path.append(curr_v)
        return path
        
    root_start = oriented_loops[outer_idx][0]
    final_path = traverse(outer_idx, root_start)
    return final_path

def triangulate_polygon_earclip(vertices, indices):
    n = len(indices)
    if n < 3:
        return []
    if n == 3:
        return [(indices[0], indices[1], indices[2])]
    if n == 4:
        return [(indices[0], indices[1], indices[2]), (indices[0], indices[2], indices[3])]
        
    normal = get_polygon_normal(vertices, indices)
    ax = 0
    if abs(normal[1]) > abs(normal[ax]): ax = 1
    if abs(normal[2]) > abs(normal[ax]): ax = 2
    
    indices_work = get_oriented_and_reconstructed(indices, vertices, ax)
    if not indices_work:
        return []
        
    if ax == 0: pts = [(vertices[idx][1], vertices[idx][2]) for idx in indices_work]
    elif ax == 1: pts = [(vertices[idx][0], vertices[idx][2]) for idx in indices_work]
    else: pts = [(vertices[idx][0], vertices[idx][1]) for idx in indices_work]
    
    work_pts = list(pts)
    
    def is_point_in_triangle(p, a, b, c):
        v0 = (c[0] - a[0], c[1] - a[1])
        v1 = (b[0] - a[0], b[1] - a[1])
        v2 = (p[0] - a[0], p[1] - a[1])
        dot00 = v0[0]*v0[0] + v0[1]*v0[1]
        dot01 = v0[0]*v1[0] + v0[1]*v1[1]
        dot02 = v0[0]*v2[0] + v0[1]*v2[1]
        dot11 = v1[0]*v1[0] + v1[1]*v1[1]
        dot12 = v1[0]*v2[0] + v1[1]*v2[1]
        denom = dot00 * dot11 - dot01 * dot01
        if abs(denom) < 1e-9: return False
        invDenom = 1.0 / denom
        u = (dot11 * dot02 - dot01 * dot12) * invDenom
        v = (dot00 * dot12 - dot01 * dot02) * invDenom
        return (u >= -1e-5) and (v >= -1e-5) and (u + v <= 1.0 + 1e-5)
        
    def is_ear(u, v, w, polygon_pts):
        a = polygon_pts[u]
        b = polygon_pts[v]
        c = polygon_pts[w]
        cross_prod = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        if cross_prod <= 1e-9: return False
        for i in range(len(polygon_pts)):
            if indices_work[i] in (indices_work[u], indices_work[v], indices_work[w]):
                continue
            if is_point_in_triangle(polygon_pts[i], a, b, c):
                return False
        return True
        
    triangles = []
    while len(indices_work) > 3:
        ear_found = False
        nw = len(indices_work)
        for i in range(nw):
            u = (i - 1 + nw) % nw
            v = i
            w = (i + 1) % nw
            if is_ear(u, v, w, work_pts):
                triangles.append((indices_work[u], indices_work[v], indices_work[w]))
                del indices_work[v]
                del work_pts[v]
                ear_found = True
                break
        if not ear_found:
            break
            
    if len(indices_work) == 3:
        triangles.append((indices_work[0], indices_work[1], indices_work[2]))
    else:
        for i in range(1, len(indices_work) - 1):
            triangles.append((indices_work[0], indices_work[i], indices_work[i+1]))
    return triangles

def parse_geometry(payload):
    if len(payload) < 36:
        return [], []
    v_count = struct.unpack('>I', payload[4:8])[0] >> 8
    e_count = struct.unpack('>I', payload[8:12])[0] >> 8
    f_count = struct.unpack('>I', payload[12:16])[0] >> 8
    
    # 3-byte shift at the start of the data array
    offset = 36 + 3
    
    vertices = []
    for _ in range(v_count):
        if offset + 12 > len(payload):
            break
        x, y, z = struct.unpack('>fff', payload[offset:offset+12])
        vertices.append((x, y, z))
        offset += 16
        
    offset += e_count * 8
    
    faces = []
    for _ in range(f_count):
        if offset + 4 > len(payload):
            break
        vcount = struct.unpack('>I', payload[offset:offset+4])[0]
        offset += 4
        face = []
        for _ in range(vcount):
            if offset + 4 > len(payload):
                break
            v_idx = struct.unpack('>I', payload[offset:offset+4])[0]
            face.append(v_idx)
            offset += 4
        faces.append(face)
        
    triangles = []
    for face in faces:
        if len(face) < 3:
            continue
        if len(face) == 3:
            triangles.append((face[0], face[1], face[2]))
        elif len(face) == 4:
            triangles.append((face[0], face[1], face[2]))
            triangles.append((face[0], face[2], face[3]))
        else:
            triangles.extend(triangulate_polygon_earclip(vertices, face))
    return vertices, triangles

class GLBBuilder:
    def __init__(self):
        self.nodes = []
        self.meshes = []
        self.materials = []
        self.accessors = []
        self.buffer_views = []
        self.binary_data = bytearray()
        
    def add_mesh(self, name, vertices, triangles, color):
        self._align_buffer()
        pos_offset = len(self.binary_data)
        min_coords = [float('inf')] * 3
        max_coords = [float('-inf')] * 3
        for x, y, z in vertices:
            self.binary_data.extend(struct.pack('<fff', x, y, z))
            min_coords[0] = min(min_coords[0], x)
            min_coords[1] = min(min_coords[1], y)
            min_coords[2] = min(min_coords[2], z)
            max_coords[0] = max(max_coords[0], x)
            max_coords[1] = max(max_coords[1], y)
            max_coords[2] = max(max_coords[2], z)
        pos_length = len(self.binary_data) - pos_offset
        if not vertices:
            min_coords = [0.0, 0.0, 0.0]
            max_coords = [0.0, 0.0, 0.0]
            
        self._align_buffer()
        idx_offset = len(self.binary_data)
        for i0, i1, i2 in triangles:
            self.binary_data.extend(struct.pack('<III', i0, i1, i2))
        idx_length = len(self.binary_data) - idx_offset
        
        pos_bv_idx = len(self.buffer_views)
        self.buffer_views.append({
            'buffer': 0,
            'byteOffset': pos_offset,
            'byteLength': pos_length,
            'target': 34962
        })
        
        idx_bv_idx = len(self.buffer_views)
        self.buffer_views.append({
            'buffer': 0,
            'byteOffset': idx_offset,
            'byteLength': idx_length,
            'target': 34963
        })
        
        pos_acc_idx = len(self.accessors)
        self.accessors.append({
            'bufferView': pos_bv_idx,
            'byteOffset': 0,
            'componentType': 5126,
            'count': len(vertices),
            'type': 'VEC3',
            'min': min_coords,
            'max': max_coords
        })
        
        idx_acc_idx = len(self.accessors)
        self.accessors.append({
            'bufferView': idx_bv_idx,
            'byteOffset': 0,
            'componentType': 5125,
            'count': len(triangles) * 3,
            'type': 'SCALAR'
        })
        
        mat_idx = len(self.materials)
        base_color = [color[0]/255.0, color[1]/255.0, color[2]/255.0, 1.0] if color else [0.8, 0.8, 0.8, 1.0]
        self.materials.append({
            'pbrMetallicRoughness': {
                'baseColorFactor': base_color,
                'metallicFactor': 0.0,
                'roughnessFactor': 0.5
            },
            'doubleSided': True
        })
        
        mesh_idx = len(self.meshes)
        self.meshes.append({
            'name': name,
            'primitives': [{
                'attributes': {'POSITION': pos_acc_idx},
                'indices': idx_acc_idx,
                'material': mat_idx,
                'mode': 4
            }]
        })
        return mesh_idx
        
    def add_node(self, name, mesh_idx, children, matrix=None):
        node_idx = len(self.nodes)
        node = {'name': name}
        if mesh_idx is not None:
            node['mesh'] = mesh_idx
        if children:
            node['children'] = children
        if matrix:
            node['matrix'] = matrix
        self.nodes.append(node)
        return node_idx
        
    def _align_buffer(self):
        while len(self.binary_data) % 4 != 0:
            self.binary_data.append(0)
            
    def build(self, root_nodes):
        gltf = {
            'asset': {'version': '2.0'},
            'scene': 0,
            'scenes': [{'nodes': root_nodes}],
            'nodes': self.nodes,
            'meshes': self.meshes,
            'materials': self.materials,
            'accessors': self.accessors,
            'bufferViews': self.buffer_views,
            'buffers': [{'byteLength': len(self.binary_data)}]
        }
        json_str = json.dumps(gltf, separators=(',', ':'))
        json_bytes = json_str.encode('utf-8')
        while len(json_bytes) % 4 != 0:
            json_bytes += b' '
        bin_bytes = bytes(self.binary_data)
        while len(bin_bytes) % 4 != 0:
            bin_bytes += b'\x00'
        glb = bytearray()
        glb.extend(b'glTF')
        glb.extend(struct.pack('<I', 2))
        total_length = 12 + 8 + len(json_bytes) + 8 + len(bin_bytes)
        glb.extend(struct.pack('<I', total_length))
        glb.extend(struct.pack('<I', len(json_bytes)))
        glb.extend(b'JSON')
        glb.extend(json_bytes)
        glb.extend(struct.pack('<I', len(bin_bytes)))
        glb.extend(b'BIN\x00')
        glb.extend(bin_bytes)
        return glb

def revolve_curve(vertices_in, segments=32):
    if len(vertices_in) < 2:
        return vertices_in, []
        
    # Calculate coordinate ranges
    ranges = [
        max(coord) - min(coord)
        for coord in zip(*vertices_in)
    ]
    
    # Height axis H is the one with the maximum range
    H = ranges.index(max(ranges))
    
    # Other two axes A and B. Sort them by range descending.
    other_axes = [i for i in range(3) if i != H]
    if ranges[other_axes[0]] >= ranges[other_axes[1]]:
        A, B = other_axes[0], other_axes[1]
    else:
        A, B = other_axes[1], other_axes[0]
        
    # Compute center for B (axis with smaller range, constant for flat profile)
    C_B = sum(p[B] for p in vertices_in) / len(vertices_in)
    C_A = 0.0
    
    import math
    revolved_vertices = []
    for j in range(segments):
        theta = j * 2.0 * math.pi / segments
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        for p in vertices_in:
            h = p[H]
            r = abs(p[A] - C_A)
            
            v = [0.0, 0.0, 0.0]
            v[H] = h
            v[A] = r * cos_t
            v[B] = C_B + r * sin_t
            revolved_vertices.append((v[0], v[1], v[2]))
            
    triangles = []
    N = len(vertices_in)
    for i in range(N - 1):
        for j in range(segments):
            next_j = (j + 1) % segments
            
            p00 = j * N + i
            p10 = next_j * N + i
            p11 = next_j * N + (i + 1)
            p01 = j * N + (i + 1)
            
            triangles.append((p00, p10, p11))
            triangles.append((p00, p11, p01))
            
    return revolved_vertices, triangles

def check_has_surface_geometry(chunks, data):
    for name, offset, size, sub in chunks:
        name_lower = name.lower()
        if name_lower in ('blokshap', 'blokctrl'):
            if check_has_surface_geometry(sub, data):
                return True
        elif name_lower == 'blokgrup':
            for child_seq in sub:
                if check_has_surface_geometry(child_seq, data):
                    return True
        elif name_lower == 'blokgeom':
            payload = data[offset+12 : offset+size]
            if len(payload) >= 16:
                f_count = struct.unpack('>I', payload[12:16])[0] >> 8
                if f_count > 0:
                    return True
        elif name_lower == 'bloktmpi':
            payload = data[offset+12 : offset+size]
            if len(payload) >= 12:
                v_count = struct.unpack('>I', payload[:4])[0]
                idx_offset = 4 + v_count * 12
                if idx_offset + 4 <= len(payload):
                    f_count = struct.unpack('>I', payload[idx_offset : idx_offset+4])[0]
                    if f_count > 0:
                        return True
        elif name_lower == 'bloknurb':
            payload = data[offset+12 : offset+size]
            if len(payload) >= 24:
                deg_u, deg_v, count_u, count_v, knots_u, knots_v = struct.unpack('>IIIIII', payload[:24])
                if count_v > 1:
                    return True
    return False

def process_container(name_in, chunks, data, builder, allow_revolve=False):
    geom_chunk = next((c for c in chunks if c[0].lower() == 'blokgeom'), None)
    tmpi_chunk = next((c for c in chunks if c[0].lower() == 'bloktmpi'), None)
    nurb_chunk = next((c for c in chunks if c[0].lower() == 'bloknurb'), None)
    name_chunk = next((c for c in chunks if c[0].lower() == 'blokname'), None)
    colr_chunk = next((c for c in chunks if c[0].lower() == 'blokcolr'), None)
    
    name = name_in
    if name_chunk:
        name_payload = data[name_chunk[1]+12 : name_chunk[1]+name_chunk[2]]
        name = name_payload.decode('ascii', errors='ignore').strip('\x00').strip()
        
    color = None
    if colr_chunk:
        colr_payload = data[colr_chunk[1]+12 : colr_chunk[1]+colr_chunk[2]]
        color = struct.unpack('BBB', colr_payload[:3])
        
    children_indices = []
    for c_name, c_offset, c_size, c_sub in chunks:
        c_name_lower = c_name.lower()
        if c_name_lower == 'blokshap':
            child_idx = process_container('Shape', c_sub, data, builder, allow_revolve)
            if child_idx is not None:
                children_indices.append(child_idx)
        elif c_name_lower == 'blokgrup':
            for child_seq in c_sub:
                child_idx = process_container('GroupShape', child_seq, data, builder, allow_revolve)
                if child_idx is not None:
                    children_indices.append(child_idx)
                    
    mesh_idx = None
    vertices, triangles = [], []
    if tmpi_chunk:
        tmpi_payload = data[tmpi_chunk[1]+12 : tmpi_chunk[1]+tmpi_chunk[2]]
        vertices, triangles = parse_tmpi(tmpi_payload)
        
    if not vertices and geom_chunk:
        geom_payload = data[geom_chunk[1]+12 : geom_chunk[1]+geom_chunk[2]]
        vertices, triangles = parse_geometry(geom_payload)
        
        # If it contains only a curve (no surface faces), check if it is an open curve and auto-revolve
        if vertices and not triangles and allow_revolve:
            v_count = struct.unpack('>I', geom_payload[4:8])[0] >> 8
            e_count = struct.unpack('>I', geom_payload[8:12])[0] >> 8
            f_count = struct.unpack('>I', geom_payload[12:16])[0] >> 8
            if f_count == 0 and e_count < v_count and v_count >= 2:
                vertices, triangles = revolve_curve(vertices)
        
    if not vertices and nurb_chunk:
        nurb_payload = data[nurb_chunk[1]+12 : nurb_chunk[1]+nurb_chunk[2]]
        vertices, triangles = parse_nurb(nurb_payload)
        
    # Only add mesh if we have triangles/faces (skip closed base curves to keep rendering clean)
    if vertices and triangles:
        mesh_idx = builder.add_mesh(name, vertices, triangles, color)
            
    if mesh_idx is not None or children_indices:
        node_idx = builder.add_node(name, mesh_idx, children_indices, matrix=None)
        return node_idx
    return None

def main():
    if len(sys.argv) != 3:
        print("Usage: amapi3DModel.py <inputFile> <outputFile>", file=sys.stderr)
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    with open(input_file, 'rb') as f:
        data = f.read()
        
    root_chunks, _ = parse_absolute(data, 8, len(data))
    allow_revolve = not check_has_surface_geometry(root_chunks, data)
    
    builder = GLBBuilder()
    roots = []
    for name, offset, size, sub in root_chunks:
        name_lower = name.lower()
        if name_lower == 'blokshap':
            root_idx = process_container('Shape', sub, data, builder, allow_revolve)
            if root_idx is not None:
                roots.append(root_idx)
        elif name_lower == 'blokgrup':
            for child_seq in sub:
                root_idx = process_container('GroupShape', child_seq, data, builder, allow_revolve)
                if root_idx is not None:
                    roots.append(root_idx)
                    
    glb_bytes = builder.build(roots)
    with open(output_file, 'wb') as f:
        f.write(glb_bytes)

if __name__ == '__main__':
    main()

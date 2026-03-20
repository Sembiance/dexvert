#!/usr/bin/env python3
# Vibe coded by Claude
"""
Starbreeze XMD (.xmd) model parser and GLB converter.

XMD files use the "MOS DATAFILE2.0" container format. Two mesh storage variants:

  1. Uncompressed CLUSTERS — standard CDataFile entries with VERTEXFRAMES,
     TVERTEXFRAMES, TRIANGLES, PRIMITIVES sub-sections.

  2. Compressed COMPRESSEDCLUSTERS — LZSS+Huffman compressed CDataFile.
     Decompresses to the same format as variant 1.

Both variants store vertex positions in VERTEXFRAMES (f32 or i16-quantized)
and triangle connectivity in PRIMITIVES (triangle strips with group markers).
"""

import struct
import sys
import os
import math

from glb import GLBBuilder


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

class XMDMesh:
    def __init__(self):
        self.positions = []
        self.normals = []
        self.triangles = []
        self.uvs = []


class XMDModel:
    def __init__(self):
        self.meshes = []
        self.name = ""
        self.variant = ""


# ---------------------------------------------------------------------------
# Bit I/O for LZSS+Huffman decompression
# ---------------------------------------------------------------------------

class _BitReader:
    """Read bits from a byte buffer, LSB first."""
    __slots__ = ('data', 'pos', 'bit')

    def __init__(self, data, start=0):
        self.data = data
        self.pos = start
        self.bit = 0

    def read_bit(self):
        if self.pos >= len(self.data):
            return 0
        val = (self.data[self.pos] >> self.bit) & 1
        self.bit += 1
        if self.bit >= 8:
            self.bit = 0
            self.pos += 1
        return val

    def read_bits(self, n):
        if n == 0:
            return 0
        if self.pos >= len(self.data):
            return 0
        val = self.data[self.pos] >> self.bit
        bits_read = 8 - self.bit
        self.bit = 0
        self.pos += 1
        while bits_read < n and self.pos < len(self.data):
            val |= self.data[self.pos] << bits_read
            bits_read += 8
            self.pos += 1
        val &= (1 << n) - 1
        remaining = bits_read - n
        if remaining > 0:
            self.pos -= 1
            self.bit = 8 - remaining
        return val


class _BitWriter:
    __slots__ = ('data', 'pos', 'bit')

    def __init__(self, size):
        self.data = bytearray(size)
        self.pos = 0
        self.bit = 0

    def write_bits(self, val, n):
        for i in range(n):
            if self.pos < len(self.data):
                self.data[self.pos] |= ((val >> i) & 1) << self.bit
                self.bit += 1
                if self.bit >= 8:
                    self.bit = 0
                    self.pos += 1


# ---------------------------------------------------------------------------
# Huffman tree for LZSS+Huffman decompression
# ---------------------------------------------------------------------------

class _HuffNode:
    __slots__ = ('value', 'children')

    def __init__(self):
        self.value = -1
        self.children = [None, None]


def _huffman_get_char(root, br):
    node = root
    while node.value == -1:
        bit = br.read_bit()
        child = node.children[bit]
        if child is None:
            return 0
        node = child
    return node.value


def _huffman_decompress_stream(src):
    """Decompress a single Huffman sub-stream.

    Format: u32 decomp_size + u8 flag + data
    If flag==0: raw copy. If flag==1: Huffman coded.
    """
    if len(src) < 5:
        return b''
    decomp_size = struct.unpack_from('<I', src, 0)[0]
    flag = src[4]
    if decomp_size == 0:
        return b''

    if flag != 1:
        return bytes(src[5:5 + decomp_size])

    br = _BitReader(src, 5)
    symbol_bits = br.read_bits(8)
    if symbol_bits == 0:
        symbol_bits = 8
    num_symbols = 1 << symbol_bits
    enc_flag = br.read_bit()

    root = _HuffNode()
    if enc_flag == 1:
        # Read per-symbol presence flags
        present = [br.read_bit() for _ in range(num_symbols)]
    else:
        # enc_flag==0: ALL symbols are present (memset code_lengths to 1)
        present = [1] * num_symbols

    for sym in range(num_symbols):
        if not present[sym]:
            continue
        depth_flag = br.read_bit()
        depth = (br.read_bits(8) + 1) if depth_flag else (br.read_bits(4) + 1)
        path_bits = [br.read_bit() for _ in range(depth)]
        node = root
        for d in range(depth):
            bit = path_bits[d]
            if node.children[bit] is None:
                child = _HuffNode()
                if d == depth - 1:
                    child.value = sym
                node.children[bit] = child
            node = node.children[bit]

    if symbol_bits == 8:
        output = bytearray(decomp_size)
        for i in range(decomp_size):
            output[i] = _huffman_get_char(root, br) & 0xFF
        return bytes(output)
    else:
        total_symbols = int(decomp_size * 8 / symbol_bits + 0.5)
        bw = _BitWriter(decomp_size + 4)
        for _ in range(total_symbols):
            ch = _huffman_get_char(root, br)
            bw.write_bits(ch, symbol_bits)
        return bytes(bw.data[:decomp_size])


# ---------------------------------------------------------------------------
# LZSS+Huffman decompression (reverses CDiskUtil::Compress from MCCDyn.dll)
# ---------------------------------------------------------------------------

def _decompress_lzss_huffman(cc_data):
    """Decompress a COMPRESSEDCLUSTERS section.

    cc_data: full section bytes starting with u32 decomp_size.
    Returns decompressed CDataFile bytes.
    """
    if len(cc_data) < 30:
        return b''
    decomp_size = struct.unpack_from('<I', cc_data, 0)[0]
    if decomp_size == 0 or decomp_size > 50_000_000:
        return b''

    huffman_flag = cc_data[4]
    if huffman_flag == 0:
        # No Huffman — raw or simple LZSS
        if cc_data[5] == 0:
            return bytes(cc_data[5:5 + decomp_size])
        return b''

    # Read 5 sub-stream offsets
    offsets = [struct.unpack_from('<I', cc_data, 6 + i * 4)[0] for i in range(5)]
    offset_bits = cc_data[26]
    length_bits = cc_data[27]
    min_match = cc_data[28]

    half_offset = offset_bits >> 1
    other_half = half_offset + (1 if offset_bits & 1 else 0)

    # Huffman-decompress each of the 5 sub-streams
    streams = []
    for i in range(5):
        start = offsets[i]
        end = offsets[i + 1] if i < 4 else len(cc_data)
        streams.append(_huffman_decompress_stream(cc_data[start:end]))

    # Set up bitreaders for LZSS
    br_flags = _BitReader(streams[0])
    br_offlo = _BitReader(streams[1])
    br_offhi = _BitReader(streams[2])
    br_length = _BitReader(streams[3])
    literals = streams[4]
    lit_pos = 0

    # Linear sliding window: write_pos tracks how far back we can ref, capped at window_size
    window_size = 1 << offset_bits
    output = bytearray()
    write_pos = 0

    while len(output) < decomp_size:
        flag = br_flags.read_bit()
        if flag == 0:
            b = literals[lit_pos] if lit_pos < len(literals) else 0
            lit_pos += 1
            output.append(b)
            write_pos += 1
            if write_pos >= window_size:
                write_pos = window_size
        else:
            off_lo = br_offlo.read_bits(half_offset)
            off_hi = br_offhi.read_bits(other_half)
            combined = (off_hi << half_offset) | off_lo
            match_len = br_length.read_bits(length_bits) + min_match
            src_pos = len(output) + combined - write_pos
            for j in range(match_len):
                if 0 <= src_pos + j < len(output):
                    output.append(output[src_pos + j])
                else:
                    output.append(0)
            write_pos += match_len
            if write_pos >= window_size:
                write_pos = window_size

    return bytes(output[:decomp_size])


# ---------------------------------------------------------------------------
# MOS DATAFILE2.0 / CDataFile directory parsing
# ---------------------------------------------------------------------------

MOS_MAGIC = b"MOS DATAFILE2.0\x00"


def _read_mos_directory(data):
    """Parse the outer MOS directory as sequential 48-byte entries."""
    if len(data) < 32 or data[:16] != MOS_MAGIC:
        return []
    dir_offset = struct.unpack_from('<I', data, 24)[0]
    entries = []
    pos = dir_offset
    while pos + 48 <= len(data):
        name = data[pos:pos + 24].split(b'\x00', 1)[0].decode('ascii', errors='replace')
        if not name or not all(32 <= ord(c) <= 126 for c in name):
            break
        vals = struct.unpack_from('<6I', data, pos + 24)
        entries.append({
            'type': name, 'next': vals[0], 'child': vals[1],
            'off': vals[2], 'len': vals[3], 'num': vals[4], 'flags': vals[5],
        })
        pos += 48
    return entries


def _parse_entry(data, offset):
    """Parse a single 48-byte directory entry at the given offset."""
    if offset + 48 > len(data):
        return None
    name = data[offset:offset + 24].split(b'\x00', 1)[0].decode('ascii', errors='replace')
    if not name or not all(32 <= ord(c) <= 126 for c in name):
        return None
    vals = struct.unpack_from('<6I', data, offset + 24)
    return {'type': name, 'next': vals[0], 'child': vals[1],
            'off': vals[2], 'len': vals[3], 'num': vals[4], 'flags': vals[5]}


def _collect_children(data, child_offset):
    """Collect all sibling entries starting from child_offset into a dict by name."""
    sections = {}
    offset = child_offset
    while 0 < offset < len(data):
        e = _parse_entry(data, offset)
        if not e:
            break
        if e['len'] > 0 and e['type'] not in sections:
            sections[e['type']] = {'off': e['off'], 'len': e['len'], 'num': e['num']}
        offset = e['next'] if 0 < e['next'] < len(data) else 0
    return sections


def _read_cdf_clusters(data):
    """Parse a CDataFile and return a list of per-cluster section dicts.

    Each dict maps section names to {off, len, num} for that cluster's
    VERTEXFRAMES, TVERTEXFRAMES, TRIANGLES, PRIMITIVES.
    Follows the tree: top-level → CLUSTER entries → child sections.
    """
    if len(data) < 32 or data[:16] != MOS_MAGIC:
        return []
    dir_offset = struct.unpack_from('<I', data, 24)[0]
    clusters = []

    def find_clusters(offset):
        while 0 < offset < len(data):
            e = _parse_entry(data, offset)
            if not e:
                break
            if e['type'] == 'CLUSTER' and 0 < e['child'] < len(data):
                sections = _collect_children(data, e['child'])
                if 'VERTEXFRAMES' in sections:
                    clusters.append(sections)
            elif 0 < e['child'] < len(data):
                find_clusters(e['child'])
            offset = e['next'] if 0 < e['next'] < len(data) else 0

    find_clusters(dir_offset)

    # Fallback: if no CLUSTER nodes found, collect top-level sections as one cluster
    if not clusters:
        sections = _collect_children(data, dir_offset)
        if 'VERTEXFRAMES' in sections:
            clusters.append(sections)

    return clusters


# ---------------------------------------------------------------------------
# VERTEXFRAMES parsing
# ---------------------------------------------------------------------------

def _parse_vf_positions(vf_data, bmin_override=None, bmax_override=None):
    """Parse vertex positions from a VERTEXFRAMES section.

    Format codes (from CVertexFrame::Read in MXR.dll sub_10087f10):
      0x200: f32 positions, hardcoded scale=1.0, header 48B, vc @48
      0x201: f32 positions, scale from stream, header 52B, vc @52
      0x202: u16 quantized positions, header 52B, vc @52
      0x204/0x205: u16 quantized (CLUSTERS variant, extra u32 prefix), header 56B, vc @52

    For code 1 (CLUSTERS with num_frames prefix):
      @0: u32 num_frames, @4: u32 format_code, then format-specific header

    Positions are SOA: u16[vc*3] contiguous, then i8[vc*3] normals.
    Dequantization: val = u16 / 65535.0 * (bmax - bmin) + bmin

    Returns (positions, normals) where each is a list of (x,y,z) tuples.
    """
    if len(vf_data) < 48:
        return [], []

    code = struct.unpack_from('<I', vf_data, 0)[0]

    # Determine header layout based on format code
    if code in (0x200, 0x201, 0x202, 0x205):
        # New format: code at @0
        # @0: u32 code, @4: Vec3 BB-related, @16: Vec3, @28: u32, @32: Vec3
        # 0x200/0x205: no scale field → vc at @48, data at @52
        # 0x201/0x202: +u32 scale → vc at @52, data at @56
        if code in (0x200, 0x205):
            vc_off, data_off, bb_off = 48, 52, 4
        else:
            vc_off, data_off, bb_off = 52, 56, 4
    elif code <= 16:
        # CLUSTERS: @0 is num_frames (small int), @4 is format code
        sub_code = struct.unpack_from('<I', vf_data, 4)[0] if len(vf_data) >= 8 else 0
        if sub_code in (0x200, 0x201, 0x202, 0x204, 0x205):
            # @0: num_frames, @4: sub_code, @8: f32 radius, @12: Vec3 BB min, @24: Vec3 BB max
            vc_off, data_off, bb_off = 52, 56, 12
        else:
            return [], []
    else:
        return [], []

    if vc_off + 4 > len(vf_data):
        return [], []
    vc = struct.unpack_from('<I', vf_data, vc_off)[0]
    if vc == 0 or vc > 500000:
        return [], []
    if data_off + vc * 6 > len(vf_data):
        return [], []

    # Bounding box for u16 dequantization
    bmin = bmin_override
    bmax = bmax_override
    if bmin is None and bb_off + 24 <= len(vf_data):
        bmin = struct.unpack_from('<3f', vf_data, bb_off)
        bmax = struct.unpack_from('<3f', vf_data, bb_off + 12)

    if code == 0x200:
        # f32 positions: 12 bytes per vertex, SOA
        if data_off + vc * 12 > len(vf_data):
            return [], []
        positions = []
        for i in range(vc):
            off = data_off + i * 12
            x, y, z = struct.unpack_from('<3f', vf_data, off)
            positions.append((x, y, z))
        # f32 normals follow positions (from MXR.dll sub_10087f10 code 0x200 path)
        norm_off = data_off + vc * 12
        normals = _read_normals_f32(vf_data, norm_off, vc)
        return positions, normals

    # u16 quantized positions (0x201, 0x202, 0x204, 0x205)
    if not bmin or not bmax:
        return [], []

    positions = []
    for i in range(vc):
        off = data_off + i * 6
        px, py, pz = struct.unpack_from('<3H', vf_data, off)
        x = bmin[0] + px / 65535.0 * (bmax[0] - bmin[0])
        y = bmin[1] + py / 65535.0 * (bmax[1] - bmin[1])
        z = bmin[2] + pz / 65535.0 * (bmax[2] - bmin[2])
        positions.append((x, y, z))

    # i8 normals follow positions (from MXR.dll: i8[vc*3] scaled by 1/127)
    norm_off = data_off + vc * 6
    normals = _read_normals_i8(vf_data, norm_off, vc)
    return positions, normals


# ---------------------------------------------------------------------------
# Normal reading helpers
# ---------------------------------------------------------------------------

def _read_normals_i8(vf_data, norm_off, vc):
    """Read i8 SOA normals, scaled by 1/127 (from MXR.dll decompile)."""
    if norm_off + vc * 3 > len(vf_data):
        return []
    normals = []
    for i in range(vc):
        off = norm_off + i * 3
        nx, ny, nz = struct.unpack_from('<3b', vf_data, off)
        normals.append((nx / 127.0, ny / 127.0, nz / 127.0))
    return normals


def _read_normals_f32(vf_data, norm_off, vc):
    """Read f32 SOA normals (code 0x200 path)."""
    if norm_off + vc * 12 > len(vf_data):
        return []
    normals = []
    for i in range(vc):
        off = norm_off + i * 12
        nx, ny, nz = struct.unpack_from('<3f', vf_data, off)
        normals.append((nx, ny, nz))
    return normals


# ---------------------------------------------------------------------------
# TVERTEXFRAMES parsing (UV coordinates)
# ---------------------------------------------------------------------------

def _parse_tvertexframes(tvf_data):
    """Parse UV coordinates from TVERTEXFRAMES section.

    Format (from MXR.dll sub_10088f00):
      @0: u32 vertex_count
      @4: f32 umin, f32 vmin, f32 umax, f32 vmax
      @20: vc pairs of u16 (u, v)
    Dequantization: u = umin + u16/65535 * (umax - umin)
    """
    if len(tvf_data) < 20:
        return []
    vc = struct.unpack_from('<I', tvf_data, 0)[0]
    if vc == 0 or vc > 500000:
        return []
    umin, vmin, umax, vmax = struct.unpack_from('<4f', tvf_data, 4)
    if 20 + vc * 4 > len(tvf_data):
        return []
    uvs = []
    for i in range(vc):
        off = 20 + i * 4
        u16, v16 = struct.unpack_from('<2H', tvf_data, off)
        u = umin + u16 / 65535.0 * (umax - umin)
        v = vmin + v16 / 65535.0 * (vmax - vmin)
        uvs.append((u, v))
    return uvs


# ---------------------------------------------------------------------------
# PRIMITIVES parsing (triangle strips with group markers)
# ---------------------------------------------------------------------------

def _parse_primitives(pr_data, max_verts):
    """Parse PRIMITIVES section into flat triangle index list.

    Group format: u8 type + u8 total_u16_count + u8 extra + u8 pad
    Then (total_u16_count - 2) u16 strip indices.
    Types: 0x03=strip, 0x05=strip, 0x07=strip. All treated as triangle strips.
    """
    off = 0
    triangles = []

    # CLUSTERS format has a 4-byte count prefix (u16 count + u16 pad)
    if len(pr_data) >= 8 and pr_data[0] not in (0x01, 0x03, 0x05, 0x07):
        off = 4

    while off + 4 <= len(pr_data):
        ptype = pr_data[off]
        if ptype not in (0x01, 0x03, 0x05, 0x07):
            break
        total_count = pr_data[off + 1]
        off += 4

        strip_len = total_count - 2
        if strip_len <= 0:
            continue

        indices = []
        for j in range(strip_len):
            if off + 2 > len(pr_data):
                break
            indices.append(struct.unpack_from('<H', pr_data, off)[0])
            off += 2

        for j in range(len(indices) - 2):
            a, b, c = indices[j], indices[j + 1], indices[j + 2]
            if a == b or b == c or a == c:
                continue
            if max(a, b, c) >= max_verts:
                continue
            if j % 2 == 0:
                triangles.extend([a, b, c])
            else:
                triangles.extend([b, a, c])

    return triangles


# ---------------------------------------------------------------------------
# KEYS parsing
# ---------------------------------------------------------------------------

def _parse_keys(data, entries):
    """Extract model name from KEYS section."""
    e = None
    for entry in entries:
        if entry.get('type') == 'KEYS' and entry.get('len', 0) > 0:
            e = entry
            break
    if not e:
        return ""
    off = e['off']
    length = e['len']
    section = data[off:off + length]
    if len(section) < 8:
        return ""
    try:
        num_keys = struct.unpack_from('<I', section, 0)[0]
        pos = 8
        for _ in range(num_keys):
            if pos + 4 > len(section):
                break
            klen = struct.unpack_from('<I', section, pos)[0]
            pos += 4
            if pos + klen > len(section):
                break
            key = section[pos:pos + klen].split(b'\x00')[0].decode('ascii', errors='replace')
            pos += klen
            if pos + 4 > len(section):
                break
            vlen = struct.unpack_from('<I', section, pos)[0]
            pos += 4
            if pos + vlen > len(section):
                break
            val = section[pos:pos + vlen].split(b'\x00')[0].decode('ascii', errors='replace')
            pos += vlen
            if key == "MODEL":
                return os.path.splitext(os.path.basename(val))[0]
    except Exception:
        pass
    return ""


# ---------------------------------------------------------------------------
# Parse a single cluster from CDataFile entries
# ---------------------------------------------------------------------------

def _parse_triangles_flat(tri_data, num_tris, max_verts):
    """Parse TRIANGLES section as flat u16 triplets.

    Handles optional 4-byte prefix (u16 count + u16 pad) in CLUSTERS format.
    """
    off = 0
    # Check for 4-byte prefix: first u16 should equal num_tris
    if len(tri_data) >= 4:
        prefix_count = struct.unpack_from('<H', tri_data, 0)[0]
        if prefix_count == num_tris and len(tri_data) >= 4 + num_tris * 6:
            off = 4

    triangles = []
    for i in range(num_tris):
        if off + 6 > len(tri_data):
            break
        a, b, c = struct.unpack_from('<3H', tri_data, off)
        off += 6
        if max(a, b, c) < max_verts:
            triangles.extend([a, b, c])
    return triangles


def _parse_cluster_from_entries(cdf_data, sections, bmin=None, bmax=None):
    """Parse a single cluster's geometry from section dict.

    sections: dict of {name: {off, len, num}} from CDataFile.
    Returns XMDMesh or None.
    """
    if 'VERTEXFRAMES' not in sections:
        return None
    if 'TRIANGLES' not in sections and 'PRIMITIVES' not in sections:
        return None

    vf_info = sections['VERTEXFRAMES']
    vf_data = cdf_data[vf_info['off']:vf_info['off'] + vf_info['len']]
    positions, normals = _parse_vf_positions(vf_data, bmin, bmax)
    if not positions:
        return None

    # Prefer TRIANGLES (flat list) over PRIMITIVES (strips) — simpler, more reliable
    triangles = []
    if 'TRIANGLES' in sections:
        tri_info = sections['TRIANGLES']
        tri_data = cdf_data[tri_info['off']:tri_info['off'] + tri_info['len']]
        triangles = _parse_triangles_flat(tri_data, tri_info['num'], len(positions))

    if not triangles and 'PRIMITIVES' in sections:
        pr_info = sections['PRIMITIVES']
        pr_data = cdf_data[pr_info['off']:pr_info['off'] + pr_info['len']]
        triangles = _parse_primitives(pr_data, len(positions))

    if not triangles:
        return None

    mesh = XMDMesh()
    mesh.positions = positions
    mesh.normals = normals
    mesh.triangles = triangles

    # Parse UVs from TVERTEXFRAMES
    if 'TVERTEXFRAMES' in sections:
        tvf_info = sections['TVERTEXFRAMES']
        if tvf_info['len'] > 20:
            tvf_data = cdf_data[tvf_info['off']:tvf_info['off'] + tvf_info['len']]
            mesh.uvs = _parse_tvertexframes(tvf_data)

    return mesh


def _get_cluster_bb(cdf_data, sections):
    """Extract per-cluster bounding box from MISCELLANEOUS section.

    MISCELLANEOUS layout: variable prefix then Vec3 BB min + Vec3 BB max.
    BB offset is at byte 12 of the MISC data.
    """
    if 'MISCELLANEOUS' not in sections:
        return None, None
    misc = sections['MISCELLANEOUS']
    if misc['len'] < 36:
        return None, None
    misc_data = cdf_data[misc['off']:misc['off'] + misc['len']]
    bmin = struct.unpack_from('<3f', misc_data, 12)
    bmax = struct.unpack_from('<3f', misc_data, 24)
    if (all(bmax[i] >= bmin[i] for i in range(3)) and
            any(bmax[i] - bmin[i] > 0.001 for i in range(3))):
        return bmin, bmax
    return None, None


# ---------------------------------------------------------------------------
# Variant 1: Uncompressed CLUSTERS
# ---------------------------------------------------------------------------

def _parse_clusters_uncompressed(data, outer_entries, verbose=False):
    """Parse uncompressed CLUSTERS variant.

    Navigates the directory tree to find the FIRST EXTENDEDMODEL's geometry,
    avoiding duplicate LOD levels. Finds CLUSTER entries within the CLUSTERS
    subtree and extracts per-cluster sections.
    """
    meshes = []

    # Find BOUND from outer entries (first EXTENDEDMODEL level)
    bound_entry = next((e for e in outer_entries if e['type'] == 'BOUND' and e['len'] >= 28), None)
    bmin = bmax = None
    if bound_entry:
        bd = data[bound_entry['off']:bound_entry['off'] + 28]
        bmin = struct.unpack_from('<3f', bd, 0)
        bmax = struct.unpack_from('<3f', bd, 12)

    # Find the first CLUSTERS or CLUSTERDATA entry and navigate its CLUSTER children
    # Use the tree walker to find CLUSTER entries with their per-cluster sections
    dir_offset = struct.unpack_from('<I', data, 24)[0] if len(data) >= 28 else 0

    # Walk tree to find first EXTENDEDMODEL → CLUSTERS → CLUSTER entries
    cluster_sections_list = []

    def find_first_em_clusters(offset):
        """Find CLUSTER entries under the first EXTENDEDMODEL."""
        while 0 < offset < len(data):
            e = _parse_entry(data, offset)
            if not e:
                break
            if e['type'] == 'EXTENDEDMODEL' and 0 < e['child'] < len(data):
                # Found first EXTENDEDMODEL — search its children for CLUSTERS
                _find_clusters_in(e['child'])
                return  # Only use first EXTENDEDMODEL (highest LOD)
            offset = e['next'] if 0 < e['next'] < len(data) else 0

    def _find_clusters_in(offset):
        """Recursively find CLUSTER entries and collect their sections."""
        while 0 < offset < len(data):
            e = _parse_entry(data, offset)
            if not e:
                break
            if e['type'] == 'CLUSTER' and 0 < e['child'] < len(data):
                sections = _collect_children(data, e['child'])
                if 'VERTEXFRAMES' in sections:
                    cluster_sections_list.append(sections)
            elif e['type'] in ('CLUSTERS', 'CLUSTERDATA', 'VERTEXBUFFERS',
                               'VERTEXBUFFER') and 0 < e['child'] < len(data):
                _find_clusters_in(e['child'])
            offset = e['next'] if 0 < e['next'] < len(data) else 0

    find_first_em_clusters(dir_offset)

    # Fallback: if tree walk found nothing, use flat list from first LOD
    if not cluster_sections_list:
        vf_list = [e for e in outer_entries if e['type'] == 'VERTEXFRAMES' and e['len'] > 0]
        tr_list = [e for e in outer_entries if e['type'] == 'TRIANGLES' and e['len'] > 0]
        for i in range(min(len(vf_list), len(tr_list))):
            sections = {
                'VERTEXFRAMES': {'off': vf_list[i]['off'], 'len': vf_list[i]['len'], 'num': vf_list[i]['num']},
                'TRIANGLES': {'off': tr_list[i]['off'], 'len': tr_list[i]['len'], 'num': tr_list[i]['num']},
            }
            cluster_sections_list.append(sections)

    for i, sections in enumerate(cluster_sections_list):
        # Use per-cluster BB from MISCELLANEOUS, fall back to outer BOUND
        c_bmin, c_bmax = _get_cluster_bb(data, sections)
        if c_bmin is None:
            c_bmin, c_bmax = bmin, bmax
        mesh = _parse_cluster_from_entries(data, sections, c_bmin, c_bmax)
        if mesh:
            meshes.append(mesh)
            if verbose:
                print(f"[XMD] Cluster {i}: {len(mesh.positions)}v {len(mesh.triangles) // 3}t",
                      file=sys.stderr)

    return meshes


# ---------------------------------------------------------------------------
# Variant 2: Compressed COMPRESSEDCLUSTERS
# ---------------------------------------------------------------------------

def _parse_clusters_compressed(data, outer_entries, verbose=False):
    """Parse compressed COMPRESSEDCLUSTERS variant."""
    meshes = []

    cc_entry = next((e for e in outer_entries
                     if 'COMPRESSEDCLUSTER' in e['type'] and e['len'] > 28), None)
    if not cc_entry:
        return meshes

    bound_entry = next((e for e in outer_entries if e['type'] == 'BOUND' and e['len'] >= 28), None)
    bmin = bmax = None
    if bound_entry:
        bd = data[bound_entry['off']:bound_entry['off'] + 28]
        bmin = struct.unpack_from('<3f', bd, 0)
        bmax = struct.unpack_from('<3f', bd, 12)

    cc_data = data[cc_entry['off']:cc_entry['off'] + cc_entry['len']]

    if verbose:
        decomp_size = struct.unpack_from('<I', cc_data, 0)[0]
        print(f"[XMD] COMPRESSEDCLUSTERS: {cc_entry['len']}B -> {decomp_size}B decompressed",
              file=sys.stderr)

    try:
        decompressed = _decompress_lzss_huffman(cc_data)
    except Exception as e:
        if verbose:
            print(f"[XMD] Decompression failed: {e}", file=sys.stderr)
        return meshes

    if len(decompressed) < 48 or decompressed[:16] != MOS_MAGIC:
        if verbose:
            print("[XMD] Decompressed data is not a valid CDataFile", file=sys.stderr)
        return meshes

    # Parse the decompressed CDataFile — extract ALL clusters
    cluster_list = _read_cdf_clusters(decompressed)

    if verbose:
        print(f"[XMD] Found {len(cluster_list)} cluster(s) in decompressed data",
              file=sys.stderr)

    for ci, cdf_sections in enumerate(cluster_list):
        # Use per-cluster BB from MISCELLANEOUS, fall back to outer BOUND
        c_bmin, c_bmax = _get_cluster_bb(decompressed, cdf_sections)
        if c_bmin is None:
            c_bmin, c_bmax = bmin, bmax
        mesh = _parse_cluster_from_entries(decompressed, cdf_sections, c_bmin, c_bmax)
        if mesh:
            meshes.append(mesh)
            if verbose:
                print(f"[XMD] Cluster {ci}: {len(mesh.positions)}v {len(mesh.triangles) // 3}t",
                      file=sys.stderr)

    return meshes


# ---------------------------------------------------------------------------
# Main parse function
# ---------------------------------------------------------------------------

def parse_xmd(path, verbose=False):
    """Parse a Starbreeze XMD model file."""
    model = XMDModel()
    try:
        with open(path, 'rb') as f:
            data = f.read()
    except Exception as e:
        if verbose:
            print(f"[XMD] Error reading: {e}", file=sys.stderr)
        return model

    if len(data) < 48 or data[:16] != MOS_MAGIC:
        return model

    entries = _read_mos_directory(data)
    if verbose:
        print(f"[XMD] {len(entries)} directory entries", file=sys.stderr)

    has_compressed = any('COMPRESSEDCLUSTER' in e['type'] for e in entries)
    has_clusters = any(e['type'] == 'CLUSTERS' for e in entries)
    has_vf = any(e['type'] == 'VERTEXFRAMES' for e in entries)

    if has_compressed:
        model.variant = "COMPRESSEDCLUSTERS"
        if verbose:
            print("[XMD] Variant: COMPRESSEDCLUSTERS", file=sys.stderr)
        try:
            model.meshes = _parse_clusters_compressed(data, entries, verbose)
        except Exception as e:
            if verbose:
                print(f"[XMD] Error: {e}", file=sys.stderr)
    elif has_clusters or has_vf:
        model.variant = "CLUSTERS"
        if verbose:
            print("[XMD] Variant: CLUSTERS (uncompressed)", file=sys.stderr)
        try:
            model.meshes = _parse_clusters_uncompressed(data, entries, verbose)
        except Exception as e:
            if verbose:
                print(f"[XMD] Error: {e}", file=sys.stderr)

    # Model name from KEYS
    model.name = _parse_keys(data, entries) or os.path.splitext(os.path.basename(path))[0]

    if verbose:
        total_v = sum(len(m.positions) for m in model.meshes)
        total_t = sum(len(m.triangles) // 3 for m in model.meshes)
        print(f"[XMD] Result: {len(model.meshes)} mesh(es), {total_v} verts, {total_t} tris",
              file=sys.stderr)

    return model


# ---------------------------------------------------------------------------
# GLB conversion
# ---------------------------------------------------------------------------

def _face_normal(p0, p1, p2):
    e1 = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
    e2 = (p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2])
    nx = e1[1] * e2[2] - e1[2] * e2[1]
    ny = e1[2] * e2[0] - e1[0] * e2[2]
    nz = e1[0] * e2[1] - e1[1] * e2[0]
    mag = math.sqrt(nx * nx + ny * ny + nz * nz)
    if mag > 1e-10:
        return (nx / mag, ny / mag, nz / mag)
    return (0.0, 0.0, 1.0)


def convert_to_glb(model, output_path, verbose=False):
    """Convert an XMDModel to GLB format."""
    builder = GLBBuilder(verbose=verbose)

    if not model.meshes:
        glb_data = builder.build_glb(generator="poly2glb-starbreezeModel")
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

        # Flat shading with face normals — gives clear visual definition without textures
        gp, gn, gi, gu = [], [], [], []
        for t in range(0, len(mesh.triangles) - 2, 3):
            i0, i1, i2 = mesh.triangles[t], mesh.triangles[t + 1], mesh.triangles[t + 2]
            if max(i0, i1, i2) >= len(mesh.positions):
                continue
            p0, p1, p2 = mesh.positions[i0], mesh.positions[i1], mesh.positions[i2]
            fn = _face_normal(p0, p1, p2)
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
            # Add UVs as TEXCOORD_0
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

    glb_data = builder.build_glb(generator="poly2glb-starbreezeModel")
    with open(output_path, 'wb') as f:
        f.write(glb_data)

    if verbose:
        print(f"[XMD] GLB written: {output_path} ({len(glb_data) / 1024:.1f} KB)",
              file=sys.stderr)

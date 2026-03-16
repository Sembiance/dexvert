# Vibe coded by Claude
"""
SketchUp SKP binary file parser and GLB converter.

Parses the proprietary MFC CArchive-based SKP format to extract geometry,
materials, textures, and scene hierarchy. Converts to GLB (glTF Binary).
"""

import struct
import sys
import math
import os

from glb import (GLBBuilder, ear_clip, merge_polygon_holes,
                 is_convex_polygon, fan_triangulate, convex_hull_2d)


class BinaryReader:
    """Low-level binary stream reader with position tracking."""

    def __init__(self, data):
        self.data = data
        self.pos = 0
        self.size = len(data)

    def tell(self):
        return self.pos

    def seek(self, pos):
        self.pos = pos

    def skip(self, n):
        self.pos += n

    def remaining(self):
        return self.size - self.pos

    def read(self, n):
        if self.pos + n > self.size:
            raise EOFError(f"Read past end at {hex(self.pos)}, need {n} bytes")
        result = self.data[self.pos:self.pos + n]
        self.pos += n
        return result

    def u8(self):
        val = self.data[self.pos]
        self.pos += 1
        return val

    def u16(self):
        val = struct.unpack_from('<H', self.data, self.pos)[0]
        self.pos += 2
        return val

    def i16(self):
        val = struct.unpack_from('<h', self.data, self.pos)[0]
        self.pos += 2
        return val

    def u32(self):
        val = struct.unpack_from('<I', self.data, self.pos)[0]
        self.pos += 4
        return val

    def i32(self):
        val = struct.unpack_from('<i', self.data, self.pos)[0]
        self.pos += 4
        return val

    def f64(self):
        val = struct.unpack_from('<d', self.data, self.pos)[0]
        self.pos += 8
        return val

    def peek_u8(self):
        return self.data[self.pos]

    def peek_u16(self):
        return struct.unpack_from('<H', self.data, self.pos)[0]

    def peek_u32(self):
        return struct.unpack_from('<I', self.data, self.pos)[0]

    def wstring(self):
        """Read FF FE FF + 1-byte length + UTF-16LE string (v5+ format)."""
        magic = self.read(3)
        if magic != b'\xff\xfe\xff':
            raise ValueError(f"Bad wstring magic at {hex(self.pos - 3)}: {magic.hex()}")
        n = self.u8()
        if n == 0:
            return ""
        text = self.read(n * 2).decode('utf-16-le')
        return text

    def astring(self):
        """Read 1-byte length + ASCII string (v3 format)."""
        n = self.u8()
        if n == 0:
            return ""
        return self.read(n).decode('ascii', errors='replace')


class Vertex:
    __slots__ = ['x', 'y', 'z', 'map_idx', 'scope']

    def __init__(self, x, y, z, map_idx=0, scope=0):
        self.x = x
        self.y = y
        self.z = z
        self.map_idx = map_idx
        self.scope = scope

    def __repr__(self):
        return f"V({self.x:.4f}, {self.y:.4f}, {self.z:.4f})"

    def coords(self):
        return (self.x, self.y, self.z)


class Edge:
    __slots__ = ['start_vertex', 'end_vertex', 'soft', 'smooth', 'map_idx']

    def __init__(self, start_vertex, end_vertex, soft=False, smooth=False, map_idx=0):
        self.start_vertex = start_vertex
        self.end_vertex = end_vertex
        self.soft = soft
        self.smooth = smooth
        self.map_idx = map_idx


class Face:
    __slots__ = ['normal', 'distance', 'vertices', 'holes', 'material_idx',
                 'back_material_idx', 'uv_front', 'uv_back', 'map_idx', 'scope',
                 '_edge_uses', 'loop_count', 'eu_assigned', '_tagless_pos',
                 'has_texture_coords']

    def __init__(self, normal, distance, vertices=None, map_idx=0, scope=0):
        self.normal = normal
        self.distance = distance
        self.vertices = vertices or []
        self.holes = []  # list of vertex lists for inner loops (holes)
        self.material_idx = -1
        self.back_material_idx = -1
        self.uv_front = None
        self.uv_back = None
        self.map_idx = map_idx
        self.scope = scope
        self.eu_assigned = False
        self._edge_uses = []
        self.loop_count = 1
        self._tagless_pos = -1
        self.has_texture_coords = False


class Material:
    __slots__ = ['name', 'color', 'opacity', 'texture_data', 'texture_filename',
                 'has_texture', 'map_idx']

    def __init__(self, name="", color=(128, 128, 128, 255), map_idx=0):
        self.name = name
        self.color = color
        self.opacity = 1.0
        self.texture_data = None
        self.texture_filename = ""
        self.has_texture = False
        self.map_idx = map_idx


class ComponentDef:
    __slots__ = ['name', 'description', 'faces', 'edges', 'vertices',
                 'sub_instances', 'sub_groups', 'map_idx']

    def __init__(self, name="", map_idx=0):
        self.name = name
        self.description = ""
        self.faces = []
        self.edges = []
        self.vertices = []
        self.sub_instances = []
        self.sub_groups = []
        self.map_idx = map_idx


class ComponentInstance:
    __slots__ = ['definition', 'transform', 'name', 'map_idx', 'material_idx']

    def __init__(self, definition=None, transform=None, name="", map_idx=0):
        self.definition = definition
        self.transform = transform or [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
        self.name = name
        self.map_idx = map_idx
        self.material_idx = -1


class Group:
    __slots__ = ['transform', 'name', 'faces', 'edges', 'vertices',
                 'sub_instances', 'sub_groups', 'map_idx']

    def __init__(self, name="", map_idx=0):
        self.name = name
        self.transform = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
        self.faces = []
        self.edges = []
        self.vertices = []
        self.sub_instances = []
        self.sub_groups = []
        self.map_idx = map_idx


class SKPModel:
    """Holds all parsed data from an SKP file."""

    def __init__(self):
        self.version_major = 0
        self.version_string = ""
        self.version_map = {}
        self.vertices = []
        self.edges = []
        self.faces = []
        self.materials = []
        self.component_defs = []
        self.component_instances = []
        self.groups = []
        self.layers = []
        self.camera = None
        self.thumbnail_png = None
        # Geometry ranges per definition for mesh instancing
        # def_ref -> (face_start, face_end)
        self.def_face_ranges = {}
        # CI transforms grouped by definition for to_glb instancing
        # def_ref -> [transform, ...]
        self.ci_transforms = {}
        # Group transforms: scope_num -> 13-double transform
        # Groups with non-identity transforms get separate mesh nodes in glTF
        self.group_transforms = {}
        # Group face ranges: scope_num -> (face_start, face_end)
        self.group_face_ranges = {}


class MFCArchive:
    """
    Handles MFC CArchive-style object serialization/deserialization.
    Tracks the class and object maps for back-references.
    """

    def __init__(self, reader, file_version, verbose=False):
        self.r = reader
        self.file_version = file_version
        self.verbose = verbose
        self.class_map = {}   # map_index -> class_name
        self.object_map = {}  # map_index -> object
        self.map_count = 0

    def log(self, msg):
        if self.verbose:
            print(f"  [{hex(self.r.tell())}] {msg}", file=sys.stderr)

    def next_map_idx(self):
        self.map_count += 1
        return self.map_count

    def register_class(self, name):
        idx = self.next_map_idx()
        self.class_map[idx] = name
        return idx

    def register_object(self, obj):
        idx = self.next_map_idx()
        self.object_map[idx] = obj
        return idx

    def set_object(self, idx, obj):
        self.object_map[idx] = obj

    def get_object(self, idx):
        return self.object_map.get(idx)

    def find_class_idx(self, class_name):
        """Find the map index for a previously registered class."""
        for idx, name in self.class_map.items():
            if name == class_name:
                return idx
        return None

    def read_object_tag(self):
        """
        Read the MFC object header tag.
        Returns: (class_name, is_new_object, obj_map_idx)
        """
        tag = self.r.u16()

        if tag == 0x0000:
            return None, False, 0

        if tag == 0xFFFF:
            schema = self.r.u16()
            namelen = self.r.u16()
            if namelen > 100 or namelen == 0:
                # Invalid name length - rewind and report failure
                self.r.seek(self.r.tell() - 6)
                return None, False, -1
            raw = self.r.read(namelen)
            try:
                name = raw.decode('ascii')
            except UnicodeDecodeError:
                # Not a valid class name - rewind
                self.r.seek(self.r.tell() - 6 - namelen)
                return None, False, -1
            class_idx = self.register_class(name)
            obj_idx = self.register_object(None)
            self.log(f"NEW {name} schema={schema} class@{class_idx} obj@{obj_idx}")
            return name, True, obj_idx

        if tag >= 0x8000:
            class_idx = tag & 0x7FFF
            if class_idx in self.class_map:
                name = self.class_map[class_idx]
                obj_idx = self.register_object(None)
                self.log(f"INST {name} (class@{class_idx}) obj@{obj_idx}")
                return name, True, obj_idx
            else:
                # Not a valid class ref, rewind
                self.r.seek(self.r.tell() - 2)
                return None, False, -1

        # Object back-reference (1 <= tag <= 0x7FFF)
        self.log(f"REF obj@{tag}")
        return '__ref__', False, tag

    def peek_is_object_tag(self):
        """Check if next u16 looks like a valid MFC tag."""
        if self.r.remaining() < 2:
            return False
        tag = self.r.peek_u16()
        if tag == 0x0000:
            return True
        if tag == 0xFFFF:
            return True
        if tag >= 0x8000:
            class_idx = tag & 0x7FFF
            return class_idx in self.class_map
        if 0 < tag <= self.map_count:
            return True
        return False


class SKPParser:
    """Main parser for SketchUp SKP files."""

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.model = SKPModel()
        self.arc = None
        self.current_scope = 0  # incremented per CComponentDefinition/CGroup
        self._next_scope_id = 1  # monotonically increasing unique scope ID
        self.in_geometry = False  # set True after first geometry FFFF intro
        # Scope tracking for component transforms
        self._scope_stack = []  # stack of (type, map_idx, scope_num)
        self._scope_map = {}  # map_idx -> scope_num
        self._scope_types = {}  # map_idx -> scope_type ('CComponentDefinition' or 'CGroup')
        self._pending_transforms = []  # (scope_num, transform_13doubles)
        self._has_tagless_faces = False  # Set when tagless faces detected
        self._class_offset = 0  # detected offset between writer's and our class indices
        self._def_geo_start = {}  # def_map_idx -> (vert_start, edge_start, face_start)
        self._edgeuse_chains = {}  # eu_map_idx -> {edge_ref, reversed, loop_ref, next_ref}
        self._loop_to_face = {}  # loop_map_idx -> Face object
        self._v1_scope_transforms = {}  # scope_num -> 13-double placement transform (v1 only)
        self._scope_parent = {}  # child_scope -> parent_scope (for nested transform composition)
        self._v1_ci_cd_scopes = set()  # scope nums opened by CI+CD pairs (v1 only)
        self._v1_last_was_ci = False  # flag: previous entity was a v1 CI+CD pair
        self._cut_opening_pairs = []  # (face_obj_idx, ci_obj_idx) from CRelationship
        self._uses_wstring = False  # True if file uses UTF-16 wstring encoding

    def log(self, msg):
        if self.verbose:
            print(f"[SKP] {msg}", file=sys.stderr)

    def parse(self, filepath):
        """Parse an SKP file and return an SKPModel."""
        with open(filepath, 'rb') as f:
            data = f.read()

        self.log(f"File size: {len(data)} bytes")
        r = BinaryReader(data)

        self._parse_header(r)
        self._parse_data(r)

        return self.model

    def _read_string(self, r):
        if self._uses_wstring:
            return r.wstring()
        else:
            return r.astring()

    def _parse_header(self, r):
        """Parse header and version map."""
        # Detect encoding by first bytes: FF FE FF = UTF-16 wstring format
        if r.data[0:3] == b'\xff\xfe\xff':
            self._uses_wstring = True
            header = r.wstring()
            version = r.wstring()
        else:
            self._uses_wstring = False
            n = r.u8()
            header = r.read(n).decode('ascii')
            n = r.u8()
            version = r.read(n).decode('ascii')

        if "SketchUp Model" not in header:
            raise ValueError(f"Not a SketchUp file: '{header}'")

        self.model.version_string = version
        ver_text = version.strip('{}')
        parts = ver_text.split('.')
        self.model.version_major = int(parts[0])
        # For v5+, always use wstring; for lower versions, keep detected encoding
        if self.model.version_major >= 5:
            self._uses_wstring = True
        self.log(f"Version: {version} (major={self.model.version_major}) "
                 f"wstring={self._uses_wstring}")

        # 16-byte checksum
        r.skip(16)

        # Post-checksum: byte-prefixed file path (v1/v2 have paths, v3+ have len=0)
        if self._uses_wstring:
            r.wstring()  # UTF-16 path
        else:
            path_len = r.u8()
            if path_len > 0:
                r.skip(path_len)  # skip embedded file save path

        # CRC/timestamp
        r.u32()

        # CVersionMap MFC class introduction: FFFF 0000 + namelen + "CVersionMap"
        ffff = r.u32()
        if ffff != 0x0000FFFF:
            raise ValueError(f"Unsupported SKP version {self.model.version_string} "
                             f"(expected CVersionMap at {hex(r.tell()-4)}, "
                             f"got {hex(ffff)})")
        vmlen = r.u16()
        vmname = r.read(vmlen).decode('ascii')
        if vmname != "CVersionMap":
            raise ValueError(f"Expected CVersionMap, got {vmname}")

        # Initialize MFC archive
        self.arc = MFCArchive(r, self.model.version_major, self.verbose)
        self.arc.register_class("CVersionMap")  # map[1]
        self.arc.register_object("CVersionMap")  # map[2]

        # Read version map entries
        while True:
            name = self._read_string(r)
            if name == "End-Of-Version-Map":
                break
            ver = r.u32()
            self.model.version_map[name] = ver

        r.u32()  # trailing 0

        self.log(f"Version map: {len(self.model.version_map)} classes")

    def _parse_data(self, r):
        """Parse the data section by first locating the CEdge section, then parsing sequentially."""
        # Pre-data values (version-dependent count)
        if self.model.version_major >= 2:
            r.u32()  # pd1
            r.u32()  # pd2 (thumbnail size hint)
        if self.model.version_major >= 6:
            r.u32()  # pd3 (only in v6+)

        # CDib thumbnail
        self._parse_cdib()

        # Now we need to find and parse the geometry.
        # Strategy: locate the first CEdge FFFF in the file, then parse everything
        # from the first CLayer onward sequentially.
        self._find_and_parse_geometry(r)

    def _parse_cdib(self):
        """Parse CDib thumbnail."""
        r = self.arc.r
        name, is_new, idx = self.arc.read_object_tag()
        if name != 'CDib':
            self.log(f"Warning: expected CDib, got {name}")
            return

        dib_type = r.u32()
        dib_size = r.u32()
        self.log(f"CDib: type={dib_type}, size={dib_size}")

        if 0 < dib_size < r.remaining():
            png_data = r.read(dib_size)
            if png_data[:4] == b'\x89PNG':
                self.model.thumbnail_png = png_data
        self.arc.set_object(idx, 'CDib')

    def _find_and_parse_geometry(self, r):
        """
        Find geometry sections by scanning for FFFF markers,
        then parse each complete entity sequentially.
        """
        data = r.data

        # Find all FFFF class introductions
        sections = []
        pos = r.tell()
        while pos < len(data) - 6:
            if data[pos] == 0xFF and data[pos + 1] == 0xFF:
                schema = struct.unpack_from('<H', data, pos + 2)[0]
                namelen = struct.unpack_from('<H', data, pos + 4)[0]
                if 1 <= namelen <= 50 and pos + 6 + namelen <= len(data):
                    try:
                        name = data[pos + 6:pos + 6 + namelen].decode('ascii')
                        if name and name[0] == 'C' and name.isalnum():
                            sections.append((name, pos))
                    except (UnicodeDecodeError, IndexError):
                        pass
            pos += 1

        self.log(f"Found sections: {[s[0] for s in sections]}")

        # Find the first MFC-tagged section after CDib to start sequential parsing.
        # This ensures CAttributeContainer, CCamera, etc. are properly registered
        # in the MFC map before geometry classes are encountered.
        first_section_pos = None
        for name, spos in sections:
            if name not in ('CVersionMap', 'CDib'):
                first_section_pos = spos
                break

        if first_section_pos is None:
            # Fallback: find geometry classes
            geo_classes = {'CEdge', 'CFace', 'CVertex', 'CLoop', 'CEdgeUse', 'CLayer',
                           'CMaterial', 'CComponentDefinition', 'CComponentInstance',
                           'CGroup', 'CDefinitionList'}
            for name, spos in sections:
                if name in geo_classes:
                    first_section_pos = spos
                    break

        if first_section_pos:
            r.seek(first_section_pos)
            self._parse_entity_list(r)
        else:
            self.log("No parseable sections found")

    def _parse_camera_inline(self, idx):
        """Parse CCamera data inline and consume extended camera/rendering data.

        v4 CCamera extended data (after 9 camera doubles):
          Camera block (80 bytes):
            aspect(f64) + far_clip(f64) + persp(u8) + fov(f64) + vp_height(f64)
            + 47 trailing bytes (zeros/flags).
          Rendering block (139 or 147 bytes):
            4 RGBA colors(16) + flags(16) + 4 RGBA colors(16) + 2 f64(16)
            + mixed(16) + u32+3 RGBA(16) + 3 u32+u8+f64(21) = 117 fixed bytes
            + tail: u32(1) + 6 zeros + u8(1) + u8(1) + 6 zeros + variable:
              if next u32 == 0: 8 more bytes + u32; else u32 is final.
        """
        r = self.arc.r
        eye = (r.f64(), r.f64(), r.f64())
        target = (r.f64(), r.f64(), r.f64())
        up = (r.f64(), r.f64(), r.f64())
        self.model.camera = {'eye': eye, 'target': target, 'up': up}
        self.arc.set_object(idx, self.model.camera)
        self.log(f"Camera: eye={eye}")

        if self.model.version_major == 4:
            # Camera extended data: 80 bytes
            r.skip(80)
            # Rendering metadata: 117 fixed + 22/30 variable tail
            r.skip(117)  # fixed rendering block
            r.skip(18)   # tail: u32(1) + 6 zeros + u8(1) + u8(1) + 6 zeros
            check = r.u32()
            if check == 0:
                r.skip(4)   # u32(0)
                r.u32()     # final count
        elif self.model.version_major == 5:
            # v5 camera: 33B extended + 32B padding + 2B flags +
            # wstring(description) + 176B fixed rendering = 247B total
            r.skip(33)   # aspect(f64) + far_clip(f64) + persp(u8) + fov(f64) + vh(f64)
            r.skip(32)   # zero padding
            r.skip(2)    # model flags
            self._read_string(r)  # model description (wstring)
            r.skip(176)  # rendering metadata (RGBA colors, shadow params, etc.)
        else:
            # v3/v6+: scan forward to find next entity
            self._scan_to_next_entity(r, max_scan=8192)

    def _read_v3_model_metadata(self, r):
        """Consume v3/v4 trailing model metadata after entity list.

        Structure (96-125 bytes):
          Font block:
            dim_font_name      astring    Dimension font name ("Arial", "MrHand", etc.)
            null               u8         0x00
            null               u8         0x00
            dim_font_height    u32        GDI LOGFONT height
            dim_font_bold      u8         Bold flag (0 or 1)
            dim_font_italic    u8         Italic flag (0 or 1)
            dim_precision      u32        Numeral precision (typically 5)
            dim_decimal        u32        Decimal precision (typically 10)
            dim_display        u32        Display mode (typically 1)
            dim_units          u32        Unit type (3 = inches)
            dim_unknown        u32        Unknown (typically 10)
            dim_axis_flag      u8         Axis display flag
            dim_color          4 bytes    RGBA dimension line color
            dim_line_mode      u16        Line mode
            dim_line_weight    f64        Line weight (typically 0.6)
          Rendering block (21 bytes):
            shadow_pad         7 bytes    Zeros / shadow settings
            shadow_byte        u8         Shadow flag (0x24 typical)
            bg_color           4 bytes    RGBA background color
            render_flag        u8         Rendering flag (0xFF typical)
            render_pad         4 bytes    Zeros
            render_u32         u32        Rendering mode (1)
          Second font (optional):
            font_ref           u16        MFC ref (0=none, >=0x8000=class backref)
            If font_ref != 0:
              text_font_name   astring    Text font name
              null             u8         0x00
              text_font_flag   u8         Font flag
              text_font_height u32        GDI LOGFONT height
          Final block:
            5 x u32                       Settings (precision, display, etc.)
            u8                            Flag
            text_color         4 bytes    RGBA text/dimension color
            ref_count          u32        Number of trailing MFC refs
            refs               N x u16    MFC object references
        """
        if r.remaining() < 30:
            return  # Not enough data for metadata

        save_pos = r.tell()

        try:
            # Font block
            dim_font = r.astring()
            r.u8()  # null
            r.u8()  # null
            dim_font_h = r.u32()
            dim_bold = r.u8()
            dim_italic = r.u8()
            for _ in range(5):
                r.u32()  # dimension format settings
            r.u8()  # axis flag
            r.skip(4)  # RGBA
            r.u16()  # line mode
            r.f64()  # line weight

            # Rendering block (21 bytes)
            r.skip(7)  # shadow padding/settings
            r.u8()  # shadow flag
            r.skip(4)  # background RGBA
            r.u8()  # render flag
            r.skip(4)  # padding
            r.u32()  # render mode

            # Optional second font
            font_ref = r.u16()
            if font_ref != 0:
                text_font = r.astring()
                r.u8()  # null
                r.u8()  # font flag
                r.u32()  # font height

            # Final block: dimension settings + color + MFC refs
            r.u32()  # precision
            r.u32()  # display mode
            r.u8()  # flag
            r.u32()  # units
            r.u8()  # flag
            r.skip(4)  # RGBA
            ref_count = r.u32()
            for _ in range(ref_count):
                r.u16()  # MFC ref

            self.log(f"v3 model metadata: dim_font='{dim_font}' "
                     f"h={dim_font_h} bold={dim_bold} "
                     f"remaining={r.remaining()}B")
        except Exception as e:
            self.log(f"v3 model metadata parse error at {hex(r.tell())}: {e}")
            # Seek to EOF on failure
            r.seek(r.size)

    def _read_v1_scope_metadata(self, r):
        """Consume v1/v2 scope-end metadata after CLayer basic data.

        v1 CD scopes: display_name + GUID(16) + def_name + null + src_path
                      + 142 fixed bytes.
        v2 CD scopes: entity_base(7) + u16 + GUID(16) + def_name + null +
                      src_path + f32 + 35 padding + transform(s) + face blocks.
                      Multiple instances encoded as CI_backref + entity(7) +
                      def_ref(u16) + transform between primary and face blocks.
                      Scopes separated by CRelationship + CLayer pairs.
        Root scope: runs to EOF (skip remaining data).
        """
        if r.remaining() < 2:
            return

        if self.model.version_major == 2:
            self._read_v2_scope_metadata(r)
            return

        # Peek: if next u16 is a valid entity tag, no metadata follows
        next_u16 = struct.unpack_from('<H', r.data, r.tell())[0]
        if next_u16 >= 0x8000 or next_u16 == 0xFFFF:
            return  # next entity immediately follows
        # Try CD scope metadata format
        save_pos = r.tell()
        try:
            dname_len = r.data[r.tell()]
            if dname_len > 50:
                raise ValueError("display_name too long for CD scope")
            r.astring()            # display_name
            r.read(16)             # GUID
            def_name = r.astring() # def_name
            r.u8()                 # null separator
            r.astring()            # source_path
            # 142 fixed bytes
            if r.remaining() < 142:
                raise ValueError("not enough data for CD scope metadata")
            r.read(142)
            # Verify: next u16 should be a valid entity tag or EOF
            valid_end = r.remaining() < 2
            if not valid_end:
                check = struct.unpack_from('<H', r.data, r.tell())[0]
                valid_end = (check >= 0x8000 or check == 0xFFFF)
            if not valid_end:
                raise ValueError(f"invalid tag after CD metadata: 0x{check:04x}")
            self.log(f"v1 CD scope metadata: '{def_name}' "
                    f"({r.tell() - save_pos}B)")
        except (ValueError, struct.error):
            # Not CD scope format — root scope, skip to EOF
            r.seek(save_pos)
            remaining = r.remaining()
            r.skip(remaining)
            self.log(f"v1 root scope metadata: skipped {remaining}B to EOF")

    def _read_v2_scope_metadata(self, r):
        """Parse v2 scope-end metadata blocks and extract transforms.

        v2 scope metadata appears after CLayer at end of file. Per-scope
        blocks appear in scope-close order (innermost first). Each block:
          entity_base(7) + u16 + GUID(16) + name(astr) + null + src(astr) +
          f32(4) + padding(35) + transform(104) + [CI instances] + face blocks.
        Scopes are separated by CRelationship(FFFF+class) + CLayer(backref).
        """
        data = r.data
        # Collect ALL CD scopes in close order (innermost first).
        # The scope_stack has scopes not yet closed; _scope_map has
        # scopes already closed by nested CD openings.
        # Close order: stack (reversed) first, then previously closed
        # scopes in reverse scope_num order.
        scope_close_order = list(reversed(self._scope_stack))
        # Add scopes from _scope_map that aren't in the stack
        stack_scopes = {sn for _, _, sn in self._scope_stack}
        prev_closed = [(mi, sn) for mi, sn in self._scope_map.items()
                       if (sn not in stack_scopes and
                           self._scope_types.get(mi) == 'CComponentDefinition')]
        # Sort by scope_num descending (higher = closed earlier)
        prev_closed.sort(key=lambda x: x[1], reverse=True)
        for mi, sn in prev_closed:
            scope_close_order.append(
                ('CComponentDefinition', mi, sn))
        scope_idx = 0

        if self._uses_wstring:
            # wstring v2: scope metadata format differs from ASCII v2.
            # Only process scope metadata if geometry classes have been
            # registered (i.e., this CLayer is a scope-end, not the initial one).
            cface_cls = self.arc.find_class_idx('CFace')
            if not cface_cls:
                # No geometry parsed yet; this is the initial CLayer.
                return
            cface_tag = 0x8000 + cface_cls
            # Scan for first CFace backref in scope metadata
            scan_start = r.tell()
            while r.remaining() > 2:
                peek = struct.unpack_from('<H', data, r.tell())[0]
                if peek == cface_tag:
                    break
                r.skip(1)
            if r.remaining() > 10:
                self._parse_v2_face_blocks(r, 0)
            remaining = r.remaining()
            if remaining > 0:
                r.skip(remaining)
                self.log(f"v2 wstring: skipped {remaining}B to EOF")
            return

        while r.remaining() > 50:
            pos = r.tell()
            # ASCII v2: scope blocks start with entity_base (4+ zero bytes)
            if not all(data[pos + j] == 0 for j in range(4)):
                break

            try:
                r.skip(7)         # entity_base (all zeros)
                mc_ref = r.u16()  # writer's map counter
                # The writer records its MFC map counter at each scope
                # block as a synchronization field.  Our counter may
                # lag because we don't deserialize every MFC object in
                # the model metadata section (CCamera, rendering, etc.).
                # Sync forward to the writer's value so that class
                # backrefs in face blocks resolve correctly.
                if mc_ref > self.arc.map_count:
                    self.arc.map_count = mc_ref
                r.read(16)        # GUID
                def_name = self._read_string(r)  # definition name
                r.u8()            # null separator
                self._read_string(r)  # source_path
                r.read(4)         # f32 bounding value
                r.read(35)        # padding/flags

                # Read primary placement transform
                if r.remaining() < 104:
                    break
                xform = struct.unpack_from('<13d', data, r.tell())
                r.skip(104)

                # Validate transform
                rot_ok = all(abs(xform[i]) <= 1.01 for i in range(9))
                scale_ok = abs(xform[12] - 1.0) < 0.01
                if not rot_ok or not scale_ok:
                    self.log(f"v2 scope '{def_name}': invalid transform, "
                            f"skipping")
                    break

                # Match to scope number
                scope_num = None
                if scope_idx < len(scope_close_order):
                    scope_type, map_idx, sn = scope_close_order[scope_idx]
                    scope_num = sn
                    self._scope_map[map_idx] = sn
                    self._scope_types[map_idx] = scope_type
                    scope_idx += 1

                is_identity = (
                    abs(xform[0]-1) < 1e-6 and abs(xform[4]-1) < 1e-6 and
                    abs(xform[8]-1) < 1e-6 and abs(xform[12]-1) < 1e-6 and
                    all(abs(xform[i]) < 1e-6
                        for i in (1, 2, 3, 5, 6, 7, 9, 10, 11)))

                # Collect all instance transforms for this scope
                all_xforms = [xform]

                # Check for additional CI instances: CI_backref(u16) +
                # entity_base(7) + def_ref(u16) + transform(104)
                # Register each as MFC object to keep counter in sync.
                while r.remaining() >= 2 + 7 + 2 + 104:
                    tag = struct.unpack_from('<H', data, r.tell())[0]
                    if tag < 0x8000 or tag == 0xFFFF:
                        break
                    # Peek ahead to validate transform
                    ci_pos = r.tell()
                    try:
                        test_xf = struct.unpack_from(
                            '<13d', data, ci_pos + 2 + 7 + 2)
                        t_rot_ok = all(abs(test_xf[i]) <= 1.01
                                       for i in range(9))
                        t_scale_ok = abs(test_xf[12] - 1.0) < 0.01
                        if not t_rot_ok or not t_scale_ok:
                            break
                    except struct.error:
                        break
                    r.skip(2)  # CI class backref tag
                    self.arc.register_object(None)  # MFC obj for CI
                    r.skip(7 + 2)  # entity_base + def_ref
                    ci_xform = struct.unpack_from('<13d', data, r.tell())
                    r.skip(104)
                    all_xforms.append(ci_xform)

                # Register transforms
                if scope_num is not None:
                    if len(all_xforms) > 1:
                        # Multiple instances: register ALL as CI transforms
                        # for mesh instancing. Don't also store in
                        # _v1_scope_transforms to avoid duplication.
                        def_map_idx = None
                        for mi, sn in self._scope_map.items():
                            if sn == scope_num:
                                def_map_idx = mi
                                break
                        if def_map_idx is not None:
                            for xf in all_xforms:
                                self._pending_transforms.append(
                                    ('ci', def_map_idx, xf))
                            self.log(
                                f"v2 scope#{scope_num} '{def_name}': "
                                f"{len(all_xforms)} instances registered"
                                f" for mesh instancing")
                    elif not is_identity:
                        # Single instance: store as placement to bake
                        # into vertices.
                        self._v1_scope_transforms[scope_num] = xform
                        self.log(
                            f"v2 scope#{scope_num} '{def_name}': "
                            f"placement T=[{xform[9]:.2f},"
                            f"{xform[10]:.2f},{xform[11]:.2f}]")

                # Parse face blocks. Face blocks after scope N's
                # metadata belong to the NEXT scope in close order
                # (the parent scope). scope_idx was already incremented,
                # so it now points to the next scope.
                if scope_idx < len(scope_close_order):
                    fb_scope = scope_close_order[scope_idx][2]
                else:
                    fb_scope = 0  # root scope
                self._parse_v2_face_blocks(r, fb_scope)

            except (struct.error, IndexError, UnicodeDecodeError):
                break

        # Close remaining scopes from stack
        while scope_idx < len(scope_close_order):
            scope_type, map_idx, sn = scope_close_order[scope_idx]
            self._scope_map[map_idx] = sn
            self._scope_types[map_idx] = scope_type
            scope_idx += 1

        # Skip remaining data to EOF (root scope metadata), but only if we
        # actually processed scope blocks. If no scopes were found, CLayer
        # appeared before geometry and the entity list continues.
        if scope_idx > 0:
            remaining = r.remaining()
            if remaining > 0:
                r.skip(remaining)
                self.log(f"v2 root scope metadata: skipped {remaining}B to EOF")

    def _parse_v2_face_blocks(self, r, fb_scope):
        """Parse scope metadata face blocks (v2) and add faces to model.

        Face blocks use class backrefs to create new MFC objects
        inline.  Each CEdgeUse references either an entity-list edge
        (object ref < 0x8000) or an inline CEdge (class backref).
        Vertices from entity-list edges that are not on the face plane
        are projected onto the plane along the normal direction.

        After face/edge entities, consumes the scope separator:
          u32(2) + CRelationship_section + padding + u32(1) + CLayer
        Two separator forms:
          - FFFF/backref: u32(2) + CRel class + 2 objects + 10 zeros
          - Lite: u32(0) + u32(2) + 2 object refs + 6 zeros
        Orphan CEdges have NO trailing bytes (unlike faces).
        """
        data = r.data
        cface_cls = self.arc.find_class_idx('CFace')
        cedge_cls = self.arc.find_class_idx('CEdge')
        cvertex_cls = self.arc.find_class_idx('CVertex')
        cloop_cls = self.arc.find_class_idx('CLoop')
        ceu_cls = self.arc.find_class_idx('CEdgeUse')
        # Find ALL class indices for each type (some files register
        # the same class multiple times with different schema versions)
        ceu_tags = set()
        for ci, cn in self.arc.class_map.items():
            if cn == 'CEdgeUse':
                ceu_tags.add(0x8000 + ci)
        cface_tag = 0x8000 + cface_cls
        cedge_tag = 0x8000 + cedge_cls
        cvertex_tag = 0x8000 + cvertex_cls
        cloop_tag = 0x8000 + cloop_cls
        ceu_tag = 0x8000 + ceu_cls

        faces_parsed = 0
        orphan_edges = 0

        while r.remaining() > 10:
            peek = struct.unpack_from('<H', data, r.tell())[0]

            if peek == cface_tag:
                # --- Parse one face block ---
                r.skip(2)
                face_idx = self.arc.register_object(None)
                r.skip(7)  # entity_base
                nx, ny, nz, d = struct.unpack_from('<4d', data, r.tell())
                r.skip(32)
                loop_count = struct.unpack_from('<I', data, r.tell())[0]
                r.skip(4)

                face = Face(normal=(nx, ny, nz), distance=d,
                            map_idx=face_idx, scope=fb_scope)
                face.loop_count = loop_count
                num_eus = 0
                num_inline_edges = 0

                for loop_i in range(loop_count):
                    if r.remaining() < 6:
                        break
                    lt = struct.unpack_from('<H', data, r.tell())[0]
                    if lt == cloop_tag:
                        r.skip(2)
                        self.arc.register_object(None)  # CLoop obj
                        r.skip(2)  # CLoop data
                    elif lt not in ceu_tags:
                        break
                    # wstring v2 may omit CLoop, going directly to CEdgeUse

                    et = struct.unpack_from('<H', data, r.tell())[0]
                    if et not in ceu_tags:
                        break
                    r.skip(2)
                    self.arc.register_object(None)  # first CEdgeUse

                    loop_verts = []
                    while True:
                        eref = struct.unpack_from('<H', data, r.tell())[0]
                        r.skip(2)

                        sv = ev = None
                        if eref >= 0x8000:
                            # Inline CEdge
                            edge_idx = self.arc.register_object(None)
                            num_inline_edges += 1
                            r.skip(7)  # entity_base
                            svr = struct.unpack_from(
                                '<H', data, r.tell())[0]
                            r.skip(2)
                            if svr >= 0x8000:
                                sv_idx = self.arc.register_object(None)
                                x, y, z = struct.unpack_from(
                                    '<3d', data, r.tell())
                                r.skip(24)
                                sv = Vertex(x, y, z, map_idx=sv_idx,
                                            scope=fb_scope)
                                self.arc.set_object(sv_idx, sv)
                                self.model.vertices.append(sv)
                            else:
                                obj = self.arc.get_object(svr)
                                if isinstance(obj, Vertex):
                                    sv = obj

                            evr = struct.unpack_from(
                                '<H', data, r.tell())[0]
                            r.skip(2)
                            if evr >= 0x8000:
                                ev_idx = self.arc.register_object(None)
                                x, y, z = struct.unpack_from(
                                    '<3d', data, r.tell())
                                r.skip(24)
                                ev = Vertex(x, y, z, map_idx=ev_idx,
                                            scope=fb_scope)
                                self.arc.set_object(ev_idx, ev)
                                self.model.vertices.append(ev)
                            else:
                                obj = self.arc.get_object(evr)
                                if isinstance(obj, Vertex):
                                    ev = obj

                            edge = Edge(sv, ev, map_idx=edge_idx)
                            self.arc.set_object(edge_idx, edge)
                            self.model.edges.append(edge)
                        else:
                            obj = self.arc.get_object(eref)
                            if isinstance(obj, Edge):
                                sv = obj.start_vertex
                                ev = obj.end_vertex

                        if self._uses_wstring:
                            # wstring v2 face blocks: edge_ref only, no rev/loop/next
                            rev = 0
                        else:
                            # ASCII v2: reversed(u8) + loop_ref(u16) + next_ref(u16)
                            rev = data[r.tell()]
                            r.skip(1)
                            r.skip(2)  # loop_ref
                            r.skip(2)  # next_ref
                        num_eus += 1

                        vert = ev if rev else sv
                        if isinstance(vert, Vertex):
                            # Project onto face plane if off-plane
                            dist = (nx * vert.x + ny * vert.y
                                    + nz * vert.z + d)
                            if abs(dist) > 0.1:
                                vert = Vertex(
                                    vert.x - dist * nx,
                                    vert.y - dist * ny,
                                    vert.z - dist * nz,
                                    map_idx=0, scope=fb_scope)
                            loop_verts.append(vert)

                        # Check what's next
                        if r.remaining() < 2:
                            break
                        nr = struct.unpack_from(
                            '<H', data, r.tell())[0]
                        if nr in ceu_tags:
                            # New CEdgeUse tag — continue chain
                            r.skip(2)
                            self.arc.register_object(None)
                            continue
                        elif self._uses_wstring and (
                                nr == cedge_tag or
                                (0 < nr < 0x8000)):
                            # wstring v2: edge_refs chain without
                            # CEdgeUse tags between entries
                            continue
                        else:
                            break

                    if loop_i == 0:
                        face.vertices = loop_verts
                    else:
                        face.holes.append(loop_verts)

                if self._uses_wstring:
                    # wstring v2: skip to next CFace, CEdge, or end
                    while r.remaining() >= 2:
                        peek_trail = struct.unpack_from(
                            '<H', data, r.tell())[0]
                        if peek_trail == cface_tag or peek_trail == cedge_tag:
                            break
                        r.skip(2)
                else:
                    # ASCII v2: skip trailing EU refs + separator + edge refs
                    trailing = num_eus * 2 + 2 + num_inline_edges * 2
                    if r.remaining() >= trailing:
                        r.skip(trailing)

                self.model.faces.append(face)
                self.arc.set_object(face_idx, face)
                faces_parsed += 1

            elif peek == cedge_tag:
                # Orphan inline CEdge after face blocks
                r.skip(2)
                edge_idx = self.arc.register_object(None)
                r.skip(7)  # entity_base
                svr = struct.unpack_from('<H', data, r.tell())[0]
                r.skip(2)
                sv = None
                if svr >= 0x8000:
                    sv_idx = self.arc.register_object(None)
                    x, y, z = struct.unpack_from('<3d', data, r.tell())
                    r.skip(24)
                    sv = Vertex(x, y, z, map_idx=sv_idx, scope=fb_scope)
                    self.arc.set_object(sv_idx, sv)
                else:
                    obj = self.arc.get_object(svr)
                    if isinstance(obj, Vertex):
                        sv = obj
                evr = struct.unpack_from('<H', data, r.tell())[0]
                r.skip(2)
                ev = None
                if evr >= 0x8000:
                    ev_idx = self.arc.register_object(None)
                    x, y, z = struct.unpack_from('<3d', data, r.tell())
                    r.skip(24)
                    ev = Vertex(x, y, z, map_idx=ev_idx, scope=fb_scope)
                    self.arc.set_object(ev_idx, ev)
                else:
                    obj = self.arc.get_object(evr)
                    if isinstance(obj, Vertex):
                        ev = obj
                edge = Edge(sv, ev, map_idx=edge_idx)
                self.arc.set_object(edge_idx, edge)
                self.model.edges.append(edge)
                orphan_edges += 1

            else:
                break  # End of face/edge entities

        if faces_parsed or orphan_edges:
            self.log(f"v2 scope face blocks: {faces_parsed} faces"
                     f" {orphan_edges} orphan edges for scope#{fb_scope}")

        # --- Parse scope separator ---
        # Two formats:
        #   FFFF/backref: u32(2) + CRel_section + 10_zeros + u32(1) + CLayer
        #   Lite:         u32(0) + u32(2) + 2_refs + 6_zeros + u32(1) + CLayer
        if r.remaining() < 20:
            return
        prefix = struct.unpack_from('<I', data, r.tell())[0]
        if prefix == 0:
            # Lite separator: u32(0) prefix before u32(2)
            r.skip(4)
            prefix = struct.unpack_from('<I', data, r.tell())[0]
        if prefix != 2:
            return
        r.skip(4)

        tag = struct.unpack_from('<H', data, r.tell())[0]
        if tag == 0xFFFF:
            # New CRelationship class + 2 CRel objects
            r.skip(2)
            r.u16()   # schema
            nlen = r.u16()
            r.skip(nlen)  # class name "CRelationship"
            self.arc.register_class('CRelationship')
            self.arc.register_object(None)  # CRel#1
            r.skip(4)  # CRel#1 data: 2 u16 refs
            r.skip(2)  # CRel self-backref (class backref)
            self.arc.register_object(None)  # CRel#2
            r.skip(4)  # CRel#2 data: 2 u16 refs
            r.skip(10)  # zero padding
        elif tag >= 0x8000:
            # CRelationship class backref + 2 CRel objects
            r.skip(2)
            self.arc.register_object(None)  # CRel#1
            r.skip(4)  # CRel#1 data: 2 u16 refs
            r.skip(2)  # CRel self-backref
            self.arc.register_object(None)  # CRel#2
            r.skip(4)  # CRel#2 data: 2 u16 refs
            r.skip(10)  # zero padding
        else:
            # Lite separator: 2 object backrefs (no new registrations)
            r.skip(4)  # 2 u16 object refs
            r.skip(6)  # zero padding

        # u32(1) + CLayer
        r.skip(4)  # u32(1) count
        r.skip(2)  # CLayer class backref tag
        self.arc.register_object(None)  # CLayer object
        r.astring()   # layer name
        r.u8()        # null
        r.astring()   # display name
        r.u8()        # null
        r.u8()        # visibility
        r.read(4)     # RGBA
        r.u16()       # flags

    def _parse_layer_inline(self, idx):
        """Parse CLayer data (after the MFC tag has been consumed).
        Reads the layer name + basic data, then scans past scope-end metadata."""
        r = self.arc.r
        if self.model.version_major >= 5:
            r.u16()  # base prefix (v5+ only)
        lname = self._read_string(r)

        layer = {'name': lname, 'map_idx': idx}
        self.model.layers.append(layer)
        self.arc.set_object(idx, layer)
        self.log(f"Layer: {lname}")

        if self.model.version_major < 3 and self._uses_wstring:
            # v2 wstring format: name + null(1) + display(wstring) +
            #   null(1) + vis(1) + RGBA(4) + folder(wstring) + 8zeros +
            #   scope metadata (GUID + names + transforms + face blocks)
            r.u8()   # null separator
            self._read_string(r)  # display_name
            r.u8()       # null separator
            r.u8()       # visibility flag
            r.read(4)    # RGBA color
            self._read_string(r)  # folder_name
            r.skip(8)    # 8 zero bytes
            self._read_v1_scope_metadata(r)
        elif self.model.version_major < 3:
            # v1 (schema=0): name + null(1) + RGBA(4) + flags(u16) = 7 trailing
            # v2 (schema=1): name + null(1) + display_name(astring) +
            #                null(1) + u8_flag(1) + RGBA(4) + flags(u16)
            r.u8()   # null separator
            if self.model.version_major >= 2:
                self._read_string(r)  # display_name (v2 schema=1 extra field)
                r.u8()       # null separator
                r.u8()       # visibility flag
            r.read(4) # RGBA color
            r.u16()  # flags
            # After CLayer data: either another CLayer back-ref follows
            # (the main loop handles it), or scope-end metadata.
            # Try to read CD scope metadata deterministically:
            #   display_name(astring) + GUID(16) + def_name(astring) +
            #   null(1) + src_path(astring) + 142 fixed bytes.
            # Root scope metadata runs to EOF (no more entities).
            self._read_v1_scope_metadata(r)
        elif self.model.version_major <= 4:
            # v3/v4 (schema=1): same basic data as v2, then fixed trailing.
            # Basic: null(1) + display_name(astr) + null(1) + vis(1) + RGBA(4) + flags(2)
            r.u8()       # null separator
            r.astring()  # display_name
            r.u8()       # null separator
            r.u8()       # visibility flag
            r.read(4)    # RGBA color
            r.u16()      # flags
            # v3 trailing: 7 zero bytes + f64 + null = 16 bytes
            r.read(7)    # 7 zero bytes
            r.read(8)    # f64 (transparency or similar)
            r.u8()       # null
            # Optional entity preamble (before CCD or entity list).
            # Only present for the LAST CLayer before entities/CCD.
            # Peek: if next u16 is an entity tag, no preamble.
            if r.remaining() >= 2:
                peek = struct.unpack_from('<H', r.data, r.tell())[0]
                if peek != 0 and peek < 0x8000 and peek != 0xFFFF:
                    # Preamble: u16(map_idx) + u16(cd_count) + u16(0)
                    r.u16()  # map_idx
                    cd_count = r.u16()  # cd_count
                    r.u16()  # padding
                    if cd_count == 0:
                        r.u32()  # entity_count_hint
        elif self.model.version_major == 5:
            # v5 (schema=2): deterministic CLayer data
            # null(1) + gap(u16) + wstring(display) + null(1) + vis(1) +
            # RGBA(4) + wstring(folder) + 8zeros(8) + f64(8) + 5zeros(5) +
            # mc_ref(u16) + preamble(u32 [+ u32])
            r.u8()       # null separator
            r.u16()      # gap
            r.wstring()  # display_name
            r.u8()       # null separator
            r.u8()       # visibility flag
            r.read(4)    # RGBA color
            r.wstring()  # folder_name
            r.skip(8)    # 8 zero bytes
            r.skip(8)    # f64 (transparency or similar)
            r.skip(5)    # 5 trailing zeros
            r.u16()      # mc_ref (writer's MFC map count)
            # Preamble: u32(cd_count), if cd_count==0: u32(entity_count)
            cd_count = r.u32()
            if cd_count == 0:
                r.u32()  # entity_count_hint
        else:
            # v6+: Layer has variable-length trailing data
            self._scan_to_next_entity(r)

    def _skip_cdib_data(self, r):
        """Skip CDib image data (type + size + raw image bytes)."""
        dib_type = r.u32()
        dib_size = r.u32()
        if 0 < dib_size < r.remaining():
            self.log(f"Skipping CDib: type={dib_type}, size={dib_size}")
            r.skip(dib_size)
            return True
        return False

    def _parse_thumbnail(self, idx):
        """Parse CThumbnail deterministically.

        Format: null_ref(u16=0) + CCamera_backref(u16) + CCamera_data + CDib_ref(u16)
        CCamera data: 151 bytes (v5) or 176 bytes (v6+).
        CDib_ref: class backref → CDib data follows; or null (0x0000) → empty thumbnail.
        """
        r = self.arc.r
        self.arc.set_object(idx, {'type': 'CThumbnail'})

        # 1. null_ref (u16=0)
        r.u16()

        # 2. CCamera class backref → register CCamera object in MFC map
        cam_tag = r.u16()
        cam_class = self.arc.find_class_idx('CCamera')
        if cam_class and cam_tag == (0x8000 | cam_class):
            self.arc.register_object('CCamera')
        else:
            self.log(f"CThumbnail: unexpected CCamera tag 0x{cam_tag:04x}")

        # 3. CCamera serialized data (version-dependent size)
        # Camera data size depends on CCamera schema, not file version.
        # Schema <= 5 = 151 bytes, schema >= 6 = 176 bytes.
        cam_schema = self.model.version_map.get('CCamera', 0)
        cam_data_size = 151 if cam_schema <= 5 else 176
        r.skip(cam_data_size)

        # 4. CDib ref: class backref or null
        cdib_tag = r.u16()
        if cdib_tag == 0:
            # No scene thumbnail. Check if a CDib follows after
            # metadata padding (variable: typically 17-25 bytes).
            cdib_class = self.arc.find_class_idx('CDib')
            if cdib_class and r.remaining() >= 20:
                # Scan byte-by-byte for CDib class backref
                cdib_expected = 0x8000 | cdib_class
                scan_limit = min(r.tell() + 60, r.size - 2)
                found_cdib = False
                for scan_pos in range(r.tell(), scan_limit):
                    peek = struct.unpack_from('<H', r.data, scan_pos)[0]
                    if peek == cdib_expected:
                        r.seek(scan_pos + 2)
                        self.arc.register_object('CDib')
                        self._skip_cdib_data(r)
                        found_cdib = True
                        self.log(f"CThumbnail: found CDib at +{scan_pos - r.tell() + 2}")
                        break
                    # Also check for alternate CDib class index
                    for ci, cn in self.arc.class_map.items():
                        if cn == 'CDib' and peek == (0x8000 | ci):
                            r.seek(scan_pos + 2)
                            self.arc.register_object('CDib')
                            self._skip_cdib_data(r)
                            found_cdib = True
                            break
                    if found_cdib:
                        break
                if not found_cdib:
                    return True
            else:
                return True
        cdib_class = self.arc.find_class_idx('CDib')
        if cdib_class and cdib_tag == (0x8000 | cdib_class):
            self.arc.register_object('CDib')
            self._skip_cdib_data(r)
        elif cdib_tag == 0xFFFF:
            # First CDib: FFFF new class header
            r.seek(r.tell() - 2)  # back up to re-read FFFF tag
            name, is_new, didx = self.arc.read_object_tag()
            self._skip_cdib_data(r)
        else:
            self.log(f"CThumbnail: unexpected CDib tag 0x{cdib_tag:04x}")
        return True

    def _parse_cd_v4(self, idx, r):
        """Parse v4 CComponentDefinition data deterministically.

        Format: entity_base(11) + def_index(u16) + 8 zeros + layer_count(u32)
                + [CLayer backref(u16) + CLayer data] per layer
                + entity preamble(14).
        CLayer data (schema=2): prefix(2) + name(astr) + null(1) + u16(2)
                + display(astr) + null(1) + vis(1) + RGBA(4) + flags(2)
                + zeros(7) + f64_transparency(8) + trailing(1).
        """
        r.read(11)   # entity_base
        r.u16()      # def_index
        r.read(8)    # 8 zero bytes
        layer_count = r.u32()
        for _ in range(layer_count):
            layer_ref = r.u16()
            if layer_ref >= 0x8000:
                # Class backref → creates new CLayer object in MFC map
                layer_idx = self.arc.map_count
                self.arc.map_count += 1
                layer_data = {'name': '', 'map_idx': layer_idx, 'type': 'CLayer'}
                self.arc.set_object(layer_idx, layer_data)
                # Parse CLayer schema=2 data deterministically
                r.skip(2)           # prefix
                r.astring()         # name
                r.skip(1)           # null
                r.skip(2)           # u16 gap
                r.astring()         # display_name
                r.skip(1)           # null
                r.skip(1)           # vis
                r.skip(4)           # RGBA
                r.skip(2)           # flags
                r.skip(7)           # zeros
                r.skip(8)           # f64 transparency
                r.skip(1)           # trailing
        # Entity preamble: u32(0) + u32(mc) + u16(0) + u32(entity_count)
        r.skip(14)

    def _parse_cd_v5(self, idx, r, is_inst=False):
        """Parse v5/v6+ CComponentDefinition data deterministically.

        v5: entity_base(12) + def_index(u16) + 8 zeros + layer_count(u32).
            CLayers follow as separate entities in the entity list.
        v6 NEW: same 26-byte header + inline CLayer data per layer:
            backref(u16) + null(u16) + wstring(name) + CLayer_data + preamble.
        v6 INST: null(u16) + wstring(name) + CLayer_data + preamble.
            (no entity_base/def_index/8zeros/layer_count, no backref)
        Some v6 CDs have no header (CAttributeContainer follows immediately).
        """
        # Check if next bytes look like entity base or another FFFF tag
        if r.peek_u16() == 0xFFFF:
            # No entity data — CD is just a container (e.g. for CAttribute*)
            return

        if self.model.version_major >= 6 and is_inst:
            # v6+ INST has two variants:
            # A) null(u16) + wstring(name) + CLayer_data (e.g. Office_Laptop)
            # B) null(u16) + entity_base(12) + def_idx(u16) + padding(4) +
            #    layer_count(u32) + CLayer_INST (e.g. Ladder Extending)
            save = r.tell()
            try:
                r.u16()          # null prefix
                # Check if next bytes are a wstring (FF FE FF)
                if r.remaining() >= 3 and r.data[r.tell():r.tell()+3] == b'\xff\xfe\xff':
                    # Variant A: wstring name + CLayer data
                    r.wstring()
                    self._read_v6_clayer_data(r)
                else:
                    # Variant B: entity_base + def_idx + padding + layer_count
                    r.read(12)   # entity_base
                    r.u16()      # def_index
                    r.read(4)    # padding
                    layer_count = r.u32()
                    # CLayer follows as a separate INST tag (handled by entity list)
                return
            except Exception as e:
                self.log(f"v6 CD INST parse error: {e}")
                r.seek(save)
                self._scan_to_next_entity(r, max_scan=8192)
                return

        r.read(12)   # entity_base
        r.u16()      # def_index
        z8 = r.read(8)    # 8 zero bytes
        layer_count = r.u32()

        if not all(b == 0 for b in z8) or layer_count > 100:
            # Not valid header — rewind (was not a v5/v6 CD format)
            r.seek(r.tell() - 26)
            self._scan_to_next_entity(r, max_scan=8192)
            return

        if self.model.version_major >= 6 and layer_count > 0:
            # v6+ NEW: inline CLayers with backref prefix
            save = r.tell()
            try:
                for _ in range(layer_count):
                    layer_ref = r.u16()  # CLayer class backref
                    if layer_ref >= 0x8000:
                        layer_idx = self.arc.register_object(None)
                        self.arc.set_object(layer_idx,
                                            {'name': '', 'map_idx': layer_idx,
                                             'type': 'CLayer'})
                    r.u16()          # null separator
                    r.wstring()      # layer name
                    self._read_v6_clayer_data(r)
            except Exception as e:
                # Format mismatch — fall back to scanning
                self.log(f"v6 CD NEW inline CLayer parse error: {e}")
                r.seek(save)
                self._scan_to_next_entity(r, max_scan=8192)

    def _read_v6_clayer_data(self, r):
        """Read the common CLayer data portion for v6+ inline CLayers.

        Format: null(u8) + gap(u16) + wstring(display) + null(u8) + vis(u8)
                + RGBA(4) + wstring(folder) + 8zeros + f64 + 5zeros
                + mc_ref(u16) + preamble.
        """
        r.u8()           # null separator
        r.u16()          # gap
        r.wstring()      # display_name
        r.u8()           # null separator
        r.u8()           # vis flag
        r.skip(4)        # RGBA color
        r.wstring()      # folder_name
        r.skip(8)        # 8 zero bytes
        r.skip(8)        # f64 transparency
        r.skip(5)        # 5 trailing zeros
        mc_ref = r.u16() # writer's MFC map counter
        # Sync map counter to writer's value (we may have missed
        # objects during scanning/skipping of unknown data)
        if mc_ref > self.arc.map_count:
            self.log(f"v6 CLayer mc_ref sync: {self.arc.map_count} -> {mc_ref}")
            self.arc.map_count = mc_ref
        cd_count = r.u32()
        if cd_count == 0:
            r.u32()      # entity_count_hint

    def _parse_component_instance(self, idx):
        """Parse CComponentInstance: base + def_ref + transform (13 doubles) + name."""
        r = self.arc.r
        save_pos = r.tell()
        try:
            # v1/v2: Two kinds of CI entities:
            # 1. CI+CD pairs (opening a scope): just 7-byte entity base, transform
            #    is in the CComponentDefinition metadata (extracted at scope close).
            # 2. Standalone CIs (instances): 7-byte entity base + def_ref(u16) +
            #    13-double transform, like v3+ format.
            # We try reading the inline transform first; if validation fails,
            # it's a CI+CD pair.
            if self.model.version_major < 3:
                r.u32()  # entity_id
                r.u8()  # flags
                self._read_v1_layer_ref(r)  # MFC layer_ref (may create inline CLayer)
                ci_save = r.tell()
                found_inline = False
                try:
                    def_ref_raw = r.u16()
                    if r.remaining() >= 104:
                        xform = struct.unpack_from('<13d', r.data, r.tell())
                        rot_ok = all(abs(xform[i]) <= 1.01 for i in range(9))
                        scale_ok = abs(xform[12] - 1.0) < 0.01
                        if rot_ok and scale_ok:
                            # Verify orthogonality
                            col0 = (xform[0], xform[1], xform[2])
                            col1 = (xform[3], xform[4], xform[5])
                            col2 = (xform[6], xform[7], xform[8])
                            lens = [sum(c*c for c in col) for col in [col0, col1, col2]]
                            dots = [
                                sum(a*b for a, b in zip(col0, col1)),
                                sum(a*b for a, b in zip(col0, col2)),
                                sum(a*b for a, b in zip(col1, col2)),
                            ]
                            if (all(abs(l - 1.0) < 0.1 for l in lens) and
                                    all(abs(d) < 0.1 for d in dots)):
                                r.skip(104)
                                ci = ComponentInstance(
                                    definition=def_ref_raw,
                                    name="", map_idx=idx)
                                ci.transform = list(xform)
                                self.model.component_instances.append(ci)
                                self.arc.set_object(idx, ci)
                                self._pending_transforms.append(
                                    ('ci', def_ref_raw, xform))
                                self.log(
                                    f"CComponentInstance[{idx}]: v1 "
                                    f"standalone def@{def_ref_raw} "
                                    f"T=[{xform[9]:.2f},{xform[10]:.2f},"
                                    f"{xform[11]:.2f}]")
                                found_inline = True
                except Exception:
                    pass
                if not found_inline:
                    # CI+CD pair: entity base only, next tag immediately follows
                    r.seek(ci_save)
                    self.arc.set_object(idx, {'type': 'CComponentInstance'})
                    self._v1_last_was_ci = True
                    self.log(f"CComponentInstance[{idx}]: v1 CI+CD pair "
                            f"(transform in CD metadata)")
                else:
                    # Standalone CI: 4 trailing bytes after transform
                    r.read(4)
                return True

            # Skip inline CAttributeContainer/CAttributeNamed if present
            # (v7+ files may have these before the CI entity base)
            if r.remaining() >= 4 and r.peek_u16() >= 0x8000:
                ci_class = r.peek_u16() & 0x7FFF
                cname = self.arc.class_map.get(ci_class, '')
                if cname == 'CAttributeContainer':
                    # AC backref(2) + AC data(2 nulls) + AN backref(2) + AN data(variable)
                    # Scan forward to find the CI entity base: look for a valid
                    # 12-byte entity base + def_ref + 13-double transform
                    ac_save = r.tell()
                    r.u16()  # AC tag
                    self.arc.register_object({'type': 'CAttributeContainer', 'inline': True})
                    r.u16()  # AC null data
                    if r.remaining() >= 2 and r.peek_u16() >= 0x8000:
                        an_ci = r.peek_u16() & 0x7FFF
                        an_name = self.arc.class_map.get(an_ci, '')
                        if an_name == 'CAttributeNamed':
                            r.u16()  # AN tag
                            self.arc.register_object({'type': 'CAttributeNamed', 'inline': True})
                    # Scan for valid CI entity base + transform
                    found = False
                    for skip in range(0, 512):
                        if r.tell() + skip + 14 + 104 > r.size:
                            break
                        test_pos = r.tell() + skip
                        dr = struct.unpack_from('<H', r.data, test_pos + 12)[0]
                        if dr > 1000:
                            continue
                        xf = struct.unpack_from('<13d', r.data, test_pos + 14)
                        rot_ok = all(abs(xf[i]) <= 1.01 for i in range(9))
                        scale_ok = abs(xf[12] - 1.0) < 0.01
                        if rot_ok and scale_ok:
                            r.seek(test_pos)
                            self.log(f"CI: skipped {test_pos - ac_save} bytes of "
                                     f"inline CAttribute data")
                            found = True
                            break
                    if not found:
                        r.seek(ac_save)

            # Base data - extract material reference for CI inheritance
            # v5+ CI entity base uses CFace format: null(u16) + mat_ref(u16) +
            # flags(4) + layer_ref(u16) + extra(u16), NOT CEdge format.
            ci_mat_ref = 0
            if self.model.version_major >= 5:
                r.u16()  # null/back ref
                ci_mat_ref = r.u16()  # mat_ref (e.g. Charcoal for laptop base)
                r.read(4)  # flags
                r.u16()  # layer_ref
                r.u16()  # extra
            elif self.model.version_major == 4:
                ci_mat_ref = r.u16()  # material reference
                r.u16()  # upper flags
                r.read(4)  # flags
                r.u16()  # layer_ref
                r.u8()
            elif self.model.version_major >= 3:
                ci_mat_ref = r.u16()  # material reference
                r.u16()  # upper flags
                r.read(2)  # flags
                r.u16()  # layer_ref
                r.u8()

            # Definition reference (MFC object back-ref)
            def_ref = r.u16()

            # Transform: 13 doubles = Xx,Xy,Xz, Yx,Yy,Yz, Zx,Zy,Zz, Tx,Ty,Tz, w
            xform = struct.unpack_from('<13d', r.data, r.tell())
            r.skip(104)

            # Instance name (wstring: FF FE FF + len + utf16le)
            inst_name = ""
            if r.remaining() > 4:
                if r.data[r.tell():r.tell()+3] == b'\xff\xfe\xff':
                    inst_name = r.wstring()
                elif r.data[r.tell():r.tell()+2] == b'\xff\x00':
                    r.skip(2)
                    inst_name = self._read_string(r)

            ci = ComponentInstance(definition=def_ref, name=inst_name, map_idx=idx)
            ci.transform = list(xform)
            # Resolve CI material reference (v3/v4 entity base has mat_ref)
            ci.material_idx = -1
            if ci_mat_ref > 0:
                mat_obj = self.arc.get_object(ci_mat_ref)
                if isinstance(mat_obj, Material):
                    try:
                        ci.material_idx = self.model.materials.index(mat_obj)
                    except ValueError:
                        pass
            self.model.component_instances.append(ci)
            self.arc.set_object(idx, ci)

            # Check if transform is non-identity
            is_identity = (abs(xform[0]-1)<1e-6 and abs(xform[4]-1)<1e-6 and
                          abs(xform[8]-1)<1e-6 and abs(xform[12]-1)<1e-6 and
                          all(abs(xform[i])<1e-6 for i in [1,2,3,5,6,7,9,10,11]))
            # Always store CI transforms (including identity) so multi-instance
            # definitions get proper mesh instancing in the GLB output.
            # Include CI obj_idx so cut-opening CIs can be filtered later.
            self._pending_transforms.append(('ci', def_ref, xform, self.current_scope, idx))
            if not is_identity:
                self.log(f"CComponentInstance[{idx}]: def@{def_ref} "
                        f"T=[{xform[9]:.2f},{xform[10]:.2f},{xform[11]:.2f}] "
                        f"(non-identity)")
            else:
                self.log(f"CComponentInstance[{idx}]: def@{def_ref} (identity)")

            # CI entity data is fully consumed (base + def_ref +
            # transform + optional name). No trailing scan needed.
            return True

        except Exception as e:
            self.log(f"CComponentInstance parse failed at {hex(save_pos)}: {e}, scanning")
            r.seek(save_pos)
            self.arc.set_object(idx, {'type': 'CComponentInstance'})
            return self._scan_to_next_entity(r, max_scan=8192)

    def _scan_to_next_entity(self, r, max_scan=256):
        """Scan forward up to max_scan bytes to find the next valid FFFF class intro or class back-ref.
        Registers any FFFF class intros encountered during scanning to keep map in sync."""
        data = r.data
        scan_start = r.tell()
        scan_end = min(r.tell() + max_scan, len(data) - 6)
        # Known geometry/entity classes that we stop at
        entity_classes = {'CEdge', 'CFace', 'CLoop', 'CEdgeUse', 'CVertex',
                          'CMaterial', 'CLayer', 'CThumbnail', 'CDib',
                          'CComponentInstance', 'CComponentDefinition',
                          'CGroup', 'CDefinitionList', 'CCamera',
                          'CAttributeContainer', 'CAttributeNamed',
                          'CFaceTextureCoords',
                          'CSkFont', 'CSkpStyle', 'CSkpStyleManager',
                          'CArcCurve', 'CCurve', 'CRelationship',
                          'CConstructionPoint', 'CConstructionLine',
                          'CConstructionGeometry'}
        while r.tell() < scan_end:
            if data[r.tell()] == 0xFF and data[r.tell() + 1] == 0xFF:
                nlen = struct.unpack_from('<H', data, r.tell() + 4)[0]
                if 1 <= nlen <= 30 and r.tell() + 6 + nlen <= len(data):
                    try:
                        cn = data[r.tell() + 6:r.tell() + 6 + nlen].decode('ascii')
                        if cn and cn[0] == 'C' and cn.isalnum():
                            if cn in entity_classes:
                                return True
                            # Non-entity class: register it to keep map in sync
                            # but don't stop scanning
                            save = r.tell()
                            name, is_new, oidx = self.arc.read_object_tag()
                            self.log(f"Registered scanned class {name} "
                                    f"obj@{oidx}")
                            # Continue scanning from after the tag
                            continue
                    except (UnicodeDecodeError, IndexError):
                        pass
            # Also check for class back-refs
            if r.tell() + 2 <= len(data):
                tv = struct.unpack_from('<H', data, r.tell())[0]
                if tv >= 0x8000:
                    ci = tv & 0x7FFF
                    if ci in self.arc.class_map:
                        cname = self.arc.class_map[ci]
                        if cname in entity_classes:
                            return True
                        # Non-entity class back-ref: register object
                        r.u16()
                        oidx = self.arc.register_object(
                            {'type': cname})
                        continue
                    # Try offset-adjusted lookup for key structural classes
                    # (CComponentDefinition, CGroup) that can be missed
                    # due to MFC map drift. Only adjust for these high-level
                    # classes to avoid false positives.
                    found_adj = False
                    if self._class_offset > 0:
                        for off in range(1, self._class_offset + 2):
                            adj = ci - off
                            if adj in self.arc.class_map:
                                adj_name = self.arc.class_map[adj]
                                if adj_name in ('CComponentDefinition',
                                                'CGroup', 'CDefinitionList'):
                                    self.arc.class_map[ci] = adj_name
                                    if adj_name in entity_classes:
                                        return True
                                    found_adj = True
                                break
                    # Unknown class - probe for CComponentInstance pattern
                    # (also runs when offset-adjusted lookup didn't match)
                    if (not found_adj and
                            ci not in self.arc.class_map and
                            ci <= self.arc.map_count + 500 and
                            self.in_geometry):
                        identified = self._identify_unknown_class(r, ci)
                        if identified and identified in entity_classes:
                            return True
            r.skip(1)
        return False

    def _close_scope(self, identity_pos=None):
        """Close the current scope and record its scope number mapping."""
        if self._scope_stack:
            scope_type, map_idx, scope_num = self._scope_stack.pop()
            self._scope_map[map_idx] = scope_num
            self._scope_types[map_idx] = scope_type
            self.log(f"Scope {scope_type}[{map_idx}] = scope#{scope_num}")

            # For v1 files: extract placement from CD scope-end metadata.
            # Structure at identity_pos: identity(104B) + 20 zero bytes +
            # [optional CLayer tag + data] + display_name(astr) + GUID(16) +
            # def_name(astr) + null(1) + src_path(astr) + 142B fixed block.
            # Placement transform is at offset 34 within the 142 fixed bytes.
            if (self.model.version_major < 3 and scope_num > 0 and
                    scope_type == 'CComponentDefinition' and
                    identity_pos is not None):
                self._parse_v1_cd_placement(identity_pos, scope_num)

    def _parse_v1_cd_placement(self, identity_pos, scope_num):
        """Extract placement from v1 CD scope-end metadata at identity_pos.

        Structure: identity(104B) + 20 zero bytes + [optional CLayer tag +
        layer data] + display_name(astr) + GUID(16B) + def_name(astr) +
        null(1B) + src_path(astr) + 142B fixed block.
        Placement transform is at offset 34 within the 142 fixed bytes.

        The CLayer tag is present when CLayer class hasn't been registered
        yet (FFFF new-class or 80xx back-ref); absent when already registered.
        """
        data = self.arc.r.data
        pos = identity_pos + 124  # skip identity(104) + 20 zeros

        if pos + 20 >= len(data):
            return
        try:
            # Optional CLayer: first byte >= 0x80 indicates MFC tag
            if data[pos] >= 0x80:
                tag = struct.unpack_from('<H', data, pos)[0]
                if tag == 0xFFFF:
                    # New class: FFFF + schema(2) + name_len(2) + name
                    name_len = struct.unpack_from('<H', data, pos + 4)[0]
                    pos += 6 + name_len
                else:
                    pos += 2  # back-ref tag
                # Layer data: name(astr) + null(1) + RGBA(4) + flags(2)
                n = data[pos]
                pos += 1 + n + 1 + 4 + 2

            # CD metadata strings
            n = data[pos]; pos += 1 + n       # display_name
            pos += 16                          # GUID
            n = data[pos]; pos += 1 + n       # def_name
            pos += 1                           # null
            n = data[pos]; pos += 1 + n       # src_path

            # 142 fixed bytes, placement at offset 34
            if pos + 142 > len(data):
                return
            xform = struct.unpack_from('<13d', data, pos + 34)

            # Validate: scale ≈ 1.0 (rejects un-instantiated scopes
            # whose 142-byte block contains entity data, not a transform)
            if abs(xform[12] - 1.0) >= 0.1:
                return

            is_identity = (abs(xform[0]-1) < 1e-6 and abs(xform[4]-1) < 1e-6
                          and abs(xform[8]-1) < 1e-6 and abs(xform[12]-1) < 1e-6
                          and all(abs(xform[i]) < 1e-6
                                  for i in (1,2,3,5,6,7,9,10,11)))
            if not is_identity:
                self._v1_scope_transforms[scope_num] = xform
                self.log(f"v1 scope#{scope_num} placement: "
                        f"T=[{xform[9]:.2f},{xform[10]:.2f},{xform[11]:.2f}]")
        except (IndexError, struct.error):
            pass

    def _try_read_v3_scope_close(self, r):
        """Try to read v3/v4 scope-close metadata.

        Format: GUID(16) + def_name(astr) + null(1) + src_path(astr)
                + 41 fixed bytes (f32 + 37 bytes padding/flags).
        Appears after last entity of each CD scope (after CRelationship
        in multi-CD files, or inline in single-CD files).

        Returns True if scope-close was successfully read.
        """
        if self.model.version_major > 4 or not self._scope_stack:
            return False
        if r.remaining() < 60:
            return False

        save = r.tell()
        try:
            # Read GUID (16 random bytes - can't validate content)
            r.read(16)

            # Validate def_name: must be a short printable ASCII string
            name_len = r.data[r.tell()]
            if name_len == 0 or name_len > 80:
                r.seek(save)
                return False
            name_bytes = r.data[r.tell() + 1:r.tell() + 1 + name_len]
            if len(name_bytes) < name_len:
                r.seek(save)
                return False
            for b in name_bytes:
                if b < 0x20 or b > 0x7E:
                    r.seek(save)
                    return False

            def_name = r.astring()
            null_byte = r.u8()
            if null_byte != 0:
                r.seek(save)
                return False
            src_path = r.astring()

            if r.remaining() < 41:
                r.seek(save)
                return False
            r.read(41)  # f32(4) + 37 fixed bytes

            # Some scope-closes (inline, no CRelationship) have 4
            # additional bytes (u32 map counter).  Peek at next u16:
            # if it's not a valid entity tag, consume 4 more bytes.
            if r.remaining() >= 2:
                peek = struct.unpack_from('<H', r.data, r.tell())[0]
                if peek != 0xFFFF and peek < 0x8000 and peek != 0:
                    r.read(4)

            self.log(f"v3 scope-close: '{def_name}' path='{src_path}'")

            # Close the current scope
            self._close_scope()
            self.current_scope = 0

            return True
        except (struct.error, IndexError, UnicodeDecodeError):
            r.seek(save)
            return False

    def _parse_group_inline(self, idx, r):
        """Parse CGroup transform (same format as CComponentInstance)."""
        save_pos = r.tell()
        try:
            # Base data (same as CEdge)
            if self.model.version_major >= 5:
                r.u32()  # entity_id
                r.read(4)  # flags
                r.u16()  # layer_ref
                r.u16()  # mat_ref
            elif self.model.version_major == 4:
                r.u32()
                r.read(4)
                r.u16()
                r.u8()
            elif self.model.version_major >= 3:
                r.u32()
                r.read(2)
                r.u16()
                r.u8()

            # Reference (could be parent or definition ref)
            group_ref = r.u16()

            # Transform: 13 doubles
            xform = struct.unpack_from('<13d', r.data, r.tell())
            r.skip(104)

            # Validate transform: reject extreme values that cause overflow
            if any(not math.isfinite(xform[i]) or abs(xform[i]) > 1e10
                   for i in range(13)):
                self.log(f"CGroup[{idx}]: rejecting transform with extreme values")
                return True

            # Check if transform is non-identity
            is_identity = (abs(xform[0]-1)<1e-6 and abs(xform[4]-1)<1e-6 and
                          abs(xform[8]-1)<1e-6 and abs(xform[12]-1)<1e-6 and
                          all(abs(xform[i])<1e-6 for i in [1,2,3,5,6,7,9,10,11]))
            if not is_identity:
                # Use current_scope which was just assigned for this CGroup
                self._pending_transforms.append(('group', self.current_scope, xform, group_ref))
                self.log(f"CGroup[{idx}]: ref@{group_ref} scope#{self.current_scope} "
                        f"T=[{xform[9]:.2f},{xform[10]:.2f},{xform[11]:.2f}] "
                        f"(non-identity)")
            else:
                # Always register CGroups with refs so nested CGroups
                # can compose transforms through identity parents
                self._pending_transforms.append(('group', self.current_scope, xform, group_ref))
                self.log(f"CGroup[{idx}]: ref@{group_ref} scope#{self.current_scope} (identity)")

            # Skip instance name (wstring: FF FE FF + len + utf16le)
            if r.remaining() > 4:
                if r.data[r.tell():r.tell()+3] == b'\xff\xfe\xff':
                    r.wstring()
                elif r.data[r.tell():r.tell()+2] == b'\xff\x00':
                    r.skip(2)
                    self._read_string(r)

            # CGroup entity data is fully consumed
            return True

        except Exception as e:
            self.log(f"CGroup parse failed at {hex(save_pos)}: {e}, scanning")
            r.seek(save_pos)
            return self._scan_to_next_entity(r, max_scan=8192)

    def _apply_cut_openings(self):
        """Apply cut-opening holes to host faces based on CRelationship data.

        CRelationship pairs (face_obj_idx, ci_obj_idx) indicate that a
        CComponentInstance cuts a hole in the specified host face. The cut
        outline is computed by projecting the CI definition's vertices onto
        the host face plane and taking the convex hull.
        """
        if not self._cut_opening_pairs:
            return

        # Build face obj_idx -> model face index mapping
        face_obj_to_idx = {}
        for i, face in enumerate(self.model.faces):
            if hasattr(face, 'map_idx') and face.map_idx is not None:
                face_obj_to_idx[face.map_idx] = i

        # Group CI refs by host face
        face_ci_map = {}  # face_model_idx -> [ci_obj_idx, ...]
        for face_ref, ci_ref in self._cut_opening_pairs:
            face_idx = face_obj_to_idx.get(face_ref)
            if face_idx is not None:
                face_ci_map.setdefault(face_idx, []).append(ci_ref)

        if not face_ci_map:
            return

        for face_idx, ci_refs in face_ci_map.items():
            face = self.model.faces[face_idx]
            if not face.vertices or len(face.vertices) < 3:
                continue

            # Get face plane: normal and a point on the plane
            fn = face.normal
            fn_mag = math.sqrt(fn[0]**2 + fn[1]**2 + fn[2]**2)
            if fn_mag < 1e-10:
                continue
            fn = (fn[0]/fn_mag, fn[1]/fn_mag, fn[2]/fn_mag)
            fp = (face.vertices[0].x, face.vertices[0].y, face.vertices[0].z)

            # Build 2D coordinate system on the face plane
            # u = arbitrary perpendicular to fn, v = fn x u
            if abs(fn[0]) < 0.9:
                up = (1, 0, 0)
            else:
                up = (0, 1, 0)
            u = (up[1]*fn[2] - up[2]*fn[1],
                 up[2]*fn[0] - up[0]*fn[2],
                 up[0]*fn[1] - up[1]*fn[0])
            u_mag = math.sqrt(u[0]**2 + u[1]**2 + u[2]**2)
            if u_mag < 1e-10:
                continue
            u = (u[0]/u_mag, u[1]/u_mag, u[2]/u_mag)
            v = (fn[1]*u[2] - fn[2]*u[1],
                 fn[2]*u[0] - fn[0]*u[2],
                 fn[0]*u[1] - fn[1]*u[0])

            for ci_ref in ci_refs:
                ci_obj = self.arc.get_object(ci_ref)
                if not isinstance(ci_obj, ComponentInstance):
                    continue

                # Get CI's definition scope and vertices
                def_ref = ci_obj.definition
                scope_num = self._scope_map.get(def_ref)
                if scope_num is None:
                    # Try offset matching
                    for off in range(1, 5):
                        adj = def_ref - off
                        if adj in self._scope_map:
                            scope_num = self._scope_map[adj]
                            break
                if scope_num is None:
                    continue

                # Collect definition vertices
                def_verts = []
                for vert in self.model.vertices:
                    if vert.scope == scope_num:
                        def_verts.append((vert.x, vert.y, vert.z))
                if not def_verts:
                    continue

                # Check if definition vertices are in local space
                # (multi-instance CI) or world space (single-instance, already
                # transformed by _apply_transforms).
                is_multi_instance = any(
                    dr_key in self.model.ci_transforms
                    for dr_key in self.model.ci_transforms
                    if self._scope_map.get(dr_key) == scope_num
                    or any(self._scope_map.get(dr_key - off) == scope_num
                           for off in range(1, 5)))
                # Also check via def_face_ranges
                if not is_multi_instance:
                    for dr_key in self.model.def_face_ranges:
                        sn = self._scope_map.get(dr_key)
                        if sn == scope_num:
                            is_multi_instance = True
                            break

                if is_multi_instance:
                    # Vertices in local space — transform using CI transform
                    xform = ci_obj.transform
                    containing_scope = 0
                    for entry in self._pending_transforms:
                        if entry[0] == 'ci' and len(entry) > 4:
                            if entry[4] == ci_ref:
                                containing_scope = entry[3]
                                break
                    if (containing_scope > 0 and
                            hasattr(self, '_applied_scope_xforms')):
                        scope_to_def = {}
                        for dr, sn in self._scope_map.items():
                            scope_to_def[sn] = dr
                        parent_xforms = self._get_scope_world_xforms(
                            containing_scope, self._applied_scope_xforms,
                            scope_to_def)
                        if parent_xforms:
                            xform = self._compose_transforms(
                                parent_xforms[0], xform)

                    R = [[xform[0], xform[1], xform[2]],
                         [xform[3], xform[4], xform[5]],
                         [xform[6], xform[7], xform[8]]]
                    T = [xform[9], xform[10], xform[11]]
                    world_verts = []
                    for lx, ly, lz in def_verts:
                        wx = R[0][0]*lx + R[0][1]*ly + R[0][2]*lz + T[0]
                        wy = R[1][0]*lx + R[1][1]*ly + R[1][2]*lz + T[1]
                        wz = R[2][0]*lx + R[2][1]*ly + R[2][2]*lz + T[2]
                        world_verts.append((wx, wy, wz))
                else:
                    # Vertices already in world space (single-instance)
                    world_verts = def_verts

                # Project world verts onto face plane (2D coords)
                pts_2d = []
                for wx, wy, wz in world_verts:
                    dx, dy, dz = wx - fp[0], wy - fp[1], wz - fp[2]
                    pu = dx*u[0] + dy*u[1] + dz*u[2]
                    pv = dx*v[0] + dy*v[1] + dz*v[2]
                    # Check distance from plane
                    pd = dx*fn[0] + dy*fn[1] + dz*fn[2]
                    if abs(pd) < 1.0:  # within 1 inch of plane
                        pts_2d.append((pu, pv))

                if len(pts_2d) < 3:
                    # Not enough points on the plane — use bounding box
                    # projection of ALL vertices
                    pts_2d = []
                    for wx, wy, wz in world_verts:
                        dx, dy, dz = wx - fp[0], wy - fp[1], wz - fp[2]
                        pu = dx*u[0] + dy*u[1] + dz*u[2]
                        pv = dx*v[0] + dy*v[1] + dz*v[2]
                        pts_2d.append((pu, pv))
                    if len(pts_2d) < 3:
                        continue
                    # Use bounding box
                    min_u = min(p[0] for p in pts_2d)
                    max_u = max(p[0] for p in pts_2d)
                    min_v = min(p[1] for p in pts_2d)
                    max_v = max(p[1] for p in pts_2d)
                    pts_2d = [(min_u, min_v), (max_u, min_v),
                              (max_u, max_v), (min_u, max_v)]

                # Compute convex hull of projected points
                hull = self._convex_hull_2d(pts_2d)
                if len(hull) < 3:
                    continue

                # Convert hull back to 3D world coordinates
                hole_verts = []
                for pu, pv in hull:
                    wx = fp[0] + pu*u[0] + pv*v[0]
                    wy = fp[1] + pu*u[1] + pv*v[1]
                    wz = fp[2] + pu*u[2] + pv*v[2]
                    nv = Vertex(wx, wy, wz)
                    nv.scope = face.scope
                    self.model.vertices.append(nv)
                    hole_verts.append(nv)

                if not face.holes:
                    face.holes = []
                face.holes.append(hole_verts)
                self.log(f"Cut opening: Face[{face_idx}] + CI@{ci_ref} "
                        f"-> hole with {len(hole_verts)} verts")

    @staticmethod
    @staticmethod
    def _convex_hull_2d(points):
        """Compute convex hull of 2D points (delegates to glb module)."""
        return convex_hull_2d(points)

    def _apply_transforms(self):
        """Apply component instance and group transforms to vertices.

        Strategy:
        - v1/v2: placement transforms extracted from CD metadata, applied per scope.
        - CComponentInstance: references a definition whose scope includes
          all nested sub-scopes. Find the definition's scope number and
          apply the transform to all vertices with scope >= that number
          (up to the next sibling scope).
        - CGroup: apply transform to vertices with that specific scope.
        """
        # For v1 files: handle scope-based transforms and exclude
        # un-instantiated definition scopes
        if self.model.version_major < 3:
            # Determine which scopes are referenced by standalone CIs
            ci_ref_scopes = set()
            for entry in self._pending_transforms:
                if entry[0] == 'ci':
                    def_ref = entry[1]
                    # Resolve def_ref to scope
                    sn = self._scope_map.get(def_ref)
                    if sn is None:
                        for off in range(1, 5):
                            if def_ref - off in self._scope_map:
                                sn = self._scope_map[def_ref - off]
                                break
                    if sn is not None:
                        ci_ref_scopes.add(sn)

            # Identify un-instantiated scopes (not CI+CD pair, no placement,
            # no CI references) and exclude their faces
            all_scopes = set(v.scope for v in self.model.vertices)
            for scope_num in all_scopes:
                if scope_num == 0:
                    continue  # root scope always renders
                is_ci_cd = scope_num in self._v1_ci_cd_scopes
                has_placement = scope_num in self._v1_scope_transforms
                has_ci_refs = scope_num in ci_ref_scopes
                if not is_ci_cd and not has_placement and not has_ci_refs:
                    # Un-instantiated library definition - exclude
                    excluded_faces = 0
                    for face in self.model.faces:
                        if face.scope == scope_num and face.vertices:
                            face.vertices = []
                            excluded_faces += 1
                    self.log(f"v1 scope#{scope_num}: un-instantiated "
                            f"definition, excluded {excluded_faces} faces")

            # Apply placement transforms from CD metadata
            if self._v1_scope_transforms:
                # Build map: scope_num -> def_ref (for checking CI instances)
                scope_to_def = {}
                for map_idx, sn in self._scope_map.items():
                    scope_to_def[sn] = map_idx
                # Count CI instances per def_ref
                ci_count_by_def = {}
                for entry in self._pending_transforms:
                    if entry[0] == 'ci':
                        ci_count_by_def[entry[1]] = (
                            ci_count_by_def.get(entry[1], 0) + 1)

                for scope_num, xform in sorted(
                        self._v1_scope_transforms.items()):
                    def_ref = scope_to_def.get(scope_num)
                    # Check CI count with MFC offset tolerance
                    # (standalone CIs may reference def_ref+1 or +2)
                    ci_count = 0
                    ci_def_key = def_ref
                    if def_ref is not None:
                        for offset in range(
                                max(self._class_offset + 2, 5)):
                            test_ref = def_ref + offset
                            if test_ref in ci_count_by_def:
                                ci_count = ci_count_by_def[test_ref]
                                ci_def_key = test_ref
                                break

                    if ci_count > 0 and def_ref is not None:
                        # Multi-instance: don't bake placement into vertices.
                        # Add it as a CI transform for mesh instancing.
                        self._pending_transforms.append(
                            ('ci', ci_def_key, xform))
                        self.log(
                            f"v1 scope#{scope_num}: placement added as "
                            f"CI instance (def@{def_ref}, "
                            f"{ci_count}+1 instances)")
                    else:
                        target_verts = [v for v in self.model.vertices
                                        if v.scope == scope_num]
                        if target_verts:
                            self._transform_verts(target_verts, xform)
                            self.log(
                                f"Applied v1 placement to "
                                f"scope#{scope_num}:"
                                f" {len(target_verts)} verts, "
                                f"T=[{xform[9]:.2f},{xform[10]:.2f},"
                                f"{xform[11]:.2f}]")

        if not self._pending_transforms:
            return

        # Separate CI and Group transforms.
        # Cut-opening CIs both define hole outlines AND render geometry.
        # Don't exclude them — process their transforms normally.
        ci_transforms = []  # (def_ref, xform, containing_scope)
        group_transforms = []
        for entry in self._pending_transforms:
            if entry[0] == 'ci':
                containing_scope = entry[3] if len(entry) > 3 else 0
                ci_transforms.append((entry[1], entry[2], containing_scope))
            else:
                # entry = ('group', scope_num, xform, group_ref) or legacy ('group', scope_num, xform)
                group_ref = entry[3] if len(entry) > 3 else None
                group_transforms.append((entry[1], entry[2], group_ref))

        # Duplicate cross-scope vertices: when a face in scope A uses a
        # vertex from scope B (due to shared edges), and scope B will be
        # transformed, the shared vertex would distort scope A's face.
        # Also needed for multi-instance CIs where definition vertices are
        # kept in local space — foreign-scope vertices would be left behind.
        dup_count = 0
        for face in self.model.faces:
            if not face.vertices:
                continue
            new_verts = []
            changed = False
            for v in face.vertices:
                if v.scope != face.scope:
                    nv = Vertex(v.x, v.y, v.z)
                    nv.scope = face.scope
                    self.model.vertices.append(nv)
                    new_verts.append(nv)
                    changed = True
                    dup_count += 1
                else:
                    new_verts.append(v)
            if changed:
                face.vertices = new_verts
        if dup_count:
            self.log(f"Duplicated {dup_count} cross-scope vertices")

        # Detect CGroups that instance a CComponentDefinition (no faces in
        # their own scope). Group by group_ref and convert to CI-style instancing.
        # When multiple CGroups share a group_ref and only one has faces,
        # use that CGroup's faces as the instanced definition.
        groups_by_ref = {}  # group_ref -> [(scope_num, xform, has_faces, face_indices)]
        standalone_groups = []  # (scope_num, xform, group_ref) for groups without shared ref
        for scope_num, xform, group_ref in group_transforms:
            face_indices = [i for i, f in enumerate(self.model.faces)
                           if f.scope == scope_num]
            if group_ref is not None:
                groups_by_ref.setdefault(group_ref, []).append(
                    (scope_num, xform, bool(face_indices), face_indices))
            elif face_indices:
                standalone_groups.append((scope_num, xform, face_indices))
            else:
                self.log(f"Group scope#{scope_num}: no faces, no ref")

        for group_ref, entries in groups_by_ref.items():
            face_bearing = [(s, x, fi) for s, x, has, fi in entries if has]
            all_xforms = [x for _, x, _, _ in entries]

            if len(face_bearing) == 1 and len(entries) > 1:
                primary_scope, primary_xform, primary_faces = face_bearing[0]

                # Check if group_ref is a CD with its own geometry.
                # If so, CGroups instance the CD's geometry, and the
                # face-bearing CGroup's own faces are standalone.
                ref_scope_type = self._scope_types.get(group_ref, '')
                cd_scope = self._scope_map.get(group_ref)
                cd_has_faces = False
                if (ref_scope_type == 'CComponentDefinition' and
                        cd_scope is not None):
                    cd_face_indices = [i for i, f in enumerate(
                        self.model.faces) if f.scope == cd_scope]
                    cd_has_faces = bool(cd_face_indices)

                if cd_has_faces:
                    # CGroups reference a CD with geometry (e.g. table leg).
                    # The face-bearing CGroup's own faces are standalone
                    # (e.g. table rim), not the instanced definition.
                    standalone_groups.append(
                        (primary_scope, primary_xform, primary_faces))
                    # All CGroups instance the CD
                    for scope_num, xform, _, _ in entries:
                        ci_transforms.append((group_ref, xform, 0))
                    self.log(f"Group CD-instance: {len(entries)} CGroups "
                            f"instance CD@{group_ref} (scope#{cd_scope}), "
                            f"scope#{primary_scope} standalone "
                            f"({len(primary_faces)} faces)")
                else:
                    # Multi-instance CGroup: one has faces, others are empty
                    f_start = primary_faces[0]
                    f_end = primary_faces[-1] + 1

                    # Convert vertices to local coordinates (CGroup vertices
                    # are stored in world space with transform baked in).
                    grp_vert_ids = set()
                    for fi in primary_faces:
                        for v in self.model.faces[fi].vertices:
                            grp_vert_ids.add(id(v))
                    non_grp_vert_ids = set()
                    for i, f in enumerate(self.model.faces):
                        if f.scope != primary_scope and f.vertices:
                            for v in f.vertices:
                                non_grp_vert_ids.add(id(v))
                    shared_ids = grp_vert_ids & non_grp_vert_ids
                    if shared_ids:
                        dup_map = {}
                        for v in self.model.vertices:
                            if id(v) in shared_ids:
                                nv = Vertex(v.x, v.y, v.z)
                                nv.scope = primary_scope
                                dup_map[id(v)] = nv
                                self.model.vertices.append(nv)
                        for fi in primary_faces:
                            face = self.model.faces[fi]
                            face.vertices = [
                                dup_map.get(id(v), v)
                                for v in face.vertices]
                        self.log(f"Group scope#{primary_scope}: "
                                f"duplicated {len(dup_map)} shared verts")
                    grp_vert_ids2 = set()
                    for fi in primary_faces:
                        for v in self.model.faces[fi].vertices:
                            grp_vert_ids2.add(id(v))
                    target = [v for v in self.model.vertices
                              if id(v) in grp_vert_ids2]
                    if target:
                        self._untransform_verts(target, primary_xform)
                        self.log(f"Group scope#{primary_scope}: "
                                f"converted {len(target)} verts to local")

                    # Use CI-style instancing with primary CGroup's faces
                    # Use negative scope as key to avoid collision with def_refs
                    inst_key = -(primary_scope + 1)
                    self.model.def_face_ranges[inst_key] = primary_faces
                    self.model.ci_transforms[inst_key] = all_xforms
                    self.log(f"Group multi-instance: scope#{primary_scope} "
                            f"{len(primary_faces)} faces, "
                            f"{len(all_xforms)} instances")

            elif face_bearing:
                # Check if the CGroup wraps a CD with its own faces.
                # When a CGroup references a CD and both have faces, the
                # CD vertices are stored with the CGroup transform baked
                # in (offset from local origin). Untransform the CD
                # vertices so both scopes share the same local space.
                ref_scope_type = self._scope_types.get(group_ref, '')
                cd_scope = self._scope_map.get(group_ref)
                cd_face_indices = []
                if (ref_scope_type == 'CComponentDefinition' and
                        cd_scope is not None):
                    cd_face_indices = [i for i, f in enumerate(
                        self.model.faces) if f.scope == cd_scope
                        and f.vertices and len(f.vertices) >= 3]

                if cd_face_indices and len(entries) == 1:
                    # Single CGroup wrapping a CD: untransform CD
                    # vertices to local space and merge into one mesh
                    scope_num, xform, _ = face_bearing[0]
                    cd_vert_ids = set()
                    for fi in cd_face_indices:
                        for v in self.model.faces[fi].vertices:
                            cd_vert_ids.add(id(v))
                    cd_verts = [v for v in self.model.vertices
                                if id(v) in cd_vert_ids]
                    if cd_verts:
                        self._transform_verts(cd_verts, xform)
                        self.log(
                            f"CGroup scope#{scope_num} wraps "
                            f"CD@{group_ref} (scope#{cd_scope}): "
                            f"untransformed {len(cd_verts)} CD verts, "
                            f"T=[{xform[9]:.4f},{xform[10]:.4f},"
                            f"{xform[11]:.4f}]")
                    # Don't create a group transform — all faces
                    # go into the root mesh at identity
                else:
                    # Each CGroup with faces is standalone
                    for scope_num, xform, face_indices in face_bearing:
                        standalone_groups.append(
                            (scope_num, xform, face_indices))
                # Empty ones become CI instances if ref is a CD
                for scope_num, xform, has_faces, _ in entries:
                    if not has_faces:
                        if ref_scope_type == 'CComponentDefinition':
                            ci_transforms.append((group_ref, xform, 0))
                            self.log(f"Group scope#{scope_num} instances "
                                    f"CD@{group_ref}")
            else:
                # All empty - instance the CD
                ref_scope_type = self._scope_types.get(group_ref, '')
                if ref_scope_type == 'CComponentDefinition':
                    for scope_num, xform, _, _ in entries:
                        ci_transforms.append((group_ref, xform, 0))
                        self.log(f"Group scope#{scope_num} instances "
                                f"CD@{group_ref}, "
                                f"T=[{xform[9]:.4f},{xform[10]:.4f},"
                                f"{xform[11]:.4f}]")

        # Process standalone groups (single instance with own faces)
        for scope_num, xform, face_indices in standalone_groups:
            f_start = face_indices[0]
            f_end = face_indices[-1] + 1
            self.model.group_face_ranges[scope_num] = (f_start, f_end)
            self.model.group_transforms[scope_num] = xform
            self.log(f"Group transform for scope#{scope_num}: "
                    f"faces [{f_start},{f_end}), "
                    f"T=[{xform[9]:.4f},{xform[10]:.4f},{xform[11]:.4f}]")
            # CGroup vertices are stored in world space (transform baked in).
            # Convert to local space so glTF node transform positions them correctly.
            # Duplicate shared vertices first to avoid disturbing other scopes.
            grp_vert_ids = set()
            for fi in face_indices:
                for v in self.model.faces[fi].vertices:
                    grp_vert_ids.add(id(v))
            non_grp_vert_ids = set()
            for i, f in enumerate(self.model.faces):
                if f.scope != scope_num and f.vertices:
                    for v in f.vertices:
                        non_grp_vert_ids.add(id(v))
            shared_ids = grp_vert_ids & non_grp_vert_ids
            if shared_ids:
                dup_map = {}
                for v in self.model.vertices:
                    if id(v) in shared_ids:
                        nv = Vertex(v.x, v.y, v.z)
                        nv.scope = scope_num
                        dup_map[id(v)] = nv
                        self.model.vertices.append(nv)
                for fi in face_indices:
                    face = self.model.faces[fi]
                    face.vertices = [
                        dup_map.get(id(v), v)
                        for v in face.vertices]
                self.log(f"Group scope#{scope_num}: "
                        f"duplicated {len(dup_map)} shared verts")
            grp_vert_ids2 = set()
            for fi in face_indices:
                for v in self.model.faces[fi].vertices:
                    grp_vert_ids2.add(id(v))
            target = [v for v in self.model.vertices
                      if id(v) in grp_vert_ids2]
            if target:
                self._untransform_verts(target, xform)
                self.log(f"Group scope#{scope_num}: "
                        f"converted {len(target)} verts to local")

        # Apply CI transforms
        # Group CIs by definition ref, track containing scopes per instance
        ci_by_def = {}  # def_ref -> [xform, ...]
        ci_instances = {}  # def_ref -> [(xform, containing_scope), ...]
        ci_containing_scopes = {}  # def_ref -> set of containing scopes
        for def_ref, xform, containing_scope in ci_transforms:
            ci_by_def.setdefault(def_ref, []).append(xform)
            ci_instances.setdefault(def_ref, []).append(
                (xform, containing_scope))
            ci_containing_scopes.setdefault(def_ref, set()).add(containing_scope)

        # First pass: try direct and small-offset matching
        ci_resolved = {}  # def_ref -> (scope_num, adjusted_def_ref)
        ci_unresolved = []  # def_refs that couldn't be matched
        matched_defs = set()  # parser map_indices already matched

        for def_ref in ci_by_def:
            scope_num = self._scope_map.get(def_ref)
            adjusted = def_ref
            if scope_num is None:
                for offset in range(1, max(self._class_offset + 2, 5)):
                    adj = def_ref - offset
                    if adj in self._scope_map:
                        scope_num = self._scope_map[adj]
                        adjusted = adj
                        self.log(f"CI def@{def_ref} -> adjusted def@{adj} "
                                f"(offset={offset})")
                        break
            if scope_num is not None:
                ci_resolved[def_ref] = (scope_num, adjusted)
                matched_defs.add(adjusted)
            else:
                ci_unresolved.append(def_ref)

        # Second pass: broad matching for unresolved CIs.
        # The writer's MFC counter includes all child objects, so def_ref
        # can be much larger than our parser's map_idx. Match by order:
        # sort unresolved def_refs and unmatched definitions, then pair them.
        if ci_unresolved:
            # Collect unmatched CComponentDefinitions with geometry
            def_candidates = []
            for map_idx, sn in sorted(self._scope_map.items()):
                stype = self._scope_types.get(map_idx, '')
                if stype != 'CComponentDefinition':
                    continue
                if map_idx in matched_defs:
                    continue
                geo = self._def_geo_start.get(map_idx)
                if geo is None:
                    continue
                f_start = geo[2]
                f_end = len(self.model.faces)
                for other_idx, other_geo in self._def_geo_start.items():
                    if other_idx != map_idx and other_geo[2] > f_start:
                        f_end = min(f_end, other_geo[2])
                if f_end > f_start:
                    def_candidates.append((map_idx, sn))

            # Sort both by value (order in file)
            ci_unresolved.sort()
            # def_candidates already sorted by map_idx

            # Match by order: smallest unresolved def_ref -> smallest candidate
            for i, def_ref in enumerate(ci_unresolved):
                if i < len(def_candidates):
                    cand_idx, cand_scope = def_candidates[i]
                    ci_resolved[def_ref] = (cand_scope, cand_idx)
                    self.log(f"CI def@{def_ref} -> order match def@{cand_idx} "
                            f"scope#{cand_scope} (gap={def_ref - cand_idx})")

        # Build scope_num -> def_ref mapping for looking up multi-instance
        # parent scope transforms during nested CI composition.
        scope_to_def = {}  # scope_num -> def_ref
        for dr, (sn, _adj) in ci_resolved.items():
            scope_to_def[sn] = dr

        # Process CIs in dependency order: single-instance first, then
        # multi-instance parents before children.  A def that has instances
        # inside scope S depends on the def that owns scope S.
        applied_scope_xforms = {}  # scope_num -> xform (from single-instance CIs)
        self._applied_scope_xforms = applied_scope_xforms  # save for cut-openings

        # Build dependency depth: how many levels of nesting above root
        def _dep_depth(dr, visited=None):
            if visited is None:
                visited = set()
            if dr in visited:
                return 0
            visited.add(dr)
            max_d = 0
            for _xf, cs in ci_instances.get(dr, []):
                if cs > 0:
                    parent_dr = scope_to_def.get(cs)
                    if parent_dr is not None and parent_dr in ci_by_def:
                        max_d = max(max_d, 1 + _dep_depth(
                            parent_dr, visited))
            return max_d

        def_ref_order = sorted(ci_by_def.keys(),
                               key=lambda d: (len(ci_by_def[d]) != 1,
                                              _dep_depth(d), d))

        # Build set of scopes that have their own CI (for descendant check)
        ci_scopes_set = set()
        for dr in ci_by_def:
            if dr in ci_resolved:
                ci_scopes_set.add(ci_resolved[dr][0])

        for def_ref in def_ref_order:
            xforms = ci_by_def[def_ref]
            if def_ref not in ci_resolved:
                self.log(f"Transform for CI def@{def_ref}: no scope found")
                continue
            scope_num, adjusted_def_ref = ci_resolved[def_ref]

            # Determine which faces belong to this definition
            geo_start = self._def_geo_start.get(adjusted_def_ref) or \
                        self._def_geo_start.get(def_ref)
            if geo_start:
                v_start, e_start, f_start = geo_start
                v_end = len(self.model.vertices)
                f_end = len(self.model.faces)
                for other_def, other_start in self._def_geo_start.items():
                    if other_def != def_ref and other_start[0] > v_start:
                        v_end = min(v_end, other_start[0])
                        f_end = min(f_end, other_start[2])
                target_verts = [v for v in self.model.vertices[v_start:v_end]
                                if v.scope == scope_num]
            else:
                target_verts = [v for v in self.model.vertices
                                if v.scope == scope_num]
                f_start = None
                f_end = None

            # If no direct vertices in scope, check descendant scopes
            # (container definitions with nested CIs/CGroups)
            if not target_verts:
                desc = self._get_descendant_scopes(scope_num, set())
                target_verts = [v for v in self.model.vertices
                                if v.scope in desc]
            if not target_verts:
                # Pure container definition: no geometry of its own, but may
                # contain CIs that reference other definitions. Register its
                # transforms so nested CIs can compose with them later.
                has_nested_cis = any(
                    e[0] == 'ci' and len(e) > 3 and e[3] == scope_num
                    for e in self._pending_transforms
                    if e[1] != def_ref)
                if has_nested_cis and len(xforms) > 1:
                    self.model.ci_transforms[def_ref] = list(xforms)
                    self.log(f"CI def@{def_ref}: container with "
                             f"{len(xforms)} instances (nested CIs inside)")
                continue

            # Check for self-referencing CIs: one definition covers ALL geometry
            # AND CI translations are all identical (or nearly so).
            # Self-referencing means transforms are already baked into vertices.
            # If translations differ, they're genuine instances even if inside bbox.
            # Use scope-filtered face count when scopes are available (v1/v2),
            # since vertex ranges can overestimate coverage.
            if f_start is not None and scope_num > 0:
                scope_faces = sum(1 for fi in range(f_start, f_end)
                                 if self.model.faces[fi].scope == scope_num)
                covers_all = (scope_faces >= len(self.model.faces) * 0.9)
            else:
                total_verts = len(self.model.vertices)
                covers_all = (len(target_verts) >= total_verts * 0.9)
            self_referencing = False
            if covers_all and len(xforms) > 1:
                # Check if all transforms are effectively identical
                # (self-referencing CIs all have the same transform)
                all_same = True
                ref_t = (xforms[0][9], xforms[0][10], xforms[0][11])
                for xf in xforms[1:]:
                    dt = math.sqrt((xf[9]-ref_t[0])**2 +
                                   (xf[10]-ref_t[1])**2 +
                                   (xf[11]-ref_t[2])**2)
                    if dt > 0.1:
                        all_same = False
                        break
                if all_same:
                    # All translations identical — check rotation too
                    all_rot_same = True
                    for xf in xforms[1:]:
                        rot_diff = sum(abs(xf[i]-xforms[0][i]) for i in range(9))
                        if rot_diff > 0.1:
                            all_rot_same = False
                            break
                    if all_rot_same:
                        self_referencing = True
                        self.log(f"CI def@{def_ref}: all {len(xforms)} transforms "
                                f"identical, treating as self-referencing")

            # When one definition covers all geometry, detect actual boundary
            # by looking for coordinate jumps (definition-local vs world coords)
            if covers_all and len(xforms) > 1 and not self_referencing:
                actual_end = self._find_definition_boundary(
                    f_start, f_end, v_start, v_end, target_verts, xforms)
                if actual_end is not None:
                    f_end = actual_end
                    # Recalculate target_verts for just the definition
                    # Find vertex range for definition faces
                    def_verts = set()
                    for fi in range(f_start, f_end):
                        face = self.model.faces[fi]
                        if face.vertices:
                            for v in face.vertices:
                                def_verts.add(id(v))
                    target_verts = [v for v in self.model.vertices[v_start:v_end]
                                    if id(v) in def_verts] or target_verts[:1]
                    covers_all = False
                    self.log(f"CI def@{def_ref}: detected definition boundary "
                            f"at face {f_end}, {len(target_verts)} def verts")

            # When one definition covers ALL geometry and no boundary was
            # found, check if there are root-scope faces. If not, the
            # definition IS all the geometry and all CIs are legitimate
            # instances. If there ARE root-scope faces, extra CIs are
            # external placement metadata — keep only the first.
            if covers_all and len(xforms) > 1 and not self_referencing:
                has_root_faces = any(f.vertices and f.scope == 0
                                     for f in self.model.faces)
                # Check if only a single definition exists (component library
                # file with one shape). If so, all CIs are placement metadata.
                # If multiple definitions exist, CIs may be legitimate instances.
                single_def = (len(ci_instances) == 1)
                if has_root_faces or (not has_root_faces and single_def):
                    self.log(f"CI def@{def_ref}: covers_all with "
                            f"{len(xforms)} different transforms, "
                            f"keeping only first (others are metadata)")
                    xforms = [xforms[0]]
                    instances = ci_instances.get(def_ref, [])
                    if len(instances) > 1:
                        ci_instances[def_ref] = [instances[0]]
                else:
                    self.log(f"CI def@{def_ref}: covers_all but "
                            f"multi-def file — all {len(xforms)} "
                            f"CIs are legitimate instances")
                    covers_all = False

            if self_referencing:
                # Self-referencing CIs: geometry already has transforms baked in.
                # Do NOT apply any transform.
                self.log(f"CI def@{def_ref}: {len(xforms)} self-referencing "
                        f"instances (translations inside geometry bbox, "
                        f"skipping transform)")
            elif len(xforms) == 1:
                # Single instance - apply the one transform.
                # For nested CIs (contained in a non-root scope),
                # compose with the parent scope's world transform.
                instances = ci_instances.get(def_ref, [])
                containing_scope = instances[0][1] if instances else 0
                effective_xform = xforms[0]
                if containing_scope > 0:
                    parent_world_xforms = self._get_scope_world_xforms(
                        containing_scope, applied_scope_xforms, scope_to_def)
                    if parent_world_xforms:
                        effective_xform = self._compose_transforms(
                            parent_world_xforms[0], xforms[0])
                        self.log(f"CI def@{def_ref}: composed with parent "
                                f"scope#{containing_scope} transform")

                # Include descendant scopes that have no CI AND no CGroup
                # transform of their own. Their geometry is in this CD's
                # coordinate space. Skip scopes that have CGroup transforms
                # (those get their own transform from the CGroup).
                desc_scopes = self._get_descendant_scopes(
                    scope_num, ci_scopes_set)
                # Remove scopes that have CGroup transforms
                group_xformed_scopes = set()
                for gs, gx, gr in group_transforms:
                    gcd_scope = self._scope_map.get(gr)
                    if gcd_scope is not None:
                        group_xformed_scopes.add(gcd_scope)
                desc_scopes -= group_xformed_scopes
                if desc_scopes:
                    desc_verts = [v for v in self.model.vertices
                                  if v.scope in desc_scopes]
                    target_verts = target_verts + desc_verts
                    self.log(f"CI def@{def_ref}: including {len(desc_verts)} "
                            f"verts from descendant scopes {desc_scopes}")

                self.log(f"Applying CI transform to {len(target_verts)} "
                        f"verts (def@{def_ref}, scope#{scope_num})")
                self._transform_verts(target_verts, effective_xform)
                # Also rotate face normals (rotation only, no translation)
                self._transform_face_normals(scope_num, effective_xform)
                for ds in desc_scopes:
                    self._transform_face_normals(ds, effective_xform)
                # Record this transform so nested CIs in this scope
                # can compose their transforms with it.
                applied_scope_xforms[scope_num] = effective_xform
            else:
                # Multiple instances - DON'T duplicate geometry.
                # Keep geometry in definition-local space and record
                # transforms for glTF node instancing in to_glb.py.
                self.log(f"CI def@{def_ref}: {len(xforms)} instances, "
                        f"{len(target_verts)} verts - using mesh instancing")
                # Collect faces for this definition.
                # If a definition boundary was detected, only include faces
                # within the boundary to avoid including loose geometry.
                # Otherwise collect all scope-matching faces.
                scope_face_indices = []
                if not covers_all and f_start is not None:
                    # Boundary detected - only use definition faces
                    for fi in range(f_start, f_end):
                        f = self.model.faces[fi]
                        if f.scope != scope_num:
                            continue
                        if f.vertices and any(v.scope != scope_num for v in f.vertices):
                            continue
                        scope_face_indices.append(fi)
                else:
                    for fi, f in enumerate(self.model.faces):
                        if f.scope != scope_num:
                            continue
                        if f.vertices and any(v.scope != scope_num for v in f.vertices):
                            continue
                        scope_face_indices.append(fi)
                # If no direct scope faces, include descendant scope faces
                # (container definitions with nested CIs/CGroups)
                if not scope_face_indices:
                    desc = self._get_descendant_scopes(scope_num, set())
                    for fi, f in enumerate(self.model.faces):
                        if f.scope in desc and f.vertices:
                            scope_face_indices.append(fi)
                    if scope_face_indices:
                        self.log(f"CI def@{def_ref}: using {len(scope_face_indices)} "
                                 f"descendant faces from scopes {desc}")
                if scope_face_indices:
                    self.model.def_face_ranges[def_ref] = scope_face_indices
                elif f_start is not None:
                    self.model.def_face_ranges[def_ref] = list(range(f_start, f_end))
                # Compose CI transforms with ancestor placements.
                # Nested CIs (e.g. chair inside desk assembly) have
                # transforms in parent-local space — compose with
                # parent placement(s) to get world-space transforms.
                # Each instance may be in a DIFFERENT containing scope
                # with different (or multiple) world transforms.
                instances = ci_instances.get(def_ref, [])
                composed_xforms = []
                for local_xf, cs in instances:
                    parent_world_xforms = self._get_scope_world_xforms(
                        cs, applied_scope_xforms, scope_to_def)
                    if parent_world_xforms:
                        for pwx in parent_world_xforms:
                            composed_xforms.append(
                                self._compose_transforms(pwx, local_xf))
                    else:
                        composed_xforms.append(local_xf)
                if len(composed_xforms) != len(xforms):
                    self.log(
                        f"CI def@{def_ref}: expanded from "
                        f"{len(xforms)} to {len(composed_xforms)} "
                        f"instances via nested composition")
                self.model.ci_transforms[def_ref] = composed_xforms

    def _get_descendant_scopes(self, scope_num, ci_scopes_set):
        """Get all descendant scopes of scope_num that don't have their own CI.

        When a CD contains nested CDs without explicit CIs, the nested CD
        vertices are in the parent CD's coordinate space and need the
        parent's transform applied.
        """
        descendants = set()
        # Build children map from _scope_parent
        children = {}
        for child, parent in self._scope_parent.items():
            children.setdefault(parent, []).append(child)
        # BFS from scope_num
        queue = children.get(scope_num, [])
        while queue:
            child = queue.pop(0)
            if child in ci_scopes_set:
                continue  # Has its own CI, skip
            descendants.add(child)
            queue.extend(children.get(child, []))
        return descendants

    def _get_scope_world_xforms(self, scope_num, applied_scope_xforms,
                                scope_to_def):
        """Get world-space transform(s) for a scope.

        For single-instance scopes the transform was applied to vertices
        and recorded in applied_scope_xforms — return it directly.
        For multi-instance scopes the transforms are in
        model.ci_transforms — return all of them.
        For root scope (0) return empty list (no ancestor transform).
        Walks up _scope_parent to compose with grandparent transforms.
        """
        if scope_num == 0:
            return []

        # Check single-instance (transform applied to vertices)
        xf = (applied_scope_xforms.get(scope_num) or
              self._v1_scope_transforms.get(scope_num))
        if xf is not None:
            return [xf]

        # Check multi-instance: find the def_ref that owns this scope
        # by looking at which CI was placed IN this scope's parent
        # The containing scope's def opens scope_num.
        # We need the def_ref whose scope == scope_num.
        parent_def = scope_to_def.get(scope_num)
        if parent_def is not None and parent_def in self.model.ci_transforms:
            return list(self.model.ci_transforms[parent_def])

        # Walk up scope_parent chain
        parent = self._scope_parent.get(scope_num)
        if parent is not None and parent > 0:
            return self._get_scope_world_xforms(
                parent, applied_scope_xforms, scope_to_def)

        return []

    def _find_definition_boundary(self, f_start, f_end, v_start, v_end,
                                    target_verts, xforms):
        """Find actual definition geometry boundary when one def covers all faces.

        Detects where definition-local geometry ends and root-level world geometry
        begins by looking for large coordinate jumps between consecutive faces.
        Returns the actual f_end, or None if no clear boundary found.
        """
        if f_start is None or f_end is None:
            return None
        faces = self.model.faces
        if f_end - f_start < 3:
            return None

        # Compute bounding box incrementally; detect when it grows too fast
        # The definition geometry should have a compact bounding box
        prev_bbox_size = 0
        for fi in range(f_start + 1, f_end):
            face = faces[fi]
            if not face.vertices or len(face.vertices) < 3:
                continue
            prev_face = faces[fi - 1]
            if not prev_face.vertices or len(prev_face.vertices) < 3:
                continue

            # Check centroid distance between consecutive faces
            cx = sum(v.x for v in face.vertices) / len(face.vertices)
            cy = sum(v.y for v in face.vertices) / len(face.vertices)
            cz = sum(v.z for v in face.vertices) / len(face.vertices)
            pcx = sum(v.x for v in prev_face.vertices) / len(prev_face.vertices)
            pcy = sum(v.y for v in prev_face.vertices) / len(prev_face.vertices)
            pcz = sum(v.z for v in prev_face.vertices) / len(prev_face.vertices)

            jump = max(abs(cx - pcx), abs(cy - pcy), abs(cz - pcz))

            # Also compute running bbox of faces so far
            all_coords = []
            for fj in range(f_start, fi):
                f = faces[fj]
                if f.vertices:
                    for v in f.vertices:
                        all_coords.append((v.x, v.y, v.z))
            if all_coords:
                bbox_extent = max(
                    max(c[0] for c in all_coords) - min(c[0] for c in all_coords),
                    max(c[1] for c in all_coords) - min(c[1] for c in all_coords),
                    max(c[2] for c in all_coords) - min(c[2] for c in all_coords))
            else:
                bbox_extent = 0

            # If centroid jumps more than 3x the current bbox extent, it's a boundary
            if bbox_extent > 0 and jump > bbox_extent * 3 and fi > f_start + 2:
                self.log(f"Definition boundary: jump={jump:.1f} > "
                        f"3*bbox={bbox_extent*3:.1f} at face {fi}")
                return fi

        return None

    def _compose_transforms(self, parent, child):
        """Compose two 13-double transforms: result = parent * child.
        Applies child first, then parent. Row-major rotation matrices.
        result_R = parent_R * child_R, result_T = parent_R * child_T + parent_T"""
        pR = (parent[0:3], parent[3:6], parent[6:9])
        cR = (child[0:3], child[3:6], child[6:9])
        cT = child[9:12]
        pT = parent[9:12]
        # R_result = pR * cR
        rR = []
        for i in range(3):
            for j in range(3):
                rR.append(pR[i][0]*cR[0][j] + pR[i][1]*cR[1][j] +
                          pR[i][2]*cR[2][j])
        # T_result = pR * cT + pT
        rT = []
        for i in range(3):
            rT.append(pR[i][0]*cT[0] + pR[i][1]*cT[1] +
                      pR[i][2]*cT[2] + pT[i])
        return tuple(rR + rT + [1.0])

    def _transform_verts(self, verts, xform):
        """Apply a 13-double transform (row-major) to a list of vertices.
        Format: [R00,R01,R02, R10,R11,R12, R20,R21,R22, Tx,Ty,Tz, scale]
        Transform: new = R * old + T (R is row-major)."""
        R00, R01, R02 = xform[0], xform[1], xform[2]
        R10, R11, R12 = xform[3], xform[4], xform[5]
        R20, R21, R22 = xform[6], xform[7], xform[8]
        Tx, Ty, Tz = xform[9], xform[10], xform[11]

        # Validate transform: rotation row magnitudes should be near 1.0
        # and all values must be finite. Skip corrupt transforms.
        x_m = math.sqrt(R00*R00 + R01*R01 + R02*R02) if math.isfinite(R00) else float('inf')
        y_m = math.sqrt(R10*R10 + R11*R11 + R12*R12) if math.isfinite(R10) else float('inf')
        z_m = math.sqrt(R20*R20 + R21*R21 + R22*R22) if math.isfinite(R20) else float('inf')
        if not (all(math.isfinite(v) for v in xform[:12]) and
                x_m < 100 and y_m < 100 and z_m < 100):
            self.log(f"Skipping corrupt transform (row mags: {x_m:.2g}, {y_m:.2g}, {z_m:.2g})")
            return

        for v in verts:
            ox, oy, oz = v.x, v.y, v.z
            v.x = ox * R00 + oy * R01 + oz * R02 + Tx
            v.y = ox * R10 + oy * R11 + oz * R12 + Ty
            v.z = ox * R20 + oy * R21 + oz * R22 + Tz

    def _transform_face_normals(self, scope_num, xform):
        """Rotate face normals to match transformed vertices.
        Only applies rotation (no translation) since normals are directions."""
        R00, R01, R02 = xform[0], xform[1], xform[2]
        R10, R11, R12 = xform[3], xform[4], xform[5]
        R20, R21, R22 = xform[6], xform[7], xform[8]
        # Skip if identity rotation
        if (abs(R00-1) < 1e-6 and abs(R11-1) < 1e-6 and abs(R22-1) < 1e-6 and
            abs(R01) < 1e-6 and abs(R02) < 1e-6 and abs(R10) < 1e-6 and
            abs(R12) < 1e-6 and abs(R20) < 1e-6 and abs(R21) < 1e-6):
            return
        for face in self.model.faces:
            if face.scope != scope_num:
                continue
            nx, ny, nz = face.normal
            new_nx = nx * R00 + ny * R01 + nz * R02
            new_ny = nx * R10 + ny * R11 + nz * R12
            new_nz = nx * R20 + ny * R21 + nz * R22
            # Normalize
            mag = math.sqrt(new_nx*new_nx + new_ny*new_ny + new_nz*new_nz)
            if mag > 1e-10:
                face.normal = (new_nx/mag, new_ny/mag, new_nz/mag)

    def _propagate_ci_materials(self):
        """Propagate CI material to unmaterialed faces in its definition scope.

        In SketchUp, painting a CComponentInstance applies that material to
        faces within the component that don't have their own material (the
        'default' material). Faces with explicit materials keep their own.

        Also assigns textured materials to faces with CFaceTextureCoords.
        """
        # Build scope -> CI material map
        ci_scope_mats = {}  # scope_num -> material_idx
        for ci in self.model.component_instances:
            mat_idx = getattr(ci, 'material_idx', -1)
            if mat_idx < 0:
                continue
            def_ref = ci.definition
            if def_ref in self._scope_map:
                ci_scope_mats[self._scope_map[def_ref]] = mat_idx
            for dr, fis in self.model.def_face_ranges.items():
                if fis:
                    scope = self.model.faces[fis[0]].scope
                    if scope not in ci_scope_mats:
                        ci_scope_mats[scope] = mat_idx
        if not ci_scope_mats:
            return

        # Assign textured material to faces with CFaceTextureCoords but no material
        for face in self.model.faces:
            if face.has_texture_coords and face.material_idx < 0:
                for mi, mat in enumerate(self.model.materials):
                    if mat.has_texture:
                        face.material_idx = mi
                        self.log(f"Assigned textured material '{mat.name}' to "
                                 f"face with CFaceTextureCoords")
                        break

        # Apply CI material to unmaterialed faces only
        count = 0
        for face in self.model.faces:
            if face.scope not in ci_scope_mats:
                continue
            if face.material_idx < 0:
                face.material_idx = ci_scope_mats[face.scope]
                count += 1
        if count:
            self.log(f"CI material inheritance: {count} faces assigned")

    def _untransform_verts(self, verts, xform):
        """Apply inverse of a 13-double row-major transform to a list of vertices.
        Assumes the rotation matrix is orthogonal (transpose = inverse).
        Forward: p' = R * p + T, Inverse: p = R^T * (p' - T)."""
        R00, R01, R02 = xform[0], xform[1], xform[2]
        R10, R11, R12 = xform[3], xform[4], xform[5]
        R20, R21, R22 = xform[6], xform[7], xform[8]
        Tx, Ty, Tz = xform[9], xform[10], xform[11]

        for v in verts:
            # Subtract translation first
            dx, dy, dz = v.x - Tx, v.y - Ty, v.z - Tz
            # Apply R^T (transposed rotation = inverse for orthogonal matrix)
            v.x = dx * R00 + dy * R10 + dz * R20
            v.y = dx * R01 + dy * R11 + dz * R21
            v.z = dx * R02 + dy * R12 + dz * R22

    def _parse_entity_list(self, r):
        """
        Parse the entity list sequentially.
        Each entity (CEdge, CFace) is parsed with all its inline sub-objects
        (CVertex, CLoop, CEdgeUse).
        """
        data = r.data
        max_pos = len(data)
        parse_limit = 100000  # safety limit on iterations

        iterations = 0
        while r.tell() < max_pos - 2 and iterations < parse_limit:
            iterations += 1
            tag = r.peek_u16()

            if tag == 0xFFFF:
                # New class
                save_pos = r.tell()
                try:
                    name, is_new, idx = self.arc.read_object_tag()
                    if name is None:
                        # Invalid FFFF tag - skip and scan forward
                        r.seek(save_pos + 2)
                        if not self._scan_to_next_entity(r, max_scan=4096):
                            break
                        continue
                    if name in ('CEdge', 'CFace', 'CLoop', 'CEdgeUse', 'CVertex'):
                        self.in_geometry = True
                    if name == 'CEdge':
                        self._parse_edge(idx)
                    elif name == 'CFace':
                        self._parse_face(idx)
                    elif name == 'CLoop':
                        self._check_face_before_loop(r, save_pos)
                        self._parse_loop_header(idx)
                    elif name == 'CEdgeUse':
                        self._parse_edgeuse(idx)
                    elif name == 'CVertex':
                        self._parse_vertex(idx, validate=True)
                    elif name == 'CMaterial':
                        self._parse_material(idx)
                    elif name == 'CLayer':
                        self._parse_layer_inline(idx)
                    elif name == 'CThumbnail':
                        # CThumbnail is a model-level entity that appears
                        # after the last CComponentDefinition's geometry.
                        # Close the CD scope so subsequent geometry goes
                        # to the root scope.
                        if (self.current_scope > 0 and
                                self.model.version_major >= 5 and
                                self._scope_stack and
                                self._scope_stack[-1][0] ==
                                'CComponentDefinition'):
                            self._close_scope()
                            self.current_scope = 0
                        self.log(f"Parsing CThumbnail")
                        if not self._parse_thumbnail(idx):
                            break
                    elif name == 'CDib':
                        self.arc.set_object(idx, {'type': 'CDib'})
                        self._skip_cdib_data(r)
                    elif name == 'CComponentInstance':
                        # v5+: CIs inside a CD scope are nested (their
                        # transforms are relative to the CD's local space).
                        # CThumbnail closes the CD scope, so CIs after the
                        # thumbnail get containing_scope=0 (root) and CIs
                        # before it get containing_scope=CD_scope (nested).
                        if not self._parse_component_instance(idx):
                            break
                    elif name in ('CComponentDefinition',
                                  'CGroup', 'CDefinitionList'):
                        # Container/non-geometry class - new scope for geometry
                        if name in ('CComponentDefinition', 'CGroup'):
                            scope_id = self._next_scope_id
                            self._next_scope_id += 1
                            self._scope_parent[scope_id] = self.current_scope
                            self.current_scope = scope_id
                            self._close_scope()
                            self._scope_stack.append(
                                (name, idx, self.current_scope))
                            # v1: track if this scope was preceded by a CI+CD pair
                            if (self.model.version_major < 3 and
                                    name == 'CComponentDefinition' and
                                    self._v1_last_was_ci):
                                self._v1_ci_cd_scopes.add(self.current_scope)
                                self.log(f"v1 scope#{self.current_scope} is CI+CD pair")
                            self._v1_last_was_ci = False
                        if name == 'CComponentDefinition':
                            # Track geometry start for this definition
                            self._def_geo_start[idx] = (
                                len(self.model.vertices),
                                len(self.model.edges),
                                len(self.model.faces))
                        if name == 'CGroup':
                            self.arc.set_object(idx, {'type': name})
                            self.log(f"Parsing CGroup[{idx}] (scope={self.current_scope})")
                            if not self._parse_group_inline(idx, r):
                                break
                        else:
                            self.arc.set_object(idx, {'type': name})
                            self.log(f"Scanning past {name} (scope={self.current_scope})")
                            if (name == 'CComponentDefinition' and
                                    self.model.version_major < 3):
                                # v1/v2 CD entity: entity_base(7) + u16 + u16 = 11 bytes
                                r.read(7)   # entity_base (all zeros)
                                r.u16()     # definition index
                                r.u16()     # null
                            elif (name == 'CComponentDefinition' and
                                    self.model.version_major == 4):
                                self._parse_cd_v4(idx, r)
                            elif (name == 'CComponentDefinition' and
                                    self.model.version_major == 3):
                                # v3 CD entity: entity_base(9) + 6 zeros +
                                # flag(u8). If flag>0: 3 more bytes (19 total).
                                # If flag==0: 11 more bytes (27 total).
                                r.read(9)    # entity_base
                                r.read(6)    # 6 zero bytes
                                flag = r.u8()  # flag at byte 15
                                if flag > 0:
                                    r.read(3)   # 3 more bytes (total 19)
                                else:
                                    r.read(11)  # 11 more bytes (total 27)
                            elif (name == 'CComponentDefinition' and
                                    self.model.version_major >= 5):
                                self._parse_cd_v5(idx, r)
                            else:
                                # unknown: scan past header
                                scan_size = 128 if not is_new and name == 'CComponentDefinition' else 8192
                                if not self._scan_to_next_entity(r, max_scan=scan_size):
                                    break
                    elif name == 'CCamera':
                        self._parse_camera_inline(idx)
                    elif name in ('CAttributeContainer', 'CAttributeNamed',
                                   'CFaceTextureCoords'):
                        self.arc.set_object(idx, {'type': name})
                        self.log(f"Skipping {name}")
                        if not self._scan_to_next_entity(r, max_scan=8192):
                            break
                    elif name == 'CRelationship':
                        self.arc.set_object(idx, {'type': name})
                        if self.model.version_major == 4:
                            # v4: 6 bytes: null(u16) + face_ref(u16) + ci_ref(u16)
                            r.u16()  # null
                            face_ref = r.u16()
                            ci_ref = r.u16()
                            self._cut_opening_pairs.append((face_ref, ci_ref))
                            self.log(f"CRelationship[{idx}]: face@{face_ref} ci@{ci_ref}")
                            self._try_read_v3_scope_close(r)
                        elif self.model.version_major <= 3:
                            # v3: 4 bytes: 2 u16 refs
                            r.u16()
                            r.u16()
                            self.log(f"CRelationship[{idx}]: 4 bytes")
                            self._try_read_v3_scope_close(r)
                        elif self.model.version_major == 5:
                            # v5: same as v4 (6 bytes)
                            r.u16()  # null
                            face_ref = r.u16()
                            ci_ref = r.u16()
                            self._cut_opening_pairs.append((face_ref, ci_ref))
                            self.log(f"CRelationship[{idx}]: face@{face_ref} ci@{ci_ref}")
                        else:
                            if not self._scan_to_next_entity(r):
                                break
                    elif name == 'CArcCurve':
                        self.arc.set_object(idx, {'type': name})
                        if self.model.version_major <= 4:
                            self._parse_arccurve_inline(idx)
                        elif self.model.version_major == 5:
                            # v5: 119 bytes = u16(0) + u8(flags) + u32(edge_count)
                            # + 14 f64 (center/normal/xaxis/yaxis/radius/angle)
                            r.skip(119)
                        else:
                            self.log(f"Skipping unknown class {name}")
                            if not self._scan_to_next_entity(r):
                                break
                    elif name in ('CSkFont', 'CSkpStyle', 'CSkpStyleManager'):
                        # End of main geometry section
                        self.arc.set_object(idx, {'type': name})
                        break
                    else:
                        # Unknown class, skip to next entity
                        self.arc.set_object(idx, {'type': name})
                        self.log(f"Skipping unknown class {name}")
                        if not self._scan_to_next_entity(r):
                            break
                except Exception as e:
                    self.log(f"Error at {hex(save_pos)}: {e}")
                    # Try to recover by scanning forward
                    r.seek(save_pos + 2)
                    if not self._scan_to_next_entity(r, max_scan=4096):
                        break
                continue

            if tag >= 0x8000:
                class_idx = tag & 0x7FFF

                # Try offset-adjusted lookup: class indices can drift due to
                # inline CLayer registrations in CDs. Check nearby offsets.
                if class_idx not in self.arc.class_map:
                    for delta in range(1, max(self._class_offset + 3, 4)):
                        adjusted = class_idx - delta
                        if adjusted in self.arc.class_map:
                            self.arc.class_map[class_idx] = (
                                self.arc.class_map[adjusted])
                            if self._class_offset == 0:
                                self._class_offset = delta
                                self.log(f"Detected MFC class offset: "
                                         f"{delta} (class@{class_idx} -> "
                                         f"{self.arc.class_map[adjusted]})")
                            break

                # Try to identify unknown class back-refs by probing data patterns
                # Only in geometry context and within reasonable range
                # Use large gap tolerance since MFC map offset grows throughout file
                if (class_idx not in self.arc.class_map and
                        self.in_geometry and
                        class_idx <= self.arc.map_count + 500):
                    identified = self._identify_unknown_class(r, class_idx)
                    if identified:
                        self._fill_map_gap(class_idx, identified)

                if class_idx in self.arc.class_map:
                    cname = self.arc.class_map[class_idx]
                    save_pos = r.tell()
                    try:
                        r.u16()  # consume tag
                        idx = self.arc.register_object(None)
                        self.arc.log(f"INST {cname} (class@{class_idx}) obj@{idx}")

                        if cname == 'CEdge':
                            self._parse_edge(idx)
                        elif cname == 'CFace':
                            self._parse_face(idx)
                        elif cname == 'CLoop':
                            self._check_face_before_loop(r, save_pos)
                            self._parse_loop_header(idx)
                        elif cname == 'CEdgeUse':
                            self._parse_edgeuse(idx)
                        elif cname == 'CVertex':
                            # When class offset detected, writer's CEdge class
                            # index may collide with our CVertex class index.
                            # Check if data actually looks like CEdge (12-byte
                            # entity base with flags pattern) rather than CVertex.
                            if (self._class_offset > 0 and
                                    self.model.version_major >= 5 and
                                    r.remaining() >= 12):
                                peek = data[r.tell():r.tell()+12]
                                # CEdge: entity_id(4) + flags(4) + layer(2) + mat(2)
                                # Flags pattern: bytes 4-7 typically 00/01 values
                                flags = peek[4:8]
                                if all(b <= 1 for b in flags):
                                    # Looks like CEdge entity base, not CVertex
                                    self.log(f"Reclassified CVertex@{idx} as CEdge "
                                            f"(class offset collision)")
                                    self._parse_edge(idx)
                                else:
                                    self._parse_vertex(idx, validate=True)
                            else:
                                self._parse_vertex(idx, validate=True)
                        elif cname == 'CMaterial':
                            self._parse_material(idx)
                        elif cname == 'CLayer':
                            self._parse_layer_inline(idx)
                        elif cname == 'CThumbnail':
                            if (self.current_scope > 0 and
                                    self.model.version_major >= 5 and
                                    self._scope_stack and
                                    self._scope_stack[-1][0] ==
                                    'CComponentDefinition'):
                                self._close_scope()
                                self.current_scope = 0
                            self.log(f"Parsing CThumbnail (back-ref)")
                            if not self._parse_thumbnail(idx):
                                break
                            pass  # post-thumbnail scope handled elsewhere
                        elif cname == 'CDib':
                            self.arc.set_object(idx, {'type': 'CDib'})
                            self._skip_cdib_data(r)
                        elif cname == 'CComponentInstance':
                            if not self._parse_component_instance(idx):
                                break
                        elif cname in ('CComponentDefinition',
                                       'CGroup', 'CDefinitionList'):
                            if cname in ('CComponentDefinition', 'CGroup'):
                                scope_id = self._next_scope_id
                                self._next_scope_id += 1
                                self._scope_parent[scope_id] = self.current_scope
                                self.current_scope = scope_id
                                self._close_scope()
                                self._scope_stack.append(
                                    (cname, idx, self.current_scope))
                                if (self.model.version_major < 3 and
                                        cname == 'CComponentDefinition' and
                                        self._v1_last_was_ci):
                                    self._v1_ci_cd_scopes.add(self.current_scope)
                                    self.log(f"v1 scope#{self.current_scope} is CI+CD pair")
                                self._v1_last_was_ci = False
                            if cname == 'CComponentDefinition':
                                self._def_geo_start[idx] = (
                                    len(self.model.vertices),
                                    len(self.model.edges),
                                    len(self.model.faces))
                            if cname == 'CGroup':
                                self.arc.set_object(idx, {'type': cname})
                                self.log(f"Parsing CGroup[{idx}] (scope={self.current_scope})")
                                if not self._parse_group_inline(idx, r):
                                    break
                            else:
                                self.arc.set_object(idx, {'type': cname})
                                self.log(f"Scanning past {cname} (scope={self.current_scope})")
                                if (cname == 'CComponentDefinition' and
                                        self.model.version_major < 3):
                                    # v1/v2 CD entity: entity_base(7) + u16 + u16 = 11 bytes
                                    r.read(7)   # entity_base (all zeros)
                                    r.u16()     # definition index
                                    r.u16()     # null
                                elif (cname == 'CComponentDefinition' and
                                        self.model.version_major == 4):
                                    self._parse_cd_v4(idx, r)
                                elif (cname == 'CComponentDefinition' and
                                        self.model.version_major == 3):
                                    # v3 CD INST entity data
                                    r.read(9)    # entity_base
                                    r.read(6)    # 6 zero bytes
                                    flag = r.u8()  # flag at byte 15
                                    if flag > 0:
                                        r.read(3)
                                    else:
                                        r.read(11)
                                elif (cname == 'CComponentDefinition' and
                                        self.model.version_major >= 5):
                                    self._parse_cd_v5(idx, r, is_inst=True)
                                else:
                                    # unknown: scan past
                                    scan_size = 128 if cname == 'CComponentDefinition' else 8192
                                    if not self._scan_to_next_entity(r, max_scan=scan_size):
                                        break
                        elif cname == 'CCamera':
                            self._parse_camera_inline(idx)
                        elif cname in ('CAttributeContainer', 'CAttributeNamed',
                                       'CFaceTextureCoords'):
                            self.arc.set_object(idx, {'type': cname})
                            self.log(f"Skipping {cname} (back-ref)")
                            if not self._scan_to_next_entity(r, max_scan=8192):
                                break
                        elif cname == 'CRelationship':
                            self.arc.set_object(idx, {'type': cname})
                            if self.model.version_major == 4:
                                # v4: 6 bytes
                                r.u16()  # null
                                face_ref = r.u16()
                                ci_ref = r.u16()
                                self._cut_opening_pairs.append((face_ref, ci_ref))
                                self.log(f"CRelationship INST[{idx}]: face@{face_ref} ci@{ci_ref}")
                                self._try_read_v3_scope_close(r)
                            elif self.model.version_major <= 3:
                                # v3: 4 bytes
                                r.u16()
                                r.u16()
                                self.log(f"CRelationship INST[{idx}]: 4 bytes")
                                # After 2nd CRel, scope-close metadata may follow.
                                self._try_read_v3_scope_close(r)
                            elif self.model.version_major == 5:
                                # v5: same as v4 (6 bytes)
                                r.u16()  # null
                                face_ref = r.u16()
                                ci_ref = r.u16()
                                self._cut_opening_pairs.append((face_ref, ci_ref))
                                self.log(f"CRelationship INST[{idx}]: face@{face_ref} ci@{ci_ref}")
                            else:
                                if not self._scan_to_next_entity(r):
                                    break
                        elif cname == 'CArcCurve':
                            if self.model.version_major <= 4:
                                self._parse_arccurve_inline(idx)
                            elif self.model.version_major == 5:
                                self.arc.set_object(idx, {'type': cname})
                                # v5: 119 bytes = u16(0) + u8(flags) +
                                # u32(edge_count) + 14 f64 (arc params)
                                r.skip(119)
                            else:
                                self.arc.set_object(idx, {'type': cname})
                                if not self._scan_to_next_entity(r):
                                    break
                        elif cname in ('CSkFont', 'CSkpStyle', 'CSkpStyleManager'):
                            self.arc.set_object(idx, {'type': cname})
                            break
                        else:
                            self.arc.set_object(idx, {'type': cname})
                            self.log(f"Skipping unknown class {cname}")
                            if not self._scan_to_next_entity(r):
                                break
                    except Exception as e:
                        self.log(f"Error at {hex(save_pos)} ({cname}): {e}")
                        # Try to recover by scanning forward
                        r.seek(save_pos + 2)
                        if not self._scan_to_next_entity(r, max_scan=4096):
                            break
                    continue

            # Not a recognized MFC tag.
            # Could be:
            # - Data between objects (loop trailing bytes, face texture coords)
            # - Object back-reference to a non-class object
            # - End of entity list
            #
            # Strategy: skip forward byte by byte looking for next valid tag
            if tag == 0x0000:
                r.u16()  # consume NULL
                continue

            if 0 < tag <= self.arc.map_count:
                # Object back-reference — check if it's a Material
                # (v5+ EU trailing data includes material refs)
                obj = self.arc.get_object(tag)
                if (isinstance(obj, Material) and
                        hasattr(self, '_last_parsed_face') and
                        self._last_parsed_face and
                        self._last_parsed_face.material_idx < 0):
                    try:
                        mi = self.model.materials.index(obj)
                        self._last_parsed_face.material_idx = mi
                        self.log(f"Back material '{obj.name}' assigned "
                                f"to face from trailing ref")
                    except ValueError:
                        pass
                r.u16()
                continue

            # v3/v4: MFC counter drift causes some object back-refs to
            # be slightly above our map_count.  Consume if within small
            # tolerance and next u16 looks like a valid entity tag.
            if (self.model.version_major in (3, 4) and
                    0 < tag <= self.arc.map_count + 10 and
                    r.remaining() >= 4):
                peek_next = struct.unpack_from('<H', r.data, r.tell() + 2)[0]
                if (peek_next >= 0x8000 or peek_next == 0xFFFF or
                        peek_next == 0 or
                        0 < peek_next <= self.arc.map_count + 10):
                    r.u16()
                    continue

            # v3/v4 scope-close metadata: appears after last entity of
            # CD scope without CRelationship marker.
            if (self.model.version_major in (3, 4) and
                    self._try_read_v3_scope_close(r)):
                continue

            # v3/v4 root scope metadata: geo-location + model settings
            # before CSkFont at end of entity list.
            if self.model.version_major in (3, 4):
                target = b'\xff\xff\x00\x00\x07\x00CSkFont'
                idx = r.data.find(target, r.tell())
                if 0 <= idx - r.tell() < 1024:
                    skipped = idx - r.tell()
                    self.log(f"v3 root metadata: {skipped}B to CSkFont")
                    r.seek(idx)
                    continue

            # Unknown data - scan forward for next valid MFC tag
            # but only scan a limited distance
            found = False
            scan_start = r.tell()
            scan_limit = min(r.tell() + 512, max_pos - 2)

            while r.tell() < scan_limit:
                tv = struct.unpack_from('<H', r.data, r.tell())[0]

                # Check for FFFF new class intro
                if tv == 0xFFFF and r.tell() + 6 < max_pos:
                    nl = struct.unpack_from('<H', r.data, r.tell() + 4)[0]
                    if 1 <= nl <= 30 and r.tell() + 6 + nl <= max_pos:
                        try:
                            cn = r.data[r.tell() + 6:r.tell() + 6 + nl].decode('ascii')
                            if cn and cn[0] == 'C' and cn.isalnum():
                                found = True
                                break
                        except (UnicodeDecodeError, IndexError):
                            pass

                # Check for class back-ref (0x8XXX)
                if tv >= 0x8000:
                    ci = tv & 0x7FFF
                    if ci in self.arc.class_map:
                        found = True
                        break
                    # Try to identify unknown class by probing (only in geometry context)
                    if self.in_geometry and ci <= self.arc.map_count + 50:
                        save_r = r.tell()
                        identified = self._identify_unknown_class(r, ci)
                        r.seek(save_r)
                        if identified:
                            self._fill_map_gap(ci, identified)
                            found = True
                            break

                r.skip(1)

            if found:
                skipped = r.tell() - scan_start
                if skipped > 0:
                    self.log(f"Skipped {skipped} bytes at {hex(scan_start)}")
                # v1/v2: Check if skipped bytes contain CD metadata
                # (identity transform pattern), indicating a scope close.
                # CD metadata starts with a 13-double identity transform.
                if (skipped >= 80 and self.current_scope > 0 and
                        self.model.version_major < 3 and
                        self._scope_stack):
                    # Search for identity transform pattern in and around
                    # skipped region (CD metadata may start a few bytes
                    # before the skip due to trailing zeros from prev entity)
                    search_start = max(0, scan_start - 8)
                    search_end = scan_start + skipped
                    search_data = r.data[search_start:search_end]
                    search_len = len(search_data)
                    for si in range(min(search_len - 104, 20)):
                        try:
                            vals = struct.unpack_from('<13d', search_data, si)
                        except struct.error:
                            continue
                        # Identity rotation + scale=1.0
                        if (abs(vals[0] - 1.0) < 0.01 and
                                abs(vals[4] - 1.0) < 0.01 and
                                abs(vals[8] - 1.0) < 0.01 and
                                abs(vals[12] - 1.0) < 0.01 and
                                all(abs(vals[i]) < 0.01
                                    for i in (1, 2, 3, 5, 6, 7))):
                            identity_abs_pos = search_start + si
                            self.log(f"v1 scope#{self.current_scope}: "
                                    f"CD metadata detected at "
                                    f"{hex(identity_abs_pos)}, "
                                    f"closing scope")
                            self._close_scope(
                                identity_pos=identity_abs_pos)
                            self.current_scope = 0
                            break
                # Check if we skipped over a tagless face entity base.
                # This happens in v7 files where faces inside definitions
                # don't have class tags. Only trigger when:
                # 1. Significant data was skipped (>80 bytes, enough for FTC + face)
                # 2. The next tag is a CLoop class back-ref
                # 3. We already have at least one face parsed
                if (skipped > 48 and self.in_geometry and
                        self.model.version_major >= 5 and
                        len(self.model.faces) > 0):
                    tv_next = struct.unpack_from('<H', r.data, r.tell())[0]
                    next_is_loop = False
                    if tv_next >= 0x8000:
                        nci = tv_next & 0x7FFF
                        next_is_loop = self.arc.class_map.get(nci) == 'CLoop'
                    elif tv_next == 0xFFFF:
                        nl = struct.unpack_from('<H', r.data, r.tell() + 4)[0]
                        if 1 <= nl <= 30:
                            try:
                                cn = r.data[r.tell()+6:r.tell()+6+nl].decode('ascii')
                                next_is_loop = (cn == 'CLoop')
                            except Exception:
                                pass
                    if next_is_loop:
                        self._try_extract_tagless_face(r, scan_start, skipped)
                continue
            else:
                self.log(f"No valid tag found after {hex(scan_start)}, stopping")
                break

        self.log(f"Parsed {len(self.model.edges)} edges, {len(self.model.faces)} faces, "
                 f"{len(self.model.vertices)} vertices")

        # v3/v4: consume trailing model metadata (font, dimension, rendering settings)
        if self.model.version_major in (3, 4):
            self._read_v3_model_metadata(r)

        # Close any remaining open scope
        self._close_scope()

        # Resolve incomplete CEdge dicts before face reconstruction (v1 only)
        if self.model.version_major < 3:
            self._resolve_incomplete_edges()

        # Reconstruct face vertices: CEdgeUse chains first, then edge-based heuristics
        self._reconstruct_faces()
        self._remove_outlier_vertices()
        self._reconstruct_multiloop_faces()
        self._remove_hole_blocking_faces()
        self._fill_glass_pane_faces()
        self._infer_missing_faces()

        # Fix face scopes: if all vertices are from a different scope,
        # reassign the face to match. Only for v5+ where MFC drift can
        # cause incorrect face scope assignment. For v3/v4, the face scope
        # from parsing is authoritative (CGroup faces share vertices with
        # root scope, so vertex majority would incorrectly reassign them).
        if self.model.version_major >= 5:
            from collections import Counter
            for face in self.model.faces:
                if not face.vertices:
                    continue
                v_scopes = [v.scope for v in face.vertices
                            if v.scope is not None]
                if not v_scopes:
                    continue
                scope_counts = Counter(v_scopes)
                if len(scope_counts) == 1:
                    majority_scope = scope_counts.most_common(1)[0][0]
                    if majority_scope != face.scope:
                        self.log(f"Fixing face scope {face.scope} -> "
                                f"{majority_scope} (vertex majority)")
                        face.scope = majority_scope

        # Apply component instance and group transforms
        self._apply_transforms()

        # Apply cut-opening holes to host faces from CRelationship data
        if self._cut_opening_pairs:
            self._apply_cut_openings()

        # Propagate CI material to unmaterialed faces within CI scope
        # (SketchUp's "paint bucket" inheritance: CI material applies to
        # faces that don't have their own explicit material)
        if self.model.version_major >= 3:
            self._propagate_ci_materials()

        # After transforms: drop faces with mixed vertex scopes that involve
        # instanced meshes (their vertices are in different coordinate spaces).
        if self.model.ci_transforms:
            instanced_scopes = set()
            for def_ref, face_indices in self.model.def_face_ranges.items():
                if def_ref in self.model.ci_transforms:
                    # Get the scope from the faces in this range
                    if isinstance(face_indices, (list, set)):
                        for fi in face_indices:
                            if fi < len(self.model.faces):
                                instanced_scopes.add(self.model.faces[fi].scope)
                                break
            if instanced_scopes:
                # Build set of faces to drop (by id) - only if few mixed faces
                # (many mixed faces = systematic cross-scope reconstruction, keep them)
                drop_ids = set()
                for face in self.model.faces:
                    if not face.vertices:
                        continue
                    v_scopes = set(v.scope for v in face.vertices
                                   if v.scope is not None)
                    if len(v_scopes) > 1 and v_scopes & instanced_scopes:
                        drop_ids.add(id(face))
                # Only drop if few artifacts (not systematic cross-scope issue)
                if len(drop_ids) > 5:
                    self.log(f"Skipping mixed-scope face drop "
                            f"({len(drop_ids)} faces too many)")
                    drop_ids = set()
                elif drop_ids:
                    self.log(f"Dropping {len(drop_ids)} mixed-scope faces "
                            f"(instanced scopes={instanced_scopes})")
                if drop_ids:
                    # Rebuild face list and update def_face_ranges
                    old_faces = self.model.faces
                    new_faces = [f for f in old_faces if id(f) not in drop_ids]
                    # Build old->new index map
                    old_to_new = {}
                    ni = 0
                    for oi, f in enumerate(old_faces):
                        if id(f) not in drop_ids:
                            old_to_new[oi] = ni
                            ni += 1
                    # Update def_face_ranges
                    for def_ref in list(self.model.def_face_ranges.keys()):
                        indices = self.model.def_face_ranges[def_ref]
                        if isinstance(indices, (list, set)):
                            new_indices = [old_to_new[i] for i in indices
                                          if i in old_to_new]
                            self.model.def_face_ranges[def_ref] = new_indices
                        else:
                            f_s, f_e = indices
                            new_indices = [old_to_new[i]
                                          for i in range(f_s, f_e)
                                          if i in old_to_new]
                            self.model.def_face_ranges[def_ref] = new_indices
                    self.model.faces = new_faces
                    self.log(f"Dropped {len(drop_ids)} mixed-scope faces")

    def _parse_vertex(self, idx, validate=False):
        """Parse CVertex: version-dependent base + 3 doubles.
        If validate=True, check coordinates for sanity. Corrupt vertices
        are still consumed (to keep MFC map counter in sync) but placed
        at origin so they don't affect geometry."""
        r = self.arc.r
        # v3: 0 bytes base, v4+: 2 bytes base
        if self.model.version_major >= 4:
            r.skip(2)
        x, y, z = r.f64(), r.f64(), r.f64()
        # Validate coordinates: clamp clearly corrupt values to origin
        if validate and (abs(x) > 1e7 or abs(y) > 1e7 or abs(z) > 1e7 or
                         x != x or y != y or z != z):
            self.log(f"Vertex[{idx}]: clamped corrupt coords "
                    f"({x:.4g}, {y:.4g}, {z:.4g})")
            x, y, z = 0.0, 0.0, 0.0
        v = Vertex(x, y, z, idx, scope=self.current_scope)
        self.model.vertices.append(v)
        self.arc.set_object(idx, v)

    def _read_vertex_ref(self):
        """Read a vertex reference (new, class back-ref, or object back-ref)."""
        r = self.arc.r
        tag = r.peek_u16()

        if tag == 0x0000:
            r.u16()
            return None

        if tag == 0xFFFF:
            name, is_new, idx = self.arc.read_object_tag()
            if name == 'CVertex':
                self._parse_vertex(idx)
                return self.arc.get_object(idx)
            return None

        if tag >= 0x8000:
            class_idx = tag & 0x7FFF
            # Try offset-adjusted lookup if class_idx not directly in map
            if class_idx not in self.arc.class_map and self._class_offset > 0:
                adjusted = class_idx - self._class_offset
                if adjusted in self.arc.class_map:
                    self.arc.class_map[class_idx] = self.arc.class_map[adjusted]
            if class_idx in self.arc.class_map and self.arc.class_map[class_idx] == 'CVertex':
                r.u16()
                # Fill map gap if needed
                while self.arc.map_count < class_idx:
                    self.arc.register_object({'type': 'skipped'})
                idx = self.arc.register_object(None)
                self.arc.log(f"INST CVertex (class@{class_idx}) obj@{idx}")
                self._parse_vertex(idx)
                return self.arc.get_object(idx)
            # Unknown class back-ref - check if data after tag looks like vertex
            base_skip = 2 if self.model.version_major >= 4 else 0
            peek_offset = r.tell() + 2 + base_skip
            if peek_offset + 24 <= r.size:
                vals = struct.unpack_from('<ddd', r.data, peek_offset)
                if all(abs(v) < 100000 for v in vals):
                    # Data looks like vertex coordinates - parse as CVertex
                    # Detect offset if this is first mismatch
                    if class_idx not in self.arc.class_map:
                        existing_cv = self.arc.find_class_idx('CVertex')
                        if existing_cv is not None and self._class_offset == 0:
                            self._class_offset = class_idx - existing_cv
                            self.log(f"Detected MFC class offset: {self._class_offset}")
                            for ci, cn in list(self.arc.class_map.items()):
                                new_ci = ci + self._class_offset
                                if new_ci not in self.arc.class_map:
                                    self.arc.class_map[new_ci] = cn
                        while self.arc.map_count < class_idx:
                            self.arc.register_object({'type': 'skipped'})
                        self.arc.class_map[class_idx] = 'CVertex'
                    r.u16()
                    idx = self.arc.register_object(None)
                    self.arc.log(f"INST CVertex (class@{class_idx} probed) obj@{idx}")
                    self._parse_vertex(idx)
                    return self.arc.get_object(idx)
            return None

        if 0 < tag < 0x8000:
            obj = self.arc.get_object(tag)
            if isinstance(obj, Vertex):
                r.u16()
                return obj
            r.u16()
            return None

        return None

    def _parse_edge(self, idx):
        """Parse CEdge: version-dependent base + start_vertex + end_vertex."""
        r = self.arc.r
        if self.model.version_major >= 5:
            # v5+: entity_id(4) + flags(4) + layer_ref(2) + mat_ref(2) = 12 bytes
            entity_id = r.u32()
            flags = r.read(4)
            layer_ref = r.u16()
            mat_ref = r.u16()
        elif self.model.version_major == 4:
            # v4: entity_id(4) + flags(4) + layer_ref(2) + trailing(1) = 11 bytes
            entity_id = r.u32()
            flags = r.read(4)
            layer_ref = r.u16()
            r.u8()
        elif self.model.version_major >= 3:
            # v3: entity_id(4) + flags(2) + layer_ref(2) + trailing(1) = 9 bytes
            entity_id = r.u32()
            flags = r.read(2)
            layer_ref = r.u16()
            r.u8()  # trailing byte
        else:
            # v1-v2: entity_id(4) + flags(u8) + layer_ref(MFC u16) = 7 bytes
            entity_id = r.u32()
            flags = r.read(1)
            self._read_v1_layer_ref(r)

        # Save raw ref tags before reading (for deferred resolution)
        sv_raw_tag = self.arc.r.peek_u16()
        sv = self._read_vertex_ref()
        ev_raw_tag = self.arc.r.peek_u16()
        ev = self._read_vertex_ref()

        # v6+: standalone CEdges have a trailing u16 (partner/curve ref)
        # that must be consumed to keep stream aligned. In v5, this trailing
        # ref is consumed by _parse_edge_inline within CEdgeUse chains.
        if self.model.version_major >= 6 and r.remaining() >= 2:
            trailing_tag = r.peek_u16()
            # Trailing ref is a u16 that can be 0 (null), object backref,
            # or class backref. Only consume if it's NOT a known entity tag
            # that starts the next top-level entity.
            if trailing_tag == 0x0000:
                r.u16()  # consume null trailing
            elif 0 < trailing_tag < 0x8000:
                r.u16()  # consume object backref trailing

        if sv and ev:
            soft = bool(flags[1]) if len(flags) > 1 else False
            smooth = bool(flags[2]) if len(flags) > 2 else False
            edge = Edge(sv, ev, soft, smooth, idx)
            self.model.edges.append(edge)
            self.arc.set_object(idx, edge)
        else:
            # Store raw ref tags for deferred resolution (object backrefs only)
            sv_tag = sv_raw_tag if not sv and 0 < sv_raw_tag < 0x8000 else None
            ev_tag = ev_raw_tag if not ev and 0 < ev_raw_tag < 0x8000 else None
            self.arc.set_object(idx, {
                'type': 'CEdge', 'incomplete': True,
                'sv': sv, 'ev': ev,
                'sv_raw': sv_tag, 'ev_raw': ev_tag
            })

    def _consume_inline_objects(self, r, scan_limit):
        """Consume inline MFC objects (CAttributeContainer, CFaceTextureCoords, etc.)
        between a class intro and entity base. Registers classes/objects to keep
        the MFC map counter in sync. Stops when data doesn't look like an MFC tag."""
        while r.tell() < scan_limit:
            tag = r.peek_u16()
            if tag == 0xFFFF:
                # New class intro - register it
                save = r.tell()
                try:
                    name, is_new, obj_idx = self.arc.read_object_tag()
                    if name:
                        self.arc.set_object(obj_idx, {'type': name, 'inline': True})
                        continue
                except:
                    r.seek(save)
                    break
            elif tag >= 0x8000:
                class_idx = tag & 0x7FFF
                if class_idx in self.arc.class_map:
                    # Known class back-ref - consume and register object
                    r.u16()
                    obj_idx = self.arc.register_object({'type': self.arc.class_map[class_idx], 'inline': True})
                    continue
            elif tag == 0x0000:
                r.u16()  # consume NULL
                continue
            # Not a recognizable MFC tag - stop
            break

    def _identify_unknown_class(self, r, class_idx):
        """Try to identify an unknown class back-ref by probing the data after the tag.
        Returns the class name if identified, None otherwise.
        Does NOT consume any bytes - caller must handle that.
        Checks are ordered from most specific to least specific to minimize false positives."""
        pos = r.tell() + 2  # position after tag would be consumed
        data = r.data
        remaining = r.size - pos

        if remaining < 4:
            return None

        # Check CFace first: entity_base + valid unit normal is very specific
        base_size = 12 if self.model.version_major >= 5 else (11 if self.model.version_major == 4 else 9)
        if remaining >= base_size + 36:
            try:
                nx = struct.unpack_from('<d', data, pos + base_size)[0]
                ny = struct.unpack_from('<d', data, pos + base_size + 8)[0]
                nz = struct.unpack_from('<d', data, pos + base_size + 16)[0]
                mag_sq = nx * nx + ny * ny + nz * nz
                if 0.95 < mag_sq < 1.05:
                    dist = struct.unpack_from('<d', data, pos + base_size + 24)[0]
                    loop_count = struct.unpack_from('<I', data, pos + base_size + 32)[0]
                    if 0 < loop_count <= 100 and abs(dist) < 1e8:
                        return 'CFace'
            except struct.error:
                pass

        # Check CEdgeUse: 0 bytes of data for v5+, then NULL, then what looks like CEdge
        # Pattern: [tag] [NULL] [class_ref with CEdge-like data after it]
        if self.model.version_major >= 5 and remaining >= 4:
            next_val = struct.unpack_from('<H', data, pos)[0]
            if next_val == 0x0000:
                after_null = struct.unpack_from('<H', data, pos + 2)[0]
                if after_null >= 0x8000:
                    ci2 = after_null & 0x7FFF
                    edge_start = pos + 4  # position after CEdge tag
                    if ci2 in self.arc.class_map:
                        if self.arc.class_map[ci2] == 'CEdge':
                            return 'CEdgeUse'
                    elif ci2 <= self.arc.map_count + 50 and edge_start + 14 <= r.size:
                        # Check if data after the second tag looks like CEdge
                        # CEdge entity base (12) + vertex ref
                        vref = struct.unpack_from('<H', data, edge_start + 12)[0]
                        if (vref == 0xFFFF or
                            (vref >= 0x8000 and self.arc.class_map.get(vref & 0x7FFF) == 'CVertex') or
                            (0 < vref <= self.arc.map_count and
                             isinstance(self.arc.get_object(vref), Vertex))):
                            return 'CEdgeUse'

        # Check CEdge: entity_base(12) + vertex_ref tag
        if self.model.version_major >= 5 and remaining >= 14:
            vref_pos = pos + 12
            if vref_pos + 2 <= r.size:
                vref_tag = struct.unpack_from('<H', data, vref_pos)[0]
                if vref_tag == 0xFFFF:
                    if vref_pos + 6 < r.size:
                        nl = struct.unpack_from('<H', data, vref_pos + 4)[0]
                        if 1 <= nl <= 10 and vref_pos + 6 + nl <= r.size:
                            try:
                                cn = data[vref_pos + 6:vref_pos + 6 + nl].decode('ascii')
                                if cn == 'CVertex':
                                    return 'CEdge'
                            except:
                                pass
                elif vref_tag >= 0x8000:
                    cname = self.arc.class_map.get(vref_tag & 0x7FFF)
                    if cname == 'CVertex':
                        return 'CEdge'
                elif 0 < vref_tag <= self.arc.map_count:
                    if isinstance(self.arc.get_object(vref_tag), Vertex):
                        return 'CEdge'

        # Check CVertex: base_skip(2) + 3 doubles(24) = 26 bytes
        # Require at least one coordinate to have reasonable magnitude (> 0.001)
        # to avoid false positives from denormalized floats
        if remaining >= 26 and self.model.version_major >= 4:
            skip_bytes = struct.unpack_from('<H', data, pos)[0]
            if skip_bytes == 0x0000:
                try:
                    vals = struct.unpack_from('<ddd', data, pos + 2)
                    if (all(abs(v) < 1e6 and not (v != v) for v in vals) and
                            any(abs(v) > 0.001 for v in vals)):
                        after = pos + 26
                        if after + 2 <= r.size:
                            next_tag = struct.unpack_from('<H', data, after)[0]
                            if (next_tag == 0 or next_tag == 0xFFFF or
                                (next_tag >= 0x8000 and (next_tag & 0x7FFF) <= self.arc.map_count + 50) or
                                (0 < next_tag <= self.arc.map_count)):
                                return 'CVertex'
                except (struct.error, ValueError):
                    pass

        # Check CComponentInstance: base + def_ref(2) + transform(13 doubles)
        # Transform rotation rows have magnitude ~1.0, scale ~1.0
        ci_base = 12 if self.model.version_major >= 5 else (11 if self.model.version_major == 4 else 9)
        if self.model.version_major >= 3 and remaining >= ci_base + 2 + 104:
            ci_pos = pos
            ci_def = struct.unpack_from('<H', data, ci_pos + ci_base)[0]
            # def_ref should be a known object (small index)
            if 0 < ci_def <= self.arc.map_count + 200:
                try:
                    xf = struct.unpack_from('<13d', data, ci_pos + ci_base + 2)
                    if all(math.isfinite(v) for v in xf):
                        x_m = math.sqrt(xf[0]**2 + xf[1]**2 + xf[2]**2)
                        y_m = math.sqrt(xf[3]**2 + xf[4]**2 + xf[5]**2)
                        z_m = math.sqrt(xf[6]**2 + xf[7]**2 + xf[8]**2)
                        if (abs(x_m - 1.0) < 0.05 and abs(y_m - 1.0) < 0.05 and
                                abs(z_m - 1.0) < 0.05 and abs(xf[12] - 1.0) < 0.05 and
                                all(math.isfinite(v) and abs(v) < 1e6 for v in xf[9:12])):
                            return 'CComponentInstance'
                except (struct.error, ValueError, OverflowError):
                    pass

        # Check CLoop: 4 bytes of data for v4+, then a known valid tag
        # Only if we already have geometry classes registered
        if self.model.version_major >= 4 and remaining >= 6:
            has_geo = (self.arc.find_class_idx('CEdge') is not None or
                       self.arc.find_class_idx('CEdgeUse') is not None or
                       self.arc.find_class_idx('CFace') is not None)
            if has_geo:
                after_loop = pos + 4
                if after_loop + 2 <= r.size:
                    next_tag = struct.unpack_from('<H', data, after_loop)[0]
                    if next_tag == 0xFFFF or (next_tag >= 0x8000 and
                        (next_tag & 0x7FFF) in self.arc.class_map):
                        return 'CLoop'

        return None

    def _fill_map_gap(self, class_idx, class_name):
        """Fill map_count gap up to class_idx and register the class there.
        Also detects consistent offset between writer's and our class indices,
        and pre-registers all known classes at offset-adjusted indices."""
        old_count = self.arc.map_count

        # Detect class offset: if we already know this class at a different index,
        # the difference is the offset between writer's and our MFC maps
        if self._class_offset == 0:
            existing_idx = self.arc.find_class_idx(class_name)
            if existing_idx is not None and existing_idx != class_idx:
                self._class_offset = class_idx - existing_idx
                self.log(f"Detected MFC class offset: {self._class_offset}")
                # Pre-register ALL known classes at offset-adjusted indices
                for idx, name in list(self.arc.class_map.items()):
                    new_idx = idx + self._class_offset
                    if new_idx not in self.arc.class_map:
                        self.arc.class_map[new_idx] = name

        while self.arc.map_count < class_idx - 1:
            self.arc.register_object({'type': 'gap_fill'})
        self.arc.class_map[class_idx] = class_name
        # Ensure map_count is at least class_idx
        while self.arc.map_count < class_idx:
            self.arc.next_map_idx()
        self.log(f"Identified class@{class_idx} as {class_name} (filled {class_idx - old_count} gap entries)")

    def _find_face_base(self, r, base_size, scan_limit):
        """Scan forward to find a valid face entity base + normal pattern.
        Returns the position of the entity base, or -1 if not found."""
        for off in range(r.tell(), min(scan_limit, r.size - base_size - 32)):
            nx = struct.unpack_from('<d', r.data, off + base_size)[0]
            ny = struct.unpack_from('<d', r.data, off + base_size + 8)[0]
            nz = struct.unpack_from('<d', r.data, off + base_size + 16)[0]
            mag_sq = nx * nx + ny * ny + nz * nz
            if 0.95 < mag_sq < 1.05:
                dist = struct.unpack_from('<d', r.data, off + base_size + 24)[0]
                loop_count = struct.unpack_from('<I', r.data, off + base_size + 32)[0]
                if 0 < loop_count <= 100 and abs(dist) < 1e8:
                    return off
        return -1

    def _register_skipped_classes(self, r, start, end):
        """Scan a skipped region and register any FFFF class intros found.
        This keeps the MFC class map synchronized even when data is skipped."""
        for i in range(start, min(end, r.size - 6)):
            if r.data[i] == 0xFF and r.data[i + 1] == 0xFF:
                schema = struct.unpack_from('<H', r.data, i + 2)[0]
                nlen = struct.unpack_from('<H', r.data, i + 4)[0]
                if 1 <= nlen <= 30 and i + 6 + nlen <= r.size:
                    try:
                        cn = r.data[i + 6:i + 6 + nlen].decode('ascii')
                        if cn and cn[0] == 'C' and cn.isalnum():
                            # Register this class (and a placeholder object)
                            cls_idx = self.arc.register_class(cn)
                            obj_idx = self.arc.register_object({'type': cn, 'skipped': True})
                            self.log(f"Registered skipped class {cn} as class@{cls_idx} obj@{obj_idx}")
                    except (UnicodeDecodeError, IndexError):
                        pass

    def _read_v1_layer_ref(self, r):
        """Read a v1/v2 MFC layer reference (u16 tag) from the entity base.
        v1 entity base format: entity_id(u32) + flags(u8) + layer_ref(MFC u16).
        The layer_ref is an MFC object tag:
          0x0000 = NULL (no layer)
          < 0x8000 = object back-ref to existing CLayer
          >= 0x8000 = class back-ref, creates new CLayer inline + Serialize data
        Returns the layer object map index (0 if NULL)."""
        tag = r.u16()
        if tag == 0x0000:
            return 0
        if tag >= 0x8000:
            class_idx = tag & 0x7FFF
            class_name = self.arc.class_map.get(class_idx)
            if class_name == 'CLayer':
                # New CLayer object created inline
                obj_idx = self.arc.register_object(None)
                # CLayer::Serialize() data:
                # v1 (schema=0): name + null(1) + RGBA(4) + flags(u16)
                # v2 (schema=1): name + null(1) + display(astring) + null(1) + u8 + RGBA(4) + flags(u16)
                lname = self._read_string(r)
                r.u8()  # null separator
                if self.model.version_major >= 2:
                    self._read_string(r)  # display_name
                    r.u8()       # null separator
                    r.u8()       # visibility flag
                r.read(4)  # color RGBA
                if self._uses_wstring and self.model.version_major < 3:
                    self._read_string(r)  # folder_name (wstring v2)
                    r.skip(8)    # 8 zero bytes
                else:
                    r.u16()  # flags
                layer = {'name': lname, 'map_idx': obj_idx}
                self.arc.set_object(obj_idx, layer)
                self.log(f"Inline CLayer '{lname}' obj@{obj_idx}")
                return obj_idx
            else:
                # Unknown class back-ref in layer position - register to keep count
                obj_idx = self.arc.register_object(None)
                self.log(f"Inline layer class@{class_idx} ({class_name}) obj@{obj_idx}")
                return obj_idx
        # Object back-ref (1 to 0x7FFF) - reference to existing layer
        return tag

    def _read_entity_base(self, r):
        """Read version-dependent entity base. Returns (entity_id, flags, layer_ref, mat_ref, back_mat_ref).
        Note: v5+ format for faces is back_mat(u16) + mat_ref(u16) + flags(u32) + layer(u16) + extra(u16).
        This is only called from _parse_face and _parse_edge_inline (v3 path)."""
        back_mat_ref = 0
        if self.model.version_major >= 5:
            back_mat_ref = r.u16()
            mat_ref = r.u16()
            flags = r.read(4)
            layer_ref = r.u16()
            r.u16()  # extra/padding
            entity_id = 0
        elif self.model.version_major == 4:
            back_mat_ref = r.u16()  # back material (usually 0)
            mat_ref = r.u16()       # front material reference
            flags = r.read(4)
            layer_ref = r.u16()
            r.u8()
            entity_id = 0
        elif self.model.version_major >= 3:
            mat_ref = r.u16()
            r.u16()  # upper entity_id / flags
            flags = r.read(2)
            layer_ref = r.u16()
            r.u8()
            entity_id = 0
        else:
            # v1-v2: entity_id(u32) + flags(u8) + layer_ref(MFC u16) = 7 bytes
            entity_id = r.u32()
            flags = r.read(1)
            layer_ref = self._read_v1_layer_ref(r)
            mat_ref = 0
        return entity_id, flags, layer_ref, mat_ref, back_mat_ref

    def _try_extract_tagless_face(self, r, scan_start, skipped):
        """Try to find a tagless face entity base in data we just skipped.

        In v7 files, faces inside CComponentDefinitions may not have class
        tags. They appear as: entity_base(12) + normal(3*f64) + distance(f64)
        + loop_count(u32) immediately before a CLoop class tag.
        """
        import math
        data = r.data
        cur_pos = r.tell()  # Position of the next tag (likely CLoop)

        # Try offsets: face data is 48 bytes, with 0-4 bytes padding before CLoop
        for pad in range(0, 8, 2):
            fpos = cur_pos - 48 - pad
            if fpos < scan_start:
                continue
            if fpos + 48 > len(data):
                continue
            # Read potential normal at fpos+12 (3 doubles)
            try:
                nx = struct.unpack_from('<d', data, fpos + 12)[0]
                ny = struct.unpack_from('<d', data, fpos + 20)[0]
                nz = struct.unpack_from('<d', data, fpos + 28)[0]
                mag_sq = nx * nx + ny * ny + nz * nz
                if not (0.95 < mag_sq < 1.05):
                    continue
                dist = struct.unpack_from('<d', data, fpos + 36)[0]
                lc = struct.unpack_from('<I', data, fpos + 44)[0]
                if not (0 < lc <= 20):
                    continue
                # Valid face found! Parse entity base
                eb = data[fpos:fpos + 12]
                # v5+ CFace entity base: back_mat(u16) + front_mat(u16) + flags(4) + layer(u16) + extra(u16)
                front_mat = struct.unpack_from('<H', data, fpos + 2)[0]
                # Create face - use a synthetic object index
                fidx = self.arc.register_object(None)
                face = Face((nx, ny, nz), dist, map_idx=fidx,
                           scope=self.current_scope)
                # Check material
                if front_mat > 0:
                    mat = self.arc.get_object(front_mat)
                    if isinstance(mat, Material):
                        try:
                            face.material_idx = self.model.materials.index(mat)
                        except ValueError:
                            pass
                self.model.faces.append(face)
                self.arc.set_object(fidx, face)
                self._last_parsed_face = face
                self._has_tagless_faces = True
                self.log(f"Face[{fidx}]: tagless face at 0x{fpos:x} "
                        f"N=({nx:.3f},{ny:.3f},{nz:.3f}) loops={lc}")
                return
            except (struct.error, IndexError):
                continue

    def _check_face_before_loop(self, r, loop_tag_pos):
        """Check if there's a tagless face entity base before a CLoop tag.

        Called before each CLoop parse. Looks backward from the CLoop class tag
        position for face data: entity_base(12) + normal(24) + distance(8) +
        loop_count(4) = 48 bytes, with 0-4 bytes padding.
        Only active for v5+ files with existing geometry.
        """
        if not self._has_tagless_faces:
            return
        if self.model.version_major < 5 or not self.in_geometry:
            return
        if not self.model.faces:
            return
        data = r.data
        for pad in range(0, 8, 2):
            fpos = loop_tag_pos - 48 - pad
            if fpos < 0:
                continue
            try:
                nx = struct.unpack_from('<d', data, fpos + 12)[0]
                ny = struct.unpack_from('<d', data, fpos + 20)[0]
                nz = struct.unpack_from('<d', data, fpos + 28)[0]
                mag_sq = nx * nx + ny * ny + nz * nz
                if not (0.95 < mag_sq < 1.05):
                    continue
                lc = struct.unpack_from('<I', data, fpos + 44)[0]
                if not (0 < lc <= 20):
                    continue
                dist = struct.unpack_from('<d', data, fpos + 36)[0]
                # Verify this isn't a face we already parsed at this position
                already_exists = any(
                    hasattr(f, '_tagless_pos') and f._tagless_pos == fpos
                    for f in self.model.faces[-5:])
                if already_exists:
                    return
                front_mat = struct.unpack_from('<H', data, fpos + 2)[0]
                fidx = self.arc.register_object(None)
                face = Face((nx, ny, nz), dist, map_idx=fidx,
                           scope=self.current_scope)
                face._tagless_pos = fpos
                if front_mat > 0:
                    mat = self.arc.get_object(front_mat)
                    if isinstance(mat, Material):
                        try:
                            face.material_idx = self.model.materials.index(mat)
                        except ValueError:
                            pass
                self.model.faces.append(face)
                self.arc.set_object(fidx, face)
                self._last_parsed_face = face
                self.log(f"Face[{fidx}]: pre-loop face at 0x{fpos:x} "
                        f"N=({nx:.3f},{ny:.3f},{nz:.3f}) loops={lc}")
                return
            except (struct.error, IndexError):
                continue

    def _parse_face(self, idx):
        """Parse CFace: version-dependent base + normal(3d) + distance(d) + loop_count + loops."""
        r = self.arc.r

        if self.model.version_major >= 5:
            base_size = 12
        elif self.model.version_major == 4:
            base_size = 11
        elif self.model.version_major >= 3:
            base_size = 9
        else:
            base_size = 7

        save_pos = r.tell()

        # v6+: face may start with inline CAttributeContainer + CFaceTextureCoords
        # (FFFF at entity base position). Skip these to reach the real entity base.
        has_texture_coords = False
        if self.model.version_major >= 6 and r.peek_u16() == 0xFFFF:
            tc_save = r.tell()
            try:
                name, is_new, ac_idx = self.arc.read_object_tag()
                if name == 'CAttributeContainer':
                    r.u16()  # AC null data
                    name2, is_new2, ftxc_idx = self.arc.read_object_tag()
                    if name2 == 'CFaceTextureCoords':
                        r.skip(154)  # FTXC data (6 prefix + 72 front + 72 back + 4 trailing)
                        has_texture_coords = True
                        self.log(f"Face[{idx}]: skipped CAttributeContainer+"
                                 f"CFaceTextureCoords ({r.tell()-tc_save}B)")
                        save_pos = r.tell()
                    else:
                        r.seek(tc_save)
                else:
                    r.seek(tc_save)
            except Exception:
                r.seek(tc_save)

        # v5+ face data starts with entity base immediately (no inline objects before it).
        # Read entity base + normal directly.
        entity_id, flags, layer_ref, mat_ref, back_mat_ref = self._read_entity_base(r)
        nx, ny, nz = r.f64(), r.f64(), r.f64()
        dist = r.f64()
        mag_sq = nx * nx + ny * ny + nz * nz
        loop_count = r.u32()

        if not (0.95 < mag_sq < 1.05 and 0 < loop_count <= 100):
            # Entity base not at expected position - scan from save_pos
            r.seek(save_pos)
            found_pos = self._find_face_base(r, base_size, save_pos + 512)
            if found_pos >= 0:
                # Parse inline CLoop + CEdgeUse data for the previous face
                self._parse_inline_loop_edgeuses(r, save_pos, found_pos)
                skipped = found_pos - save_pos
                self.log(f"Face[{idx}]: parsed {skipped} bytes of inline loop/EU data at {hex(save_pos)}")
                r.seek(found_pos)
                entity_id, flags, layer_ref, mat_ref, back_mat_ref = self._read_entity_base(r)
                nx, ny, nz = r.f64(), r.f64(), r.f64()
                dist = r.f64()
                loop_count = r.u32()
            else:
                self.log(f"Face[{idx}]: could not find valid entity base, skipping")
                r.seek(save_pos)
                self.arc.set_object(idx, {'type': 'CFace', 'invalid': True})
                return

        face = Face((nx, ny, nz), dist, map_idx=idx, scope=self.current_scope)
        face.loop_count = loop_count
        face.has_texture_coords = has_texture_coords

        # Check for front material ref
        if mat_ref > 0:
            mat = self.arc.get_object(mat_ref)
            if isinstance(mat, Material):
                try:
                    face.material_idx = self.model.materials.index(mat)
                except ValueError:
                    pass

        # Check for back material ref
        if back_mat_ref > 0:
            back_mat = self.arc.get_object(back_mat_ref)
            if isinstance(back_mat, Material):
                try:
                    back_idx = self.model.materials.index(back_mat)
                    face.back_material_idx = back_idx
                    # Prefer transparent back material over opaque front
                    # (e.g., glass lens has Safety Glass on back side)
                    if (face.material_idx >= 0 and
                            back_mat.opacity < 1.0 and
                            self.model.materials[face.material_idx].opacity >= 1.0):
                        face.material_idx = back_idx
                        self.log(f"Face[{idx}]: using transparent back "
                                f"material '{back_mat.name}'")
                    elif face.material_idx < 0:
                        face.material_idx = back_idx
                except ValueError:
                    pass

        self.model.faces.append(face)
        self.arc.set_object(idx, face)
        # Track last parsed face for loop-to-face association
        self._last_parsed_face = face

        self.log(f"Face[{idx}]: normal=({nx:.3f},{ny:.3f},{nz:.3f}) loops={loop_count}")

    def _parse_loop_header(self, idx):
        """Parse CLoop header: version-dependent size.
        For v1/v2 files with implicit faces, also consumes the face plane
        data that follows the CLoop header (3 prefix + 32 plane + 4 loop_count
        = 39-41 bytes)."""
        r = self.arc.r
        if self.model.version_major >= 4:
            r.skip(4)  # v4+: 4 bytes (flags/winding)
        else:
            r.skip(2)  # v1-v3: 2 bytes

        # For v4/v5: check if implicit face data follows (36 bytes:
        # normal(24) + distance(8) + loop_count(4), no entity_base prefix).
        # The face data appears after the CLoop header and BEFORE the
        # CEdgeUse entries for this face. Validate by checking that the
        # next tag after 36 bytes is a CEdgeUse (the face's EU chain).
        if (self.model.version_major in (4, 5) and r.remaining() >= 38 and
                self.in_geometry):
            save = r.tell()
            try:
                nx = struct.unpack_from('<d', r.data, save)[0]
                ny = struct.unpack_from('<d', r.data, save + 8)[0]
                nz = struct.unpack_from('<d', r.data, save + 16)[0]
                dist = struct.unpack_from('<d', r.data, save + 24)[0]
                mag_sq = nx * nx + ny * ny + nz * nz
                lc = struct.unpack_from('<I', r.data, save + 32)[0]
                if 0.95 < mag_sq < 1.05 and 0 < lc <= 100:
                    # Validate: next u16 must be a CEdgeUse class tag
                    next_tag = struct.unpack_from('<H', r.data, save + 36)[0]
                    if next_tag >= 0x8000:
                        nci = next_tag & 0x7FFF
                        ncn = self.arc.class_map.get(nci, '')
                        if ncn == 'CEdgeUse':
                            r.seek(save + 36)
                            fidx = self.arc.register_object(None)
                            face = Face((nx, ny, nz), dist, map_idx=fidx,
                                        scope=self.current_scope)
                            face.loop_count = lc
                            self.model.faces.append(face)
                            self.arc.set_object(fidx, face)
                            self._last_parsed_face = face
                            self._loop_to_face[idx] = face
                            self.arc.set_object(idx,
                                {'type': 'CLoop', 'map_idx': idx})
                            return
            except Exception:
                pass

        # For v6+: check if implicit face data follows (44 bytes:
        # prefix(8) + normal(24) + distance(8) + loop_count(4)).
        if (self.model.version_major >= 6 and r.remaining() >= 44 and
                self.in_geometry):
            save = r.tell()
            try:
                nx = struct.unpack_from('<d', r.data, save + 8)[0]
                ny = struct.unpack_from('<d', r.data, save + 16)[0]
                nz = struct.unpack_from('<d', r.data, save + 24)[0]
                dist = struct.unpack_from('<d', r.data, save + 32)[0]
                mag_sq = nx * nx + ny * ny + nz * nz
                lc = struct.unpack_from('<I', r.data, save + 40)[0]
                if 0.95 < mag_sq < 1.05 and 0 < lc <= 100:
                    r.seek(save + 44)  # consume face data
                    fidx = self.arc.register_object(None)
                    face = Face((nx, ny, nz), dist, map_idx=fidx,
                                scope=self.current_scope)
                    face.loop_count = lc
                    self.model.faces.append(face)
                    self.arc.set_object(fidx, face)
                    self._last_parsed_face = face
                    self._loop_to_face[idx] = face
                    self.arc.set_object(idx, {'type': 'CLoop', 'map_idx': idx})
                    return
            except Exception:
                pass

        # For v1/v2: check if implicit face data follows the CLoop header.
        # After CLoop data, there may be a 00 00 NULL (consumed by entity loop),
        # then face plane data: prefix(3) + normal(3*f64) + distance(f64) +
        # loop_count(u32) = 39 bytes. We need to scan ahead for this pattern.
        if (self.model.version_major < 3 and r.remaining() >= 41 and
                self.in_geometry):
            save = r.tell()
            try:
                # Skip up to 4 bytes of NULL/padding to find face prefix
                for skip_nulls in range(0, 5):
                    test_pos = save + skip_nulls
                    if test_pos + 39 > r.size:
                        break
                    # Read face data at this offset
                    nx = struct.unpack_from('<d', r.data, test_pos + 3)[0]
                    ny = struct.unpack_from('<d', r.data, test_pos + 11)[0]
                    nz = struct.unpack_from('<d', r.data, test_pos + 19)[0]
                    dist = struct.unpack_from('<d', r.data, test_pos + 27)[0]
                    mag_sq = nx * nx + ny * ny + nz * nz
                    lc = struct.unpack_from('<I', r.data, test_pos + 35)[0]
                    if 0.95 < mag_sq < 1.05 and 0 < lc <= 100:
                        # Valid face plane: create implicit Face
                        r.seek(test_pos + 39)  # consume face data
                        fidx = self.arc.register_object(None)
                        face = Face((nx, ny, nz), dist, map_idx=fidx,
                                    scope=self.current_scope)
                        face.loop_count = lc
                        self.model.faces.append(face)
                        self.arc.set_object(fidx, face)
                        self._last_parsed_face = face
                        self._loop_to_face[idx] = face
                        self.arc.set_object(idx, {'type': 'CLoop', 'map_idx': idx})
                        self.log(f"Implicit face for Loop[{idx}] at {hex(test_pos)}: "
                                 f"n=({nx:.3f},{ny:.3f},{nz:.3f}) d={dist:.3f}")
                        return
            except Exception:
                pass
            r.seek(save)

        # Associate this loop with the most recently parsed face
        if hasattr(self, '_last_parsed_face') and self._last_parsed_face:
            self._loop_to_face[idx] = self._last_parsed_face
        self.arc.set_object(idx, {'type': 'CLoop', 'map_idx': idx})

    def _parse_inline_loop_edgeuses(self, r, start, end):
        """Parse inline CLoop + CEdgeUse data found between face INST tags.

        In v5+ files, the entity stream interleaves face data with their
        CLoop/CEdgeUse children. When _parse_face encounters data that isn't
        a face entity base, it's CLoop+CEdgeUse data for the previous face.

        Format: CLoop_header(4 bytes) + repeated CEdgeUse entries, each:
          class_tag(u16) + null_ref(u16) + edge_ref(u16/MFC) + reversed(u8) + loop_ref(u16)
        Terminated by 0x0000 0x0000 (4 null bytes).
        """
        if self.model.version_major < 4:
            return
        if not hasattr(self, '_last_parsed_face') or not self._last_parsed_face:
            return
        prev_face = self._last_parsed_face

        save = r.tell()
        r.seek(start)

        try:
            # Parse CLoop header (4 bytes for v4+)
            if start + 4 > end:
                return
            loop_data = r.read(4)
            loop_idx = self.arc.register_object({'type': 'CLoop', 'map_idx': -1})
            self._loop_to_face[loop_idx] = prev_face

            # Parse CEdgeUse entries until we hit terminator or reach end
            eu_count = 0
            while r.tell() < end - 4:
                pos = r.tell()

                # Check for terminator: 4 null bytes
                peek4 = struct.unpack_from('<I', r.data, pos)[0]
                if peek4 == 0:
                    break

                # Read class tag for CEdgeUse
                eu_tag = r.u16()

                if eu_tag < 0x8000 and eu_tag > 0:
                    # Object backref - this might be an edge ref within an EU
                    # Actually this shouldn't happen at EU start; likely misaligned
                    break

                if eu_tag >= 0x8000:
                    # Class backref - register as CEdgeUse if not already known
                    eu_ci = eu_tag & 0x7FFF
                    if eu_ci not in self.arc.class_map:
                        self.arc.class_map[eu_ci] = 'CEdgeUse'
                    elif self.arc.class_map.get(eu_ci) not in ('CEdgeUse', 'CFace'):
                        break  # Wrong class type, stop parsing

                # Read null_ref
                null_ref = r.u16()

                # Read edge_ref (MFC ref)
                edge_ref = self._read_mfc_ref_inline(r, 'CEdge')

                # Read reversed flag
                reversed_flag = r.u8()

                # Read loop_ref
                loop_ref = r.u16()

                eu_idx = self.arc.register_object(None)
                eu_data = {
                    'type': 'CEdgeUse',
                    'edge_ref': edge_ref,
                    'reversed': reversed_flag,
                    'loop_ref': loop_ref,
                    'map_idx': eu_idx
                }
                self.arc.set_object(eu_idx, eu_data)

                if not hasattr(self, '_edgeuse_chains'):
                    self._edgeuse_chains = {}
                self._edgeuse_chains[eu_idx] = eu_data

                # Associate with previous face
                prev_face._edge_uses.append(eu_data)
                eu_count += 1

            if eu_count > 0:
                self.log(f"Parsed {eu_count} inline CEdgeUses for face "
                        f"(scope={prev_face.scope})")

        except (struct.error, IndexError):
            pass
        finally:
            r.seek(end)

    def _parse_edgeuse(self, idx):
        """Parse CEdgeUse.

        v3 format: edge_ref(MFC) + reversed(u8) + loop_ref(MFC) + next_in_loop_ref(MFC)
        v4+: null_ref(u16) + edge_ref(MFC) + reversed(u8) + loop_ref(u16)

        For v3, CEdgeUse forms a singly-linked list via next_in_loop_ref.
        Each edge_ref can be a NEW CEdge with inline vertices.
        """
        r = self.arc.r
        if self.model.version_major >= 4:
            # v5+ CEdgeUse: null_ref(MFC) + edge_ref(MFC) + reversed(u8) + loop_ref(MFC)
            # edge_ref can be object backref (existing edge) or class backref (inline CEdge)
            eu_data = self._parse_edgeuse_v5(idx)
            self.arc.set_object(idx, eu_data)
            return

        # v3 (and likely v1-v2): parse the full CEdgeUse chain
        eu_data = self._parse_edgeuse_v3(idx)
        self.arc.set_object(idx, eu_data)

        # v1-v2: after the chain loop closes, consume trailing edge/vertex index
        # lists.  The EU chain's directed edges already give correct polygon
        # winding, so these lists are consumed for stream alignment but NOT
        # used for face reconstruction.
        if self.model.version_major < 3:
            self._consume_eu_trailing_data(r)
        elif self.model.version_major in (3, 4):
            # v3/v4: trailing data after EU chain starts with back_mat u16.
            # If non-zero and resolves to a Material, assign to face.
            self._read_v3_back_material(r)

    def _parse_edgeuse_v5(self, idx):
        """Parse a v5+ CEdgeUse: null_ref + edge_ref + reversed + loop_ref.

        The edge_ref can be an object backref to an existing CEdge, or a class
        backref that creates a new CEdge inline (with inline CVertex objects).
        """
        r = self.arc.r

        # Field 1: null_ref (MFC ref, usually NULL for twin/partner edge use)
        null_ref_tag = r.u16()

        # Field 2: edge_ref (MFC ref - object backref or class backref with inline CEdge)
        edge_ref = self._read_mfc_ref_inline(r, 'CEdge')

        # Field 3: reversed flag (u8)
        reversed_flag = r.u8()

        # Field 4: loop_ref (MFC ref)
        loop_ref_tag = r.u16()

        eu_data = {
            'type': 'CEdgeUse',
            'edge_ref': edge_ref,
            'reversed': reversed_flag,
            'loop_ref': loop_ref_tag,
            'map_idx': idx
        }

        # Store for face reconstruction
        if not hasattr(self, '_edgeuse_chains'):
            self._edgeuse_chains = {}
        self._edgeuse_chains[idx] = eu_data

        # Associate with the most recently parsed face (sequential association)
        if hasattr(self, '_last_parsed_face') and self._last_parsed_face:
            self._last_parsed_face._edge_uses.append(eu_data)

        return eu_data

    def _parse_edgeuse_v3(self, idx, depth=0):
        """Parse a v3 CEdgeUse and recursively parse the chain.

        v3 CEdgeUse format: edge_ref(MFC) + reversed(u8) + loop_ref(MFC) + next_ref(MFC)
        The edge_ref can be an inline CEdge (class backref) which includes a trailing
        curve/partner MFC reference consumed by _parse_edge_inline.

        When the edge_ref's curve_ref introduces a new class (FFFF, e.g. CArcCurve),
        the unconsumed arc data follows; peek detects this (byte > 1) and skips r/l/n.
        """
        r = self.arc.r

        # Field 1: edge_ref (MFC object reference)
        edge_ref = self._read_mfc_ref_inline(r, 'CEdge')

        # Fields 2-4: reversed + loop_ref + next_ref
        # Peek at next byte to detect presence: reversed is always 0 or 1.
        # When edge_ref triggered an inline CArcCurve (FFFF), unconsumed arc
        # data follows and the peek byte will be > 1.
        reversed_flag = 0
        loop_ref = None
        next_eu_ref = None
        if r.remaining() >= 1 and r.data[r.tell()] <= 1:
            # Field 2: reversed flag (u8)
            reversed_flag = r.u8()

            # Field 3: loop_ref (MFC object reference)
            loop_ref = self._read_mfc_ref_inline(r, 'CLoop')

            # Field 4: next_in_loop_ref (MFC object reference)
            next_eu_ref = self._read_mfc_ref_inline(r, 'CEdgeUse')

        eu_data = {
            'type': 'CEdgeUse',
            'edge_ref': edge_ref,
            'reversed': reversed_flag,
            'loop_ref': loop_ref,
            'next_ref': next_eu_ref,
            'map_idx': idx
        }

        # Store edge-use connectivity for face reconstruction
        if not hasattr(self, '_edgeuse_chains'):
            self._edgeuse_chains = {}
        self._edgeuse_chains[idx] = eu_data

        return eu_data

    def _consume_eu_trailing_data(self, r):
        """Consume v1/v2 trailing EU/edge index lists after a CEdgeUse chain.

        Format: N u16 EU-index refs (winding order) + optional 4-byte
        separator (0x0000 0x0000) + M u16 edge refs.  The EU chain's
        directed edges already provide correct polygon winding, so these
        lists are consumed only for stream alignment.
        """
        # Consume EU index list until separator (0x0000) or next entity tag
        while r.remaining() >= 2:
            val = r.peek_u16()
            if val == 0:
                break
            if val >= 0x8000 or val == 0xFFFF:
                return  # Next entity tag — no trailing data
            r.u16()

        if r.remaining() < 4:
            return

        # Consume separator (two u16 NULLs)
        sep1 = r.u16()
        sep2 = r.u16()
        if sep1 != 0 or sep2 != 0:
            r.seek(r.tell() - 4)
            return

        # Consume edge/vertex ref list until next entity tag
        while r.remaining() >= 2:
            val = r.peek_u16()
            if val >= 0x8000 or val == 0xFFFF:
                break
            if val == 0:
                r.u16()
                continue
            # Stop on values too large to be valid MFC refs
            if val > self.arc.map_count + 100:
                break
            r.u16()

    def _read_v3_back_material(self, r):
        """Read the back material u16 from v3/v4 CEdgeUse trailing data.

        After a face's EU chain, the stream contains: back_mat(u16) +
        optional edge/vertex object refs.  If back_mat is non-zero and
        resolves to a Material, assign it to the face (only when the face
        has no front material, to avoid overriding explicit assignments).
        """
        if r.remaining() < 2:
            return
        val = r.peek_u16()
        if val == 0:
            r.u16()  # consume null (no back material)
            return
        if val >= 0x8000 or val == 0xFFFF:
            return  # next entity tag — no trailing data
        # Check if this is a material reference
        obj = self.arc.get_object(val)
        if isinstance(obj, Material):
            r.u16()  # consume
            if hasattr(self, '_last_parsed_face') and self._last_parsed_face:
                face = self._last_parsed_face
                try:
                    mat_idx = self.model.materials.index(obj)
                    face.back_material_idx = mat_idx
                    if face.material_idx < 0:
                        face.material_idx = mat_idx
                        self.log(f"Back material '{obj.name}' assigned "
                                f"to face from trailing ref")
                    elif (obj.opacity < 1.0 and
                          self.model.materials[face.material_idx].opacity >= 1.0):
                        face.material_idx = mat_idx
                        self.log(f"Transparent back material '{obj.name}' "
                                f"preferred over opaque front")
                except ValueError:
                    pass

    def _read_mfc_ref_inline(self, r, expected_class):
        """Read an MFC object reference during CEdgeUse parsing.

        Handles: NULL (0), backref (<0x8000), class INST (>=0x8000), new class (0xFFFF).
        For INST/new, parses the object inline.
        Returns the object's map index, or None for NULL.
        """
        tag = r.u16()

        if tag == 0x0000:
            return None

        if tag < 0x8000:
            # Object back-reference
            return tag

        if tag == 0xFFFF:
            # New class introduction
            r.seek(r.tell() - 2)  # Back up to FFFF
            name, is_new, oidx = self.arc.read_object_tag()
            self._parse_inline_object(name, oidx)
            return oidx

        # Class back-ref (>= 0x8000)
        ci = tag & 0x7FFF
        cname = self.arc.class_map.get(ci)

        # Use expected_class hint when class is unknown OR misidentified due
        # to MFC class offset drift. E.g., writer has CEdge at class@16 but
        # our map says CVertex at class@16 due to different counter progression.
        if expected_class and cname != expected_class:
            if cname is None:
                self.arc.class_map[ci] = expected_class
                cname = expected_class
            elif self._class_offset > 0:
                # Class offset drift: the writer's class index for expected_class
                # collides with our class index for a different class.
                # Check if data looks like expected_class (e.g., 12-byte entity base for CEdge)
                if expected_class == 'CEdge' and cname == 'CVertex':
                    # CEdge has 12-byte entity base with flags pattern; CVertex has 2+24 bytes
                    # Peek at data: CEdge entity base has flags at bytes 4-7
                    peek_pos = self.arc.r.tell()
                    if self.arc.r.remaining() >= 12:
                        peek = self.arc.r.data[peek_pos:peek_pos+8]
                        # CEdge flags pattern: bytes 4-7 typically have 00/01 values
                        flags = peek[4:8]
                        if all(b <= 1 for b in flags):
                            cname = expected_class

        oidx = self.arc.register_object({'type': cname or f'unknown@{ci}'})
        self._parse_inline_object(cname, oidx)
        return oidx

    def _parse_inline_object(self, name, oidx):
        """Parse an inline object created within CEdgeUse data."""
        if name == 'CEdge':
            self._parse_edge_inline(oidx)
        elif name == 'CVertex':
            self._parse_vertex(oidx)
        elif name == 'CLoop':
            self._parse_loop_header(oidx)
        elif name == 'CEdgeUse':
            if self.model.version_major >= 5:
                eu = self._parse_edgeuse_v5(oidx)
                self.arc.set_object(oidx, eu)
            else:
                eu = self._parse_edgeuse_v3(oidx)
                self.arc.set_object(oidx, eu)
        elif name == 'CArcCurve':
            if self.model.version_major <= 4:
                self._parse_arccurve_inline(oidx)
            else:
                # v5+ CArcCurve INST: 7 prefix bytes + 14 f64 arc params = 119 bytes
                # prefix: u16(0) + u8(flag) + u32(edge_count)
                # params: center(3) + normal(3) + xaxis(3) + yaxis(3) + radius + angle
                r = self.arc.r
                consumed = False
                if r.remaining() >= 119:
                    pos = r.tell()
                    arc_start = pos + 7
                    if arc_start + 112 <= len(r.data):
                        # Validate: normal vector at offset +24 from arc params should be unit length
                        d3 = struct.unpack_from('<d', r.data, arc_start + 24)[0]
                        d4 = struct.unpack_from('<d', r.data, arc_start + 32)[0]
                        d5 = struct.unpack_from('<d', r.data, arc_start + 40)[0]
                        nmag = d3*d3 + d4*d4 + d5*d5
                        if 0.99 < nmag < 1.01:
                            edge_count = struct.unpack_from('<I', r.data, pos + 3)[0]
                            r.skip(119)
                            self.arc.set_object(oidx, {'type': 'CArcCurve', 'edge_count': edge_count})
                            consumed = True
                if not consumed:
                    self.arc.set_object(oidx, {'type': 'CArcCurve'})
        elif name:
            self.arc.set_object(oidx, {'type': name})

    def _parse_arccurve_inline(self, idx):
        """Parse CArcCurve inline data: N inline CEdge objects + 117 bytes arc params.

        CArcCurve is a CEdge subclass representing an arc. Its serialized data
        contains the individual straight-edge segments approximating the arc
        (each as an inline CEdge with entity_base + sv + ev + curve_ref back
        to this arc), followed by 117 bytes of arc parameters:
          5 prefix bytes (00 + u32 edge_count_hint) + 14 f64 values
          (center(3) + normal(3) + xaxis(3) + yaxis(3) + radius + angle).
        """
        r = self.arc.r

        # v4 has a 2-byte NULL prefix + 2-byte edge backref before inline CEdge backrefs
        # The edge backref points to the arc's parent edge (the first chord edge).
        if self.model.version_major == 4 and r.remaining() >= 4:
            if r.peek_u16() == 0:
                r.skip(2)  # null prefix
                tag = r.u16()
                if tag >= 0x8000:
                    # Not an edge backref - back up and let the CEdge loop handle it
                    r.seek(r.tell() - 2)
                # else: consumed the edge backref (object backref < 0x8000)

        # Read inline CEdge objects (class backrefs >= 0x8000)
        edge_count = 0
        while r.remaining() >= 2:
            peek = struct.unpack_from('<H', r.data, r.tell())[0]
            if peek >= 0x8000:
                self._read_mfc_ref_inline(r, 'CEdge')
                edge_count += 1
            else:
                break

        # Arc parameters: 5 prefix bytes + 14 f64 values = 117 bytes
        if r.remaining() >= 117:
            r.read(117)

        self.arc.set_object(idx, {'type': 'CArcCurve', 'edge_count': edge_count})
        self.log(f"CArcCurve[{idx}]: {edge_count} edges + 117 arc params")

    def _parse_edge_inline(self, idx):
        """Parse a CEdge created inline within a CEdgeUse chain.

        Format: entity_base(version-dependent) + start_vertex(MFC) + end_vertex(MFC) + trailing(u16)
        The trailing u16 is always present (edge-use partner ref or zero).
        """
        r = self.arc.r

        entity_id, flags, layer_ref, mat_ref, back_mat_ref = self._read_entity_base(r)

        # Start vertex
        sv_ref = self._read_mfc_ref_inline(r, 'CVertex')
        # End vertex
        ev_ref = self._read_mfc_ref_inline(r, 'CVertex')

        # Trailing curve/partner reference (MFC object ref)
        # Present in v3+ inline CEdge; v1-v2 inline CEdge has NO trailing ref.
        # This can be NULL (0), object backref, class backref, or FFFF new class
        # (e.g., CArcCurve introduced inline when this edge belongs to an arc).
        if self.model.version_major >= 3 and r.remaining() >= 2:
            self._read_mfc_ref_inline(r, 'CArcCurve')

        # Resolve vertex objects - try direct lookup first, then fuzzy
        sv = self.arc.get_object(sv_ref) if sv_ref else None
        ev = self.arc.get_object(ev_ref) if ev_ref else None
        if not isinstance(sv, Vertex) and sv_ref:
            sv = self._resolve_vertex_ref(sv_ref)
        if not isinstance(ev, Vertex) and ev_ref:
            ev = self._resolve_vertex_ref(ev_ref)

        if isinstance(sv, Vertex) and isinstance(ev, Vertex):
            edge = Edge(sv, ev, map_idx=idx)
            self.model.edges.append(edge)
            self.arc.set_object(idx, edge)
        else:
            # Store resolved vertex objects directly in dict for later use
            self.arc.set_object(idx, {
                'type': 'CEdge', 'sv': sv_ref, 'ev': ev_ref,
                'sv_obj': sv if isinstance(sv, Vertex) else None,
                'ev_obj': ev if isinstance(ev, Vertex) else None
            })

    def _parse_material(self, idx):
        """Parse CMaterial."""
        r = self.arc.r
        try:
            # v4+/v5+ has a u16 base field; v3 starts directly with the name string
            if self.model.version_major >= 4:
                base = r.u16()
            name = self._read_string(r)
            mat = Material(name, map_idx=idx)
            mat_type = r.u8()

            if mat_type == 0:
                r.u8()  # reserved
                red, green, blue, alpha = r.u8(), r.u8(), r.u8(), r.u8()
                mat.color = (red, green, blue, alpha)
                self._read_string(r)  # display name
                r.skip(8)  # padding
                transparency = r.f64()  # material-level transparency (0.0-1.0)
                use_alpha = r.u8()  # flag: 1 = apply transparency
                if use_alpha:
                    mat.opacity = 1.0 - transparency
                self.log(f"Material: {name} rgba=({red},{green},{blue},{alpha}) opacity={mat.opacity}")
            elif mat_type == 1:
                mat.has_texture = True
                fb = r.read(4)
                if fb[3] == 0x80:
                    tv = r.u32()
                    if tv > 0:
                        ts = r.u32()
                        if 0 < ts < r.remaining():
                            mat.texture_data = r.read(ts)
                else:
                    # Alternate texture format: flag(1) + size(4) + image data
                    r.u8()  # flag
                    ts = r.u32()
                    if 0 < ts < r.remaining():
                        mat.texture_data = r.read(ts)
                # Post-texture: dims + filename + color + transparency
                try:
                    tex_w = r.f64()  # texture width
                    tex_h = r.f64()  # texture height
                    tex_fn = self._read_string(r)  # texture filename
                    mat.texture_filename = tex_fn
                    red, green, blue, alpha = r.u8(), r.u8(), r.u8(), r.u8()
                    mat.color = (red, green, blue, alpha)
                    r.u8()  # reserved
                    r.u8(); r.u8(); r.u8(); r.u8()  # second RGBA (back color)
                    self._read_string(r)  # display name
                    r.skip(8)  # padding
                    transparency = r.f64()
                    use_alpha = r.u8()
                    if use_alpha:
                        mat.opacity = 1.0 - transparency
                    self.log(f"Material: {name} (textured) "
                            f"rgba=({red},{green},{blue},{alpha}) "
                            f"opacity={mat.opacity}")
                except Exception:
                    self._scan_to_next_entity(r, max_scan=8192)
                    self.log(f"Material: {name} (textured, "
                            f"trailing data scan)")

            self.model.materials.append(mat)
            self.arc.set_object(idx, mat)
        except Exception as e:
            self.log(f"Material parse error: {e}")
            self.arc.set_object(idx, {'type': 'CMaterial', 'error': str(e)})

    def _resolve_eu_face_loops(self):
        """Build a mapping from each CEdgeUse to its owning face's loop index.

        In v1 files, CEdgeUse loop_ref often points to another CEdgeUse rather
        than the CLoop directly.  Following the loop_ref chain transitively
        eventually reaches the CLoop.  For circular chains that never reach a
        CLoop, fall back to positional assignment (EU belongs to the face whose
        loop is the largest known loop index <= the EU's map index).
        """
        face_loops = set(self._loop_to_face.keys())
        face_loop_sorted = sorted(face_loops)
        eu_to_face_loop = {}

        def _resolve(idx, visited=None):
            if visited is None:
                visited = set()
            if idx in eu_to_face_loop:
                return eu_to_face_loop[idx]
            if idx in face_loops:
                return idx
            if idx in visited:
                return None  # circular
            visited.add(idx)
            eu = self._edgeuse_chains.get(idx)
            if eu is None:
                return idx if idx in face_loops else None
            lr = eu.get('loop_ref')
            if lr is None:
                return None
            if lr in face_loops:
                return lr
            return _resolve(lr, visited)

        for eu_idx in self._edgeuse_chains:
            resolved = _resolve(eu_idx)
            eu_to_face_loop[eu_idx] = resolved

        # Positional fallback for unresolved (circular) chains
        unresolved = [idx for idx, r in eu_to_face_loop.items() if r is None]
        if unresolved and face_loop_sorted:
            import bisect
            for eu_idx in unresolved:
                pos = bisect.bisect_right(face_loop_sorted, eu_idx) - 1
                if pos >= 0:
                    eu_to_face_loop[eu_idx] = face_loop_sorted[pos]

        return eu_to_face_loop

    def _verts_on_plane(self, verts, face):
        """Check if vertices are within tolerance of face plane."""
        nx, ny, nz = face.normal
        d = face.distance
        nl = math.sqrt(nx*nx + ny*ny + nz*nz)
        if nl > 0:
            nx, ny, nz = nx/nl, ny/nl, nz/nl
            d = d / nl
        max_dist = max(abs(nx*v.x + ny*v.y + nz*v.z + d) for v in verts)
        return max_dist <= 1.0

    def _reconstruct_faces_from_edgeuse(self):
        """Reconstruct face vertex lists from CEdgeUse chain data.

        v5+: Uses face._edge_uses populated during parsing, or sequential matching.
        v3: Uses sequential matching: face -> loop -> first EU chain after the loop.
        v1: Uses transitive loop_ref resolution to collect all EUs per face,
            then builds a directed edge graph to order vertices.
        """
        if not self._edgeuse_chains:
            return 0

        assigned = 0

        # First pass: v5+ faces with direct _edge_uses (always override heuristic)
        eu_rejected = 0
        for face in self.model.faces:
            edge_uses = getattr(face, '_edge_uses', None)
            if not edge_uses:
                continue

            # For multi-loop faces (holes): split EUs by loop_ref
            # and assign outer loop + holes separately.
            if face.loop_count > 1:
                # Group EUs by loop_ref (sequential order preserved)
                # First EU of each inner loop may have loop_ref=0
                # (the null_ref prefix in v4 EU format) - merge with next group
                raw_groups = []
                current_loop = None
                current_eus = []
                for eu in edge_uses:
                    lr = eu.get('loop_ref', 0)
                    if lr != current_loop and current_eus:
                        raw_groups.append((current_loop, current_eus))
                        current_eus = []
                    current_loop = lr
                    current_eus.append(eu)
                if current_eus:
                    raw_groups.append((current_loop, current_eus))
                # Merge loop_ref=0 groups into the following group
                loop_groups = []
                pending = []
                for lr, eus in raw_groups:
                    if lr == 0 and len(eus) <= 2:
                        pending.extend(eus)
                    else:
                        if pending:
                            eus = pending + eus
                            pending = []
                        loop_groups.append(eus)
                if pending:
                    if loop_groups:
                        loop_groups[-1].extend(pending)
                    else:
                        loop_groups.append(pending)

                # Validate plane for all vertices
                outer_done = False
                any_assigned = False
                # Use face's stored plane for validation (more
                # reliable than RANSAC on drifted vertices)
                fnx, fny, fnz = face.normal
                fnl = math.sqrt(fnx*fnx + fny*fny + fnz*fnz)
                if fnl > 0:
                    fnx, fny, fnz = fnx/fnl, fny/fnl, fnz/fnl
                fd = face.distance / fnl if fnl > 0 else face.distance

                def _on_fplane(v):
                    return abs(fnx*v.x + fny*v.y + fnz*v.z + fd) <= 1.0

                for loop_eus in loop_groups:
                    verts_ordered = []
                    eu_refs_ml = []
                    for eu in loop_eus:
                        edge_ref = eu.get('edge_ref')
                        reversed_flag = eu.get('reversed', 0)
                        if edge_ref:
                            sv = self._get_edge_vertex(
                                edge_ref, reversed_flag)
                            if (isinstance(sv, Vertex) and
                                    sv not in verts_ordered):
                                verts_ordered.append(sv)
                                eu_refs_ml.append(
                                    (edge_ref, reversed_flag, sv))
                            elif isinstance(sv, Vertex):
                                eu_refs_ml.append(
                                    (edge_ref, reversed_flag, sv))
                            else:
                                eu_refs_ml.append(
                                    (edge_ref, reversed_flag, None))
                    if len(verts_ordered) < 3:
                        continue
                    # Filter + recover using face's stored plane
                    fp = (fnx, fny, fnz, fd)
                    verts_ordered = self._filter_coplanar_verts_recover(
                        verts_ordered, eu_refs_ml, face_plane=fp)
                    if len(verts_ordered) < 3:
                        eu_rejected += 1
                        continue
                    if not outer_done:
                        face.vertices = verts_ordered
                        face.eu_assigned = True
                        outer_done = True
                        any_assigned = True
                    else:
                        face.holes.append(verts_ordered)
                        self.log(f"Face[{face.map_idx}]: hole with "
                                f"{len(verts_ordered)} verts")
                if any_assigned:
                    assigned += 1
                continue

            verts_ordered = []
            eu_refs = []  # (edge_ref, reversed, vertex_or_None)
            for eu in edge_uses:
                edge_ref = eu.get('edge_ref')
                reversed_flag = eu.get('reversed', 0)
                if edge_ref:
                    sv = self._get_edge_vertex(edge_ref, reversed_flag)
                    if isinstance(sv, Vertex) and sv not in verts_ordered:
                        verts_ordered.append(sv)
                        eu_refs.append((edge_ref, reversed_flag, sv))
                    elif isinstance(sv, Vertex):
                        eu_refs.append((edge_ref, reversed_flag, sv))
                    else:
                        eu_refs.append((edge_ref, reversed_flag, None))
            if len(verts_ordered) >= 3:
                # Use face's stored plane for validation
                fnx, fny, fnz = face.normal
                fnl = math.sqrt(fnx*fnx + fny*fny + fnz*fnz)
                if fnl > 0:
                    fp = (fnx/fnl, fny/fnl, fnz/fnl,
                          face.distance / fnl)
                else:
                    fp = None
                verts_ordered = self._filter_coplanar_verts_recover(
                    verts_ordered, eu_refs, face_plane=fp)
                if len(verts_ordered) < 3:
                    eu_rejected += 1
                    face._edge_uses = []
                    continue
                face.vertices = verts_ordered
                face.eu_assigned = True
                assigned += 1
        # Build transitive EU -> face loop mapping for v1 orphan resolution
        eu_to_face_loop = self._resolve_eu_face_loops()

        # Second pass: sequential matching for remaining faces (v3 path)
        eu_sorted = sorted(self._edgeuse_chains.keys())
        loop_face_sorted = sorted(self._loop_to_face.items())
        is_v3 = self.model.version_major in (2, 3, 4)

        # For v3: build set of boundary indices (loops and faces) to
        # determine the end of EUs for each loop
        if is_v3:
            loop_indices = set(self._loop_to_face.keys())
            face_indices = {f.map_idx for f in self.model.faces}
            boundary_indices = sorted(loop_indices | face_indices)

        # Track how many loops we've assigned per face
        face_loop_assigned = {}

        for loop_idx, face in loop_face_sorted:
            face_id = id(face)
            loops_done = face_loop_assigned.get(face_id, 0)
            is_hole = (face.vertices and len(face.vertices) >= 3 and
                       face.loop_count > 1 and loops_done > 0)
            if face.vertices and len(face.vertices) >= 3 and not is_hole:
                continue

            # Find the first CEdgeUse with map_idx > loop_idx (sequential match)
            first_eu = None
            for eu_idx in eu_sorted:
                if eu_idx > loop_idx:
                    first_eu = eu_idx
                    break

            if first_eu is None:
                continue

            if is_v3:
                # v3: CEdgeUse next_ref points to CLoop (terminator), not
                # next EU. Collect ALL EUs sequentially between this loop
                # and the next boundary (next CLoop or CFace) in file order.
                next_boundary = None
                for bi in boundary_indices:
                    if bi > loop_idx:
                        next_boundary = bi
                        break
                if next_boundary is None:
                    next_boundary = float('inf')

                verts_ordered = []
                seen = set()
                for eu_idx in eu_sorted:
                    if eu_idx <= loop_idx or eu_idx >= next_boundary:
                        if eu_idx >= next_boundary:
                            break
                        continue
                    eu = self._edgeuse_chains[eu_idx]
                    edge_ref = eu.get('edge_ref')
                    rev = eu.get('reversed', 0)
                    if edge_ref:
                        sv = self._get_edge_vertex(edge_ref, rev)
                        if isinstance(sv, Vertex) and id(sv) not in seen:
                            verts_ordered.append(sv)
                            seen.add(id(sv))
            else:
                # v1/v4+: Use the EU's actual loop_ref for orphan resolution
                effective_loop = loop_idx
                first_eu_data = self._edgeuse_chains.get(first_eu)
                if first_eu_data:
                    eu_loop = first_eu_data.get('loop_ref')
                    if eu_loop and eu_loop != loop_idx:
                        effective_loop = eu_loop

                # Trace the chain to get ordered vertices
                verts_ordered = self._trace_edgeuse_chain(
                    first_eu, face_loop_idx=effective_loop,
                    eu_to_face_loop=eu_to_face_loop,
                    face_scope=face.scope)

            if len(verts_ordered) >= 3:
                # Validate vertices lie on face plane (same as first pass)
                nx, ny, nz = face.normal
                d = face.distance
                nl = math.sqrt(nx*nx + ny*ny + nz*nz)
                if nl > 0:
                    nx, ny, nz = nx/nl, ny/nl, nz/nl
                    d = d / nl
                max_dist = max(abs(nx*v.x + ny*v.y + nz*v.z + d)
                              for v in verts_ordered)
                if max_dist > 1.0:
                    eu_rejected += 1
                    continue
                if is_hole:
                    face.holes.append(verts_ordered)
                    self.log(f"Face[{face.map_idx}]: hole loop with "
                            f"{len(verts_ordered)} verts")
                else:
                    face.vertices = verts_ordered
                    face.eu_assigned = True
                    assigned += 1
                face_loop_assigned[face_id] = loops_done + 1

        if eu_rejected:
            self.log(f"Rejected {eu_rejected} EU-assigned faces "
                    f"(vertices off-plane >1.0)")
            self._eu_rejected_count = eu_rejected

        return assigned

    @staticmethod
    def _count_crossings(verts):
        """Count edge-edge crossings in a polygon vertex list."""
        n = len(verts)
        crossings = 0
        for i in range(n):
            j = (i + 1) % n
            ax, ay = verts[i].x, verts[i].y
            bx, by = verts[j].x, verts[j].y
            for k in range(i + 2, n):
                if k == (i - 1) % n or k == j:
                    continue
                el = (k + 1) % n
                if el == i:
                    continue
                cx, cy = verts[k].x, verts[k].y
                dx, dy = verts[el].x, verts[el].y
                d1 = (bx-ax)*(cy-ay) - (by-ay)*(cx-ax)
                d2 = (bx-ax)*(dy-ay) - (by-ay)*(dx-ax)
                d3 = (dx-cx)*(ay-cy) - (dy-cy)*(ax-cx)
                d4 = (dx-cx)*(by-cy) - (dy-cy)*(bx-cx)
                if d1 * d2 < 0 and d3 * d4 < 0:
                    crossings += 1
        return crossings

    def _compute_best_plane(self, verts):
        """Find the best-fit plane for a vertex list using RANSAC.

        Returns (nx, ny, nz, d) for the plane with the most inliers,
        or None if no valid plane found.
        """
        n = len(verts)
        best_plane = None
        best_count = 0
        for i in range(n):
            v0 = verts[i]
            v1 = verts[(i + 1) % n]
            v2 = verts[(i + 2) % n]
            ax, ay, az = v1.x-v0.x, v1.y-v0.y, v1.z-v0.z
            bx, by, bz = v2.x-v0.x, v2.y-v0.y, v2.z-v0.z
            cnx = ay*bz - az*by
            cny = az*bx - ax*bz
            cnz = ax*by - ay*bx
            cnl = math.sqrt(cnx*cnx + cny*cny + cnz*cnz)
            if cnl < 1e-10:
                continue
            cnx, cny, cnz = cnx/cnl, cny/cnl, cnz/cnl
            cd = -(cnx*v0.x + cny*v0.y + cnz*v0.z)
            count = sum(1 for v in verts
                        if abs(cnx*v.x + cny*v.y + cnz*v.z + cd) <= 1.0)
            if count > best_count:
                best_count = count
                best_plane = (cnx, cny, cnz, cd)
                if count == n:
                    break
        return best_plane

    def _fix_scrambled_face_boundaries(self):
        """Fix faces with scrambled vertex order by reconstructing boundaries
        from edge connectivity.

        When EU chains produce vertices in wrong order (< 50% of consecutive
        pairs are edge-connected), trace the actual edge loops to reconstruct
        correct polygon boundaries. The largest loop becomes the outer boundary;
        smaller loops become holes.
        """
        from collections import defaultdict
        if not self.model.edges:
            return

        # Build DUAL edge adjacency: ID-based (fast, exact) and
        # coordinate-based (fallback for inline-created vertices).
        adj_id = defaultdict(set)
        def _coord_key(v):
            return (round(v.x, 4), round(v.y, 4), round(v.z, 4))
        coord_adj = defaultdict(set)
        for e in self.model.edges:
            if e.start_vertex and e.end_vertex:
                adj_id[id(e.start_vertex)].add(id(e.end_vertex))
                adj_id[id(e.end_vertex)].add(id(e.start_vertex))
                sk = _coord_key(e.start_vertex)
                ek = _coord_key(e.end_vertex)
                coord_adj[sk].add(ek)
                coord_adj[ek].add(sk)

        fixed = 0
        for face in self.model.faces:
            if not face.vertices or len(face.vertices) < 10:
                continue

            # Check if vertex order is valid
            all_verts = list(face.vertices)
            if face.holes:
                for h in face.holes:
                    all_verts.extend(h)
            # Try ID-based adjacency first (exact match)
            face_vids = set(id(v) for v in all_verts)
            adj_by_id = defaultdict(set)
            for vid in face_vids:
                for nb in adj_id.get(vid, set()):
                    if nb in face_vids:
                        adj_by_id[vid].add(nb)

            n = len(face.vertices)
            connected_id = sum(
                1 for i in range(n)
                if id(face.vertices[(i+1) % n])
                    in adj_by_id[id(face.vertices[i])])

            # If ID-based works well, use it; otherwise fall back to coords
            if connected_id >= n * 0.5 or len(adj_by_id) >= len(face_vids) * 0.8:
                use_coords = False
                adj = {vid: nbs for vid, nbs in adj_by_id.items()}
                key_fn = id
                key_to_vert = {id(v): v for v in all_verts}
                connected = connected_id
            else:
                use_coords = True
                coord_to_vert = {}
                face_coords = set()
                for v in all_verts:
                    ck = _coord_key(v)
                    coord_to_vert[ck] = v
                    face_coords.add(ck)
                adj = defaultdict(set)
                for ck in face_coords:
                    for nb in coord_adj.get(ck, set()):
                        if nb in face_coords:
                            adj[ck].add(nb)
                key_fn = _coord_key
                key_to_vert = coord_to_vert
                connected = sum(
                    1 for i in range(n)
                    if _coord_key(face.vertices[(i+1) % n])
                        in adj[_coord_key(face.vertices[i])])

            if connected >= n * 0.5:
                continue  # vertex order is fine

            # Trace edge loops from degree-2 vertices
            visited = set()
            loops = []
            for start_key in adj:
                if start_key in visited or len(adj[start_key]) != 2:
                    continue
                loop = [start_key]
                visited.add(start_key)
                prev = start_key
                curr = list(adj[start_key])[0]
                while curr != start_key:
                    if curr in visited:
                        break
                    visited.add(curr)
                    loop.append(curr)
                    neighbors = adj[curr] - {prev}
                    if not neighbors:
                        break
                    prev = curr
                    curr = list(neighbors)[0]
                if curr == start_key and len(loop) >= 3:
                    loops.append(loop)

            if not loops:
                continue

            # Sort loops by area (largest = outer boundary)
            loop_data = []
            for loop in loops:
                area = 0
                nx, ny, nz = face.normal
                ax = abs(nx)
                ay = abs(ny)
                az = abs(nz)
                for j in range(len(loop)):
                    k = (j + 1) % len(loop)
                    v1 = key_to_vert[loop[j]]
                    v2 = key_to_vert[loop[k]]
                    if ay >= ax and ay >= az:
                        area += v1.x * v2.z - v2.x * v1.z
                    elif ax >= ay and ax >= az:
                        area += v1.y * v2.z - v2.y * v1.z
                    else:
                        area += v1.x * v2.y - v2.x * v1.y
                loop_verts = [key_to_vert[k] for k in loop]
                loop_data.append((abs(area), loop_verts))

            loop_data.sort(reverse=True)

            # Largest loop = outer, rest = holes
            face.vertices = loop_data[0][1]
            face.holes = [ld[1] for ld in loop_data[1:]]
            face.loop_count = len(loop_data)
            fixed += 1
            self.log(f"Fixed scrambled face: {n} -> {len(face.vertices)} outer "
                     f"+ {len(face.holes)} holes (edge-traced)")

        if fixed:
            self.log(f"Fixed {fixed} faces with scrambled vertex order")

    def _supplement_incomplete_eu_faces(self):
        """Supplement EU-assigned faces that have fewer vertices than EUs.

        For each such face, find on-plane vertices reachable from existing
        face vertices via the model's edge graph, and insert them to form
        a proper polygon.
        """
        # Build edge adjacency: vertex id -> set of edge-connected vertex ids
        adj = {}
        vid_map = {}
        for e in self.model.edges:
            sv, ev = e.start_vertex, e.end_vertex
            if sv and ev:
                sid, eid = id(sv), id(ev)
                adj.setdefault(sid, set()).add(eid)
                adj.setdefault(eid, set()).add(sid)
                vid_map[sid] = sv
                vid_map[eid] = ev

        supplemented = 0
        for face in self.model.faces:
            if not face.vertices or len(face.vertices) < 3:
                continue
            eu_count = len(getattr(face, '_edge_uses', []))
            if eu_count == 0 or len(face.vertices) >= eu_count:
                continue
            # Skip if EU resolved enough unique vertices — the "missing"
            # ones are just shared-edge duplicates. Adding neighbors from
            # other faces then re-sorting with _convex_order corrupts
            # non-convex (concave) polygon winding order.
            missing = eu_count - len(face.vertices)
            if missing <= 3 and len(face.vertices) >= eu_count * 0.9:
                continue

            # Face's stored plane
            nx, ny, nz = face.normal
            nl = math.sqrt(nx*nx + ny*ny + nz*nz)
            if nl < 1e-10:
                continue
            nx, ny, nz = nx/nl, ny/nl, nz/nl
            d = face.distance / nl

            def on_plane(v):
                return abs(nx*v.x + ny*v.y + nz*v.z + d) < 0.1

            # Find on-plane vertices reachable via edges from face
            # verts (up to 2 hops for faces missing many vertices)
            face_vids = set(id(v) for v in face.vertices)
            candidates = set()
            frontier = set(face_vids)
            max_hops = 2 if len(face.vertices) < eu_count - 1 else 1
            for _ in range(max_hops):
                next_frontier = set()
                for fvid in frontier:
                    for nbr_id in adj.get(fvid, set()):
                        if nbr_id not in face_vids and \
                                nbr_id not in candidates:
                            nbr = vid_map.get(nbr_id)
                            if nbr and on_plane(nbr):
                                candidates.add(nbr_id)
                                next_frontier.add(nbr_id)
                frontier = next_frontier
                if not frontier:
                    break

            # If no edge-connected candidates found and face has 3
            # verts (should be 4+), try parallelogram completion:
            # for each triple permutation, compute D = X + Y - Z
            # and check if D matches an on-plane model vertex.
            if not candidates and len(face.vertices) == 3 and \
                    eu_count >= 4:
                verts3 = face.vertices
                on_plane_verts = [
                    v for v in self.model.vertices
                    if on_plane(v) and v not in verts3]
                for ai in range(3):
                    for bi in range(3):
                        if bi == ai:
                            continue
                        ci = 3 - ai - bi
                        a, b, c = verts3[ai], verts3[bi], verts3[ci]
                        dx = b.x + c.x - a.x
                        dy = b.y + c.y - a.y
                        dz = b.z + c.z - a.z
                        for v in on_plane_verts:
                            if (abs(v.x - dx) < 0.01 and
                                    abs(v.y - dy) < 0.01 and
                                    abs(v.z - dz) < 0.01):
                                candidates.add(id(v))
                                break
                        if candidates:
                            break
                    if candidates:
                        break

            if not candidates:
                continue

            # Add candidate vertices and re-order the polygon
            all_verts = list(face.vertices)
            for cid in candidates:
                v = vid_map.get(cid)
                if not v:
                    # Check model vertices
                    for mv in self.model.vertices:
                        if id(mv) == cid:
                            v = mv
                            break
                if v and v not in all_verts:
                    all_verts.append(v)

            if len(all_verts) > len(face.vertices):
                ordered = self._convex_order(all_verts, face.normal)
                if ordered and len(ordered) > len(face.vertices):
                    face.vertices = ordered
                    supplemented += 1

        if supplemented:
            self.log(f"Supplemented {supplemented} faces with "
                    f"edge-connected on-plane vertices")

    def _filter_coplanar_verts(self, verts):
        """Filter vertex list to keep only coplanar vertices."""
        if len(verts) < 3:
            return verts
        plane = self._compute_best_plane(verts)
        if not plane:
            return []
        cnx, cny, cnz, cd = plane
        return [v for v in verts
                if abs(cnx*v.x + cny*v.y + cnz*v.z + cd) <= 1.0]

    def _filter_coplanar_verts_recover(self, verts, eu_refs,
                                       face_plane=None):
        """Filter coplanar vertices and try to recover dropped ones.

        For each vertex dropped by plane validation, search nearby edge_refs
        (±5) for an Edge with a vertex on the computed plane.
        If face_plane is provided (nx, ny, nz, d), use it instead of RANSAC.
        """
        if len(verts) < 3:
            return verts
        if face_plane:
            cnx, cny, cnz, cd = face_plane
        else:
            plane = self._compute_best_plane(verts)
            if not plane:
                return []
            cnx, cny, cnz, cd = plane

        def on_plane(v):
            return abs(cnx*v.x + cny*v.y + cnz*v.z + cd) <= 1.0

        result = []
        seen = set()
        for eref, rev, sv in eu_refs:
            if sv is None or id(sv) in seen:
                continue
            if on_plane(sv):
                result.append(sv)
                seen.add(id(sv))
            else:
                # Try nearby edge_refs for a better vertex
                recovered = False
                for delta in [-1, 1, -2, 2, -3, 3, -4, 4, -5, 5]:
                    alt = self.arc.get_object(eref + delta)
                    if isinstance(alt, Edge):
                        sv2 = alt.start_vertex
                        ev2 = alt.end_vertex
                        if rev:
                            sv2, ev2 = ev2, sv2
                        if (isinstance(sv2, Vertex) and
                                id(sv2) not in seen and on_plane(sv2)):
                            result.append(sv2)
                            seen.add(id(sv2))
                            recovered = True
                            break
                        if (isinstance(ev2, Vertex) and
                                id(ev2) not in seen and on_plane(ev2)):
                            result.append(ev2)
                            seen.add(id(ev2))
                            recovered = True
                            break
                    elif isinstance(alt, Vertex):
                        if id(alt) not in seen and on_plane(alt):
                            result.append(alt)
                            seen.add(id(alt))
                            recovered = True
                            break
        return result

    def _get_edge_vertex(self, edge_ref, reversed_flag, _depth=0,
                         face_scope=None):
        """Get the start vertex of an edge, respecting the reversed flag.

        Handles MFC map drift by trying multiple resolution strategies:
        1. Direct Edge object lookup
        2. Dict with sv/ev keys (partially parsed edge)
        3. Vertex object (edge_ref actually points to vertex)
        4. CEdgeUse dict (follow its edge_ref, max 1 level)
        5. Fuzzy search ±10 for nearby Edge objects
        face_scope: if set, only accept edges whose vertices match this scope.
        """
        edge_obj = self.arc.get_object(edge_ref)
        if isinstance(edge_obj, Edge):
            sv = edge_obj.start_vertex
            ev = edge_obj.end_vertex
            if reversed_flag:
                sv, ev = ev, sv
            if face_scope is not None and isinstance(sv, Vertex):
                if sv.scope != face_scope:
                    pass  # wrong scope, fall through to fuzzy
                else:
                    return sv
            else:
                return sv
        elif isinstance(edge_obj, Vertex):
            if self.model.version_major >= 4:
                # v4+: edge_ref should be an Edge; Vertex = MFC drift of +1.
                # The Edge is typically at edge_ref-1, with this Vertex as sv.
                # Check edge_ref-1: if it's an Edge whose sv or ev is this vertex,
                # use the correct vertex respecting reversed_flag.
                prev = self.arc.get_object(edge_ref - 1)
                if isinstance(prev, Edge):
                    sv = prev.start_vertex
                    ev = prev.end_vertex
                    if sv is edge_obj or ev is edge_obj:
                        if reversed_flag:
                            sv, ev = ev, sv
                        if face_scope is None or (isinstance(sv, Vertex) and
                                                  sv.scope == face_scope):
                            return sv
                # Fall through to fuzzy search
            else:
                # v1-v3: use Vertex directly.
                return edge_obj
        elif isinstance(edge_obj, dict):
            # Try pre-resolved vertex objects first (from inline parsing)
            sv_o = edge_obj.get('sv_obj')
            ev_o = edge_obj.get('ev_obj')
            if isinstance(sv_o, Vertex) and isinstance(ev_o, Vertex):
                v = ev_o if reversed_flag else sv_o
                if face_scope is None or v.scope == face_scope:
                    return v
            sv_ref = edge_obj.get('sv')
            ev_ref = edge_obj.get('ev')
            if sv_ref is not None and ev_ref is not None:
                if reversed_flag:
                    sv_ref, ev_ref = ev_ref, sv_ref
                v = self._resolve_vertex_ref(sv_ref)
                if v and (face_scope is None or v.scope == face_scope):
                    return v
            # CEdgeUse dict: follow its edge_ref (max 1 level deep)
            if _depth < 1:
                inner_edge_ref = edge_obj.get('edge_ref')
                if inner_edge_ref and inner_edge_ref != edge_ref:
                    return self._get_edge_vertex(inner_edge_ref, reversed_flag,
                                                  _depth + 1,
                                                  face_scope=face_scope)
        # Fuzzy search for nearby Edge (scope-filtered if available)
        # v5+ MFC drift is typically small (-1 to -3), try close offsets first
        search_range = 15 if self.model.version_major >= 4 else 10
        for offset in range(-search_range, search_range + 1):
            if offset == 0:
                continue
            nearby = self.arc.get_object(edge_ref + offset)
            if isinstance(nearby, Edge):
                sv = nearby.start_vertex
                ev = nearby.end_vertex
                if reversed_flag:
                    sv, ev = ev, sv
                if face_scope is not None and isinstance(sv, Vertex):
                    if sv.scope != face_scope:
                        continue  # wrong scope, try next
                return sv
        return None

    def _trace_edgeuse_chain(self, first_eu, face_loop_idx=None,
                             eu_to_face_loop=None, face_scope=None):
        """Trace a CEdgeUse chain starting at first_eu, returning ordered vertices.

        In v1 files, twin edge-uses (from adjacent faces) can be interleaved in
        the chain via next_ref, causing some own-loop EUs to be orphaned (skipped).
        When face_loop_idx is provided, we also collect orphaned EUs and build an
        edge connectivity graph to reconstruct the full polygon.

        eu_to_face_loop: optional dict mapping EU map_idx -> owning face loop idx,
        built by _resolve_eu_face_loops() using transitive loop_ref resolution.
        face_scope: scope number for scope-filtered fuzzy edge search (v4+).
        """
        # Step 1: Trace the next_ref chain, collecting directed edges
        chain_edges = []  # list of (sv, ev)
        simple_verts = []  # start-vertex-only list (original approach)
        chain_visited = set()
        current = first_eu
        while current and current not in chain_visited:
            chain_visited.add(current)
            eu = self._edgeuse_chains.get(current)
            if not eu:
                break

            edge_ref = eu.get('edge_ref')
            reversed_flag = eu.get('reversed', 0)

            if edge_ref:
                edge_obj = self.arc.get_object(edge_ref)
                sv = None
                ev = None
                # Use scope filtering for v4+ fuzzy searches
                fs = face_scope if self.model.version_major >= 4 else None
                if isinstance(edge_obj, Edge):
                    sv = edge_obj.start_vertex
                    ev = edge_obj.end_vertex
                    if reversed_flag:
                        sv, ev = ev, sv
                    # v4+: reject cross-scope edges from MFC drift
                    if (fs is not None and isinstance(sv, Vertex)
                            and sv.scope != fs):
                        sv = self._get_edge_vertex(
                            edge_ref, reversed_flag, face_scope=fs)
                        ev = None
                elif isinstance(edge_obj, dict):
                    etype = edge_obj.get('type', '')
                    if etype in ('CEdge', '') and (
                            edge_obj.get('sv') is not None or
                            edge_obj.get('sv_obj') is not None):
                        sv_ref = edge_obj.get('sv')
                        ev_ref = edge_obj.get('ev')
                        if reversed_flag:
                            sv_ref, ev_ref = ev_ref, sv_ref
                        sv = self._resolve_vertex_ref(sv_ref)
                        ev = self._resolve_vertex_ref(ev_ref)
                        # v4+: reject cross-scope
                        if (fs is not None and isinstance(sv, Vertex)
                                and sv.scope != fs):
                            sv = self._get_edge_vertex(
                                edge_ref, reversed_flag, face_scope=fs)
                            ev = None
                    elif self.model.version_major >= 4:
                        sv = self._get_edge_vertex(
                            edge_ref, reversed_flag, face_scope=fs)
                    else:
                        sv_ref = edge_obj.get('sv')
                        ev_ref = edge_obj.get('ev')
                        if reversed_flag:
                            sv_ref, ev_ref = ev_ref, sv_ref
                        sv = self._resolve_vertex_ref(sv_ref)
                        ev = self._resolve_vertex_ref(ev_ref)
                elif isinstance(edge_obj, Vertex):
                    if self.model.version_major >= 4:
                        sv = self._get_edge_vertex(
                            edge_ref, reversed_flag, face_scope=fs)
                        if sv is None:
                            sv = edge_obj  # last resort
                    else:
                        sv = edge_obj
                else:
                    # Fallback: check edge_ref-1 for Edge (drift from
                    # Face or other non-edge object)
                    prev = self.arc.get_object(edge_ref - 1) if edge_ref > 0 else None
                    if isinstance(prev, Edge):
                        sv = prev.start_vertex
                        ev = prev.end_vertex
                        if reversed_flag:
                            sv, ev = ev, sv
                        if (fs is not None and isinstance(sv, Vertex)
                                and sv.scope != fs):
                            sv = self._get_edge_vertex(
                                edge_ref, reversed_flag, face_scope=fs)
                            ev = None
                    else:
                        sv = self._get_edge_vertex(
                            edge_ref, reversed_flag, face_scope=fs)

                if isinstance(sv, Vertex) and sv not in simple_verts:
                    simple_verts.append(sv)
                if isinstance(sv, Vertex) and isinstance(ev, Vertex):
                    chain_edges.append((sv, ev))

            current = eu.get('next_ref')
            if current and current not in self._edgeuse_chains:
                break

        # Step 2: If face_loop_idx provided, find orphaned EUs and try graph approach
        if face_loop_idx is not None:
            # Collect ALL EUs that belong to this face using transitive resolution
            own_eu_indices = set()
            for idx, eu in self._edgeuse_chains.items():
                if eu_to_face_loop and eu_to_face_loop.get(idx) == face_loop_idx:
                    own_eu_indices.add(idx)
                elif eu.get('loop_ref') == face_loop_idx:
                    own_eu_indices.add(idx)

            # Collect directed edges from all own-face EUs not in the chain
            orphan_edges = []
            for idx in own_eu_indices:
                if idx in chain_visited:
                    continue
                eu = self._edgeuse_chains[idx]
                edge_ref = eu.get('edge_ref')
                rev = eu.get('reversed', 0)
                if edge_ref:
                    edge_obj = self.arc.get_object(edge_ref)
                    if isinstance(edge_obj, Edge):
                        sv = edge_obj.start_vertex
                        ev = edge_obj.end_vertex
                        if rev:
                            sv, ev = ev, sv
                        orphan_edges.append((sv, ev))

            # Also collect edges from own-face EUs that WERE in the chain
            own_chain_edges = []
            for idx in own_eu_indices & chain_visited:
                eu = self._edgeuse_chains[idx]
                edge_ref = eu.get('edge_ref')
                rev = eu.get('reversed', 0)
                if edge_ref:
                    edge_obj = self.arc.get_object(edge_ref)
                    if isinstance(edge_obj, Edge):
                        sv = edge_obj.start_vertex
                        ev = edge_obj.end_vertex
                        if rev:
                            sv, ev = ev, sv
                        own_chain_edges.append((sv, ev))

            # Use all own-face edges (chain + orphan) for graph approach
            all_own_edges = own_chain_edges + orphan_edges
            if len(all_own_edges) >= 3:
                adj = {}
                for sv, ev in all_own_edges:
                    adj.setdefault(id(sv), []).append(ev)

                start_v = all_own_edges[0][0]

                # Walk the graph to produce ordered vertices
                graph_verts = [start_v]
                seen_ids = {id(start_v)}
                current_v = start_v
                for _ in range(len(all_own_edges) + 2):
                    nexts = adj.get(id(current_v), [])
                    next_v = None
                    for nv in nexts:
                        if id(nv) not in seen_ids:
                            next_v = nv
                            break
                    if next_v is None:
                        break
                    graph_verts.append(next_v)
                    seen_ids.add(id(next_v))
                    current_v = next_v

                if len(graph_verts) >= 3 and len(graph_verts) >= len(simple_verts):
                    return graph_verts

            # Fallback: if we have orphans but < 3 total own edges,
            # try the old chain+orphan approach
            if orphan_edges and len(chain_edges) >= 2:
                all_edges = chain_edges + orphan_edges
                adj = {}
                for sv, ev in all_edges:
                    adj.setdefault(id(sv), []).append(ev)

                start_v = all_edges[0][0]
                graph_verts = [start_v]
                seen_ids = {id(start_v)}
                current_v = start_v
                for _ in range(len(all_edges) + 2):
                    nexts = adj.get(id(current_v), [])
                    next_v = None
                    for nv in nexts:
                        if id(nv) not in seen_ids:
                            next_v = nv
                            break
                    if next_v is None:
                        break
                    graph_verts.append(next_v)
                    seen_ids.add(id(next_v))
                    current_v = next_v

                if len(graph_verts) > len(simple_verts):
                    return graph_verts

        return simple_verts

    def _resolve_vertex_ref(self, ref):
        """Resolve a vertex reference, with fuzzy MFC map lookup."""
        if ref is None:
            return None
        if isinstance(ref, Vertex):
            return ref
        if not isinstance(ref, int):
            return None
        obj = self.arc.get_object(ref)
        if isinstance(obj, Vertex):
            return obj
        # MFC map drift: try nearby indices
        for offset in range(-15, 16):
            if offset == 0:
                continue
            obj = self.arc.get_object(ref + offset)
            if isinstance(obj, Vertex):
                return obj
        return None

    def _resolve_incomplete_edges(self):
        """Resolve incomplete CEdge dicts using fuzzy vertex ref lookup.

        After all parsing, some standalone CEdge dicts have raw vertex ref
        tags that couldn't be resolved during parsing due to MFC drift.
        Try fuzzy resolution now that all objects are registered.
        """
        resolved = 0
        for idx in range(self.arc.map_count + 100):
            obj = self.arc.get_object(idx)
            if not isinstance(obj, dict) or obj.get('type') != 'CEdge':
                continue
            if not obj.get('incomplete'):
                continue

            sv = obj.get('sv')
            ev = obj.get('ev')
            sv_raw = obj.get('sv_raw')
            ev_raw = obj.get('ev_raw')

            # Try to resolve using raw tags with fuzzy search
            if not isinstance(sv, Vertex) and isinstance(sv_raw, int):
                sv = self._resolve_vertex_ref(sv_raw)
            if not isinstance(ev, Vertex) and isinstance(ev_raw, int):
                ev = self._resolve_vertex_ref(ev_raw)

            if isinstance(sv, Vertex) and isinstance(ev, Vertex):
                edge = Edge(sv, ev, False, False, idx)
                self.model.edges.append(edge)
                self.arc.set_object(idx, edge)
                resolved += 1
            elif isinstance(sv, Vertex) or isinstance(ev, Vertex):
                # Partial resolution: store back for chain tracing
                obj['sv'] = sv if isinstance(sv, Vertex) else obj.get('sv')
                obj['ev'] = ev if isinstance(ev, Vertex) else obj.get('ev')
                obj['sv_obj'] = sv if isinstance(sv, Vertex) else None
                obj['ev_obj'] = ev if isinstance(ev, Vertex) else None

        if resolved:
            self.log(f"Resolved {resolved} incomplete CEdge dicts")

    def _reconstruct_faces(self):
        """
        Reconstruct face vertex lists from edge connectivity and face planes.
        Each face's vertices are determined by finding edges whose vertices
        lie on the face's plane, then ordering them into a polygon.
        Handles coplanar faces by finding distinct edge loops.
        """
        # First, try CEdgeUse-based reconstruction (v3 files)
        eu_assigned = self._reconstruct_faces_from_edgeuse()
        if eu_assigned:
            self.log(f"CEdgeUse chains assigned vertices to {eu_assigned} faces")

        # Post-EU validation: reject EU-assigned faces where any vertex
        # is far from the face's stored plane.  These faces will fall
        # through to heuristic reconstruction below.
        eu_reverted = 0
        for face in self.model.faces:
            if not face.vertices:
                continue
            nx, ny, nz = face.normal
            nl = math.sqrt(nx*nx + ny*ny + nz*nz)
            if nl < 1e-10:
                continue
            nx, ny, nz = nx/nl, ny/nl, nz/nl
            d = face.distance / nl
            max_dist = max(abs(nx*v.x + ny*v.y + nz*v.z + d)
                          for v in face.vertices)
            if max_dist > 0.5:
                face.vertices = []
                face.holes = []
                face._edge_uses = []
                face.eu_assigned = False
                eu_reverted += 1
                eu_assigned -= 1
        if eu_reverted:
            self.log(f"Reverted {eu_reverted} EU-assigned faces "
                    f"(vertices off-plane >0.5)")

        # Remove duplicate vertices from faces (same coordinates)
        dedup_count = 0
        for face in self.model.faces:
            if not face.vertices or len(face.vertices) < 3:
                continue
            seen_coords = []
            deduped = []
            for v in face.vertices:
                coord = (round(v.x, 6), round(v.y, 6), round(v.z, 6))
                if coord not in seen_coords:
                    seen_coords.append(coord)
                    deduped.append(v)
                else:
                    dedup_count += 1
            if len(deduped) < len(face.vertices):
                face.vertices = deduped
        if dedup_count:
            self.log(f"Removed {dedup_count} duplicate vertices from faces")

        # Supplement incomplete EU faces: for faces with fewer vertices
        # than EUs, find additional on-plane vertices reachable via
        # edges from the existing face vertices.
        if self.model.edges:
            self._supplement_incomplete_eu_faces()

        # Fix scrambled vertex order: when EU chains produce vertices in
        # wrong order (< 50% consecutive pairs edge-connected), reconstruct
        # the boundary by tracing edge loops.
        self._fix_scrambled_face_boundaries()

        if not self.model.edges or not self.model.faces:
            return

        # Group vertices and edges by scope for efficient lookup
        verts_by_scope = {}
        for v in self.model.vertices:
            verts_by_scope.setdefault(v.scope, []).append(v)
        edges_by_scope = {}
        for e in self.model.edges:
            if e.start_vertex:
                edges_by_scope.setdefault(e.start_vertex.scope, []).append(e)

        # Group faces by approximate plane for coplanar detection
        def plane_key(face):
            nx, ny, nz = face.normal
            d = face.distance
            nl = math.sqrt(nx*nx + ny*ny + nz*nz)
            if nl > 0:
                nx, ny, nz = nx/nl, ny/nl, nz/nl
            for c in (nx, ny, nz):
                if abs(c) > 1e-6:
                    if c < 0:
                        nx, ny, nz, d = -nx, -ny, -nz, -d
                    break
            return (round(nx, 3), round(ny, 3), round(nz, 3), round(d, 2))

        plane_groups = {}
        for face in self.model.faces:
            if face.vertices:
                continue
            nx, ny, nz = face.normal
            norm_len = math.sqrt(nx * nx + ny * ny + nz * nz)
            if norm_len < 1e-10:
                continue
            pk = plane_key(face)
            plane_groups.setdefault(pk, []).append(face)

        all_edges = [e for e in self.model.edges if e.start_vertex and e.end_vertex]

        for pk, faces in plane_groups.items():
            nx_n, ny_n, nz_n, d_n = pk

            # Find vertices on this plane (cascading tolerance)
            face_verts = []
            for v in self.model.vertices:
                dot = nx_n * v.x + ny_n * v.y + nz_n * v.z
                if abs(dot + d_n) < 0.1:
                    face_verts.append(v)

            if len(face_verts) < 3:
                face_verts = []
                for v in self.model.vertices:
                    dot = nx_n * v.x + ny_n * v.y + nz_n * v.z
                    if abs(dot + d_n) < 0.5:
                        face_verts.append(v)

            if len(face_verts) < 3 and len(faces) == 1:
                # For single faces, try nearest-N vertices to the plane
                face = faces[0]
                nx, ny, nz = face.normal
                d = face.distance
                scored = sorted([(abs(nx*v.x + ny*v.y + nz*v.z + d), id(v), v)
                                  for v in self.model.vertices])
                # Use 3-4 nearest if they're within a reasonable distance
                if len(scored) >= 3 and scored[2][0] < 10.0:
                    # Take vertices up to 2x the 3rd closest distance
                    threshold = max(scored[2][0] * 2.0, 0.5)
                    face_verts = [v for dist, _, v in scored if dist < threshold]
                    if len(face_verts) > 8:
                        face_verts = [v for _, _, v in scored[:4]]
                    face.vertices = self._convex_order(face_verts, face.normal)
                elif len(face_verts) >= 2 and len(self.model.vertices) <= 50:
                    # Small model: expand from on-plane verts via edge connectivity
                    on_plane_ids = set(id(v) for v in face_verts)
                    for e in all_edges:
                        sv, ev = e.start_vertex, e.end_vertex
                        if id(sv) in on_plane_ids and id(ev) not in on_plane_ids:
                            face_verts.append(ev)
                            on_plane_ids.add(id(ev))
                        elif id(ev) in on_plane_ids and id(sv) not in on_plane_ids:
                            face_verts.append(sv)
                            on_plane_ids.add(id(sv))
                    if len(face_verts) >= 3:
                        face.vertices = self._convex_order(face_verts, face.normal)
                elif len(scored) >= 3 and len(self.model.vertices) <= 20:
                    # Very small model: just use all vertices
                    face_verts = [v for _, _, v in scored[:min(len(scored), 8)]]
                    face.vertices = self._convex_order(face_verts, face.normal)
                continue

            if len(face_verts) < 3:
                continue

            vert_set = set(id(v) for v in face_verts)
            plane_edges = [e for e in all_edges
                           if id(e.start_vertex) in vert_set
                           and id(e.end_vertex) in vert_set]

            if len(faces) == 1:
                # Single face - simple matching
                face = faces[0]
                if len(face_verts) > 100:
                    continue
                if plane_edges:
                    ordered = self._order_vertices(face_verts, plane_edges)
                    if ordered and len(ordered) >= 3:
                        face.vertices = ordered
                        continue
                if len(face_verts) <= 50:
                    face.vertices = self._convex_order(face_verts, face.normal)
                continue

            # Multiple coplanar faces - try loop finding first
            if plane_edges and len(plane_edges) >= 3:
                loops = self._find_edge_loops(face_verts, plane_edges,
                                              faces[0].normal)
                loops = [l for l in loops if len(l) >= 3]
                loops.sort(key=len, reverse=True)
                if loops and len(loops) >= len(faces):
                    for i, face in enumerate(faces):
                        if i < len(loops):
                            face.vertices = loops[i]
                    continue
                elif loops:
                    # Assign available loops to faces (fewer loops than faces)
                    for i, face in enumerate(faces):
                        if i < len(loops):
                            face.vertices = loops[i]
                    if any(f.vertices for f in faces):
                        continue

            # Try connected components of on-plane edges
            if plane_edges and len(faces) > 1:
                adj = {}
                for e in plane_edges:
                    sid, eid = id(e.start_vertex), id(e.end_vertex)
                    adj.setdefault(sid, set()).add(eid)
                    adj.setdefault(eid, set()).add(sid)
                visited = set()
                components = []
                for v in face_verts:
                    vid = id(v)
                    if vid in visited or vid not in adj:
                        continue
                    comp = []
                    stack = [vid]
                    while stack:
                        n = stack.pop()
                        if n in visited:
                            continue
                        visited.add(n)
                        comp.append(n)
                        for nb in adj.get(n, []):
                            if nb not in visited:
                                stack.append(nb)
                    if len(comp) >= 3:
                        components.append(comp)
                if components:
                    vid_to_vert = {id(v): v for v in face_verts}
                    components.sort(key=len, reverse=True)
                    for i, face in enumerate(faces):
                        if i < len(components):
                            cverts = [vid_to_vert[vid] for vid in components[i]
                                      if vid in vid_to_vert]
                            if len(cverts) >= 3:
                                comp_edges = [e for e in plane_edges
                                              if id(e.start_vertex) in set(components[i])
                                              and id(e.end_vertex) in set(components[i])]
                                ordered = self._order_vertices(cverts, comp_edges)
                                if ordered and len(ordered) >= 3:
                                    face.vertices = ordered
                                else:
                                    face.vertices = self._convex_order(cverts,
                                                                       face.normal)
                    if any(f.vertices for f in faces):
                        continue

            # Spatial partitioning for large coplanar groups with insufficient edges
            remaining_faces = [f for f in faces if not f.vertices]
            if remaining_faces and len(remaining_faces) > 1 and len(face_verts) >= 6:
                # Project to 2D using two axes perpendicular to normal
                anx, any_, anz = abs(nx_n), abs(ny_n), abs(nz_n)
                if anx >= any_ and anx >= anz:
                    proj = [(v.y, v.z, v) for v in face_verts]
                elif any_ >= anx and any_ >= anz:
                    proj = [(v.x, v.z, v) for v in face_verts]
                else:
                    proj = [(v.x, v.y, v) for v in face_verts]
                if len(proj) >= 6:
                    # Sort by primary spread axis
                    us = [p[0] for p in proj]
                    vs = [p[1] for p in proj]
                    u_spread = max(us) - min(us)
                    v_spread = max(vs) - min(vs)
                    sort_axis = 0 if u_spread >= v_spread else 1
                    proj.sort(key=lambda p: p[sort_axis])
                    # Create triangle fan from sorted vertices
                    # Each face gets 3 consecutive vertices (with overlap)
                    n_faces = len(remaining_faces)
                    n_verts = len(proj)
                    assigned_spatial = 0
                    step = max(1, (n_verts - 2) // n_faces)
                    for fi, face in enumerate(remaining_faces):
                        idx = fi * step
                        if idx + 2 < n_verts:
                            tri_verts = [proj[idx][2], proj[idx+1][2], proj[idx+2][2]]
                            face.vertices = tri_verts
                            assigned_spatial += 1
                    if assigned_spatial > 0:
                        self.log(f"Spatial partition: {assigned_spatial} faces "
                                f"from {n_verts} verts on plane {pk}")
                        continue

            # Per-face matching with used_verts tracking
            used_verts = set()
            unassigned = [f for f in faces if not f.vertices]
            for fi, face in enumerate(unassigned):
                if face.vertices:
                    continue
                nx, ny, nz = face.normal
                d = face.distance
                fv = [v for v in self.model.vertices
                      if abs(nx*v.x + ny*v.y + nz*v.z + d) < 0.1
                      and id(v) not in used_verts]
                if len(fv) > 100:
                    fv = []
                if len(fv) < 3:
                    fv = [v for v in self.model.vertices
                          if abs(nx*v.x + ny*v.y + nz*v.z + d) < 0.5
                          and id(v) not in used_verts]
                    if len(fv) > 50:
                        fv = []
                if len(fv) < 3:
                    if fi == 0:
                        fv = [v for v in self.model.vertices
                              if abs(nx*v.x + ny*v.y + nz*v.z + d) < 0.1]
                        if len(fv) > 100:
                            fv = []
                    if len(fv) < 3:
                        continue
                fv_set = set(id(v) for v in fv)
                fe = [e for e in plane_edges
                      if id(e.start_vertex) in fv_set
                      and id(e.end_vertex) in fv_set]
                if fe:
                    ordered = self._order_vertices(fv, fe)
                    if ordered and len(ordered) >= 3:
                        face.vertices = ordered
                        for v in ordered:
                            used_verts.add(id(v))
                        continue
                if len(fv) <= 50:
                    face.vertices = self._convex_order(fv, face.normal)
                    for v in fv:
                        used_verts.add(id(v))

        # Global fallback: unassigned faces get vertices from ANY assigned face
        # on the same plane. Only for front/back pairs (1 unassigned per plane).
        # Don't duplicate for multi-face plane groups (creates overlapping geometry).
        still_unassigned = [f for f in self.model.faces
                            if not f.vertices or len(f.vertices) < 3]
        if still_unassigned:
            assigned_by_plane = {}
            for f in self.model.faces:
                if f.vertices and len(f.vertices) >= 3:
                    pk = plane_key(f)
                    if pk not in assigned_by_plane:
                        assigned_by_plane[pk] = f
            # Count unassigned per plane to avoid mass duplication
            from collections import Counter
            unassigned_plane_counts = Counter(plane_key(f) for f in still_unassigned)
            for face in still_unassigned:
                pk = plane_key(face)
                if pk in assigned_by_plane and unassigned_plane_counts[pk] <= 2:
                    face.vertices = list(assigned_by_plane[pk].vertices)


    def _remove_outlier_vertices(self):
        """Remove outlier vertices from faces assigned by heuristics.

        When EU chains fail (MFC drift in v5+), spatial partition assigns
        on-plane vertices to faces. Occasionally a vertex very far from
        the face centroid gets assigned, creating spikes/corruption.
        Remove vertices >3x the median distance from centroid.
        """
        removed_total = 0
        for fi, face in enumerate(self.model.faces):
            if not face.vertices or len(face.vertices) < 4:
                continue
            if getattr(face, 'eu_assigned', False):
                continue  # EU-assigned faces are correct
            verts = face.vertices
            cx = sum(v.x for v in verts) / len(verts)
            cy = sum(v.y for v in verts) / len(verts)
            cz = sum(v.z for v in verts) / len(verts)
            dists = [math.sqrt((v.x-cx)**2 + (v.y-cy)**2 + (v.z-cz)**2)
                     for v in verts]
            sorted_dists = sorted(dists)
            median_d = sorted_dists[len(sorted_dists) // 2]
            if median_d < 0.01:
                continue  # All vertices at same point
            threshold = max(median_d * 3.0, 1.0)
            outliers = [i for i, d in enumerate(dists) if d > threshold]
            if outliers:
                kept = [v for i, v in enumerate(verts) if i not in outliers]
                if len(kept) >= 3:
                    face.vertices = kept
                    removed_total += len(outliers)
                    self.log(f"Face[{fi}] map@{getattr(face, 'map_idx', '?')}: "
                            f"removed {len(outliers)} outlier vertices "
                            f"(threshold={threshold:.1f})")
        if removed_total:
            self.log(f"Removed {removed_total} outlier vertices total")

    def _reconstruct_multiloop_faces(self):
        """Reconstruct multi-loop faces (faces with holes) that EU chains
        couldn't resolve due to MFC drift.

        For faces with loop_count > 1 that are either unassigned or
        assigned without holes, find all on-plane vertices and use
        geometric analysis to identify outer boundary and rectangular
        hole cutouts.
        """
        reconstructed = 0
        for face in self.model.faces:
            if face.loop_count <= 1:
                continue
            # Skip faces that already have the correct number of holes
            expected_holes = face.loop_count - 1
            if face.holes and len(face.holes) >= expected_holes:
                continue

            # Face's plane
            nx, ny, nz = face.normal
            nl = math.sqrt(nx*nx + ny*ny + nz*nz)
            if nl < 1e-10:
                continue
            nx, ny, nz = nx/nl, ny/nl, nz/nl
            d = face.distance / nl

            # Find ALL on-plane vertices
            on_plane = []
            for v in self.model.vertices:
                if abs(nx*v.x + ny*v.y + nz*v.z + d) < 0.1:
                    on_plane.append(v)

            if len(on_plane) < 4:
                continue

            # Project to 2D for geometric analysis
            # Choose projection axes based on normal direction
            anx, any, anz = abs(nx), abs(ny), abs(nz)
            if anz >= anx and anz >= any:
                # Z-facing: project to XY
                def proj(v):
                    return (v.x, v.y)
            elif any >= anx:
                # Y-facing: project to XZ
                def proj(v):
                    return (v.x, v.z)
            else:
                # X-facing: project to YZ
                def proj(v):
                    return (v.y, v.z)

            # Find the outermost 4 vertices (bounding rectangle)
            coords = [(proj(v), v) for v in on_plane]
            xs = [c[0] for c, _ in coords]
            ys = [c[1] for c, _ in coords]
            xmin, xmax = min(xs), max(xs)
            ymin, ymax = min(ys), max(ys)

            # Outer loop: vertices AT the bounding rectangle edges
            # Use tight tolerance to avoid classifying inner vertices
            # near the boundary as outer
            # Classify vertices: on bbox edge = outer, else inner
            outer_tol = 0.5
            outer_verts = []
            inner_verts = []
            for (cx, cy), v in coords:
                on_edge = (abs(cx - xmin) < outer_tol or
                          abs(cx - xmax) < outer_tol or
                          abs(cy - ymin) < outer_tol or
                          abs(cy - ymax) < outer_tol)
                if on_edge:
                    outer_verts.append(v)
                else:
                    inner_verts.append(v)

            if len(outer_verts) < 4 or len(inner_verts) < 3:
                continue

            # Order outer loop
            outer_ordered = self._convex_order(outer_verts, face.normal)
            if not outer_ordered or len(outer_ordered) < 4:
                continue

            # Cluster inner vertices into rectangular holes
            # Group by spatial proximity using grid alignment
            # Use ALL on-plane vertices (not just inner) to detect holes
            # whose corners may sit on the outer boundary edge (sidelights)
            all_coords = [(proj(v), v) for v in on_plane]
            inner_coords = [(proj(v), v) for v in inner_verts]

            # Find unique Y values (rows) among inner vertices
            y_vals = sorted(set(round(cy, 1) for (cx, cy), _ in
                              inner_coords))
            # Find unique X values (columns)
            x_vals = sorted(set(round(cx, 1) for (cx, cy), _ in
                              inner_coords))

            # Also include outer vertex grid lines that are NOT the
            # bounding box extremes (sidelight divider positions)
            for (cx, cy), v in all_coords:
                rcx, rcy = round(cx, 1), round(cy, 1)
                rmin_x, rmax_x = round(xmin, 1), round(xmax, 1)
                rmin_y, rmax_y = round(ymin, 1), round(ymax, 1)
                if rcx != rmin_x and rcx != rmax_x and rcx not in x_vals:
                    x_vals.append(rcx)
                if rcy != rmin_y and rcy != rmax_y and rcy not in y_vals:
                    y_vals.append(rcy)
            x_vals = sorted(set(x_vals))
            y_vals = sorted(set(y_vals))

            # Group vertices into rectangular holes:
            # Each hole is defined by 4 corners at grid line intersections
            holes = []
            used = set()
            outer_ids = set(id(v) for v in outer_verts)
            # Try ALL x/y combinations (not just adjacent) to find
            # rectangles that span multiple grid cells (e.g. sidelights)
            # Start with adjacent pairs first (smaller holes), then
            # try non-adjacent for larger holes
            tried_rects = set()
            for xi in range(len(x_vals)):
                for xi2 in range(xi + 1, len(x_vals)):
                    for yi in range(len(y_vals)):
                        for yi2 in range(yi + 1, len(y_vals)):
                            x_lo, x_hi = x_vals[xi], x_vals[xi2]
                            y_lo, y_hi = y_vals[yi], y_vals[yi2]
                            rk = (x_lo, x_hi, y_lo, y_hi)
                            if rk in tried_rects:
                                continue
                            tried_rects.add(rk)
                            corners = []
                            for (cx, cy), v in all_coords:
                                rcx = round(cx, 1)
                                rcy = round(cy, 1)
                                if ((rcx == x_lo or rcx == x_hi) and
                                        (rcy == y_lo or rcy == y_hi)):
                                    if id(v) not in used:
                                        corners.append(v)
                            if len(corners) != 4:
                                continue
                            # Skip if all corners are outer boundary
                            inner_count = sum(
                                1 for v in corners
                                if id(v) not in outer_ids)
                            if inner_count == 0:
                                continue
                            # Skip if this rect contains a smaller hole
                            contained = False
                            for h in holes:
                                hxs = [proj(v)[0] for v in h]
                                hys = [proj(v)[1] for v in h]
                                if (min(hxs) >= x_lo - 0.1 and
                                        max(hxs) <= x_hi + 0.1 and
                                        min(hys) >= y_lo - 0.1 and
                                        max(hys) <= y_hi + 0.1):
                                    contained = True
                                    break
                            if contained:
                                continue
                            ordered = self._convex_order(
                                corners, face.normal)
                            if ordered and len(ordered) == 4:
                                holes.append(ordered)
                                for v in ordered:
                                    used.add(id(v))

            # Detect sidelight holes: windows that span the full
            # height and share edge vertices with the outer boundary.
            # Look for inner vertices that define divider columns
            # and create rectangles from outer edge to divider.
            if holes:
                outer_ids = set(id(v) for v in outer_verts)
                # Find inner x-columns that could be sidelight dividers
                inner_x_set = sorted(set(
                    round(proj(v)[0], 1) for v in inner_verts))
                rxmin_r = round(xmin, 1)
                rxmax_r = round(xmax, 1)
                # Dividers: inner x values between the known hole
                # x-range and the outer edge
                hole_xs = set()
                for h in holes:
                    for v in h:
                        hole_xs.add(round(proj(v)[0], 1))
                # Left divider: max inner x that is less than the
                # leftmost hole x
                if hole_xs:
                    left_hole_x = min(hole_xs)
                    right_hole_x = max(hole_xs)
                    left_dividers = [x for x in inner_x_set
                                     if x < left_hole_x - 0.5]
                    right_dividers = [x for x in inner_x_set
                                      if x > right_hole_x + 0.5]
                    for div_x, side in [(max(left_dividers)
                                         if left_dividers else None,
                                         'left'),
                                        (min(right_dividers)
                                         if right_dividers else None,
                                         'right')]:
                        if div_x is None:
                            continue
                        edge_x = rxmin_r if side == 'left' else rxmax_r
                        # Find y range for this sidelight from
                        # available vertices at divider x and edge x
                        div_ys = sorted(
                            round(proj(v)[1], 1) for v in on_plane
                            if abs(round(proj(v)[0], 1) - div_x) < 0.5)
                        edge_ys = sorted(
                            round(proj(v)[1], 1) for v in on_plane
                            if abs(round(proj(v)[0], 1) - edge_x) < 0.5)
                        if not div_ys or not edge_ys:
                            continue
                        # Sidelight spans from min shared y to max
                        y_lo = max(min(div_ys), min(edge_ys))
                        y_hi = min(max(div_ys), max(edge_ys))
                        if y_hi - y_lo < 1.0:
                            continue
                        x_lo = min(edge_x, div_x)
                        x_hi = max(edge_x, div_x)
                        corners = []
                        for tx, ty in [(x_lo, y_lo), (x_lo, y_hi),
                                       (x_hi, y_lo), (x_hi, y_hi)]:
                            for (cx, cy), v in all_coords:
                                if (abs(round(cx, 1) - tx) < 0.5 and
                                        abs(round(cy, 1) - ty) < 0.5 and
                                        id(v) not in used):
                                    corners.append(v)
                                    break
                        if len(corners) == 4:
                            ordered = self._convex_order(
                                corners, face.normal)
                            if ordered and len(ordered) == 4:
                                holes.append(ordered)
                                for v in ordered:
                                    used.add(id(v))

            if not holes:
                continue

            # Check if any holes share vertices with the outer boundary.
            # If so, rebuild outer as simple bbox rectangle to avoid
            # degenerate bridge-edge triangulation.
            outer_ids = set(id(v) for v in outer_ordered)
            sidelight_detected = False
            for h in holes:
                shared = sum(1 for v in h if id(v) in outer_ids)
                if shared >= 2:
                    sidelight_detected = True
                    break
            if sidelight_detected:
                # Use 4 bbox corner vertices as outer boundary
                corner_tol = 0.5
                bbox_corners = [(xmin, ymin), (xmin, ymax),
                                (xmax, ymax), (xmax, ymin)]
                bbox_verts = []
                matched = set()
                for bx, by in bbox_corners:
                    for (cx, cy), v in coords:
                        if (abs(cx - bx) < corner_tol and
                                abs(cy - by) < corner_tol and
                                id(v) not in matched):
                            bbox_verts.append(v)
                            matched.add(id(v))
                            break
                if len(bbox_verts) == 4:
                    outer_ordered = self._convex_order(
                        bbox_verts, face.normal)

            face.vertices = outer_ordered
            face.holes = holes
            reconstructed += 1
            self.log(f"Face[{face.map_idx}]: reconstructed multi-loop "
                    f"with {len(outer_ordered)} outer + "
                    f"{len(holes)} holes")

        if reconstructed:
            self.log(f"Reconstructed {reconstructed} multi-loop faces")

    def _remove_hole_blocking_faces(self):
        """Remove heuristic-assigned faces that block multi-loop face holes.

        When EU chains can't assign vertices (MFC drift), the spatial partition
        heuristic assigns whatever on-plane vertices it finds. This can produce
        opaque triangles between front/back panels that cover the window
        openings (holes) of multi-loop faces on nearby parallel planes.

        Only checks faces in the SAME scope as the multi-loop face, since
        different scopes will be transformed to different world positions.
        """
        # Find multi-loop faces with holes
        hole_faces = []
        for fi, face in enumerate(self.model.faces):
            if not face.holes or not face.vertices:
                continue
            nx, ny, nz = face.normal
            nl = math.sqrt(nx*nx + ny*ny + nz*nz)
            if nl < 1e-10:
                continue
            face_scope = face.scope
            # Get the plane's dominant axis and position
            anx, any_, anz = abs(nx/nl), abs(ny/nl), abs(nz/nl)
            if anz >= anx and anz >= any_:
                axis = 2  # z-axis normal
                pos = face.vertices[0].z
            elif any_ >= anx:
                axis = 1  # y-axis normal
                pos = face.vertices[0].y
            else:
                axis = 0  # x-axis normal
                pos = face.vertices[0].x
            # Collect hole bounding boxes in the face's 2D plane
            hole_bboxes = []
            for hole in face.holes:
                if axis == 2:
                    coords = [(v.x, v.y) for v in hole]
                elif axis == 1:
                    coords = [(v.x, v.z) for v in hole]
                else:
                    coords = [(v.y, v.z) for v in hole]
                min_u = min(c[0] for c in coords)
                max_u = max(c[0] for c in coords)
                min_v = min(c[1] for c in coords)
                max_v = max(c[1] for c in coords)
                hole_bboxes.append((min_u, max_u, min_v, max_v))
            hole_faces.append((axis, pos, hole_bboxes, face_scope))

        if not hole_faces:
            return

        # Track which planes had faces removed
        removed_planes = set()  # (scope, axis, rounded_pos)
        removed = 0
        for fi, face in enumerate(self.model.faces):
            if not face.vertices or len(face.vertices) < 3:
                continue
            if face.holes:
                continue
            # Protect faces with transparent material (glass panes)
            if face.material_idx >= 0 and face.material_idx < len(self.model.materials):
                mat = self.model.materials[face.material_idx]
                if mat.opacity < 1.0:
                    continue  # Glass face — keep it
            # Check if this face is on a parallel plane near a hole face
            for axis, hole_pos, hole_bboxes, hole_scope in hole_faces:
                # Only compare faces in the same scope
                if face.scope != hole_scope:
                    continue
                if axis == 2:
                    face_pos = face.vertices[0].z
                    if not all(abs(v.z - face_pos) < 0.1 for v in face.vertices):
                        continue
                    coords = [(v.x, v.y) for v in face.vertices]
                elif axis == 1:
                    face_pos = face.vertices[0].y
                    if not all(abs(v.y - face_pos) < 0.1 for v in face.vertices):
                        continue
                    coords = [(v.x, v.z) for v in face.vertices]
                else:
                    face_pos = face.vertices[0].x
                    if not all(abs(v.x - face_pos) < 0.1 for v in face.vertices):
                        continue
                    coords = [(v.y, v.z) for v in face.vertices]
                # Within ±5 units of the hole face plane?
                if abs(face_pos - hole_pos) > 5.0:
                    continue
                if abs(face_pos - hole_pos) < 0.01:
                    continue  # Same plane — don't remove
                # Check overlap with any hole
                f_min_u = min(c[0] for c in coords)
                f_max_u = max(c[0] for c in coords)
                f_min_v = min(c[1] for c in coords)
                f_max_v = max(c[1] for c in coords)
                for h_min_u, h_max_u, h_min_v, h_max_v in hole_bboxes:
                    # Check bounding box overlap
                    if (f_min_u < h_max_u and f_max_u > h_min_u and
                            f_min_v < h_max_v and f_max_v > h_min_v):
                        # This face overlaps a hole — remove it
                        rp = round(face_pos, 1)
                        removed_planes.add((hole_scope, axis, rp))
                        self.log(f"Removed Face[{fi}] map@"
                                f"{getattr(face, 'map_idx', '?')}: "
                                f"blocks hole in multi-loop face")
                        face.vertices = []
                        face.holes = []
                        removed += 1
                        break
                if not face.vertices:
                    break

        if removed:
            self.log(f"Removed {removed} faces blocking multi-loop holes")

        # Second pass: remove other heuristic faces on the same planes
        # where we already removed blocking faces. These are spurious
        # triangles that don't overlap a hole bbox but sit on the same
        # intermediate plane (e.g., z=-4 between front z=0 and back z=-5).
        if removed_planes:
            removed2 = 0
            for fi, face in enumerate(self.model.faces):
                if not face.vertices or len(face.vertices) < 3:
                    continue
                if face.holes:
                    continue
                if face.material_idx >= 0:
                    continue  # Has material — likely legitimate
                if getattr(face, 'eu_assigned', False):
                    continue  # EU-assigned — legitimate
                for scope, axis, rp in removed_planes:
                    if face.scope != scope:
                        continue
                    if axis == 2:
                        fp = face.vertices[0].z
                        if not all(abs(v.z - fp) < 0.1
                                   for v in face.vertices):
                            continue
                    elif axis == 1:
                        fp = face.vertices[0].y
                        if not all(abs(v.y - fp) < 0.1
                                   for v in face.vertices):
                            continue
                    else:
                        fp = face.vertices[0].x
                        if not all(abs(v.x - fp) < 0.1
                                   for v in face.vertices):
                            continue
                    if abs(round(fp, 1) - rp) < 0.2:
                        self.log(f"Removed Face[{fi}] map@"
                                f"{getattr(face, 'map_idx', '?')}: "
                                f"heuristic face on blocked plane")
                        face.vertices = []
                        face.holes = []
                        removed2 += 1
                        break
            if removed2:
                self.log(f"Removed {removed2} heuristic faces on "
                        f"blocked planes")

    def _fill_glass_pane_faces(self):
        """Fill empty faces that share a plane with multi-loop face holes.

        Glass pane faces in the SKP file share the same plane as the
        back panel (z=-5) and should have geometry matching the hole
        rectangles. When EU chains fail (MFC drift), assign hole vertices.
        """
        # Find multi-loop faces and their holes by plane
        for fi, face in enumerate(self.model.faces):
            if not face.holes or not face.vertices:
                continue
            nx, ny, nz = face.normal
            nl = math.sqrt(nx*nx + ny*ny + nz*nz)
            if nl < 1e-10:
                continue
            nx, ny, nz = nx/nl, ny/nl, nz/nl
            fd = face.distance / nl

            # Find empty faces on the same plane
            for gi, gface in enumerate(self.model.faces):
                if gface.vertices and len(gface.vertices) >= 3:
                    continue
                if gface.loop_count != 1:
                    continue
                gnx, gny, gnz = gface.normal
                gnl = math.sqrt(gnx*gnx + gny*gny + gnz*gnz)
                if gnl < 1e-10:
                    continue
                gnx, gny, gnz = gnx/gnl, gny/gnl, gnz/gnl
                gd = gface.distance / gnl
                # Same plane? (parallel normals, same distance)
                dot = abs(nx*gnx + ny*gny + nz*gnz)
                if dot < 0.99 or abs(fd - gd) > 0.1:
                    continue
                # This empty face is on the same plane as the hole face.
                # Try to match it to an unassigned hole.
                for hole in face.holes:
                    # Check if any other face already uses these hole verts
                    hole_coords = set(
                        (round(v.x, 4), round(v.y, 4), round(v.z, 4))
                        for v in hole)
                    already_used = False
                    for of in self.model.faces:
                        if of is gface or not of.vertices:
                            continue
                        of_coords = set(
                            (round(v.x, 4), round(v.y, 4), round(v.z, 4))
                            for v in of.vertices)
                        if hole_coords <= of_coords:
                            already_used = True
                            break
                    if already_used:
                        continue
                    # Assign hole vertices to this face
                    gface.vertices = list(hole)
                    self.log(f"Filled glass pane Face[{gi}] map@"
                            f"{getattr(gface, 'map_idx', '?')} "
                            f"with {len(hole)} hole vertices")
                    break

    def _infer_missing_faces(self):
        """Infer missing faces from edge and face connectivity.

        Three strategies:
        0. Closed edge loops: coplanar vertices all with degree 2 form a polygon face.
        1. Edge-complete triangles: 3 vertices connected by 3 edges with no face.
        2. Face-gap filling: for each edge (A,B), if both A and B appear in
           existing faces that share a common vertex C, and no face covers
           {A,B,C}, create the missing triangle. This handles cases like cones
           where not all triangle edges are explicit CEdge objects.
        """
        if len(self.model.edges) < 3:
            return

        # Skip if all faces already have geometry assigned
        faces_without_geo = sum(1 for f in self.model.faces
                                if not f.vertices or len(f.vertices) < 3)
        if faces_without_geo == 0 and self.model.faces:
            return

        all_edges = [(e.start_vertex, e.end_vertex) for e in self.model.edges
                     if e.start_vertex and e.end_vertex]
        if not all_edges:
            return

        # Strategy 0: closed edge loops forming polygon faces
        # When there are no faces, look for closed loops of degree-2 vertices
        if not self.model.faces:
            self._infer_loop_faces(all_edges)

        # Build edge adjacency: vertex_id -> set of edge-connected vertex_ids
        adj = {}
        edge_set = set()
        for sv, ev in all_edges:
            sid, eid = id(sv), id(ev)
            adj.setdefault(sid, set()).add(eid)
            adj.setdefault(eid, set()).add(sid)
            edge_set.add((min(sid, eid), max(sid, eid)))

        # Build face adjacency: vertex_id -> set of face-neighbor vertex_ids
        face_neighbors = {}  # vid -> set of vids that share a face
        for face in self.model.faces:
            if face.vertices and len(face.vertices) >= 3:
                vids = [id(v) for v in face.vertices]
                for vid in vids:
                    face_neighbors.setdefault(vid, set()).update(
                        v for v in vids if v != vid)

        # Collect existing face vertex sets to avoid duplicates
        existing = set()
        # Also track which faces each vertex belongs to (for coplanarity check)
        vert_faces = {}  # vid -> set of face indices
        for fi, face in enumerate(self.model.faces):
            if face.vertices and len(face.vertices) >= 3:
                vids = tuple(sorted(id(v) for v in face.vertices))
                existing.add(vids)
                for vid in (id(v) for v in face.vertices):
                    vert_faces.setdefault(vid, set()).add(fi)

        vid_to_vert = {}
        for v in self.model.vertices:
            vid_to_vert[id(v)] = v
        for e in self.model.edges:
            if e.start_vertex:
                vid_to_vert[id(e.start_vertex)] = e.start_vertex
            if e.end_vertex:
                vid_to_vert[id(e.end_vertex)] = e.end_vertex

        # Build set of existing face planes for coplanarity check
        existing_planes = []  # (nx, ny, nz, d) for each face with geometry
        for face in self.model.faces:
            if face.vertices and len(face.vertices) >= 3:
                fnx, fny, fnz = face.normal
                fnl = math.sqrt(fnx*fnx + fny*fny + fnz*fnz)
                if fnl > 1e-10:
                    existing_planes.append(
                        (fnx/fnl, fny/fnl, fnz/fnl, face.distance/fnl))

        new_faces = []
        seen_tris = set()

        def _try_add_face(a, b, c):
            tri = tuple(sorted([a, b, c]))
            if tri in seen_tris or tri in existing:
                return
            # Skip if all 3 verts belong to the same existing face (redundant)
            common_faces = (vert_faces.get(a, set()) &
                            vert_faces.get(b, set()) &
                            vert_faces.get(c, set()))
            if common_faces:
                return
            seen_tris.add(tri)
            va, vb, vc = vid_to_vert[a], vid_to_vert[b], vid_to_vert[c]
            e1 = (vb.x - va.x, vb.y - va.y, vb.z - va.z)
            e2 = (vc.x - va.x, vc.y - va.y, vc.z - va.z)
            nx = e1[1]*e2[2] - e1[2]*e2[1]
            ny = e1[2]*e2[0] - e1[0]*e2[2]
            nz = e1[0]*e2[1] - e1[1]*e2[0]
            nl = math.sqrt(nx*nx + ny*ny + nz*nz)
            if nl > 1e-10:
                nx, ny, nz = nx/nl, ny/nl, nz/nl
                d = -(nx*va.x + ny*va.y + nz*va.z)
                # Check that all 3 vertices lie on an existing face plane.
                # This prevents creating diagonal triangles spanning
                # different z-planes (e.g., covering window openings).
                on_existing = False
                for epnx, epny, epnz, epd in existing_planes:
                    dists = [abs(epnx*v.x + epny*v.y + epnz*v.z + epd)
                             for v in (va, vb, vc)]
                    if max(dists) < 0.5:
                        on_existing = True
                        break
                if not on_existing:
                    return
                face = Face((nx, ny, nz), d, scope=va.scope)
                face.vertices = [va, vb, vc]
                new_faces.append(face)

        # Strategy 1: edge-complete triangles
        for sv, ev in all_edges:
            a, b = id(sv), id(ev)
            common = adj.get(a, set()) & adj.get(b, set())
            for c in common:
                ab = (min(a, b), max(a, b))
                bc = (min(b, c), max(b, c))
                ac = (min(a, c), max(a, c))
                if ab in edge_set and bc in edge_set and ac in edge_set:
                    _try_add_face(a, b, c)

        # Strategy 2: face-gap filling (only for small models with clear gaps)
        # Only apply when edges <= 50 and faces are clearly missing
        faces_with_geo = sum(1 for f in self.model.faces
                             if f.vertices and len(f.vertices) >= 3)
        if len(all_edges) <= 50 and faces_with_geo < len(all_edges):
            # Count how many existing faces use each edge (adjacent pairs only)
            edge_face_count = {}
            for face in self.model.faces:
                if face.vertices and len(face.vertices) >= 3:
                    fvids = [id(v) for v in face.vertices]
                    n = len(fvids)
                    for i in range(n):
                        a2, b2 = fvids[i], fvids[(i + 1) % n]
                        ek = (min(a2, b2), max(a2, b2))
                        edge_face_count[ek] = edge_face_count.get(ek, 0) + 1

            for sv, ev in all_edges:
                a, b = id(sv), id(ev)
                ek = (min(a, b), max(a, b))
                if edge_face_count.get(ek, 0) >= 2:
                    continue  # Already has 2 faces, no gap
                fn_a = face_neighbors.get(a, set())
                fn_b = face_neighbors.get(b, set())
                common_face_verts = fn_a & fn_b
                for c in common_face_verts:
                    if c != a and c != b and c in vid_to_vert:
                        _try_add_face(a, b, c)

        if new_faces:
            self.model.faces.extend(new_faces)
            self.log(f"Inferred {len(new_faces)} missing faces from edge/face connectivity")

    def _infer_loop_faces(self, all_edges):
        """Create polygon faces from closed edge loops where all vertices have degree 2.
        Handles 2D silhouettes and outlines that form closed polygons without explicit faces."""
        # Build adjacency
        adj = {}
        vid_to_vert = {}
        for sv, ev in all_edges:
            sid, eid = id(sv), id(ev)
            adj.setdefault(sid, []).append(eid)
            adj.setdefault(eid, []).append(sid)
            vid_to_vert[sid] = sv
            vid_to_vert[eid] = ev

        # Find connected components where all vertices have degree 2
        visited = set()
        for start_vid in adj:
            if start_vid in visited:
                continue
            # Trace the loop
            loop = []
            current = start_vid
            prev = None
            is_loop = True
            while True:
                if current in visited:
                    # Check if we closed the loop back to start
                    if current == start_vid and len(loop) >= 3:
                        break
                    is_loop = False
                    break
                neighbors = adj.get(current, [])
                if len(neighbors) != 2:
                    is_loop = False
                    break
                visited.add(current)
                loop.append(current)
                # Go to next unvisited neighbor
                next_vid = neighbors[0] if neighbors[1] == prev else neighbors[1]
                prev = current
                current = next_vid

            if not is_loop or len(loop) < 3:
                continue

            # Check coplanarity: compute normal from first 3 vertices
            verts = [vid_to_vert[vid] for vid in loop]
            v0, v1, v2 = verts[0], verts[1], verts[2]
            e1 = (v1.x - v0.x, v1.y - v0.y, v1.z - v0.z)
            e2 = (v2.x - v0.x, v2.y - v0.y, v2.z - v0.z)
            nx = e1[1]*e2[2] - e1[2]*e2[1]
            ny = e1[2]*e2[0] - e1[0]*e2[2]
            nz = e1[0]*e2[1] - e1[1]*e2[0]
            nl = math.sqrt(nx*nx + ny*ny + nz*nz)
            if nl < 1e-10:
                continue
            nx, ny, nz = nx/nl, ny/nl, nz/nl
            d = -(nx*v0.x + ny*v0.y + nz*v0.z)

            # Verify all vertices are on the plane
            coplanar = all(abs(nx*v.x + ny*v.y + nz*v.z + d) < 0.1 for v in verts)
            if not coplanar:
                continue

            face = Face((nx, ny, nz), d, scope=verts[0].scope)
            face.vertices = verts
            self.model.faces.append(face)
            self.log(f"Inferred polygon face from {len(verts)}-vertex edge loop")

    def _find_edge_loops(self, verts, edges, normal):
        """Find minimal closed loops in a planar edge graph.
        Uses angular ordering to find face boundaries."""
        # Build adjacency with angular ordering
        adj = {}
        for e in edges:
            sid = id(e.start_vertex)
            eid = id(e.end_vertex)
            adj.setdefault(sid, []).append(e.end_vertex)
            adj.setdefault(eid, []).append(e.start_vertex)

        vid_to_vert = {id(v): v for v in verts}

        # For planar graph face finding, sort neighbors by angle
        nx, ny, nz = normal
        nl = math.sqrt(nx*nx + ny*ny + nz*nz)
        if nl > 0:
            nx, ny, nz = nx/nl, ny/nl, nz/nl

        # Create local 2D coordinate system
        if abs(nx) < 0.9:
            ref = (1, 0, 0)
        else:
            ref = (0, 1, 0)
        ux = ref[1]*nz - ref[2]*ny
        uy = ref[2]*nx - ref[0]*nz
        uz = ref[0]*ny - ref[1]*nx
        ul = math.sqrt(ux*ux + uy*uy + uz*uz)
        if ul > 0:
            ux, uy, uz = ux/ul, uy/ul, uz/ul
        vx = ny*uz - nz*uy
        vy = nz*ux - nx*uz
        vz = nx*uy - ny*ux

        def proj2d(v):
            return (v.x*ux + v.y*uy + v.z*uz, v.x*vx + v.y*vy + v.z*vz)

        # Sort neighbors of each vertex by angle
        sorted_adj = {}
        for vid, neighbors in adj.items():
            if vid not in vid_to_vert:
                continue
            v = vid_to_vert[vid]
            vp = proj2d(v)
            angles = []
            for n in neighbors:
                np = proj2d(n)
                angle = math.atan2(np[1] - vp[1], np[0] - vp[0])
                angles.append((angle, id(n), n))
            angles.sort(key=lambda x: x[0])
            sorted_adj[vid] = [n for _, _, n in angles]

        # Find minimal loops using "next edge CCW" rule
        used_half_edges = set()  # (from_vid, to_vid)
        loops = []

        for e in edges:
            for sv, ev in [(e.start_vertex, e.end_vertex), (e.end_vertex, e.start_vertex)]:
                he = (id(sv), id(ev))
                if he in used_half_edges:
                    continue

                # Trace a loop
                loop = [sv]
                cur_from = sv
                cur_to = ev
                used_half_edges.add((id(cur_from), id(cur_to)))
                loop.append(cur_to)

                max_steps = len(verts) + 2
                for _ in range(max_steps):
                    if id(cur_to) == id(loop[0]):
                        break
                    # Find next edge: the one immediately CW from the incoming direction
                    nbrs = sorted_adj.get(id(cur_to), [])
                    if not nbrs:
                        break
                    # Find cur_from in the sorted neighbor list
                    from_idx = -1
                    for i, n in enumerate(nbrs):
                        if id(n) == id(cur_from):
                            from_idx = i
                            break
                    if from_idx < 0:
                        break
                    # Next edge is the one BEFORE cur_from in CCW order (i.e., CW next)
                    next_idx = (from_idx - 1) % len(nbrs)
                    next_vert = nbrs[next_idx]
                    he2 = (id(cur_to), id(next_vert))
                    if he2 in used_half_edges:
                        break
                    used_half_edges.add(he2)
                    cur_from = cur_to
                    cur_to = next_vert
                    if id(cur_to) != id(loop[0]):
                        loop.append(cur_to)
                else:
                    continue

                if len(loop) >= 3 and id(cur_to) == id(loop[0]):
                    loops.append(loop)

        return loops

    def _order_vertices(self, verts, edges):
        """Order vertices into a polygon by following connected edges."""
        if not edges:
            return None

        # Build adjacency
        adj = {}
        for e in edges:
            sid = id(e.start_vertex)
            eid = id(e.end_vertex)
            adj.setdefault(sid, []).append(e.end_vertex)
            adj.setdefault(eid, []).append(e.start_vertex)

        # Find a vertex with exactly 2 neighbors (typical for polygon boundary)
        start = None
        for v in verts:
            if len(adj.get(id(v), [])) == 2:
                start = v
                break
        if not start:
            start = verts[0]

        # Trace the polygon
        ordered = [start]
        visited = {id(start)}
        current = start
        while True:
            neighbors = adj.get(id(current), [])
            found = False
            for n in neighbors:
                if id(n) not in visited:
                    ordered.append(n)
                    visited.add(id(n))
                    current = n
                    found = True
                    break
            if not found:
                break

        return ordered if len(ordered) >= 3 else None

    def _cluster_vertices(self, verts, k, normal):
        """Cluster vertices into k groups using spatial proximity.
        Projects onto the face plane for 2D clustering."""
        if len(verts) < 3 * k:
            return None

        # Project vertices onto plane for 2D clustering
        nx, ny, nz = normal
        nl = math.sqrt(nx*nx + ny*ny + nz*nz)
        if nl > 0:
            nx, ny, nz = nx/nl, ny/nl, nz/nl

        # Build 2D basis on the plane
        if abs(nx) < 0.9:
            up = (1, 0, 0)
        else:
            up = (0, 1, 0)
        ux = up[1]*nz - up[2]*ny, up[2]*nx - up[0]*nz, up[0]*ny - up[1]*nx
        ul = math.sqrt(ux[0]**2 + ux[1]**2 + ux[2]**2)
        if ul < 1e-10:
            return None
        ux = (ux[0]/ul, ux[1]/ul, ux[2]/ul)
        uy = (ny*ux[2]-nz*ux[1], nz*ux[0]-nx*ux[2], nx*ux[1]-ny*ux[0])

        # Project vertices to 2D
        pts = []
        for v in verts:
            px = v.x*ux[0] + v.y*ux[1] + v.z*ux[2]
            py = v.x*uy[0] + v.y*uy[1] + v.z*uy[2]
            pts.append((px, py))

        # Simple k-means clustering
        # Initialize centroids using vertices spread apart
        centroids = [pts[0]]
        for _ in range(1, k):
            # Pick point furthest from all existing centroids
            best_d = -1
            best_i = 0
            for i, (px, py) in enumerate(pts):
                min_d = min((px-cx)**2 + (py-cy)**2
                           for cx, cy in centroids)
                if min_d > best_d:
                    best_d = min_d
                    best_i = i
            centroids.append(pts[best_i])

        # Run a few iterations of k-means
        for _ in range(10):
            # Assign points to nearest centroid
            clusters = [[] for _ in range(k)]
            for i, (px, py) in enumerate(pts):
                best_c = 0
                best_d = float('inf')
                for c, (cx, cy) in enumerate(centroids):
                    d = (px-cx)**2 + (py-cy)**2
                    if d < best_d:
                        best_d = d
                        best_c = c
                clusters[best_c].append(i)

            # Update centroids
            new_centroids = []
            for c in range(k):
                if clusters[c]:
                    cx = sum(pts[i][0] for i in clusters[c]) / len(clusters[c])
                    cy = sum(pts[i][1] for i in clusters[c]) / len(clusters[c])
                    new_centroids.append((cx, cy))
                else:
                    new_centroids.append(centroids[c])
            centroids = new_centroids

        # Convert cluster indices back to vertex lists
        result = []
        for c in range(k):
            cverts = [verts[i] for i in clusters[c]]
            result.append(cverts)

        # Sort clusters by size (largest first)
        result.sort(key=len, reverse=True)
        return result

    def _convex_order(self, verts, normal):
        """Order vertices by angle around centroid projected onto face plane."""
        if len(verts) < 3:
            return verts

        # Centroid
        cx = sum(v.x for v in verts) / len(verts)
        cy = sum(v.y for v in verts) / len(verts)
        cz = sum(v.z for v in verts) / len(verts)

        nx, ny, nz = normal
        norm_len = math.sqrt(nx * nx + ny * ny + nz * nz)
        if norm_len < 1e-10:
            return verts
        nx /= norm_len
        ny /= norm_len
        nz /= norm_len

        # Create local 2D coordinate system on the face plane
        # Find a vector not parallel to normal
        if abs(nx) < 0.9:
            ref = (1, 0, 0)
        else:
            ref = (0, 1, 0)

        # u = normalize(ref cross normal)
        ux = ref[1] * nz - ref[2] * ny
        uy = ref[2] * nx - ref[0] * nz
        uz = ref[0] * ny - ref[1] * nx
        u_len = math.sqrt(ux * ux + uy * uy + uz * uz)
        if u_len < 1e-10:
            return verts
        ux /= u_len
        uy /= u_len
        uz /= u_len

        # v = normal cross u
        vx = ny * uz - nz * uy
        vy = nz * ux - nx * uz
        vz = nx * uy - ny * ux

        # Project and sort by angle
        def angle_key(vert):
            dx = vert.x - cx
            dy = vert.y - cy
            dz = vert.z - cz
            proj_u = dx * ux + dy * uy + dz * uz
            proj_v = dx * vx + dy * vy + dz * vz
            return math.atan2(proj_v, proj_u)

        return sorted(verts, key=angle_key)


def parse_skp(filepath, verbose=False):
    """Parse an SKP file and return an SKPModel."""
    parser = SKPParser(verbose=verbose)
    return parser.parse(filepath)


# ============================================================================
# GLB Converter — SketchUp-specific GLB output
# ============================================================================

# SketchUp uses inches internally; glTF uses meters
INCHES_TO_METERS = 0.0254


def convert_to_glb(model, output_path, verbose=False):
    """Convert an SKPModel to a GLB file."""
    builder = SKPGLBBuilder(model, verbose)
    glb_data = builder.build()

    with open(output_path, 'wb') as f:
        f.write(glb_data)

    if verbose:
        print(f"[GLB] Wrote {len(glb_data)} bytes to {output_path}",
              file=sys.stderr)


class SKPGLBBuilder(GLBBuilder):
    """Builds a GLB file from SKP model data.

    Extends the generic GLBBuilder with SketchUp-specific logic:
      - SKP Z-up → glTF Y-up coordinate conversion
      - SKP material color scaling for PBR
      - Mesh instancing for CComponentInstances and CGroups
      - SKP 13-double transform → glTF 4x4 column-major matrix
    """

    def __init__(self, model, verbose=False):
        super().__init__(verbose)
        self.model = model
        self._def_mesh_map = {}   # def_ref -> mesh index
        self._group_mesh_map = {}  # scope_num -> mesh index

    def build(self):
        """Build the complete GLB binary."""
        self._build_materials()
        self._build_meshes()
        self._build_nodes()
        return self.build_glb(generator="poly2glb - SketchUp Converter")

    def _build_materials(self):
        """Build glTF materials from SKP materials."""
        if not self.model.materials:
            self._default_mat_idx = 0
            self.materials_gltf.append({
                "name": "default",
                "pbrMetallicRoughness": {
                    "baseColorFactor": [0.4, 0.4, 0.4, 1.0],
                    "metallicFactor": 0.0,
                    "roughnessFactor": 0.5
                },
                "doubleSided": True
            })
            return

        for mat in self.model.materials:
            r, g, b, a = mat.color
            # SketchUp colors are sRGB; scale by 0.4 for correct PBR appearance
            COLOR_SCALE = 0.4
            alpha = mat.opacity
            gltf_mat = {
                "name": mat.name or "material",
                "pbrMetallicRoughness": {
                    "baseColorFactor": [
                        r / 255.0 * COLOR_SCALE,
                        g / 255.0 * COLOR_SCALE,
                        b / 255.0 * COLOR_SCALE,
                        alpha
                    ],
                    "metallicFactor": 0.0,
                    "roughnessFactor": 0.5
                },
                "doubleSided": True
            }

            # Handle texture
            if mat.has_texture and mat.texture_data:
                img_idx = self.add_image_from_data(mat.texture_data)
                tex_idx = self.add_texture(img_idx)

                # When texture is present, use white baseColorFactor
                gltf_mat["pbrMetallicRoughness"]["baseColorFactor"] = [
                    1.0, 1.0, 1.0, alpha]
                gltf_mat["pbrMetallicRoughness"]["baseColorTexture"] = {
                    "index": tex_idx
                }

            if alpha < 1.0:
                gltf_mat["alphaMode"] = "BLEND"

            self.materials_gltf.append(gltf_mat)

        # Add a default material for faces with no material assignment
        self._default_mat_idx = len(self.materials_gltf)
        self.materials_gltf.append({
            "name": "default",
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.4, 0.4, 0.4, 1.0],
                "metallicFactor": 0.0,
                "roughnessFactor": 0.5
            },
            "doubleSided": True
        })

    def _build_meshes(self):
        """Build glTF meshes from SKP faces."""
        faces = self.model.faces
        if not faces:
            self.log("No faces to export")
            return

        # Identify faces belonging to instanced definitions or transformed groups
        separated_face_indices = set()
        self._def_mesh_map = {}
        self._group_mesh_map = {}

        for def_ref, face_indices in self.model.def_face_ranges.items():
            if def_ref in self.model.ci_transforms:
                if isinstance(face_indices, (list, set)):
                    separated_face_indices.update(face_indices)
                else:
                    f_start, f_end = face_indices
                    for i in range(f_start, f_end):
                        separated_face_indices.add(i)

        for scope_num, (f_start, f_end) in self.model.group_face_ranges.items():
            for i in range(f_start, f_end):
                separated_face_indices.add(i)

        # Build root mesh from non-separated faces
        root_faces = []
        for i, face in enumerate(faces):
            if i not in separated_face_indices:
                if face.vertices and len(face.vertices) >= 3:
                    root_faces.append(face)

        if root_faces:
            root_prims = self._build_primitives_for_faces(root_faces)
            if root_prims:
                self.meshes.append({
                    "name": "SketchUpModel",
                    "primitives": root_prims
                })

        # Build separate meshes for each instanced definition
        for def_ref in sorted(self.model.ci_transforms.keys()):
            if def_ref not in self.model.def_face_ranges:
                continue
            face_indices = self.model.def_face_ranges[def_ref]
            if isinstance(face_indices, (list, set)):
                idx_iter = face_indices
            else:
                idx_iter = range(face_indices[0], face_indices[1])
            def_faces = [faces[i] for i in idx_iter
                         if faces[i].vertices and len(faces[i].vertices) >= 3]
            if def_faces:
                prims = self._build_primitives_for_faces(def_faces)
                if prims:
                    self._def_mesh_map[def_ref] = len(self.meshes)
                    self.meshes.append({
                        "name": f"Definition_{def_ref}",
                        "primitives": prims
                    })

        # Build separate meshes for each transformed group
        for scope_num in sorted(self.model.group_transforms.keys()):
            if scope_num not in self.model.group_face_ranges:
                continue
            f_start, f_end = self.model.group_face_ranges[scope_num]
            grp_faces = [faces[i] for i in range(f_start, min(f_end, len(faces)))
                         if faces[i].vertices and len(faces[i].vertices) >= 3]
            if grp_faces:
                prims = self._build_primitives_for_faces(grp_faces)
                if prims:
                    self._group_mesh_map[scope_num] = len(self.meshes)
                    self.meshes.append({
                        "name": f"Group_scope{scope_num}",
                        "primitives": prims
                    })

    def _build_primitives_for_faces(self, faces):
        """Build glTF primitives grouped by material."""
        mat_groups = {}
        for face in faces:
            mat_idx = face.material_idx if face.material_idx >= 0 else self._default_mat_idx
            mat_groups.setdefault(mat_idx, []).append(face)

        primitives = []
        for mat_idx in sorted(mat_groups.keys()):
            prim = self._build_skp_primitive(mat_groups[mat_idx], mat_idx)
            if prim:
                primitives.append(prim)
        return primitives

    def _build_skp_primitive(self, faces, material_idx):
        """Build a glTF primitive from SKP faces with normal splitting."""
        SMOOTH_THRESHOLD = 0.85  # cos(~32°)
        pos_faces = {}
        face_data = []

        for face in faces:
            verts = face.vertices
            if len(verts) < 3:
                continue

            # Skip faces with extreme coordinates (corrupt transforms)
            if any(not math.isfinite(v.x) or not math.isfinite(v.y) or
                   not math.isfinite(v.z) or
                   abs(v.x) > 1e8 or abs(v.y) > 1e8 or abs(v.z) > 1e8
                   for v in verts):
                continue

            # Merge near-duplicate vertices (< 0.1 inch apart)
            if len(verts) > 3:
                merged = [verts[0]]
                for v in verts[1:]:
                    pv = merged[-1]
                    dist_sq = (v.x-pv.x)**2 + (v.y-pv.y)**2 + (v.z-pv.z)**2
                    if dist_sq > 0.01:
                        merged.append(v)
                if len(merged) > 3:
                    pv = merged[-1]
                    fv = merged[0]
                    dist_sq = (fv.x-pv.x)**2 + (fv.y-pv.y)**2 + (fv.z-pv.z)**2
                    if dist_sq <= 0.01:
                        merged.pop()
                if len(merged) >= 3 and len(merged) < len(verts):
                    verts = merged

            # Skip faces with invalid vertex coordinates
            bad = False
            for v in verts:
                if abs(v.x) > 1e6 or abs(v.y) > 1e6 or abs(v.z) > 1e6:
                    bad = True
                    break
            if bad:
                continue

            nx, ny, nz = face.normal
            norm_len = math.sqrt(nx*nx + ny*ny + nz*nz)
            if norm_len > 0:
                nx /= norm_len
                ny /= norm_len
                nz /= norm_len

            gn = (nx, nz, -ny)  # SKP to glTF normal transform

            fi = len(face_data)
            gltf_verts = []
            for vi, v in enumerate(verts):
                px = v.x * INCHES_TO_METERS
                py = v.z * INCHES_TO_METERS
                pz = -v.y * INCHES_TO_METERS
                gltf_verts.append((px, py, pz))
                key = (round(px, 8), round(py, 8), round(pz, 8))
                pos_faces.setdefault(key, []).append((gn, fi, vi))

            # Collect hole loop vertices
            hole_verts_list = []
            holes = getattr(face, 'holes', None)
            if holes:
                for hole in holes:
                    hole_gltf = []
                    for hv in hole:
                        px = hv.x * INCHES_TO_METERS
                        py = hv.z * INCHES_TO_METERS
                        pz = -hv.y * INCHES_TO_METERS
                        vi_h = len(gltf_verts)
                        gltf_verts.append((px, py, pz))
                        hole_gltf.append(vi_h)
                        key = (round(px, 8), round(py, 8), round(pz, 8))
                        pos_faces.setdefault(key, []).append((gn, fi, vi_h))
                    hole_verts_list.append(hole_gltf)

            face_data.append((gltf_verts, gn, hole_verts_list))

        if not face_data:
            return None

        # Build soft-edge adjacency: which face pairs share a soft edge?
        # A soft edge means the faces should share smooth normals at that edge's vertices.
        soft_face_pairs = set()  # set of frozenset({fi1, fi2})
        if self.model.edges:
            # Map vertex id → set of face indices
            vert_to_faces = {}
            for fi, (gverts, gn, _) in enumerate(face_data):
                for v_orig in faces[fi].vertices if fi < len(faces) else []:
                    vid = id(v_orig)
                    vert_to_faces.setdefault(vid, set()).add(fi)
            # For each soft edge, find which faces share both endpoints
            for edge in self.model.edges:
                if not edge.soft:
                    continue
                sv = edge.start_vertex
                ev = edge.end_vertex
                if sv is None or ev is None:
                    continue
                sv_faces = vert_to_faces.get(id(sv), set())
                ev_faces = vert_to_faces.get(id(ev), set())
                shared = sv_faces & ev_faces
                if len(shared) >= 2:
                    shared_list = list(shared)
                    for a in range(len(shared_list)):
                        for b in range(a+1, len(shared_list)):
                            soft_face_pairs.add(frozenset(
                                {shared_list[a], shared_list[b]}))

        # Normal splitting: group by soft-edge connectivity + angle threshold
        pos_groups = {}
        for key, contributions in pos_faces.items():
            groups = []
            for gn, fi, vi in contributions:
                merged_into = False
                for group in groups:
                    avg = group[0]
                    dot = gn[0]*avg[0] + gn[1]*avg[1] + gn[2]*avg[2]
                    # Merge if: soft edge connects them, OR angle is within threshold
                    has_soft_edge = any(
                        frozenset({fi, member_fi}) in soft_face_pairs
                        for member_fi, _ in group[1])
                    should_merge = has_soft_edge or dot >= SMOOTH_THRESHOLD
                    if should_merge:
                        group[1].append((fi, vi))
                        new_n = (group[0][0]+gn[0], group[0][1]+gn[1],
                                 group[0][2]+gn[2])
                        nl = math.sqrt(new_n[0]**2 + new_n[1]**2 + new_n[2]**2)
                        if nl > 0:
                            group[0] = (new_n[0]/nl, new_n[1]/nl, new_n[2]/nl)
                        merged_into = True
                        break
                if not merged_into:
                    groups.append([gn, [(fi, vi)]])
            pos_groups[key] = groups

        # Assign vertex indices
        positions = []
        normals = []
        face_vert_index = [[None]*len(fd[0]) for fd in face_data]

        for key, groups in pos_groups.items():
            pos = (float(key[0]), float(key[1]), float(key[2]))
            for group_normal, members in groups:
                idx = len(positions)
                positions.append(pos)
                normals.append(group_normal)
                for fi, vi in members:
                    face_vert_index[fi][vi] = idx

        # Build index buffer with triangulation
        indices = []
        for fi, (gltf_verts, gn, hole_vi_lists) in enumerate(face_data):
            fvi = face_vert_index[fi]
            if any(v is None for v in fvi):
                continue

            # Handle faces with holes
            if hole_vi_lists:
                outer_count = len(fvi) - sum(len(h) for h in hole_vi_lists)
                outer_fvi = list(fvi[:outer_count])
                hole_fvis = []
                offset = outer_count
                for hole_vis in hole_vi_lists:
                    h = list(fvi[offset:offset + len(hole_vis)])
                    if len(h) >= 3:
                        hole_fvis.append(h)
                    offset += len(hole_vis)
                if hole_fvis:
                    merged_poly = merge_polygon_holes(
                        outer_fvi, hole_fvis, positions, gn)
                    if len(merged_poly) >= 3:
                        tris = ear_clip(merged_poly, positions, gn,
                                        bridge_merged=True,
                                        outer_ring=outer_fvi,
                                        hole_rings=hole_fvis)
                        indices.extend(tris)
                        continue
                fvi = fvi[:outer_count]

            n_verts = len(fvi)
            if n_verts < 3:
                continue

            if is_convex_polygon(fvi, positions, gn) or n_verts == 3:
                indices.extend(fan_triangulate(fvi, positions, gn))
            else:
                tris = ear_clip(fvi, positions, gn)
                indices.extend(tris)

        if not positions or not indices:
            return None

        gltf_mat_idx = min(material_idx, len(self.materials_gltf) - 1)
        return self.build_primitive(positions, normals, indices,
                                    material_idx=gltf_mat_idx)

    def _build_nodes(self):
        """Build glTF node hierarchy with mesh instancing."""
        if not self.meshes:
            return

        has_separate_meshes = self._def_mesh_map or self._group_mesh_map

        if not has_separate_meshes:
            self.nodes.append({"name": "root", "mesh": 0})
            self.scene_nodes.append(0)
            return

        children = []

        # Root mesh node
        if self.meshes and self.meshes[0]['name'] == 'SketchUpModel':
            root_mesh_node = len(self.nodes)
            self.nodes.append({"name": "root_mesh", "mesh": 0})
            children.append(root_mesh_node)

        # Instanced definition nodes
        for def_ref in sorted(self.model.ci_transforms.keys()):
            mesh_idx = self._def_mesh_map.get(def_ref)
            if mesh_idx is None:
                continue
            xforms = self.model.ci_transforms[def_ref]
            for i, xform in enumerate(xforms):
                node_idx = len(self.nodes)
                gltf_matrix = self._skp_transform_to_gltf(xform)
                node = {
                    "name": f"CI_{def_ref}_{i}",
                    "mesh": mesh_idx,
                    "matrix": gltf_matrix
                }
                self.nodes.append(node)
                children.append(node_idx)

        # Group nodes with transforms
        for scope_num in sorted(self.model.group_transforms.keys()):
            mesh_idx = self._group_mesh_map.get(scope_num)
            if mesh_idx is None:
                continue
            xform = self.model.group_transforms[scope_num]
            node_idx = len(self.nodes)
            gltf_matrix = self._skp_transform_to_gltf(xform)
            node = {
                "name": f"Group_scope{scope_num}",
                "mesh": mesh_idx,
                "matrix": gltf_matrix
            }
            self.nodes.append(node)
            children.append(node_idx)

        # Scene root node
        if children:
            root = {"name": "root", "children": children}
            root_idx = len(self.nodes)
            self.nodes.append(root)
            self.scene_nodes.append(root_idx)

    def _skp_transform_to_gltf(self, xform):
        """Convert SKP 13-double transform to glTF column-major 4x4 matrix.

        SKP: Z-up, inches. glTF: Y-up, meters.
        Coordinate transform: gltf_x = skp_x, gltf_y = skp_z, gltf_z = -skp_y
        """
        s = INCHES_TO_METERS
        Xx, Xy, Xz = xform[0], xform[1], xform[2]
        Yx, Yy, Yz = xform[3], xform[4], xform[5]
        Zx, Zy, Zz = xform[6], xform[7], xform[8]
        Tx, Ty, Tz = xform[9] * s, xform[10] * s, xform[11] * s

        # glTF column-major: C * M_skp * C^-1
        return [
            Xx,   Zx,  -Yx,  0.0,   # column 0
            Xz,   Zz,  -Yz,  0.0,   # column 1
            -Xy, -Zy,   Yy,  0.0,   # column 2
            Tx,   Tz,  -Ty,  1.0    # column 3
        ]

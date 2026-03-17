# Vibe coded by Claude
"""
Open Inventor (.iv) parser and GLB converter.

Supports ASCII and binary .iv files (V1.0, V2.0, V2.1).
Parses the scene graph with state inheritance, transforms, materials,
and geometry nodes. Converts to GLB via GLBBuilder.

Parse phase:  Build a tree of IVNode objects with fields.
Traverse phase: Walk the tree accumulating state (Material, Transform, etc.)
                and collecting geometry from shape nodes.
Convert phase: Build GLB output using GLBBuilder.
"""

import struct
import sys
import os
import math
import re
from collections import OrderedDict

from glb import (GLBBuilder, ear_clip, merge_polygon_holes,
                 is_convex_polygon, fan_triangulate)


# ---------------------------------------------------------------------------
# Scene graph data structures
# ---------------------------------------------------------------------------

class IVNode:
    """A node in the Open Inventor scene graph."""
    __slots__ = ('node_type', 'fields', 'children', 'def_name')

    def __init__(self, node_type):
        self.node_type = node_type
        self.fields = OrderedDict()   # field_name -> value
        self.children = []            # list of IVNode (for group nodes)
        self.def_name = None          # DEF name if any

    def __repr__(self):
        name = f" DEF {self.def_name}" if self.def_name else ""
        kids = f" ({len(self.children)} children)" if self.children else ""
        return f"<IVNode {self.node_type}{name}{kids}>"


class IVUseRef:
    """A USE reference placeholder."""
    __slots__ = ('name',)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"<USE {self.name}>"


# ---------------------------------------------------------------------------
# GROUP_NODES: nodes that can contain children
# ---------------------------------------------------------------------------

GROUP_NODES = {
    'Separator', 'Group', 'Switch', 'TransformSeparator',
    'WWWAnchor', 'LOD', 'LevelOfDetail', 'Selection',
    'Annotation', 'Array', 'MultipleCopy', 'Decal',
    'ShapeKit', 'AppearanceKit',
}


# ---------------------------------------------------------------------------
# ASCII Parser - recursive descent
# ---------------------------------------------------------------------------

class AsciiParser:
    """Recursive descent parser for Open Inventor ASCII format."""

    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.length = len(text)
        self.def_table = {}  # DEF name -> IVNode

    def parse(self):
        """Parse all top-level nodes. Returns list of IVNode/IVUseRef."""
        nodes = []
        while True:
            self._skip_ws()
            if self.pos >= self.length:
                break
            node = self._parse_node_or_use()
            if node is None:
                break
            nodes.append(node)
        return nodes

    def _skip_ws(self):
        """Skip whitespace and comments."""
        while self.pos < self.length:
            c = self.text[self.pos]
            if c in ' \t\r\n':
                self.pos += 1
            elif c == '#':
                # Skip to end of line
                nl = self.text.find('\n', self.pos)
                if nl < 0:
                    self.pos = self.length
                else:
                    self.pos = nl + 1
            else:
                break

    def _peek_char(self):
        if self.pos < self.length:
            return self.text[self.pos]
        return ''

    def _read_identifier(self):
        """Read an identifier (alphanumeric + _ + .)."""
        self._skip_ws()
        start = self.pos
        while self.pos < self.length:
            c = self.text[self.pos]
            if c.isalnum() or c in '_.-+':
                self.pos += 1
            else:
                break
        return self.text[start:self.pos]

    def _read_quoted_string(self):
        """Read a double-quoted string."""
        assert self.text[self.pos] == '"'
        self.pos += 1
        result = []
        while self.pos < self.length:
            c = self.text[self.pos]
            if c == '\\' and self.pos + 1 < self.length:
                self.pos += 1
                nc = self.text[self.pos]
                if nc == 'n':
                    result.append('\n')
                elif nc == 't':
                    result.append('\t')
                elif nc == '"':
                    result.append('"')
                elif nc == '\\':
                    result.append('\\')
                else:
                    result.append(nc)
                self.pos += 1
            elif c == '"':
                self.pos += 1
                break
            else:
                result.append(c)
                self.pos += 1
        return ''.join(result)

    def _read_number(self):
        """Read a numeric value (int or float, possibly hex)."""
        self._skip_ws()
        start = self.pos
        if self.pos < self.length and self.text[self.pos] in '+-':
            self.pos += 1
        # Check for hex
        if (self.pos + 1 < self.length and
                self.text[self.pos] == '0' and
                self.text[self.pos + 1] in 'xX'):
            self.pos += 2
            while self.pos < self.length and self.text[self.pos] in '0123456789abcdefABCDEF':
                self.pos += 1
            return int(self.text[start:self.pos], 0)
        # Regular number
        while self.pos < self.length and self.text[self.pos] in '0123456789':
            self.pos += 1
        if self.pos < self.length and self.text[self.pos] == '.':
            self.pos += 1
            while self.pos < self.length and self.text[self.pos] in '0123456789':
                self.pos += 1
        if self.pos < self.length and self.text[self.pos] in 'eE':
            self.pos += 1
            if self.pos < self.length and self.text[self.pos] in '+-':
                self.pos += 1
            while self.pos < self.length and self.text[self.pos] in '0123456789':
                self.pos += 1
        s = self.text[start:self.pos]
        if not s:
            return 0.0
        try:
            if '.' in s or 'e' in s or 'E' in s:
                return float(s)
            return int(s)
        except ValueError:
            return 0.0

    def _peek_is_number(self):
        """Check if the next token looks like a number."""
        self._skip_ws()
        if self.pos >= self.length:
            return False
        c = self.text[self.pos]
        if c in '0123456789.':
            return True
        if c in '+-' and self.pos + 1 < self.length:
            nc = self.text[self.pos + 1]
            if nc in '0123456789.':
                return True
        return False

    def _parse_node_or_use(self):
        """Parse a node, possibly prefixed with DEF, or a USE reference."""
        self._skip_ws()
        if self.pos >= self.length:
            return None

        c = self._peek_char()
        if c == '}' or c == ']':
            return None

        ident = self._read_identifier()
        if not ident:
            # Try to skip past unexpected characters
            if self.pos < self.length:
                self.pos += 1
            return None

        # Handle DEF
        def_name = None
        if ident == 'DEF':
            def_name = self._read_identifier()
            ident = self._read_identifier()

        # Handle USE
        if ident == 'USE':
            use_name = self._read_identifier()
            ref = IVUseRef(use_name)
            if use_name in self.def_table:
                return self.def_table[use_name]
            return ref

        # Now ident is the node type
        node = IVNode(ident)
        node.def_name = def_name

        # Look for opening brace
        self._skip_ws()
        if self.pos < self.length and self.text[self.pos] == '{':
            self.pos += 1  # consume '{'
            self._parse_node_body(node)
            self._skip_ws()
            if self.pos < self.length and self.text[self.pos] == '}':
                self.pos += 1  # consume '}'
        # Else: node with no body (e.g., bare type name)

        if def_name:
            self.def_table[def_name] = node

        return node

    def _parse_node_body(self, node):
        """Parse the body of a node (fields and children)."""
        is_group = node.node_type in GROUP_NODES

        while True:
            self._skip_ws()
            if self.pos >= self.length:
                break
            c = self._peek_char()
            if c == '}':
                break

            # Try to parse as field or child node
            saved_pos = self.pos
            ident = self._read_identifier()
            if not ident:
                if self.pos < self.length and self.text[self.pos] not in '}':
                    self.pos += 1
                continue

            # Special: "fields [...]" declaration (V2.1 extension nodes)
            if ident == 'fields':
                self._skip_ws()
                if self._peek_char() == '[':
                    self._skip_brackets()
                continue

            # DEF / USE as child
            if ident == 'DEF' or ident == 'USE':
                self.pos = saved_pos
                child = self._parse_node_or_use()
                if child is not None:
                    node.children.append(child)
                continue

            # Check if this is a child node (starts with uppercase, followed by '{')
            self._skip_ws()
            if self._peek_char() == '{':
                # It's a child node
                self.pos = saved_pos
                child = self._parse_node_or_use()
                if child is not None:
                    if is_group or True:
                        # In OIV, even non-group nodes can have children
                        # but we treat them as children anyway
                        node.children.append(child)
                continue

            # It's a field name; parse the field value
            field_name = ident
            value = self._parse_field_value(node.node_type, field_name)
            node.fields[field_name] = value

    def _skip_brackets(self):
        """Skip past a [...] block."""
        if self._peek_char() != '[':
            return
        self.pos += 1
        depth = 1
        while self.pos < self.length and depth > 0:
            c = self.text[self.pos]
            if c == '[':
                depth += 1
            elif c == ']':
                depth -= 1
            elif c == '"':
                self.pos += 1
                while self.pos < self.length and self.text[self.pos] != '"':
                    if self.text[self.pos] == '\\':
                        self.pos += 1
                    self.pos += 1
            elif c == '#':
                nl = self.text.find('\n', self.pos)
                if nl < 0:
                    self.pos = self.length
                    return
                self.pos = nl
            self.pos += 1

    def _parse_field_value(self, node_type, field_name):
        """Parse a field value based on context. Returns the parsed value."""
        self._skip_ws()

        # Special case: vertexProperty is an inline node
        if field_name == 'vertexProperty':
            return self._parse_node_or_use()

        # Special case: "fields" declaration
        if field_name == 'fields':
            if self._peek_char() == '[':
                self._skip_brackets()
            return None

        # Known multi-value fields that use [] notation
        multi_fields = {
            'point', 'vector', 'coordIndex', 'materialIndex',
            'normalIndex', 'textureCoordIndex', 'numVertices',
            'diffuseColor', 'ambientColor', 'specularColor',
            'emissiveColor', 'shininess', 'transparency',
            'rgb', 'orderedRGBA', 'vertex', 'normal', 'texCoord',
            'range', 'screenArea', 'width', 'string', 'colorIndex',
        }

        # Enum/named fields
        enum_fields = {
            'vertexOrdering', 'shapeType', 'faceType',
            'value', 'model', 'style', 'renderCaching',
            'boundingBoxCaching', 'renderCulling', 'pickCulling',
            'materialBinding', 'normalBinding', 'textureCoordBinding',
            'justification', 'family', 'axis', 'wrapS', 'wrapT',
            'whichChild', 'type', 'viewModel', 'axes',
            'map1', 'map2',
        }

        # String fields
        string_fields = {
            'filename', 'name', 'description', 'label', 'string',
        }

        # Bool fields
        bool_fields = {'on', 'clamp'}

        # "parts" field (bitmask of identifiers like ALL, SIDES, etc.)
        if field_name == 'parts':
            return self._parse_enum_or_bitmask()

        if field_name in bool_fields:
            tok = self._read_identifier()
            return tok.upper() in ('TRUE', '1', 'ON')

        if field_name in enum_fields:
            # Could be a named enum or a number
            if self._peek_is_number():
                return self._read_number()
            return self._read_identifier()

        # image field: width height numComponents data...
        if field_name == 'image':
            return self._parse_image_field()

        # matrix field: 16 floats
        if field_name == 'matrix':
            vals = []
            for _ in range(16):
                vals.append(float(self._read_number()))
            return vals

        # Check if next char is [  -> multi-value
        self._skip_ws()
        if self._peek_char() == '[':
            return self._parse_array()

        # Check if next char is " -> string
        if self._peek_char() == '"':
            return self._read_quoted_string()

        # Otherwise, parse as number(s) based on field semantic
        # rotation: 4 floats
        if field_name in ('rotation', 'scaleOrientation', 'orientation'):
            vals = []
            for _ in range(4):
                vals.append(float(self._read_number()))
            return tuple(vals)

        # Vec3f fields
        vec3_fields = {
            'translation', 'scaleFactor', 'center', 'position',
            'direction', 'location', 'directionS', 'directionT',
        }
        if field_name in vec3_fields:
            vals = []
            for _ in range(3):
                vals.append(float(self._read_number()))
            return tuple(vals)

        # Vec2f fields
        if field_name in ('point',) and node_type == 'TextureCoordinate2':
            return self._parse_array()

        # Color fields that might be single value
        if field_name in ('color', 'blendColor'):
            vals = []
            for _ in range(3):
                vals.append(float(self._read_number()))
            return tuple(vals)

        # Single/multi float/int: context-dependent
        # For fields like 'point', 'vector' that are MFVec3f, they need []
        if field_name in multi_fields:
            # Could be a single value or array
            if self._peek_is_number():
                # Parse as single value or tuple
                return self._parse_inline_values()
            return self._read_identifier()

        # Default: try as number if it looks like one
        if self._peek_is_number():
            return self._read_number()

        # Otherwise read as identifier (enum value)
        return self._read_identifier()

    def _parse_enum_or_bitmask(self):
        """Parse a bitmask or enum value like (ALL | SIDES)."""
        self._skip_ws()
        if self._peek_char() == '(':
            self.pos += 1
            parts = []
            while True:
                self._skip_ws()
                if self._peek_char() == ')':
                    self.pos += 1
                    break
                if self._peek_char() == '|':
                    self.pos += 1
                    continue
                tok = self._read_identifier()
                if tok:
                    parts.append(tok)
                else:
                    break
            return parts
        # Single identifier
        return self._read_identifier()

    def _parse_image_field(self):
        """Parse SFImage: width height numComponents pixels..."""
        w = int(self._read_number())
        h = int(self._read_number())
        nc = int(self._read_number())
        # Skip pixel values
        for _ in range(w * h):
            self._read_number()
        return {'width': w, 'height': h, 'numComponents': nc}

    def _parse_array(self):
        """Parse a [...] array of values."""
        assert self.text[self.pos] == '['
        self.pos += 1
        values = []
        while True:
            self._skip_ws()
            if self.pos >= self.length:
                break
            if self._peek_char() == ']':
                self.pos += 1
                break
            if self._peek_char() == ',':
                self.pos += 1
                continue
            if self._peek_char() == '"':
                values.append(self._read_quoted_string())
                continue
            if self._peek_is_number():
                values.append(self._read_number())
            else:
                # Could be an enum value in array context
                tok = self._read_identifier()
                if tok:
                    values.append(tok)
                else:
                    self.pos += 1  # skip unknown char
        return values

    def _parse_inline_values(self):
        """Parse inline numeric values (single or multi)."""
        vals = []
        while self._peek_is_number():
            vals.append(self._read_number())
            self._skip_ws()
            if self._peek_char() == ',':
                self.pos += 1
        if len(vals) == 1:
            return vals[0]
        return vals


# ---------------------------------------------------------------------------
# Binary Parser - adapted from decode_all5.py but stores field values
# ---------------------------------------------------------------------------

class BinaryParser:
    """Parser for Open Inventor binary format."""

    GROUP_NODES = {
        'Separator', 'Group', 'Switch', 'TransformSeparator',
        'WWWAnchor', 'LOD', 'LevelOfDetail', 'Selection',
        'Annotation', 'Array', 'MultipleCopy', 'Decal',
        'ShapeKit', 'AppearanceKit',
    }

    NO_FIELD_DATA_NODES = {'Group'}

    NODE_FIELDS = {
        'Coordinate3': {'point': 'MFVec3f'},
        'Coordinate4': {'point': 'MFVec4f'},
        'TextureCoordinate2': {'point': 'MFVec2f'},
        'Normal': {'vector': 'MFVec3f'},
        'Info': {'string': 'SFString'},
        'VertexProperty': {
            'vertex': 'MFVec3f', 'normal': 'MFVec3f',
            'texCoord': 'MFVec2f', 'orderedRGBA': 'MFUInt32',
            'materialBinding': 'SFEnum', 'normalBinding': 'SFEnum',
            'textureCoordBinding': 'SFEnum',
        },
        'RotationXYZ': {'axis': 'SFEnum', 'angle': 'SFFloat'},
        'Complexity': {'type': 'SFEnum', 'value': 'SFFloat',
                       'textureQuality': 'SFFloat'},
        'LOD': {'range': 'MFFloat', 'center': 'SFVec3f'},
        'LevelOfDetail': {'screenArea': 'MFFloat'},
        'IndexedTriangleStripSet': {
            'coordIndex': 'MFInt32', 'materialIndex': 'MFInt32',
            'normalIndex': 'MFInt32', 'textureCoordIndex': 'MFInt32',
            'vertexProperty': 'SFNode',
        },
        'IndexedFaceSet': {
            'coordIndex': 'MFInt32', 'materialIndex': 'MFInt32',
            'normalIndex': 'MFInt32', 'textureCoordIndex': 'MFInt32',
            'vertexProperty': 'SFNode',
        },
        'IndexedLineSet': {
            'coordIndex': 'MFInt32', 'materialIndex': 'MFInt32',
            'normalIndex': 'MFInt32', 'textureCoordIndex': 'MFInt32',
            'vertexProperty': 'SFNode',
        },
        'TriangleStripSet': {'numVertices': 'MFInt32',
                             'vertexProperty': 'SFNode',
                             'startIndex': 'SFInt32'},
        'FaceSet': {'numVertices': 'MFInt32', 'vertexProperty': 'SFNode'},
        'QuadMesh': {'verticesPerColumn': 'SFInt32',
                     'verticesPerRow': 'SFInt32',
                     'vertexProperty': 'SFNode'},
        'PointSet': {'startIndex': 'SFInt32', 'numPoints': 'SFInt32',
                     'vertexProperty': 'SFNode'},
        'LineSet': {'numVertices': 'MFInt32', 'vertexProperty': 'SFNode'},
        'TextureCoordinateEnvironment': {'viewModel': 'SFEnum'},
        'TextureCoordinatePlane': {'directionS': 'SFVec3f',
                                   'directionT': 'SFVec3f'},
        'Texture2Transform': {
            'translation': 'SFVec2f', 'rotation': 'SFFloat',
            'scaleFactor': 'SFVec2f', 'center': 'SFVec2f',
        },
        'Cylinder': {'parts': 'SFBitMask', 'radius': 'SFFloat',
                     'height': 'SFFloat'},
        'Cone': {'parts': 'SFBitMask', 'bottomRadius': 'SFFloat',
                 'height': 'SFFloat'},
        'Text3': {'string': 'MFString', 'spacing': 'SFFloat',
                  'justification': 'SFEnum', 'parts': 'SFBitMask'},
        'Font': {'name': 'SFName', 'size': 'SFFloat'},
        'Text2': {'string': 'MFString', 'spacing': 'SFFloat',
                  'justification': 'SFEnum'},
        'AsciiText': {'string': 'MFString', 'spacing': 'SFFloat',
                      'justification': 'SFEnum', 'width': 'MFFloat'},
    }

    DEFAULT_FIELD_TYPES = {
        'ambientColor': 'MFColor', 'diffuseColor': 'MFColor',
        'specularColor': 'MFColor', 'emissiveColor': 'MFColor',
        'shininess': 'MFFloat', 'transparency': 'MFFloat',
        'point': 'MFVec3f', 'vector': 'MFVec3f',
        'coordIndex': 'MFInt32', 'materialIndex': 'MFInt32',
        'normalIndex': 'MFInt32', 'textureCoordIndex': 'MFInt32',
        'numVertices': 'MFInt32',
        'translation': 'SFVec3f', 'rotation': 'SFRotation',
        'scaleFactor': 'SFVec3f', 'scaleOrientation': 'SFRotation',
        'center': 'SFVec3f',
        'matrix': 'SFMatrix',
        'width': 'SFFloat', 'height': 'SFFloat', 'depth': 'SFFloat',
        'radius': 'SFFloat',
        'parts': 'SFBitMask', 'bottomRadius': 'SFFloat',
        'style': 'SFEnum', 'model': 'SFEnum', 'value': 'SFEnum',
        'rgb': 'MFColor',
        'renderCaching': 'SFEnum', 'boundingBoxCaching': 'SFEnum',
        'renderCulling': 'SFEnum', 'pickCulling': 'SFEnum',
        'filename': 'SFString', 'image': 'SFImage',
        'blendColor': 'SFColor',
        'vertexOrdering': 'SFEnum', 'shapeType': 'SFEnum',
        'faceType': 'SFEnum', 'creaseAngle': 'SFFloat',
        'position': 'SFVec3f', 'orientation': 'SFRotation',
        'nearDistance': 'SFFloat', 'farDistance': 'SFFloat',
        'focalDistance': 'SFFloat', 'heightAngle': 'SFFloat',
        'direction': 'SFVec3f', 'intensity': 'SFFloat',
        'color': 'SFColor', 'on': 'SFBool',
        'description': 'SFString', 'name': 'SFName',
        'whichChild': 'SFInt32',
        'dropOffRate': 'SFFloat', 'cutOffAngle': 'SFFloat',
        'location': 'SFVec3f',
        'startIndex': 'SFInt32',
        'string': 'MFString',
        'spacing': 'SFFloat', 'justification': 'SFEnum',
        'size': 'SFFloat', 'family': 'SFEnum',
        'wrapS': 'SFEnum', 'wrapT': 'SFEnum',
        'colorIndex': 'MFInt32',
        'axes': 'SFEnum',
        'map1': 'SFEnum', 'map2': 'SFEnum',
        'clamp': 'SFBool',
        'label': 'SFString',
        'range': 'MFFloat',
        'axis': 'SFEnum', 'angle': 'SFFloat',
        'vertex': 'MFVec3f', 'normal': 'MFVec3f',
        'texCoord': 'MFVec2f', 'orderedRGBA': 'MFUInt32',
        'materialBinding': 'SFEnum', 'normalBinding': 'SFEnum',
        'textureCoordBinding': 'SFEnum',
        'screenArea': 'MFFloat',
        'vertexProperty': 'SFNode',
        'verticesPerColumn': 'SFInt32', 'verticesPerRow': 'SFInt32',
        'numPoints': 'SFInt32',
        'type': 'SFEnum', 'textureQuality': 'SFFloat',
        'viewModel': 'SFEnum',
        'directionS': 'SFVec3f', 'directionT': 'SFVec3f',
        'functions': 'SFNode',
        # Array node fields
        'numElements1': 'SFInt32', 'numElements2': 'SFInt32',
        'numElements3': 'SFInt32',
        'separation1': 'SFVec3f', 'separation2': 'SFVec3f',
        'separation3': 'SFVec3f',
        'origin': 'SFEnum',
        # Rotor/Pendulum/Shuttle animation nodes
        'speed': 'SFFloat', 'on': 'SFBool',
    }

    def __init__(self, data, version):
        self.data = data
        self.pos = 0
        self.version = version
        self.def_table = {}

    def remaining(self):
        return len(self.data) - self.pos

    def read_u32(self):
        val = struct.unpack('>I', self.data[self.pos:self.pos + 4])[0]
        self.pos += 4
        return val

    def read_i32(self):
        val = struct.unpack('>i', self.data[self.pos:self.pos + 4])[0]
        self.pos += 4
        return val

    def read_f32(self):
        val = struct.unpack('>f', self.data[self.pos:self.pos + 4])[0]
        self.pos += 4
        return val

    def read_string(self):
        slen = self.read_u32()
        if slen > 5000000:
            raise ValueError(
                f"String length {slen} too large at offset {self.pos - 4}")
        raw = self.data[self.pos:self.pos + slen]
        padded = slen
        if padded % 4 != 0:
            padded += 4 - (padded % 4)
        self.pos += padded
        return raw.rstrip(b'\x00').decode('ascii', errors='replace')

    def peek_string(self):
        if self.remaining() < 4:
            return None
        slen = struct.unpack('>I', self.data[self.pos:self.pos + 4])[0]
        if slen == 0 or slen > 10000:
            return None
        if self.pos + 4 + slen > len(self.data):
            return None
        raw = self.data[self.pos + 4:self.pos + 4 + slen]
        if all(0x20 <= b < 0x7f for b in raw):
            return raw.decode('ascii')
        return None

    def get_field_type(self, fname, nname):
        if nname in self.NODE_FIELDS:
            ft = self.NODE_FIELDS[nname].get(fname)
            if ft:
                return ft
        return self.DEFAULT_FIELD_TYPES.get(fname)

    def read_field_value(self, fname, nname=""):
        """Read and RETURN the field value (unlike decode_all5 which skips)."""
        ftype = self.get_field_type(fname, nname)
        if ftype is None:
            raise ValueError(
                f"Unknown field '{fname}' in '{nname}' at 0x{self.pos:04x}")

        if ftype == 'SFFloat':
            return self.read_f32()
        elif ftype == 'SFBitMask':
            parts = []
            while True:
                s = self.read_string()
                if not s:
                    break
                parts.append(s)
            return parts
        elif ftype == 'SFEnum':
            return self.read_string()
        elif ftype in ('SFString', 'SFName'):
            return self.read_string()
        elif ftype == 'SFBool':
            return bool(self.read_u32())
        elif ftype == 'SFInt32':
            return self.read_i32()
        elif ftype == 'SFColor':
            r, g, b = self.read_f32(), self.read_f32(), self.read_f32()
            return (r, g, b)
        elif ftype == 'SFVec3f':
            x, y, z = self.read_f32(), self.read_f32(), self.read_f32()
            return (x, y, z)
        elif ftype == 'SFVec2f':
            x, y = self.read_f32(), self.read_f32()
            return (x, y)
        elif ftype == 'SFRotation':
            x, y, z, a = (self.read_f32(), self.read_f32(),
                          self.read_f32(), self.read_f32())
            return (x, y, z, a)
        elif ftype == 'SFMatrix':
            vals = [self.read_f32() for _ in range(16)]
            return vals
        elif ftype == 'SFImage':
            w = self.read_i32()
            h = self.read_i32()
            nc = self.read_i32()
            if self.version < 2.1:
                nbytes = w * h * 4
            else:
                nbytes = w * h * nc
            padded = nbytes
            if padded % 4 != 0:
                padded += 4 - (padded % 4)
            self.pos += padded
            return {'width': w, 'height': h, 'numComponents': nc}
        elif ftype == 'SFNode':
            return self.read_node()
        elif ftype == 'MFFloat':
            n = self.read_u32()
            return [self.read_f32() for _ in range(n)]
        elif ftype == 'MFUInt32':
            n = self.read_u32()
            return [self.read_u32() for _ in range(n)]
        elif ftype == 'MFColor':
            n = self.read_u32()
            vals = [self.read_f32() for _ in range(n * 3)]
            return [vals[i:i + 3] for i in range(0, len(vals), 3)]
        elif ftype == 'MFVec3f':
            n = self.read_u32()
            vals = [self.read_f32() for _ in range(n * 3)]
            return [(vals[i], vals[i + 1], vals[i + 2])
                    for i in range(0, len(vals), 3)]
        elif ftype == 'MFVec2f':
            n = self.read_u32()
            vals = [self.read_f32() for _ in range(n * 2)]
            return [(vals[i], vals[i + 1]) for i in range(0, len(vals), 2)]
        elif ftype == 'MFVec4f':
            n = self.read_u32()
            vals = [self.read_f32() for _ in range(n * 4)]
            return [(vals[i], vals[i + 1], vals[i + 2], vals[i + 3])
                    for i in range(0, len(vals), 4)]
        elif ftype == 'MFInt32':
            n = self.read_u32()
            return [self.read_i32() for _ in range(n)]
        elif ftype == 'MFString':
            n = self.read_u32()
            return [self.read_string() for _ in range(n)]
        else:
            raise ValueError(f"Unhandled type {ftype}")

    def read_node(self):
        """Read a node and return an IVNode (or IVUseRef)."""
        if self.remaining() < 4:
            return None

        def_name = None
        peek = self.peek_string()
        if peek == "DEF":
            self.read_string()  # "DEF"
            def_name = self.read_string()
        elif peek == "USE":
            self.read_string()  # "USE"
            use_name = self.read_string()
            if use_name in self.def_table:
                return self.def_table[use_name]
            return IVUseRef(use_name)

        node_type = self.read_string()
        node = IVNode(node_type)
        node.def_name = def_name

        is_group = node_type in self.GROUP_NODES

        if self.version >= 2.1:
            flags = self.read_u32()
            is_group = bool(flags & 0x02)

        skip_field_count = (self.version < 2.1 and
                            node_type in self.NO_FIELD_DATA_NODES)

        if skip_field_count:
            num_fields = 0
            not_builtin = False
        else:
            field_word = self.read_u32()
            if self.version >= 2.1:
                num_fields = field_word & 0xFF
                not_builtin = bool((field_word >> 8) & 0x01)
            else:
                num_fields = field_word
                not_builtin = False

        if not_builtin:
            for _ in range(num_fields):
                self.read_string()  # field name
                self.read_string()  # field type

        for _ in range(num_fields):
            fname = self.read_string()
            value = self.read_field_value(fname, node_type)
            node.fields[fname] = value
            self.read_u32()  # field_flags

        if is_group:
            nc = self.read_u32()
            for _ in range(nc):
                child = self.read_node()
                if child is not None:
                    node.children.append(child)

        if def_name:
            self.def_table[def_name] = node

        return node

    def parse(self):
        """Parse all top-level nodes. Returns list of IVNode."""
        nodes = []
        while self.remaining() >= 4:
            node = self.read_node()
            if node is None:
                break
            nodes.append(node)
        return nodes


# ---------------------------------------------------------------------------
# parse_iv - main entry point for parsing
# ---------------------------------------------------------------------------

def parse_iv(filepath, verbose=False):
    """Parse an Open Inventor .iv file. Returns list of IVNode."""
    with open(filepath, 'rb') as f:
        data = f.read()

    # Find header line (handle both \n and \r line endings)
    nl_lf = data.find(b'\x0a')
    nl_cr = data.find(b'\x0d')
    if nl_lf < 0 and nl_cr < 0:
        raise ValueError("Not an Open Inventor file: no header line")
    if nl_lf < 0:
        nl = nl_cr
    elif nl_cr < 0:
        nl = nl_lf
    else:
        nl = min(nl_lf, nl_cr)

    header = data[:nl].decode('ascii', errors='replace').strip()
    if '#Inventor' not in header and '#VRML' not in header:
        raise ValueError(f"Not an Open Inventor file: {header!r}")

    is_binary = 'binary' in header.lower()

    # Determine version
    if 'V2.1' in header:
        version = 2.1
    elif 'V2.0' in header:
        version = 2.0
    elif 'V1.0' in header:
        version = 1.0
    else:
        version = 2.0

    if verbose:
        mode = "binary" if is_binary else "ascii"
        print(f"[IV] File: {filepath} ({len(data)}B, V{version} {mode})",
              file=sys.stderr)

    if is_binary:
        parser = BinaryParser(data, version)
        parser.pos = nl + 1
        # Skip past \r\n combo if present
        if parser.pos < len(data) and data[parser.pos] in (0x0a, 0x0d):
            if data[parser.pos] != data[nl]:
                parser.pos += 1
        nodes = parser.parse()
    else:
        text = data[nl + 1:].decode('ascii', errors='replace')
        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        parser = AsciiParser(text)
        nodes = parser.parse()

    if verbose:
        _print_tree(nodes, 0)

    return nodes


def _print_tree(nodes, depth):
    """Debug: print scene graph tree."""
    indent = "  " * depth
    for n in nodes:
        if isinstance(n, IVUseRef):
            print(f"{indent}USE {n.name}", file=sys.stderr)
            continue
        defstr = f" DEF {n.def_name}" if n.def_name else ""
        fields_str = ", ".join(
            f"{k}={_short_val(v)}" for k, v in n.fields.items())
        print(f"{indent}{n.node_type}{defstr} {{ {fields_str} }}",
              file=sys.stderr)
        if n.children:
            _print_tree(n.children, depth + 1)


def _short_val(v):
    """Abbreviated value for debug printing."""
    if isinstance(v, list):
        if len(v) > 4:
            return f"[{len(v)} items]"
        return str(v)
    if isinstance(v, IVNode):
        return f"<{v.node_type}>"
    return str(v)


# ---------------------------------------------------------------------------
# Scene graph traversal state
# ---------------------------------------------------------------------------

class TraversalState:
    """State accumulated during scene graph traversal."""

    def __init__(self):
        self.transform = _identity_4x4()
        self.coords = []           # list of (x,y,z)
        self.normals = []          # list of (nx,ny,nz)
        self.material_diffuse = [(0.8, 0.8, 0.8)]  # list of (r,g,b)
        self.material_binding = 'OVERALL'
        self.normal_binding = 'PER_VERTEX_INDEXED'
        self.vertex_ordering = 'COUNTERCLOCKWISE'
        self.shape_type = 'UNKNOWN_SHAPE_TYPE'
        self.face_type = 'CONVEX'
        self.crease_angle = 0.0

    def copy(self):
        s = TraversalState()
        s.transform = [row[:] for row in self.transform]
        s.coords = self.coords  # shared reference (copy on write)
        s.normals = self.normals
        s.material_diffuse = self.material_diffuse
        s.material_binding = self.material_binding
        s.normal_binding = self.normal_binding
        s.vertex_ordering = self.vertex_ordering
        s.shape_type = self.shape_type
        s.face_type = self.face_type
        s.crease_angle = self.crease_angle
        return s


# ---------------------------------------------------------------------------
# Transform math utilities
# ---------------------------------------------------------------------------

def _identity_4x4():
    return [[1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]]


def _mat_mul(a, b):
    """Multiply two 4x4 matrices."""
    r = [[0] * 4 for _ in range(4)]
    for i in range(4):
        for j in range(4):
            s = 0.0
            for k in range(4):
                s += a[i][k] * b[k][j]
            r[i][j] = s
    return r


def _translate_mat(tx, ty, tz):
    m = _identity_4x4()
    m[0][3] = tx
    m[1][3] = ty
    m[2][3] = tz
    return m


def _scale_mat(sx, sy, sz):
    m = _identity_4x4()
    m[0][0] = sx
    m[1][1] = sy
    m[2][2] = sz
    return m


def _rotation_mat(ax, ay, az, angle):
    """Build rotation matrix from axis-angle."""
    length = math.sqrt(ax * ax + ay * ay + az * az)
    if length < 1e-12:
        return _identity_4x4()
    ax /= length
    ay /= length
    az /= length
    c = math.cos(angle)
    s = math.sin(angle)
    t = 1.0 - c
    m = _identity_4x4()
    m[0][0] = t * ax * ax + c
    m[0][1] = t * ax * ay - s * az
    m[0][2] = t * ax * az + s * ay
    m[1][0] = t * ax * ay + s * az
    m[1][1] = t * ay * ay + c
    m[1][2] = t * ay * az - s * ax
    m[2][0] = t * ax * az - s * ay
    m[2][1] = t * ay * az + s * ax
    m[2][2] = t * az * az + c
    return m


def _transform_point(mat, p):
    """Transform a 3D point by a 4x4 matrix."""
    x = mat[0][0] * p[0] + mat[0][1] * p[1] + mat[0][2] * p[2] + mat[0][3]
    y = mat[1][0] * p[0] + mat[1][1] * p[1] + mat[1][2] * p[2] + mat[1][3]
    z = mat[2][0] * p[0] + mat[2][1] * p[1] + mat[2][2] * p[2] + mat[2][3]
    return (x, y, z)


def _transform_normal(mat, n):
    """Transform a normal by the upper-left 3x3 of a 4x4 matrix.
    Uses the transpose of the inverse. For uniform scale, just
    transform and renormalize."""
    x = mat[0][0] * n[0] + mat[0][1] * n[1] + mat[0][2] * n[2]
    y = mat[1][0] * n[0] + mat[1][1] * n[1] + mat[1][2] * n[2]
    z = mat[2][0] * n[0] + mat[2][1] * n[1] + mat[2][2] * n[2]
    length = math.sqrt(x * x + y * y + z * z)
    if length > 1e-12:
        return (x / length, y / length, z / length)
    return (0, 1, 0)


def _build_transform_matrix(fields):
    """Build a 4x4 transform matrix from Transform node fields.

    Transform order: T * C * R * SO * S * SO^-1 * C^-1
    """
    t = fields.get('translation', (0, 0, 0))
    r = fields.get('rotation', (0, 0, 1, 0))
    s = fields.get('scaleFactor', (1, 1, 1))
    so = fields.get('scaleOrientation', (0, 0, 1, 0))
    c = fields.get('center', (0, 0, 0))

    mat = _identity_4x4()

    # T
    if t != (0, 0, 0):
        mat = _mat_mul(mat, _translate_mat(*t))

    # C
    if c != (0, 0, 0):
        mat = _mat_mul(mat, _translate_mat(*c))

    # R
    if len(r) >= 4 and abs(r[3]) > 1e-12:
        mat = _mat_mul(mat, _rotation_mat(r[0], r[1], r[2], r[3]))

    # SO
    has_so = len(so) >= 4 and abs(so[3]) > 1e-12
    if has_so:
        mat = _mat_mul(mat, _rotation_mat(so[0], so[1], so[2], so[3]))

    # S
    if s != (1, 1, 1):
        mat = _mat_mul(mat, _scale_mat(*s))

    # SO^-1
    if has_so:
        mat = _mat_mul(mat, _rotation_mat(so[0], so[1], so[2], -so[3]))

    # C^-1
    if c != (0, 0, 0):
        mat = _mat_mul(mat, _translate_mat(-c[0], -c[1], -c[2]))

    return mat


def _fields_to_4x4(raw):
    """Convert a flat 16-element list to a 4x4 column-major matrix.
    Open Inventor stores matrices row-major with row vectors (v * M),
    but our _transform_point uses column vectors (M * v), so we
    transpose: mat[col][row] = raw[row * 4 + col]."""
    if not raw or len(raw) < 16:
        return _identity_4x4()
    return [[raw[j * 4 + i] for j in range(4)] for i in range(4)]


# ---------------------------------------------------------------------------
# Primitive shape generators
# ---------------------------------------------------------------------------

def _generate_cube(width=2.0, height=2.0, depth=2.0):
    """Generate a unit cube mesh centered at origin.

    Returns (positions, normals, indices)."""
    hw, hh, hd = width / 2.0, height / 2.0, depth / 2.0
    # 6 faces, 4 verts each = 24 verts
    positions = [
        # +Z face
        (-hw, -hh, hd), (hw, -hh, hd), (hw, hh, hd), (-hw, hh, hd),
        # -Z face
        (hw, -hh, -hd), (-hw, -hh, -hd), (-hw, hh, -hd), (hw, hh, -hd),
        # +Y face
        (-hw, hh, hd), (hw, hh, hd), (hw, hh, -hd), (-hw, hh, -hd),
        # -Y face
        (-hw, -hh, -hd), (hw, -hh, -hd), (hw, -hh, hd), (-hw, -hh, hd),
        # +X face
        (hw, -hh, hd), (hw, -hh, -hd), (hw, hh, -hd), (hw, hh, hd),
        # -X face
        (-hw, -hh, -hd), (-hw, -hh, hd), (-hw, hh, hd), (-hw, hh, -hd),
    ]
    normals = [
        (0, 0, 1)] * 4 + [(0, 0, -1)] * 4 + \
        [(0, 1, 0)] * 4 + [(0, -1, 0)] * 4 + \
        [(1, 0, 0)] * 4 + [(-1, 0, 0)] * 4
    indices = []
    for face in range(6):
        b = face * 4
        indices.extend([b, b + 1, b + 2, b, b + 2, b + 3])
    return positions, normals, indices


def _generate_sphere(radius=1.0, slices=16, stacks=12):
    """Generate a sphere mesh. Returns (positions, normals, indices)."""
    positions = []
    normals = []
    indices = []

    for j in range(stacks + 1):
        phi = math.pi * j / stacks
        sp = math.sin(phi)
        cp = math.cos(phi)
        for i in range(slices + 1):
            theta = 2.0 * math.pi * i / slices
            st = math.sin(theta)
            ct = math.cos(theta)
            nx, ny, nz = sp * ct, cp, sp * st
            positions.append((radius * nx, radius * ny, radius * nz))
            normals.append((nx, ny, nz))

    for j in range(stacks):
        for i in range(slices):
            a = j * (slices + 1) + i
            b = a + slices + 1
            indices.extend([a, b, a + 1, a + 1, b, b + 1])

    return positions, normals, indices


def _generate_cone(bottom_radius=1.0, height=2.0, slices=16,
                   parts='ALL'):
    """Generate a cone mesh. Returns (positions, normals, indices)."""
    positions = []
    normals = []
    indices = []
    hh = height / 2.0
    has_sides = parts == 'ALL' or (isinstance(parts, (list, str)) and
                                    'SIDES' in str(parts))
    has_bottom = parts == 'ALL' or (isinstance(parts, (list, str)) and
                                     'BOTTOM' in str(parts))
    if parts == 'ALL' or parts is None:
        has_sides = True
        has_bottom = True

    if has_sides:
        # Apex
        apex_idx = len(positions)
        positions.append((0, hh, 0))
        normals.append((0, 1, 0))
        # Base ring
        slope = bottom_radius / height
        ny = 1.0 / math.sqrt(1 + slope * slope)
        nr = slope * ny
        for i in range(slices + 1):
            theta = 2.0 * math.pi * i / slices
            ct, st = math.cos(theta), math.sin(theta)
            positions.append(
                (bottom_radius * ct, -hh, bottom_radius * st))
            normals.append((nr * ct, ny, nr * st))
        for i in range(slices):
            b = apex_idx + 1 + i
            indices.extend([apex_idx, b, b + 1])

    if has_bottom:
        center_idx = len(positions)
        positions.append((0, -hh, 0))
        normals.append((0, -1, 0))
        for i in range(slices + 1):
            theta = 2.0 * math.pi * i / slices
            ct, st = math.cos(theta), math.sin(theta)
            positions.append(
                (bottom_radius * ct, -hh, bottom_radius * st))
            normals.append((0, -1, 0))
        for i in range(slices):
            b = center_idx + 1 + i
            indices.extend([center_idx, b + 1, b])

    return positions, normals, indices


def _generate_cylinder(radius=1.0, height=2.0, slices=16,
                       parts='ALL'):
    """Generate a cylinder mesh. Returns (positions, normals, indices)."""
    positions = []
    normals = []
    indices = []
    hh = height / 2.0
    has_sides = True
    has_top = True
    has_bottom = True

    if isinstance(parts, list):
        pset = set(parts)
        if 'ALL' not in pset:
            has_sides = 'SIDES' in pset
            has_top = 'TOP' in pset
            has_bottom = 'BOTTOM' in pset
    elif isinstance(parts, str) and parts not in ('ALL', ''):
        has_sides = 'SIDES' in parts
        has_top = 'TOP' in parts
        has_bottom = 'BOTTOM' in parts

    if has_sides:
        base = len(positions)
        for ring in range(2):
            y = hh if ring == 0 else -hh
            for i in range(slices + 1):
                theta = 2.0 * math.pi * i / slices
                ct, st = math.cos(theta), math.sin(theta)
                positions.append((radius * ct, y, radius * st))
                normals.append((ct, 0, st))
        for i in range(slices):
            a = base + i
            b = a + slices + 1
            indices.extend([a, b, a + 1, a + 1, b, b + 1])

    if has_top:
        center_idx = len(positions)
        positions.append((0, hh, 0))
        normals.append((0, 1, 0))
        for i in range(slices + 1):
            theta = 2.0 * math.pi * i / slices
            ct, st = math.cos(theta), math.sin(theta)
            positions.append((radius * ct, hh, radius * st))
            normals.append((0, 1, 0))
        for i in range(slices):
            b = center_idx + 1 + i
            indices.extend([center_idx, b, b + 1])

    if has_bottom:
        center_idx = len(positions)
        positions.append((0, -hh, 0))
        normals.append((0, -1, 0))
        for i in range(slices + 1):
            theta = 2.0 * math.pi * i / slices
            ct, st = math.cos(theta), math.sin(theta)
            positions.append((radius * ct, -hh, radius * st))
            normals.append((0, -1, 0))
        for i in range(slices):
            b = center_idx + 1 + i
            indices.extend([center_idx, b + 1, b])

    return positions, normals, indices


# ---------------------------------------------------------------------------
# Geometry collection from shape nodes
# ---------------------------------------------------------------------------

class CollectedMesh:
    """A mesh collected from a shape node with baked transforms."""
    __slots__ = ('positions', 'normals', 'indices', 'diffuse_color')

    def __init__(self):
        self.positions = []
        self.normals = []
        self.indices = []
        self.diffuse_color = (0.8, 0.8, 0.8)


def _get_coords_and_normals(state, node):
    """Get coordinates and normals, checking VertexProperty first."""
    coords = list(state.coords)
    norms = list(state.normals)
    normal_binding = state.normal_binding
    material_binding = state.material_binding
    diffuse_colors = state.material_diffuse

    vp = node.fields.get('vertexProperty')
    if isinstance(vp, IVNode) and vp.node_type == 'VertexProperty':
        vp_verts = vp.fields.get('vertex')
        if vp_verts:
            coords = _to_vec3_list(vp_verts)
        vp_norms = vp.fields.get('normal')
        if vp_norms:
            norms = _to_vec3_list(vp_norms)
        nb = vp.fields.get('normalBinding')
        if nb:
            normal_binding = nb
        mb = vp.fields.get('materialBinding')
        if mb:
            material_binding = mb

    return coords, norms, normal_binding, material_binding, diffuse_colors


def _to_vec3_list(val):
    """Convert a field value to a list of (x,y,z) tuples."""
    if isinstance(val, list):
        if len(val) == 0:
            return []
        if isinstance(val[0], tuple):
            return val
        # Flat list of numbers -> group into triples
        result = []
        i = 0
        while i + 2 < len(val):
            result.append((float(val[i]), float(val[i + 1]),
                           float(val[i + 2])))
            i += 3
        return result
    return []


def _to_int_list(val):
    """Convert a field value to a flat list of ints."""
    if isinstance(val, list):
        return [int(v) for v in val]
    if isinstance(val, (int, float)):
        return [int(val)]
    return []


def _to_float_list(val):
    """Convert a field value to a flat list of floats."""
    if isinstance(val, list):
        return [float(v) for v in val]
    if isinstance(val, (int, float)):
        return [float(val)]
    return []


def _split_by_neg1(indices):
    """Split a -1-delimited index list into sublists (faces/strips)."""
    faces = []
    current = []
    for idx in indices:
        if idx < 0:
            if current:
                faces.append(current)
                current = []
        else:
            current.append(idx)
    if current:
        faces.append(current)
    return faces


def _compute_face_normal(positions, face_indices):
    """Compute the face normal from vertex positions using Newell's method."""
    nx, ny, nz = 0.0, 0.0, 0.0
    n = len(face_indices)
    for i in range(n):
        v0 = positions[face_indices[i]]
        v1 = positions[face_indices[(i + 1) % n]]
        nx += (v0[1] - v1[1]) * (v0[2] + v1[2])
        ny += (v0[2] - v1[2]) * (v0[0] + v1[0])
        nz += (v0[0] - v1[0]) * (v0[1] + v1[1])
    length = math.sqrt(nx * nx + ny * ny + nz * nz)
    if length > 1e-12:
        return (nx / length, ny / length, nz / length)
    return (0, 1, 0)


def _collect_indexed_face_set(node, state, transform):
    """Collect geometry from an IndexedFaceSet node."""
    coords, norms, normal_binding, mat_binding, diff_colors = \
        _get_coords_and_normals(state, node)

    coord_index = _to_int_list(node.fields.get('coordIndex', []))
    normal_index = _to_int_list(node.fields.get('normalIndex', []))
    if not coord_index or not coords:
        return None

    faces = _split_by_neg1(coord_index)
    normal_faces = _split_by_neg1(normal_index) if normal_index else []

    mesh = CollectedMesh()
    # Get primary diffuse color
    if diff_colors and len(diff_colors) > 0:
        c = diff_colors[0]
        if isinstance(c, (list, tuple)) and len(c) >= 3:
            mesh.diffuse_color = (float(c[0]), float(c[1]), float(c[2]))

    ccw = state.vertex_ordering != 'CLOCKWISE'

    for fi, face in enumerate(faces):
        if len(face) < 3:
            continue
        # Validate indices
        valid = True
        for idx in face:
            if idx < 0 or idx >= len(coords):
                valid = False
                break
        if not valid:
            continue

        # Get face vertices
        face_verts = [coords[idx] for idx in face]

        # Determine normals for this face
        face_normals = []
        nb = normal_binding
        # Normalize binding names
        if 'PER_VERTEX' in nb and 'INDEXED' in nb:
            # PER_VERTEX_INDEXED: use normalIndex
            if fi < len(normal_faces):
                nf = normal_faces[fi]
                for ni_idx in nf:
                    if 0 <= ni_idx < len(norms):
                        face_normals.append(norms[ni_idx])
                    else:
                        face_normals.append((0, 1, 0))
            if not face_normals and norms:
                # Fallback: use coord indices into normals
                for idx in face:
                    if 0 <= idx < len(norms):
                        face_normals.append(norms[idx])
                    else:
                        face_normals.append((0, 1, 0))
        elif 'PER_VERTEX' in nb:
            # PER_VERTEX: normals consumed per vertex
            for idx in face:
                if 0 <= idx < len(norms):
                    face_normals.append(norms[idx])
                else:
                    face_normals.append((0, 1, 0))
        elif 'PER_FACE' in nb and 'INDEXED' in nb:
            # PER_FACE_INDEXED: one normal per face via normalIndex
            if fi < len(normal_index) and 0 <= normal_index[fi] < len(norms):
                fn = norms[normal_index[fi]]
            else:
                fn = _compute_face_normal(coords, face)
            face_normals = [fn] * len(face)
        elif 'PER_FACE' in nb:
            if fi < len(norms):
                fn = norms[fi]
            else:
                fn = _compute_face_normal(coords, face)
            face_normals = [fn] * len(face)
        elif nb == 'OVERALL':
            if norms:
                fn = norms[0]
            else:
                fn = _compute_face_normal(coords, face)
            face_normals = [fn] * len(face)
        else:
            # Default: use per-vertex if available, else compute
            for idx in face:
                if 0 <= idx < len(norms):
                    face_normals.append(norms[idx])
                else:
                    face_normals.append(_compute_face_normal(coords, face))

        if not face_normals:
            fn = _compute_face_normal(coords, face)
            face_normals = [fn] * len(face)

        # Transform vertices and normals
        transformed_verts = [_transform_point(transform, v)
                             for v in face_verts]
        transformed_norms = [_transform_normal(transform, n)
                             for n in face_normals]

        # Build local face with indices into mesh arrays
        base = len(mesh.positions)
        for i in range(len(face)):
            mesh.positions.append(transformed_verts[i])
            mesh.normals.append(transformed_norms[i])

        local_face = list(range(base, base + len(face)))

        # Reverse winding if clockwise
        if not ccw:
            local_face = list(reversed(local_face))

        # Triangulate
        fn = _compute_face_normal(
            mesh.positions, local_face)
        if len(local_face) == 3:
            mesh.indices.extend(local_face)
        elif len(local_face) == 4:
            # Quad split
            mesh.indices.extend([
                local_face[0], local_face[1], local_face[2],
                local_face[0], local_face[2], local_face[3]])
        else:
            if is_convex_polygon(local_face, mesh.positions, fn):
                tris = fan_triangulate(local_face, mesh.positions, fn)
            else:
                tris = ear_clip(local_face, mesh.positions, fn)
            mesh.indices.extend(tris)

    if not mesh.positions or not mesh.indices:
        return None
    return mesh


def _collect_indexed_tri_strip_set(node, state, transform):
    """Collect geometry from an IndexedTriangleStripSet node."""
    coords, norms, normal_binding, mat_binding, diff_colors = \
        _get_coords_and_normals(state, node)

    coord_index = _to_int_list(node.fields.get('coordIndex', []))
    normal_index = _to_int_list(node.fields.get('normalIndex', []))
    if not coord_index or not coords:
        return None

    strips = _split_by_neg1(coord_index)
    normal_strips = _split_by_neg1(normal_index) if normal_index else []

    mesh = CollectedMesh()
    if diff_colors and len(diff_colors) > 0:
        c = diff_colors[0]
        if isinstance(c, (list, tuple)) and len(c) >= 3:
            mesh.diffuse_color = (float(c[0]), float(c[1]), float(c[2]))

    ccw = state.vertex_ordering != 'CLOCKWISE'

    for si, strip in enumerate(strips):
        if len(strip) < 3:
            continue

        n_strip = normal_strips[si] if si < len(normal_strips) else []

        for i in range(len(strip) - 2):
            i0, i1, i2 = strip[i], strip[i + 1], strip[i + 2]
            if i0 == i1 or i1 == i2 or i0 == i2:
                continue
            if (i0 >= len(coords) or i1 >= len(coords) or
                    i2 >= len(coords)):
                continue

            # Alternate winding for triangle strips
            if (i % 2 == 0) == ccw:
                tri_idx = [i0, i1, i2]
            else:
                tri_idx = [i0, i2, i1]

            # Get normals
            tri_norms = []
            for j, vi in enumerate(tri_idx):
                ni = i + j
                if n_strip and ni < len(n_strip):
                    nidx = n_strip[ni]
                    if 0 <= nidx < len(norms):
                        tri_norms.append(norms[nidx])
                        continue
                if vi < len(norms):
                    tri_norms.append(norms[vi])
                else:
                    v0 = coords[tri_idx[0]]
                    v1 = coords[tri_idx[1]]
                    v2 = coords[tri_idx[2]]
                    e1 = (v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2])
                    e2 = (v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2])
                    nx = e1[1] * e2[2] - e1[2] * e2[1]
                    ny = e1[2] * e2[0] - e1[0] * e2[2]
                    nz = e1[0] * e2[1] - e1[1] * e2[0]
                    nl = math.sqrt(nx * nx + ny * ny + nz * nz)
                    if nl > 1e-12:
                        tri_norms.append((nx / nl, ny / nl, nz / nl))
                    else:
                        tri_norms.append((0, 1, 0))

            # Transform and add
            base = len(mesh.positions)
            for j in range(3):
                mesh.positions.append(
                    _transform_point(transform, coords[tri_idx[j]]))
                mesh.normals.append(
                    _transform_normal(transform, tri_norms[j]))
            mesh.indices.extend([base, base + 1, base + 2])

    if not mesh.positions or not mesh.indices:
        return None
    return mesh


def _collect_face_set(node, state, transform):
    """Collect geometry from a FaceSet node."""
    coords, norms, normal_binding, mat_binding, diff_colors = \
        _get_coords_and_normals(state, node)

    num_vertices = _to_int_list(node.fields.get('numVertices', []))
    if not num_vertices or not coords:
        return None

    mesh = CollectedMesh()
    if diff_colors and len(diff_colors) > 0:
        c = diff_colors[0]
        if isinstance(c, (list, tuple)) and len(c) >= 3:
            mesh.diffuse_color = (float(c[0]), float(c[1]), float(c[2]))

    ccw = state.vertex_ordering != 'CLOCKWISE'
    vertex_offset = 0

    for fi, nv in enumerate(num_vertices):
        nv = int(nv)
        if nv < 3:
            vertex_offset += nv
            continue
        if vertex_offset + nv > len(coords):
            break

        face_verts = coords[vertex_offset:vertex_offset + nv]

        # Determine normals
        face_normals = []
        nb = normal_binding
        if 'PER_VERTEX' in nb:
            for i in range(nv):
                vi = vertex_offset + i
                if vi < len(norms):
                    face_normals.append(norms[vi])
                else:
                    face_normals.append(
                        _compute_face_normal(coords,
                                             list(range(vertex_offset,
                                                        vertex_offset + nv))))
        elif 'PER_FACE' in nb:
            if fi < len(norms):
                fn = norms[fi]
            else:
                fn = _compute_face_normal(
                    coords,
                    list(range(vertex_offset, vertex_offset + nv)))
            face_normals = [fn] * nv
        elif nb == 'OVERALL':
            fn = norms[0] if norms else _compute_face_normal(
                coords,
                list(range(vertex_offset, vertex_offset + nv)))
            face_normals = [fn] * nv
        else:
            fn = _compute_face_normal(
                coords, list(range(vertex_offset, vertex_offset + nv)))
            face_normals = [fn] * nv

        # Transform
        transformed_verts = [_transform_point(transform, v)
                             for v in face_verts]
        transformed_norms = [_transform_normal(transform, n)
                             for n in face_normals]

        base = len(mesh.positions)
        for i in range(nv):
            mesh.positions.append(transformed_verts[i])
            mesh.normals.append(transformed_norms[i])

        local_face = list(range(base, base + nv))
        if not ccw:
            local_face = list(reversed(local_face))

        fn = _compute_face_normal(mesh.positions, local_face)
        if nv == 3:
            mesh.indices.extend(local_face)
        elif nv == 4:
            mesh.indices.extend([
                local_face[0], local_face[1], local_face[2],
                local_face[0], local_face[2], local_face[3]])
        else:
            if is_convex_polygon(local_face, mesh.positions, fn):
                tris = fan_triangulate(local_face, mesh.positions, fn)
            else:
                tris = ear_clip(local_face, mesh.positions, fn)
            mesh.indices.extend(tris)

        vertex_offset += nv

    if not mesh.positions or not mesh.indices:
        return None
    return mesh


def _collect_triangle_strip_set(node, state, transform):
    """Collect geometry from a TriangleStripSet node."""
    coords, norms, normal_binding, mat_binding, diff_colors = \
        _get_coords_and_normals(state, node)

    num_vertices = _to_int_list(node.fields.get('numVertices', []))
    start_index = int(node.fields.get('startIndex', 0))
    if not num_vertices or not coords:
        return None

    mesh = CollectedMesh()
    if diff_colors and len(diff_colors) > 0:
        c = diff_colors[0]
        if isinstance(c, (list, tuple)) and len(c) >= 3:
            mesh.diffuse_color = (float(c[0]), float(c[1]), float(c[2]))

    ccw = state.vertex_ordering != 'CLOCKWISE'
    vertex_offset = start_index

    for nv in num_vertices:
        nv = int(nv)
        if nv < 3:
            vertex_offset += nv
            continue
        if vertex_offset + nv > len(coords):
            break

        for i in range(nv - 2):
            i0 = vertex_offset + i
            i1 = vertex_offset + i + 1
            i2 = vertex_offset + i + 2
            if i0 >= len(coords) or i1 >= len(coords) or i2 >= len(coords):
                continue

            if (i % 2 == 0) == ccw:
                tri_idx = [i0, i1, i2]
            else:
                tri_idx = [i0, i2, i1]

            tri_norms = []
            for vi in tri_idx:
                if vi < len(norms):
                    tri_norms.append(norms[vi])
                else:
                    v0 = coords[tri_idx[0]]
                    v1 = coords[tri_idx[1]]
                    v2 = coords[tri_idx[2]]
                    e1 = (v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2])
                    e2 = (v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2])
                    nx = e1[1] * e2[2] - e1[2] * e2[1]
                    ny = e1[2] * e2[0] - e1[0] * e2[2]
                    nz = e1[0] * e2[1] - e1[1] * e2[0]
                    nl = math.sqrt(nx * nx + ny * ny + nz * nz)
                    if nl > 1e-12:
                        tri_norms.append((nx / nl, ny / nl, nz / nl))
                    else:
                        tri_norms.append((0, 1, 0))

            base = len(mesh.positions)
            for j in range(3):
                mesh.positions.append(
                    _transform_point(transform, coords[tri_idx[j]]))
                mesh.normals.append(
                    _transform_normal(transform, tri_norms[j]))
            mesh.indices.extend([base, base + 1, base + 2])

        vertex_offset += nv

    if not mesh.positions or not mesh.indices:
        return None
    return mesh


def _collect_quad_mesh(node, state, transform):
    """Collect geometry from a QuadMesh node."""
    coords, norms, normal_binding, mat_binding, diff_colors = \
        _get_coords_and_normals(state, node)

    rows = int(node.fields.get('verticesPerRow', 0))
    cols = int(node.fields.get('verticesPerColumn', 0))
    if rows < 2 or cols < 2 or not coords:
        return None

    mesh = CollectedMesh()
    if diff_colors and len(diff_colors) > 0:
        c = diff_colors[0]
        if isinstance(c, (list, tuple)) and len(c) >= 3:
            mesh.diffuse_color = (float(c[0]), float(c[1]), float(c[2]))

    ccw = state.vertex_ordering != 'CLOCKWISE'

    # Transform all vertices
    t_coords = [_transform_point(transform, c) for c in coords]
    t_norms = []
    for i, n in enumerate(norms):
        t_norms.append(_transform_normal(transform, n))

    # Generate quads from grid
    for r in range(cols - 1):
        for c in range(rows - 1):
            i00 = r * rows + c
            i10 = r * rows + c + 1
            i01 = (r + 1) * rows + c
            i11 = (r + 1) * rows + c + 1

            if i11 >= len(t_coords):
                continue

            quad = [i00, i10, i11, i01]
            if not ccw:
                quad = [i00, i01, i11, i10]

            # Get normals for each vertex
            for vi in quad:
                base = len(mesh.positions)
                mesh.positions.append(t_coords[vi])
                if vi < len(t_norms):
                    mesh.normals.append(t_norms[vi])
                else:
                    fn = _compute_face_normal(t_coords, quad)
                    mesh.normals.append(fn)

            base = len(mesh.positions) - 4
            mesh.indices.extend([
                base, base + 1, base + 2,
                base, base + 2, base + 3])

    if not mesh.positions or not mesh.indices:
        return None
    return mesh


def _collect_primitive_shape(node, state, transform):
    """Collect geometry from Cube, Sphere, Cone, Cylinder."""
    node_type = node.node_type
    diff_colors = state.material_diffuse

    if node_type == 'Cube':
        w = float(node.fields.get('width', 2.0))
        h = float(node.fields.get('height', 2.0))
        d = float(node.fields.get('depth', 2.0))
        positions, normals, indices = _generate_cube(w, h, d)
    elif node_type == 'Sphere':
        r = float(node.fields.get('radius', 1.0))
        positions, normals, indices = _generate_sphere(r)
    elif node_type == 'Cone':
        br = float(node.fields.get('bottomRadius', 1.0))
        h = float(node.fields.get('height', 2.0))
        parts = node.fields.get('parts', 'ALL')
        positions, normals, indices = _generate_cone(br, h, parts=parts)
    elif node_type == 'Cylinder':
        r = float(node.fields.get('radius', 1.0))
        h = float(node.fields.get('height', 2.0))
        parts = node.fields.get('parts', 'ALL')
        positions, normals, indices = _generate_cylinder(r, h, parts=parts)
    else:
        return None

    if not positions or not indices:
        return None

    mesh = CollectedMesh()
    if diff_colors and len(diff_colors) > 0:
        c = diff_colors[0]
        if isinstance(c, (list, tuple)) and len(c) >= 3:
            mesh.diffuse_color = (float(c[0]), float(c[1]), float(c[2]))

    # Transform all positions and normals
    for p in positions:
        mesh.positions.append(_transform_point(transform, p))
    for n in normals:
        mesh.normals.append(_transform_normal(transform, n))
    mesh.indices = indices

    return mesh


# ---------------------------------------------------------------------------
# Scene graph traversal
# ---------------------------------------------------------------------------

SHAPE_NODES = {
    'IndexedFaceSet', 'IndexedTriangleStripSet', 'FaceSet',
    'TriangleStripSet', 'QuadMesh', 'Cube', 'Sphere', 'Cone', 'Cylinder',
}


def _traverse(nodes, state, meshes, verbose=False):
    """Walk the scene graph collecting geometry.

    State inheritance:
    - Separator: pushes/pops state
    - Group/other groups: state changes persist to siblings
    - Material, Transform, Coordinate3, Normal, etc.: modify state
    - Shape nodes: collect geometry using current state
    """
    for node in nodes:
        if isinstance(node, IVUseRef):
            continue
        if not isinstance(node, IVNode):
            continue

        nt = node.node_type

        # --- State nodes ---
        if nt == 'Coordinate3':
            val = node.fields.get('point', [])
            state.coords = _to_vec3_list(val)

        elif nt == 'Normal':
            val = node.fields.get('vector', [])
            state.normals = _to_vec3_list(val)

        elif nt == 'Material':
            dc = node.fields.get('diffuseColor')
            if dc is not None:
                if isinstance(dc, list) and len(dc) > 0:
                    if isinstance(dc[0], (list, tuple)):
                        state.material_diffuse = [
                            tuple(float(x) for x in c) for c in dc]
                    elif isinstance(dc[0], (int, float)):
                        # Flat list or single color
                        floats = [float(x) for x in dc]
                        if len(floats) >= 3:
                            colors = []
                            for i in range(0, len(floats) - 2, 3):
                                colors.append(
                                    (floats[i], floats[i + 1], floats[i + 2]))
                            if colors:
                                state.material_diffuse = colors
                elif isinstance(dc, tuple) and len(dc) >= 3:
                    state.material_diffuse = [
                        (float(dc[0]), float(dc[1]), float(dc[2]))]

        elif nt == 'BaseColor':
            rgb = node.fields.get('rgb')
            if rgb is not None:
                if isinstance(rgb, list) and len(rgb) > 0:
                    if isinstance(rgb[0], (list, tuple)):
                        state.material_diffuse = [
                            tuple(float(x) for x in c) for c in rgb]
                    elif isinstance(rgb[0], (int, float)):
                        floats = [float(x) for x in rgb]
                        if len(floats) >= 3:
                            colors = []
                            for i in range(0, len(floats) - 2, 3):
                                colors.append(
                                    (floats[i], floats[i + 1], floats[i + 2]))
                            if colors:
                                state.material_diffuse = colors

        elif nt == 'MaterialBinding':
            val = node.fields.get('value', 'OVERALL')
            if isinstance(val, str):
                state.material_binding = val

        elif nt == 'NormalBinding':
            val = node.fields.get('value', 'PER_VERTEX_INDEXED')
            if isinstance(val, str):
                state.normal_binding = val

        elif nt == 'ShapeHints':
            vo = node.fields.get('vertexOrdering')
            if vo:
                state.vertex_ordering = vo
            st = node.fields.get('shapeType')
            if st:
                state.shape_type = st
            ft = node.fields.get('faceType')
            if ft:
                state.face_type = ft
            ca = node.fields.get('creaseAngle')
            if ca is not None:
                state.crease_angle = float(ca)

        elif nt == 'Transform':
            mat = _build_transform_matrix(node.fields)
            state.transform = _mat_mul(state.transform, mat)

        elif nt == 'MatrixTransform':
            raw = node.fields.get('matrix', [])
            mat = _fields_to_4x4(raw)
            state.transform = _mat_mul(state.transform, mat)

        elif nt == 'Translation':
            t = node.fields.get('translation', (0, 0, 0))
            if isinstance(t, (list, tuple)) and len(t) >= 3:
                mat = _translate_mat(float(t[0]), float(t[1]), float(t[2]))
                state.transform = _mat_mul(state.transform, mat)

        elif nt == 'Scale':
            s = node.fields.get('scaleFactor', (1, 1, 1))
            if isinstance(s, (list, tuple)) and len(s) >= 3:
                mat = _scale_mat(float(s[0]), float(s[1]), float(s[2]))
                state.transform = _mat_mul(state.transform, mat)

        elif nt == 'Rotation':
            r = node.fields.get('rotation', (0, 0, 1, 0))
            if isinstance(r, (list, tuple)) and len(r) >= 4:
                mat = _rotation_mat(float(r[0]), float(r[1]),
                                    float(r[2]), float(r[3]))
                state.transform = _mat_mul(state.transform, mat)

        elif nt == 'RotationXYZ':
            axis = node.fields.get('axis', 'X')
            angle = float(node.fields.get('angle', 0))
            if axis == 'X' or axis == '0':
                mat = _rotation_mat(1, 0, 0, angle)
            elif axis == 'Y' or axis == '1':
                mat = _rotation_mat(0, 1, 0, angle)
            else:
                mat = _rotation_mat(0, 0, 1, angle)
            state.transform = _mat_mul(state.transform, mat)

        # --- Group nodes ---
        elif nt == 'Separator':
            saved = state.copy()
            saved.transform = [row[:] for row in state.transform]
            _traverse(node.children, state, meshes, verbose)
            # Restore state
            state.transform = saved.transform
            state.coords = saved.coords
            state.normals = saved.normals
            state.material_diffuse = saved.material_diffuse
            state.material_binding = saved.material_binding
            state.normal_binding = saved.normal_binding
            state.vertex_ordering = saved.vertex_ordering
            state.shape_type = saved.shape_type
            state.face_type = saved.face_type
            state.crease_angle = saved.crease_angle
            continue  # Don't process children again

        elif nt == 'TransformSeparator':
            saved_transform = [row[:] for row in state.transform]
            _traverse(node.children, state, meshes, verbose)
            state.transform = saved_transform
            continue

        elif nt in GROUP_NODES:
            # Group, Switch, LOD, etc. - traverse children
            # For Switch, ideally only render whichChild
            if nt == 'Switch':
                wc = node.fields.get('whichChild', -1)
                if isinstance(wc, int) and 0 <= wc < len(node.children):
                    _traverse([node.children[wc]], state, meshes, verbose)
                elif wc == -3:  # SO_SWITCH_ALL
                    _traverse(node.children, state, meshes, verbose)
                # else: SO_SWITCH_NONE (-1) or inherit (-2)
            elif nt == 'LOD' or nt == 'LevelOfDetail':
                # Use highest detail (first child)
                if node.children:
                    _traverse([node.children[0]], state, meshes, verbose)
            else:
                _traverse(node.children, state, meshes, verbose)
            continue

        # --- Shape nodes ---
        if nt in SHAPE_NODES:
            mesh = None
            try:
                if nt == 'IndexedFaceSet':
                    mesh = _collect_indexed_face_set(
                        node, state, state.transform)
                elif nt == 'IndexedTriangleStripSet':
                    mesh = _collect_indexed_tri_strip_set(
                        node, state, state.transform)
                elif nt == 'FaceSet':
                    mesh = _collect_face_set(
                        node, state, state.transform)
                elif nt == 'TriangleStripSet':
                    mesh = _collect_triangle_strip_set(
                        node, state, state.transform)
                elif nt == 'QuadMesh':
                    mesh = _collect_quad_mesh(
                        node, state, state.transform)
                elif nt in ('Cube', 'Sphere', 'Cone', 'Cylinder'):
                    mesh = _collect_primitive_shape(
                        node, state, state.transform)
            except Exception as e:
                if verbose:
                    print(f"[IV] Warning: Failed to collect {nt}: {e}",
                          file=sys.stderr)

            if mesh:
                meshes.append(mesh)
                if verbose:
                    print(f"[IV]   Collected {nt}: "
                          f"{len(mesh.positions)} verts, "
                          f"{len(mesh.indices) // 3} tris",
                          file=sys.stderr)

        # Also process children of non-group nodes that have children
        # (e.g., custom extension nodes)
        if node.children and nt not in GROUP_NODES and nt != 'Separator':
            _traverse(node.children, state, meshes, verbose)


# ---------------------------------------------------------------------------
# convert_to_glb - build GLB output
# ---------------------------------------------------------------------------

def convert_to_glb(nodes, output_path, verbose=False):
    """Convert parsed IV scene graph to GLB.

    Args:
        nodes: list of IVNode from parse_iv()
        output_path: path to write GLB file
        verbose: enable debug output
    """
    # Traverse to collect meshes
    state = TraversalState()
    meshes = []
    _traverse(nodes, state, meshes, verbose)

    if verbose:
        print(f"[IV] Collected {len(meshes)} meshes", file=sys.stderr)

    builder = GLBBuilder(verbose=verbose)

    if not meshes:
        glb_data = builder.build_glb(generator="poly2glb-openinventor")
        with open(output_path, 'wb') as f:
            f.write(glb_data)
        return

    # Build materials: deduplicate by color
    color_to_mat = {}
    total_tris = 0

    for mesh in meshes:
        color = mesh.diffuse_color
        color_key = (round(color[0], 4), round(color[1], 4),
                     round(color[2], 4))

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

        mi = color_to_mat[color_key]

        prim = builder.build_primitive(
            mesh.positions, mesh.normals, mesh.indices, material_idx=mi)
        if prim:
            total_tris += len(mesh.indices) // 3
            mesh_idx = len(builder.meshes)
            builder.meshes.append({"primitives": [prim]})
            node_idx = len(builder.nodes)
            builder.nodes.append({"mesh": mesh_idx})
            builder.scene_nodes.append(node_idx)

    glb_data = builder.build_glb(generator="poly2glb-openinventor")
    with open(output_path, 'wb') as f:
        f.write(glb_data)

    if verbose:
        print(f"[IV] Output: {total_tris} tris, "
              f"{len(meshes)} meshes, {len(color_to_mat)} materials",
              file=sys.stderr)

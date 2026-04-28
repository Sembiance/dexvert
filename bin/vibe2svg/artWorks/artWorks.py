#!/usr/bin/env python3
# Vibe coded by Claude

"""ArtWorks RISC OS vector image to SVG converter.

Converts ArtWorks (.aff) files to SVG format. Handles path objects with
fill/stroke colors (flat and gradient), line widths, groups, layers, and
text objects.

Usage: python3 artWorks.py <inputFile> <outputDir>
"""

import struct
import sys
import os
import math
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement

MAGIC1 = b'Top!'
MAGIC2 = b'TopDraw\x00'
HEADER_SIZE = 128
RECORD_HEADER_SIZE = 24
DRAW_UNITS_PER_INCH = 46080
DRAW_UNITS_PER_MM = DRAW_UNITS_PER_INCH / 25.4

# Path element tags (low byte of uint32)
PATH_END = 0x00
PATH_MOVE = 0x02
PATH_CLOSE = 0x05
PATH_BEZIER = 0x06
PATH_LINE = 0x08

# Record types
TYPE_TEXT = 0x01
TYPE_PATH = 0x02
TYPE_GROUP = 0x06
TYPE_LAYER = 0x0A
TYPE_PALETTE_CONFIG = 0x22
TYPE_FILE_PATH = 0x23
TYPE_STROKE_COLOR = 0x24
TYPE_LINE_WIDTH = 0x25
TYPE_FILL_COLOR = 0x26
TYPE_MITRE_LIMIT = 0x27
TYPE_FLATNESS = 0x28
TYPE_WINDING_RULE = 0x29
TYPE_JOIN_STYLE = 0x2A
TYPE_CAP_STYLE = 0x2B
TYPE_UNKNOWN_2C = 0x2C
TYPE_DASH_PATTERN = 0x2D
TYPE_FONT_REF = 0x2F
TYPE_TEXT_STYLE = 0x30
TYPE_EXTENDED_PATH = 0x33
TYPE_DISTORTED_PATH = 0x34
TYPE_BLEND_PATH = 0x35
TYPE_UNKNOWN_37 = 0x37
TYPE_PERSPECTIVE_PATH = 0x38
TYPE_FILE_INFO = 0x39
TYPE_COMPOUND_PATH = 0x3A
TYPE_UNKNOWN_3B = 0x3B
TYPE_SETTINGS_2 = 0x3E
TYPE_SETTINGS_1 = 0x3F

# Fill types
FILL_FLAT = 0
FILL_LINEAR_GRADIENT = 1
FILL_RADIAL_GRADIENT = 2

PALETTE_INDEX_NONE = -1


class ArtWorksError(Exception):
    pass


class PaletteEntry:
    __slots__ = ('name', 'r', 'g', 'b')

    def __init__(self, name, r, g, b):
        self.name = name
        self.r = r
        self.g = g
        self.b = b

    def to_hex(self):
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"


class FillAttr:
    __slots__ = ('fill_type', 'palette_index', 'start_x', 'start_y',
                 'end_x', 'end_y', 'start_color_idx', 'end_color_idx')

    def __init__(self):
        self.fill_type = FILL_FLAT
        self.palette_index = 0
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0
        self.start_color_idx = 0
        self.end_color_idx = 0


class StrokeAttr:
    __slots__ = ('palette_index',)

    def __init__(self):
        self.palette_index = PALETTE_INDEX_NONE


class PathElement:
    __slots__ = ('tag', 'points')

    def __init__(self, tag, points=None):
        self.tag = tag
        self.points = points or []


class PathObject:
    __slots__ = ('bbox', 'elements', 'fill', 'stroke', 'line_width',
                 'join_style', 'cap_style', 'winding_rule', 'dash_pattern',
                 'mitre_limit', 'path_evenodd', 'is_closed')

    def __init__(self):
        self.bbox = (0, 0, 0, 0)
        self.elements = []
        self.fill = None
        self.stroke = None
        self.line_width = None
        self.join_style = None
        self.cap_style = None
        self.winding_rule = None
        self.dash_pattern = None
        self.mitre_limit = None
        self.path_evenodd = False


class TextChar:
    __slots__ = ('char_code', 'x', 'y', 'glyph_h')

    def __init__(self, char_code, x, y, glyph_h=0):
        self.char_code = char_code
        self.x = x
        self.y = y
        self.glyph_h = glyph_h


class TextObject:
    __slots__ = ('bbox', 'chars', 'fill', 'stroke', 'line_width',
                 'column_rect', 'font_name', 'font_size')

    def __init__(self):
        self.bbox = (0, 0, 0, 0)
        self.chars = []
        self.fill = None
        self.stroke = None
        self.line_width = None
        self.column_rect = None
        self.font_name = None
        self.font_size = None


class GroupObject:
    __slots__ = ('bbox', 'children', 'fill', 'stroke', 'line_width',
                 'join_style', 'cap_style', 'winding_rule')

    def __init__(self):
        self.bbox = (0, 0, 0, 0)
        self.children = []
        self.fill = None
        self.stroke = None
        self.line_width = None
        self.join_style = None
        self.cap_style = None
        self.winding_rule = None


class LayerObject:
    __slots__ = ('name', 'children', 'flags')

    def __init__(self):
        self.name = ''
        self.children = []
        self.flags = 0


class ArtWorksFile:

    def __init__(self, filepath):
        with open(filepath, 'rb') as f:
            self.data = f.read()
        self.filepath = filepath
        self.palette = []
        self.layers = []
        self.default_fill = FillAttr()
        self.default_stroke = StrokeAttr()
        self.default_line_width = 0
        self.default_join_style = 0
        self.default_cap_style = 0
        self.default_winding_rule = 0
        self.default_mitre_limit = 0x40000
        self.doc_width = 0
        self.doc_height = 0
        self.file_info = ''
        self.font_table = []

    def validate(self):
        if len(self.data) < HEADER_SIZE:
            raise ArtWorksError(f"File too small: {len(self.data)} bytes")
        if self.data[0:4] != MAGIC1:
            raise ArtWorksError(f"Bad magic1: {self.data[0:4]!r}")
        if self.data[8:16] != MAGIC2:
            raise ArtWorksError(f"Bad magic2: {self.data[8:16]!r}")
        hdr_size = struct.unpack_from('<I', self.data, 0x14)[0]
        if hdr_size != HEADER_SIZE:
            raise ArtWorksError(f"Unexpected header size: {hdr_size}")

    def _u32(self, offset):
        return struct.unpack_from('<I', self.data, offset)[0]

    def _i32(self, offset):
        return struct.unpack_from('<i', self.data, offset)[0]

    def parse_header(self):
        self.version = self._u32(4)
        self.doc_width = self._u32(0x18)
        self.doc_height = self._u32(0x1C)
        self.flags = self._u32(0x20)
        self.color_table_offset = self._u32(0x3C)

    def parse_palette(self):
        pos = self.color_table_offset
        if pos >= len(self.data):
            return
        num_entries = self._u32(pos) & 0xFF
        if num_entries == 0:
            num_entries = 17
        max_entries = min(num_entries, (len(self.data) - pos) // 48)
        for i in range(max_entries):
            epos = pos + i * 48
            color_word = self._u32(epos + 32)
            model = (color_word >> 24) & 0xFF
            if model == 0x20:
                name_bytes = self.data[epos + 8:epos + 32]
                name = name_bytes.split(b'\x00')[0].decode('ascii', errors='replace')
                r = color_word & 0xFF
                g = (color_word >> 8) & 0xFF
                b = (color_word >> 16) & 0xFF
                self.palette.append(PaletteEntry(name, r, g, b))
            else:
                self.palette.append(None)

    def get_color(self, palette_index):
        if palette_index == PALETTE_INDEX_NONE:
            return None
        unsigned = palette_index & 0xFFFFFFFF
        if unsigned & 0x80000000 and unsigned != 0xFFFFFFFF:
            r = unsigned & 0xFF
            g = (unsigned >> 8) & 0xFF
            b = (unsigned >> 16) & 0xFF
            return PaletteEntry('', r, g, b)
        if palette_index < 0 or palette_index >= len(self.palette):
            return None
        return self.palette[palette_index]

    def parse_fill_attr(self, data_bytes):
        fill = FillAttr()
        if len(data_bytes) < 28:
            return fill
        fill.fill_type = struct.unpack_from('<I', data_bytes, 16)[0]
        if fill.fill_type == FILL_FLAT:
            if len(data_bytes) >= 28:
                fill.palette_index = struct.unpack_from('<i', data_bytes, 24)[0]
        elif fill.fill_type in (FILL_LINEAR_GRADIENT, FILL_RADIAL_GRADIENT):
            if len(data_bytes) >= 48:
                fill.start_x = struct.unpack_from('<i', data_bytes, 24)[0]
                fill.start_y = struct.unpack_from('<i', data_bytes, 28)[0]
                fill.end_x = struct.unpack_from('<i', data_bytes, 32)[0]
                fill.end_y = struct.unpack_from('<i', data_bytes, 36)[0]
                fill.start_color_idx = struct.unpack_from('<I', data_bytes, 40)[0]
                fill.end_color_idx = struct.unpack_from('<I', data_bytes, 44)[0]
        return fill

    def parse_stroke_attr(self, data_bytes):
        stroke = StrokeAttr()
        if len(data_bytes) >= 20:
            stroke.palette_index = struct.unpack_from('<i', data_bytes, 16)[0]
        return stroke

    def parse_path_data(self, data, start, end):
        elements = []
        evenodd = False
        closed = False
        pos = start
        while pos < end:
            if pos + 4 > len(data):
                break
            tag_word = struct.unpack_from('<I', data, pos)[0]
            tag = tag_word & 0xFF

            if tag == PATH_END:
                pos += 4
                break
            elif tag == PATH_MOVE:
                if pos + 12 > end:
                    break
                if not elements and (tag_word & 0x80000000):
                    evenodd = True
                x = struct.unpack_from('<i', data, pos + 4)[0]
                y = struct.unpack_from('<i', data, pos + 8)[0]
                elements.append(PathElement(PATH_MOVE, [(x, y)]))
                pos += 12
            elif tag == PATH_LINE:
                if pos + 12 > end:
                    break
                x = struct.unpack_from('<i', data, pos + 4)[0]
                y = struct.unpack_from('<i', data, pos + 8)[0]
                elements.append(PathElement(PATH_LINE, [(x, y)]))
                pos += 12
            elif tag == PATH_BEZIER:
                if pos + 28 > end:
                    break
                cp1x = struct.unpack_from('<i', data, pos + 4)[0]
                cp1y = struct.unpack_from('<i', data, pos + 8)[0]
                cp2x = struct.unpack_from('<i', data, pos + 12)[0]
                cp2y = struct.unpack_from('<i', data, pos + 16)[0]
                ex = struct.unpack_from('<i', data, pos + 20)[0]
                ey = struct.unpack_from('<i', data, pos + 24)[0]
                elements.append(PathElement(PATH_BEZIER, [(cp1x, cp1y), (cp2x, cp2y), (ex, ey)]))
                pos += 28
            elif tag == PATH_CLOSE:
                closed = True
                elements.append(PathElement(PATH_CLOSE))
                pos += 4
            else:
                break
        return elements, evenodd, closed

    def parse_inline_attrs(self, rec_start, sub_hdr, rec_size):
        attrs = {}
        pos = rec_start + sub_hdr
        end = rec_start + rec_size
        while pos < end - 8:
            if pos + 8 > len(self.data):
                break
            a_back = self._i32(pos)
            a_size = self._u32(pos + 4)
            if a_size == 0:
                if pos + 0x18 < end:
                    peek_type = self._u32(pos + 0x10) & 0xFF
                    if peek_type in (TYPE_FILL_COLOR, TYPE_STROKE_COLOR,
                            TYPE_LINE_WIDTH, TYPE_MITRE_LIMIT, TYPE_FLATNESS,
                            TYPE_WINDING_RULE, TYPE_JOIN_STYLE, TYPE_CAP_STYLE,
                            TYPE_DASH_PATTERN):
                        a_size = end - pos
                    else:
                        break
                else:
                    break
            if a_size < RECORD_HEADER_SIZE or pos + a_size > end:
                break
            a_type = self._u32(pos + 0x10) & 0xFF
            a_data = self.data[pos + 0x18:pos + a_size]
            attrs[a_type] = a_data
            pos += a_size
        return attrs

    def parse_text_chars(self, rec_start, sub_hdr, rec_size):
        chars = []
        attrs = {}
        pos = rec_start + sub_hdr
        end = rec_start + rec_size
        while pos < end - 8:
            if pos + 8 > len(self.data):
                break
            a_back = self._i32(pos)
            a_size = self._u32(pos + 4)
            if a_size == 0:
                if pos + 0x18 < end:
                    peek_type = self._u32(pos + 0x10) & 0xFF
                    if peek_type in (TYPE_FILL_COLOR, TYPE_STROKE_COLOR,
                            TYPE_LINE_WIDTH, TYPE_DASH_PATTERN,
                            TYPE_FONT_REF, TYPE_TEXT_STYLE):
                        a_size = end - pos
                    else:
                        break
                else:
                    break
            if a_size < RECORD_HEADER_SIZE or pos + a_size > end:
                break
            a_type = self._u32(pos + 0x10) & 0xFF
            a_data = self.data[pos + 0x18:pos + a_size]

            if a_type == TYPE_DASH_PATTERN:
                if len(a_data) >= 28:
                    gh = struct.unpack_from('<i', a_data, 12)[0] - struct.unpack_from('<i', a_data, 4)[0]
                    char_code = struct.unpack_from('<I', a_data, 16)[0] & 0xFF
                    x = struct.unpack_from('<i', a_data, 20)[0]
                    y = struct.unpack_from('<i', a_data, 24)[0]
                    chars.append(TextChar(char_code, x, y, gh))
            else:
                attrs[a_type] = a_data
            pos += a_size
        return chars, attrs

    def parse_path_object(self, rec_start, rec_size, sub_hdr, path_data_offset=0x28):
        path = PathObject()
        path.bbox = (
            self._i32(rec_start + 0x18),
            self._i32(rec_start + 0x1C),
            self._i32(rec_start + 0x20),
            self._i32(rec_start + 0x24),
        )

        path_data_start = rec_start + path_data_offset
        path_data_end = rec_start + sub_hdr if sub_hdr > path_data_offset else rec_start + rec_size
        path.elements, path.path_evenodd, path.is_closed = self.parse_path_data(self.data, path_data_start, path_data_end)

        if sub_hdr > 0:
            attrs = self.parse_inline_attrs(rec_start, sub_hdr, rec_size)
            if TYPE_FILL_COLOR in attrs:
                path.fill = self.parse_fill_attr(attrs[TYPE_FILL_COLOR])
            if TYPE_STROKE_COLOR in attrs:
                path.stroke = self.parse_stroke_attr(attrs[TYPE_STROKE_COLOR])
            if TYPE_LINE_WIDTH in attrs:
                d = attrs[TYPE_LINE_WIDTH]
                if len(d) >= 20:
                    w = struct.unpack_from('<I', d, 16)[0]
                    path.line_width = w if w < 0x80000000 else 0
            if TYPE_JOIN_STYLE in attrs:
                d = attrs[TYPE_JOIN_STYLE]
                if len(d) >= 20:
                    path.join_style = struct.unpack_from('<I', d, 16)[0]
            if TYPE_CAP_STYLE in attrs:
                d = attrs[TYPE_CAP_STYLE]
                if len(d) >= 20:
                    path.cap_style = struct.unpack_from('<I', d, 16)[0]
            if TYPE_WINDING_RULE in attrs:
                d = attrs[TYPE_WINDING_RULE]
                if len(d) >= 20:
                    path.winding_rule = struct.unpack_from('<I', d, 16)[0]
            if TYPE_MITRE_LIMIT in attrs:
                d = attrs[TYPE_MITRE_LIMIT]
                if len(d) >= 20:
                    path.mitre_limit = struct.unpack_from('<I', d, 16)[0]
            if TYPE_DASH_PATTERN in attrs:
                d = attrs[TYPE_DASH_PATTERN]
                path.dash_pattern = d

        return path

    def parse_text_object(self, rec_start, rec_size, sub_hdr):
        text = TextObject()
        text.bbox = (
            self._i32(rec_start + 0x18),
            self._i32(rec_start + 0x1C),
            self._i32(rec_start + 0x20),
            self._i32(rec_start + 0x24),
        )

        if rec_start + 0x40 + 32 <= len(self.data):
            text.column_rect = (
                self._i32(rec_start + 0x40),
                self._i32(rec_start + 0x44),
                self._i32(rec_start + 0x48),
                self._i32(rec_start + 0x4C),
            )

        if sub_hdr > 0:
            chars, attrs = self.parse_text_chars(rec_start, sub_hdr, rec_size)
            text.chars = chars
            if TYPE_FILL_COLOR in attrs:
                text.fill = self.parse_fill_attr(attrs[TYPE_FILL_COLOR])
            if TYPE_STROKE_COLOR in attrs:
                text.stroke = self.parse_stroke_attr(attrs[TYPE_STROKE_COLOR])
            if TYPE_FONT_REF in attrs:
                d = attrs[TYPE_FONT_REF]
                name = d.split(b'\x00')[0].decode('ascii', errors='replace')
                if name:
                    text.font_name = name
            if TYPE_TEXT_STYLE in attrs:
                d = attrs[TYPE_TEXT_STYLE]
                if len(d) >= 20:
                    text.font_size = struct.unpack_from('<I', d, 16)[0]

        return text

    def parse_children(self, parent_start, sub_hdr, parent_size, group_obj=None):
        children = []
        pos = parent_start + sub_hdr
        end = parent_start + parent_size
        while pos < end - 8:
            if pos + 8 > len(self.data):
                break
            c_back = self._i32(pos)
            c_size = self._u32(pos + 4)
            if c_size == 0:
                if pos + 0x14 < len(self.data):
                    peek_sub = self._i32(pos + 8)
                    peek_type = self._u32(pos + 0x10) & 0xFF
                    if peek_sub > 0 and peek_type in (TYPE_GROUP, TYPE_LAYER,
                            TYPE_COMPOUND_PATH, TYPE_PATH, TYPE_TEXT,
                            TYPE_DISTORTED_PATH, TYPE_EXTENDED_PATH,
                            TYPE_PERSPECTIVE_PATH, TYPE_BLEND_PATH,
                            TYPE_UNKNOWN_37, TYPE_UNKNOWN_2C,
                            0x05, 0x42, 0x65, 0x67):
                        c_size = end - pos
                        self._handle_child(children, pos, c_size, peek_sub, peek_type)
                        pos += c_size
                        continue
                break
            if c_size < RECORD_HEADER_SIZE or pos + c_size > end:
                break
            c_sub = self._i32(pos + 8)
            c_type_raw = self._u32(pos + 0x10)
            c_type = c_type_raw & 0xFF

            if group_obj is not None and c_type in (TYPE_FILL_COLOR, TYPE_STROKE_COLOR,
                    TYPE_LINE_WIDTH, TYPE_JOIN_STYLE, TYPE_CAP_STYLE, TYPE_WINDING_RULE):
                attr_data = self.data[pos + 0x18:pos + c_size]
                if c_type == TYPE_FILL_COLOR:
                    group_obj.fill = self.parse_fill_attr(attr_data)
                elif c_type == TYPE_STROKE_COLOR:
                    group_obj.stroke = self.parse_stroke_attr(attr_data)
                elif c_type == TYPE_LINE_WIDTH and len(attr_data) >= 20:
                    w = struct.unpack_from('<I', attr_data, 16)[0]
                    group_obj.line_width = w if w < 0x80000000 else 0
                elif c_type == TYPE_JOIN_STYLE and len(attr_data) >= 20:
                    group_obj.join_style = struct.unpack_from('<I', attr_data, 16)[0]
                elif c_type == TYPE_CAP_STYLE and len(attr_data) >= 20:
                    group_obj.cap_style = struct.unpack_from('<I', attr_data, 16)[0]
                elif c_type == TYPE_WINDING_RULE and len(attr_data) >= 20:
                    group_obj.winding_rule = struct.unpack_from('<I', attr_data, 16)[0]
            else:
                self._handle_child(children, pos, c_size, c_sub, c_type)
            pos += c_size
        return children

    def _parse_group(self, pos, c_size, c_sub):
        group = GroupObject()
        if pos + 0x24 < len(self.data):
            group.bbox = (
                self._i32(pos + 0x18),
                self._i32(pos + 0x1C),
                self._i32(pos + 0x20),
                self._i32(pos + 0x24),
            )
        if c_sub > 0:
            group.children = self.parse_children(pos, c_sub, c_size, group_obj=group)
        return group

    def _handle_child(self, children, pos, c_size, c_sub, c_type):
        if c_type == TYPE_PATH:
            children.append(self.parse_path_object(pos, c_size, c_sub))
        elif c_type in (TYPE_DISTORTED_PATH, TYPE_EXTENDED_PATH):
            children.append(self.parse_path_object(pos, c_size, c_sub, path_data_offset=0x40))
        elif c_type == TYPE_BLEND_PATH:
            children.append(self.parse_path_object(pos, c_size, c_sub))
        elif c_type == TYPE_PERSPECTIVE_PATH:
            if c_sub > 0:
                children.append(self._parse_group(pos, c_size, c_sub))
            else:
                children.append(self.parse_path_object(pos, c_size, c_sub))
        elif c_type == 0x42:
            children.append(self._parse_group(pos, c_size, c_sub))
        elif c_type == TYPE_UNKNOWN_37:
            path = self.parse_path_object(pos, c_size, c_sub)
            if path.fill is None:
                path.fill = FillAttr()
                path.fill.palette_index = PALETTE_INDEX_NONE
            if path.stroke is None:
                path.stroke = StrokeAttr()
            children.append(path)
        elif c_type == TYPE_UNKNOWN_2C:
            children.append(self.parse_path_object(pos, c_size, c_sub, path_data_offset=0x2C))
        elif c_type in (TYPE_GROUP, TYPE_COMPOUND_PATH, 0x65, 0x67):
            children.append(self._parse_group(pos, c_size, c_sub))
        elif c_type == TYPE_TEXT:
            children.append(self.parse_text_object(pos, c_size, c_sub))
        elif c_type == TYPE_LAYER:
            layer = LayerObject()
            if pos + 0x4C <= len(self.data):
                name_bytes = self.data[pos + 0x2C:pos + 0x4C]
                layer.name = name_bytes.split(b'\x00')[0].decode('ascii', errors='replace')
            if c_sub > 0:
                layer.children = self.parse_children(pos, c_sub, c_size)
            children.append(layer)

    def parse_font_table(self, data_bytes):
        fonts = []
        pos = 0
        while pos < len(data_bytes):
            name = data_bytes[pos:].split(b'\x00')[0]
            if not name:
                break
            fonts.append(name.decode('ascii', errors='replace'))
            pos += len(name) + 1
        return fonts

    def parse_records(self):
        pos = HEADER_SIZE
        while pos < len(self.data) - 8:
            back = self._i32(pos)
            size = self._u32(pos + 4)
            if size == 0:
                break
            if size < RECORD_HEADER_SIZE or pos + size > len(self.data):
                break
            sub = self._i32(pos + 8)
            typ = self._u32(pos + 0x10)
            attr_data = self.data[pos + 0x18:pos + size]

            if typ == TYPE_FILL_COLOR:
                self.default_fill = self.parse_fill_attr(attr_data)
            elif typ == TYPE_STROKE_COLOR:
                self.default_stroke = self.parse_stroke_attr(attr_data)
            elif typ == TYPE_LINE_WIDTH:
                if len(attr_data) >= 20:
                    w = struct.unpack_from('<I', attr_data, 16)[0]
                    self.default_line_width = w if w < 0x80000000 else 0
            elif typ == TYPE_JOIN_STYLE:
                if len(attr_data) >= 20:
                    self.default_join_style = struct.unpack_from('<I', attr_data, 16)[0]
            elif typ == TYPE_CAP_STYLE:
                if len(attr_data) >= 20:
                    self.default_cap_style = struct.unpack_from('<I', attr_data, 16)[0]
            elif typ == TYPE_WINDING_RULE:
                if len(attr_data) >= 20:
                    self.default_winding_rule = struct.unpack_from('<I', attr_data, 16)[0]
            elif typ == TYPE_MITRE_LIMIT:
                if len(attr_data) >= 20:
                    self.default_mitre_limit = struct.unpack_from('<I', attr_data, 16)[0]
            elif typ == TYPE_FILE_INFO:
                self.file_info = attr_data.decode('ascii', errors='replace').strip('\x00').strip()
            elif typ == TYPE_FONT_REF:
                self.font_table = self.parse_font_table(attr_data)
            elif typ == TYPE_LAYER:
                layer = LayerObject()
                if pos + 0x4C <= len(self.data):
                    name_bytes = self.data[pos + 0x2C:pos + 0x4C]
                    layer.name = name_bytes.split(b'\x00')[0].decode('ascii', errors='replace')
                if pos + 0x28 < len(self.data):
                    layer.flags = self._u32(pos + 0x28)
                if sub > 0:
                    layer.children = self.parse_children(pos, sub, size)
                self.layers.append(layer)

            pos += size

    def parse(self):
        self.validate()
        self.parse_header()
        self.parse_palette()
        self.parse_records()


class SVGRenderer:

    def __init__(self, aw_file):
        self.aw = aw_file
        self.gradient_id = 0
        self.bounds_min_x = 0
        self.bounds_max_y = 0

    def du_to_mm(self, du):
        return du / DRAW_UNITS_PER_MM

    def tx(self, draw_x):
        return self.du_to_mm(draw_x - self.bounds_min_x)

    def ty(self, draw_y):
        return self.du_to_mm(self.bounds_max_y - draw_y)

    def compute_bounds(self):
        min_x = float('inf')
        min_y = float('inf')
        max_x = float('-inf')
        max_y = float('-inf')

        def update_from_objects(objects):
            nonlocal min_x, min_y, max_x, max_y
            for obj in objects:
                if isinstance(obj, PathObject):
                    bx0, by0, bx1, by1 = obj.bbox
                    lw = obj.line_width if obj.line_width is not None else self.aw.default_line_width
                    half_lw = lw / 2
                    min_x = min(min_x, bx0 - half_lw)
                    min_y = min(min_y, by0 - half_lw)
                    max_x = max(max_x, bx1 + half_lw)
                    max_y = max(max_y, by1 + half_lw)
                elif isinstance(obj, TextObject):
                    bx0, by0, bx1, by1 = obj.bbox
                    min_x = min(min_x, bx0)
                    min_y = min(min_y, by0)
                    max_x = max(max_x, bx1)
                    max_y = max(max_y, by1)
                elif isinstance(obj, GroupObject):
                    update_from_objects(obj.children)
                elif isinstance(obj, LayerObject):
                    update_from_objects(obj.children)

        for layer in self.aw.layers:
            update_from_objects(layer.children)

        if min_x == float('inf'):
            return 0, 0, self.aw.doc_width, self.aw.doc_height

        doc_limit = max(self.aw.doc_width, self.aw.doc_height) * 2
        min_x = max(min_x, -doc_limit)
        min_y = max(min_y, -doc_limit)
        max_x = min(max_x, doc_limit)
        max_y = min(max_y, doc_limit)

        pad = (max_x - min_x) * 0.01
        return (min_x - pad, min_y - pad, max_x + pad, max_y + pad)

    def _resolve_fill(self, obj, inherited):
        if obj.fill is not None:
            return obj.fill
        if inherited and inherited.get('fill') is not None:
            return inherited['fill']
        return self.aw.default_fill

    def _resolve_stroke(self, obj, inherited):
        if obj.stroke is not None:
            return obj.stroke
        if inherited and inherited.get('stroke') is not None:
            return inherited['stroke']
        return self.aw.default_stroke

    def _resolve_line_width(self, obj, inherited):
        if obj.line_width is not None:
            return obj.line_width
        if inherited and inherited.get('line_width') is not None:
            return inherited['line_width']
        return self.aw.default_line_width

    def _resolve_join(self, obj, inherited):
        if obj.join_style is not None:
            return obj.join_style
        if inherited and inherited.get('join_style') is not None:
            return inherited['join_style']
        return self.aw.default_join_style

    def _resolve_cap(self, obj, inherited):
        if obj.cap_style is not None:
            return obj.cap_style
        if inherited and inherited.get('cap_style') is not None:
            return inherited['cap_style']
        return self.aw.default_cap_style

    def _resolve_winding(self, obj, inherited):
        if obj.winding_rule is not None:
            return obj.winding_rule
        if inherited and inherited.get('winding_rule') is not None:
            return inherited['winding_rule']
        return self.aw.default_winding_rule

    def _build_inherited(self, group_obj, parent_inherited):
        ctx = dict(parent_inherited) if parent_inherited else {}
        if group_obj.fill is not None:
            ctx['fill'] = group_obj.fill
        if group_obj.stroke is not None:
            ctx['stroke'] = group_obj.stroke
        if group_obj.line_width is not None:
            ctx['line_width'] = group_obj.line_width
        if group_obj.join_style is not None:
            ctx['join_style'] = group_obj.join_style
        if group_obj.cap_style is not None:
            ctx['cap_style'] = group_obj.cap_style
        if group_obj.winding_rule is not None:
            ctx['winding_rule'] = group_obj.winding_rule
        return ctx

    def _fill_to_svg(self, fill, defs_elem):
        if fill.fill_type == FILL_FLAT:
            if fill.palette_index == PALETTE_INDEX_NONE:
                return "none"
            color = self.aw.get_color(fill.palette_index)
            if color is None:
                return "none"
            return color.to_hex()

        elif fill.fill_type in (FILL_LINEAR_GRADIENT, FILL_RADIAL_GRADIENT):
            start_color = self.aw.get_color(fill.start_color_idx)
            end_color = self.aw.get_color(fill.end_color_idx)
            if start_color is None or end_color is None:
                return "none"

            if fill.start_x == fill.end_x and fill.start_y == fill.end_y:
                return start_color.to_hex()

            self.gradient_id += 1
            grad_id = f"grad{self.gradient_id}"

            sx = self.tx(fill.start_x)
            sy = self.ty(fill.start_y)
            ex = self.tx(fill.end_x)
            ey = self.ty(fill.end_y)

            if fill.fill_type == FILL_LINEAR_GRADIENT:
                grad = SubElement(defs_elem, 'linearGradient',
                                  id=grad_id,
                                  x1=f"{sx:.4f}", y1=f"{sy:.4f}",
                                  x2=f"{ex:.4f}", y2=f"{ey:.4f}",
                                  gradientUnits="userSpaceOnUse")
            else:
                cx = (sx + ex) / 2
                cy = (sy + ey) / 2
                r_val = math.sqrt((ex - sx) ** 2 + (ey - sy) ** 2) / 2
                if r_val < 0.001:
                    r_val = 0.001
                grad = SubElement(defs_elem, 'radialGradient',
                                  id=grad_id,
                                  cx=f"{cx:.4f}", cy=f"{cy:.4f}",
                                  r=f"{r_val:.4f}",
                                  gradientUnits="userSpaceOnUse")

            stop1 = SubElement(grad, 'stop', offset="0%")
            stop1.set('stop-color', start_color.to_hex())
            stop2 = SubElement(grad, 'stop', offset="100%")
            stop2.set('stop-color', end_color.to_hex())

            return f"url(#{grad_id})"

        return "none"

    def _stroke_to_svg(self, stroke):
        if stroke.palette_index == PALETTE_INDEX_NONE:
            return "none"
        color = self.aw.get_color(stroke.palette_index)
        if color is None:
            return "none"
        return color.to_hex()

    def path_to_d(self, elements):
        parts = []
        for elem in elements:
            if elem.tag == PATH_MOVE:
                x, y = elem.points[0]
                parts.append(f"M{self.tx(x):.4f},{self.ty(y):.4f}")
            elif elem.tag == PATH_LINE:
                x, y = elem.points[0]
                parts.append(f"L{self.tx(x):.4f},{self.ty(y):.4f}")
            elif elem.tag == PATH_BEZIER:
                (cp1x, cp1y), (cp2x, cp2y), (ex, ey) = elem.points
                parts.append(
                    f"C{self.tx(cp1x):.4f},{self.ty(cp1y):.4f} "
                    f"{self.tx(cp2x):.4f},{self.ty(cp2y):.4f} "
                    f"{self.tx(ex):.4f},{self.ty(ey):.4f}"
                )
            elif elem.tag == PATH_CLOSE:
                parts.append("Z")
        return " ".join(parts)

    def render_path(self, path_obj, parent_elem, defs_elem, inherited=None):
        if not path_obj.elements:
            return

        d = self.path_to_d(path_obj.elements)
        if not d:
            return

        path_elem = SubElement(parent_elem, 'path', d=d)

        fill = self._resolve_fill(path_obj, inherited)
        if (not path_obj.is_closed and path_obj.fill is None
                and not (inherited and inherited.get('fill') is not None)):
            fill_val = "none"
        else:
            fill_val = self._fill_to_svg(fill, defs_elem)
        path_elem.set('fill', fill_val)

        stroke = self._resolve_stroke(path_obj, inherited)
        stroke_val = self._stroke_to_svg(stroke)
        lw = self._resolve_line_width(path_obj, inherited)

        if stroke_val != "none":
            path_elem.set('stroke', stroke_val)
            if lw > 0:
                path_elem.set('stroke-width', f"{self.du_to_mm(lw):.4f}")
            else:
                path_elem.set('stroke-width', "0.1")
                path_elem.set('vector-effect', 'non-scaling-stroke')

            join = self._resolve_join(path_obj, inherited)
            if join == 1:
                path_elem.set('stroke-linejoin', 'round')
            elif join == 2:
                path_elem.set('stroke-linejoin', 'bevel')

            cap = self._resolve_cap(path_obj, inherited)
            if cap == 1:
                path_elem.set('stroke-linecap', 'round')
            elif cap == 2:
                path_elem.set('stroke-linecap', 'square')
        else:
            path_elem.set('stroke', 'none')

        if path_obj.path_evenodd:
            path_elem.set('fill-rule', 'evenodd')
        else:
            wr = self._resolve_winding(path_obj, inherited)
            if wr != 0:
                path_elem.set('fill-rule', 'evenodd')

    def render_text(self, text_obj, parent_elem, defs_elem, inherited=None):
        if not text_obj.chars:
            return

        fill = self._resolve_fill(text_obj, inherited)
        fill_val = self._fill_to_svg(fill, defs_elem)

        stroke = self._resolve_stroke(text_obj, inherited)
        stroke_val = self._stroke_to_svg(stroke)

        max_gh = max((c.glyph_h for c in text_obj.chars if c.char_code >= 32), default=0)
        if max_gh > 0:
            font_size_svg = self.du_to_mm(max_gh) * 1.25
        else:
            font_size_du = text_obj.font_size if text_obj.font_size else 0x200
            font_size_svg = self.du_to_mm(font_size_du)
            if font_size_svg < 0.5:
                font_size_svg = self.du_to_mm(text_obj.bbox[3] - text_obj.bbox[1])
                if font_size_svg < 0.5:
                    font_size_svg = 3.0

        font_family = "sans-serif"
        if text_obj.font_name:
            fn = text_obj.font_name.replace('.', ' ')
            font_family = f"'{fn}', sans-serif"

        printable = [c for c in text_obj.chars if c.char_code >= 32]
        if not printable:
            return

        text_elem = SubElement(parent_elem, 'text')
        text_elem.set('fill', fill_val)
        if stroke_val != "none":
            text_elem.set('stroke', stroke_val)
        text_elem.set('font-size', f"{font_size_svg:.2f}")
        text_elem.set('font-family', font_family)

        for tc in printable:
            tspan = SubElement(text_elem, 'tspan',
                               x=f"{self.tx(tc.x):.4f}",
                               y=f"{self.ty(tc.y):.4f}")
            tspan.text = chr(tc.char_code)

    def render_objects(self, objects, parent_elem, defs_elem, inherited=None):
        for obj in objects:
            if isinstance(obj, PathObject):
                self.render_path(obj, parent_elem, defs_elem, inherited)
            elif isinstance(obj, TextObject):
                self.render_text(obj, parent_elem, defs_elem, inherited)
            elif isinstance(obj, GroupObject):
                g = SubElement(parent_elem, 'g')
                child_ctx = self._build_inherited(obj, inherited)
                self.render_objects(obj.children, g, defs_elem, child_ctx)
            elif isinstance(obj, LayerObject):
                g = SubElement(parent_elem, 'g')
                if obj.name:
                    g.set('id', f"layer-{obj.name.replace(' ', '_')}")
                self.render_objects(obj.children, g, defs_elem, inherited)

    def render(self):
        bmin_x, bmin_y, bmax_x, bmax_y = self.compute_bounds()
        self.bounds_min_x = bmin_x
        self.bounds_max_y = bmax_y

        w_mm = self.du_to_mm(bmax_x - bmin_x)
        h_mm = self.du_to_mm(bmax_y - bmin_y)

        svg = Element('svg')
        svg.set('xmlns', 'http://www.w3.org/2000/svg')
        svg.set('viewBox', f"0 0 {w_mm:.4f} {h_mm:.4f}")
        svg.set('width', f"{w_mm:.2f}mm")
        svg.set('height', f"{h_mm:.2f}mm")

        defs = SubElement(svg, 'defs')

        for layer in self.aw.layers:
            if layer.children:
                g = SubElement(svg, 'g')
                if layer.name:
                    g.set('id', f"layer-{layer.name.replace(' ', '_')}")
                self.render_objects(layer.children, g, defs)

        if len(defs) == 0:
            svg.remove(defs)

        return svg


def svg_to_string(svg_elem):
    ET.indent(svg_elem, space='  ')
    xml_str = ET.tostring(svg_elem, encoding='unicode', xml_declaration=False)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str


def convert_file(input_path, output_path):
    aw = ArtWorksFile(input_path)
    aw.parse()

    renderer = SVGRenderer(aw)
    svg = renderer.render()
    svg_str = svg_to_string(svg)

    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg_str)

    return output_path


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputFile>", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    if not os.path.isfile(input_path):
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    with open(input_path, 'rb') as f:
        magic = f.read(4)
    if magic != MAGIC1:
        print(f"Error: not an ArtWorks file (bad magic: {magic!r})", file=sys.stderr)
        sys.exit(1)

    try:
        convert_file(input_path, output_path)
        print(f"Converted: {output_path}")
    except ArtWorksError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

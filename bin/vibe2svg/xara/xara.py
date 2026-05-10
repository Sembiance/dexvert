#!/usr/bin/env python3
# Vibe coded by Codex
"""Convert a Xara XAR/WEB graphic into an SVG file.

This reader validates and accounts for the complete XAR byte stream, including
raw-deflate compression sections. The SVG renderer is intentionally conservative:
it renders the documented core drawing records and preserves unsupported records
as parsed-but-not-rendered diagnostics in the SVG metadata.
"""

from __future__ import annotations

import base64
import colorsys
import copy
import dataclasses
import html
import math
import os
from pathlib import Path
import struct
import sys
import zlib
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple


MAGIC = b"XARA\xa3\xa3\r\n"


TAG_NAMES = {
    0: "TAG_UP",
    1: "TAG_DOWN",
    2: "TAG_FILEHEADER",
    3: "TAG_ENDOFFILE",
    10: "TAG_ATOMICTAGS",
    12: "TAG_TAGDESCRIPTION",
    30: "TAG_STARTCOMPRESSION",
    31: "TAG_ENDCOMPRESSION",
    40: "TAG_DOCUMENT",
    41: "TAG_CHAPTER",
    42: "TAG_SPREAD",
    43: "TAG_LAYER",
    45: "TAG_SPREADINFORMATION",
    46: "TAG_GRIDRULERSETTINGS",
    47: "TAG_GRIDRULERORIGIN",
    48: "TAG_LAYERDETAILS",
    49: "TAG_GUIDELAYERDETAILS",
    50: "TAG_DEFINERGBCOLOUR",
    51: "TAG_DEFINECOMPLEXCOLOUR",
    53: "TAG_SPREADSCALING_INACTIVE",
    61: "TAG_PREVIEWBITMAP_GIF",
    67: "TAG_DEFINEBITMAP_JPEG",
    68: "TAG_DEFINEBITMAP_PNG",
    71: "TAG_DEFINEBITMAP_JPEG8BPP",
    80: "TAG_VIEWPORT",
    81: "TAG_VIEWQUALITY",
    82: "TAG_DOCUMENTVIEW",
    87: "TAG_DEFINE_DEFAULTUNITS",
    90: "TAG_DOCUMENTCOMMENT",
    91: "TAG_DOCUMENTDATES",
    92: "TAG_DOCUMENTUNDOSIZE",
    93: "TAG_DOCUMENTFLAGS",
    100: "TAG_PATH",
    101: "TAG_PATH_FILLED",
    102: "TAG_PATH_STROKED",
    103: "TAG_PATH_FILLED_STROKED",
    104: "TAG_GROUP",
    105: "TAG_BLEND",
    106: "TAG_BLENDER",
    107: "TAG_MOULD_ENVELOPE",
    108: "TAG_MOULD_PERSPECTIVE",
    109: "TAG_MOULD_GROUP",
    110: "TAG_MOULD_PATH",
    111: "TAG_PATH_FLAGS",
    112: "TAG_GUIDELINE",
    113: "TAG_PATH_RELATIVE",
    114: "TAG_PATH_RELATIVE_FILLED",
    115: "TAG_PATH_RELATIVE_STROKED",
    116: "TAG_PATH_RELATIVE_FILLED_STROKED",
    118: "TAG_PATHREF_TRANSFORM",
    150: "TAG_FLATFILL",
    151: "TAG_LINECOLOUR",
    152: "TAG_LINEWIDTH",
    153: "TAG_LINEARFILL",
    154: "TAG_CIRCULARFILL",
    155: "TAG_ELLIPTICALFILL",
    156: "TAG_CONICALFILL",
    157: "TAG_BITMAPFILL",
    158: "TAG_CONTONEBITMAPFILL",
    159: "TAG_FRACTALFILL",
    160: "TAG_FILLEFFECT_FADE",
    161: "TAG_FILLEFFECT_RAINBOW",
    162: "TAG_FILLEFFECT_ALTRAINBOW",
    163: "TAG_FILL_REPEATING",
    164: "TAG_FILL_NONREPEATING",
    165: "TAG_FILL_REPEATINGINVERTED",
    166: "TAG_FLATTRANSPARENTFILL",
    167: "TAG_LINEARTRANSPARENTFILL",
    168: "TAG_CIRCULARTRANSPARENTFILL",
    169: "TAG_ELLIPTICALTRANSPARENTFILL",
    170: "TAG_CONICALTRANSPARENTFILL",
    171: "TAG_BITMAPTRANSPARENTFILL",
    172: "TAG_FRACTALTRANSPARENTFILL",
    173: "TAG_LINETRANSPARENCY",
    174: "TAG_STARTCAP",
    175: "TAG_ENDCAP",
    176: "TAG_JOINSTYLE",
    177: "TAG_MITRELIMIT",
    178: "TAG_WINDINGRULE",
    179: "TAG_QUALITY",
    180: "TAG_TRANSPARENTFILL_REPEATING",
    181: "TAG_TRANSPARENTFILL_NONREPEATING",
    182: "TAG_TRANSPARENTFILL_REPEATINGINVERTED",
    183: "TAG_DASHSTYLE",
    185: "TAG_ARROWHEAD",
    186: "TAG_ARROWTAIL",
    189: "TAG_USERVALUE",
    190: "TAG_FLATFILL_NONE",
    191: "TAG_FLATFILL_BLACK",
    192: "TAG_FLATFILL_WHITE",
    193: "TAG_LINECOLOUR_NONE",
    194: "TAG_LINECOLOUR_BLACK",
    195: "TAG_LINECOLOUR_WHITE",
    198: "TAG_NODE_BITMAP",
    199: "TAG_NODE_CONTONEDBITMAP",
    200: "TAG_SQUAREFILL",
    201: "TAG_SQUARETRANSPARENTFILL",
    204: "TAG_FOURCOLFILL",
    206: "TAG_FILL_REPEATING_EXTRA",
    4050: "TAG_SHADOWCONTROLLER",
    4051: "TAG_SHADOW",
    4060: "TAG_BLENDER_CURVEPROP",
    4061: "TAG_BLEND_PATH",
    4062: "TAG_BLENDER_CURVEANGLES",
    4073: "TAG_BLENDERADDITIONAL",
    4074: "TAG_NODEBLENDPATH_FILLED",
    1000: "TAG_ELLIPSE_SIMPLE",
    1001: "TAG_ELLIPSE_COMPLEX",
    1100: "TAG_RECTANGLE_SIMPLE",
    1104: "TAG_RECTANGLE_SIMPLE_ROUNDED",
    1108: "TAG_RECTANGLE_COMPLEX",
    1110: "TAG_RECTANGLE_COMPLEX_STELLATED",
    1112: "TAG_RECTANGLE_COMPLEX_ROUNDED",
    1114: "TAG_RECTANGLE_COMPLEX_ROUNDED_STELLATED",
    1200: "TAG_POLYGON_COMPLEX",
    1212: "TAG_POLYGON_COMPLEX_STELLATED",
    1216: "TAG_POLYGON_COMPLEX_ROUNDED_STELLATED",
    1901: "TAG_REGULAR_SHAPE_PHASE_2",
    2000: "TAG_FONT_DEF_TRUETYPE",
    2100: "TAG_TEXT_STORY_SIMPLE",
    2101: "TAG_TEXT_STORY_COMPLEX",
    2110: "TAG_TEXT_STORY_SIMPLE_START_LEFT",
    2114: "TAG_TEXT_STORY_COMPLEX_START_LEFT",
    2117: "TAG_TEXT_STORY_COMPLEX_END_RIGHT",
    2150: "TAG_TEXT_STORY_WORD_WRAP_INFO",
    2151: "TAG_TEXT_STORY_INDENT_INFO",
    2200: "TAG_TEXT_LINE",
    2201: "TAG_TEXT_STRING",
    2202: "TAG_TEXT_CHAR",
    2203: "TAG_TEXT_EOL",
    2204: "TAG_TEXT_KERN",
    2206: "TAG_TEXT_LINE_INFO",
    2900: "TAG_TEXT_LINESPACE_RATIO",
    2901: "TAG_TEXT_LINESPACE_ABSOLUTE",
    2902: "TAG_TEXT_JUSTIFICATION_LEFT",
    2903: "TAG_TEXT_JUSTIFICATION_CENTRE",
    2904: "TAG_TEXT_JUSTIFICATION_RIGHT",
    2905: "TAG_TEXT_JUSTIFICATION_FULL",
    2906: "TAG_TEXT_FONT_SIZE",
    2907: "TAG_TEXT_TYPEFACE",
    2908: "TAG_TEXT_BOLD_ON",
    2909: "TAG_TEXT_BOLD_OFF",
    2910: "TAG_TEXT_ITALIC_ON",
    2918: "TAG_TEXT_TRACKING",
    2919: "TAG_TEXT_ASPECT_RATIO",
    2920: "TAG_TEXT_BASELINE",
    3506: "TAG_WEBADDRESS",
    3507: "TAG_WEBADDRESS_BOUNDINGBOX",
    4086: "TAG_FEATHER",
    4115: "TAG_BITMAP_PROPERTIES",
    4119: "TAG_CURRENTATTRIBUTES",
    4120: "TAG_CURRENTATTRIBUTEBOUNDS",
    4121: "TAG_LINEARFILL3POINT",
    4123: "TAG_LINEARTRANSPARENTFILL3POINT",
    4128: "TAG_COMPOUNDRENDER",
    4129: "TAG_OBJECTBOUNDS",
    4131: "TAG_SPREAD_PHASE2",
    4132: "TAG_CURRENTATTRIBUTES_PHASE2",
    4134: "TAG_SPREAD_FLASHPROPS",
    4136: "TAG_DOCUMENTINFORMATION",
    4200: "TAG_TEXT_TAB",
    4201: "TAG_TEXT_LEFT_INDENT",
    4202: "TAG_TEXT_FIRST_INDENT",
    4203: "TAG_TEXT_RIGHT_INDENT",
    4204: "TAG_TEXT_RULER",
    4205: "TAG_TEXT_STORY_HEIGHT_INFO",
    4206: "TAG_TEXT_STORY_LINK_INFO",
    4207: "TAG_TEXT_STORY_TRANSLATION_INFO",
    4208: "TAG_TEXT_SPACE_BEFORE",
    4209: "TAG_TEXT_SPACE_AFTER",
}


class XaraError(Exception):
    pass


@dataclasses.dataclass
class Record:
    seq: int
    tag: int
    size: int
    payload: bytes
    offset: int
    compressed: bool = False

    @property
    def name(self) -> str:
        return TAG_NAMES.get(self.tag, f"TAG_{self.tag}")


@dataclasses.dataclass
class Node:
    record: Record
    children: List["Node"] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class Bitmap:
    seq: int
    mime: str
    name: str
    data: bytes


@dataclasses.dataclass
class Fill:
    kind: str
    color: Optional[str] = None
    opacity: float = 1.0
    points: Tuple[Tuple[float, float], ...] = ()
    colors: Tuple[Optional[str], ...] = ()
    bitmap_ref: Optional[int] = None


@dataclasses.dataclass
class Transparency:
    kind: str = "none"
    points: Tuple[Tuple[float, float], ...] = ()
    values: Tuple[int, ...] = ()
    transp_type: int = 0
    bitmap_ref: Optional[int] = None


@dataclasses.dataclass
class Context:
    fill: Fill = dataclasses.field(default_factory=lambda: Fill("none"))
    stroke: Optional[str] = "#000000"
    line_width: int = 501
    fill_opacity: float = 1.0
    fill_transparency: Transparency = dataclasses.field(default_factory=Transparency)
    fill_effect: str = "fade"
    feather_width: int = 0
    stroke_opacity: float = 1.0
    line_cap: str = "butt"
    line_join: str = "bevel"
    dasharray: Tuple[int, ...] = ()
    dashoffset: int = 0
    fill_rule: str = "evenodd"
    font_size: int = 12000
    font_family: str = "Times New Roman"
    font_aspect: float = 1.0
    font_baseline: int = 0
    tracking: int = 0
    text_left_indent: int = 0
    text_first_indent: int = 0
    text_right_indent: int = 0
    text_anchor: str = "start"
    bold: bool = False
    italic: bool = False


@dataclasses.dataclass
class TextRun:
    text: str
    ctx: Context


@dataclasses.dataclass
class TextLine:
    runs: List[TextRun]
    offset: int = 0
    width: int = 0
    height: int = 0


@dataclasses.dataclass
class PageBlock:
    name: str
    layer_seqs: Optional[set[int]]
    phase_seq: Optional[int]


def u32(data: bytes, off: int) -> int:
    return struct.unpack_from("<I", data, off)[0]


def i32(data: bytes, off: int) -> int:
    return struct.unpack_from("<i", data, off)[0]


def u16(data: bytes, off: int) -> int:
    return struct.unpack_from("<H", data, off)[0]


def fixed16(data: bytes, off: int) -> float:
    return i32(data, off) / 65536.0


def f64(data: bytes, off: int) -> float:
    return struct.unpack_from("<d", data, off)[0]


def coord(data: bytes, off: int) -> Tuple[int, int]:
    return i32(data, off), i32(data, off + 4)


def color_ref(data: bytes, off: int) -> int:
    return i32(data, off)


def fmt_num(value: float) -> str:
    if abs(value - round(value)) < 0.0001:
        return str(int(round(value)))
    return f"{value:.4f}".rstrip("0").rstrip(".")


def xml_attr(value: object) -> str:
    return html.escape(str(value), quote=True)


def svg_y(value: float) -> float:
    return -value


def signed_interleaved_coord(raw: bytes) -> Tuple[int, int]:
    if len(raw) != 8:
        raise XaraError("bad interleaved coordinate length")
    xb = bytes((raw[0], raw[2], raw[4], raw[6]))
    yb = bytes((raw[1], raw[3], raw[5], raw[7]))
    return int.from_bytes(xb, "big", signed=True), int.from_bytes(yb, "big", signed=True)


def parse_ascii_cstrs(payload: bytes, count: int) -> List[str]:
    out = []
    pos = 0
    for _ in range(count):
        end = payload.find(b"\x00", pos)
        if end < 0:
            raise XaraError("unterminated ASCII string")
        out.append(payload[pos:end].decode("latin1", errors="replace"))
        pos = end + 1
    return out


def split_utf16_cstr(payload: bytes) -> Tuple[str, int]:
    for pos in range(0, len(payload) - 1, 2):
        if payload[pos : pos + 2] == b"\x00\x00":
            text = payload[:pos].decode("utf-16le", errors="replace")
            return text, pos + 2
    return "", 0


def font_name_from_payload(payload: bytes) -> str:
    text = payload.decode("utf-16le", errors="ignore")
    for part in text.split("\x00"):
        part = part.strip()
        if part and any(ch.isalpha() for ch in part):
            return part
    return ""


def utf16z_from_payload(payload: bytes) -> str:
    text = payload.decode("utf-16le", errors="replace")
    return text.split("\x00", 1)[0].strip()


def safe_filename(name: str) -> str:
    cleaned = []
    for ch in name.strip():
        if ch.isalnum() or ch in ("-", "_", "."):
            cleaned.append(ch)
        elif ch.isspace():
            cleaned.append("_")
        else:
            cleaned.append("_")
    out = "".join(cleaned).strip("._")
    return out or "page"


def find_image_start(payload: bytes, signatures: Sequence[bytes]) -> int:
    name, pos = split_utf16_cstr(payload)
    if pos:
        for sig in signatures:
            if payload[pos : pos + len(sig)] == sig:
                return pos
    for sig in signatures:
        idx = payload.find(sig)
        if idx >= 0:
            return idx
    return -1


def png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", zlib.crc32(chunk_type + data) & 0xFFFFFFFF)


def paeth_predictor(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def unfilter_png_scanline(filter_type: int, row: bytearray, prev: bytes, bpp: int) -> bytes:
    out = bytearray(row)
    for idx, value in enumerate(row):
        left = out[idx - bpp] if idx >= bpp else 0
        up = prev[idx] if prev else 0
        upper_left = prev[idx - bpp] if prev and idx >= bpp else 0
        if filter_type == 0:
            out[idx] = value
        elif filter_type == 1:
            out[idx] = (value + left) & 0xFF
        elif filter_type == 2:
            out[idx] = (value + up) & 0xFF
        elif filter_type == 3:
            out[idx] = (value + ((left + up) // 2)) & 0xFF
        elif filter_type == 4:
            out[idx] = (value + paeth_predictor(left, up, upper_left)) & 0xFF
        else:
            raise XaraError("unsupported PNG filter type")
    return bytes(out)


def invert_xara_png_alpha(data: bytes) -> bytes:
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        return data
    pos = 8
    chunks: List[Tuple[bytes, bytes]] = []
    idat = bytearray()
    inserted_idat_marker = False
    width = height = bit_depth = color_type = None
    while pos + 8 <= len(data):
        length = struct.unpack_from(">I", data, pos)[0]
        chunk_type = data[pos + 4 : pos + 8]
        chunk_data = data[pos + 8 : pos + 8 + length]
        if pos + 12 + length > len(data):
            return data
        pos += 12 + length
        if chunk_type == b"IHDR":
            if len(chunk_data) != 13:
                return data
            width, height, bit_depth, color_type = struct.unpack_from(">IIBB", chunk_data, 0)
            chunks.append((chunk_type, chunk_data))
        elif chunk_type == b"IDAT":
            idat.extend(chunk_data)
            if not inserted_idat_marker:
                chunks.append((chunk_type, b""))
                inserted_idat_marker = True
        elif chunk_type == b"IEND":
            break
        else:
            chunks.append((chunk_type, chunk_data))
    if width is None or height is None or bit_depth != 8 or color_type != 6 or not idat:
        return data

    row_len = width * 4
    try:
        raw = zlib.decompress(bytes(idat))
    except zlib.error:
        return data
    if len(raw) < (row_len + 1) * height:
        return data

    out = bytearray()
    prev = b""
    offset = 0
    try:
        for _row_idx in range(height):
            filter_type = raw[offset]
            offset += 1
            row = unfilter_png_scanline(filter_type, bytearray(raw[offset : offset + row_len]), prev, 4)
            offset += row_len
            row_out = bytearray(row)
            for alpha_idx in range(3, len(row_out), 4):
                row_out[alpha_idx] = 255 - row_out[alpha_idx]
            out.append(0)
            out.extend(row_out)
            prev = row
    except XaraError:
        return data

    rebuilt = bytearray(b"\x89PNG\r\n\x1a\n")
    compressed = zlib.compress(bytes(out))
    for chunk_type, chunk_data in chunks:
        if chunk_type == b"IDAT":
            rebuilt.extend(png_chunk(b"IDAT", compressed))
        else:
            rebuilt.extend(png_chunk(chunk_type, chunk_data))
    rebuilt.extend(png_chunk(b"IEND", b""))
    return bytes(rebuilt)


def default_color(ref: int) -> Optional[str]:
    defaults = {
        -1: None,
        -2: "#000000",
        2: "#000000",
        -3: "#ffffff",
        -4: "#ff0000",
        -5: "#00ff00",
        5: "#00ff00",
        -6: "#0000ff",
        -7: "#00ffff",
        -8: "#ff00ff",
        -9: "#ffff00",
    }
    return defaults.get(ref, "#000000")


DASH_UNIT = 72000 // 4
DEFAULT_DASHES: Dict[int, Tuple[int, ...]] = {
    -21: (),
    -1: (DASH_UNIT * 2, DASH_UNIT * 2),
    -2: (DASH_UNIT * 4, DASH_UNIT * 2),
    -3: (DASH_UNIT * 8, DASH_UNIT * 2),
    -4: (DASH_UNIT * 16, DASH_UNIT * 2),
    -5: (DASH_UNIT * 24, DASH_UNIT * 2),
    -6: (DASH_UNIT * 4, DASH_UNIT * 4),
    -7: (DASH_UNIT * 8, DASH_UNIT * 4),
    -8: (DASH_UNIT * 16, DASH_UNIT * 4),
    -9: (DASH_UNIT * 8, DASH_UNIT * 8),
    -10: (DASH_UNIT * 16, DASH_UNIT * 8),
    -11: (DASH_UNIT * 4, DASH_UNIT * 2, DASH_UNIT * 2, DASH_UNIT * 2),
    -12: (DASH_UNIT * 8, DASH_UNIT * 2, DASH_UNIT * 2, DASH_UNIT * 2),
    -13: (DASH_UNIT * 16, DASH_UNIT * 2, DASH_UNIT * 2, DASH_UNIT * 2),
    -14: (DASH_UNIT * 8, DASH_UNIT * 2, DASH_UNIT * 4, DASH_UNIT * 2),
    -15: (DASH_UNIT * 16, DASH_UNIT * 2, DASH_UNIT * 4, DASH_UNIT * 2),
    -16: (DASH_UNIT * 8, DASH_UNIT * 2, DASH_UNIT * 2, DASH_UNIT * 2, DASH_UNIT * 2, DASH_UNIT * 2),
    -17: (DASH_UNIT * 16, DASH_UNIT * 2, DASH_UNIT * 2, DASH_UNIT * 2, DASH_UNIT * 2, DASH_UNIT * 2),
    -22: (DASH_UNIT * 2, DASH_UNIT * 2),
}


class Parser:
    def __init__(self, data: bytes):
        self.data = data
        self.records: List[Record] = []
        self._seq = 0

    def parse(self) -> List[Record]:
        if not self.data.startswith(MAGIC):
            raise XaraError("not a XAR file: missing XARA magic")
        self._parse_stream(self.data, len(MAGIC), False, stop_at=None)
        if not self.records or self.records[0].tag != 2:
            raise XaraError("first record is not TAG_FILEHEADER")
        if self.records[-1].tag != 3:
            raise XaraError("last logical record is not TAG_ENDOFFILE")
        return self.records

    def _next_seq(self) -> int:
        self._seq += 1
        return self._seq

    def _parse_stream(
        self, data: bytes, pos: int, compressed: bool, stop_at: Optional[int]
    ) -> int:
        while pos < len(data):
            rec_offset = pos
            if pos + 8 > len(data):
                raise XaraError(f"truncated record header at byte {pos}")
            tag, size = struct.unpack_from("<II", data, pos)
            pos += 8
            if compressed and tag == 31:
                if size != 8:
                    raise XaraError("compressed TAG_ENDCOMPRESSION size is not 8")
                self.records.append(Record(self._next_seq(), tag, size, b"", rec_offset, True))
                if pos != len(data):
                    raise XaraError("compressed bytes remain after TAG_ENDCOMPRESSION")
                return pos
            if pos + size > len(data):
                raise XaraError(f"record {tag} at byte {rec_offset} exceeds stream length")
            payload = data[pos : pos + size]
            pos += size
            rec = Record(self._next_seq(), tag, size, payload, rec_offset, compressed)
            self.records.append(rec)
            if tag == 30:
                if size != 4 or payload[3] != 0:
                    raise XaraError("unsupported compression record")
                decomp, consumed = self._inflate_raw(data[pos:])
                before = len(self.records)
                self._parse_stream(decomp, 0, True, 31)
                if len(self.records) == before or self.records[-1].tag != 31:
                    raise XaraError("compressed section did not end with TAG_ENDCOMPRESSION")
                pos += consumed
                if pos + 8 > len(data):
                    raise XaraError("missing uncompressed TAG_ENDCOMPRESSION payload")
                crc, uncompressed_size = struct.unpack_from("<II", data, pos)
                pos += 8
                if (zlib.crc32(decomp) & 0xFFFFFFFF) != crc:
                    raise XaraError("compressed section CRC mismatch")
                if len(decomp) != uncompressed_size:
                    raise XaraError("compressed section uncompressed length mismatch")
                self.records[-1].payload = struct.pack("<II", crc, uncompressed_size)
            if stop_at is not None and tag == stop_at:
                return pos
        return pos

    @staticmethod
    def _inflate_raw(data: bytes) -> Tuple[bytes, int]:
        try:
            dobj = zlib.decompressobj(-15)
            out = dobj.decompress(data)
        except zlib.error as exc:
            raise XaraError(f"raw deflate decompression failed: {exc}") from exc
        if not dobj.eof:
            raise XaraError("unterminated raw deflate stream")
        consumed = len(data) - len(dobj.unused_data)
        return out, consumed


def build_tree(records: Sequence[Record]) -> List[Node]:
    roots: List[Node] = []
    stack: List[List[Node]] = [roots]
    last: Optional[Node] = None
    for rec in records:
        if rec.tag in (0, 1, 30, 31):
            if rec.tag == 1:
                if last is None:
                    raise XaraError("TAG_DOWN without a parent record")
                stack.append(last.children)
                last = None
            elif rec.tag == 0:
                if len(stack) == 1:
                    raise XaraError("TAG_UP without matching TAG_DOWN")
                stack.pop()
                last = stack[-1][-1] if stack[-1] else None
            continue
        node = Node(rec)
        stack[-1].append(node)
        last = node
    if len(stack) != 1:
        raise XaraError("unbalanced TAG_DOWN/TAG_UP records")
    return roots


class SvgRenderer:
    ATTR_TAGS = {
        150,
        151,
        152,
        153,
        154,
        155,
        156,
        157,
        158,
        160,
        161,
        162,
        163,
        164,
        165,
        166,
        167,
        168,
        169,
        170,
        171,
        172,
        173,
        174,
        175,
        176,
        177,
        178,
        180,
        181,
        182,
        183,
        190,
        191,
        192,
        193,
        194,
        195,
        200,
        201,
        204,
        206,
        2900,
        2901,
        2902,
        2903,
        2904,
        2906,
        2907,
        2908,
        2909,
        2910,
        2918,
        2919,
        2920,
        4201,
        4202,
        4203,
        4121,
        4123,
        4086,
    }
    PATH_TAGS = {100, 101, 102, 103, 113, 114, 115, 116}
    SHAPE_TAGS = {1000, 1001, 1100, 1104, 1108, 1110, 1112, 1114, 1200, 1212, 1216, 1901}
    CONTAINER_TAGS = {
        40,
        41,
        42,
        43,
        104,
        105,
        107,
        108,
        109,
        4050,
        2100,
        2101,
        2110,
        2114,
        2117,
        2200,
        4119,
        4131,
        4132,
    }

    def __init__(self, records: Sequence[Record], roots: Sequence[Node], page_index: int = 0):
        self.records = records
        self.roots = roots
        self.colors: Dict[int, Optional[str]] = {}
        self.bitmaps: Dict[int, Bitmap] = {}
        self.preview: Optional[bytes] = None
        self.preview_mime = "image/gif"
        self.fonts: Dict[int, str] = {}
        self.elements: List[str] = []
        self.defs: List[str] = []
        self._def_index = 0
        self.path_cache: Dict[int, List[Tuple[str, Tuple[float, ...]]]] = {}
        self.unsupported_render_tags: Dict[int, int] = {}
        self.coord_warp: Optional[Callable[[float, float], Tuple[float, float]]] = None
        self.pages = self._discover_pages()
        if page_index < 0 or page_index >= len(self.pages):
            raise XaraError("page index out of range")
        self.selected_page = self.pages[page_index]
        self.selected_layer_seqs = self.selected_page.layer_seqs
        self.selected_phase_seq = self.selected_page.phase_seq
        self.bitmap_boxes: List[Tuple[float, float, float, float]] = []
        self.viewbox = self._find_viewbox()
        self._collect_reusable_records()
        self._collect_bitmap_boxes()

    def render(self) -> str:
        ctx = Context()
        self._render_nodes(self.roots, ctx)
        if not self.elements and self.preview:
            self._render_preview_fallback()
        min_x, min_y, width, height = self.viewbox
        defs = "\n".join(self.defs)
        body = "\n".join(self.elements)
        unsupported = ", ".join(
            f"{TAG_NAMES.get(tag, tag)}:{count}"
            for tag, count in sorted(self.unsupported_render_tags.items())
        )
        desc = html.escape(
            f"Converted from XAR. Parsed {len(self.records)} records. "
            f"Unsupported rendered features: {unsupported or 'none noted'}."
        )
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" '
            'xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'viewBox="{fmt_num(min_x)} {fmt_num(min_y)} {fmt_num(width)} {fmt_num(height)}" '
            f'width="{fmt_num(width / 750)}" height="{fmt_num(height / 750)}">\n'
            f"<desc>{desc}</desc>\n"
            f"<defs>{defs}</defs>\n"
            f"{body}\n"
            "</svg>\n"
        )

    def _collect_reusable_records(self) -> None:
        for rec in self.records:
            p = rec.payload
            if rec.tag in (50, 51) and len(p) >= 3:
                self.colors[rec.seq] = f"#{p[0]:02x}{p[1]:02x}{p[2]:02x}"
            elif rec.tag == 67:
                self._store_bitmap(rec, "image/jpeg", (b"\xff\xd8",))
            elif rec.tag == 68:
                self._store_bitmap(rec, "image/png", (b"\x89PNG\r\n\x1a\n",), invert_png_alpha=True)
            elif rec.tag == 71:
                self._store_bitmap(rec, "image/jpeg", (b"\xff\xd8",))
            elif rec.tag == 61 and p.startswith((b"GIF87a", b"GIF89a")):
                self.preview = p
            elif rec.tag == 2000:
                name = font_name_from_payload(p)
                if name:
                    self.fonts[rec.seq] = name

    def _store_bitmap(
        self,
        rec: Record,
        mime: str,
        signatures: Sequence[bytes],
        invert_png_alpha: bool = False,
    ) -> None:
        p = rec.payload
        name, pos = split_utf16_cstr(p)
        start = pos if pos else find_image_start(p, signatures)
        if start < 0 or start >= len(p):
            return
        data = p[start:]
        if invert_png_alpha:
            data = invert_xara_png_alpha(data)
        self.bitmaps[rec.seq] = Bitmap(rec.seq, mime, name, data)

    def _find_viewbox(self) -> Tuple[float, float, float, float]:
        for rec in self.records:
            if rec.tag == 80 and len(rec.payload) == 16:
                bl = coord(rec.payload, 0)
                tr = coord(rec.payload, 8)
                return float(bl[0]), float(-tr[1]), float(tr[0] - bl[0]), float(tr[1] - bl[1])
        for rec in self.records:
            if rec.tag == 45 and len(rec.payload) >= 8:
                w = i32(rec.payload, 0)
                h = i32(rec.payload, 4)
                if w > 0 and h > 0:
                    return 0.0, float(-h), float(w), float(h)
        return 0.0, -96000.0, 96000.0, 96000.0

    def _render_nodes(self, nodes: Sequence[Node], ctx: Context) -> None:
        local = ctx
        for node in nodes:
            rec = node.record
            if rec.tag in self.ATTR_TAGS:
                self._apply_attr(rec, local)
                if node.children:
                    self._render_nodes(node.children, copy.deepcopy(local))
            elif rec.tag in self.CONTAINER_TAGS:
                if rec.tag == 4131:
                    if self.selected_phase_seq is None or rec.seq != self.selected_phase_seq:
                        continue
                if rec.tag in (4119, 4132):
                    continue
                if rec.tag == 43 and not self._layer_should_render(node):
                    continue
                if rec.tag in (2100, 2101, 2110, 2114, 2117):
                    self._render_text_story(node, copy.deepcopy(local))
                elif rec.tag == 105:
                    self._render_blend(node, copy.deepcopy(local))
                elif rec.tag in (107, 108):
                    self._render_mould(node, copy.deepcopy(local))
                elif rec.tag == 4050:
                    self._render_shadow_controller(node, copy.deepcopy(local))
                else:
                    self._render_nodes(node.children, copy.deepcopy(local))
            else:
                if node.children:
                    child_ctx = copy.deepcopy(local)
                    self._render_nodes(node.children, child_ctx)
                    self._render_visible(rec, child_ctx)
                else:
                    self._render_visible(rec, local)

    def _apply_attr(self, rec: Record, ctx: Context) -> None:
        p = rec.payload
        try:
            if rec.tag == 150 and len(p) >= 4:
                ctx.fill = Fill("solid", self._resolve_color(color_ref(p, 0)))
            elif rec.tag == 151 and len(p) >= 4:
                ctx.stroke = self._resolve_color(color_ref(p, 0))
            elif rec.tag == 152 and len(p) >= 4:
                ctx.line_width = max(0, i32(p, 0))
            elif rec.tag in (153, 154, 156) and len(p) >= 20:
                kind = {153: "linear", 154: "radial", 156: "conical"}[rec.tag]
                ctx.fill = Fill(
                    kind,
                    points=(coord(p, 0), coord(p, 8)),
                    colors=(self._resolve_color(color_ref(p, 16)), self._resolve_color(color_ref(p, 20))),
                )
            elif rec.tag == 4121 and len(p) >= 32:
                ctx.fill = Fill(
                    "linear",
                    points=(coord(p, 0), coord(p, 8), coord(p, 16)),
                    colors=(self._resolve_color(color_ref(p, 24)), self._resolve_color(color_ref(p, 28))),
                )
            elif rec.tag == 155 and len(p) >= 32:
                ctx.fill = Fill(
                    "elliptical",
                    points=(coord(p, 0), coord(p, 8), coord(p, 16)),
                    colors=(self._resolve_color(color_ref(p, 24)), self._resolve_color(color_ref(p, 28))),
                )
            elif rec.tag == 157 and len(p) >= 28:
                ctx.fill = Fill("bitmap", points=(coord(p, 0), coord(p, 8), coord(p, 16)), bitmap_ref=i32(p, 24))
            elif rec.tag == 158 and len(p) >= 36:
                ctx.fill = Fill("bitmap", points=(coord(p, 0), coord(p, 8), coord(p, 16)), bitmap_ref=i32(p, 32))
            elif rec.tag == 160:
                ctx.fill_effect = "fade"
            elif rec.tag == 161:
                ctx.fill_effect = "rainbow"
            elif rec.tag == 162:
                ctx.fill_effect = "alt-rainbow"
            elif rec.tag == 166 and len(p) >= 1:
                ctx.fill_opacity = max(0.0, min(1.0, 1.0 - p[0] / 255.0))
                ctx.fill_transparency = Transparency("flat", values=(p[0],), transp_type=p[1] if len(p) >= 2 else 1)
            elif rec.tag == 167 and len(p) >= 19:
                ctx.fill_opacity = 1.0
                ctx.fill_transparency = Transparency(
                    "linear", points=(coord(p, 0), coord(p, 8)), values=(p[16], p[17]), transp_type=p[18]
                )
            elif rec.tag == 168 and len(p) >= 19:
                ctx.fill_opacity = 1.0
                ctx.fill_transparency = Transparency(
                    "radial", points=(coord(p, 0), coord(p, 8)), values=(p[16], p[17]), transp_type=p[18]
                )
            elif rec.tag == 170 and len(p) >= 19:
                ctx.fill_opacity = max(0.0, min(1.0, 1.0 - ((p[16] + p[17]) / 2.0) / 255.0))
                ctx.fill_transparency = Transparency()
            elif rec.tag == 169 and len(p) >= 27:
                ctx.fill_opacity = 1.0
                ctx.fill_transparency = Transparency(
                    "elliptical", points=(coord(p, 0), coord(p, 8), coord(p, 16)), values=(p[24], p[25]), transp_type=p[26]
                )
            elif rec.tag == 4123 and len(p) >= 27:
                ctx.fill_opacity = 1.0
                ctx.fill_transparency = Transparency(
                    "linear", points=(coord(p, 0), coord(p, 8), coord(p, 16)), values=(p[24], p[25]), transp_type=p[26]
                )
            elif rec.tag == 171 and len(p) >= 31:
                ctx.fill_opacity = max(0.0, min(1.0, 1.0 - ((p[24] + p[25]) / 2.0) / 255.0))
                ctx.fill_transparency = Transparency()
            elif rec.tag == 172 and len(p) >= 27:
                ctx.fill_opacity = max(0.0, min(1.0, 1.0 - ((p[24] + p[25]) / 2.0) / 255.0))
                ctx.fill_transparency = Transparency()
            elif rec.tag == 173 and len(p) >= 1:
                ctx.stroke_opacity = max(0.0, min(1.0, 1.0 - p[0] / 255.0))
            elif rec.tag == 174 and p:
                ctx.line_cap = {0: "butt", 1: "round", 2: "square"}.get(p[0], "butt")
            elif rec.tag == 176 and p:
                ctx.line_join = {0: "miter", 1: "round", 2: "bevel"}.get(p[0], "bevel")
            elif rec.tag == 178 and p:
                ctx.fill_rule = "nonzero" if p[0] == 0 else "evenodd"
            elif rec.tag == 183 and len(p) >= 4:
                ctx.dasharray = DEFAULT_DASHES.get(i32(p, 0), ())
            elif rec.tag == 190:
                ctx.fill = Fill("none")
            elif rec.tag == 191:
                ctx.fill = Fill("solid", "#000000")
            elif rec.tag == 192:
                ctx.fill = Fill("solid", "#ffffff")
            elif rec.tag == 193:
                ctx.stroke = None
            elif rec.tag == 194:
                ctx.stroke = "#000000"
            elif rec.tag == 195:
                ctx.stroke = "#ffffff"
            elif rec.tag == 200 and len(p) >= 32:
                ctx.fill = Fill(
                    "elliptical",
                    points=(coord(p, 0), coord(p, 8), coord(p, 16)),
                    colors=(self._resolve_color(color_ref(p, 24)), self._resolve_color(color_ref(p, 28))),
                )
            elif rec.tag == 201 and len(p) >= 27:
                ctx.fill_opacity = 1.0
                ctx.fill_transparency = Transparency(
                    "elliptical", points=(coord(p, 0), coord(p, 8), coord(p, 16)), values=(p[24], p[25]), transp_type=p[26]
                )
            elif rec.tag == 4086 and len(p) >= 4:
                ctx.feather_width = max(0, i32(p, 0))
            elif rec.tag == 204 and len(p) >= 40:
                ctx.fill = Fill(
                    "fourcol",
                    points=(coord(p, 0), coord(p, 8), coord(p, 16)),
                    colors=(
                        self._resolve_color(color_ref(p, 24)),
                        self._resolve_color(color_ref(p, 28)),
                        self._resolve_color(color_ref(p, 32)),
                        self._resolve_color(color_ref(p, 36)),
                    ),
                )
            elif rec.tag == 2902:
                ctx.text_anchor = "start"
            elif rec.tag == 2903:
                ctx.text_anchor = "middle"
            elif rec.tag == 2904:
                ctx.text_anchor = "end"
            elif rec.tag == 2905:
                ctx.text_anchor = "start"
            elif rec.tag == 2906 and len(p) >= 4:
                ctx.font_size = max(1, i32(p, 0))
            elif rec.tag == 2907 and len(p) >= 4:
                ref = i32(p, 0)
                if ref in self.fonts:
                    ctx.font_family = self.fonts[ref]
            elif rec.tag == 2908:
                ctx.bold = True
            elif rec.tag == 2909:
                ctx.bold = False
            elif rec.tag == 2910:
                ctx.italic = True
            elif rec.tag == 2918 and len(p) >= 4:
                ctx.tracking = i32(p, 0)
            elif rec.tag == 2919 and len(p) >= 4:
                ctx.font_aspect = max(0.01, fixed16(p, 0))
            elif rec.tag == 2920 and len(p) >= 4:
                ctx.font_baseline = i32(p, 0)
            elif rec.tag == 4201 and len(p) >= 4:
                ctx.text_left_indent = i32(p, 0)
            elif rec.tag == 4202 and len(p) >= 4:
                ctx.text_first_indent = i32(p, 0)
            elif rec.tag == 4203 and len(p) >= 4:
                ctx.text_right_indent = i32(p, 0)
        except struct.error as exc:
            raise XaraError(f"bad payload for {rec.name}") from exc

    def _resolve_color(self, ref: int) -> Optional[str]:
        if ref in self.colors:
            return self.colors[ref]
        return default_color(ref)

    def _render_visible(self, rec: Record, ctx: Context) -> None:
        if rec.tag in self.PATH_TAGS:
            path = self._parse_path(rec)
            self.path_cache[rec.seq] = path
            self._emit_path(path, rec.tag, ctx)
        elif rec.tag == 118:
            self._render_pathref(rec, ctx)
        elif rec.tag in self.SHAPE_TAGS:
            path = self._shape_to_path(rec)
            if path:
                self.path_cache[rec.seq] = path
                self._emit_path(path, 116, ctx)
        elif rec.tag == 198:
            self._render_bitmap_node(rec, ctx)
        elif rec.tag in {105, 107, 108, 109, 110, 1114, 1216, 1901, 4128}:
            self.unsupported_render_tags[rec.tag] = self.unsupported_render_tags.get(rec.tag, 0) + 1

    def _collect_bitmap_boxes(self) -> None:
        self._collect_bitmap_boxes_nodes(self.roots, Context())

    def _collect_bitmap_boxes_nodes(self, nodes: Sequence[Node], ctx: Context) -> None:
        local = ctx
        for node in nodes:
            rec = node.record
            if rec.tag in self.ATTR_TAGS:
                self._apply_attr(rec, local)
                if node.children:
                    self._collect_bitmap_boxes_nodes(node.children, copy.deepcopy(local))
            elif rec.tag in self.CONTAINER_TAGS:
                if rec.tag == 4131:
                    if self.selected_phase_seq is None or rec.seq != self.selected_phase_seq:
                        continue
                if rec.tag in (4119, 4132):
                    continue
                if rec.tag == 43 and not self._layer_should_render(node):
                    continue
                self._collect_bitmap_boxes_nodes(node.children, copy.deepcopy(local))
            else:
                child_ctx = copy.deepcopy(local)
                if node.children:
                    self._collect_bitmap_boxes_nodes(node.children, child_ctx)
                if rec.tag in self.SHAPE_TAGS and child_ctx.fill.kind == "bitmap":
                    path = self._shape_to_path(rec)
                    box = path_bounds(path)
                    if box:
                        self.bitmap_boxes.append(box)
                elif rec.tag == 198 and len(rec.payload) == 36:
                    pts = [coord(rec.payload, off) for off in (0, 8, 16, 24)]
                    xs = [pt[0] for pt in pts]
                    ys = [pt[1] for pt in pts]
                    self.bitmap_boxes.append((min(xs), min(ys), max(xs), max(ys)))

    def _layer_should_render(self, node: Node) -> bool:
        if self.selected_layer_seqs is not None and node.record.seq not in self.selected_layer_seqs:
            return False
        details = self._layer_details(node)
        if details is None:
            return True
        visible, _name = details
        return visible

    def _discover_pages(self) -> List[PageBlock]:
        layers: List[Tuple[Node, Optional[int], str]] = []
        self._collect_layer_nodes(self.roots, layers, None, "")
        page_starts = [
            idx
            for idx, (layer, _phase_seq, _page_name) in enumerate(layers)
            if (self._layer_details(layer) or (False, ""))[1] == "Page background"
        ]
        if not page_starts:
            return [PageBlock("", None, None)]
        pages = []
        for page_idx, start in enumerate(page_starts):
            end = page_starts[page_idx + 1] if page_idx + 1 < len(page_starts) else len(layers)
            layer, phase_seq, page_name = layers[start]
            layer_seqs = {entry_layer.record.seq for entry_layer, _phase, _name in layers[start:end]}
            pages.append(PageBlock(page_name or f"page_{page_idx + 1}", layer_seqs, phase_seq))
        return pages

    def _collect_layer_nodes(
        self,
        nodes: Sequence[Node],
        out: List[Tuple[Node, Optional[int], str]],
        phase_seq: Optional[int],
        page_name: str,
    ) -> None:
        for node in nodes:
            child_page_name = self._page_name_from_children(node.children) or page_name
            child_phase_seq = phase_seq
            if node.record.tag == 4131:
                child_phase_seq = node.record.seq
            if node.record.tag == 43:
                out.append((node, phase_seq, page_name))
            if node.children:
                self._collect_layer_nodes(node.children, out, child_phase_seq, child_page_name)

    @staticmethod
    def _page_name_from_children(nodes: Sequence[Node]) -> str:
        for child in nodes:
            if child.record.tag == 4372 and child.record.payload:
                return utf16z_from_payload(child.record.payload)
        return ""

    @staticmethod
    def _layer_details(node: Node) -> Optional[Tuple[bool, str]]:
        for child in node.children:
            if child.record.tag == 48 and child.record.payload:
                payload = child.record.payload
                name = payload[1:].decode("utf-16le", errors="replace").rstrip("\x00")
                return bool(payload[0] & 1), name
        return None

    def _node_path_and_context(
        self, node: Node, base_ctx: Context
    ) -> Optional[Tuple[List[Tuple[str, Tuple[float, ...]]], int, Context]]:
        ctx = copy.deepcopy(base_ctx)
        for child in node.children:
            if child.record.tag in self.ATTR_TAGS:
                self._apply_attr(child.record, ctx)
        rec = node.record
        if rec.tag in self.PATH_TAGS:
            return self._parse_path(rec), rec.tag, ctx
        if rec.tag in self.SHAPE_TAGS:
            path = self._shape_to_path(rec)
            if path:
                return path, 116, ctx
        return None

    def _render_blend(self, node: Node, ctx: Context) -> None:
        if len(node.record.payload) < 3:
            self._render_nodes(node.children, copy.deepcopy(ctx))
            return
        steps = u16(node.record.payload, 0)
        if steps <= 0:
            self._render_nodes(node.children, copy.deepcopy(ctx))
            return
        local = copy.deepcopy(ctx)
        items: List[
            Tuple[
                str,
                Optional[Tuple[List[Tuple[str, Tuple[float, ...]]], int, Context]],
                Optional[Node],
                Context,
            ]
        ] = []
        for child in node.children:
            tag = child.record.tag
            if tag in self.ATTR_TAGS:
                self._apply_attr(child.record, local)
            elif tag == 106:
                items.append(("blender", None, child, copy.deepcopy(local)))
            elif tag in (4060, 4062, 4073, 4074):
                items.append(("blend_meta", None, child, copy.deepcopy(local)))
            else:
                item = self._node_path_and_context(child, local)
                if item:
                    items.append(("object", item, child, copy.deepcopy(local)))
                else:
                    items.append(("node", None, child, copy.deepcopy(local)))

        for idx, (kind, item, child, item_ctx) in enumerate(items):
            if kind == "object" and item:
                path, tag, obj_ctx = item
                if child is not None:
                    self.path_cache[child.record.seq] = path
                self._emit_path(path, tag, obj_ctx)
                next_obj_idx = next(
                    (j for j in range(idx + 1, len(items)) if items[j][0] == "object"),
                    None,
                )
                if next_obj_idx is None:
                    continue
                if not any(entry[0] == "blender" for entry in items[idx + 1 : next_obj_idx]):
                    continue
                next_item = items[next_obj_idx][1]
                if next_item is None:
                    self.unsupported_render_tags[106] = self.unsupported_render_tags.get(106, 0) + 1
                    continue
                end_path, _, end_ctx = next_item
                for step in range(1, steps + 1):
                    t = step / (steps + 1)
                    blended = interpolate_path(path, end_path, t)
                    if blended is None:
                        blended = interpolate_sampled_path(path, end_path, t)
                    if blended is None:
                        self.unsupported_render_tags[106] = self.unsupported_render_tags.get(106, 0) + 1
                        break
                    self._emit_path(blended, tag, blend_context(obj_ctx, end_ctx, t))
            elif kind == "node" and child is not None:
                self._render_nodes([child], copy.deepcopy(item_ctx))

    def _render_mould(self, node: Node, ctx: Context) -> None:
        mould_path = None
        mould_group = None
        for child in node.children:
            if child.record.tag == 110:
                mould_path = self._parse_absolute_path(child.record.payload)
            elif child.record.tag == 109:
                mould_group = child
        if mould_group is not None:
            source_box = self._nodes_geometry_bounds(mould_group.children)
            warp = self._mould_warp(source_box, mould_path, node.record.tag) if mould_path else None
            if warp:
                parent_warp = self.coord_warp

                def combined_warp(x: float, y: float) -> Tuple[float, float]:
                    wx, wy = warp(x, y)
                    return parent_warp(wx, wy) if parent_warp else (wx, wy)

                self.coord_warp = combined_warp
                try:
                    self._render_nodes(mould_group.children, copy.deepcopy(ctx))
                finally:
                    self.coord_warp = parent_warp
            else:
                before = len(self.elements)
                self._render_nodes(mould_group.children, copy.deepcopy(ctx))
                if mould_path:
                    target_box = path_bounds(mould_path)
                    transform = self._bbox_svg_transform(source_box, target_box)
                    if transform and len(self.elements) > before:
                        rendered = self.elements[before:]
                        self.elements[before:] = [f'<g transform="{transform}">' + "".join(rendered) + "</g>"]
                self.unsupported_render_tags[node.record.tag] = self.unsupported_render_tags.get(node.record.tag, 0) + 1

    def _render_shadow_controller(self, node: Node, ctx: Context) -> None:
        if len(node.record.payload) < 29:
            self._render_nodes(node.children, copy.deepcopy(ctx))
            return
        payload = node.record.payload
        shadow_type = payload[0]
        penumbra = i32(payload, 1)
        offset_x = i32(payload, 5)
        offset_y = i32(payload, 9)
        glow_width = i32(payload, 25)

        local = copy.deepcopy(ctx)
        target_nodes: List[Node] = []
        shadow_node: Optional[Node] = None
        found_shadow = False
        for child in node.children:
            if child.record.tag == 4051:
                shadow_node = child
                found_shadow = True
            elif not found_shadow and child.record.tag in self.ATTR_TAGS:
                self._apply_attr(child.record, local)
            else:
                target_nodes.append(child)
        if not found_shadow or not target_nodes:
            self._render_nodes(node.children, copy.deepcopy(ctx))
            return

        shadow_ctx = copy.deepcopy(local)
        if shadow_node:
            for child in shadow_node.children:
                if child.record.tag in self.ATTR_TAGS:
                    self._apply_attr(child.record, shadow_ctx)
        shadow_color = shadow_ctx.fill.color or "#000000"
        shadow_opacity = shadow_ctx.fill_opacity
        if shadow_node and len(shadow_node.record.payload) >= 24:
            shadow_opacity *= max(0.0, min(1.0, f64(shadow_node.record.payload, 16)))
        shadow_opacity = max(0.0, min(1.0, shadow_opacity))

        if shadow_type == 1:
            dx = float(offset_x)
            dy = float(-offset_y)
            blur = max(0.0, penumbra / 2.0)
        elif shadow_type == 2:
            self._render_floor_shadow(
                target_nodes,
                local,
                shadow_color,
                shadow_opacity,
                penumbra,
                offset_x,
                offset_y,
                i32(payload, 13),
                i32(payload, 17),
            )
            return
        elif shadow_type == 3:
            dx = dy = 0.0
            blur = max(0.0, glow_width / 2.0)
        else:
            self._render_nodes(target_nodes, local)
            self.unsupported_render_tags[node.record.tag] = self.unsupported_render_tags.get(node.record.tag, 0) + 1
            return

        fid = self._new_def_id("shadow")
        self.defs.append(
            f'<filter id="{fid}" x="-50%" y="-50%" width="200%" height="200%">'
            f'<feDropShadow dx="{fmt_num(dx)}" dy="{fmt_num(dy)}" stdDeviation="{fmt_num(blur)}" '
            f'flood-color="{shadow_color}" flood-opacity="{fmt_num(shadow_opacity)}"/>'
            "</filter>"
        )
        before = len(self.elements)
        self._render_nodes(target_nodes, local)
        if len(self.elements) > before:
            rendered = self.elements[before:]
            self.elements[before:] = [f'<g filter="url(#{fid})">' + "".join(rendered) + "</g>"]

    def _render_floor_shadow(
        self,
        target_nodes: Sequence[Node],
        ctx: Context,
        shadow_color: str,
        shadow_opacity: float,
        penumbra: int,
        offset_x: int,
        offset_y: int,
        floor_angle: int,
        floor_height: int,
    ) -> None:
        source_box = self._nodes_geometry_bounds(target_nodes)
        if not source_box:
            self._render_nodes(target_nodes, ctx)
            return
        x0, y0, x1, _y1 = source_box
        anchor_y = svg_y(y0)
        angle = max(-math.tau, min(math.tau, floor_angle / 1000000.0))
        scale_y = max(0.01, min(4.0, floor_height / 100.0))
        shear = -math.tan(angle)
        dx = float(offset_x)
        dy = float(-offset_y)
        e = dx - shear * anchor_y
        f = anchor_y * (1.0 - scale_y) + dy
        blur = max(0.0, penumbra / 2.0)
        pad = max(1000.0, blur * 6.0)
        min_x, min_y, width, height = self.viewbox

        fid = self._new_def_id("floorshadow")
        self.defs.append(
            f'<filter id="{fid}" filterUnits="userSpaceOnUse" '
            f'x="{fmt_num(min_x - pad)}" y="{fmt_num(min_y - pad)}" '
            f'width="{fmt_num(width + pad * 2.0)}" height="{fmt_num(height + pad * 2.0)}" '
            'color-interpolation-filters="sRGB">'
            f'<feGaussianBlur in="SourceAlpha" stdDeviation="{fmt_num(blur)}" result="blur"/>'
            f'<feFlood flood-color="{shadow_color}" flood-opacity="{fmt_num(shadow_opacity)}" result="color"/>'
            '<feComposite in="color" in2="blur" operator="in"/>'
            "</filter>"
        )

        before = len(self.elements)
        self._render_nodes(target_nodes, copy.deepcopy(ctx))
        shadow_elements = self.elements[before:]
        self.elements[before:] = []
        if shadow_elements:
            transform = (
                f"matrix(1 0 {fmt_num(shear)} {fmt_num(scale_y)} "
                f"{fmt_num(e)} {fmt_num(f)})"
            )
            self.elements.append(
                f'<g transform="{transform}" filter="url(#{fid})">'
                + "".join(shadow_elements)
                + "</g>"
            )
        self._render_nodes(target_nodes, ctx)

    def _mould_warp(
        self,
        source_box: Optional[Tuple[float, float, float, float]],
        mould_path: Optional[Sequence[Tuple[str, Tuple[float, ...]]]],
        mould_tag: int,
    ) -> Optional[Callable[[float, float], Tuple[float, float]]]:
        if not source_box or not mould_path:
            return None
        sx0, sy0, sx1, sy1 = source_box
        if abs(sx1 - sx0) < 1e-9 or abs(sy1 - sy0) < 1e-9:
            return None
        corners = self._mould_quad(mould_path)
        if corners is None:
            return None
        p00, p01, p11, p10 = corners
        if mould_tag == 108:
            homography = projective_transform_from_unit_square((p00, p01, p11, p10))
            if homography:
                def perspective_warp(x: float, y: float) -> Tuple[float, float]:
                    u = (x - sx0) / (sx1 - sx0)
                    v = (y - sy0) / (sy1 - sy0)
                    return apply_projective_transform(homography, u, v)

                return perspective_warp

        def bilinear_warp(x: float, y: float) -> Tuple[float, float]:
            u = (x - sx0) / (sx1 - sx0)
            v = (y - sy0) / (sy1 - sy0)
            x0 = (1 - u) * (1 - v) * p00[0] + (1 - u) * v * p01[0] + u * v * p11[0] + u * (1 - v) * p10[0]
            y0 = (1 - u) * (1 - v) * p00[1] + (1 - u) * v * p01[1] + u * v * p11[1] + u * (1 - v) * p10[1]
            return x0, y0

        return bilinear_warp

    @staticmethod
    def _mould_quad(
        mould_path: Sequence[Tuple[str, Tuple[float, ...]]]
    ) -> Optional[Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float], Tuple[float, float]]]:
        points: List[Tuple[float, float]] = []
        for cmd, vals in mould_path:
            if cmd in ("M", "L") and len(vals) >= 2:
                pt = (vals[0], vals[1])
            elif cmd == "C" and len(vals) >= 6:
                pt = (vals[4], vals[5])
            else:
                continue
            if not points or pt != points[-1]:
                points.append(pt)
        if len(points) >= 2 and points[0] == points[-1]:
            points.pop()
        if len(points) < 4:
            return None
        return points[0], points[1], points[2], points[3]

    def _nodes_geometry_bounds(self, nodes: Sequence[Node]) -> Optional[Tuple[float, float, float, float]]:
        boxes: List[Tuple[float, float, float, float]] = []
        local_paths: Dict[int, List[Tuple[str, Tuple[float, ...]]]] = {}

        def add_path(rec: Record, path: List[Tuple[str, Tuple[float, ...]]]) -> None:
            local_paths[rec.seq] = path
            box = path_bounds(path)
            if box:
                boxes.append(box)

        def visit(children: Sequence[Node]) -> None:
            for child in children:
                rec = child.record
                if rec.tag in self.PATH_TAGS:
                    add_path(rec, self._parse_path(rec))
                elif rec.tag in self.SHAPE_TAGS:
                    path = self._shape_to_path(rec)
                    if path:
                        add_path(rec, path)
                elif rec.tag == 118:
                    path = self._transformed_pathref_path(rec, local_paths)
                    if path:
                        add_path(rec, path)
                if child.children:
                    visit(child.children)

        visit(nodes)
        if not boxes:
            return None
        return (
            min(box[0] for box in boxes),
            min(box[1] for box in boxes),
            max(box[2] for box in boxes),
            max(box[3] for box in boxes),
        )

    def _transformed_pathref_path(
        self, rec: Record, local_paths: Optional[Dict[int, List[Tuple[str, Tuple[float, ...]]]]] = None
    ) -> Optional[List[Tuple[str, Tuple[float, ...]]]]:
        p = rec.payload
        if len(p) != 28:
            return None
        ref = i32(p, 0)
        src = (local_paths or {}).get(ref) or self.path_cache.get(ref)
        if not src:
            return None
        a, b, c, d = fixed16(p, 4), fixed16(p, 8), fixed16(p, 12), fixed16(p, 16)
        e, f = i32(p, 20), i32(p, 24)

        def tx(x: float, y: float) -> Tuple[float, float]:
            return a * x + c * y + e, b * x + d * y + f

        transformed = []
        for cmd, vals in src:
            if cmd in ("M", "L"):
                transformed.append((cmd, tx(vals[0], vals[1])))
            elif cmd == "C":
                p1 = tx(vals[0], vals[1])
                p2 = tx(vals[2], vals[3])
                p3 = tx(vals[4], vals[5])
                transformed.append(("C", p1 + p2 + p3))
            else:
                transformed.append((cmd, vals))
        return transformed

    @staticmethod
    def _bbox_svg_transform(
        source_box: Optional[Tuple[float, float, float, float]],
        target_box: Optional[Tuple[float, float, float, float]],
    ) -> Optional[str]:
        if not source_box or not target_box:
            return None
        sx0, sy0, sx1, sy1 = source_box
        tx0, ty0, tx1, ty1 = target_box
        source_w = sx1 - sx0
        source_h = sy1 - sy0
        target_w = tx1 - tx0
        target_h = ty1 - ty0
        if source_w == 0 or source_h == 0 or target_w == 0 or target_h == 0:
            return None
        scale_x = target_w / source_w
        scale_y = target_h / source_h
        source_svg_y0 = svg_y(sy1)
        target_svg_y0 = svg_y(ty1)
        translate_x = tx0 - scale_x * sx0
        translate_y = target_svg_y0 - scale_y * source_svg_y0
        return (
            f"matrix({fmt_num(scale_x)} 0 0 {fmt_num(scale_y)} "
            f"{fmt_num(translate_x)} {fmt_num(translate_y)})"
        )

    def _style(self, tag: int, ctx: Context) -> str:
        return self._path_style(tag in (101, 103, 114, 116), tag in (102, 103, 115, 116), ctx)

    def _path_style(
        self,
        filled: bool,
        stroked: bool,
        ctx: Context,
        use_fill_transparency: bool = True,
    ) -> str:
        fill = "none"
        if filled:
            fill = self._fill_paint(ctx.fill, ctx.fill_effect)
        stroke = "none"
        if stroked and ctx.stroke and ctx.line_width > 0:
            stroke = ctx.stroke
        attrs = [
            f'fill="{fill}"',
            f'stroke="{stroke}"',
            f'stroke-width="{ctx.line_width}"',
            f'stroke-linecap="{ctx.line_cap}"',
            f'stroke-linejoin="{ctx.line_join}"',
            f'fill-rule="{ctx.fill_rule}"',
        ]
        if filled and ctx.fill_opacity < 1:
            attrs.append(f'fill-opacity="{fmt_num(ctx.fill_opacity)}"')
        if filled and use_fill_transparency and ctx.feather_width <= 0:
            mask = self._transparency_mask_attr(ctx.fill_transparency)
            if mask:
                attrs.append(mask)
        if ctx.stroke_opacity < 1:
            attrs.append(f'stroke-opacity="{fmt_num(ctx.stroke_opacity)}"')
        blend_mode = self._transparency_blend_mode(ctx.fill_transparency.transp_type)
        if blend_mode:
            attrs.append(f'style="mix-blend-mode:{blend_mode}"')
        if ctx.dasharray:
            attrs.append('stroke-dasharray="' + " ".join(fmt_num(v) for v in ctx.dasharray) + '"')
            if ctx.dashoffset:
                attrs.append(f'stroke-dashoffset="{fmt_num(ctx.dashoffset)}"')
        return " ".join(attrs)

    @staticmethod
    def _transparency_blend_mode(transp_type: int) -> str:
        return {
            2: "multiply",
            3: "screen",
            4: "overlay",
            5: "saturation",
            6: "darken",
            7: "lighten",
            9: "luminosity",
            10: "hue",
        }.get(transp_type, "")

    @staticmethod
    def _transparency_stop(value: int) -> float:
        return max(0.0, min(1.0, 1.0 - value / 255.0))

    def _transparency_mask_attr(self, transparency: Transparency) -> str:
        paint = self._transparency_mask_paint(transparency)
        if paint == "#ffffff":
            return ""
        mid = self._new_def_id("tm")
        min_x, min_y, width, height = self.viewbox
        self.defs.append(
            f'<mask id="{mid}" maskUnits="userSpaceOnUse" maskContentUnits="userSpaceOnUse" '
            f'x="{fmt_num(min_x)}" y="{fmt_num(min_y)}" width="{fmt_num(width)}" height="{fmt_num(height)}" '
            'mask-type="alpha">'
            f'<rect x="{fmt_num(min_x)}" y="{fmt_num(min_y)}" width="{fmt_num(width)}" '
            f'height="{fmt_num(height)}" fill="{paint}"/>'
            "</mask>"
        )
        return f'mask="url(#{mid})"'

    def _transparency_mask_paint(self, transparency: Transparency) -> str:
        if transparency.kind == "none" or len(transparency.values) < 2:
            return "#ffffff"
        op0 = self._transparency_stop(transparency.values[0])
        op1 = self._transparency_stop(transparency.values[1])
        if abs(op0 - 1.0) < 1e-9 and abs(op1 - 1.0) < 1e-9:
            return "#ffffff"
        gid = self._new_def_id("tg")
        if transparency.kind == "linear" and len(transparency.points) >= 2:
            (x1, y1), (x2, y2) = transparency.points[0], transparency.points[1]
            gradient = (
                f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" '
                f'x1="{fmt_num(x1)}" y1="{fmt_num(svg_y(y1))}" x2="{fmt_num(x2)}" y2="{fmt_num(svg_y(y2))}">'
                f'<stop offset="0%" stop-color="#ffffff" stop-opacity="{fmt_num(op0)}"/>'
                f'<stop offset="100%" stop-color="#ffffff" stop-opacity="{fmt_num(op1)}"/>'
                "</linearGradient>"
            )
        elif transparency.kind == "radial" and len(transparency.points) >= 2:
            (cx, cy), (ex, ey) = transparency.points[0], transparency.points[1]
            radius = max(1.0, math.hypot(ex - cx, ey - cy))
            gradient = (
                f'<radialGradient id="{gid}" gradientUnits="userSpaceOnUse" '
                f'cx="{fmt_num(cx)}" cy="{fmt_num(svg_y(cy))}" r="{fmt_num(radius)}">'
                f'<stop offset="0%" stop-color="#ffffff" stop-opacity="{fmt_num(op0)}"/>'
                f'<stop offset="100%" stop-color="#ffffff" stop-opacity="{fmt_num(op1)}"/>'
                "</radialGradient>"
            )
        elif transparency.kind == "elliptical" and len(transparency.points) >= 3:
            (cx, cy), major, minor = transparency.points[0], transparency.points[1], transparency.points[2]
            a = major[0] - cx
            b = svg_y(major[1] - cy)
            c = minor[0] - cx
            d = svg_y(minor[1] - cy)
            e = cx
            f = svg_y(cy)
            gradient = (
                f'<radialGradient id="{gid}" gradientUnits="userSpaceOnUse" cx="0" cy="0" r="1" '
                f'gradientTransform="matrix({fmt_num(a)} {fmt_num(b)} {fmt_num(c)} {fmt_num(d)} '
                f'{fmt_num(e)} {fmt_num(f)})">'
                f'<stop offset="0%" stop-color="#ffffff" stop-opacity="{fmt_num(op0)}"/>'
                f'<stop offset="100%" stop-color="#ffffff" stop-opacity="{fmt_num(op1)}"/>'
                "</radialGradient>"
            )
        else:
            return "#ffffff"
        self.defs.append(gradient)
        return f"url(#{gid})"

    def _fill_mask_attr_for_path(self, ctx: Context, d: str) -> str:
        paint = self._transparency_mask_paint(ctx.fill_transparency)
        if ctx.feather_width <= 0 and paint == "#ffffff":
            return ""
        mid = self._new_def_id("fm")
        min_x, min_y, width, height = self.viewbox
        pad = max(0.0, ctx.feather_width * 4.0)
        x = min_x - pad
        y = min_y - pad
        w = width + pad * 2.0
        h = height + pad * 2.0
        filter_attr = ""
        filter_def = ""
        if ctx.feather_width > 0:
            fid = self._new_def_id("feather")
            std_dev = max(0.1, ctx.feather_width / 2.0)
            filter_def = (
                f'<filter id="{fid}" filterUnits="userSpaceOnUse" '
                f'x="{fmt_num(x)}" y="{fmt_num(y)}" width="{fmt_num(w)}" height="{fmt_num(h)}">'
                f'<feGaussianBlur stdDeviation="{fmt_num(std_dev)}"/>'
                "</filter>"
            )
            filter_attr = f' filter="url(#{fid})"'
        self.defs.append(
            filter_def
            + f'<mask id="{mid}" maskUnits="userSpaceOnUse" maskContentUnits="userSpaceOnUse" '
            f'x="{fmt_num(x)}" y="{fmt_num(y)}" width="{fmt_num(w)}" height="{fmt_num(h)}" '
            'mask-type="alpha">'
            f'<path d="{d}" fill="{paint}" fill-rule="{ctx.fill_rule}" stroke="none"{filter_attr}/>'
            "</mask>"
        )
        return f'mask="url(#{mid})"'

    def _new_def_id(self, prefix: str) -> str:
        self._def_index += 1
        return f"{prefix}{self._def_index}"

    def _fill_paint(self, fill: Fill, fill_effect: str = "fade") -> str:
        if fill.kind == "none":
            return "none"
        if fill.kind == "solid":
            return fill.color or "none"
        if fill.kind == "linear" and len(fill.points) >= 2 and len(fill.colors) >= 2:
            gid = self._new_def_id("lg")
            points = self._warp_points(fill.points)
            (x1, y1), (x2, y2) = points[0], points[1]
            c0 = fill.colors[0] or "transparent"
            c1 = fill.colors[1] or "transparent"
            self.defs.append(
                f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" '
                f'x1="{fmt_num(x1)}" y1="{fmt_num(svg_y(y1))}" x2="{fmt_num(x2)}" y2="{fmt_num(svg_y(y2))}">'
                f'{self._gradient_stops(c0, c1, fill_effect)}'
                "</linearGradient>"
            )
            return f"url(#{gid})"
        if fill.kind == "radial" and len(fill.points) >= 2 and len(fill.colors) >= 2:
            gid = self._new_def_id("rg")
            points = self._warp_points(fill.points)
            (cx, cy), (ex, ey) = points[0], points[1]
            radius = max(1.0, math.hypot(ex - cx, ey - cy))
            c0 = fill.colors[0] or "transparent"
            c1 = fill.colors[1] or "transparent"
            self.defs.append(
                f'<radialGradient id="{gid}" gradientUnits="userSpaceOnUse" '
                f'cx="{fmt_num(cx)}" cy="{fmt_num(svg_y(cy))}" r="{fmt_num(radius)}">'
                f'{self._gradient_stops(c0, c1, fill_effect)}'
                "</radialGradient>"
            )
            return f"url(#{gid})"
        if fill.kind == "conical" and len(fill.points) >= 2 and len(fill.colors) >= 2:
            return self._conical_fill_paint(fill, fill_effect)
        if fill.kind == "elliptical" and len(fill.points) >= 3 and len(fill.colors) >= 2:
            gid = self._new_def_id("eg")
            points = self._warp_points(fill.points)
            (cx, cy), major, minor = points[0], points[1], points[2]
            c0 = fill.colors[0] or "transparent"
            c1 = fill.colors[1] or "transparent"
            a = major[0] - cx
            b = svg_y(major[1] - cy)
            c = minor[0] - cx
            d = svg_y(minor[1] - cy)
            e = cx
            f = svg_y(cy)
            self.defs.append(
                f'<radialGradient id="{gid}" gradientUnits="userSpaceOnUse" cx="0" cy="0" r="1" '
                f'gradientTransform="matrix({fmt_num(a)} {fmt_num(b)} {fmt_num(c)} {fmt_num(d)} {fmt_num(e)} {fmt_num(f)})">'
                f'{self._gradient_stops(c0, c1, fill_effect)}'
                "</radialGradient>"
            )
            return f"url(#{gid})"
        if fill.kind == "fourcol" and len(fill.points) >= 3 and len(fill.colors) >= 4:
            pid = self._new_def_id("fc")
            gx1 = self._new_def_id("fcg")
            gx2 = self._new_def_id("fcg")
            points = self._warp_points(fill.points)
            start, end1, end2 = points[0], points[1], points[2]
            c0 = fill.colors[0] or "transparent"
            c1 = fill.colors[1] or "transparent"
            c2 = fill.colors[2] or "transparent"
            c3 = fill.colors[3] or "transparent"
            a = end1[0] - start[0]
            b = svg_y(end1[1] - start[1])
            c = start[0] - end2[0]
            d = svg_y(start[1] - end2[1])
            e = end2[0]
            f = svg_y(end2[1])
            self.defs.append(
                f'<linearGradient id="{gx1}" x1="0" y1="0" x2="1" y2="0">'
                f'<stop offset="0%" stop-color="{c0}"/><stop offset="100%" stop-color="{c1}"/>'
                "</linearGradient>"
                f'<linearGradient id="{gx2}" x1="0" y1="0" x2="1" y2="0">'
                f'<stop offset="0%" stop-color="{c2}"/><stop offset="100%" stop-color="{c3}"/>'
                "</linearGradient>"
                f'<pattern id="{pid}" patternUnits="userSpaceOnUse" x="0" y="0" width="1" height="1" '
                f'patternTransform="matrix({fmt_num(a)} {fmt_num(b)} {fmt_num(c)} {fmt_num(d)} {fmt_num(e)} {fmt_num(f)})">'
                f'<rect x="0" y="0" width="1" height="1" fill="url(#{gx1})"/>'
                f'<rect x="0" y="0" width="1" height="1" fill="url(#{gx2})" opacity="0.5"/>'
                "</pattern>"
            )
            return f"url(#{pid})"
        if fill.kind == "bitmap" and len(fill.points) >= 3 and fill.bitmap_ref is not None:
            bitmap = self.bitmaps.get(fill.bitmap_ref)
            if not bitmap:
                return "none"
            pid = self._new_def_id("pat")
            points = self._warp_points(fill.points)
            bl, br, tl = points[0], points[1], points[2]
            href = f"data:{bitmap.mime};base64,{base64.b64encode(bitmap.data).decode('ascii')}"
            a = br[0] - bl[0]
            b = svg_y(br[1] - bl[1])
            c = bl[0] - tl[0]
            d = svg_y(bl[1] - tl[1])
            e = tl[0]
            f = svg_y(tl[1])
            self.defs.append(
                f'<pattern id="{pid}" patternUnits="userSpaceOnUse" x="0" y="0" width="1" height="1" '
                f'patternTransform="matrix({fmt_num(a)} {fmt_num(b)} {fmt_num(c)} {fmt_num(d)} {fmt_num(e)} {fmt_num(f)})">'
                f'<image x="0" y="0" width="1" height="1" preserveAspectRatio="none" href="{href}"/>'
                "</pattern>"
            )
            return f"url(#{pid})"
        return fill.color or "none"

    @staticmethod
    def _gradient_stops(c0: str, c1: str, fill_effect: str) -> str:
        if fill_effect not in ("rainbow", "alt-rainbow"):
            return f'<stop offset="0%" stop-color="{c0}"/><stop offset="100%" stop-color="{c1}"/>'
        colors = rainbow_color_ramp(c0, c1, fill_effect == "alt-rainbow", 16)
        if not colors:
            return f'<stop offset="0%" stop-color="{c0}"/><stop offset="100%" stop-color="{c1}"/>'
        denom = max(1, len(colors) - 1)
        return "".join(
            f'<stop offset="{fmt_num(100.0 * idx / denom)}%" stop-color="{color}"/>'
            for idx, color in enumerate(colors)
        )

    def _conical_fill_paint(self, fill: Fill, fill_effect: str = "fade") -> str:
        pid = self._new_def_id("cg")
        points = self._warp_points(fill.points)
        (cx, cy), (ex, ey) = points[0], points[1]
        c0 = fill.colors[0] or "#000000"
        c1 = fill.colors[1] or c0
        min_x, min_y, width, height = self.viewbox
        radius = max(width, height) * 1.5
        scx = cx
        scy = svg_y(cy)
        start_angle = math.atan2(svg_y(ey - cy), ex - cx)
        steps = 96
        wedges: List[str] = []
        for idx in range(steps):
            a0 = start_angle + (idx / steps) * math.tau
            a1 = start_angle + ((idx + 1) / steps) * math.tau
            mid = (idx + 0.5) / steps
            color = blend_fill_effect_color(c0, c1, mid, fill_effect) or c0
            x0 = scx + math.cos(a0) * radius
            y0 = scy + math.sin(a0) * radius
            x1 = scx + math.cos(a1) * radius
            y1 = scy + math.sin(a1) * radius
            points_attr = " ".join(
                (
                    f"{fmt_num(scx)},{fmt_num(scy)}",
                    f"{fmt_num(x0)},{fmt_num(y0)}",
                    f"{fmt_num(x1)},{fmt_num(y1)}",
                )
            )
            wedges.append(f'<polygon points="{points_attr}" fill="{color}"/>')
        self.defs.append(
            f'<pattern id="{pid}" patternUnits="userSpaceOnUse" x="{fmt_num(min_x)}" y="{fmt_num(min_y)}" '
            f'width="{fmt_num(width)}" height="{fmt_num(height)}">'
            + "".join(wedges)
            + "</pattern>"
        )
        return f"url(#{pid})"

    def _emit_path(
        self, commands: Sequence[Tuple[str, Tuple[float, ...]]], tag: int, ctx: Context
    ) -> None:
        if not commands:
            return
        commands = self._warp_commands(commands)
        d = xml_attr(self._commands_to_svg_d(commands))
        filled = tag in (101, 103, 114, 116)
        stroked = tag in (102, 103, 115, 116) and ctx.stroke and ctx.line_width > 0
        masked_fill = filled and (ctx.feather_width > 0 or ctx.fill_transparency.kind != "none")
        if masked_fill:
            attrs = self._path_style(True, False, ctx, False)
            mask = self._fill_mask_attr_for_path(ctx, d)
            if mask:
                attrs += f" {mask}"
            self.elements.append(f'<path d="{d}" {attrs}/>')
            if stroked:
                self.elements.append(f'<path d="{d}" {self._path_style(False, True, ctx, False)}/>')
        else:
            self.elements.append(f'<path d="{d}" {self._style(tag, ctx)}/>')

    def _warp_point(self, point: Tuple[float, float]) -> Tuple[float, float]:
        if self.coord_warp is None:
            return point
        return self.coord_warp(point[0], point[1])

    def _warp_points(
        self, points: Sequence[Tuple[float, float]]
    ) -> Tuple[Tuple[float, float], ...]:
        if self.coord_warp is None:
            return tuple(points)
        return tuple(self._warp_point(point) for point in points)

    def _warp_commands(
        self, commands: Sequence[Tuple[str, Tuple[float, ...]]]
    ) -> List[Tuple[str, Tuple[float, ...]]]:
        if self.coord_warp is None:
            return list(commands)
        out: List[Tuple[str, Tuple[float, ...]]] = []
        for cmd, vals in commands:
            if cmd in ("M", "L") and len(vals) >= 2:
                out.append((cmd, self.coord_warp(vals[0], vals[1])))
            elif cmd == "C" and len(vals) >= 6:
                p1 = self.coord_warp(vals[0], vals[1])
                p2 = self.coord_warp(vals[2], vals[3])
                p3 = self.coord_warp(vals[4], vals[5])
                out.append(("C", p1 + p2 + p3))
            else:
                out.append((cmd, vals))
        return out

    @staticmethod
    def _commands_to_svg_d(commands: Sequence[Tuple[str, Tuple[float, ...]]]) -> str:
        dparts = []
        for cmd, vals in commands:
            if cmd == "Z":
                dparts.append("Z")
            else:
                svg_vals = tuple(svg_y(v) if idx % 2 else v for idx, v in enumerate(vals))
                dparts.append(cmd + " " + " ".join(fmt_num(v) for v in svg_vals))
        return " ".join(dparts)

    def _parse_path(self, rec: Record) -> List[Tuple[str, Tuple[float, ...]]]:
        if rec.tag in (113, 114, 115, 116):
            return self._parse_relative_path(rec.payload)
        return self._parse_absolute_path(rec.payload)

    def _parse_absolute_path(self, p: bytes) -> List[Tuple[str, Tuple[float, ...]]]:
        if len(p) < 4:
            return []
        n = u32(p, 0)
        expected = 4 + n + n * 8
        if expected > len(p):
            raise XaraError("absolute path payload is truncated")
        verbs = p[4 : 4 + n]
        coords = [coord(p, 4 + n + i * 8) for i in range(n)]
        return self._verbs_coords_to_path(verbs, coords)

    def _parse_embedded_absolute_path(
        self, p: bytes, offset: int
    ) -> Tuple[List[Tuple[str, Tuple[float, ...]]], int]:
        if offset + 4 > len(p):
            raise XaraError("embedded path is truncated")
        n = u32(p, offset)
        expected = 4 + n + n * 8
        end = offset + expected
        if end > len(p):
            raise XaraError("embedded path payload is truncated")
        verbs = p[offset + 4 : offset + 4 + n]
        coords = [coord(p, offset + 4 + n + i * 8) for i in range(n)]
        return self._verbs_coords_to_path(verbs, coords), end

    def _parse_relative_path(self, p: bytes) -> List[Tuple[str, Tuple[float, ...]]]:
        if len(p) % 9 != 0:
            raise XaraError("relative path payload is not a multiple of 9")
        verbs = []
        coords = []
        prev = (0, 0)
        for off in range(0, len(p), 9):
            verb = p[off]
            value = signed_interleaved_coord(p[off + 1 : off + 9])
            if off == 0:
                cur = value
            else:
                cur = (prev[0] - value[0], prev[1] - value[1])
            verbs.append(verb)
            coords.append(cur)
            prev = cur
        return self._verbs_coords_to_path(verbs, coords)

    def _verbs_coords_to_path(
        self, verbs: Sequence[int], coords: Sequence[Tuple[int, int]]
    ) -> List[Tuple[str, Tuple[float, ...]]]:
        out: List[Tuple[str, Tuple[float, ...]]] = []
        i = 0
        while i < len(verbs):
            verb = verbs[i] & 0xFE
            close = bool(verbs[i] & 1)
            x, y = coords[i]
            if verb == 6:
                out.append(("M", (x, y)))
                i += 1
            elif verb == 2:
                out.append(("L", (x, y)))
                if close:
                    out.append(("Z", ()))
                i += 1
            elif verb == 4:
                if i + 2 >= len(verbs):
                    break
                x1, y1 = coords[i]
                x2, y2 = coords[i + 1]
                x3, y3 = coords[i + 2]
                out.append(("C", (x1, y1, x2, y2, x3, y3)))
                if verbs[i + 2] & 1:
                    out.append(("Z", ()))
                i += 3
            else:
                i += 1
        return out

    def _render_pathref(self, rec: Record, ctx: Context) -> None:
        transformed = self._transformed_pathref_path(rec)
        if not transformed:
            self.unsupported_render_tags[rec.tag] = self.unsupported_render_tags.get(rec.tag, 0) + 1
            return
        self.path_cache[rec.seq] = transformed
        self._emit_path(transformed, 116, ctx)

    def _shape_to_path(self, rec: Record) -> List[Tuple[str, Tuple[float, ...]]]:
        p = rec.payload
        if rec.tag in (1000, 1100, 1104) and len(p) >= 16:
            c = coord(p, 0)
            w = i32(p, 8)
            h = i32(p, 12)
            if rec.tag == 1000:
                return ellipse_path(c, (w / 2, 0), (0, h / 2))
            return rectangle_quickshape_path(c, (w / 2, 0), (0, h / 2))
        if rec.tag in (1001, 1108, 1112) and len(p) >= 24:
            c = coord(p, 0)
            major = coord(p, 8)
            minor = coord(p, 16)
            if rec.tag == 1001:
                return ellipse_path(c, major, minor)
            return rectangle_quickshape_path(c, major, minor)
        if rec.tag == 1110 and len(p) >= 40:
            c = coord(p, 0)
            major = coord(p, 8)
            minor = coord(p, 16)
            return translate_path(
                regular_shape_polygon_path(4, major, minor, True, f64(p, 24), f64(p, 32), 0.0, 0.0),
                c[0],
                c[1],
            )
        if rec.tag == 1200 and len(p) >= 26:
            sides = u16(p, 0)
            c = coord(p, 2)
            major = coord(p, 10)
            minor = coord(p, 18)
            return polygon_path(sides, c, major, minor)
        if rec.tag == 1212 and len(p) >= 42:
            sides = u16(p, 0)
            c = coord(p, 2)
            major = coord(p, 10)
            minor = coord(p, 18)
            return translate_path(
                regular_shape_polygon_path(sides, major, minor, True, f64(p, 26), f64(p, 34), 0.0, 0.0),
                c[0],
                c[1],
            )
        if rec.tag == 1216 and len(p) >= 58:
            sides = u16(p, 0)
            c = coord(p, 2)
            major = coord(p, 10)
            minor = coord(p, 18)
            return translate_path(
                regular_shape_polygon_path(sides, major, minor, True, f64(p, 26), f64(p, 34), 0.0, 0.0),
                c[0],
                c[1],
            )
        if rec.tag == 1114 and len(p) >= 56:
            c = coord(p, 0)
            major = coord(p, 8)
            minor = coord(p, 16)
            return rectangle_quickshape_path(c, major, minor)
        if rec.tag == 1901 and len(p) >= 75:
            return self._regular_shape_phase2_to_path(p)
        return []

    def _regular_shape_phase2_to_path(self, p: bytes) -> List[Tuple[str, Tuple[float, ...]]]:
        flags = p[0]
        sides = u16(p, 1)
        major = coord(p, 3)
        minor = coord(p, 11)
        matrix_off = 19
        a, b, c, d = (
            fixed16(p, matrix_off),
            fixed16(p, matrix_off + 4),
            fixed16(p, matrix_off + 8),
            fixed16(p, matrix_off + 12),
        )
        e, f = i32(p, matrix_off + 16), i32(p, matrix_off + 20)
        is_circular = bool(flags & 0x01)
        is_stellated = bool(flags & 0x02)
        has_primary_curvature = bool(flags & 0x04)
        has_stellation_curvature = bool(flags & 0x08)
        edge1 = None
        edge2 = None
        if len(p) > 75:
            edge1, off = self._parse_embedded_absolute_path(p, 75)
            edge2, off = self._parse_embedded_absolute_path(p, off)
            if off != len(p):
                raise XaraError("regular shape phase 2 has trailing edge-path bytes")
        if is_circular:
            base = ellipse_path((0, 0), major, minor)
        else:
            base = regular_shape_polygon_path(
                sides,
                major,
                minor,
                is_stellated,
                f64(p, 43) if len(p) >= 51 else 0.5,
                f64(p, 51) if len(p) >= 59 else 0.0,
                f64(p, 59) if len(p) >= 67 and has_primary_curvature else 0.0,
                f64(p, 67) if len(p) >= 75 and has_stellation_curvature else 0.0,
                edge1,
                edge2,
            )
        return transform_path(base, a, b, c, d, e, f)

    def _render_bitmap_node(self, rec: Record, ctx: Context) -> None:
        p = rec.payload
        if len(p) != 36:
            return
        tl = coord(p, 0)
        tr = coord(p, 8)
        br = coord(p, 16)
        bl = coord(p, 24)
        tl, tr, br, bl = self._warp_points((tl, tr, br, bl))
        bitmap_ref = i32(p, 32)
        bitmap = self.bitmaps.get(bitmap_ref)
        if not bitmap:
            return
        href = f"data:{bitmap.mime};base64,{base64.b64encode(bitmap.data).decode('ascii')}"
        a = tr[0] - tl[0]
        b = svg_y(tr[1] - tl[1])
        c = bl[0] - tl[0]
        d = svg_y(bl[1] - tl[1])
        e = tl[0]
        f = svg_y(tl[1])
        attrs = []
        if ctx.fill_opacity < 1:
            attrs.append(f'opacity="{fmt_num(ctx.fill_opacity)}"')
        mask_path = self._commands_to_svg_d(
            [
                ("M", (tl[0], tl[1])),
                ("L", (tr[0], tr[1])),
                ("L", (br[0], br[1])),
                ("L", (bl[0], bl[1])),
                ("Z", ()),
            ]
        )
        mask = self._fill_mask_attr_for_path(ctx, xml_attr(mask_path))
        if mask:
            attrs.append(mask)
        extra = (" " + " ".join(attrs)) if attrs else ""
        self.elements.append(
            '<image x="0" y="0" width="1" height="1" preserveAspectRatio="none" '
            f'transform="matrix({fmt_num(a)} {fmt_num(b)} {fmt_num(c)} {fmt_num(d)} {fmt_num(e)} {fmt_num(f)})" '
            f'href="{href}"{extra}/>'
        )

    def _render_text_story(self, node: Node, ctx: Context) -> None:
        rec = node.record
        anchor = (0, 0)
        transform = ""
        if rec.tag in (2100, 2110) and len(rec.payload) >= 8:
            anchor = coord(rec.payload, 0)
        elif rec.tag in (2101, 2114, 2117) and len(rec.payload) >= 24:
            a, b, c, d = fixed16(rec.payload, 0), fixed16(rec.payload, 4), fixed16(rec.payload, 8), fixed16(rec.payload, 12)
            e, f = i32(rec.payload, 16), i32(rec.payload, 20)
            transform = (
                f' transform="matrix({fmt_num(a)} {fmt_num(-b)} '
                f'{fmt_num(-c)} {fmt_num(d)} {fmt_num(e)} {fmt_num(svg_y(f))})"'
            )
        lines: List[TextLine] = []
        current: List[TextRun] = []
        self._collect_text(node.children, copy.deepcopy(ctx), lines, current)
        if current:
            lines.append(TextLine(current))
        if not lines:
            return
        text_path = self._text_story_path(node)
        if text_path and len(lines) == 1:
            self._render_text_path(lines[0], text_path, transform, ctx)
            return
        story_width = self._story_wrap_width(node)
        tspans = []
        yoff = 0
        for idx, line in enumerate(lines):
            line_ctx = self._line_context(line, ctx)
            nonempty_runs = [run for run in line.runs if run.text]
            use_text_length = line.width > 0 and len(nonempty_runs) == 1
            if idx == 0:
                dy = max(0, -line.offset)
            else:
                if line.offset:
                    dy = -line.offset
                else:
                    previous = lines[idx - 1]
                    previous_size = max((run.ctx.font_size for run in previous.runs), default=ctx.font_size)
                    dy = previous_size * 1.2
            yoff += dy
            source_y = anchor[1] - yoff
            line_x = self._repelled_line_x(anchor[0], source_y, story_width, line_ctx)
            first = True
            for run in line.runs:
                if not run.text:
                    continue
                attrs = self._text_run_attrs(run.ctx)
                if first:
                    attrs.insert(0, f'x="{fmt_num(line_x)}"')
                    attrs.insert(1, f'y="{fmt_num(svg_y(anchor[1]) + yoff)}"')
                    if run.ctx.text_anchor != "start":
                        attrs.append(f'text-anchor="{run.ctx.text_anchor}"')
                    if use_text_length:
                        attrs.append(f'textLength="{fmt_num(line.width)}"')
                        attrs.append('lengthAdjust="spacingAndGlyphs"')
                    first = False
                tspans.append(f'<tspan {" ".join(attrs)}>{html.escape(run.text)}</tspan>')
            if first:
                attrs = [f'x="{fmt_num(line_x)}"', f'y="{fmt_num(svg_y(anchor[1]) + yoff)}"']
                if line_ctx.text_anchor != "start":
                    attrs.append(f'text-anchor="{line_ctx.text_anchor}"')
                tspans.append(
                    f'<tspan {" ".join(attrs)}></tspan>'
                )
        style = []
        style.append('xml:space="preserve"')
        style_attr = " " + " ".join(style) if style else ""
        self.elements.append(f'<text{transform}{style_attr}>' + "".join(tspans) + "</text>")

    def _text_story_path(self, node: Node) -> Optional[List[Tuple[str, Tuple[float, ...]]]]:
        for child in node.children:
            if child.record.tag in self.PATH_TAGS:
                path = self._parse_path(child.record)
                if path:
                    return path
        return None

    def _render_text_path(
        self,
        line: TextLine,
        path: List[Tuple[str, Tuple[float, ...]]],
        transform: str,
        fallback: Context,
    ) -> None:
        pid = self._new_def_id("textpath")
        self.defs.append(f'<path id="{pid}" d="{xml_attr(self._commands_to_svg_d(path))}"/>')
        line_ctx = self._line_context(line, fallback)
        start_offset = {"start": "0%", "middle": "50%", "end": "100%"}.get(line_ctx.text_anchor, "0%")
        path_attrs = [f'href="#{pid}"', f'startOffset="{start_offset}"']
        if line_ctx.text_anchor != "start":
            path_attrs.append(f'text-anchor="{line_ctx.text_anchor}"')
        tspans = []
        for run in line.runs:
            if not run.text:
                continue
            tspans.append(f'<tspan {" ".join(self._text_run_attrs(run.ctx))}>{html.escape(run.text)}</tspan>')
        self.elements.append(
            f'<text{transform} xml:space="preserve"><textPath {" ".join(path_attrs)}>'
            + "".join(tspans)
            + "</textPath></text>"
        )

    @staticmethod
    def _line_context(line: TextLine, fallback: Context) -> Context:
        for run in line.runs:
            if run.text:
                return run.ctx
        return fallback

    @staticmethod
    def _story_wrap_width(node: Node) -> int:
        for child in node.children:
            if child.record.tag == 2150 and len(child.record.payload) >= 4:
                return max(0, i32(child.record.payload, 0))
        return 0

    def _repelled_line_x(self, x: float, y: float, width: int, ctx: Context) -> float:
        if width <= 0 or ctx.text_anchor != "start":
            return x
        line_left = x
        line_right = x + width
        shifted = x
        pad = max(3000.0, ctx.font_size * 0.6)
        for min_x, min_y, max_x, max_y in self.bitmap_boxes:
            if y < min_y - pad or y > max_y + pad:
                continue
            if max_x <= line_left or min_x >= line_right:
                continue
            shifted = max(shifted, max_x + pad)
        return shifted

    def _text_run_attrs(self, ctx: Context) -> List[str]:
        fill = ctx.fill.color if ctx.fill.kind == "solid" and ctx.fill.color else self._fill_paint(ctx.fill, ctx.fill_effect)
        if fill == "none":
            fill = "#000000"
        attrs = [
            f'font-family="{xml_attr(ctx.font_family)}"',
            f'font-size="{ctx.font_size}"',
            f'fill="{fill}"',
        ]
        if ctx.bold:
            attrs.append('font-weight="700"')
        if ctx.italic:
            attrs.append('font-style="italic"')
        if ctx.fill_opacity < 1:
            attrs.append(f'fill-opacity="{fmt_num(ctx.fill_opacity)}"')
        if ctx.tracking:
            attrs.append(f'letter-spacing="{fmt_num(ctx.tracking)}"')
        if ctx.font_baseline:
            attrs.append(f'baseline-shift="{fmt_num(ctx.font_baseline)}"')
        return attrs

    def _append_text_run(self, current: List[TextRun], text: str, ctx: Context) -> None:
        if not text:
            return
        if current and current[-1].ctx == ctx:
            current[-1].text += text
        else:
            current.append(TextRun(text, copy.deepcopy(ctx)))

    def _collect_text(
        self,
        nodes: Sequence[Node],
        ctx: Context,
        lines: List[TextLine],
        current: List[TextRun],
    ) -> None:
        for node in nodes:
            rec = node.record
            if rec.tag == 2200:
                if current:
                    lines.append(TextLine(current[:]))
                    current.clear()
                line_current: List[TextRun] = []
                self._collect_inline_text(node.children, copy.deepcopy(ctx), line_current)
                if line_current or any(child.record.tag in (2203, 2206) for child in node.children):
                    width, height, offset = self._line_info(node)
                    lines.append(TextLine(line_current, offset=offset, width=width, height=height))
                continue
            if rec.tag in self.ATTR_TAGS:
                self._apply_attr(rec, ctx)
            elif rec.tag == 2201:
                self._append_text_run(current, rec.payload.decode("utf-16le", errors="replace"), self._run_context(node, ctx))
            elif rec.tag == 2202 and len(rec.payload) == 2:
                self._append_text_run(current, chr(u16(rec.payload, 0)), self._run_context(node, ctx))
            elif rec.tag == 2203:
                lines.append(TextLine(current[:]))
                current.clear()
            elif rec.tag == 4200:
                self._append_text_run(current, "\xa0" * 4, ctx)
            if node.children:
                self._collect_text(node.children, copy.deepcopy(ctx), lines, current)

    def _collect_inline_text(self, nodes: Sequence[Node], ctx: Context, current: List[TextRun]) -> None:
        for node in nodes:
            rec = node.record
            if rec.tag == 2206:
                continue
            if rec.tag in self.ATTR_TAGS:
                self._apply_attr(rec, ctx)
            elif rec.tag == 2201:
                self._append_text_run(current, rec.payload.decode("utf-16le", errors="replace"), self._run_context(node, ctx))
                continue
            elif rec.tag == 2202 and len(rec.payload) == 2:
                self._append_text_run(current, chr(u16(rec.payload, 0)), self._run_context(node, ctx))
                continue
            elif rec.tag == 4200:
                self._append_text_run(current, "\xa0" * 4, ctx)
                continue
            elif rec.tag == 2203:
                continue
            if node.children:
                self._collect_inline_text(node.children, copy.deepcopy(ctx), current)

    def _run_context(self, node: Node, ctx: Context) -> Context:
        run_ctx = copy.deepcopy(ctx)
        for child in node.children:
            if child.record.tag in self.ATTR_TAGS:
                self._apply_attr(child.record, run_ctx)
        return run_ctx

    @staticmethod
    def _line_info(node: Node) -> Tuple[int, int, int]:
        for child in node.children:
            if child.record.tag == 2206 and len(child.record.payload) >= 12:
                return (
                    max(0, i32(child.record.payload, 0)),
                    max(0, i32(child.record.payload, 4)),
                    i32(child.record.payload, 8),
                )
        return (0, 0, 0)

    def _render_preview_fallback(self) -> None:
        if not self.preview:
            return
        w, h = gif_size(self.preview)
        self.viewbox = (0.0, 0.0, float(w), float(h))
        href = f"data:{self.preview_mime};base64,{base64.b64encode(self.preview).decode('ascii')}"
        self.elements.append(
            f'<image x="0" y="0" width="{fmt_num(w)}" height="{fmt_num(h)}" href="{href}"/>'
        )


def ellipse_path(
    center: Tuple[float, float], major: Tuple[float, float], minor: Tuple[float, float]
) -> List[Tuple[str, Tuple[float, ...]]]:
    cx, cy = center
    ax, ay = major
    bx, by = minor
    k = 0.5522847498307936
    p0 = (cx + ax, cy + ay)
    p1 = (cx + bx, cy + by)
    p2 = (cx - ax, cy - ay)
    p3 = (cx - bx, cy - by)
    return [
        ("M", p0),
        ("C", (p0[0] + k * bx, p0[1] + k * by, p1[0] + k * ax, p1[1] + k * ay, p1[0], p1[1])),
        ("C", (p1[0] - k * ax, p1[1] - k * ay, p2[0] + k * bx, p2[1] + k * by, p2[0], p2[1])),
        ("C", (p2[0] - k * bx, p2[1] - k * by, p3[0] - k * ax, p3[1] - k * ay, p3[0], p3[1])),
        ("C", (p3[0] + k * ax, p3[1] + k * ay, p0[0] - k * bx, p0[1] - k * by, p0[0], p0[1])),
        ("Z", ()),
    ]


def rect_path(
    center: Tuple[float, float], major: Tuple[float, float], minor: Tuple[float, float]
) -> List[Tuple[str, Tuple[float, ...]]]:
    cx, cy = center
    ax, ay = major
    bx, by = minor
    pts = [
        (cx - ax - bx, cy - ay - by),
        (cx + ax - bx, cy + ay - by),
        (cx + ax + bx, cy + ay + by),
        (cx - ax + bx, cy - ay + by),
    ]
    return [("M", pts[0]), ("L", pts[1]), ("L", pts[2]), ("L", pts[3]), ("Z", ())]


def rectangle_quickshape_path(
    center: Tuple[float, float], major: Tuple[float, float], minor: Tuple[float, float]
) -> List[Tuple[str, Tuple[float, ...]]]:
    scale = 1.0 / math.sqrt(2.0)
    return rect_path(
        center,
        (major[0] * scale, major[1] * scale),
        (minor[0] * scale, minor[1] * scale),
    )


def is_straight_regular_shape_edge(commands: Sequence[Tuple[str, Tuple[float, ...]]]) -> bool:
    return len(commands) == 2 and commands[0][0] == "M" and commands[1][0] == "L"


def custom_regular_shape_edge_path(
    vertices: Sequence[Tuple[Tuple[float, float], str]],
    is_stellated: bool,
    edge1: Sequence[Tuple[str, Tuple[float, ...]]],
    edge2: Sequence[Tuple[str, Tuple[float, ...]]],
) -> List[Tuple[str, Tuple[float, ...]]]:
    if not vertices:
        return []
    out: List[Tuple[str, Tuple[float, ...]]] = [("M", vertices[0][0])]
    for idx in range(len(vertices)):
        start = vertices[idx][0]
        end = vertices[(idx + 1) % len(vertices)][0]
        edge = edge2 if is_stellated and vertices[(idx + 1) % len(vertices)][1] == "primary" else edge1
        out.extend(transform_regular_shape_edge(edge, start, end))
    out.append(("Z", ()))
    return out


def transform_regular_shape_edge(
    edge: Sequence[Tuple[str, Tuple[float, ...]]],
    start: Tuple[float, float],
    end: Tuple[float, float],
) -> List[Tuple[str, Tuple[float, ...]]]:
    if is_straight_regular_shape_edge(edge):
        return [("L", end)]
    if len(edge) != 2 or edge[0][0] != "M" or edge[1][0] != "C":
        raise XaraError("unsupported regular shape edge template")
    edge_start = (edge[0][1][0], edge[0][1][1])
    vals = edge[1][1]
    edge_cp1 = (vals[0], vals[1])
    edge_cp2 = (vals[2], vals[3])
    edge_end = (vals[4], vals[5])
    source_len = math.hypot(edge_end[0] - edge_start[0], edge_end[1] - edge_start[1])
    target_len = math.hypot(end[0] - start[0], end[1] - start[1])
    if source_len <= 0.0 or target_len <= 0.0:
        return [("C", (start[0], start[1], end[0], end[1], end[0], end[1]))]
    scale = target_len / source_len
    edge_angle = math.atan2(edge_end[1] - edge_start[1], edge_end[0] - edge_start[0])
    target_angle = math.atan2(end[1] - start[1], end[0] - start[0])
    theta = target_angle - edge_angle
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)

    def tx_delta(pt: Tuple[float, float]) -> Tuple[float, float]:
        dx = pt[0] - edge_start[0]
        dy = pt[1] - edge_start[1]
        return (
            start[0] + scale * (dx * cos_t - dy * sin_t),
            start[1] + scale * (dx * sin_t + dy * cos_t),
        )

    cp1 = tx_delta(edge_cp1)
    cp2 = tx_delta(edge_cp2)
    return [("C", (*cp1, *cp2, *end))]


def regular_shape_polygon_path(
    sides: int,
    major: Tuple[float, float],
    minor: Tuple[float, float],
    is_stellated: bool,
    stellation_radius_ratio: float,
    stellation_offset_ratio: float,
    primary_curve_ratio: float,
    stellation_curve_ratio: float,
    edge1: Optional[Sequence[Tuple[str, Tuple[float, ...]]]] = None,
    edge2: Optional[Sequence[Tuple[str, Tuple[float, ...]]]] = None,
) -> List[Tuple[str, Tuple[float, ...]]]:
    if sides < 3 or sides > 99:
        return []
    ax, ay = major
    bx, by = minor
    angle_inc = 2.0 * math.pi / sides
    primary_radius = 0.5
    stellation_radius = primary_radius * stellation_radius_ratio if is_stellated else primary_radius
    if stellation_radius > primary_radius:
        scale = primary_radius / stellation_radius
        primary_radius *= scale
        stellation_radius *= scale

    def point_at(radius: float, theta: float) -> Tuple[float, float]:
        # Xara maps the normalized quickshape square onto the major/minor-axis parallelogram.
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        return (
            2.0 * radius * (cos_t * ax - sin_t * bx),
            2.0 * radius * (cos_t * ay - sin_t * by),
        )

    vertices: List[Tuple[Tuple[float, float], str]] = []
    for side in range(sides):
        theta = math.pi / sides + side * angle_inc
        vertices.append((point_at(primary_radius, theta), "primary"))
        if is_stellated:
            vertices.append(
                (
                    point_at(stellation_radius, theta + angle_inc / 2.0 + stellation_offset_ratio * angle_inc),
                    "stellation",
                )
            )

    desired_curve_lengths: List[float] = []
    major_len = math.hypot(ax, ay) * max(1.0, stellation_radius_ratio if is_stellated else 1.0)
    for _pt, kind in vertices:
        if kind == "primary":
            desired_curve_lengths.append(max(0.0, major_len * primary_curve_ratio))
        else:
            desired_curve_lengths.append(max(0.0, major_len * stellation_curve_ratio))

    if (
        edge1
        and edge2
        and (
            not is_straight_regular_shape_edge(edge1)
            or (is_stellated and not is_straight_regular_shape_edge(edge2))
        )
    ):
        if any(length > 0.0 for length in desired_curve_lengths):
            raise XaraError("unsupported curved regular shape edge path with vertex curvature")
        return custom_regular_shape_edge_path(vertices, is_stellated, edge1, edge2)

    if not any(length > 0.0 for length in desired_curve_lengths):
        out = [("M", vertices[0][0])]
        out.extend(("L", pt) for pt, _kind in vertices[1:])
        out.append(("Z", ()))
        return out

    def lerp(a: Tuple[float, float], b: Tuple[float, float], t: float) -> Tuple[float, float]:
        return a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t

    count = len(vertices)
    edge_out: List[Tuple[float, float]] = [vertices[i][0] for i in range(count)]
    edge_in_next: List[Tuple[float, float]] = [vertices[(i + 1) % count][0] for i in range(count)]
    for idx in range(count):
        next_idx = (idx + 1) % count
        start = vertices[idx][0]
        end = vertices[next_idx][0]
        dist = math.hypot(end[0] - start[0], end[1] - start[1])
        if dist < 1.0:
            continue
        start_len = desired_curve_lengths[idx]
        end_len = desired_curve_lengths[next_idx]
        total = start_len + end_len
        scale = min(1.0, dist / total) if total > 0.0 else 1.0
        edge_out[idx] = lerp(start, end, (start_len * scale) / dist)
        edge_in_next[idx] = lerp(end, start, (end_len * scale) / dist)

    out = [("M", edge_out[0] if desired_curve_lengths[0] > 0.0 else vertices[0][0])]
    for idx in range(count):
        next_idx = (idx + 1) % count
        next_vertex = vertices[next_idx][0]
        if desired_curve_lengths[next_idx] > 0.0:
            curve_start = edge_in_next[idx]
            curve_end = edge_out[next_idx]
            out.append(("L", curve_start))
            out.append(
                (
                    "C",
                    (
                        *lerp(curve_start, next_vertex, 0.552),
                        *lerp(curve_end, next_vertex, 0.552),
                        *curve_end,
                    ),
                )
            )
        else:
            out.append(("L", next_vertex))
    out.append(("Z", ()))
    return out


def polygon_path(
    sides: int,
    center: Tuple[float, float],
    major: Tuple[float, float],
    minor: Tuple[float, float],
    stellation_radius: Optional[float] = None,
    stellation_offset: float = 0.0,
) -> List[Tuple[str, Tuple[float, ...]]]:
    if sides < 3 or sides > 99:
        return []
    cx, cy = center
    ax, ay = major
    bx, by = minor
    start = math.pi / sides
    pts = []
    for i in range(sides):
        theta = start + i * 2 * math.pi / sides
        pts.append((cx + math.cos(theta) * ax + math.sin(theta) * bx, cy + math.cos(theta) * ay + math.sin(theta) * by))
        if stellation_radius is not None and stellation_radius > 0:
            inner = theta + math.pi / sides + stellation_offset
            pts.append(
                (
                    cx
                    + stellation_radius * (math.cos(inner) * ax + math.sin(inner) * bx),
                    cy
                    + stellation_radius * (math.cos(inner) * ay + math.sin(inner) * by),
                )
            )
    out = [("M", pts[0])]
    out.extend(("L", pt) for pt in pts[1:])
    out.append(("Z", ()))
    return out


def transform_path(
    commands: Sequence[Tuple[str, Tuple[float, ...]]],
    a: float,
    b: float,
    c: float,
    d: float,
    e: float,
    f: float,
) -> List[Tuple[str, Tuple[float, ...]]]:
    def tx(x: float, y: float) -> Tuple[float, float]:
        return a * x + c * y + e, b * x + d * y + f

    out: List[Tuple[str, Tuple[float, ...]]] = []
    for cmd, vals in commands:
        if cmd in ("M", "L"):
            out.append((cmd, tx(vals[0], vals[1])))
        elif cmd == "C":
            p1 = tx(vals[0], vals[1])
            p2 = tx(vals[2], vals[3])
            p3 = tx(vals[4], vals[5])
            out.append(("C", p1 + p2 + p3))
        else:
            out.append((cmd, vals))
    return out


def solve_linear_system(matrix: List[List[float]], vector: List[float]) -> Optional[List[float]]:
    n = len(vector)
    rows = [matrix[i][:] + [vector[i]] for i in range(n)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(rows[row][col]))
        if abs(rows[pivot][col]) < 1e-12:
            return None
        rows[col], rows[pivot] = rows[pivot], rows[col]
        div = rows[col][col]
        for j in range(col, n + 1):
            rows[col][j] /= div
        for row in range(n):
            if row == col:
                continue
            factor = rows[row][col]
            if abs(factor) < 1e-18:
                continue
            for j in range(col, n + 1):
                rows[row][j] -= factor * rows[col][j]
    return [rows[i][n] for i in range(n)]


def projective_transform_from_unit_square(
    corners: Sequence[Tuple[float, float]]
) -> Optional[Tuple[float, float, float, float, float, float, float, float]]:
    if len(corners) != 4:
        return None
    sources = ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0))
    matrix: List[List[float]] = []
    vector: List[float] = []
    for (u, v), (x, y) in zip(sources, corners):
        matrix.append([u, v, 1.0, 0.0, 0.0, 0.0, -x * u, -x * v])
        vector.append(x)
        matrix.append([0.0, 0.0, 0.0, u, v, 1.0, -y * u, -y * v])
        vector.append(y)
    solved = solve_linear_system(matrix, vector)
    if solved is None:
        return None
    return tuple(solved)  # type: ignore[return-value]


def apply_projective_transform(
    coeffs: Tuple[float, float, float, float, float, float, float, float],
    u: float,
    v: float,
) -> Tuple[float, float]:
    a, b, c, d, e, f, g, h = coeffs
    denom = g * u + h * v + 1.0
    if abs(denom) < 1e-12:
        denom = 1e-12 if denom >= 0 else -1e-12
    return (a * u + b * v + c) / denom, (d * u + e * v + f) / denom


def translate_path(
    commands: Sequence[Tuple[str, Tuple[float, ...]]], dx: float, dy: float
) -> List[Tuple[str, Tuple[float, ...]]]:
    out = []
    for cmd, vals in commands:
        if cmd in ("M", "L"):
            out.append((cmd, (vals[0] + dx, vals[1] + dy)))
        elif cmd == "C":
            out.append(
                (
                    cmd,
                    (
                        vals[0] + dx,
                        vals[1] + dy,
                        vals[2] + dx,
                        vals[3] + dy,
                        vals[4] + dx,
                        vals[5] + dy,
                    ),
                )
            )
        else:
            out.append((cmd, vals))
    return out


def path_bounds(commands: Sequence[Tuple[str, Tuple[float, ...]]]) -> Optional[Tuple[float, float, float, float]]:
    xs: List[float] = []
    ys: List[float] = []
    for _cmd, vals in commands:
        for idx, value in enumerate(vals):
            if idx % 2:
                ys.append(value)
            else:
                xs.append(value)
    if not xs or not ys:
        return None
    return min(xs), min(ys), max(xs), max(ys)


def interpolate_path(
    start: Sequence[Tuple[str, Tuple[float, ...]]],
    end: Sequence[Tuple[str, Tuple[float, ...]]],
    t: float,
) -> Optional[List[Tuple[str, Tuple[float, ...]]]]:
    if len(start) != len(end):
        return None
    out: List[Tuple[str, Tuple[float, ...]]] = []
    for (cmd_a, vals_a), (cmd_b, vals_b) in zip(start, end):
        if cmd_a != cmd_b or len(vals_a) != len(vals_b):
            return None
        if cmd_a == "Z":
            out.append((cmd_a, ()))
        else:
            out.append((cmd_a, tuple(a + (b - a) * t for a, b in zip(vals_a, vals_b))))
    return out


def path_to_polyline(
    commands: Sequence[Tuple[str, Tuple[float, ...]]], curve_steps: int = 10
) -> Tuple[List[Tuple[float, float]], bool]:
    points: List[Tuple[float, float]] = []
    current: Optional[Tuple[float, float]] = None
    subpath_start: Optional[Tuple[float, float]] = None
    closed = False
    for cmd, vals in commands:
        if cmd == "M" and len(vals) >= 2:
            current = (vals[0], vals[1])
            subpath_start = current
            points.append(current)
        elif cmd == "L" and len(vals) >= 2:
            current = (vals[0], vals[1])
            points.append(current)
        elif cmd == "C" and len(vals) >= 6 and current is not None:
            p0 = current
            p1 = (vals[0], vals[1])
            p2 = (vals[2], vals[3])
            p3 = (vals[4], vals[5])
            for idx in range(1, curve_steps + 1):
                u = idx / curve_steps
                inv = 1.0 - u
                x = inv**3 * p0[0] + 3 * inv**2 * u * p1[0] + 3 * inv * u**2 * p2[0] + u**3 * p3[0]
                y = inv**3 * p0[1] + 3 * inv**2 * u * p1[1] + 3 * inv * u**2 * p2[1] + u**3 * p3[1]
                points.append((x, y))
            current = p3
        elif cmd == "Z" and subpath_start is not None:
            closed = True
            if points and points[-1] != subpath_start:
                points.append(subpath_start)
            current = subpath_start
    return points, closed


def resample_polyline(points: Sequence[Tuple[float, float]], count: int, closed: bool) -> List[Tuple[float, float]]:
    if not points:
        return []
    if len(points) == 1:
        return [points[0]] * count
    pts = list(points)
    if closed and pts[0] != pts[-1]:
        pts.append(pts[0])
    lengths = [0.0]
    for a, b in zip(pts, pts[1:]):
        lengths.append(lengths[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    total = lengths[-1]
    if total <= 1e-9:
        return [pts[0]] * count
    out: List[Tuple[float, float]] = []
    denom = count if closed else max(1, count - 1)
    seg = 0
    for idx in range(count):
        target = total * idx / denom
        if closed and idx == count - 1:
            target = total * (count - 1) / count
        while seg + 1 < len(lengths) and lengths[seg + 1] < target:
            seg += 1
        if seg + 1 >= len(pts):
            out.append(pts[-1])
            continue
        span = lengths[seg + 1] - lengths[seg]
        u = 0.0 if span <= 1e-9 else (target - lengths[seg]) / span
        a = pts[seg]
        b = pts[seg + 1]
        out.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u))
    return out


def interpolate_sampled_path(
    start: Sequence[Tuple[str, Tuple[float, ...]]],
    end: Sequence[Tuple[str, Tuple[float, ...]]],
    t: float,
) -> Optional[List[Tuple[str, Tuple[float, ...]]]]:
    points_a, closed_a = path_to_polyline(start)
    points_b, closed_b = path_to_polyline(end)
    if len(points_a) < 2 or len(points_b) < 2:
        return None
    count = max(16, min(256, max(len(points_a), len(points_b)) * 2))
    closed = closed_a and closed_b
    a = resample_polyline(points_a, count, closed)
    b = resample_polyline(points_b, count, closed)
    if len(a) != len(b) or not a:
        return None
    mixed = [(pa[0] + (pb[0] - pa[0]) * t, pa[1] + (pb[1] - pa[1]) * t) for pa, pb in zip(a, b)]
    out: List[Tuple[str, Tuple[float, ...]]] = [("M", mixed[0])]
    out.extend(("L", pt) for pt in mixed[1:])
    if closed:
        out.append(("Z", ()))
    return out


def parse_hex_color(value: Optional[str]) -> Optional[Tuple[int, int, int]]:
    if not value or not value.startswith("#") or len(value) != 7:
        return None
    try:
        return int(value[1:3], 16), int(value[3:5], 16), int(value[5:7], 16)
    except ValueError:
        return None


def blend_hex_color(a: Optional[str], b: Optional[str], t: float) -> Optional[str]:
    ca = parse_hex_color(a)
    cb = parse_hex_color(b)
    if ca is None or cb is None:
        return a if t < 0.5 else b
    rgb = tuple(round(x + (y - x) * t) for x, y in zip(ca, cb))
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def blend_fill_effect_color(a: Optional[str], b: Optional[str], t: float, fill_effect: str) -> Optional[str]:
    ca = parse_hex_color(a)
    cb = parse_hex_color(b)
    if ca is None or cb is None:
        return blend_hex_color(a, b, t)
    if fill_effect not in ("rainbow", "alt-rainbow"):
        return blend_hex_color(a, b, t)
    rgb = rainbow_rgb_at(ca, cb, t, fill_effect == "alt-rainbow")
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def rainbow_color_ramp(a: str, b: str, use_long_hue_route: bool, steps: int) -> List[str]:
    ca = parse_hex_color(a)
    cb = parse_hex_color(b)
    if ca is None or cb is None or steps < 2:
        return []
    return [
        f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        for rgb in (rainbow_rgb_at(ca, cb, idx / (steps - 1), use_long_hue_route) for idx in range(steps))
    ]


def rainbow_rgb_at(
    ca: Tuple[int, int, int], cb: Tuple[int, int, int], t: float, use_long_hue_route: bool
) -> Tuple[int, int, int]:
    h0, s0, v0 = colorsys.rgb_to_hsv(ca[0] / 255.0, ca[1] / 255.0, ca[2] / 255.0)
    h1, s1, v1 = colorsys.rgb_to_hsv(cb[0] / 255.0, cb[1] / 255.0, cb[2] / 255.0)
    if s0 <= 1e-9 or s1 <= 1e-9:
        return tuple(round(x + (y - x) * t) for x, y in zip(ca, cb))
    delta = (h1 - h0) % 1.0
    if use_long_hue_route:
        if delta < 0.5:
            delta -= 1.0
    else:
        if delta > 0.5:
            delta -= 1.0
    h = (h0 + delta * t) % 1.0
    s = s0 + (s1 - s0) * t
    v = v0 + (v1 - v0) * t
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return round(r * 255), round(g * 255), round(b * 255)


def blend_fill(a: Fill, b: Fill, t: float) -> Fill:
    if a.kind == "solid" and b.kind == "solid":
        return Fill("solid", blend_hex_color(a.color, b.color, t))
    return copy.deepcopy(a if t < 0.5 else b)


def blend_context(a: Context, b: Context, t: float) -> Context:
    ctx = copy.deepcopy(a)
    ctx.fill = blend_fill(a.fill, b.fill, t)
    ctx.stroke = blend_hex_color(a.stroke, b.stroke, t)
    ctx.line_width = round(a.line_width + (b.line_width - a.line_width) * t)
    ctx.fill_opacity = a.fill_opacity + (b.fill_opacity - a.fill_opacity) * t
    ctx.stroke_opacity = a.stroke_opacity + (b.stroke_opacity - a.stroke_opacity) * t
    ctx.fill_effect = a.fill_effect if t < 0.5 else b.fill_effect
    return ctx


def gif_size(data: bytes) -> Tuple[int, int]:
    if len(data) >= 10 and data.startswith((b"GIF87a", b"GIF89a")):
        return u16(data, 6), u16(data, 8)
    return 128, 128


def convert(input_file: str, output_dir: str) -> None:
    if not os.path.isdir(output_dir):
        raise XaraError("output path must be an existing directory")
    data = open(input_file, "rb").read()
    parser = Parser(data)
    records = parser.parse()
    roots = build_tree(records)
    first_renderer = SvgRenderer(records, roots, 0)
    pages = first_renderer.pages
    rendered: List[Tuple[str, str]] = []
    used_names: Dict[str, int] = {}
    input_stem = Path(input_file).stem
    for idx, page in enumerate(pages):
        renderer = first_renderer if idx == 0 else SvgRenderer(records, roots, idx)
        svg = renderer.render()
        if len(pages) == 1 and not page.name:
            base = safe_filename(input_stem)
        else:
            base = safe_filename(page.name or f"page_{idx + 1}")
        count = used_names.get(base, 0)
        used_names[base] = count + 1
        if count:
            base = f"{base}_{count + 1}"
        rendered.append((base + ".svg", svg))
    tmp_paths = []
    try:
        for filename, svg in rendered:
            tmp = os.path.join(output_dir, filename + ".tmp")
            with open(tmp, "w", encoding="utf-8", newline="\n") as f:
                f.write(svg)
            os.chmod(tmp, 0o664)
            tmp_paths.append((tmp, os.path.join(output_dir, filename)))
        for tmp, final in tmp_paths:
            os.replace(tmp, final)
    finally:
        for tmp, _final in tmp_paths:
            if os.path.exists(tmp):
                os.unlink(tmp)


def main(argv: Sequence[str]) -> int:
    if len(argv) != 3:
        print("usage: xara.py <inputFile> <outputDirectory>", file=sys.stderr)
        return 2
    try:
        convert(argv[1], argv[2])
    except Exception as exc:
        print(f"xara.py: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

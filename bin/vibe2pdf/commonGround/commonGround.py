#!/usr/bin/env python3
# Vibe coded by Codex
"""
Convert supported Common Ground Digital Paper samples to a direct PDF file.

This implementation strictly validates the discovered containers, then extracts
text drawing operators from CGDC and DPL2 display streams. It intentionally
refuses inputs whose container boundaries do not validate.
"""

from __future__ import annotations

import argparse
import binascii
import io
import math
import os
import re
import statistics
import struct
import subprocess
import sys
import tempfile
import zlib
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Callable

try:
    from PIL import Image, ImageFile, ImageFont
    ImageFile.LOAD_TRUNCATED_IMAGES = True
except ImportError:  # pragma: no cover - exercised only on systems without Pillow
    Image = None
    ImageFont = None

try:
    from fontTools.ttLib import TTFont
except ImportError:  # pragma: no cover - exercised only on systems without fontTools
    TTFont = None


class CommonGroundError(Exception):
    pass


PDF_BASE_FONTS = {
    "times": {
        0: ("FTimes", "Times-Roman"),
        1: ("FTimesBold", "Times-Bold"),
        2: ("FTimesItalic", "Times-Italic"),
        3: ("FTimesBoldItalic", "Times-BoldItalic"),
    },
    "helvetica": {
        0: ("FHelvetica", "Helvetica"),
        1: ("FHelveticaBold", "Helvetica-Bold"),
        2: ("FHelveticaOblique", "Helvetica-Oblique"),
        3: ("FHelveticaBoldOblique", "Helvetica-BoldOblique"),
    },
    "helvetica_narrow": {
        0: ("FNimbusNarrow", "Helvetica"),
        1: ("FNimbusNarrowBold", "Helvetica-Bold"),
        2: ("FNimbusNarrowOblique", "Helvetica-Oblique"),
        3: ("FNimbusNarrowBoldOblique", "Helvetica-BoldOblique"),
    },
    "futura": {
        0: ("FFuturaBook", "Helvetica"),
        1: ("FFuturaDemi", "Helvetica-Bold"),
        2: ("FFuturaBookOblique", "Helvetica-Oblique"),
        3: ("FFuturaDemiOblique", "Helvetica-BoldOblique"),
    },
    "berkeley": {
        0: ("FBerkeleyBook", "Times-Roman"),
        1: ("FBerkeleyDemi", "Times-Bold"),
        2: ("FBerkeleyBookItalic", "Times-Italic"),
        3: ("FBerkeleyDemiItalic", "Times-BoldItalic"),
    },
    "palatino": {
        0: ("FPalatino", "Times-Roman"),
        1: ("FPalatinoBold", "Times-Bold"),
        2: ("FPalatinoItalic", "Times-Italic"),
        3: ("FPalatinoBoldItalic", "Times-BoldItalic"),
    },
    "symbol": {
        0: ("FSymbol", "Symbol"),
        1: ("FSymbol", "Symbol"),
        2: ("FSymbol", "Symbol"),
        3: ("FSymbol", "Symbol"),
    },
}


PDF_FONT_PATHS = {
    "times": {
        0: ("FTimes", "/usr/share/fonts/corefonts/times.ttf", "Times-Roman"),
        1: ("FTimesBold", "/usr/share/fonts/corefonts/timesbd.ttf", "Times-Bold"),
        2: ("FTimesItalic", "/usr/share/fonts/corefonts/timesi.ttf", "Times-Italic"),
        3: ("FTimesBoldItalic", "/usr/share/fonts/corefonts/timesbi.ttf", "Times-BoldItalic"),
    },
    "helvetica": {
        0: ("FHelvetica", "/usr/share/fonts/corefonts/arial.ttf", "Helvetica"),
        1: ("FHelveticaBold", "/usr/share/fonts/corefonts/arialbd.ttf", "Helvetica-Bold"),
        2: ("FHelveticaOblique", "/usr/share/fonts/corefonts/ariali.ttf", "Helvetica-Oblique"),
        3: ("FHelveticaBoldOblique", "/usr/share/fonts/corefonts/arialbi.ttf", "Helvetica-BoldOblique"),
    },
    "helvetica_narrow": {
        0: ("FNimbusNarrow", "/usr/share/fonts/urw-fonts/NimbusSansNarrow-Regular.ttf", "Helvetica"),
        1: ("FNimbusNarrowBold", "/usr/share/fonts/urw-fonts/NimbusSansNarrow-Bold.ttf", "Helvetica-Bold"),
        2: ("FNimbusNarrowOblique", "/usr/share/fonts/urw-fonts/NimbusSansNarrow-Oblique.ttf", "Helvetica-Oblique"),
        3: ("FNimbusNarrowBoldOblique", "/usr/share/fonts/urw-fonts/NimbusSansNarrow-BoldOblique.ttf", "Helvetica-BoldOblique"),
    },
    "futura": {
        0: ("FFuturaBook", "/usr/share/fonts/urw-fonts/URWGothic-Book.ttf", "Helvetica"),
        1: ("FFuturaDemi", "/usr/share/fonts/urw-fonts/URWGothic-Demi.ttf", "Helvetica-Bold"),
        2: ("FFuturaBookOblique", "/usr/share/fonts/urw-fonts/URWGothic-BookOblique.ttf", "Helvetica-Oblique"),
        3: ("FFuturaDemiOblique", "/usr/share/fonts/urw-fonts/URWGothic-DemiOblique.ttf", "Helvetica-BoldOblique"),
    },
    "berkeley": {
        0: ("FBerkeleyBook", "/usr/share/fonts/urw-fonts/URWBookman-Light.ttf", "Times-Roman"),
        1: ("FBerkeleyDemi", "/usr/share/fonts/urw-fonts/URWBookman-Demi.ttf", "Times-Bold"),
        2: ("FBerkeleyBookItalic", "/usr/share/fonts/urw-fonts/URWBookman-LightItalic.ttf", "Times-Italic"),
        3: ("FBerkeleyDemiItalic", "/usr/share/fonts/urw-fonts/URWBookman-DemiItalic.ttf", "Times-BoldItalic"),
    },
    "palatino": {
        0: ("FPalatino", "/usr/share/fonts/urw-fonts/P052-Roman.ttf", "Times-Roman"),
        1: ("FPalatinoBold", "/usr/share/fonts/urw-fonts/P052-Bold.ttf", "Times-Bold"),
        2: ("FPalatinoItalic", "/usr/share/fonts/urw-fonts/P052-Italic.ttf", "Times-Italic"),
        3: ("FPalatinoBoldItalic", "/usr/share/fonts/urw-fonts/P052-BoldItalic.ttf", "Times-BoldItalic"),
    },
    "symbol": {
        0: ("FSymbol", None, "Symbol"),
        1: ("FSymbol", None, "Symbol"),
        2: ("FSymbol", None, "Symbol"),
        3: ("FSymbol", None, "Symbol"),
    },
}

SYMBOL_TO_UNICODE = {
    0x20: 0x0020,
    0x34: 0x0034,
    0xB4: 0x00D7,
}

MATH_PI_SIX_TO_UNICODE = {
    0x20: " ",
    0x62: "\u25c0",
    0x63: "\u25b6",
}

FUTURA_BOOK_FRACTIONS_TO_UNICODE = {
    0x5E: "\u00bd",
    0xA3: "\u215b",
    0xB4: "\u00be",
    0xC4: "\u00bc",
    0xDB: "\u2154",
    0xE4: "\u2153",
}

@dataclass(frozen=True)
class PdfFontSpec:
    resource_name: str
    path: str | None
    base14_name: str


LOCAL_UNICODE_FONT_PATH = Path(__file__).resolve().parent / "assets" / "unifont_jp.ttf"
SYSTEM_UNICODE_FONT_PATH = Path("/usr/share/fonts/unifont/unifont_jp.otf")
UNICODE_FONT_SPEC = PdfFontSpec(
    "FUnicode",
    str(LOCAL_UNICODE_FONT_PATH if LOCAL_UNICODE_FONT_PATH.exists() else SYSTEM_UNICODE_FONT_PATH),
    "Unifont-JP",
)
UNICODE_GID_MAP: dict[int, int] | None = None


PDF_FONT_SPECS_BY_RESOURCE = {
    resource_name: PdfFontSpec(resource_name, path, base14_name)
    for family in PDF_FONT_PATHS.values()
    for resource_name, path, base14_name in family.values()
}


@dataclass(frozen=True)
class Payload:
    data: bytes
    wrapper: str
    note: str


@dataclass(frozen=True)
class Segment:
    kind: str
    body: bytes
    description: str
    trailer: bytes = b""


@dataclass(frozen=True)
class Dpl2ResourceRef:
    resource_type: str
    resource_id: int
    attributes: int
    data_offset: int
    data: bytes


@dataclass(frozen=True)
class Dpl2PageGraphEntry:
    page_id: int
    base_id: int | None
    bounds: tuple[float, float, float, float] | None
    cbts_refs: tuple[tuple[int, int, int], ...] = ()
    crct_refs: tuple[tuple[int, int, int], ...] = ()
    cpic_refs: tuple[tuple[int, int, int], ...] = ()
    cpic_ids: tuple[int, ...] = ()
    crct_ids: tuple[int, ...] = ()
    resource_refs: tuple[tuple[str, int], ...] = ()


@dataclass(frozen=True)
class PfrFontMetrics:
    font_id: str
    metrics_resolution: int
    outline_resolution: int
    bbox: tuple[int, int, int, int]
    advances: dict[int, int]
    glyph_programs: dict[int, tuple[int, int]]
    gps_section_offset: int
    pfr_data: bytes
    logical_size_half_points: int | None = None
    logical_index: int | None = None
    logical_physical_offset: int | None = None


@dataclass(frozen=True)
class PfrPathCommand:
    op: str
    points: tuple[tuple[float, float], ...] = ()


CURRENT_PFR_METRICS: dict[str, PfrFontMetrics] = {}
CURRENT_PFR_FONT_RESOURCES: dict[str, str] = {}
CURRENT_PFR_FONT_BY_RESOURCE: dict[str, PfrFontMetrics] = {}
CURRENT_PFR_STYLE_METRICS: dict[tuple[str, int], PfrFontMetrics] = {}
CURRENT_PFR_STYLE_FONT_RESOURCES: dict[tuple[str, int], str] = {}


@dataclass(frozen=True)
class StyleState:
    emphasis: int = 0
    size_half_points: int = 22
    color: tuple[int, int, int] | None = None
    background_color: tuple[int, int, int] | None = None
    superscript: bool = False
    font_id: int | None = None
    font_name: str | None = None
    tx_ratio: float = 1.0
    space_extra: float = 0.0
    char_extra: float = 0.0


@dataclass(frozen=True)
class TextRun:
    text: str
    style: StyleState


@dataclass(frozen=True)
class ImageRun:
    png: bytes
    width: int
    height: int
    width_twips: int
    height_twips: int
    x: int | None = None
    y: int | None = None
    offset: int | None = None


@dataclass(frozen=True)
class TextFragment:
    offset: int
    op: int
    data: bytes
    y: int | None = None
    x: int | None = None
    advance: int | None = None
    style: StyleState = field(default_factory=StyleState)
    image: ImageRun | None = None


@dataclass(frozen=True)
class PictPage:
    start: int
    end: int
    top: int | None = None
    left: int | None = None
    bottom: int | None = None
    right: int | None = None


@dataclass(frozen=True)
class PictClipRegion:
    bounds: tuple[int, int, int, int]
    runs: tuple[tuple[int, int, int, int], ...] = ()


@dataclass(frozen=True)
class PictTextEvent:
    offset: int
    x: float
    y: int
    text: str
    style: StyleState
    clip: PictClipRegion | None = None


@dataclass(frozen=True)
class PictImageEvent:
    offset: int
    image: ImageRun
    clip: PictClipRegion | None = None


@dataclass(frozen=True)
class PictVectorEvent:
    offset: int
    kind: str
    points: tuple[tuple[int, int], ...]
    filled: bool = False
    color: tuple[int, int, int] | None = None
    stroke_width: int = 1
    clip: PictClipRegion | None = None
    fill_pattern: bytes | None = None


@dataclass(frozen=True)
class Dpl2DisplayItem:
    events: tuple[PictTextEvent | PictImageEvent | PictVectorEvent, ...]
    bounds: tuple[float, float, float, float] | None = None
    collision_bounds: tuple[float, float, float, float] | None = None
    base_id: int | None = None
    base_variant: int | None = None
    page_id: int | None = None
    cpic_ids: tuple[int, ...] = ()
    crct_ids: tuple[int, ...] = ()
    break_before: bool = False


@dataclass
class PdfPage:
    width: float
    height: float
    commands: list[str] = field(default_factory=list)
    xobjects: dict[str, int] = field(default_factory=dict)
    fonts: set[str] = field(default_factory=set)
    patterns: dict[str, tuple[bytes, tuple[int, int, int], float]] = field(default_factory=dict)


@dataclass(frozen=True)
class VisualLine:
    text: str
    y: int | None
    x: int | None
    runs: tuple[TextRun, ...] = field(default_factory=tuple)
    images: tuple[ImageRun, ...] = field(default_factory=tuple)
    offset: int | None = None


def be32(data: bytes, offset: int) -> int:
    return struct.unpack_from(">I", data, offset)[0]


def be16(data: bytes, offset: int) -> int:
    return struct.unpack_from(">H", data, offset)[0]


def be16s(data: bytes, offset: int) -> int:
    return struct.unpack_from(">h", data, offset)[0]


def i8(data: bytes, offset: int) -> int:
    return struct.unpack_from("b", data, offset)[0]


def png_chunk(kind: bytes, payload: bytes) -> bytes:
    body = kind + payload
    return struct.pack(">I", len(payload)) + body + struct.pack(">I", binascii.crc32(body) & 0xFFFFFFFF)


def rgba_png(
    width: int,
    height: int,
    rows: list[bytes],
    color: tuple[int, int, int],
    background: tuple[int, int, int] | None = None,
) -> bytes:
    red, green, blue = color
    raw = bytearray()
    for row in rows:
        raw.append(0)
        for byte_index in range((width + 7) // 8):
            byte = row[byte_index] if byte_index < len(row) else 0
            for bit in range(7, -1, -1):
                pixel = byte & (1 << bit)
                x = byte_index * 8 + (7 - bit)
                if x >= width:
                    break
                if pixel:
                    raw.extend((red, green, blue, 255))
                elif background is not None:
                    bg_red, bg_green, bg_blue = background
                    raw.extend((bg_red, bg_green, bg_blue, 255))
                else:
                    raw.extend((255, 255, 255, 0))
    return (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
        + png_chunk(b"IDAT", zlib.compress(bytes(raw)))
        + png_chunk(b"IEND", b"")
    )


def indexed_png(width: int, height: int, rows: list[bytes], palette: dict[int, tuple[int, int, int]]) -> bytes:
    raw = bytearray()
    for row in rows:
        raw.append(0)
        for x in range(width):
            index = row[x] if x < len(row) else 0
            red, green, blue = palette.get(index, (index, index, index))
            raw.extend((red, green, blue, 255))
    return (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
        + png_chunk(b"IDAT", zlib.compress(bytes(raw)))
        + png_chunk(b"IEND", b"")
    )


def unpack_indexed_pixels(row: bytes, width: int, pixel_size: int) -> bytes | None:
    if pixel_size == 8:
        return row[:width]
    if pixel_size == 4:
        out = bytearray()
        for byte in row:
            out.append(byte >> 4)
            if len(out) >= width:
                break
            out.append(byte & 0x0F)
            if len(out) >= width:
                break
        if len(out) < width:
            return None
        return bytes(out)
    if pixel_size in (1, 2):
        out = bytearray()
        mask = (1 << pixel_size) - 1
        for byte in row:
            for shift in range(8 - pixel_size, -1, -pixel_size):
                out.append((byte >> shift) & mask)
                if len(out) >= width:
                    break
            if len(out) >= width:
                break
        if len(out) < width:
            return None
        return bytes(out)
    return None


def crop_1bit_rows(
    rows: list[bytes],
    crop_left: int,
    crop_top: int,
    crop_width: int,
    crop_height: int,
) -> list[bytes] | None:
    if crop_left < 0 or crop_top < 0 or crop_width <= 0 or crop_height <= 0:
        return None
    out_rows: list[bytes] = []
    for source_row in rows[crop_top : crop_top + crop_height]:
        out = bytearray((crop_width + 7) // 8)
        for x in range(crop_width):
            source_x = crop_left + x
            source_byte_index = source_x // 8
            if source_byte_index >= len(source_row):
                return None
            if source_row[source_byte_index] & (0x80 >> (source_x & 7)):
                out[x // 8] |= 0x80 >> (x & 7)
        out_rows.append(bytes(out))
    if len(out_rows) != crop_height:
        return None
    return out_rows


def padded128(n: int) -> int:
    return (n + 127) & ~127


def parse_macbinary(raw: bytes) -> Payload | None:
    if len(raw) < 128:
        return None
    name_len = raw[1]
    if raw[0] != 0 or not (1 <= name_len <= 63):
        return None
    if raw[74] != 0 or raw[82] != 0:
        return None
    file_type = raw[65:69]
    if file_type != b"CGDC":
        return None

    data_len = be32(raw, 83)
    resource_len = be32(raw, 87)
    data_start = 128
    resource_start = data_start + padded128(data_len)
    total = resource_start + padded128(resource_len)
    if data_len <= 0 or resource_start > len(raw) or total > len(raw):
        raise CommonGroundError("invalid MacBinary fork lengths")
    if raw[data_start + 8 : data_start + 12] not in (b"CGDC", b"DPL2"):
        raise CommonGroundError("MacBinary data fork is not a Common Ground stream")
    if any(raw[data_start + data_len : resource_start]):
        raise CommonGroundError("non-zero MacBinary data-fork padding")
    if any(raw[resource_start + resource_len : total]):
        raise CommonGroundError("non-zero MacBinary resource-fork padding")
    if any(raw[total:]):
        raise CommonGroundError("non-zero trailing bytes after MacBinary forks")

    name = raw[2 : 2 + name_len].decode("mac_roman", "replace")
    creator = raw[69:73].decode("latin1", "replace")
    return Payload(
        raw[data_start : data_start + data_len],
        "MacBinary",
        f"name={name!r}, type=CGDC, creator={creator!r}, data={data_len}, resource={resource_len}",
    )


def valid_cgdc_at(raw: bytes, offset: int) -> bool:
    if offset < 0 or offset + 16 > len(raw):
        return False
    if raw[offset + 8 : offset + 12] != b"CGDC":
        return False
    first = be32(raw, offset)
    second = be32(raw, offset + 4)
    return first > 0 and second >= 0 and first + second == len(raw) - offset


def valid_dpl2_at(raw: bytes, offset: int) -> bool:
    if offset < 0 or offset + 48 > len(raw):
        return False
    if raw[offset + 8 : offset + 12] != b"DPL2":
        return False
    outer_header = be32(raw, offset)
    inner_header = be32(raw, offset + 24)
    inner_total = be32(raw, offset + 28)
    inner_payload = be32(raw, offset + 32)
    trailer_len = be32(raw, offset + 36)
    return (
        outer_header == 24
        and inner_header == 24
        and inner_payload == inner_total - inner_header
        and offset + outer_header + inner_total + trailer_len == len(raw)
    )


def parse_payload(raw: bytes) -> Payload:
    mac = parse_macbinary(raw)
    if mac is not None:
        return mac

    if valid_cgdc_at(raw, 0) or valid_dpl2_at(raw, 0):
        return Payload(raw, "raw data fork", "stream starts at byte 0")

    candidates: list[int] = []
    for signature in (b"CGDC", b"DPL2"):
        search = 0
        while True:
            pos = raw.find(signature, search)
            if pos < 0:
                break
            start = pos - 8
            if valid_cgdc_at(raw, start) or valid_dpl2_at(raw, start):
                candidates.append(start)
            search = pos + 1

    candidates = sorted(set(candidates))
    if len(candidates) == 1:
        start = candidates[0]
        return Payload(raw[start:], "embedded payload", f"payload starts at byte 0x{start:x}")
    if candidates:
        raise CommonGroundError("ambiguous embedded Common Ground payloads")
    raise CommonGroundError("not a supported Common Ground CGDC/DPL2 payload")


def parse_segment(payload: bytes) -> Segment:
    sig = payload[8:12]
    if sig == b"CGDC":
        if not valid_cgdc_at(payload, 0):
            raise CommonGroundError("invalid CGDC length table")
        if be32(payload, 12) != 0:
            raise CommonGroundError("unsupported CGDC version/flags")
        body_len = be32(payload, 0)
        trailer_len = be32(payload, 4)
        return Segment("CGDC", payload[:body_len], f"body={body_len}, trailer={trailer_len}", payload[body_len:])

    if sig == b"DPL2":
        if not valid_dpl2_at(payload, 0):
            raise CommonGroundError("invalid DPL2 length table")
        flags = be32(payload, 12)
        if flags not in (0, 0x00000A00):
            raise CommonGroundError(f"unsupported DPL2 flags 0x{flags:08x}")
        inner_total = be32(payload, 28)
        trailer_len = be32(payload, 36)
        body_start = 48
        body_end = 24 + inner_total
        trailer = payload[body_end : body_end + trailer_len]
        return Segment("DPL2", payload[body_start:body_end], f"body={body_end - body_start}, trailer={trailer_len}", trailer)

    raise CommonGroundError("unsupported Common Ground signature")


def decode_dpl2_ascii(data: bytes) -> str:
    out = bytearray()
    i = 0
    while i < len(data):
        c = data[i]
        if 32 <= c <= 126 or c in (9, 10, 13):
            out.append(c)
            i += 1
            continue
        if c >= 0x80 and i + 1 < len(data) and 32 <= data[i + 1] <= 126:
            out.append(data[i + 1])
            i += 2
            continue
        i += 1
    return out.decode("ascii", "replace")


def decode_dpl2_glyph_run(data: bytes, start: int, glyph_count: int, limit: int) -> tuple[str, bytes, int] | None:
    """Decode one counted DPL2 glyph run from expanded display bytecode."""
    if glyph_count <= 0 or glyph_count > 240:
        return None
    end = start + glyph_count
    if start >= limit or end > limit:
        return None
    raw = data[start:end]
    if any(byte < 32 and byte not in (9, 10, 13) for byte in raw):
        return None
    return raw.decode("mac_roman", "replace"), raw, end


def dpl2_text_score(text: str, glyph_count: int) -> float:
    stripped = text.strip()
    if len(stripped) < 2:
        return 0.0
    if glyph_count and len(stripped) / glyph_count < 0.35:
        return 0.0
    resource_words = ("BASE", "CBTS", "CLUT", "CNMS", "PFR", "PIC", "TYP", "Postscript Converter")
    if any(word in stripped for word in resource_words):
        return 0.0
    if len(stripped) > 30 and " " not in stripped:
        return 0.0
    rare = sum(1 for c in stripped if c in "{}[]\\|_@#$^~=<>`")
    question_marks = stripped.count("?")
    if rare / len(stripped) > 0.04 or question_marks / len(stripped) > 0.08:
        return 0.0
    expected = sum(1 for c in stripped if c.isalnum() or c in " \t.,;:!?-+/()'\"&%")
    letters = sum(1 for c in stripped if c.isalpha())
    return (expected / len(stripped)) + (letters / len(stripped)) - (rare / len(stripped))


def parse_dpl2_text_record(body: bytes, offset: int, op: int) -> tuple[TextFragment, int] | None:
    layouts: tuple[tuple[int, int], ...]
    if op == 0x15:
        return None
    elif op == 0x28:
        layouts = ((7, 8), (6, 7))
    elif op == 0x29:
        layouts = ((4, 5), (3, 4))
    elif op in (0x2A, 0x2B):
        layouts = ((4, 5),) if op == 0x2B else ((3, 4),)
    else:
        return None

    best: tuple[float, TextFragment, int] | None = None
    limit = len(body)
    for count_delta, start_delta in layouts:
        if offset + start_delta > limit:
            continue
        glyph_count = body[offset + count_delta]
        decoded = decode_dpl2_glyph_run(body, offset + start_delta, glyph_count, limit)
        if decoded is None:
            continue
        text, raw, end = decoded
        score = dpl2_text_score(text, glyph_count)
        if score < 1.25:
            continue
        fragment = TextFragment(offset, op, text.encode("ascii", "replace"))
        if best is None or score > best[0] or (score == best[0] and end < best[2]):
            best = (score, fragment, end)

    if best is None:
        return None
    return best[1], best[2]


def pict_v2_display_start(body: bytes) -> int:
    if len(body) < 38:
        raise CommonGroundError("truncated PICT v2 display stream")
    if body[8:12] != b"\x00\x11\x02\xff" or body[12:14] != b"\x0c\x00":
        raise CommonGroundError("unsupported DPL2 PICT v2 header")
    if len(body) >= 60 and body[46:50] == b"\x00\x01\x00\x0a":
        return 58
    return 38


def pict_region_end(body: bytes, offset: int) -> int:
    if offset + 4 > len(body):
        raise CommonGroundError("truncated PICT region")
    region_size = be16(body, offset + 2)
    if region_size < 2:
        raise CommonGroundError("invalid PICT region size")
    end = offset + 2 + region_size
    if end > len(body):
        raise CommonGroundError("truncated PICT region payload")
    return end + (end & 1)


def pict_embedded_region_end(body: bytes, offset: int) -> int:
    if offset + 2 > len(body):
        raise CommonGroundError("truncated embedded PICT region")
    region_size = be16(body, offset)
    if region_size < 2:
        raise CommonGroundError("invalid embedded PICT region size")
    end = offset + region_size
    if end > len(body):
        raise CommonGroundError("truncated embedded PICT region payload")
    return end + (end & 1)


def parse_pict_clip_region(body: bytes, offset: int) -> tuple[PictClipRegion, int]:
    if offset + 12 > len(body) or be16(body, offset) != 0x0001:
        raise CommonGroundError("truncated PICT clip region")
    region_size = be16(body, offset + 2)
    if region_size < 10:
        raise CommonGroundError("invalid PICT clip region size")
    end = offset + 2 + region_size
    if end > len(body):
        raise CommonGroundError("truncated PICT clip region payload")
    top = be16s(body, offset + 4)
    left = be16s(body, offset + 6)
    bottom = be16s(body, offset + 8)
    right = be16s(body, offset + 10)
    bounds = (left, top, right, bottom)
    if region_size == 10:
        return PictClipRegion(bounds), end + (end & 1)

    runs: list[tuple[int, int, int, int]] = []
    pos = offset + 12
    while pos + 2 <= end:
        y_word = be16(body, pos)
        pos += 2
        if y_word == 0x7FFF:
            break
        y = struct.unpack(">h", struct.pack(">H", y_word))[0]
        xs: list[int] = []
        while pos + 2 <= end:
            x_word = be16(body, pos)
            pos += 2
            if x_word == 0x7FFF:
                break
            xs.append(struct.unpack(">h", struct.pack(">H", x_word))[0])
        for index in range(0, len(xs) - 1, 2):
            run_left = max(left, xs[index])
            run_right = min(right, xs[index + 1])
            run_top = max(top, y)
            run_bottom = min(bottom, y + 1)
            if run_right > run_left and run_bottom > run_top:
                runs.append((run_left, run_top, run_right, run_bottom))
    return PictClipRegion(bounds, tuple(runs)), end + (end & 1)


def pict_long_comment_end(body: bytes, offset: int) -> int:
    if offset + 6 > len(body):
        raise CommonGroundError("truncated PICT long comment")
    payload_size = be16(body, offset + 4)
    end = offset + 6 + payload_size
    if end > len(body):
        raise CommonGroundError("truncated PICT long comment payload")
    return end + (end & 1)


def parse_common_ground_span_comment(body: bytes, offset: int) -> tuple[tuple[tuple[int, int], ...], int] | None:
    if offset + 8 > len(body) or be16(body, offset) != 0x00A1 or be16(body, offset + 2) != 0x8003:
        return None
    payload_size = be16(body, offset + 4)
    end = offset + 6 + payload_size
    if payload_size < 2 or end > len(body):
        return None
    payload = body[offset + 6 : end]
    span_count = be16(payload, 0)
    if len(payload) != 2 + span_count * 8:
        return None
    points: list[tuple[int, int]] = []
    pos = 2
    for _ in range(span_count):
        top = be16s(payload, pos)
        left = be16s(payload, pos + 2)
        bottom = be16s(payload, pos + 4)
        right = be16s(payload, pos + 6)
        pos += 8
        if right < left or bottom < top:
            return None
        points.extend(((left, top), (right, bottom)))
    return tuple(points), end + (end & 1)


def pict_variable_size_end(body: bytes, offset: int) -> int:
    if offset + 4 > len(body):
        raise CommonGroundError("truncated PICT variable-sized opcode")
    payload_size = be16(body, offset + 2)
    if payload_size < 2:
        raise CommonGroundError("invalid PICT variable-sized opcode")
    end = offset + 2 + payload_size
    if end > len(body):
        raise CommonGroundError("truncated PICT variable-sized opcode payload")
    return end + (end & 1)


def pict_direct_bits_end(body: bytes, offset: int) -> int:
    """Return the end of a DirectBitsRect/DirectBitsRgn opcode.

    The samples use opcode 0x009A for embedded 32-bit PixMap content. We do not
    consume the image here; this skipper prevents text scanning from entering
    compressed pixel data. If the advertised pixel payload is larger than the
    enclosing display record, the opcode is treated as consuming the rest of the
    stream, matching the sample catalog records that store bitmap-only tables.
    """
    pos = offset + 2
    if pos + 50 > len(body):
        raise CommonGroundError("truncated PICT DirectBits opcode")
    pos += 4  # baseAddr
    row_bytes = be16(body, pos) & 0x3FFF
    pos += 2
    top = be16(body, pos)
    left = be16(body, pos + 2)
    bottom = be16(body, pos + 4)
    right = be16(body, pos + 6)
    pos += 8
    pos += 26  # remaining PixMap fields through pmReserved
    pos += 8  # source rect
    pos += 8  # destination rect
    pos += 2  # transfer mode
    height = max(0, bottom - top)
    if row_bytes <= 0 or height <= 0:
        raise CommonGroundError("invalid PICT DirectBits dimensions")
    # DirectBits data in these samples is PackBits-like row data. The catalog
    # records also advertise large image payloads that intentionally run to the
    # enclosing display-record end; clamping is stricter than scanning into it.
    if row_bytes > 250:
        estimated = height * (row_bytes + 2)
    else:
        estimated = height * (row_bytes + 1)
    end = pos + estimated
    return min(len(body), end)


def parse_pict_direct_bits(body: bytes, offset: int, style: StyleState) -> tuple[TextFragment, int] | None:
    if offset + 2 + 68 > len(body) or be16(body, offset) not in (0x009A, 0x009B):
        return None
    pos = offset + 2
    pos += 4  # baseAddr
    row_bytes = be16(body, pos) & 0x3FFF
    pos += 2
    bounds_top = be16s(body, pos)
    bounds_left = be16s(body, pos + 2)
    bounds_bottom = be16s(body, pos + 4)
    bounds_right = be16s(body, pos + 6)
    pos += 8
    pixmap_version = be16(body, pos)
    pack_type = be16(body, pos + 2)
    pos += 4
    pos += 4  # packSize
    pos += 8  # hRes/vRes
    pixel_type = be16(body, pos)
    pixel_size = be16(body, pos + 2)
    cmp_count = be16(body, pos + 4)
    cmp_size = be16(body, pos + 6)
    pos += 8
    pos += 12  # planeBytes, pmTable, pmReserved
    if pixmap_version != 0 or pack_type not in (0, 3, 4) or pixel_type != 16:
        return None
    if pixel_size == 16:
        if pack_type != 3 or cmp_size != 5:
            return None
    elif pixel_size == 32:
        if pack_type != 4 or cmp_count not in (3, 4) or cmp_size != 8:
            return None
    else:
        return None
    width = bounds_right - bounds_left
    height = bounds_bottom - bounds_top
    if width <= 0 or height <= 0:
        return None
    if pixel_size == 16 and row_bytes < width * 2:
        return None
    if pixel_size == 32 and row_bytes < width * 4:
        return None

    src_top = be16s(body, pos)
    src_left = be16s(body, pos + 2)
    src_bottom = be16s(body, pos + 4)
    src_right = be16s(body, pos + 6)
    dst_top = be16s(body, pos + 8)
    dst_left = be16s(body, pos + 10)
    dst_bottom = be16s(body, pos + 12)
    dst_right = be16s(body, pos + 14)
    transfer_mode = be16(body, pos + 16)
    pos += 18
    if transfer_mode not in (0, 1, 3, 36, 64):
        return None
    if be16(body, offset) == 0x009B:
        if pos + 2 > len(body):
            return None
        region_size = be16(body, pos)
        if region_size < 2 or pos + region_size > len(body):
            return None
        pos += region_size

    rows: list[bytes] = []
    if pack_type == 0:
        data_len = row_bytes * height
        if pos + data_len > len(body):
            return None
        for row_start in range(pos, pos + data_len, row_bytes):
            rows.append(body[row_start : row_start + row_bytes])
        pos += data_len
    else:
        for _ in range(height):
            if pos + 2 > len(body):
                break
            packed_len = be16(body, pos) if row_bytes > 250 else body[pos]
            pos += 2 if row_bytes > 250 else 1
            if packed_len <= 0:
                break
            available_len = min(packed_len, max(0, len(body) - pos))
            expected_row_size = width * 2 if pixel_size == 16 else (width * 3 if cmp_count == 3 else row_bytes)
            if available_len < packed_len:
                rows.append(b"\x00" * expected_row_size)
                pos += packed_len
                break
            if pixel_size == 16:
                decoded = packbits_decode_units_loose(body[pos : pos + available_len], 2, expected_row_size)
            elif cmp_count == 3:
                decoded = packbits_decode_units_loose(body[pos : pos + available_len], 1, expected_row_size)
            else:
                decoded = packbits_decode_units_loose(body[pos : pos + available_len], 1, expected_row_size)
            rows.append(decoded)
            pos += packed_len
        expected_row_size = width * 2 if pixel_size == 16 else (width * 3 if cmp_count == 3 else row_bytes)
        while len(rows) < height:
            rows.append(b"\x00" * expected_row_size)

    crop_left = max(0, src_left - bounds_left)
    crop_top = max(0, src_top - bounds_top)
    crop_right = min(width, src_right - bounds_left)
    crop_bottom = min(height, src_bottom - bounds_top)
    if crop_right <= crop_left or crop_bottom <= crop_top:
        return None

    png_rows: list[bytes] = []
    for source_row in rows[crop_top:crop_bottom]:
        out = bytearray()
        for x in range(crop_left, crop_right):
            if pixel_size == 16:
                base = x * 2
                if base + 2 > len(source_row):
                    return None
                value = be16(source_row, base)
                red = round(((value >> 10) & 0x1F) * 255 / 31)
                green = round(((value >> 5) & 0x1F) * 255 / 31)
                blue = round((value & 0x1F) * 255 / 31)
            elif cmp_count == 3:
                if x >= width or (width * 2 + x) >= len(source_row):
                    return None
                red = source_row[x]
                green = source_row[width + x]
                blue = source_row[width * 2 + x]
            else:
                if x >= width or (width * 3 + x) >= len(source_row):
                    return None
                # QuickDraw 32-bit PixMaps store an unused component followed
                # by red, green, and blue component planes.
                red = source_row[width + x]
                green = source_row[width * 2 + x]
                blue = source_row[width * 3 + x]
            alpha = 255
            out.extend((red, green, blue, alpha))
        png_rows.append(bytes(out))

    png_width = crop_right - crop_left
    png_height = crop_bottom - crop_top
    raw = bytearray()
    for row in png_rows:
        raw.append(0)
        raw.extend(row)
    png = (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", struct.pack(">IIBBBBB", png_width, png_height, 8, 6, 0, 0, 0))
        + png_chunk(b"IDAT", zlib.compress(bytes(raw)))
        + png_chunk(b"IEND", b"")
    )
    dst_width = dst_right - dst_left
    dst_height = dst_bottom - dst_top
    if dst_width <= 0 or dst_height <= 0:
        return None
    image = ImageRun(
        png=png,
        width=png_width,
        height=png_height,
        width_twips=max(1, dst_width * 5),
        height_twips=max(1, dst_height * 5),
        x=dst_left,
        y=dst_top,
        offset=offset,
    )
    return TextFragment(offset, be16(body, offset), b"", y=dst_top, x=dst_left, style=style, image=image), pos


def pict_direct_bits_destination(body: bytes, offset: int) -> tuple[int, int, int, int, int] | None:
    if offset + 70 > len(body) or be16(body, offset) not in (0x009A, 0x009B):
        return None
    pos = offset + 2 + 4 + 2 + 8 + 2 + 2 + 4 + 8 + 2 + 2 + 2 + 2 + 4 + 4 + 4
    if pos + 18 > len(body):
        return None
    src_top = be16s(body, pos)
    src_left = be16s(body, pos + 2)
    src_bottom = be16s(body, pos + 4)
    src_right = be16s(body, pos + 6)
    dst_top = be16s(body, pos + 8)
    dst_left = be16s(body, pos + 10)
    dst_bottom = be16s(body, pos + 12)
    dst_right = be16s(body, pos + 14)
    transfer_mode = be16(body, pos + 16)
    if src_bottom <= src_top or src_right <= src_left or dst_bottom <= dst_top or dst_right <= dst_left:
        return None
    return dst_left, dst_top, dst_right - dst_left, dst_bottom - dst_top, transfer_mode


def parse_pict_compressed_quicktime(body: bytes, offset: int, style: StyleState) -> tuple[TextFragment, int] | None:
    if offset + 6 > len(body) or be16(body, offset) != 0x8200:
        return None
    payload_size = be32(body, offset + 2)
    payload_start = offset + 6
    payload_end = payload_start + payload_size
    if payload_size < 160 or payload_end > len(body):
        return None
    payload = body[payload_start:payload_end]
    jpeg_start = payload.find(b"\xff\xd8\xff")
    if jpeg_start < 0:
        return None
    jpeg_end = payload.find(b"\xff\xd9", jpeg_start)
    if jpeg_end < 0:
        return None
    jpeg = payload[jpeg_start : jpeg_end + 2]
    if Image is None:
        return None
    try:
        with Image.open(io.BytesIO(jpeg)) as image:
            image_width, image_height = image.size
    except Exception:
        return None
    x_scale = struct.unpack_from(">q", payload, 0)[0] / 4294967296.0
    y_scale = struct.unpack_from(">q", payload, 16)[0] / 4294967296.0
    if x_scale <= 0 or y_scale <= 0:
        return None
    x = struct.unpack_from(">i", payload, 24)[0]
    y = struct.unpack_from(">i", payload, 28)[0]
    dst_width = max(1, int(round(image_width * x_scale)))
    dst_height = max(1, int(round(image_height * y_scale)))
    image = ImageRun(
        png=jpeg,
        width=image_width,
        height=image_height,
        width_twips=dst_width * 5,
        height_twips=dst_height * 5,
        x=x,
        y=y,
        offset=offset,
    )
    return TextFragment(offset, 0x8200, b"", y=y, x=x, style=style, image=image), payload_end + (payload_end & 1)


def pict_compressed_quicktime_end(body: bytes, offset: int) -> int:
    if offset + 6 > len(body) or be16(body, offset) != 0x8200:
        raise CommonGroundError("invalid CompressedQuickTime opcode")
    payload_size = be32(body, offset + 2)
    payload_end = offset + 6 + payload_size
    if payload_end > len(body):
        raise CommonGroundError("truncated CompressedQuickTime payload")
    return payload_end + (payload_end & 1)


def pict_bitmap_destination(body: bytes, offset: int) -> tuple[int, int, int, int, int] | None:
    if offset + 30 > len(body) or body[offset] != 0 or body[offset + 1] not in (0x98, 0x99):
        return None
    row_word = be16(body, offset + 2)
    if row_word & 0x8000:
        pix = offset + 2
        color_table = pix + 46
        if color_table + 8 > len(body):
            return None
        color_count = be16(body, color_table + 6) + 1
        table_end = color_table + 8 + color_count * 8
        if color_count <= 0 or table_end + 18 > len(body):
            return None
        src_top = be16s(body, table_end)
        src_left = be16s(body, table_end + 2)
        src_bottom = be16s(body, table_end + 4)
        src_right = be16s(body, table_end + 6)
        dst_top = be16s(body, table_end + 8)
        dst_left = be16s(body, table_end + 10)
        dst_bottom = be16s(body, table_end + 12)
        dst_right = be16s(body, table_end + 14)
        transfer_mode = be16(body, table_end + 16)
    else:
        src_top = be16s(body, offset + 12)
        src_left = be16s(body, offset + 14)
        src_bottom = be16s(body, offset + 16)
        src_right = be16s(body, offset + 18)
        dst_top = be16s(body, offset + 20)
        dst_left = be16s(body, offset + 22)
        dst_bottom = be16s(body, offset + 24)
        dst_right = be16s(body, offset + 26)
        transfer_mode = be16(body, offset + 28)
    if src_bottom <= src_top or src_right <= src_left or dst_bottom <= dst_top or dst_right <= dst_left:
        return None
    return dst_left, dst_top, dst_right - dst_left, dst_bottom - dst_top, transfer_mode


def synthesize_pict_for_deark(record_data: bytes) -> bytes:
    if len(record_data) < 14 or record_data[8:12] != b"\x00\x11\x02\xff":
        raise CommonGroundError("cannot synthesize unsupported PICT stream")
    height = be16(record_data, 4)
    width = be16(record_data, 6)
    if width <= 0 or height <= 0:
        raise CommonGroundError("invalid PICT dimensions")
    return struct.pack(">HHHHH", 0, 0, 0, height, width) + record_data[8:]


def deark_extract_first_pict_png(record_data: bytes) -> bytes | None:
    with tempfile.TemporaryDirectory(prefix="commonGround_deark_") as tmp_name:
        tmp = Path(tmp_name)
        pict_path = tmp / "record.pict"
        out_dir = tmp / "out"
        out_dir.mkdir()
        pict_path.write_bytes(synthesize_pict_for_deark(record_data))
        try:
            subprocess.run(
                ["deark", "-m", "pict", "-od", str(out_dir), str(pict_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=30,
            )
        except (OSError, subprocess.SubprocessError):
            return None
        pngs = sorted(out_dir.glob("*.png"))
        if not pngs:
            return None
        return pngs[0].read_bytes()


def fallback_cgdc_pict_page_events(body: bytes, page: PictPage) -> list[PictImageEvent]:
    if page.start < 8:
        return []
    record_data = body[page.start - 8 : page.end]
    events: list[PictImageEvent] = []
    i = 0
    while i + 6 <= len(record_data):
        op = be16(record_data, i)
        if op == 0x8200:
            parsed = parse_pict_compressed_quicktime(record_data, i, StyleState())
            if parsed is None:
                i += 2
                continue
            fragment, end = parsed
            if fragment.image is not None:
                events.append(PictImageEvent(i, fragment.image))
            i = end
            continue
        i += 1
    if events:
        return events

    png = deark_extract_first_pict_png(record_data)
    if png is None:
        return []
    destination: tuple[int, int, int, int, int] | None = None
    for offset in range(len(record_data) - 2):
        op = be16(record_data, offset)
        if op in (0x009A, 0x009B):
            destination = pict_direct_bits_destination(record_data, offset)
            if destination is not None:
                break
        if op in (0x0098, 0x0099):
            destination = pict_bitmap_destination(record_data, offset)
            if destination is not None:
                break
    if Image is not None:
        try:
            with Image.open(io.BytesIO(png)) as image:
                image_width, image_height = image.size
        except Exception:
            image_width = max(1, (page.right or 0) - (page.left or 0))
            image_height = max(1, (page.bottom or 0) - (page.top or 0))
    else:
        image_width = max(1, (page.right or 0) - (page.left or 0))
        image_height = max(1, (page.bottom or 0) - (page.top or 0))
    if destination is None:
        dst_left = page.left or 0
        dst_top = page.top or 0
        dst_width = image_width
        dst_height = image_height
    else:
        dst_left, dst_top, dst_width, dst_height, _ = destination
    image = ImageRun(
        png=png,
        width=image_width,
        height=image_height,
        width_twips=max(1, dst_width * 5),
        height_twips=max(1, dst_height * 5),
        x=dst_left,
        y=dst_top,
        offset=page.start,
    )
    return [PictImageEvent(page.start, image)]


PICT_FIXED_DATA_LENGTHS: dict[int, int] = {
    0x0000: 0,   # NOP
    0x0002: 8,   # BkPat
    0x0003: 2,   # TxFont
    0x0004: 2,   # TxFace
    0x0005: 2,   # TxMode
    0x0006: 4,   # SpExtra
    0x0007: 4,   # PnSize
    0x0008: 2,   # PnMode
    0x0009: 8,   # PnPat
    0x000A: 8,   # FillPat
    0x000B: 4,   # OvSize
    0x000C: 4,   # Origin
    0x000D: 2,   # TxSize
    0x000E: 4,   # FgColor
    0x000F: 4,   # BkColor
    0x0010: 8,   # TxRatio
    0x0013: 16,  # PnPixPat, observed short dither-pattern form
    0x0015: 2,   # PnLocHFrac
    0x0016: 4,   # ChExtra
    0x001A: 6,   # RGBFgCol
    0x001B: 6,   # RGBBkCol
    0x001C: 0,   # HiliteMode
    0x001D: 6,   # HiliteColor
    0x001E: 0,   # DefHilite
    0x001F: 6,   # OpColor
    0x0020: 8,   # Line
    0x0021: 4,   # LineFrom
    0x0022: 6,   # ShortLine
    0x0023: 2,   # ShortLineFrom
    0x002E: 6,   # glyphState
    0x0030: 8,
    0x0031: 8,
    0x0032: 8,
    0x0033: 8,
    0x0034: 8,
    0x0038: 0,
    0x0039: 0,
    0x003A: 0,
    0x003B: 0,
    0x003C: 0,
    0x0040: 8,
    0x0041: 8,
    0x0042: 8,
    0x0043: 8,
    0x0044: 8,
    0x0048: 0,
    0x0049: 0,
    0x004A: 0,
    0x004B: 0,
    0x004C: 0,
    0x0050: 8,
    0x0051: 8,
    0x0052: 8,
    0x0053: 8,
    0x0054: 8,
    0x0058: 0,
    0x0059: 0,
    0x005A: 0,
    0x005B: 0,
    0x005C: 0,
    0x0060: 12,
    0x0061: 12,
    0x0062: 12,
    0x0063: 12,
    0x0064: 12,
    0x0068: 4,
    0x0069: 4,
    0x006A: 4,
    0x006B: 4,
    0x006C: 4,
    0x00A0: 2,   # ShortComment
    0x0C00: 24,  # HeaderOp
}


def dpl2_pict_draw_events(
    record_data: bytes,
    encoding: str = "mac_roman",
    size_mapper: Callable[[int], int] | None = None,
) -> list[PictTextEvent | PictImageEvent | PictVectorEvent]:
    if size_mapper is None:
        size_mapper = cgdc_size_to_half_points
    events: list[PictTextEvent | PictImageEvent | PictVectorEvent] = []
    style = StyleState()
    font_names: dict[int, str] = {}
    current_x = 0.0
    current_y = 0
    last_baseline_y = 0
    current_x_frac = 0.0
    pen_width = 1
    current_fill_pattern: bytes | None = None
    current_clip: PictClipRegion | None = None
    decoded_quicktime_rect: tuple[int, int, int, int] | None = None
    i = pict_v2_display_start(record_data)
    limit = len(record_data)

    def aligned(end: int) -> int:
        return end + (end & 1)

    while i + 2 <= limit:
        op = be16(record_data, i)
        styled = apply_cgdc_style_control(record_data, i, style, font_names, size_mapper)
        if styled is not None and styled[1] <= limit:
            style, i = styled
            if op == 0x002C:
                i = aligned(i)
            continue
        if op == 0x00FF:
            break
        if op == 0x0015 and i + 4 <= limit:
            current_x_frac = be16(record_data, i + 2) / 65536.0
            current_x = math.floor(current_x) + current_x_frac
            i += 4
            continue
        if op == 0x0007 and i + 6 <= limit:
            pen_width = max(1, be16s(record_data, i + 4))
            i += 6
            continue
        if op == 0x000A and i + 10 <= limit:
            current_fill_pattern = record_data[i + 2 : i + 10]
            i += 10
            continue
        if op == 0x0020 and i + 10 <= limit:
            y1 = be16s(record_data, i + 2)
            x1 = be16s(record_data, i + 4)
            y2 = be16s(record_data, i + 6)
            x2 = be16s(record_data, i + 8)
            events.append(PictVectorEvent(i, "line", ((x1, y1), (x2, y2)), False, style.color, pen_width, current_clip))
            current_x = x2
            current_y = y2
            i += 10
            continue
        if op == 0x0021 and i + 6 <= limit:
            y2 = be16s(record_data, i + 2)
            x2 = be16s(record_data, i + 4)
            events.append(PictVectorEvent(i, "line", ((current_x, current_y), (x2, y2)), False, style.color, pen_width, current_clip))
            current_x = x2
            current_y = y2
            i += 6
            continue
        if op == 0x0022 and i + 8 <= limit:
            y1 = be16s(record_data, i + 2)
            x1 = be16s(record_data, i + 4)
            dh = i8(record_data, i + 6)
            dv = i8(record_data, i + 7)
            x2 = x1 + dh
            y2 = y1 + dv
            events.append(PictVectorEvent(i, "line", ((x1, y1), (x2, y2)), False, style.color, pen_width, current_clip))
            current_x = x2
            current_y = y2
            i += 8
            continue
        if op == 0x0023 and i + 4 <= limit:
            dh = i8(record_data, i + 2)
            dv = i8(record_data, i + 3)
            x2 = current_x + dh
            y2 = current_y + dv
            events.append(PictVectorEvent(i, "line", ((current_x, current_y), (x2, y2)), False, style.color, pen_width, current_clip))
            current_x = x2
            current_y = y2
            i += 4
            continue
        if op in (0x0030, 0x0031, 0x0034, 0x0040, 0x0041, 0x0044, 0x0050, 0x0051, 0x0054) and i + 10 <= limit:
            top = be16s(record_data, i + 2)
            left = be16s(record_data, i + 4)
            bottom = be16s(record_data, i + 6)
            right = be16s(record_data, i + 8)
            if bottom >= top and right >= left:
                kind = "oval" if 0x0050 <= op <= 0x005F else "rect"
                filled = op in (0x0031, 0x0034, 0x0041, 0x0044, 0x0051, 0x0054)
                events.append(
                    PictVectorEvent(
                        i,
                        kind,
                        ((left, top), (right, bottom)),
                        filled,
                        style.color,
                        pen_width,
                        current_clip,
                        current_fill_pattern if filled and op in (0x0034, 0x0044, 0x0054) else None,
                    )
                )
            i += 10
            continue
        if op == 0x0001:
            current_clip, i = parse_pict_clip_region(record_data, i)
            continue
        if op in (0x0070, 0x0071, 0x0072, 0x0073, 0x0074) and i + 14 <= limit:
            poly_size = be16(record_data, i + 2)
            end = i + 2 + poly_size
            if poly_size >= 10 and end <= limit:
                points = []
                pos = i + 12
                while pos + 4 <= end:
                    y = be16s(record_data, pos)
                    x = be16s(record_data, pos + 2)
                    points.append((x, y))
                    pos += 4
                if len(points) >= 2:
                    color = (255, 255, 255) if op == 0x0072 else style.color
                    fill_pattern = current_fill_pattern if op in (0x0071, 0x0074) else None
                    events.append(PictVectorEvent(i, "polygon", tuple(points), op in (0x0071, 0x0072, 0x0074), color, pen_width, current_clip, fill_pattern))
                i = aligned(end)
                continue
        if op in (0x0070, 0x0071, 0x0072, 0x0073, 0x0074, 0x0078, 0x0079, 0x007A, 0x007B, 0x007C):
            i = pict_variable_size_end(record_data, i)
            continue
        if op in (0x0080, 0x0081, 0x0082, 0x0083, 0x0084, 0x0088, 0x0089, 0x008A, 0x008B, 0x008C):
            i = pict_variable_size_end(record_data, i)
            continue
        if op == 0x00A1:
            span_comment = parse_common_ground_span_comment(record_data, i)
            if span_comment is not None:
                points, end = span_comment
                if points:
                    events.append(PictVectorEvent(i, "rects", points, True, style.color, pen_width, current_clip))
                i = end
                continue
            i = pict_long_comment_end(record_data, i)
            continue
        if op in (0x0090, 0x0091, 0x0098, 0x0099):
            bitmap = parse_cgdc_bitmap(record_data, i, style)
            if bitmap is None:
                destination = pict_bitmap_destination(record_data, i) if op in (0x0098, 0x0099) else None
                png = deark_extract_first_pict_png(record_data) if destination is not None else None
                if destination is None or png is None:
                    break
                dst_left, dst_top, dst_width, dst_height, _ = destination
                if Image is not None:
                    try:
                        with Image.open(io.BytesIO(png)) as image:
                            image_width, image_height = image.size
                    except Exception:
                        image_width = max(1, dst_width)
                        image_height = max(1, dst_height)
                else:
                    image_width = max(1, dst_width)
                    image_height = max(1, dst_height)
                image = ImageRun(
                    png=png,
                    width=image_width,
                    height=image_height,
                    width_twips=max(1, dst_width * 5),
                    height_twips=max(1, dst_height * 5),
                    x=dst_left,
                    y=dst_top,
                    offset=i,
                )
                events.append(PictImageEvent(i, image, current_clip))
                break
            fragment, end = bitmap
            if fragment.image is not None:
                events.append(PictImageEvent(i, fragment.image, current_clip))
                decoded_quicktime_rect = None
            i = aligned(end)
            continue
        if op in (0x009A, 0x009B):
            direct_bits = parse_pict_direct_bits(record_data, i, style)
            if direct_bits is None:
                destination = pict_direct_bits_destination(record_data, i)
                png = deark_extract_first_pict_png(record_data) if destination is not None else None
                if destination is not None and png is not None:
                    dst_left, dst_top, dst_width, dst_height, _ = destination
                    if Image is not None:
                        try:
                            with Image.open(io.BytesIO(png)) as image:
                                image_width, image_height = image.size
                        except Exception:
                            image_width = max(1, dst_width)
                            image_height = max(1, dst_height)
                    else:
                        image_width = max(1, dst_width)
                        image_height = max(1, dst_height)
                    image = ImageRun(
                        png=png,
                        width=image_width,
                        height=image_height,
                        width_twips=max(1, dst_width * 5),
                        height_twips=max(1, dst_height * 5),
                        x=dst_left,
                        y=dst_top,
                        offset=i,
                    )
                    events.append(PictImageEvent(i, image, current_clip))
                    break
                i = pict_direct_bits_end(record_data, i)
                continue
            fragment, end = direct_bits
            if fragment.image is not None:
                events.append(PictImageEvent(i, fragment.image, current_clip))
                decoded_quicktime_rect = None
            i = aligned(end)
            continue
        if op == 0x8200:
            compressed_quicktime = parse_pict_compressed_quicktime(record_data, i, style)
            if compressed_quicktime is not None:
                fragment, end = compressed_quicktime
                if fragment.image is not None:
                    events.append(PictImageEvent(i, fragment.image, current_clip))
                    decoded_quicktime_rect = (
                        fragment.image.x or 0,
                        fragment.image.y or 0,
                        (fragment.image.x or 0) + max(1, fragment.image.width_twips // 5),
                        (fragment.image.y or 0) + max(1, fragment.image.height_twips // 5),
                    )
                    fallback_start = aligned(end)
                    if fallback_start + 2 <= limit and be16(record_data, fallback_start) in (0x0090, 0x0091, 0x0098, 0x0099):
                        fallback = parse_cgdc_bitmap(record_data, fallback_start, style)
                        if fallback is not None and fallback[0].image is not None:
                            fallback_image = fallback[0].image
                            if (
                                fallback_image.x == fragment.image.x
                                and fallback_image.y == fragment.image.y
                                and fallback_image.width_twips == fragment.image.width_twips
                                and fallback_image.height_twips == fragment.image.height_twips
                            ):
                                end = fallback[1]
                i = aligned(end)
                continue
            i = pict_compressed_quicktime_end(record_data, i)
            decoded_quicktime_rect = None
            continue

        if op == 0x0028 and i + 7 <= limit:
            y = be16(record_data, i + 2)
            x = be16s(record_data, i + 4)
            length = record_data[i + 6]
            start = i + 7
            end = start + length
            if 0 < length <= 240 and end <= limit:
                raw_text = record_data[start:end]
                text = decode_cgdc_text_bytes(raw_text, encoding).replace("\x00", "") if pict_text_payload_ok(raw_text) else ""
                current_x = x + current_x_frac
                draw_y = y
                raised_mark = visible_pict_text(text) and len(text.strip()) <= 2 and 10 <= last_baseline_y - y <= 80
                current_y = last_baseline_y if raised_mark else y
                if not raised_mark:
                    last_baseline_y = y
                if emit_pict_text(op, text) and not (quicktime_fallback_text(text) and point_in_rect(current_x, draw_y, decoded_quicktime_rect)):
                    events.append(PictTextEvent(i, current_x, draw_y, text, style, current_clip))
                i = aligned(end)
                continue
        elif op == 0x0029 and i + 4 <= limit:
            length = record_data[i + 3]
            start = i + 4
            end = start + length
            if 0 < length <= 240 and end <= limit:
                current_x = math.floor(current_x) + current_x_frac
                current_x += record_data[i + 2]
                raw_text = record_data[start:end]
                text = decode_cgdc_text_bytes(raw_text, encoding).replace("\x00", "") if pict_text_payload_ok(raw_text) else ""
                if emit_pict_text(op, text) and not (quicktime_fallback_text(text) and point_in_rect(current_x, current_y, decoded_quicktime_rect)):
                    events.append(PictTextEvent(i, current_x, current_y, text, style, current_clip))
                i = aligned(end)
                continue
        elif op == 0x002A and i + 4 <= limit:
            length = record_data[i + 3]
            start = i + 4
            end = start + length
            if 0 < length <= 240 and end <= limit:
                current_x = math.floor(current_x) + current_x_frac
                current_y += record_data[i + 2]
                last_baseline_y = current_y
                raw_text = record_data[start:end]
                text = decode_cgdc_text_bytes(raw_text, encoding).replace("\x00", "") if pict_text_payload_ok(raw_text) else ""
                if emit_pict_text(op, text) and not (quicktime_fallback_text(text) and point_in_rect(current_x, current_y, decoded_quicktime_rect)):
                    events.append(PictTextEvent(i, current_x, current_y, text, style, current_clip))
                i = aligned(end)
                continue
        elif op == 0x002B and i + 5 <= limit:
            length = record_data[i + 4]
            start = i + 5
            end = start + length
            if 0 < length <= 240 and end <= limit:
                current_x = math.floor(current_x) + current_x_frac
                current_x += record_data[i + 2]
                current_y += record_data[i + 3]
                last_baseline_y = current_y
                raw_text = record_data[start:end]
                text = decode_cgdc_text_bytes(raw_text, encoding).replace("\x00", "") if pict_text_payload_ok(raw_text) else ""
                if emit_pict_text(op, text) and not (quicktime_fallback_text(text) and point_in_rect(current_x, current_y, decoded_quicktime_rect)):
                    events.append(PictTextEvent(i, current_x, current_y, text, style, current_clip))
                i = aligned(end)
                continue

        data_len = PICT_FIXED_DATA_LENGTHS.get(op)
        if data_len is None:
            break
        end = i + 2 + data_len
        if end > limit:
            raise CommonGroundError(f"truncated PICT opcode 0x{op:04x}")
        i = end
    return events


def dpl2_pict_text_events(
    record_data: bytes,
    encoding: str = "mac_roman",
    size_mapper: Callable[[int], int] | None = None,
) -> list[PictTextEvent]:
    return [
        event
        for event in dpl2_pict_draw_events(record_data, encoding, size_mapper)
        if isinstance(event, PictTextEvent)
    ]


def iter_dpl2_records(body: bytes) -> list[tuple[int, bytes]]:
    records: list[tuple[int, bytes]] = []
    offset = 0
    while offset + 16 <= len(body):
        payload_len = be32(body, offset)
        end = offset + 4 + payload_len
        if end > len(body):
            break
        if payload_len < 10:
            payload = body[offset + 4 : end]
            if payload_len == 2 and payload == b"\x00\x00":
                record = (
                    struct.pack(">I", 12 + payload_len)
                    + b"\x01\x01\x00\x0c"
                    + b"\x00\x00\x00\x00"
                    + struct.pack(">I", payload_len)
                    + payload
                )
                records.append((offset, record))
                offset = end
                continue
            break
        record = body[offset:end]
        if record[4:8] != b"\x01\x01\x00\x0c":
            break
        records.append((offset, record))
        offset = end
    return records


def dpl2_lzss_decode(data: bytes, expected_size: int) -> bytes:
    """Expand a compressed DPL2 record payload.

    DPL2 resource records use the classic LZSS layout also used by many early
    1990s Mac/Windows applications: one LSB-first flag byte controls eight
    items, set bits are literals, clear bits are 12-bit window backreferences,
    and the match length is the low nibble plus three.
    """
    if expected_size < 0:
        raise CommonGroundError("invalid DPL2 expanded record size")
    window_size = 4096
    window = bytearray(window_size)
    write_pos = window_size - 18
    out = bytearray()
    i = 0

    def emit(byte: int) -> None:
        nonlocal write_pos
        out.append(byte)
        window[write_pos] = byte
        write_pos = (write_pos + 1) & (window_size - 1)

    while i < len(data) and len(out) < expected_size:
        flags = data[i]
        i += 1
        for bit in range(8):
            if len(out) >= expected_size:
                break
            if flags & (1 << bit):
                if i >= len(data):
                    raise CommonGroundError("truncated DPL2 LZSS literal")
                emit(data[i])
                i += 1
                continue

            if i + 2 > len(data):
                raise CommonGroundError("truncated DPL2 LZSS backreference")
            low = data[i]
            high = data[i + 1]
            i += 2
            read_pos = ((high & 0xF0) << 4) | low
            count = (high & 0x0F) + 3
            for delta in range(count):
                emit(window[(read_pos + delta) & (window_size - 1)])
                if len(out) >= expected_size:
                    break

    if len(out) != expected_size or i != len(data):
        raise CommonGroundError(
            f"DPL2 LZSS size mismatch: expanded {len(out)} of {expected_size}, consumed {i} of {len(data)}"
        )
    return bytes(out)


def dpl2_lzss_decode_all(data: bytes) -> bytes:
    window_size = 4096
    window = bytearray(window_size)
    write_pos = window_size - 18
    out = bytearray()
    i = 0

    def emit(byte: int) -> None:
        nonlocal write_pos
        out.append(byte)
        window[write_pos] = byte
        write_pos = (write_pos + 1) & (window_size - 1)

    while i < len(data):
        flags = data[i]
        i += 1
        for bit in range(8):
            if i >= len(data):
                break
            if flags & (1 << bit):
                emit(data[i])
                i += 1
                continue
            if i + 2 > len(data):
                raise CommonGroundError("truncated DPL2 LZSS backreference")
            low = data[i]
            high = data[i + 1]
            i += 2
            read_pos = ((high & 0xF0) << 4) | low
            count = (high & 0x0F) + 3
            for delta in range(count):
                emit(window[(read_pos + delta) & (window_size - 1)])

    return bytes(out)


def pfr_u24(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 3], "big")


def pfr_s24(data: bytes, offset: int) -> int:
    value = pfr_u24(data, offset)
    if value & 0x800000:
        value -= 0x1000000
    return value


def pfr_i8(value: int) -> int:
    return value - 256 if value >= 128 else value


def pfr_extra_items(data: bytes, offset: int, limit: int) -> tuple[list[tuple[int, bytes]], int]:
    if offset >= limit:
        raise CommonGroundError("truncated PFR extra item count")
    count = data[offset]
    offset += 1
    items: list[tuple[int, bytes]] = []
    for _ in range(count):
        if offset + 2 > limit:
            raise CommonGroundError("truncated PFR extra item header")
        item_size = data[offset]
        item_type = data[offset + 1]
        item_start = offset + 2
        item_end = item_start + item_size
        if item_end > limit:
            raise CommonGroundError("truncated PFR extra item payload")
        items.append((item_type, data[item_start:item_end]))
        offset = item_end
    return items, offset


def transform_pfr_commands(
    commands: list[PfrPathCommand],
    x_scale: float,
    y_scale: float,
    x_delta: float,
    y_delta: float,
) -> list[PfrPathCommand]:
    transformed: list[PfrPathCommand] = []
    for command in commands:
        points = tuple((x * x_scale + x_delta, y * y_scale + y_delta) for x, y in command.points)
        transformed.append(PfrPathCommand(command.op, points))
    return transformed


def parse_pfr_glyph_path(
    metric: PfrFontMetrics,
    char_code: int,
    *,
    depth: int = 0,
) -> list[PfrPathCommand]:
    if depth > 32:
        raise CommonGroundError("PFR compound glyph recursion limit exceeded")
    glyph_ref = metric.glyph_programs.get(char_code)
    if glyph_ref is None:
        raise CommonGroundError("PFR glyph program not found")
    glyph_size, glyph_offset = glyph_ref
    return parse_pfr_glyph_program(metric, glyph_offset, glyph_size, depth=depth)


def parse_pfr_glyph_program(
    metric: PfrFontMetrics,
    glyph_offset: int,
    glyph_size: int,
    *,
    depth: int = 0,
) -> list[PfrPathCommand]:
    start = metric.gps_section_offset + glyph_offset
    end = start + glyph_size
    data = metric.pfr_data
    if glyph_size <= 0 or start < 0 or end > len(data):
        raise CommonGroundError("invalid PFR glyph program range")
    if data[start] & 0x80:
        return parse_pfr_compound_glyph(metric, data[start:end], depth=depth)
    return parse_pfr_simple_glyph(data[start:end])


def parse_pfr_compound_glyph(metric: PfrFontMetrics, payload: bytes, *, depth: int) -> list[PfrPathCommand]:
    pos = 0
    flags = payload[pos]
    pos += 1
    if not (flags & 0x80):
        raise CommonGroundError("not a PFR compound glyph")
    component_count = flags & 0x3F
    if flags & 0x40:
        _, pos = pfr_extra_items(payload, pos, len(payload))
    commands: list[PfrPathCommand] = []
    for _ in range(component_count):
        if pos >= len(payload):
            raise CommonGroundError("truncated PFR compound component")
        fmt = payload[pos]
        pos += 1
        x_scale = 1.0
        y_scale = 1.0
        if fmt & 0x10:
            if pos + 2 > len(payload):
                raise CommonGroundError("truncated PFR compound x scale")
            x_scale = be16s(payload, pos) / 4096.0
            pos += 2
        if fmt & 0x20:
            if pos + 2 > len(payload):
                raise CommonGroundError("truncated PFR compound y scale")
            y_scale = be16s(payload, pos) / 4096.0
            pos += 2
        x_delta = 0
        y_delta = 0
        if (fmt & 0x03) == 1:
            if pos + 2 > len(payload):
                raise CommonGroundError("truncated PFR compound x position")
            x_delta = be16s(payload, pos)
            pos += 2
        elif (fmt & 0x03) == 2:
            if pos >= len(payload):
                raise CommonGroundError("truncated PFR compound x delta")
            x_delta = pfr_i8(payload[pos])
            pos += 1
        if ((fmt >> 2) & 0x03) == 1:
            if pos + 2 > len(payload):
                raise CommonGroundError("truncated PFR compound y position")
            y_delta = be16s(payload, pos)
            pos += 2
        elif ((fmt >> 2) & 0x03) == 2:
            if pos >= len(payload):
                raise CommonGroundError("truncated PFR compound y delta")
            y_delta = pfr_i8(payload[pos])
            pos += 1
        if fmt & 0x40:
            if pos + 2 > len(payload):
                raise CommonGroundError("truncated PFR compound glyph size")
            sub_size = be16(payload, pos)
            pos += 2
        else:
            if pos >= len(payload):
                raise CommonGroundError("truncated PFR compound glyph size")
            sub_size = payload[pos]
            pos += 1
        if fmt & 0x80:
            if pos + 3 > len(payload):
                raise CommonGroundError("truncated PFR compound glyph offset")
            sub_offset = pfr_u24(payload, pos)
            pos += 3
        else:
            if pos + 2 > len(payload):
                raise CommonGroundError("truncated PFR compound glyph offset")
            sub_offset = be16(payload, pos)
            pos += 2
        commands.extend(
            transform_pfr_commands(
                parse_pfr_glyph_program(metric, sub_offset, sub_size, depth=depth + 1),
                x_scale,
                y_scale,
                x_delta,
                y_delta,
            )
        )
    return commands


def parse_pfr_simple_glyph(payload: bytes) -> list[PfrPathCommand]:
    pos = 0
    if not payload:
        raise CommonGroundError("empty PFR glyph program")
    flags = payload[pos]
    pos += 1
    if flags & 0x80:
        raise CommonGroundError("compound PFR glyph passed to simple parser")
    x_count = 0
    y_count = 0
    if flags & 0x04:
        if pos >= len(payload):
            raise CommonGroundError("truncated PFR glyph xy count")
        count_byte = payload[pos]
        pos += 1
        x_count = count_byte & 0x0F
        y_count = count_byte >> 4
    else:
        if flags & 0x02:
            if pos >= len(payload):
                raise CommonGroundError("truncated PFR glyph x count")
            x_count = payload[pos]
            pos += 1
        if flags & 0x01:
            if pos >= len(payload):
                raise CommonGroundError("truncated PFR glyph y count")
            y_count = payload[pos]
            pos += 1
    control_count = x_count + y_count
    controls: list[int] = []
    current = 0
    mask = 0
    for index in range(control_count):
        if index & 7 == 0:
            if pos >= len(payload):
                raise CommonGroundError("truncated PFR glyph control mask")
            mask = payload[pos]
            pos += 1
        if mask & 1:
            if pos + 2 > len(payload):
                raise CommonGroundError("truncated PFR glyph absolute control")
            current = be16s(payload, pos)
            pos += 2
        else:
            if pos >= len(payload):
                raise CommonGroundError("truncated PFR glyph delta control")
            current += payload[pos]
            pos += 1
        controls.append(current)
        mask >>= 1
    x_controls = controls[:x_count]
    y_controls = controls[x_count:]
    if flags & 0x08:
        _, pos = pfr_extra_items(payload, pos, len(payload))

    commands: list[PfrPathCommand] = []
    current_point = (0.0, 0.0)
    path_open = False

    def close_path() -> None:
        nonlocal path_open
        if path_open:
            commands.append(PfrPathCommand("h"))
            path_open = False

    def read_point(args_format: int, base: tuple[float, float]) -> tuple[tuple[float, float], int]:
        nonlocal pos
        if (args_format & 0x03) == 0:
            if pos >= len(payload):
                raise CommonGroundError("truncated PFR glyph x index")
            index = payload[pos]
            pos += 1
            if index >= x_count:
                raise CommonGroundError("invalid PFR glyph x control index")
            x = float(x_controls[index])
        elif (args_format & 0x03) == 1:
            if pos + 2 > len(payload):
                raise CommonGroundError("truncated PFR glyph x value")
            x = float(be16s(payload, pos))
            pos += 2
        elif (args_format & 0x03) == 2:
            if pos >= len(payload):
                raise CommonGroundError("truncated PFR glyph x delta")
            x = base[0] + pfr_i8(payload[pos])
            pos += 1
        else:
            x = base[0]

        y_format = (args_format >> 2) & 0x03
        if y_format == 0:
            if pos >= len(payload):
                raise CommonGroundError("truncated PFR glyph y index")
            index = payload[pos]
            pos += 1
            if index >= y_count:
                raise CommonGroundError("invalid PFR glyph y control index")
            y = float(y_controls[index])
        elif y_format == 1:
            if pos + 2 > len(payload):
                raise CommonGroundError("truncated PFR glyph y value")
            y = float(be16s(payload, pos))
            pos += 2
        elif y_format == 2:
            if pos >= len(payload):
                raise CommonGroundError("truncated PFR glyph y delta")
            y = base[1] + pfr_i8(payload[pos])
            pos += 1
        else:
            y = base[1]
        return (x, y), pos

    while True:
        if pos >= len(payload):
            raise CommonGroundError("unterminated PFR glyph")
        fmt = payload[pos]
        pos += 1
        high = fmt >> 4
        low = fmt & 0x0F
        points: list[tuple[float, float]] = []
        if high == 0:
            close_path()
            return commands
        if high in (1, 4, 5):
            point, _ = read_point(low, current_point)
            points = [point]
        elif high == 2:
            if low >= x_count:
                raise CommonGroundError("invalid PFR horizontal line control")
            points = [(float(x_controls[low]), current_point[1])]
        elif high == 3:
            if low >= y_count:
                raise CommonGroundError("invalid PFR vertical line control")
            points = [(current_point[0], float(y_controls[low]))]
        else:
            args_count = 3 if high in (6, 7) else 4
            args_format = 0xB8E if high == 6 else (0xE2B if high == 7 else low)
            point_index = 0
            while point_index < args_count:
                point, _ = read_point(args_format, current_point)
                points.append(point)
                current_point = point
                if point_index == 0 and args_count == 4:
                    if pos >= len(payload):
                        raise CommonGroundError("truncated PFR general curve format")
                    args_format = payload[pos]
                    pos += 1
                    args_count = 3
                else:
                    args_format >>= 4
                point_index += 1
        if high in (4, 5):
            close_path()
            commands.append(PfrPathCommand("m", (points[0],)))
            path_open = True
            current_point = points[0]
        elif high in (1, 2, 3):
            if not path_open:
                raise CommonGroundError("PFR line before move")
            commands.append(PfrPathCommand("l", (points[0],)))
            current_point = points[0]
        else:
            if not path_open:
                raise CommonGroundError("PFR curve before move")
            if len(points) != 3:
                raise CommonGroundError("invalid PFR curve point count")
            commands.append(PfrPathCommand("c", tuple(points)))
            current_point = points[-1]


def expand_cpfr_resource(data: bytes) -> bytes:
    if len(data) < 12 or data[:4] != b"\x01\x01\x00\x0c":
        raise CommonGroundError("unsupported CPFR wrapper")
    expanded_size = be32(data, 8)
    payload = data[12:]
    if len(payload) == expanded_size:
        pfr = payload
    else:
        pfr = dpl2_lzss_decode(payload, expanded_size)
    if pfr[:4] != b"PFR0":
        raise CommonGroundError("CPFR resource did not expand to PFR0")
    return pfr


def parse_pfr0_metrics(data: bytes) -> dict[str, PfrFontMetrics]:
    if len(data) < 54 or data[:4] != b"PFR0":
        raise CommonGroundError("not a supported PFR0 resource")
    version = be16(data, 4)
    signature2 = be16(data, 6)
    header_size = be16(data, 8)
    if version not in (1, 3, 4) or signature2 != 0x0D0A or header_size not in (43, 54, 58):
        raise CommonGroundError("unsupported PFR0 header")
    log_dir_offset = be16(data, 12)
    if log_dir_offset + 2 > len(data):
        raise CommonGroundError("truncated PFR logical directory")
    log_count = be16(data, log_dir_offset)
    log_entries_end = log_dir_offset + 2 + log_count * 5
    if log_entries_end > len(data):
        raise CommonGroundError("truncated PFR logical directory entries")
    gps_section_offset = pfr_u24(data, 35)

    fonts: dict[str, PfrFontMetrics] = {}
    for index in range(log_count):
        entry = log_dir_offset + 2 + index * 5
        log_size = be16(data, entry)
        log_offset = pfr_u24(data, entry + 2)
        log_end = log_offset + log_size
        if log_offset + 18 > len(data) or log_end > len(data):
            raise CommonGroundError("truncated PFR logical font")
        matrix = tuple(pfr_s24(data, log_offset + component * 3) for component in range(4))
        logical_size_half_points = round(abs(matrix[0]) / 512) if matrix[0] else None
        pos = log_offset + 12  # 4 signed 24-bit matrix values
        flags = data[pos]
        pos += 1
        if flags & 0x04:  # PFR_LOG_STROKE
            pos += 2 if flags & 0x08 else 1
            if (flags & 0x03) == 0:
                pos += 3
        if flags & 0x10:  # PFR_LOG_BOLD
            pos += 2 if flags & 0x20 else 1
        if flags & 0x40:
            _, pos = pfr_extra_items(data, pos, log_end)
        if pos + 5 > log_end:
            raise CommonGroundError("truncated PFR physical-font pointer")
        phys_size = be16(data, pos)
        phys_offset = pfr_u24(data, pos + 2)
        pos += 5
        if header_size >= 58:
            if pos >= log_end:
                raise CommonGroundError("truncated PFR large physical-font size")
            phys_size += data[pos] << 16

        phys_end = phys_offset + phys_size
        if phys_offset + 15 > len(data) or phys_end > len(data):
            raise CommonGroundError("truncated PFR physical font")
        p = phys_offset
        p += 2  # font reference number
        outline_resolution = be16(data, p)
        metrics_resolution = be16(data, p + 2)
        p += 4
        bbox = (be16s(data, p), be16s(data, p + 2), be16s(data, p + 4), be16s(data, p + 6))
        p += 8
        phys_flags = data[p]
        p += 1
        standard_advance: int | None = None
        if not (phys_flags & 0x04):
            if p + 2 > phys_end:
                raise CommonGroundError("truncated PFR standard advance")
            standard_advance = be16s(data, p)
            p += 2

        font_id: str | None = None
        if phys_flags & 0x80:
            items, p = pfr_extra_items(data, p, phys_end)
            for item_type, payload in items:
                if item_type == 2:
                    font_id = payload.rstrip(b"\x00").decode("ascii", "replace")
                    break

        if p + 3 > phys_end:
            raise CommonGroundError("truncated PFR auxiliary data size")
        aux_size = pfr_u24(data, p)
        p += 3 + aux_size
        if p > phys_end:
            raise CommonGroundError("truncated PFR auxiliary data")
        if p >= phys_end:
            continue
        blue_count = data[p]
        p += 1 + blue_count * 2
        if p + 8 > phys_end:
            raise CommonGroundError("truncated PFR character table header")
        p += 6  # blue_fuzz, blue_scale, vertical standard, horizontal standard
        char_count = be16(data, p)
        p += 2

        advances: dict[int, int] = {}
        glyph_programs: dict[int, tuple[int, int]] = {}
        for _ in range(char_count):
            if p >= phys_end:
                raise CommonGroundError("truncated PFR character descriptor")
            if phys_flags & 0x02:
                if p + 2 > phys_end:
                    raise CommonGroundError("truncated PFR two-byte char code")
                char_code = be16(data, p)
                p += 2
            else:
                char_code = data[p]
                p += 1
            if phys_flags & 0x04:
                if p + 2 > phys_end:
                    raise CommonGroundError("truncated PFR proportional advance")
                advance = be16s(data, p)
                p += 2
            else:
                advance = standard_advance if standard_advance is not None else 0
            if phys_flags & 0x08:
                p += 1
            if phys_flags & 0x10:
                glyph_size = be16(data, p)
                p += 2
            else:
                glyph_size = data[p]
                p += 1
            if phys_flags & 0x20:
                glyph_offset = pfr_u24(data, p)
                p += 3
            else:
                glyph_offset = be16(data, p)
                p += 2
            if p > phys_end:
                raise CommonGroundError("truncated PFR glyph-program pointer")
            advances[char_code] = advance
            glyph_programs[char_code] = (glyph_size, glyph_offset)

        if metrics_resolution > 0:
            metric_id = font_id or f"\x00unnamed:{index}"
            fonts[metric_id.lower()] = PfrFontMetrics(
                metric_id,
                metrics_resolution,
                outline_resolution,
                bbox,
                advances,
                glyph_programs,
                gps_section_offset,
                data,
                logical_size_half_points,
                index,
                phys_offset,
            )
    return fonts


def dpl2_pfr_metrics(body: bytes, trailer: bytes, *, include_unnamed: bool = False) -> dict[str, PfrFontMetrics]:
    metrics: dict[str, PfrFontMetrics] = {}
    for ref in parse_dpl2_resource_map(body, trailer):
        if ref.resource_type != "CPFR":
            continue
        metrics.update(parse_pfr0_metrics(expand_cpfr_resource(ref.data)))
    unnamed = [metric for key, metric in metrics.items() if key.startswith("\x00unnamed:") and metric.advances]
    if unnamed:
        active_fonts: set[str] = set()
        for _, record in iter_dpl2_records(body):
            if len(record) < 16 or record[8:10] != b"\x00\x81":
                continue
            for event in dpl2_pict_draw_events(expand_dpl2_display_record(record)):
                if isinstance(event, PictTextEvent) and event.style.font_name:
                    font_name = event.style.font_name.lower()
                    if font_name not in metrics and font_name not in ("symbol", "mathematicalpi-six"):
                        active_fonts.add(font_name)
        if len(active_fonts) == 1:
            inferred_name = next(iter(active_fonts))
            inferred_metric = max(unnamed, key=lambda metric: len(metric.advances))
            metrics[inferred_name] = PfrFontMetrics(
                inferred_name,
                inferred_metric.metrics_resolution,
                inferred_metric.outline_resolution,
                inferred_metric.bbox,
                inferred_metric.advances,
                inferred_metric.glyph_programs,
                inferred_metric.gps_section_offset,
                inferred_metric.pfr_data,
                inferred_metric.logical_size_half_points,
                inferred_metric.logical_index,
                inferred_metric.logical_physical_offset,
            )
    if include_unnamed:
        return metrics
    return {key: metric for key, metric in metrics.items() if not key.startswith("\x00unnamed:")}


def infer_dpl2_pfr_style_metrics(
    body: bytes,
    metrics: dict[str, PfrFontMetrics],
    size_mapper: Callable[[int], int] | None = None,
) -> dict[tuple[str, int], PfrFontMetrics]:
    if size_mapper is None:
        size_mapper = cgdc_size_to_half_points
    unnamed = [(key, metric) for key, metric in metrics.items() if key.startswith("\x00unnamed:") and metric.advances and metric.glyph_programs]
    if not unnamed:
        return {}

    text_by_style: dict[tuple[str, int, int], dict[int, int]] = {}
    for _, record in iter_dpl2_records(body):
        if len(record) < 16 or record[8:10] != b"\x00\x81":
            continue
        for event in dpl2_pict_draw_events(expand_dpl2_display_record(record), size_mapper=size_mapper):
            if not isinstance(event, PictTextEvent) or not event.style.font_name:
                continue
            font_name = event.style.font_name.lower()
            if font_name in metrics or font_name in ("symbol", "mathematicalpi-six", "futurabookfractions"):
                continue
            key = (font_name, pdf_font_emphasis(event.style), event.style.size_half_points)
            counter = text_by_style.setdefault(key, {})
            for byte in event.text.encode("mac_roman", "replace"):
                counter[byte] = counter.get(byte, 0) + 1

    grouped: dict[tuple[str, int], list[tuple[int, dict[int, int]]]] = {}
    for (font_name, emphasis, size), counter in text_by_style.items():
        grouped.setdefault((font_name, emphasis), []).append((size, counter))

    assigned: dict[tuple[str, int], PfrFontMetrics] = {}
    used_physical_offsets: set[int] = set()
    for style_key, size_counters in sorted(grouped.items(), key=lambda item: -sum(sum(counter.values()) for _, counter in item[1])):
        best: tuple[int, int, int, int, str, PfrFontMetrics] | None = None
        for metric_key, metric in unnamed:
            coverage = 0
            matched_size_coverage = 0
            unique_coverage = 0
            for size, counter in size_counters:
                style_coverage = sum(count for byte, count in counter.items() if byte in metric.advances)
                coverage += style_coverage
                unique_coverage += sum(1 for byte in counter if byte in metric.advances)
                if metric.logical_size_half_points == size:
                    matched_size_coverage += style_coverage
            if coverage <= 0:
                continue
            reuse_penalty = 1 if metric.logical_physical_offset in used_physical_offsets else 0
            rank = (coverage, matched_size_coverage, unique_coverage, -reuse_penalty, metric_key, metric)
            if best is None or rank[:5] > best[:5]:
                best = rank
        if best is None:
            continue
        chosen = best[5]
        if best[0] == sum(sum(counter.values()) for _, counter in size_counters):
            assigned[style_key] = PfrFontMetrics(
                f"{style_key[0]}:{style_key[1]}",
                chosen.metrics_resolution,
                chosen.outline_resolution,
                chosen.bbox,
                chosen.advances,
                chosen.glyph_programs,
                chosen.gps_section_offset,
                chosen.pfr_data,
                chosen.logical_size_half_points,
                chosen.logical_index,
                chosen.logical_physical_offset,
            )
            if chosen.logical_physical_offset is not None:
                used_physical_offsets.add(chosen.logical_physical_offset)
    return assigned


def expand_dpl2_display_record(record: bytes) -> bytes:
    if len(record) < 20 or record[8:10] != b"\x00\x81":
        raise CommonGroundError("not a DPL2 display record")
    payload = record[16:]
    if len(payload) < 4:
        raise CommonGroundError("truncated DPL2 display payload")
    stream_flags = payload[0]
    stream_size = int.from_bytes(payload[1:4], "big")
    if stream_flags not in (0x20, 0x40):
        raise CommonGroundError("invalid DPL2 display payload header")
    expanded_size = be32(record, 12)
    marker = payload.find(b"\xfe\xed\xf1")
    if marker < 0 and expanded_size == len(payload) - 4:
        return payload[4:]

    if marker >= 0:
        if marker < 4 or (marker - 4) % 2:
            raise CommonGroundError("invalid DPL2 display chunk table")
        chunk_sizes = [stream_size]
        for pos in range(4, marker, 2):
            chunk_sizes.append(be16(payload, pos))
        compressed = payload[marker:]
        if sum(chunk_sizes) != len(compressed):
            raise CommonGroundError("DPL2 display chunk size table mismatch")
        chunk_unit = 8192 if stream_flags == 0x20 else 16384
        chunks: list[bytes] = []
        pos = 0
        for index, chunk_size in enumerate(chunk_sizes):
            stored = compressed[pos : pos + chunk_size]
            pos += chunk_size
            chunk = stored if chunk_size == chunk_unit else dpl2_lzss_decode_all(stored)
            if len(chunk) > chunk_unit:
                raise CommonGroundError("DPL2 display chunk overexpanded")
            if index + 1 < len(chunk_sizes) and len(chunk) != chunk_unit:
                raise CommonGroundError("DPL2 display chunk underexpanded")
            chunks.append(chunk)
        expanded = b"".join(chunks)
        if len(expanded) != expanded_size:
            raise CommonGroundError("DPL2 display expanded-size mismatch")
        return expanded

    if stream_size == len(payload) - 4:
        return dpl2_lzss_decode(payload[4:], expanded_size)
    if marker < 0:
        raise CommonGroundError("DPL2 display payload has no LZSS stream marker")
    raise CommonGroundError("unsupported DPL2 display payload layout")


def expand_dpl2_resource_records(body: bytes) -> list[tuple[int, bytes, bytes]]:
    """Return expanded DPL2 class 0x0001 resource records.

    The returned tuples contain the original body offset, record header, and
    expanded payload. Non-resource records are deliberately not returned here:
    class 0x0081 display records are not LZSS streams, even when their size
    field differs from the stored payload length by a few bytes.
    """
    expanded: list[tuple[int, bytes, bytes]] = []
    for record_offset, record in iter_dpl2_records(body):
        if len(record) < 16 or record[8:10] != b"\x00\x01":
            continue
        expected_size = be32(record, 12)
        payload = record[16:]
        if expected_size == len(payload):
            data = payload
        else:
            data = dpl2_lzss_decode(payload, expected_size)
        expanded.append((record_offset, record[:16], data))
    return expanded


def parse_dpl2_resource_map(body: bytes, trailer: bytes) -> list[Dpl2ResourceRef]:
    if len(trailer) < 30:
        raise CommonGroundError("truncated DPL2 resource map")
    data_offset = be32(trailer, 0)
    map_offset = be32(trailer, 4)
    data_length = be32(trailer, 8)
    map_length = be32(trailer, 12)
    if data_offset != 24 or data_length != len(body) or map_offset != data_offset + data_length:
        raise CommonGroundError("invalid DPL2 resource-map header")
    if map_length != len(trailer):
        raise CommonGroundError("DPL2 resource-map length mismatch")
    if trailer[16:24] != b"\x00" * 8:
        raise CommonGroundError("unsupported DPL2 resource-map attributes")
    type_list_offset = be16(trailer, 24)
    name_list_offset = be16(trailer, 26)
    if type_list_offset + 2 > len(trailer):
        raise CommonGroundError("truncated DPL2 resource type list")
    type_count = be16(trailer, type_list_offset) + 1
    type_entries_start = type_list_offset + 2
    type_entries_end = type_entries_start + type_count * 8
    if type_entries_end > len(trailer):
        raise CommonGroundError("truncated DPL2 resource type entries")

    refs: list[Dpl2ResourceRef] = []
    for index in range(type_count):
        entry = type_entries_start + index * 8
        resource_type = trailer[entry : entry + 4].decode("mac_roman", "replace")
        ref_count = be16(trailer, entry + 4) + 1
        ref_list_offset = be16(trailer, entry + 6)
        ref_list_start = type_list_offset + ref_list_offset
        ref_list_end = ref_list_start + ref_count * 12
        if ref_list_start < type_entries_end or ref_list_end > len(trailer):
            raise CommonGroundError("invalid DPL2 resource reference list")
        for ref_index in range(ref_count):
            ref = ref_list_start + ref_index * 12
            resource_id = be16s(trailer, ref)
            name_offset = be16s(trailer, ref + 2)
            attributes = trailer[ref + 4]
            data_record_offset = int.from_bytes(trailer[ref + 5 : ref + 8], "big")
            if name_offset != -1:
                if name_list_offset == 0 or name_list_offset + name_offset >= len(trailer):
                    raise CommonGroundError("invalid DPL2 resource name offset")
            if attributes != 0:
                raise CommonGroundError("unsupported DPL2 resource attributes")
            if data_record_offset + 4 > len(body):
                raise CommonGroundError("DPL2 resource data offset outside body")
            data_size = be32(body, data_record_offset)
            data_start = data_record_offset + 4
            data_end = data_start + data_size
            if data_end > len(body):
                raise CommonGroundError("truncated DPL2 resource data")
            refs.append(Dpl2ResourceRef(resource_type, resource_id, attributes, data_record_offset, body[data_start:data_end]))
    return refs


DPL2_PAGE_RESOURCE_TAGS = (
    b"BASE",
    b"CBTS",
    b"CLUT",
    b"CNMS",
    b"CPFR",
    b"CPIC",
    b"CRCT",
    b"CTYP",
)


def expand_dpl2_resource_ref(ref: Dpl2ResourceRef) -> bytes:
    if len(ref.data) < 12 or ref.data[:4] != b"\x01\x01\x00\x0c":
        return ref.data
    if ref.data[4:6] != b"\x00\x01":
        return ref.data
    expected_size = be32(ref.data, 8)
    payload = ref.data[12:]
    if expected_size == len(payload):
        return payload
    return dpl2_lzss_decode(payload, expected_size)


def parse_dpl2_page_graph(refs: list[Dpl2ResourceRef]) -> dict[int, Dpl2PageGraphEntry]:
    known_refs = {(ref.resource_type, ref.resource_id) for ref in refs}
    page_graph: dict[int, Dpl2PageGraphEntry] = {}
    for ref in sorted((item for item in refs if item.resource_type == "PAGE"), key=lambda item: item.resource_id):
        page_data = expand_dpl2_resource_ref(ref)
        if len(page_data) < 20:
            raise CommonGroundError("truncated DPL2 PAGE graph record")
        top = be16(page_data, 12)
        left = be16(page_data, 14)
        bottom = be16(page_data, 16)
        right = be16(page_data, 18)
        bounds: tuple[float, float, float, float] | None
        if left == top == right == bottom == 0:
            bounds = None
        elif bottom >= top and right >= left:
            bounds = (float(left), float(top), float(right), float(bottom))
        else:
            raise CommonGroundError("invalid DPL2 PAGE graph bounds")

        table_start = page_data.find(b"BASE")
        if table_start < 0:
            continue
        positioned_refs: list[tuple[int, str, int, int, int]] = []
        pos = table_start
        known_tag_values = set(DPL2_PAGE_RESOURCE_TAGS)
        while pos + 10 <= len(page_data):
            tag = page_data[pos : pos + 4]
            if tag not in known_tag_values:
                raise CommonGroundError("unsupported DPL2 PAGE graph edge tag")
            resource_type = tag.decode("ascii")
            resource_id = be16(page_data, pos + 4)
            variant = be16(page_data, pos + 6)
            edge_code = be16(page_data, pos + 8)
            if (resource_type, resource_id) not in known_refs:
                raise CommonGroundError(f"DPL2 PAGE graph references missing {resource_type} {resource_id}")
            positioned_refs.append((pos, resource_type, resource_id, variant, edge_code))
            pos += 10
        if pos != len(page_data):
            raise CommonGroundError("trailing bytes in DPL2 PAGE graph edge table")
        resource_refs = tuple((resource_type, resource_id) for _, resource_type, resource_id, _, _ in positioned_refs)
        base_ids = tuple(resource_id for resource_type, resource_id in resource_refs if resource_type == "BASE")
        if len(set(base_ids)) > 1:
            raise CommonGroundError("DPL2 PAGE graph references multiple BASE resources")
        base_id = base_ids[0] if base_ids else None
        cpic_refs = tuple(
            (resource_id, variant, edge_code)
            for _, resource_type, resource_id, variant, edge_code in positioned_refs
            if resource_type == "CPIC"
        )
        cbts_refs = tuple(
            (resource_id, variant, edge_code)
            for _, resource_type, resource_id, variant, edge_code in positioned_refs
            if resource_type == "CBTS"
        )
        crct_refs = tuple(
            (resource_id, variant, edge_code)
            for _, resource_type, resource_id, variant, edge_code in positioned_refs
            if resource_type == "CRCT"
        )
        cpic_ids = tuple(resource_id for resource_id, _, _ in cpic_refs)
        crct_ids = tuple(resource_id for resource_id, _, _ in crct_refs)
        if base_id is not None and base_id in page_graph:
            raise CommonGroundError("DPL2 PAGE graph has duplicate BASE bindings")
        if base_id is not None:
            page_graph[base_id] = Dpl2PageGraphEntry(
                page_id=ref.resource_id,
                base_id=base_id,
                bounds=bounds,
                cbts_refs=cbts_refs,
                crct_refs=crct_refs,
                cpic_refs=cpic_refs,
                cpic_ids=cpic_ids,
                crct_ids=crct_ids,
                resource_refs=resource_refs,
            )
    return page_graph


def dpl2_logical_page_count(refs: list[Dpl2ResourceRef]) -> int | None:
    counts = [be16(ref.data, 0) for ref in refs if ref.resource_type == "LLFL" and len(ref.data) == 2]
    if not counts:
        return None
    if len(set(counts)) != 1:
        raise CommonGroundError("conflicting DPL2 logical page counts")
    return counts[0]


def dpl2_cpic_payload(ref: Dpl2ResourceRef) -> bytes:
    if len(ref.data) < 12 or ref.data[:4] != b"\x01\x01\x00\x0c":
        raise CommonGroundError("unsupported DPL2 CPIC wrapper")
    expected_size = be32(ref.data, 8)
    payload = ref.data[12:]
    if ref.data[4:6] == b"\x00\x00":
        if expected_size != len(payload):
            raise CommonGroundError("DPL2 CPIC uncompressed size mismatch")
        return payload
    if ref.data[4:6] == b"\x00\x01":
        if expected_size == len(payload):
            return payload
        return dpl2_lzss_decode(payload, expected_size)
    raise CommonGroundError("unsupported DPL2 CPIC record class")


def dpl2_cpic_number(value: int) -> float:
    if value & 0x80000000:
        value -= 0x100000000
    if -0x10000 < value < 0x10000:
        return float(value)
    return value / 256.0


def decode_dpl2_cpic_point(data: bytes, pos: int) -> tuple[tuple[float, float] | None, int]:
    if pos >= len(data) or data[pos] != 0x80:
        return None, pos
    if pos + 5 > len(data):
        raise CommonGroundError("truncated DPL2 CPIC fixed coordinate")
    x = dpl2_cpic_number(be32(data, pos + 1))
    pos += 5
    if pos < len(data) and data[pos] == 0x80:
        if pos + 5 > len(data):
            raise CommonGroundError("truncated DPL2 CPIC fixed coordinate pair")
        y = dpl2_cpic_number(be32(data, pos + 1))
        pos += 5
        return (x, y), pos
    return None, pos


def decode_dpl2_cpic_coord(data: bytes, pos: int) -> tuple[float | None, int]:
    if pos >= len(data) or data[pos] != 0x80:
        return None, pos
    if pos + 5 > len(data):
        raise CommonGroundError("truncated DPL2 CPIC fixed coordinate")
    value = dpl2_cpic_number(be32(data, pos + 1))
    return value, pos + 5


def dpl2_cpic_draw_events(
    ref: Dpl2ResourceRef,
    bounds: tuple[float, float, float, float] | None,
    resolution: int,
    target_dpi: int,
) -> list[PictVectorEvent]:
    if bounds is None:
        return []
    payload = dpl2_cpic_payload(ref)
    if len(payload) <= 2:
        return []
    left, top, _, _ = bounds
    pos = 2
    current_path: list[tuple[int, int]] = []
    paths: list[list[tuple[int, int]]] = []
    current_point: tuple[float, float] | None = None

    def flush_path() -> None:
        nonlocal current_path
        if len(current_path) >= 2:
            paths.append(current_path)
        current_path = []

    def to_page_point(point: tuple[float, float]) -> tuple[int, int]:
        x, y = point
        scale = target_dpi / resolution
        return int(round(left + x * scale)), int(round(top + y * scale))

    clip = PictClipRegion(tuple(int(round(value)) for value in bounds))

    def path_visible_in_clip(path: list[tuple[int, int]]) -> bool:
        xs = [x for x, _ in path]
        ys = [y for _, y in path]
        path_left, path_top, path_right, path_bottom = min(xs), min(ys), max(xs), max(ys)
        clip_left, clip_top, clip_right, clip_bottom = clip.bounds
        return min(path_right, clip_right) >= max(path_left, clip_left) and min(path_bottom, clip_bottom) >= max(path_top, clip_top)

    while pos < len(payload):
        op = payload[pos]
        pos += 1
        low = op & 0x3F
        closes = bool(op & 0x40)
        if low == 0:
            flush_path()
            current_point = None
            continue
        if low in (1, 4, 5, 7, 9, 10, 12, 30):
            while pos < len(payload) and payload[pos] != 0x80:
                # These bytes are compact path-format/style selectors. The
                # visible coordinate payload begins at the 0x80 fixed-point tag.
                pos += 1
            point, pos = decode_dpl2_cpic_point(payload, pos)
            if point is not None:
                flush_path()
                current_path = [to_page_point(point)]
                current_point = point
            if closes:
                flush_path()
                current_point = None
            continue
        if low in (2, 3):
            coord, pos = decode_dpl2_cpic_coord(payload, pos)
            if coord is not None and current_point is not None:
                if low == 2:
                    point = (coord, current_point[1])
                else:
                    point = (current_point[0], coord)
                if not current_path:
                    current_path = [to_page_point(current_point)]
                current_path.append(to_page_point(point))
                current_point = point
            if closes:
                flush_path()
                current_point = None
            continue
        if low in (2, 6):
            point, pos = decode_dpl2_cpic_point(payload, pos)
            if point is not None:
                if not current_path:
                    current_path = [to_page_point(point)]
                else:
                    current_path.append(to_page_point(point))
                current_point = point
            if closes:
                flush_path()
                current_point = None
            continue
        # Unknown compact drawing opcodes in the CPIC stream fail fast rather
        # than silently dropping visible content.
        raise CommonGroundError(f"unsupported DPL2 CPIC opcode 0x{op:02x}")
    flush_path()
    return [
        PictVectorEvent(ref.data_offset, "polygon", tuple(path), False, (0, 0, 0), 1, clip)
        for path in paths
        if len(path) >= 2 and any(first != second for first, second in zip(path, path[1:])) and path_visible_in_clip(path)
    ]


def dpl2_nonvisual_cpic_label(events: list[PictTextEvent | PictImageEvent | PictVectorEvent]) -> bool:
    text_events = [event for event in events if isinstance(event, PictTextEvent)]
    if len(text_events) != 1 or len(text_events) != len(events):
        return False
    text = text_events[0].text.strip()
    return bool(re.fullmatch(r"[a-z][a-z0-9_-]{0,31}", text))


def validate_dpl2_body_byte_coverage(body: bytes, refs: list[Dpl2ResourceRef]) -> list[str]:
    coverage = bytearray(len(body))
    for offset, record in iter_dpl2_records(body):
        end = offset + len(record)
        coverage[offset:end] = b"\x01" * len(record)
    for ref in refs:
        data_size = be32(body, ref.data_offset)
        end = ref.data_offset + 4 + data_size
        for index in range(ref.data_offset, end):
            coverage[index] |= 0x02

    labels: list[str] = []
    pos = 0
    while pos < len(body):
        if coverage[pos] != 0:
            pos += 1
            continue
        start = pos
        while pos < len(body) and coverage[pos] == 0:
            pos += 1
        gap = body[start:pos]
        if len(gap) == 10 and re.fullmatch(rb"\d\d \(Page 1", gap):
            labels.append(gap.decode("ascii"))
            continue
        raise CommonGroundError("unaccounted DPL2 body bytes")
    return labels


def dpl2_page_geometry(body: bytes) -> tuple[int, int, int, int]:
    for _, record in iter_dpl2_records(body):
        if len(record) < 34 or record[8:10] != b"\x00\x00":
            continue
        payload = record[16:]
        if len(payload) != 18:
            continue
        if payload[:8] != b"\x00\x01\x00\x01\x00\x00\x00\x00":
            continue
        width = be16(payload, 8)
        height = be16(payload, 10)
        dpi_x = be16(payload, 12)
        dpi_y = be16(payload, 14)
        scale_percent = be16(payload, 16)
        if width <= 0 or height <= 0 or dpi_x <= 0 or dpi_y <= 0 or scale_percent <= 0:
            raise CommonGroundError("invalid DPL2 page geometry")
        return width, height, dpi_x, dpi_y
    for _, record in iter_dpl2_records(body):
        if len(record) < 16 or record[8:10] != b"\x00\x81":
            continue
        record_data = expand_dpl2_display_record(record)
        if len(record_data) >= 8:
            height = be16(record_data, 4)
            width = be16(record_data, 6)
            if width > 0 and height > 0:
                return width, height, 300, 300
    raise CommonGroundError("DPL2 page geometry record not found")


def dpl2_has_explicit_page_geometry(body: bytes) -> bool:
    for _, record in iter_dpl2_records(body):
        if len(record) < 34 or record[8:10] != b"\x00\x00":
            continue
        payload = record[16:]
        if len(payload) == 18 and payload[:8] == b"\x00\x01\x00\x01\x00\x00\x00\x00":
            return True
    return False


def dpl2_size_mapper_for_body(body: bytes) -> Callable[[int], int]:
    if dpl2_has_explicit_page_geometry(body):
        return cgdc_size_to_half_points
    return dpl2_direct_size_to_units


def dpl2_base_metadata(data: bytes) -> tuple[float, float, float, float, int, int] | None:
    if len(data) < 44 or data[:4] != b"\x00\x00\x00\x22":
        return None
    base_pos = data.find(b"BASE", 40)
    if base_pos < 0 or base_pos + 8 > len(data):
        return None
    top = be16(data, 12)
    left = be16(data, 14)
    bottom = be16(data, 16)
    right = be16(data, 18)
    if bottom < top or right < left:
        return None
    base_id = be16(data, base_pos + 4)
    base_variant = be16(data, base_pos + 6)
    return float(left), float(top), float(right), float(bottom), base_id, base_variant


def scan_dpl2_text_fragments(body: bytes) -> list[TextFragment]:
    fragments: list[TextFragment] = []
    size_mapper = dpl2_size_mapper_for_body(body)
    for record_offset, record in iter_dpl2_records(body):
        # DPL2 record class 0x0081 contains visible text drawing streams. Other
        # record classes include PFR/TrueDoc fonts, resource directories, and
        # bitmap/vector payloads that can contain bytes resembling text opcodes.
        if len(record) < 16 or record[8:10] != b"\x00\x81":
            continue
        record_data = expand_dpl2_display_record(record)
        for event in dpl2_pict_text_events(record_data, size_mapper=size_mapper):
            fragments.append(
                TextFragment(
                    offset=record_offset + event.offset,
                    op=0x28,
                    data=event.text.encode("mac_roman", "replace"),
                    y=event.y,
                    x=event.x,
                    style=event.style,
                )
            )
    return fragments


def plausible_text_bytes(text: bytes, *, dpl2: bool, op: int | None = None) -> bool:
    if not text:
        return False
    if not dpl2 and len(text) == 1 and chr(text[0]) in " .,;:!?-'\"()/":
        return op == 0x29
    if not dpl2 and len(text) == 1 and text[0] == 0xD0:
        return True
    if len(text) == 1 and text[0] < 0x80 and not chr(text[0]).isalnum():
        return False
    if dpl2:
        decoded = decode_dpl2_ascii(text)
        if len(decoded.strip()) < 2:
            return False
        expected = sum(1 for c in decoded if c.isalnum() or c in " \t.,;:!?-+/()'\"&%")
        noisy = sum(1 for c in decoded if c in "{}[]\\|_@#$^~=<>")
        return expected / len(decoded) >= 0.72 and noisy / len(decoded) <= 0.18
    bad_controls = sum(1 for c in text if c < 32 and c not in (9, 10, 13))
    return bad_controls == 0


def plausible_pict_text_record(text: bytes, *, op: int) -> bool:
    if plausible_text_bytes(text, dpl2=False, op=op):
        return True
    if len(text) == 1 and chr(text[0]) in " .,;:!?-'\"()/":
        return op in (0x28, 0x29)
    # QuickDraw text records are stateful: even a blank LongText/DHText can set
    # the current text point for following continuation records.
    return bool(text) and all(c in (0x00, 0x09, 0x0A, 0x0D, 0x20) for c in text)


def visible_pict_text(text: str) -> bool:
    return bool(text.replace("\x00", "").strip())


def pict_text_payload_ok(text: bytes) -> bool:
    return bool(text) and all(byte >= 32 or byte in (9, 10, 13) for byte in text)


def emit_pict_text(op: int, text: str) -> bool:
    text = text.replace("\x00", "")
    if op == 0x28:
        return bool(text.strip())
    return bool(text)


def quicktime_fallback_text(text: str) -> bool:
    normalized = " ".join(text.replace("\r", " ").replace("\n", " ").split())
    return normalized in {
        "QuickTime™ and a",
        "Photo - JPEG decompressor",
        "are needed to see this picture",
    }


def point_in_rect(x: float, y: int, rect: tuple[int, int, int, int] | None) -> bool:
    if rect is None:
        return False
    left, top, right, bottom = rect
    return left <= x <= right and top <= y <= bottom


def cgdc_size_to_half_points(size: int) -> int:
    if size <= 0:
        return 22
    # Some CGDC streams use familiar point-size values here (12, 14, 18).
    # Others use larger device-size values; scale those back to half-points.
    if size <= 24:
        return max(12, min(72, size * 2))
    return max(12, min(72, round(size / 2)))


def dpl2_direct_size_to_units(size: int) -> int:
    if size <= 0:
        return 22
    return max(4, min(160, size))


def pict_fixed_16_16(data: bytes, offset: int) -> float:
    return struct.unpack_from(">i", data, offset)[0] / 65536.0


def apply_cgdc_style_control(
    body: bytes,
    offset: int,
    style: StyleState,
    font_names: dict[int, str] | None = None,
    size_mapper: Callable[[int], int] = cgdc_size_to_half_points,
) -> tuple[StyleState, int] | None:
    if offset + 2 > len(body) or body[offset] != 0:
        return None
    op = body[offset + 1]
    if op == 0x03 and offset + 4 <= len(body):
        font_id = be16(body, offset + 2)
        font_name = font_names.get(font_id) if font_names is not None else style.font_name
        return replace(style, font_id=font_id, font_name=font_name), offset + 4
    if op == 0x04 and offset + 4 <= len(body) and body[offset + 3] == 0:
        selector = body[offset + 2]
        emphasis = selector if selector in (0, 1, 2, 3) else style.emphasis
        return replace(style, emphasis=emphasis), offset + 4
    if op == 0x06 and offset + 6 <= len(body):
        return replace(style, space_extra=pict_fixed_16_16(body, offset + 2)), offset + 6
    if op == 0x0D and offset + 4 <= len(body) and body[offset + 2] == 0:
        return replace(style, size_half_points=size_mapper(body[offset + 3])), offset + 4
    if op == 0x10 and offset + 10 <= len(body):
        numerator = pict_fixed_16_16(body, offset + 2)
        denominator = pict_fixed_16_16(body, offset + 6)
        if denominator != 0:
            ratio = numerator / denominator
            if 0.1 <= ratio <= 10.0:
                return replace(style, tx_ratio=ratio), offset + 10
    if op == 0x16 and offset + 6 <= len(body):
        return replace(style, char_extra=pict_fixed_16_16(body, offset + 2)), offset + 6
    if op == 0x1A and offset + 8 <= len(body):
        red16 = be16(body, offset + 2)
        green16 = be16(body, offset + 4)
        blue16 = be16(body, offset + 6)
        if red16 == green16 == blue16 == 0:
            color = None
        else:
            color = (red16 >> 8, green16 >> 8, blue16 >> 8)
        return replace(style, color=color), offset + 8
    if op == 0x1B and offset + 8 <= len(body):
        red16 = be16(body, offset + 2)
        green16 = be16(body, offset + 4)
        blue16 = be16(body, offset + 6)
        return replace(style, background_color=(red16 >> 8, green16 >> 8, blue16 >> 8)), offset + 8
    if op == 0x2C and offset + 7 <= len(body):
        payload_len = be16(body, offset + 2)
        end = offset + 4 + payload_len
        if payload_len >= 3 and end <= len(body):
            font_id = be16(body, offset + 4)
            name_len = body[offset + 6]
            name_start = offset + 7
            name_end = name_start + name_len
            if name_end <= end:
                font_name = body[name_start:name_end].decode("mac_roman", "replace")
                if font_names is not None:
                    font_names[font_id] = font_name
                if style.font_id == font_id:
                    return replace(style, font_name=font_name), end
                return style, end
    return None


def packbits_decode_row(encoded: bytes, row_bytes: int) -> bytes | None:
    decoded = packbits_decode_units(encoded, 1, row_bytes)
    return decoded


def packbits_decode_units(encoded: bytes, unit_size: int, expected_size: int) -> bytes | None:
    out = bytearray()
    i = 0
    while i < len(encoded):
        control = struct.unpack("b", encoded[i : i + 1])[0]
        i += 1
        if 0 <= control <= 127:
            count = (control + 1) * unit_size
            if i + count > len(encoded):
                return None
            out.extend(encoded[i : i + count])
            i += count
        elif -127 <= control <= -1:
            count = (1 - control) * unit_size
            if i + unit_size > len(encoded):
                return None
            out.extend(encoded[i : i + unit_size] * (1 - control))
            i += unit_size
        else:
            pass
    if len(out) != expected_size:
        return None
    return bytes(out)


def packbits_decode_units_loose(encoded: bytes, unit_size: int, expected_size: int) -> bytes:
    out = bytearray()
    i = 0
    while i < len(encoded) and len(out) < expected_size:
        control = struct.unpack("b", encoded[i : i + 1])[0]
        i += 1
        if 0 <= control <= 127:
            count = (control + 1) * unit_size
            available = min(count, len(encoded) - i, expected_size - len(out))
            out.extend(encoded[i : i + available])
            i += count
        elif -127 <= control <= -1:
            if i + unit_size > len(encoded):
                break
            out.extend(encoded[i : i + unit_size] * min(1 - control, (expected_size - len(out) + unit_size - 1) // unit_size))
            if len(out) > expected_size:
                del out[expected_size:]
            i += unit_size
        else:
            pass
    if len(out) < expected_size:
        out.extend(b"\x00" * (expected_size - len(out)))
    return bytes(out)


def parse_cgdc_bitmap(body: bytes, offset: int, style: StyleState) -> tuple[TextFragment, int] | None:
    if offset + 32 > len(body) or body[offset] != 0 or body[offset + 1] not in (0x90, 0x91, 0x98, 0x99):
        return None
    op = body[offset + 1]
    row_word = be16(body, offset + 2)
    if row_word & 0x8000:
        if op not in (0x98, 0x99):
            return None
        return parse_cgdc_pixmap(body, offset, style)

    row_bytes = row_word
    if row_bytes <= 0 or row_bytes > 256:
        return None
    bounds_top = be16s(body, offset + 4)
    bounds_left = be16s(body, offset + 6)
    bounds_bottom = be16s(body, offset + 8)
    bounds_right = be16s(body, offset + 10)
    src_top = be16s(body, offset + 12)
    src_left = be16s(body, offset + 14)
    src_bottom = be16s(body, offset + 16)
    src_right = be16s(body, offset + 18)
    dst_top = be16s(body, offset + 20)
    dst_left = be16s(body, offset + 22)
    dst_bottom = be16s(body, offset + 24)
    dst_right = be16s(body, offset + 26)
    transfer_mode = be16(body, offset + 28)
    if transfer_mode not in (0, 1, 3, 64):
        return None
    bounds_width = bounds_right - bounds_left
    bounds_height = bounds_bottom - bounds_top
    width = src_right - src_left
    height = src_bottom - src_top
    dst_width = dst_right - dst_left
    dst_height = dst_bottom - dst_top
    if bounds_width <= 0 or bounds_height <= 0 or width <= 0 or height <= 0 or dst_width <= 0 or dst_height <= 0:
        return None
    if row_bytes < (bounds_width + 7) // 8:
        return None
    crop_left = src_left - bounds_left
    crop_top = src_top - bounds_top
    if crop_left < 0 or crop_top < 0 or crop_left + width > bounds_width or crop_top + height > bounds_height:
        return None

    rows: list[bytes] = []
    pos = offset + 30
    if op in (0x91, 0x99):
        try:
            pos = pict_embedded_region_end(body, pos)
        except CommonGroundError:
            return None
    if op in (0x90, 0x91):
        data_len = row_bytes * bounds_height
        if pos + data_len > len(body):
            return None
        for row_start in range(pos, pos + data_len, row_bytes):
            rows.append(body[row_start : row_start + row_bytes])
        pos += data_len
    else:
        for _ in range(bounds_height):
            if pos >= len(body):
                return None
            if row_bytes > 250:
                if pos + 2 > len(body):
                    return None
                packed_len = be16(body, pos)
                pos += 2
            else:
                packed_len = body[pos]
                pos += 1
            if packed_len <= 0 or pos + packed_len > len(body):
                return None
            decoded = packbits_decode_row(body[pos : pos + packed_len], row_bytes)
            if decoded is None:
                decoded = packbits_decode_units_loose(body[pos : pos + packed_len], 1, row_bytes)
            rows.append(decoded)
            pos += packed_len

    cropped_rows = crop_1bit_rows(rows, crop_left, crop_top, width, height)
    if cropped_rows is None:
        return None

    color = style.color or (0, 0, 0)
    background = (style.background_color or (255, 255, 255)) if transfer_mode == 0 else None
    png = rgba_png(width, height, cropped_rows, color, background)
    width_twips = max(1, dst_width * 5)
    height_twips = max(1, dst_height * 5)
    image = ImageRun(
        png=png,
        width=width,
        height=height,
        width_twips=width_twips,
        height_twips=height_twips,
        x=dst_left,
        y=dst_top,
        offset=offset,
    )
    return TextFragment(offset, op, b"", y=dst_top, x=dst_left, style=style, image=image), pos


def parse_cgdc_pixmap(body: bytes, offset: int, style: StyleState) -> tuple[TextFragment, int] | None:
    if offset + 2 + 46 + 8 > len(body):
        return None
    pix = offset + 2
    row_bytes = be16(body, pix) & 0x3FFF
    bounds_top = be16s(body, pix + 2)
    bounds_left = be16s(body, pix + 4)
    bounds_bottom = be16s(body, pix + 6)
    bounds_right = be16s(body, pix + 8)
    pack_type = be16(body, pix + 12)
    pixel_type = be16(body, pix + 26)
    pixel_size = be16(body, pix + 28)
    cmp_count = be16(body, pix + 30)
    cmp_size = be16(body, pix + 32)
    width = bounds_right - bounds_left
    height = bounds_bottom - bounds_top
    if row_bytes <= 0 or row_bytes > 8192 or width <= 0 or height < 0:
        return None
    if pack_type not in (0, 1, 2, 3, 4):
        return None
    if pixel_type != 0 or pixel_size not in (1, 2, 4, 8) or cmp_count != 1 or cmp_size != pixel_size:
        return None
    min_row_bytes = (width * pixel_size + 7) // 8
    if row_bytes < min_row_bytes:
        return None

    color_table = pix + 46
    if color_table + 8 > len(body):
        return None
    color_flags = be16(body, color_table + 4)
    color_count = be16(body, color_table + 6) + 1
    if color_count <= 0 or color_count > 4096:
        return None
    specs = color_table + 8
    table_end = specs + color_count * 8
    if table_end + 18 > len(body):
        return None
    palette: dict[int, tuple[int, int, int]] = {}
    for entry in range(color_count):
        base = specs + entry * 8
        value = be16(body, base)
        red = be16(body, base + 2) >> 8
        green = be16(body, base + 4) >> 8
        blue = be16(body, base + 6) >> 8
        pixel_index = entry if color_flags & 0x8000 else value
        palette[pixel_index & 0xFF] = (red, green, blue)

    src_top = be16s(body, table_end)
    src_left = be16s(body, table_end + 2)
    src_bottom = be16s(body, table_end + 4)
    src_right = be16s(body, table_end + 6)
    dst_top = be16s(body, table_end + 8)
    dst_left = be16s(body, table_end + 10)
    dst_bottom = be16s(body, table_end + 12)
    dst_right = be16s(body, table_end + 14)
    transfer_mode = be16(body, table_end + 16)
    if transfer_mode not in (0, 1, 3, 36, 39):
        return None
    src_width = src_right - src_left
    src_height = src_bottom - src_top
    dst_width = dst_right - dst_left
    dst_height = dst_bottom - dst_top
    pos = table_end + 18
    if body[offset + 1] == 0x99:
        try:
            pos = pict_embedded_region_end(body, pos)
        except CommonGroundError:
            return None
    if height == 0 and src_height == 0 and dst_height == 0:
        return TextFragment(offset, body[offset + 1], b"", y=dst_top, x=dst_left, style=style), pos
    if src_width <= 0 or src_height <= 0 or dst_width <= 0 or dst_height <= 0:
        return None
    if src_width > width or src_height > height:
        return None

    rows: list[bytes] = []
    compressed_rows = body[offset + 1] in (0x98, 0x99)
    if pack_type == 0 and not compressed_rows:
        data_len = row_bytes * height
        if pos + data_len > len(body):
            return None
        for row_start in range(pos, pos + data_len, row_bytes):
            unpacked = unpack_indexed_pixels(body[row_start : row_start + row_bytes], width, pixel_size)
            if unpacked is None:
                return None
            rows.append(unpacked)
        pos += data_len
    else:
        broken_rows = False
        for _ in range(height):
            if pos >= len(body):
                broken_rows = True
                break
            if row_bytes > 250:
                if pos + 2 > len(body):
                    broken_rows = True
                    break
                packed_len = be16(body, pos)
                pos += 2
            else:
                packed_len = body[pos]
                pos += 1
            if packed_len <= 0 or pos + packed_len > len(body):
                broken_rows = True
                break
            decoded = packbits_decode_row(body[pos : pos + packed_len], row_bytes)
            if decoded is None:
                decoded = packbits_decode_units_loose(body[pos : pos + packed_len], 1, row_bytes)
            unpacked = unpack_indexed_pixels(decoded, width, pixel_size)
            if unpacked is None:
                broken_rows = True
                break
            rows.append(unpacked)
            pos += packed_len
        while len(rows) < height:
            rows.append(b"\x00" * width)
        if broken_rows:
            pos = len(body)

    crop_left = max(0, src_left - bounds_left)
    crop_top = max(0, src_top - bounds_top)
    crop_right = min(width, src_right - bounds_left)
    crop_bottom = min(height, src_bottom - bounds_top)
    if crop_right <= crop_left or crop_bottom <= crop_top:
        return None
    cropped_rows = [row[crop_left:crop_right] for row in rows[crop_top:crop_bottom]]
    png = indexed_png(src_width, src_height, cropped_rows, palette)
    width_twips = max(1, dst_width * 5)
    height_twips = max(1, dst_height * 5)
    image = ImageRun(
        png=png,
        width=src_width,
        height=src_height,
        width_twips=width_twips,
        height_twips=height_twips,
        x=dst_left,
        y=dst_top,
        offset=offset,
    )
    return TextFragment(offset, body[offset + 1], b"", y=dst_top, x=dst_left, style=style, image=image), pos


def find_cgdc_pict_pages(body: bytes) -> list[PictPage]:
    signature = b"\x00\x11\x02\xff\x0c\x00"
    starts: list[int] = []
    search = 0
    while True:
        pos = body.find(signature, search)
        if pos < 0:
            break
        starts.append(pos)
        search = pos + 1
    if not starts:
        return []
    pages: list[PictPage] = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(body)
        frame: tuple[int | None, int | None, int | None, int | None] = (None, None, None, None)
        if start >= 8:
            top = be16s(body, start - 8)
            left = be16s(body, start - 6)
            bottom = be16s(body, start - 4)
            right = be16s(body, start - 2)
            if -2000 <= top <= bottom <= 10000 and -2000 <= left <= right <= 10000:
                frame = (top, left, bottom, right)
        pages.append(PictPage(start, end, *frame))
    return pages


def scan_text_fragments(body: bytes, kind: str) -> list[TextFragment]:
    dpl2 = kind == "DPL2"
    if dpl2:
        return scan_dpl2_text_fragments(body)
    fragments: list[TextFragment] = []
    i = 0
    limit = len(body)
    cgdc_y: int | None = None
    style = StyleState()
    font_names: dict[int, str] = {}
    while i + 8 <= limit:
        if body[i] != 0:
            i += 1
            continue
        op = body[i + 1]
        styled = apply_cgdc_style_control(body, i, style, font_names)
        if styled is not None:
            style, i = styled
            continue
        bitmap = parse_cgdc_bitmap(body, i, style)
        if bitmap is not None:
            fragment, end = bitmap
            fragments.append(fragment)
            i = end
            continue

        if not dpl2 and op == 0x28 and i + 7 <= limit:
            y = be16(body, i + 2)
            x = be16s(body, i + 4)
            length = body[i + 6]
            start = i + 7
            end = start + length
            if 0 < length <= 240 and end <= limit and plausible_text_bytes(body[start:end], dpl2=dpl2, op=op):
                cgdc_y = y
                fragments.append(TextFragment(i, op, body[start:end], y=y, x=x, style=style))
                i = end
                continue
        elif not dpl2 and op == 0x29 and i + 4 <= limit:
            length = body[i + 3]
            start = i + 4
            end = start + length
            if 0 < length <= 240 and end <= limit and plausible_text_bytes(body[start:end], dpl2=dpl2, op=op):
                fragments.append(TextFragment(i, op, body[start:end], y=cgdc_y, advance=body[i + 2], style=style))
                i = end
                continue
        elif not dpl2 and op == 0x2A and i + 4 <= limit:
            length = body[i + 3]
            start = i + 4
            end = start + length
            if 0 < length <= 240 and end <= limit and plausible_text_bytes(body[start:end], dpl2=dpl2, op=op):
                if cgdc_y is not None:
                    cgdc_y += body[i + 2]
                fragments.append(TextFragment(i, op, body[start:end], y=cgdc_y, style=style))
                i = end
                continue
        elif not dpl2 and op == 0x2B and i + 5 <= limit:
            length = body[i + 4]
            start = i + 5
            end = start + length
            if 0 < length <= 240 and end <= limit and plausible_text_bytes(body[start:end], dpl2=dpl2, op=op):
                fragments.append(TextFragment(i, op, body[start:end], style=style))
                i = end
                continue
        i += 1
    return fragments


def choose_cgdc_encoding(chunks: list[bytes]) -> str:
    sample = b"".join(chunks)
    if not sample:
        return "mac_roman"
    decoded = sample.decode("cp932", "ignore")
    cjk = sum(1 for ch in decoded if "\u3040" <= ch <= "\u30ff" or "\u4e00" <= ch <= "\u9fff")
    replacement = len(sample) - len(decoded.encode("cp932", "ignore"))
    return "cp932" if cjk >= 3 and replacement <= max(128, len(sample) // 20) else "mac_roman"


CP932_PRIVATE_MAP = {
    "\uf8f2": "™",
}

CGDC_JAPANESE_PAIR_MAP = {
    b"\x85\x7e": "〜",
}


def cp932_lead_byte(byte: int) -> bool:
    return 0x81 <= byte <= 0x9F or 0xE0 <= byte <= 0xFC


def decode_cgdc_text_bytes(data: bytes, encoding: str) -> str:
    if encoding != "cp932":
        return data.decode("mac_roman", "replace")
    out: list[str] = []
    i = 0
    while i < len(data):
        byte = data[i]
        if byte == 0:
            out.append("\x00")
            i += 1
            continue
        if i + 1 < len(data) and data[i : i + 2] in CGDC_JAPANESE_PAIR_MAP:
            out.append(CGDC_JAPANESE_PAIR_MAP[data[i : i + 2]])
            i += 2
            continue
        if cp932_lead_byte(byte) and i + 1 < len(data):
            pair = data[i : i + 2]
            try:
                text = pair.decode("cp932")
            except UnicodeDecodeError:
                text = ""
            if text:
                out.append("".join(CP932_PRIVATE_MAP.get(ch, ch) for ch in text))
                i += 2
                continue
        try:
            text = data[i : i + 1].decode("cp932")
        except UnicodeDecodeError:
            text = data[i : i + 1].decode("mac_roman", "replace")
        out.append(CP932_PRIVATE_MAP.get(text, text))
        i += 1
    return "".join(out)


def clean_dpl2_bytes(data: bytes) -> str:
    return data.decode("mac_roman", "replace")


def same_cgdc_line(current_y: int | None, fragment_y: int | None, text: str) -> bool:
    if current_y is None or fragment_y is None:
        return False
    if abs(current_y - fragment_y) <= 2:
        return True
    # Superscript marks are drawn slightly above the surrounding baseline.
    return len(text.strip()) <= 2 and 0 < current_y - fragment_y <= 44


def should_insert_join_space(current: str, text: str, fragment: TextFragment) -> bool:
    if not current or not text:
        return False
    left = current[-1]
    right = text[0]
    if left.isspace() or right.isspace():
        return False
    if right in ",.;:!?)]}%\u2122\u00ae'\"\u2019\u201d":
        return False
    if left in "([{\u2018\u201c'\"/-\u2019":
        return False
    if len(current.strip()) == 1 and left.isupper() and right.islower():
        return False
    if fragment.op == 0x29 and fragment.advance is not None and fragment.advance < 45 and left.isalpha() and right.islower():
        return False
    if fragment.op == 0x29 and fragment.advance is not None and fragment.advance < 45 and len(text) == 1 and left.isalnum() and right.isalnum():
        return False
    left_is_ascii_alnum = left.isascii() and left.isalnum()
    right_is_ascii_alnum = right.isascii() and right.isalnum()
    if right.isascii() and right.islower():
        if len(text) == 1:
            return False
        if len(current) >= 2 and current[-2] == "/" and left.isupper():
            return False
        current_word = re.search(r"[A-Za-z]+$", current)
        next_word = re.match(r"[A-Za-z']+", text)
        current_token = current_word.group(0) if current_word else ""
        next_token = next_word.group(0) if next_word else ""
        separate_words = {
            "and",
            "for",
            "from",
            "that",
            "that'll",
            "the",
            "then",
            "there",
            "they",
            "this",
            "to",
            "when",
            "where",
            "which",
            "while",
            "who",
            "will",
            "with",
            "you",
        }
        if len(next_token) <= 3 and next_token not in separate_words:
            return False
        if current_token.islower() and len(current_token) <= 4 and next_token not in separate_words:
            return False
        return next_token in separate_words
    word_left = left_is_ascii_alnum or left in ")\u2122\u00ae"
    word_right = right_is_ascii_alnum or right in "(\u2018\u201c'\""
    return word_left and word_right


def append_text_run(current: str, text: str, fragment: TextFragment) -> str:
    if not current:
        return text
    if should_insert_join_space(current, text, fragment):
        return current + " " + text
    return current + text


def append_styled_run(runs: list[TextRun], text: str, style: StyleState) -> None:
    if not text:
        return
    if runs and runs[-1].style == style:
        runs[-1] = TextRun(runs[-1].text + text, style)
    else:
        runs.append(TextRun(text, style))


def append_styled_fragment(
    runs: list[TextRun],
    current_text: str,
    text: str,
    fragment: TextFragment,
    style: StyleState | None = None,
) -> str:
    prefix = " " if should_insert_join_space(current_text, text, fragment) else ""
    append_styled_run(runs, prefix + text, style or fragment.style)
    return current_text + prefix + text


def decoded_fragments(fragments: list[TextFragment], kind: str) -> list[tuple[TextFragment, str]]:
    if kind == "CGDC":
        encoding = choose_cgdc_encoding([f.data for f in fragments])
        return [(f, decode_cgdc_text_bytes(f.data, encoding)) for f in fragments]
    return [(f, clean_dpl2_bytes(f.data)) for f in fragments]


def fragments_to_rich_lines(fragments: list[TextFragment], kind: str) -> list[VisualLine]:
    if not fragments:
        return []

    lines: list[VisualLine] = []
    current = ""
    current_runs: list[TextRun] = []
    current_images: list[ImageRun] = []
    pending_images: list[TextFragment] = []
    current_y: int | None = None
    current_x: int | None = None
    current_offset: int | None = None

    for fragment, text in decoded_fragments(fragments, kind):
        if fragment.image is not None:
            pending_images.append(fragment)
            continue
        text = text.replace("\x00", "").replace("\r", "\n")
        if not text:
            continue
        if kind == "CGDC":
            line_images: list[ImageRun] = []
            remaining_images: list[TextFragment] = []
            eligible_images: list[TextFragment] = []
            for image_fragment in pending_images:
                offset_gap = fragment.offset - image_fragment.offset
                if (
                    image_fragment.image is not None
                    and 0 < offset_gap <= 1800
                    and fragment.y is not None
                    and image_fragment.y is not None
                    and image_fragment.x is not None
                    and fragment.x is not None
                    and image_fragment.x <= fragment.x + 20
                    and image_fragment.y - 80 <= fragment.y <= image_fragment.y + image_fragment.image.height + 80
                ):
                    eligible_images.append(image_fragment)
                elif offset_gap <= 4096:
                    remaining_images.append(image_fragment)
            if eligible_images:
                line_images.append(max(eligible_images, key=lambda item: item.offset).image)  # type: ignore[arg-type]
            pending_images = remaining_images
            moves_left = (
                fragment.x is not None
                and current_x is not None
                and fragment.x < current_x - 30
            )
            joins_current = bool(current) and not moves_left and (
                fragment.op == 0x29 or same_cgdc_line(current_y, fragment.y, text)
            )
            if joins_current:
                if line_images:
                    current_images.extend(line_images)
                run_style = fragment.style
                if (
                    current_y is not None
                    and fragment.y is not None
                    and len(text.strip()) <= 2
                    and 0 < current_y - fragment.y <= 44
                ):
                    run_style = replace(fragment.style, superscript=True)
                current = append_styled_fragment(current_runs, current, text, fragment, run_style)
                if current_y is None:
                    current_y = fragment.y
                if current_x is None:
                    current_x = fragment.x
                continue
            if current.strip():
                lines.append(
                    VisualLine(
                        current.rstrip(),
                        current_y,
                        current_x,
                        tuple(current_runs),
                        tuple(current_images),
                        current_offset,
                    )
                )
            current = text
            current_runs = [TextRun(text, fragment.style)]
            current_images = line_images
            current_y = fragment.y
            current_x = fragment.x
            current_offset = fragment.offset
        elif fragment.op in (0x15, 0x29) and current:
            current += text
            append_styled_run(current_runs, text, fragment.style)
        else:
            if current.strip():
                lines.append(
                    VisualLine(
                        current.rstrip(),
                        current_y,
                        current_x,
                        tuple(current_runs),
                        tuple(current_images),
                        current_offset,
                    )
                )
            current = text
            current_runs = [TextRun(text, fragment.style)]
            current_images = []
            current_y = None
            current_x = None
            current_offset = fragment.offset
    if current.strip():
        lines.append(
            VisualLine(
                current.rstrip(),
                current_y,
                current_x,
                tuple(current_runs),
                tuple(current_images),
                current_offset,
            )
        )
    return lines


def fragments_to_lines(fragments: list[TextFragment], kind: str) -> list[str]:
    if not fragments:
        return []

    compact: list[str] = []
    for line in fragments_to_rich_lines(fragments, kind):
        normalized = " ".join(line.text.split()) if kind == "DPL2" else line.text
        if normalized.strip():
            compact.append(normalized)
    return compact


def pict_page_frame_size(pict_pages: list[PictPage]) -> tuple[int | None, int | None]:
    widths = [
        page.right - page.left
        for page in pict_pages
        if page.left is not None and page.right is not None and page.right > page.left
    ]
    heights = [
        page.bottom - page.top
        for page in pict_pages
        if page.top is not None and page.bottom is not None and page.bottom > page.top
    ]
    if not widths or not heights:
        return None, None
    return max(widths), max(heights)


def cgdc_render_geometry(fragments: list[TextFragment], pict_pages: list[PictPage]) -> tuple[int, int, int, int]:
    frame_width, frame_height = pict_page_frame_size(pict_pages)
    base_width = frame_width or 2450
    base_height = frame_height or 3200
    xs: list[int] = []
    ys: list[int] = []

    def keep_point(x: int | None, y: int | None) -> bool:
        if x is None or y is None:
            return False
        return -600 <= x <= base_width + 600 and -600 <= y <= base_height + 600

    for fragment in fragments:
        if keep_point(fragment.x, fragment.y):
            assert fragment.x is not None and fragment.y is not None
            xs.append(fragment.x)
            ys.append(fragment.y)
        if fragment.image is not None and fragment.image.x is not None and fragment.image.y is not None:
            dst_w = max(1, fragment.image.width_twips // 5)
            dst_h = max(1, fragment.image.height_twips // 5)
            corners = (
                (fragment.image.x, fragment.image.y),
                (fragment.image.x + dst_w, fragment.image.y + dst_h),
            )
            for x, y in corners:
                if keep_point(x, y):
                    xs.append(x)
                    ys.append(y)
    min_x = min(xs, default=0)
    min_y = min(ys, default=0)
    x_shift = max(0, -min_x) + (4 if min_x < 0 else 0)
    y_shift = max(0, -min_y) + (4 if min_y < 0 else 0)
    width = max(base_width + x_shift, max(xs, default=base_width) + x_shift + 40)
    height = max(base_height + y_shift, max(ys, default=base_height) + y_shift + 40)
    return width, height, x_shift, y_shift


def cgdc_render_encoding(fragments: list[TextFragment]) -> str:
    return choose_cgdc_encoding([fragment.data for fragment in fragments if fragment.image is None])


def pict_page_draw_events(
    body: bytes,
    page: PictPage,
    encoding: str,
) -> list[PictTextEvent | PictImageEvent | PictVectorEvent]:
    if page.start >= 8:
        record_data = body[page.start - 8 : page.end]
        try:
            return dpl2_pict_draw_events(record_data, encoding)
        except CommonGroundError:
            pass
    events: list[PictTextEvent | PictImageEvent] = []
    style = StyleState()
    font_names: dict[int, str] = {}
    current_x = 0
    current_y = 0
    last_baseline_y = 0
    i = page.start
    limit = page.end
    while i + 8 <= limit:
        if body[i] != 0:
            i += 1
            continue
        styled = apply_cgdc_style_control(body, i, style, font_names)
        if styled is not None and styled[1] <= limit:
            style, i = styled
            continue
        bitmap = parse_cgdc_bitmap(body, i, style)
        if bitmap is not None and bitmap[1] <= limit:
            fragment, end = bitmap
            if fragment.image is not None:
                events.append(PictImageEvent(i, fragment.image))
            i = end
            continue

        op = body[i + 1]
        if op == 0xFF and i > page.start + 10:
            break
        if op == 0x28 and i + 7 <= limit:
            y = be16(body, i + 2)
            x = be16s(body, i + 4)
            length = body[i + 6]
            start = i + 7
            end = start + length
            if 0 < length <= 240 and end <= limit and plausible_pict_text_record(body[start:end], op=op):
                text = decode_cgdc_text_bytes(body[start:end], encoding).replace("\x00", "")
                current_x = x
                draw_y = y
                raised_mark = visible_pict_text(text) and len(text.strip()) <= 2 and 10 <= last_baseline_y - y <= 80
                current_y = last_baseline_y if raised_mark else y
                if not raised_mark:
                    last_baseline_y = y
                if emit_pict_text(op, text):
                    events.append(PictTextEvent(i, current_x, draw_y, text, style))
                i = end
                continue
        elif op == 0x29 and i + 4 <= limit:
            length = body[i + 3]
            start = i + 4
            end = start + length
            if 0 < length <= 240 and end <= limit and plausible_pict_text_record(body[start:end], op=op):
                current_x += body[i + 2]
                text = decode_cgdc_text_bytes(body[start:end], encoding).replace("\x00", "")
                if emit_pict_text(op, text):
                    events.append(PictTextEvent(i, current_x, current_y, text, style))
                i = end
                continue
        elif op == 0x2A and i + 4 <= limit:
            length = body[i + 3]
            start = i + 4
            end = start + length
            if 0 < length <= 240 and end <= limit and plausible_pict_text_record(body[start:end], op=op):
                current_y += body[i + 2]
                last_baseline_y = current_y
                text = decode_cgdc_text_bytes(body[start:end], encoding).replace("\x00", "")
                if emit_pict_text(op, text):
                    events.append(PictTextEvent(i, current_x, current_y, text, style))
                i = end
                continue
        elif op == 0x2B and i + 5 <= limit:
            length = body[i + 4]
            start = i + 5
            end = start + length
            if 0 < length <= 240 and end <= limit and plausible_pict_text_record(body[start:end], op=op):
                current_x += body[i + 2]
                current_y += body[i + 3]
                last_baseline_y = current_y
                text = decode_cgdc_text_bytes(body[start:end], encoding).replace("\x00", "")
                if emit_pict_text(op, text):
                    events.append(PictTextEvent(i, current_x, current_y, text, style))
                i = end
                continue
        i += 1
    return events


def font_path_for_style(style: StyleState) -> str:
    family = (style.font_name or "").lower()
    pdf_family = pdf_font_family(style)
    emphasis = pdf_font_emphasis(style)
    path = PDF_FONT_PATHS.get(pdf_family, {}).get(emphasis, ("", None, ""))[1]
    if path is not None and Path(path).exists():
        return path
    if family == "symbol":
        return "/usr/share/fonts/urw-fonts/StandardSymbolsPS.otf"
    if "helvetica-condensed" in family:
        if emphasis == 3:
            return "/usr/share/fonts/urw-fonts/NimbusSansNarrow-BoldOblique.ttf"
        if emphasis == 1:
            return "/usr/share/fonts/urw-fonts/NimbusSansNarrow-Bold.ttf"
        if emphasis == 2:
            return "/usr/share/fonts/urw-fonts/NimbusSansNarrow-Oblique.ttf"
        return "/usr/share/fonts/urw-fonts/NimbusSansNarrow-Regular.ttf"
    if any(name in family for name in ("helvetica", "arial", "geneva", "futura")):
        if emphasis == 3:
            return "/usr/share/fonts/corefonts/arialbi.ttf"
        if emphasis == 1:
            return "/usr/share/fonts/corefonts/arialbd.ttf"
        if emphasis == 2:
            return "/usr/share/fonts/corefonts/ariali.ttf"
        return "/usr/share/fonts/corefonts/arial.ttf"
    if emphasis == 3:
        return "/usr/share/fonts/corefonts/timesbi.ttf"
    if emphasis == 1:
        return "/usr/share/fonts/corefonts/timesbd.ttf"
    if emphasis == 2:
        return "/usr/share/fonts/corefonts/timesi.ttf"
    return "/usr/share/fonts/corefonts/times.ttf"


def load_render_font(style: StyleState, render_scale: int, font_unit_scale: float) -> object:
    if ImageFont is None:
        raise CommonGroundError("Pillow is required for CGDC page raster rendering")
    pixel_size = max(8, int(style.size_half_points * font_unit_scale * render_scale))
    path = font_path_for_style(style)
    try:
        return ImageFont.truetype(path, pixel_size)
    except OSError:
        return ImageFont.load_default(pixel_size)


def pdf_number(value: float) -> str:
    if abs(value) < 0.0000005:
        return "0"
    if abs(value - round(value)) < 0.0000005:
        return str(int(round(value)))
    return f"{value:.6f}".rstrip("0").rstrip(".")


def pdf_escape_name(name: str) -> str:
    return name.replace("#", "#23").replace(" ", "#20")


def pdf_escape_text(text: str) -> str:
    encoded = text.encode("cp1252", "replace")
    return pdf_escape_bytes(encoded)


def pdf_escape_bytes(encoded: bytes) -> str:
    out = bytearray()
    for byte in encoded:
        if byte in (0x28, 0x29, 0x5C):
            out.append(0x5C)
            out.append(byte)
    return out.decode("latin1")


def pdf_escape_bytes(data: bytes) -> str:
    out = bytearray()
    for byte in data:
        if byte in (0x28, 0x29, 0x5C):
            out.append(0x5C)
        out.append(byte)
    return out.decode("latin1")


def pdf_pattern_name(pattern: bytes, color: tuple[int, int, int], point_scale: float) -> str:
    scale_part = str(int(round(point_scale * 1000)))
    return "Pat" + pattern.hex().upper() + f"{color[0]:02X}{color[1]:02X}{color[2]:02X}" + scale_part


def pdf_hex_utf16be(text: str) -> str:
    return "<" + text.encode("utf-16-be", "replace").hex().upper() + ">"


def unicode_gid_map() -> dict[int, int]:
    global UNICODE_GID_MAP
    if UNICODE_GID_MAP is not None:
        return UNICODE_GID_MAP
    mapping: dict[int, int] = {}
    if TTFont is not None and UNICODE_FONT_SPEC.path is not None:
        try:
            font = TTFont(UNICODE_FONT_SPEC.path)
            for codepoint, glyph_name in (font.getBestCmap() or {}).items():
                if 0 <= codepoint <= 0xFFFF:
                    mapping[codepoint] = font.getGlyphID(glyph_name)
        except Exception:
            mapping = {}
    UNICODE_GID_MAP = mapping
    return mapping


def pdf_hex_unicode_cids(text: str) -> str:
    out = bytearray()
    for char in text:
        cid = ord(char) if ord(char) <= 0xFFFF else 0
        out.extend(struct.pack(">H", max(0, min(0xFFFF, cid))))
    return "<" + out.hex().upper() + ">"


def needs_unicode_pdf_font(text: str) -> bool:
    try:
        text.encode("cp1252")
        return False
    except UnicodeEncodeError:
        return True


def math_pi_six_text(text: str) -> str:
    out: list[str] = []
    for byte in text.encode("mac_roman", "replace"):
        out.append(MATH_PI_SIX_TO_UNICODE.get(byte, "?"))
    return "".join(out)


def futura_book_fractions_text(text: str) -> str:
    out: list[str] = []
    for byte in text.encode("mac_roman", "replace"):
        out.append(FUTURA_BOOK_FRACTIONS_TO_UNICODE.get(byte, "?"))
    return "".join(out)


def pdf_font_family(style: StyleState) -> str:
    family = (style.font_name or "").lower()
    if family == "symbol":
        return "symbol"
    if "helvetica-condensed" in family:
        return "helvetica_narrow"
    if "futura" in family:
        return "futura"
    if "berkeley" in family:
        return "berkeley"
    if "palatia" in family or "schneid" in family:
        return "palatino"
    if any(name in family for name in ("helvetica", "arial", "geneva")):
        return "helvetica"
    return "times"


def pdf_font_emphasis(style: StyleState) -> int:
    family = (style.font_name or "").lower()
    emphasis = style.emphasis & 3
    if any(token in family for token in ("bold", "black", "demi")):
        emphasis |= 1
    if any(token in family for token in ("italic", "oblique", "obl")):
        emphasis |= 2
    return emphasis & 3


def pdf_font_for_style(style: StyleState) -> tuple[str, str]:
    emphasis = pdf_font_emphasis(style)
    return PDF_BASE_FONTS[pdf_font_family(style)][emphasis]


def pdf_font_spec_for_style(style: StyleState) -> PdfFontSpec:
    emphasis = pdf_font_emphasis(style)
    resource_name, path, base14_name = PDF_FONT_PATHS[pdf_font_family(style)][emphasis]
    if path is None or not Path(path).exists():
        resource_name, base14_name = PDF_BASE_FONTS[pdf_font_family(style)][emphasis]
        return PdfFontSpec(resource_name, None, base14_name)
    return PdfFontSpec(resource_name, path, base14_name)


def pfr_named_keys_for_style(style: StyleState) -> list[str]:
    font_name = (style.font_name or "").lower()
    emphasis = pdf_font_emphasis(style)
    keys: list[str] = []
    if emphasis == 1:
        keys.extend((font_name + "_b", font_name + "-bold"))
    elif emphasis == 2:
        keys.extend((font_name + "_i", font_name + "-italic", font_name + "-bookitalic"))
    elif emphasis == 3:
        keys.extend((font_name + "_bi", font_name + "-bolditalic", font_name + "-boldobl"))
    keys.append(font_name)
    return keys


def pfr_metric_for_style(style: StyleState) -> PfrFontMetrics | None:
    font_name = (style.font_name or "").lower()
    style_metric = CURRENT_PFR_STYLE_METRICS.get((font_name, pdf_font_emphasis(style)))
    if style_metric is not None:
        return style_metric
    for key in pfr_named_keys_for_style(style):
        metric = CURRENT_PFR_METRICS.get(key)
        if metric is not None:
            return metric
    return None


def pfr_resource_for_style(style: StyleState) -> str | None:
    font_name = (style.font_name or "").lower()
    style_resource = CURRENT_PFR_STYLE_FONT_RESOURCES.get((font_name, pdf_font_emphasis(style)))
    if style_resource is not None:
        return style_resource
    for key in pfr_named_keys_for_style(style):
        resource = CURRENT_PFR_FONT_RESOURCES.get(key)
        if resource is not None:
            return resource
    return None


def style_font_internal_size(style: StyleState, font_unit_scale: float) -> float:
    return max(4.0, style.size_half_points * font_unit_scale)


def style_text_width(text: str, style: StyleState, font_unit_scale: float) -> float:
    extra = text.count(" ") * style.space_extra + len(text) * style.char_extra
    pfr_metrics = pfr_metric_for_style(style)
    if pfr_metrics is not None and pfr_metrics.metrics_resolution > 0:
        raw = text.encode("mac_roman", "replace")
        advances = pfr_metrics.advances
        alternate_advances: dict[int, int] = {}
        font_name_key = (style.font_name or "").lower()
        alternate_metrics = CURRENT_PFR_METRICS.get(font_name_key)
        if alternate_metrics is pfr_metrics:
            alternate_metrics = CURRENT_PFR_METRICS.get(font_name_key + "_b")
        if alternate_metrics is not None and alternate_metrics.metrics_resolution == pfr_metrics.metrics_resolution:
            alternate_advances = alternate_metrics.advances
        def pfr_advance(byte: int) -> int | None:
            if byte in advances:
                return advances[byte]
            if byte in alternate_advances:
                return alternate_advances[byte]
            return None
        known = [advance for byte in raw if (advance := pfr_advance(byte)) is not None]
        if len(known) == len(raw):
            width_units = sum(known)
        elif known:
            fallback_advance = sum(known) / len(known)
            width_units = sum((advance if (advance := pfr_advance(byte)) is not None else fallback_advance) for byte in raw)
        else:
            width_units = len(raw) * pfr_metrics.metrics_resolution * 0.5
        return max(1.0, width_units / pfr_metrics.metrics_resolution * style_font_internal_size(style, font_unit_scale) + extra)
    if pdf_font_family(style) == "symbol":
        return max(1.0, len(text.encode("mac_roman", "replace")) * style_font_internal_size(style, font_unit_scale) * 0.72 + extra)
    if (style.font_name or "").lower() == "mathematicalpi-six":
        return max(1.0, len(text.encode("mac_roman", "replace")) * style_font_internal_size(style, font_unit_scale) * 0.78 + extra)
    if (style.font_name or "").lower() == "futurabookfractions":
        return max(1.0, len(text.encode("mac_roman", "replace")) * style_font_internal_size(style, font_unit_scale) * 0.74 + extra)
    if ImageFont is None:
        return max(1.0, len(text) * style_font_internal_size(style, font_unit_scale) * 0.48 + extra)
    try:
        font = load_render_font(style, 1, font_unit_scale)
        return max(1.0, float(font.getlength(text)) + extra)  # type: ignore[attr-defined]
    except Exception:
        return max(1.0, len(text) * style_font_internal_size(style, font_unit_scale) * 0.48 + extra)


class PdfBuilder:
    def __init__(self) -> None:
        self.objects: list[bytes] = []

    def add_object(self, payload: bytes) -> int:
        self.objects.append(payload)
        return len(self.objects)

    def add_stream(self, dictionary: str, payload: bytes, *, compress: bool = True) -> int:
        stream = zlib.compress(payload) if compress else payload
        filter_part = " /Filter /FlateDecode" if compress else ""
        obj = (
            f"<< {dictionary} /Length {len(stream)}{filter_part} >>\nstream\n".encode("ascii")
            + stream
            + b"\nendstream"
        )
        return self.add_object(obj)

    def add_base14_font_object(self, spec: PdfFontSpec) -> int:
        if spec.base14_name == "Symbol":
            cmap_lines = [
                "/CIDInit /ProcSet findresource begin",
                "12 dict begin",
                "begincmap",
                "/CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def",
                "/CMapName /Adobe-Symbol-UCS def",
                "/CMapType 2 def",
                "1 begincodespacerange",
                "<00> <FF>",
                "endcodespacerange",
                f"{len(SYMBOL_TO_UNICODE)} beginbfchar",
            ]
            for code, unicode_value in sorted(SYMBOL_TO_UNICODE.items()):
                cmap_lines.append(f"<{code:02X}> <{unicode_value:04X}>")
            cmap_lines.extend(
                [
                    "endbfchar",
                    "endcmap",
                    "CMapName currentdict /CMap defineresource pop",
                    "end",
                    "end",
                    "",
                ]
            )
            to_unicode = self.add_stream("", "\n".join(cmap_lines).encode("ascii"))
            return self.add_object(
                f"<< /Type /Font /Subtype /Type1 /BaseFont /Symbol /ToUnicode {to_unicode} 0 R >>".encode("ascii")
            )
        return self.add_object(
            f"<< /Type /Font /Subtype /Type1 /BaseFont /{spec.base14_name} /Encoding /WinAnsiEncoding >>".encode(
                "ascii"
            )
        )

    def add_pfr_type3_font_object(self, metric: PfrFontMetrics) -> int:
        if metric.metrics_resolution <= 0:
            raise CommonGroundError("invalid PFR Type3 metrics resolution")
        first_char = min(metric.glyph_programs)
        last_char = max(metric.glyph_programs)
        widths = [str(metric.advances.get(code, 0)) for code in range(first_char, last_char + 1)]
        charproc_ids: dict[int, int] = {}
        for code in range(first_char, last_char + 1):
            if code not in metric.glyph_programs:
                continue
            path_commands = parse_pfr_glyph_path(metric, code)
            parts = [
                f"{metric.advances.get(code, 0)} 0 {metric.bbox[0]} {metric.bbox[1]} {metric.bbox[2]} {metric.bbox[3]} d1"
            ]
            for command in path_commands:
                if command.op == "m":
                    (x, y), = command.points
                    parts.append(f"{pdf_number(x)} {pdf_number(y)} m")
                elif command.op == "l":
                    (x, y), = command.points
                    parts.append(f"{pdf_number(x)} {pdf_number(y)} l")
                elif command.op == "c":
                    (x1, y1), (x2, y2), (x3, y3) = command.points
                    parts.append(
                        f"{pdf_number(x1)} {pdf_number(y1)} {pdf_number(x2)} {pdf_number(y2)} {pdf_number(x3)} {pdf_number(y3)} c"
                    )
                elif command.op == "h":
                    parts.append("h")
            if len(parts) > 1:
                parts.append("f")
            charproc_ids[code] = self.add_stream("", "\n".join(parts).encode("ascii"))

        differences = " ".join(f"{code} /g{code:02X}" for code in range(first_char, last_char + 1) if code in charproc_ids)
        charprocs = " ".join(f"/g{code:02X} {obj_id} 0 R" for code, obj_id in sorted(charproc_ids.items()))
        cmap_lines = [
            "/CIDInit /ProcSet findresource begin",
            "12 dict begin",
            "begincmap",
            "/CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def",
            f"/CMapName /{pdf_escape_name(metric.font_id)}-UCS def",
            "/CMapType 2 def",
            "1 begincodespacerange",
            "<00> <FF>",
            "endcodespacerange",
            f"{len(charproc_ids)} beginbfchar",
        ]
        for code in sorted(charproc_ids):
            font_id_key = metric.font_id.lower()
            if font_id_key == "symbol" and code in SYMBOL_TO_UNICODE:
                unicode_values = [SYMBOL_TO_UNICODE[code]]
            elif font_id_key == "mathematicalpi-six" and code in MATH_PI_SIX_TO_UNICODE:
                unicode_values = [ord(char) for char in MATH_PI_SIX_TO_UNICODE[code]]
            elif font_id_key == "futurabookfractions" and code in FUTURA_BOOK_FRACTIONS_TO_UNICODE:
                unicode_values = [ord(char) for char in FUTURA_BOOK_FRACTIONS_TO_UNICODE[code]]
            else:
                try:
                    unicode_values = [ord(bytes([code]).decode("mac_roman"))]
                except UnicodeDecodeError:
                    unicode_values = [0xFFFD]
            unicode_hex = "".join(f"{value:04X}" for value in unicode_values)
            cmap_lines.append(f"<{code:02X}> <{unicode_hex}>")
        cmap_lines.extend(["endbfchar", "endcmap", "CMapName currentdict /CMap defineresource pop", "end", "end", ""])
        to_unicode = self.add_stream("", "\n".join(cmap_lines).encode("ascii"))
        bbox = " ".join(str(value) for value in metric.bbox)
        return self.add_object(
            (
                f"<< /Type /Font /Subtype /Type3 /Name /{pdf_escape_name(metric.font_id)} "
                f"/FontBBox [{bbox}] /FontMatrix [{pdf_number(1.0 / metric.metrics_resolution)} 0 0 {pdf_number(1.0 / metric.metrics_resolution)} 0 0] "
                f"/FirstChar {first_char} /LastChar {last_char} /Widths [{' '.join(widths)}] "
                f"/Encoding << /Type /Encoding /Differences [ {differences} ] >> "
                f"/CharProcs << {charprocs} >> /Resources << >> /ToUnicode {to_unicode} 0 R >>"
            ).encode("ascii")
        )

    def add_identity_unicode_font_object(self, spec: PdfFontSpec) -> int:
        if TTFont is None or spec.path is None:
            return self.add_base14_font_object(spec)
        try:
            font = TTFont(spec.path)
            raw_font = Path(spec.path).read_bytes()
            units_per_em = font["head"].unitsPerEm
            scale = 1000.0 / units_per_em
            name = font["name"].getDebugName(6) or font["name"].getBestFullName() or spec.base14_name
            font_name = re.sub(r"[^A-Za-z0-9_.-]", "", name) or spec.base14_name
            head = font["head"]
            hhea = font["hhea"]
            os2 = font["OS/2"] if "OS/2" in font else None
            post = font["post"] if "post" in font else None
            hmtx = font["hmtx"].metrics
            cmap = font.getBestCmap() or {}
            glyph_id_by_code = unicode_gid_map()

            def scaled(value: float) -> int:
                return int(round(value * scale))

            default_width = scaled(hmtx.get(".notdef", (units_per_em, 0))[0])
            cid_to_unicode: list[tuple[int, int]] = []
            width_by_cid: dict[int, int] = {}
            for code, glyph_name in cmap.items():
                if not (0 <= code <= 0xFFFF):
                    continue
                cid = code
                advance = scaled(hmtx.get(glyph_name, (default_width / scale, 0))[0])
                cid_to_unicode.append((cid, code))
                if advance != default_width:
                    width_by_cid[cid] = advance
            width_entries = [f"{cid} [{width_by_cid[cid]}]" for cid in sorted(width_by_cid)]
            widths_part = f"/W [ {' '.join(width_entries)} ]" if width_entries else ""

            flags = 4 | 32
            ascent = scaled(getattr(os2, "sTypoAscender", hhea.ascent) if os2 is not None else hhea.ascent)
            descent = scaled(getattr(os2, "sTypoDescender", hhea.descent) if os2 is not None else hhea.descent)
            cap_height = scaled(getattr(os2, "sCapHeight", hhea.ascent) if os2 is not None else hhea.ascent)
            italic_angle = getattr(post, "italicAngle", 0) if post is not None else 0
            bbox = [scaled(head.xMin), scaled(head.yMin), scaled(head.xMax), scaled(head.yMax)]
            cff_font = "CFF " in font or "CFF2" in font
            if cff_font:
                font_file = self.add_stream("/Subtype /OpenType", raw_font)
                font_file_key = "FontFile3"
                cid_subtype = "CIDFontType0"
                cid_to_gid_part = ""
            else:
                font_file = self.add_stream("/Length1 " + str(len(raw_font)), raw_font)
                font_file_key = "FontFile2"
                cid_subtype = "CIDFontType2"
                cid_to_gid = bytearray(0x10000 * 2)
                for code, glyph_id in glyph_id_by_code.items():
                    if 0 <= code <= 0xFFFF and 0 <= glyph_id <= 0xFFFF:
                        struct.pack_into(">H", cid_to_gid, code * 2, glyph_id)
                cid_to_gid_obj = self.add_stream("", bytes(cid_to_gid))
                cid_to_gid_part = f"/CIDToGIDMap {cid_to_gid_obj} 0 R "
            descriptor = self.add_object(
                (
                    f"<< /Type /FontDescriptor /FontName /{pdf_escape_name(font_name)} "
                    f"/Flags {flags} /FontBBox [{' '.join(str(v) for v in bbox)}] "
                    f"/ItalicAngle {pdf_number(float(italic_angle))} /Ascent {ascent} /Descent {descent} "
                    f"/CapHeight {cap_height} /StemV 80 /{font_file_key} {font_file} 0 R >>"
                ).encode("ascii")
            )
            cid_font = self.add_object(
                (
                    f"<< /Type /Font /Subtype /{cid_subtype} /BaseFont /{pdf_escape_name(font_name)} "
                    f"/CIDSystemInfo << /Registry (Adobe) /Ordering (Identity) /Supplement 0 >> "
                    f"/FontDescriptor {descriptor} 0 R /DW {default_width} {widths_part} {cid_to_gid_part}>>"
                ).encode("ascii")
            )
            ranges: list[tuple[int, int, int]] = []
            for cid, code in sorted(cid_to_unicode):
                if ranges and cid == ranges[-1][1] + 1 and code == ranges[-1][2] + (cid - ranges[-1][0]):
                    start, _, start_code = ranges[-1]
                    ranges[-1] = (start, cid, start_code)
                else:
                    ranges.append((cid, cid, code))
            cmap_lines = [
                "/CIDInit /ProcSet findresource begin",
                "12 dict begin",
                "begincmap",
                "/CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def",
                "/CMapName /Adobe-Identity-UCS def",
                "/CMapType 2 def",
                "1 begincodespacerange",
                "<0000> <FFFF>",
                "endcodespacerange",
            ]
            for chunk_start in range(0, len(ranges), 100):
                chunk = ranges[chunk_start : chunk_start + 100]
                cmap_lines.append(f"{len(chunk)} beginbfrange")
                for start, end, start_code in chunk:
                    cmap_lines.append(f"<{start:04X}> <{end:04X}> <{start_code:04X}>")
                cmap_lines.append("endbfrange")
            cmap_lines.extend(
                [
                    "endcmap",
                    "CMapName currentdict /CMap defineresource pop",
                    "end",
                    "end",
                    "",
                ]
            )
            to_unicode = self.add_stream("", "\n".join(cmap_lines).encode("ascii"))
            return self.add_object(
                (
                    f"<< /Type /Font /Subtype /Type0 /BaseFont /{pdf_escape_name(font_name)} "
                    f"/Encoding /Identity-H /DescendantFonts [ {cid_font} 0 R ] "
                    f"/ToUnicode {to_unicode} 0 R >>"
                ).encode("ascii")
            )
        except Exception:
            return self.add_base14_font_object(spec)

    def add_truetype_font_object(self, spec: PdfFontSpec) -> int:
        if TTFont is None or spec.path is None:
            return self.add_base14_font_object(spec)
        try:
            font = TTFont(spec.path)
            raw_font = Path(spec.path).read_bytes()
            units_per_em = font["head"].unitsPerEm
            scale = 1000.0 / units_per_em
            name = font["name"].getDebugName(6) or font["name"].getBestFullName() or spec.base14_name
            font_name = re.sub(r"[^A-Za-z0-9_.-]", "", name) or spec.base14_name
            head = font["head"]
            hhea = font["hhea"]
            os2 = font["OS/2"] if "OS/2" in font else None
            post = font["post"] if "post" in font else None
            cmap = font.getBestCmap() or {}
            hmtx = font["hmtx"].metrics

            def scaled(value: float) -> int:
                return int(round(value * scale))

            missing_width = scaled(hmtx.get(".notdef", (units_per_em // 2, 0))[0])
            widths: list[int] = []
            for code in range(32, 256):
                try:
                    char = bytes([code]).decode("cp1252")
                    glyph_name = cmap.get(ord(char))
                except UnicodeDecodeError:
                    glyph_name = None
                advance = hmtx.get(glyph_name, (missing_width / scale, 0))[0] if glyph_name else missing_width / scale
                widths.append(scaled(advance))

            flags = 32
            family = spec.resource_name.lower()
            if "times" in family:
                flags |= 2
            else:
                flags |= 4
            if "italic" in family or "oblique" in family:
                flags |= 64
            ascent = scaled(getattr(os2, "sTypoAscender", hhea.ascent) if os2 is not None else hhea.ascent)
            descent = scaled(getattr(os2, "sTypoDescender", hhea.descent) if os2 is not None else hhea.descent)
            cap_height = scaled(getattr(os2, "sCapHeight", hhea.ascent) if os2 is not None else hhea.ascent)
            italic_angle = getattr(post, "italicAngle", 0) if post is not None else 0
            bbox = [scaled(head.xMin), scaled(head.yMin), scaled(head.xMax), scaled(head.yMax)]
            stem_v = 120 if "bold" in family else 80
            font_file = self.add_stream("/Length1 " + str(len(raw_font)), raw_font)
            descriptor = self.add_object(
                (
                    f"<< /Type /FontDescriptor /FontName /{pdf_escape_name(font_name)} "
                    f"/Flags {flags} /FontBBox [{' '.join(str(v) for v in bbox)}] "
                    f"/ItalicAngle {pdf_number(float(italic_angle))} /Ascent {ascent} /Descent {descent} "
                    f"/CapHeight {cap_height} /StemV {stem_v} /FontFile2 {font_file} 0 R >>"
                ).encode("ascii")
            )
            return self.add_object(
                (
                    f"<< /Type /Font /Subtype /TrueType /BaseFont /{pdf_escape_name(font_name)} "
                    f"/FirstChar 32 /LastChar 255 /Widths [{' '.join(str(w) for w in widths)}] "
                    f"/FontDescriptor {descriptor} 0 R /Encoding /WinAnsiEncoding >>"
                ).encode("ascii")
            )
        except Exception:
            return self.add_base14_font_object(spec)

    def add_image_xobject(self, png: bytes) -> tuple[int, int, int]:
        if Image is None:
            raise CommonGroundError("Pillow is required for PDF image embedding")
        image = Image.open(io.BytesIO(png)).convert("RGBA")
        width, height = image.size
        rgba = image.tobytes()
        rgb = bytearray()
        alpha = bytearray()
        opaque = True
        for i in range(0, len(rgba), 4):
            rgb.extend(rgba[i : i + 3])
            a = rgba[i + 3]
            alpha.append(a)
            if a != 255:
                opaque = False

        smask_obj: int | None = None
        if not opaque:
            smask_obj = self.add_stream(
                f"/Type /XObject /Subtype /Image /Width {width} /Height {height} "
                "/ColorSpace /DeviceGray /BitsPerComponent 8",
                bytes(alpha),
            )
        smask_part = f" /SMask {smask_obj} 0 R" if smask_obj is not None else ""
        image_obj = self.add_stream(
            f"/Type /XObject /Subtype /Image /Width {width} /Height {height} "
            f"/ColorSpace /DeviceRGB /BitsPerComponent 8{smask_part}",
            bytes(rgb),
        )
        return image_obj, width, height

    def add_tiling_pattern_object(self, pattern: bytes, color: tuple[int, int, int], point_scale: float) -> int:
        if len(pattern) != 8:
            raise CommonGroundError("invalid QuickDraw pattern size")
        red, green, blue = color
        cell = 8 * point_scale
        parts = [
            "q",
            "1 1 1 rg",
            f"0 0 {pdf_number(cell)} {pdf_number(cell)} re f",
            f"{pdf_number(red / 255)} {pdf_number(green / 255)} {pdf_number(blue / 255)} rg",
        ]
        for row, byte in enumerate(pattern):
            y = (7 - row) * point_scale
            for column in range(8):
                if byte & (1 << (7 - column)):
                    x = column * point_scale
                    parts.append(
                        f"{pdf_number(x)} {pdf_number(y)} {pdf_number(point_scale)} {pdf_number(point_scale)} re f"
                    )
        parts.append("Q")
        return self.add_stream(
            f"/Type /Pattern /PatternType 1 /PaintType 1 /TilingType 1 "
            f"/BBox [0 0 {pdf_number(cell)} {pdf_number(cell)}] "
            f"/XStep {pdf_number(cell)} /YStep {pdf_number(cell)} /Resources << >>",
            "\n".join(parts).encode("ascii"),
        )

    def build(self, pages: list[PdfPage]) -> bytes:
        if not pages:
            raise CommonGroundError("no PDF pages produced")

        font_object_ids: dict[str, int] = {}
        used_fonts = sorted({font_name for page in pages for font_name in page.fonts})
        for resource_name in used_fonts:
            if resource_name == UNICODE_FONT_SPEC.resource_name:
                font_object_ids[resource_name] = self.add_identity_unicode_font_object(UNICODE_FONT_SPEC)
                continue
            if resource_name in CURRENT_PFR_FONT_BY_RESOURCE:
                font_object_ids[resource_name] = self.add_pfr_type3_font_object(CURRENT_PFR_FONT_BY_RESOURCE[resource_name])
                continue
            spec = PDF_FONT_SPECS_BY_RESOURCE.get(resource_name)
            if spec is None:
                base_name = dict(font for family in PDF_BASE_FONTS.values() for font in family.values()).get(
                    resource_name, "Times-Roman"
                )
                spec = PdfFontSpec(resource_name, None, base_name)
            font_object_ids[resource_name] = self.add_truetype_font_object(spec)

        pattern_object_ids: dict[str, int] = {}
        used_patterns: dict[str, tuple[bytes, tuple[int, int, int], float]] = {}
        for page in pages:
            used_patterns.update(page.patterns)
        for name, (pattern, color, scale) in sorted(used_patterns.items()):
            pattern_object_ids[name] = self.add_tiling_pattern_object(pattern, color, scale)

        kids: list[int] = []
        page_entries: list[tuple[PdfPage, int]] = []
        for page in pages:
            content = "\n".join(page.commands).encode("latin1", "replace")
            content_obj = self.add_stream("", content)
            page_entries.append((page, content_obj))
            kids.append(0)

        pages_obj = len(self.objects) + len(page_entries) + 1
        for index, (page, content_obj) in enumerate(page_entries):
            font_resources = " ".join(
                f"/{name} {font_object_ids[name]} 0 R" for name in sorted(page.fonts)
            )
            xobject_resources = " ".join(
                f"/{name} {obj_id} 0 R" for name, obj_id in sorted(page.xobjects.items())
            )
            resources = f"<< /Font << {font_resources} >>"
            if xobject_resources:
                resources += f" /XObject << {xobject_resources} >>"
            pattern_resources = " ".join(
                f"/{name} {pattern_object_ids[name]} 0 R" for name in sorted(page.patterns)
            )
            if pattern_resources:
                resources += f" /Pattern << {pattern_resources} >>"
            resources += " >>"
            page_obj = self.add_object(
                (
                    f"<< /Type /Page /Parent {pages_obj} 0 R "
                    f"/MediaBox [0 0 {pdf_number(page.width)} {pdf_number(page.height)}] "
                    f"/Resources {resources} /Contents {content_obj} 0 R >>"
                ).encode("ascii")
            )
            kids[index] = page_obj

        kids_ref = " ".join(f"{obj_id} 0 R" for obj_id in kids)
        self.add_object(f"<< /Type /Pages /Kids [ {kids_ref} ] /Count {len(kids)} >>".encode("ascii"))
        catalog_obj = self.add_object(f"<< /Type /Catalog /Pages {pages_obj} 0 R >>".encode("ascii"))

        out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]
        for index, obj in enumerate(self.objects, 1):
            offsets.append(len(out))
            out.extend(f"{index} 0 obj\n".encode("ascii"))
            out.extend(obj)
            out.extend(b"\nendobj\n")
        xref_offset = len(out)
        out.extend(f"xref\n0 {len(self.objects) + 1}\n".encode("ascii"))
        out.extend(b"0000000000 65535 f \n")
        for offset in offsets[1:]:
            out.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
        out.extend(
            (
                f"trailer\n<< /Size {len(self.objects) + 1} /Root {catalog_obj} 0 R >>\n"
                f"startxref\n{xref_offset}\n%%EOF\n"
            ).encode("ascii")
        )
        return bytes(out)


def pdf_draw_image(
    builder: PdfBuilder,
    page: PdfPage,
    image: ImageRun,
    x_shift: int,
    y_shift: int,
    point_scale: float,
    image_index: int,
    clip: PictClipRegion | None = None,
) -> int:
    if image.x is None or image.y is None:
        return image_index
    dst_w = max(1, image.width_twips // 5)
    dst_h = max(1, image.height_twips // 5)
    obj_id, _, _ = builder.add_image_xobject(image.png)
    name = f"Im{image_index}"
    page.xobjects[name] = obj_id
    x = (image.x + x_shift) * point_scale
    y = page.height - (image.y + y_shift + dst_h) * point_scale
    w = dst_w * point_scale
    h = dst_h * point_scale
    command = f"q {pdf_number(w)} 0 0 {pdf_number(h)} {pdf_number(x)} {pdf_number(y)} cm /{name} Do Q"
    page.commands.append(pdf_apply_clip(command, clip, page, x_shift, y_shift, point_scale))
    return image_index + 1


def pdf_clip_command(
    clip: PictClipRegion | None,
    page: PdfPage,
    x_shift: int,
    y_shift: int,
    point_scale: float,
) -> str | None:
    if clip is None:
        return None
    rectangles = clip.runs if clip.runs else (clip.bounds,)
    parts: list[str] = []
    for left, top, right, bottom in rectangles:
        width = right - left
        height = bottom - top
        if width <= 0 or height <= 0:
            continue
        x = (left + x_shift) * point_scale
        y = page.height - (bottom + y_shift) * point_scale
        parts.append(f"{pdf_number(x)} {pdf_number(y)} {pdf_number(width * point_scale)} {pdf_number(height * point_scale)} re")
    if not parts:
        return None
    return f"{' '.join(parts)} W n"


def pdf_apply_clip(
    command: str,
    clip: PictClipRegion | None,
    page: PdfPage,
    x_shift: int,
    y_shift: int,
    point_scale: float,
) -> str:
    clip_command = pdf_clip_command(clip, page, x_shift, y_shift, point_scale)
    if clip_command is None:
        return command
    return f"q {clip_command} {command} Q"


def pdf_draw_vector(
    page: PdfPage,
    event: PictVectorEvent,
    x_shift: int,
    y_shift: int,
    point_scale: float,
) -> None:
    red, green, blue = event.color or (0, 0, 0)
    color = f"{pdf_number(red / 255)} {pdf_number(green / 255)} {pdf_number(blue / 255)}"
    stroke_width = max(0.25, event.stroke_width * point_scale)

    def fill_command(path: str) -> str:
        if event.fill_pattern is not None and event.fill_pattern not in (b"\x00" * 8, b"\xff" * 8):
            pattern_name = pdf_pattern_name(event.fill_pattern, (red, green, blue), point_scale)
            page.patterns[pattern_name] = (event.fill_pattern, (red, green, blue), point_scale)
            return f"q /Pattern cs /{pattern_name} scn {path} h f Q"
        return f"q {color} rg {path} h f Q"

    def xy(point: tuple[int, int]) -> tuple[float, float]:
        x, y = point
        return (x + x_shift) * point_scale, page.height - (y + y_shift) * point_scale

    if event.kind in ("rect", "oval") and len(event.points) >= 2:
        x1, y1 = xy(event.points[0])
        x2, y2 = xy(event.points[1])
        left = min(x1, x2)
        bottom = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        if width <= 0 or height <= 0:
            return
        path = f"{pdf_number(left)} {pdf_number(bottom)} {pdf_number(width)} {pdf_number(height)} re"
        if event.filled:
            command = fill_command(path)
        else:
            command = f"q {color} RG {pdf_number(stroke_width)} w {path} S Q"
        page.commands.append(pdf_apply_clip(command, event.clip, page, x_shift, y_shift, point_scale))
        return

    if event.kind == "rects" and len(event.points) >= 2:
        rect_parts: list[str] = []
        for first, second in zip(event.points[0::2], event.points[1::2]):
            x1, y1 = xy(first)
            x2, y2 = xy(second)
            left = min(x1, x2)
            bottom = min(y1, y2)
            width = abs(x2 - x1)
            height = abs(y2 - y1)
            if width <= 0 or height <= 0:
                continue
            rect_parts.append(
                f"{pdf_number(left)} {pdf_number(bottom)} {pdf_number(width)} {pdf_number(height)} re"
            )
        if not rect_parts:
            return
        command = f"q {color} rg {' '.join(rect_parts)} f Q"
        page.commands.append(pdf_apply_clip(command, event.clip, page, x_shift, y_shift, point_scale))
        return

    if event.kind == "line" and len(event.points) >= 2:
        x1, y1 = xy(event.points[0])
        x2, y2 = xy(event.points[1])
        command = (
            f"q {color} RG {pdf_number(stroke_width)} w {pdf_number(x1)} {pdf_number(y1)} m "
            f"{pdf_number(x2)} {pdf_number(y2)} l S Q"
        )
        page.commands.append(pdf_apply_clip(command, event.clip, page, x_shift, y_shift, point_scale))
        return

    if event.kind == "polygon" and len(event.points) >= 2:
        first_x, first_y = xy(event.points[0])
        parts = [f"{pdf_number(first_x)} {pdf_number(first_y)} m"]
        for point in event.points[1:]:
            x, y = xy(point)
            parts.append(f"{pdf_number(x)} {pdf_number(y)} l")
        path = " ".join(parts)
        if event.filled:
            command = fill_command(path)
        else:
            command = f"q {color} RG {pdf_number(stroke_width)} w {path} S Q"
        page.commands.append(pdf_apply_clip(command, event.clip, page, x_shift, y_shift, point_scale))


def text_horizontal_scale(
    event: PictTextEvent,
    next_event: PictTextEvent | None,
    page_width: int,
    x_shift: int,
    font_unit_scale: float,
) -> float:
    width = style_text_width(event.text, event.style, font_unit_scale)
    if width <= 0:
        return 100.0
    base_scale = max(10.0, min(400.0, event.style.tx_ratio * 100.0))
    target: float | None = None
    has_next_same_baseline = (
        next_event is not None
        and abs(next_event.y - event.y) <= 2
        and next_event.x > event.x
    )
    if has_next_same_baseline:
        target = next_event.x - event.x - 1
    else:
        target = page_width - (event.x + x_shift) - 24
    if target is None or target <= 4:
        return base_scale
    if width * base_scale / 100.0 <= target:
        return base_scale
    scale = target / width * 100.0
    return max(35.0, min(base_scale, scale))


def dpl2_adaptive_font_unit_scale(
    events: list[PictTextEvent | PictImageEvent | PictVectorEvent],
    default_scale: float,
) -> float:
    text_events = [event for event in events if isinstance(event, PictTextEvent)]
    if len(text_events) < 100:
        return default_scale
    counts: dict[int, int] = {}
    for event in text_events:
        counts[event.style.size_half_points] = counts.get(event.style.size_half_points, 0) + 1
    candidates: list[float] = []
    for size_half_points, count in counts.items():
        if count < 100 or size_half_points <= 0:
            continue
        baselines = sorted({event.y for event in text_events if event.style.size_half_points == size_half_points})
        deltas = [next_y - y for y, next_y in zip(baselines, baselines[1:]) if 2 <= next_y - y <= 200]
        if len(deltas) < 20:
            continue
        median_delta = statistics.median(deltas)
        candidate = median_delta / (size_half_points * 1.05)
        if 0.35 <= candidate < default_scale * 0.75:
            candidates.append(candidate)
    if not candidates:
        return default_scale
    return max(0.45, min(default_scale, min(candidates)))


def pdf_text_show_operator(
    text: str,
    use_unicode: bool,
    style: StyleState,
    font_size: float,
    hscale: float,
    point_scale: float,
    raw_mac_roman: bool = False,
) -> str:
    if not text:
        return "() Tj"
    if pdf_font_family(style) == "symbol":
        raw = text.encode("mac_roman", "replace")
        return f"({pdf_escape_bytes(raw)}) Tj"
    if raw_mac_roman:
        raw = text.encode("mac_roman", "replace")
        if abs(style.space_extra) < 0.001 and abs(style.char_extra) < 0.001:
            return f"({pdf_escape_bytes(raw)}) Tj"
        scale = max(0.01, hscale / 100.0)
        denominator = max(0.01, font_size * scale)
        parts: list[str] = []
        for char in text:
            parts.append("(" + pdf_escape_bytes(char.encode("mac_roman", "replace")) + ")")
            extra = style.char_extra + (style.space_extra if char == " " else 0.0)
            if abs(extra) >= 0.001:
                parts.append(pdf_number(-extra * point_scale * 1000.0 / denominator))
        return "[ " + " ".join(parts) + " ] TJ"
    if abs(style.space_extra) < 0.001 and abs(style.char_extra) < 0.001:
        return f"{pdf_hex_unicode_cids(text) if use_unicode else '(' + pdf_escape_text(text) + ')'} Tj"
    scale = max(0.01, hscale / 100.0)
    denominator = max(0.01, font_size * scale)
    parts: list[str] = []
    for char in text:
        parts.append(pdf_hex_unicode_cids(char) if use_unicode else "(" + pdf_escape_text(char) + ")")
        extra = style.char_extra + (style.space_extra if char == " " else 0.0)
        if abs(extra) >= 0.001:
            parts.append(pdf_number(-extra * point_scale * 1000.0 / denominator))
    return "[ " + " ".join(parts) + " ] TJ"


def pdf_draw_text(
    page: PdfPage,
    event: PictTextEvent,
    next_event: PictTextEvent | None,
    page_width: int,
    x_shift: int,
    y_shift: int,
    point_scale: float,
    font_unit_scale: float,
) -> None:
    text = event.text.replace("\x00", "")
    if not text:
        return
    original_text = text
    font_name = (event.style.font_name or "").lower()
    force_unicode = False
    if font_name == "mathematicalpi-six":
        text = math_pi_six_text(text)
        force_unicode = True
    elif font_name == "futurabookfractions":
        text = futura_book_fractions_text(text)
        force_unicode = True
    use_symbol = pdf_font_family(event.style) == "symbol"
    use_unicode = False if use_symbol else force_unicode or needs_unicode_pdf_font(text)
    raw_mac_roman = False
    pfr_resource_name = pfr_resource_for_style(event.style)
    if pfr_resource_name is not None and (not use_symbol and not use_unicode or font_name in ("symbol", "mathematicalpi-six", "futurabookfractions")):
        raw_source = original_text if font_name in ("symbol", "mathematicalpi-six", "futurabookfractions") else text
        raw = raw_source.encode("mac_roman", "replace")
        metric = CURRENT_PFR_FONT_BY_RESOURCE[pfr_resource_name]
        if all(byte in metric.glyph_programs for byte in raw):
            resource_name = pfr_resource_name
            raw_mac_roman = True
            if raw_source is not text:
                text = raw_source
            use_unicode = False
        else:
            resource_name = (UNICODE_FONT_SPEC if use_unicode else pdf_font_spec_for_style(event.style)).resource_name
    else:
        resource_name = (UNICODE_FONT_SPEC if use_unicode else pdf_font_spec_for_style(event.style)).resource_name
    page.fonts.add(resource_name)
    font_size = style_font_internal_size(event.style, font_unit_scale) * point_scale
    x = (event.x + x_shift) * point_scale
    y = page.height - (event.y + y_shift) * point_scale
    red, green, blue = event.style.color or (0, 0, 0)
    hscale = text_horizontal_scale(event, next_event, page_width, x_shift, font_unit_scale)
    command = (
        "BT "
        f"/{resource_name} {pdf_number(font_size)} Tf "
        f"{pdf_number(red / 255)} {pdf_number(green / 255)} {pdf_number(blue / 255)} rg "
        f"{pdf_number(hscale)} Tz "
        f"1 0 0 1 {pdf_number(x)} {pdf_number(y)} Tm "
        f"{pdf_text_show_operator(text, use_unicode, event.style, font_size, hscale, point_scale, raw_mac_roman)} "
        "ET"
    )
    page.commands.append(pdf_apply_clip(command, event.clip, page, x_shift, y_shift, point_scale))


def make_cgdc_pdf(body: bytes, fragments: list[TextFragment]) -> bytes:
    pict_pages = find_cgdc_pict_pages(body)
    if not pict_pages:
        raise CommonGroundError("no CGDC PICT page streams found")
    page_width, page_height, x_shift, y_shift = cgdc_render_geometry(fragments, pict_pages)
    point_scale = 1.0 if max(page_width, page_height) <= 1200 else 0.24
    font_unit_scale = 0.42 if max(page_width, page_height) <= 1200 else 1.55
    encoding = cgdc_render_encoding(fragments)
    builder = PdfBuilder()
    pages: list[PdfPage] = []

    for pict_page in pict_pages:
        page = PdfPage(page_width * point_scale, page_height * point_scale)
        events = pict_page_draw_events(body, pict_page, encoding)
        if not events:
            events = fallback_cgdc_pict_page_events(body, pict_page)
        text_events = [event for event in events if isinstance(event, PictTextEvent)]
        next_text_by_offset: dict[int, PictTextEvent | None] = {}
        for index, event in enumerate(text_events):
            next_text_by_offset[event.offset] = text_events[index + 1] if index + 1 < len(text_events) else None

        image_index = 1
        for event in events:
            if isinstance(event, PictImageEvent):
                image_index = pdf_draw_image(builder, page, event.image, x_shift, y_shift, point_scale, image_index, event.clip)
            elif isinstance(event, PictVectorEvent):
                pdf_draw_vector(page, event, x_shift, y_shift, point_scale)
            else:
                if event.y < -200 or event.y > page_height + 200:
                    continue
                pdf_draw_text(
                    page,
                    event,
                    next_text_by_offset.get(event.offset),
                    page_width,
                    x_shift,
                    y_shift,
                    point_scale,
                    font_unit_scale,
                )
        pages.append(page)
    return builder.build(pages)


def make_dpl2_pdf(body: bytes, trailer: bytes = b"") -> bytes:
    page_width, page_height, dpi_x, dpi_y = dpl2_page_geometry(body)
    if dpi_x != dpi_y:
        raise CommonGroundError("DPL2 pages with non-square pixels are not supported")
    refs = parse_dpl2_resource_map(body, trailer) if trailer else []
    page_graph = parse_dpl2_page_graph(refs) if refs else {}
    resource_by_offset = {ref.data_offset: ref for ref in refs}
    resource_by_type_id = {(ref.resource_type, ref.resource_id): ref for ref in refs}
    page_graph_by_page_offset = {
        ref.data_offset: page_graph[entry.base_id]
        for ref in refs
        if ref.resource_type == "PAGE"
        for entry in page_graph.values()
        if entry.page_id == ref.resource_id and entry.base_id is not None
    }
    point_scale = 72.0 / dpi_x
    direct_size_units = not dpl2_has_explicit_page_geometry(body)
    size_mapper = dpl2_direct_size_to_units if direct_size_units else cgdc_size_to_half_points
    font_unit_scale = 1.0 if direct_size_units else 1.55
    builder = PdfBuilder()
    pages: list[PdfPage] = []

    def item_bounds(events: list[PictTextEvent | PictImageEvent | PictVectorEvent]) -> tuple[float, float, float, float] | None:
        xs: list[float] = []
        ys: list[float] = []
        for event in events:
            if isinstance(event, PictImageEvent):
                image = event.image
                if image.x is None or image.y is None:
                    continue
                width = max(1, image.width_twips // 5)
                height = max(1, image.height_twips // 5)
                xs.extend((image.x, image.x + width))
                ys.extend((image.y, image.y + height))
            elif isinstance(event, PictVectorEvent):
                for x, y in event.points:
                    xs.append(x)
                    ys.append(y)
            else:
                size = style_font_internal_size(event.style, font_unit_scale)
                width = max(1.0, style_text_width(event.text, event.style, font_unit_scale))
                xs.extend((event.x, event.x + width))
                ys.extend((event.y - size, event.y + size * 0.35))
        if not xs or not ys:
            return None
        return min(xs), min(ys), max(xs), max(ys)

    def bounds_overlap(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
        left = max(a[0], b[0])
        top = max(a[1], b[1])
        right = min(a[2], b[2])
        bottom = min(a[3], b[3])
        return right > left and bottom > top

    def common_crct_slots(items: list[Dpl2DisplayItem]) -> set[int]:
        counts: dict[int, int] = {}
        for item in items:
            for crct_id in set(item.crct_ids):
                counts[crct_id] = counts.get(crct_id, 0) + 1
        return {crct_id for crct_id, count in counts.items() if count >= 3}

    def layout_slot_reset(
        previous: Dpl2DisplayItem,
        item: Dpl2DisplayItem,
        common_slots: set[int],
    ) -> bool:
        previous_slots = set(previous.crct_ids)
        item_slots = set(item.crct_ids)
        if len(previous_slots) != 1 or not previous_slots.issubset(common_slots):
            return False
        if not item_slots or previous_slots & item_slots:
            return False
        if previous.bounds is None or item.bounds is None:
            return False
        return previous.bounds[0] < page_width * 0.25 and item.bounds[0] > page_width * 0.25

    items: list[Dpl2DisplayItem] = []
    pending_item: Dpl2DisplayItem | None = None
    next_metadata: tuple[float, float, float, float, int, int] | None = None
    force_graph_break = False

    def attach_page_metadata(
        item: Dpl2DisplayItem,
        metadata: tuple[float, float, float, float, int, int],
        graph_entry: Dpl2PageGraphEntry | None = None,
    ) -> Dpl2DisplayItem:
        left, top, right, bottom, base_id, base_variant = metadata
        if graph_entry is None:
            graph_entry = page_graph.get(base_id)
        bounds = graph_entry.bounds if graph_entry is not None and graph_entry.bounds is not None else (left, top, right, bottom)
        return replace(
            item,
            bounds=bounds,
            collision_bounds=bounds,
            base_id=base_id,
            base_variant=base_variant,
            page_id=graph_entry.page_id if graph_entry is not None else item.page_id,
            cpic_ids=graph_entry.cpic_ids if graph_entry is not None else item.cpic_ids,
            crct_ids=graph_entry.crct_ids if graph_entry is not None else item.crct_ids,
        )

    for record_offset, record in iter_dpl2_records(body):
        if len(record) >= 16 and record[8:10] == b"\x00\x01":
            expected_size = be32(record, 12)
            payload = record[16:]
            try:
                data = dpl2_lzss_decode(payload, expected_size) if expected_size != len(payload) else payload
            except CommonGroundError:
                data = payload
            metadata = dpl2_base_metadata(data)
            graph_entry = page_graph_by_page_offset.get(record_offset)
            if metadata is not None:
                if pending_item is not None:
                    if pending_item.base_id is None or pending_item.base_id == metadata[4]:
                        pending_item = attach_page_metadata(pending_item, metadata, graph_entry)
                        items.append(pending_item)
                        pending_item = None
                    else:
                        items.append(pending_item)
                        pending_item = None
                        next_metadata = metadata
                else:
                    next_metadata = metadata
            continue

        if len(record) < 16 or record[8:10] != b"\x00\x81":
            continue
        if pending_item is not None:
            items.append(pending_item)
            pending_item = None
        record_data = expand_dpl2_display_record(record)
        display_events = dpl2_pict_draw_events(record_data, size_mapper=size_mapper)
        base_ref = resource_by_offset.get(record_offset)
        base_id = base_ref.resource_id if base_ref is not None and base_ref.resource_type == "BASE" else None
        graph_entry = page_graph.get(base_id) if base_id is not None else None
        graph_bounds = graph_entry.bounds if graph_entry is not None else None
        cpic_events: list[PictVectorEvent] = []
        if graph_entry is not None and graph_entry.cpic_refs:
            selected_refs = [entry for entry in graph_entry.cpic_refs if entry[2] == dpi_x]
            if not selected_refs:
                max_resolution = max(entry[2] for entry in graph_entry.cpic_refs)
                selected_refs = [entry for entry in graph_entry.cpic_refs if entry[2] == max_resolution]
            for cpic_id, _, cpic_resolution in selected_refs:
                cpic_ref = resource_by_type_id.get(("CPIC", cpic_id))
                if cpic_ref is not None:
                    try:
                        cpic_events.extend(dpl2_cpic_draw_events(cpic_ref, graph_bounds, cpic_resolution, dpi_x))
                    except CommonGroundError:
                        pass
        if graph_entry is not None and graph_entry.cpic_refs and not cpic_events and dpl2_nonvisual_cpic_label(display_events):
            continue
        events = cpic_events + display_events
        if not events:
            if graph_entry is not None and graph_entry.bounds is None:
                force_graph_break = True
            continue

        visual_bounds = item_bounds(events)
        pending_item = Dpl2DisplayItem(
            tuple(events),
            graph_bounds or visual_bounds,
            graph_bounds or visual_bounds,
            base_id=base_id,
            page_id=graph_entry.page_id if graph_entry is not None else None,
            cpic_ids=graph_entry.cpic_ids if graph_entry is not None else (),
            crct_ids=graph_entry.crct_ids if graph_entry is not None else (),
            break_before=force_graph_break,
        )
        force_graph_break = False
        if next_metadata is not None:
            if base_id is None or next_metadata[4] == base_id:
                pending_item = attach_page_metadata(pending_item, next_metadata)
                items.append(pending_item)
                pending_item = None
            next_metadata = None

    if pending_item is not None:
        items.append(pending_item)

    if not direct_size_units:
        all_events = [event for item in items for event in item.events]
        font_unit_scale = dpl2_adaptive_font_unit_scale(all_events, font_unit_scale)

    item_groups: list[list[Dpl2DisplayItem]] = []
    current_group: list[Dpl2DisplayItem] = []
    common_slots = common_crct_slots(items)
    for item in items:
        item_collision_bounds = item.collision_bounds or item.bounds
        collides = (
            item_collision_bounds is not None
            and any(
                (existing_bounds := existing.collision_bounds or existing.bounds) is not None
                and bounds_overlap(existing_bounds, item_collision_bounds)
                for existing in current_group
            )
        )
        resets_layout = bool(current_group) and layout_slot_reset(current_group[-1], item, common_slots)
        if current_group and (item.break_before or collides or resets_layout):
            item_groups.append(current_group)
            current_group = []
        current_group.append(item)
    if current_group:
        item_groups.append(current_group)
    for items in item_groups:
        events = [event for item in items for event in item.events]
        page = PdfPage(page_width * point_scale, page_height * point_scale)
        next_text_by_offset: dict[int, PictTextEvent | None] = {}
        text_events = [event for event in events if isinstance(event, PictTextEvent)]
        for index, event in enumerate(text_events):
            next_text_by_offset[event.offset] = text_events[index + 1] if index + 1 < len(text_events) else None
        image_index = 1
        for event in events:
            if isinstance(event, PictImageEvent):
                image_index = pdf_draw_image(builder, page, event.image, 0, 0, point_scale, image_index, event.clip)
            elif isinstance(event, PictVectorEvent):
                pdf_draw_vector(page, event, 0, 0, point_scale)
            else:
                if event.y < -200 or event.y > page_height + 200:
                    continue
                pdf_draw_text(
                    page,
                    event,
                    next_text_by_offset.get(event.offset),
                    page_width,
                    0,
                    0,
                    point_scale,
                    font_unit_scale,
                )
        if page.commands:
            pages.append(page)
    if not pages:
        raise CommonGroundError("no supported DPL2 display text records found")
    return builder.build(pages)


def make_flow_pdf(fragments: list[TextFragment], kind: str) -> bytes:
    lines = fragments_to_lines(fragments, kind)
    if not lines:
        raise CommonGroundError("no supported text drawing operators found")
    builder = PdfBuilder()
    pages: list[PdfPage] = []
    page = PdfPage(612, 792)
    page.fonts.add("FTimes")
    x = 54
    y = 738
    for line in lines:
        for chunk in re.findall(r".{1,92}(?:\\s+|$)|\\S+", line):
            text = chunk.strip()
            if not text:
                continue
            page.commands.append(
                "BT /FTimes 10 Tf 0 0 0 rg 1 0 0 1 "
                f"{pdf_number(x)} {pdf_number(y)} Tm ({pdf_escape_text(text)}) Tj ET"
            )
            y -= 13
            if y < 54:
                pages.append(page)
                page = PdfPage(612, 792)
                page.fonts.add("FTimes")
                y = 738
    pages.append(page)
    return builder.build(pages)


def make_document_pdf(
    fragments: list[TextFragment],
    kind: str,
    body: bytes | None = None,
    trailer: bytes = b"",
) -> bytes:
    if kind == "DPL2":
        if body is None:
            raise CommonGroundError("DPL2 body is required for PDF conversion")
        expand_dpl2_resource_records(body)
        return make_dpl2_pdf(body, trailer)
    if kind == "CGDC" and body is not None and find_cgdc_pict_pages(body):
        return make_cgdc_pdf(body, fragments)
    return make_flow_pdf(fragments, kind)


def convert(input_path: Path, output_path: Path) -> tuple[str, int]:
    global CURRENT_PFR_METRICS, CURRENT_PFR_FONT_RESOURCES, CURRENT_PFR_FONT_BY_RESOURCE
    global CURRENT_PFR_STYLE_METRICS, CURRENT_PFR_STYLE_FONT_RESOURCES
    raw = input_path.read_bytes()
    payload = parse_payload(raw)
    segment = parse_segment(payload.data)
    if segment.kind == "DPL2":
        refs = parse_dpl2_resource_map(segment.body, segment.trailer)
        validate_dpl2_body_byte_coverage(segment.body, refs)
        size_mapper = dpl2_size_mapper_for_body(segment.body)
        all_pfr_metrics = dpl2_pfr_metrics(segment.body, segment.trailer, include_unnamed=True)
        CURRENT_PFR_METRICS = {key: metric for key, metric in all_pfr_metrics.items() if not key.startswith("\x00unnamed:")}
        CURRENT_PFR_STYLE_METRICS = infer_dpl2_pfr_style_metrics(segment.body, all_pfr_metrics, size_mapper)
        CURRENT_PFR_FONT_RESOURCES = {}
        CURRENT_PFR_STYLE_FONT_RESOURCES = {}
        CURRENT_PFR_FONT_BY_RESOURCE = {}
        for index, (font_name, metric) in enumerate(sorted(CURRENT_PFR_METRICS.items())):
            if metric.glyph_programs and not font_name.startswith("\x00"):
                resource_name = f"FPFR{index}"
                CURRENT_PFR_FONT_RESOURCES[font_name] = resource_name
                CURRENT_PFR_FONT_BY_RESOURCE[resource_name] = metric
        for index, (style_key, metric) in enumerate(sorted(CURRENT_PFR_STYLE_METRICS.items()), start=len(CURRENT_PFR_FONT_RESOURCES)):
            if metric.glyph_programs:
                resource_name = f"FPFR{index}"
                CURRENT_PFR_STYLE_FONT_RESOURCES[style_key] = resource_name
                CURRENT_PFR_FONT_BY_RESOURCE[resource_name] = metric
    else:
        CURRENT_PFR_METRICS = {}
        CURRENT_PFR_FONT_RESOURCES = {}
        CURRENT_PFR_FONT_BY_RESOURCE = {}
        CURRENT_PFR_STYLE_METRICS = {}
        CURRENT_PFR_STYLE_FONT_RESOURCES = {}
    fragments = scan_text_fragments(segment.body, segment.kind)
    pdf = make_document_pdf(fragments, segment.kind, segment.body, segment.trailer)
    tmp = output_path.with_suffix(output_path.suffix + ".tmp")
    tmp.write_bytes(pdf)
    os.chmod(tmp, 0o664)
    tmp.replace(output_path)
    os.chmod(output_path, 0o664)
    return segment.kind, len(fragments)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Convert Common Ground Digital Paper to PDF")
    parser.add_argument("inputFile")
    parser.add_argument("outputFile")
    args = parser.parse_args(argv)

    input_path = Path(args.inputFile)
    output_path = Path(args.outputFile)
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        kind, count = convert(input_path, output_path)
    except Exception as exc:
        try:
            if output_path.exists():
                output_path.unlink()
            tmp = output_path.with_suffix(output_path.suffix + ".tmp")
            if tmp.exists():
                tmp.unlink()
        finally:
            print(f"commonGround: {exc}", file=sys.stderr)
        return 1

    print(f"converted {input_path} -> {output_path} ({kind}, {count} text/image operators)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

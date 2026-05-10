#!/usr/bin/env python3
# Vibe coded by Codex
"""Render NAPLPS drawing streams to PNG.

This converter implements the NAPLPS profile used by the sample0 corpus:
PDI graphics in 7-bit and 8-bit forms, text, mosaics, color modes, fields,
incremental bitmaps, and the C0/C1 controls that occur in the files.
"""

from __future__ import annotations

import math
import os
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


WIDTH = 640
HEIGHT = 480
VISIBLE_Y = 0.75
AA = 3

ASCII_WIDTH_CLASSES = [
    [9, 5, 9, 5, 1, 5],
    [0, 1, 5, 6, 5, 5],
    [4, 5, 5, 5, 5, 5],
    [6, 5, 5, 5, 5, 5],
    [9, 5, 5, 9, 5, 2],
    [9, 5, 5, 5, 5, 5],
    [9, 5, 5, 9, 5, 9],
    [0, 5, 8, 9, 5, 9],
    [1, 5, 5, 9, 5, 9],
    [1, 5, 2, 9, 0, 5],
    [9, 0, 5, 9, 4, 5],
    [9, 3, 5, 4, 5, 5],
    [3, 5, 5, 9, 0, 0],
    [5, 8, 9, 4, 9, 5],
    [0, 5, 5, 2, 5, 9],
    [9, 8, 9, 9, 5, 9],
]

PROP_SPACING_SMALL = {
    6: [2, 3, 4, 3, 4, 5, 6, 4, 5, 6],
    7: [3, 4, 5, 4, 5, 6, 7, 5, 6, 7],
    8: [2, 3, 4, 4, 5, 6, 7, 6, 7, 8],
    9: [3, 4, 5, 5, 6, 7, 8, 7, 8, 9],
    10: [4, 5, 6, 6, 7, 8, 9, 8, 9, 10],
    11: [3, 4, 6, 6, 7, 8, 10, 8, 10, 11],
}

PROP_SPACING_ADJUST = [6, 5, 4, 4, 3, 2, 1, 2, 1, 0]


class NaplpsError(Exception):
    pass


DEFAULT_PALETTE = [
    (0, 0, 0),
    (32, 32, 32),
    (65, 65, 65),
    (97, 97, 97),
    (130, 130, 130),
    (158, 158, 158),
    (190, 190, 190),
    (223, 223, 223),
    (0, 0, 255),
    (190, 0, 255),
    (255, 0, 130),
    (255, 65, 0),
    (255, 255, 0),
    (65, 255, 0),
    (0, 255, 130),
    (0, 190, 255),
]


def clamp(v: int, lo: int = 0, hi: int = 255) -> int:
    return max(lo, min(hi, v))


def scale_bits(value: int, bits: int) -> int:
    if bits <= 0:
        return 0
    return clamp(round(value * 255 / ((1 << bits) - 1)))


def data_value(byte: int) -> int:
    return byte & 0x3F


def chunked_with_pad(values: list[int], size: int) -> Iterable[list[int]]:
    if size <= 0:
        raise NaplpsError("invalid operand size")
    for i in range(0, len(values), size):
        chunk = values[i : i + size]
        if chunk:
            yield chunk + [0] * (size - len(chunk))


@dataclass
class TextState:
    width: float = 1 / 40
    height: float = 5 / 128
    path: int = 0
    rotation: int = 0
    inter_char: float = 1.0
    proportional: bool = False
    inter_row: float = 1.0
    cursor_style: int = 0
    cursor_relation: int = 0
    underline: bool = False
    reverse: bool = False
    cursor_visible: bool = False
    cursor_blink: bool = False
    wrap: bool = False
    scroll: bool = False
    pending_auto_crlf: bool = False


@dataclass
class State:
    image: Image.Image = field(default_factory=lambda: Image.new("RGB", (WIDTH * AA, HEIGHT * AA), (0, 0, 0)))
    draw: ImageDraw.ImageDraw = field(init=False)
    gl: str = "G0"
    gr: str = "G1"
    gsets: dict[str, str] = field(default_factory=lambda: {"G0": "ASCII", "G1": "PDI", "G2": "SUPP", "G3": "MOSAIC"})
    single_len: int = 1
    multi_len: int = 3
    dimensions: int = 2
    pel: tuple[float, float] = (0.0, 0.0)
    point: tuple[float, float] = (0.0, 0.0)
    cursor: tuple[float, float] = (0.0, VISIBLE_Y - 5 / 128)
    field_origin: tuple[float, float] = (0.0, 0.0)
    field_size: tuple[float, float] = (1.0, 1.0)
    text: TextState = field(default_factory=TextState)
    palette: list[tuple[int, int, int]] = field(default_factory=lambda: list(DEFAULT_PALETTE))
    palette_used: set[int] = field(default_factory=set)
    color_mode: int = 0
    fg_index: int = 7
    bg_index: int = 0
    fg: tuple[int, int, int] = (223, 223, 223)
    bg: tuple[int, int, int] = (0, 0, 0)
    fill_pattern: int = 0
    outline_filled: bool = False
    line_texture: int = 0
    texture_mask_size: tuple[float, float] = (1 / 40, 5 / 128)
    programmable_textures: dict[str, bytes] = field(default_factory=dict)
    macros: dict[int, bytes] = field(default_factory=dict)
    drcs: dict[int, bytes] = field(default_factory=dict)
    unprotected_fields: list[tuple[tuple[float, float], tuple[float, float]]] = field(default_factory=list)
    top_overflow_regions: list[tuple[float, float, float]] = field(default_factory=list)
    last_spacing_byte: int | None = None

    def __post_init__(self) -> None:
        self.draw = ImageDraw.Draw(self.image)

    def reset_environment(self, keep_palette: bool = True) -> None:
        self.gl = "G0"
        self.gr = "G1"
        self.gsets = {"G0": "ASCII", "G1": "PDI", "G2": "SUPP", "G3": "MOSAIC"}
        self.single_len = 1
        self.multi_len = 3
        self.dimensions = 2
        self.pel = (0.0, 0.0)
        self.point = (0.0, 0.0)
        self.cursor = (0.0, VISIBLE_Y - 5 / 128)
        self.field_origin = (0.0, 0.0)
        self.field_size = (1.0, 1.0)
        self.text = TextState()
        self.color_mode = 0
        self.fg_index = 7
        self.bg_index = 0
        self.fg = self.palette[7]
        self.bg = self.palette[0]
        self.fill_pattern = 0
        self.outline_filled = False
        self.line_texture = 0
        self.texture_mask_size = (1 / 40, 5 / 128)
        self.last_spacing_byte = None
        self.unprotected_fields.clear()
        self.top_overflow_regions.clear()
        if not keep_palette:
            self.palette = list(DEFAULT_PALETTE)
            self.palette_used = set()

    def xy(self, p: tuple[float, float]) -> tuple[int, int]:
        x = round(p[0] * WIDTH * AA)
        y = round((1 - p[1] / VISIBLE_Y) * HEIGHT * AA)
        return x, y

    def dist_x(self, v: float) -> int:
        return max(1, round(abs(v) * WIDTH * AA))

    def dist_y(self, v: float) -> int:
        return max(1, round(abs(v) / VISIBLE_Y * HEIGHT * AA))

    def line_width(self) -> int:
        px = self.dist_x(self.pel[0]) if self.pel[0] else 1
        py = self.dist_y(self.pel[1]) if self.pel[1] else 1
        return max(1, int(round((px + py) / 2)))

    def current_color(self) -> tuple[int, int, int]:
        return self.fg

    def clear(self, color: tuple[int, int, int] | None = None) -> None:
        self.draw.rectangle([0, 0, WIDTH * AA, HEIGHT * AA], fill=color or (0, 0, 0))

    def set_point(self, p: tuple[float, float], sync_cursor: bool = True) -> None:
        self.point = p
        if sync_cursor and self.text.cursor_relation in (0, 2):
            self.cursor = p

    def set_cursor(self, p: tuple[float, float], sync_point: bool = True) -> None:
        self.cursor = p
        if sync_point and self.text.cursor_relation in (0, 1):
            self.point = p

    def final_image(self) -> Image.Image:
        if AA == 1:
            return self.image
        return self.image.resize((WIDTH, HEIGHT), Image.Resampling.BOX)


class Renderer:
    def __init__(self, data: bytes):
        self.data = data
        self.state = State()
        self.pending_pdi: int | None = None
        self.pending_data: list[int] = []
        self.pdi_seen = False
        self.ss: str | None = None
        self.in_definition: int | None = None
        self.definition_key: int | None = None
        self.definition_data = bytearray()
        self.texture_cache: dict[tuple[str, int, int], Image.Image] = {}
        self.macro_depth = 0

    def parse(self) -> Image.Image:
        if not self.data:
            raise NaplpsError("empty input")
        self.execute_bytes(self.data)
        self.flush_pdi()
        if not self.pdi_seen:
            raise NaplpsError("input contains no NAPLPS PDI records")
        self.draw_cursor()
        return self.state.final_image()

    def execute_bytes(self, data: bytes) -> None:
        old_data = self.data
        self.data = data
        i = 0
        while i < len(self.data):
            i = self.consume_at(i)
        self.data = old_data

    def consume_at(self, i: int) -> int:
        b = self.data[i]
        if self.in_definition is not None:
            return self.consume_definition(i)
        if b == 0x1B:
            self.flush_pdi()
            return self.consume_escape(i)
        if b in (0x0E, 0x0F, 0x19, 0x1D):
            self.flush_pdi()
            self.shift(b)
            return i + 1
        if b < 0x20:
            self.flush_pdi()
            return self.consume_c0(i)
        if 0x80 <= b <= 0x9F:
            self.flush_pdi()
            return self.consume_c1(i, b)

        pdi_kind = self.pdi_class(b)
        if pdi_kind == "command":
            self.flush_pdi()
            self.pending_pdi = b & 0x7F
            self.pdi_seen = True
            return i + 1
        if pdi_kind == "data":
            if self.pending_pdi is None:
                raise NaplpsError(f"PDI data byte {b:02X} without active PDI at offset {i}")
            self.pending_data.append(data_value(b))
            return i + 1

        self.flush_pdi()
        self.display_graphic_byte(b)
        return i + 1

    def consume_definition(self, i: int) -> int:
        b = self.data[i]
        if b == 0x1B and i + 1 < len(self.data) and 0x40 <= self.data[i + 1] <= 0x5F:
            c1 = self.data[i + 1] + 0x40
            if c1 in (0x80, 0x81, 0x82, 0x83, 0x84, 0x85):
                self.finish_definition()
                return self.consume_c1(i + 1, c1, escaped=True)
        if b in (0x80, 0x81, 0x82, 0x83, 0x84, 0x85):
            self.finish_definition()
            return self.consume_c1(i, b)
        self.definition_data.append(b)
        return i + 1

    def finish_definition(self) -> None:
        if self.definition_key is not None:
            body = bytes(self.definition_data)
            if self.in_definition in (0x80, 0x81):
                if body:
                    self.state.macros[self.definition_key] = body
                else:
                    self.state.macros.pop(self.definition_key, None)
            elif self.in_definition == 0x83:
                if body:
                    self.state.drcs[self.definition_key] = body
                else:
                    self.state.drcs.pop(self.definition_key, None)
            elif self.in_definition == 0x84:
                key = chr(self.definition_key)
                if body:
                    self.state.programmable_textures[key] = body
                else:
                    self.state.programmable_textures.pop(key, None)
                self.texture_cache.clear()
        self.in_definition = None
        self.definition_key = None
        self.definition_data.clear()

    def pdi_class(self, b: int) -> str | None:
        if 0xA0 <= b <= 0xBF and self.state.gr == "G1" and self.state.gsets.get("G1") == "PDI":
            return "command"
        if 0xC0 <= b <= 0xFF and self.state.gr == "G1" and self.state.gsets.get("G1") == "PDI":
            return "data"
        active = self.ss or self.state.gl
        if self.state.gsets.get(active) != "PDI":
            return None
        if 0x20 <= b <= 0x3F:
            return "command"
        if 0x40 <= b <= 0x7F:
            return "data"
        return None

    def shift(self, b: int) -> None:
        if b == 0x0E:
            self.state.gl = "G1"
        elif b == 0x0F:
            self.state.gl = "G0"
        elif b == 0x19:
            self.ss = "G2"
        elif b == 0x1D:
            self.ss = "G3"

    def consume_escape(self, i: int) -> int:
        if i + 1 >= len(self.data):
            raise NaplpsError("trailing ESC")
        b = self.data[i + 1]
        if 0x40 <= b <= 0x5F:
            return self.consume_c1(i + 1, b + 0x40, escaped=True)
        if b in (0x6E, 0x6F, 0x7E, 0x7D, 0x7C, 0x6B, 0x6C, 0x6D):
            if b == 0x6E:
                self.state.gl = "G2"
            elif b == 0x6F:
                self.state.gl = "G3"
            elif b in (0x7E, 0x6B):
                self.state.gr = "G1"
            elif b in (0x7D, 0x6C):
                self.state.gr = "G2"
            elif b in (0x7C, 0x6D):
                self.state.gr = "G3"
            return i + 2
        if b in (0x21, 0x22):
            if i + 2 >= len(self.data):
                raise NaplpsError("trailing control designation")
            return i + 3
        if b in (0x28, 0x29, 0x2A, 0x2B, 0x2D, 0x2E, 0x2F):
            return self.consume_designation(i)
        if b == 0x25:
            if i + 2 >= len(self.data):
                raise NaplpsError("trailing NAPLPS delimiter")
            return i + 3
        if b == 0x24:
            if i + 3 >= len(self.data):
                raise NaplpsError("trailing multi-byte G-set designation")
            if self.data[i + 2] == 0x2B:
                self.state.gsets["G3"] = "DBCS"
                return i + 4
            return i + 3
        raise NaplpsError(f"unsupported ESC sequence at offset {i}: ESC {b:02X}")

    def consume_designation(self, i: int) -> int:
        inter = self.data[i + 1]
        if i + 2 >= len(self.data):
            raise NaplpsError("trailing G-set designation")
        target_map_94 = {0x28: "G0", 0x29: "G1", 0x2A: "G2", 0x2B: "G3"}
        target_map_96 = {0x29: "G1", 0x2A: "G2", 0x2B: "G3", 0x2D: "G1", 0x2E: "G2", 0x2F: "G3"}
        if inter in target_map_94 and self.data[i + 2] in (0x42, 0x7C):
            self.state.gsets[target_map_94[inter]] = "ASCII" if self.data[i + 2] == 0x42 else "SUPP"
            return i + 3
        if inter in target_map_96:
            if self.data[i + 2] == 0x20:
                if i + 3 >= len(self.data):
                    raise NaplpsError("trailing extended G-set designation")
                final = self.data[i + 3]
                consumed = 4
            else:
                final = self.data[i + 2]
                consumed = 3
            names = {0x57: "PDI", 0x7D: "MOSAIC", 0x7A: "MACRO", 0x7B: "DRCS"}
            if final not in names:
                raise NaplpsError(f"unknown G-set designation final {final:02X}")
            self.state.gsets[target_map_96[inter]] = names[final]
            return i + consumed
        raise NaplpsError(f"unknown G-set designation at offset {i}")

    def consume_c0(self, i: int) -> int:
        b = self.data[i]
        s = self.state
        if s.text.pending_auto_crlf and b in (0x0A, 0x0B, 0x0D):
            return i + 1
        s.text.pending_auto_crlf = False
        if b in (0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x1A):
            return i + 1
        if b == 0x08:
            self.advance_cursor(-s.text.inter_char, 0)
            return i + 1
        if b == 0x09:
            self.advance_cursor(s.text.inter_char * 4, 0)
            return i + 1
        if b == 0x0A:
            self.linefeed(1)
            return i + 1
        if b == 0x0B:
            self.linefeed(-1)
            return i + 1
        if b == 0x0C:
            s.clear(s.bg if s.color_mode == 2 else (0, 0, 0))
            s.set_cursor((0.0, VISIBLE_Y - abs(s.text.height)))
            return i + 1
        if b == 0x0D:
            self.carriage_return()
            return i + 1
        if b == 0x1C:
            if i + 2 >= len(self.data):
                raise NaplpsError("trailing cursor-position control")
            r, c = self.data[i + 1], self.data[i + 2]
            if r < 0x20 or c < 0x20 or 0x80 <= r <= 0x9F or 0x80 <= c <= 0x9F:
                return i + 3
            row = (r & 0x7F) - 32
            col = (c & 0x7F) - 32
            s.set_cursor((col * abs(s.text.width), row * abs(s.text.height)))
            return i + 3
        if b == 0x1E:
            s.set_cursor((0.0, VISIBLE_Y - abs(s.text.height)))
            return i + 1
        if b == 0x1F:
            s.reset_environment(keep_palette=True)
            if i + 2 < len(self.data) and 0x40 <= self.data[i + 1] <= 0x7F and 0x40 <= self.data[i + 2] <= 0x7F:
                row = self.data[i + 1] & 0x3F
                col = self.data[i + 2] & 0x3F
                s.set_cursor((col * abs(s.text.width), VISIBLE_Y - (row + 1) * abs(s.text.height)))
                return i + 3
            return i + 1
        raise NaplpsError(f"unsupported C0 {b:02X} at offset {i}")

    def consume_c1(self, i: int, b: int, escaped: bool = False) -> int:
        s = self.state
        if b in (0x80, 0x81, 0x82, 0x83, 0x84):
            if i + 1 >= len(self.data):
                raise NaplpsError("trailing definition control")
            key = self.data[i + 1]
            if b == 0x84 and key not in (0x41, 0x42, 0x43, 0x44):
                return i + 2
            if b != 0x84 and not (0x20 <= key <= 0x7F):
                return i + 2
            self.in_definition = b
            self.definition_key = key
            self.definition_data.clear()
            return i + 2
        if b == 0x85:
            return i + 1
        if b == 0x86:
            if i + 1 >= len(self.data):
                raise NaplpsError("trailing REPEAT")
            count_byte = self.data[i + 1]
            if not (0x40 <= count_byte <= 0x7F or 0xC0 <= count_byte <= 0xFF):
                return i + 1
            if s.last_spacing_byte is not None:
                for _ in range(data_value(count_byte)):
                    self.display_graphic_byte(s.last_spacing_byte, repeated=True)
            return i + 2
        if b == 0x87:
            if s.last_spacing_byte is not None:
                limit = int(max(0, (1.0 - s.cursor[0]) / max(abs(s.text.width), 1e-9)))
                for _ in range(min(limit, 200)):
                    self.display_graphic_byte(s.last_spacing_byte, repeated=True)
            return i + 1
        if b == 0x88:
            s.text.reverse = True
            return i + 1
        if b == 0x89:
            s.text.reverse = False
            return i + 1
        if b == 0x8A:
            s.text.width, s.text.height = 1 / 80, 5 / 128
            return i + 1
        if b == 0x8B:
            s.text.width, s.text.height = 1 / 32, 3 / 64
            return i + 1
        if b == 0x8C:
            s.text.width, s.text.height = 1 / 40, 5 / 128
            return i + 1
        if b == 0x8D:
            s.text.width, s.text.height = 1 / 40, 5 / 64
            return i + 1
        if b == 0x8E:
            s.text.cursor_blink = True
            return i + 1
        if b == 0x8F:
            s.text.width, s.text.height = 1 / 20, 5 / 64
            return i + 1
        if b == 0x90:
            s.unprotected_fields = [
                field for field in s.unprotected_fields
                if not self.fields_overlap(field, (s.field_origin, s.field_size))
            ]
            return i + 1
        if b in (0x91, 0x92, 0x93, 0x94):
            return i + 1
        if b == 0x95:
            s.text.wrap = True
            return i + 1
        if b == 0x96:
            s.text.wrap = False
            return i + 1
        if b == 0x97:
            s.text.scroll = True
            return i + 1
        if b == 0x98:
            s.text.scroll = False
            return i + 1
        if b == 0x99:
            s.text.underline = True
            return i + 1
        if b == 0x9A:
            s.text.underline = False
            return i + 1
        if b in (0x9B, 0x9C):
            s.text.cursor_visible = True
            s.text.cursor_blink = b == 0x9B
            return i + 1
        if b == 0x9D:
            s.text.cursor_visible = False
            return i + 1
        if b == 0x9E:
            s.text.cursor_blink = False
            return i + 1
        if b == 0x9F:
            active = (s.field_origin, s.field_size)
            s.unprotected_fields = [field for field in s.unprotected_fields if not self.fields_overlap(field, active)]
            s.unprotected_fields.append(active)
            return i + 1
        raise NaplpsError(f"unsupported C1 {b:02X} at offset {i}")

    def flush_pdi(self) -> None:
        if self.pending_pdi is None:
            return
        self.state.text.pending_auto_crlf = False
        code = self.pending_pdi
        values = self.pending_data
        self.pending_pdi = None
        self.pending_data = []
        self.execute_pdi(code, values)

    def execute_pdi(self, code: int, values: list[int]) -> None:
        if code == 0x20:
            self.pdi_reset(values)
        elif code == 0x21:
            self.pdi_domain(values)
        elif code == 0x22:
            self.pdi_text(values)
        elif code == 0x23:
            self.pdi_texture(values)
        elif code in (0x24, 0x25, 0x26, 0x27):
            self.pdi_point(code, values)
        elif code in (0x28, 0x29, 0x2A, 0x2B):
            self.pdi_line(code, values)
        elif code in (0x2C, 0x2D, 0x2E, 0x2F):
            self.pdi_arc(code, values)
        elif code in (0x30, 0x31, 0x32, 0x33):
            self.pdi_rect(code, values)
        elif code in (0x34, 0x35, 0x36, 0x37):
            self.pdi_polygon(code, values)
        elif code == 0x38:
            self.pdi_field(values)
        elif code == 0x39:
            self.pdi_incremental_point(values)
        elif code in (0x3A, 0x3B):
            self.pdi_incremental_line(code, values)
        elif code == 0x3C:
            self.pdi_set_color(values)
        elif code == 0x3D:
            if values and values[0] != 0x1C:
                return
        elif code == 0x3E:
            self.pdi_select_color(values)
        elif code == 0x3F:
            return
        else:
            raise NaplpsError(f"unknown PDI {code:02X}")

    def field_rect(self, field: tuple[tuple[float, float], tuple[float, float]]) -> tuple[float, float, float, float]:
        (x, y), (w, h) = field
        x0, x1 = sorted((x, x + w))
        y0, y1 = sorted((y, y + h))
        return x0, y0, x1, y1

    def fields_overlap(
        self,
        a: tuple[tuple[float, float], tuple[float, float]],
        b: tuple[tuple[float, float], tuple[float, float]],
    ) -> bool:
        ax0, ay0, ax1, ay1 = self.field_rect(a)
        bx0, by0, bx1, by1 = self.field_rect(b)
        return ax0 < bx1 and bx0 < ax1 and ay0 < by1 and by0 < ay1

    def pdi_reset(self, values: list[int]) -> None:
        s = self.state
        a = values[0] if values else 0
        b = values[1] if len(values) > 1 else 0
        if a & 0x01:
            s.single_len = 1
            s.multi_len = 3
            s.dimensions = 2
            s.pel = (0.0, 0.0)
        color_bits = (a >> 1) & 0x03
        if color_bits:
            s.palette = list(DEFAULT_PALETTE)
            s.palette_used = set()
            s.color_mode = 1 if color_bits == 3 else 0
            s.fg_index = 7
            s.bg_index = 0
            s.fg = s.palette[7]
            s.bg = s.palette[0]
        screen_bits = (a >> 3) & 0x07
        if screen_bits in (1, 7):
            s.clear((0, 0, 0))
        elif screen_bits in (2, 5, 6):
            s.clear(s.current_color())
        if b & 0x01:
            s.text = TextState()
            s.cursor = (0.0, VISIBLE_Y - s.text.height)
            s.field_origin = (0.0, 0.0)
            s.field_size = (1.0, 1.0)
            s.top_overflow_regions.clear()
        if b & 0x08:
            s.fill_pattern = 0
            s.outline_filled = False
            s.line_texture = 0
            s.texture_mask_size = (1 / 40, 5 / 128)
        if b & 0x10:
            s.macros.clear()
        if b & 0x20:
            s.drcs.clear()

    def pdi_domain(self, values: list[int]) -> None:
        if not values:
            return
        s = self.state
        fixed = values[0]
        s.dimensions = 3 if fixed & 0x20 else 2
        s.multi_len = ((fixed >> 2) & 0x07) + 1
        s.single_len = (fixed & 0x03) + 1
        rest = values[1:]
        if rest:
            s.pel = self.decode_multi(rest[: s.multi_len])

    def pdi_text(self, values: list[int]) -> None:
        s = self.state
        a = values[0] if values else 0
        b = values[1] if len(values) > 1 else 0
        spacings = [1.0, 1.25, 1.5, 1.0]
        spacing_code = (a >> 4) & 0x03
        s.text.proportional = spacing_code == 0x03
        s.text.inter_char = spacings[spacing_code]
        s.text.path = (a >> 2) & 0x03
        s.text.rotation = a & 0x03
        s.text.cursor_style = (b >> 4) & 0x03
        s.text.cursor_relation = (b >> 2) & 0x03
        row_spacings = [1.0, 1.25, 1.5, 2.0]
        s.text.inter_row = row_spacings[b & 0x03]
        rest = values[2:]
        if rest:
            s.text.width, s.text.height = self.decode_multi(rest[: s.multi_len])

    def pdi_texture(self, values: list[int]) -> None:
        if not values:
            return
        s = self.state
        fixed = values[0]
        s.fill_pattern = (fixed >> 3) & 0x07
        s.outline_filled = bool((fixed >> 2) & 0x01)
        s.line_texture = fixed & 0x03
        rest = values[1:]
        if rest:
            s.texture_mask_size = self.decode_multi(rest[: s.multi_len])

    def pdi_point(self, code: int, values: list[int]) -> None:
        s = self.state
        relative = code in (0x25, 0x27)
        draw = code in (0x26, 0x27)
        for op in chunked_with_pad(values, s.multi_len):
            p = self.decode_multi(op)
            if relative:
                p = (s.point[0] + p[0], s.point[1] + p[1])
            s.set_point(p)
            if draw:
                self.draw_pel(p)

    def pdi_line(self, code: int, values: list[int]) -> None:
        s = self.state
        relative = code in (0x29, 0x2B)
        set_first = code in (0x2A, 0x2B)
        ops = [self.decode_multi(op) for op in chunked_with_pad(values, s.multi_len)]
        if not ops:
            return
        if set_first:
            first = ops.pop(0)
            s.set_point((s.point[0] + first[0], s.point[1] + first[1]) if relative else first)
        for p in ops:
            end = (s.point[0] + p[0], s.point[1] + p[1]) if relative else p
            self.draw_line(s.point, end)
            s.set_point(end)

    def pdi_arc(self, code: int, values: list[int]) -> None:
        s = self.state
        filled = code in (0x2D, 0x2F)
        set_first = code in (0x2E, 0x2F)
        pts = [self.decode_multi(op) for op in chunked_with_pad(values, s.multi_len)]
        if set_first and pts:
            s.set_point(pts.pop(0))
        start = s.point
        if len(pts) < 1:
            return
        if len(pts) == 1:
            mid, end = (start[0] + pts[0][0], start[1] + pts[0][1]), start
            path = self.arc_points(start, mid, end)
            if filled:
                self.fill_polygon(path)
            self.draw_polyline(path)
            s.set_point(end)
            return
        idx = 0
        cur = start
        while idx + 1 < len(pts):
            mid = (cur[0] + pts[idx][0], cur[1] + pts[idx][1])
            end = (mid[0] + pts[idx + 1][0], mid[1] + pts[idx + 1][1])
            path = self.arc_points(cur, mid, end)
            if filled:
                self.fill_polygon(path + [cur])
            self.draw_polyline(path)
            cur = end
            idx += 2
        s.set_point(cur)

    def pdi_rect(self, code: int, values: list[int]) -> None:
        s = self.state
        filled = code in (0x31, 0x33)
        set_first = code in (0x32, 0x33)
        ops = [self.decode_multi(op) for op in chunked_with_pad(values, s.multi_len)]
        if set_first:
            idx = 0
            while idx + 1 < len(ops):
                s.set_point(ops[idx])
                self.draw_rect_from_point(ops[idx + 1], filled)
                idx += 2
            if idx < len(ops):
                s.set_point(ops[idx])
            return
        for wh in ops:
            self.draw_rect_from_point(wh, filled)

    def draw_rect_from_point(self, wh: tuple[float, float], filled: bool) -> None:
        s = self.state
        x, y = s.point
        w, h = wh
        if filled:
            if abs(w) <= 1e-12:
                w = s.pel[0] if s.pel[0] else 1 / (1 << (2 + 3 * (s.multi_len - 1)))
            if abs(h) <= 1e-12:
                h = s.pel[1] if s.pel[1] else 1 / (1 << (2 + 3 * (s.multi_len - 1)))
        y1 = y
        y2 = y + h
        top_overflow_region: tuple[float, float, float] | None = None
        if filled and h > 0 and y2 > VISIBLE_Y + 1e-9 and y - h >= -0.1:
            overshoot = y2 - VISIBLE_Y
            if h <= 0.08:
                if s.pel == (0.0, 0.0):
                    x0, x1 = sorted((x, x + w))
                    top_overflow_region = (x0, x1, overshoot * 1.45)
                y1 = y + overshoot * 0.75
                y2 = y1 - h
            else:
                y2 = y - h
        pts = [(x, y1), (x + w, y1), (x + w, y2), (x, y2)]
        if filled and s.fill_pattern == 0 and not s.outline_filled:
            pix = [s.xy(p) for p in [self.adjust_top_overflow_point(p) for p in pts]]
            xs = [p[0] for p in pix]
            ys = [p[1] for p in pix]
            s.draw.rectangle([min(xs), min(ys), max(xs), max(ys)], fill=s.current_color())
        elif filled:
            self.fill_polygon(pts)
        else:
            adjusted = [self.adjust_top_overflow_point(p) for p in pts]
            self.draw_polyline(adjusted + [adjusted[0]])
        if top_overflow_region is not None:
            s.top_overflow_regions.append(top_overflow_region)
        s.set_point((x + w, y))

    def pdi_polygon(self, code: int, values: list[int]) -> None:
        s = self.state
        filled = code in (0x35, 0x37)
        set_first = code in (0x36, 0x37)
        ops = [self.decode_multi(op) for op in chunked_with_pad(values, s.multi_len)]
        if set_first and ops:
            s.set_point(ops.pop(0))
        pts = [s.point]
        cur = s.point
        for d in ops:
            cur = (cur[0] + d[0], cur[1] + d[1])
            pts.append(cur)
        if len(pts) > 1:
            if filled:
                self.fill_polygon(pts)
            else:
                self.draw_polyline(pts + [pts[0]])

    def pdi_field(self, values: list[int]) -> None:
        s = self.state
        ops = [self.decode_multi(op) for op in chunked_with_pad(values, s.multi_len)]
        if not ops:
            s.field_origin = (0.0, 0.0)
            s.field_size = (1.0, 1.0)
        elif len(ops) == 1:
            s.field_origin = s.point
            s.field_size = ops[0]
        else:
            s.field_origin = ops[0]
            s.field_size = ops[1]
            s.set_point(ops[0])

    def pdi_incremental_point(self, values: list[int]) -> None:
        if not values:
            return
        packing = values[0]
        if packing == 0 or packing > 48:
            return
        bits = []
        for v in values[1:]:
            for bit in range(5, -1, -1):
                bits.append((v >> bit) & 1)
        s = self.state
        x, y = s.point
        origin = s.field_origin
        fw, fh = s.field_size
        px = s.pel[0] if s.pel[0] else 1 / (1 << (2 + 3 * (s.multi_len - 1)))
        py = s.pel[1] if s.pel[1] else px
        minx, maxx = sorted([origin[0], origin[0] + fw])
        miny, maxy = sorted([origin[1], origin[1] + fh])
        idx = 0
        while idx + packing <= len(bits):
            val = 0
            for bit in bits[idx : idx + packing]:
                val = (val << 1) | bit
            idx += packing
            if s.color_mode == 0:
                color = self.bits_to_direct_color(bits[idx - packing : idx])
                s.fg = color
            else:
                palidx = self.palette_index_from_value(val, packing)
                s.fg_index = palidx
                s.fg = s.palette[palidx]
                color = s.fg
            self.draw_pel((x, y), color=color)
            x += px
            if (px >= 0 and x + px > maxx + 1e-9) or (px < 0 and x + px < minx - 1e-9):
                rem = idx % 6
                if rem:
                    idx += 6 - rem
                x = minx if px >= 0 else maxx
                y += py
                if (py >= 0 and y + py > maxy + 1e-9) or (py < 0 and y + py < miny - 1e-9):
                    break
        s.set_point(origin)

    def pdi_incremental_line(self, code: int, values: list[int]) -> None:
        if len(values) < 1:
            return
        s = self.state
        step = self.decode_multi((values + [0] * s.multi_len)[: s.multi_len])
        bits = []
        for v in values[s.multi_len :]:
            for bit in range(5, -1, -1):
                bits.append((v >> bit) & 1)
        draw_flag = True
        pts = [s.point]
        i = 0
        dx, dy = step
        while i + 1 < len(bits):
            op = (bits[i] << 1) | bits[i + 1]
            i += 2
            old = s.point
            if op == 0 and i + 1 < len(bits):
                sub = (bits[i] << 1) | bits[i + 1]
                i += 2
                if sub == 0 and code == 0x3A:
                    draw_flag = not draw_flag
                elif sub == 1:
                    dx = -dx
                elif sub == 2:
                    dy = -dy
                else:
                    dx, dy = -dx, -dy
                continue
            if op == 1:
                s.set_point((s.point[0] + dx, s.point[1]))
            elif op == 2:
                s.set_point((s.point[0], s.point[1] + dy))
            elif op == 3:
                s.set_point((s.point[0] + dx, s.point[1] + dy))
            if code == 0x3A and draw_flag:
                self.draw_line(old, s.point)
            pts.append(s.point)
        if code == 0x3B and len(pts) > 2:
            self.fill_polygon(pts)

    def pdi_set_color(self, values: list[int]) -> None:
        s = self.state
        if not values:
            s.fg = (0, 0, 0)
            return
        for idx, op in enumerate(chunked_with_pad(values, s.multi_len)):
            color = self.decode_color(op)
            if s.color_mode == 0:
                s.fg = color
                s.fg_index = self.find_or_set_palette(color)
            else:
                palidx = s.fg_index if idx == 0 else self.increment_palette_index(s.fg_index, idx)
                s.palette[palidx] = color
                s.palette_used.add(palidx)
                if palidx == s.fg_index:
                    s.fg = color

    def pdi_select_color(self, values: list[int]) -> None:
        s = self.state
        if not values:
            s.color_mode = 0
            return
        operands = [self.decode_single(op) for op in chunked_with_pad(values, s.single_len)]
        bits = 6 * s.single_len
        if len(operands) == 1:
            s.color_mode = 1
            idx = self.palette_index_from_value(operands[0], bits)
            s.fg_index = idx
            s.fg = s.palette[idx]
            s.palette_used.add(idx)
        else:
            s.color_mode = 2
            fg = self.palette_index_from_value(operands[0], bits)
            bg = self.palette_index_from_value(operands[1], bits)
            if fg != bg:
                s.fg_index = fg
                s.fg = s.palette[fg]
                s.palette_used.add(fg)
            s.bg_index = bg
            s.bg = s.palette[bg]
            s.palette_used.add(bg)

    def decode_single(self, values: list[int]) -> int:
        value = 0
        for v in values:
            value = (value << 6) | (v & 0x3F)
        return value

    def decode_multi(self, values: list[int]) -> tuple[float, float]:
        s = self.state
        vals = (values + [0] * s.multi_len)[: s.multi_len]
        if s.dimensions == 3:
            v = vals[0]
            signs = [(v >> 5) & 1, (v >> 3) & 1, (v >> 1) & 1]
            mags = [(v >> 4) & 1, (v >> 2) & 1, v & 1]
            bits = 1
            for v in vals[1:]:
                mags[0] = (mags[0] << 2) | ((v >> 4) & 0x03)
                mags[1] = (mags[1] << 2) | ((v >> 2) & 0x03)
                mags[2] = (mags[2] << 2) | (v & 0x03)
                bits += 2
            denom = 1 << bits
            x = (mags[0] - denom) / denom if signs[0] else mags[0] / denom
            y = (mags[1] - denom) / denom if signs[1] else mags[1] / denom
            return x, y
        v = vals[0]
        xsign = (v >> 5) & 1
        xmag = (v >> 3) & 0x03
        ysign = (v >> 2) & 1
        ymag = v & 0x03
        bits = 2
        for v in vals[1:]:
            xmag = (xmag << 3) | ((v >> 3) & 0x07)
            ymag = (ymag << 3) | (v & 0x07)
            bits += 3
        denom = 1 << bits
        x = (xmag - denom) / denom if xsign else xmag / denom
        y = (ymag - denom) / denom if ysign else ymag / denom
        return x, y

    def decode_color(self, values: list[int]) -> tuple[int, int, int]:
        streams = [0, 0, 0]
        counts = [0, 0, 0]
        for v in values:
            order = [(0, 5), (1, 4), (2, 3), (0, 2), (1, 1), (2, 0)]
            for chan, bit in order:
                streams[chan] = (streams[chan] << 1) | ((v >> bit) & 1)
                counts[chan] += 1
        g = scale_bits(streams[0], counts[0])
        r = scale_bits(streams[1], counts[1])
        b = scale_bits(streams[2], counts[2])
        return r, g, b

    def bits_to_direct_color(self, bits: list[int]) -> tuple[int, int, int]:
        streams = [0, 0, 0]
        counts = [0, 0, 0]
        for i, bit in enumerate(bits):
            chan = i % 3
            streams[chan] = (streams[chan] << 1) | bit
            counts[chan] += 1
        g = scale_bits(streams[0], counts[0])
        r = scale_bits(streams[1], counts[1])
        b = scale_bits(streams[2], counts[2])
        return r, g, b

    def palette_index_from_value(self, value: int, bits: int) -> int:
        if bits <= 4:
            return (value << (4 - bits)) & 0x0F
        return (value >> (bits - 4)) & 0x0F

    def find_or_set_palette(self, color: tuple[int, int, int]) -> int:
        s = self.state
        for i, c in enumerate(s.palette):
            if c == color:
                return i
        for i in range(1, 16):
            if i == 7:
                continue
            if i not in s.palette_used:
                s.palette[i] = color
                s.palette_used.add(i)
                return i
        return 7

    def increment_palette_index(self, value: int, amount: int) -> int:
        x = value
        for _ in range(amount):
            for bit in range(3, -1, -1):
                if not (x & (1 << bit)):
                    x |= 1 << bit
                    mask = sum(1 << j for j in range(bit + 1, 4))
                    x &= ~mask
                    break
        return x & 0x0F

    def draw_pel(self, p: tuple[float, float], color: tuple[int, int, int] | None = None) -> None:
        s = self.state
        p = self.adjust_top_overflow_point(p)
        x, y = s.xy(p)
        w = s.dist_x(s.pel[0]) if s.pel[0] else 1
        h = s.dist_y(s.pel[1]) if s.pel[1] else 1
        self.state.draw.rectangle([x, y - h, x + w, y], fill=color or s.current_color())

    def draw_line(self, a: tuple[float, float], b: tuple[float, float]) -> None:
        s = self.state
        if s.line_texture == 0:
            if self.draw_axis_aligned_line(a, b):
                return
            self.state.draw.line([s.xy(a), s.xy(b)], fill=s.current_color(), width=s.line_width(), joint="curve")
        else:
            self.draw_textured_line(a, b)

    def draw_polyline(self, pts: list[tuple[float, float]]) -> None:
        if len(pts) < 2:
            return
        if self.state.line_texture:
            for a, b in zip(pts, pts[1:]):
                self.draw_textured_line(a, b)
            return
        for a, b in zip(pts, pts[1:]):
            if not self.draw_axis_aligned_line(a, b):
                self.state.draw.line([self.state.xy(a), self.state.xy(b)], fill=self.state.current_color(), width=self.state.line_width(), joint="curve")

    def draw_axis_aligned_line(self, a: tuple[float, float], b: tuple[float, float]) -> bool:
        s = self.state
        ax, ay = s.xy(a)
        bx, by = s.xy(b)
        if abs(a[1] - b[1]) <= 1e-12:
            h = s.dist_y(s.pel[1]) if s.pel[1] else s.line_width()
            x0, x1 = sorted((ax, bx))
            s.draw.rectangle([x0, ay - h, x1, ay], fill=s.current_color())
            return True
        if abs(a[0] - b[0]) <= 1e-12:
            w = s.dist_x(s.pel[0]) if s.pel[0] else s.line_width()
            y0, y1 = sorted((ay, by))
            s.draw.rectangle([ax, y0, ax + w, y1], fill=s.current_color())
            return True
        return False

    def fill_polygon(self, pts: list[tuple[float, float]]) -> None:
        if len(pts) < 3:
            return
        self.register_top_overflow_polygon(pts)
        pts = [self.adjust_top_overflow_point(p) for p in pts]
        pix = [self.state.xy(p) for p in pts]
        if self.state.fill_pattern <= 3:
            self.state.draw.polygon(pix, fill=self.state.current_color())
        else:
            shape = Image.new("L", self.state.image.size, 0)
            ImageDraw.Draw(shape).polygon(pix, fill=255)
            if self.state.color_mode == 2:
                background = Image.new("RGB", self.state.image.size, self.state.bg)
                self.state.image.paste(background, (0, 0), shape)
            pattern = self.fill_pattern_mask(self.state.image.size)
            mask = ImageChops.multiply(shape, pattern)
            fill = Image.new("RGB", self.state.image.size, self.state.current_color())
            self.state.image.paste(fill, (0, 0), mask)
        if self.state.outline_filled:
            outline = self.state.bg if self.state.color_mode == 2 else (0, 0, 0)
            self.state.draw.line(pix + [pix[0]], fill=outline, width=self.state.line_width(), joint="curve")
        else:
            self.seal_filled_polygon_axis_edges(pts)

    def adjust_top_overflow_point(self, p: tuple[float, float]) -> tuple[float, float]:
        x, y = p
        if y < VISIBLE_Y - 0.08:
            return p
        for minx, maxx, shift in reversed(self.state.top_overflow_regions):
            if minx - 1e-9 <= x <= maxx + 1e-9:
                return x, y - shift
        return p

    def register_top_overflow_polygon(self, pts: list[tuple[float, float]]) -> None:
        ys = [p[1] for p in pts]
        min_y, max_y = min(ys), max(ys)
        if min_y < VISIBLE_Y - 1e-9 or max_y <= VISIBLE_Y + 1e-9:
            return
        if max_y - min_y > 0.08:
            return
        xs = [p[0] for p in pts]
        self.state.top_overflow_regions.append((min(xs), max(xs), (max_y - VISIBLE_Y) * 1.2))

    def seal_filled_polygon_axis_edges(self, pts: list[tuple[float, float]]) -> None:
        s = self.state
        if s.fill_pattern != 0 or not (s.pel[0] and s.pel[1]):
            return
        pel_w = s.dist_x(s.pel[0])
        pel_h = s.dist_y(s.pel[1])
        if pel_w >= AA or pel_h >= AA:
            return
        for a, b in zip(pts, pts[1:] + pts[:1]):
            ax, ay = s.xy(a)
            bx, by = s.xy(b)
            if abs(a[1] - b[1]) <= 1e-12:
                h = max(pel_h, AA)
                x0, x1 = sorted((ax, bx))
                s.draw.rectangle([x0, ay - h, x1, ay + h], fill=s.current_color())
            elif abs(a[0] - b[0]) <= 1e-12:
                w = max(pel_w, AA)
                y0, y1 = sorted((ay, by))
                s.draw.rectangle([ax - w, y0, ax + w, y1], fill=s.current_color())

    def draw_textured_line(self, a: tuple[float, float], b: tuple[float, float]) -> None:
        s = self.state
        ax, ay = s.xy(a)
        bx, by = s.xy(b)
        dx, dy = bx - ax, by - ay
        length = math.hypot(dx, dy)
        if length <= 0:
            self.draw_pel(a)
            return
        lw = s.line_width()
        unit = max(2, lw * 2)
        if s.line_texture == 1:
            pattern = [(lw, unit)]
        elif s.line_texture == 2:
            pattern = [(unit * 3, unit)]
        else:
            pattern = [(unit * 3, unit), (lw, unit)]
        pos = 0.0
        pi = 0
        while pos < length:
            draw_len, gap_len = pattern[pi % len(pattern)]
            end = min(length, pos + draw_len)
            if end > pos:
                p0 = (ax + dx * pos / length, ay + dy * pos / length)
                p1 = (ax + dx * end / length, ay + dy * end / length)
                s.draw.line([p0, p1], fill=s.current_color(), width=lw)
            pos = end + gap_len
            pi += 1

    def fill_pattern_mask(self, size: tuple[int, int]) -> Image.Image:
        s = self.state
        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        lw = max(1, s.line_width())
        gap = max(1, lw)
        step = max(2, lw + gap)
        if s.fill_pattern in (1, 3):
            for x in range(0, size[0] + step, step):
                draw.line([(x, 0), (x, size[1])], fill=255, width=lw)
        if s.fill_pattern in (2, 3):
            for y in range(0, size[1] + step, step):
                draw.line([(0, y), (size[0], y)], fill=255, width=lw)
        if 4 <= s.fill_pattern <= 7:
            key = chr(0x41 + s.fill_pattern - 4)
            tile_w = max(1, min(size[0], s.dist_x(s.texture_mask_size[0]) if s.texture_mask_size[0] else 16 * AA))
            tile_h = max(1, min(size[1], s.dist_y(s.texture_mask_size[1]) if s.texture_mask_size[1] else 16 * AA))
            tile = self.programmable_texture_tile(key, tile_w, tile_h)
            if tile is not None:
                for y in range(0, size[1], tile_h):
                    for x in range(0, size[0], tile_w):
                        mask.paste(tile, (x, y))
        return mask

    def programmable_texture_tile(self, key: str, width: int, height: int) -> Image.Image | None:
        body = self.state.programmable_textures.get(key)
        if not body:
            return None
        cache_key = (key, width, height)
        cached = self.texture_cache.get(cache_key)
        if cached is not None:
            return cached
        child = Renderer(body)
        try:
            child.execute_bytes(body)
            child.flush_pdi()
        except Exception:
            return None
        rendered = child.state.final_image().convert("L")
        tile = rendered.resize((width, height), Image.Resampling.NEAREST)
        tile = tile.point(lambda v: 255 if v else 0)
        self.texture_cache[cache_key] = tile
        return tile

    def arc_points(self, a: tuple[float, float], b: tuple[float, float], c: tuple[float, float]) -> list[tuple[float, float]]:
        if abs(a[0] - c[0]) < 1e-9 and abs(a[1] - c[1]) < 1e-9:
            cx = (a[0] + b[0]) / 2
            cy = (a[1] + b[1]) / 2
            r = math.hypot(a[0] - b[0], a[1] - b[1]) / 2
            return [(cx + r * math.cos(t), cy + r * math.sin(t)) for t in [2 * math.pi * i / 96 for i in range(97)]]
        d = 2 * (a[0] * (b[1] - c[1]) + b[0] * (c[1] - a[1]) + c[0] * (a[1] - b[1]))
        if abs(d) < 1e-12:
            return [a, c]
        ux = ((a[0] ** 2 + a[1] ** 2) * (b[1] - c[1]) + (b[0] ** 2 + b[1] ** 2) * (c[1] - a[1]) + (c[0] ** 2 + c[1] ** 2) * (a[1] - b[1])) / d
        uy = ((a[0] ** 2 + a[1] ** 2) * (c[0] - b[0]) + (b[0] ** 2 + b[1] ** 2) * (a[0] - c[0]) + (c[0] ** 2 + c[1] ** 2) * (b[0] - a[0])) / d
        angles = [math.atan2(p[1] - uy, p[0] - ux) for p in (a, b, c)]
        start, mid, end = angles
        ccw_end = end
        while ccw_end < start:
            ccw_end += 2 * math.pi
        ccw_mid = mid
        while ccw_mid < start:
            ccw_mid += 2 * math.pi
        if not (start <= ccw_mid <= ccw_end):
            if end > start:
                end -= 2 * math.pi
            step_count = max(8, int(abs(start - end) / (2 * math.pi) * 96))
            return [(ux + math.hypot(a[0] - ux, a[1] - uy) * math.cos(start + (end - start) * i / step_count), uy + math.hypot(a[0] - ux, a[1] - uy) * math.sin(start + (end - start) * i / step_count)) for i in range(step_count + 1)]
        step_count = max(8, int(abs(ccw_end - start) / (2 * math.pi) * 96))
        r = math.hypot(a[0] - ux, a[1] - uy)
        return [(ux + r * math.cos(start + (ccw_end - start) * i / step_count), uy + r * math.sin(start + (ccw_end - start) * i / step_count)) for i in range(step_count + 1)]

    def display_graphic_byte(self, b: int, repeated: bool = False) -> None:
        self.state.text.pending_auto_crlf = False
        active = self.ss or self.state.gl
        gset = self.state.gsets.get(active, "ASCII")
        if self.ss:
            self.ss = None
        if gset == "ASCII":
            self.draw_text(chr(b & 0x7F))
            if not repeated and (b == 0x20 or 0x21 <= b <= 0x7E):
                self.state.last_spacing_byte = b
        elif gset == "SUPP":
            self.draw_text(self.supplementary_char(b & 0x7F))
            self.state.last_spacing_byte = b
        elif gset == "MOSAIC":
            self.draw_mosaic(b & 0x7F)
            self.state.last_spacing_byte = b
        elif gset == "MACRO":
            body = self.state.macros.get(b & 0x7F)
            if body:
                if self.macro_depth > 16:
                    raise NaplpsError("macro recursion limit exceeded")
                self.macro_depth += 1
                try:
                    self.execute_bytes(body)
                finally:
                    self.macro_depth -= 1
        elif gset == "DRCS":
            self.draw_drcs(b & 0x7F)
        elif gset == "DBCS":
            self.advance_cursor(1, 0)
        else:
            raise NaplpsError(f"cannot display byte {b:02X} from {gset}")

    def draw_drcs(self, code: int) -> None:
        body = self.state.drcs.get(code)
        if not body:
            self.advance_cursor(1, 0)
            return
        child = Renderer(body)
        try:
            child.execute_bytes(body)
            child.flush_pdi()
        except Exception:
            self.advance_cursor(1, 0)
            return
        glyph = child.state.final_image().convert("L")
        bbox = glyph.getbbox()
        if bbox:
            glyph = glyph.crop(bbox)
        w = self.state.dist_x(self.state.text.width)
        h = self.state.dist_y(self.state.text.height)
        glyph = glyph.resize((w, h), Image.Resampling.NEAREST).point(lambda v: 255 if v else 0)
        x0, y0 = self.state.xy((self.state.cursor[0], self.state.cursor[1] + self.state.text.height))
        fill = Image.new("RGB", glyph.size, self.state.fg)
        self.state.image.paste(fill, (x0, y0), glyph)
        self.advance_cursor(1, 0)

    def font(self, px: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        bitmap_family = os.environ.get("NAPLPS_FONT_FAMILY", "times-pcf").lower()
        pcf_families = {
            "times-pcf": "timR",
            "courier-pcf": "courR",
            "helvetica-pcf": "helvR",
            "charter-pcf": "charR",
            "new-century-pcf": "ncenR",
            "utopia-pcf": "UTRG__",
        }
        pcf_prefix = pcf_families.get(bitmap_family, "timR")
        bitmap_fonts = tuple(
            (size, f"/usr/share/fonts/redhat-classic-fonts/{pcf_prefix}{size:02d}.pcf.gz")
            for size in (8, 10, 12, 14, 18, 24)
        )
        target = max(1, round(px))
        if bitmap_family in pcf_families:
            for size, path in sorted(bitmap_fonts, key=lambda item: abs(item[0] - target)):
                if Path(path).exists():
                    try:
                        return ImageFont.truetype(path, size)
                    except OSError:
                        pass
        named_fonts = {
            "times": "/usr/share/fonts/corefonts/times.ttf",
            "times-bold": "/usr/share/fonts/corefonts/timesbd.ttf",
            "courier": "/usr/share/fonts/corefonts/cour.ttf",
            "arial": "/usr/share/fonts/corefonts/arial.ttf",
            "bodoni": "/usr/share/fonts/freefonts/bodoni.pfb",
            "dejavu-serif": "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "dejavu-sans": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "liberation-serif": "/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf",
            "liberation-sans": "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
            "nimbus-roman": "/usr/share/fonts/opentype/urw-base35/NimbusRoman-Regular.otf",
            "nimbus-sans": "/usr/share/fonts/opentype/urw-base35/NimbusSans-Regular.otf",
            "nimbus-sans-narrow": "/usr/share/fonts/opentype/urw-base35/NimbusSansNarrow-Regular.otf",
            "unifont": "/usr/share/fonts/opentype/unifont/unifont.otf",
        }
        fallback = (
            named_fonts.get(bitmap_family),
            "/usr/share/fonts/corefonts/times.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        )
        for path in fallback:
            if Path(path).exists():
                return ImageFont.truetype(path, target)
        return ImageFont.load_default()

    def ensure_text_cell_visible(self) -> None:
        s = self.state
        minx, miny, maxx, maxy = self.active_text_bounds()
        cw = abs(s.text.width)
        ch = abs(s.text.height)
        x, y = s.cursor
        if s.text.path == 0 and x + cw > maxx + 1e-9:
            s.set_cursor((minx, y - ch * s.text.inter_row))
            s.text.pending_auto_crlf = True
        elif s.text.path == 1 and x < minx - 1e-9:
            s.set_cursor((max(minx, maxx - cw), y - ch * s.text.inter_row))
            s.text.pending_auto_crlf = True
        elif s.text.path == 2 and y + ch > maxy + 1e-9:
            s.set_cursor((x + cw * s.text.inter_row, miny))
            s.text.pending_auto_crlf = True
        elif s.text.path == 3 and y < miny - 1e-9:
            s.set_cursor((x + cw * s.text.inter_row, max(miny, maxy - ch)))
            s.text.pending_auto_crlf = True

    def draw_text(self, ch: str) -> None:
        s = self.state
        self.ensure_text_cell_visible()
        base_x = round(s.cursor[0] * WIDTH)
        base_y = round((1 - s.cursor[1] / VISIBLE_Y) * HEIGHT)
        w = max(1, round(abs(s.text.width) * WIDTH))
        h = max(1, round(abs(s.text.height) / VISIBLE_Y * HEIGHT))
        fg = s.bg if s.text.reverse and s.color_mode == 2 else s.fg
        bg = s.fg if s.text.reverse and s.color_mode != 2 else s.bg
        cell = Image.new("L", (w, h), 0)
        if ch != " ":
            ink_w = w
            if s.text.proportional and s.text.path in (0, 1):
                ink_w = max(1, round(self.proportional_advance(ch) * WIDTH))
            font_scale = 1.65 if h <= 14 else 1.05
            font = self.font(max(1, int(round(h * font_scale))))
            bbox = font.getbbox(ch)
            try:
                ascent, descent = font.getmetrics()
            except AttributeError:
                ascent, descent = max(1, bbox[3]), 0
            advance = math.ceil(font.getlength(ch)) if hasattr(font, "getlength") else bbox[2] - bbox[0]
            gw = max(1, advance, bbox[2] - bbox[0])
            line_h = max(1, ascent + descent, bbox[3] - min(0, bbox[1])) + 4
            glyph = Image.new("L", (gw + 6, line_h), 0)
            gdraw = ImageDraw.Draw(glyph)
            gdraw.text((3 - min(0, bbox[0]), 1 - min(0, bbox[1])), ch, fill=255, font=font)
            drawn = glyph.getbbox()
            if drawn:
                if h <= 14 and max(fg) < 96 and not ch.isalnum():
                    glyph = glyph.crop((drawn[0], 0, drawn[2], glyph.height))
                    target_h = h
                elif h <= 14 and max(fg) < 96:
                    glyph = glyph.crop(drawn)
                    target_h = max(1, int(round(h * 0.62)))
                elif h <= 14:
                    glyph = glyph.crop(drawn)
                    target_h = max(1, int(round(h * 0.82)))
                else:
                    glyph = glyph.crop((drawn[0], 0, drawn[2], glyph.height))
                    target_h = h
                scale_y = target_h / glyph.height
                tw = max(1, int(round(min(ink_w * 0.96, glyph.width * scale_y))))
                th = max(1, int(round(glyph.height * scale_y)))
                if (tw, th) != glyph.size:
                    glyph = glyph.resize((tw, th), Image.Resampling.NEAREST)
                glyph = glyph.point(lambda v: 255 if v >= 48 else 0)
                if h <= 12 and max(fg) >= 96:
                    glyph = glyph.filter(ImageFilter.MaxFilter(3))
                gx = max(0, int((min(w, ink_w) - tw) / 2))
                if s.text.proportional and h >= 100:
                    gy = 0
                else:
                    gy = max(0, h - th - 1) if h <= 14 else max(0, int((h - th) * 0.28))
                cell.paste(glyph, (gx, gy), glyph)
        if s.text.underline:
            underline = max(1, s.line_width())
            ImageDraw.Draw(cell).rectangle([0, h - underline, w, h], fill=255)
        if s.text.width < 0:
            cell = cell.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        if s.text.height < 0:
            cell = cell.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        rotation = s.text.rotation & 0x03
        if rotation:
            cell = cell.rotate(rotation * 90, expand=True)
        top_shift = max(0, int(round(h * 0.05)))
        if rotation == 0:
            if s.text.proportional:
                if h >= 150:
                    medium_shift = max(0, int(round(h * 0.90)))
                elif h >= 100:
                    medium_shift = max(0, int(round(h * 0.86)))
                elif h >= 34 and s.cursor[1] >= 0.45 and fg[1] > 80 and fg[0] < 40 and fg[2] < 60:
                    medium_shift = max(0, int(round(h * 0.86)))
                elif 24 <= h <= 26:
                    medium_shift = max(0, int(round(h * 0.55)))
                else:
                    medium_shift = max(0, int(round(h * 0.86))) if 19 <= h <= 23 else 0
                if 24 <= h <= 26 and s.cursor[1] < 0.25 and min(fg) >= 90:
                    medium_shift = max(1, int(round(h * 0.60)))
                elif 16 <= h <= 18 and s.cursor[1] < 0.25 and 70 <= min(fg) <= 140 and max(fg) <= 160:
                    medium_shift = max(1, int(round(h * 0.45)))
                px, py = base_x, base_y - top_shift - medium_shift
            elif h <= 14 and max(fg) < 96:
                px, py = base_x, base_y - top_shift - max(1, int(round(h * 0.25)))
            else:
                px, py = base_x, base_y - cell.height + max(0, int(round(h * 0.20)))
        elif rotation == 1:
            px, py = base_x - cell.width + top_shift, base_y
        elif rotation == 2:
            px, py = base_x - cell.width, base_y - cell.height + top_shift
        else:
            px, py = base_x, base_y - cell.height
        px *= AA
        py *= AA
        if AA != 1:
            cell = cell.resize((cell.width * AA, cell.height * AA), Image.Resampling.NEAREST)
        if s.color_mode == 2 or s.text.reverse:
            bg_mask = Image.new("L", cell.size, 255)
            s.image.paste(Image.new("RGB", cell.size, bg), (px, py), bg_mask)
        if cell.getbbox():
            s.image.paste(Image.new("RGB", cell.size, fg), (px, py), cell)
        self.advance_text_char(ch)

    def draw_mosaic(self, code: int) -> None:
        s = self.state
        x0, y0 = s.xy((s.cursor[0], s.cursor[1] + s.text.height))
        w = s.dist_x(s.text.width)
        h = s.dist_y(s.text.height)
        bits = [0, 1, 2, 3, 4, 6]
        cellw = w / 2
        cellh = h / 3
        for idx, bit in enumerate(bits):
            if code & (1 << bit):
                cx = idx % 2
                cy = idx // 2
                s.draw.rectangle([x0 + cx * cellw, y0 + cy * cellh, x0 + (cx + 1) * cellw, y0 + (cy + 1) * cellh], fill=s.fg)
        self.advance_cursor(1, 0)

    def draw_cursor(self) -> None:
        s = self.state
        if not s.text.cursor_visible:
            return
        x0, y0 = s.xy(s.cursor)
        w = max(1, s.dist_x(s.text.width))
        h = max(1, s.dist_y(s.text.height))
        mask = Image.new("L", (w, h), 0)
        draw = ImageDraw.Draw(mask)
        lw = max(1, s.line_width())
        if s.text.cursor_style == 1:
            draw.rectangle([0, 0, w, h], fill=255)
        elif s.text.cursor_style == 2:
            draw.line([(w // 2, 0), (w // 2, h)], fill=255, width=lw)
            draw.line([(0, h // 2), (w, h // 2)], fill=255, width=lw)
        else:
            draw.rectangle([0, max(0, h - lw), w, h], fill=255)
        if s.text.rotation:
            mask = mask.rotate((s.text.rotation & 0x03) * 90, expand=True)
        s.image.paste(Image.new("RGB", mask.size, s.fg), (x0, y0), mask)

    def ascii_width_class(self, ch: str) -> int:
        code = ord(ch)
        if code == 0x20:
            return 9
        if 0x20 <= code <= 0x7F:
            return ASCII_WIDTH_CLASSES[code & 0x0F][(code >> 4) - 2]
        return 9

    def proportional_advance(self, ch: str) -> float:
        width = abs(self.state.text.width)
        cls = self.ascii_width_class(ch)
        n = int(width * 256)
        if n < 6:
            return width * PROP_SPACING_SMALL[6][cls] / 6
        if n < 12:
            return PROP_SPACING_SMALL[n][cls] / 256
        n = min(255, n)
        f = (((n * 11) // 13 - 1) | 1) - 1
        adjust = (PROP_SPACING_ADJUST[cls] * f + 3) // 6
        return max(1, n - adjust) / 256

    def advance_text_char(self, ch: str) -> None:
        s = self.state
        if s.text.proportional and s.text.path in (0, 1):
            self.advance_cursor_distance(self.proportional_advance(ch), 0.0, wrap_extent=0.0)
        else:
            self.advance_cursor(1, 0)
        if s.text.cursor_relation in (0, 1):
            s.point = self.text_cursor_drawing_point()

    def text_cursor_drawing_point(self) -> tuple[float, float]:
        s = self.state
        x, y = s.cursor
        offset = abs(s.text.height) * 0.75
        if s.text.rotation == 0:
            return x, y - offset
        if s.text.rotation == 1:
            return x + offset, y
        if s.text.rotation == 2:
            return x, y + offset
        return x - offset, y

    def active_text_bounds(self) -> tuple[float, float, float, float]:
        x0, y0, x1, y1 = self.field_rect((self.state.field_origin, self.state.field_size))
        minx, miny, maxx, maxy = max(0.0, x0), max(0.0, y0), min(1.0, x1), min(VISIBLE_Y, y1)
        x, y = self.state.cursor
        cw = abs(self.state.text.width)
        ch = abs(self.state.text.height)
        if cw > maxx - minx + 1e-9 or ch > maxy - miny + 1e-9:
            return 0.0, 0.0, 1.0, VISIBLE_Y
        if x + cw < minx or x > maxx or y + ch < miny or y - ch > maxy:
            return 0.0, 0.0, 1.0, VISIBLE_Y
        return minx, miny, maxx, maxy

    def carriage_return(self) -> None:
        s = self.state
        minx, miny, maxx, maxy = self.active_text_bounds()
        cw = abs(s.text.width)
        ch = abs(s.text.height)
        x, y = s.cursor
        if s.text.path == 0:
            x = minx
        elif s.text.path == 1:
            x = max(minx, maxx - cw)
        elif s.text.path == 2:
            y = miny
        else:
            y = max(miny, maxy - ch)
        s.set_cursor((x, y))

    def advance_cursor_distance(self, parallel: float, perpendicular: float, wrap_extent: float | None = None) -> None:
        s = self.state
        if s.text.path == 0:
            s.cursor = (s.cursor[0] + parallel, s.cursor[1] - perpendicular)
        elif s.text.path == 1:
            s.cursor = (s.cursor[0] - parallel, s.cursor[1] - perpendicular)
        elif s.text.path == 2:
            s.cursor = (s.cursor[0], s.cursor[1] + parallel - perpendicular)
        else:
            s.cursor = (s.cursor[0], s.cursor[1] - parallel - perpendicular)
        extent = s.text.width if wrap_extent is None else wrap_extent
        minx, miny, maxx, maxy = self.active_text_bounds()
        cw = abs(s.text.width)
        ch = abs(s.text.height)
        x, y = s.cursor
        if s.text.path == 0 and x + max(cw, extent) > maxx + 1e-9:
            x, y = minx, y - ch * s.text.inter_row
            s.text.pending_auto_crlf = True
        elif s.text.path == 1 and x < minx - 1e-9:
            x, y = max(minx, maxx - cw), y - ch * s.text.inter_row
            s.text.pending_auto_crlf = True
        if s.text.path in (0, 1):
            if y < miny - ch:
                y = max(miny, maxy - ch)
            if y > maxy:
                y = miny
            if x < minx - cw:
                x = max(minx, maxx - cw)
            if x > maxx:
                x = minx
        s.set_cursor((x, y))

    def advance_cursor(self, chars: float, rows: float) -> None:
        s = self.state
        parallel = chars * s.text.width * s.text.inter_char
        perpendicular = rows * s.text.height * s.text.inter_row
        self.advance_cursor_distance(parallel, perpendicular)

    def linefeed(self, direction: int) -> None:
        s = self.state
        minx, miny, maxx, maxy = self.active_text_bounds()
        cw = abs(s.text.width)
        ch = abs(s.text.height)
        x, y = s.cursor
        amount = s.text.inter_row * (ch if s.text.path in (0, 1) else cw)
        if s.text.path in (0, 1):
            y -= direction * amount
            if direction > 0 and y < miny:
                y = max(miny, maxy - ch)
            elif direction < 0 and y + ch > maxy:
                y = miny
        else:
            x += direction * amount
            if direction > 0 and x + cw > maxx:
                x = minx
            elif direction < 0 and x < minx:
                x = max(minx, maxx - cw)
        s.set_cursor((x, y))

    def supplementary_char(self, code: int) -> str:
        table = {
            0x21: "¡", 0x22: "¢", 0x23: "£", 0x24: "$", 0x25: "¥", 0x26: "#",
            0x30: "°", 0x31: "±", 0x32: "²", 0x34: "×", 0x38: "÷", 0x3F: "¿",
            0x50: "—", 0x52: "®", 0x53: "©", 0x54: "™", 0x60: "Ω", 0x7B: "ß",
        }
        return table.get(code, " ")


def convert(input_file: Path, output_file: Path) -> Path:
    if output_file.exists() and output_file.is_dir():
        raise NaplpsError(f"output path is a directory: {output_file}")
    data = input_file.read_bytes()
    renderer = Renderer(data)
    image = renderer.parse()
    output_file.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(output_file.parent, 0o775)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{output_file.name}.", suffix=".tmp", dir=output_file.parent)
    os.close(fd)
    tmp = Path(tmp_name)
    try:
        image.save(tmp, "PNG")
        os.chmod(tmp, 0o664)
        tmp.replace(output_file)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise
    os.chmod(output_file, 0o664)
    return output_file


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: naplps.py <inputFile> <outputFile.png>", file=sys.stderr)
        return 2
    try:
        out = convert(Path(argv[1]), Path(argv[2]))
    except Exception as exc:
        print(f"naplps.py: {exc}", file=sys.stderr)
        return 1
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

#!/usr/bin/env python3
# Vibe coded by Codex
"""
Convert Amiga TurboCalc .TCD spreadsheets to a simple RTF table.

The parser is deliberately strict: it consumes and validates the complete input
stream before writing the output file.
"""

from __future__ import annotations

import html
import math
import os
import struct
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class TCDParseError(ValueError):
    pass


RECORD_NAMES = {
    0x00: "FILE_END",
    0x01: "FILE_START",
    0x02: "FILE_VERSION",
    0x03: "FILE_PASSWORD",
    0x04: "FILE_OPT0",
    0x05: "FILE_OPT1",
    0x06: "FILE_WIDTH",
    0x07: "FILE_HEIGHT",
    0x08: "FILE_CELL",
    0x09: "FILE_LCELL",
    0x0A: "FILE_NAME",
    0x0B: "FILE_OPT2",
    0x0C: "FILE_WINDOW",
    0x0D: "FILE_FONTS",
    0x0E: "FILE_SCREEN",
    0x0F: "FILE_COLOR",
    0x10: "FILE_DIAGRAM",
    0x11: "FILE_STDFONTS",
    0x12: "FILE_PATTERNS",
    0x13: "FILE_COLUMNFLAGS",
    0x14: "FILE_ROWFLAGS",
    0x15: "FILE_SHEETSIZE",
    0x16: "FILE_SYSTEMFONTS",
    0x17: "FILE_FROZEN",
    0x18: "FILE_SAVEOPT",
    0x19: "FILE_CRYPT",
    0x1A: "FILE_DIAGRAM2",
    0x1B: "FILE_GLOBALFLAGS",
    0x1C: "FILE_OBJECT",
    0x1D: "FILE_STDCHART",
    0x1E: "FILE_OPT3",
    0x1F: "FILE_LASTFILES",
    0x20: "FILE_CURSOR",
    0x21: "FILE_STARTUPOPTIONS",
    0x22: "FILE_TURBOCALCOWNER",
    0x23: "FILE_FILEINFO",
    0x24: "FILE_UNKNOWN_24",
    0x25: "FILE_UNKNOWN_25",
    0x26: "FILE_UNKNOWN_26",
    0x27: "FILE_UNKNOWN_27",
    0x28: "FILE_UNKNOWN_28",
    0x29: "FILE_UNKNOWN_29",
    0x2A: "FILE_UNKNOWN_2A",
    0x2B: "FILE_UNKNOWN_2B",
    0x2C: "FILE_UNKNOWN_2C",
    0x2D: "FILE_UNKNOWN_2D",
    0x2E: "FILE_UNKNOWN_2E",
    0x2F: "FILE_UNKNOWN_2F",
    0x30: "FILE_UNKNOWN_30",
    0x31: "FILE_UNKNOWN_31",
    0x32: "FILE_UNKNOWN_32",
    0x33: "FILE_UNKNOWN_33",
    0x34: "FILE_UNKNOWN_34",
}

VALID_RECORD_IDS = set(RECORD_NAMES)

CELL_TYPE_NAMES = {
    0: "empty",
    1: "no-value",
    2: "float",
    3: "integer",
    4: "date",
    5: "time",
    6: "boolean",
    7: "text",
    8: "unknown",
    9: "error",
}

FUNCTION_TOKENS = {
    0x01: "EXP",
    0x02: "LN",
    0x03: "LOG10",
    0x04: "LOG",
    0x05: "LN",
    0x06: "SQRT",
    0x07: "SUMSQ",
    0x08: "FACT",
    0x09: "PI()",
    0x0A: "SINH",
    0x0B: "COSH",
    0x0C: "TANH",
    0x0D: "SIN",
    0x0E: "COS",
    0x0F: "TAN",
    0x10: "ASIN",
    0x11: "ACOS",
    0x12: "ATAN",
    0x13: "DEGREES",
    0x14: "RADIANS",
    0x15: "IF",
    0x17: "MOD",
    0x18: "INT",
    0x1A: "ABS",
    0x1B: "SIGN",
    0x1C: "ROUND",
    0x1D: "NOT",
    0x1E: "RAND()",
    0x1F: "TRUE",
    0x20: "FALSE",
    0x21: "TEXT",
    0x22: "LEFT",
    0x23: "RIGHT",
    0x24: "MID",
    0x25: "AVERAGE",
    0x26: "CHAR",
    0x27: "LEN",
    0x28: "LOWER",
    0x29: "PROPER",
    0x2A: "UPPER",
    0x2B: "CODE",
    0x2C: "REPT",
    0x2D: "TRIM",
    0x2E: "CLEAN",
    0x2F: "VALUE",
    0x49: "COUNTA",
    0x4A: "COUNT",
    0x4B: "MIN",
    0x4C: "MAX",
    0x4E: "SUM",
    0x4F: "PRODUCT",
    0x50: "MID",
    0x51: "AND",
    0x52: "OR",
    0x53: "XOR",
    0x55: "ISNUMBER",
    0x56: "ISTEXT",
    0x57: "ISDATE",
    0x58: "ISTIME",
    0x59: "ISBLANK",
    0x72: "INSTRING",
    0x73: "SPIEGELN",
    0x74: "SHIFTL",
    0x75: "SHIFTR",
    0x76: "KOMPRIMIEREN",
    0x79: "HEX",
    0x7B: "STDEV",
    0x7D: "VAR",
}


def be_u16(data: bytes, off: int) -> int:
    if off + 2 > len(data):
        raise TCDParseError("short uint16")
    return int.from_bytes(data[off : off + 2], "big")


def be_i16(data: bytes, off: int) -> int:
    value = be_u16(data, off)
    return value - 0x10000 if value & 0x8000 else value


def be_i32(data: bytes, off: int) -> int:
    if off + 4 > len(data):
        raise TCDParseError("short int32")
    return int.from_bytes(data[off : off + 4], "big", signed=True)


def read_text(data: bytes, off: int) -> Tuple[str, int, bytes]:
    n = be_u16(data, off)
    start = off + 2
    end = start + n
    if end > len(data):
        raise TCDParseError("text field runs past record")
    raw = data[start:end]
    return raw.decode("latin-1"), end, raw


def decode_formula(raw: bytes, base_col: int, base_row: int) -> str:
    out: List[str] = []
    i = 0
    while i < len(raw):
        b = raw[i]
        if 0x08 <= b <= 0x0B:
            if i + 5 > len(raw):
                out.append(f"<{b:02X}>")
                i += 1
                continue
            col_abs = (b & 1) == 0
            row_abs = (b & 2) == 0
            col = be_i16(raw, i + 1)
            row = be_i16(raw, i + 3)
            if not col_abs:
                col += base_col
            if not row_abs:
                row += base_row
            out.append(a1(col, row))
            i += 5
        elif b in (0x04, 0x05):
            if i + 2 > len(raw):
                out.append(f"<{b:02X}>")
                i += 1
                continue
            out.append(FUNCTION_TOKENS.get(raw[i + 1], f"FUNC_{raw[i + 1]:02X}"))
            i += 2
        else:
            ch = chr(b)
            out.append("," if ch == ";" else ch)
            i += 1
    return "".join(out)


@dataclass
class CellFormat:
    raw: bytes

    @property
    def bg_pen(self) -> int:
        return self.raw[0] & 0x3F if len(self.raw) >= 1 else 0

    @property
    def text_pen(self) -> int:
        return self.raw[1] & 0x3F if len(self.raw) >= 2 else 0

    @property
    def border(self) -> int:
        return self.raw[2] if len(self.raw) >= 3 else 0

    @property
    def font(self) -> int:
        return self.raw[3] if len(self.raw) >= 4 else 0

    @property
    def text_format(self) -> int:
        return self.raw[4] if len(self.raw) >= 5 else 0

    @property
    def flags(self) -> int:
        return self.raw[5] if len(self.raw) >= 6 else 0

    @property
    def align(self) -> int:
        return self.flags & 0x07

    @property
    def bold(self) -> bool:
        return bool(self.font & 0x02)

    @property
    def italic(self) -> bool:
        return bool(self.font & 0x04)

    @property
    def underline(self) -> bool:
        return bool(self.font & 0x01)


@dataclass
class Cell:
    col: int
    row: int
    type_id: int
    value_raw: bytes
    formula_raw: bytes
    fmt: CellFormat
    text: str = ""
    formula: str = ""

    def display(self) -> str:
        if self.type_id == 7:
            return self.text
        if self.type_id == 1:
            return self.formula if self.formula else ""
        if self.type_id == 2:
            if len(self.value_raw) != 12:
                return ""
            val = struct.unpack(">d", self.value_raw[4:12])[0]
            if math.isfinite(val) and val == int(val):
                return str(int(val))
            return f"{val:.12g}"
        if self.type_id in (3, 4, 5):
            if len(self.value_raw) < 4:
                return ""
            return str(int.from_bytes(self.value_raw[:4], "big", signed=True))
        if self.type_id == 6:
            return "TRUE" if int.from_bytes(self.value_raw[:4], "big", signed=True) else "FALSE"
        if self.type_id == 9:
            return "#ERROR"
        if self.formula:
            return self.formula
        return ""


@dataclass
class Record:
    offset: int
    record_id: int
    declared_size: int
    actual_size: int
    payload: bytes
    note: str = ""


@dataclass
class Document:
    records: List[Record] = field(default_factory=list)
    cells: Dict[Tuple[int, int], Cell] = field(default_factory=dict)
    colors: List[Tuple[int, int, int]] = field(default_factory=list)
    widths: Dict[int, int] = field(default_factory=dict)
    heights: Dict[int, int] = field(default_factory=dict)
    sheet_limit: Tuple[int, int] = (0, 0)
    tail: bytes = b""


class Parser:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.doc = Document()

    def parse(self) -> Document:
        off = 0
        saw_start = False
        while off < len(self.data):
            if off + 3 > len(self.data):
                self.doc.tail = self.data[off:]
                break
            rid = self.data[off]
            declared = be_u16(self.data, off + 1)
            payload_start = off + 3
            payload_end = payload_start + declared
            if rid not in VALID_RECORD_IDS:
                self.doc.tail = self.data[off:]
                break
            if payload_end > len(self.data):
                self.doc.tail = self.data[off:]
                break

            actual = declared
            note = ""
            payload = self.data[payload_start:payload_end]
            if rid == 0x01:
                self._parse_start(payload)
                saw_start = True
            elif not saw_start:
                raise TCDParseError("first record is not FILE_START")
            elif rid in (0x08, 0x09):
                actual, cell, note = self._parse_cell_at(payload_start, declared, rid == 0x09)
                payload = self.data[payload_start : payload_start + actual]
                self.doc.cells[(cell.row, cell.col)] = cell
            elif rid == 0x0A:
                actual, note = self._parse_name_at(payload_start, declared)
                payload = self.data[payload_start : payload_start + actual]
            elif rid == 0x0F:
                self._parse_colors(payload)
            elif rid == 0x06:
                if len(payload) != 6:
                    raise TCDParseError("FILE_WIDTH length is not 6")
                self.doc.widths[be_i32(payload, 0)] = be_u16(payload, 4)
            elif rid == 0x07:
                if len(payload) != 6:
                    raise TCDParseError("FILE_HEIGHT length is not 6")
                self.doc.heights[be_i32(payload, 0)] = be_u16(payload, 4)
            elif rid == 0x15:
                if len(payload) != 12:
                    raise TCDParseError("FILE_SHEETSIZE length is not 12")
                self.doc.sheet_limit = (be_i32(payload, 0), be_i32(payload, 4))

            self.doc.records.append(Record(off, rid, declared, actual, payload, note))
            off = payload_start + actual
            if rid == 0x00 and declared == 0:
                self.doc.tail = self.data[off:]
                break

        if not saw_start:
            raise TCDParseError("missing FILE_START")
        if not self.doc.records:
            raise TCDParseError("empty record stream")
        if self.doc.tail:
            self._validate_tail(self.doc.tail)
        return self.doc

    def _parse_start(self, payload: bytes) -> None:
        if len(payload) != 12:
            raise TCDParseError("FILE_START length is not 12")
        if payload[:9] != b"TURBOCALC":
            raise TCDParseError("missing TURBOCALC signature")

    def _parse_colors(self, payload: bytes) -> None:
        if len(payload) < 2:
            raise TCDParseError("truncated FILE_COLOR")
        count = be_u16(payload, 0)
        if len(payload) == 2 + count * 4:
            colors = []
            p = 2
            for _ in range(count):
                r, g, b, _pad = payload[p : p + 4]
                p += 4
                colors.append((r, g, b))
            self.doc.colors = colors
            return
        if len(payload) != 2 + count * 2:
            raise TCDParseError("FILE_COLOR length does not match count")
        colors = []
        p = 2
        for _ in range(count):
            word = be_u16(payload, p)
            p += 2
            r = (word & 0x000F) * 17
            g = ((word >> 4) & 0x000F) * 17
            b = ((word >> 8) & 0x000F) * 17
            colors.append((r, g, b))
        self.doc.colors = colors

    def _parse_name_at(self, payload_start: int, declared: int) -> Tuple[int, str]:
        _, after_name, _ = read_text(self.data, payload_start)
        candidates = [(after_name - payload_start + declared, "name")]
        candidates.append((after_name - payload_start + declared + 1, "name+overlap"))
        for actual, note in candidates:
            nxt = payload_start + actual
            if self._valid_next_header(nxt):
                return actual, note
        actual = candidates[0][0]
        if payload_start + actual > len(self.data):
            raise TCDParseError("FILE_NAME overruns input")
        return actual, "name-final"

    def _parse_cell_at(self, payload_start: int, declared: int, long_coords: bool) -> Tuple[int, Cell, str]:
        p = payload_start
        if long_coords:
            col = be_i32(self.data, p)
            row = be_i32(self.data, p + 4)
            p += 8
        else:
            col = be_u16(self.data, p)
            row = be_u16(self.data, p + 2)
            p += 4
        if p >= len(self.data):
            raise TCDParseError("truncated cell type")
        type_id = self.data[p]
        p += 1
        if type_id not in CELL_TYPE_NAMES:
            raise TCDParseError(f"unsupported cell type {type_id}")

        value_raw = b""
        text = ""
        if type_id == 0:
            pass
        elif type_id == 2:
            value_raw = self._slice(p, 12)
            p += 12
        elif type_id in (1, 3, 4, 5, 6, 8, 9):
            value_raw = self._slice(p, 8)
            p += 8
        elif type_id == 7:
            text, p, value_raw = read_text(self.data, p)

        base = p - payload_start
        remaining = declared - base
        formula_raw = b""
        formula = ""
        note = "cell-no-formula"
        if remaining == 8:
            fmt_raw = self._slice(p, 8)
            p += 8
        elif type_id == 0 and remaining == 6:
            fmt_raw = self._slice(p, 6)
            p += 6
        else:
            flen = be_u16(self.data, p)
            fstart = p + 2
            fend = fstart + flen
            if fend + 6 > len(self.data):
                raise TCDParseError("cell formula overruns input")
            formula_raw = self.data[fstart:fend]
            formula = decode_formula(formula_raw, col, row)
            p = fend
            fmt_raw = self._slice(p, 6)
            p += 6
            note = "cell-formula"

        actual = p - payload_start
        if actual == declared:
            pass
        elif actual + 1 == declared and self._valid_next_header(payload_start + actual):
            note += "+overlap"
        else:
            raise TCDParseError(
                f"cell length mismatch at {payload_start - 3:#x}: declared {declared}, parsed {actual}"
            )
        return actual, Cell(col, row, type_id, value_raw, formula_raw, CellFormat(fmt_raw), text, formula), note

    def _slice(self, off: int, length: int) -> bytes:
        if off + length > len(self.data):
            raise TCDParseError("slice overruns input")
        return self.data[off : off + length]

    def _valid_next_header(self, off: int) -> bool:
        if off == len(self.data):
            return True
        if off + 3 > len(self.data):
            return False
        rid = self.data[off]
        if rid not in VALID_RECORD_IDS:
            return False
        size = be_u16(self.data, off + 1)
        return off + 3 + size <= len(self.data)

    def _validate_tail(self, tail: bytes) -> None:
        if len(tail) <= 3:
            return
        first = tail[0]
        if first in (0x00, 0x04, 0x05):
            return
        raise TCDParseError(f"unsupported trailing data starts with 0x{first:02X}")


def a1(col: int, row: int) -> str:
    if col < 0 or row < 0:
        return f"R{row + 1}C{col + 1}"
    n = col + 1
    letters = ""
    while n:
        n, rem = divmod(n - 1, 26)
        letters = chr(ord("A") + rem) + letters
    return f"{letters}{row + 1}"


def rtf_escape(text: str) -> str:
    out = []
    for ch in text:
        code = ord(ch)
        if ch in "\\{}":
            out.append("\\" + ch)
        elif ch == "\n":
            out.append("\\line ")
        elif code < 128:
            out.append(ch)
        else:
            signed = code if code < 32768 else code - 65536
            out.append(f"\\u{signed}?")
    return "".join(out)


def color_index(doc: Document, pen: int) -> Optional[int]:
    if 1 <= pen <= len(doc.colors):
        return pen
    return None


def build_rtf(doc: Document) -> str:
    if doc.cells:
        max_row = min(max(r for r, _ in doc.cells), 250)
        max_col = min(max(c for _, c in doc.cells), 40)
    else:
        max_row = 0
        max_col = 0

    color_table = [";"]
    for r, g, b in doc.colors:
        color_table.append(f"\\red{r}\\green{g}\\blue{b};")

    parts = [
        "{\\rtf1\\ansi\\deff0",
        "{\\fonttbl{\\f0 Arial;}{\\f1 Courier New;}}",
        "{\\colortbl" + "".join(color_table) + "}",
        "\\paperw15840\\paperh12240\\margl720\\margr720\\margt720\\margb720",
        "\\fs18 ",
    ]

    twips = []
    pos = 900
    for col in range(max_col + 1):
        width = doc.widths.get(col, 2000)
        pos += max(700, min(2600, int(width * 0.75)))
        twips.append(pos)

    for row in range(max_row + 1):
        row_cells = [doc.cells.get((row, col)) for col in range(max_col + 1)]
        if not any(cell and cell.display() for cell in row_cells):
            continue
        merge_state = [0] * (max_col + 1)
        for col, cell in enumerate(row_cells):
            if not cell or merge_state[col] or cell.type_id != 7 or cell.fmt.align not in (0, 1):
                continue
            if not cell.display():
                continue
            next_used = max_col + 1
            for nxt in range(col + 1, max_col + 1):
                if row_cells[nxt] is not None:
                    next_used = nxt
                    break
            span = next_used - col
            if span > 1:
                merge_state[col] = 1
                for nxt in range(col + 1, next_used):
                    merge_state[nxt] = 2
        parts.append("\\trowd\\trgaph80\\trleft0")
        for col, cell in enumerate(row_cells):
            shading = ""
            if merge_state[col] == 1:
                shading += "\\clmgf"
            elif merge_state[col] == 2:
                shading += "\\clmrg"
            if cell:
                ci = color_index(doc, cell.fmt.bg_pen)
                if ci:
                    shading += f"\\clcbpat{ci}"
                border = cell.fmt.border
                bparts = []
                if border & 0x03:
                    bparts.append("\\clbrdrl\\brdrs")
                if border & 0x0C:
                    bparts.append("\\clbrdrr\\brdrs")
                if border & 0x30:
                    bparts.append("\\clbrdrt\\brdrs")
                if border & 0xC0:
                    bparts.append("\\clbrdrb\\brdrs")
                shading += "".join(bparts)
            parts.append(f"{shading}\\cellx{twips[col]}")
        parts.append("\n")
        for col, cell in enumerate(row_cells):
            if not cell or merge_state[col] == 2:
                parts.append("\\pard\\intbl \\cell")
                continue
            align = {2: "\\qr ", 3: "\\qc "}.get(cell.fmt.align, "")
            styles = ""
            if cell.fmt.bold:
                styles += "\\b "
            if cell.fmt.italic:
                styles += "\\i "
            if cell.fmt.underline:
                styles += "\\ul "
            ci = color_index(doc, cell.fmt.text_pen)
            color = f"\\cf{ci} " if ci else ""
            reset = "\\b0\\i0\\ul0\\cf0 "
            parts.append(
                f"\\pard\\intbl {align}{styles}{color}{rtf_escape(cell.display())}{reset}\\cell"
            )
        parts.append("\\row\n")
    parts.append("}")
    return "".join(parts)


def convert(input_path: Path, output_path: Path) -> None:
    data = input_path.read_bytes()
    doc = Parser(data).parse()
    rtf = build_rtf(doc)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=output_path.name + ".", suffix=".tmp", dir=str(output_path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(rtf)
        os.chmod(tmp_name, 0o664)
        os.replace(tmp_name, output_path)
        os.chmod(output_path, 0o664)
    except Exception:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        try:
            output_path.unlink()
        except FileNotFoundError:
            pass
        raise


def main(argv: List[str]) -> int:
    if len(argv) != 3:
        print("usage: turboCalc.py <inputFile> <outputFile>", file=sys.stderr)
        return 2
    input_path = Path(argv[1])
    output_path = Path(argv[2])
    try:
        convert(input_path, output_path)
    except Exception as exc:
        try:
            output_path.unlink()
        except FileNotFoundError:
            pass
        print(f"turboCalc.py: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

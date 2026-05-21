#!/usr/bin/env python3
# Vibe coded by Codex
from __future__ import annotations

import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


class PerfectFormsError(ValueError):
    pass


@dataclass
class ParsedForm:
    family: str
    width: int
    rows: list[bytes]
    title: str
    notes: list[str]


DISPLAY_SPACE_BYTES = {
    0x00,  # compact/raw empty cell
    0x01, 0x02, 0x04, 0x05, 0x07,  # observed non-printing field/attribute cells
    0x10, 0x80, 0x90,  # observed fill-field marker cells
    0x7E,  # Perfect Forms visible-space marker
}


def parse_compact(data: bytes) -> ParsedForm:
    if len(data) < 32:
        raise PerfectFormsError("file is too short for a compact Perfect Forms header")
    if data[0] != 0x56 or data[1] != 0x00 or data[4] != 0x4D:
        raise PerfectFormsError("not a compact Perfect Forms file")

    visible_half_rows = data[2]
    width = data[3]
    if not (1 <= visible_half_rows <= 128 and 32 <= width <= 160):
        raise PerfectFormsError("compact header has an unsupported geometry")

    info_at = None
    for i in range(5, min(len(data) - 13, 64)):
        if data[i] != 0x49:
            continue
        title_len = data[i + 1]
        settings_at = i + 2 + title_len
        marker_at = settings_at + 9
        if marker_at + 13 <= len(data) and data[marker_at:marker_at + 3] == b"\x00\x00\x01":
            info_at = i
            break
    if info_at is None:
        raise PerfectFormsError("compact header does not contain a valid information block")

    title_len = data[info_at + 1]
    title_bytes = data[info_at + 2:info_at + 2 + title_len]
    title = title_bytes.decode("cp437", errors="replace")
    settings_at = info_at + 2 + title_len
    settings = data[settings_at:settings_at + 9]
    if len(settings) != 9:
        raise PerfectFormsError("compact header settings block is truncated")

    marker_at = settings_at + 9
    stream_kind = data[marker_at + 3]
    if stream_kind not in (0x42, 0x58):
        raise PerfectFormsError("compact body has an unsupported stream kind")
    reserved = data[marker_at + 4:marker_at + 12]
    if reserved not in (b"\x00" * 8, b"\x50" + b"\x00" * 7):
        raise PerfectFormsError("compact body reserved bytes have an unsupported pattern")
    if data[marker_at + 12] != 0x42:
        raise PerfectFormsError("compact body stream marker is missing")

    visible_cells = visible_half_rows * 2 * width
    stream_at = marker_at + 13
    expanded = bytearray()
    pos = stream_at
    complete_visible_plane = True

    while len(expanded) < visible_cells and pos < len(data):
        byte = data[pos]
        pos += 1
        if byte == 0x08:
            if pos + 2 > len(data):
                raise PerfectFormsError("compact run-length token is truncated")
            value = data[pos]
            count = data[pos + 1]
            pos += 2
            if count == 0:
                raise PerfectFormsError("compact run-length token has a zero count")
            if len(expanded) + count > visible_cells:
                raise PerfectFormsError("compact run-length token crosses the visible plane boundary")
            expanded.extend([value] * count)
        else:
            expanded.append(byte)

    if len(expanded) < visible_cells:
        complete_visible_plane = False

    metadata = b""
    terminator = None
    if complete_visible_plane:
        remainder = data[pos:]
        if remainder:
            terminator = remainder[-1]
            if terminator != 0x2A:
                raise PerfectFormsError("compact file has non-empty data after the visible plane without a '*' terminator")
            metadata = remainder[:-1]
    else:
        # One observed compact sample is an unterminated partial stream. Consume all bytes
        # as the partial plane; there is no byte left to classify as metadata.
        if pos != len(data):
            raise PerfectFormsError("partial compact stream parser did not consume the file")

    rows = [bytes(expanded[i:i + width]) for i in range(0, len(expanded), width)]
    notes = [
        f"compact stream kind 0x{stream_kind:02X}",
        f"header settings {settings.hex(' ')}",
        f"body reserved bytes {reserved.hex(' ')}",
    ]
    if data[5:info_at]:
        notes.append(f"pre-information option bytes {data[5:info_at].hex(' ')}")
    if metadata:
        notes.append(f"{len(metadata)} bytes of post-plane formula/metadata were parsed and not rendered")
    if terminator == 0x2A:
        notes.append("complete stream terminator 0x2A")
    if not complete_visible_plane:
        notes.append("unterminated partial stream; rendered all available cells")

    return ParsedForm("compact", width, rows, title, notes)


def parse_raw(data: bytes) -> ParsedForm:
    if len(data) < 128 or data[6:9] != b"FRM" or data[3:6] != b"\x00\x00\x00":
        raise PerfectFormsError("not a raw Perfect Forms file")

    title = ""
    declared_rows: int | None = None
    if data[:3] == b"APP":
        width = 80
        title = "APP raw form"
    elif data[1] in (0x47, 0x4F, 0x50, 0x82, 0x84, 0x88) and data[2] == 0x50:
        declared_rows = data[0]
        width = data[1]
        title = "raw form"
    else:
        raise PerfectFormsError("raw Perfect Forms header has an unsupported geometry")

    body = data[127:]
    if declared_rows is not None:
        visible_len = declared_rows * width
        if len(body) < visible_len:
            raise PerfectFormsError("raw body is shorter than the declared geometry")
        plane = body[:visible_len]
        padding = body[visible_len:]
        if any(b not in (0x00, 0x20, 0x2D, 0x7C, 0x7E, 0x07) for b in padding):
            raise PerfectFormsError("raw padding contains unsupported non-padding bytes")
    else:
        plane = body
        padding = b""

    rows = [plane[i:i + width] for i in range(0, len(plane), width)]
    notes = ["127-byte raw header"]
    if declared_rows is not None:
        notes.append(f"declared rows {declared_rows}")
    if padding:
        notes.append(f"{len(padding)} trailing raw padding bytes were parsed and not rendered")
    return ParsedForm("raw", width, rows, title, notes)


def parse_form(data: bytes) -> ParsedForm:
    parsers = (parse_compact, parse_raw)
    errors = []
    for parser in parsers:
        try:
            return parser(data)
        except PerfectFormsError as exc:
            errors.append(str(exc))
    raise PerfectFormsError("; ".join(errors))


def display_char(byte: int) -> str:
    if byte in DISPLAY_SPACE_BYTES:
        return " "
    if byte < 0x20:
        return " "
    return bytes([byte]).decode("cp437", errors="replace")


def row_to_text(row: bytes) -> str:
    return "".join(display_char(b) for b in row).rstrip()


def presentation_rows(rows: list[bytes], family: str) -> list[bytes]:
    if family == "compact":
        rows = rows[::2]
    rows = [row for row in rows if row_to_text(row).strip()]
    return rows or [b""]


def trim_rows(rows: list[bytes], family: str) -> list[str]:
    return [row_to_text(row) for row in presentation_rows(rows, family)]


BOX_COMPONENTS = {
    0xB3: ((), ("u", "d")), 0xC4: (("l", "r"), ()),
    0xDA: (("r",), ("d",)), 0xBF: (("l",), ("d",)),
    0xC0: (("r",), ("u",)), 0xD9: (("l",), ("u",)),
    0xC3: (("r",), ("u", "d")), 0xB4: (("l",), ("u", "d")),
    0xC2: (("l", "r"), ("d",)), 0xC1: (("l", "r"), ("u",)),
    0xC5: (("l", "r"), ("u", "d")),
    0xBA: ((), ("u2", "d2")), 0xCD: (("l2", "r2"), ()),
    0xC9: (("r2",), ("d2",)), 0xBB: (("l2",), ("d2",)),
    0xC8: (("r2",), ("u2",)), 0xBC: (("l2",), ("u2",)),
    0xCC: (("r2",), ("u2", "d2")), 0xB9: (("l2",), ("u2", "d2")),
    0xCB: (("l2", "r2"), ("d2",)), 0xCA: (("l2", "r2"), ("u2",)),
    0xCE: (("l2", "r2"), ("u2", "d2")),
    0xD5: (("r2",), ("d",)), 0xB8: (("l2",), ("d",)),
    0xD4: (("r2",), ("u",)), 0xBE: (("l2",), ("u",)),
    0xD6: (("r",), ("d2",)), 0xB7: (("l",), ("d2",)),
    0xD3: (("r",), ("u2",)), 0xBD: (("l",), ("u2",)),
    0xC6: (("r2",), ("u", "d")), 0xB5: (("l2",), ("u", "d")),
    0xC7: (("r",), ("u2", "d2")), 0xB6: (("l",), ("u2", "d2")),
    0xD1: (("l2", "r2"), ("d",)), 0xCF: (("l2", "r2"), ("u",)),
    0xD2: (("l", "r"), ("d2",)), 0xD0: (("l", "r"), ("u2",)),
    0xD8: (("l2", "r2"), ("u", "d")),
    0xD7: (("l", "r"), ("u2", "d2")),
    0xDE: ((), ("u", "d")), 0xDD: ((), ("u", "d")),
    0xDF: (("l", "r"), ()), 0xDC: (("l", "r"), ()),
}


SHADE_BYTES = {0xB0: 70, 0xB1: 130, 0xB2: 190, 0xDB: 255}
ASCII_LINE_CANDIDATES = {0x2D, 0x3D, 0x5F, 0x7C}
OPPOSITE = {"l": "r", "r": "l", "u": "d", "d": "u"}


def xml_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def box_connectors(byte: int) -> dict[str, str]:
    components = BOX_COMPONENTS.get(byte)
    if components is None:
        return {}

    horizontal, vertical = components
    connectors: dict[str, str] = {}
    for direction in horizontal + vertical:
        connectors[direction[0]] = "double" if direction.endswith("2") else "single"
    return connectors


def byte_at(rows: list[bytes], row_index: int, col_index: int) -> int:
    if not (0 <= row_index < len(rows)):
        return 0x20
    row = rows[row_index]
    if not (0 <= col_index < len(row)):
        return 0x20
    return row[col_index]


def base_line_connectors(byte: int) -> dict[str, str]:
    connectors = box_connectors(byte)
    if connectors:
        return connectors
    if byte == 0x7C:
        return {"u": "single", "d": "single"}
    return {}


def has_horizontal_neighbor(rows: list[bytes], row_index: int, col_index: int, direction: str) -> bool:
    neighbor_col = col_index - 1 if direction == "l" else col_index + 1
    neighbor = byte_at(rows, row_index, neighbor_col)
    if neighbor in (0x2D, 0x3D, 0x5F):
        return True
    return OPPOSITE[direction] in base_line_connectors(neighbor)


def has_vertical_neighbor(rows: list[bytes], row_index: int, col_index: int, direction: str) -> bool:
    neighbor_row = row_index - 1 if direction == "u" else row_index + 1
    neighbor = byte_at(rows, neighbor_row, col_index)
    if neighbor == 0x7C:
        return True
    return OPPOSITE[direction] in base_line_connectors(neighbor)


def cell_connectors(rows: list[bytes], row_index: int, col_index: int) -> dict[str, str]:
    byte = byte_at(rows, row_index, col_index)
    connectors = base_line_connectors(byte)
    if connectors:
        return connectors
    if byte == 0x2D:
        style = "single"
    elif byte == 0x5F:
        style = "single"
    elif byte == 0x3D:
        style = "double"
    else:
        return {}

    resolved: dict[str, str] = {}
    if has_horizontal_neighbor(rows, row_index, col_index, "l"):
        resolved["l"] = style
    if has_horizontal_neighbor(rows, row_index, col_index, "r"):
        resolved["r"] = style
    return resolved


def line_grid(rows: list[bytes], width: int) -> list[list[dict[str, str]]]:
    grid = [
        [cell_connectors(rows, row_index, col_index) for col_index in range(width)]
        for row_index in range(len(rows))
    ]
    for row_index, row in enumerate(grid):
        for col_index, connectors in enumerate(row):
            byte = byte_at(rows, row_index, col_index)
            if byte != 0x7C:
                continue
            if not (
                has_vertical_neighbor(rows, row_index, col_index, "u")
                or has_vertical_neighbor(rows, row_index, col_index, "d")
            ):
                grid[row_index][col_index] = {}
    return grid


def add_horizontal_run(
    runs: dict[tuple[float, float], list[tuple[float, float]]],
    style: str,
    y: float,
    x0: float,
    x1: float,
    offset: float,
    thickness: float,
) -> None:
    offsets = (-offset, offset) if style == "double" else (0.0,)
    for dy in offsets:
        runs.setdefault((round(y + dy, 3), round(thickness, 3)), []).append((x0, x1))


def add_vertical_run(
    runs: dict[tuple[float, float], list[tuple[float, float]]],
    style: str,
    x: float,
    y0: float,
    y1: float,
    offset: float,
    thickness: float,
) -> None:
    offsets = (-offset, offset) if style == "double" else (0.0,)
    for dx in offsets:
        runs.setdefault((round(x + dx, 3), round(thickness, 3)), []).append((y0, y1))


def add_center_join(
    elements: list[str],
    connectors: dict[str, str],
    cx: float,
    cy: float,
    offset: float,
    thickness: float,
) -> None:
    has_horizontal = "l" in connectors or "r" in connectors
    has_vertical = "u" in connectors or "d" in connectors
    if not (has_horizontal and has_vertical):
        return
    half_size = thickness / 2
    if "double" in connectors.values():
        half_size = offset + thickness / 2
    elements.append(
        f'<rect x="{(cx - half_size):.2f}" y="{(cy - half_size):.2f}" '
        f'width="{(half_size * 2):.2f}" height="{(half_size * 2):.2f}" fill="#000"/>'
    )


def merge_intervals(intervals: list[tuple[float, float]]) -> list[tuple[float, float]]:
    if not intervals:
        return []
    ordered = sorted((min(a, b), max(a, b)) for a, b in intervals)
    merged = [ordered[0]]
    epsilon = 0.01
    for start, end in ordered[1:]:
        prev_start, prev_end = merged[-1]
        if start <= prev_end + epsilon:
            merged[-1] = (prev_start, max(prev_end, end))
        else:
            merged.append((start, end))
    return merged


def build_svg(form: ParsedForm) -> str:
    rows = presentation_rows(form.rows, form.family)
    width = max(form.width, max((len(row) for row in rows), default=0))
    if width >= 100:
        cell_w, cell_h, font_size = 9.0, 16.0, 13.0
    else:
        cell_w, cell_h, font_size = 12.0, 20.0, 16.0
    margin = cell_w
    image_w = width * cell_w + margin * 2
    image_h = len(rows) * cell_h + margin * 2
    baseline = cell_h * 0.72

    elements = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!-- Vibe coded by Codex -->',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" '
            f'width="{image_w:.0f}" height="{image_h:.0f}" viewBox="0 0 {image_w:.0f} {image_h:.0f}">'
        ),
        '<rect width="100%" height="100%" fill="#fff"/>',
        '<g shape-rendering="crispEdges">',
    ]

    grid = line_grid(rows, width)
    horizontal_runs: dict[tuple[float, float], list[tuple[float, float]]] = {}
    vertical_runs: dict[tuple[float, float], list[tuple[float, float]]] = {}
    line_width = 1.4
    line_offset = round(max(2.0, min(cell_w, cell_h) / 8))
    for row_index, row in enumerate(rows):
        y = margin + row_index * cell_h
        for col_index in range(width):
            byte = row[col_index] if col_index < len(row) else 0x20
            if byte in DISPLAY_SPACE_BYTES or byte == 0x20:
                continue
            shade = SHADE_BYTES.get(byte)
            x = margin + col_index * cell_w
            if shade is not None:
                gray = 255 - shade
                elements.append(
                    f'<rect x="{x:.2f}" y="{y:.2f}" width="{cell_w:.2f}" height="{cell_h:.2f}" '
                    f'fill="rgb({gray},{gray},{gray})"/>'
                )
                continue
            connectors = grid[row_index][col_index]
            if connectors:
                cx = x + cell_w / 2
                cy = y + cell_h / 2
                if "l" in connectors:
                    add_horizontal_run(horizontal_runs, connectors["l"], cy, x, cx, line_offset, line_width)
                if "r" in connectors:
                    add_horizontal_run(horizontal_runs, connectors["r"], cy, cx, x + cell_w, line_offset, line_width)
                if "u" in connectors:
                    add_vertical_run(vertical_runs, connectors["u"], cx, y, cy, line_offset, line_width)
                if "d" in connectors:
                    add_vertical_run(vertical_runs, connectors["d"], cx, cy, y + cell_h, line_offset, line_width)
                add_center_join(elements, connectors, cx, cy, line_offset, line_width)
                continue

    for (line_y, line_width), intervals in sorted(horizontal_runs.items()):
        for x0, x1 in merge_intervals(intervals):
            elements.append(
                f'<rect x="{x0:.2f}" y="{(line_y - line_width / 2):.2f}" '
                f'width="{(x1 - x0):.2f}" height="{line_width:.2f}" fill="#000"/>'
            )
    for (line_x, line_width), intervals in sorted(vertical_runs.items()):
        for y0, y1 in merge_intervals(intervals):
            elements.append(
                f'<rect x="{(line_x - line_width / 2):.2f}" y="{y0:.2f}" '
                f'width="{line_width:.2f}" height="{(y1 - y0):.2f}" fill="#000"/>'
            )

    elements.append("</g>")
    elements.append(
        f'<g font-family="DejaVu Sans Mono, Liberation Mono, Courier New, monospace" '
        f'font-size="{font_size:.2f}" fill="#000" xml:space="preserve">'
    )
    for row_index, row in enumerate(rows):
        y = margin + row_index * cell_h
        col = 0
        while col < width:
            byte = row[col] if col < len(row) else 0x20
            if grid[row_index][col] or byte in SHADE_BYTES or byte in DISPLAY_SPACE_BYTES or byte == 0x20:
                col += 1
                continue
            start = col
            chars: list[str] = []
            while col < width:
                byte = row[col] if col < len(row) else 0x20
                if grid[row_index][col] or byte in SHADE_BYTES:
                    break
                chars.append(display_char(byte))
                col += 1
            text = "".join(chars).rstrip()
            if text:
                x = margin + start * cell_w
                elements.append(
                    f'<text x="{x:.2f}" y="{(y + baseline):.2f}">{xml_escape(text)}</text>'
                )
    elements.append("</g>")
    elements.append("</svg>")
    return "\n".join(elements) + "\n"


def convert(input_path: Path, output_path: Path) -> None:
    data = input_path.read_bytes()
    form = parse_form(data)
    svg = build_svg(form)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=output_path.name + ".", suffix=".tmp", dir=str(output_path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(svg)
        os.chmod(temp_name, 0o664)
        os.replace(temp_name, output_path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: perfectForms.py <inputFile.frm> <outputFile.svg>", file=sys.stderr)
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
        print(f"perfectForms.py: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

#!/usr/bin/env python3
# Vibe coded by Codex
"""Convert IBM Storyboard Text Maker EP_CAP documents to ANSI art."""

from __future__ import annotations

import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


MAGIC_PREFIX = b"EP_CAP\x00"
FIXED_HEADER_TAIL = bytes([0x03, 0x50, 0x00, 0x00, 0xA0, 0x00, 0x19, 0x00])
TRAILER = b"\x00" * 12
WIDTH = 80
HEIGHT = 25
CELLS = WIDTH * HEIGHT

# ANSI art cannot safely contain these screen glyph bytes literally: 0x1A is
# commonly consumed as DOS EOF/SUB, and 0x1B starts ANSI escape sequences.
ANSI_CONTROL_GLYPH_FALLBACKS = {
    0x00: b" ",
    0x1A: b">",
    0x1B: b"<",
}

CGA_TO_ANSI_COLOR = {
    0: 0,  # black
    1: 4,  # blue
    2: 2,  # green
    3: 6,  # cyan
    4: 1,  # red
    5: 5,  # magenta
    6: 3,  # brown/yellow
    7: 7,  # light gray/white
}


class FormatError(ValueError):
    """Raised when the input is not a supported EP_CAP Text Maker document."""


@dataclass(frozen=True)
class Screen:
    chars: bytes
    attrs: bytes


def parse_rle_plane(
    data: bytes, offset: int, name: str, require_terminator: bool
) -> tuple[bytes, int]:
    out = bytearray()
    pos = offset

    while True:
        if pos + 2 > len(data):
            raise FormatError(f"{name} plane is missing a run header at offset {pos}")

        low = data[pos]
        high = data[pos + 1]
        pos += 2

        if high & 0x80:
            count = low + ((high & 0x7F) << 8)
            if count == 0:
                raise FormatError(f"{name} plane has an invalid zero-length repeat run")
            if pos >= len(data):
                raise FormatError(f"{name} plane repeat run is missing its byte value")
            value = data[pos]
            pos += 1
            out.extend(bytes([value]) * count)
        else:
            count = low + (high << 8)
            if count == 0:
                if not require_terminator:
                    raise FormatError(f"{name} plane has an unexpected terminator")
                if len(out) != CELLS:
                    raise FormatError(
                        f"{name} plane terminated after {len(out)} cells, expected {CELLS}"
                    )
                return bytes(out), pos
            if pos + count > len(data):
                raise FormatError(f"{name} plane literal run extends past content")
            out.extend(data[pos : pos + count])
            pos += count

        if len(out) > CELLS:
            raise FormatError(f"{name} plane expands past {CELLS} cells")
        if len(out) == CELLS and not require_terminator:
            return bytes(out), pos


def parse_document(blob: bytes) -> Screen:
    if len(blob) < 17 + len(TRAILER):
        raise FormatError("file is too short")
    if blob[:7] != MAGIC_PREFIX:
        raise FormatError("missing EP_CAP signature")
    if blob[7:15] != FIXED_HEADER_TAIL:
        raise FormatError("unsupported EP_CAP header values")
    if blob[-12:] != TRAILER:
        raise FormatError("missing 12-byte zero trailer")

    content_len = int.from_bytes(blob[15:17], "little")
    if content_len < 2:
        raise FormatError("content length is smaller than its own length field")
    expected_len = 15 + content_len + len(TRAILER)
    if len(blob) != expected_len:
        raise FormatError(
            f"content length says {content_len} bytes, but file is {len(blob)} bytes"
        )

    content = blob[17 : 15 + content_len]
    chars, pos = parse_rle_plane(content, 0, "character", require_terminator=True)
    attrs, pos = parse_rle_plane(content, pos, "attribute", require_terminator=False)
    if pos != len(content):
        raise FormatError(f"{len(content) - pos} unexpected byte(s) after attribute plane")
    return Screen(chars=chars, attrs=attrs)


def screen_char_to_ansi_byte(value: int) -> bytes:
    return ANSI_CONTROL_GLYPH_FALLBACKS.get(value, bytes([value]))


def attrs_to_colors(attr: int) -> tuple[int, int, bool]:
    foreground = attr & 0x0F
    background = (attr >> 4) & 0x07
    blink = bool(attr & 0x80)
    return foreground, background, blink


def ansi_sgr(attr: int) -> bytes:
    fg, bg, blink = attrs_to_colors(attr)
    codes = ["0"]
    if blink:
        codes.append("5")
    if fg >= 8:
        codes.append("1")
        fg -= 8
    codes.append(str(30 + CGA_TO_ANSI_COLOR[fg]))
    codes.append(str(40 + CGA_TO_ANSI_COLOR[bg]))
    return f"\x1b[{';'.join(codes)}m".encode("ascii")


def render_ansi(screen: Screen) -> bytes:
    out = bytearray()
    current_attr: int | None = None

    for row in range(HEIGHT):
        start = row * WIDTH
        end = start + WIDTH
        for col in range(start, end):
            attr = screen.attrs[col]
            if attr != current_attr:
                out.extend(ansi_sgr(attr))
                current_attr = attr
            out.extend(screen_char_to_ansi_byte(screen.chars[col]))
    out.extend(b"\x1b[0m")
    return bytes(out)


def convert_file(input_path: Path, output_path: Path) -> None:
    blob = input_path.read_bytes()
    screen = parse_document(blob)
    ansi = render_ansi(screen)

    output_dir = output_path.parent if output_path.parent != Path("") else Path(".")
    output_dir.mkdir(parents=True, exist_ok=True)

    fd, temp_name = tempfile.mkstemp(
        prefix=f".{output_path.name}.", suffix=".tmp", dir=str(output_dir)
    )
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(ansi)
        os.chmod(temp_name, 0o664)
        os.replace(temp_name, output_path)
        os.chmod(output_path, 0o664)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(
            "Usage: ibmStoryboardDocument.py <inputFile> <outputFile.ans>",
            file=sys.stderr,
        )
        return 2

    input_path = Path(argv[1])
    output_path = Path(argv[2])
    try:
        convert_file(input_path, output_path)
    except (OSError, FormatError) as exc:
        try:
            if output_path.exists():
                output_path.unlink()
        except OSError:
            pass
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

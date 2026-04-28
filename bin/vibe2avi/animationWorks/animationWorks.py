#!/usr/bin/env python3
# Vibe coded by Codex
"""
Convert Gold Disk Animation Works Movie files to AVI.

The parser is intentionally strict: it consumes the complete container, nested
resource chunks, typed property streams, and DCL fragments before producing an
output file. Invalid input exits non-zero and leaves no output behind.
"""

from __future__ import annotations

import argparse
import io
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import wave
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    from PIL import Image
except Exception as exc:  # pragma: no cover - environment validation
    raise SystemExit(f"Pillow is required: {exc}")


class FormatError(Exception):
    pass


class BlastState:
    MAXWIN = 4096

    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0
        self.bitbuf = 0
        self.bitcnt = 0
        self.output = bytearray()
        self.window = bytearray(self.MAXWIN)
        self.next = 0
        self.first = True

    def bits(self, need: int) -> int:
        val = self.bitbuf
        while self.bitcnt < need:
            if self.pos >= len(self.data):
                raise FormatError("DCL stream ended inside a bit field")
            val |= self.data[self.pos] << self.bitcnt
            self.bitcnt += 8
            self.pos += 1
        self.bitbuf = val >> need
        self.bitcnt -= need
        return val & ((1 << need) - 1)


class Huffman:
    MAXBITS = 13

    def __init__(self, rep: list[int]):
        length: list[int] = []
        for val in rep:
            length.extend([val & 0x0F] * ((val >> 4) + 1))
        self.count = [0] * (self.MAXBITS + 1)
        for bitlen in length:
            self.count[bitlen] += 1
        left = 1
        for bitlen in range(1, self.MAXBITS + 1):
            left = (left << 1) - self.count[bitlen]
            if left < 0:
                raise FormatError("invalid DCL Huffman table")
        offs = [0] * (self.MAXBITS + 1)
        for bitlen in range(1, self.MAXBITS):
            offs[bitlen + 1] = offs[bitlen] + self.count[bitlen]
        self.symbol = [0] * len(length)
        for sym, bitlen in enumerate(length):
            if bitlen:
                self.symbol[offs[bitlen]] = sym
                offs[bitlen] += 1

    def decode(self, state: BlastState) -> int:
        code = 0
        first = 0
        index = 0
        for bitlen in range(1, self.MAXBITS + 1):
            code = (code << 1) | (state.bits(1) ^ 1)
            count = self.count[bitlen]
            if code < first + count:
                return self.symbol[index + code - first]
            index += count
            first = (first + count) << 1
        raise FormatError("invalid DCL Huffman code")


class DCLExploder:
    LITLEN = [
        11, 124, 8, 7, 28, 7, 188, 13, 76, 4, 10, 8, 12, 10, 12, 10, 8, 23,
        8, 9, 7, 6, 7, 8, 7, 6, 55, 8, 23, 24, 12, 11, 7, 9, 11, 12, 6, 7,
        22, 5, 7, 24, 6, 11, 9, 6, 7, 22, 7, 11, 38, 7, 9, 8, 25, 11, 8,
        11, 9, 12, 8, 12, 5, 38, 5, 38, 5, 11, 7, 5, 6, 21, 6, 10, 53, 8,
        7, 24, 10, 27, 44, 253, 253, 253, 252, 252, 252, 13, 12, 45, 12,
        45, 12, 61, 12, 45, 44, 173,
    ]
    LENLEN = [2, 35, 36, 53, 38, 23]
    DISTLEN = [2, 20, 53, 230, 247, 151, 248]
    BASE = [3, 2, 4, 5, 6, 7, 8, 9, 10, 12, 16, 24, 40, 72, 136, 264]
    EXTRA = [0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8]

    def __init__(self):
        self.litcode = Huffman(self.LITLEN)
        self.lencode = Huffman(self.LENLEN)
        self.distcode = Huffman(self.DISTLEN)

    def decompress(self, data: bytes) -> bytes:
        st = BlastState(data)
        literal_mode = st.bits(8)
        if literal_mode > 1:
            raise FormatError("invalid DCL literal mode")
        dict_bits = st.bits(8)
        if not 4 <= dict_bits <= 6:
            raise FormatError("invalid DCL dictionary size")
        while True:
            if st.bits(1):
                symbol = self.lencode.decode(st)
                length = self.BASE[symbol] + st.bits(self.EXTRA[symbol])
                if length == 519:
                    break
                dist_bits = 2 if length == 2 else dict_bits
                dist = (self.distcode.decode(st) << dist_bits) + st.bits(dist_bits) + 1
                if st.first and dist > st.next:
                    raise FormatError("DCL distance too far back")
                for _ in range(length):
                    b = st.window[(st.next - dist) % st.MAXWIN]
                    st.window[st.next % st.MAXWIN] = b
                    st.output.append(b)
                    st.next += 1
                    if st.next >= st.MAXWIN:
                        st.first = False
            else:
                sym = self.litcode.decode(st) if literal_mode else st.bits(8)
                st.window[st.next % st.MAXWIN] = sym
                st.output.append(sym)
                st.next += 1
                if st.next >= st.MAXWIN:
                    st.first = False
        return bytes(st.output)


EXPLODER = DCLExploder()


def u16(data: bytes, off: int) -> int:
    return struct.unpack_from("<H", data, off)[0]


def s16(data: bytes, off: int) -> int:
    return struct.unpack_from("<h", data, off)[0]


def u32(data: bytes, off: int) -> int:
    return struct.unpack_from("<I", data, off)[0]


def is_upper_chunk(tag: bytes) -> bool:
    return len(tag) == 4 and all((65 <= c <= 90) or (48 <= c <= 57) for c in tag)


def parse_typed_stream(data: bytes, context: str) -> list[tuple[str, Any]]:
    out: list[tuple[str, Any]] = []
    off = 0
    while off < len(data):
        if off + 4 > len(data):
            raise FormatError(f"{context}: truncated field tag")
        tag_b = data[off:off + 4]
        tag = tag_b.decode("latin1")
        off += 4
        if is_upper_chunk(tag_b):
            if off + 4 > len(data):
                raise FormatError(f"{context}/{tag}: truncated chunk size")
            size = u32(data, off)
            off += 4
            end = off + size
            if end > len(data):
                raise FormatError(f"{context}/{tag}: chunk overruns parent")
            out.append((tag, parse_typed_stream(data[off:end], f"{context}/{tag}")))
            off = end
            continue
        typ = tag_b[:2]
        if typ in (b"ps", b"fn"):
            if off >= len(data):
                raise FormatError(f"{context}/{tag}: truncated Pascal string")
            size = data[off]
            off += 1
            end = off + size
            if end > len(data):
                raise FormatError(f"{context}/{tag}: Pascal string overruns stream")
            out.append((tag, data[off:end].decode("latin1")))
            off = end
        elif typ == b"wd":
            if off + 2 > len(data):
                raise FormatError(f"{context}/{tag}: truncated word")
            out.append((tag, u16(data, off)))
            off += 2
        elif typ == b"dw":
            if off + 4 > len(data):
                raise FormatError(f"{context}/{tag}: truncated dword")
            out.append((tag, u32(data, off)))
            off += 4
        elif typ in (b"td", b"tz"):
            if off + 4 > len(data):
                raise FormatError(f"{context}/{tag}: truncated blob size")
            size = u32(data, off)
            off += 4
            end = off + size
            if end > len(data):
                raise FormatError(f"{context}/{tag}: blob overruns stream")
            out.append((tag, data[off:end]))
            off = end
        elif typ == b"pt":
            if off + 4 > len(data):
                raise FormatError(f"{context}/{tag}: truncated point")
            out.append((tag, (s16(data, off), s16(data, off + 2))))
            off += 4
        elif typ == b"rc":
            if off + 8 > len(data):
                raise FormatError(f"{context}/{tag}: truncated rectangle")
            out.append((tag, tuple(s16(data, off + i) for i in range(0, 8, 2))))
            off += 8
        elif typ == b"by":
            if off >= len(data):
                raise FormatError(f"{context}/{tag}: truncated byte")
            out.append((tag, data[off]))
            off += 1
        elif typ == b"nn":
            out.append((tag, None))
        else:
            raise FormatError(f"{context}: unknown field tag {tag_b!r}")
    return out


def parse_chunk_list(data: bytes, context: str) -> list[tuple[str, bytes]]:
    out: list[tuple[str, bytes]] = []
    off = 0
    while off < len(data):
        if off + 8 > len(data):
            raise FormatError(f"{context}: truncated chunk header")
        tag_b = data[off:off + 4]
        if not is_upper_chunk(tag_b):
            raise FormatError(f"{context}: invalid chunk tag {tag_b!r}")
        tag = tag_b.decode("latin1")
        size = u32(data, off + 4)
        off += 8
        end = off + size
        if end > len(data):
            raise FormatError(f"{context}/{tag}: chunk overruns parent")
        out.append((tag, data[off:end]))
        off = end
    return out


def decompress_tz(blob: bytes, context: str) -> bytes:
    out = bytearray()
    off = 0
    while off < len(blob):
        if off + 8 > len(blob):
            raise FormatError(f"{context}: truncated DCL fragment header")
        comp_size = u32(blob, off)
        raw_size = u32(blob, off + 4)
        off += 8
        end = off + comp_size
        if end > len(blob):
            raise FormatError(f"{context}: DCL fragment overruns blob")
        raw = EXPLODER.decompress(blob[off:end])
        if len(raw) != raw_size:
            raise FormatError(f"{context}: DCL fragment expanded to {len(raw)}, expected {raw_size}")
        out.extend(raw)
        off = end
    return bytes(out)


def color_from_dword(value: int) -> tuple[int, int, int]:
    # Stored as COLORREF-style bytes: rr gg bb flag.
    return (value & 0xFF, (value >> 8) & 0xFF, (value >> 16) & 0xFF)


def patch_bmp_palette(blob: bytes, palette: list[tuple[int, int, int]] | None) -> bytes:
    if not palette or len(blob) < 54 or not blob.startswith(b"BM"):
        return blob
    pixel_offset = u32(blob, 10)
    dib_size = u32(blob, 14)
    if dib_size < 40 or 14 + dib_size > pixel_offset:
        return blob
    bpp = u16(blob, 28)
    if bpp > 8:
        return blob
    pal_start = 14 + dib_size
    pal_entries = (pixel_offset - pal_start) // 4
    out = bytearray(blob)
    for i, (r, g, b) in enumerate(palette):
        idx = 10 + i
        if idx >= pal_entries:
            break
        off = pal_start + idx * 4
        out[off:off + 4] = bytes((b, g, r, 0))
    return bytes(out)


def decode_bmp(blob: bytes, context: str, transparent: int | None = None, palette: list[tuple[int, int, int]] | None = None) -> Image.Image:
    if not blob.startswith(b"BM"):
        raise FormatError(f"{context}: decompressed image is not BMP/DIB")
    blob = patch_bmp_palette(blob, palette)
    with Image.open(io.BytesIO(blob)) as img:
        rgba = img.convert("RGBA")
    if transparent is not None:
        key = color_from_dword(transparent)
        pix = rgba.load()
        for y in range(rgba.height):
            for x in range(rgba.width):
                r, g, b, a = pix[x, y]
                if (r, g, b) == key:
                    pix[x, y] = (r, g, b, 0)
    return rgba


def decode_text_bitmap(bits: bytes, width: int, height: int, fg: int, bg: int) -> Image.Image:
    stride = (len(bits) // height) if height else 0
    if stride * height != len(bits) or stride <= 0:
        raise FormatError("text bitmap dimensions do not match tzbi size")
    fg_rgb = color_from_dword(fg)
    bg_rgb = color_from_dword(bg)
    img = Image.new("RGBA", (width, height), bg_rgb + (0,))
    pix = img.load()
    for y in range(height):
        row = bits[y * stride:(y + 1) * stride]
        for x in range(width):
            bit = (row[x >> 3] >> (7 - (x & 7))) & 1
            if bit == 0:
                pix[x, y] = fg_rgb + (255,)
    return img


def make_color_transparent(img: Image.Image, key: tuple[int, int, int]) -> int:
    pix = img.load()
    changed = 0
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = pix[x, y]
            if (r, g, b) == key:
                pix[x, y] = (r, g, b, 0)
                changed += 1
    return changed


def border_matte_color(img: Image.Image) -> tuple[int, int, int] | None:
    counts: dict[tuple[int, int, int], int] = {}
    w, h = img.size
    if w == 0 or h == 0:
        return None
    pix = img.load()
    total = 0
    for x in range(w):
        for y in (0, h - 1):
            r, g, b, a = pix[x, y]
            if a:
                counts[(r, g, b)] = counts.get((r, g, b), 0) + 1
                total += 1
    for y in range(h):
        for x in (0, w - 1):
            r, g, b, a = pix[x, y]
            if a:
                counts[(r, g, b)] = counts.get((r, g, b), 0) + 1
                total += 1
    if not counts:
        return None
    key, count = max(counts.items(), key=lambda item: item[1])
    if count * 2 < total:
        return None
    r, g, b = key
    if r == g == b:
        return None
    return key


@dataclass
class Cel:
    image: Image.Image
    size: tuple[int, int] = (0, 0)
    point: tuple[int, int] = (0, 0)
    registration: tuple[int, int] = (0, 0)
    is_text: bool = False


@dataclass
class Actor:
    name: str
    cels: list[Cel] = field(default_factory=list)


@dataclass
class Background:
    name: str
    image: Image.Image | None
    color: tuple[int, int, int] | None = None
    gradient: tuple[tuple[int, int], tuple[int, int], list[tuple[int, int, int]]] | None = None


@dataclass
class Sound:
    name: str
    data: bytes
    kind: str


@dataclass
class Track:
    start_frame: int
    target: str
    base: tuple[int, int]
    deltas: list[tuple[int, int, int, int]]


@dataclass
class LoopEvent:
    frame: int
    marker: str
    count: int


@dataclass
class Movie:
    frames: int
    frame_delay: int
    timing_events: dict[int, int]
    playback_delays: dict[int, int]
    actors: dict[str, Actor]
    backgrounds: dict[str, Background]
    sounds: dict[str, Sound]
    sound_events: list[tuple[int, str]]
    markers: dict[str, int]
    loops: list[LoopEvent]
    bg_events: dict[int, tuple[str | None, tuple[int, int, int] | None]]
    tracks: list[Track]
    width: int
    height: int


def prop_value(props: list[tuple[str, Any]], name: str, default: Any = None) -> Any:
    for tag, value in props:
        if tag == name:
            return value
    return default


def validate_all_tz(props: list[tuple[str, Any]], context: str) -> None:
    for tag, value in props:
        if isinstance(value, list):
            validate_all_tz(value, f"{context}/{tag}")
        elif tag.startswith("tz"):
            decompress_tz(value, f"{context}/{tag}")


def parse_actor(props: list[tuple[str, Any]], context: str, palettes: dict[str, list[tuple[int, int, int]]]) -> Actor:
    name = prop_value(props, "psnm", "Untitled")
    palette = palettes.get(prop_value(props, "pspl", ""))
    actor = Actor(name=name)
    current: dict[str, Any] = {}
    text_fg = 0
    text_bg = 0xFFFFFF
    for tag, value in props:
        if tag == "dwtc":
            text_fg = value
        elif tag == "dwbc":
            text_bg = value
        elif tag == "nnel":
            if current.get("image") is not None:
                image = current["image"]
                registration = current.get("ptrg")
                if registration is None and current.get("is_text"):
                    registration = (image.width // 2, image.height // 2)
                actor.cels.append(Cel(image, current.get("ptex", (0, 0)), current.get("ptps", (0, 0)), registration or (0, 0), bool(current.get("is_text"))))
            current = {}
        elif tag in ("ptex", "ptps", "ptrg"):
            current[tag] = value
        elif tag == "tzim":
            bmp = decompress_tz(value, f"{context}/{name}/tzim")
            current["image"] = decode_bmp(bmp, f"{context}/{name}/tzim", palette=palette)
        elif tag == "tzbi":
            w, h = current.get("ptex", (0, 0))
            bits = decompress_tz(value, f"{context}/{name}/tzbi")
            current["image"] = decode_text_bitmap(bits, w, h, text_fg, text_bg)
            current["is_text"] = True
        elif tag == "dwrb" and current.get("image") is not None:
            current["image"] = current["image"].copy()
            key = color_from_dword(value)
            changed = make_color_transparent(current["image"], key)
            if changed == 0:
                matte = border_matte_color(current["image"])
                if matte is not None:
                    make_color_transparent(current["image"], matte)
    if current.get("image") is not None:
        image = current["image"]
        registration = current.get("ptrg")
        if registration is None and current.get("is_text"):
            registration = (image.width // 2, image.height // 2)
        actor.cels.append(Cel(image, current.get("ptex", (0, 0)), current.get("ptps", (0, 0)), registration or (0, 0), bool(current.get("is_text"))))
    return actor


def parse_background(props: list[tuple[str, Any]], context: str, palettes: dict[str, list[tuple[int, int, int]]]) -> Background:
    name = prop_value(props, "psnm", "..Screen Background..")
    palette = palettes.get(prop_value(props, "pspl", ""))
    color = color_from_dword(prop_value(props, "dwbc", 0)) if prop_value(props, "dwbc") is not None else None
    image = None
    gradient = None
    for tag, value in props:
        if tag in ("tzfd", "tzim"):
            image = decode_bmp(decompress_tz(value, f"{context}/{name}/{tag}"), f"{context}/{name}/{tag}", palette=palette)
        elif tag == "tdgc":
            if len(value) % 4 != 0:
                raise FormatError(f"{context}/{name}/tdgc: color table is not dword-aligned")
            colors = [color_from_dword(u32(value, off)) for off in range(0, len(value), 4)]
            start = prop_value(props, "ptgs", (0, 0))
            end = prop_value(props, "ptge", (0, 1))
            gradient = (start, end, colors)
    return Background(name, image, color, gradient)


def parse_sound(props: list[tuple[str, Any]], context: str) -> Sound | None:
    name = prop_value(props, "psnm", "")
    data = None
    for tag, value in props:
        if tag == "tzfd":
            data = decompress_tz(value, f"{context}/{name}/tzfd")
    if data is None:
        return None
    if data.startswith(b"RIFF") and data[8:12] == b"WAVE":
        return Sound(name, data, "wav")
    if data.startswith(b"MThd"):
        return Sound(name, data, "midi")
    raise FormatError(f"{context}/{name}: unknown sound payload")


def parse_path(path_chunks: list[tuple[str, Any]]) -> list[Track]:
    tracks: list[Track] = []
    for tag, prtk in path_chunks:
        if tag != "PRTK":
            continue
        for subtag, ptin in prtk:
            if subtag != "PTIN":
                continue
            start = int(prop_value(ptin, "wdfn", 1))
            target = prop_value(ptin, "psst", prop_value(ptin, "psnm", ""))
            base = prop_value(ptin, "ptbs", (0, 0))
            deltas: list[tuple[int, int, int, int]] = []
            for dtag, blob in ptin:
                if dtag == "tdel":
                    if len(blob) != 8:
                        raise FormatError("PATH/PTIN/tdel is not 8 bytes")
                    deltas.append((s16(blob, 0), s16(blob, 2), u16(blob, 4), u16(blob, 6)))
            tracks.append(Track(start, target, base, deltas))
    return tracks


def render_gradient(width: int, height: int, gradient: tuple[tuple[int, int], tuple[int, int], list[tuple[int, int, int]]]) -> Image.Image:
    start, end, colors = gradient
    if not colors:
        return Image.new("RGB", (width, height), (0, 0, 0))
    if len(colors) == 1:
        return Image.new("RGB", (width, height), colors[0])

    dx = end[0] - start[0]
    dy = end[1] - start[1]
    if dx == 0 and dy == 0:
        dy = 1
    corners = [(0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)]
    projections = [x * dx + y * dy for x, y in corners]
    min_proj = min(projections)
    max_proj = max(projections)
    span = max(max_proj - min_proj, 1)
    img = Image.new("RGB", (width, height))
    pix = img.load()
    stops = len(colors) - 1
    for y in range(height):
        for x in range(width):
            t = ((x * dx + y * dy) - min_proj) / span
            t = min(1.0, max(0.0, t)) * stops
            idx = min(stops - 1, int(t))
            frac = t - idx
            c0 = colors[idx]
            c1 = colors[idx + 1]
            pix[x, y] = tuple(round(c0[i] + (c1[i] - c0[i]) * frac) for i in range(3))
    return img


def load_movie(path: Path) -> Movie:
    data = path.read_bytes()
    if len(data) < 8 or data[:4] != b"GDAW":
        raise FormatError("missing GDAW signature")
    if u32(data, 4) != len(data) - 8:
        raise FormatError("GDAW size does not match file length")
    top = parse_chunk_list(data[8:], "GDAW")
    if [tag for tag, _ in top] != ["VERS", "PREF", "RSRC", "SEEN"]:
        raise FormatError("top-level chunks are not VERS, PREF, RSRC, SEEN")

    parsed_top: dict[str, Any] = {}
    resource_chunks: list[tuple[str, list[tuple[str, Any]]]] = []
    for tag, payload in top:
        if tag == "RSRC":
            for rtag, rpayload in parse_chunk_list(payload, "GDAW/RSRC"):
                props = parse_typed_stream(rpayload, f"RSRC/{rtag}")
                validate_all_tz(props, f"RSRC/{rtag}")
                resource_chunks.append((rtag, props))
        else:
            props = parse_typed_stream(payload, f"GDAW/{tag}")
            validate_all_tz(props, f"GDAW/{tag}")
            parsed_top[tag] = props

    seen = parsed_top["SEEN"]
    frames = int(prop_value(seen, "wdnf", 1))
    if frames <= 0:
        raise FormatError("movie has no frames")
    pref_size = prop_value(parsed_top["PREF"], "ptex", (640, 480))
    actors: dict[str, Actor] = {}
    backgrounds: dict[str, Background] = {}
    sounds: dict[str, Sound] = {}
    palettes: dict[str, list[tuple[int, int, int]]] = {}
    max_w, max_h = int(pref_size[0]), int(pref_size[1])
    for rtag, props in resource_chunks:
        if rtag == "PALT":
            name = prop_value(props, "psnm")
            entries = prop_value(props, "tdpe")
            if name and isinstance(entries, bytes):
                if len(entries) % 4 != 0:
                    raise FormatError(f"RSRC/PALT/{name}: palette data is not dword-aligned")
                palettes[name] = [color_from_dword(u32(entries, off)) for off in range(0, len(entries), 4)]
    for rtag, props in resource_chunks:
        if rtag == "ACTR":
            actor = parse_actor(props, "RSRC/ACTR", palettes)
            actors.setdefault(actor.name, actor)
        elif rtag == "BKGD":
            bg = parse_background(props, "RSRC/BKGD", palettes)
            backgrounds[bg.name] = bg
            if bg.image is not None and bg.image.width > max_w:
                max_w = bg.image.width
            if bg.image is not None and bg.image.height > max_h:
                max_h = bg.image.height
        elif rtag == "SWND":
            sound = parse_sound(props, "RSRC/SWND")
            if sound is not None:
                sounds[sound.name] = sound

    frame_delay = 10
    timing_events: dict[int, int] = {}
    playback_delays: dict[int, int] = {}
    bg_events: dict[int, tuple[str | None, tuple[int, int, int] | None]] = {}
    sound_events: list[tuple[int, str]] = []
    markers: dict[str, int] = {}
    loops: list[LoopEvent] = []
    tracks: list[Track] = []
    fram = prop_value(seen, "FRAM")
    if not isinstance(fram, list):
        raise FormatError("SEEN has no FRAM chunk")
    for event_tag, props in fram:
        if not isinstance(props, list):
            continue
        frame = int(prop_value(props, "wdif", 1))
        if event_tag == "TMEV" and prop_value(props, "wddy") is not None:
            delay = int(prop_value(props, "wddy"))
            if delay <= 0:
                raise FormatError("TMEV has non-positive frame delay")
            timing_events[frame] = delay
            if frame == 1:
                frame_delay = delay
        elif event_tag == "BKEV":
            bg_name = prop_value(props, "psnm")
            bg_color = color_from_dword(prop_value(props, "dwbc")) if prop_value(props, "dwbc") is not None else None
            bg_events[frame] = (bg_name, bg_color)
        elif event_tag == "SNEV":
            sound_name = prop_value(props, "pssn")
            if sound_name and sound_name in sounds and sounds[sound_name].kind == "wav":
                sound_events.append((frame, sound_name))
        elif event_tag == "MKEV":
            marker_name = prop_value(props, "psnm")
            if marker_name:
                markers[marker_name] = frame
        elif event_tag == "PLEV" and prop_value(props, "wddy") is not None:
            delay = int(prop_value(props, "wddy"))
            if delay > 0:
                playback_delays[frame] = delay
        elif event_tag == "PLEV" and prop_value(props, "byty") == 108:
            marker_name = prop_value(props, "psmt")
            count = int(prop_value(props, "wdcn", 0))
            if marker_name and count > 0:
                loops.append(LoopEvent(frame, marker_name, count))
        elif event_tag == "PATH":
            tracks.extend(parse_path(props))
    if frame_delay <= 0:
        frame_delay = 10

    if 1 not in timing_events:
        timing_events[1] = frame_delay

    first_bg_frame = min(bg_events) if bg_events else None
    if first_bg_frame is not None:
        first_bg_name, _ = bg_events[first_bg_frame]
        first_bg = backgrounds.get(first_bg_name or "")
        if first_bg is not None and first_bg.image is not None and first_bg.image.width > 1 and first_bg.image.height > 1:
            max_w, max_h = first_bg.image.size

    return Movie(frames, frame_delay, timing_events, playback_delays, actors, backgrounds, sounds, sound_events, markers, loops, bg_events, tracks, max_w, max_h)


def render_frames(movie: Movie):
    active_bg_name: str | None = None
    active_bg_color: tuple[int, int, int] | None = (0, 0, 0)
    track_states: list[tuple[Track, tuple[int, int, int, int] | None]] = [(track, None) for track in movie.tracks]
    for frame_no in range(1, movie.frames + 1):
        if frame_no in movie.bg_events:
            active_bg_name, active_bg_color = movie.bg_events[frame_no]
        bg_img = None
        if active_bg_name and active_bg_name in movie.backgrounds:
            bg_img = movie.backgrounds[active_bg_name].image
        if bg_img is not None:
            frame = Image.new("RGB", (movie.width, movie.height), active_bg_color or (0, 0, 0))
            frame.paste(bg_img.convert("RGB"), (0, 0))
        elif active_bg_name and active_bg_name in movie.backgrounds and movie.backgrounds[active_bg_name].gradient:
            frame = render_gradient(movie.width, movie.height, movie.backgrounds[active_bg_name].gradient)
        else:
            frame = Image.new("RGB", (movie.width, movie.height), active_bg_color or (0, 0, 0))
        canvas = frame.convert("RGBA")
        draw_ops: list[tuple[int, int, Image.Image, int, int]] = []
        for idx, (track, last) in enumerate(track_states):
            rel = frame_no - track.start_frame
            if 0 <= rel < len(track.deltas):
                last = track.deltas[rel]
                track_states[idx] = (track, last)
            elif rel >= len(track.deltas):
                track_states[idx] = (track, None)
                last = None
            if last is None or rel < 0:
                continue
            actor = movie.actors.get(track.target)
            if actor is None or not actor.cels:
                continue
            xoff, yoff, cel_no, visible = last
            if visible == 0:
                continue
            cel_index = max(0, min(cel_no - 1, len(actor.cels) - 1))
            cel = actor.cels[cel_index]
            x = track.base[0] + xoff - cel.registration[0]
            y = track.base[1] + yoff - cel.registration[1]
            draw_ops.append((track.base[1] + yoff, idx, cel.image, x, y))
        for _, _, image, x, y in sorted(draw_ops, key=lambda item: (item[0], item[1])):
            canvas.alpha_composite(image, (x, y))
        yield canvas.convert("RGB")


def source_frame_delays(movie: Movie) -> dict[int, int]:
    delays: dict[int, int] = {}
    delay = movie.frame_delay
    for frame_no in range(1, movie.frames + 1):
        delay = movie.timing_events.get(frame_no, delay)
        delays[frame_no] = movie.playback_delays.get(frame_no, delay)
    return delays


def wav_duration_ticks(sound: Sound) -> int:
    with wave.open(io.BytesIO(sound.data)) as wav:
        return round((wav.getnframes() * 60) / wav.getframerate())


def playback_runs(movie: Movie, expand_infinite: bool = True) -> list[tuple[int, int]]:
    delays = source_frame_delays(movie)
    loops_by_frame: dict[int, list[LoopEvent]] = {}
    for loop in movie.loops:
        loops_by_frame.setdefault(loop.frame, []).append(loop)

    finite_runs: list[tuple[int, int]] = []
    first_starts: dict[int, int] = {}
    total = 0

    def append_frame(frame_no: int) -> None:
        nonlocal total
        if frame_no not in first_starts:
            first_starts[frame_no] = total
        duration = delays.get(frame_no, movie.frame_delay)
        finite_runs.append((frame_no, duration))
        total += duration

    for frame_no in range(1, movie.frames + 1):
        append_frame(frame_no)
        for loop in loops_by_frame.get(frame_no, []):
            marker_frame = movie.markers.get(loop.marker)
            if marker_frame is None or marker_frame > frame_no:
                continue
            repeat_count = 0 if loop.count >= 65534 else loop.count
            for _ in range(repeat_count):
                for loop_frame in range(marker_frame, frame_no + 1):
                    append_frame(loop_frame)

    target_ticks = total
    for frame_no, name in movie.sound_events:
        sound = movie.sounds.get(name)
        if sound is None or sound.kind != "wav":
            continue
        target_ticks = max(target_ticks, first_starts.get(frame_no, 0) + wav_duration_ticks(sound))

    if not expand_infinite or not any(loop.count >= 65534 for loop in movie.loops):
        return finite_runs

    runs: list[tuple[int, int]] = []
    total = 0
    stopped = False

    def emit(frame_no: int) -> None:
        nonlocal total
        duration = delays.get(frame_no, movie.frame_delay)
        runs.append((frame_no, duration))
        total += duration

    for frame_no in range(1, movie.frames + 1):
        emit(frame_no)
        for loop in loops_by_frame.get(frame_no, []):
            marker_frame = movie.markers.get(loop.marker)
            if marker_frame is None or marker_frame > frame_no:
                continue
            if loop.count >= 65534:
                while total < target_ticks:
                    for loop_frame in range(marker_frame, frame_no + 1):
                        emit(loop_frame)
                        if total >= target_ticks:
                            break
                stopped = True
                break
            for _ in range(loop.count):
                for loop_frame in range(marker_frame, frame_no + 1):
                    emit(loop_frame)
        if stopped:
            break
    return runs


def frame_start_ticks(movie: Movie) -> dict[int, int]:
    ticks: dict[int, int] = {}
    total = 0
    for frame_no, duration in playback_runs(movie):
        ticks.setdefault(frame_no, total)
        total += duration
    return ticks


def write_video_only_avi(movie: Movie, out_path: Path) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise FormatError("ffmpeg is required to write AVI")
    fps = 60.0
    cmd = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{movie.width}x{movie.height}",
        "-r",
        f"{fps:.6f}",
        "-i",
        "-",
        "-an",
        "-f",
        "avi",
        "-c:v",
        "mjpeg",
        "-q:v",
        "3",
        str(out_path),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin is not None
    try:
        try:
            frames = list(render_frames(movie))
            for frame_no, frame_delay in playback_runs(movie):
                raw = frames[frame_no - 1].tobytes()
                for _ in range(frame_delay):
                    proc.stdin.write(raw)
            proc.stdin.close()
        except BrokenPipeError as exc:
            raise FormatError("ffmpeg failed while writing AVI") from exc
        if proc.wait() != 0:
            raise FormatError("ffmpeg failed while writing AVI")
    except Exception:
        proc.kill()
        proc.wait()
        raise


def mux_audio(movie: Movie, video_path: Path, out_path: Path, work_dir: Path) -> None:
    events = [(frame, name) for frame, name in movie.sound_events if name in movie.sounds]
    if not events:
        os.replace(video_path, out_path)
        return

    tick_starts = frame_start_ticks(movie)
    sound_files: list[Path] = []
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(video_path)]
    for index, (frame, name) in enumerate(events):
        sound_path = work_dir / f"sound_{index}.wav"
        sound_path.write_bytes(movie.sounds[name].data)
        sound_files.append(sound_path)
        cmd.extend(["-i", str(sound_path)])

    filters: list[str] = []
    labels: list[str] = []
    for index, (frame, _name) in enumerate(events, start=1):
        delay_ms = round((tick_starts.get(frame, 0) * 1000) / 60)
        label = f"a{index}"
        filters.append(f"[{index}:a]adelay={delay_ms}:all=1[{label}]")
        labels.append(f"[{label}]")
    filters.append("".join(labels) + f"amix=inputs={len(labels)}:duration=longest:normalize=0[aout]")
    cmd.extend([
        "-filter_complex",
        ";".join(filters),
        "-map",
        "0:v:0",
        "-map",
        "[aout]",
        "-c:v",
        "copy",
        "-c:a",
        "pcm_s16le",
        "-f",
        "avi",
        str(out_path),
    ])
    cp = subprocess.run(cmd, text=True, capture_output=True)
    if cp.returncode:
        raise FormatError(f"ffmpeg failed while muxing audio: {cp.stderr.strip()}")


def write_avi_with_ffmpeg(movie: Movie, out_path: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="animationWorks.", dir=str(out_path.parent)) as tmpdir:
        work_dir = Path(tmpdir)
        video_path = work_dir / "video.avi"
        audio_mux_path = work_dir / "muxed.avi"
        write_video_only_avi(movie, video_path)
        mux_audio(movie, video_path, audio_mux_path, work_dir)
        os.replace(audio_mux_path, out_path)


def convert(input_file: Path, output_file: Path) -> None:
    movie = load_movie(input_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=output_file.name + ".", suffix=".tmp", dir=str(output_file.parent))
    os.close(fd)
    tmp_path = Path(tmp_name)
    try:
        tmp_path.unlink(missing_ok=True)
        write_avi_with_ffmpeg(movie, tmp_path)
        os.chmod(tmp_path, 0o664)
        os.replace(tmp_path, output_file)
        os.chmod(output_file, 0o664)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        output_file.unlink(missing_ok=True)
        raise


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Convert Animation Works Movie files to AVI")
    parser.add_argument("inputFile")
    parser.add_argument("outputFile")
    args = parser.parse_args(argv)
    try:
        convert(Path(args.inputFile), Path(args.outputFile))
    except Exception as exc:
        print(f"animationWorks.py: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

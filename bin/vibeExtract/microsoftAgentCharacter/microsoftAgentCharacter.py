#!/usr/bin/env python3
# Vibe coded by Codex
"""Strict Microsoft Agent character extractor.

Usage:
    microsoftAgentCharacter.py <inputFile> <outputDir>

The extractor accepts Microsoft Agent v2 ACS/ACG-style single-file
characters (0xABCDABC3) and ACF core character files (0xABCDABC4).
It parses every byte in supported complete files before writing output.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import wave
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from PIL import Image


ACS_SIGNATURE = 0xABCDABC3
ACF_SIGNATURE = 0xABCDABC4
NO_AUDIO = 0xFFFF


class FormatError(Exception):
    pass


class Reader:
    def __init__(self, data: bytes, base: int = 0, label: str = "data"):
        self.data = data
        self.pos = 0
        self.base = base
        self.label = label

    def tell(self) -> int:
        return self.pos

    def remain(self) -> int:
        return len(self.data) - self.pos

    def require(self, n: int) -> None:
        if n < 0 or self.pos + n > len(self.data):
            raise FormatError(f"{self.label}: need {n} bytes at 0x{self.base + self.pos:x}")

    def read(self, n: int) -> bytes:
        self.require(n)
        out = self.data[self.pos : self.pos + n]
        self.pos += n
        return out

    def u8(self) -> int:
        return self.read(1)[0]

    def bool(self) -> int:
        return self.u8()

    def u16(self) -> int:
        self.require(2)
        v = struct.unpack_from("<H", self.data, self.pos)[0]
        self.pos += 2
        return v

    def i16(self) -> int:
        self.require(2)
        v = struct.unpack_from("<h", self.data, self.pos)[0]
        self.pos += 2
        return v

    def u32(self) -> int:
        self.require(4)
        v = struct.unpack_from("<I", self.data, self.pos)[0]
        self.pos += 4
        return v

    def i32(self) -> int:
        self.require(4)
        v = struct.unpack_from("<i", self.data, self.pos)[0]
        self.pos += 4
        return v

    def guid(self) -> str:
        raw = self.read(16)
        d1, d2, d3 = struct.unpack_from("<IHH", raw, 0)
        d4 = raw[8:]
        return f"{d1:08x}-{d2:04x}-{d3:04x}-{d4[:2].hex()}-{d4[2:].hex()}"

    def eof(self) -> None:
        if self.pos != len(self.data):
            raise FormatError(
                f"{self.label}: {len(self.data) - self.pos} trailing bytes at 0x{self.base + self.pos:x}"
            )


@dataclass
class Coverage:
    size: int
    ranges: list[tuple[int, int, str]] = field(default_factory=list)

    def add(self, start: int, size: int, label: str) -> None:
        if size < 0 or start < 0 or start + size > self.size:
            raise FormatError(f"{label}: range 0x{start:x}+0x{size:x} outside file")
        if size:
            self.ranges.append((start, start + size, label))

    def gaps_and_overlaps(self) -> tuple[list[tuple[int, int]], list[tuple[int, int, str, str]]]:
        gaps: list[tuple[int, int]] = []
        overlaps: list[tuple[int, int, str, str]] = []
        cur = 0
        last_label = ""
        for s, e, label in sorted(self.ranges):
            if s > cur:
                gaps.append((cur, s))
                cur = e
                last_label = label
            elif s < cur:
                overlaps.append((s, min(e, cur), last_label, label))
                if e > cur:
                    cur = e
                    last_label = label
            else:
                cur = e
                last_label = label
        if cur < self.size:
            gaps.append((cur, self.size))
        return gaps, overlaps


class BitReader:
    def __init__(self, data: bytes):
        self.data = data
        self.bitpos = 0

    def bit(self) -> int:
        idx = self.bitpos // 8
        if idx >= len(self.data):
            raise FormatError("compressed stream ended before terminator")
        out = (self.data[idx] >> (self.bitpos & 7)) & 1
        self.bitpos += 1
        return out

    def bits(self, count: int) -> int:
        value = 0
        for i in range(count):
            value |= self.bit() << i
        return value


def decompress_agent(data: bytes, expected_size: int) -> bytes:
    if len(data) < 7:
        raise FormatError("compressed block too short")
    if data[0] != 0:
        raise FormatError("compressed block missing leading 0x00")
    if data[-6:] != b"\xff" * 6:
        raise FormatError("compressed block missing trailing 0xff bytes")
    # The 20-bit end marker may straddle the final 0xff padding bytes, so the
    # sentinel bytes must remain readable by the bit reader.
    br = BitReader(data[1:])
    out = bytearray()
    while True:
        if br.bit() == 0:
            out.append(br.bits(8))
            if len(out) > expected_size:
                raise FormatError("decompressed block exceeds expected size")
            continue

        count = 2
        prefix = 0
        while prefix < 3 and br.bit() == 1:
            prefix += 1
        bit_count = (6, 9, 12, 20)[prefix]
        raw_offset = br.bits(bit_count)
        if bit_count == 20 and raw_offset == 0xFFFFF:
            break
        offset = raw_offset + {6: 1, 9: 65, 12: 577, 20: 4673}[bit_count]
        if bit_count == 20:
            count += 1

        ones = 0
        while ones < 11 and br.bit() == 1:
            ones += 1
        if ones == 11 and br.bit() == 1:
            raise FormatError("invalid compressed count prefix")
        count += (1 << ones) - 1
        count += br.bits(ones) if ones else 0

        if offset <= 0 or offset > len(out):
            raise FormatError("compressed copy offset outside output")
        for _ in range(count):
            out.append(out[-offset])
            if len(out) > expected_size:
                raise FormatError("decompressed block exceeds expected size")
    if len(out) != expected_size:
        raise FormatError(f"decompressed size {len(out)} != expected {expected_size}")
    return bytes(out)


def read_string(r: Reader, acs: bool) -> str:
    count = r.u32()
    if count == 0:
        return ""
    byte_count = count * 2
    raw = r.read(byte_count)
    if acs:
        term = r.read(2)
        if term != b"\x00\x00":
            raise FormatError(f"{r.label}: unterminated ACS string at 0x{r.base + r.pos - 2:x}")
    return raw.decode("utf-16le")


def read_string_list(r: Reader, acs: bool) -> list[str]:
    return [read_string(r, acs) for _ in range(r.u16())]


def read_datablock(r: Reader) -> bytes:
    size = r.u32()
    return r.read(size)


def read_compressed_block(r: Reader, compressed_first: bool = True) -> tuple[bytes, dict[str, int]]:
    first = r.u32()
    second = r.u32()
    if compressed_first:
        compressed_size, uncompressed_size = first, second
    else:
        uncompressed_size, compressed_size = first, second
    if compressed_size == 0:
        data = r.read(uncompressed_size)
        return data, {"uncompressed_size": uncompressed_size, "compressed_size": 0}
    raw = r.read(compressed_size)
    return decompress_agent(raw, uncompressed_size), {
        "uncompressed_size": uncompressed_size,
        "compressed_size": compressed_size,
    }


def parse_rgbquad(r: Reader) -> list[int]:
    return [r.u8(), r.u8(), r.u8(), r.u8()]


def parse_voice(r: Reader, acs: bool) -> dict[str, Any]:
    out: dict[str, Any] = {
        "tts_engine_id": r.guid(),
        "tts_mode_id": r.guid(),
        "speed": r.u32(),
        "pitch": r.u16(),
        "extra_data_present": r.bool(),
    }
    if out["extra_data_present"]:
        out.update(
            {
                "language_id": r.u16(),
                "language_dialect": read_string(r, acs),
                "gender": r.u16(),
                "age": r.u16(),
                "style": read_string(r, acs),
            }
        )
    return out


def parse_balloon(r: Reader, acs: bool) -> dict[str, Any]:
    return {
        "text_lines": r.u8(),
        "characters_per_line": r.u8(),
        "foreground_rgba": parse_rgbquad(r),
        "background_rgba": parse_rgbquad(r),
        "border_rgba": parse_rgbquad(r),
        "font_name": read_string(r, acs),
        "font_height": r.i32(),
        "font_weight": r.i32(),
        "italicized": r.bool(),
        "unknown": r.u8(),
    }


def parse_tray_icon(r: Reader) -> dict[str, Any]:
    mono_size = r.u32()
    mono = r.read(mono_size)
    color_size = r.u32()
    color = r.read(color_size)
    return {
        "monochrome_size": mono_size,
        "monochrome_sha256": sha256_hex(mono),
        "color_size": color_size,
        "color_sha256": sha256_hex(color),
        "_mono": mono,
        "_color": color,
    }


def parse_states(r: Reader, acs: bool) -> list[dict[str, Any]]:
    states = []
    for _ in range(r.u16()):
        states.append({"name": read_string(r, acs), "animations": read_string_list(r, acs)})
    return states


def parse_localized_list(r: Reader, acs: bool) -> list[dict[str, Any]]:
    out = []
    for _ in range(r.u16()):
        out.append(
            {
                "language_id": r.u16(),
                "name": read_string(r, acs),
                "description": read_string(r, acs),
                "extra_data": read_string(r, acs),
            }
        )
    return out


def parse_character_common(r: Reader, acs: bool, localized_inline: bool) -> dict[str, Any]:
    minor = r.u16()
    major = r.u16()
    out: dict[str, Any] = {"minor_version": minor, "major_version": major}
    if localized_inline:
        out["animations"] = parse_acf_animation_refs(r)
    else:
        out["localized_locator"] = read_locator(r)
    out["guid"] = r.guid()
    if localized_inline:
        out["localized_info"] = parse_localized_list(r, acs=False)
    out.update(
        {
            "width": r.u16(),
            "height": r.u16(),
            "transparent_color_index": r.u8(),
            "flags": r.u32(),
            "animation_set_major_version": r.u16(),
            "animation_set_minor_version": r.u16(),
        }
    )
    if out["flags"] & 0x20:
        out["voice_info"] = parse_voice(r, acs)
    if out["flags"] & 0x200:
        out["balloon_info"] = parse_balloon(r, acs)
    palette_count = r.u32()
    out["palette"] = [parse_rgbquad(r) for _ in range(palette_count)]
    out["tray_icon_enabled"] = r.bool()
    if out["tray_icon_enabled"]:
        out["tray_icon"] = parse_tray_icon(r)
    out["states"] = parse_states(r, acs)
    return out


def read_locator(r: Reader) -> dict[str, int]:
    return {"offset": r.u32(), "size": r.u32()}


def sha256_hex(data: bytes) -> str:
    import hashlib

    return hashlib.sha256(data).hexdigest()


def safe_name(name: str, fallback: str) -> str:
    name = name.strip() or fallback
    name = re.sub(r"[^\w .()-]+", "_", name, flags=re.UNICODE)
    name = name.strip(" .")
    return name[:96] or fallback


def dib_stride(width: int) -> int:
    return (width + 3) & 0xFFFFFFFC


def parse_branch_list(r: Reader) -> list[dict[str, int]]:
    return [{"frame_index": r.u16(), "probability_percent": r.u16()} for _ in range(r.u8())]


def parse_acs_overlays(r: Reader, overlay_has_replace: bool) -> list[dict[str, Any]]:
    out = []
    for _ in range(r.u8()):
        item: dict[str, Any] = {
            "overlay_type": r.u8(),
        }
        if overlay_has_replace:
            item["replace_top_image"] = r.bool()
        else:
            item["replace_top_image"] = None
        item.update(
            {
                "image_index": r.u16(),
                "unknown": r.u8(),
                "region_data_present": r.bool(),
                "x": r.i16(),
                "y": r.i16(),
                "width_half": r.u16(),
                "height_half": r.u16(),
            }
        )
        if item["region_data_present"]:
            item["region_data"] = read_datablock(r)
            item["region_sha256"] = sha256_hex(item["region_data"])
            item["region_size"] = len(item["region_data"])
        out.append(item)
    return out


def parse_acs_frame(r: Reader, overlay_has_replace: bool) -> dict[str, Any]:
    images = []
    for _ in range(r.u16()):
        images.append({"image_index": r.u32(), "x": r.i16(), "y": r.i16()})
    return {
        "images": images,
        "audio_index": r.u16(),
        "duration_centiseconds": r.u16(),
        "exit_frame_index": r.i16(),
        "branches": parse_branch_list(r),
        "overlays": parse_acs_overlays(r, overlay_has_replace),
    }


def parse_acs_animation_info(r: Reader, overlay_has_replace: bool) -> dict[str, Any]:
    name = read_string(r, acs=True)
    transition = r.u8()
    ret = read_string(r, acs=True)
    frames = [parse_acs_frame(r, overlay_has_replace) for _ in range(r.u16())]
    return {"name": name, "transition_type": transition, "return_animation": ret, "frames": frames}


def parse_acs_animation_list(r: Reader) -> list[dict[str, Any]]:
    out = []
    for _ in range(r.u32()):
        out.append({"name": read_string(r, acs=True), "locator": read_locator(r)})
    return out


def parse_acs_image_list(r: Reader) -> list[dict[str, Any]]:
    return [{"locator": read_locator(r), "checksum": r.u32()} for _ in range(r.u32())]


def parse_acs_audio_list(r: Reader) -> list[dict[str, Any]]:
    return [{"locator": read_locator(r), "checksum": r.u32()} for _ in range(r.u32())]


def parse_image_info(r: Reader) -> dict[str, Any]:
    if len(r.data) == 1:
        marker = r.u8()
        if marker != 0:
            raise FormatError(f"{r.label}: unknown one-byte image marker 0x{marker:02x}")
        return {
            "empty": True,
            "unknown": marker,
            "width": 0,
            "height": 0,
            "compressed": False,
            "image_block_size": 0,
            "image_data": b"",
            "image_sha256": sha256_hex(b""),
            "region_data": b"",
            "region_sha256": sha256_hex(b""),
            "region": {"compressed_size": 0, "uncompressed_size": 0},
        }
    unknown = r.u8()
    width = r.u16()
    height = r.u16()
    compressed = r.bool()
    raw_block = read_datablock(r)
    expected = dib_stride(width) * height
    image_data = decompress_agent(raw_block, expected) if compressed else raw_block
    if len(image_data) != expected:
        raise FormatError(f"image data size {len(image_data)} != expected {expected}")
    region_data, region_sizes = read_compressed_block(r, compressed_first=True)
    return {
        "unknown": unknown,
        "width": width,
        "height": height,
        "compressed": compressed,
        "image_block_size": len(raw_block),
        "image_data": image_data,
        "image_sha256": sha256_hex(image_data),
        "region_data": region_data,
        "region_sha256": sha256_hex(region_data),
        "region": region_sizes,
    }


def validate_locator(loc: dict[str, int], total: int, label: str) -> None:
    off = loc["offset"]
    size = loc["size"]
    if off + size > total:
        raise FormatError(f"{label}: locator 0x{off:x}+0x{size:x} outside file size 0x{total:x}")


def slice_at(data: bytes, loc: dict[str, int], label: str, cov: Coverage) -> Reader:
    validate_locator(loc, len(data), label)
    cov.add(loc["offset"], loc["size"], label)
    return Reader(data[loc["offset"] : loc["offset"] + loc["size"]], loc["offset"], label)


def parse_acs(data: bytes) -> dict[str, Any]:
    cov = Coverage(len(data))
    r = Reader(data, 0, "ACSHEADER")
    sig = r.u32()
    if sig != ACS_SIGNATURE:
        raise FormatError("not an ACS/ACG Microsoft Agent v2 file")
    locs = {
        "character": read_locator(r),
        "animations": read_locator(r),
        "images": read_locator(r),
        "audio": read_locator(r),
    }
    cov.add(0, r.tell(), "ACSHEADER")
    for key, loc in locs.items():
        validate_locator(loc, len(data), key)

    cr = slice_at(data, locs["character"], "ACSCHARACTERINFO", cov)
    character = parse_character_common(cr, acs=True, localized_inline=False)
    localized_locator = character["localized_locator"]
    expected_localized_offset = locs["character"]["offset"] + cr.tell()
    if localized_locator["offset"] != expected_localized_offset:
        raise FormatError(
            "LOCALIZEDINFO does not immediately follow ACS character core "
            f"(got 0x{localized_locator['offset']:x}, expected 0x{expected_localized_offset:x})"
        )
    if localized_locator["size"] != cr.remain():
        raise FormatError(
            f"LOCALIZEDINFO size {localized_locator['size']} does not match remaining character bytes {cr.remain()}"
        )
    lr = Reader(
        data[localized_locator["offset"] : localized_locator["offset"] + localized_locator["size"]],
        localized_locator["offset"],
        "LOCALIZEDINFO",
    )
    character["localized_info"] = parse_localized_list(lr, acs=True)
    lr.eof()
    cr.pos += localized_locator["size"]
    cr.eof()

    ar = slice_at(data, locs["animations"], "ACSANIMATIONINFO_LIST", cov)
    animations = parse_acs_animation_list(ar)
    ar.eof()
    for i, anim in enumerate(animations):
        rr = slice_at(data, anim["locator"], f"animation[{i}]", cov)
        anim["info"] = parse_acs_animation_info(rr, overlay_has_replace=character["major_version"] >= 2)
        rr.eof()

    ir = slice_at(data, locs["images"], "ACSIMAGEINFO_LIST", cov)
    images = parse_acs_image_list(ir)
    ir.eof()
    for i, img in enumerate(images):
        rr = slice_at(data, img["locator"], f"image[{i}]", cov)
        info = parse_image_info(rr)
        rr.eof()
        img["info"] = info

    aur = slice_at(data, locs["audio"], "ACSAUDIOINFO_LIST", cov)
    audio = parse_acs_audio_list(aur)
    aur.eof()
    for i, aud in enumerate(audio):
        loc = aud["locator"]
        validate_locator(loc, len(data), f"audio[{i}]")
        cov.add(loc["offset"], loc["size"], f"audio[{i}]")
        blob = data[loc["offset"] : loc["offset"] + loc["size"]]
        if blob and not (blob.startswith(b"RIFF") and blob[8:12] == b"WAVE"):
            raise FormatError(f"audio[{i}] is not RIFF WAVE")
        aud["data"] = blob
        aud["size"] = len(blob)
        aud["sha256"] = sha256_hex(blob)

    gaps, overlaps = cov.gaps_and_overlaps()
    if gaps:
        desc = ", ".join(f"0x{s:x}-0x{e:x}" for s, e in gaps[:8])
        raise FormatError(f"unaccounted file bytes: {desc}")
    if overlaps:
        desc = ", ".join(f"0x{s:x}-0x{e:x}" for s, e, _, _ in overlaps[:8])
        raise FormatError(f"overlapping file byte ownership: {desc}")

    return {
        "format": "ACS",
        "locators": locs,
        "character": character,
        "animations": animations,
        "images": images,
        "audio": audio,
        "coverage_ranges": len(cov.ranges),
    }


def parse_acf_animation_refs(r: Reader) -> list[dict[str, Any]]:
    out = []
    for _ in range(r.u16()):
        out.append(
            {
                "name": read_string(r, acs=False),
                "aca_filename": read_string(r, acs=False),
                "return_animation": read_string(r, acs=False),
                "aca_checksum": r.u32(),
            }
        )
    return out


def parse_acf(data: bytes) -> dict[str, Any]:
    r = Reader(data, 0, "ACFHEADER")
    sig = r.u32()
    if sig != ACF_SIGNATURE:
        raise FormatError("not an ACF Microsoft Agent v2 file")
    character_data, compressed = read_compressed_block(r, compressed_first=False)
    r.eof()
    cr = Reader(character_data, 0, "ACFCHARACTERINFO")
    character = parse_character_common(cr, acs=False, localized_inline=True)
    cr.eof()
    return {
        "format": "ACF",
        "compressed_character_data": compressed,
        "character": character,
        "coverage_ranges": 1,
    }


def strip_binary(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: strip_binary(v) for k, v in obj.items() if not k.startswith("_") and k not in {"data", "image_data", "region_data"}}
    if isinstance(obj, list):
        return [strip_binary(v) for v in obj]
    if isinstance(obj, bytes):
        return {"size": len(obj), "sha256": sha256_hex(obj)}
    return obj


def palette_for_pil(palette: list[list[int]]) -> list[int]:
    out: list[int] = []
    for rgba in palette[:256]:
        out.extend(rgba[:3])
    out.extend([0] * (768 - len(out)))
    return out[:768]


def indexed_to_rgba(image_info: dict[str, Any], palette: list[list[int]], transparent_index: int) -> Image.Image:
    w = image_info["width"]
    h = image_info["height"]
    stride = dib_stride(w)
    raw = image_info["image_data"]
    pixels = bytearray()
    for row in range(h):
        src_y = h - 1 - row
        pixels.extend(raw[src_y * stride : src_y * stride + w])
    img = Image.frombytes("P", (w, h), bytes(pixels))
    img.putpalette(palette_for_pil(palette))
    rgba = img.convert("RGBA")
    if 0 <= transparent_index < len(palette):
        alpha = bytes(0 if p == transparent_index else 255 for p in pixels)
        rgba.putalpha(Image.frombytes("L", (w, h), alpha))
    return rgba


def save_bmp(path: Path, image_info: dict[str, Any], palette: list[list[int]]) -> None:
    img = indexed_to_rgba(image_info, palette, -1)
    img.save(path)


def render_frame(parsed: dict[str, Any], frame: dict[str, Any]) -> Image.Image:
    char = parsed["character"]
    palette = char["palette"]
    transparent = char["transparent_color_index"]
    canvas = Image.new("RGBA", (char["width"], char["height"]), (0, 0, 0, 0))
    for ref in reversed(frame["images"]):
        idx = ref["image_index"]
        if idx >= len(parsed["images"]):
            raise FormatError(f"frame references image {idx}, but only {len(parsed['images'])} images exist")
        if parsed["images"][idx]["info"].get("empty"):
            continue
        layer = indexed_to_rgba(parsed["images"][idx]["info"], palette, transparent)
        canvas.alpha_composite(layer, (ref["x"], ref["y"]))
    return canvas


def write_wav_timeline(path: Path, parsed: dict[str, Any], frames: list[dict[str, Any]]) -> Optional[Path]:
    # Only create a Python-mixed PCM timeline when all referenced WAVs are PCM
    # with identical parameters. ffmpeg rendering still includes non-PCM clips
    # directly using filter inputs.
    params = None
    timeline = bytearray()
    used = False
    for frame in frames:
        duration = frame["duration_centiseconds"] / 100.0
        idx = frame["audio_index"]
        clip = None
        if idx != NO_AUDIO and idx < len(parsed["audio"]):
            clip = parsed["audio"][idx]["data"]
        if clip:
            try:
                with wave.open(str(write_temp_bytes(path.parent, f"_clip_{idx}.wav", clip)), "rb") as w:
                    if w.getcomptype() != "NONE":
                        return None
                    current = (w.getnchannels(), w.getsampwidth(), w.getframerate())
                    if params is None:
                        params = current
                    if current != params:
                        return None
                    frames_bytes = w.readframes(w.getnframes())
            except Exception:
                return None
            used = True
        if params is None:
            continue
        need_bytes = int(round(duration * params[2])) * params[0] * params[1]
        if clip:
            timeline.extend(frames_bytes[:need_bytes])
            if len(frames_bytes) < need_bytes:
                timeline.extend(b"\x00" * (need_bytes - len(frames_bytes)))
        else:
            timeline.extend(b"\x00" * need_bytes)
    if not used or params is None:
        return None
    with wave.open(str(path), "wb") as out:
        out.setnchannels(params[0])
        out.setsampwidth(params[1])
        out.setframerate(params[2])
        out.writeframes(bytes(timeline))
    return path


def write_temp_bytes(directory: Path, name: str, data: bytes) -> Path:
    path = directory / name
    path.write_bytes(data)
    return path


def run_ffmpeg(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        raise FormatError(f"ffmpeg failed: {proc.stderr[-2000:]}")


def run_video_only_ffmpeg(concat: Path, path: Path) -> None:
    run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat),
            "-c:v",
            "png",
            "-pix_fmt",
            "rgba",
            str(path),
        ]
    )


def render_animation_avi(parsed: dict[str, Any], anim: dict[str, Any], path: Path, work: Path) -> None:
    frames = anim["info"]["frames"]
    frame_dir = work / f"frames_{safe_name(anim['name'], 'animation')}"
    frame_dir.mkdir(parents=True, exist_ok=True)
    concat = frame_dir / "frames.txt"
    lines = []
    if not frames:
        char = parsed["character"]
        img_path = frame_dir / "frame_0000.png"
        Image.new("RGBA", (char["width"], char["height"]), (0, 0, 0, 0)).save(img_path)
        lines.append(f"file '{img_path.resolve().as_posix()}'\n")
        lines.append("duration 0.10\n")
        lines.append(f"file '{img_path.resolve().as_posix()}'\n")
        concat.write_text("".join(lines), encoding="utf-8")
        run_video_only_ffmpeg(concat, path)
        path.with_suffix(".render_warning.txt").write_text(
            "Animation contains no frames; rendered as a transparent placeholder AVI.\n",
            encoding="utf-8",
        )
        return
    for i, frame in enumerate(frames):
        img_path = frame_dir / f"frame_{i:04d}.png"
        render_frame(parsed, frame).save(img_path)
        duration = max(frame["duration_centiseconds"], 1) / 100.0
        lines.append(f"file '{img_path.resolve().as_posix()}'\n")
        lines.append(f"duration {duration:.2f}\n")
    lines.append(f"file '{(frame_dir / f'frame_{len(frames)-1:04d}.png').resolve().as_posix()}'\n")
    concat.write_text("".join(lines), encoding="utf-8")

    total_duration = sum(max(frame["duration_centiseconds"], 1) for frame in frames) / 100.0
    wav_path = write_wav_timeline(frame_dir / "timeline.wav", parsed, frames)
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(concat)]
    has_audio = False
    if wav_path:
        cmd += ["-i", str(wav_path), "-shortest"]
        has_audio = True
    else:
        delayed_inputs = []
        elapsed_ms = 0
        for frame_no, frame in enumerate(frames):
            idx = frame["audio_index"]
            if idx != NO_AUDIO and idx < len(parsed["audio"]) and parsed["audio"][idx]["data"]:
                clip_path = write_temp_bytes(frame_dir, f"audio_{frame_no:04d}_{idx:04d}.wav", parsed["audio"][idx]["data"])
                delayed_inputs.append((clip_path, elapsed_ms))
            elapsed_ms += max(frame["duration_centiseconds"], 1) * 10
        if delayed_inputs:
            cmd += ["-f", "lavfi", "-t", f"{total_duration:.2f}", "-i", "anullsrc=r=22050:cl=mono"]
            for clip_path, _ in delayed_inputs:
                cmd += ["-i", str(clip_path)]
            filters = []
            labels = ["[1:a]"]
            for i, (_, delay_ms) in enumerate(delayed_inputs):
                input_index = i + 2
                filters.append(f"[{input_index}:a]adelay={delay_ms}|{delay_ms}[a{i}]")
                labels.append(f"[a{i}]")
            filters.append("".join(labels) + f"amix=inputs={len(labels)}:duration=first[aout]")
            cmd += ["-filter_complex", ";".join(filters), "-map", "0:v", "-map", "[aout]", "-shortest"]
            has_audio = True
    cmd += ["-c:v", "png", "-pix_fmt", "rgba"]
    if has_audio:
        cmd += ["-c:a", "pcm_s16le"]
    cmd += [str(path)]
    try:
        run_ffmpeg(cmd)
    except FormatError as exc:
        if not has_audio:
            raise
        run_video_only_ffmpeg(concat, path)
        path.with_suffix(".render_warning.txt").write_text(
            f"Audio could not be muxed into this AVI; rendered silent video fallback.\n{exc}\n",
            encoding="utf-8",
        )


def write_outputs(parsed: dict[str, Any], outdir: Path, render_avi: bool = True) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "metadata.json").write_text(json.dumps(strip_binary(parsed), indent=2), encoding="utf-8")
    char = parsed["character"]
    if parsed["format"] == "ACS":
        images_dir = outdir / "images"
        images_dir.mkdir()
        for i, img in enumerate(parsed["images"]):
            info = img["info"]
            stem = f"image_{i:04d}"
            (images_dir / f"{stem}.raw").write_bytes(info["image_data"])
            (images_dir / f"{stem}.region").write_bytes(info["region_data"])
            if not info.get("empty"):
                indexed_to_rgba(info, char["palette"], char["transparent_color_index"]).save(images_dir / f"{stem}.png")

        audio_dir = outdir / "audio"
        audio_dir.mkdir()
        for i, aud in enumerate(parsed["audio"]):
            if aud["data"]:
                (audio_dir / f"audio_{i:04d}.wav").write_bytes(aud["data"])

        anim_dir = outdir / "animations"
        anim_dir.mkdir()
        work = outdir / "_render_work"
        work.mkdir()
        for i, anim in enumerate(parsed["animations"]):
            name = safe_name(anim["name"], f"animation_{i:04d}")
            (anim_dir / f"{i:04d}_{name}.json").write_text(
                json.dumps(strip_binary(anim), indent=2), encoding="utf-8"
            )
            if render_avi:
                render_animation_avi(parsed, anim, anim_dir / f"{i:04d}_{name}.avi", work)
        shutil.rmtree(work)

    tray = char.get("tray_icon")
    if tray:
        tray_dir = outdir / "tray_icon"
        tray_dir.mkdir()
        (tray_dir / "monochrome.iconimage").write_bytes(tray["_mono"])
        (tray_dir / "color.iconimage").write_bytes(tray["_color"])


def parse_file(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    if len(data) < 4:
        raise FormatError("file too small")
    sig = struct.unpack_from("<I", data, 0)[0]
    if sig == ACS_SIGNATURE:
        return parse_acs(data)
    if sig == ACF_SIGNATURE:
        return parse_acf(data)
    raise FormatError(f"unknown signature 0x{sig:08x}")


def extract(input_file: Path, output_dir: Path) -> None:
    if output_dir.exists() and not output_dir.is_dir():
        raise FormatError(f"output path exists and is not a directory: {output_dir}")
    parsed = parse_file(input_file)
    parent = output_dir.parent if output_dir.parent != Path("") else Path(".")
    tmp = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.tmp.", dir=str(parent)))
    try:
        write_outputs(parsed, tmp)
        if output_dir.exists():
            for item in tmp.iterdir():
                target = output_dir / item.name
                if target.exists():
                    if target.is_dir():
                        shutil.rmtree(target)
                    else:
                        target.unlink()
                os.replace(item, target)
            shutil.rmtree(tmp)
        else:
            os.replace(tmp, output_dir)
    except Exception:
        shutil.rmtree(tmp, ignore_errors=True)
        raise


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Extract Microsoft Agent character files")
    ap.add_argument("inputFile", type=Path)
    ap.add_argument("outputDir", type=Path)
    args = ap.parse_args(argv)
    try:
        extract(args.inputFile, args.outputDir)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

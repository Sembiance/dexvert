#!/usr/bin/env python3
# Vibe coded by Codex
"""Extract CD-i Real Time File sector streams to inspectable resources."""

from __future__ import annotations

import argparse
import binascii
import hashlib
import json
import os
import shutil
import struct
import sys
import tempfile
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SYNC = bytes.fromhex("00ffffffffffffffffffff00")
SUBMODE_EOR = 0x01
SUBMODE_VIDEO = 0x02
SUBMODE_AUDIO = 0x04
SUBMODE_DATA = 0x08
SUBMODE_TRIGGER = 0x10
SUBMODE_FORM2 = 0x20
SUBMODE_REALTIME = 0x40
SUBMODE_EOF = 0x80

CODING_NAMES = {
    0x0: "clut4",
    0x1: "clut7",
    0x2: "clut8",
    0x3: "rl3",
    0x4: "rl7",
    0x5: "dyuv",
    0x6: "rgb555_lower",
    0x7: "rgb555_upper",
    0x8: "qhy",
}

DYUV_DELTAS = (0, 1, 4, 9, 16, 27, 44, 79, 128, 177, 212, 229, 240, 247, 252, 255)
MIN_INFERRED_PARTIAL_HEIGHT = 64


class RTFError(Exception):
    """Raised when an input is not a supported CD-i RTF sector stream."""


@dataclass(frozen=True)
class Sector:
    index: int
    offset: int
    raw: bytes
    file_number: int
    channel_number: int
    submode: int
    coding_info: int
    form2: bool
    user_data: bytes
    edc_stored: int
    edc_computed: int
    edc_status: str
    ecc_sha256: str | None
    msf: tuple[int, int, int] | None

    @property
    def is_data(self) -> bool:
        return bool(self.submode & SUBMODE_DATA)

    @property
    def is_video(self) -> bool:
        return bool(self.submode & SUBMODE_VIDEO)

    @property
    def is_audio(self) -> bool:
        return bool(self.submode & SUBMODE_AUDIO)


@dataclass
class Palette:
    resource_id: str
    sector_index: int
    file_number: int
    channel_number: int
    start_index: int
    entry_count: int
    entries: list[tuple[int, int, int]]
    png_path: str = ""


@dataclass
class VideoRun:
    sectors: list[Sector]
    palette: Palette | None


def build_edc_table() -> tuple[int, ...]:
    table: list[int] = []
    for value in range(256):
        edc = value
        for _ in range(8):
            if edc & 1:
                edc = (edc >> 1) ^ 0xD8018001
            else:
                edc >>= 1
        table.append(edc & 0xFFFFFFFF)
    return tuple(table)


EDC_TABLE = build_edc_table()


def cd_edc(data: bytes) -> int:
    edc = 0
    for byte in data:
        edc = ((edc >> 8) ^ EDC_TABLE[(edc ^ byte) & 0xFF]) & 0xFFFFFFFF
    return edc


def bcd_to_int(value: int) -> int:
    hi = value >> 4
    lo = value & 0x0F
    if hi > 9 or lo > 9:
        raise RTFError(f"invalid BCD value 0x{value:02x}")
    return hi * 10 + lo


def msf_to_frame(msf: tuple[int, int, int]) -> int:
    minute, second, frame = msf
    if second >= 60 or frame >= 75:
        raise RTFError(f"invalid MSF value {minute:02d}:{second:02d}:{frame:02d}")
    return (minute * 60 + second) * 75 + frame


def detect_layout(data: bytes) -> tuple[str, int, int]:
    if len(data) >= 2352 and len(data) % 2352 == 0:
        ok = True
        for offset in range(0, len(data), 2352):
            if data[offset : offset + 12] != SYNC or data[offset + 15] != 0x02:
                ok = False
                break
        if ok:
            return "raw2352", 2352, 16

    if len(data) >= 2336 and len(data) % 2336 == 0:
        ok = True
        for offset in range(0, len(data), 2336):
            if data[offset : offset + 4] != data[offset + 4 : offset + 8]:
                ok = False
                break
        if ok:
            return "stripped2336", 2336, 0

    raise RTFError(
        "unsupported layout: expected raw 2352-byte Mode 2 sectors or stripped 2336-byte Mode 2 sector data"
    )


def parse_sectors(data: bytes) -> tuple[str, list[Sector]]:
    layout, stride, subheader_offset = detect_layout(data)
    sectors: list[Sector] = []
    first_frame: int | None = None

    for index, offset in enumerate(range(0, len(data), stride)):
        sector = data[offset : offset + stride]
        msf: tuple[int, int, int] | None = None
        if layout == "raw2352":
            try:
                msf = (
                    bcd_to_int(sector[12]),
                    bcd_to_int(sector[13]),
                    bcd_to_int(sector[14]),
                )
            except RTFError as exc:
                raise RTFError(f"sector {index}: {exc}") from exc
            frame = msf_to_frame(msf)
            if first_frame is None:
                first_frame = frame
            elif frame != first_frame + index:
                raise RTFError(f"sector {index}: raw sector MSF is not consecutive")

        subheader = sector[subheader_offset : subheader_offset + 8]
        if subheader[:4] != subheader[4:]:
            raise RTFError(f"sector {index}: duplicated subheader copy does not match")

        file_number, channel_number, submode, coding_info = subheader[:4]
        type_bits = submode & (SUBMODE_VIDEO | SUBMODE_AUDIO | SUBMODE_DATA)
        if type_bits and type_bits & (type_bits - 1):
            raise RTFError(f"sector {index}: multiple sector type bits are set")
        if submode & SUBMODE_DATA and submode & SUBMODE_FORM2:
            raise RTFError(f"sector {index}: data sectors must be Form 1")
        if submode & SUBMODE_AUDIO:
            raise RTFError(f"sector {index}: ADPCM audio sectors are not implemented")
        if submode & SUBMODE_VIDEO and not (submode & SUBMODE_FORM2):
            raise RTFError(f"sector {index}: video sectors must be Form 2")
        if submode & SUBMODE_DATA and coding_info != 0:
            raise RTFError(f"sector {index}: data sectors must use coding information 0")

        form2 = bool(submode & SUBMODE_FORM2)
        user_start = subheader_offset + 8
        user_size = 2324 if form2 else 2048
        edc_offset = user_start + user_size
        if edc_offset + 4 > len(sector):
            raise RTFError(f"sector {index}: sector is truncated before EDC")

        user_data = sector[user_start:edc_offset]
        edc_stored = int.from_bytes(sector[edc_offset : edc_offset + 4], "little")
        edc_span_start = subheader_offset
        edc_computed = cd_edc(sector[edc_span_start:edc_offset])
        if form2 and edc_stored == 0 and layout == "raw2352":
            edc_status = "form2_zero_edc"
        elif edc_stored == edc_computed:
            edc_status = "ok"
        else:
            raise RTFError(
                f"sector {index}: EDC mismatch, stored 0x{edc_stored:08x}, computed 0x{edc_computed:08x}"
            )

        ecc = None
        if not form2:
            ecc = hashlib.sha256(sector[edc_offset + 4 :]).hexdigest()

        sectors.append(
            Sector(
                index=index,
                offset=offset,
                raw=sector,
                file_number=file_number,
                channel_number=channel_number,
                submode=submode,
                coding_info=coding_info,
                form2=form2,
                user_data=user_data,
                edc_stored=edc_stored,
                edc_computed=edc_computed,
                edc_status=edc_status,
                ecc_sha256=ecc,
                msf=msf,
            )
        )

    if sectors and not (sectors[-1].submode & SUBMODE_EOF):
        raise RTFError("last sector is not marked EOF")
    if sectors and (sectors[-1].submode & SUBMODE_REALTIME) and not (sectors[-1].submode & SUBMODE_EOR):
        raise RTFError("final real-time record is not marked EOR")

    return layout, sectors


def parse_palette(payload: bytes) -> tuple[int, int, list[tuple[int, int, int]]] | None:
    if len(payload) != 2048:
        return None
    start = int.from_bytes(payload[0:2], "big")
    count = int.from_bytes(payload[2:4], "big")
    end = 4 + count * 3
    if count <= 0 or start >= 256 or start + count > 256 or end > len(payload):
        return None
    if any(payload[end:]):
        return None
    entries = [(0, 0, 0)] * 256
    pos = 4
    for palette_index in range(start, start + count):
        entries[palette_index] = tuple(payload[pos : pos + 3])  # type: ignore[assignment]
        pos += 3
    return start, count, entries


def submode_flags(submode: int) -> list[str]:
    names = [
        (SUBMODE_EOF, "EOF"),
        (SUBMODE_REALTIME, "RT"),
        (SUBMODE_FORM2, "FORM2"),
        (SUBMODE_TRIGGER, "TRIGGER"),
        (SUBMODE_DATA, "DATA"),
        (SUBMODE_AUDIO, "AUDIO"),
        (SUBMODE_VIDEO, "VIDEO"),
        (SUBMODE_EOR, "EOR"),
    ]
    return [name for bit, name in names if submode & bit]


def video_coding_parts(coding_info: int) -> dict[str, object]:
    return {
        "application_specific": bool(coding_info & 0x80),
        "even_odd_lines": "odd" if (coding_info & 0x40) else "even_or_unsplit",
        "resolution": (coding_info >> 4) & 0x03,
        "coding": coding_info & 0x0F,
        "coding_name": CODING_NAMES.get(coding_info & 0x0F, "reserved"),
    }


def is_video_run_compatible(run: VideoRun, sector: Sector) -> bool:
    if not run.sectors:
        return True
    first = run.sectors[0]
    return (
        sector.file_number == first.file_number
        and sector.channel_number == first.channel_number
        and sector.coding_info == first.coding_info
    )


def collect_runs(sectors: list[Sector]) -> tuple[list[Palette], list[VideoRun], list[dict[str, object]]]:
    palettes: list[Palette] = []
    video_runs: list[VideoRun] = []
    data_resources: list[dict[str, object]] = []
    active_palette_by_file: dict[int, Palette] = {}
    current_run: VideoRun | None = None

    def finish_run() -> None:
        nonlocal current_run
        if current_run and current_run.sectors:
            video_runs.append(current_run)
        current_run = None

    for sector in sectors:
        if sector.is_video:
            if current_run is None or not is_video_run_compatible(current_run, sector):
                finish_run()
                current_run = VideoRun(
                    sectors=[],
                    palette=active_palette_by_file.get(sector.file_number),
                )
            current_run.sectors.append(sector)
            if sector.submode & (SUBMODE_EOR | SUBMODE_EOF):
                finish_run()
            continue

        finish_run()

        if sector.is_data:
            parsed_palette = parse_palette(sector.user_data)
            if parsed_palette:
                start, count, entries = parsed_palette
                palette = Palette(
                    resource_id=f"resource_{len(palettes):03d}_palette",
                    sector_index=sector.index,
                    file_number=sector.file_number,
                    channel_number=sector.channel_number,
                    start_index=start,
                    entry_count=count,
                    entries=entries,
                )
                palettes.append(palette)
                active_palette_by_file[sector.file_number] = palette
            else:
                data_resources.append(
                    {
                        "sector": sector.index,
                        "file_number": sector.file_number,
                        "channel_number": sector.channel_number,
                        "size": len(sector.user_data),
                        "sha256": hashlib.sha256(sector.user_data).hexdigest(),
                    }
                )
        elif sector.submode & (SUBMODE_AUDIO | SUBMODE_VIDEO | SUBMODE_DATA):
            raise RTFError(f"sector {sector.index}: unsupported sector type")

    finish_run()
    return palettes, video_runs, data_resources


def all_zero(data: bytes) -> bool:
    return not any(data)


def determine_dimensions(coding: int, resolution: int, payload: bytes) -> tuple[int, int, int, int]:
    if resolution != 0:
        raise RTFError(f"unsupported video resolution code {resolution}")
    if coding not in (0x1, 0x2, 0x5):
        raise RTFError(f"unsupported video coding {coding} ({CODING_NAMES.get(coding, 'reserved')})")

    # Normal-resolution CD-i on-disc full-screen dimensions.
    standard_sizes = [(384, 280), (384, 240), (360, 240)]
    candidates: list[tuple[int, int, int, int]] = []
    for width, height in standard_sizes:
        image_size = width * height
        padding = len(payload) - image_size
        if 0 <= padding < 2324 and all_zero(payload[image_size:]):
            candidates.append((width, height, image_size, padding))
    if candidates:
        return max(candidates, key=lambda item: item[2])

    # Partial updates in these RTF streams do not carry width/height in the sector
    # data. They are stored as full-width normal-resolution rows followed by the
    # unused tail of the last sector.
    width = 384
    height = len(payload) // width
    image_size = width * height
    padding = len(payload) - image_size
    if (
        height < MIN_INFERRED_PARTIAL_HEIGHT
        or padding >= 2324
        or not all_zero(payload[image_size:])
    ):
        raise RTFError("could not determine normal-resolution image dimensions from sector payload")
    return width, height, image_size, padding


def clamp_byte(value: int) -> int:
    if value < 0:
        return 0
    if value > 255:
        return 255
    return value


def yuv_to_rgb(y: int, u: int, v: int) -> tuple[int, int, int]:
    blue = y + (444 * (u - 128)) // 256
    green = y - (86 * (u - 128)) // 256 - (179 * (v - 128)) // 256
    red = y + (351 * (v - 128)) // 256
    return clamp_byte(red), clamp_byte(green), clamp_byte(blue)


def decode_dyuv(data: bytes, width: int, height: int) -> list[tuple[int, int, int]]:
    if width % 2:
        raise RTFError("DYUV width must be even")
    needed = width * height
    if len(data) < needed:
        raise RTFError("DYUV data is shorter than image dimensions")

    pixels: list[tuple[int, int, int]] = []
    offset = 0
    pairs_per_line = width // 2
    for _ypos in range(height):
        y = 16
        u = 128
        v = 128
        for pair_index in range(pairs_per_line):
            byte0 = data[offset]
            byte1 = data[offset + 1]
            offset += 2

            y_even = (y + DYUV_DELTAS[byte0 & 0x0F]) & 0xFF
            y_odd = (y_even + DYUV_DELTAS[byte1 & 0x0F]) & 0xFF
            u_even = (u + DYUV_DELTAS[byte0 >> 4]) & 0xFF
            v_even = (v + DYUV_DELTAS[byte1 >> 4]) & 0xFF

            if pair_index + 1 < pairs_per_line:
                next0 = data[offset]
                next1 = data[offset + 1]
                u_next = (u_even + DYUV_DELTAS[next0 >> 4]) & 0xFF
                v_next = (v_even + DYUV_DELTAS[next1 >> 4]) & 0xFF
                u_odd = (u_even >> 1) + (u_next >> 1) + (u_even & u_next & 1)
                v_odd = (v_even >> 1) + (v_next >> 1) + (v_even & v_next & 1)
            else:
                u_odd = u_even
                v_odd = v_even

            pixels.append(yuv_to_rgb(y_even, u_even, v_even))
            pixels.append(yuv_to_rgb(y_odd, u_odd, v_odd))
            y, u, v = y_odd, u_even, v_even

    return pixels


def decode_clut(data: bytes, width: int, height: int, coding: int, palette: Palette) -> list[tuple[int, int, int]]:
    needed = width * height
    if len(data) < needed:
        raise RTFError("CLUT data is shorter than image dimensions")
    pixels: list[tuple[int, int, int]] = []
    for value in data[:needed]:
        if coding == 0x1:
            if value & 0x80:
                raise RTFError("CLUT7 image contains a nonzero high bit")
            palette_index = value & 0x7F
        else:
            palette_index = value
        pixels.append(palette.entries[palette_index])
    return pixels


def png_chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", binascii.crc32(kind + payload) & 0xFFFFFFFF)
    )


def write_png(path: Path, width: int, height: int, pixels: list[tuple[int, int, int]]) -> None:
    if len(pixels) != width * height:
        raise RTFError("PNG pixel count does not match dimensions")
    raw = bytearray()
    pos = 0
    for _ in range(height):
        raw.append(0)
        for red, green, blue in pixels[pos : pos + width]:
            raw.extend((red, green, blue))
        pos += width
    payload = b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)),
            png_chunk(b"IDAT", zlib.compress(bytes(raw), 9)),
            png_chunk(b"IEND", b""),
        ]
    )
    path.write_bytes(payload)


def write_palette_png(path: Path, entries: list[tuple[int, int, int]], block_size: int = 24) -> None:
    width = 16 * block_size
    height = 16 * block_size
    pixels: list[tuple[int, int, int]] = []
    for y in range(height):
        entry_row = y // block_size
        for x in range(width):
            entry_col = x // block_size
            pixels.append(entries[entry_row * 16 + entry_col])
    write_png(path, width, height, pixels)


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def chmod_tree(path: Path) -> None:
    for root, dirs, files in os.walk(path):
        os.chmod(root, 0o775)
        for dirname in dirs:
            os.chmod(Path(root) / dirname, 0o775)
        for filename in files:
            os.chmod(Path(root) / filename, 0o664)


def sector_summary(sector: Sector) -> dict[str, object]:
    return {
        "index": sector.index,
        "offset": sector.offset,
        "file_number": sector.file_number,
        "channel_number": sector.channel_number,
        "submode": f"0x{sector.submode:02x}",
        "submode_flags": submode_flags(sector.submode),
        "coding_info": f"0x{sector.coding_info:02x}",
        "form": 2 if sector.form2 else 1,
        "user_data_size": len(sector.user_data),
        "edc_stored": f"0x{sector.edc_stored:08x}",
        "edc_computed": f"0x{sector.edc_computed:08x}",
        "edc_status": sector.edc_status,
        "ecc_sha256": sector.ecc_sha256,
        "msf": None if sector.msf is None else f"{sector.msf[0]:02d}:{sector.msf[1]:02d}:{sector.msf[2]:02d}",
    }


def extract(input_file: Path, output_dir: Path, include_all: bool = False) -> dict[str, object]:
    data = input_file.read_bytes()
    layout, sectors = parse_sectors(data)
    palettes, runs, data_resources = collect_runs(sectors)

    if not palettes and not runs and not data_resources:
        raise RTFError("no extractable real-time resources found")
    if data_resources:
        raise RTFError("program data sectors that are not palette blocks are not implemented")
    if not runs:
        raise RTFError("no supported video resources found")
    if not any(sector.submode & SUBMODE_EOR for sector in sectors):
        raise RTFError("no real-time record boundary found")

    resources_meta: list[dict[str, object]] = []
    files_written: list[str] = []

    for palette in palettes:
        png_path = output_dir / f"{palette.resource_id}.png"
        write_palette_png(png_path, palette.entries)
        palette.png_path = png_path.name
        files_written.append(png_path.name)
        resources_meta.append(
            {
                "id": palette.resource_id,
                "type": "palette",
                "sector": palette.sector_index,
                "start_index": palette.start_index,
                "entry_count": palette.entry_count,
                "files": [png_path.name],
            }
        )

    for run_index, run in enumerate(runs):
        first = run.sectors[0]
        coding_parts = video_coding_parts(first.coding_info)
        if coding_parts["application_specific"]:
            raise RTFError(f"video run {run_index}: application-specific video coding is not implemented")
        if coding_parts["even_odd_lines"] != "even_or_unsplit":
            raise RTFError(f"video run {run_index}: split odd-line video coding is not implemented")

        coding = int(coding_parts["coding"])
        resolution = int(coding_parts["resolution"])
        coding_name = str(coding_parts["coding_name"])
        payload = b"".join(sector.user_data for sector in run.sectors)
        width, height, image_size, padding_size = determine_dimensions(coding, resolution, payload)
        image_bytes = payload[:image_size]
        padding = payload[image_size:]
        if (width, height) not in ((384, 280), (384, 240), (360, 240)) and len(set(image_bytes)) < 2:
            raise RTFError(f"video run {run_index}: inferred partial-update payload is blank")

        if coding in (0x1, 0x2):
            if run.palette is None:
                raise RTFError(f"video run {run_index}: CLUT image has no preceding palette data")
            pixels = decode_clut(image_bytes, width, height, coding, run.palette)
        elif coding == 0x5:
            pixels = decode_dyuv(image_bytes, width, height)
        else:
            raise RTFError(f"video run {run_index}: unsupported video coding {coding}")

        resource_id = f"resource_{len(resources_meta):03d}_{coding_name}_{width}x{height}"
        png_path = output_dir / f"{resource_id}.png"
        write_png(png_path, width, height, pixels)
        written = [png_path.name]

        padding_path_name = None
        if include_all:
            pixels_path = output_dir / f"{resource_id}.pixels.bin"
            vdsq_path = output_dir / f"{resource_id}.vdsq.bin"
            pixels_path.write_bytes(image_bytes)
            vdsq_path.write_bytes(payload)
            written.extend([pixels_path.name, vdsq_path.name])
            if padding_size:
                padding_path = output_dir / f"{resource_id}.padding.bin"
                padding_path.write_bytes(padding)
                padding_path_name = padding_path.name
                written.append(padding_path.name)

        files_written.extend(written)
        resources_meta.append(
            {
                "id": resource_id,
                "type": "video_image",
                "coding_info": f"0x{first.coding_info:02x}",
                "coding_name": coding_name,
                "resolution_code": resolution,
                "width": width,
                "height": height,
                "sector_start": run.sectors[0].index,
                "sector_end": run.sectors[-1].index,
                "sector_count": len(run.sectors),
                "file_number": first.file_number,
                "channel_number": first.channel_number,
                "triggered": any(s.submode & SUBMODE_TRIGGER for s in run.sectors),
                "eor": bool(run.sectors[-1].submode & SUBMODE_EOR),
                "eof": bool(run.sectors[-1].submode & SUBMODE_EOF),
                "palette": None if run.palette is None else run.palette.resource_id,
                "image_data_size": image_size,
                "sector_payload_size": len(payload),
                "padding_size": padding_size,
                "padding_file": padding_path_name,
                "files": written,
            }
        )

    manifest = {
        "format": "CD-i Real Time File sector stream",
        "input": str(input_file),
        "input_size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "layout": layout,
        "sector_count": len(sectors),
        "include_all": include_all,
        "resources": resources_meta,
        "resource_count": len(resources_meta),
        "output_files": sorted(files_written + ["manifest.json"]),
        "output_file_count": len(files_written) + 1,
        "sectors": [sector_summary(sector) for sector in sectors],
    }
    write_json(output_dir / "manifest.json", manifest)
    return manifest


def create_output_atomically(input_file: Path, output_dir: Path, include_all: bool = False) -> dict[str, object]:
    if output_dir.exists():
        if output_dir.is_file():
            raise RTFError(f"output path {output_dir} exists and is a file")
        if any(output_dir.iterdir()):
            raise RTFError(f"output directory {output_dir} already exists and is not empty")
    output_parent = output_dir.parent if output_dir.parent != Path("") else Path(".")
    output_parent.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.tmp.", dir=str(output_parent)))
    try:
        manifest = extract(input_file, temp_dir, include_all=include_all)
        chmod_tree(temp_dir)
        if output_dir.exists():
            output_dir.rmdir()
        temp_dir.rename(output_dir)
        chmod_tree(output_dir)
        return manifest
    except Exception:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract resources from a supported CD-i Real Time File RTF sector stream."
    )
    parser.add_argument("--all", action="store_true", help="also write raw VDSQ, decoded pixel, and padding .bin files")
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputDir", type=Path)
    args = parser.parse_args(argv)

    try:
        manifest = create_output_atomically(args.inputFile, args.outputDir, include_all=args.all)
    except RTFError as exc:
        print(f"realTimeFile.py: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"realTimeFile.py: {exc}", file=sys.stderr)
        return 1

    print(
        f"extracted {manifest['resource_count']} resources from {args.inputFile} "
        f"to {args.outputDir} ({manifest['output_file_count']} files)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

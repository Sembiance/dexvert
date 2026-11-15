#!/usr/bin/env python3
# Vibe coded by Codex
"""Extract paletted TIS V1 and TISpack TIZ0 tiles. Requires Pillow.

Usage: infinityEngineTileset.py [--all] inputFile outputDir
See infinityEngineTileset.txt for byte layouts and recovery/conversion policy.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, field
from functools import lru_cache
import hashlib
import io
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
import zlib


TIS_MAGIC = b"TIS V1  "
TIZ_MAGIC = b"TIZ0"
TILE_SIZE = 5120
SIDE = 64
PIXELS = SIDE * SIDE
CODECS = {b"TIL0", b"TIL1", b"TIL2"}


class UnsupportedFormat(ValueError):
    """Not an implemented, positively identified tileset variant."""


class DamagedTile(ValueError):
    """A tile cannot be decoded without guessing missing information."""


@dataclass
class Record:
    index: int
    offset: int
    payload_offset: int
    payload_length: int
    available_length: int
    codec: str
    beyond_count: bool = False


@dataclass
class Layout:
    format: str
    header: dict
    declared: int | None
    records: list[Record] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)
    regions: list[dict] = field(default_factory=list)


def inspect(data: bytes) -> Layout:
    """Preflight the entire framing before creating any output files.

    No extension checks, alignment searches, magic searches or guessed offsets.
    Recognized framing is also used beyond an incorrectly small tile count.
    """
    size = len(data)
    if data.startswith(TIS_MAGIC):
        result = Layout("TIS V1 paletted", {}, None)
        if size < 24:
            result.issues.append(f"Truncated TIS header: {size}/24 bytes; no tile offset available")
            result.regions.append(dict(offset=0, length=size, role="truncated_header"))
            return result
        count, stride, start, dimension = struct.unpack_from("<4I", data, 8)
        if stride == 12:
            raise UnsupportedFormat("PVRZ-reference TIS variant (12-byte records); external textures are outside this extractor's scope")
        if stride != TILE_SIZE or dimension != SIDE:
            raise UnsupportedFormat(f"Unsupported or damaged TIS geometry: record size {stride}, side {dimension}; cannot infer a layout")
        result.declared = count
        result.header = dict(signature="TIS ", version="V1  ", tile_count=count,
                             tile_record_bytes=stride, tile_data_offset=start, tile_side=dimension)
        result.regions.append(dict(offset=0, length=24, role="header"))
        if start < 24 or start > size:
            result.issues.append(f"Invalid/unavailable tile-data offset {start} for {size}-byte file")
            if size > 24:
                result.regions.append(dict(offset=24, length=size-24, role="unreachable_data"))
            return result
        if start > 24:
            result.issues.append(f"Noncanonical {start-24}-byte gap before tiles; explicit offset honored")
            result.regions.append(dict(offset=24, length=start-24, role="header_gap",
                                       hex=data[24:start].hex()))
        full, remainder = divmod(size-start, stride)
        for index in range(full + bool(remainder)):
            offset = start + index * stride
            available = min(stride, size-offset)
            result.records.append(Record(index, offset, offset, stride, available,
                                         "TIS", index >= count))
        if full != count or remainder:
            result.issues.append(f"Header declares {count} tiles; physical data has {full} complete tiles and {remainder} bytes of a final tile")
        return result
    if not data.startswith(TIZ_MAGIC):
        if data.startswith(b"TIS "):
            raise UnsupportedFormat("Unsupported or incomplete TIS version signature; expected the exact eight bytes 'TIS V1  '")
        if data.startswith(b"\x1f\x8b"):
            raise UnsupportedFormat("gzip archive/stream, not a TIS or TIZ tileset; archive contents are not traversed")
        raise UnsupportedFormat("No supported TIS V1 or TIZ0 signature")
    result = Layout("TIZ0", {}, None)
    if size < 8:
        result.issues.append(f"Truncated TIZ0 header: {size}/8 bytes")
        result.regions.append(dict(offset=0, length=size, role="truncated_header"))
        return result
    count, reserved = struct.unpack_from(">HH", data, 4)
    result.declared = count
    result.header = dict(signature="TIZ0", tile_count=count, reserved=reserved, tile_side=SIDE)
    result.regions.append(dict(offset=0, length=8, role="header"))
    if reserved:
        result.issues.append(f"Reserved TIZ0 header field is nonzero: 0x{reserved:04x}")
    offset = 8
    while offset < size:
        if size-offset < 6:
            result.issues.append(f"Truncated tile header at byte {offset}: {size-offset}/6 bytes")
            result.regions.append(dict(offset=offset, length=size-offset, role="truncated_tile_header"))
            break
        tag = data[offset:offset+4]
        length = struct.unpack_from(">H", data, offset+4)[0]
        if tag not in CODECS:
            if tag[:3] == b"TIL":
                raise UnsupportedFormat(f"Unsupported TIZ tile encoding {tag!r} at byte {offset}; preflight wrote nothing")
            result.issues.append(f"Damaged tile tag {tag.hex()} at byte {offset}; boundaries after this point cannot be trusted")
            result.regions.append(dict(offset=offset, length=size-offset, role="unframed_damaged_tail"))
            break
        index = len(result.records)
        available = min(length, size-offset-6)
        result.records.append(Record(index, offset, offset+6, length, available,
                                     tag.decode("ascii"), index >= count))
        if available != length:
            result.issues.append(f"Tile {index} payload truncated: {available}/{length} bytes")
        offset += 6 + available
    if len(result.records) != count:
        result.issues.append(f"Header declares {count} tiles; {len(result.records)} framed tile records are present")
    return result


def inflate(data: bytes, expected: int) -> tuple[bytes, list[str], dict]:
    """Bounded zlib decoding, including Adler-32 and exact stream end checks.

    On a zlib error, replay one byte at a time to retain the deterministically
    decoded prefix that Python would otherwise discard in the failing call.
    """
    issues: list[str] = []
    decoder = zlib.decompressobj()
    try:
        raw = decoder.decompress(data, expected+1)
    except zlib.error as error:
        issues.append(f"Invalid zlib stream: {error}; retaining decoded prefix")
        decoder = zlib.decompressobj()
        prefix = bytearray()
        for value in data:
            try:
                prefix.extend(decoder.decompress(bytes((value,)), expected+1-len(prefix)))
            except zlib.error:
                break
            if len(prefix) > expected:
                break
        raw = bytes(prefix)
    if len(raw) != expected:
        issues.append(f"Decoded size {len(raw)}; expected exactly {expected} bytes")
    if not decoder.eof:
        issues.append("zlib end/checksum not validated (truncated, invalid, or oversized stream)")
    if decoder.unused_data:
        issues.append(f"{len(decoder.unused_data)} extra bytes after the zlib stream")
    details = dict(compressed_bytes=len(data), decoded_bytes=len(raw), expected_bytes=expected,
                   checksum_valid=decoder.eof, trailing_bytes=len(decoder.unused_data),
                   cmf_flg=data[:2].hex())
    if decoder.eof:
        end = len(data)-len(decoder.unused_data)
        details["adler32"] = data[end-4:end].hex()
    return raw[:expected], issues, details


def jpeg_structure(data: bytes) -> dict:
    """Account for every JPEG byte by marker segments and entropy-coded scans.

    Entropy decoding/IDCT are delegated to Pillow's JPEG codec. Marker framing
    handles byte stuffing, restart markers, fill bytes and multiple scans.
    """
    if data[:2] != b"\xff\xd8":
        raise DamagedTile("JPEG payload has no SOI marker")
    offset = 2
    markers = Counter({"FFD8": 1})
    segment_bytes = 2
    entropy_bytes = 0
    frames = []
    while offset < len(data):
        begin = offset
        if data[offset] != 255:
            raise DamagedTile(f"Invalid JPEG marker boundary at payload byte {offset}")
        while offset < len(data) and data[offset] == 255:
            offset += 1
        if offset == len(data):
            raise DamagedTile("Truncated JPEG marker")
        code = data[offset]
        offset += 1
        markers[f"FF{code:02X}"] += 1
        if code == 0xD9:
            segment_bytes += offset-begin
            if not frames:
                raise DamagedTile("JPEG has no image frame")
            return dict(markers=dict(markers), marker_segment_bytes=segment_bytes,
                        entropy_coded_bytes=entropy_bytes, frames=frames,
                        bytes_through_eoi=offset, trailing_bytes=len(data)-offset)
        if code in (0x00, 0xD8) or 0xD0 <= code <= 0xD7:
            raise DamagedTile(f"Unexpected JPEG marker FF{code:02X} outside a scan")
        if code == 0x01:
            segment_bytes += offset-begin
            continue
        if offset+2 > len(data):
            raise DamagedTile("Truncated JPEG segment length")
        length = struct.unpack_from(">H", data, offset)[0]
        if length < 2 or offset+length > len(data):
            raise DamagedTile("Invalid/truncated JPEG segment")
        if code in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            if length < 8:
                raise DamagedTile("Short JPEG frame header")
            precision, height, width, components = struct.unpack_from(">BHHB", data, offset+2)
            if length != 8 + 3*components:
                raise DamagedTile("Incorrect JPEG frame component table size")
            if (width, height, components, precision) != (SIDE, SIDE, 3, 8):
                raise DamagedTile(f"Expected an 8-bit 64x64 three-component JPEG; got {width}x{height}, {components} components, {precision} bits")
            frames.append(dict(marker=f"FF{code:02X}", width=width, height=height,
                               components=components, precision=precision,
                               component_parameters_hex=data[offset+8:offset+length].hex()))
        offset += length
        segment_bytes += offset-begin
        if code == 0xDA:
            scan_start = offset
            while True:
                marker_start = data.find(b"\xff", offset)
                if marker_start < 0:
                    raise DamagedTile("JPEG scan is truncated before EOI")
                end = marker_start+1
                while end < len(data) and data[end] == 255:
                    end += 1
                if end == len(data):
                    raise DamagedTile("JPEG scan ends inside a marker")
                following = data[end]
                if following == 0 or 0xD0 <= following <= 0xD7:
                    if following:
                        markers[f"FF{following:02X}"] += 1
                    offset = end+1
                    continue
                entropy_bytes += marker_start-scan_start
                offset = marker_start
                break
    raise DamagedTile("JPEG has no EOI marker")


def nearest_palette(palette: list[tuple[int, int, int]]):
    """Exact nearest-color search, squared Euclidean distance, lowest-index ties.

    A kd-tree accelerates the exhaustive mathematical result; no approximate
    color lookup, quantization grid or dithering is used. Entry zero is excluded.
    """
    def build(indices, depth=0):
        if not indices:
            return None
        axis = depth % 3
        indices.sort(key=lambda index: (palette[index][axis], index))
        middle = len(indices)//2
        return (indices[middle], axis, build(indices[:middle], depth+1),
                build(indices[middle+1:], depth+1))

    tree = build(list(range(1, 256)))

    @lru_cache(maxsize=4096)
    def lookup(color):
        best_distance = 3*255*255+1
        best_index = 256

        def visit(node):
            nonlocal best_distance, best_index
            if node is None:
                return
            index, axis, left, right = node
            candidate = palette[index]
            distance = ((color[0]-candidate[0])**2 + (color[1]-candidate[1])**2
                        + (color[2]-candidate[2])**2)
            if (distance, index) < (best_distance, best_index):
                best_distance, best_index = distance, index
            delta = color[axis]-candidate[axis]
            near, far = (left, right) if delta < 0 else (right, left)
            visit(near)
            if delta*delta <= best_distance:
                visit(far)

        visit(tree)
        return best_index

    return lookup


def paletted_image(raw: bytes, Image):
    if len(raw) <= 1024:
        raise DamagedTile("No complete palette plus pixel data available")
    palette = raw[:1024]
    pixels = raw[1024:5120]
    rgb = bytes(channel for i in range(256) for channel in palette[i*4:i*4+3][::-1])
    image = Image.frombytes("P", (SIDE, SIDE), pixels.ljust(PIXELS, b"\0"))
    image.putpalette(rgb)
    green_key = palette[:3] == b"\x00\xff\x00"
    if green_key:
        image.info["transparency"] = 0
    if len(pixels) < PIXELS:
        image = image.convert("RGBA")
        alpha = bytearray(image.getchannel("A").tobytes())
        alpha[len(pixels):] = b"\0" * (PIXELS-len(pixels))
        image.putalpha(Image.frombytes("L", (SIDE, SIDE), bytes(alpha)))
    details = dict(palette_bgrx_hex=palette.hex(), unused_palette_bytes=dict(Counter(palette[3::4])),
                   transparent_palette_index=0 if green_key else None, known_pixels=len(pixels))
    return image, details


def decode(data: bytes, record: Record, Image):
    payload = data[record.payload_offset:record.payload_offset+record.available_length]
    issues = []
    details = {}
    if record.available_length != record.payload_length:
        issues.append(f"Incomplete tile payload: {record.available_length}/{record.payload_length} bytes")
    if record.codec in ("TIS", "TIL0"):
        raw = payload
        if record.codec == "TIL0":
            raw, warnings, details["zlib"] = inflate(payload, TILE_SIZE)
            issues.extend(warnings)
        image, palette_info = paletted_image(raw, Image)
        details.update(palette_info)
        if len(raw) < TILE_SIZE:
            issues.append("Only known pixels exported; unavailable pixels have alpha zero")
        return image, issues, details
    header = None
    jpeg = payload
    if record.codec == "TIL1":
        if len(payload) < 2:
            raise DamagedTile("Missing TIL1 compressed-header length")
        header_length = struct.unpack_from(">H", payload)[0]
        if header_length+2 > len(payload):
            raise DamagedTile("TIL1 compressed header exceeds available tile payload")
        header, warnings, details["zlib"] = inflate(payload[2:2+header_length], 1280)
        issues.extend(warnings)
        if len(header) < 768:
            raise DamagedTile("TIL1 palette is incomplete")
        if len(header) < 1280:
            issues.append("TIL1 mask incomplete; pixels with missing mask bits have alpha zero")
        header = header.ljust(1280, b"\0")
        details["compressed_header_bytes"] = header_length
        details["palette_bgr_planes_hex"] = header[:768].hex()
        details["opacity_mask_hex"] = header[768:].hex()
        jpeg = payload[2+header_length:]
    details["jpeg"] = jpeg_structure(jpeg)
    if details["jpeg"]["trailing_bytes"]:
        issues.append(f"{details['jpeg']['trailing_bytes']} trailing bytes after JPEG EOI")
    try:
        with Image.open(io.BytesIO(jpeg), formats=["JPEG"]) as source:
            if source.size != (SIDE, SIDE) or source.mode != "RGB":
                raise DamagedTile("JPEG decoder did not identify a 64x64 color tile")
            source.load()
            stored = source.copy()
    except (OSError, ValueError) as error:
        raise DamagedTile(f"JPEG decode failed: {error}") from error
    if header is None:
        blue, green, red = stored.split()
        return Image.merge("RGB", (red, green, blue)), issues, details
    palette = [(header[i], header[256+i], header[512+i]) for i in range(256)]
    nearest = nearest_palette(palette)
    colors = stored.tobytes()
    mask = header[768:]
    indices = bytearray(PIXELS)
    for index in range(PIXELS):
        if mask[index//8] & (128 >> (index % 8)):
            indices[index] = nearest(tuple(colors[3*index:3*index+3]))
    image = Image.frombytes("P", (SIDE, SIDE), bytes(indices))
    image.putpalette(bytes(channel for color in palette for channel in reversed(color)))
    image.info["transparency"] = 0
    details["transparent_pixels"] = indices.count(0)
    return image, issues, details


def ensure_directory(path: Path):
    missing = []
    current = path
    while not current.exists():
        missing.append(current)
        current = current.parent
    path.mkdir(parents=True, exist_ok=True)
    for directory in missing:
        directory.chmod(directory.stat().st_mode | 0o750)
    path.chmod(path.stat().st_mode | 0o050)


def atomic_write(path: Path, writer):
    """Replace only the named output; never leave a half-written PNG/JSON."""
    fd, temporary = tempfile.mkstemp(prefix=".tileset-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            writer(stream)
            os.fchmod(stream.fileno(), 0o644)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def extract(input_file: Path | str, output_dir: Path | str, *, all_metadata=False) -> dict:
    input_file, output_dir = Path(input_file), Path(output_dir)
    with input_file.open("rb") as stream:
        prefix = stream.read(24)
        # Reject unrelated files and unsupported fixed headers without reading
        # an arbitrarily large archive, or creating the output directory.
        inspect(prefix)
        data = prefix + stream.read()
    layout = inspect(data)
    try:
        from PIL import Image
    except ImportError as error:
        raise RuntimeError("Pillow is required; install with: python -m pip install Pillow") from error
    summary = dict(input_file=str(input_file), input_bytes=len(data), format=layout.format,
                   header=layout.header, declared_tiles=layout.declared,
                   encountered_tiles=len(layout.records), extracted_tiles=0, failed_tiles=0,
                   recovered_extra_tiles=0, damaged_tiles=0, output_bytes=0,
                   codec_counts=dict(Counter(record.codec for record in layout.records)),
                   issues=list(layout.issues), tile_issues=[], non_tile_regions=layout.regions)
    if all_metadata:
        summary["input_sha256"] = hashlib.sha256(data).hexdigest()
        summary["tiles"] = []
    occupied = sum(region["length"] for region in layout.regions)
    occupied += sum(record.available_length + record.payload_offset-record.offset
                    for record in layout.records)
    summary["classified_input_bytes"] = occupied
    # This invariant catches accidental gaps or overlap in our own framing.
    if occupied != len(data):
        raise RuntimeError(f"Internal byte-accounting mismatch: {occupied} != {len(data)}")
    directory_ready = False
    for record in layout.records:
        tile = dict(index=record.index, offset=record.offset, codec=record.codec,
                    payload_offset=record.payload_offset, payload_bytes=record.payload_length,
                    available_payload_bytes=record.available_length, beyond_declared_count=record.beyond_count)
        try:
            image, issues, details = decode(data, record, Image)
        except DamagedTile as error:
            summary["failed_tiles"] += 1
            tile.update(status="skipped", issues=[str(error)])
            summary["tile_issues"].append(dict(index=record.index, issues=tile["issues"], status="skipped"))
        else:
            if not directory_ready:
                ensure_directory(output_dir)
                directory_ready = True
            name = f"tile_{record.index:06d}.png"
            destination = output_dir / name
            atomic_write(destination, lambda stream: image.save(stream, format="PNG", compress_level=6))
            image.close()
            output_size = destination.stat().st_size
            summary["extracted_tiles"] += 1
            summary["output_bytes"] += output_size
            summary["recovered_extra_tiles"] += int(record.beyond_count)
            summary["damaged_tiles"] += bool(issues)
            tile.update(status="recovered" if issues else "ok", output=name,
                        output_bytes=output_size, issues=issues)
            if issues:
                summary["tile_issues"].append(dict(index=record.index, issues=issues, status="recovered"))
            if all_metadata:
                tile.update(details)
        if all_metadata:
            summary["tiles"].append(tile)
    summary["status"] = "warning" if (summary["issues"] or summary["tile_issues"]) else "ok"
    if all_metadata:
        if not directory_ready:
            ensure_directory(output_dir)
        metadata = output_dir / "metadata.json"
        encoded = (json.dumps(summary, indent=2, ensure_ascii=False)+"\n").encode("utf-8")
        atomic_write(metadata, lambda stream: stream.write(encoded))
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", help="also write a JSON byte/codec/palette audit; default output is PNG only")
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputDir", type=Path)
    arguments = parser.parse_args(argv)
    try:
        result = extract(arguments.inputFile, arguments.outputDir, all_metadata=arguments.all)
    except UnsupportedFormat as error:
        print(f"Unsupported: {error}", file=sys.stderr)
        return 2
    except (OSError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    for issue in result["issues"]:
        print(f"Warning: {issue}", file=sys.stderr)
    for tile in result["tile_issues"]:
        print(f"Warning: tile {tile['index']} ({tile['status']}): {'; '.join(tile['issues'])}", file=sys.stderr)
    print(f"{result['format']}: extracted {result['extracted_tiles']} PNGs; "
          f"{result['failed_tiles']} skipped; {result['classified_input_bytes']}/{result['input_bytes']} input bytes classified")
    return 1 if result["status"] != "ok" else 0


if __name__ == "__main__":
    sys.exit(main())

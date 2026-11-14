#!/usr/bin/env python3
# Vibe coded by Codex
"""Convert Infinity Engine MOS V1 / zlib-wrapped MOSC V1 to one RGBA PNG.

Usage: infinityEngineGraphic.py [-verbose] inputFile outputFile
Only the PNG is retained; diagnostics (including verbose byte accounting) go
to stderr. No third-party modules, game resources, or companion files needed.
"""

import argparse
from collections import Counter
from dataclasses import dataclass, field
import io
import json
import mmap
import os
from pathlib import Path
import struct
import sys
import tempfile
import zlib


SIGNATURE = b"MOS V1  "
COMPRESSED_SIGNATURE = b"MOSCV1  "
HEADER = struct.Struct("<8s4H2I")
SIDE = 64
TRANSPARENT = b"\0\0\0\0"


class MosError(ValueError):
    """Unrecognized, unsupported, or unrecoverable input."""


@dataclass
class Diagnostics:
    counts: Counter = field(default_factory=Counter)
    examples: dict = field(default_factory=dict)

    def add(self, code, message, count=1):
        self.counts[code] += count
        if code not in self.examples:
            self.examples[code] = message

    def messages(self):
        return [f"{self.examples[k]} (occurrences: {v})"
                for k, v in self.counts.items()]


def _inflate(data, diagnostics):
    """Inflate one RFC 1950 member; retain its valid prefix if damaged."""
    if len(data) < 12:
        raise MosError("MOSC V1 header is truncated; no compressed payload")
    declared = struct.unpack_from("<I", data, 8)[0]
    decoder = zlib.decompressobj()
    output = bytearray()
    position = 12
    broken = False
    while position < len(data) and not decoder.eof:
        block = data[position:position + 65536]
        saved = decoder.copy()
        try:
            output.extend(decoder.decompress(block))
            position += len(block)
        except zlib.error as error:
            # Retry the failing chunk byte by byte to retain the prefix even
            # when only the final Adler-32 checksum is damaged.
            decoder = saved
            for value in block:
                position += 1
                try:
                    output.extend(decoder.decompress(bytes((value,))))
                except zlib.error:
                    break
            diagnostics.add("zlib_error", f"Damaged zlib stream: {error}")
            broken = True
            break
    if not decoder.eof and not broken:
        diagnostics.add("zlib_truncated", "Zlib member has no complete end/checksum")
    stream_end = position - len(decoder.unused_data)
    trailing = len(data) - stream_end
    if trailing:
        diagnostics.add("wrapper_unconsumed", f"{trailing} wrapper bytes were not consumed")
    if len(output) != declared:
        diagnostics.add("expanded_length", f"MOSC declares {declared} expanded bytes; recovered {len(output)}")
    if output[:8] != SIGNATURE:
        raise MosError("MOSC does not contain a recoverable MOS V1 image")
    return output, {"file_bytes": len(data), "header_bytes": 12,
                    "declared_expanded_bytes": declared,
                    "expanded_bytes": len(output),
                    "zlib_consumed_bytes": stream_end - 12,
                    "unconsumed_bytes": trailing,
                    "zlib_complete": decoder.eof}


def _merge_ranges(ranges):
    merged = []
    for start, end in sorted(ranges):
        if start >= end:
            continue
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
        else:
            merged.append((start, end))
    return merged


class MosImage:
    """Random-access MOS V1 reader with deterministic partial-file recovery."""

    def __init__(self, data):
        self.diagnostics = Diagnostics()
        self.wrapper = None
        if data[:8] == COMPRESSED_SIGNATURE:
            data, self.wrapper = _inflate(data, self.diagnostics)
        elif data[:8] != SIGNATURE:
            raise MosError("Not a supported MOS V1 / MOSC V1 file (exact signature required)")
        if len(data) < HEADER.size:
            raise MosError("Confirmed MOS V1, but its 24-byte header is truncated")
        self.data = data
        (_, self.width, self.height, self.columns, self.rows,
         self.block_size, self.palette_offset) = HEADER.unpack_from(data)
        if not self.width or not self.height:
            raise MosError("MOS V1 has a zero image dimension; dimensions cannot be inferred")
        if not self.columns or not self.rows:
            raise MosError("MOS V1 has an empty tile grid; table positions cannot be recovered")
        if self.palette_offset < HEADER.size:
            raise MosError("Palette offset overlaps the MOS header; no reliable palette location")
        if self.block_size != SIDE:
            self.diagnostics.add("block_size", f"Invalid V1 block-size field {self.block_size}; using V1's defined 64 pixels")
        expected = ((self.width + 63) // 64, (self.height + 63) // 64)
        if (self.columns, self.rows) != expected:
            self.diagnostics.add("grid", f"Declared grid {self.columns}x{self.rows} disagrees with required {expected[0]}x{expected[1]}; retaining declared table layout")
        self.tile_count = self.columns * self.rows
        self.lookup_offset = self.palette_offset + 1024 * self.tile_count
        self.pixel_offset = self.lookup_offset + 4 * self.tile_count
        self.available_offsets = min(self.tile_count,
                                     max(0, (len(data) - self.lookup_offset) // 4))
        if self.lookup_offset > len(data):
            self.diagnostics.add("palettes_truncated", "Palette array is truncated")
        if self.available_offsets < self.tile_count:
            self.diagnostics.add("lookup_truncated", "Tile offset table is truncated",
                                 self.tile_count - self.available_offsets)
        self.recovered_pixels = 0
        self.transparent_pixels = 0
        self.audit = self._audit()

    def _tile(self, index):
        x = (index % self.columns) * SIDE
        y = (index // self.columns) * SIDE
        width = max(0, min(SIDE, self.width - x))
        height = max(0, min(SIDE, self.height - y))
        relative = struct.unpack_from("<I", self.data, self.lookup_offset + index * 4)[0]
        return x, y, width, height, self.pixel_offset + relative

    def _audit(self):
        """Account for every stored byte, including unused palette entries."""
        size = len(self.data)
        spans = [(0, HEADER.size)]
        regions = {"header": HEADER.size}
        for name, start, end in (
                ("palettes", self.palette_offset, self.lookup_offset),
                ("tile_offsets", self.lookup_offset, self.pixel_offset)):
            present_end = min(size, end)
            regions[name] = max(0, present_end - start)
            if start < present_end:
                spans.append((start, present_end))
        pixel_spans = []
        logical_pixels = 0
        for index in range(self.available_offsets):
            _, _, width, height, start = self._tile(index)
            count = width * height
            logical_pixels += count
            if not count:
                self.diagnostics.add("outside_canvas", "Tile lies outside declared image dimensions")
                continue
            end = min(size, start + count)
            if end < start + count:
                self.diagnostics.add("tile_truncated", "Tile pixels extend past end of file")
            if start < end:
                pixel_spans.append((start, end))
        merged_pixels = _merge_ranges(pixel_spans)
        unique_pixels = sum(b - a for a, b in merged_pixels)
        spans.extend(merged_pixels)
        regions["pixel_indices"] = unique_pixels
        covered = _merge_ranges(spans)
        gaps = []
        cursor = 0
        for start, end in covered:
            if start > cursor:
                gaps.append([cursor, start])
            cursor = end
        if cursor < size:
            gaps.append([cursor, size])
        unused = sum(b - a for a, b in gaps)
        if unused:
            self.diagnostics.add("unreferenced_bytes", f"{unused} bytes lie outside the header, tables, and referenced pixels; no V1 image meaning")
        reserved_count = 0
        nonzero_reserved = 0
        # Chunk the palette scan to avoid making a whole-file copy.
        for start in range(self.palette_offset, min(size, self.lookup_offset), 1024 * 1024):
            end = min(start + 1024 * 1024, size, self.lookup_offset)
            values = self.data[start + 3:end:4]
            reserved_count += len(values)
            nonzero_reserved += len(values) - values.count(0)
        return {"file_bytes": size, "regions": regions,
                "accounted_bytes": sum(regions.values()),
                "unreferenced_bytes": unused, "unreferenced_ranges": gaps,
                "palette_reserved_bytes": reserved_count,
                "nonzero_reserved_bytes": nonzero_reserved,
                "logical_tile_pixels": logical_pixels,
                "shared_pixel_reference_bytes": sum(b - a for a, b in pixel_spans) - unique_pixels}

    def iter_rgba_rows(self):
        """Yield top-down RGBA rows, using at most one 64-row canvas band."""
        self.recovered_pixels = 0
        self.transparent_pixels = 0
        width = self.width
        for y0 in range(0, self.height, SIDE):
            band_height = min(SIDE, self.height - y0)
            band = bytearray(width * band_height * 4)
            tile_row = y0 // SIDE
            if tile_row < self.rows:
                for column in range(min(self.columns, (width + 63) // 64)):
                    index = tile_row * self.columns + column
                    if index >= self.available_offsets:
                        continue
                    x, _, tile_width, tile_height, start = self._tile(index)
                    palette_start = self.palette_offset + index * 1024
                    palette = []
                    valid = []
                    green = []
                    for entry in range(256):
                        pos = palette_start + entry * 4
                        known = pos + 3 <= min(len(self.data), self.lookup_offset)
                        valid.append(known)
                        if known:
                            b, g, r = self.data[pos:pos + 3]
                            key = (r, g, b) == (0, 255, 0)
                            palette.append(bytes((r, g, b, 0 if key else 255)))
                            green.append(key)
                        else:
                            palette.append(TRANSPARENT)
                            green.append(False)
                    for row in range(tile_height):
                        source = start + row * tile_width
                        indices = self.data[source:min(source + tile_width, len(self.data))]
                        decoded = b"".join(palette[value] for value in indices)
                        target = (row * width + x) * 4
                        band[target:target + len(decoded)] = decoded
                        self.recovered_pixels += sum(valid[value] for value in indices)
                        self.transparent_pixels += sum(green[value] for value in indices)
            for row in range(band_height):
                yield bytes(band[row * width * 4:(row + 1) * width * 4])

    def metadata(self):
        return {"format": "MOSC V1" if self.wrapper else "MOS V1",
                "width": self.width, "height": self.height,
                "columns": self.columns, "rows": self.rows,
                "block_size_field": self.block_size,
                "palette_offset": self.palette_offset,
                "tile_offset_table": self.lookup_offset,
                "pixel_data_offset": self.pixel_offset,
                "tile_count": self.tile_count, "byte_audit": self.audit,
                "wrapper": self.wrapper, "recovered_pixels": self.recovered_pixels,
                "missing_pixels": self.width * self.height - self.recovered_pixels,
                "color_key_pixels": self.transparent_pixels,
                "warnings": self.diagnostics.messages()}


def _png_chunk(kind, payload):
    return (struct.pack(">I", len(payload)) + kind + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xffffffff))


def encode_png(image):
    """Create an 8-bit, noninterlaced RGBA PNG using only the standard library."""
    output = io.BytesIO()
    output.write(b"\x89PNG\r\n\x1a\n")
    output.write(_png_chunk(b"IHDR", struct.pack(">2I5B", image.width, image.height,
                                                8, 6, 0, 0, 0)))
    compressor = zlib.compressobj(6)
    for row in image.iter_rgba_rows():
        # PNG filter 1 (Sub), with a four-byte RGBA pixel stride.
        filtered = bytearray(row)
        for i in range(len(row) - 1, 3, -1):
            filtered[i] = (row[i] - row[i - 4]) & 255
        compressed = compressor.compress(b"\x01" + filtered)
        if compressed:
            output.write(_png_chunk(b"IDAT", compressed))
    output.write(_png_chunk(b"IDAT", compressor.flush()))
    output.write(_png_chunk(b"IEND", b""))
    if image.recovered_pixels == 0:
        raise MosError("Confirmed MOS V1, but no pixel with a known palette color can be recovered")
    missing = image.width * image.height - image.recovered_pixels
    if missing:
        image.diagnostics.add("missing_pixels", f"{missing} unrecoverable pixels were left transparent")
    return output.getvalue()


def _write_png(destination, encoded):
    """Atomically replace the destination; leave no auxiliary files behind."""
    destination = Path(destination)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(prefix="." + destination.name + ".",
                                         suffix=".png", dir=destination.parent,
                                         delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(encoded)
            stream.flush()
            os.fchmod(stream.fileno(), 0o644)
        os.replace(temporary, destination)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def convert(input_file, output_file):
    """Write one PNG, returning diagnostic metadata without writing sidecars."""
    source = Path(input_file)
    destination = Path(output_file)
    if source.resolve() == destination.resolve() or (
            destination.exists() and os.path.samefile(source, destination)):
        raise MosError("Input and output must be different files")
    with source.open("rb") as stream:
        signature = stream.read(8)
        if signature not in (SIGNATURE, COMPRESSED_SIGNATURE):
            raise MosError("Not a supported MOS V1 / MOSC V1 file (exact signature required)")
        with mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
            image = MosImage(data)
            encoded = encode_png(image)
            metadata = image.metadata()
    _write_png(destination, encoded)
    return metadata


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputFile", help="MOS V1 or MOSC V1 file (extension is ignored)")
    parser.add_argument("outputFile", help="destination PNG; parent directory must exist")
    parser.add_argument("-verbose", "--verbose", action="store_true",
                        help="print structure and byte accounting to stderr; no sidecars")
    args = parser.parse_args(argv)
    try:
        metadata = convert(args.inputFile, args.outputFile)
    except (MosError, OSError, MemoryError, OverflowError) as error:
        print(f"infinityEngineGraphic: {error or type(error).__name__}", file=sys.stderr)
        return 1
    if args.verbose:
        print(json.dumps(metadata, indent=2), file=sys.stderr)
    else:
        for warning in metadata["warnings"]:
            print(f"infinityEngineGraphic: warning: {warning}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

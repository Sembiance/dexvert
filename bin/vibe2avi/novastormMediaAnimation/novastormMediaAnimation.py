#!/usr/bin/env python3
# Vibe coded by Codex
"""Decode Novastorm PCFM animations. Python standard library only."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
import json
import os
from pathlib import Path
import struct
import sys


class FormatError(ValueError):
    """The input cannot be converted without inventing format semantics."""


class DamagedFrame(ValueError):
    """A recognized frame has damaged or truncated commands."""


class Reader:
    def __init__(self, data: bytes, pos: int = 0):
        self.data = data
        self.pos = pos

    def take(self, count: int) -> bytes:
        end = self.pos + count
        if end > len(self.data):
            raise DamagedFrame(f"truncated command at payload offset {self.pos}")
        result = self.data[self.pos:end]
        self.pos = end
        return result

    def byte(self) -> int:
        return self.take(1)[0]

    def word(self) -> int:
        return int.from_bytes(self.take(2), "little")


def expand_runs(reader: Reader, bits: int, count: int) -> bytes:
    """Paired runs; the final pair is consumed in full and clipped."""
    result = bytearray()
    while len(result) < count:
        lengths = reader.byte()
        values = reader.byte()
        for pair in range(2):
            if pair and bits == 4:
                values = reader.byte()
            for j in range(2):
                k = pair * 2 + j
                n = ((lengths >> (6 - 2 * k)) & 3) + 1
                shift = (6 - 2 * k) if bits == 2 else (4 - 4 * j)
                value = (values >> shift) & ((1 << bits) - 1)
                result.extend(bytes([value]) * n)
            if len(result) >= count:
                return bytes(result[:count])
    return bytes(result)


class Decoder:
    """Persistent block palettes and selectors, in column-major block order."""
    def __init__(self, width: int, height: int):
        self.width, self.height = width, height
        self.block_rows = height // 8
        self.count = width // 8 * self.block_rows
        self.palettes = [bytearray(16) for _ in range(self.count)]
        self.selectors = [bytearray(64) for _ in range(self.count)]
        self.opcodes = Counter()

    def block(self, reader: Reader, index: int) -> int:
        opcode = reader.byte()
        palette = self.palettes[index][:]
        pixels = self.selectors[index][:]
        mode, bits = 0, 0
        if opcode in (0x00, 0x20):
            if opcode == 0x20:
                palette[0] = reader.byte()
            pixels[:] = bytes(64)
        elif opcode in (0x08, 0x09, 0x0A, 0x0C, 0x0D, 0x0E,
                        0x30, 0x70, 0xB0):
            source = index + reader.byte()
            if source >= self.count:
                raise DamagedFrame(f"palette reference outside image: block {source}")
            bits = 1 if opcode in (8, 9, 10) else 2 if opcode in (0x30, 0x70, 0xB0) else 4
            size = 1 << bits
            palette[:size] = self.palettes[source][:size]
            mode = {8: 0, 9: 1, 10: 2, 12: 0, 13: 1, 14: 2,
                    0x30: 0, 0x70: 1, 0xB0: 2}[opcode]
        elif 0x40 <= opcode <= 0x6C and opcode % 4 == 0:
            bits, mode = 1, (opcode >> 4) - 4
            for slot, flag in ((0, 8), (1, 4)):
                if opcode & flag:
                    palette[slot] = reader.byte()
        elif 0x80 <= opcode <= 0xAF or 0xC0 <= opcode <= 0xEF:
            bits = 2 if opcode < 0xC0 else 4
            mode = (opcode >> 4) - (8 if bits == 2 else 12)
            if bits == 4 and opcode & 15 == 0:
                mask, size = reader.word(), 16
            else:
                mask, size = opcode & 15, 4
            for slot in range(size):
                if mask & (1 << (size - 1 - slot)):
                    palette[slot] = reader.byte()
        else:
            raise DamagedFrame(f"invalid block opcode 0x{opcode:02x}")

        if mode:
            mask = reader.byte() if mode == 1 else 255
            rows = [y for y in range(7, -1, -1) if mask & (1 << y)]
            if not rows and bits > 1:
                raise DamagedFrame("empty row mask on a pixel-update command")
            if bits == 1:
                values = bytes((b >> shift) & 1 for b in reader.take(len(rows))
                               for shift in range(7, -1, -1))
            else:
                values = expand_runs(reader, bits, len(rows) * 8)
            # The full four-bit path copies its temporary rows forwards.
            if bits == 4 and mode == 2:
                rows = list(range(8))
            for k, y in enumerate(rows):
                pixels[y * 8:y * 8 + 8] = values[k * 8:k * 8 + 8]

        self.palettes[index] = palette
        self.selectors[index] = pixels
        self.opcodes[opcode] += 1
        return opcode

    def frame(self, payload: bytes, strict: bool = True) -> list[str]:
        warnings = []
        self.last_consumed = 2
        reader = Reader(payload, 2)
        try:
            bitmap = reader.take(self.count // 8)
        except DamagedFrame as exc:
            if strict:
                raise
            return [str(exc)]
        self.last_consumed = reader.pos
        for i in range(self.count):
            if bitmap[i // 8] & (128 >> (i % 8)):
                start = reader.pos
                try:
                    self.block(reader, i)
                except DamagedFrame as exc:
                    if strict:
                        raise
                    warnings.append(f"block {i}, payload offset {start}: {exc}; "
                                    "retained this and remaining blocks")
                    return warnings
                self.last_consumed = reader.pos
        if reader.pos != len(payload):
            message = f"{len(payload) - reader.pos} trailing byte(s) in frame"
            if strict:
                raise DamagedFrame(message)
            warnings.append(message)
        return warnings

    def image(self) -> bytes:
        """Top-down, global 8-bit palette indices."""
        result = bytearray(self.width * self.height)
        for i, (pal, selectors) in enumerate(zip(self.palettes, self.selectors)):
            x, y = i // self.block_rows * 8, i % self.block_rows * 8
            block = selectors.translate(bytes(pal) + bytes(240))
            for row in range(8):
                at = (y + row) * self.width + x
                result[at:at + 8] = block[row * 8:row * 8 + 8]
        return bytes(result)


@dataclass
class Chunk:
    tag: bytes
    offset: int
    declared_size: int
    payload: bytes


class Movie:
    """Parse only declared chunk boundaries; never search for guessed markers."""
    TAGS = {b"PCFM", b"SPAL", b"FRAM", b"EOFL", b"SHED", b"SAMP"}

    def __init__(self, data: bytes, fps: Fraction | None = None):
        if len(data) < 8 or data[:8] not in (b"PCFM\x06\0\0\0", b"SHED\x08\0\0\0"):
            raise FormatError("not a supported Novastorm PCFM animation signature")
        header_offset = 16 if data[:4] == b"SHED" else 0
        if data[header_offset:header_offset + 8] != b"PCFM\x06\0\0\0":
            raise FormatError("sound header is not followed by a PCFM animation header")
        if len(data) < header_offset + 14:
            raise FormatError("truncated PCFM header: dimensions cannot be recovered")
        self.declared_frames, self.width, self.height = struct.unpack_from("<3H", data, header_offset + 8)
        blocks = self.width // 8 * (self.height // 8)
        if not self.width or not self.height or self.width % 8 or self.height % 8 or blocks % 8:
            raise FormatError("invalid PCFM geometry: need whole 8x8 blocks and whole bitmap bytes")
        if self.width * self.height > 16_777_216:
            raise FormatError("image exceeds the converter's 16-megapixel resource limit")
        self.sample_rate = 0
        self.samples_per_frame = 0
        self.time_constant = None
        if header_offset:
            self.time_constant, self.samples_per_frame = struct.unpack_from("<2I", data, 8)
            if self.time_constant > 255 or not self.samples_per_frame:
                raise FormatError("unsupported SHED parameters (8-bit mono PCM time-constant profile required)")
            divisor = 256 - self.time_constant
            self.sample_rate = (1_000_000 + divisor // 2) // divisor
        self.fps = fps or (Fraction(self.sample_rate, self.samples_per_frame)
                           if self.sample_rate else Fraction(14))
        if self.fps <= 0 or self.fps.numerator > 0xFFFFFFFF or self.fps.denominator > 0xFFFFFFFF:
            raise FormatError("frame rate is outside AVI's positive 32-bit rational range")
        self.warnings = []
        self.chunks = []
        self.frames = 0
        self.audio_bytes = 0
        self.file_bytes = len(data)
        self.frame_audit = []
        self.chunk_counts = Counter()
        offset, ended, palette_seen = 0, False, False
        while offset < len(data):
            if len(data) - offset < 8:
                self.warnings.append(f"truncated chunk header at byte {offset}; {len(data)-offset} bytes unavailable to decoding")
                break
            tag, size = struct.unpack_from("<4sI", data, offset)
            if tag not in self.TAGS:
                raise FormatError(f"unsupported chunk {tag!r} at byte {offset}; no AVI written")
            payload = data[offset + 8:min(offset + 8 + size, len(data))]
            chunk = Chunk(tag, offset, size, payload)
            self.chunks.append(chunk)
            self.chunk_counts[tag.decode("ascii")] += 1
            if tag == b"PCFM" and offset != header_offset:
                raise FormatError("multiple PCFM headers are not a supported stream")
            if tag == b"SHED" and offset != 0:
                raise FormatError("SHED must precede PCFM")
            if tag == b"SPAL":
                if len(payload) < 4:
                    self.warnings.append(f"truncated SPAL at byte {offset}; retained previous colors")
                else:
                    first, count = struct.unpack_from("<2H", payload)
                    if first + count > 256:
                        raise FormatError("SPAL range exceeds the 256-entry VGA palette")
                    if size != 4 + 3 * count:
                        self.warnings.append(f"SPAL at byte {offset}: size does not match its entry count; using complete RGB triplets")
                    palette_seen = True
            elif tag == b"FRAM":
                if not palette_seen:
                    raise FormatError("FRAM precedes a usable SPAL; global colors cannot be recovered")
                self.frames += 1
            elif tag == b"SAMP":
                if not self.sample_rate:
                    raise FormatError("SAMP without SHED: audio timing is unspecified")
                self.audio_bytes += len(payload)
                if len(payload) != self.samples_per_frame:
                    self.warnings.append(f"SAMP at byte {offset}: {len(payload)} bytes instead of {self.samples_per_frame}; preserving available audio")
            elif tag == b"EOFL":
                ended = True
                if size:
                    self.warnings.append(f"nonempty EOFL at byte {offset}; ignored its {len(payload)} payload bytes")
                if offset + 8 + size < len(data):
                    self.warnings.append(f"{len(data)-offset-8-size} bytes follow EOFL; ignored")
                break
            if len(payload) < size:
                self.warnings.append(f"truncated {tag.decode()} at byte {offset}: {len(payload)}/{size} payload bytes available")
                break
            offset += 8 + size
        if not ended:
            self.warnings.append("missing EOFL; stopped at the last available chunk boundary")
        if not self.frames:
            raise FormatError("no recoverable FRAM chunks")
        if self.frames != self.declared_frames:
            self.warnings.append(f"PCFM declares {self.declared_frames} frames; preserving {self.frames} available frames")

    def events(self, audit: bool = False):
        decoder = Decoder(self.width, self.height)
        palette = bytearray(768)
        defined = set()
        frame_number = 0
        for chunk in self.chunks:
            p = chunk.payload
            if chunk.tag == b"SPAL" and len(p) >= 4:
                first, count = struct.unpack_from("<2H", p)
                count = min(count, (len(p) - 4) // 3)
                values = p[4:4 + 3 * count]
                if audit and any(c > 63 for c in values):
                    self.warnings.append(f"SPAL at byte {chunk.offset}: upper component bits discarded as by the VGA DAC")
                # Expand the VGA six-bit range with bit replication.
                palette[first * 3:(first + count) * 3] = bytes(((v & 63) << 2) | ((v & 63) >> 4) for v in values)
                defined.update(range(first, first + count))
            elif chunk.tag == b"FRAM":
                messages = decoder.frame(p, strict=False)
                serial = int.from_bytes(p[:2], "little") if len(p) >= 2 else None
                if serial != frame_number:
                    messages.append(f"frame number {serial}, expected {frame_number}; preserved physical order")
                if audit:
                    indices = decoder.image()
                    undefined = sorted(set(indices) - defined)
                    if undefined:
                        messages.append(f"undefined global palette indices {undefined}; rendered black")
                    self.warnings.extend(f"frame {frame_number} at byte {chunk.offset}: {m}" for m in messages)
                    self.frame_audit.append(dict(frame=frame_number, serial=serial, offset=chunk.offset,
                                                payload_bytes=len(p), decoded_payload_bytes=min(decoder.last_consumed, len(p)),
                                                warnings=messages))
                yield "video", decoder, bytes(palette)
                frame_number += 1
            elif chunk.tag == b"SAMP":
                yield "audio", p, None
        if audit:
            self.opcodes = dict(sorted(decoder.opcodes.items()))

    def validate(self):
        for _ in self.events(audit=True):
            pass

    def diagnostics(self) -> dict:
        return dict(format="Novastorm PCFM", width=self.width, height=self.height,
                    frames=self.frames, declared_frames=self.declared_frames,
                    fps=str(self.fps), timing="external nominal 14 fps or explicit override" if not self.sample_rate
                    else "rounded PCM sample rate / SHED samples per frame, unless overridden",
                    sample_rate=self.sample_rate, audio_bytes=self.audio_bytes,
                    input_bytes=self.file_bytes, warnings=self.warnings,
                    opcodes={f"{k:02x}": v for k, v in self.opcodes.items()},
                    chunks=[dict(type=c.tag.decode(), offset=c.offset, declared_size=c.declared_size,
                                 available_size=len(c.payload)) for c in self.chunks], frames_detail=self.frame_audit)


def riff_chunk(tag: bytes, data: bytes) -> bytes:
    return tag + struct.pack("<I", len(data)) + data + (b"\0" if len(data) & 1 else b"")


def riff_list(tag: bytes, data: bytes) -> bytes:
    return riff_chunk(b"LIST", tag + data)


def stream_header(kind: bytes, handler: bytes, scale: int, rate: int, length: int,
                  buffer: int, sample_size: int, width: int = 0, height: int = 0) -> bytes:
    return struct.pack("<4s4sIHH8I4h", kind, handler, 0, 0, 0, 0, scale, rate, 0,
                       length, buffer, 0xFFFFFFFF, sample_size, 0, 0, width, height)


def write_avi(movie: Movie, destination: Path):
    """Write lossless BGR24 + optional unsigned PCM directly, with idx1."""
    w, h = movie.width, movie.height
    if w > 32767 or h > 32767:
        raise FormatError("dimensions exceed the signed AVI stream rectangle fields")
    frame_size = ((w * 3 + 3) & ~3) * h
    fps = movie.fps
    has_audio = bool(movie.audio_bytes)
    avih = struct.pack("<14I", max(1, round(1_000_000 / fps)),
                       min(0xFFFFFFFF, int(frame_size * fps) + movie.sample_rate),
                       0, 0x10, movie.frames, 0, 1 + has_audio, frame_size, w, h, 0, 0, 0, 0)
    video = riff_chunk(b"strh", stream_header(b"vids", b"DIB ", fps.denominator,
                       fps.numerator, movie.frames, frame_size, 0, w, h))
    video += riff_chunk(b"strf", struct.pack("<IiiHH6I", 40, w, h, 1, 24, 0, frame_size, 0, 0, 0, 0))
    hdrl = riff_chunk(b"avih", avih) + riff_list(b"strl", video)
    if has_audio:
        audio = riff_chunk(b"strh", stream_header(b"auds", bytes(4), 1, movie.sample_rate,
                           movie.audio_bytes, movie.samples_per_frame, 1))
        audio += riff_chunk(b"strf", struct.pack("<HHIIHH", 1, 1, movie.sample_rate, movie.sample_rate, 1, 8))
        hdrl += riff_list(b"strl", audio)
    hdrl = riff_list(b"hdrl", hdrl)
    audio_chunks = [c for c in movie.chunks if c.tag == b"SAMP" and c.payload]
    movi_size = 4 + movie.frames * (8 + frame_size)
    movi_size += sum(8 + len(c.payload) + (len(c.payload) & 1) for c in audio_chunks)
    index_size = 16 * (movie.frames + len(audio_chunks))
    riff_size = 4 + len(hdrl) + 8 + movi_size + 8 + index_size
    if riff_size > 0xFFFFFFFF:
        raise FormatError("output exceeds classic AVI's 4 GiB limit; OpenDML is not implemented")
    index = bytearray()
    with destination.open("wb") as output:
        os.fchmod(output.fileno(), os.fstat(output.fileno()).st_mode | 0o440)
        output.write(b"RIFF" + struct.pack("<I", riff_size) + b"AVI " + hdrl)
        output.write(b"LIST" + struct.pack("<I", movi_size) + b"movi")
        relative = 4
        for kind, data, palette in movie.events():
            if kind == "video":
                indices = data.image()
                # Translation tables keep per-pixel work in the standard library's C loops.
                red = indices.translate(palette[0::3])
                green = indices.translate(palette[1::3])
                blue = indices.translate(palette[2::3])
                pixels = bytearray(frame_size)
                stride = ((w * 3 + 3) & ~3)
                for y in range(h):
                    start = (h - 1 - y) * stride
                    src = y * w
                    pixels[start:start + w * 3:3] = blue[src:src + w]
                    pixels[start + 1:start + w * 3:3] = green[src:src + w]
                    pixels[start + 2:start + w * 3:3] = red[src:src + w]
                tag, payload = b"00db", pixels
            else:
                if not data:
                    continue
                tag, payload = b"01wb", data
            output.write(riff_chunk(tag, payload))
            index.extend(struct.pack("<4sIII", tag, 0x10, relative, len(payload)))
            relative += 8 + len(payload) + (len(payload) & 1)
        output.write(riff_chunk(b"idx1", index))


def positive_rate(text: str) -> Fraction:
    try:
        value = Fraction(text)
        if value > 0:
            return value
    except (ValueError, ZeroDivisionError):
        pass
    raise argparse.ArgumentTypeError("expected a positive frame rate, such as 14 or 30000/1001")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputFile", type=Path)
    parser.add_argument("-verbose", "--verbose", action="store_true", help="also write OUTPUT.avi.json diagnostics")
    parser.add_argument("--fps", type=positive_rate, help="external playback rate; silent default: nominal 14 fps")
    args = parser.parse_args(argv)
    try:
        def same_path(a, b):
            return a.resolve() == b.resolve() or (a.exists() and b.exists() and os.path.samefile(a, b))

        if same_path(args.inputFile, args.outputFile):
            raise FormatError("input and output must be different files")
        diagnostics = Path(str(args.outputFile) + ".json")
        if args.verbose and (same_path(diagnostics, args.inputFile) or same_path(diagnostics, args.outputFile)):
            raise FormatError("verbose sidecar must be separate from the input and AVI")
        with args.inputFile.open("rb") as source:
            signature = source.read(24)
            if signature[:8] not in (b"PCFM\x06\0\0\0", b"SHED\x08\0\0\0"):
                raise FormatError("not a supported Novastorm animation signature")
            data = signature + source.read()
        movie = Movie(data, args.fps)
        movie.validate()
        write_avi(movie, args.outputFile)
        for message in movie.warnings:
            print(f"warning: {message}", file=sys.stderr)
        if args.verbose:
            diagnostics.write_text(json.dumps(movie.diagnostics(), indent=2) + "\n", encoding="utf-8")
            diagnostics.chmod(diagnostics.stat().st_mode | 0o440)
            print(f"{movie.frames} frames, {movie.width}x{movie.height}, {movie.fps} fps; "
                  f"{movie.audio_bytes} audio bytes; {len(movie.warnings)} warning(s)", file=sys.stderr)
        return 0
    except (FormatError, OSError, OverflowError, struct.error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

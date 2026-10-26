#!/usr/bin/env python3
# Vibe coded by Codex
"""Decode HP palmtop EVA3/EVA5 to lossless AVI using only the Python stdlib.

Usage: python3 evaVideo.py inputFile outputFile
See evaVideo.txt for the on-disk grammar and explicit corruption recovery rules.
"""

import argparse
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import os
from pathlib import Path
import struct
import sys
import tempfile


WIDTH, HEIGHT = 96, 92              # Constants of the original EVA profile.
PACKED_SIZE = WIDTH * HEIGHT // 4
GRAY_TABLE = tuple(bytes(((b >> s) & 3) * 85 for s in (6, 4, 2, 0))
                   for b in range(256))
PCM_TABLES = {
    0: tuple(bytes([b]) for b in range(256)),
    1: tuple(bytes((b & 240, (b & 15) << 4)) for b in range(256)),
    2: tuple(bytes(((b >> s) & 3) << 6 for s in (6, 4, 2, 0))
             for b in range(256)),
}


class EVAError(Exception):
    """Unrecognized, unsupported, or unrecoverable input; no output is committed."""


@dataclass(frozen=True)
class Header:
    version: int
    comment: bytes
    frames: int
    fps: Fraction
    pcm_format: int | None
    sample_rate: int
    pcm_bytes: int
    raw: bytes

    @property
    def samples_per_frame(self):
        return self.pcm_bytes * (1 << self.pcm_format) if self.version == 5 else 0


def unpack_pcm(data, pcm_format):
    """Unsigned PCM; packed samples are most significant first and left aligned."""
    if pcm_format == 0:
        return data
    return b"".join(map(PCM_TABLES[pcm_format].__getitem__, data))


def unpack_pixels(packed):
    """Top-down 8-bit gray; there are four 2-bit pixels per input byte."""
    return b"".join(map(GRAY_TABLE.__getitem__, packed))


def expand_image(payload, previous, first=False):
    """Return (packed image, opcode histogram, warnings, literal byte count).

    No opcode search or inferred frame boundaries. On damage, apply only writes
    inside the known image and preserve the previous values for missing pixels.
    """
    out = bytearray(previous)
    counts = Counter()
    problems = set()
    src = dst = literals = 0
    while src < len(payload):
        control = payload[src]
        src += 1
        kind = control >> 6
        counts[kind] += 1
        skip = copy = repeat = 0
        if kind == 0:
            skip, copy = (control >> 3) & 7, control & 7
        elif kind == 1:
            skip = control & 63
        elif kind == 2:
            copy = control & 63
        else:
            skip, repeat = (control >> 3) & 7, control & 7
        if first and skip:
            problems.add("first frame references an undefined previous image; black used")
        dst += skip
        if dst + copy + repeat > len(out):
            problems.add("image operation exceeds the raster; out-of-bounds writes discarded")
        if copy:
            available = min(copy, len(payload) - src)
            inside = max(0, min(available, len(out) - dst))
            out[dst:dst + inside] = payload[src:src + inside]
            src += available
            literals += available
            dst += available
            if available != copy:
                problems.add("truncated literal run; missing pixels retained")
                break
        if repeat:
            if dst == 0:
                problems.add("repeat has no preceding byte; affected pixels retained")
            elif dst <= len(out):
                inside = min(repeat, len(out) - dst)
                out[dst:dst + inside] = bytes([out[dst - 1]]) * inside
            dst += repeat
    if dst < len(out):
        problems.add(f"image ends at byte {dst} of {len(out)}; remaining pixels retained")
    return bytes(out), counts, sorted(problems), literals


class EVAReader:
    """Sequential parser with an exhaustive, nonoverlapping byte-range ledger."""

    def __init__(self, stream):
        self.stream = stream
        self.warnings = []
        self.spans = []
        self.opcodes = Counter()
        self.literal_bytes = 0
        self.frames_read = 0
        self.header = self._header()

    def _read(self, amount, role, frame=None):
        start = self.stream.tell()
        data = self.stream.read(amount)
        if data:
            span = {"offset": start, "length": len(data), "role": role}
            if frame is not None:
                span["frame"] = frame
            self.spans.append(span)
        return data

    def _header(self):
        magic = self._read(4, "signature")
        if magic not in (b"EVA3", b"EVA5"):
            raise EVAError("not supported HP palmtop EVA3/EVA5 (exact signature required)")
        # Comments are opaque bytes. Neither their encoding nor their contents
        # are used to identify the format or select decoding parameters.
        comment = bytearray()
        start = self.stream.tell()
        while True:
            block = self.stream.read(4096)
            marker = block.find(b"\x1a")
            if marker >= 0:
                comment.extend(block[:marker])
                self.stream.seek(marker + 1 - len(block), 1)
                break
            comment.extend(block)
            if not block:
                raise EVAError("EVA header is truncated: no comment terminator")
        if comment:
            self.spans.append({"offset": start, "length": len(comment), "role": "comment"})
        self.spans.append({"offset": start + len(comment), "length": 1,
                           "role": "comment terminator"})
        version = magic[3] - 48
        fields = [("frame count", 2)]
        if version == 3:
            fields += [("frames per second", 1), ("reserved", 1)]
        else:
            fields += [("width", 2), ("height", 2), ("bits per pixel", 1),
                       ("display aspect", 1), ("PCM format", 1),
                       ("PCM sample rate", 2), ("PCM bytes per frame", 2), ("reserved", 1)]
        raw = bytearray(magic + comment + b"\x1a")
        values = {}
        for name, size in fields:
            value = self._read(size, name)
            if len(value) != size:
                raise EVAError(f"EVA header is truncated in {name}; cannot recover framing")
            raw.extend(value)
            values[name] = int.from_bytes(value, "little")
        if values["reserved"]:
            self.warnings.append("nonzero reserved header byte; preserved but not interpreted")
        if version == 3:
            fps = values["frames per second"]
            if not fps:
                raise EVAError("EVA3 frame rate is zero; timing cannot be recovered without guessing")
            return Header(3, bytes(comment), values["frame count"], Fraction(fps),
                          None, 0, 0, bytes(raw))
        profile = tuple(values[k] for k in ("width", "height", "bits per pixel", "display aspect"))
        if profile != (WIDTH, HEIGHT, 2, 0x18):
            raise EVAError(f"unsupported EVA5 raster profile {profile}; expected (96, 92, 2, 24)")
        fmt = values["PCM format"]
        if fmt not in PCM_TABLES:
            raise EVAError(f"unsupported EVA5 PCM format {fmt}; supported: 0, 1, 2")
        rate, length = values["PCM sample rate"], values["PCM bytes per frame"]
        if not rate or not length:
            raise EVAError("zero PCM rate/length; EVA5 frame timing cannot be recovered without guessing")
        return Header(5, bytes(comment), values["frame count"],
                      Fraction(rate, length * (1 << fmt)), fmt, rate, length, bytes(raw))

    def frames(self):
        """Yield (top-down packed video, unsigned 8-bit PCM) for each recoverable frame."""
        h = self.header
        previous = bytes(PACKED_SIZE)
        for index in range(h.frames):
            frame = index + 1
            if h.version == 3:
                packed = self._read(PACKED_SIZE, "raw video", frame)
                if not packed:
                    self.warnings.append(f"EOF before frame {frame}; absent frames omitted")
                    break
                if len(packed) != PACKED_SIZE:
                    self.warnings.append(f"frame {frame}: truncated raw image; missing pixels retained")
                    packed += previous[len(packed):]
                pcm = b""
                final = self.spans[-1]["length"] != PACKED_SIZE
            else:
                audio = self._read(h.pcm_bytes, "packed PCM", frame)
                if not audio:
                    self.warnings.append(f"EOF before frame {frame}; absent frames omitted")
                    break
                pcm = unpack_pcm(audio, h.pcm_format)
                final = len(audio) != h.pcm_bytes
                if final:
                    self.warnings.append(f"frame {frame}: truncated PCM; missing samples filled with silence")
                    pcm += b"\x80" * (h.samples_per_frame - len(pcm))
                size_bytes = self._read(2, "compressed image length", frame)
                if len(size_bytes) != 2:
                    self.warnings.append(f"frame {frame}: missing image length; previous image retained")
                    packed, final = previous, True
                else:
                    size = int.from_bytes(size_bytes, "little")
                    payload = self._read(size, "compressed video", frame)
                    packed, counts, issues, literals = expand_image(payload, previous, index == 0)
                    self.opcodes.update(counts)
                    self.literal_bytes += literals
                    self.warnings.extend(f"frame {frame}: {issue}" for issue in issues)
                    if len(payload) != size:
                        self.warnings.append(f"frame {frame}: compressed payload truncated at EOF")
                        final = True
            previous = packed
            self.frames_read += 1
            yield packed, pcm
            if final:
                if frame < h.frames:
                    self.warnings.append(f"EOF: {h.frames - frame} wholly absent frame(s) omitted")
                break
        # There is no trailer in this format. Do not search extra bytes for
        # plausible frames or reinterpret them as another stream.
        extra_start = self.stream.tell()
        extra_size = 0
        while True:
            block = self.stream.read(65536)
            if not block:
                break
            extra_size += len(block)
        if extra_size:
            self.spans.append({"offset": extra_start, "length": extra_size, "role": "invalid trailing data"})
            self.warnings.append(f"{extra_size} unexpected trailing byte(s) after declared frames; not decoded")

    def audit(self):
        counts = Counter()
        offset = 0
        for span in self.spans:
            if span["offset"] != offset:
                raise EVAError("internal error: byte accounting is not contiguous")
            offset += span["length"]
            counts[span["role"]] += span["length"]
        h = self.header
        return {"version": f"EVA{h.version}", "comment_hex": h.comment.hex(),
                "declared_frames": h.frames, "decoded_frames": self.frames_read,
                "width": WIDTH, "height": HEIGHT, "display_aspect": "3:2",
                "fps": str(h.fps), "duration_seconds": float(self.frames_read / h.fps),
                "audio_bits": (8 >> h.pcm_format) if h.version == 5 else None,
                "audio_sample_rate": h.sample_rate, "audio_samples_per_frame": h.samples_per_frame,
                "bytes_accounted": offset, "byte_counts": dict(counts),
                "opcodes": {str(k): self.opcodes[k] for k in range(4)},
                "literal_bytes": self.literal_bytes, "warnings": self.warnings,
                "spans": self.spans}


def chunk(tag, payload):
    return tag + struct.pack("<I", len(payload)) + payload + b"\0" * (len(payload) & 1)


def list_chunk(kind, payload):
    return chunk(b"LIST", kind + payload)


def stream_header(kind, handler, scale, rate, length, buffer_size, sample_size, rectangle=(0, 0, 0, 0)):
    return struct.pack("<4s4sIHH8I4h", kind, handler, 0, 0, 0, 0, scale, rate,
                       0, length, buffer_size, 0xffffffff, sample_size, *rectangle)


class AVIWriter:
    """Classic indexed AVI: uncompressed 8-bit gray DIB + optional PCM_U8."""

    def __init__(self, stream, header):
        self.stream, self.header = stream, header
        self.frames = self.audio_samples = 0
        self.index = bytearray()
        self.header_bytes = self._headers()
        stream.write(b"RIFF\0\0\0\0AVI " + self.header_bytes)
        # Preserve the complete source header, including all opaque comment bytes.
        stream.write(chunk(b"evah", header.raw))
        self.movi_start = stream.tell()
        stream.write(b"LIST\0\0\0\0movi")

    def _headers(self):
        h = self.header
        frame_size = WIDTH * HEIGHT  # Width is already DWORD aligned.
        microseconds = (1000000 * h.fps.denominator + h.fps.numerator // 2) // h.fps.numerator
        max_rate = (frame_size * h.fps.numerator + h.fps.denominator - 1) // h.fps.denominator
        max_rate += h.sample_rate
        main = struct.pack("<14I", microseconds, max_rate, 0,
                           0x110 if h.version == 5 else 0x10, self.frames, 0,
                           2 if h.version == 5 else 1,
                           max(frame_size, h.samples_per_frame), WIDTH, HEIGHT, 0, 0, 0, 0)
        video = chunk(b"strh", stream_header(b"vids", b"DIB ", h.fps.denominator,
                      h.fps.numerator, self.frames, frame_size, 0, (0, 0, WIDTH, HEIGHT)))
        bitmap = struct.pack("<IiiHHIIiiII", 40, WIDTH, HEIGHT, 1, 8, 0,
                             frame_size, 0, 0, 256, 256)
        palette = b"".join(bytes((g, g, g, 0)) for g in range(256))
        video += chunk(b"strf", bitmap + palette)
        # vprp carries the nominal 3:2 DISPLAY aspect, retaining the stored raster.
        video += chunk(b"vprp", struct.pack("<17I", 0, 0, 0, WIDTH, HEIGHT,
                        (3 << 16) | 2, WIDTH, HEIGHT, 1,
                        HEIGHT, WIDTH, HEIGHT, WIDTH, 0, 0, 0, 0))
        streams = list_chunk(b"strl", video)
        if h.version == 5:
            audio = chunk(b"strh", stream_header(b"auds", b"\0" * 4, 1,
                          h.sample_rate, self.audio_samples, h.samples_per_frame, 1))
            audio += chunk(b"strf", struct.pack("<HHIIHH", 1, 1, h.sample_rate,
                                               h.sample_rate, 1, 8))
            streams += list_chunk(b"strl", audio)
        return list_chunk(b"hdrl", chunk(b"avih", main) + streams)

    def _media_chunk(self, tag, data):
        # Classic RIFF uses 32-bit sizes. Check before writing any oversized data.
        if self.stream.tell() + len(data) + len(self.index) + 64 > 0xffffffff:
            raise EVAError("output exceeds classic AVI's 4 GiB limit")
        offset = self.stream.tell() - (self.movi_start + 8)
        self.index.extend(struct.pack("<4sIII", tag, 0x10, offset, len(data)))
        self.stream.write(chunk(tag, data))

    def add(self, packed, pcm):
        pixels = unpack_pixels(packed)
        bottom_up = b"".join(pixels[y * WIDTH:(y + 1) * WIDTH]
                             for y in range(HEIGHT - 1, -1, -1))
        self._media_chunk(b"00db", bottom_up)
        if self.header.version == 5:
            self._media_chunk(b"01wb", pcm)
            self.audio_samples += len(pcm)
        self.frames += 1

    def finish(self):
        if not self.frames:
            raise EVAError("no recoverable frames; no AVI produced")
        end_movi = self.stream.tell()
        self.stream.write(chunk(b"idx1", bytes(self.index)))
        end = self.stream.tell()
        if end - 8 > 0xffffffff:
            raise EVAError("output exceeds classic AVI's 4 GiB limit")
        self.stream.seek(4)
        self.stream.write(struct.pack("<I", end - 8))
        self.stream.seek(12)
        headers = self._headers()
        if len(headers) != len(self.header_bytes):
            raise EVAError("internal error: AVI header size changed")
        self.stream.write(headers)
        self.stream.seek(self.movi_start + 4)
        self.stream.write(struct.pack("<I", end_movi - self.movi_start - 8))
        self.stream.seek(end)


def convert(input_file, output_file):
    """Convert atomically and return a byte audit. Never modify the input."""
    source, destination = Path(input_file), Path(output_file)
    if source.resolve() == destination.resolve() or (
            destination.exists() and os.path.samefile(source, destination)):
        raise EVAError("input and output refer to the same file")
    temporary = None
    try:
        with source.open("rb") as stream:
            reader = EVAReader(stream)  # Reject unsupported profiles before creating any file.
            if not reader.header.frames:
                raise EVAError("header declares no frames; no AVI produced")
            with tempfile.NamedTemporaryFile(mode="w+b", prefix=".eva-", suffix=".avi",
                                             dir=destination.parent, delete=False) as output:
                temporary = Path(output.name)
                writer = AVIWriter(output, reader.header)
                video_hash, audio_hash = hashlib.sha256(), hashlib.sha256()
                for packed, pcm in reader.frames():
                    writer.add(packed, pcm)
                    video_hash.update(unpack_pixels(packed))
                    audio_hash.update(pcm)
                writer.finish()
                audit = reader.audit()
                audit["decoded_gray_sha256"] = video_hash.hexdigest()
                audit["decoded_pcm_u8_sha256"] = audio_hash.hexdigest()
                output.flush()
                os.fsync(output.fileno())
                os.fchmod(output.fileno(), 0o664)
        os.replace(temporary, destination)
        temporary = None
        return audit
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inputFile")
    parser.add_argument("outputFile")
    args = parser.parse_args(argv)
    try:
        audit = convert(args.inputFile, args.outputFile)
    except (EVAError, OSError, OverflowError, struct.error) as error:
        print(f"evaVideo: {error}", file=sys.stderr)
        return 1
    for warning in audit["warnings"]:
        print(f"evaVideo: warning: {warning}", file=sys.stderr)
    audio = f", mono {audit['audio_sample_rate']} Hz audio" if audit["audio_sample_rate"] else ", no audio"
    print(f"{audit['version']}: {audit['decoded_frames']} frames, {audit['fps']} fps{audio}; "
          f"accounted for {audit['bytes_accounted']} input bytes -> {args.outputFile}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

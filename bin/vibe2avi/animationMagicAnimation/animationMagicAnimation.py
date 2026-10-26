#!/usr/bin/env python3
# Vibe coded by Codex
"""Decode Animation Magic ANI v1/v2 to lossless FFV1 + native PCM in AVI.

Usage: animationMagicAnimation.py inputFile outputFile
Requires Python 3.10+ and the ffmpeg command. No third-party Python modules.
Exit status: 0 = clean conversion, 2 = output with warnings, 1 = no new AVI.
See animationMagicAnimation.txt for the supported profile and open questions.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, field
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
from typing import Callable


class ANIError(ValueError):
    """Unrecognized, unsupported, or unrecoverable input; leave output alone."""


def u16(data: bytes, pos: int) -> int:
    return struct.unpack_from("<H", data, pos)[0]


def u32(data: bytes, pos: int) -> int:
    return struct.unpack_from("<I", data, pos)[0]


def recognize(data: bytes) -> int:
    """Reject unrelated files using only their first twenty bytes."""
    if len(data) < 20 or data[:4] != b"ANI " or data[8:12] != b"hdr ":
        raise ANIError("not an Animation Magic ANI file (ANI / hdr signatures absent)")
    version = u32(data, 16)
    if version not in (1, 2):
        raise ANIError(f"unsupported ANI version {version}")
    if u32(data, 12) != 1:
        raise ANIError("unsupported ANI header discriminator (only value 1 is understood)")
    return version


@dataclass
class Frame:
    number: int
    video_start: int
    video_end: int
    video_declared: int
    audio_start: int = 0
    audio_end: int = 0
    audio_declared: int | None = None
    decoded_pixels: int = 0
    complete_image: bool = False
    placeholder: bool = False
    token_counts: dict = field(default_factory=dict)


def decode_rle(payload: bytes, width: int, height: int,
               issue: Callable[[str], None] | None = None) -> tuple[bytes, int, dict]:
    """The input starts AFTER the four-byte frame prefix; never guess its start.

    Damage recovery initializes missing pixels to transparent index zero. A run
    crossing a scanline is rejected, not wrapped or assigned a guessed length.
    The returned pixel count is the size of the provably decoded prefix.
    """
    pixels = bytearray(width * height)
    size = len(pixels)
    cursor = pos = 0
    counts: Counter = Counter()

    def problem(message: str) -> None:
        if issue:
            issue(message)

    while pos < len(payload) and cursor < size:
        code = payload[pos]
        pos += 1
        if code < 0x80:
            counts["literal_bytes"] += 1
            pixels[cursor] = code
            cursor += 1
            continue
        counts["run_opcode_bytes"] += 1
        if pos == len(payload):
            counts["incomplete_run_opcodes"] += 1
            problem("RLE run opcode is missing its count byte")
            break
        count = payload[pos]
        pos += 1
        counts["run_count_bytes"] += 1
        remaining = width - cursor % width
        if count == 0:
            counts["end_of_line_runs"] += 1
            count = remaining
        if count > remaining:
            problem("RLE run crosses a scanline; stopped at its last valid pixel")
            break
        pixels[cursor:cursor + count] = bytes((code & 0x7f,)) * count
        cursor += count
    if cursor != size:
        problem(f"incomplete image: decoded {cursor} of {size} pixels; remainder transparent")
    if pos != len(payload):
        counts["uninterpreted_bytes"] = len(payload) - pos
        problem(f"{len(payload) - pos} video bytes remain after RLE decoding stopped")
    counts["consumed_bytes"] = pos
    return bytes(pixels), cursor, dict(counts)


class Animation:
    """Structural parser with exact byte accounting and explicit damage reports."""

    def __init__(self, data: bytes):
        self.data = data
        self.issues: list[str] = []
        self.spans: list[dict] = []
        self.frames: list[Frame] = []
        self.palette: list[tuple[int, int, int, int]] = []
        self._parse()

    def warn(self, message: str) -> None:
        self.issues.append(message)

    def span(self, start: int, end: int, role: str, frame: int | None = None) -> None:
        start, end = max(0, start), min(len(self.data), end)
        if end > start:
            item = {"offset": start, "length": end - start, "role": role}
            if frame is not None:
                item["frame"] = frame
            self.spans.append(item)

    def _parse(self) -> None:
        b = self.data
        self.version = recognize(b)
        hs = 46 if self.version == 1 else 50
        if len(b) < hs:
            raise ANIError("recognized ANI, but its fixed header is truncated")
        self.declared_size = u32(b, 4) + 4
        self.fps = u16(b, 20)
        self.sample_rate = u32(b, 22)
        self.channels = 1 if self.version == 1 else u16(b, 26)
        self.bits = 8 if self.version == 1 else u16(b, 28)
        dim = 26 if self.version == 1 else 30
        self.width, self.height = u16(b, dim), u16(b, dim + 2)
        self.frame_count = u32(b, dim + 4)
        self.video_buffer = u32(b, dim + 8)
        self.audio_hint = u32(b, dim + 12)
        table_bytes = u32(b, dim + 16)
        if not self.width or not self.height or not self.fps:
            raise ANIError("recognized ANI has zero dimensions or zero frame rate")
        if self.width * self.height > (0x7fffffff // 3):
            raise ANIError("decoded image exceeds the supported 2 GiB raw frame size")
        if self.bits not in (8, 16) or self.channels not in (1, 2):
            raise ANIError(f"unsupported PCM layout: {self.channels} channels, {self.bits} bits")
        self.block_align = self.channels * (self.bits // 8)
        if self.declared_size != len(b):
            self.warn(f"file length {len(b)} differs from declared length {self.declared_size}")
        if table_bytes != 4 * self.frame_count:
            self.warn(f"offset table length {table_bytes} differs from frame count * 4")
        if table_bytes % 4:
            raise ANIError("recognized ANI has a fractional frame-offset entry")
        ps = hs + table_bytes
        if ps + 24 > len(b):
            raise ANIError("recognized ANI has a truncated index or palette header")
        self.span(0, hs, "fixed_header")
        self.span(hs, ps, "frame_offset_table")
        offsets = [u32(b, p) for p in range(hs, ps, 4)]
        if not offsets:
            raise ANIError("recognized ANI contains no frame offsets")
        if offsets[0] != 0 or any(x >= y for x, y in zip(offsets, offsets[1:])):
            raise ANIError("recognized ANI has an invalid/non-increasing frame index")
        # Use the stored table length to find the palette; do not scan for tags.
        if b[ps:ps + 4] != b"RIFF" or b[ps + 8:ps + 12] != b"PAL ":
            raise ANIError("recognized ANI has no RIFF PAL at the indexed palette position")
        palette_end = ps + 8 + u32(b, ps + 4)
        if palette_end > len(b) or palette_end < ps + 24:
            raise ANIError("recognized ANI has a truncated or invalid palette")
        self.span(ps, ps + 12, "palette_riff_header")
        pos = ps + 12
        found = False
        while pos < palette_end:
            if pos + 8 > palette_end:
                raise ANIError("truncated RIFF palette subchunk header")
            tag, size = b[pos:pos + 4], u32(b, pos + 4)
            end = pos + 8 + size
            if end + (size & 1) > palette_end:
                raise ANIError("palette subchunk extends beyond its RIFF container")
            if tag == b"data":
                if found or size < 4:
                    raise ANIError("invalid/duplicate palette data chunk")
                found = True
                if u16(b, pos + 8) != 0x0300:
                    raise ANIError("unsupported logical palette version")
                ncolors = u16(b, pos + 10)
                if not 1 <= ncolors <= 256 or size != 4 + 4 * ncolors:
                    raise ANIError("invalid logical palette size")
                self.span(pos, pos + 12, "palette_data_header")
                for j in range(ncolors):
                    at = pos + 12 + j * 4
                    color = tuple(b[at:at + 4])
                    if color[3] & ~7 or color[3] & 2:
                        raise ANIError("palette requires unsupported hardware-index/reserved flags")
                    self.palette.append(color)
                self.span(pos + 12, end, "palette_rgb_and_flags")
            elif tag == b"JUNK":
                self.span(pos, end, "riff_junk")
            else:
                raise ANIError(f"unsupported RIFF palette chunk {tag!r}")
            if size & 1:
                self.span(end, end + 1, "riff_alignment_byte")
            pos = end + (size & 1)
        if not found:
            raise ANIError("RIFF PAL has no data chunk")
        self.data_start = palette_end
        available_offsets = [o for o in offsets if palette_end + o < len(b)]
        if len(available_offsets) != len(offsets):
            self.warn(f"only {len(available_offsets)} of {len(offsets)} indexed frame records are present")
        for i, relative in enumerate(available_offsets):
            start = palette_end + relative
            boundary = min(palette_end + offsets[i + 1], len(b)) if i + 1 < len(offsets) else len(b)
            self._frame(i, start, boundary)
        if not self.frames:
            raise ANIError("recognized ANI has no recoverable video frames")
        if self.sample_rate == 0 and any(f.audio_end > f.audio_start for f in self.frames):
            raise ANIError("PCM is present but the audio sampling rate is zero")
        self.has_audio = self.sample_rate > 0 and any(f.audio_end > f.audio_start for f in self.frames)
        self._account_gaps()

    def _frame(self, number: int, start: int, boundary: int) -> None:
        b = self.data
        mark = lambda message: self.warn(f"frame {number}: {message}")
        if start + 4 > boundary:
            self.span(start, boundary, "truncated_video_size", number)
            mark("incomplete video-size field; no image can be recovered")
            # Only retain a placeholder if later indexed data exists.
            if boundary < len(b):
                self.frames.append(Frame(number, boundary, boundary, 0, placeholder=True))
            return
        size = u32(b, start)
        self.span(start, start + 4, "video_size", number)
        vs = start + 4
        ve = min(vs + size, boundary)
        f = Frame(number, vs, ve, size)
        self.frames.append(f)
        if size > self.video_buffer:
            mark(f"video size {size} exceeds the header buffer hint {self.video_buffer}")
        if ve < vs + size:
            mark(f"truncated video payload: {ve - vs} of {size} bytes present")
        if ve - vs < 4:
            self.span(vs, ve, "truncated_frame_prefix", number)
            mark("missing frame prefix; image replaced with transparent pixels")
            f.placeholder = True
        else:
            self.span(vs, vs + 4, "zero_frame_prefix_unresolved_semantics", number)
            if u32(b, vs) != 0:
                raise ANIError(f"frame {number}: nonzero video prefix is an unsupported variant")
            self.span(vs + 4, ve, "video_rle", number)
            pixels, f.decoded_pixels, f.token_counts = decode_rle(
                b[vs + 4:ve], self.width, self.height, mark)
            f.complete_image = f.decoded_pixels == self.width * self.height
            if pixels and max(pixels) >= len(self.palette):
                mark("image uses a missing palette entry; undefined colors rendered black")
        audio_header = vs + size
        if audio_header > boundary:
            mark("audio-size field and audio are unavailable")
            return
        if audio_header + 4 > boundary:
            self.span(audio_header, boundary, "truncated_audio_size", number)
            mark("incomplete audio-size field; no audio length inferred")
            return
        self.span(audio_header, audio_header + 4, "audio_size", number)
        audio_size = u32(b, audio_header)
        f.audio_declared = audio_size
        f.audio_start = audio_header + 4
        f.audio_end = min(f.audio_start + audio_size, boundary)
        self.span(f.audio_start, f.audio_end, "pcm_audio", number)
        if f.audio_end < f.audio_start + audio_size:
            mark(f"truncated audio payload: {f.audio_end - f.audio_start} of {audio_size} bytes present")
        if audio_size % self.block_align:
            mark("declared audio length ends within an interleaved PCM sample")
        if (f.audio_end - f.audio_start) % self.block_align:
            mark("partial interleaved PCM sample will be zero/silence-completed")
        if f.audio_end < boundary:
            self.span(f.audio_end, boundary, "uninterpreted_record_tail", number)
            mark(f"{boundary - f.audio_end} unexplained bytes follow audio")

    def _account_gaps(self) -> None:
        self.spans.sort(key=lambda s: s["offset"])
        end = 0
        gaps = []
        for s in self.spans:
            if s["offset"] < end:
                raise ANIError("internal byte-accounting error: overlapping fields")
            if s["offset"] > end:
                gaps.append((end, s["offset"]))
            end = s["offset"] + s["length"]
        if end < len(self.data):
            gaps.append((end, len(self.data)))
        for a, z in gaps:
            self.span(a, z, "uninterpreted_gap")
            self.warn(f"uninterpreted byte range [{a}, {z})")
        self.spans.sort(key=lambda s: s["offset"])

    def indexed_pixels(self, frame: Frame) -> bytes:
        if frame.placeholder:
            return bytes(self.width * self.height)
        return decode_rle(self.data[frame.video_start + 4:frame.video_end],
                          self.width, self.height)[0]

    def rgb_frames(self):
        # Index 0 is transparent; AVI is flattened over an explicitly black matte.
        palette = [(0, 0, 0, 0)] + self.palette[1:]
        palette += [(0, 0, 0, 0)] * (256 - len(palette))
        tables = [bytes(p[c] for p in palette) for c in range(3)]
        for f in self.frames:
            indices = self.indexed_pixels(f)
            rgb = bytearray(3 * len(indices))
            for c in range(3):
                rgb[c::3] = indices.translate(tables[c])
            yield bytes(rgb)

    def audio_parts(self):
        for i, f in enumerate(self.frames):
            if f.audio_declared is None:
                # No guessed duration is inserted for an absent length field.
                continue
            raw = self.data[f.audio_start:f.audio_end]
            if raw:
                yield raw
            missing = (-len(raw)) % self.block_align
            if missing:
                yield (b"\x80" if self.bits == 8 else b"\x00") * missing
            # If a damaged interior record has an explicit audio length, preserve
            # that declared interval. EOF truncation is NOT padded to full length.
            if i + 1 < len(self.frames) and f.audio_declared > len(raw) + missing:
                missing = f.audio_declared - len(raw) - missing
                missing += (-missing) % self.block_align
                yield (b"\x80" if self.bits == 8 else b"\x00") * missing

    def audit(self) -> dict:
        totals: Counter = Counter()
        for span in self.spans:
            totals[span["role"]] += span["length"]
        unknown = sum(n for role, n in totals.items() if role.startswith("uninterpreted"))
        unknown += sum(f.token_counts.get("uninterpreted_bytes", 0) for f in self.frames)
        return {
            "input_bytes": len(self.data),
            "input_sha256": hashlib.sha256(self.data).hexdigest(),
            "declared_bytes": self.declared_size,
            "version": self.version,
            "width": self.width, "height": self.height, "fps": self.fps,
            "declared_frames": self.frame_count, "output_frames": len(self.frames),
            "complete_images": sum(f.complete_image for f in self.frames),
            "partial_images": sum(not f.complete_image for f in self.frames),
            "sample_rate": self.sample_rate, "channels": self.channels, "bits": self.bits,
            "palette_entries": len(self.palette),
            "video_buffer_hint": self.video_buffer, "audio_chunk_hint": self.audio_hint,
            "source_pcm_bytes": sum(f.audio_end - f.audio_start for f in self.frames),
            "output_pcm_bytes": sum(map(len, self.audio_parts())),
            "accounted_bytes": sum(totals.values()),
            "uninterpreted_payload_bytes": unknown,
            "unresolved_constant_bytes": 4 + totals["zero_frame_prefix_unresolved_semantics"],
            "semantic_completeness": False,
            "issues": self.issues, "byte_categories": dict(totals), "byte_spans": self.spans,
            "frames": [vars(f) for f in self.frames],
        }


def convert(input_file: str | Path, output_file: str | Path) -> dict:
    """Validate first; publish output atomically only after ffmpeg succeeds."""
    source, target = Path(input_file), Path(output_file)
    if source.resolve() == target.resolve():
        raise ANIError("input and output paths must differ")
    with source.open("rb") as stream:
        prefix = stream.read(20)
        recognize(prefix)
        animation = Animation(prefix + stream.read())
    executable = shutil.which("ffmpeg")
    if executable is None:
        raise ANIError("ffmpeg is required on PATH (FFV1 encoder and AVI muxer)")
    if not target.parent.is_dir():
        raise ANIError(f"output directory does not exist: {target.parent}")
    with tempfile.TemporaryDirectory(prefix=".animation-magic-", dir=target.parent) as work:
        work = Path(work)
        output = work / "video.avi"
        args = [executable, "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
                "-f", "rawvideo", "-pixel_format", "rgb24", "-video_size",
                f"{animation.width}x{animation.height}", "-framerate", str(animation.fps),
                "-i", "pipe:0"]
        if animation.has_audio:
            audio = work / "audio.pcm"
            with audio.open("wb") as f:
                for part in animation.audio_parts():
                    f.write(part)
            args += ["-f", "u8" if animation.bits == 8 else "s16le", "-ar",
                     str(animation.sample_rate), "-ac", str(animation.channels),
                     "-i", str(audio), "-map", "0:v:0", "-map", "1:a:0",
                     "-c:a", "pcm_u8" if animation.bits == 8 else "pcm_s16le"]
        else:
            args += ["-map", "0:v:0", "-an"]
        args += ["-c:v", "ffv1", "-level", "3", "-pix_fmt", "bgr0", "-threads", "1",
                 "-f", "avi", str(output)]
        with (work / "ffmpeg.log").open("w+b") as log:
            process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                                       stderr=log)
            try:
                try:
                    for rgb in animation.rgb_frames():
                        process.stdin.write(rgb)
                    process.stdin.close()
                except BrokenPipeError:
                    # Read ffmpeg's diagnostic after it exits.
                    try:
                        process.stdin.close()
                    except BrokenPipeError:
                        pass
                code = process.wait()
                if code or not output.is_file() or output.stat().st_size == 0:
                    log.seek(0)
                    reason = log.read().decode("utf-8", "replace").strip()
                    raise ANIError(f"AVI encoding failed: {reason or code}")
            finally:
                if process.poll() is None:
                    process.kill()
                    process.wait()
            output.chmod(0o664)
            os.replace(output, target)
    return animation.audit()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputFile", type=Path)
    parser.add_argument("--audit-json", type=Path, help="optional byte-coverage and recovery report")
    args = parser.parse_args(argv)
    if args.audit_json and args.audit_json.resolve() in (args.inputFile.resolve(), args.outputFile.resolve()):
        parser.error("audit path must differ from input and output")
    try:
        report = convert(args.inputFile, args.outputFile)
        if args.audit_json:
            try:
                args.audit_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
                args.audit_json.chmod(0o664)
            except OSError as error:
                report["issues"].append(f"AVI created, but optional audit could not be written: {error}")
    except (ANIError, OSError, MemoryError, OverflowError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    for message in report["issues"]:
        print(f"warning: {message}", file=sys.stderr)
    print(f"Wrote {args.outputFile}: {report['output_frames']} frames, "
          f"{report['fps']} fps, {report['output_pcm_bytes']} PCM bytes")
    return 2 if report["issues"] else 0


if __name__ == "__main__":
    sys.exit(main())

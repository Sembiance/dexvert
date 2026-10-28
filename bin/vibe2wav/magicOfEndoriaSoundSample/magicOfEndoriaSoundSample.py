#!/usr/bin/env python3
# Vibe coded by Codex
"""Convert a standalone Magic of Endoria / Palladix SM8 sample to PCM WAV.

Usage: magicOfEndoriaSoundSample.py <inputFile> <outputDir> [-verbose]
Only the Python standard library is required. See the accompanying .txt for
the format, primary evidence, timing convention, and corruption policy.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import struct
import sys
import tempfile
from dataclasses import dataclass


SIGNATURE = b"SM8\x00"
HEADER = struct.Struct("<4sHHH")
PIT_HZ = 1_193_182
MAX_SAMPLES = 0xFFFF


class SampleError(ValueError):
    """An unrecognized, unsupported, or unrecoverable input."""


class NotTargetFormat(SampleError):
    """The exact standalone SM8 signature is absent."""


class UnsupportedSample(SampleError):
    """An SM8 representation is not an inline PCM sample file."""


class MalformedSample(SampleError):
    """The format is recognizable but essential data cannot be recovered."""


@dataclass(frozen=True)
class Sample:
    scale_marker: int
    declared_samples: int
    timer_divisor: int
    pcm: bytes
    trailing_bytes: int
    warnings: tuple[str, ...]

    @property
    def effective_divisor(self) -> int:
        # A zero reload value represents 65536 ticks on the 16-bit PC PIT.
        return self.timer_divisor or 65_536

    @property
    def sample_rate(self) -> int:
        # WAV rates are integers: round the nominal PIT rate to nearest Hz.
        divisor = self.effective_divisor
        return (PIT_HZ + divisor // 2) // divisor

    @property
    def nominal_rate(self) -> float:
        return PIT_HZ / self.effective_divisor


def parse_sample(data: bytes) -> Sample:
    """Parse the complete file before creating any output.

    No extension tests, signature searches, rate guesses, amplitude guesses,
    or padding/silence trimming are used. Trailing bytes are not decoded.
    """
    if data[:4] != SIGNATURE:
        raise NotTargetFormat("not a standalone SM8 file: expected 53 4d 38 00 at offset 0")
    if len(data) < HEADER.size:
        raise MalformedSample(
            f"SM8 header is truncated ({len(data)} of {HEADER.size} bytes); "
            "cannot determine the complete sample count and timer divisor"
        )

    _, scale_marker, count, divisor = HEADER.unpack_from(data)
    if scale_marker > 256:
        detail = (
            "the original driver uses 0xffxx for an in-memory external PCM address"
            if scale_marker >> 8 == 0xFF else
            "this is outside the documented inline PCM scaling-marker range"
        )
        raise UnsupportedSample(
            f"unsupported SM8 scaling marker 0x{scale_marker:04x}: {detail}; "
            "no standalone audio will be guessed"
        )
    if count == 0:
        raise MalformedSample(
            "SM8 declares zero samples; no nonempty audio extent can be recovered "
            "without inventing a sample count"
        )

    available = len(data) - HEADER.size
    recovered = min(count, available)
    if recovered == 0:
        raise MalformedSample("SM8 contains a complete header but no recoverable PCM bytes")
    warnings = []
    if available < count:
        warnings.append(
            f"truncated PCM: declared {count} samples, recovered {available}; "
            "missing samples were not synthesized"
        )
    trailing = max(0, available - count)
    if trailing:
        warnings.append(
            f"{trailing} trailing byte(s) after the declared PCM extent were excluded; "
            "SM8 has no trailer or concatenated-sample syntax"
        )

    # The driver records PREVIOUS scaling at +4. Scaling again is incorrect.
    return Sample(scale_marker, count, divisor,
                  data[HEADER.size:HEADER.size + recovered], trailing,
                  tuple(warnings))


def make_wav(sample: Sample) -> bytes:
    """Wrap the unchanged unsigned 8-bit mono PCM in a minimal RIFF/WAVE."""
    count = len(sample.pcm)
    pad = b"\x00" if count & 1 else b""
    rate = sample.sample_rate
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF", 36 + count + len(pad), b"WAVE",
        b"fmt ", 16, 1, 1, rate, rate, 1, 8,
        b"data", count,
    )
    return header + sample.pcm + pad


def describe_sample(data: bytes, sample: Sample) -> dict:
    """Return a byte accounting and conversion audit, for explicit verbose use."""
    end = HEADER.size + len(sample.pcm)
    regions = [
        {"offset": 0, "length": 4, "meaning": "SM8 NUL signature", "hex": data[:4].hex()},
        {"offset": 4, "length": 2, "meaning": "previous PCM scaling marker",
         "value": sample.scale_marker, "hex": data[4:6].hex()},
        {"offset": 6, "length": 2, "meaning": "declared PCM sample count",
         "value": sample.declared_samples, "hex": data[6:8].hex()},
        {"offset": 8, "length": 2, "meaning": "16-bit PIT reload divisor",
         "value": sample.timer_divisor, "hex": data[8:10].hex()},
        {"offset": 10, "length": len(sample.pcm), "meaning": "unsigned 8-bit mono PCM",
         "sha256": hashlib.sha256(sample.pcm).hexdigest()},
    ]
    if sample.trailing_bytes:
        regions.append({
            "offset": end, "length": sample.trailing_bytes,
            "meaning": "uninterpreted malformed trailing data; excluded from WAV",
            "sha256": hashlib.sha256(data[end:]).hexdigest(),
        })
    return {
        "format": "Palladix SM8 / Magic of Endoria sound sample",
        "input_bytes": len(data),
        "input_sha256": hashlib.sha256(data).hexdigest(),
        "header_bytes": HEADER.size,
        "scale_marker": sample.scale_marker,
        "scale_handling": "PCM already reflects any prescaling; no gain applied",
        "declared_samples": sample.declared_samples,
        "recovered_samples": len(sample.pcm),
        "timer_divisor": sample.timer_divisor,
        "effective_timer_divisor": sample.effective_divisor,
        "nominal_rate_numerator": PIT_HZ,
        "nominal_rate_denominator": sample.effective_divisor,
        "nominal_sample_rate_hz": sample.nominal_rate,
        "wav_sample_rate_hz": sample.sample_rate,
        "wav_rate_error_hz": sample.sample_rate - sample.nominal_rate,
        "wav_duration_seconds": len(sample.pcm) / sample.sample_rate,
        "wav_channels": 1,
        "wav_bits_per_sample": 8,
        "wav_alignment_pad_bytes": len(sample.pcm) & 1,
        "pcm_bytes_unchanged": True,
        "byte_regions": regions,
        "warnings": list(sample.warnings),
    }


def ensure_directory(directory: Path) -> None:
    """Create missing directories with owner/group read and traversal access."""
    missing = []
    current = directory
    while not current.exists():
        missing.append(current)
        if current.parent == current:
            break
        current = current.parent
    directory.mkdir(parents=True, exist_ok=True)
    for created in reversed(missing):
        created.chmod(stat.S_IMODE(created.stat().st_mode) | 0o750)


def atomic_write(path: Path, content: bytes) -> None:
    """Install a complete file with explicit owner/group readability."""
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fchmod(stream.fileno(), 0o644)
        os.replace(temporary, path)
    finally:
        if os.path.lexists(temporary):
            os.unlink(temporary)


def convert_file(input_file: Path, output_dir: Path, verbose: bool = False) -> tuple[Path, Sample]:
    """Convert exactly one SM8 stream; rejected inputs create no output files."""
    input_file, output_dir = Path(input_file), Path(output_dir)
    with input_file.open("rb") as source:
        # Reject unrelated files after four bytes, before reading the payload.
        prefix = source.read(4)
        if prefix != SIGNATURE:
            raise NotTargetFormat("not a standalone SM8 file: expected 53 4d 38 00 at offset 0")
        data = prefix + source.read()
    sample = parse_sample(data)
    wav = make_wav(sample)
    stem = input_file.stem or input_file.name
    wav_path = output_dir / f"{stem}.wav"
    json_path = output_dir / f"{stem}.json"
    destinations = [wav_path] + ([json_path] if verbose else [])
    for destination in destinations:
        if destination.resolve() == input_file.resolve() or (
            destination.exists() and os.path.samefile(destination, input_file)
        ):
            raise SampleError(f"output would overwrite the input file: {destination}")
        if destination.is_dir():
            raise SampleError(f"output path is an existing directory: {destination}")

    audit = None
    if verbose:
        audit = describe_sample(data, sample)
        audit.update({"input_file": str(input_file), "output_wav": str(wav_path)})
    # All format validation and serialization precedes any output creation.
    ensure_directory(output_dir)
    atomic_write(wav_path, wav)
    if audit is not None:
        atomic_write(json_path, (json.dumps(audit, indent=2, ensure_ascii=True) + "\n").encode("utf-8"))
    return wav_path, sample


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Convert one standalone Magic of Endoria / Palladix SM8 sample to WAV.",
        epilog="The destination may exist. Matching output filenames are replaced. "
               "Without -verbose, only the WAV is written.",
    )
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputDir", type=Path)
    parser.add_argument("-verbose", "--verbose", "-v", action="store_true",
                        help="also write a JSON byte/format audit and print conversion details")
    args = parser.parse_args(argv)
    try:
        path, sample = convert_file(args.inputFile, args.outputDir, args.verbose)
    except (SampleError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    for warning in sample.warnings:
        print(f"warning: {warning}", file=sys.stderr)
    if args.verbose:
        print(f"{path}: {len(sample.pcm)} samples, mono unsigned 8-bit PCM, "
              f"{sample.sample_rate} Hz (PIT {PIT_HZ}/{sample.effective_divisor})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

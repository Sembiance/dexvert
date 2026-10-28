#!/usr/bin/env python3
# Vibe coded by Codex
"""Extract KOEPAC voice archives to mono 16-bit PCM WAV (Python 3.10+).

Usage: koepacAudioArchive.py inputFile outputDir [-verbose]
See koepacAudioArchive.txt for the complete supported format and recovery rules.
Only Python's standard library is required. No external decoder/data is used.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
import wave

MAGIC = b"KOEPAC\0\0"
BLOCK_SAMPLES = 1024
SILENCE = b"\0" * (BLOCK_SAMPLES * 2)


def expand_code(code: int) -> int:
    """Exact KOEPAC quadratic companding, including its three exceptions."""
    if code == 0:
        return -32768
    if code == 128:
        return 0
    if code == 255:
        return 32767
    distance = code - 128
    magnitude = 2 * distance * distance - 1
    return -magnitude if distance < 0 else magnitude


PCM = tuple(struct.pack("<h", expand_code(code)) for code in range(256))
DELTA = tuple(-(code + 1) // 2 if code & 1 else code // 2
              for code in range(256))


class UnsupportedFormat(ValueError):
    """The input does not match the explicitly supported KOEPAC profile."""


class MalformedArchive(ValueError):
    """Identified KOEPAC, but no safe interpretation of essential data exists."""


@dataclass
class Entry:
    ordinal: int
    clip_id: int
    block_count: int
    offset: int
    limit: int = 0
    lengths: tuple[int, ...] = ()
    payload_offset: int = 0
    issues: list[str] = field(default_factory=list)
    skip_reason: str | None = None


@dataclass
class Archive:
    data: bytes
    declared_count: int
    data_offset: int
    sample_rate_field: int
    sample_rate: int
    entries: list[Entry]
    issues: list[str]
    unreferenced_ranges: list[tuple[int, int]]


def parse_archive(data: bytes) -> Archive:
    """Parse explicit offsets only; never scan for or guess an audio format."""
    if data[:8] != MAGIC:
        raise UnsupportedFormat("not KOEPAC: expected the exact 8-byte KOEPAC\\0\\0 signature")
    if len(data) < 32:
        raise MalformedArchive("truncated KOEPAC header; no clip index can be located")
    if any(data[8:16]) or any(data[28:32]):
        raise UnsupportedFormat(
            "KOEPAC with nonzero reserved header bytes: unsupported extension; "
            "their meaning is not defined by the supported profile")
    count, data_offset, rate_field = struct.unpack_from("<III", data, 16)
    rate = rate_field or 22050
    if rate > 0x7FFFFFFF:
        raise MalformedArchive("sample rate cannot be represented in a mono 16-bit WAV byte rate")
    issues: list[str] = []
    expected_index_end = 32 + 8 * count
    index_end = min(expected_index_end, len(data))
    if data_offset != expected_index_end:
        issues.append(f"data offset {data_offset} differs from index end {expected_index_end}")
        # An explicit start-of-data boundary prevents reading payload as records.
        if 32 <= data_offset < index_end:
            index_end = data_offset
    available_count = max(0, (index_end - 32) // 8)
    if available_count < count:
        issues.append(f"only {available_count} of {count} index records are accessible")
    entries = [Entry(i, *struct.unpack_from("<HHI", data, 32 + 8 * i))
               for i in range(available_count)]
    directory_end = 32 + 8 * available_count
    # A later explicit entry boundary also bounds recovery from a damaged length.
    offsets = sorted({e.offset for e in entries if directory_end <= e.offset <= len(data)})
    limits = {offset: offsets[i + 1] if i + 1 < len(offsets) else len(data)
              for i, offset in enumerate(offsets)}
    spans = [(0, directory_end)]
    seen_ids: set[int] = set()
    seen_offsets: set[int] = set()
    for entry in entries:
        if entry.clip_id in seen_ids:
            entry.issues.append("duplicate clip ID; index ordinal added to output name")
        seen_ids.add(entry.clip_id)
        if entry.offset < directory_end or entry.offset > len(data):
            entry.skip_reason = "clip offset lies in the header/index or beyond end of file"
            continue
        entry.limit = limits[entry.offset]
        if entry.offset in seen_offsets:
            entry.issues.append("shared clip offset; decoded separately for this index record")
        seen_offsets.add(entry.offset)
        entry.payload_offset = entry.offset + 2 * entry.block_count
        if entry.payload_offset > entry.limit:
            entry.skip_reason = "incomplete block-length table; payload start cannot be recovered"
            continue
        entry.lengths = struct.unpack_from(f"<{entry.block_count}H", data, entry.offset)
        declared_end = entry.payload_offset + sum(entry.lengths)
        spans.append((entry.offset, min(declared_end, entry.limit)))
        if declared_end > entry.limit:
            entry.issues.append(
                f"payload ends at {declared_end}, beyond its available boundary {entry.limit}; "
                "recoverable samples will be retained and missing samples replaced with silence")
    # Account for all bytes, including unreferenced bytes in malformed archives.
    cursor = 0
    unreferenced = []
    for start, end in sorted(spans):
        if start > cursor:
            unreferenced.append((cursor, start))
        cursor = max(cursor, end)
    if cursor < len(data):
        unreferenced.append((cursor, len(data)))
    for start, end in unreferenced:
        issues.append(f"unreferenced bytes [{start}, {end}); no audio interpretation is assigned")
    return Archive(data, count, data_offset, rate_field, rate, entries, issues, unreferenced)


def decode_block(payload: bytes, declared_size: int) -> tuple[bytes, int, str | None]:
    """Return PCM, bytes consumed, and an optional corruption diagnostic.

    Recovery preserves only completely decoded samples and zero-fills the rest.
    The caller advances by the declared size, not by bytes consumed here.
    """
    if declared_size == 0:
        return SILENCE, 0, None
    if declared_size == 1024:
        usable = payload[:1024]
        result = b"".join(map(PCM.__getitem__, usable))
        problem = None if len(usable) == 1024 else f"raw block truncated at {len(usable)} samples"
        return result + SILENCE[len(result):], len(usable), problem
    # Two samples at a time keeps nibble alignment explicit. Each escape takes
    # two additional nibbles, so every sample pair ends on a byte boundary.
    state = 0
    pos = 0
    codes = bytearray()
    adjust = DELTA
    try:
        for _ in range(BLOCK_SAMPLES // 2):
            bits = payload[pos]
            pos += 1
            code = bits & 15
            if code == 15:
                low = bits >> 4
                bits = payload[pos]
                pos += 1
                code = low | ((bits & 15) << 4)
            state = (state - adjust[code]) & 255
            codes.append(state)
            code = bits >> 4
            if code == 15:
                code = payload[pos]
                pos += 1
            state = (state - adjust[code]) & 255
            codes.append(state)
    except IndexError:
        problem = f"DPCM block ended after {len(codes)} of 1024 samples"
    else:
        problem = None
        if pos != declared_size:
            problem = f"DPCM block uses {pos} bytes but declares {declared_size}"
    result = b"".join(map(PCM.__getitem__, codes))
    return result + SILENCE[len(result):], pos, problem


def readable_directory(path: Path) -> None:
    """Create missing directories with user/group read and search permissions."""
    missing = []
    parent = path
    while not parent.exists():
        missing.append(parent)
        parent = parent.parent
    path.mkdir(parents=True, exist_ok=True)
    for directory in reversed(missing):
        directory.chmod(directory.stat().st_mode | 0o750)


def _atomic_json(path: Path, value: dict) -> None:
    fd, name = tempfile.mkstemp(prefix=".koepac-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            json.dump(value, output, indent=2)
            output.write("\n")
            os.fchmod(output.fileno(), 0o644)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def extract(input_file: str | Path, output_dir: str | Path, verbose: bool = False) -> dict:
    """Extract all recoverable clips. No output path is touched before recognition."""
    source = Path(input_file)
    destination = Path(output_dir)
    with source.open("rb") as stream:
        signature = stream.read(8)
        if signature != MAGIC:
            raise UnsupportedFormat("not KOEPAC: expected the exact 8-byte KOEPAC\\0\\0 signature")
        archive = parse_archive(signature + stream.read())
    stem = source.stem
    counts = Counter(entry.clip_id for entry in archive.entries)
    names = {
        entry.ordinal: (f"{stem}_{entry.clip_id:05d}"
                        + (f"_entry{entry.ordinal:05d}" if counts[entry.clip_id] > 1 else "")
                        + ".wav")
        for entry in archive.entries
    }
    metadata_path = destination / f"{stem}.koepac.json"
    # Prevent replacing the input, even if its extension happens to be .wav.
    source_real = source.resolve()
    targets = [destination / names[e.ordinal] for e in archive.entries if not e.skip_reason]
    if verbose:
        targets.append(metadata_path)
    for target in targets:
        if target.resolve() == source_real or (target.exists() and os.path.samefile(source, target)):
            raise OSError(f"output would overwrite the input: {target}")
        if target.exists() and target.is_dir():
            raise OSError(f"output path is an existing directory: {target}")
    report = {
        "input": str(source), "input_bytes": len(archive.data),
        "format": "KOEPAC", "channels": 1, "bits_per_sample": 16,
        "sample_rate": archive.sample_rate, "sample_rate_field": archive.sample_rate_field,
        "declared_clip_count": archive.declared_count, "data_offset": archive.data_offset,
        "header_hex": archive.data[:32].hex(),
        "issues": list(archive.issues),
        "unreferenced_ranges": [
            {"start": start, "end": end, "hex": archive.data[start:end].hex()}
            for start, end in archive.unreferenced_ranges
        ] if verbose else [{"start": a, "end": b} for a, b in archive.unreferenced_ranges],
        "entries": [], "written": 0, "skipped": 0,
    }
    if targets:
        readable_directory(destination)
    for entry in archive.entries:
        item = {
            "index": entry.ordinal, "id": entry.clip_id, "offset": entry.offset,
            "block_count": entry.block_count, "issues": list(entry.issues),
        }
        report["entries"].append(item)
        if entry.skip_reason:
            item.update(status="skipped", reason=entry.skip_reason)
            report["skipped"] += 1
            continue
        target = destination / names[entry.ordinal]
        fd, temporary = tempfile.mkstemp(prefix=".koepac-", suffix=".tmp", dir=destination)
        block_modes: Counter = Counter()
        block_details = []
        try:
            with os.fdopen(fd, "wb") as output:
                with wave.open(output, "wb") as wav:
                    wav.setparams((1, 2, archive.sample_rate, entry.block_count * 1024, "NONE", "not compressed"))
                    cursor = entry.payload_offset
                    for block_index, length in enumerate(entry.lengths):
                        end = min(cursor + length, entry.limit)
                        payload = archive.data[cursor:end] if cursor < end else b""
                        pcm, consumed, problem = decode_block(payload, length)
                        mode = "silence" if length == 0 else "raw" if length == 1024 else "dpcm"
                        block_modes[mode] += 1
                        if problem:
                            item["issues"].append(f"block {block_index} at {cursor}: {problem}")
                        if verbose:
                            detail = {"index": block_index, "offset": cursor, "length": length,
                                      "available": len(payload), "consumed": consumed, "mode": mode}
                            if problem:
                                detail["issue"] = problem
                                detail["unconsumed_hex"] = payload[consumed:].hex()
                            block_details.append(detail)
                        wav.writeframesraw(pcm)
                        cursor += length
                os.fchmod(output.fileno(), 0o644)
            os.replace(temporary, target)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        item.update(status="recovered" if item["issues"] else "ok", output=str(target),
                    frames=entry.block_count * 1024, duration=entry.block_count * 1024 / archive.sample_rate,
                    block_modes=dict(block_modes))
        if verbose:
            item["blocks"] = block_details
        report["written"] += 1
    report["clean"] = not report["issues"] and all(e["status"] == "ok" for e in report["entries"])
    if verbose:
        _atomic_json(metadata_path, report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputDir", type=Path, help="existing directories are allowed")
    parser.add_argument("-verbose", "--verbose", action="store_true",
                        help="also write a JSON byte/block audit and print per-clip details")
    args = parser.parse_args(argv)
    try:
        report = extract(args.inputFile, args.outputDir, args.verbose)
    except UnsupportedFormat as error:
        print(f"Unsupported: {error}", file=sys.stderr)
        return 2
    except (MalformedArchive, OSError, wave.Error, struct.error) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    for issue in report["issues"]:
        print(f"Warning: {issue}", file=sys.stderr)
    for entry in report["entries"]:
        if entry["status"] == "skipped":
            print(f"Skipped clip {entry['id']}: {entry['reason']}", file=sys.stderr)
        for issue in entry["issues"]:
            print(f"Warning, clip {entry['id']}: {issue}", file=sys.stderr)
        if args.verbose and entry["status"] != "skipped":
            print(f"{entry['output']}: {entry['frames']} samples, {entry['duration']:.3f} seconds")
    if args.verbose:
        print(f"Wrote {report['written']} WAV file(s); skipped {report['skipped']} clip(s).")
    return 0 if report["clean"] else 3


if __name__ == "__main__":
    raise SystemExit(main())

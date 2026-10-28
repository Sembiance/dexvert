#!/usr/bin/env python3
# Vibe coded by Codex
"""Decode MADE SFLX sound resources using only the Python standard library.

Usage: madeSoundFile.py inputFile outputDir [-verbose] [--rate 11025]
See madeSoundFile.txt for the binary grammar, recovery rules, and limitations.
The PCM algorithm was checked against ScummVM's MADE sound decoder; this is
an independently structured parser with explicit bounds and byte accounting.
"""

import argparse
from collections import Counter
from dataclasses import dataclass
import json
import os
from pathlib import Path
import struct
import sys
import tempfile


class FormatError(ValueError):
    """Input cannot be decoded within the documented SFLX profile."""


@dataclass
class Decoded:
    pcm: bytes
    audit: dict


def decode(data, *, declared_only=False):
    """Validate the entire resource, then decode every recoverable PCM sample.

    No filesystem writes occur here. Unsupported control codes reject the
    entire conversion, including when they occur after valid blocks.
    """
    if data[:4] != b"SFLX":
        raise FormatError("not a MADE SFLX resource: missing exact SFLX signature")
    if len(data) < 14:
        raise FormatError("SFLX header is truncated; block size is unavailable")
    size, count, block_size = struct.unpack_from("<IIH", data, 4)
    declared_end = size + 4
    if declared_end < 14:
        raise FormatError("SFLX length field ends inside its own header")
    if block_size == 0:
        raise FormatError("SFLX block size is zero; sample boundaries are unknowable")

    spans = []

    def span(start, end, role, block=None):
        if start == end:
            return
        item = {"start": start, "end": end, "bytes": end - start, "role": role}
        if block is not None:
            item["block"] = block
        spans.append(item)

    span(0, 4, "signature")
    span(4, 8, "resource_length_minus_four")
    span(8, 12, "declared_block_count")
    span(12, 14, "decoded_samples_per_block")
    warnings = []
    if declared_end > len(data):
        warnings.append(f"File is truncated: header requires {declared_end} bytes, "
                        f"but only {len(data)} are present ({declared_end - len(data)} missing).")
    elif declared_end < len(data):
        warnings.append(f"{len(data) - declared_end} bytes after the declared resource "
                        "are outside SFLX and will not be interpreted as audio.")

    end = min(declared_end, len(data))
    blocks = []
    pos = 14
    while pos < end:
        start = pos
        control = data[pos]
        kind = control & 15
        reduction = control >> 6
        number = len(blocks)
        if kind > 5:
            raise FormatError(f"unsupported SFLX coding type {kind} at byte {pos}; "
                              "no unambiguous block boundary is defined")
        if reduction == 3:
            raise FormatError(f"unsupported SFLX resampling mode 3 at byte {pos}")
        factor = 1 << reduction
        if block_size % factor:
            raise FormatError(f"block {number}: {block_size} samples cannot be "
                              f"divided exactly by interpolation factor {factor}")
        work = block_size // factor
        bits = {2: 1, 3: 2, 4: 4}.get(kind, 0)
        if bits and work % (8 // bits):
            raise FormatError(f"block {number}: nonintegral packed-code byte count; "
                              "the interpretation of excess codes is unverified")
        pos += 1
        span(start, pos, "block_control", number)
        table_size = (1 << bits) if bits else 0
        payload_size = work * bits // 8 if bits else (work if kind == 5 else 0)
        table_start = pos
        table_end = min(end, pos + table_size)
        span(pos, table_end, "delta_codebook", number)
        pos = table_end
        payload_start = pos
        payload_end = min(end, pos + payload_size) if table_end - table_start == table_size else pos
        span(pos, payload_end, "packed_delta_indices" if bits else "unsigned_pcm", number)
        pos = payload_end
        complete = pos - start == 1 + table_size + payload_size
        block = {
            "index": number, "start": start, "end": pos,
            "control": control, "coding_type": kind,
            "ignored_control_bits": control & 0x30,
            "interpolation_factor": factor, "stored_samples": work,
            "bits_per_index": bits, "table_start": table_start,
            "table_end": table_end, "payload_start": payload_start,
            "payload_end": payload_end, "expected_bytes": 1 + table_size + payload_size,
            "complete": complete, "beyond_declared_count": number >= count,
        }
        if bits:
            block["delta_table"] = [2 * v - 128 for v in data[table_start:table_end]]
        blocks.append(block)
        if not complete:
            warnings.append(f"Block {number} at byte {start} is truncated: "
                            f"{pos - start} of {block['expected_bytes']} bytes remain; "
                            "only samples determined by the present bytes are exported.")
            break
    span(end, len(data), "outside_declared_resource")

    # Assert a disjoint, exhaustive partition, including malformed-file regions.
    next_offset = 0
    for item in spans:
        if item["start"] != next_offset:
            raise AssertionError("internal byte accounting gap")
        next_offset = item["end"]
    if next_offset != len(data):
        raise AssertionError("internal byte accounting incomplete")

    complete_count = sum(b["complete"] for b in blocks)
    if complete_count < count:
        warnings.append(f"Only {complete_count} of {count} declared blocks are complete; "
                        "missing audio is not replaced by invented samples.")
    extra_count = max(0, len(blocks) - count)
    notes = []
    if extra_count:
        policy = "excluded by --declared-only" if declared_only else "included in the WAV"
        notes.append(f"{extra_count} stored block(s) beyond the declared count were parsed and "
                     f"{policy}. Their intended playback inclusion is not established.")

    previous = bytearray([128]) * block_size
    accumulator = 0
    pcm = bytearray()
    controls = Counter()
    partial_samples = 0
    for block in blocks:
        kind = block["coding_type"]
        factor = block["interpolation_factor"]
        work = block["stored_samples"]
        controls[f"0x{block['control']:02x}"] += 1
        payload = data[block["payload_start"]:block["payload_end"]]
        if kind == 0:
            base = bytes([128]) * work
            accumulator = 0
        elif kind == 1:
            # Repeat the beginning of the previous *expanded* block. The DPCM
            # accumulator is a separate state and does not change on repeat.
            base = previous[:work]
        elif kind == 5:
            base = payload
            if base:
                accumulator = base[-1] - 128
        else:
            bits = block["bits_per_index"]
            table = block["delta_table"]
            base = bytearray()
            if len(table) == 1 << bits:
                mask = (1 << bits) - 1
                for value in payload:
                    for shift in range(0, 8, bits):
                        accumulator = max(-127, min(127, accumulator + table[(value >> shift) & mask]))
                        base.append(accumulator + 128)

        # Interpolation uses integer averages on unsigned PCM. Only the end of
        # a complete block permits clamping the next endpoint to the last one.
        expanded = bytearray()
        if factor == 1:
            expanded.extend(base)
        else:
            for index, first in enumerate(base):
                expanded.append(first)
                if index + 1 < len(base):
                    second = base[index + 1]
                elif block["complete"]:
                    second = first
                else:
                    break  # The following interpolated samples need absent data.
                middle = (first + second) // 2
                if factor == 2:
                    expanded.append(middle)
                else:
                    expanded.extend(((first + middle) // 2, middle, (middle + second) // 2))
        previous[:len(expanded)] = expanded
        block["decoded_samples"] = len(expanded)
        block["output_start_sample"] = len(pcm)
        include = not declared_only or not block["beyond_declared_count"]
        if include:
            pcm.extend(expanded)
            if not block["complete"]:
                partial_samples += len(expanded)
        block["output_end_sample"] = len(pcm)

    if not pcm:
        raise FormatError("SFLX is recognized, but no audio samples can be recovered")
    audit = {
        "format": "MADE SFLX", "input_bytes": len(data),
        "declared_resource_bytes": declared_end, "declared_blocks": count,
        "samples_per_block": block_size, "complete_blocks": complete_count,
        "stored_tail_blocks": extra_count, "partial_block_samples_exported": partial_samples,
        "output_samples": len(pcm), "declared_only": declared_only,
        "sample_rate_is_external": True, "control_counts": dict(sorted(controls.items())),
        "accounted_bytes": next_offset,
        "uninterpreted_bytes": max(0, len(data) - declared_end),
        "warnings": warnings, "notes": notes, "spans": spans, "blocks": blocks,
    }
    return Decoded(bytes(pcm), audit)


def wav_bytes(pcm, rate):
    """Build a correctly padded RIFF WAVE containing unsigned 8-bit mono PCM."""
    if not 1 <= rate <= 0xFFFFFFFF:
        raise FormatError("sample rate must be between 1 and 4294967295 Hz")
    padding = b"\0" if len(pcm) & 1 else b""
    riff_size = 36 + len(pcm) + len(padding)
    if riff_size > 0xFFFFFFFF:
        raise FormatError("decoded sound exceeds the classic RIFF/WAV size limit")
    return (b"RIFF" + struct.pack("<I", riff_size) + b"WAVEfmt "
            + struct.pack("<IHHIIHH", 16, 1, 1, rate, rate, 1, 8)
            + b"data" + struct.pack("<I", len(pcm)) + pcm + padding)


def _mkdir_readable(path):
    missing = []
    current = path
    while not current.exists():
        missing.append(current)
        current = current.parent
    path.mkdir(parents=True, exist_ok=True)
    for directory in reversed(missing):
        directory.chmod(directory.stat().st_mode | 0o750)


def _write_atomic(path, contents):
    # The temporary file is always removed, including after a failed replace.
    fd, temporary = tempfile.mkstemp(prefix=".madeSoundFile-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(contents)
            os.fchmod(stream.fileno(), 0o644)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def convert(input_file, output_dir, *, rate=11025, verbose=False, declared_only=False):
    """Convert one resource. Existing output directories are supported."""
    source = Path(input_file)
    destination = Path(output_dir)
    with source.open("rb") as stream:
        prefix = stream.read(14)
        if prefix[:4] != b"SFLX":
            raise FormatError("not a MADE SFLX resource: missing exact SFLX signature")
        data = prefix + stream.read()
    result = decode(data, declared_only=declared_only)
    wave_data = wav_bytes(result.pcm, rate)
    name = source.stem or "sound"
    wave_path = destination / (name + ".wav")
    metadata_path = destination / (name + ".json")
    for target in (wave_path, metadata_path) if verbose else (wave_path,):
        if target.resolve() == source.resolve():
            raise FormatError("output path would overwrite the input file")
    result.audit.update({"input_file": str(source), "output_file": str(wave_path),
                         "sample_rate_hz": rate, "duration_seconds": len(result.pcm) / rate})
    metadata = (json.dumps(result.audit, indent=2) + "\n").encode("utf-8") if verbose else None
    # Parsing, decoding, and WAV construction all finish before creating output.
    _mkdir_readable(destination)
    _write_atomic(wave_path, wave_data)
    if metadata is not None:
        _write_atomic(metadata_path, metadata)
    return wave_path, result.audit


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputDir", type=Path)
    parser.add_argument("-verbose", "--verbose", action="store_true",
                        help="also write a JSON byte map and decoding diagnostics")
    parser.add_argument("--rate", type=int, default=11025, metavar="HZ",
                        help="external playback rate; default 11025 Hz, not stored in SFLX")
    parser.add_argument("--declared-only", action="store_true",
                        help="parse stored tail blocks but omit them from the WAV")
    args = parser.parse_args(argv)
    try:
        path, audit = convert(args.inputFile, args.outputDir, rate=args.rate,
                              verbose=args.verbose, declared_only=args.declared_only)
    except (FormatError, OSError, OverflowError, MemoryError) as error:
        print(f"madeSoundFile: {error}", file=sys.stderr)
        return 1
    for warning in audit["warnings"]:
        print(f"Warning: {warning}", file=sys.stderr)
    for note in audit["notes"]:
        print(f"Note: {note}", file=sys.stderr)
    print(f"{path} ({audit['output_samples']} samples, {args.rate} Hz)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# Vibe coded by Codex
"""Decode the tPxD/T eJay sample format; see raveEJaySampleAudio.txt.

Usage: raveEJaySampleAudio.py [-verbose] inputFile outputDir
Python 3.9+, standard library only. No DLLs, external tools or data files.
"""
import argparse
from array import array
from dataclasses import dataclass, field
from itertools import accumulate
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
import wave

MAGIC = b"tPxD"
SAMPLE_RATE = 44100
# Exact positive half of the original decoder's doubled delta lookup table.
POSITIVE = (
    0, 2, 4, 6, 8, 10, 14, 18, 22, 26, 32, 38, 44, 50, 56, 64,
    72, 80, 88, 98, 108, 118, 130, 142, 154, 168, 182, 198, 214, 230, 248, 266,
    286, 306, 328, 352, 376, 402, 430, 458, 488, 520, 554, 588, 624, 662, 702, 744,
    788, 834, 882, 934, 988, 1044, 1102, 1164, 1228, 1296, 1366, 1440, 1516, 1596, 1680, 1768,
    1860, 1956, 2056, 2160, 2268, 2380, 2498, 2620, 2748, 2880, 3018, 3162, 3312, 3468, 3630, 3798,
    3974, 4156, 4346, 4542, 4746, 4958, 5178, 5408, 5646, 5892, 6148, 6414, 6690, 6976, 7272, 7578,
    7896, 8224, 8564, 8916, 9282, 9660, 10050, 10454, 10872, 11304, 11752, 12214, 12692, 13186, 13696, 14222,
    14766, 15326, 15904, 16500, 17116, 17752, 18406, 19082, 19778, 20494, 21232, 21992, 22776, 23582, 24412, 25266,
)
DELTA = (0,) + tuple(-v for v in reversed(POSITIVE[1:])) + POSITIVE


class FormatError(ValueError):
    """Unsupported identification or header: do not create output files."""


@dataclass
class Record:
    index: int
    start: int
    header_end: int
    audio_end: int
    end: int
    declared_frames: int
    recovered_frames: int
    expanded_frames: int
    seed: int
    metadata: bytes
    tail: bytes = b""
    incomplete_bytes: bytes = b""
    warnings: list = field(default_factory=list)
    token_counts: dict = field(default_factory=dict)
    filename: str = ""

    @property
    def title(self):
        # Latin-1 is a reversible byte display, not a claimed charset identifier.
        lines = self.metadata.rstrip(b"\0").decode("latin-1").split("\r\n")
        return " / ".join(x for x in lines[:2] if x)

    def details(self):
        return dict(index=self.index, filename=self.filename, title=self.title,
                    start=self.start, header_end=self.header_end,
                    audio_end=self.audio_end, end=self.end,
                    declared_frames=self.declared_frames,
                    recovered_frames=self.recovered_frames,
                    expanded_frames=self.expanded_frames,
                    duration_seconds=self.recovered_frames / SAMPLE_RATE,
                    seed=self.seed, metadata_hex=self.metadata.hex(),
                    metadata_lines=self.metadata.rstrip(b"\0").decode("latin-1").split("\r\n"),
                    tail_hex=self.tail.hex(),
                    incomplete_bytes_hex=self.incomplete_bytes.hex(),
                    token_counts=self.token_counts, warnings=self.warnings)


class Dictionary:
    """Fast normal slots, with exact legacy word-arena aliasing for long entries."""
    def __init__(self):
        self.slots = [None] * 256
        self.slots[0] = b"\x80" * 5
        self.arena = None

    def define(self, index, block):
        if len(block) <= 7 and self.arena is None:
            self.slots[index] = block
            return
        # The original decoder uses an eight-word stride and a -1 terminator.
        # Lengths 8..11 overwrite the start of the following slot. Preserve that
        # behavior safely instead of treating them as independent long strings.
        if self.arena is None:
            self.arena = [None] * (256 * 8 + 12)
            for i, value in enumerate(self.slots):
                if value is not None:
                    base = i * 8
                    self.arena[base:base + len(value) + 1] = [*value, -1]
        base = index * 8
        self.arena[base:base + len(block) + 1] = [*block, -1]
        for i in range(256):
            base = i * 8
            end = base
            while end < len(self.arena) and self.arena[end] not in (None, -1):
                end += 1
            self.slots[i] = (bytes(self.arena[base:end])
                             if end < len(self.arena) and self.arena[end] == -1 else None)


def _boundary(data, pos):
    return pos == len(data) or data[pos:pos + 4] == MAGIC


def _read_record(data, start, index, decode=False):
    """Read tokens by their lengths, never search for a signature in audio."""
    size = len(data)
    if data[start:start + 4] != MAGIC:
        raise FormatError(f"offset {start}: expected the exact tPxD signature")
    if size - start < 5:
        return None, b"", f"offset {start}: truncated metadata-length field"
    length = data[start + 4]
    marker = start + 5 + length
    if marker + 7 > size:
        return None, b"", f"offset {start}: truncated record header"
    if data[marker] != 0x54:
        raise FormatError(f"offset {marker}: unsupported tPxD marker 0x{data[marker]:02x}; expected T")
    n, seed = struct.unpack_from("<Ih", data, marker + 1)
    pos = marker + 7
    record = Record(index, start, pos, pos, pos, n, 0, 1, seed, data[start + 5:marker])
    if length < 2 or not record.metadata.endswith(b"\0\0"):
        record.warnings.append("Metadata is missing the two trailing NUL bytes; length field used as stored.")
    if n == 0:
        record.warnings.append("Declared sample count is zero; no audio exported.")
    dictionary = Dictionary()
    codes = bytearray() if decode else None
    expanded = 1
    counts = [0] * 256
    while expanded < n and pos < size:
        token_start = pos
        op = data[pos]
        pos += 1
        counts[op] += 1
        if op < 0xF4:
            block = dictionary.slots[op]
            if block is None:
                record.warnings.append(f"Undefined dictionary reference 0x{op:02x} at offset {token_start}; stopped before it.")
                pos = token_start
                break
        elif op == 0xFF:
            if pos == size:
                record.incomplete_bytes = data[token_start:pos]
                record.warnings.append(f"Literal at offset {token_start} is missing its delta byte.")
                break
            block = data[pos:pos + 1]
            pos += 1
        else:
            count = op - 0xF3
            if pos == size:
                record.incomplete_bytes = data[token_start:pos]
                record.warnings.append(f"Definition at offset {token_start} is missing its index and delta bytes.")
                break
            slot = data[pos]
            pos += 1
            block = data[pos:min(pos + count, size)]
            pos += len(block)
            if len(block) != count:
                record.incomplete_bytes = data[token_start:pos]
                record.warnings.append(f"Definition at offset {token_start} has {len(block)} of {count} delta bytes; available deltas recovered.")
            else:
                dictionary.define(slot, block)
        expanded += len(block)
        if decode:
            codes.extend(block)
    record.audio_end = pos
    record.expanded_frames = expanded
    record.recovered_frames = min(n, expanded)
    record.token_counts = {f"{i:02x}": c for i, c in enumerate(counts) if c}
    if expanded < n:
        record.warnings.append(f"Audio is incomplete: recovered {expanded} of {n} declared frames; missing audio was not synthesized.")
    # Complete trailing commands from known writers are outside the declared
    # duration. They are accepted only when followed by EOF or the next record.
    if expanded >= n and not _boundary(data, pos):
        tail_end = pos
        if data[pos:pos + 1] == b"\0" and _boundary(data, pos + 1):
            tail_end = pos + 1
        elif (expanded == n and data[pos:pos + 1] == b"\xff"
              and pos + 3 <= size and data[pos + 2] == 0
              and _boundary(data, pos + 3)):
            tail_end = pos + 3
        if tail_end != pos:
            record.tail = data[pos:tail_end]
            pos = tail_end
    record.end = pos
    pcm = b""
    if decode and record.recovered_frames:
        del codes[record.recovered_frames - 1:]
        pcm_array = array("H", (v & 0xFFFF for v in accumulate(
            map(DELTA.__getitem__, codes), initial=seed * 2)))
        if sys.byteorder != "little":
            pcm_array.byteswap()
        pcm = pcm_array.tobytes()
    return record, pcm, None


def inspect(data):
    """Validate the whole input before any destination directory is created."""
    if data[:4] != MAGIC:
        raise FormatError("not a tPxD eJay sample file (signature mismatch)")
    records = []
    issues = []
    pos = 0
    while pos < len(data):
        if data[pos:pos + 4] != MAGIC:
            issues.append(dict(offset=pos, length=len(data) - pos,
                               reason="Unrecognized trailing bytes after a confirmed tPxD record; no resynchronization attempted."))
            break
        record, _, problem = _read_record(data, pos, len(records) + 1)
        if problem:
            issues.append(dict(offset=pos, length=len(data) - pos, reason=problem))
            break
        records.append(record)
        if record.end <= pos:
            raise FormatError("record parser did not advance")
        pos = record.end
    return records, issues


def decode_record(data, record):
    actual, pcm, error = _read_record(data, record.start, record.index, decode=True)
    if error or actual.end != record.end or len(pcm) != record.recovered_frames * 2:
        raise FormatError("record changed between inspection and decoding")
    return pcm


def _readable_directory(path):
    missing = []
    current = path
    while not current.exists():
        missing.append(current)
        current = current.parent
    path.mkdir(parents=True, exist_ok=True)
    for directory in missing:
        directory.chmod(directory.stat().st_mode | 0o550)


def _atomic_write(path, writer):
    descriptor, temporary = tempfile.mkstemp(prefix=".ejay-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w+b") as stream:
            writer(stream)
            stream.flush()
            os.fchmod(stream.fileno(), 0o644)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _write_wave(stream, pcm):
    with wave.open(stream, "wb") as output:
        output.setparams((1, 2, SAMPLE_RATE, 0, "NONE", "not compressed"))
        output.writeframes(pcm)


def convert(input_file, output_dir, verbose=False):
    """Return the inspection manifest. Only WAVs are written unless verbose."""
    source = Path(input_file)
    destination = Path(output_dir)
    # Read four bytes first so a foreign large input is rejected immediately.
    with source.open("rb") as stream:
        signature = stream.read(4)
        if signature != MAGIC:
            raise FormatError("not a tPxD eJay sample file (signature mismatch)")
        data = signature + stream.read()
    records, issues = inspect(data)
    exportable = [r for r in records if r.recovered_frames]
    stem = source.stem or "sample"
    for record in exportable:
        record.filename = (f"{stem}.wav" if len(records) == 1 else
                           f"{stem}_{record.index:04d}.wav")
    manifest_name = f"{stem}.json"
    targets = [destination / r.filename for r in exportable]
    if verbose:
        targets.append(destination / manifest_name)
    for target in targets:
        if target.resolve() == source.resolve():
            raise FormatError("an output path would replace the input file")
    manifest = dict(format="tPxD/T", input=str(source), input_bytes=len(data),
                    sample_rate=SAMPLE_RATE, channels=1, bits_per_sample=16,
                    records=[r.details() for r in records], issues=issues,
                    output_files=[str(destination / r.filename) for r in exportable])
    if targets:
        _readable_directory(destination)
    for record in exportable:
        pcm = decode_record(data, record)
        _atomic_write(destination / record.filename, lambda stream: _write_wave(stream, pcm))
    if verbose:
        # Unparsed bytes are preserved in the opt-in manifest, never hidden.
        for issue in manifest["issues"]:
            issue["bytes_hex"] = data[issue["offset"]:issue["offset"] + issue["length"]].hex()
        encoded = (json.dumps(manifest, ensure_ascii=True, indent=2) + "\n").encode("utf-8")
        _atomic_write(destination / manifest_name, lambda stream: stream.write(encoded))
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputDir", type=Path)
    parser.add_argument("-verbose", "--verbose", action="store_true",
                        help="also write a JSON manifest with metadata, byte ranges and recovery details")
    args = parser.parse_args(argv)
    try:
        result = convert(args.inputFile, args.outputDir, args.verbose)
    except (OSError, FormatError, OverflowError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    damaged = bool(result["issues"])
    for record in result["records"]:
        for warning in record["warnings"]:
            print(f"warning: record {record['index']}: {warning}", file=sys.stderr)
            damaged = True
    for issue in result["issues"]:
        print(f"warning: {issue['reason']} ({issue['length']} bytes at offset {issue['offset']})", file=sys.stderr)
    print(f"Wrote {len(result['output_files'])} WAV file(s) to {args.outputDir}")
    return 3 if damaged else 0


if __name__ == "__main__":
    raise SystemExit(main())

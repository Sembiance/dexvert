#!/usr/bin/env python3
# Vibe coded by Codex
"""Extract HyperStudio RWP sampled sounds to WAV using only the Python stdlib.

Usage: hyperStudioSampledSound.py [-verbose] inputFile outputDir
See hyperStudioSampledSound.txt for the byte layout, ACE algorithms, recovery
policy, and the distinction between waveform extraction and hardware playback.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
from dataclasses import dataclass


class FormatError(ValueError):
    """Not a supported sound, or insufficient information for safe decoding."""


# Exact ACE step sizes, recovered from Apple Tool029 v1.3. These are NOT
# the IMA ADPCM step table. Index zero corresponds to Apple's table row one.
ACE_STEPS = (
    3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 18, 20, 22, 24, 26,
    29, 32, 35, 39, 43, 47, 52, 57, 63, 69, 76, 84, 92, 102, 112,
    123, 135, 149, 164, 180, 198, 218, 240, 264,
)
ACE_ADJUST = {1: (-1, -1, -1, -1, 2, 4, 6, 8), 2: (-1, -1, 2, 5)}
CODECS = {0: "unsigned 8-bit PCM", 1: "ACE 2:1", 2: "ACE 8:3"}

# (byte offset, byte count, field name, interpretation)
FIELDS = (
    (0, 4, "HFileID", "signature"),
    (4, 4, "HDataOffset", "u32"),
    (8, 4, "HVersID", "identifier"),
    (12, 4, "HDataID", "identifier"),
    (16, 2, "HLength2", "u16"),
    (18, 2, "HPbRate2", "u16"),
    (20, 2, "HVolume2", "u16"),
    (22, 2, "HEcho2", "u16"),
    (24, 2, "HLength", "u16"),
    (26, 2, "HAce", "u16"),
    (28, 2, "HPbRate", "u16"),
    (30, 2, "HVolume", "u16"),
    (32, 2, "HStereo", "u16"),
    (34, 2, "HEcho", "u16"),
    (36, 2, "HReserved", "u16"),
    (38, 2, "HRepeat", "u16"),
    (40, 4, "HOffset1", "u32"),
    (44, 4, "HExtra", "u32"),
    (48, 1, "HFileName.length", "u8"),
    (49, 15, "HFileName.storage", "bytes"),
)


def signed16(value: int) -> int:
    """Match the original 65816 accumulator wrap, including corrupt streams."""
    return ((value + 32768) & 65535) - 32768


def decode_ace(data: bytes, method: int) -> tuple[bytes, int, int]:
    """Return PCM, number of incomplete final bits, and those bits' value.

    State continues across all 512-sample blocks. Output clipping does NOT
    clip the predictor. ACE adds its half-step bias AFTER emitting a sample.
    """
    if method not in ACE_ADJUST:
        raise FormatError(f"Unsupported ACE method {method}")
    width = 5 - method
    sign_bit = 1 << (width - 1)
    mask = (1 << width) - 1
    adjustments = ACE_ADJUST[method]
    index, predictor, reservoir, bit_count = 0, 128, 0, 0
    pcm = bytearray()
    for byte in data:
        reservoir |= byte << bit_count
        bit_count += 8
        while bit_count >= width:
            code = reservoir & mask
            reservoir >>= width
            bit_count -= width
            magnitude = code & (sign_bit - 1)
            sign = -1 if code & sign_bit else 1
            step = ACE_STEPS[index]
            delta = 0
            for bit in range(width - 1):
                if magnitude & (1 << bit):
                    delta += step >> (width - 2 - bit)
            predictor = signed16(predictor + sign * delta)
            pcm.append(max(1, min(255, predictor)))
            predictor = signed16(predictor + sign * (step >> (width - 1)))
            index = max(0, min(len(ACE_STEPS) - 1, index + adjustments[magnitude]))
    return bytes(pcm), bit_count, reservoir


@dataclass
class Sound:
    header: bytes
    pcm: bytes
    rate: int
    metadata: dict


def parse_sound(data: bytes) -> Sound:
    """Validate identity before interpreting any payload; never guess a codec."""
    if data[:4] != b"SSHS":
        raise FormatError("Not a HyperStudio sampled sound: missing SSHS signature")
    if len(data) < 64:
        raise FormatError("Recognized SSHS file, but its 64-byte header is truncated")
    if data[8:12] != b"RWP ":
        raise FormatError(
            f"Recognized SSHS file, but version {data[8:12]!r} is unsupported; "
            "only the documented RWP-space revision is implemented"
        )
    fields, regions = {}, []
    for offset, length, name, kind in FIELDS:
        raw = data[offset:offset + length]
        value = int.from_bytes(raw, "little") if kind.startswith("u") else raw.hex()
        fields[name] = value
        regions.append({"offset": offset, "length": length, "field": name,
                        "hex": raw.hex(), "value": value})
    if fields["HDataOffset"] != 56:
        raise FormatError(
            "Recognized SSHS/RWP file, but HDataOffset is not 56; "
            "the audio boundary cannot be established without guessing"
        )
    stereo = fields["HStereo"]
    if stereo:
        raise FormatError(
            f"Recognized HyperStudio file with HStereo={stereo}; stereo/other "
            "channel layouts are not implemented because their on-disk "
            "ordering and compressed-channel state have not been verified"
        )
    method = fields["HAce"] >> 14
    if method == 3:
        raise FormatError("Recognized HyperStudio file using reserved ACE method 3")
    payload = data[64:]
    if not payload:
        raise FormatError("Recognized HyperStudio file contains no recoverable sound data")

    warnings = []
    notes = []
    nblocks = fields["HAce"] & 0x3fff
    declared_pages = fields["HLength"]
    declared_bytes = declared_pages * 256
    if method:
        expected_bytes = nblocks * (256 if method == 1 else 192)
        if not nblocks:
            warnings.append("ACE block count is zero; decoding the available payload")
        if len(payload) != expected_bytes:
            warnings.append(
                f"ACE block count specifies {expected_bytes} encoded bytes; "
                f"{len(payload)} are present. Decoding all complete available codes"
            )
        if declared_pages != expected_bytes // 256:
            warnings.append(
                f"HLength={declared_pages} differs from the encoded byte count's "
                f"whole-page value {expected_bytes // 256}"
            )
        pcm, leftover_count, leftover_value = decode_ace(payload, method)
        if leftover_count:
            warnings.append(
                f"Truncated ACE code: {leftover_count} final bits cannot produce "
                "another sample; their value is retained in the WAV comment"
            )
    else:
        expected_bytes = declared_bytes
        pcm, leftover_count, leftover_value = payload, 0, 0
        if nblocks:
            warnings.append("ACE block count is nonzero although compression is disabled")
        if len(payload) != declared_bytes:
            difference = len(payload) - declared_bytes
            warnings.append(
                f"HLength specifies {declared_bytes} PCM bytes; {len(payload)} "
                f"are present ({difference:+d}). Preserving every available PCM "
                "byte; no trimming or invented samples"
            )
    if not pcm:
        raise FormatError("Recognized HyperStudio file contains no complete audio samples")

    # These words have defined roles but are inactive in a monophonic file.
    for name in ("HLength2", "HPbRate2", "HVolume2", "HEcho2", "HOffset1"):
        if fields[name]:
            warnings.append(f"Inactive mono field {name} is nonzero; retained verbatim")
    for name in ("HReserved", "HExtra"):
        if fields[name]:
            warnings.append(f"Reserved field {name} is nonzero; retained verbatim")
    for name, maximum in (("HVolume", 15), ("HEcho", 127), ("HRepeat", 20)):
        if fields[name] > maximum:
            warnings.append(f"{name}={fields[name]} exceeds its documented maximum {maximum}")

    name_length = fields["HFileName.length"]
    if name_length > 15:
        warnings.append(f"Invalid Pascal name length {name_length}; only 15 name bytes exist")
    title_bytes = data[49:49 + min(name_length, 15)]
    # Latin-1 is only a reversible byte display for non-ASCII names. No encoding
    # is guessed, and the exact original bytes are also stored in hshd.
    title = title_bytes.decode("latin-1")
    if any(data[49 + min(name_length, 15):64]):
        warnings.append("Unused Pascal-name storage is nonzero; retained verbatim")
    numerator = (fields["HPbRate"] + 40) * 1645
    rate = (numerator + 16) // 32
    notes.append("The WAV contains one unscaled waveform pass at the stored playback rate")
    notes.append("Volume, echo, and repeat settings are preserved as metadata, not synthesized")
    if fields["HEcho"]:
        warnings.append(
            f"Echo setting {fields['HEcho']} is preserved but its hardware playback "
            "effect is not rendered"
        )
    if fields["HRepeat"]:
        notes.append(f"Stored repeat setting: {fields['HRepeat']}; WAV playback is one pass")
    if numerator % 32:
        notes.append(f"Exact rate {numerator}/32 Hz is rounded to {rate} Hz for PCM WAV")

    regions.append({"offset": 64, "length": len(payload), "field": "sound_data",
                    "codec": CODECS[method], "complete_codes": len(pcm),
                    "incomplete_final_bits": leftover_count,
                    "incomplete_final_bits_value": leftover_value})
    metadata = {
        "format": "HyperStudio sampled sound", "revision": "RWP ",
        "creator_bytes_hex": data[12:16].hex(), "source_bytes": len(data),
        "source_sha256": hashlib.sha256(data).hexdigest(),
        "title_byte_display": title, "title_bytes_hex": title_bytes.hex(),
        "codec": CODECS[method], "ace_method": method, "ace_blocks": nblocks,
        "header_fields": fields, "encoded_bytes": len(payload),
        "declared_encoded_bytes": expected_bytes, "decoded_samples": len(pcm),
        "pcm_sha256": hashlib.sha256(pcm).hexdigest(),
        "rate_numerator": numerator, "rate_denominator": 32, "wav_rate": rate,
        "channels": 1, "bits_per_sample": 8,
        "duration_seconds": len(pcm) / rate,
        "byte_coverage": regions, "warnings": warnings, "notes": notes,
    }
    assert sum(region["length"] for region in regions) == len(data)
    return Sound(data[:64], pcm, rate, metadata)


def riff_chunk(tag: bytes, payload: bytes) -> bytes:
    if len(payload) > 0xffffffff:
        raise FormatError("Output exceeds the RIFF chunk size limit")
    return tag + struct.pack("<I", len(payload)) + payload + (b"\0" if len(payload) & 1 else b"")


def make_wav(sound: Sound) -> bytes:
    """A normal PCM WAV with readable settings and the exact original header."""
    fmt = struct.pack("<HHIIHH", 1, 1, sound.rate, sound.rate, 1, 8)
    # All 64 original header bytes remain available even without -verbose.
    comment = json.dumps({key: value for key, value in sound.metadata.items()
                          if key != "byte_coverage"}, ensure_ascii=True, sort_keys=True)
    info = b"INFO" + riff_chunk(b"ICMT", comment.encode("ascii") + b"\0")
    body = (b"WAVE" + riff_chunk(b"fmt ", fmt) + riff_chunk(b"hshd", sound.header)
            + riff_chunk(b"LIST", info) + riff_chunk(b"data", sound.pcm))
    if len(body) > 0xffffffff:
        raise FormatError("Output exceeds the RIFF/WAV 4 GiB size limit")
    return b"RIFF" + struct.pack("<I", len(body)) + body


def write_outputs(input_path: Path, output_dir: Path, sound: Sound,
                  verbose: bool = False) -> list[Path]:
    """Stage complete files before replacing outputs; leave no temp files."""
    wav_path = output_dir / (input_path.name + ".wav")
    output_data = [(wav_path, make_wav(sound))]
    if verbose:
        diagnostic = dict(sound.metadata, input_file=str(input_path), output_file=wav_path.name)
        output_data.append((output_dir / (input_path.name + ".json"),
                            (json.dumps(diagnostic, indent=2, ensure_ascii=True) + "\n").encode()))
    for path, _ in output_data:
        if path.resolve() == input_path.resolve():
            raise FormatError("Refusing to replace the input file with an output")
        if path.exists() and not path.is_file():
            raise FormatError(f"Output path is not a regular file: {path}")
    # No output directory is created until parsing, decoding, and WAV generation succeed.
    missing = []
    parent = output_dir
    while not parent.exists():
        missing.append(parent)
        parent = parent.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    for directory in missing:
        directory.chmod(directory.stat().st_mode | 0o550)
    staged = []
    try:
        for path, contents in output_data:
            fd, temporary = tempfile.mkstemp(prefix=".hyperstudio-", dir=output_dir)
            staged.append((Path(temporary), path))
            with os.fdopen(fd, "wb") as stream:
                stream.write(contents)
                os.fchmod(stream.fileno(), 0o644)
        for temporary, path in staged:
            os.replace(temporary, path)
    finally:
        for temporary, _ in staged:
            temporary.unlink(missing_ok=True)
    return [path for path, _ in output_data]


def convert(input_path: Path, output_dir: Path, verbose: bool = False) -> tuple[Sound, list[Path]]:
    # Read identity first: a large unrelated input is rejected without reading it all.
    with input_path.open("rb") as stream:
        header = stream.read(64)
        if header[:4] != b"SSHS":
            raise FormatError("Not a HyperStudio sampled sound: missing SSHS signature")
        if len(header) < 64:
            raise FormatError("Recognized SSHS file has a truncated header")
        if header[8:12] != b"RWP ":
            raise FormatError(f"Unsupported HyperStudio revision {header[8:12]!r}")
        if int.from_bytes(header[4:8], "little") != 56:
            raise FormatError("Unsupported/invalid HDataOffset; expected 56")
        if int.from_bytes(header[32:34], "little"):
            raise FormatError("HyperStudio stereo/other channel layout is not implemented")
        if int.from_bytes(header[26:28], "little") >> 14 == 3:
            raise FormatError("Reserved ACE method 3 is unsupported")
        sound = parse_sound(header + stream.read())
    return sound, write_outputs(input_path, output_dir, sound, verbose)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-verbose", "--verbose", action="store_true",
                        help="also write a JSON byte map and diagnostic metadata")
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputDir", type=Path)
    args = parser.parse_args(argv)
    try:
        sound, paths = convert(args.inputFile, args.outputDir, args.verbose)
    except (FormatError, OSError, OverflowError, MemoryError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    for warning in sound.metadata["warnings"]:
        print(f"warning: {warning}", file=sys.stderr)
    for path in paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

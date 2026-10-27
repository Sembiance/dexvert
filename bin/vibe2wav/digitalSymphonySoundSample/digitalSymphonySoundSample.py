#!/usr/bin/env python3
# Vibe coded by Codex
"""Decode Digital Symphony SySample files using only the Python standard library.

See digitalSymphonySoundSample.txt for the on-disk specification, references,
recovery rules, and the distinction between stored samples and playback rate.
"""

import argparse
from array import array
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
import tempfile


MAGIC = bytes.fromhex("02 01 13 13 13 01 0d 10")
DEFAULT_RATE = 8363  # Explicit audition convention; the file stores no rate.
CODECS = {
    0: "8-bit VIDC logarithmic",
    1: "13-bit LZW, signed 8-bit deltas",
    2: "signed 8-bit PCM",
    3: "signed 16-bit little-endian PCM",
    4: "sigma-delta, unsigned 8-bit linear",
    5: "sigma-delta, unsigned logarithmic",
}
RISC_OS_C1 = (
    0x20AC, 0x0174, 0x0175, 0x25F0, 0x1FBC0, 0x0176, 0x0177, 0xFFFD,
    0x21E6, 0x21E8, 0x21E9, 0x21E7, 0x2026, 0x2122, 0x2030, 0x2022,
    0x2018, 0x2019, 0x2039, 0x203A, 0x201C, 0x201D, 0x201E, 0x2013,
    0x2014, 0x2212, 0x0152, 0x0153, 0x2020, 0x2021, 0xFB01, 0xFB02,
)


class FormatError(ValueError):
    """Foreign, unsupported, or unrecoverable input. No files are written."""


class DecodeError(ValueError):
    """A recognized sample has a damaged payload; keep its decoded prefix."""


class Bits:
    """A bounded, least-significant-bit-first reader with exact bit accounting."""

    def __init__(self, data, offset):
        self.data = data
        self.start = self.pos = offset * 8

    def read(self, width):
        end = self.pos + width
        if end > len(self.data) * 8:
            raise DecodeError(f"truncated {width}-bit code at bit {self.pos}")
        first = self.pos // 8
        value = int.from_bytes(self.data[first:(end + 7) // 8], "little")
        value = (value >> (self.pos % 8)) & ((1 << width) - 1)
        self.pos = end
        return value


def _lzw(reader, count, output, stats):
    dictionary = [bytes([i]) for i in range(256)] + [None, None]
    previous = None
    width = 9
    while len(output) < count:
        code = reader.read(width)
        stats["codes"] += 1
        if code == 256:
            dictionary = dictionary[:258]
            previous, width = None, 9
            stats["dictionary_resets"] += 1
            continue
        if code == 257:
            stats["end_code_seen"] = True
            raise DecodeError(f"early LZW end: {len(output)} of {count} samples")
        if code < len(dictionary):
            phrase = dictionary[code]
        elif code == len(dictionary) and previous is not None:
            phrase = previous + previous[:1]
            stats["kwkwk_codes"] += 1
        else:
            raise DecodeError(f"invalid LZW dictionary reference {code}")
        if phrase is None:
            raise DecodeError("invalid LZW control reference")
        remaining = count - len(output)
        output.extend(phrase[:remaining])
        if len(phrase) > remaining:
            raise DecodeError("LZW phrase exceeds the declared sample count")
        # Symphony writes EOF using the width of the final data code, including
        # when adding the final dictionary entry would have increased the width.
        if len(output) == count:
            break
        if previous is not None and len(dictionary) < 8192:
            dictionary.append(previous + phrase[:1])
            if len(dictionary) == 1 << width and width < 13:
                width += 1
                stats["maximum_code_bits"] = width
        previous = phrase
    if reader.read(width) != 257:
        raise DecodeError("missing LZW end code after the declared samples")
    stats["end_code_seen"] = True


def _sigma(reader, count, output, stats):
    threshold = max(1, stats["run_threshold"])
    width, small_run = 8, 0
    accumulator = reader.read(8)
    output.append(accumulator)
    while len(output) < count:
        code = reader.read(width)
        stats["codes"] += 1
        if code == 0:
            if width == 9:
                raise DecodeError("sigma-delta width increase beyond nine bits")
            width += 1
            small_run = 0
            stats["width_increases"] += 1
            continue
        delta = -(code >> 1) if code & 1 else code >> 1
        accumulator = (accumulator + delta) & 255
        output.append(accumulator)
        if code & (1 << (width - 1)):
            small_run = 0
        else:
            small_run += 1
            if small_run >= threshold:
                width = max(1, width - 1)
                small_run = 0
                stats["width_decreases"] += 1


def _vidc(code):
    magnitude = ((((code >> 1) & 15) * 8 + 132) << (code >> 5)) - 132
    return -magnitude if code & 1 else magnitude


def _pcm16(decoded, codec):
    if codec == 3:
        return bytes(decoded)
    if codec == 1:
        accumulator = 0
        linear = bytearray()
        for delta in decoded:
            accumulator = (accumulator + delta) & 255
            linear.append(accumulator)
        decoded = linear
    if codec in (1, 2):
        values = ((v if v < 128 else v - 256) * 256 for v in decoded)
    elif codec == 4:
        values = ((v - 128) * 256 for v in decoded)
    elif codec == 0:
        values = (_vidc(v) for v in decoded)
    else:  # Codec 5 has a different logarithmic sign/magnitude arrangement.
        values = (_vidc((v >> 7) | (((~v if v < 128 else v) << 1) & 255))
                  for v in decoded)
    samples = array("h", values)
    if sys.byteorder != "little":
        samples.byteswap()
    return samples.tobytes()


def display_name(raw):
    return "".join(chr(RISC_OS_C1[b - 128] if 128 <= b < 160 else b) for b in raw)


def decode(data):
    """Return (PCM16 bytes, audit dict); perform no filesystem mutations.

    The audit's half-open bit ranges partition every input bit, including
    damaged or unexplained regions. Accounting is not a claim that unexplained
    bytes have known semantics.
    """
    if data[:8] != MAGIC:
        raise FormatError("not a Digital Symphony SySample: exact signature absent")
    if len(data) < 10:
        raise FormatError("recognized SySample, but version/name length is truncated")
    version, name_length = data[8:10]
    if version >= 10:
        raise FormatError(f"unsupported SySample major version {version}")
    payload = 20 + name_length
    if len(data) < payload:
        raise FormatError("recognized SySample, but name/length/loop/codec header is truncated")
    codec = data[payload - 1]
    if codec not in CODECS:
        raise FormatError(f"recognized SySample, unsupported packing method {codec}")
    name = data[10:10 + name_length]
    fields = [int.from_bytes(data[payload - 10 + i:payload - 7 + i], "little") * 2
              for i in (0, 3, 6)]
    count, loop_start, loop_length = fields
    warnings, ranges = [], []

    def region(start, end, role, include_hex=False):
        end = min(end, len(data) * 8)
        if end <= start:
            return
        item = {"start_bit": start, "end_bit": end, "role": role}
        if include_hex and start % 8 == end % 8 == 0:
            item["hex"] = data[start // 8:end // 8].hex()
        ranges.append(item)

    for start, end, role in ((0, 8, "signature"), (8, 9, "version"),
                             (9, 10, "name length"), (10, payload - 10, "name"),
                             (payload - 10, payload - 7, "sample count / 2"),
                             (payload - 7, payload - 4, "loop start / 2"),
                             (payload - 4, payload - 1, "loop length / 2"),
                             (payload - 1, payload, "packing method")):
        region(start * 8, end * 8, role, True)
    stats = {"codes": 0, "dictionary_resets": 0, "kwkwk_codes": 0,
             "maximum_code_bits": 9, "width_increases": 0, "width_decreases": 0}
    decoded = bytearray()
    complete = True
    reader = Bits(data, payload)
    stream_start = payload
    if count == 0:
        # No audio or compressed stream is needed for an empty sample.
        end_bit = payload * 8
    elif codec in (0, 2, 3):
        needed = count * (2 if codec == 3 else 1)
        available = min(needed, len(data) - payload)
        if codec == 3:
            available &= ~1  # A lone byte cannot define a 16-bit sample.
        decoded.extend(data[payload:payload + available])
        end_bit = (payload + available) * 8
        region(payload * 8, end_bit, "audio data")
        if available != needed:
            complete = False
            warnings.append(f"truncated raw audio: {available} of {needed} bytes recovered")
    else:
        try:
            if codec in (4, 5):
                stats["run_threshold"] = reader.read(8)
                region(payload * 8, reader.pos, "sigma-delta run threshold", True)
                stream_start += 1
                if stats["run_threshold"] == 0:
                    warnings.append("zero sigma-delta run threshold treated as one")
                if stats["run_threshold"] > 31:
                    warnings.append("sigma-delta threshold above 31: full-byte OpenMPT/libxmp interpretation; TimPlayer masks to five bits")
                _sigma(reader, count, decoded, stats)
            else:
                _lzw(reader, count, decoded, stats)
        except DecodeError as exc:
            complete = False
            warnings.append(str(exc))
        end_bit = reader.pos
        region(stream_start * 8, end_bit, "compressed audio codes")

    if complete:
        byte_end = (end_bit + 7) // 8
        if end_bit % 8:
            region(end_bit, byte_end * 8, "unused high bits of final code byte")
            if data[byte_end - 1] >> (end_bit % 8):
                warnings.append("nonzero unused high bits in compressed stream")
        stream_end = byte_end
        if count and codec in (1, 4, 5):
            stream_end = stream_start + ((byte_end - stream_start + 3) & ~3)
            region(byte_end * 8, stream_end * 8, "compressed stream word padding", True)
            if any(data[byte_end:stream_end]):
                warnings.append("nonzero compressed stream word padding")
        file_end = (stream_end + 3) & ~3
        region(stream_end * 8, file_end * 8, "file word padding", True)
        if any(data[stream_end:file_end]):
            warnings.append("nonzero file word padding (audio is unaffected)")
        if file_end > len(data):
            warnings.append(f"missing {file_end - len(data)} alignment byte(s)")
        if file_end < len(data):
            region(file_end * 8, len(data) * 8, "unexplained trailing data", True)
            warnings.append(f"{len(data) - file_end} unexplained trailing byte(s) at offset {file_end}; excluded from audio")
    else:
        region(end_bit, len(data) * 8, "unparsed remainder after damaged audio", True)

    pcm = _pcm16(decoded, codec)
    frames = len(pcm) // 2
    if count and not frames:
        raise FormatError("recognized SySample, but no complete audio samples can be recovered: " + "; ".join(warnings))
    loop = None
    if loop_length > 2:
        if loop_start < frames:
            loop_end = min(frames, loop_start + loop_length)
            loop = [loop_start, loop_end]
            if loop_end != loop_start + loop_length:
                warnings.append("repeat extends past recovered audio; WAV loop end clipped")
        else:
            warnings.append("repeat starts outside recovered audio; WAV loop omitted")
    cursor = 0
    for item in ranges:
        if item["start_bit"] != cursor:
            raise AssertionError("internal error: incomplete or overlapping byte accounting")
        cursor = item["end_bit"]
    if cursor != len(data) * 8:
        raise AssertionError("internal error: unaccounted input bits")
    return pcm, {
        "format": "Digital Symphony SySample", "version": version,
        "name": display_name(name), "name_hex": name.hex(),
        "codec": codec, "codec_name": CODECS[codec], "declared_frames": count,
        "decoded_frames": frames, "loop_start": loop_start,
        "loop_length": loop_length, "wav_loop_start_end_exclusive": loop,
        "audio_complete": frames == count, "stream_complete": complete,
        "input_bytes": len(data), "input_sha256": hashlib.sha256(data).hexdigest(),
        "pcm_sha256": hashlib.sha256(pcm).hexdigest(), "warnings": warnings,
        "decoder_statistics": stats, "bit_ranges": ranges,
    }


def _chunk(kind, body):
    return kind + struct.pack("<I", len(body)) + body + b"\0" * (len(body) & 1)


def make_wav(pcm, audit, rate):
    """PCM mono WAV; retain the native name and any usable forward loop."""
    if not 1 <= rate <= 0x7FFFFFFF:
        raise ValueError("rate must be between 1 and 2147483647 Hz")
    chunks = [_chunk(b"fmt ", struct.pack("<HHIIHH", 1, 1, rate, rate * 2, 2, 16))]
    raw_name = bytes.fromhex(audit["name_hex"])
    if raw_name:
        chunks.append(_chunk(b"LIST", b"INFO" + _chunk(b"INAM", raw_name + b"\0")))
    loop = audit["wav_loop_start_end_exclusive"]
    if loop:
        # MIDI note 60 is an export convention, not a recovered root note.
        smpl = struct.pack("<9I", 0, 0, min(0xFFFFFFFF, round(1e9 / rate)), 60, 0, 0, 0, 1, 0)
        smpl += struct.pack("<6I", 0, 0, loop[0], loop[1] - 1, 0, 0)
        chunks.append(_chunk(b"smpl", smpl))
    chunks.append(_chunk(b"data", pcm))
    body = b"WAVE" + b"".join(chunks)
    return b"RIFF" + struct.pack("<I", len(body)) + body


def _prepare_directory(path):
    missing = []
    cursor = path
    while not cursor.exists():
        missing.append(cursor)
        cursor = cursor.parent
    path.mkdir(parents=True, exist_ok=True)
    for directory in missing:
        directory.chmod(directory.stat().st_mode | 0o550)


def _atomic_write(path, data):
    fd, temporary = tempfile.mkstemp(prefix=".dsym-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            os.fchmod(stream.fileno(), 0o644)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def convert(input_file, output_dir, *, rate=DEFAULT_RATE, verbose=False):
    """Validate and decode before creating the output directory or any files."""
    source, destination = Path(input_file), Path(output_dir)
    with source.open("rb") as stream:
        if stream.read(8) != MAGIC:
            raise FormatError("not a Digital Symphony SySample: exact signature absent")
        prefix = stream.read(2)
        if len(prefix) != 2:
            raise FormatError("recognized SySample, truncated header")
        if prefix[0] >= 10:
            raise FormatError(f"unsupported SySample major version {prefix[0]}")
        header_rest = stream.read(prefix[1] + 10)
        if len(header_rest) != prefix[1] + 10:
            raise FormatError("recognized SySample, truncated header")
        if header_rest[-1] not in CODECS:
            raise FormatError(f"recognized SySample, unsupported packing method {header_rest[-1]}")
        data = MAGIC + prefix + header_rest + stream.read()
    pcm, audit = decode(data)
    wav = make_wav(pcm, audit, rate)
    output = destination / (source.name + ".wav")
    if output.resolve() == source.resolve():
        raise FormatError("output would replace the input file")
    audit.update({"input_file": str(source), "output_file": str(output),
                  "wav_rate": rate, "rate_source": "user/export convention; not stored in SySample"})
    _prepare_directory(destination)
    _atomic_write(output, wav)
    if verbose:
        _atomic_write(destination / (source.name + ".json"),
                      (json.dumps(audit, indent=2, ensure_ascii=True) + "\n").encode("utf-8"))
    return output, audit


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputDir", type=Path)
    parser.add_argument("-verbose", "--verbose", action="store_true",
                        help="also write a JSON bit-accounting/diagnostic sidecar")
    parser.add_argument("-rate", "--rate", type=int, default=DEFAULT_RATE,
                        help=f"WAV playback rate; absent from input (default: {DEFAULT_RATE} Hz)")
    args = parser.parse_args(argv)
    try:
        output, audit = convert(args.inputFile, args.outputDir,
                                rate=args.rate, verbose=args.verbose)
    except (OSError, ValueError, OverflowError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    for warning in audit["warnings"]:
        print(f"warning: {warning}", file=sys.stderr)
    if args.verbose:
        print(f"{output}: {audit['decoded_frames']} frames, mono PCM16, {args.rate} Hz")
    return 0


if __name__ == "__main__":
    sys.exit(main())

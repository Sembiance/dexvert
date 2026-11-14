#!/usr/bin/env python3
# Vibe coded by Codex
"""Decode WAVC V1.0 / Interplay ACM v1 to 16-bit PCM WAV; standard library only.

The inverse transform follows libacm (https://github.com/markokr/libacm).
Copyright (c) 2004-2010, Marko Kreen
Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.
THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
"""

import argparse
from array import array
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import sys
import tempfile
import wave

ACM_MAGIC = b"\x97\x28\x03\x01"
WAVC_MAGIC = b"WAVCV1.0"
INVALID_MODES = {1, 2, 25, 28, 30, 31}


class FormatError(ValueError):
    """Unrecognized, unsupported, or unrecoverable input; no output is created."""


class DamagedStream(ValueError):
    """Recognized ACM with a damaged or incomplete block."""


class Bits:
    """LSB-first reader with the encoder's implicit all-zero suffix at EOF."""

    def __init__(self, data, start, end):
        self.data = data
        self.pos = start * 8
        self.end = end * 8
        self.next_byte = start
        self.buffer = 0
        self.available = 0

    def get(self, width):
        if self.available < width:
            stop = min(self.next_byte + 8, self.end // 8)
            self.buffer |= int.from_bytes(self.data[self.next_byte:stop], "little") << self.available
            self.available += (stop - self.next_byte) * 8
            self.next_byte = stop
            # CBitStream::flush deliberately does not emit its pending zero run.
            # The declared sample count, not physical EOF, terminates decoding.
            self.available = max(self.available, width)
        value = self.buffer & ((1 << width) - 1)
        self.buffer >>= width
        self.available -= width
        self.pos += width
        return value


def header(data):
    """Recognize exact signatures, and interpret redundant header fields explicitly."""
    notes = []
    outer = None
    if data[:8] == WAVC_MAGIC:
        if len(data) < 28:
            raise FormatError("recognized WAVC V1.0, but its 28-byte header is truncated")
        raw, size, offset, channels, depth, rate, unused = struct.unpack_from("<IIIHHHH", data, 8)
        outer = dict(uncompressed_bytes=raw, compressed_bytes=size, acm_offset=offset,
                     channels=channels, bits_per_sample=depth, sample_rate=rate,
                     unused_word=unused)
        if offset < 28 or offset + 14 > len(data):
            raise FormatError("recognized WAVC, but the ACM pointer does not address a complete header")
        if data[offset:offset + 4] != ACM_MAGIC:
            raise FormatError("recognized WAVC, but its declared payload is not Interplay ACM v1")
        if depth != 16:
            notes.append(f"WAVC bit depth {depth} contradicts ACM's fixed 16-bit output; using 16")
        end = offset + size
        if size < 14 or end > len(data):
            notes.append("invalid/truncated WAVC compressed extent; using bytes through physical EOF")
            end = len(data)
    elif data[:4] == ACM_MAGIC:
        offset, end = 0, len(data)
    else:
        raise FormatError("not WAVC V1.0 or Interplay ACM v1 (signature/version mismatch)")
    if offset + 14 > end:
        raise FormatError("recognized ACM v1, but its 14-byte header is truncated")
    count, inner_channels, inner_rate, packed = struct.unpack_from("<IHHH", data, offset + 4)
    level, rows = packed & 15, packed >> 4
    if not rows:
        raise FormatError("recognized ACM, but zero rows leaves no decodable block geometry")
    channels, rate = inner_channels, inner_rate
    if outer:
        # The wrapper describes playback; the inner header describes the coded stream.
        if outer["channels"] in (1, 2):
            channels = outer["channels"]
        if outer["sample_rate"]:
            rate = outer["sample_rate"]
        if channels != inner_channels or rate != inner_rate:
            notes.append("WAVC/ACM playback metadata disagree; using valid WAVC playback fields")
        if raw != count * 2:
            notes.append("WAVC uncompressed size disagrees with ACM sample count; using ACM count")
    if channels not in (1, 2) or not rate:
        raise FormatError("recognized ACM, but no valid mono/stereo channel count or nonzero rate")
    if count % channels:
        notes.append("sample count ends within a channel frame; final incomplete frame will be omitted")
    return dict(container="WAVC V1.0" if outer else "Interplay ACM v1", wrapper=outer,
                acm_offset=offset, payload_end=end, input_bytes=len(data),
                sample_values=count, acm_channels=inner_channels, acm_sample_rate=inner_rate,
                channels=channels, sample_rate=rate, level=level, rows=rows,
                columns=1 << level, warnings=notes)


def column_indices(bits, mode, rows):
    """Read one column, including complete final grouped codewords."""
    get = bits.get
    if mode == 0:
        return [0] * rows
    if mode in INVALID_MODES:
        raise DamagedStream(f"reserved column mode {mode} at bit {bits.pos - 5}")
    if 3 <= mode <= 16:
        middle = 1 << (mode - 1)
        return [get(mode) - middle for _ in range(rows)]
    result = []
    if mode in (19, 22, 29):
        width, radix, group = {19: (5, 3, 3), 22: (7, 5, 3), 29: (7, 11, 2)}[mode]
        while len(result) < rows:
            code = get(width)
            if code >= radix ** group:
                raise DamagedStream(f"invalid base-{radix} group {code} at bit {bits.pos - width}")
            for _ in range(group):
                result.append(code % radix - radix // 2)
                code //= radix
        return result[:rows]
    pair_zero = mode in (17, 20, 23, 26)
    near = (-2, -1, 1, 2)
    far = (-3, -2, 2, 3)
    wide = (-4, -3, -2, -1, 1, 2, 3, 4)
    while len(result) < rows:
        if get(1) == 0:
            result.extend((0, 0) if pair_zero else (0,))
            continue
        if pair_zero and get(1) == 0:
            result.append(0)
        elif mode in (17, 18):
            result.append(2 * get(1) - 1)
        elif mode in (20, 21):
            result.append(near[get(2)])
        elif mode in (23, 24):
            result.append(2 * get(1) - 1 if get(1) == 0 else far[get(2)])
        else:  # 26 / 27
            result.append(wide[get(3)])
    return result[:rows]


def signed32(value):
    return ((value + 0x80000000) & 0xffffffff) - 0x80000000


def synthesize(block, history, level, rows):
    """Stateful integer inverse subband transform, including 32-bit wraparound."""
    if not level:
        return
    columns = 1 << level
    step = 1 if level > 9 else (2048 >> level) - 2
    for row_start in range(0, rows, step):
        base = row_start * columns
        length = columns // 2
        count = min(step, rows - row_start) * 2
        hist = 0
        first = True
        while length:
            for lane in range(length):
                h = hist + lane * 2
                a, b = history[h], history[h + 1]
                pos = base + lane
                for _ in range(count // 2):
                    c, d = block[pos], block[pos + length]
                    block[pos] = signed32(a + 2 * b + c)
                    block[pos + length] = signed32(2 * c - b - d)
                    a, b = c, d
                    pos += 2 * length
                history[h], history[h + 1] = a, b
            if first:
                for pos in range(base, base + count * length, length):
                    block[pos] = signed32(block[pos] + 1)
                first = False
            hist += length * 2
            length //= 2
            count *= 2


def bit_region(data, start, end, role):
    """Describe an exact half-open bit span, including its non-audio values."""
    item = dict(role=role, start_bit=start, end_bit=end)
    if end > start:
        lo, hi = start // 8, (end + 7) // 8
        raw = data[lo:hi]
        item["storage_sha256"] = hashlib.sha256(raw).hexdigest()
        if end - start <= 64:
            item["value"] = (int.from_bytes(raw, "little") >> (start % 8)) & ((1 << (end - start)) - 1)
        else:
            # Mask boundary bits before assessing padding; no huge integer allocation.
            nonzero = bool(raw[0] & (0xff << (start % 8))) if len(raw) == 1 else bool(
                raw[0] & (0xff << (start % 8)) or any(raw[1:-1]) or
                raw[-1] & ((1 << ((end - 1) % 8 + 1)) - 1))
            item["all_zero"] = not nonzero
    return item


def decode(data, pcm, trace=False):
    """Write recoverable complete blocks to a binary PCM sink and return an audit."""
    info = header(data)
    start = info["acm_offset"] + 14
    bits = Bits(data, start, info["payload_end"])
    rows, columns, level = info["rows"], info["columns"], info["level"]
    block_size = rows * columns
    history = [0] * (2 * columns - 2)
    remaining = info["sample_values"]
    written, blocks, last_good = 0, 0, bits.pos
    modes = Counter()
    traces = []
    error = None
    while remaining:
        block_start = bits.pos
        try:
            power, step = bits.get(4), bits.get(16)
            limit = 1 << power
            block = array("i", [0]) * block_size
            column_spans = []
            for col in range(columns):
                col_start = bits.pos
                mode = bits.get(5)
                indices = column_indices(bits, mode, rows)
                if min(indices) < -limit or max(indices) >= limit:
                    raise DamagedStream(f"coefficient outside amplitude table in column {col}")
                for row, index in enumerate(indices):
                    block[row * columns + col] = index * step
                modes[mode] += 1
                if trace:
                    column_spans.append(dict(column=col, mode=mode,
                                             start_bit=col_start, end_bit=bits.pos))
            synthesize(block, history, level, rows)
        except DamagedStream as exc:
            error = str(exc)
            info["warnings"].append(f"stopped before damaged block {blocks}: {error}")
            break
        take = min(remaining, block_size)
        # Frames may straddle blocks at level 0; truncate to a frame only at EOF.
        values = array("H", ((value >> level) & 0xffff for value in block[:take]))
        if sys.byteorder != "little":
            values.byteswap()
        pcm.write(values.tobytes())
        written += take
        remaining -= take
        blocks += 1
        last_good = bits.pos
        if trace:
            traces.append(dict(index=blocks - 1, start_bit=block_start, end_bit=bits.pos,
                               power=power, amplitude_step=step, output_values=take,
                               discarded_transform_values=block_size - take, columns=column_spans))
    written -= written % info["channels"]
    pcm.truncate(written * 2)
    regions = []
    if info["wrapper"]:
        regions.append(bit_region(data, 0, 28 * 8, "WAVC header"))
        if info["acm_offset"] > 28:
            regions.append(bit_region(data, 28 * 8, info["acm_offset"] * 8,
                                      "uninterpreted wrapper gap (not part of ACM)"))
            info["warnings"].append("wrapper contains an uninterpreted gap before ACM")
    regions.append(bit_region(data, info["acm_offset"] * 8, start * 8, "ACM header"))
    physical_end = min(last_good, bits.end)
    regions.append(dict(role="complete coded blocks", start_bit=start * 8, end_bit=physical_end))
    if error:
        regions.append(bit_region(data, physical_end, bits.end, "damaged/incomplete coded remainder"))
    else:
        aligned = min((physical_end + 7) // 8 * 8, bits.end)
        if aligned > physical_end:
            regions.append(bit_region(data, physical_end, aligned, "unused final-byte high bits"))
        if aligned < bits.end:
            regions.append(bit_region(data, aligned, bits.end, "uninterpreted bytes after coded audio"))
            info["warnings"].append(f"{(bits.end - aligned) // 8} trailing ACM bytes have no defined audio meaning")
    if bits.end < len(data) * 8:
        regions.append(bit_region(data, bits.end, len(data) * 8, "bytes outside declared WAVC payload"))
        info["warnings"].append("bytes follow the declared WAVC compressed extent")
    info.update(output_sample_values=written, output_frames=written // info["channels"],
                decoded_blocks=blocks, expected_blocks=(info["sample_values"] + block_size - 1) // block_size,
                block_values=block_size, mode_counts=dict(sorted(modes.items())),
                coded_end_bit=last_good, implicit_zero_bits=max(0, last_good - bits.end),
                regions=regions, complete=remaining == 0,
                input_sha256=hashlib.sha256(data).hexdigest())
    if trace:
        info["blocks"] = traces
    if remaining and not written:
        raise FormatError("recognized ACM but no complete audio block could be recovered: " + str(error))
    return info


def readable_directory(path):
    """Create needed directories and make newly created ones group-traversable."""
    missing = []
    current = path
    while not current.exists():
        missing.append(current)
        current = current.parent
    path.mkdir(parents=True, exist_ok=True)
    for current in reversed(missing):
        current.chmod(current.stat().st_mode | 0o750)


def convert(input_file, output_dir, verbose=False):
    """Default persistent output is exactly one WAV; invalid input creates nothing."""
    source, destination = Path(input_file), Path(output_dir)
    # Check the short signature before loading potentially large unrelated files.
    with source.open("rb") as stream:
        prefix = stream.read(8)
        if prefix != WAVC_MAGIC and prefix[:4] != ACM_MAGIC:
            raise FormatError("not WAVC V1.0 or Interplay ACM v1 (signature/version mismatch)")
        data = prefix + stream.read()
    target = destination / (source.stem + ".wav")
    if target.resolve() == source.resolve():
        raise FormatError("output WAV would overwrite the compressed input; choose another output directory")
    with tempfile.TemporaryFile() as pcm:
        info = decode(data, pcm, trace=verbose)
        output_bytes = info["output_sample_values"] * 2
        # Ordinary RIFF has 32-bit lengths; use the standardized RF64 extension if needed.
        rf64 = output_bytes + 36 > 0xffffffff
        readable_directory(destination)
        fd, temporary = tempfile.mkstemp(prefix=".infinity-sound-", dir=destination)
        try:
            with os.fdopen(fd, "wb") as out:
                if rf64:
                    channels, rate = info["channels"], info["sample_rate"]
                    out.write(struct.pack("<4sI4s4sIQQQI", b"RF64", 0xffffffff, b"WAVE",
                                          b"ds64", 28, output_bytes + 72, output_bytes,
                                          info["output_frames"], 0))
                    out.write(struct.pack("<4sIHHIIHH4sI", b"fmt ", 16, 1, channels, rate,
                                          rate * channels * 2, channels * 2, 16, b"data", 0xffffffff))
                    pcm.seek(0)
                    shutil.copyfileobj(pcm, out)
                else:
                    with wave.open(out, "wb") as wav:
                        wav.setnchannels(info["channels"])
                        wav.setsampwidth(2)
                        wav.setframerate(info["sample_rate"])
                        wav.setnframes(info["output_frames"])
                        pcm.seek(0)
                        while True:
                            chunk = pcm.read(1024 * 1024)
                            if not chunk:
                                break
                            wav.writeframesraw(chunk)
                os.fchmod(out.fileno(), 0o644)
            os.replace(temporary, target)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    if verbose:
        audit = destination / (source.stem + ".infinityEngineSound.json")
        audit.write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")
        audit.chmod(0o644)
    return target, info


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputDir", type=Path)
    parser.add_argument("-verbose", "--verbose", action="store_true",
                        help="also write a JSON header, block/column bit-span and recovery audit")
    args = parser.parse_args(argv)
    try:
        target, info = convert(args.inputFile, args.outputDir, args.verbose)
    except (FormatError, OSError, MemoryError, OverflowError) as exc:
        print(f"infinityEngineSound: {exc}", file=sys.stderr)
        return 1
    for warning in info["warnings"]:
        print(f"warning: {warning}", file=sys.stderr)
    if args.verbose:
        print(f"{target}: {info['output_frames']} frames, {info['channels']} channel(s), "
              f"{info['sample_rate']} Hz, {info['decoded_blocks']} blocks")
    return 0 if info["complete"] else 2


if __name__ == "__main__":
    sys.exit(main())

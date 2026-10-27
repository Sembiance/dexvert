#!/usr/bin/env python3
# Vibe coded by Codex
"""Extract Apple IIgs ASIF waveforms. Python 3.10+, standard library only.

See appleIIgsSampledInstrument.txt for the wire format, producer deviations,
recovery rules, and the distinction between samples and synthesized notes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys
import tempfile
from dataclasses import dataclass, field


DEFAULT_UNKNOWN_RATE = 8363


class ASIFError(ValueError):
    """Recognized ASIF that cannot be converted under the requested policy."""


class WrongFormat(ASIFError):
    """The input does not carry the FORM ASIF signature."""


@dataclass
class Document:
    data: bytes
    form_size: int
    chunks: list = field(default_factory=list)
    waves: list = field(default_factory=list)
    instruments: list = field(default_factory=list)
    fields: list = field(default_factory=list)
    warnings: list = field(default_factory=list)

    def mark(self, start, end, name, value=None):
        if end > start:
            item = {"offset": start, "length": end - start, "field": name}
            if value is not None:
                item["value"] = value
            self.fields.append(item)

    def warn(self, message):
        if message not in self.warnings:
            self.warnings.append(message)

    def audit(self):
        """Produce a disjoint byte ledger; opaque regions stay explicitly opaque."""
        spans = sorted(self.fields, key=lambda x: x["offset"])
        cursor = 0
        for span in spans:
            if span["offset"] != cursor:
                raise AssertionError(f"byte ledger discontinuity at {cursor}")
            cursor += span["length"]
        if cursor != len(self.data):
            raise AssertionError(f"byte ledger ends at {cursor}, not {len(self.data)}")
        return spans


class Reader:
    def __init__(self, doc, start, end, label):
        self.doc, self.pos, self.end, self.label = doc, start, end, label

    def take(self, count, name, fmt=None):
        if self.pos + count > self.end:
            raise ASIFError(f"truncated {self.label}.{name} at offset {self.pos}")
        start = self.pos
        self.pos += count
        raw = self.doc.data[start:self.pos]
        value = struct.unpack(fmt, raw)[0] if fmt else raw.hex()
        self.doc.mark(start, self.pos, f"{self.label}.{name}", value)
        return value if fmt else raw

    def byte(self, name):
        return self.take(1, name, "<B")

    def word(self, name):
        return self.take(2, name, "<H")

    def long(self, name):
        return self.take(4, name, "<I")

    def name(self):
        length = self.byte("name_length")
        raw = self.take(length, "name_bytes")
        return {"length": length, "hex": raw.hex(), "display": display_text(raw)}

    def remainder(self, name):
        self.doc.mark(self.pos, self.end, f"{self.label}.{name}")
        self.pos = self.end


def display_text(raw):
    # Exact bytes are kept separately. No encoding guesses or high-bit stripping.
    return "".join(chr(c) if 32 <= c < 127 else f"\\x{c:02x}" for c in raw)


def instrument_length(data, start):
    if start >= len(data):
        return None
    name_end = start + 1 + data[start]
    if name_end + 34 > len(data):
        return None
    return 1 + data[start] + 34 + 6 * (data[name_end + 32] + data[name_end + 33])


def read_instrument(doc, start, end, index):
    r = Reader(doc, start, end, f"INST[{index}]")
    inst = {"offset": start, "complete": False, "envelope": [], "a_waves": [], "b_waves": []}
    doc.instruments.append(inst)
    try:
        inst["name"] = r.name()
        inst["sample_number"] = r.word("sample_number")
        for i in range(8):
            point = r.byte(f"envelope[{i}].breakpoint")
            increment = r.word(f"envelope[{i}].increment_8_8")
            inst["envelope"].append({"breakpoint": point, "increment_8_8": increment})
            if point > 127:
                doc.warn(f"INST {index}: envelope breakpoint exceeds 127")
        for name in ("release_segment", "priority_increment", "pitch_bend_range",
                     "vibrato_depth", "vibrato_speed", "unused_update_rate",
                     "a_count", "b_count"):
            inst[name] = r.byte(name)
        for side in ("a", "b"):
            previous = -1
            for i in range(inst[f"{side}_count"]):
                label = f"{side}_waves[{i}]"
                top = r.byte(f"{label}.top_key")
                address = r.byte(f"{label}.address_page")
                size = r.byte(f"{label}.size_resolution")
                mode = r.byte(f"{label}.doc_mode")
                pitch = r.take(2, f"{label}.relative_pitch_8_8", "<h")
                length = 256 << ((size >> 3) & 7)
                entry = {"top_key": top, "address_page": address,
                         "size_resolution": size, "doc_mode": mode,
                         "relative_pitch_8_8": pitch, "relative_pitch_semitones": pitch / 256,
                         "table_bytes": length, "resolution": size & 7,
                         "bank_bit": (size >> 6) & 1, "unused_size_bit": size >> 7,
                         "effective_address": (address * 256) & ~(length - 1),
                         "halted": bool(mode & 1), "mode": (mode >> 1) & 3,
                         "interrupt_enabled": bool(mode & 8), "channel": mode >> 4}
                inst[f"{side}_waves"].append(entry)
                if top < previous or top > 127:
                    doc.warn(f"INST {index}: invalid {side.upper()} key split ordering")
                previous = top
                if size & 192:
                    doc.warn(f"INST {index}: nonzero upper DOC size bits; bank is not available in IIgs ASIF")
                if mode & 8:
                    doc.warn(f"INST {index}: DOC interrupt bit is set, contrary to the ASIF specification")
            if previous != 127 and inst[f"{side}_count"]:
                doc.warn(f"INST {index}: {side.upper()} wave list does not end at key 127")
        inst["complete"] = True
        if r.pos < r.end:
            doc.warn(f"INST {index}: unrecognized extension after the defined instrument fields")
        if inst["unused_update_rate"]:
            doc.warn(f"INST {index}: unused UpdateRate is nonzero; the specified envelope clock remains 200 Hz")
        if inst["pitch_bend_range"] not in (1, 2, 4):
            doc.warn(f"INST {index}: pitch-bend range is outside the specified values 1, 2, 4")
        if not 1 <= inst["release_segment"] <= 7:
            doc.warn(f"INST {index}: invalid release segment")
    except ASIFError as exc:
        doc.warn(str(exc))
    r.remainder("undecoded_or_truncated_remainder")


def read_wave(doc, start, end, declared_size, chunk_offset, index):
    r = Reader(doc, start, end, f"WAVE[{index}]")
    wave = {"offset": start, "chunk_offset": chunk_offset, "samples": [], "complete_header": False}
    doc.waves.append(wave)
    try:
        wave["name"] = r.name()
        wave["wave_size_field"] = r.word("wave_size")
        count = r.word("sample_count")
        wave["sample_count"] = count
        if not count:
            doc.warn(f"WAVE {index}: zero sample-table entries")
        for i in range(count):
            label = f"sample[{i}]"
            wave["samples"].append({
                "location": r.word(f"{label}.location"),
                "pages": r.word(f"{label}.pages"),
                "original_frequency_raw": r.long(f"{label}.original_frequency_fixed"),
                "sample_rate_raw": r.long(f"{label}.sample_rate_fixed")})
        wave["complete_header"] = True
        wave["data_offset"] = r.pos
        prefix = r.pos - start
        available = end - r.pos
        declared_data_size = declared_size - prefix
        size = wave["wave_size_field"]
        if declared_data_size == size + 1:
            wave["length_convention"] = "standard_minus_one"
        elif declared_data_size == size:
            wave["length_convention"] = "legacy_byte_count"
        else:
            wave["length_convention"] = "inconsistent"
            doc.warn(f"WAVE {index}: chunk length and WaveSize disagree; using only the bounded declared data")
        # A chunk boundary is stronger evidence than an inconsistent 16-bit length.
        wave["data_length"] = available
        wave["zero_control_bytes"] = doc.data[r.pos:end].count(0)
        r.remainder("unsigned_8_bit_wave_data_including_zero_controls")
    except ASIFError as exc:
        doc.warn(str(exc))
        r.remainder("undecoded_truncated_wave_header")


def parse_asif(data):
    if len(data) < 12 or data[:4] != b"FORM" or data[8:12] != b"ASIF":
        raise WrongFormat("not an Apple IIgs FORM ASIF file")
    form_size = int.from_bytes(data[4:8], "big")
    doc = Document(data, form_size)
    doc.mark(0, 4, "FORM.id", "FORM")
    doc.mark(4, 8, "FORM.size_big_endian", form_size)
    doc.mark(8, 12, "FORM.type", "ASIF")
    declared_end = 8 + form_size
    limit = min(len(data), max(12, declared_end))
    if declared_end > len(data):
        doc.warn(f"FORM is truncated: declares {declared_end} bytes, has {len(data)}")
    if form_size < 4:
        doc.warn("FORM length is smaller than its type field")
    p = 12
    while p < limit:
        if limit - p < 8:
            doc.mark(p, limit, "FORM.incomplete_chunk_header")
            doc.warn(f"incomplete chunk header at offset {p}")
            p = limit
            break
        tag = data[p:p + 4]
        if any(c < 32 or c > 126 for c in tag):
            doc.mark(p, limit, "FORM.unparseable_remainder")
            doc.warn(f"invalid chunk ID at {p}; remaining FORM bytes are opaque (no signature scanning)")
            p = limit
            break
        n = int.from_bytes(data[p + 4:p + 8], "big")
        effective = n
        start = p + 8
        if tag == b"INST":
            expected = instrument_length(data, start)
            if expected is not None and n == expected << 8 and start + n > limit:
                effective = expected
                doc.warn(f"INST at {p}: repaired little-endian low size word ({n} -> {expected})")
            elif expected is not None and n == 0:
                effective = expected
                doc.warn(f"INST at {p}: zero chunk size; used its self-described length {expected}")
            # NoiseTracker sizes FORM using the pre-alignment waveform length.
            if (expected is not None and effective == expected
                    and 0 < start + expected - declared_end <= 2
                    and start + expected <= len(data)):
                limit = start + expected
                doc.warn("FORM omits one or two bytes of the final self-described INST; recovered those bytes")
        end = min(start + effective, limit)
        name = tag.decode("ascii")
        doc.mark(p, p + 4, "chunk.id", name)
        doc.mark(p + 4, p + 8, "chunk.size_big_endian", n)
        doc.chunks.append({"id": name, "offset": p, "size": n,
                           "effective_size": effective, "available_size": end - start})
        if start + effective > limit:
            doc.warn(f"{name} at {p}: payload truncated ({end - start} of {effective} bytes available)")
        if tag == b"WAVE":
            read_wave(doc, start, end, effective, p, len(doc.waves))
        elif tag == b"INST":
            read_instrument(doc, start, end, len(doc.instruments))
        elif tag in (b"NAME", b"AUTH", b"ANNO", b"(c) "):
            raw = data[start:end]
            value = {"hex": raw.hex(), "ascii_escaped": display_text(raw)}
            if raw and raw[0] == len(raw) - 1:
                value["pascal_interpretation"] = display_text(raw[1:])
            doc.mark(start, end, f"{name}.text_bytes", value)
        else:
            doc.mark(start, end, f"{name}.opaque_extension")
            doc.warn(f"unknown IFF chunk {name!r} retained in the audit; its semantics are not implemented")
        p = end
        if end < start + effective:
            break
        if effective & 1:
            if p < limit:
                doc.mark(p, p + 1, f"{name}.iff_pad", data[p])
                if data[p]:
                    doc.warn(f"{name} at {start - 8}: nonzero IFF pad byte")
                p += 1
            else:
                doc.warn(f"{name} at {start - 8}: missing IFF pad byte")
    if p < len(data):
        zero = not any(data[p:])
        doc.mark(p, len(data), "outside_FORM.zero_fill" if zero else "outside_FORM.opaque_bytes")
        if zero:
            doc.warn(f"{len(data) - p} zero fill bytes follow FORM; excluded from audio")
        else:
            doc.warn(f"{len(data) - p} nonzero/opaque bytes follow FORM; not interpreted as audio")
    if len(doc.waves) != 1:
        doc.warn(f"ASIF requires one WAVE chunk; found {len(doc.waves)}")
    if not doc.instruments:
        doc.warn("missing INST chunk; waveform extraction can still recover bounded sample data")
    doc.audit()
    return doc


# A producer's instrument template, not a filename or a corpus-specific ID.
# Confirmed against AudioZap 1.2s's embedded ASIF writer template.
AZ_ENVELOPE = [(127, 16384), (0, 512)] + [(0, 0)] * 6


def is_audiozap(inst):
    return (inst.get("sample_number") == 1
            and [(x["breakpoint"], x["increment_8_8"]) for x in inst["envelope"]] == AZ_ENVELOPE
            and [inst.get(k) for k in ("release_segment", "priority_increment", "pitch_bend_range",
                                      "vibrato_depth", "vibrato_speed", "unused_update_rate")]
            == [1, 32, 0, 0, 0, 0])


def sample_rate(doc, wave, sample, override, unknown_rate, legacy_hz):
    if override is not None:
        return override, "explicit --rate override"
    value = sample["sample_rate_raw"]
    original = sample["original_frequency_raw"]
    legacy = wave["length_convention"] == "legacy_byte_count"
    if not value:
        if unknown_rate is None:
            return None, "sample rate is explicitly unknown; supply --rate or --unknown-rate"
        doc.warn(f"original sample rate is unknown; using fallback {unknown_rate:g} Hz")
        return unknown_rate, "fallback playback rate (--unknown-rate); original recording rate is absent"
    if legacy and sample["location"] == 0:
        if original == 0 and any(is_audiozap(x) for x in doc.instruments):
            if value > 799:
                return None, "rate exceeds AudioZap's 1..799 UI range; integer-Hz versus DOC-register intent is ambiguous; supply --rate"
            return value * 1645 / 32, "AudioZap DOC frequency units × 1645/32 Hz (nominal software rate)"
        if original == value and value <= 65535:
            if not legacy_hz:
                return None, "untagged equal-frequency legacy fields; integer-Hz interpretation requires --legacy-hz or --rate"
            return float(value), "explicit --legacy-hz interpretation of untagged equal-frequency fields"
        return None, "untagged legacy rate encoding is ambiguous; supply --rate"
    # Apple's Fixed: signed 16.16, little-endian, fraction in the low word.
    signed = value if value < 0x80000000 else value - 0x100000000
    if signed <= 0:
        return None, "invalid nonpositive Fixed sample rate; supply --rate"
    return signed / 65536, "Apple signed 16.16 Fixed Hz"


@dataclass
class Output:
    label: str
    pcm: bytes
    rate: int
    rate_exact: float
    rate_source: str
    source_offset: int
    loop: bool = False
    notes: list = field(default_factory=list)

    def metadata(self):
        return {"label": self.label, "frames": len(self.pcm), "sample_rate": self.rate,
                "exact_rate": self.rate_exact, "rate_source": self.rate_source,
                "source_offset": self.source_offset, "loop": self.loop, "notes": self.notes,
                "pcm_sha256": hashlib.sha256(self.pcm).hexdigest()}


def extract(doc, rate=None, unknown_rate=DEFAULT_UNKNOWN_RATE, legacy_hz=False):
    """Extract bounded sample records and additional referenced oscillator regions.

    This is sample extraction, not a performance of the Note Synthesizer.
    Stops are DOC zero bytes; envelopes and oscillator interactions are decoded
    but deliberately do not alter the sample data. Missing rates use 8363 Hz;
    passing unknown_rate=None explicitly disables this fallback.
    """
    outputs, failures = [], []
    for wi, wave in enumerate(doc.waves):
        if not wave["complete_header"]:
            failures.append(f"WAVE {wi}: incomplete sample table")
            continue
        data_start = wave["data_offset"]
        data_end = data_start + wave["data_length"]
        for si, sample in enumerate(wave["samples"]):
            legacy = wave["length_convention"] == "legacy_byte_count"
            # Zero Location is an established WaveData-relative producer deviation.
            if legacy and len(wave["samples"]) == 1 and sample["location"] == 0:
                start = data_start
            else:
                start = wave["chunk_offset"] + sample["location"]
            if not data_start <= start < data_end:
                failures.append(f"WAVE {wi} sample {si}: location {sample['location']} is outside WaveData")
                continue
            if legacy and len(wave["samples"]) == 1:
                # AudioZap floors pages; NoiseTracker rounds them up. WaveSize is exact.
                end = data_end
            else:
                end = min(data_end, start + sample["pages"] * 256)
                if start + sample["pages"] * 256 > data_end:
                    doc.warn(f"WAVE {wi} sample {si}: page extent exceeds available WaveData; clipped")
            exact, source = sample_rate(doc, wave, sample, rate, unknown_rate, legacy_hz)
            if exact is None:
                failures.append(f"WAVE {wi} sample {si}: {source}")
                continue
            rounded = int(math.floor(exact + 0.5))
            if not 1 <= rounded <= 0xFFFFFFFF:
                failures.append(f"WAVE {wi} sample {si}: rate cannot be represented by PCM WAV")
                continue
            entries = []
            for ii, inst in enumerate(doc.instruments):
                number = inst.get("sample_number")
                if number != si and not (legacy and len(wave["samples"]) == 1 and number == 1):
                    continue
                for side in ("a", "b"):
                    for ei, entry in enumerate(inst[f"{side}_waves"]):
                        entries.append((ii, side, ei, entry))
            # The whole stored sample is useful even if it exceeds a DOC table.
            regions = [(start, end, f"wave{wi + 1:02d}_sample{si + 1:02d}", [])]
            extra = {}
            for ii, side, ei, entry in entries:
                address = entry["effective_address"]
                if entry["bank_bit"]:
                    failures.append(f"INST {ii}: oscillator requests a bank absent from IIgs wave RAM")
                    continue
                if address:
                    a = start + address
                    z = min(end, a + entry["table_bytes"])
                    if a >= end:
                        failures.append(f"INST {ii} {side.upper()}{ei}: waveform address lies beyond the stored sample")
                    else:
                        extra.setdefault((a, z), []).append(entry)
                else:
                    regions[0][3].append(entry)
            for (a, z), refs in sorted(extra.items()):
                regions.append((a, z, f"wave{wi + 1:02d}_sample{si + 1:02d}_offset{a - start:05d}", refs))
            for a, z, label, refs in regions:
                raw = doc.data[a:z]
                stop = raw.find(b"\0")
                notes = []
                if stop >= 0:
                    notes.append(f"DOC zero control at file offset {a + stop}; {len(raw) - stop} bytes after the playable prefix excluded")
                    if any(raw[stop + 1:]):
                        notes.append("Nonzero bytes follow the first stop: retained in the byte audit, not played through as PCM")
                    raw = raw[:stop]
                if not raw:
                    failures.append(f"{label}: no playable samples (empty extent or immediate DOC stop)")
                    continue
                loop = (stop < 0 and any(e["mode"] == 0 and len(raw) == e["table_bytes"] for e in refs))
                outputs.append(Output(label, raw, rounded, exact, source, a, loop, notes))
    return outputs, failures


def riff_chunk(tag, payload):
    return tag + struct.pack("<I", len(payload)) + payload + (b"\0" if len(payload) & 1 else b"")


def wav_bytes(output):
    fmt = struct.pack("<HHIIHH", 1, 1, output.rate, output.rate, 1, 8)
    payload = b"WAVE" + riff_chunk(b"fmt ", fmt) + riff_chunk(b"data", output.pcm)
    # PCM extraction has no chosen MIDI root or note duration. Do not invent
    # a WAV smpl root note or bake a performance into the source waveform.
    return b"RIFF" + struct.pack("<I", len(payload)) + payload


def write_readable(path, data):
    """Atomic per-file replacement; ensure user and group read permission."""
    path = Path(path)
    fd, temporary = tempfile.mkstemp(prefix=".asif-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            os.fchmod(f.fileno(), 0o664)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def mkdir_readable(path):
    path = Path(path)
    missing = []
    current = path
    while not current.exists():
        missing.append(current)
        current = current.parent
    path.mkdir(parents=True, exist_ok=True)
    for directory in missing:
        os.chmod(directory, directory.stat().st_mode | 0o550)


def save_outputs(doc, outputs, failures, input_path, output_dir, verbose=False):
    if not outputs:
        raise ASIFError("; ".join(failures) or "no recoverable waveform data")
    output_dir, input_path = Path(output_dir), Path(input_path)
    # Keep the whole basename: foo and foo.aif must not collide.
    basename = input_path.name
    names = [f"{basename}.wav" if len(outputs) == 1 else f"{basename}.{x.label}.wav" for x in outputs]
    for name in names + ([f"{basename}.asif.json"] if verbose else []):
        target = output_dir / name
        if target.resolve() == input_path.resolve():
            raise ASIFError("output path would overwrite the input")
        if target.exists() and target.is_dir():
            raise ASIFError(f"output target is a directory: {target}")
    # Build and validate all bytes before creating any directory or output file.
    payloads = [(name, wav_bytes(output)) for name, output in zip(names, outputs)]
    if verbose:
        audit = {"format": "Apple IIgs ASIF", "source_size": len(doc.data),
                 "source_sha256": hashlib.sha256(doc.data).hexdigest(),
                 "source_hex": doc.data.hex(), "fields": doc.audit(),
                 "chunks": doc.chunks, "waves": doc.waves, "instruments": doc.instruments,
                 "warnings": doc.warnings, "skipped_parts": failures,
                 "outputs": [dict(x.metadata(), file=n) for x, n in zip(outputs, names)]}
        payloads.append((f"{basename}.asif.json", (json.dumps(audit, indent=2) + "\n").encode()))
    mkdir_readable(output_dir)
    for name, payload in payloads:
        write_readable(output_dir / name, payload)
    return [output_dir / n for n in names]


def positive_rate(value):
    number = float(value)
    if not math.isfinite(number) or not 0.5 <= number <= 0xFFFFFFFF:
        raise argparse.ArgumentTypeError("rate must be finite and between 0.5 and 4294967295 Hz")
    return number


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("inputFile", type=Path)
    p.add_argument("outputDir", type=Path)
    p.add_argument("-verbose", "--verbose", action="store_true", help="also write a lossless JSON byte audit")
    p.add_argument("--rate", type=positive_rate, help="explicit playback rate in Hz for all extracted samples")
    p.add_argument("--unknown-rate", type=positive_rate, default=DEFAULT_UNKNOWN_RATE,
                   help="fallback playback rate when SampRate is zero (default: 8363 Hz)")
    p.add_argument("--legacy-hz", action="store_true",
                   help="explicitly interpret equal nonzero legacy frequency fields as integer Hz")
    args = p.parse_args(argv)
    try:
        doc = parse_asif(args.inputFile.read_bytes())
        outputs, failures = extract(doc, args.rate, args.unknown_rate, args.legacy_hz)
        paths = save_outputs(doc, outputs, failures, args.inputFile, args.outputDir, args.verbose)
        for warning in doc.warnings + failures:
            print(f"warning: {warning}", file=sys.stderr)
        for path in paths:
            print(path)
        return 0
    except (ASIFError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

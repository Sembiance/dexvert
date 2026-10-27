#!/usr/bin/env python3
# Vibe coded by Codex
"""Extract explicitly addressed PCM from Ensoniq ECLW/ECW wavesets.

Python 3.9+, standard library only. See ensoniqWaveSetFormat.txt for the
supported layout and unresolved synthesis semantics. This is a sample
extractor, not an emulation of the AudioPCI MIDI synthesizer.
"""

import argparse
import base64
from dataclasses import asdict, dataclass, field
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import sys
import wave


class FormatError(ValueError):
    """No safe extraction is possible; the caller must not create outputs."""


# Relative to the allocation directory, not hardcoded absolute file offsets.
TABLE_LAYOUT = (
    ("bank_maps", 4, 256), ("drum_kit_maps", 16, 256),
    ("program_maps", 28, 256), ("drum_note_maps", 40, 256),
    ("instruments", 52, 23), ("patches", 64, 76),
    ("set_slots", 80, 2), ("set_tags", 92, 2),
    ("set_samples", 104, 2), ("samples", 116, 16),
)
LIMITATIONS = [
    "Synthesis is not emulated: envelopes, LFOs, layering, tuning and dynamic "
    "wavetable selection are not rendered into the extracted PCM.",
    "Several control fields and the algorithm producing sample-set tags remain "
    "unresolved; parsing/preserving their bytes is not semantic understanding.",
    "ECW has no decoded per-sample sample-rate field. The WAV rate is an explicit "
    "export convention (22050 Hz by default), not a recovered recording rate.",
    "Sample WAVs contain the interval from start to end, with a fractional end "
    "rounded up to retain its containing PCM word. Loops are not repeated.",
    "The PCM-pool WAV preserves all words after the RDNS data boundary, including "
    "additional wavetable frames, shared data, interpolation words and unused tails.",
    "No verified payload checksum is available. In-range altered audio bytes "
    "cannot be distinguished from intentional PCM values by this converter.",
]


def ctext(raw):
    """A byte string with a NUL terminator; retain raw bytes separately."""
    return raw.split(b"\0", 1)[0].decode("latin-1").rstrip()


def safe_name(name):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("._")[:96] or "unnamed"


@dataclass
class Section:
    name: str
    offset: int
    length: int
    count: int
    stride: int


@dataclass
class Sample:
    index: int
    key_high: int
    control: int
    pitch_word: int
    start: int
    loop: int
    end: int
    raw_hex: str
    names: list = field(default_factory=list)


@dataclass
class Extraction:
    label: str
    kind: str
    start: int
    end: int
    sample_index: object = None
    partial: bool = False
    note: str = ""


class WaveSet:
    def __init__(self, data):
        self.data = data
        self.warnings = []
        self.sections = {}
        self.tables = {}
        self.samples = []
        self.sets = []
        self.skipped = []
        self.rdns = None
        self.pcm_start = None
        self.claims = []
        self._parse()

    def warn(self, message):
        self.warnings.append(message)

    def claim(self, start, end, label):
        start, end = max(0, start), min(len(self.data), end)
        if end > start:
            self.claims.append((start, end, label))

    def records(self, section):
        s = section
        if not s.length or not s.count:
            if s.length or s.count:
                self.warn(f"{s.name}: inconsistent zero length/count")
            return []
        if s.length != s.count * s.stride:
            self.warn(f"{s.name}: length {s.length} != count {s.count} * {s.stride}; "
                      "using only complete records within both limits")
        if s.offset < self.allocation + 140 or (
                s.offset < self.wave_offset + self.wave_length and
                s.offset + s.length > self.wave_offset):
            self.warn(f"{s.name}: overlaps a header or waveform area; table ignored")
            return []
        available = max(0, min(s.length, len(self.data) - s.offset))
        count = min(s.count, available // s.stride)
        if count < s.count:
            self.warn(f"{s.name}: only {count} of {s.count} records are available")
        return [self.data[s.offset + i * s.stride:s.offset + (i + 1) * s.stride]
                for i in range(count)]

    def _parse(self):
        b = self.data
        if b[:4] != b"ECLW":
            raise FormatError("not an Ensoniq ECLW waveset (signature mismatch)")
        if len(b) < 16:
            raise FormatError("truncated ECLW header; no allocation pointer is available")
        self.allocation, text_offset = struct.unpack_from("<II", b, 8)
        a = self.allocation
        if a < 16 or a + 140 > len(b):
            raise FormatError("ECLW allocation directory is missing or out of bounds")
        # These words have no established version semantics; do not invent them.
        self.markers = {str(o): b[o:o + 4].hex() for o in (4, a, a + 76, a + 128)}
        if any(bytes.fromhex(v) != b"\x01\0\x01\0" for v in self.markers.values()):
            self.warn("nonstandard opaque marker words; extracting independently described PCM")
        self.text_offset = text_offset
        self.text = {}
        if 16 <= text_offset <= a and text_offset + 496 <= a:
            for name, offset, size in (("copyright", 0, 80), ("name", 80, 80),
                                       ("filename", 160, 256), ("description", 416, 80),
                                       ("information", 496, a - text_offset - 496)):
                raw = b[text_offset + offset:text_offset + offset + size]
                self.text[name] = {"text": ctext(raw), "raw_hex": raw.hex()}
        else:
            self.warn("text area pointer is invalid; text decoding omitted")
        self.claim(0, a, "file header and text slots (opaque words retained)")
        self.claim(a, a + 140, "allocation directory")
        for name, rel, stride in TABLE_LAYOUT:
            offset, length, count = struct.unpack_from("<III", b, a + rel)
            self.sections[name] = Section(name, offset, length, count, stride)
            self.claim(offset, offset + length, name)
        self.wave_offset, self.wave_length = struct.unpack_from("<II", b, a + 132)
        if self.wave_offset < a + 140:
            raise FormatError("waveform area overlaps the file header or allocation directory")
        if self.wave_offset > len(b):
            raise FormatError("waveform area lies beyond EOF; no audio bytes survive")
        self.wave_available = min(self.wave_length, len(b) - self.wave_offset)
        self.wave_end = self.wave_offset + self.wave_available
        if self.wave_available < self.wave_length:
            self.warn(f"waveform area truncated: {self.wave_available} of "
                      f"{self.wave_length} bytes available; {self.wave_length - self.wave_available} missing")
        if self.wave_end < len(b):
            self.warn(f"{len(b) - self.wave_end} trailing bytes outside the declared waveform area")
        occupied = sorted((s.offset, s.offset + s.length, s.name)
                          for s in self.sections.values() if s.length)
        for prev, curr in zip(occupied, occupied[1:]):
            if curr[0] < prev[1]:
                self.warn(f"overlapping table declarations: {prev[2]} and {curr[2]}")
        for name, section in self.sections.items():
            records = self.records(section)
            if section.stride == 256:
                self.tables[name] = [list(struct.unpack("<128H", x)) for x in records]
            elif section.stride == 2:
                self.tables[name] = [struct.unpack("<H", x)[0] for x in records]
            elif name == "samples":
                self.samples = [self.decode_sample(i, x) for i, x in enumerate(records)]
            elif name == "instruments":
                self.tables[name] = [self.decode_instrument(x) for x in records]
            elif name == "patches":
                self.tables[name] = [self.decode_patch(x) for x in records]
        self._parse_rdns()
        self._validate_references()

    @staticmethod
    def decode_sample(index, raw):
        return Sample(index, *struct.unpack("<BBhIII", raw), raw.hex())

    @staticmethod
    def decode_instrument(raw):
        result = {"type": raw[0], "raw_hex": raw.hex()}
        if raw[0] == 2:
            result.update(mode=raw[1], split_key=raw[2], layers=[])
            for o in (3, 13):
                values = struct.unpack_from("<HbbbbHBB", raw, o)
                result["layers"].append(dict(zip(
                    ("patch", "amplitude", "pan", "coarse_tune", "fine_tune",
                     "delay", "unresolved_control", "exclusive_group"), values)))
        elif raw[0] == 255:
            result.update(unresolved_byte_01=raw[1], branches=[])
            active = True
            for o in range(2, 23, 3):
                target, limit = struct.unpack_from("<HB", raw, o)
                result["branches"].append({"instrument": target, "key_high": limit,
                                           "active": active})
                if limit == 127:
                    active = False
        else:
            result["unresolved_payload_hex"] = raw[1:].hex()
        return result

    @staticmethod
    def decode_patch(raw):
        # Keep every control byte, even where a precise meaning/scale is unknown.
        result = {"raw_hex": raw.hex(), "bytes": list(raw),
                  "pitch_envelope_depth": struct.unpack_from("b", raw)[0],
                  "modulation_sensitivity": raw[1], "scale_mode": raw[2],
                  "set_slot": struct.unpack_from("<H", raw, 11)[0],
                  "tuning_byte_0d": struct.unpack_from("b", raw, 13)[0],
                  "split_shift": struct.unpack_from("b", raw, 16)[0]}
        fields = ("release_target_unverified", "delay", "initial_level", "attack_time",
                  "attack_level", "decay_time", "decay_level", "sustain_time",
                  "sustain_level", "release_time", "velocity_amount",
                  "unresolved_11", "key_time_amount", "release_control", "unresolved_14")
        for name, offset in (("pitch_envelope", 27), ("wavetable_envelope", 42),
                             ("amplitude_envelope", 57)):
            result[name] = dict(zip(fields, raw[offset:offset + 15]))
        result["vibrato"] = dict(zip(("depth", "speed", "delay", "unresolved"), raw[72:76]))
        return result

    def _parse_rdns(self):
        w = self.wave_offset
        b = self.data
        if self.wave_available < 12 or b[w + 8:w + 12] != b"RDNS":
            self.warn("no RDNS directory: sample names and PCM-pool boundary unavailable; "
                      "only explicit sample ranges will be extracted")
            self.claim(w, self.wave_end, "waveform area without recognized RDNS directory")
            return
        if self.wave_available < 40:
            self.warn("truncated RDNS header")
            return
        magic_word, size, signature, name_len, set_len, sample_len, set_offset, \
            copy_offset, data_offset, set_count, sample_count = struct.unpack_from("<II4sBB6H", b, w)
        self.rdns = dict(opaque_word=magic_word, declared_size=size, signature=signature.decode(),
                         name_length=name_len, set_stride=set_len, sample_stride=sample_len,
                         sets_offset=set_offset, samples_offset=copy_offset, pcm_offset=data_offset,
                         set_count=set_count, sample_count=sample_count,
                         rom_name=ctext(b[w + 26:w + 40]), raw_header_hex=b[w:w + 40].hex())
        self.claim(w, w + 40, "RDNS header")
        if size != self.wave_length:
            self.warn("RDNS and outer waveform lengths disagree; outer allocation bounds are used")
        if (name_len, set_len, sample_len) != (14, 22, 16):
            self.warn("unsupported RDNS record sizes; only outer sample descriptors are used")
            return
        if not (40 <= set_offset <= copy_offset <= data_offset <= self.wave_length
                and set_offset + set_count * set_len <= copy_offset
                and copy_offset + sample_count * sample_len <= data_offset):
            self.warn("inconsistent RDNS directory boundaries; no pool extraction or name recovery")
            return
        self.pcm_start = w + data_offset
        self.claim(w + set_offset, w + copy_offset, "RDNS sample-set directory")
        self.claim(w + copy_offset, w + data_offset, "RDNS duplicate sample descriptors")
        self.claim(self.pcm_start, self.wave_end, "signed 16-bit little-endian PCM pool")
        available_sets = min(set_count, max(0, (self.wave_available - set_offset) // set_len))
        for i in range(available_sets):
            o = w + set_offset + i * set_len
            raw = b[o:o + set_len]
            pointer, slot, tag, name = struct.unpack("<IHH14s", raw)
            delta = pointer - copy_offset
            first = delta // 16 if delta >= 0 and delta % 16 == 0 else None
            self.sets.append(dict(index=i, sample_pointer=pointer, slot=slot, tag=tag,
                                  name=ctext(name), first_sample=first, raw_hex=raw.hex()))
        copy_count = min(sample_count, max(0, (self.wave_available - copy_offset) // 16))
        outer_count = self.sections["samples"].count
        if sample_count != outer_count:
            self.warn(f"RDNS sample count {sample_count} differs from outer count {outer_count}")
        # Recover missing *whole* outer descriptors from the independently bounded copy.
        for i in range(copy_count):
            raw = b[w + copy_offset + i * 16:w + copy_offset + (i + 1) * 16]
            if i < len(self.samples):
                if raw.hex() != self.samples[i].raw_hex:
                    self.warn(f"sample {i}: duplicate descriptor differs; outer descriptor takes precedence")
            elif i < outer_count:
                self.samples.append(self.decode_sample(i, raw))
                self.warn(f"sample {i}: recovered missing outer descriptor from RDNS copy")
        for entry in self.sets:
            first = entry["first_sample"]
            if first is None or first >= len(self.samples):
                self.warn(f"RDNS set {entry['index']}: sample pointer does not resolve")
                continue
            for sample in self.samples[first:]:
                if entry["name"] and entry["name"] not in sample.names:
                    sample.names.append(entry["name"])
                if sample.key_high == 127:
                    break

    def _validate_references(self):
        for name, target in (("bank_maps", "program_maps"), ("drum_kit_maps", "drum_note_maps"),
                             ("program_maps", "instruments"), ("drum_note_maps", "instruments")):
            count = len(self.tables[target])
            bad = sum(x != 65535 and x >= count for row in self.tables[name] for x in row)
            if bad:
                self.warn(f"{name}: {bad} references outside {target}")
        for i, item in enumerate(self.tables["instruments"]):
            if item["type"] == 2:
                mode = item["mode"]
                active = (0,) if mode == 0 else (1,) if mode == 3 else (0, 1) if mode in (1, 2) else ()
                for j in active:
                    if item["layers"][j]["patch"] >= len(self.tables["patches"]):
                        self.warn(f"instrument {i}, layer {j}: invalid patch reference")
            elif item["type"] == 255:
                for branch in item["branches"]:
                    if branch["active"] and branch["instrument"] >= len(self.tables["instruments"]):
                        self.warn(f"instrument {i}: invalid branch target")
            else:
                self.warn(f"instrument {i}: unresolved instrument type {item['type']}")
        slots, tags, indices = (self.tables[n] for n in ("set_slots", "set_tags", "set_samples"))
        for i, patch in enumerate(self.tables["patches"]):
            slot = patch["set_slot"]
            if slot >= len(slots) or slots[slot] == 65535 or slots[slot] >= len(indices):
                self.warn(f"patch {i}: sample-set slot cannot be resolved")
        for entry in self.sets:
            slot = entry["slot"]
            if slot >= len(slots) or slots[slot] == 65535:
                self.warn(f"RDNS set {entry['index']}: unresolved slot")
                continue
            # Array 1 addresses a tag-terminated list, not just one fixed pair.
            j = slots[slot]
            matched = False
            while j < min(len(tags), len(indices)) and tags[j] != 0:
                if tags[j] == entry["tag"] and indices[j] == entry["first_sample"]:
                    matched = True
                j += 1
            if not matched:
                self.warn(f"RDNS set {entry['index']}: no matching tag/sample pair in slot list")

    def plan(self):
        result = []
        self.skipped = []
        if self.pcm_start is not None and self.pcm_start < self.wave_end:
            end = self.wave_end - (self.wave_end - self.pcm_start) % 2
            if end > self.pcm_start:
                result.append(Extraction("PCM_pool", "pool", self.pcm_start, end,
                                         partial=self.wave_available < self.wave_length,
                                         note="Complete available PCM pool, including extra wavetable frames and guards"))
        for sample in self.samples:
            reason = None
            if sample.start % 16:
                reason = "fractional sample start is unsupported; PCM is preserved in the pool"
            elif sample.end <= sample.start:
                reason = "end address is not after start"
            start = self.wave_offset + (sample.start // 16) * 2
            end = self.wave_offset + ((sample.end + 15) // 16) * 2
            if self.pcm_start is not None and start < self.pcm_start:
                reason = "sample points into the RDNS metadata, not PCM"
            if start >= self.wave_end:
                reason = "sample starts beyond available waveform data (missing/truncated)"
            if reason:
                self.skipped.append({"sample_index": sample.index, "names": sample.names, "reason": reason})
                continue
            partial = end > self.wave_end
            end = min(end, self.wave_end)
            end -= (end - start) % 2
            if end <= start:
                self.skipped.append({"sample_index": sample.index, "names": sample.names,
                                     "reason": "no complete PCM words survive"})
                continue
            notes = []
            if partial:
                notes.append("Truncated: only surviving complete PCM words exported")
            if sample.control >= 128:
                notes.append("Moving wavetable: base interval only; additional frames retained in PCM pool")
            if sample.end % 16:
                notes.append("Fractional endpoint: containing PCM word retained")
            name = safe_name(sample.names[0]) if sample.names else "sample"
            result.append(Extraction(f"{sample.index:04d}_{name}", "sample", start, end,
                                     sample.index, partial, "; ".join(notes)))
        return result

    def byte_map(self):
        """Partition every existing byte without implying all semantics are known."""
        points = {0, len(self.data)}
        for a, z, _ in self.claims:
            points.update((a, z))
        points = sorted(points)
        result = []
        for a, z in zip(points, points[1:]):
            labels = [label for x, y, label in self.claims if x <= a and z <= y]
            result.append({"offset": a, "length": z - a,
                           "regions": labels or ["unallocated bytes; purpose unresolved"],
                           "all_zero": not any(self.data[a:z]),
                           "sha256": hashlib.sha256(self.data[a:z]).hexdigest()})
        return result

    def metadata(self):
        return dict(format="Ensoniq ECLW", semantic_reverse_engineering_complete=False,
                    limitations=LIMITATIONS, source_size=len(self.data),
                    source_sha256=hashlib.sha256(self.data).hexdigest(), text=self.text,
                    allocation_offset=self.allocation, text_offset=self.text_offset,
                    opaque_markers=self.markers,
                    sections={k: asdict(v) for k, v in self.sections.items()},
                    waveform_offset=self.wave_offset, waveform_declared_length=self.wave_length,
                    waveform_available_length=self.wave_available, rdns=self.rdns,
                    tables=self.tables, sample_sets=self.sets,
                    samples=[asdict(s) for s in self.samples], byte_map=self.byte_map(),
                    warnings=self.warnings, skipped_samples=self.skipped)


def ensure_directory(path):
    missing = []
    p = path
    while not p.exists():
        missing.append(p)
        p = p.parent
    path.mkdir(parents=True, exist_ok=True)
    for p in missing:
        p.chmod(p.stat().st_mode | 0o550)


def new_output(directory, stem, suffix):
    """Exclusive creation avoids replacing existing files or following symlinks."""
    n = 1
    while True:
        name = stem + (f"__{n}" if n > 1 else "") + suffix
        path = directory / name
        try:
            f = path.open("xb")
            os.fchmod(f.fileno(), 0o664)
            return path, f
        except FileExistsError:
            n += 1


def convert(input_file, output_dir, verbose=False, sample_rate=22050):
    input_file, output_dir = Path(input_file), Path(output_dir)
    if not 1 <= sample_rate <= 2147483647:
        raise FormatError("sample rate must be in 1..2147483647 Hz")
    # Identification and all parsing happen before even making the destination.
    with input_file.open("rb") as f:
        if f.read(4) != b"ECLW":
            raise FormatError("not an Ensoniq ECLW waveset (signature mismatch)")
        f.seek(0)
        data = f.read()
    bank = WaveSet(data)
    plan = bank.plan()
    if not plan:
        raise FormatError("recognized ECLW, but no safely located complete PCM words can be extracted")
    ensure_directory(output_dir)
    prefix = safe_name(input_file.name)
    outputs = []
    for item in plan:
        path, file = new_output(output_dir, prefix + "_" + item.label, ".wav")
        try:
            with file:
                with wave.open(file, "wb") as wav:
                    wav.setparams((1, 2, sample_rate, 0, "NONE", "not compressed"))
                    wav.writeframes(memoryview(data)[item.start:item.end])
        except BaseException:
            path.unlink(missing_ok=True)
            raise
        outputs.append(dict(**asdict(item), filename=path.name, frames=(item.end - item.start) // 2,
                            sample_rate=sample_rate,
                            pcm_sha256=hashlib.sha256(data[item.start:item.end]).hexdigest()))
    result = bank.metadata()
    result.update(input_file=str(input_file), outputs=outputs, sample_rate=sample_rate)
    if verbose:
        # A lossless source reconstruction recipe: the WAV's data chunk supplies
        # PCM; base64 supplies all other bytes. No sidecar is written otherwise.
        pool = next((x for x in outputs if x["kind"] == "pool"), None)
        ranges = []
        if pool:
            for a, z in ((0, pool["start"]), (pool["end"], len(data))):
                if z > a:
                    ranges.append(dict(offset=a, length=z - a,
                                       base64=base64.b64encode(data[a:z]).decode("ascii")))
            ranges.append(dict(offset=pool["start"], length=pool["end"] - pool["start"],
                               wav_file=pool["filename"], wav_pcm_byte_offset=0))
        else:
            ranges.append(dict(offset=0, length=len(data), base64=base64.b64encode(data).decode("ascii")))
        result["source_reconstruction"] = sorted(ranges, key=lambda r: r["offset"])
        path, file = new_output(output_dir, prefix + "_metadata", ".json")
        with file:
            file.write((json.dumps(result, indent=2, ensure_ascii=True) + "\n").encode("utf-8"))
        result["metadata_file"] = path.name
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputDir", type=Path)
    parser.add_argument("-verbose", "--verbose", action="store_true",
                        help="also write a JSON parse, byte map and source reconstruction recipe")
    parser.add_argument("--sample-rate", type=int, default=22050,
                        help="explicit WAV playback rate, default 22050; ECW recording rates are unresolved")
    args = parser.parse_args(argv)
    try:
        result = convert(args.inputFile, args.outputDir, args.verbose, args.sample_rate)
    except (OSError, FormatError, struct.error, wave.Error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    for warning in result["warnings"]:
        print(f"warning: {warning}", file=sys.stderr)
    print(f"Wrote {len(result['outputs'])} WAV files to {args.outputDir}; "
          f"{len(result['skipped_samples'])} sample descriptors skipped. "
          f"Raw PCM at {args.sample_rate} Hz; synthesis is not emulated.", file=sys.stderr)
    for item in result["skipped_samples"]:
        print(f"warning: sample {item['sample_index']}: {item['reason']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

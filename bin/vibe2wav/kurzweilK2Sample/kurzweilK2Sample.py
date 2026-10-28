#!/usr/bin/env python3
# Vibe coded by Codex
"""Extract explicitly addressed PCM from Kurzweil PRAM sample banks.

Python 3.10+, standard library only. See kurzweilK2Sample.txt for the format,
recovery policy, and the precise limits of this reverse engineering.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from typing import Any


TYPE_NAMES = {
    0x64: "table", 0x67: "intonation", 0x68: "velocity", 0x69: "pressure",
    0x6F: "quick_access", 0x70: "song", 0x71: "effect", 0x90: "program",
    0x94: "keymap", 0x98: "sample", 0x9C: "K2000_setup", 0xA4: "K2500_setup",
    0xB0: "KDFX_studio", 0xB4: "KDFX_preset", 0xBC: "KDFX_algorithm",
}
NS_PER_SECOND = 1_000_000_000


class NotKurzweil(ValueError):
    """Input has not been identified as a supported PRAM container."""


class BadStructure(ValueError):
    """An identified bank has a damaged or unsupported structure."""


def u16(data: bytes, offset: int) -> int:
    return struct.unpack_from(">H", data, offset)[0]


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from(">I", data, offset)[0]


def i32(data: bytes, offset: int) -> int:
    return struct.unpack_from(">i", data, offset)[0]


def object_type(value: int) -> tuple[int, int]:
    if value & 0x8000:
        return (value >> 8) & 0xFC, value & 0x3FF
    return value >> 8, value & 0xFF


def text_name(raw: bytes) -> str:
    # Latin-1 provides a reversible display mapping; the raw bytes are retained.
    return raw.split(b"\0", 1)[0].decode("latin-1").rstrip(" ")


def safe_name(name: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")[:80]
    return value or "unnamed"


def merge_ranges(ranges: list[tuple[int, int]], size: int) -> list[tuple[int, int]]:
    merged: list[tuple[int, int]] = []
    for a, b in sorted((max(0, a), min(size, b)) for a, b in ranges):
        if b <= a:
            continue
        if merged and a <= merged[-1][1]:
            merged[-1] = merged[-1][0], max(b, merged[-1][1])
        else:
            merged.append((a, b))
    return merged


def complement(ranges: list[tuple[int, int]], size: int) -> list[tuple[int, int]]:
    result = []
    pos = 0
    for a, b in merge_ranges(ranges, size):
        if pos < a:
            result.append((pos, a))
        pos = b
    if pos < size:
        result.append((pos, size))
    return result


@dataclass
class FileHeader:
    object_end: int
    memory_or_remaining: int
    memory_or_part: int
    os_version: int
    machine_configuration: int
    reserved: str

    @classmethod
    def read(cls, data: bytes) -> FileHeader:
        if len(data) < 32 or data[:4] != b"PRAM":
            raise NotKurzweil("not a PRAM bank with a complete 32-byte header")
        values = struct.unpack_from(">5I", data, 4)
        if values[0] < 36 or values[0] & 1:
            raise NotKurzweil("invalid PRAM object-section boundary")
        return cls(*values, data[24:32].hex())


@dataclass
class Sound:
    root_key: int
    flags: int
    volume_half_db: int
    alternate_volume_half_db: int
    highest_pitch_cents: int
    name_offset: int
    start: int
    alternate_start: int
    loop_start: int
    end: int
    envelope_offset: int
    alternate_envelope_offset: int
    period_ns: int
    index: int = 0
    sub_id: int = 1
    header_offset: int = 0
    name: str = ""
    envelopes: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class BankObject:
    offset: int
    length: int
    body_offset: int
    kind: int
    object_id: int
    name: str
    raw: bytes = field(repr=False)
    details: dict[str, Any] = field(default_factory=dict)
    sounds: list[Sound] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class Clip:
    name: str
    filename: str
    object_id: int
    sub_ids: list[int]
    rate: int
    channels: int
    frames: int
    period_ns: int
    root_key: int
    pcm: bytes = field(repr=False)
    source_spans: list[tuple[int, int]] = field(default_factory=list)
    cues: list[tuple[str, int]] = field(default_factory=list)
    loop: tuple[int, int, int] | None = None
    warnings: list[str] = field(default_factory=list)
    partial: bool = False
    source_object: bytes = field(default=b"", repr=False)

    def summary(self) -> dict[str, Any]:
        return {key: value for key, value in self.__dict__.items()
                if key not in ("pcm", "source_object")}


@dataclass
class BankResult:
    input_file: Path
    primary_file: Path
    header: FileHeader
    objects: list[BankObject] = field(default_factory=list)
    clips: list[Clip] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    skipped: list[dict[str, Any]] = field(default_factory=list)
    sources: list[dict[str, Any]] = field(default_factory=list)
    regions: list[dict[str, Any]] = field(default_factory=list)
    unreferenced_pcm: list[tuple[int, int]] = field(default_factory=list)
    pool: bytes = field(default=b"", repr=False)
    metadata_complete: bool = False

    @property
    def status(self) -> str:
        if not self.clips:
            return "no_audio"
        if any(c.partial or c.warnings for c in self.clips) or self.skipped or self.warnings:
            return "recovered_with_notes"
        return "converted"


def plausible_object(data: bytes, pos: int, limit: int) -> bool:
    if pos + 8 > min(len(data), limit):
        return False
    kind, _ = object_type(u16(data, pos))
    length, relative = u16(data, pos + 2), u16(data, pos + 4)
    return kind in TYPE_NAMES and length >= 8 and 4 <= relative <= length - 4


def is_continuation(data: bytes, header: FileHeader) -> bool:
    # A large legacy heap counter is not a split sequence number. A first
    # object block distinguishes a normal bank even if its suffix is .KR2.
    if header.memory_or_part < 2 or len(data) < 36:
        return False
    block = -i32(data, 32)
    if block >= 12 and plausible_object(data, 36, header.object_end):
        return False
    return header.object_end == 36


def family_stem(path: Path) -> str:
    match = re.fullmatch(r"(.*)\.kr[1-9][0-9]*(?:\.krz)?", path.name, re.I)
    return match[1] if match else path.stem


def sibling_candidates(path: Path, number: int) -> list[Path]:
    stem = family_stem(path).casefold()
    names = {f"{stem}.kr{number}", f"{stem}.kr{number}.krz"}
    if number == 1:
        names.add(f"{stem}.krz")
    return sorted((p for p in path.parent.iterdir()
                   if p.is_file() and p.name.casefold() in names), key=str)


def matching_part(path: Path, number: int, first: FileHeader,
                  warnings: list[str]) -> tuple[Path, bytes, FileHeader] | None:
    matches = []
    for candidate in sibling_candidates(path, number):
        try:
            data = candidate.read_bytes()
            header = FileHeader.read(data)
        except (OSError, NotKurzweil):
            continue
        if (header.memory_or_part == number
                and header.os_version == first.os_version
                and header.machine_configuration == first.machine_configuration
                and (number == 1 or header.object_end in (36, first.object_end))):
            if number > 1 and len(data) < 36:
                continue
            matches.append((candidate, data, header))
    if len(matches) > 1:
        warnings.append(f"ambiguous part {number}: " + ", ".join(p.name for p, _, _ in matches))
        return None
    return matches[0] if matches else None


def parse_sample(obj: BankObject) -> None:
    body = obj.body_offset - obj.offset
    data = obj.raw
    if body + 12 > len(data):
        raise BadStructure("truncated 12-byte sound block")
    base, last_index, relative, flags, reserved_byte, copy_id, reserved_word = (
        struct.unpack_from(">HHHBBHH", data, body))
    first = body + 4 + relative
    count = last_index + 1
    obj.details.update(base_id=base, header_count=count, headers_offset=relative,
                       flags=flags, reserved_byte=reserved_byte, copy_id=copy_id,
                       reserved_word=reserved_word)
    if first < body + 12 or first > len(data):
        raise BadStructure("sound-header offset is outside the sample body")
    available = min(count, (len(data) - first) // 32)
    if available < count:
        obj.warnings.append(f"only {available} of {count} sound headers are present")
    covered = [(body, body + 12), (first, first + 32 * available)]
    for index in range(available):
        pos = first + 32 * index
        h = Sound(*struct.unpack_from(">BBbbHH4IHHI", data, pos), index=index,
                  sub_id=base + index, header_offset=obj.offset + pos)
        if h.name_offset:
            target = pos + 6 + h.name_offset
            end = data.find(b"\0", target) if target < len(data) else -1
            if body <= target < len(data) and end >= 0:
                h.name = text_name(data[target:end])
                covered.append((target, end + 1))
            else:
                obj.warnings.append(f"subsample {h.sub_id}: name pointer is outside the object")
        for field_offset, distance in ((24, h.envelope_offset),
                                       (26, h.alternate_envelope_offset)):
            target = pos + field_offset + distance
            env: dict[str, Any] = {"offset": obj.offset + target, "stages": []}
            cursor = target
            zero_times = 0
            if distance == 0 or target < first + 32 * available:
                env["error"] = "absent or invalid envelope pointer"
            else:
                while cursor + 4 <= len(data):
                    rate, time = struct.unpack_from(">hH", data, cursor)
                    env["stages"].append({"rate": rate, "time": time})
                    cursor += 4
                    if time == 0:
                        zero_times += 1
                        if zero_times == 2:
                            break
                if zero_times < 2:
                    env["error"] = "envelope has no complete sustain/release termination"
                covered.append((target, cursor))
            if "error" in env:
                obj.warnings.append(f"subsample {h.sub_id}: {env['error']}")
            h.envelopes.append(env)
        obj.sounds.append(h)
    gaps = complement([(a - body, b - body) for a, b in covered], len(data) - body)
    obj.details["uninterpreted_body_ranges"] = [
        {"offset": obj.body_offset + a, "length": b - a,
         "hex": data[body + a:body + b].hex()} for a, b in gaps]


def parse_keymap(obj: BankObject) -> None:
    """Decode all explicitly described key tables without inferring zones."""
    body = obj.body_offset - obj.offset
    data = obj.raw
    if body + 28 > len(data):
        raise BadStructure("truncated 28-byte keymap header")
    sample_id, method, base_pitch, cents, last, stride = struct.unpack_from(">HHhhHH", data, body)
    pointers = struct.unpack_from(">8H", data, body + 12)
    obj.details.update(sample_id=sample_id, method=method, base_pitch=base_pitch,
                       cents_per_entry=cents, entry_count=last + 1,
                       entry_size=stride, table_offsets=list(pointers))
    if method & ~0x1F or method & 0x18 == 0x18:
        obj.warnings.append("unsupported keymap method bits; body retained verbatim")
        return
    widths = [(0x10, 2), (0x08, 1), (0x04, 1), (0x02, 2), (0x01, 1)]
    if stride != sum(size for flag, size in widths if method & flag) or stride == 0:
        obj.warnings.append("keymap entry-size/method disagreement; body retained verbatim")
        return
    tables = {}
    covered = [(body, body + 28)]
    for level, relative in enumerate(pointers):
        start = body + 12 + 2 * level + relative
        if start in tables:
            tables[start]["velocity_levels"].append(level)
            continue
        if start < body + 28 or start > len(data):
            obj.warnings.append(f"velocity level {level}: invalid key-table pointer")
            continue
        count = min(last + 1, (len(data) - start) // stride)
        if count < last + 1:
            obj.warnings.append(f"velocity level {level}: truncated key table")
        entries = []
        for n in range(count):
            pos = start + n * stride
            entry: dict[str, int] = {"sample_id": sample_id}
            for mask, size in widths:
                if not method & mask:
                    continue
                key = {16: "tuning_cents", 8: "tuning_coarse", 4: "volume_half_db",
                       2: "sample_id", 1: "subsample_id"}[mask]
                entry[key] = int.from_bytes(data[pos:pos + size], "big", signed=mask in (16, 8, 4))
                pos += size
            entries.append(entry)
        tables[start] = {"offset": obj.offset + start, "velocity_levels": [level],
                         "entries": entries}
        covered.append((start, start + count * stride))
    obj.details["tables"] = list(tables.values())
    obj.details["uninterpreted_body_ranges"] = [
        {"offset": obj.body_offset + a, "length": b - a,
         "hex": data[body + a:body + b].hex()}
        for a, b in complement([(a - body, b - body) for a, b in covered], len(data) - body)]


def parse_objects(data: bytes, result: BankResult) -> None:
    limit = min(result.header.object_end, len(data))
    if len(data) < 36:
        raise NotKurzweil("no PRAM block header")
    block = -i32(data, 32)
    if not (block == 0 or (block >= 12 and plausible_object(data, 36, limit))):
        raise NotKurzweil("PRAM signature without a recognizable object-block structure")
    pos = 32
    terminated = False
    while pos + 4 <= limit:
        length = -i32(data, pos)
        if length == 0:
            result.regions.append({"start": pos, "end": pos + 4, "kind": "object_terminator"})
            pos += 4
            terminated = True
            break
        if length < 12 or length & 1:
            result.warnings.append(f"invalid block length at 0x{pos:x}; remaining objects not guessed")
            break
        declared_end = pos + length
        end = min(declared_end, limit)
        result.regions.append({"start": pos, "end": pos + 4, "kind": "negative_block_length"})
        cursor = pos + 4
        while cursor + 6 <= end:
            packed, size, offset = struct.unpack_from(">HHH", data, cursor)
            kind, number = object_type(packed)
            if size < 8 or offset < 4 or offset + 4 > size:
                result.warnings.append(f"invalid object header at 0x{cursor:x}; rest of this block not guessed")
                break
            obj_end = cursor + size
            if obj_end > end:
                result.warnings.append(f"truncated object {number} at 0x{cursor:x}")
                break
            body = cursor + 4 + offset
            obj = BankObject(cursor, size, body, kind, number,
                             text_name(data[cursor + 6:min(body, cursor + 22)]), data[cursor:obj_end])
            result.objects.append(obj)
            result.regions.append({"start": cursor, "end": body, "kind": "object_header_and_name"})
            result.regions.append({"start": body, "end": obj_end,
                                   "kind": TYPE_NAMES.get(kind, "unknown_object") + "_body"})
            try:
                if kind == 0x98:
                    parse_sample(obj)
                elif kind == 0x94:
                    parse_keymap(obj)
                else:
                    obj.details["semantic_status"] = "opaque synthesis/control body; not rendered"
            except (BadStructure, struct.error) as exc:
                obj.warnings.append(str(exc))
            cursor = obj_end
            if cursor & 1 and cursor < end:
                result.regions.append({"start": cursor, "end": cursor + 1, "kind": "object_alignment"})
                cursor += 1
        if cursor < end:
            result.regions.append({"start": cursor, "end": end,
                                   "kind": "block_padding" if end - cursor <= 3 else "unparsed_block_tail"})
        pos = end
        if declared_end > limit:
            result.warnings.append("object block is truncated by end of file/object section")
            break
    if not terminated:
        result.warnings.append("missing object-section terminator")
    if pos < limit:
        result.regions.append({"start": pos, "end": limit, "kind": "unparsed_object_section"})
    if result.header.object_end > len(data):
        result.warnings.append("file ends before the declared PCM section")


def swap16(data: bytes) -> bytes:
    out = bytearray(len(data))
    out[0::2], out[1::2] = data[1::2], data[0::2]
    return bytes(out)


def interleave(channels: list[bytes]) -> bytes:
    if len(channels) == 1:
        return channels[0]
    size = len(channels[0])
    if any(len(c) != size for c in channels):
        raise ValueError("cannot interleave unequal channel lengths")
    out = bytearray(size * len(channels))
    step = 2 * len(channels)
    for index, pcm in enumerate(channels):
        out[index * 2::step] = pcm[0::2]
        out[index * 2 + 1::step] = pcm[1::2]
    return bytes(out)


def sound_audio(sound: Sound, pool: bytes) -> tuple[bytes, int, bool, list[str]]:
    if not sound.flags & 0x40:
        raise BadStructure("ROM or external sample reference; no embedded PCM")
    if sound.period_ns in (0, 0xFFFFFFFF):
        raise BadStructure(f"sample period 0x{sound.period_ns:08x} is unspecified/invalid; no exact playback rate available")
    if sound.root_key > 127:
        raise BadStructure("invalid MIDI root key")
    if sound.start > sound.end:
        raise BadStructure("sample start follows sample end")
    if sound.flags & 3 == 3:
        raise BadStructure("undefined playback-direction value 3")
    # Preserve all addressed data, including an alternate or loop start before
    # the normal start. Do not infer storage extents from neighbouring objects.
    anchors = [sound.start]
    warnings = []
    for label, address in (("alternate start", sound.alternate_start), ("loop start", sound.loop_start)):
        if address <= sound.end:
            anchors.append(address)
        else:
            warnings.append(f"{label} follows sample end; marker omitted")
    start = min(anchors)
    stop = min(sound.end + 1, len(pool) // 2)
    if start >= stop:
        raise BadStructure("sample PCM is absent (missing part or truncated bank)")
    partial = stop < sound.end + 1
    if partial:
        warnings.append(f"truncated PCM: {sound.end + 1 - stop} declared words unavailable")
    return swap16(pool[start * 2:stop * 2]), start, partial, warnings


def make_clip(obj: BankObject, sounds: list[Sound], result: BankResult,
              suffix: str = "") -> Clip:
    audio = [sound_audio(h, result.pool) for h in sounds]
    if len(sounds) == 2:
        if sounds[0].period_ns != sounds[1].period_ns:
            raise BadStructure("stereo channel sample periods disagree")
        if len(audio[0][0]) != len(audio[1][0]):
            raise BadStructure("stereo channel lengths differ; exported as separate channels")
    sound = sounds[0]
    pcm = interleave([a[0] for a in audio])
    frames = len(pcm) // (2 * len(sounds))
    rate = (NS_PER_SECOND + sound.period_ns // 2) // sound.period_ns
    if not 1 <= rate <= 0xFFFFFFFF // (2 * len(sounds)):
        raise BadStructure("sample period cannot be represented by a PCM WAV rate")
    base = audio[0][1]
    warnings = list(dict.fromkeys(w for a in audio for w in a[3]))
    name = sound.name or obj.name or f"sample_{obj.object_id}"
    loop = None
    if not sound.flags & 0x80:
        a, b = sound.loop_start - base, sound.end - base
        if 0 <= a <= b < frames:
            mode = {0: 0, 1: 2, 2: 1}[sound.flags & 3]
            loop = (a, b, mode)
        else:
            warnings.append("loop exceeds recovered PCM; loop metadata omitted")
    cues = [(label, address - base) for label, address in (
        ("Normal start", sound.start), ("Alternate start", sound.alternate_start))
        if 0 <= address - base < frames]
    if len(sounds) == 2:
        other = sounds[1]
        if (other.flags & 0x83, other.loop_start - audio[1][1], other.end - audio[1][1]) != (
                sound.flags & 0x83, sound.loop_start - base, sound.end - base):
            loop = None
            warnings.append("stereo loop definitions differ; common WAV loop omitted")
        if other.root_key != sound.root_key:
            warnings.append("channel root keys differ; WAV smpl uses the left key; both originals retained in krz chunk")
    ident = f"{obj.object_id:03d}_{sound.sub_id:03d}"
    filename = f"{safe_name(result.primary_file.stem)}__{ident}_{safe_name(name)}{suffix}.wav"
    return Clip(name, filename, obj.object_id, [h.sub_id for h in sounds], rate,
                len(sounds), frames, sound.period_ns, sound.root_key, pcm,
                [(a[1], a[1] + len(a[0]) // 2) for a in audio], cues, loop,
                warnings, any(a[2] for a in audio), obj.raw)


def extract_clips(result: BankResult) -> None:
    used_names: set[str] = set()
    spans = []

    def add(obj: BankObject, sounds: list[Sound], suffix: str = "") -> bool:
        try:
            clip = make_clip(obj, sounds, result, suffix)
        except BadStructure as exc:
            result.skipped.append({"object_id": obj.object_id, "name": obj.name,
                                   "sub_ids": [h.sub_id for h in sounds], "reason": str(exc)})
            return False
        candidate = clip.filename
        n = 2
        while candidate.casefold() in used_names:
            candidate = f"{Path(clip.filename).stem}__{n}.wav"
            n += 1
        clip.filename = candidate
        used_names.add(candidate.casefold())
        result.clips.append(clip)
        spans.extend((a * 2, b * 2) for a, b in clip.source_spans)
        return True

    for obj in result.objects:
        if obj.kind != 0x98:
            continue
        if not obj.sounds:
            result.skipped.append({"object_id": obj.object_id, "name": obj.name,
                                   "reason": "sample object has no readable sound headers"})
            continue
        if obj.details.get("flags", 0) & 1:
            # The stereo flag is explicit. More than two headers has no
            # established channel ordering here: preserve independent channels.
            if len(obj.sounds) == 2:
                before = len(result.skipped)
                if add(obj, obj.sounds):
                    continue
                reason = result.skipped.pop()["reason"]
                result.warnings.append(f"sample {obj.object_id}: {reason}")
                assert len(result.skipped) == before
            else:
                result.warnings.append(f"sample {obj.object_id}: unsupported stereo multi-root ordering; separate channels")
            for h in obj.sounds:
                add(obj, [h], f"_channel{h.index + 1}")
        else:
            for h in obj.sounds:
                add(obj, [h])
    result.unreferenced_pcm = complement(spans, len(result.pool))


def read_bank(input_file: str | Path) -> BankResult:
    path = Path(input_file)
    data = path.read_bytes()
    header = FileHeader.read(data)
    requested_path = path
    preliminary: list[str] = []
    continuation = is_continuation(data, header)
    # Some older continuations copy the first part's object offset instead of
    # writing 36. Accept this only after a matching part 1 has been identified.
    block_valid = len(data) >= 44 and -i32(data, 32) >= 12 and plausible_object(data, 36, len(data))
    if header.memory_or_part >= 2 and not block_valid:
        match = matching_part(path, 1, header, preliminary)
        if match:
            first_path, first_data, first_header = match
            if header.object_end in (36, first_header.object_end):
                path, data, header = first_path, first_data, first_header
                preliminary.append(f"input is a continuation; recovered bank using {path.name}")
                continuation = False
        elif continuation:
            result = BankResult(requested_path, path, header)
            result.warnings = preliminary + ["continuation has no matching part 1; sample boundaries and rates are unavailable"]
            result.sources.append({"path": str(path), "size": len(data),
                                   "sha256": hashlib.sha256(data).hexdigest(),
                                   "header": asdict(header), "pcm_file_offset": 36,
                                   "pcm_pool_offset": None,
                                   "prefix_hex": data[:36].hex()})
            result.pool = data[36:]
            result.unreferenced_pcm = [(0, len(result.pool))] if result.pool else []
            result.regions = [{"start": 0, "end": 32, "kind": "file_header"},
                              {"start": 32, "end": 36, "kind": "continuation_control"},
                              {"start": 36, "end": len(data), "kind": "unlocated_continuation_pcm"}]
            return result
    result = BankResult(requested_path, path, header, warnings=preliminary)
    result.regions.append({"start": 0, "end": 32, "kind": "file_header"})
    parse_objects(data, result)
    offset = min(header.object_end, len(data))
    result.pool = data[offset:]
    result.sources.append({"path": str(path), "size": len(data),
                           "sha256": hashlib.sha256(data).hexdigest(),
                           "header": asdict(header), "pcm_file_offset": offset,
                           "pcm_pool_offset": 0, "prefix_hex": data[:offset].hex()})
    if offset < len(data):
        result.regions.append({"start": offset, "end": len(data), "kind": "pcm_pool"})
    if header.memory_or_part == 1:
        expected = header.memory_or_remaining
        number = 2
        remaining = max(0, expected - len(result.pool))
        while remaining:
            part = matching_part(path, number, header, result.warnings)
            if part is None:
                result.warnings.append(f"missing split part {number}; {remaining} declared PCM bytes unavailable")
                break
            part_path, part_data, part_header = part
            # No sample data or metadata is discovered by scanning magic bytes.
            payload = part_data[36:]
            source = {"path": str(part_path), "size": len(part_data),
                                   "sha256": hashlib.sha256(part_data).hexdigest(),
                                   "header": asdict(part_header), "pcm_file_offset": 36,
                                   "pcm_pool_offset": len(result.pool),
                                   "prefix_hex": part_data[:36].hex()}
            predicted_remaining = expected - len(result.pool) - len(payload)
            if part_header.memory_or_remaining != predicted_remaining:
                source["pcm_pool_offset"] = None
                source["unlocated_pcm_base64"] = base64.b64encode(payload).decode("ascii")
                result.sources.append(source)
                result.warnings.append(f"part {number}: split lengths disagree by "
                                       f"{abs(part_header.memory_or_remaining - predicted_remaining)} bytes; "
                                       "continuation position is ambiguous, so only the validated prefix is decoded")
                break
            result.sources.append(source)
            result.pool += payload
            remaining = predicted_remaining
            if not part_header.memory_or_remaining:
                break
            if not payload:
                result.warnings.append("empty continuation; further assembly stopped")
                break
            number += 1
        if len(result.pool) != expected:
            result.warnings.append(f"split PCM total is {len(result.pool)} bytes; first header declares {expected}")
    if len(result.pool) & 1:
        result.warnings.append("odd PCM byte count: final incomplete 16-bit word is not decoded")
    extract_clips(result)
    return result


def riff_chunk(tag: bytes, payload: bytes) -> bytes:
    return tag + struct.pack("<I", len(payload)) + payload + (b"\0" if len(payload) & 1 else b"")


def wav_bytes(clip: Clip) -> bytes:
    fmt = struct.pack("<HHIIHH", 1, clip.channels, clip.rate,
                      clip.rate * clip.channels * 2, clip.channels * 2, 16)
    loops = []
    if clip.loop:
        start, end, mode = clip.loop
        loops = [struct.pack("<6I", 0, mode, start, end, 0, 0)]
    smpl = struct.pack("<9I", 0, 0, clip.period_ns, clip.root_key, 0, 0, 0, len(loops), 0)
    chunks = [riff_chunk(b"fmt ", fmt), riff_chunk(b"smpl", smpl + b"".join(loops))]
    if clip.cues:
        points = []
        labels = []
        for index, (name, frame) in enumerate(clip.cues, 1):
            points.append(struct.pack("<II4sIII", index, frame, b"data", 0, 0, frame))
            labels.append(riff_chunk(b"labl", struct.pack("<I", index) + name.encode("ascii") + b"\0"))
        chunks.append(riff_chunk(b"cue ", struct.pack("<I", len(points)) + b"".join(points)))
        chunks.append(riff_chunk(b"LIST", b"adtl" + b"".join(labels)))
    if clip.source_object:
        # A private RIFF chunk retains the exact sample object, including fields
        # that standard WAV sampler metadata cannot express. Players skip it.
        chunks.append(riff_chunk(b"krz ", clip.source_object))
    chunks.append(riff_chunk(b"data", clip.pcm))
    payload = b"WAVE" + b"".join(chunks)
    if len(payload) > 0xFFFFFFFF:
        raise BadStructure("audio exceeds the RIFF/WAV 32-bit size limit")
    return b"RIFF" + struct.pack("<I", len(payload)) + payload


def verbose_metadata(result: BankResult) -> dict[str, Any]:
    objects = []
    for obj in result.objects:
        record = asdict(obj)
        record["raw_hex"] = record.pop("raw").hex()
        objects.append(record)
    leftovers = [{"pool_byte_start": a, "pool_byte_end": b,
                  "meaning": "PCM outside successfully exported declared spans; allocation unknown",
                  "base64": base64.b64encode(result.pool[a:b]).decode("ascii")}
                 for a, b in result.unreferenced_pcm]
    return {"input": str(result.input_file), "primary": str(result.primary_file),
            "status": result.status, "semantic_reverse_engineering_complete": False,
            "limitations": ["synthesis/control bodies are opaque and not rendered",
                            "legacy header allocator fields and continuation control word unresolved",
                            "unreferenced PCM allocation is not guessed",
                            "natural-envelope time units are not established",
                            "WAV rate is rounded from period; original period is in smpl"],
            "header": asdict(result.header), "sources": result.sources,
            "primary_byte_regions": result.regions, "objects": objects,
            "outputs": [c.summary() for c in result.clips], "warnings": result.warnings,
            "skipped": result.skipped, "unexported_pcm": leftovers}


def atomic_write(path: Path, payload: bytes) -> None:
    """Write a complete, user/group-readable file; leave no temporary files."""
    descriptor, temporary = tempfile.mkstemp(prefix=".kurzweil-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fchmod(stream.fileno(), 0o664)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def write_bank(result: BankResult, output_dir: str | Path, verbose: bool = False) -> list[Path]:
    # Fully validate and construct outputs before touching the output directory.
    outputs = [(c.filename, wav_bytes(c)) for c in result.clips]
    if verbose:
        outputs.append((safe_name(result.primary_file.stem) + ".metadata.json",
                        (json.dumps(verbose_metadata(result), indent=2, ensure_ascii=True) + "\n").encode()))
    if not outputs:
        return []
    directory = Path(output_dir)
    new_parents = []
    parent = directory
    while not parent.exists():
        new_parents.append(parent)
        parent = parent.parent
    directory.mkdir(parents=True, exist_ok=True)
    for parent in new_parents:
        parent.chmod(parent.stat().st_mode | 0o750)
    directory.chmod(directory.stat().st_mode | 0o750)
    written = []
    for name, payload in outputs:
        target = directory / name
        if target.resolve() in {Path(s["path"]).resolve() for s in result.sources}:
            raise OSError("output would overwrite a source file")
        atomic_write(target, payload)
        written.append(target)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputDir", type=Path)
    parser.add_argument("-verbose", "--verbose", action="store_true",
                        help="also write JSON with raw metadata, diagnostics, and unexported bytes")
    args = parser.parse_args(argv)
    try:
        result = read_bank(args.inputFile)
        written = write_bank(result, args.outputDir, args.verbose)
    except (NotKurzweil, BadStructure, OSError) as exc:
        print(f"kurzweilK2Sample: {exc}", file=sys.stderr)
        return 1
    for warning in result.warnings:
        print(f"warning: {warning}", file=sys.stderr)
    non_rom = [s for s in result.skipped if not s["reason"].startswith("ROM or external")]
    for item in non_rom:
        print(f"skipped sample {item['object_id']} {item['name']!r}: {item['reason']}", file=sys.stderr)
    if result.clips:
        print(f"Wrote {len(result.clips)} WAV file(s) into {args.outputDir}")
        if args.verbose:
            print(f"Wrote metadata: {written[-1]}")
        return 0
    print("No exportable embedded audio: " +
          (result.warnings[0] if result.warnings else
           "bank contains only synthesis objects and/or ROM/external sample references"), file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

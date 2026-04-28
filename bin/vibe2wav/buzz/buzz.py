#!/usr/bin/env python3
# Vibe coded by Codex
"""Strict Jeskola Buzz container parser and raw wavetable WAV converter."""

from __future__ import annotations

import argparse
import math
import os
from dataclasses import dataclass
from pathlib import Path
import re
import struct
import sys
import wave


class BuzzError(Exception):
    """Raised when an input is not one of the supported Buzz sample files."""


class Reader:
    def __init__(self, data: bytes, label: str):
        self.data = data
        self.label = label
        self.pos = 0

    def require(self, size: int) -> None:
        if size < 0 or self.pos + size > len(self.data):
            raise BuzzError(f"{self.label}: truncated at offset {self.pos}")

    def read(self, size: int) -> bytes:
        self.require(size)
        out = self.data[self.pos : self.pos + size]
        self.pos += size
        return out

    def u8(self) -> int:
        return self.read(1)[0]

    def u16(self) -> int:
        value = struct.unpack_from("<H", self.data, self.pos)[0]
        self.pos += 2
        return value

    def u32(self) -> int:
        value = struct.unpack_from("<I", self.data, self.pos)[0]
        self.pos += 4
        return value

    def i32(self) -> int:
        value = struct.unpack_from("<i", self.data, self.pos)[0]
        self.pos += 4
        return value

    def f32(self) -> float:
        value = struct.unpack_from("<f", self.data, self.pos)[0]
        self.pos += 4
        return value

    def zstr(self) -> str:
        end = self.data.find(b"\x00", self.pos)
        if end < 0:
            raise BuzzError(f"{self.label}: unterminated string at offset {self.pos}")
        raw = self.data[self.pos : end]
        self.pos = end + 1
        return raw.decode("latin-1")

    def finish(self) -> None:
        if self.pos != len(self.data):
            raise BuzzError(
                f"{self.label}: {len(self.data) - self.pos} unconsumed bytes at offset {self.pos}"
            )


@dataclass
class Section:
    tag: str
    offset: int
    declared_size: int
    data: bytes
    trailing_continuation: int = 0


@dataclass
class Parameter:
    kind: int
    name: str
    min_value: int
    max_value: int
    no_value: int
    flags: int
    default_value: int


@dataclass
class MachineParameters:
    name: str
    machine_type: str
    global_count: int
    track_count: int
    parameters: list[Parameter]


@dataclass
class WaveLevel:
    sample_count: int
    loop_begin: int
    loop_end: int
    samples_per_second: int
    root_note: int


@dataclass
class WaveEntry:
    index: int
    file_name: str
    name: str
    volume: float
    flags: int
    levels: list[WaveLevel]

    @property
    def is_stereo(self) -> bool:
        return bool(self.flags & 0x08)

    @property
    def is_float(self) -> bool:
        return bool(self.flags & 0x04)


@dataclass
class RawWave:
    entry: WaveEntry
    level: WaveLevel
    pcm: bytes


def parameter_size(kind: int) -> int:
    if kind == 3:
        return 2
    if kind in (0, 1, 2):
        return 1
    raise BuzzError(f"unknown parameter kind {kind}")


def parse_sections(data: bytes) -> dict[str, Section]:
    if len(data) < 380:
        raise BuzzError("file is shorter than the fixed Buzz header")
    if data[:4] != b"Buzz":
        raise BuzzError("missing Buzz magic")

    section_count = struct.unpack_from("<I", data, 4)[0]
    if section_count > 31:
        raise BuzzError(f"section count {section_count} exceeds directory capacity")

    entries: list[tuple[str, int, int]] = []
    seen: set[str] = set()
    for i in range(31):
        base = 8 + i * 12
        raw_tag = data[base : base + 4]
        offset, size = struct.unpack_from("<II", data, base + 4)
        if i >= section_count:
            if raw_tag != b"\x00\x00\x00\x00" or offset != 0 or size != 0:
                raise BuzzError(f"unused directory entry {i} is not zero-filled")
            continue
        try:
            tag = raw_tag.decode("ascii")
        except UnicodeDecodeError as exc:
            raise BuzzError(f"directory entry {i} has a non-ASCII tag") from exc
        if not re.fullmatch(r"[A-Z0-9 ]{4}", tag):
            raise BuzzError(f"directory entry {i} has invalid tag {tag!r}")
        if tag in seen:
            raise BuzzError(f"duplicate section {tag}")
        seen.add(tag)
        entries.append((tag, offset, size))

    if not entries:
        raise BuzzError("Buzz file has no sections")
    ordered = sorted(entries, key=lambda item: item[1])
    if ordered[0][1] != 380:
        raise BuzzError(f"first section starts at {ordered[0][1]}, expected 380")

    sections: dict[str, Section] = {}
    for i, (tag, offset, declared_size) in enumerate(ordered):
        if offset < 380 or offset > len(data):
            raise BuzzError(f"section {tag} has invalid offset {offset}")
        declared_end = offset + declared_size
        next_offset = ordered[i + 1][1] if i + 1 < len(ordered) else len(data)
        if declared_end > next_offset:
            raise BuzzError(f"section {tag} overlaps following data")
        if declared_end < next_offset and i + 1 < len(ordered):
            raise BuzzError(f"gap after section {tag}")
        effective_end = next_offset
        trailing = effective_end - declared_end
        sections[tag] = Section(tag, offset, declared_size, data[offset:effective_end], trailing)
    return sections


def parse_para(section: Section) -> list[MachineParameters]:
    r = Reader(section.data, "PARA")
    count = r.u32()
    machines: list[MachineParameters] = []
    for _ in range(count):
        name = r.zstr()
        machine_type = r.zstr()
        global_count = r.u32()
        track_count = r.u32()
        parameters: list[Parameter] = []
        for _ in range(global_count + track_count):
            parameters.append(
                Parameter(r.u8(), r.zstr(), r.i32(), r.i32(), r.i32(), r.i32(), r.i32())
            )
        machines.append(MachineParameters(name, machine_type, global_count, track_count, parameters))
    r.finish()
    return machines


def parse_mach(section: Section, para: list[MachineParameters] | None) -> None:
    r = Reader(section.data, "MACH")
    count = r.u16()
    if para is None:
        return
    if len(para) != count:
        raise BuzzError(f"MACH/PARA machine count mismatch: {count} != {len(para)}")
    for i in range(count):
        r.zstr()
        machine_kind = r.u8()
        if machine_kind in (1, 2):
            r.zstr()
        elif machine_kind != 0:
            raise BuzzError(f"MACH: invalid machine type {machine_kind}")
        r.f32()
        r.f32()
        data_size = r.u32()
        r.read(data_size)
        attribute_count = r.u16()
        for _ in range(attribute_count):
            r.zstr()
            r.u32()
        params = para[i].parameters
        global_size = sum(parameter_size(p.kind) for p in params[: para[i].global_count])
        track_size = sum(parameter_size(p.kind) for p in params[para[i].global_count :])
        r.read(global_size)
        track_count = r.u16()
        r.read(track_count * track_size)
    r.finish()


def parse_wavt(section: Section) -> list[WaveEntry]:
    r = Reader(section.data, "WAVT")
    count = r.u16()
    waves: list[WaveEntry] = []
    for _ in range(count):
        index = r.u16()
        file_name = r.zstr()
        name = r.zstr()
        volume = r.f32()
        flags = r.u8()
        if flags & 0x80:
            envelope_count = r.u16()
            for _ in range(envelope_count):
                r.read(10)
                point_count_field = r.u16()
                point_count = point_count_field & 0x7FFF
                r.read(point_count * 5)
        level_count = r.u8()
        levels: list[WaveLevel] = []
        for _ in range(level_count):
            levels.append(WaveLevel(r.u32(), r.u32(), r.u32(), r.u32(), r.u8()))
        waves.append(WaveEntry(index, file_name, name, volume, flags, levels))
    r.finish()
    return waves


def level_bytes(entry: WaveEntry, level: WaveLevel) -> int:
    channels = 2 if entry.is_stereo else 1
    sample_size = 4 if entry.is_float else 2
    return level.sample_count * channels * sample_size


def parse_wave_data(section: Section, wavetable: list[WaveEntry]) -> list[RawWave]:
    by_index = {entry.index: entry for entry in wavetable}
    r = Reader(section.data, section.tag)
    wave_count = r.u16()
    if wave_count == 0:
        r.finish()
        return []

    if section.tag == "CWAV":
        # The public format identifies format 1 as proprietary compression but
        # does not include compressed block sizes. Decoding is required before
        # later wave headers can be located, so the stream is intentionally
        # rejected as unsupported audio rather than guessed.
        raise BuzzError("CWAV compressed wave data is not supported by this converter")

    out: list[RawWave] = []
    for _ in range(wave_count):
        index = r.u16()
        fmt = r.u8()
        if fmt != 0:
            raise BuzzError(f"WAVE: unsupported wave format {fmt} for wave {index}")
        byte_count = r.u32()
        payload = r.read(byte_count)
        if index not in by_index:
            raise BuzzError(f"WAVE: data for wave {index} has no WAVT entry")
        entry = by_index[index]
        expected = sum(level_bytes(entry, level) for level in entry.levels)
        if byte_count != expected:
            raise BuzzError(f"WAVE: wave {index} has {byte_count} bytes, expected {expected}")
        pos = 0
        for level in entry.levels:
            size = level_bytes(entry, level)
            out.append(RawWave(entry, level, payload[pos : pos + size]))
            pos += size
    r.finish()
    return out


def parse_conn(section: Section) -> None:
    r = Reader(section.data, "CONN")
    count = r.u16()
    for _ in range(count):
        r.u16()
        r.u16()
        r.u16()
        r.u16()
    r.finish()


def parse_sequ(section: Section) -> None:
    r = Reader(section.data, "SEQU")
    r.u32()
    r.u32()
    r.u32()
    count = r.u16()
    for _ in range(count):
        r.u16()
        event_count = r.u32()
        if event_count == 0:
            continue
        pos_size = r.u8()
        event_size = r.u8()
        if pos_size not in (1, 2, 4) or event_size not in (1, 2, 4):
            raise BuzzError("SEQU: unsupported event width")
        r.read(event_count * (pos_size + event_size))
    r.finish()


def parse_blah(section: Section) -> None:
    r = Reader(section.data, "BLAH")
    size = r.u32()
    r.read(size)
    r.finish()


def parse_bver(section: Section) -> None:
    r = Reader(section.data, "BVER")
    r.zstr()
    r.finish()


def parse_pdlig(section: Section) -> None:
    r = Reader(section.data, "PDLG")
    if not section.data:
        return
    r.u8()
    while r.pos < len(r.data):
        if r.data[r.pos] == 0:
            r.u8()
            break
        r.zstr()
        r.read(44)
    r.finish()


def parse_midi(section: Section) -> None:
    r = Reader(section.data, "MIDI")
    while r.pos < len(r.data):
        if r.data[r.pos] == 0:
            r.u8()
            break
        r.zstr()
        r.read(5)
    r.finish()


def parse_known_sections(sections: dict[str, Section]) -> tuple[list[WaveEntry], list[RawWave]]:
    allowed = {"BVER", "PARA", "MACH", "CONN", "WAVT", "PATT", "SEQU", "BLAH", "PDLG", "MIDI", "WAVE", "CWAV"}
    unknown = sorted(set(sections) - allowed)
    if unknown:
        raise BuzzError(f"unsupported sections: {', '.join(unknown)}")

    para = parse_para(sections["PARA"]) if "PARA" in sections else None
    if "MACH" in sections:
        parse_mach(sections["MACH"], para)
    if "CONN" in sections:
        parse_conn(sections["CONN"])
    if "SEQU" in sections:
        parse_sequ(sections["SEQU"])
    if "BLAH" in sections:
        parse_blah(sections["BLAH"])
    if "BVER" in sections:
        parse_bver(sections["BVER"])
    if "PDLG" in sections:
        parse_pdlig(sections["PDLG"])
    if "MIDI" in sections:
        parse_midi(sections["MIDI"])

    wavetable = parse_wavt(sections["WAVT"]) if "WAVT" in sections else []
    wave_section = sections.get("WAVE") or sections.get("CWAV")
    if wave_section is None:
        return wavetable, []
    waves = parse_wave_data(wave_section, wavetable)
    return wavetable, waves


def int16_at(data: bytes, index: int) -> int:
    return struct.unpack_from("<h", data, index * 2)[0]


def render_level(raw: RawWave, target_rate: int) -> list[tuple[int, int]]:
    if raw.entry.is_float:
        raise BuzzError(f"wave {raw.entry.index} uses float samples, unsupported")
    channels = 2 if raw.entry.is_stereo else 1
    frame_count = raw.level.sample_count
    if frame_count == 0:
        return []

    frames: list[tuple[int, int]] = []
    if channels == 1:
        for i in range(frame_count):
            sample = int16_at(raw.pcm, i)
            frames.append((sample, sample))
    else:
        for i in range(frame_count):
            left = int16_at(raw.pcm, i * 2)
            right = int16_at(raw.pcm, i * 2 + 1)
            frames.append((left, right))

    source_rate = raw.level.samples_per_second
    if source_rate <= 0:
        raise BuzzError(f"wave {raw.entry.index} has invalid sample rate {source_rate}")
    if source_rate == target_rate or len(frames) < 2:
        return frames

    ratio = source_rate / target_rate
    out_count = max(1, int(round(len(frames) * target_rate / source_rate)))
    out: list[tuple[int, int]] = []
    for i in range(out_count):
        src = i * ratio
        left_index = min(int(math.floor(src)), len(frames) - 1)
        right_index = min(left_index + 1, len(frames) - 1)
        frac = src - left_index
        l0, r0 = frames[left_index]
        l1, r1 = frames[right_index]
        out.append((round(l0 + (l1 - l0) * frac), round(r0 + (r1 - r0) * frac)))
    return out


def sanitize_text(value: str, fallback: str) -> str:
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._")
    return stem or fallback


def output_name(raw: RawWave, level_index: int, level_count: int, used: set[str]) -> str:
    base = sanitize_text(raw.entry.name, f"wave_{raw.entry.index:02d}")
    if level_count > 1:
        base = f"{base}_level_{level_index + 1}"
    name = f"{base}.wav"
    if name not in used:
        used.add(name)
        return name
    suffix = 2
    while True:
        candidate = f"{base}_{suffix}.wav"
        if candidate not in used:
            used.add(candidate)
            return candidate
        suffix += 1


def write_wav(path: Path, frames: list[tuple[int, int]], rate: int) -> None:
    tmp_file = path.with_suffix(path.suffix + ".tmp")
    try:
        with wave.open(str(tmp_file), "wb") as out:
            out.setnchannels(2)
            out.setsampwidth(2)
            out.setframerate(rate)
            packed = bytearray()
            for left, right in frames:
                packed.extend(
                    struct.pack(
                        "<hh",
                        max(-32768, min(32767, left)),
                        max(-32768, min(32767, right)),
                    )
                )
            out.writeframes(bytes(packed))
        os.replace(tmp_file, path)
    except Exception:
        try:
            tmp_file.unlink()
        except FileNotFoundError:
            pass
        raise


def convert(input_file: Path, output_dir: Path) -> list[Path]:
    data = input_file.read_bytes()
    sections = parse_sections(data)
    _, waves = parse_known_sections(sections)
    if not waves:
        raise BuzzError("no supported raw WAVE audio is embedded in this file")

    target_rate = 44100
    rendered: list[tuple[RawWave, list[tuple[int, int]]]] = []
    for raw in waves:
        frames = render_level(raw, target_rate)
        if not frames:
            raise BuzzError(f"wave {raw.entry.index} decoded to empty audio")
        rendered.append((raw, frames))

    output_dir.mkdir(parents=True, exist_ok=True)
    level_counts: dict[int, int] = {}
    for raw in waves:
        level_counts[raw.entry.index] = level_counts.get(raw.entry.index, 0) + 1
    level_positions: dict[int, int] = {}
    used: set[str] = set()
    output_files: list[Path] = []

    for raw, frames in rendered:
        level_index = level_positions.get(raw.entry.index, 0)
        level_positions[raw.entry.index] = level_index + 1
        name = output_name(raw, level_index, level_counts[raw.entry.index], used)
        output_file = output_dir / name
        write_wav(output_file, frames, target_rate)
        output_files.append(output_file)
    return output_files


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Convert supported Jeskola Buzz raw WAVE data to WAV.")
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputDir", type=Path)
    args = parser.parse_args(argv)

    try:
        output = convert(args.inputFile, args.outputDir)
    except BuzzError as exc:
        print(f"buzz.py: {exc}", file=sys.stderr)
        return 1
    for path in output:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

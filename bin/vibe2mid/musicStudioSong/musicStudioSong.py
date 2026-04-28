#!/usr/bin/env python3
# Vibe coded by Codex
from __future__ import annotations

import os
import struct
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path


MAGIC_STUDIO = b"\xcdMstudio\xcd\x02"
MAGIC_STUDIO_88 = b"\xceMstudio\xce\x02"
TPQ = 96
UNIT_TICKS = 8


class FormatError(Exception):
    pass


@dataclass
class NoteEvent:
    time: int
    voice: int
    duration: int
    pitch: int
    raw_voice: int
    raw_duration: int
    raw_pitch: int


@dataclass
class ControlEvent:
    time: int
    opcode: int
    args: bytes


@dataclass
class ParsedSong:
    variant: str
    title: str
    voice_names: list[str]
    midi_names: list[str]
    control_prefix: bytes
    trailer: bytes
    notes: list[NoteEvent] = field(default_factory=list)
    controls: list[ControlEvent] = field(default_factory=list)


def decode_field(raw: bytes) -> str:
    return raw.split(b"\x00", 1)[0].decode("latin-1", "replace").strip()


def read_names(data: bytes, offset: int) -> list[str]:
    return [decode_field(data[offset + i * 10 : offset + (i + 1) * 10]) for i in range(15)]


def find_score_start(path: Path, data: bytes) -> tuple[int, int, int]:
    if data.startswith(MAGIC_STUDIO):
        if len(data) < 0x20A:
            raise FormatError("truncated Music Studio file")
        return 0x1E0, 0x200, 0x209

    if data.startswith(MAGIC_STUDIO_88):
        if len(data) < 0x642:
            raise FormatError("truncated Music Studio 88 file")
        candidates = (0x641, 0x637)
        for score_start in candidates:
            if score_start < len(data) and data[score_start] in (0x80, 0x83):
                title_start = score_start - 0x29
                prefix_start = score_start - 9
                if title_start >= 0:
                    return title_start, prefix_start, score_start
        raise FormatError("Music Studio 88 score preamble not found")

    raise FormatError("missing Music Studio magic")


def parse_song(path: Path) -> ParsedSong:
    data = path.read_bytes()
    title_offset, prefix_offset, pos = find_score_start(path, data)

    if data.startswith(MAGIC_STUDIO):
        variant = "Music Studio"
        voice_names = read_names(data, 0x00A)
        midi_names = read_names(data, 0x118)
    else:
        variant = "Music Studio 88"
        voice_names = read_names(data, 0x00A)
        # The Music Studio 88 samples have a variable-size instrument-definition
        # area, but the second 15-name table is fixed relative to the score.
        midi_names = read_names(data, pos - 0xF1)

    title = decode_field(data[title_offset : title_offset + 32])
    control_prefix = data[prefix_offset:pos]

    song = ParsedSong(
        variant=variant,
        title=title,
        voice_names=voice_names,
        midi_names=midi_names,
        control_prefix=control_prefix,
        trailer=b"",
    )

    group: list[NoteEvent] = []
    time_units = 0

    def close_group() -> None:
        nonlocal time_units, group
        if group:
            step = min(max(1, n.duration) for n in group)
            time_units += step
            group = []
        else:
            time_units += 1

    while pos < len(data):
        b = data[pos]

        if b == 0xFF:
            song.trailer = data[pos + 1 :]
            return song

        if b == 0x00:
            close_group()
            pos += 1
            continue

        if b == 0x60:
            song.controls.append(ControlEvent(time_units, b, b""))
            pos += 1
            continue

        if b == 0x80:
            need = 3
        elif b == 0x81:
            need = 2
        elif b == 0x82 and pos + 1 < len(data) and data[pos + 1] == 0x00:
            if pos + 1 >= len(data):
                raise FormatError(f"truncated 0x82 control at 0x{pos:x}")
            song.controls.append(ControlEvent(time_units, b, data[pos + 1 : pos + 2]))
            close_group()
            pos += 2
            continue
        elif b == 0x83:
            need = 2
        elif b == 0x84:
            need = 3
        elif b == 0x85 and pos + 1 < len(data) and data[pos + 1] <= 0x04 and (
            pos + 2 >= len(data) or data[pos + 2] in (0x00, 0xFF)
        ):
            need = 2
        elif b == 0x86:
            if pos + 1 >= len(data):
                raise FormatError(f"truncated 0x86 control at 0x{pos:x}")
            song.controls.append(ControlEvent(time_units, b, data[pos + 1 : pos + 2]))
            close_group()
            pos += 2
            continue
        else:
            need = 0

        if need:
            if pos + need > len(data):
                raise FormatError(f"truncated control 0x{b:02x} at 0x{pos:x}")
            song.controls.append(ControlEvent(time_units, b, data[pos + 1 : pos + need]))
            pos += need
            continue

        if pos + 3 > len(data):
            raise FormatError(f"truncated note at 0x{pos:x}")
        raw_voice, raw_duration, raw_pitch = data[pos : pos + 3]
        if raw_duration == 0:
            raise FormatError(
                f"invalid zero-duration note at 0x{pos:x}: "
                f"{raw_voice:02x} {raw_duration:02x} {raw_pitch:02x}"
            )
        voice = raw_voice & 0x0F
        if not 1 <= voice <= 15:
            raise FormatError(f"invalid voice nibble {voice} at 0x{pos:x}")
        duration = raw_duration & 0x7F
        pitch = raw_pitch & 0x7F
        if duration == 0:
            raise FormatError(f"invalid normalized note at 0x{pos:x}")
        note = NoteEvent(
            time=time_units,
            voice=voice,
            duration=duration,
            pitch=pitch,
            raw_voice=raw_voice,
            raw_duration=raw_duration,
            raw_pitch=raw_pitch,
        )
        song.notes.append(note)
        group.append(note)
        pos += 3

    raise FormatError("score stream has no 0xff terminator")


def vlq(value: int) -> bytes:
    if value < 0:
        raise ValueError("negative delta")
    out = [value & 0x7F]
    value >>= 7
    while value:
        out.append(0x80 | (value & 0x7F))
        value >>= 7
    return bytes(reversed(out))


def meta_event(delta: int, kind: int, payload: bytes) -> bytes:
    return vlq(delta) + bytes([0xFF, kind]) + vlq(len(payload)) + payload


def midi_event(delta: int, status: int, *data: int) -> bytes:
    return vlq(delta) + bytes([status, *data])


def name_to_program(name: str) -> int:
    n = name.lower().replace(".", "").replace(" ", "")
    mapping = [
        ("piano", 0),
        ("honky", 3),
        ("organ", 16),
        ("accord", 21),
        ("harmonica", 22),
        ("guitar", 24),
        ("electricg", 27),
        ("fiddle", 40),
        ("violin", 40),
        ("cello", 42),
        ("bassoon", 70),
        ("bass", 32),
        ("strings", 48),
        ("tuba", 58),
        ("horn", 60),
        ("trump", 56),
        ("sax", 65),
        ("baritone", 67),
        ("clarinet", 71),
        ("flute", 73),
        ("piccolo", 72),
        ("vibes", 11),
        ("bells", 14),
        ("hihat", 0),
        ("snare", 0),
        ("conga", 0),
        ("block", 115),
    ]
    for key, program in mapping:
        if key in n:
            return program
    return 0


def tempo_from_song(song: ParsedSong) -> int:
    for c in song.controls:
        if c.opcode == 0x81 and c.args:
            bpm = c.args[0]
            if 20 <= bpm <= 240:
                return bpm
    return 120


def build_midi(song: ParsedSong) -> bytes:
    title = song.title or "Music Studio Song"
    tempo_bpm = tempo_from_song(song)
    tempo_us = int(60_000_000 / tempo_bpm)

    track = bytearray()
    track += meta_event(0, 0x03, title.encode("latin-1", "replace"))
    track += meta_event(0, 0x51, tempo_us.to_bytes(3, "big"))
    track += meta_event(0, 0x58, bytes([4, 2, 24, 8]))

    for voice in range(1, 16):
        midi_channel = voice - 1
        name = song.midi_names[voice - 1] or song.voice_names[voice - 1]
        program = name_to_program(name)
        track += midi_event(0, 0xC0 | midi_channel, program)
        track += midi_event(0, 0xB0 | midi_channel, 7, 96)
        track += midi_event(0, 0xB0 | midi_channel, 10, int(12 + (voice - 1) * 7.7))

    events: list[tuple[int, int, bytes]] = []
    order = 0
    for n in song.notes:
        start = n.time * UNIT_TICKS
        duration = max(1, n.duration) * UNIT_TICKS
        channel = n.voice - 1
        velocity = 84
        if n.raw_duration & 0x80:
            velocity = 64
        if n.raw_pitch & 0x80:
            velocity = 54
        events.append((start, order, bytes([0x90 | channel, n.pitch, velocity])))
        order += 1
        events.append((start + duration, order, bytes([0x80 | channel, n.pitch, 0])))
        order += 1

    events.sort(key=lambda item: (item[0], item[1]))
    current = 0
    for when, _, payload in events:
        track += vlq(when - current) + payload
        current = when
    track += meta_event(0, 0x2F, b"")

    header = b"MThd" + struct.pack(">IHHH", 6, 0, 1, TPQ)
    return header + b"MTrk" + struct.pack(">I", len(track)) + bytes(track)


def convert(input_path: Path, output_path: Path) -> None:
    song = parse_song(input_path)
    midi = build_midi(song)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=output_path.name + ".", suffix=".tmp", dir=output_path.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(midi)
        os.chmod(tmp_name, 0o664)
        os.replace(tmp_name, output_path)
        os.chmod(output_path, 0o664)
    except Exception:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: musicStudioSong.py <inputFile> <out.mid>", file=sys.stderr)
        return 2
    input_path = Path(argv[1])
    output_path = Path(argv[2])
    try:
        convert(input_path, output_path)
    except Exception as exc:
        print(f"musicStudioSong: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

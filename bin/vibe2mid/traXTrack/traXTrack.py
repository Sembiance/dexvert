#!/usr/bin/env python3
# Vibe coded by Codex
"""
Convert Passport Trax/Master Tracks .MTS music tracks to Standard MIDI files.
"""

from __future__ import annotations

import html
import os
import struct
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


class MtsError(Exception):
    pass


def u16(data: bytes, off: int) -> int:
    if off + 2 > len(data):
        raise MtsError("unexpected end of file")
    return struct.unpack_from("<H", data, off)[0]


def u32(data: bytes, off: int) -> int:
    if off + 4 > len(data):
        raise MtsError("unexpected end of file")
    return struct.unpack_from("<I", data, off)[0]


def cstr(raw: bytes) -> str:
    return raw.split(b"\0", 1)[0].decode("latin-1")


@dataclass
class ConductorRecord:
    tempo: int
    tick_base: int
    ticks_per_bar: int
    numerator: int
    denominator: int
    seconds: float
    seconds_fraction: int
    tempo_points: list[tuple[int, int]]
    raw: bytes


@dataclass
class MidiEvent:
    tick: int
    order: int
    data: bytes


@dataclass
class NoteEvent:
    tick: int
    order: int
    status: int
    note: int
    velocity: int
    release_velocity: int
    flags: int
    duration: int


@dataclass
class Track:
    index: int
    name: str
    measure_count: int
    channel_field: int
    program: int
    events: list[MidiEvent]
    notes: list[NoteEvent]


@dataclass
class Marker:
    measure: int
    tick_hint: int
    text: str


@dataclass
class Song:
    name: str
    timebase: int
    conductor: list[ConductorRecord]
    tracks: list[Track]
    markers: list[Marker]
    notes_text: str


def parse_conductor_record(record: bytes) -> ConductorRecord:
    if len(record) < 18:
        raise MtsError("truncated conductor record")
    payload_len = u16(record, 0)
    if payload_len + 2 != len(record):
        raise MtsError("bad conductor record length")
    tempo = u16(record, 2)
    zero = u16(record, 4)
    tick_base = u16(record, 6)
    ticks_per_bar = u16(record, 8)
    numerator = record[10]
    denominator = record[11]
    seconds = struct.unpack_from("<f", record, 12)[0]
    seconds_fraction = u16(record, 16)
    if zero != 0:
        raise MtsError("unexpected non-zero conductor reserved field")
    if tempo == 0 or tick_base == 0 or ticks_per_bar == 0:
        raise MtsError("invalid conductor timing values")
    if numerator == 0 or denominator == 0 or denominator & (denominator - 1):
        raise MtsError("invalid conductor time signature")

    tempo_points: list[tuple[int, int]] = []
    extra = record[18:]
    if extra:
        if len(extra) < 2 or extra[-2:] != b"\xff\xff":
            raise MtsError("bad conductor tempo-point terminator")
        body = extra[:-2]
        if len(body) % 4:
            raise MtsError("bad conductor tempo-point length")
        for off in range(0, len(body), 4):
            tick = u16(body, off)
            bpm = u16(body, off + 2)
            if bpm == 0:
                raise MtsError("invalid conductor tempo point")
            tempo_points.append((tick, bpm))

    return ConductorRecord(
        tempo=tempo,
        tick_base=tick_base,
        ticks_per_bar=ticks_per_bar,
        numerator=numerator,
        denominator=denominator,
        seconds=seconds,
        seconds_fraction=seconds_fraction,
        tempo_points=tempo_points,
        raw=record,
    )


def parse_track_measures(data: bytes, off: int, count: int, measure_starts: list[int]) -> tuple[list[MidiEvent], list[NoteEvent], int]:
    midi_events: list[MidiEvent] = []
    notes: list[NoteEvent] = []
    order = 0
    for measure_index in range(count):
        if off + 4 > len(data):
            raise MtsError("truncated measure block")
        block_len = u16(data, off)
        if block_len < 2 or off + block_len + 2 > len(data):
            raise MtsError("bad measure block length")
        if data[off + block_len:off + block_len + 2] != b"\xff\xff":
            raise MtsError("bad measure block terminator")

        measure_tick = measure_starts[measure_index] if measure_index < len(measure_starts) else measure_starts[-1]
        pos = off + 2
        end = off + block_len
        while pos < end:
            start = u16(data, pos)
            status = data[pos + 2]
            kind = status >> 4
            abs_tick = measure_tick + start
            if kind in (0x8, 0x9):
                if pos + 10 > end:
                    raise MtsError("truncated note event")
                note = data[pos + 3]
                velocity = data[pos + 4]
                release_velocity = data[pos + 5]
                flags = u16(data, pos + 6)
                duration = u16(data, pos + 8)
                if note > 127 or velocity > 127 or release_velocity > 127:
                    raise MtsError("invalid note event data")
                if flags > 3:
                    raise MtsError("invalid note notation flags")
                notes.append(NoteEvent(abs_tick, order, status, note, velocity, release_velocity, flags, duration))
                pos += 10
            elif kind in (0xA, 0xB, 0xC, 0xD, 0xE):
                if pos + 6 > end:
                    raise MtsError("truncated MIDI event")
                d1 = data[pos + 3]
                d2 = data[pos + 4]
                pad = data[pos + 5]
                if d1 > 127 or d2 > 127 or pad != 0:
                    raise MtsError("invalid MIDI event data")
                if kind in (0xC, 0xD):
                    msg = bytes([status, d1])
                else:
                    msg = bytes([status, d1, d2])
                midi_events.append(MidiEvent(abs_tick, order, msg))
                pos += 6
            else:
                raise MtsError(f"unsupported event status 0x{status:02x}")
            order += 1
        off += block_len + 2
    return midi_events, notes, off


def parse_mark_chunk(payload: bytes) -> list[Marker]:
    if len(payload) % 48 == 0:
        record_len = 48
    elif len(payload) % 112 == 0:
        record_len = 112
    else:
        raise MtsError("bad MARK chunk length")
    markers: list[Marker] = []
    for off in range(0, len(payload), record_len):
        rec = payload[off:off + record_len]
        text = cstr(rec[16:48])
        markers.append(Marker(measure=u16(rec, 2), tick_hint=u32(rec, 8), text=text))
    return markers


def parse_song(path: Path) -> Song:
    data = path.read_bytes()
    if len(data) < 128:
        raise MtsError("file is too short")
    if data[:8] != b"RO\0\0@\0\0\0":
        raise MtsError("not a TraX/Master Tracks RO file")

    name = cstr(data[8:40])
    timebase = u16(data, 42)
    conductor_count = u16(data, 50)
    if timebase != 240 or conductor_count == 0:
        raise MtsError("unsupported root timing")
    if u16(data, 46) != 0xFFFF or u16(data, 48) != 0:
        raise MtsError("unexpected root reserved fields")

    off = 64
    conductor: list[ConductorRecord] | None = None
    tracks: list[Track] = []
    markers: list[Marker] = []
    notes_text = ""

    while off < len(data):
        if off + 8 > len(data):
            raise MtsError("truncated chunk header")
        chunk_id = data[off:off + 4]
        chunk_size = u32(data, off + 4)
        if chunk_size < 8 or off + chunk_size > len(data):
            raise MtsError("bad chunk size")

        if chunk_id[:2] == b"TK" and chunk_size == 64:
            try:
                index = int(chunk_id[2:4].decode("ascii"))
            except ValueError as exc:
                raise MtsError("bad track id") from exc
            if not tracks and index != 0:
                raise MtsError("missing conductor track")
            if tracks and index == 0:
                raise MtsError("duplicate conductor track")
            header = data[off:off + 64]
            track_name = cstr(header[8:40])
            measure_count = u16(header, 40)
            channel_field = u16(header, 48)
            program = u16(header, 50)
            body_off = off + 64

            if index == 0:
                conductor = []
                cur = body_off
                for _ in range(measure_count):
                    rec_len = u16(data, cur)
                    if rec_len < 16 or cur + rec_len + 2 > len(data):
                        raise MtsError("bad conductor record length")
                    conductor.append(parse_conductor_record(data[cur:cur + rec_len + 2]))
                    cur += rec_len + 2
                off = cur
                measure_starts = [0]
                total = 0
                for rec in conductor:
                    total += rec.ticks_per_bar
                    measure_starts.append(total)
                tracks.append(Track(index, track_name, measure_count, channel_field, program, [], []))
            else:
                if conductor is None:
                    raise MtsError("track appears before conductor")
                measure_starts = [0]
                total = 0
                for rec in conductor:
                    total += rec.ticks_per_bar
                    measure_starts.append(total)
                events, note_events, off = parse_track_measures(data, body_off, measure_count, measure_starts)
                tracks.append(Track(index, track_name, measure_count, channel_field, program, events, note_events))
            continue

        if chunk_id == b"MARK":
            markers.extend(parse_mark_chunk(data[off + 8:off + chunk_size]))
        elif chunk_id == b"N?TE":
            notes_text = data[off + 8:off + chunk_size].rstrip(b"\0").decode("latin-1")
        else:
            raise MtsError(f"unsupported chunk {chunk_id!r}")
        off += chunk_size

    if conductor is None:
        raise MtsError("missing conductor track")
    return Song(name, timebase, conductor, tracks, markers, notes_text)


def vlq(value: int) -> bytes:
    if value < 0:
        raise ValueError("negative delta")
    out = [value & 0x7F]
    value >>= 7
    while value:
        out.append((value & 0x7F) | 0x80)
        value >>= 7
    return bytes(reversed(out))


def meta_event(delta: int, typ: int, payload: bytes) -> bytes:
    return vlq(delta) + bytes([0xFF, typ]) + vlq(len(payload)) + payload


def midi_track(events: list[tuple[int, int, bytes]]) -> bytes:
    events.sort(key=lambda item: (item[0], item[1]))
    out = bytearray()
    last = 0
    for tick, _order, payload in events:
        out.extend(vlq(tick - last))
        out.extend(payload)
        last = tick
    out.extend(meta_event(0, 0x2F, b""))
    return b"MTrk" + struct.pack(">I", len(out)) + bytes(out)


def midi_meta_payload(typ: int, payload: bytes) -> bytes:
    return bytes([0xFF, typ]) + vlq(len(payload)) + payload


def bpm_to_mpqn(bpm: int) -> bytes:
    mpqn = round(60_000_000 / bpm)
    return mpqn.to_bytes(3, "big")


def denominator_power(denominator: int) -> int:
    power = 0
    while denominator > 1:
        denominator >>= 1
        power += 1
    return power


def build_midi(song: Song) -> bytes:
    measure_starts = [0]
    total = 0
    for rec in song.conductor:
        total += rec.ticks_per_bar
        measure_starts.append(total)

    conductor_events: list[tuple[int, int, bytes]] = []
    title = song.name.encode("latin-1", "replace")
    conductor_events.append((0, 0, midi_meta_payload(0x03, title)))
    last_sig: tuple[int, int] | None = None
    last_tempo: int | None = None
    for i, rec in enumerate(song.conductor):
        tick = measure_starts[i]
        if rec.tempo != last_tempo:
            conductor_events.append((tick, 1, midi_meta_payload(0x51, bpm_to_mpqn(rec.tempo))))
            last_tempo = rec.tempo
        sig = (rec.numerator, rec.denominator)
        if sig != last_sig:
            conductor_events.append((tick, 2, midi_meta_payload(0x58, bytes([rec.numerator, denominator_power(rec.denominator), 24, 8]))))
            last_sig = sig
        for j, (point_tick, bpm) in enumerate(rec.tempo_points):
            conductor_events.append((tick + point_tick, 3 + j, midi_meta_payload(0x51, bpm_to_mpqn(bpm))))
    for marker in song.markers:
        if marker.text:
            tick = measure_starts[min(marker.measure, len(measure_starts) - 1)]
            conductor_events.append((tick, 1000, midi_meta_payload(0x06, marker.text.encode("latin-1", "replace"))))
    if song.notes_text:
        conductor_events.append((0, 2000, midi_meta_payload(0x01, song.notes_text.encode("latin-1", "replace"))))

    chunks = [midi_track(conductor_events)]
    for track in song.tracks[1:]:
        events: list[tuple[int, int, bytes]] = []
        events.append((0, 0, midi_meta_payload(0x03, track.name.encode("latin-1", "replace"))))

        channel = None
        if track.channel_field & 0xFF:
            high = (track.channel_field >> 8) & 0xFF
            if 1 <= high <= 16:
                channel = high - 1
        if channel is None:
            for event in track.events:
                if event.data and 0x80 <= event.data[0] <= 0xEF:
                    channel = event.data[0] & 0x0F
                    break
            if channel is None and track.notes:
                channel = track.notes[0].status & 0x0F
        if channel is not None and 0 < track.program < 128 and channel != 9:
            events.append((0, 1, bytes([0xC0 | channel, track.program])))

        for event in track.events:
            events.append((event.tick, 100 + event.order, event.data))
        for note in track.notes:
            channel = note.status & 0x0F
            status = 0x90 | channel
            off_status = 0x80 | channel
            events.append((note.tick, 100 + note.order, bytes([status, note.note, note.velocity])))
            events.append((note.tick + note.duration, 50 + note.order, bytes([off_status, note.note, note.release_velocity])))
        chunks.append(midi_track(events))

    header = b"MThd" + struct.pack(">IHHH", 6, 1, len(chunks), song.timebase)
    return header + b"".join(chunks)


def convert(input_file: Path, output_file: Path) -> None:
    song = parse_song(input_file)
    midi = build_midi(song)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{output_file.name}.", suffix=".tmp", dir=str(output_file.parent))
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(midi)
        os.chmod(tmp_name, 0o664)
        os.replace(tmp_name, output_file)
        os.chmod(output_file, 0o664)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: traXTrack.py <inputFile> <outputFile>", file=sys.stderr)
        return 2
    input_file = Path(argv[1])
    output_file = Path(argv[2])
    try:
        convert(input_file, output_file)
    except Exception as exc:
        if output_file.exists():
            output_file.unlink()
        print(f"traXTrack: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

#!/usr/bin/env python3
# Vibe coded by Codex
"""
Convert Creative Music System .CMS song files to WAV.
"""

from __future__ import annotations

import math
import json
import os
import struct
import sys
import wave
from array import array
from dataclasses import dataclass
from pathlib import Path

try:
    import numpy as np
except Exception:  # pragma: no cover - standard-library fallback is below.
    np = None


BLOCK_SIZE = 256
VOICE_COUNT = 12
SAMPLE_RATE = 22050
TEMPO_CONSTANT = 2_982_600.0

CTRL_LENGTHS = {
    0x01: 1,  # key signature
    0x02: 1,  # time signature
    0x03: 2,  # tempo timer divisor, big endian
    0x05: 1,  # volume
    0x06: 1,  # stereo mask
    0x07: 1,  # preset/instrument
    0x09: 1,  # P/Q articulation marker
}

MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]
OCTAVE_LETTERS = "ABCDEFGH"
NOTE_CHARS = set("01234567WXYwxy")
MOD_CHARS = set("/-.")
IGNORED_CHARS = set('| %^,;:"!$&\'()*<=>?[\\]`abcdefghijklmnopqrstuvxyz}~')


class CMSFormatError(ValueError):
    pass


@dataclass
class Voice:
    index: int
    start_block: int
    blocks: list[int]
    data: bytes


@dataclass
class Song:
    path: Path
    title: str
    composer: str
    message: str
    instruments: list[bytes]
    voices: list[Voice]


@dataclass
class RenderState:
    bpm: float = 120.0
    key: int = 0
    octave: int = 4
    preset: int = 1
    volume: int = 255
    stereo: int = 0xFF


@dataclass
class Event:
    voice: int
    start: float
    duration: float
    midi: int | None
    volume: float
    pan_l: float
    pan_r: float
    preset: int
    noise: bool


@dataclass
class BeatEvent:
    voice: int
    start_beat: float
    duration_beats: float
    note: str
    octave: int
    accidental: int
    volume: float
    pan_l: float
    pan_r: float
    preset: int
    noise: bool


@dataclass
class GlobalControl:
    beat: float
    kind: int
    value: int


def c_string(raw: bytes) -> str:
    raw = raw.split(b"\x00", 1)[0]
    return raw.decode("cp437", errors="replace").strip()


def parse_cms(path: Path) -> Song:
    data = path.read_bytes()
    if len(data) < 4 * BLOCK_SIZE or len(data) % BLOCK_SIZE != 0:
        raise CMSFormatError("file size is not a whole number of 256-byte CMS blocks")
    block_count = len(data) // BLOCK_SIZE
    if data[:2] != b"CM":
        raise CMSFormatError("missing CM signature")

    starts = list(data[2:14])
    if any(v and (v < 4 or v >= block_count) for v in starts):
        raise CMSFormatError("voice start block outside valid data range")
    nonzero_starts = [v for v in starts if v]
    if len(nonzero_starts) != len(set(nonzero_starts)):
        raise CMSFormatError("duplicate voice start block")

    if data[14:17] != b"\x00\x00\x00":
        raise CMSFormatError("reserved header bytes 0x0e..0x10 are not zero")
    if data[17:30] != b"\x01" + b"\x03" * 12:
        raise CMSFormatError("unknown channel-allocation header bytes")
    if data[0x80:0x83] != b"\x05\x19\x61":
        raise CMSFormatError("unknown header timing marker")

    header_mask = bytearray(BLOCK_SIZE)
    header_mask[0:30] = b"\xff" * 30
    header_mask[0x20:0x80] = b"\xff" * 0x60
    header_mask[0x80:0x83] = b"\xff" * 3
    for i, b in enumerate(data[:BLOCK_SIZE]):
        if not header_mask[i] and b:
            raise CMSFormatError(f"unexpected nonzero header byte at 0x{i:02x}")

    if any(data[BLOCK_SIZE:2 * BLOCK_SIZE]):
        raise CMSFormatError("reserved block 1 is not zero")
    if any(data[3 * BLOCK_SIZE:4 * BLOCK_SIZE]):
        raise CMSFormatError("reserved block 3 is not zero")

    instruments = [
        data[2 * BLOCK_SIZE + i * 8:2 * BLOCK_SIZE + (i + 1) * 8]
        for i in range(32)
    ]

    voices: list[Voice] = []
    owned: dict[int, int] = {}
    start_set = set(nonzero_starts)
    for voice_index, start in enumerate(starts, 1):
        if not start:
            continue
        blocks: list[int] = []
        payload = bytearray()
        block = start
        prev = 0
        seen: set[int] = set()
        while block:
            if block < 4 or block >= block_count:
                raise CMSFormatError(f"voice {voice_index} links outside file")
            if block in seen:
                raise CMSFormatError(f"voice {voice_index} has a block-link cycle")
            if block in owned:
                raise CMSFormatError(f"block {block} is shared by voices {owned[block]} and {voice_index}")
            chunk = data[block * BLOCK_SIZE:(block + 1) * BLOCK_SIZE]
            expected_back = 0 if prev == 0 or prev in start_set else prev
            if chunk[0] != expected_back:
                raise CMSFormatError(
                    f"block {block} has back-link {chunk[0]}, expected {expected_back}"
                )
            owned[block] = voice_index
            seen.add(block)
            blocks.append(block)
            payload.extend(chunk[1:255])
            prev = block
            block = chunk[255]
        validate_voice_payload(payload, voice_index)
        voices.append(Voice(voice_index, start, blocks, bytes(payload)))

    nonzero_blocks = {
        i for i in range(4, block_count)
        if any(data[i * BLOCK_SIZE:(i + 1) * BLOCK_SIZE])
    }
    if nonzero_blocks - set(owned):
        raise CMSFormatError(f"unowned nonzero data blocks: {sorted(nonzero_blocks - set(owned))[:8]}")

    return Song(
        path=path,
        title=c_string(data[0x20:0x40]),
        composer=c_string(data[0x40:0x60]),
        message=c_string(data[0x60:0x80]),
        instruments=instruments,
        voices=voices,
    )


def validate_voice_payload(payload: bytes, voice_index: int) -> None:
    i = 0
    while i < len(payload):
        b = payload[i]
        if b == 0:
            i += 1
            continue
        if b in CTRL_LENGTHS:
            needed = CTRL_LENGTHS[b]
            if i + needed >= len(payload):
                raise CMSFormatError(f"voice {voice_index} has truncated control 0x{b:02x}")
            i += 1 + needed
            continue
        if 32 <= b < 127:
            i += 1
            continue
        raise CMSFormatError(f"voice {voice_index} has unknown payload byte 0x{b:02x}")


def duration_from_mods(mods: str) -> float:
    if not mods:
        return 1.0
    if "-" in mods:
        return float(mods.count("-") + 1)
    dur = 1.0
    slashes = mods.count("/")
    if slashes:
        dur /= 2 ** slashes
    if "." in mods:
        dur *= 1.5
    return dur


def key_code_to_tonic(code: int) -> int:
    return (code - 5) % 12


def midi_for_note(note: str, octave: int, key: int, accidental: int) -> int | None:
    if note == "0" or note in "WXYwxy":
        return None
    degree = int(note) - 1
    semitone = key + MAJOR_SCALE[degree] + accidental
    return (octave + 1) * 12 + semitone


def parse_events(song: Song) -> list[Event]:
    beat_events: list[BeatEvent] = []
    global_controls: list[GlobalControl] = []
    for voice in song.voices:
        state = RenderState()
        beat = 0.0
        mods = ""
        pending_accidental: int | None = None
        bar_accidentals: dict[int, int] = {}
        triplet = False
        saw_group_note = False
        i = 0
        while i < len(voice.data):
            b = voice.data[i]
            i += 1
            if b == 0:
                continue
            if b in CTRL_LENGTHS:
                arg = voice.data[i:i + CTRL_LENGTHS[b]]
                i += CTRL_LENGTHS[b]
                if b == 0x01:
                    global_controls.append(GlobalControl(beat, b, key_code_to_tonic(arg[0])))
                elif b == 0x03:
                    divisor = (arg[0] << 8) | arg[1]
                    if divisor:
                        bpm = max(30.0, min(260.0, TEMPO_CONSTANT / divisor))
                        global_controls.append(GlobalControl(beat, b, int(round(bpm * 1000))))
                elif b == 0x05:
                    state.volume = arg[0]
                elif b == 0x06:
                    state.stereo = arg[0]
                elif b == 0x07:
                    state.preset = max(1, min(32, arg[0]))
                continue

            ch = chr(b)
            if ch == "|":
                mods = ""
                pending_accidental = None
                bar_accidentals.clear()
                triplet = False
                saw_group_note = False
                continue
            if ch == " ":
                mods = ""
                triplet = False
                saw_group_note = False
                continue
            if ch in MOD_CHARS:
                if saw_group_note:
                    mods = ""
                    saw_group_note = False
                mods += ch
                continue
            if ch == "T":
                triplet = True
                continue
            if ch == "#":
                pending_accidental = 1
                continue
            if ch == "@":
                pending_accidental = -1
                continue
            if ch == "~":
                pending_accidental = 0
                continue
            if ch == "+":
                state.octave = min(8, state.octave + 1)
                continue
            if ch == "_":
                state.octave = max(1, state.octave - 1)
                continue
            if ch in OCTAVE_LETTERS:
                state.octave = OCTAVE_LETTERS.index(ch) + 1
                continue
            if ch in NOTE_CHARS:
                beats = duration_from_mods(mods)
                if triplet:
                    beats *= 2.0 / 3.0
                noise = ch in "WXYwxy"
                vol = max(0.0, min(1.0, state.volume / 255.0))
                pan_l, pan_r = stereo_pan(state.stereo)
                effective_accidental = 0
                if ch in "1234567":
                    degree = int(ch)
                    if pending_accidental is not None:
                        bar_accidentals[degree] = pending_accidental
                    effective_accidental = bar_accidentals.get(degree, 0)
                if ch != "0" or noise:
                    beat_events.append(BeatEvent(
                        voice=voice.index,
                        start_beat=beat,
                        duration_beats=beats,
                        note=ch,
                        octave=state.octave,
                        accidental=effective_accidental,
                        volume=vol,
                        pan_l=pan_l,
                        pan_r=pan_r,
                        preset=state.preset,
                        noise=noise,
                    ))
                beat += beats
                saw_group_note = True
                pending_accidental = None
                continue
            if ch in IGNORED_CHARS:
                continue
            raise CMSFormatError(f"voice {voice.index} has unsupported notation character {ch!r}")
    return materialize_events(beat_events, global_controls)


def materialize_events(beat_events: list[BeatEvent], global_controls: list[GlobalControl]) -> list[Event]:
    key_timeline = build_global_timeline(global_controls, 0x01, 0)
    tempo_timeline = build_global_timeline(global_controls, 0x03, 120_000)
    events: list[Event] = []
    for event in beat_events:
        start = beat_to_seconds(event.start_beat, tempo_timeline)
        end = beat_to_seconds(event.start_beat + event.duration_beats, tempo_timeline)
        key = timeline_value_at(event.start_beat, key_timeline)
        events.append(Event(
            voice=event.voice,
            start=start,
            duration=end - start,
            midi=midi_for_note(event.note, event.octave, key, event.accidental),
            volume=event.volume,
            pan_l=event.pan_l,
            pan_r=event.pan_r,
            preset=event.preset,
            noise=event.noise,
        ))
    return events


def build_global_timeline(controls: list[GlobalControl], kind: int, default: int) -> list[tuple[float, int]]:
    timeline = [(0.0, default)]
    for control in sorted((c for c in controls if c.kind == kind), key=lambda c: c.beat):
        if control.beat == timeline[-1][0]:
            timeline[-1] = (control.beat, control.value)
        else:
            timeline.append((control.beat, control.value))
    return timeline


def timeline_value_at(beat: float, timeline: list[tuple[float, int]]) -> int:
    value = timeline[0][1]
    for change_beat, change_value in timeline[1:]:
        if change_beat > beat:
            break
        value = change_value
    return value


def beat_to_seconds(beat: float, tempo_timeline: list[tuple[float, int]]) -> float:
    seconds = 0.0
    prev_beat = tempo_timeline[0][0]
    bpm = tempo_timeline[0][1] / 1000.0
    for change_beat, change_tempo in tempo_timeline[1:]:
        if change_beat >= beat:
            break
        seconds += (change_beat - prev_beat) * 60.0 / bpm
        prev_beat = change_beat
        bpm = change_tempo / 1000.0
    seconds += (beat - prev_beat) * 60.0 / bpm
    return seconds


def stereo_pan(mask: int) -> tuple[float, float]:
    left = mask & 0x0F
    right = (mask >> 4) & 0x0F
    if not left and not right:
        return 0.7, 0.7
    return left / 15.0, right / 15.0


def midi_to_freq(midi: int) -> float:
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def synthesize(song: Song) -> bytes:
    if np is not None:
        return synthesize_numpy(song)
    return synthesize_stdlib(song)


def synthesize_numpy(song: Song) -> bytes:
    events = parse_events(song)
    total = max((e.start + e.duration for e in events), default=0.5) + 0.25
    frames = max(1, int(total * SAMPLE_RATE))
    left = np.zeros(frames, dtype=np.float32)
    right = np.zeros(frames, dtype=np.float32)

    for event in events:
        start = max(0, int(event.start * SAMPLE_RATE))
        end = min(frames, int((event.start + event.duration) * SAMPLE_RATE))
        if end <= start:
            continue
        n = end - start
        preset = song.instruments[event.preset - 1]
        base_amp = 0.075 * event.volume * instrument_gain(preset)
        attack = min(0.008, event.duration * 0.15)
        release = min(0.035, event.duration * 0.35)
        env = envelope_numpy(n, attack, max(release, 0.08 if event.noise else release))
        if event.noise:
            rng = np.random.default_rng((event.voice << 16) + start + event.preset)
            samples = rng.choice(np.array([-base_amp, base_amp], dtype=np.float32), size=n)
        else:
            freq = midi_to_freq(event.midi if event.midi is not None else 60)
            idx = np.arange(n, dtype=np.float32)
            phase = (idx * (freq / SAMPLE_RATE) + (event.voice * 0.173)) % 1.0
            samples = np.where(phase < 0.5, base_amp, -base_amp).astype(np.float32)
        samples *= env
        left[start:end] += samples * event.pan_l
        right[start:end] += samples * event.pan_r

    peak = float(max(0.01, np.max(np.abs(left)), np.max(np.abs(right))))
    scale = min(1.0, 0.92 / peak)
    interleaved = np.empty(frames * 2, dtype="<i2")
    interleaved[0::2] = np.clip(left * scale, -1.0, 1.0) * 32767
    interleaved[1::2] = np.clip(right * scale, -1.0, 1.0) * 32767
    return interleaved.tobytes()


def envelope_numpy(n: int, attack: float, release: float):
    idx = np.arange(n, dtype=np.float32) / SAMPLE_RATE
    env = np.ones(n, dtype=np.float32)
    if attack > 0:
        env = np.minimum(env, idx / attack)
    if release > 0:
        rem = (n - np.arange(n, dtype=np.float32)) / SAMPLE_RATE
        env = np.minimum(env, rem / release)
    return np.clip(env, 0.0, 1.0)


def synthesize_stdlib(song: Song) -> bytes:
    events = parse_events(song)
    total = max((e.start + e.duration for e in events), default=0.5) + 0.25
    frames = max(1, int(total * SAMPLE_RATE))
    left = array("f", [0.0]) * frames
    right = array("f", [0.0]) * frames

    for event in events:
        start = max(0, int(event.start * SAMPLE_RATE))
        end = min(frames, int((event.start + event.duration) * SAMPLE_RATE))
        if end <= start:
            continue
        preset = song.instruments[event.preset - 1]
        base_amp = 0.075 * event.volume * instrument_gain(preset)
        release = min(0.035, event.duration * 0.35)
        attack = min(0.008, event.duration * 0.15)
        if event.noise:
            add_noise(left, right, start, end, base_amp, event.pan_l, event.pan_r, attack, release, event.voice)
        else:
            freq = midi_to_freq(event.midi if event.midi is not None else 60)
            add_square(left, right, start, end, freq, base_amp, event.pan_l, event.pan_r, attack, release, event.voice)

    peak = 0.01
    for l, r in zip(left, right):
        peak = max(peak, abs(l), abs(r))
    scale = min(1.0, 0.92 / peak)
    out = bytearray()
    for l, r in zip(left, right):
        out += struct.pack("<hh", int(max(-1.0, min(1.0, l * scale)) * 32767),
                           int(max(-1.0, min(1.0, r * scale)) * 32767))
    return bytes(out)


def instrument_gain(preset: bytes) -> float:
    if not preset:
        return 1.0
    # The original table drives SAA1099 envelope/noise parameters.  For this
    # renderer, fold the nonzero shape bytes into a small loudness variation.
    weight = 0.85 + (sum(preset[:4]) % 48) / 160.0
    return max(0.65, min(1.15, weight))


def envelope(pos: int, start: int, end: int, attack: float, release: float) -> float:
    t = (pos - start) / SAMPLE_RATE
    rem = (end - pos) / SAMPLE_RATE
    a = 1.0 if attack <= 0 else min(1.0, t / attack)
    r = 1.0 if release <= 0 else min(1.0, rem / release)
    return min(a, r)


def add_square(left: array, right: array, start: int, end: int, freq: float, amp: float,
               pan_l: float, pan_r: float, attack: float, release: float, voice: int) -> None:
    phase = (voice * 0.173) % 1.0
    step = freq / SAMPLE_RATE
    for pos in range(start, end):
        phase += step
        phase -= int(phase)
        sample = amp if phase < 0.5 else -amp
        env = envelope(pos, start, end, attack, release)
        left[pos] += sample * env * pan_l
        right[pos] += sample * env * pan_r


def add_noise(left: array, right: array, start: int, end: int, amp: float,
              pan_l: float, pan_r: float, attack: float, release: float, seed: int) -> None:
    lfsr = 0xACE1 ^ (seed * 0x1021)
    for pos in range(start, end):
        bit = ((lfsr >> 0) ^ (lfsr >> 2) ^ (lfsr >> 3) ^ (lfsr >> 5)) & 1
        lfsr = (lfsr >> 1) | (bit << 15)
        sample = amp if (lfsr & 1) else -amp
        env = envelope(pos, start, end, attack, max(release, 0.08))
        left[pos] += sample * env * pan_l
        right[pos] += sample * env * pan_r


def output_name(input_path: Path, output_dir: Path) -> Path:
    return output_dir / f"{input_path.stem}.wav"


def write_wav(path: Path, pcm: bytes) -> None:
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(pcm)


def convert(input_file: Path, output_dir: Path) -> list[Path]:
    song = parse_cms(input_file)
    output_dir.mkdir(parents=True, exist_ok=True)
    wav_path = output_name(input_file, output_dir)
    pcm = synthesize(song)
    write_wav(wav_path, pcm)
    return [wav_path]


def main(argv: list[str]) -> int:
    if len(argv) == 3 and argv[1] == "--info":
        try:
            song = parse_cms(Path(argv[2]))
        except Exception:
            return 1
        print_metadata(song)
        return 0

    if len(argv) != 3:
        print("usage: cms.py [--info] <inputFile> <outputDir>", file=sys.stderr)
        return 2
    input_file = Path(argv[1])
    output_dir = Path(argv[2])
    before = set(output_dir.iterdir()) if output_dir.exists() else set()
    try:
        song = parse_cms(input_file)
        convert(input_file, output_dir)
    except Exception as exc:
        if output_dir.exists():
            for child in set(output_dir.iterdir()) - before:
                if child.is_file():
                    child.unlink()
        print(f"cms.py: {exc}", file=sys.stderr)
        return 1
    print_metadata(song)
    return 0


def print_metadata(song: Song) -> None:
    print(json.dumps({
        "title": song.title,
        "composer": song.composer,
        "message": song.message,
    }, ensure_ascii=False))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

#!/usr/bin/env python3
# Vibe coded by Codex
"""Render Music-X Performance IFF/MSCX files to mono 16-bit WAV."""

from __future__ import annotations

import argparse
import html
import math
import os
import struct
import sys
import tempfile
import wave
from array import array
from dataclasses import dataclass, field
from pathlib import Path


SAMPLE_RATE = 22050
NATIVE_PPQN = 192
TAIL_SECONDS = 0.6


class MusicXError(ValueError):
    pass


def u16(data: bytes, offset: int = 0) -> int:
    return int.from_bytes(data[offset : offset + 2], "big")


def u24(data: bytes, offset: int = 0) -> int:
    return int.from_bytes(data[offset : offset + 3], "big")


def u32(data: bytes, offset: int = 0) -> int:
    return int.from_bytes(data[offset : offset + 4], "big")


def latin1_clean(data: bytes) -> str:
    return data.split(b"\0", 1)[0].decode("latin-1", "replace").rstrip()


@dataclass
class Chunk:
    chunk_id: bytes
    offset: int
    declared_size: int
    actual_size: int
    payload: bytes


@dataclass
class Event:
    start: int
    status: int
    data1: int
    data2: int
    end: int
    release: int


@dataclass
class Sequence:
    name: str
    header: bytes
    events: list[Event]


@dataclass
class Sample8SVX:
    slot: int
    name: str
    one_shot_samples: int
    repeat_samples: int
    samples_per_cycle: int
    sample_rate: int
    octave: int
    compression: int
    volume: int
    attack: bytes
    release: bytes
    body: bytes


@dataclass
class MusicXPerformance:
    path: Path
    author: str = ""
    name: str = ""
    tempo: int = 120
    time_signature: tuple[int, int] = (4, 2)
    cues: tuple[int, ...] = ()
    sequences: list[Sequence] = field(default_factory=list)
    samples: dict[int, Sample8SVX] = field(default_factory=dict)
    chunks: list[Chunk] = field(default_factory=list)


KNOWN_CHUNKS = {
    b"AUTH",
    b"NAME",
    b"TSIG",
    b"TMPO",
    b"CUES",
    b"SEQU",
    b"OUTC",
    b"SYNC",
    b"TCDD",
    b"AUDI",
    b"MXFL",
    b"SWIT",
    b"FILT",
    b"SLOT",
    b"FORM",
    b"KMAP",
}


def parse_8svx(payload: bytes, slot: int) -> tuple[Sample8SVX, int]:
    if len(payload) < 4 or payload[:4] != b"8SVX":
        raise MusicXError("embedded FORM is not FORM 8SVX")

    pos = 4
    fields: dict[bytes, list[bytes]] = {}
    while pos + 8 <= len(payload):
        cid = payload[pos : pos + 4]
        size = u32(payload, pos + 4)
        end = pos + 8 + size
        padded_end = end + (size & 1)
        if padded_end > len(payload):
            break
        fields.setdefault(cid, []).append(payload[pos + 8 : end])
        pos = padded_end

    extra = len(payload) - pos
    if extra not in (0, 2):
        raise MusicXError(f"embedded 8SVX leaves {extra} unparsed bytes")
    if extra == 2 and payload[pos:pos + 2] != b"SL":
        raise MusicXError("embedded 8SVX size repair does not expose a SLOT chunk")

    required = {b"VHDR", b"NAME", b"ATAK", b"RLSE", b"BODY"}
    missing = required.difference(fields)
    if missing:
        names = ", ".join(x.decode("ascii") for x in sorted(missing))
        raise MusicXError(f"embedded 8SVX missing {names}")
    for cid, values in fields.items():
        if cid not in required or len(values) != 1:
            raise MusicXError(f"unsupported embedded 8SVX chunk layout for {cid!r}")

    vhdr = fields[b"VHDR"][0]
    if len(vhdr) != 20:
        raise MusicXError("8SVX VHDR must be 20 bytes")
    if len(fields[b"ATAK"][0]) % 6 or len(fields[b"RLSE"][0]) % 6:
        raise MusicXError("8SVX ATAK/RLSE envelope chunks must contain 6-byte points")
    compression = vhdr[15]
    if compression != 0:
        raise MusicXError("compressed 8SVX samples are not supported")

    return (
        Sample8SVX(
            slot=slot,
            name=latin1_clean(fields[b"NAME"][0]),
            one_shot_samples=u32(vhdr, 0),
            repeat_samples=u32(vhdr, 4),
            samples_per_cycle=u32(vhdr, 8),
            sample_rate=u16(vhdr, 12),
            octave=vhdr[14],
            compression=compression,
            volume=u32(vhdr, 16),
            attack=fields[b"ATAK"][0],
            release=fields[b"RLSE"][0],
            body=fields[b"BODY"][0],
        ),
        pos,
    )


def parse_sequence(payload: bytes) -> Sequence:
    if len(payload) < 50 or (len(payload) - 40) % 10:
        raise MusicXError("SEQU chunk size must be 40-byte header plus 10-byte records")
    header = payload[:40]
    name = latin1_clean(header[4:34])
    events = []
    for pos in range(40, len(payload), 10):
        rec = payload[pos : pos + 10]
        events.append(
            Event(
                start=u24(rec, 0),
                status=rec[3],
                data1=rec[4],
                data2=rec[5],
                end=u24(rec, 6),
                release=rec[9],
            )
        )
    return Sequence(name=name, header=header, events=events)


def validate_fixed_chunk(cid: bytes, payload: bytes) -> None:
    fixed_sizes = {
        b"TSIG": 4,
        b"TMPO": 4,
        b"CUES": 24,
        b"OUTC": 16,
        b"SYNC": 4,
        b"TCDD": 6,
        b"AUDI": 2,
        b"MXFL": 2,
        b"SWIT": 4,
        b"FILT": 18,
        b"SLOT": 4,
        b"KMAP": 388,
    }
    if cid in fixed_sizes and len(payload) != fixed_sizes[cid]:
        raise MusicXError(f"{cid.decode('ascii')} chunk must be {fixed_sizes[cid]} bytes")


def parse_musicx(path: Path) -> MusicXPerformance:
    data = path.read_bytes()
    if len(data) < 12 or data[:4] != b"FORM":
        raise MusicXError("not an IFF FORM file")
    form_size = u32(data, 4)
    if form_size + 8 != len(data):
        raise MusicXError("top-level FORM size does not match file length")
    if data[8:12] != b"MSCX":
        raise MusicXError("top-level FORM type is not MSCX")

    perf = MusicXPerformance(path=path)
    pos = 12
    current_slot = -1
    while pos < len(data):
        if pos + 8 > len(data):
            raise MusicXError("truncated top-level chunk header")
        cid = data[pos : pos + 4]
        size = u32(data, pos + 4)
        if cid not in KNOWN_CHUNKS:
            raise MusicXError(f"unsupported top-level chunk {cid!r}")
        if pos + 8 + size > len(data):
            raise MusicXError(f"{cid!r} chunk extends past end of file")

        payload = data[pos + 8 : pos + 8 + size]
        actual_size = size
        validate_fixed_chunk(cid, payload)

        if cid == b"AUTH":
            perf.author = latin1_clean(payload)
        elif cid == b"NAME":
            perf.name = latin1_clean(payload)
        elif cid == b"TSIG":
            perf.time_signature = (u16(payload, 0), u16(payload, 2))
        elif cid == b"TMPO":
            perf.tempo = u16(payload, 0)
            if payload[2:] != b"\0\0" or perf.tempo <= 0:
                raise MusicXError("TMPO chunk has unsupported payload")
        elif cid == b"CUES":
            perf.cues = tuple(u32(payload, i) for i in range(0, 24, 4))
        elif cid == b"SEQU":
            perf.sequences.append(parse_sequence(payload))
        elif cid == b"SLOT":
            current_slot = u32(payload, 0)
            if current_slot > 15:
                raise MusicXError("sample SLOT must be in range 0..15")
        elif cid == b"FORM":
            sample, natural_size = parse_8svx(payload, current_slot)
            if current_slot < 0:
                raise MusicXError("8SVX FORM appeared before a SLOT chunk")
            perf.samples[current_slot] = sample
            actual_size = natural_size

        perf.chunks.append(
            Chunk(
                chunk_id=cid,
                offset=pos,
                declared_size=size,
                actual_size=actual_size,
                payload=payload[:actual_size],
            )
        )

        if cid == b"FORM" and actual_size != size:
            pos = pos + 8 + actual_size
        else:
            pos = pos + 8 + size + (size & 1)

    return perf


def bar_ticks(time_signature: tuple[int, int]) -> int:
    numerator, denominator_code = time_signature
    denominator = 2 ** denominator_code
    ticks = numerator * NATIVE_PPQN * 4 // denominator
    if ticks <= 0:
        raise MusicXError("invalid time signature timing")
    return ticks


def unpack_time(raw_time: int, time_signature: tuple[int, int]) -> int:
    bar = raw_time >> 12
    clock = raw_time & 0x0FFF
    ticks_per_bar = bar_ticks(time_signature)
    return bar * ticks_per_bar + clock


def tick_to_sample(raw_time: int, tempo: int, time_signature: tuple[int, int]) -> int:
    tick = unpack_time(raw_time, time_signature)
    seconds = tick * 60.0 / (tempo * NATIVE_PPQN)
    return max(0, int(round(seconds * SAMPLE_RATE)))


def pan_gain(channel: int, pan: int) -> float:
    if channel == 9:
        return 0.9
    return 0.72 + 0.18 * math.sin((pan / 127.0) * math.pi)


def program_wave(program: int) -> str:
    if 24 <= program <= 31:
        return "pluck"
    if 32 <= program <= 39:
        return "bass"
    if 40 <= program <= 51:
        return "string"
    if 56 <= program <= 63:
        return "brass"
    if 64 <= program <= 79:
        return "reed"
    if 80 <= program <= 103:
        return "lead"
    return "piano"


def add(buf: array, index: int, value: float) -> None:
    if 0 <= index < len(buf):
        buf[index] += value


def render_tone(
    buf: array,
    start: int,
    end: int,
    note: int,
    velocity: int,
    program: int,
    channel: int,
    volume: int,
    pan: int,
) -> None:
    if end <= start:
        end = start + max(1, int(0.08 * SAMPLE_RATE))
    tail = int(0.04 * SAMPLE_RATE)
    stop = min(len(buf), end + tail)
    freq = 440.0 * (2.0 ** ((note - 69) / 12.0))
    amp = (velocity / 127.0) * (volume / 127.0) * 0.16 * pan_gain(channel, pan)
    wave = program_wave(program)
    duration = max(1, end - start)
    phase_step = 2.0 * math.pi * freq / SAMPLE_RATE
    phase = 0.0
    for i in range(start, stop):
        age = i - start
        if age < 0:
            continue
        if i < end:
            attack = min(1.0, age / max(1, int(0.012 * SAMPLE_RATE)))
            release = 1.0
            if wave in ("piano", "pluck"):
                release = math.exp(-2.5 * age / duration)
            env = attack * release
        else:
            env = max(0.0, 1.0 - (i - end) / max(1, tail)) * 0.25
        if wave == "bass":
            sample = math.sin(phase) * 0.85 + math.sin(phase * 0.5) * 0.25
        elif wave == "string":
            sample = math.sin(phase) + 0.35 * math.sin(phase * 2.0)
        elif wave == "brass":
            sample = math.tanh(1.8 * math.sin(phase)) + 0.18 * math.sin(phase * 3.0)
        elif wave == "reed":
            sample = 1.0 if math.sin(phase) >= 0 else -1.0
            sample *= 0.45
        elif wave == "lead":
            frac = (phase / (2.0 * math.pi)) % 1.0
            sample = (2.0 * frac - 1.0) * 0.7
        elif wave == "pluck":
            sample = math.sin(phase) + 0.5 * math.sin(phase * 2.01)
        else:
            sample = math.sin(phase) + 0.25 * math.sin(phase * 2.0)
        buf[i] += amp * env * sample
        phase += phase_step


def render_drum(buf: array, start: int, note: int, velocity: int, volume: int) -> None:
    length = int((0.10 if note in (35, 36, 38, 40) else 0.23) * SAMPLE_RATE)
    amp = (velocity / 127.0) * (volume / 127.0) * 0.35
    base = {35: 58.0, 36: 64.0, 38: 190.0, 40: 230.0, 41: 115.0, 43: 140.0}.get(note, 420.0)
    seed = (note * 1103515245 + start) & 0x7FFFFFFF
    for n in range(length):
        i = start + n
        if i >= len(buf):
            break
        env = math.exp(-5.0 * n / max(1, length))
        if note in (42, 44, 46, 49, 51, 52, 55, 57, 59):
            seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
            noise = ((seed >> 16) & 0x7FFF) / 16384.0 - 1.0
            value = noise * env * amp * (0.8 if note in (42, 44) else 0.55)
        elif note in (38, 39, 40):
            seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
            noise = ((seed >> 16) & 0x7FFF) / 16384.0 - 1.0
            value = (math.sin(2 * math.pi * base * n / SAMPLE_RATE) * 0.45 + noise * 0.55) * env * amp
        else:
            freq = base * (1.0 - 0.45 * n / max(1, length))
            value = math.sin(2 * math.pi * freq * n / SAMPLE_RATE) * env * amp
        buf[i] += value


def render_sample(
    buf: array,
    start: int,
    event: Event,
    sample: Sample8SVX,
    volume: int,
    tempo: int,
    time_signature: tuple[int, int],
) -> None:
    if not sample.body or sample.sample_rate <= 0:
        return
    pitch = 2.0 ** ((event.data1 - 60) / 12.0)
    step = (sample.sample_rate * pitch) / SAMPLE_RATE
    amp = (event.data2 / 127.0) * (volume / 127.0) * min(1.0, sample.volume / 65536.0) * 0.55
    pos = 0.0
    out = start
    max_end = tick_to_sample(max(event.end, event.start + 1), tempo, time_signature)
    target_end = max(
        start + int(0.04 * SAMPLE_RATE),
        start + max_end - tick_to_sample(event.start, tempo, time_signature),
    )
    while out < len(buf):
        idx = int(pos)
        if idx >= len(sample.body):
            break
        raw = sample.body[idx]
        if raw >= 128:
            raw -= 256
        env = 1.0
        if out > target_end:
            env = max(0.0, 1.0 - (out - target_end) / max(1, int(0.025 * SAMPLE_RATE)))
            if env <= 0.0:
                break
        buf[out] += (raw / 128.0) * amp * env
        pos += step
        out += 1


def render_performance(perf: MusicXPerformance) -> bytes:
    max_tick = 0
    note_events: list[tuple[Sequence, Event]] = []
    for seq in perf.sequences:
        for event in seq.events:
            if 0x90 <= event.status <= 0x9F and event.data2 > 0:
                note_events.append((seq, event))
                max_tick = max(max_tick, event.start, event.end)
    total_samples = tick_to_sample(max_tick, perf.tempo, perf.time_signature) + int(TAIL_SECONDS * SAMPLE_RATE) + 1
    if total_samples <= int(0.25 * SAMPLE_RATE):
        total_samples = int(0.25 * SAMPLE_RATE)
    buf = array("f", [0.0]) * total_samples

    programs = [0] * 16
    volumes = [100] * 16
    pans = [64] * 16

    all_events = [(seq, event) for seq in perf.sequences for event in seq.events]
    all_events.sort(key=lambda item: item[1].start)
    for seq, event in all_events:
        status = event.status
        channel = status & 0x0F
        command = status & 0xF0
        if command == 0xB0:
            if event.data1 == 7:
                volumes[channel] = event.data2
            elif event.data1 == 10:
                pans[channel] = event.data2
            elif event.data1 == 11:
                volumes[channel] = min(volumes[channel], event.data2)
        elif command == 0xC0:
            programs[channel] = event.data1
        elif command == 0x90 and event.data2 > 0:
            start = tick_to_sample(event.start, perf.tempo, perf.time_signature)
            end = tick_to_sample(event.end, perf.tempo, perf.time_signature)
            if end <= start:
                end = start + max(1, int((NATIVE_PPQN // 32) * 60.0 / perf.tempo / NATIVE_PPQN * SAMPLE_RATE))
            sample = None
            if seq.header[36] == 1 and channel in perf.samples:
                sample = perf.samples[channel]
            elif seq.header[36] == 1 and 0 in perf.samples and channel == 0:
                sample = perf.samples[0]
            if sample is not None:
                render_sample(buf, start, event, sample, volumes[channel], perf.tempo, perf.time_signature)
            elif channel == 9:
                render_drum(buf, start, event.data1, event.data2, volumes[channel])
            else:
                render_tone(
                    buf,
                    start,
                    end,
                    event.data1,
                    event.data2,
                    programs[channel],
                    channel,
                    volumes[channel],
                    pans[channel],
                )

    peak = max((abs(x) for x in buf), default=0.0)
    scale = 0.92 / peak if peak > 0.92 else 1.0
    pcm = bytearray()
    for value in buf:
        sample = int(max(-1.0, min(1.0, value * scale)) * 32767)
        pcm.extend(struct.pack("<h", sample))
    return bytes(pcm)


def output_path_for(input_path: Path, output_dir: Path) -> Path:
    if not input_path.is_absolute():
        rel = input_path
    else:
        try:
            rel = input_path.relative_to(Path.cwd())
        except ValueError:
            rel = Path(input_path.name)
    return output_dir / rel.with_name(rel.name + ".wav")


def write_wav_atomic(path: Path, pcm: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    os.close(fd)
    tmp_path = Path(tmp_name)
    try:
        with wave.open(str(tmp_path), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(SAMPLE_RATE)
            wav.writeframes(pcm)
        os.chmod(tmp_path, 0o664)
        tmp_path.replace(path)
        os.chmod(path, 0o664)
    except Exception:
        try:
            tmp_path.unlink()
        finally:
            raise


def convert(input_file: Path, output_dir: Path) -> Path:
    perf = parse_musicx(input_file)
    pcm = render_performance(perf)
    out_path = output_path_for(input_file, output_dir)
    write_wav_atomic(out_path, pcm)
    return out_path


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Convert a Music-X Performance IFF/MSCX file to WAV."
    )
    parser.add_argument("inputFile")
    parser.add_argument("outputDir")
    args = parser.parse_args(argv)

    input_file = Path(args.inputFile)
    output_dir = Path(args.outputDir)
    try:
        out_path = convert(input_file, output_dir)
    except MusicXError as exc:
        print(f"musicXPerformance: {exc}", file=sys.stderr)
        return 2
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

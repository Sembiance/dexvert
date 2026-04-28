#!/usr/bin/env python3
# Vibe coded by Codex
"""Convert classic ConcertWare score files to synthesized WAV audio."""

from __future__ import annotations

import math
import os
import re
import struct
import sys
import tempfile
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple


HEADER_SIZE = 0x38
SUPPORTED_VERSIONS = {b"1.00", b"2.00", b"4.01"}
SAMPLE_RATE = 22050
SECONDS_PER_TICK = 0.0225
MAX_RENDER_SECONDS = 15 * 60

TEXT_BYTES = set(range(32, 127)) | {9, 10, 13} | set(range(128, 256))
CONTROL_PART_SELECTORS = {0xF6, 0xF7}
CONTROL_LANE_SELECTORS = {0x18, 0x28, 0x38, 0x48, 0x58, 0x68}
CONTROL_NAMES = {
    0xF0: "v4-control-0",
    0xF1: "v4/control-1",
    0xF2: "v4-control-2",
    0xF3: "note-modifier",
    0xF4: "staff/layout-control-4",
    0xF5: "phrase/measure-control-5",
    0xF6: "part-control-6",
    0xF7: "part-control-7",
    0xF8: "playback/tempo",
    0xF9: "key/transposition",
    0xFA: "layout-control-a",
    0xFB: "layout-control-b",
    0xFC: "layout-control-c",
    0xFD: "layout-control-d",
    0xFE: "meter/beat",
    0xFF: "staff/layout-control-f",
}


class ConcertWareError(ValueError):
    """Raised when an input cannot be decoded as a supported ConcertWare file."""


@dataclass(frozen=True)
class MetadataString:
    offset: int
    raw: bytes

    @property
    def text(self) -> str:
        return self.raw.decode("mac_roman", errors="replace")


@dataclass(frozen=True)
class Header:
    version: str
    words32: Tuple[int, ...]
    words16: Tuple[int, ...]


@dataclass(frozen=True)
class NoteEvent:
    part: int
    start_tick: int
    duration_ticks: int
    pitch_code: int
    raw_duration: int
    raw_pitch: int


@dataclass(frozen=True)
class ControlEvent:
    offset: int
    opcode: int
    operand: int


@dataclass(frozen=True)
class ParsedFile:
    path: Path
    data: bytes
    header: Header
    metadata: Tuple[MetadataString, ...]
    score_offset: int
    prescore_blob: bytes
    controls: Tuple[ControlEvent, ...]
    notes: Tuple[NoteEvent, ...]
    unary_data: Tuple[Tuple[int, int], ...]
    part_lengths: Dict[int, int]
    tick_seconds: float


def _decode_duration(raw_duration: int) -> int:
    duration = raw_duration & 0x3F
    if duration == 0 and raw_duration != 0:
        return 64
    return duration


def _scan_controls(data: bytes, score_offset: int) -> Tuple[List[ControlEvent], int, set[int], List[int]]:
    controls: List[ControlEvent] = []
    f5_count = 0
    f6_parts: set[int] = set()
    ff_lanes: List[int] = []
    offset = score_offset
    while offset < len(data):
        byte = data[offset]
        if byte >= 0xF0:
            if offset + 1 >= len(data):
                raise ConcertWareError(f"control opcode at 0x{offset:x} has no operand")
            operand = data[offset + 1]
            controls.append(ControlEvent(offset=offset, opcode=byte, operand=operand))
            if byte == 0xF5:
                f5_count += 1
            elif byte in CONTROL_PART_SELECTORS and operand <= 0x0F:
                f6_parts.add(operand)
            elif byte == 0xFF and operand in CONTROL_LANE_SELECTORS:
                ff_lanes.append(operand)
            offset += 2
        elif offset + 1 < len(data) and data[offset + 1] < 0xF0:
            offset += 2
        else:
            offset += 1
    return controls, f5_count, f6_parts, ff_lanes


def _uses_dense_ff_lanes(data: bytes, score_offset: int) -> bool:
    controls, f5_count, f6_parts, ff_lanes = _scan_controls(data, score_offset)
    del controls
    if f5_count:
        return False
    return len(f6_parts) <= 1 and len(ff_lanes) >= 50 and len(set(ff_lanes)) >= 4


def _tempo_scale(controls: Sequence[ControlEvent]) -> float:
    first_f8 = next((control.operand for control in controls if control.opcode == 0xF8), None)
    if first_f8 is None:
        return 1.0

    if first_f8 == 0x24:
        return 2.0
    if first_f8 == 0x44:
        # 0x44 appears on the samples the previous renderer played much too
        # quickly. Interpreting it with the same inverse-delay curve anchored
        # at 0x24 puts it near the independently chosen Axel_F probe.
        return 2.0 * (256 - first_f8) / (256 - 0x24)
    return 1.0


def _scan_data_blocks(data: bytes, score_offset: int) -> List[Dict[str, object]]:
    blocks: List[Dict[str, object]] = []
    previous_controls: List[ControlEvent] = []
    offset = score_offset
    while offset < len(data):
        byte = data[offset]
        if byte >= 0xF0:
            if offset + 1 >= len(data):
                raise ConcertWareError(f"control opcode at 0x{offset:x} has no operand")
            previous_controls.append(ControlEvent(offset=offset, opcode=byte, operand=data[offset + 1]))
            offset += 2
            continue

        start = offset
        total_duration = 0
        note_count = 0
        event_count = 0
        while offset < len(data) and data[offset] < 0xF0:
            if offset + 1 < len(data) and data[offset + 1] < 0xF0:
                raw_duration = data[offset]
                raw_pitch = data[offset + 1]
                offset += 2
            else:
                raw_duration = data[offset]
                raw_pitch = 0
                offset += 1
            total_duration += _decode_duration(raw_duration)
            if raw_pitch & 0x3F:
                note_count += 1
            event_count += 1

        blocks.append(
            {
                "start": start,
                "end": offset,
                "duration": total_duration,
                "notes": note_count,
                "events": event_count,
                "previous_controls": tuple(previous_controls[-4:]),
            }
        )
    return blocks


def _layout_padding_blocks(data: bytes, score_offset: int) -> Dict[int, int]:
    blocks = _scan_data_blocks(data, score_offset)
    padding: Dict[int, int] = {}
    layout_controls = {0xFA, 0xFB, 0xFC}
    for index in range(1, len(blocks) - 1):
        previous_block = blocks[index - 1]
        block = blocks[index]
        next_block = blocks[index + 1]
        duration = int(block["duration"])
        previous_controls = block["previous_controls"]
        has_layout_control = any(control.opcode in layout_controls for control in previous_controls)
        if (
            has_layout_control
            and duration >= 96
            and int(block["events"]) >= 2
            and int(block["notes"]) == 0
            and int(previous_block["notes"]) > 0
            and int(next_block["notes"]) > 0
            and int(previous_block["duration"]) == duration
            and int(next_block["duration"]) == duration
        ):
            padding[int(block["start"])] = int(block["end"])
    return padding


def _uses_inline_layout_rests(
    data: bytes,
    score_offset: int,
    controls: Sequence[ControlEvent],
    layout_padding: Dict[int, int],
) -> bool:
    control_opcodes = {control.opcode for control in controls}
    if control_opcodes & {0xF4, 0xF5, 0xF6, 0xFF}:
        return False

    offset = score_offset
    total_ticks = 0
    filler_ticks = 0
    filler_count = 0
    while offset < len(data):
        padding_end = layout_padding.get(offset)
        if padding_end is not None:
            offset = padding_end
            continue

        byte = data[offset]
        if byte >= 0xF0:
            offset += 2
            continue

        if offset + 1 < len(data) and data[offset + 1] < 0xF0:
            raw_duration = data[offset]
            raw_pitch = data[offset + 1]
            duration = _decode_duration(raw_duration)
            total_ticks += duration
            if (raw_pitch & 0x3F) == 0 and raw_duration in {0x7C, 0x80}:
                filler_ticks += duration
                filler_count += 1
            offset += 2
            continue

        total_ticks += _decode_duration(byte)
        offset += 1

    return filler_count >= 20 and total_ticks > 0 and filler_ticks / total_ticks >= 0.25


def _is_text_payload(payload: bytes) -> bool:
    return all(byte in TEXT_BYTES for byte in payload)


def _decode_pascal_strings(data: bytes) -> Tuple[Tuple[MetadataString, ...], int]:
    offset = HEADER_SIZE
    strings: List[MetadataString] = []
    while offset < len(data):
        length = data[offset]
        end = offset + 1 + length
        if end > len(data):
            break
        payload = data[offset + 1 : end]
        if not _is_text_payload(payload):
            break
        strings.append(MetadataString(offset=offset, raw=payload))
        offset = end
    if not strings:
        raise ConcertWareError("no Pascal metadata strings found")
    return tuple(strings), offset


def _find_score_offset(version: bytes, data: bytes, metadata_end: int) -> Tuple[int, bytes]:
    if version != b"4.01":
        return metadata_end, b""

    # Version 4.01 samples carry a fixed-width settings block after metadata.
    # Its exact semantic fields are documented as unresolved, but every byte is
    # retained and the score begins at the first high-byte score control.
    for offset in range(metadata_end, len(data)):
        if data[offset] >= 0xF0:
            return offset, data[metadata_end:offset]
    raise ConcertWareError("version 4.01 file has no score bytecode")


def parse_file(path: Path) -> ParsedFile:
    data = path.read_bytes()
    if len(data) < HEADER_SIZE:
        raise ConcertWareError("file is shorter than the 56-byte header")
    version = data[:4]
    if version not in SUPPORTED_VERSIONS:
        raise ConcertWareError(f"unsupported ConcertWare version marker {version!r}")

    words32 = tuple(struct.unpack(">I", data[offset : offset + 4])[0] for offset in range(4, HEADER_SIZE, 4))
    words16 = tuple(struct.unpack(">H", data[offset : offset + 2])[0] for offset in range(4, HEADER_SIZE, 2))
    metadata, metadata_end = _decode_pascal_strings(data)
    score_offset, prescore_blob = _find_score_offset(version, data, metadata_end)
    if score_offset >= len(data):
        raise ConcertWareError("missing score bytecode")

    controls: List[ControlEvent] = []
    notes: List[NoteEvent] = []
    unary_data: List[Tuple[int, int]] = []
    part_lengths: Dict[int, int] = {0: 0}
    current_part = 0
    current_group = 0
    current_lane = 0
    use_ff_lanes = _uses_dense_ff_lanes(data, score_offset)
    layout_padding = _layout_padding_blocks(data, score_offset)
    use_inline_layout_rests = _uses_inline_layout_rests(data, score_offset, controls, layout_padding)
    offset = score_offset

    while offset < len(data):
        padding_end = layout_padding.get(offset)
        if padding_end is not None:
            offset = padding_end
            continue

        byte = data[offset]
        if byte >= 0xF0:
            if offset + 1 >= len(data):
                raise ConcertWareError(f"control opcode at 0x{offset:x} has no operand")
            operand = data[offset + 1]
            controls.append(ControlEvent(offset=offset, opcode=byte, operand=operand))
            if byte in CONTROL_PART_SELECTORS and operand <= 0x0F:
                current_group = operand
                current_part = (current_group << 8) | current_lane if use_ff_lanes else current_group
                part_lengths.setdefault(current_part, 0)
            elif use_ff_lanes and byte == 0xFF and operand in CONTROL_LANE_SELECTORS:
                current_lane = operand
                current_part = (current_group << 8) | current_lane
                part_lengths.setdefault(current_part, 0)
            offset += 2
            continue

        if offset + 1 < len(data) and data[offset + 1] < 0xF0:
            raw_duration = data[offset]
            raw_pitch = data[offset + 1]
            duration = _decode_duration(raw_duration)
            start = part_lengths.setdefault(current_part, 0)
            pitch = raw_pitch & 0x3F
            if pitch and duration:
                notes.append(
                    NoteEvent(
                        part=current_part,
                        start_tick=start,
                        duration_ticks=duration,
                        pitch_code=pitch,
                        raw_duration=raw_duration,
                        raw_pitch=raw_pitch,
                    )
                )
            if not (use_inline_layout_rests and not pitch and raw_duration in {0x7C, 0x80}):
                part_lengths[current_part] = start + duration
            offset += 2
            continue

        # A few samples contain single low bytes immediately before a control.
        # The playback engine treats these as standalone rest/delay bytes.
        raw_duration = data[offset]
        duration = _decode_duration(raw_duration)
        unary_data.append((offset, raw_duration))
        part_lengths[current_part] = part_lengths.setdefault(current_part, 0) + duration
        offset += 1

    if not notes:
        raise ConcertWareError("score contains no playable note events")

    return ParsedFile(
        path=path,
        data=data,
        header=Header(version=version.decode("ascii"), words32=words32, words16=words16),
        metadata=metadata,
        score_offset=score_offset,
        prescore_blob=prescore_blob,
        controls=tuple(controls),
        notes=tuple(notes),
        unary_data=tuple(unary_data),
        part_lengths=part_lengths,
        tick_seconds=SECONDS_PER_TICK * _tempo_scale(controls),
    )


def _pitch_to_midi(raw_pitch: int) -> int:
    # ConcertWare pitch codes behave like diatonic staff steps in these samples.
    # Code 0x18 maps to middle C; the top two bits act as accidental flags.
    pitch_code = raw_pitch & 0x3F
    diatonic = pitch_code - 0x18
    octave, degree = divmod(diatonic, 7)
    semitone = [0, 2, 4, 5, 7, 9, 11][degree]
    accidental = {0x40: 1, 0x80: -1, 0xC0: 0}.get(raw_pitch & 0xC0, 0)
    midi = 60 + octave * 12 + semitone + accidental
    return max(24, min(96, midi))


def _instrument_for_part(part: int) -> Tuple[float, float, float]:
    palette = [
        (0.55, 0.25, 0.08),
        (0.45, 0.15, 0.05),
        (0.50, 0.05, 0.20),
        (0.40, 0.35, 0.05),
        (0.48, 0.20, 0.14),
        (0.36, 0.28, 0.22),
        (0.42, 0.10, 0.28),
        (0.46, 0.18, 0.18),
    ]
    return palette[part % len(palette)]


def _add_note(buffer: List[float], event: NoteEvent, gain: float, tick_seconds: float) -> None:
    start = int(event.start_tick * tick_seconds * SAMPLE_RATE)
    duration = max(1, int(event.duration_ticks * tick_seconds * SAMPLE_RATE))
    midi = _pitch_to_midi(event.raw_pitch)
    frequency = 440.0 * (2.0 ** ((midi - 69) / 12.0))
    sine_gain, second_gain, third_gain = _instrument_for_part(event.part)
    phase_step = 2.0 * math.pi * frequency / SAMPLE_RATE
    release = max(1, min(duration // 3, int(0.025 * SAMPLE_RATE)))
    attack = max(1, min(duration // 5, int(0.008 * SAMPLE_RATE)))

    for index in range(duration):
        target = start + index
        if target >= len(buffer):
            break
        if index < attack:
            envelope = index / attack
        elif index > duration - release:
            envelope = max(0.0, (duration - index) / release)
        else:
            envelope = 1.0
        phase = phase_step * index
        sample = (
            sine_gain * math.sin(phase)
            + second_gain * math.sin(phase * 2.0 + 0.3)
            + third_gain * math.sin(phase * 3.0 + 0.8)
        )
        buffer[target] += sample * envelope * gain


def render_wav(parsed: ParsedFile, output_path: Path) -> None:
    max_ticks = max(parsed.part_lengths.values())
    total_seconds = max_ticks * parsed.tick_seconds + 1.0
    if total_seconds > MAX_RENDER_SECONDS:
        raise ConcertWareError(f"render would exceed {MAX_RENDER_SECONDS} seconds")
    total_samples = max(1, int(total_seconds * SAMPLE_RATE))
    mix = [0.0] * total_samples
    gain = min(0.18, 1.1 / max(1, math.sqrt(len(parsed.part_lengths))))

    for event in parsed.notes:
        _add_note(mix, event, gain, parsed.tick_seconds)

    peak = max((abs(value) for value in mix), default=0.0)
    scale = 0.92 / peak if peak > 0.92 else 1.0

    with wave.open(str(output_path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        frames = bytearray()
        for value in mix:
            sample = int(max(-1.0, min(1.0, value * scale)) * 32767)
            frames.extend(struct.pack("<h", sample))
        wav.writeframes(frames)


def output_name_for(input_path: Path) -> str:
    name = input_path.name.strip() or "concertware"
    name = re.sub(r"[^\w .,'&()+\\-]+", "_", name, flags=re.ASCII)
    name = name.strip(" .") or "concertware"
    return f"{name}.wav"


def convert(input_file: Path, output_dir: Path) -> Path:
    parsed = parse_file(input_file)
    output_dir.mkdir(parents=True, exist_ok=True)
    final_path = output_dir / output_name_for(input_file)
    fd, temp_name = tempfile.mkstemp(prefix=f".{final_path.name}.", suffix=".tmp", dir=str(output_dir))
    os.close(fd)
    temp_path = Path(temp_name)
    try:
        render_wav(parsed, temp_path)
        os.replace(temp_path, final_path)
        os.chmod(final_path, 0o644)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise
    return final_path


def describe(parsed: ParsedFile) -> str:
    title = parsed.metadata[0].text if parsed.metadata else parsed.path.name
    return (
        f"{parsed.path}: {parsed.header.version}, {len(parsed.metadata)} metadata strings, "
        f"score @ 0x{parsed.score_offset:x}, {len(parsed.controls)} controls, "
        f"{len(parsed.notes)} notes, {len(parsed.unary_data)} unary rests, title={title!r}"
    )


def main(argv: Sequence[str]) -> int:
    if len(argv) != 3:
        print("usage: concertWare.py <inputFile> <outputDir>", file=sys.stderr)
        return 2

    input_file = Path(argv[1])
    output_dir = Path(argv[2])
    try:
        output_path = convert(input_file, output_dir)
    except ConcertWareError as exc:
        print(f"concertWare.py: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"concertWare.py: {exc}", file=sys.stderr)
        return 1

    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

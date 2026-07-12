#!/usr/bin/env python3
# Vibe coded by Codex
"""Strict Mohawk WAVEData to RIFF/WAVE converter."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
from dataclasses import dataclass


SECTOR_SIZE = 2048
IMA_INDEX_ADJUST = (-1, -1, -1, -1, 2, 4, 6, 8)
IMA_STEP_TABLE = (
    7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 19, 21, 23, 25, 28, 31,
    34, 37, 41, 45, 50, 55, 60, 66, 73, 80, 88, 97, 107, 118,
    130, 143, 157, 173, 190, 209, 230, 253, 279, 307, 337, 371,
    408, 449, 494, 544, 598, 658, 724, 796, 876, 963, 1060, 1166,
    1282, 1411, 1552, 1707, 1878, 2066, 2272, 2499, 2749, 3024,
    3327, 3660, 4026, 4428, 4871, 5358, 5894, 6484, 7132, 7845,
    8630, 9493, 10442, 11487, 12635, 13899, 15289, 16818, 18500,
    20350, 22385, 24623, 27086, 29794, 32767,
)


class FormatError(Exception):
    """The input is not a supported, structurally valid Mohawk WAVEData file."""


@dataclass(frozen=True)
class CuePoint:
    sample_frame: int
    name: bytes


@dataclass(frozen=True)
class ADPCMChannelStatus:
    last_sample: int
    step_index: int


@dataclass(frozen=True)
class ADPCMStatusPoint:
    sample_frame: int
    channels: tuple[ADPCMChannelStatus, ...]


@dataclass(frozen=True)
class ADPCMStatusTable:
    channel_count: int
    points: tuple[ADPCMStatusPoint, ...]


@dataclass(frozen=True)
class MohawkAudio:
    sample_rate: int
    sample_count: int
    bits_per_sample: int
    channels: int
    encoding: int
    loop_count: int
    loop_start: int
    loop_end: int
    encoded_audio: bytes
    cues: tuple[CuePoint, ...]
    adpcm_status: ADPCMStatusTable | None


def _be16(data: bytes, offset: int) -> int:
    return struct.unpack_from(">H", data, offset)[0]


def _be32(data: bytes, offset: int) -> int:
    return struct.unpack_from(">I", data, offset)[0]


def _validate_physical_tail(data: bytes, logical_end: int) -> None:
    """Accept no tail or one of the exact extracted-resource tail forms."""
    if len(data) == logical_end:
        return
    if len(data) < logical_end:
        raise FormatError(
            f"truncated container: header ends at {logical_end}, file ends at {len(data)}"
        )
    if len(data) == logical_end + 1 and data[logical_end] == 0:
        return

    rounded_end = (logical_end + SECTOR_SIZE - 1) // SECTOR_SIZE * SECTOR_SIZE
    tail_size = len(data) - logical_end
    if (
        logical_end < SECTOR_SIZE
        or len(data) != rounded_end
        or tail_size <= 0
        or data[logical_end:] != data[logical_end - SECTOR_SIZE:logical_end - SECTOR_SIZE + tail_size]
    ):
        raise FormatError(
            f"{tail_size} unrecognized byte(s) follow the declared MHWK container"
        )


def _chunk_next(data: bytes, chunk_end: int, chunk_size: int, logical_end: int) -> int:
    if chunk_end > logical_end:
        raise FormatError("chunk extends past the declared MHWK container")
    if chunk_size & 1 and chunk_end < logical_end:
        if data[chunk_end] != 0:
            raise FormatError("odd-sized chunk has a nonzero alignment byte")
        return chunk_end + 1
    return chunk_end


def _parse_cues(payload: bytes) -> tuple[CuePoint, ...]:
    if len(payload) < 2:
        raise FormatError("Cue# chunk is shorter than its point-count field")
    point_count = _be16(payload, 0)
    offset = 2
    points: list[CuePoint] = []
    for index in range(point_count):
        if offset + 5 > len(payload):
            raise FormatError(f"Cue# point {index} is truncated")
        sample_frame = _be32(payload, offset)
        name_length = payload[offset + 4]
        offset += 5
        if offset + name_length > len(payload):
            raise FormatError(f"Cue# point {index} name is truncated")
        name = payload[offset:offset + name_length]
        offset += name_length
        if name_length % 2 == 0:
            if offset >= len(payload):
                raise FormatError(f"Cue# point {index} is missing its record alignment byte")
            if payload[offset] != 0:
                raise FormatError(f"Cue# point {index} has a nonzero record alignment byte")
            offset += 1
        points.append(CuePoint(sample_frame, name))
    if offset != len(payload):
        raise FormatError(f"Cue# chunk has {len(payload) - offset} unexplained trailing byte(s)")
    return tuple(points)


def _parse_adpcm_status(payload: bytes) -> ADPCMStatusTable:
    if len(payload) < 4:
        raise FormatError("ADPC chunk is shorter than its fixed header")
    item_count, channel_count = struct.unpack_from(">HH", payload, 0)
    if channel_count not in (1, 2):
        raise FormatError(f"ADPC channel count {channel_count} is not 1 or 2")
    expected_size = 4 + item_count * (4 + channel_count * 4)
    if len(payload) != expected_size:
        raise FormatError(
            f"ADPC size is {len(payload)}, expected exactly {expected_size} from its counts"
        )
    offset = 4
    points: list[ADPCMStatusPoint] = []
    previous_frame = -1
    for item_index in range(item_count):
        sample_frame = _be32(payload, offset)
        offset += 4
        if sample_frame <= previous_frame:
            raise FormatError("ADPC sample-frame entries are not strictly increasing")
        previous_frame = sample_frame
        statuses: list[ADPCMChannelStatus] = []
        for channel_index in range(channel_count):
            last_sample, step_index = struct.unpack_from(">hH", payload, offset)
            offset += 4
            if step_index >= len(IMA_STEP_TABLE):
                raise FormatError(
                    f"ADPC item {item_index}, channel {channel_index} has invalid step index {step_index}"
                )
            statuses.append(ADPCMChannelStatus(last_sample, step_index))
        points.append(ADPCMStatusPoint(sample_frame, tuple(statuses)))
    return ADPCMStatusTable(channel_count, tuple(points))


def _parse_data_chunk(payload: bytes) -> MohawkAudio:
    if len(payload) < 20:
        raise FormatError("Data chunk is shorter than its 20-byte header")
    (
        sample_rate,
        sample_count,
        bits_per_sample,
        channels,
        encoding,
        loop_count,
        loop_start,
        loop_end,
    ) = struct.unpack_from(">HIBBHHII", payload, 0)

    if sample_rate == 0:
        raise FormatError("sample rate is zero")
    if channels not in (1, 2):
        raise FormatError(f"channel count {channels} is not 1 or 2")
    if encoding not in (0, 1, 2):
        raise FormatError(f"unsupported Mohawk encoding {encoding}")
    if loop_count != 0 and not (loop_start < loop_end <= sample_count):
        raise FormatError(
            "active loop requires 0 <= loopStart < loopEnd <= sampleCount"
        )

    encoded_audio = payload[20:]
    if encoding == 0:
        if bits_per_sample not in (8, 16):
            raise FormatError(f"raw PCM depth {bits_per_sample} is not 8 or 16 bits")
        expected_size = sample_count * channels * (bits_per_sample // 8)
        if len(encoded_audio) == expected_size:
            pass
        elif (
            bits_per_sample == 8
            and channels == 1
            and len(encoded_audio) == expected_size + 1
            and encoded_audio[-1] == 0xC1
        ):
            encoded_audio = encoded_audio[:-1]
        else:
            raise FormatError(
                f"raw PCM payload is {len(encoded_audio)} bytes, expected {expected_size}"
            )
    elif encoding == 1:
        expected_nibbles = sample_count * channels
        if expected_nibbles % 2 or len(encoded_audio) * 2 != expected_nibbles:
            raise FormatError(
                "DVI IMA ADPCM payload length does not encode exactly sampleCount frames"
            )
    elif not encoded_audio:
        raise FormatError("MPEG Layer II payload is empty")

    return MohawkAudio(
        sample_rate,
        sample_count,
        bits_per_sample,
        channels,
        encoding,
        loop_count,
        loop_start,
        loop_end,
        encoded_audio,
        (),
        None,
    )


def parse_mohawk_wave(data: bytes) -> MohawkAudio:
    if len(data) < 12:
        raise FormatError("file is shorter than the 12-byte MHWK/WAVE header")
    if data[0:4] != b"MHWK":
        raise FormatError("missing MHWK signature at offset 0")
    container_size = _be32(data, 4)
    logical_end = 8 + container_size
    if logical_end < 12:
        raise FormatError("MHWK container size is too small to contain WAVE")
    if data[8:12] != b"WAVE":
        raise FormatError("missing WAVE form type at offset 8")
    _validate_physical_tail(data, logical_end)

    offset = 12
    cues: tuple[CuePoint, ...] | None = None
    adpcm_status: ADPCMStatusTable | None = None
    audio: MohawkAudio | None = None
    while offset < logical_end:
        if logical_end - offset < 8:
            raise FormatError(f"{logical_end - offset} trailing byte(s) cannot form a chunk header")
        tag = data[offset:offset + 4]
        chunk_size = _be32(data, offset + 4)
        payload_start = offset + 8
        chunk_end = payload_start + chunk_size
        if chunk_end > logical_end:
            raise FormatError(f"{tag!r} chunk extends past the declared MHWK container")
        payload = data[payload_start:chunk_end]
        next_offset = _chunk_next(data, chunk_end, chunk_size, logical_end)

        if tag == b"Cue#":
            if cues is not None:
                raise FormatError("duplicate Cue# chunk")
            if audio is not None:
                raise FormatError("Cue# chunk occurs after Data")
            cues = _parse_cues(payload)
        elif tag == b"ADPC":
            if adpcm_status is not None:
                raise FormatError("duplicate ADPC chunk")
            if audio is not None:
                raise FormatError("ADPC chunk occurs after Data")
            adpcm_status = _parse_adpcm_status(payload)
        elif tag == b"Data":
            if audio is not None:
                raise FormatError("duplicate Data chunk")
            audio = _parse_data_chunk(payload)
            if next_offset != logical_end:
                raise FormatError("Data must be the final chunk in a Mohawk WAVE form")
        else:
            printable = tag.decode("ascii", "backslashreplace")
            raise FormatError(f"unknown Mohawk WAVE chunk {printable!r}")
        offset = next_offset

    if offset != logical_end:
        raise FormatError("chunk layout does not end at the declared MHWK boundary")
    if audio is None:
        raise FormatError("MHWK/WAVE container has no Data chunk")

    final_cues = cues or ()
    for cue_index, cue in enumerate(final_cues):
        if cue.sample_frame > audio.sample_count:
            raise FormatError(
                f"Cue# point {cue_index} lies beyond sampleCount ({cue.sample_frame} > {audio.sample_count})"
            )
    if adpcm_status is not None:
        if audio.encoding != 1:
            raise FormatError("ADPC status table is present for non-ADPCM audio")
        if adpcm_status.channel_count != audio.channels:
            raise FormatError("ADPC and Data channel counts disagree")
        for point in adpcm_status.points:
            if point.sample_frame > audio.sample_count:
                raise FormatError("ADPC status entry lies beyond sampleCount")

    return MohawkAudio(
        audio.sample_rate,
        audio.sample_count,
        audio.bits_per_sample,
        audio.channels,
        audio.encoding,
        audio.loop_count,
        audio.loop_start,
        audio.loop_end,
        audio.encoded_audio,
        final_cues,
        adpcm_status,
    )


def _decode_ima_nibble(code: int, last: int, step_index: int) -> tuple[int, int]:
    step = IMA_STEP_TABLE[step_index]
    difference = ((2 * (code & 7) + 1) * step) >> 3
    if code & 8:
        last -= difference
    else:
        last += difference
    last = max(-32768, min(32767, last))
    step_index += IMA_INDEX_ADJUST[code & 7]
    step_index = max(0, min(88, step_index))
    return last, step_index


def _decode_dvi_ima(audio: MohawkAudio) -> bytes:
    last = [0] * audio.channels
    step_index = [0] * audio.channels
    output = bytearray(audio.sample_count * audio.channels * 2)
    output_offset = 0
    for value in audio.encoded_audio:
        for nibble_number, code in enumerate((value >> 4, value & 0x0F)):
            channel = nibble_number if audio.channels == 2 else 0
            sample, index = _decode_ima_nibble(code, last[channel], step_index[channel])
            last[channel] = sample
            step_index[channel] = index
            struct.pack_into("<h", output, output_offset, sample)
            output_offset += 2
    return bytes(output)


MPEG1_LAYER2_BITRATES = (0, 32, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 384)
MPEG2_LAYER2_BITRATES = (0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160)


def _mpeg_layer2_header(audio: MohawkAudio, offset: int) -> tuple[int, int, int]:
    payload = audio.encoded_audio
    if len(payload) - offset < 4:
        raise FormatError("truncated MPEG Layer II frame header")
    header = _be32(payload, offset)
    if header >> 21 != 0x7FF:
        raise FormatError(f"MPEG Layer II sync is absent at payload offset {offset}")
    version_id = (header >> 19) & 3
    layer = (header >> 17) & 3
    bitrate_index = (header >> 12) & 0xF
    rate_index = (header >> 10) & 3
    padding = (header >> 9) & 1
    channel_mode = (header >> 6) & 3
    emphasis = header & 3
    if version_id == 1 or layer != 2:
        raise FormatError("compressed Data payload is not MPEG Audio Layer II")
    if bitrate_index == 15:
        raise FormatError("MPEG Layer II frame uses the reserved bitrate index")
    if rate_index == 3 or emphasis == 2:
        raise FormatError("MPEG Layer II frame uses a reserved header value")

    base_rates = (44100, 48000, 32000)
    divisor = 1 if version_id == 3 else (2 if version_id == 2 else 4)
    frame_rate = base_rates[rate_index] // divisor
    frame_channels = 1 if channel_mode == 3 else 2
    if frame_rate != audio.sample_rate:
        raise FormatError(
            f"MPEG frame rate {frame_rate} disagrees with Data rate {audio.sample_rate}"
        )
    if frame_channels != audio.channels:
        raise FormatError("MPEG frame channel mode disagrees with Data channel count")
    return version_id, bitrate_index, padding


def _validate_free_mpeg_layer2(audio: MohawkAudio, version_id: int, first_padding: int) -> None:
    """Find the unique free-format frame length that partitions the whole payload."""
    payload = audio.encoded_audio
    candidates = {len(payload) - first_padding}
    for possible_header in range(4, len(payload) - 3):
        try:
            candidate_version, candidate_bitrate, _ = _mpeg_layer2_header(audio, possible_header)
        except FormatError:
            continue
        if candidate_version == version_id and candidate_bitrate == 0:
            candidates.add(possible_header - first_padding)

    valid_lengths: list[int] = []
    for base_size in candidates:
        if base_size < 4:
            continue
        offset = 0
        frame_count = 0
        try:
            while offset < len(payload):
                frame_version, bitrate_index, padding = _mpeg_layer2_header(audio, offset)
                if frame_version != version_id or bitrate_index != 0:
                    raise FormatError("mixed free and table bitrate MPEG frames")
                frame_size = base_size + padding
                if offset + frame_size > len(payload):
                    raise FormatError("truncated free-bitrate MPEG Layer II frame")
                offset += frame_size
                frame_count += 1
        except FormatError:
            continue
        if offset == len(payload) and frame_count * 1152 == audio.sample_count:
            valid_lengths.append(base_size)
    if len(valid_lengths) != 1:
        if not valid_lengths:
            raise FormatError("free-bitrate MPEG Layer II frames do not exactly partition the payload")
        raise FormatError("free-bitrate MPEG Layer II frame size is structurally ambiguous")


def _validate_mpeg_layer2(audio: MohawkAudio) -> None:
    payload = audio.encoded_audio
    first_version, first_bitrate, first_padding = _mpeg_layer2_header(audio, 0)
    if first_bitrate == 0:
        _validate_free_mpeg_layer2(audio, first_version, first_padding)
        return

    offset = 0
    frame_count = 0
    while offset < len(payload):
        version_id, bitrate_index, padding = _mpeg_layer2_header(audio, offset)
        if bitrate_index == 0:
            raise FormatError("MPEG Layer II stream mixes table and free bitrate frames")
        rate_index = (_be32(payload, offset) >> 10) & 3
        base_rates = (44100, 48000, 32000)
        divisor = 1 if version_id == 3 else (2 if version_id == 2 else 4)
        frame_rate = base_rates[rate_index] // divisor
        bitrates = MPEG1_LAYER2_BITRATES if version_id == 3 else MPEG2_LAYER2_BITRATES
        bitrate = bitrates[bitrate_index]
        frame_size = (144000 * bitrate) // frame_rate + padding
        if offset + frame_size > len(payload):
            raise FormatError("truncated MPEG Layer II frame")
        offset += frame_size
        frame_count += 1

    expected_samples = frame_count * 1152
    if expected_samples != audio.sample_count:
        raise FormatError(
            f"MPEG frames decode to {expected_samples} samples, Data declares {audio.sample_count}"
        )


def _decode_mpeg_layer2(audio: MohawkAudio) -> bytes:
    _validate_mpeg_layer2(audio)
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise FormatError("MPEG Layer II input requires ffmpeg in PATH")
    command = (
        ffmpeg,
        "-v", "error",
        "-xerror",
        "-err_detect", "explode",
        "-f", "mp3",
        "-i", "pipe:0",
        "-map", "0:a:0",
        "-c:a", "pcm_s16le",
        "-f", "s16le",
        "pipe:1",
    )
    result = subprocess.run(command, input=audio.encoded_audio, capture_output=True, check=False)
    if result.returncode != 0:
        reason = result.stderr.decode("utf-8", "replace").strip().splitlines()
        detail = reason[-1] if reason else f"exit status {result.returncode}"
        raise FormatError(f"ffmpeg rejected MPEG Layer II payload: {detail}")
    expected_size = audio.sample_count * audio.channels * 2
    if len(result.stdout) != expected_size:
        raise FormatError(
            f"MPEG decoder produced {len(result.stdout)} PCM bytes, expected {expected_size}"
        )
    return result.stdout


def decode_audio(audio: MohawkAudio) -> tuple[bytes, int]:
    if audio.encoding == 0:
        if audio.bits_per_sample == 8:
            return audio.encoded_audio, 8
        source = audio.encoded_audio
        swapped = bytearray(len(source))
        swapped[0::2] = source[1::2]
        swapped[1::2] = source[0::2]
        return bytes(swapped), 16
    if audio.encoding == 1:
        return _decode_dvi_ima(audio), 16
    return _decode_mpeg_layer2(audio), 16


def _riff_chunk(tag: bytes, payload: bytes) -> bytes:
    if len(tag) != 4:
        raise ValueError("RIFF chunk tag must be four bytes")
    return tag + struct.pack("<I", len(payload)) + payload + (b"\x00" if len(payload) & 1 else b"")


def _cue_chunks(cues: tuple[CuePoint, ...]) -> list[bytes]:
    if not cues:
        return []
    cue_payload = bytearray(struct.pack("<I", len(cues)))
    adtl_payload = bytearray(b"adtl")
    for index, cue in enumerate(cues, start=1):
        cue_payload.extend(
            struct.pack("<II4sIII", index, cue.sample_frame, b"data", 0, 0, cue.sample_frame)
        )
        label_payload = struct.pack("<I", index) + cue.name + b"\x00"
        adtl_payload.extend(_riff_chunk(b"labl", label_payload))
    return [_riff_chunk(b"cue ", bytes(cue_payload)), _riff_chunk(b"LIST", bytes(adtl_payload))]


def _loop_chunk(audio: MohawkAudio) -> bytes | None:
    if audio.loop_count == 0:
        return None
    play_count = 0 if audio.loop_count == 0xFFFF else audio.loop_count
    sample_period = (1_000_000_000 + audio.sample_rate // 2) // audio.sample_rate
    header = struct.pack(
        "<9I", 0, 0, sample_period, 60, 0, 0, 0, 1, 0
    )
    loop = struct.pack(
        "<6I", 0, 0, audio.loop_start, audio.loop_end - 1, 0, play_count
    )
    return _riff_chunk(b"smpl", header + loop)


def build_wave(audio: MohawkAudio, pcm: bytes, output_bits: int) -> bytes:
    block_align = audio.channels * (output_bits // 8)
    expected_size = audio.sample_count * block_align
    if len(pcm) != expected_size:
        raise FormatError(f"internal PCM size mismatch: {len(pcm)} != {expected_size}")
    fmt_payload = struct.pack(
        "<HHIIHH",
        1,
        audio.channels,
        audio.sample_rate,
        audio.sample_rate * block_align,
        block_align,
        output_bits,
    )
    chunks = [_riff_chunk(b"fmt ", fmt_payload)]
    chunks.extend(_cue_chunks(audio.cues))
    loop_chunk = _loop_chunk(audio)
    if loop_chunk is not None:
        chunks.append(loop_chunk)
    chunks.append(_riff_chunk(b"data", pcm))
    body = b"WAVE" + b"".join(chunks)
    if len(body) > 0xFFFFFFFF:
        raise FormatError("decoded audio is too large for classic RIFF/WAVE")
    return b"RIFF" + struct.pack("<I", len(body)) + body


def _write_atomic(path: Path, contents: bytes) -> None:
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", prefix=f".{path.name}.", suffix=".tmp", dir=path.parent, delete=False
        ) as temporary:
            temporary_name = temporary.name
            temporary.write(contents)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.chmod(temporary_name, 0o664)
        os.replace(temporary_name, path)
        temporary_name = None
    finally:
        if temporary_name is not None:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass


def convert(input_path: Path, output_directory: Path) -> Path:
    try:
        data = input_path.read_bytes()
    except OSError as error:
        raise FormatError(f"cannot read input: {error}") from error
    audio = parse_mohawk_wave(data)
    pcm, output_bits = decode_audio(audio)
    wave_file = build_wave(audio, pcm, output_bits)

    output_path = output_directory / f"{input_path.name}.wav"
    if output_directory.exists() and not output_directory.is_dir():
        raise FormatError(f"output path is not a directory: {output_directory}")
    if output_path.exists() and output_path.is_dir():
        raise FormatError(f"output file path is a directory: {output_path}")
    try:
        output_directory.mkdir(parents=True, exist_ok=True, mode=0o775)
        _write_atomic(output_path, wave_file)
    except OSError as error:
        raise FormatError(f"cannot write output: {error}") from error
    return output_path


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mohawkWAVE.py",
        description="Convert one strict Mohawk MHWK/WAVEData resource to RIFF/WAVE.",
    )
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputDir", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = _argument_parser().parse_args(argv)
    try:
        output_path = convert(arguments.inputFile, arguments.outputDir)
    except FormatError as error:
        print(f"mohawkWAVE.py: error: {error}", file=sys.stderr)
        return 2
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

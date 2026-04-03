#!/usr/bin/env python3
# Vibe coded by Claude
#
# stosSample.py - Convert STOS BASIC sample files to WAV
#
# Usage: stosSample.py <inputFile> <outputDir>
#
# STOS sample format:
#   Offset 0-2: "JON" magic (0x4A 0x4F 0x4E)
#   Offset 3:   Sample rate in kHz (1-255, typical range 5-32)
#   Offset 4+:  Raw unsigned 8-bit PCM audio data
#
# Files may contain multiple sub-samples, each preceded by a JON header.
# Sample rate = rate_byte * 1000 Hz

import sys
import os
import struct

MAX_RATE_BYTE = 40  # rate bytes above this are coincidental audio data


def validate_stos_file(data):
    """Check that data starts with JON and has a valid rate byte. Raises ValueError if not."""
    if len(data) < 5:
        raise ValueError(f"File too small ({len(data)} bytes, need at least 5)")

    if data[:3] != b"JON":
        raise ValueError(f"Invalid magic: expected 'JON' (4A4F4E), got {data[:3].hex().upper()}")

    freq_byte = data[3]
    if freq_byte == 0:
        raise ValueError("Rate byte is 0 (invalid sample rate)")

    if freq_byte >= 0x41:
        raise ValueError(
            f"Byte 3 is 0x{freq_byte:02X} ('{chr(freq_byte)}'), looks like ASCII text, "
            f"not a STOS sample rate"
        )

    audio_data = data[4:]
    avg = sum(audio_data) / len(audio_data)
    if avg < 80 or avg > 170:
        raise ValueError(
            f"Data average {avg:.1f} is far from unsigned 8-bit center (128). "
            f"This is not a STOS sample file."
        )

    null_ratio = sum(1 for b in audio_data[:1000] if b == 0) / min(len(audio_data), 1000)
    if null_ratio > 0.5:
        raise ValueError(
            f"Data is {null_ratio*100:.0f}% null bytes in first 1000 bytes. "
            f"This is not a STOS sample file."
        )


def find_sub_samples(data):
    """Find all sub-sample boundaries in a STOS sample file.
    Returns list of (rate_byte, audio_start, audio_end) tuples."""
    # Find all JON headers with plausible rate bytes
    jon_positions = []
    i = 0
    while True:
        pos = data.find(b"JON", i)
        if pos == -1 or pos + 3 >= len(data):
            break
        rate = data[pos + 3]
        if 1 <= rate <= MAX_RATE_BYTE:
            jon_positions.append((pos, rate))
        i = pos + 1

    if not jon_positions:
        return []

    # Build sub-samples: each runs from JON+4 to next JON or EOF
    samples = []
    for i, (pos, rate) in enumerate(jon_positions):
        audio_start = pos + 4
        audio_end = jon_positions[i + 1][0] if i + 1 < len(jon_positions) else len(data)
        audio_len = audio_end - audio_start

        # Skip empty or tiny segments (< 100 bytes)
        if audio_len < 100:
            continue

        # Skip segments that don't look like audio
        segment = data[audio_start:min(audio_start + 1000, audio_end)]
        avg = sum(segment) / len(segment)
        if avg < 80 or avg > 170:
            continue

        samples.append((rate, audio_start, audio_end))

    return samples


def write_wav(filepath, sample_rate, audio_data):
    """Write unsigned 8-bit mono PCM WAV file."""
    num_channels = 1
    bits_per_sample = 8
    byte_rate = sample_rate * num_channels
    block_align = num_channels
    data_size = len(audio_data)
    riff_size = 4 + 24 + 8 + data_size

    with open(filepath, "wb") as f:
        f.write(b"RIFF")
        f.write(struct.pack("<I", riff_size))
        f.write(b"WAVE")
        f.write(b"fmt ")
        f.write(struct.pack("<I", 16))
        f.write(struct.pack("<H", 1))
        f.write(struct.pack("<H", num_channels))
        f.write(struct.pack("<I", sample_rate))
        f.write(struct.pack("<I", byte_rate))
        f.write(struct.pack("<H", block_align))
        f.write(struct.pack("<H", bits_per_sample))
        f.write(b"data")
        f.write(struct.pack("<I", data_size))
        f.write(audio_data)


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(input_file):
        print(f"Error: Input file not found: {input_file}", file=sys.stderr)
        sys.exit(1)

    with open(input_file, "rb") as f:
        data = f.read()

    try:
        validate_stos_file(data)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    basename = os.path.splitext(os.path.basename(input_file))[0]
    if not basename:
        basename = os.path.basename(input_file)

    samples = find_sub_samples(data)

    if not samples:
        print(f"Error: No valid audio segments found in {input_file}", file=sys.stderr)
        sys.exit(1)

    for i, (rate_byte, audio_start, audio_end) in enumerate(samples):
        audio_data = data[audio_start:audio_end]
        sample_rate = rate_byte * 1000
        duration = len(audio_data) / sample_rate

        if len(samples) == 1:
            wav_name = basename + ".wav"
        else:
            wav_name = f"{i+1}.wav"

        wav_path = os.path.join(output_dir, wav_name)
        write_wav(wav_path, sample_rate, audio_data)

        print(f"Input:       {input_file}")
        print(f"  Sample {i+1}/{len(samples)}: offset={audio_start}, "
              f"rate={sample_rate}Hz, {len(audio_data)} bytes, {duration:.3f}s")
        print(f"  Output:    {wav_path}")


if __name__ == "__main__":
    main()

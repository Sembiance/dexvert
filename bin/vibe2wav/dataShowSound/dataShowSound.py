#!/usr/bin/env python3
# Vibe coded by Claude
#
# DataShow .SND to WAV converter
# Converts DataShow presentation sound files (PC speaker tone sequences)
# into standard WAV audio files.
#
# Usage: dataShowSound.py <inputFile> <outputDir>

import sys
import os
import struct
import math

SAMPLE_RATE = 44100
AMPLITUDE = 24000  # 16-bit signed amplitude for square wave


def parse_snd_file(filepath):
    """Parse a DataShow .SND file and return (header_info, notes).

    header_info is a dict with keys: version, filename, raw_header
    notes is a list of (frequency_hz, duration_ms) tuples.
    """
    with open(filepath, "rb") as f:
        raw = f.read()

    # Strip optional trailing DOS EOF marker (0x1A)
    if raw and raw[-1] == 0x1A:
        raw = raw[:-1]

    # Decode as ASCII text with CRLF line endings
    text = raw.decode("ascii")
    lines = text.split("\r\n")

    # Remove trailing empty line from final CRLF
    if lines and lines[-1] == "":
        lines.pop()

    if not lines:
        print(f"Error: empty file {filepath}", file=sys.stderr)
        sys.exit(1)

    # Parse header line: ;DataShow [<version> ]music file: <filename>
    header_line = lines[0]
    if not header_line.startswith(";DataShow"):
        print(f"Error: invalid header in {filepath}: {header_line!r}", file=sys.stderr)
        sys.exit(1)

    # Extract version and filename from header
    rest = header_line[len(";DataShow"):]  # after ";DataShow"
    music_idx = rest.find("music file: ")
    if music_idx == -1:
        print(f"Error: cannot parse header in {filepath}: {header_line!r}", file=sys.stderr)
        sys.exit(1)

    version_part = rest[:music_idx].strip()  # version string or empty
    original_filename = rest[music_idx + len("music file: "):]

    header_info = {
        "version": version_part if version_part else None,
        "filename": original_filename,
        "raw_header": header_line,
    }

    # Parse note lines
    notes = []
    for i, line in enumerate(lines[1:], start=2):
        line = line.strip()
        if not line:
            continue

        # Expected format: "Freq: <freq>   Dur: <dur>"
        if not line.startswith("Freq:"):
            print(f"Error: unexpected line {i} in {filepath}: {line!r}", file=sys.stderr)
            sys.exit(1)

        # Split on "Dur:"
        parts = line.split("Dur:")
        if len(parts) != 2:
            print(f"Error: cannot parse line {i} in {filepath}: {line!r}", file=sys.stderr)
            sys.exit(1)

        freq_part = parts[0]  # "Freq:    494   "
        dur_part = parts[1]   # " 400"

        freq_str = freq_part[len("Freq:"):].strip()
        dur_str = dur_part.strip()

        try:
            freq = int(freq_str)
            dur = int(dur_str)
        except ValueError:
            print(f"Error: invalid values on line {i} in {filepath}: {line!r}", file=sys.stderr)
            sys.exit(1)

        notes.append((freq, dur))

    return header_info, notes


def generate_square_wave(frequency, duration_ms, sample_rate=SAMPLE_RATE):
    """Generate 16-bit signed PCM samples for a square wave tone.

    frequency: tone frequency in Hz (0 = silence)
    duration_ms: duration in milliseconds
    Returns a list of 16-bit signed integer samples.
    """
    num_samples = int(sample_rate * duration_ms / 1000)
    samples = []

    if frequency == 0:
        # Silence
        samples = [0] * num_samples
    else:
        period = sample_rate / frequency
        for i in range(num_samples):
            # Square wave: positive for first half of period, negative for second half
            pos_in_period = (i % period) / period
            if pos_in_period < 0.5:
                samples.append(AMPLITUDE)
            else:
                samples.append(-AMPLITUDE)

    return samples


def write_wav(filepath, samples, sample_rate=SAMPLE_RATE):
    """Write 16-bit mono PCM WAV file."""
    num_samples = len(samples)
    data_size = num_samples * 2  # 16-bit = 2 bytes per sample
    file_size = 36 + data_size   # RIFF header (44 bytes) - 8 + data

    with open(filepath, "wb") as f:
        # RIFF header
        f.write(b"RIFF")
        f.write(struct.pack("<I", file_size))
        f.write(b"WAVE")

        # fmt chunk
        f.write(b"fmt ")
        f.write(struct.pack("<I", 16))       # chunk size
        f.write(struct.pack("<H", 1))        # PCM format
        f.write(struct.pack("<H", 1))        # mono
        f.write(struct.pack("<I", sample_rate))
        f.write(struct.pack("<I", sample_rate * 2))  # byte rate
        f.write(struct.pack("<H", 2))        # block align
        f.write(struct.pack("<H", 16))       # bits per sample

        # data chunk
        f.write(b"data")
        f.write(struct.pack("<I", data_size))
        for s in samples:
            f.write(struct.pack("<h", s))


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(input_file):
        print(f"Error: input file not found: {input_file}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    header_info, notes = parse_snd_file(input_file)

    version_str = f" (version {header_info['version']})" if header_info["version"] else ""
    print(f"DataShow sound file{version_str}: {header_info['filename']}")
    print(f"Notes: {len(notes)}")

    # Generate audio
    all_samples = []
    total_duration_ms = 0
    for freq, dur in notes:
        all_samples.extend(generate_square_wave(freq, dur))
        total_duration_ms += dur

    print(f"Total duration: {total_duration_ms} ms ({total_duration_ms / 1000:.2f} s)")

    # Output filename: use original filename stem with .wav extension
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_path = os.path.join(output_dir, base_name + ".wav")

    write_wav(output_path, all_samples)
    print(f"Written: {output_path}")


if __name__ == "__main__":
    main()

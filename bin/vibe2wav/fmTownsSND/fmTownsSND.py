#!/usr/bin/env python3
# Vibe coded by Claude
#
# FM Towns SND to WAV converter
# Converts Fujitsu FM Towns .snd audio files to standard .wav files.
#
# Usage: fmTownsSND.py <inputFile> <outputDir>
#        fmTownsSND.py <inputDir> <outputDir>    (batch mode)

import struct
import sys
import os
import pathlib


HEADER_SIZE = 32
SAMPLE_RATE_MULTIPLIER = 10  # SND rate field * 10 = Hz


def parse_header(data):
    """Parse the 32-byte SND header. Returns a dict of all fields."""
    if len(data) < HEADER_SIZE:
        raise ValueError(f"File too small for SND header: {len(data)} bytes (need {HEADER_SIZE})")

    name_raw = data[0:8]
    id_val = struct.unpack_from('<I', data, 8)[0]
    data_size = struct.unpack_from('<I', data, 12)[0]
    loop_start = struct.unpack_from('<I', data, 16)[0]
    loop_length = struct.unpack_from('<I', data, 20)[0]
    sample_rate = struct.unpack_from('<H', data, 24)[0]
    adjust = struct.unpack_from('<H', data, 26)[0]
    note = data[28]
    reserved1 = data[29]
    reserved2 = struct.unpack_from('<H', data, 30)[0]

    # Decode name - try ASCII first, fall back to Shift-JIS, then raw repr
    try:
        name = name_raw.decode('ascii').rstrip('\x00')
    except UnicodeDecodeError:
        try:
            name = name_raw.decode('shift_jis').rstrip('\x00')
        except UnicodeDecodeError:
            name = name_raw.hex()

    return {
        'name_raw': name_raw,
        'name': name,
        'id': id_val,
        'data_size': data_size,
        'loop_start': loop_start,
        'loop_length': loop_length,
        'sample_rate': sample_rate,
        'adjust': adjust,
        'note': note,
        'reserved1': reserved1,
        'reserved2': reserved2,
    }


def convert_sign_magnitude_to_unsigned(audio_data):
    """Convert sign-magnitude 8-bit PCM to unsigned 8-bit PCM for WAV output.

    FM Towns SND files use sign-magnitude encoding where:
      - Bit 7 is the sign (0=positive, 1=negative)
      - Bits 6-0 are the magnitude (0-127)
      - Both 0x00 (+0) and 0x80 (-0) represent silence
      - 0x7F = +127 (max positive), 0xFF = -127 (max negative)

    WAV 8-bit format uses unsigned encoding where:
      - 0x80 (128) = silence/center
      - 0xFF (255) = max positive
      - 0x01 (1) = max negative

    Conversion:
      - Positive (0x00-0x7F): unsigned = byte + 128
      - Negative (0x80-0xFF): unsigned = 128 - (byte & 0x7F) = 256 - byte
    """
    # Build lookup table for speed
    lut = bytearray(256)
    for b in range(256):
        if b < 0x80:
            lut[b] = b + 128       # positive: shift above center
        else:
            lut[b] = 256 - b       # negative: mirror below center
    return bytes(lut[b] for b in audio_data)


def write_wav(filepath, audio_data, sample_rate, bits_per_sample=8, num_channels=1):
    """Write a PCM WAV file. Audio data must be unsigned 8-bit."""
    byte_rate = sample_rate * num_channels * (bits_per_sample // 8)
    block_align = num_channels * (bits_per_sample // 8)
    data_size = len(audio_data)

    with open(filepath, 'wb') as f:
        # RIFF header
        f.write(b'RIFF')
        f.write(struct.pack('<I', 36 + data_size))  # file size - 8
        f.write(b'WAVE')

        # fmt chunk
        f.write(b'fmt ')
        f.write(struct.pack('<I', 16))              # chunk size
        f.write(struct.pack('<H', 1))               # PCM format
        f.write(struct.pack('<H', num_channels))
        f.write(struct.pack('<I', sample_rate))
        f.write(struct.pack('<I', byte_rate))
        f.write(struct.pack('<H', block_align))
        f.write(struct.pack('<H', bits_per_sample))

        # data chunk
        f.write(b'data')
        f.write(struct.pack('<I', data_size))
        f.write(audio_data)


def convert_snd_to_wav(input_path, output_dir):
    """Convert a single SND file to WAV. Returns True on success."""
    input_path = pathlib.Path(input_path)
    output_dir = pathlib.Path(output_dir)

    with open(input_path, 'rb') as f:
        file_data = f.read()

    file_size = len(file_data)
    header = parse_header(file_data)

    # Validate data size
    expected_size = header['data_size'] + HEADER_SIZE
    if expected_size != file_size:
        print(f"  WARNING: DataSize ({header['data_size']}) + header ({HEADER_SIZE}) "
              f"= {expected_size}, but file is {file_size} bytes")
        return False

    # Extract audio data
    audio_data = file_data[HEADER_SIZE:HEADER_SIZE + header['data_size']]

    # Validate sample rate
    if header['sample_rate'] == 0:
        print(f"  WARNING: Sample rate is 0, defaulting to 1000 Hz")
        actual_rate = 1000
    else:
        actual_rate = header['sample_rate'] * SAMPLE_RATE_MULTIPLIER

    # Convert sign-magnitude PCM to unsigned PCM for WAV
    wav_data = convert_sign_magnitude_to_unsigned(audio_data)

    # Build output filename
    stem = input_path.stem
    wav_path = output_dir / f"{stem}.wav"

    # Handle name collisions
    counter = 1
    while wav_path.exists():
        wav_path = output_dir / f"{stem}_{counter}.wav"
        counter += 1

    # Write WAV
    write_wav(str(wav_path), wav_data, actual_rate)

    # Print info
    duration = header['data_size'] / actual_rate if actual_rate > 0 else 0

    loop_info = "none"
    if header['loop_start'] != 0 or header['loop_length'] != 0:
        if header['loop_length'] == 0:
            loop_info = f"start={header['loop_start']} to end (implicit)"
        else:
            loop_info = f"start={header['loop_start']} len={header['loop_length']}"

    print(f"  Name: {header['name']:10s}  ID: {header['id']}")
    print(f"  Rate: {header['sample_rate']} (x10 = {actual_rate} Hz)  "
          f"Encoding: sign-magnitude  Duration: {duration:.2f}s")
    print(f"  Loop: {loop_info}  Note: {header['note']}  "
          f"Adjust: {header['adjust']}  "
          f"Reserved: {header['reserved1']},{header['reserved2']}")
    print(f"  Data: {header['data_size']} bytes  "
          f"File: {file_size} bytes  -> {wav_path.name}")

    return True


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile|inputDir> <outputDir>")
        print()
        print("  Converts FM Towns SND audio files to WAV format.")
        print()
        print("  <inputFile>  Single .snd file to convert")
        print("  <inputDir>   Directory to scan recursively for .snd files")
        print("  <outputDir>  Directory to write .wav files into")
        sys.exit(1)

    input_path = pathlib.Path(sys.argv[1])
    output_dir = pathlib.Path(sys.argv[2])

    # Collect input files
    if input_path.is_file():
        snd_files = [input_path]
    elif input_path.is_dir():
        snd_files = sorted(input_path.rglob('*.[sS][nN][dD]'))
        if not snd_files:
            print(f"No .snd files found in {input_path}")
            sys.exit(1)
    else:
        print(f"Input path does not exist: {input_path}")
        sys.exit(1)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Converting {len(snd_files)} SND file(s) to WAV")
    print(f"Output directory: {output_dir}")
    print()

    success = 0
    fail = 0

    for snd_file in snd_files:
        print(f"[{snd_file}]")
        try:
            if convert_snd_to_wav(snd_file, output_dir):
                success += 1
            else:
                fail += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            fail += 1
        print()

    print(f"Done: {success} converted, {fail} failed")


if __name__ == '__main__':
    main()

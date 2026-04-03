#!/usr/bin/env python3
# Vibe coded by Claude
"""Superscape Sounds (.snd) to WAV converter.

Usage: python3 superscapeSounds.py <inputFile> <outputDir>

Converts Superscape VRT/VR Toolkit .snd sound files to individual WAV files.
Each sound entry in the .snd file produces a separate WAV file in outputDir.
"""

import struct
import wave
import sys
import os
import re

# File structure constants
HEADER_SIZE = 0xF0           # 240-byte text header block
SOUN_HEADER_OFFSET = 0xF0   # Start of SOUN section header
SOUN_MAGIC = b'SOUN'
SOUN_MAGIC_OFFSET = 0xF4
AUDIO_DATA_START = 0x102     # First sound data entry starts here
ENTRY_HEADER_SIZE = 8        # 4 (size) + 1 (rate) + 1 (flags) + 2 (format_type)
NAME_ENTRY_SIZE = 40         # Each name table entry is 40 bytes
NAME_ENTRY_MARKER = 0xFFFF
END_MARKER = b'\xff\xff\xff\xff'


def parse_header_text(data):
    """Parse the 240-byte text header, extracting readable text up to the 0x1A EOF marker."""
    text_region = data[:HEADER_SIZE]
    eof_pos = text_region.find(0x1A)
    if eof_pos > 0:
        text = text_region[:eof_pos].decode('ascii', errors='replace')
    else:
        text = text_region.rstrip(b'\x00').decode('ascii', errors='replace')
    return text.strip()


def detect_16bit(audio_data):
    """Detect if audio data is 16-bit LE signed PCM rather than 8-bit signed PCM.

    Uses a skip-difference metric: compares average absolute difference between
    adjacent bytes (step 1) vs every-other byte (step 2). In 16-bit LE audio,
    adjacent bytes alternate between low and high bytes of each sample, creating
    large step-1 differences. Step-2 differences compare like-bytes (low-to-low
    or high-to-high), which are smoother. So step2 < step1 indicates 16-bit.
    For true 8-bit audio, step2 > step1 (skipping a sample increases the diff).
    """
    if len(audio_data) < 200 or len(audio_data) % 2 != 0:
        return False

    # Sample from the middle of the audio
    n = min(4000, len(audio_data))
    start = max(0, len(audio_data) // 2 - n // 2)
    start = start - (start % 2)  # Align to 2-byte boundary
    sec = audio_data[start:start + n]

    if len(sec) < 10:
        return False

    # Average absolute difference between adjacent bytes (step 1)
    d1 = sum(abs(int(sec[i]) - int(sec[i - 1])) for i in range(1, len(sec))) / (len(sec) - 1)
    # Average absolute difference between every-other byte (step 2)
    d2 = sum(abs(int(sec[i]) - int(sec[i - 2])) for i in range(2, len(sec))) / (len(sec) - 2)

    if d1 < 0.01:
        return False  # Near-silence, cannot determine

    # 16-bit LE: like-bytes are more correlated than adjacent bytes -> d2 < d1
    # 8-bit:     adjacent samples are more correlated than skip-one  -> d2 > d1
    return d2 / d1 < 1.0


def parse_snd(filepath):
    """Parse a Superscape .snd file and return all parsed components."""
    with open(filepath, 'rb') as f:
        data = f.read()

    file_size = len(data)

    # --- Validate and parse text header (0x00 - 0xEF) ---
    if not data.startswith(b'SuperScape'):
        raise ValueError("Not a Superscape Sounds file (missing 'SuperScape' header)")

    header_text = parse_header_text(data)

    # --- Parse SOUN section header (0xF0 - 0x101) ---
    name_table_offset = struct.unpack_from('<I', data, 0xF0)[0]

    magic = data[SOUN_MAGIC_OFFSET:SOUN_MAGIC_OFFSET + 4]
    if magic != SOUN_MAGIC:
        raise ValueError(f"Expected 'SOUN' at offset 0xF4, got {magic!r}")

    reserved1 = struct.unpack_from('<H', data, 0xF8)[0]
    revision = struct.unpack_from('<H', data, 0xFA)[0]
    reserved2 = struct.unpack_from('<H', data, 0xFC)[0]
    format_major = data[0xFE]
    format_minor = data[0xFF]
    section_flags = struct.unpack_from('<H', data, 0x100)[0]

    # --- Parse sound data entries (0x102 to name_table_offset) ---
    entries = []
    offset = AUDIO_DATA_START
    idx = 0
    while offset < name_table_offset:
        if offset + 4 > name_table_offset:
            break
        entry_size = struct.unpack_from('<I', data, offset)[0]
        if entry_size < ENTRY_HEADER_SIZE or offset + entry_size > name_table_offset:
            # Remaining bytes that don't form a valid entry
            break

        rate_byte = data[offset + 4]
        entry_flags = data[offset + 5]
        format_type = struct.unpack_from('<H', data, offset + 6)[0]

        audio_data = data[offset + ENTRY_HEADER_SIZE: offset + entry_size]

        # Compute sample rate from rate byte and format version.
        # VRT 5.x (format 05.0A): rate = byte * 44100 / 256  (0x40 -> 11025 Hz)
        # VR Toolkit 2.x (format 02.xx): rate = byte * 44100 / 128  (0x40 -> 22050 Hz)
        if rate_byte > 0:
            if format_major < 5:
                sample_rate = round(rate_byte * 44100 / 128)
            else:
                sample_rate = round(rate_byte * 44100 / 256)
        else:
            sample_rate = 11025  # Fallback default

        # Detect if this entry is 16-bit LE audio
        is_16bit = detect_16bit(audio_data)

        entries.append({
            'index': idx,
            'offset': offset,
            'size': entry_size,
            'rate_byte': rate_byte,
            'flags': entry_flags,
            'format_type': format_type,
            'sample_rate': sample_rate,
            'audio': audio_data,
            'is_16bit': is_16bit,
        })

        offset += entry_size
        idx += 1

    # Verify sound data block is fully consumed
    sound_block_remainder = name_table_offset - offset
    if sound_block_remainder != 0:
        print(f"  WARNING: {sound_block_remainder} unaccounted bytes in sound data block")

    # --- Parse name table (name_table_offset to end) ---
    names = {}
    offset = name_table_offset
    while offset + 4 <= file_size:
        marker = struct.unpack_from('<H', data, offset)[0]
        if marker != NAME_ENTRY_MARKER:
            break

        # Check for end marker (0xFFFF 0xFFFF)
        next_val = struct.unpack_from('<H', data, offset + 2)[0]
        if next_val == NAME_ENTRY_MARKER:
            # This is the end marker
            offset += 4  # Consume the 4-byte end marker
            break

        entry_type = struct.unpack_from('<H', data, offset + 2)[0]
        entry_data_size = struct.unpack_from('<H', data, offset + 4)[0]
        sound_idx = struct.unpack_from('<H', data, offset + 6)[0]

        # Read the 32-byte name field (null-terminated, may contain leftover garbage)
        name_bytes = data[offset + 8: offset + NAME_ENTRY_SIZE]
        null_pos = name_bytes.find(0)
        if null_pos >= 0:
            name = name_bytes[:null_pos].decode('ascii', errors='replace')
        else:
            name = name_bytes.decode('ascii', errors='replace')

        names[sound_idx] = {
            'name': name,
            'type': entry_type,
            'data_size': entry_data_size,
            'raw': data[offset:offset + NAME_ENTRY_SIZE],
        }

        offset += NAME_ENTRY_SIZE

    # Verify we consumed exactly to end of file
    if offset != file_size:
        print(f"  WARNING: Expected end at {file_size}, parser at {offset} "
              f"({file_size - offset} bytes remaining)")

    info = {
        'file_size': file_size,
        'header_text': header_text,
        'header_raw': data[:HEADER_SIZE],
        'name_table_offset': name_table_offset,
        'revision': revision,
        'format_major': format_major,
        'format_minor': format_minor,
        'section_flags': section_flags,
        'reserved1': reserved1,
        'reserved2': reserved2,
        'num_entries': len(entries),
        'num_names': len(names),
    }

    return entries, names, info


def sanitize_filename(name):
    """Convert a sound name to a filesystem-safe filename."""
    safe = re.sub(r'[^\w\-. ]', '_', name)
    safe = re.sub(r'_+', '_', safe)
    safe = safe.strip('_ ')
    return safe if safe else 'unnamed'


def save_wav(filepath, audio_data, sample_rate, is_16bit=False):
    """Save audio data as a WAV file.

    For 8-bit: converts signed int8 to unsigned uint8 (WAV 8-bit format).
    For 16-bit: writes as signed int16 LE (WAV 16-bit format).
    """
    with wave.open(filepath, 'wb') as wav:
        wav.setnchannels(1)

        if is_16bit:
            wav.setsampwidth(2)  # 16-bit
            wav.setframerate(sample_rate)
            wav.writeframes(audio_data)  # Already signed 16-bit LE
        else:
            wav.setsampwidth(1)  # 8-bit
            wav.setframerate(sample_rate)
            # Convert signed int8 to unsigned uint8: XOR each byte with 0x80
            unsigned_data = bytes(b ^ 0x80 for b in audio_data)
            wav.writeframes(unsigned_data)


def convert_snd(input_file, output_dir):
    """Convert a Superscape .snd file to WAV files."""
    os.makedirs(output_dir, exist_ok=True)

    entries, names, info = parse_snd(input_file)

    print(f"File: {input_file}")
    print(f"  Size: {info['file_size']} bytes")
    print(f"  Revision: {info['revision']}")
    print(f"  Format version: {info['format_major']:02X}.{info['format_minor']:02X}")
    print(f"  Section flags: {info['section_flags']}")
    print(f"  Sound entries: {info['num_entries']}")
    print(f"  Name entries: {info['num_names']}")

    wav_files = []
    for entry in entries:
        idx = entry['index']
        name_info = names.get(idx)
        name = name_info['name'] if name_info else f"sound_{idx:03d}"
        safe_name = sanitize_filename(name)
        audio_len = len(entry['audio'])
        is_16bit = entry['is_16bit']

        # Check if audio is all silence
        is_silent = all(b == 0 for b in entry['audio'])

        # Skip truly empty entries (__EMPTY with no audio data)
        if is_silent and (name == '__EMPTY' or audio_len == 0):
            print(f"  [{idx:3d}] '{name}' - EMPTY/silent ({audio_len}b, skipped)")
            continue

        # Skip entries with 0 audio bytes
        if audio_len == 0:
            print(f"  [{idx:3d}] '{name}' - no audio data (skipped)")
            continue

        wav_name = f"{idx:03d}_{safe_name}.wav"
        wav_path = os.path.join(output_dir, wav_name)

        save_wav(wav_path, entry['audio'], entry['sample_rate'], is_16bit)

        if is_16bit:
            num_samples = audio_len // 2
            bit_label = "16-bit"
        else:
            num_samples = audio_len
            bit_label = "8-bit"

        duration = num_samples / entry['sample_rate']
        status = "SILENT" if is_silent else f"{duration:.2f}s"

        print(f"  [{idx:3d}] '{name}' -> {wav_name} "
              f"({entry['sample_rate']} Hz, {bit_label}, rate=0x{entry['rate_byte']:02X}, "
              f"flags=0x{entry['flags']:02X}, fmt={entry['format_type']}, {status})")

        wav_files.append({
            'filename': wav_name,
            'name': name,
            'index': idx,
            'sample_rate': entry['sample_rate'],
            'duration': duration,
            'is_16bit': is_16bit,
            'is_silent': is_silent,
        })

    return wav_files, info


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>")
        print()
        print("Converts a Superscape VRT .snd file to WAV files.")
        print("Each sound in the .snd file produces a separate WAV in outputDir.")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(input_file):
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)

    wav_files, info = convert_snd(input_file, output_dir)
    print(f"\n  Produced {len(wav_files)} WAV file(s) in {output_dir}")


if __name__ == '__main__':
    main()

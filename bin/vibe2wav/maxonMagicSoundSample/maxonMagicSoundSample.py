#!/usr/bin/env python3
# Vibe coded by Claude

"""
MaxonMAGIC Sound Sample (.HSN / HSND) to WAV converter.

Converts Amiga MaxonMAGIC Sound Sample files (HSND1.0 and HSND1.1 formats)
to standard WAV files.

Usage: maxonMagicSoundSample.py <inputFile> <outputDir>
"""

import struct
import sys
import os

AMIGA_VOLUME_MAX = 64
HSND_V10_HEADER_SIZE = 48  # 0x30
HSND_V11_HEADER_SIZE = 90  # 0x5A
HSND_DESCRIPTION_SIZE = 42


def read_hsn(filepath):
    """Parse an HSN file and return a dict with all header fields and audio data."""
    with open(filepath, "rb") as f:
        raw = f.read()

    if len(raw) < HSND_V10_HEADER_SIZE:
        raise ValueError(f"File too small ({len(raw)} bytes), minimum header is {HSND_V10_HEADER_SIZE} bytes")

    # 0x00-0x07: Magic and version
    magic = raw[0x00:0x08]
    if magic[:4] != b"HSND":
        raise ValueError(f"Not an HSND file (magic: {magic[:4]!r})")

    version_str = magic[4:7].decode("ascii", errors="replace")
    if version_str == "1.0":
        version = 10
        header_size = HSND_V10_HEADER_SIZE
    elif version_str == "1.1":
        version = 11
        header_size = HSND_V11_HEADER_SIZE
    else:
        raise ValueError(f"Unknown HSND version: {version_str!r}")

    if len(raw) < header_size:
        raise ValueError(f"File too small ({len(raw)} bytes) for HSND{version_str} header ({header_size} bytes)")

    # 0x08-0x0B: Source format tag (original file extension, 4 bytes, null-padded)
    source_format_tag = raw[0x08:0x0C]

    # 0x0C-0x13: Reserved (8 bytes, must be zero)
    reserved1 = raw[0x0C:0x14]

    # 0x14-0x17: Audio data length (uint32 big-endian)
    data_length = struct.unpack(">I", raw[0x14:0x18])[0]

    # 0x18-0x19: Sample rate encoding (uint16 big-endian, multiply by 10 for Hz)
    sample_rate_raw = struct.unpack(">H", raw[0x18:0x1A])[0]
    sample_rate = sample_rate_raw * 10

    # 0x1A-0x1D: Reserved (4 bytes, must be zero)
    reserved2 = raw[0x1A:0x1E]

    # 0x1E-0x1F: Bits per sample indicator (uint16 big-endian, typically 8)
    bits_per_sample = struct.unpack(">H", raw[0x1E:0x20])[0]

    # 0x20: Padding (always 0x00)
    padding_20 = raw[0x20]

    # 0x21: Flag byte (0 or 1)
    flag_21 = raw[0x21]

    # 0x22-0x23: Volume (uint16 big-endian, 0-64 Amiga scale)
    volume = struct.unpack(">H", raw[0x22:0x24])[0]

    # 0x24-0x25: Playback parameter 1 (uint16 big-endian, always 20)
    playback_param1 = struct.unpack(">H", raw[0x24:0x26])[0]

    # 0x26-0x27: Playback parameter 2 (uint16 big-endian, always 20)
    playback_param2 = struct.unpack(">H", raw[0x26:0x28])[0]

    # 0x28: Padding (always 0x00)
    padding_28 = raw[0x28]

    # 0x29: Metadata byte A
    meta_a = raw[0x29]

    # 0x2A: Padding (always 0x00)
    padding_2a = raw[0x2A]

    # 0x2B: Metadata byte B
    meta_b = raw[0x2B]

    # 0x2C-0x2F: Metadata field C (uint32 big-endian)
    meta_c = struct.unpack(">I", raw[0x2C:0x30])[0]

    # 0x30-0x59: Description (v1.1 only, 42 bytes, null-terminated)
    description = ""
    if version == 11:
        desc_raw = raw[0x30:0x5A]
        description = desc_raw.split(b"\x00")[0].decode("latin-1", errors="replace")

    # Audio data
    audio_start = header_size
    available_data = len(raw) - audio_start
    truncated = available_data < data_length
    actual_data_length = min(data_length, available_data)
    audio_data = raw[audio_start:audio_start + actual_data_length]

    # Format source tag for display
    source_tag_display = ""
    for b in source_format_tag:
        if 0x20 <= b < 0x7F:
            source_tag_display += chr(b)
        elif b == 0:
            source_tag_display += "\\0"
        else:
            source_tag_display += f"\\x{b:02x}"

    return {
        "version": version,
        "version_str": version_str,
        "header_size": header_size,
        "source_format_tag": source_format_tag,
        "source_tag_display": source_tag_display,
        "reserved1": reserved1,
        "data_length": data_length,
        "sample_rate_raw": sample_rate_raw,
        "sample_rate": sample_rate,
        "reserved2": reserved2,
        "bits_per_sample": bits_per_sample,
        "padding_20": padding_20,
        "flag_21": flag_21,
        "volume": volume,
        "playback_param1": playback_param1,
        "playback_param2": playback_param2,
        "padding_28": padding_28,
        "meta_a": meta_a,
        "padding_2a": padding_2a,
        "meta_b": meta_b,
        "meta_c": meta_c,
        "description": description,
        "audio_data": audio_data,
        "actual_data_length": actual_data_length,
        "truncated": truncated,
        "file_size": len(raw),
    }


def signed8_to_unsigned8(data):
    """Convert signed 8-bit PCM (Amiga format) to unsigned 8-bit PCM (WAV format).

    Signed:   0 = silence, range -128..+127
    Unsigned: 128 = silence, range 0..255
    Conversion: XOR each byte with 0x80 (flip the sign bit)
    """
    return bytes(b ^ 0x80 for b in data)


def write_wav(filepath, sample_rate, audio_data_unsigned):
    """Write a WAV file with 8-bit unsigned mono PCM audio."""
    num_channels = 1
    bits_per_sample = 8
    byte_rate = sample_rate * num_channels * (bits_per_sample // 8)
    block_align = num_channels * (bits_per_sample // 8)
    data_size = len(audio_data_unsigned)

    with open(filepath, "wb") as f:
        # RIFF header
        f.write(b"RIFF")
        f.write(struct.pack("<I", 36 + data_size))  # file size - 8
        f.write(b"WAVE")

        # fmt chunk
        f.write(b"fmt ")
        f.write(struct.pack("<I", 16))               # chunk size
        f.write(struct.pack("<H", 1))                 # audio format (1 = PCM)
        f.write(struct.pack("<H", num_channels))      # channels
        f.write(struct.pack("<I", sample_rate))        # sample rate
        f.write(struct.pack("<I", byte_rate))          # byte rate
        f.write(struct.pack("<H", block_align))        # block align
        f.write(struct.pack("<H", bits_per_sample))    # bits per sample

        # data chunk
        f.write(b"data")
        f.write(struct.pack("<I", data_size))
        f.write(audio_data_unsigned)


def print_header_info(info, filepath):
    """Print detailed header information."""
    print(f"File:              {filepath}")
    print(f"File size:         {info['file_size']} bytes")
    print(f"Format:            HSND{info['version_str']} ({'extended' if info['version'] == 11 else 'basic'} header)")
    print(f"Header size:       {info['header_size']} bytes (0x{info['header_size']:02X})")
    print(f"Source format tag: [{info['source_tag_display']}] (0x{info['source_format_tag'].hex()})")
    print(f"Reserved 1:        0x{info['reserved1'].hex()}")
    print(f"Data length:       {info['data_length']} bytes (0x{info['data_length']:08X})")
    print(f"Sample rate raw:   {info['sample_rate_raw']} (x10 = {info['sample_rate']} Hz)")
    print(f"Reserved 2:        0x{info['reserved2'].hex()}")
    print(f"Bits per sample:   {info['bits_per_sample']}")
    print(f"Padding 0x20:      0x{info['padding_20']:02X}")
    print(f"Flag 0x21:         {info['flag_21']}")
    print(f"Volume:            {info['volume']} / {AMIGA_VOLUME_MAX}")
    print(f"Playback param 1:  {info['playback_param1']}")
    print(f"Playback param 2:  {info['playback_param2']}")
    print(f"Padding 0x28:      0x{info['padding_28']:02X}")
    print(f"Metadata A (0x29): {info['meta_a']}")
    print(f"Padding 0x2A:      0x{info['padding_2a']:02X}")
    print(f"Metadata B (0x2B): {info['meta_b']}")
    print(f"Metadata C:        {info['meta_c']} (0x{info['meta_c']:08X})")
    if info["version"] == 11:
        print(f"Description:       {info['description']!r}")
    print(f"Audio data:        {info['actual_data_length']} bytes" +
          (f" (TRUNCATED from {info['data_length']})" if info['truncated'] else ""))
    duration = info["actual_data_length"] / info["sample_rate"] if info["sample_rate"] > 0 else 0
    print(f"Duration:          {duration:.3f} seconds")


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>")
        print()
        print("Converts MaxonMAGIC Sound Sample (.HSN) files to WAV format.")
        print()
        print("  inputFile  Path to an .HSN file")
        print("  outputDir  Directory where the .WAV file will be written")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(input_file):
        print(f"Error: input file not found: {input_file}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    # Parse the HSN file
    info = read_hsn(input_file)

    # Print header info
    print_header_info(info, input_file)
    print()

    if info["actual_data_length"] == 0:
        print("Warning: no audio data to convert", file=sys.stderr)
        sys.exit(1)

    if info["sample_rate"] == 0:
        print("Error: sample rate is 0", file=sys.stderr)
        sys.exit(1)

    # Convert signed 8-bit to unsigned 8-bit for WAV
    wav_audio = signed8_to_unsigned8(info["audio_data"])

    # Generate output filename
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join(output_dir, base_name + ".wav")

    # Write WAV
    write_wav(output_file, info["sample_rate"], wav_audio)

    print(f"Wrote: {output_file}")
    print(f"  Format: WAV, 8-bit unsigned PCM, mono, {info['sample_rate']} Hz")
    print(f"  Size: {os.path.getsize(output_file)} bytes")


if __name__ == "__main__":
    main()

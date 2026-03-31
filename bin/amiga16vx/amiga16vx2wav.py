#!/usr/bin/env python3
# Vibe coded by Claude
#
# amiga16vx2wav.py - Convert Amiga 16SV (16-bit Sampled Voice) files to WAV
#
# Usage: python3 amiga16vx2wav.py <inputFile> <outputFile>

import struct
import sys
import os


def read_uint32_be(data, offset):
    return struct.unpack('>I', data[offset:offset + 4])[0]


def read_uint16_be(data, offset):
    return struct.unpack('>H', data[offset:offset + 2])[0]


def parse_iff_chunks(data):
    """Parse all IFF chunks from a 16SV file. Returns (form_type, chunks_dict, chunks_list)."""
    if len(data) < 12:
        raise ValueError("File too small to be a valid IFF file")

    form_id = data[0:4]
    if form_id != b'FORM':
        raise ValueError(f"Not an IFF file: expected 'FORM', got {form_id!r}")

    form_size = read_uint32_be(data, 4)
    form_type = data[8:12]

    if form_type != b'16SV':
        raise ValueError(f"Not a 16SV file: FORM type is {form_type!r}")

    expected_size = form_size + 8
    if len(data) != expected_size:
        print(f"Warning: file size {len(data)} != expected {expected_size}", file=sys.stderr)

    chunks = {}
    chunks_list = []
    offset = 12

    while offset + 8 <= len(data):
        chunk_id = data[offset:offset + 4]
        chunk_size = read_uint32_be(data, offset + 4)
        chunk_data = data[offset + 8:offset + 8 + chunk_size]

        chunk_id_str = chunk_id.decode('latin-1')
        chunks[chunk_id_str] = chunk_data
        chunks_list.append((chunk_id_str, chunk_data))

        # Advance past chunk, with IFF even-alignment padding
        offset += 8 + chunk_size
        if chunk_size % 2 == 1:
            offset += 1

    return form_type, chunks, chunks_list


def parse_vhdr(data):
    """Parse a VHDR (Voice Header) chunk. Returns a dict of fields."""
    if len(data) < 20:
        raise ValueError(f"VHDR chunk too small: {len(data)} bytes, expected 20")

    return {
        'oneShotHiSamples': read_uint32_be(data, 0),
        'repeatHiSamples': read_uint32_be(data, 4),
        'samplesPerHiCycle': read_uint32_be(data, 8),
        'samplesPerSec': read_uint16_be(data, 12),
        'ctOctave': data[14],
        'sCompression': data[15],
        'volume': read_uint32_be(data, 16),
    }


def parse_chan(data):
    """Parse a CHAN chunk. Returns number of channels."""
    if len(data) < 4:
        raise ValueError(f"CHAN chunk too small: {len(data)} bytes")

    chan_val = read_uint32_be(data, 0)
    if chan_val == 6:
        return 2  # stereo
    elif chan_val in (2, 4):
        return 1  # left-only or right-only
    else:
        print(f"Warning: unknown CHAN value {chan_val}, assuming mono", file=sys.stderr)
        return 1


def convert_body_to_pcm(body_data, num_channels, samples_per_channel):
    """Convert big-endian 16-bit BODY data to little-endian interleaved PCM."""
    expected_body_size = samples_per_channel * 2 * num_channels
    if len(body_data) != expected_body_size:
        print(f"Warning: BODY size {len(body_data)} != expected {expected_body_size}",
              file=sys.stderr)

    total_samples = len(body_data) // 2
    # Read all samples as big-endian signed 16-bit
    samples = struct.unpack(f'>{total_samples}h', body_data[:total_samples * 2])

    if num_channels == 1:
        # Mono: just convert to little-endian
        return struct.pack(f'<{total_samples}h', *samples)
    else:
        # Stereo planar -> interleaved
        # First half = left channel, second half = right channel
        left = samples[:samples_per_channel]
        right = samples[samples_per_channel:samples_per_channel * 2]

        # Interleave: L[0], R[0], L[1], R[1], ...
        interleaved = []
        for i in range(samples_per_channel):
            interleaved.append(left[i])
            interleaved.append(right[i])

        return struct.pack(f'<{len(interleaved)}h', *interleaved)


def write_wav(filename, pcm_data, sample_rate, num_channels, bits_per_sample=16):
    """Write a standard PCM WAV file."""
    byte_rate = sample_rate * num_channels * bits_per_sample // 8
    block_align = num_channels * bits_per_sample // 8
    data_size = len(pcm_data)

    # RIFF header + fmt chunk + data chunk
    riff_size = 4 + 24 + 8 + data_size  # "WAVE" + fmt chunk (24) + data header (8) + data

    with open(filename, 'wb') as f:
        # RIFF header
        f.write(b'RIFF')
        f.write(struct.pack('<I', riff_size))
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
        f.write(pcm_data)


def print_file_info(chunks_list, vhdr, num_channels):
    """Print metadata about the 16SV file."""
    samples_per_channel = vhdr['oneShotHiSamples'] + vhdr['repeatHiSamples']
    duration = samples_per_channel / vhdr['samplesPerSec'] if vhdr['samplesPerSec'] else 0

    print(f"  Sample rate:    {vhdr['samplesPerSec']} Hz")
    print(f"  Channels:       {num_channels} ({'stereo' if num_channels == 2 else 'mono'})")
    print(f"  Samples:        {samples_per_channel} per channel")
    print(f"  Duration:       {duration:.3f} seconds")
    print(f"  One-shot:       {vhdr['oneShotHiSamples']} samples")
    if vhdr['repeatHiSamples'] > 0:
        print(f"  Repeat loop:    {vhdr['repeatHiSamples']} samples")
    if vhdr['samplesPerHiCycle'] > 0:
        print(f"  Samples/cycle:  {vhdr['samplesPerHiCycle']}")
    print(f"  Compression:    {vhdr['sCompression']} ({'none' if vhdr['sCompression'] == 0 else 'unknown'})")

    vol = vhdr['volume']
    if vol == 0x00010000:
        print(f"  Volume:         1.0 (unity)")
    else:
        vol_float = vol / 65536.0
        print(f"  Volume:         0x{vol:08X} ({vol_float:.4f})")

    for chunk_id, chunk_data in chunks_list:
        if chunk_id == 'NAME':
            name = chunk_data.decode('latin-1').rstrip('\x00')
            if name:
                print(f"  Name:           {name}")
        elif chunk_id == 'ANNO':
            anno = chunk_data.decode('latin-1').rstrip('\x00')
            if anno:
                print(f"  Annotation:     {anno}")
        elif chunk_id == 'AUTH':
            auth = chunk_data.decode('latin-1').rstrip('\x00')
            if auth:
                print(f"  Author:         {auth}")
        elif chunk_id == '(c) ':
            copy = chunk_data.decode('latin-1').rstrip('\x00')
            if copy:
                print(f"  Copyright:      {copy}")
        elif chunk_id == 'ADSR':
            if len(chunk_data) >= 16:
                a, d, s, r = struct.unpack('>IIII', chunk_data[0:16])
                print(f"  ADSR:           A={a} D={d} S={s} R={r}")


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputFile>", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    if not os.path.isfile(input_file):
        print(f"Error: input file not found: {input_file}", file=sys.stderr)
        sys.exit(1)

    with open(input_file, 'rb') as f:
        data = f.read()

    print(f"Reading: {input_file} ({len(data)} bytes)")

    # Parse IFF structure
    form_type, chunks, chunks_list = parse_iff_chunks(data)

    # Parse VHDR (required)
    if 'VHDR' not in chunks:
        print("Error: no VHDR chunk found", file=sys.stderr)
        sys.exit(1)
    vhdr = parse_vhdr(chunks['VHDR'])

    if vhdr['sCompression'] != 0:
        print(f"Error: unsupported compression type {vhdr['sCompression']}", file=sys.stderr)
        sys.exit(1)

    # Determine channel count
    num_channels = 1
    if 'CHAN' in chunks:
        num_channels = parse_chan(chunks['CHAN'])

    # Print file info
    print_file_info(chunks_list, vhdr, num_channels)

    # Parse BODY (required)
    if 'BODY' not in chunks:
        print("Error: no BODY chunk found", file=sys.stderr)
        sys.exit(1)

    samples_per_channel = vhdr['oneShotHiSamples'] + vhdr['repeatHiSamples']

    # Convert to PCM
    pcm_data = convert_body_to_pcm(chunks['BODY'], num_channels, samples_per_channel)

    # Write WAV
    write_wav(output_file, pcm_data, vhdr['samplesPerSec'], num_channels)

    out_size = os.path.getsize(output_file)
    print(f"Written: {output_file} ({out_size} bytes)")


if __name__ == '__main__':
    main()

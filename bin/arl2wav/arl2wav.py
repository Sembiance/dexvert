#!/usr/bin/env python3
# Vibe coded by Claude

"""
arl2wav - Extract WAV files from Aureal Aspen Sound Bank (.arl) files.

Aureal Aspen Sound Banks are a variant of the SoundFont 2.0 (SF2) RIFF format
used by Aureal Semiconductor's ASPEN wavetable synthesizer hardware.

Usage: arl2wav.py <input.arl> <outputDir>
"""

import struct
import sys
import os
import wave


def read_u32(data, offset):
    return struct.unpack_from('<I', data, offset)[0]


def read_u16(data, offset):
    return struct.unpack_from('<H', data, offset)[0]


def read_i8(data, offset):
    return struct.unpack_from('<b', data, offset)[0]


def parse_info_chunks(data, start, end):
    """Parse INFO sub-chunks and return as dict."""
    info = {}
    pos = start
    while pos < end:
        chunk_id = data[pos:pos+4].decode('ascii', errors='replace')
        chunk_size = read_u32(data, pos + 4)
        chunk_data = data[pos+8:pos+8+chunk_size]
        info[chunk_id] = chunk_data
        pos += 8 + chunk_size + (chunk_size % 2)
    return info


def parse_shdr_records(data, shdr_offset, shdr_size):
    """Parse 48-byte sample header records."""
    record_size = 48
    num_records = shdr_size // record_size
    samples = []

    pos = shdr_offset
    for i in range(num_records):
        rec = data[pos:pos+record_size]

        # 20-byte null-terminated name
        name_raw = rec[0:20]
        null_idx = name_raw.find(b'\x00')
        if null_idx >= 0:
            name = name_raw[:null_idx].decode('ascii', errors='replace')
        else:
            name = name_raw.decode('ascii', errors='replace')

        start = struct.unpack_from('<I', rec, 20)[0]
        end = struct.unpack_from('<I', rec, 24)[0]
        loop_start = struct.unpack_from('<I', rec, 28)[0]
        loop_end = struct.unpack_from('<I', rec, 32)[0]
        sample_rate = struct.unpack_from('<I', rec, 36)[0]
        original_pitch = rec[40]
        pitch_correction = struct.unpack_from('<b', rec, 41)[0]
        sample_link = struct.unpack_from('<H', rec, 42)[0]
        sample_type = struct.unpack_from('<H', rec, 44)[0]
        flags = struct.unpack_from('<H', rec, 46)[0]

        samples.append({
            'name': name,
            'start': start,
            'end': end,
            'loop_start': loop_start,
            'loop_end': loop_end,
            'sample_rate': sample_rate,
            'original_pitch': original_pitch,
            'pitch_correction': pitch_correction,
            'sample_link': sample_link,
            'sample_type': sample_type,
            'flags': flags,
        })
        pos += record_size

    return samples


def sanitize_filename(name):
    """Make a sample name safe for use as a filename."""
    # Replace problematic characters
    bad_chars = '<>:"/\\|?*'
    result = name
    for c in bad_chars:
        result = result.replace(c, '_')
    # Remove leading/trailing whitespace and dots
    result = result.strip(' .')
    if not result:
        result = 'unnamed'
    return result


def extract_samples(input_path, output_dir):
    with open(input_path, 'rb') as f:
        data = f.read()

    file_size = len(data)

    # Validate RIFF/sfbk header
    if data[0:4] != b'RIFF':
        print(f'Error: Not a RIFF file', file=sys.stderr)
        sys.exit(1)
    if data[8:12] != b'sfbk':
        print(f'Error: Not a SoundFont bank (expected "sfbk" form type)', file=sys.stderr)
        sys.exit(1)

    # Validate INFO LIST
    if data[12:16] != b'LIST' or data[20:24] != b'INFO':
        print(f'Error: Expected INFO LIST at offset 12', file=sys.stderr)
        sys.exit(1)

    # Find sdta LIST (always at fixed offset 0x13A in observed files,
    # but scan for it to be safe)
    sdta_offset = data.find(b'LIST', 24)
    while sdta_offset != -1:
        list_type = data[sdta_offset+8:sdta_offset+12]
        if list_type == b'sdta':
            break
        sdta_offset = data.find(b'LIST', sdta_offset + 4)

    if sdta_offset == -1:
        print(f'Error: sdta LIST not found', file=sys.stderr)
        sys.exit(1)

    sdta_size = read_u32(data, sdta_offset + 4)

    # Parse smpl chunk within sdta
    smpl_offset = sdta_offset + 12  # after LIST header + type
    if data[smpl_offset:smpl_offset+4] != b'smpl':
        print(f'Error: Expected smpl chunk at offset 0x{smpl_offset:X}', file=sys.stderr)
        sys.exit(1)

    smpl_size = read_u32(data, smpl_offset + 4)
    smpl_data_offset = smpl_offset + 8  # start of raw PCM data
    smpl_data_end = smpl_data_offset + smpl_size

    # Find pdta LIST (immediately after smpl data)
    pdta_offset = smpl_data_end
    if data[pdta_offset:pdta_offset+4] != b'LIST':
        print(f'Error: Expected pdta LIST at offset 0x{pdta_offset:X}', file=sys.stderr)
        sys.exit(1)
    if data[pdta_offset+8:pdta_offset+12] != b'pdta':
        print(f'Error: Expected pdta type at offset 0x{pdta_offset+8:X}', file=sys.stderr)
        sys.exit(1)

    pdta_size = read_u32(data, pdta_offset + 4)

    # Find shdr chunk within pdta
    shdr_offset = data.find(b'shdr', pdta_offset + 12)
    if shdr_offset == -1 or shdr_offset >= pdta_offset + 8 + pdta_size:
        print(f'Error: shdr chunk not found in pdta', file=sys.stderr)
        sys.exit(1)

    shdr_size = read_u32(data, shdr_offset + 4)
    shdr_data_offset = shdr_offset + 8

    # Parse sample headers (48 bytes each)
    samples = parse_shdr_records(data, shdr_data_offset, shdr_size)

    # Print INFO
    info_start = 24
    info_end = sdta_offset
    info = parse_info_chunks(data, info_start, info_end)
    for key, val in info.items():
        text = val.rstrip(b'\x00').decode('ascii', errors='replace')
        if text:
            print(f'  {key}: {text}')

    print(f'  Sample data: {smpl_size} bytes ({smpl_size // 2} samples)')
    print(f'  Sample headers: {len(samples)} records')

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Extract each sample as WAV
    extracted = 0
    name_counts = {}
    for sample in samples:
        name = sample['name']

        # Skip EOS terminal record
        if name == 'EOS':
            continue

        # Skip zero-length samples (LP metadata records with start == end)
        if sample['start'] >= sample['end']:
            continue

        # Skip samples with no sample rate
        if sample['sample_rate'] == 0:
            continue

        num_samples = sample['end'] - sample['start']
        byte_start = smpl_data_offset + sample['start'] * 2
        byte_end = smpl_data_offset + sample['end'] * 2

        if byte_end > smpl_data_end:
            print(f'  Warning: Sample "{name}" extends past smpl data, truncating', file=sys.stderr)
            byte_end = smpl_data_end
            num_samples = (byte_end - byte_start) // 2

        pcm_data = data[byte_start:byte_end]

        # Handle duplicate names
        safe_name = sanitize_filename(name)
        if safe_name in name_counts:
            name_counts[safe_name] += 1
            safe_name = f'{safe_name}_{name_counts[safe_name]}'
        else:
            name_counts[safe_name] = 0

        wav_path = os.path.join(output_dir, f'{safe_name}.wav')

        # Write WAV file (16-bit mono PCM)
        with wave.open(wav_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(sample['sample_rate'])
            wf.writeframes(pcm_data)

        duration_ms = num_samples / sample['sample_rate'] * 1000
        extracted += 1

    print(f'  Extracted {extracted} WAV files to {output_dir}')


def main():
    if len(sys.argv) != 3:
        print(f'Usage: {sys.argv[0]} <input.arl> <outputDir>', file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(input_path):
        print(f'Error: File not found: {input_path}', file=sys.stderr)
        sys.exit(1)

    extract_samples(input_path, output_dir)


if __name__ == '__main__':
    main()

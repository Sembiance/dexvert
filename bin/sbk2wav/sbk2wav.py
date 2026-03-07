#!/usr/bin/env python3
# Vibe coded by Claude

"""
sbk2wav.py - Convert SoundFont 1.0 (.SBK) files to individual WAV files.

Usage: python3 sbk2wav.py <input.sbk> <outputDir>

Extracts all audio samples from a SoundFont 1.0 bank file and writes each
as a separate 16-bit mono WAV file.
"""

import struct
import sys
import os
import wave


def read_riff_chunks(data, start, end):
    """Parse RIFF chunks from data[start:end], yielding (id, offset, size, data_offset)."""
    pos = start
    while pos + 8 <= end:
        ck_id = data[pos:pos + 4]
        ck_size = struct.unpack_from('<I', data, pos + 4)[0]
        data_offset = pos + 8
        yield ck_id, pos, ck_size, data_offset
        pos = data_offset + ck_size  # No word-alignment padding in SBK files


def parse_sbk(filepath):
    """Parse a SoundFont 1.0 (.SBK) file and return its structure."""
    with open(filepath, 'rb') as f:
        data = f.read()

    if len(data) < 12:
        raise ValueError("File too small to be a valid SBK file")

    # Verify RIFF header
    riff_id = data[0:4]
    riff_size = struct.unpack_from('<I', data, 4)[0]
    riff_form = data[8:12]

    if riff_id != b'RIFF':
        raise ValueError(f"Not a RIFF file (got {riff_id!r})")
    if riff_form != b'sfbk':
        raise ValueError(f"Not a SoundFont bank (form type {riff_form!r}, expected 'sfbk')")

    result = {
        'riff_size': riff_size,
        'info': {},
        'snam': b'',
        'smpl': b'',
        'pdta': {},
    }

    # Parse top-level LIST chunks
    for ck_id, ck_pos, ck_size, ck_data_off in read_riff_chunks(data, 12, 8 + riff_size):
        if ck_id == b'LIST':
            list_type = data[ck_data_off:ck_data_off + 4]
            list_end = ck_data_off + ck_size

            if list_type == b'INFO':
                for sub_id, _, sub_size, sub_data_off in read_riff_chunks(data, ck_data_off + 4, list_end):
                    key = sub_id.decode('ascii', errors='replace')
                    result['info'][key] = data[sub_data_off:sub_data_off + sub_size]

            elif list_type == b'sdta':
                for sub_id, _, sub_size, sub_data_off in read_riff_chunks(data, ck_data_off + 4, list_end):
                    if sub_id == b'snam':
                        result['snam'] = data[sub_data_off:sub_data_off + sub_size]
                    elif sub_id == b'smpl':
                        result['smpl'] = data[sub_data_off:sub_data_off + sub_size]

            elif list_type == b'pdta':
                for sub_id, _, sub_size, sub_data_off in read_riff_chunks(data, ck_data_off + 4, list_end):
                    key = sub_id.decode('ascii', errors='replace')
                    result['pdta'][key] = data[sub_data_off:sub_data_off + sub_size]

    return result


def extract_sample_names(snam_data):
    """Extract sample names from the snam chunk. Each name is 20 bytes, null-padded."""
    names = []
    num_samples = len(snam_data) // 20
    for i in range(num_samples):
        raw = snam_data[i * 20:(i + 1) * 20]
        name = raw.split(b'\x00')[0].decode('ascii', errors='replace')
        names.append(name)
    return names


def extract_sample_headers(shdr_data):
    """Extract sample headers from the shdr chunk. Each record is 16 bytes."""
    headers = []
    num_samples = len(shdr_data) // 16
    for i in range(num_samples):
        start, end, loop_start, loop_end = struct.unpack_from('<IIII', shdr_data, i * 16)
        headers.append({
            'start': start,
            'end': end,
            'loop_start': loop_start,
            'loop_end': loop_end,
        })
    return headers


def extract_sample_rates(pdta):
    """Walk igen generators to find sample rate (gen 55) per sampleID (gen 53)."""
    igen_data = pdta.get('igen', b'')
    sample_rates = {}
    current_rate = None

    num_gens = len(igen_data) // 4
    for i in range(num_gens):
        gen_op, gen_val = struct.unpack_from('<HH', igen_data, i * 4)
        if gen_op == 55:  # sampleRate (SF1-specific generator)
            current_rate = gen_val
        elif gen_op == 53:  # sampleID
            if current_rate is not None:
                sample_rates[gen_val] = current_rate
            current_rate = None

    # Also check pgen for a default sample rate
    pgen_data = pdta.get('pgen', b'')
    default_rate = None
    num_pgens = len(pgen_data) // 4
    for i in range(num_pgens):
        gen_op, gen_val = struct.unpack_from('<HH', pgen_data, i * 4)
        if gen_op == 55:
            default_rate = gen_val

    return sample_rates, default_rate


def sanitize_filename(name):
    """Make a string safe for use as a filename."""
    # Replace problematic characters
    safe = name.replace('/', '_').replace('\\', '_').replace(':', '_')
    safe = safe.replace('*', '_').replace('?', '_').replace('"', '_')
    safe = safe.replace('<', '_').replace('>', '_').replace('|', '_')
    safe = safe.strip()
    if not safe:
        safe = "unnamed"
    return safe


def write_wav(filepath, pcm_data, sample_rate, num_channels=1, bits_per_sample=16):
    """Write raw PCM data as a WAV file."""
    with wave.open(filepath, 'wb') as wf:
        wf.setnchannels(num_channels)
        wf.setsampwidth(bits_per_sample // 8)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_data)


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.sbk> <outputDir>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(input_path):
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    # Parse the SBK file
    print(f"Parsing: {input_path}")
    sbk = parse_sbk(input_path)

    # Display INFO metadata
    print(f"  RIFF size: {sbk['riff_size']} bytes")
    for key, val in sbk['info'].items():
        text = val.rstrip(b'\x00').decode('ascii', errors='replace')
        if key == 'ifil':
            major, minor = struct.unpack_from('<HH', val)
            text = f"{major}.{minor}"
        elif key == 'iver':
            major, minor = struct.unpack_from('<HH', val)
            text = f"{major}.{minor}"
        print(f"  {key}: {text}")

    # Extract sample names and headers
    sample_names = extract_sample_names(sbk['snam'])
    sample_headers = extract_sample_headers(sbk['pdta'].get('shdr', b''))
    smpl_data = sbk['smpl']

    if not sample_names:
        print("No samples found in file.")
        sys.exit(0)

    print(f"  Samples: {len(sample_names)}")
    print(f"  Sample data: {len(smpl_data)} bytes")

    if not smpl_data:
        print("\nNo embedded sample data (smpl chunk) found.")
        print("This bank likely references ROM samples only and contains no extractable audio.")
        sys.exit(0)

    # Get sample rates from igen/pgen generators
    sample_rates, default_rate = extract_sample_rates(sbk['pdta'])

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Extract and write each sample
    total_samples_in_smpl = len(smpl_data) // 2  # 16-bit samples
    extracted = 0
    skipped = 0

    for i, name in enumerate(sample_names):
        if i >= len(sample_headers):
            print(f"  Warning: Sample {i} ({name}) has no header record, skipping")
            skipped += 1
            continue

        hdr = sample_headers[i]
        start = hdr['start']
        end = hdr['end']

        # Validate sample boundaries
        if start >= total_samples_in_smpl or end > total_samples_in_smpl:
            print(f"  Warning: Sample {i} ({name}) offsets ({start}-{end}) exceed smpl data ({total_samples_in_smpl}), skipping")
            skipped += 1
            continue

        if end <= start:
            print(f"  Warning: Sample {i} ({name}) has zero or negative length ({start}-{end}), skipping")
            skipped += 1
            continue

        # Get sample rate
        rate = sample_rates.get(i)
        if rate is None:
            rate = default_rate if default_rate else 8000
            rate_source = "default"
        else:
            rate_source = "igen"

        # Extract PCM data (16-bit signed LE, mono)
        byte_start = start * 2
        byte_end = end * 2
        pcm = smpl_data[byte_start:byte_end]

        num_frames = end - start

        # Generate unique filename
        safe_name = sanitize_filename(name)
        filename = f"{i:03d}_{safe_name}.wav"
        filepath = os.path.join(output_dir, filename)

        # Write WAV
        write_wav(filepath, pcm, rate)

        duration = num_frames / rate
        print(f"  [{i:3d}] {name:20s} -> {filename:40s} rate={rate:5d}Hz ({rate_source}) frames={num_frames:7d} dur={duration:.2f}s loop={hdr['loop_start']}-{hdr['loop_end']}")
        extracted += 1

    print(f"\nDone: {extracted} samples extracted, {skipped} skipped")
    print(f"Output: {output_dir}/")


if __name__ == '__main__':
    main()

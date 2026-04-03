# Vibe coded by Claude
# StoneTracker Sample (SPS) file converter - extracts audio samples to WAV files
# Supports both uncompressed (type 0x00) and DeltaHuffMan compressed (type 0x01) SPS files

import struct
import wave
import sys
import os

SAMPLE_RATE = 8363  # Standard Amiga C-2 tuning frequency


def read_be_u16(data, offset):
    return struct.unpack_from('>H', data, offset)[0]


def read_be_u32(data, offset):
    return struct.unpack_from('>I', data, offset)[0]


def parse_sps_header(data):
    """Parse the SPS file header and sample entries."""
    if len(data) < 6 or data[0:3] != b'SPS':
        return None

    version = data[3]
    stype = data[4]
    num_samples = data[5]

    if version not in (1, 2) or stype not in (0, 1):
        return None

    header = {
        'magic': 'SPS',
        'version': version,
        'type': stype,
        'num_samples': num_samples,
        'samples': [],
    }

    for i in range(num_samples):
        off = 6 + i * 32
        if off + 32 > len(data):
            break
        entry = data[off:off + 32]
        name_raw = entry[0:10]
        name = name_raw.split(b'\x00')[0].decode('ascii', errors='replace').strip()
        if not name:
            name = f'sample_{i}'

        f0 = read_be_u16(entry, 10)   # data offset (low 16 bits)
        f1 = read_be_u16(entry, 12)   # reserved (always 0)
        f2 = read_be_u16(entry, 14)   # data length in bytes/samples
        f3 = read_be_u16(entry, 16)   # page (offset high bits, informational)
        f4 = read_be_u16(entry, 18)   # loop start (low 16 bits)
        f5 = read_be_u16(entry, 20)   # reserved
        f6 = read_be_u16(entry, 22)   # loop length
        f7 = read_be_u16(entry, 24)   # volume (0-64)
        f8 = read_be_u16(entry, 26)   # finetune/flags
        f9 = read_be_u16(entry, 28)   # reserved
        f10 = read_be_u16(entry, 30)  # reserved

        header['samples'].append({
            'name': name,
            'name_raw': name_raw,
            'offset_lo': f0,
            'length': f2,
            'page': f3,
            'loop_start_lo': f4,
            'loop_length': f6,
            'volume': f7,
            'finetune': f8,
            'reserved1': f1,
            'reserved2': f5,
            'reserved3': f9,
            'reserved4': f10,
        })

    header['header_size'] = 6 + num_samples * 32
    return header


def decompress_delta_huffman(data, psn_offset):
    """Decompress DeltaHuffMan compressed audio data from the PSN section."""
    # Read PSN header
    tag = data[psn_offset:psn_offset + 3]
    if tag != b'psn':
        raise ValueError(f"Expected 'psn' tag, got {tag!r}")

    flag_byte = data[psn_offset + 3]
    decomp_size = read_be_u32(data, psn_offset + 4)
    num_symbols = flag_byte + 1

    pos = psn_offset + 8

    # Read Huffman table entries
    codes = []  # list of (symbol, code_length, code_bits)
    for _ in range(num_symbols):
        if pos + 2 > len(data):
            break
        symbol = data[pos]
        code_length = data[pos + 1]
        pos += 2

        # Number of code bytes: (code_length >> 3) clamped to 0-3, plus 1
        num_code_bytes = min(code_length >> 3, 3) + 1
        if pos + num_code_bytes > len(data):
            break

        # Read code bits in big-endian order
        code_bits = 0
        for j in range(num_code_bytes):
            code_bits = (code_bits << 8) | data[pos + j]
        pos += num_code_bytes

        codes.append((symbol, code_length, code_bits))

    # Align to even byte boundary
    if pos & 1:
        pos += 1

    # Build Huffman tree from codes
    # Tree node: [left_child, right_child, leaf_value]
    # left_child/right_child are either None (leaf) or another node
    # For a leaf, left_child is None and leaf_value is the delta symbol
    root = [None, None, None]

    for symbol, code_length, code_bits in codes:
        if code_length == 0:
            continue
        node = root
        # Navigate/build tree based on code bits
        # Bits are stored LSB-first in the code (bit 0 = root decision)
        # In the bitstream, they're read MSB-first from 16-bit words
        # Bit=1 in stream → left child (offset 0), bit=0 → right child (offset 4)
        for bit_idx in range(code_length):
            bit = (code_bits >> bit_idx) & 1
            if bit == 1:
                # Left child (bit=1 in stream, carry set)
                if node[0] is None:
                    node[0] = [None, None, None]
                node = node[0]
            else:
                # Right child (bit=0 in stream, carry clear)
                if node[1] is None:
                    node[1] = [None, None, None]
                node = node[1]
        # Mark as leaf with the symbol value
        node[2] = symbol

    # Decode the Huffman bitstream
    output = bytearray()
    accumulator = 0  # Delta accumulator (wrapping byte)

    # Read 16-bit words from pos, decode bits MSB-first
    bit_buffer = 0
    bits_remaining = 0

    while len(output) < decomp_size:
        # Read next word if needed
        if bits_remaining == 0:
            if pos + 2 > len(data):
                break
            bit_buffer = read_be_u16(data, pos)
            pos += 2
            bits_remaining = 16

        # Traverse Huffman tree
        node = root
        while node[0] is not None or node[1] is not None:
            if bits_remaining == 0:
                if pos + 2 > len(data):
                    break
                bit_buffer = read_be_u16(data, pos)
                pos += 2
                bits_remaining = 16

            # Read one bit (MSB first)
            bit = (bit_buffer >> 15) & 1
            bit_buffer = (bit_buffer << 1) & 0xFFFF
            bits_remaining -= 1

            if bit == 1:
                node = node[0] if node[0] is not None else node
            else:
                node = node[1] if node[1] is not None else node

        if node[2] is None:
            break

        # Apply delta
        delta = node[2]
        if delta > 127:
            delta -= 256  # Convert to signed
        accumulator = (accumulator + delta) & 0xFF
        output.append(accumulator)

    return bytes(output)


def extract_samples(data, header):
    """Extract individual audio samples from the decoded audio data."""
    samples = []
    cum_offset = 0

    for samp in header['samples']:
        length = samp['length']
        if length == 0:
            samples.append(b'')
            continue

        if cum_offset + length > len(data):
            # Truncate if necessary
            length = max(0, len(data) - cum_offset)

        audio = data[cum_offset:cum_offset + length]
        samples.append(audio)
        cum_offset += samp['length']  # Use original length for offset calculation

    return samples


def write_wav(filename, audio_data, sample_rate=SAMPLE_RATE):
    """Write 8-bit signed PCM data as a WAV file."""
    # WAV uses unsigned 8-bit, so convert signed to unsigned
    unsigned = bytes([(b + 128) & 0xFF if b < 128 else b - 128 for b in audio_data])
    # Actually: the data is stored as unsigned bytes where 0x00=-128, 0x80=0, 0xFF=+127
    # For WAV 8-bit unsigned: 0=min, 128=center, 255=max
    # Our data: if value < 128, it's positive (0-127), add 128 → 128-255
    #           if value >= 128, it's negative (-128 to -1), add 128 → 0-127
    # Actually simpler: just XOR with 0x80 or add 128 mod 256
    unsigned = bytes([(b ^ 0x80) for b in audio_data])

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(1)
        wf.setframerate(sample_rate)
        wf.writeframes(unsigned)


def convert_sps(input_file, output_dir):
    """Convert an SPS file to WAV files."""
    data = open(input_file, 'rb').read()
    header = parse_sps_header(data)
    if header is None:
        print(f"  ERROR: Not a valid SPS file: {input_file}")
        return []

    os.makedirs(output_dir, exist_ok=True)
    basename = os.path.splitext(os.path.basename(input_file))[0]

    # Determine audio data location
    header_end = header['header_size']
    results = []

    if header['type'] == 0:
        # Type 0: raw 8-bit signed PCM after header
        audio_data = data[header_end:]
    elif header['type'] == 1:
        # Type 1: DeltaHuffMan compressed with PSN section
        try:
            audio_data = decompress_delta_huffman(data, header_end)
        except Exception as e:
            print(f"  ERROR decompressing {input_file}: {e}")
            return []
    else:
        print(f"  ERROR: Unknown type {header['type']} in {input_file}")
        return []

    # Extract individual samples
    sample_audios = extract_samples(audio_data, header)

    for i, (samp, audio) in enumerate(zip(header['samples'], sample_audios)):
        if len(audio) == 0:
            continue

        # Sanitize filename
        safe_name = ''.join(c if c.isalnum() or c in '-_.' else '_' for c in samp['name'])
        if not safe_name:
            safe_name = f'sample_{i}'
        wav_filename = f"{i:02d}_{safe_name}.wav"
        wav_path = os.path.join(output_dir, wav_filename)

        write_wav(wav_path, audio)
        results.append({
            'index': i,
            'name': samp['name'],
            'filename': wav_filename,
            'length': len(audio),
            'volume': samp['volume'],
            'loop_length': samp['loop_length'],
        })
        print(f"  Wrote {wav_filename} ({len(audio)} samples, {len(audio)/SAMPLE_RATE:.2f}s)")

    return results


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>")
        print("  Converts StoneTracker Sample (SPS) files to WAV")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(input_file):
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)

    print(f"Converting: {input_file}")
    results = convert_sps(input_file, output_dir)
    if results:
        print(f"Successfully extracted {len(results)} sample(s) to {output_dir}/")
    else:
        print("No samples extracted.")


if __name__ == '__main__':
    main()

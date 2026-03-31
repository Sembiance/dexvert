#!/usr/bin/env python3
# Vibe coded by Claude

"""
Extractor for Yu-Gi-Oh! Power of Chaos KCEJYUGI archive files (Data.dat, Voice.dat).
Handles both compressed (LZSS) and uncompressed entries.

Usage: python3 unYuGiOhData.py <inputFile> <outputDir>
"""

import struct
import sys
import os


def decrypt_filename(enc_bytes):
    """Decrypt a filename by rotating each byte right by 4 bits (nibble swap)."""
    decrypted = bytearray(len(enc_bytes))
    for i, b in enumerate(enc_bytes):
        decrypted[i] = ((b >> 4) | (b << 4)) & 0xFF
    return bytes(decrypted).split(b'\x00')[0].decode('ascii')


def lzss_decompress(data, uncompressed_size):
    """
    Decompress LZSS data using a 4096-byte ring buffer.

    Ring buffer initialized to 0x00, initial write position at 0xFEE.
    Flag byte controls 8 items (LSB first):
      - bit=1: literal byte
      - bit=0: 2-byte back-reference
        - ring_position = b1 | ((b2 & 0xF0) << 4)  [12 bits]
        - copy_length   = (b2 & 0x0F) + 3           [3..18]
    """
    RING_SIZE = 4096
    RING_MASK = RING_SIZE - 1
    ring = bytearray(RING_SIZE)
    ring_pos = 0xFEE

    output = bytearray()
    pos = 0

    while pos < len(data) and len(output) < uncompressed_size:
        flag = data[pos]
        pos += 1

        for bit in range(8):
            if len(output) >= uncompressed_size:
                break

            if flag & (1 << bit):
                # Literal byte
                byte = data[pos]
                pos += 1
                output.append(byte)
                ring[ring_pos] = byte
                ring_pos = (ring_pos + 1) & RING_MASK
            else:
                # Back-reference
                b1 = data[pos]
                b2 = data[pos + 1]
                pos += 2
                ref_pos = b1 | ((b2 & 0xF0) << 4)
                ref_len = (b2 & 0x0F) + 3

                for _ in range(ref_len):
                    byte = ring[ref_pos & RING_MASK]
                    output.append(byte)
                    ring[ring_pos] = byte
                    ring_pos = (ring_pos + 1) & RING_MASK
                    ref_pos += 1

    return bytes(output[:uncompressed_size])


def extract_archive(input_path, output_dir):
    file_size = os.path.getsize(input_path)

    with open(input_path, 'rb') as f:
        # Read and validate header
        magic = f.read(8)
        if magic != b'KCEJYUGI':
            print(f"Error: invalid magic {magic!r}, expected b'KCEJYUGI'", file=sys.stderr)
            sys.exit(1)

        file_count = struct.unpack('<I', f.read(4))[0]
        print(f"Archive: {os.path.basename(input_path)}")
        print(f"Files:   {file_count}")
        print(f"Size:    {file_size:,} bytes")
        print()

        # Read file table
        entries = []
        for i in range(file_count):
            enc_name = f.read(256)
            name = decrypt_filename(enc_name)
            data_offset = struct.unpack('<I', f.read(4))[0]
            uncompressed_size = struct.unpack('<I', f.read(4))[0]
            stored_size = struct.unpack('<I', f.read(4))[0]
            entries.append((name, data_offset, uncompressed_size, stored_size))

        # Extract each file
        for i, (name, data_offset, uncompressed_size, stored_size) in enumerate(entries):
            # Convert backslashes to OS path separator
            os_name = name.replace('\\', os.sep)
            out_path = os.path.join(output_dir, os_name)

            # Create directories
            out_dir = os.path.dirname(out_path)
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)

            # Read stored data
            f.seek(data_offset)
            stored_data = f.read(stored_size)

            # Decompress if needed
            if stored_size == 0:
                file_data = b''
            elif uncompressed_size == stored_size:
                file_data = stored_data
            else:
                file_data = lzss_decompress(stored_data, uncompressed_size)

            # Write output file
            with open(out_path, 'wb') as out_f:
                out_f.write(file_data)

            compressed_tag = ""
            if stored_size != uncompressed_size and stored_size > 0:
                ratio = uncompressed_size / stored_size
                compressed_tag = f" (LZSS {ratio:.1f}x)"
            elif stored_size == 0:
                compressed_tag = " (empty)"

            print(f"  [{i + 1:4d}/{file_count}] {name}{compressed_tag}")

    print()
    print(f"Extracted {file_count} files to {output_dir}")


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(input_path):
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    extract_archive(input_path, output_dir)


if __name__ == '__main__':
    main()

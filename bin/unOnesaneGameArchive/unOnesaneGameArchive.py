#!/usr/bin/env python3
# Vibe coded by Claude
#
# onesaneGameArchive.py - Extractor for 1nsane game IDF archive files
#
# Usage: onesaneGameArchive.py <inputFile> <outputDir>

import struct
import sys
import os


def decrypt_toc(toc_data, key_byte):
    """Decrypt TOC entries using the rolling XOR cipher.

    Algorithm:
        k = (0x27 + key_byte) & 0xFF
        For each byte i:
            decrypted[i] = encrypted[i] XOR k
            k = (decrypted[i] + i + k * 5) & 0xFF
    """
    k = (0x27 + key_byte) & 0xFF
    decrypted = bytearray(len(toc_data))
    for i in range(len(toc_data)):
        dec_byte = toc_data[i] ^ k
        decrypted[i] = dec_byte
        k = (dec_byte + i + (k * 5)) & 0xFF
    return decrypted


def extract_idf(input_path, output_dir):
    with open(input_path, "rb") as f:
        data = f.read()

    fsize = len(data)
    if fsize < 20:
        print(f"ERROR: File too small ({fsize} bytes)", file=sys.stderr)
        sys.exit(1)

    # Parse header (20 bytes)
    magic = data[0:4]
    if magic != b"FFFL":
        print(f"ERROR: Invalid magic: {magic!r} (expected b'FFFL')", file=sys.stderr)
        sys.exit(1)

    header_extra_size = struct.unpack_from("<I", data, 4)[0]
    if header_extra_size != 12:
        print(f"WARNING: Unexpected header extra size: {header_extra_size} (expected 12)", file=sys.stderr)

    file_type = struct.unpack_from("<I", data, 8)[0]
    raw_toc_offset = struct.unpack_from("<I", data, 12)[0]
    enc_key = struct.unpack_from("<I", data, 16)[0]

    # Determine if TOC is encrypted
    if file_type == 0x00010100:
        encrypted = True
        toc_offset = raw_toc_offset ^ 0x123
        key_byte = enc_key & 0xFF
    elif file_type == 0x00010000:
        encrypted = False
        toc_offset = raw_toc_offset
    else:
        print(f"ERROR: Unknown file type: 0x{file_type:08X}", file=sys.stderr)
        sys.exit(1)

    if toc_offset + 8 > fsize:
        print(f"ERROR: TOC offset {toc_offset} exceeds file size {fsize}", file=sys.stderr)
        sys.exit(1)

    # Read entry count (stored before and after the TOC entries)
    entry_count = struct.unpack_from("<I", data, toc_offset)[0]
    trailing_count = struct.unpack_from("<I", data, fsize - 4)[0]

    if entry_count != trailing_count:
        print(f"WARNING: Entry count mismatch: {entry_count} vs trailing {trailing_count}", file=sys.stderr)

    expected_size = toc_offset + 4 + entry_count * 64 + 4
    if expected_size != fsize:
        print(f"ERROR: File size mismatch: expected {expected_size}, actual {fsize}", file=sys.stderr)
        sys.exit(1)

    # Read and decrypt TOC entries
    toc_raw = data[toc_offset + 4 : toc_offset + 4 + entry_count * 64]
    if encrypted:
        toc_entries = decrypt_toc(toc_raw, key_byte)
    else:
        toc_entries = bytearray(toc_raw)

    # Parse and extract each file
    os.makedirs(output_dir, exist_ok=True)
    archive_name = os.path.basename(input_path)

    print(f"Archive: {archive_name}")
    print(f"Type: {'encrypted' if encrypted else 'plaintext'} TOC")
    print(f"Files: {entry_count}")
    print()

    for i in range(entry_count):
        entry = toc_entries[i * 64 : (i + 1) * 64]

        # Parse entry: 56 bytes path + 4 bytes offset + 4 bytes size
        path_raw = entry[:56]
        path_str = path_raw.split(b"\x00")[0].decode("ascii", errors="replace")
        file_offset = struct.unpack_from("<I", entry, 56)[0]
        file_size = struct.unpack_from("<I", entry, 60)[0]

        # Normalize path separators
        rel_path = path_str.replace("\\", os.sep)

        # Create output path
        out_path = os.path.join(output_dir, rel_path)
        out_dir = os.path.dirname(out_path)
        os.makedirs(out_dir, exist_ok=True)

        # Extract file data
        file_data = data[file_offset : file_offset + file_size]
        with open(out_path, "wb") as out_f:
            out_f.write(file_data)

        print(f"  [{i + 1:4d}/{entry_count}] {path_str} ({file_size} bytes)")

    print(f"\nExtracted {entry_count} files to {output_dir}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    output_directory = sys.argv[2]

    if not os.path.isfile(input_file):
        print(f"ERROR: Input file not found: {input_file}", file=sys.stderr)
        sys.exit(1)

    extract_idf(input_file, output_directory)

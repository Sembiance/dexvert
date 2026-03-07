#!/usr/bin/env python3
# Vibe coded by Claude

"""Convert an Elecbyte M.U.G.E.N. Sound file (.snd) to individual WAV files."""

import struct
import sys
import os

SIGNATURE = b"ElecbyteSnd\x00"
HEADER_SIZE = 512


def parse_snd(input_path, output_dir):
    with open(input_path, "rb") as f:
        # Read and validate file header
        header = f.read(HEADER_SIZE)
        if len(header) < HEADER_SIZE:
            print(f"Error: File too small to contain a valid SND header.", file=sys.stderr)
            sys.exit(1)

        sig = header[0:12]
        if sig != SIGNATURE:
            print(f"Error: Invalid signature. Expected 'ElecbyteSnd\\0', got {sig!r}.", file=sys.stderr)
            sys.exit(1)

        version_bytes = header[12:16]
        num_sounds = struct.unpack_from("<I", header, 16)[0]
        first_offset = struct.unpack_from("<I", header, 20)[0]

        # Decode version for display
        ver_u32 = struct.unpack_from("<I", header, 12)[0]
        if ver_u32 <= 0xFF:
            version_str = str(ver_u32)
        else:
            version_str = f"{header[15]}.{header[14]}.{header[13]}.{header[12]}"

        print(f"Signature:    ElecbyteSnd")
        print(f"Version:      {version_str} (bytes: {version_bytes.hex()})")
        print(f"Sounds:       {num_sounds}")
        print(f"First offset: {first_offset:#x}")
        print()

        if num_sounds == 0:
            print("No sounds to extract.")
            return

        os.makedirs(output_dir, exist_ok=True)

        file_size = os.fstat(f.fileno()).st_size
        offset = first_offset
        extracted = 0

        for i in range(num_sounds):
            if offset + 16 > file_size:
                print(f"Warning: Subfile {i} header at offset {offset:#x} exceeds file size. Stopping.", file=sys.stderr)
                break

            f.seek(offset)
            sub_header = f.read(16)
            if len(sub_header) < 16:
                print(f"Warning: Truncated subfile header at offset {offset:#x}. Stopping.", file=sys.stderr)
                break

            next_offset, wav_length, group, sound = struct.unpack("<IIII", sub_header)

            if offset + 16 + wav_length > file_size:
                print(f"Warning: WAV data for subfile {i} (g={group}, s={sound}) exceeds file size. Truncating.", file=sys.stderr)
                wav_length = file_size - offset - 16

            wav_data = f.read(wav_length)

            out_name = os.path.join(output_dir, f"g{group}_s{sound}.wav")
            with open(out_name, "wb") as out_f:
                out_f.write(wav_data)

            print(f"  [{i:3d}] group={group:5d}  sound={sound:3d}  size={wav_length:8d}  -> {out_name}")
            extracted += 1
            offset = next_offset

        print(f"\nExtracted {extracted} sound(s).")


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.snd> <outputDir>", file=sys.stderr)
        print(f"  Extracts all sounds from a M.U.G.E.N. .snd file to individual .wav files.", file=sys.stderr)
        print(f"  Output files are named g<group>_s<sound>.wav", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(input_path):
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    parse_snd(input_path, output_dir)


if __name__ == "__main__":
    main()

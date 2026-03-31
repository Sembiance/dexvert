#!/usr/bin/env python3
# Vibe coded by Claude

"""
dls2wav.py - Extract WAV files from a DLS (Downloadable Sound Bank) file.

Usage: dls2wav.py <input.snd> <outputDir>

Parses the RIFF/DLS structure and extracts each wave sample from the
wvpl (Wave Pool) LIST into individual WAV files.
"""

import struct
import sys
import os


def read_chunk_header(f):
    """Read an 8-byte RIFF chunk header. Returns (tag, size) or (None, 0) at EOF."""
    data = f.read(8)
    if len(data) < 8:
        return None, 0
    tag = data[:4].decode("ascii", errors="replace")
    size = struct.unpack("<I", data[4:8])[0]
    return tag, size


def parse_riff_chunks(f, end):
    """Parse sequential RIFF chunks from current position to end offset.
    Returns a list of (tag, offset_of_data, size, [form_type]) tuples.
    For LIST/RIFF chunks, a 4th element gives the form type.
    """
    chunks = []
    while f.tell() < end:
        chunk_start = f.tell()
        tag, size = read_chunk_header(f)
        if tag is None:
            break
        if tag in ("RIFF", "LIST"):
            form_type = f.read(4).decode("ascii", errors="replace")
            chunks.append((tag, chunk_start, size, form_type))
            # Skip past the content (size includes the 4-byte form type we already read)
            f.seek(chunk_start + 8 + size + (size % 2))
        else:
            data_offset = f.tell()
            chunks.append((tag, data_offset, size))
            f.seek(data_offset + size + (size % 2))
    return chunks


def parse_list_children(f, list_data_offset, list_size):
    """Parse the child chunks inside a LIST or RIFF chunk.
    list_data_offset points right after the form-type (4 bytes into the data).
    list_size is the chunk size from the header (includes the 4-byte form type).
    """
    # The children start after the 4-byte form type
    children_start = list_data_offset
    children_end = list_data_offset + list_size - 4  # -4 for form type already consumed
    f.seek(children_start)
    return parse_riff_chunks(f, children_end)


def read_chunk_data(f, chunk):
    """Read the raw data bytes for a non-LIST/RIFF chunk tuple."""
    _, data_offset, size = chunk[:3]
    f.seek(data_offset)
    return f.read(size)


def parse_fmt(data):
    """Parse a 'fmt ' chunk. Returns dict with audio format fields."""
    if len(data) < 16:
        return None
    format_tag, channels, sample_rate, avg_bytes_per_sec, block_align, bits_per_sample = struct.unpack(
        "<HHIIHH", data[:16]
    )
    result = {
        "format_tag": format_tag,
        "channels": channels,
        "sample_rate": sample_rate,
        "avg_bytes_per_sec": avg_bytes_per_sec,
        "block_align": block_align,
        "bits_per_sample": bits_per_sample,
    }
    # If there are extra format bytes (cbSize field at offset 16)
    if len(data) >= 18:
        cb_size = struct.unpack("<H", data[16:18])[0]
        result["cb_size"] = cb_size
        if len(data) > 18:
            result["extra_bytes"] = data[18 : 18 + cb_size]
    return result


def parse_info_list(f, list_chunk):
    """Parse an INFO LIST chunk into a dict of tag -> string value."""
    _, chunk_start, size, form_type = list_chunk
    children_start = chunk_start + 12  # 8 header + 4 form type
    info = {}
    f.seek(children_start)
    children = parse_riff_chunks(f, children_start + size - 4)
    for child in children:
        tag = child[0]
        data = read_chunk_data(f, child)
        # INFO strings are null-terminated
        text = data.rstrip(b"\x00").decode("ascii", errors="replace")
        info[tag] = text
    return info


def write_wav(filepath, fmt_info, pcm_data):
    """Write a standard WAV file from format info and raw PCM data."""
    channels = fmt_info["channels"]
    sample_rate = fmt_info["sample_rate"]
    bits_per_sample = fmt_info["bits_per_sample"]
    block_align = fmt_info["block_align"]
    avg_bytes_per_sec = fmt_info["avg_bytes_per_sec"]
    format_tag = fmt_info["format_tag"]

    # fmt chunk data
    fmt_data = struct.pack(
        "<HHIIHH",
        format_tag,
        channels,
        sample_rate,
        avg_bytes_per_sec,
        block_align,
        bits_per_sample,
    )

    data_size = len(pcm_data)
    # RIFF header: 4 (WAVE) + 8 (fmt hdr) + len(fmt_data) + 8 (data hdr) + data_size
    riff_size = 4 + 8 + len(fmt_data) + 8 + data_size

    with open(filepath, "wb") as out:
        out.write(b"RIFF")
        out.write(struct.pack("<I", riff_size))
        out.write(b"WAVE")
        # fmt chunk
        out.write(b"fmt ")
        out.write(struct.pack("<I", len(fmt_data)))
        out.write(fmt_data)
        # data chunk
        out.write(b"data")
        out.write(struct.pack("<I", data_size))
        out.write(pcm_data)


def extract_wave_name(f, wave_chunk):
    """Try to extract a name from an INFO list inside a wave chunk."""
    _, chunk_start, size, form_type = wave_chunk
    children_start = chunk_start + 12
    f.seek(children_start)
    children = parse_riff_chunks(f, children_start + size - 4)
    for child in children:
        if len(child) == 4 and child[0] == "LIST" and child[3] == "INFO":
            info = parse_info_list(f, child)
            name = info.get("INAM", "").strip()
            if name:
                return name
    return None


def extract_wave(f, wave_chunk, index, output_dir):
    """Extract a single wave from a LIST/wave chunk and write it as a WAV file."""
    _, chunk_start, size, form_type = wave_chunk
    children_start = chunk_start + 12
    f.seek(children_start)
    children = parse_riff_chunks(f, children_start + size - 4)

    fmt_info = None
    pcm_data = None
    wave_name = None

    for child in children:
        tag = child[0]
        if tag == "fmt ":
            fmt_info = parse_fmt(read_chunk_data(f, child))
        elif tag == "data":
            pcm_data = read_chunk_data(f, child)
        elif len(child) == 4 and tag == "LIST" and child[3] == "INFO":
            info = parse_info_list(f, child)
            wave_name = info.get("INAM", "").strip()

    if fmt_info is None or pcm_data is None:
        print(f"  WARNING: Wave {index} missing fmt or data chunk, skipping")
        return

    # Build filename
    if wave_name:
        # Sanitize the name for filesystem use
        safe_name = "".join(c if c.isalnum() or c in " _-." else "_" for c in wave_name).strip()
        if not safe_name:
            safe_name = f"wave_{index:04d}"
        filename = f"{index:04d}_{safe_name}.wav"
    else:
        filename = f"wave_{index:04d}.wav"

    filepath = os.path.join(output_dir, filename)
    write_wav(filepath, fmt_info, pcm_data)

    rate = fmt_info["sample_rate"]
    bits = fmt_info["bits_per_sample"]
    ch = fmt_info["channels"]
    samples = len(pcm_data) // fmt_info["block_align"]
    duration = samples / rate if rate else 0
    print(f"  [{index:4d}] {filename} ({rate}Hz {bits}bit {ch}ch, {duration:.2f}s, {len(pcm_data)} bytes)")


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.snd> <outputDir>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(input_path):
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    with open(input_path, "rb") as f:
        # Read RIFF header
        tag, riff_size = read_chunk_header(f)
        if tag != "RIFF":
            print(f"Error: Not a RIFF file (got '{tag}')")
            sys.exit(1)

        form_type = f.read(4).decode("ascii", errors="replace")
        if form_type != "DLS ":
            print(f"Error: Not a DLS file (form type '{form_type}')")
            sys.exit(1)

        file_size = os.path.getsize(input_path)
        print(f"DLS file: {input_path} ({file_size} bytes)")
        print(f"RIFF size: {riff_size}")

        # Parse top-level chunks
        top_chunks = parse_riff_chunks(f, 12 + riff_size - 4)

        # Display top-level info
        for chunk in top_chunks:
            tag = chunk[0]
            if tag == "colh":
                data = read_chunk_data(f, chunk)
                num_instruments = struct.unpack("<I", data[:4])[0]
                print(f"Instruments (colh): {num_instruments}")
            elif tag == "vers":
                data = read_chunk_data(f, chunk)
                ver_ms, ver_ls = struct.unpack("<II", data[:8])
                major = ver_ms >> 16
                minor = ver_ms & 0xFFFF
                build_major = ver_ls >> 16
                build_minor = ver_ls & 0xFFFF
                print(f"Version: {major}.{minor}.{build_major}.{build_minor}")
            elif tag == "dlid":
                data = read_chunk_data(f, chunk)
                print(f"DLID (GUID): {data.hex()}")
            elif tag == "msyn":
                data = read_chunk_data(f, chunk)
                val = struct.unpack("<I", data[:4])[0]
                print(f"MSynthesis hardware: {val}")
            elif tag == "ptbl":
                data = read_chunk_data(f, chunk)
                cb_size = struct.unpack("<I", data[:4])[0]
                num_cues = struct.unpack("<I", data[4:8])[0]
                print(f"Pool Table: {num_cues} wave entries")

        # Find the wvpl LIST (wave pool)
        wvpl_chunk = None
        lins_chunk = None
        info_chunk = None
        for chunk in top_chunks:
            if len(chunk) == 4:
                tag, _, _, form_type = chunk
                if tag == "LIST" and form_type == "wvpl":
                    wvpl_chunk = chunk
                elif tag == "LIST" and form_type == "lins":
                    lins_chunk = chunk
                elif tag == "LIST" and form_type == "INFO":
                    info_chunk = chunk

        # Print bank-level INFO
        if info_chunk:
            info = parse_info_list(f, info_chunk)
            if info:
                print("Bank info:")
                for k, v in info.items():
                    if v:
                        print(f"  {k}: {v}")

        # Print instrument summary
        if lins_chunk:
            _, chunk_start, size, _ = lins_chunk
            children_start = chunk_start + 12
            f.seek(children_start)
            ins_chunks = parse_riff_chunks(f, children_start + size - 4)
            ins_list = [c for c in ins_chunks if len(c) == 4 and c[0] == "LIST" and c[3] == "ins "]
            print(f"\nInstruments found: {len(ins_list)}")
            for i, ins in enumerate(ins_list):
                _, ins_start, ins_size, _ = ins
                ins_children_start = ins_start + 12
                f.seek(ins_children_start)
                ins_children = parse_riff_chunks(f, ins_children_start + ins_size - 4)

                ins_name = ""
                bank_num = 0
                program_num = 0
                num_regions = 0

                for child in ins_children:
                    if child[0] == "insh":
                        data = read_chunk_data(f, child)
                        num_regions, bank_num, program_num = struct.unpack("<III", data[:12])
                    elif len(child) == 4 and child[0] == "LIST" and child[3] == "INFO":
                        info = parse_info_list(f, child)
                        ins_name = info.get("INAM", "")

                msb = (bank_num >> 8) & 0x7F
                lsb = bank_num & 0x7F
                is_drum = (bank_num >> 31) & 1
                kind = "drum" if is_drum else "melodic"
                print(
                    f"  [{i:3d}] Bank {msb}:{lsb} Program {program_num} "
                    f"({kind}, {num_regions} regions) {ins_name}"
                )

        # Extract waves
        if wvpl_chunk is None:
            print("Error: No wvpl (Wave Pool) LIST found in DLS file")
            sys.exit(1)

        _, wvpl_start, wvpl_size, _ = wvpl_chunk
        wvpl_children_start = wvpl_start + 12
        f.seek(wvpl_children_start)
        wave_chunks = parse_riff_chunks(f, wvpl_children_start + wvpl_size - 4)
        wave_list = [c for c in wave_chunks if len(c) == 4 and c[0] == "LIST" and c[3] == "wave"]

        print(f"\nExtracting {len(wave_list)} waves to: {output_dir}")
        for i, wave_chunk in enumerate(wave_list):
            extract_wave(f, wave_chunk, i, output_dir)

    print("\nDone.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# Vibe coded by Claude
#
# undiskcopy.py - Convert MacBinary-wrapped NDIF (Apple Disk Copy 6) images to raw disk images
#
# Usage: undiskcopy.py <input.bin> <output.img>
#
# Supports: MacBinary II/III wrapped NDIF images with RAW, ZERO, and ADC compressed blocks.
# Produces: Raw disk images suitable for use with hmount, hfsexplorer, 7-zip, etc.

import struct
import sys
import os

# NDIF block types (stored as signed byte in bcem entries)
NDIF_ZERO = 0        # Zero-filled sectors
NDIF_RAW = 2         # Uncompressed raw data
NDIF_KENCODE = 128   # KenCode compressed (0x80, signed = -128)
NDIF_ADC = 131       # ADC compressed (0x83, signed = -125)
NDIF_TERM = 255      # Terminator (0xFF, signed = -1)

TYPE_NAMES = {
    NDIF_ZERO: "ZERO",
    NDIF_RAW: "RAW",
    NDIF_KENCODE: "KENCODE",
    NDIF_ADC: "ADC",
    NDIF_TERM: "TERM",
}


def adc_decompress(input_data, expected_size):
    """Decompress Apple Data Compression (ADC) data.

    ADC is an LZ77-variant with three opcodes:
      0x80-0xFF: Literal copy, length = (byte & 0x7F) + 1
      0x40-0x7F: 3-byte back-reference, length = (byte & 0x3F) + 4, 16-bit offset
      0x00-0x3F: 2-byte back-reference, length = ((byte & 0x3F) >> 2) + 3, 10-bit offset
    """
    out = bytearray(expected_size)
    inp = 0
    outp = 0
    in_len = len(input_data)

    while inp < in_len and outp < expected_size:
        byte = input_data[inp]

        if byte & 0x80:
            # PLAIN: literal copy
            chunk_size = (byte & 0x7F) + 1
            end = outp + chunk_size
            if end > expected_size:
                chunk_size = expected_size - outp
                end = expected_size
            out[outp:end] = input_data[inp + 1:inp + 1 + chunk_size]
            inp += chunk_size + 1
            outp = end

        elif byte & 0x40:
            # THREEBYTE: back-reference with 16-bit offset
            chunk_size = (byte & 0x3F) + 4
            offset = (input_data[inp + 1] << 8) | input_data[inp + 2]
            inp += 3
            src = outp - offset - 1
            for _ in range(chunk_size):
                if outp >= expected_size:
                    break
                out[outp] = out[src]
                outp += 1
                src += 1

        else:
            # TWOBYTE: back-reference with 10-bit offset
            chunk_size = ((byte & 0x3F) >> 2) + 3
            offset = ((byte & 0x03) << 8) | input_data[inp + 1]
            inp += 2
            src = outp - offset - 1
            for _ in range(chunk_size):
                if outp >= expected_size:
                    break
                out[outp] = out[src]
                outp += 1
                src += 1

    if outp != expected_size:
        raise ValueError(f"ADC decompression size mismatch: got {outp}, expected {expected_size}")

    return bytes(out)


def parse_macbinary(f):
    """Parse MacBinary header and return data fork/resource fork positions and sizes."""
    hdr = f.read(128)
    if len(hdr) < 128:
        raise ValueError("File too small for MacBinary header")

    version = hdr[0]
    namelen = hdr[1]

    if version != 0 or namelen < 1 or namelen > 63:
        raise ValueError("Not a valid MacBinary file")

    name = hdr[2:2 + namelen].decode('macroman', errors='replace')
    ftype = hdr[65:69].decode('macroman', errors='replace')
    creator = hdr[69:73].decode('macroman', errors='replace')
    data_len = struct.unpack('>I', hdr[83:87])[0]
    rsrc_len = struct.unpack('>I', hdr[87:91])[0]

    # Check for mBIN signature (MacBinary III) or valid structure
    mb3_sig = hdr[102:106]
    is_mb3 = mb3_sig == b'mBIN'

    data_start = 128
    data_padded = data_len + (128 - data_len % 128) % 128
    rsrc_start = data_start + data_padded

    print(f"  MacBinary {'III' if is_mb3 else 'II'}: name='{name}' type='{ftype}' creator='{creator}'")
    print(f"  Data fork: {data_len:,} bytes at offset {data_start}")
    print(f"  Resource fork: {rsrc_len:,} bytes at offset {rsrc_start:,}")

    if ftype != 'rohd':
        raise ValueError(f"Unexpected file type '{ftype}' (expected 'rohd' for NDIF)")

    if rsrc_len == 0:
        raise ValueError("No resource fork found - cannot read NDIF block map")

    return name, data_start, data_len, rsrc_start, rsrc_len


def parse_resource_fork(rsrc_data):
    """Parse a Mac resource fork and return the bcem resource data (ID 128)."""
    rsrc_data_offset = struct.unpack('>I', rsrc_data[0:4])[0]
    rsrc_map_offset = struct.unpack('>I', rsrc_data[4:8])[0]

    map_data = rsrc_data[rsrc_map_offset:]
    type_list_offset = struct.unpack('>H', map_data[24:26])[0]
    type_list_data = map_data[type_list_offset:]
    num_types = struct.unpack('>h', type_list_data[0:2])[0] + 1

    off = 2
    for _ in range(num_types):
        rtype = type_list_data[off:off + 4].decode('macroman', errors='replace')
        rcount = struct.unpack('>H', type_list_data[off + 4:off + 6])[0] + 1
        ref_offset = struct.unpack('>H', type_list_data[off + 6:off + 8])[0]

        if rtype == 'bcem':
            ref_data = map_data[type_list_offset + ref_offset:]
            for j in range(rcount):
                rid = struct.unpack('>H', ref_data[j * 12:j * 12 + 2])[0]
                doff = (ref_data[j * 12 + 5] << 16) | (ref_data[j * 12 + 6] << 8) | ref_data[j * 12 + 7]
                actual_offset = rsrc_data_offset + doff
                data_size = struct.unpack('>I', rsrc_data[actual_offset:actual_offset + 4])[0]
                if rid == 128:
                    return rsrc_data[actual_offset + 4:actual_offset + 4 + data_size]

        off += 8

    raise ValueError("No 'bcem' resource (ID 128) found in resource fork")


def parse_bcem(bcem_data):
    """Parse the NDIF bcem block map header and entries."""
    if len(bcem_data) < 128:
        raise ValueError(f"bcem resource too small: {len(bcem_data)} bytes")

    # Parse 128-byte header
    version_major = struct.unpack('>H', bcem_data[0:2])[0]
    version_minor = struct.unpack('>H', bcem_data[2:4])[0]
    img_namelen = bcem_data[4]
    img_name = bcem_data[5:5 + img_namelen].decode('macroman', errors='replace')

    hdr_off = 68  # After 2+2+1+63 bytes
    num_sectors = struct.unpack('>I', bcem_data[hdr_off:hdr_off + 4])[0]
    chunk_size = struct.unpack('>I', bcem_data[hdr_off + 4:hdr_off + 8])[0]
    backing_offset = struct.unpack('>I', bcem_data[hdr_off + 8:hdr_off + 12])[0]
    crc32_val = struct.unpack('>I', bcem_data[hdr_off + 12:hdr_off + 16])[0]
    is_segmented = struct.unpack('>I', bcem_data[hdr_off + 16:hdr_off + 20])[0]
    num_blocks = struct.unpack('>I', bcem_data[hdr_off + 56:hdr_off + 60])[0]

    print(f"  NDIF version: {version_major}.{version_minor}")
    print(f"  Image name: '{img_name}'")
    print(f"  Total sectors: {num_sectors:,} ({num_sectors * 512 / 1024 / 1024:.1f} MB)")
    print(f"  Chunk size: {chunk_size} sectors")
    print(f"  Backing offset: {backing_offset}")
    print(f"  CRC32: 0x{crc32_val:08x}")
    print(f"  Segmented: {is_segmented}")
    print(f"  Block entries: {num_blocks}")

    if is_segmented:
        raise ValueError("Segmented NDIF images are not supported")

    # Verify data size
    expected_data = 128 + num_blocks * 12
    if len(bcem_data) < expected_data:
        raise ValueError(f"bcem resource truncated: {len(bcem_data)} < {expected_data}")

    # Parse 12-byte block entries
    entries = []
    for i in range(num_blocks):
        raw = bcem_data[128 + i * 12:128 + (i + 1) * 12]
        sector = (raw[0] << 16) | (raw[1] << 8) | raw[2]
        btype = raw[3]  # unsigned for comparison
        offset = struct.unpack('>I', raw[4:8])[0]
        length = struct.unpack('>I', raw[8:12])[0]
        entries.append((sector, btype, offset, length))

    # Validate last entry is TERM
    if entries[-1][1] != NDIF_TERM:
        raise ValueError(f"Last block entry is not TERM (type={entries[-1][1]})")

    if entries[-1][0] != num_sectors:
        raise ValueError(f"TERM sector {entries[-1][0]} != total sectors {num_sectors}")

    # Count block types
    type_counts = {}
    for _, btype, _, _ in entries:
        tname = TYPE_NAMES.get(btype, f"UNKNOWN({btype})")
        type_counts[tname] = type_counts.get(tname, 0) + 1
    print(f"  Block types: {type_counts}")

    return num_sectors, backing_offset, entries


def convert_ndif(input_path, output_path):
    """Convert a MacBinary-wrapped NDIF image to a raw disk image."""
    file_size = os.path.getsize(input_path)
    print(f"Input: {input_path} ({file_size:,} bytes)")

    with open(input_path, 'rb') as f:
        # Step 1: Parse MacBinary header
        name, data_start, data_len, rsrc_start, rsrc_len = parse_macbinary(f)

        # Step 2: Read and parse resource fork
        f.seek(rsrc_start)
        rsrc_data = f.read(rsrc_len)
        bcem_data = parse_resource_fork(rsrc_data)

        # Step 3: Parse bcem block map
        num_sectors, backing_offset, entries = parse_bcem(bcem_data)

        total_size = num_sectors * 512
        print(f"\nConverting to raw image: {total_size:,} bytes ({total_size / 1024 / 1024:.1f} MB)")

        # Step 4: Convert blocks and write output
        with open(output_path, 'wb') as out:
            num_data_blocks = len(entries) - 1  # Exclude TERM entry
            blocks_done = 0

            for i in range(num_data_blocks):
                sector, btype, offset, length = entries[i]
                next_sector = entries[i + 1][0]
                block_sectors = next_sector - sector
                block_bytes = block_sectors * 512

                if btype == NDIF_ZERO:
                    out.write(b'\x00' * block_bytes)

                elif btype == NDIF_RAW:
                    f.seek(data_start + offset)
                    raw_data = f.read(length)
                    if len(raw_data) != length:
                        raise ValueError(f"Block {i}: short read ({len(raw_data)}/{length})")
                    out.write(raw_data)
                    # Pad if raw data is shorter than the sector span
                    if length < block_bytes:
                        out.write(b'\x00' * (block_bytes - length))

                elif btype == NDIF_ADC:
                    f.seek(data_start + backing_offset + offset)
                    compressed = f.read(length)
                    if len(compressed) != length:
                        raise ValueError(f"Block {i}: short read ({len(compressed)}/{length})")
                    decompressed = adc_decompress(compressed, block_bytes)
                    out.write(decompressed)

                elif btype == NDIF_KENCODE:
                    raise ValueError(f"Block {i}: KenCode compression is not supported")

                elif btype == NDIF_TERM:
                    break

                else:
                    raise ValueError(f"Block {i}: unknown type {btype}")

                blocks_done += 1
                if blocks_done % 100 == 0 or blocks_done == num_data_blocks:
                    pct = blocks_done / num_data_blocks * 100
                    written = out.tell()
                    print(f"\r  Progress: {blocks_done}/{num_data_blocks} blocks ({pct:.0f}%) - {written / 1024 / 1024:.0f} MB written", end='', flush=True)

            print()

        actual_size = os.path.getsize(output_path)
        if actual_size != total_size:
            print(f"WARNING: Output size {actual_size:,} != expected {total_size:,}")
        else:
            print(f"Output: {output_path} ({actual_size:,} bytes) - OK")


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.bin> <output.img>")
        print()
        print("Convert MacBinary-wrapped NDIF (Apple Disk Copy 6) images to raw disk images.")
        print("The raw output can be used with hmount, hfsexplorer, 7-zip, etc.")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    if not os.path.exists(input_path):
        print(f"Error: input file not found: {input_path}")
        sys.exit(1)

    convert_ndif(input_path, output_path)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# Vibe coded by Codex
"""Convert EZ-DisKlone Plus FDF files to headerless raw floppy images.

Usage: python3 floppyDiskFile.py input.fdf output.img

Requires only Python 3.8+ and its standard library. Format references:
http://fileformats.archiveteam.org/wiki/FDF_Image
https://github.com/86Box/86Box/blob/master/src/floppy/fdd_img.c
"""

import argparse
import os
from pathlib import Path
import struct
import sys
import tempfile


SIGNATURE = b"\x1aFDF"
HEADER_SIZE = 128
BLOCK_HEADER = struct.Struct("<BHH")
MAX_IMAGE_SIZE = 16 * 1024 * 1024
MAX_INPUT_SIZE = 2 * MAX_IMAGE_SIZE


class FDFError(ValueError):
    """The input is corrupt or uses an unsupported FDF variant."""


def _make_crc_table():
    table = []
    for value in range(256):
        for _ in range(8):
            value = (value >> 1) ^ (0xA001 if value & 1 else 0)
        table.append(value)
    return tuple(table)


CRC_TABLE = _make_crc_table()


def crc16(data):
    """CRC-16/ARC (LHA): reflected 0x8005, initial value 0, no final XOR."""
    value = 0
    for byte in data:
        value = (value >> 8) ^ CRC_TABLE[(value ^ byte) & 0xFF]
    return value


def decode_rle(data, limit=MAX_IMAGE_SIZE):
    """Decode an FDF block, without letting runs cross its encoded boundary."""
    result = bytearray()
    pos = 0
    while pos < len(data):
        control = data[pos]
        pos += 1
        count = control & 0x7F
        if len(result) + count > limit:
            raise FDFError("decoded data exceeds the supported image size")
        if control & 0x80:
            if pos == len(data):
                raise FDFError("truncated RLE repeat run")
            result.extend(data[pos:pos + 1] * count)
            pos += 1
        else:
            if pos + count > len(data):
                raise FDFError("truncated RLE literal run")
            result.extend(data[pos:pos + count])
            pos += count
    return result


def disk_geometry(data):
    """Read capacity and cylinder size from the DOS BIOS Parameter Block."""
    if len(data) < 36:
        raise FDFError("decoded image is too short to contain a boot-sector BPB")
    sector_size = struct.unpack_from("<H", data, 11)[0]
    total_sectors = struct.unpack_from("<H", data, 19)[0]
    if total_sectors == 0:
        total_sectors = struct.unpack_from("<I", data, 32)[0]
    sectors_per_track, heads = struct.unpack_from("<HH", data, 24)
    if (sector_size not in (128, 256, 512, 1024, 2048, 4096, 8192)
            or not 1 <= sectors_per_track <= 63 or heads not in (1, 2)
            or total_sectors == 0):
        raise FDFError("invalid or unsupported boot-sector BPB; cannot determine disk size")
    sectors_per_cylinder = sectors_per_track * heads
    if (total_sectors % sectors_per_cylinder != 0
            or not 1 <= total_sectors // sectors_per_cylinder <= 255):
        raise FDFError("boot-sector BPB does not describe a supported floppy geometry")
    image_size = sector_size * total_sectors
    if image_size > MAX_IMAGE_SIZE:
        raise FDFError("boot-sector BPB exceeds the supported image size (16 MiB)")
    return image_size, sector_size * sectors_per_cylinder


def decode_fdf(data):
    """Return the complete raw disk image, including omitted 0xF6-filled tracks."""
    if data[:4] != SIGNATURE:
        raise FDFError("not an FDF file (expected signature 1A 46 44 46)")
    if len(data) < HEADER_SIZE:
        raise FDFError("truncated FDF file header (expected 128 bytes)")
    if len(data) > MAX_INPUT_SIZE:
        raise FDFError("FDF input exceeds the supported size (32 MiB)")

    # 86Box reads the saved cylinder count at 0x50. It is often smaller than
    # the full disk capacity in the BPB because EZ-DisKlone omits unused tracks.
    saved_cylinders = struct.unpack_from("<I", data, 0x50)[0]
    output = bytearray()
    pos = HEADER_SIZE
    block_number = 0
    while pos < len(data):
        block_number += 1
        context = "block {} at offset 0x{:x}".format(block_number, pos)
        if len(data) - pos < BLOCK_HEADER.size:
            raise FDFError("{}: truncated block header".format(context))
        method, expected_crc, size = BLOCK_HEADER.unpack_from(data, pos)
        pos += BLOCK_HEADER.size
        if method == 0xFF:
            if pos != len(data):
                raise FDFError("{}: unexpected data after end marker".format(context))
            break
        if method not in (0, 1):
            raise FDFError("{}: unknown compression method 0x{:02x}".format(context, method))
        if size == 0:
            raise FDFError("{}: empty data block".format(context))
        if pos + size > len(data):
            raise FDFError("{}: truncated block payload".format(context))
        payload = data[pos:pos + size]
        pos += size
        actual_crc = crc16(payload)
        if actual_crc != expected_crc:
            raise FDFError(
                "{}: CRC mismatch (stored {:04x}, calculated {:04x})".format(
                    context, expected_crc, actual_crc))
        try:
            decoded = (decode_rle(payload, MAX_IMAGE_SIZE - len(output))
                       if method == 1 else payload)
        except FDFError as error:
            raise FDFError("{}: {}".format(context, error)) from error
        if len(output) + len(decoded) > MAX_IMAGE_SIZE:
            raise FDFError("decoded image exceeds the supported size (16 MiB)")
        output.extend(decoded)

    image_size, cylinder_size = disk_geometry(output)
    if len(output) > image_size:
        raise FDFError("decoded data exceeds the disk capacity recorded in the BPB")
    if saved_cylinders:
        expected_size = saved_cylinders * cylinder_size
        if len(output) != expected_size:
            raise FDFError(
                "decoded {} bytes, but the FDF header records {} saved cylinders "
                "({} bytes); input may be truncated or use an unsupported variant".format(
                    len(output), saved_cylinders, expected_size))
    elif len(output) != image_size:
        # Without the saved count, a short stream cannot be distinguished from
        # a file truncated exactly at a block boundary. Do not silently pad it.
        raise FDFError("incomplete disk data with no saved cylinder count in the FDF header")

    output.extend(b"\xf6" * (image_size - len(output)))
    return bytes(output)


def convert(input_file, output_file):
    """Validate and convert before atomically replacing the destination file."""
    source = Path(input_file)
    destination = Path(output_file)
    if (source.resolve() == destination.resolve()
            or (destination.exists() and source.samefile(destination))):
        raise FDFError("input and output must be different files")
    with source.open("rb") as stream:
        data = stream.read(MAX_INPUT_SIZE + 1)
    image = decode_fdf(data)

    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
                mode="wb", dir=destination.parent,
                prefix="." + destination.name + ".", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(image)
        os.replace(temporary, destination)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
    return len(image)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Convert an EZ-DisKlone Plus FDF file to a standard raw disk image.",
        epilog="Uses only the Python standard library. Existing output files are replaced.")
    parser.add_argument("inputFile", type=Path, help="source FDF file")
    parser.add_argument("output_img", type=Path, metavar="output.img", help="destination raw image")
    args = parser.parse_args(argv)
    try:
        size = convert(args.inputFile, args.output_img)
    except (OSError, FDFError) as error:
        print("{}: error: {}".format(parser.prog, error), file=sys.stderr)
        return 1
    print("Wrote {} ({} bytes, {} KiB)".format(args.output_img, size, size // 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# Vibe coded by Codex
"""Dump PKZIP 1.x/2.x authenticity metadata and AVEXTRA using only stdlib.

The stored central-directory checksums suffice to decrypt this metadata; no
members are extracted, and successful decoding does NOT verify file contents.
Format reference: Jeffrey H. Johnson's infozip-av/unzip60/extract.c (MIT-0).
"""

import argparse
from dataclasses import dataclass
import struct
import sys
import zipfile
import zlib


MASK32 = 0xFFFFFFFF
EF_AV = 0x0007


@dataclass(frozen=True)
class PkavData:
    generation: int
    stamp: str
    company: bytes
    avextra: bytes


def crc_byte(crc, value):
    """Advance the uncomplemented CRC used by traditional ZIP encryption."""
    return zlib.crc32(bytes((value,)), crc ^ MASK32) ^ MASK32


def rotate_left(value, count):
    count &= 31
    return ((value << count) | (value >> ((32 - count) & 31))) & MASK32


def decrypt(payload, accumulator, generation):
    """Undo the length XOR and ZipCrypto layers (no 12-byte ZIP prefix)."""
    keys = [0x12345678, 0x23456789, 0x34567890]

    def update(value):
        keys[0] = crc_byte(keys[0], value)
        keys[1] = ((keys[1] + (keys[0] & 255)) * 134775813 + 1) & MASK32
        keys[2] = crc_byte(keys[2], keys[1] >> 24)

    for shift in range(0, 32, 4):
        update(((accumulator >> shift) & 15) + (0x12 if generation == 1 else 0x13))

    plain = bytearray()
    for index, value in enumerate(payload):
        temp = (keys[2] | 2) & 0xFFFF
        value ^= ((len(payload) - index) & 255) ^ ((temp * (temp ^ 1) >> 8) & 255)
        plain.append(value)
        update(value)
    return bytes(plain)


def av_records(extra):
    """Walk actual extra-field boundaries, never search arbitrary ZIP bytes."""
    offset = 0
    while offset < len(extra):
        if len(extra) - offset < 4:
            raise ValueError("truncated ZIP extra-field header")
        tag, length = struct.unpack_from("<HH", extra, offset)
        offset += 4
        end = offset + length
        if end > len(extra):
            raise ValueError("truncated ZIP extra-field payload")
        if tag == EF_AV:
            yield extra[offset:end]
        offset = end


def dos_datetime(entry):
    year, month, day, hour, minute, second = entry.date_time
    date = ((year - 1980) << 9) | (month << 5) | day
    time = (hour << 11) | (minute << 5) | (second // 2)
    return (date << 16) | time


def read_pkav(path):
    """Return decoded PKAV data, or None if no central EF_AV record exists.

    Raise OSError, BadZipFile or ValueError for unreadable/malformed input.
    ZIP64 and executable prefixes are handled by the standard ZIP reader.
    """
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        records = [
            (entry, payload)
            for entry in entries
            for payload in av_records(entry.extra)
        ]
        # Marker bits alone have other uses in newer ZIP specifications.
        if not records:
            return None
        if len(records) != 1:
            raise ValueError("expected one PKAV extra field, found %d" % len(records))

        version2 = [entry for entry in entries if entry.internal_attr & 0x0006]
        version1 = [
            entry for entry in entries
            if entry.create_system == 0 and entry.flag_bits & 0x2000
        ]
        if version2 and any(not entry.internal_attr & 0x0006 for entry in version1):
            raise ValueError("mixed PKAV 1.x and 2.x member sets")
        generation = 2 if version2 else 1
        members = version2 or version1
        owner, payload = records[0]
        if not members or (generation == 1 and owner not in version1):
            raise ValueError("PKAV extra field has no matching member markers")

        accumulator = 0
        for entry in members:
            auxiliary = (
                entry.external_attr
                if generation == 2 and entry.internal_attr & 0x0004
                else dos_datetime(entry)
            )
            accumulator = (accumulator + entry.CRC + auxiliary) & MASK32

    if len(payload) < 14:
        raise ValueError("PKAV payload is shorter than its header and company name")
    plain = decrypt(payload, accumulator, generation)
    terminator = plain.find(b"\0", 12)
    if terminator <= 12:
        raise ValueError("cannot decode the PKAV company name")
    company = plain[12:terminator]
    _, company_check, seed = struct.unpack_from("<III", plain)
    if ((seed - 26) & MASK32) % 157 or sum(int(digit) for digit in str(seed)) != 62:
        raise ValueError("cannot decode PKAV: invalid seed (damaged metadata)")
    if generation == 2:
        checksum = seed
        for value in company:
            checksum = crc_byte(checksum, value)
        if company_check != rotate_left(checksum ^ MASK32, seed & 31):
            raise ValueError("cannot decode PKAV: company checksum mismatch")
    # The first two dwords in PKAV 1.x are opaque, not a PKAV 2.x checksum.
    avextra = plain[terminator + 1:]
    if generation == 1 and avextra.endswith(b"\x1a"):
        avextra = avextra[:-1]  # DOS end-of-file marker, as in PKUNZIP 1.x.

    rotated = rotate_left(seed, 7)
    letters = (rotated >> 18) & 0x3FFF
    digits = (rotated & 0x3FFFF) // 263
    stamp = "".join(chr(65 + part) for part in (
        letters // 676, (letters // 26) % 26, letters % 26,
    )) + "%03d" % digits
    return PkavData(generation, stamp, company, avextra)


def format_dump(data, content_only=False):
    """Render DOS CP437 as Unicode, preserving AVEXTRA line formatting."""
    if content_only:
        output = data.company.decode("cp437") + "\n"
    else:
        output = "PKAV %d.x\nStamp: %s\nCompany: %s\n" % (
            data.generation, data.stamp, data.company.decode("cp437"),
        )
    if data.avextra:
        if not content_only:
            output += "AVEXTRA:\n"
        output += data.avextra.decode("cp437")
        if not output.endswith("\n"):
            output += "\n"
    return output


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Dump PKAV/AVEXTRA as UTF-8; print nothing if absent.",
        epilog="Reads metadata only; does not verify archive contents.",
    )
    parser.add_argument("inputFile", help="ZIP file (or ZIP self-extracting executable)")
    parser.add_argument(
        "--contentOnly", dest="content_only", action="store_true",
        help="print only company and AVEXTRA text, without labels, version, or stamp",
    )
    args = parser.parse_args(argv)
    try:
        data = read_pkav(args.inputFile)
        if data is not None:
            sys.stdout.buffer.write(format_dump(data, args.content_only).encode("utf-8"))
            sys.stdout.buffer.flush()
    except (OSError, ValueError, zipfile.BadZipFile, NotImplementedError) as exc:
        print("pkavDump.py: %s" % exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

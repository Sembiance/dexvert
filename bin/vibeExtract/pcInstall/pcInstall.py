#!/usr/bin/env python3
# Vibe coded by Codex
"""Extract application payloads from 20/20 Software PC-Install 4 containers."""

# The PKWARE DCL decompressor below is an independent Python adaptation of
# Mark Adler's blast.c (zlib contrib/blast), Copyright (C) 2003, 2012, 2013
# Mark Adler. Its license is reproduced here as required:
#
# This software is provided 'as-is', without any express or implied warranty.
# In no event will the author be held liable for any damages arising from the
# use of this software. Permission is granted to anyone to use this software
# for any purpose, including commercial applications, and to alter it and
# redistribute it freely, subject to these restrictions: (1) the origin must
# not be misrepresented; (2) altered versions must be plainly marked; and
# (3) this notice may not be removed or altered from any source distribution.

from __future__ import annotations

import argparse
import datetime as _datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import struct
import sys
from dataclasses import dataclass
from typing import NoReturn


MAGIC = b"[20/20]\x00"
MAX_BITS = 13
MAX_OUTPUT_SIZE = 2 * 1024 * 1024 * 1024


class FormatError(Exception):
    """The input is not a complete supported PC-Install container."""


def _fail(message: str) -> NoReturn:
    raise FormatError(message)


def _u16(data: bytes, offset: int) -> int:
    if offset < 0 or offset + 2 > len(data):
        _fail("unexpected end of file while reading a 16-bit field")
    return struct.unpack_from("<H", data, offset)[0]


def _u32(data: bytes, offset: int) -> int:
    if offset < 0 or offset + 4 > len(data):
        _fail("unexpected end of file while reading a 32-bit field")
    return struct.unpack_from("<I", data, offset)[0]


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _decode_name(field: bytes) -> str:
    nul = field.find(b"\x00")
    if nul < 0:
        _fail("a filename field is not NUL-terminated")
    # PC-Install only initializes bytes through the terminating NUL. Remaining
    # bytes in the fixed buffer are explicitly undefined (and often contain
    # allocator residue), so they are accounted for but have no semantics.
    raw = field[:nul]
    if not raw:
        _fail("an embedded filename is empty")
    if any(value < 0x20 for value in raw):
        _fail("an embedded filename contains a control character")
    return raw.decode("cp437")


def _safe_path(name: str) -> PurePosixPath:
    name = name.replace("\\", "/")
    if name.startswith("/") or (len(name) >= 2 and name[1] == ":"):
        _fail(f"unsafe absolute embedded path: {name!r}")
    parts = name.split("/")
    if any(part in ("", ".", "..") for part in parts):
        _fail(f"unsafe embedded path: {name!r}")
    return PurePosixPath(*parts)


def _parse_pe_end(data: bytes) -> int:
    if len(data) < 64 or data[:2] != b"MZ":
        _fail("missing DOS MZ executable header")
    pe = _u32(data, 0x3C)
    if pe < 64 or pe + 24 > len(data) or data[pe : pe + 4] != b"PE\x00\x00":
        _fail("missing or invalid PE signature")
    section_count = _u16(data, pe + 6)
    optional_size = _u16(data, pe + 20)
    if section_count == 0 or section_count > 96:
        _fail("invalid PE section count")
    optional = pe + 24
    if optional + optional_size > len(data) or _u16(data, optional) != 0x10B:
        _fail("the bootstrap is not a PE32 executable")
    table = optional + optional_size
    if table + section_count * 40 > len(data):
        _fail("truncated PE section table")
    end = 0
    for index in range(section_count):
        header = table + index * 40
        raw_size = _u32(data, header + 16)
        raw_offset = _u32(data, header + 20)
        if raw_size:
            if raw_offset == 0 or raw_offset + raw_size > len(data):
                _fail("a PE section extends beyond the input")
            end = max(end, raw_offset + raw_size)
    if end == 0:
        _fail("the PE image has no file-backed sections")
    return end


def _construct_huffman(repetitions: tuple[int, ...]) -> tuple[list[int], list[int]]:
    lengths: list[int] = []
    for item in repetitions:
        lengths.extend([item & 15] * ((item >> 4) + 1))
    counts = [0] * (MAX_BITS + 1)
    for length in lengths:
        if length > MAX_BITS:
            _fail("invalid built-in DCL Huffman table")
        counts[length] += 1
    left = 1
    for length in range(1, MAX_BITS + 1):
        left = (left << 1) - counts[length]
        if left < 0:
            _fail("oversubscribed built-in DCL Huffman table")
    offsets = [0] * (MAX_BITS + 1)
    offsets[1] = 0
    for length in range(1, MAX_BITS):
        offsets[length + 1] = offsets[length] + counts[length]
    symbols = [0] * sum(counts[1:])
    current = offsets[:]
    for symbol, length in enumerate(lengths):
        if length:
            symbols[current[length]] = symbol
            current[length] += 1
    return counts, symbols


_LITERAL_TABLE = _construct_huffman((
    11, 124, 8, 7, 28, 7, 188, 13, 76, 4, 10, 8, 12, 10, 12, 10, 8,
    23, 8, 9, 7, 6, 7, 8, 7, 6, 55, 8, 23, 24, 12, 11, 7, 9, 11, 12,
    6, 7, 22, 5, 7, 24, 6, 11, 9, 6, 7, 22, 7, 11, 38, 7, 9, 8, 25,
    11, 8, 11, 9, 12, 8, 12, 5, 38, 5, 38, 5, 11, 7, 5, 6, 21, 6,
    10, 53, 8, 7, 24, 10, 27, 44, 253, 253, 253, 252, 252, 252, 13,
    12, 45, 12, 45, 12, 61, 12, 45, 44, 173,
))
_LENGTH_TABLE = _construct_huffman((2, 35, 36, 53, 38, 23))
_DISTANCE_TABLE = _construct_huffman((2, 20, 53, 230, 247, 151, 248))
_LENGTH_BASE = (3, 2, 4, 5, 6, 7, 8, 9, 10, 12, 16, 24, 40, 72, 136, 264)
_LENGTH_EXTRA = (0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8)


class _BitReader:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.position = 0
        self.buffer = 0
        self.count = 0

    def bits(self, needed: int) -> int:
        while self.count < needed:
            if self.position >= len(self.data):
                _fail("truncated DCL implode bitstream")
            self.buffer |= self.data[self.position] << self.count
            self.position += 1
            self.count += 8
        value = self.buffer & ((1 << needed) - 1)
        self.buffer >>= needed
        self.count -= needed
        return value

    def decode(self, table: tuple[list[int], list[int]]) -> int:
        counts, symbols = table
        code = first = index = 0
        for length in range(1, MAX_BITS + 1):
            code |= self.bits(1) ^ 1
            count = counts[length]
            if code < first + count:
                return symbols[index + code - first]
            index += count
            first = (first + count) << 1
            code <<= 1
        _fail("invalid DCL implode Huffman code")


def _explode_dcl(data: bytes) -> bytes:
    reader = _BitReader(data)
    coded_literals = reader.bits(8)
    dictionary_bits = reader.bits(8)
    if coded_literals not in (0, 1):
        _fail("invalid DCL literal-coding flag")
    if dictionary_bits not in (4, 5, 6):
        _fail("invalid DCL dictionary size")
    output = bytearray()
    while True:
        if reader.bits(1) == 0:
            value = reader.decode(_LITERAL_TABLE) if coded_literals else reader.bits(8)
            output.append(value)
            if len(output) > MAX_OUTPUT_SIZE:
                _fail("a decompressed member exceeds the safety limit")
        else:
            symbol = reader.decode(_LENGTH_TABLE)
            length = _LENGTH_BASE[symbol] + reader.bits(_LENGTH_EXTRA[symbol])
            if length == 519:
                break
            low_bits = 2 if length == 2 else dictionary_bits
            distance = (reader.decode(_DISTANCE_TABLE) << low_bits) + reader.bits(low_bits) + 1
            if distance > len(output):
                _fail("DCL back-reference precedes the start of the output")
            for _ in range(length):
                output.append(output[-distance])
                if len(output) > MAX_OUTPUT_SIZE:
                    _fail("a decompressed member exceeds the safety limit")
    if reader.position != len(data):
        _fail("unused whole bytes follow the DCL end marker")
    # The end marker can leave high padding bits in its final byte. The encoder
    # defines them as zero, so checking them accounts for the complete stream.
    if reader.buffer != 0:
        _fail("nonzero padding bits follow the DCL end marker")
    return bytes(output)


@dataclass(frozen=True)
class Payload:
    path: PurePosixPath
    data: bytes
    timestamp: _datetime.datetime | None = None
    attributes: int = 0x20
    source: str = ""


@dataclass(frozen=True)
class ShrinkMember:
    name: str
    attributes: int
    compressed_size: int
    date_word: int
    time_word: int
    header_offset: int
    data_offset: int
    compressed_data: bytes
    output: bytes

    @property
    def timestamp(self) -> _datetime.datetime:
        year = 1980 + ((self.date_word >> 9) & 0x7F)
        month = (self.date_word >> 5) & 0x0F
        day = self.date_word & 0x1F
        hour = (self.time_word >> 11) & 0x1F
        minute = (self.time_word >> 5) & 0x3F
        second = (self.time_word & 0x1F) * 2
        try:
            return _datetime.datetime(year, month, day, hour, minute, second)
        except ValueError:
            _fail(f"invalid DOS timestamp on PC-Shrink member {self.name!r}")


@dataclass(frozen=True)
class ShrinkArchive:
    member_count: int
    members: tuple[ShrinkMember, ...]


def _parse_pcshrink(data: bytes, base_offset: int) -> ShrinkArchive | None:
    if len(data) < 58:
        return None
    signature_match = data[13] == 0 and _u16(data, 14) == 0x74
    if not signature_match:
        return None
    if any(data[:14]) or data[20:58] != bytes(38):
        _fail("invalid reserved bytes in the PC-Shrink archive header")
    count = _u16(data, 16)
    volume = _u16(data, 18)
    if volume == 0x75:
        _fail("multipart PC-Shrink archives are not supported")
    if volume != 0x74:
        _fail("invalid PC-Shrink volume marker")
    position = 58
    members: list[ShrinkMember] = []
    for _ in range(count):
        header = position
        if header + 168 > len(data):
            _fail("truncated PC-Shrink member header")
        name = _decode_name(data[header : header + 128])
        attributes = data[header + 128]
        # In addition to DOS attribute bits 0..5, PC-Shrink uses 0x80 for a
        # normal file. Bit 6 remains reserved.
        if attributes & 0x40:
            _fail(f"invalid DOS attributes on PC-Shrink member {name!r}")
        if any(data[header + 129 : header + 136]) or any(data[header + 148 : header + 168]):
            _fail(f"nonzero reserved bytes on PC-Shrink member {name!r}")
        compressed_size = _u32(data, header + 136)
        date_full = _u32(data, header + 140)
        time_full = _u32(data, header + 144)
        if date_full >> 16 or time_full >> 16:
            _fail(f"invalid extended DOS timestamp on PC-Shrink member {name!r}")
        data_offset = header + 168
        end = data_offset + compressed_size
        if end > len(data):
            _fail(f"truncated compressed data for PC-Shrink member {name!r}")
        compressed = data[data_offset:end]
        if attributes & 0x10:
            if compressed_size != 0:
                _fail(f"directory member {name!r} unexpectedly contains data")
            output = b""
        elif compressed_size == 0:
            output = b""
        else:
            output = _explode_dcl(compressed)
        member = ShrinkMember(
            name, attributes, compressed_size, date_full, time_full,
            base_offset + header, base_offset + data_offset, compressed, output,
        )
        # Validate the timestamp even when the caller does not preserve it.
        member.timestamp
        members.append(member)
        position = end
    if position != len(data):
        _fail("bytes remain after the final PC-Shrink member")
    return ShrinkArchive(count, tuple(members))


@dataclass(frozen=True)
class OuterRecord:
    index: int
    link_offset: int
    record_offset: int
    data_offset: int
    end_offset: int
    name: str
    name_field: bytes
    data: bytes
    link: bytes
    archive: ShrinkArchive | None


@dataclass(frozen=True)
class Container:
    pe_end: int
    pif_end: int
    pif: bytes
    pif_trailer_offset: int
    footer_offset: int
    footer: bytes
    records: tuple[OuterRecord, ...]
    payloads: tuple[Payload, ...]


def _parse_container(data: bytes) -> Container:
    pe_end = _parse_pe_end(data)
    if pe_end + 16 > len(data) or data[pe_end : pe_end + 8] != MAGIC:
        _fail("the PE overlay does not begin with a PC-Install PIF object")
    if len(data) < pe_end + 32 or data[-16:-8] != MAGIC:
        _fail("missing PC-Install locator trailer (the file may be truncated)")
    footer_offset = len(data) - 16
    footer = data[footer_offset:]
    first_locator = _u32(footer, 8)
    last_link = _u32(footer, 12)
    if first_locator != pe_end + 8:
        _fail("the final trailer does not point to the PIF header locator")
    # The historical implementation stores the first embedded-file link in
    # the PIF header's offset-8 slot. "pif_trailer_offset" is retained in the
    # internal model because that link is the final 16 bytes of the PIF blob.
    pif_trailer_offset = _u32(data, pe_end + 8)
    records: list[OuterRecord] = []
    payloads: list[Payload] = []
    if pif_trailer_offset == 0:
        if last_link != first_locator:
            _fail("invalid empty embedded-file list locator")
        pif_end = len(data)
        return Container(
            pe_end, pif_end, data[pe_end:pif_end], footer_offset,
            footer_offset, footer, tuple(), tuple(),
        )
    if not (pe_end + 16 <= pif_trailer_offset < footer_offset):
        _fail("the first embedded-file link locator is out of range")
    pif_end = pif_trailer_offset + 16
    link_offset = pif_trailer_offset
    index = 0
    while True:
        record_offset = link_offset + 16
        if record_offset + 260 > footer_offset:
            _fail("truncated outer embedded-file record")
        size = _u32(data, record_offset)
        name_field = data[record_offset + 4 : record_offset + 260]
        name = _decode_name(name_field)
        data_offset = record_offset + 260
        end_offset = data_offset + size
        if end_offset > footer_offset:
            _fail(f"truncated outer embedded file {name!r}")
        archive = _parse_pcshrink(data[data_offset:end_offset], data_offset)
        link = data[link_offset : link_offset + 16]
        records.append(OuterRecord(
            index, link_offset, record_offset, data_offset, end_offset,
            name, name_field, data[data_offset:end_offset], link, archive,
        ))
        if end_offset == footer_offset:
            if link_offset != last_link:
                _fail("the final trailer does not locate the last embedded-file record")
            if _u32(link, 0) != 0:
                _fail("the last embedded-file link is not terminated")
            break
        next_link = end_offset
        if next_link + 16 + 260 > footer_offset:
            _fail("unframed bytes occur between outer embedded-file records")
        if _u32(link, 0) != next_link:
            _fail("an outer embedded-file link points to the wrong record")
        link_offset = next_link
        index += 1
        if index > 65535:
            _fail("unreasonable outer embedded-file record count")
    if not records:
        _fail("the embedded-file list is unexpectedly empty")

    control = records[0]
    for record in records[1:]:
        is_control_copy = record.name.casefold() == control.name.casefold() and record.data == control.data
        if is_control_copy:
            continue
        if record.archive is not None:
            for member in record.archive.members:
                if member.attributes & 0x10:
                    continue
                payloads.append(Payload(
                    _safe_path(member.name), member.output, member.timestamp,
                    member.attributes, f"{record.name}:{member.name}",
                ))
        else:
            payloads.append(Payload(
                _safe_path(record.name), record.data, None, 0x20,
                f"outer record {record.index}",
            ))

    seen: dict[str, Payload] = {}
    unique: list[Payload] = []
    for payload in payloads:
        key = str(payload.path).casefold()
        previous = seen.get(key)
        if previous is not None:
            if previous.data != payload.data or previous.path != payload.path:
                _fail(f"conflicting Windows filename collision: {payload.path}")
            continue
        seen[key] = payload
        unique.append(payload)
    return Container(
        pe_end, pif_end, data[pe_end:pif_end], pif_trailer_offset,
        footer_offset, footer, tuple(records), tuple(unique),
    )


def _metadata_files(container: Container, data: bytes) -> list[Payload]:
    files = [
        Payload(PurePosixPath("__pcinstall__/bootstrap.exe"), data[:container.pe_end]),
        Payload(PurePosixPath("__pcinstall__/install.pif"), container.pif),
    ]
    for record in container.records:
        basename = Path(record.name.replace("\\", "/")).name
        files.append(Payload(
            PurePosixPath(f"__pcinstall__/records/{record.index:03d}_{basename}"),
            record.data,
        ))
    manifest = {
        "format": "20/20 Software PC-Install 4 PE container",
        "input_size": len(data),
        "input_sha256": _sha256(data),
        "pe_end": container.pe_end,
        "pif_end": container.pif_end,
        "pif_trailer_offset": container.pif_trailer_offset,
        "footer_offset": container.footer_offset,
        "footer_hex": container.footer.hex(),
        "records": [
            {
                "index": record.index,
                "name": record.name,
                "link_offset": record.link_offset,
                "record_offset": record.record_offset,
                "data_offset": record.data_offset,
                "end_offset": record.end_offset,
                "size": len(record.data),
                "sha256": _sha256(record.data),
                "link_hex": record.link.hex(),
                "name_field_hex": record.name_field.hex(),
                "pcshrink_members": 0 if record.archive is None else record.archive.member_count,
            }
            for record in container.records
        ],
        "payloads": [
            {"path": str(item.path), "size": len(item.data), "sha256": _sha256(item.data), "source": item.source}
            for item in container.payloads
        ],
    }
    files.append(Payload(
        PurePosixPath("__pcinstall__/manifest.json"),
        (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8"),
    ))
    return files


def _write_payloads(output_dir: Path, payloads: list[Payload]) -> None:
    # Format validation and decompression have already completed. No filesystem
    # mutation occurs before that point, which gives invalid inputs fail-fast
    # behavior even when output_dir already exists.
    seen: dict[str, Payload] = {}
    for payload in payloads:
        key = str(payload.path).casefold()
        previous = seen.get(key)
        if previous is not None and (previous.path != payload.path or previous.data != payload.data):
            _fail(f"conflicting output filename: {payload.path}")
        seen[key] = payload
    output_dir.mkdir(parents=True, exist_ok=True)
    resolved_root = output_dir.resolve()
    for payload in payloads:
        destination = output_dir.joinpath(*payload.path.parts)
        resolved_parent = destination.parent.resolve()
        if resolved_parent != resolved_root and resolved_root not in resolved_parent.parents:
            _fail(f"an existing symlink escapes the output directory: {payload.path}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_name(destination.name + ".pcinstall-tmp")
        try:
            with temporary.open("wb") as handle:
                handle.write(payload.data)
            os.chmod(temporary, 0o664)
            os.replace(temporary, destination)
            if payload.timestamp is not None:
                timestamp = payload.timestamp.timestamp()
                os.utime(destination, (timestamp, timestamp))
            mode = 0o444 if payload.attributes & 0x01 else 0o664
            os.chmod(destination, mode)
        finally:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass
    for root, directories, _ in os.walk(output_dir):
        os.chmod(root, 0o775)
        for directory in directories:
            os.chmod(Path(root, directory), 0o775)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract installed payloads from a PC-Install 4 executable.",
    )
    parser.add_argument("--all", action="store_true", help="also extract container metadata and a JSON manifest")
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputDir", type=Path)
    args = parser.parse_args(argv)
    try:
        data = args.inputFile.read_bytes()
        container = _parse_container(data)
        payloads = list(container.payloads)
        if args.all:
            payloads.extend(_metadata_files(container, data))
        _write_payloads(args.outputDir, payloads)
    except (FormatError, OSError) as error:
        print(f"pcInstall.py: error: {error}", file=sys.stderr)
        return 1
    print(f"Extracted {len(container.payloads)} installed file(s) to {args.outputDir}")
    if args.all:
        print("Also extracted PC-Install container metadata under __pcinstall__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# Vibe coded by Codex
"""Strict extractor for AOL Setup/Install self-extracting prefix images."""

from __future__ import annotations

import argparse
import binascii
import hashlib
import json
import os
import shutil
import struct
import sys
import tempfile
import zlib
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path, PureWindowsPath
from typing import Any


class FormatError(Exception):
    """The input is not a supported, internally consistent AOL Setup image."""


def _need(data: bytes, offset: int, size: int, what: str) -> None:
    if offset < 0 or size < 0 or offset + size > len(data):
        raise FormatError(f"truncated {what} at file offset 0x{offset:x}")


def _ascii(raw: bytes, what: str) -> str:
    try:
        value = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        raise FormatError(f"{what} is not ASCII") from exc
    if "\x00" in value:
        raise FormatError(f"{what} contains NUL")
    return value


@dataclass
class PEInfo:
    raw_end: int
    export_name: str
    machine: int
    timestamp: int
    sections: int


def _parse_pe(data: bytes, *, exact_size: bool = False, label: str = "PE image") -> PEInfo:
    _need(data, 0, 0x40, f"{label} DOS header")
    if data[:2] != b"MZ":
        raise FormatError(f"{label} has no MZ signature")
    pe_offset = struct.unpack_from("<I", data, 0x3C)[0]
    _need(data, pe_offset, 24, f"{label} PE header")
    if data[pe_offset : pe_offset + 4] != b"PE\0\0":
        raise FormatError(f"{label} has no PE signature")
    machine, section_count, timestamp = struct.unpack_from("<HHI", data, pe_offset + 4)
    optional_size = struct.unpack_from("<H", data, pe_offset + 20)[0]
    if machine != 0x14C or not 1 <= section_count <= 96:
        raise FormatError(f"{label} is not a supported i386 PE image")
    optional = pe_offset + 24
    _need(data, optional, optional_size, f"{label} optional header")
    if optional_size < 224 or struct.unpack_from("<H", data, optional)[0] != 0x10B:
        raise FormatError(f"{label} is not PE32")
    section_table = optional + optional_size
    _need(data, section_table, section_count * 40, f"{label} section table")

    sections: list[tuple[int, int, int, int]] = []
    raw_end = 0
    for index in range(section_count):
        entry = section_table + index * 40
        virtual_size, virtual_address, raw_size, raw_pointer = struct.unpack_from(
            "<IIII", data, entry + 8
        )
        if raw_size:
            _need(data, raw_pointer, raw_size, f"{label} section {index}")
            raw_end = max(raw_end, raw_pointer + raw_size)
        sections.append((virtual_address, virtual_size, raw_pointer, raw_size))
    if raw_end == 0:
        raise FormatError(f"{label} has no file-backed sections")
    if exact_size and raw_end != len(data):
        raise FormatError(
            f"{label} section data ends at 0x{raw_end:x}, not its 0x{len(data):x} boundary"
        )

    def rva_to_offset(rva: int, size: int, what: str) -> int:
        for virtual_address, virtual_size, raw_pointer, raw_size in sections:
            extent = max(virtual_size, raw_size)
            if virtual_address <= rva and rva + size <= virtual_address + extent:
                delta = rva - virtual_address
                if delta + size > raw_size:
                    break
                return raw_pointer + delta
        raise FormatError(f"{label} {what} RVA 0x{rva:x} is not file-backed")

    directory_count = struct.unpack_from("<I", data, optional + 92)[0]
    if directory_count < 1:
        raise FormatError(f"{label} has no export directory")
    export_rva, export_size = struct.unpack_from("<II", data, optional + 96)
    if not export_rva or export_size < 40:
        raise FormatError(f"{label} has no usable export directory")
    export_offset = rva_to_offset(export_rva, 40, "export directory")
    name_rva = struct.unpack_from("<I", data, export_offset + 12)[0]
    name_offset = rva_to_offset(name_rva, 1, "export module name")
    name_end = data.find(b"\0", name_offset, min(raw_end, name_offset + 128))
    if name_end < 0:
        raise FormatError(f"{label} export module name is unterminated")
    export_name = _ascii(data[name_offset:name_end], f"{label} export module name")
    return PEInfo(raw_end, export_name, machine, timestamp, section_count)


@dataclass
class Reader:
    data: bytes
    pos: int
    limit: int

    def take(self, size: int, what: str) -> bytes:
        if size < 0 or self.pos + size > self.limit:
            raise FormatError(f"truncated {what} at file offset 0x{self.pos:x}")
        value = self.data[self.pos : self.pos + size]
        self.pos += size
        return value

    def u16(self, what: str) -> int:
        return struct.unpack("<H", self.take(2, what))[0]

    def u32(self, what: str) -> int:
        return struct.unpack("<I", self.take(4, what))[0]

    def lp_string(self, what: str, maximum: int) -> str:
        length = self.u16(f"{what} length")
        if length >= maximum:
            raise FormatError(f"{what} length {length} exceeds the format limit {maximum - 1}")
        return _ascii(self.take(length, what), what)


@dataclass
class FileRecord:
    name: str
    unpacked_size: int
    stored_span: int


@dataclass
class Database:
    variant: str
    start: int
    end: int
    header_strings: list[str]
    scalars: list[int]
    resource_ids: list[int]
    string_collections: list[list[tuple[str, str | None]]]
    u16_arrays: list[list[int]]
    extra_scalars: list[int]
    complex_groups: list[dict[str, Any]]
    files: list[FileRecord]
    file_table_start: int = 0
    configuration_prefix: bytes = field(default=b"", repr=False)


OLD_STRING_LIMITS = [257, 64, 128, 64, 64, 32, 512, 256, 32, 32]
NEW_STRING_LIMITS = [
    257, 64, 128, 128, 64, 64, 32, 512, 256, 32, 32,
    32, 32, 32, 64, 64, 64, 32, 6, 6, 6, 6,
]


def _parse_collection(reader: Reader, label: str, paired: bool) -> list[tuple[str, str | None]]:
    count = reader.u16(f"{label} count")
    result: list[tuple[str, str | None]] = []
    for index in range(count):
        first = reader.lp_string(f"{label}[{index}].first", 128)
        second = reader.lp_string(f"{label}[{index}].second", 128) if paired else None
        result.append((first, second))
    return result


def _parse_database(data: bytes, start: int, export_name: str) -> Database:
    reader = Reader(data, start, len(data))
    if reader.take(2, "AOL database signature") != b"RS":
        raise FormatError(f"PE overlay at 0x{start:x} is not an AOL RS database")
    if export_name == "SETUP.EXE":
        variant = "setup"
        limits = OLD_STRING_LIMITS
        scalar_count = 4
    elif export_name == "INSTALL.EXE":
        variant = "install"
        limits = NEW_STRING_LIMITS
        scalar_count = 5
    else:
        raise FormatError(
            f"unsupported setup-stub export name {export_name!r}; expected SETUP.EXE or INSTALL.EXE"
        )

    header = [reader.lp_string(f"header string {i + 1}", limit) for i, limit in enumerate(limits)]
    scalars = [reader.u16(f"header scalar {i + 1}") for i in range(scalar_count)]
    resource_count = reader.u16("resource-ID count")
    resource_ids = [reader.u32(f"resource ID {i}") for i in range(resource_count)]
    paired = [True, True, False, False, False, False, False]
    collections = [
        _parse_collection(reader, f"string collection {i + 1}", is_paired)
        for i, is_paired in enumerate(paired)
    ]

    array_count = 3 if variant == "install" else 2
    arrays: list[list[int]] = []
    for index in range(array_count):
        count = reader.u16(f"u16 array {index + 1} count")
        arrays.append([reader.u16(f"u16 array {index + 1}[{j}]") for j in range(count)])

    extra_scalars: list[int] = []
    complex_groups: list[dict[str, Any]] = []
    if variant == "install":
        for is_paired in (False, True, False):
            collections.append(
                _parse_collection(reader, f"string collection {len(collections) + 1}", is_paired)
            )
        extra_scalars = [reader.u16("install scalar 1"), reader.u16("install scalar 2")]
        group_count = reader.u16("complex-group count")
        for i in range(group_count):
            name = reader.lp_string(f"complex group {i} name", 32)
            value = reader.u32(f"complex group {i} value")
            first_count = reader.u16(f"complex group {i} dword count")
            dwords = [reader.u32(f"complex group {i} dword {j}") for j in range(first_count)]
            second_count = reader.u16(f"complex group {i} string count")
            strings = [
                reader.lp_string(f"complex group {i} string {j}", 32)
                for j in range(second_count)
            ]
            complex_groups.append({"name": name, "value": value, "dwords": dwords, "strings": strings})

    file_table_start = reader.pos
    file_count = reader.u16("file-record count")
    if file_count < 1:
        raise FormatError("AOL database has no embedded-helper file record")
    files: list[FileRecord] = []
    seen: set[str] = set()
    for index in range(file_count):
        name = reader.lp_string(f"file record {index} name", 260)
        unpacked = reader.u32(f"file record {index} unpacked size")
        stored = reader.u32(f"file record {index} stored span")
        if not name or not stored:
            raise FormatError(f"file record {index} has an empty name or stored span")
        key = name.replace("/", "\\").casefold()
        if index and key in seen:
            raise FormatError(f"duplicate Windows output path {name!r}")
        seen.add(key)
        files.append(FileRecord(name, unpacked, stored))
    return Database(
        variant, start, reader.pos, header, scalars, resource_ids,
        collections, arrays, extra_scalars, complex_groups, files,
        file_table_start, data[start + 2 : file_table_start],
    )


def _parse_file_table(data: bytes, table_start: int, helper_start: int) -> list[FileRecord]:
    reader = Reader(data, table_start, helper_start)
    file_count = reader.u16("file-record count")
    if not 1 <= file_count <= 4096:
        raise FormatError("invalid file-record count")
    files: list[FileRecord] = []
    seen: set[str] = set()
    for index in range(file_count):
        name = reader.lp_string(f"file record {index} name", 260)
        unpacked = reader.u32(f"file record {index} unpacked size")
        stored = reader.u32(f"file record {index} stored span")
        if not name or not stored:
            raise FormatError(f"file record {index} has an empty name or stored span")
        key = name.replace("/", "\\").casefold()
        if key in seen:
            raise FormatError(f"duplicate Windows output path {name!r}")
        seen.add(key)
        files.append(FileRecord(name, unpacked, stored))
    if reader.pos != helper_start:
        raise FormatError("file table does not end at the embedded helper")
    return files


def _locate_database(data: bytes, pe: PEInfo) -> Database:
    """Recognize the self-describing file-table suffix across compiled RS revisions."""
    start = pe.raw_end
    if data[start : start + 2] != b"RS":
        raise FormatError(f"PE overlay at 0x{start:x} is not an AOL RS database")
    if pe.export_name not in ("SETUP.EXE", "INSTALL.EXE"):
        raise FormatError(
            f"unsupported setup-stub export name {pe.export_name!r}; expected SETUP.EXE or INSTALL.EXE"
        )

    lowered = data.lower()
    candidates: list[tuple[int, int, list[FileRecord]]] = []
    search_at = start + 2
    while True:
        name_at = lowered.find(b"dunzip", search_at)
        if name_at < 0:
            break
        search_at = name_at + 1
        if name_at < start + 6:
            continue
        name_length = struct.unpack_from("<H", data, name_at - 2)[0]
        if not 1 <= name_length <= 32:
            continue
        raw_name = data[name_at : name_at + name_length]
        try:
            helper_name = raw_name.decode("ascii")
        except UnicodeDecodeError:
            continue
        if helper_name.casefold() not in ("dunzipnt.dll", "dunzip32.dll"):
            continue
        table_start = name_at - 4
        if table_start < start + 2:
            continue
        try:
            count = struct.unpack_from("<H", data, table_start)[0]
            if not 1 <= count <= 4096:
                continue
            probe = Reader(data, table_start + 2, len(data))
            records: list[FileRecord] = []
            for index in range(count):
                record_name = probe.lp_string(f"file record {index} name", 260)
                records.append(FileRecord(record_name, probe.u32("unpacked size"), probe.u32("stored span")))
            helper_start = probe.pos
            if records[0].name.casefold() != helper_name.casefold():
                continue
            if records[0].unpacked_size != records[0].stored_span or not records[0].stored_span:
                continue
            _need(data, helper_start, records[0].stored_span, "embedded DynaZIP helper")
            helper = data[helper_start : helper_start + records[0].stored_span]
            helper_pe = _parse_pe(helper, exact_size=True, label="embedded DynaZIP helper")
            if not helper_pe.export_name.casefold().startswith("dunzip"):
                continue
            records = _parse_file_table(data, table_start, helper_start)
            candidates.append((table_start, helper_start, records))
        except (FormatError, struct.error):
            continue
    unique = {(table, helper) for table, helper, _ in candidates}
    if len(unique) != 1:
        if not unique:
            raise FormatError("could not locate a validated AOL file table and DynaZIP helper")
        raise FormatError("AOL overlay contains more than one valid file-table/helper pairing")
    table_start, helper_start, files = candidates[0]

    # Decode the two fully specified layouts when applicable. Other revisions
    # compile a different configuration grammar into their stub; their common,
    # self-describing file-table suffix remains identical.
    try:
        detailed = _parse_database(data, start, pe.export_name)
        if detailed.end == helper_start and detailed.files == files:
            return detailed
    except FormatError:
        pass
    variant = "setup-compiled" if pe.export_name == "SETUP.EXE" else "install-compiled"
    return Database(
        variant, start, helper_start, [], [], [], [], [], [], [], files,
        table_start, data[start + 2 : table_start],
    )


def _safe_output_path(name: str) -> Path:
    windows = PureWindowsPath(name.replace("/", "\\"))
    if windows.is_absolute() or windows.drive or not windows.parts:
        raise FormatError(f"unsafe absolute output path {name!r}")
    parts: list[str] = []
    for part in windows.parts:
        if part in ("", ".", "..") or ":" in part or "\x00" in part:
            raise FormatError(f"unsafe output path component in {name!r}")
        parts.append(part)
    return Path(*parts)


def _dos_datetime(date: int, time: int) -> tuple[int, int, int, int, int, int]:
    year = 1980 + ((date >> 9) & 0x7F)
    month = (date >> 5) & 0x0F
    day = date & 0x1F
    hour = (time >> 11) & 0x1F
    minute = (time >> 5) & 0x3F
    second = (time & 0x1F) * 2
    try:
        datetime(year, month, day, hour, minute, second)
    except ValueError as exc:
        raise FormatError("ZIP member has an invalid DOS timestamp") from exc
    return year, month, day, hour, minute, second


@dataclass
class ExtractedMember:
    record: FileRecord
    path: Path
    data: bytes
    crc32: int
    method: int
    dos_datetime: tuple[int, int, int, int, int, int] | None
    zip_span: int
    storage: str = "zip"


def _member_basename(name: str) -> str:
    return PureWindowsPath(name.replace("/", "\\")).name


def _parse_complete_zip(chunk: bytes, record: FileRecord) -> ExtractedMember:
    if len(chunk) != record.stored_span:
        raise FormatError(f"ZIP span for {record.name!r} does not match its database record")
    _need(chunk, 0, 30, f"ZIP local header for {record.name}")
    local = struct.unpack_from("<IHHHHHIIIHH", chunk, 0)
    signature, version, flags, method, mod_time, mod_date, crc, csize, usize, name_len, extra_len = local
    if signature != 0x04034B50:
        raise FormatError(f"{record.name!r} has no ZIP local-header signature")
    if flags & 0x0009 or flags & ~0x0006:
        raise FormatError(f"{record.name!r} uses unsupported ZIP flags 0x{flags:04x}")
    if flags & 0x0008:
        raise FormatError(f"{record.name!r} uses a ZIP data descriptor")
    if method not in (0, 8):
        raise FormatError(f"{record.name!r} uses unsupported ZIP method {method}")
    if usize != record.unpacked_size:
        raise FormatError(f"{record.name!r} unpacked size disagrees with the database")
    _need(chunk, 30, name_len + extra_len + csize, f"ZIP data for {record.name}")
    local_name = _ascii(chunk[30 : 30 + name_len], f"ZIP name for {record.name}")
    if local_name.casefold() != _member_basename(record.name).casefold():
        raise FormatError(f"ZIP basename {local_name!r} disagrees with database path {record.name!r}")
    data_start = 30 + name_len + extra_len
    compressed = chunk[data_start : data_start + csize]
    try:
        if method == 0:
            output = compressed
        else:
            decompressor = zlib.decompressobj(-15)
            output = decompressor.decompress(compressed) + decompressor.flush()
            if not decompressor.eof or decompressor.unused_data or decompressor.unconsumed_tail:
                raise FormatError(f"{record.name!r} has a malformed raw DEFLATE stream")
    except zlib.error as exc:
        raise FormatError(f"{record.name!r} DEFLATE stream is invalid: {exc}") from exc
    actual_crc = binascii.crc32(output) & 0xFFFFFFFF
    if len(output) != usize or actual_crc != crc:
        raise FormatError(f"{record.name!r} fails its ZIP size/CRC check")

    central_offset = data_start + csize
    _need(chunk, central_offset, 46, f"ZIP central header for {record.name}")
    central = struct.unpack_from("<IHHHHHHIIIHHHHHII", chunk, central_offset)
    (
        csig, made_by, cversion, cflags, cmethod, ctime, cdate, ccrc, ccsize, cusize,
        cname_len, cextra_len, comment_len, disk_start, internal_attr, external_attr, local_offset,
    ) = central
    if csig != 0x02014B50:
        raise FormatError(f"{record.name!r} has no ZIP central-header signature")
    if (cversion, cflags, cmethod, ctime, cdate, ccrc, ccsize, cusize) != (
        version, flags, method, mod_time, mod_date, crc, csize, usize
    ):
        raise FormatError(f"{record.name!r} local and central ZIP headers disagree")
    _need(chunk, central_offset + 46, cname_len + cextra_len + comment_len, f"ZIP central fields for {record.name}")
    central_name = chunk[central_offset + 46 : central_offset + 46 + cname_len]
    if central_name != local_name.encode("ascii") or disk_start != 0 or local_offset != 0:
        raise FormatError(f"{record.name!r} has inconsistent ZIP central-directory metadata")
    eocd_offset = central_offset + 46 + cname_len + cextra_len + comment_len
    _need(chunk, eocd_offset, 22, f"ZIP end record for {record.name}")
    eocd = struct.unpack_from("<IHHHHIIH", chunk, eocd_offset)
    esig, disk, cd_disk, disk_entries, entries, cd_size, cd_offset, zip_comment_len = eocd
    if (
        esig != 0x06054B50 or disk != 0 or cd_disk != 0 or disk_entries != 1 or entries != 1
        or cd_size != 46 + cname_len + cextra_len + comment_len
        or cd_offset != central_offset or zip_comment_len != 0 or eocd_offset + 22 != len(chunk)
    ):
        raise FormatError(f"{record.name!r} has an inconsistent ZIP end record")
    return ExtractedMember(
        record, _safe_output_path(record.name), output, actual_crc, method,
        _dos_datetime(mod_date, mod_time), len(chunk),
    )


def _parse_partial_zip(
    chunk: bytes, record: FileRecord
) -> tuple[dict[str, Any], ExtractedMember | None]:
    """Validate a ZIP prefix and recover it when its complete payload is present."""
    if not chunk or len(chunk) >= record.stored_span:
        raise FormatError("internal partial-member boundary error")
    signature = b"PK\x03\x04"
    if len(chunk) < 4:
        if chunk != signature[: len(chunk)]:
            raise FormatError(f"truncated member {record.name!r} does not match a ZIP signature prefix")
        return ({"name": record.name, "available": len(chunk), "expected_span": record.stored_span,
                 "stage": "signature", "payload_recovered": False}, None)
    if chunk[:4] != signature:
        raise FormatError(f"truncated member {record.name!r} has no ZIP local-header signature")
    if len(chunk) < 30:
        return ({"name": record.name, "available": len(chunk), "expected_span": record.stored_span,
                 "stage": "local_header", "payload_recovered": False}, None)
    local = struct.unpack_from("<IHHHHHIIIHH", chunk, 0)
    _, version, flags, method, mod_time, mod_date, crc, csize, usize, name_len, extra_len = local
    if flags & 0x0009 or flags & ~0x0006 or flags & 0x0008 or method not in (0, 8):
        raise FormatError(f"truncated member {record.name!r} has unsupported ZIP header values")
    if usize != record.unpacked_size:
        raise FormatError(f"truncated member {record.name!r} size disagrees with the database")
    if len(chunk) < 30 + name_len + extra_len:
        return ({"name": record.name, "available": len(chunk), "expected_span": record.stored_span,
                 "stage": "name_or_extra", "payload_recovered": False}, None)
    local_name = _ascii(chunk[30 : 30 + name_len], f"partial ZIP name for {record.name}")
    if local_name.casefold() != _member_basename(record.name).casefold():
        raise FormatError(f"partial ZIP basename {local_name!r} disagrees with database path {record.name!r}")
    expected_span = 30 + name_len + extra_len + csize + 46 + name_len + 22
    if expected_span != record.stored_span:
        raise FormatError(f"truncated member {record.name!r} span disagrees with the database")
    data_start = 30 + name_len + extra_len
    available_data = chunk[data_start : min(len(chunk), data_start + csize)]
    data_end = data_start + csize
    if len(chunk) < data_end:
        try:
            if method == 8:
                zlib.decompressobj(-15).decompress(available_data)
        except zlib.error as exc:
            raise FormatError(f"truncated member {record.name!r} has an invalid DEFLATE prefix: {exc}") from exc
        return ({
            "name": record.name,
            "available": len(chunk),
            "expected_span": record.stored_span,
            "stage": "compressed_data",
            "compressed_available": len(available_data),
            "compressed_size": csize,
            "crc32": f"{crc:08x}",
            "dos_datetime": _dos_datetime(mod_date, mod_time),
            "version_needed": version,
            "payload_recovered": False,
        }, None)

    compressed = chunk[data_start:data_end]
    try:
        if method == 0:
            output = compressed
        else:
            decompressor = zlib.decompressobj(-15)
            output = decompressor.decompress(compressed) + decompressor.flush()
            if not decompressor.eof or decompressor.unused_data or decompressor.unconsumed_tail:
                raise FormatError(f"{record.name!r} has a malformed raw DEFLATE stream")
    except zlib.error as exc:
        raise FormatError(f"{record.name!r} DEFLATE stream is invalid: {exc}") from exc
    actual_crc = binascii.crc32(output) & 0xFFFFFFFF
    if len(output) != usize or actual_crc != crc:
        raise FormatError(f"truncated container's {record.name!r} payload fails its ZIP size/CRC check")

    trailing = chunk[data_end:]
    central_signature = b"PK\x01\x02"
    if len(trailing) < 4:
        if trailing != central_signature[: len(trailing)]:
            raise FormatError(f"{record.name!r} has invalid bytes after its complete payload")
        stage = "central_header"
    else:
        if trailing[:4] != central_signature:
            raise FormatError(f"{record.name!r} has no central-header prefix after its complete payload")
        stage = "central_header"
        known_fields = [
            (6, struct.pack("<H", version)), (8, struct.pack("<H", flags)),
            (10, struct.pack("<H", method)), (12, struct.pack("<H", mod_time)),
            (14, struct.pack("<H", mod_date)), (16, struct.pack("<I", crc)),
            (20, struct.pack("<I", csize)), (24, struct.pack("<I", usize)),
            (28, struct.pack("<H", name_len)), (34, b"\0\0"), (42, b"\0\0\0\0"),
        ]
        for offset, expected in known_fields:
            available = max(0, min(len(expected), len(trailing) - offset))
            if available and trailing[offset : offset + available] != expected[:available]:
                raise FormatError(f"{record.name!r} has an inconsistent truncated central header")
        if len(trailing) >= 46:
            central = struct.unpack_from("<IHHHHHHIIIHHHHHII", trailing, 0)
            cname_len, cextra_len, comment_len = central[10:13]
            central_variable = 46 + cname_len + cextra_len + comment_len
            available_name = max(0, min(cname_len, len(trailing) - 46))
            expected_name = local_name.encode("ascii")
            if cname_len != name_len or trailing[46 : 46 + available_name] != expected_name[:available_name]:
                raise FormatError(f"{record.name!r} has an inconsistent truncated central name")
            if len(trailing) >= central_variable:
                eocd_prefix = trailing[central_variable:]
                end_signature = b"PK\x05\x06"
                if len(eocd_prefix) < 4:
                    if eocd_prefix != end_signature[: len(eocd_prefix)]:
                        raise FormatError(f"{record.name!r} has invalid end-record prefix bytes")
                elif eocd_prefix[:4] != end_signature:
                    raise FormatError(f"{record.name!r} has no ZIP end-record prefix")
                stage = "end_record"

    timestamp = _dos_datetime(mod_date, mod_time)
    recovered = ExtractedMember(
        record, _safe_output_path(record.name), output, actual_crc, method,
        timestamp, len(chunk), "zip-recovered",
    )
    return ({
        "name": record.name,
        "available": len(chunk),
        "expected_span": record.stored_span,
        "stage": stage,
        "compressed_available": csize,
        "compressed_size": csize,
        "crc32": f"{crc:08x}",
        "dos_datetime": timestamp,
        "version_needed": version,
        "payload_recovered": True,
    }, recovered)


def _validate_partial_zip(chunk: bytes, record: FileRecord) -> dict[str, Any]:
    """Compatibility wrapper used by external validation callers."""
    metadata, _ = _parse_partial_zip(chunk, record)
    return metadata


def _parse_raw_member(chunk: bytes, record: FileRecord) -> ExtractedMember:
    if record.stored_span != record.unpacked_size or len(chunk) != record.stored_span:
        raise FormatError(f"raw member {record.name!r} has inconsistent sizes")
    return ExtractedMember(
        record, _safe_output_path(record.name), chunk,
        binascii.crc32(chunk) & 0xFFFFFFFF, -1, None, len(chunk), "raw",
    )


@dataclass
class ParsedSetup:
    source_size: int
    source_sha256: str
    pe: PEInfo
    database: Database
    helper: bytes
    members: list[ExtractedMember]
    partial: dict[str, Any] | None
    partial_bytes: bytes = field(repr=False)


def parse_setup(data: bytes) -> ParsedSetup:
    pe = _parse_pe(data, label="outer setup PE")
    database = _locate_database(data, pe)
    helper_record = database.files[0]
    if helper_record.name.replace("/", "\\").casefold() not in ("dunzipnt.dll", "dunzip32.dll"):
        raise FormatError("first file record is not a supported embedded DynaZIP helper")
    if helper_record.unpacked_size != helper_record.stored_span:
        raise FormatError("embedded DynaZIP helper sizes disagree")
    helper_start = database.end
    _need(data, helper_start, helper_record.stored_span, "embedded DynaZIP helper")
    helper = data[helper_start : helper_start + helper_record.stored_span]
    _parse_pe(helper, exact_size=True, label="embedded DynaZIP helper")

    cursor = helper_start + helper_record.stored_span
    members: list[ExtractedMember] = []
    partial: dict[str, Any] | None = None
    partial_bytes = b""
    for record in database.files[1:]:
        remaining = len(data) - cursor
        if remaining == 0:
            break
        if remaining < record.stored_span:
            partial_bytes = data[cursor:]
            if record.stored_span == record.unpacked_size:
                partial = {
                    "name": record.name,
                    "available": len(partial_bytes),
                    "expected_span": record.stored_span,
                    "stage": "raw_data",
                    "payload_recovered": False,
                }
            else:
                partial, recovered = _parse_partial_zip(partial_bytes, record)
                if recovered is not None:
                    members.append(recovered)
            cursor = len(data)
            break
        chunk = data[cursor : cursor + record.stored_span]
        if record.stored_span == record.unpacked_size:
            members.append(_parse_raw_member(chunk, record))
        else:
            members.append(_parse_complete_zip(chunk, record))
        cursor += record.stored_span
    if cursor != len(data):
        if len(members) == len(database.files) - 1:
            raise FormatError(f"{len(data) - cursor} unexplained bytes follow the last declared member")
        raise FormatError(f"unexplained bytes begin at file offset 0x{cursor:x}")
    return ParsedSetup(
        len(data), hashlib.sha256(data).hexdigest(), pe, database, helper,
        members, partial, partial_bytes,
    )


def _metadata(parsed: ParsedSetup, input_path: Path) -> dict[str, Any]:
    db = parsed.database
    return {
        "format": "AOL RS Setup prefix image",
        "input": str(input_path),
        "input_size": parsed.source_size,
        "input_sha256": parsed.source_sha256,
        "variant": db.variant,
        "outer_pe": {
            "bytes": parsed.pe.raw_end,
            "export_name": parsed.pe.export_name,
            "machine": parsed.pe.machine,
            "timestamp": parsed.pe.timestamp,
            "section_count": parsed.pe.sections,
        },
        "database": {
            "offset": db.start,
            "size": db.end - db.start,
            "file_table_offset": db.file_table_start,
            "configuration_prefix_size": len(db.configuration_prefix),
            "configuration_prefix_sha256": hashlib.sha256(db.configuration_prefix).hexdigest(),
            "header_strings": db.header_strings,
            "scalars": db.scalars,
            "resource_ids": db.resource_ids,
            "string_collections": db.string_collections,
            "u16_arrays": db.u16_arrays,
            "extra_scalars": db.extra_scalars,
            "complex_groups": db.complex_groups,
            "declared_records": len(db.files),
        },
        "embedded_helper": {
            "name": db.files[0].name,
            "size": len(parsed.helper),
            "sha256": hashlib.sha256(parsed.helper).hexdigest(),
        },
        "extracted_count": len(parsed.members),
        "extracted_unpacked_bytes": sum(len(member.data) for member in parsed.members),
        "members": [
            {
                "path": str(member.path),
                "unpacked_size": len(member.data),
                "zip_span": member.zip_span,
                "crc32": f"{member.crc32:08x}",
                "method": member.method,
                "storage": member.storage,
                "dos_datetime": member.dos_datetime,
                "sha256": hashlib.sha256(member.data).hexdigest(),
            }
            for member in parsed.members
        ],
        "partial_member": parsed.partial,
    }


def _chmod_tree(root: Path) -> None:
    for directory, dirs, files in os.walk(root):
        os.chmod(directory, 0o775)
        for name in dirs:
            os.chmod(Path(directory, name), 0o775)
        for name in files:
            os.chmod(Path(directory, name), 0o664)


def extract(parsed: ParsedSetup, input_path: Path, output_dir: Path, include_all: bool) -> None:
    # Validate existing path conflicts before any output is changed.
    targets = [output_dir / member.path for member in parsed.members]
    if include_all:
        targets.extend([
            output_dir / "__aolsetup__" / "metadata.json",
            output_dir / "__aolsetup__" / "dunzipnt.dll",
        ])
        if parsed.partial:
            targets.append(output_dir / "__aolsetup__" / "partial-member.zip.part")
    for target in targets:
        parent = target.parent
        while parent != output_dir.parent and parent != output_dir:
            if parent.exists() and not parent.is_dir():
                raise OSError(f"output parent exists as a non-directory: {parent}")
            parent = parent.parent
        if target.exists() and target.is_dir():
            raise OSError(f"output file exists as a directory: {target}")
    if output_dir.exists() and not output_dir.is_dir():
        raise OSError(f"output path exists and is not a directory: {output_dir}")

    output_parent = output_dir.parent.resolve()
    output_parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".aolSetup-", dir=output_parent))
    try:
        for member in parsed.members:
            target = stage / member.path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(member.data)
            if member.dos_datetime is not None:
                try:
                    stamp = datetime(*member.dos_datetime).timestamp()
                    os.utime(target, (stamp, stamp))
                except (OSError, OverflowError, ValueError):
                    pass
        if include_all:
            auxiliary = stage / "__aolsetup__"
            auxiliary.mkdir(parents=True, exist_ok=True)
            (auxiliary / "dunzipnt.dll").write_bytes(parsed.helper)
            if parsed.partial:
                (auxiliary / "partial-member.zip.part").write_bytes(parsed.partial_bytes)
            (auxiliary / "metadata.json").write_text(
                json.dumps(_metadata(parsed, input_path), indent=2, ensure_ascii=True) + "\n",
                encoding="utf-8",
            )
        _chmod_tree(stage)
        output_dir.mkdir(parents=True, exist_ok=True)
        for source in sorted(stage.rglob("*"), key=lambda p: (not p.is_dir(), len(p.parts))):
            relative = source.relative_to(stage)
            destination = output_dir / relative
            if source.is_dir():
                destination.mkdir(parents=True, exist_ok=True)
                os.chmod(destination, 0o775)
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                os.replace(source, destination)
                os.chmod(destination, 0o664)
        os.chmod(output_dir, 0o775)
    finally:
        shutil.rmtree(stage, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="aolSetup.py",
        description="Extract validated files from an AOL Setup RS prefix image.",
    )
    parser.add_argument("--all", action="store_true", help="also emit helper, partial member, and JSON metadata")
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputDir", type=Path)
    args = parser.parse_args(argv)
    try:
        data = args.inputFile.read_bytes()
        parsed = parse_setup(data)
        extract(parsed, args.inputFile, args.outputDir, args.all)
    except (FormatError, OSError) as exc:
        print(f"aolSetup.py: {exc}", file=sys.stderr)
        return 1
    partial_note = ""
    if parsed.partial:
        disposition = "payload recovered" if parsed.partial.get("payload_recovered") else "not extracted"
        partial_note = (
            f"; input ends {parsed.partial['available']} bytes into "
            f"{parsed.partial['name']} ({disposition})"
        )
    print(
        f"extracted {len(parsed.members)} files "
        f"({sum(len(member.data) for member in parsed.members)} bytes) to {args.outputDir}{partial_note}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

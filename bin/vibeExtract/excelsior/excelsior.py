#!/usr/bin/env python3
# Vibe coded by Codex
"""Extract files from Excelsior Installer II executable containers."""

from __future__ import annotations

import argparse
import hashlib
import json
import lzma
import os
import stat
import struct
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path, PureWindowsPath
from typing import Any, Iterable


MAGIC = b"ExcelsiorII1"
OVERLAY_HEADER_SIZE = 40
METADATA_COMMON_ROOT_SIZE = 0xB4
IO_CHUNK = 1 << 16


class NotExcelsiorError(Exception):
    """The input is not the Excelsior II container handled here."""


class DamagedExcelsiorError(Exception):
    """The input has the Excelsior identity but cannot be parsed further."""


@dataclass
class PEInfo:
    raw_end: int
    security_offset: int
    security_size: int
    section_count: int
    machine: int


@dataclass
class LZMAResult:
    expected_size: int
    data: bytes
    complete: bool
    properties: bytes
    error: str | None = None


@dataclass
class FileRecord:
    path: str
    timestamp: int
    size: int
    auxiliary: int
    processing_flag: bool
    serialized_offset: int
    payload_offset: int = 0

    @property
    def is_directory(self) -> bool:
        return self.size == -1


@dataclass
class PackageDescriptor:
    name: str
    count: int
    reserved: int
    payload_offset: int
    payload_size: int
    table_offset: int
    records: list[FileRecord] = field(default_factory=list)


@dataclass
class Metadata:
    raw: bytes
    complete: bool
    version_fields: bytes
    primary_offset: int
    primary_record_size: int
    internal: PackageDescriptor
    installed: PackageDescriptor
    root_strings: dict[str, str | None]
    collections: dict[str, list[dict[str, Any]]]


@dataclass
class Container:
    source: Path
    raw: bytes
    pe: PEInfo
    overlay_offset: int
    metadata_record_size: int
    metadata_offset: int
    metadata_uncompressed_size: int
    bootstrap_size: int
    primary_offset: int
    primary_record_size: int
    primary: LZMAResult
    metadata_stream: LZMAResult
    metadata: Metadata
    certificate: bytes
    padding_after_metadata: bytes
    warnings: list[str] = field(default_factory=list)


def _need(blob: bytes, offset: int, size: int, what: str, *, wrong: bool = False) -> None:
    if offset < 0 or size < 0 or offset + size > len(blob):
        exc = NotExcelsiorError if wrong else DamagedExcelsiorError
        raise exc(f"{what} is outside the available input")


def _u16(blob: bytes, offset: int) -> int:
    return struct.unpack_from("<H", blob, offset)[0]


def _u32(blob: bytes, offset: int) -> int:
    return struct.unpack_from("<I", blob, offset)[0]


def _i64(blob: bytes, offset: int) -> int:
    return struct.unpack_from("<q", blob, offset)[0]


def _u64(blob: bytes, offset: int) -> int:
    return struct.unpack_from("<Q", blob, offset)[0]


def parse_pe(blob: bytes, *, require_complete_sections: bool) -> PEInfo:
    """Parse only the PE fields needed to find an overlay and certificate table."""
    _need(blob, 0, 0x40, "DOS header", wrong=True)
    if blob[:2] != b"MZ":
        raise NotExcelsiorError("input has no DOS MZ signature")
    pe_offset = _u32(blob, 0x3C)
    _need(blob, pe_offset, 24, "PE signature and COFF header", wrong=True)
    if blob[pe_offset : pe_offset + 4] != b"PE\0\0":
        raise NotExcelsiorError("input has no PE signature")

    machine = _u16(blob, pe_offset + 4)
    section_count = _u16(blob, pe_offset + 6)
    optional_size = _u16(blob, pe_offset + 20)
    if machine != 0x014C or section_count == 0 or optional_size < 96:
        raise NotExcelsiorError("input is not a 32-bit x86 PE image")
    optional = pe_offset + 24
    _need(blob, optional, optional_size, "PE optional header", wrong=True)
    if _u16(blob, optional) != 0x010B:
        raise NotExcelsiorError("input is not a PE32 image")

    size_of_headers = _u32(blob, optional + 60)
    directory_count = _u32(blob, optional + 92)
    security_offset = 0
    security_size = 0
    if directory_count > 4 and optional_size >= 96 + 5 * 8:
        security_offset = _u32(blob, optional + 96 + 4 * 8)
        security_size = _u32(blob, optional + 96 + 4 * 8 + 4)
        if bool(security_offset) != bool(security_size):
            raise NotExcelsiorError("PE security directory has only one nonzero member")

    section_table = optional + optional_size
    _need(blob, section_table, section_count * 40, "PE section table", wrong=True)
    raw_end = size_of_headers
    for index in range(section_count):
        entry = section_table + index * 40
        raw_size = _u32(blob, entry + 16)
        raw_offset = _u32(blob, entry + 20)
        if raw_size:
            if raw_offset == 0:
                raise NotExcelsiorError("PE section has data but no file offset")
            raw_end = max(raw_end, raw_offset + raw_size)
            if require_complete_sections and raw_offset + raw_size > len(blob):
                raise NotExcelsiorError("PE image is truncated before its overlay")
    return PEInfo(raw_end, security_offset, security_size, section_count, machine)


def _decode_lzma_properties(properties: bytes) -> dict[str, int]:
    if len(properties) != 5:
        raise DamagedExcelsiorError("LZMA property block is not five bytes")
    coded = properties[0]
    if coded >= 9 * 5 * 5:
        raise DamagedExcelsiorError("invalid LZMA lc/lp/pb property byte")
    lc = coded % 9
    coded //= 9
    lp = coded % 5
    pb = coded // 5
    dictionary = _u32(properties, 1)
    if dictionary == 0:
        raise DamagedExcelsiorError("invalid zero LZMA dictionary size")
    return {
        "id": lzma.FILTER_LZMA1,
        "dict_size": dictionary,
        "lc": lc,
        "lp": lp,
        "pb": pb,
    }


def decompress_record(blob: bytes, offset: int, total_size: int, label: str) -> LZMAResult:
    """Decode an end-marker-free size+properties+raw-LZMA1 record, retaining a prefix."""
    if total_size < 13:
        raise DamagedExcelsiorError(f"{label} record is shorter than its 13-byte header")
    _need(blob, offset, min(total_size, 13), f"{label} record header")
    expected = _u64(blob, offset)
    properties = blob[offset + 8 : offset + 13]
    filters = [_decode_lzma_properties(properties)]
    available_end = min(len(blob), offset + total_size)
    compressed = memoryview(blob)[offset + 13 : available_end]
    decoder = lzma.LZMADecompressor(format=lzma.FORMAT_RAW, filters=filters)
    output = bytearray()
    error: str | None = None
    position = 0

    try:
        while position < len(compressed) and len(output) < expected:
            chunk = compressed[position : position + IO_CHUNK]
            position += len(chunk)
            output.extend(decoder.decompress(chunk, max_length=expected - len(output)))
            while not decoder.needs_input and len(output) < expected:
                before = len(output)
                output.extend(decoder.decompress(b"", max_length=expected - len(output)))
                if len(output) == before:
                    break
        while not decoder.needs_input and len(output) < expected:
            before = len(output)
            output.extend(decoder.decompress(b"", max_length=expected - len(output)))
            if len(output) == before:
                break
    except lzma.LZMAError as exc:
        error = str(exc)

    if len(output) > expected:
        error = f"decoded beyond declared size {expected}"
        del output[expected:]
    complete = (
        error is None
        and len(output) == expected
        and available_end == offset + total_size
        and not decoder.unused_data
    )
    if not complete and error is None:
        if len(output) != expected:
            error = f"decoded {len(output)} of {expected} declared bytes"
        elif available_end != offset + total_size:
            error = "compressed record is truncated"
        elif decoder.unused_data:
            error = "compressed record contains unused trailing data"
        else:
            error = "compressed record contains invalid trailing data"
    return LZMAResult(expected, bytes(output), complete, properties, error)


def decode_x86_filter(data: bytes, *, ip: int = 0, state: int = 0) -> bytes:
    """Invert the exact LZMA SDK x86 BCJ transform used by the installer."""
    result = bytearray(data)
    size = len(result)
    if size < 5:
        return bytes(result)
    position = 0
    previous_position = -1
    previous_mask = state & 7
    mask_allowed = (1, 1, 1, 0, 1, 0, 0, 0)
    mask_bits = (0, 1, 2, 2, 3, 3, 3, 3)
    ip = (ip + 5) & 0xFFFFFFFF
    limit = size - 5

    while True:
        candidate = position
        while candidate <= limit and (result[candidate] & 0xFE) != 0xE8:
            candidate += 1
        position = candidate
        if candidate > limit:
            break
        distance = position - previous_position
        if distance > 3:
            previous_mask = 0
        else:
            previous_mask = (previous_mask << (distance - 1)) & 7
            if previous_mask:
                check = result[position + 4 - mask_bits[previous_mask]]
                if not mask_allowed[previous_mask] or check in (0x00, 0xFF):
                    previous_position = position
                    previous_mask = ((previous_mask << 1) | 1) & 7
                    position += 1
                    continue
        previous_position = position
        if result[position + 4] in (0x00, 0xFF):
            source = int.from_bytes(result[position + 1 : position + 5], "little")
            while True:
                destination = (source - (ip + position)) & 0xFFFFFFFF
                if previous_mask == 0:
                    break
                bit_index = mask_bits[previous_mask] * 8
                check = (destination >> (24 - bit_index)) & 0xFF
                if check not in (0x00, 0xFF):
                    break
                source = destination ^ ((1 << (32 - bit_index)) - 1)
            result[position + 1 : position + 4] = (destination & 0xFFFFFF).to_bytes(3, "little")
            result[position + 4] = 0xFF if destination & 0x01000000 else 0x00
            position += 5
        else:
            previous_mask = ((previous_mask << 1) | 1) & 7
            position += 1
    return bytes(result)


def _metadata_string(raw: bytes, offset: int, field: str, *, optional: bool = True) -> str | None:
    if offset == 0 and optional:
        return None
    if offset == 0 or offset >= len(raw) or offset & 1:
        raise DamagedExcelsiorError(f"metadata {field} has invalid UTF-16 offset 0x{offset:x}")
    end = offset
    while end + 1 < len(raw) and raw[end : end + 2] != b"\0\0":
        end += 2
    if end + 1 >= len(raw):
        raise DamagedExcelsiorError(f"metadata {field} has an unterminated UTF-16 string")
    try:
        return raw[offset:end].decode("utf-16le")
    except UnicodeDecodeError as exc:
        raise DamagedExcelsiorError(f"metadata {field} is invalid UTF-16LE") from exc


def _bounded_table(raw: bytes, count: int, offset: int, stride: int, field: str) -> None:
    if count > len(raw) // max(stride, 1):
        raise DamagedExcelsiorError(f"metadata {field} count is impossible")
    _need(raw, offset, count * stride, f"metadata {field} table")


def _parse_package(raw: bytes, offset: int, name: str, *, tolerant: bool) -> PackageDescriptor:
    _need(raw, offset, 32, f"metadata {name} descriptor")
    count = _u32(raw, offset)
    reserved = _u32(raw, offset + 4)
    payload_offset = _u64(raw, offset + 8)
    payload_size = _u64(raw, offset + 16)
    table_offset = _u64(raw, offset + 24)
    descriptor = PackageDescriptor(name, count, reserved, payload_offset, payload_size, table_offset)
    if reserved != 0:
        raise DamagedExcelsiorError(f"metadata {name} descriptor reserved field is nonzero")
    if table_offset > len(raw):
        if tolerant:
            return descriptor
        raise DamagedExcelsiorError(f"metadata {name} record table is outside metadata")
    available_count = min(count, (len(raw) - table_offset) // 24)
    if available_count != count and not tolerant:
        raise DamagedExcelsiorError(f"metadata {name} record table is truncated")

    payload_cursor = payload_offset
    for index in range(available_count):
        record_offset = table_offset + index * 24
        path_offset = _u32(raw, record_offset)
        try:
            path = _metadata_string(raw, path_offset, f"{name} path {index}", optional=False)
        except DamagedExcelsiorError:
            if tolerant:
                break
            raise
        assert path is not None
        timestamp = _u32(raw, record_offset + 4)
        size = _i64(raw, record_offset + 8)
        auxiliary = _u32(raw, record_offset + 16)
        processing = raw[record_offset + 20] != 0
        if size < -1:
            if tolerant:
                break
            raise DamagedExcelsiorError(f"metadata {name} record {index} has invalid size {size}")
        record = FileRecord(path, timestamp, size, auxiliary, processing, record_offset)
        if not record.is_directory:
            record.payload_offset = payload_cursor
            payload_cursor += size
        descriptor.records.append(record)
    if len(descriptor.records) == count and payload_cursor != payload_offset + payload_size:
        raise DamagedExcelsiorError(
            f"metadata {name} payload size does not equal the sum of its regular files"
        )
    return descriptor


def _parse_root_collections(
    raw: bytes,
    *,
    shortcut_fields: int,
    modern_path_arrays: bool,
    legacy_second_path_array: bool,
) -> dict[str, list[dict[str, Any]]]:
    """Parse every non-package variable table referenced by the fixed root."""
    result: dict[str, list[dict[str, Any]]] = {}

    def strings_at(count_offset: int, table_offset: int, name: str) -> list[dict[str, Any]]:
        count, start = _u32(raw, count_offset), _u32(raw, table_offset)
        _bounded_table(raw, count, start, 4, name)
        return [
            {"value": _metadata_string(raw, _u32(raw, start + i * 4), f"{name}[{i}]", optional=False)}
            for i in range(count)
        ]

    count, start = _u32(raw, 0x9C), _u32(raw, 0xA0)
    _bounded_table(raw, count, start, 8, "command pairs")
    result["command_pairs"] = [
        {
            "program": _metadata_string(raw, _u32(raw, start + i * 8), f"command {i} program", optional=False),
            "arguments": _metadata_string(raw, _u32(raw, start + i * 8 + 4), f"command {i} arguments"),
        }
        for i in range(count)
    ]

    count, start = _u32(raw, shortcut_fields), _u32(raw, shortcut_fields + 4)
    _bounded_table(raw, count, start, 28, "shortcut records")
    result["shortcuts"] = []
    for i in range(count):
        base = start + i * 28
        result["shortcuts"].append(
            {
                "kind": _u32(raw, base),
                "title": _metadata_string(raw, _u32(raw, base + 4), f"shortcut {i} title", optional=False),
                "icon": _metadata_string(raw, _u32(raw, base + 8), f"shortcut {i} icon"),
                "icon_index": _u32(raw, base + 12),
                "working_directory": _metadata_string(raw, _u32(raw, base + 16), f"shortcut {i} working directory"),
                "target": _metadata_string(raw, _u32(raw, base + 20), f"shortcut {i} target", optional=False),
                "arguments": _metadata_string(raw, _u32(raw, base + 24), f"shortcut {i} arguments"),
            }
        )

    association_fields = shortcut_fields + 8
    count, start = _u32(raw, association_fields), _u32(raw, association_fields + 4)
    _bounded_table(raw, count, start, 24, "file association records")
    result["file_associations"] = []
    for i in range(count):
        base = start + i * 24
        result["file_associations"].append(
            {
                "extension": _metadata_string(raw, _u32(raw, base), f"association {i} extension", optional=False),
                "type_name": _metadata_string(raw, _u32(raw, base + 4), f"association {i} type name", optional=False),
                "description": _metadata_string(raw, _u32(raw, base + 8), f"association {i} description"),
                "executable": _metadata_string(raw, _u32(raw, base + 12), f"association {i} executable", optional=False),
                "arguments": _metadata_string(raw, _u32(raw, base + 16), f"association {i} arguments"),
                "flag": raw[base + 20] != 0,
            }
        )

    environment_fields = shortcut_fields + 16
    count, start = _u32(raw, environment_fields), _u32(raw, environment_fields + 4)
    _bounded_table(raw, count, start, 20, "post-install action records")
    result["postinstall_actions"] = []
    for i in range(count):
        base = start + i * 20
        result["postinstall_actions"].append(
            {
                "kind": _u32(raw, base),
                "label": _metadata_string(raw, _u32(raw, base + 4), f"post-install action {i} label", optional=False),
                "executable": _metadata_string(raw, _u32(raw, base + 8), f"post-install action {i} executable"),
                "arguments": _metadata_string(raw, _u32(raw, base + 12), f"post-install action {i} arguments"),
                "mode": raw[base + 16],
                "selected_by_default": raw[base + 17] != 0,
            }
        )

    service_fields = shortcut_fields + 24
    count, start = _u32(raw, service_fields), _u32(raw, service_fields + 4)
    _bounded_table(raw, count, start, 28, "service records")
    result["services"] = []
    for i in range(count):
        base = start + i * 28
        dependency_count, dependency_offset = _u32(raw, base + 16), _u32(raw, base + 20)
        _bounded_table(raw, dependency_count, dependency_offset, 4, f"service {i} dependencies")
        dependencies = [
            _metadata_string(raw, _u32(raw, dependency_offset + j * 4), f"service {i} dependency {j}", optional=False)
            for j in range(dependency_count)
        ]
        result["services"].append(
            {
                "name": _metadata_string(raw, _u32(raw, base), f"service {i} name", optional=False),
                "display_name": _metadata_string(raw, _u32(raw, base + 4), f"service {i} display name"),
                "description": _metadata_string(raw, _u32(raw, base + 8), f"service {i} description"),
                "executable": _metadata_string(raw, _u32(raw, base + 12), f"service {i} executable", optional=False),
                "dependencies": dependencies,
                "start_type": raw[base + 24],
                "error_control": raw[base + 25],
                "flag": raw[base + 26] != 0,
            }
        )

    if modern_path_arrays:
        result["remove_paths"] = strings_at(shortcut_fields + 32, shortcut_fields + 36, "remove paths")
        result["generated_paths"] = strings_at(shortcut_fields + 40, shortcut_fields + 44, "generated paths")
    else:
        result["generated_paths"] = strings_at(shortcut_fields + 32, shortcut_fields + 36, "generated paths")
        if legacy_second_path_array:
            result["legacy_paths"] = strings_at(shortcut_fields + 40, shortcut_fields + 44, "legacy paths")
    return result


def _validate_metadata_coverage(
    raw: bytes,
    metadata: Metadata,
    *,
    root_size: int,
    shortcut_fields: int,
    modern_path_arrays: bool,
    legacy_second_path_array: bool,
) -> None:
    """Prove that every metadata byte belongs to a declared object or fixed padding."""
    covered = bytearray(len(raw))

    def mark(offset: int, size: int, field: str) -> None:
        _need(raw, offset, size, f"metadata {field}")
        covered[offset : offset + size] = b"\x01" * size

    def mark_string(offset: int, field: str) -> None:
        if not offset:
            return
        _metadata_string(raw, offset, field)
        end = offset
        while raw[end : end + 2] != b"\0\0":
            end += 2
        mark(offset, end + 2 - offset, field)

    mark(0, root_size, "fixed root")
    aligned_root = (root_size + 7) & ~7
    if aligned_root > root_size:
        _need(raw, root_size, aligned_root - root_size, "root alignment padding")
        if any(raw[root_size:aligned_root]):
            raise DamagedExcelsiorError("metadata root alignment padding is nonzero")
        mark(root_size, aligned_root - root_size, "root alignment padding")

    direct_strings = list(range(0x68, 0x90, 4)) + [0x98, 0xA4, 0xA8, 0xAC, 0xB0]
    direct_strings += [0xB4] if modern_path_arrays else [0xB4, 0xB8]
    for field_offset in direct_strings:
        mark_string(_u32(raw, field_offset), f"root string at 0x{field_offset:x}")

    for package in (metadata.internal, metadata.installed):
        mark(package.table_offset, package.count * 24, f"{package.name} record table")
        for index, record in enumerate(package.records):
            mark_string(_u32(raw, record.serialized_offset), f"{package.name} path {index}")

    pair_count, pair_offset = _u32(raw, 0x9C), _u32(raw, 0xA0)
    mark(pair_offset, pair_count * 8, "command-pair table")
    for index in range(pair_count):
        mark_string(_u32(raw, pair_offset + index * 8), f"command {index} program")
        mark_string(_u32(raw, pair_offset + index * 8 + 4), f"command {index} arguments")

    table_layouts = (
        (shortcut_fields, 28, (4, 8, 16, 20, 24), "shortcut"),
        (shortcut_fields + 8, 24, (0, 4, 8, 12, 16), "association"),
        (shortcut_fields + 16, 20, (4, 8, 12), "post-install action"),
    )
    for fields, stride, string_fields, name in table_layouts:
        count, offset = _u32(raw, fields), _u32(raw, fields + 4)
        mark(offset, count * stride, f"{name} table")
        for index in range(count):
            for relative in string_fields:
                mark_string(_u32(raw, offset + index * stride + relative), f"{name} {index} string")

    service_fields = shortcut_fields + 24
    service_count, service_offset = _u32(raw, service_fields), _u32(raw, service_fields + 4)
    mark(service_offset, service_count * 28, "service table")
    for index in range(service_count):
        base = service_offset + index * 28
        for relative in (0, 4, 8, 12):
            mark_string(_u32(raw, base + relative), f"service {index} string")
        dependency_count, dependency_offset = _u32(raw, base + 16), _u32(raw, base + 20)
        mark(dependency_offset, dependency_count * 4, f"service {index} dependency table")
        for dependency in range(dependency_count):
            mark_string(
                _u32(raw, dependency_offset + dependency * 4),
                f"service {index} dependency {dependency}",
            )

    array_count = 2 if modern_path_arrays or legacy_second_path_array else 1
    for array_index in range(array_count):
        fields = shortcut_fields + 32 + array_index * 8
        count, offset = _u32(raw, fields), _u32(raw, fields + 4)
        mark(offset, count * 4, f"path array {array_index}")
        for index in range(count):
            mark_string(_u32(raw, offset + index * 4), f"path array {array_index} item {index}")

    try:
        first_uncovered = covered.index(0)
    except ValueError:
        return
    end = first_uncovered + 1
    while end < len(raw) and not covered[end]:
        end += 1
    raise DamagedExcelsiorError(
        f"metadata bytes 0x{first_uncovered:x}..0x{end - 1:x} are not referenced by its object graph"
    )


def parse_metadata(raw: bytes, *, complete: bool) -> Metadata:
    if len(raw) < 12 or raw[:12] != MAGIC:
        raise DamagedExcelsiorError("decoded metadata has no ExcelsiorII1 signature")
    tolerant = not complete
    if len(raw) < METADATA_COMMON_ROOT_SIZE:
        raise DamagedExcelsiorError("decoded metadata root is truncated")
    internal = _parse_package(raw, 0x28, "internal", tolerant=tolerant)
    installed = _parse_package(raw, 0x48, "installed", tolerant=tolerant)

    version_fields = raw[0x0C:0x18]
    format_major = version_fields[0]
    format_minor = version_fields[1]
    generator_family = version_fields[4]
    if format_major != 1 or format_minor not in (0, 5, 6, 7):
        raise DamagedExcelsiorError(
            f"unsupported metadata schema version {format_major}.{format_minor}"
        )
    modern_schema = format_minor >= 6
    legacy_second_path_array = format_minor == 0 and generator_family == 2
    shortcut_fields = 0xB8 if modern_schema else 0xBC
    root_size = shortcut_fields + (48 if modern_schema else 40)
    if legacy_second_path_array:
        root_size += 8
    _need(raw, 0, root_size, "decoded metadata root")

    root_string_fields = {
        "product_name": 0x68,
        "display_name": 0x6C,
        "publisher_or_variant": 0x70,
        "product_identifier": 0x74,
        "license_text": 0x78,
        "splash_image": 0x7C,
        "uninstaller_name": 0x80,
        "installer_library": 0x84,
        "auxiliary_library": 0x88,
        "uninstaller_library": 0x8C,
        "root_option_string": 0x98,
        "pair_name": 0xA4,
        "pair_value": 0xA8,
        "default_install_directory": 0xAC,
        "product_short_name": 0xB0,
    }
    if modern_schema:
        root_string_fields["launcher_or_variant"] = 0xB4
    else:
        root_string_fields["legacy_option_string"] = 0xB4
        root_string_fields["launcher_or_variant"] = 0xB8
    root_strings: dict[str, str | None] = {}
    for name, offset in root_string_fields.items():
        try:
            root_strings[name] = _metadata_string(raw, _u32(raw, offset), name)
        except DamagedExcelsiorError:
            if not tolerant:
                raise
            root_strings[name] = None
    collections = (
        _parse_root_collections(
            raw,
            shortcut_fields=shortcut_fields,
            modern_path_arrays=modern_schema,
            legacy_second_path_array=legacy_second_path_array,
        )
        if complete
        else {}
    )
    metadata = Metadata(
        raw=raw,
        complete=complete,
        version_fields=version_fields,
        primary_offset=_u64(raw, 0x18),
        primary_record_size=_u64(raw, 0x20),
        internal=internal,
        installed=installed,
        root_strings=root_strings,
        collections=collections,
    )
    if complete:
        _validate_metadata_coverage(
            raw,
            metadata,
            root_size=root_size,
            shortcut_fields=shortcut_fields,
            modern_path_arrays=modern_schema,
            legacy_second_path_array=legacy_second_path_array,
        )
    return metadata


def _validate_certificate_table(raw: bytes, offset: int, size: int) -> bytes:
    if not size:
        return b""
    if offset & 7:
        raise DamagedExcelsiorError("Authenticode certificate table is not eight-byte aligned")
    _need(raw, offset, size, "Authenticode certificate table")
    cursor, end = offset, offset + size
    while cursor < end:
        _need(raw, cursor, 8, "WIN_CERTIFICATE header")
        length = _u32(raw, cursor)
        revision = _u16(raw, cursor + 4)
        certificate_type = _u16(raw, cursor + 6)
        if length < 8 or cursor + length > end:
            raise DamagedExcelsiorError("invalid WIN_CERTIFICATE length")
        if revision not in (0x0100, 0x0200) or certificate_type == 0:
            raise DamagedExcelsiorError("invalid WIN_CERTIFICATE header")
        aligned = (length + 7) & ~7
        if cursor + aligned > end:
            raise DamagedExcelsiorError("WIN_CERTIFICATE alignment exceeds certificate table")
        if any(raw[cursor + length : cursor + aligned]):
            raise DamagedExcelsiorError("WIN_CERTIFICATE alignment padding is nonzero")
        cursor += aligned
    if cursor != end:
        raise DamagedExcelsiorError("certificate table has an incomplete final entry")
    return raw[offset:end]


def inspect_container(source: os.PathLike[str] | str) -> Container:
    path = Path(source)
    raw = path.read_bytes()
    pe = parse_pe(raw, require_complete_sections=True)
    overlay = pe.raw_end
    _need(raw, overlay, OVERLAY_HEADER_SIZE, "Excelsior overlay header", wrong=True)
    if raw[overlay : overlay + 12] != MAGIC:
        raise NotExcelsiorError("PE overlay does not begin with ExcelsiorII1")

    metadata_record_size = _u32(raw, overlay + 0x0C)
    metadata_offset = _u64(raw, overlay + 0x10)
    metadata_uncompressed = _u32(raw, overlay + 0x18)
    bootstrap_size = _u32(raw, overlay + 0x1C)
    primary_offset = _u64(raw, overlay + 0x20)
    if primary_offset != overlay + OVERLAY_HEADER_SIZE:
        raise NotExcelsiorError("Excelsior primary stream does not follow its overlay header")
    if metadata_offset < primary_offset + 13 or metadata_record_size < 13:
        raise NotExcelsiorError("Excelsior stream offsets are structurally impossible")
    primary_record_size = metadata_offset - primary_offset

    warnings: list[str] = []
    metadata_stream = decompress_record(raw, metadata_offset, metadata_record_size, "metadata")
    if metadata_stream.expected_size != metadata_uncompressed:
        raise DamagedExcelsiorError("metadata size in overlay and LZMA record disagree")
    if metadata_stream.error:
        warnings.append(f"metadata stream: {metadata_stream.error}")
    metadata_decoded = decode_x86_filter(metadata_stream.data)
    metadata = parse_metadata(metadata_decoded, complete=metadata_stream.complete)
    if metadata.primary_offset != primary_offset or metadata.primary_record_size != primary_record_size:
        raise DamagedExcelsiorError("metadata copy of primary stream location/size disagrees with overlay")

    primary = decompress_record(raw, primary_offset, primary_record_size, "primary")
    if primary.error:
        warnings.append(f"primary stream: {primary.error}")
    primary.data = decode_x86_filter(primary.data)

    if metadata.internal.payload_offset != bootstrap_size:
        raise DamagedExcelsiorError("internal payload does not begin after declared bootstrap DLL")
    if metadata.installed.payload_offset != metadata.internal.payload_offset + metadata.internal.payload_size:
        raise DamagedExcelsiorError("installed payload does not follow internal payload")
    if metadata.installed.payload_offset + metadata.installed.payload_size != primary.expected_size:
        raise DamagedExcelsiorError("installed payload does not end at declared primary stream size")
    if primary.complete:
        if len(primary.data) < bootstrap_size or primary.data[:2] != b"MZ":
            raise DamagedExcelsiorError("primary stream does not begin with its bootstrap PE DLL")
        bootstrap_pe = parse_pe(primary.data[:bootstrap_size], require_complete_sections=True)
        if bootstrap_pe.raw_end != bootstrap_size:
            raise DamagedExcelsiorError("bootstrap DLL raw extent disagrees with overlay")

    metadata_end = metadata_offset + metadata_record_size
    padding = b""
    certificate = b""
    if pe.security_size:
        if pe.security_offset < metadata_end:
            raise DamagedExcelsiorError("Authenticode certificate overlaps Excelsior metadata")
        available_padding_end = min(len(raw), pe.security_offset)
        if metadata_end <= available_padding_end:
            padding = raw[metadata_end:available_padding_end]
            if any(padding):
                raise DamagedExcelsiorError("nonzero bytes occur between metadata and certificate")
            if len(padding) != (8 - (metadata_end & 7)):
                raise DamagedExcelsiorError("metadata-to-certificate padding has the wrong length")
        certificate = _validate_certificate_table(raw, pe.security_offset, pe.security_size)
        if pe.security_offset + pe.security_size != len(raw):
            warnings.append("bytes are missing after, or appended beyond, the certificate table")
    elif metadata_end != len(raw):
        if metadata_end < len(raw):
            warnings.append(f"{len(raw) - metadata_end} unaccounted trailing byte(s)")
        else:
            warnings.append(f"input ends {metadata_end - len(raw)} byte(s) inside metadata record")

    return Container(
        source=path,
        raw=raw,
        pe=pe,
        overlay_offset=overlay,
        metadata_record_size=metadata_record_size,
        metadata_offset=metadata_offset,
        metadata_uncompressed_size=metadata_uncompressed,
        bootstrap_size=bootstrap_size,
        primary_offset=primary_offset,
        primary_record_size=primary_record_size,
        primary=primary,
        metadata_stream=metadata_stream,
        metadata=metadata,
        certificate=certificate,
        padding_after_metadata=padding,
        warnings=warnings,
    )


def _safe_parts(installer_path: str) -> tuple[str, ...]:
    normalized = installer_path.replace("/", "\\")
    windows = PureWindowsPath(normalized)
    if windows.drive or windows.root or windows.is_absolute():
        raise DamagedExcelsiorError(f"unsafe absolute installer path: {installer_path!r}")
    parts = tuple(part for part in windows.parts if part not in ("", "."))
    if not parts or any(part == ".." for part in parts):
        raise DamagedExcelsiorError(f"unsafe installer path: {installer_path!r}")
    if any("\0" in part for part in parts):
        raise DamagedExcelsiorError(f"NUL in installer path: {installer_path!r}")
    return parts


def _record_outputs(container: Container, include_all: bool) -> list[tuple[FileRecord, tuple[str, ...]]]:
    output: list[tuple[FileRecord, tuple[str, ...]]] = []
    for record in container.metadata.installed.records:
        output.append((record, _safe_parts(record.path)))
    if include_all:
        for record in container.metadata.internal.records:
            output.append((record, ("_excelsior", "internal", *_safe_parts(record.path))))
    folded: dict[tuple[str, ...], bool] = {}
    for record, parts in output:
        key = tuple(part.casefold() for part in parts)
        if key in folded and folded[key] != record.is_directory:
            raise DamagedExcelsiorError(f"file/directory path collision: {record.path!r}")
        if key in folded and not record.is_directory:
            raise DamagedExcelsiorError(f"duplicate output file path: {record.path!r}")
        folded[key] = record.is_directory
    for key, is_directory in folded.items():
        for length in range(1, len(key)):
            ancestor = key[:length]
            if ancestor in folded and not folded[ancestor]:
                raise DamagedExcelsiorError(
                    f"output path is nested below a file: {'/'.join(key)!r}"
                )
    return output


def _ensure_no_symlink(path: Path, stop: Path) -> None:
    cursor = path
    while cursor != stop and cursor != cursor.parent:
        if cursor.is_symlink():
            raise OSError(f"refusing to extract through symlink: {cursor}")
        cursor = cursor.parent


def _preflight(output_dir: Path, outputs: Iterable[tuple[FileRecord, tuple[str, ...]]]) -> None:
    stop = output_dir.parent
    if output_dir.exists() and not output_dir.is_dir():
        raise OSError(f"output path exists but is not a directory: {output_dir}")
    for record, parts in outputs:
        target = output_dir.joinpath(*parts)
        _ensure_no_symlink(target, stop)
        cursor = output_dir
        for part in parts[:-1]:
            cursor /= part
            if cursor.exists() and not cursor.is_dir():
                raise OSError(f"output parent exists but is not a directory: {cursor}")
        if target.exists() and target.is_dir() != record.is_directory:
            raise OSError(f"output type conflicts with existing path: {target}")


def _write_file(target: Path, data: bytes, timestamp: int | None = None) -> None:
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o775)
    with tempfile.NamedTemporaryFile(prefix=".excelsior-", dir=target.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.chmod(temporary, 0o664)
        os.replace(temporary, target)
        if timestamp:
            os.utime(target, (timestamp, timestamp))
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def _jsonable_record(record: FileRecord) -> dict[str, Any]:
    return {
        "path": record.path,
        "type": "directory" if record.is_directory else "file",
        "timestamp_unix": record.timestamp,
        "size": record.size,
        "auxiliary": record.auxiliary,
        "processing_flag": record.processing_flag,
        "metadata_offset": record.serialized_offset,
        "primary_payload_offset": None if record.is_directory else record.payload_offset,
    }


def manifest_for(container: Container, extracted: list[str], skipped: list[str]) -> dict[str, Any]:
    props = _decode_lzma_properties(container.primary.properties)
    meta_props = _decode_lzma_properties(container.metadata_stream.properties)
    return {
        "format": "Excelsior Installer II",
        "source": str(container.source),
        "source_size": len(container.raw),
        "source_sha256": hashlib.sha256(container.raw).hexdigest(),
        "overlay_offset": container.overlay_offset,
        "primary": {
            "offset": container.primary_offset,
            "record_size": container.primary_record_size,
            "uncompressed_size": container.primary.expected_size,
            "complete": container.primary.complete,
            "lzma1": {k: v for k, v in props.items() if k != "id"},
        },
        "metadata": {
            "offset": container.metadata_offset,
            "record_size": container.metadata_record_size,
            "uncompressed_size": container.metadata_stream.expected_size,
            "complete": container.metadata_stream.complete,
            "version_fields_hex": container.metadata.version_fields.hex(),
            "lzma1": {k: v for k, v in meta_props.items() if k != "id"},
            "root_strings": container.metadata.root_strings,
            "collections": container.metadata.collections,
        },
        "bootstrap_dll_size": container.bootstrap_size,
        "authenticode_size": len(container.certificate),
        "packages": {
            "internal": [_jsonable_record(item) for item in container.metadata.internal.records],
            "installed": [_jsonable_record(item) for item in container.metadata.installed.records],
        },
        "extracted": extracted,
        "unavailable_due_to_damage": skipped,
        "warnings": container.warnings,
    }


def extract(container: Container, output_dir: os.PathLike[str] | str, *, include_all: bool) -> tuple[list[str], list[str]]:
    destination = Path(output_dir)
    outputs = _record_outputs(container, include_all)
    preflight_outputs = list(outputs)
    if include_all:
        extra_names = ["xinstres_lzma.dll", "metadata.bin", "manifest.json"]
        if container.certificate:
            extra_names.append("authenticode.bin")
        for name in extra_names:
            synthetic = FileRecord(name, 0, 0, 0, False, 0)
            preflight_outputs.append((synthetic, ("_excelsior", name)))
    _preflight(destination, preflight_outputs)

    extracted: list[str] = []
    skipped: list[str] = []
    safe_primary_length = len(container.primary.data)
    if not container.primary.complete:
        safe_primary_length = max(0, safe_primary_length - 4)

    destination.mkdir(parents=True, exist_ok=True, mode=0o775)
    os.chmod(destination, destination.stat().st_mode | stat.S_IRGRP | stat.S_IXGRP | stat.S_IRUSR | stat.S_IXUSR)
    for record, parts in outputs:
        target = destination.joinpath(*parts)
        relative = target.relative_to(destination).as_posix()
        if record.is_directory:
            target.mkdir(parents=True, exist_ok=True, mode=0o775)
            os.chmod(target, 0o775)
            extracted.append(relative + "/")
            continue
        end = record.payload_offset + record.size
        if end > safe_primary_length:
            skipped.append(relative)
            continue
        _write_file(target, container.primary.data[record.payload_offset:end], record.timestamp)
        extracted.append(relative)

    if include_all:
        extras = destination / "_excelsior"
        extras.mkdir(parents=True, exist_ok=True, mode=0o775)
        bootstrap_end = container.bootstrap_size
        if bootstrap_end <= safe_primary_length:
            _write_file(extras / "xinstres_lzma.dll", container.primary.data[:bootstrap_end])
            extracted.append("_excelsior/xinstres_lzma.dll")
        else:
            skipped.append("_excelsior/xinstres_lzma.dll")
        _write_file(extras / "metadata.bin", container.metadata.raw)
        extracted.append("_excelsior/metadata.bin")
        if container.certificate:
            _write_file(extras / "authenticode.bin", container.certificate)
            extracted.append("_excelsior/authenticode.bin")
        manifest = manifest_for(container, extracted, skipped)
        _write_file(
            extras / "manifest.json",
            (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        )
        extracted.append("_excelsior/manifest.json")
    return extracted, skipped


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="excelsior.py",
        description="Extract installed files from an Excelsior Installer II executable.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        dest="include_all",
        help="also write installer-internal resources and generated diagnostic metadata",
    )
    parser.add_argument("inputFile", help="Excelsior Installer executable")
    parser.add_argument("outputDir", help="destination directory (may already exist)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        container = inspect_container(args.inputFile)
        extracted, skipped = extract(container, args.outputDir, include_all=args.include_all)
    except NotExcelsiorError as exc:
        print(f"excelsior.py: unsupported input: {exc}", file=sys.stderr)
        return 2
    except DamagedExcelsiorError as exc:
        print(f"excelsior.py: damaged Excelsior input: {exc}", file=sys.stderr)
        return 3
    except (OSError, OverflowError) as exc:
        print(f"excelsior.py: {exc}", file=sys.stderr)
        return 1

    regular_count = sum(not item.endswith("/") for item in extracted)
    directory_count = len(extracted) - regular_count
    print(f"extracted {regular_count} file(s) and {directory_count} directorie(s) to {args.outputDir}")
    for warning in container.warnings:
        print(f"warning: {warning}", file=sys.stderr)
    if skipped:
        print(f"warning: {len(skipped)} file(s) were unavailable because the primary stream is damaged", file=sys.stderr)
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

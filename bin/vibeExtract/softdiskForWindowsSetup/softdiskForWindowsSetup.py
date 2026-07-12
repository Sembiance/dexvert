#!/usr/bin/env python3
# Vibe coded by Codex
"""Strict extractor for supported 16-bit Softdisk/Wise setup containers."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import struct
import sys
import tempfile
import zlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


MAX_U32 = 0xFFFFFFFF
CONTINUATION_SUFFIX = ".W02"


class FormatError(Exception):
    """Raised when an input is not exactly a supported setup container."""


@dataclass(frozen=True)
class LoaderVariant:
    name: str
    loader_sha256: str
    script_dialect: str
    archive_header_size: int
    crc_present: bool


LOADER_VARIANTS = {
    variant.loader_sha256: variant
    for variant in (
        LoaderVariant(
            "Wise 3.x legacy",
            "3639abb3bcf2196aa4cf89f833353f4b1ceb05bd7574a8afad3cf884cd406008",
            "legacy",
            4,
            False,
        ),
        LoaderVariant(
            "Wise 3.x CRC",
            "fe4249ceba2bd1fb2352d128f9e5888fc26c7646434b5cd0410cee941ce48775",
            "crc-v1",
            0x1E,
            True,
        ),
        LoaderVariant(
            "Wise 3.x extended",
            "0da10577a6927a5eb25ef2695be00c93d224082a71c90612e7df5ec0eae82ea7",
            "crc-v2",
            0x1E,
            True,
        ),
        LoaderVariant(
            "Wise 4.x extended",
            "3e956ba9cbe66a0006d8da2d8e653f1f3c246bd93244f3c82e5ddbe65785d759",
            "crc-v3",
            0x22,
            True,
        ),
    )
}


@dataclass(frozen=True)
class NEResource:
    type_value: int
    id_value: int
    offset: int
    length: int
    flags: int


@dataclass
class PayloadResource:
    kind: str
    script_offset: int
    start: int
    end: int
    inflated_size: int | None
    destination: str | None = None
    description: list[str] = field(default_factory=list)
    supplemental_description: list[str] = field(default_factory=list)
    flags: int | None = None
    record_control: int | None = None
    dos_date: int | None = None
    dos_time: int | None = None
    control: tuple[int, ...] | None = None
    crc32: int | None = None
    data: bytes = b""


@dataclass(frozen=True)
class InputVolume:
    path: Path
    size: int
    sha256: str


@dataclass
class ParsedInstaller:
    source_size: int
    source_sha256: str
    volumes: list[InputVolume]
    ne_offset: int
    overlay_offset: int
    loader_variant: LoaderVariant
    archive_header: bytes
    archive_fields: dict[str, Any]
    script_stored_size: int
    script_deflate_size: int
    script_crc32: int | None
    script_data: bytes
    script_header: dict[str, Any]
    operations: list[dict[str, Any]]
    runtime_offset: int | None
    runtime_stored_size: int
    runtime_crc32: int | None
    runtime_data: bytes | None
    payload_base: int
    payload_resources: list[PayloadResource]
    ne_resources: list[NEResource]
    source_data: bytes


class Reader:
    def __init__(self, data: bytes, label: str) -> None:
        self.data = data
        self.label = label
        self.pos = 0

    def require(self, count: int) -> None:
        if count < 0 or self.pos + count > len(self.data):
            raise FormatError(f"truncated {self.label} at 0x{self.pos:X}")

    def read(self, count: int) -> bytes:
        self.require(count)
        value = self.data[self.pos : self.pos + count]
        self.pos += count
        return value

    def u8(self) -> int:
        return self.read(1)[0]

    def u16(self) -> int:
        return struct.unpack("<H", self.read(2))[0]

    def u32(self) -> int:
        return struct.unpack("<I", self.read(4))[0]

    def cstring(self) -> str:
        end = self.data.find(b"\0", self.pos)
        if end < 0:
            raise FormatError(f"unterminated string in {self.label} at 0x{self.pos:X}")
        raw = self.data[self.pos:end]
        self.pos = end + 1
        try:
            return raw.decode("cp1252", errors="strict")
        except UnicodeDecodeError as exc:
            raise FormatError(f"invalid CP1252 string in {self.label}") from exc


def u16_at(data: bytes, offset: int) -> int:
    if offset < 0 or offset + 2 > len(data):
        raise FormatError(f"16-bit field outside file at 0x{offset:X}")
    return struct.unpack_from("<H", data, offset)[0]


def u32_at(data: bytes, offset: int) -> int:
    if offset < 0 or offset + 4 > len(data):
        raise FormatError(f"32-bit field outside file at 0x{offset:X}")
    return struct.unpack_from("<I", data, offset)[0]


def inflate_exact(raw: bytes, label: str) -> bytes:
    try:
        inflater = zlib.decompressobj(wbits=-15)
        output = inflater.decompress(raw)
        output += inflater.flush()
    except zlib.error as exc:
        raise FormatError(f"invalid raw-DEFLATE data in {label}: {exc}") from exc
    if not inflater.eof:
        raise FormatError(f"unterminated raw-DEFLATE stream in {label}")
    if inflater.unused_data or inflater.unconsumed_tail:
        raise FormatError(f"raw-DEFLATE stream in {label} does not consume its declared range")
    return output


def inflate_crc_member(raw: bytes, label: str) -> tuple[bytes, int]:
    if len(raw) <= 4:
        raise FormatError(f"CRC-bearing member in {label} is too short")
    output = inflate_exact(raw[:-4], label)
    stored_crc = u32_at(raw, len(raw) - 4)
    actual_crc = zlib.crc32(output) & MAX_U32
    if stored_crc != actual_crc:
        raise FormatError(
            f"CRC32 mismatch in {label}: stored 0x{stored_crc:08X}, actual 0x{actual_crc:08X}"
        )
    return output, stored_crc


def parse_ne(data: bytes) -> tuple[int, int, list[NEResource]]:
    if len(data) < 0x40 or data[:2] != b"MZ":
        raise FormatError("missing MS-DOS MZ header")
    ne_offset = u32_at(data, 0x3C)
    if ne_offset < 0x40 or ne_offset + 0x40 > len(data):
        raise FormatError("invalid NE header offset")
    if data[ne_offset : ne_offset + 2] != b"NE":
        raise FormatError("missing Windows New Executable header")

    segment_count = u16_at(data, ne_offset + 0x1C)
    segment_table_rel = u16_at(data, ne_offset + 0x22)
    resource_table_rel = u16_at(data, ne_offset + 0x24)
    resident_table_rel = u16_at(data, ne_offset + 0x26)
    alignment_shift = u16_at(data, ne_offset + 0x32)
    target_os = data[ne_offset + 0x36]
    if not segment_count or segment_count > 0x1000 or alignment_shift > 31:
        raise FormatError("invalid NE segment declarations")
    if target_os != 2:
        raise FormatError("NE target is not Microsoft Windows")

    segment_table = ne_offset + segment_table_rel
    resource_table = ne_offset + resource_table_rel
    resident_table = ne_offset + resident_table_rel
    if not (ne_offset + 0x40 <= segment_table <= resource_table < resident_table <= len(data)):
        raise FormatError("invalid NE table ordering")

    image_end = 0
    if segment_table + segment_count * 8 > len(data):
        raise FormatError("truncated NE segment table")
    for index in range(segment_count):
        entry = segment_table + index * 8
        sector = u16_at(data, entry)
        stored_length = u16_at(data, entry + 2)
        if sector == 0:
            raise FormatError("unallocated NE segment is unsupported")
        length = stored_length or 0x10000
        start = sector << alignment_shift
        end = start + length
        if start >= len(data) or end > len(data):
            raise FormatError("NE segment exceeds physical file")
        image_end = max(image_end, end)

    r = Reader(data[resource_table:resident_table], "NE resource table")
    resource_shift = r.u16()
    if resource_shift > 31:
        raise FormatError("invalid NE resource alignment")
    resources: list[NEResource] = []
    while True:
        type_value = r.u16()
        if type_value == 0:
            break
        count = r.u16()
        reserved = r.u32()
        if count == 0 or reserved != 0:
            raise FormatError("invalid NE resource type record")
        for _ in range(count):
            offset_units = r.u16()
            length_units = r.u16()
            flags = r.u16()
            id_value = r.u16()
            handle = r.u16()
            usage = r.u16()
            if not offset_units or not length_units or handle != 0 or usage != 0:
                raise FormatError("invalid NE resource record")
            offset = offset_units << resource_shift
            length = length_units << resource_shift
            if offset + length > len(data):
                raise FormatError("NE resource exceeds physical file")
            resources.append(NEResource(type_value, id_value, offset, length, flags))
            image_end = max(image_end, offset + length)

    if r.pos > resident_table - resource_table:
        raise FormatError("NE resource table overlaps resident-name table")
    if image_end <= ne_offset or image_end >= len(data):
        raise FormatError("NE image has no appended setup data")
    if image_end & 0x0F:
        raise FormatError("setup data is not on the required 16-byte boundary")

    resident = Reader(data[resident_table:], "NE resident-name table")
    module_name_length = resident.u8()
    if resident.read(module_name_length) != b"INSTALL":
        raise FormatError("NE module is not the supported INSTALL loader")
    return ne_offset, image_end, resources


def parse_script_header(r: Reader, dialect: str) -> dict[str, Any]:
    control_prefix = r.read(5)
    layout_value = r.u32()
    media_capacity = r.u32()
    font_name: str | None = None
    font_size: int | None = None
    language_names: list[str] = []

    if control_prefix[1] != 0 or control_prefix[4] != 0:
        raise FormatError("invalid Wise script control prefix")

    if dialect == "legacy":
        if control_prefix[0] not in (0x08, 0x48):
            raise FormatError("unsupported legacy Wise script control value")
        if r.read(4) != b"\0" * 4 or r.u8() != 0:
            raise FormatError("invalid legacy Wise script reserved fields")
        language_count = r.u8()
        ui_count = 31
        layout_name = "expanded_layout_size"
    elif dialect == "crc-v1":
        if control_prefix[0] not in (0x08, 0x18) or r.read(7) != b"\0" * 7:
            raise FormatError("invalid CRC-v1 Wise script header")
        language_count = r.u8()
        if r.u8() != 0:
            raise FormatError("invalid CRC-v1 language-table terminator")
        ui_count = 38
        layout_name = "resource_data_size"
    elif dialect in ("crc-v2", "crc-v3"):
        allowed = (0x15, 0x18) if dialect == "crc-v2" else (0x15,)
        if control_prefix[0] not in allowed or r.read(7) != b"\0" * 7:
            raise FormatError(f"invalid {dialect} Wise script header")
        font_name = r.cstring()
        font_size = r.u16()
        if not font_name or font_size == 0:
            raise FormatError("invalid Wise script UI font declaration")
        if dialect == "crc-v3" and r.read(4) != b"\0" * 4:
            raise FormatError("invalid CRC-v3 reserved fields")
        language_count = r.u8()
        language_names = [r.cstring() for _ in range(language_count)]
        ui_count = 42 if dialect == "crc-v2" else 44
        layout_name = "resource_data_size"
    else:
        raise FormatError("internal error: unknown script dialect")

    if language_count != 1:
        raise FormatError("supported Softdisk scripts require exactly one language")
    ui_strings = [r.cstring() for _ in range(ui_count)]
    if not ui_strings[0] or not ui_strings[-1]:
        raise FormatError("invalid Wise script UI string table")
    return {
        "dialect": dialect,
        "control_prefix_hex": control_prefix.hex(),
        layout_name: layout_value,
        "media_capacity": media_capacity,
        "font_name": font_name,
        "font_size": font_size,
        "language_count": language_count,
        "language_names": language_names,
        "ui_string_count": ui_count,
        "ui_strings": ui_strings,
        "operation_stream_offset": r.pos,
    }


def parse_script(
    script: bytes, dialect: str
) -> tuple[dict[str, Any], list[dict[str, Any]], list[PayloadResource]]:
    r = Reader(script, "Wise script")
    if len(script) < 19:
        raise FormatError("Wise script is too short")
    header = parse_script_header(r, dialect)
    language_count = header["language_count"]
    operations: list[dict[str, Any]] = []
    payloads: list[PayloadResource] = []
    graphic_index = 0

    while r.pos < len(script):
        operation_offset = r.pos
        opcode = r.u8()
        op: dict[str, Any] = {"offset": operation_offset, "opcode": opcode}

        if opcode == 0x00:
            flags = r.u8()
            record_control = r.u8() if dialect in ("crc-v2", "crc-v3") else None
            start = r.u32()
            end = r.u32()
            dos_date = r.u16()
            dos_time = r.u16()
            inflated_size = r.u32()
            destination = r.cstring()
            descriptions = [r.cstring() for _ in range(language_count)]
            supplemental = (
                [r.cstring() for _ in range(language_count)] if dialect == "crc-v3" else []
            )
            if not destination:
                raise FormatError(f"empty install-file path at script offset 0x{operation_offset:X}")
            payloads.append(PayloadResource(
                "file", operation_offset, start, end, inflated_size, destination,
                descriptions, supplemental, flags, record_control, dos_date, dos_time,
            ))
            op.update(
                flags=flags, record_control=record_control, deflate_start=start,
                deflate_end=end, dos_date=dos_date, dos_time=dos_time,
                inflated_size=inflated_size, destination=destination,
                descriptions=descriptions, supplemental_descriptions=supplemental,
            )
        elif opcode == 0x03:
            op.update(flags=r.u8(), strings=[r.cstring() for _ in range(language_count * 2)])
        elif opcode == 0x04:
            op.update(number=r.u8(), strings=[r.cstring() for _ in range(language_count)])
        elif opcode == 0x05:
            op.update(path=r.cstring(), section=r.cstring(), values=r.cstring())
        elif opcode == 0x06:
            graphic_index += 1
            control = r.u8()
            extended_control = r.u8() if dialect in ("crc-v2", "crc-v3") else None
            value_1 = r.u16()
            value_2 = r.u16()
            start = r.u32()
            end = r.u32()
            inflated_size = None if dialect == "legacy" else r.u32()
            control_values = tuple(
                value for value in (control, extended_control, value_1, value_2)
                if value is not None
            )
            payloads.append(PayloadResource(
                "graphic", operation_offset, start, end, inflated_size,
                destination=f"_setup/graphic_{graphic_index:03d}.bin",
                control=control_values,
            ))
            op.update(
                control=control, extended_control=extended_control, value_1=value_1,
                value_2=value_2, deflate_start=start, deflate_end=end,
                inflated_size=inflated_size,
            )
        elif opcode == 0x07:
            op.update(flags=r.u8(), pathname=r.cstring(), command_line=r.cstring())
            if dialect != "legacy":
                op["working_directory"] = r.cstring()
        elif opcode == 0x08:
            if dialect != "legacy":
                op["control"] = r.u8()
        elif opcode == 0x09:
            op.update(
                flags=r.u8(), library=r.cstring(), function=r.cstring(),
                arguments=[r.cstring() for _ in range(language_count)],
            )
        elif opcode == 0x0B:
            op.update(flags=r.u8(), pathname=r.cstring())
        elif opcode == 0x0C:
            op.update(operator=r.u8(), variable=r.cstring(), value=r.cstring())
        elif opcode in (0x0D, 0x0F, 0x10):
            pass
        elif opcode == 0x11 and dialect != "legacy":
            op.update(pathname=r.cstring())
        elif opcode == 0x14 and dialect != "legacy":
            graphic_index += 1
            control = r.u8()
            start = r.u32()
            end = r.u32()
            inflated_size = r.u32()
            payloads.append(PayloadResource(
                "graphic", operation_offset, start, end, inflated_size,
                destination=f"_setup/graphic_{graphic_index:03d}.bin",
                control=(control,),
            ))
            op.update(
                control=control, deflate_start=start, deflate_end=end,
                inflated_size=inflated_size,
            )
        else:
            raise FormatError(
                f"unsupported Wise script opcode 0x{opcode:02X} at 0x{operation_offset:X}"
            )
        operations.append(op)

    if r.pos != len(script):
        raise FormatError("Wise script operation stream has trailing bytes")
    return header, operations, payloads


def validate_dos_datetime(date_value: int, time_value: int) -> dt.datetime:
    year = 1980 + ((date_value >> 9) & 0x7F)
    month = (date_value >> 5) & 0x0F
    day = date_value & 0x1F
    hour = (time_value >> 11) & 0x1F
    minute = (time_value >> 5) & 0x3F
    second = (time_value & 0x1F) * 2
    try:
        return dt.datetime(year, month, day, hour, minute, second)
    except ValueError as exc:
        raise FormatError("invalid MS-DOS date/time in install-file record") from exc


def find_continuation(input_path: Path) -> Path:
    wanted = f"{input_path.stem}{CONTINUATION_SUFFIX}".casefold()
    try:
        matches = [entry for entry in input_path.parent.iterdir() if entry.name.casefold() == wanted]
    except OSError as exc:
        raise FormatError(f"cannot inspect input directory for continuation volume: {exc}") from exc
    if len(matches) != 1 or not matches[0].is_file():
        raise FormatError(
            f"required continuation volume {input_path.stem}{CONTINUATION_SUFFIX} "
            "was not found beside the input executable"
        )
    return matches[0]


def read_and_parse(input_path: Path) -> ParsedInstaller:
    executable_data = input_path.read_bytes()
    ne_offset, overlay_offset, ne_resources = parse_ne(executable_data)
    loader_hash = hashlib.sha256(executable_data[:overlay_offset]).hexdigest()
    variant = LOADER_VARIANTS.get(loader_hash)
    if variant is None:
        raise FormatError("NE loader generation is not a supported Softdisk setup dialect")

    archive_end = overlay_offset + variant.archive_header_size
    if archive_end > len(executable_data):
        raise FormatError("truncated Wise archive header")
    archive_header = executable_data[overlay_offset:archive_end]
    archive_fields: dict[str, Any] = {
        "header_size": variant.archive_header_size,
        "header_hex": archive_header.hex(),
    }

    if not variant.crc_present:
        script_deflate_size = u32_at(archive_header, 0)
        if script_deflate_size == 0:
            raise FormatError("zero-length compressed Wise script")
        script_stored_size = script_deflate_size
        script_start = archive_end
        script_end = script_start + script_stored_size
        if script_end > len(executable_data):
            raise FormatError("compressed Wise script is not contained on the first volume")
        script_data = inflate_exact(executable_data[script_start:script_end], "Wise script")
        script_crc = None
        runtime_offset = None
        runtime_stored_size = 0
        runtime_crc = None
        runtime_data = None
        payload_base = script_end
        archive_fields["script_deflate_size"] = script_deflate_size
    else:
        if variant.archive_header_size not in (0x1E, 0x22):
            raise FormatError("invalid CRC archive-header size")
        script_inflated_size = u32_at(archive_header, 14)
        script_stored_size = u32_at(archive_header, 18)
        runtime_stored_size = u32_at(archive_header, 22)
        if script_stored_size <= 4 or runtime_stored_size <= 4:
            raise FormatError("invalid CRC archive member sizes")
        script_deflate_size = script_stored_size - 4
        script_start = archive_end
        script_end = script_start + script_stored_size
        runtime_offset = script_end
        runtime_end = runtime_offset + runtime_stored_size
        if runtime_end > len(executable_data):
            raise FormatError("script or Wise runtime is not contained on the first volume")
        script_data, script_crc = inflate_crc_member(
            executable_data[script_start:script_end], "Wise script"
        )
        if len(script_data) != script_inflated_size:
            raise FormatError("inflated Wise script size does not match archive header")
        runtime_data, runtime_crc = inflate_crc_member(
            executable_data[runtime_offset:runtime_end], "embedded Wise runtime"
        )
        if len(runtime_data) < 0x40 or runtime_data[:2] != b"MZ":
            raise FormatError("embedded Wise runtime is not an MZ executable")
        payload_base = runtime_end
        archive_fields.update({
            "loader_configuration_hex": archive_header[:14].hex(),
            "script_inflated_size": script_inflated_size,
            "script_stored_size": script_stored_size,
            "runtime_stored_size": runtime_stored_size,
            "trailing_configuration_hex": archive_header[26:].hex(),
        })

    script_header, operations, payloads = parse_script(script_data, variant.script_dialect)
    if not payloads:
        raise FormatError("Wise script declares no compressed resources")
    media_capacity = script_header["media_capacity"]
    if media_capacity == 0 or media_capacity & 0xFFF:
        raise FormatError("invalid setup-media capacity")

    ordered = sorted(payloads, key=lambda item: (item.start, item.end))
    cursor = 0
    seen_ranges: set[tuple[int, int]] = set()
    for item in ordered:
        if not (0 <= item.start < item.end <= MAX_U32):
            raise FormatError(f"invalid payload range in script record 0x{item.script_offset:X}")
        if item.start != cursor:
            raise FormatError(f"payload coverage gap or overlap at relative offset 0x{cursor:X}")
        if (item.start, item.end) in seen_ranges:
            raise FormatError("duplicate payload range")
        seen_ranges.add((item.start, item.end))
        cursor = item.end

    if variant.crc_present:
        if script_header["resource_data_size"] != cursor:
            raise FormatError("script resource-data size does not match its declared ranges")
        expected_size = payload_base + cursor
    else:
        expected_size = payload_base + cursor
        expanded_size = expected_size - variant.archive_header_size - script_stored_size + len(script_data)
        if script_header["expanded_layout_size"] != expanded_size:
            raise FormatError("expanded-layout size does not match the archive and script sizes")

    volumes = [InputVolume(
        input_path, len(executable_data), hashlib.sha256(executable_data).hexdigest()
    )]
    source_data = executable_data
    if expected_size > len(executable_data):
        if len(executable_data) != media_capacity:
            raise FormatError("first-volume size does not match the script media capacity")
        continuation_path = find_continuation(input_path)
        continuation_data = continuation_path.read_bytes()
        volumes.append(InputVolume(
            continuation_path,
            len(continuation_data),
            hashlib.sha256(continuation_data).hexdigest(),
        ))
        source_data += continuation_data
    if len(source_data) != expected_size:
        relation = "truncated" if len(source_data) < expected_size else "has trailing bytes"
        raise FormatError(
            f"logical archive {relation}: expected {expected_size} bytes, got {len(source_data)}"
        )

    for index, item in enumerate(ordered, 1):
        raw = source_data[payload_base + item.start : payload_base + item.end]
        if variant.crc_present:
            item.data, item.crc32 = inflate_crc_member(raw, f"payload resource {index}")
        else:
            item.data = inflate_exact(raw, f"payload resource {index}")
        if item.inflated_size is not None and len(item.data) != item.inflated_size:
            raise FormatError(f"inflated-size mismatch in script record 0x{item.script_offset:X}")
        if item.dos_date is not None and item.dos_time is not None:
            validate_dos_datetime(item.dos_date, item.dos_time)

    return ParsedInstaller(
        len(source_data), hashlib.sha256(source_data).hexdigest(), volumes,
        ne_offset, overlay_offset, variant, archive_header, archive_fields,
        script_stored_size, script_deflate_size, script_crc, script_data,
        script_header, operations, runtime_offset, runtime_stored_size,
        runtime_crc, runtime_data, payload_base, ordered, ne_resources, source_data,
    )


_WINDOWS_FORBIDDEN = re.compile(r'[<>:"|?*]')


def safe_output_path(pathname: str) -> Path:
    normalized = pathname.replace("\\", "/")
    parts: list[str] = []
    for raw_part in normalized.split("/"):
        if raw_part in ("", "."):
            continue
        if raw_part == "..":
            raise FormatError("parent-directory component in destination path")
        part = _WINDOWS_FORBIDDEN.sub("_", raw_part).rstrip(" .")
        if not part:
            raise FormatError("empty destination path component")
        parts.append(part)
    if not parts:
        raise FormatError("empty destination path")
    return Path(*parts)


def resource_label(value: int) -> str:
    if value & 0x8000:
        return f"{value & 0x7FFF:04X}"
    return f"nameoff_{value:04X}"


def build_outputs(
    parsed: ParsedInstaller, include_all: bool
) -> list[tuple[Path, bytes, float | None, dict[str, Any]]]:
    outputs: list[tuple[Path, bytes, float | None, dict[str, Any]]] = []
    if include_all:
        outputs.append((
            Path("_setup/WiseScript.bin"), parsed.script_data, None, {"kind": "script"}
        ))
        outputs.append((
            Path("_setup/ArchiveHeader.bin"), parsed.archive_header, None,
            {"kind": "archive_header"},
        ))
        if parsed.runtime_data is not None:
            outputs.append((
                Path("_setup/WiseRuntime.bin"), parsed.runtime_data, None,
                {"kind": "wise_runtime", "crc32": parsed.runtime_crc32},
            ))

    for item in parsed.payload_resources:
        if item.kind != "file" and not include_all:
            continue
        assert item.destination is not None
        output_path = safe_output_path(item.destination)
        timestamp: float | None = None
        if item.dos_date is not None and item.dos_time is not None:
            timestamp = validate_dos_datetime(item.dos_date, item.dos_time).timestamp()
        outputs.append((output_path, item.data, timestamp, {
            "kind": item.kind,
            "script_offset": item.script_offset,
            "deflate_start": item.start,
            "deflate_end": item.end,
            "stored_size": item.end - item.start,
            "deflate_size": item.end - item.start - (4 if item.crc32 is not None else 0),
            "inflated_size": len(item.data),
            "crc32": item.crc32,
            "destination": item.destination,
            "description": item.description,
            "supplemental_description": item.supplemental_description,
            "flags": item.flags,
            "record_control": item.record_control,
            "dos_date": item.dos_date,
            "dos_time": item.dos_time,
            "control": item.control,
        }))

    if include_all:
        for resource in parsed.ne_resources:
            path = Path(
                "_setup/ne_resources/"
                f"type_{resource_label(resource.type_value)}_id_{resource_label(resource.id_value)}.bin"
            )
            raw = parsed.source_data[resource.offset : resource.offset + resource.length]
            outputs.append((path, raw, None, {
                "kind": "ne_resource", "type": resource.type_value,
                "id": resource.id_value, "offset": resource.offset,
                "length": resource.length, "flags": resource.flags,
            }))

    # Conditional branches can contain the same destination more than once.
    # Preserve every declared resource with a deterministic disambiguator.
    folded: set[str] = set()
    disambiguated: list[tuple[Path, bytes, float | None, dict[str, Any]]] = []
    for path, content, timestamp, details in outputs:
        original = path
        serial = 1
        while path.as_posix().casefold() in folded:
            serial += 1
            path = original.with_name(
                f"{original.stem}.duplicate_{serial:03d}{original.suffix}"
            )
        if path != original:
            details = {"original_output": original.as_posix(), **details}
        folded.add(path.as_posix().casefold())
        disambiguated.append((path, content, timestamp, details))

    # A Wise destination can denote a directory while still carrying a file
    # member.  If another output needs that same pathname as a directory,
    # retain the member under a visible, deterministic ".resource" suffix.
    all_parts = [tuple(part.casefold() for part in item[0].parts) for item in disambiguated]
    final: list[tuple[Path, bytes, float | None, dict[str, Any]]] = []
    final_keys: set[str] = set()
    for index, (path, content, timestamp, details) in enumerate(disambiguated):
        parts = all_parts[index]
        if any(len(other) > len(parts) and other[: len(parts)] == parts for other in all_parts):
            original = path
            path = path.with_name(f"{path.name}.resource")
            serial = 1
            while path.as_posix().casefold() in final_keys:
                serial += 1
                path = original.with_name(f"{original.name}.resource_{serial:03d}")
            details = {"original_output": original.as_posix(), **details}
        final_keys.add(path.as_posix().casefold())
        final.append((path, content, timestamp, details))
    return final


def extract(parsed: ParsedInstaller, output_dir: Path, include_all: bool) -> dict[str, Any]:
    outputs = build_outputs(parsed, include_all)
    if output_dir.exists() and not output_dir.is_dir():
        raise FormatError("output path exists and is not a directory")
    if output_dir.is_symlink():
        raise FormatError("output directory may not be a symbolic link")

    # Check the entire merge against a pre-existing tree before creating a
    # temporary directory or replacing a single destination.
    for relative, _, _, _ in outputs:
        current = output_dir
        for part in relative.parts[:-1]:
            current /= part
            if current.is_symlink():
                raise FormatError(f"symbolic-link directory blocks output path: {current}")
            if current.exists() and not current.is_dir():
                raise FormatError(f"file blocks required output directory: {current}")
        destination = output_dir / relative
        if destination.is_symlink():
            raise FormatError(f"symbolic link blocks output file: {destination}")
        if destination.exists() and destination.is_dir():
            raise FormatError(f"directory blocks required output file: {destination}")

    parent = output_dir.parent.resolve()
    parent.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.tmp-", dir=parent))
    try:
        manifest_files: list[dict[str, Any]] = []
        for relative, content, timestamp, details in outputs:
            destination = temp_dir / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content)
            os.chmod(destination, 0o664)
            if timestamp is not None:
                os.utime(destination, (timestamp, timestamp))
            manifest_files.append({
                "output": relative.as_posix(), "size": len(content),
                "sha256": hashlib.sha256(content).hexdigest(), **details,
            })

        manifest = {
            "format": "Softdisk for Windows Setup / Wise 16-bit script dialects",
            "loader_variant": parsed.loader_variant.name,
            "script_dialect": parsed.loader_variant.script_dialect,
            "logical_input_size": parsed.source_size,
            "logical_input_sha256": parsed.source_sha256,
            "volumes": [
                {"path": str(volume.path), "size": volume.size, "sha256": volume.sha256}
                for volume in parsed.volumes
            ],
            "ne_header_offset": parsed.ne_offset,
            "overlay_offset": parsed.overlay_offset,
            "loader_sha256": parsed.loader_variant.loader_sha256,
            "archive_fields": parsed.archive_fields,
            "script_stored_size": parsed.script_stored_size,
            "script_deflate_size": parsed.script_deflate_size,
            "script_crc32": parsed.script_crc32,
            "script_inflated_size": len(parsed.script_data),
            "runtime_offset": parsed.runtime_offset,
            "runtime_stored_size": parsed.runtime_stored_size,
            "runtime_crc32": parsed.runtime_crc32,
            "payload_data_offset": parsed.payload_base,
            "payload_resource_count": len(parsed.payload_resources),
            "install_file_count": sum(item.kind == "file" for item in parsed.payload_resources),
            "ne_resource_count": len(parsed.ne_resources),
            "extracted_file_count": len(outputs),
            "include_all": include_all,
            "byte_coverage": {
                "loader_and_ne_image": parsed.overlay_offset,
                "archive_header": len(parsed.archive_header),
                "compressed_script_member": parsed.script_stored_size,
                "compressed_runtime_member": parsed.runtime_stored_size,
                "compressed_payload_members": parsed.source_size - parsed.payload_base,
                "total": parsed.source_size,
            },
            "script_header": parsed.script_header,
            "operations": parsed.operations,
            "files": manifest_files,
        }
        if include_all:
            manifest_path = temp_dir / "_manifest.json"
            manifest_path.write_text(
                json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            os.chmod(manifest_path, 0o664)

        for directory, _, _ in os.walk(temp_dir):
            os.chmod(directory, 0o775)
        output_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(output_dir, 0o775)
        for source in sorted(temp_dir.rglob("*")):
            relative = source.relative_to(temp_dir)
            destination = output_dir / relative
            if source.is_dir():
                destination.mkdir(parents=True, exist_ok=True)
                os.chmod(destination, 0o775)
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                os.replace(source, destination)
        shutil.rmtree(temp_dir)
        return manifest
    except Exception:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract a Softdisk for Windows Setup executable without running it."
    )
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputDir", type=Path)
    parser.add_argument(
        "--all", action="store_true",
        help="also extract _setup resources and write _manifest.json",
    )
    args = parser.parse_args(argv)

    try:
        parsed = read_and_parse(args.inputFile)
        manifest = extract(parsed, args.outputDir, args.all)
    except (OSError, FormatError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    suffix = " including setup resources and manifest" if args.all else ""
    volume_text = f" from {len(parsed.volumes)} volume(s)"
    print(
        f"extracted {manifest['extracted_file_count']} files{suffix}{volume_text} to {args.outputDir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# Vibe coded by Codex
"""Strict, transactional extractor for the InstallUs self-extracting format."""

from __future__ import annotations

import hashlib
import json
import mmap
import os
import re
import shutil
import stat
import struct
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO


class FormatError(Exception):
    """The input is not a supported, structurally valid InstallUs installer."""


def fail(message: str) -> "None":
    raise FormatError(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def u16(data: mmap.mmap, offset: int) -> int:
    require(0 <= offset <= len(data) - 2, "truncated 16-bit field")
    return struct.unpack_from("<H", data, offset)[0]


def u32(data: mmap.mmap, offset: int) -> int:
    require(0 <= offset <= len(data) - 4, "truncated 32-bit field")
    return struct.unpack_from("<I", data, offset)[0]


def checked_slice(data: mmap.mmap, offset: int, size: int, what: str) -> bytes:
    require(offset >= 0 and size >= 0 and offset <= len(data) - size, f"truncated {what}")
    return data[offset : offset + size]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def make_user_group_readable(root: Path) -> None:
    """Ensure the published tree is readable/traversable by its user and group."""
    directory_bits = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP
    file_bits = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP
    for directory, _, file_names in os.walk(root):
        directory_path = Path(directory)
        os.chmod(directory_path, stat.S_IMODE(directory_path.stat().st_mode) | directory_bits)
        for name in file_names:
            path = directory_path / name
            os.chmod(path, stat.S_IMODE(path.stat().st_mode) | file_bits)


def files_equal(first: Path, second: Path) -> bool:
    """Compare regular files exactly without loading a large payload into memory."""
    if first.stat().st_size != second.stat().st_size:
        return False
    with first.open("rb") as first_stream, second.open("rb") as second_stream:
        while True:
            first_block = first_stream.read(1024 * 1024)
            second_block = second_stream.read(1024 * 1024)
            if first_block != second_block:
                return False
            if not first_block:
                return True


def merge_staged_output(stage: Path, output: Path) -> None:
    """Publish into an existing directory without overwriting user content."""
    directory_bits = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP
    directories = sorted(
        (path for path in stage.rglob("*") if path.is_dir()),
        key=lambda path: len(path.relative_to(stage).parts),
    )
    files = [path for path in stage.rglob("*") if path.is_file()]
    existing_directory_modes = {output: stat.S_IMODE(output.stat().st_mode)}

    for directory in directories:
        target = output / directory.relative_to(stage)
        if os.path.lexists(target):
            require(target.is_dir() and not target.is_symlink(), f"output collision at {target}")
            existing_directory_modes[target] = stat.S_IMODE(target.stat().st_mode)
    for source in files:
        target = output / source.relative_to(stage)
        if os.path.lexists(target):
            require(
                target.is_file() and not target.is_symlink() and files_equal(source, target),
                f"output file collision at {target}",
            )

    created_directories: list[Path] = []
    created_files: list[Path] = []
    try:
        for directory in directories:
            target = output / directory.relative_to(stage)
            if not target.exists():
                target.mkdir()
                created_directories.append(target)
        for source in files:
            target = output / source.relative_to(stage)
            if not os.path.lexists(target):
                os.rename(source, target)
                created_files.append(target)
        for directory in [output, *(output / path.relative_to(stage) for path in directories)]:
            os.chmod(directory, stat.S_IMODE(directory.stat().st_mode) | directory_bits)
    except BaseException:
        for path in reversed(created_files):
            try:
                path.unlink()
            except OSError:
                pass
        for path, mode in existing_directory_modes.items():
            try:
                os.chmod(path, mode)
            except OSError:
                pass
        for path in reversed(created_directories):
            try:
                path.rmdir()
            except OSError:
                pass
        raise


def json_name(raw: bytes) -> str:
    return raw.decode("cp1252", errors="replace")


def safe_component(raw: bytes) -> str:
    """Reversibly encode one archive-name component as portable ASCII."""
    require(raw not in (b"", b".", b".."), "empty or relative archive path component")
    safe = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 !#$&'()+,-.;=@[]^_`{}~"
    return "".join(chr(value) if value in safe and value != ord("%") else f"%{value:02X}" for value in raw)


def safe_archive_path(raw: bytes) -> Path:
    require(raw and b"\x00" not in raw, "empty or NUL-containing archive filename")
    require(not raw.startswith((b"/", b"\\")), "absolute archive filename")
    components: list[bytes] = []
    current = bytearray()
    for value in raw:
        if value in (ord("/"), ord("\\")):
            require(current, "empty archive path component")
            components.append(bytes(current))
            current.clear()
        else:
            current.append(value)
    require(current, "archive filename ends with a separator")
    components.append(bytes(current))
    require(all(component not in (b".", b"..") for component in components), "relative archive path")
    return Path(*(safe_component(component) for component in components))


def safe_destination_path(raw: bytes, filename: bytes) -> Path:
    """Map a variable-rooted InstallUs destination to a portable relative path."""
    require(raw.startswith(b"%"), "installation destination is not variable-rooted")
    variable_end = raw.find(b"%", 1)
    require(variable_end > 1, "malformed installation destination variable")
    variable = raw[1:variable_end]
    remainder = raw[variable_end + 1 :]
    require(not remainder or remainder[0] in (ord("/"), ord("\\")), "destination variable has a suffix")
    require(not remainder or remainder[-1] in (ord("/"), ord("\\")), "destination is not a directory")

    components = [safe_component(variable)]
    interior = remainder[1:-1].replace(b"\\", b"/") if remainder else b""
    if interior:
        raw_components = interior.split(b"/")
        require(all(raw_components), "empty installation destination component")
        for component in raw_components:
            require(component not in (b".", b".."), "relative destination path")
            components.append(safe_component(component))
    return Path(*components) / safe_archive_path(filename)


def parse_setup_ini(raw: bytes) -> dict[bytes, dict[bytes, bytes]]:
    """Parse the byte-oriented subset of setup.inf used for payload placement."""
    sections: dict[bytes, dict[bytes, bytes]] = {}
    current: dict[bytes, bytes] | None = None
    for line_number, source_line in enumerate(raw.splitlines(), 1):
        line = source_line.strip()
        if not line or line.startswith((b";", b"#")):
            continue
        if line.startswith(b"[") and line.endswith(b"]"):
            name = line[1:-1].strip().lower()
            require(name and name not in sections, f"duplicate/empty setup.inf section at line {line_number}")
            current = {}
            sections[name] = current
            continue
        require(current is not None and b"=" in line, f"malformed setup.inf line {line_number}")
        key, value = line.split(b"=", 1)
        key = key.strip().lower()
        require(key and key not in current, f"duplicate/empty setup.inf key at line {line_number}")
        current[key] = value.strip()
    return sections


def parse_decimal(raw: bytes, what: str) -> int:
    require(raw and all(0x30 <= value <= 0x39 for value in raw), f"invalid {what}")
    require(len(raw) == 1 or raw[0] != 0x30, f"noncanonical {what}")
    return int(raw)


@dataclass(frozen=True)
class Section:
    index: int
    name: str
    virtual_size: int
    virtual_address: int
    raw_size: int
    raw_offset: int
    characteristics: int


@dataclass(frozen=True)
class Resource:
    type_value: int | str
    name_value: int | str
    language_value: int | str
    data_offset: int
    size: int
    code_page: int


@dataclass(frozen=True)
class PEInfo:
    pe_offset: int
    timestamp: int
    image_base: int
    entry_rva: int
    section_alignment: int
    file_alignment: int
    size_of_image: int
    size_of_headers: int
    resource_rva: int
    resource_size: int
    stub_end: int
    sections: tuple[Section, ...]
    resources: tuple[Resource, ...]


RESOURCE_TYPES = {
    1: "cursor",
    2: "bitmap",
    3: "icon",
    4: "menu",
    5: "dialog",
    6: "string",
    7: "fontdir",
    8: "font",
    9: "accelerator",
    10: "rcdata",
    11: "messagetable",
    12: "group_cursor",
    14: "group_icon",
    16: "version",
    17: "dlginclude",
    19: "plugplay",
    20: "vxd",
    21: "anicursor",
    22: "aniicon",
    23: "html",
    24: "manifest",
}


def parse_pe(data: mmap.mmap) -> PEInfo:
    require(len(data) >= 0x40 and data[:2] == b"MZ", "missing DOS MZ header")
    pe_offset = u32(data, 0x3C)
    require(pe_offset >= 0x40 and pe_offset <= len(data) - 24, "invalid PE header offset")
    require(data[pe_offset : pe_offset + 4] == b"PE\x00\x00", "missing PE signature")
    machine, section_count, timestamp, _, _, optional_size, characteristics = struct.unpack_from(
        "<HHIIIHH", data, pe_offset + 4
    )
    require(machine == 0x14C, "InstallUs stub is not 32-bit x86")
    require(1 <= section_count <= 96, "invalid PE section count")
    require(characteristics & 0x0002, "PE image is not executable")
    optional = pe_offset + 24
    require(optional_size >= 224 and optional <= len(data) - optional_size, "truncated PE32 optional header")
    require(u16(data, optional) == 0x10B, "PE optional header is not PE32")
    entry_rva = u32(data, optional + 16)
    image_base = u32(data, optional + 28)
    section_alignment = u32(data, optional + 32)
    file_alignment = u32(data, optional + 36)
    size_of_image = u32(data, optional + 56)
    size_of_headers = u32(data, optional + 60)
    directory_count = u32(data, optional + 92)
    require(directory_count >= 16 and optional_size >= 224, "incomplete PE data-directory table")
    resource_rva, resource_size = struct.unpack_from("<II", data, optional + 112)
    certificate_offset, certificate_size = struct.unpack_from("<II", data, optional + 128)
    require(certificate_offset == 0 and certificate_size == 0, "signed/extended PE layout is unsupported")
    require(
        section_alignment and section_alignment & (section_alignment - 1) == 0,
        "invalid PE section alignment",
    )
    require(file_alignment and file_alignment & (file_alignment - 1) == 0, "invalid PE file alignment")
    require(size_of_headers <= len(data), "PE headers extend beyond EOF")

    section_table = optional + optional_size
    require(section_table <= len(data) - section_count * 40, "truncated PE section table")
    sections: list[Section] = []
    raw_ranges: list[tuple[int, int]] = []
    for index in range(section_count):
        offset = section_table + index * 40
        raw_name = data[offset : offset + 8].split(b"\x00", 1)[0]
        try:
            name = raw_name.decode("ascii")
        except UnicodeDecodeError:
            fail("non-ASCII PE section name")
        virtual_size, virtual_address, raw_size, raw_offset = struct.unpack_from("<IIII", data, offset + 8)
        characteristics_value = u32(data, offset + 36)
        if raw_size:
            require(raw_offset >= size_of_headers, "PE section overlaps headers")
            require(raw_offset % file_alignment == 0, "misaligned PE section")
            require(raw_offset <= len(data) - raw_size, "PE section extends beyond EOF")
            raw_ranges.append((raw_offset, raw_offset + raw_size))
        require(virtual_address % section_alignment == 0, "misaligned PE virtual section")
        sections.append(
            Section(index, name, virtual_size, virtual_address, raw_size, raw_offset, characteristics_value)
        )
    for (_, previous_end), (next_start, _) in zip(sorted(raw_ranges), sorted(raw_ranges)[1:]):
        require(previous_end <= next_start, "overlapping PE sections")
    require(raw_ranges, "PE image has no file-backed sections")
    stub_end = max(end for _, end in raw_ranges)
    require(stub_end < len(data), "PE image has no InstallUs overlay")
    require(any(s.virtual_address <= entry_rva < s.virtual_address + max(s.virtual_size, s.raw_size) for s in sections),
            "PE entry point is outside all sections")

    def rva_to_file(rva: int, size: int, what: str) -> int:
        require(size >= 0, f"negative {what} size")
        for section in sections:
            if section.virtual_address <= rva and rva - section.virtual_address <= section.raw_size:
                relative = rva - section.virtual_address
                require(relative <= section.raw_size - size, f"{what} exceeds its PE section")
                result = section.raw_offset + relative
                require(result <= stub_end - size, f"{what} exceeds the PE stub")
                return result
        fail(f"unmapped RVA for {what}")

    resources: list[Resource] = []
    if resource_rva or resource_size:
        require(resource_rva and resource_size, "partial PE resource directory")
        resource_base = rva_to_file(resource_rva, resource_size, "resource directory")
        resource_limit = resource_base + resource_size
        active_directories: set[int] = set()
        visited_directories: set[int] = set()

        def resource_string(value: int) -> str:
            relative = value & 0x7FFFFFFF
            require(relative <= resource_size - 2, "resource name offset outside directory")
            count = u16(data, resource_base + relative)
            byte_count = count * 2
            require(relative + 2 <= resource_size - byte_count, "truncated resource name")
            try:
                return data[resource_base + relative + 2 : resource_base + relative + 2 + byte_count].decode(
                    "utf-16le"
                )
            except UnicodeDecodeError:
                fail("invalid UTF-16 resource name")

        def entry_name(value: int) -> int | str:
            return resource_string(value) if value & 0x80000000 else value

        def walk(relative: int, path: tuple[int | str, ...]) -> None:
            require(relative <= resource_size - 16, "resource subdirectory outside directory")
            require(relative not in active_directories, "cyclic PE resource directory")
            require(relative not in visited_directories, "multiply referenced PE resource directory")
            active_directories.add(relative)
            visited_directories.add(relative)
            directory = resource_base + relative
            _, _, major, minor, named_count, id_count = struct.unpack_from("<IIHHHH", data, directory)
            require(major == 0 and minor == 0, "unsupported PE resource-directory version")
            count = named_count + id_count
            require(count <= 65535 and relative + 16 <= resource_size - count * 8, "truncated resource entries")
            previous_named: str | None = None
            previous_id = -1
            for index in range(count):
                name_raw, target = struct.unpack_from("<II", data, directory + 16 + index * 8)
                named = bool(name_raw & 0x80000000)
                require(named == (index < named_count), "misordered PE resource entries")
                value = entry_name(name_raw)
                if named:
                    require(isinstance(value, str) and (previous_named is None or previous_named <= value),
                            "unsorted named PE resource entries")
                    previous_named = value
                else:
                    require(isinstance(value, int) and value > previous_id, "unsorted numeric PE resource entries")
                    previous_id = value
                new_path = path + (value,)
                target_relative = target & 0x7FFFFFFF
                if target & 0x80000000:
                    require(len(new_path) < 3, "over-deep PE resource tree")
                    walk(target_relative, new_path)
                else:
                    require(len(new_path) == 3, "PE resource leaf is not type/name/language")
                    require(target_relative <= resource_size - 16, "resource data entry outside directory")
                    data_rva, data_size, code_page, reserved = struct.unpack_from(
                        "<IIII", data, resource_base + target_relative
                    )
                    require(reserved == 0, "nonzero PE resource-data reserved field")
                    file_offset = rva_to_file(data_rva, data_size, "resource data")
                    resources.append(Resource(new_path[0], new_path[1], new_path[2], file_offset, data_size, code_page))
            active_directories.remove(relative)

        walk(0, ())
        require(resource_base <= resource_limit <= stub_end, "invalid resource-directory extent")
        keys = {(r.type_value, r.name_value, r.language_value) for r in resources}
        require(len(keys) == len(resources), "duplicate PE resource key")
    require(resources, "InstallUs PE stub has no resources")
    return PEInfo(
        pe_offset,
        timestamp,
        image_base,
        entry_rva,
        section_alignment,
        file_alignment,
        size_of_image,
        size_of_headers,
        resource_rva,
        resource_size,
        stub_end,
        tuple(sections),
        tuple(resources),
    )


@dataclass(frozen=True)
class OuterHeader:
    offset: int
    skipped_byte: int
    strings: tuple[bytes, ...]
    archive_offset: int
    region_sizes: tuple[int, int]
    trailer: bytes


def parse_outer_header(data: mmap.mmap, pe: PEInfo) -> OuterHeader:
    position = pe.stub_end
    require(position < len(data), "missing InstallUs overlay skipped byte")
    skipped_byte = data[position]
    position += 1
    trailer = data[-4:]
    require(trailer[3] == 0xDE, "missing InstallUs footer terminator")
    require(trailer[2] <= 9, "noncanonical InstallUs footer remainder")
    string_offset = 10 * int.from_bytes(trailer[:2], "little") + trailer[2] + 1
    require(string_offset == position, "InstallUs footer does not point just past the PE/skipped byte")
    values: list[bytes] = []
    for index in range(10):
        require(position < len(data), f"truncated overlay string {index}")
        size = data[position]
        position += 1
        values.append(checked_slice(data, position, size, f"overlay string {index}"))
        position += size
    require(data[position : position + 5] == b"SPIS\x1A", "archive does not follow the ten overlay strings")
    require(values[7], "empty phase name")
    region_sizes: list[int] = []
    for index in (8, 9):
        raw = values[index]
        require(raw and all(0x30 <= value <= 0x39 for value in raw), "nonnumeric archive-region length")
        require(len(raw) == 1 or raw[0] != 0x30, "archive-region length has a leading zero")
        value = int(raw)
        require(value > 0, "empty archive region")
        region_sizes.append(value)
    expected_size = position + sum(region_sizes) + 4
    require(expected_size == len(data), "overlay lengths do not account for the complete input")
    return OuterHeader(pe.stub_end, skipped_byte, tuple(values), position, tuple(region_sizes), trailer)


@dataclass(frozen=True)
class ArchiveEntry:
    region_index: int
    archive_index: int
    entry_index: int
    archive_offset: int
    header_offset: int
    data_offset: int
    name: bytes
    dos_datetime: int
    attributes: int
    full_size: int
    compressed_size: int
    method: int
    checksum: int


@dataclass(frozen=True)
class Archive:
    region_index: int
    archive_index: int
    offset: int
    end_offset: int
    full_size: int
    entries: tuple[ArchiveEntry, ...]


def parse_archives(data: mmap.mmap, outer: OuterHeader) -> tuple[Archive, ...]:
    position = outer.archive_offset
    archives: list[Archive] = []
    global_archive_index = 0
    for region_index, region_size in enumerate(outer.region_sizes):
        region_end = position + region_size
        region_archive_index = 0
        while position < region_end:
            archive_offset = position
            require(data[position : position + 5] == b"SPIS\x1A", "missing TCompress archive signature")
            require(position <= region_end - 21, "truncated TCompress archive header")
            magic, method_id, full_size, archive_type, checksum, reserved = struct.unpack_from(
                "<5s3sIBII", data, position
            )
            require(magic == b"SPIS\x1A" and method_id == b"LZH", "unsupported TCompress archive method")
            require(archive_type == 1, "TCompress archive is not a multi-file archive")
            require(checksum == 0 and reserved == 0, "nonzero multi-file archive checksum/reserved field")
            position += 21
            entries: list[ArchiveEntry] = []
            expanded_total = 0
            while position < region_end and data[position : position + 5] != b"SPIS\x1A":
                header_offset = position
                require(position <= region_end - 25, "truncated TCompress file header")
                (
                    filename_length,
                    dos_datetime,
                    attributes,
                    entry_full_size,
                    compressed_size,
                    method,
                    entry_checksum,
                    entry_reserved,
                ) = struct.unpack_from("<hIHIIBII", data, position)
                position += 25
                require(0 < filename_length <= 255, "invalid TCompress filename length")
                name = checked_slice(data, position, filename_length, "TCompress filename")
                position += filename_length
                safe_archive_path(name)
                require(entry_reserved == 0, "nonzero TCompress file reserved field")
                require(method in (0, 2), "unsupported TCompress file compression method")
                if method == 0:
                    require(compressed_size == entry_full_size, "stored entry has unequal sizes")
                    require(entry_checksum == 0, "stored entry has a checksum")
                else:
                    require(entry_full_size == 0 or compressed_size > 0, "compressed entry has no data")
                    require(compressed_size <= entry_full_size or entry_full_size == 0,
                            "LZH entry is not smaller than its original")
                require(position <= region_end - compressed_size, "compressed entry crosses its archive region")
                data_offset = position
                position += compressed_size
                entries.append(
                    ArchiveEntry(
                        region_index,
                        global_archive_index,
                        len(entries),
                        archive_offset,
                        header_offset,
                        data_offset,
                        name,
                        dos_datetime,
                        attributes,
                        entry_full_size,
                        compressed_size,
                        method,
                        entry_checksum,
                    )
                )
                expanded_total += entry_full_size
            require(entries, "empty concatenated TCompress archive")
            require(expanded_total == full_size, "TCompress archive expanded-size total mismatch")
            archives.append(
                Archive(
                    region_index,
                    global_archive_index,
                    archive_offset,
                    position,
                    full_size,
                    tuple(entries),
                )
            )
            global_archive_index += 1
            region_archive_index += 1
        require(position == region_end, "archive region does not end on an entry boundary")
        require(region_archive_index > 0, "archive region contains no archives")
    require(position == len(data) - 4, "archive regions do not end at the trailer")
    return tuple(archives)


def build_install_paths(
    archives: tuple[Archive, ...], setup_inf: bytes, archive_list: bytes
) -> dict[int, Path]:
    """Resolve each main archive to its symbolic Windows installation directory."""
    main_archives = [archive for archive in archives if archive.region_index == 1]
    require(main_archives, "main archive region contains no installable files")
    require(len(archive_list) == len(main_archives) * 16, "iuslst.dat record count mismatch")

    destinations: list[int] = []
    main_region_offset = main_archives[0].offset
    for ordinal, archive in enumerate(main_archives):
        require(len(archive.entries) == 1, "main install archive does not contain exactly one file")
        destination, relative_offset, medium, stored_size = struct.unpack_from(
            "<IIII", archive_list, ordinal * 16
        )
        require(destination > 0, "invalid installation destination index")
        require(medium == 1, "embedded main archive refers to an external installation medium")
        require(relative_offset == archive.offset - main_region_offset, "main archive list offset mismatch")
        require(stored_size == archive.end_offset - archive.offset, "main archive list size mismatch")
        destinations.append(destination)

    sections = parse_setup_ini(setup_inf)
    result: dict[int, Path] = {}
    casefolded_paths: dict[str, Path] = {}
    for section_name, values in sections.items():
        option_match = re.fullmatch(rb"option_([0-9]+)", section_name)
        if option_match is None:
            continue
        option_number = parse_decimal(option_match.group(1), "install option number")
        directory_values = sections.get(f"dirs_{option_number}".encode("ascii"))
        require(directory_values is not None, f"missing dirs_{option_number} section")
        for key, filename in values.items():
            file_match = re.fullmatch(rb"f([0-9]+)", key)
            if file_match is None:
                continue
            file_number = file_match.group(1)
            location_key = b"l" + file_number
            require(location_key in values, f"missing archive location for Option_{option_number} file")
            location = parse_decimal(values[location_key], "main archive location")
            require(location % 4 == 0, "unaligned main archive location")
            ordinal = location // 4
            require(ordinal < len(main_archives), "main archive location is out of range")
            archive = main_archives[ordinal]
            require(archive.archive_index not in result, "main archive is referenced more than once")
            entry = archive.entries[0]
            require(filename == entry.name, "setup.inf filename does not match its main archive")
            directory_key = f"d{destinations[ordinal]}".encode("ascii")
            require(directory_key in directory_values, "missing declared installation directory")
            path = safe_destination_path(directory_values[directory_key], entry.name)
            folded = path.as_posix().casefold()
            path = casefolded_paths.setdefault(folded, path)
            result[archive.archive_index] = path

    require(len(result) == len(main_archives), "not every main archive has an installation mapping")
    return result


class LZHUFDecoder:
    N = 4096
    F = 60
    THRESHOLD = 2
    N_CHAR = 256 - THRESHOLD + F
    T = N_CHAR * 2 - 1
    R = T - 1
    MAX_FREQ = 0x8000

    D_CODE = bytes(
        [0] * 32
        + sum(([value] * 16 for value in range(1, 4)), [])
        + sum(([value] * 8 for value in range(4, 12)), [])
        + sum(([value] * 4 for value in range(12, 24)), [])
        + sum(([value] * 2 for value in range(24, 48)), [])
        + list(range(48, 64))
    )
    D_LEN = bytes([3] * 32 + [4] * 48 + [5] * 64 + [6] * 48 + [7] * 48 + [8] * 16)

    def __init__(self, source: memoryview):
        self.source = source
        self.source_position = 0
        self.eof_zero_reads = 0
        self.bit_buffer = 0
        self.bit_count = 0
        self.frequency = [0] * (self.T + 1)
        self.parent = [0] * (self.T + self.N_CHAR)
        self.child = [0] * self.T
        self._start_huffman()

    def _source_byte(self) -> int:
        if self.source_position == len(self.source):
            self.eof_zero_reads += 1
            return 0
        value = self.source[self.source_position]
        self.source_position += 1
        return value

    def _get_bit(self) -> int:
        while self.bit_count <= 8:
            self.bit_buffer |= self._source_byte() << (8 - self.bit_count)
            self.bit_count += 8
        old_buffer = self.bit_buffer
        self.bit_buffer = (self.bit_buffer << 1) & 0xFFFF
        self.bit_count -= 1
        return old_buffer >> 15

    def _get_byte(self) -> int:
        while self.bit_count <= 8:
            self.bit_buffer |= self._source_byte() << (8 - self.bit_count)
            self.bit_count += 8
        old_buffer = self.bit_buffer
        self.bit_buffer = (self.bit_buffer << 8) & 0xFFFF
        self.bit_count -= 8
        return old_buffer >> 8

    def _start_huffman(self) -> None:
        frequency = self.frequency
        parent = self.parent
        child = self.child
        for index in range(self.N_CHAR):
            frequency[index] = 1
            child[index] = index + self.T
            parent[index + self.T] = index
        source = 0
        target = self.N_CHAR
        while target <= self.R:
            frequency[target] = frequency[source] + frequency[source + 1]
            child[target] = source
            parent[source] = target
            parent[source + 1] = target
            source += 2
            target += 1
        frequency[self.T] = 0xFFFF
        parent[self.R] = 0

    def _reconstruct(self) -> None:
        frequency = self.frequency
        parent = self.parent
        child = self.child
        target = 0
        for source in range(self.T):
            if child[source] >= self.T:
                frequency[target] = (frequency[source] + 1) // 2
                child[target] = child[source]
                target += 1
        source = 0
        target = self.N_CHAR
        while target < self.T:
            combined = frequency[source] + frequency[source + 1]
            frequency[target] = combined
            insertion = target - 1
            while combined < frequency[insertion]:
                insertion -= 1
            insertion += 1
            frequency[insertion + 1 : target + 1] = frequency[insertion:target]
            frequency[insertion] = combined
            child[insertion + 1 : target + 1] = child[insertion:target]
            child[insertion] = source
            source += 2
            target += 1
        for index in range(self.T):
            node = child[index]
            if node >= self.T:
                parent[node] = index
            else:
                parent[node] = index
                parent[node + 1] = index

    def _update(self, symbol: int) -> None:
        frequency = self.frequency
        parent = self.parent
        child = self.child
        if frequency[self.R] == self.MAX_FREQ:
            self._reconstruct()
        node = parent[symbol + self.T]
        while True:
            new_frequency = frequency[node] + 1
            frequency[node] = new_frequency
            exchange = node + 1
            if new_frequency > frequency[exchange]:
                while new_frequency > frequency[exchange + 1]:
                    exchange += 1
                frequency[node] = frequency[exchange]
                frequency[exchange] = new_frequency
                first = child[node]
                parent[first] = exchange
                if first < self.T:
                    parent[first + 1] = exchange
                second = child[exchange]
                child[exchange] = first
                parent[second] = node
                if second < self.T:
                    parent[second + 1] = node
                child[node] = second
                node = exchange
            node = parent[node]
            if node == 0:
                break

    def _decode_symbol(self) -> int:
        symbol = self.child[self.R]
        while symbol < self.T:
            symbol = self.child[symbol + self._get_bit()]
        symbol -= self.T
        self._update(symbol)
        return symbol

    def _decode_position(self) -> int:
        value = self._get_byte()
        position = self.D_CODE[value] << 6
        remaining = self.D_LEN[value] - 2
        while remaining:
            value = (value << 1) + self._get_bit()
            remaining -= 1
        return position | (value & 0x3F)

    def expand_to(self, full_size: int, destination: BinaryIO) -> tuple[int, str]:
        require(full_size >= 0, "negative LZH output size")
        window = bytearray(self.N)
        window[: self.N - self.F] = b" " * (self.N - self.F)
        window_position = self.N - self.F
        output_count = 0
        checksum = 0
        digest = hashlib.sha256()
        block = bytearray()
        window_mask = self.N - 1
        flush_size = 1024 * 1024

        source = self.source
        source_length = len(source)
        input_position = self.source_position
        eof_zero_reads = self.eof_zero_reads
        bit_buffer = self.bit_buffer
        bit_count = self.bit_count
        frequency = self.frequency
        parent = self.parent
        child = self.child
        tree_size = self.T
        tree_root = self.R
        d_code = self.D_CODE
        d_length = self.D_LEN

        while output_count < full_size:
            symbol = child[tree_root]
            while symbol < tree_size:
                while bit_count <= 8:
                    if input_position == source_length:
                        eof_zero_reads += 1
                        next_byte = 0
                    else:
                        next_byte = source[input_position]
                        input_position += 1
                    bit_buffer |= next_byte << (8 - bit_count)
                    bit_count += 8
                bit = bit_buffer >> 15
                bit_buffer = (bit_buffer << 1) & 0xFFFF
                bit_count -= 1
                symbol = child[symbol + bit]
            symbol -= tree_size

            if frequency[tree_root] == self.MAX_FREQ:
                self._reconstruct()
            node = parent[symbol + tree_size]
            while True:
                new_frequency = frequency[node] + 1
                frequency[node] = new_frequency
                exchange = node + 1
                if new_frequency > frequency[exchange]:
                    while new_frequency > frequency[exchange + 1]:
                        exchange += 1
                    frequency[node] = frequency[exchange]
                    frequency[exchange] = new_frequency
                    first = child[node]
                    parent[first] = exchange
                    if first < tree_size:
                        parent[first + 1] = exchange
                    second = child[exchange]
                    child[exchange] = first
                    parent[second] = node
                    if second < tree_size:
                        parent[second + 1] = node
                    child[node] = second
                    node = exchange
                node = parent[node]
                if node == 0:
                    break

            if symbol < 256:
                block.append(symbol)
                window[window_position] = symbol
                window_position = (window_position + 1) & window_mask
                output_count += 1
            else:
                while bit_count <= 8:
                    if input_position == source_length:
                        eof_zero_reads += 1
                        next_byte = 0
                    else:
                        next_byte = source[input_position]
                        input_position += 1
                    bit_buffer |= next_byte << (8 - bit_count)
                    bit_count += 8
                position_value = bit_buffer >> 8
                bit_buffer = (bit_buffer << 8) & 0xFFFF
                bit_count -= 8
                distance = d_code[position_value] << 6
                remaining = d_length[position_value] - 2
                while remaining:
                    while bit_count <= 8:
                        if input_position == source_length:
                            eof_zero_reads += 1
                            next_byte = 0
                        else:
                            next_byte = source[input_position]
                            input_position += 1
                        bit_buffer |= next_byte << (8 - bit_count)
                        bit_count += 8
                    position_value = (position_value << 1) + (bit_buffer >> 15)
                    bit_buffer = (bit_buffer << 1) & 0xFFFF
                    bit_count -= 1
                    remaining -= 1
                distance |= position_value & 0x3F
                distance += 1
                match_position = (window_position - distance) & window_mask
                length = symbol - 255 + self.THRESHOLD
                require(
                    output_count + length <= full_size,
                    f"LZH match overruns declared output size "
                    f"({output_count}+{length}>{full_size}, input byte {input_position})",
                )
                seed_length = min(distance, length)
                source_end = match_position + seed_length
                if source_end <= self.N:
                    chunk = bytes(window[match_position:source_end])
                else:
                    chunk = bytes(window[match_position:]) + bytes(window[: source_end - self.N])
                if seed_length < length:
                    chunk = (chunk * ((length + seed_length - 1) // seed_length))[:length]

                first_length = min(length, self.N - window_position)
                window[window_position : window_position + first_length] = chunk[:first_length]
                if first_length < length:
                    window[: length - first_length] = chunk[first_length:]
                window_position = (window_position + length) & window_mask
                block.extend(chunk)
                output_count += length

            if len(block) >= flush_size:
                destination.write(block)
                digest.update(block)
                checksum = (checksum + sum(block)) & 0xFFFFFFFF
                block.clear()
        if block:
            destination.write(block)
            digest.update(block)
            checksum = (checksum + sum(block)) & 0xFFFFFFFF

        self.source_position = input_position
        self.eof_zero_reads = eof_zero_reads
        self.bit_buffer = bit_buffer
        self.bit_count = bit_count
        require(input_position == source_length, "unused bytes at end of LZH bitstream")
        expected_eof_fill = 0 if full_size == 0 else 1
        require(
            eof_zero_reads == expected_eof_fill,
            "noncanonical LZH terminal EOF fill",
        )
        require(bit_count <= 15, "invalid terminal LZH bit count")
        if bit_count:
            require(bit_buffer == 0, "nonzero LZH padding bits")
        return checksum, digest.hexdigest()


def value_filename(value: int | str) -> str:
    if isinstance(value, int):
        return f"id_{value:05d}"
    encoded = value.encode("utf-8")
    return "name_" + safe_component(encoded)


def resource_extension(type_value: int | str) -> str:
    if not isinstance(type_value, int):
        return ".bin"
    return {
        1: ".curdata",
        2: ".dib",
        3: ".icondata",
        4: ".menu",
        5: ".dialog",
        6: ".stringtable",
        7: ".fontdir",
        8: ".font",
        9: ".accelerator",
        10: ".rcdata",
        11: ".messagetable",
        12: ".group_cursor",
        14: ".group_icon",
        16: ".version",
        21: ".ani.cur",
        22: ".ani.ico",
        23: ".html",
        24: ".manifest",
    }.get(type_value, ".bin")


def extract_resource(data: mmap.mmap, resource: Resource, root: Path) -> dict[str, object]:
    type_name = RESOURCE_TYPES.get(resource.type_value, str(resource.type_value))
    path = (
        root
        / "pe_resources"
        / safe_component(type_name.encode("utf-8"))
        / value_filename(resource.name_value)
        / (value_filename(resource.language_value) + resource_extension(resource.type_value))
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = checked_slice(data, resource.data_offset, resource.size, "PE resource")
    path.write_bytes(raw)
    return {
        "type": resource.type_value,
        "type_name": type_name,
        "name": resource.name_value,
        "language": resource.language_value,
        "code_page": resource.code_page,
        "input_offset": resource.data_offset,
        "size": resource.size,
        "sha256": sha256_bytes(raw),
        "output": path.relative_to(root).as_posix(),
    }


def extract_entry(
    data: mmap.mmap, entry: ArchiveEntry, root: Path, installed_path: Path | None = None
) -> dict[str, object]:
    region_name = "bootstrap" if entry.region_index == 0 else "main"
    relative = installed_path or (
        Path("payload")
        / region_name
        / f"archive_{entry.archive_index:04d}"
        / f"entry_{entry.entry_index:04d}"
        / safe_archive_path(entry.name)
    )
    output = root / relative
    output.parent.mkdir(parents=True, exist_ok=True)
    if entry.method == 0:
        raw = checked_slice(data, entry.data_offset, entry.compressed_size, "stored entry")
        output.write_bytes(raw)
        checksum = 0
        digest = sha256_bytes(raw)
    else:
        source = memoryview(data)[entry.data_offset : entry.data_offset + entry.compressed_size]
        try:
            with output.open("wb") as destination:
                decoder = LZHUFDecoder(source)
                checksum, digest = decoder.expand_to(entry.full_size, destination)
        finally:
            source.release()
        require(checksum == entry.checksum, f"checksum mismatch for {json_name(entry.name)!r}")
        require(output.stat().st_size == entry.full_size, "expanded output size mismatch")
    return {
        "region": region_name,
        "archive_index": entry.archive_index,
        "entry_index": entry.entry_index,
        "name": json_name(entry.name),
        "name_bytes_hex": entry.name.hex(),
        "dos_datetime": entry.dos_datetime,
        "attributes": entry.attributes,
        "input_header_offset": entry.header_offset,
        "input_data_offset": entry.data_offset,
        "full_size": entry.full_size,
        "compressed_size": entry.compressed_size,
        "method": "stored" if entry.method == 0 else "lzhuf",
        "checksum": entry.checksum,
        "sha256": digest,
        "output": relative.as_posix(),
    }


_WORKER_FILE: BinaryIO | None = None
_WORKER_DATA: mmap.mmap | None = None


def initialize_decode_worker(input_name: str) -> None:
    """Open one shared read-only input mapping per decoder worker process."""
    global _WORKER_FILE, _WORKER_DATA
    _WORKER_FILE = open(input_name, "rb")
    _WORKER_DATA = mmap.mmap(_WORKER_FILE.fileno(), 0, access=mmap.ACCESS_READ)


def extract_entry_job(
    job: tuple[tuple[ArchiveEntry, ...], str, tuple[Path | None, ...]],
) -> list[dict[str, object]]:
    """Decode one ordered group; entries in a group may overwrite each other."""
    entries, root_name, installed_paths = job
    require(_WORKER_DATA is not None, "decoder worker was not initialized")
    root = Path(root_name)
    return [
        extract_entry(_WORKER_DATA, entry, root, installed_path)
        for entry, installed_path in zip(entries, installed_paths, strict=True)
    ]


def extract_entry_jobs(
    input_path: Path,
    data: mmap.mmap,
    jobs: list[tuple[tuple[ArchiveEntry, ...], Path, tuple[Path | None, ...]]],
) -> list[dict[str, object]]:
    """Decode independent archive groups concurrently, preserving job order."""
    if not jobs:
        return []
    worker_count = min(len(jobs), os.cpu_count() or 1, 8)
    if worker_count == 1:
        return [
            extract_entry(data, entry, root, installed_path)
            for entries, root, installed_paths in jobs
            for entry, installed_path in zip(entries, installed_paths, strict=True)
        ]
    worker_jobs = [
        (entries, str(root), installed_paths) for entries, root, installed_paths in jobs
    ]
    with ProcessPoolExecutor(
        max_workers=worker_count,
        initializer=initialize_decode_worker,
        initargs=(str(input_path),),
    ) as executor:
        grouped_records = executor.map(extract_entry_job, worker_jobs)
        return [record for records in grouped_records for record in records]


def build_manifest(
    input_path: Path,
    data: mmap.mmap,
    pe: PEInfo,
    outer: OuterHeader,
    archives: tuple[Archive, ...],
    resource_records: list[dict[str, object]],
    entry_records: list[dict[str, object]],
) -> dict[str, object]:
    regions = []
    position = outer.archive_offset
    for index, size in enumerate(outer.region_sizes):
        regions.append({"index": index, "name": "bootstrap" if index == 0 else "main", "offset": position, "size": size})
        position += size
    return {
        "format": "InstallUs / TCompress LZHUF self-extracting installer",
        "input": str(input_path),
        "input_size": len(data),
        "input_sha256": hashlib.sha256(data).hexdigest(),
        "byte_accounting": {
            "pe_stub": {"offset": 0, "size": pe.stub_end},
            "overlay_header": {"offset": pe.stub_end, "size": outer.archive_offset - pe.stub_end},
            "archive_regions": regions,
            "trailer": {"offset": len(data) - 4, "size": 4, "hex": outer.trailer.hex()},
            "total": pe.stub_end + (outer.archive_offset - pe.stub_end) + sum(outer.region_sizes) + 4,
        },
        "pe": {
            "pe_offset": pe.pe_offset,
            "timestamp": pe.timestamp,
            "image_base": pe.image_base,
            "entry_rva": pe.entry_rva,
            "section_alignment": pe.section_alignment,
            "file_alignment": pe.file_alignment,
            "size_of_image": pe.size_of_image,
            "size_of_headers": pe.size_of_headers,
            "resource_rva": pe.resource_rva,
            "resource_size": pe.resource_size,
            "stub_end": pe.stub_end,
            "sections": [section.__dict__ for section in pe.sections],
            "resources": resource_records,
        },
        "overlay": {
            "offset": outer.offset,
            "skipped_byte": outer.skipped_byte,
            "strings": [json_name(value) for value in outer.strings],
            "strings_bytes_hex": [value.hex() for value in outer.strings],
            "archive_offset": outer.archive_offset,
            "region_sizes": list(outer.region_sizes),
            "trailer_hex": outer.trailer.hex(),
        },
        "archives": [
            {
                "region": "bootstrap" if archive.region_index == 0 else "main",
                "archive_index": archive.archive_index,
                "offset": archive.offset,
                "end_offset": archive.end_offset,
                "stored_size": archive.end_offset - archive.offset,
                "full_size": archive.full_size,
                "entry_count": len(archive.entries),
            }
            for archive in archives
        ],
        "files": entry_records,
        "summary": {
            "archive_count": len(archives),
            "payload_file_count": len(entry_records),
            "pe_resource_count": len(resource_records),
            "payload_expanded_bytes": sum(entry.full_size for archive in archives for entry in archive.entries),
            "payload_stored_bytes": sum(entry.compressed_size for archive in archives for entry in archive.entries),
        },
    }


def run(input_name: str, output_name: str, include_all: bool = False) -> None:
    input_path = Path(input_name)
    output_path = Path(output_name)
    require(input_path.is_file(), "input is not a regular file")
    output_exists = os.path.lexists(output_path)
    if output_exists:
        require(
            output_path.is_dir() and not output_path.is_symlink(),
            "pre-existing output path is not a real directory",
        )
    parent = output_path.parent if output_path.parent != Path("") else Path(".")
    require(parent.is_dir(), "output parent directory does not exist")
    stage = Path(tempfile.mkdtemp(prefix=f".{output_path.name}.tmp-", dir=parent))
    try:
        with input_path.open("rb") as source_file:
            data = mmap.mmap(source_file.fileno(), 0, access=mmap.ACCESS_READ)
            try:
                pe = parse_pe(data)
                outer = parse_outer_header(data, pe)
                archives = parse_archives(data, outer)
                if include_all:
                    resource_records = [extract_resource(data, resource, stage) for resource in pe.resources]
                    entry_jobs = [
                        ((entry,), stage, (None,))
                        for archive in archives
                        for entry in archive.entries
                    ]
                    entry_records = extract_entry_jobs(input_path, data, entry_jobs)
                    manifest = build_manifest(
                        input_path, data, pe, outer, archives, resource_records, entry_records
                    )
                    (stage / "installus_manifest.json").write_text(
                        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
                    )
                else:
                    metadata_root = stage / ".installus-bootstrap"
                    bootstrap_entries = [
                        entry
                        for archive in archives
                        if archive.region_index == 0
                        for entry in archive.entries
                    ]

                    def bootstrap_entry(name: bytes) -> ArchiveEntry:
                        matches = [entry for entry in bootstrap_entries if entry.name.lower() == name]
                        require(len(matches) == 1, f"bootstrap does not contain exactly one {name.decode()}")
                        return matches[0]

                    setup_entry = bootstrap_entry(b"setup.inf")
                    list_entry = bootstrap_entry(b"iuslst.dat")
                    bootstrap_records = [
                        extract_entry(data, setup_entry, metadata_root),
                        extract_entry(data, list_entry, metadata_root),
                    ]

                    def metadata_file(name: str) -> bytes:
                        matches = [record for record in bootstrap_records if record["name"].lower() == name]
                        require(len(matches) == 1, f"bootstrap does not contain exactly one {name}")
                        return (metadata_root / str(matches[0]["output"])).read_bytes()

                    install_paths = build_install_paths(
                        archives, metadata_file("setup.inf"), metadata_file("iuslst.dat")
                    )
                    destination_groups: dict[str, tuple[Path, list[ArchiveEntry]]] = {}
                    for archive in archives:
                        if archive.region_index != 1:
                            continue
                        for entry in archive.entries:
                            path = install_paths[archive.archive_index]
                            folded = path.as_posix().casefold()
                            if folded not in destination_groups:
                                destination_groups[folded] = (path, [])
                            destination_groups[folded][1].append(entry)
                    install_jobs = [
                        (tuple(entries), stage, tuple(path for _ in entries))
                        for path, entries in destination_groups.values()
                    ]
                    bootstrap_validation_jobs = [
                        ((entry,), metadata_root, (None,))
                        for entry in bootstrap_entries
                        if entry not in (setup_entry, list_entry)
                    ]
                    extract_entry_jobs(
                        input_path, data, bootstrap_validation_jobs + install_jobs
                    )
                    shutil.rmtree(metadata_root)
            finally:
                data.close()
        make_user_group_readable(stage)
        if output_exists:
            merge_staged_output(stage, output_path)
            shutil.rmtree(stage, ignore_errors=True)
        else:
            os.rename(stage, output_path)
    except BaseException:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def main(argv: list[str]) -> int:
    include_all = len(argv) == 4 and argv[1] == "--all"
    if not (len(argv) == 3 or include_all):
        print(f"Usage: {Path(argv[0]).name} [--all] <inputFile> <outputDir>", file=sys.stderr)
        return 2
    argument_offset = 2 if include_all else 1
    try:
        run(argv[argument_offset], argv[argument_offset + 1], include_all)
    except (FormatError, OSError, UnicodeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

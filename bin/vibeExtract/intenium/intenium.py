#!/usr/bin/env python3
# Vibe coded by Codex
"""Extract the installed payload from an INTENIUM stgc installer."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import sys
import zlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import BinaryIO, Iterable
from urllib.parse import quote


class FormatError(Exception):
    """The input is not a supported, internally consistent INTENIUM installer."""


def _u16(data: bytes, offset: int) -> int:
    if offset < 0 or offset + 2 > len(data):
        raise FormatError(f"truncated 16-bit field at file offset 0x{offset:x}")
    return struct.unpack_from("<H", data, offset)[0]


def _u32(data: bytes, offset: int) -> int:
    if offset < 0 or offset + 4 > len(data):
        raise FormatError(f"truncated 32-bit field at file offset 0x{offset:x}")
    return struct.unpack_from("<I", data, offset)[0]


def _decode(raw: bytes, what: str) -> str:
    # The format stores Windows ANSI strings and carries no code-page field.
    try:
        return raw.decode("cp1252")
    except UnicodeDecodeError as exc:
        raise FormatError(f"invalid Windows-1252 {what}") from exc


def _component(text: str, what: str) -> str:
    if not text or text in (".", "..") or any(ch in text for ch in "/\\\0:"):
        raise FormatError(f"unsafe {what}: {text!r}")
    return text


def _rotl3(value: int) -> int:
    return ((value << 3) | (value >> 29)) & 0xFFFFFFFF


def _stgc_checksum(data: bytes, start: int, size: int) -> int:
    value = 0
    for byte in data[start + 40 : start + size]:
        value = _rotl3(value) ^ byte
    return value


@dataclass
class Section:
    name: str
    virtual_address: int
    virtual_size: int
    raw_offset: int
    raw_size: int


@dataclass
class PEResource:
    path: tuple[str, ...]
    data: bytes
    code_page: int


@dataclass
class PEInfo:
    image_end: int
    package_end: int
    certificate_offset: int
    certificate_size: int
    certificate_count: int
    resources: list[PEResource]


@dataclass
class Entry:
    container_index: int
    record_offset: int
    timestamp: int
    data_offset: int
    original_size: int
    stored_size: int
    name_offset: int
    name_length: int
    entry_type: int
    name: str
    archive_parts: tuple[str, ...]
    digest: str = ""
    output_parts: tuple[str, ...] | None = None


@dataclass
class Container:
    index: int
    file_offset: int
    size: int
    checksum: int
    timestamp: int
    kind: str
    identifier: str
    roots: list[Entry] = field(default_factory=list)
    entries: list[Entry] = field(default_factory=list)

    @property
    def files(self) -> list[Entry]:
        return [entry for entry in self.entries if entry.entry_type in (0, 1)]


@dataclass
class Installer:
    source: Path
    data: bytes
    pe: PEInfo
    containers: list[Container]
    signature_padding: int


def _rva_to_file(rva: int, size: int, sections: list[Section]) -> int:
    for section in sections:
        relative = rva - section.virtual_address
        if relative < 0:
            continue
        if relative + size <= section.raw_size:
            return section.raw_offset + relative
    raise FormatError(f"RVA 0x{rva:x} (size 0x{size:x}) is not file-backed")


def _resource_label(value: int | str) -> str:
    if isinstance(value, int):
        return f"id_{value}"
    # Preserve the exact UTF-16 name through reversible percent encoding.
    return "name_" + quote(value, safe="-_.()[]{}")


def _parse_pe_resources(
    data: bytes, rsrc_rva: int, rsrc_size: int, sections: list[Section]
) -> list[PEResource]:
    if not rsrc_rva and not rsrc_size:
        return []
    if not rsrc_rva or not rsrc_size:
        raise FormatError("incomplete PE resource data-directory entry")
    base = _rva_to_file(rsrc_rva, rsrc_size, sections)
    limit = base + rsrc_size
    resources: list[PEResource] = []
    active: set[int] = set()

    def within(relative: int, size: int, what: str) -> int:
        absolute = base + relative
        if relative < 0 or absolute + size > limit:
            raise FormatError(f"PE resource {what} is outside its data directory")
        return absolute

    def name_of(value: int) -> int | str:
        if not value & 0x80000000:
            return value
        relative = value & 0x7FFFFFFF
        absolute = within(relative, 2, "name")
        length = _u16(data, absolute)
        absolute = within(relative + 2, length * 2, "name text")
        try:
            return data[absolute : absolute + length * 2].decode("utf-16le")
        except UnicodeDecodeError as exc:
            raise FormatError("invalid UTF-16 PE resource name") from exc

    def directory(relative: int, path: tuple[str, ...], depth: int) -> None:
        if depth > 16 or relative in active:
            raise FormatError("cyclic or excessively deep PE resource tree")
        active.add(relative)
        absolute = within(relative, 16, "directory")
        named = _u16(data, absolute + 12)
        ids = _u16(data, absolute + 14)
        count = named + ids
        entries = within(relative + 16, count * 8, "directory entries")
        for index in range(count):
            name_value, child_value = struct.unpack_from("<II", data, entries + index * 8)
            label = _resource_label(name_of(name_value))
            child_relative = child_value & 0x7FFFFFFF
            child_path = path + (label,)
            if child_value & 0x80000000:
                directory(child_relative, child_path, depth + 1)
            else:
                leaf = within(child_relative, 16, "data entry")
                payload_rva, payload_size, code_page, reserved = struct.unpack_from(
                    "<IIII", data, leaf
                )
                if reserved:
                    raise FormatError("nonzero reserved PE resource data field")
                payload_offset = _rva_to_file(payload_rva, payload_size, sections)
                if payload_offset + payload_size > len(data):
                    raise FormatError("truncated PE resource payload")
                resources.append(
                    PEResource(child_path, data[payload_offset : payload_offset + payload_size], code_page)
                )
        active.remove(relative)

    directory(0, (), 0)
    return resources


def _parse_pe(data: bytes) -> PEInfo:
    if len(data) < 64 or data[:2] != b"MZ":
        raise FormatError("missing DOS MZ signature")
    pe_offset = _u32(data, 0x3C)
    if pe_offset < 64 or pe_offset + 24 > len(data) or data[pe_offset : pe_offset + 4] != b"PE\0\0":
        raise FormatError("missing or invalid PE signature")
    machine = _u16(data, pe_offset + 4)
    section_count = _u16(data, pe_offset + 6)
    optional_size = _u16(data, pe_offset + 20)
    if machine != 0x14C or not section_count:
        raise FormatError("carrier is not a 32-bit x86 PE image")
    optional = pe_offset + 24
    if optional + optional_size > len(data) or optional_size < 96:
        raise FormatError("truncated PE optional header")
    if _u16(data, optional) != 0x10B:
        raise FormatError("carrier is not a PE32 image")
    directory_count = _u32(data, optional + 92)
    available_directories = (optional_size - 96) // 8
    if directory_count > available_directories:
        raise FormatError("PE data-directory count exceeds the optional header")
    table = optional + optional_size
    if table + section_count * 40 > len(data):
        raise FormatError("truncated PE section table")
    sections: list[Section] = []
    image_end = _u32(data, optional + 60)  # SizeOfHeaders
    if image_end > len(data):
        raise FormatError("PE headers extend beyond end of file")
    for index in range(section_count):
        entry = table + index * 40
        raw_name = data[entry : entry + 8].split(b"\0", 1)[0]
        name = raw_name.decode("ascii", "replace")
        virtual_size, virtual_address, raw_size, raw_offset = struct.unpack_from(
            "<IIII", data, entry + 8
        )
        if raw_size and (raw_offset < image_end or raw_offset + raw_size > len(data)):
            raise FormatError(f"PE section {name!r} is outside the file")
        image_end = max(image_end, raw_offset + raw_size)
        sections.append(Section(name, virtual_address, virtual_size, raw_offset, raw_size))

    def data_directory(index: int) -> tuple[int, int]:
        if index >= directory_count:
            return 0, 0
        return struct.unpack_from("<II", data, optional + 96 + index * 8)

    rsrc_rva, rsrc_size = data_directory(2)
    resources = _parse_pe_resources(data, rsrc_rva, rsrc_size, sections)
    certificate_offset, certificate_size = data_directory(4)
    if bool(certificate_offset) != bool(certificate_size):
        raise FormatError("incomplete PE certificate data-directory entry")
    certificate_count = 0
    package_end = len(data)
    if certificate_offset:
        if certificate_offset % 8 or certificate_offset < image_end:
            raise FormatError("misplaced PE certificate table")
        if certificate_offset + certificate_size != len(data):
            raise FormatError("PE certificate table does not end at end of file")
        cursor = certificate_offset
        certificate_end = certificate_offset + certificate_size
        while cursor < certificate_end:
            if cursor + 8 > certificate_end:
                raise FormatError("truncated WIN_CERTIFICATE header")
            length, revision, certificate_type = struct.unpack_from("<IHH", data, cursor)
            if length < 8 or cursor + length > certificate_end:
                raise FormatError("invalid WIN_CERTIFICATE length")
            if revision not in (0x0100, 0x0200) or not certificate_type:
                raise FormatError("invalid WIN_CERTIFICATE metadata")
            certificate_count += 1
            cursor += (length + 7) & ~7
        if cursor != certificate_end:
            raise FormatError("WIN_CERTIFICATE alignment exceeds the certificate table")
        package_end = certificate_offset
    if image_end >= package_end:
        raise FormatError("PE carrier has no appended INTENIUM package")
    return PEInfo(
        image_end,
        package_end,
        certificate_offset,
        certificate_size,
        certificate_count,
        resources,
    )


def _bounded_cstring(data: bytes, base: int, relative: int, size: int, what: str) -> tuple[str, int]:
    if relative < 0 or relative >= size:
        raise FormatError(f"{what} offset is outside its container")
    end = data.find(b"\0", base + relative, base + size)
    if end < 0:
        raise FormatError(f"unterminated {what}")
    raw = data[base + relative : end]
    return _decode(raw, what), len(raw) + 1


def _process_entry(data: bytes, base: int, entry: Entry, sink: BinaryIO | None = None) -> str:
    start = base + entry.data_offset
    if entry.entry_type == 0:
        raw = data[start : start + entry.original_size]
        if len(raw) != entry.original_size:
            raise FormatError(f"truncated raw file data for {'/'.join(entry.archive_parts)}")
        if sink is not None:
            sink.write(raw)
        return hashlib.sha256(raw).hexdigest()
    if entry.entry_type != 1:
        raise FormatError(f"cannot extract entry type {entry.entry_type}")
    compressed = memoryview(data)[start : start + entry.stored_size]
    stream = zlib.decompressobj()
    digest = hashlib.sha256()
    produced = 0
    cursor = 0
    try:
        while cursor < len(compressed):
            block = compressed[cursor : cursor + 1024 * 1024]
            cursor += len(block)
            pending = block
            while pending:
                remaining = entry.original_size - produced
                if remaining < 0:
                    raise FormatError(f"expanded size exceeds declaration for {'/'.join(entry.archive_parts)}")
                output = stream.decompress(pending, remaining + 1)
                pending = stream.unconsumed_tail
                produced += len(output)
                if produced > entry.original_size:
                    raise FormatError(f"expanded size exceeds declaration for {'/'.join(entry.archive_parts)}")
                digest.update(output)
                if sink is not None:
                    sink.write(output)
                if not output and pending and not stream.eof:
                    raise FormatError(f"stalled zlib stream for {'/'.join(entry.archive_parts)}")
        remaining = entry.original_size - produced
        output = stream.flush(remaining + 1)
    except zlib.error as exc:
        raise FormatError(f"invalid zlib stream for {'/'.join(entry.archive_parts)}: {exc}") from exc
    produced += len(output)
    digest.update(output)
    if sink is not None:
        sink.write(output)
    if produced != entry.original_size:
        raise FormatError(
            f"expanded size mismatch for {'/'.join(entry.archive_parts)}: "
            f"declared {entry.original_size}, got {produced}"
        )
    if not stream.eof or stream.unused_data or stream.unconsumed_tail:
        raise FormatError(f"zlib stream boundary mismatch for {'/'.join(entry.archive_parts)}")
    return digest.hexdigest()


def _parse_container(data: bytes, start: int, limit: int, index: int) -> Container:
    if start + 44 > limit or data[start : start + 8] != b"stgc_hdr":
        raise FormatError(f"missing stgc_hdr at file offset 0x{start:x}")
    version, checksum, size = struct.unpack_from("<III", data, start + 8)
    if version != 1:
        raise FormatError(f"unsupported stgc header version {version}")
    if size < 44 or start + size > limit:
        raise FormatError(f"invalid stgc container size 0x{size:x}")
    timestamp = struct.unpack_from("<Q", data, start + 20)[0]
    kind_offset, identifier_offset = struct.unpack_from("<II", data, start + 28)
    if data[start + 36 : start + 40] != b"data":
        raise FormatError("missing stgc data marker")
    root_count = _u32(data, start + 40)
    if not root_count or 44 + root_count * 32 > size:
        raise FormatError("invalid stgc root-record count")
    if _stgc_checksum(data, start, size) != checksum:
        raise FormatError(f"stgc checksum mismatch at file offset 0x{start:x}")
    kind, kind_bytes = _bounded_cstring(data, start, kind_offset, size, "package kind")
    identifier, identifier_bytes = _bounded_cstring(
        data, start, identifier_offset, size, "package identifier"
    )
    _component(identifier, "package identifier")
    container = Container(index, start, size, checksum, timestamp, kind, identifier)
    intervals: list[tuple[int, int, str]] = [(0, 44, "header")]
    intervals.extend(
        [
            (kind_offset, kind_offset + kind_bytes, "package kind"),
            (identifier_offset, identifier_offset + identifier_bytes, "package identifier"),
        ]
    )
    seen_records: set[int] = set()

    def interval(relative: int, length: int, what: str) -> None:
        if relative < 0 or length < 0 or relative + length > size:
            raise FormatError(f"{what} is outside its stgc container")
        intervals.append((relative, relative + length, what))

    def record(relative: int, parents: tuple[str, ...], depth: int) -> Entry:
        if depth > 1024 or relative in seen_records:
            raise FormatError("cyclic, duplicate, or excessively deep stgc record tree")
        seen_records.add(relative)
        interval(relative, 32, "entry record")
        fields = struct.unpack_from("<QIIIIII", data, start + relative)
        timestamp_value, data_offset, original_size, stored_size, name_offset, name_length, entry_type = fields
        name, encoded_length = _bounded_cstring(data, start, name_offset, size, "entry name")
        if encoded_length != name_length + 1:
            raise FormatError(f"entry-name length mismatch at container offset 0x{relative:x}")
        _component(name, "entry name")
        interval(name_offset, encoded_length, "entry name")
        item = Entry(
            index,
            relative,
            timestamp_value,
            data_offset,
            original_size,
            stored_size,
            name_offset,
            name_length,
            entry_type,
            name,
            parents + (name,),
        )
        container.entries.append(item)
        if entry_type == 0:
            if stored_size:
                raise FormatError(f"raw file has nonzero compressed size at container offset 0x{relative:x}")
            if original_size:
                interval(data_offset, original_size, "raw file data")
            item.digest = _process_entry(data, start, item)
        elif entry_type == 1:
            interval(data_offset, stored_size, "compressed file data")
            item.digest = _process_entry(data, start, item)
        elif entry_type == 2:
            if original_size or stored_size:
                raise FormatError(f"directory has nonzero size at container offset 0x{relative:x}")
            interval(data_offset, 4, "directory child count")
            child_count = _u32(data, start + data_offset)
            if data_offset + 4 + child_count * 32 > size:
                raise FormatError("directory child records are outside their stgc container")
            for child_index in range(child_count):
                record(data_offset + 4 + child_index * 32, parents + (name,), depth + 1)
        else:
            raise FormatError(f"unsupported stgc entry type {entry_type}")
        return item

    for root_index in range(root_count):
        container.roots.append(record(44 + root_index * 32, (), 0))

    # Every byte is required to belong to exactly one typed structure or payload.
    points: list[tuple[int, int, str]] = []
    for begin, end, label in intervals:
        points.append((begin, 1, label))
        points.append((end, -1, label))
    points.sort(key=lambda point: (point[0], point[1]))
    active = 0
    previous = 0
    for position, change, label in points:
        if position > previous and active != 1:
            state = "unreferenced" if active == 0 else "multiply referenced"
            raise FormatError(
                f"{state} bytes 0x{previous:x}..0x{position:x} in stgc container {index}"
            )
        active += change
        if active < 0:
            raise FormatError(f"invalid interval accounting near {label}")
        previous = position
    if previous != size or active:
        raise FormatError(f"stgc container {index} does not account for every byte")
    return container


def _output_parts(container: Container, entry: Entry, include_all: bool) -> tuple[str, ...] | None:
    root, *tail = entry.archive_parts
    if root in ("%DIR_GAME%", "#DIR_GAME#"):
        return ("games", container.identifier, *tail)
    if root == "%DIR_GP%":
        return ("GamePlayer", *tail)
    if root == "~Info":
        if not include_all:
            return None
        return ("_intenium", "package_metadata", container.identifier, *tail)
    return entry.archive_parts


def _resource_output(resource: PEResource, index: int) -> tuple[str, ...]:
    suffix = ".bin"
    if resource.path and resource.path[0] == "id_24":
        suffix = ".xml"
    leaf = resource.path[-1] + suffix if resource.path else f"resource_{index}.bin"
    return ("_intenium", "pe_resources", *resource.path[:-1], leaf)


def parse_installer(source: Path, include_all: bool) -> Installer:
    try:
        data = source.read_bytes()
    except OSError as exc:
        raise FormatError(f"cannot read input: {exc}") from exc
    pe = _parse_pe(data)
    containers: list[Container] = []
    cursor = pe.image_end
    while cursor < pe.package_end and data[cursor : cursor + 8] == b"stgc_hdr":
        container = _parse_container(data, cursor, pe.package_end, len(containers))
        containers.append(container)
        cursor += container.size
    if not containers:
        raise FormatError("PE image has no INTENIUM stgc containers")
    padding = pe.package_end - cursor
    if padding:
        expected = (-cursor) & 7 if pe.certificate_offset else 0
        if padding != expected or any(data[cursor : pe.package_end]):
            raise FormatError(f"unexpected bytes after final stgc container at file offset 0x{cursor:x}")

    targets: dict[tuple[str, ...], Entry] = {}
    kinds: dict[tuple[str, ...], str] = {}
    for container in containers:
        for entry in container.files:
            entry.output_parts = _output_parts(container, entry, include_all)
            if entry.output_parts is None:
                continue
            canonical = entry.output_parts
            prior = targets.get(canonical)
            if prior is not None:
                if include_all and prior.digest != entry.digest:
                    prior_container = containers[prior.container_index]
                    superseded = (
                        "_intenium",
                        "superseded",
                        f"{prior.container_index:04d}_{prior_container.identifier}",
                        *prior.archive_parts,
                    )
                    if superseded in targets:
                        raise FormatError(f"superseded-output collision at {'/'.join(superseded)}")
                    prior.output_parts = superseded
                    targets[superseded] = prior
                    kinds[superseded] = "file"
                else:
                    prior.output_parts = None
            targets[canonical] = entry
            kinds[canonical] = "file"
    if include_all:
        for index, resource in enumerate(pe.resources):
            parts = _resource_output(resource, index)
            digest = hashlib.sha256(resource.data).hexdigest()
            prior = targets.get(parts)
            if prior is not None and prior.digest != digest:
                raise FormatError(f"PE resources map to the same output path: {'/'.join(parts)}")
            kinds[parts] = "file"
    all_files = set(kinds)
    for parts in all_files:
        for length in range(1, len(parts)):
            if parts[:length] in all_files:
                raise FormatError(f"output file/directory conflict at {'/'.join(parts[:length])}")
    return Installer(source, data, pe, containers, padding)


def _safe_target(root: Path, parts: Iterable[str]) -> Path:
    target = root.joinpath(*parts)
    root_resolved = root.resolve(strict=False)
    target_resolved = target.resolve(strict=False)
    try:
        common = os.path.commonpath((str(root_resolved), str(target_resolved)))
    except ValueError as exc:
        raise FormatError(f"output path escapes destination: {target}") from exc
    if common != str(root_resolved):
        raise FormatError(f"output path escapes destination: {target}")
    return target


def _filetime_seconds(value: int) -> float | None:
    if not value:
        return None
    return value / 10_000_000 - 11_644_473_600


def _manifest(installer: Installer, installed_count: int, metadata_count: int) -> dict[str, object]:
    return {
        "format": "INTENIUM stgc installer",
        "input": installer.source.name,
        "input_size": len(installer.data),
        "input_sha256": hashlib.sha256(installer.data).hexdigest(),
        "pe_image_end": installer.pe.image_end,
        "certificate_offset": installer.pe.certificate_offset,
        "certificate_size": installer.pe.certificate_size,
        "certificate_count": installer.pe.certificate_count,
        "stgc_container_count": len(installer.containers),
        "installed_file_count": installed_count,
        "package_metadata_file_count": metadata_count,
        "pe_resource_count": len(installer.pe.resources),
        "containers": [
            {
                "index": container.index,
                "offset": container.file_offset,
                "size": container.size,
                "checksum": f"{container.checksum:08x}",
                "filetime": container.timestamp,
                "kind": container.kind,
                "identifier": container.identifier,
                "files": [
                    {
                        "archive_path": "/".join(entry.archive_parts),
                        "output_path": "/".join(entry.output_parts) if entry.output_parts else None,
                        "original_size": entry.original_size,
                        "stored_size": entry.stored_size,
                        "filetime": entry.timestamp,
                        "sha256": entry.digest,
                    }
                    for entry in container.files
                ],
            }
            for container in installer.containers
        ],
    }


def extract(installer: Installer, output: Path, include_all: bool) -> tuple[int, int]:
    planned: dict[tuple[str, ...], tuple[Container, Entry]] = {}
    metadata_count = 0
    for container in installer.containers:
        for entry in container.files:
            if entry.output_parts is None:
                continue
            if entry.archive_parts[0] == "~Info":
                metadata_count += 1
            planned.setdefault(entry.output_parts, (container, entry))

    # Check existing filesystem objects before making any changes.
    for parts in planned:
        target = _safe_target(output, parts)
        probe = target.parent
        while probe != output.parent and probe != output:
            if probe.exists() and not probe.is_dir():
                raise FormatError(f"output parent is not a directory: {probe}")
            probe = probe.parent
        if target.is_symlink() or (target.exists() and not target.is_file()):
            raise FormatError(f"output target is not a regular file: {target}")
    if include_all:
        for index, resource in enumerate(installer.pe.resources):
            target = _safe_target(output, _resource_output(resource, index))
            if target.is_symlink() or (target.exists() and not target.is_file()):
                raise FormatError(f"output target is not a regular file: {target}")

    output.mkdir(parents=True, exist_ok=True)
    for parts, (container, entry) in planned.items():
        target = _safe_target(output, parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("wb") as stream:
            digest = _process_entry(installer.data, container.file_offset, entry, stream)
        if digest != entry.digest:
            raise FormatError(f"internal digest mismatch while writing {target}")
        timestamp = _filetime_seconds(entry.timestamp)
        if timestamp is not None:
            try:
                os.utime(target, (timestamp, timestamp))
            except (OSError, OverflowError):
                pass

    if include_all:
        for index, resource in enumerate(installer.pe.resources):
            target = _safe_target(output, _resource_output(resource, index))
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(resource.data)
        manifest_path = output / "_intenium" / "manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        installed_count = sum(1 for parts in planned if parts[0] != "_intenium")
        manifest_path.write_text(
            json.dumps(_manifest(installer, installed_count, metadata_count), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    installed_count = sum(1 for parts in planned if parts[0] != "_intenium")
    return installed_count, metadata_count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract installed files from an INTENIUM stgc installer"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="also extract package metadata, PE resources, and generate _intenium/manifest.json",
    )
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputDir", type=Path)
    args = parser.parse_args(argv)
    try:
        installer = parse_installer(args.inputFile, args.all)
        installed, metadata = extract(installer, args.outputDir, args.all)
    except FormatError as exc:
        print(f"intenium.py: error: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"intenium.py: filesystem error: {exc}", file=sys.stderr)
        return 1
    extra = ""
    if args.all:
        extra = f", {metadata} package-metadata files, {len(installer.pe.resources)} PE resources"
    print(
        f"Extracted {installed} installed files from {len(installer.containers)} stgc containers{extra}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

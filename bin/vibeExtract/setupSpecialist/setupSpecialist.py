#!/usr/bin/env python3
# Vibe coded by Codex
"""Extract TG Byte Software Setup Specialist self-extracting installers."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import struct
import sys
import zlib
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Iterable, Optional


TGCF = b"TGCF"
SUPPORTED_ARCHIVE_VERSIONS = {0x0130, 0x0140, 0x0150}
SUPPORTED_ENTRY_KINDS = {0x033A, 0x033C, 0x0048}
MAIN_ARCHIVE_KIND = 0x0024
BOOTSTRAP_ARCHIVE_KIND = 0x0022
REQUIRED_READER = 0x0130


class UnsupportedFormat(Exception):
    """The input is not a supported Setup Specialist installer."""


@dataclass
class ArchiveHeader:
    offset: int
    end: int
    kind: int
    made_by: int
    required: int
    flags: int
    reserved: int
    platform: int
    created: int
    modified: int
    volume: int
    reserved2: int
    name: bytes
    stored_crc: int
    crc_mode: str
    trailer_offset: Optional[int] = None
    boundary: Optional[int] = None


@dataclass
class EntryHeader:
    offset: int
    data_offset: int
    kind: int
    made_by: int
    required: int
    flags: int
    record_flags: int
    method: int
    reserved: int
    modified: int
    stored_size: int
    original_size: int
    data_crc: int
    attributes: int
    extra: Optional[int]
    canonical_name: bytes
    original_name: bytes
    comment: bytes
    stored_header_crc: int


@dataclass
class Entry:
    archive_index: int
    index: int
    header: EntryHeader
    raw: bytes
    quality: str
    crc_ok: bool
    size_ok: bool
    stream_complete: bool
    physical_complete: bool
    issue: str = ""
    stored: bytes = b""
    fragments: list[dict] = field(default_factory=list)


@dataclass
class Archive:
    header: ArchiveHeader
    entries: list[Entry] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class ContinuationVolume:
    path: Path
    data: bytes
    archive: Archive


@dataclass
class FileRecord:
    offset: int
    source: bytes
    flags: int
    destination: bytes


@dataclass
class ExtractionResult:
    input_file: str
    input_size: int
    output_dir: str
    recognized: bool = True
    archive_version: str = ""
    archive_crc_mode: str = ""
    package_name: str = ""
    wrapper: str = ""
    sha256: str = ""
    continuation_files: int = 0
    continuation_bytes: int = 0
    archive_count: int = 0
    archive_entries: int = 0
    complete_entries: int = 0
    partial_entries: int = 0
    damaged_entries: int = 0
    unreadable_entries: int = 0
    internal_entries: int = 0
    installed_actions: int = 0
    files_written: int = 0
    bytes_written: int = 0
    output_files: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    manifest: dict = field(default_factory=dict)

    @property
    def status(self) -> str:
        if self.partial_entries or self.damaged_entries or self.unreadable_entries or self.warnings:
            return "partial"
        return "complete"


def _crc(data: bytes, mode: str) -> int:
    if mode == "standard":
        return zlib.crc32(data) & 0xFFFFFFFF
    if mode == "legacy":
        return (zlib.crc32(data, 0xFFFFFFFF) ^ 0xFFFFFFFF) & 0xFFFFFFFF
    raise ValueError(f"unknown CRC mode {mode!r}")


def _matching_crc_mode(data: bytes, stored: int) -> Optional[str]:
    if _crc(data, "standard") == stored:
        return "standard"
    if _crc(data, "legacy") == stored:
        return "legacy"
    return None


def _decode_name(value: bytes) -> str:
    return value.decode("cp1252", errors="replace")


def _version(value: int) -> str:
    return f"{(value >> 8) & 0xF}.{(value >> 4) & 0xF}{value & 0xF}"


def _validate_ne_bootstrap(data: bytes) -> dict:
    if len(data) < 0x40 or data[:2] != b"MZ":
        raise UnsupportedFormat("not an MZ executable")
    ne_offset = struct.unpack_from("<I", data, 0x3C)[0]
    if ne_offset < 0x40 or ne_offset + 0x40 > len(data) or data[ne_offset : ne_offset + 2] != b"NE":
        raise UnsupportedFormat("MZ image does not contain a valid NE header")
    linker_version = data[ne_offset + 2]
    linker_revision = data[ne_offset + 3]
    resident_relative = struct.unpack_from("<H", data, ne_offset + 0x26)[0]
    resident = ne_offset + resident_relative
    if resident >= len(data):
        raise UnsupportedFormat("NE resident-name table is outside the input")
    name_length = data[resident]
    if resident + 1 + name_length + 2 > len(data):
        raise UnsupportedFormat("NE resident-name table is truncated")
    module_name = data[resident + 1 : resident + 1 + name_length]
    if module_name != b"SSPBOOT" or (linker_version, linker_revision) != (7, 1):
        raise UnsupportedFormat("NE program is not a Setup Specialist SSPBOOT module")
    return {
        "mz_offset": 0,
        "ne_offset": ne_offset,
        "linker_version": "7.01",
        "resident_module_name": "SSPBOOT",
    }


def _archive_crc_bytes(values: tuple, name: bytes) -> bytes:
    (
        magic,
        kind,
        made_by,
        required,
        flags,
        reserved,
        platform,
        created,
        modified,
        volume,
        reserved2,
        name_length,
    ) = values
    return b"".join(
        (
            magic,
            struct.pack("<HHH", kind, made_by, required),
            bytes((flags,)),
            struct.pack("<H", reserved),
            bytes((platform,)),
            struct.pack("<IIHHH", created, modified, volume, reserved2, name_length),
            name,
        )
    )


def _parse_archive_header(data: bytes, offset: int) -> Optional[ArchiveHeader]:
    if offset < 0 or offset + 32 > len(data) or data[offset : offset + 4] != TGCF:
        return None
    try:
        values = struct.unpack_from(">4sHHHBHBIIHHH", data, offset)
    except struct.error:
        return None
    (
        _magic,
        kind,
        made_by,
        required,
        flags,
        reserved,
        platform,
        created,
        modified,
        volume,
        reserved2,
        name_length,
    ) = values
    if kind not in (BOOTSTRAP_ARCHIVE_KIND, MAIN_ARCHIVE_KIND):
        return None
    if made_by not in SUPPORTED_ARCHIVE_VERSIONS or required != REQUIRED_READER:
        return None
    expected_flags = 1 if kind == BOOTSTRAP_ARCHIVE_KIND else 3
    if flags != expected_flags or reserved != 0 or platform != 2 or volume < 1 or reserved2 != 0:
        return None
    end_of_name = offset + 28 + name_length
    if end_of_name + 4 > len(data):
        return None
    name = data[offset + 28 : end_of_name]
    stored_crc = struct.unpack_from(">I", data, end_of_name)[0]
    crc_mode = _matching_crc_mode(_archive_crc_bytes(values, name), stored_crc)
    if crc_mode is None:
        return None
    return ArchiveHeader(
        offset=offset,
        end=end_of_name + 4,
        kind=kind,
        made_by=made_by,
        required=required,
        flags=flags,
        reserved=reserved,
        platform=platform,
        created=created,
        modified=modified,
        volume=volume,
        reserved2=reserved2,
        name=name,
        stored_crc=stored_crc,
        crc_mode=crc_mode,
    )


def _scan_archive_headers(data: bytes) -> list[ArchiveHeader]:
    headers: list[ArchiveHeader] = []
    position = 0
    while True:
        position = data.find(TGCF, position)
        if position < 0:
            break
        header = _parse_archive_header(data, position)
        if header is not None:
            headers.append(header)
        position += 1
    headers.sort(key=lambda item: item.offset)
    for index, header in enumerate(headers):
        search = header.end
        trailer = None
        while True:
            candidate = data.find(TGCF, search)
            if candidate < 0:
                break
            if candidate + 10 <= len(data):
                archive_length = int.from_bytes(data[candidate + 4 : candidate + 10], "big")
                if archive_length == candidate - header.offset:
                    trailer = candidate
                    break
            search = candidate + 1
        header.trailer_offset = trailer
        next_header = headers[index + 1].offset if index + 1 < len(headers) else len(data)
        header.boundary = trailer if trailer is not None else next_header
    return headers


def _read_cstring(data: bytes, position: int, limit: int) -> tuple[bytes, int]:
    if position >= limit:
        raise ValueError("missing NUL-terminated string")
    end = data.find(b"\0", position, limit)
    if end < 0:
        raise ValueError("unterminated string")
    return data[position:end], end + 1


def _entry_crc_bytes(values: tuple, extra: Optional[int], strings: Iterable[bytes]) -> bytes:
    (
        magic,
        kind,
        made_by,
        required,
        flags,
        record_flags,
        method,
        reserved,
        modified,
        stored_size,
        original_size,
        data_crc,
        attributes,
    ) = values
    parts = [
        magic,
        struct.pack("<HHH", kind, made_by, required),
        bytes((flags,)),
        struct.pack("<HH", record_flags, method),
        bytes((reserved,)),
        struct.pack("<IIIII", modified, stored_size, original_size, data_crc, attributes),
    ]
    if record_flags & 4:
        assert extra is not None
        parts.append(struct.pack("<I", extra))
    parts.extend(strings)
    return b"".join(parts)


def _parse_entry_header(
    data: bytes, offset: int, limit: int, archive: ArchiveHeader
) -> Optional[EntryHeader]:
    if offset + 36 > limit or data[offset : offset + 4] != TGCF:
        return None
    try:
        values = struct.unpack_from(">4sHHHBHHBIIIII", data, offset)
    except struct.error:
        return None
    (
        _magic,
        kind,
        made_by,
        required,
        flags,
        record_flags,
        method,
        reserved,
        modified,
        stored_size,
        original_size,
        data_crc,
        attributes,
    ) = values
    if kind not in SUPPORTED_ENTRY_KINDS:
        return None
    if made_by != archive.made_by or required != REQUIRED_READER or flags != archive.flags:
        return None
    if record_flags & ~0x0006 or method not in (0, 4) or reserved != 0:
        return None
    position = offset + 36
    extra = None
    if record_flags & 4:
        if position + 4 > limit:
            return None
        extra = struct.unpack_from(">I", data, position)[0]
        position += 4
    try:
        canonical_name, position = _read_cstring(data, position, limit)
        original_name, position = _read_cstring(data, position, limit)
        comment, position = _read_cstring(data, position, limit)
    except ValueError:
        return None
    if position + 4 > limit:
        return None
    stored_header_crc = struct.unpack_from(">I", data, position)[0]
    position += 4
    logical = _entry_crc_bytes(values, extra, (canonical_name, original_name, comment))
    if _crc(logical, archive.crc_mode) != stored_header_crc:
        return None
    return EntryHeader(
        offset=offset,
        data_offset=position,
        kind=kind,
        made_by=made_by,
        required=required,
        flags=flags,
        record_flags=record_flags,
        method=method,
        reserved=reserved,
        modified=modified,
        stored_size=stored_size,
        original_size=original_size,
        data_crc=data_crc,
        attributes=attributes,
        extra=extra,
        canonical_name=canonical_name,
        original_name=original_name,
        comment=comment,
        stored_header_crc=stored_header_crc,
    )


def _find_next_entry_header(
    data: bytes, start: int, limit: int, archive: ArchiveHeader
) -> Optional[EntryHeader]:
    position = start
    while True:
        position = data.find(TGCF, position, limit)
        if position < 0:
            return None
        header = _parse_entry_header(data, position, limit, archive)
        if header is not None:
            return header
        position += 1


def _inflate_salvage(payload: bytes) -> tuple[bytes, bool, str]:
    inflater = zlib.decompressobj()
    output: list[bytes] = []
    issue = ""
    for start in range(0, len(payload), 65536):
        try:
            output.append(inflater.decompress(payload[start : start + 65536]))
        except zlib.error as error:
            issue = str(error)
            break
    else:
        try:
            output.append(inflater.flush())
        except zlib.error as error:
            issue = str(error)
    return b"".join(output), inflater.eof, issue


def _decode_entry_payload(
    entry_header: EntryHeader,
    payload: bytes,
    crc_mode: str,
    physical_complete: bool,
) -> tuple[bytes, str, bool, bool, bool, str]:
    issue = ""
    if entry_header.method == 0:
        raw = payload
        stream_complete = physical_complete and len(raw) == entry_header.original_size
    else:
        raw, stream_complete, issue = _inflate_salvage(payload)
    size_ok = len(raw) == entry_header.original_size
    crc_ok = _crc(raw, crc_mode) == entry_header.data_crc
    if physical_complete and stream_complete and size_ok and crc_ok:
        quality = "complete"
    elif not physical_complete or not stream_complete or (entry_header.record_flags & 2):
        quality = "partial"
    else:
        quality = "damaged"
    if not issue and quality != "complete":
        reasons = []
        if not physical_complete:
            reasons.append("stored data is truncated")
        if entry_header.method == 4 and not stream_complete:
            reasons.append("DEFLATE stream does not reach its end")
        if not size_ok:
            reasons.append(f"expanded size is {len(raw)}, expected {entry_header.original_size}")
        if not crc_ok:
            reasons.append("expanded-data CRC does not match")
        if entry_header.record_flags & 2:
            reasons.append("record crosses a volume boundary")
        issue = "; ".join(reasons)
    return raw, quality, crc_ok, size_ok, stream_complete, issue


def _parse_archive(data: bytes, archive_index: int, header: ArchiveHeader) -> Archive:
    assert header.boundary is not None
    limit = header.boundary
    archive = Archive(header=header)
    position = header.end
    entry_index = 0
    while position < limit:
        entry_header = _parse_entry_header(data, position, limit, header)
        if entry_header is None:
            recovered = _find_next_entry_header(data, position + 1, limit, header)
            if recovered is None:
                archive.warnings.append(
                    f"archive {archive_index}: {limit - position} unparseable byte(s) at offset {position}"
                )
                break
            archive.warnings.append(
                f"archive {archive_index}: skipped {recovered.offset - position} damaged byte(s) "
                f"before a checksummed record at offset {recovered.offset}"
            )
            entry_header = recovered
        available_end = min(entry_header.data_offset + entry_header.stored_size, limit)
        payload = data[entry_header.data_offset:available_end]
        physical_complete = len(payload) == entry_header.stored_size
        raw, quality, crc_ok, size_ok, stream_complete, issue = _decode_entry_payload(
            entry_header, payload, header.crc_mode, physical_complete
        )
        archive.entries.append(
            Entry(
                archive_index=archive_index,
                index=entry_index,
                header=entry_header,
                raw=raw,
                quality=quality,
                crc_ok=crc_ok,
                size_ok=size_ok,
                stream_complete=stream_complete,
                physical_complete=physical_complete,
                issue=issue,
                stored=payload,
                fragments=[
                    {
                        "volume": header.volume,
                        "header_offset": entry_header.offset,
                        "data_offset": entry_header.data_offset,
                        "stored_size": len(payload),
                        "declared_stored_size": entry_header.stored_size,
                        "header_data_crc": f"0x{entry_header.data_crc:08x}",
                    }
                ],
            )
        )
        entry_index += 1
        declared_end = entry_header.data_offset + entry_header.stored_size
        if declared_end > limit:
            break
        position = declared_end
    if header.trailer_offset is None:
        archive.warnings.append(f"archive {archive_index}: package trailer is absent")
    return archive


def _decode_jn_string(data: bytes, position: int) -> tuple[bytes, int]:
    if position >= len(data):
        raise ValueError("missing string length")
    length = data[position]
    position += 1
    if length == 0xFF:
        if position + 2 > len(data):
            raise ValueError("missing 16-bit string length")
        length = struct.unpack_from("<H", data, position)[0]
        position += 2
        if length == 0xFFFF:
            if position + 4 > len(data):
                raise ValueError("missing 32-bit string length")
            length = struct.unpack_from("<I", data, position)[0]
            position += 4
    end = position + length
    if end >= len(data) or data[end] != 0:
        raise ValueError("serialized string is truncated or lacks its terminator")
    return data[position:end], end + 1


def _valid_destination(value: bytes) -> bool:
    if not value:
        return True
    if value.startswith(b"%"):
        return True
    if len(value) >= 2 and value[1:2] == b":" and chr(value[0]).isalpha():
        return len(value) == 2 or value[2:3] in (b"\\", b"/")
    return value.startswith((b"\\\\", b"//"))


def _project_file_records(data: bytes) -> list[FileRecord]:
    if not data.startswith(b"TGJN"):
        return []
    records: list[FileRecord] = []
    # Type 0x02 is the TGJN file-record tag. Its source string starts at the
    # following byte, followed by a 32-bit LE flags value and destination string.
    for position in range(1, len(data)):
        if data[position - 1] != 0x02:
            continue
        try:
            source, after_source = _decode_jn_string(data, position)
            if not source or after_source + 4 >= len(data):
                continue
            flags = struct.unpack_from("<I", data, after_source)[0]
            destination, _after_destination = _decode_jn_string(data, after_source + 4)
        except (ValueError, struct.error):
            continue
        if _valid_destination(destination):
            records.append(FileRecord(position - 1, source, flags, destination))
    return records


def _windows_basename(value: bytes) -> bytes:
    return value.replace(b"/", b"\\").rsplit(b"\\", 1)[-1]


def _destinations_for(source: bytes, records: list[FileRecord]) -> list[bytes]:
    folded = source.lower()
    exact = [record for record in records if record.source.lower() == folded]
    matches = exact
    if not matches:
        basename = _windows_basename(source).lower()
        matches = [
            record
            for record in records
            if _windows_basename(record.source).lower() == basename
        ]
    destinations: list[bytes] = []
    for record in matches:
        if record.destination not in destinations:
            destinations.append(record.destination)
    if any(destinations):
        destinations = [item for item in destinations if item]
    return destinations


_VARIABLE_COMPONENT = re.compile(r"^%([^%]+)%$", re.IGNORECASE)


def _safe_component(value: str) -> str:
    value = value.replace("\0", "_").strip()
    if value in ("", "."):
        return "_"
    if value == "..":
        return "__parent__"
    value = value.replace("/", "_").replace("\\", "_")
    return value or "_"


def _split_windows_path(value: bytes) -> tuple[Optional[str], list[str], bool]:
    text = _decode_name(value).replace("/", "\\")
    drive = None
    unc = text.startswith("\\\\")
    if len(text) >= 2 and text[1] == ":" and text[0].isalpha():
        drive = text[0].upper()
        text = text[2:]
    parts = [_safe_component(item) for item in text.split("\\") if item not in ("", ".")]
    return drive, parts, unc


def _source_relative(source: bytes) -> Path:
    drive, parts, unc = _split_windows_path(source)
    root: list[str] = ["SOURCE"]
    if drive:
        root.append(drive)
    elif unc:
        root.append("UNC")
    root.extend(parts or ["unnamed"])
    return Path(*root)


def _destination_relative(destination: bytes, source: bytes) -> Path:
    filename = _safe_component(_decode_name(_windows_basename(source)))
    if not destination:
        return Path("INSTALLDIR", filename)
    drive, parts, unc = _split_windows_path(destination)
    root: list[str] = []
    if drive:
        root.extend(("ABSOLUTE", drive))
    elif unc:
        root.extend(("UNC",))
    for component in parts:
        match = _VARIABLE_COMPONENT.match(component)
        if match:
            root.append(_safe_component(match.group(1).upper()))
        else:
            # A variable can form the first part of a longer component only in
            # malformed project data; preserve it literally rather than expand it.
            root.append(component.replace("%", ""))
    if not root:
        root.append("INSTALLDIR")
    root.append(filename)
    return Path(*root)


def _quality_path(path: Path, quality: str) -> Path:
    if quality == "partial":
        return path.with_name(path.name + ".partial")
    if quality == "damaged":
        return path.with_name(path.name + ".damaged")
    return path


def _tgpl_layout(data: bytes, headers: list[ArchiveHeader]) -> dict:
    first = headers[0]
    if first.kind != BOOTSTRAP_ARCHIVE_KIND or len(headers) < 2:
        return {"kind": "direct", "sspboot_end": first.offset}
    main = next(header for header in headers if header.kind == MAIN_ARCHIVE_KIND)
    if first.trailer_offset is None:
        raise ValueError("bootstrap package has no trailer")
    tgpl_offset = main.offset - 1024
    if tgpl_offset < first.trailer_offset + 10 or data[tgpl_offset : tgpl_offset + 4] != b"TGPL":
        raise ValueError("fixed 1024-byte TGPL table is absent before the main package")
    block = data[tgpl_offset : main.offset]
    total_files = struct.unpack_from("<I", block, 4)[0]
    position = 8
    volumes = []
    while position < len(block) and block[position] != 0:
        count = block[position]
        position += 1
        if count == 0xFF:
            if position + 2 > len(block):
                raise ValueError("TGPL extended file count is truncated")
            count = struct.unpack_from("<H", block, position)[0]
            position += 2
        if position >= len(block):
            raise ValueError("TGPL volume number is truncated")
        volume = block[position]
        position += 1
        volumes.append({"volume": volume, "file_count": count})
    if position >= len(block):
        raise ValueError("TGPL table lacks its zero terminator")
    position += 1
    if any(block[position:]):
        raise ValueError("TGPL reserved tail contains nonzero bytes")
    if sum(item["file_count"] for item in volumes) != total_files:
        raise ValueError("TGPL per-volume counts do not equal its total")
    if [item["volume"] for item in volumes] != list(range(1, len(volumes) + 1)):
        raise ValueError("TGPL volume numbers are not consecutive from one")
    gap_start = first.trailer_offset + 10
    layer_start = gap_start
    while layer_start < tgpl_offset and data[layer_start] == 0:
        layer_start += 1
    loader = None
    if layer_start < tgpl_offset:
        if data[layer_start : layer_start + 2] != b"MZ":
            raise ValueError("bytes before TGPL are neither padding nor an MZ loader")
        try:
            ne_offset = layer_start + struct.unpack_from("<I", data, layer_start + 0x3C)[0]
            if data[ne_offset : ne_offset + 2] != b"NE":
                raise ValueError
            resident_relative = struct.unpack_from("<H", data, ne_offset + 0x26)[0]
            resident = ne_offset + resident_relative
            name_length = data[resident]
            module_name = data[resident + 1 : resident + 1 + name_length]
        except (IndexError, struct.error, ValueError) as error:
            raise ValueError("Win32s loader has an invalid NE structure") from error
        if module_name != b"WN32SLDR":
            raise ValueError("intermediate NE module is not WN32SLDR")
        loader = {"offset": layer_start, "end": tgpl_offset, "size": tgpl_offset - layer_start}
    return {
        "kind": "bootstrap",
        "sspboot_end": first.offset,
        "bootstrap_package_offset": first.offset,
        "bootstrap_trailer_end": gap_start,
        "padding_offset": gap_start,
        "padding_end": layer_start,
        "padding_size": layer_start - gap_start,
        "win32s_loader": loader,
        "tgpl_offset": tgpl_offset,
        "tgpl_end": main.offset,
        "tgpl_size": 1024,
        "tgpl_total_files": total_files,
        "tgpl_volumes": volumes,
        "main_package_offset": main.offset,
    }


def _make_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    try:
        path.chmod(0o775)
    except OSError:
        pass


def _write_file(
    output_dir: Path,
    relative: Path,
    content: bytes,
    modified: int,
    written: dict[Path, bytes],
) -> tuple[Path, bool]:
    relative = Path(*(_safe_component(part) for part in relative.parts))
    target = output_dir / relative
    digest = hashlib.sha256(content).digest()
    if relative in written:
        if written[relative] == digest:
            return target, False
        number = 2
        while True:
            alternate = relative.with_name(f"{relative.name}.duplicate-{number}")
            if alternate not in written:
                relative = alternate
                target = output_dir / relative
                break
            number += 1
    _make_directory(target.parent)
    with target.open("wb") as handle:
        handle.write(content)
    target.chmod(0o664)
    try:
        os.utime(target, (modified, modified))
    except (OSError, OverflowError):
        pass
    written[relative] = digest
    return target, True


def _entry_manifest(entry: Entry) -> dict:
    header = entry.header
    return {
        "index": entry.index,
        "header_offset": header.offset,
        "data_offset": header.data_offset,
        "entry_kind": f"0x{header.kind:04x}",
        "record_flags": f"0x{header.record_flags:04x}",
        "compression_method": header.method,
        "stored_size": header.stored_size,
        "original_size": header.original_size,
        "data_crc": f"0x{header.data_crc:08x}",
        "attributes": f"0x{header.attributes:08x}",
        "extra": header.extra,
        "canonical_name": _decode_name(header.canonical_name),
        "original_name": _decode_name(header.original_name),
        "comment": _decode_name(header.comment),
        "quality": entry.quality,
        "crc_ok": entry.crc_ok,
        "size_ok": entry.size_ok,
        "stream_complete": entry.stream_complete,
        "physical_complete": entry.physical_complete,
        "recovered_size": len(entry.raw),
        "logical_stored_size": len(entry.stored),
        "fragments": entry.fragments,
        "issue": entry.issue,
    }


def _write_all_extras(
    data: bytes,
    output_dir: Path,
    headers: list[ArchiveHeader],
    archives: list[Archive],
    result: ExtractionResult,
    written: dict[Path, bytes],
) -> None:
    def write_extra(relative: Path, content: bytes, modified: int) -> None:
        target, created = _write_file(
            output_dir, relative, content, modified, written
        )
        if created:
            result.files_written += 1
            result.bytes_written += len(content)
            result.output_files.append(target.relative_to(output_dir).as_posix())

    first = headers[0]
    write_extra(
        Path("_setup_specialist/layers/sspboot-ne.exe"),
        data[: first.offset],
        first.modified,
    )
    if first.kind == BOOTSTRAP_ARCHIVE_KIND and len(headers) > 1:
        layout = _tgpl_layout(data, headers)
        padding_offset = layout["padding_offset"]
        padding_end = layout["padding_end"]
        if padding_end > padding_offset:
            write_extra(
                Path("_setup_specialist/layers/separator-padding.bin"),
                data[padding_offset:padding_end],
                first.modified,
            )
        loader = layout["win32s_loader"]
        if loader is not None:
            write_extra(
                Path("_setup_specialist/layers/win32s-loader.exe"),
                data[loader["offset"] : loader["end"]],
                first.modified,
            )
        write_extra(
            Path("_setup_specialist/layers/tgpl-volume-table.bin"),
            data[layout["tgpl_offset"] : layout["tgpl_end"]],
            first.modified,
        )
    for archive_index, archive in enumerate(archives):
        for entry in archive.entries:
            if archive.header.kind == MAIN_ARCHIVE_KIND:
                continue
            name = entry.header.original_name or entry.header.canonical_name or b"unnamed"
            relative = Path(
                "_setup_specialist",
                "bootstrap_archive",
                f"archive-{archive_index:02d}",
            ) / _source_relative(name).relative_to("SOURCE")
            relative = _quality_path(relative, entry.quality)
            if entry.raw or entry.header.original_size == 0:
                target, created = _write_file(
                    output_dir, relative, entry.raw, entry.header.modified, written
                )
                if created:
                    result.files_written += 1
                    result.bytes_written += len(entry.raw)
                    result.output_files.append(target.relative_to(output_dir).as_posix())


def inspect_installer(input_file: Path) -> tuple[bytes, dict, list[ArchiveHeader], list[Archive]]:
    try:
        data = input_file.read_bytes()
    except OSError:
        raise
    ne_info = _validate_ne_bootstrap(data)
    headers = _scan_archive_headers(data)
    main_headers = [item for item in headers if item.kind == MAIN_ARCHIVE_KIND]
    if not main_headers:
        raise UnsupportedFormat("SSPBOOT contains no checksummed Setup Specialist main archive")
    if headers[-1] is not main_headers[-1]:
        raise UnsupportedFormat("a checked non-main package follows the main archive")
    if main_headers[-1].volume != 1:
        raise UnsupportedFormat("self-extracting main package is not volume 1")
    archives = [_parse_archive(data, index, header) for index, header in enumerate(headers)]
    return data, ne_info, headers, archives


def _continuation_name(main_header: ArchiveHeader, volume: int) -> str:
    leaf = _decode_name(main_header.name).replace("\\", "/").rsplit("/", 1)[-1]
    stem = leaf.rsplit(".", 1)[0] if "." in leaf else leaf
    return f"{stem}.{volume}"


def _find_case_insensitive_sibling(directory: Path, expected_name: str) -> tuple[Optional[Path], str]:
    try:
        matches = [
            item
            for item in directory.iterdir()
            if item.is_file() and item.name.casefold() == expected_name.casefold()
        ]
    except OSError as error:
        return None, f"cannot list continuation directory: {error}"
    if not matches:
        return None, ""
    if len(matches) > 1:
        names = ", ".join(sorted(item.name for item in matches))
        return None, f"ambiguous case-insensitive continuation name {expected_name}: {names}"
    return matches[0], ""


def _read_continuation_volume(
    path: Path,
    expected_name: str,
    expected_volume: int,
    main_header: ArchiveHeader,
    archive_index: int,
) -> ContinuationVolume:
    data = path.read_bytes()
    headers = _scan_archive_headers(data)
    if not headers or headers[0].offset != 0:
        raise ValueError("file does not begin with a checksummed TGCF package header")
    header = headers[0]
    if header.kind != MAIN_ARCHIVE_KIND:
        raise ValueError("package is not a main/continuation archive")
    if header.volume != expected_volume:
        raise ValueError(f"header says volume {header.volume}, expected {expected_volume}")
    if _decode_name(header.name).casefold() != expected_name.casefold():
        raise ValueError(
            f"header name {_decode_name(header.name)!r} does not match {expected_name!r}"
        )
    if path.name.casefold() != expected_name.casefold():
        raise ValueError(f"filesystem name {path.name!r} does not match {expected_name!r}")
    if (
        header.made_by != main_header.made_by
        or header.required != main_header.required
        or header.flags != main_header.flags
        or header.platform != main_header.platform
        or header.crc_mode != main_header.crc_mode
    ):
        raise ValueError("package format fields do not match volume 1")
    archive = _parse_archive(data, archive_index, header)
    if header.trailer_offset is not None and header.trailer_offset + 10 != len(data):
        archive.warnings.append(
            f"volume {expected_volume}: {len(data) - header.trailer_offset - 10} trailing byte(s) "
            "follow the package trailer"
        )
    return ContinuationVolume(path=path, data=data, archive=archive)


def _fragment_headers_match(first: EntryHeader, continuation: EntryHeader) -> bool:
    return (
        bool(first.record_flags & 2)
        and bool(continuation.record_flags & 2)
        and first.kind == continuation.kind
        and first.made_by == continuation.made_by
        and first.required == continuation.required
        and first.flags == continuation.flags
        and first.method == continuation.method
        and first.reserved == continuation.reserved
        and first.modified == continuation.modified
        and first.original_size == continuation.original_size
        and first.attributes == continuation.attributes
        and first.extra == continuation.extra
        and first.canonical_name == continuation.canonical_name
        and first.original_name == continuation.original_name
        and first.comment == continuation.comment
    )


def _merge_fragment(first: Entry, continuation: Entry, crc_mode: str) -> Entry:
    stored = first.stored + continuation.stored
    logical_header = replace(
        first.header,
        stored_size=len(stored),
        data_crc=continuation.header.data_crc,
    )
    physical_complete = first.physical_complete and continuation.physical_complete
    raw, quality, crc_ok, size_ok, stream_complete, issue = _decode_entry_payload(
        logical_header, stored, crc_mode, physical_complete
    )
    if quality == "complete":
        issue = ""
    return Entry(
        archive_index=first.archive_index,
        index=first.index,
        header=logical_header,
        raw=raw,
        quality=quality,
        crc_ok=crc_ok,
        size_ok=size_ok,
        stream_complete=stream_complete,
        physical_complete=physical_complete,
        issue=issue,
        stored=stored,
        fragments=first.fragments + continuation.fragments,
    )


def _load_continuations(
    input_file: Path,
    main_header: ArchiveHeader,
    main_archive: Archive,
    first_archive_index: int,
) -> tuple[list[Entry], list[ContinuationVolume], list[str]]:
    logical_entries = list(main_archive.entries)
    volumes: list[ContinuationVolume] = []
    warnings: list[str] = []
    expected_volume = 2
    while (
        logical_entries
        and logical_entries[-1].quality == "partial"
        and (logical_entries[-1].header.record_flags & 2)
    ):
        expected_name = _continuation_name(main_header, expected_volume)
        path, discovery_error = _find_case_insensitive_sibling(input_file.parent, expected_name)
        if discovery_error:
            warnings.append(discovery_error)
            break
        if path is None:
            warnings.append(
                f"continuation volume {expected_volume} ({expected_name}) was not found beside the input"
            )
            break
        try:
            volume = _read_continuation_volume(
                path,
                expected_name,
                expected_volume,
                main_header,
                first_archive_index + len(volumes),
            )
        except (OSError, ValueError) as error:
            warnings.append(f"continuation {path.name} was ignored: {error}")
            break
        if not volume.archive.entries:
            warnings.append(f"continuation {path.name} contains no checked member records")
            break
        continuation = volume.archive.entries[0]
        if not _fragment_headers_match(logical_entries[-1].header, continuation.header):
            wanted = _decode_name(logical_entries[-1].header.original_name)
            found = _decode_name(continuation.header.original_name)
            warnings.append(
                f"continuation {path.name} starts with {found!r}, not the pending member {wanted!r}"
            )
            break
        logical_entries[-1] = _merge_fragment(
            logical_entries[-1], continuation, main_header.crc_mode
        )
        logical_entries.extend(volume.archive.entries[1:])
        volumes.append(volume)
        expected_volume += 1
    return logical_entries, volumes, warnings


def extract_installer(input_file: Path, output_dir: Path, include_all: bool = False) -> ExtractionResult:
    data, ne_info, headers, archives = inspect_installer(input_file)
    main_header = next(header for header in reversed(headers) if header.kind == MAIN_ARCHIVE_KIND)
    main_archive = archives[headers.index(main_header)]
    logical_entries, continuation_volumes, continuation_warnings = _load_continuations(
        input_file, main_header, main_archive, len(archives)
    )
    physical_archives = archives + [volume.archive for volume in continuation_volumes]
    wrapper_layout = _tgpl_layout(data, headers)
    if wrapper_layout["kind"] == "direct":
        wrapper_description = "SSPBOOT"
    elif wrapper_layout["win32s_loader"] is None:
        wrapper_description = "SSPBOOT + bootstrap package + TGPL"
    else:
        wrapper_description = "SSPBOOT + bootstrap package + WN32SLDR + TGPL"
    result = ExtractionResult(
        input_file=str(input_file),
        input_size=len(data),
        output_dir=str(output_dir),
        archive_version=_version(main_header.made_by),
        archive_crc_mode=main_header.crc_mode,
        package_name=_decode_name(main_header.name),
        wrapper=wrapper_description,
        sha256=hashlib.sha256(data).hexdigest(),
        continuation_files=len(continuation_volumes),
        continuation_bytes=sum(len(volume.data) for volume in continuation_volumes),
        archive_count=len(physical_archives),
        archive_entries=sum(len(archive.entries) for archive in physical_archives),
    )
    result.warnings.extend(continuation_warnings)
    for archive in archives:
        result.warnings.extend(archive.warnings)
        if archive.header.kind == MAIN_ARCHIVE_KIND:
            continue
        for entry in archive.entries:
            if entry.quality == "complete":
                result.complete_entries += 1
            elif entry.quality == "partial":
                result.partial_entries += 1
            else:
                result.damaged_entries += 1
            if entry.quality != "complete":
                name = entry.header.original_name or entry.header.canonical_name
                result.warnings.append(
                    f"bootstrap record {entry.index} ({_decode_name(name)}) is "
                    f"{entry.quality}: {entry.issue}"
                )
    for volume in continuation_volumes:
        result.warnings.extend(volume.archive.warnings)
    for entry in logical_entries:
        if entry.quality == "complete":
            result.complete_entries += 1
        elif entry.quality == "partial":
            result.partial_entries += 1
        else:
            result.damaged_entries += 1
    setup_index = None
    setup_entry = None
    for index, entry in enumerate(logical_entries):
        name = entry.header.original_name or entry.header.canonical_name
        if _windows_basename(name).upper() == b"SETUP.INF":
            setup_index = index
            setup_entry = entry
            break
    project_records: list[FileRecord] = []
    if setup_entry is not None and setup_entry.raw.startswith(b"TGJN"):
        project_records = _project_file_records(setup_entry.raw)
    elif setup_entry is None:
        result.warnings.append("main archive has no SETUP.INF project database")
    else:
        result.warnings.append("SETUP.INF could not be decoded as a complete TGJN project database")

    _make_directory(output_dir)
    written: dict[Path, bytes] = {}
    internal_dir = Path("_setup_specialist/internal")
    for index, entry in enumerate(logical_entries):
        header = entry.header
        name = header.original_name or header.canonical_name or b"unnamed"
        is_internal = setup_index is not None and index <= setup_index
        if is_internal:
            result.internal_entries += 1
            if not include_all:
                continue
            relative = internal_dir / _source_relative(name).relative_to("SOURCE")
            destinations = [relative]
        else:
            destinations_bytes = _destinations_for(name, project_records)
            if destinations_bytes:
                destinations = [
                    _destination_relative(destination, name)
                    for destination in destinations_bytes
                ]
            else:
                destinations = [_source_relative(name)]
        if not entry.raw and header.original_size != 0:
            result.unreadable_entries += 1
            result.warnings.append(
                f"record {index} ({_decode_name(name)}): no bytes could be recovered; {entry.issue}"
            )
            continue
        for relative in destinations:
            result.installed_actions += 1
            relative = _quality_path(relative, entry.quality)
            target, created = _write_file(
                output_dir, relative, entry.raw, header.modified, written
            )
            if created:
                result.files_written += 1
                result.bytes_written += len(entry.raw)
                result.output_files.append(target.relative_to(output_dir).as_posix())
        if entry.quality != "complete":
            result.warnings.append(
                f"record {index} ({_decode_name(name)}) extracted as {entry.quality}: {entry.issue}"
            )

    if include_all:
        _write_all_extras(data, output_dir, headers, archives, result, written)
        manifest_archives = []
        archive_sources = [(input_file, archive) for archive in archives]
        archive_sources.extend(
            (volume.path, volume.archive) for volume in continuation_volumes
        )
        for source_path, archive in archive_sources:
            header = archive.header
            manifest_archives.append(
                {
                    "source_file": str(source_path),
                    "offset": header.offset,
                    "header_end": header.end,
                    "kind": f"0x{header.kind:04x}",
                    "made_by": _version(header.made_by),
                    "required_reader": _version(header.required),
                    "flags": f"0x{header.flags:02x}",
                    "platform": header.platform,
                    "created": header.created,
                    "modified": header.modified,
                    "volume": header.volume,
                    "name": _decode_name(header.name),
                    "header_crc": f"0x{header.stored_crc:08x}",
                    "crc_mode": header.crc_mode,
                    "trailer_offset": header.trailer_offset,
                    "boundary": header.boundary,
                    "warnings": archive.warnings,
                    "entries": [_entry_manifest(entry) for entry in archive.entries],
                }
            )
        result.manifest = {
            "format": "TG Byte Software Setup Specialist self-extracting installer",
            "input": str(input_file),
            "input_size": len(data),
            "sha256": result.sha256,
            "input_files": [
                {
                    "path": str(input_file),
                    "volume": 1,
                    "size": len(data),
                    "sha256": result.sha256,
                }
            ]
            + [
                {
                    "path": str(volume.path),
                    "volume": volume.archive.header.volume,
                    "size": len(volume.data),
                    "sha256": hashlib.sha256(volume.data).hexdigest(),
                }
                for volume in continuation_volumes
            ],
            "ne_bootstrap": ne_info,
            "wrapper_layers": wrapper_layout,
            "archives": manifest_archives,
            "logical_entries": [_entry_manifest(entry) for entry in logical_entries],
            "extraction": {
                key: value
                for key, value in asdict(result).items()
                if key not in ("manifest",)
            },
        }
        manifest_content = (
            json.dumps(result.manifest, indent=2, ensure_ascii=False).encode("utf-8") + b"\n"
        )
        manifest_path, created = _write_file(
            output_dir,
            Path("_setup_specialist/manifest.json"),
            manifest_content,
            main_header.modified,
            written,
        )
        if created:
            result.files_written += 1
            result.bytes_written += len(manifest_content)
            result.output_files.append(manifest_path.relative_to(output_dir).as_posix())
    result.output_files.sort(key=str.lower)
    return result


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract a TG Byte Software Setup Specialist installer."
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="also extract installer internals/wrapper layers and generate a JSON manifest",
    )
    parser.add_argument("inputFile", type=Path, help="Setup Specialist installer executable")
    parser.add_argument("outputDir", type=Path, help="destination directory (may already exist)")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    args = _argument_parser().parse_args(argv)
    try:
        result = extract_installer(args.inputFile, args.outputDir, args.all)
    except UnsupportedFormat as error:
        print(f"setupSpecialist.py: unsupported input: {error}", file=sys.stderr)
        return 2
    except OSError as error:
        print(f"setupSpecialist.py: I/O error: {error}", file=sys.stderr)
        return 1
    print(
        f"Extracted {result.files_written} file(s), {result.bytes_written} byte(s) "
        f"from Setup Specialist {result.archive_version} using "
        f"{result.continuation_files} continuation volume(s) ({result.status})."
    )
    for warning in result.warnings:
        print(f"warning: {warning}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

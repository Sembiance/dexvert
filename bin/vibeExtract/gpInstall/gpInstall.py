#!/usr/bin/env python3
# Vibe coded by Codex
"""Extract payload files from a GP-Install 5 self-extracting installer."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime


OUTER_ARCHIVE_COUNT = 2
TCOMPRESS_HEADER_SIZE = 21
TCOMPRESS_FILE_HEADER_SIZE = 25
TCOMPRESS_MAGICS = {b"SPIS\x1aLH5", b"SPIS\x1aNON"}
MAX_FILE_SIZE = 8 * 1024 * 1024 * 1024
MAX_FILE_COUNT = 1_000_000


class FormatError(Exception):
    """The input is not a supported, intact GP-Install file."""


@dataclass(frozen=True)
class StoredFile:
    archive_index: int
    index: int
    name_bytes: bytes
    name: str
    dos_datetime: int
    attributes: int
    full_size: int
    compressed_size: int
    compression_method: int
    checksum: int
    locked: int
    data: memoryview


@dataclass(frozen=True)
class Archive:
    index: int
    framed_size: int
    method_id: bytes
    full_size_field: int
    archive_type: int
    checksum: int
    locked: int
    files: tuple[StoredFile, ...]


@dataclass(frozen=True)
class ParsedInstaller:
    input_size: int
    overlay_offset: int
    stub_sha256: str
    archives: tuple[Archive, ...]


@dataclass(frozen=True)
class SalvagedInstaller:
    input_size: int
    overlay_offset: int
    stub_sha256: str
    archives: tuple[Archive, ...]
    issues: tuple[str, ...]


def _u16(data: bytes | memoryview, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def _u32(data: bytes | memoryview, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def pe_overlay_offset(data: bytes) -> int:
    """Validate enough of the PE32 image to locate its exact overlay."""
    if len(data) < 0x40 or data[:2] != b"MZ":
        raise FormatError("missing DOS MZ header")
    pe_offset = _u32(data, 0x3C)
    if pe_offset > len(data) - 24 or data[pe_offset : pe_offset + 4] != b"PE\0\0":
        raise FormatError("missing or invalid PE signature")
    section_count = _u16(data, pe_offset + 6)
    optional_size = _u16(data, pe_offset + 20)
    if section_count == 0 or section_count > 96:
        raise FormatError("invalid PE section count")
    optional = pe_offset + 24
    sections = optional + optional_size
    if optional_size < 96 or sections > len(data):
        raise FormatError("truncated PE optional header")
    if _u16(data, optional) != 0x10B:
        raise FormatError("the GP-Install bootstrap must be PE32")
    section_table_end = sections + section_count * 40
    if section_table_end > len(data):
        raise FormatError("truncated PE section table")
    size_of_headers = _u32(data, optional + 60)
    if size_of_headers < section_table_end or size_of_headers > len(data):
        raise FormatError("invalid PE header size")

    overlay = size_of_headers
    ranges: list[tuple[int, int]] = []
    for index in range(section_count):
        section = sections + index * 40
        raw_size = _u32(data, section + 16)
        raw_offset = _u32(data, section + 20)
        if raw_size == 0:
            continue
        end = raw_offset + raw_size
        if raw_offset < size_of_headers or end < raw_offset or end > len(data):
            raise FormatError(f"invalid PE section {index} raw-data range")
        ranges.append((raw_offset, end))
        overlay = max(overlay, end)
    ranges.sort()
    for previous, current in zip(ranges, ranges[1:]):
        if current[0] < previous[1]:
            raise FormatError("overlapping PE section raw-data ranges")
    if overlay >= len(data):
        raise FormatError("PE image has no GP-Install overlay")
    return overlay


def _decode_stored_name(raw: bytes) -> str:
    if not raw or b"\0" in raw:
        raise FormatError("empty or NUL-containing stored filename")
    normalized = raw.replace(b"\\", b"/")
    if normalized.startswith(b"/") or len(normalized) >= 2 and normalized[1:2] == b":":
        raise FormatError(f"absolute stored filename is unsafe: {raw!r}")
    parts = normalized.split(b"/")
    if any(part in (b"", b".", b"..") for part in parts):
        raise FormatError(f"unsafe stored filename: {raw!r}")
    if any(any(byte < 32 for byte in part) for part in parts):
        raise FormatError(f"control character in stored filename: {raw!r}")
    # TCompress stores ANSI bytes but no code-page identifier.  fsdecode uses
    # surrogateescape on POSIX, preserving every original filename byte rather
    # than guessing the installer's locale.
    return "/".join(os.fsdecode(part) for part in parts)


def _parse_archive(
    data: bytes, archive_start: int, archive_size: int, archive_index: int
) -> Archive:
    archive_end = archive_start + archive_size
    if archive_size < TCOMPRESS_HEADER_SIZE or archive_end > len(data):
        raise FormatError(f"archive {archive_index} is truncated")
    method_id = data[archive_start : archive_start + 8]
    if method_id not in TCOMPRESS_MAGICS:
        raise FormatError(f"archive {archive_index} has no supported SPIS signature")

    full_size_field = _u32(data, archive_start + 8)
    archive_type = data[archive_start + 12]
    checksum = _u32(data, archive_start + 13)
    locked = _u32(data, archive_start + 17)
    if archive_type != 1:
        raise FormatError(f"archive {archive_index} is not a multi-file archive")
    if checksum != 0:
        raise FormatError(f"archive {archive_index} has a nonzero unused checksum")
    if locked != 0:
        raise FormatError(f"archive {archive_index} is locked or encrypted")

    position = archive_start + TCOMPRESS_HEADER_SIZE
    files: list[StoredFile] = []
    while position < archive_end:
        if len(files) >= MAX_FILE_COUNT:
            raise FormatError(f"archive {archive_index} has too many files")
        if archive_end - position < TCOMPRESS_FILE_HEADER_SIZE:
            raise FormatError(f"archive {archive_index} has a truncated file header")
        name_length = _u16(data, position)
        dos_datetime = _u32(data, position + 2)
        attributes = _u16(data, position + 6)
        full_size = _u32(data, position + 8)
        compressed_size = _u32(data, position + 12)
        method = data[position + 16]
        file_checksum = _u32(data, position + 17)
        file_locked = _u32(data, position + 21)
        position += TCOMPRESS_FILE_HEADER_SIZE

        if name_length == 0 or name_length > 255:
            raise FormatError(f"archive {archive_index} has an invalid filename length")
        if full_size > MAX_FILE_SIZE:
            raise FormatError(f"stored file is larger than the safety limit")
        if method not in (0, 4):
            raise FormatError(f"unsupported TCompress method {method}")
        if file_locked != 0:
            raise FormatError("locked or encrypted stored file is unsupported")
        if method == 0 and compressed_size != full_size:
            raise FormatError("literal stored file has unequal stored and original sizes")
        if method == 0 and file_checksum != 0:
            raise FormatError("literal stored file has a nonzero checksum")
        data_start = position + name_length
        data_end = data_start + compressed_size
        if data_start > archive_end or data_end > archive_end:
            raise FormatError(f"archive {archive_index} has a truncated stored file")
        name_bytes = data[position:data_start]
        name = _decode_stored_name(name_bytes)
        files.append(
            StoredFile(
                archive_index=archive_index,
                index=len(files),
                name_bytes=name_bytes,
                name=name,
                dos_datetime=dos_datetime,
                attributes=attributes,
                full_size=full_size,
                compressed_size=compressed_size,
                compression_method=method,
                checksum=file_checksum,
                locked=file_locked,
                data=memoryview(data)[data_start:data_end],
            )
        )
        position = data_end
    if position != archive_end:
        raise FormatError(f"archive {archive_index} does not end on a record boundary")
    return Archive(
        index=archive_index,
        framed_size=archive_size,
        method_id=method_id,
        full_size_field=full_size_field,
        archive_type=archive_type,
        checksum=checksum,
        locked=locked,
        files=tuple(files),
    )


def parse_installer(data: bytes) -> ParsedInstaller:
    overlay = pe_overlay_offset(data)
    position = overlay
    archives: list[Archive] = []
    for index in range(OUTER_ARCHIVE_COUNT):
        if len(data) - position < 4:
            raise FormatError(f"missing archive {index} length")
        archive_size = _u32(data, position)
        archive_start = position + 4
        archive_end = archive_start + archive_size
        if archive_end < archive_start or archive_end > len(data):
            raise FormatError(
                f"archive {index} length exceeds the input ({archive_size} bytes claimed)"
            )
        archives.append(_parse_archive(data, archive_start, archive_size, index))
        position = archive_end
    if position != len(data):
        raise FormatError(f"{len(data) - position} unexplained byte(s) follow archive 1")
    if not any(file.name.casefold() == "installer/gpinstall.exe" for file in archives[0].files):
        raise FormatError("bootstrap archive has no Installer/GPInstall.exe")
    return ParsedInstaller(
        input_size=len(data),
        overlay_offset=overlay,
        stub_sha256=hashlib.sha256(data[:overlay]).hexdigest(),
        archives=tuple(archives),
    )


def _parse_salvage_archive(
    data: bytes,
    archive_start: int,
    claimed_size: int,
    archive_index: int,
    issues: list[str],
) -> Archive:
    available_end = min(len(data), archive_start + claimed_size)
    if available_end - archive_start < TCOMPRESS_HEADER_SIZE:
        raise FormatError(f"archive {archive_index} has no complete TCompress header")
    method_id = data[archive_start : archive_start + 8]
    if method_id not in TCOMPRESS_MAGICS:
        raise FormatError(f"archive {archive_index} has no supported SPIS signature")
    full_size_field = _u32(data, archive_start + 8)
    archive_type = data[archive_start + 12]
    checksum = _u32(data, archive_start + 13)
    locked = _u32(data, archive_start + 17)
    if archive_type != 1 or checksum != 0 or locked != 0:
        raise FormatError(f"archive {archive_index} is not an unprotected multi-file archive")

    position = archive_start + TCOMPRESS_HEADER_SIZE
    files: list[StoredFile] = []
    while position < available_end:
        if available_end - position < TCOMPRESS_FILE_HEADER_SIZE:
            issues.append(
                f"archive {archive_index}: incomplete member header at file offset {position}"
            )
            break
        name_length = _u16(data, position)
        dos_datetime = _u32(data, position + 2)
        attributes = _u16(data, position + 6)
        full_size = _u32(data, position + 8)
        compressed_size = _u32(data, position + 12)
        method = data[position + 16]
        file_checksum = _u32(data, position + 17)
        file_locked = _u32(data, position + 21)
        header_position = position
        position += TCOMPRESS_FILE_HEADER_SIZE
        if name_length == 0 or name_length > 255:
            issues.append(f"archive {archive_index}: invalid member filename length")
            break
        if full_size > MAX_FILE_SIZE or method not in (0, 4) or file_locked != 0:
            issues.append(f"archive {archive_index}: unsupported or corrupt member header")
            break
        if method == 0 and (compressed_size != full_size or file_checksum != 0):
            issues.append(f"archive {archive_index}: invalid literal member header")
            break
        name_end = position + name_length
        data_end = name_end + compressed_size
        if name_end > available_end:
            issues.append(f"archive {archive_index}: truncated member filename")
            break
        name_bytes = data[position:name_end]
        name = _decode_stored_name(name_bytes)
        if data_end > available_end:
            available = max(0, available_end - name_end)
            issues.append(
                f"archive {archive_index}: {name!r} is incomplete "
                f"({available} of {compressed_size} stored bytes available)"
            )
            break
        files.append(
            StoredFile(
                archive_index=archive_index,
                index=len(files),
                name_bytes=name_bytes,
                name=name,
                dos_datetime=dos_datetime,
                attributes=attributes,
                full_size=full_size,
                compressed_size=compressed_size,
                compression_method=method,
                checksum=file_checksum,
                locked=file_locked,
                data=memoryview(data)[name_end:data_end],
            )
        )
        position = data_end
        if position <= header_position:
            raise FormatError("member parser made no progress")

    if archive_start + claimed_size > len(data):
        missing = archive_start + claimed_size - len(data)
        issues.append(f"archive {archive_index}: container is missing {missing} trailing byte(s)")
    return Archive(
        index=archive_index,
        framed_size=claimed_size,
        method_id=method_id,
        full_size_field=full_size_field,
        archive_type=archive_type,
        checksum=checksum,
        locked=locked,
        files=tuple(files),
    )


def parse_installer_salvage(data: bytes) -> SalvagedInstaller:
    """Parse only structurally reachable members; never scan for guessed boundaries."""
    overlay = pe_overlay_offset(data)
    position = overlay
    archives: list[Archive] = []
    issues: list[str] = []
    truncated_container = False
    for index in range(OUTER_ARCHIVE_COUNT):
        if len(data) - position < 4:
            issues.append(f"archive {index}: missing four-byte outer length")
            break
        claimed_size = _u32(data, position)
        archive_start = position + 4
        archive = _parse_salvage_archive(
            data, archive_start, claimed_size, index, issues
        )
        archives.append(archive)
        claimed_end = archive_start + claimed_size
        if claimed_end > len(data):
            truncated_container = True
            break
        position = claimed_end
    if not archives:
        raise FormatError("no GP-Install archive could be recovered")
    if not any(
        file.name.casefold() == "installer/gpinstall.exe"
        for file in archives[0].files
    ):
        raise FormatError("recoverable bootstrap has no Installer/GPInstall.exe")
    if len(archives) < OUTER_ARCHIVE_COUNT:
        issues.append("installed-payload archive is not structurally reachable")
    elif not truncated_container and position != len(data):
        issues.append(f"{len(data) - position} trailing byte(s) are not in a framed archive")
    return SalvagedInstaller(
        input_size=len(data),
        overlay_offset=overlay,
        stub_sha256=hashlib.sha256(data[:overlay]).hexdigest(),
        archives=tuple(archives),
        issues=tuple(issues),
    )


class BitReader:
    def __init__(self, data: memoryview):
        self.data = data
        self.position = 0
        self.byte_position = 0
        self.buffer = 0
        self.buffered_bits = 0

    def read(self, count: int) -> int:
        if count < 0 or self.position + count > len(self.data) * 8:
            raise FormatError("truncated LH5 bitstream")
        while self.buffered_bits < count:
            self.buffer = (self.buffer << 8) | self.data[self.byte_position]
            self.byte_position += 1
            self.buffered_bits += 8
        self.buffered_bits -= count
        value = (self.buffer >> self.buffered_bits) & ((1 << count) - 1)
        if self.buffered_bits:
            self.buffer &= (1 << self.buffered_bits) - 1
        else:
            self.buffer = 0
        self.position += count
        return value


class HuffmanTree:
    def __init__(self, lengths: list[int] | None = None, single: int | None = None):
        self.single = single
        self.codes: dict[tuple[int, int], int] = {}
        self.maximum_length = 0
        if single is not None:
            return
        if not lengths or not any(lengths):
            raise FormatError("empty LH5 Huffman tree")
        self.maximum_length = max(lengths)
        if self.maximum_length > 32:
            raise FormatError("invalid LH5 Huffman code length")
        counts = [0] * (self.maximum_length + 1)
        for length in lengths:
            if length:
                counts[length] += 1
        next_codes = [0] * (self.maximum_length + 1)
        code = 0
        for length in range(1, self.maximum_length + 1):
            code = (code + counts[length - 1]) << 1
            next_codes[length] = code
        if code + counts[self.maximum_length] != 1 << self.maximum_length:
            raise FormatError("incomplete or oversubscribed LH5 Huffman tree")
        for symbol, length in enumerate(lengths):
            if length:
                key = (length, next_codes[length])
                if key in self.codes:
                    raise FormatError("duplicate LH5 Huffman code")
                self.codes[key] = symbol
                next_codes[length] += 1

    def decode(self, reader: BitReader) -> int:
        if self.single is not None:
            return self.single
        code = 0
        for length in range(1, self.maximum_length + 1):
            code = (code << 1) | reader.read(1)
            symbol = self.codes.get((length, code))
            if symbol is not None:
                return symbol
        raise FormatError("invalid LH5 Huffman code")


def _read_code_length(reader: BitReader) -> int:
    length = reader.read(3)
    if length == 7:
        while reader.read(1):
            length += 1
            if length > 32:
                raise FormatError("invalid extended LH5 code length")
    return length


def _read_temporary_tree(reader: BitReader) -> HuffmanTree:
    count = reader.read(5)
    if count == 0:
        return HuffmanTree(single=reader.read(5))
    lengths: list[int] = []
    index = 0
    while index < count:
        lengths.append(_read_code_length(reader))
        if index == 2:
            skipped = reader.read(2)
            lengths.extend([0] * skipped)
            index += skipped
        index += 1
    if len(lengths) != count:
        raise FormatError("invalid LH5 temporary-tree length run")
    return HuffmanTree(lengths)


def _read_code_tree(reader: BitReader, temporary: HuffmanTree) -> HuffmanTree:
    count = reader.read(9)
    if count == 0:
        symbol = reader.read(9)
        if symbol >= 510:
            raise FormatError("invalid LH5 single code symbol")
        return HuffmanTree(single=symbol)
    if count > 510:
        raise FormatError("too many LH5 code-tree symbols")
    lengths: list[int] = []
    while len(lengths) < count:
        code = temporary.decode(reader)
        if code == 0:
            skipped = 1
        elif code == 1:
            skipped = reader.read(4) + 3
        elif code == 2:
            skipped = reader.read(9) + 20
        else:
            lengths.append(code - 2)
            continue
        if len(lengths) + skipped > count:
            raise FormatError("LH5 code-length run exceeds its table")
        lengths.extend([0] * skipped)
    return HuffmanTree(lengths)


def _read_offset_tree(reader: BitReader) -> HuffmanTree:
    count = reader.read(4)
    if count == 0:
        symbol = reader.read(4)
        if symbol >= 14:
            raise FormatError("invalid LH5 single offset symbol")
        return HuffmanTree(single=symbol)
    if count > 15:
        raise FormatError("too many LH5 offset-tree symbols")
    return HuffmanTree([_read_code_length(reader) for _ in range(count)])


def decompress_lh5(data: memoryview, full_size: int) -> bytes:
    if full_size == 0:
        if len(data) != 0:
            raise FormatError("nonempty LH5 stream represents an empty file")
        return b""
    reader = BitReader(data)
    output = bytearray()
    history = bytearray(b" " * 16384)
    history_position = 0
    commands_remaining = 0

    while len(output) < full_size:
        if commands_remaining == 0:
            commands_remaining = reader.read(16)
            if commands_remaining == 0:
                raise FormatError("zero-length LH5 command block")
            temporary = _read_temporary_tree(reader)
            code_tree = _read_code_tree(reader, temporary)
            offset_tree = _read_offset_tree(reader)
        commands_remaining -= 1
        code = code_tree.decode(reader)
        if code < 256:
            output.append(code)
            history[history_position] = code
            history_position = (history_position + 1) & 0x3FFF
            continue
        copy_count = code - 256 + 3
        offset_bits = offset_tree.decode(reader)
        if offset_bits == 0:
            offset = 0
        elif offset_bits == 1:
            offset = 1
        else:
            offset = (1 << (offset_bits - 1)) + reader.read(offset_bits - 1)
        source = (history_position - offset - 1) & 0x3FFF
        if len(output) + copy_count > full_size:
            raise FormatError("LH5 copy command exceeds the declared original size")
        for index in range(copy_count):
            value = history[(source + index) & 0x3FFF]
            output.append(value)
            history[history_position] = value
            history_position = (history_position + 1) & 0x3FFF

    if commands_remaining != 0:
        raise FormatError("LH5 stream ends before its final command block")
    used_bytes = (reader.position + 7) // 8
    if used_bytes != len(data):
        raise FormatError(f"LH5 stream has {len(data) - used_bytes} unexplained trailing byte(s)")
    padding_bits = len(data) * 8 - reader.position
    if padding_bits and reader.read(padding_bits) != 0:
        raise FormatError("LH5 stream has nonzero terminal padding bits")
    return bytes(output)


def expand_stored_file(stored: StoredFile) -> bytes:
    if stored.compression_method == 0:
        expanded = bytes(stored.data)
    else:
        expanded = decompress_lh5(stored.data, stored.full_size)
        actual_checksum = sum(expanded) & 0xFFFFFFFF
        if actual_checksum != stored.checksum:
            raise FormatError(
                f"checksum mismatch for {stored.name!r}: "
                f"expected {stored.checksum:08x}, got {actual_checksum:08x}"
            )
    if len(expanded) != stored.full_size:
        raise FormatError(f"wrong expanded size for {stored.name!r}")
    return expanded


def _dos_timestamp(value: int) -> float | None:
    if value == 0:
        return None
    second = (value & 0x1F) * 2
    minute = (value >> 5) & 0x3F
    hour = (value >> 11) & 0x1F
    day = (value >> 16) & 0x1F
    month = (value >> 21) & 0x0F
    year = ((value >> 25) & 0x7F) + 1980
    try:
        return datetime(year, month, day, hour, minute, second).timestamp()
    except (ValueError, OverflowError, OSError) as exc:
        raise FormatError(f"invalid packed DOS timestamp 0x{value:08x}") from exc


def _preflight_destination(root: Path, relative_names: list[str]) -> None:
    if root.exists() and not root.is_dir():
        raise OSError(f"output path exists and is not a directory: {root}")
    seen: set[str] = set()
    for relative in relative_names:
        folded = relative.casefold()
        if folded in seen:
            raise OSError(f"output paths collide on Windows: {relative}")
        seen.add(folded)
        current = root
        for part in Path(relative).parts[:-1]:
            current /= part
            if current.is_symlink():
                raise OSError(f"refusing to traverse output symlink: {current}")
            if current.exists() and not current.is_dir():
                raise OSError(f"output parent is not a directory: {current}")
        target = root / relative
        if target.is_symlink() or target.exists() and target.is_dir():
            raise OSError(f"output file conflicts with existing path: {target}")


def _metadata(
    parsed: ParsedInstaller | SalvagedInstaller,
    source: Path,
    salvage_issues: tuple[str, ...] | None = None,
) -> dict[str, object]:
    metadata: dict[str, object] = {
        "format": "GP-Install 5 self-extracting installer",
        "source_name": source.name,
        "input_size": parsed.input_size,
        "pe_overlay_offset": parsed.overlay_offset,
        "stub_sha256": parsed.stub_sha256,
        "archives": [
            {
                "index": archive.index,
                "framed_size": archive.framed_size,
                "method_id": archive.method_id[5:].decode("ascii", errors="strict"),
                "full_size_field": archive.full_size_field,
                "archive_type": archive.archive_type,
                "checksum": archive.checksum,
                "locked": archive.locked,
                "files": [
                    {
                        "name": stored.name,
                        "dos_datetime": f"0x{stored.dos_datetime:08x}",
                        "attributes": f"0x{stored.attributes:04x}",
                        "full_size": stored.full_size,
                        "compressed_size": stored.compressed_size,
                        "compression_method": stored.compression_method,
                        "checksum": f"0x{stored.checksum:08x}",
                        "locked": stored.locked,
                    }
                    for stored in archive.files
                ],
            }
            for archive in parsed.archives
        ],
    }
    effective_issues = salvage_issues
    if effective_issues is None and isinstance(parsed, SalvagedInstaller):
        effective_issues = parsed.issues
    if effective_issues:
        metadata["recovered"] = True
        metadata["issues"] = list(effective_issues)
    return metadata


def extract(
    source: Path, output: Path, include_all: bool
) -> tuple[int, int, tuple[str, ...], int]:
    data = source.read_bytes()
    parsed: ParsedInstaller | SalvagedInstaller
    recovering_container = False
    try:
        parsed = parse_installer(data)
    except FormatError:
        parsed = parse_installer_salvage(data)
        recovering_container = True

    selected: list[tuple[StoredFile, str]] = []
    if len(parsed.archives) > 1:
        selected.extend((stored, stored.name) for stored in parsed.archives[1].files)
    if include_all or recovering_container:
        selected.extend(
            (stored, f"_gpinstall/bootstrap/{stored.name}")
            for stored in parsed.archives[0].files
        )

    issues = list(parsed.issues) if isinstance(parsed, SalvagedInstaller) else []
    recovered_installed: dict[str, StoredFile] = {}
    recovered_relative_names: list[str] = []
    recovered_paths: set[str] = set()
    with tempfile.TemporaryDirectory(prefix="gpInstall-") as temporary:
        stage = Path(temporary)
        selected_paths: dict[tuple[int, int], str] = {}
        canonical_paths: dict[str, str] = {}
        for stored, relative in selected:
            folded = relative.casefold()
            canonical = canonical_paths.setdefault(folded, relative)
            selected_paths[(stored.archive_index, stored.index)] = canonical
        # Expand every reachable member, even when normal mode omits bootstrap
        # output.  Only members whose bytes, checksum, boundaries, and padding
        # validate are staged; recognizable damage is reported and skipped.
        for archive in parsed.archives:
            for stored in archive.files:
                try:
                    expanded = expand_stored_file(stored)
                    timestamp = _dos_timestamp(stored.dos_datetime)
                except FormatError as exc:
                    issues.append(
                        f"archive {archive.index}: skipped {stored.name!r}: {exc}"
                    )
                    continue
                relative = selected_paths.get((stored.archive_index, stored.index))
                if relative is None:
                    continue
                folded = relative.casefold()
                if folded not in recovered_paths:
                    recovered_paths.add(folded)
                    recovered_relative_names.append(relative)
                if stored.archive_index == 1:
                    recovered_installed[folded] = stored
                target = stage / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(expanded)
                if timestamp is not None:
                    os.utime(target, (timestamp, timestamp))
                if stored.attributes & 0x01:
                    target.chmod(0o444)
                else:
                    target.chmod(0o664)

        if include_all:
            manifest = stage / "_gpinstall/manifest.json"
            manifest.parent.mkdir(parents=True, exist_ok=True)
            manifest.write_text(
                json.dumps(
                    _metadata(parsed, source, tuple(issues)),
                    indent=2,
                    ensure_ascii=True,
                )
                + "\n",
                encoding="utf-8",
            )
            manifest.chmod(0o664)

        relative_names = recovered_relative_names
        if include_all:
            relative_names.append("_gpinstall/manifest.json")
        _preflight_destination(output, relative_names)
        output.mkdir(parents=True, exist_ok=True)
        output.chmod(output.stat().st_mode | 0o050)
        for staged in sorted(stage.rglob("*")):
            relative = staged.relative_to(stage)
            destination = output / relative
            if staged.is_dir():
                destination.mkdir(exist_ok=True)
                destination.chmod(destination.stat().st_mode | 0o050)
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(staged, destination)
                mode = destination.stat().st_mode
                destination.chmod(mode | 0o040)

    return (
        len(recovered_installed),
        sum(stored.full_size for stored in recovered_installed.values()),
        tuple(issues),
        len(recovered_paths),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gpInstall.py",
        description="Extract installed payload files from a GP-Install 5 executable.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="also extract bootstrap resources and generate _gpinstall/manifest.json",
    )
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputDir", type=Path)
    args = parser.parse_args(argv)

    try:
        count, total, issues, recovered = extract(
            args.inputFile, args.outputDir, args.all
        )
    except (FormatError, OSError) as exc:
        print(f"gpInstall.py: {exc}", file=sys.stderr)
        return 1
    if issues:
        print(
            f"Recovered {recovered} complete member(s), including {count} installed "
            f"file(s) / {total} installed byte(s), to {args.outputDir}"
        )
        for issue in issues:
            print(f"gpInstall.py: warning: {issue}", file=sys.stderr)
    else:
        print(f"Extracted {count} installed file(s), {total} byte(s), to {args.outputDir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# Vibe coded by Codex
"""Strict extractor for the 1997 THEMEPAK self-extracting installer format."""

from __future__ import annotations

import argparse
import binascii
import hashlib
import json
import os
import stat
import struct
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import NoReturn


BLOCK_SIZE = 4096
STUB_SIZE = 0x2E00
STUB_NORMALIZED_SHA256 = (
    "dbc0cf967ac2936a2bb69082234d03c5b9b77d2d49a88c310538c9b60c84b585"
)
FILETIME_EPOCH_DELTA = 116_444_736_000_000_000


class FormatError(ValueError):
    """The input is not the supported THEMEPAK format."""


@dataclass(frozen=True)
class ContainerInfo:
    file_size: int
    payload_offset: int
    payload_size: int
    padding_size: int
    stored_crc32: int
    sha256: str


@dataclass(frozen=True)
class FileRecord:
    archive_name: str
    relative_path: PurePosixPath
    data: bytes
    creation_filetime: int
    modification_filetime: int
    first_block_offset: int
    block_count: int


class BitReader:
    def __init__(self, data: bytes):
        self.data = data
        self.bit_position = 12

    def read(self, width: int) -> int:
        end = self.bit_position + width
        if end > len(self.data) * 8:
            raise FormatError("compressed block exhausted its four-byte sentinel")
        value = 0
        for shift in range(width):
            bit = self.bit_position + shift
            value |= ((self.data[bit >> 3] >> (bit & 7)) & 1) << shift
        self.bit_position = end
        return value


class ThemeStream:
    """Stateful THEMEPAK block decoder.

    The original engine retains its 512-entry hash table and reuses one 4 KiB
    output buffer across blocks.  Those details are format-significant.
    """

    def __init__(self, payload: bytes):
        self.payload = payload
        self.offset = 0
        self.buffer = bytearray(BLOCK_SIZE)
        self.hash_table: list[int | None] = [None] * 512
        self.raw_blocks = 0
        self.repeat_blocks = 0
        self.compressed_blocks = 0

    @staticmethod
    def _hash_pair(buffer: bytearray, start: int) -> int:
        word = buffer[start] | (buffer[start + 1] << 8)
        return (word + (word >> 6)) & 0x1FF

    def _decompress(self, physical: bytes, stored_length: int) -> None:
        # The native decoder writes 0xffffffff immediately after each physical
        # block.  It is an implicit end marker, not four bytes from the file.
        bits = BitReader(physical + b"\xff\xff\xff\xff")
        output = 0
        pending_pair = True

        self.buffer[output] = bits.read(8)
        output += 1

        def require_space(length: int) -> None:
            if length < 0 or output + length > BLOCK_SIZE:
                raise FormatError("compressed token exceeds its 4 KiB block")

        def copy_hash_match(length: int) -> None:
            nonlocal output, pending_pair
            require_space(length)
            index = bits.read(9)
            source_pointer = self.hash_table[index]
            if source_pointer is None:
                raise FormatError("compressed token references an unset hash slot")

            self.hash_table[index] = output + 1
            boundary = output
            source = source_pointer - 1
            if source < 0 or source >= BLOCK_SIZE:
                raise FormatError("compressed token has an invalid source pointer")

            for _ in range(length):
                if source >= BLOCK_SIZE:
                    raise FormatError("compressed match source leaves the block buffer")
                self.buffer[output] = self.buffer[source]
                output += 1
                source += 1

            if pending_pair:
                self.hash_table[self._hash_pair(self.buffer, boundary - 1)] = boundary
            pending_pair = False

        while True:
            if bits.read(1) == 0:
                require_space(1)
                self.buffer[output] = bits.read(8)
                if pending_pair:
                    self.hash_table[self._hash_pair(self.buffer, output - 1)] = output
                output += 1
                pending_pair = True
                continue

            if bits.read(1) == 0:
                copy_hash_match(2)
                continue
            if bits.read(1) == 0:
                copy_hash_match(3)
                continue
            if bits.read(1) == 0:
                copy_hash_match(4 + bits.read(1))
                continue
            if bits.read(1) == 0:
                copy_hash_match(6)
                continue
            if bits.read(1) == 0:
                copy_hash_match(7 + bits.read(1))
                continue

            if bits.read(1) == 0:
                short_code = bits.read(2)
                if short_code:
                    copy_hash_match(8 + short_code)
                    continue

                pending_pair = False
                if bits.read(1) == 0:
                    run_length = 2 + bits.read(1)
                elif bits.read(1) == 0:
                    run_length = 4 + bits.read(5)
                else:
                    run_length = bits.read(12)

                if run_length < 2:
                    raise FormatError("repeat token length is smaller than two")
                require_space(run_length)
                repeated = self.buffer[output - 1]
                run_start = output
                self.buffer[output : output + run_length] = bytes([repeated]) * run_length
                output += run_length
                word = repeated | (repeated << 8)
                self.hash_table[(word + (word >> 6)) & 0x1FF] = run_start + 1
                continue

            if bits.read(1) == 0:
                copy_hash_match(12 + bits.read(3))
                continue
            if bits.read(1) == 0:
                copy_hash_match(20 + bits.read(4))
                continue

            long_code = bits.read(5)
            if long_code == 31:
                match_length = bits.read(12)
                if match_length == 0xFFF:
                    break
            else:
                match_length = 36 + long_code
            copy_hash_match(match_length)

        if output != BLOCK_SIZE:
            raise FormatError(
                f"compressed block expands to {output} bytes instead of {BLOCK_SIZE}"
            )
        if bits.bit_position > stored_length * 8 + 32:
            raise FormatError("compressed block reads beyond its implicit sentinel")

    def read_block(self) -> tuple[bytes, int, str]:
        start = self.offset
        if len(self.payload) - start < 2:
            raise FormatError("truncated block header")
        header = struct.unpack_from("<H", self.payload, start)[0]
        stored_length = header & 0x0FFF

        if header == 0:
            consumed = BLOCK_SIZE + 2
            end = start + consumed
            if end > len(self.payload):
                raise FormatError("truncated raw block")
            self.buffer[:] = self.payload[start + 2 : end]
            kind = "raw"
            self.raw_blocks += 1
        elif header == 1:
            consumed = 6
            end = start + consumed
            if end > len(self.payload):
                raise FormatError("truncated repeated-dword block")
            self.buffer[:] = self.payload[start + 2 : end] * 1024
            kind = "repeat-dword"
            self.repeat_blocks += 1
        else:
            consumed = stored_length
            end = start + consumed
            if end > len(self.payload):
                raise FormatError("truncated compressed block")
            self._decompress(self.payload[start:end], stored_length)
            kind = "compressed"
            self.compressed_blocks += 1

        self.offset = end
        return bytes(self.buffer), consumed, kind


def _u16(data: bytes, offset: int, description: str) -> int:
    if offset < 0 or offset + 2 > len(data):
        raise FormatError(f"truncated {description}")
    return struct.unpack_from("<H", data, offset)[0]


def _u32(data: bytes, offset: int, description: str) -> int:
    if offset < 0 or offset + 4 > len(data):
        raise FormatError(f"truncated {description}")
    return struct.unpack_from("<I", data, offset)[0]


def _normalize_archive_path(raw_name: bytes) -> tuple[str, PurePosixPath]:
    if not raw_name or b"\x00" in raw_name:
        raise FormatError("archive path is empty or contains NUL")
    try:
        archive_name = raw_name.decode("cp1252")
    except UnicodeDecodeError as error:
        raise FormatError("archive path is not a valid Windows ANSI name") from error

    normalized = archive_name.replace("\\", "/")
    components = normalized.split("/")
    path = PurePosixPath(normalized)
    if (
        normalized.startswith("/")
        or path.is_absolute()
        or any(part in ("", ".", "..") for part in components)
        or (path.parts and ":" in path.parts[0])
    ):
        raise FormatError(f"unsafe archive path: {archive_name!r}")
    return archive_name, path


def parse_container(data: bytes) -> tuple[ContainerInfo, list[FileRecord], ThemeStream]:
    if len(data) < STUB_SIZE + 4:
        raise FormatError("file is too short")

    stored_crc = _u32(data, len(data) - 4, "CRC-32 trailer")
    calculated_crc = binascii.crc32(data[:-4]) & 0xFFFFFFFF
    if stored_crc != calculated_crc:
        raise FormatError(
            f"CRC-32 mismatch (stored {stored_crc:08x}, calculated {calculated_crc:08x})"
        )

    if data[:2] != b"MZ":
        raise FormatError("missing DOS MZ signature")
    pe_offset = _u32(data, 0x3C, "DOS e_lfanew")
    if pe_offset + 24 > len(data) or data[pe_offset : pe_offset + 4] != b"PE\0\0":
        raise FormatError("missing PE signature")

    machine = _u16(data, pe_offset + 4, "COFF machine")
    section_count = _u16(data, pe_offset + 6, "COFF section count")
    optional_size = _u16(data, pe_offset + 20, "COFF optional-header size")
    optional_offset = pe_offset + 24
    if machine != 0x014C or section_count != 5 or optional_size != 0x00E0:
        raise FormatError("unsupported THEMEPAK installer-engine PE layout")
    if _u16(data, optional_offset, "PE optional magic") != 0x010B:
        raise FormatError("installer is not PE32")

    section_table = optional_offset + optional_size
    if section_table + section_count * 40 > len(data):
        raise FormatError("truncated PE section table")
    theme_header = section_table + (section_count - 1) * 40
    if data[theme_header : theme_header + 8].rstrip(b"\0") != b".theme":
        raise FormatError("last PE section is not .theme")

    virtual_size = _u32(data, theme_header + 8, ".theme virtual size")
    raw_size = _u32(data, theme_header + 16, ".theme raw size")
    raw_offset = _u32(data, theme_header + 20, ".theme raw offset")
    if raw_offset != STUB_SIZE or raw_size == 0 or raw_size % 0x200:
        raise FormatError("invalid .theme placement or file alignment")
    if raw_offset + raw_size != len(data):
        raise FormatError("bytes exist outside the final PE section")
    if virtual_size < 4 or virtual_size > raw_size:
        raise FormatError("invalid .theme meaningful length")
    if raw_size != ((virtual_size + 0x1FF) & ~0x1FF):
        raise FormatError(".theme raw size is not the aligned virtual size")

    expected_initialized = raw_size + 0x1E00
    if _u32(data, optional_offset + 8, "SizeOfInitializedData") != expected_initialized:
        raise FormatError("inconsistent PE initialized-data size")
    expected_image = (0x5000 + virtual_size + 0xFFF) & ~0xFFF
    if _u32(data, optional_offset + 56, "SizeOfImage") != expected_image:
        raise FormatError("inconsistent PE image size")

    normalized_stub = bytearray(data[:raw_offset])
    for offset in (
        optional_offset + 8,
        optional_offset + 56,
        theme_header + 8,
        theme_header + 16,
    ):
        normalized_stub[offset : offset + 4] = b"\0\0\0\0"
    if hashlib.sha256(normalized_stub).hexdigest() != STUB_NORMALIZED_SHA256:
        raise FormatError("unsupported THEMEPAK installer-engine build")

    payload_size = virtual_size - 4
    payload_end = raw_offset + payload_size
    trailer_offset = len(data) - 4
    if any(data[payload_end:trailer_offset]):
        raise FormatError("nonzero byte in .theme alignment padding")

    payload = data[raw_offset:payload_end]
    stream = ThemeStream(payload)
    records: list[FileRecord] = []
    seen_paths: set[str] = set()

    while stream.offset < len(payload):
        first_block_offset = stream.offset
        first, _, _ = stream.read_block()
        if len(first) < 24:
            raise FormatError("truncated file-record header")
        (
            file_size,
            creation_low,
            creation_high,
            modification_low,
            modification_high,
            name_length,
        ) = struct.unpack_from("<6I", first)

        if name_length == 0 or 24 + name_length >= BLOCK_SIZE:
            raise FormatError("invalid file-record path length")
        raw_name = first[24 : 24 + name_length]
        archive_name, relative_path = _normalize_archive_path(raw_name)
        collision_key = "/".join(relative_path.parts).casefold()
        if collision_key in seen_paths:
            raise FormatError(f"duplicate Windows archive path: {archive_name!r}")
        seen_paths.add(collision_key)

        content_start = 24 + name_length
        initial_count = min(file_size, BLOCK_SIZE - content_start)
        content = bytearray(first[content_start : content_start + initial_count])
        block_count = 1
        while len(content) < file_size:
            block, _, _ = stream.read_block()
            take = min(BLOCK_SIZE, file_size - len(content))
            content.extend(block[:take])
            block_count += 1

        records.append(
            FileRecord(
                archive_name=archive_name,
                relative_path=relative_path,
                data=bytes(content),
                creation_filetime=creation_low | (creation_high << 32),
                modification_filetime=modification_low | (modification_high << 32),
                first_block_offset=first_block_offset,
                block_count=block_count,
            )
        )

    if stream.offset != len(payload):
        raise FormatError("block stream does not end at the declared payload boundary")
    if not records:
        raise FormatError("archive contains no file records")

    info = ContainerInfo(
        file_size=len(data),
        payload_offset=raw_offset,
        payload_size=payload_size,
        padding_size=trailer_offset - payload_end,
        stored_crc32=stored_crc,
        sha256=hashlib.sha256(data).hexdigest(),
    )
    return info, records, stream


def _filetime_iso(filetime: int) -> str | None:
    try:
        timestamp = (filetime - FILETIME_EPOCH_DELTA) / 10_000_000
        return datetime.fromtimestamp(timestamp, timezone.utc).isoformat()
    except (OverflowError, OSError, ValueError):
        return None


def _safe_destination(root: Path, relative: PurePosixPath) -> Path:
    destination = root.joinpath(*relative.parts)
    current = root
    for part in relative.parts[:-1]:
        current /= part
        if current.is_symlink():
            raise OSError(f"refusing to traverse existing symlink: {current}")
    if destination.is_symlink():
        raise OSError(f"refusing to replace existing symlink: {destination}")
    return destination


def extract(
    input_path: Path,
    output_path: Path,
    info: ContainerInfo,
    records: list[FileRecord],
    stream: ThemeStream,
    include_metadata: bool,
) -> None:
    metadata_name = "themepak-metadata.json"
    if include_metadata and any(
        record.relative_path.as_posix().casefold() == metadata_name for record in records
    ):
        raise OSError(f"archive conflicts with generated {metadata_name}")

    # Check every destination before changing the output tree.  The archive has
    # already been fully decoded and validated at this point.
    if output_path.exists() and not output_path.is_dir():
        raise OSError(f"output path is not a directory: {output_path}")
    if output_path.is_symlink():
        raise OSError(f"refusing symlink output directory: {output_path}")
    for record in records:
        destination = _safe_destination(output_path, record.relative_path)
        current = output_path
        for part in record.relative_path.parts[:-1]:
            current /= part
            if current.exists() and not current.is_dir():
                raise OSError(f"archive directory conflicts with a file: {current}")
        if destination.exists() and destination.is_dir():
            raise OSError(f"archive file conflicts with a directory: {destination}")

    output_path.mkdir(parents=True, exist_ok=True)
    os.chmod(output_path, os.stat(output_path).st_mode | stat.S_IRGRP | stat.S_IXGRP)

    for record in records:
        destination = _safe_destination(output_path, record.relative_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        os.chmod(
            destination.parent,
            os.stat(destination.parent).st_mode | stat.S_IRGRP | stat.S_IXGRP,
        )
        temporary = destination.with_name(f".{destination.name}.themepak-tmp-{os.getpid()}")
        try:
            with temporary.open("xb") as handle:
                handle.write(record.data)
            os.chmod(temporary, 0o664)
            os.replace(temporary, destination)
            modification = (record.modification_filetime - FILETIME_EPOCH_DELTA) / 10_000_000
            os.utime(destination, (modification, modification))
        finally:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass

    if include_metadata:
        metadata_path = output_path / metadata_name
        manifest = {
            "format": "THEMEPAK Installer (1997 engine)",
            "source": str(input_path),
            "container": {
                "size": info.file_size,
                "sha256": info.sha256,
                "crc32": f"{info.stored_crc32:08x}",
                "payload_offset": info.payload_offset,
                "payload_size": info.payload_size,
                "alignment_padding_size": info.padding_size,
                "block_counts": {
                    "raw": stream.raw_blocks,
                    "repeat_dword": stream.repeat_blocks,
                    "compressed": stream.compressed_blocks,
                },
            },
            "files": [
                {
                    "path": record.relative_path.as_posix(),
                    "archive_name": record.archive_name,
                    "size": len(record.data),
                    "sha256": hashlib.sha256(record.data).hexdigest(),
                    "creation_filetime": record.creation_filetime,
                    "creation_time_utc": _filetime_iso(record.creation_filetime),
                    "modification_filetime": record.modification_filetime,
                    "modification_time_utc": _filetime_iso(record.modification_filetime),
                    "first_block_offset": record.first_block_offset,
                    "block_count": record.block_count,
                }
                for record in records
            ],
        }
        temporary = metadata_path.with_name(f".{metadata_name}.themepak-tmp-{os.getpid()}")
        try:
            with temporary.open("x", encoding="utf-8", newline="\n") as handle:
                json.dump(manifest, handle, indent=2, ensure_ascii=False)
                handle.write("\n")
            os.chmod(temporary, 0o664)
            os.replace(temporary, metadata_path)
        finally:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass


def fail(message: str) -> NoReturn:
    print(f"themepak.py: error: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract files installed by a supported THEMEPAK Installer executable."
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="also generate themepak-metadata.json with container and file metadata",
    )
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputDir", type=Path)
    arguments = parser.parse_args()

    try:
        data = arguments.inputFile.read_bytes()
        info, records, stream = parse_container(data)
    except (OSError, FormatError) as error:
        fail(str(error))

    try:
        extract(
            arguments.inputFile,
            arguments.outputDir,
            info,
            records,
            stream,
            arguments.all,
        )
    except OSError as error:
        fail(f"extraction failed: {error}")

    print(
        f"Extracted {len(records)} files from {arguments.inputFile} "
        f"to {arguments.outputDir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# Vibe coded by Codex
"""Strict extractor for the BitRock InstallBuilder bundles documented here."""

from __future__ import annotations

import argparse
import binascii
import hashlib
import json
import lzma
import mmap
import os
import re
import shutil
import stat
import struct
import sys
import tempfile
import zlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import BinaryIO, Iterable


BITROCK_TRAILER = b"bitrock-lzma-4.0mFC3acAOJrQinu5aEHu0uH7N5XSQ3Z14"
METAKIT_SCHEMA = b"dirs[name:S,parent:I,files[name:S,size:I,date:I,contents:B]]"
COOKFS_TRAILER = b"CFS0002"
COOKFS_INDEX_MAGIC = b"CFS2.200"
TCLKIT_LAUNCHER_PREFIX = (
    b'#!/bin/sh\n# \\\nexec tclkit "$0" ${1+"$@"}\n'
    b'package require starkit\nstarkit::header mk4 -readonly\n\x1a'
)
TCLKIT_LAUNCHER = TCLKIT_LAUNCHER_PREFIX + b"#" * (256 - len(TCLKIT_LAUNCHER_PREFIX))
BIG_FILE_RE = re.compile(r"^(.*)___bitrockBigFile([1-9][0-9]*)$")


class FormatError(Exception):
    """The input is not one of the fully supported BitRock formats."""


def fail(message: str) -> None:
    raise FormatError(message)


def read_exact(handle: BinaryIO, offset: int, size: int) -> bytes:
    if offset < 0 or size < 0:
        fail("negative file range")
    handle.seek(offset)
    data = handle.read(size)
    if len(data) != size:
        fail("truncated file")
    return data


def be32(data: bytes, offset: int = 0) -> int:
    return struct.unpack_from(">I", data, offset)[0]


@dataclass(frozen=True)
class Range:
    start: int
    end: int
    label: str


@dataclass
class PEInfo:
    end: int
    sections: int
    timestamp: int
    image_size: int
    certificate_offset: int
    certificate_size: int
    certificate_truncated: bool


def parse_pe(handle: BinaryIO, file_size: int) -> PEInfo:
    if file_size < 0x100 or read_exact(handle, 0, 2) != b"MZ":
        fail("not a PE executable")
    dos = read_exact(handle, 0, 0x40)
    pe_offset = struct.unpack_from("<I", dos, 0x3C)[0]
    if pe_offset < 0x40 or pe_offset + 24 > file_size:
        fail("invalid DOS PE pointer")
    coff = read_exact(handle, pe_offset, 24)
    if coff[:4] != b"PE\0\0":
        fail("missing PE signature")
    machine, section_count, timestamp = struct.unpack_from("<HHI", coff, 4)
    symbols_offset, symbol_count = struct.unpack_from("<II", coff, 12)
    optional_size = struct.unpack_from("<H", coff, 20)[0]
    if machine != 0x14C or not (1 <= section_count <= 96):
        fail("unsupported PE machine or section count")
    optional = read_exact(handle, pe_offset + 24, optional_size)
    if len(optional) < 96 or struct.unpack_from("<H", optional, 0)[0] != 0x10B:
        fail("only PE32 executables are supported")
    headers_size = struct.unpack_from("<I", optional, 60)[0]
    image_size = struct.unpack_from("<I", optional, 56)[0]
    if headers_size == 0 or headers_size > file_size:
        fail("invalid PE header size")
    section_table = pe_offset + 24 + optional_size
    if section_table + section_count * 40 > headers_size:
        fail("PE section table exceeds SizeOfHeaders")
    pe_end = headers_size
    for index in range(section_count):
        section = read_exact(handle, section_table + index * 40, 40)
        raw_size, raw_offset = struct.unpack_from("<II", section, 16)
        if raw_size:
            if raw_offset < headers_size or raw_offset + raw_size > file_size:
                fail("PE section has an invalid raw range")
            pe_end = max(pe_end, raw_offset + raw_size)
    if symbols_offset:
        strings_offset = symbols_offset + symbol_count * 18
        if symbols_offset < pe_end or strings_offset + 4 > file_size:
            fail("invalid PE/COFF symbol table")
        strings_size = struct.unpack("<I", read_exact(handle, strings_offset, 4))[0]
        if strings_size < 4 or strings_offset + strings_size > file_size:
            fail("invalid PE/COFF string table")
        pe_end = strings_offset + strings_size
    directory_count = struct.unpack_from("<I", optional, 92)[0]
    cert_offset = cert_size = 0
    certificate_truncated = False
    if directory_count > 4 and optional_size >= 96 + 5 * 8:
        cert_offset, cert_size = struct.unpack_from("<II", optional, 96 + 4 * 8)
        if cert_size:
            if cert_offset < pe_end:
                fail("invalid PE certificate table")
            certificate_truncated = cert_offset + cert_size > file_size
    return PEInfo(pe_end, section_count, timestamp, image_size,
                  cert_offset, cert_size, certificate_truncated)


def der_object_length(data: bytes) -> int:
    if len(data) < 2 or data[0] != 0x30:
        fail("Authenticode payload is not a DER SEQUENCE")
    first = data[1]
    if first < 0x80:
        return 2 + first
    count = first & 0x7F
    if count == 0 or count > 4 or len(data) < 2 + count or data[2] == 0:
        fail("invalid DER length in Authenticode payload")
    length = int.from_bytes(data[2:2 + count], "big")
    return 2 + count + length


def find_database_end(handle: BinaryIO, file_size: int, pe_end: int) -> tuple[int, bool]:
    """Locate the exact BitRock trailer and validate any appended WIN_CERTIFICATE."""
    handle.seek(pe_end)
    overlay = handle.read()
    trailer_at = overlay.rfind(BITROCK_TRAILER)
    if trailer_at < 0:
        return file_size, False
    absolute = pe_end + trailer_at
    after = absolute + len(BITROCK_TRAILER)
    if after == file_size:
        return absolute, True
    certificate_start = (after + 7) & ~7
    padding = read_exact(handle, after, certificate_start - after)
    if any(padding) or certificate_start + 8 > file_size:
        fail("unrecognized bytes after the BitRock trailer")
    certificate = read_exact(handle, certificate_start, file_size - certificate_start)
    length, revision, cert_type = struct.unpack_from("<IHH", certificate, 0)
    if revision != 0x0200 or cert_type != 0x0002 or length < 8 or length > len(certificate):
        fail("invalid appended WIN_CERTIFICATE")
    aligned = (length + 7) & ~7
    if aligned != len(certificate) or any(certificate[length:aligned]):
        fail("invalid WIN_CERTIFICATE alignment padding")
    der = certificate[8:length]
    der_length = der_object_length(der)
    if der_length > len(der) or any(der[der_length:]):
        fail("WIN_CERTIFICATE does not contain exactly one DER object")
    return absolute, True


class Cursor:
    def __init__(self, data: bytes, label: str):
        self.data = data
        self.pos = 0
        self.label = label

    def remaining(self) -> int:
        return len(self.data) - self.pos

    def take(self, count: int) -> bytes:
        if count < 0 or self.pos + count > len(self.data):
            fail(f"truncated {self.label}")
        value = self.data[self.pos:self.pos + count]
        self.pos += count
        return value

    def bp(self) -> int:
        if self.remaining() < 1:
            fail(f"truncated byte-packed integer in {self.label}")
        start = self.pos
        first = self.data[self.pos]
        negative = first == 0
        if negative:
            self.pos += 1
            if self.remaining() < 1:
                fail(f"truncated negative byte-packed integer in {self.label}")
        value = 0
        groups = 0
        while True:
            if self.remaining() < 1 or groups == 5:
                fail(f"invalid byte-packed integer in {self.label}")
            byte = self.data[self.pos]
            self.pos += 1
            value = (value << 7) | (byte & 0x7F)
            groups += 1
            if byte & 0x80:
                break
        value = ~value if negative else value
        if value < -(1 << 31) or value > 0xFFFFFFFF:
            fail(f"byte-packed integer out of range in {self.label}")
        if self.data[start:self.pos] != encode_bp(value):
            fail(f"non-canonical byte-packed integer in {self.label}")
        return value


def encode_bp(value: int) -> bytes:
    prefix = b""
    if value < 0:
        prefix = b"\0"
        value = ~value
    groups = [value & 0x7F]
    value >>= 7
    while value:
        groups.append(value & 0x7F)
        value >>= 7
    groups.reverse()
    groups[-1] |= 0x80
    return prefix + bytes(groups)


@dataclass(frozen=True)
class IVecRef:
    size: int
    position: int | None


@dataclass
class StoredFile:
    content: bytes
    stored_size: int
    size: int
    mtime: int
    path: tuple[str, ...]
    source: str


@dataclass
class MetakitInfo:
    base: int
    end: int
    toc_position: int
    toc_size: int
    directory_count: int
    stored_files: list[StoredFile]
    ranges: list[Range]
    holes: list[tuple[int, int]]
    declared_length: int
    recovered_prior_commit: bool


class MetakitReader:
    def __init__(self, handle: BinaryIO, base: int, end: int,
                 allow_prior_commit: bool = False):
        self.handle = handle
        self.base = base
        self.end = end
        self.length = end - base
        self.ranges: list[Range] = []
        self.allow_prior_commit = allow_prior_commit
        self.declared_length = 0

    def relative(self, position: int, size: int, label: str) -> bytes:
        if position < 0 or size < 0 or position + size > self.length:
            fail(f"Metakit {label} points outside the database")
        if size:
            self.ranges.append(Range(position, position + size, label))
        return read_exact(self.handle, self.base + position, size)

    @staticmethod
    def ref(cursor: Cursor) -> IVecRef:
        size = cursor.bp()
        if size < 0:
            fail("negative Metakit item-vector size")
        position = cursor.bp() if size else None
        if position is not None and position < 0:
            fail("negative Metakit item-vector position")
        return IVecRef(size, position)

    def ref_data(self, ref: IVecRef, label: str) -> bytes:
        if ref.size == 0:
            return b""
        assert ref.position is not None
        return self.relative(ref.position, ref.size, label)

    @staticmethod
    def access_width(rows: int, vector_size: int) -> int:
        if rows <= 0:
            fail("adaptive integer vector has no rows")
        width = (vector_size * 8) // rows
        special = rows <= 7 and 0 < vector_size <= 6
        if special:
            table = (
                (8, 16, 1, 32, 2, 4),
                (4, 8, 1, 16, 2, 0),
                (2, 4, 8, 1, 0, 16),
                (2, 4, 0, 8, 1, 0),
                (1, 2, 4, 0, 8, 0),
                (1, 2, 4, 0, 0, 8),
                (1, 2, 0, 4, 0, 0),
            )
            width = table[rows - 1][vector_size - 1]
        if width not in (0, 1, 2, 4, 8, 16, 32, 64):
            fail("invalid Metakit adaptive-integer width")
        required = (rows * width + 7) // 8
        if not special and required != vector_size:
            fail("non-canonical Metakit adaptive-integer vector")
        return width

    def integers(self, ref: IVecRef, rows: int, signed: bool, label: str) -> list[int]:
        if rows == 0:
            if ref.size:
                fail(f"nonempty {label} for an empty view")
            return []
        data = self.ref_data(ref, label)
        width = self.access_width(rows, len(data))
        if width == 0:
            return [0] * rows
        values: list[int] = []
        if width < 8:
            mask = (1 << width) - 1
            for index in range(rows):
                values.append((data[(index * width) // 8] >> ((index * width) & 7)) & mask)
        else:
            step = width // 8
            byte_order = "little"
            for index in range(rows):
                values.append(int.from_bytes(data[index * step:(index + 1) * step], byte_order,
                                             signed=signed))
        return values

    def variable(self, cursor: Cursor, rows: int, is_string: bool,
        label: str) -> list[bytes]:
        data_ref = self.ref(cursor)
        # Metakit omits the direct-size vector reference when the direct-data
        # vector is empty; the memo catalog reference still follows.
        size_ref = self.ref(cursor) if data_ref.size else IVecRef(0, None)
        catalog_ref = self.ref(cursor)
        sizes = self.integers(size_ref, rows, False, f"{label} sizes")
        direct = self.ref_data(data_ref, f"{label} direct data")
        if sum(sizes) != len(direct):
            fail(f"Metakit {label} direct-data length mismatch")
        values: list[bytes | None] = [None] * rows
        direct_pos = 0
        for index, size in enumerate(sizes):
            if size:
                values[index] = direct[direct_pos:direct_pos + size]
                direct_pos += size
        catalog = self.ref_data(catalog_ref, f"{label} memo catalog")
        cat = Cursor(catalog, f"{label} memo catalog")
        row = 0
        inline: list[tuple[int, int]] = []
        while cat.remaining():
            row += cat.bp()
            if row < 0 or row >= rows or values[row] is not None:
                fail(f"invalid row in Metakit {label} memo catalog")
            memo = self.ref(cat)
            if memo.size:
                if memo.position == 0:
                    inline.append((row, memo.size))
                else:
                    values[row] = self.ref_data(memo, f"{label} memo row {row}")
            else:
                values[row] = b""
            row += 1
        if inline:
            assert catalog_ref.position is not None
            inline_pos = catalog_ref.position + catalog_ref.size
            for index, size in inline:
                values[index] = self.relative(inline_pos, size, f"{label} inline memo row {index}")
                inline_pos += size
        result: list[bytes] = []
        for value in values:
            if value is None:
                value = b""
            if is_string:
                if not value.endswith(b"\0"):
                    fail(f"Metakit {label} string lacks its terminator")
                value = value[:-1]
            result.append(value)
        return result

    def parse(self) -> MetakitInfo:
        if self.length < 24:
            fail("Metakit database is too short")
        header = self.relative(0, 8, "header")
        if header[:4] != b"JL\x1a\x00":
            fail("unsupported Metakit header")
        self.declared_length = be32(header, 4)
        if self.declared_length != self.length and not (
                self.allow_prior_commit and self.declared_length > self.length):
            fail("Metakit header length does not match the linked end")
        footer = self.relative(self.length - 16, 16, "footer")
        if footer[:4] != b"\x80\0\0\0":
            fail("invalid Metakit skip footer")
        header_distance = be32(footer, 4)
        if header_distance != self.length - 16:
            fail("Metakit footer does not link back to its header")
        if footer[8] != 0x80:
            fail("invalid Metakit commit footer")
        toc_size = int.from_bytes(footer[9:12], "big")
        toc_position = be32(footer, 12)
        if toc_size == 0 or toc_position + toc_size > self.length - 16:
            fail("invalid Metakit table-of-contents range")
        toc = Cursor(self.relative(toc_position, toc_size, "table of contents"),
                     "Metakit table of contents")
        if toc.bp() != 0:
            fail("invalid Metakit table-of-contents marker")
        schema_len = toc.bp()
        if schema_len != len(METAKIT_SCHEMA) or toc.take(schema_len) != METAKIT_SCHEMA:
            fail("unsupported Metakit schema")
        root_rows = toc.bp()
        if root_rows != 1:
            fail("BitRock Metakit root view must contain one row")
        dirs_ref = self.ref(toc)
        if toc.remaining():
            fail("unconsumed Metakit table-of-contents bytes")
        dirs_map = Cursor(self.ref_data(dirs_ref, "dirs subview map"), "dirs subview map")
        if dirs_map.bp() != 0:
            fail("invalid dirs subview marker")
        directory_count = dirs_map.bp()
        if directory_count <= 0:
            fail("BitRock directory view is empty")
        names_raw = self.variable(dirs_map, directory_count, True, "directory names")
        parents = self.integers(self.ref(dirs_map), directory_count, True, "directory parents")
        files_ref = self.ref(dirs_map)
        if dirs_map.remaining():
            fail("unconsumed dirs subview mapping bytes")
        names = [decode_name(value, "Metakit directory") for value in names_raw]
        if names[0] != "<root>" or parents[0] != -1:
            fail("invalid BitRock root directory row")
        dir_paths: list[tuple[str, ...]] = [()]
        for index in range(1, directory_count):
            parent = parents[index]
            if parent < 0 or parent >= index:
                fail("Metakit directory parent does not precede its child")
            dir_paths.append(dir_paths[parent] + (names[index],))
        files_map = Cursor(self.ref_data(files_ref, "files subview maps"), "files subview maps")
        stored_files: list[StoredFile] = []
        for directory in range(directory_count):
            marker = files_map.bp()
            if marker != 0:
                fail(f"invalid files subview marker at directory {directory}")
            count = files_map.bp()
            if count < 0:
                fail("negative BitRock file count")
            if count == 0:
                continue
            file_names_raw = self.variable(files_map, count, True,
                                           f"file names for directory {directory}")
            sizes = self.integers(self.ref(files_map), count, True,
                                  f"file sizes for directory {directory}")
            dates = self.integers(self.ref(files_map), count, True,
                                  f"file dates for directory {directory}")
            before = len(self.ranges)
            contents = self.variable(files_map, count, False,
                                     f"file contents for directory {directory}")
            # Resolve each value back to its already-read bytes. This keeps extraction
            # streaming at the file level while preserving strict Metakit validation.
            for index, (name_raw, size, date, content) in enumerate(
                    zip(file_names_raw, sizes, dates, contents)):
                if size < 0:
                    fail("negative BitRock file size")
                name = decode_name(name_raw, "Metakit file")
                stored_files.append(StoredFile(content, len(content), size, date,
                                               dir_paths[directory] + (name,), "metakit"))
            if len(self.ranges) < before:
                fail("internal Metakit range accounting error")
        if files_map.remaining():
            fail("unconsumed files subview mapping bytes")
        holes = self.compute_holes()
        return MetakitInfo(self.base, self.end, toc_position, toc_size,
                           directory_count, stored_files, self.ranges[:], holes,
                           self.declared_length, self.declared_length > self.length)

    def compute_holes(self) -> list[tuple[int, int]]:
        unique = sorted({(r.start, r.end) for r in self.ranges})
        last = 0
        holes: list[tuple[int, int]] = []
        for start, end in unique:
            if start < last:
                # Exact duplicate vectors are legal; partial overlaps are not.
                if end <= last:
                    continue
                fail("overlapping Metakit item vectors")
            if start > last:
                holes.append((last, start))
            last = end
        if last < self.length:
            holes.append((last, self.length))
        return holes


def decode_name(raw: bytes, kind: str) -> str:
    try:
        name = raw.decode("utf-8")
    except UnicodeDecodeError:
        fail(f"{kind} name is not UTF-8")
    if not name or name in (".", "..") or any(c in name for c in ("/", "\\", "\0")):
        fail(f"unsafe {kind} name")
    return name


def safe_components(path: Iterable[str], kind: str) -> tuple[str, ...]:
    result = tuple(path)
    for component in result:
        if not component or component in (".", "..") or any(
                c in component for c in ("/", "\\", "\0")):
            fail(f"unsafe {kind} path")
    return result


@dataclass
class CookFile:
    path: tuple[str, ...]
    mtime: int
    blocks: list[tuple[int, int, int]]


@dataclass
class CookFSInfo:
    start: int
    end: int
    pages: int
    index_size: int
    files: list[CookFile]
    directories: int
    page_sizes: list[int]
    page_hashes: list[bytes]
    page_offsets: list[int]
    page_hash_kind: str
    codec_counts: dict[int, int]
    decoded_sizes: list[int]


def decompress_cookfs(data: bytes, label: str) -> tuple[int, bytes]:
    if not data:
        fail(f"empty CookFS {label}")
    codec, payload = data[0], data[1:]
    try:
        if codec == 0:
            decoded = payload
        elif codec == 1:
            decoder = zlib.decompressobj(-15)
            decoded = decoder.decompress(payload) + decoder.flush()
            if not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
                fail(f"CookFS {label} is not exactly one raw DEFLATE stream")
        elif codec == 255:
            decoder = lzma.LZMADecompressor(format=lzma.FORMAT_ALONE)
            decoded = decoder.decompress(payload)
            if not decoder.eof or decoder.unused_data:
                fail(f"CookFS {label} is not exactly one LZMA-Alone stream")
        else:
            fail(f"unsupported CookFS codec {codec} in {label}")
    except (zlib.error, lzma.LZMAError) as error:
        fail(f"corrupt CookFS {label}: {error}")
    return codec, decoded


class CookIndexCursor(Cursor):
    def u8(self) -> int:
        return self.take(1)[0]

    def u32(self) -> int:
        return struct.unpack(">I", self.take(4))[0]

    def i32(self) -> int:
        return struct.unpack(">i", self.take(4))[0]

    def u64(self) -> int:
        return struct.unpack(">Q", self.take(8))[0]


def parse_cookfs(handle: BinaryIO, start_required: int, end: int) -> CookFSInfo:
    trailer = read_exact(handle, end - 16, 16)
    index_size, page_count = struct.unpack_from(">II", trailer, 0)
    default_codec = trailer[8]
    if trailer[9:] != COOKFS_TRAILER or default_codec not in (0, 1, 255):
        fail("invalid CookFS trailer")
    if index_size == 0 or page_count == 0:
        fail("empty CookFS archive")
    index_meta = end - 16 - index_size - page_count * 20
    if index_meta < start_required:
        fail("CookFS index overlaps the PE image")
    page_hashes = [read_exact(handle, index_meta + i * 16, 16)
                   for i in range(page_count)]
    sizes_raw = read_exact(handle, index_meta + page_count * 16, page_count * 4)
    page_sizes = list(struct.unpack(">" + "I" * page_count, sizes_raw))
    if any(size == 0 for size in page_sizes):
        fail("CookFS contains a zero-length stored page")
    pages_start = index_meta - sum(page_sizes)
    if pages_start != start_required:
        fail("unaccounted bytes between the PE image and CookFS pages")
    offsets: list[int] = []
    offset = pages_start
    for size in page_sizes:
        offsets.append(offset)
        offset += size
    index_stored = read_exact(handle, index_meta + page_count * 20, index_size)
    _, index_data = decompress_cookfs(index_stored, "index")
    if not index_data.startswith(COOKFS_INDEX_MAGIC):
        fail("invalid CookFS filesystem index magic")
    cursor = CookIndexCursor(index_data[len(COOKFS_INDEX_MAGIC):], "CookFS filesystem index")
    files: list[CookFile] = []
    directories = 1

    def walk(parent: tuple[str, ...]) -> None:
        nonlocal directories
        count = cursor.u32()
        if count > 10_000_000:
            fail("implausible CookFS directory entry count")
        for _ in range(count):
            length = cursor.u8()
            raw_name = cursor.take(length)
            if cursor.take(1) != b"\0":
                fail("CookFS filename lacks its terminator")
            name = decode_name(raw_name, "CookFS")
            mtime = cursor.u64()
            blocks_count = cursor.i32()
            path = parent + (name,)
            if blocks_count == -1:
                directories += 1
                walk(path)
            elif blocks_count < 0 or blocks_count > page_count * 2 + 1:
                fail("invalid CookFS block count")
            else:
                blocks = [(cursor.u32(), cursor.u32(), cursor.u32())
                          for _ in range(blocks_count)]
                files.append(CookFile(path, mtime, blocks))

    walk(())
    metadata_count = cursor.u32() if cursor.remaining() >= 4 else 0
    metadata: dict[bytes, bytes] = {}
    for _ in range(metadata_count):
        length = cursor.u32()
        entry = cursor.take(length)
        if b"\0" not in entry:
            fail("invalid CookFS metadata entry")
        key, value = entry.split(b"\0", 1)
        if not key or key in metadata:
            fail("invalid or duplicate CookFS metadata key")
        metadata[key] = value
    if cursor.remaining():
        fail("unconsumed CookFS filesystem-index bytes")
    hash_kind = "crc32" if metadata.get(b"cookfs.pagehash") == b"crc32" else "md5"
    if b"cookfs.pagehash" in metadata and hash_kind != "crc32":
        fail("unsupported CookFS page hash")
    decoded_sizes: list[int] = []
    codec_counts: dict[int, int] = {}
    for index, (offset, stored_size, expected_hash) in enumerate(
            zip(offsets, page_sizes, page_hashes)):
        codec, page = decompress_cookfs(read_exact(handle, offset, stored_size),
                                        f"page {index}")
        codec_counts[codec] = codec_counts.get(codec, 0) + 1
        decoded_sizes.append(len(page))
        if hash_kind == "md5":
            actual_hash = hashlib.md5(page).digest()
        else:
            actual_hash = (b"\0" * 8 + len(page).to_bytes(4, "big") +
                           (binascii.crc32(page) & 0xFFFFFFFF).to_bytes(4, "big"))
        if actual_hash != expected_hash:
            fail(f"CookFS page {index} hash mismatch")
    for file in files:
        safe_components(file.path, "CookFS")
        for page, block_offset, size in file.blocks:
            if page >= page_count or block_offset + size > decoded_sizes[page]:
                fail("CookFS file block points outside its page")
    return CookFSInfo(pages_start, end, page_count, index_size, files, directories,
                      page_sizes, page_hashes, offsets, hash_kind, codec_counts,
                      decoded_sizes)


@dataclass
class Bundle:
    input_path: Path
    file_size: int
    sha256: str
    pe: PEInfo
    metakit: MetakitInfo
    cookfs: CookFSInfo | None
    signature: bool
    mount: tuple[str, ...] | None
    tclkit_launcher: bool
    partial: bool = False
    partial_reason: str | None = None
    skipped_resources: list[str] = field(default_factory=list)
    output_files: int = 0
    output_bytes: int = 0
    merged_chunks: int = 0
    codec_stats: dict[str, int] = field(default_factory=dict)


def metakit_mount(metakit: MetakitInfo, cookfs: CookFSInfo | None) -> tuple[str, ...] | None:
    origin = next((entry for entry in metakit.stored_files
                   if entry.path == ("origindist",)), None)
    if origin is None:
        if cookfs is not None:
            fail("CookFS bundle has no origindist mount resource")
        return ("dist",)
    raw = materialize_metakit_bytes(origin)
    try:
        mount_text = raw.decode("utf-8")
    except UnicodeDecodeError:
        fail("origindist is not UTF-8")
    mount = safe_components(tuple(part for part in mount_text.split("/") if part),
                            "origindist")
    if not mount:
        fail("empty origindist mount point")
    return mount


def partial_suffix_reason(handle: BinaryIO, database_end: int, file_size: int,
                          pe: PEInfo) -> str | None:
    """Validate a strict prefix of the trailer/certificate suffix."""
    tail = read_exact(handle, database_end, file_size - database_end)
    trailer_size = len(BITROCK_TRAILER)
    if len(tail) < trailer_size:
        if tail and BITROCK_TRAILER.startswith(tail):
            return "input ends inside the BitRock trailer"
        return None
    if tail[:trailer_size] != BITROCK_TRAILER:
        return None
    after = database_end + trailer_size
    certificate_start = (after + 7) & ~7
    available_padding = min(file_size, certificate_start) - after
    if any(tail[trailer_size:trailer_size + available_padding]):
        return None
    if file_size < certificate_start:
        return ("input ends in certificate alignment padding"
                if pe.certificate_truncated else None)
    certificate = read_exact(handle, certificate_start, file_size - certificate_start)
    if not certificate:
        if (pe.certificate_truncated and pe.certificate_offset == certificate_start and
                pe.certificate_size >= 8):
            return "input ends before the declared WIN_CERTIFICATE"
        return None
    if len(certificate) < 8:
        if (pe.certificate_truncated and pe.certificate_offset == certificate_start):
            return "input ends inside the WIN_CERTIFICATE header"
        return None
    length, revision, cert_type = struct.unpack_from("<IHH", certificate, 0)
    if revision != 0x0200 or cert_type != 0x0002 or length < 8:
        return None
    aligned = (length + 7) & ~7
    if len(certificate) >= aligned:
        return None
    if pe.certificate_size and (pe.certificate_offset != certificate_start or
                                pe.certificate_size != aligned):
        return None
    return "input ends inside the WIN_CERTIFICATE"


def recover_truncated(handle: BinaryIO, file_size: int, pe: PEInfo,
                      input_path: Path) -> Bundle | None:
    """Recover the newest complete Metakit commit from a proven truncated bundle."""
    payload_start = pe.end
    has_launcher = False
    if file_size >= pe.end + len(TCLKIT_LAUNCHER) and read_exact(
            handle, pe.end, len(TCLKIT_LAUNCHER)) == TCLKIT_LAUNCHER:
        payload_start += len(TCLKIT_LAUNCHER)
        has_launcher = True
    if file_size < payload_start + 8:
        return None
    with mmap.mmap(handle.fileno(), 0, access=mmap.ACCESS_READ) as mapped:
        bases: list[int] = []
        position = mapped.find(b"JL\x1a\0", payload_start)
        while position >= 0:
            if position + 8 <= file_size:
                bases.append(position)
            position = mapped.find(b"JL\x1a\0", position + 1)
        recovered: list[tuple[int, Bundle]] = []
        for base in bases:
            declared = be32(mapped[base:base + 8], 4)
            if declared < 24:
                continue
            declared_end = base + declared
            reason: str | None
            if declared_end > file_size:
                reason = (f"input is truncated at 0x{file_size:x}; Metakit declares "
                          f"an end at 0x{declared_end:x}")
                search_end = file_size
            else:
                reason = partial_suffix_reason(handle, declared_end, file_size, pe)
                if reason is None:
                    continue
                search_end = declared_end
            cookfs: CookFSInfo | None = None
            if base == payload_start:
                pass
            elif base >= 7 and mapped[base - 7:base] == COOKFS_TRAILER:
                try:
                    cookfs = parse_cookfs(handle, payload_start, base)
                except FormatError:
                    continue
            else:
                continue
            footer_positions: list[int] = []
            footer_at = mapped.find(b"\x80\0\0\0", base + 8, search_end)
            while footer_at >= 0 and footer_at + 16 <= search_end:
                footer = mapped[footer_at:footer_at + 16]
                if be32(footer, 4) == footer_at - base and footer[8] == 0x80:
                    footer_positions.append(footer_at)
                footer_at = mapped.find(b"\x80\0\0\0", footer_at + 1, search_end)
            for footer_at in reversed(footer_positions):
                commit_end = footer_at + 16
                try:
                    metakit = MetakitReader(handle, base, commit_end,
                                            allow_prior_commit=True).parse()
                    mount = metakit_mount(metakit, cookfs)
                except FormatError:
                    continue
                detail = reason
                if commit_end < declared_end:
                    detail += f"; recovered complete commit ending at 0x{commit_end:x}"
                bundle = Bundle(input_path, file_size, "", pe, metakit, cookfs,
                                False, mount, has_launcher, True, detail)
                recovered.append((commit_end, bundle))
                break
        if not recovered:
            return None
        return max(recovered, key=lambda item: item[0])[1]


def analyze(input_path: Path) -> Bundle:
    try:
        file_size = input_path.stat().st_size
        with input_path.open("rb") as handle:
            pe = parse_pe(handle, file_size)
            complete_error: FormatError | None = None
            try:
                database_end, has_signature = find_database_end(handle, file_size, pe.end)
                if pe.certificate_size:
                    expected_certificate = (database_end + len(BITROCK_TRAILER) + 7) & ~7
                    if (pe.certificate_truncated or not has_signature or
                            pe.certificate_offset != expected_certificate or
                            pe.certificate_offset + pe.certificate_size != file_size):
                        fail("PE security directory does not match the appended certificate")
                if database_end < 16:
                    fail("no linked BitRock Metakit footer")
                footer = read_exact(handle, database_end - 16, 16)
                if footer[:4] != b"\x80\0\0\0" or footer[8] != 0x80:
                    fail("no linked BitRock Metakit footer")
                header_distance = be32(footer, 4)
                database_base = database_end - 16 - header_distance
                if database_base < pe.end or database_base + 8 > database_end:
                    fail("invalid linked BitRock Metakit header position")
                metakit = MetakitReader(handle, database_base, database_end).parse()
                payload_start = pe.end
                has_launcher = False
                if database_base >= pe.end + len(TCLKIT_LAUNCHER) and read_exact(
                        handle, pe.end, len(TCLKIT_LAUNCHER)) == TCLKIT_LAUNCHER:
                    payload_start += len(TCLKIT_LAUNCHER)
                    has_launcher = True
                cookfs = None
                if database_base >= 16 and read_exact(
                        handle, database_base - 7, 7) == COOKFS_TRAILER:
                    cookfs = parse_cookfs(handle, payload_start, database_base)
                elif database_base != payload_start:
                    fail("unaccounted payload bytes before the Metakit database")
                mount = metakit_mount(metakit, cookfs)
                bundle = Bundle(input_path, file_size, "", pe, metakit, cookfs,
                                has_signature, mount, has_launcher)
            except FormatError as error:
                complete_error = error
                bundle = recover_truncated(handle, file_size, pe, input_path)
                if bundle is None:
                    raise complete_error
        digest = hashlib.sha256()
        with input_path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        bundle.sha256 = digest.hexdigest()
        return bundle
    except OSError as error:
        fail(str(error))


def materialize_metakit_bytes(entry: StoredFile) -> bytes:
    data = entry.content
    if len(data) == entry.size:
        return data
    try:
        decoder = zlib.decompressobj()
        decoded = decoder.decompress(data) + decoder.flush()
    except zlib.error as error:
        fail(f"corrupt zlib resource {'/'.join(entry.path)}: {error}")
    if not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
        fail(f"resource is not exactly one zlib stream: {'/'.join(entry.path)}")
    if len(decoded) != entry.size:
        fail(f"resource size mismatch for {'/'.join(entry.path)}")
    return decoded


class PageSource:
    def __init__(self, handle: BinaryIO, info: CookFSInfo):
        self.handle = handle
        self.info = info
        self.cached_index: int | None = None
        self.cached_data = b""

    def get(self, index: int) -> bytes:
        if index != self.cached_index:
            raw = read_exact(self.handle, self.info.page_offsets[index],
                             self.info.page_sizes[index])
            _, self.cached_data = decompress_cookfs(raw, f"page {index}")
            self.cached_index = index
        return self.cached_data


def output_path(root: Path, components: tuple[str, ...]) -> Path:
    safe_components(components, "output")
    result = root
    for component in components:
        result = result / component
    return result


def write_file(path: Path, chunks: Iterable[bytes], mtime: int) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    with path.open("wb") as handle:
        for chunk in chunks:
            handle.write(chunk)
            total += len(chunk)
    os.chmod(path, 0o664)
    if mtime > 0:
        try:
            os.utime(path, (mtime, mtime))
        except (OSError, OverflowError):
            pass
    return total


def merge_big_files(stage: Path, mtimes: dict[tuple[str, ...], int]) -> int:
    groups: dict[tuple[str, ...], dict[int, Path]] = {}
    for path in stage.rglob("*"):
        if not path.is_file():
            continue
        match = BIG_FILE_RE.match(path.name)
        if match:
            base = path.relative_to(stage).parts[:-1] + (match.group(1),)
            index = int(match.group(2))
            if index in groups.setdefault(base, {}):
                fail("duplicate BitRock big-file chunk")
            groups[base][index] = path
    merged = 0
    for base_parts, chunks in groups.items():
        expected = set(range(1, max(chunks) + 1))
        if set(chunks) != expected:
            fail(f"non-contiguous BitRock chunks for {'/'.join(base_parts)}")
        base = output_path(stage, base_parts)
        if not base.is_file():
            fail(f"BitRock big-file chunk has no base file: {'/'.join(base_parts)}")
        with base.open("ab") as out:
            for index in sorted(chunks):
                with chunks[index].open("rb") as source:
                    shutil.copyfileobj(source, out, 1024 * 1024)
                chunks[index].unlink()
                merged += 1
        os.chmod(base, 0o664)
        mtime = mtimes.get(base_parts, 0)
        if mtime > 0:
            os.utime(base, (mtime, mtime))
    return merged


def metadata_for(bundle: Bundle) -> dict[str, object]:
    return {
        "format": "BitRock InstallBuilder / Metakit-CookFS",
        "extraction_scope": "complete-installer-vfs",
        "payload_mount": "/".join(bundle.mount or ()),
        "input": bundle.input_path.name,
        "input_size": bundle.file_size,
        "sha256": bundle.sha256,
        "pe": {
            "end_offset": bundle.pe.end,
            "sections": bundle.pe.sections,
            "timestamp": bundle.pe.timestamp,
            "image_size": bundle.pe.image_size,
            "certificate_offset": bundle.pe.certificate_offset,
            "certificate_size": bundle.pe.certificate_size,
            "certificate_truncated": bundle.pe.certificate_truncated,
        },
        "metakit": {
            "start_offset": bundle.metakit.base,
            "end_offset": bundle.metakit.end,
            "declared_end_offset": (bundle.metakit.base +
                                    bundle.metakit.declared_length),
            "recovered_prior_commit": bundle.metakit.recovered_prior_commit,
            "toc_offset": bundle.metakit.base + bundle.metakit.toc_position,
            "toc_size": bundle.metakit.toc_size,
            "directories": bundle.metakit.directory_count,
            "stored_files": len(bundle.metakit.stored_files),
            "holes": [{"offset": bundle.metakit.base + a, "size": b - a}
                      for a, b in bundle.metakit.holes],
        },
        "cookfs": None if bundle.cookfs is None else {
            "start_offset": bundle.cookfs.start,
            "end_offset": bundle.cookfs.end,
            "pages": bundle.cookfs.pages,
            "index_size": bundle.cookfs.index_size,
            "directories": bundle.cookfs.directories,
            "stored_files": len(bundle.cookfs.files),
            "page_hash": bundle.cookfs.page_hash_kind,
            "page_codecs": bundle.cookfs.codec_counts,
            "mount": "/".join(bundle.mount or ()),
        },
        "bitrock_trailer": bundle.signature,
        "tclkit_launcher": bundle.tclkit_launcher,
        "partial_extraction": bundle.partial,
        "partial_reason": bundle.partial_reason,
        "skipped_resources": bundle.skipped_resources,
        "extracted_files": bundle.output_files,
        "extracted_bytes": bundle.output_bytes,
        "merged_chunk_files": bundle.merged_chunks,
        "resource_codecs": bundle.codec_stats,
    }


def extract(bundle: Bundle, output_dir: Path, include_metadata: bool) -> None:
    output_parent = output_dir.parent.resolve()
    output_parent.mkdir(parents=True, exist_ok=True)
    output_existed = output_dir.exists()
    with tempfile.TemporaryDirectory(prefix=".bitRock-", dir=output_parent) as temporary:
        stage = Path(temporary)
        mtimes: dict[tuple[str, ...], int] = {}
        zlib_count = raw_count = 0
        # Without --all, expose only the installable distribution and strip its
        # VFS mount name. The other Metakit trees are InstallBuilder's runtime.
        for entry in bundle.metakit.stored_files:
            if include_metadata:
                destination_path = entry.path
            else:
                assert bundle.mount is not None
                if entry.path[:len(bundle.mount)] != bundle.mount:
                    continue
                destination_path = entry.path[len(bundle.mount):]
                if not destination_path:
                    continue
            try:
                data = materialize_metakit_bytes(entry)
            except FormatError as error:
                if not bundle.partial:
                    raise
                bundle.skipped_resources.append(f"{'/'.join(entry.path)}: {error}")
                continue
            if entry.stored_size == entry.size:
                raw_count += 1
            else:
                zlib_count += 1
            write_file(output_path(stage, destination_path), (data,), entry.mtime)
            mtimes[destination_path] = entry.mtime
        if bundle.cookfs is not None:
            assert bundle.mount is not None
            with bundle.input_path.open("rb") as handle:
                pages = PageSource(handle, bundle.cookfs)
                for entry in bundle.cookfs.files:
                    path = bundle.mount + entry.path if include_metadata else entry.path
                    def chunks() -> Iterable[bytes]:
                        for page_index, offset, size in entry.blocks:
                            yield pages.get(page_index)[offset:offset + size]
                    total = write_file(output_path(stage, path), chunks(), entry.mtime)
                    expected = sum(block[2] for block in entry.blocks)
                    if total != expected:
                        fail(f"CookFS output length mismatch for {'/'.join(path)}")
                    mtimes[path] = entry.mtime
        bundle.merged_chunks = merge_big_files(stage, mtimes)
        files: list[Path] = []
        for root, directories, names in os.walk(stage):
            parent = Path(root)
            for directory in directories:
                os.chmod(parent / directory, 0o775)
            files.extend(parent / name for name in names)
        bundle.output_files = len(files)
        bundle.output_bytes = sum(path.stat().st_size for path in files)
        bundle.codec_stats = {"raw": raw_count, "zlib": zlib_count}
        if bundle.cookfs:
            for codec, count in bundle.cookfs.codec_counts.items():
                bundle.codec_stats[{0: "cookfs-raw", 1: "cookfs-deflate",
                                    255: "cookfs-lzma"}[codec]] = count
        if include_metadata:
            metadata = json.dumps(metadata_for(bundle), indent=2, sort_keys=True).encode() + b"\n"
            write_file(stage / "__bitrock_metadata__.json", (metadata,), 0)
            bundle.output_files += 1
            bundle.output_bytes += len(metadata)
        os.chmod(stage, 0o775)
        if not output_existed:
            # The complete staged tree is on the destination filesystem, so a
            # directory rename commits it atomically without duplicating every
            # file. TemporaryDirectory cleanup tolerates the moved path.
            os.replace(stage, output_dir)
            return
        output_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(output_dir, os.stat(output_dir).st_mode | stat.S_IRGRP | stat.S_IXGRP |
                 stat.S_IRUSR | stat.S_IXUSR)
        for source in sorted(stage.iterdir(), key=lambda p: p.name):
            destination = output_dir / source.name
            if source.is_dir():
                destination.mkdir(parents=True, exist_ok=True)
                shutil.copytree(source, destination, dirs_exist_ok=True, copy_function=shutil.copy2)
            else:
                os.replace(source, destination)
        for path in output_dir.rglob("*"):
            if path.is_dir():
                os.chmod(path, 0o775)
            elif path.is_file():
                os.chmod(path, 0o664)


def cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="bitRock.py",
        description="Strictly extract a supported BitRock InstallBuilder executable.",
    )
    parser.add_argument("--all", action="store_true",
                        help="extract the complete installer VFS and create metadata")
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputDir", type=Path)
    args = parser.parse_args(argv)
    if not args.inputFile.is_file():
        parser.error("inputFile must be an existing regular file")
    try:
        bundle = analyze(args.inputFile)
        extract(bundle, args.outputDir, args.all)
    except FormatError as error:
        print(f"bitRock.py: error: {error}", file=sys.stderr)
        return 1
    if bundle.partial:
        print(f"bitRock.py: warning: partial BitRock installer: {bundle.partial_reason}",
              file=sys.stderr)
        if bundle.skipped_resources:
            print(f"bitRock.py: warning: skipped {len(bundle.skipped_resources)} "
                  "incomplete or corrupt resources", file=sys.stderr)
    verb = "partially extracted" if bundle.partial else "extracted"
    print(f"{verb} {bundle.output_files} files ({bundle.output_bytes} bytes) "
          f"to {args.outputDir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())

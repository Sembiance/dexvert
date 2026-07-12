#!/usr/bin/env python3
# Vibe coded by Codex
"""Strict extractor for self-contained Clickteam installer generations."""

from __future__ import annotations

import argparse
import bz2
import codecs
import datetime as dt
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import shutil
import struct
import sys
import tempfile
import zlib


MAGIC = b"wwgT)H"
OLD_STREAM_END = 0x1234
FILE_LIST = 0x143A
FILE_DATA = 0x7F7F
KNOWN_LAYOUTS = (20, 24, 30, 35, 40)
BLOCK_NAMES = {
    0x1435: "font",
    0x1436: "installer_data",
    0x1437: "background_image",
    0x1438: "unknown_1438",
    0x1439: "unknown_1439",
    0x143A: "file_list",
    0x143D: "unknown_143d",
    0x143E: "strings",
    0x143F: "uninstaller",
    0x1441: "unknown_1441",
    0x1442: "unknown_1442",
    0x1443: "unknown_1443",
    0x1444: "numbers",
    0x1445: "registry_changes",
    0x1446: "unknown_1446",
    0x7F7F: "file_data",
}
FILETIME_EPOCH = dt.datetime(1601, 1, 1, tzinfo=dt.timezone.utc)
FILETIME_MAX = int((dt.datetime(2200, 1, 1, tzinfo=dt.timezone.utc) - FILETIME_EPOCH).total_seconds() * 10_000_000)


class FormatError(Exception):
    """The input is not one of the completely supported containers."""


def u16(data: bytes, offset: int) -> int:
    if offset < 0 or offset + 2 > len(data):
        raise FormatError("truncated 16-bit field")
    return struct.unpack_from("<H", data, offset)[0]


def u32(data: bytes, offset: int) -> int:
    if offset < 0 or offset + 4 > len(data):
        raise FormatError("truncated 32-bit field")
    return struct.unpack_from("<I", data, offset)[0]


def u64(data: bytes, offset: int) -> int:
    if offset < 0 or offset + 8 > len(data):
        raise FormatError("truncated 64-bit field")
    return struct.unpack_from("<Q", data, offset)[0]


def pe_overlay_offset(data: bytes) -> int:
    if len(data) < 64 or data[:2] != b"MZ":
        raise FormatError("input is not a DOS/PE executable")
    pe = u32(data, 0x3C)
    if pe + 24 > len(data) or data[pe:pe + 4] != b"PE\0\0":
        raise FormatError("invalid PE header")
    section_count = u16(data, pe + 6)
    optional_size = u16(data, pe + 20)
    if section_count == 0 or section_count > 96:
        raise FormatError("invalid PE section count")
    table = pe + 24 + optional_size
    if table + section_count * 40 > len(data):
        raise FormatError("truncated PE section table")
    ends = []
    for index in range(section_count):
        entry = table + index * 40
        raw_size = u32(data, entry + 16)
        raw_offset = u32(data, entry + 20)
        if raw_offset + raw_size > len(data):
            raise FormatError("PE section extends beyond end of input")
        ends.append(raw_offset + raw_size)
    return max(ends)


def pe_certificate_tail(data: bytes, archive_end: int) -> bytes:
    """Validate and return an Authenticode certificate/padding tail."""
    pe = u32(data, 0x3C)
    optional = pe + 24
    optional_end = optional + u16(data, pe + 20)
    magic = u16(data, optional)
    if magic == 0x10B:
        directories = optional + 96
        directory_count_offset = optional + 92
    elif magic == 0x20B:
        directories = optional + 112
        directory_count_offset = optional + 108
    else:
        raise FormatError("unsupported PE optional-header magic")
    if (directory_count_offset + 4 > optional_end
            or u32(data, directory_count_offset) < 5
            or directories + 5 * 8 > optional_end):
        raise FormatError("PE optional header has no certificate-table directory")
    certificate_offset = u32(data, directories + 4 * 8)
    certificate_size = u32(data, directories + 4 * 8 + 4)
    if certificate_offset == 0 and certificate_size == 0:
        if archive_end != len(data):
            raise FormatError("bytes follow the final archive block without a PE certificate entry")
        return b""
    if (certificate_offset % 8 or certificate_size < 8
            or certificate_offset < archive_end
            or certificate_offset + certificate_size != len(data)
            or any(data[archive_end:certificate_offset])):
        raise FormatError("invalid PE certificate tail after the archive")
    position = certificate_offset
    end = certificate_offset + certificate_size
    while position < end:
        length = u32(data, position)
        if length < 8 or position + length > end:
            raise FormatError("invalid WIN_CERTIFICATE boundary")
        next_position = (position + length + 7) & ~7
        if next_position > end or any(data[position + length:next_position]):
            raise FormatError("invalid WIN_CERTIFICATE alignment padding")
        position = next_position
    if position != end:
        raise FormatError("WIN_CERTIFICATE records do not consume their directory")
    return data[archive_end:]


class ClickteamBits:
    """LSB-first bit reader used by pre-wwg Clickteam streams."""

    def __init__(self, data: bytes):
        self.data = data
        self.position = 0
        self.bits = 0
        self.count = 0
        self.total = 0

    def fill(self, count: int) -> None:
        while self.count < count and self.position < len(self.data):
            self.bits |= self.data[self.position] << self.count
            self.position += 1
            self.count += 8

    def read(self, count: int) -> int:
        self.fill(count)
        if self.count < count:
            raise FormatError("truncated old-generation compressed stream")
        value = self.bits & ((1 << count) - 1)
        self.bits >>= count
        self.count -= count
        self.total += count
        return value

    def peek(self, count: int) -> int:
        self.fill(count)
        return self.bits & ((1 << count) - 1)

    def drop(self, count: int) -> None:
        if self.count < count:
            raise FormatError("truncated old-generation Huffman symbol")
        self.bits >>= count
        self.count -= count
        self.total += count

    def align(self) -> None:
        padding = (-self.total) & 7
        if padding:
            self.drop(padding)


def reverse_bits(value: int, count: int) -> int:
    result = 0
    for _ in range(count):
        result = (result << 1) | (value & 1)
        value >>= 1
    return result


class ClickteamHuffman:
    def __init__(self, lengths: list[int]):
        counts = [0] * 17
        for length in lengths:
            if length < 0 or length > 16:
                raise FormatError("invalid old-generation Huffman code length")
            if length:
                counts[length] += 1
        next_code = [0] * 17
        code = 0
        for length in range(1, 17):
            code = (code + counts[length - 1]) << 1
            next_code[length] = code
        self.table: dict[tuple[int, int], int] = {}
        self.maximum = max(lengths, default=0)
        for symbol, length in enumerate(lengths):
            if length:
                key = (reverse_bits(next_code[length], length), length)
                if key in self.table:
                    raise FormatError("oversubscribed old-generation Huffman tree")
                self.table[key] = symbol
                next_code[length] += 1
        self.fast: list[tuple[int, int] | None] = [None] * (1 << self.maximum)
        for (code, length), symbol in self.table.items():
            for suffix in range(1 << (self.maximum - length)):
                self.fast[code | (suffix << length)] = (symbol, length)

    def decode(self, reader: ClickteamBits) -> int:
        if not self.maximum:
            raise FormatError("empty old-generation Huffman tree")
        item = self.fast[reader.peek(self.maximum)]
        if item is None:
            raise FormatError("invalid old-generation Huffman code")
        symbol, length = item
        reader.drop(length)
        return symbol


OLD_LENGTH_BASE = (3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 17, 19, 23, 27, 31,
                   35, 43, 51, 59, 67, 83, 99, 115, 131, 163, 195, 227, 258)
OLD_LENGTH_EXTRA = (0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2,
                    3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 0)
OLD_DISTANCE_BASE = (1, 2, 3, 4, 5, 7, 9, 13, 17, 25, 33, 49, 65, 97, 129,
                     193, 257, 385, 513, 769, 1025, 1537, 2049, 3073, 4097,
                     6145, 8193, 12289, 16385, 24577)
OLD_DISTANCE_EXTRA = (0, 0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6,
                      7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13)
OLD_CODE_ORDER = (18, 17, 16, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)


def clickteam_trees(reader: ClickteamBits, block_type: int) -> tuple[ClickteamHuffman, ClickteamHuffman]:
    if block_type == 5:
        return (ClickteamHuffman([8] * 144 + [9] * 112 + [7] * 24 + [8] * 8),
                ClickteamHuffman([5] * 30))
    literal_count = reader.read(5) + 257
    distance_count = reader.read(5) + 1
    code_count = reader.read(4) + 4
    if literal_count > 286 or distance_count > 30:
        raise FormatError("invalid old-generation dynamic tree dimensions")
    code_lengths = [0] * 19
    for index in range(code_count):
        code_lengths[OLD_CODE_ORDER[index]] = reader.read(3)
    code_tree = ClickteamHuffman(code_lengths)
    lengths: list[int] = []
    total = literal_count + distance_count
    while len(lengths) < total:
        symbol = code_tree.decode(reader)
        if symbol < 16:
            lengths.append(symbol)
        elif symbol == 16:
            if not lengths:
                raise FormatError("old-generation tree repeats a missing length")
            lengths.extend([lengths[-1]] * (reader.read(2) + 3))
        elif symbol == 17:
            lengths.extend([0] * (reader.read(3) + 3))
        elif symbol == 18:
            lengths.extend([0] * (reader.read(7) + 11))
        if len(lengths) > total:
            raise FormatError("old-generation tree repeat exceeds its boundary")
    return (ClickteamHuffman(lengths[:literal_count]),
            ClickteamHuffman(lengths[literal_count:]))


def decompress_clickteam(data: bytes, expected: int | None, require_exact: bool = True,
                         sentinel: bool = True) -> tuple[bytes, int]:
    """Decode Clickteam's pre-wwg DEFLATE dialect and return bytes consumed."""
    reader = ClickteamBits(data)
    result = bytearray()
    final = False
    while not final:
        header = reader.read(4)
        final = bool(header & 8)
        block_type = header & 7
        if block_type == 7:
            reader.align()
            stored_size = reader.read(16)
            for _ in range(stored_size):
                result.append(reader.read(8))
            continue
        if block_type not in (5, 6):
            raise FormatError(f"invalid old-generation compressed block type {block_type}")
        literal_tree, distance_tree = clickteam_trees(reader, block_type)
        while True:
            symbol = literal_tree.decode(reader)
            if symbol < 256:
                result.append(symbol)
                continue
            if symbol == 256:
                break
            length_index = symbol - 257
            if not 0 <= length_index < len(OLD_LENGTH_BASE):
                raise FormatError("invalid old-generation length symbol")
            length = OLD_LENGTH_BASE[length_index] + reader.read(OLD_LENGTH_EXTRA[length_index])
            distance_symbol = distance_tree.decode(reader)
            if distance_symbol >= len(OLD_DISTANCE_BASE):
                raise FormatError("invalid old-generation distance symbol")
            distance = OLD_DISTANCE_BASE[distance_symbol] + reader.read(OLD_DISTANCE_EXTRA[distance_symbol])
            if distance > len(result):
                raise FormatError("old-generation back-reference precedes output")
            pattern = bytes(result[-distance:])
            repeats = (length + distance - 1) // distance
            result.extend((pattern * repeats)[:length])
    consumed = (reader.total + 7) // 8
    if sentinel:
        if consumed + 4 > len(data) or u32(data, consumed) != OLD_STREAM_END:
            raise FormatError("old-generation compressed stream has no 0x1234 end sentinel")
        consumed += 4
    if require_exact and consumed != len(data):
        raise FormatError("bytes follow old-generation compressed stream sentinel")
    if expected is not None and len(result) != expected:
        raise FormatError(f"old-generation decompressed size mismatch ({len(result)} != {expected})")
    return bytes(result), consumed


def decompress_exact(method: int, payload: bytes, expected: int) -> bytes:
    try:
        if method == 0:
            result = payload
        elif method == 1:
            obj = zlib.decompressobj()
            result = obj.decompress(payload) + obj.flush()
            if not obj.eof or obj.unused_data or obj.unconsumed_tail:
                raise FormatError("zlib stream does not end exactly at its declared boundary")
        elif method == 2:
            obj = bz2.BZ2Decompressor()
            result = obj.decompress(payload)
            if not obj.eof or obj.unused_data:
                raise FormatError("bzip2 stream does not end exactly at its declared boundary")
        else:
            raise FormatError(f"unsupported compression method {method}")
    except (OSError, EOFError, zlib.error) as exc:
        raise FormatError(f"damaged compressed stream: {exc}") from exc
    if len(result) != expected:
        raise FormatError(f"decompressed size mismatch ({len(result)} != {expected})")
    return result


def decompress_file_record(record: bytes, expected: int) -> tuple[bytes, int | str]:
    """Decode either generation of the modern per-file compression wrapper."""
    if not record:
        raise FormatError("compressed file record is empty")
    if record[0] in (0, 1, 2):
        return decompress_exact(record[0], record[1:], expected), record[0]
    # Early wwg containers put the RFC 1950 stream directly in the record;
    # later containers prefix it with method byte 1.  The CMF/FLG check and
    # exact decompression distinguish the old wrapper without guessing.
    if (len(record) >= 2 and record[0] == 0x78
            and ((record[0] << 8) | record[1]) % 31 == 0):
        return decompress_exact(1, record, expected), "zlib-implicit"
    raise FormatError(f"unsupported compression method {record[0]}")


def modern_delta_section(data: bytes, position: int) -> tuple[bytes, int]:
    """Decode one size-bounded command/literal section in a wwg delta record."""
    if position >= len(data):
        raise FormatError("truncated modern delta section")
    flags = data[position]
    position += 1
    if flags & ~7:
        raise FormatError("modern delta section has unknown flags")
    size_width = 4 if flags & 2 else 2
    if position + size_width > len(data):
        raise FormatError("truncated modern delta decoded size")
    decoded_size = int.from_bytes(data[position:position + size_width], "little")
    position += size_width
    if flags & 1:
        compressed_width = 4 if flags & 4 else 2
        if position + compressed_width > len(data):
            raise FormatError("truncated modern delta compressed size")
        compressed_size = int.from_bytes(
            data[position:position + compressed_width], "little")
        position += compressed_width
        end = position + compressed_size
        if end > len(data):
            raise FormatError("modern delta section exceeds its record")
        decoded, _ = decompress_file_record(data[position:end], decoded_size)
        return decoded, end
    end = position + decoded_size
    if end > len(data):
        raise FormatError("stored modern delta section exceeds its record")
    return data[position:end], end


def validate_modern_delta(record: bytes, expected: int) -> tuple[int, int]:
    commands, position = modern_delta_section(record, 0)
    literals, position = modern_delta_section(record, position)
    if position != len(record):
        raise FormatError("bytes follow modern delta sections")
    return validate_patch_program(commands, literals, expected)


def parse_blocks(data: bytes, overlay: int, issues: list[str] | None = None) -> list[dict]:
    issues = issues if issues is not None else []
    position = overlay + len(MAGIC)
    blocks: list[dict] = []
    while position < len(data):
        if position + 8 > len(data):
            raise FormatError("truncated block header")
        block_start = position
        block_id, marker, size = struct.unpack_from("<HHI", data, position)
        position += 8
        if block_id == FILE_DATA:
            if marker != 0:
                raise FormatError("file-data block marker is not zero")
            if position + 4 > len(data):
                raise FormatError("truncated file-data block header")
            repeated_size = u32(data, position)
            if repeated_size != size:
                raise FormatError("file-data repeated length does not match its block length")
            content_start = position + 4
            expected_end = content_start + size
            content_end = min(expected_end, len(data))
            incomplete = content_end != expected_end
            if incomplete:
                issues.append(
                    f"file-data block is truncated: {content_end - content_start} of {size} bytes are present"
                )
            blocks.append({
                "id": block_id,
                "marker": marker,
                "start": block_start,
                "physical_size": content_end - block_start,
                "declared_size": size,
                "method": None,
                "uncompressed_size": size,
                "raw": data[block_start:content_end],
                "decoded": data[content_start:content_end],
                "incomplete": incomplete,
            })
            position = content_end
            if not incomplete:
                try:
                    pe_certificate_tail(data, position)
                except FormatError as exc:
                    issues.append(str(exc))
            break

        if marker == 0:
            end = position + size
            if end > len(data):
                raise FormatError(f"stored block 0x{block_id:04x} exceeds the input")
            blocks.append({
                "id": block_id,
                "marker": marker,
                "start": block_start,
                "physical_size": 8 + size,
                "declared_size": size,
                "method": 0,
                "uncompressed_size": size,
                "raw": data[block_start:end],
                "decoded": data[position:end],
            })
            position = end
            continue
        if marker != 1:
            raise FormatError(f"block 0x{block_id:04x} marker is neither stored nor compressed")
        end = position + size
        if size < 5 or end > len(data):
            raise FormatError(f"invalid size for block 0x{block_id:04x}")
        wrapper = data[position:end]
        decoded_size = u32(wrapper, 0)
        if wrapper[4] in (0, 1, 2):
            method = wrapper[4]
            decoded = decompress_exact(method, wrapper[5:], decoded_size)
        elif (wrapper[4] == 0x78 and len(wrapper) >= 6
              and ((wrapper[4] << 8) | wrapper[5]) % 31 == 0):
            method = "zlib-implicit"
            decoded = decompress_exact(1, wrapper[4:], decoded_size)
        else:
            raise FormatError(f"unsupported compression method {wrapper[4]}")
        blocks.append({
            "id": block_id,
            "marker": marker,
            "start": block_start,
            "physical_size": 8 + size,
            "declared_size": size,
            "method": method,
            "uncompressed_size": decoded_size,
            "raw": data[block_start:end],
            "decoded": decoded,
        })
        position = end
    if not blocks or blocks[-1]["id"] != FILE_DATA:
        raise FormatError("container has no final file-data block")
    return blocks


def parse_old_blocks(data: bytes, overlay: int, issues: list[str] | None = None) -> tuple[int, bytes, tuple[int, int], list[dict], bytes]:
    issues = issues if issues is not None else []
    if overlay + 12 > len(data):
        raise FormatError("truncated old-generation overlay header")
    generation_tag, compressed_size, decoded_size = struct.unpack_from("<III", data, overlay)
    if generation_tag not in (0x11239, 0x11241, 0x11242):
        raise FormatError(f"unsupported Clickteam overlay tag 0x{generation_tag:08x}")
    stream_start = overlay + 12
    stream_end = stream_start + compressed_size
    if stream_end > len(data):
        raise FormatError("old-generation initial stream exceeds the input")
    standard = None
    try:
        initial, _ = decompress_clickteam(data[stream_start:stream_end], decoded_size)
        if stream_end + 8 <= len(data):
            prefix_size = u32(data, stream_end)
            prefix_end = stream_end + 4 + prefix_size
            if prefix_size in (4, 12) and prefix_end <= len(data):
                prefix = (prefix_size, u32(data, stream_end + 4))
                standard = (initial, prefix, prefix_end)
    except FormatError:
        pass
    compact = None
    if generation_tag == 0x11242 and compressed_size >= 5:
        try:
            initial, used = decompress_clickteam(
                data[stream_start:stream_end - 4], decoded_size, sentinel=False)
            first_block = u32(data, stream_end - 4)
            if used == compressed_size - 4 and first_block & 0x10000 and first_block & 0xFFFF in {
                    0x1235, 0x1236, 0x1237, 0x1238, 0x1239, 0x123A,
                    0x123B, 0x123C, 0x123D, 0x123E, 0x123F, 0x1240, 0x1241,
                    0x1242, 0x1243, 0x1244, 0x1245, 0x1246}:
                compact = (initial, (0, 0), stream_end - 4)
        except FormatError:
            pass
    variants = [item for item in (standard, compact) if item is not None]
    if not variants:
        raise FormatError("old-generation initial stream has no valid header variant")
    if len(variants) != 1:
        raise FormatError("old-generation initial stream header is ambiguous")
    initial, prefix, position = variants[0]
    blocks: list[dict] = []
    trailing = b""
    while position < len(data):
        if data[position:] and not any(data[position:]):
            trailing = data[position:]
            position = len(data)
            break
        if position + 8 > len(data):
            raise FormatError("truncated old-generation block header")
        start = position
        block_id, size = struct.unpack_from("<II", data, position)
        position += 8
        if block_id == 0 or block_id & 0xFFFF not in {
                0x1234, 0x1235, 0x1236, 0x1237, 0x1238, 0x1239, 0x123A, 0x123B,
                0x123C, 0x123D, 0x123E, 0x123F, 0x1240, 0x1241, 0x1242,
                0x1243, 0x1244, 0x1245, 0x1246, 0x7F7F}:
            raise FormatError(f"unknown old-generation block id 0x{block_id:08x}")
        if block_id == FILE_DATA:
            if position + 4 > len(data):
                raise FormatError("truncated old-generation file-data block")
            stored_size = u32(data, position)
            available_size = min(stored_size, len(data) - (position + 4))
            if available_size != stored_size:
                issues.append(
                    "old-generation file-data payload is truncated: "
                    f"{available_size} of {stored_size} stored bytes are present"
                )
            if stored_size != size:
                issues.append(
                    "old-generation file-data payload is incomplete: "
                    f"header declares {size} bytes but only {stored_size} are stored"
                )
            decoded = data[position + 4:position + 4 + available_size]
            end = position + 4 + available_size
        else:
            end = position + size
            if end > len(data):
                raise FormatError(f"old-generation block 0x{block_id:08x} is truncated")
            payload = data[position:end]
            if block_id & 0x10000:
                if size < 4:
                    raise FormatError("compressed old-generation block has no decoded length")
                expected = u32(payload, 0)
                decoded, _ = decompress_clickteam(payload[4:], expected, sentinel=False)
            else:
                decoded = payload
        blocks.append({
            "id": block_id,
            "start": start,
            "physical_size": end - start,
            "declared_size": size,
            "logical_size": size if block_id == FILE_DATA else None,
            "raw": data[start:end],
            "decoded": decoded,
        })
        position = end
        if block_id == FILE_DATA:
            if position < len(data):
                if any(data[position:]):
                    issues.append("nonzero bytes follow the old-generation file-data block")
                trailing = data[position:]
                position = len(data)
            break
    if position != len(data) or not blocks or blocks[-1]["id"] != FILE_DATA:
        raise FormatError("old-generation container has no final file-data block")
    return generation_tag, initial, prefix, blocks, trailing


def old_path(raw: bytes, start: int, encoding: str) -> tuple[str, bytes]:
    if start >= len(raw):
        raise FormatError("old-generation file record has no path")
    return decode_install_path(raw[start:], encoding)


def old_time_path_candidates(node: bytes, start: int, encoding: str) -> list[tuple[int, list[int], str, bytes]]:
    matches = []
    for times_start in range(start, len(node) - 24):
        times = [u64(node, times_start + delta) for delta in (0, 8, 16)]
        if not all(valid_filetime(value) for value in times):
            continue
        try:
            path, suffix = old_path(node, times_start + 24, encoding)
        except FormatError:
            continue
        matches.append((times_start, times, path, suffix))
    return matches


def parse_install_maker(file_list: bytes, file_data: bytes, encoding: str,
                        issues: list[str] | None = None) -> list[dict]:
    issues = issues if issues is not None else []
    count = u32(file_list, 0)
    if count == 0 or count > 1_000_000:
        raise FormatError("invalid Install Maker file count")
    position = 4
    data_position = 0
    entries = []
    early_layout: bool | None = None
    unavailable = 0
    for index in range(count):
        size = u32(file_list, position)
        end = position + size
        if size < 24 or end > len(file_list):
            raise FormatError("Install Maker file node exceeds its boundary")
        node = file_list[position:end]
        kind = u16(node, 4)
        recoverable = True
        try:
            decoded, compressed = decompress_clickteam(
                file_data[data_position:], None, False, False)
            uncompressed = len(decoded)
        except FormatError:
            recoverable = False
            unavailable += 1
            if early_layout is None:
                raise FormatError("first Install Maker file stream is incomplete; node layout cannot be established")
            if early_layout:
                compressed = u32(node, 6)
                uncompressed = u32(node, 10)
            else:
                uncompressed = u32(node, 18)
                compressed = u32(node, 22)
        early_special = (index == 0 and recoverable and u32(node, 6) == compressed
                         and u32(node, 10) == uncompressed)
        if index == 0:
            early_layout = early_special
        if early_layout:
            if recoverable and (u32(node, 6) != compressed or u32(node, 10) != uncompressed):
                raise FormatError("early Install Maker stored lengths do not match its stream")
            candidates = old_time_path_candidates(node, 22, encoding)
        else:
            candidates = old_time_path_candidates(node, 26, encoding)
        special = index == 0 and not candidates
        if special and early_layout:
            path, suffix = old_path(node, 26, encoding)
            times = []
            attribute_vector = node[14:26]
        elif special:
            if recoverable and (u32(node, 18) != uncompressed or u32(node, 22) != compressed):
                raise FormatError("Install Maker uninstaller lengths do not match its stream")
            path, suffix = old_path(node, 26, encoding)
            times: list[int] = []
            attribute_vector = b""
        else:
            if (recoverable and not early_layout
                    and (u32(node, 18) != uncompressed or u32(node, 22) != compressed)):
                raise FormatError("Install Maker stored file lengths do not match its stream")
            if len(candidates) == 1:
                times_start, times, path, suffix = candidates[0]
                attributes_start = 22 if early_layout else 26
                attribute_vector = node[attributes_start:times_start]
            elif not candidates:
                boundaries = []
                attributes_start = 22 if early_layout else 26
                for path_start in range(attributes_start, len(node)):
                    if path_start > attributes_start and node[path_start - 1] != 0:
                        continue
                    try:
                        item_path, item_suffix = old_path(node, path_start, encoding)
                    except FormatError:
                        continue
                    boundaries.append((path_start, item_path, item_suffix))
                if u16(node, 10) == 0:
                    zero_suffix = [item for item in boundaries if not any(item[2])]
                    boundaries = zero_suffix or boundaries
                if not boundaries:
                    raise FormatError("Install Maker node has no path boundary")
                path_start, path, suffix = boundaries[0]
                times = []
                attribute_vector = node[attributes_start:path_start]
            else:
                raise FormatError("Install Maker node has ambiguous timestamp fields")
        entries.append({
            "node": index,
            "kind": kind,
            "node_start": position,
            "node_size": size,
            "node_raw": node,
            "path": path,
            "path_suffix_hex": suffix.hex(),
            "offset": data_position,
            "compressed_size": compressed,
            "uncompressed_size": uncompressed,
            "times": times,
            "empty": uncompressed == 0,
            "special_uninstaller": special,
            "attribute_vector_hex": attribute_vector.hex(),
            "old_compression": True,
            "recoverable": recoverable,
        })
        data_position += compressed
        position = end
    if position != len(file_list):
        raise FormatError("Install Maker file nodes do not consume the list exactly")
    if unavailable:
        issues.append(f"{unavailable} Install Maker file record(s) are incomplete or unavailable")
    elif data_position != len(file_data):
        raise FormatError("Install Maker file streams do not consume their block exactly")
    return entries


def parse_early_creator(file_list: bytes, file_data: bytes, encoding: str,
                        require_full_data: bool = True,
                        validate_streams: bool = True,
                        record_layout: str | None = None) -> list[dict]:
    if record_layout is None:
        candidates = []
        for candidate in ("standard", "extended", "compact"):
            try:
                candidates.append((candidate, parse_early_creator(
                    file_list, file_data, encoding, require_full_data,
                    validate_streams, candidate)))
            except FormatError:
                pass
        if not candidates:
            raise FormatError("unsupported early Install Creator file-node layout")
        if len(candidates) != 1:
            names = ", ".join(item[0] for item in candidates)
            raise FormatError(f"ambiguous early Install Creator node layout ({names})")
        return candidates[0][1]
    if record_layout not in ("standard", "extended", "compact"):
        raise FormatError("unknown early Install Creator node layout")
    count = u32(file_list, 0)
    if count == 0 or count > 1_000_000:
        raise FormatError("invalid early Install Creator file count")
    position = 4
    entries = []
    ranges = []
    for index in range(count):
        size = u32(file_list, position)
        end = position + size
        if size < 34 or end > len(file_list):
            raise FormatError("early Install Creator file node exceeds its boundary")
        node = file_list[position:end]
        kind = u16(node, 4)
        if record_layout == "extended":
            uncompressed = u32(node, 20)
            offset = u32(node, 24)
            compressed = u32(node, 28)
            fixed_end = 32
        elif record_layout == "compact":
            uncompressed = u32(node, 18)
            offset = u32(node, 22)
            compressed = u32(node, 26)
            fixed_end = 30
        else:
            offset, compressed, uncompressed = struct.unpack_from("<III", node, 6)
            fixed_end = 18
        if (record_layout == "extended" and size >= 62 and u32(node, 6) == 0
                and u32(node, 24) == 0 and u32(node, 28) == len(file_data)):
            uncompressed = u32(node, 20)
        if compressed == 0 or offset + compressed > len(file_data):
            raise FormatError("early Install Creator file-data range is invalid")
        decoded_size = None
        if validate_streams:
            decoded, used = decompress_clickteam(file_data[offset:offset + compressed], uncompressed,
                                                 sentinel=False)
            if used != compressed:
                raise FormatError("early Install Creator stream length disagrees with its node")
            decoded_size = len(decoded)
        matches = old_time_path_candidates(node, fixed_end, encoding)
        special = index == 0 and not matches
        if not matches:
            if record_layout == "compact" and node[30:36] == b"\0" * 6:
                path_start = 36
            else:
                path_start = {"standard": 36, "extended": 38, "compact": 32}[record_layout]
            if path_start >= len(node):
                raise FormatError("early Install Creator node has no fixed no-time path field")
            path, suffix = old_path(node, path_start, encoding)
            times: list[int] = []
            attributes = node[fixed_end:path_start]
        else:
            if len(matches) != 1:
                raise FormatError("early Install Creator node has no unique attribute/time/path boundary")
            times_start, times, path, suffix = matches[0]
            attributes = node[fixed_end:times_start]
        entries.append({
            "node": index,
            "kind": kind,
            "node_start": position,
            "node_size": size,
            "node_raw": node,
            "path": path,
            "path_suffix_hex": suffix.hex(),
            "offset": offset,
            "compressed_size": compressed,
            "uncompressed_size": uncompressed,
            "times": times,
            "empty": uncompressed == 0,
            "special_uninstaller": special,
            "attribute_vector_hex": attributes.hex(),
            "old_compression": True,
            "decoded_check": decoded_size,
        })
        ranges.append((offset, offset + compressed))
        position = end
    if position != len(file_list):
        raise FormatError("early Install Creator nodes do not consume the list exactly")
    if require_full_data:
        ordered = sorted(set(ranges))
        if any(left[1] != right[0] for left, right in zip(ordered, ordered[1:])):
            raise FormatError("early Install Creator product streams are not contiguous")
        if not ordered or ordered[0][0] != 0 or ordered[-1][1] != len(file_data):
            raise FormatError("early Install Creator streams do not tile the data block")
    return entries


def validate_shared_old_ranges(products: list[dict], file_data: bytes) -> None:
    """Validate a shared old-generation pool without assuming product ordering."""
    unique = sorted({(entry["offset"], entry["offset"] + entry["compressed_size"])
                     for product in products for entry in product["entries"]})
    if not unique or unique[0][0] != 0 or unique[-1][1] != len(file_data):
        raise FormatError("multi-product streams do not tile the shared data block")
    for left, right in zip(unique, unique[1:]):
        if left[1] != right[0]:
            relation = "overlap" if right[0] < left[1] else "gap"
            raise FormatError(f"multi-product shared data ranges have a {relation}")


def clickteam_crypt(data: bytes, key: bytes) -> bytes:
    """Apply the symmetric early-Clickteam per-record stream cipher."""
    if not 1 <= len(key) <= 31:
        raise FormatError("early Clickteam cipher key length is outside 1..31")
    state = bytearray(key)
    position = 0
    addend = 0x39
    output = bytearray(len(data))
    for offset, value in enumerate(data):
        stream = state[position] ^ addend
        output[offset] = value ^ stream
        addend = (addend + 5) & 0xFF
        state[position] = ((stream << 1) | (stream >> 7)) & 0xFF
        position = (position + 1) % len(state)
    return bytes(output)


def recover_clickteam_key(ciphertext: bytes, plaintext: bytes) -> bytes | None:
    """Recover a key only when a complete known stream proves it uniquely."""
    if len(ciphertext) != len(plaintext):
        return None
    stream = bytes(left ^ right for left, right in zip(ciphertext, plaintext))
    matches = []
    for length in range(1, min(31, len(stream)) + 1):
        key = bytes(stream[index] ^ ((0x39 + 5 * index) & 0xFF)
                    for index in range(length))
        if clickteam_crypt(plaintext, key) == ciphertext:
            matches.append(key)
    return matches[0] if len(matches) == 1 else None


def try_old_stream(record: bytes, expected: int) -> bool:
    try:
        decoded, used = decompress_clickteam(record, expected, sentinel=False)
        return used == len(record) and len(decoded) == expected
    except FormatError:
        return False


def patch_section(data: bytes, position: int) -> tuple[bytes, int]:
    if position >= len(data):
        raise FormatError("truncated old-generation delta section")
    flags = data[position]
    position += 1
    if flags & ~7:
        raise FormatError("old-generation delta section has unknown flags")
    size_width = 4 if flags & 2 else 2
    if position + size_width > len(data):
        raise FormatError("truncated old-generation delta decoded size")
    decoded_size = int.from_bytes(data[position:position + size_width], "little")
    position += size_width
    if flags & 1:
        compressed_width = 4 if flags & 4 else 2
        if position + compressed_width > len(data):
            raise FormatError("truncated old-generation delta compressed size")
        compressed_size = int.from_bytes(data[position:position + compressed_width], "little")
        position += compressed_width
        end = position + compressed_size
        if end > len(data):
            raise FormatError("old-generation delta section exceeds its record")
        decoded, used = decompress_clickteam(data[position:end], decoded_size, sentinel=False)
        if used != compressed_size:
            raise FormatError("old-generation delta section stream has trailing bytes")
        return decoded, end
    end = position + decoded_size
    if end > len(data):
        raise FormatError("stored old-generation delta section exceeds its record")
    return data[position:end], end


def signed_bits(value: int, width: int) -> int:
    return value - (1 << width) if value & (1 << (width - 1)) else value


def validate_patch_program(commands: bytes, literals: bytes,
                           expected_size: int) -> tuple[int, int]:
    command_at = 0
    literal_at = 0
    output_size = 0
    source_at = 0
    source_min = 0
    source_max = 0

    def command_byte() -> int:
        nonlocal command_at
        if command_at >= len(commands):
            raise FormatError("truncated old-generation delta command")
        value = commands[command_at]
        command_at += 1
        return value

    while output_size < expected_size:
        opcode = command_byte()
        if opcode & 0x80:
            mode = (opcode >> 5) & 3
            if mode == 0:
                literal_size = (opcode & 0x1F) + 1
                copy_size = 0
            else:
                literal_size = mode
                copy_size = (opcode & 0x1F) + 2
        else:
            literal_size = 0
            if opcode:
                copy_size = opcode + 1
            else:
                low = command_byte()
                copy_size = (low | command_byte() << 8) + 0x81
        if literal_at + literal_size > len(literals):
            raise FormatError("old-generation delta consumes beyond its literal stream")
        literal_at += literal_size
        output_size += literal_size
        if copy_size:
            first = command_byte()
            if first & 0x80:
                if first & 0x40:
                    encoded = ((first & 0x3F) << 16) | (command_byte() << 8) | command_byte()
                    if encoded == 0x100000:
                        encoded = ((command_byte() << 24) | (command_byte() << 16) |
                                   (command_byte() << 8) | command_byte())
                        delta = signed_bits(encoded, 32)
                    else:
                        delta = signed_bits(encoded, 22)
                    delta += 0x4020 if delta >= 0 else -0x4020
                else:
                    delta = signed_bits(first & 0x3F, 6)
            else:
                delta = signed_bits(((first & 0x7F) << 8) | command_byte(), 15)
                delta += 0x20 if delta >= 0 else -0x20
            source_at += delta
            if source_at < 0:
                raise FormatError("old-generation delta references before its base file")
            source_min = min(source_min, source_at)
            source_max = max(source_max, source_at + copy_size)
            source_at += copy_size
            output_size += copy_size
        if output_size > expected_size:
            raise FormatError("old-generation delta produces beyond its declared output")
    if command_at != len(commands) or literal_at != len(literals):
        raise FormatError("old-generation delta does not consume both sections exactly")
    return source_min, source_max


def validate_old_multi_payloads(products: list[dict], file_data: bytes,
                                skip_deltas: bool = False,
                                issues: list[str] | None = None) -> list[int]:
    """Resolve encrypted records, validate deltas, and return dependent products."""
    issues = issues if issues is not None else []
    unavailable = 0
    plain_by_identity: dict[tuple[str, int, int], list[bytes]] = {}
    for product in products:
        for entry in product["entries"]:
            if entry["empty"] or entry["special_uninstaller"]:
                continue
            start = entry["offset"]
            record = file_data[start:start + entry["compressed_size"]]
            is_delta = len(entry["node_raw"]) > 22 and bool(entry["node_raw"][22] & 0x10)
            entry["old_delta"] = is_delta
            if not is_delta and try_old_stream(record, entry["uncompressed_size"]):
                identity = (entry["path"].casefold(), entry["compressed_size"],
                            entry["uncompressed_size"])
                plain_by_identity.setdefault(identity, []).append(record)
                entry["decoded_check"] = entry["uncompressed_size"]

    for product in products:
        candidates: set[bytes] = set()
        for entry in product["entries"]:
            if entry["empty"] or entry["special_uninstaller"] or entry.get("old_delta"):
                continue
            start = entry["offset"]
            record = file_data[start:start + entry["compressed_size"]]
            if try_old_stream(record, entry["uncompressed_size"]):
                continue
            identity = (entry["path"].casefold(), entry["compressed_size"],
                        entry["uncompressed_size"])
            for plaintext in plain_by_identity.get(identity, []):
                key = recover_clickteam_key(record, plaintext)
                if key is not None:
                    candidates.add(key)
        valid_keys = []
        for key in candidates:
            valid = True
            for entry in product["entries"]:
                if entry["empty"] or entry["special_uninstaller"] or entry.get("old_delta"):
                    continue
                start = entry["offset"]
                record = file_data[start:start + entry["compressed_size"]]
                if (not try_old_stream(record, entry["uncompressed_size"])
                        and not try_old_stream(clickteam_crypt(record, key), entry["uncompressed_size"])):
                    valid = False
                    break
            if valid:
                valid_keys.append(key)
        key = valid_keys[0] if len(valid_keys) == 1 else None
        for entry in product["entries"]:
            if entry["empty"] or entry["special_uninstaller"]:
                continue
            start = entry["offset"]
            record = file_data[start:start + entry["compressed_size"]]
            if not entry.get("old_delta"):
                if try_old_stream(record, entry["uncompressed_size"]):
                    continue
                if key is None or not try_old_stream(clickteam_crypt(record, key),
                                                     entry["uncompressed_size"]):
                    entry["recoverable"] = False
                    unavailable += 1
                    continue
                entry["old_cipher_key_hex"] = key.hex()
                entry["decoded_check"] = entry["uncompressed_size"]
            else:
                if skip_deltas:
                    continue
                variants = [(None, record)]
                if key is not None:
                    variants.append((key, clickteam_crypt(record, key)))
                parsed = []
                for variant_key, variant in variants:
                    try:
                        commands, at = patch_section(variant, 0)
                        literals, at = patch_section(variant, at)
                        if at != len(variant):
                            raise FormatError("bytes follow old-generation delta sections")
                        source_range = validate_patch_program(commands, literals,
                                                              entry["uncompressed_size"])
                        parsed.append((variant_key, source_range))
                    except FormatError:
                        pass
                if len(parsed) != 1:
                    raise FormatError("old-generation delta record has no unique valid decoding")
                variant_key, source_range = parsed[0]
                if variant_key is not None:
                    entry["old_cipher_key_hex"] = variant_key.hex()
                entry["delta_source_range"] = list(source_range)
    if unavailable:
        issues.append(
            f"{unavailable} encrypted early multi-product file record(s) have no provable cipher key"
        )
    return sorted({product["index"] for product in products
                   if any(entry.get("old_delta") for entry in product["entries"])})


def valid_filetime(value: int) -> bool:
    return value == 0 or 116_444_736_000_000_000 <= value <= FILETIME_MAX


def filetime_to_timestamp(value: int) -> float | None:
    if value == 0:
        return None
    return (value - 116_444_736_000_000_000) / 10_000_000


def decode_install_path(raw: bytes, encoding: str = "cp1252") -> tuple[str, bytes]:
    terminator = raw.find(b"\0")
    if terminator <= 0 or raw[-1:] != b"\0":
        raise FormatError("file record has no valid NUL-terminated path field")
    path_bytes = raw[:terminator]
    try:
        path = path_bytes.decode(encoding)
    except UnicodeDecodeError as exc:
        raise FormatError(f"file path is not valid {encoding} text") from exc
    if any(ord(char) < 32 for char in path):
        raise FormatError("file path contains control bytes")
    windows = PureWindowsPath(path)
    if windows.is_absolute() or windows.drive or any(part in ("", ".", "..") for part in windows.parts):
        raise FormatError(f"unsafe installer path {path!r}")
    if ":" in path or "/" in path:
        raise FormatError(f"non-relative Windows installer path {path!r}")
    return path, raw[terminator + 1:]


def parse_candidate(file_list: bytes, data_size: int, layout: int, encoding: str = "cp1252") -> list[dict]:
    count = u16(file_list, 0)
    if u16(file_list, 2) != 0:
        raise FormatError("file-list reserved field is not zero")
    position = 4
    entries: list[dict] = []
    file_index = 0
    for node_index in range(count):
        start = position
        if layout in (20, 35, 40):
            size = u32(file_list, position)
            kind = u16(file_list, position + 4)
            position += 6
            minimum = 6
        else:
            size = u16(file_list, position)
            kind = u16(file_list, position + 2)
            position += 4
            minimum = 4
        end = start + size
        if size < minimum or end > len(file_list):
            raise FormatError("file-list node exceeds its declared boundary")
        entry = {
            "node": node_index,
            "kind": kind,
            "node_start": start,
            "node_size": size,
            "node_raw": file_list[start:end],
            "path": None,
        }
        if kind not in (0, 1):
            entries.append(entry)
            position = end
            continue

        file_index += 1
        empty = False
        stored_index = None
        if layout == 20:
            marker = file_list[start + 9]
            if marker == 0xE2:
                uncompressed = offset = compressed = 0
                empty = True
                position = start + 32
            else:
                position += 14
                uncompressed = u32(file_list, position)
                offset = u32(file_list, position + 4)
                compressed = u32(file_list, position + 8)
                position += 12
        elif layout == 24:
            position += 2
            offset = u32(file_list, position)
            compressed = u32(file_list, position + 4)
            entry["unknown32"] = u32(file_list, position + 8)
            uncompressed = u32(file_list, position + 12)
            position += 32
        elif layout == 30:
            position += 2
            offset = u32(file_list, position)
            compressed = u32(file_list, position + 4)
            entry["unknown32"] = u32(file_list, position + 8)
            uncompressed = u32(file_list, position + 12)
            position += 34
            stored_index = u32(file_list, position)
            position += 4
            if stored_index > count:
                raise FormatError("layout-30 file index exceeds the node count")
        elif layout == 35:
            position += 3
            marker = file_list[position]
            position += 1 + (30 if marker == 0xE2 else 14)
            uncompressed = u32(file_list, position)
            offset = u32(file_list, position + 4)
            compressed = u32(file_list, position + 8)
            entry["unknown32"] = u32(file_list, position + 12)
            stored_index = u32(file_list, position + 16)
            position += 22
            if stored_index > count:
                raise FormatError("layout-35 file index exceeds the node count")
        else:
            position += 3
            marker = file_list[position]
            position += 1
            if marker == 0xE2:
                position += 30
                uncompressed = offset = compressed = 0
                empty = True
            else:
                position += 14
                uncompressed = u32(file_list, position)
                offset = u32(file_list, position + 4)
                compressed = u32(file_list, position + 8)
                entry["unknown32"] = u32(file_list, position + 12)
                position += 16

        times: list[int] = []
        if not empty:
            for delta in (0, 8, 16):
                value = u64(file_list, position + delta)
                if not valid_filetime(value):
                    raise FormatError("file record contains an invalid Windows FILETIME")
                times.append(value)
            position += 24
        if position > end:
            raise FormatError("fixed file fields exceed the node boundary")
        path, suffix = decode_install_path(file_list[position:end], encoding)
        if offset + compressed > data_size:
            raise FormatError("file data range exceeds the data block")
        if empty:
            if uncompressed or compressed:
                raise FormatError("empty-file record has nonzero lengths")
        elif compressed < 1:
            raise FormatError("nonempty file has no compressed record")
        entry.update({
            "path": path,
            "path_suffix_hex": suffix.hex(),
            "offset": offset,
            "compressed_size": compressed,
            "uncompressed_size": uncompressed,
            "times": times,
            "stored_index": stored_index,
            "empty": empty,
        })
        entries.append(entry)
        position = end
    if position != len(file_list):
        raise FormatError("file-list records do not consume the decoded block exactly")
    return entries


def choose_layout(file_list: bytes, file_data: bytes, encoding: str = "cp1252",
                  declared_data_size: int | None = None) -> tuple[int, list[dict]]:
    data_size = len(file_data) if declared_data_size is None else declared_data_size
    candidates: list[tuple[int, list[dict]]] = []
    for layout in KNOWN_LAYOUTS:
        try:
            candidates.append((layout, parse_candidate(file_list, data_size, layout, encoding)))
        except FormatError:
            pass
    if not candidates:
        flexible: list[tuple[int, list[dict]]] = []
        for layout in (17, 21, 25, 26):
            try:
                if data_size != len(file_data):
                    raise FormatError("cannot validate a flexible layout against a truncated data pool")
                flexible.append((layout, parse_flexible_candidate(
                    file_list, file_data, layout, encoding, validate_streams=True)))
            except FormatError:
                pass
        candidates = flexible
    if not candidates and data_size == len(file_data):
        structural: list[tuple[int, list[dict]]] = []
        for layout in (17, 21, 25, 26):
            try:
                structural.append((layout, parse_flexible_candidate(
                    file_list, file_data, layout, encoding, validate_streams=False)))
            except FormatError:
                pass
        candidates = structural
    if not candidates:
        raise FormatError("unsupported file-list record layout")
    if len(candidates) != 1:
        versions = ", ".join(str(item[0]) for item in candidates)
        raise FormatError(f"ambiguous file-list grammar ({versions}); refusing to guess")
    return candidates[0]


def parse_flexible_candidate(file_list: bytes, file_data: bytes, layout: int,
                             encoding: str = "cp1252",
                             validate_streams: bool = True) -> list[dict]:
    """Parse early/extended records whose attribute vector precedes three FILETIMEs."""
    count = u16(file_list, 0)
    if u16(file_list, 2) != 0:
        raise FormatError("file-list reserved field is not zero")
    wide = layout in (21, 26)
    position = 4
    entries: list[dict] = []
    for node_index in range(count):
        start = position
        if wide:
            size = u32(file_list, position)
            kind = u16(file_list, position + 4)
            position += 6
        else:
            size = u16(file_list, position)
            kind = u16(file_list, position + 2)
            position += 4
        end = start + size
        if size < (6 if wide else 4) or end > len(file_list):
            raise FormatError("flexible file-list node exceeds its boundary")
        entry = {
            "node": node_index,
            "kind": kind,
            "node_start": start,
            "node_size": size,
            "node_raw": file_list[start:end],
            "path": None,
        }
        if kind not in (0, 1):
            entries.append(entry)
            position = end
            continue

        if layout == 21:
            core = start + 20
            uncompressed = u32(file_list, core)
            offset = u32(file_list, core + 4)
            compressed = u32(file_list, core + 8)
            attributes_start = core + 12
        elif layout == 26:
            core = start + 24
            uncompressed = u32(file_list, core)
            offset = u32(file_list, core + 4)
            compressed = u32(file_list, core + 8)
            attributes_start = core + 12
        elif layout == 25:
            core = start + 6
            offset = u32(file_list, core)
            compressed = u32(file_list, core + 4)
            entry["unknown32"] = u32(file_list, core + 8)
            if entry["unknown32"] != 0:
                raise FormatError("layout-25 reserved field is not zero")
            uncompressed = u32(file_list, core + 12)
            attributes_start = core + 16
        else:
            core = start + 6
            offset = u32(file_list, core)
            compressed = u32(file_list, core + 4)
            uncompressed = u32(file_list, core + 8)
            entry["unknown32"] = u32(file_list, core + 12)
            attributes_start = core + 16
        external = (layout == 25 and offset == 0xFFFFFFFF and compressed == 0
                    and entry.get("unknown32") == 0)
        empty = offset == 0 and compressed == 0 and uncompressed == 0
        if ((not external and offset + compressed > len(file_data))
                or (compressed < 1 and not (empty or external))):
            raise FormatError("flexible record has an invalid data range")
        if not (empty or external) and uncompressed == 0 and compressed != 1:
            raise FormatError("zero-length flexible record is not the one-byte empty encoding")
        if validate_streams and not (empty or external):
            record = file_data[offset:offset + compressed]
            if kind == 1:
                validate_modern_delta(record, uncompressed)
            elif uncompressed:
                decompress_file_record(record, uncompressed)

        matches = []
        for times_start in range(attributes_start, end - 24):
            times = [u64(file_list, times_start + delta) for delta in (0, 8, 16)]
            if not all(valid_filetime(value) for value in times):
                continue
            for padding in (0, 1, 2):
                path_start = times_start + 24 + padding
                if path_start >= end or any(file_list[times_start + 24:path_start]):
                    continue
                try:
                    path, suffix = decode_install_path(file_list[path_start:end], encoding)
                except FormatError:
                    continue
                matches.append((times_start, padding, times, path, suffix))
        if len(matches) == 1:
            times_start, padding, times, path, suffix = matches[0]
            attributes_end = times_start
        elif not matches:
            fixed_path_start = None
            if layout == 17 and file_list[attributes_start:attributes_start + 8] == b"\0\xe0\x07\0\0\0\0\0":
                fixed_path_start = attributes_start + 8
            elif (layout == 17 and empty
                  and file_list[attributes_start:attributes_start + 14]
                  == b"\xe2\x07" + b"\0" * 12):
                fixed_path_start = attributes_start + 14
            elif layout == 25 and empty:
                fixed_path_start = attributes_start + 22
            elif layout == 26:
                fixed_path_start = attributes_start + 4
            boundaries = ([fixed_path_start] if fixed_path_start is not None
                          else range(attributes_start, end))
            path_matches = []
            for path_start in boundaries:
                if (fixed_path_start is None and path_start > attributes_start
                        and file_list[path_start - 1] != 0):
                    continue
                try:
                    path, suffix = decode_install_path(file_list[path_start:end], encoding)
                except FormatError:
                    continue
                path_matches.append((path_start, path, suffix))
            if len(path_matches) != 1:
                raise FormatError("extended attribute vector has no unique path boundary")
            path_start, path, suffix = path_matches[0]
            times = []
            padding = 0
            attributes_end = path_start
        else:
            raise FormatError("extended attribute vector has ambiguous timestamp/path boundaries")
        entry.update({
            "path": path,
            "path_suffix_hex": suffix.hex(),
            "offset": offset,
            "compressed_size": compressed,
            "uncompressed_size": uncompressed,
            "times": times,
            "stored_index": None,
            "empty": empty,
            "external": external,
            "recoverable": not external,
            "attribute_vector_hex": file_list[attributes_start:attributes_end].hex(),
            "path_padding": padding,
        })
        entries.append(entry)
        position = end
    if position != len(file_list):
        raise FormatError("flexible records do not consume the decoded block exactly")
    return entries


def validate_ranges(entries: list[dict], file_data: bytes,
                    issues: list[str] | None = None) -> dict[int, int]:
    issues = issues if issues is not None else []
    ranges: list[tuple[int, int, str]] = []
    methods: dict[int | str, int] = {0: 0, 1: 0, 2: 0, "zlib-implicit": 0}
    unavailable = 0
    deltas = 0
    for entry in entries:
        if entry["kind"] not in (0, 1) or entry["empty"] or entry["uncompressed_size"] == 0:
            continue
        if entry.get("external"):
            entry["recoverable"] = False
            unavailable += 1
            continue
        start = entry["offset"]
        end = start + entry["compressed_size"]
        ranges.append((start, end, entry["path"]))
        if end > len(file_data):
            entry["recoverable"] = False
            unavailable += 1
            continue
        try:
            if entry["kind"] == 1:
                source_range = validate_modern_delta(
                    file_data[start:end], entry["uncompressed_size"])
                entry["modern_delta"] = True
                entry["delta_source_range"] = list(source_range)
                entry["recoverable"] = False
                deltas += 1
                continue
            _, method = decompress_file_record(
                file_data[start:end], entry["uncompressed_size"])
        except FormatError:
            entry["recoverable"] = False
            unavailable += 1
            continue
        entry["recoverable"] = True
        methods[method] += 1
    ranges.sort()
    for previous, current in zip(ranges, ranges[1:]):
        if current[0] < previous[1] and current[:2] != previous[:2]:
            raise FormatError(f"overlapping file-data records {previous[2]!r} and {current[2]!r}")
    if unavailable:
        issues.append(f"{unavailable} installed-file record(s) are incomplete or fail exact decompression")
    if deltas:
        issues.append(
            f"{deltas} binary-delta file record(s) require exact pre-existing destination files"
        )
    return methods


def product_directory(index: int) -> str:
    return f"product_{index:03d}"


def validate_product_paths(entries: list[dict], old_generation: bool) -> None:
    paths = [entry["path"].casefold() for entry in entries
             if ((old_generation or entry["kind"] == 0) and entry.get("extract", True)
                 and entry.get("recoverable", True))]
    if not old_generation and len(paths) != len(set(paths)):
        raise FormatError("duplicate case-insensitive output paths are not supported")


def parse_installer(input_path: Path, encoding: str = "cp1252") -> dict:
    data = input_path.read_bytes()
    overlay = pe_overlay_offset(data)
    issues: list[str] = []
    if data[overlay:overlay + len(MAGIC)] != MAGIC:
        if u32(data, overlay) == 0x11241:
            raise FormatError("Clickteam Patch Maker package requires original target files; it is not a self-contained installer")
        generation_tag, initial, prefix, blocks, trailing = parse_old_blocks(data, overlay, issues)
        expected_list = 0x11243 if generation_tag == 0x11242 else 0x1123A
        lists = [block for block in blocks if block["id"] == expected_list]
        file_blocks = [block for block in blocks if block["id"] == FILE_DATA]
        if not lists or len(file_blocks) != 1:
            raise FormatError("old-generation container has no unique file-data block")
        file_data = file_blocks[0]["decoded"]
        products = []
        if generation_tag == 0x11242:
            if len(lists) != 1:
                raise FormatError("multi-product Install Maker layout is unsupported")
            entries = parse_install_maker(lists[0]["decoded"], file_data, encoding, issues)
            layout = "install-maker"
            products.append({"index": 0, "directory": product_directory(0),
                             "layout": layout, "entries": entries})
        else:
            layout = "early-install-creator"
            if not file_data:
                external_nodes = []
                found_external = False
                for item in lists:
                    decoded = item["decoded"]
                    position = 4
                    for _ in range(u32(decoded, 0)):
                        size = u32(decoded, position)
                        node = decoded[position:position + size]
                        if size < 32 or position + size > len(decoded):
                            external_nodes = []
                            break
                        external = (u32(node, 20) > 0
                                    and u32(node, 24) == 0xFFFFFFFF
                                    and u32(node, 28) == 0)
                        empty = (u32(node, 20) == 0 and u32(node, 24) == 0
                                 and u32(node, 28) == 0)
                        external_nodes.append(external or empty)
                        found_external |= external
                        position += size
                if found_external and external_nodes and all(external_nodes):
                    raise FormatError(
                        "early Clickteam container references external source files "
                        "that are not embedded in the executable"
                    )
            if len(lists) == 1:
                entries = parse_early_creator(lists[0]["decoded"], file_data, encoding)
                for entry in entries:
                    entry["extract"] = not entry["special_uninstaller"]
                products.append({"index": 0, "directory": product_directory(0),
                                 "layout": layout, "entries": entries})
            else:
                variants = []
                for record_layout in ("standard", "extended", "compact"):
                    candidate_products = []
                    try:
                        for index, item in enumerate(lists):
                            entries = parse_early_creator(
                                item["decoded"], file_data, encoding,
                                require_full_data=False, validate_streams=False,
                                record_layout=record_layout)
                            for entry in entries:
                                entry["extract"] = not entry["special_uninstaller"]
                            candidate_products.append({
                                "index": index,
                                "directory": product_directory(index),
                                "layout": layout,
                                "entries": entries,
                            })
                        validate_shared_old_ranges(candidate_products, file_data)
                        variants.append((record_layout, candidate_products))
                    except FormatError:
                        pass
                if not variants:
                    raise FormatError("unsupported early multi-product file-node layout")
                if len(variants) != 1:
                    names = ", ".join(item[0] for item in variants)
                    raise FormatError(f"ambiguous early multi-product node layout ({names})")
                _, products = variants[0]
                delta_products = sorted({
                    product["index"] for product in products
                    if any(len(entry["node_raw"]) > 22 and entry["node_raw"][22] & 0x10
                           for entry in product["entries"])
                })
                if delta_products:
                    labels = ", ".join(product_directory(index) for index in delta_products)
                    skipped = 0
                    for product in products:
                        for entry in product["entries"]:
                            if (len(entry["node_raw"]) > 22
                                    and entry["node_raw"][22] & 0x10):
                                entry["recoverable"] = False
                                skipped += 1
                    issues.append(
                        f"{skipped} binary-delta file(s) in {labels} require an exact "
                        "pre-existing installed base file"
                    )
                validate_old_multi_payloads(
                    products, file_data, skip_deltas=True, issues=issues)
        entries = [entry for product in products for entry in product["entries"]]
        for product in products:
            validate_product_paths(product["entries"], True)
        return {
            "input": input_path,
            "data": data,
            "overlay": overlay,
            "blocks": blocks,
            "file_data": file_data,
            "layout": layout,
            "entries": entries,
            "products": products,
            "methods": {"clickteam-deflate": len(entries)},
            "encoding": encoding,
            "generation_tag": generation_tag,
            "initial_decoded": initial,
            "old_prefix": prefix,
            "trailing_padding": trailing,
            "old_generation": True,
            "issues": issues,
        }
    blocks = parse_blocks(data, overlay, issues)
    lists = [block for block in blocks if block["id"] == FILE_LIST]
    file_blocks = [block for block in blocks if block["id"] == FILE_DATA]
    if not lists or len(file_blocks) != 1:
        raise FormatError("container has no unique file-data block")
    file_data = file_blocks[0]["decoded"]
    declared_data_size = file_blocks[0]["declared_size"]
    products = []
    methods: dict[int | str, int] = {0: 0, 1: 0, 2: 0, "zlib-implicit": 0}
    for index, item in enumerate(lists):
        layout, product_entries = choose_layout(
            item["decoded"], file_data, encoding, declared_data_size)
        product_methods = validate_ranges(product_entries, file_data, issues)
        for method, count in product_methods.items():
            methods[method] += count
        validate_product_paths(product_entries, False)
        products.append({"index": index, "directory": product_directory(index),
                         "layout": layout, "entries": product_entries})
    entries = [entry for product in products for entry in product["entries"]]
    layouts = [product["layout"] for product in products]
    layout = layouts[0] if len(set(layouts)) == 1 else "+".join(str(item) for item in layouts)
    return {
        "input": input_path,
        "data": data,
        "overlay": overlay,
        "blocks": blocks,
        "file_data": file_data,
        "layout": layout,
        "entries": entries,
        "products": products,
        "methods": methods,
        "encoding": encoding,
        "old_generation": False,
        "issues": issues,
    }


def local_path(root: Path, installer_path: str) -> Path:
    return root.joinpath(*PureWindowsPath(installer_path).parts)


def write_decoded_file(path: Path, method: int, payload: bytes, expected: int) -> None:
    decoded = decompress_exact(method, payload, expected)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(decoded)
    path.chmod(0o664)


def extract_product(parsed: dict, product: dict, root: Path, report_prefix: str) -> list[dict]:
    extracted: list[dict] = []
    extracted_index: dict[str, int] = {}
    targets: dict[str, Path] = {}
    file_data: bytes = parsed["file_data"]
    for entry in product["entries"]:
        if (entry["kind"] not in (0, 1) and not parsed.get("old_generation")) or not entry.get("extract", True):
            continue
        if not entry.get("recoverable", True):
            continue
        key = entry["path"].casefold()
        target = targets.setdefault(key, local_path(root, entry["path"]))
        target.parent.mkdir(parents=True, exist_ok=True)
        if entry["empty"] or entry["uncompressed_size"] == 0:
            target.write_bytes(b"")
            method = None
        elif entry.get("old_compression"):
            start = entry["offset"]
            record = file_data[start:start + entry["compressed_size"]]
            if entry.get("old_cipher_key_hex"):
                record = clickteam_crypt(record, bytes.fromhex(entry["old_cipher_key_hex"]))
            content, used = decompress_clickteam(record, entry["uncompressed_size"], sentinel=False)
            if used != len(record):
                raise FormatError("old-generation file stream does not end at its declared boundary")
            target.write_bytes(content)
            method = "clickteam-deflate"
        else:
            start = entry["offset"]
            record = file_data[start:start + entry["compressed_size"]]
            content, method = decompress_file_record(record, entry["uncompressed_size"])
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        target.chmod(0o664)
        modified = filetime_to_timestamp(entry["times"][0]) if entry["times"] else None
        accessed = filetime_to_timestamp(entry["times"][1]) if entry["times"] else None
        if modified is not None:
            os.utime(target, (accessed if accessed is not None else modified, modified))
        row = {
            "path": report_prefix + entry["path"],
            "size": target.stat().st_size,
            "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
            "compression": method,
        }
        if key in extracted_index:
            extracted[extracted_index[key]] = row
        else:
            extracted_index[key] = len(extracted)
            extracted.append(row)
    return extracted


def stage_extraction(parsed: dict, staging: Path, include_all: bool) -> list[dict]:
    extracted: list[dict] = []
    products = parsed.get("products") or [{
        "index": 0,
        "directory": product_directory(0),
        "layout": parsed["layout"],
        "entries": parsed["entries"],
    }]
    multiple = len(products) > 1
    for product in products:
        if multiple:
            directory = product["directory"]
            root = staging / directory
            prefix = directory + "/"
        else:
            root = staging
            prefix = ""
        extracted.extend(extract_product(parsed, product, root, prefix))

    if include_all:
        metadata = staging / "_clickteam_metadata"
        if metadata.exists():
            raise FormatError("installer path collides with the --all metadata directory")
        metadata.mkdir(parents=True)
        (metadata / "pe_stub.bin").write_bytes(parsed["data"][:parsed["overlay"]])
        (metadata / "overlay.bin").write_bytes(parsed["data"][parsed["overlay"]:])
        block_rows = []
        for index, block in enumerate(parsed["blocks"]):
            name = BLOCK_NAMES.get(block["id"], f"block_{block['id']:04x}")
            raw_name = f"{index:02d}_{block['id']:04x}_{name}.raw"
            decoded_name = f"{index:02d}_{block['id']:04x}_{name}.decoded"
            (metadata / raw_name).write_bytes(block["raw"])
            if block["id"] != FILE_DATA:
                (metadata / decoded_name).write_bytes(block["decoded"])
            block_rows.append({key: value for key, value in block.items() if key not in ("raw", "decoded")})
        manifest_entries = []
        for entry in parsed["entries"]:
            row = {key: value for key, value in entry.items() if key != "node_raw"}
            row["node_raw_hex"] = entry["node_raw"].hex()
            manifest_entries.append(row)
        manifest = {
            "input_name": parsed["input"].name,
            "input_size": len(parsed["data"]),
            "input_sha256": hashlib.sha256(parsed["data"]).hexdigest(),
            "pe_stub_size": parsed["overlay"],
            "layout": parsed["layout"],
            "products": [{
                "index": product["index"],
                "directory": product["directory"] if len(products) > 1 else ".",
                "layout": product["layout"],
                "entry_count": len(product["entries"]),
            } for product in products],
            "path_encoding": parsed["encoding"],
            "blocks": block_rows,
            "entries": manifest_entries,
            "extracted": extracted,
            "issues": parsed.get("issues", []),
        }
        if parsed.get("old_generation"):
            manifest.update({
                "generation_tag": parsed["generation_tag"],
                "initial_decoded_hex": parsed["initial_decoded"].hex(),
                "old_prefix": list(parsed["old_prefix"]),
                "trailing_padding_hex": parsed["trailing_padding"].hex(),
            })
        (metadata / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        for item in metadata.iterdir():
            item.chmod(0o664)
    return extracted


def merge_staging(staging: Path, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    output.chmod(0o775)
    for source in staging.rglob("*"):
        relative = source.relative_to(staging)
        target = output / relative
        if source.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            target.chmod(0o775)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            target.chmod(0o664)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract complete recoverable files from a supported Clickteam installer executable")
    parser.add_argument("--all", action="store_true", help="also dump embedded resources, raw blocks, and generated metadata")
    parser.add_argument("--encoding", default="cp1252", help="Windows ANSI encoding used for stored paths (default: cp1252)")
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputDir", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if not args.inputFile.is_file():
            raise FormatError("input file does not exist or is not a regular file")
        try:
            codecs.lookup(args.encoding)
        except LookupError as exc:
            raise FormatError(f"unknown path encoding {args.encoding!r}") from exc
        parsed = parse_installer(args.inputFile, args.encoding)
        with tempfile.TemporaryDirectory(prefix="clickteam-") as temporary:
            staging = Path(temporary)
            extracted = stage_extraction(parsed, staging, args.all)
            if not extracted and not args.all:
                detail = "; ".join(parsed.get("issues", [])) or "no installed-file record is recoverable"
                raise FormatError(f"no recoverable installed files: {detail}")
            merge_staging(staging, args.outputDir)
        total = sum(item["size"] for item in extracted)
        product_note = (f" from {len(parsed['products'])} products"
                        if len(parsed["products"]) > 1 else "")
        skipped_files = sum(
            1 for entry in parsed["entries"]
            if entry.get("extract", True) and entry.get("kind", 0) in (0, 1)
            and not entry.get("recoverable", True)
        )
        partial = bool(parsed.get("issues"))
        action = "Partially extracted" if partial else "Extracted"
        print(f"{action} {len(extracted)} files ({total} bytes){product_note} "
              f"using file-list layout {parsed['layout']}."
              + (f" Skipped {skipped_files} unrecoverable file records." if skipped_files else ""))
        for issue in parsed.get("issues", []):
            print(f"clickTeam.py: warning: {issue}", file=sys.stderr)
        return 0
    except (FormatError, OSError) as exc:
        print(f"clickTeam.py: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

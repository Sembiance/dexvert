#!/usr/bin/env python3
# Vibe coded by Codex
"""Strict extractor for Myriad Install self-extracting archives."""

from __future__ import annotations

import argparse
import datetime as _datetime
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import struct
import sys
import tempfile
from dataclasses import dataclass, field
from typing import Any


ARCHIVE_MAGIC = 0x15620001
WRAPPER_MAGIC = 0x02081967
LH5_WINDOW = 8192
MAX_FILES = 65535
MAX_STRING = 255


class FormatError(Exception):
    """The input is not a supported, internally consistent Myriad archive."""


class Reader:
    def __init__(self, data: bytes, pos: int = 0, limit: int | None = None):
        self.data = data
        self.pos = pos
        self.limit = len(data) if limit is None else limit

    def need(self, count: int) -> None:
        if count < 0 or self.pos + count > self.limit:
            raise FormatError(f"unexpected end of input at 0x{self.pos:x}")

    def take(self, count: int) -> bytes:
        self.need(count)
        result = self.data[self.pos : self.pos + count]
        self.pos += count
        return result

    def u8(self) -> int:
        return self.take(1)[0]

    def u16(self) -> int:
        return struct.unpack("<H", self.take(2))[0]

    def u32(self) -> int:
        return struct.unpack("<I", self.take(4))[0]

    def cstring(self, maximum: int = MAX_STRING) -> str:
        end_limit = min(self.limit, self.pos + maximum + 1)
        end = self.data.find(b"\0", self.pos, end_limit)
        if end < 0:
            raise FormatError(f"unterminated string at 0x{self.pos:x}")
        raw = self.data[self.pos:end]
        self.pos = end + 1
        try:
            return raw.decode("cp1252")
        except UnicodeDecodeError as error:
            raise FormatError(f"invalid Windows string at 0x{self.pos:x}") from error


class BitReader:
    """MSB-first reader used by the Myriad LH5 implementation."""

    def __init__(self, data: bytes):
        self.data = data
        self.bit_pos = 0

    def get(self, count: int) -> int:
        if not 0 <= count <= 32:
            raise FormatError("invalid LH5 bit count")
        if self.bit_pos + count > len(self.data) * 8:
            raise FormatError("truncated LH5 stream")
        value = 0
        for _ in range(count):
            byte = self.data[self.bit_pos >> 3]
            value = (value << 1) | ((byte >> (7 - (self.bit_pos & 7))) & 1)
            self.bit_pos += 1
        return value


class Huffman:
    def __init__(self, lengths: list[int]):
        counts = [0] * 17
        for length in lengths:
            if not 0 <= length <= 16:
                raise FormatError("invalid LH5 Huffman code length")
            if length:
                counts[length] += 1
        code = 0
        next_code = [0] * 17
        for bits in range(1, 17):
            code = (code + counts[bits - 1]) << 1
            next_code[bits] = code
            if code + counts[bits] > 1 << bits:
                raise FormatError("oversubscribed LH5 Huffman tree")
        if code + counts[16] != 1 << 16:
            raise FormatError("incomplete LH5 Huffman tree")
        self.codes: dict[tuple[int, int], int] = {}
        for symbol, length in enumerate(lengths):
            if length:
                self.codes[(length, next_code[length])] = symbol
                next_code[length] += 1
        if not self.codes:
            raise FormatError("empty LH5 Huffman tree")

    def decode(self, bits: BitReader) -> int:
        code = 0
        for length in range(1, 17):
            code = (code << 1) | bits.get(1)
            symbol = self.codes.get((length, code))
            if symbol is not None:
                return symbol
        raise FormatError("invalid LH5 Huffman code")


class LH5Decoder:
    NC = 510
    NP = 14
    NT = 19

    def __init__(self, stored: bytes):
        self.bits = BitReader(stored)
        self.block_remaining = 0
        self.c_table: int | Huffman | None = None
        self.p_table: int | Huffman | None = None

    @staticmethod
    def _decode(table: int | Huffman, bits: BitReader) -> int:
        return table if isinstance(table, int) else table.decode(bits)

    def _read_pt(self, count: int, count_bits: int, special: int) -> int | Huffman:
        used = self.bits.get(count_bits)
        if used == 0:
            symbol = self.bits.get(count_bits)
            if symbol >= count:
                raise FormatError("invalid constant LH5 position symbol")
            return symbol
        if used > count:
            raise FormatError("invalid LH5 position-tree size")
        lengths = [0] * count
        index = 0
        while index < used:
            length = self.bits.get(3)
            if length == 7:
                while self.bits.get(1):
                    length += 1
                    if length > 16:
                        raise FormatError("LH5 position code is too long")
            lengths[index] = length
            index += 1
            if index == special:
                index += self.bits.get(2)
                if index > count:
                    raise FormatError("LH5 position zero run is too long")
        return Huffman(lengths)

    def _read_c(self, pt_table: int | Huffman) -> int | Huffman:
        used = self.bits.get(9)
        if used == 0:
            symbol = self.bits.get(9)
            if symbol >= self.NC:
                raise FormatError("invalid constant LH5 literal symbol")
            return symbol
        if used > self.NC:
            raise FormatError("invalid LH5 literal-tree size")
        lengths = [0] * self.NC
        index = 0
        while index < used:
            symbol = self._decode(pt_table, self.bits)
            if symbol <= 2:
                if symbol == 0:
                    run = 1
                elif symbol == 1:
                    run = self.bits.get(4) + 3
                else:
                    run = self.bits.get(9) + 20
                index += run
                if index > used:
                    raise FormatError("LH5 literal zero run exceeds its tree")
            else:
                lengths[index] = symbol - 2
                index += 1
        return Huffman(lengths)

    def _literal_or_length(self) -> int:
        if self.block_remaining == 0:
            self.block_remaining = self.bits.get(16)
            if self.block_remaining == 0:
                raise FormatError("zero-length LH5 block")
            temporary = self._read_pt(self.NT, 5, 3)
            self.c_table = self._read_c(temporary)
            self.p_table = self._read_pt(self.NP, 4, -1)
        self.block_remaining -= 1
        assert self.c_table is not None
        return self._decode(self.c_table, self.bits)

    def _distance(self) -> int:
        assert self.p_table is not None
        symbol = self._decode(self.p_table, self.bits)
        if symbol == 0:
            return 0
        return (1 << (symbol - 1)) + self.bits.get(symbol - 1)

    def decompress(self, expected_size: int) -> bytes:
        if expected_size < 0:
            raise FormatError("negative expanded size")
        output = bytearray()
        ring = bytearray(LH5_WINDOW)
        write_pos = 0
        while len(output) < expected_size:
            symbol = self._literal_or_length()
            if symbol < 256:
                ring[write_pos] = symbol
                output.append(symbol)
                write_pos = (write_pos + 1) & (LH5_WINDOW - 1)
                continue
            length = symbol - 253
            if length < 3 or length > 256:
                raise FormatError("invalid LH5 match length")
            if len(output) + length > expected_size:
                raise FormatError("LH5 match exceeds declared expanded size")
            source = (write_pos - self._distance() - 1) & (LH5_WINDOW - 1)
            for _ in range(length):
                value = ring[source]
                ring[write_pos] = value
                output.append(value)
                source = (source + 1) & (LH5_WINDOW - 1)
                write_pos = (write_pos + 1) & (LH5_WINDOW - 1)
        if self.block_remaining != 0:
            raise FormatError("declared LH5 size ends before its Huffman block")
        # The encoder pads only the final partially used byte with zero bits.
        used_bytes = (self.bits.bit_pos + 7) // 8
        if used_bytes != len(self.bits.data):
            raise FormatError("unused bytes at the end of an LH5 stream")
        if self.bits.bit_pos & 7:
            unused = 8 - (self.bits.bit_pos & 7)
            if self.bits.data[-1] & ((1 << unused) - 1):
                raise FormatError("nonzero LH5 padding bits")
        return bytes(output)


def md5_xor(data: bytes) -> int:
    words = struct.unpack("<4I", hashlib.md5(data).digest())
    return words[0] ^ words[1] ^ words[2] ^ words[3]


def file_check(data: bytes) -> int:
    result = 0xCAFEDECA
    # The installer hashes the final read even when that read returns zero
    # bytes, so an empty file has one MD5(empty) contribution.
    for start in range(0, max(1, len(data)), LH5_WINDOW):
        result ^= md5_xor(data[start : start + LH5_WINDOW])
    return result & 0xFFFFFFFF


def decode_fixed_string(raw: bytes, field: str) -> str:
    nul = raw.find(b"\0")
    if nul < 0:
        raise FormatError(f"unterminated fixed {field} field")
    try:
        return raw[:nul].decode("cp1252")
    except UnicodeDecodeError as error:
        raise FormatError(f"invalid fixed {field} encoding") from error


def dos_datetime(date: int, time: int) -> str | None:
    if date == 0 and time == 0:
        return None
    try:
        value = _datetime.datetime(
            1980 + ((date >> 9) & 0x7F),
            (date >> 5) & 0x0F,
            date & 0x1F,
            (time >> 11) & 0x1F,
            (time >> 5) & 0x3F,
            (time & 0x1F) * 2,
        )
    except ValueError as error:
        raise FormatError(f"invalid DOS timestamp 0x{date:04x}/0x{time:04x}") from error
    return value.isoformat()


@dataclass
class Entry:
    block: int
    index: int
    name: str
    destination: str
    group: str
    date: int
    time: int
    stored_size: int
    expanded_size: int
    check: int
    method: int
    component: int
    progress_offset: int
    data_offset: int
    flags: int
    raw_table: bytes
    content: bytes | None = None
    output_name: str | None = None


@dataclass
class Block:
    index: int
    offset: int
    dialect: str
    version: int
    uninstall: int
    stored_total: int
    default_directory: str
    uninstall_name: str
    shortcuts: list[str]
    title: str
    copyright: str
    release: str
    ui_words: list[int]
    entries: list[Entry] = field(default_factory=list)
    associations: list[dict[str, Any]] = field(default_factory=list)
    table_check: int = 0
    global_kind: int = 0
    global_resource: bytes | None = None
    end: int = 0


@dataclass
class Archive:
    input_size: int
    pe_end: int
    wrapped: bool
    blocks: list[Block]


def pe_overlay_offset(data: bytes) -> int:
    if len(data) < 0x40 or data[:2] != b"MZ":
        raise FormatError("missing DOS MZ header")
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    if pe > len(data) - 24 or data[pe : pe + 4] != b"PE\0\0":
        raise FormatError("missing PE signature")
    section_count = struct.unpack_from("<H", data, pe + 6)[0]
    optional_size = struct.unpack_from("<H", data, pe + 20)[0]
    if section_count == 0 or section_count > 96:
        raise FormatError("invalid PE section count")
    table = pe + 24 + optional_size
    if table + section_count * 40 > len(data):
        raise FormatError("truncated PE section table")
    end = 0
    for index in range(section_count):
        section = table + index * 40
        stored_size, stored_offset = struct.unpack_from("<II", data, section + 16)
        if stored_offset + stored_size > len(data):
            raise FormatError("PE section extends beyond the input")
        end = max(end, stored_offset + stored_size)
    if end == 0 or end >= len(data):
        raise FormatError("PE file has no appended Myriad archive")
    return end


def parse_variable_entry(reader: Reader, block_index: int, entry_index: int,
                         flag_count: int) -> Entry:
    start = reader.pos
    name = reader.cstring()
    destination = reader.cstring()
    group = reader.cstring()
    date = reader.u16()
    time = reader.u16()
    stored_size = reader.u32()
    expanded_size = reader.u32()
    check = reader.u32()
    method = reader.u8()
    component = reader.u16()
    progress_offset = reader.u32()
    data_offset = reader.u32()
    flag_bytes = reader.take(flag_count)
    if any(value not in (0, 1) for value in flag_bytes):
        raise FormatError("file flags must be serialized booleans")
    flags = sum(bool(value) << index for index, value in enumerate(flag_bytes))
    return Entry(block_index, entry_index, name, destination, group, date, time,
                 stored_size, expanded_size, check, method, component,
                 progress_offset, data_offset, flags, reader.data[start:reader.pos])


def parse_variable_block(data: bytes, offset: int, index: int, legacy: bool) -> Block:
    reader = Reader(data, offset)
    if reader.u32() != ARCHIVE_MAGIC:
        raise FormatError(f"missing archive header magic at 0x{offset:x}")
    file_count = reader.u16()
    version = reader.u16()
    uninstall = reader.u16()
    association_count = reader.u16()
    stored_total = reader.u32()
    if file_count > MAX_FILES or version != 1 or uninstall not in (0, 1):
        raise FormatError("unsupported variable archive header")
    default_directory = reader.cstring()
    uninstall_name = reader.cstring()
    shortcut_count = reader.u8()
    shortcuts = [reader.cstring() for _ in range(shortcut_count)]
    title, copyright_text, release = (reader.cstring() for _ in range(3))
    ui_words = [] if legacy else [reader.u32() for _ in range(3)]
    dialect = "variable-3.5" if legacy else "variable-4.1"
    block = Block(index, offset, dialect, version, uninstall, stored_total,
                  default_directory, uninstall_name, shortcuts, title,
                  copyright_text, release, ui_words)
    for entry_index in range(file_count):
        block.entries.append(parse_variable_entry(reader, index, entry_index, 2 if legacy else 3))
    for _ in range(association_count):
        association = {
            "extension": reader.cstring(),
            "class_name": reader.cstring(),
            "application": reader.cstring(),
            "icon_index": reader.u16(),
        }
        block.associations.append(association)
    if reader.u32() != ARCHIVE_MAGIC:
        raise FormatError("archive header/footer magic mismatch")
    block.table_check = reader.u32()
    global_stored = reader.u32()
    header_end = reader.pos
    if global_stored:
        global_expanded = reader.u32()
        block.global_kind = reader.u16()
        stored = reader.take(global_stored)
        block.global_resource = LH5Decoder(stored).decompress(global_expanded)
        header_end = reader.pos
    data_end = header_end
    ranges: list[tuple[int, int]] = []
    for entry in block.entries:
        begin = offset + entry.data_offset
        end = begin + entry.stored_size
        if begin < header_end or end > len(data):
            raise FormatError(f"file payload {entry.name!r} is out of bounds")
        if entry.stored_size:
            ranges.append((begin, end))
        data_end = max(data_end, end)
    ranges.sort()
    cursor = header_end
    for previous, current in zip(ranges, ranges[1:]):
        if current[0] < previous[1]:
            raise FormatError("overlapping file payloads")
    for begin, end in ranges:
        if begin != cursor:
            raise FormatError(f"unaccounted archive bytes at 0x{cursor:x}")
        cursor = end
    if cursor != data_end:
        raise FormatError("archive payload coverage mismatch")
    block.end = data_end
    return block


def parse_fixed_block(data: bytes, offset: int, index: int) -> Block:
    reader = Reader(data, offset)
    header = reader.take(0x610)
    if struct.unpack_from("<I", header, 0)[0] != ARCHIVE_MAGIC:
        raise FormatError("missing fixed archive header magic")
    file_count, version, uninstall, association_count = struct.unpack_from("<4H", header, 4)
    stored_total = struct.unpack_from("<I", header, 12)[0]
    if file_count > MAX_FILES or version != 1 or uninstall not in (0, 1):
        raise FormatError("unsupported fixed archive header")
    strings = [decode_fixed_string(header[16 + i * 255 : 16 + (i + 1) * 255], "header string")
               for i in range(6)]
    if header[0x60A:0x60C] != b"\0\0":
        raise FormatError("nonzero fixed-header alignment padding")
    if struct.unpack_from("<I", header, 0x60C)[0] != ARCHIVE_MAGIC:
        raise FormatError("fixed archive header/footer magic mismatch")
    shortcuts = [item for item in strings[2].split(";") if item]
    block = Block(index, offset, "fixed-3.0", version, uninstall, stored_total,
                  strings[0], strings[1], shortcuts, strings[3], strings[4],
                  strings[5], [])
    table_start = reader.pos
    table = reader.take(file_count * 0x68)
    for entry_index in range(file_count):
        raw = table[entry_index * 0x68 : (entry_index + 1) * 0x68]
        name = decode_fixed_string(raw[0:32], "file name")
        destination = decode_fixed_string(raw[32:64], "destination")
        if raw[64] != 0:
            raise FormatError("nonzero fixed-record reserved byte")
        group = decode_fixed_string(raw[65:70], "group")
        date, time = struct.unpack_from("<HH", raw, 70)
        if raw[74:76] != b"\0\0":
            raise FormatError("nonzero fixed-record alignment padding")
        stored_size, expanded_size, check = struct.unpack_from("<III", raw, 76)
        method = raw[88]
        if raw[89] != 0:
            raise FormatError("nonzero fixed-record alignment byte")
        component = struct.unpack_from("<H", raw, 90)[0]
        progress_offset, data_offset, flags = struct.unpack_from("<III", raw, 92)
        if flags & ~0x7:
            raise FormatError("unsupported fixed-record flag bits")
        block.entries.append(Entry(index, entry_index, name, destination, group,
                                   date, time, stored_size, expanded_size, check,
                                   method, component, progress_offset, data_offset,
                                   flags, raw))
    for _ in range(association_count):
        raw = reader.take(0x48)
        if raw[36] != 0 or raw[69] != 0:
            raise FormatError("nonzero fixed-association reserved/padding byte")
        block.associations.append({
            "extension": decode_fixed_string(raw[0:4], "extension"),
            "class_name": decode_fixed_string(raw[4:36], "class name"),
            "application": decode_fixed_string(raw[37:69], "association application"),
            "icon_index": struct.unpack_from("<H", raw, 70)[0],
        })
    block.table_check = reader.u32()
    if block.table_check != md5_xor(data[table_start : table_start + len(table)]):
        raise FormatError("fixed file table checksum mismatch")
    global_stored = reader.u32()
    header_end = reader.pos
    if global_stored:
        global_expanded = reader.u32()
        block.global_kind = reader.u16()
        block.global_resource = LH5Decoder(reader.take(global_stored)).decompress(global_expanded)
        header_end = reader.pos
    data_end = header_end
    ranges: list[tuple[int, int]] = []
    for entry in block.entries:
        begin = offset + entry.data_offset
        end = begin + entry.stored_size
        if begin < header_end or end > len(data):
            raise FormatError(f"file payload {entry.name!r} is out of bounds")
        if entry.stored_size:
            ranges.append((begin, end))
        data_end = max(data_end, end)
    ranges.sort()
    cursor = header_end
    for previous, current in zip(ranges, ranges[1:]):
        if current[0] < previous[1]:
            raise FormatError("overlapping file payloads")
    for begin, end in ranges:
        if begin != cursor:
            raise FormatError(f"unaccounted archive bytes at 0x{cursor:x}")
        cursor = end
    if cursor != data_end:
        raise FormatError("archive payload coverage mismatch")
    block.end = data_end
    return block


def unpack_entry(data: bytes, block: Block, entry: Entry) -> bytes | None:
    if entry.stored_size == 0 and entry.expanded_size == 0:
        if entry.method in (2, 3, 4):
            if entry.check != 0:
                raise FormatError(f"action entry {entry.name!r} has a checksum")
            return None
        if entry.method not in (0, 1):
            raise FormatError(f"entry {entry.name!r} uses unsupported method {entry.method}")
        if entry.check and file_check(b"") != entry.check:
            raise FormatError(f"empty-file checksum mismatch for {entry.name!r}")
        return b""
    stored = data[block.offset + entry.data_offset : block.offset + entry.data_offset + entry.stored_size]
    if entry.method == 0:
        if entry.stored_size != entry.expanded_size:
            raise FormatError(f"stored entry {entry.name!r} has unequal sizes")
        expanded = stored
    elif entry.method == 1:
        expanded = LH5Decoder(stored).decompress(entry.expanded_size)
    else:
        raise FormatError(f"entry {entry.name!r} uses unsupported method {entry.method}")
    if len(expanded) != entry.expanded_size:
        raise FormatError(f"expanded size mismatch for {entry.name!r}")
    if entry.check and file_check(expanded) != entry.check:
        raise FormatError(f"content checksum mismatch for {entry.name!r}")
    return expanded


def parse_archive(data: bytes) -> Archive:
    pe_end = pe_overlay_offset(data)
    offset = pe_end
    wrapped = False
    if offset + 4 <= len(data) and struct.unpack_from("<I", data, offset)[0] == WRAPPER_MAGIC:
        wrapped = True
        offset += 4
    if offset + 4 > len(data) or struct.unpack_from("<I", data, offset)[0] != ARCHIVE_MAGIC:
        raise FormatError("PE overlay is not a supported Myriad archive")
    # Fixed revision headers are exactly 0x610 bytes and carry their second
    # magic at +0x60c. Variable revision headers are self-delimiting.
    is_fixed = (offset + 0x610 <= len(data) and
                struct.unpack_from("<I", data, offset + 0x60C)[0] == ARCHIVE_MAGIC)
    blocks: list[Block] = []
    while offset < len(data):
        if struct.unpack_from("<I", data, offset)[0] != ARCHIVE_MAGIC:
            raise FormatError(f"unaccounted bytes at 0x{offset:x}")
        block = (parse_fixed_block(data, offset, len(blocks)) if is_fixed else
                 parse_variable_block(data, offset, len(blocks), wrapped))
        if block.end <= offset:
            raise FormatError("archive block does not advance")
        blocks.append(block)
        offset = block.end
        if is_fixed:
            break
    if offset != len(data):
        raise FormatError(f"{len(data) - offset} trailing byte(s) are not accounted for")
    if not blocks:
        raise FormatError("archive contains no blocks")
    for block in blocks:
        for entry in block.entries:
            entry.content = unpack_entry(data, block, entry)
        computed_total = sum(entry.stored_size for entry in block.entries)
        if computed_total != block.stored_total:
            raise FormatError(
                f"block {block.index} stored total is {block.stored_total}, records total {computed_total}"
            )
    return Archive(len(data), pe_end, wrapped, blocks)


def safe_parts(value: str) -> list[str]:
    value = value.replace("/", "\\")
    parts = []
    for part in PureWindowsPath(value).parts:
        if part in ("", ".", "\\"):
            continue
        if part == ".." or ":" in part or "\0" in part:
            raise FormatError(f"unsafe archive path component {part!r}")
        parts.append(part)
    return parts


def logical_path(entry: Entry) -> Path:
    destination = entry.destination.replace("/", "\\")
    parts = safe_parts(destination)
    if parts and parts[0].upper() == "$D":
        parts = parts[1:]
    elif parts and parts[0].startswith("$"):
        macro = parts.pop(0)[1:] or "UNKNOWN"
        parts = ["_myriad_system", macro] + parts
    elif parts:
        parts = ["_myriad_absolute"] + parts
    name_parts = safe_parts(entry.name)
    if not name_parts:
        raise FormatError("empty output file name")
    return Path(*parts, *name_parts)


def resource_extension(content: bytes) -> str:
    if content.startswith(b"BM"):
        return ".bmp"
    if content.startswith(b"MZ"):
        return ".exe"
    return ".bin"


def metadata(archive: Archive, source: Path) -> dict[str, Any]:
    return {
        "format": "Myriad Install",
        "source": source.name,
        "input_size": archive.input_size,
        "pe_overlay_offset": archive.pe_end,
        "wrapper_magic_present": archive.wrapped,
        "blocks": [
            {
                "index": block.index,
                "offset": block.offset,
                "end": block.end,
                "dialect": block.dialect,
                "version": block.version,
                "uninstall_enabled": bool(block.uninstall),
                "stored_total": block.stored_total,
                "default_directory": block.default_directory,
                "uninstall_name": block.uninstall_name,
                "shortcuts": block.shortcuts,
                "title": block.title,
                "copyright": block.copyright,
                "release": block.release,
                "ui_words": block.ui_words,
                "table_check": f"0x{block.table_check:08x}",
                "global_kind": block.global_kind,
                "global_resource_size": len(block.global_resource or b""),
                "associations": block.associations,
                "entries": [
                    {
                        "index": entry.index,
                        "name": entry.name,
                        "destination": entry.destination,
                        "group": entry.group,
                        "timestamp": dos_datetime(entry.date, entry.time),
                        "stored_size": entry.stored_size,
                        "expanded_size": entry.expanded_size,
                        "check": f"0x{entry.check:08x}",
                        "method": entry.method,
                        "component": entry.component,
                        "progress_offset": entry.progress_offset,
                        "data_offset": entry.data_offset,
                        "flags": entry.flags,
                        "output": entry.output_name,
                    }
                    for entry in block.entries
                ],
            }
            for block in archive.blocks
        ],
    }


def stage_outputs(archive: Archive, source: Path, staging: Path, include_metadata: bool) -> int:
    used: dict[str, tuple[bytes, Path]] = {}
    written = 0
    for block in archive.blocks:
        if block.global_resource is not None:
            suffix = resource_extension(block.global_resource)
            relative = Path("_myriad_resources", f"block_{block.index:03d}_global{suffix}")
            target = staging / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(block.global_resource)
            written += 1
        for entry in block.entries:
            if entry.content is None:
                continue
            relative = logical_path(entry)
            key = str(relative).replace("\\", "/").casefold()
            if key in used:
                old_content, old_path = used[key]
                if old_content == entry.content:
                    entry.output_name = old_path.as_posix()
                    continue
                group = "_".join(safe_parts(entry.group)) or "ungrouped"
                relative = Path("_myriad_variants", f"block_{block.index:03d}", group, relative)
                key = str(relative).replace("\\", "/").casefold()
                if key in used:
                    raise FormatError(f"multiple different payloads map to {relative}")
            target = staging / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(entry.content)
            timestamp = _datetime.datetime.fromisoformat(dos_datetime(entry.date, entry.time)).timestamp() if dos_datetime(entry.date, entry.time) else None
            if timestamp is not None:
                os.utime(target, (timestamp, timestamp))
            entry.output_name = relative.as_posix()
            used[key] = (entry.content, relative)
            written += 1
    if include_metadata:
        (staging / "_myriad_metadata.json").write_text(
            json.dumps(metadata(archive, source), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return written


def merge_tree(staging: Path, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    if output.is_symlink() or not output.is_dir():
        raise OSError(f"output path is not a real directory: {output}")
    for source in sorted(staging.rglob("*")):
        relative = source.relative_to(staging)
        target = output / relative
        if source.is_dir():
            if target.exists() and (target.is_symlink() or not target.is_dir()):
                raise OSError(f"cannot create directory over {target}")
            target.mkdir(exist_ok=True)
        else:
            if target.exists() and target.is_dir():
                raise OSError(f"cannot replace directory {target} with a file")
            target.parent.mkdir(parents=True, exist_ok=True)
            os.replace(source, target)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [--all] <inputFile> <outputDir>",
        description="Extract Myriad Install PE archives after complete validation.",
    )
    parser.add_argument("--all", action="store_true", help="also write _myriad_metadata.json")
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputDir", type=Path)
    args = parser.parse_args(argv)
    try:
        source = args.inputFile
        data = source.read_bytes()
        archive = parse_archive(data)
        parent = args.outputDir.absolute().parent
        parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".myriadInstall-", dir=parent) as temporary:
            staging = Path(temporary)
            count = stage_outputs(archive, source, staging, args.all)
            merge_tree(staging, args.outputDir.absolute())
        print(f"Extracted {count} payload file(s) from {source} into {args.outputDir}")
        return 0
    except (FormatError, OSError) as error:
        print(f"myriadInstall.py: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

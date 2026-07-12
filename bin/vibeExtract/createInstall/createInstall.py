#!/usr/bin/env python3
# Vibe coded by Codex
"""Validated extractor with bounded recovery for supported CreateInstall archives."""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
import shutil
import stat
import struct
import subprocess
import sys
import tempfile
import zlib
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path, PureWindowsPath

try:
    import pyppmd_gentee
except ImportError:  # Reported only when a GEA input actually needs it.
    pyppmd_gentee = None

try:
    from unicorn import UC_ARCH_X86, UC_HOOK_CODE, UC_MODE_32, Uc
    from unicorn.x86_const import (
        UC_X86_REG_EAX,
        UC_X86_REG_ECX,
        UC_X86_REG_EDX,
        UC_X86_REG_EIP,
        UC_X86_REG_ESP,
    )
except ImportError:  # Reported only if the fast GEA decoder needs its fallback.
    Uc = None


class FormatError(Exception):
    """The input is not a supported, structurally valid CreateInstall file."""


def _u16(data: bytes | memoryview, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def _u32(data: bytes | memoryview, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def _filetime(value: int) -> str:
    if value == 0:
        return "1601-01-01T00:00:00Z"
    epoch = datetime(1601, 1, 1, tzinfo=timezone.utc)
    try:
        return (epoch + timedelta(microseconds=value // 10)).isoformat().replace("+00:00", "Z")
    except OverflowError:
        raise FormatError("a file record contains an invalid FILETIME") from None


class _Codec:
    """CreateInstall's per-stream adaptive-Huffman/LZ decoder."""

    _BIT_COUNTS = (4, 6, 8, 10, 12, 14)
    _LEAF_BASE = 629
    _LAST_NODE = 1257

    def __init__(self, source: memoryview, expected_size: int):
        self.source = source
        self.expected_size = expected_size
        self.source_offset = 0
        self.bits_left = 0
        self.bit_buffer = 0

        self.parent = [0] * (self._LAST_NODE + 1)
        self.left = [0] * (self._LAST_NODE + 1)
        self.right = [0] * (self._LAST_NODE + 1)
        self.weight = [0] * (self._LAST_NODE + 1)
        for node in range(2, self._LAST_NODE + 1):
            self.weight[node] = 1
            self.parent[node] = node // 2
        for node in range(1, self._LEAF_BASE):
            self.left[node] = node * 2
            self.right[node] = node * 2 + 1

        self.distance_base: list[int] = []
        base = 0
        for count in self._BIT_COUNTS:
            self.distance_base.append(base)
            base += 1 << count
        self.window = bytearray(base + 64)
        self.window_offset = 0
        self.output = bytearray()

    def _bit(self) -> int:
        old_count = self.bits_left
        self.bits_left -= 1
        if old_count == 0:
            if self.source_offset >= len(self.source):
                raise FormatError("a compressed stream is truncated")
            self.bit_buffer = self.source[self.source_offset]
            self.source_offset += 1
            self.bits_left = 7
        result = self.bit_buffer >> 7
        self.bit_buffer = (self.bit_buffer << 1) & 0xFF
        return result

    def _bits(self, count: int) -> int:
        result = 0
        for bit_number in range(count):
            result |= self._bit() << bit_number
        return result

    def _recalculate_ancestors(self, node: int, other: int) -> None:
        while True:
            parent = self.parent[node]
            self.weight[parent] = (self.weight[node] + self.weight[other]) & 0xFFFF
            node = parent
            if node == 1:
                break
            grandparent = self.parent[node]
            other = self.left[grandparent]
            if other == node:
                other = self.right[grandparent]
        if self.weight[1] == 2000:
            for index in range(1, self._LAST_NODE + 1):
                value = self.weight[index]
                if value & 0x8000:
                    value -= 0x10000
                self.weight[index] = (value // 2) & 0xFFFF

    def _update_model(self, symbol: int) -> None:
        node = self._LEAF_BASE + symbol
        self.weight[node] = (self.weight[node] + 1) & 0xFFFF
        parent = self.parent[node]
        if parent == 1:
            return
        other = self.left[parent]
        if node == other:
            other = self.right[parent]
        self._recalculate_ancestors(node, other)
        while True:
            grandparent = self.parent[parent]
            cousin = self.left[grandparent]
            if parent == cousin:
                cousin = self.right[grandparent]
            node_weight = self.weight[node]
            cousin_weight = self.weight[cousin]
            if node_weight & 0x8000:
                node_weight -= 0x10000
            if cousin_weight & 0x8000:
                cousin_weight -= 0x10000
            if node_weight > cousin_weight:
                if parent == self.left[grandparent]:
                    self.right[grandparent] = node
                else:
                    self.left[grandparent] = node

                first = self.left[parent]
                if node == first:
                    displaced = self.right[parent]
                    self.left[parent] = cousin
                else:
                    displaced = first
                    self.right[parent] = cousin
                self.parent[cousin] = parent
                self.parent[node] = grandparent
                node = cousin
                self._recalculate_ancestors(node, displaced)

            node = self.parent[node]
            parent = self.parent[node]
            if parent == 1:
                return

    def _symbol(self) -> int:
        node = 1
        while node < self._LEAF_BASE:
            node = self.right[node] if self._bit() else self.left[node]
        symbol = node - self._LEAF_BASE
        self._update_model(symbol)
        return symbol

    def decode(self) -> tuple[bytes, int]:
        while True:
            symbol = self._symbol()
            if symbol == 256:
                return bytes(self.output), self.source_offset
            if symbol < 256:
                value = symbol
                self.output.append(value)
                self.window[self.window_offset] = value
                self.window_offset = (self.window_offset + 1) % len(self.window)
                continue

            group = (symbol - 257) // 62
            if group >= len(self._BIT_COUNTS):
                raise FormatError("a compressed stream contains an invalid match symbol")
            length = symbol - group * 62 - 254
            distance = (
                self.distance_base[group]
                + self._bits(self._BIT_COUNTS[group])
                + length
            )
            source_offset = (self.window_offset - distance) % len(self.window)
            for _ in range(length):
                value = self.window[source_offset]
                source_offset = (source_offset + 1) % len(self.window)
                self.output.append(value)
                if len(self.output) > self.expected_size:
                    raise FormatError("compressed output exceeds its declared size")
                self.window[self.window_offset] = value
                self.window_offset = (self.window_offset + 1) % len(self.window)


@dataclass(frozen=True)
class _Entry:
    archive_name: bytes
    relative_name: Path
    attributes: int
    filetime: int
    storage: str
    data: bytes | None


@dataclass(frozen=True)
class _Archive:
    input_size: int
    pe_end: int
    runtime_size: int
    header_offset: int
    expanded_size: int
    configuration: bytes
    directories: tuple[Path, ...]
    entries: tuple[_Entry, ...]
    metadata: dict[str, object]


@dataclass(frozen=True)
class _GeaFile:
    archive_name: bytes
    size: int
    attributes: int
    filetime: int
    version_high: int
    version_low: int


@dataclass(frozen=True)
class _GeaGroup:
    group_id: int
    payload_size: int
    files: tuple[_GeaFile, ...]
    cabinet_expanded_size: int | None
    password_crc: int | None


def _pe_overlay_offset(data: bytes) -> int:
    if len(data) < 0x40 or data[:2] != b"MZ":
        raise FormatError("input is not a DOS/PE executable")
    pe_offset = _u32(data, 0x3C)
    if pe_offset > len(data) - 24 or data[pe_offset : pe_offset + 4] != b"PE\0\0":
        raise FormatError("input has no valid PE signature")
    section_count = _u16(data, pe_offset + 6)
    optional_size = _u16(data, pe_offset + 20)
    if section_count == 0:
        raise FormatError("PE image has no sections")
    section_table = pe_offset + 24 + optional_size
    if section_table + section_count * 40 > len(data):
        raise FormatError("PE section table is truncated")
    ends = []
    for index in range(section_count):
        section = section_table + index * 40
        raw_size = _u32(data, section + 16)
        raw_offset = _u32(data, section + 20)
        if raw_offset + raw_size > len(data):
            raise FormatError("a PE section extends beyond the input")
        ends.append(raw_offset + raw_size)
    return max(ends)


def _pe_sections(data: bytes) -> tuple[tuple[bytes, int, int, int], ...]:
    """Return (name, RVA, raw size, raw offset) for a validated PE image."""
    _pe_overlay_offset(data)
    pe_offset = _u32(data, 0x3C)
    section_count = _u16(data, pe_offset + 6)
    section_table = pe_offset + 24 + _u16(data, pe_offset + 20)
    return tuple(
        (
            data[offset : offset + 8].rstrip(b"\0"),
            _u32(data, offset + 12),
            _u32(data, offset + 16),
            _u32(data, offset + 20),
        )
        for offset in (section_table + index * 40 for index in range(section_count))
    )


def _pe_rva_offset(data: bytes, rva: int) -> int:
    for _name, virtual_address, raw_size, raw_offset in _pe_sections(data):
        if virtual_address <= rva < virtual_address + raw_size:
            return raw_offset + rva - virtual_address
    raise FormatError(f"PE RVA 0x{rva:x} is not backed by file data")


def _pe_security_range(data: bytes) -> tuple[int, int] | None:
    pe_offset = _u32(data, 0x3C)
    optional = pe_offset + 24
    optional_size = _u16(data, pe_offset + 20)
    if optional_size < 136 or _u16(data, optional) != 0x10B:
        return None
    certificate_offset = _u32(data, optional + 128)
    certificate_size = _u32(data, optional + 132)
    if not certificate_offset and not certificate_size:
        return None
    if (
        not certificate_offset
        or certificate_size < 8
        or certificate_offset + certificate_size != len(data)
    ):
        raise FormatError("PE Security Directory is invalid")
    cursor = certificate_offset
    end = len(data)
    while cursor < end:
        if cursor + 8 > end:
            raise FormatError("WIN_CERTIFICATE header is truncated")
        length, revision, certificate_type = struct.unpack_from("<IHH", data, cursor)
        if (
            length < 8
            or cursor + length > end
            or revision != 0x0200
            or certificate_type not in (1, 2)
        ):
            raise FormatError("WIN_CERTIFICATE record is invalid")
        aligned = (length + 7) & ~7
        if cursor + aligned > end or any(data[cursor + length : cursor + aligned]):
            raise FormatError("WIN_CERTIFICATE alignment padding is invalid")
        cursor += aligned
    if cursor != end:
        raise FormatError("PE Security Directory has unexplained bytes")
    return certificate_offset, certificate_size


def _declared_runtime_size(data: bytes, pe_end: int) -> int:
    # The loader passes this immediate operand to ReadFile for its embedded
    # runtime block.  This complete instruction sequence occurs once in every
    # supported loader and is part of the on-disk format, not a data guess.
    instruction = b"\x57\x8d\x45\xfc\x50\x68"
    positions = []
    start = 0
    while True:
        found = data.find(instruction, start, pe_end)
        if found < 0:
            break
        positions.append(found)
        start = found + 1
    if len(positions) != 1 or positions[0] + 10 > pe_end:
        raise FormatError("unsupported CreateInstall loader code")
    return _u32(data, positions[0] + len(instruction))


def _runtime_size(data: bytes, pe_end: int) -> int:
    size = _declared_runtime_size(data, pe_end)
    if size == 0 or pe_end + size + 77 > len(data):
        raise FormatError("embedded runtime size is invalid")
    return size


def _header_size(runtime_size: int) -> int:
    # Successive classic-runtime revisions extended the packed header twice.
    sizes = {
        32500: 77,
        32600: 77,
        32800: 77,
        33000: 77,
        33200: 78,
        33300: 79,
        33400: 79,
    }
    try:
        return sizes[runtime_size]
    except KeyError:
        raise FormatError(f"unsupported embedded runtime revision ({runtime_size} bytes)") from None


def _decode_name(raw: bytes) -> str:
    # CreateInstall used the active Windows ANSI code page.  ASCII is exact;
    # non-ASCII byte names are losslessly mapped one-to-one through Latin-1.
    return raw.decode("latin-1")


def _relative_name(raw: bytes) -> Path:
    if not raw or b"\0" in raw:
        raise FormatError("an archive path is empty or contains NUL")
    return _relative_name_text(_decode_name(raw))


def _relative_name_text(text: str) -> Path:
    if not text or "\0" in text:
        raise FormatError("an archive path is empty or contains NUL")
    if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
        text = text[1:-1]
    lowered = text.lower()
    prefix = "%installpath%"
    if lowered == prefix:
        raise FormatError("an archive entry names the installation root, not a file")
    if lowered.startswith(prefix + "\\"):
        text = text[len(prefix) + 1 :]
    elif lowered.startswith(prefix + "/"):
        text = text[len(prefix) + 1 :]
    else:
        # Files targeting a different installer root remain grouped beneath a
        # literal, filesystem-safe representation of that root.
        text = text.replace("%", "_")
    path = PureWindowsPath(text)
    if not path.parts:
        raise FormatError("archive path has no components")
    parts = list(path.parts)
    mapped: list[str] = []
    if path.drive:
        drive = path.drive.rstrip(":\\/")
        mapped.append(f"_drive_{drive}")
        parts = parts[1:]
    elif path.root:
        mapped.append("_root")
        parts = parts[1:]
    for part in parts:
        if part in ("", "."):
            continue
        mapped.append("_parent" if part == ".." else part)
    if not mapped:
        raise FormatError("archive path resolves to no output components")
    return Path(*mapped)


_GEA_STUB_TEXT_SHA256 = "7e7c6eaeb55c94bd2af105027b4632bb6f120597685a521259ba8e06c5a1ed1f"
_GEA_RUNTIME_SHA256 = "0bf1779ce9a1ef46f5d44d3840d2f9e139bfed275d4a0aca3dd1172eb7c91d5c"


def _require_gea_decoder() -> None:
    if pyppmd_gentee is None:
        raise FormatError(
            "GEA extraction requires the non-standard pyppmd-gentee Python package"
        )


def _raw_ppmd(data: bytes, maximum_output: int) -> bytes:
    """Decode one [parameters][packed-size][PPMd bytes] stream."""
    _require_gea_decoder()
    if len(data) < 8:
        raise FormatError("a GEA PPMd stream header is truncated")
    parameters = data[:4]
    if not (2 <= parameters[1] <= 16 and parameters[0] != 0):
        raise FormatError("a GEA PPMd stream has invalid model parameters")
    header_size = 5 if parameters[3] & 4 else 4
    if len(data) < header_size + 4:
        raise FormatError("a GEA PPMd stream header is truncated")
    packed_field = _u32(data, header_size)
    packed_size = packed_field & 0x7FFFFFFF
    if header_size + 4 + packed_size != len(data):
        raise FormatError("a GEA PPMd stream size does not match its container")
    payload = data[header_size + 4 :]
    if packed_field & 0x80000000:
        return payload
    try:
        decoder = pyppmd_gentee.Ppmd8gDecoder(parameters[1], parameters[0] << 20)
        output = decoder.decode(payload, maximum_output + 1)
        if len(output) <= maximum_output and not decoder.eof and decoder.needs_input:
            output += decoder.decode(b"\0", maximum_output + 1 - len(output))
    except (ValueError, MemoryError) as error:
        raise FormatError(f"invalid GEA PPMd stream: {error}") from None
    if not decoder.eof or len(output) > maximum_output:
        raise FormatError("a GEA PPMd stream has no bounded end marker")
    return output


class _VerifiedStubDecoder:
    """Run only the hash-identified CreateInstall PPM decoder under Unicorn."""

    IMAGE = 0x00400000
    SOURCE = 0x10000000
    OUTPUT = 0x20000000
    HEAP = 0x30000000
    CONTEXT = 0x40000000
    STACK = 0x41000000
    STOP = 0x42000000
    ALLOC = 0x43000000
    FREE = ALLOC + 0x100

    def __init__(self, executable: bytes, source: bytes, output_size: int):
        if Uc is None:
            raise FormatError(
                "this GEA stream requires the non-standard unicorn Python package"
            )
        text_section = next(
            (item for item in _pe_sections(executable) if item[0] == b".text"), None
        )
        if text_section is None:
            raise FormatError("GEA loader has no .text section")
        _name, _rva, raw_size, raw_offset = text_section
        if hashlib.sha256(executable[raw_offset : raw_offset + raw_size]).hexdigest() != _GEA_STUB_TEXT_SHA256:
            raise FormatError("unsupported GEA loader decoder revision")

        self.machine = Uc(UC_ARCH_X86, UC_MODE_32)
        self.source_size = len(source)
        self.machine.mem_map(self.IMAGE, 0x10000)
        pe_offset = _u32(executable, 0x3C)
        header_size = _u32(executable, pe_offset + 84)
        self.machine.mem_write(self.IMAGE, executable[:header_size])
        for _name, rva, size, offset in _pe_sections(executable):
            if size:
                self.machine.mem_write(self.IMAGE + rva, executable[offset : offset + size])

        def pages(size: int) -> int:
            return max(0x1000, (size + 0xFFF) & ~0xFFF)

        self.machine.mem_map(self.SOURCE, pages(len(source)))
        self.machine.mem_write(self.SOURCE, source)
        self.machine.mem_map(self.OUTPUT, pages(output_size + 1))
        self.machine.mem_map(self.HEAP, 0x01000000)
        self.machine.mem_map(self.CONTEXT, 0x1000)
        self.machine.mem_map(self.STACK, 0x10000)
        self.machine.mem_map(self.STOP, 0x1000)
        self.machine.mem_map(self.ALLOC, 0x1000)
        self.machine.mem_write(self.IMAGE + 0x80C4, struct.pack("<I", self.ALLOC))
        self.machine.mem_write(self.IMAGE + 0x809C, struct.pack("<I", self.FREE))
        self.memory_hook = self.machine.hook_add(
            UC_HOOK_CODE, self._memory_api, begin=self.ALLOC, end=self.FREE
        )

    def close(self) -> None:
        if self.machine is not None:
            self.machine.hook_del(self.memory_hook)
            self.machine = None

    def _memory_api(self, machine: Uc, address: int, _size: int, _user: object) -> None:
        stack = machine.reg_read(UC_X86_REG_ESP)
        return_address = _u32(bytes(machine.mem_read(stack, 4)), 0)
        if address == self.ALLOC:
            requested = _u32(bytes(machine.mem_read(stack + 8, 4)), 0)
            if requested > 0x01000000:
                raise FormatError("GEA decoder requested an excessive model allocation")
            machine.mem_write(self.HEAP, bytes(requested))
            machine.reg_write(UC_X86_REG_EAX, self.HEAP)
            machine.reg_write(UC_X86_REG_ESP, stack + 20)
        else:
            machine.reg_write(UC_X86_REG_EAX, 1)
            machine.reg_write(UC_X86_REG_ESP, stack + 16)
        machine.reg_write(UC_X86_REG_EIP, return_address)

    def _call(self, address: int, ecx: int, edx: int, argument: int | None = None) -> int:
        stack = self.STACK + 0xFF00
        call_stack = struct.pack("<I", self.STOP)
        if argument is not None:
            call_stack += struct.pack("<I", argument)
        self.machine.mem_write(stack, call_stack)
        self.machine.reg_write(UC_X86_REG_ESP, stack)
        self.machine.reg_write(UC_X86_REG_ECX, ecx)
        self.machine.reg_write(UC_X86_REG_EDX, edx)
        try:
            self.machine.emu_start(address, self.STOP, timeout=120_000_000)
        except Exception as error:
            raise FormatError(f"the verified GEA decoder rejected a stream: {error}") from None
        return self.machine.reg_read(UC_X86_REG_EAX)

    def decode_group(self, files: tuple[_GeaFile, ...]) -> tuple[bytes, ...]:
        header_size = self._call(0x401400, self.CONTEXT, self.SOURCE)
        if header_size not in (1, 4, 5):
            raise FormatError("GEA decoder returned an invalid parameter-header size")
        cursor = header_size
        result: list[bytes] = []
        for entry in files:
            chunks = bytearray()
            while len(chunks) < entry.size:
                if cursor + 4 > self.source_size:
                    raise FormatError("GEA block size is truncated")
                packed_size = _u32(
                    bytes(self.machine.mem_read(self.SOURCE + cursor, 4)), 0
                ) & 0x7FFFFFFF
                if cursor + 4 + packed_size > self.source_size:
                    raise FormatError("GEA block is truncated")
                output_size = self._call(
                    0x401470, self.CONTEXT, self.SOURCE + cursor, self.OUTPUT
                )
                if output_size == 0 or len(chunks) + output_size > entry.size:
                    raise FormatError(
                        f"{_decode_name(entry.archive_name)!r}: invalid GEA block output size"
                    )
                chunks.extend(self.machine.mem_read(self.OUTPUT, output_size))
                cursor += 4 + packed_size
            result.append(bytes(chunks))
        if cursor + 4 == self.source_size and bytes(
            self.machine.mem_read(self.SOURCE + cursor, 4)
        ) == b"\0\0\0\0":
            cursor += 4
        if cursor != self.source_size:
            raise FormatError("unexplained bytes follow a GEA group")
        return tuple(result)


def _gea_group_fast(group_data: bytes, files: tuple[_GeaFile, ...]) -> tuple[bytes, ...]:
    _require_gea_decoder()
    if not group_data:
        raise FormatError("a GEA group has no data")
    if group_data[0] == 0:
        header_size = 1
        parameters = b"\0\0\0\0"
        decoder = None
    else:
        if len(group_data) < 4:
            raise FormatError("a GEA group parameter header is truncated")
        parameters = group_data[:4]
        if not (2 <= parameters[1] <= 16 and parameters[0] <= 64):
            raise FormatError("a GEA group has invalid PPMd parameters")
        header_size = 5 if parameters[3] & 4 else 4
        if header_size > len(group_data):
            raise FormatError("a GEA group parameter header is truncated")
        decoder = pyppmd_gentee.Ppmd8gDecoder(parameters[1], parameters[0] << 20)

    cursor = header_size
    previous_stored = False
    block_index = 0
    outputs: list[bytes] = []
    for entry in files:
        chunks = bytearray()
        while len(chunks) < entry.size:
            if cursor + 4 > len(group_data):
                raise FormatError("a GEA block size is truncated")
            packed_field = _u32(group_data, cursor)
            packed_size = packed_field & 0x7FFFFFFF
            cursor += 4
            if cursor + packed_size > len(group_data):
                raise FormatError("a GEA block is truncated")
            payload = group_data[cursor : cursor + packed_size]
            cursor += packed_size
            if block_index and decoder is not None:
                if parameters[3] & 1 and not previous_stored:
                    decoder.lightweight_reset()
                else:
                    decoder.reinit(parameters[1])
            if group_data[0] == 0 or packed_field & 0x80000000:
                output = payload
                previous_stored = True
            else:
                remaining = entry.size - len(chunks)
                try:
                    output = decoder.decode(payload, remaining + 1)
                    if len(output) <= remaining and not decoder.eof and decoder.needs_input:
                        output += decoder.decode(b"\0", remaining + 1 - len(output))
                except (ValueError, MemoryError) as error:
                    raise FormatError(str(error)) from None
                previous_stored = False
            if not output or len(chunks) + len(output) > entry.size:
                raise FormatError("fast GEA decoder did not reproduce the declared file size")
            chunks.extend(output)
            block_index += 1
        outputs.append(bytes(chunks))
    if cursor + 4 == len(group_data) and group_data[cursor:] == b"\0\0\0\0":
        cursor += 4
    if cursor != len(group_data):
        raise FormatError("unexplained bytes follow a GEA group")
    return tuple(outputs)


def _dos_filetime(date_word: int, time_word: int) -> int:
    try:
        value = datetime(
            1980 + (date_word >> 9),
            (date_word >> 5) & 15,
            date_word & 31,
            time_word >> 11,
            (time_word >> 5) & 63,
            (time_word & 31) * 2,
            tzinfo=timezone.utc,
        )
    except ValueError:
        raise FormatError("a cabinet file has an invalid DOS timestamp") from None
    epoch = datetime(1601, 1, 1, tzinfo=timezone.utc)
    return int((value - epoch).total_seconds() * 10_000_000)


def _expand_cabinet(cabinet: bytes) -> tuple[_Entry, ...]:
    if len(cabinet) < 36 or cabinet[:4] != b"MSCF":
        raise FormatError("a GEA cabinet group does not contain a cabinet")
    declared_size = _u32(cabinet, 8)
    file_table = _u32(cabinet, 16)
    folder_count = _u16(cabinet, 26)
    file_count = _u16(cabinet, 28)
    flags = _u16(cabinet, 30)
    cabinet_index = _u16(cabinet, 34)
    if declared_size != len(cabinet):
        raise FormatError(
            f"cabinet declares {declared_size} bytes but contains {len(cabinet)}"
        )
    if not folder_count or cabinet_index != 0 or flags & 3:
        raise FormatError("multi-cabinet payloads are not supported by this generation")
    if flags & ~7:
        raise FormatError("cabinet header contains unknown flags")
    header_end = 36
    if flags & 4:
        if len(cabinet) < 40:
            raise FormatError("cabinet reserve header is truncated")
        reserve_size = _u16(cabinet, 36)
        header_end = 40 + reserve_size
    if not (header_end <= file_table <= len(cabinet)):
        raise FormatError("cabinet file table offset is invalid")

    descriptions: list[tuple[bytes, Path, int, int, int]] = []
    cursor = file_table
    total_size = 0
    for _index in range(file_count):
        if cursor + 16 > len(cabinet):
            raise FormatError("cabinet file record is truncated")
        size, _folder_offset = struct.unpack_from("<II", cabinet, cursor)
        folder_index, date_word, time_word, attributes = struct.unpack_from(
            "<HHHH", cabinet, cursor + 8
        )
        if folder_index >= folder_count:
            raise FormatError("cabinet file uses an external continuation folder")
        name_end = cabinet.find(b"\0", cursor + 16)
        if name_end < 0:
            raise FormatError("cabinet filename is unterminated")
        raw_name = cabinet[cursor + 16 : name_end]
        if attributes & 0x80:
            try:
                relative_name = _relative_name_text(raw_name.decode("utf-8"))
            except UnicodeDecodeError:
                raise FormatError("cabinet UTF-8 filename is invalid") from None
        else:
            relative_name = _relative_name(raw_name)
        descriptions.append(
            (raw_name, relative_name, size, attributes & 0x27, _dos_filetime(date_word, time_word))
        )
        total_size += size
        cursor = name_end + 1

    executable = shutil.which("cabextract")
    if executable is None:
        raise FormatError("nested LZX cabinets require the external cabextract utility")
    temporary_name = None
    try:
        with tempfile.NamedTemporaryFile(prefix="createinstall-", suffix=".cab", delete=False) as temporary:
            temporary.write(cabinet)
            temporary_name = temporary.name
        tested = subprocess.run(
            [executable, "-q", "-t", temporary_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120,
            check=False,
        )
        if tested.returncode:
            message = tested.stderr.decode("utf-8", "replace").strip()
            raise FormatError(f"cabinet integrity test failed: {message or 'cabextract error'}")
        unpacked = subprocess.run(
            [executable, "-q", "-p", temporary_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120,
            check=False,
        )
        if unpacked.returncode:
            message = unpacked.stderr.decode("utf-8", "replace").strip()
            raise FormatError(f"cabinet extraction failed: {message or 'cabextract error'}")
    except subprocess.TimeoutExpired:
        raise FormatError("cabinet extraction timed out") from None
    finally:
        if temporary_name is not None:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass
    if len(unpacked.stdout) != total_size:
        raise FormatError(
            f"cabinet produced {len(unpacked.stdout)} bytes, expected {total_size}"
        )
    result: list[_Entry] = []
    cursor = 0
    for raw_name, relative_name, size, attributes, filetime in descriptions:
        content = unpacked.stdout[cursor : cursor + size]
        cursor += size
        result.append(
            _Entry(
                archive_name=raw_name,
                relative_name=relative_name,
                attributes=attributes,
                filetime=filetime,
                storage="cabinet",
                data=content,
            )
        )
    return tuple(result)


def _parse_gea_groups(info: bytes) -> tuple[_GeaGroup, ...]:
    groups: list[_GeaGroup] = []
    cursor = 0
    while cursor < len(info):
        if cursor + 12 > len(info):
            raise FormatError("GEA group descriptor is truncated")
        descriptor_size = _u16(info, cursor)
        payload_size = _u32(info, cursor + 2)
        group_id = _u32(info, cursor + 6)
        file_count = _u16(info, cursor + 10)
        end = cursor + descriptor_size
        if descriptor_size < 13 or end > len(info) or group_id == 0:
            raise FormatError("GEA group descriptor size or identifier is invalid")
        position = cursor + 12
        cabinet_expanded_size = None
        password_crc = None
        while True:
            if position >= end:
                raise FormatError("GEA group option list is unterminated")
            tag = info[position]
            position += 1
            if tag == 0xFF:
                break
            if tag == 1:
                if position + 4 > end or password_crc is not None:
                    raise FormatError("invalid GEA password-protection option")
                password_crc = _u32(info, position)
                position += 4
            elif tag == 2:
                if position + 6 > end:
                    raise FormatError("truncated GEA group transform")
                kind, algorithm = info[position], info[position + 1]
                expanded_size = _u32(info, position + 2)
                position += 6
                if (kind, algorithm) != (1, 3) or cabinet_expanded_size is not None:
                    raise FormatError("unsupported GEA group transform")
                cabinet_expanded_size = expanded_size
            else:
                raise FormatError(f"unknown GEA group option tag {tag}")

        files: list[_GeaFile] = []
        for _index in range(file_count):
            start = position
            if start + 19 > end:
                raise FormatError("GEA file descriptor is truncated")
            record_size = _u16(info, start)
            size = _u32(info, start + 2)
            volume = info[start + 6]
            attributes = _u32(info, start + 7)
            filetime = struct.unpack_from("<Q", info, start + 11)[0]
            record_end = start + record_size
            if record_size < 21 or record_end > end or volume != 1:
                raise FormatError("GEA file descriptor size or volume is invalid")
            position = start + 19
            version_high = version_low = 0
            archive_name = None
            while position < record_end:
                tag = info[position]
                position += 1
                if tag == 2:
                    if position + 8 > record_end or version_high or version_low:
                        raise FormatError("invalid GEA version tag")
                    version_high, version_low = struct.unpack_from("<II", info, position)
                    position += 8
                elif tag == 4:
                    name_end = info.find(b"\0", position, record_end)
                    if name_end < 0 or archive_name is not None:
                        raise FormatError("invalid GEA filename tag")
                    archive_name = info[position:name_end]
                    position = name_end + 1
                else:
                    raise FormatError(f"unknown GEA file option tag {tag}")
            if position != record_end or not archive_name:
                raise FormatError("GEA file descriptor has no exact filename boundary")
            _relative_name(archive_name)
            files.append(
                _GeaFile(
                    archive_name=archive_name,
                    size=size,
                    attributes=attributes,
                    filetime=filetime,
                    version_high=version_high,
                    version_low=version_low,
                )
            )
        if position != end:
            raise FormatError("unexplained bytes follow GEA file descriptors")
        if cabinet_expanded_size is not None and len(files) != 1:
            raise FormatError("a GEA cabinet transform must describe exactly one file")
        groups.append(
            _GeaGroup(
                group_id,
                payload_size,
                tuple(files),
                cabinet_expanded_size,
                password_crc,
            )
        )
        cursor = end
    if cursor != len(info):
        raise FormatError("unexplained bytes follow the GEA description stream")
    return tuple(groups)


def _parse_gea(data: bytes) -> _Archive:
    pe_end = _pe_overlay_offset(data)
    globals_offset = _pe_rva_offset(data, 0x5000)
    if globals_offset + 28 > pe_end:
        raise FormatError("GEA loader constants lie outside the PE image")
    initial_size, declared_pe_end, first_size, second_size, checksum, loader_flags, data_offset = struct.unpack_from(
        "<7I", data, globals_offset
    )
    text_section = next(
        (item for item in _pe_sections(data) if item[0] == b".text"), None
    )
    if text_section is None:
        raise FormatError("GEA loader has no .text section")
    _name, _rva, text_size, text_offset = text_section
    if hashlib.sha256(data[text_offset : text_offset + text_size]).hexdigest() != _GEA_STUB_TEXT_SHA256:
        raise FormatError("unsupported GEA CreateInstall loader revision")
    if (
        declared_pe_end != pe_end
        or initial_size != pe_end + first_size + second_size
        or initial_size > len(data)
        or loader_flags != 1
        or data_offset != globals_offset
    ):
        raise FormatError("GEA loader size constants are contradictory")
    if data[pe_end : pe_end + 4] != b"\x02\x06\x0a\x04":
        raise FormatError("not the supported GEA CreateInstall generation")
    actual_checksum = (~zlib.crc32(data[pe_end:initial_size])) & 0xFFFFFFFF
    if checksum != actual_checksum:
        raise FormatError("GEA packed loader/configuration checksum is wrong")
    if hashlib.sha256(data[pe_end : pe_end + first_size]).hexdigest() != _GEA_RUNTIME_SHA256:
        raise FormatError("unsupported GEA embedded-runtime revision")
    second_offset = pe_end + first_size
    configuration = _raw_ppmd(
        data[second_offset : second_offset + second_size], 16 * 1024 * 1024
    )

    gea_offset = initial_size
    if gea_offset + 39 > len(data) or data[gea_offset : gea_offset + 4] != b"GEA\0":
        raise FormatError("GEA archive header is missing")
    if (
        _u16(data, gea_offset + 4) != 31
        or _u16(data, gea_offset + 6) != 1
        or _u32(data, gea_offset + 8) != 0
        or data[gea_offset + 16 : gea_offset + 19] != b"\x01\x01\0"
        or _u32(data, gea_offset + 27) != 0xFFFFFFFF
    ):
        raise FormatError("unsupported GEA archive-header revision")
    gea_size = _u32(data, gea_offset + 12)
    gea_end = gea_offset + gea_size
    if gea_end > len(data):
        raise FormatError("GEA archive physical-size field exceeds the input")
    security = _pe_security_range(data)
    if gea_end != len(data):
        aligned_gea_end = (gea_end + 7) & ~7
        if (
            security is None
            or security[0] != aligned_gea_end
            or any(data[gea_end:aligned_gea_end])
        ):
            raise FormatError("unexplained bytes follow the GEA archive")
    rotation = _u32(data, gea_offset + 19)
    logical_size = _u32(data, gea_offset + 23)
    packed_info_size = _u32(data, gea_offset + 35)
    info_end = gea_offset + 39 + packed_info_size
    if info_end > gea_end:
        raise FormatError("GEA description stream is truncated")
    info = _raw_ppmd(data[gea_offset + 31 : info_end], 4 * 1024 * 1024)
    groups = _parse_gea_groups(info)
    if rotation > logical_size or info_end + logical_size != gea_end:
        raise FormatError("GEA data size or rotation is contradictory")
    physical = data[info_end:gea_end]
    logical = physical[rotation:] + physical[:rotation]
    if sum(group.payload_size for group in groups) != len(logical):
        raise FormatError("GEA group payload sizes do not cover the data region")

    entries: list[_Entry] = []
    group_cursor = 0
    decoder_fallbacks = 0
    cabinet_groups = 0
    for group in groups:
        group_data = logical[group_cursor : group_cursor + group.payload_size]
        group_cursor += group.payload_size
        if not group_data:
            raise FormatError("GEA group has no payload")
        if group.password_crc is not None:
            raise FormatError(
                "password-protected GEA groups require the original installation password"
            )
        try:
            contents = _gea_group_fast(group_data, group.files)
        except FormatError:
            decoder_fallbacks += 1
            verified_decoder = _VerifiedStubDecoder(
                data, group_data, max((item.size for item in group.files), default=0)
            )
            try:
                contents = verified_decoder.decode_group(group.files)
            finally:
                verified_decoder.close()
                del verified_decoder
                gc.collect()
        if group.cabinet_expanded_size is not None:
            cabinet_groups += 1
            cabinet_entries = _expand_cabinet(contents[0])
            if sum(len(item.data or b"") for item in cabinet_entries) != group.cabinet_expanded_size:
                raise FormatError("GEA cabinet expanded-size option is contradictory")
            if group.group_id == 1:
                entries.extend(cabinet_entries)
            continue
        if group.group_id != 1:
            continue
        for item, content in zip(group.files, contents, strict=True):
            entries.append(
                _Entry(
                    archive_name=item.archive_name,
                    relative_name=_relative_name(item.archive_name),
                    attributes=item.attributes,
                    filetime=item.filetime,
                    storage="gea",
                    data=content,
                )
            )

    canonical: dict[str, Path] = {}
    normalized: list[_Entry] = []
    for entry in entries:
        key = entry.relative_name.as_posix().casefold()
        relative_name = canonical.setdefault(key, entry.relative_name)
        normalized.append(
            _Entry(
                archive_name=entry.archive_name,
                relative_name=relative_name,
                attributes=entry.attributes,
                filetime=entry.filetime,
                storage=entry.storage,
                data=entry.data,
            )
        )
    expanded_size = sum(len(entry.data or b"") for entry in normalized)
    metadata = {
        "format_generation": "gea-1.0",
        "declared_input_size": len(data),
        "declared_expanded_size": expanded_size,
        "configuration_size": len(configuration),
        "runtime_packed_size": first_size,
        "configuration_packed_size": second_size,
        "gea_offset": gea_offset,
        "authenticode_size": security[1] if security else 0,
        "authenticode_alignment_size": (security[0] - gea_end) if security else 0,
        "gea_description_packed_size": packed_info_size,
        "gea_description_size": len(info),
        "gea_rotation": rotation,
        "gea_group_count": len(groups),
        "gea_install_record_count": sum(
            len(group.files) for group in groups if group.group_id == 1
        ),
        "cabinet_group_count": cabinet_groups,
        "password_protected_group_count": sum(
            group.password_crc is not None for group in groups
        ),
        "verified_decoder_fallback_count": decoder_fallbacks,
    }
    return _Archive(
        input_size=len(data),
        pe_end=pe_end,
        runtime_size=first_size,
        header_offset=gea_offset,
        expanded_size=expanded_size,
        configuration=configuration,
        directories=(),
        entries=tuple(normalized),
        metadata=metadata,
    )


def _recover_gea(data: bytes, strict_error: FormatError) -> _Archive:
    """Recover independently decodable groups from an identified GEA revision."""
    pe_end = _pe_overlay_offset(data)
    globals_offset = _pe_rva_offset(data, 0x5000)
    if globals_offset + 28 > pe_end:
        raise strict_error
    initial_size, declared_pe_end, first_size, second_size, _checksum, loader_flags, data_offset = struct.unpack_from(
        "<7I", data, globals_offset
    )
    text_section = next(
        (item for item in _pe_sections(data) if item[0] == b".text"), None
    )
    if text_section is None:
        raise strict_error
    _name, _rva, text_size, text_offset = text_section
    if hashlib.sha256(data[text_offset : text_offset + text_size]).hexdigest() != _GEA_STUB_TEXT_SHA256:
        raise strict_error
    if (
        declared_pe_end != pe_end
        or loader_flags != 1
        or data_offset != globals_offset
        or first_size == 0
        or pe_end + first_size > len(data)
        or hashlib.sha256(data[pe_end : pe_end + first_size]).hexdigest()
        != _GEA_RUNTIME_SHA256
    ):
        raise strict_error

    metadata: dict[str, object] = {
        "format_generation": "gea-1.0",
        "partial_extraction": True,
        "recovery_error": str(strict_error),
        "declared_input_size": len(data),
        "runtime_packed_size": first_size,
        "configuration_packed_size": second_size,
        "gea_offset": initial_size,
        "recovered_group_errors": [],
    }

    def empty(stop: str, configuration: bytes = b"") -> _Archive:
        metadata["recovery_stop"] = stop
        metadata["declared_expanded_size"] = 0
        return _Archive(
            len(data), pe_end, first_size, initial_size, 0, configuration, (), (), metadata
        )

    if initial_size != pe_end + first_size + second_size or initial_size > len(data):
        return empty("GEA loader size constants do not locate a complete archive")
    second_offset = pe_end + first_size
    try:
        configuration = _raw_ppmd(
            data[second_offset : second_offset + second_size], 16 * 1024 * 1024
        )
    except FormatError as error:
        configuration = b""
        metadata["configuration_recovery_error"] = str(error)
    metadata["configuration_size"] = len(configuration)

    gea_offset = initial_size
    if gea_offset + 39 > len(data) or data[gea_offset : gea_offset + 4] != b"GEA\0":
        return empty("GEA archive header is truncated or missing", configuration)
    if (
        _u16(data, gea_offset + 4) != 31
        or _u16(data, gea_offset + 6) != 1
        or _u32(data, gea_offset + 8) != 0
        or data[gea_offset + 16 : gea_offset + 19] != b"\x01\x01\0"
        or _u32(data, gea_offset + 27) != 0xFFFFFFFF
    ):
        return empty("GEA archive header is not the supported revision", configuration)
    gea_size = _u32(data, gea_offset + 12)
    gea_end = gea_offset + gea_size
    if gea_end > len(data):
        return empty("GEA archive data is physically truncated", configuration)
    rotation = _u32(data, gea_offset + 19)
    logical_size = _u32(data, gea_offset + 23)
    packed_info_size = _u32(data, gea_offset + 35)
    info_end = gea_offset + 39 + packed_info_size
    if info_end > gea_end:
        return empty("GEA description stream is truncated", configuration)
    try:
        info = _raw_ppmd(data[gea_offset + 31 : info_end], 4 * 1024 * 1024)
        groups = _parse_gea_groups(info)
    except FormatError as error:
        return empty(f"GEA description cannot be recovered: {error}", configuration)
    if rotation > logical_size or info_end + logical_size != gea_end:
        return empty("GEA data size or rotation is contradictory", configuration)
    physical = data[info_end:gea_end]
    logical = physical[rotation:] + physical[:rotation]
    if sum(group.payload_size for group in groups) != len(logical):
        return empty("GEA group sizes do not cover the data region", configuration)

    entries: list[_Entry] = []
    group_cursor = 0
    cabinet_groups = 0
    recovered_groups = 0
    group_errors: list[dict[str, object]] = []
    for group_index, group in enumerate(groups):
        group_data = logical[group_cursor : group_cursor + group.payload_size]
        group_cursor += group.payload_size
        if group.password_crc is not None:
            group_errors.append(
                {
                    "index": group_index,
                    "group_id": group.group_id,
                    "error": (
                        "password-protected GEA group requires the original "
                        "installation password"
                    ),
                }
            )
            continue
        try:
            contents = _gea_group_fast(group_data, group.files)
        except FormatError:
            try:
                verified_decoder = _VerifiedStubDecoder(
                    data, group_data, max((item.size for item in group.files), default=0)
                )
                try:
                    contents = verified_decoder.decode_group(group.files)
                finally:
                    verified_decoder.close()
                    del verified_decoder
                    gc.collect()
            except FormatError as error:
                group_errors.append(
                    {"index": group_index, "group_id": group.group_id, "error": str(error)}
                )
                continue
        try:
            if group.cabinet_expanded_size is not None:
                cabinet_entries = _expand_cabinet(contents[0])
                if sum(len(item.data or b"") for item in cabinet_entries) != group.cabinet_expanded_size:
                    raise FormatError("GEA cabinet expanded-size option is contradictory")
                cabinet_groups += 1
                if group.group_id == 1:
                    entries.extend(cabinet_entries)
            elif group.group_id == 1:
                for item, content in zip(group.files, contents, strict=True):
                    entries.append(
                        _Entry(
                            archive_name=item.archive_name,
                            relative_name=_relative_name(item.archive_name),
                            attributes=item.attributes,
                            filetime=item.filetime,
                            storage="gea",
                            data=content,
                        )
                    )
            recovered_groups += 1
        except (FormatError, ValueError) as error:
            group_errors.append(
                {"index": group_index, "group_id": group.group_id, "error": str(error)}
            )

    canonical: dict[str, Path] = {}
    normalized: list[_Entry] = []
    for entry in entries:
        key = entry.relative_name.as_posix().casefold()
        relative_name = canonical.setdefault(key, entry.relative_name)
        normalized.append(
            _Entry(
                archive_name=entry.archive_name,
                relative_name=relative_name,
                attributes=entry.attributes,
                filetime=entry.filetime,
                storage=entry.storage,
                data=entry.data,
            )
        )
    expanded_size = sum(len(entry.data or b"") for entry in normalized)
    protected_groups = sum(group.password_crc is not None for group in groups)
    damaged_groups = len(group_errors) - protected_groups
    recovery_parts = []
    if protected_groups:
        recovery_parts.append(f"{protected_groups} password-protected group(s) skipped")
    if damaged_groups:
        recovery_parts.append(f"{damaged_groups} damaged group(s) skipped")
    metadata.update(
        {
            "declared_expanded_size": expanded_size,
            "gea_description_packed_size": packed_info_size,
            "gea_description_size": len(info),
            "gea_rotation": rotation,
            "gea_group_count": len(groups),
            "recovered_group_count": recovered_groups,
            "cabinet_group_count": cabinet_groups,
            "password_protected_group_count": protected_groups,
            "recovered_group_errors": group_errors,
            "recovery_stop": (
                "; ".join(recovery_parts) if recovery_parts else str(strict_error)
            ),
        }
    )
    return _Archive(
        input_size=len(data),
        pe_end=pe_end,
        runtime_size=first_size,
        header_offset=gea_offset,
        expanded_size=expanded_size,
        configuration=configuration,
        directories=(),
        entries=tuple(normalized),
        metadata=metadata,
    )


def _parse_classic(data: bytes) -> _Archive:
    pe_end = _pe_overlay_offset(data)
    if data[pe_end : pe_end + 4] != b"aWAW":
        raise FormatError("not the supported classic CreateInstall family")
    runtime_size = _runtime_size(data, pe_end)
    runtime, runtime_consumed = _Codec(
        memoryview(data)[pe_end : pe_end + runtime_size], 16 * 1024 * 1024
    ).decode()
    if runtime[:2] != b"MZ" or _pe_overlay_offset(runtime) != len(runtime):
        raise FormatError("embedded runtime does not expand to one complete PE DLL")
    header_offset = pe_end + runtime_size
    header_size = _header_size(runtime_size)
    header = data[header_offset : header_offset + header_size]
    declared_size, expanded_size, configuration_size = struct.unpack_from("<III", header)
    if declared_size != len(data):
        raise FormatError(
            f"header declares {declared_size} bytes but input has {len(data)} bytes"
        )
    configuration_offset = header_offset + header_size
    data_offset = configuration_offset + configuration_size
    if data_offset > len(data):
        raise FormatError("configuration block extends beyond the input")
    configuration = data[configuration_offset:data_offset]
    if not configuration or configuration[-1] != 0:
        raise FormatError("configuration string table is empty or unterminated")

    cursor = data_offset
    entries: list[_Entry] = []
    directories: list[Path] = []
    canonical_paths: dict[str, tuple[Path, str]] = {}
    total_output_size = 0
    record_counts = {"file": 0, "directory": 0, "root": 0, "end": 0}
    while True:
        if cursor + 17 > len(data):
            raise FormatError("record header is truncated")
        record = data[cursor : cursor + 17]
        cursor += 17
        record_type = record[0]
        name_size = _u16(record, 15)
        if record_type == 4:
            record_counts["end"] += 1
            break
        if record_type == 3:
            record_counts["root"] += 1
            continue
        if record_type not in (1, 2):
            raise FormatError(f"unknown archive record type {record_type}")
        if cursor + name_size > len(data):
            raise FormatError("record path is truncated")
        archive_name = data[cursor : cursor + name_size]
        cursor += name_size
        relative_name = _relative_name(archive_name)
        path_key = relative_name.as_posix().casefold()
        kind = "directory" if record_type == 2 else "file"
        previous = canonical_paths.get(path_key)
        if previous is None:
            canonical_paths[path_key] = (relative_name, kind)
        else:
            relative_name, previous_kind = previous
            if previous_kind != kind:
                raise FormatError("a path is used as both a file and a directory")
        if record_type == 2:
            record_counts["directory"] += 1
            directories.append(relative_name)
            continue

        record_counts["file"] += 1
        if cursor + 4 > len(data):
            raise FormatError("file size field is truncated")
        output_size = _u32(data, cursor)
        cursor += 4
        total_output_size += output_size
        if output_size > expanded_size or total_output_size > expanded_size:
            raise FormatError("file sizes exceed the header's expanded-size total")
        if record[14] != 0:
            if cursor + output_size > len(data):
                raise FormatError("stored file data is truncated")
            content = data[cursor : cursor + output_size]
            cursor += output_size
            storage = "stored"
        else:
            chunks = bytearray()
            try:
                while len(chunks) < output_size:
                    content, consumed = _Codec(
                        memoryview(data)[cursor:], output_size - len(chunks)
                    ).decode()
                    if not content:
                        raise FormatError("compressed file contains an empty intermediate stream")
                    chunks.extend(content)
                    cursor += consumed
            except FormatError as error:
                raise FormatError(f"{_decode_name(archive_name)!r}: {error}") from None
            content = bytes(chunks)
            storage = "compressed"
        entries.append(
            _Entry(
                archive_name=archive_name,
                relative_name=relative_name,
                attributes=_u32(record, 2),
                filetime=struct.unpack_from("<Q", record, 6)[0],
                storage=storage,
                data=content,
            )
        )

    if cursor != len(data):
        raise FormatError(f"{len(data) - cursor} unexplained byte(s) follow the end record")
    if total_output_size != expanded_size:
        raise FormatError(
            f"file records total {total_output_size} bytes, not the header's "
            f"declared {expanded_size} expanded bytes"
        )
    metadata = {
        "format_generation": "classic-awaw",
        "declared_input_size": declared_size,
        "declared_expanded_size": expanded_size,
        "configuration_size": configuration_size,
        "runtime_expanded_size": len(runtime),
        "runtime_compressed_size": runtime_consumed,
        "runtime_padding_size": runtime_size - runtime_consumed,
        "header_hex": header.hex(),
        "record_counts": record_counts,
    }
    return _Archive(
        input_size=len(data),
        pe_end=pe_end,
        runtime_size=runtime_size,
        header_offset=header_offset,
        expanded_size=expanded_size,
        configuration=configuration,
        directories=tuple(directories),
        entries=tuple(entries),
        metadata=metadata,
    )


def _recover_classic(data: bytes, strict_error: FormatError) -> _Archive:
    """Recover only complete records from a positively identified classic file."""
    pe_end = _pe_overlay_offset(data)
    if data[pe_end : pe_end + 4] != b"aWAW":
        raise strict_error
    runtime_size = _declared_runtime_size(data, pe_end)
    header_size = _header_size(runtime_size)
    header_offset = pe_end + runtime_size
    base_metadata: dict[str, object] = {
        "format_generation": "classic-awaw",
        "partial_extraction": True,
        "recovery_error": str(strict_error),
        "declared_input_size": None,
        "declared_expanded_size": None,
        "configuration_size": 0,
        "record_counts": {"file": 0, "directory": 0, "root": 0, "end": 0},
    }

    # A recognized loader may itself be the final surviving region of a
    # truncated installer.  There are then no archive records to recover.
    if header_offset + header_size > len(data):
        base_metadata["recovery_stop"] = "setup/archive header is truncated"
        return _Archive(
            len(data), pe_end, runtime_size, header_offset, 0, b"", (), (), base_metadata
        )

    try:
        runtime, runtime_consumed = _Codec(
            memoryview(data)[pe_end : pe_end + runtime_size], 16 * 1024 * 1024
        ).decode()
        if runtime[:2] != b"MZ" or _pe_overlay_offset(runtime) != len(runtime):
            raise FormatError("embedded runtime is not one complete PE DLL")
    except FormatError as error:
        base_metadata["recovery_stop"] = str(error)
        return _Archive(
            len(data), pe_end, runtime_size, header_offset, 0, b"", (), (), base_metadata
        )

    header = data[header_offset : header_offset + header_size]
    declared_size, declared_expanded_size, configuration_size = struct.unpack_from(
        "<III", header
    )
    base_metadata.update(
        {
            "declared_input_size": declared_size,
            "declared_expanded_size": declared_expanded_size,
            "configuration_size": configuration_size,
            "runtime_expanded_size": len(runtime),
            "runtime_compressed_size": runtime_consumed,
            "runtime_padding_size": runtime_size - runtime_consumed,
            "header_hex": header.hex(),
        }
    )
    configuration_offset = header_offset + header_size
    data_offset = configuration_offset + configuration_size
    if data_offset > len(data):
        base_metadata["recovery_stop"] = "configuration block is truncated"
        return _Archive(
            len(data), pe_end, runtime_size, header_offset, 0, b"", (), (), base_metadata
        )
    configuration = data[configuration_offset:data_offset]

    cursor = data_offset
    entries: list[_Entry] = []
    directories: list[Path] = []
    canonical_paths: dict[str, tuple[Path, str]] = {}
    record_counts = {"file": 0, "directory": 0, "root": 0, "end": 0}
    recovered_size = 0
    recovery_stop = "archive ended without a complete end record"
    while cursor < len(data):
        record_start = cursor
        archive_name: bytes | None = None
        try:
            if cursor + 17 > len(data):
                raise FormatError("record header is truncated")
            record = data[cursor : cursor + 17]
            cursor += 17
            record_type = record[0]
            name_size = _u16(record, 15)
            if record_type == 4:
                record_counts["end"] += 1
                recovery_stop = (
                    f"{len(data) - cursor} unexplained byte(s) follow the end record"
                    if cursor != len(data)
                    else str(strict_error)
                )
                break
            if record_type == 3:
                record_counts["root"] += 1
                continue
            if record_type not in (1, 2):
                raise FormatError(f"unknown archive record type {record_type}")
            if cursor + name_size > len(data):
                raise FormatError("record path is truncated")
            archive_name = data[cursor : cursor + name_size]
            cursor += name_size
            relative_name = _relative_name(archive_name)
            path_key = relative_name.as_posix().casefold()
            kind = "directory" if record_type == 2 else "file"
            previous = canonical_paths.get(path_key)
            if previous is None:
                canonical_paths[path_key] = (relative_name, kind)
            else:
                relative_name, previous_kind = previous
                if previous_kind != kind:
                    raise FormatError("a path is used as both a file and a directory")
            if record_type == 2:
                record_counts["directory"] += 1
                directories.append(relative_name)
                continue

            if cursor + 4 > len(data):
                raise FormatError("file size field is truncated")
            output_size = _u32(data, cursor)
            cursor += 4
            if declared_expanded_size and output_size > declared_expanded_size:
                raise FormatError("file size exceeds the archive expanded-size field")
            if record[14] != 0:
                if cursor + output_size > len(data):
                    raise FormatError("stored file data is truncated")
                content = data[cursor : cursor + output_size]
                cursor += output_size
                storage = "stored"
            else:
                chunks = bytearray()
                while len(chunks) < output_size:
                    content, consumed = _Codec(
                        memoryview(data)[cursor:], output_size - len(chunks)
                    ).decode()
                    if not content:
                        raise FormatError("compressed file contains an empty intermediate stream")
                    chunks.extend(content)
                    cursor += consumed
                content = bytes(chunks)
                storage = "compressed"
            entries.append(
                _Entry(
                    archive_name=archive_name,
                    relative_name=relative_name,
                    attributes=_u32(record, 2),
                    filetime=struct.unpack_from("<Q", record, 6)[0],
                    storage=storage,
                    data=content,
                )
            )
            record_counts["file"] += 1
            recovered_size += len(content)
        except FormatError as error:
            name = _decode_name(archive_name) if archive_name is not None else None
            recovery_stop = f"{name!r}: {error}" if name else str(error)
            cursor = record_start
            break

    base_metadata["record_counts"] = record_counts
    base_metadata["recovery_stop"] = recovery_stop
    base_metadata["recovered_input_offset"] = cursor
    base_metadata["recovered_expanded_size"] = recovered_size
    return _Archive(
        input_size=len(data),
        pe_end=pe_end,
        runtime_size=runtime_size,
        header_offset=header_offset,
        expanded_size=recovered_size,
        configuration=configuration,
        directories=tuple(directories),
        entries=tuple(entries),
        metadata=base_metadata,
    )


def _parse(data: bytes) -> _Archive:
    pe_end = _pe_overlay_offset(data)
    signature = data[pe_end : pe_end + 4]
    if signature == b"aWAW":
        return _parse_classic(data)
    if signature == b"\x02\x06\x0a\x04":
        return _parse_gea(data)
    raise FormatError("not a supported CreateInstall generation")


def _recover_supported(data: bytes, strict_error: FormatError) -> _Archive:
    pe_end = _pe_overlay_offset(data)
    signature = data[pe_end : pe_end + 4]
    if signature == b"aWAW":
        return _recover_classic(data, strict_error)
    # GEA recovery is reached only after the exact loader/runtime revision has
    # been positively identified.  A different executable revision is not a
    # damaged instance of the supported format.
    if signature == b"\x02\x06\x0a\x04":
        return _recover_gea(data, strict_error)
    raise strict_error


def _write(archive: _Archive, output_dir: Path, include_metadata: bool) -> None:
    if output_dir.is_symlink():
        raise OSError(f"refusing symlink output directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_dir.chmod(output_dir.stat().st_mode | stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP)

    def ensure_directory(relative: Path) -> Path:
        current = output_dir
        for component in relative.parts:
            current = current / component
            if current.is_symlink():
                raise OSError(f"refusing symlink output directory: {current}")
            if current.exists() and not current.is_dir():
                raise OSError(f"output path is not a directory: {current}")
            current.mkdir(exist_ok=True)
            current.chmod(
                current.stat().st_mode
                | stat.S_IRUSR
                | stat.S_IRGRP
                | stat.S_IWUSR
                | stat.S_IWGRP
                | stat.S_IXUSR
                | stat.S_IXGRP
            )
        return current

    for directory in archive.directories:
        ensure_directory(directory)
    for entry in archive.entries:
        destination = output_dir / entry.relative_name
        ensure_directory(entry.relative_name.parent)
        if destination.is_symlink():
            raise OSError(f"refusing symlink output path: {destination}")
        if destination.exists():
            if not destination.is_file():
                raise OSError(f"output path is not a regular file: {destination}")
            destination.chmod(
                destination.stat().st_mode | stat.S_IWUSR | stat.S_IWGRP
            )
        destination.write_bytes(entry.data if entry.data is not None else b"")
        timestamp = (entry.filetime - 116444736000000000) / 10_000_000
        try:
            os.utime(destination, (timestamp, timestamp))
        except (OSError, OverflowError, ValueError):
            pass
        mode = destination.stat().st_mode | stat.S_IRUSR | stat.S_IRGRP
        if entry.attributes & 0x01:
            destination.chmod(mode & ~stat.S_IWUSR & ~stat.S_IWGRP & ~stat.S_IWOTH)
        else:
            destination.chmod(mode | stat.S_IWUSR | stat.S_IWGRP)
    if include_metadata:
        details = dict(archive.metadata)
        details["configuration_hex"] = archive.configuration.hex()
        details["files"] = [
            {
                "archive_name_hex": entry.archive_name.hex(),
                "output_name": entry.relative_name.as_posix(),
                "size": len(entry.data or b""),
                "storage": entry.storage,
                "attributes": entry.attributes,
                "filetime": entry.filetime,
                "timestamp_utc": _filetime(entry.filetime),
            }
            for entry in archive.entries
        ]
        metadata_path = output_dir / "createInstall-metadata.json"
        metadata_path.write_text(
            json.dumps(details, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        metadata_path.chmod(
            metadata_path.stat().st_mode
            | stat.S_IRUSR
            | stat.S_IRGRP
            | stat.S_IWUSR
            | stat.S_IWGRP
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        usage="createInstall.py [--all] [--strict] <inputFile> <outputDir>",
        description=(
            "Extract a supported CreateInstall archive, recovering complete files "
            "from damaged inputs by default."
        ),
    )
    parser.add_argument("--all", action="store_true", help="also write generated metadata")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="reject a damaged supported archive instead of recovering complete files",
    )
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputDir", type=Path)
    arguments = parser.parse_args(argv)
    partial = False
    try:
        data = arguments.inputFile.read_bytes()
        try:
            archive = _parse(data)
        except FormatError as error:
            if arguments.strict:
                raise
            archive = _recover_supported(data, error)
            partial = True
        _write(archive, arguments.outputDir, arguments.all)
    except (FormatError, OSError) as error:
        print(f"createInstall.py: {error}", file=sys.stderr)
        return 1
    if partial:
        print(
            f"createInstall.py: partial recovery: {archive.metadata['recovery_error']}; "
            f"stopped at: {archive.metadata.get('recovery_stop', 'unknown damage')}",
            file=sys.stderr,
        )
    action = "partially extracted" if partial else "extracted"
    print(f"{action} {len(archive.entries)} file(s) to {arguments.outputDir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

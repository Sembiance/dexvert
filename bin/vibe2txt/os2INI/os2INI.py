#!/usr/bin/env python3
# Vibe coded by Codex
"""Convert an OS/2 binary INI/profile file into an exact text dump."""

from __future__ import annotations

import argparse
import os
import pathlib
import struct
import sys
import tempfile
from dataclasses import dataclass
from typing import BinaryIO, Iterable, NoReturn


class ParseError(ValueError):
    pass


@dataclass(frozen=True)
class Segment:
    start: int
    end: int
    kind: str


@dataclass(frozen=True)
class FreeDescriptor:
    offset: int
    next_offset: int
    payload_offset: int
    payload_length: int


@dataclass(frozen=True)
class KeyRecord:
    offset: int
    next_offset: int
    name_length: int
    name_capacity: int
    name_offset: int
    data_capacity: int
    data_length: int
    data_offset: int
    name_allocation: bytes
    data_allocation: bytes


@dataclass(frozen=True)
class AppRecord:
    offset: int
    next_offset: int
    first_key_offset: int
    name_length: int
    name_capacity: int
    name_offset: int
    name_allocation: bytes
    keys: tuple[KeyRecord, ...]


@dataclass(frozen=True)
class ParsedIni:
    path: pathlib.Path
    data: bytes
    file_size: int
    free_payload_total: int
    free_list_head: int
    apps: tuple[AppRecord, ...]
    free_descriptors: tuple[FreeDescriptor, ...]
    slack_segments: tuple[Segment, ...]
    all_segments: tuple[Segment, ...]


def fail(message: str) -> NoReturn:
    raise ParseError(message)


def u16(data: bytes, offset: int) -> int:
    if offset + 2 > len(data):
        fail(f"16-bit field at 0x{offset:x} is outside the file")
    return struct.unpack_from("<H", data, offset)[0]


def u32(data: bytes, offset: int) -> int:
    if offset + 4 > len(data):
        fail(f"32-bit field at 0x{offset:x} is outside the file")
    return struct.unpack_from("<I", data, offset)[0]


def require_range(data: bytes, offset: int, length: int, label: str) -> bytes:
    if length < 0:
        fail(f"{label} has a negative length")
    if offset < 0 or offset + length > len(data):
        fail(
            f"{label} span 0x{offset:x}..0x{offset + length:x} is outside "
            f"the {len(data)} byte file"
        )
    return data[offset : offset + length]


def parse_ini(path: pathlib.Path) -> ParsedIni:
    data = path.read_bytes()
    size = len(data)
    if size < 40:
        fail("file is too small for an OS/2 profile header and first app record")
    if data[0:4] != b"\xff\xff\xff\xff":
        fail("missing OS/2 profile magic ffffffff at offset 0")

    header_size = u32(data, 4)
    if header_size != 0x14:
        fail(f"unsupported profile header size 0x{header_size:x}; expected 0x14")

    stored_size = u32(data, 8)
    if stored_size != size:
        fail(f"stored file size {stored_size} does not match actual size {size}")

    free_payload_total = u32(data, 12)
    free_list_head = u32(data, 16)

    segments: list[Segment] = [Segment(0, 20, "file header")]
    free_descriptors: list[FreeDescriptor] = []
    if free_list_head == 0:
        if free_payload_total != 0:
            fail("free payload total is nonzero but free-list head is zero")
    else:
        total = 0
        seen_free: set[int] = set()
        free_offset = free_list_head
        while free_offset != 0:
            if free_offset in seen_free:
                fail(f"free-list cycle at descriptor 0x{free_offset:x}")
            seen_free.add(free_offset)
            require_range(data, free_offset, 12, "free descriptor")
            next_free = u32(data, free_offset)
            payload_offset = u32(data, free_offset + 4)
            payload_length = u32(data, free_offset + 8)
            if payload_length:
                require_range(data, payload_offset, payload_length, "free payload")
            total += payload_length
            free_descriptors.append(
                FreeDescriptor(free_offset, next_free, payload_offset, payload_length)
            )
            segments.append(Segment(free_offset, free_offset + 12, "free descriptor"))
            if payload_length:
                segments.append(
                    Segment(
                        payload_offset,
                        payload_offset + payload_length,
                        "free payload",
                    )
                )
            free_offset = next_free
        if total != free_payload_total:
            fail(
                f"free payload total {free_payload_total} does not match "
                f"free-list sum {total}"
            )

    apps: list[AppRecord] = []
    seen_apps: set[int] = set()
    app_offset = 0x14
    while app_offset != 0:
        if app_offset in seen_apps:
            fail(f"application record cycle at 0x{app_offset:x}")
        seen_apps.add(app_offset)
        require_range(data, app_offset, 20, "application record")
        next_app = u32(data, app_offset)
        first_key = u32(data, app_offset + 4)
        reserved = u32(data, app_offset + 8)
        if reserved != 0:
            fail(
                f"application record 0x{app_offset:x} reserved field is "
                f"0x{reserved:x}, expected 0"
            )
        name_length = u16(data, app_offset + 12)
        name_capacity = u16(data, app_offset + 14)
        name_offset = u32(data, app_offset + 16)
        if not (1 <= name_length <= name_capacity):
            fail(
                f"application record 0x{app_offset:x} has invalid name "
                f"length/capacity {name_length}/{name_capacity}"
            )
        name_allocation = require_range(
            data, name_offset, name_capacity, "application name allocation"
        )
        if name_allocation[name_length - 1] != 0:
            fail(f"application name at 0x{name_offset:x} is not NUL terminated")
        segments.append(Segment(app_offset, app_offset + 20, "application record"))
        segments.append(
            Segment(name_offset, name_offset + name_capacity, "application name")
        )

        keys: list[KeyRecord] = []
        seen_keys: set[int] = set()
        key_offset = first_key
        while key_offset != 0:
            if key_offset in seen_keys:
                fail(f"key record cycle at 0x{key_offset:x}")
            seen_keys.add(key_offset)
            require_range(data, key_offset, 24, "key record")
            next_key = u32(data, key_offset)
            key_reserved = u32(data, key_offset + 4)
            if key_reserved != 0:
                fail(
                    f"key record 0x{key_offset:x} reserved field is "
                    f"0x{key_reserved:x}, expected 0"
                )
            key_name_length = u16(data, key_offset + 8)
            key_name_capacity = u16(data, key_offset + 10)
            key_name_offset = u32(data, key_offset + 12)
            data_capacity = u16(data, key_offset + 16)
            data_length = u16(data, key_offset + 18)
            data_offset = u32(data, key_offset + 20)
            if not (1 <= key_name_length <= key_name_capacity):
                fail(
                    f"key record 0x{key_offset:x} has invalid name "
                    f"length/capacity {key_name_length}/{key_name_capacity}"
                )
            key_name_allocation = require_range(
                data, key_name_offset, key_name_capacity, "key name allocation"
            )
            if key_name_allocation[key_name_length - 1] != 0:
                fail(f"key name at 0x{key_name_offset:x} is not NUL terminated")
            if data_length > data_capacity:
                fail(
                    f"key record 0x{key_offset:x} has data length/capacity "
                    f"{data_length}/{data_capacity}"
                )
            if data_capacity:
                data_allocation = require_range(
                    data, data_offset, data_capacity, "key data allocation"
                )
                segments.append(
                    Segment(data_offset, data_offset + data_capacity, "key data")
                )
            else:
                data_allocation = b""
            segments.append(Segment(key_offset, key_offset + 24, "key record"))
            segments.append(
                Segment(
                    key_name_offset,
                    key_name_offset + key_name_capacity,
                    "key name",
                )
            )
            keys.append(
                KeyRecord(
                    key_offset,
                    next_key,
                    key_name_length,
                    key_name_capacity,
                    key_name_offset,
                    data_capacity,
                    data_length,
                    data_offset,
                    key_name_allocation,
                    data_allocation,
                )
            )
            key_offset = next_key

        apps.append(
            AppRecord(
                app_offset,
                next_app,
                first_key,
                name_length,
                name_capacity,
                name_offset,
                name_allocation,
                tuple(keys),
            )
        )
        app_offset = next_app

    labels: list[list[str]] = [[] for _ in range(size)]
    for segment in segments:
        for index in range(segment.start, segment.end):
            labels[index].append(segment.kind)

    overlaps: list[tuple[int, int, tuple[str, ...]]] = []
    slack: list[Segment] = []
    index = 0
    while index < size:
        if not labels[index]:
            start = index
            while index < size and not labels[index]:
                labels[index].append("allocator slack")
                index += 1
            slack.append(Segment(start, index, "allocator slack"))
        elif len(labels[index]) > 1:
            start = index
            overlap_key = tuple(labels[index])
            while index < size and tuple(labels[index]) == overlap_key:
                index += 1
            overlaps.append((start, index, overlap_key))
        else:
            index += 1

    if overlaps:
        start, end, overlap_key = overlaps[0]
        fail(
            f"overlapping allocations at 0x{start:x}..0x{end:x}: "
            + ", ".join(overlap_key)
        )

    all_segments = tuple(segments + slack)
    return ParsedIni(
        path=path,
        data=data,
        file_size=size,
        free_payload_total=free_payload_total,
        free_list_head=free_list_head,
        apps=tuple(apps),
        free_descriptors=tuple(free_descriptors),
        slack_segments=tuple(slack),
        all_segments=all_segments,
    )


def logical_name(allocation: bytes, length: int) -> bytes:
    return allocation[: length - 1]


def escape_byte_string(data: bytes) -> str:
    out: list[str] = []
    for byte in data:
        if byte == 0x5C:
            out.append("\\\\")
        elif byte == 0x22:
            out.append('\\"')
        elif byte == 0x0A:
            out.append("\\n")
        elif byte == 0x0D:
            out.append("\\r")
        elif byte == 0x09:
            out.append("\\t")
        elif 0x20 <= byte <= 0x7E:
            out.append(chr(byte))
        else:
            out.append(f"\\x{byte:02x}")
    return "".join(out)


def decode_printable_text(data: bytes) -> str | None:
    try:
        text = data.decode("cp850")
    except UnicodeDecodeError:
        return None
    for char in text:
        if char in "\r\n\t":
            continue
        if ord(char) < 0x20 or ord(char) == 0x7F:
            return None
    return text


def display_name(data: bytes) -> str:
    text = decode_printable_text(data)
    if text is None:
        return 'b"' + escape_byte_string(data) + '"'
    return text.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")


def hexview(data: bytes, indent: str = "") -> str:
    lines = []
    for offset in range(0, len(data), 16):
        chunk = data[offset : offset + 16]
        hex_left = " ".join(f"{byte:02x}" for byte in chunk[:8])
        hex_right = " ".join(f"{byte:02x}" for byte in chunk[8:])
        hex_bytes = f"{hex_left:<23}  {hex_right:<23}"
        chars = []
        for byte in chunk:
            char = bytes([byte]).decode("cp850", errors="replace")
            if char in "\r\n\t" or ord(char) < 0x20 or ord(char) == 0x7F:
                chars.append(".")
            else:
                chars.append(char)
        lines.append(f"{indent}{offset:08x}  {hex_bytes}  |{''.join(chars)}|")
    return "\n".join(lines)


def render_value(data: bytes) -> str:
    text_data = data[:-1] if data.endswith(b"\x00") else data
    text = decode_printable_text(text_data)
    if text is None:
        return "hexview:\n" + hexview(data, "  ")
    if "\n" in text or "\r" in text:
        return '"""\n' + text.replace('"""', '\\"\\"\\"') + '\n"""'
    return text


def write_bytes(out: BinaryIO, indent: str, label: str, data: bytes) -> None:
    escaped = escape_byte_string(data)
    prefix = f"{indent}{label} ({len(data)} bytes)"
    if len(escaped) <= 140:
        out.write(f'{prefix} = b"{escaped}"\n'.encode("ascii"))
        return
    out.write(f"{prefix} =\n".encode("ascii"))
    for start in range(0, len(data), 48):
        chunk = escape_byte_string(data[start : start + 48])
        out.write(f'{indent}  b"{chunk}"\n'.encode("ascii"))


def coverage_summary(parsed: ParsedIni) -> dict[str, int]:
    totals: dict[str, int] = {}
    for segment in parsed.all_segments:
        totals[segment.kind] = totals.get(segment.kind, 0) + segment.end - segment.start
    return totals


def write_dump(parsed: ParsedIni, output_path: pathlib.Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(
        prefix=f".{output_path.name}.", suffix=".tmp", dir=str(output_path.parent)
    )
    try:
        with os.fdopen(fd, "wb") as out:
            for app in parsed.apps:
                app_name = logical_name(app.name_allocation, app.name_length)
                out.write(f"[{display_name(app_name)}]\n".encode("utf-8"))
                for key in app.keys:
                    key_name = logical_name(key.name_allocation, key.name_length)
                    used_data = key.data_allocation[: key.data_length]
                    out.write(
                        f"{display_name(key_name)} = {render_value(used_data)}\n".encode(
                            "utf-8"
                        )
                    )
                out.write(b"\n")

        os.chmod(temp_name, 0o664)
        os.replace(temp_name, output_path)
        os.chmod(output_path, 0o664)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def convert(input_path: pathlib.Path, output_path: pathlib.Path) -> None:
    parsed = parse_ini(input_path)
    write_dump(parsed, output_path)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Convert an OS/2 binary INI/profile file into a text dump."
    )
    parser.add_argument("inputFile", type=pathlib.Path)
    parser.add_argument("outputFile", type=pathlib.Path)
    args = parser.parse_args(argv)

    try:
        convert(args.inputFile, args.outputFile)
    except Exception as exc:
        try:
            args.outputFile.unlink()
        except FileNotFoundError:
            pass
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

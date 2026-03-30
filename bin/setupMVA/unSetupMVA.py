#!/usr/bin/env python3
# Vibe coded by Codex
"""Extract SetupMVA / Setup Program Archive files."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib
from dataclasses import dataclass
from pathlib import Path


ARCHIVE_MAGIC = b"mflh"
ENTRY_MAGIC = b"mfen"
ARCHIVE_VERSION = 1
ENTRY_VERSION = 1
MIN_ENTRY_HEADER_SIZE = 0x132
LH5_METHOD = "-lh5-"


class SetupMVAError(RuntimeError):
    """Raised when the archive is malformed or uses an unsupported variant."""


@dataclass(frozen=True)
class Entry:
    index: int
    offset: int
    version: int
    header_size: int
    source_mtime: int
    packed_time: int
    source_path: str
    unpacked_size: int
    packed_size: int
    unknown_11c: int
    unknown_120: int
    method: int
    reserved_128: int
    tag_attr: int
    tag: int
    attributes: int
    extra_flag: int
    description: str
    payload_offset: int
    payload_truncated: bool
    payload: bytes


def read_u16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def read_i16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<h", data, offset)[0]


def read_u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def decode_c_string(raw: bytes) -> str:
    return raw.split(b"\x00", 1)[0].decode("latin-1")


def parse_archive(data: bytes) -> list[Entry]:
    if len(data) < 8:
        raise SetupMVAError("file is too small to be a SetupMVA archive")
    if data[:4] != ARCHIVE_MAGIC:
        raise SetupMVAError("missing mflh archive magic")
    archive_version = read_u32(data, 4)
    if archive_version != ARCHIVE_VERSION:
        raise SetupMVAError(
            f"unsupported archive version {archive_version}, expected {ARCHIVE_VERSION}"
        )

    entries: list[Entry] = []
    offset = 8
    entry_index = 0
    while offset < len(data):
        if offset + 8 > len(data):
            raise SetupMVAError(f"truncated entry header at 0x{offset:x}")
        if data[offset : offset + 4] != ENTRY_MAGIC:
            raise SetupMVAError(f"missing mfen entry magic at 0x{offset:x}")

        version = read_u16(data, offset + 4)
        if version != ENTRY_VERSION:
            raise SetupMVAError(
                f"unsupported entry version {version} at 0x{offset:x}, "
                f"expected {ENTRY_VERSION}"
            )
        header_size = read_u16(data, offset + 6)
        if header_size < MIN_ENTRY_HEADER_SIZE:
            raise SetupMVAError(
                f"entry header at 0x{offset:x} is too small: 0x{header_size:x}"
            )
        header_end = offset + header_size
        if header_end > len(data):
            raise SetupMVAError(f"entry header at 0x{offset:x} runs past EOF")

        source_mtime = read_u32(data, offset + 0x08)
        packed_time = read_u32(data, offset + 0x0C)
        source_path = decode_c_string(data[offset + 0x10 : offset + 0x11C])
        unpacked_size = read_u32(data, offset + 0x114)
        packed_size = read_u32(data, offset + 0x118)
        unknown_11c = read_u32(data, offset + 0x11C)
        unknown_120 = read_u32(data, offset + 0x120)
        method = read_u32(data, offset + 0x124)
        reserved_128 = read_u32(data, offset + 0x128)
        tag_attr = read_u32(data, offset + 0x12C)
        tag = read_i16(data, offset + 0x12C)
        attributes = read_u16(data, offset + 0x12E)
        extra_flag = read_u16(data, offset + 0x130)
        description = decode_c_string(data[offset + 0x132 : header_end])

        payload_offset = header_end
        payload_end = payload_offset + packed_size
        payload_truncated = False
        if payload_end > len(data):
            if extra_flag != 1:
                raise SetupMVAError(
                    f"entry payload at 0x{offset:x} overruns EOF "
                    f"(need 0x{payload_end:x}, have 0x{len(data):x})"
                )
            payload_end = len(data)
            payload_truncated = True
        payload = data[payload_offset:payload_end]

        entries.append(
            Entry(
                index=entry_index,
                offset=offset,
                version=version,
                header_size=header_size,
                source_mtime=source_mtime,
                packed_time=packed_time,
                source_path=source_path,
                unpacked_size=unpacked_size,
                packed_size=packed_size,
                unknown_11c=unknown_11c,
                unknown_120=unknown_120,
                method=method,
                reserved_128=reserved_128,
                tag_attr=tag_attr,
                tag=tag,
                attributes=attributes,
                extra_flag=extra_flag,
                description=description,
                payload_offset=payload_offset,
                payload_truncated=payload_truncated,
                payload=payload,
            )
        )
        entry_index += 1
        offset = payload_end

    if offset != len(data):
        raise SetupMVAError(
            f"parser stopped at 0x{offset:x}, but file ends at 0x{len(data):x}"
        )
    return entries


def decompress_zlib(payload: bytes, expected_size: int, entry: Entry) -> bytes:
    decomp = zlib.decompressobj()
    output = decomp.decompress(payload)
    output += decomp.flush()
    if not decomp.eof and not entry.payload_truncated:
        raise SetupMVAError(f"entry {entry.index} ended before the zlib stream finished")
    if decomp.unused_data:
        raise SetupMVAError(f"entry {entry.index} has trailing bytes after the zlib stream")
    if len(output) != expected_size and not entry.payload_truncated:
        raise SetupMVAError(
            f"entry {entry.index} zlib output size mismatch: "
            f"expected {expected_size}, got {len(output)}"
        )
    if entry.payload_truncated and not output:
        raise SetupMVAError(f"entry {entry.index} is truncated and yielded no recoverable output")
    return output


def crc16_arc(data: bytes) -> int:
    crc = 0
    for value in data:
        crc ^= value
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc & 0xFFFF


def build_lha_level0_archive(method: str, payload: bytes, unpacked_size: int, crc16: int) -> bytes:
    name = b"payload.bin"
    header = bytearray(b"\x00\x00")
    header.extend(method.encode("ascii"))
    header.extend(struct.pack("<I", len(payload)))
    header.extend(struct.pack("<I", unpacked_size))
    header.extend(struct.pack("<I", 0))
    header.append(0x20)
    header.append(0x00)
    header.append(len(name))
    header.extend(name)
    header.extend(struct.pack("<H", crc16))
    header[0] = len(header) - 2
    header[1] = sum(header[2:]) & 0xFF
    return bytes(header) + payload + b"\x00"


def run_lha_payload(archive_bytes: bytes) -> tuple[bytes, str]:
    lha = shutil.which("lha")
    if not lha:
        raise SetupMVAError("method 3 requires the external 'lha' command in PATH")

    with tempfile.TemporaryDirectory(prefix="setupmva_lh5_") as temp_dir:
        archive_path = Path(temp_dir) / "payload.lzh"
        archive_path.write_bytes(archive_bytes)
        result = subprocess.run(
            [lha, "p", "-q", str(archive_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    stderr_text = result.stderr.decode("latin-1", errors="replace").strip()
    return result.stdout, stderr_text


def decompress_lh5(payload: bytes, expected_size: int, entry: Entry) -> bytes:
    output, stderr_text = run_lha_payload(
        build_lha_level0_archive(LH5_METHOD, payload, expected_size, 0)
    )
    if len(output) != expected_size:
        raise SetupMVAError(
            f"entry {entry.index} lh5 output size mismatch: "
            f"expected {expected_size}, got {len(output)}"
        )

    crc = crc16_arc(output)
    verified_output, verified_stderr = run_lha_payload(
        build_lha_level0_archive(LH5_METHOD, payload, expected_size, crc)
    )
    if verified_output != output:
        raise SetupMVAError(f"entry {entry.index} lh5 verification pass changed the output")
    if verified_stderr:
        raise SetupMVAError(
            f"entry {entry.index} lh5 verification failed: {verified_stderr}"
        )

    if stderr_text and "CRC error" not in stderr_text:
        raise SetupMVAError(f"entry {entry.index} lh5 decode failed: {stderr_text}")
    return output


def decode_entry(entry: Entry) -> bytes:
    if entry.method == 2:
        if entry.payload_truncated:
            raise SetupMVAError(f"entry {entry.index} truncates an uncompressed payload")
        if entry.packed_size != entry.unpacked_size:
            raise SetupMVAError(
                f"entry {entry.index} method 2 claims packed size {entry.packed_size} "
                f"but unpacked size {entry.unpacked_size}"
            )
        return entry.payload
    if entry.method == 3:
        if entry.payload_truncated:
            raise SetupMVAError(f"entry {entry.index} truncates an lh5 payload")
        return decompress_lh5(entry.payload, entry.unpacked_size, entry)
    if entry.method == 4:
        return decompress_zlib(entry.payload, entry.unpacked_size, entry)
    raise SetupMVAError(f"entry {entry.index} uses unsupported method {entry.method}")


def sanitize_component(component: str) -> str:
    component = component.replace(":", "_")
    if component in {"", "."}:
        return "_"
    if component == "..":
        return "__parent__"
    return component


def normalize_source_path(source_path: str, index: int) -> tuple[str, ...]:
    normalized = source_path.replace("\\", "/")
    drive_match = re.match(r"^([A-Za-z]):/(.*)$", normalized)
    if drive_match:
        drive = drive_match.group(1).upper()
        remainder = drive_match.group(2)
        parts = [drive]
        if remainder:
            parts.extend(sanitize_component(part) for part in remainder.split("/") if part)
        return tuple(parts)
    if normalized.startswith("//"):
        remainder = normalized.lstrip("/")
        parts = ["_UNC"]
        if remainder:
            parts.extend(sanitize_component(part) for part in remainder.split("/") if part)
        return tuple(parts)
    if normalized:
        return tuple(["_ROOT"] + [sanitize_component(part) for part in normalized.split("/") if part])
    return ("_UNNAMED", f"entry_{index:04d}.bin")


def uniquify_path(candidate: Path, seen: set[Path]) -> Path:
    unique = candidate
    counter = 1
    while unique in seen:
        suffix = "".join(candidate.suffixes)
        stem = candidate.name[: -len(suffix)] if suffix else candidate.name
        unique = candidate.with_name(f"{stem}__dup{counter}{suffix}")
        counter += 1
    seen.add(unique)
    return unique


def write_entry(output_root: Path, entry: Entry, decoded: bytes, seen_paths: set[Path]) -> Path:
    rel_parts = normalize_source_path(entry.source_path, entry.index)
    target = uniquify_path(output_root.joinpath(*rel_parts), seen_paths)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(decoded)
    if entry.source_mtime > 0:
        try:
            os.utime(target, (entry.source_mtime, entry.source_mtime))
        except OSError:
            pass
    return target


def extract_archive(input_path: Path, output_root: Path) -> tuple[int, int]:
    data = input_path.read_bytes()
    entries = parse_archive(data)
    seen_paths: set[Path] = set()
    partial_count = 0
    for entry in entries:
        decoded = decode_entry(entry)
        if len(decoded) != entry.unpacked_size and not entry.payload_truncated:
            raise SetupMVAError(
                f"entry {entry.index} decoded length mismatch: "
                f"expected {entry.unpacked_size}, got {len(decoded)}"
            )
        if entry.payload_truncated:
            partial_count += 1
        write_entry(output_root, entry, decoded, seen_paths)
    return len(entries), partial_count


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract Setup Program Archive (SetupMVA) files."
    )
    parser.add_argument("inputFile", type=Path, help="input SetupMVA archive")
    parser.add_argument("outputDir", type=Path, help="directory to extract into")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    try:
        args.outputDir.mkdir(parents=True, exist_ok=True)
        count, partial_count = extract_archive(args.inputFile, args.outputDir)
    except SetupMVAError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if partial_count:
        print(
            f"Extracted {count} file(s) from {args.inputFile} into {args.outputDir} "
            f"({partial_count} partial/spanned member(s))"
        )
    else:
        print(f"Extracted {count} file(s) from {args.inputFile} into {args.outputDir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

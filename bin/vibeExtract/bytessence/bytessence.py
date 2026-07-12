#!/usr/bin/env python3
# Vibe coded by Codex
"""Strict extractor for Bytessence InstallMaker 5.x installer executables."""

from __future__ import annotations

import argparse
import binascii
import datetime as dt
import hashlib
import json
import lzma
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import struct
import sys
import tempfile
import time
import zlib


CONFIG_START = b"$_BIM_CONFIG_START_$"
CONFIG_END = b"$_BIM_CONFIG_END_$"
INTERNAL_RE = re.compile(r"^_\$_INSTALLER_Data_([0-9]+)_\$_\\(.+)$")


class FormatError(Exception):
    """The input is not a supported, structurally valid installer."""


def fail(message: str) -> "None":
    raise FormatError(message)


def need(data: bytes, offset: int, size: int, what: str) -> None:
    if offset < 0 or size < 0 or offset + size > len(data):
        fail(f"truncated {what}")


def unpack_from(fmt: str, data: bytes, offset: int, what: str):
    size = struct.calcsize(fmt)
    need(data, offset, size, what)
    return struct.unpack_from(fmt, data, offset)


def pe_extent(data: bytes, base: int, limit: int, what: str) -> tuple[int, dict]:
    need(data, base, 0x40, f"{what} DOS header")
    if data[base : base + 2] != b"MZ":
        fail(f"missing MZ signature in {what}")
    pe_rel = unpack_from("<I", data, base + 0x3C, f"{what} e_lfanew")[0]
    pe = base + pe_rel
    need(data, pe, 24, f"{what} PE header")
    if data[pe : pe + 4] != b"PE\0\0":
        fail(f"missing PE signature in {what}")
    machine, section_count, timestamp, _, _, optional_size, characteristics = unpack_from(
        "<HHIIIHH", data, pe + 4, f"{what} COFF header"
    )
    if machine != 0x014C or not (1 <= section_count <= 96):
        fail(f"unsupported {what} PE machine or section count")
    optional = pe + 24
    need(data, optional, optional_size, f"{what} optional header")
    if optional_size < 64 or unpack_from("<H", data, optional, f"{what} optional magic")[0] != 0x10B:
        fail(f"{what} is not PE32")
    header_size = unpack_from("<I", data, optional + 60, f"{what} SizeOfHeaders")[0]
    if not (0 < header_size <= limit - base):
        fail(f"invalid {what} SizeOfHeaders")
    extent = header_size
    sections = []
    table = optional + optional_size
    need(data, table, section_count * 40, f"{what} section table")
    for index in range(section_count):
        pos = table + index * 40
        raw_name = data[pos : pos + 8]
        name = raw_name.split(b"\0", 1)[0].decode("ascii", "replace")
        virtual_size, virtual_address, raw_size, raw_offset = unpack_from(
            "<IIII", data, pos + 8, f"{what} section {index}"
        )
        if raw_size:
            # Packed PE images may deliberately overlap raw sections with the
            # area described by SizeOfHeaders; only the bounded extent matters.
            if raw_offset + raw_size > limit - base:
                fail(f"invalid raw range for {what} section {index}")
            extent = max(extent, raw_offset + raw_size)
        sections.append(
            {
                "name": name,
                "virtual_size": virtual_size,
                "virtual_address": virtual_address,
                "raw_size": raw_size,
                "raw_offset": raw_offset,
            }
        )
    return extent, {
        "machine": machine,
        "section_count": section_count,
        "timestamp": timestamp,
        "characteristics": characteristics,
        "header_size": header_size,
        "sections": sections,
    }


def parse_container(data: bytes) -> dict:
    outer_size, pe = pe_extent(data, 0, len(data), "installer")
    if data[outer_size : outer_size + len(CONFIG_START)] != CONFIG_START:
        fail("the PE overlay does not begin with the Bytessence configuration marker")
    header = outer_size + len(CONFIG_START)
    candidates = []

    # Format 1 has three DWORDs; format 2 adds the embedded-module CRC32.
    if header + 12 <= len(data):
        elevation, module_size, reserved = struct.unpack_from("<III", data, header)
        module_offset = header + 12
        if reserved == 0 and module_size and module_offset + module_size <= len(data):
            try:
                extent, module_pe = pe_extent(data, module_offset, module_offset + module_size, "embedded module")
                if extent == module_size:
                    candidates.append((1, elevation, None, module_size, module_offset, module_pe))
            except FormatError:
                pass
    if header + 16 <= len(data):
        elevation, module_crc, module_size, reserved = struct.unpack_from("<IIII", data, header)
        module_offset = header + 16
        if reserved == 0 and module_size and module_offset + module_size <= len(data):
            try:
                extent, module_pe = pe_extent(data, module_offset, module_offset + module_size, "embedded module")
                actual_crc = binascii.crc32(data[module_offset : module_offset + module_size]) & 0xFFFFFFFF
                if extent == module_size and actual_crc == module_crc:
                    candidates.append((2, elevation, module_crc, module_size, module_offset, module_pe))
            except FormatError:
                pass
    if len(candidates) != 1:
        fail("invalid or ambiguous Bytessence configuration header")
    variant, elevation, module_crc, module_size, module_offset, module_pe = candidates[0]
    if elevation not in (0, 1):
        fail("invalid elevation flag")
    end_marker = module_offset + module_size
    if data[end_marker : end_marker + len(CONFIG_END)] != CONFIG_END:
        fail("missing Bytessence configuration end marker")
    archive_offset = end_marker + len(CONFIG_END)
    if archive_offset >= len(data):
        fail("missing installer archive")
    module = data[module_offset:end_marker]
    if data[archive_offset : archive_offset + 5] == b"BLZMA":
        archive_type = "BLZMA"
        if b"BLPUnpack32.dll" not in module:
            fail("BLZMA overlay does not use the expected embedded module")
    elif data[archive_offset : archive_offset + 4] == b"PK\x03\x04":
        archive_type = "ZIP"
        if b"ZIPUnpack32.dll" not in module:
            fail("ZIP overlay does not use the expected embedded module")
    else:
        fail("unknown Bytessence archive signature")
    return {
        "outer_pe_size": outer_size,
        "outer_pe": pe,
        "config_variant": variant,
        "requires_elevation": bool(elevation),
        "module_crc32": module_crc,
        "module_size": module_size,
        "module_offset": module_offset,
        "module_pe": module_pe,
        "archive_offset": archive_offset,
        "archive_type": archive_type,
    }


def safe_parts(name: str) -> tuple[str, ...]:
    if not name or "\0" in name:
        fail("empty filename or embedded NUL in archive entry")
    normalized = name.replace("\\", "/")
    if normalized.startswith("/") or re.match(r"^[A-Za-z]:", normalized):
        fail(f"absolute archive path is forbidden: {name!r}")
    parts = PurePosixPath(normalized).parts
    if not parts or any(part in ("", ".", "..") for part in parts):
        fail(f"unsafe archive path: {name!r}")
    return tuple(parts)


def write_spool(root: Path, archive_name: str, content: bytes, mtime: int | None) -> Path:
    parts = safe_parts(archive_name)
    target = root.joinpath(*parts)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        fail(f"duplicate archive path: {archive_name!r}")
    target.write_bytes(content)
    if mtime is not None:
        os.utime(target, (mtime, mtime))
    return target


def decode_lzma_properties(properties: bytes) -> dict:
    if len(properties) != 5:
        fail("invalid LZMA properties length")
    packed = properties[0]
    if packed >= 225:
        fail("invalid LZMA lc/lp/pb properties")
    lc = packed % 9
    remainder = packed // 9
    lp = remainder % 5
    pb = remainder // 5
    dictionary = int.from_bytes(properties[1:5], "little")
    if lc + lp > 4 or dictionary == 0:
        fail("unsupported LZMA properties")
    return {
        "id": lzma.FILTER_LZMA1,
        "dict_size": dictionary,
        "lc": lc,
        "lp": lp,
        "pb": pb,
    }


def decompress_raw_lzma(payload: bytes, expected_size: int, filt: dict) -> tuple[bytes, int]:
    try:
        decoder = lzma.LZMADecompressor(format=lzma.FORMAT_RAW, filters=[filt])
        # BIM's encoder can leave range-coder padding that decodes to one or
        # two zero bytes past the logical block size. The DLL obeys the size
        # field, so validate the padding and return only the logical bytes.
        output = decoder.decompress(payload, max_length=expected_size + 4096)
    except lzma.LZMAError as exc:
        fail(f"invalid raw LZMA block: {exc}")
    if (
        len(output) < expected_size
        or decoder.unused_data
        or not decoder.needs_input
        or any(output[expected_size:])
    ):
        fail("raw LZMA block length mismatch")
    return output[:expected_size], len(output) - expected_size


def parse_blzma(data: bytes, offset: int, spool: Path) -> tuple[list[dict], dict]:
    pos = offset
    need(data, pos, 42, "BLZMA header")
    if data[pos : pos + 5] != b"BLZMA":
        fail("missing BLZMA signature")
    pos += 5
    version, timestamp = unpack_from("<II", data, pos, "BLZMA version/timestamp")
    pos += 8
    if version not in (1, 2):
        fail(f"unsupported BLZMA version {version}")
    entry_count, total_compressed, total_uncompressed = unpack_from(
        "<QQQ", data, pos, "BLZMA aggregate fields"
    )
    pos += 24
    properties = data[pos : pos + 5]
    pos += 5
    filt = decode_lzma_properties(properties)
    entries = []
    compressed_sum = 0
    uncompressed_sum = 0
    seen = set()
    for index in range(entry_count):
        name_length = unpack_from("<I", data, pos, f"entry {index} name length")[0]
        pos += 4
        if name_length == 0 or name_length > 1024 * 1024:
            fail(f"invalid entry {index} name length")
        need(data, pos, name_length, f"entry {index} name")
        raw_name = data[pos : pos + name_length]
        pos += name_length
        if raw_name.endswith(b"\0"):
            raw_name = raw_name[:-1]
        if not raw_name or b"\0" in raw_name:
            fail(f"invalid entry {index} filename bytes")
        try:
            name = raw_name.decode("cp1252")
        except UnicodeDecodeError:
            fail(f"entry {index} filename is not Windows-1252")
        safe_parts(name)
        key = name.replace("/", "\\").casefold()
        if key in seen:
            fail(f"duplicate case-insensitive entry name: {name!r}")
        seen.add(key)
        mtime, attributes = unpack_from("<II", data, pos, f"entry {index} metadata")
        pos += 8
        compressed_size, uncompressed_size = unpack_from("<QQ", data, pos, f"entry {index} sizes")
        pos += 16
        crc32 = unpack_from("<I", data, pos, f"entry {index} CRC32")[0]
        pos += 4
        if version == 1:
            encrypted = unpack_from("<I", data, pos, f"entry {index} encryption flag")[0]
            pos += 4
        else:
            need(data, pos, 1, f"entry {index} encryption flag")
            encrypted = data[pos]
            pos += 1
        if encrypted != 0:
            fail("encrypted BLZMA entries are not supported")
        chunks = []
        padding_output = 0
        consumed_compressed = 0
        consumed_uncompressed = 0
        crc = 0
        while consumed_compressed < compressed_size or consumed_uncompressed < uncompressed_size:
            block_compressed, block_uncompressed = unpack_from(
                "<II", data, pos, f"entry {index} block header"
            )
            pos += 8
            if block_compressed == 0 or block_uncompressed == 0:
                fail(f"invalid zero-sized block in entry {index}")
            if (
                consumed_compressed + block_compressed > compressed_size
                or consumed_uncompressed + block_uncompressed > uncompressed_size
            ):
                fail(f"block totals exceed entry {index} totals")
            need(data, pos, block_compressed, f"entry {index} compressed block")
            payload = data[pos : pos + block_compressed]
            pos += block_compressed
            output, block_padding = decompress_raw_lzma(payload, block_uncompressed, filt)
            chunks.append(output)
            padding_output += block_padding
            crc = binascii.crc32(output, crc)
            consumed_compressed += block_compressed
            consumed_uncompressed += block_uncompressed
        if (consumed_compressed, consumed_uncompressed) != (compressed_size, uncompressed_size):
            fail(f"entry {index} block totals do not match its header")
        if (crc & 0xFFFFFFFF) != crc32:
            fail(f"entry {index} CRC32 mismatch")
        content = b"".join(chunks)
        write_spool(spool, name, content, mtime)
        entries.append(
            {
                "name": name,
                "mtime": mtime,
                "attributes": attributes,
                "compressed_size": compressed_size,
                "uncompressed_size": uncompressed_size,
                "crc32": f"{crc32:08x}",
                "encrypted": False,
                "block_count": len(chunks),
                "lzma_zero_padding_output": padding_output,
            }
        )
        compressed_sum += compressed_size
        uncompressed_sum += uncompressed_size
    if compressed_sum != total_compressed or uncompressed_sum != total_uncompressed:
        fail("BLZMA aggregate size fields do not match the entries")
    if pos != len(data):
        fail("unaccounted bytes after the BLZMA archive")
    return entries, {
        "version": version,
        "timestamp": timestamp,
        "entry_count": entry_count,
        "total_compressed": total_compressed,
        "total_uncompressed": total_uncompressed,
        "lzma_properties": properties.hex(),
        "end_offset": pos,
    }


def dos_timestamp(date_value: int, time_value: int) -> int:
    year = 1980 + ((date_value >> 9) & 0x7F)
    month = (date_value >> 5) & 0x0F
    day = date_value & 0x1F
    hour = (time_value >> 11) & 0x1F
    minute = (time_value >> 5) & 0x3F
    second = (time_value & 0x1F) * 2
    try:
        value = dt.datetime(year, month, day, hour, minute, second)
    except ValueError:
        fail("invalid DOS date/time in ZIP entry")
    return int(time.mktime(value.timetuple()))


def decode_zip_name(raw: bytes, flags: int) -> str:
    # InstallMaker's bundled Windows minizip writer stores non-UTF-8 names in
    # the process ANSI code page, even though generic ZIP defaults to CP437.
    encoding = "utf-8" if flags & 0x0800 else "cp1252"
    try:
        return raw.decode(encoding)
    except UnicodeDecodeError:
        fail(f"invalid {encoding} ZIP filename")


def inflate_zip(method: int, payload: bytes, expected_size: int) -> bytes:
    if method == 0:
        output = payload
    elif method == 8:
        try:
            decoder = zlib.decompressobj(-15)
            output = decoder.decompress(payload) + decoder.flush()
        except zlib.error as exc:
            fail(f"invalid ZIP deflate stream: {exc}")
        if not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
            fail("ZIP deflate stream boundary mismatch")
    else:
        fail(f"unsupported ZIP compression method {method}")
    if len(output) != expected_size:
        fail("ZIP uncompressed length mismatch")
    return output


def parse_zip(data: bytes, offset: int, spool: Path) -> tuple[list[dict], dict]:
    pos = offset
    local = []
    seen = set()
    while True:
        need(data, pos, 4, "ZIP record signature")
        signature = struct.unpack_from("<I", data, pos)[0]
        if signature == 0x02014B50:
            break
        if signature != 0x04034B50:
            fail("unexpected record before ZIP central directory")
        fields = unpack_from("<I5H3I2H", data, pos, "ZIP local header")
        (
            _, needed, flags, method, mod_time, mod_date, crc32,
            compressed_size, uncompressed_size, name_length, extra_length,
        ) = fields
        if needed > 63 or flags & ~0x0800:
            fail("unsupported ZIP version or flags")
        pos += 30
        need(data, pos, name_length + extra_length, "ZIP local name/extra")
        raw_name = data[pos : pos + name_length]
        extra = data[pos + name_length : pos + name_length + extra_length]
        pos += name_length + extra_length
        name = decode_zip_name(raw_name, flags)
        safe_parts(name)
        key = name.replace("/", "\\").casefold()
        if key in seen:
            fail(f"duplicate case-insensitive ZIP entry: {name!r}")
        seen.add(key)
        need(data, pos, compressed_size, "ZIP compressed data")
        payload = data[pos : pos + compressed_size]
        pos += compressed_size
        output = inflate_zip(method, payload, uncompressed_size)
        if (binascii.crc32(output) & 0xFFFFFFFF) != crc32:
            fail(f"ZIP CRC32 mismatch for {name!r}")
        mtime = dos_timestamp(mod_date, mod_time)
        write_spool(spool, name, output, mtime)
        local.append(
            {
                "name": name,
                "raw_name": raw_name,
                "needed": needed,
                "flags": flags,
                "method": method,
                "mod_time": mod_time,
                "mod_date": mod_date,
                "mtime": mtime,
                "crc32_int": crc32,
                "crc32": f"{crc32:08x}",
                "compressed_size": compressed_size,
                "uncompressed_size": uncompressed_size,
                "extra": extra,
                "header_offset": pos - compressed_size - extra_length - name_length - 30,
            }
        )
    central_offset = pos
    central = []
    while data[pos : pos + 4] == b"PK\x01\x02":
        fields = unpack_from("<I6H3I5H2I", data, pos, "ZIP central header")
        (
            _, made_by, needed, flags, method, mod_time, mod_date, crc32,
            compressed_size, uncompressed_size, name_length, extra_length,
            comment_length, disk, internal_attr, external_attr, local_offset,
        ) = fields
        pos += 46
        need(data, pos, name_length + extra_length + comment_length, "ZIP central variable fields")
        raw_name = data[pos : pos + name_length]
        extra = data[pos + name_length : pos + name_length + extra_length]
        comment = data[
            pos + name_length + extra_length : pos + name_length + extra_length + comment_length
        ]
        pos += name_length + extra_length + comment_length
        central.append(
            {
                "made_by": made_by,
                "needed": needed,
                "flags": flags,
                "method": method,
                "mod_time": mod_time,
                "mod_date": mod_date,
                "crc32": crc32,
                "compressed_size": compressed_size,
                "uncompressed_size": uncompressed_size,
                "raw_name": raw_name,
                "extra": extra,
                "comment": comment,
                "disk": disk,
                "internal_attr": internal_attr,
                "external_attr": external_attr,
                "local_offset": local_offset,
            }
        )
    central_end = pos
    eocd = unpack_from("<I4H2IH", data, pos, "ZIP end of central directory")
    if eocd[0] != 0x06054B50:
        fail("missing ZIP end-of-central-directory record")
    _, disk, central_disk, disk_entries, total_entries, central_size, recorded_offset, comment_length = eocd
    pos += 22
    need(data, pos, comment_length, "ZIP archive comment")
    archive_comment = data[pos : pos + comment_length]
    pos += comment_length
    if pos != len(data):
        fail("unaccounted bytes after ZIP end record")
    if disk or central_disk or disk_entries != total_entries or total_entries != len(local):
        fail("multi-disk ZIP or inconsistent ZIP entry counts")
    if len(central) != len(local) or central_size != central_end - central_offset:
        fail("inconsistent ZIP central-directory size/count")
    if recorded_offset not in (central_offset, central_offset - offset):
        fail("ZIP central-directory offset does not point to the central directory")
    for index, (left, right) in enumerate(zip(local, central)):
        comparable = (
            "raw_name", "needed", "flags", "method", "mod_time", "mod_date",
            "compressed_size", "uncompressed_size", "extra",
        )
        if any(left[field] != right[field] for field in comparable) or left["crc32_int"] != right["crc32"]:
            fail(f"ZIP local/central mismatch for entry {index}")
        if right["disk"] != 0 or right["local_offset"] not in (
            left["header_offset"], left["header_offset"] - offset
        ):
            fail(f"invalid ZIP local-header offset for entry {index}")
        left.update(
            {
                "made_by": right["made_by"],
                "internal_attributes": right["internal_attr"],
                "external_attributes": right["external_attr"],
                "central_comment_hex": right["comment"].hex(),
                "local_extra_hex": left.pop("extra").hex(),
            }
        )
        left.pop("raw_name")
        left.pop("crc32_int")
    return local, {
        "entry_count": len(local),
        "total_compressed": sum(item["compressed_size"] for item in local),
        "total_uncompressed": sum(item["uncompressed_size"] for item in local),
        "central_offset": central_offset,
        "central_size": central_size,
        "comment_hex": archive_comment.hex(),
        "end_offset": pos,
    }


def component_ids(script: bytes) -> set[str]:
    try:
        text = script.decode("cp1252")
    except UnicodeDecodeError:
        fail("Script.bim is not Windows-1252 text")
    section = None
    items = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1]
            continue
        if section == "Components" and line.startswith("Items") and "=" in line:
            if items is not None:
                fail("duplicate Components/Items setting")
            items = line.split("=", 1)[1].strip()
    if items is None:
        fail("Script.bim has no Components/Items setting")
    result = {value.strip() for value in items.split(",") if value.strip()}
    if not result or any(not value.isdecimal() for value in result):
        fail("invalid component ID list in Script.bim")
    return result


def classify_entries(entries: list[dict], spool: Path) -> tuple[str, set[str], list[dict]]:
    internal_prefixes = set()
    script_names = []
    for entry in entries:
        match = INTERNAL_RE.fullmatch(entry["name"].replace("/", "\\"))
        if match:
            internal_prefixes.add(match.group(1))
            if match.group(2).casefold() == "config\\script.bim":
                script_names.append(entry["name"])
    if len(internal_prefixes) != 1 or len(script_names) != 1:
        fail("archive does not contain one coherent internal installer namespace and Script.bim")
    script_name = script_names[0]
    script_path = spool.joinpath(*safe_parts(script_name))
    ids = component_ids(script_path.read_bytes())
    mapped = []
    output_seen = set()
    for entry in entries:
        archive_name = entry["name"].replace("/", "\\")
        internal = INTERNAL_RE.fullmatch(archive_name)
        if internal:
            entry["kind"] = "internal"
            entry["internal_path"] = internal.group(2)
            continue
        parts = archive_name.split("\\")
        if len(parts) < 2 or parts[0] not in ids:
            fail(f"payload entry is not assigned to a declared component: {entry['name']!r}")
        output_name = "\\".join(parts[1:])
        key = output_name.casefold()
        if key in output_seen:
            fail(f"multiple payload records map to {output_name!r}")
        output_seen.add(key)
        entry["kind"] = "payload"
        entry["component_id"] = parts[0]
        entry["output_name"] = output_name
        mapped.append(entry)
    if not mapped:
        fail("archive contains no installable payload files")
    return next(iter(internal_prefixes)), ids, mapped


def copy_validated(source: Path, destination: Path, mtime: int | None) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(destination.parent, 0o775)
    with tempfile.NamedTemporaryFile(prefix=".bytessence-", dir=destination.parent, delete=False) as handle:
        temporary = Path(handle.name)
        with source.open("rb") as incoming:
            shutil.copyfileobj(incoming, handle, 1024 * 1024)
    try:
        os.chmod(temporary, 0o664)
        if mtime is not None:
            os.utime(temporary, (mtime, mtime))
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)


def ensure_tree_modes(root: Path) -> None:
    for directory, directories, files in os.walk(root):
        os.chmod(directory, 0o775)
        for name in directories:
            os.chmod(Path(directory, name), 0o775)
        for name in files:
            os.chmod(Path(directory, name), 0o664)


def extract(input_path: Path, output_path: Path, include_all: bool) -> dict:
    try:
        data = input_path.read_bytes()
    except OSError as exc:
        fail(f"cannot read input: {exc}")
    container = parse_container(data)
    with tempfile.TemporaryDirectory(prefix="bytessence-") as temporary_name:
        temporary = Path(temporary_name)
        spool = temporary / "archive"
        spool.mkdir()
        if container["archive_type"] == "BLZMA":
            entries, archive = parse_blzma(data, container["archive_offset"], spool)
        else:
            entries, archive = parse_zip(data, container["archive_offset"], spool)
        internal_id, ids, payload = classify_entries(entries, spool)
        manifest = {
            "format": "Bytessence InstallMaker executable",
            "input_name": input_path.name,
            "input_size": len(data),
            "input_sha256": hashlib.sha256(data).hexdigest(),
            "container": container,
            "archive": archive,
            "internal_namespace_id": internal_id,
            "component_ids": sorted(ids),
            "payload_file_count": len(payload),
            "internal_file_count": len(entries) - len(payload),
            "entries": entries,
        }
        # Validation and decompression are complete before outputPath is touched.
        output_path.mkdir(parents=True, exist_ok=True)
        os.chmod(output_path, 0o775)
        for entry in payload:
            source = spool.joinpath(*safe_parts(entry["name"]))
            destination = output_path.joinpath(*safe_parts(entry["output_name"]))
            copy_validated(source, destination, entry.get("mtime"))
        if include_all:
            metadata_root = output_path / "_bytessence"
            for entry in entries:
                if entry["kind"] != "internal":
                    continue
                source = spool.joinpath(*safe_parts(entry["name"]))
                destination = metadata_root / "internal"
                destination = destination.joinpath(*safe_parts(entry["internal_path"]))
                copy_validated(source, destination, entry.get("mtime"))
            module_source = temporary / "decompressor.dll"
            start = container["module_offset"]
            module_source.write_bytes(data[start : start + container["module_size"]])
            copy_validated(module_source, metadata_root / "decompressor.dll", None)
            manifest_path = temporary / "manifest.json"
            manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            copy_validated(manifest_path, metadata_root / "manifest.json", None)
        ensure_tree_modes(output_path)
        return manifest


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract installable files from a Bytessence InstallMaker executable."
    )
    parser.add_argument("--all", action="store_true", help="also write internal resources, module, and metadata")
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputDir", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        manifest = extract(args.inputFile, args.outputDir, args.all)
    except FormatError as exc:
        print(f"bytessence.py: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"bytessence.py: output error: {exc}", file=sys.stderr)
        return 1
    print(
        f"Extracted {manifest['payload_file_count']} payload files "
        f"from {manifest['archive']['entry_count']} archive entries."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# Vibe coded by Codex
from __future__ import annotations

import argparse
import binascii
import html
import io
import json
import os
import re
import shutil
import struct
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


MAGIC = b"EKIF"
TOC_TRAILER = b"\x00"
RECORD_SIGNATURE = 0x0096
RECORD_APP_ID = 0x03E7
RESOURCE_SIGNATURES = (
    (b"GIF87a", "gif", "GIF87a image"),
    (b"GIF89a", "gif", "GIF89a image"),
    (b"BM", "bmp", "BMP image"),
    (b"II*\x00", "tif", "little-endian TIFF image"),
    (b"MM\x00*", "tif", "big-endian TIFF image"),
    (b"\xff\xd8\xff", "jpg", "JPEG image"),
    (b"\x89PNG\r\n\x1a\n", "png", "PNG image"),
)
WMF_PLACEABLE = b"\xd7\xcd\xc6\x9a"
ZIP_LOCAL = b"PK\x03\x04"
NATIVE_MARKER = b"\xf7\xff\xff\xff"


class FormatError(Exception):
    pass


@dataclass
class TocEntry:
    index: int
    thumbnail_marker: int
    record_offset: int
    record_length: int
    name: bytes


@dataclass
class Extent:
    offset: int
    length: int
    kind: str
    toc_entry: TocEntry | None = None


@dataclass
class Resource:
    role: str
    extension: str
    description: str
    data: bytes
    container_data: bytes | None = None
    container_extension: str | None = None
    container_description: str | None = None


@dataclass
class ParsedRecord:
    offset: int
    length: int
    kind: str
    label: str
    format_tag: int | None
    app_id: int | None
    metadata_length: int
    trailer: dict[str, Any] | None
    resources: list[Resource]


def le16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def le32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def cstring(data: bytes, offset: int) -> tuple[bytes, int]:
    end = data.find(b"\x00", offset)
    if end < 0:
        raise FormatError(f"missing NUL-terminated string at record-relative offset 0x{offset:x}")
    return data[offset:end], end + 1


def decode_name(raw: bytes) -> str:
    return raw.decode("cp1252", errors="replace")


def safe_component(value: str, fallback: str) -> str:
    value = value.replace("\\", "/").split("/")[-1].strip()
    value = re.sub(r"[\x00-\x1f<>:\"/\\|?*]+", "_", value)
    value = value.strip(" .")
    return value or fallback


def split_name(name: str, fallback: str) -> tuple[str, str]:
    safe = safe_component(name, fallback)
    if "." in safe:
        stem, ext = safe.rsplit(".", 1)
        return stem or fallback, ext.lower()
    return safe, ""


def ensure_group_readable(path: Path) -> None:
    if path.is_dir():
        path.chmod(0o775)
    else:
        path.chmod(0o664)


def write_file(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    ensure_group_readable(path)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    ensure_group_readable(path)


def parse_toc(data: bytes) -> tuple[int, int, int, list[TocEntry]]:
    if len(data) < 13:
        raise FormatError("file is too short")
    if data[:4] != MAGIC:
        raise FormatError("missing EKIF magic")

    toc_offset = le32(data, 8)
    if toc_offset < 12 or toc_offset + 7 > len(data):
        raise FormatError("table-of-contents offset is outside the file")
    if data[-1:] != TOC_TRAILER:
        raise FormatError("missing one-byte table terminator")

    entry_count = le16(data, toc_offset)
    table_view_0 = le16(data, toc_offset + 2)
    table_view_1 = le16(data, toc_offset + 4)

    entries: list[TocEntry] = []
    pos = toc_offset + 6
    for index in range(entry_count):
        if pos + 12 > len(data) - 1:
            raise FormatError("table entry runs past terminator")
        thumbnail_marker = le16(data, pos)
        record_offset = le32(data, pos + 2)
        record_length = le32(data, pos + 6)
        name_len = le16(data, pos + 10)
        pos += 12
        if thumbnail_marker != 0x009B:
            raise FormatError(f"unexpected table record marker 0x{thumbnail_marker:04x}")
        if pos + name_len > len(data) - 1:
            raise FormatError("table entry name runs past terminator")
        name = data[pos:pos + name_len]
        pos += name_len
        if record_offset < 12 or record_length <= 0 or record_offset + record_length > toc_offset:
            raise FormatError("table entry points outside the object area")
        entries.append(TocEntry(index, thumbnail_marker, record_offset, record_length, name))

    if pos != len(data) - 1:
        raise FormatError("table does not end immediately before the one-byte terminator")
    return toc_offset, entry_count, table_view_0, table_view_1, entries


def collect_extents(toc_offset: int, entries: list[TocEntry]) -> list[Extent]:
    spans = sorted((e.record_offset, e.record_offset + e.record_length, e) for e in entries)
    extents: list[Extent] = []
    cursor = 12
    last_end = 12
    for start, end, entry in spans:
        if start < last_end:
            raise FormatError("table entries overlap")
        if start > cursor:
            extents.append(Extent(cursor, start - cursor, "unindexed"))
        extents.append(Extent(start, end - start, "indexed", entry))
        cursor = end
        last_end = end
    if cursor < toc_offset:
        extents.append(Extent(cursor, toc_offset - cursor, "unindexed"))
    return sorted(extents, key=lambda item: item.offset)


def validate_gif(data: bytes) -> None:
    if not data.endswith(b";"):
        raise FormatError("GIF resource does not end with trailer byte 0x3b")


def validate_bmp(data: bytes) -> None:
    if len(data) < 14 or data[:2] != b"BM":
        raise FormatError("invalid BMP resource")
    declared = le32(data, 2)
    if declared != len(data):
        raise FormatError("BMP resource length does not match BMP header")


def validate_tiff(data: bytes) -> None:
    if len(data) < 8 or data[:4] not in (b"II*\x00", b"MM\x00*"):
        raise FormatError("invalid TIFF resource")


def validate_jpeg(data: bytes) -> None:
    if len(data) < 4 or not data.startswith(b"\xff\xd8\xff") or not data.endswith(b"\xff\xd9"):
        raise FormatError("invalid JPEG resource")


def validate_png(data: bytes) -> None:
    if not data.startswith(b"\x89PNG\r\n\x1a\n") or not data.endswith(b"IEND\xaeB`\x82"):
        raise FormatError("invalid PNG resource")


def validate_resource(data: bytes, extension: str) -> None:
    if extension == "gif":
        validate_gif(data)
    elif extension == "bmp":
        validate_bmp(data)
    elif extension == "tif":
        validate_tiff(data)
    elif extension == "jpg":
        validate_jpeg(data)
    elif extension == "png":
        validate_png(data)


def iter_signature_positions(record: bytes) -> list[tuple[int, bytes, str, str]]:
    positions: list[tuple[int, bytes, str, str]] = []
    for signature, extension, description in RESOURCE_SIGNATURES:
        start = 0
        while True:
            pos = record.find(signature, start)
            if pos < 0:
                break
            positions.append((pos, signature, extension, description))
            start = pos + 1
    return sorted(positions, key=lambda item: item[0])


def classify_after_resource(record: bytes, payload_end: int) -> tuple[dict[str, Any], int | None]:
    remaining = len(record) - payload_end
    if remaining == 0:
        return {"kind": "none", "length": 0}, None
    if remaining in (6, 18):
        return parse_trailer(record[payload_end:]), None

    if remaining > 6:
        length6 = le32(record, payload_end)
        marker6 = le16(record, payload_end + 4)
        if marker6 == 1 and length6 == remaining - 6:
            return {
                "kind": "native-length-6",
                "length": 6,
                "native_length": length6,
                "marker": marker6,
            }, payload_end + 6

    if remaining > 18:
        length18 = le32(record, payload_end)
        if length18 == remaining - 18:
            return {
                "kind": "native-length-18",
                "length": 18,
                "native_length": length18,
                "stored_length_1": le32(record, payload_end + 4),
                "stored_length_2": le32(record, payload_end + 8),
                "width_or_x_extent": le16(record, payload_end + 12),
                "height_or_y_extent": le16(record, payload_end + 14),
                "format_code": le16(record, payload_end + 16),
            }, payload_end + 18

    raise FormatError("resource trailer/native bridge does not match record length")


def parse_trailer(trailer: bytes) -> dict[str, Any]:
    if len(trailer) == 6:
        return {
            "kind": "trailer-6",
            "length": 6,
            "stored_length": le32(trailer, 0),
            "format_code": le16(trailer, 4),
        }
    if len(trailer) == 18:
        return {
            "kind": "trailer-18",
            "length": 18,
            "stored_length_0": le32(trailer, 0),
            "stored_length_1": le32(trailer, 4),
            "stored_length_2": le32(trailer, 8),
            "width_or_x_extent": le16(trailer, 12),
            "height_or_y_extent": le16(trailer, 14),
            "format_code": le16(trailer, 16),
        }
    raise FormatError("invalid trailer length")


def parse_native_container(native: bytes, preferred_extension: str) -> list[Resource]:
    if native.startswith(WMF_PLACEABLE):
        return [Resource("native", "wmf", "placeable WMF", native)]

    if native.startswith(ZIP_LOCAL):
        with zipfile.ZipFile(io.BytesIO(native)) as archive:
            infos = archive.infolist()
            if len(infos) != 1:
                raise FormatError("native ZIP container does not contain exactly one member")
            member = infos[0]
            payload = archive.read(member)
            extension = preferred_extension or extension_for_payload(payload)
            description = f"ZIP-wrapped native resource ({member.filename})"
            return [Resource(
                "native",
                extension,
                description,
                payload,
                container_data=native,
                container_extension="zip",
                container_description="raw native ZIP container",
            )]

    extension = extension_for_payload(native) or preferred_extension or "bin"
    return [Resource("native", extension, "native payload", native)]


def extension_for_payload(payload: bytes) -> str:
    for signature, extension, _description in RESOURCE_SIGNATURES:
        if payload.startswith(signature):
            return extension
    if payload.startswith(WMF_PLACEABLE):
        return "wmf"
    return ""


def parse_96_record(record: bytes, offset: int) -> ParsedRecord:
    if len(record) < 10:
        raise FormatError("0x0096 record is too short")
    if le16(record, 0) != RECORD_SIGNATURE:
        raise FormatError("record signature mismatch")
    format_tag = le32(record, 2)
    app_id = le16(record, 6)
    if format_tag not in (0x23, 0x24, 0x25):
        raise FormatError(f"unexpected record format tag 0x{format_tag:x}")
    if app_id != RECORD_APP_ID:
        raise FormatError(f"unexpected record app id 0x{app_id:04x}")

    raw_label, label_end = cstring(record, 8)
    label = decode_name(raw_label)
    resources: list[Resource] = []
    trailer: dict[str, Any] | None = None

    candidates: list[tuple[int, str, str, int, dict[str, Any], int | None]] = []
    for pos, _signature, extension, description in iter_signature_positions(record):
        if pos < 4:
            continue
        declared_length = le32(record, pos - 4)
        if declared_length <= 0 or pos + declared_length > len(record):
            continue
        try:
            candidate_trailer, native_start = classify_after_resource(record, pos + declared_length)
        except FormatError:
            continue
        candidates.append((pos, extension, description, declared_length, candidate_trailer, native_start))

    if candidates:
        pos, extension, description, declared_length, trailer, native_start = candidates[0]
        payload = record[pos:pos + declared_length]
        validate_resource(payload, extension)
        resources.append(Resource("preview", extension, description, payload))
        if native_start is not None:
            native = record[native_start:]
            preferred_extension = split_name(label, "resource")[1]
            resources.extend(parse_native_container(native, preferred_extension))
        return ParsedRecord(offset, len(record), "standard", label, format_tag, app_id, pos - 4, trailer, resources)

    native_marker = record.find(NATIVE_MARKER, label_end)
    if native_marker >= 0 and native_marker + 10 <= len(record):
        native_length = le32(record, native_marker + 4)
        marker = le16(record, native_marker + 8)
        native_start = native_marker + 10
        if marker == 1 and native_start + native_length == len(record):
            native = record[native_start:]
            preferred_extension = split_name(label, "resource")[1]
            resources.extend(parse_native_container(native, preferred_extension))
            trailer = {
                "kind": "native-only",
                "length": 10,
                "native_marker": "f7ffffff",
                "native_length": native_length,
                "format_code": marker,
            }
            return ParsedRecord(offset, len(record), "standard", label, format_tag, app_id, native_marker, trailer, resources)

    return ParsedRecord(offset, len(record), "metadata-only", label, format_tag, app_id, len(record), None, [])


def parse_special_record(record: bytes, offset: int) -> ParsedRecord:
    if len(record) != 225:
        raise FormatError("special DCT index record has unexpected length")
    if record[:3] != b"\x00\x00\x00":
        raise FormatError("special DCT index record has bad prefix")
    raw_name, pos = cstring(record, 3)
    if not raw_name:
        raise FormatError("special DCT index record has empty dictionary name")
    return ParsedRecord(offset, len(record), "dct-index", decode_name(raw_name), None, None, len(record), None, [])


def parse_record(record: bytes, offset: int) -> ParsedRecord:
    if record.startswith(struct.pack("<H", RECORD_SIGNATURE)):
        return parse_96_record(record, offset)
    if record.startswith(b"\x00\x00\x00"):
        return parse_special_record(record, offset)
    raise FormatError(f"unknown record type at file offset 0x{offset:x}")


def parse_file(data: bytes) -> tuple[dict[str, Any], list[tuple[Extent, ParsedRecord]]]:
    toc_offset, entry_count, table_view_0, table_view_1, entries = parse_toc(data)
    header_hint = le32(data, 4)
    extents = collect_extents(toc_offset, entries)
    records: list[tuple[Extent, ParsedRecord]] = []
    for extent in extents:
        record = data[extent.offset:extent.offset + extent.length]
        parsed = parse_record(record, extent.offset)
        records.append((extent, parsed))

    covered = 12 + sum(extent.length for extent in extents) + (len(data) - toc_offset)
    if covered != len(data):
        raise FormatError("internal coverage accounting failed")

    meta = {
        "magic": MAGIC.decode("ascii"),
        "file_size": len(data),
        "header_record_hint": header_hint,
        "toc_offset": toc_offset,
        "toc_size": len(data) - toc_offset,
        "toc_entry_count": entry_count,
        "toc_table_view_0": table_view_0,
        "toc_table_view_1": table_view_1,
        "toc_terminator": "00",
        "extent_count": len(extents),
        "indexed_record_count": sum(1 for extent in extents if extent.kind == "indexed"),
        "unindexed_record_count": sum(1 for extent in extents if extent.kind == "unindexed"),
    }
    return meta, records


def unique_path(base_dir: Path, relative: Path, used: set[Path]) -> Path:
    candidate = relative
    counter = 2
    while candidate in used or (base_dir / candidate).exists():
        candidate = relative.with_name(f"{relative.stem}_{counter}{relative.suffix}")
        counter += 1
    used.add(candidate)
    return base_dir / candidate


def extract(input_file: Path, output_dir: Path, full: bool = False) -> dict[str, Any]:
    data = input_file.read_bytes()
    meta, records = parse_file(data)

    parent = output_dir.parent if output_dir.parent != Path("") else Path(".")
    parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.tmp-", dir=str(parent)))
    used: set[Path] = set()
    manifest_records: list[dict[str, Any]] = []

    try:
        resource_count = 0
        indexed_resource_count = 0
        native_count = 0
        preview_count = 0
        for sequence, (extent, record) in enumerate(records):
            toc_name = decode_name(extent.toc_entry.name) if extent.toc_entry else ""
            display_name = toc_name or record.label or f"record_{sequence:04d}"
            stem, original_ext = split_name(display_name, f"record_{sequence:04d}")
            record_prefix = f"{sequence:04d}_{safe_component(stem, f'record_{sequence:04d}')}"
            record_info: dict[str, Any] = {
                "sequence": sequence,
                "extent_kind": extent.kind,
                "toc_index": extent.toc_entry.index if extent.toc_entry else None,
                "offset": extent.offset,
                "length": extent.length,
                "record_kind": record.kind,
                "format_tag": record.format_tag,
                "app_id": record.app_id,
                "label": record.label,
                "toc_name": toc_name,
                "metadata_length": record.metadata_length,
                "trailer": record.trailer,
                "resources": [],
            }

            for resource_index, resource in enumerate(record.resources):
                resource_count += 1
                if extent.kind == "indexed":
                    indexed_resource_count += 1
                if resource.role == "preview":
                    preview_count += 1
                    rel = Path(f"{record_prefix}_preview.{resource.extension}")
                else:
                    native_count += 1
                    ext = original_ext or resource.extension
                    if resource.extension and ext.lower() != resource.extension.lower() and resource.extension not in ("bin", ""):
                        ext = resource.extension
                    rel = Path(f"{record_prefix}_native.{ext or 'bin'}")
                out_path = unique_path(tmp, rel, used)
                write_file(out_path, resource.data)
                resource_entry = {
                    "role": resource.role,
                    "description": resource.description,
                    "path": str(out_path.relative_to(tmp)),
                    "size": len(resource.data),
                    "crc32": f"{binascii.crc32(resource.data) & 0xffffffff:08x}",
                }
                if full and resource.container_data is not None:
                    container_rel = Path(f"{record_prefix}_container.{resource.container_extension or 'bin'}")
                    container_path = unique_path(tmp, container_rel, used)
                    write_file(container_path, resource.container_data)
                    resource_entry["container"] = {
                        "description": resource.container_description,
                        "path": str(container_path.relative_to(tmp)),
                        "size": len(resource.container_data),
                        "crc32": f"{binascii.crc32(resource.container_data) & 0xffffffff:08x}",
                    }
                record_info["resources"].append(resource_entry)
            manifest_records.append(record_info)

        manifest = {
            "input_file": str(input_file),
            **meta,
            "resource_count": resource_count,
            "indexed_resource_count": indexed_resource_count,
            "preview_resource_count": preview_count,
            "native_resource_count": native_count,
            "records": manifest_records,
        }
        if full:
            write_text(tmp / "manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

        if output_dir.exists():
            shutil.rmtree(output_dir)
        tmp.rename(output_dir)
        for root, dirs, files in os.walk(output_dir):
            for dirname in dirs:
                ensure_group_readable(Path(root) / dirname)
            for filename in files:
                ensure_group_readable(Path(root) / filename)
        ensure_group_readable(output_dir)
        return manifest
    except Exception:
        shutil.rmtree(tmp, ignore_errors=True)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract resources from MediaPaq DCF/PAQ catalog files.")
    parser.add_argument("--full", action="store_true", help="write manifest.json and raw native ZIP containers")
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputDir", type=Path)
    args = parser.parse_args(argv)

    try:
        manifest = extract(args.inputFile, args.outputDir, full=args.full)
    except Exception as exc:
        print(f"mediaPaqDCF: {exc}", file=sys.stderr)
        return 1

    print(
        f"extracted {manifest['resource_count']} resources "
        f"({manifest['indexed_resource_count']} indexed) from {args.inputFile}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# Vibe coded by Codex
"""Strict extractor for Microsoft MediaView resource archive containers."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


MAGIC_BASE = b"?_\x04"
MAGIC_PLAIN = MAGIC_BASE + b"\x01"
MAGIC_INCREMENTAL = MAGIC_BASE + b"\x11"
HEADER_SIZE = 36
FREE_BLOCK_SIZE = 8 + 510 * 16
DIRECTORY_HEADER_SIZE = 48
DIRECTORY_MAGIC = 0x293B
DIRECTORY_FLAGS = 0x0102
DIRECTORY_PAGE_SIZE = 8192
DIRECTORY_STRUCTURE = b"VOO1" + b"\0" * 12
IVT_TRAILER_SIZE = 36


class M20Error(Exception):
    """An input is not a supported, structurally valid MediaView archive."""


@dataclass(frozen=True)
class Resource:
    raw_name: bytes
    offset: int
    size: int
    flags: int
    output_name: str

    @property
    def end(self) -> int:
        return self.offset + self.size


@dataclass
class PageResult:
    first_name: bytes
    last_name: bytes
    leaf_pages: list[int]
    resources: list[tuple[bytes, int, int, int]]


@dataclass
class Archive:
    data: bytes
    declared_size: int
    directory_offset: int
    free_chain_offset: int
    directory_size: int
    padding_size: int
    free_spans: list[tuple[int, int]]
    free_chain_blocks: list[tuple[int, int]]
    page_size: int
    total_pages: int
    levels: int
    page_splits: int
    root_page: int
    resources: list[Resource]
    ivt_timestamp: Optional[int]


def fail(message: str) -> None:
    raise M20Error(message)


def unpack_from(fmt: str, data: bytes, offset: int, context: str) -> tuple:
    size = struct.calcsize(fmt)
    if offset < 0 or offset + size > len(data):
        fail(f"truncated {context}")
    return struct.unpack_from(fmt, data, offset)


def read_uleb128(data: bytes, pos: int, end: int, context: str) -> tuple[int, int]:
    value = 0
    shift = 0
    start = pos
    while pos < end and pos < len(data):
        byte = data[pos]
        pos += 1
        if shift == 63 and byte > 1:
            fail(f"overflowing ULEB128 in {context}")
        if shift > 63:
            fail(f"overflowing ULEB128 in {context}")
        value |= (byte & 0x7F) << shift
        if byte < 0x80:
            if pos - start > 1 and byte == 0:
                fail(f"non-canonical ULEB128 in {context}")
            return value, pos
        shift += 7
    fail(f"unterminated ULEB128 in {context}")


def safe_output_name(raw_name: bytes) -> str:
    """Map an opaque on-disk name injectively to one host directory entry."""
    if not raw_name:
        return "%EMPTY"
    out: list[str] = []
    for byte in raw_name:
        if byte == 0 or byte < 0x20 or byte == 0x7F or byte >= 0x80:
            out.append(f"%{byte:02X}")
        elif byte in (ord("%"), ord("/"), ord("\\")):
            out.append(f"%{byte:02X}")
        else:
            out.append(chr(byte))
    name = "".join(out)
    if name in (".", ".."):
        name = "".join(f"%{byte:02X}" for byte in raw_name)
    return name


def parse_free_chain(
    data: bytes,
    first_offset: int,
    directory_offset: int,
    directory_end: int,
    archive_end: int,
) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    free_spans: list[tuple[int, int]] = []
    blocks: list[tuple[int, int]] = []
    seen: set[int] = set()
    offset = first_offset
    while offset:
        if offset in seen:
            fail("cyclic free-chain block list")
        seen.add(offset)
        if offset < HEADER_SIZE or offset + FREE_BLOCK_SIZE > archive_end:
            fail("free-chain block outside the archive")
        if offset < directory_end and offset + FREE_BLOCK_SIZE > directory_offset:
            fail("free-chain block overlaps the directory")
        blocks.append((offset, offset + FREE_BLOCK_SIZE))
        count, capacity, next_offset = unpack_from(
            "<HHI", data, offset, "free-chain block header"
        )
        if capacity != 510 or count > capacity:
            fail("invalid free-chain block capacity/count")
        pos = offset + 8
        for index in range(capacity):
            span_offset, span_size = unpack_from(
                "<QQ", data, pos, f"free-chain record {index}"
            )
            pos += 16
            if index < count:
                if span_size == 0:
                    fail("zero-length active free span")
                if span_offset < HEADER_SIZE or span_offset + span_size > archive_end:
                    fail("free span outside the archive")
                if span_offset < directory_end and span_offset + span_size > directory_offset:
                    fail("free span overlaps the directory")
                free_spans.append((span_offset, span_offset + span_size))
            elif span_offset != 0 or span_size != 0:
                fail("nonzero unused free-chain record")
        offset = next_offset
    return free_spans, blocks


def parse_archive(data: bytes) -> Archive:
    if len(data) < HEADER_SIZE:
        fail("file is shorter than the MediaView header")
    magic, directory_offset, free_chain_offset, declared_size, directory_size = (
        unpack_from("<4sQQQQ", data, 0, "MediaView header")
    )
    if magic not in (MAGIC_PLAIN, MAGIC_INCREMENTAL):
        fail("bad MediaView signature")
    ivt_timestamp: Optional[int] = None
    if declared_size == len(data):
        archive_end = declared_size
    elif declared_size + IVT_TRAILER_SIZE == len(data):
        timestamp, reserved, trailer_magic, trailer_version, trailer_size = unpack_from(
            "<I20s4sII", data, declared_size, "IVT trailer"
        )
        if any(reserved):
            fail("nonzero IVT trailer reserved bytes")
        if trailer_magic != b"IVTV" or trailer_version != 6:
            fail("invalid IVT trailer signature/version")
        if trailer_size != IVT_TRAILER_SIZE:
            fail("invalid IVT trailer size")
        ivt_timestamp = timestamp
        archive_end = declared_size
    else:
        fail("declared archive size does not match the input length")
    if directory_offset < HEADER_SIZE or directory_offset > archive_end:
        fail("directory offset outside the archive")
    directory_end = directory_offset + directory_size
    if directory_end > archive_end:
        fail("directory extends beyond end of file")
    if not (HEADER_SIZE <= free_chain_offset < directory_offset):
        fail("free-chain offset outside the data area")
    padding = data[HEADER_SIZE:free_chain_offset]
    if any(padding):
        fail("nonzero bytes in the main-header padding")

    free_spans, free_chain_blocks = parse_free_chain(
        data, free_chain_offset, directory_offset, directory_end, archive_end
    )

    d = directory_offset
    (
        directory_magic,
        directory_flags,
        page_size,
        structure,
        must_be_zero,
        page_splits,
        root_page,
        must_be_minus_one,
        total_pages,
        levels,
        total_entries,
    ) = unpack_from("<HHH16sIIIIIHI", data, d, "directory header")
    if directory_magic != DIRECTORY_MAGIC:
        fail("bad directory B+ tree signature")
    if directory_flags != DIRECTORY_FLAGS:
        fail("unsupported directory flags")
    if page_size != DIRECTORY_PAGE_SIZE:
        fail("unsupported directory page size")
    if structure != DIRECTORY_STRUCTURE:
        fail("unsupported directory record structure")
    if must_be_zero != 0 or must_be_minus_one != 0xFFFFFFFF:
        fail("invalid directory reserved fields")
    if total_pages == 0 or levels == 0 or levels > total_pages:
        fail("invalid directory page/level count")
    if root_page >= total_pages:
        fail("directory root page outside the page array")
    expected_directory_size = DIRECTORY_HEADER_SIZE + total_pages * page_size
    if directory_size != expected_directory_size:
        fail("directory size is inconsistent with its page array")

    if magic == MAGIC_PLAIN:
        if directory_end != archive_end:
            fail("plain MediaView archive has bytes after its directory")

    visited: set[int] = set()

    def parse_page(page_number: int, level: int) -> PageResult:
        if page_number >= total_pages:
            fail("B+ tree child page outside the page array")
        if page_number in visited:
            fail("B+ tree page is referenced more than once")
        visited.add(page_number)
        start = d + DIRECTORY_HEADER_SIZE + page_number * page_size
        unused, count = unpack_from("<HH", data, start, "B+ tree page header")
        used_end = start + page_size - unused
        if used_end < start + 4 or used_end > start + page_size:
            fail("invalid B+ tree unused-byte count")

        if level == 1:
            if used_end < start + 12:
                fail("truncated B+ tree leaf header")
            previous_page, next_page = unpack_from(
                "<ii", data, start + 4, "B+ tree leaf links"
            )
            pos = start + 12
            records: list[tuple[bytes, int, int, int]] = []
            for entry_index in range(count):
                if pos >= used_end:
                    fail("truncated directory leaf entry")
                name_length = data[pos]
                pos += 1
                if pos + name_length > used_end:
                    fail("invalid directory resource name")
                name = data[pos : pos + name_length]
                pos += name_length
                resource_offset, pos = read_uleb128(
                    data, pos, used_end, "directory resource offset"
                )
                resource_size, pos = read_uleb128(
                    data, pos, used_end, "directory resource size"
                )
                if pos >= used_end:
                    fail("missing directory resource flags")
                resource_flags = data[pos]
                pos += 1
                if resource_flags != 0:
                    fail("unsupported nonzero directory resource flags")
                records.append((name, resource_offset, resource_size, resource_flags))
            if pos != used_end:
                fail("leaf used-byte count does not match its records")
            if not records:
                fail("empty B+ tree leaf page")
            leaf_links[page_number] = (previous_page, next_page)
            return PageResult(records[0][0], records[-1][0], [page_number], records)

        pos = start + 4
        if pos + 4 > used_end:
            fail("truncated B+ tree index page")
        first_child = unpack_from("<I", data, pos, "B+ tree first child")[0]
        pos += 4
        separators: list[bytes] = []
        children = [first_child]
        for entry_index in range(count):
            if pos >= used_end:
                fail("truncated B+ tree index entry")
            name_length = data[pos]
            pos += 1
            if name_length == 0 or pos + name_length + 4 > used_end:
                fail("invalid B+ tree index key")
            separators.append(data[pos : pos + name_length])
            pos += name_length
            children.append(unpack_from("<I", data, pos, "B+ tree child")[0])
            pos += 4
        if pos != used_end:
            fail("index used-byte count does not match its records")
        child_results = [parse_page(child, level - 1) for child in children]
        for separator, right in zip(separators, child_results[1:]):
            if separator != right.first_name:
                fail("B+ tree separator is not the first key of its right child")
        return PageResult(
            child_results[0].first_name,
            child_results[-1].last_name,
            [p for result in child_results for p in result.leaf_pages],
            [record for result in child_results for record in result.resources],
        )

    leaf_links: dict[int, tuple[int, int]] = {}
    tree = parse_page(root_page, levels)
    if len(visited) != total_pages:
        fail("directory contains unreachable B+ tree pages")
    if len(tree.resources) != total_entries:
        fail("directory entry count does not match its header")
    for index, page_number in enumerate(tree.leaf_pages):
        expected_previous = tree.leaf_pages[index - 1] if index else -1
        expected_next = tree.leaf_pages[index + 1] if index + 1 < len(tree.leaf_pages) else -1
        if leaf_links[page_number] != (expected_previous, expected_next):
            fail("B+ tree leaf links disagree with index traversal order")

    def collation_key(name: bytes) -> tuple[int, tuple[int, ...]]:
        if not name:
            leading_class = -1
        else:
            leading_class = 0 if name.startswith(b">") else 1 if name.startswith(b"|") else 2
        # ASCII case-insensitive order, except '_' has the legacy collation
        # weight between '/' and '0' rather than its byte value after 'Z'.
        weights = tuple(
            95 if byte == ord("_") else 2 * (byte + 32 if 65 <= byte <= 90 else byte)
            for byte in name
        )
        return leading_class, weights

    names_in_order = [record[0] for record in tree.resources]
    if any(
        collation_key(left) >= collation_key(right)
        for left, right in zip(names_in_order, names_in_order[1:])
    ):
        fail("directory resource names are not in MediaView collation order")

    resources: list[Resource] = []
    raw_names: set[bytes] = set()
    output_names: set[str] = set()
    for raw_name, offset, size, flags in tree.resources:
        if raw_name in raw_names:
            fail("duplicate resource name")
        output_name = safe_output_name(raw_name)
        if output_name in output_names:
            fail("resource names collide after safe host-name encoding")
        if offset < HEADER_SIZE or offset + size > archive_end:
            fail("resource extent outside the archive")
        if offset < directory_end and offset + size > directory_offset:
            fail("resource extent overlaps the directory")
        raw_names.add(raw_name)
        output_names.add(output_name)
        resources.append(Resource(raw_name, offset, size, flags, output_name))

    # Every byte must belong to exactly one structural, allocated, or free extent.
    extents: list[tuple[int, int, str]] = [
        (0, HEADER_SIZE, "header"),
        (directory_offset, directory_end, "directory"),
    ]
    if free_chain_offset > HEADER_SIZE:
        extents.append((HEADER_SIZE, free_chain_offset, "header padding"))
    extents.extend((a, b, "free-chain block") for a, b in free_chain_blocks)
    extents.extend((a, b, "free span") for a, b in free_spans)
    extents.extend((r.offset, r.end, "resource") for r in resources if r.size)
    if archive_end < len(data):
        extents.append((archive_end, len(data), "IVT trailer"))
    extents.sort()
    cursor = 0
    for start, end, kind in extents:
        if start != cursor:
            if start < cursor:
                fail(f"overlapping archive extent at offset {start}")
            fail(f"unaccounted archive bytes at offsets {cursor}..{start - 1}")
        if end <= start:
            fail(f"invalid empty {kind} extent")
        cursor = end
    if cursor != len(data):
        fail(f"unaccounted archive bytes at offsets {cursor}..{len(data) - 1}")

    return Archive(
        data=data,
        declared_size=declared_size,
        directory_offset=directory_offset,
        free_chain_offset=free_chain_offset,
        directory_size=directory_size,
        padding_size=free_chain_offset - HEADER_SIZE,
        free_spans=free_spans,
        free_chain_blocks=free_chain_blocks,
        page_size=page_size,
        total_pages=total_pages,
        levels=levels,
        page_splits=page_splits,
        root_page=root_page,
        resources=resources,
        ivt_timestamp=ivt_timestamp,
    )


def preflight_output(output_dir: Path, resources: list[Resource], include_metadata: bool) -> None:
    if output_dir.exists() and not output_dir.is_dir():
        fail("output path exists but is not a directory")
    for resource in resources:
        target = output_dir / resource.output_name
        if target.exists() and not target.is_file():
            fail(f"output target is not a regular file: {target}")
    if include_metadata:
        if any(resource.output_name == "_m20_manifest.json" for resource in resources):
            fail("archive resource name conflicts with the --all metadata file")
        target = output_dir / "_m20_manifest.json"
        if target.exists() and not target.is_file():
            fail(f"metadata target is not a regular file: {target}")


def write_bytes_atomic(path: Path, payload: bytes) -> None:
    temporary = path.with_name(f".{path.name}.m20-tmp-{os.getpid()}")
    try:
        with temporary.open("wb") as handle:
            handle.write(payload)
        os.chmod(temporary, 0o664)
        os.replace(temporary, path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def build_manifest(input_path: Path, archive: Archive) -> bytes:
    resources = []
    for resource in archive.resources:
        payload = archive.data[resource.offset : resource.end]
        resources.append(
            {
                "name_bytes_hex": resource.raw_name.hex(),
                "output_name": resource.output_name,
                "offset": resource.offset,
                "size": resource.size,
                "flags": resource.flags,
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        )
    manifest = {
        "format": "Microsoft MediaView resource archive container",
        "input_extension": input_path.suffix,
        "input_name": input_path.name,
        "input_size": len(archive.data),
        "declared_archive_size": archive.declared_size,
        "input_sha256": hashlib.sha256(archive.data).hexdigest(),
        "ivt_trailer": (
            {"timestamp": archive.ivt_timestamp, "version": 6, "size": IVT_TRAILER_SIZE}
            if archive.ivt_timestamp is not None
            else None
        ),
        "header_size": HEADER_SIZE,
        "header_padding_size": archive.padding_size,
        "free_chain_offset": archive.free_chain_offset,
        "free_chain_block_count": len(archive.free_chain_blocks),
        "free_span_count": len(archive.free_spans),
        "directory_offset": archive.directory_offset,
        "directory_size": archive.directory_size,
        "directory_page_size": archive.page_size,
        "directory_page_count": archive.total_pages,
        "directory_levels": archive.levels,
        "directory_root_page": archive.root_page,
        "directory_page_splits": archive.page_splits,
        "resource_count": len(archive.resources),
        "resource_bytes": sum(resource.size for resource in archive.resources),
        "resources": resources,
    }
    return (json.dumps(manifest, indent=2, ensure_ascii=True) + "\n").encode("utf-8")


def extract(input_path: Path, output_dir: Path, include_metadata: bool) -> Archive:
    try:
        data = input_path.read_bytes()
    except OSError as exc:
        fail(f"cannot read input: {exc}")
    archive = parse_archive(data)
    preflight_output(output_dir, archive.resources, include_metadata)

    output_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(output_dir, os.stat(output_dir).st_mode | 0o070)
    for resource in archive.resources:
        write_bytes_atomic(
            output_dir / resource.output_name,
            archive.data[resource.offset : resource.end],
        )
    if include_metadata:
        write_bytes_atomic(
            output_dir / "_m20_manifest.json", build_manifest(input_path, archive)
        )
    return archive


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Strictly validate and extract every resource from a MediaView archive."
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="also write _m20_manifest.json (resources are always all extracted)",
    )
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputDir", type=Path)
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    args = make_parser().parse_args(argv)
    try:
        archive = extract(args.inputFile, args.outputDir, args.all)
    except M20Error as exc:
        print(f"mediaView.py: error: {exc}", file=sys.stderr)
        return 1
    print(
        f"extracted {len(archive.resources)} resources "
        f"({sum(resource.size for resource in archive.resources)} bytes) "
        f"to {args.outputDir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# Vibe coded by Codex
"""Strict extractor for the block-compressed MSZP resource format."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from pathlib import PurePosixPath
import shutil
import struct
import sys
import tempfile
from typing import BinaryIO
from urllib.parse import unquote
import zlib


MAGIC = b"mszp"
GLOBAL_HEADER_SIZE = 12
BLOCK_MARKER = b"CK"
MSZIP_WINDOW_SIZE = 32 * 1024
MSZIP_MAX_STORED_SIZE = MSZIP_WINDOW_SIZE + 12


class MSZPError(Exception):
    """Raised when an input violates the MSZP format."""


def read_exact(stream: BinaryIO, size: int, description: str) -> bytes:
    data = stream.read(size)
    if len(data) != size:
        raise MSZPError(f"truncated {description}")
    return data


def output_relative_path(input_path: Path) -> Path:
    """Map the externally encoded resource name safely below outputDir."""
    try:
        decoded = unquote(input_path.name, encoding="utf-8", errors="strict")
    except UnicodeError as exc:
        raise MSZPError("input filename is not valid percent-encoded UTF-8") from exc

    if "\x00" in decoded or "\\" in decoded:
        raise MSZPError("input filename cannot be mapped to a safe resource path")

    # Resource names in this family may be URL-style absolute paths.  Their
    # leading slash denotes the resource root, which is outputDir here.
    relative = decoded.lstrip("/")
    pieces = relative.split("/")
    if not relative or any(piece in {"", ".", ".."} for piece in pieces):
        raise MSZPError("input filename cannot be mapped to a safe resource path")

    logical = PurePosixPath(*pieces)
    return Path(*logical.parts)


def inflate_and_validate(input_path: Path, staged_output: BinaryIO) -> dict[str, object]:
    """Validate the complete member and write its payload only to staging."""
    input_hash = hashlib.sha256()
    output_hash = hashlib.sha256()
    blocks: list[dict[str, int]] = []

    try:
        source = input_path.open("rb")
    except OSError as exc:
        raise MSZPError(f"cannot open input: {exc}") from exc

    with source:
        def tracked_read(size: int, description: str) -> bytes:
            data = read_exact(source, size, description)
            input_hash.update(data)
            return data

        header = tracked_read(GLOBAL_HEADER_SIZE, "global header")
        magic, total_size, block_size = struct.unpack("<4sII", header)

        if magic != MAGIC:
            raise MSZPError("bad magic (expected lowercase ASCII 'mszp')")
        if not 1 <= block_size <= MSZIP_WINDOW_SIZE:
            raise MSZPError("declared block size is outside the MSZIP 32 KiB limit")

        produced = 0
        block_index = 0
        file_offset = GLOBAL_HEADER_SIZE
        history = b""

        while True:
            raw_uncompressed_size = tracked_read(2, "block size or terminator")
            uncompressed_size = struct.unpack("<H", raw_uncompressed_size)[0]
            file_offset += 2

            if uncompressed_size == 0:
                terminator_offset = file_offset - 2
                break

            if produced >= total_size:
                raise MSZPError("block appears after the declared uncompressed size")

            expected_size = min(block_size, total_size - produced)
            if uncompressed_size != expected_size:
                raise MSZPError(
                    f"block {block_index} has uncompressed size {uncompressed_size}; "
                    f"expected {expected_size}"
                )

            compressed_size = struct.unpack(
                "<H", tracked_read(2, f"compressed size for block {block_index}")
            )[0]
            descriptor_offset = file_offset - 2
            file_offset += 2

            if compressed_size <= len(BLOCK_MARKER):
                raise MSZPError(f"block {block_index} has no DEFLATE stream")
            if compressed_size > MSZIP_MAX_STORED_SIZE:
                raise MSZPError(f"block {block_index} exceeds the MSZIP stored-size limit")

            payload_offset = file_offset
            payload = tracked_read(compressed_size, f"payload for block {block_index}")
            file_offset += compressed_size

            if payload[:2] != BLOCK_MARKER:
                raise MSZPError(f"block {block_index} has a bad CK marker")

            if history:
                inflater = zlib.decompressobj(wbits=-15, zdict=history)
            else:
                inflater = zlib.decompressobj(wbits=-15)
            try:
                # One byte beyond the declared size is enough to prove a size
                # violation without allowing a malformed stream to exhaust RAM.
                expanded = inflater.decompress(payload[2:], uncompressed_size + 1)
            except zlib.error as exc:
                raise MSZPError(f"block {block_index} has invalid raw DEFLATE data: {exc}") from exc

            if len(expanded) != uncompressed_size:
                raise MSZPError(
                    f"block {block_index} expands to more than {uncompressed_size} bytes"
                    if len(expanded) > uncompressed_size
                    else f"block {block_index} expands to {len(expanded)} bytes; "
                    f"expected {uncompressed_size}"
                )
            if not inflater.eof:
                raise MSZPError(f"block {block_index} has an incomplete DEFLATE stream")
            if inflater.unused_data or inflater.unconsumed_tail:
                raise MSZPError(f"block {block_index} has bytes after its DEFLATE stream")

            staged_output.write(expanded)
            output_hash.update(expanded)
            history = (history + expanded)[-MSZIP_WINDOW_SIZE:]
            blocks.append(
                {
                    "index": block_index,
                    "descriptor_offset": descriptor_offset,
                    "payload_offset": payload_offset,
                    "uncompressed_offset": produced,
                    "uncompressed_size": uncompressed_size,
                    "stored_size": compressed_size,
                    "deflate_size": compressed_size - len(BLOCK_MARKER),
                }
            )
            produced += uncompressed_size
            block_index += 1

        if produced != total_size:
            raise MSZPError(
                f"terminator reached after {produced} uncompressed bytes; expected {total_size}"
            )

        trailing = source.read(1)
        if trailing:
            raise MSZPError("data follows the two-byte zero terminator")

    staged_output.flush()
    os.fsync(staged_output.fileno())
    return {
        "format": "MSZP",
        "magic_ascii": MAGIC.decode("ascii"),
        "uncompressed_size": total_size,
        "block_size": block_size,
        "block_count": len(blocks),
        "terminator_offset": terminator_offset,
        "input_size": file_offset,
        "input_sha256": input_hash.hexdigest(),
        "output_sha256": output_hash.hexdigest(),
        "blocks": blocks,
    }


def make_staging_file() -> tuple[BinaryIO, Path]:
    handle = tempfile.NamedTemporaryFile(prefix="mszp-", suffix=".tmp", delete=False)
    return handle, Path(handle.name)


def write_metadata_staging(metadata: dict[str, object]) -> Path:
    handle, path = make_staging_file()
    try:
        with handle:
            encoded = (json.dumps(metadata, indent=2, sort_keys=True) + "\n").encode("utf-8")
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(path, 0o664)
        return path
    except Exception:
        path.unlink(missing_ok=True)
        raise


def ensure_directory(path: Path) -> None:
    missing: list[Path] = []
    current = path
    while not current.exists():
        missing.append(current)
        current = current.parent
    path.mkdir(parents=True, exist_ok=True)
    for created in reversed(missing):
        os.chmod(created, 0o775)


def commit_staged_file(staged_path: Path, destination: Path) -> None:
    """Copy staging onto the destination filesystem, then rename atomically."""
    local_handle = tempfile.NamedTemporaryFile(
        prefix=".mszp-", suffix=".tmp", dir=destination.parent, delete=False
    )
    local_path = Path(local_handle.name)
    try:
        with local_handle, staged_path.open("rb") as source:
            shutil.copyfileobj(source, local_handle)
            local_handle.flush()
            os.fsync(local_handle.fileno())
        os.chmod(local_path, 0o664)
        os.replace(local_path, destination)
    finally:
        local_path.unlink(missing_ok=True)


def extract(input_path: Path, output_dir: Path, include_metadata: bool) -> tuple[Path, Path | None]:
    relative_output = output_relative_path(input_path)
    staged_handle, staged_path = make_staging_file()
    metadata_path: Path | None = None
    staged_metadata: Path | None = None

    try:
        with staged_handle:
            metadata = inflate_and_validate(input_path, staged_handle)

        destination = output_dir / relative_output
        output_root = output_dir.resolve(strict=False)
        resolved_destination = destination.resolve(strict=False)
        if not resolved_destination.is_relative_to(output_root):
            raise MSZPError("resolved resource path escapes outputDir through a symbolic link")
        metadata["input_file"] = str(input_path)
        metadata["output_file"] = str(relative_output)

        if include_metadata:
            metadata_path = destination.with_name(destination.name + ".mszp.json")
            staged_metadata = write_metadata_staging(metadata)

        ensure_directory(destination.parent)
        commit_staged_file(staged_path, destination)

        if staged_metadata is not None and metadata_path is not None:
            commit_staged_file(staged_metadata, metadata_path)
            staged_metadata = None

        return destination, metadata_path
    finally:
        if staged_path != Path():
            staged_path.unlink(missing_ok=True)
        if staged_metadata is not None:
            staged_metadata.unlink(missing_ok=True)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Strictly validate and extract one MSZP-compressed resource."
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="also write a .mszp.json structural metadata sidecar",
    )
    parser.add_argument("inputFile", type=Path, help="MSZP member to extract")
    parser.add_argument("outputDir", type=Path, help="destination directory (may already exist)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        destination, metadata_path = extract(args.inputFile, args.outputDir, args.all)
    except (MSZPError, OSError) as exc:
        print(f"mszp.py: {exc}", file=sys.stderr)
        return 1

    print(destination)
    if metadata_path is not None:
        print(metadata_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

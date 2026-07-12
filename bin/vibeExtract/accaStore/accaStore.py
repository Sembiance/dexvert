#!/usr/bin/env python3
# Vibe coded by Codex
"""Strict extractor for the signed PE32 payload profile used by ACCAStore.

The observed ACCAStore objects are raw executable payloads, not archives.  A
successful extraction therefore emits one byte-identical file.  With --all,
an additional JSON description of the validated PE structure is emitted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
from typing import Any


class FormatError(ValueError):
    """Raised when an input is not the supported ACCAStore payload profile."""


DIRECTORY_NAMES = (
    "export",
    "import",
    "resource",
    "exception",
    "security",
    "base_relocation",
    "debug",
    "architecture",
    "global_pointer",
    "tls",
    "load_configuration",
    "bound_import",
    "import_address_table",
    "delay_import",
    "clr_runtime",
    "reserved",
)


RESOURCE_TYPE_NAMES = {
    1: "CURSOR",
    2: "BITMAP",
    3: "ICON",
    4: "MENU",
    5: "DIALOG",
    6: "STRING",
    7: "FONTDIR",
    8: "FONT",
    9: "ACCELERATOR",
    10: "RCDATA",
    11: "MESSAGETABLE",
    12: "GROUP_CURSOR",
    14: "GROUP_ICON",
    16: "VERSION",
    17: "DLGINCLUDE",
    19: "PLUGPLAY",
    20: "VXD",
    21: "ANICURSOR",
    22: "ANIICON",
    23: "HTML",
    24: "MANIFEST",
}


def fail(condition: bool, message: str) -> None:
    if not condition:
        raise FormatError(message)


def is_power_of_two(value: int) -> bool:
    return value > 0 and value & (value - 1) == 0


def align_up(value: int, alignment: int) -> int:
    return (value + alignment - 1) & ~(alignment - 1)


def unpack_from(fmt: str, data: bytes, offset: int, what: str) -> tuple[Any, ...]:
    size = struct.calcsize(fmt)
    fail(0 <= offset <= len(data) - size, f"truncated {what}")
    return struct.unpack_from(fmt, data, offset)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pe_checksum(data: bytes, checksum_offset: int) -> int:
    """Compute the PE checksum with its four-byte field treated as zero."""
    total = 0
    for offset in range(0, len(data), 2):
        if checksum_offset <= offset < checksum_offset + 4:
            word = 0
        elif offset + 1 < len(data):
            word = data[offset] | data[offset + 1] << 8
        else:
            word = data[offset]
        total += word
        total = (total & 0xFFFF) + (total >> 16)
    total = (total & 0xFFFF) + (total >> 16)
    return (total + len(data)) & 0xFFFFFFFF


def der_object_length(blob: bytes) -> int:
    """Return the encoded size of one DER object, validating its length form."""
    fail(len(blob) >= 2, "truncated PKCS#7 DER object")
    first = blob[1]
    if first < 0x80:
        header_size = 2
        content_size = first
    else:
        count = first & 0x7F
        fail(1 <= count <= 4, "unsupported or indefinite PKCS#7 DER length")
        fail(len(blob) >= 2 + count, "truncated PKCS#7 DER length")
        fail(blob[2] != 0, "non-minimal PKCS#7 DER length")
        content_size = int.from_bytes(blob[2 : 2 + count], "big")
        fail(content_size >= 0x80, "non-minimal PKCS#7 DER long length")
        header_size = 2 + count
    total = header_size + content_size
    fail(total <= len(blob), "truncated PKCS#7 DER content")
    return total


def validate_payload(data: bytes, source_name: str) -> dict[str, Any]:
    """Validate and describe every structural byte in the supported profile."""
    fail(len(data) >= 64, "file is too small for an IMAGE_DOS_HEADER")
    fail(data[:2] == b"MZ", "missing DOS MZ signature")
    pe_offset = unpack_from("<I", data, 0x3C, "DOS e_lfanew")[0]
    fail(pe_offset >= 64 and pe_offset % 4 == 0, "invalid DOS e_lfanew")
    fail(pe_offset <= len(data) - 24, "PE header is outside the file")
    fail(data[pe_offset : pe_offset + 4] == b"PE\0\0", "missing PE signature")

    coff_offset = pe_offset + 4
    (
        machine,
        section_count,
        timestamp,
        symbol_table_offset,
        symbol_count,
        optional_size,
        characteristics,
    ) = unpack_from("<HHIIIHH", data, coff_offset, "COFF header")
    fail(machine == 0x014C, "only Intel 386 PE32 payloads are supported")
    fail(1 <= section_count <= 96, "invalid COFF section count")
    fail(symbol_table_offset == 0 and symbol_count == 0, "COFF symbol tables are unsupported")
    fail(characteristics & 0x0002 != 0, "PE image is not executable")
    fail(characteristics & 0x0100 != 0, "PE image is not marked 32-bit")

    optional_offset = coff_offset + 20
    optional_end = optional_offset + optional_size
    fail(optional_size >= 96, "truncated PE32 optional header")
    fail(optional_end <= len(data), "optional header extends beyond the file")
    magic = unpack_from("<H", data, optional_offset, "optional-header magic")[0]
    fail(magic == 0x010B, "only PE32 optional headers are supported")

    entry_point = unpack_from("<I", data, optional_offset + 16, "entry point")[0]
    image_base = unpack_from("<I", data, optional_offset + 28, "image base")[0]
    section_alignment = unpack_from("<I", data, optional_offset + 32, "section alignment")[0]
    file_alignment = unpack_from("<I", data, optional_offset + 36, "file alignment")[0]
    size_of_image = unpack_from("<I", data, optional_offset + 56, "SizeOfImage")[0]
    size_of_headers = unpack_from("<I", data, optional_offset + 60, "SizeOfHeaders")[0]
    checksum_offset = optional_offset + 64
    stored_checksum = unpack_from("<I", data, checksum_offset, "PE checksum")[0]
    subsystem = unpack_from("<H", data, optional_offset + 68, "subsystem")[0]
    directory_count = unpack_from("<I", data, optional_offset + 92, "directory count")[0]

    fail(is_power_of_two(file_alignment) and 512 <= file_alignment <= 65536,
         "invalid file alignment for this profile")
    fail(is_power_of_two(section_alignment) and section_alignment >= file_alignment,
         "invalid section alignment")
    fail(size_of_headers % file_alignment == 0, "SizeOfHeaders is not file-aligned")
    fail(size_of_headers <= len(data), "SizeOfHeaders extends beyond the file")
    fail(directory_count >= 16, "the standard 16 PE data directories are required")
    fail(96 + directory_count * 8 <= optional_size, "data-directory array is truncated")

    directories: list[dict[str, Any]] = []
    directory_offset = optional_offset + 96
    for index in range(directory_count):
        address, size = unpack_from(
            "<II", data, directory_offset + index * 8, f"data directory {index}"
        )
        directories.append(
            {
                "index": index,
                "name": DIRECTORY_NAMES[index] if index < len(DIRECTORY_NAMES) else f"extra_{index}",
                "address": address,
                "size": size,
            }
        )
    fail(directories[15]["address"] == 0 and directories[15]["size"] == 0,
         "reserved data directory is nonzero")

    section_table_offset = optional_end
    section_table_end = section_table_offset + section_count * 40
    fail(section_table_end <= size_of_headers, "section table is outside SizeOfHeaders")
    sections: list[dict[str, Any]] = []
    for index in range(section_count):
        offset = section_table_offset + index * 40
        raw_name = data[offset : offset + 8]
        fail(len(raw_name) == 8, f"truncated section header {index}")
        name_bytes = raw_name.split(b"\0", 1)[0]
        fail(name_bytes and all(0x20 <= byte <= 0x7E for byte in name_bytes),
             f"invalid section name at index {index}")
        name = name_bytes.decode("ascii")
        (
            virtual_size,
            virtual_address,
            raw_size,
            raw_offset,
            relocation_offset,
            line_number_offset,
            relocation_count,
            line_number_count,
            section_characteristics,
        ) = unpack_from("<IIIIIIHHI", data, offset + 8, f"section header {index}")
        fail(relocation_offset == 0 and line_number_offset == 0 and
             relocation_count == 0 and line_number_count == 0,
             f"section {name!r} contains unsupported object-file tables")
        fail(virtual_address % section_alignment == 0,
             f"section {name!r} virtual address is not aligned")
        if raw_size:
            fail(raw_offset >= size_of_headers and raw_offset % file_alignment == 0,
                 f"section {name!r} raw offset is invalid")
            fail(raw_size % file_alignment == 0,
                 f"section {name!r} raw size is not aligned")
            fail(raw_offset <= len(data) - raw_size,
                 f"section {name!r} extends beyond the file")
        sections.append(
            {
                "index": index,
                "name": name,
                "virtual_size": virtual_size,
                "virtual_address": virtual_address,
                "raw_size": raw_size,
                "raw_offset": raw_offset,
                "characteristics": section_characteristics,
                "sha256": sha256_hex(data[raw_offset : raw_offset + raw_size]),
            }
        )

    virtual_ranges = sorted(
        (
            section["virtual_address"],
            align_up(section["virtual_address"] + max(section["virtual_size"], section["raw_size"]),
                     section_alignment),
            section["name"],
        )
        for section in sections
        if section["virtual_size"] or section["raw_size"]
    )
    prior_end = 0
    for start, end, name in virtual_ranges:
        fail(start >= prior_end, f"overlapping virtual section {name!r}")
        prior_end = end
    expected_image_size = align_up(max(end for _, end, _ in virtual_ranges), section_alignment)
    fail(size_of_image == expected_image_size, "SizeOfImage does not match the section map")

    raw_ranges = sorted(
        (section["raw_offset"], section["raw_offset"] + section["raw_size"], section["name"])
        for section in sections
        if section["raw_size"]
    )
    cursor = size_of_headers
    for start, end, name in raw_ranges:
        fail(start == cursor, f"unaccounted gap or overlap before section {name!r}")
        cursor = end

    def rva_to_offset(rva: int, size: int, what: str) -> int:
        fail(size >= 0 and rva <= 0xFFFFFFFF - size, f"overflow in {what}")
        if rva < size_of_headers and rva + size <= size_of_headers:
            return rva
        matches = []
        for section in sections:
            start = section["virtual_address"]
            raw_size = section["raw_size"]
            if start <= rva and rva + size <= start + raw_size:
                matches.append(section["raw_offset"] + rva - start)
        fail(len(matches) == 1, f"{what} is not uniquely backed by file bytes")
        return matches[0]

    for directory in directories:
        if directory["index"] == 4 or directory["size"] == 0:
            fail((directory["address"] == 0) == (directory["size"] == 0),
                 f"partially empty {directory['name']} directory")
            continue
        directory["file_offset"] = rva_to_offset(
            directory["address"], directory["size"], f"{directory['name']} directory"
        )

    fail(entry_point != 0, "executable has no entry point")
    rva_to_offset(entry_point, 1, "entry point")
    fail(stored_checksum != 0, "a stored PE checksum is required")
    calculated_checksum = pe_checksum(data, checksum_offset)
    fail(stored_checksum == calculated_checksum, "PE checksum mismatch")

    security = directories[4]
    certificate_offset = security["address"]
    certificate_size = security["size"]
    fail(certificate_offset != 0 and certificate_size != 0,
         "a terminal Authenticode certificate table is required")
    fail(certificate_offset % 8 == 0, "certificate table is not 8-byte aligned")
    fail(certificate_offset == cursor, "section bytes do not end at the certificate table")
    fail(certificate_offset + certificate_size == len(data),
         "certificate table is not terminal (overlay or truncation present)")

    certificates: list[dict[str, Any]] = []
    cert_cursor = certificate_offset
    certificate_end = certificate_offset + certificate_size
    while cert_cursor < certificate_end:
        length, revision, certificate_type = unpack_from(
            "<IHH", data, cert_cursor, "WIN_CERTIFICATE header"
        )
        fail(length >= 8 and length <= certificate_end - cert_cursor,
             "invalid WIN_CERTIFICATE length")
        fail(revision == 0x0200, "unsupported WIN_CERTIFICATE revision")
        fail(certificate_type == 0x0002, "certificate is not PKCS#7 SignedData")
        blob = data[cert_cursor + 8 : cert_cursor + length]
        fail(blob[:1] == b"\x30", "PKCS#7 payload is not a DER SEQUENCE")
        der_size = der_object_length(blob)
        fail(all(byte == 0 for byte in blob[der_size:]),
             "nonzero bytes follow the PKCS#7 DER object")
        padded_length = align_up(length, 8)
        fail(cert_cursor + padded_length <= certificate_end,
             "WIN_CERTIFICATE padding extends beyond its table")
        fail(all(byte == 0 for byte in data[cert_cursor + length : cert_cursor + padded_length]),
             "nonzero WIN_CERTIFICATE alignment padding")
        certificates.append(
            {
                "file_offset": cert_cursor,
                "length": length,
                "revision": revision,
                "certificate_type": certificate_type,
                "der_size": der_size,
                "sha256": sha256_hex(blob[:der_size]),
            }
        )
        cert_cursor += padded_length
    fail(cert_cursor == certificate_end and certificates,
         "certificate records do not exactly fill the security directory")

    resource = directories[2]
    fail(resource["address"] != 0 and resource["size"] >= 16,
         "a PE resource tree is required")
    resource_base_rva = resource["address"]
    resource_base_offset = rva_to_offset(resource_base_rva, resource["size"], "resource tree")
    resource_size = resource["size"]
    visited_directories: set[int] = set()
    resources: list[dict[str, Any]] = []

    def resource_identifier(value: int, what: str) -> str | int:
        if value & 0x80000000 == 0:
            return value
        relative = value & 0x7FFFFFFF
        fail(relative <= resource_size - 2, f"{what} string offset is outside resource tree")
        length = unpack_from("<H", data, resource_base_offset + relative, f"{what} string length")[0]
        byte_length = length * 2
        fail(relative + 2 + byte_length <= resource_size, f"truncated {what} string")
        raw = data[resource_base_offset + relative + 2 :
                   resource_base_offset + relative + 2 + byte_length]
        try:
            text = raw.decode("utf-16le", errors="strict")
        except UnicodeDecodeError as error:
            raise FormatError(f"invalid UTF-16LE {what} string") from error
        fail(text != "" and "\x00" not in text, f"invalid empty or NUL-containing {what} string")
        return text

    def walk_resources(relative: int, path: list[str | int]) -> None:
        fail(len(path) <= 2, "resource tree is deeper than type/name/language")
        fail(relative not in visited_directories, "cyclic or multiply referenced resource directory")
        fail(relative <= resource_size - 16, "resource directory is outside resource tree")
        visited_directories.add(relative)
        offset = resource_base_offset + relative
        characteristics_r, timestamp_r, major, minor, named_count, id_count = unpack_from(
            "<IIHHHH", data, offset, "resource directory header"
        )
        entry_count = named_count + id_count
        fail(entry_count <= 65535 and relative + 16 + entry_count * 8 <= resource_size,
             "resource directory entries are truncated")
        entries: list[tuple[str | int, int]] = []
        for index in range(entry_count):
            name_value, target = unpack_from(
                "<II", data, offset + 16 + index * 8, "resource directory entry"
            )
            identifier = resource_identifier(name_value, "resource identifier")
            if index < named_count:
                fail(isinstance(identifier, str), "numeric resource is in the named-entry range")
            else:
                fail(isinstance(identifier, int), "named resource is in the ID-entry range")
            entries.append((identifier, target))
        fail(len({str(type(item)).encode() + str(item).encode() for item, _ in entries}) == len(entries),
             "duplicate resource identifier")

        for identifier, target in entries:
            new_path = path + [identifier]
            if target & 0x80000000:
                fail(len(new_path) < 3, "language-level resource entry points to a directory")
                walk_resources(target & 0x7FFFFFFF, new_path)
            else:
                fail(len(new_path) == 3, "resource data appears before the language level")
                data_relative = target
                fail(data_relative <= resource_size - 16,
                     "resource data entry is outside resource tree")
                data_rva, data_size, code_page, reserved = unpack_from(
                    "<IIII", data, resource_base_offset + data_relative, "resource data entry"
                )
                fail(reserved == 0, "resource data entry reserved field is nonzero")
                file_offset = rva_to_offset(data_rva, data_size, "resource payload")
                type_id = new_path[0]
                resources.append(
                    {
                        "type": type_id,
                        "type_name": RESOURCE_TYPE_NAMES.get(type_id) if isinstance(type_id, int) else None,
                        "name": new_path[1],
                        "language": new_path[2],
                        "data_rva": data_rva,
                        "file_offset": file_offset,
                        "size": data_size,
                        "code_page": code_page,
                        "sha256": sha256_hex(data[file_offset : file_offset + data_size]),
                    }
                )

    walk_resources(0, [])
    fail(resources, "resource tree contains no payloads")

    return {
        "format": "ACCAStore raw signed-PE32 payload profile",
        "source_name": source_name,
        "file_size": len(data),
        "sha256": sha256_hex(data),
        "byte_coverage": {
            "headers": [0, size_of_headers],
            "sections": [size_of_headers, cursor],
            "certificate_table": [certificate_offset, certificate_end],
            "unaccounted_bytes": 0,
        },
        "pe": {
            "pe_header_offset": pe_offset,
            "machine": machine,
            "section_count": section_count,
            "timestamp": timestamp,
            "characteristics": characteristics,
            "optional_header_size": optional_size,
            "entry_point_rva": entry_point,
            "image_base": image_base,
            "section_alignment": section_alignment,
            "file_alignment": file_alignment,
            "size_of_image": size_of_image,
            "size_of_headers": size_of_headers,
            "subsystem": subsystem,
            "stored_checksum": stored_checksum,
            "calculated_checksum": calculated_checksum,
        },
        "data_directories": directories,
        "sections": sections,
        "certificates": certificates,
        "resource_count": len(resources),
        "resources": resources,
    }


def atomic_write(path: Path, content: bytes, mode: int) -> None:
    """Write content beside its destination, then atomically replace it."""
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary_path, mode)
        os.replace(temporary_path, path)
    except BaseException:
        try:
            temporary_path.unlink(missing_ok=True)
        finally:
            raise


def extract(input_path: Path, output_dir: Path, include_metadata: bool) -> list[Path]:
    fail(input_path.is_file(), "input path is not a regular file")
    data = input_path.read_bytes()

    # All parsing and optional metadata serialization happen before outputDir is
    # created, which guarantees malformed input has no output-side effects.
    metadata = validate_payload(data, input_path.name)
    metadata_bytes = None
    if include_metadata:
        metadata_bytes = (json.dumps(metadata, indent=2, ensure_ascii=False) + "\n").encode("utf-8")

    fail(output_dir.exists() is False or output_dir.is_dir(), "output path exists but is not a directory")
    output_dir.mkdir(parents=True, exist_ok=True, mode=0o775)
    try:
        os.chmod(output_dir, os.stat(output_dir).st_mode | 0o050)
    except OSError:
        pass

    output_path = output_dir / input_path.name
    atomic_write(output_path, data, 0o664)
    written = [output_path]
    if metadata_bytes is not None:
        metadata_path = output_dir / f"{input_path.name}.accastore.json"
        atomic_write(metadata_path, metadata_bytes, 0o664)
        written.append(metadata_path)
    return written


def parse_arguments(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract one validated ACCAStore raw signed-PE32 payload."
    )
    parser.add_argument("--all", action="store_true", help="also write structural JSON metadata")
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputDir", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    arguments = parse_arguments(sys.argv[1:] if argv is None else argv)
    try:
        written = extract(arguments.inputFile, arguments.outputDir, arguments.all)
    except (FormatError, OSError) as error:
        print(f"accaStore.py: {error}", file=sys.stderr)
        return 1
    for path in written:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

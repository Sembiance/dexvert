#!/usr/bin/env python3
# Vibe coded by Codex
"""Extract files from classic DeployMaster 2.5 through 2.8 installers."""

from __future__ import annotations

import argparse
import bz2
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import struct
import sys
import tempfile
import zlib


class FormatError(Exception):
    """Raised when an input fails a structural or integrity check."""


def need(condition: bool, message: str) -> None:
    if not condition:
        raise FormatError(message)


def u16(data: bytes, offset: int) -> int:
    need(0 <= offset <= len(data) - 2, "truncated 16-bit field")
    return struct.unpack_from("<H", data, offset)[0]


def u32(data: bytes, offset: int) -> int:
    need(0 <= offset <= len(data) - 4, "truncated 32-bit field")
    return struct.unpack_from("<I", data, offset)[0]


def i32(data: bytes, offset: int) -> int:
    need(0 <= offset <= len(data) - 4, "truncated signed 32-bit field")
    return struct.unpack_from("<i", data, offset)[0]


def pe_layout(data: bytes, label: str) -> dict:
    need(len(data) >= 0x40 and data[:2] == b"MZ", f"{label}: missing DOS MZ header")
    pe = u32(data, 0x3C)
    need(pe <= len(data) - 24 and data[pe:pe + 4] == b"PE\0\0", f"{label}: missing PE signature")
    machine, section_count, _, _, _, opt_size, _ = struct.unpack_from("<HHIIIHH", data, pe + 4)
    need(machine == 0x14C, f"{label}: only i386 PE containers are supported")
    opt = pe + 24
    need(opt + opt_size <= len(data) and opt_size >= 96, f"{label}: invalid optional header")
    need(u16(data, opt) == 0x10B, f"{label}: only PE32 containers are supported")
    file_alignment = u32(data, opt + 36)
    need(file_alignment and not (file_alignment & (file_alignment - 1)), f"{label}: invalid file alignment")
    directory_count = u32(data, opt + 92)
    sections = opt + opt_size
    need(section_count and sections + 40 * section_count <= len(data), f"{label}: truncated section table")
    raw_ranges = []
    image_end = 0
    rsrc = None
    for index in range(section_count):
        entry = sections + index * 40
        name = data[entry:entry + 8].rstrip(b"\0")
        raw_size, raw_offset = struct.unpack_from("<II", data, entry + 16)
        if raw_size:
            need(raw_offset % file_alignment == 0, f"{label}: misaligned section")
            need(raw_offset <= len(data) - raw_size, f"{label}: section outside file")
            raw_ranges.append((raw_offset, raw_offset + raw_size))
            image_end = max(image_end, raw_offset + raw_size)
        if name == b".rsrc":
            rsrc = (raw_offset, raw_size, u32(data, entry + 12))
    ordered = sorted(raw_ranges)
    need(all(a[1] <= b[0] for a, b in zip(ordered, ordered[1:])), f"{label}: overlapping sections")
    need(rsrc is not None, f"{label}: PE resource section is required")
    cert_offset = cert_size = 0
    if directory_count > 4 and opt_size >= 96 + 8 * 5:
        cert_offset, cert_size = struct.unpack_from("<II", data, opt + 96 + 8 * 4)
        if cert_size:
            need(cert_offset >= image_end and cert_offset <= len(data) - cert_size,
                 f"{label}: invalid certificate directory")
            need(cert_offset % 8 == 0, f"{label}: unaligned certificate directory")
    return {
        "pe_offset": pe,
        "image_end": image_end,
        "resource": rsrc,
        "certificate_offset": cert_offset,
        "certificate_size": cert_size,
    }


def resource_leaf(data: bytes, layout: dict, wanted_type: int) -> bytes:
    raw, raw_size, rva = layout["resource"]

    def directory(relative: int) -> list[tuple[int, bool, int]]:
        base = raw + relative
        need(raw <= base <= raw + raw_size - 16, "invalid PE resource directory")
        named, ids = struct.unpack_from("<HH", data, base + 12)
        count = named + ids
        need(base + 16 + count * 8 <= raw + raw_size, "truncated PE resource directory")
        result = []
        for n in range(count):
            name, target = struct.unpack_from("<II", data, base + 16 + n * 8)
            if not (name & 0x80000000):
                result.append((name, bool(target & 0x80000000), target & 0x7FFFFFFF))
        return result

    type_entries = [x for x in directory(0) if x[0] == wanted_type and x[1]]
    need(len(type_entries) == 1, "missing or duplicate PE version resource")
    level = type_entries[0][2]
    for _ in range(2):
        entries = directory(level)
        need(entries, "empty PE version resource directory")
        chosen = entries[0]
        if _ == 0:
            need(chosen[1], "malformed PE version resource tree")
            level = chosen[2]
        else:
            need(not chosen[1], "malformed PE version resource leaf")
            leaf = raw + chosen[2]
            need(raw <= leaf <= raw + raw_size - 16, "invalid PE resource data entry")
            payload_rva, size = struct.unpack_from("<II", data, leaf)
            payload = raw + (payload_rva - rva)
            need(raw <= payload <= raw + raw_size and size <= raw + raw_size - payload,
                 "version resource outside .rsrc")
            return data[payload:payload + size]
    raise AssertionError


def deploymaster_version(data: bytes, layout: dict) -> tuple[int, int, int, int]:
    version = resource_leaf(data, layout, 16)
    signature = b"\xbd\x04\xef\xfe"
    at = version.find(signature)
    need(at >= 0 and version.find(signature, at + 1) < 0, "invalid VS_FIXEDFILEINFO")
    need(at <= len(version) - 16, "truncated VS_FIXEDFILEINFO")
    ms, ls = struct.unpack_from("<II", version, at + 8)
    value = (ms >> 16, ms & 0xFFFF, ls >> 16, ls & 0xFFFF)
    need((2, 5, 3, 0) <= value <= (2, 8, 0, 0),
         f"unsupported DeployMaster version {'.'.join(map(str, value))}")
    return value


def parse_certificates(data: bytes, offset: int, size: int) -> list[dict]:
    if not size:
        return []
    end = offset + size
    records = []
    while offset < end:
        if not any(data[offset:end]):
            records.append({"length": end - offset, "revision": 0, "type": 0, "padding": True})
            offset = end
            break
        remaining = end - offset
        if remaining == 320 and data[offset:offset + 5] == b"\0\0\0\0\x02":
            name_length = data[offset + 5]
            need(name_length <= 31 and not any(data[offset + 6 + name_length:end]),
                 "invalid DeployMaster certificate auxiliary block")
            name = data[offset + 6:offset + 6 + name_length].decode("ascii", "strict")
            records.append({"length": 320, "revision": 0, "type": 0,
                            "deploymaster_auxiliary": name})
            offset = end
            break
        need(offset <= end - 8, "truncated WIN_CERTIFICATE")
        length, revision, cert_type = struct.unpack_from("<IHH", data, offset)
        need(length >= 8 and offset <= end - length, "invalid WIN_CERTIFICATE length")
        need(revision in (0x0100, 0x0200), "unsupported WIN_CERTIFICATE revision")
        records.append({"length": length, "revision": revision, "type": cert_type})
        aligned = (length + 7) & ~7
        need(offset <= end - aligned, "WIN_CERTIFICATE alignment exceeds directory")
        need(not any(data[offset + length:offset + aligned]), "nonzero WIN_CERTIFICATE padding")
        offset += aligned
    need(offset == end, "certificate directory length mismatch")
    return records


def compressed_record(data: bytes, offset: int, limit: int, label: str) -> tuple[bytes, int, int]:
    need(offset <= limit - 4, f"{label}: missing compressed length")
    length = u32(data, offset)
    start = offset + 4
    need(length >= 8 and start <= limit - length, f"{label}: invalid compressed length")
    decoder = zlib.decompressobj()
    try:
        output = decoder.decompress(data[start:start + length])
        output += decoder.flush()
    except zlib.error as exc:
        raise FormatError(f"{label}: invalid zlib stream: {exc}") from None
    need(decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail,
         f"{label}: zlib stream does not exactly fill its record")
    return output, start + length, length


def decode_text(value: bytes) -> str:
    return value.decode("cp1252", "strict")


def safe_component(value: str) -> str:
    value = value.replace("\\", "/")
    parts = [p for p in value.split("/") if p not in ("", ".")]
    need(parts and all(p != ".." and "\0" not in p for p in parts), "unsafe output path")
    return "/".join(parts)


def action_path(data: bytes, offset: int, limit: int) -> tuple[list[str], int] | None:
    """Decode a destination descriptor, returning None at the action-list sentinel."""
    start = offset
    while offset < limit and data[offset] == 0xFF:
        # One or more 0xFF bytes walk back toward the destination-tree root. A
        # following zlib length starts the next metadata section instead.
        if offset + 5 <= limit:
            length = u32(data, offset + 1)
            if length == 0 or (length >= 8 and offset + 5 + length <= limit and data[offset + 5] == 0x78):
                return None
        offset += 1
    pieces = []
    while offset < limit:
        length = data[offset]
        offset += 1
        if length == 0xFE:
            return pieces, offset
        need(length < 0xFE and offset <= limit - length, "invalid destination descriptor")
        raw = data[offset:offset + length]
        offset += length
        text = decode_text(raw)
        need("\0" not in text and "\\" not in text and "/" not in text,
             "invalid destination component")
        pieces.append(text)
    if offset == start:
        return None
    raise FormatError("unterminated destination descriptor")


def normalized_destination(parts: list[str]) -> str:
    if not parts:
        return "%APPFOLDER%"
    if not parts[0].startswith("%"):
        parts = ["%APPFOLDER%"] + parts
    return "/".join(parts)


def parse_installer(path: Path) -> dict:
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise FormatError(str(exc)) from None
    layout = pe_layout(data, "outer executable")
    version = deploymaster_version(data, layout)
    overlay = layout["image_end"]
    need(data[overlay:overlay + 3] == b"BZh", "DeployMaster engine bzip2 stream is absent")
    bz = bz2.BZ2Decompressor()
    try:
        engine = bz.decompress(data[overlay:])
    except OSError as exc:
        raise FormatError(f"invalid engine bzip2 stream: {exc}") from None
    need(bz.eof, "truncated engine bzip2 stream")
    engine_used = len(data) - overlay - len(bz.unused_data)
    engine_layout = pe_layout(engine, "embedded installer engine")
    need(engine_layout["image_end"] == len(engine), "embedded installer engine has unexplained trailing data")
    pos = overlay + engine_used
    cert_offset = layout["certificate_offset"] or len(data)
    need(pos < cert_offset, "missing DeployMaster package")
    need(u32(data, pos) == 0xFFFFFFFF, "invalid DeployMaster package marker")
    pos += 4
    language, pos, language_stored = compressed_record(data, pos, cert_offset, "language table")
    need(language.endswith(b"\r\n"), "malformed language table")
    project, pos, project_stored = compressed_record(data, pos, cert_offset, "project record")
    fields = project.split(b"\x0c")
    need(len(fields) in (15, 18), "unsupported project record field count")
    need(all(not field or b"\0" not in field[:-1] for field in fields), "NUL inside project string")

    identity_records = []
    tail_flag = fields[-1][-1] if fields[-1] else 0
    if tail_flag & 1:
        for label in ("identity registry test", "identity validation expression"):
            value, pos, stored = compressed_record(data, pos, cert_offset, label)
            identity_records.append({"label": label, "size": len(value), "stored_size": stored})
        need(u32(data, pos) == 0, "invalid identity record terminator")
        pos += 4

    need(pos <= cert_offset - 67, "missing project authentication block")
    authentication = data[pos:pos + 67]
    pos += 67
    need(any(authentication), "invalid project authentication block")

    if version[:2] >= (2, 7):
        need(pos <= cert_offset - 43, "truncated 2.7+ appearance header")
        appearance_header = data[pos:pos + 43]
        font_length = appearance_header[3]
        need(font_length <= 31 and not any(appearance_header[4 + font_length:35]),
             "invalid installer font short string")
        pos += 43
    else:
        need(pos <= cert_offset - 4, "truncated appearance header")
        appearance_header = data[pos:pos + 4]
        pos += 4
    has_appearance_record = bool(appearance_header[-1])
    appearance = None
    if has_appearance_record:
        appearance, pos, _ = compressed_record(data, pos, cert_offset, "appearance settings")

    resource_fields = [7, 8, 9]
    if len(fields) == 18:
        resource_fields.append(14)
    resource_fields.append(10)
    resources = []
    for field_index in resource_fields:
        if field_index < len(fields) and fields[field_index] not in (b"", b"\0"):
            payload, pos, stored = compressed_record(data, pos, cert_offset, f"project resource {field_index}")
            resources.append({
                "field": field_index,
                "name": decode_text(fields[field_index].rstrip(b"\0")),
                "data": payload,
                "stored_size": stored,
            })

    need(pos < cert_offset, "missing component table")
    component_count = data[pos]
    pos += 1
    components = []
    for index in range(component_count):
        component, pos, stored = compressed_record(data, pos, cert_offset, f"component {index}")
        need(component, "empty component record")
        components.append({"data": component, "stored_size": stored})

    file_list, pos, file_list_stored = compressed_record(data, pos, cert_offset, "file name list")
    need(file_list.endswith(b"\r\n") and b"\0" not in file_list, "malformed file name list")
    raw_names = file_list[:-2].split(b"\r\n") if file_list != b"\r\n" else []
    need(raw_names and all(raw_names), "empty file name in list")
    names = [decode_text(name) for name in raw_names]
    need(all("/" not in n and "\\" not in n and n not in (".", "..") and "\0" not in n for n in names),
         "unsafe file name")

    count = len(resources) + len(names)
    table_start = pos
    need(count <= (cert_offset - pos) // 24, "truncated file table")
    offsets = [i32(data, pos + 4 * n) for n in range(count)]
    pos += 4 * count
    timestamps = [u32(data, pos + 4 * n) for n in range(count)]
    pos += 4 * count
    versions = [struct.unpack_from("<q", data, pos + 8 * n)[0] for n in range(count)]
    pos += 8 * count
    sizes = [u32(data, pos + 4 * n) for n in range(count)]
    pos += 4 * count
    crcs = [u32(data, pos + 4 * n) for n in range(count)]
    pos += 4 * count

    resource_count = len(resources)
    need(all(value == -1 for value in offsets[:resource_count]), "project resource offset must be -1")
    for index, resource in enumerate(resources):
        need(len(resource["data"]) == sizes[index], "project resource size mismatch")
        need(zlib.crc32(resource["data"]) == crcs[index], "project resource CRC-32 mismatch")

    file_offsets = offsets[resource_count:]
    need(all(value >= pos for value in file_offsets), "file payload points inside metadata")
    need(file_offsets == sorted(file_offsets), "file payload offsets are not ordered")
    payload_start = min(file_offsets)
    files = []
    record_ends = []
    for index, (name, offset) in enumerate(zip(names, file_offsets)):
        payload, end, stored = compressed_record(data, offset, cert_offset, f"file payload {index}")
        table_index = resource_count + index
        need(len(payload) == sizes[table_index], f"size mismatch for {name}")
        need(zlib.crc32(payload) == crcs[table_index], f"CRC-32 mismatch for {name}")
        files.append({
            "name": name,
            "data": payload,
            "offset": offset,
            "stored_size": stored,
            "timestamp": timestamps[table_index],
            "version": versions[table_index],
            "crc32": crcs[table_index],
        })
        record_ends.append(end)
    need(all(a <= b for a, b in zip(record_ends, file_offsets[1:])), "overlapping file payload records")
    for end, following in zip(record_ends, file_offsets[1:]):
        need(end == following, "unexplained bytes between file payload records")
    package_end = record_ends[-1]
    need(package_end <= cert_offset, "file payload crosses certificate directory")
    trailing_package = data[package_end:cert_offset]
    if any(trailing_package):
        need(version[:2] == (2, 7) and not layout["certificate_size"] and len(trailing_package) == 260,
             "nonzero bytes after package payload")
        legacy_signature = trailing_package
    else:
        legacy_signature = b""

    # Decode the leading destination/action records. Their internal file IDs are
    # stable but sparse; ascending IDs correspond to file-table order. Files not
    # present in these records are DeployMaster-generated files and default to
    # %APPFOLDER%.
    action_pos = pos
    assignments: dict[int, str] = {}
    action_records = []
    while action_pos < payload_start:
        try:
            descriptor = action_path(data, action_pos, payload_start)
        except (FormatError, UnicodeDecodeError):
            break
        if descriptor is None:
            break
        path_parts, after_path = descriptor
        payload, after_record, stored = compressed_record(data, after_path, payload_start, "destination action")
        action_record = {
            "path": normalized_destination(path_parts),
            "size": len(payload),
            "stored_size": stored,
        }
        action_records.append(action_record)
        if len(payload) % 3 == 0 and payload and all(payload[n] >= 0x80 for n in range(0, len(payload), 3)):
            action_record["file_ids"] = [u16(payload, n + 1) for n in range(0, len(payload), 3)]
            for n in range(0, len(payload), 3):
                item_id = u16(payload, n + 1)
                assignments.setdefault(item_id, normalized_destination(path_parts))
        action_pos = after_record

    ordered_ids = sorted(assignments)
    if len(ordered_ids) > len(files):
        # Generated support/uninstall items can have action IDs without entries
        # in the installable-file table.  They sort after table-backed IDs.
        ordered_ids = ordered_ids[:len(files)]
    for index, file in enumerate(files):
        file["destination"] = assignments[ordered_ids[index]] if index < len(ordered_ids) else "%APPFOLDER%"
        file["internal_id"] = ordered_ids[index] if index < len(ordered_ids) else None

    # The remaining installer-action area is retained and bounded exactly by the
    # first table-declared payload offset. It contains registry, association,
    # shortcut, and uninstall directives rather than installable file bytes.
    action_tail = data[action_pos:payload_start]
    need(len(action_tail) == payload_start - action_pos, "installer action block accounting failure")

    certificates = parse_certificates(data, layout["certificate_offset"], layout["certificate_size"])
    return {
        "input": str(path),
        "input_size": len(data),
        "version": ".".join(map(str, version)),
        "pe_image_size": overlay,
        "engine_stored_size": engine_used,
        "engine_size": len(engine),
        "language_size": len(language),
        "language_stored_size": language_stored,
        "project_size": len(project),
        "project_stored_size": project_stored,
        "project_fields": [decode_text(x.rstrip(b"\0")) for x in fields],
        "authentication_hex": authentication.hex(),
        "appearance_header_hex": appearance_header.hex(),
        "appearance_size": len(appearance) if appearance is not None else 0,
        "identity_records": identity_records,
        "components": components,
        "resources": resources,
        "file_list_stored_size": file_list_stored,
        "file_table_offset": table_start,
        "installer_action_offset": pos,
        "installer_action_size": payload_start - pos,
        "parsed_action_records": action_records,
        "unparsed_action_tail_size": len(action_tail),
        "unparsed_action_tail_hex": action_tail.hex(),
        "package_end": package_end,
        "legacy_signature_size": len(legacy_signature),
        "certificate_records": certificates,
        "files": files,
    }


def unique_output_paths(files: list[dict]) -> list[str]:
    used: dict[str, int] = {}
    result = []
    for file in files:
        base = safe_component(file["destination"] + "/" + file["name"])
        folded = base.casefold()
        ordinal = used.get(folded, 0)
        used[folded] = ordinal + 1
        if ordinal:
            path = PurePosixPath(base)
            base = str(path.with_name(f"{path.stem}.deploymaster-{ordinal + 1}{path.suffix}"))
        result.append(base)
    return result


def public_metadata(parsed: dict, output_paths: list[str]) -> dict:
    return {
        key: value for key, value in parsed.items()
        if key not in ("files", "resources", "components")
    } | {
        "components": [
            {"size": len(x["data"]), "stored_size": x["stored_size"], "hex": x["data"].hex()}
            for x in parsed["components"]
        ],
        "resources": [
            {k: v for k, v in x.items() if k != "data"} |
            {"size": len(x["data"]), "crc32": f"{zlib.crc32(x['data']):08x}"}
            for x in parsed["resources"]
        ],
        "files": [
            {k: v for k, v in x.items() if k != "data"} |
            {"size": len(x["data"]), "crc32": f"{x['crc32']:08x}", "output": output}
            for x, output in zip(parsed["files"], output_paths)
        ],
    }


def extract(parsed: dict, output_dir: Path, include_all: bool) -> list[str]:
    output_paths = unique_output_paths(parsed["files"])
    parent = output_dir.resolve().parent
    parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".deployMaster-", dir=parent))
    try:
        for file, relative in zip(parsed["files"], output_paths):
            target = stage / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(file["data"])
            target.chmod(0o664)
        if include_all:
            metadata_dir = stage / "_deploymaster"
            resource_dir = metadata_dir / "resources"
            resource_dir.mkdir(parents=True, exist_ok=True)
            for index, resource in enumerate(parsed["resources"]):
                target = resource_dir / f"{index:02d}-{safe_component(resource['name'])}"
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(resource["data"])
                target.chmod(0o664)
            metadata = metadata_dir / "metadata.json"
            metadata.write_text(json.dumps(public_metadata(parsed, output_paths), indent=2, ensure_ascii=False) + "\n",
                                encoding="utf-8")
            metadata.chmod(0o664)
        for directory, _, _ in os.walk(stage):
            Path(directory).chmod(0o775)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_dir.chmod(output_dir.stat().st_mode | 0o070)
        for child in stage.iterdir():
            destination = output_dir / child.name
            if child.is_dir():
                destination.mkdir(parents=True, exist_ok=True)
                shutil.copytree(child, destination, dirs_exist_ok=True, copy_function=shutil.copy2)
            else:
                shutil.copy2(child, destination)
        for directory, _, filenames in os.walk(output_dir):
            Path(directory).chmod(Path(directory).stat().st_mode | 0o070)
            for filename in filenames:
                item = Path(directory) / filename
                item.chmod(item.stat().st_mode | 0o060)
    finally:
        shutil.rmtree(stage, ignore_errors=True)
    return output_paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract classic DeployMaster installer files")
    parser.add_argument("--all", action="store_true", help="also emit project resources and metadata JSON")
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputDir", type=Path)
    args = parser.parse_args(argv)
    try:
        parsed = parse_installer(args.inputFile)
        outputs = extract(parsed, args.outputDir, args.all)
    except FormatError as exc:
        print(f"deployMaster.py: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"deployMaster.py: {exc}", file=sys.stderr)
        return 1
    print(f"Extracted {len(outputs)} files from DeployMaster {parsed['version']} into {args.outputDir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

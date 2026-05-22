#!/usr/bin/env python3
# Vibe coded by Codex
"""Lossless extractor/reporter for observed Asymetrix ToolBook .TBK samples."""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import os
import re
import shutil
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable


TBK_MAGIC = b"\x03JBO"
SUPPORTED_MEDIA = ("bmp", "riff", "jpeg", "gif", "zip")
ASCII_RE = re.compile(rb"[\x09\x0a\x0d\x20-\x7e]{5,}")
TOOLBOOK_DIB_RECORD_TYPES = {
    b"\x07\x01",
    b"\x07\x04",
    b"\x0f\x01",
    b"\x0f\x04",
}
RUNTIME_OBJECT_CLASS_NAMES = {
    1: "Book",
    4: "Background",
    5: "Page",
    8: "Rectangle",
    9: "Button",
    10: "Field",
    11: "Group",
    12: "Ellipse",
    13: "RoundedRectangle",
    14: "Line",
    15: "Polygon",
    16: "IrregularPolygon",
    17: "Arc",
    18: "Pie",
    19: "AngledLine",
    20: "Curve",
    21: "PaintObject",
    22: "RecordField",
    23: "Hotword",
    24: "Hotword",
    25: "Picture",
    27: "MultipleSelection",
}


class ToolBookError(Exception):
    """Raised when an input is not an observed ToolBook container."""


@dataclass(frozen=True)
class MediaHit:
    kind: str
    offset: int
    size: int
    extension: str
    description: str

    @property
    def end(self) -> int:
        return self.offset + self.size


@dataclass(frozen=True)
class ExtractionResult:
    input_path: str
    output_dir: str
    status: str
    reason: str
    input_size: int
    wrapper_kind: str
    tbk_offset: int
    tbk_size: int
    version_hex: str
    sha256: str
    files_written: int
    media_counts: dict[str, int]
    probable_objects: int = 0
    handlers: int = 0
    references: int = 0
    text_blocks: int = 0
    typed_text_values: int = 0
    typed_text_values_with_native_object_owner: int = 0
    typed_text_values_with_native_storage_prefix: int = 0
    typed_text_capacity_tail_values: int = 0
    typed_text_capacity_tail_bytes: int = 0
    typed_text_capacity_tail_nonzero_bytes: int = 0
    typed_text_capacity_tail_text_values: int = 0
    large_text_values: int = 0
    field_hotword_run_tables: int = 0
    field_hotword_run_table_rows: int = 0
    field_hotword_run_table_active_rows: int = 0
    field_hotword_run_table_linked_rows: int = 0
    field_hotword_run_table_bytes: int = 0
    page_background_offset_vectors: int = 0
    page_background_offset_vector_bytes: int = 0
    page_background_offset_vector_offsets: int = 0
    page_background_offset_vector_nonzero_offsets: int = 0
    page_background_payloads: int = 0
    page_background_payload_segments: int = 0
    page_background_payload_segment_bytes: int = 0
    page_background_bounded_payload_fragments: int = 0
    page_background_bounded_payload_fragment_bytes: int = 0
    book_payload_segments: int = 0
    book_payload_segment_bytes: int = 0
    book_common_native_headers: int = 0
    book_common_native_header_bytes: int = 0
    book_openscript_record_links: int = 0
    book_openscript_record_link_bytes: int = 0
    book_reference_blocks: int = 0
    book_control_descriptors: int = 0
    book_control_descriptor_bytes: int = 0
    book_pointer_target_name_prefixes: int = 0
    book_pointer_target_name_prefix_bytes: int = 0
    book_pointer_target_leading_descriptors: int = 0
    book_pointer_target_leading_descriptor_bytes: int = 0
    book_named_payload_reference_inline_prefixes: int = 0
    book_named_payload_reference_inline_prefix_bytes: int = 0
    book_palette_entries: int = 0
    book_pointer_tables: int = 0
    book_pointer_table_entries: int = 0
    book_pointer_table_bytes: int = 0
    book_pointer_table_reference_words: int = 0
    book_pointer_table_reference_bytes: int = 0
    book_pre_pointer_descriptor_blocks: int = 0
    book_pre_pointer_descriptor_bytes: int = 0
    book_compact_named_descriptors: int = 0
    book_compact_named_descriptor_bytes: int = 0
    book_pre_pointer_count_descriptors: int = 0
    book_pre_pointer_count_descriptor_bytes: int = 0
    book_compact_descriptor_payload_fragments: int = 0
    book_compact_descriptor_payload_fragment_bytes: int = 0
    book_named_payload_reference_descriptors: int = 0
    book_named_payload_reference_descriptor_bytes: int = 0
    book_openscript_objects: int = 0
    book_openscript_object_bytes: int = 0
    book_openscript_code_bytes: int = 0
    book_openscript_auxiliary_prefixes: int = 0
    book_openscript_auxiliary_prefix_bytes: int = 0
    book_openscript_duplicate_tails: int = 0
    book_openscript_duplicate_tail_bytes: int = 0
    book_pointer_target_payload_fragments: int = 0
    book_pointer_target_payload_fragment_bytes: int = 0
    book_named_payload_reference_payload_fragments: int = 0
    book_named_payload_reference_payload_fragment_bytes: int = 0
    book_zero_reserved_gaps: int = 0
    book_zero_reserved_gap_bytes: int = 0
    embedded_native_text_objects: int = 0
    self_reference_offset_tables: int = 0
    self_reference_offset_table_entries: int = 0
    self_reference_offset_table_nonzero_entries: int = 0
    self_reference_offset_table_linked_text_objects: int = 0
    self_reference_child_object_headers: int = 0
    self_reference_child_object_header_bytes: int = 0
    self_reference_child_object_spans: int = 0
    self_reference_child_object_span_bytes: int = 0
    self_reference_final_child_object_spans: int = 0
    self_reference_final_child_object_span_bytes: int = 0
    self_reference_offset_table_bytes: int = 0
    reconstructed_images: int = 0
    native_property_stream_images: int = 0
    native_nested_dib_images: int = 0
    native_class41_icons: int = 0
    native_class41_icon_descriptors_unhandled: int = 0
    embedded_media: int = 0
    unhandled_bitmap_descriptors: int = 0
    toolbook_backed_bitmap_descriptors: int = 0
    toolbook_bitmap_info_descriptors: int = 0
    toolbook_bitmap_info_container_descriptors: int = 0
    toolbook_bitmap_info_native_payload_descriptors: int = 0
    native_record_nested_dib_container_descriptors: int = 0
    native_record_native_payload_descriptors: int = 0
    nested_dib_container_extracted_descriptors: int = 0
    nested_dib_chain_crosses_metadata_descriptors: int = 0
    nested_dib_chain_spans_records_descriptors: int = 0
    nested_dib_chain_property_metadata_descriptors: int = 0
    nested_dib_chain_property_nested_descriptors: int = 0
    nested_dib_chain_property_unmatched_descriptors: int = 0
    nested_dib_chain_invalid_descriptors: int = 0
    toolbook_property_stream_dib_descriptors: int = 0
    toolbook_property_stream_metadata_descriptors: int = 0
    toolbook_property_stream_nested_descriptors: int = 0
    toolbook_property_stream_container_nested_descriptors: int = 0
    toolbook_property_stream_unmatched_descriptors: int = 0
    toolbook_property_stream_unmatched_nested_descriptors: int = 0
    toolbook_compressed_dib_descriptors: int = 0
    unproven_dib_like_descriptors: int = 0
    native_record_bitmap_descriptors: int = 0
    nested_dib_bitmap_descriptors: int = 0
    nested_native_header_bitmap_descriptors: int = 0
    unsupported_bitmap_record_type_descriptors: int = 0
    native_property_stream_bitmap_descriptors: int = 0
    missing_envelope_bitmap_descriptors: int = 0
    invalid_bitmap_descriptors: int = 0
    suppressed_bitmap_descriptors: int = 0
    external_refs: int = 0
    native_index_status: str = ""
    native_index_reason: str = ""
    native_records: int = 0
    native_index_pages: int = 0
    active_record_bytes: int = 0
    active_record_coverage_percent: float = 0.0
    inactive_payload_bytes: int = 0


@dataclass(frozen=True)
class ToolBookHeader:
    signature_hex: str
    format_word0_hex: str
    format_word1_hex: str
    format_id_hex: str
    fixed_header_size: int
    runtime_probe_size: int
    first_native_offset: int
    family: str


@dataclass(frozen=True)
class NativeSegment:
    name: str
    role: str
    offset: int
    size: int
    description: str

    @property
    def end(self) -> int:
        return self.offset + self.size


@dataclass(frozen=True)
class DibHit:
    offset: int
    dib_size: int
    pixel_offset: int
    width: int
    height: int
    bits_per_pixel: int
    compression: int
    file_size: int

    @property
    def end(self) -> int:
        return self.offset + self.dib_size


@dataclass(frozen=True)
class DibCandidate:
    offset: int
    header_size: int
    width: int
    height: int
    bits_per_pixel: int
    compression: int
    pixel_offset: int
    expected_end: int
    reject_reason: str


@dataclass(frozen=True)
class NativeIconHit:
    offset: int
    size: int
    stored_size: int
    padding_size: int
    width: int
    height: int
    bits_per_pixel: int
    record_number: int
    record_offset: int
    local_offset: int

    @property
    def end(self) -> int:
        return self.offset + self.size


@dataclass(frozen=True)
class NativePropertyDibHit:
    offset: int
    dib_info_end: int
    pixel_source_offset: int
    pixel_size: int
    width: int
    height: int
    bits_per_pixel: int
    compression: int
    property_offset: int
    property_value_offset: int
    physical_width_twips: int
    physical_height_twips: int
    descriptor_pointer_offset: int
    descriptor_pointer_value: int
    record_number: int
    record_offset: int
    local_offset: int

    @property
    def end(self) -> int:
        return self.pixel_source_offset + self.pixel_size


@dataclass(frozen=True)
class NativeNestedDibHit:
    parent_offset: int
    parent_width: int
    parent_height: int
    chain_depth: int
    record_number: int
    record_offset: int
    local_offset: int
    dib: DibHit


@dataclass(frozen=True)
class NativePropertyStreamMetadata:
    property_offset: int
    property_value_offset: int
    physical_width_twips: int
    physical_height_twips: int
    match_kind: str
    record_number: int
    record_offset: int
    local_offset: int
    nested_dib_offset: int | None


@dataclass(frozen=True)
class NativeIndexEntry:
    entry_offset: int
    payload_offset: int
    absolute_offset: int
    length: int
    end: int
    flags: int
    unit: int
    handle: int
    extra0: int
    extra1: int | None
    page_size: int
    depth: int


@dataclass(frozen=True)
class NativeIndexPage:
    offset: int
    size: int
    depth: int

    @property
    def end(self) -> int:
        return self.offset + self.size


@dataclass(frozen=True)
class NativeIndex:
    status: str
    reason: str
    descriptor_offset: int
    descriptor_size: int
    descriptor_flags: int
    root_block_offset: int
    root_block_end: int
    record_size: int
    index_root_offset: int
    declared_record_count: int
    index_flags: int
    pages: list[NativeIndexPage]
    records: list[NativeIndexEntry]
    bad_entries: list[dict[str, object]]
    payload_offset: int
    payload_size: int
    pointer_base: int
    pointer_base_kind: str

    @property
    def supported(self) -> bool:
        return self.status == "ok"

    @property
    def record_ranges(self) -> list[tuple[int, int]]:
        return [(record.absolute_offset, record.end) for record in self.records]

    @property
    def metadata_ranges(self) -> list[tuple[int, int]]:
        ranges = [
            (self.payload_offset, min(self.payload_offset + 0x116, self.payload_offset + self.payload_size)),
            *[(page.offset, page.end) for page in self.pages],
        ]
        if self.root_block_offset and self.root_block_end > self.root_block_offset:
            ranges.append((self.root_block_offset, self.root_block_end))
        if self.root_block_end and self.record_size:
            tail_end = self.root_block_end + self.record_size
            if tail_end <= self.payload_offset + self.payload_size:
                ranges.append((self.root_block_end, tail_end))
        return ranges

    @property
    def active_ranges(self) -> list[tuple[int, int]]:
        return merge_ranges(self.metadata_ranges + self.record_ranges)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def chmod_group_readable(path: Path) -> None:
    if path.is_dir():
        path.chmod(0o775)
    else:
        path.chmod(0o664)


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    chmod_group_readable(path)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    chmod_group_readable(path)


def write_json(path: Path, obj: object) -> None:
    write_text(path, json.dumps(obj, indent=2, sort_keys=True) + "\n")


def parse_pe_end(data: bytes) -> int | None:
    if len(data) < 0x40 or data[:2] != b"MZ":
        return None
    pe_off = struct.unpack_from("<I", data, 0x3C)[0]
    if pe_off + 24 > len(data) or data[pe_off : pe_off + 4] != b"PE\0\0":
        return None
    machine, section_count, _timestamp, _symptr, _symcnt, opt_size, _chars = struct.unpack_from(
        "<HHIIIHH", data, pe_off + 4
    )
    if machine not in (0x014C, 0x8664):
        return None
    section_table = pe_off + 24 + opt_size
    if section_table + section_count * 40 > len(data):
        return None
    raw_end = 0
    for idx in range(section_count):
        off = section_table + idx * 40
        raw_size = struct.unpack_from("<I", data, off + 16)[0]
        raw_ptr = struct.unpack_from("<I", data, off + 20)[0]
        if raw_size:
            raw_end = max(raw_end, raw_ptr + raw_size)
    return raw_end if raw_end <= len(data) else None


def locate_tbk_payload(data: bytes) -> tuple[int, str]:
    if data.startswith(TBK_MAGIC):
        return 0, "plain_tbk"
    pe_end = parse_pe_end(data)
    if pe_end is not None:
        found = data.find(TBK_MAGIC)
        if found >= 0:
            # Observed ToolBook application files append/embed a normal TBK stream
            # after the Windows launcher/resources. The PE parser is used only to
            # establish that the wrapper is real before accepting the inner stream.
            return found, "pe_wrapped_tbk"
    raise ToolBookError("missing ToolBook magic at start or inside a valid PE wrapper")


def validate_tbk_payload(payload: bytes) -> None:
    if len(payload) < 0x100:
        raise ToolBookError("ToolBook payload is shorter than the fixed header area")
    if not payload.startswith(TBK_MAGIC):
        raise ToolBookError("ToolBook payload does not start with 03 4A 42 4F")
    version = payload[4:8]
    if version == b"\0\0\0\0":
        raise ToolBookError("ToolBook version/signature word is zero")
    head_words = [struct.unpack_from("<I", payload, off)[0] for off in range(0x18, min(0x100, len(payload)), 4)]
    if all(word == 0 for word in head_words):
        raise ToolBookError("ToolBook fixed header has no descriptor words")


def parse_toolbook_header(payload: bytes) -> ToolBookHeader:
    validate_tbk_payload(payload)
    word0, word1 = struct.unpack_from("<HH", payload, 4)
    format_id = payload[4:8]
    if format_id in (b"\x72\x13\x42\x1c", b"\x71\x13\x42\x1c"):
        family = "runtime_toolbook_1_x"
    elif word0 == 1:
        family = f"toolbook_generation_{word1 >> 8}"
    else:
        family = "observed_toolbook"
    return ToolBookHeader(
        signature_hex=payload[:4].hex(),
        format_word0_hex=f"0x{word0:04x}",
        format_word1_hex=f"0x{word1:04x}",
        format_id_hex=format_id.hex(),
        fixed_header_size=0x100,
        runtime_probe_size=0x116,
        first_native_offset=0x100,
        family=family,
    )


def parse_native_index(data: bytes, tbk_offset: int, payload: bytes) -> NativeIndex:
    descriptor_offset = tbk_offset + 0x100
    if len(payload) < 0x116:
        return NativeIndex(
            status="unsupported",
            reason="ToolBook payload is shorter than the native index descriptor prefix",
            descriptor_offset=descriptor_offset,
            descriptor_size=0,
            descriptor_flags=0,
            root_block_offset=0,
            root_block_end=0,
            record_size=0,
            index_root_offset=0,
            declared_record_count=0,
            index_flags=0,
            pages=[],
            records=[],
            bad_entries=[],
            payload_offset=tbk_offset,
            payload_size=len(payload),
            pointer_base=tbk_offset,
            pointer_base_kind="payload_relative",
        )

    descriptor_size = struct.unpack_from("<H", payload, 0x100)[0]
    descriptor_flags = struct.unpack_from("<H", payload, 0x102)[0]
    root_payload_offset = struct.unpack_from("<I", payload, 0x104)[0]
    root_end_payload_offset = struct.unpack_from("<I", payload, 0x108)[0]
    record_size = struct.unpack_from("<H", payload, 0x10C)[0]
    index_payload_offset = struct.unpack_from("<I", payload, 0x10E)[0]
    declared_record_count = struct.unpack_from("<H", payload, 0x112)[0]
    index_flags = struct.unpack_from("<H", payload, 0x114)[0]

    def make_index(
        status: str,
        reason: str,
        pointer_base: int,
        pointer_base_kind: str,
        pages: list[NativeIndexPage] | None = None,
        records: list[NativeIndexEntry] | None = None,
        bad_entries: list[dict[str, object]] | None = None,
    ) -> NativeIndex:
        root_block_offset = pointer_base + root_payload_offset if root_payload_offset else 0
        root_block_end = pointer_base + root_end_payload_offset if root_end_payload_offset else 0
        index_root_offset = pointer_base + index_payload_offset if index_payload_offset else 0
        return NativeIndex(
            status=status,
            reason=reason,
            descriptor_offset=descriptor_offset,
            descriptor_size=descriptor_size,
            descriptor_flags=descriptor_flags,
            root_block_offset=root_block_offset,
            root_block_end=root_block_end,
            record_size=record_size,
            index_root_offset=index_root_offset,
            declared_record_count=declared_record_count,
            index_flags=index_flags,
            pages=pages or [],
            records=records or [],
            bad_entries=bad_entries or [],
            payload_offset=tbk_offset,
            payload_size=len(payload),
            pointer_base=pointer_base,
            pointer_base_kind=pointer_base_kind,
        )

    payload_end = tbk_offset + len(payload)
    if not declared_record_count:
        return make_index("unsupported", "native index declares zero records", tbk_offset, "payload_relative")

    def decode_with_pointer_base(pointer_base: int, pointer_base_kind: str) -> NativeIndex:
        root_block_offset = pointer_base + root_payload_offset if root_payload_offset else 0
        root_block_end = pointer_base + root_end_payload_offset if root_end_payload_offset else 0
        index_root_offset = pointer_base + index_payload_offset if index_payload_offset else 0
        pages: list[NativeIndexPage] = []
        records: list[NativeIndexEntry] = []
        bad_entries: list[dict[str, object]] = []

        if index_root_offset < tbk_offset + 0x116 or index_root_offset + 0x140 > payload_end:
            return make_index(
                "unsupported",
                "native index root page is outside the ToolBook payload",
                pointer_base,
                pointer_base_kind,
            )

        stack: list[tuple[int, int, int]] = [(index_root_offset, 0x140, 0)]
        seen_pages: set[int] = set()
        while stack:
            page_offset, page_size, depth = stack.pop()
            if page_offset in seen_pages:
                continue
            seen_pages.add(page_offset)
            if (
                page_size not in (0x140, 0x180)
                or page_offset < tbk_offset + 0x116
                or page_offset + page_size > payload_end
            ):
                bad_entries.append(
                    {
                        "entry_offset": page_offset,
                        "reason": "page_outside_payload",
                        "page_size": page_size,
                        "depth": depth,
                    }
                )
                continue

            pages.append(NativeIndexPage(page_offset, page_size, depth))
            entry_size = 20 if page_size == 0x140 else 24
            entry_format = "<IIHHHHI" if page_size == 0x140 else "<IIHHHHII"
            for entry_index in range(16):
                entry_offset = page_offset + entry_index * entry_size
                values = struct.unpack_from(entry_format, data, entry_offset)
                ptr_payload, alternate_ptr, flags, unit, length, handle, *extra = values
                if ptr_payload == 0:
                    continue
                absolute_offset = pointer_base + ptr_payload
                if unit == 6 and (flags & 0x0004) and length in (0x140, 0x180):
                    if tbk_offset + 0x116 <= absolute_offset and absolute_offset + length <= payload_end:
                        stack.append((absolute_offset, length, depth + 1))
                    else:
                        bad_entries.append(
                            {
                                "entry_offset": entry_offset,
                                "reason": "child_page_outside_payload",
                                "payload_offset": ptr_payload,
                                "length": length,
                                "flags": flags,
                                "unit": unit,
                            }
                        )
                    continue
                if length and tbk_offset + 0x116 <= absolute_offset and absolute_offset + length <= payload_end:
                    records.append(
                        NativeIndexEntry(
                            entry_offset=entry_offset,
                            payload_offset=ptr_payload,
                            absolute_offset=absolute_offset,
                            length=length,
                            end=absolute_offset + length,
                            flags=flags,
                            unit=unit,
                            handle=handle,
                            extra0=extra[0] if extra else 0,
                            extra1=extra[1] if len(extra) > 1 else None,
                            page_size=page_size,
                            depth=depth,
                        )
                    )
                else:
                    bad_entries.append(
                        {
                            "entry_offset": entry_offset,
                            "reason": "record_outside_payload_or_zero_length",
                            "payload_offset": ptr_payload,
                            "length": length,
                            "flags": flags,
                            "unit": unit,
                            "handle": handle,
                            "extra": extra,
                        }
                    )

        missing_records = declared_record_count - len(records)
        if bad_entries:
            return make_index(
                "unsupported",
                f"native index has {len(bad_entries)} entries that do not resolve cleanly",
                pointer_base,
                pointer_base_kind,
                pages,
                records,
                bad_entries,
            )
        if not pages:
            return make_index(
                "unsupported",
                "native index root did not resolve to a page",
                pointer_base,
                pointer_base_kind,
                pages,
                records,
                bad_entries,
            )
        if not records:
            return make_index(
                "unsupported",
                "native index resolved no active records",
                pointer_base,
                pointer_base_kind,
                pages,
                records,
                bad_entries,
            )
        if missing_records < 0:
            return make_index(
                "unsupported",
                (
                    f"native index resolves {len(records)} active records, "
                    f"more than declared count {declared_record_count}"
                ),
                pointer_base,
                pointer_base_kind,
                pages,
                records,
                bad_entries,
            )
        if missing_records > 1:
            return make_index(
                "unsupported",
                (
                    f"native index resolves {len(records)} active records, "
                    f"fewer than declared count {declared_record_count}"
                ),
                pointer_base,
                pointer_base_kind,
                pages,
                records,
                bad_entries,
            )

        reason = (
            "native index record count matches descriptor"
            if missing_records == 0
            else "native index has one empty/deleted slot"
        )
        if root_block_offset >= payload_end or root_block_end > payload_end:
            reason += "; root/native control block pointer is outside payload"
        return make_index(
            "ok",
            reason,
            pointer_base,
            pointer_base_kind,
            pages,
            sorted(records, key=lambda record: (record.absolute_offset, record.length)),
            bad_entries,
        )

    candidates = [decode_with_pointer_base(tbk_offset, "payload_relative")]
    if tbk_offset:
        candidates.append(decode_with_pointer_base(0, "file_absolute"))
    supported = [candidate for candidate in candidates if candidate.supported]
    if supported:
        exact = [
            candidate
            for candidate in supported
            if len(candidate.records) == candidate.declared_record_count
        ]
        return (exact or supported)[0]
    return candidates[-1] if tbk_offset else candidates[0]


def native_index_to_json(native_index: NativeIndex) -> dict[str, object]:
    active_ranges = native_index.active_ranges
    active_bytes = range_total(active_ranges)
    return {
        "status": native_index.status,
        "reason": native_index.reason,
        "descriptor": {
            "offset": native_index.descriptor_offset,
            "size": native_index.descriptor_size,
            "flags": native_index.descriptor_flags,
            "root_block_offset": native_index.root_block_offset,
            "root_block_end": native_index.root_block_end,
            "record_size": native_index.record_size,
            "index_root_offset": native_index.index_root_offset,
            "declared_record_count": native_index.declared_record_count,
            "index_flags": native_index.index_flags,
            "pointer_base": native_index.pointer_base,
            "pointer_base_kind": native_index.pointer_base_kind,
        },
        "counts": {
            "pages": len(native_index.pages),
            "records": len(native_index.records),
            "bad_entries": len(native_index.bad_entries),
            "active_bytes": active_bytes,
            "inactive_payload_bytes": max(0, native_index.payload_size - active_bytes),
            "active_payload_percent": active_bytes / max(1, native_index.payload_size) * 100.0,
        },
        "pages": [
            {"offset": page.offset, "size": page.size, "end": page.end, "depth": page.depth}
            for page in native_index.pages
        ],
        "records": [
            {
                "entry_offset": record.entry_offset,
                "payload_offset": record.payload_offset,
                "offset": record.absolute_offset,
                "size": record.length,
                "end": record.end,
                "flags": record.flags,
                "unit": record.unit,
                "handle": record.handle,
                "extra0": record.extra0,
                "extra1": record.extra1,
                "page_size": record.page_size,
                "depth": record.depth,
            }
            for record in native_index.records
        ],
        "bad_entries": native_index.bad_entries,
    }


def valid_bmp(data: bytes, offset: int) -> MediaHit | None:
    if offset + 54 > len(data) or data[offset : offset + 2] != b"BM":
        return None
    size = struct.unpack_from("<I", data, offset + 2)[0]
    pixel_offset = struct.unpack_from("<I", data, offset + 10)[0]
    dib_size = struct.unpack_from("<I", data, offset + 14)[0]
    if dib_size not in (12, 16, 40, 52, 56, 64, 108, 124):
        return None
    if size < 14 + dib_size or pixel_offset < 14 + dib_size or offset + size > len(data):
        return None
    return MediaHit("bmp", offset, size, "bmp", "Windows bitmap")


def valid_riff(data: bytes, offset: int) -> MediaHit | None:
    if offset + 12 > len(data) or data[offset : offset + 4] != b"RIFF":
        return None
    form = data[offset + 8 : offset + 12]
    ext_by_form = {b"WAVE": "wav", b"AVI ": "avi", b"RMID": "rmi"}
    if form not in ext_by_form:
        return None
    size = struct.unpack_from("<I", data, offset + 4)[0] + 8
    if size < 12 or offset + size > len(data):
        return None
    return MediaHit("riff", offset, size, ext_by_form[form], f"RIFF/{form.decode('ascii', 'replace').strip()}")


def valid_jpeg(data: bytes, offset: int) -> MediaHit | None:
    if offset + 4 > len(data) or data[offset : offset + 3] != b"\xff\xd8\xff":
        return None
    pos = offset + 2
    saw_scan = False
    while pos + 4 <= len(data):
        if data[pos] != 0xFF:
            if not saw_scan:
                return None
            end = data.find(b"\xff\xd9", pos)
            if end == -1:
                return None
            size = end + 2 - offset
            return MediaHit("jpeg", offset, size, "jpg", "JPEG image") if size >= 20 else None
        while pos < len(data) and data[pos] == 0xFF:
            pos += 1
        if pos >= len(data):
            return None
        marker = data[pos]
        pos += 1
        if marker == 0xD9:
            size = pos - offset
            return MediaHit("jpeg", offset, size, "jpg", "JPEG image") if size >= 20 else None
        if marker == 0xDA:
            saw_scan = True
        if marker == 0x01 or 0xD0 <= marker <= 0xD7:
            continue
        if pos + 2 > len(data):
            return None
        segment_size = struct.unpack_from(">H", data, pos)[0]
        if segment_size < 2:
            return None
        pos += segment_size
        if saw_scan:
            end = data.find(b"\xff\xd9", pos)
            if end == -1:
                return None
            size = end + 2 - offset
            return MediaHit("jpeg", offset, size, "jpg", "JPEG image") if size >= 20 else None
    return None


def valid_gif(data: bytes, offset: int) -> MediaHit | None:
    if offset + 13 > len(data) or data[offset : offset + 6] not in (b"GIF87a", b"GIF89a"):
        return None
    packed = data[offset + 10]
    pos = offset + 13
    if packed & 0x80:
        pos += 3 * (2 ** ((packed & 0x07) + 1))
    if pos > len(data):
        return None
    while pos < len(data):
        introducer = data[pos]
        pos += 1
        if introducer == 0x3B:
            return MediaHit("gif", offset, pos - offset, "gif", "GIF image")
        if introducer == 0x2C:
            if pos + 9 > len(data):
                return None
            image_packed = data[pos + 8]
            pos += 9
            if image_packed & 0x80:
                pos += 3 * (2 ** ((image_packed & 0x07) + 1))
            if pos >= len(data):
                return None
            pos += 1
        elif introducer == 0x21:
            if pos >= len(data):
                return None
            pos += 1
        else:
            return None
        while True:
            if pos >= len(data):
                return None
            block_size = data[pos]
            pos += 1
            if block_size == 0:
                break
            pos += block_size
            if pos > len(data):
                return None
    return None


def valid_zip(data: bytes, offset: int) -> MediaHit | None:
    if data[offset : offset + 4] != b"PK\x03\x04":
        return None
    search_end = min(len(data), offset + 200 * 1024 * 1024)
    eocd = data.find(b"PK\x05\x06", offset, search_end)
    if eocd == -1 or eocd + 22 > len(data):
        return None
    comment_len = struct.unpack_from("<H", data, eocd + 20)[0]
    end = eocd + 22 + comment_len
    if end > len(data):
        return None
    return MediaHit("zip", offset, end - offset, "zip", "ZIP archive")


def valid_dib(data: bytes, offset: int) -> DibHit | None:
    if offset + 12 > len(data):
        return None
    header_size = struct.unpack_from("<I", data, offset)[0]
    if header_size not in (12, 40, 52, 56, 108, 124):
        return None
    if offset + header_size > len(data):
        return None

    if header_size == 12:
        width, height, planes, bpp = struct.unpack_from("<HHHH", data, offset + 4)
        compression = 0
        size_image = 0
        clr_used = 0
        palette_entry_size = 3
    else:
        width, height_signed, planes, bpp, compression, size_image = struct.unpack_from(
            "<iiHHII", data, offset + 4
        )
        height = abs(height_signed)
        clr_used = struct.unpack_from("<I", data, offset + 32)[0]
        palette_entry_size = 4

    if width <= 0 or height <= 0 or width > 10000 or height > 10000:
        return None
    if width == 1 and height == 1:
        return None
    if planes != 1 or bpp not in (1, 4, 8, 16, 24, 32):
        return None
    if compression not in (0, 1, 2, 3):
        return None

    colors = clr_used if clr_used else ((1 << bpp) if bpp <= 8 else 0)
    if colors > 256:
        return None
    palette_size = colors * palette_entry_size
    pixel_offset = header_size + palette_size
    if compression == 0:
        row_bytes = ((width * bpp + 31) // 32) * 4
        pixel_size = row_bytes * height
    else:
        pixel_size = size_image
    if pixel_size <= 0:
        return None
    dib_size = pixel_offset + pixel_size
    if offset + dib_size > len(data):
        return None
    if not has_contiguous_dib_pixels(data, offset, pixel_offset, dib_size):
        return None

    return DibHit(
        offset=offset,
        dib_size=dib_size,
        pixel_offset=pixel_offset,
        width=width,
        height=height,
        bits_per_pixel=bpp,
        compression=compression,
        file_size=14 + dib_size,
    )


def parse_dib_candidate(data: bytes, offset: int) -> DibCandidate | None:
    if offset + 12 > len(data):
        return None
    header_size = struct.unpack_from("<I", data, offset)[0]
    if header_size not in (12, 40, 52, 56, 108, 124):
        return None
    if offset + header_size > len(data):
        return None
    if header_size == 12:
        width, height, planes, bpp = struct.unpack_from("<HHHH", data, offset + 4)
        compression = 0
        size_image = 0
        clr_used = 0
        palette_entry_size = 3
    else:
        width, height_signed, planes, bpp, compression, size_image = struct.unpack_from(
            "<iiHHII", data, offset + 4
        )
        height = abs(height_signed)
        clr_used = struct.unpack_from("<I", data, offset + 32)[0]
        palette_entry_size = 4
    if width <= 0 or height <= 0 or width > 10000 or height > 10000:
        return None
    if planes != 1 or bpp not in (1, 4, 8, 16, 24, 32):
        return None
    if compression not in (0, 1, 2, 3):
        return None
    colors = clr_used if clr_used else ((1 << bpp) if bpp <= 8 else 0)
    if colors > 256:
        return None
    pixel_offset = header_size + colors * palette_entry_size
    if compression == 0:
        pixel_size = ((width * bpp + 31) // 32) * 4 * height
    else:
        pixel_size = size_image
    if pixel_size <= 0:
        return None
    expected_end = offset + pixel_offset + pixel_size
    reject_reason = classify_rejected_dib(data, offset, pixel_offset, expected_end, width, height)
    return DibCandidate(
        offset=offset,
        header_size=header_size,
        width=width,
        height=height,
        bits_per_pixel=bpp,
        compression=compression,
        pixel_offset=offset + pixel_offset,
        expected_end=expected_end,
        reject_reason=reject_reason,
    )


def valid_dib_header_only(data: bytes, offset: int) -> bool:
    if offset + 40 > len(data):
        return False
    header_size = struct.unpack_from("<I", data, offset)[0]
    if header_size not in (12, 40, 52, 56, 108, 124) or offset + header_size > len(data):
        return False
    if header_size == 12:
        width, height, planes, bpp = struct.unpack_from("<HHHH", data, offset + 4)
        compression = 0
        clr_used = 0
        palette_entry_size = 3
    else:
        width, height_signed, planes, bpp, compression = struct.unpack_from("<iiHHI", data, offset + 4)
        height = abs(height_signed)
        clr_used = struct.unpack_from("<I", data, offset + 32)[0]
        palette_entry_size = 4
    if width <= 0 or height <= 0 or width > 10000 or height > 10000:
        return False
    if planes != 1 or bpp not in (1, 4, 8, 16, 24, 32) or compression not in (0, 1, 2, 3):
        return False
    colors = clr_used if clr_used else ((1 << bpp) if bpp <= 8 else 0)
    return colors <= 256 and offset + header_size + colors * palette_entry_size <= len(data)


def has_contiguous_dib_pixels(data: bytes, offset: int, pixel_offset: int, dib_size: int) -> bool:
    return classify_rejected_dib(
        data,
        offset,
        pixel_offset,
        offset + dib_size,
        None,
        None,
    ) == ""


def classify_rejected_dib(
    data: bytes,
    offset: int,
    pixel_offset: int,
    pixel_end: int,
    width: int | None,
    height: int | None,
) -> str:
    if width == 1 and height == 1:
        return "suppressed_1x1_candidate"
    record_type = toolbook_bitmap_record_type(data, offset)
    if record_type and record_type not in TOOLBOOK_DIB_RECORD_TYPES:
        return f"unsupported_native_bitmap_record_type_{record_type.hex()}"
    pixel_start = offset + pixel_offset
    if pixel_start >= pixel_end or pixel_end > len(data):
        return "pixel_range_outside_file"
    if b"PHYSSIZE" in data[pixel_start : min(len(data), pixel_start + 64)]:
        return "native_property_stream_at_pixel_start"

    # Some ToolBook native image descriptors contain a BITMAPINFOHEADER for
    # dimensions/color tables, but the following bytes are more object records,
    # not the bitmap bits. Reject those descriptor headers unless the pixel bytes
    # are actually contiguous after the DIB header/palette.
    if pixel_start + 12 <= len(data):
        record_kind = struct.unpack_from("<H", data, pixel_start + 2)[0]
        record_count_or_size = struct.unpack_from("<I", data, pixel_start + 4)[0]
        descriptor_word = struct.unpack_from("<H", data, pixel_start + 8)[0]
        if 0x0001 <= record_kind <= 0x001F and record_count_or_size <= 0x1000 and descriptor_word == 0x0014:
            return "native_record_at_pixel_start"

    search_end = min(pixel_end, pixel_start + 4096)
    nested = data.find(b"\x28\x00\x00\x00", pixel_start, search_end)
    while nested >= 0:
        if valid_dib_header_only(data, nested):
            return "nested_dib_header_in_pixel_range"
        nested = data.find(b"\x28\x00\x00\x00", nested + 1, search_end)
    return ""


def toolbook_bitmap_record_type(data: bytes, offset: int) -> bytes | None:
    marker = data.rfind(b"\xff\xff\xff\x00\x01\x00\x00", max(0, offset - 120), offset)
    if marker < 0 or marker + 9 > offset:
        return None
    if marker + 18 > len(data) or data[marker + 9 : marker + 13] != b"\x00\x00\xfe\x00":
        return None
    return data[marker + 7 : marker + 9]


def first_nested_dib_header_offset(data: bytes, candidate: DibCandidate) -> int | None:
    search_end = min(candidate.expected_end, candidate.pixel_offset + 4096, len(data))
    nested = data.find(b"\x28\x00\x00\x00", candidate.pixel_offset, search_end)
    while nested >= 0:
        if valid_dib_header_only(data, nested):
            return nested
        nested = data.find(b"\x28\x00\x00\x00", nested + 1, search_end)
    return None


def toolbook_compressed_dib_payload_end(
    data: bytes,
    native_index: NativeIndex | None,
    candidate: DibCandidate,
) -> int | None:
    if native_index is None or candidate.reject_reason != "nested_dib_header_in_pixel_range":
        return None
    owner = native_record_for_offset(native_index, candidate.offset)
    if owner is None or candidate.pixel_offset + 4 > len(data):
        return None
    _record_number, entry = owner
    nested = first_nested_dib_header_offset(data, candidate)
    if nested is None or nested > entry.end:
        return None
    dword_value = struct.unpack_from("<I", data, candidate.pixel_offset)[0]
    dword_end = entry.absolute_offset + dword_value
    if candidate.pixel_offset < dword_end < nested:
        return dword_end
    return None


def native_property_stream_metadata(
    data: bytes,
    native_index: NativeIndex | None,
    candidate: DibCandidate,
) -> NativePropertyStreamMetadata | None:
    if native_index is None or candidate.reject_reason != "native_property_stream_at_pixel_start":
        return None
    owner = native_record_for_offset(native_index, candidate.offset)
    if owner is None:
        return None
    record_number, entry = owner
    nested_dib_offset = first_nested_dib_header_offset(data, candidate)
    if nested_dib_offset is not None and nested_dib_offset >= entry.end:
        nested_dib_offset = None
    expected_width_twips = candidate.width * 15
    expected_height_twips = candidate.height * 15
    search_end = min(entry.end, candidate.pixel_offset + 1024)
    property_marker = data.find(b":PHYSSIZE\0", candidate.pixel_offset, search_end)
    while property_marker >= 0:
        direct_value_size_offset = property_marker + len(b":PHYSSIZE\0") + 4
        if direct_value_size_offset + 6 <= entry.end:
            value_size = struct.unpack_from("<H", data, direct_value_size_offset)[0]
            physical_width_twips, physical_height_twips = struct.unpack_from(
                "<HH", data, direct_value_size_offset + 2
            )
            if (
                value_size == 4
                and physical_width_twips == expected_width_twips
                and physical_height_twips == expected_height_twips
            ):
                return NativePropertyStreamMetadata(
                    property_offset=property_marker,
                    property_value_offset=direct_value_size_offset + 2,
                    physical_width_twips=physical_width_twips,
                    physical_height_twips=physical_height_twips,
                    match_kind="direct_physsize_value",
                    record_number=record_number,
                    record_offset=entry.absolute_offset,
                    local_offset=candidate.offset - entry.absolute_offset,
                    nested_dib_offset=nested_dib_offset,
                )

        compound_end = min(entry.end, property_marker + 128)
        next_property = data.find(b":PHYSSIZE\0", property_marker + 1, compound_end)
        if next_property >= 0:
            compound_end = next_property
        value_pattern = struct.pack("<HHH", 4, expected_width_twips, expected_height_twips)
        delayed_value_size_offset = data.find(value_pattern, property_marker + len(b":PHYSSIZE\0"), compound_end)
        if delayed_value_size_offset >= 0:
            return NativePropertyStreamMetadata(
                property_offset=property_marker,
                property_value_offset=delayed_value_size_offset + 2,
                physical_width_twips=expected_width_twips,
                physical_height_twips=expected_height_twips,
                match_kind="compound_physsize_value",
                record_number=record_number,
                record_offset=entry.absolute_offset,
                local_offset=candidate.offset - entry.absolute_offset,
                nested_dib_offset=nested_dib_offset,
            )
        property_marker = data.find(b":PHYSSIZE\0", property_marker + 1, search_end)
    return None


def native_property_stream_has_unmatched_physsize(
    data: bytes,
    native_index: NativeIndex | None,
    candidate: DibCandidate,
) -> bool:
    if native_index is None or candidate.reject_reason != "native_property_stream_at_pixel_start":
        return False
    owner = native_record_for_offset(native_index, candidate.offset)
    if owner is None:
        return False
    _record_number, entry = owner
    return (
        data.find(
            b":PHYSSIZE\0",
            candidate.pixel_offset,
            min(entry.end, candidate.pixel_offset + 1024),
        )
        >= 0
    )


def nested_native_property_stream_metadata(
    data: bytes,
    native_index: NativeIndex | None,
    candidate: DibCandidate,
) -> NativePropertyStreamMetadata | None:
    nested_offset = first_nested_dib_header_offset(data, candidate)
    if nested_offset is None:
        return None
    nested_candidate = parse_dib_candidate(data, nested_offset)
    if nested_candidate is None:
        return None
    return native_property_stream_metadata(data, native_index, nested_candidate)


def find_native_nested_dibs(
    data: bytes,
    native_index: NativeIndex,
    candidates: Iterable[DibCandidate],
) -> list[NativeNestedDibHit]:
    hits: list[NativeNestedDibHit] = []
    seen_offsets: set[int] = set()
    for candidate in candidates:
        if candidate.reject_reason != "nested_dib_header_in_pixel_range":
            continue
        owner = native_record_for_offset(native_index, candidate.offset)
        if owner is None:
            continue
        record_number, entry = owner
        chain = nested_dib_chain_terminal(data, native_index, candidate)
        if chain is None:
            continue
        nested_hit, chain_depth = chain
        if nested_hit.offset in seen_offsets:
            continue
        hits.append(
            NativeNestedDibHit(
                parent_offset=candidate.offset,
                parent_width=candidate.width,
                parent_height=candidate.height,
                chain_depth=chain_depth,
                record_number=record_number,
                record_offset=entry.absolute_offset,
                local_offset=nested_hit.offset - entry.absolute_offset,
                dib=nested_hit,
            )
        )
        seen_offsets.add(nested_hit.offset)
    return hits


def nested_dib_chain_terminal(
    data: bytes,
    native_index: NativeIndex | None,
    candidate: DibCandidate,
    max_depth: int = 16,
) -> tuple[DibHit, int] | None:
    result = nested_dib_chain_terminal_info(data, native_index, candidate, max_depth)
    if result is None:
        return None
    hit, depth, status = result
    if status != "contiguous_record_bounded":
        return None
    return hit, depth


def nested_dib_chain_terminal_info(
    data: bytes,
    native_index: NativeIndex | None,
    candidate: DibCandidate,
    max_depth: int = 16,
) -> tuple[DibHit, int, str] | None:
    if native_index is None or candidate.reject_reason != "nested_dib_header_in_pixel_range":
        return None
    owner = native_record_for_offset(native_index, candidate.offset)
    if owner is None:
        return None
    _record_number, entry = owner
    current = candidate
    seen: set[int] = {candidate.offset}
    for depth in range(1, max_depth + 1):
        nested_offset = first_nested_dib_header_offset(data, current)
        if nested_offset is None:
            return None
        if nested_offset in seen:
            return None
        if not (current.pixel_offset < nested_offset < min(current.expected_end, entry.end)):
            return None
        nested_hit = valid_dib(data, nested_offset)
        if nested_hit is not None:
            if nested_hit.end <= entry.end:
                return nested_hit, depth, "contiguous_record_bounded"
            if any(nested_hit.offset < range_end and nested_hit.end > range_start for range_start, range_end in native_index.metadata_ranges):
                return nested_hit, depth, "crosses_native_metadata"
            return nested_hit, depth, "spans_native_records"
        nested_candidate = parse_dib_candidate(data, nested_offset)
        if nested_candidate is None or nested_candidate.reject_reason != "nested_dib_header_in_pixel_range":
            return None
        seen.add(nested_offset)
        current = nested_candidate
    return None


def nested_dib_chain_terminal_source_kind(
    data: bytes,
    native_index: NativeIndex | None,
    candidate: DibCandidate,
    max_depth: int = 20,
) -> str | None:
    if native_index is None or candidate.reject_reason != "nested_dib_header_in_pixel_range":
        return None
    owner = native_record_for_offset(native_index, candidate.offset)
    if owner is None:
        return None
    _record_number, entry = owner
    current = candidate
    seen: set[int] = {candidate.offset}
    for _depth in range(1, max_depth + 1):
        nested_offset = first_nested_dib_header_offset(data, current)
        if nested_offset is None or nested_offset in seen:
            return None
        if not (current.pixel_offset < nested_offset < min(current.expected_end, entry.end)):
            return None
        nested_hit = valid_dib(data, nested_offset)
        if nested_hit is not None:
            return None
        nested_candidate = parse_dib_candidate(data, nested_offset)
        if nested_candidate is None:
            return "toolbook_nested_dib_chain_to_invalid_metadata"
        if nested_candidate.reject_reason == "native_property_stream_at_pixel_start":
            metadata = native_property_stream_metadata(data, native_index, nested_candidate)
            if metadata is not None:
                if metadata.nested_dib_offset is not None:
                    return "toolbook_nested_dib_chain_to_property_stream_with_nested_dib_descriptor"
                return "toolbook_nested_dib_chain_to_property_stream_metadata"
            if native_property_stream_has_unmatched_physsize(data, native_index, nested_candidate):
                return "toolbook_nested_dib_chain_to_unmatched_physsize_property_stream"
            return "toolbook_nested_dib_chain_to_property_stream"
        if nested_candidate.reject_reason == "pixel_range_outside_file":
            return "toolbook_nested_dib_chain_to_invalid_metadata"
        if nested_candidate.reject_reason == "native_record_at_pixel_start":
            return "toolbook_nested_dib_chain_to_native_record_payload"
        if nested_candidate.reject_reason != "nested_dib_header_in_pixel_range":
            return None
        seen.add(nested_offset)
        current = nested_candidate
    return None


def rejected_dib_source_kind(
    data: bytes,
    candidate: DibCandidate,
    native_index: NativeIndex | None = None,
) -> str:
    if candidate.reject_reason.startswith("native_class41_icon_descriptor_"):
        return "toolbook_class41_icon_descriptor"
    if candidate.reject_reason == "native_property_stream_at_pixel_start":
        metadata = native_property_stream_metadata(data, native_index, candidate)
        if metadata is not None:
            if metadata.nested_dib_offset is not None:
                return "toolbook_property_stream_with_nested_dib_descriptor"
            return "toolbook_property_stream_descriptor_metadata"
        if nested_native_property_stream_metadata(data, native_index, candidate) is not None:
            return "toolbook_property_stream_container_with_nested_physsize_descriptor"
        if native_property_stream_has_unmatched_physsize(data, native_index, candidate):
            if first_nested_dib_header_offset(data, candidate) is not None:
                return "toolbook_property_stream_unmatched_physsize_with_nested_dib"
            return "toolbook_property_stream_unmatched_physsize"
        return "toolbook_dib_info_with_property_stream"
    backed_by_toolbook_record = toolbook_bitmap_record_type(data, candidate.offset) is not None
    if candidate.reject_reason == "native_record_at_pixel_start":
        if first_nested_dib_header_offset(data, candidate) is not None:
            if backed_by_toolbook_record:
                return "toolbook_bitmap_info_container_with_nested_dib_descriptor"
            return "toolbook_native_record_container_with_nested_dib_descriptor"
        if backed_by_toolbook_record:
            return "toolbook_bitmap_info_descriptor_with_native_payload"
        return "toolbook_dib_info_with_native_payload"
    if backed_by_toolbook_record:
        return "toolbook_bitmap_descriptor"
    if candidate.reject_reason == "nested_dib_header_in_pixel_range":
        if toolbook_compressed_dib_payload_end(data, native_index, candidate) is not None:
            return "toolbook_compressed_dib_descriptor"
        chain_terminal = nested_dib_chain_terminal_info(data, native_index, candidate)
        if chain_terminal is not None and chain_terminal[2] == "contiguous_record_bounded":
            return "toolbook_nested_dib_container_with_extracted_dib"
        if chain_terminal is not None and chain_terminal[2] == "crosses_native_metadata":
            return "toolbook_nested_dib_chain_crosses_native_metadata"
        if chain_terminal is not None and chain_terminal[2] == "spans_native_records":
            return "toolbook_nested_dib_chain_spans_native_records"
        terminal_kind = nested_dib_chain_terminal_source_kind(data, native_index, candidate)
        if terminal_kind is not None:
            return terminal_kind
        return "toolbook_dib_info_with_nested_dib_header"
    if candidate.reject_reason == "nested_native_descriptor_header":
        return "toolbook_dib_info_with_nested_native_descriptor"
    if candidate.reject_reason == "pixel_range_outside_file":
        return "invalid_dib_metadata"
    if candidate.reject_reason == "suppressed_1x1_candidate":
        return "suppressed_dib_metadata"
    return "dib_like_native_record"


MEDIA_SCANNERS: tuple[tuple[bytes, Callable[[bytes, int], MediaHit | None]], ...] = (
    (b"BM", valid_bmp),
    (b"RIFF", valid_riff),
    (b"\xff\xd8\xff", valid_jpeg),
    (b"GIF8", valid_gif),
    (b"PK\x03\x04", valid_zip),
)


def overlaps_any(start: int, end: int, ranges: Iterable[tuple[int, int]]) -> bool:
    return any(start < range_end and end > range_start for range_start, range_end in ranges)


def contained_by_any(start: int, end: int, ranges: Iterable[tuple[int, int]]) -> bool:
    return any(range_start <= start and end <= range_end for range_start, range_end in ranges)


def merge_ranges(ranges: Iterable[tuple[int, int]]) -> list[tuple[int, int]]:
    merged: list[list[int]] = []
    for start, end in sorted((start, end) for start, end in ranges if end > start):
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    return [(start, end) for start, end in merged]


def range_total(ranges: Iterable[tuple[int, int]]) -> int:
    return sum(end - start for start, end in merge_ranges(ranges))


def find_media(
    data: bytes,
    base_offset: int = 0,
    allowed_ranges: Iterable[tuple[int, int]] | None = None,
) -> list[MediaHit]:
    allowed = list(allowed_ranges or [])
    hits: list[MediaHit] = []
    for signature, validator in MEDIA_SCANNERS:
        pos = 0
        while True:
            found = data.find(signature, pos)
            if found < 0:
                break
            hit = validator(data, found)
            if hit is not None:
                absolute_offset = hit.offset + base_offset
                absolute_end = absolute_offset + hit.size
                if not allowed or contained_by_any(absolute_offset, absolute_end, allowed):
                    hits.append(
                        MediaHit(hit.kind, absolute_offset, hit.size, hit.extension, hit.description)
                    )
            pos = found + 1
    hits.sort(key=lambda h: (h.offset, -h.size))
    selected: list[MediaHit] = []
    current_end = -1
    for hit in hits:
        if hit.offset >= current_end:
            selected.append(hit)
            current_end = hit.end
    return selected


def find_dibs(
    data: bytes,
    excluded_ranges: Iterable[tuple[int, int]],
    allowed_ranges: Iterable[tuple[int, int]] | None = None,
) -> list[DibHit]:
    excluded = list(excluded_ranges)
    allowed = list(allowed_ranges or [])
    hits = find_toolbook_enveloped_dibs(data, excluded, allowed)
    hits.sort(key=lambda h: (h.offset, -h.dib_size))
    selected: list[DibHit] = []
    selected_ranges: list[tuple[int, int]] = []
    for hit in hits:
        if (not allowed or contained_by_any(hit.offset, hit.end, allowed)) and not overlaps_any(
            hit.offset, hit.end, selected_ranges
        ):
            selected.append(hit)
            selected_ranges.append((hit.offset, hit.end))
    return selected


def find_toolbook_enveloped_dibs(
    data: bytes,
    excluded: Iterable[tuple[int, int]],
    allowed_ranges: Iterable[tuple[int, int]] | None = None,
) -> list[DibHit]:
    excluded_ranges = list(excluded)
    allowed = list(allowed_ranges or [])
    hits: list[DibHit] = []
    pos = 0
    while True:
        marker = data.find(b"\xff\xff\xff\x00\x01\x00\x00", pos)
        if marker < 0:
            break
        pos = marker + 1
        if marker + 30 > len(data) or data[marker + 7 : marker + 9] not in TOOLBOOK_DIB_RECORD_TYPES:
            continue
        search_pos = marker + 30
        search_end = min(len(data), marker + 160)
        while True:
            found = data.find(b"\x28\x00\x00\x00", search_pos, search_end)
            if found < 0:
                break
            search_pos = found + 1
            hit = valid_dib(data, found)
            if (
                hit
                and toolbook_type_a_envelope_matches(data, marker, hit)
                and (not allowed or contained_by_any(hit.offset, hit.end, allowed))
                and not overlaps_any(hit.offset, hit.end, excluded_ranges)
                and not enclosing_native_descriptor_record(data, hit.offset)
            ):
                hits.append(hit)
                break

    pos = 0
    while True:
        start = data.find(b"\x04\x00\x00\x00", pos)
        if start < 0:
            break
        pos = start + 1
        dib_offset = start + 42
        hit = valid_dib(data, dib_offset)
        if (
            hit
            and toolbook_type_b_record_matches(data, start, hit)
            and (not allowed or contained_by_any(hit.offset, hit.end, allowed))
            and not overlaps_any(hit.offset, hit.end, excluded_ranges)
            and not enclosing_native_descriptor_record(data, hit.offset)
        ):
            hits.append(hit)
    return hits


def has_toolbook_dib_envelope(data: bytes, hit: DibHit) -> bool:
    # Observed ToolBook bitmap resource envelope. The record declares the
    # bitmap byte count and display size before the DIB header.
    marker = data.rfind(b"\xff\xff\xff\x00\x01\x00\x00", max(0, hit.offset - 128), hit.offset)
    if marker >= 0 and toolbook_type_a_envelope_matches(data, marker, hit):
        return True

    # Observed compact native image record used by some books. It carries exact
    # width/height immediately before the DIB header.
    start = hit.offset - 42
    if start >= 0 and toolbook_type_b_record_matches(data, start, hit):
        return True
    return False


def toolbook_type_a_envelope_matches(data: bytes, marker: int, hit: DibHit) -> bool:
    if marker < 0 or marker + 30 > len(data) or not (marker + 30 <= hit.offset <= marker + 160):
        return False
    pixel_size = hit.dib_size - hit.pixel_offset
    record_type = data[marker + 7 : marker + 9]
    declared_size = struct.unpack_from("<I", data, marker + 14)[0]
    width_twips = struct.unpack_from("<H", data, marker + 22)[0]
    height_twips = struct.unpack_from("<H", data, marker + 24)[0]
    return (
        record_type in TOOLBOOK_DIB_RECORD_TYPES
        and declared_size == pixel_size
        and width_twips == hit.width * 15
        and height_twips == hit.height * 15
    )


def toolbook_type_b_record_matches(data: bytes, start: int, hit: DibHit) -> bool:
    if start < 0 or start + 42 != hit.offset or start + 30 > len(data):
        return False
    return (
        struct.unpack_from("<I", data, start)[0] == 4
        and struct.unpack_from("<I", data, start + 8)[0] == 3
        and struct.unpack_from("<H", data, start + 12)[0] == 0x35
        and struct.unpack_from("<H", data, start + 26)[0] == hit.height
        and struct.unpack_from("<H", data, start + 28)[0] == hit.width
    )


def enclosing_native_descriptor_record(data: bytes, offset: int) -> DibCandidate | None:
    search_start = max(0, offset - 8192)
    pos = search_start
    while True:
        found = data.find(b"\x28\x00\x00\x00", pos, offset)
        if found < 0:
            return None
        pos = found + 1
        candidate = parse_dib_candidate(data, found)
        if not candidate or candidate.offset == offset:
            continue
        if candidate.reject_reason not in {"native_record_at_pixel_start", "nested_dib_header_in_pixel_range"}:
            continue
        if candidate.pixel_offset <= offset < min(candidate.expected_end, len(data)):
            # DIB headers that appear immediately inside the native record stream
            # of a rejected bitmap descriptor are metadata for that descriptor,
            # not standalone pixel payloads.
            if offset - candidate.pixel_offset <= 4096:
                return candidate


def find_rejected_dib_candidates(
    data: bytes,
    excluded_ranges: Iterable[tuple[int, int]],
    accepted_dibs: Iterable[DibHit],
    allowed_ranges: Iterable[tuple[int, int]] | None = None,
) -> list[DibCandidate]:
    excluded = list(excluded_ranges)
    allowed = list(allowed_ranges or [])
    accepted_offsets = {hit.offset for hit in accepted_dibs}
    candidates: list[DibCandidate] = []
    pos = 0
    while True:
        found = data.find(b"\x28\x00\x00\x00", pos)
        if found < 0:
            break
        pos = found + 1
        if found in accepted_offsets or overlaps_any(found, found + 4, excluded):
            continue
        candidate = parse_dib_candidate(data, found)
        if candidate and allowed and not contained_by_any(
            candidate.offset, min(candidate.expected_end, len(data)), allowed
        ):
            continue
        if candidate and not candidate.reject_reason:
            parent = enclosing_native_descriptor_record(data, found)
            if parent:
                reason = "nested_native_descriptor_header"
            else:
                hit = DibHit(
                    offset=candidate.offset,
                    dib_size=candidate.expected_end - candidate.offset,
                    pixel_offset=candidate.pixel_offset - candidate.offset,
                    width=candidate.width,
                    height=candidate.height,
                    bits_per_pixel=candidate.bits_per_pixel,
                    compression=candidate.compression,
                    file_size=14 + candidate.expected_end - candidate.offset,
                )
                reason = "" if has_toolbook_dib_envelope(data, hit) else "missing_toolbook_bitmap_envelope"
            if reason:
                candidate = DibCandidate(
                    offset=candidate.offset,
                    header_size=candidate.header_size,
                    width=candidate.width,
                    height=candidate.height,
                    bits_per_pixel=candidate.bits_per_pixel,
                    compression=candidate.compression,
                    pixel_offset=candidate.pixel_offset,
                    expected_end=candidate.expected_end,
                    reject_reason=reason,
                )
        if candidate and candidate.reject_reason:
            candidates.append(candidate)
    return candidates


def nearby_context(data: bytes, offset: int, window: int = 1536) -> str:
    start = max(0, offset - window)
    end = min(len(data), offset + 256)
    matches: list[str] = []
    for match in ASCII_RE.finditer(data[start:end]):
        text = match.group(0).decode("cp1252", "replace").strip("\0\r\n\t ")
        if not text or looks_like_gibberish(text):
            continue
        if len(text) > 80:
            text = text[:77] + "..."
        matches.append(text)
    if not matches:
        return ""
    return " | ".join(matches[-4:])


def external_reference_rows(object_model: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    seen = set()
    for ref in object_model["references"]:
        target = str(ref["target"])
        target_lower = target.lower()
        if not target_lower.endswith((".bmp", ".tbk", ".wav", ".avi", ".rmi", ".exe", ".sbk")):
            continue
        key = (int(ref["offset"]), target)
        if key in seen:
            continue
        seen.add(key)
        rows.append(ref)
    return rows


def context_from_blocks(content_blocks: list[dict[str, object]], offset: int) -> str:
    def usable(block: dict[str, object]) -> bool:
        kind = str(block["kind"])
        text = str(block["text"]).replace("\r", " ").replace("\n", " ").strip()
        if kind == "body_text":
            return len(text) >= 24
        if kind in {"handler_name", "menu_label"}:
            return True
        if kind != "label":
            return False
        if text.lower() in {"true", "false", "default", "button", "seite"}:
            return False
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_ /()&.-]{3,63}", text):
            return False
        return sum(ch.isalpha() for ch in text) >= 4

    nearby = [
        block
        for block in content_blocks
        if 0 <= offset - int(block["offset"]) <= 4096 and usable(block)
    ]
    if not nearby:
        return ""
    parts = []
    for block in nearby[-4:]:
        text = str(block["text"]).replace("\r", " ").replace("\n", " ").strip()
        if len(text) > 80:
            text = text[:77] + "..."
        parts.append(text)
    return " | ".join(parts)


def write_content_index(
    path: Path,
    data: bytes,
    media_manifest: list[dict[str, object]],
    dib_manifest: list[dict[str, object]],
    property_dib_manifest: list[dict[str, object]],
    nested_dib_manifest: list[dict[str, object]],
    icon_manifest: list[dict[str, object]],
    object_model: dict[str, object],
    rejected_dibs: list[DibCandidate],
    content_blocks: list[dict[str, object]],
    native_index: NativeIndex | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "kind",
        "name_or_target",
        "offset",
        "end",
        "size",
        "width",
        "height",
        "bits_per_pixel",
        "status",
        "context",
    ]
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        for row in media_manifest:
            off = int(row["offset"])
            writer.writerow(
                {
                    "kind": f"embedded_{row['kind']}",
                    "name_or_target": row["name"],
                    "offset": f"0x{off:08x}",
                    "end": f"0x{int(row['end']):08x}",
                    "size": row["size"],
                    "status": "extracted",
                    "context": context_from_blocks(content_blocks, off),
                }
            )
        for row in dib_manifest:
            off = int(row["offset"])
            writer.writerow(
                {
                    "kind": "reconstructed_dib",
                    "name_or_target": row["name"],
                    "offset": f"0x{off:08x}",
                    "end": f"0x{off + int(row['dib_size']):08x}",
                    "size": row["dib_size"],
                    "width": row["width"],
                    "height": row["height"],
                    "bits_per_pixel": row["bits_per_pixel"],
                    "status": "extracted",
                    "context": context_from_blocks(content_blocks, off),
                }
            )
        for row in property_dib_manifest:
            off = int(row["offset"])
            writer.writerow(
                {
                    "kind": "native_property_stream_dib",
                    "name_or_target": row["name"],
                    "offset": f"0x{off:08x}",
                    "end": f"0x{int(row['pixel_source_offset']) + int(row['pixel_size']):08x}",
                    "size": row["dib_size"],
                    "width": row["width"],
                    "height": row["height"],
                    "bits_per_pixel": row["bits_per_pixel"],
                    "status": "extracted",
                    "context": context_from_blocks(content_blocks, off),
                }
            )
        for row in nested_dib_manifest:
            off = int(row["offset"])
            writer.writerow(
                {
                    "kind": "native_nested_dib",
                    "name_or_target": row["name"],
                    "offset": f"0x{off:08x}",
                    "end": f"0x{off + int(row['dib_size']):08x}",
                    "size": row["dib_size"],
                    "width": row["width"],
                    "height": row["height"],
                    "bits_per_pixel": row["bits_per_pixel"],
                    "status": "extracted",
                    "context": context_from_blocks(content_blocks, off),
                }
            )
        for row in icon_manifest:
            off = int(row["offset"])
            writer.writerow(
                {
                    "kind": "native_class41_icon",
                    "name_or_target": row["name"],
                    "offset": f"0x{off:08x}",
                    "end": f"0x{int(row['end']):08x}",
                    "size": row["size"],
                    "width": row["width"],
                    "height": row["height"],
                    "bits_per_pixel": row["bits_per_pixel"],
                    "status": "extracted",
                    "context": context_from_blocks(content_blocks, off),
                }
            )
        for ref in external_reference_rows(object_model):
            off = int(ref["offset"])
            writer.writerow(
                {
                    "kind": ref["target_type"],
                    "name_or_target": ref["target"],
                    "offset": f"0x{off:08x}",
                    "status": "referenced_not_embedded",
                    "context": context_from_blocks(content_blocks, off),
                }
            )
        for candidate in rejected_dibs:
            source_kind = rejected_dib_source_kind(data, candidate, native_index)
            row_end = min(candidate.expected_end, len(data))
            row_status = candidate.reject_reason
            compressed_payload_end = toolbook_compressed_dib_payload_end(data, native_index, candidate)
            if source_kind == "toolbook_compressed_dib_descriptor" and compressed_payload_end is not None:
                row_end = compressed_payload_end
                row_status = "compressed_payload_not_decoded:dword_local_end_pointer_and_two_substreams"
            elif source_kind == "toolbook_property_stream_with_nested_dib_descriptor":
                metadata = native_property_stream_metadata(data, native_index, candidate)
                if metadata is not None and metadata.nested_dib_offset is not None:
                    row_end = metadata.nested_dib_offset
                    row_status = f"native_property_metadata_before_nested_dib_descriptor:{metadata.match_kind}"
            elif source_kind == "toolbook_property_stream_descriptor_metadata":
                metadata = native_property_stream_metadata(data, native_index, candidate)
                if metadata is not None:
                    row_status = f"native_property_metadata_not_pixel_payload:{metadata.match_kind}"
            elif source_kind == "toolbook_property_stream_container_with_nested_physsize_descriptor":
                metadata = nested_native_property_stream_metadata(data, native_index, candidate)
                if metadata is not None and metadata.nested_dib_offset is None:
                    nested_dib_offset = first_nested_dib_header_offset(data, candidate)
                    if nested_dib_offset is not None:
                        row_end = nested_dib_offset
                    row_status = f"native_property_container_before_nested_physsize:{metadata.match_kind}"
            elif source_kind in {
                "toolbook_bitmap_info_container_with_nested_dib_descriptor",
                "toolbook_native_record_container_with_nested_dib_descriptor",
                "toolbook_nested_dib_container_with_extracted_dib",
                "toolbook_nested_dib_chain_crosses_native_metadata",
                "toolbook_nested_dib_chain_spans_native_records",
                "toolbook_nested_dib_chain_to_property_stream_with_nested_dib_descriptor",
                "toolbook_nested_dib_chain_to_property_stream_metadata",
                "toolbook_nested_dib_chain_to_unmatched_physsize_property_stream",
                "toolbook_nested_dib_chain_to_property_stream",
                "toolbook_nested_dib_chain_to_invalid_metadata",
                "toolbook_nested_dib_chain_to_native_record_payload",
            }:
                nested_dib_offset = first_nested_dib_header_offset(data, candidate)
                if nested_dib_offset is not None:
                    row_end = nested_dib_offset
                    if source_kind == "toolbook_nested_dib_container_with_extracted_dib":
                        row_status = "native_container_before_extracted_nested_dib"
                    elif source_kind == "toolbook_nested_dib_chain_crosses_native_metadata":
                        row_status = "native_nested_dib_chain_crosses_native_metadata"
                    elif source_kind == "toolbook_nested_dib_chain_spans_native_records":
                        row_status = "native_nested_dib_chain_spans_native_records"
                    elif source_kind == "toolbook_nested_dib_chain_to_property_stream_with_nested_dib_descriptor":
                        row_status = "native_nested_dib_chain_to_property_stream_before_nested_dib"
                    elif source_kind == "toolbook_nested_dib_chain_to_property_stream_metadata":
                        row_status = "native_nested_dib_chain_to_property_stream_metadata"
                    elif source_kind == "toolbook_nested_dib_chain_to_unmatched_physsize_property_stream":
                        row_status = "native_nested_dib_chain_to_unmatched_physsize_property_stream"
                    elif source_kind == "toolbook_nested_dib_chain_to_property_stream":
                        row_status = "native_nested_dib_chain_to_property_stream"
                    elif source_kind == "toolbook_nested_dib_chain_to_invalid_metadata":
                        row_status = "native_nested_dib_chain_to_invalid_metadata"
                    elif source_kind == "toolbook_nested_dib_chain_to_native_record_payload":
                        row_status = "native_nested_dib_chain_to_native_record_payload"
                    else:
                        row_status = "native_record_container_before_nested_dib_descriptor"
            elif source_kind == "toolbook_bitmap_info_descriptor_with_native_payload":
                row_status = "native_payload_not_pixel_array"
            elif source_kind == "toolbook_dib_info_with_native_payload":
                row_status = "native_payload_not_pixel_array"
            elif source_kind == "toolbook_property_stream_unmatched_physsize_with_nested_dib":
                nested_dib_offset = first_nested_dib_header_offset(data, candidate)
                if nested_dib_offset is not None:
                    row_end = nested_dib_offset
                    row_status = "native_property_unmatched_physsize_before_nested_dib"
            elif source_kind == "toolbook_property_stream_unmatched_physsize":
                row_status = "native_property_unmatched_physsize"
            writer.writerow(
                {
                    "kind": source_kind,
                    "name_or_target": "",
                    "offset": f"0x{candidate.offset:08x}",
                    "end": f"0x{row_end:08x}",
                    "size": max(0, row_end - candidate.offset),
                    "width": candidate.width,
                    "height": candidate.height,
                    "bits_per_pixel": candidate.bits_per_pixel,
                    "status": row_status,
                    "context": context_from_blocks(content_blocks, candidate.offset),
                }
            )
    chmod_group_readable(path)


def build_bmp_from_dib(dib: bytes) -> bytes:
    pixel_offset = 14 + struct.unpack_from("<I", dib, 0)[0]
    header_size = struct.unpack_from("<I", dib, 0)[0]
    if header_size == 12:
        bpp = struct.unpack_from("<H", dib, 10)[0]
        colors = 1 << bpp if bpp <= 8 else 0
        pixel_offset = 14 + header_size + colors * 3
    else:
        bpp = struct.unpack_from("<H", dib, 14)[0]
        clr_used = struct.unpack_from("<I", dib, 32)[0]
        colors = clr_used if clr_used else ((1 << bpp) if bpp <= 8 else 0)
        pixel_offset = 14 + header_size + colors * 4
    file_size = 14 + len(dib)
    return b"BM" + struct.pack("<IHHI", file_size, 0, 0, pixel_offset) + dib


def build_ico_from_dib_icon_payload(dib: bytes, width: int, height: int, bits_per_pixel: int) -> bytes:
    colors = (1 << bits_per_pixel) if bits_per_pixel <= 8 else 0
    color_count = colors if 0 < colors < 256 else 0
    icon_dir = struct.pack("<HHH", 0, 1, 1)
    entry = struct.pack(
        "<BBBBHHII",
        width if width < 256 else 0,
        height if height < 256 else 0,
        color_count,
        0,
        1,
        bits_per_pixel,
        len(dib),
        6 + 16,
    )
    return icon_dir + entry + dib


def native_icon_payload_size(data: bytes, candidate: DibCandidate) -> int | None:
    if candidate.header_size != 40 or candidate.compression != 0 or candidate.height < 2 or candidate.height % 2:
        return None
    if candidate.offset + 40 > len(data):
        return None
    clr_used = struct.unpack_from("<I", data, candidate.offset + 32)[0]
    colors = clr_used if clr_used else ((1 << candidate.bits_per_pixel) if candidate.bits_per_pixel <= 8 else 0)
    if colors > 256:
        return None
    icon_height = candidate.height // 2
    xor_stride = ((candidate.width * candidate.bits_per_pixel + 31) // 32) * 4
    mask_stride = ((candidate.width + 31) // 32) * 4
    return candidate.header_size + colors * 4 + xor_stride * icon_height + mask_stride * icon_height


def dib_is_inside_embedded_bmp(blob: bytes, local_offset: int) -> bool:
    if local_offset < 14 or blob[local_offset - 14 : local_offset - 12] != b"BM":
        return False
    bmp_start = local_offset - 14
    if bmp_start + 14 > len(blob):
        return False
    file_size = struct.unpack_from("<I", blob, bmp_start + 2)[0]
    return file_size >= 14 and bmp_start + file_size <= len(blob)


def find_native_class41_icons(data: bytes, native_index: NativeIndex) -> tuple[list[NativeIconHit], list[DibCandidate]]:
    icons: list[NativeIconHit] = []
    rejected: list[DibCandidate] = []
    seen_offsets: set[int] = set()
    for record_number, entry in enumerate(native_index.records, 1):
        blob = data[entry.absolute_offset : entry.end]
        if len(blob) < 0x12:
            continue
        type_word = struct.unpack_from("<H", blob, 0x0A)[0]
        class_id = struct.unpack_from("<H", blob, 0x0C)[0]
        object_id = struct.unpack_from("<H", blob, 0x0E)[0]
        if class_id != 41 or type_word != 0x001B or object_id != 0x0201:
            continue
        pos = 0x12
        while True:
            local = blob.find(b"\x28\x00\x00\x00", pos)
            if local < 0:
                break
            pos = local + 1
            absolute = entry.absolute_offset + local
            if absolute in seen_offsets or dib_is_inside_embedded_bmp(blob, local):
                continue
            if local < 8:
                continue
            candidate = parse_dib_candidate(data, absolute)
            if not candidate:
                continue
            stored_size = struct.unpack_from("<I", blob, local - 8)[0]
            payload_marker = struct.unpack_from("<I", blob, local - 4)[0]
            icon_size = native_icon_payload_size(data, candidate)
            if (
                payload_marker == 0x16
                and icon_size is not None
                and stored_size >= icon_size
                and local + stored_size <= len(blob)
                and set(blob[local + icon_size : local + stored_size]) <= {0}
            ):
                icons.append(
                    NativeIconHit(
                        offset=absolute,
                        size=icon_size,
                        stored_size=stored_size,
                        padding_size=stored_size - icon_size,
                        width=candidate.width,
                        height=candidate.height // 2,
                        bits_per_pixel=candidate.bits_per_pixel,
                        record_number=record_number,
                        record_offset=entry.absolute_offset,
                        local_offset=local,
                    )
                )
                seen_offsets.add(absolute)
                continue
            rejected.append(
                DibCandidate(
                    offset=candidate.offset,
                    header_size=candidate.header_size,
                    width=candidate.width,
                    height=candidate.height,
                    bits_per_pixel=candidate.bits_per_pixel,
                    compression=candidate.compression,
                    pixel_offset=candidate.pixel_offset,
                    expected_end=min(entry.end, candidate.offset + max(0, stored_size)),
                    reject_reason="native_class41_icon_descriptor_size_mismatch",
                )
            )
    return icons, rejected


def native_record_for_offset(native_index: NativeIndex, offset: int) -> tuple[int, NativeIndexEntry] | None:
    for record_number, entry in enumerate(native_index.records, 1):
        if entry.absolute_offset <= offset < entry.end:
            return record_number, entry
    return None


def native_property_stream_dib_hit(
    data: bytes,
    native_index: NativeIndex,
    candidate: DibCandidate,
) -> NativePropertyDibHit | None:
    if candidate.reject_reason != "native_property_stream_at_pixel_start":
        return None
    owner = native_record_for_offset(native_index, candidate.offset)
    if owner is None:
        return None
    record_number, entry = owner
    if candidate.offset < entry.absolute_offset + 2:
        return None

    property_marker = data.find(
        b":PHYSSIZE\0",
        candidate.pixel_offset,
        min(entry.end, candidate.pixel_offset + 512),
    )
    if property_marker < 0:
        return None
    value_size_offset = property_marker + len(b":PHYSSIZE\0") + 4
    if value_size_offset + 6 > entry.end:
        return None
    value_size = struct.unpack_from("<H", data, value_size_offset)[0]
    if value_size != 4:
        return None
    physical_width_twips, physical_height_twips = struct.unpack_from("<HH", data, value_size_offset + 2)
    if physical_width_twips != candidate.width * 15 or physical_height_twips != candidate.height * 15:
        return None

    # The PHYSSIZE value is followed by a native four-byte property-link/control
    # word. In the observed records that actually carry pixels, bitmap bits begin
    # immediately after that control word.
    pixel_source_offset = value_size_offset + 2 + value_size + 4
    pixel_size = candidate.expected_end - candidate.pixel_offset
    descriptor_pointer_value = struct.unpack_from("<H", data, candidate.offset - 2)[0]
    descriptor_pointer_offset = entry.absolute_offset + descriptor_pointer_value
    if not (candidate.pixel_offset <= descriptor_pointer_offset <= min(entry.end, candidate.pixel_offset + 512)):
        return None
    if not (pixel_source_offset <= descriptor_pointer_offset):
        return None
    if pixel_source_offset + pixel_size > entry.end:
        return None

    return NativePropertyDibHit(
        offset=candidate.offset,
        dib_info_end=candidate.pixel_offset,
        pixel_source_offset=pixel_source_offset,
        pixel_size=pixel_size,
        width=candidate.width,
        height=candidate.height,
        bits_per_pixel=candidate.bits_per_pixel,
        compression=candidate.compression,
        property_offset=property_marker,
        property_value_offset=value_size_offset + 2,
        physical_width_twips=physical_width_twips,
        physical_height_twips=physical_height_twips,
        descriptor_pointer_offset=descriptor_pointer_offset,
        descriptor_pointer_value=descriptor_pointer_value,
        record_number=record_number,
        record_offset=entry.absolute_offset,
        local_offset=candidate.offset - entry.absolute_offset,
    )


def find_native_property_stream_dibs(
    data: bytes,
    native_index: NativeIndex,
    candidates: Iterable[DibCandidate],
) -> list[NativePropertyDibHit]:
    hits = []
    seen_offsets: set[int] = set()
    for candidate in candidates:
        if candidate.offset in seen_offsets:
            continue
        hit = native_property_stream_dib_hit(data, native_index, candidate)
        if hit is None:
            continue
        hits.append(hit)
        seen_offsets.add(hit.offset)
    return hits


def dib_palette_and_pixels(dib: bytes) -> tuple[int, int, int, int, list[tuple[int, int, int]], int] | None:
    header_size = struct.unpack_from("<I", dib, 0)[0]
    if header_size != 40 or len(dib) < 40:
        return None
    width, signed_height, planes, bpp, compression, _size_image = struct.unpack_from("<iiHHII", dib, 4)
    if planes != 1 or bpp != 8 or compression != 0 or width <= 0 or signed_height == 0:
        return None
    height = abs(signed_height)
    clr_used = struct.unpack_from("<I", dib, 32)[0] or 256
    if clr_used > 256 or len(dib) < header_size + clr_used * 4:
        return None
    palette = []
    pal_off = header_size
    for idx in range(clr_used):
        b, g, r, _reserved = dib[pal_off + idx * 4 : pal_off + idx * 4 + 4]
        palette.append((r, g, b))
    pixel_offset = header_size + clr_used * 4
    return width, height, signed_height, bpp, palette, pixel_offset


def detect_cyclic_row_shift_8bpp(dib: bytes) -> int:
    parsed = dib_palette_and_pixels(dib)
    if not parsed:
        return 0
    width, height, _signed_height, _bpp, palette, pixel_offset = parsed
    stride = ((width + 3) // 4) * 4
    if width < 64 or height < 32 or pixel_offset + stride * height > len(dib):
        return 0
    scores = []
    for x in range(1, width):
        score = 0
        for y in range(height):
            row = pixel_offset + y * stride
            left = palette[dib[row + x - 1]]
            right = palette[dib[row + x]]
            score += abs(left[0] - right[0]) + abs(left[1] - right[1]) + abs(left[2] - right[2])
        scores.append((score, x))
    if not scores:
        return 0
    scores_sorted = sorted(scores)
    median = scores_sorted[len(scores_sorted) // 2][0]
    best_score, best_x = max(scores)
    edge_limit = max(8, width // 5)
    if not (best_x <= edge_limit or best_x >= width - edge_limit):
        return 0
    if median <= 0 or best_score < median * 6:
        return 0
    # Avoid shifting on normal hard image edges by requiring the best seam to be
    # much stronger than typical content seams outside its local neighborhood.
    outside = [score for score, x in scores if abs(x - best_x) > 4]
    outside.sort()
    p95 = outside[int(len(outside) * 0.95)] if outside else median
    if p95 and best_score < p95 * 2.5:
        return 0
    return best_x


def build_unwrapped_bmp_from_dib(dib: bytes, shift: int) -> bytes:
    parsed = dib_palette_and_pixels(dib)
    if not parsed or shift <= 0:
        return build_bmp_from_dib(dib)
    width, height, _signed_height, _bpp, _palette, pixel_offset = parsed
    stride = ((width + 3) // 4) * 4
    fixed = bytearray(dib)
    for y in range(height):
        row_off = pixel_offset + y * stride
        row = bytes(fixed[row_off : row_off + width])
        fixed[row_off : row_off + width] = row[shift:] + row[:shift]
    return build_bmp_from_dib(bytes(fixed))


def extract_strings(data: bytes) -> str:
    lines = []
    for match in ASCII_RE.finditer(data):
        text = match.group(0).decode("utf-8", "replace")
        lines.append(f"0x{match.start():08x}\t{text}")
    return "\n".join(lines) + "\n"


def make_byte_map(input_size: int, tbk_offset: int, media_hits: Iterable[MediaHit]) -> list[dict[str, object]]:
    top_level = []
    if tbk_offset:
        top_level.append({"offset": 0, "size": tbk_offset, "end": tbk_offset, "role": "pe_wrapper_stub"})
    top_level.append({"offset": tbk_offset, "size": input_size - tbk_offset, "end": input_size, "role": "toolbook_payload"})
    overlays = [
        {
            "offset": hit.offset,
            "size": hit.size,
            "end": hit.end,
            "role": f"embedded_{hit.kind}",
            "description": hit.description,
        }
        for hit in media_hits
    ]
    return top_level + overlays


def find_native_segments(payload_size: int, media_hits: list[MediaHit], tbk_offset: int) -> list[NativeSegment]:
    segments: list[NativeSegment] = []
    cursor = tbk_offset
    payload_end = tbk_offset + payload_size
    local_hits = sorted((hit for hit in media_hits if tbk_offset <= hit.offset < payload_end), key=lambda h: h.offset)
    if not local_hits:
        return [
            NativeSegment(
                "0001_native_payload",
                "native_payload",
                tbk_offset,
                payload_size,
                "Complete ToolBook-native payload; no standalone embedded media was validated",
            )
        ]
    for idx, hit in enumerate(local_hits):
        if cursor < hit.offset:
            if cursor == tbk_offset:
                role = "native_header_index_objects"
                desc = "ToolBook header, allocation/index data, object records, scripts, and resource envelope bytes before first extracted media"
            else:
                role = "native_media_envelope_gap"
                desc = "ToolBook-native bytes between embedded media payloads; often padding plus the next resource envelope prefix"
            segments.append(
                NativeSegment(f"{len(segments)+1:04d}_{role}", role, cursor, hit.offset - cursor, desc)
            )
        cursor = max(cursor, hit.end)
    if cursor < payload_end:
        role = "native_trailing_records"
        desc = "ToolBook-native bytes after the last extracted media payload"
        segments.append(NativeSegment(f"{len(segments)+1:04d}_{role}", role, cursor, payload_end - cursor, desc))
    return segments


def native_record_segments(native_index: NativeIndex) -> list[NativeSegment]:
    return [
        NativeSegment(
            f"{idx:04d}_native_record",
            "native_active_record",
            record.absolute_offset,
            record.length,
            "Active ToolBook record reached through the native allocation/index tree",
        )
        for idx, record in enumerate(native_index.records, 1)
    ]


def extract_ascii_records(data: bytes) -> list[dict[str, object]]:
    records = []
    for match in ASCII_RE.finditer(data):
        text = match.group(0).decode("utf-8", "replace")
        kind = "text"
        lowered = text.lower()
        if "\\" in text or lowered.endswith((".tbk", ".bmp", ".wav", ".exe", ".sbk")):
            kind = "path_or_file_reference"
        elif text in {"enterpage", "leavepage", "enterBook", "buttonUp", "update", "notifyBefore update"}:
            kind = "openscript_handler_or_event"
        records.append({"offset": match.start(), "size": match.end() - match.start(), "kind": kind, "text": text})
    return records


def classify_ascii_text(text: str) -> str:
    lowered = text.lower()
    if "\\" in text or lowered.endswith((".tbk", ".bmp", ".wav", ".exe", ".sbk")):
        return "path_or_file_reference"
    if text in {"enterpage", "leavepage", "enterBook", "buttonUp", "update", "notifyBefore update", "enterbook", "leavesystem"}:
        return "openscript_handler_or_event"
    if text.startswith("&") or "\tCtrl+" in text or "\tAlt+" in text or "\tF" in text:
        return "menu_or_command_label"
    return "text"


def in_ranges(offset: int, ranges: list[tuple[int, int]]) -> bool:
    return any(start <= offset < end for start, end in ranges)


def find_probable_objects(data: bytes, allowed_ranges: list[tuple[int, int]]) -> list[dict[str, object]]:
    objects: list[dict[str, object]] = []
    name_matches = []
    for match in ASCII_RE.finditer(data):
        if not in_ranges(match.start(), allowed_ranges):
            continue
        raw = match.group(0)
        text = raw.decode("latin1", "replace").strip("\0")
        if not text or len(text) > 64:
            continue
        kind = classify_ascii_text(text)
        if kind == "path_or_file_reference":
            continue
        if text in {"buttonUp", "enterpage", "leavepage", "update", "enterbook", "leavesystem"}:
            continue
        if re.fullmatch(r"[0-9A-Fa-f]{3,}|[3DCR8\"#:$& ]{5,}", text):
            continue
        name_matches.append((match.start(), match.end(), text, kind))

    object_post_markers = (b"\x09\x00", b"\x02\x02", b"\x14\x00\x00")
    for idx, (start, end, text, kind) in enumerate(name_matches):
        pre = data[max(0, start - 96) : start]
        post = data[end : min(len(data), end + 512)]
        short_post = data[end : min(len(data), end + 32)]
        evidence = []
        object_kind = "named_record"
        if any(marker in short_post for marker in object_post_markers):
            evidence.append("record-like marker after name")
        if b"\x02\x02" in short_post:
            evidence.append("object payload marker after name")
        if b"\x14\x00\x00" in short_post:
            evidence.append("ToolBook descriptor word after name")
        if b"buttonUp\x00" in data[end : min(len(data), end + 160)]:
            evidence.append("buttonUp handler nearby")
            object_kind = "button_or_interactive_object"
        if text.startswith("&"):
            object_kind = "menu_or_command"
        if text.lower() in {"inhalt", "ebenen", "polygone", "sterne", "schnittstudie", "zurück", "zuruck", "ausschneiden"}:
            object_kind = "page_or_named_object"
            evidence.append("known page/object-style name in sample corpus")
        if not any(marker in short_post for marker in object_post_markers) and not text.startswith("&"):
            continue
        if not evidence and kind == "text":
            continue
        objects.append(
            {
                "index": len(objects) + 1,
                "offset": start,
                "text": text,
                "probable_kind": object_kind,
                "classification": kind,
                "evidence": evidence,
                "context_start": max(0, start - 64),
                "context_end": min(len(data), end + 128),
            }
        )
    return objects


def find_handlers(data: bytes, allowed_ranges: list[tuple[int, int]]) -> list[dict[str, object]]:
    handlers: list[dict[str, object]] = []
    handler_names = [
        b"buttonUp",
        b"enterpage",
        b"leavepage",
        b"enterbook",
        b"enterBook",
        b"leavesystem",
        b"update",
        b"notifyBefore update",
    ]
    seen = set()
    for name in handler_names:
        pos = 0
        while True:
            off = data.find(name + b"\x00", pos)
            if off < 0:
                break
            pos = off + 1
            if not in_ranges(off, allowed_ranges):
                continue
            if off in seen:
                continue
            seen.add(off)
            # The compiled script body commonly follows the handler name after a
            # short length/flag prefix. Keep a bounded window and extract any
            # readable fragments inside it as evidence.
            window = data[off : min(len(data), off + 320)]
            fragments = []
            for m in ASCII_RE.finditer(window):
                txt = m.group(0).decode("latin1", "replace")
                fragments.append({"relative_offset": m.start(), "text": txt})
            handlers.append(
                {
                    "offset": off,
                    "name": name.decode("ascii", "replace"),
                    "context_start": max(0, off - 64),
                    "context_end": min(len(data), off + 320),
                    "readable_fragments": fragments,
                    "note": "Handler located; following bytes are tokenized OpenScript and are not fully decompiled.",
                }
            )
    handlers.sort(key=lambda row: row["offset"])
    for idx, row in enumerate(handlers, 1):
        row["index"] = idx
    return handlers


def extract_reference_edges(records: list[dict[str, object]], allowed_ranges: list[tuple[int, int]]) -> list[dict[str, object]]:
    edges = []
    ref_re = re.compile(r"^[A-Za-z0-9_.:/\\$() -]+\.(tbk|bmp|wav|avi|rmi|exe|sbk)$", re.IGNORECASE)
    for rec in records:
        text = str(rec["text"])
        if not in_ranges(int(rec["offset"]), allowed_ranges):
            continue
        lowered = text.lower()
        if ref_re.match(text.strip()):
            target_type = "external_or_embedded_reference"
            if lowered.endswith(".tbk"):
                target_type = "toolbook_link"
            elif lowered.endswith(".bmp") or ".bmp" in lowered:
                target_type = "bitmap_reference"
            elif lowered.endswith(".exe") or ".exe " in lowered:
                target_type = "external_program_reference"
            edges.append({"offset": rec["offset"], "target": text, "target_type": target_type})
    return edges


def analyze_object_model(
    data: bytes, ascii_records: list[dict[str, object]], native_segments: list[NativeSegment]
) -> dict[str, object]:
    allowed_ranges = [(seg.offset, seg.end) for seg in native_segments]
    objects = find_probable_objects(data, allowed_ranges)
    handlers = find_handlers(data, allowed_ranges)
    references = extract_reference_edges(ascii_records, allowed_ranges)
    return {
        "status": "candidate_object_model_not_full_semantic_decode",
        "probable_objects": objects,
        "handlers": handlers,
        "references": references,
        "counts": {
            "probable_objects": len(objects),
            "handlers": len(handlers),
            "references": len(references),
            "native_ranges_considered": len(allowed_ranges),
        },
        "limitations": [
            "Object boundaries and type names are inferred from corpus patterns and surrounding descriptors.",
            "Handler bytecode is located but not decompiled into complete OpenScript source.",
            "Ownership relationships between book/page/background/object records are not fully resolved.",
        ],
    }


def looks_like_gibberish(text: str) -> bool:
    stripped = text.strip()
    if len(stripped) < 3:
        return True
    tokenish = set("€‚ƒ„…†‡ˆ‰Š‹ŒŽ‘’“”•–—˜™š›œžŸ")
    if any(ch in tokenish for ch in stripped):
        return True
    unlikely_content = set("ÿþÞÐð×÷¼½¾¹²³¬¦¤")
    if any(ch in unlikely_content for ch in stripped):
        return True
    letters = sum(ch.isalpha() for ch in stripped)
    nonspace = sum(not ch.isspace() for ch in stripped)
    high_bytes = sum(ord(ch) >= 0x80 for ch in stripped)
    if len(stripped) < 20 and high_bytes / max(1, nonspace) > 0.18:
        return True
    printable = sum((ch.isprintable() or ch in "\r\n\t") for ch in stripped)
    if printable / max(1, len(stripped)) < 0.85:
        return True
    if letters == 0:
        return True
    if letters / max(1, nonspace) < 0.35:
        return True
    most_common = max((stripped.count(ch) for ch in set(stripped)), default=0)
    if len(stripped) >= 8 and most_common / len(stripped) > 0.72:
        return True
    symbolish = sum(not (ch.isalnum() or ch.isspace() or ch in ".,;:!?()[]{}'\"/-_\\&\t") for ch in stripped)
    return symbolish / max(1, nonspace) > 0.18


def classify_content_text(text: str) -> str:
    low = text.lower()
    if low.endswith((".tbk", ".bmp", ".wav", ".exe", ".sbk")) or "\\" in text:
        return "reference"
    if text in {"buttonUp", "enterpage", "leavepage", "enterbook", "enterBook", "update", "leavesystem"}:
        return "handler_name"
    if text.startswith("&") or "\tCtrl+" in text or "\tAlt+" in text or "\tF" in text:
        return "menu_label"
    if len(text) >= 30 or any(ch in text for ch in ".!?\r\n") or any(ord(ch) >= 0x80 for ch in text):
        return "body_text"
    return "label"


def decode_native_record_name(blob: bytes) -> str:
    if len(blob) < 0x12:
        return ""
    raw = blob[0x12 : min(len(blob), 0x32)]
    return raw.split(b"\0", 1)[0].decode("cp1252", "replace")


def decode_class2_directory(
    blob: bytes,
    record_start: int,
    key_to_record: dict[int, dict[str, object]],
) -> dict[str, object] | None:
    entry_start = 0x13
    entry_size = 12
    if len(blob) < entry_start + entry_size:
        return None
    entries = []
    pos = entry_start
    while pos + entry_size <= len(blob):
        value0, value1 = struct.unpack_from("<II", blob, pos)
        marker = blob[pos + 8 : pos + 10]
        target_key = struct.unpack_from("<H", blob, pos + 10)[0]
        target = key_to_record.get(target_key)
        if marker != b"\x14\x00" or target is None:
            break
        entries.append(
            {
                "entry_offset": record_start + pos,
                "local_offset": pos,
                "entry_size": entry_size,
                "value0": value0,
                "value1": value1,
                "value1_matches_target_object_id": value1 == target["object_id"],
                "target_key": target_key,
                "target_record_number": target["record_number"],
                "target_class_id": target["class_id"],
                "target_class_name": target["class_name"],
                "target_object_id": target["object_id"],
                "target_name": target["name"],
            }
        )
        pos += entry_size
    if not entries:
        return None
    tail = blob[pos:]
    return {
        "kind": "class2_page_or_background_directory",
        "entry_start": entry_start,
        "entry_size": entry_size,
        "entry_count": len(entries),
        "entries_end": pos,
        "trailing_zero_padding_bytes": len(tail) if all(byte == 0 for byte in tail) else 0,
        "trailing_unparsed_bytes": 0 if all(byte == 0 for byte in tail) else len(tail),
        "entries": entries,
    }


def decode_class3_name_hash_table(
    blob: bytes,
    record_start: int,
    object_id: int,
    owner_or_reserved: int,
    key_to_record: dict[int, dict[str, object]],
) -> dict[str, object] | None:
    if object_id == 0:
        return None
    table_start = owner_or_reserved - 6
    entry_size = 4
    if table_start < 0 or table_start + object_id * entry_size > len(blob):
        return {
            "kind": "class3_name_hash_table",
            "decoded": False,
            "entry_count_from_object_id": object_id,
            "table_start_from_header_0x10_minus_6": table_start,
            "reason": "header-derived table range is outside the record",
        }

    entries = []
    for index in range(object_id):
        entry_offset = table_start + index * entry_size
        hash_word, text_offset = struct.unpack_from("<HH", blob, entry_offset)
        if text_offset < 6 or text_offset >= len(blob):
            return {
                "kind": "class3_name_hash_table",
                "decoded": False,
                "entry_count_from_object_id": object_id,
                "table_start_from_header_0x10_minus_6": table_start,
                "failed_entry_index": index,
                "failed_entry_local_offset": entry_offset,
                "failed_text_offset": text_offset,
                "reason": "table entry does not point inside the record to a typed string value",
            }
        value_type, link_offset, text_length = struct.unpack_from("<HHH", blob, text_offset - 6)
        if value_type not in {1, 3}:
            return {
                "kind": "class3_name_hash_table",
                "decoded": False,
                "entry_count_from_object_id": object_id,
                "table_start_from_header_0x10_minus_6": table_start,
                "failed_entry_index": index,
                "failed_entry_local_offset": entry_offset,
                "failed_text_offset": text_offset,
                "failed_value_type": value_type,
                "reason": "table entry does not point to an observed class-3 typed string value",
            }
        if text_length == 0 or text_offset + text_length > len(blob) or blob[text_offset + text_length - 1] != 0:
            return {
                "kind": "class3_name_hash_table",
                "decoded": False,
                "entry_count_from_object_id": object_id,
                "table_start_from_header_0x10_minus_6": table_start,
                "failed_entry_index": index,
                "failed_entry_local_offset": entry_offset,
                "failed_text_offset": text_offset,
                "failed_text_length": text_length,
                "reason": "typed string length is not a NUL-terminated string inside the record",
            }
        raw_text = blob[text_offset : text_offset + text_length - 1]
        entries.append(
            {
                "entry_index": index,
                "entry_offset": record_start + entry_offset,
                "local_offset": entry_offset,
                "hash_word": hash_word,
                "text_offset": record_start + text_offset,
                "text_local_offset": text_offset,
                "value_header_offset": record_start + text_offset - 6,
                "value_header_local_offset": text_offset - 6,
                "value_type": value_type,
                "link_offset": link_offset,
                "text_length_including_nul": text_length,
                "text": raw_text.decode("cp1252", "replace"),
            }
        )

    value_entries_by_start: dict[int, list[dict[str, object]]] = {}
    for entry in entries:
        value_entries_by_start.setdefault(int(entry["value_header_local_offset"]), []).append(entry)
    value_starts = sorted(value_entries_by_start)
    value_records = []
    if value_starts:
        for index, value_start in enumerate(value_starts):
            value_entries = value_entries_by_start[value_start]
            boundary_candidates = [len(blob)]
            boundary_candidates.extend(start for start in value_starts[index + 1 :] if start > value_start)
            if table_start > value_start:
                boundary_candidates.append(table_start)
            value_end = min(boundary_candidates)
            text_end = max(
                int(entry["text_local_offset"]) + int(entry["text_length_including_nul"])
                for entry in value_entries
            )
            if not (value_start + 6 <= text_end <= value_end <= len(blob)):
                continue
            value_records.append(
                {
                    "kind": "class3_typed_string_value_record",
                    "offset": record_start + value_start,
                    "local_offset": value_start,
                    "end": record_start + value_end,
                    "end_local_offset": value_end,
                    "size": value_end - value_start,
                    "value_type": int(value_entries[0]["value_type"]),
                    "link_offsets": sorted({int(entry["link_offset"]) for entry in value_entries}),
                    "text_offset": record_start + int(value_entries[0]["text_local_offset"]),
                    "text_local_offset": int(value_entries[0]["text_local_offset"]),
                    "text_length_including_nul": int(value_entries[0]["text_length_including_nul"]),
                    "text": str(value_entries[0]["text"]),
                    "hash_entry_indices": [int(entry["entry_index"]) for entry in value_entries],
                    "hash_entry_local_offsets": [int(entry["local_offset"]) for entry in value_entries],
                }
            )

    short_name_field = None
    first_payload_start = min([table_start, *value_starts]) if value_starts else table_start
    if first_payload_start == 0x16 and len(blob) >= 0x16:
        name_field = blob[0x12:0x16]
        name_word, reserved_word = struct.unpack_from("<HH", blob, 0x12)
        if reserved_word == 0:
            short_name_field = {
                "kind": "class3_short_name_field",
                "offset": record_start + 0x12,
                "local_offset": 0x12,
                "end": record_start + 0x16,
                "end_local_offset": 0x16,
                "size": 4,
                "name_word": name_word,
                "reserved_word": reserved_word,
                "bytes_hex": name_field.hex(),
            }

    segments = [
        {
            "kind": "class3_common_native_header",
            "offset": record_start,
            "local_offset": 0,
            "end": record_start + 0x12,
            "end_local_offset": 0x12,
            "size": 0x12,
        },
        {
            "kind": "class3_name_hash_table",
            "offset": record_start + table_start,
            "local_offset": table_start,
            "end": record_start + table_start + len(entries) * entry_size,
            "end_local_offset": table_start + len(entries) * entry_size,
            "size": len(entries) * entry_size,
            "entry_count": len(entries),
        },
    ]
    if short_name_field:
        segments.append(short_name_field)
    segments.extend(value_records)
    segments.sort(key=lambda segment: (int(segment["local_offset"]), int(segment["end_local_offset"])))

    value_text_offsets = {int(entry["text_local_offset"]) for entry in entries}
    extra_hash_table_entries = []
    post_table_reference_tails = []
    post_table_value_prefixes = []
    zero_padding_segments = []

    def append_gap_segment(segment: dict[str, object]) -> None:
        segments.append(segment)
        segments.sort(key=lambda item: (int(item["local_offset"]), int(item["end_local_offset"])))

    def classify_gap(gap_start: int, gap_end: int) -> None:
        if gap_start >= gap_end:
            return
        gap = blob[gap_start:gap_end]
        if all(byte == 0 for byte in gap):
            segment = {
                "kind": "class3_zero_padding",
                "offset": record_start + gap_start,
                "local_offset": gap_start,
                "end": record_start + gap_end,
                "end_local_offset": gap_end,
                "size": gap_end - gap_start,
            }
            zero_padding_segments.append(segment)
            append_gap_segment(segment)
            return

        if gap_start == table_start + len(entries) * entry_size and len(gap) >= 4:
            cursor = gap_start
            extra_entries = []
            while cursor + 4 <= gap_end:
                hash_word, text_local_offset = struct.unpack_from("<HH", blob, cursor)
                if text_local_offset not in value_text_offsets:
                    break
                extra_entries.append(
                    {
                        "entry_offset": record_start + cursor,
                        "local_offset": cursor,
                        "hash_word": hash_word,
                        "text_offset": record_start + text_local_offset,
                        "text_local_offset": text_local_offset,
                    }
                )
                cursor += 4
            if extra_entries and all(byte == 0 for byte in blob[cursor:gap_end]):
                segment = {
                    "kind": "class3_extra_hash_table_entries",
                    "offset": record_start + gap_start,
                    "local_offset": gap_start,
                    "end": record_start + gap_end,
                    "end_local_offset": gap_end,
                    "size": gap_end - gap_start,
                    "entry_count": len(extra_entries),
                    "entries": extra_entries,
                    "trailing_zero_bytes": gap_end - cursor,
                }
                extra_hash_table_entries.append(segment)
                append_gap_segment(segment)
                return

        if gap_start == table_start + len(entries) * entry_size and len(gap) >= 8 and len(gap) % 2 == 0:
            prefix_word, zero_word = struct.unpack_from("<HH", blob, gap_start)
            cursor = gap_start + 4
            references = []
            while cursor + 4 <= gap_end and blob[cursor:cursor + 2] == b"\x14\x00":
                target_key = struct.unpack_from("<H", blob, cursor + 2)[0]
                target = key_to_record.get(target_key)
                if target is None:
                    break
                references.append(
                    {
                        "offset": record_start + cursor,
                        "local_offset": cursor,
                        "target_key": target_key,
                        "target_record_number": target["record_number"],
                        "target_class_id": target["class_id"],
                        "target_class_name": target["class_name"],
                        "target_object_id": target["object_id"],
                        "target_name": target["name"],
                    }
                )
                cursor += 4
            if (
                prefix_word == object_id
                and zero_word == 0
                and references
                and all(byte == 0 for byte in blob[cursor:gap_end])
            ):
                segment = {
                    "kind": "class3_post_table_reference_tail",
                    "offset": record_start + gap_start,
                    "local_offset": gap_start,
                    "end": record_start + gap_end,
                    "end_local_offset": gap_end,
                    "size": gap_end - gap_start,
                    "prefix_word": prefix_word,
                    "zero_word": zero_word,
                    "references": references,
                    "trailing_zero_bytes": gap_end - cursor,
                }
                post_table_reference_tails.append(segment)
                append_gap_segment(segment)
                return

        previous_segments = [
            segment for segment in segments if int(segment["end_local_offset"]) <= gap_start
        ]
        next_segments = [
            segment for segment in segments if int(segment["local_offset"]) >= gap_end
        ]
        previous_kind = str(previous_segments[-1]["kind"]) if previous_segments else ""
        next_kind = str(next_segments[0]["kind"]) if next_segments else ""
        if (
            previous_kind == "class3_name_hash_table"
            and next_kind == "class3_typed_string_value_record"
            and 0 < gap_end - gap_start <= 16
            and (gap_end - gap_start) % 2 == 0
        ):
            segment = {
                "kind": "class3_post_table_value_prefix",
                "offset": record_start + gap_start,
                "local_offset": gap_start,
                "end": record_start + gap_end,
                "end_local_offset": gap_end,
                "size": gap_end - gap_start,
                "words": [
                    struct.unpack_from("<H", blob, local)[0]
                    for local in range(gap_start, gap_end, 2)
                ],
            }
            post_table_value_prefixes.append(segment)
            append_gap_segment(segment)

    cursor = 0
    for occupied_start, occupied_end in merge_ranges(
        (int(segment["local_offset"]), int(segment["end_local_offset"]))
        for segment in segments
    ):
        if cursor < occupied_start:
            classify_gap(cursor, occupied_start)
        cursor = max(cursor, occupied_end)
    if cursor < len(blob):
        classify_gap(cursor, len(blob))
    segments.sort(key=lambda segment: (int(segment["local_offset"]), int(segment["end_local_offset"])))

    return {
        "kind": "class3_name_hash_table",
        "decoded": True,
        "entry_start": table_start,
        "entry_start_from_header_0x10_minus_6": table_start,
        "entry_size": entry_size,
        "entry_count": len(entries),
        "entry_count_from_object_id": object_id,
        "entries_end": table_start + len(entries) * entry_size,
        "segments": segments,
        "short_name_field": short_name_field,
        "value_records": value_records,
        "extra_hash_table_entries": extra_hash_table_entries,
        "post_table_reference_tails": post_table_reference_tails,
        "post_table_value_prefixes": post_table_value_prefixes,
        "zero_padding_segments": zero_padding_segments,
        "entries": entries,
    }


def decode_self_reference_offset_tables(
    row: dict[str, object],
    blob: bytes,
    record_start: int,
) -> list[dict[str, object]]:
    tables = []
    record_number = int(row["record_number"])
    for marker in row.get("record_reference_markers", []):
        if not isinstance(marker, dict):
            continue
        if int(marker.get("target_record_number", -1)) != record_number:
            continue
        local = int(marker["local_offset"])
        if local + 8 > len(blob):
            continue
        table_start, first_body_pointer = struct.unpack_from("<HH", blob, local + 4)
        # In CATALIST page/background records, the self-reference header stores a
        # pointer seven bytes into the first body item. The table immediately
        # before that body is a sequence of 6-byte local-offset entries.
        table_end = first_body_pointer - 7
        if table_start < local + 4 or table_end < table_start or table_end > len(blob):
            continue
        table_size = table_end - table_start
        if table_size == 0 or table_size % 6:
            continue
        entries = []
        for entry_local in range(table_start, table_end, 6):
            entry_id, entry_state, entry_pointer = struct.unpack_from("<HHH", blob, entry_local)
            linked_object = None
            if entry_pointer:
                for obj in row.get("embedded_native_objects", []):
                    if not isinstance(obj, dict):
                        continue
                    if int(obj.get("object_id", -1)) != entry_id:
                        continue
                    object_start = int(obj["object_local_offset"])
                    text_start = int(obj["text_value_local_offset"])
                    if object_start <= entry_pointer <= text_start:
                        linked_object = {
                            "object_format": obj.get("object_format"),
                            "object_local_offset": object_start,
                            "object_offset": record_start + object_start,
                            "object_class_id": obj.get("object_class_id"),
                            "object_class_name": obj.get("object_class_name"),
                            "object_id": obj.get("object_id"),
                            "text_value_local_offset": text_start,
                            "text_value_offset": obj.get("text_value_offset"),
                            "text_preview": obj.get("text_preview"),
                        }
                        break
            child_object_header = None
            child_start = entry_pointer - 10
            if entry_pointer and child_start >= 0 and child_start + 12 <= len(blob):
                first_word, class_id, object_id, object_flags = struct.unpack_from("<HHHH", blob, child_start)
                if object_id == entry_id and class_id in RUNTIME_OBJECT_CLASS_NAMES:
                    child_object_header = {
                        "object_header_offset": record_start + child_start,
                        "object_header_local_offset": child_start,
                        "first_word": first_word,
                        "object_class_id": class_id,
                        "object_class_name": RUNTIME_OBJECT_CLASS_NAMES[class_id],
                        "object_id": object_id,
                        "object_flags": object_flags,
                        "word_before_entry_pointer": struct.unpack_from("<H", blob, entry_pointer - 2)[0],
                        "entry_pointer_relative_offset": 10,
                    }
            entries.append(
                {
                    "entry_offset": record_start + entry_local,
                    "entry_local_offset": entry_local,
                    "entry_id": entry_id,
                    "entry_id_runtime_name": RUNTIME_OBJECT_CLASS_NAMES.get(entry_id, ""),
                    "entry_state": entry_state,
                    "entry_pointer_local_offset": entry_pointer,
                    "entry_pointer_offset": record_start + entry_pointer if entry_pointer < len(blob) else None,
                    "entry_pointer_points_inside_record": entry_pointer < len(blob),
                    "child_object_header": child_object_header,
                    "linked_embedded_text_object": linked_object,
                }
            )
        if not any(entry["child_object_header"] or entry["linked_embedded_text_object"] for entry in entries):
            continue
        tables.append(
            {
                "kind": "self_reference_offset_table",
                "self_reference_marker_offset": record_start + local,
                "self_reference_marker_local_offset": local,
                "table_start": record_start + table_start,
                "table_start_local_offset": table_start,
                "table_end": record_start + table_end,
                "table_end_local_offset": table_end,
                "table_size": table_size,
                "entry_size": 6,
                "entry_count": len(entries),
                "first_body_pointer_local_offset": first_body_pointer,
                "first_body_starts_at_pointer_minus_7": table_end,
                "entries": entries,
            }
        )
    return tables


def decode_page_background_offset_vectors(
    row: dict[str, object],
    blob: bytes,
    record_start: int,
) -> list[dict[str, object]]:
    vectors = []
    header = row.get("header")
    if not isinstance(header, dict):
        return vectors
    key = int(header.get("key", -1))
    occupied = merge_ranges(
        [
            (int(table["self_reference_marker_local_offset"]), int(table["table_end_local_offset"]))
            for table in row.get("self_reference_offset_tables", [])
            if isinstance(table, dict)
        ]
    )

    def overlaps_occupied(start: int, end: int) -> bool:
        return any(start < occupied_end and end > occupied_start for occupied_start, occupied_end in occupied)

    for local in range(0, max(0, len(blob) - 22), 2):
        if overlaps_occupied(local, local + 20):
            continue
        first_pointer, entry_size, allocated_count, current_count, payload_word, zero_word = struct.unpack_from(
            "<HHHHHH", blob, local
        )
        marker_local = local + 12
        if (
            entry_size != 6
            or allocated_count == 0
            or current_count > allocated_count
            or allocated_count > 512
            or zero_word != 0
            or marker_local + 10 > len(blob)
        ):
            continue
        marker_word, marker_key, marker_table_start, first_body_pointer = struct.unpack_from("<HHHH", blob, marker_local)
        offsets_count = allocated_count
        offsets_start = marker_local + 10
        offsets_end = offsets_start + offsets_count * 2
        if (
            marker_word != 0x0014
            or marker_key != key
            or offsets_end > len(blob)
            or struct.unpack_from("<H", blob, marker_local + 8)[0] != 0
        ):
            continue
        offsets = [
            struct.unpack_from("<H", blob, offset)[0]
            for offset in range(offsets_start, offsets_end, 2)
        ]
        nonzero_offsets = [offset for offset in offsets if offset]
        if not nonzero_offsets:
            continue
        if all(offset >= len(blob) for offset in nonzero_offsets):
            continue
        first_zero_index = next((idx for idx, offset in enumerate(offsets) if offset == 0), len(offsets))
        if any(offset != 0 for offset in offsets[first_zero_index:]):
            continue
        if any(left > right for left, right in zip(nonzero_offsets, nonzero_offsets[1:])):
            continue
        if first_pointer < marker_local or first_pointer > offsets_end + 8:
            continue
        end = offsets_end
        trailer = None
        if end + 6 <= len(blob):
            trailer_pointer, trailer_zero, trailer_flags = struct.unpack_from("<HHH", blob, end)
            if trailer_zero == 0 and trailer_flags & 0x8000:
                trailer = {
                    "offset": record_start + end,
                    "local_offset": end,
                    "pointer_word": trailer_pointer,
                    "zero_word": trailer_zero,
                    "flags_word": trailer_flags,
                }
                end += 6
        if overlaps_occupied(local, end):
            continue
        vectors.append(
            {
                "kind": "page_background_offset_vector",
                "offset": record_start + local,
                "local_offset": local,
                "end": record_start + end,
                "end_local_offset": end,
                "size": end - local,
                "first_pointer_word": first_pointer,
                "entry_size_word": entry_size,
                "allocated_count": allocated_count,
                "current_count": current_count,
                "payload_word": payload_word,
                "marker_offset": record_start + marker_local,
                "marker_local_offset": marker_local,
                "marker_table_start_word": marker_table_start,
                "first_body_pointer_word": first_body_pointer,
                "offsets_start": record_start + offsets_start,
                "offsets_local_start": offsets_start,
                "offset_count": offsets_count,
                "nonzero_offset_count": len(nonzero_offsets),
                "offsets": offsets,
                "trailer": trailer,
            }
        )
    vectors.sort(key=lambda vector: (int(vector["local_offset"]), int(vector["end_local_offset"])))
    merged_vectors = []
    cursor = -1
    for vector in vectors:
        start = int(vector["local_offset"])
        end = int(vector["end_local_offset"])
        if start < cursor:
            continue
        merged_vectors.append(vector)
        cursor = end
    return merged_vectors


def decode_terminal_child_pointer_tables(
    row: dict[str, object],
    blob: bytes,
    record_start: int,
) -> list[dict[str, object]]:
    tables = []
    search_start = max(0, len(blob) - 0x400)
    for local in range(search_start, max(search_start, len(blob) - 12), 2):
        prefix_word, entry_count, zero_word = struct.unpack_from("<HHH", blob, local)
        if entry_count == 0 or entry_count > 512 or zero_word != 0:
            continue
        entries_start = local + 6
        entries_end = entries_start + entry_count * 6
        if entries_end > len(blob):
            continue
        trailing = blob[entries_end:]
        if trailing and any(byte != 0 for byte in trailing):
            continue
        entries = []
        linked = 0
        for entry_local in range(entries_start, entries_end, 6):
            pointer_word, entry_id, entry_state = struct.unpack_from("<HHH", blob, entry_local)
            child = None
            child_start = pointer_word - 10
            if pointer_word and 0 <= child_start and child_start + 8 <= len(blob):
                first_word, class_id, object_id, object_flags = struct.unpack_from("<HHHH", blob, child_start)
                if class_id in RUNTIME_OBJECT_CLASS_NAMES:
                    child = {
                        "object_header_offset": record_start + child_start,
                        "object_header_local_offset": child_start,
                        "first_word": first_word,
                        "object_class_id": class_id,
                        "object_class_name": RUNTIME_OBJECT_CLASS_NAMES[class_id],
                        "object_id": object_id,
                        "object_flags": object_flags,
                        "entry_pointer_relative_offset": 10,
                    }
                    linked += 1
            entries.append(
                {
                    "entry_offset": record_start + entry_local,
                    "entry_local_offset": entry_local,
                    "entry_pointer_local_offset": pointer_word,
                    "entry_pointer_offset": record_start + pointer_word if pointer_word < len(blob) else None,
                    "entry_id": entry_id,
                    "entry_state": entry_state,
                    "child_object_header": child,
                }
            )
        if linked != entry_count:
            continue
        tables.append(
            {
                "kind": "terminal_child_pointer_table",
                "offset": record_start + local,
                "local_offset": local,
                "end": record_start + len(blob),
                "end_local_offset": len(blob),
                "size": len(blob) - local,
                "entry_start": record_start + entries_start,
                "entry_start_local_offset": entries_start,
                "entry_end": record_start + entries_end,
                "entry_end_local_offset": entries_end,
                "prefix_word": prefix_word,
                "entry_count": entry_count,
                "entry_size": 6,
                "trailing_zero_bytes": len(trailing),
                "entries": entries,
            }
        )
    tables.sort(key=lambda table: (int(table["local_offset"]), -int(table["entry_count"])))
    return tables[:1]


def decode_self_reference_child_object_spans(
    row: dict[str, object],
    blob: bytes,
    record_start: int,
) -> list[dict[str, object]]:
    children: dict[tuple[int, int, int], dict[str, object]] = {}
    for table in row.get("self_reference_offset_tables", []):
        if not isinstance(table, dict):
            continue
        for entry in table.get("entries", []):
            if not isinstance(entry, dict):
                continue
            child = entry.get("child_object_header")
            if not isinstance(child, dict):
                continue
            key = (
                int(child["object_header_local_offset"]),
                int(child["object_class_id"]),
                int(child["object_id"]),
            )
            children[key] = {
                "object_header_local_offset": int(child["object_header_local_offset"]),
                "object_header_offset": int(child["object_header_offset"]),
                "object_class_id": int(child["object_class_id"]),
                "object_class_name": child["object_class_name"],
                "object_id": int(child["object_id"]),
                "object_flags": int(child["object_flags"]),
                "first_word": int(child["first_word"]),
                "entry_pointer_local_offset": int(entry["entry_pointer_local_offset"]),
                "entry_pointer_offset": int(entry["entry_pointer_offset"]),
                "entry_state": int(entry["entry_state"]),
                "source_table_marker_local_offset": int(table["self_reference_marker_local_offset"]),
                "source_table_entry_local_offset": int(entry["entry_local_offset"]),
                "source_kind": "self_reference_offset_table",
            }
    for vector in row.get("page_background_offset_vectors", []):
        if not isinstance(vector, dict):
            continue
        for entry_index, entry_pointer in enumerate(vector.get("offsets", [])):
            if not isinstance(entry_pointer, int) or not entry_pointer:
                continue
            child_start = entry_pointer - 10
            if child_start < 0 or child_start + 10 > len(blob):
                continue
            first_word, class_id, object_id, object_flags = struct.unpack_from("<HHHH", blob, child_start)
            if class_id not in RUNTIME_OBJECT_CLASS_NAMES:
                continue
            key = (child_start, class_id, object_id)
            children.setdefault(
                key,
                {
                    "object_header_local_offset": child_start,
                    "object_header_offset": record_start + child_start,
                    "object_class_id": class_id,
                    "object_class_name": RUNTIME_OBJECT_CLASS_NAMES[class_id],
                    "object_id": object_id,
                    "object_flags": object_flags,
                    "first_word": first_word,
                    "entry_pointer_local_offset": entry_pointer,
                    "entry_pointer_offset": record_start + entry_pointer,
                    "entry_state": 0,
                    "source_table_marker_local_offset": int(vector["marker_local_offset"]),
                    "source_table_entry_local_offset": int(vector["offsets_local_start"]) + entry_index * 2,
                    "source_kind": "page_background_offset_vector",
                },
            )
    for table in row.get("terminal_child_pointer_tables", []):
        if not isinstance(table, dict):
            continue
        for entry in table.get("entries", []):
            if not isinstance(entry, dict):
                continue
            child = entry.get("child_object_header")
            if not isinstance(child, dict):
                continue
            key = (
                int(child["object_header_local_offset"]),
                int(child["object_class_id"]),
                int(child["object_id"]),
            )
            children.setdefault(
                key,
                {
                    "object_header_local_offset": int(child["object_header_local_offset"]),
                    "object_header_offset": int(child["object_header_offset"]),
                    "object_class_id": int(child["object_class_id"]),
                    "object_class_name": child["object_class_name"],
                    "object_id": int(child["object_id"]),
                    "object_flags": int(child["object_flags"]),
                    "first_word": int(child["first_word"]),
                    "entry_pointer_local_offset": int(entry["entry_pointer_local_offset"]),
                    "entry_pointer_offset": int(entry["entry_pointer_offset"]),
                    "entry_state": int(entry["entry_state"]),
                    "source_table_marker_local_offset": int(table["local_offset"]),
                    "source_table_entry_local_offset": int(entry["entry_local_offset"]),
                    "source_kind": "terminal_child_pointer_table",
                },
            )
    ordered = sorted(children.values(), key=lambda item: int(item["object_header_local_offset"]))
    spans = []
    for index, child in enumerate(ordered):
        start = int(child["object_header_local_offset"])
        next_child = ordered[index + 1] if index + 1 < len(ordered) else None
        if next_child is None:
            end = int(row["size"])
            end_reason = "native_record_end"
        else:
            end = int(next_child["object_header_local_offset"])
            end_reason = "next_source_linked_child_object_header"
        if end <= start:
            continue
        span = {
            "kind": "source_linked_child_object_span",
            "span_offset": record_start + start,
            "span_local_offset": start,
            "span_end": record_start + end,
            "span_end_local_offset": end,
            "span_size": end - start,
            "span_end_reason": end_reason,
            "object_class_id": child["object_class_id"],
            "object_class_name": child["object_class_name"],
            "object_id": child["object_id"],
            "object_flags": child["object_flags"],
            "first_word": child["first_word"],
            "entry_pointer_local_offset": child["entry_pointer_local_offset"],
            "entry_state": child["entry_state"],
            "source_table_marker_local_offset": child["source_table_marker_local_offset"],
            "source_table_entry_local_offset": child["source_table_entry_local_offset"],
            "source_kind": child["source_kind"],
        }
        if next_child is not None:
            span.update(
                {
                    "next_object_header_local_offset": end,
                    "next_object_class_id": next_child["object_class_id"],
                    "next_object_class_name": next_child["object_class_name"],
                    "next_object_id": next_child["object_id"],
                }
            )
        spans.append(span)
    return spans


def is_toolbook_text_bytes(raw: bytes) -> bool:
    return bool(raw) and all(byte in (9, 10, 13) or 32 <= byte <= 126 or byte >= 0xA0 for byte in raw)


def annotate_stored_text_capacity_tails(values: list[dict[str, object]], blob: bytes) -> int:
    matched = 0
    for value in values:
        value_pos = int(value["value_body_local_offset"])
        capacity_word = int(value["capacity_word"])
        text_start = int(value["text_local_offset"])
        text_length = int(value["text_length"])
        declared_text_end = text_start + text_length
        capacity_end = min(text_start + capacity_word, len(blob))
        if capacity_end <= declared_text_end:
            continue
        tail = blob[declared_text_end:capacity_end]
        nonzero = sum(1 for byte in tail if byte)
        printable = sum(1 for byte in tail if byte in (9, 10, 13) or 32 <= byte <= 126 or byte >= 0xA0)
        stripped_tail = tail.rstrip(b"\0")
        decoded_text = ""
        if nonzero and is_toolbook_text_bytes(stripped_tail):
            decoded_text = stripped_tail.decode("cp1252", "replace")
        if nonzero == 0:
            kind = "zero_allocated_text_tail"
        elif decoded_text:
            kind = "printable_allocated_text_tail"
        else:
            kind = "mixed_allocated_text_tail"
        value["capacity_tail"] = {
            "kind": kind,
            "tail_offset": int(value["value_body_offset"]) + declared_text_end - value_pos,
            "tail_local_offset": declared_text_end,
            "tail_size": len(tail),
            "tail_end_offset": int(value["value_body_offset"]) + capacity_end - value_pos,
            "tail_end_local_offset": capacity_end,
            "tail_nonzero_bytes": nonzero,
            "tail_printable_bytes": printable,
            "tail_text": decoded_text,
        }
        matched += 1
    return matched


def decode_typed_text_values(blob: bytes, record_start: int) -> list[dict[str, object]]:
    candidates = []
    for pos in range(0, max(0, len(blob) - 8)):
        if blob[pos : pos + 2] != b"\x00\x00":
            continue
        capacity_word = struct.unpack_from("<H", blob, pos + 2)[0]
        text_length = struct.unpack_from("<H", blob, pos + 4)[0]
        text_start = pos + 6
        text_end = text_start + text_length
        if text_length < 2 or text_end > len(blob):
            continue
        if capacity_word < text_length or capacity_word > 0x4000:
            continue
        if capacity_word % 0x20 != 0 and capacity_word - text_length > 8:
            continue
        raw_text = blob[text_start:text_end]
        if len(raw_text.strip()) < 2 or not is_toolbook_text_bytes(raw_text):
            continue
        context_start = max(0, pos - 10)
        following_nul = text_end < len(blob) and blob[text_end] == 0
        candidates.append(
            {
                "kind": "stored_text_value",
                "value_body_offset": record_start + pos,
                "value_body_local_offset": pos,
                "context_offset": record_start + context_start,
                "context_local_offset": context_start,
                "context_hex": blob[context_start:pos].hex(),
                "capacity_word": capacity_word,
                "text_length": text_length,
                "text_offset": record_start + text_start,
                "text_local_offset": text_start,
                "following_nul": following_nul,
                "nul_offset": record_start + text_end if following_nul else None,
                "total_value_body_bytes": 6 + text_length + (1 if following_nul else 0),
                "text": raw_text.decode("cp1252", "replace"),
            }
        )
    values = []
    last_end = -1
    for candidate in sorted(candidates, key=lambda item: (int(item["value_body_local_offset"]), -int(item["text_length"]))):
        value_end = (
            int(candidate["value_body_local_offset"])
            + 6
            + int(candidate["text_length"])
            + (1 if candidate["following_nul"] else 0)
        )
        if int(candidate["value_body_local_offset"]) < last_end:
            continue
        values.append(candidate)
        last_end = value_end
    return values


def decode_inline_class11_text_values(blob: bytes, record_start: int) -> list[dict[str, object]]:
    values = []
    for object_local in range(0, max(0, len(blob) - 18), 2):
        prefix_word, class_id, object_id, flags, trailing_word = struct.unpack_from("<HHHHH", blob, object_local)
        value_pos = object_local + 10
        if class_id != 11 or value_pos + 6 > len(blob) or blob[value_pos:value_pos + 2] != b"\x00\x00":
            continue
        capacity_word, text_length = struct.unpack_from("<HH", blob, value_pos + 2)
        text_start = value_pos + 6
        text_end = text_start + text_length
        if text_length < 2 or text_end > len(blob):
            continue
        if capacity_word < text_length or capacity_word > 0x4000:
            continue
        raw_text = blob[text_start:text_end]
        if len(raw_text.strip()) < 2 or not is_toolbook_text_bytes(raw_text):
            continue
        following_nul = text_end < len(blob) and blob[text_end] == 0
        values.append(
            {
                "kind": "stored_text_value",
                "descriptor_kind": "class_11_inline_prefix_relaxed_capacity",
                "value_body_offset": record_start + value_pos,
                "value_body_local_offset": value_pos,
                "context_offset": record_start + object_local,
                "context_local_offset": object_local,
                "context_hex": blob[object_local:value_pos].hex(),
                "capacity_word": capacity_word,
                "text_length": text_length,
                "text_offset": record_start + text_start,
                "text_local_offset": text_start,
                "following_nul": following_nul,
                "nul_offset": record_start + text_end if following_nul else None,
                "total_value_body_bytes": 6 + text_length + (1 if following_nul else 0),
                "text": raw_text.decode("cp1252", "replace"),
                "object_owner": {
                    "kind": "native_object_inline_class_prefix",
                    "object_header_local_offset": object_local,
                    "object_header_offset": record_start + object_local,
                    "object_class_id": class_id,
                    "object_class_name": RUNTIME_OBJECT_CLASS_NAMES.get(class_id, "unknown"),
                    "object_id": object_id,
                    "object_flags": flags,
                    "prefix_word": prefix_word,
                    "trailing_word": trailing_word,
                },
            }
        )
    return values


def decode_extended_inline_text_values(blob: bytes, record_start: int) -> list[dict[str, object]]:
    values = []
    for pos in range(0, max(0, len(blob) - 24), 2):
        words = struct.unpack_from("<HHHHHHHHHHH", blob, pos)
        text_start = pos + 22
        text_length = words[9]
        text_end = text_start + text_length
        if (
            words[0] + 1 != text_start
            or words[1] != 0
            or words[2] != 0
            or words[3] != text_start + 2
            or words[5] != 0
            or words[6] != 0
            or words[7] < text_length
            or words[8] != 0
            or text_length < 16
            or text_end > len(blob)
        ):
            continue
        raw_text = blob[text_start:text_end]
        if len(raw_text.strip()) < 2 or not is_toolbook_text_bytes(raw_text):
            continue
        following_nul = text_end < len(blob) and blob[text_end] == 0
        values.append(
            {
                "kind": "extended_inline_text_value",
                "descriptor_kind": "extended_22_byte_text_descriptor",
                "value_body_offset": record_start + pos,
                "value_body_local_offset": pos,
                "context_offset": record_start + pos,
                "context_local_offset": pos,
                "context_hex": blob[pos:text_start].hex(),
                "capacity_word": words[7],
                "text_length": text_length,
                "text_offset": record_start + text_start,
                "text_local_offset": text_start,
                "following_nul": following_nul,
                "nul_offset": record_start + text_end if following_nul else None,
                "total_value_body_bytes": 22 + text_length + (1 if following_nul else 0),
                "text": raw_text.decode("cp1252", "replace"),
                "descriptor_words": list(words),
            }
        )
    return values


def decode_large_field_text_values(blob: bytes, record_start: int) -> list[dict[str, object]]:
    values = []
    for pos in range(0x78, max(0, len(blob) - 18)):
        words = struct.unpack_from("<HHHHHHHH", blob, pos)
        word0, word1, word2, word3, word4, word5, text_length, aux_word = words
        object_delta = 0
        object_local = 0
        first_word = 0
        class_id = 0
        object_id = 0
        flags = 0
        descriptor_pointer = 0
        text_start = pos + 16
        text_end = text_start + text_length
        descriptor_variant = ""
        total_value_body_bytes = 0
        if text_length >= 8 and text_end <= len(blob):
            for candidate_delta, end_delta in ((0x78, 8), (0x7A, 7)):
                candidate_object_local = pos - candidate_delta
                if candidate_object_local < 0 or candidate_object_local + 0x4C > len(blob):
                    continue
                candidate_first_word, candidate_class_id, candidate_object_id, candidate_flags = struct.unpack_from(
                    "<HHHH", blob, candidate_object_local
                )
                candidate_descriptor_pointer = struct.unpack_from("<H", blob, candidate_object_local + 0x4A)[0]
                if (
                    word0 == text_start - 1
                    and word1 == 0
                    and word2 == 0
                    and word3 == text_start + 2
                    and word4 == text_end + end_delta
                    and word5 == 0
                    and candidate_class_id == 10
                    and candidate_descriptor_pointer == pos + 7
                ):
                    object_delta = candidate_delta
                    object_local = candidate_object_local
                    first_word = candidate_first_word
                    class_id = candidate_class_id
                    object_id = candidate_object_id
                    flags = candidate_flags
                    descriptor_pointer = candidate_descriptor_pointer
                    descriptor_variant = f"inline_length_at_0x0c_delta_0x{candidate_delta:02x}"
                    total_value_body_bytes = 16 + text_length
                    break
        if not object_delta and pos + 18 <= len(blob):
            embedded_text_length = struct.unpack_from("<H", blob, pos + 16)[0]
            embedded_text_start = pos + 18
            embedded_text_end = embedded_text_start + embedded_text_length
            candidate_object_local = pos - 0x78
            first_child_header_local = word5 - 7
            if (
                embedded_text_length >= 8
                and embedded_text_end <= len(blob)
                and candidate_object_local >= 0
                and candidate_object_local + 0x4C <= len(blob)
                and first_child_header_local >= 0
                and first_child_header_local + 8 <= len(blob)
            ):
                candidate_first_word, candidate_class_id, candidate_object_id, candidate_flags = struct.unpack_from(
                    "<HHHH", blob, candidate_object_local
                )
                child_class_id = struct.unpack_from("<H", blob, first_child_header_local + 2)[0]
                candidate_descriptor_pointer = struct.unpack_from("<H", blob, candidate_object_local + 0x4A)[0]
                if (
                    word0 == 4
                    and word1 == pos + 17
                    and word2 == 0
                    and word3 == 0
                    and word4 == embedded_text_start + 2
                    and text_length == 0
                    and candidate_class_id == 10
                    and child_class_id in RUNTIME_OBJECT_CLASS_NAMES
                    and candidate_descriptor_pointer == pos + 9
                ):
                    object_delta = 0x78
                    object_local = candidate_object_local
                    first_word = candidate_first_word
                    class_id = candidate_class_id
                    object_id = candidate_object_id
                    flags = candidate_flags
                    descriptor_pointer = candidate_descriptor_pointer
                    text_length = embedded_text_length
                    text_start = embedded_text_start
                    text_end = embedded_text_end
                    descriptor_variant = "embedded_length_at_0x10_first_child_pointer"
                    total_value_body_bytes = 18 + text_length
        if not object_delta:
            continue
        raw_text = blob[text_start:text_end]
        if len(raw_text.strip()) < 2 or not is_toolbook_text_bytes(raw_text):
            continue
        object_name = ""
        name_local = first_word - 3
        if 0 <= name_local < len(blob):
            name_end = blob.find(b"\0", name_local, min(len(blob), name_local + 0x80))
            if name_end > name_local:
                raw_name = blob[name_local:name_end]
                if is_toolbook_text_bytes(raw_name):
                    object_name = raw_name.decode("cp1252", "replace")
        value = {
                "kind": "large_field_text_value",
                "value_body_offset": record_start + pos,
                "value_body_local_offset": pos,
                "storage_words": list(words),
                "object_to_descriptor_delta": object_delta,
                "descriptor_variant": descriptor_variant,
                "capacity_word": aux_word if descriptor_variant == "embedded_length_at_0x10_first_child_pointer" else 0,
                "text_length": text_length,
                "aux_word": aux_word,
                "text_offset": record_start + text_start,
                "text_local_offset": text_start,
                "following_nul": False,
                "nul_offset": None,
                "total_value_body_bytes": total_value_body_bytes,
                "text": raw_text.decode("cp1252", "replace"),
                "object_owner": {
                    "kind": "native_field_large_text_descriptor",
                    "object_header_local_offset": object_local,
                    "object_header_offset": record_start + object_local,
                    "object_class_id": class_id,
                    "object_class_name": RUNTIME_OBJECT_CLASS_NAMES.get(class_id, "unknown"),
                    "object_id": object_id,
                    "object_flags": flags,
                    "object_first_word": first_word,
                    "object_name": object_name,
                    "text_descriptor_pointer_word": descriptor_pointer,
                    "text_descriptor_pointer_local_offset": object_local + 0x4A,
                },
            }
        if descriptor_variant == "embedded_length_at_0x10_first_child_pointer":
            capacity_end = min(text_start + aux_word, len(blob))
            if capacity_end > text_end:
                tail = blob[text_end:capacity_end]
                nonzero = sum(1 for byte in tail if byte)
                printable = sum(1 for byte in tail if byte in (9, 10, 13) or 32 <= byte <= 126 or byte >= 0xA0)
                stripped_tail = tail.rstrip(b"\0")
                decoded_text = ""
                if nonzero and is_toolbook_text_bytes(stripped_tail):
                    decoded_text = stripped_tail.decode("cp1252", "replace")
                if nonzero == 0:
                    kind = "zero_allocated_text_tail"
                elif decoded_text:
                    kind = "printable_allocated_text_tail"
                else:
                    kind = "mixed_allocated_text_tail"
                value["capacity_tail"] = {
                    "kind": kind,
                    "tail_offset": record_start + text_end,
                    "tail_local_offset": text_end,
                    "tail_size": len(tail),
                    "tail_end_offset": record_start + capacity_end,
                    "tail_end_local_offset": capacity_end,
                    "tail_nonzero_bytes": nonzero,
                    "tail_printable_bytes": printable,
                    "tail_text": decoded_text,
                }
        values.append(value)
    deduped = {}
    variant_priority = {
        "embedded_length_at_0x10_first_child_pointer": 0,
        "inline_length_at_0x0c_delta_0x78": 1,
        "inline_length_at_0x0c_delta_0x7a": 1,
    }
    for value in values:
        owner = value.get("object_owner")
        key = int(owner["object_header_local_offset"]) if isinstance(owner, dict) else int(value["value_body_local_offset"])
        current = deduped.get(key)
        if current is None or (
            variant_priority.get(str(value.get("descriptor_variant")), 9),
            int(value["value_body_local_offset"]),
        ) < (
            variant_priority.get(str(current.get("descriptor_variant")), 9),
            int(current["value_body_local_offset"]),
        ):
            deduped[key] = value
    return sorted(deduped.values(), key=lambda item: int(item["text_offset"]))


def decode_field_hotword_run_tables(row: dict[str, object], blob: bytes, record_start: int) -> list[dict[str, object]]:
    child_headers_by_pointer = {}
    for table in row.get("self_reference_offset_tables", []):
        if not isinstance(table, dict):
            continue
        for entry in table.get("entries", []):
            if not isinstance(entry, dict):
                continue
            child = entry.get("child_object_header")
            if not isinstance(child, dict):
                continue
            child_headers_by_pointer[int(child["object_header_local_offset"]) + 10] = child

    tables = []
    for value in row.get("typed_text_values", []):
        if not isinstance(value, dict) or value.get("kind") != "stored_text_value":
            continue
        owner = value.get("object_owner")
        tail = value.get("capacity_tail")
        if not isinstance(owner, dict) or not isinstance(tail, dict):
            continue
        if owner.get("object_class_id") != 10:
            continue
        table_start = int(tail["tail_end_local_offset"])
        if table_start + 15 > len(blob):
            continue
        first_child_state_pointer = struct.unpack_from("<H", blob, table_start)[0]
        header_zero_0 = struct.unpack_from("<H", blob, table_start + 2)[0]
        row_capacity_plus_one = struct.unpack_from("<H", blob, table_start + 4)[0]
        active_row_count_word = struct.unpack_from("<H", blob, table_start + 6)[0]
        header_zero_1 = struct.unpack_from("<H", blob, table_start + 8)[0]
        header_one = struct.unpack_from("<H", blob, table_start + 10)[0]
        header_zero_2 = struct.unpack_from("<H", blob, table_start + 12)[0]
        header_trailing_zero = blob[table_start + 14]
        row_count = row_capacity_plus_one - 1
        table_end = table_start + 15 + row_count * 7
        if (
            row_capacity_plus_one < 2
            or row_capacity_plus_one > 0x400
            or active_row_count_word > row_count
            or table_end > len(blob)
            or header_zero_0
            or header_zero_1
            or header_zero_2
            or header_one != 1
            or header_trailing_zero
        ):
            continue
        rows = []
        linked_rows = 0
        all_trailing_zero = True
        monotonic_prefix_row_count = row_count
        last_text_offset = -1
        for index in range(row_count):
            row_local = table_start + 15 + index * 7
            text_offset = struct.unpack_from("<H", blob, row_local)[0]
            row_state = struct.unpack_from("<H", blob, row_local + 2)[0]
            child_pointer = struct.unpack_from("<H", blob, row_local + 4)[0]
            trailing = blob[row_local + 6]
            all_trailing_zero = all_trailing_zero and trailing == 0
            if text_offset < last_text_offset and monotonic_prefix_row_count == row_count:
                monotonic_prefix_row_count = index
            last_text_offset = text_offset
        active_row_count = min(active_row_count_word, monotonic_prefix_row_count)
        for index in range(row_count):
            row_local = table_start + 15 + index * 7
            text_offset = struct.unpack_from("<H", blob, row_local)[0]
            row_state = struct.unpack_from("<H", blob, row_local + 2)[0]
            child_pointer = struct.unpack_from("<H", blob, row_local + 4)[0]
            trailing = blob[row_local + 6]
            linked_child = child_headers_by_pointer.get(child_pointer)
            if index < active_row_count and child_pointer and linked_child is None:
                linked_rows = -1
            elif index < active_row_count and linked_child is not None:
                linked_rows += 1
            rows.append(
                {
                    "row_index": index,
                    "row_offset": record_start + row_local,
                    "row_local_offset": row_local,
                    "text_offset_in_allocated_field": text_offset,
                    "row_state": row_state,
                    "child_pointer_local_offset": child_pointer,
                    "trailing_byte": trailing,
                    "active": index < active_row_count,
                    "linked_child_object_header": linked_child,
                }
            )
        if not all_trailing_zero or linked_rows < 0:
            continue
        first_child = child_headers_by_pointer.get(first_child_state_pointer + 3)
        if first_child is None:
            continue
        tables.append(
            {
                "kind": "field_hotword_run_table",
                "table_offset": record_start + table_start,
                "table_local_offset": table_start,
                "table_end": record_start + table_end,
                "table_end_local_offset": table_end,
                "table_size": table_end - table_start,
                "header_size": 15,
                "row_size": 7,
                "first_child_state_pointer_local_offset": first_child_state_pointer,
                "first_child_object_header": first_child,
                "row_capacity_plus_one": row_capacity_plus_one,
                "row_count": row_count,
                "active_row_count_word": active_row_count_word,
                "monotonic_prefix_row_count": monotonic_prefix_row_count,
                "active_row_count": active_row_count,
                "linked_active_rows": linked_rows,
                "storage_text_value_local_offset": value.get("value_body_local_offset"),
                "storage_text_length": value.get("text_length"),
                "storage_capacity_word": value.get("capacity_word"),
                "rows": rows,
            }
        )
    return tables


def decode_page_background_payload(row: dict[str, object], blob: bytes, record_start: int) -> dict[str, object]:
    segments: list[dict[str, object]] = []

    def add_segment(kind: str, start: int, end: int, **extra: object) -> None:
        if not (0 <= start < end <= len(blob)):
            return
        segment = {
            "kind": kind,
            "offset": record_start + start,
            "local_offset": start,
            "end": record_start + end,
            "end_local_offset": end,
            "size": end - start,
        }
        segment.update(extra)
        segments.append(segment)

    add_segment("page_background_common_native_header", 0, min(0x12, len(blob)))
    if len(blob) > 0x12:
        add_segment("page_background_name_field", 0x12, min(0x32, len(blob)))

    for table in row.get("self_reference_offset_tables", []):
        if not isinstance(table, dict):
            continue
        marker_start = int(table["self_reference_marker_local_offset"])
        add_segment(
            "page_background_self_reference_marker",
            marker_start,
            marker_start + 8,
            table_start_local_offset=int(table["table_start_local_offset"]),
            table_end_local_offset=int(table["table_end_local_offset"]),
        )
        table_start = int(table["table_start_local_offset"])
        if marker_start + 8 < table_start:
            add_segment(
                "page_background_self_reference_table_descriptor_tail",
                marker_start + 8,
                table_start,
                words=[
                    struct.unpack_from("<H", blob, word_offset)[0]
                    for word_offset in range(marker_start + 8, table_start, 2)
                ],
            )
        add_segment(
            "page_background_self_reference_offset_table",
            table_start,
            int(table["table_end_local_offset"]),
            entry_count=int(table["entry_count"]),
            entry_size=int(table["entry_size"]),
        )

    for vector in row.get("page_background_offset_vectors", []):
        if not isinstance(vector, dict):
            continue
        add_segment(
            "page_background_offset_vector",
            int(vector["local_offset"]),
            int(vector["end_local_offset"]),
            allocated_count=int(vector["allocated_count"]),
            current_count=int(vector["current_count"]),
            offset_count=int(vector["offset_count"]),
            nonzero_offset_count=int(vector["nonzero_offset_count"]),
        )

    for table in row.get("terminal_child_pointer_tables", []):
        if not isinstance(table, dict):
            continue
        add_segment(
            "page_background_terminal_child_pointer_table",
            int(table["local_offset"]),
            int(table["end_local_offset"]),
            entry_count=int(table["entry_count"]),
            entry_size=int(table["entry_size"]),
            trailing_zero_bytes=int(table["trailing_zero_bytes"]),
        )

    for value in row.get("typed_text_values", []):
        if not isinstance(value, dict):
            continue
        value_start = int(value["value_body_local_offset"])
        value_end = value_start + int(value.get("total_value_body_bytes", 0))
        tail = value.get("capacity_tail")
        if isinstance(tail, dict):
            value_end = max(value_end, int(tail["tail_end_local_offset"]))
        elif value.get("kind") == "stored_text_value":
            text_start = int(value["text_local_offset"])
            value_end = max(value_end, text_start + int(value.get("capacity_word", 0)))
        add_segment(
            "page_background_text_value_allocation",
            value_start,
            min(value_end, len(blob)),
            text_local_offset=int(value["text_local_offset"]),
            text_length=int(value["text_length"]),
            value_kind=str(value.get("kind", "")),
        )

    for obj in row.get("embedded_native_objects", []):
        if not isinstance(obj, dict):
            continue
        object_start = int(obj.get("object_local_offset", -1))
        text_start = int(obj.get("text_value_local_offset", -1))
        if object_start >= 0 and text_start > object_start:
            add_segment(
                "page_background_embedded_text_object_prefix",
                object_start,
                text_start,
                object_format=str(obj.get("object_format", "")),
                object_class_id=int(obj.get("object_class_id", 0)),
                object_class_name=str(obj.get("object_class_name", "")),
                object_id=int(obj.get("object_id", 0)),
            )

    for table in row.get("field_hotword_run_tables", []):
        if not isinstance(table, dict):
            continue
        add_segment(
            "page_background_field_hotword_run_table",
            int(table["table_local_offset"]),
            int(table["table_end_local_offset"]),
            row_count=int(table["row_count"]),
            active_row_count=int(table["active_row_count"]),
        )

    for span in row.get("self_reference_child_object_spans", []):
        if not isinstance(span, dict):
            continue
        add_segment(
            "page_background_child_object_span",
            int(span["span_local_offset"]),
            int(span["span_end_local_offset"]),
            span_end_reason=str(span["span_end_reason"]),
            object_class_id=int(span["object_class_id"]),
            object_class_name=str(span["object_class_name"]),
            object_id=int(span["object_id"]),
        )

    post_name_anchor_starts = [
        int(segment["local_offset"])
        for segment in segments
        if int(segment["local_offset"]) >= 0x32 and segment["kind"] not in {
            "page_background_common_native_header",
            "page_background_name_field",
        }
    ]
    control_end = min(post_name_anchor_starts) if post_name_anchor_starts else len(blob)
    if (
        len(blob) >= 0x34
        and 0x32 < control_end
        and blob[0x32:0x34] == b"\x14\x00"
        and control_end <= len(blob)
    ):
        add_segment(
            "page_background_control_stream",
            0x32,
            control_end,
            first_words=[
                struct.unpack_from("<H", blob, word_offset)[0]
                for word_offset in range(0x32, min(control_end, 0x32 + 16), 2)
            ],
        )

    preliminary_ranges = merge_ranges(
        (int(segment["local_offset"]), int(segment["end_local_offset"]))
        for segment in segments
        if int(segment["end_local_offset"]) > int(segment["local_offset"])
    )
    cursor = 0
    for occupied_start, occupied_end in preliminary_ranges:
        if cursor < occupied_start:
            previous_segments = [
                segment for segment in segments if int(segment["end_local_offset"]) <= cursor
            ]
            next_segments = [
                segment for segment in segments if int(segment["local_offset"]) >= occupied_start
            ]
            previous_kind = str(previous_segments[-1]["kind"]) if previous_segments else ""
            next_kind = str(next_segments[0]["kind"]) if next_segments else ""
            gap_size = occupied_start - cursor
            gap_words = [
                struct.unpack_from("<H", blob, word_offset)[0]
                for word_offset in range(cursor, occupied_start, 2)
            ] if gap_size % 2 == 0 else []
            if (
                gap_size <= 32
                and gap_size % 2 == 0
                and next_kind == "page_background_child_object_span"
                and occupied_start - 4 in gap_words
                and occupied_start + 7 in gap_words
            ):
                add_segment(
                    "page_background_pre_child_descriptor",
                    cursor,
                    occupied_start,
                    previous_segment_kind=previous_kind,
                    next_segment_kind=next_kind,
                    words=gap_words,
                    next_child_local_offset=occupied_start,
                )
            elif (
                gap_size <= 14
                and gap_size % 2 == 0
                and next_kind in {
                    "page_background_embedded_text_object_prefix",
                    "page_background_text_value_allocation",
                    "page_background_child_object_span",
                }
            ):
                add_segment(
                    "page_background_link_tail",
                    cursor,
                    occupied_start,
                    previous_segment_kind=previous_kind,
                    next_segment_kind=next_kind,
                    words=gap_words,
                )
            elif gap_size == 1 and blob[cursor] == 0:
                add_segment(
                    "page_background_zero_alignment_byte",
                    cursor,
                    occupied_start,
                    previous_segment_kind=previous_kind,
                    next_segment_kind=next_kind,
                )
        cursor = max(cursor, occupied_end)

    strong_ranges = merge_ranges(
        (int(segment["local_offset"]), int(segment["end_local_offset"]))
        for segment in segments
        if int(segment["end_local_offset"]) > int(segment["local_offset"])
    )
    bounded_fragments = []
    cursor = 0
    for occupied_start, occupied_end in strong_ranges:
        if cursor < occupied_start:
            previous_kind = ""
            next_kind = ""
            previous_segments = [
                segment for segment in segments if int(segment["end_local_offset"]) <= cursor
            ]
            next_segments = [
                segment for segment in segments if int(segment["local_offset"]) >= occupied_start
            ]
            if previous_segments:
                previous_kind = str(previous_segments[-1]["kind"])
            if next_segments:
                next_kind = str(next_segments[0]["kind"])
            fragment = {
                "kind": "page_background_bounded_payload_fragment",
                "offset": record_start + cursor,
                "local_offset": cursor,
                "end": record_start + occupied_start,
                "end_local_offset": occupied_start,
                "size": occupied_start - cursor,
                "previous_segment_kind": previous_kind,
                "next_segment_kind": next_kind,
            }
            bounded_fragments.append(fragment)
            segments.append(fragment)
        cursor = max(cursor, occupied_end)
    if cursor < len(blob):
        previous_segments = [
            segment for segment in segments if int(segment["end_local_offset"]) <= cursor
        ]
        previous_kind = str(previous_segments[-1]["kind"]) if previous_segments else ""
        fragment = {
            "kind": "page_background_bounded_payload_fragment",
            "offset": record_start + cursor,
            "local_offset": cursor,
            "end": record_start + len(blob),
            "end_local_offset": len(blob),
            "size": len(blob) - cursor,
            "previous_segment_kind": previous_kind,
            "next_segment_kind": "native_record_end",
        }
        bounded_fragments.append(fragment)
        segments.append(fragment)

    return {
        "kind": "page_background_payload",
        "segments": sorted(segments, key=lambda item: (int(item["local_offset"]), int(item["end_local_offset"]))),
        "bounded_payload_fragments": bounded_fragments,
    }


def decode_book_payload(row: dict[str, object], blob: bytes, record_start: int) -> dict[str, object]:
    segments = []
    common_native_header = None
    if len(blob) >= 0x12:
        (
            key,
            declared_body_length,
            aux_length_0,
            aux_length_1,
            flags_word,
            type_word,
            class_id,
            object_id,
            owner_or_reserved,
        ) = struct.unpack_from("<HHHHHHHHH", blob, 0)
        common_native_header = {
            "kind": "book_common_native_record_header",
            "offset": record_start,
            "local_offset": 0,
            "end": record_start + 0x12,
            "end_local_offset": 0x12,
            "size": 0x12,
            "key": key,
            "declared_body_length": declared_body_length,
            "aux_length_0": aux_length_0,
            "aux_length_1": aux_length_1,
            "child_count_or_flags": flags_word & 0x00FF,
            "status_flags": flags_word >> 8,
            "type_word": type_word,
            "class_id": class_id,
            "object_id": object_id,
            "owner_or_reserved": owner_or_reserved,
        }
        segments.append(common_native_header)
    reference_blocks = []
    markers = sorted(
        (
            marker
            for marker in row.get("record_reference_markers", [])
            if isinstance(marker, dict) and 0 <= int(marker.get("local_offset", -1)) <= len(blob) - 4
        ),
        key=lambda marker: int(marker["local_offset"]),
    )
    block = []
    previous_local = -8
    for marker in markers:
        local = int(marker["local_offset"])
        if block and local != previous_local + 4:
            block_start = int(block[0]["local_offset"])
            block_end = int(block[-1]["local_offset"]) + 4
            reference_blocks.append(
                {
                    "kind": "book_record_reference_block",
                    "block_offset": record_start + block_start,
                    "block_local_offset": block_start,
                    "block_end": record_start + block_end,
                    "block_end_local_offset": block_end,
                    "block_size": block_end - block_start,
                    "entry_size": 4,
                    "entry_count": len(block),
                    "entries": block,
                }
            )
            block = []
        block.append(marker)
        previous_local = local
    if block:
        block_start = int(block[0]["local_offset"])
        block_end = int(block[-1]["local_offset"]) + 4
        reference_blocks.append(
            {
                "kind": "book_record_reference_block",
                "block_offset": record_start + block_start,
                "block_local_offset": block_start,
                "block_end": record_start + block_end,
                "block_end_local_offset": block_end,
                "block_size": block_end - block_start,
                "entry_size": 4,
                "entry_count": len(block),
                "entries": block,
            }
        )
    for block_row in reference_blocks:
        segments.append(
            {
                "kind": "book_record_reference_block",
                "offset": block_row["block_offset"],
                "local_offset": block_row["block_local_offset"],
                "end": block_row["block_end"],
                "end_local_offset": block_row["block_end_local_offset"],
                "size": block_row["block_size"],
                "entry_count": block_row["entry_count"],
            }
        )

    palette = None
    for local in range(0x32, max(0, len(blob) - 260)):
        if blob[local : local + 4] != b"\x01\x03\x00\x00":
            continue
        entries = []
        color_start = local + 4
        color_end = color_start + 64 * 4
        if color_end > len(blob):
            continue
        for index in range(64):
            blue, green, red, reserved = blob[color_start + index * 4 : color_start + index * 4 + 4]
            entries.append({"index": index, "red": red, "green": green, "blue": blue, "reserved": reserved})
        if all(entry["reserved"] == 0 for entry in entries):
            palette = {
                "kind": "book_64_color_palette",
                "palette_offset": record_start + local,
                "palette_local_offset": local,
                "palette_end": record_start + color_end,
                "palette_end_local_offset": color_end,
                "palette_size": color_end - local,
                "header_words": [0x0301, 0],
                "entry_size": 4,
                "entry_count": len(entries),
                "entries": entries,
            }
            segments.append(
                {
                    "kind": "book_64_color_palette",
                    "offset": record_start + local,
                    "local_offset": local,
                    "end": record_start + color_end,
                    "end_local_offset": color_end,
                    "size": color_end - local,
                    "entry_count": len(entries),
                }
            )
            break

    occupied_ranges = [
        (int(segment["local_offset"]), int(segment["end_local_offset"]))
        for segment in segments
        if int(segment["end_local_offset"]) > int(segment["local_offset"])
    ]

    def range_is_free(start: int, end: int) -> bool:
        return all(end <= occupied_start or start >= occupied_end for occupied_start, occupied_end in occupied_ranges)

    local_pointer_targets: dict[int, list[int]] = {}
    for pointer_local in range(0, len(blob) - 1, 2):
        target = struct.unpack_from("<H", blob, pointer_local)[0]
        if 0x10 <= target <= len(blob) - 2 and target % 2 == 0:
            local_pointer_targets.setdefault(target, []).append(pointer_local)

    pointer_tables = []
    pointer_table_reference_words = []
    accepted_pointer_table_ranges: list[tuple[int, int]] = []
    for local in range(0x10, len(blob) - 3, 2):
        if local not in local_pointer_targets:
            continue
        count = struct.unpack_from("<H", blob, local)[0]
        if not 2 <= count <= 64:
            continue
        table_end = local + 2 + count * 2
        if table_end > len(blob) or not range_is_free(local, table_end):
            continue
        if any(not (table_end <= start or local >= end) for start, end in accepted_pointer_table_ranges):
            continue
        entries = [struct.unpack_from("<H", blob, local + 2 + index * 2)[0] for index in range(count)]
        if any(entry < 0x10 or entry > len(blob) - 2 or entry % 2 for entry in entries):
            continue
        unique_entries = sorted(set(entries))
        if len(unique_entries) < max(2, count // 2):
            continue
        pointing_words = [
            pointer_local
            for pointer_local in local_pointer_targets.get(local, [])
            if not (local <= pointer_local < table_end)
        ]
        if not pointing_words:
            continue
        table = {
            "kind": "book_local_pointer_table",
            "table_offset": record_start + local,
            "table_local_offset": local,
            "table_end": record_start + table_end,
            "table_end_local_offset": table_end,
            "table_size": table_end - local,
            "entry_size": 2,
            "entry_count": count,
            "pointing_word_offsets": [record_start + pointer_local for pointer_local in pointing_words],
            "pointing_word_local_offsets": pointing_words,
            "entries": [
                {
                    "index": index,
                    "target_offset": record_start + entry,
                    "target_local_offset": entry,
                }
                for index, entry in enumerate(entries)
            ],
        }
        pointer_tables.append(table)
        accepted_pointer_table_ranges.append((local, table_end))
        occupied_ranges.append((local, table_end))
        segments.append(
            {
                "kind": "book_local_pointer_table",
                "offset": record_start + local,
                "local_offset": local,
                "end": record_start + table_end,
                "end_local_offset": table_end,
                "size": table_end - local,
                "entry_count": count,
            }
        )
        for pointer_local in pointing_words:
            pointer_end = pointer_local + 2
            if not range_is_free(pointer_local, pointer_end):
                continue
            reference_word = {
                "kind": "book_local_pointer_table_reference",
                "offset": record_start + pointer_local,
                "local_offset": pointer_local,
                "end": record_start + pointer_end,
                "end_local_offset": pointer_end,
                "size": 2,
                "target_offset": record_start + local,
                "target_local_offset": local,
            }
            pointer_table_reference_words.append(reference_word)
            occupied_ranges.append((pointer_local, pointer_end))
            segments.append(reference_word)

    pre_pointer_descriptor_blocks = []
    occupied_ranges.sort()
    table_starts = {int(table["table_local_offset"]) for table in pointer_tables}
    reference_word_starts = {
        int(word["local_offset"])
        for word in pointer_table_reference_words
    }
    for table_start in sorted(table_starts):
        ref_start = table_start
        while ref_start - 2 in reference_word_starts:
            ref_start -= 2
        if ref_start == table_start:
            continue
        previous_end = max((end for start, end in occupied_ranges if end <= ref_start), default=0)
        descriptor_start = previous_end
        descriptor_end = ref_start
        if descriptor_end - descriptor_start != 50:
            continue
        if not range_is_free(descriptor_start, descriptor_end):
            continue
        if struct.unpack_from("<H", blob, descriptor_start)[0] != table_start + 1:
            continue
        if struct.unpack_from("<H", blob, descriptor_start + 2)[0] != 0:
            continue
        name_start = descriptor_start + 4
        name_end = blob.find(b"\x00", name_start, descriptor_end)
        if name_end == -1:
            continue
        try:
            descriptor_name = blob[name_start:name_end].decode("cp1252")
        except UnicodeDecodeError:
            continue
        if not descriptor_name or any(ord(ch) < 0x20 for ch in descriptor_name):
            continue
        block = {
            "kind": "book_pre_pointer_descriptor_block",
            "offset": record_start + descriptor_start,
            "local_offset": descriptor_start,
            "end": record_start + descriptor_end,
            "end_local_offset": descriptor_end,
            "size": descriptor_end - descriptor_start,
            "following_table_offset": record_start + table_start,
            "following_table_local_offset": table_start,
            "first_word_table_plus_one": table_start + 1,
            "zero_word": 0,
            "name": descriptor_name,
            "name_offset": record_start + name_start,
            "name_local_offset": name_start,
            "name_end": record_start + name_end,
            "name_end_local_offset": name_end,
            "descriptor_tail_offset": record_start + name_end + 1,
            "descriptor_tail_local_offset": name_end + 1,
            "descriptor_tail_size": descriptor_end - (name_end + 1),
        }
        pre_pointer_descriptor_blocks.append(block)
        occupied_ranges.append((descriptor_start, descriptor_end))
        segments.append(block)

    pre_pointer_count_descriptors = []
    for table in pointer_tables:
        table_start = int(table["table_local_offset"])
        descriptor_start = table_start - 6
        descriptor_end = table_start
        if descriptor_start < 0 or not range_is_free(descriptor_start, descriptor_end):
            continue
        payload_local, zero_word, table_count_plus_one = struct.unpack_from("<HHH", blob, descriptor_start)
        if zero_word != 0 or table_count_plus_one != int(table["entry_count"]) + 1:
            continue
        if not table_start <= payload_local < len(blob):
            continue
        block = {
            "kind": "book_pre_pointer_count_descriptor",
            "offset": record_start + descriptor_start,
            "local_offset": descriptor_start,
            "end": record_start + descriptor_end,
            "end_local_offset": descriptor_end,
            "size": 6,
            "payload_offset": record_start + payload_local,
            "payload_local_offset": payload_local,
            "zero_word": zero_word,
            "table_count_plus_one": table_count_plus_one,
            "following_table_offset": record_start + table_start,
            "following_table_local_offset": table_start,
            "following_table_entry_count": int(table["entry_count"]),
        }
        pre_pointer_count_descriptors.append(block)
        occupied_ranges.append((descriptor_start, descriptor_end))
        segments.append(block)

    compact_named_descriptors = []
    occupied_ranges = merge_ranges(occupied_ranges)
    cursor = 0
    for occupied_start, occupied_end in occupied_ranges:
        if cursor < occupied_start:
            descriptor_start = cursor
            if descriptor_start + 10 <= occupied_start:
                descriptor_id, payload_local, table_plus_one, zero_word = struct.unpack_from("<HHHH", blob, descriptor_start)
                descriptor_end = payload_local
                descriptor_size = descriptor_end - descriptor_start
                name_bytes = blob[descriptor_start + 8 : descriptor_end] if descriptor_start + 8 <= descriptor_end else b""
                if (
                    descriptor_id == 1
                    and descriptor_start + 10 <= descriptor_end <= occupied_start
                    and descriptor_size % 2 == 0
                    and table_plus_one - 1 in table_starts
                    and zero_word == 0
                    and name_bytes
                    and all(0x20 <= byte <= 0x7E for byte in name_bytes)
                ):
                    descriptor_name = name_bytes.decode("cp1252")
                    block = {
                        "kind": "book_compact_named_descriptor",
                        "offset": record_start + descriptor_start,
                        "local_offset": descriptor_start,
                        "end": record_start + descriptor_end,
                        "end_local_offset": descriptor_end,
                        "size": descriptor_size,
                        "descriptor_id": descriptor_id,
                        "payload_offset": record_start + payload_local,
                        "payload_local_offset": payload_local,
                        "pointer_table_offset": record_start + table_plus_one - 1,
                        "pointer_table_local_offset": table_plus_one - 1,
                        "table_plus_one_word": table_plus_one,
                        "zero_word": zero_word,
                        "name": descriptor_name,
                        "name_offset": record_start + descriptor_start + 8,
                        "name_local_offset": descriptor_start + 8,
                        "name_size": len(name_bytes),
                    }
                    compact_named_descriptors.append(block)
                    occupied_ranges.append((descriptor_start, descriptor_end))
                    segments.append(block)
        cursor = max(cursor, occupied_end)

    zero_runs = []
    local = 0
    while local < len(blob):
        if blob[local] != 0:
            local += 1
            continue
        start = local
        while local < len(blob) and blob[local] == 0:
            local += 1
        if local - start >= 16:
            if range_is_free(start, local):
                zero_runs.append(
                    {
                        "kind": "book_zero_padding",
                        "offset": record_start + start,
                        "local_offset": start,
                        "end": record_start + local,
                        "end_local_offset": local,
                        "size": local - start,
                    }
                )
                occupied_ranges.append((start, local))
                segments.append(zero_runs[-1])

    compact_descriptor_payload_fragments = []
    occupied_ranges = merge_ranges(occupied_ranges)
    for descriptor in compact_named_descriptors:
        payload_start = int(descriptor["payload_local_offset"])
        payload_end = int(descriptor["pointer_table_local_offset"])
        if not payload_start < payload_end <= len(blob):
            continue
        cursor = payload_start
        for occupied_start, occupied_end in occupied_ranges:
            if occupied_end <= payload_start:
                continue
            if occupied_start >= payload_end:
                break
            if cursor < occupied_start:
                fragment_start = cursor
                fragment_end = min(occupied_start, payload_end)
                if fragment_start < fragment_end:
                    fragment = {
                        "kind": "book_compact_descriptor_payload_fragment",
                        "offset": record_start + fragment_start,
                        "local_offset": fragment_start,
                        "end": record_start + fragment_end,
                        "end_local_offset": fragment_end,
                        "size": fragment_end - fragment_start,
                        "descriptor_offset": descriptor["offset"],
                        "descriptor_local_offset": descriptor["local_offset"],
                        "descriptor_name_fragment": descriptor["name"],
                        "payload_region_offset": record_start + payload_start,
                        "payload_region_local_offset": payload_start,
                        "payload_region_end": record_start + payload_end,
                        "payload_region_end_local_offset": payload_end,
                    }
                    compact_descriptor_payload_fragments.append(fragment)
                    occupied_ranges.append((fragment_start, fragment_end))
                    segments.append(fragment)
            cursor = max(cursor, occupied_end)
        if cursor < payload_end:
            fragment = {
                "kind": "book_compact_descriptor_payload_fragment",
                "offset": record_start + cursor,
                "local_offset": cursor,
                "end": record_start + payload_end,
                "end_local_offset": payload_end,
                "size": payload_end - cursor,
                "descriptor_offset": descriptor["offset"],
                "descriptor_local_offset": descriptor["local_offset"],
                "descriptor_name_fragment": descriptor["name"],
                "payload_region_offset": record_start + payload_start,
                "payload_region_local_offset": payload_start,
                "payload_region_end": record_start + payload_end,
                "payload_region_end_local_offset": payload_end,
            }
            compact_descriptor_payload_fragments.append(fragment)
            occupied_ranges.append((cursor, payload_end))
            segments.append(fragment)

    named_payload_reference_descriptors = []
    pointer_table_reference_starts = {
        int(word["local_offset"]) for word in pointer_table_reference_words
    }
    occupied_ranges = merge_ranges(occupied_ranges)
    cursor = 0
    for occupied_start, occupied_end in occupied_ranges:
        if cursor < occupied_start and occupied_start in pointer_table_reference_starts:
            descriptor_start = cursor
            descriptor_end = occupied_start
            if descriptor_end - descriptor_start >= 8:
                payload_local, zero_word = struct.unpack_from("<HH", blob, descriptor_start)
                name_field = blob[descriptor_start + 4 : descriptor_end]
                first_nul = name_field.find(b"\x00")
                if first_nul == -1:
                    name_bytes = name_field
                    trailing_zero_bytes = b""
                    extra_word_bytes = b""
                else:
                    name_bytes = name_field[:first_nul]
                    tail = name_field[first_nul:]
                    zero_tail_size = 0
                    while zero_tail_size < len(tail) and tail[zero_tail_size] == 0:
                        zero_tail_size += 1
                    trailing_zero_bytes = tail[:zero_tail_size]
                    extra_word_bytes = tail[zero_tail_size:]
                extra_words = (
                    [
                        struct.unpack_from("<H", extra_word_bytes, index)[0]
                        for index in range(0, len(extra_word_bytes), 2)
                    ]
                    if len(extra_word_bytes) % 2 == 0
                    else []
                )
                if (
                    zero_word == 0
                    and descriptor_end + 2 <= payload_local < len(blob)
                    and name_bytes
                    and all(0x20 <= byte <= 0x7E for byte in name_bytes)
                    and len(extra_word_bytes) % 2 == 0
                    and all(0x10 <= word < len(blob) for word in extra_words)
                ):
                    descriptor_name = name_bytes.decode("cp1252")
                    descriptor = {
                        "kind": "book_named_payload_reference_descriptor",
                        "offset": record_start + descriptor_start,
                        "local_offset": descriptor_start,
                        "end": record_start + descriptor_end,
                        "end_local_offset": descriptor_end,
                        "size": descriptor_end - descriptor_start,
                        "payload_offset": record_start + payload_local,
                        "payload_local_offset": payload_local,
                        "zero_word": zero_word,
                        "name": descriptor_name,
                        "name_offset": record_start + descriptor_start + 4,
                        "name_local_offset": descriptor_start + 4,
                        "name_field_size": len(name_field),
                        "trailing_zero_bytes": len(trailing_zero_bytes),
                        "extra_local_offset_words": extra_words,
                        "payload_fragment_eligible": not extra_words,
                        "following_pointer_reference_offset": record_start + descriptor_end,
                        "following_pointer_reference_local_offset": descriptor_end,
                    }
                    named_payload_reference_descriptors.append(descriptor)
                    occupied_ranges.append((descriptor_start, descriptor_end))
                    segments.append(descriptor)
        cursor = max(cursor, occupied_end)

    openscript_objects = []
    occupied_ranges = merge_ranges(occupied_ranges)

    def scan_openscript_gap(gap_start: int, gap_end: int) -> None:
        nonlocal occupied_ranges, pointer_table_reference_words, segments

        def script_range_is_free(start: int, end: int) -> bool:
            strong_ranges = [
                (int(segment["local_offset"]), int(segment["end_local_offset"]))
                for segment in segments
                if segment.get("kind") not in {
                    "book_local_pointer_table_reference",
                    "book_pointer_target_payload_fragment",
                }
            ]
            return all(end <= occupied_start or start >= occupied_end for occupied_start, occupied_end in strong_ranges)

        candidate = blob.find(b"\x04\x01", gap_start, gap_end)
        while candidate != -1 and candidate + 0x1E <= gap_end:
            if candidate % 2 == 0 and script_range_is_free(candidate, candidate + 0x1E):
                (
                    script_type,
                    section0_offset,
                    section1_offset,
                    section2_offset,
                    source_text_offset,
                    code_offset,
                    code_end_offset,
                    reserved_word,
                ) = struct.unpack_from("<8H", blob, candidate)
                section_offsets = [section0_offset, section1_offset, section2_offset]
                nonzero_sections = [offset for offset in section_offsets if offset]
                if (
                    script_type == 0x0104
                    and source_text_offset == 0
                    and reserved_word == 0
                    and code_offset
                    and 0x1E <= code_offset < code_end_offset
                    and candidate + code_end_offset <= gap_end
                    and script_range_is_free(candidate, candidate + code_end_offset)
                    and all(0x1E <= offset < code_offset for offset in nonzero_sections)
                    and nonzero_sections == sorted(nonzero_sections)
                ):
                    boundary_offsets = sorted(set(nonzero_sections + [code_offset, code_end_offset]))
                    script_sections = []
                    for index, section_offset in enumerate(section_offsets):
                        if not section_offset:
                            continue
                        following_offsets = [offset for offset in boundary_offsets if offset > section_offset]
                        section_end_offset = following_offsets[0] if following_offsets else code_offset
                        script_sections.append(
                            {
                                "index": index,
                                "offset": record_start + candidate + section_offset,
                                "local_offset": candidate + section_offset,
                                "script_relative_offset": section_offset,
                                "end": record_start + candidate + section_end_offset,
                                "end_local_offset": candidate + section_end_offset,
                                "script_relative_end": section_end_offset,
                                "size": section_end_offset - section_offset,
                            }
                        )
                    block = {
                        "kind": "book_openscript_object",
                        "offset": record_start + candidate,
                        "local_offset": candidate,
                        "end": record_start + candidate + code_end_offset,
                        "end_local_offset": candidate + code_end_offset,
                        "size": code_end_offset,
                        "script_type": script_type,
                        "script_type_hex": f"0x{script_type:04x}",
                        "header_size": 0x1E,
                        "section_offsets": section_offsets,
                        "source_text_offset": source_text_offset,
                        "code_offset": code_offset,
                        "code_end_offset": code_end_offset,
                        "code_size": code_end_offset - code_offset,
                        "reserved_word": reserved_word,
                        "sections": script_sections,
                        "code_absolute_offset": record_start + candidate + code_offset,
                        "code_local_offset": candidate + code_offset,
                        "code_absolute_end": record_start + candidate + code_end_offset,
                        "code_local_end": candidate + code_end_offset,
                    }
                    openscript_objects.append(block)
                    script_start = candidate
                    script_end = candidate + code_end_offset
                    pointer_table_reference_words = [
                        word
                        for word in pointer_table_reference_words
                        if int(word["end_local_offset"]) <= script_start
                        or int(word["local_offset"]) >= script_end
                    ]
                    for table in pointer_tables:
                        pointing_word_locals = [
                            local
                            for local in table.get("pointing_word_local_offsets", [])
                            if local < script_start or local >= script_end
                        ]
                        table["pointing_word_local_offsets"] = pointing_word_locals
                        table["pointing_word_offsets"] = [
                            record_start + local for local in pointing_word_locals
                        ]
                    segments = [
                        segment
                        for segment in segments
                        if segment.get("kind") != "book_local_pointer_table_reference"
                        or int(segment["end_local_offset"]) <= script_start
                        or int(segment["local_offset"]) >= script_end
                    ]
                    occupied_ranges.append((candidate, candidate + code_end_offset))
                    segments.append(block)
                    occupied_ranges = merge_ranges(
                        (int(segment["local_offset"]), int(segment["end_local_offset"]))
                        for segment in segments
                        if int(segment["end_local_offset"]) > int(segment["local_offset"])
                    )
                    candidate = blob.find(b"\x04\x01", script_end, gap_end)
                    continue
            candidate = blob.find(b"\x04\x01", candidate + 1, gap_end)

    script_scan_occupied_ranges = merge_ranges(
        (int(segment["local_offset"]), int(segment["end_local_offset"]))
        for segment in segments
        if segment.get("kind") != "book_local_pointer_table_reference"
        and int(segment["end_local_offset"]) > int(segment["local_offset"])
    )
    cursor = 0
    for occupied_start, occupied_end in script_scan_occupied_ranges:
        if cursor < occupied_start:
            scan_openscript_gap(cursor, occupied_start)
        cursor = max(cursor, occupied_end)
    if cursor < len(blob):
        scan_openscript_gap(cursor, len(blob))

    named_payload_reference_inline_prefixes = []
    occupied_ranges = merge_ranges(occupied_ranges)
    pointer_reference_targets = {
        int(word["local_offset"]): int(word["target_local_offset"])
        for word in pointer_table_reference_words
    }
    for descriptor in named_payload_reference_descriptors:
        if not descriptor.get("payload_fragment_eligible", True):
            continue
        payload_start = int(descriptor["payload_local_offset"])
        reference_local = int(descriptor["following_pointer_reference_local_offset"])
        payload_end = pointer_reference_targets.get(reference_local, 0)
        if not payload_start < payload_end <= len(blob):
            continue
        prefix_start = int(descriptor["following_pointer_reference_local_offset"]) + 2
        prefix_end = payload_start
        if (
            prefix_start < prefix_end
            and prefix_end - prefix_start <= 32
            and range_is_free(prefix_start, prefix_end)
        ):
            prefix_bytes = blob[prefix_start:prefix_end]
            prefix = {
                "kind": "book_named_payload_reference_inline_prefix",
                "offset": record_start + prefix_start,
                "local_offset": prefix_start,
                "end": record_start + prefix_end,
                "end_local_offset": prefix_end,
                "size": prefix_end - prefix_start,
                "descriptor_offset": descriptor["offset"],
                "descriptor_local_offset": descriptor["local_offset"],
                "descriptor_name": descriptor["name"],
                "payload_region_offset": record_start + payload_start,
                "payload_region_local_offset": payload_start,
                "following_pointer_reference_offset": descriptor["following_pointer_reference_offset"],
                "following_pointer_reference_local_offset": reference_local,
                "bytes_hex": prefix_bytes.hex(),
            }
            if len(prefix_bytes) % 2 == 0:
                prefix["words"] = [
                    struct.unpack_from("<H", prefix_bytes, index)[0]
                    for index in range(0, len(prefix_bytes), 2)
                ]
            named_payload_reference_inline_prefixes.append(prefix)
            occupied_ranges.append((prefix_start, prefix_end))
            segments.append(prefix)
            occupied_ranges = merge_ranges(occupied_ranges)

    named_payload_reference_payload_fragments = []
    occupied_ranges = merge_ranges(occupied_ranges)
    for descriptor in named_payload_reference_descriptors:
        if not descriptor.get("payload_fragment_eligible", True):
            continue
        payload_start = int(descriptor["payload_local_offset"])
        reference_local = int(descriptor["following_pointer_reference_local_offset"])
        payload_end = pointer_reference_targets.get(reference_local, 0)
        if not payload_start < payload_end <= len(blob):
            continue
        cursor = payload_start
        for occupied_start, occupied_end in occupied_ranges:
            if occupied_end <= payload_start:
                continue
            if occupied_start >= payload_end:
                break
            if cursor < occupied_start:
                fragment_start = cursor
                fragment_end = min(occupied_start, payload_end)
                if fragment_start < fragment_end:
                    fragment = {
                        "kind": "book_named_payload_reference_payload_fragment",
                        "offset": record_start + fragment_start,
                        "local_offset": fragment_start,
                        "end": record_start + fragment_end,
                        "end_local_offset": fragment_end,
                        "size": fragment_end - fragment_start,
                        "descriptor_offset": descriptor["offset"],
                        "descriptor_local_offset": descriptor["local_offset"],
                        "descriptor_name": descriptor["name"],
                        "payload_region_offset": record_start + payload_start,
                        "payload_region_local_offset": payload_start,
                        "payload_region_end": record_start + payload_end,
                        "payload_region_end_local_offset": payload_end,
                        "following_pointer_reference_offset": descriptor["following_pointer_reference_offset"],
                        "following_pointer_reference_local_offset": reference_local,
                    }
                    named_payload_reference_payload_fragments.append(fragment)
                    occupied_ranges.append((fragment_start, fragment_end))
                    segments.append(fragment)
            cursor = max(cursor, occupied_end)
        if cursor < payload_end:
            fragment = {
                "kind": "book_named_payload_reference_payload_fragment",
                "offset": record_start + cursor,
                "local_offset": cursor,
                "end": record_start + payload_end,
                "end_local_offset": payload_end,
                "size": payload_end - cursor,
                "descriptor_offset": descriptor["offset"],
                "descriptor_local_offset": descriptor["local_offset"],
                "descriptor_name": descriptor["name"],
                "payload_region_offset": record_start + payload_start,
                "payload_region_local_offset": payload_start,
                "payload_region_end": record_start + payload_end,
                "payload_region_end_local_offset": payload_end,
                "following_pointer_reference_offset": descriptor["following_pointer_reference_offset"],
                "following_pointer_reference_local_offset": reference_local,
            }
            named_payload_reference_payload_fragments.append(fragment)
            occupied_ranges.append((cursor, payload_end))
            segments.append(fragment)

    pointer_target_payload_fragments = []
    occupied_ranges = merge_ranges(occupied_ranges)
    pointer_target_tables: dict[int, list[dict[str, object]]] = {}
    for table in pointer_tables:
        for entry in table.get("entries", []):
            target_local = int(entry["target_local_offset"])
            pointer_target_tables.setdefault(target_local, []).append(table)
    pointer_targets = sorted(pointer_target_tables)
    for index, target_start in enumerate(pointer_targets):
        occupied_ranges = merge_ranges(occupied_ranges)
        strong_occupied_ranges = merge_ranges(
            (int(segment["local_offset"]), int(segment["end_local_offset"]))
            for segment in segments
            if segment.get("kind") not in {
                "book_local_pointer_table_reference",
                "book_pointer_target_payload_fragment",
                "book_zero_padding",
            }
            and int(segment["end_local_offset"]) > int(segment["local_offset"])
        )
        candidate_ends = []
        if index + 1 < len(pointer_targets):
            candidate_ends.append(pointer_targets[index + 1])
        candidate_ends.extend(start for start, _end in strong_occupied_ranges if start > target_start)
        if not candidate_ends:
            continue
        target_end = min(candidate_ends)
        if not target_start < target_end <= len(blob):
            continue
        cursor = target_start
        for occupied_start, occupied_end in occupied_ranges:
            if occupied_end <= target_start:
                continue
            if occupied_start >= target_end:
                break
            if cursor < occupied_start:
                fragment_start = cursor
                fragment_end = min(occupied_start, target_end)
                if fragment_start < fragment_end:
                    tables = pointer_target_tables[target_start]
                    fragment = {
                        "kind": "book_pointer_target_payload_fragment",
                        "offset": record_start + fragment_start,
                        "local_offset": fragment_start,
                        "end": record_start + fragment_end,
                        "end_local_offset": fragment_end,
                        "size": fragment_end - fragment_start,
                        "target_offset": record_start + target_start,
                        "target_local_offset": target_start,
                        "target_span_end": record_start + target_end,
                        "target_span_end_local_offset": target_end,
                        "source_pointer_table_offsets": [
                            int(table["table_offset"]) for table in tables
                        ],
                        "source_pointer_table_local_offsets": [
                            int(table["table_local_offset"]) for table in tables
                        ],
                    }
                    pointer_target_payload_fragments.append(fragment)
                    occupied_ranges.append((fragment_start, fragment_end))
                    segments.append(fragment)
            cursor = max(cursor, occupied_end)
        if cursor < target_end:
            tables = pointer_target_tables[target_start]
            fragment = {
                "kind": "book_pointer_target_payload_fragment",
                "offset": record_start + cursor,
                "local_offset": cursor,
                "end": record_start + target_end,
                "end_local_offset": target_end,
                "size": target_end - cursor,
                "target_offset": record_start + target_start,
                "target_local_offset": target_start,
                "target_span_end": record_start + target_end,
                "target_span_end_local_offset": target_end,
                "source_pointer_table_offsets": [
                    int(table["table_offset"]) for table in tables
                ],
                "source_pointer_table_local_offsets": [
                    int(table["table_local_offset"]) for table in tables
                ],
            }
            pointer_target_payload_fragments.append(fragment)
            occupied_ranges.append((cursor, target_end))
            segments.append(fragment)

    openscript_auxiliary_prefixes = []
    openscript_duplicate_tails = []
    occupied_ranges = merge_ranges(occupied_ranges)
    if len(blob) >= 8:
        _record_key, _declared_body_length, aux_length_0, aux_length_1 = struct.unpack_from("<HHHH", blob, 0)
    else:
        aux_length_0 = aux_length_1 = 0

    def current_range_is_free(start: int, end: int) -> bool:
        return all(end <= occupied_start or start >= occupied_end for occupied_start, occupied_end in occupied_ranges)

    if (
        aux_length_0 == aux_length_1
        and 0x12 <= aux_length_0 < len(blob)
    ):
        for script_object in openscript_objects:
            script_start = int(script_object["local_offset"])
            script_end = int(script_object["end_local_offset"])
            prefix_start = script_end
            prefix_end = aux_length_0
            if not (script_end < aux_length_0 < len(blob)):
                continue
            if aux_length_0 - script_end > 0x80:
                continue
            candidate_tail_ends = [
                occupied_start
                for occupied_start, _occupied_end in occupied_ranges
                if occupied_start > aux_length_0
            ]
            tail_end = min(candidate_tail_ends) if candidate_tail_ends else len(blob)
            if not (aux_length_0 < tail_end <= len(blob)):
                continue
            if not current_range_is_free(prefix_start, prefix_end):
                continue
            if not current_range_is_free(aux_length_0, tail_end):
                continue
            tail_size = tail_end - aux_length_0
            duplicate_source_start = script_end - tail_size
            if duplicate_source_start < script_start:
                continue
            if blob[duplicate_source_start:script_end] != blob[aux_length_0:tail_end]:
                continue
            prefix_words = []
            if (prefix_end - prefix_start) % 2 == 0:
                prefix_words = [
                    struct.unpack_from("<H", blob, local)[0]
                    for local in range(prefix_start, prefix_end, 2)
                ]
            if prefix_start < prefix_end:
                prefix = {
                    "kind": "book_openscript_auxiliary_prefix",
                    "offset": record_start + prefix_start,
                    "local_offset": prefix_start,
                    "end": record_start + prefix_end,
                    "end_local_offset": prefix_end,
                    "size": prefix_end - prefix_start,
                    "script_offset": script_object["offset"],
                    "script_local_offset": script_start,
                    "script_end": script_object["end"],
                    "script_end_local_offset": script_end,
                    "book_header_auxiliary_local_offset": aux_length_0,
                    "book_header_auxiliary_offset": record_start + aux_length_0,
                    "prefix_words": prefix_words,
                }
                openscript_auxiliary_prefixes.append(prefix)
                occupied_ranges.append((prefix_start, prefix_end))
                segments.append(prefix)
            tail = {
                "kind": "book_openscript_duplicate_tail",
                "offset": record_start + aux_length_0,
                "local_offset": aux_length_0,
                "end": record_start + tail_end,
                "end_local_offset": tail_end,
                "size": tail_size,
                "script_offset": script_object["offset"],
                "script_local_offset": script_start,
                "script_end": script_object["end"],
                "script_end_local_offset": script_end,
                "duplicate_source_offset": record_start + duplicate_source_start,
                "duplicate_source_local_offset": duplicate_source_start,
                "duplicate_source_end": record_start + script_end,
                "duplicate_source_end_local_offset": script_end,
                "book_header_auxiliary_local_offset": aux_length_0,
                "book_header_auxiliary_offset": record_start + aux_length_0,
            }
            openscript_duplicate_tails.append(tail)
            occupied_ranges.append((aux_length_0, tail_end))
            segments.append(tail)
            occupied_ranges = merge_ranges(occupied_ranges)
            break

    openscript_record_links = []
    occupied_ranges = merge_ranges(occupied_ranges)
    if len(blob) >= 0x1A:
        reserved_word_0, reserved_word_1, script_size_word, script_link_word = struct.unpack_from("<HHHH", blob, 0x12)
        def link_range_is_free(start: int, end: int) -> bool:
            strong_ranges = [
                (int(segment["local_offset"]), int(segment["end_local_offset"]))
                for segment in segments
                if segment.get("kind") not in {
                    "book_local_pointer_table_reference",
                    "book_pointer_target_payload_fragment",
                }
            ]
            return all(end <= occupied_start or start >= occupied_end for occupied_start, occupied_end in strong_ranges)

        matching_scripts = [
            script_object
            for script_object in openscript_objects
            if int(script_object["size"]) == script_size_word
            and int(script_object["local_offset"]) + 6 == script_link_word
        ]
        if (
            matching_scripts
            and reserved_word_0 == 0
            and reserved_word_1 == 0
            and link_range_is_free(0x12, 0x1A)
        ):
            script_object = matching_scripts[0]
            link = {
                "kind": "book_openscript_record_link",
                "offset": record_start + 0x12,
                "local_offset": 0x12,
                "end": record_start + 0x1A,
                "end_local_offset": 0x1A,
                "size": 8,
                "reserved_words": [reserved_word_0, reserved_word_1],
                "script_size_word": script_size_word,
                "script_link_word": script_link_word,
                "script_offset": script_object["offset"],
                "script_local_offset": int(script_object["local_offset"]),
                "script_end": script_object["end"],
                "script_end_local_offset": int(script_object["end_local_offset"]),
                "script_link_target_offset": record_start + script_link_word,
                "script_link_target_local_offset": script_link_word,
            }
            pointer_table_reference_words = [
                word
                for word in pointer_table_reference_words
                if int(word["end_local_offset"]) <= 0x12
                or int(word["local_offset"]) >= 0x1A
            ]
            for table in pointer_tables:
                pointing_word_locals = [
                    local
                    for local in table.get("pointing_word_local_offsets", [])
                    if local < 0x12 or local >= 0x1A
                ]
                table["pointing_word_local_offsets"] = pointing_word_locals
                table["pointing_word_offsets"] = [
                    record_start + local for local in pointing_word_locals
                ]
            segments = [
                segment
                for segment in segments
                if segment.get("kind") not in {
                    "book_local_pointer_table_reference",
                    "book_pointer_target_payload_fragment",
                }
                or int(segment["end_local_offset"]) <= 0x12
                or int(segment["local_offset"]) >= 0x1A
            ]
            pointer_target_payload_fragments = [
                fragment
                for fragment in pointer_target_payload_fragments
                if int(fragment["end_local_offset"]) <= 0x12
                or int(fragment["local_offset"]) >= 0x1A
            ]
            openscript_record_links.append(link)
            occupied_ranges.append((0x12, 0x1A))
            segments.append(link)
            occupied_ranges = merge_ranges(
                (int(segment["local_offset"]), int(segment["end_local_offset"]))
                for segment in segments
                if int(segment["end_local_offset"]) > int(segment["local_offset"])
            )

    book_control_descriptors = []
    occupied_ranges = merge_ranges(occupied_ranges)

    def add_book_control_descriptor(start: int, end: int, kind: str, previous_kind: str, next_kind: str) -> None:
        if not (0 <= start < end <= len(blob)):
            return
        if (end - start) % 2:
            return
        descriptor_bytes = blob[start:end]
        if not descriptor_bytes or all(byte == 0 for byte in descriptor_bytes):
            return
        words = [
            struct.unpack_from("<H", descriptor_bytes, index)[0]
            for index in range(0, len(descriptor_bytes), 2)
        ]
        if not words:
            return
        descriptor = {
            "kind": kind,
            "offset": record_start + start,
            "local_offset": start,
            "end": record_start + end,
            "end_local_offset": end,
            "size": end - start,
            "words": words,
            "previous_segment_kind": previous_kind,
            "next_segment_kind": next_kind,
        }
        book_control_descriptors.append(descriptor)
        occupied_ranges.append((start, end))
        segments.append(descriptor)

    def range_is_currently_free(start: int, end: int) -> bool:
        return all(end <= occupied_start or start >= occupied_end for occupied_start, occupied_end in occupied_ranges)

    strong_segments = sorted(
        (
            int(segment["local_offset"]),
            int(segment["end_local_offset"]),
            str(segment["kind"]),
        )
        for segment in segments
        if segment.get("kind") not in {
            "book_local_pointer_table_reference",
            "book_pointer_target_payload_fragment",
        }
        and int(segment["end_local_offset"]) > int(segment["local_offset"])
    )
    for index in range(len(strong_segments) - 1):
        previous_start, previous_end, previous_kind = strong_segments[index]
        next_start, next_end, next_kind = strong_segments[index + 1]
        if previous_end >= next_start:
            continue
        gap_start = previous_end
        gap_end = next_start
        gap_size = gap_end - gap_start
        if gap_size > 64:
            continue
        if "book_record_reference_block" in {previous_kind, next_kind}:
            if gap_size >= 4 and gap_size % 2 == 0:
                add_book_control_descriptor(
                    gap_start,
                    gap_end,
                    "book_record_reference_control_descriptor",
                    previous_kind,
                    next_kind,
                )
            continue
        if (
            previous_kind == "book_64_color_palette"
            and next_kind in {"book_compact_named_descriptor", "book_local_pointer_table"}
            and gap_size == 4
        ):
            add_book_control_descriptor(
                gap_start,
                gap_end,
                "book_pointer_list_control_descriptor",
                previous_kind,
                next_kind,
            )
    occupied_ranges = merge_ranges(occupied_ranges)
    for reference_word in pointer_table_reference_words:
        reference_start = int(reference_word["local_offset"])
        descriptor_start = reference_start - 4
        descriptor_end = reference_start
        if descriptor_start < 0 or not range_is_currently_free(descriptor_start, descriptor_end):
            continue
        previous_strong = [
            segment
            for segment in strong_segments
            if segment[1] == descriptor_start
        ]
        next_strong = [
            segment
            for segment in strong_segments
            if segment[0] >= reference_start + 2
        ]
        if not previous_strong or not next_strong:
            continue
        _previous_start, _previous_end, previous_kind = previous_strong[-1]
        next_start, next_end, next_kind = next_strong[0]
        if previous_kind != "book_64_color_palette":
            continue
        target_word, zero_word = struct.unpack_from("<HH", blob, descriptor_start)
        if zero_word != 0:
            continue
        if not (reference_start + 2 <= target_word < next_end):
            continue
        add_book_control_descriptor(
            descriptor_start,
            descriptor_end,
            "book_palette_pointer_control_descriptor",
            previous_kind,
            next_kind,
        )

    pointer_target_name_prefixes = []
    occupied_ranges = merge_ranges(occupied_ranges)

    for target_start in pointer_targets:
        if not (0 < target_start < len(blob)):
            continue
        best_prefix = None
        scan_start = max(0, target_start - 32)
        for name_start in range(scan_start, target_start):
            if not range_is_currently_free(name_start, target_start):
                continue
            if name_start > 0 and 0x20 <= blob[name_start - 1] <= 0x7E:
                continue
            nul_position = blob.find(b"\x00", name_start, min(len(blob), target_start + 3))
            if nul_position == -1:
                continue
            if not (target_start - 2 <= nul_position <= target_start + 2):
                continue
            name_bytes = blob[name_start:nul_position]
            if not (3 <= len(name_bytes) <= 31):
                continue
            if not all(0x20 <= byte <= 0x7E for byte in name_bytes):
                continue
            if any(byte != 0 for byte in blob[nul_position:min(target_start, len(blob))]):
                continue
            best_prefix = (name_start, nul_position, name_bytes)
            break
        if best_prefix is None:
            continue
        name_start, nul_position, name_bytes = best_prefix
        if name_start >= target_start:
            continue
        prefix = {
            "kind": "book_pointer_target_name_prefix",
            "offset": record_start + name_start,
            "local_offset": name_start,
            "end": record_start + target_start,
            "end_local_offset": target_start,
            "size": target_start - name_start,
            "name": name_bytes.decode("cp1252"),
            "name_offset": record_start + name_start,
            "name_local_offset": name_start,
            "name_nul_offset": record_start + nul_position,
            "name_nul_local_offset": nul_position,
            "target_offset": record_start + target_start,
            "target_local_offset": target_start,
        }
        pointer_target_name_prefixes.append(prefix)
        occupied_ranges.append((name_start, target_start))
        segments.append(prefix)
        occupied_ranges = merge_ranges(occupied_ranges)

    pointer_target_leading_descriptors = []
    occupied_ranges = merge_ranges(occupied_ranges)
    for name_prefix in pointer_target_name_prefixes:
        descriptor_end = int(name_prefix["local_offset"])
        previous_end = max((end for _start, end in occupied_ranges if end <= descriptor_end), default=0)
        descriptor_start = previous_end
        descriptor_size = descriptor_end - descriptor_start
        if not (4 <= descriptor_size <= 32 and descriptor_size % 2 == 0):
            continue
        if not range_is_currently_free(descriptor_start, descriptor_end):
            continue
        descriptor_bytes = blob[descriptor_start:descriptor_end]
        if all(byte == 0 for byte in descriptor_bytes):
            continue
        words = [
            struct.unpack_from("<H", descriptor_bytes, index)[0]
            for index in range(0, len(descriptor_bytes), 2)
        ]
        descriptor = {
            "kind": "book_pointer_target_leading_descriptor",
            "offset": record_start + descriptor_start,
            "local_offset": descriptor_start,
            "end": record_start + descriptor_end,
            "end_local_offset": descriptor_end,
            "size": descriptor_size,
            "words": words,
            "target_offset": name_prefix["target_offset"],
            "target_local_offset": name_prefix["target_local_offset"],
            "name_prefix_offset": name_prefix["offset"],
            "name_prefix_local_offset": name_prefix["local_offset"],
            "name_prefix": name_prefix["name"],
        }
        nul_positions = [
            descriptor_start + index
            for index, byte in enumerate(descriptor_bytes)
            if byte == 0
        ]
        printable_runs = []
        run_start = None
        for index, byte in enumerate(descriptor_bytes + b"\x00"):
            if 0x20 <= byte <= 0x7E:
                if run_start is None:
                    run_start = index
                continue
            if run_start is not None and index - run_start >= 3:
                printable_runs.append(
                    (run_start, descriptor_bytes[run_start:index].decode("cp1252"))
                )
            run_start = None
        descriptor["nul_local_offsets"] = nul_positions
        descriptor["printable_runs"] = [
            {
                "offset": record_start + descriptor_start + run_offset,
                "local_offset": descriptor_start + run_offset,
                "text": text,
            }
            for run_offset, text in printable_runs
        ]
        pointer_target_leading_descriptors.append(descriptor)
        occupied_ranges.append((descriptor_start, descriptor_end))
        segments.append(descriptor)
        occupied_ranges = merge_ranges(occupied_ranges)

    zero_reserved_gaps = []
    occupied_ranges = merge_ranges(occupied_ranges)
    cursor = 0
    for occupied_start, occupied_end in occupied_ranges:
        if cursor < occupied_start:
            gap = blob[cursor:occupied_start]
            if len(gap) >= 2 and all(byte == 0 for byte in gap):
                zero_reserved_gaps.append(
                    {
                        "kind": "book_zero_reserved_gap",
                        "offset": record_start + cursor,
                        "local_offset": cursor,
                        "end": record_start + occupied_start,
                        "end_local_offset": occupied_start,
                        "size": occupied_start - cursor,
                    }
                )
                segments.append(zero_reserved_gaps[-1])
        cursor = max(cursor, occupied_end)
    if cursor < len(blob):
        gap = blob[cursor:]
        if len(gap) >= 2 and all(byte == 0 for byte in gap):
            zero_reserved_gaps.append(
                {
                    "kind": "book_zero_reserved_gap",
                    "offset": record_start + cursor,
                    "local_offset": cursor,
                    "end": record_start + len(blob),
                    "end_local_offset": len(blob),
                    "size": len(blob) - cursor,
                }
            )
            segments.append(zero_reserved_gaps[-1])

    return {
        "kind": "book_payload",
        "common_native_header": common_native_header,
        "segments": sorted(segments, key=lambda item: (int(item["local_offset"]), int(item["end_local_offset"]))),
        "reference_blocks": reference_blocks,
        "palette": palette,
        "pointer_tables": pointer_tables,
        "pointer_table_reference_words": pointer_table_reference_words,
        "pre_pointer_descriptor_blocks": pre_pointer_descriptor_blocks,
        "compact_named_descriptors": compact_named_descriptors,
        "pre_pointer_count_descriptors": pre_pointer_count_descriptors,
        "compact_descriptor_payload_fragments": compact_descriptor_payload_fragments,
        "named_payload_reference_descriptors": named_payload_reference_descriptors,
        "named_payload_reference_inline_prefixes": named_payload_reference_inline_prefixes,
        "openscript_objects": openscript_objects,
        "openscript_auxiliary_prefixes": openscript_auxiliary_prefixes,
        "openscript_duplicate_tails": openscript_duplicate_tails,
        "openscript_record_links": openscript_record_links,
        "book_control_descriptors": book_control_descriptors,
        "pointer_target_name_prefixes": pointer_target_name_prefixes,
        "pointer_target_leading_descriptors": pointer_target_leading_descriptors,
        "named_payload_reference_payload_fragments": named_payload_reference_payload_fragments,
        "pointer_target_payload_fragments": pointer_target_payload_fragments,
        "zero_padding_runs": zero_runs,
        "zero_reserved_gaps": zero_reserved_gaps,
    }


def annotate_stored_text_object_owners(values: list[dict[str, object]], blob: bytes) -> int:
    matched = 0
    native_object_classes = set(RUNTIME_OBJECT_CLASS_NAMES)
    for value in values:
        value_pos = int(value["value_body_local_offset"])
        owner = None
        for local in range(max(0, value_pos - 0x300), max(0, value_pos - 3)):
            if local + 12 > len(blob):
                continue
            text_pointer, class_id, object_id, flags = struct.unpack_from("<HHHH", blob, local)
            if text_pointer != value_pos - 3 or class_id not in native_object_classes:
                continue
            owner = {
                "kind": "native_object_text_pointer",
                "object_header_local_offset": local,
                "object_header_offset": int(value["value_body_offset"]) - value_pos + local,
                "object_class_id": class_id,
                "object_class_name": RUNTIME_OBJECT_CLASS_NAMES.get(class_id, "unknown"),
                "object_id": object_id,
                "object_flags": flags,
                "text_pointer_word": text_pointer,
            }
            if blob[local + 8 : local + 10] == b"\x14\x00":
                owner.update(
                    {
                        "record_reference_marker_local_offset": local + 8,
                        "record_reference_target_key": struct.unpack_from("<H", blob, local + 10)[0],
                    }
                )
        if owner:
            value["object_owner"] = owner
            matched += 1
            continue
        for local in range(max(0, value_pos - 0x400), max(0, value_pos - 0x20)):
            if local + 0x40 > len(blob):
                continue
            name_pointer, class_id, object_id, flags = struct.unpack_from("<HHHH", blob, local)
            text_pointer = struct.unpack_from("<H", blob, local + 0x36)[0]
            if class_id != 10 or text_pointer != value_pos - 3:
                continue
            object_name = ""
            if 0 <= name_pointer < len(blob):
                end = blob.find(b"\0", name_pointer, min(len(blob), name_pointer + 0x80))
                if end > name_pointer:
                    raw_name = blob[name_pointer:end]
                    if is_toolbook_text_bytes(raw_name):
                        object_name = raw_name.decode("cp1252", "replace")
            owner = {
                "kind": "native_object_named_field_text_pointer",
                "object_header_local_offset": local,
                "object_header_offset": int(value["value_body_offset"]) - value_pos + local,
                "object_class_id": class_id,
                "object_class_name": RUNTIME_OBJECT_CLASS_NAMES.get(class_id, "unknown"),
                "object_id": object_id,
                "object_flags": flags,
                "object_name_pointer": name_pointer,
                "object_name": object_name,
                "text_pointer_word": text_pointer,
                "text_pointer_local_offset": local + 0x36,
            }
        if owner:
            value["object_owner"] = owner
            matched += 1
            continue
        for local in range(max(0, value_pos - 0x1000), max(0, value_pos - 0x10)):
            if local + 4 > len(blob):
                continue
            class_id = struct.unpack_from("<H", blob, local + 2)[0]
            if class_id not in {8, 9, 10, 11, 21, 22, 25}:
                continue
            pointer_rel = None
            for rel in range(0, min(0x100, len(blob) - local - 1), 2):
                if struct.unpack_from("<H", blob, local + rel)[0] == value_pos - 3:
                    pointer_rel = rel
            if pointer_rel is None:
                continue
            first_word, _class_id, object_id, flags = struct.unpack_from("<HHHH", blob, local)
            object_name = ""
            if 0 <= first_word < len(blob):
                end = blob.find(b"\0", first_word, min(len(blob), first_word + 0x80))
                if end > first_word:
                    raw_name = blob[first_word:end]
                    if is_toolbook_text_bytes(raw_name):
                        object_name = raw_name.decode("cp1252", "replace")
            owner = {
                "kind": "native_object_variable_text_pointer",
                "object_header_local_offset": local,
                "object_header_offset": int(value["value_body_offset"]) - value_pos + local,
                "object_class_id": class_id,
                "object_class_name": RUNTIME_OBJECT_CLASS_NAMES.get(class_id, "unknown"),
                "object_id": object_id,
                "object_flags": flags,
                "object_first_word": first_word,
                "object_name": object_name,
                "text_pointer_word": value_pos - 3,
                "text_pointer_local_offset": local + pointer_rel,
                "text_pointer_relative_offset": pointer_rel,
            }
        if owner:
            value["object_owner"] = owner
            matched += 1
            continue
        if value_pos >= 10:
            prefix_word, class_id, object_id, flags, trailing_word = struct.unpack_from("<HHHHH", blob, value_pos - 10)
            if class_id == 11:
                value["object_owner"] = {
                    "kind": "native_object_inline_class_prefix",
                    "object_header_local_offset": value_pos - 10,
                    "object_header_offset": int(value["value_body_offset"]) - 10,
                    "object_class_id": class_id,
                    "object_class_name": RUNTIME_OBJECT_CLASS_NAMES.get(class_id, "unknown"),
                    "object_id": object_id,
                    "object_flags": flags,
                    "prefix_word": prefix_word,
                    "trailing_word": trailing_word,
                }
                matched += 1
                continue
    return matched


def annotate_stored_text_storage_prefixes(values: list[dict[str, object]], blob: bytes) -> int:
    matched = 0
    for value in values:
        if "object_owner" in value:
            continue
        value_pos = int(value["value_body_local_offset"])
        capacity_word = int(value["capacity_word"])
        if value_pos < 10:
            continue
        words = struct.unpack_from("<HHHHH", blob, value_pos - 10)
        word0, word1, word2, word3, word4 = words
        prefix_kind = ""
        prefix_offset_delta = 10
        prefix_words: list[int] = list(words)
        if value_pos >= 16:
            extended_words = struct.unpack_from("<HHHHHHHH", blob, value_pos - 16)
            if (
                extended_words[0] == value_pos + 5
                and extended_words[1] == 0
                and extended_words[2] == value_pos + capacity_word + 16
                and extended_words[3] == value_pos + 8
                and extended_words[4] in {0, 1}
                and extended_words[5] == 0
                and extended_words[6] == 0
                and extended_words[7] == value_pos + capacity_word + 13
            ):
                prefix_kind = "native_text_extended_storage_prefix"
                prefix_offset_delta = 16
                prefix_words = list(extended_words)
        if (
            not prefix_kind
            and
            word0 == value_pos + 5
            and word1 == 0
            and word3 == value_pos + 8
            and word2 in {0, value_pos + capacity_word + 16}
            and word4 in {1, value_pos + capacity_word + 13, value_pos + capacity_word + 15, value_pos + capacity_word + 17}
        ):
            prefix_kind = "native_text_allocation_prefix"
        elif (
            word0 == value_pos + 5
            and word1 == 0
            and word2 == 0x8001
            and word3 == value_pos - 14
            and word4 in {value_pos + capacity_word + 13, value_pos + capacity_word + 15, value_pos + capacity_word + 17}
        ):
            prefix_kind = "native_text_title_prefix"
        if not prefix_kind:
            continue
        value["storage_prefix"] = {
            "kind": prefix_kind,
            "prefix_offset": int(value["value_body_offset"]) - prefix_offset_delta,
            "prefix_local_offset": value_pos - prefix_offset_delta,
            "words": prefix_words,
            "word0_delta_from_value_body": prefix_words[0] - value_pos,
            "word2_delta_from_value_body": prefix_words[2] - value_pos if len(prefix_words) > 2 else None,
            "word3_delta_from_value_body": prefix_words[3] - value_pos if len(prefix_words) > 3 else None,
            "word4_delta_from_value_body": prefix_words[4] - value_pos if len(prefix_words) > 4 else None,
        }
        matched += 1
    return matched


def decode_embedded_native_text_objects(row: dict[str, object], blob: bytes, record_start: int) -> list[dict[str, object]]:
    objects = []
    for value in row.get("typed_text_values", []):
        if not isinstance(value, dict):
            continue
        owner = value.get("object_owner")
        if not isinstance(owner, dict):
            continue
        owner_kind = owner.get("kind")
        value_local = int(value["value_body_local_offset"])
        header_local = int(owner["object_header_local_offset"])
        if owner_kind == "native_object_text_pointer":
            prefix_size = value_local - header_local
            if prefix_size != 0x40 or header_local < 0 or value_local > len(blob):
                continue
            prefix = blob[header_local:value_local]
            words = list(struct.unpack("<" + "H" * (len(prefix) // 2), prefix))
            storage_words = list(struct.unpack_from("<HHHHH", blob, value_local - 10))
            objects.append(
                {
                    "kind": "embedded_native_text_object",
                    "object_format": "field_64_byte_prefix_before_text_value",
                    "object_offset": record_start + header_local,
                    "object_local_offset": header_local,
                    "prefix_size": prefix_size,
                    "record_class_name": row["header"].get("class_name"),
                    "record_name": row["header"].get("name"),
                    "object_class_id": owner.get("object_class_id"),
                    "object_class_name": owner.get("object_class_name"),
                    "object_id": owner.get("object_id"),
                    "object_flags": owner.get("object_flags"),
                    "text_pointer_word": owner.get("text_pointer_word"),
                    "text_pointer_expected": value_local - 3,
                    "prefix_words": words,
                    "storage_descriptor_local_offset": value_local - 10,
                    "storage_descriptor_words": storage_words,
                    "text_value_local_offset": value_local,
                    "text_value_offset": int(value["value_body_offset"]),
                    "text_capacity_word": value.get("capacity_word"),
                    "text_length": value.get("text_length"),
                    "text_preview": str(value.get("text", ""))[:120],
                }
            )
        elif owner_kind == "native_object_named_field_text_pointer":
            prefix_size = value_local - header_local
            if prefix_size not in {0x4E, 0x54} or header_local < 0 or value_local > len(blob):
                continue
            prefix = blob[header_local:value_local]
            objects.append(
                {
                    "kind": "embedded_native_text_object",
                    "object_format": "named_field_prefix_before_text_value",
                    "object_offset": record_start + header_local,
                    "object_local_offset": header_local,
                    "prefix_size": prefix_size,
                    "record_class_name": row["header"].get("class_name"),
                    "record_name": row["header"].get("name"),
                    "object_class_id": owner.get("object_class_id"),
                    "object_class_name": owner.get("object_class_name"),
                    "object_id": owner.get("object_id"),
                    "object_flags": owner.get("object_flags"),
                    "object_name_pointer": owner.get("object_name_pointer"),
                    "object_name": owner.get("object_name"),
                    "text_pointer_word": owner.get("text_pointer_word"),
                    "text_pointer_expected": value_local - 3,
                    "text_pointer_local_offset": owner.get("text_pointer_local_offset"),
                    "prefix_words": list(struct.unpack("<" + "H" * (len(prefix) // 2), prefix)),
                    "storage_descriptor_local_offset": value_local - 10,
                    "storage_descriptor_words": list(struct.unpack_from("<HHHHH", blob, value_local - 10)),
                    "text_value_local_offset": value_local,
                    "text_value_offset": int(value["value_body_offset"]),
                    "text_capacity_word": value.get("capacity_word"),
                    "text_length": value.get("text_length"),
                    "text_preview": str(value.get("text", ""))[:120],
                }
            )
        elif owner_kind == "native_object_variable_text_pointer":
            prefix_size = value_local - header_local
            if prefix_size <= 0 or prefix_size > 0x1000 or header_local < 0 or value_local > len(blob):
                continue
            prefix = blob[header_local:value_local]
            if len(prefix) % 2:
                prefix = prefix[:-1]
            objects.append(
                {
                    "kind": "embedded_native_text_object",
                    "object_format": "variable_offset_text_pointer_before_text_value",
                    "object_offset": record_start + header_local,
                    "object_local_offset": header_local,
                    "prefix_size": prefix_size,
                    "record_class_name": row["header"].get("class_name"),
                    "record_name": row["header"].get("name"),
                    "object_class_id": owner.get("object_class_id"),
                    "object_class_name": owner.get("object_class_name"),
                    "object_id": owner.get("object_id"),
                    "object_flags": owner.get("object_flags"),
                    "object_first_word": owner.get("object_first_word"),
                    "object_name": owner.get("object_name"),
                    "text_pointer_word": owner.get("text_pointer_word"),
                    "text_pointer_expected": value_local - 3,
                    "text_pointer_local_offset": owner.get("text_pointer_local_offset"),
                    "text_pointer_relative_offset": owner.get("text_pointer_relative_offset"),
                    "prefix_words": list(struct.unpack("<" + "H" * (len(prefix) // 2), prefix)),
                    "storage_descriptor_local_offset": value_local - 10,
                    "storage_descriptor_words": list(struct.unpack_from("<HHHHH", blob, value_local - 10)),
                    "text_value_local_offset": value_local,
                    "text_value_offset": int(value["value_body_offset"]),
                    "text_capacity_word": value.get("capacity_word"),
                    "text_length": value.get("text_length"),
                    "text_preview": str(value.get("text", ""))[:120],
                }
            )
        elif owner_kind == "native_object_inline_class_prefix":
            if value_local - header_local != 10:
                continue
            objects.append(
                {
                    "kind": "embedded_native_text_object",
                    "object_format": "class_11_inline_prefix_before_text_value",
                    "object_offset": record_start + header_local,
                    "object_local_offset": header_local,
                    "prefix_size": 10,
                    "record_class_name": row["header"].get("class_name"),
                    "record_name": row["header"].get("name"),
                    "object_class_id": owner.get("object_class_id"),
                    "object_class_name": owner.get("object_class_name"),
                    "object_id": owner.get("object_id"),
                    "object_flags": owner.get("object_flags"),
                    "prefix_word": owner.get("prefix_word"),
                    "trailing_word": owner.get("trailing_word"),
                    "prefix_words": list(struct.unpack_from("<HHHHH", blob, header_local)),
                    "text_value_local_offset": value_local,
                    "text_value_offset": int(value["value_body_offset"]),
                    "text_capacity_word": value.get("capacity_word"),
                    "text_length": value.get("text_length"),
                    "text_preview": str(value.get("text", ""))[:120],
                }
            )
    return objects


def extract_content_text(
    data: bytes,
    native_segments: list[NativeSegment],
    excluded_ranges: Iterable[tuple[int, int]] = (),
) -> list[dict[str, object]]:
    native_ranges = [(seg.offset, seg.end) for seg in native_segments]
    excluded = list(excluded_ranges)
    blocks: list[dict[str, object]] = []
    # Keep ASCII plus CP1252/Latin-1 printable bytes 0xA0-0xFF. Split on
    # 0x80-0x9F because those bytes are commonly ToolBook/OpenScript tokens in
    # these samples, even though CP1252 maps them to printable punctuation.
    for match in re.finditer(rb"[\x09\x0a\x0d\x20-\x7e\xa0-\xff]{3,}", data):
        if not in_ranges(match.start(), native_ranges):
            continue
        if in_ranges(match.start(), excluded):
            continue
        if match.start() < 0x100 and data.startswith(TBK_MAGIC):
            continue
        raw = match.group(0).strip(b"\0")
        if len(raw) < 3:
            continue
        text = raw.decode("cp1252", "replace")
        if looks_like_gibberish(text):
            continue
        blocks.append(
            {
                "offset": match.start(),
                "size": match.end() - match.start(),
                "kind": classify_content_text(text),
                "text": text,
            }
        )
    return blocks


def analyze_native_records(data: bytes, native_index: NativeIndex) -> dict[str, object]:
    key_to_record: dict[int, dict[str, object]] = {}
    record_rows: list[dict[str, object]] = []
    class_counts: dict[str, int] = {}
    duplicate_keys: list[dict[str, object]] = []

    for record_number, entry in enumerate(native_index.records, 1):
        blob = data[entry.absolute_offset : entry.end]
        header: dict[str, object] = {
            "valid": False,
            "error": "record shorter than 0x12-byte native object header",
        }
        if len(blob) >= 0x12:
            key, declared_body_length, aux_length_0, aux_length_1 = struct.unpack_from("<HHHH", blob, 0)
            child_count_or_flags = blob[0x08]
            status_flags = blob[0x09]
            type_word, class_id, object_id, owner_or_reserved = struct.unpack_from("<HHHH", blob, 0x0A)
            class_name = RUNTIME_OBJECT_CLASS_NAMES.get(class_id, "unknown")
            name = decode_native_record_name(blob)
            header = {
                "valid": True,
                "key": key,
                "declared_body_length": declared_body_length,
                "indexed_record_length": entry.length,
                "declared_length_matches_index": declared_body_length + 2 == entry.length,
                "aux_length_0": aux_length_0,
                "aux_length_1": aux_length_1,
                "child_count_or_flags": child_count_or_flags,
                "status_flags": status_flags,
                "type_word": type_word,
                "class_id": class_id,
                "class_name": class_name,
                "object_id": object_id,
                "owner_or_reserved": owner_or_reserved,
                "name_offset": entry.absolute_offset + 0x12,
                "name_size": min(0x20, max(0, len(blob) - 0x12)),
                "name": name,
                "name_is_direct_object_name": class_id in {4, 5},
            }
            class_key = f"{class_id}:{class_name}"
            class_counts[class_key] = class_counts.get(class_key, 0) + 1
            if key in key_to_record:
                duplicate_keys.append(
                    {
                        "key": key,
                        "first_record_number": key_to_record[key]["record_number"],
                        "duplicate_record_number": record_number,
                    }
                )
            key_to_record[key] = {
                "record_number": record_number,
                "offset": entry.absolute_offset,
                "size": entry.length,
                "class_id": class_id,
                "class_name": class_name,
                "object_id": object_id,
                "name": name,
            }

        record_rows.append(
            {
                "record_number": record_number,
                "offset": entry.absolute_offset,
                "size": entry.length,
                "end": entry.end,
                "index_entry_offset": entry.entry_offset,
                "index_page_size": entry.page_size,
                "index_depth": entry.depth,
                "header": header,
                "typed_payload": None,
                "record_reference_markers": [],
                "self_reference_offset_tables": [],
                "self_reference_child_object_spans": [],
                "page_background_offset_vectors": [],
                "terminal_child_pointer_tables": [],
                "field_hotword_run_tables": [],
                "book_payload": None,
                "page_background_payload": None,
                "typed_text_values": [],
                "embedded_native_objects": [],
                "text_blocks": [],
            }
        )

    total_candidate_14_markers = 0
    resolved_reference_markers = 0
    unresolved_candidate_14_markers = 0
    stored_text_object_owner_matches = 0
    stored_text_storage_prefix_matches = 0
    stored_text_capacity_tail_matches = 0
    content_blocks = extract_content_text(data, native_record_segments(native_index), ())
    blocks_by_record: dict[int, list[dict[str, object]]] = {}
    for block in content_blocks:
        absolute = int(block["offset"])
        for row in record_rows:
            if int(row["offset"]) <= absolute < int(row["end"]):
                blocks_by_record.setdefault(int(row["record_number"]), []).append(block)
                break

    total_text_blocks = 0
    for row in record_rows:
        record_start = int(row["offset"])
        record_end = int(row["end"])
        blob = data[record_start:record_end]
        if row["header"].get("class_id") == 2:
            row["typed_payload"] = decode_class2_directory(blob, record_start, key_to_record)
        elif row["header"].get("class_id") == 3:
            row["typed_payload"] = decode_class3_name_hash_table(
                blob,
                record_start,
                int(row["header"].get("object_id", 0)),
                int(row["header"].get("owner_or_reserved", 0)),
                key_to_record,
            )
        if row["header"].get("class_id") in {4, 5}:
            row["typed_text_values"] = decode_typed_text_values(blob, record_start)
            stored_text_capacity_tail_matches += annotate_stored_text_capacity_tails(row["typed_text_values"], blob)
            stored_text_object_owner_matches += annotate_stored_text_object_owners(row["typed_text_values"], blob)
            stored_text_storage_prefix_matches += annotate_stored_text_storage_prefixes(row["typed_text_values"], blob)
            existing_text_value_positions = {
                int(value["value_body_local_offset"]) for value in row["typed_text_values"]
            }
            inline_class11_text_values = [
                value
                for value in decode_inline_class11_text_values(blob, record_start)
                if int(value["value_body_local_offset"]) not in existing_text_value_positions
            ]
            stored_text_capacity_tail_matches += annotate_stored_text_capacity_tails(inline_class11_text_values, blob)
            row["typed_text_values"].extend(inline_class11_text_values)
            existing_text_value_positions.update(
                int(value["value_body_local_offset"]) for value in inline_class11_text_values
            )
            existing_text_value_ranges = [
                (
                    int(value["value_body_local_offset"]),
                    int(value["value_body_local_offset"]) + int(value.get("total_value_body_bytes", 0)),
                )
                for value in row["typed_text_values"]
            ]
            extended_inline_text_values = [
                value
                for value in decode_extended_inline_text_values(blob, record_start)
                if int(value["value_body_local_offset"]) not in existing_text_value_positions
                and not any(
                    int(value["value_body_local_offset"]) < existing_end
                    and int(value["value_body_local_offset"]) + int(value.get("total_value_body_bytes", 0)) > existing_start
                    for existing_start, existing_end in existing_text_value_ranges
                )
            ]
            row["typed_text_values"].extend(extended_inline_text_values)
            row["typed_text_values"].extend(decode_large_field_text_values(blob, record_start))
            row["typed_text_values"].sort(key=lambda value: int(value["text_offset"]))
            row["embedded_native_objects"] = decode_embedded_native_text_objects(row, blob, record_start)
        markers = []
        for local in range(0, max(0, len(blob) - 3)):
            if blob[local : local + 2] != b"\x14\x00":
                continue
            total_candidate_14_markers += 1
            target_key = struct.unpack_from("<H", blob, local + 2)[0]
            target = key_to_record.get(target_key)
            if not target:
                unresolved_candidate_14_markers += 1
                continue
            marker = {
                "offset": record_start + local,
                "local_offset": local,
                "target_key": target_key,
                "resolved": target is not None,
            }
            marker.update(
                {
                    "target_record_number": target["record_number"],
                    "target_class_id": target["class_id"],
                    "target_class_name": target["class_name"],
                    "target_object_id": target["object_id"],
                    "target_name": target["name"],
                }
            )
            markers.append(marker)
        resolved_reference_markers += len(markers)
        row["record_reference_markers"] = markers
        if row["header"].get("class_id") == 1:
            row["book_payload"] = decode_book_payload(row, blob, record_start)
        row["self_reference_offset_tables"] = decode_self_reference_offset_tables(row, blob, record_start)
        if row["header"].get("class_id") in {4, 5}:
            row["page_background_offset_vectors"] = decode_page_background_offset_vectors(row, blob, record_start)
            row["terminal_child_pointer_tables"] = decode_terminal_child_pointer_tables(row, blob, record_start)
        row["field_hotword_run_tables"] = decode_field_hotword_run_tables(row, blob, record_start)
        row["self_reference_child_object_spans"] = decode_self_reference_child_object_spans(row, blob, record_start)
        if row["header"].get("class_id") in {4, 5}:
            row["page_background_payload"] = decode_page_background_payload(row, blob, record_start)

        text_rows = []
        for block in blocks_by_record.get(int(row["record_number"]), []):
            total_text_blocks += 1
            text_rows.append(
                {
                    "offset": block["offset"],
                    "local_offset": int(block["offset"]) - record_start,
                    "size": block["size"],
                    "kind": block["kind"],
                    "text": block["text"],
                }
            )
        row["text_blocks"] = text_rows

    length_mismatch_count = sum(
        1 for row in record_rows if row["header"].get("valid") and not row["header"].get("declared_length_matches_index")
    )
    typed_class2_directories = [
        row for row in record_rows if isinstance(row.get("typed_payload"), dict)
        and row["typed_payload"].get("kind") == "class2_page_or_background_directory"
    ]
    typed_payload_records = len(typed_class2_directories)
    typed_directory_entries = sum(int(row["typed_payload"]["entry_count"]) for row in typed_class2_directories)
    typed_directory_value1_matches = sum(
        1
        for row in typed_class2_directories
        for entry in row["typed_payload"]["entries"]
        if entry["value1_matches_target_object_id"]
    )
    typed_payload_bytes = sum(
        int(row["typed_payload"]["entries_end"]) - int(row["typed_payload"]["entry_start"])
        + int(row["typed_payload"]["trailing_zero_padding_bytes"])
        for row in typed_class2_directories
    )
    class3_rows = [row for row in record_rows if row["header"].get("class_id") == 3]
    decoded_class3_tables = [
        row for row in class3_rows
        if isinstance(row.get("typed_payload"), dict)
        and row["typed_payload"].get("kind") == "class3_name_hash_table"
        and row["typed_payload"].get("decoded")
    ]
    failed_class3_tables = [
        row for row in class3_rows
        if isinstance(row.get("typed_payload"), dict)
        and row["typed_payload"].get("kind") == "class3_name_hash_table"
        and not row["typed_payload"].get("decoded")
    ]
    class3_entry_total = sum(int(row["header"].get("object_id", 0)) for row in class3_rows)
    class3_entries_decoded = sum(int(row["typed_payload"]["entry_count"]) for row in decoded_class3_tables)
    class3_segments = [
        segment
        for row in decoded_class3_tables
        for segment in row["typed_payload"].get("segments", [])
        if isinstance(segment, dict)
    ]
    class3_segment_bytes = range_total(
        merge_ranges((int(segment["offset"]), int(segment["end"])) for segment in class3_segments)
    )
    class3_value_records = [
        value_record
        for row in decoded_class3_tables
        for value_record in row["typed_payload"].get("value_records", [])
        if isinstance(value_record, dict)
    ]
    class3_value_record_bytes = sum(int(value_record["size"]) for value_record in class3_value_records)
    class3_short_name_fields = [
        row["typed_payload"].get("short_name_field")
        for row in decoded_class3_tables
        if isinstance(row["typed_payload"].get("short_name_field"), dict)
    ]
    class3_short_name_field_bytes = sum(int(field["size"]) for field in class3_short_name_fields)
    class3_hash_table_bytes = sum(
        int(row["typed_payload"]["entries_end"]) - int(row["typed_payload"]["entry_start"])
        for row in decoded_class3_tables
    )
    class3_extra_hash_table_entries = [
        entry_segment
        for row in decoded_class3_tables
        for entry_segment in row["typed_payload"].get("extra_hash_table_entries", [])
        if isinstance(entry_segment, dict)
    ]
    class3_extra_hash_table_entry_slots = sum(
        int(entry_segment["entry_count"]) for entry_segment in class3_extra_hash_table_entries
    )
    class3_extra_hash_table_entry_bytes = sum(
        int(entry_segment["size"]) for entry_segment in class3_extra_hash_table_entries
    )
    class3_post_table_reference_tails = [
        tail
        for row in decoded_class3_tables
        for tail in row["typed_payload"].get("post_table_reference_tails", [])
        if isinstance(tail, dict)
    ]
    class3_post_table_reference_tail_bytes = sum(int(tail["size"]) for tail in class3_post_table_reference_tails)
    class3_post_table_value_prefixes = [
        prefix
        for row in decoded_class3_tables
        for prefix in row["typed_payload"].get("post_table_value_prefixes", [])
        if isinstance(prefix, dict)
    ]
    class3_post_table_value_prefix_bytes = sum(int(prefix["size"]) for prefix in class3_post_table_value_prefixes)
    class3_zero_padding_segments = [
        segment
        for row in decoded_class3_tables
        for segment in row["typed_payload"].get("zero_padding_segments", [])
        if isinstance(segment, dict)
    ]
    class3_zero_padding_bytes = sum(int(segment["size"]) for segment in class3_zero_padding_segments)
    typed_text_value_rows = [
        value
        for row in record_rows
        for value in row.get("typed_text_values", [])
    ]
    large_text_value_rows = [
        value
        for value in typed_text_value_rows
        if value.get("kind") == "large_field_text_value"
    ]
    typed_text_value_records = sum(1 for row in record_rows if row.get("typed_text_values"))
    typed_text_value_bytes = sum(int(value["total_value_body_bytes"]) for value in typed_text_value_rows)
    typed_text_capacity_tail_rows = [
        value["capacity_tail"]
        for value in typed_text_value_rows
        if isinstance(value.get("capacity_tail"), dict)
    ]
    typed_text_capacity_tail_bytes = sum(int(tail["tail_size"]) for tail in typed_text_capacity_tail_rows)
    typed_text_capacity_tail_nonzero_bytes = sum(
        int(tail["tail_nonzero_bytes"]) for tail in typed_text_capacity_tail_rows
    )
    typed_text_capacity_tail_text_values = sum(1 for tail in typed_text_capacity_tail_rows if tail.get("tail_text"))
    embedded_native_objects = [
        obj
        for row in record_rows
        for obj in row.get("embedded_native_objects", [])
    ]
    embedded_native_object_formats: dict[str, int] = {}
    for obj in embedded_native_objects:
        fmt = str(obj.get("object_format", "unknown"))
        embedded_native_object_formats[fmt] = embedded_native_object_formats.get(fmt, 0) + 1
    self_reference_tables = [
        table
        for row in record_rows
        for table in row.get("self_reference_offset_tables", [])
        if isinstance(table, dict)
    ]
    self_reference_table_entries = sum(int(table["entry_count"]) for table in self_reference_tables)
    self_reference_table_bytes = sum(int(table["table_size"]) for table in self_reference_tables)
    self_reference_table_nonzero_entries = sum(
        1
        for table in self_reference_tables
        for entry in table.get("entries", [])
        if isinstance(entry, dict) and int(entry.get("entry_pointer_local_offset", 0))
    )
    self_reference_table_linked_text_objects = sum(
        1
        for table in self_reference_tables
        for entry in table.get("entries", [])
        if isinstance(entry, dict) and isinstance(entry.get("linked_embedded_text_object"), dict)
    )
    self_reference_child_object_headers = sum(
        1
        for table in self_reference_tables
        for entry in table.get("entries", [])
        if isinstance(entry, dict) and isinstance(entry.get("child_object_header"), dict)
    )
    self_reference_child_object_spans = [
        span
        for row in record_rows
        for span in row.get("self_reference_child_object_spans", [])
        if isinstance(span, dict)
    ]
    self_reference_child_object_span_bytes = sum(int(span["span_size"]) for span in self_reference_child_object_spans)
    self_reference_final_child_object_spans = [
        span
        for span in self_reference_child_object_spans
        if span.get("span_end_reason") == "native_record_end"
    ]
    self_reference_final_child_object_span_bytes = sum(
        int(span["span_size"]) for span in self_reference_final_child_object_spans
    )
    field_hotword_run_tables = [
        table
        for row in record_rows
        for table in row.get("field_hotword_run_tables", [])
        if isinstance(table, dict)
    ]
    field_hotword_run_table_rows = sum(int(table["row_count"]) for table in field_hotword_run_tables)
    field_hotword_run_table_active_rows = sum(int(table["active_row_count"]) for table in field_hotword_run_tables)
    field_hotword_run_table_linked_rows = sum(int(table["linked_active_rows"]) for table in field_hotword_run_tables)
    field_hotword_run_table_bytes = sum(int(table["table_size"]) for table in field_hotword_run_tables)
    page_background_offset_vectors = [
        vector
        for row in record_rows
        for vector in row.get("page_background_offset_vectors", [])
        if isinstance(vector, dict)
    ]
    page_background_offset_vector_bytes = sum(int(vector["size"]) for vector in page_background_offset_vectors)
    page_background_offset_vector_offsets = sum(
        int(vector["offset_count"]) for vector in page_background_offset_vectors
    )
    page_background_offset_vector_nonzero_offsets = sum(
        int(vector["nonzero_offset_count"]) for vector in page_background_offset_vectors
    )
    page_background_payloads = [
        row.get("page_background_payload")
        for row in record_rows
        if isinstance(row.get("page_background_payload"), dict)
    ]
    page_background_payload_segments = [
        segment
        for payload in page_background_payloads
        for segment in payload.get("segments", [])
        if isinstance(segment, dict)
    ]
    page_background_payload_segment_bytes = range_total(
        merge_ranges((int(segment["offset"]), int(segment["end"])) for segment in page_background_payload_segments)
    )
    page_background_bounded_payload_fragments = [
        fragment
        for payload in page_background_payloads
        for fragment in payload.get("bounded_payload_fragments", [])
        if isinstance(fragment, dict)
    ]
    page_background_bounded_payload_fragment_bytes = sum(
        int(fragment["size"]) for fragment in page_background_bounded_payload_fragments
    )
    book_payloads = [
        row.get("book_payload")
        for row in record_rows
        if isinstance(row.get("book_payload"), dict)
    ]
    book_payload_segments = [
        segment
        for payload in book_payloads
        for segment in payload.get("segments", [])
        if isinstance(segment, dict)
    ]
    book_payload_segment_bytes = range_total(
        merge_ranges((int(segment["offset"]), int(segment["end"])) for segment in book_payload_segments)
    )
    book_common_native_headers = [
        payload.get("common_native_header")
        for payload in book_payloads
        if isinstance(payload.get("common_native_header"), dict)
    ]
    book_common_native_header_bytes = sum(int(header["size"]) for header in book_common_native_headers)
    book_reference_blocks = sum(len(payload.get("reference_blocks", [])) for payload in book_payloads)
    book_control_descriptors = [
        descriptor
        for payload in book_payloads
        for descriptor in payload.get("book_control_descriptors", [])
        if isinstance(descriptor, dict)
    ]
    book_control_descriptor_bytes = sum(int(descriptor["size"]) for descriptor in book_control_descriptors)
    book_pointer_target_name_prefixes = [
        prefix
        for payload in book_payloads
        for prefix in payload.get("pointer_target_name_prefixes", [])
        if isinstance(prefix, dict)
    ]
    book_pointer_target_name_prefix_bytes = sum(
        int(prefix["size"]) for prefix in book_pointer_target_name_prefixes
    )
    book_pointer_target_leading_descriptors = [
        descriptor
        for payload in book_payloads
        for descriptor in payload.get("pointer_target_leading_descriptors", [])
        if isinstance(descriptor, dict)
    ]
    book_pointer_target_leading_descriptor_bytes = sum(
        int(descriptor["size"]) for descriptor in book_pointer_target_leading_descriptors
    )
    book_named_payload_reference_inline_prefixes = [
        prefix
        for payload in book_payloads
        for prefix in payload.get("named_payload_reference_inline_prefixes", [])
        if isinstance(prefix, dict)
    ]
    book_named_payload_reference_inline_prefix_bytes = sum(
        int(prefix["size"]) for prefix in book_named_payload_reference_inline_prefixes
    )
    book_palette_entries = sum(
        int(payload["palette"]["entry_count"])
        for payload in book_payloads
        if isinstance(payload.get("palette"), dict)
    )
    book_pointer_tables = [
        table
        for payload in book_payloads
        for table in payload.get("pointer_tables", [])
        if isinstance(table, dict)
    ]
    book_pointer_table_entries = sum(int(table["entry_count"]) for table in book_pointer_tables)
    book_pointer_table_bytes = sum(int(table["table_size"]) for table in book_pointer_tables)
    book_pointer_table_reference_words = [
        word
        for payload in book_payloads
        for word in payload.get("pointer_table_reference_words", [])
        if isinstance(word, dict)
    ]
    book_pointer_table_reference_bytes = sum(int(word["size"]) for word in book_pointer_table_reference_words)
    book_pre_pointer_descriptor_blocks = [
        block
        for payload in book_payloads
        for block in payload.get("pre_pointer_descriptor_blocks", [])
        if isinstance(block, dict)
    ]
    book_pre_pointer_descriptor_bytes = sum(int(block["size"]) for block in book_pre_pointer_descriptor_blocks)
    book_compact_named_descriptors = [
        block
        for payload in book_payloads
        for block in payload.get("compact_named_descriptors", [])
        if isinstance(block, dict)
    ]
    book_compact_named_descriptor_bytes = sum(int(block["size"]) for block in book_compact_named_descriptors)
    book_pre_pointer_count_descriptors = [
        block
        for payload in book_payloads
        for block in payload.get("pre_pointer_count_descriptors", [])
        if isinstance(block, dict)
    ]
    book_pre_pointer_count_descriptor_bytes = sum(
        int(block["size"]) for block in book_pre_pointer_count_descriptors
    )
    book_compact_descriptor_payload_fragments = [
        fragment
        for payload in book_payloads
        for fragment in payload.get("compact_descriptor_payload_fragments", [])
        if isinstance(fragment, dict)
    ]
    book_compact_descriptor_payload_fragment_bytes = sum(
        int(fragment["size"]) for fragment in book_compact_descriptor_payload_fragments
    )
    book_named_payload_reference_descriptors = [
        descriptor
        for payload in book_payloads
        for descriptor in payload.get("named_payload_reference_descriptors", [])
        if isinstance(descriptor, dict)
    ]
    book_named_payload_reference_descriptor_bytes = sum(
        int(descriptor["size"]) for descriptor in book_named_payload_reference_descriptors
    )
    book_openscript_objects = [
        script_object
        for payload in book_payloads
        for script_object in payload.get("openscript_objects", [])
        if isinstance(script_object, dict)
    ]
    book_openscript_object_bytes = sum(int(script_object["size"]) for script_object in book_openscript_objects)
    book_openscript_code_bytes = sum(int(script_object["code_size"]) for script_object in book_openscript_objects)
    book_openscript_auxiliary_prefixes = [
        prefix
        for payload in book_payloads
        for prefix in payload.get("openscript_auxiliary_prefixes", [])
        if isinstance(prefix, dict)
    ]
    book_openscript_auxiliary_prefix_bytes = sum(
        int(prefix["size"]) for prefix in book_openscript_auxiliary_prefixes
    )
    book_openscript_duplicate_tails = [
        tail
        for payload in book_payloads
        for tail in payload.get("openscript_duplicate_tails", [])
        if isinstance(tail, dict)
    ]
    book_openscript_duplicate_tail_bytes = sum(
        int(tail["size"]) for tail in book_openscript_duplicate_tails
    )
    book_openscript_record_links = [
        link
        for payload in book_payloads
        for link in payload.get("openscript_record_links", [])
        if isinstance(link, dict)
    ]
    book_openscript_record_link_bytes = sum(
        int(link["size"]) for link in book_openscript_record_links
    )
    book_pointer_target_payload_fragments = [
        fragment
        for payload in book_payloads
        for fragment in payload.get("pointer_target_payload_fragments", [])
        if isinstance(fragment, dict)
    ]
    book_pointer_target_payload_fragment_bytes = sum(
        int(fragment["size"]) for fragment in book_pointer_target_payload_fragments
    )
    book_named_payload_reference_payload_fragments = [
        fragment
        for payload in book_payloads
        for fragment in payload.get("named_payload_reference_payload_fragments", [])
        if isinstance(fragment, dict)
    ]
    book_named_payload_reference_payload_fragment_bytes = sum(
        int(fragment["size"]) for fragment in book_named_payload_reference_payload_fragments
    )
    book_zero_reserved_gaps = [
        gap
        for payload in book_payloads
        for gap in payload.get("zero_reserved_gaps", [])
        if isinstance(gap, dict)
    ]
    book_zero_reserved_gap_bytes = sum(int(gap["size"]) for gap in book_zero_reserved_gaps)
    return {
        "status": "native_record_headers_and_references",
        "note": (
            "This is a deterministic top-level record map. It decodes the indexed native record "
            "header and resolves 14 00 <record-key> markers against the active record index. "
            "It does not claim that every byte inside object payloads or OpenScript bytecode is semantically named."
        ),
        "counts": {
            "records": len(record_rows),
            "class_counts": class_counts,
            "duplicate_keys": len(duplicate_keys),
            "declared_length_mismatches": length_mismatch_count,
            "candidate_14_00_markers": total_candidate_14_markers,
            "resolved_record_reference_markers": resolved_reference_markers,
            "unresolved_candidate_14_00_markers": unresolved_candidate_14_markers,
            "self_reference_offset_tables": len(self_reference_tables),
            "self_reference_offset_table_entries": self_reference_table_entries,
            "self_reference_offset_table_nonzero_entries": self_reference_table_nonzero_entries,
            "self_reference_offset_table_linked_text_objects": self_reference_table_linked_text_objects,
            "self_reference_child_object_headers": self_reference_child_object_headers,
            "self_reference_child_object_header_bytes": self_reference_child_object_headers * 10,
            "self_reference_child_object_spans": len(self_reference_child_object_spans),
            "self_reference_child_object_span_bytes": self_reference_child_object_span_bytes,
            "self_reference_final_child_object_spans": len(self_reference_final_child_object_spans),
            "self_reference_final_child_object_span_bytes": self_reference_final_child_object_span_bytes,
            "self_reference_offset_table_bytes": self_reference_table_bytes,
            "field_hotword_run_tables": len(field_hotword_run_tables),
            "field_hotword_run_table_rows": field_hotword_run_table_rows,
            "field_hotword_run_table_active_rows": field_hotword_run_table_active_rows,
            "field_hotword_run_table_linked_rows": field_hotword_run_table_linked_rows,
            "field_hotword_run_table_bytes": field_hotword_run_table_bytes,
            "page_background_offset_vectors": len(page_background_offset_vectors),
            "page_background_offset_vector_bytes": page_background_offset_vector_bytes,
            "page_background_offset_vector_offsets": page_background_offset_vector_offsets,
            "page_background_offset_vector_nonzero_offsets": page_background_offset_vector_nonzero_offsets,
            "page_background_payloads": len(page_background_payloads),
            "page_background_payload_segments": len(page_background_payload_segments),
            "page_background_payload_segment_bytes": page_background_payload_segment_bytes,
            "page_background_bounded_payload_fragments": len(page_background_bounded_payload_fragments),
            "page_background_bounded_payload_fragment_bytes": page_background_bounded_payload_fragment_bytes,
            "book_payload_segments": len(book_payload_segments),
            "book_payload_segment_bytes": book_payload_segment_bytes,
            "book_common_native_headers": len(book_common_native_headers),
            "book_common_native_header_bytes": book_common_native_header_bytes,
            "book_reference_blocks": book_reference_blocks,
            "book_control_descriptors": len(book_control_descriptors),
            "book_control_descriptor_bytes": book_control_descriptor_bytes,
            "book_pointer_target_name_prefixes": len(book_pointer_target_name_prefixes),
            "book_pointer_target_name_prefix_bytes": book_pointer_target_name_prefix_bytes,
            "book_pointer_target_leading_descriptors": len(book_pointer_target_leading_descriptors),
            "book_pointer_target_leading_descriptor_bytes": book_pointer_target_leading_descriptor_bytes,
            "book_palette_entries": book_palette_entries,
            "book_pointer_tables": len(book_pointer_tables),
            "book_pointer_table_entries": book_pointer_table_entries,
            "book_pointer_table_bytes": book_pointer_table_bytes,
            "book_pointer_table_reference_words": len(book_pointer_table_reference_words),
            "book_pointer_table_reference_bytes": book_pointer_table_reference_bytes,
            "book_pre_pointer_descriptor_blocks": len(book_pre_pointer_descriptor_blocks),
            "book_pre_pointer_descriptor_bytes": book_pre_pointer_descriptor_bytes,
            "book_compact_named_descriptors": len(book_compact_named_descriptors),
            "book_compact_named_descriptor_bytes": book_compact_named_descriptor_bytes,
            "book_pre_pointer_count_descriptors": len(book_pre_pointer_count_descriptors),
            "book_pre_pointer_count_descriptor_bytes": book_pre_pointer_count_descriptor_bytes,
            "book_compact_descriptor_payload_fragments": len(book_compact_descriptor_payload_fragments),
            "book_compact_descriptor_payload_fragment_bytes": book_compact_descriptor_payload_fragment_bytes,
            "book_named_payload_reference_descriptors": len(book_named_payload_reference_descriptors),
            "book_named_payload_reference_descriptor_bytes": book_named_payload_reference_descriptor_bytes,
            "book_named_payload_reference_inline_prefixes": len(
                book_named_payload_reference_inline_prefixes
            ),
            "book_named_payload_reference_inline_prefix_bytes": (
                book_named_payload_reference_inline_prefix_bytes
            ),
            "book_openscript_objects": len(book_openscript_objects),
            "book_openscript_object_bytes": book_openscript_object_bytes,
            "book_openscript_code_bytes": book_openscript_code_bytes,
            "book_openscript_auxiliary_prefixes": len(book_openscript_auxiliary_prefixes),
            "book_openscript_auxiliary_prefix_bytes": book_openscript_auxiliary_prefix_bytes,
            "book_openscript_duplicate_tails": len(book_openscript_duplicate_tails),
            "book_openscript_duplicate_tail_bytes": book_openscript_duplicate_tail_bytes,
            "book_openscript_record_links": len(book_openscript_record_links),
            "book_openscript_record_link_bytes": book_openscript_record_link_bytes,
            "book_pointer_target_payload_fragments": len(book_pointer_target_payload_fragments),
            "book_pointer_target_payload_fragment_bytes": book_pointer_target_payload_fragment_bytes,
            "book_named_payload_reference_payload_fragments": len(book_named_payload_reference_payload_fragments),
            "book_named_payload_reference_payload_fragment_bytes": (
                book_named_payload_reference_payload_fragment_bytes
            ),
            "book_zero_reserved_gaps": len(book_zero_reserved_gaps),
            "book_zero_reserved_gap_bytes": book_zero_reserved_gap_bytes,
            "content_text_blocks_by_record": total_text_blocks,
            "typed_payload_records": typed_payload_records,
            "typed_directory_entries": typed_directory_entries,
            "typed_directory_entries_with_value1_matching_target_object_id": typed_directory_value1_matches,
            "typed_payload_or_padding_bytes": typed_payload_bytes,
            "class3_records": len(class3_rows),
            "class3_payload_segments": len(class3_segments),
            "class3_payload_segment_bytes": class3_segment_bytes,
            "class3_common_native_headers": len(decoded_class3_tables),
            "class3_common_native_header_bytes": len(decoded_class3_tables) * 0x12,
            "class3_short_name_fields": len(class3_short_name_fields),
            "class3_short_name_field_bytes": class3_short_name_field_bytes,
            "class3_typed_string_value_records": len(class3_value_records),
            "class3_typed_string_value_record_bytes": class3_value_record_bytes,
            "class3_name_hash_table_bytes": class3_hash_table_bytes,
            "class3_extra_hash_table_entry_segments": len(class3_extra_hash_table_entries),
            "class3_extra_hash_table_entry_slots": class3_extra_hash_table_entry_slots,
            "class3_extra_hash_table_entry_bytes": class3_extra_hash_table_entry_bytes,
            "class3_post_table_reference_tails": len(class3_post_table_reference_tails),
            "class3_post_table_reference_tail_bytes": class3_post_table_reference_tail_bytes,
            "class3_post_table_value_prefixes": len(class3_post_table_value_prefixes),
            "class3_post_table_value_prefix_bytes": class3_post_table_value_prefix_bytes,
            "class3_zero_padding_segments": len(class3_zero_padding_segments),
            "class3_zero_padding_bytes": class3_zero_padding_bytes,
            "class3_name_hash_table_records_decoded": len(decoded_class3_tables),
            "class3_name_hash_table_records_not_decoded": len(failed_class3_tables),
            "class3_name_hash_table_entries_total_from_object_ids": class3_entry_total,
            "class3_name_hash_table_entries_decoded": class3_entries_decoded,
            "class3_name_hash_table_entries_not_decoded": class3_entry_total - class3_entries_decoded,
            "typed_text_value_records": typed_text_value_records,
            "typed_text_values": len(typed_text_value_rows),
            "large_text_values": len(large_text_value_rows),
            "typed_text_value_body_bytes": typed_text_value_bytes,
            "typed_text_values_with_native_object_owner": stored_text_object_owner_matches,
            "typed_text_values_with_native_storage_prefix": stored_text_storage_prefix_matches,
            "typed_text_capacity_tail_values": len(typed_text_capacity_tail_rows),
            "typed_text_capacity_tail_bytes": typed_text_capacity_tail_bytes,
            "typed_text_capacity_tail_nonzero_bytes": typed_text_capacity_tail_nonzero_bytes,
            "typed_text_capacity_tail_text_values": typed_text_capacity_tail_text_values,
            "embedded_native_text_objects": len(embedded_native_objects),
            "embedded_native_text_object_formats": embedded_native_object_formats,
            "active_ranges_considered": len(native_index.record_ranges),
        },
        "duplicate_keys": duplicate_keys,
        "records": record_rows,
    }


def analyze_native_structure(
    data: bytes,
    tbk_offset: int,
    payload: bytes,
    media_hits: list[MediaHit],
    native_index: NativeIndex,
) -> dict[str, object]:
    header = parse_toolbook_header(payload)
    header_words = []
    for off in range(0, min(0x120, len(payload)), 4):
        value = struct.unpack_from("<I", payload + b"\0\0\0\0", off)[0]
        points_inside = 0 <= value < len(payload)
        header_words.append(
            {
                "offset": tbk_offset + off,
                "local_offset": off,
                "value_hex": f"0x{value:08x}",
                "points_inside_payload": bool(value and points_inside),
            }
        )

    segments = native_record_segments(native_index)
    native_rows = [
        {
            "name": seg.name,
            "role": seg.role,
            "offset": seg.offset,
            "size": seg.size,
            "end": seg.end,
            "description": seg.description,
        }
        for seg in segments
    ]

    envelope_rows = []
    for hit in media_hits:
        if not (tbk_offset <= hit.offset < tbk_offset + len(payload)):
            continue
        prefix_start = max(tbk_offset, hit.offset - 0x40)
        prefix = data[prefix_start : hit.offset]
        envelope_rows.append(
            {
                "media_offset": hit.offset,
                "media_size": hit.size,
                "kind": hit.kind,
                "prefix_offset": prefix_start,
                "prefix_size": len(prefix),
                "prefix_hex": prefix.hex(),
                "note": "Bytes immediately before the standalone media payload; often includes ToolBook resource-envelope metadata and padding.",
            }
        )

    ascii_records = extract_ascii_records(data)
    return {
        "status": "partial_native_reverse_engineering",
        "toolbook_magic": payload[:4].hex(),
        "toolbook_version_hex": payload[4:8].hex(),
        "toolbook_header": {
            "signature_hex": header.signature_hex,
            "format_id_hex": header.format_id_hex,
            "format_word0_hex": header.format_word0_hex,
            "format_word1_hex": header.format_word1_hex,
            "family": header.family,
            "fixed_header_size": header.fixed_header_size,
            "runtime_probe_size": header.runtime_probe_size,
            "first_native_offset": header.first_native_offset,
            "note": (
                "Static analysis of Runtime ToolBook 1.5 TBKBASE.DLL shows CDBFILEOPEN "
                "reads 0x116 bytes: the 0x100-byte fixed file header plus the first "
                "0x16 bytes of native stream data."
            ),
        },
        "tbk_offset": tbk_offset,
        "payload_size": len(payload),
        "header_words_le32": header_words,
        "native_segments": native_rows,
        "native_index": native_index_to_json(native_index),
        "embedded_media_envelopes": envelope_rows,
        "ascii_records": ascii_records,
        "native_records": analyze_native_records(data, native_index),
        "object_model": analyze_object_model(data, ascii_records, segments),
        "remaining_limitations": [
            "Native object records are segmented and byte-accounted but not fully typed.",
            "OpenScript bytecode/token streams are located by strings but not decompiled.",
            "The 20-byte allocation/index slot table seen in newer files is detected only as native bytes, not resolved into object ownership.",
            "ToolBook resource envelope fields before BMP payloads are exposed but not fully named.",
        ],
    }


def native_typed_text_values(native_analysis: dict[str, object]) -> list[dict[str, object]]:
    values = []
    native_records = native_analysis.get("native_records", {})
    if not isinstance(native_records, dict):
        return values
    for row in native_records.get("records", []):
        if not isinstance(row, dict):
            continue
        header = row.get("header", {})
        if not isinstance(header, dict):
            continue
        for value in row.get("typed_text_values", []):
            if not isinstance(value, dict):
                continue
            enriched = dict(value)
            enriched.update(
                {
                    "record_number": row.get("record_number"),
                    "record_offset": row.get("offset"),
                    "record_class_id": header.get("class_id"),
                    "record_class_name": header.get("class_name"),
                    "record_object_id": header.get("object_id"),
                    "record_name": header.get("name"),
                }
            )
            values.append(enriched)
    values.sort(key=lambda item: int(item["text_offset"]))
    return values


def extract_file(input_path: Path, output_dir: Path, verbose: bool = False) -> ExtractionResult:
    data = input_path.read_bytes()
    tbk_offset, wrapper_kind = locate_tbk_payload(data)
    payload = data[tbk_offset:]
    header = parse_toolbook_header(payload)
    native_index = parse_native_index(data, tbk_offset, payload)
    if not native_index.supported:
        raise ToolBookError(f"unsupported native ToolBook index: {native_index.reason}")
    active_record_ranges = native_index.record_ranges

    if output_dir.exists() and any(output_dir.iterdir()):
        raise ToolBookError(f"output directory already exists and is not empty: {output_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)
    chmod_group_readable(output_dir)

    files_written = 0
    if verbose and tbk_offset:
        write_bytes(output_dir / "wrapper_stub.exe", data[:tbk_offset])
        files_written += 1

    if verbose:
        write_bytes(output_dir / "toolbook_payload.tbkbin", payload)
        files_written += 1

    media_hits = find_media(data, 0, active_record_ranges)
    media_ranges = [(hit.offset, hit.end) for hit in media_hits]
    dib_hits = find_dibs(data, media_ranges, active_record_ranges)
    rejected_dibs = find_rejected_dib_candidates(data, media_ranges, dib_hits, active_record_ranges)
    native_icon_hits, native_icon_rejects = find_native_class41_icons(data, native_index)
    native_icon_offsets = {hit.offset for hit in native_icon_hits}
    native_icon_reject_offsets = {hit.offset for hit in native_icon_rejects}
    rejected_dibs = [
        hit
        for hit in rejected_dibs
        if hit.offset not in native_icon_offsets and hit.offset not in native_icon_reject_offsets
    ] + native_icon_rejects
    native_property_dib_hits = find_native_property_stream_dibs(data, native_index, rejected_dibs)
    native_property_dib_offsets = {hit.offset for hit in native_property_dib_hits}
    rejected_dibs = [hit for hit in rejected_dibs if hit.offset not in native_property_dib_offsets]
    native_nested_dib_hits = find_native_nested_dibs(data, native_index, rejected_dibs)
    native_nested_dib_offsets = {hit.dib.offset for hit in native_nested_dib_hits}
    rejected_dibs = [hit for hit in rejected_dibs if hit.offset not in native_nested_dib_offsets]
    media_dir = output_dir / "embedded_media" if verbose else output_dir
    media_counts = {kind: 0 for kind in SUPPORTED_MEDIA}
    media_manifest = []
    for idx, hit in enumerate(media_hits, 1):
        media_counts[hit.kind] += 1
        prefix = "" if verbose else "embedded_"
        name = f"{prefix}{idx:04d}_off_{hit.offset:08x}.{hit.extension}"
        blob = data[hit.offset : hit.end]
        write_bytes(media_dir / name, blob)
        files_written += 1
        media_manifest.append(
            {
                "name": name,
                "kind": hit.kind,
                "description": hit.description,
                "offset": hit.offset,
                "size": hit.size,
                "end": hit.end,
                "sha256": sha256_bytes(blob),
            }
        )
    if media_dir.exists():
        chmod_group_readable(media_dir)

    reconstructed_dir = output_dir / "content" / "images_reconstructed" if verbose else output_dir
    dib_manifest = []
    for idx, hit in enumerate(dib_hits, 1):
        dib = data[hit.offset : hit.end]
        bmp = build_bmp_from_dib(dib)
        name = (
            f"image_{idx:04d}_off_{hit.offset:08x}_{hit.width}x{hit.height}_"
            f"{hit.bits_per_pixel}bpp.bmp"
        )
        write_bytes(reconstructed_dir / name, bmp)
        files_written += 1
        dib_manifest.append(
            {
                "name": name,
                "offset": hit.offset,
                "dib_size": hit.dib_size,
                "bmp_size": len(bmp),
                "width": hit.width,
                "height": hit.height,
                "bits_per_pixel": hit.bits_per_pixel,
                "compression": hit.compression,
                "sha256": sha256_bytes(bmp),
            }
        )
    if reconstructed_dir.exists():
        chmod_group_readable(reconstructed_dir)

    property_dib_manifest = []
    for idx, hit in enumerate(native_property_dib_hits, 1):
        dib = data[hit.offset : hit.dib_info_end] + data[hit.pixel_source_offset : hit.end]
        bmp = build_bmp_from_dib(dib)
        image_index = len(dib_manifest) + idx
        name = (
            f"image_{image_index:04d}_off_{hit.offset:08x}_{hit.width}x{hit.height}_"
            f"{hit.bits_per_pixel}bpp.bmp"
        )
        write_bytes(reconstructed_dir / name, bmp)
        files_written += 1
        property_dib_manifest.append(
            {
                "name": name,
                "offset": hit.offset,
                "dib_info_end": hit.dib_info_end,
                "pixel_source_offset": hit.pixel_source_offset,
                "pixel_size": hit.pixel_size,
                "dib_size": len(dib),
                "bmp_size": len(bmp),
                "width": hit.width,
                "height": hit.height,
                "bits_per_pixel": hit.bits_per_pixel,
                "compression": hit.compression,
                "property_offset": hit.property_offset,
                "property_value_offset": hit.property_value_offset,
                "physical_width_twips": hit.physical_width_twips,
                "physical_height_twips": hit.physical_height_twips,
                "descriptor_pointer_offset": hit.descriptor_pointer_offset,
                "descriptor_pointer_value": hit.descriptor_pointer_value,
                "record_number": hit.record_number,
                "record_offset": hit.record_offset,
                "local_offset": hit.local_offset,
                "sha256": sha256_bytes(bmp),
            }
        )
    if reconstructed_dir.exists():
        chmod_group_readable(reconstructed_dir)

    nested_dib_manifest = []
    for idx, hit in enumerate(native_nested_dib_hits, 1):
        dib = data[hit.dib.offset : hit.dib.end]
        bmp = build_bmp_from_dib(dib)
        image_index = len(dib_manifest) + len(property_dib_manifest) + idx
        name = (
            f"image_{image_index:04d}_off_{hit.dib.offset:08x}_{hit.dib.width}x{hit.dib.height}_"
            f"{hit.dib.bits_per_pixel}bpp.bmp"
        )
        write_bytes(reconstructed_dir / name, bmp)
        files_written += 1
        nested_dib_manifest.append(
            {
                "name": name,
                "offset": hit.dib.offset,
                "parent_offset": hit.parent_offset,
                "chain_depth": hit.chain_depth,
                "record_number": hit.record_number,
                "record_offset": hit.record_offset,
                "local_offset": hit.local_offset,
                "dib_size": hit.dib.dib_size,
                "bmp_size": len(bmp),
                "width": hit.dib.width,
                "height": hit.dib.height,
                "bits_per_pixel": hit.dib.bits_per_pixel,
                "compression": hit.dib.compression,
                "sha256": sha256_bytes(bmp),
            }
        )
    if reconstructed_dir.exists():
        chmod_group_readable(reconstructed_dir)

    icon_manifest = []
    for idx, hit in enumerate(native_icon_hits, 1):
        dib = data[hit.offset : hit.end]
        ico = build_ico_from_dib_icon_payload(dib, hit.width, hit.height, hit.bits_per_pixel)
        name = f"icon_{idx:04d}_off_{hit.offset:08x}_{hit.width}x{hit.height}_{hit.bits_per_pixel}bpp.ico"
        write_bytes(reconstructed_dir / name, ico)
        files_written += 1
        icon_manifest.append(
            {
                "name": name,
                "offset": hit.offset,
                "size": hit.size,
                "stored_size": hit.stored_size,
                "padding_size": hit.padding_size,
                "end": hit.end,
                "width": hit.width,
                "height": hit.height,
                "bits_per_pixel": hit.bits_per_pixel,
                "record_number": hit.record_number,
                "record_offset": hit.record_offset,
                "local_offset": hit.local_offset,
                "sha256": sha256_bytes(ico),
            }
        )
    if reconstructed_dir.exists():
        chmod_group_readable(reconstructed_dir)

    compressed_dib_manifest = []
    for idx, hit in enumerate(rejected_dibs, 1):
        if rejected_dib_source_kind(data, hit, native_index) != "toolbook_compressed_dib_descriptor":
            continue
        payload_end = toolbook_compressed_dib_payload_end(data, native_index, hit)
        if payload_end is None:
            continue
        owner = native_record_for_offset(native_index, hit.offset)
        if owner is None:
            continue
        record_number, entry = owner
        end_pointer_value = struct.unpack_from("<I", data, hit.pixel_offset)[0]
        descriptor = data[hit.offset:payload_end]
        compressed_payload = data[hit.pixel_offset + 4 : payload_end]
        first_substream_size = (
            struct.unpack_from("<H", compressed_payload, 0)[0] if len(compressed_payload) >= 2 else 0
        )
        first_substream_offset = hit.pixel_offset + 6 if first_substream_size else 0
        first_substream_end = min(first_substream_offset + first_substream_size, payload_end)
        second_substream_offset = first_substream_end if first_substream_size else 0
        name = (
            f"compressed_dib_{len(compressed_dib_manifest) + 1:04d}_off_{hit.offset:08x}_"
            f"{hit.width}x{hit.height}_{hit.bits_per_pixel}bpp.tbkcdib"
        )
        if verbose:
            write_bytes(output_dir / "compressed_dib_payloads" / name, descriptor)
            files_written += 1
        compressed_dib_manifest.append(
            {
                "name": name,
                "offset": hit.offset,
                "end": payload_end,
                "size": len(descriptor),
                "dib_info_size": hit.pixel_offset - hit.offset,
                "payload_offset": hit.pixel_offset + 4,
                "payload_size": len(compressed_payload),
                "first_substream_size": first_substream_size,
                "first_substream_offset": first_substream_offset,
                "first_substream_end": first_substream_end,
                "second_substream_offset": second_substream_offset,
                "second_substream_size": max(0, payload_end - second_substream_offset),
                "end_pointer_offset": hit.pixel_offset,
                "end_pointer_value": end_pointer_value,
                "record_number": record_number,
                "record_offset": entry.absolute_offset,
                "local_end_pointer_target": entry.absolute_offset + end_pointer_value,
                "width": hit.width,
                "height": hit.height,
                "bits_per_pixel": hit.bits_per_pixel,
                "compression": hit.compression,
                "sha256": sha256_bytes(descriptor),
            }
        )
    if verbose and compressed_dib_manifest:
        compressed_dir = output_dir / "compressed_dib_payloads"
        with (compressed_dir / "index.tsv").open("w", newline="", encoding="utf-8") as fp:
            fieldnames = [
                "name",
                "offset",
                "end",
                "size",
                "dib_info_size",
                "payload_offset",
                "payload_size",
                "first_substream_size",
                "first_substream_offset",
                "first_substream_end",
                "second_substream_offset",
                "second_substream_size",
                "end_pointer_offset",
                "end_pointer_value",
                "record_number",
                "record_offset",
                "local_end_pointer_target",
                "width",
                "height",
                "bits_per_pixel",
                "compression",
                "sha256",
            ]
            writer = csv.DictWriter(fp, fieldnames=fieldnames, delimiter="\t")
            writer.writeheader()
            for row in compressed_dib_manifest:
                writer.writerow(row)
        chmod_group_readable(compressed_dir / "index.tsv")
        chmod_group_readable(compressed_dir)
        files_written += 1

    if verbose:
        strings_text = extract_strings(data)
        write_text(output_dir / "strings.txt", strings_text)
        files_written += 1

    byte_map = make_byte_map(len(data), tbk_offset, media_hits)
    if verbose:
        write_json(output_dir / "byte_map.json", byte_map)
        files_written += 1

        with (output_dir / "byte_map.csv").open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=["offset", "size", "end", "role", "description"])
            writer.writeheader()
            for row in byte_map:
                writer.writerow(row)
        chmod_group_readable(output_dir / "byte_map.csv")
        files_written += 1

    native_analysis = analyze_native_structure(data, tbk_offset, payload, media_hits, native_index)
    if verbose:
        write_json(output_dir / "native_map.json", native_analysis)
        files_written += 1
        write_json(output_dir / "native_index.json", native_index_to_json(native_index))
        files_written += 1
        write_json(output_dir / "native_records.json", native_analysis["native_records"])
        files_written += 1

    object_model = native_analysis["object_model"]
    clean_external_refs = external_reference_rows(object_model)
    if verbose:
        write_json(output_dir / "object_model.json", object_model)
        files_written += 1

    if verbose:
        handler_dir = output_dir / "handlers"
        for handler in object_model["handlers"]:
            name = f"{handler['index']:04d}_off_{handler['offset']:08x}_{handler['name']}.txt"
            lines = [
                f"Handler: {handler['name']}",
                f"Offset: 0x{handler['offset']:08x}",
                "Readable fragments from tokenized OpenScript context:",
                "",
            ]
            for fragment in handler["readable_fragments"]:
                lines.append(f"+0x{fragment['relative_offset']:04x}\t{fragment['text']}")
            lines.append("")
            lines.append("Hex context:")
            ctx = data[handler["context_start"] : handler["context_end"]]
            for pos in range(0, len(ctx), 16):
                chunk = ctx[pos : pos + 16]
                asc = "".join(chr(c) if 32 <= c < 127 else "." for c in chunk)
                lines.append(f"{handler['context_start'] + pos:08x}: {chunk.hex(' '):47}  {asc}")
            write_text(handler_dir / name, "\n".join(lines) + "\n")
            files_written += 1
        if handler_dir.exists():
            chmod_group_readable(handler_dir)

    native_segments = native_record_segments(native_index)
    typed_text_values = native_typed_text_values(native_analysis)
    typed_text_ranges = [
        (int(value["text_offset"]), int(value["text_offset"]) + int(value["text_length"]))
        for value in typed_text_values
    ]
    typed_text_tail_ranges = [
        (int(tail["tail_offset"]), int(tail["tail_end_offset"]))
        for value in typed_text_values
        if isinstance((tail := value.get("capacity_tail")), dict)
    ]
    property_dib_ranges = [(hit.offset, hit.end) for hit in native_property_dib_hits]
    nested_dib_ranges = [(hit.dib.offset, hit.dib.end) for hit in native_nested_dib_hits]
    content_excluded_ranges = (
        media_ranges
        + [(hit.offset, hit.end) for hit in dib_hits]
        + property_dib_ranges
        + nested_dib_ranges
        + typed_text_ranges
        + typed_text_tail_ranges
    )
    content_blocks = extract_content_text(data, native_segments, content_excluded_ranges)
    content_dir = output_dir / "content" if verbose else output_dir
    if verbose:
        write_json(content_dir / "text_blocks.json", {"blocks": content_blocks})
        files_written += 1
    text_lines = []
    for value in typed_text_values:
        owner = str(value.get("record_name") or value.get("record_object_id") or "")
        capacity_word = int(value.get("capacity_word", 0))
        object_owner = value.get("object_owner")
        object_label = ""
        if isinstance(object_owner, dict):
            object_label = (
                f" {object_owner.get('object_class_name')}#{object_owner.get('object_id')}"
                f"@0x{int(object_owner.get('object_header_offset', 0)):08x}"
            )
        storage_prefix = value.get("storage_prefix")
        storage_label = ""
        if isinstance(storage_prefix, dict):
            storage_label = f" {storage_prefix.get('kind')}@0x{int(storage_prefix.get('prefix_offset', 0)):08x}"
        if value.get("kind") == "large_field_text_value":
            text_label = f"large_field_text_length_0x{int(value.get('text_length', 0)):04x}"
        else:
            text_label = f"stored_text_value_capacity_0x{capacity_word:04x}"
        text_lines.append(
            f"[0x{int(value['text_offset']):08x}] "
            f"{value.get('record_class_name')} {owner}{object_label}{storage_label} "
            f"{text_label}"
        )
        text_lines.append(str(value["text"]).replace("\r\n", "\n").replace("\r", "\n"))
        tail = value.get("capacity_tail")
        if isinstance(tail, dict) and tail.get("tail_text"):
            text_lines.append(
                f"[0x{int(tail['tail_offset']):08x}] stored_text_capacity_tail "
                f"{tail['tail_nonzero_bytes']}/{tail['tail_size']} nonzero bytes"
            )
            text_lines.append(str(tail["tail_text"]).replace("\r\n", "\n").replace("\r", "\n"))
        text_lines.append("")
    for block in content_blocks:
        text = str(block["text"]).replace("\r\n", "\n").replace("\r", "\n")
        text_lines.append(f"[0x{int(block['offset']):08x}] {block['kind']}")
        text_lines.append(text)
        text_lines.append("")
    write_text(content_dir / "text.txt", "\n".join(text_lines))
    files_written += 1
    reference_lines = []
    for ref in clean_external_refs:
        reference_lines.append(f"0x{int(ref['offset']):08x}\t{ref['target_type']}\t{ref['target']}")
    write_text(content_dir / "references.txt", "\n".join(reference_lines) + "\n")
    files_written += 1
    if verbose:
        write_content_index(
            content_dir / "content_index.tsv",
            data,
            media_manifest,
            dib_manifest,
            property_dib_manifest,
            nested_dib_manifest,
            icon_manifest,
            object_model,
            rejected_dibs,
            content_blocks,
            native_index,
        )
        files_written += 1
        write_json(
            content_dir / "references.json",
            {"references": object_model["references"]},
        )
        files_written += 1
    if content_dir.exists():
        chmod_group_readable(content_dir)

    if verbose:
        native_dir = output_dir / "native_segments"
        for seg in native_segments:
            safe_name = f"{seg.name}_off_{seg.offset:08x}.bin"
            write_bytes(native_dir / safe_name, data[seg.offset : seg.end])
            files_written += 1
        if native_dir.exists():
            chmod_group_readable(native_dir)

    manifest = {
        "input_path": str(input_path),
        "input_size": len(data),
        "input_sha256": sha256_bytes(data),
        "wrapper_kind": wrapper_kind,
        "toolbook_offset": tbk_offset,
        "toolbook_size": len(payload),
        "toolbook_version_hex": payload[4:8].hex(),
        "toolbook_header": {
            "signature_hex": header.signature_hex,
            "format_id_hex": header.format_id_hex,
            "format_word0_hex": header.format_word0_hex,
            "format_word1_hex": header.format_word1_hex,
            "family": header.family,
            "fixed_header_size": header.fixed_header_size,
            "runtime_probe_size": header.runtime_probe_size,
            "first_native_offset": header.first_native_offset,
        },
        "toolbook_header_hex": payload[:0x100].hex(),
        "toolbook_open_probe_hex": payload[:0x116].hex(),
        "files_written": files_written + 1,
        "media_counts": media_counts,
        "media": media_manifest,
        "reconstructed_dib_images": dib_manifest,
        "native_property_stream_dib_images": property_dib_manifest,
        "native_nested_dib_images": nested_dib_manifest,
        "native_class41_icons": icon_manifest,
        "compressed_dib_payloads": compressed_dib_manifest,
        "image_like_records_not_extracted": [
            {
                "source_kind": rejected_dib_source_kind(data, hit, native_index),
                "offset": hit.offset,
                "width": hit.width,
                "height": hit.height,
                "bits_per_pixel": hit.bits_per_pixel,
                "pixel_offset": hit.pixel_offset,
                "expected_end": hit.expected_end,
                "reason": hit.reject_reason,
            }
            for hit in rejected_dibs
        ],
        "typed_text_values": len(typed_text_values),
        "typed_text_values_with_native_object_owner": sum(1 for value in typed_text_values if "object_owner" in value),
        "typed_text_values_with_native_storage_prefix": sum(1 for value in typed_text_values if "storage_prefix" in value),
        "typed_text_capacity_tail_values": native_analysis["native_records"]["counts"].get(
            "typed_text_capacity_tail_values", 0
        ),
        "typed_text_capacity_tail_bytes": native_analysis["native_records"]["counts"].get(
            "typed_text_capacity_tail_bytes", 0
        ),
        "typed_text_capacity_tail_nonzero_bytes": native_analysis["native_records"]["counts"].get(
            "typed_text_capacity_tail_nonzero_bytes", 0
        ),
        "typed_text_capacity_tail_text_values": native_analysis["native_records"]["counts"].get(
            "typed_text_capacity_tail_text_values", 0
        ),
        "large_text_values": native_analysis["native_records"]["counts"].get("large_text_values", 0),
        "field_hotword_run_tables": native_analysis["native_records"]["counts"].get("field_hotword_run_tables", 0),
        "field_hotword_run_table_rows": native_analysis["native_records"]["counts"].get(
            "field_hotword_run_table_rows", 0
        ),
        "field_hotword_run_table_active_rows": native_analysis["native_records"]["counts"].get(
            "field_hotword_run_table_active_rows", 0
        ),
        "field_hotword_run_table_linked_rows": native_analysis["native_records"]["counts"].get(
            "field_hotword_run_table_linked_rows", 0
        ),
        "field_hotword_run_table_bytes": native_analysis["native_records"]["counts"].get(
            "field_hotword_run_table_bytes", 0
        ),
        "page_background_offset_vectors": native_analysis["native_records"]["counts"].get(
            "page_background_offset_vectors", 0
        ),
        "page_background_offset_vector_bytes": native_analysis["native_records"]["counts"].get(
            "page_background_offset_vector_bytes", 0
        ),
        "page_background_offset_vector_offsets": native_analysis["native_records"]["counts"].get(
            "page_background_offset_vector_offsets", 0
        ),
        "page_background_offset_vector_nonzero_offsets": native_analysis["native_records"]["counts"].get(
            "page_background_offset_vector_nonzero_offsets", 0
        ),
        "page_background_payloads": native_analysis["native_records"]["counts"].get(
            "page_background_payloads", 0
        ),
        "page_background_payload_segments": native_analysis["native_records"]["counts"].get(
            "page_background_payload_segments", 0
        ),
        "page_background_payload_segment_bytes": native_analysis["native_records"]["counts"].get(
            "page_background_payload_segment_bytes", 0
        ),
        "page_background_bounded_payload_fragments": native_analysis["native_records"]["counts"].get(
            "page_background_bounded_payload_fragments", 0
        ),
        "page_background_bounded_payload_fragment_bytes": native_analysis["native_records"]["counts"].get(
            "page_background_bounded_payload_fragment_bytes", 0
        ),
        "book_payload_segments": native_analysis["native_records"]["counts"].get("book_payload_segments", 0),
        "book_payload_segment_bytes": native_analysis["native_records"]["counts"].get(
            "book_payload_segment_bytes", 0
        ),
        "book_common_native_headers": native_analysis["native_records"]["counts"].get(
            "book_common_native_headers", 0
        ),
        "book_common_native_header_bytes": native_analysis["native_records"]["counts"].get(
            "book_common_native_header_bytes", 0
        ),
        "book_reference_blocks": native_analysis["native_records"]["counts"].get("book_reference_blocks", 0),
        "book_control_descriptors": native_analysis["native_records"]["counts"].get(
            "book_control_descriptors", 0
        ),
        "book_control_descriptor_bytes": native_analysis["native_records"]["counts"].get(
            "book_control_descriptor_bytes", 0
        ),
        "book_pointer_target_name_prefixes": native_analysis["native_records"]["counts"].get(
            "book_pointer_target_name_prefixes", 0
        ),
        "book_pointer_target_name_prefix_bytes": native_analysis["native_records"]["counts"].get(
            "book_pointer_target_name_prefix_bytes", 0
        ),
        "book_pointer_target_leading_descriptors": native_analysis["native_records"]["counts"].get(
            "book_pointer_target_leading_descriptors", 0
        ),
        "book_pointer_target_leading_descriptor_bytes": native_analysis["native_records"]["counts"].get(
            "book_pointer_target_leading_descriptor_bytes", 0
        ),
        "book_named_payload_reference_inline_prefixes": native_analysis["native_records"]["counts"].get(
            "book_named_payload_reference_inline_prefixes", 0
        ),
        "book_named_payload_reference_inline_prefix_bytes": native_analysis["native_records"]["counts"].get(
            "book_named_payload_reference_inline_prefix_bytes", 0
        ),
        "book_palette_entries": native_analysis["native_records"]["counts"].get("book_palette_entries", 0),
        "book_pointer_tables": native_analysis["native_records"]["counts"].get("book_pointer_tables", 0),
        "book_pointer_table_entries": native_analysis["native_records"]["counts"].get(
            "book_pointer_table_entries", 0
        ),
        "book_pointer_table_bytes": native_analysis["native_records"]["counts"].get("book_pointer_table_bytes", 0),
        "book_pointer_table_reference_words": native_analysis["native_records"]["counts"].get(
            "book_pointer_table_reference_words", 0
        ),
        "book_pointer_table_reference_bytes": native_analysis["native_records"]["counts"].get(
            "book_pointer_table_reference_bytes", 0
        ),
        "book_pre_pointer_descriptor_blocks": native_analysis["native_records"]["counts"].get(
            "book_pre_pointer_descriptor_blocks", 0
        ),
        "book_pre_pointer_descriptor_bytes": native_analysis["native_records"]["counts"].get(
            "book_pre_pointer_descriptor_bytes", 0
        ),
        "book_compact_named_descriptors": native_analysis["native_records"]["counts"].get(
            "book_compact_named_descriptors", 0
        ),
        "book_compact_named_descriptor_bytes": native_analysis["native_records"]["counts"].get(
            "book_compact_named_descriptor_bytes", 0
        ),
        "book_pre_pointer_count_descriptors": native_analysis["native_records"]["counts"].get(
            "book_pre_pointer_count_descriptors", 0
        ),
        "book_pre_pointer_count_descriptor_bytes": native_analysis["native_records"]["counts"].get(
            "book_pre_pointer_count_descriptor_bytes", 0
        ),
        "book_compact_descriptor_payload_fragments": native_analysis["native_records"]["counts"].get(
            "book_compact_descriptor_payload_fragments", 0
        ),
        "book_compact_descriptor_payload_fragment_bytes": native_analysis["native_records"]["counts"].get(
            "book_compact_descriptor_payload_fragment_bytes", 0
        ),
        "book_named_payload_reference_descriptors": native_analysis["native_records"]["counts"].get(
            "book_named_payload_reference_descriptors", 0
        ),
        "book_named_payload_reference_descriptor_bytes": native_analysis["native_records"]["counts"].get(
            "book_named_payload_reference_descriptor_bytes", 0
        ),
        "book_openscript_objects": native_analysis["native_records"]["counts"].get("book_openscript_objects", 0),
        "book_openscript_object_bytes": native_analysis["native_records"]["counts"].get(
            "book_openscript_object_bytes", 0
        ),
        "book_openscript_code_bytes": native_analysis["native_records"]["counts"].get(
            "book_openscript_code_bytes", 0
        ),
        "book_openscript_auxiliary_prefixes": native_analysis["native_records"]["counts"].get(
            "book_openscript_auxiliary_prefixes", 0
        ),
        "book_openscript_auxiliary_prefix_bytes": native_analysis["native_records"]["counts"].get(
            "book_openscript_auxiliary_prefix_bytes", 0
        ),
        "book_openscript_duplicate_tails": native_analysis["native_records"]["counts"].get(
            "book_openscript_duplicate_tails", 0
        ),
        "book_openscript_duplicate_tail_bytes": native_analysis["native_records"]["counts"].get(
            "book_openscript_duplicate_tail_bytes", 0
        ),
        "book_openscript_record_links": native_analysis["native_records"]["counts"].get(
            "book_openscript_record_links", 0
        ),
        "book_openscript_record_link_bytes": native_analysis["native_records"]["counts"].get(
            "book_openscript_record_link_bytes", 0
        ),
        "book_pointer_target_payload_fragments": native_analysis["native_records"]["counts"].get(
            "book_pointer_target_payload_fragments", 0
        ),
        "book_pointer_target_payload_fragment_bytes": native_analysis["native_records"]["counts"].get(
            "book_pointer_target_payload_fragment_bytes", 0
        ),
        "book_named_payload_reference_payload_fragments": native_analysis["native_records"]["counts"].get(
            "book_named_payload_reference_payload_fragments", 0
        ),
        "book_named_payload_reference_payload_fragment_bytes": native_analysis["native_records"]["counts"].get(
            "book_named_payload_reference_payload_fragment_bytes", 0
        ),
        "book_zero_reserved_gaps": native_analysis["native_records"]["counts"].get("book_zero_reserved_gaps", 0),
        "book_zero_reserved_gap_bytes": native_analysis["native_records"]["counts"].get(
            "book_zero_reserved_gap_bytes", 0
        ),
        "embedded_native_text_objects": native_analysis["native_records"]["counts"].get("embedded_native_text_objects", 0),
        "self_reference_offset_tables": native_analysis["native_records"]["counts"].get("self_reference_offset_tables", 0),
        "self_reference_offset_table_entries": native_analysis["native_records"]["counts"].get(
            "self_reference_offset_table_entries", 0
        ),
        "self_reference_offset_table_nonzero_entries": native_analysis["native_records"]["counts"].get(
            "self_reference_offset_table_nonzero_entries", 0
        ),
        "self_reference_offset_table_linked_text_objects": native_analysis["native_records"]["counts"].get(
            "self_reference_offset_table_linked_text_objects", 0
        ),
        "self_reference_child_object_headers": native_analysis["native_records"]["counts"].get(
            "self_reference_child_object_headers", 0
        ),
        "self_reference_child_object_header_bytes": native_analysis["native_records"]["counts"].get(
            "self_reference_child_object_header_bytes", 0
        ),
        "self_reference_child_object_spans": native_analysis["native_records"]["counts"].get(
            "self_reference_child_object_spans", 0
        ),
        "self_reference_child_object_span_bytes": native_analysis["native_records"]["counts"].get(
            "self_reference_child_object_span_bytes", 0
        ),
        "self_reference_final_child_object_spans": native_analysis["native_records"]["counts"].get(
            "self_reference_final_child_object_spans", 0
        ),
        "self_reference_final_child_object_span_bytes": native_analysis["native_records"]["counts"].get(
            "self_reference_final_child_object_span_bytes", 0
        ),
        "self_reference_offset_table_bytes": native_analysis["native_records"]["counts"].get(
            "self_reference_offset_table_bytes", 0
        ),
        "content_text_blocks": len(content_blocks),
        "native_index": native_index_to_json(native_index),
        "completion_note": (
            "Content extraction is limited to active native records reached through the ToolBook index. "
            "Native object semantics are not fully decoded; see asymetrixToolbook.txt."
        ),
    }
    if verbose:
        write_json(output_dir / "manifest.json", manifest)
        files_written += 1

    return ExtractionResult(
        input_path=str(input_path),
        output_dir=str(output_dir),
        status="ok",
        reason="",
        input_size=len(data),
        wrapper_kind=wrapper_kind,
        tbk_offset=tbk_offset,
        tbk_size=len(payload),
        version_hex=payload[4:8].hex(),
        sha256=sha256_bytes(data),
        files_written=files_written,
        media_counts=media_counts,
        probable_objects=object_model["counts"]["probable_objects"],
        handlers=object_model["counts"]["handlers"],
        references=object_model["counts"]["references"],
        text_blocks=len(content_blocks),
        typed_text_values=len(typed_text_values),
        typed_text_values_with_native_object_owner=sum(1 for value in typed_text_values if "object_owner" in value),
        typed_text_values_with_native_storage_prefix=sum(1 for value in typed_text_values if "storage_prefix" in value),
        typed_text_capacity_tail_values=int(
            native_analysis["native_records"]["counts"].get("typed_text_capacity_tail_values", 0)
        ),
        typed_text_capacity_tail_bytes=int(
            native_analysis["native_records"]["counts"].get("typed_text_capacity_tail_bytes", 0)
        ),
        typed_text_capacity_tail_nonzero_bytes=int(
            native_analysis["native_records"]["counts"].get("typed_text_capacity_tail_nonzero_bytes", 0)
        ),
        typed_text_capacity_tail_text_values=int(
            native_analysis["native_records"]["counts"].get("typed_text_capacity_tail_text_values", 0)
        ),
        large_text_values=int(native_analysis["native_records"]["counts"].get("large_text_values", 0)),
        field_hotword_run_tables=int(
            native_analysis["native_records"]["counts"].get("field_hotword_run_tables", 0)
        ),
        field_hotword_run_table_rows=int(
            native_analysis["native_records"]["counts"].get("field_hotword_run_table_rows", 0)
        ),
        field_hotword_run_table_active_rows=int(
            native_analysis["native_records"]["counts"].get("field_hotword_run_table_active_rows", 0)
        ),
        field_hotword_run_table_linked_rows=int(
            native_analysis["native_records"]["counts"].get("field_hotword_run_table_linked_rows", 0)
        ),
        field_hotword_run_table_bytes=int(
            native_analysis["native_records"]["counts"].get("field_hotword_run_table_bytes", 0)
        ),
        page_background_offset_vectors=int(
            native_analysis["native_records"]["counts"].get("page_background_offset_vectors", 0)
        ),
        page_background_offset_vector_bytes=int(
            native_analysis["native_records"]["counts"].get("page_background_offset_vector_bytes", 0)
        ),
        page_background_offset_vector_offsets=int(
            native_analysis["native_records"]["counts"].get("page_background_offset_vector_offsets", 0)
        ),
        page_background_offset_vector_nonzero_offsets=int(
            native_analysis["native_records"]["counts"].get("page_background_offset_vector_nonzero_offsets", 0)
        ),
        page_background_payloads=int(
            native_analysis["native_records"]["counts"].get("page_background_payloads", 0)
        ),
        page_background_payload_segments=int(
            native_analysis["native_records"]["counts"].get("page_background_payload_segments", 0)
        ),
        page_background_payload_segment_bytes=int(
            native_analysis["native_records"]["counts"].get("page_background_payload_segment_bytes", 0)
        ),
        page_background_bounded_payload_fragments=int(
            native_analysis["native_records"]["counts"].get("page_background_bounded_payload_fragments", 0)
        ),
        page_background_bounded_payload_fragment_bytes=int(
            native_analysis["native_records"]["counts"].get("page_background_bounded_payload_fragment_bytes", 0)
        ),
        book_payload_segments=int(native_analysis["native_records"]["counts"].get("book_payload_segments", 0)),
        book_payload_segment_bytes=int(
            native_analysis["native_records"]["counts"].get("book_payload_segment_bytes", 0)
        ),
        book_common_native_headers=int(
            native_analysis["native_records"]["counts"].get("book_common_native_headers", 0)
        ),
        book_common_native_header_bytes=int(
            native_analysis["native_records"]["counts"].get("book_common_native_header_bytes", 0)
        ),
        book_reference_blocks=int(native_analysis["native_records"]["counts"].get("book_reference_blocks", 0)),
        book_control_descriptors=int(
            native_analysis["native_records"]["counts"].get("book_control_descriptors", 0)
        ),
        book_control_descriptor_bytes=int(
            native_analysis["native_records"]["counts"].get("book_control_descriptor_bytes", 0)
        ),
        book_pointer_target_name_prefixes=int(
            native_analysis["native_records"]["counts"].get("book_pointer_target_name_prefixes", 0)
        ),
        book_pointer_target_name_prefix_bytes=int(
            native_analysis["native_records"]["counts"].get("book_pointer_target_name_prefix_bytes", 0)
        ),
        book_pointer_target_leading_descriptors=int(
            native_analysis["native_records"]["counts"].get("book_pointer_target_leading_descriptors", 0)
        ),
        book_pointer_target_leading_descriptor_bytes=int(
            native_analysis["native_records"]["counts"].get("book_pointer_target_leading_descriptor_bytes", 0)
        ),
        book_named_payload_reference_inline_prefixes=int(
            native_analysis["native_records"]["counts"].get("book_named_payload_reference_inline_prefixes", 0)
        ),
        book_named_payload_reference_inline_prefix_bytes=int(
            native_analysis["native_records"]["counts"].get("book_named_payload_reference_inline_prefix_bytes", 0)
        ),
        book_palette_entries=int(native_analysis["native_records"]["counts"].get("book_palette_entries", 0)),
        book_pointer_tables=int(native_analysis["native_records"]["counts"].get("book_pointer_tables", 0)),
        book_pointer_table_entries=int(
            native_analysis["native_records"]["counts"].get("book_pointer_table_entries", 0)
        ),
        book_pointer_table_bytes=int(
            native_analysis["native_records"]["counts"].get("book_pointer_table_bytes", 0)
        ),
        book_pointer_table_reference_words=int(
            native_analysis["native_records"]["counts"].get("book_pointer_table_reference_words", 0)
        ),
        book_pointer_table_reference_bytes=int(
            native_analysis["native_records"]["counts"].get("book_pointer_table_reference_bytes", 0)
        ),
        book_pre_pointer_descriptor_blocks=int(
            native_analysis["native_records"]["counts"].get("book_pre_pointer_descriptor_blocks", 0)
        ),
        book_pre_pointer_descriptor_bytes=int(
            native_analysis["native_records"]["counts"].get("book_pre_pointer_descriptor_bytes", 0)
        ),
        book_compact_named_descriptors=int(
            native_analysis["native_records"]["counts"].get("book_compact_named_descriptors", 0)
        ),
        book_compact_named_descriptor_bytes=int(
            native_analysis["native_records"]["counts"].get("book_compact_named_descriptor_bytes", 0)
        ),
        book_pre_pointer_count_descriptors=int(
            native_analysis["native_records"]["counts"].get("book_pre_pointer_count_descriptors", 0)
        ),
        book_pre_pointer_count_descriptor_bytes=int(
            native_analysis["native_records"]["counts"].get("book_pre_pointer_count_descriptor_bytes", 0)
        ),
        book_compact_descriptor_payload_fragments=int(
            native_analysis["native_records"]["counts"].get("book_compact_descriptor_payload_fragments", 0)
        ),
        book_compact_descriptor_payload_fragment_bytes=int(
            native_analysis["native_records"]["counts"].get("book_compact_descriptor_payload_fragment_bytes", 0)
        ),
        book_named_payload_reference_descriptors=int(
            native_analysis["native_records"]["counts"].get("book_named_payload_reference_descriptors", 0)
        ),
        book_named_payload_reference_descriptor_bytes=int(
            native_analysis["native_records"]["counts"].get("book_named_payload_reference_descriptor_bytes", 0)
        ),
        book_openscript_objects=int(native_analysis["native_records"]["counts"].get("book_openscript_objects", 0)),
        book_openscript_object_bytes=int(
            native_analysis["native_records"]["counts"].get("book_openscript_object_bytes", 0)
        ),
        book_openscript_code_bytes=int(
            native_analysis["native_records"]["counts"].get("book_openscript_code_bytes", 0)
        ),
        book_openscript_auxiliary_prefixes=int(
            native_analysis["native_records"]["counts"].get("book_openscript_auxiliary_prefixes", 0)
        ),
        book_openscript_auxiliary_prefix_bytes=int(
            native_analysis["native_records"]["counts"].get("book_openscript_auxiliary_prefix_bytes", 0)
        ),
        book_openscript_duplicate_tails=int(
            native_analysis["native_records"]["counts"].get("book_openscript_duplicate_tails", 0)
        ),
        book_openscript_duplicate_tail_bytes=int(
            native_analysis["native_records"]["counts"].get("book_openscript_duplicate_tail_bytes", 0)
        ),
        book_openscript_record_links=int(
            native_analysis["native_records"]["counts"].get("book_openscript_record_links", 0)
        ),
        book_openscript_record_link_bytes=int(
            native_analysis["native_records"]["counts"].get("book_openscript_record_link_bytes", 0)
        ),
        book_pointer_target_payload_fragments=int(
            native_analysis["native_records"]["counts"].get("book_pointer_target_payload_fragments", 0)
        ),
        book_pointer_target_payload_fragment_bytes=int(
            native_analysis["native_records"]["counts"].get("book_pointer_target_payload_fragment_bytes", 0)
        ),
        book_named_payload_reference_payload_fragments=int(
            native_analysis["native_records"]["counts"].get("book_named_payload_reference_payload_fragments", 0)
        ),
        book_named_payload_reference_payload_fragment_bytes=int(
            native_analysis["native_records"]["counts"].get("book_named_payload_reference_payload_fragment_bytes", 0)
        ),
        book_zero_reserved_gaps=int(native_analysis["native_records"]["counts"].get("book_zero_reserved_gaps", 0)),
        book_zero_reserved_gap_bytes=int(
            native_analysis["native_records"]["counts"].get("book_zero_reserved_gap_bytes", 0)
        ),
        embedded_native_text_objects=int(native_analysis["native_records"]["counts"].get("embedded_native_text_objects", 0)),
        self_reference_offset_tables=int(native_analysis["native_records"]["counts"].get("self_reference_offset_tables", 0)),
        self_reference_offset_table_entries=int(
            native_analysis["native_records"]["counts"].get("self_reference_offset_table_entries", 0)
        ),
        self_reference_offset_table_nonzero_entries=int(
            native_analysis["native_records"]["counts"].get("self_reference_offset_table_nonzero_entries", 0)
        ),
        self_reference_offset_table_linked_text_objects=int(
            native_analysis["native_records"]["counts"].get("self_reference_offset_table_linked_text_objects", 0)
        ),
        self_reference_child_object_headers=int(
            native_analysis["native_records"]["counts"].get("self_reference_child_object_headers", 0)
        ),
        self_reference_child_object_header_bytes=int(
            native_analysis["native_records"]["counts"].get("self_reference_child_object_header_bytes", 0)
        ),
        self_reference_child_object_spans=int(
            native_analysis["native_records"]["counts"].get("self_reference_child_object_spans", 0)
        ),
        self_reference_child_object_span_bytes=int(
            native_analysis["native_records"]["counts"].get("self_reference_child_object_span_bytes", 0)
        ),
        self_reference_final_child_object_spans=int(
            native_analysis["native_records"]["counts"].get("self_reference_final_child_object_spans", 0)
        ),
        self_reference_final_child_object_span_bytes=int(
            native_analysis["native_records"]["counts"].get("self_reference_final_child_object_span_bytes", 0)
        ),
        self_reference_offset_table_bytes=int(
            native_analysis["native_records"]["counts"].get("self_reference_offset_table_bytes", 0)
        ),
        reconstructed_images=len(dib_hits),
        native_property_stream_images=len(native_property_dib_hits),
        native_nested_dib_images=len(native_nested_dib_hits),
        native_class41_icons=len(native_icon_hits),
        native_class41_icon_descriptors_unhandled=len(native_icon_rejects),
        embedded_media=len(media_hits),
        unhandled_bitmap_descriptors=len(rejected_dibs),
        toolbook_backed_bitmap_descriptors=sum(
            1
            for hit in rejected_dibs
            if toolbook_bitmap_record_type(data, hit.offset) is not None
            and hit.reject_reason != "native_record_at_pixel_start"
        ),
        toolbook_bitmap_info_descriptors=sum(
            1
            for hit in rejected_dibs
            if rejected_dib_source_kind(data, hit, native_index)
            == "toolbook_bitmap_info_descriptor_without_contiguous_pixels"
        ),
        toolbook_bitmap_info_container_descriptors=sum(
            1
            for hit in rejected_dibs
            if rejected_dib_source_kind(data, hit, native_index)
            == "toolbook_bitmap_info_container_with_nested_dib_descriptor"
        ),
        toolbook_bitmap_info_native_payload_descriptors=sum(
            1
            for hit in rejected_dibs
            if rejected_dib_source_kind(data, hit, native_index)
            == "toolbook_bitmap_info_descriptor_with_native_payload"
        ),
        native_record_nested_dib_container_descriptors=sum(
            1
            for hit in rejected_dibs
            if rejected_dib_source_kind(data, hit, native_index)
            == "toolbook_native_record_container_with_nested_dib_descriptor"
        ),
        native_record_native_payload_descriptors=sum(
            1
            for hit in rejected_dibs
            if rejected_dib_source_kind(data, hit, native_index) == "toolbook_dib_info_with_native_payload"
        ),
        nested_dib_container_extracted_descriptors=sum(
            1
            for hit in rejected_dibs
            if rejected_dib_source_kind(data, hit, native_index)
            == "toolbook_nested_dib_container_with_extracted_dib"
        ),
        nested_dib_chain_crosses_metadata_descriptors=sum(
            1
            for hit in rejected_dibs
            if rejected_dib_source_kind(data, hit, native_index)
            == "toolbook_nested_dib_chain_crosses_native_metadata"
        ),
        nested_dib_chain_spans_records_descriptors=sum(
            1
            for hit in rejected_dibs
            if rejected_dib_source_kind(data, hit, native_index)
            == "toolbook_nested_dib_chain_spans_native_records"
        ),
        nested_dib_chain_property_metadata_descriptors=sum(
            1
            for hit in rejected_dibs
            if rejected_dib_source_kind(data, hit, native_index)
            == "toolbook_nested_dib_chain_to_property_stream_metadata"
        ),
        nested_dib_chain_property_nested_descriptors=sum(
            1
            for hit in rejected_dibs
            if rejected_dib_source_kind(data, hit, native_index)
            == "toolbook_nested_dib_chain_to_property_stream_with_nested_dib_descriptor"
        ),
        nested_dib_chain_property_unmatched_descriptors=sum(
            1
            for hit in rejected_dibs
            if rejected_dib_source_kind(data, hit, native_index)
            in {
                "toolbook_nested_dib_chain_to_unmatched_physsize_property_stream",
                "toolbook_nested_dib_chain_to_property_stream",
            }
        ),
        nested_dib_chain_invalid_descriptors=sum(
            1
            for hit in rejected_dibs
            if rejected_dib_source_kind(data, hit, native_index)
            in {
                "toolbook_nested_dib_chain_to_invalid_metadata",
                "toolbook_nested_dib_chain_to_native_record_payload",
            }
        ),
        toolbook_property_stream_dib_descriptors=sum(
            1
            for hit in rejected_dibs
            if rejected_dib_source_kind(data, hit, native_index) == "toolbook_dib_info_with_property_stream"
        ),
        toolbook_property_stream_metadata_descriptors=sum(
            1
            for hit in rejected_dibs
            if rejected_dib_source_kind(data, hit, native_index) == "toolbook_property_stream_descriptor_metadata"
        ),
        toolbook_property_stream_nested_descriptors=sum(
            1
            for hit in rejected_dibs
            if rejected_dib_source_kind(data, hit, native_index)
            == "toolbook_property_stream_with_nested_dib_descriptor"
        ),
        toolbook_property_stream_container_nested_descriptors=sum(
            1
            for hit in rejected_dibs
            if rejected_dib_source_kind(data, hit, native_index)
            == "toolbook_property_stream_container_with_nested_physsize_descriptor"
        ),
        toolbook_property_stream_unmatched_descriptors=sum(
            1
            for hit in rejected_dibs
            if rejected_dib_source_kind(data, hit, native_index) == "toolbook_property_stream_unmatched_physsize"
        ),
        toolbook_property_stream_unmatched_nested_descriptors=sum(
            1
            for hit in rejected_dibs
            if rejected_dib_source_kind(data, hit, native_index)
            == "toolbook_property_stream_unmatched_physsize_with_nested_dib"
        ),
        toolbook_compressed_dib_descriptors=sum(
            1
            for hit in rejected_dibs
            if rejected_dib_source_kind(data, hit, native_index) == "toolbook_compressed_dib_descriptor"
        ),
        unproven_dib_like_descriptors=sum(
            1 for hit in rejected_dibs if rejected_dib_source_kind(data, hit, native_index) == "dib_like_native_record"
        ),
        native_record_bitmap_descriptors=sum(
            1 for hit in rejected_dibs if hit.reject_reason == "native_record_at_pixel_start"
        ),
        nested_dib_bitmap_descriptors=sum(
            1 for hit in rejected_dibs if hit.reject_reason == "nested_dib_header_in_pixel_range"
        ),
        nested_native_header_bitmap_descriptors=sum(
            1 for hit in rejected_dibs if hit.reject_reason == "nested_native_descriptor_header"
        ),
        unsupported_bitmap_record_type_descriptors=sum(
            1 for hit in rejected_dibs if hit.reject_reason.startswith("unsupported_native_bitmap_record_type_")
        ),
        native_property_stream_bitmap_descriptors=sum(
            1 for hit in rejected_dibs if hit.reject_reason == "native_property_stream_at_pixel_start"
        ),
        missing_envelope_bitmap_descriptors=sum(
            1 for hit in rejected_dibs if hit.reject_reason == "missing_toolbook_bitmap_envelope"
        ),
        invalid_bitmap_descriptors=sum(
            1 for hit in rejected_dibs if hit.reject_reason == "pixel_range_outside_file"
        ),
        suppressed_bitmap_descriptors=sum(
            1 for hit in rejected_dibs if hit.reject_reason == "suppressed_1x1_candidate"
        ),
        external_refs=len(clean_external_refs),
        native_index_status=native_index.status,
        native_index_reason=native_index.reason,
        native_records=len(native_index.records),
        native_index_pages=len(native_index.pages),
        active_record_bytes=range_total(native_index.record_ranges),
        active_record_coverage_percent=range_total(native_index.active_ranges) / max(1, len(payload)) * 100.0,
        inactive_payload_bytes=max(0, len(payload) - range_total(native_index.active_ranges)),
    )


def safe_output_for_sample(extract_root: Path, sample_root: Path, sample: Path) -> Path:
    rel = sample.relative_to(sample_root)
    return extract_root / rel.parent / sample.name


def run_report(sample_root: Path, extract_root: Path, report_path: Path, verbose: bool = False) -> None:
    if extract_root.exists():
        shutil.rmtree(extract_root)
    extract_root.mkdir(parents=True, exist_ok=True)
    chmod_group_readable(extract_root)

    rows: list[ExtractionResult] = []
    for sample in sorted(p for p in sample_root.glob("*/*") if p.is_file()):
        out_dir = safe_output_for_sample(extract_root, sample_root, sample)
        try:
            rows.append(extract_file(sample, out_dir, verbose=verbose))
        except Exception as exc:
            if out_dir.exists():
                shutil.rmtree(out_dir)
            rows.append(
                ExtractionResult(
                    input_path=str(sample),
                    output_dir=str(out_dir),
                    status="skipped",
                    reason=str(exc),
                    input_size=sample.stat().st_size,
                    wrapper_kind="",
                    tbk_offset=-1,
                    tbk_size=0,
                    version_hex="",
                    sha256=sha256_bytes(sample.read_bytes()),
                    files_written=0,
                    media_counts={kind: 0 for kind in SUPPORTED_MEDIA},
                    probable_objects=0,
                    handlers=0,
                    references=0,
                    text_blocks=0,
                    embedded_native_text_objects=0,
                    reconstructed_images=0,
                    native_property_stream_images=0,
                    native_nested_dib_images=0,
                    native_class41_icons=0,
                    native_class41_icon_descriptors_unhandled=0,
                    embedded_media=0,
                    unhandled_bitmap_descriptors=0,
                    toolbook_backed_bitmap_descriptors=0,
                    toolbook_bitmap_info_descriptors=0,
                    toolbook_bitmap_info_container_descriptors=0,
                    toolbook_bitmap_info_native_payload_descriptors=0,
                    native_record_nested_dib_container_descriptors=0,
                    native_record_native_payload_descriptors=0,
                    nested_dib_container_extracted_descriptors=0,
                    nested_dib_chain_crosses_metadata_descriptors=0,
                    nested_dib_chain_spans_records_descriptors=0,
                    nested_dib_chain_property_metadata_descriptors=0,
                    nested_dib_chain_property_nested_descriptors=0,
                    nested_dib_chain_property_unmatched_descriptors=0,
                    nested_dib_chain_invalid_descriptors=0,
                    toolbook_property_stream_dib_descriptors=0,
                    toolbook_property_stream_metadata_descriptors=0,
                    toolbook_property_stream_nested_descriptors=0,
                    toolbook_property_stream_container_nested_descriptors=0,
                    toolbook_property_stream_unmatched_descriptors=0,
                    toolbook_property_stream_unmatched_nested_descriptors=0,
                    toolbook_compressed_dib_descriptors=0,
                    unproven_dib_like_descriptors=0,
                    native_record_bitmap_descriptors=0,
                    nested_dib_bitmap_descriptors=0,
                    nested_native_header_bitmap_descriptors=0,
                    unsupported_bitmap_record_type_descriptors=0,
                    native_property_stream_bitmap_descriptors=0,
                    missing_envelope_bitmap_descriptors=0,
                    invalid_bitmap_descriptors=0,
                    suppressed_bitmap_descriptors=0,
                    external_refs=0,
                    native_index_status="unsupported",
                    native_index_reason=str(exc),
                    native_records=0,
                    native_index_pages=0,
                    active_record_bytes=0,
                    active_record_coverage_percent=0.0,
                    inactive_payload_bytes=0,
                )
            )

    grouped: dict[str, list[ExtractionResult]] = {}
    for row in rows:
        parent = str(Path(row.input_path).parent.relative_to(sample_root))
        grouped.setdefault(parent, []).append(row)

    total_ok = sum(1 for row in rows if row.status == "ok")
    total_files = sum(row.files_written for row in rows)
    total_media = {kind: sum(row.media_counts.get(kind, 0) for row in rows) for kind in SUPPORTED_MEDIA}
    total_embedded_media = sum(row.embedded_media for row in rows)
    total_reconstructed = sum(row.reconstructed_images for row in rows)
    total_native_property_stream_images = sum(row.native_property_stream_images for row in rows)
    total_native_nested_dib_images = sum(row.native_nested_dib_images for row in rows)
    total_native_class41_icons = sum(row.native_class41_icons for row in rows)
    total_native_class41_icon_descriptors_unhandled = sum(
        row.native_class41_icon_descriptors_unhandled for row in rows
    )
    total_extracted_image_media = (
        total_embedded_media
        + total_reconstructed
        + total_native_property_stream_images
        + total_native_nested_dib_images
        + total_native_class41_icons
    )
    total_unhandled_bitmaps = sum(row.unhandled_bitmap_descriptors for row in rows)
    total_toolbook_backed_bitmaps = sum(row.toolbook_backed_bitmap_descriptors for row in rows)
    total_toolbook_bitmap_info_descriptors = sum(row.toolbook_bitmap_info_descriptors for row in rows)
    total_toolbook_bitmap_info_container_descriptors = sum(
        row.toolbook_bitmap_info_container_descriptors for row in rows
    )
    total_toolbook_bitmap_info_native_payload_descriptors = sum(
        row.toolbook_bitmap_info_native_payload_descriptors for row in rows
    )
    total_native_record_nested_dib_container_descriptors = sum(
        row.native_record_nested_dib_container_descriptors for row in rows
    )
    total_native_record_native_payload_descriptors = sum(
        row.native_record_native_payload_descriptors for row in rows
    )
    total_nested_dib_container_extracted_descriptors = sum(
        row.nested_dib_container_extracted_descriptors for row in rows
    )
    total_nested_dib_chain_crosses_metadata_descriptors = sum(
        row.nested_dib_chain_crosses_metadata_descriptors for row in rows
    )
    total_nested_dib_chain_spans_records_descriptors = sum(
        row.nested_dib_chain_spans_records_descriptors for row in rows
    )
    total_nested_dib_chain_property_metadata_descriptors = sum(
        row.nested_dib_chain_property_metadata_descriptors for row in rows
    )
    total_nested_dib_chain_property_nested_descriptors = sum(
        row.nested_dib_chain_property_nested_descriptors for row in rows
    )
    total_nested_dib_chain_property_unmatched_descriptors = sum(
        row.nested_dib_chain_property_unmatched_descriptors for row in rows
    )
    total_nested_dib_chain_invalid_descriptors = sum(row.nested_dib_chain_invalid_descriptors for row in rows)
    total_toolbook_property_stream_dib_descriptors = sum(
        row.toolbook_property_stream_dib_descriptors for row in rows
    )
    total_toolbook_property_stream_metadata_descriptors = sum(
        row.toolbook_property_stream_metadata_descriptors for row in rows
    )
    total_toolbook_property_stream_nested_descriptors = sum(
        row.toolbook_property_stream_nested_descriptors for row in rows
    )
    total_toolbook_property_stream_container_nested_descriptors = sum(
        row.toolbook_property_stream_container_nested_descriptors for row in rows
    )
    total_toolbook_property_stream_unmatched_descriptors = sum(
        row.toolbook_property_stream_unmatched_descriptors for row in rows
    )
    total_toolbook_property_stream_unmatched_nested_descriptors = sum(
        row.toolbook_property_stream_unmatched_nested_descriptors for row in rows
    )
    total_toolbook_compressed_dib_descriptors = sum(row.toolbook_compressed_dib_descriptors for row in rows)
    total_unproven_dib_like = sum(row.unproven_dib_like_descriptors for row in rows)
    total_proven_image_like = total_extracted_image_media + total_toolbook_backed_bitmaps
    total_external_refs = sum(row.external_refs for row in rows)
    total_text_blocks = sum(row.text_blocks for row in rows)
    total_typed_text_values = sum(row.typed_text_values for row in rows)
    total_typed_text_object_owner_values = sum(row.typed_text_values_with_native_object_owner for row in rows)
    total_typed_text_storage_prefix_values = sum(row.typed_text_values_with_native_storage_prefix for row in rows)
    total_typed_text_structured_values = total_typed_text_object_owner_values + total_typed_text_storage_prefix_values
    total_typed_text_capacity_tail_values = sum(row.typed_text_capacity_tail_values for row in rows)
    total_typed_text_capacity_tail_bytes = sum(row.typed_text_capacity_tail_bytes for row in rows)
    total_typed_text_capacity_tail_nonzero_bytes = sum(row.typed_text_capacity_tail_nonzero_bytes for row in rows)
    total_typed_text_capacity_tail_text_values = sum(row.typed_text_capacity_tail_text_values for row in rows)
    total_large_text_values = sum(row.large_text_values for row in rows)
    total_field_hotword_run_tables = sum(row.field_hotword_run_tables for row in rows)
    total_field_hotword_run_table_rows = sum(row.field_hotword_run_table_rows for row in rows)
    total_field_hotword_run_table_active_rows = sum(row.field_hotword_run_table_active_rows for row in rows)
    total_field_hotword_run_table_linked_rows = sum(row.field_hotword_run_table_linked_rows for row in rows)
    total_field_hotword_run_table_bytes = sum(row.field_hotword_run_table_bytes for row in rows)
    total_page_background_offset_vectors = sum(row.page_background_offset_vectors for row in rows)
    total_page_background_offset_vector_bytes = sum(row.page_background_offset_vector_bytes for row in rows)
    total_page_background_offset_vector_offsets = sum(row.page_background_offset_vector_offsets for row in rows)
    total_page_background_offset_vector_nonzero_offsets = sum(
        row.page_background_offset_vector_nonzero_offsets for row in rows
    )
    total_page_background_payloads = sum(row.page_background_payloads for row in rows)
    total_page_background_payload_segments = sum(row.page_background_payload_segments for row in rows)
    total_page_background_payload_segment_bytes = sum(row.page_background_payload_segment_bytes for row in rows)
    total_page_background_bounded_payload_fragments = sum(
        row.page_background_bounded_payload_fragments for row in rows
    )
    total_page_background_bounded_payload_fragment_bytes = sum(
        row.page_background_bounded_payload_fragment_bytes for row in rows
    )
    total_book_payload_segments = sum(row.book_payload_segments for row in rows)
    total_book_payload_segment_bytes = sum(row.book_payload_segment_bytes for row in rows)
    total_book_common_native_headers = sum(row.book_common_native_headers for row in rows)
    total_book_common_native_header_bytes = sum(row.book_common_native_header_bytes for row in rows)
    total_book_reference_blocks = sum(row.book_reference_blocks for row in rows)
    total_book_control_descriptors = sum(row.book_control_descriptors for row in rows)
    total_book_control_descriptor_bytes = sum(row.book_control_descriptor_bytes for row in rows)
    total_book_pointer_target_name_prefixes = sum(row.book_pointer_target_name_prefixes for row in rows)
    total_book_pointer_target_name_prefix_bytes = sum(row.book_pointer_target_name_prefix_bytes for row in rows)
    total_book_pointer_target_leading_descriptors = sum(row.book_pointer_target_leading_descriptors for row in rows)
    total_book_pointer_target_leading_descriptor_bytes = sum(
        row.book_pointer_target_leading_descriptor_bytes for row in rows
    )
    total_book_named_payload_reference_inline_prefixes = sum(
        row.book_named_payload_reference_inline_prefixes for row in rows
    )
    total_book_named_payload_reference_inline_prefix_bytes = sum(
        row.book_named_payload_reference_inline_prefix_bytes for row in rows
    )
    total_book_palette_entries = sum(row.book_palette_entries for row in rows)
    total_book_pointer_tables = sum(row.book_pointer_tables for row in rows)
    total_book_pointer_table_entries = sum(row.book_pointer_table_entries for row in rows)
    total_book_pointer_table_bytes = sum(row.book_pointer_table_bytes for row in rows)
    total_book_pointer_table_reference_words = sum(row.book_pointer_table_reference_words for row in rows)
    total_book_pointer_table_reference_bytes = sum(row.book_pointer_table_reference_bytes for row in rows)
    total_book_pre_pointer_descriptor_blocks = sum(row.book_pre_pointer_descriptor_blocks for row in rows)
    total_book_pre_pointer_descriptor_bytes = sum(row.book_pre_pointer_descriptor_bytes for row in rows)
    total_book_compact_named_descriptors = sum(row.book_compact_named_descriptors for row in rows)
    total_book_compact_named_descriptor_bytes = sum(row.book_compact_named_descriptor_bytes for row in rows)
    total_book_pre_pointer_count_descriptors = sum(row.book_pre_pointer_count_descriptors for row in rows)
    total_book_pre_pointer_count_descriptor_bytes = sum(row.book_pre_pointer_count_descriptor_bytes for row in rows)
    total_book_compact_descriptor_payload_fragments = sum(
        row.book_compact_descriptor_payload_fragments for row in rows
    )
    total_book_compact_descriptor_payload_fragment_bytes = sum(
        row.book_compact_descriptor_payload_fragment_bytes for row in rows
    )
    total_book_named_payload_reference_descriptors = sum(row.book_named_payload_reference_descriptors for row in rows)
    total_book_named_payload_reference_descriptor_bytes = sum(
        row.book_named_payload_reference_descriptor_bytes for row in rows
    )
    total_book_openscript_objects = sum(row.book_openscript_objects for row in rows)
    total_book_openscript_object_bytes = sum(row.book_openscript_object_bytes for row in rows)
    total_book_openscript_code_bytes = sum(row.book_openscript_code_bytes for row in rows)
    total_book_openscript_auxiliary_prefixes = sum(row.book_openscript_auxiliary_prefixes for row in rows)
    total_book_openscript_auxiliary_prefix_bytes = sum(row.book_openscript_auxiliary_prefix_bytes for row in rows)
    total_book_openscript_duplicate_tails = sum(row.book_openscript_duplicate_tails for row in rows)
    total_book_openscript_duplicate_tail_bytes = sum(row.book_openscript_duplicate_tail_bytes for row in rows)
    total_book_openscript_record_links = sum(row.book_openscript_record_links for row in rows)
    total_book_openscript_record_link_bytes = sum(row.book_openscript_record_link_bytes for row in rows)
    total_book_pointer_target_payload_fragments = sum(row.book_pointer_target_payload_fragments for row in rows)
    total_book_pointer_target_payload_fragment_bytes = sum(
        row.book_pointer_target_payload_fragment_bytes for row in rows
    )
    total_book_named_payload_reference_payload_fragments = sum(
        row.book_named_payload_reference_payload_fragments for row in rows
    )
    total_book_named_payload_reference_payload_fragment_bytes = sum(
        row.book_named_payload_reference_payload_fragment_bytes for row in rows
    )
    total_book_zero_reserved_gaps = sum(row.book_zero_reserved_gaps for row in rows)
    total_book_zero_reserved_gap_bytes = sum(row.book_zero_reserved_gap_bytes for row in rows)
    total_embedded_native_text_objects = sum(row.embedded_native_text_objects for row in rows)
    total_self_reference_offset_tables = sum(row.self_reference_offset_tables for row in rows)
    total_self_reference_offset_table_entries = sum(row.self_reference_offset_table_entries for row in rows)
    total_self_reference_offset_table_nonzero_entries = sum(
        row.self_reference_offset_table_nonzero_entries for row in rows
    )
    total_self_reference_offset_table_linked_text_objects = sum(
        row.self_reference_offset_table_linked_text_objects for row in rows
    )
    total_self_reference_child_object_headers = sum(row.self_reference_child_object_headers for row in rows)
    total_self_reference_child_object_header_bytes = sum(row.self_reference_child_object_header_bytes for row in rows)
    total_self_reference_child_object_spans = sum(row.self_reference_child_object_spans for row in rows)
    total_self_reference_child_object_span_bytes = sum(row.self_reference_child_object_span_bytes for row in rows)
    total_self_reference_final_child_object_spans = sum(
        row.self_reference_final_child_object_spans for row in rows
    )
    total_self_reference_final_child_object_span_bytes = sum(
        row.self_reference_final_child_object_span_bytes for row in rows
    )
    total_self_reference_offset_table_bytes = sum(row.self_reference_offset_table_bytes for row in rows)
    total_probable_objects = sum(row.probable_objects for row in rows)
    total_handlers = sum(row.handlers for row in rows)
    total_native_records = sum(row.native_records for row in rows)
    total_native_pages = sum(row.native_index_pages for row in rows)
    total_active_record_bytes = sum(row.active_record_bytes for row in rows)
    total_inactive_payload_bytes = sum(row.inactive_payload_bytes for row in rows)
    nested_dib_unclassified = sum(row.nested_dib_bitmap_descriptors for row in rows) - (
        total_toolbook_compressed_dib_descriptors
        + total_nested_dib_container_extracted_descriptors
        + total_nested_dib_chain_crosses_metadata_descriptors
        + total_nested_dib_chain_spans_records_descriptors
        + total_nested_dib_chain_property_metadata_descriptors
        + total_nested_dib_chain_property_nested_descriptors
        + total_nested_dib_chain_property_unmatched_descriptors
        + total_nested_dib_chain_invalid_descriptors
    )
    native_record_unclassified = sum(row.native_record_bitmap_descriptors for row in rows) - (
        total_toolbook_bitmap_info_descriptors
        + total_toolbook_bitmap_info_container_descriptors
        + total_toolbook_bitmap_info_native_payload_descriptors
        + total_native_record_nested_dib_container_descriptors
        + total_native_record_native_payload_descriptors
    )
    bitmap_reason_totals = [
        ("native record at pixel start", native_record_unclassified),
        ("bitmap info, no contiguous pixels", total_toolbook_bitmap_info_descriptors),
        ("bitmap info container before nested DIB", total_toolbook_bitmap_info_container_descriptors),
        ("bitmap info native payload", total_toolbook_bitmap_info_native_payload_descriptors),
        ("native record container before nested DIB", total_native_record_nested_dib_container_descriptors),
        ("native record payload, not pixels", total_native_record_native_payload_descriptors),
        ("nested native descriptor header", sum(row.nested_native_header_bitmap_descriptors for row in rows)),
        ("nested DIB in pixel range", nested_dib_unclassified),
        ("nested DIB container with extracted DIB", total_nested_dib_container_extracted_descriptors),
        ("nested DIB chain crosses native metadata", total_nested_dib_chain_crosses_metadata_descriptors),
        ("nested DIB chain spans native records", total_nested_dib_chain_spans_records_descriptors),
        ("nested DIB chain to property metadata", total_nested_dib_chain_property_metadata_descriptors),
        ("nested DIB chain to property+nested DIB", total_nested_dib_chain_property_nested_descriptors),
        ("nested DIB chain to unmatched PHYSSIZE", total_nested_dib_chain_property_unmatched_descriptors),
        ("nested DIB chain to invalid metadata", total_nested_dib_chain_invalid_descriptors),
        ("compressed DIB payload", total_toolbook_compressed_dib_descriptors),
        ("unsupported native record type", sum(row.unsupported_bitmap_record_type_descriptors for row in rows)),
        ("class 41 icon size mismatch", total_native_class41_icon_descriptors_unhandled),
        ("unclassified native property stream", total_toolbook_property_stream_dib_descriptors),
        ("property metadata, not pixels", total_toolbook_property_stream_metadata_descriptors),
        ("property metadata before nested DIB", total_toolbook_property_stream_nested_descriptors),
        (
            "property container before nested PHYSSIZE",
            total_toolbook_property_stream_container_nested_descriptors,
        ),
        ("unmatched PHYSSIZE property stream", total_toolbook_property_stream_unmatched_descriptors),
        (
            "unmatched PHYSSIZE before nested DIB",
            total_toolbook_property_stream_unmatched_nested_descriptors,
        ),
        ("missing ToolBook envelope", sum(row.missing_envelope_bitmap_descriptors for row in rows)),
        ("pixel range outside file", sum(row.invalid_bitmap_descriptors for row in rows)),
        ("suppressed 1x1 candidate", sum(row.suppressed_bitmap_descriptors for row in rows)),
    ]

    def ratio(numer: int, denom: int) -> str:
        percent = (numer / denom * 100.0) if denom else 100.0
        return f"{numer} / {denom} ({percent:.1f}%)"

    def bitmap_breakdown(row: ExtractionResult) -> str:
        parts = []
        native_unclassified = row.native_record_bitmap_descriptors - (
            row.toolbook_bitmap_info_descriptors
            + row.toolbook_bitmap_info_container_descriptors
            + row.toolbook_bitmap_info_native_payload_descriptors
            + row.native_record_nested_dib_container_descriptors
            + row.native_record_native_payload_descriptors
        )
        nested_unclassified = row.nested_dib_bitmap_descriptors - (
            row.toolbook_compressed_dib_descriptors
            + row.nested_dib_container_extracted_descriptors
            + row.nested_dib_chain_crosses_metadata_descriptors
            + row.nested_dib_chain_spans_records_descriptors
            + row.nested_dib_chain_property_metadata_descriptors
            + row.nested_dib_chain_property_nested_descriptors
            + row.nested_dib_chain_property_unmatched_descriptors
            + row.nested_dib_chain_invalid_descriptors
        )
        if native_unclassified:
            parts.append(f"native:{native_unclassified}")
        if row.toolbook_bitmap_info_descriptors:
            parts.append(f"info:{row.toolbook_bitmap_info_descriptors}")
        if row.toolbook_bitmap_info_container_descriptors:
            parts.append(f"infocont:{row.toolbook_bitmap_info_container_descriptors}")
        if row.toolbook_bitmap_info_native_payload_descriptors:
            parts.append(f"infopayload:{row.toolbook_bitmap_info_native_payload_descriptors}")
        if row.native_record_nested_dib_container_descriptors:
            parts.append(f"nativecont:{row.native_record_nested_dib_container_descriptors}")
        if row.native_record_native_payload_descriptors:
            parts.append(f"nativepayload:{row.native_record_native_payload_descriptors}")
        if nested_unclassified:
            parts.append(f"nested:{nested_unclassified}")
        if row.nested_dib_container_extracted_descriptors:
            parts.append(f"nestedx:{row.nested_dib_container_extracted_descriptors}")
        if row.nested_dib_chain_crosses_metadata_descriptors:
            parts.append(f"nestedmeta:{row.nested_dib_chain_crosses_metadata_descriptors}")
        if row.nested_dib_chain_spans_records_descriptors:
            parts.append(f"nestedspan:{row.nested_dib_chain_spans_records_descriptors}")
        if row.nested_dib_chain_property_metadata_descriptors:
            parts.append(f"nestedpmeta:{row.nested_dib_chain_property_metadata_descriptors}")
        if row.nested_dib_chain_property_nested_descriptors:
            parts.append(f"nestedpnested:{row.nested_dib_chain_property_nested_descriptors}")
        if row.nested_dib_chain_property_unmatched_descriptors:
            parts.append(f"nestedpunmatch:{row.nested_dib_chain_property_unmatched_descriptors}")
        if row.nested_dib_chain_invalid_descriptors:
            parts.append(f"nestedinvalid:{row.nested_dib_chain_invalid_descriptors}")
        if row.toolbook_compressed_dib_descriptors:
            parts.append(f"cmp:{row.toolbook_compressed_dib_descriptors}")
        if row.nested_native_header_bitmap_descriptors:
            parts.append(f"desc:{row.nested_native_header_bitmap_descriptors}")
        if row.unsupported_bitmap_record_type_descriptors:
            parts.append(f"type:{row.unsupported_bitmap_record_type_descriptors}")
        if row.native_class41_icon_descriptors_unhandled:
            parts.append(f"cls41:{row.native_class41_icon_descriptors_unhandled}")
        if row.toolbook_property_stream_dib_descriptors:
            parts.append(f"prop:{row.toolbook_property_stream_dib_descriptors}")
        if row.toolbook_property_stream_metadata_descriptors:
            parts.append(f"pmeta:{row.toolbook_property_stream_metadata_descriptors}")
        if row.toolbook_property_stream_nested_descriptors:
            parts.append(f"pnested:{row.toolbook_property_stream_nested_descriptors}")
        if row.toolbook_property_stream_container_nested_descriptors:
            parts.append(f"pcontainer:{row.toolbook_property_stream_container_nested_descriptors}")
        if row.toolbook_property_stream_unmatched_descriptors:
            parts.append(f"punmatch:{row.toolbook_property_stream_unmatched_descriptors}")
        if row.toolbook_property_stream_unmatched_nested_descriptors:
            parts.append(f"punest:{row.toolbook_property_stream_unmatched_nested_descriptors}")
        if row.missing_envelope_bitmap_descriptors:
            parts.append(f"noenv:{row.missing_envelope_bitmap_descriptors}")
        if row.invalid_bitmap_descriptors:
            parts.append(f"invalid:{row.invalid_bitmap_descriptors}")
        if row.suppressed_bitmap_descriptors:
            parts.append(f"1x1:{row.suppressed_bitmap_descriptors}")
        return ", ".join(parts) if parts else "0"

    css = """
    :root { color-scheme: dark; font-family: Inter, system-ui, sans-serif; background: #0d1117; color: #d8dee9; }
    body { margin: 0; padding: 28px; }
    h1, h2 { margin: 0 0 12px; }
    .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 12px; margin: 18px 0 28px; }
    .metric { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 14px; }
    .metric b { display: block; font-size: 24px; color: #f0f6fc; margin-top: 6px; }
    .metric span { display: block; color: #9fb3c8; margin-top: 5px; font-size: 12px; }
    table { width: 100%; border-collapse: collapse; margin: 10px 0 28px; font-size: 13px; }
    th, td { border-bottom: 1px solid #30363d; padding: 8px 10px; text-align: left; vertical-align: top; }
    th { color: #9fb3c8; background: #161b22; position: sticky; top: 0; }
    .ok { color: #7ee787; }
    .skipped { color: #ffb86c; }
    code { color: #c9d1d9; }
    .note { color: #9fb3c8; max-width: 980px; line-height: 1.45; }
    """

    parts = [
        "<!doctype html>",
        "<html><head><meta charset='utf-8'><title>Asymetrix ToolBook Extraction Report</title>",
        f"<style>{css}</style></head><body>",
        "<h1>Asymetrix ToolBook Extraction Report</h1>",
        "<p class='note'>This report was generated from the deterministic extractor. Content is extracted only from active native records reached through the ToolBook index. Handled image/media means bytes were written as an extracted file. ToolBook bitmap-info descriptors carry DIB header/palette metadata but no contiguous pixel payload in the observed record. ToolBook DIB/property-stream images are extracted only when the native PHYSSIZE property and local descriptor pointer identify the post-property pixel bytes. Remaining PHYSSIZE/property-stream records are split into direct or compound native metadata descriptors, metadata-before-nested-DIB descriptors, and unmatched-PHYSSIZE descriptors, not treated as direct pixel payloads. Nested-DIB chains are extracted only when the terminal DIB is fully bounded by the same native record; chains crossing native index pages or later native records are reported separately because treating those physical bytes as contiguous pixels produces garbage. ToolBook compressed DIB descriptors have source-bounded compressed payloads whose opcodes are not decoded yet. DIB-shaped metadata candidates are listed separately and are not counted as proven image resources. External references are listed but not embedded in the book.</p>",
        "<div class='summary'>",
        f"<div class='metric'>Samples<b>{len(rows)}</b></div>",
        f"<div class='metric'>Supported<b>{total_ok}</b></div>",
        f"<div class='metric'>Skipped<b>{len(rows) - total_ok}</b></div>",
        f"<div class='metric'>Files written<b>{total_files}</b></div>",
        f"<div class='metric'>Proven image/media handled<b>{html.escape(ratio(total_extracted_image_media, total_proven_image_like))}</b><span>embedded:{total_embedded_media}, reconstructed DIB:{total_reconstructed}, property DIB:{total_native_property_stream_images}, nested DIB:{total_native_nested_dib_images}, class41 icons:{total_native_class41_icons}</span></div>",
        f"<div class='metric'>Native property-stream DIBs extracted<b>{total_native_property_stream_images}</b><span>PHYSSIZE plus local pixel pointer</span></div>",
        f"<div class='metric'>Native nested DIBs extracted<b>{total_native_nested_dib_images}</b><span>contiguous DIB inside source descriptor</span></div>",
        f"<div class='metric'>Native class 41 icons extracted<b>{total_native_class41_icons}</b><span>source-described icon DIB payloads</span></div>",
        f"<div class='metric'>Native class 41 icon descriptors unhandled<b>{total_native_class41_icon_descriptors_unhandled}</b><span>stored size shorter than icon payload</span></div>",
        f"<div class='metric'>ToolBook bitmap records unhandled<b>{total_toolbook_backed_bitmaps}</b><span>source-backed descriptors</span></div>",
        f"<div class='metric'>ToolBook bitmap info descriptors<b>{total_toolbook_bitmap_info_descriptors}</b><span>DIB header, no contiguous pixels</span></div>",
        f"<div class='metric'>Bitmap-info containers before nested DIB<b>{total_toolbook_bitmap_info_container_descriptors}</b><span>source-backed native container records</span></div>",
        f"<div class='metric'>Bitmap-info native payloads<b>{total_toolbook_bitmap_info_native_payload_descriptors}</b><span>script/object bytes at pixel slot</span></div>",
        f"<div class='metric'>Native containers before nested DIB<b>{total_native_record_nested_dib_container_descriptors}</b><span>not source-backed bitmap records</span></div>",
        f"<div class='metric'>Native payloads at pixel slot<b>{total_native_record_native_payload_descriptors}</b><span>object/script bytes, no nested DIB</span></div>",
        f"<div class='metric'>Nested DIB containers extracted<b>{total_nested_dib_container_extracted_descriptors}</b><span>outer descriptor before contiguous DIB</span></div>",
        f"<div class='metric'>Nested DIB chains crossing metadata<b>{total_nested_dib_chain_crosses_metadata_descriptors}</b><span>terminal DIB spans native index/page bytes</span></div>",
        f"<div class='metric'>Nested DIB chains spanning records<b>{total_nested_dib_chain_spans_records_descriptors}</b><span>terminal DIB runs into later native records</span></div>",
        f"<div class='metric'>Nested chains to property metadata<b>{total_nested_dib_chain_property_metadata_descriptors}</b><span>terminal property stream, no pixels</span></div>",
        f"<div class='metric'>Nested chains to property+nested DIB<b>{total_nested_dib_chain_property_nested_descriptors}</b><span>terminal property metadata before another descriptor</span></div>",
        f"<div class='metric'>Nested chains to unmatched PHYSSIZE<b>{total_nested_dib_chain_property_unmatched_descriptors}</b><span>property stream present, value layout unresolved</span></div>",
        f"<div class='metric'>Nested chains to invalid metadata<b>{total_nested_dib_chain_invalid_descriptors}</b><span>terminal nested metadata range invalid</span></div>",
        f"<div class='metric'>Unclassified DIB/property streams<b>{total_toolbook_property_stream_dib_descriptors}</b><span>PHYSSIZE rule not proven</span></div>",
        f"<div class='metric'>Property-stream metadata descriptors<b>{total_toolbook_property_stream_metadata_descriptors}</b><span>PHYSSIZE matches dimensions, no pixel payload</span></div>",
        f"<div class='metric'>Property metadata before nested DIB<b>{total_toolbook_property_stream_nested_descriptors}</b><span>native metadata precedes another descriptor</span></div>",
        f"<div class='metric'>Property containers before nested PHYSSIZE<b>{total_toolbook_property_stream_container_nested_descriptors}</b><span>outer descriptor wraps a matched nested descriptor</span></div>",
        f"<div class='metric'>Unmatched PHYSSIZE descriptors<b>{total_toolbook_property_stream_unmatched_descriptors}</b><span>property stream present, dimensions not proven</span></div>",
        f"<div class='metric'>Unmatched PHYSSIZE before nested DIB<b>{total_toolbook_property_stream_unmatched_nested_descriptors}</b><span>property stream precedes another descriptor</span></div>",
        f"<div class='metric'>ToolBook compressed DIB descriptors<b>{total_toolbook_compressed_dib_descriptors}</b><span>compressed payload not decoded</span></div>",
        f"<div class='metric'>DIB-shaped metadata candidates<b>{total_unproven_dib_like}</b><span>active records, not proven images</span></div>",
        f"<div class='metric'>External refs listed<b>{total_external_refs}</b><span>not embedded payloads</span></div>",
        f"<div class='metric'>Typed text values handled<b>{total_typed_text_values}</b><span>owner-tied explicit-length values</span></div>",
        f"<div class='metric'>Typed text structured<b>{html.escape(ratio(total_typed_text_structured_values, total_typed_text_values))}</b><span>object owner or storage prefix</span></div>",
        f"<div class='metric'>Typed text object-owned<b>{html.escape(ratio(total_typed_text_object_owner_values, total_typed_text_values))}</b><span>native object header matched</span></div>",
        f"<div class='metric'>Typed text storage-prefixed<b>{html.escape(ratio(total_typed_text_storage_prefix_values, total_typed_text_values))}</b><span>native text prefix matched</span></div>",
        f"<div class='metric'>Typed text capacity tails<b>{html.escape(ratio(total_typed_text_capacity_tail_values, total_typed_text_values))}</b><span>{total_typed_text_capacity_tail_bytes} bytes, {total_typed_text_capacity_tail_nonzero_bytes} nonzero, {total_typed_text_capacity_tail_text_values} printable tails</span></div>",
        f"<div class='metric'>Large field text descriptors<b>{total_large_text_values}</b><span>field-owned pointer/length text storage</span></div>",
        f"<div class='metric'>Field hotword run tables<b>{total_field_hotword_run_tables}</b><span>{total_field_hotword_run_table_rows} rows, {total_field_hotword_run_table_active_rows} active, {total_field_hotword_run_table_linked_rows} linked, {total_field_hotword_run_table_bytes} bytes</span></div>",
        f"<div class='metric'>Page/Background offset vectors<b>{total_page_background_offset_vectors}</b><span>{total_page_background_offset_vector_bytes} bytes, {total_page_background_offset_vector_nonzero_offsets}/{total_page_background_offset_vector_offsets} nonzero offsets</span></div>",
        f"<div class='metric'>Page/Background payload maps<b>{total_page_background_payloads}</b><span>{total_page_background_payload_segments} segments/{total_page_background_payload_segment_bytes} bytes, bounded fragments:{total_page_background_bounded_payload_fragments}/{total_page_background_bounded_payload_fragment_bytes} bytes</span></div>",
        f"<div class='metric'>Book payload segments<b>{total_book_payload_segments}</b><span>{total_book_payload_segment_bytes} bytes, common headers:{total_book_common_native_headers}/{total_book_common_native_header_bytes} bytes, refs:{total_book_reference_blocks}, ref controls:{total_book_control_descriptors}/{total_book_control_descriptor_bytes} bytes, pointer target name prefixes:{total_book_pointer_target_name_prefixes}/{total_book_pointer_target_name_prefix_bytes} bytes, pointer target leading descriptors:{total_book_pointer_target_leading_descriptors}/{total_book_pointer_target_leading_descriptor_bytes} bytes, named payload inline prefixes:{total_book_named_payload_reference_inline_prefixes}/{total_book_named_payload_reference_inline_prefix_bytes} bytes, palette entries:{total_book_palette_entries}, pointer tables:{total_book_pointer_tables}/{total_book_pointer_table_entries} entries/{total_book_pointer_table_bytes} bytes, table refs:{total_book_pointer_table_reference_words}/{total_book_pointer_table_reference_bytes} bytes, pre-table descriptors:{total_book_pre_pointer_descriptor_blocks}/{total_book_pre_pointer_descriptor_bytes} bytes, compact descriptors:{total_book_compact_named_descriptors}/{total_book_compact_named_descriptor_bytes} bytes, compact payload fragments:{total_book_compact_descriptor_payload_fragments}/{total_book_compact_descriptor_payload_fragment_bytes} bytes, named payload refs:{total_book_named_payload_reference_descriptors}/{total_book_named_payload_reference_descriptor_bytes} bytes, named payload fragments:{total_book_named_payload_reference_payload_fragments}/{total_book_named_payload_reference_payload_fragment_bytes} bytes, OpenScript objects:{total_book_openscript_objects}/{total_book_openscript_object_bytes} bytes/{total_book_openscript_code_bytes} code bytes, OpenScript record links:{total_book_openscript_record_links}/{total_book_openscript_record_link_bytes} bytes, OpenScript aux prefixes:{total_book_openscript_auxiliary_prefixes}/{total_book_openscript_auxiliary_prefix_bytes} bytes, OpenScript duplicate tails:{total_book_openscript_duplicate_tails}/{total_book_openscript_duplicate_tail_bytes} bytes, pointer target fragments:{total_book_pointer_target_payload_fragments}/{total_book_pointer_target_payload_fragment_bytes} bytes, pre-table count descriptors:{total_book_pre_pointer_count_descriptors}/{total_book_pre_pointer_count_descriptor_bytes} bytes, zero reserved:{total_book_zero_reserved_gaps}/{total_book_zero_reserved_gap_bytes} bytes</span></div>",
        f"<div class='metric'>Embedded text objects decoded<b>{total_embedded_native_text_objects}</b><span>strict native object patterns</span></div>",
        f"<div class='metric'>Self-ref offset tables decoded<b>{total_self_reference_offset_tables}</b><span>{total_self_reference_offset_table_entries} entries, {total_self_reference_offset_table_nonzero_entries} nonzero, {total_self_reference_offset_table_linked_text_objects} linked text objects, {total_self_reference_offset_table_bytes} bytes</span></div>",
        f"<div class='metric'>Self-ref child object headers<b>{total_self_reference_child_object_headers}</b><span>{total_self_reference_child_object_header_bytes} bytes named from table pointers</span></div>",
        f"<div class='metric'>Bounded child object spans<b>{total_self_reference_child_object_spans}</b><span>{total_self_reference_child_object_span_bytes} bytes, final-to-record-end:{total_self_reference_final_child_object_spans}/{total_self_reference_final_child_object_span_bytes} bytes</span></div>",
        f"<div class='metric'>Other text blocks extracted<b>{total_text_blocks}</b><span>generic printable fragments</span></div>",
        f"<div class='metric'>Object model unresolved<b>{total_probable_objects}</b><span>handlers:{total_handlers}</span></div>",
        f"<div class='metric'>Native records parsed<b>{total_native_records}</b><span>index pages:{total_native_pages}</span></div>",
        f"<div class='metric'>Active record bytes<b>{total_active_record_bytes}</b><span>inactive payload bytes:{total_inactive_payload_bytes}</span></div>",
        "</div>",
        "<div class='summary'>",
    ]
    for kind in SUPPORTED_MEDIA:
        parts.append(f"<div class='metric'>{html.escape(kind.upper())}<b>{total_media[kind]}</b></div>")
    parts.append("</div>")
    parts.append("<h2>Unhandled Bitmap Descriptor Reasons</h2>")
    parts.append("<div class='summary'>")
    for label, count in bitmap_reason_totals:
        parts.append(f"<div class='metric'>{html.escape(label)}<b>{count}</b></div>")
    parts.append("</div>")

    for group in sorted(grouped):
        parts.append(f"<h2>{html.escape(group)}</h2>")
        parts.append(
            "<table><thead><tr><th>Sample</th><th>Status</th><th>Input bytes</th><th>Wrapper</th>"
            "<th>TBK offset</th><th>Version</th><th>Files</th><th>Proven image/media handled</th>"
            "<th>Unhandled image metadata</th><th>Source-backed / candidates</th><th>External refs listed</th>"
            "<th>Native index</th><th>Objects unresolved</th><th>Handlers unresolved</th><th>Stored text</th><th>Text objects</th><th>Other text</th>"
            "<th>Output / reason</th></tr></thead><tbody>"
        )
        for row in grouped[group]:
            handled_image_media = (
                row.embedded_media
                + row.reconstructed_images
                + row.native_property_stream_images
                + row.native_nested_dib_images
                + row.native_class41_icons
            )
            proven_image_like = handled_image_media + row.toolbook_backed_bitmap_descriptors
            handled_summary = (
                f"{html.escape(ratio(handled_image_media, proven_image_like))}<br>"
                f"<code>embedded:{row.embedded_media}, dib:{row.reconstructed_images}, "
                f"propdib:{row.native_property_stream_images}, nestdib:{row.native_nested_dib_images}, "
                f"ico:{row.native_class41_icons}</code>"
            )
            unhandled_summary = (
                f"{row.unhandled_bitmap_descriptors}<br><code>{html.escape(bitmap_breakdown(row))}</code>"
            )
            source_summary = (
                f"ToolBook:{row.toolbook_backed_bitmap_descriptors}<br>"
                f"Info:{row.toolbook_bitmap_info_descriptors}<br>"
                f"InfoCont:{row.toolbook_bitmap_info_container_descriptors}<br>"
                f"InfoPayload:{row.toolbook_bitmap_info_native_payload_descriptors}<br>"
                f"NativeCont:{row.native_record_nested_dib_container_descriptors}<br>"
                f"NativePayload:{row.native_record_native_payload_descriptors}<br>"
                f"NestedExtract:{row.nested_dib_container_extracted_descriptors}<br>"
                f"NestedMeta:{row.nested_dib_chain_crosses_metadata_descriptors}<br>"
                f"NestedSpan:{row.nested_dib_chain_spans_records_descriptors}<br>"
                f"NestedPropMeta:{row.nested_dib_chain_property_metadata_descriptors}<br>"
                f"NestedPropNested:{row.nested_dib_chain_property_nested_descriptors}<br>"
                f"NestedPropUnmatch:{row.nested_dib_chain_property_unmatched_descriptors}<br>"
                f"NestedInvalid:{row.nested_dib_chain_invalid_descriptors}<br>"
                f"Props:{row.toolbook_property_stream_dib_descriptors}<br>"
                f"PropMeta:{row.toolbook_property_stream_metadata_descriptors}<br>"
                f"PropNested:{row.toolbook_property_stream_nested_descriptors}<br>"
                f"PropContainer:{row.toolbook_property_stream_container_nested_descriptors}<br>"
                f"PropUnmatch:{row.toolbook_property_stream_unmatched_descriptors}<br>"
                f"PropUnNest:{row.toolbook_property_stream_unmatched_nested_descriptors}<br>"
                f"Compressed:{row.toolbook_compressed_dib_descriptors}<br>"
                f"Class41:{row.native_class41_icon_descriptors_unhandled}<br>"
                f"DIB-like:{row.unproven_dib_like_descriptors}"
            )
            native_summary = (
                f"{row.native_records} records / {row.native_index_pages} pages<br>"
                f"<code>{row.active_record_coverage_percent:.1f}% active</code>"
            )
            cls = "ok" if row.status == "ok" else "skipped"
            if row.status == "ok":
                output_or_reason = (
                    f"<a href='{html.escape(row.output_dir, quote=True)}/' target='_blank' "
                    f"rel='noopener'><code>{html.escape(row.output_dir)}</code></a>"
                )
            else:
                output_or_reason = html.escape(row.reason)
            parts.append(
                "<tr>"
                f"<td><code>{html.escape(Path(row.input_path).name)}</code></td>"
                f"<td class='{cls}'>{html.escape(row.status)}</td>"
                f"<td>{row.input_size}</td>"
                f"<td>{html.escape(row.wrapper_kind)}</td>"
                f"<td>{row.tbk_offset}</td>"
                f"<td><code>{html.escape(row.version_hex)}</code></td>"
                f"<td>{row.files_written}</td>"
                f"<td>{handled_summary}</td>"
                f"<td>{unhandled_summary}</td>"
                f"<td>{source_summary}</td>"
                f"<td>{row.external_refs}</td>"
                f"<td>{native_summary}</td>"
                f"<td>{row.probable_objects}</td>"
                f"<td>{row.handlers}</td>"
                f"<td>{row.typed_text_values}<br><code>object:{row.typed_text_values_with_native_object_owner}, prefix:{row.typed_text_values_with_native_storage_prefix}, tails:{row.typed_text_capacity_tail_values}, large:{row.large_text_values}, hotruns:{row.field_hotword_run_tables}</code></td>"
                f"<td>{row.embedded_native_text_objects}</td>"
                f"<td>{row.text_blocks}</td>"
                f"<td>{output_or_reason}</td>"
                "</tr>"
            )
        parts.append("</tbody></table>")

    parts.append("</body></html>\n")
    write_text(report_path, "\n".join(parts))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract observed Asymetrix ToolBook files into a byte-accounted output directory."
    )
    parser.add_argument("inputFile", nargs="?", help="ToolBook .tbk/.exe-wrapped input file")
    parser.add_argument("outputDir", nargs="?", help="output directory")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="also write diagnostic metadata, byte maps, native segments, handler contexts, and payload copies",
    )
    parser.add_argument(
        "--make-report",
        nargs=3,
        metavar=("SAMPLE_ROOT", "EXTRACT_ROOT", "REPORT_HTML"),
        help="one-time helper used to extract every sample under SAMPLE_ROOT and build an HTML report",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        if args.make_report:
            sample_root, extract_root, report_html = (Path(x) for x in args.make_report)
            run_report(sample_root, extract_root, report_html, verbose=args.verbose)
            return 0
        if not args.inputFile or not args.outputDir:
            raise ToolBookError("usage: asymetrixToolbook.py <inputFile> <outputDir>")
        result = extract_file(Path(args.inputFile), Path(args.outputDir), verbose=args.verbose)
        print(
            json.dumps(
                {
                    "status": result.status,
                    "files_written": result.files_written,
                    "media_counts": result.media_counts,
                    "output_dir": result.output_dir,
                },
                sort_keys=True,
            )
        )
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

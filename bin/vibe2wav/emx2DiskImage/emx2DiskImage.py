#!/usr/bin/env python3
# Vibe coded by Codex
"""Strict extractor for the E-mu EMAX-II EMX2 SyQuest disk image format."""

from __future__ import annotations

import hashlib
import html
import json
import os
import re
import shutil
import struct
import sys
import tempfile
import wave
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import quote


SECTOR_SIZE = 512
DIRECTORY_ENTRY_SIZE = 32
DIRECTORY_ENTRY_COUNT = SECTOR_SIZE // DIRECTORY_ENTRY_SIZE
FAT_FREE = 0x0000
FAT_END = 0x7FFF
FAT_RESERVED = 0x8000
BANK_HEADER_SIZE = 0x7000
PRESET_POINTER_COUNT = 100
SAMPLE_DESCRIPTOR_OFFSET = 0x5E00
SAMPLE_DESCRIPTOR_SIZE = 32
SAMPLE_DESCRIPTOR_COUNT = 144
SAMPLE_FIRST_WORD = 44
SAMPLE_PREFIX_WORDS = 2
SAMPLE_TRAILER_WORDS = 40
SAMPLE_OVERHEAD_WORDS = SAMPLE_PREFIX_WORDS + SAMPLE_TRAILER_WORDS
EMX2_CONFIGURATION = bytes.fromhex("01 01 ab 52 01 00 00 00 00 00 01 0d 01 01")
SAMPLE_RATES = {
    0: 10000,
    1: 15625,
    2: 20000,
    3: 22050,
    4: 27778,
    5: 31250,
    6: 41667,
    7: 44100,
    8: 39063,
}


class FormatError(Exception):
    """Raised when an input is not the supported EMX2 image profile."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise FormatError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def clean_name(value: str, fallback: str) -> str:
    value = value.replace("/", "_").replace("\\", "_")
    value = re.sub(r"[^A-Za-z0-9._'() -]", "_", value).strip(" .")
    return value or fallback


def decode_fixed_name(raw: bytes, context: str) -> str:
    nul = raw.find(b"\x00")
    require(nul >= 0, f"{context}: name has no NUL terminator")
    visible = raw[:nul]
    require(not any(raw[nul:]), f"{context}: nonzero byte after name terminator")
    require(all(0x20 <= byte <= 0x7E for byte in visible), f"{context}: name is not ASCII")
    return visible.decode("ascii").rstrip()


@dataclass
class SourceSegment:
    source_offset: int
    length: int
    logical_offset: int


@dataclass
class DirectoryEntry:
    index: int
    name: str
    bank_number: int
    start_cluster: int
    cluster_count: int
    used_sectors: int
    final_sector_bytes: int
    flags: int
    size: int
    chain: list[int] = field(default_factory=list)


@dataclass
class Preset:
    number: int
    name: str
    bank_offset: int
    region_end_bank_offset: int | None


@dataclass
class Sample:
    number: int
    descriptor_slot: int
    identifier: int
    start_word: int
    end_word: int
    sustain_start_word: int
    sustain_end_word: int
    release_start_word: int
    release_end_word: int
    format_word: int
    rate_code: int
    sample_rate: int
    loop_flags: int
    prefix: bytes
    pcm: bytes
    trailer: bytes
    allocation: bytes

    @property
    def is_used(self) -> bool:
        return self.identifier != 0

    @property
    def frame_count(self) -> int:
        return len(self.pcm) // 2

    def loop(self) -> tuple[int, int] | None:
        if not self.loop_flags:
            return None
        start = self.sustain_start_word - self.start_word - 2
        end = self.sustain_end_word - self.start_word - 3
        if 0 <= start <= end < self.frame_count:
            return start, end
        return None

    @property
    def loop_status(self) -> str:
        if not self.loop_flags:
            return "disabled"
        return "enabled" if self.loop() is not None else "invalid"


@dataclass
class Bank:
    entry: DirectoryEntry
    raw: bytes
    segments: list[SourceSegment]
    presets: list[Preset]
    samples: list[Sample]
    sample_data_end: int
    sequencer_data: bytes
    sequencer_payload: bytes
    warnings: list[str]


@dataclass
class ParsedImage:
    source: Path
    data: bytes
    header: dict[str, int]
    metadata_regions: list[tuple[int, int, str, str]]
    operating_system: bytes
    operating_system_entry: DirectoryEntry
    operating_system_segments: list[SourceSegment]
    banks: list[Bank]
    deleted_entries: list[DirectoryEntry]


def read_chain(
    data: bytes,
    chain: list[int],
    size: int,
    first_cluster_offset: int,
    cluster_size: int,
    context: str,
) -> tuple[bytes, list[SourceSegment]]:
    output = bytearray()
    segments: list[SourceSegment] = []
    remaining = size
    for cluster in chain:
        take = min(remaining, cluster_size)
        source_offset = first_cluster_offset + (cluster - 1) * cluster_size
        require(source_offset >= 0 and source_offset + take <= len(data), f"{context}: extent is outside image")
        logical_offset = len(output)
        output.extend(data[source_offset : source_offset + take])
        segments.append(SourceSegment(source_offset, take, logical_offset))
        remaining -= take
        if remaining == 0:
            break
    require(remaining == 0, f"{context}: allocation chain is shorter than directory size")
    return bytes(output), segments


def parse_bank(entry: DirectoryEntry, raw: bytes, segments: list[SourceSegment]) -> Bank:
    context = f"bank {entry.bank_number} ({entry.name})"
    require(len(raw) >= BANK_HEADER_SIZE + SAMPLE_FIRST_WORD * 2, f"{context}: too short")
    require(raw[:2] == b"\xac\x81", f"{context}: invalid hard-disk bank marker")

    warnings: list[str] = []
    samples: list[Sample] = []
    declared_sample_end = struct.unpack_from("<I", raw, 0x1A8)[0]
    require(declared_sample_end >= SAMPLE_FIRST_WORD, f"{context}: invalid sample-memory end pointer")
    expected_start = SAMPLE_FIRST_WORD
    for number, descriptor_slot in enumerate(range(SAMPLE_DESCRIPTOR_COUNT - 1, -1, -1), 1):
        if expected_start == declared_sample_end:
            break
        values = struct.unpack_from(
            "<8I", raw, SAMPLE_DESCRIPTOR_OFFSET + descriptor_slot * SAMPLE_DESCRIPTOR_SIZE
        )
        identifier, start, end, sustain_start, sustain_end, release_start, release_end, format_word = values
        require(start == expected_start, f"{context}: sample descriptor chain breaks at sample {number}")
        require(end > start + SAMPLE_OVERHEAD_WORDS, f"{context}: sample {number} has no PCM payload")
        require(end <= declared_sample_end, f"{context}: sample {number} ends beyond sample memory")
        rate_code = (format_word >> 8) & 0xFF
        require(rate_code in SAMPLE_RATES, f"{context}: sample {number} has unsupported rate code {rate_code}")
        allocation_start = BANK_HEADER_SIZE + start * 2
        pcm_start = allocation_start + SAMPLE_PREFIX_WORDS * 2
        pcm_end = BANK_HEADER_SIZE + (end - SAMPLE_TRAILER_WORDS) * 2
        allocation_end = BANK_HEADER_SIZE + end * 2
        require(allocation_end <= len(raw), f"{context}: sample {number} allocation outside bank")
        sample = Sample(
            number=number,
            descriptor_slot=descriptor_slot,
            identifier=identifier,
            start_word=start,
            end_word=end,
            sustain_start_word=sustain_start,
            sustain_end_word=sustain_end,
            release_start_word=release_start,
            release_end_word=release_end,
            format_word=format_word,
            rate_code=rate_code,
            sample_rate=SAMPLE_RATES[rate_code],
            loop_flags=format_word & 0x03,
            prefix=raw[allocation_start:pcm_start],
            pcm=raw[pcm_start:pcm_end],
            trailer=raw[pcm_end:allocation_end],
            allocation=raw[allocation_start:allocation_end],
        )
        if sample.loop_status == "invalid":
            warnings.append(f"{context}: sample {number} has invalid loop addresses; WAV loop omitted")
        samples.append(sample)
        expected_start = end

    require(
        declared_sample_end == expected_start,
        f"{context}: sample-memory end pointer does not match descriptor chain",
    )
    sample_data_end = BANK_HEADER_SIZE + expected_start * 2
    require(sample_data_end <= len(raw), f"{context}: sample-memory end is outside directory extent")

    pointer_values = struct.unpack_from("<100H", raw, 0)
    require(pointer_values[0] == 0x81AC, f"{context}: invalid first preset pointer")
    pointer_offsets = [value & 0x7FFF for value in pointer_values]
    lowest_descriptor_offset = (
        SAMPLE_DESCRIPTOR_OFFSET + samples[-1].descriptor_slot * SAMPLE_DESCRIPTOR_SIZE
        if samples
        else BANK_HEADER_SIZE
    )
    pointer_table_clean = all(value & 0x8000 for value in pointer_values) and all(
        0x1AC <= offset and offset + 12 <= lowest_descriptor_offset for offset in pointer_offsets
    )
    pointer_table_clean = pointer_table_clean and all(
        left < right for left, right in zip(pointer_offsets, pointer_offsets[1:])
    )

    presets: list[Preset] = []
    invalid_preset_slots: list[int] = []
    for number, (value, offset) in enumerate(zip(pointer_values, pointer_offsets)):
        if not value & 0x8000 or not (0x1AC <= offset and offset + 12 <= lowest_descriptor_offset):
            invalid_preset_slots.append(number)
            pointer_table_clean = False
            continue
        name_raw = raw[offset : offset + 12]
        if name_raw[0] == 0:
            continue
        if not all(0x20 <= byte <= 0x7E for byte in name_raw):
            invalid_preset_slots.append(number)
            pointer_table_clean = False
            continue
        presets.append(
            Preset(
                number=number,
                name=name_raw.decode("ascii").rstrip(),
                bank_offset=offset,
                region_end_bank_offset=None,
            )
        )
    if invalid_preset_slots:
        slots = ", ".join(str(number) for number in invalid_preset_slots)
        warnings.append(f"{context}: invalid preset pointer slots preserved in bank metadata: {slots}")
    if not pointer_table_clean and not invalid_preset_slots:
        warnings.append(f"{context}: non-monotonic preset pointer table preserved in bank metadata")
    if pointer_table_clean:
        for preset in presets:
            preset.region_end_bank_offset = (
                pointer_offsets[preset.number + 1]
                if preset.number + 1 < PRESET_POINTER_COUNT
                else lowest_descriptor_offset
            )

    sequencer_data = raw[sample_data_end:]
    require(len(sequencer_data) % 2 == 0, f"{context}: sequencer appendix has an odd byte count")
    if sequencer_data:
        require(
            sequencer_data[0::2] == b"\x05" * (len(sequencer_data) // 2),
            f"{context}: invalid sequencer-cell tags",
        )
    return Bank(
        entry=entry,
        raw=raw,
        segments=segments,
        presets=presets,
        samples=samples,
        sample_data_end=sample_data_end,
        sequencer_data=sequencer_data,
        sequencer_payload=sequencer_data[1::2],
        warnings=warnings,
    )


def parse_image(source: Path) -> ParsedImage:
    try:
        data = source.read_bytes()
    except OSError as exc:
        raise FormatError(f"cannot read input: {exc}") from exc
    require(len(data) >= 7 * SECTOR_SIZE, "image is too short")
    require(len(data) % SECTOR_SIZE == 0, "image size is not a multiple of 512 bytes")

    superblock = data[:SECTOR_SIZE]
    require(superblock[:4] == b"EMX2", "missing EMX2 signature")
    values = struct.unpack_from("<9I", superblock, 4)
    (
        logical_sectors,
        directory_header_sector,
        allocation_map_sector,
        directory_sector,
        bank_sector_bias,
        fat_sector,
        fat_sector_count,
        cluster_size_kib,
        max_cluster,
    ) = values
    require(cluster_size_kib > 0 and cluster_size_kib * 1024 % SECTOR_SIZE == 0, "invalid cluster size")
    cluster_size = cluster_size_kib * 1024
    cluster_sectors = cluster_size // SECTOR_SIZE
    require(max_cluster > 0, "volume has no clusters")
    require(logical_sectors == (max_cluster + 1) * cluster_sectors, "inconsistent logical sector count")
    require(allocation_map_sector == 1, "unsupported allocation-map location")
    require(fat_sector == allocation_map_sector + 1 and fat_sector_count > 0, "unsupported FAT location")
    require(directory_header_sector == fat_sector + fat_sector_count, "unsupported directory-header location")
    require(directory_sector == directory_header_sector + 1, "unsupported directory location")
    require(bank_sector_bias > 0, "invalid sound-bank sector bias")
    require(superblock[0x28:0x36] == EMX2_CONFIGURATION, "unsupported EMX2 configuration profile")
    require(not any(superblock[0x36:0x1FE]), "nonzero reserved superblock bytes")
    checksum = struct.unpack_from("<H", superblock, 0x1FE)[0]
    calculated_checksum = sum(struct.unpack_from("<255H", superblock, 0)) & 0xFFFF
    require(checksum == calculated_checksum, "superblock checksum mismatch")

    def sector_slice(sector: int, count: int, context: str) -> bytes:
        start = sector * SECTOR_SIZE
        end = start + count * SECTOR_SIZE
        require(start >= 0 and end <= len(data), f"{context} lies outside image")
        return data[start:end]

    allocation_map = sector_slice(allocation_map_sector, 1, "allocation map")
    data_sector = struct.unpack_from("<I", allocation_map, 0)[0]
    require(data_sector == directory_sector + 1, "unsupported data-sector location")
    require(all(byte == 0x80 for byte in allocation_map[4:]), "invalid allocation-map fill")

    fat_raw = sector_slice(fat_sector, fat_sector_count, "FAT")
    fat_capacity = len(fat_raw) // 2
    require(fat_capacity >= max_cluster + 1, "FAT cannot address declared clusters")
    fat = list(struct.unpack_from(f"<{fat_capacity}H", fat_raw, 0))
    require(fat[0] == FAT_RESERVED, "FAT entry zero is not reserved")
    require(all(value == FAT_RESERVED for value in fat[max_cluster + 1 :]), "invalid FAT tail fill")
    require(
        all(value in (FAT_FREE, FAT_END) or 1 <= value <= max_cluster for value in fat[1 : max_cluster + 1]),
        "FAT contains an invalid cluster value",
    )

    directory_header = sector_slice(directory_header_sector, 1, "directory header")
    require(directory_header[:16] == b"Designed by S&M.", "invalid directory-header signature")
    require(struct.unpack_from("<H", directory_header, 16)[0] == 0x4000, "invalid directory load address")
    require(struct.unpack_from("<H", directory_header, 18)[0] == directory_sector, "directory pointer mismatch")
    require(directory_header[20:32] == b"\xff" * 12, "invalid directory-header marker")
    require(not any(directory_header[32:]), "nonzero directory-header padding")

    directory_raw = sector_slice(directory_sector, 1, "directory")
    entries: list[DirectoryEntry] = []
    reached_empty = False
    for index in range(DIRECTORY_ENTRY_COUNT):
        raw = directory_raw[index * DIRECTORY_ENTRY_SIZE : (index + 1) * DIRECTORY_ENTRY_SIZE]
        if not any(raw):
            reached_empty = True
            continue
        require(not reached_empty, "used directory entry follows an empty entry")
        name = decode_fixed_name(raw[:16], f"directory entry {index}")
        reserved, bank_number, start_cluster, cluster_count, used_sectors, final_bytes, flags, tail = struct.unpack_from(
            "<BBHHHHHI", raw, 16
        )
        require(name != "", f"directory entry {index}: empty name")
        require(reserved == 0 and tail == 0, f"directory entry {index}: invalid reserved fields")
        require(flags in (0x0000, 0x0080, 0x0081), f"directory entry {index}: unsupported flags 0x{flags:04x}")
        require(1 <= start_cluster <= max_cluster, f"directory entry {index}: invalid start cluster")
        require(1 <= cluster_count <= max_cluster, f"directory entry {index}: invalid cluster count")
        require(1 <= used_sectors <= cluster_sectors, f"directory entry {index}: invalid used-sector count")
        require(0 < final_bytes <= SECTOR_SIZE and final_bytes % 2 == 0, f"directory entry {index}: invalid final byte count")
        size = (cluster_count - 1) * cluster_size + (used_sectors - 1) * SECTOR_SIZE + final_bytes
        require(0 < size <= cluster_count * cluster_size, f"directory entry {index}: invalid extent size")
        entries.append(
            DirectoryEntry(
                index=index,
                name=name,
                bank_number=bank_number,
                start_cluster=start_cluster,
                cluster_count=cluster_count,
                used_sectors=used_sectors,
                final_sector_bytes=final_bytes,
                flags=flags,
                size=size,
            )
        )

    require(entries, "directory is empty")
    os_entry = entries[0]
    require(os_entry.name == "EMAX2 Software", "first directory entry is not EMAX2 Software")
    require(os_entry.bank_number == 0x78, "invalid operating-system directory tag")
    require(os_entry.flags & 0x0080, "operating-system directory entry is not live")
    require(os_entry.start_cluster == 1, "unsupported operating-system start cluster")
    require(os_entry.cluster_count == 4, "unsupported operating-system allocation length")
    live_bank_entries = [entry for entry in entries[1:] if entry.flags & 0x0080]
    deleted_entries = [entry for entry in entries[1:] if not entry.flags & 0x0080]
    bank_numbers = [entry.bank_number for entry in live_bank_entries]
    require(len(bank_numbers) == len(set(bank_numbers)), "live directory contains duplicate bank numbers")

    claimed: set[int] = set()
    for entry in [os_entry, *live_bank_entries]:
        current = entry.start_cluster
        chain: list[int] = []
        for chain_index in range(entry.cluster_count):
            require(current not in claimed, f"cluster {current} is cross-linked")
            require(current not in chain, f"directory entry {entry.index}: FAT cycle")
            chain.append(current)
            claimed.add(current)
            next_cluster = fat[current]
            if chain_index + 1 == entry.cluster_count:
                require(next_cluster == FAT_END, f"directory entry {entry.index}: chain does not end at declared length")
            else:
                require(1 <= next_cluster <= max_cluster, f"directory entry {entry.index}: premature FAT chain end")
                current = next_cluster
        entry.chain = chain
    allocated = {cluster for cluster in range(1, max_cluster + 1) if fat[cluster] != FAT_FREE}
    require(allocated == claimed, "FAT has allocated clusters not owned by the directory")

    os_first_cluster_offset = data_sector * SECTOR_SIZE
    operating_system, os_segments = read_chain(
        data, os_entry.chain, os_entry.size, os_first_cluster_offset, cluster_size, "operating system"
    )
    sound_first_cluster_offset = (directory_sector + bank_sector_bias) * SECTOR_SIZE
    require(
        sound_first_cluster_offset + max_cluster * cluster_size <= len(data),
        "image is shorter than its shifted sound-cluster space",
    )
    banks: list[Bank] = []
    for entry in live_bank_entries:
        raw, segments = read_chain(
            data,
            entry.chain,
            entry.size,
            sound_first_cluster_offset,
            cluster_size,
            f"bank {entry.bank_number}",
        )
        banks.append(parse_bank(entry, raw, segments))

    metadata_regions = [
        (0, SECTOR_SIZE, "superblock", "volume/superblock.bin"),
        (allocation_map_sector * SECTOR_SIZE, SECTOR_SIZE, "allocation-map", "volume/allocation-map.bin"),
        (fat_sector * SECTOR_SIZE, fat_sector_count * SECTOR_SIZE, "fat", "volume/fat.bin"),
        (directory_header_sector * SECTOR_SIZE, SECTOR_SIZE, "directory-header", "volume/directory-header.bin"),
        (directory_sector * SECTOR_SIZE, SECTOR_SIZE, "directory", "volume/directory.bin"),
    ]
    header = {
        "logical_sectors": logical_sectors,
        "directory_header_sector": directory_header_sector,
        "allocation_map_sector": allocation_map_sector,
        "directory_sector": directory_sector,
        "data_sector": data_sector,
        "bank_sector_bias": bank_sector_bias,
        "fat_sector": fat_sector,
        "fat_sector_count": fat_sector_count,
        "cluster_size_kib": cluster_size_kib,
        "cluster_size_bytes": cluster_size,
        "max_cluster": max_cluster,
        "superblock_checksum": checksum,
    }
    return ParsedImage(
        source=source,
        data=data,
        header=header,
        metadata_regions=metadata_regions,
        operating_system=operating_system,
        operating_system_entry=os_entry,
        operating_system_segments=os_segments,
        banks=banks,
        deleted_entries=deleted_entries,
    )


def make_wav(sample: Sample) -> bytes:
    import io

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample.sample_rate)
        wav.writeframes(sample.pcm)
    plain = buffer.getvalue()
    loop = sample.loop()
    if loop is None:
        return plain
    start, end = loop
    sample_period = 1_000_000_000 // sample.sample_rate
    smpl_data = struct.pack(
        "<15I",
        0,
        0,
        sample_period,
        60,
        0,
        0,
        0,
        1,
        0,
        0,
        0,
        start,
        end,
        0,
        0,
    )
    fmt_and_data = plain[12:]
    data_position = fmt_and_data.find(b"data")
    require(data_position >= 0, "internal WAV encoder did not produce a data chunk")
    chunks = fmt_and_data[:data_position] + b"smpl" + struct.pack("<I", len(smpl_data)) + smpl_data + fmt_and_data[data_position:]
    return b"RIFF" + struct.pack("<I", len(chunks) + 4) + b"WAVE" + chunks


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


class OutputWriter:
    def __init__(self, root: Path):
        self.root = root
        self.paths: list[str] = []

    def write(self, relative: str, data: bytes) -> None:
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True, mode=0o775)
        os.chmod(target.parent, 0o775)
        with target.open("wb") as handle:
            handle.write(data)
        os.chmod(target, 0o664)
        self.paths.append(relative)


def extraction_manifest(parsed: ParsedImage, bank_records: list[dict[str, Any]], files_written: int) -> dict[str, Any]:
    revision_match = re.search(rb"Emax II rev\s+[^\x00\r\n]{1,32}", parsed.operating_system, re.IGNORECASE)
    revision = revision_match.group(0).decode("ascii", "replace") if revision_match else None
    return {
        "format": "E-mu EMAX-II EMX2 SyQuest hard-disk image",
        "extractor": "emx2DiskImage.py",
        "source": {
            "name": parsed.source.name,
            "parent": parsed.source.parent.name,
            "path": str(parsed.source.resolve()),
            "bytes": len(parsed.data),
            "sectors": len(parsed.data) // SECTOR_SIZE,
            "sha256": sha256_bytes(parsed.data),
        },
        "volume": parsed.header,
        "operating_system": {
            "name": parsed.operating_system_entry.name,
            "bytes": len(parsed.operating_system),
            "sha256": sha256_bytes(parsed.operating_system),
            "revision_string": revision,
            "path": "operating-system/EMAX2 Software.emx",
        },
        "counts": {
            "banks": len(parsed.banks),
            "deleted_directory_entries": len(parsed.deleted_entries),
            "presets": sum(len(bank.presets) for bank in parsed.banks),
            "sample_allocations": sum(len(bank.samples) for bank in parsed.banks),
            "wav_samples": sum(sample.is_used for bank in parsed.banks for sample in bank.samples),
            "warnings": sum(len(bank.warnings) for bank in parsed.banks),
            "files_written": files_written,
        },
        "deleted_directory_entries": [
            {
                "directory_index": entry.index,
                "name": entry.name,
                "bank_number": entry.bank_number,
                "start_cluster": entry.start_cluster,
                "cluster_count": entry.cluster_count,
                "flags": f"0x{entry.flags:04x}",
            }
            for entry in parsed.deleted_entries
        ],
        "banks": bank_records,
    }


def extract(parsed: ParsedImage, output: Path, extract_all: bool = False) -> None:
    output = output.resolve()
    if output.exists():
        require(output.is_dir(), "output path exists and is not a directory")
        require(not any(output.iterdir()), "output directory already exists and is not empty")
    parent = output.parent
    require(parent.exists() and parent.is_dir(), "output parent directory does not exist")
    stage = Path(tempfile.mkdtemp(prefix=f".{output.name}.tmp-", dir=parent))
    os.chmod(stage, 0o775)
    writer = OutputWriter(stage)
    accounting_claims: list[dict[str, Any]] = []

    def claim(offset: int, length: int, kind: str, path: str, output_offset: int = 0) -> None:
        accounting_claims.append(
            {
                "source_offset": offset,
                "length": length,
                "kind": kind,
                "extracted_path": path,
                "extracted_offset": output_offset,
            }
        )

    def commit() -> None:
        for directory, _, _ in os.walk(stage):
            os.chmod(directory, 0o775)
        if output.exists():
            output.rmdir()
        os.replace(stage, output)
        os.chmod(output, 0o775)

    def emit_warnings() -> None:
        for bank in parsed.banks:
            for warning in bank.warnings:
                print(f"emx2DiskImage.py: warning: {warning}", file=sys.stderr)

    try:
        if not extract_all:
            for bank in parsed.banks:
                bank_name = clean_name(bank.entry.name, f"bank-{bank.entry.bank_number:02d}")
                prefix = f"{bank.entry.bank_number:02d} - {bank_name}"
                eb2 = bytearray(bank.raw)
                eb2[0] = 0xAD
                writer.write(f"{prefix}.eb2", bytes(eb2))
                for sample in bank.samples:
                    if sample.is_used:
                        writer.write(f"{prefix} - Sample {sample.number:03d}.wav", make_wav(sample))
            commit()
            emit_warnings()
            return

        for offset, length, kind, path in parsed.metadata_regions:
            writer.write(path, parsed.data[offset : offset + length])
            claim(offset, length, kind, path)

        os_path = "operating-system/EMAX2 Software.emx"
        writer.write(os_path, parsed.operating_system)
        for segment in parsed.operating_system_segments:
            claim(segment.source_offset, segment.length, "operating-system", os_path, segment.logical_offset)

        bank_records: list[dict[str, Any]] = []
        for bank in parsed.banks:
            bank_name = clean_name(bank.entry.name, f"bank-{bank.entry.bank_number:02d}")
            bank_root = f"banks/{bank.entry.bank_number:02d} - {bank_name}"
            raw_path = f"{bank_root}/{bank_name}.disk-bank.bin"
            eb2_path = f"{bank_root}/{bank_name}.eb2"
            metadata_path = f"{bank_root}/bank-metadata.bin"
            sequencer_path = f"{bank_root}/sequencer-data.bin" if bank.sequencer_data else None
            sequencer_payload_path = f"{bank_root}/sequencer-payload.bin" if bank.sequencer_data else None
            writer.write(raw_path, bank.raw)
            eb2 = bytearray(bank.raw)
            eb2[0] = 0xAD
            writer.write(eb2_path, bytes(eb2))
            writer.write(metadata_path, bank.raw[:BANK_HEADER_SIZE])
            if sequencer_path:
                writer.write(sequencer_path, bank.sequencer_data)
                writer.write(sequencer_payload_path, bank.sequencer_payload)
            for segment in bank.segments:
                claim(segment.source_offset, segment.length, "sound-bank", raw_path, segment.logical_offset)

            sample_records: list[dict[str, Any]] = []
            for sample in bank.samples:
                allocation_path = f"{bank_root}/sample-allocations/sample-{sample.number:03d}.bin"
                writer.write(allocation_path, sample.allocation)
                wav_path: str | None = None
                if sample.is_used:
                    wav_path = f"{bank_root}/samples/sample-{sample.number:03d}.wav"
                    writer.write(wav_path, make_wav(sample))
                sample_records.append(
                    {
                        "number": sample.number,
                        "descriptor_slot": sample.descriptor_slot,
                        "used": sample.is_used,
                        "identifier": f"0x{sample.identifier:08x}",
                        "start_word": sample.start_word,
                        "end_word": sample.end_word,
                        "pcm_frames": sample.frame_count,
                        "sample_rate": sample.sample_rate,
                        "rate_code": sample.rate_code,
                        "format_word": f"0x{sample.format_word:08x}",
                        "loop_flags": sample.loop_flags,
                        "loop_status": sample.loop_status,
                        "sustain_loop_words": [sample.sustain_start_word, sample.sustain_end_word],
                        "release_loop_words": [sample.release_start_word, sample.release_end_word],
                        "wav_loop_frames": list(sample.loop()) if sample.is_used and sample.loop() else None,
                        "pcm_sha256": sha256_bytes(sample.pcm),
                        "prefix_sha256": sha256_bytes(sample.prefix),
                        "trailer_sha256": sha256_bytes(sample.trailer),
                        "allocation_path": allocation_path,
                        "wav_path": wav_path,
                    }
                )

            preset_records: list[dict[str, Any]] = []
            for preset in bank.presets:
                native_region_path: str | None = None
                if preset.region_end_bank_offset is not None:
                    native_region_path = (
                        f"{bank_root}/presets/preset-{preset.number:03d} - "
                        f"{clean_name(preset.name, 'unnamed')}.preset-region.bin"
                    )
                    writer.write(
                        native_region_path,
                        bank.raw[preset.bank_offset : preset.region_end_bank_offset],
                    )
                preset_records.append({
                    "number": preset.number,
                    "name": preset.name,
                    "bank_offset": preset.bank_offset,
                    "region_end_bank_offset": preset.region_end_bank_offset,
                    "native_region_path": native_region_path,
                })
            bank_json_path = f"{bank_root}/bank.json"
            bank_record = {
                "number": bank.entry.bank_number,
                "name": bank.entry.name,
                "bytes": len(bank.raw),
                "sha256": sha256_bytes(bank.raw),
                "start_cluster": bank.entry.start_cluster,
                "cluster_count": bank.entry.cluster_count,
                "cluster_chain": bank.entry.chain,
                "directory_flags": f"0x{bank.entry.flags:04x}",
                "preset_count": len(bank.presets),
                "sample_allocation_count": len(bank.samples),
                "wav_sample_count": sum(sample.is_used for sample in bank.samples),
                "sample_memory_end_offset": bank.sample_data_end,
                "sequencer_data_bytes": len(bank.sequencer_data),
                "sequencer_payload_bytes": len(bank.sequencer_payload),
                "raw_path": raw_path,
                "eb2_path": eb2_path,
                "metadata_path": metadata_path,
                "sequencer_path": sequencer_path,
                "sequencer_payload_path": sequencer_payload_path,
                "bank_json_path": bank_json_path,
                "warnings": bank.warnings,
                "presets": preset_records,
                "samples": sample_records,
            }
            writer.write(bank_json_path, json_bytes(bank_record))
            bank_records.append(bank_record)

        accounting_claims.sort(key=lambda item: item["source_offset"])
        previous_end = 0
        residual_number = 0
        full_accounting: list[dict[str, Any]] = []
        for item in accounting_claims:
            offset = item["source_offset"]
            require(offset >= previous_end, f"internal byte-accounting overlap at input offset {offset}")
            if offset > previous_end:
                residual_number += 1
                length = offset - previous_end
                residual_path = f"residual/region-{residual_number:03d}-offset-{previous_end:08x}-length-{length:08x}.bin"
                writer.write(residual_path, parsed.data[previous_end:offset])
                full_accounting.append(
                    {
                        "source_offset": previous_end,
                        "length": length,
                        "kind": "unallocated-or-allocation-slack",
                        "extracted_path": residual_path,
                        "extracted_offset": 0,
                    }
                )
            full_accounting.append(item)
            previous_end = offset + item["length"]
        if previous_end < len(parsed.data):
            residual_number += 1
            length = len(parsed.data) - previous_end
            residual_path = f"residual/region-{residual_number:03d}-offset-{previous_end:08x}-length-{length:08x}.bin"
            writer.write(residual_path, parsed.data[previous_end:])
            full_accounting.append(
                {
                    "source_offset": previous_end,
                    "length": length,
                    "kind": "unallocated-or-allocation-slack",
                    "extracted_path": residual_path,
                    "extracted_offset": 0,
                }
            )
            previous_end = len(parsed.data)
        require(previous_end == len(parsed.data), "internal byte-accounting length mismatch")
        require(sum(item["length"] for item in full_accounting) == len(parsed.data), "not every source byte is accounted")
        accounting = {
            "source_bytes": len(parsed.data),
            "accounted_bytes": sum(item["length"] for item in full_accounting),
            "regions": full_accounting,
        }
        writer.write("byte-accounting.json", json_bytes(accounting))

        files_written = len(writer.paths) + 1
        manifest = extraction_manifest(parsed, bank_records, files_written)
        writer.write("manifest.json", json_bytes(manifest))
        commit()
        emit_warnings()
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def relative_url(from_file: Path, target: Path) -> str:
    return quote(os.path.relpath(target, from_file.parent).replace(os.sep, "/"), safe="/'()")


def generate_report(input_root: Path, output_root: Path, report_path: Path) -> None:
    input_root = input_root.resolve()
    output_root = output_root.resolve()
    report_path = report_path.resolve()
    manifests: dict[str, tuple[dict[str, Any], Path]] = {}
    for path in output_root.rglob("manifest.json") if output_root.exists() else []:
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
            manifests[manifest["source"]["sha256"]] = (manifest, path.parent)
        except (OSError, ValueError, KeyError, TypeError):
            continue

    groups: dict[str, list[tuple[Path, str, tuple[dict[str, Any], Path] | None]]] = {}
    for source in sorted(input_root.rglob("*.img")):
        try:
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
        except OSError:
            digest = ""
        relative_parent_path = source.parent.relative_to(input_root)
        relative_parent = input_root.name if relative_parent_path == Path(".") else relative_parent_path.as_posix()
        groups.setdefault(relative_parent, []).append((source, digest, manifests.get(digest)))

    sections: list[str] = []
    total_images = 0
    total_banks = 0
    total_wavs = 0
    total_presets = 0
    for group_name, samples in groups.items():
        sample_html: list[str] = []
        for source, digest, found in samples:
            total_images += 1
            if found is None:
                sample_html.append(
                    f'<article class="image skipped"><h3>{html.escape(source.name)}</h3>'
                    '<span class="status bad">Skipped</span>'
                    '<p>No successful extraction manifest matching this input was found.</p></article>'
                )
                continue
            manifest, extraction_root = found
            counts = manifest["counts"]
            total_banks += counts["banks"]
            total_wavs += counts["wav_samples"]
            total_presets += counts["presets"]
            bank_html: list[str] = []
            for bank in manifest["banks"]:
                samples_html: list[str] = []
                for sample in bank["samples"]:
                    if not sample["used"] or not sample["wav_path"]:
                        continue
                    wav_target = extraction_root / sample["wav_path"]
                    wav_url = relative_url(report_path, wav_target)
                    if sample.get("loop_status") == "invalid":
                        loop_text = "invalid loop omitted"
                    else:
                        loop_text = "loop" if sample["wav_loop_frames"] else "one-shot"
                    samples_html.append(
                        '<div class="sample">'
                        f'<a href="{wav_url}" target="_blank" rel="noopener">Sample {sample["number"]:03d}</a>'
                        f'<span>{sample["sample_rate"]:,} Hz · {sample["pcm_frames"]:,} frames · {loop_text}</span>'
                        f'<audio controls preload="none" src="{wav_url}"></audio></div>'
                    )
                eb2_url = relative_url(report_path, extraction_root / bank["eb2_path"])
                raw_url = relative_url(report_path, extraction_root / bank["raw_path"])
                bank_html.append(
                    '<details class="bank"><summary>'
                    f'<strong>{bank["number"]:02d} · {html.escape(bank["name"])}</strong>'
                    f'<span>{bank["preset_count"]} presets · {bank["wav_sample_count"]} WAVs · {bank["bytes"]:,} bytes</span>'
                    '</summary><div class="bank-links">'
                    f'<a href="{eb2_url}">EB2 bank</a><a href="{raw_url}">Exact disk bank</a></div>'
                    f'<div class="samples">{"".join(samples_html)}</div></details>'
                )
            manifest_url = relative_url(report_path, extraction_root / "manifest.json")
            accounting_url = relative_url(report_path, extraction_root / "byte-accounting.json")
            revision = manifest["operating_system"].get("revision_string") or "revision string not present"
            sample_html.append(
                '<article class="image"><div class="image-heading"><div>'
                f'<h3>{html.escape(source.name)}</h3><span class="status good">Extracted</span></div>'
                f'<div class="metrics"><b>{counts["banks"]}</b> banks <b>{counts["presets"]}</b> presets '
                f'<b>{counts["wav_samples"]}</b> WAVs <b>{counts["files_written"]}</b> output files</div></div>'
                '<div class="facts">'
                f'<span>{manifest["source"]["bytes"]:,} bytes</span><span>{manifest["source"]["sectors"]:,} sectors</span>'
                f'<span>{html.escape(revision)}</span><span>SHA-256 {digest[:16]}…</span>'
                f'<a href="{manifest_url}">Manifest</a><a href="{accounting_url}">Byte accounting</a></div>'
                f'{"".join(bank_html)}</article>'
            )
        sections.append(f'<section><h2>{html.escape(group_name)}</h2>{"".join(sample_html)}</section>')

    document = f'''<!doctype html>
<!-- Vibe coded by Codex -->
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>EMAX-II Disk Image Extraction Report</title>
<style>
:root {{ color-scheme: dark; --bg:#101214; --panel:#181c20; --panel2:#20262b; --line:#394149; --text:#edf1f3; --muted:#aab4bb; --accent:#53c7a2; --link:#70b7ff; --bad:#ff7a7a; }}
* {{ box-sizing:border-box; }} body {{ margin:0; background:var(--bg); color:var(--text); font:14px/1.45 system-ui,sans-serif; letter-spacing:0; }}
header,main {{ width:min(1500px,calc(100% - 32px)); margin:auto; }} header {{ padding:28px 0 18px; border-bottom:1px solid var(--line); }}
h1 {{ margin:0 0 10px; font-size:clamp(24px,3vw,38px); }} h2 {{ margin:28px 0 12px; font-size:20px; }} h3 {{ margin:0; font-size:16px; overflow-wrap:anywhere; }}
.totals,.facts,.bank-links {{ display:flex; flex-wrap:wrap; gap:8px 18px; color:var(--muted); }} .totals b,.metrics b {{ color:var(--text); }}
.image {{ margin:0 0 18px; border:1px solid var(--line); background:var(--panel); border-radius:6px; overflow:hidden; }}
.image-heading {{ display:flex; justify-content:space-between; align-items:flex-start; gap:18px; padding:16px; }} .metrics {{ color:var(--muted); white-space:nowrap; }}
.status {{ display:inline-block; margin-top:7px; font-size:12px; font-weight:700; text-transform:uppercase; }} .good {{ color:var(--accent); }} .bad {{ color:var(--bad); }}
.facts {{ padding:10px 16px; background:var(--panel2); border-top:1px solid var(--line); border-bottom:1px solid var(--line); }} a {{ color:var(--link); }}
.bank {{ border-top:1px solid var(--line); }} .bank summary {{ display:flex; justify-content:space-between; gap:16px; cursor:pointer; padding:12px 16px; }} .bank summary span {{ color:var(--muted); }}
.bank-links {{ padding:0 16px 12px; }} .samples {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(230px,1fr)); gap:1px; background:var(--line); border-top:1px solid var(--line); }}
.sample {{ min-width:0; padding:10px; background:var(--panel2); }} .sample>a,.sample>span {{ display:block; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }} .sample>span {{ margin:3px 0 8px; color:var(--muted); font-size:12px; }} audio {{ display:block; width:100%; height:32px; }}
.skipped {{ padding:16px; }} @media(max-width:700px) {{ .image-heading,.bank summary {{ display:block; }} .metrics,.bank summary span {{ display:block; margin-top:8px; white-space:normal; }} }}
</style></head><body><header><h1>EMAX-II Disk Image Extraction Report</h1>
<div class="totals"><span><b>{total_images}</b> images</span><span><b>{total_banks}</b> banks</span><span><b>{total_presets}</b> presets</span><span><b>{total_wavs}</b> playable samples</span></div></header>
<main>{''.join(sections)}</main></body></html>'''
    report_path.parent.mkdir(parents=True, exist_ok=True, mode=0o775)
    report_path.write_text(document, encoding="utf-8")
    os.chmod(report_path, 0o664)


def usage() -> str:
    return (
        "Usage: emx2DiskImage.py [--all] <inputFile> <outputDir>\n"
        "       emx2DiskImage.py --report <inputDir> <outputRoot> <report.html>"
    )


def main(argv: list[str]) -> int:
    if len(argv) == 5 and argv[1] == "--report":
        try:
            generate_report(Path(argv[2]), Path(argv[3]), Path(argv[4]))
        except (OSError, FormatError) as exc:
            print(f"emx2DiskImage.py: {exc}", file=sys.stderr)
            return 1
        return 0
    extract_all = len(argv) == 4 and argv[1] == "--all"
    if not extract_all and len(argv) != 3:
        print(usage(), file=sys.stderr)
        return 2
    source_index = 2 if extract_all else 1
    source = Path(argv[source_index])
    output = Path(argv[source_index + 1])
    try:
        parsed = parse_image(source)
        extract(parsed, output, extract_all=extract_all)
    except (OSError, FormatError, struct.error, ValueError) as exc:
        print(f"emx2DiskImage.py: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

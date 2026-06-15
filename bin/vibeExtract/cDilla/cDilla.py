#!/usr/bin/env python3
# Vibe coded by Codex
"""Extractor for the verified C-Dilla CD-Secure/CD-Compress file subset."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


MAGIC = bytes.fromhex("47 f4 62 af c2 51 05 f4")
MAX_RECORD_BYTES = 0x4FF8
LCG_MULTIPLIER = 0xF2A534E5
LCG_INCREMENT = 0x361962E9
SELECTOR_0012_SBOX = bytes.fromhex(
    "ab 62 1e 58 21 ac fc 25 53 b3 9a f8 1d 3e dc f5 "
    "96 da 3d ea bd 8a 7d 9b 92 e5 35 1c 57 67 02 e4 "
    "c8 ca a2 5e bc 46 ef ae c2 d4 24 d6 70 aa 4b 38 "
    "e0 29 66 37 07 56 fb 0f e6 6a 51 c3 d8 d0 4e b2 "
    "44 f1 83 b6 16 fe 45 2c d5 78 36 eb cb 60 a6 3f "
    "1f a7 0a 48 d2 2a f4 b9 be ee d7 7a 0d 80 49 6b "
    "08 c5 de 41 c7 20 88 61 8f a9 ff 64 5c bb 2d f7 "
    "10 5a e8 14 ec ed 52 ba c6 59 e1 cc 76 c9 04 d3 "
    "90 74 63 0e 54 f9 22 f2 1a 27 6e dd 05 94 87 e3 "
    "81 85 95 50 b7 7e a1 9f cf 79 ad a4 6d 69 4a e2 "
    "c0 40 4d 8b b5 28 9e c1 fd 23 55 75 93 39 e7 30 "
    "89 5b f6 97 7f 9d 3a a5 8d 82 47 11 cd 7b 01 3b "
    "00 b8 bf ce 15 b0 d1 9c 31 43 c4 42 98 73 af 26 "
    "b4 1b 65 03 7c 34 a0 84 33 4f b1 0b f3 6f 2f 12 "
    "2b 13 f0 e9 2e 32 09 17 8e 72 06 18 5d 99 71 df "
    "91 5f 86 68 fa a3 8c 19 0c 77 4c a8 6c db 3c d9"
)

# Product masks are licence/runtime values used by verified selector 0x0012
# sample families. The byte transform is fully implemented; deriving these
# masks from arbitrary C-Dilla licence state is not yet fully specified.
SELECTOR_0012_PRODUCT_MASKS: dict[bytes, int] = {
    bytes.fromhex("00 c0 56 bd 03 02 00 80 00 00"): 0x5BC41A78,
    bytes.fromhex("00 20 0a b0 03 02 00 80 01 00"): 0xD6020BE0,
    bytes.fromhex("00 20 0a b0 0b 02 00 80 01 00"): 0xD6020BE0,
    bytes.fromhex("00 b0 4c bd 03 02 00 80 00 00"): 0xD49F22A3,
    bytes.fromhex("00 70 75 bd 03 02 00 80 00 00"): 0xCE1871F6,
    bytes.fromhex("00 90 4c bd 03 02 00 80 00 00"): 0xB8EEA68E,
    bytes.fromhex("00 f0 0a b0 03 00 00 80 00 00"): 0xFFA3BF09,
    bytes.fromhex("00 a0 4c bd 03 02 00 80 00 00"): 0x46C6A9B8,
    bytes.fromhex("00 10 41 bd 03 02 00 80 00 00"): 0x2C9E5893,
    bytes.fromhex("00 d0 4c bd 03 02 00 80 00 00"): 0xF04E85E8,
    bytes.fromhex("00 80 4c bd 03 02 00 80 00 00"): 0x2B16A833,
    bytes.fromhex("00 c0 40 bd 03 02 00 80 00 00"): 0x07E8CAC9,
    bytes.fromhex("00 90 75 bd 03 02 00 80 00 00"): 0xE9CFC63B,
    bytes.fromhex("00 60 1d b0 03 00 00 80 00 00"): 0xD7E70B30,
    bytes.fromhex("00 c0 0c b0 0b 00 00 80 00 00"): 0x8DA9F55B,
    bytes.fromhex("00 70 e0 b1 03 02 00 80 00 00"): 0xFE4B07F6,
    bytes.fromhex("00 80 6d bd 03 02 00 80 00 00"): 0xEC26FD0A,
    bytes.fromhex("00 10 0d b0 0b 00 00 80 00 00"): 0x9DA3C125,
    bytes.fromhex("00 90 1c b0 03 00 00 80 00 00"): 0xE16F6E82,
    bytes.fromhex("00 80 14 b0 03 00 00 80 00 00"): 0x4116EFCA,
}

DCL_MAX_BITS = 13
DCL_LITLEN = (
    11, 124, 8, 7, 28, 7, 188, 13, 76, 4, 10, 8, 12, 10, 12, 10,
    8, 23, 8, 9, 7, 6, 7, 8, 7, 6, 55, 8, 23, 24, 12, 11,
    7, 9, 11, 12, 6, 7, 22, 5, 7, 24, 6, 11, 9, 6,
    7, 22, 7, 11, 38, 7, 9, 8, 25, 11, 8, 11, 9, 12,
    8, 12, 5, 38, 5, 38, 5, 11, 7, 5, 6, 21, 6, 10,
    53, 8, 7, 24, 10, 27, 44, 253, 253, 253, 252, 252, 252, 13,
    12, 45, 12, 45, 12, 61, 12, 45, 44, 173,
)
DCL_LENLEN = (2, 35, 36, 53, 38, 23)
DCL_DISTLEN = (2, 20, 53, 230, 247, 151, 248)
DCL_LENGTH_BASE = (3, 2, 4, 5, 6, 7, 8, 9, 10, 12, 16, 24, 40, 72, 136, 264)
DCL_LENGTH_EXTRA = (0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8)


class CDilaError(Exception):
    """Base class for expected extractor errors."""


class UnsupportedFormatError(CDilaError):
    """Raised when the input is not a fully implemented C-Dilla file."""


@dataclass(frozen=True)
class MetadataRecord:
    offset: int
    key: int
    length: int
    next_offset: int
    encrypted: bytes
    decrypted: bytes


@dataclass(frozen=True)
class TransformDescriptor:
    raw: bytes
    selector: int
    key32: int
    key16: int
    prefix_words: tuple[int, int, int, int, int]
    suffix_word: int


@dataclass(frozen=True)
class CompressionDescriptor:
    raw: bytes
    tag5: bytes | None
    block_size: int
    flags: int
    marker: int
    table_offset: int
    table_size: int
    block_offsets: tuple[int, ...]


@dataclass(frozen=True)
class ParsedCDila:
    input_size: int
    metadata_records: tuple[MetadataRecord, ...]
    unknown_tag1_word: int
    payload_offset: int
    logical_size: int
    transform: TransformDescriptor | None
    compression: CompressionDescriptor | None
    output_data: bytes


@dataclass(frozen=True)
class ExtractedMember:
    """An extracted member prepared in memory before any filesystem writes."""

    path: PurePosixPath
    data: bytes


def le16(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 2], "little")


def le32(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 4], "little")


class DCLBitReader:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.offset = 0
        self.bitbuf = 0
        self.bitcnt = 0

    def bits(self, count: int) -> int:
        while self.bitcnt < count:
            if self.offset >= len(self.data):
                raise UnsupportedFormatError("DCL stream ended before an end code")
            self.bitbuf |= self.data[self.offset] << self.bitcnt
            self.offset += 1
            self.bitcnt += 8

        value = self.bitbuf & ((1 << count) - 1)
        self.bitbuf >>= count
        self.bitcnt -= count
        return value


def lcg_next(state: int) -> int:
    return (state * LCG_MULTIPLIER + LCG_INCREMENT) & 0xFFFFFFFF


def make_permutation(seed: int, length: int) -> list[int]:
    if length == 0:
        return []

    state = seed & 0xFFFFFFFF
    result: list[int] = []
    used: set[int] = set()
    random_bytes = b""

    for index in range(length):
        if index % 4 == 0:
            state = lcg_next(state)
            random_bytes = state.to_bytes(4, "little")

        candidate = random_bytes[index % 4] % length
        step = 1 if index & 1 else -1
        while candidate in used:
            candidate += step
            if candidate >= length:
                candidate = 0
            elif candidate < 0:
                candidate = length - 1

        used.add(candidate)
        result.append(candidate)

    return result


def swap_permutation_pairs(buffer: bytearray, start: int, length: int, permutation: list[int]) -> None:
    index = 0
    while length > 1:
        left = permutation[index]
        right = permutation[index + 1]
        buffer[start + left], buffer[start + right] = buffer[start + right], buffer[start + left]
        index += 2
        length -= 2


def metadata_transform(data: bytes, key: int) -> bytes:
    """Apply the self-inverse metadata record transform from CDILLA05.DLL."""

    buffer = bytearray(data)
    length = len(buffer)
    block_size = (key % 31) + 33

    position = 0
    permutation = make_permutation(key, block_size)
    for _ in range(length // block_size):
        swap_permutation_pairs(buffer, position, block_size, permutation)
        position += block_size

    remainder = length % block_size
    swap_permutation_pairs(buffer, position, remainder, make_permutation(key, remainder))

    state = key & 0xFFFFFFFF
    position = 0
    for _ in range(length // 4):
        state = lcg_next(state)
        mask = state.to_bytes(4, "little")
        for byte_index in range(4):
            buffer[position + byte_index] ^= mask[byte_index]
        position += 4

    for _ in range(length % 4):
        state = lcg_next(state)
        buffer[position] ^= state & 0xFF
        position += 1

    return bytes(buffer)


def construct_dcl_huffman(repeats: tuple[int, ...]) -> tuple[tuple[int, ...], tuple[int, ...]]:
    lengths: list[int] = []
    for repeat in repeats:
        lengths.extend([repeat & 0x0F] * ((repeat >> 4) + 1))

    counts = [0] * (DCL_MAX_BITS + 1)
    for length in lengths:
        if length > DCL_MAX_BITS:
            raise UnsupportedFormatError("DCL Huffman code length is out of range")
        counts[length] += 1

    left = 1
    for length in range(1, DCL_MAX_BITS + 1):
        left <<= 1
        left -= counts[length]
        if left < 0:
            raise UnsupportedFormatError("DCL Huffman table is over-subscribed")

    offsets = [0] * (DCL_MAX_BITS + 1)
    for length in range(1, DCL_MAX_BITS):
        offsets[length + 1] = offsets[length] + counts[length]

    symbols = [0] * sum(counts[1:])
    next_offsets = offsets[:]
    for symbol, length in enumerate(lengths):
        if length:
            symbols[next_offsets[length]] = symbol
            next_offsets[length] += 1

    return tuple(counts), tuple(symbols)


# Altered Python port of Mark Adler's zlib contrib/blast PKWARE DCL decoder.
DCL_LITCODE = construct_dcl_huffman(DCL_LITLEN)
DCL_LENCODE = construct_dcl_huffman(DCL_LENLEN)
DCL_DISTCODE = construct_dcl_huffman(DCL_DISTLEN)


def dcl_decode_symbol(reader: DCLBitReader, table: tuple[tuple[int, ...], tuple[int, ...]]) -> int:
    counts, symbols = table
    code = 0
    first = 0
    index = 0

    for length in range(1, DCL_MAX_BITS + 1):
        code |= reader.bits(1) ^ 1
        count = counts[length]
        if code < first + count:
            return symbols[index + (code - first)]

        index += count
        first = (first + count) << 1
        code <<= 1

    raise UnsupportedFormatError("DCL stream contains an invalid Huffman code")


def dcl_copy_from_window(output: bytearray, distance: int, length: int) -> None:
    if distance <= 0 or distance > len(output):
        raise UnsupportedFormatError("DCL stream has a copy distance before the output start")

    source_start = len(output) - distance
    if distance >= length:
        output.extend(output[source_start : source_start + length])
        return

    pattern = bytes(output[source_start:])
    if not pattern:
        raise UnsupportedFormatError("DCL stream has an empty copy source")
    repeat_count, remainder = divmod(length, len(pattern))
    output.extend(pattern * repeat_count)
    output.extend(pattern[:remainder])


def dcl_explode_block(data: bytes, expected_size: int) -> bytes:
    reader = DCLBitReader(data)
    coded_literals = reader.bits(8)
    dictionary_bits = reader.bits(8)
    if coded_literals > 1:
        raise UnsupportedFormatError("DCL block has an invalid literal coding flag")
    if dictionary_bits < 4 or dictionary_bits > 6:
        raise UnsupportedFormatError("DCL block has an invalid dictionary size")

    output = bytearray()
    while True:
        if reader.bits(1):
            symbol = dcl_decode_symbol(reader, DCL_LENCODE)
            length = DCL_LENGTH_BASE[symbol] + reader.bits(DCL_LENGTH_EXTRA[symbol])
            if length == 519:
                break

            distance_bits = 2 if length == 2 else dictionary_bits
            distance = dcl_decode_symbol(reader, DCL_DISTCODE) << distance_bits
            distance += reader.bits(distance_bits)
            distance += 1
            dcl_copy_from_window(output, distance, length)
        else:
            symbol = dcl_decode_symbol(reader, DCL_LITCODE) if coded_literals else reader.bits(8)
            output.append(symbol)

        if len(output) > expected_size:
            raise UnsupportedFormatError("DCL block produced more bytes than expected")

    if len(output) != expected_size:
        raise UnsupportedFormatError("DCL block produced fewer bytes than expected")
    if reader.offset != len(data):
        raise UnsupportedFormatError("DCL block did not consume every compressed byte")
    return bytes(output)


def parse_tags(record_data: bytes) -> list[tuple[int, bytes]]:
    tags: list[tuple[int, bytes]] = []
    position = 0

    while position < len(record_data):
        if position + 4 > len(record_data):
            raise UnsupportedFormatError("metadata tag header is truncated")

        tag_type = le16(record_data, position)
        tag_length = le16(record_data, position + 2)
        position += 4

        if position + tag_length > len(record_data):
            raise UnsupportedFormatError("metadata tag payload is truncated")

        tag_value = record_data[position : position + tag_length]
        position += tag_length
        tags.append((tag_type, tag_value))

        if tag_type == 0:
            if any(record_data[position:]):
                raise UnsupportedFormatError("non-zero bytes follow terminal metadata tag")
            break

    if position != len(record_data):
        raise UnsupportedFormatError("metadata record contains unparsed bytes")

    return tags


def parse_metadata_records(data: bytes) -> tuple[tuple[MetadataRecord, ...], list[tuple[int, bytes]], int]:
    records: list[MetadataRecord] = []
    tags: list[tuple[int, bytes]] = []
    seen_offsets: set[int] = set()
    offset = 8
    metadata_end = 0

    while offset:
        if offset in seen_offsets:
            raise UnsupportedFormatError("metadata record chain contains a loop")
        seen_offsets.add(offset)

        if offset < 8 or offset + 8 > len(data):
            raise UnsupportedFormatError("metadata record offset is outside the file")

        key = le16(data, offset)
        length = le16(data, offset + 2)
        next_offset = le32(data, offset + 4)

        if length > MAX_RECORD_BYTES:
            raise UnsupportedFormatError("metadata record is larger than the verified runtime buffer")

        record_end = offset + 8 + length
        if record_end > len(data):
            raise UnsupportedFormatError("metadata record extends beyond end of file")

        encrypted = data[offset + 8 : record_end]
        decrypted = metadata_transform(encrypted, key) if key else encrypted
        record = MetadataRecord(offset, key, length, next_offset, encrypted, decrypted)
        records.append(record)
        tags.extend(parse_tags(decrypted))
        metadata_end = max(metadata_end, record_end)
        offset = next_offset

    return tuple(records), tags, metadata_end


def unique_tag(tags: list[tuple[int, bytes]], tag_type: int) -> bytes | None:
    values = [value for current_type, value in tags if current_type == tag_type]
    if len(values) > 1:
        raise UnsupportedFormatError(f"metadata tag {tag_type} appears more than once")
    return values[0] if values else None


def parse_transform(raw_tag: bytes | None) -> TransformDescriptor | None:
    if raw_tag is None:
        return None

    if len(raw_tag) > 18:
        raise UnsupportedFormatError("metadata tag 4 is longer than the runtime accepts")

    padded = raw_tag.ljust(18, b"\x00")
    return TransformDescriptor(
        raw=raw_tag,
        selector=le16(padded, 14),
        key32=le32(padded, 10),
        key16=le16(padded, 10),
        prefix_words=(
            le16(padded, 0),
            le16(padded, 2),
            le16(padded, 4),
            le16(padded, 6),
            le16(padded, 8),
        ),
        suffix_word=le16(padded, 16),
    )


def parse_compression(
    raw_tag: bytes | None,
    raw_tag5: bytes | None,
    data: bytes,
    metadata_end: int,
    payload_offset: int,
    logical_size: int,
) -> CompressionDescriptor | None:
    if raw_tag is None:
        if raw_tag5 is not None:
            raise UnsupportedFormatError("metadata tag 5 is present without compression tag 6")
        return None

    if len(raw_tag) != 14:
        raise UnsupportedFormatError("metadata tag 6 length is not 14 bytes")

    block_size = le16(raw_tag, 0)
    flags = le16(raw_tag, 2)
    marker = le16(raw_tag, 4)
    table_offset = le32(raw_tag, 6)
    table_size = le32(raw_tag, 10)

    if block_size == 0:
        raise UnsupportedFormatError("compressed block size is zero")
    if flags not in {0, 1}:
        raise UnsupportedFormatError("metadata tag 6 compression flags are not implemented")
    if table_offset != metadata_end:
        raise UnsupportedFormatError("metadata tag 6 table offset does not match metadata end")
    if table_size != payload_offset - metadata_end:
        raise UnsupportedFormatError("metadata tag 6 table size does not match payload offset")

    if flags == 0 and raw_tag5 is not None:
        raise UnsupportedFormatError("metadata tag 5 is present for a tag 6 mode that does not use it")
    if flags == 1:
        if raw_tag5 is None:
            raise UnsupportedFormatError("metadata tag 6 requires metadata tag 5")
        if len(raw_tag5) != 4:
            raise UnsupportedFormatError("metadata tag 5 length is not 4 bytes")
        if le16(raw_tag5, 2) != marker:
            raise UnsupportedFormatError("metadata tag 5 does not match tag 6 marker")

    block_count = (logical_size + block_size - 1) // block_size
    if table_size != (block_count + 1) * 4:
        raise UnsupportedFormatError("compressed block table length does not match logical size")

    table = data[metadata_end:payload_offset]
    block_offsets = tuple(le32(table, index * 4) for index in range(block_count + 1))
    physical_payload_size = len(data) - payload_offset
    if block_offsets[0] != 0:
        raise UnsupportedFormatError("compressed block table does not start at zero")
    if block_offsets[-1] != physical_payload_size:
        raise UnsupportedFormatError("compressed block table does not end at physical payload size")
    if any(left > right for left, right in zip(block_offsets, block_offsets[1:])):
        raise UnsupportedFormatError("compressed block table offsets are not monotonic")

    return CompressionDescriptor(
        raw=raw_tag,
        tag5=raw_tag5,
        block_size=block_size,
        flags=flags,
        marker=marker,
        table_offset=table_offset,
        table_size=table_size,
        block_offsets=block_offsets,
    )


def transform_selector_0010(payload: bytes, seed: int, logical_offset: int = 0) -> bytes:
    state = seed & 0xFFFFFFFF
    table = bytearray()
    for _ in range(32):
        state = lcg_next(state)
        table.extend(state.to_bytes(4, "little"))

    output = bytearray(payload)
    for index, value in enumerate(output):
        position = logical_offset + index
        output[index] = value ^ ((position >> 7) & 0xFF) ^ table[position & 0x7F]

    return bytes(output)


def transform_selector_0011(payload: bytes, key: int, logical_offset: int = 0) -> bytes:
    output = bytearray(payload)
    position = 0

    if logical_offset & 1 and output:
        output[position] ^= (key >> 8) & 0xFF
        position += 1

    while position + 1 < len(output):
        word = le16(output, position) ^ key
        output[position : position + 2] = word.to_bytes(2, "little")
        position += 2

    if position < len(output):
        output[position] ^= key & 0xFF

    return bytes(output)


def selector_0012_seed(transform: TransformDescriptor) -> int:
    if not (transform.prefix_words[3] & 0x8000):
        return transform.key32

    prefix = transform.raw[:10].ljust(10, b"\x00")
    product_mask = SELECTOR_0012_PRODUCT_MASKS.get(prefix)
    if product_mask is None:
        raise UnsupportedFormatError(
            "payload transform selector 0x0012 uses an unknown licence-bound "
            f"descriptor prefix: {prefix.hex()}"
        )

    return transform.key32 ^ product_mask


def transform_selector_0012(payload: bytes, seed: int, logical_offset: int = 0) -> bytes:
    state = seed & 0xFFFFFFFF
    table = bytearray()
    for _ in range(128):
        state = lcg_next(state)
        table.append((state >> 24) & 0xFF)

    output = bytearray(payload)
    for index, value in enumerate(output):
        position = logical_offset + index
        output[index] = (
            value
            ^ SELECTOR_0012_SBOX[table[position % 123] ^ table[position % 127]]
            ^ table[position & 0x7F]
        )

    return bytes(output)


def apply_payload_transform(
    payload: bytes,
    transform: TransformDescriptor | None,
    logical_offset: int = 0,
) -> bytes:
    if transform is None or transform.selector == 0xFFFF:
        return payload

    if transform.selector == 0x0010:
        return transform_selector_0010(payload, transform.key32, logical_offset)

    if transform.selector == 0x0011:
        return transform_selector_0011(payload, transform.key16, logical_offset)

    if transform.selector == 0x0012:
        return transform_selector_0012(payload, selector_0012_seed(transform), logical_offset)

    raise UnsupportedFormatError(
        f"payload transform selector 0x{transform.selector:04x} is not implemented"
    )


def decode_compressed_payload(
    physical_payload: bytes,
    transform: TransformDescriptor | None,
    compression: CompressionDescriptor,
    logical_size: int,
) -> bytes:
    output = bytearray()

    for block_index, (start, end) in enumerate(
        zip(compression.block_offsets, compression.block_offsets[1:])
    ):
        expected_size = min(compression.block_size, logical_size - len(output))
        if expected_size <= 0:
            raise UnsupportedFormatError("compressed block table contains extra blocks")
        if end <= start:
            raise UnsupportedFormatError("compressed block table contains an empty block")

        encrypted_block = physical_payload[start:end]
        transformed_block = apply_payload_transform(encrypted_block, transform, start)
        try:
            block_data = dcl_explode_block(transformed_block, expected_size)
        except UnsupportedFormatError as exc:
            raise UnsupportedFormatError(f"DCL block {block_index} failed: {exc}") from exc
        output.extend(block_data)

    if len(output) != logical_size:
        raise UnsupportedFormatError("compressed payload did not produce the logical size")
    return bytes(output)


def parse_cdila(data: bytes) -> ParsedCDila:
    if len(data) < 16:
        raise UnsupportedFormatError("file is too small for a C-Dilla header")
    if data[:8] != MAGIC:
        raise UnsupportedFormatError("missing C-Dilla magic bytes")

    records, tags, metadata_end = parse_metadata_records(data)
    tag1 = unique_tag(tags, 1)
    if tag1 is None:
        raise UnsupportedFormatError("required metadata tag 1 is missing")
    if len(tag1) != 10:
        raise UnsupportedFormatError("metadata tag 1 length is not 10 bytes")

    tag4 = unique_tag(tags, 4)
    transform = parse_transform(tag4)

    unsupported_tags = sorted({tag_type for tag_type, _ in tags if tag_type not in {0, 1, 4, 5, 6}})
    if unsupported_tags:
        tag_list = ", ".join(str(tag_type) for tag_type in unsupported_tags)
        raise UnsupportedFormatError(f"metadata tag(s) not implemented: {tag_list}")

    unknown_tag1_word = le16(tag1, 0)
    payload_offset = le32(tag1, 2)
    logical_size = le32(tag1, 6)
    tag5 = unique_tag(tags, 5)
    tag6 = unique_tag(tags, 6)

    if payload_offset < metadata_end:
        raise UnsupportedFormatError("payload starts inside metadata records")

    compression = parse_compression(tag6, tag5, data, metadata_end, payload_offset, logical_size)
    payload = data[payload_offset:]
    if compression is None:
        if any(data[metadata_end:payload_offset]):
            raise UnsupportedFormatError("non-zero padding before payload is not implemented")
        if payload_offset + logical_size != len(data):
            raise UnsupportedFormatError("physical payload size does not match logical size")
        output_data = apply_payload_transform(payload, transform)
    else:
        output_data = decode_compressed_payload(payload, transform, compression, logical_size)

    return ParsedCDila(
        input_size=len(data),
        metadata_records=records,
        unknown_tag1_word=unknown_tag1_word,
        payload_offset=payload_offset,
        logical_size=logical_size,
        transform=transform,
        compression=compression,
        output_data=output_data,
    )


def output_member_name(input_file: Path) -> PurePosixPath:
    name = input_file.name
    if not name:
        raise CDilaError("input file has no usable basename")
    return PurePosixPath(name)


def extract_members(input_file: Path) -> tuple[ParsedCDila, list[ExtractedMember]]:
    data = input_file.read_bytes()
    parsed = parse_cdila(data)
    return parsed, [ExtractedMember(output_member_name(input_file), parsed.output_data)]


def validate_member_path(path: PurePosixPath) -> None:
    """Reject paths that could escape the extraction directory."""

    if path.is_absolute() or not path.parts:
        raise CDilaError(f"unsafe archive member path: {path}")
    if any(part in ("", ".", "..") for part in path.parts):
        raise CDilaError(f"unsafe archive member path: {path}")


def chmod_tree(path: Path) -> None:
    for root, dirs, files in os.walk(path):
        os.chmod(root, 0o775)
        for dirname in dirs:
            os.chmod(Path(root, dirname), 0o775)
        for filename in files:
            os.chmod(Path(root, filename), 0o664)


def write_members_atomically(output_dir: Path, members: list[ExtractedMember]) -> None:
    """Write prepared members only after parsing has fully succeeded."""

    if output_dir.exists() and any(output_dir.iterdir()):
        raise CDilaError(f"output directory already exists and is not empty: {output_dir}")

    parent = output_dir.parent if output_dir.parent != Path("") else Path(".")
    parent.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.tmp-", dir=parent))

    try:
        for member in members:
            validate_member_path(member.path)
            target = temp_dir.joinpath(*member.path.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(member.data)
            os.chmod(target, 0o664)

        if output_dir.exists():
            output_dir.rmdir()
        temp_dir.rename(output_dir)
        chmod_tree(output_dir)
    except Exception:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise


def extract(input_file: Path, output_dir: Path) -> int:
    if not input_file.is_file():
        raise CDilaError(f"input file does not exist or is not a regular file: {input_file}")

    parsed, members = extract_members(input_file)
    del parsed
    write_members_atomically(output_dir, members)
    return len(members)


def identify_bytes(data: bytes) -> str:
    if data.startswith((b"GIF87a", b"GIF89a")):
        return "GIF"
    if data.startswith(b"BM"):
        return "BMP"
    if data.startswith((b"FWS", b"CWS", b"ZWS")):
        return "SWF"
    if data.startswith(b"{\\rtf"):
        return "RTF"
    if data.startswith(b"MZ"):
        return "PE/EXE"
    if data.startswith(b"8BPS"):
        return "Photoshop"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "PNG"
    if data[:32] and all(byte in b"\r\n\t" or 32 <= byte < 127 for byte in data[:32]):
        return "ASCII text"
    return "data"


def parsed_summary(parsed: ParsedCDila) -> dict[str, object]:
    selector = None if parsed.transform is None else parsed.transform.selector
    return {
        "input_size": parsed.input_size,
        "record_count": len(parsed.metadata_records),
        "payload_offset": parsed.payload_offset,
        "logical_size": parsed.logical_size,
        "selector": selector,
        "output_sha256": hashlib.sha256(parsed.output_data).hexdigest(),
        "output_type": identify_bytes(parsed.output_data),
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cDilla.py",
        description="Extract a supported C-Dilla protected file into an output directory.",
    )
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputDir", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    try:
        count = extract(args.inputFile, args.outputDir)
    except CDilaError as exc:
        print(f"cDilla.py: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"cDilla.py: filesystem error: {exc}", file=sys.stderr)
        return 1

    print(f"extracted {count} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

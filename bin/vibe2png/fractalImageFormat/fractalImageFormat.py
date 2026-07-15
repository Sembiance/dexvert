#!/usr/bin/env python3
# Vibe coded by Codex
"""Strict, self-contained FIF-family image/video to PNG or animated GIF."""

from __future__ import annotations

import binascii
import base64
import os
from dataclasses import dataclass, replace
from pathlib import Path
import struct
import sys
import tempfile
import zlib


HEADER_SIZE = 67
MAX_FILE_SIZE = 0x7FFFFFFF
GENERATION2_VENDOR_STAMP = b"VS##IFX000VP20"
FTC_VIDEO_GRAY_SIGNATURE = b"FTC\x00\x01\x01\x01\x02"
FTC_VIDEO_COLOR_SIGNATURE = b"FTC\x00\x01\x01\x02\x02"
FTC_VIDEO_SIGNATURES = (FTC_VIDEO_GRAY_SIGNATURE, FTC_VIDEO_COLOR_SIGNATURE)
FJF_VIDEO_SIGNATURE = b"FTC\x00\x02\x02\x02\x02"

# P.OEM Video 2.0 represents the 61 useful motion offsets as indices into this
# width-independent coordinate table.  Codes 61..63 address padding rather
# than defined offsets in the reference decoder and are rejected.
VIDEO_MOTION_DELTAS = (
    (0, 0),
    (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0),
    (-1, 1), (0, 1), (1, 1),
    (-2, -2), (-1, -2), (0, -2), (1, -2), (2, -2),
    (-2, -1), (2, -1), (-2, 0), (2, 0), (-2, 1), (2, 1),
    (-2, 2), (-1, 2), (0, 2), (1, 2), (2, 2),
    (-1, -3), (0, -3), (1, -3), (-3, -1), (3, -1),
    (-3, 0), (3, 0), (-3, 1), (3, 1),
    (-1, 3), (0, 3), (1, 3),
    (4, 0), (-4, 1), (4, 1), (-3, 2), (3, 2),
    (-3, 3), (-2, 3), (2, 3), (3, 3),
    (-1, 4), (0, 4), (1, 4),
    (-4, 0), (4, -1), (-4, -1), (3, -2), (-3, -2),
    (3, -3), (2, -3), (-2, -3), (-3, -3),
    (1, -4), (0, -4), (-1, -4),
)

# Within each padded 4-by-4 range-block tile, records use this permutation.
Y_IN_TILE = (0, 0, 1, 1, 0, 0, 1, 1, 2, 2, 3, 3, 2, 2, 3, 3)
X_IN_TILE = (0, 1, 0, 1, 2, 3, 2, 3, 0, 1, 0, 1, 2, 3, 2, 3)


class FormatError(ValueError):
    """The input is malformed or is not the exact FTC profile implemented here."""


class Bits:
    """Little-endian/least-significant-bit-first payload reader."""

    def __init__(self, data: bytes):
        self.data = data
        self.position = 0

    @property
    def length(self) -> int:
        return len(self.data) * 8

    def read(self, count: int) -> int:
        remaining = self.length - self.position
        if count < 0 or count > remaining:
            raise FormatError(
                f"truncated at payload bit {self.position}: "
                f"need {count} bits but only {max(remaining, 0)} remain"
            )
        result = 0
        for shift in range(count):
            result |= (
                (self.data[self.position >> 3] >> (self.position & 7)) & 1
            ) << shift
            self.position += 1
        return result

    def read_run(self) -> int:
        ones = 0
        while self.read(1):
            ones += 1
            if ones > 31:
                raise FormatError("run-length prefix exceeds 31 one bits")
        if ones == 0:
            return 1
        return (1 << (ones - 1)) + self.read(ones - 1) + 1

    def require_zero(self, count: int, description: str) -> None:
        if count and self.read(count) != 0:
            raise FormatError(f"nonzero {description}")


def _u16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def _u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def _s16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<h", data, offset)[0]


def validate_header(data: bytes) -> tuple[int, int, int, bytes]:
    """Validate every header byte and return width, height, domain step, payload."""
    if len(data) < HEADER_SIZE:
        raise FormatError(f"file is shorter than the {HEADER_SIZE}-byte FTC header")
    if len(data) > MAX_FILE_SIZE:
        raise FormatError("file exceeds the FTC profile's signed 32-bit size limit")
    if data[:4] != b"FTC\x00":
        raise FormatError("signature is not FTC\\0")

    width = _u16(data, 8)
    height = _u16(data, 10)
    if width == 0 or height == 0 or width % 8 or height % 8:
        raise FormatError("canvas dimensions must be positive multiples of eight")

    header_size = _u32(data, 16)
    payload_size = _u32(data, 20)
    if header_size != HEADER_SIZE:
        raise FormatError(f"unsupported header size {header_size}; expected {HEADER_SIZE}")
    if payload_size == 0:
        raise FormatError("compressed payload is empty")
    if header_size + payload_size != len(data):
        raise FormatError(
            "declared header and payload lengths do not equal the physical file length"
        )
    domain_step = _u16(data, 48)
    if domain_step not in (2, 8):
        raise FormatError(
            f"unsupported domain-grid step {domain_step}; expected 2 or 8"
        )

    expected = bytearray(
        b"FTC\x00"
        b"\x01\x01\x02\x01"
        b"\x00\x00\x00\x00"
        b"\x18\x00\x01\x00"
        b"\x43\x00\x00\x00"
        b"\x00\x00\x00\x00"
        b"\x00\x00\x00\x00"
        b"\x01\x01\x10\x00"
        b"\x00\x00\x00\x00"
        b"\x00\x00\x00\x00"
        b"\x00\x00\x00\x00"
        b"\x04\x00\x04\x00"
        b"\x02\x00\x03\x07"
        b"\x04\x00\x00\x01"
        b"\x00\x06\x00\x08"
        b"\x00\x00\x00\x00"
        b"\x00\x00\x00"
    )
    struct.pack_into("<H", expected, 8, width)
    struct.pack_into("<H", expected, 10, height)
    struct.pack_into("<I", expected, 20, payload_size)
    struct.pack_into("<H", expected, 36, width)
    struct.pack_into("<H", expected, 38, height)
    struct.pack_into("<H", expected, 48, domain_step)
    expected[61] = 1 if domain_step == 8 else 0
    if data[:HEADER_SIZE] != expected:
        mismatch = next(
            offset
            for offset, (actual, wanted) in enumerate(zip(data, expected))
            if actual != wanted
        )
        raise FormatError(
            f"unsupported header byte at 0x{mismatch:02x}: "
            f"0x{data[mismatch]:02x} (expected 0x{expected[mismatch]:02x})"
        )
    return width, height, domain_step, data[HEADER_SIZE:]


def _reject_missing_early_template(
    data: bytes, directories: tuple[Path, ...]
) -> None:
    """Validate the early 112-byte FTC template profile and name its dependency."""
    if len(data) < 112:
        raise FormatError("file is shorter than its 112-byte FTC header")
    width = _u16(data, 8)
    height = _u16(data, 10)
    payload_size = _u32(data, 20)
    if (
        data[:8] != b"FTC\x00\x01\x01\x02\x01"
        or _u16(data, 12) != 24
        or _u16(data, 14) != 1
        or _u32(data, 16) != 112
        or payload_size == 0
        or 112 + payload_size != len(data)
        or _u32(data, 24) != 0
        or data[28:32] != b"\x01\x01\x3d\x00"
        or _u16(data, 32) != 0
        or _u16(data, 34) != 0
        or data[36:40] != data[8:12]
        or data[40:44] != b"\x16\x00\x01\x08"
        or data[60:64] != data[8:12]
        or data[64:66] != b"\x17\x00"
        or _u32(data, 66) == 0
        or data[84:88] != data[8:12]
        or data[88:112] != bytes.fromhex(
            "000800080002000307040000010006000800000000000000"
        )
        or width == 0 or height == 0
    ):
        raise FormatError("invalid early FTC external-template header")
    name_field = data[44:60]
    terminator = name_field.find(0)
    if terminator <= 0 or any(name_field[terminator + 1:]):
        raise FormatError("invalid early FTC external-template filename")
    filename = name_field[:terminator].decode("cp437")
    folded = filename.casefold()
    found = False
    for directory in directories:
        try:
            if any(
                path.is_file() and path.name.casefold() == folded
                for path in directory.iterdir()
            ):
                found = True
                break
        except OSError:
            continue
    if not found:
        raise FormatError(
            f"early FTC image requires external transform raster {filename!r}, "
            "but no matching file was found"
        )
    raise FormatError(
        "early 112-byte FTC external-transform reconstruction is not implemented"
    )


def _c_div(numerator: int, denominator: int) -> int:
    """C89 signed division: truncate toward zero."""
    return abs(numerator) // denominator * (-1 if numerator < 0 else 1)


def _quantization_table() -> tuple[int, ...]:
    values: list[int] = []
    current = -2048 << 4
    for _ in range(128):
        adjusted = max(current, -0x6000)
        adjusted = adjusted - 5 if adjusted < 0 else adjusted + 6
        values.append(_c_div(adjusted, 12) + 0x800)
        current += 32 << 4
    return tuple(values)


QUANTIZATION = _quantization_table()


def _affine_table() -> bytes:
    table = bytearray(8192)
    accumulator = 32
    for index in range(2048, 8192):
        table[index] = min(accumulator >> 6, 255)
        accumulator += 6
    return bytes(table)


AFFINE = _affine_table()


@dataclass
class Record:
    kind: int
    quantization_index: int
    quantized: int
    domain_index: int
    domain_x: int
    domain_y: int
    symmetry: int
    # The affine lookup ramp is selected by the quantizer's numeric type.
    slope: int = 6
    quantizer_selector: int = 0


def _tile_order(width_cells: int, height_cells: int) -> tuple[list[int], int, int]:
    padded_width = ((width_cells + 3) // 4) * 4
    padded_height = ((height_cells + 3) // 4) * 4
    order: list[int] = []
    for tile_y in range(0, padded_height, 4):
        for tile_x in range(0, padded_width, 4):
            for delta_y, delta_x in zip(Y_IN_TILE, X_IN_TILE):
                y = tile_y + delta_y
                x = tile_x + delta_x
                order.append(
                    y * width_cells + x
                    if y < height_cells and x < width_cells
                    else -1
                )
    return order, padded_width, padded_height


def _mark_runs(
    bits: Bits,
    candidates: list[int],
    labels: bytearray,
    mark: int,
    description: str,
) -> list[int]:
    state = bits.read(1)
    cursor = 0
    remaining = len(candidates)
    survivors: list[int] = []
    while remaining:
        run = bits.read_run()
        if run > remaining:
            raise FormatError(
                f"{description} run of {run} exceeds {remaining} remaining entries"
            )
        group = candidates[cursor:cursor + run]
        if state == 0:
            for ordinal in group:
                labels[ordinal] |= mark
        else:
            survivors.extend(group)
        cursor += run
        remaining -= run
        state ^= 1
    return survivors


SYMMETRY_DY = (0, 0, 0, 0, 1, 1, -1, -1)
SYMMETRY_DX = (1, -1, 1, -1, 0, 0, 0, 0)
SYMMETRY_ROW_X = (0, 0, 0, 0, 1, -1, 1, -1)
SYMMETRY_COL_Y = (1, 1, -1, -1, 0, 0, 0, 0)
START_X_4 = (0, 3, 0, 3, 0, 3, 0, 3)
START_Y_4 = (0, 0, 3, 3, 0, 0, 3, 3)
START_X_2 = (0, 1, 0, 1, 0, 1, 0, 1)
START_Y_2 = (0, 0, 1, 1, 0, 0, 1, 1)


def _grouped_record(base: Record, ordinal: int, group_size: int) -> Record:
    in_group = ordinal & (group_size * group_size - 1)
    row = Y_IN_TILE[in_group]
    column = X_IN_TILE[in_group]
    symmetry = base.symmetry
    if group_size == 4:
        start_x = START_X_4[symmetry]
        start_y = START_Y_4[symmetry]
    else:
        start_x = START_X_2[symmetry]
        start_y = START_Y_2[symmetry]
    delta_x = (
        start_x
        + SYMMETRY_ROW_X[symmetry] * row
        + SYMMETRY_DX[symmetry] * column
    ) * 8
    delta_y = (
        start_y
        + SYMMETRY_COL_Y[symmetry] * row
        + SYMMETRY_DY[symmetry] * column
    ) * 8
    return replace(base, domain_x=base.domain_x + delta_x,
                   domain_y=base.domain_y + delta_y)


def _read_record(bits: Bits, domain_width: int, domain_height: int,
                 domain_step: int, kind: int) -> Record:
    quantization_index = bits.read(7)
    domain_count = domain_width * domain_height
    domain_bits = (domain_count - 1).bit_length()
    domain_index = bits.read(domain_bits)
    if domain_index >= domain_count:
        raise FormatError(
            f"domain index {domain_index} is outside a {domain_count}-cell domain grid"
        )
    symmetry = bits.read(3)
    return Record(
        kind,
        quantization_index,
        QUANTIZATION[quantization_index],
        domain_index,
        domain_index % domain_width * domain_step,
        domain_index // domain_width * domain_step,
        symmetry,
    )


def _parse_plane(bits: Bits, width: int, height: int, domain_step: int,
                 domain_height_prefix: int = 0) -> list[Record]:
    range_width = width // 4
    range_height = height // 4
    domain_width = (width + domain_step - 1) // domain_step
    domain_height = (
        domain_height_prefix + (height + domain_step - 1) // domain_step
    )
    order, padded_width, padded_height = _tile_order(range_width, range_height)
    candidates = [ordinal for ordinal, logical in enumerate(order) if logical >= 0]
    labels = bytearray(padded_width * padded_height)

    survivors = _mark_runs(bits, candidates, labels, 2, "class-2 mask")
    if survivors:
        survivors = _mark_runs(bits, survivors, labels, 6, "reserved-class mask")
    if survivors:
        survivors = _mark_runs(bits, survivors, labels, 1, "class-1 mask")
    if survivors:
        # State zero marks class 1; state one leaves class 0.
        _mark_runs(bits, survivors, labels, 1, "class-0/1 mask")

    if any(labels[ordinal] == 6 for ordinal in candidates):
        raise FormatError("reserved transform class 6 is not valid in this FTC profile")

    records: list[Record | None] = [None] * (range_width * range_height)
    last_group = -1
    base: Record | None = None
    for ordinal, label in enumerate(labels):
        if label != 2:
            continue
        group = ordinal >> 4
        if group != last_group:
            base = _read_record(bits, domain_width, domain_height, domain_step, 2)
            last_group = group
        logical = order[ordinal]
        if logical >= 0:
            assert base is not None
            records[logical] = _grouped_record(base, ordinal, 4)

    last_group = -1
    for ordinal, label in enumerate(labels):
        if label != 1:
            continue
        group = ordinal >> 2
        if group != last_group:
            base = _read_record(bits, domain_width, domain_height, domain_step, 1)
            last_group = group
        logical = order[ordinal]
        if logical >= 0:
            assert base is not None
            records[logical] = _grouped_record(base, ordinal, 2)

    for ordinal, label in enumerate(labels):
        if label == 0:
            logical = order[ordinal]
            if logical >= 0:
                records[logical] = _read_record(
                    bits, domain_width, domain_height, domain_step, 0
                )

    if any(record is None for record in records):
        raise FormatError("one or more range blocks did not receive a transform record")
    return [record for record in records if record is not None]


def parse_payload(payload: bytes, width: int, height: int,
                  domain_step: int) -> list[Record]:
    bits = Bits(payload)
    try:
        primary = _parse_plane(bits, width, height, domain_step)
    except FormatError as error:
        raise FormatError(f"primary transform plane: {error}") from error
    bits.require_zero((-bits.position) & 7, "primary-plane byte-alignment padding")
    try:
        primary_domain_height = (height + domain_step - 1) // domain_step
        secondary = _parse_plane(
            bits, width, height // 2, domain_step, primary_domain_height
        )
    except FormatError as error:
        raise FormatError(f"secondary transform plane: {error}") from error

    trailing = bits.length - bits.position
    if trailing > 7:
        raise FormatError(f"payload has {trailing} unexplained trailing bits")
    bits.require_zero(trailing, "terminal payload padding")
    return primary + secondary


@dataclass(frozen=True)
class Quantizer:
    kind: int
    bits: int
    step: int
    base: int
    values: tuple[int, ...]


@dataclass(frozen=True)
class Region:
    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True)
class TransformTemplateReference:
    """One external FTT transform-template reference from an FTC directory."""

    width: int
    height: int
    identifier: int
    filename: str


@dataclass(frozen=True)
class FractalTransformTemplate:
    """Validated FTT 1.1 source-fragment raster."""

    width: int
    height: int
    identifier: int
    pixels: bytes


@dataclass(frozen=True)
class ModernFTC:
    codec_profile: int
    transform_major: int
    transform_minor: int
    output_width: int
    output_height: int
    origin_x: int
    origin_y: int
    color: bool
    euv_color: bool
    range_size: int
    domain_step: int
    symmetry_bits: int
    quantizers: tuple[Quantizer, ...]
    template_step: int
    template_symmetry_bits: int
    template_quantizer: Quantizer
    regions: tuple[Region, ...]
    directory_budget: int
    directory_plane_code: int
    directory_workspace: int
    transform_templates: tuple[TransformTemplateReference, ...]
    payload_segments: tuple[bytes, ...]
    descriptor_tail: bytes
    encoder_statistics: bytes
    auxiliary_palette: tuple[tuple[int, int, int], ...]
    arithmetic_deltas: tuple[int, ...]
    attached_type: str | None
    attached_metadata: bytes
    attached_data: bytes
    container_trailer: bytes


def _parse_palette(data: bytes) -> tuple[tuple[int, int, int], ...]:
    """Parse the optional counted three-component container palette."""
    if not data:
        return ()
    if len(data) < 2:
        raise FormatError("truncated FTC auxiliary palette")
    count = _u16(data, 0)
    if len(data) != 2 + count * 3:
        raise FormatError("FTC auxiliary-palette length is inconsistent")
    return tuple(
        (data[offset], data[offset + 1], data[offset + 2])
        for offset in range(2, len(data), 3)
    )


def _validate_wave(data: bytes) -> None:
    """Validate and account for every byte of a RIFF/WAVE attachment."""
    if len(data) < 12 or data[:4] != b"RIFF" or data[8:12] != b"WAVE":
        raise FormatError("FTC attachment is not a RIFF/WAVE stream")
    if _u32(data, 4) != len(data) - 8:
        raise FormatError("RIFF/WAVE attachment length is inconsistent")
    position = 12
    found_format = False
    found_samples = False
    while position < len(data):
        if position + 8 > len(data):
            raise FormatError("truncated RIFF/WAVE chunk header")
        kind = data[position:position + 4]
        size = _u32(data, position + 4)
        position += 8
        if position + size > len(data):
            raise FormatError("truncated RIFF/WAVE chunk payload")
        payload = data[position:position + size]
        if kind == b"fmt ":
            if found_format or size < 16:
                raise FormatError("invalid RIFF/WAVE format chunk")
            encoding, channels, rate, byte_rate, alignment, bits = struct.unpack_from(
                "<HHIIHH", payload
            )
            if (encoding != 1 or channels == 0 or rate == 0 or
                    alignment == 0 or bits == 0 or bits & 7 or
                    alignment != channels * (bits // 8) or
                    byte_rate != rate * alignment):
                raise FormatError("unsupported or inconsistent PCM WAVE format")
            found_format = True
        elif kind == b"data":
            if found_samples:
                raise FormatError("RIFF/WAVE attachment has multiple data chunks")
            found_samples = True
        position += size
        if size & 1:
            if position >= len(data) or data[position] != 0:
                raise FormatError("invalid RIFF/WAVE chunk pad byte")
            position += 1
    if position != len(data) or not found_format or not found_samples:
        raise FormatError("incomplete RIFF/WAVE attachment")


def _parse_attachment(prefix: bytes, data: bytes) -> tuple[str, bytes, bytes]:
    """Parse the FTC 106-byte associated-data descriptor and its payload."""
    if len(prefix) != 106:
        raise FormatError("FTC associated-data descriptor is not 106 bytes")
    if _u32(prefix, 0) != 1 or _u16(prefix, 4) != 1:
        raise FormatError("unsupported FTC associated-data descriptor version/type")
    type_field = prefix[6:38]
    terminator = type_field.find(0)
    if terminator < 0 or any(type_field[terminator + 1:]):
        raise FormatError("invalid FTC associated-data type string")
    try:
        attached_type = type_field[:terminator].decode("ascii")
    except UnicodeDecodeError as error:
        raise FormatError("non-ASCII FTC associated-data type string") from error
    if attached_type != "Image Carousel image/sound file":
        raise FormatError(f"unsupported FTC associated-data type {attached_type!r}")
    if _u32(prefix, 86) != len(data) or any(prefix[90:106]):
        raise FormatError("inconsistent FTC associated-data length/reserved bytes")
    _validate_wave(data)
    return attached_type, prefix[38:86], data


def _make_quantizer(kind: int, bits: int, step: int, base: int,
                    version: int) -> Quantizer:
    if kind not in (4, 5, 6, 7, 8):
        raise FormatError(f"unsupported affine quantizer type {kind}")
    if not 1 <= bits <= 12:
        raise FormatError(f"invalid quantizer width {bits}")
    if step == 0:
        raise FormatError("quantizer step is zero")

    if version < 32:
        current = base * 8 - 2048
        increment = step * 8
    else:
        current = base - 2048
        increment = step

    values: list[int] = []
    if kind == 4:
        current *= 2
        increment *= 2
        for _ in range(1 << bits):
            values.append(max(current, -2048) + 2048)
            current += increment
    elif kind in (5, 6, 7):
        denominator = {5: 10, 6: 12, 7: 14}[kind]
        lower = {5: -0x5000, 6: -0x6000, 7: -0x7000}[kind]
        negative_round = {5: 4, 6: 5, 7: 6}[kind]
        positive_round = {5: 5, 6: 6, 7: 7}[kind]
        current <<= 4
        increment <<= 4
        for _ in range(1 << bits):
            adjusted = max(current, lower)
            adjusted += positive_round if adjusted >= 0 else -negative_round
            values.append(_c_div(adjusted, denominator) + 2048)
            current += increment
    else:
        for _ in range(1 << bits):
            values.append(max(current, -2048) + 2048)
            current += increment

    if any(not 0 <= value < 8192 for value in values):
        raise FormatError("quantizer generates an affine index outside 0..8191")
    return Quantizer(kind, bits, step, base, tuple(values))


def _make_template_quantizer(bits: int, step: int, base: int) -> Quantizer:
    """Build the FTT transform's signed brightness-offset table."""
    if not 1 <= bits <= 12:
        raise FormatError(f"invalid FTT quantizer width {bits}")
    if step == 0:
        raise FormatError("FTT quantizer step is zero")

    current = base - 0x100
    values: list[int] = []
    for _ in range(1 << bits):
        # The native table stores a biased clamp-table index.  Removing its
        # 0x2000 bias yields the signed offset applied to an FTT source byte.
        values.append(max(current, -0x200) - 0x2000)
        current += step
    return Quantizer(8, bits, step, base, tuple(values))


def _parse_modern_ftc(data: bytes) -> ModernFTC:
    """Parse and validate an FTC 3.x profile-1 or profile-2 container."""
    if len(data) < 48:
        raise FormatError("file is shorter than the FTC 3.x fixed header")
    if data[:4] != b"FTC\x00":
        raise FormatError("signature is not FTC\\0")
    if data[5] != 3 or data[4] not in (1, 2, 3, 4):
        raise FormatError("unsupported FTC 3.x outer-header generation")

    color_code = _u16(data, 6)
    depth = _u16(data, 12)
    if color_code == 0x0101 and depth == 8:
        color = False
        euv_color = False
    elif color_code in (0x0102, 0x0104) and depth == 24:
        color = True
        euv_color = color_code == 0x0104
    else:
        raise FormatError(
            f"unsupported FTC color/depth combination 0x{color_code:04x}/{depth}"
        )
    codec_profile = _u16(data, 14)
    if codec_profile not in (1, 2):
        raise FormatError(f"unsupported FTC transform codec profile {codec_profile}")

    main_size = _u16(data, 16)
    auxiliary_size = _u16(data, 18)
    payload_size = _u32(data, 20)
    secondary_size = _u32(data, 24)
    if main_size < 48 or main_size + auxiliary_size > len(data):
        raise FormatError("invalid FTC header lengths")
    # Outer generation 2 predates the associated-data wrapper used by later
    # containers.  Its secondary-size field counts a literal encoder stamp at
    # EOF.  Generations 3 and 4 instead count only the RIFF/WAVE payload and
    # place a 106-byte associated-data descriptor before it.
    if data[4] in (1, 2):
        trailing_size = secondary_size
    else:
        trailing_size = 106 + secondary_size if secondary_size else 0
    if main_size + auxiliary_size + payload_size + trailing_size != len(data):
        raise FormatError("FTC header and payload lengths do not equal the file length")

    transform_major = data[28]
    transform_minor = data[29]
    version = transform_major * 10 + transform_minor
    if version not in (31, 32, 33):
        raise FormatError(
            f"unsupported profile-1 transform version {transform_major}.{transform_minor}"
        )
    if _u16(data, 32) != 0 or _u16(data, 34) != 0:
        raise FormatError("nonzero FTC image origin is not supported")
    output_width = _u16(data, 36)
    output_height = _u16(data, 38)
    stored_width = _u16(data, 40)
    stored_height = _u16(data, 42)
    if not output_width or not output_height:
        raise FormatError("FTC image dimensions are zero")
    if stored_width != output_width or stored_height != output_height:
        raise FormatError("FTC stored and original dimensions disagree")

    extension_size = _u16(data, 44)
    position = 46 + extension_size
    if position + 2 > main_size:
        raise FormatError("truncated FTC transform-header extension")
    if extension_size and any(data[46:position]):
        raise FormatError("unsupported nonempty FTC transform-header extension")
    region_size = _u16(data, position)
    position += 2
    if _u16(data, 30) != region_size + 20:
        raise FormatError("inconsistent FTC transform-header length")
    if position + region_size > main_size:
        raise FormatError("truncated FTC region directory")
    directory = data[position:position + region_size]
    position += region_size
    if len(directory) < 15:
        raise FormatError("FTC region directory is too short")
    directory_budget = _u32(directory, 0)
    directory_plane_code = _u32(directory, 4)
    if directory[8] != 0:
        raise FormatError("nonzero FTC region-directory reserved byte")
    directory_workspace = _u32(directory, 9)
    if not directory_budget or not directory_plane_code or not directory_workspace:
        raise FormatError("FTC region-directory encoder limits are zero")
    region_count = directory[13] or _u32(directory, 9)
    if region_count == 0:
        raise FormatError("FTC region directory contains no regions")
    template_cursor = 14 + region_count * 8
    if template_cursor >= len(directory):
        raise FormatError("FTC region directory omits its FTT-reference count")
    template_count = directory[template_cursor]
    template_cursor += 1
    transform_templates: list[TransformTemplateReference] = []
    for template_index in range(template_count):
        if template_cursor + 9 > len(directory):
            raise FormatError(
                f"truncated FTC FTT reference {template_index}"
            )
        template_width = _u16(directory, template_cursor)
        template_height = _u16(directory, template_cursor + 2)
        template_identifier = _u32(directory, template_cursor + 4)
        filename_length = directory[template_cursor + 8]
        template_cursor += 9
        if not template_width or not template_height:
            raise FormatError("FTC FTT reference has zero dimensions")
        if not filename_length or template_cursor + filename_length > len(directory):
            raise FormatError("FTC FTT reference has an invalid filename length")
        filename_bytes = directory[
            template_cursor:template_cursor + filename_length
        ]
        template_cursor += filename_length
        # The field is a DOS/Windows locale byte string, not declared Unicode.
        # Early writers used a NUL-padded fixed allocation while later writers
        # stored only the occupied bytes under the same length field.
        terminator = filename_bytes.find(0)
        if terminator >= 0:
            if not terminator or any(filename_bytes[terminator + 1:]):
                raise FormatError("FTC FTT reference has invalid filename padding")
            filename_bytes = filename_bytes[:terminator]
        # CP437 gives every stored byte a stable round-trip representation;
        # path separators and the required extension are invariant ASCII bytes.
        filename = filename_bytes.decode("cp437")
        if filename_bytes[-4:].lower() != b".ftt":
            raise FormatError("FTC FTT reference has an invalid filename")
        transform_templates.append(TransformTemplateReference(
            template_width, template_height, template_identifier, filename
        ))
    if template_cursor != len(directory):
        raise FormatError("bytes remain after the FTC FTT-reference list")
    regions: list[Region] = []
    for index in range(region_count):
        x, y, width, height = struct.unpack_from("<HHHH", directory, 14 + index * 8)
        if not width or not height or (x | y | width | height) & 7:
            raise FormatError("FTC regions must be nonempty and eight-pixel aligned")
        regions.append(Region(x, y, width, height))

    descriptor = position
    if descriptor + 20 > main_size:
        raise FormatError("truncated FTC transform descriptor")
    range_size = _u16(data, descriptor)
    domain_size = _u16(data, descriptor + 2)
    domain_step = _u16(data, descriptor + 4)
    symmetry_bits = data[descriptor + 6]
    if (range_size, domain_size, domain_step, symmetry_bits) not in (
        (4, 4, 2, 3), (8, 8, 2, 3),
    ):
        raise FormatError("unsupported FTC range/domain geometry")

    quantizer_specs: list[tuple[int, int, int, int]] = []
    if version < 32:
        bits = data[descriptor + 7]
        step = data[descriptor + 8]
        base = _s16(data, descriptor + 9)
        count = _u16(data, descriptor + 11)
        cursor = descriptor + 13
        if cursor + count * 2 > main_size:
            raise FormatError("truncated FTC quantizer list")
        for index in range(count):
            quantizer_specs.append((_u16(data, cursor + index * 2), bits, step, base))
        cursor += count * 2
    else:
        count = _u16(data, descriptor + 7)
        cursor = descriptor + 9
        if cursor + count * 6 > main_size:
            raise FormatError("truncated FTC quantizer list")
        for index in range(count):
            quantizer_specs.append(struct.unpack_from("<HBBh", data, cursor + index * 6))
        cursor += count * 6
    if count not in (1, 2):
        raise FormatError(f"unsupported FTC quantizer count {count}")
    if version < 32 and len({spec[1] for spec in quantizer_specs}) != 1:
        raise FormatError("FTC 3.1 quantizers do not share a bit width")
    quantizers = tuple(_make_quantizer(*spec, version) for spec in quantizer_specs)

    if cursor + 13 > main_size:
        raise FormatError("truncated FTC descriptor tail")
    descriptor_tail = data[cursor:cursor + 13]
    if not (
        descriptor_tail[:2] == b"\x08\x00"
        and _u16(descriptor_tail, 2) in (1, 3)
        and descriptor_tail[4:9] == b"\x00\x00\x01\x00\x03"
        and 1 <= descriptor_tail[9] <= 12
        and descriptor_tail[10] != 0
    ):
        raise FormatError("unsupported FTC descriptor-tail geometry")
    template_step = _u16(descriptor_tail, 6)
    template_symmetry_bits = descriptor_tail[8]
    template_quantizer = _make_template_quantizer(
        descriptor_tail[9], descriptor_tail[10],
        _s16(descriptor_tail, 11),
    )
    cursor += 13
    arithmetic_deltas: tuple[int, ...] = ()
    if version >= 33:
        if cursor >= main_size:
            raise FormatError("missing FTC arithmetic-delta count")
        delta_count = data[cursor]
        cursor += 1
        if cursor + delta_count > main_size:
            raise FormatError("truncated FTC arithmetic-delta list")
        arithmetic_deltas = tuple(
            value - 256 if value >= 128 else value
            for value in data[cursor:cursor + delta_count]
        )
        cursor += delta_count
    encoder_statistics = data[cursor:main_size]
    if version >= 33:
        if len(encoder_statistics) != 4:
            raise FormatError("invalid FTC 3.3 encoder-statistics fields")
    elif count == 1:
        if encoder_statistics:
            raise FormatError("unexpected bytes after the FTC quantizer descriptor")
    elif len(encoder_statistics) != 5 or encoder_statistics[0] != 0:
        raise FormatError("invalid FTC two-quantizer encoder statistics")

    auxiliary_palette = _parse_palette(data[main_size:main_size + auxiliary_size])
    payload_start = main_size + auxiliary_size
    payload = data[payload_start:payload_start + payload_size]
    segments: list[bytes] = []
    cursor = 0
    for index in range(region_count):
        if cursor + 4 > len(payload):
            raise FormatError(f"missing compressed length for FTC region {index}")
        length = _u32(payload, cursor)
        cursor += 4
        if length == 0 or cursor + length > len(payload):
            raise FormatError(f"invalid compressed length for FTC region {index}")
        segments.append(payload[cursor:cursor + length])
        cursor += length
    if cursor != len(payload):
        raise FormatError("bytes remain after the final FTC region stream")

    attached_type: str | None = None
    attached_metadata = b""
    attached_data = b""
    container_trailer = b""
    if data[4] in (1, 2) and secondary_size:
        container_trailer = data[payload_start + payload_size:]
        if container_trailer not in (
            GENERATION2_VENDOR_STAMP, b"VS##LTS000ST30",
        ):
            raise FormatError("unsupported FTC generation-1/2 encoder stamp")
    elif secondary_size:
        attachment = data[payload_start + payload_size:]
        attached_type, attached_metadata, attached_data = _parse_attachment(
            attachment[:106], attachment[106:]
        )

    return ModernFTC(
        codec_profile, transform_major, transform_minor,
        output_width, output_height, 0, 0,
        color, euv_color, range_size, domain_step, symmetry_bits, quantizers,
        template_step, template_symmetry_bits, template_quantizer,
        tuple(regions), directory_budget, directory_plane_code,
        directory_workspace, tuple(transform_templates), tuple(segments),
        descriptor_tail, encoder_statistics,
        auxiliary_palette, arithmetic_deltas, attached_type,
        attached_metadata, attached_data, container_trailer,
    )


def _parse_ftt(data: bytes,
               reference: TransformTemplateReference) -> FractalTransformTemplate:
    """Parse the raw-raster FTT 1.1 profile referenced by FTC 3.x."""
    if len(data) < 26:
        raise FormatError("external FTT file is shorter than its 26-byte header")
    if data[:4] != b"FTT\x00":
        raise FormatError("external template signature is not FTT\\0")
    if data[4:6] != b"\x00\x00" or _u16(data, 6) != 0x0101:
        raise FormatError("unsupported external FTT header version")
    width = _u16(data, 8)
    height = _u16(data, 10)
    if (_u16(data, 12), _u16(data, 14), _u16(data, 16)) != (8, 0, 26):
        raise FormatError("unsupported external FTT raster geometry")
    payload_length = _u32(data, 18)
    identifier = _u32(data, 22)
    if len(data) != 26 + payload_length:
        raise FormatError("external FTT payload length is inconsistent")
    if payload_length != width * height:
        raise FormatError("external FTT is not the one-byte raw-raster profile")
    if (width, height, identifier) != (
        reference.width, reference.height, reference.identifier
    ):
        raise FormatError(
            "external FTT dimensions or identity do not match the FTC reference"
        )
    return FractalTransformTemplate(width, height, identifier, data[26:])


def _load_ftt(reference: TransformTemplateReference,
              directories: tuple[Path, ...]) -> FractalTransformTemplate:
    """Locate an FTT by referenced basename, case-insensitively."""
    basename = reference.filename.rsplit("\\", 1)[-1]
    folded = basename.casefold()
    checked: set[Path] = set()
    for directory in directories:
        try:
            resolved = directory.resolve()
        except OSError:
            continue
        if resolved in checked or not resolved.is_dir():
            continue
        checked.add(resolved)
        try:
            matches = sorted(
                path for path in resolved.iterdir()
                if path.is_file() and path.name.casefold() == folded
            )
        except OSError:
            continue
        if matches:
            try:
                return _parse_ftt(matches[0].read_bytes(), reference)
            except OSError as error:
                raise FormatError(f"cannot read external FTT {matches[0]}") from error
    raise FormatError(
        f"FTC image requires external FTT template {basename!r} "
        f"({reference.width}x{reference.height}, identity "
        f"0x{reference.identifier:08x}), but no matching FTT file was found"
    )


def _mark_final_runs(bits: Bits, candidates: list[int], labels: bytearray,
                     zero_label: int, one_label: int, description: str) -> None:
    state = bits.read(1)
    cursor = 0
    remaining = len(candidates)
    while remaining:
        run = bits.read_run()
        if run > remaining:
            raise FormatError(
                f"{description} run of {run} exceeds {remaining} remaining entries"
            )
        label = zero_label if state == 0 else one_label
        if label:
            for ordinal in candidates[cursor:cursor + run]:
                labels[ordinal] |= label
        cursor += run
        remaining -= run
        state ^= 1


def _read_modern_record(bits: Bits, header: ModernFTC, domain_width: int,
                        domain_height: int, kind: int) -> Record:
    version = header.transform_major * 10 + header.transform_minor
    if version < 32:
        raw = bits.read(header.quantizers[0].bits)
        selector = bits.read(1) if len(header.quantizers) == 2 else 0
    else:
        selector = bits.read(1) if len(header.quantizers) == 2 else 0
        raw = bits.read(header.quantizers[selector].bits)
    quantizer = header.quantizers[selector]
    if raw >= len(quantizer.values):
        raise FormatError("quantizer index is outside its declared table")

    domain_count = domain_width * domain_height
    domain_index = bits.read((domain_count - 1).bit_length())
    if domain_index >= domain_count:
        raise FormatError("domain index is outside its declared grid")
    symmetry = bits.read(header.symmetry_bits)
    return Record(
        kind, raw, quantizer.values[raw], domain_index,
        domain_index % domain_width * header.domain_step,
        domain_index // domain_width * header.domain_step,
        symmetry, quantizer.kind,
    )


def _read_template_record(bits: Bits, header: ModernFTC,
                          template: FractalTransformTemplate,
                          kind: int) -> Record:
    quantizer = header.template_quantizer
    raw = bits.read(quantizer.bits)
    domain_width = (
        template.width + header.template_step - 1
    ) // header.template_step
    domain_height = (
        template.height + header.template_step - 1
    ) // header.template_step
    domain_count = domain_width * domain_height
    domain_index = bits.read((domain_count - 1).bit_length())
    if domain_index >= domain_count:
        raise FormatError("FTT domain index is outside its declared grid")
    symmetry = bits.read(header.template_symmetry_bits)
    return Record(
        kind, raw, quantizer.values[raw], domain_index,
        domain_index % domain_width * header.template_step * 2,
        domain_index // domain_width * header.template_step * 2,
        symmetry, quantizer.kind,
    )


def _parse_modern_plane(bits: Bits, header: ModernFTC, width: int, height: int,
                        domain_height_prefix: int = 0,
                        template: FractalTransformTemplate | None = None) \
        -> list[Record]:
    range_width = width // header.range_size
    range_height = height // header.range_size
    domain_width = (width + header.domain_step - 1) // header.domain_step
    domain_height = (
        domain_height_prefix
        + (height + header.domain_step - 1) // header.domain_step
    )
    order, padded_width, padded_height = _tile_order(range_width, range_height)
    candidates = [ordinal for ordinal, logical in enumerate(order) if logical >= 0]
    labels = bytearray(padded_width * padded_height)

    survivors = _mark_runs(bits, candidates, labels, 2, "class-2 mask")
    if survivors:
        survivors = _mark_runs(bits, survivors, labels, 6, "class-6 mask")
    if survivors:
        survivors = _mark_runs(bits, survivors, labels, 1, "class-1 mask")
    if survivors:
        survivors = _mark_runs(bits, survivors, labels, 5, "class-5 mask")
    if survivors:
        _mark_final_runs(bits, survivors, labels, 0, 4, "class-0/4 mask")

    if (any(labels[ordinal] in (4, 5, 6) for ordinal in candidates)
            and template is None):
        raise FormatError("stream uses an external FTT but none was supplied")

    records: list[Record | None] = [None] * (range_width * range_height)
    for label, group_size in ((2, 4), (1, 2)):
        last_group = -1
        base: Record | None = None
        group_area = group_size * group_size
        for ordinal, actual in enumerate(labels):
            if actual != label:
                continue
            group = ordinal // group_area
            if group != last_group:
                base = _read_modern_record(
                    bits, header, domain_width, domain_height, label
                )
                last_group = group
            logical = order[ordinal]
            if logical >= 0:
                assert base is not None
                records[logical] = _grouped_record(base, ordinal, group_size)

    for ordinal, label in enumerate(labels):
        logical = order[ordinal]
        if label == 0 and logical >= 0:
            records[logical] = _read_modern_record(
                bits, header, domain_width, domain_height, 0
            )

    if template is not None:
        for label, group_size in ((6, 4), (5, 2)):
            last_group = -1
            base = None
            group_area = group_size * group_size
            for ordinal, actual in enumerate(labels):
                if actual != label:
                    continue
                group = ordinal // group_area
                if group != last_group:
                    base = _read_template_record(bits, header, template, label)
                    last_group = group
                logical = order[ordinal]
                if logical >= 0:
                    assert base is not None
                    records[logical] = _grouped_record(base, ordinal, group_size)
        for ordinal, label in enumerate(labels):
            logical = order[ordinal]
            if label == 4 and logical >= 0:
                records[logical] = _read_template_record(
                    bits, header, template, 4
                )
    if any(record is None for record in records):
        raise FormatError("one or more FTC range blocks lack a transform record")
    return [record for record in records if record is not None]


class ArithmeticDecoder:
    """FTC profile-2 24-bit arithmetic decoder."""

    def __init__(self, data: bytes):
        self.data = data
        self.position = 0
        self.bit_position = 0
        self.interval = 0
        self.code = 0
        self.restart()

    def _byte(self) -> int:
        if self.position >= len(self.data):
            raise FormatError("truncated FTC arithmetic stream")
        value = self.data[self.position]
        self.position += 1
        return value

    def restart(self) -> None:
        self.code = (self._byte() << 16) | (self._byte() << 8) | self._byte()
        self.interval = 0x1000000

    def raw_bit(self) -> int:
        """Read the side-channel bitstream sharing the arithmetic byte cursor."""
        if self.position >= len(self.data):
            raise FormatError("truncated FTC arithmetic side channel")
        value = (self.data[self.position] >> self.bit_position) & 1
        self.bit_position += 1
        if self.bit_position == 8:
            self.bit_position = 0
            self.position += 1
        return value

    def decode(self, cumulative: tuple[int, ...]) -> int:
        if len(cumulative) < 2 or cumulative[0] != 0x4000 or cumulative[-1] != 0:
            raise FormatError("invalid internal FTC arithmetic model")
        symbol = -1
        lower = upper = 0
        for index in range(len(cumulative) - 1):
            upper = self.interval * cumulative[index] // 0x4000
            lower = self.interval * cumulative[index + 1] // 0x4000
            if lower <= self.code < upper:
                symbol = index
                break
        if symbol < 0 or upper <= lower:
            raise FormatError("FTC arithmetic code selects a zero-probability symbol")
        self.code -= lower
        self.interval = upper - lower
        while self.interval < 0x8000:
            self.interval <<= 8
            self.code = (self.code << 8) | self._byte()
        return symbol

    def uniform(self, count: int) -> int:
        if count not in (2, 4, 16):
            raise RuntimeError("internal FTC uniform model is not 2, 4, or 16")
        step = 0x4000 // count
        return self.decode(tuple(range(0x4000, -1, -step)))

    def model(self, count: int) -> tuple[int, ...]:
        """Read the profile-2 model-description stream for one alphabet."""
        if count <= 0 or count > 0x10000:
            raise FormatError(f"invalid FTC arithmetic alphabet size {count}")
        if count < 32:
            weights = [self.uniform(16) ** 2 for _ in range(count)]
        else:
            # Large alphabets encode a four-symbol predictor model with the
            # raw uniform symbols; only the small-alphabet form squares them.
            seed = [self.uniform(16) for _ in range(4)]
            total = sum(seed)
            if total == 0:
                raise FormatError("zero-total FTC arithmetic seed model")
            control = (
                0x4000,
                (total - seed[0]) * 0x4000 // total,
                (seed[2] + seed[3]) * 0x4000 // total,
                seed[3] * 0x4000 // total,
                0,
            )
            weights = []
            previous = 0
            delta = 1
            for _ in range(count):
                action = self.decode(control)
                if previous == 0:
                    delta = (1, 1, 4, 12)[action]
                    value = (0, 1, 4, 12)[action]
                else:
                    if action == 1:
                        delta = (
                            _c_div(1 - delta, 2)
                            if delta < 0 else _c_div(-1 - delta, 2)
                        )
                    elif action == 2:
                        delta = (
                            _c_div(delta - 1, 2)
                            if delta < 0 else _c_div(delta + 1, 2)
                        )
                    elif action == 3:
                        delta *= 2
                    value = max(previous + delta, 0)
                weights.append(value)
                previous = value
        total = sum(weights)
        if total == 0:
            raise FormatError("zero-total FTC arithmetic model")
        cumulative = [0] * (count + 1)
        running = 0
        for index in range(count - 1, -1, -1):
            running += weights[index]
            cumulative[index] = running * 0x4000 // total
        cumulative[count] = 0
        cumulative[0] = 0x4000
        return tuple(cumulative)


@dataclass
class _Profile2Group:
    kind: int
    size: int
    start: int
    ordinals: list[int]
    selector: int = 0
    raw_quantization: int = 0
    symmetry: int = 0
    domain_x: int = 0
    domain_y: int = 0


def _decode_profile2_classes(decoder: ArithmeticDecoder, width: int,
                             height: int) -> tuple[list[int], bytearray]:
    range_width = width // 4
    range_height = height // 4
    order, padded_width, padded_height = _tile_order(range_width, range_height)
    count = padded_width * padded_height
    labels = bytearray(0xFF if logical < 0 else 0 for logical in order)
    flags = decoder.uniform(4)

    def symbols(amount: int) -> list[int]:
        model = decoder.model(16)
        return [decoder.decode(model) for _ in range(amount)]

    if flags & 1:
        dictionary = symbols(count // 4)
        for group, value in enumerate(dictionary):
            for bit in range(4):
                ordinal = group * 4 + bit
                if labels[ordinal] != 0xFF and value & (1 << bit):
                    labels[ordinal] |= 4

    if flags & 2:
        classes = symbols(count // 4)
        zeroes = symbols(count // 4)
        for group, (class_bits, zero_bits) in enumerate(zip(classes, zeroes)):
            for bit in range(4):
                ordinal = group * 4 + bit
                if labels[ordinal] == 0xFF:
                    continue
                if class_bits & (1 << bit):
                    labels[ordinal] |= 2
                elif not zero_bits & (1 << bit):
                    labels[ordinal] |= 1
    else:
        classes = symbols(count // 16)
        zeroes = symbols(count // 4)
        for supergroup, class_bits in enumerate(classes):
            for subgroup in range(4):
                group = supergroup * 4 + subgroup
                label = 2 if class_bits & (1 << subgroup) else 1
                zero_bits = zeroes[group]
                for bit in range(4):
                    ordinal = group * 4 + bit
                    if labels[ordinal] == 0xFF:
                        continue
                    labels[ordinal] |= label
                    if zero_bits & (1 << bit):
                        labels[ordinal] &= 0xFC
    return order, labels


def _profile2_groups(labels: bytearray) -> list[_Profile2Group]:
    groups: list[_Profile2Group] = []
    for kind, size in ((2, 4), (1, 2), (0, 1)):
        area = size * size
        by_group: dict[int, list[int]] = {}
        for ordinal, actual in enumerate(labels):
            if actual == kind:
                by_group.setdefault(ordinal // area, []).append(ordinal)
        for group, ordinals in by_group.items():
            groups.append(_Profile2Group(kind, size, group * area, ordinals))
    return groups


def _decode_profile2_field(decoder: ArithmeticDecoder,
                           groups: list[_Profile2Group], count: int,
                           setter) -> None:
    model = decoder.model(count)
    for group in groups:
        setter(group, decoder.decode(model))


def _parse_profile2_plane(decoder: ArithmeticDecoder, header: ModernFTC,
                          width: int, height: int,
                          combined_height: int | None = None) -> list[Record]:
    order, labels = _decode_profile2_classes(decoder, width, height)
    if any(label in (4, 5, 6) for label in labels if label != 0xFF):
        raise FormatError("FTC profile-2 stream references a transform dictionary")
    groups = _profile2_groups(labels)
    if not groups:
        raise FormatError("FTC profile-2 plane contains no transforms")

    selector_bits = (len(header.quantizers) - 1).bit_length()
    maximum_bits = max(quantizer.bits for quantizer in header.quantizers)
    main_bits = min(maximum_bits, 9)
    extra_bits = maximum_bits - main_bits
    if len(header.quantizers) > 1:
        _decode_profile2_field(
            decoder, groups, len(header.quantizers),
            lambda group, value: setattr(group, "selector", value),
        )
    _decode_profile2_field(
        decoder, groups, 1 << main_bits,
        lambda group, value: setattr(group, "raw_quantization", value << extra_bits),
    )
    if extra_bits:
        _decode_profile2_field(
            decoder, groups, 1 << extra_bits,
            lambda group, value: setattr(
                group, "raw_quantization", group.raw_quantization | value
            ),
        )
    _decode_profile2_field(
        decoder, groups, 1 << header.symmetry_bits,
        lambda group, value: setattr(group, "symmetry", value),
    )

    domain_width = (width + header.domain_step - 1) // header.domain_step
    x_predictive = decoder.uniform(2) != 0
    x_model = decoder.model(domain_width)
    range_width = width // header.range_size
    for group in groups:
        value = decoder.decode(x_model)
        if x_predictive:
            logical = order[group.start]
            if logical < 0:
                raise FormatError("invalid FTC profile-2 group origin")
            predictor = (logical % range_width) * header.range_size // header.domain_step
            value = (predictor - domain_width // 2 + value) % domain_width
        group.domain_x = value * header.domain_step

    domain_height = (combined_height if combined_height is not None else height)
    domain_height = (domain_height + header.domain_step - 1) // header.domain_step
    y_predictive = decoder.uniform(2) != 0
    y_model = decoder.model(domain_height)
    for group in groups:
        value = decoder.decode(y_model)
        if y_predictive:
            logical = order[group.start]
            if logical < 0:
                raise FormatError("invalid FTC profile-2 group origin")
            predictor = (logical // range_width) * header.range_size // header.domain_step
            value = (predictor - domain_height // 2 + value) % domain_height
        group.domain_y = value * header.domain_step

    records: list[Record | None] = [None] * (width // 4 * (height // 4))
    for group in groups:
        if group.selector >= len(header.quantizers):
            raise FormatError("FTC profile-2 quantizer selector is outside its table")
        quantizer = header.quantizers[group.selector]
        raw = group.raw_quantization
        if raw >= len(quantizer.values):
            raise FormatError("FTC profile-2 quantization index is outside its table")
        base = Record(
            group.kind, raw, quantizer.values[raw], 0,
            group.domain_x, group.domain_y, group.symmetry, quantizer.kind,
            group.selector,
        )
        for ordinal in group.ordinals:
            logical = order[ordinal]
            if logical >= 0:
                records[logical] = (
                    base if group.size == 1
                    else _grouped_record(base, ordinal, group.size)
                )
    if any(record is None for record in records):
        raise FormatError("one or more FTC profile-2 blocks lack a transform")
    complete = [record for record in records if record is not None]
    if header.arithmetic_deltas:
        for ordinal, label in enumerate(labels):
            if label not in (1, 2):
                continue
            if decoder.raw_bit() == 0:
                delta = header.arithmetic_deltas[0]
            else:
                delta = header.arithmetic_deltas[1 + decoder.raw_bit()]
            logical = order[ordinal]
            if logical < 0:
                raise FormatError("FTC arithmetic side channel marks padding")
            record = complete[logical]
            quantizer = header.quantizers[record.quantizer_selector]
            raw = record.quantization_index + delta
            if not 0 <= raw < len(quantizer.values):
                raise FormatError("FTC arithmetic quantizer delta leaves its table")
            complete[logical] = replace(
                record, quantization_index=raw, quantized=quantizer.values[raw]
            )
    return complete


def _parse_profile2_segment(segment: bytes, header: ModernFTC,
                            region: Region) -> list[Record]:
    decoder = ArithmeticDecoder(segment)
    primary = _parse_profile2_plane(decoder, header, region.width, region.height)
    if header.color:
        if decoder.bit_position:
            decoder.position += 1
            decoder.bit_position = 0
        if header.arithmetic_deltas:
            decoder.restart()
        secondary = _parse_profile2_plane(
            decoder, header, region.width, region.height // 2,
            region.height + (region.height + 1) // 2,
        )
    else:
        secondary = []
    # The arithmetic coder retains up to three final code-register bytes.  They
    # are part of its termination state and need not be fetched by renormalizing.
    if len(segment) - decoder.position > 3:
        raise FormatError(
            f"FTC arithmetic stream has {len(segment) - decoder.position} "
            "unexplained terminal bytes"
        )
    return primary + secondary


def _parse_modern_segment(segment: bytes, header: ModernFTC,
                          region: Region,
                          template: FractalTransformTemplate | None = None) \
        -> list[Record]:
    if header.codec_profile == 2:
        if template is not None:
            raise FormatError(
                "external FTT transforms in profile-2 arithmetic streams "
                "are not implemented"
            )
        return _parse_profile2_segment(segment, header, region)
    bits = Bits(segment)
    primary = _parse_modern_plane(
        bits, header, region.width, region.height, template=template
    )
    if header.color:
        bits.require_zero((-bits.position) & 7, "primary-plane alignment padding")
        prefix = (region.height + header.domain_step - 1) // header.domain_step
        secondary = _parse_modern_plane(
            bits, header, region.width, region.height // 2, prefix, template
        )
    else:
        secondary = []
    trailing = bits.length - bits.position
    if trailing > 7:
        raise FormatError(f"FTC region stream has {trailing} unexplained trailing bits")
    bits.require_zero(trailing, "FTC region terminal padding")
    return primary + secondary


def _transformed_coord(symmetry: int, row: int, column: int,
                       extent: int) -> tuple[int, int]:
    if symmetry == 0:
        return row, column
    if symmetry == 1:
        return row, extent - 1 - column
    if symmetry == 2:
        return extent - 1 - row, column
    if symmetry == 3:
        return extent - 1 - row, extent - 1 - column
    if symmetry == 4:
        return column, row
    if symmetry == 5:
        return column, extent - 1 - row
    if symmetry == 6:
        return extent - 1 - column, row
    return extent - 1 - column, extent - 1 - row


def _apply_affine(quantized: int, value: int, slope: int = 6) -> int:
    index = quantized + value * 8
    if not 0 <= index < 8192 or slope not in (4, 5, 6, 7, 8):
        raise FormatError("affine transform table index is outside its defined range")
    if slope == 6:
        return AFFINE[index]
    if index < 2048:
        return 0
    return min((32 + (index - 2048) * slope) >> 6, 255)


def _apply_template_offset(offset: int, value: int) -> int:
    """Apply an external-template transform through its saturating table."""
    return min(max(value + offset, 0), 255)


def _validate_sources(records: list[Record], width: int, packed_height: int,
                      template: FractalTransformTemplate | None = None) -> None:
    half_width = width // 2
    half_height = packed_height // 2
    for record in records:
        base_x = record.domain_x // 2
        base_y = record.domain_y // 2
        if record.kind >= 4:
            if template is None:
                raise FormatError("an FTT transform has no template raster")
            source_width = template.width
            source_height = template.height
        else:
            source_width = half_width
            source_height = half_height
        if not (0 <= base_x < source_width and 0 <= base_y < source_height):
            raise FormatError("transform domain origin is outside the packed canvas")


def _clamped_source_index(base_x: int, base_y: int, source_x: int,
                          source_y: int, half_width: int,
                          half_height: int) -> int:
    """Apply the codec's replicated-edge extension to a domain sample."""
    x = min(max(base_x + source_x, 0), half_width - 1)
    y = min(max(base_y + source_y, 0), half_height - 1)
    return y * half_width + x


def _initialize_half(records: list[Record], width: int,
                     packed_height: int,
                     template: FractalTransformTemplate | None = None) -> bytearray:
    half_width = width // 2
    half_height = packed_height // 2
    node_count = half_width * half_height
    quantized = [0] * node_count
    slopes = [6] * node_count
    sources = [0] * node_count
    states = bytearray(node_count)
    output = bytearray(node_count)
    block_width = width // 4

    for block_index, record in enumerate(records):
        block_y, block_x = divmod(block_index, block_width)
        target = block_y * 2 * half_width + block_x * 2
        base_x = record.domain_x // 2
        base_y = record.domain_y // 2
        for row in range(2):
            for column in range(2):
                source_y, source_x = _transformed_coord(
                    record.symmetry, row * 2, column * 2, 4
                )
                index = target + row * half_width + column
                if record.kind >= 4:
                    if template is None:
                        raise FormatError("an FTT transform has no template raster")
                    source = _clamped_source_index(
                        base_x, base_y, source_x, source_y,
                        template.width, template.height,
                    )
                    output[index] = _apply_template_offset(
                        record.quantized, template.pixels[source]
                    )
                    states[index] = 1
                    continue
                quantized[index] = record.quantized
                slopes[index] = record.slope
                sources[index] = _clamped_source_index(
                    base_x, base_y, source_x, source_y,
                    half_width, half_height,
                )

    for root in range(node_count):
        if states[root] != 0:
            continue
        source_index = sources[root]
        if states[source_index] == 1:
            output[root] = _apply_affine(
                quantized[root], output[source_index], slopes[root]
            )
            states[root] = 1
            continue

        chain = [root]
        states[source_index] = 2
        current = source_index
        while len(chain) < 513:
            chain.append(current)
            current = sources[current]
            if states[current] != 0:
                break
            states[current] = 2

        if states[current] == 1:
            value = output[current]
        else:
            for _ in range(32):
                chain.append(current)
                current = sources[current]
            value = 128
            for node in reversed(chain[-32:]):
                value = _apply_affine(quantized[node], value, slopes[node])
            del chain[-32:]

        for node in reversed(chain):
            states[node] = 1
            value = _apply_affine(quantized[node], value, slopes[node])
            output[node] = value
    return output


def _converge_half(records: list[Record], half: bytearray,
                   width: int) -> None:
    half_width = width // 2
    half_height = len(half) // half_width
    block_width = width // 4
    converged = bytearray(len(records))
    while True:
        any_changed = False
        for block_index, record in enumerate(records):
            if converged[block_index]:
                continue
            if record.kind >= 4:
                converged[block_index] = 1
                continue
            block_y, block_x = divmod(block_index, block_width)
            target = block_y * 2 * half_width + block_x * 2
            base_x = record.domain_x // 2
            base_y = record.domain_y // 2
            significant = False
            for row in range(2):
                for column in range(2):
                    source_y, source_x = _transformed_coord(
                        record.symmetry, row * 2, column * 2, 3
                    )
                    sources = (
                        _clamped_source_index(
                            base_x, base_y, source_x, source_y,
                            half_width, half_height,
                        ),
                        _clamped_source_index(
                            base_x, base_y, source_x + 1, source_y,
                            half_width, half_height,
                        ),
                        _clamped_source_index(
                            base_x, base_y, source_x, source_y + 1,
                            half_width, half_height,
                        ),
                        _clamped_source_index(
                            base_x, base_y, source_x + 1, source_y + 1,
                            half_width, half_height,
                        ),
                    )
                    total = (
                        half[sources[0]] + half[sources[1]]
                        + half[sources[2]] + half[sources[3]]
                    )
                    value = _apply_affine(
                        record.quantized, (total + 2) // 4, record.slope
                    )
                    target_index = target + row * half_width + column
                    difference = (value - half[target_index]) & 0xFF
                    if 4 < difference < 252:
                        significant = True
                    half[target_index] = value
            if significant:
                any_changed = True
            else:
                converged[block_index] = 1
        if not any_changed:
            return


def _expand_full(records: list[Record], half: bytearray,
                 width: int, packed_height: int,
                 template: FractalTransformTemplate | None = None) -> bytearray:
    half_width = width // 2
    half_height = packed_height // 2
    block_width = width // 4
    packed = bytearray(width * packed_height)
    for block_index, record in enumerate(records):
        block_y, block_x = divmod(block_index, block_width)
        target = block_y * 4 * width + block_x * 4
        base_x = record.domain_x // 2
        base_y = record.domain_y // 2
        for row in range(4):
            for column in range(4):
                source_y, source_x = _transformed_coord(
                    record.symmetry, row, column, 4
                )
                if record.kind >= 4:
                    if template is None:
                        raise FormatError("an FTT transform has no template raster")
                    value = template.pixels[_clamped_source_index(
                        base_x, base_y, source_x, source_y,
                        template.width, template.height,
                    )]
                else:
                    value = half[_clamped_source_index(
                        base_x, base_y, source_x, source_y,
                        half_width, half_height,
                    )]
                if record.kind >= 4:
                    value = _apply_template_offset(record.quantized, value)
                else:
                    value = _apply_affine(record.quantized, value, record.slope)
                packed[target + row * width + column] = value
    return packed


def reconstruct(records: list[Record], width: int, height: int,
                color: bool = True,
                template: FractalTransformTemplate | None = None) -> bytearray:
    packed_height = height * 3 // 2 if color else height
    expected_records = width // 4 * (
        height // 4 + (height // 8 if color else 0)
    )
    if len(records) != expected_records:
        raise FormatError(
            f"decoded {len(records)} records; expected {expected_records}"
        )
    _validate_sources(records, width, packed_height, template)
    half = _initialize_half(records, width, packed_height, template)
    _converge_half(records, half, width)
    return _expand_full(records, half, width, packed_height, template)


def _signed_byte(value: int) -> int:
    value &= 0xFF
    return value - 256 if value >= 128 else value


def _clamp_10bit(value: int) -> int:
    index = value & 0x3FF
    if index < 256:
        return index
    if index < 640:
        return 255
    return 0


def _filter_tables() -> tuple[list[int], list[int]]:
    near = [0] * 512
    far = [0] * 512
    for index in range(256):
        near[index] = min((index * 2 + 2) // 5, 16)
        far[index] = min((index + 1) // 6, 16)
    for index in range(256, 512):
        value = _c_div(index * 2 - 0x402, 5) + 0x100
        value = 0xF0 if value < 0xF0 else (0 if value > 0xFF else value)
        near[index] = _signed_byte(value)
        value = _c_div(index - 0x201, 10) + 0x100
        value = 0xF0 if value < 0xF0 else (0 if value > 0xFF else value)
        far[index] = _signed_byte(value)
    return near, far


FILTER_NEAR, FILTER_FAR = _filter_tables()


def _filter_side(pixels: bytearray, minus_two: int, minus_one: int,
                 plus_zero: int, plus_one: int, flags: int) -> None:
    correction_near = FILTER_NEAR[
        (pixels[plus_zero] - pixels[minus_one]) & 0x1FF
    ]
    correction_far = FILTER_FAR[
        (pixels[plus_one] - pixels[minus_two]) & 0x1FF
    ]
    half = _c_div(correction_near, 2)
    if flags & 1:
        pixels[plus_zero] = _clamp_10bit(
            pixels[plus_zero] - correction_near + correction_far
        )
        pixels[plus_one] = _clamp_10bit(pixels[plus_one] - half)
    if flags & 2:
        pixels[minus_one] = _clamp_10bit(
            pixels[minus_one] + correction_near - correction_far
        )
        pixels[minus_two] = _clamp_10bit(pixels[minus_two] + half)


def transform_filter(records: list[Record], packed: bytearray,
                     width: int, height: int, color: bool = True) -> None:
    block_columns = width // 4
    block_rows = height // 4 + (height // 8 if color else 0)
    stride = block_columns + 1
    markers = bytearray(stride * (block_rows + 1))
    mask = bytearray(stride * (block_rows + 1))
    for index, record in enumerate(records):
        row, column = divmod(index, block_columns)
        markers[row * stride + column] = 1 << record.kind

    for category, group_size in ((2, 2), (4, 4), (32, 2), (64, 4)):
        for group_y in range(0, block_rows // group_size * group_size, group_size):
            for group_x in range(
                0, block_columns // group_size * group_size, group_size
            ):
                for offset in range(group_size):
                    if markers[group_y * stride + group_x + offset] == category:
                        mask[group_y * stride + group_x + offset] |= 4
                    if markers[
                        (group_y + group_size - 1) * stride + group_x + offset
                    ] == category:
                        mask[(group_y + group_size) * stride + group_x + offset] |= 8
                    if markers[(group_y + offset) * stride + group_x] == category:
                        mask[(group_y + offset) * stride + group_x] |= 1
                    if markers[
                        (group_y + offset) * stride + group_x + group_size - 1
                    ] == category:
                        mask[(group_y + offset) * stride + group_x + group_size] |= 2

    primary_rows = block_rows * 2 // 3 if color else block_rows
    if color:
        for row in range(primary_rows, block_rows):
            mask[row * stride + block_columns // 2] &= 0xFC
        for column in range(block_columns):
            mask[primary_rows * stride + column] &= 0xF3
            mask[column] &= 0xF3
    else:
        for column in range(block_columns):
            mask[column] &= 0xF3
    for row in range(block_rows):
        mask[row * stride] &= 0xFC

    for block_y in range(block_rows):
        for block_x in range(block_columns):
            flags = mask[block_y * stride + block_x]
            base = block_y * 4 * width + block_x * 4
            vertical = flags & 3
            if vertical:
                for offset in range(4):
                    position = base + offset * width
                    _filter_side(packed, position - 2, position - 1,
                                 position, position + 1, vertical)
            horizontal = (flags >> 2) & 3
            if horizontal:
                for offset in range(4):
                    position = base + offset
                    _filter_side(packed, position - 2 * width, position - width,
                                 position, position + width, horizontal)


def _color_tables() -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
    red_from_v = [0] * 256
    green_from_v = [0] * 256
    green_from_u = [0] * 256
    value = -0x804
    accumulator_v = -0x34187
    accumulator_u = -0x31A8F
    for index in range(128):
        red_from_v[index] = _c_div(value, 10)
        green_from_v[index] = _c_div(accumulator_v, 16)
        green_from_u[index] = _c_div(accumulator_u, 32)
        value += 0x10
        accumulator_v += 0x683
        accumulator_u += 0x635
    value = 5
    accumulator_v = 8
    accumulator_u = 0x10
    for index in range(128, 256):
        red_from_v[index] = _c_div(value, 10)
        green_from_v[index] = _c_div(accumulator_v, 16)
        green_from_u[index] = _c_div(accumulator_u, 32)
        value += 0x10
        accumulator_v += 0x683
        accumulator_u += 0x635
    return tuple(red_from_v), tuple(green_from_v), tuple(green_from_u)


RED_FROM_V, GREEN_FROM_V, GREEN_FROM_U = _color_tables()


def packed_yuv_to_rgb(packed: bytes, width: int, height: int) -> bytes:
    y_plane = memoryview(packed)[:width * height]
    chroma = memoryview(packed)[width * height:]
    chroma_width = width // 2
    chroma_height = height // 2
    rgb = bytearray(width * height * 3)

    for y in range(height):
        chroma_y = y // 2
        next_y = min(chroma_y + 1, chroma_height - 1)
        odd_y = y & 1
        for x in range(width):
            chroma_x = x // 2
            next_x = min(chroma_x + 1, chroma_width - 1)
            odd_x = x & 1
            u00 = chroma[chroma_y * width + chroma_x]
            v00 = chroma[chroma_y * width + chroma_width + chroma_x]
            if odd_x and odd_y:
                u = (
                    u00
                    + chroma[chroma_y * width + next_x]
                    + chroma[next_y * width + chroma_x]
                    + chroma[next_y * width + next_x]
                    + 2
                ) // 4
                v = (
                    v00
                    + chroma[chroma_y * width + chroma_width + next_x]
                    + chroma[next_y * width + chroma_width + chroma_x]
                    + chroma[next_y * width + chroma_width + next_x]
                    + 2
                ) // 4
            elif odd_x:
                u = (u00 + chroma[chroma_y * width + next_x] + 1) // 2
                v = (
                    v00 + chroma[chroma_y * width + chroma_width + next_x] + 1
                ) // 2
            elif odd_y:
                u = (u00 + chroma[next_y * width + chroma_x] + 1) // 2
                v = (
                    v00 + chroma[next_y * width + chroma_width + chroma_x] + 1
                ) // 2
            else:
                u, v = u00, v00

            luminance = y_plane[y * width + x]
            output = (y * width + x) * 3
            rgb[output] = _clamp_10bit(luminance + RED_FROM_V[v])
            rgb[output + 1] = _clamp_10bit(
                luminance - ((GREEN_FROM_U[u] + GREEN_FROM_V[v]) >> 7)
            )
            rgb[output + 2] = _clamp_10bit(luminance - 0x100 + u * 2)
    return bytes(rgb)


def packed_euv_to_rgb(packed: bytes, width: int, height: int) -> bytes:
    """Convert the later error-UV representation to interleaved RGB."""
    y_plane = memoryview(packed)[:width * height]
    chroma = memoryview(packed)[width * height:]
    chroma_width = width // 2
    chroma_height = height // 2
    rgb = bytearray(width * height * 3)

    for y in range(height):
        chroma_y = y // 2
        next_y = min(chroma_y + 1, chroma_height - 1)
        odd_y = y & 1
        for x in range(width):
            chroma_x = x // 2
            next_x = min(chroma_x + 1, chroma_width - 1)
            odd_x = x & 1
            first = chroma[chroma_y * width + chroma_x]
            second = chroma[chroma_y * width + chroma_width + chroma_x]
            if odd_x and odd_y:
                first = (
                    first
                    + chroma[chroma_y * width + next_x]
                    + chroma[next_y * width + chroma_x]
                    + chroma[next_y * width + next_x]
                    + 2
                ) // 4
                second = (
                    second
                    + chroma[chroma_y * width + chroma_width + next_x]
                    + chroma[next_y * width + chroma_width + chroma_x]
                    + chroma[next_y * width + chroma_width + next_x]
                    + 2
                ) // 4
            elif odd_x:
                first = (first + chroma[chroma_y * width + next_x] + 1) // 2
                second = (
                    second + chroma[chroma_y * width + chroma_width + next_x] + 1
                ) // 2
            elif odd_y:
                first = (first + chroma[next_y * width + chroma_x] + 1) // 2
                second = (
                    second + chroma[next_y * width + chroma_width + chroma_x] + 1
                ) // 2

            luminance = y_plane[y * width + x]
            shared = ((first + second) * 2 + 1) // 3
            shared = (shared + luminance + 0x56) & 0x3FF
            output = (y * width + x) * 3
            rgb[output] = _clamp_10bit(shared - first * 2)
            rgb[output + 1] = _clamp_10bit(shared - 0x100)
            rgb[output + 2] = _clamp_10bit(shared - second * 2)
    return bytes(rgb)


def _crop_rgb(pixels: bytes, source_width: int, output_width: int,
              output_height: int, origin_x: int = 0, origin_y: int = 0) -> bytes:
    if origin_x == 0 and output_width == source_width and origin_y == 0:
        return pixels[:output_width * output_height * 3]
    cropped = bytearray(output_width * output_height * 3)
    source_stride = source_width * 3
    output_stride = output_width * 3
    for row in range(output_height):
        start = (origin_y + row) * source_stride + origin_x * 3
        cropped[row * output_stride:(row + 1) * output_stride] = (
            pixels[start:start + output_stride]
        )
    return bytes(cropped)


def _decode_modern_profile1(
    data: bytes,
    template_directories: tuple[Path, ...] = (),
) -> tuple[int, int, bytes]:
    header = _parse_modern_ftc(data)
    template: FractalTransformTemplate | None = None
    if header.transform_templates:
        if len(header.transform_templates) != 1:
            raise FormatError("FTC images with multiple FTT references are unsupported")
        template = _load_ftt(header.transform_templates[0], template_directories)
    if header.range_size != 4:
        raise FormatError(
            "FTC 8x8 range/domain reconstruction is not implemented"
        )
    canvas_width = max(region.x + region.width for region in header.regions)
    canvas_height = max(region.y + region.height for region in header.regions)
    if canvas_width & 7 or canvas_height & 7:
        raise FormatError("FTC coded canvas is not eight-pixel aligned")
    if (header.origin_x + header.output_width > canvas_width or
            header.origin_y + header.output_height > canvas_height):
        raise FormatError("FTC original-image rectangle exceeds its coded canvas")

    y_plane = bytearray(canvas_width * canvas_height)
    coverage = bytearray(canvas_width * canvas_height)
    if header.color:
        chroma = bytearray(canvas_width * canvas_height // 2)
    else:
        chroma = bytearray()

    for region_index, (region, segment) in enumerate(
            zip(header.regions, header.payload_segments)):
        try:
            records = _parse_modern_segment(segment, header, region, template)
            packed = reconstruct(
                records, region.width, region.height,
                color=header.color, template=template,
            )
            transform_filter(
                records, packed, region.width, region.height, color=header.color
            )
        except FormatError as error:
            raise FormatError(f"FTC region {region_index}: {error}") from error

        for row in range(region.height):
            source = row * region.width
            target = (region.y + row) * canvas_width + region.x
            if any(coverage[target:target + region.width]):
                raise FormatError("FTC regions overlap")
            y_plane[target:target + region.width] = packed[source:source + region.width]
            coverage[target:target + region.width] = b"\x01" * region.width

        if header.color:
            source_base = region.width * region.height
            for row in range(region.height // 2):
                source = source_base + row * region.width
                target = (region.y // 2 + row) * canvas_width + region.x // 2
                half = region.width // 2
                chroma[target:target + half] = packed[source:source + half]
                target += canvas_width // 2
                chroma[target:target + half] = packed[
                    source + half:source + region.width
                ]

    for row in range(header.origin_y, header.origin_y + header.output_height):
        start = row * canvas_width + header.origin_x
        if 0 in coverage[start:start + header.output_width]:
            raise FormatError("FTC regions do not cover the original-image rectangle")

    if header.color:
        packed_canvas = y_plane + chroma
        if header.euv_color:
            rgb = packed_euv_to_rgb(packed_canvas, canvas_width, canvas_height)
        else:
            rgb = packed_yuv_to_rgb(packed_canvas, canvas_width, canvas_height)
    else:
        rgb_buffer = bytearray(canvas_width * canvas_height * 3)
        for index, value in enumerate(y_plane):
            rgb_buffer[index * 3:index * 3 + 3] = bytes((value, value, value))
        rgb = bytes(rgb_buffer)
    return (
        header.output_width,
        header.output_height,
        _crop_rgb(
            rgb, canvas_width, header.output_width, header.output_height,
            header.origin_x, header.origin_y,
        ),
    )


# The original 1990s FIF generation uses a progressive transform stream whose
# fixed prefix-code books are part of the format.  LEGACY_PREFIX_TABLES below
# is a compressed copy of the normative 0x110310d0..0x11033867 table range;
# embedding it keeps this decoder self-contained and avoids any binary runtime.
LEGACY_PREFIX_BASE = 0x110310D0
LEGACY_PREFIX_TABLES = zlib.decompress(base64.b85decode(
    b"c-"
    b"rk*33ycH6+Lg>G7l1x5E94&2@saB%Ay7YD!8C6)M5*?g;s3q2DMrXRnP(!tl~l~*h&?&xM78=X%&@NMQbWzE3MKB"
    b"YEi)|Rj8UalWp?m_Pl@oOvB*hQNz-"
    b"Y@G^hicfXS}XYRk8d*5UVfGNo3IGw}busCdv$s8Ryn((n4lQ?oTel|x|GdzfYn&yxDl>B4*heF@5_+zUdOaHbEhj"
    b"*u0d=%pm%)+bq4jw|pSb{I(U3?WYaXF@<+7Qm&g}4CyaR)viUXS~51s>qMt;g-"
    b"e*P_OF64T(}9DGFlaeN)G;b&L}7i%>CL)?ZC=3xf$tMGkH$6v|6ALna+1N9%n)rb<Wq5kXCufW2D{toKjjT;an-j"
    b"n)oDgD}n{x7LNAD3Vw@qbc(1NCpkl?nX^slN>?@i6hHssEnRUy;!F^M7CG|7ME(SL^)uq{#mlI{!CP<lkNAzdJ?#"
    b"?REZ7rO5x=I{yVJ^1oB(Uz#HSOLhK>J|X|G<A%eQ>x7+f*s*N;zp<SZADy_3ez*wNVma=`=a7k?<1T!RZ=wL_p%1"
    b"QygLCOBlkpW?gC6(^mSH@8jBL8m7x4_z@f)=Ea$uqz2H;HGgCTUOe;^;_cmli78#mI;euOmoR3iq{;U?i%_#=kX*"
    b"E-`SyiFg=z$qApljvsOz`s#~v+z^Ah*9_~mg4Vt0eLtX-"
    b"$NaG;W!lHPw0fcn2R6c7CeG~VK077Z*<TBBXKh(VmrEE1g^s?7=+*9d2GSA@LgPni?JACoPjy`Gj?JqK93?)VlxI"
    b"}G`@!4qZlXPM2x`%Jc@28!z#Rlm+>6l!Qb!&I`)_7y0h^YRO7eUgsu1t{(vg{0MDW;j>oBL9;Wb|T)<r!;Z9wtVt"
    b";R6$o;yO``eFQo{ef_huX=0ypHE)I)uCUEfwF!y<bfiix>~9_yeAY2f5SN@_hU8?L1%A#%ki*RQwQ~=^UPksayd+"
    b"o~88tllrQPZ=n7LrGKZ2?^F6$D5vq`*QkHL(tlsYYm|OZ;tN%LH}z|k{zer)p!C}le@w;iQvW@r|4dT;^He;O`lU"
    b"*LY*PLoso10b>q_59%72K8`&0j8rJtUZf0l|br~Z7UA4|$Vs^VLz|Dn>ilk&Gzd<XR#l>V7X`M;^+3hF<p^y`!IU"
    b"!mgl)W1^cUj)<Sapb`?P1kW9+ub*I+@l@0=|E4@Yx>dc9lU`WI>9yco85Svr+yC|>MD9uHXZ6I)|-"
    b"3jPz&f+*VCDL(5ces0j>9;;q;;LtQHw`yFT=o-t@R-"
    b"bi#bP+}re_8|h6q(fvy3kuT5*%IQS|=sfq(nR4kNL+M$M(2MfuRWH&ndeNJnpzjQ#qcqY-UZEG=Oa~iD$LK`28be"
    b"pPh0ZaGepE?sa_Crn=}AlJVI$~Z&(m=V=|eBmsp{xd6X|ht=zLq~Qv>O0bLm27(OWL2+iarmOrY2J&hic&=TSOM7"
    b"v)aH^sw3Vsw(=?I6BuVdQvsrYA2oNGJ4Uo^rchjLuK?M=zei>v%V3!Z-"
    b"nj}p?gv2o)fy4gzi5Ngm3A4Q~x^df8@7TKPO55w8O0b|CWEp1m6g;E8cfF&4&F6BdoD-"
    b"3j9F%ZY%i*MIW4_5a%b8p5pT48;D9wiclq^Q70wzZyzru9ub!(Tg1nQ5g$jq3~~NmiSu_$oWDz|WIXX55>fo^66b"
    b"G~IDZTA3B)%`YW+z8`cne*rz!oKl=?FQ^ed%h{f*MHeucE0|9WXzzdS&HU4Z@?rC*y;|1PC(TNc}5%TagNa-"
    b"5_%84m~GL43EB{DZA;v6{|gzd4)LWj+?Ma;=gTvRszR5?L$@WS-y<UnXnpGWK38F-I<yS#tg%SKR*-"
    b"tY)vbmd}jm%5<43XCL-YV6%R2U_bO6`;3>^H*90g-"
    b"pO8h5Bu4O>NzLM8FGq@kr6Un21`HbCB;%8xsoMm;)rn&K5>X=&*eFbiOsX*$HEhm!#FDW3A{>tJR(hak-|$-"
    b"^7o35@0L{jYQx7P#;4WarQUysv`)XqXxsVM8m4Jkw#gUoj>%WEIBfFO0`3Ih2f%laxISylAU;);u~uwleb{^iTxc"
    b"}=!tw0tD_L7BSRW7nC-"
    b"D2mX_$d>R@XJGkcaydIQvzjrrOZt&_O<#T)moVN|Un(`)Cf@b0tjnBBfl9^Z3k_$yIUq6gY@$Q*G>(8un%$&(tvW"
    b"okhIYYTy|x<IKhRmE!Zaa~&^H{0i~;Te+qY#V;41zlF0r8}VMn=WkXszOVk=0R8y^`ilbeuM5y$B`xc(ke2nAOUw"
    b"F8rDgpk0s4yr^cMu^&r8y`ZQJ3?arNCvijQ{O+V8|ApP;tT3;CCU4(fYA6B%fy>S-o-"
    b"A^0qx#hvKm9T8S|Hg}wlcVd0@@f-"
    b"|Rc&_Gm*7dlH=I7x!h39L2f%?8OghI{liXjT`ruju$zgY9TW2nM=Xns$vU!wWF)VE^>dTV|kt>0JkOEFyG{WQP7)"
    b"*qnx195yn{wD<Fe_}xXWdZq*2*`hAK>jBM<UcAP|Ir9pVVlFzceky@S@6H}PUjjss&C9zbJ?D29A@l4vHN%j_1_e"
    b"O>(g1`X<TC;H@U_>p20Pa^9wY;Q1iPgJd<l2=ND;yvF0DsKeGCcWwIEUcC*o@Vt@Wk&Ra*$i^Dm|R&hJdzaOWo`8"
    b"PSAxf<`RVt@W^_5Z~@&Cl0(f#w&gI77|9&+n%3BF!&WaVC!GA6b1qAlm*zqP{zAEe3n<MeM;W<8<R%W0T>An%W{W"
    b"oLPMG!sI5)&{s%broODiAB6a{?Sxa_6PM6`VhD*C20WM&iwWP=KqIVJEEE#Y6T>tOM7dH8a6Hd6W1bhIVyGD%qzm"
    b"bYvn574NRP$Y;%Pca*X)?*^F6PTQc+^{s6(y9yvArleI05f8jE^S4_;$47<Kgx(MB&OHHfM|Xv)V;&&umQWbD<6m"
    b"~Y)qIdJ?+)Aw|J{|^;AZA<"
))
if len(LEGACY_PREFIX_TABLES) != 0x2798:
    raise RuntimeError("corrupt embedded legacy FIF prefix tables")


@dataclass(frozen=True)
class LegacyRegion:
    x: int
    y: int
    width: int
    height: int
    offsets: tuple[int, ...]


@dataclass(frozen=True)
class LegacyFIF:
    output_width: int
    output_height: int
    canvas_width: int
    canvas_height: int
    color: bool
    levels: int
    initial_exponent: int
    luminance_domain_step: int
    chroma_domain_step: int
    tile_width: int
    tile_height: int
    header_size: int
    primary_transform_limit: int
    aggregate_transform_limit: int
    quality: int
    global_offsets: tuple[int, ...]
    regions: tuple[LegacyRegion, ...]
    stream_ends: dict[int, int]
    palette: tuple[tuple[int, int, int], ...]
    extension_value: int
    data: bytes


@dataclass(frozen=True)
class LegacyModel:
    domain_kind: int
    components: int
    symmetry_count: int
    symmetry_base: int
    affine_count: int
    affine_base: int


@dataclass
class LegacyTransform:
    range_x: int
    range_y: int
    domain_x: int = 0
    domain_y: int = 0
    range_code: int = 0
    symmetry: int = 0
    affine: int = 0
    level_value: int = 0
    constant: bool = False


class LegacyBits:
    """Bounded LSB-first reader used by one legacy progressive segment."""

    def __init__(self, data: bytes, start: int, end: int,
                 virtual_zero_tail: bool = False):
        if not 0 <= start <= end or (end > len(data) and not virtual_zero_tail):
            raise FormatError("legacy FIF stream has invalid bounds")
        self.data = data
        self.position = start * 8
        self.limit = end * 8
        self.start = start
        self.end = end
        self.virtual_zero_tail = virtual_zero_tail

    def peek(self, count: int) -> int:
        if count < 0:
            raise FormatError("negative legacy FIF bit count")
        # The reference lookup tables speculatively fetch a machine word.  A
        # peek may therefore cross the logical segment boundary, but advancing
        # the stream across it is still rejected by read()/advance().
        value = 0
        for shift in range(count):
            bit = self.position + shift
            byte = bit >> 3
            if byte < len(self.data):
                value |= ((self.data[byte] >> (bit & 7)) & 1) << shift
        return value

    def advance(self, count: int) -> None:
        if count < 0 or self.position + count > self.limit:
            raise FormatError(
                f"legacy FIF stream at 0x{self.start:x} is truncated at "
                f"bit {self.position - self.start * 8}"
            )
        self.position += count

    def read(self, count: int) -> int:
        value = self.peek(count)
        self.advance(count)
        return value

    def finish(self, description: str) -> None:
        remaining = self.limit - self.position
        if remaining:
            if remaining > 7 or self.read(remaining) != 0:
                raise FormatError(
                    f"{description} leaves {remaining} non-padding bits"
                )


def _parse_legacy_palette(payload: bytes, components: int) \
        -> tuple[tuple[int, int, int], ...]:
    if len(payload) < 2 + components:
        raise FormatError("truncated legacy FIF palette chunk")
    count = _u16(payload, 0)
    widths = tuple(payload[2:2 + components])
    if count == 0 or components != 3 or any(not 1 <= width <= 8 for width in widths):
        raise FormatError("unsupported legacy FIF palette geometry")
    bits = Bits(payload[2 + components:])
    entries: list[tuple[int, int, int]] = []
    for _ in range(count):
        entries.append(tuple(bits.read(width) for width in widths))
    if bits.position != bits.length:
        raise FormatError("legacy FIF palette has unexplained trailing bits")
    return tuple(entries)


def _parse_legacy_ftu(payload: bytes) -> tuple[int, int]:
    if (len(payload) != 16 or payload[:4] != b"FTU\x00" or
            payload[4:8] != b"\x01\x01\x08\x00"):
        raise FormatError("invalid legacy FIF FTU original-size chunk")
    width = _u32(payload, 8)
    height = _u32(payload, 12)
    if width == 0 or height == 0:
        raise FormatError("legacy FIF FTU dimensions are zero")
    return width, height


def _parse_legacy_fif(data: bytes) -> LegacyFIF:
    """Parse and strictly validate the original FIF version-1 container."""
    if len(data) < 56:
        raise FormatError("file is shorter than the 56-byte legacy FIF header")
    if data[:4] != b"FIF\x01":
        raise FormatError("signature is not FIF\\x01")
    if data[4:6] != b"u\x00":
        raise FormatError("unsupported legacy FIF container version")
    output_width = _u32(data, 6)
    output_height = _u32(data, 10)
    header_size = _u16(data, 14)
    if not output_width or not output_height:
        raise FormatError("legacy FIF output dimensions are zero")
    if _u32(data, 16) != len(data):
        raise FormatError("legacy FIF declared length differs from file length")

    color_tag = data[20:24]
    output_tag = data[24:28]
    if (color_tag, output_tag) == (b"EUV\x00", b"BGR\x00"):
        color = True
        components = 3
    elif (color_tag, output_tag) == (b"Y\x00\x00\x00", b"Y\x00\x00\x00"):
        color = False
        components = 1
    else:
        raise FormatError("unsupported legacy FIF color/output representation")

    scale = _u16(data, 28)
    canvas_width = _u16(data, 30)
    canvas_height = _u16(data, 32)
    luminance_step = data[34]
    chroma_step = data[35]
    initial_exponent = data[36]
    levels = data[37]
    tile_width = _u16(data, 38)
    tile_height = _u16(data, 40)
    primary_transform_limit = _u32(data, 42)
    aggregate_transform_limit = _u32(data, 46)
    codec = data[50]
    chunk_count = data[51]
    if (scale != 1 or luminance_step != 2 or chroma_step != 4 or
            initial_exponent != 4 or levels != 5 or codec != 0x10):
        raise FormatError("unsupported legacy FIF transform geometry/codec")
    if (not canvas_width or not canvas_height or not tile_width or not tile_height or
            primary_transform_limit == 0 or aggregate_transform_limit == 0 or
            primary_transform_limit > aggregate_transform_limit):
        raise FormatError("invalid legacy FIF canvas/tiling fields")
    if data[52:55] != b"\x00\x00\x00":
        raise FormatError("nonzero legacy FIF reserved header bytes")
    quality = data[55]

    position = 56
    extension_value: int | None = None
    palette: tuple[tuple[int, int, int], ...] = ()
    ftu_size: tuple[int, int] | None = None
    directory: bytes | None = None
    chunk_order: list[int] = []
    for _ in range(chunk_count):
        if position + 3 > len(data):
            raise FormatError("truncated legacy FIF chunk header")
        kind = data[position]
        length = _u16(data, position + 1)
        position += 3
        if position + length > len(data):
            raise FormatError("truncated legacy FIF chunk payload")
        payload = data[position:position + length]
        position += length
        chunk_order.append(kind)
        if kind == 0xC0:
            if extension_value is not None or length != 2:
                raise FormatError("invalid duplicate/length for legacy FIF C0 chunk")
            extension_value = _u16(payload, 0)
            if extension_value not in (2, 4):
                raise FormatError("unsupported legacy FIF C0 transform option")
        elif kind == 0x31:
            if palette or not color:
                raise FormatError("invalid duplicate/inapplicable legacy FIF palette")
            palette = _parse_legacy_palette(payload, components)
        elif kind == 0xFF:
            if ftu_size is not None:
                raise FormatError("duplicate legacy FIF FTU chunk")
            ftu_size = _parse_legacy_ftu(payload)
        elif kind == 0x03:
            if directory is not None:
                raise FormatError("duplicate legacy FIF offset-directory chunk")
            directory = payload
        else:
            raise FormatError(f"unsupported legacy FIF chunk type 0x{kind:02x}")
    if position != header_size:
        raise FormatError("legacy FIF chunk sequence does not end at header size")
    expected_order = [0xC0] + ([0x31] if palette else []) + [0xFF, 0x03]
    if chunk_order != expected_order:
        raise FormatError("legacy FIF chunks are not in canonical order")
    if extension_value is None or ftu_size is None or directory is None:
        raise FormatError("legacy FIF is missing a required container chunk")
    if ftu_size != (output_width, output_height):
        raise FormatError("legacy FIF fixed header and FTU dimensions disagree")

    columns = (canvas_width + tile_width - 1) // tile_width
    rows = (canvas_height + tile_height - 1) // tile_height
    region_count = columns * rows
    expected_directory_size = (1 + region_count) * levels * 4
    if len(directory) != expected_directory_size:
        raise FormatError("legacy FIF offset-directory length is inconsistent")
    values = struct.unpack("<" + "I" * (len(directory) // 4), directory)
    global_offsets = tuple(values[:levels])
    level_offsets = tuple(
        values[levels + level * region_count:levels + (level + 1) * region_count]
        for level in range(levels)
    )
    regions: list[LegacyRegion] = []
    for index in range(region_count):
        row, column = divmod(index, columns)
        x = column * tile_width
        y = row * tile_height
        width = min(tile_width, canvas_width - x)
        height = min(tile_height, canvas_height - y)
        offsets = tuple(level_offsets[level][index] for level in range(levels))
        if any(first > second for first, second in zip(offsets, offsets[1:])):
            raise FormatError("legacy FIF region offsets are not progressive")
        regions.append(LegacyRegion(x, y, width, height, offsets))

    all_offsets = global_offsets + tuple(
        offset for region in regions for offset in region.offsets
    )
    if any(offset < header_size or offset > len(data) for offset in all_offsets):
        raise FormatError("legacy FIF stream offset lies outside the data area")
    if any(first > second for first, second in zip(global_offsets, global_offsets[1:])):
        raise FormatError("legacy FIF global offsets are not progressive")
    boundaries = sorted(set(all_offsets + (len(data),)))
    stream_ends = {
        start: boundaries[index + 1] if index + 1 < len(boundaries) else start
        for index, start in enumerate(boundaries)
    }
    if global_offsets[0] != regions[0].offsets[0]:
        raise FormatError("legacy FIF level-zero anchor is inconsistent")

    return LegacyFIF(
        output_width, output_height, canvas_width, canvas_height, color,
        levels, initial_exponent, luminance_step, chroma_step,
        tile_width, tile_height, header_size, primary_transform_limit,
        aggregate_transform_limit, quality,
        global_offsets, tuple(regions), stream_ends, palette,
        extension_value, data,
    )


def _legacy_offset(address: int, length: int = 1) -> int:
    offset = address - LEGACY_PREFIX_BASE
    if offset < 0 or offset + length > len(LEGACY_PREFIX_TABLES):
        raise RuntimeError(f"legacy FIF table address 0x{address:08x} is invalid")
    return offset


def _legacy_u8(address: int) -> int:
    return LEGACY_PREFIX_TABLES[_legacy_offset(address)]


def _legacy_s8(address: int) -> int:
    value = _legacy_u8(address)
    return value - 256 if value >= 128 else value


def _legacy_u16(address: int) -> int:
    return _u16(LEGACY_PREFIX_TABLES, _legacy_offset(address, 2))


def _legacy_s16(address: int) -> int:
    return _s16(LEGACY_PREFIX_TABLES, _legacy_offset(address, 2))


def _legacy_huffman(reader: LegacyBits, symbol_table: int, length_table: int,
                    extension_metadata: int | None = None,
                    extension_symbols: int | None = None) -> int:
    """Decode one value from a fixed FIF least-significant-bit prefix book."""
    lookahead = reader.peek(24)
    index = lookahead & 0xFF
    length = _legacy_u8(length_table + index)
    if not 1 <= length <= 16:
        raise FormatError("invalid legacy FIF prefix-code length")
    symbol = _legacy_s16(symbol_table + index * 2)
    reader.advance(length)
    if symbol >= 500:
        if extension_metadata is None or extension_symbols is None:
            raise FormatError("unexpected extended legacy FIF prefix symbol")
        base = _legacy_u16(0x11033310 + symbol * 2)
        extra = _legacy_u8(extension_metadata + base * 2)
        if not 1 <= extra <= 8:
            raise FormatError("invalid legacy FIF extended-prefix width")
        suffix = reader.peek(extra) & ((1 << extra) - 1)
        symbol = _legacy_s16(extension_symbols + (base + suffix) * 2)
        reader.advance(extra)
    return symbol


def _legacy_decode_models(header: LegacyFIF, level: int,
                          coverage: list[tuple[int, int]] | None = None) \
        -> tuple[LegacyModel, ...]:
    if level == 0:
        return ()
    start = header.global_offsets[level]
    reader = LegacyBits(header.data, start, header.stream_ends[start])
    count = reader.read(8)
    if not 1 <= count <= 3:
        raise FormatError(f"legacy FIF level {level} has invalid model count {count}")
    nibble_values = (0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 16, 24, 32, 48, 64, 128)
    models: list[LegacyModel] = []
    for _ in range(count):
        domain_kind = reader.read(6)
        components = reader.read(2)
        if domain_kind not in (0x11, 0x21, 0x22) or components not in (1, 2, 3):
            raise FormatError("invalid legacy FIF progressive model descriptor")
        values = tuple(nibble_values[reader.read(4)] for _ in range(4))
        if values[0] == 0 or values[2] == 0:
            raise FormatError("legacy FIF model has a zero-sized symbol alphabet")
        models.append(LegacyModel(domain_kind, components, *values))
    reader.finish(f"legacy FIF global model stream {level}")
    if coverage is not None:
        coverage.append((reader.start * 8, min(reader.position, len(header.data) * 8)))
    return tuple(models)


def _legacy_selection_symbol(reader: LegacyBits, doubled_range: int) -> int:
    if doubled_range == 2:
        return _legacy_huffman(reader, 0x110310D0, 0x110312D0) & 0xFF
    if doubled_range == 4:
        return _legacy_huffman(
            reader, 0x110313D0, 0x110315D0, 0x110316D0, 0x110316D2
        ) & 0xFF
    if doubled_range == 8:
        return _legacy_huffman(
            reader, 0x11031858, 0x11031A58, 0x11031B58, 0x11031B5A
        ) & 0xFF
    if doubled_range == 16:
        return _legacy_huffman(reader, 0x11031CE0, 0x11031EE0) & 0xFF
    raise FormatError(f"unsupported legacy FIF progressive range {doubled_range}")


def _legacy_intensity_symbol(reader: LegacyBits, table_kind: int) -> int:
    if table_kind == 0:
        return _legacy_huffman(
            reader, 0x11031FE0, 0x110321E0, 0x110322E0, 0x110322E2
        )
    if table_kind == 1:
        return _legacy_huffman(
            reader, 0x110324E8, 0x110326E8, 0x110327E8, 0x110327EA
        )
    if table_kind == 2:
        return _legacy_huffman(
            reader, 0x110329F0, 0x11032BF0, 0x11032CF0, 0x11032CF2
        )
    raise RuntimeError("invalid legacy FIF intensity table")


def _legacy_component_models(models: tuple[LegacyModel, ...], component: int) \
        -> tuple[tuple[int, LegacyModel], ...]:
    return tuple(
        (index, model)
        for index, model in enumerate(models)
        if (component == 0 and model.components != 2)
        or (component != 0 and model.components != 1)
    )


def _legacy_split_children(parent: LegacyTransform, half: int,
                           reader: LegacyBits, table_kind: int) \
        -> list[LegacyTransform]:
    coordinates = (
        (parent.range_x, parent.range_y),
        (parent.range_x + half, parent.range_y),
        (parent.range_x, parent.range_y + half),
        (parent.range_x + half, parent.range_y + half),
    )
    children = [
        LegacyTransform(x, y, level_value=parent.level_value)
        for x, y in coordinates
    ]
    for child in children[1:]:
        child.level_value = _clamp_10bit(
            parent.level_value - _legacy_intensity_symbol(reader, table_kind)
        )
    return children


def _legacy_decode_domain_position(reader: LegacyBits,
                                   transform: LegacyTransform,
                                   model: LegacyModel, range_size: int,
                                   doubled_range: int, domain_step: int,
                                   domain_columns: int,
                                   domain_bits: int) -> None:
    if model.domain_kind == 0x21:
        symbol = _legacy_huffman(reader, 0x11032DF8, 0x11032FF8) & 0xFF
        radius = range_size >> 1
        if radius < domain_step:
            radius = 0
        transform.domain_x = (
            transform.range_x
            + _legacy_s8(0x11033770 + symbol) * domain_step - radius
        )
        transform.domain_y = (
            transform.range_y
            + _legacy_s8(0x110337B0 + symbol) * domain_step - radius
        )
        transform.symmetry = 0
    elif model.domain_kind == 0x11:
        if doubled_range == 8:
            symbol = _legacy_huffman(reader, 0x110333F8, 0x110335F8) & 0xFF
        else:
            symbol = _legacy_huffman(reader, 0x110330F8, 0x110332F8) & 0xFF
        transform.domain_x = (
            transform.range_x + _legacy_s8(0x110337F0 + symbol) * domain_step
        )
        transform.domain_y = (
            transform.range_y + _legacy_s8(0x11033810 + symbol) * domain_step
        )
        transform.symmetry = 8
    else:
        domain_index = reader.read(domain_bits)
        transform.domain_x = domain_index % domain_columns * domain_step
        transform.domain_y = domain_index // domain_columns * domain_step
        transform.symmetry = 0


def _legacy_decode_model_symmetries(reader: LegacyBits,
                                    transforms: list[LegacyTransform],
                                    model: LegacyModel) -> None:
    """Decode one model's columnar symmetry side channel."""
    symmetry_bits = (model.symmetry_count - 1).bit_length()
    for transform in transforms:
        symmetry_delta = (
            0 if model.symmetry_count == 1 else reader.read(symmetry_bits)
        )
        if symmetry_delta >= model.symmetry_count:
            raise FormatError("legacy FIF symmetry symbol exceeds its model alphabet")
        transform.symmetry += model.symmetry_base + symmetry_delta


def _legacy_decode_model_affines(reader: LegacyBits,
                                 transforms: list[LegacyTransform],
                                 model: LegacyModel) -> None:
    """Decode one model's columnar affine side channel."""
    affine_bits = (model.affine_count - 1).bit_length()
    for transform in transforms:
        affine_delta = 0 if model.affine_count == 1 else reader.read(affine_bits)
        if affine_delta >= model.affine_count:
            raise FormatError("legacy FIF affine symbol exceeds its model alphabet")
        transform.affine = model.affine_base + affine_delta
        if not 0 <= transform.symmetry <= 15 or not 0 <= transform.affine <= 255:
            raise FormatError("legacy FIF model produces an invalid transform parameter")


def _legacy_decode_component(header: LegacyFIF, region: LegacyRegion,
                             component: int, readers: list[LegacyBits],
                             models_by_level: tuple[tuple[LegacyModel, ...], ...]) \
        -> list[LegacyTransform]:
    subsampled = component != 0
    # A 2:1-subsampled FIF1 chroma component reaches unit-sized ranges one
    # level before luminance.  The following luminance-only level has no
    # chroma payload; treating it as another chroma subdivision both creates
    # zero-sized ranges and advances into the next restart stream.
    component_levels = header.levels - (1 if subsampled else 0)
    encoded_domain_step = (
        header.luminance_domain_step if component == 0
        else header.chroma_domain_step
    )
    # Coordinates in an unpacked FIF transform are stored at half-pixel
    # precision for E and quarter-pixel precision for the subsampled U/V
    # planes.  The domain-grid cardinality, however, is calculated using the
    # encoded (pre-scaling) step.
    domain_step = encoded_domain_step // (4 if subsampled else 2)
    if domain_step == 0:
        raise FormatError("legacy FIF domain step collapses to zero")
    full_scale = 1 << header.initial_exponent
    domain_columns = (region.width - 1) // encoded_domain_step + 1
    domain_rows = (region.height - 1) // encoded_domain_step + 1
    domain_count = domain_columns * domain_rows
    domain_bits = (domain_count - 1).bit_length()
    working_width = region.width // 2 if subsampled else region.width
    working_height = region.height // 2 if subsampled else region.height
    coordinate_step = full_scale // 4 if subsampled else full_scale // 2
    expected = region.width // full_scale * (region.height // full_scale)
    parents = [
        LegacyTransform(x, y)
        for y in range(0, working_height // 2, coordinate_step)
        for x in range(0, working_width // 2, coordinate_step)
    ]
    if (len(parents) != expected or expected == 0 or
            expected > header.aggregate_transform_limit):
        raise FormatError("legacy FIF region has inconsistent transform capacity")
    if expected & 3:
        raise FormatError("legacy FIF base transform count is not four-aligned")

    output: list[LegacyTransform] = []
    for level in range(component_levels):
        reader = readers[level]
        range_size = 1 << (header.initial_exponent - level)
        doubled_range = range_size * 2
        range_code = (range_size // 1) * 2
        if subsampled:
            range_code //= 2
            range_size //= 2

        split: list[LegacyTransform]
        grouped: dict[int, list[LegacyTransform]] = {}
        applicable = _legacy_component_models(models_by_level[level], component)
        if level == 0:
            split = parents
        elif not applicable:
            split = parents
        else:
            mapping: list[int | None] = [None]
            mapping.extend(index for index, _ in applicable)
            assignments: list[int] = []
            for _ in range(len(parents) // 4):
                packed = _legacy_selection_symbol(reader, doubled_range)
                assignments.extend((packed >> shift) & 3 for shift in (0, 2, 4, 6))
            split = []
            for parent, assignment in zip(parents, assignments):
                if assignment >= len(mapping):
                    raise FormatError("legacy FIF model-selection symbol is out of range")
                model_index = mapping[assignment]
                if model_index is None:
                    split.append(parent)
                else:
                    transform = LegacyTransform(
                        parent.range_x, parent.range_y,
                        range_code=range_code, level_value=parent.level_value,
                    )
                    grouped.setdefault(model_index, []).append(transform)

        if level == 0:
            columns = region.width // full_scale
            if columns == 0 or len(split) % columns:
                raise FormatError("legacy FIF level-zero prediction grid is invalid")
            table_kind = 0 if component == 0 else 1
            for index, transform in enumerate(split):
                if index == 0:
                    predictor = 0x80
                elif index < columns:
                    predictor = split[index - 1].level_value
                else:
                    predictor = split[index - columns].level_value
                transform.level_value = _clamp_10bit(
                    predictor - _legacy_intensity_symbol(reader, table_kind)
                )
            parents = split
        else:
            if component == 0:
                table_kind = 2 if (1 << (header.initial_exponent - level)) < 3 else 0
            else:
                full_range = 1 << (header.initial_exponent - level)
                table_kind = 1 if full_range in (8, 16) else (0 if full_range == 4 else 2)
            modified_range = 1 << (header.initial_exponent - level)
            if subsampled:
                modified_range //= 2
            if modified_range == 1:
                for parent in split:
                    parent.range_x *= 2
                    parent.range_y *= 2
            child_half = modified_range // 2
            if modified_range == 1:
                child_half = 1
            children: list[LegacyTransform] = []
            for parent in split:
                children.extend(
                    _legacy_split_children(parent, child_half, reader, table_kind)
                )
            parents = children
            if level == component_levels - 1:
                for transform in parents:
                    transform.constant = True

        # The legacy stream is columnar across the whole level: every model's
        # domains, then every model's symmetries, then every model's affines.
        # Within each column, models use descriptor order.
        for model_index in sorted(grouped):
            transforms = grouped[model_index]
            model = models_by_level[level][model_index]
            for transform in transforms:
                _legacy_decode_domain_position(
                    reader, transform, model,
                    range_size, doubled_range,
                    domain_step, domain_columns, domain_bits,
                )
        for model_index in sorted(grouped):
            _legacy_decode_model_symmetries(
                reader, grouped[model_index], models_by_level[level][model_index]
            )
        for model_index in sorted(grouped):
            _legacy_decode_model_affines(
                reader, grouped[model_index], models_by_level[level][model_index]
            )
        # The unpacked record array is grouped in descriptor order.  Local
        # transforms subsequently retain this order for dependency sorting.
        for model_index in sorted(grouped):
            output.extend(grouped[model_index])
        if level == component_levels - 1:
            output.extend(parents)

    if parents and header.levels == 0:
        raise FormatError("legacy FIF has no progressive transform levels")
    return output


def _legacy_decode_region(header: LegacyFIF, region: LegacyRegion,
                          coverage: list[tuple[int, int]] | None = None) \
        -> tuple[tuple[list[LegacyTransform], ...], tuple[LegacyBits, ...]]:
    # Version-1 FIF progressive tile streams intentionally overlap at fine
    # levels.  Offsets are restart points, not segment boundaries.  The final
    # restart is terminated by an implicit all-zero entropy tail; the original
    # decoder implements this by word lookahead beyond the declared buffer.
    # The aggregate transform-limit field supplies a strict finite upper
    # bound for the implicit zero extension.
    virtual_end = len(header.data) + header.aggregate_transform_limit * 16 + 32
    readers = [
        LegacyBits(header.data, start, virtual_end, virtual_zero_tail=True)
        for start in region.offsets
    ]
    models = tuple(
        _legacy_decode_models(header, level, coverage)
        for level in range(header.levels)
    )
    component_count = 3 if header.color else 1
    decoded = tuple(
        _legacy_decode_component(header, region, component, readers, models)
        for component in range(component_count)
    )
    if len(decoded[0]) > header.primary_transform_limit:
        raise FormatError("legacy FIF primary transform limit is exceeded")
    if sum(map(len, decoded)) > header.aggregate_transform_limit:
        raise FormatError("legacy FIF aggregate transform limit is exceeded")
    if coverage is not None:
        coverage.extend(
            (reader.start * 8, min(reader.position, len(header.data) * 8))
            for reader in readers
        )
    return decoded, tuple(readers)


def _legacy_validate_payload_coverage(
        header: LegacyFIF, intervals: list[tuple[int, int]]) -> None:
    """Account for decoded intervals and offset-delimited restart slack."""
    start = header.header_size * 8
    end = len(header.data) * 8
    merged: list[list[int]] = []
    for first, last in sorted(intervals):
        first = max(first, start)
        last = min(last, end)
        if last <= first:
            continue
        if merged and first <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], last)
        else:
            merged.append([first, last])
    # Gaps between these intervals are restart slack.  Their bytes have no
    # prescribed value and the reference decoder intentionally skips them.
    # Computing the union here makes that accounting explicit; the directory
    # and declared-size checks already bound every decoded interval and gap.
    if merged and (merged[0][0] < start or merged[-1][1] > end):
        raise FormatError("legacy FIF decoded interval leaves the payload")


LEGACY_CONTRAST = tuple(range(0x8000, 0x20000, 0x2000)) + (0x2000,)


def _legacy_contrast_value(affine: int, level_value: int,
                           sample: int, mean: int,
                           four_sample_sum: bool) -> int:
    """Apply the FIF1 block-mean-normalized contrast transform."""
    if not 0 <= affine < len(LEGACY_CONTRAST) or not 0 <= level_value <= 255:
        raise FormatError("legacy FIF affine/intensity value is outside its table")
    delta = ((sample - mean + 2) >> 2) if four_sample_sum else sample - mean
    scaled = (delta * LEGACY_CONTRAST[affine] + 0x8000) >> 16
    return _clamp_10bit(level_value + scaled)


def _legacy_special_order(transforms: list[LegacyTransform], width: int,
                          height: int, scale: int) -> list[LegacyTransform]:
    """Reproduce the FIF1 local-domain dependency ordering."""
    ordered = [transform for transform in transforms if transform.symmetry & 8]
    active = len(ordered)
    while active > 8:
        mask = bytearray(width * height)
        for index in range(active - 1, -1, -1):
            transform = ordered[index]
            side = transform.range_code * scale // 2
            for row in range(side):
                y = min(max(transform.domain_y * scale + row, 0), height - 1)
                start_x = transform.domain_x * scale
                for column in range(side):
                    x = min(max(start_x + column, 0), width - 1)
                    mask[y * width + x] = 1
        dependent = bytearray(active)
        dependent_count = 0
        for index in range(active - 1, -1, -1):
            transform = ordered[index]
            side = transform.range_code * scale // 2
            found = False
            for row in range(side):
                y = min(max(transform.range_y * scale + row, 0), height - 1)
                for column in range(side):
                    x = min(max(transform.range_x * scale + column, 0), width - 1)
                    if mask[y * width + x]:
                        found = True
                        break
                if found:
                    break
            dependent[index] = found
            dependent_count += found

        # The reference decoder uses an in-place two-ended partition here,
        # rather than a stable partition.  The resulting order matters because
        # local-domain transforms read pixels written by earlier transforms.
        first = 0
        last = active - 1
        while first < last:
            if not dependent[first]:
                while first < last and not dependent[last]:
                    last -= 1
                if first == last:
                    break
                ordered[first], ordered[last] = ordered[last], ordered[first]
                dependent[first], dependent[last] = dependent[last], dependent[first]
                last -= 1
            first += 1
        new_active = dependent_count
        if new_active == active:
            break
        active = new_active

    # The final reference pass is a reverse-direction overlap sort.
    for end in range(active - 1, 0, -1):
        for index in range(end - 1, -1, -1):
            later = ordered[end]
            earlier = ordered[index]
            side = earlier.range_code * scale // 2
            if (later.range_x * scale < earlier.range_x * scale + side and
                    later.range_y * scale < earlier.range_y * scale + side):
                ordered[index], ordered[end] = later, earlier
    return ordered


def _legacy_sample(source: bytearray, width: int, height: int,
                   x: int, y: int) -> int:
    # The decoder's working allocation includes a replicated boundary apron.
    # Express it explicitly so malformed coordinates cannot read unrelated
    # process memory as the original unchecked implementation could.
    x = min(max(x, 0), width - 1)
    y = min(max(y, 0), height - 1)
    return source[y * width + x]


def _legacy_transform_block(
        source: bytearray, output: bytearray, source_width: int,
        source_height: int, target_width: int, target_height: int,
        transform: LegacyTransform, side: int, target_scale: int,
        domain_scale: int, box_reduce: bool) -> None:
    samples: list[int] = []
    for row in range(side):
        for column in range(side):
            source_y, source_x = _transformed_coord(
                transform.symmetry & 7, row, column, side
            )
            source_x = transform.domain_x * domain_scale + source_x * (2 if box_reduce else 1)
            source_y = transform.domain_y * domain_scale + source_y * (2 if box_reduce else 1)
            if box_reduce:
                sample = sum(
                    _legacy_sample(
                        source, source_width, source_height,
                        source_x + delta_x, source_y + delta_y,
                    )
                    for delta_y in (0, 1) for delta_x in (0, 1)
                )
            else:
                sample = _legacy_sample(
                    source, source_width, source_height, source_x, source_y
                )
            samples.append(sample)
    mean = (sum(samples) + len(samples) // 2) // len(samples)
    range_x = transform.range_x * target_scale
    range_y = transform.range_y * target_scale
    if (range_x < 0 or range_y < 0 or
            range_x + side > target_width or range_y + side > target_height):
        raise FormatError("legacy FIF range block leaves its reconstruction tile")
    for ordinal, sample in enumerate(samples):
        row, column = divmod(ordinal, side)
        output[(range_y + row) * target_width + range_x + column] = (
            _legacy_contrast_value(
                transform.affine, transform.level_value,
                sample, mean, box_reduce,
            )
        )


def _legacy_render_region(region: LegacyRegion, component: int,
                          transforms: list[LegacyTransform]) -> bytearray:
    divisor = 1 if component == 0 else 2
    width = region.width // divisor
    height = region.height // divisor
    half_width = width // 2
    half_height = height // 2
    if not transforms or half_width == 0 or half_height == 0:
        raise FormatError("legacy FIF reconstruction tile is empty")

    half = bytearray(half_width * half_height)
    half_coverage = bytearray(len(half))
    constants: list[LegacyTransform] = []
    ordinary: list[LegacyTransform] = []
    for transform in transforms:
        if transform.constant:
            constants.append(transform)
            continue
        if not 0 <= transform.affine < len(LEGACY_CONTRAST):
            raise FormatError("legacy FIF affine selector is outside its table")
        if transform.range_code not in (2, 4, 8, 16):
            raise FormatError("legacy FIF transform has an invalid range code")
        side = transform.range_code // 2
        if (transform.range_x < 0 or transform.range_y < 0 or
                transform.range_x + side > half_width or
                transform.range_y + side > half_height):
            raise FormatError("legacy FIF half-resolution range leaves its tile")
        value = bytes((transform.level_value,)) * side
        for row in range(side):
            start = (transform.range_y + row) * half_width + transform.range_x
            half[start:start + side] = value
            half_coverage[start:start + side] = b"\x01" * side
        ordinary.append(transform)

    if len(constants) & 3:
        raise FormatError("legacy FIF finest constants are not grouped in fours")
    for index in range(0, len(constants), 4):
        group = constants[index:index + 4]
        anchor = group[0]
        x = anchor.range_x // 2
        y = anchor.range_y // 2
        if not 0 <= x < half_width or not 0 <= y < half_height:
            raise FormatError("legacy FIF finest constant leaves its tile")
        half[y * half_width + x] = (sum(item.level_value for item in group) >> 2)
        half_coverage[y * half_width + x] = 1
    if 0 in half_coverage:
        raise FormatError("legacy FIF transforms do not cover the half-resolution tile")

    special = _legacy_special_order(ordinary, half_width, half_height, 1)
    normal = [transform for transform in ordinary if not transform.symmetry & 8]
    for _ in range(4):
        output = bytearray(half)
        for transform in normal:
            side = transform.range_code // 2
            if side > 1:
                _legacy_transform_block(
                    half, output, half_width, half_height,
                    half_width, half_height, transform, side, 1, 1, True,
                )
        for transform in special:
            side = transform.range_code // 2
            if side > 1:
                _legacy_transform_block(
                    output, output, half_width, half_height,
                    half_width, half_height, transform, side, 1, 1, False,
                )
        half = output

    full = bytearray(width * height)
    coverage = bytearray(len(full))
    for transform in normal:
        side = transform.range_code
        _legacy_transform_block(
            half, full, half_width, half_height,
            width, height, transform, side, 2, 1, False,
        )
        for row in range(side):
            start = (transform.range_y * 2 + row) * width + transform.range_x * 2
            coverage[start:start + side] = b"\x01" * side
    for transform in constants:
        x, y = transform.range_x, transform.range_y
        if not 0 <= x < width or not 0 <= y < height:
            raise FormatError("legacy FIF full-resolution constant leaves its tile")
        full[y * width + x] = transform.level_value
        coverage[y * width + x] = 1
    for transform in special:
        side = transform.range_code
        _legacy_transform_block(
            full, full, width, height, width, height,
            transform, side, 2, 2, False,
        )
        for row in range(side):
            start = (transform.range_y * 2 + row) * width + transform.range_x * 2
            coverage[start:start + side] = b"\x01" * side
    if 0 in coverage:
        raise FormatError("legacy FIF transforms do not cover the full-resolution tile")
    return full


def _legacy_render_plane(
        header: LegacyFIF, component: int,
        region_transforms: list[tuple[LegacyRegion, list[LegacyTransform]]]) \
        -> bytearray:
    divisor = 1 if component == 0 else 2
    width = header.canvas_width // divisor
    height = header.canvas_height // divisor
    plane = bytearray(width * height)
    for region, transforms in region_transforms:
        tile = _legacy_render_region(region, component, transforms)
        tile_width = region.width // divisor
        tile_height = region.height // divisor
        origin_x = region.x // divisor
        origin_y = region.y // divisor
        for row in range(tile_height):
            source = row * tile_width
            target = (origin_y + row) * width + origin_x
            plane[target:target + tile_width] = tile[source:source + tile_width]
    return plane


def _decode_legacy_fif(data: bytes) -> tuple[int, int, bytes]:
    header = _parse_legacy_fif(data)
    coverage: list[tuple[int, int]] = []
    per_component: list[list[tuple[LegacyRegion, list[LegacyTransform]]]] = [
        [] for _ in range(3 if header.color else 1)
    ]
    for region in header.regions:
        decoded, _ = _legacy_decode_region(header, region, coverage)
        for component, transforms in enumerate(decoded):
            per_component[component].append((region, transforms))
    _legacy_validate_payload_coverage(header, coverage)

    # Restart windows are deliberately non-partitioning: a fine-level window
    # may overlap its successor or terminate before it.  The global offsets
    # delimit the physical level payloads, while the per-region offsets are
    # independently decodable entry points into those payloads.

    planes = [
        _legacy_render_plane(header, component, transforms)
        for component, transforms in enumerate(per_component)
    ]
    if not header.color:
        rgb = bytearray(header.canvas_width * header.canvas_height * 3)
        for index, value in enumerate(planes[0]):
            rgb[index * 3:index * 3 + 3] = bytes((value, value, value))
    else:
        width, height = header.canvas_width, header.canvas_height
        packed = bytearray(width * height * 3 // 2)
        packed[:width * height] = planes[0]
        chroma = width * height
        half_width = width // 2
        half_height = height // 2
        for y in range(half_height):
            source_row = y * half_width
            target_row = chroma + y * width
            for x in range(half_width):
                source = source_row + x
                packed[target_row + x] = planes[1][source]
                packed[target_row + half_width + x] = planes[2][source]
        rgb = bytearray(packed_euv_to_rgb(packed, width, height))
    cropped = _crop_rgb(
        rgb, header.canvas_width, header.output_width,
        header.output_height,
    )
    return header.output_width, header.output_height, cropped


def _png_chunk(chunk_type: bytes, payload: bytes) -> bytes:
    body = chunk_type + payload
    return (
        struct.pack(">I", len(payload))
        + body
        + struct.pack(">I", binascii.crc32(body) & 0xFFFFFFFF)
    )


def make_png(width: int, height: int, pixels: bytes) -> bytes:
    expected = width * height * 3
    if len(pixels) != expected:
        raise RuntimeError(f"internal raster has {len(pixels)} bytes; expected {expected}")
    row_bytes = width * 3
    compressor = zlib.compressobj(level=9)
    compressed = bytearray()
    for offset in range(0, len(pixels), row_bytes):
        compressed.extend(compressor.compress(b"\x00" + pixels[offset:offset + row_bytes]))
    compressed.extend(compressor.flush())
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", ihdr)
        + _png_chunk(b"IDAT", bytes(compressed))
        + _png_chunk(b"IEND", b"")
    )


def _video_source_coordinate(mode: int, x: int, y: int) -> tuple[int, int]:
    """Map one output sample to its even-positioned 8-by-8 domain sample."""
    if mode == 0:
        return y * 2, 6 - x * 2
    if mode == 1:
        return 6 - x * 2, 6 - y * 2
    if mode == 2:
        return 6 - y * 2, x * 2
    if mode == 3:
        return 6 - x * 2, y * 2
    if mode == 4:
        return 6 - y * 2, 6 - x * 2
    if mode == 5:
        return x * 2, 6 - y * 2
    if mode == 6:
        return y * 2, x * 2
    if mode == 7:
        return x * 2, y * 2
    raise RuntimeError(f"internal invalid P.OEM symmetry {mode}")


class _FTCVideoDecoder:
    """Strict P.OEM Video 2.0 FTC grayscale/color reconstruction state."""

    def __init__(self, width: int, height: int, color: bool,
                 compact_affine: bool = False):
        self.width = width
        self.height = height
        self.color = color
        self.compact_affine = compact_affine
        self.total_blocks = width * height * (3 if color else 2) // 32
        self.plane_size = width * height
        self.buffer_size = self.plane_size * (3 if color else 2) // 2
        self.current = bytearray([0xAB]) * self.buffer_size
        self.scratch = bytearray([0xAB]) * self.buffer_size
        if color:
            self.palette = bytearray(256 * 3)
        else:
            self.palette = bytearray(
                component for value in range(256) for component in (value, value, value)
            )
        self.palette_lookup: bytes | None = None
        self.palette_base = 4

    def _block_offset(self, block: int) -> int:
        blocks_across = self.width // 4
        return (block // blocks_across) * self.width * 4 + (block % blocks_across) * 4

    def _copy_motion_block(self, block: int, motion: int) -> None:
        destination = self._block_offset(block)
        source = destination + motion
        if source < 0 or source + self.width * 3 + 4 > self.buffer_size:
            raise FormatError(f"P.OEM motion source is outside the frame at block {block}")
        for row in range(4):
            dst = destination + row * self.width
            src = source + row * self.width
            self.scratch[dst:dst + 4] = self.current[src:src + 4]

    def _affine_block(self, bits: Bits, block: int, mode: int) -> None:
        source_x = bits.read(7 if self.compact_affine else 8) * 2
        source_y = bits.read(7) * 2
        # The decoder's 64-KiB lookup is ordered from -128 through +127,
        # while the stored byte selects its 256-byte page without sign
        # extension.  Thus page zero means -128 and page 255 means +127.
        if self.compact_affine:
            bias = bits.read(7) - 64
            adjustment = bias * 4
        else:
            bias = bits.read(8) - 128
            adjustment = bias * 2
        source = source_y * self.width + source_x
        if source + self.width * 6 + 7 >= self.buffer_size:
            raise FormatError(f"P.OEM affine source is outside the frame at block {block}")

        destination = self._block_offset(block)
        for y in range(4):
            dst = destination + y * self.width
            for x in range(4):
                sx, sy = _video_source_coordinate(mode, x, y)
                value = ((self.current[source + sy * self.width + sx] * 3 + 2) >> 2)
                self.scratch[dst + x] = max(0, min(255, value + adjustment))

    @staticmethod
    def _read_run(bits: Bits) -> int:
        if bits.read(1) == 0:
            return 1
        if bits.read(1) == 0:
            return bits.read(4) + 2
        if bits.read(1) == 0:
            return bits.read(6) + 18
        return bits.read(12)

    def _decode_iteration(self, compressed: bytes) -> int:
        bits = Bits(compressed)
        motion_offsets = [0]
        for _ in range(6):
            code = bits.read(8)
            if code >= len(VIDEO_MOTION_DELTAS):
                raise FormatError(f"undefined P.OEM motion-offset code {code}")
            dx, dy = VIDEO_MOTION_DELTAS[code]
            motion_offsets.append(dy * self.width + dx)

        block = 0
        while block < self.total_blocks:
            mode = bits.read(4)
            if mode < 8:
                self._affine_block(bits, block, mode)
                block += 1
            elif mode < 15:
                count = self._read_run(bits)
                if count == 0 or block + count > self.total_blocks:
                    raise FormatError(
                        f"P.OEM motion run crosses the block raster at block {block}"
                    )
                motion = motion_offsets[mode - 8]
                for current_block in range(block, block + count):
                    self._copy_motion_block(current_block, motion)
                block += count
            else:
                code = bits.read(6)
                if code >= len(VIDEO_MOTION_DELTAS):
                    raise FormatError(f"undefined P.OEM single-motion code {code}")
                dx, dy = VIDEO_MOTION_DELTAS[code]
                self._copy_motion_block(block, dy * self.width + dx)
                block += 1

        self.current, self.scratch = self.scratch, self.current
        return bits.position

    def _update_palette(self, record: bytes) -> None:
        if len(record) < 2:
            raise FormatError("truncated P.OEM palette record")
        count = _u16(record, 0)
        if count != 126 or len(record) != 2 + count * 9:
            raise FormatError("invalid P.OEM 126-entry palette record")
        payload = record[2:]
        rgb = payload[:count * 3]
        if any(value > 63 for value in rgb):
            raise FormatError("P.OEM VGA palette component exceeds six bits")

        base = self.palette_base
        for index in range(count):
            source = index * 3
            target = (base + index) * 3
            for component in range(3):
                value = rgb[source + component]
                self.palette[target + component] = (value << 2) | (value >> 4)

        bounds = [
            payload[(3 + plane) * count:(4 + plane) * count]
            for plane in range(6)
        ]
        if any(value > 31 for plane in bounds for value in plane):
            raise FormatError("P.OEM palette-cube coordinate exceeds five bits")

        lookup = bytearray(1 << 15)
        covered = bytearray(1 << 15)
        for index in range(count):
            red_low, green_low, blue_low = (bounds[j][index] for j in range(3))
            red_high, green_high, blue_high = (
                bounds[j][index] for j in range(3, 6)
            )
            if (
                red_low > red_high
                or green_low > green_high
                or blue_low > blue_high
            ):
                raise FormatError("reversed P.OEM palette-cube interval")
            palette_index = base + index
            for green in range(green_low, green_high + 1):
                for red in range(red_low, red_high + 1):
                    start = (green << 10) | (red << 5) | blue_low
                    stop = start + blue_high - blue_low + 1
                    if any(covered[start:stop]):
                        raise FormatError("overlapping P.OEM palette-cube intervals")
                    lookup[start:stop] = bytes([palette_index]) * (stop - start)
                    covered[start:stop] = b"\x01" * (stop - start)
        if 0 in covered:
            raise FormatError("P.OEM palette cubes do not cover 15-bit RGB space")
        self.palette_lookup = bytes(lookup)
        self.palette_base = 130 if base == 4 else 4

    def decode_record(self, payload: bytes) -> tuple[bytes, bytes]:
        if len(payload) < 10:
            raise FormatError("P.OEM frame payload is too short")
        flags = _u16(payload, 0)
        allowed_flags = 7 if self.compact_affine else (3 if self.color else 1)
        if flags & ~allowed_flags:
            raise FormatError(f"unsupported P.OEM frame flags 0x{flags:04x}")
        compressed = payload[2:]
        iterations = 16 if flags & 1 else 1
        consumed_bits = -1
        for _ in range(iterations):
            position = self._decode_iteration(compressed)
            if consumed_bits < 0:
                consumed_bits = position
            elif position != consumed_bits:
                raise RuntimeError("P.OEM iterations consumed different bit counts")

        aligned_bytes = ((consumed_bits + 15) // 16) * 2
        padding = aligned_bytes * 8 - consumed_bits
        if padding:
            verifier = Bits(compressed)
            verifier.position = consumed_bits
            verifier.require_zero(padding, "P.OEM frame-alignment bits")
        cursor = 2 + aligned_bytes
        if flags & 2:
            if cursor + 2 > len(payload):
                raise FormatError("P.OEM frame omits its palette record")
            count = _u16(payload, cursor)
            end = cursor + 2 + count * 9
            if end > len(payload):
                raise FormatError("truncated P.OEM frame palette")
            self._update_palette(payload[cursor:end])
            cursor = end
        if cursor != len(payload):
            raise FormatError("bytes remain after the P.OEM frame record")
        if self.color and self.palette_lookup is None:
            raise FormatError("P.OEM video emits a frame before its first palette")
        return self._indexed_frame(), bytes(self.palette)

    def _indexed_frame(self) -> bytes:
        if not self.color:
            return bytes(self.current[:self.plane_size])
        lookup = self.palette_lookup
        if lookup is None:
            raise RuntimeError("internal P.OEM palette is missing")
        result = bytearray(self.plane_size)
        chroma = self.plane_size
        half_width = self.width // 2
        for y in range(self.height):
            green_row = y * self.width
            color_row = chroma + (y // 2) * self.width
            for x in range(self.width):
                green = self.current[green_row + x]
                red = self.current[color_row + x // 2]
                blue = self.current[color_row + half_width + x // 2]
                result[green_row + x] = lookup[
                    ((green >> 3) << 10)
                    | ((red >> 3) << 5)
                    | (blue >> 3)
                ]
        return bytes(result)


def _gif_literal_lzw(indices: bytes) -> bytes:
    """Encode a GIF image with fixed nine-bit literal runs and frequent clears."""
    clear_code = 256
    end_code = 257
    accumulator = 0
    bit_count = 0
    packed = bytearray()

    def emit(code: int) -> None:
        nonlocal accumulator, bit_count
        accumulator |= code << bit_count
        bit_count += 9
        while bit_count >= 8:
            packed.append(accumulator & 0xFF)
            accumulator >>= 8
            bit_count -= 8

    position = 0
    while position < len(indices):
        emit(clear_code)
        end = min(position + 250, len(indices))
        for value in indices[position:end]:
            emit(value)
        position = end
    emit(end_code)
    if bit_count:
        packed.append(accumulator & 0xFF)

    blocks = bytearray((8,))
    for offset in range(0, len(packed), 255):
        block = packed[offset:offset + 255]
        blocks.append(len(block))
        blocks.extend(block)
    blocks.append(0)
    return bytes(blocks)


def _parse_video_header(data: bytes) -> tuple[int, int, int, str, bool]:
    if len(data) < 66:
        raise FormatError("file is shorter than the 66-byte P.OEM video header")
    if len(data) > MAX_FILE_SIZE:
        raise FormatError("file exceeds the P.OEM signed 32-bit size limit")
    if data[:8] not in FTC_VIDEO_SIGNATURES:
        raise FormatError("signature is not an FTC 1.1 P.OEM video profile")
    color = data[:8] == FTC_VIDEO_COLOR_SIGNATURE
    width = _u16(data, 8)
    height = _u16(data, 10)
    if (width, height) not in ((160, 100), (160, 120), (256, 160)):
        raise FormatError(f"unsupported P.OEM video dimensions {width}x{height}")
    title_field = data[28:64]
    terminator = title_field.find(0)
    if terminator < 0:
        raise FormatError("P.OEM video title field has no NUL terminator")
    frame_rate = data[64]
    if not 1 <= frame_rate <= 30:
        raise FormatError(f"invalid P.OEM frame rate {frame_rate}")
    return width, height, frame_rate, title_field[:terminator].decode("cp437"), color


def make_video_gif(data: bytes) -> bytes:
    width, height, frame_rate, _title, color = _parse_video_header(data)
    records: list[tuple[int, int]] = []
    cursor = 66
    while cursor < len(data):
        if cursor + 2 > len(data):
            raise FormatError("truncated P.OEM frame-length word")
        length = _u16(data, cursor)
        frame_index = len(records)
        cursor += 2
        if length < 10 or length & 1 or cursor + length > len(data):
            raise FormatError(f"invalid P.OEM frame length {length} at frame {frame_index}")
        flags = _u16(data, cursor)
        allowed_flags = 3 if color else 1
        if flags & ~allowed_flags:
            raise FormatError(f"unsupported P.OEM frame flags 0x{flags:04x}")
        records.append((cursor, cursor + length))
        cursor += length
    if not records:
        raise FormatError("P.OEM video contains no frames")
    expected_first_flags = 3 if color else 1
    if _u16(data, records[0][0]) != expected_first_flags:
        description = "fractal frame with a palette" if color else "fractal frame"
        raise FormatError(f"first P.OEM frame is not a {description}")

    decoder = _FTCVideoDecoder(width, height, color)
    output = bytearray(b"GIF89a")
    output.extend(struct.pack("<HHBBB", width, height, 0xF7, 0, 0))
    output.extend(b"\x00" * (256 * 3))
    output.extend(b"\x21\xFF\x0BNETSCAPE2.0\x03\x01\x00\x00\x00")

    for frame_index, (start, end) in enumerate(records):
        payload = data[start:end]
        indices, palette = decoder.decode_record(payload)

        start_tick = (frame_index * 100 + frame_rate // 2) // frame_rate
        end_tick = ((frame_index + 1) * 100 + frame_rate // 2) // frame_rate
        delay = max(1, end_tick - start_tick)
        output.extend(b"\x21\xF9\x04\x04")
        output.extend(struct.pack("<HBB", delay, 0, 0))
        output.extend(b"\x2C\x00\x00\x00\x00")
        output.extend(struct.pack("<HHB", width, height, 0x87))
        output.extend(palette)
        output.extend(_gif_literal_lzw(indices))
    output.extend(b"\x3B")
    return bytes(output)


def _parse_fjf_video_header(data: bytes) -> tuple[int, int, int, int, str, int]:
    """Parse the generation-2 compact-affine FJF video header."""
    if len(data) < 66:
        raise FormatError("file is shorter than the 66-byte FJF video header")
    if len(data) > MAX_FILE_SIZE:
        raise FormatError("file exceeds the FJF signed 32-bit size limit")
    if data[:8] != FJF_VIDEO_SIGNATURE:
        raise FormatError("signature is not FTC 2.2 video profile 0x0202")
    width = _u16(data, 8)
    height = _u16(data, 10)
    if (width, height) != (256, 160):
        raise FormatError(f"unsupported FJF video dimensions {width}x{height}")
    title_field = data[28:60]
    terminator = title_field.find(0)
    if terminator < 0:
        raise FormatError("FJF video title field has no NUL terminator")
    frame_limit = _u32(data, 60)
    if frame_limit == 0:
        raise FormatError("FJF video frame-limit field is zero")
    frame_rate = data[64]
    if not 1 <= frame_rate <= 30:
        raise FormatError(f"invalid FJF frame rate {frame_rate}")
    return (
        width, height, frame_limit, frame_rate,
        title_field[:terminator].decode("cp437"), data[65],
    )


def make_fjf_video_gif(data: bytes) -> bytes:
    width, height, frame_limit, frame_rate, _title, _encoder_field = (
        _parse_fjf_video_header(data)
    )
    records: list[tuple[int, int]] = []
    cursor = 66
    while cursor < len(data):
        if cursor + 2 > len(data):
            raise FormatError("truncated FJF frame-length word")
        length = _u16(data, cursor)
        frame_index = len(records)
        cursor += 2
        if length < 10 or length & 1 or cursor + length > len(data):
            raise FormatError(
                f"invalid or truncated FJF frame length {length} at frame {frame_index}"
            )
        flags = _u16(data, cursor)
        expected_flags = (3,) if frame_index == 0 else (4, 6)
        if flags not in expected_flags:
            raise FormatError(
                f"unsupported FJF frame flags 0x{flags:04x} at frame {frame_index}"
            )
        records.append((cursor, cursor + length))
        cursor += length
    if not records:
        raise FormatError("FJF video contains no frames")
    # The header stores the exclusive terminal frame number.  Record numbering
    # begins at one, so a complete stream has terminal = record count + one.
    if frame_limit != len(records) + 1:
        raise FormatError(
            f"FJF terminal frame number {frame_limit} does not match "
            f"{len(records)} physical frames"
        )

    decoder = _FTCVideoDecoder(width, height, True, compact_affine=True)
    output = bytearray(b"GIF89a")
    output.extend(struct.pack("<HHBBB", width, height, 0xF7, 0, 0))
    output.extend(b"\x00" * (256 * 3))
    output.extend(b"\x21\xFF\x0BNETSCAPE2.0\x03\x01\x00\x00\x00")

    for frame_index, (start, end) in enumerate(records):
        indices, palette = decoder.decode_record(data[start:end])
        start_tick = (frame_index * 100 + frame_rate // 2) // frame_rate
        end_tick = ((frame_index + 1) * 100 + frame_rate // 2) // frame_rate
        delay = max(1, end_tick - start_tick)
        output.extend(b"\x21\xF9\x04\x04")
        output.extend(struct.pack("<HBB", delay, 0, 0))
        output.extend(b"\x2C\x00\x00\x00\x00")
        output.extend(struct.pack("<HHB", width, height, 0x87))
        output.extend(palette)
        output.extend(_gif_literal_lzw(indices))
    output.extend(b"\x3B")
    return bytes(output)


def decode(data: bytes,
           template_directories: tuple[Path, ...] = ()) -> tuple[int, int, bytes]:
    if data[:4] == b"FIF\x01":
        return _decode_legacy_fif(data)
    if data[:4] == b"FTC\x00" and len(data) >= 6 and data[5] == 3:
        return _decode_modern_profile1(data, template_directories)
    if data[:8] in FTC_VIDEO_SIGNATURES:
        raise FormatError(
            "FTC 1.1 P.OEM profile is video; use convert() to produce animated GIF"
        )
    if data[:8] == FJF_VIDEO_SIGNATURE:
        raise FormatError(
            "FTC 2.2 profile 0x0202 is FJF video; use convert() to produce animated GIF"
        )
    if (data[:8] == b"FTC\x00\x01\x01\x02\x01" and len(data) >= 20
            and _u32(data, 16) == 112):
        _reject_missing_early_template(data, template_directories)
    width, height, domain_step, payload = validate_header(data)
    records = parse_payload(payload, width, height, domain_step)
    packed = reconstruct(records, width, height)
    transform_filter(records, packed, width, height)
    return width, height, packed_yuv_to_rgb(packed, width, height)


def convert(input_path: Path, output_path: Path) -> None:
    if input_path.resolve() == output_path.resolve():
        raise OSError("input and output paths must be different")
    output_parent = output_path.resolve().parent
    if not output_parent.is_dir():
        raise OSError(f"output directory does not exist: {output_parent}")

    # No output is opened until the complete input has validated and decoded.
    # External FTT sidecars belong beside the FIF that references them.  The
    # loader matches the referenced basename case-insensitively.
    data = input_path.read_bytes()
    if data[:8] in FTC_VIDEO_SIGNATURES:
        encoded = make_video_gif(data)
    elif data[:8] == FJF_VIDEO_SIGNATURE:
        encoded = make_fjf_video_gif(data)
    else:
        width, height, pixels = decode(data, (input_path.resolve().parent,))
        encoded = make_png(width, height, pixels)

    temporary: Path | None = None
    descriptor = -1
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{output_path.name}.", suffix=".tmp", dir=output_parent
        )
        temporary = Path(temporary_name)
        with os.fdopen(descriptor, "wb") as stream:
            descriptor = -1
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, 0o664)
        os.replace(temporary, output_path)
        temporary = None
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(f"Usage: {Path(argv[0]).name} <inputFile> <outputFile>", file=sys.stderr)
        return 2
    try:
        convert(Path(argv[1]), Path(argv[2]))
    except (FormatError, OSError, RuntimeError, MemoryError, OverflowError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

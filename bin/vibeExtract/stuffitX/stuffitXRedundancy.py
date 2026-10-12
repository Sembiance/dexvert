# Vibe coded by Codex
"""Decode and validate the interleaved Reed-Solomon archive wrapper.

This implements intact codewords, not repair of damaged or missing records.
The framing and GF(256) parameters were recovered from the sample archives.
"""

from functools import lru_cache
import zlib


@lru_cache(maxsize=1)
def _multipliers():
    powers = []
    value = 1
    for _ in range(255):
        powers.append(value)
        value <<= 1
        if value & 256:
            value ^= 0x187
    logs = {value: index for index, value in enumerate(powers)}
    powers *= 2
    return tuple(bytes([0] + [powers[logs[value] + root] for value in range(1, 256)])
                 for root in range(255))


def _check_parity(matrix, width, symbols):
    # Each column is one RS(255, symbols) codeword. Evaluate all columns
    # together using byte translation for GF multiplication and integer XOR.
    rows = [int.from_bytes(matrix[pos:pos + width], 'little')
            for pos in range(0, len(matrix), width)]
    for table in _multipliers()[symbols:]:
        syndrome = 0
        for row in rows:
            product = syndrome.to_bytes(width, 'little').translate(table)
            syndrome = int.from_bytes(product, 'little') ^ row
        if syndrome:
            raise ValueError("Redundancy Reed-Solomon parity mismatch (repair not supported)")


def unwrap_redundancy(data):
    """Consume all framing, padding and parity, returning the element bytes."""
    output = bytearray()
    pos = 0
    final = False
    while pos < len(data):
        if final:
            raise ValueError("Trailing redundancy data after partial group")
        if len(data) - pos < 16:
            raise ValueError("Truncated redundancy group header")
        if data[pos] != 0xb2:
            raise ValueError("Missing redundancy group header")
        params = data[pos + 4:pos + 12]
        width = int.from_bytes(params[:3], 'big')
        used = int.from_bytes(params[3:6], 'big')
        symbols, tail = params[6:]
        if (not width or width % 4 or not 1 <= used <= width
                or not 1 <= symbols <= 254 or tail >= symbols):
            raise ValueError("Invalid redundancy group parameters")
        records = width // 4
        required = records * 1029 + ((records + 7) // 8) * 8
        if required > len(data) - pos:
            raise ValueError("Truncated redundancy group")
        matrix = bytearray()
        for index in range(records):
            full = index % 8 == 0
            header_size = 16 if full else 8
            marker = 0xb2 if full else 0xb1
            if data[pos] != marker:
                raise ValueError("Invalid redundancy record marker")
            if int.from_bytes(data[pos + 1:pos + 4], 'big') != index:
                raise ValueError("Out-of-order redundancy record")
            if full and data[pos + 4:pos + 12] != params:
                raise ValueError("Inconsistent redundancy group parameters")
            crc = int.from_bytes(data[pos + header_size - 4:pos + header_size], 'big')
            if zlib.crc32(data[pos + 1:pos + header_size - 4]) != crc:
                raise ValueError("Redundancy header CRC-32 mismatch")
            start = pos + header_size
            end = start + 1020
            if data[end] != 0xb3:
                raise ValueError("Invalid redundancy record terminator")
            matrix.extend(data[start:end])
            pos = end + 1

        _check_parity(matrix, width, symbols)
        decoded = b''.join(matrix[column:width * symbols:width] for column in range(width))
        size = used * symbols if not tail else (used - 1) * symbols + tail
        # Unused cells need not be zero; they are still covered by RS parity.
        output.extend(decoded[:size])
        final = size < width * symbols
    if not output:
        raise ValueError("Empty redundancy wrapper")
    return bytes(output)

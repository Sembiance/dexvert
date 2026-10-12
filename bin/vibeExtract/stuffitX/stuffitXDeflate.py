# Vibe coded by Codex
"""Bounded StuffIt X DEFLATE decoding, including multi-block streams.

Format reference: RFC 1951 and XADMaster's XADDeflateHandle.m.
Copyright (c) 2017-present, MacPaw Way Ltd. All rights reserved.
This module is licensed under LGPL-2.1-or-later, without any warranty.
See LICENSE-XADMaster.txt. StuffIt X uses six HDIST bits.
"""


class _Bits:
    def __init__(self, data):
        self.data = data
        self.pos = 0
        self.value = 0
        self.count = 0

    def fill(self, count):
        while self.count < count and self.pos < len(self.data):
            self.value |= self.data[self.pos] << self.count
            self.count += 8
            self.pos += 1

    def read(self, count):
        self.fill(count)
        if self.count < count:
            raise ValueError("Truncated Deflate stream")
        value = self.value & ((1 << count) - 1)
        self.value >>= count
        self.count -= count
        return value

    def stored(self):
        self.read(self.count % 8)
        length = self.read(16)
        if self.read(16) != length ^ 0xffff:
            raise ValueError("Invalid Deflate stored-block length")
        # A Huffman lookup may have prefetched bytes from this stored block.
        start = self.pos - self.count // 8
        end = start + length
        if end > len(self.data):
            raise ValueError("Truncated Deflate stored block")
        self.pos, self.value, self.count = end, 0, 0
        return self.data[start:end]

    def finish(self):
        consumed = (self.pos * 8 - self.count + 7) // 8
        if consumed != len(self.data):
            raise ValueError("Trailing Deflate data")


class _Huffman:
    def __init__(self, lengths):
        self.width = max(lengths, default=0)
        if self.width > 15 or any(length < 0 for length in lengths):
            raise ValueError("Invalid Deflate Huffman length")
        counts = [0] * (self.width + 1)
        for length in lengths:
            if length:
                counts[length] += 1
        codes = [0] * (self.width + 1)
        code = 0
        for length in range(1, self.width + 1):
            code = (code + counts[length - 1]) << 1
            if code + counts[length] > 1 << length:
                raise ValueError("Oversubscribed Deflate Huffman tree")
            codes[length] = code

        self.table = [0] * (1 << self.width)
        self.mask = len(self.table) - 1
        for symbol, length in enumerate(lengths):
            if not length:
                continue
            code = codes[length]
            codes[length] += 1
            reverse = 0
            for _ in range(length):
                reverse = (reverse << 1) | (code & 1)
                code >>= 1
            self.table[reverse::1 << length] = [symbol << 4 | length] * (1 << (self.width - length))

    def read(self, bits):
        bits.fill(self.width)
        entry = self.table[bits.value & self.mask]
        length = entry & 15
        if not length:
            raise ValueError("Invalid Deflate Huffman code")
        if bits.count < length:
            raise ValueError("Truncated Deflate Huffman code")
        bits.value >>= length
        bits.count -= length
        return entry >> 4


_ORDER = (16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15)
_FIXED_LITERAL = _Huffman([8] * 144 + [9] * 112 + [7] * 24 + [8] * 8)
_FIXED_DISTANCE = _Huffman([5] * 32)
_LENGTH_BASE = (3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 17, 19, 23, 27,
                31, 35, 43, 51, 59, 67, 83, 99, 115, 131, 163, 195, 227, 258)


def _dynamic(bits):
    literals = bits.read(5) + 257
    distances = bits.read(6) + 1
    metas = bits.read(4) + 4
    if literals > 286:
        raise ValueError("Invalid Deflate literal count")
    lengths = [0] * 19
    for symbol in _ORDER[:metas]:
        lengths[symbol] = bits.read(3)
    meta = _Huffman(lengths)
    lengths = []
    total = literals + distances
    while len(lengths) < total:
        symbol = meta.read(bits)
        if symbol < 16:
            lengths.append(symbol)
            continue
        if symbol == 16:
            if not lengths:
                raise ValueError("Deflate repeat has no previous length")
            value, count = lengths[-1], bits.read(2) + 3
        elif symbol == 17:
            value, count = 0, bits.read(3) + 3
        else:
            value, count = 0, bits.read(7) + 11
        if count > total - len(lengths):
            raise ValueError("Deflate code-length repeat exceeds alphabet")
        lengths.extend([value] * count)
    if not lengths[256]:
        raise ValueError("Deflate tree has no end-of-block code")
    return _Huffman(lengths[:literals]), _Huffman(lengths[literals:])


def decompress_deflate(block_data, output_size):
    """Decode the complete stream, refusing to exceed the output capacity."""
    if not block_data:
        raise ValueError("Truncated Deflate header")
    if block_data[0] != 15:
        raise ValueError(f"Unsupported Deflate window size {block_data[0]}")
    if output_size < 0:
        raise ValueError("Invalid Deflate output capacity")
    bits = _Bits(block_data[1:])
    output = bytearray()
    final = False
    while not final:
        final = bits.read(1)
        kind = bits.read(2)
        if kind == 0:
            stored = bits.stored()
            if len(stored) > output_size - len(output):
                raise ValueError("Deflate stored block exceeds output capacity")
            output.extend(stored)
            continue
        if kind == 1:
            literals, distances = _FIXED_LITERAL, _FIXED_DISTANCE
        elif kind == 2:
            literals, distances = _dynamic(bits)
        else:
            raise ValueError("Reserved Deflate block type")

        while True:
            symbol = literals.read(bits)
            if symbol < 256:
                if len(output) >= output_size:
                    raise ValueError("Deflate literal exceeds output capacity")
                output.append(symbol)
            elif symbol == 256:
                break
            else:
                if symbol > 285:
                    raise ValueError("Reserved Deflate length code")
                extra = (symbol - 261) // 4 if 265 <= symbol <= 284 else 0
                length = _LENGTH_BASE[symbol - 257] + bits.read(extra)
                code = distances.read(bits)
                if code > 29:
                    raise ValueError("Reserved Deflate distance code")
                if code < 4:
                    distance = code + 1
                else:
                    extra = code // 2 - 1
                    distance = ((2 + (code & 1)) << extra) + 1 + bits.read(extra)
                if distance > len(output):
                    raise ValueError("Deflate match precedes output history")
                if length > output_size - len(output):
                    raise ValueError("Deflate match exceeds output capacity")
                start = len(output) - distance
                match = output[start:start + length]
                if length > distance:
                    match = (match * ((length + distance - 1) // distance))[:length]
                output.extend(match)
    bits.finish()
    return bytes(output)

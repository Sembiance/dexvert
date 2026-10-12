#!/usr/bin/env python3
# Vibe coded by Codex
# Vibe coded by Claude
"""
stuffitX.py - StuffIt X (.sitx/.sit) archive extractor

Usage: python3 stuffitX.py <inputFile> [outputDir]

Extracts files from StuffIt X archives. Supports compression methods:
  - Brimstone (PPMd variant G)
  - Cyanide (BWT + range coder)
  - Darkhorse (LZSS + range coder)
  - Deflate (StuffIt X variant)
  - Blend (multi-algorithm)
  - RC4 (obfuscation)
  - Iron (advanced BWT) [listed, not encountered in samples]

Preprocessing filters: English, x86. Unsupported filters are rejected.
Reed-Solomon archive wrappers are unpacked and their parity is verified.
Decoded lengths and available CRC-32 checksums are verified before writing.
"""

import sys
import os
import struct
import ctypes
import zlib
import datetime
import shutil

from stuffitXEnglish import unfilter_english
from stuffitXDeflate import decompress_deflate
from stuffitXRedundancy import unwrap_redundancy

# ─────────────────────────────────────────────────────────────────────
# BitReader - matches CSHandle bit/byte semantics exactly
# ─────────────────────────────────────────────────────────────────────

class BitReader:
    """Reads bits LSB-first, matching CSHandle semantics from XADMaster."""

    def __init__(self, data):
        self.data = data if isinstance(data, (bytes, bytearray, memoryview)) else bytes(data)
        self.byte_pos = 0
        self.bit_buf = 0
        self.bits_left = 0
        self.bitoffs = -1

    def _check_invalidate(self):
        if self.byte_pos != self.bitoffs:
            self.bits_left = 0

    def read_bits_le(self, count):
        res = 0
        done = 0
        while done < count:
            self._check_invalidate()
            if self.bits_left == 0:
                if self.byte_pos >= len(self.data):
                    raise EOFError(f"EOF at byte {self.byte_pos}")
                self.bit_buf = self.data[self.byte_pos]
                self.byte_pos += 1
                self.bitoffs = self.byte_pos
                self.bits_left = 8
            num = min(count - done, self.bits_left)
            res |= (((self.bit_buf >> (8 - self.bits_left)) & ((1 << num) - 1)) << done)
            done += num
            self.bits_left -= num
        return res

    def flush(self):
        self.bits_left = 0

    def offset_in_file(self):
        return self.byte_pos

    def skip_bytes(self, n):
        if n < 0 or self.byte_pos + n > len(self.data):
            raise EOFError(f"Truncated data at byte {self.byte_pos} (need {n} bytes)")
        self.byte_pos += n

    def seek(self, pos):
        self.byte_pos = pos

    # Raw byte-level reads (bypass bit buffer)
    def read_uint8_raw(self):
        val = self.data[self.byte_pos]
        self.byte_pos += 1
        return val

    def read_uint32_be_raw(self):
        val = struct.unpack('>I', self.data[self.byte_pos:self.byte_pos + 4])[0]
        self.byte_pos += 4
        return val

    def read_bytes_raw(self, n):
        if n < 0 or self.byte_pos + n > len(self.data):
            raise EOFError(f"Truncated data at byte {self.byte_pos} (need {n} bytes)")
        val = self.data[self.byte_pos:self.byte_pos + n]
        self.byte_pos += n
        return bytes(val)

    # Bit-level multi-byte reads (like ReadSitxUInt32/ReadSitxUInt64)
    def read_uint32_be_bits(self):
        val = 0
        for _ in range(4):
            val = (val << 8) | self.read_bits_le(8)
        return val

    def read_uint64_be_bits(self):
        val = 0
        for _ in range(8):
            val = (val << 8) | self.read_bits_le(8)
        return val

    def read_data_bits(self, n):
        return bytes(self.read_bits_le(8) for _ in range(n))


# ─────────────────────────────────────────────────────────────────────
# P2 Variable-Length Integer Encoding
# ─────────────────────────────────────────────────────────────────────

def read_p2(br):
    """Read a SitxP2 variable-length integer."""
    n = 1
    while br.read_bits_le(1) == 1 and n < 64:
        n += 1
    if n >= 64:
        raise ValueError("P2 overflow")
    value = 0
    bit = 1
    while n > 0:
        if br.read_bits_le(1) == 1:
            n -= 1
            value |= bit
        bit <<= 1
    return value - 1


def read_sitx_string(br):
    """Read a P2-length-prefixed string (byte-level after length)."""
    length = read_p2(br)
    data = br.read_bytes_raw(length)
    br.flush()
    return data


# ─────────────────────────────────────────────────────────────────────
# Element Parsing
# ─────────────────────────────────────────────────────────────────────

ELEM_NAMES = {
    0: "end", 1: "data", 2: "file", 3: "fork", 4: "directory",
    5: "catalog", 6: "clue", 7: "root", 8: "boundary", 9: "unknown9",
    10: "receipt", 11: "index", 12: "locator", 13: "id", 14: "link",
    15: "segment_index"
}

COMP_NAMES = {
    -1: "none", 0: "Brimstone", 1: "Cyanide", 2: "Darkhorse",
    3: "Deflate", 4: "Blend", 5: "RC4", 6: "Iron"
}


def read_element(br):
    """Parse a StuffIt X element header."""
    something = br.read_bits_le(1)
    elem_type = read_p2(br)

    attribs = [-1] * 10
    while True:
        atype = read_p2(br)
        if atype == 0:
            break
        aval = read_p2(br)
        if 1 <= atype <= 10:
            attribs[atype - 1] = aval

    alglist = [-1] * 6
    alglist3_extra = -1
    while True:
        atype = read_p2(br)
        if atype == 0:
            break
        aval = read_p2(br)
        if 1 <= atype <= 6:
            alglist[atype - 1] = aval
        if atype == 4:
            alglist3_extra = read_p2(br)

    return {
        'something': something,
        'type': elem_type,
        'attribs': attribs,
        'alglist': alglist,
        'alglist3_extra': alglist3_extra,
        'dataoffset': br.offset_in_file(),
        'actualsize': 0,
        'datacrc': None,
    }


def scan_element_data(br, elem):
    """Scan data blocks and CRC, updating elem. Returns (total_bytes, block_list)."""
    br.seek(elem['dataoffset'])
    br.flush()

    total = 0
    blocks = []
    while True:
        blen = read_p2(br)
        if blen == 0:
            break
        offset = br.offset_in_file()
        br.skip_bytes(blen)
        total += blen
        blocks.append((offset, blen))

    br.flush()
    crc_len = read_p2(br)

    if crc_len == 0:
        pass
    elif crc_len == 4:
        elem['datacrc'] = br.read_uint32_be_raw()
        crc_len = read_p2(br)
        while crc_len:
            br.skip_bytes(crc_len)
            crc_len = read_p2(br)
    else:
        br.skip_bytes(crc_len)
        crc_len = read_p2(br)
        while crc_len:
            br.skip_bytes(crc_len)
            crc_len = read_p2(br)

    return total, blocks


def extract_block_data(data, blocks):
    """Extract raw bytes from data blocks."""
    result = bytearray()
    for offset, length in blocks:
        result.extend(data[offset:offset + length])
    return bytes(result)


# ─────────────────────────────────────────────────────────────────────
# PPMd Brimstone Decompressor (via compiled C library)
# ─────────────────────────────────────────────────────────────────────

_decomp_lib = None

def get_decomp_lib():
    """Load the combined C decompressor library."""
    global _decomp_lib
    if _decomp_lib is None:
        for name in ['libsitx_decomp.so', 'libppmd_sitx.so']:
            lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
            if not os.path.exists(lib_path):
                lib_path = os.path.join('/tmp', name)
            if os.path.exists(lib_path):
                try:
                    _decomp_lib = ctypes.CDLL(lib_path)
                    break
                except OSError:
                    continue
        if _decomp_lib is None:
            raise RuntimeError("Cannot load decompressor library (libsitx_decomp.so)")

        _decomp_lib.ppmd_brimstone_decompress.restype = ctypes.c_int
        _decomp_lib.ppmd_brimstone_decompress.argtypes = [
            ctypes.c_char_p, ctypes.c_size_t,
            ctypes.c_char_p, ctypes.c_size_t,
            ctypes.c_int, ctypes.c_int
        ]

        if hasattr(_decomp_lib, 'cyanide_decompress'):
            _decomp_lib.cyanide_decompress.restype = ctypes.c_int
            _decomp_lib.cyanide_decompress.argtypes = [
                ctypes.c_char_p, ctypes.c_size_t,
                ctypes.c_char_p, ctypes.c_size_t
            ]

    return _decomp_lib


def decompress_brimstone(compressed_data, output_size, max_order, alloc_size):
    """Decompress PPMd Brimstone data."""
    lib = get_decomp_lib()
    output = ctypes.create_string_buffer(output_size)
    result = lib.ppmd_brimstone_decompress(
        compressed_data, len(compressed_data),
        output, output_size,
        max_order, alloc_size
    )
    if result < 0:
        raise ValueError("PPMd Brimstone decompression failed")
    return output.raw[:result]


# ─────────────────────────────────────────────────────────────────────
# RC4 Decompressor
# ─────────────────────────────────────────────────────────────────────

def rc4_decrypt(data, key):
    """RC4 stream cipher."""
    s = list(range(256))
    j = 0
    for i in range(256):
        j = (j + s[i] + key[i % len(key)]) & 255
        s[i], s[j] = s[j], s[i]

    i = j = 0
    result = bytearray(len(data))
    for n in range(len(data)):
        i = (i + 1) & 255
        j = (j + s[i]) & 255
        s[i], s[j] = s[j], s[i]
        result[n] = data[n] ^ s[(s[i] + s[j]) & 255]
    return bytes(result)


def decompress_rc4(block_data):
    """Decompress RC4-obfuscated data (algo 5). First 3 bytes: skip 2, key = byte 3."""
    if len(block_data) < 3:
        raise ValueError("Truncated RC4 header")
    key = bytes([block_data[2]])
    return rc4_decrypt(block_data[3:], key)


# ─────────────────────────────────────────────────────────────────────
# Carryless Range Coder (Python port)
# ─────────────────────────────────────────────────────────────────────

class ByteStream:
    """Simple byte stream for feeding range coder."""
    def __init__(self, data):
        self.data = data
        self.pos = 0

    def next_byte(self):
        if self.pos >= len(self.data):
            raise EOFError("Truncated compressed stream")
        b = self.data[self.pos]
        self.pos += 1
        return b

    def next_uint32_be(self):
        val = 0
        for _ in range(4):
            val = (val << 8) | self.next_byte()
        return val


class CarrylessRangeCoder:
    """Carryless range coder, ported from XADMaster."""

    def __init__(self, stream, uselow=True, bottom=0x10000):
        self.stream = stream
        self.low = 0
        self.code = stream.next_uint32_be()
        self.range = 0xFFFFFFFF
        self.uselow = uselow
        self.bottom = bottom

    def _mask32(self):
        self.low &= 0xFFFFFFFF
        self.code &= 0xFFFFFFFF
        self.range &= 0xFFFFFFFF

    def current_count(self, scale):
        if scale <= 0:
            raise ValueError("Invalid range-coder scale")
        self.range = (self.range // scale) & 0xFFFFFFFF
        if not self.range:
            raise ValueError("Invalid range-coder interval")
        count = ((self.code - self.low) & 0xFFFFFFFF) // self.range
        if count >= scale:
            raise ValueError("Range-coder count out of bounds")
        return count

    def remove_subrange(self, lowcount, highcount):
        if self.uselow:
            self.low = (self.low + self.range * lowcount) & 0xFFFFFFFF
        else:
            self.code = (self.code - self.range * lowcount) & 0xFFFFFFFF
        self.range = (self.range * (highcount - lowcount)) & 0xFFFFFFFF
        self.normalize()

    def normalize(self):
        while True:
            test = (self.low ^ ((self.low + self.range) & 0xFFFFFFFF)) & 0xFFFFFFFF
            if test >= 0x1000000:
                if self.range >= self.bottom:
                    break
                else:
                    self.range = ((-self.low) & 0xFFFFFFFF) & (self.bottom - 1)
            self.code = ((self.code << 8) | self.stream.next_byte()) & 0xFFFFFFFF
            self.range = (self.range << 8) & 0xFFFFFFFF
            self.low = (self.low << 8) & 0xFFFFFFFF

    def next_symbol(self, freqtable):
        total = sum(freqtable)
        tmp = self.current_count(total)
        cumul = 0
        n = 0
        while n < len(freqtable) - 1 and cumul + freqtable[n] <= tmp:
            cumul += freqtable[n]
            n += 1
        self.remove_subrange(cumul, cumul + freqtable[n])
        return n

    def next_bit(self):
        bit = self.current_count(2)
        if bit == 0:
            self.remove_subrange(0, 1)
        else:
            self.remove_subrange(1, 2)
        return bit

    def next_weighted_bit2(self, weight, shift):
        if not 0 < weight < (1 << shift) or self.code >= self.range:
            raise ValueError("Invalid weighted range-coder interval")
        threshold = ((self.range >> shift) * weight) & 0xFFFFFFFF
        if not threshold:
            raise ValueError("Empty weighted range-coder interval")
        if self.code < threshold:
            self.range = threshold
            self.normalize()
            return 0
        else:
            self.range = (self.range - threshold) & 0xFFFFFFFF
            self.code = (self.code - threshold) & 0xFFFFFFFF
            self.normalize()
            return 1


# ─────────────────────────────────────────────────────────────────────
# BWT (Burrows-Wheeler Transform) Unsort
# ─────────────────────────────────────────────────────────────────────

def unsort_bwt(src, blocklen, firstindex):
    """Inverse BWT transform."""
    counts = [0] * 256
    for i in range(blocklen):
        counts[src[i]] += 1

    cumcounts = [0] * 256
    total = 0
    for i in range(256):
        cumcounts[i] = total
        total += counts[i]

    transform = [0] * blocklen
    for i in range(blocklen):
        transform[cumcounts[src[i]]] = i
        cumcounts[src[i]] += 1

    dest = bytearray(blocklen)
    idx = firstindex
    for i in range(blocklen):
        idx = transform[idx]
        dest[i] = src[idx]

    return bytes(dest)


def decode_m1ffn(block, blocklen, order):
    """M1FFN (Move-1-From-Front-N) decode."""
    data = bytearray(block[:blocklen])
    table = list(range(256))
    lasthead = order - 1

    for i in range(blocklen):
        sym = data[i]
        data[i] = table[sym]
        if sym == 0:
            lasthead = 0
        elif sym == 1:
            if lasthead >= order:
                table[0], table[1] = table[1], table[0]
        else:
            val = table[sym]
            for j in range(sym, 1, -1):
                table[j] = table[j - 1]
            table[1] = val
        lasthead += 1

    return bytes(data)


# ─────────────────────────────────────────────────────────────────────
# Cyanide Decompressor (BWT + Range Coder)
# ─────────────────────────────────────────────────────────────────────

class RangeCoderModel:
    def __init__(self, numsymbols):
        self.num = numsymbols
        self.frequencies = [1] * numsymbols
        self.mapping = list(range(numsymbols - 1, -1, -1))

    def bump_frequency(self, index, maxtotal):
        total = sum(self.frequencies[:self.num])
        if total >= maxtotal:
            for i in range(self.num):
                self.frequencies[i] = (self.frequencies[i] + 1) // 2
        freq = self.frequencies[index]
        last = index
        while last < self.num - 1 and self.frequencies[last + 1] == freq:
            last += 1
        if last != index:
            self.mapping[index], self.mapping[last] = self.mapping[last], self.mapping[index]
        self.frequencies[last] += 1
        return last


def calc_ternary_freqs(infreqs):
    a, b, c = infreqs[0], infreqs[1], infreqs[2]
    # Equal frequencies have format-specific priorities, not stable-sort order.
    if a < b:
        if a < c:
            meanings = [0, 1, 2] if b < c else [0, 2, 1]
        else:
            meanings = [2, 0, 1]
    elif b < c:
        meanings = [1, 2, 0] if c < a else [1, 0, 2]
    else:
        meanings = [2, 1, 0]
    outfreqs = [infreqs[meanings[0]] + 1, infreqs[meanings[1]] + 1, infreqs[meanings[2]] + 1]
    return outfreqs, meanings


_cyanide_lib = None


def get_cyanide_lib():
    """The legacy combined library has an incorrect M1FFN decoder; never use it."""
    global _cyanide_lib
    if _cyanide_lib is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libsitx_cyanide.so')
        try:
            lib = ctypes.CDLL(path)
        except OSError:
            return None
        lib.sitx_cyanide_decompress.restype = ctypes.c_ssize_t
        lib.sitx_cyanide_decompress.argtypes = [
            ctypes.c_char_p, ctypes.c_size_t, ctypes.c_char_p, ctypes.c_size_t
        ]
        _cyanide_lib = lib
    return _cyanide_lib


def decompress_cyanide(block_data, output_size):
    """Decompress Cyanide with the checked native decoder or Python fallback."""
    lib = get_cyanide_lib()
    if lib is not None:
        output = ctypes.create_string_buffer(output_size)
        result = lib.sitx_cyanide_decompress(
            block_data, len(block_data),
            output, output_size
        )
        if result < 0:
            raise ValueError("Cyanide decompression failed")
        return output.raw[:result]
    return decompress_cyanide_python(block_data, output_size)


def decompress_cyanide_python(block_data, output_size):
    """Portable reference implementation, with the same bounds as native code."""
    stream = ByteStream(block_data)
    _something = stream.next_byte()  # skip first byte

    result = bytearray()
    while True:
        marker = stream.next_byte()
        if marker == 0xFF:
            if stream.pos != len(block_data):
                raise ValueError("Trailing Cyanide data")
            break
        if marker != 0x77:
            raise ValueError(f"Invalid Cyanide block marker: 0x{marker:02x}")

        blocksize = stream.next_uint32_be()
        firstindex = stream.next_uint32_be()
        numsymbols = stream.next_byte()
        if not blocksize or firstindex >= blocksize or blocksize > output_size - len(result):
            raise ValueError("Invalid Cyanide block size or BWT index")

        # Ternary coded block decoding with range coder
        markovgroups = [0, 1, 2, 3, 4, 5, 6, 7, 8, 3, 9, 10, 3, 4, 5, 11, 11, 8, 6, 2, 5, 6, 7, 8, 12, 12, 13]
        coder = CarrylessRangeCoder(stream, uselow=True, bottom=0x10000)
        markovfreqs = [[0, 0, 0] for _ in range(14)]

        # Initialize low-bits models
        lowbitsmodels = []
        b = numsymbols
        shift = 1
        while b > 0:
            n = 1 << shift
            if b < (3 << shift):
                n = b
            lowbitsmodels.append(RangeCoderModel(n))
            b -= n
            shift += 1
        highbitmodel = RangeCoderModel(shift)

        sorted_data = bytearray(blocksize)
        prev = prev2 = prev3 = 0
        someflag = 1

        for i in range(blocksize):
            ctx = prev3 * 9 + prev2 * 3 + prev
            midx = markovgroups[ctx]

            freqs, meanings = calc_ternary_freqs(markovfreqs[midx])
            symbol = coder.next_symbol(freqs)
            tresym = meanings[symbol]

            if tresym == 0 and someflag == 0 and midx == 0:
                someflag = 1
                markovfreqs[midx][0] >>= 1
                markovfreqs[midx][1] >>= 1
                markovfreqs[midx][2] >>= 1
                markovfreqs[midx][0] += 3
                sorted_data[i] = 0
            else:
                if tresym != 0:
                    someflag = 0
                total = freqs[0] + freqs[1] + freqs[2]
                limit = 4096 if someflag else 128
                if total > limit:
                    markovfreqs[midx][0] >>= 1
                    markovfreqs[midx][1] >>= 1
                    markovfreqs[midx][2] >>= 1
                markovfreqs[midx][tresym] += 2

                if tresym <= 1:
                    sorted_data[i] = tresym
                else:
                    hbi = coder.next_symbol(highbitmodel.frequencies[:highbitmodel.num])
                    highbit = highbitmodel.mapping[hbi]
                    newi = highbitmodel.bump_frequency(hbi, 0x100)
                    highbitmodel.bump_frequency(newi, 0x10000)

                    if highbit == 0:
                        sorted_data[i] = 2
                    else:
                        lbm = lowbitsmodels[highbit - 1]
                        lbi = coder.next_symbol(lbm.frequencies[:lbm.num])
                        lowbits = lbm.mapping[lbi]
                        maxv = min(lbm.num * 128, 0x4000)
                        lbm.bump_frequency(lbi, maxv)
                        value = (1 << highbit) + lowbits + 1
                        if value > 255:
                            raise ValueError("Invalid Cyanide byte value")
                        sorted_data[i] = value

            prev3 = prev2
            prev2 = prev
            prev = tresym

        # M1FFN decode then BWT unsort
        decoded = decode_m1ffn(sorted_data, blocksize, 2)
        unsorted = unsort_bwt(decoded, blocksize, firstindex)
        result.extend(unsorted)

    return bytes(result[:output_size])


# ─────────────────────────────────────────────────────────────────────
# Darkhorse Decompressor (LZSS + Range Coder)
# ─────────────────────────────────────────────────────────────────────

DARKHORSE_OFFSET_TABLE = [
    0, 1, 2, 3, 4, 6, 8, 0xc,
    0x10, 0x18, 0x20, 0x30, 0x40, 0x60, 0x80, 0xc0,
    0x100, 0x180, 0x200, 0x300, 0x400, 0x600, 0x800, 0xc00,
    0x1000, 0x1800, 0x2000, 0x3000, 0x4000, 0x6000, 0x8000, 0xc000,
    0x10000, 0x18000, 0x20000, 0x30000, 0x40000, 0x60000, 0x80000, 0xc0000,
    0x100000, 0x180000, 0x200000, 0x300000, 0x400000, 0x600000, 0x800000, 0xc00000,
    0x1000000, 0x1800000, 0x2000000, 0x3000000, 0x4000000, 0x6000000, 0x8000000, 0xc000000,
    0x10000000, 0x18000000, 0x20000000, 0x30000000, 0, 0, 0, 0,
]

DARKHORSE_BITLEN_TABLE = [
    0, 0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9,
    10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 16, 16, 17, 17, 18, 18, 19, 19,
    20, 20, 21, 21, 22, 22, 23, 23, 24, 24, 25, 25, 26, 26, 27, 27, 28, 28, 0, 0, 0, 0
]


_darkhorse_lib = None


def get_darkhorse_lib():
    """Never call the unsafe Darkhorse entry point in the legacy library."""
    global _darkhorse_lib
    if _darkhorse_lib is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libsitx_darkhorse.so')
        try:
            lib = ctypes.CDLL(path)
        except OSError:
            return None
        lib.sitx_darkhorse_decompress.restype = ctypes.c_ssize_t
        lib.sitx_darkhorse_decompress.argtypes = [
            ctypes.c_char_p, ctypes.c_size_t, ctypes.c_char_p, ctypes.c_size_t,
            ctypes.c_uint32,
        ]
        _darkhorse_lib = lib
    return _darkhorse_lib


def validate_darkhorse_parameters(block_data, output_size, window_size):
    if len(block_data) < 6:
        raise ValueError("Truncated Darkhorse header")
    if block_data[0] > 30:
        raise ValueError("Unsupported Darkhorse window exponent")
    if window_size != max(1 << block_data[0], 0x100000):
        raise ValueError("Darkhorse window does not match header")
    if not 0 <= output_size <= sys.maxsize:
        raise ValueError("Invalid Darkhorse output capacity")


def decompress_darkhorse(block_data, output_size, window_size):
    """Decode a complete Darkhorse stream, with output_size as a hard limit."""
    validate_darkhorse_parameters(block_data, output_size, window_size)
    lib = get_darkhorse_lib()
    if lib is not None:
        output = ctypes.create_string_buffer(output_size)
        result = lib.sitx_darkhorse_decompress(
            block_data, len(block_data),
            output, output_size,
            window_size
        )
        if result < 0:
            raise ValueError("Invalid, truncated, or oversized Darkhorse stream")
        return output.raw[:result]
    return decompress_darkhorse_python(block_data, output_size, window_size)


def decompress_darkhorse_python(block_data, output_size, window_size):
    """Checked Python implementation, adapted from XADMaster (LGPL-2.1+)."""
    validate_darkhorse_parameters(block_data, output_size, window_size)
    stream = ByteStream(block_data)
    stream.next_byte()  # window exponent
    stream.next_byte()  # separate initialization byte, observed as zero
    coder = CarrylessRangeCoder(stream, uselow=False, bottom=0)
    pos = 0

    flagweights = [0x800] * 4
    flagweight2 = 0x800
    litweights = [[0x800] * 256 for _ in range(16)]
    litweights2 = [[[0x800, 0x800] for _ in range(256)] for _ in range(16)]
    recencyweight1 = 0x800
    recencyweight2 = 0x800
    recencyweight3 = 0x800
    recencyweights = [0x800] * 4
    lenweight = 0x800
    shortweights = [[0x800] * 16 for _ in range(4)]
    longweights = [0x800] * 256
    distlenweights = [[0x800] * 64 for _ in range(4)]
    distweights = [[0x800] * 32 for _ in range(10)]
    distlowbitweights = [0x800] * 16
    distancetable = [0] * 4

    result = bytearray()
    next_guess = -1

    def next_bit_w(weight_list, idx):
        bit = coder.next_weighted_bit2(weight_list[idx], 12)
        if bit == 0:
            weight_list[idx] += (0x1000 - weight_list[idx]) >> 5
        else:
            weight_list[idx] -= weight_list[idx] >> 5
        return bit

    def next_bit_w_single():
        nonlocal flagweight2
        bit = coder.next_weighted_bit2(flagweight2, 12)
        if bit == 0:
            flagweight2 += (0x1000 - flagweight2) >> 5
        else:
            flagweight2 -= flagweight2 >> 5
        return bit

    def read_symbol_w(weights, num):
        val = 1
        for _ in range(num):
            bit = coder.next_weighted_bit2(weights[val], 12)
            if bit == 0:
                weights[val] += (0x1000 - weights[val]) >> 5
            else:
                weights[val] -= weights[val] >> 5
            val = (val << 1) | bit
        return val - (1 << num)

    def read_literal(prev, guess):
        val = 1
        if guess == -1:
            while val < 0x100:
                bit = coder.next_weighted_bit2(litweights[prev // 16][val], 12)
                if bit == 0:
                    litweights[prev // 16][val] += (0x1000 - litweights[prev // 16][val]) >> 5
                else:
                    litweights[prev // 16][val] -= litweights[prev // 16][val] >> 5
                val = (val << 1) | bit
        else:
            g = guess
            while val < 0x100:
                gbit = (g >> 7) & 1
                bit = coder.next_weighted_bit2(litweights2[prev // 16][val][gbit], 12)
                if bit == 0:
                    litweights2[prev // 16][val][gbit] += (0x1000 - litweights2[prev // 16][val][gbit]) >> 5
                else:
                    litweights2[prev // 16][val][gbit] -= litweights2[prev // 16][val][gbit] >> 5
                val = (val << 1) | bit
                if bit != gbit:
                    break
                g = (g << 1) & 0xFF
            while val < 0x100:
                bit = coder.next_weighted_bit2(litweights[prev // 16][val], 12)
                if bit == 0:
                    litweights[prev // 16][val] += (0x1000 - litweights[prev // 16][val]) >> 5
                else:
                    litweights[prev // 16][val] -= litweights[prev // 16][val] >> 5
                val = (val << 1) | bit
        return val & 0xFF

    def read_length(index):
        nonlocal lenweight
        bit = coder.next_weighted_bit2(lenweight, 12)
        if bit == 0:
            lenweight += (0x1000 - lenweight) >> 5
            return read_symbol_w(shortweights[index], 4)
        else:
            lenweight -= lenweight >> 5
            return read_symbol_w(longweights, 8) + 16

    def read_distance(length):
        ln = min(length - 2, 3)
        sym = read_symbol_w(distlenweights[ln], 6)
        if sym >= 60:
            raise ValueError("Reserved Darkhorse distance symbol")
        if sym < 4:
            return sym
        elif sym < 14:
            return DARKHORSE_OFFSET_TABLE[sym] + read_symbol_w(distweights[sym - 4], DARKHORSE_BITLEN_TABLE[sym])
        else:
            numbits = DARKHORSE_BITLEN_TABLE[sym]
            val = 0
            for i in range(numbits - 1, 3, -1):
                val |= coder.next_bit() << i
            return val + DARKHORSE_OFFSET_TABLE[sym] + read_symbol_w(distlowbitweights, 4)

    def read_recency(index):
        nonlocal recencyweight1, recencyweight2, recencyweight3
        bit = coder.next_weighted_bit2(recencyweight1, 12)
        if bit == 0:
            recencyweight1 += (0x1000 - recencyweight1) >> 5
            bit2 = coder.next_weighted_bit2(recencyweights[index], 12)
            if bit2 == 0:
                recencyweights[index] += (0x1000 - recencyweights[index]) >> 5
                return -1
            else:
                recencyweights[index] -= recencyweights[index] >> 5
                return 0
        else:
            recencyweight1 -= recencyweight1 >> 5
            bit2 = coder.next_weighted_bit2(recencyweight2, 12)
            if bit2 == 0:
                recencyweight2 += (0x1000 - recencyweight2) >> 5
                return 1
            else:
                recencyweight2 -= recencyweight2 >> 5
                bit3 = coder.next_weighted_bit2(recencyweight3, 12)
                if bit3 == 0:
                    recencyweight3 += (0x1000 - recencyweight3) >> 5
                    return 2
                else:
                    recencyweight3 -= recencyweight3 >> 5
                    return 3

    def update_dist_mem(oldindex, dist):
        for i in range(oldindex, 0, -1):
            distancetable[i] = distancetable[i - 1]
        distancetable[0] = dist

    # Keep history in the output buffer rather than allocating the entire
    # declared window. References before the beginning address initialized zeroes.
    def history(distance):
        return result[pos - distance] if distance <= pos else 0

    while True:
        pidx = pos & 3
        is_match = next_bit_w(flagweights, pidx)

        if is_match == 0:
            if pos == output_size:
                raise ValueError("Darkhorse output exceeds capacity")
            prev = history(1)
            byte = read_literal(prev, next_guess)
            next_guess = -1
            result.append(byte)
            pos += 1
        else:
            bit2 = next_bit_w_single()
            if bit2 == 0:
                length = read_length(pidx) + 2
                if length == 0x111:
                    if stream.pos != len(block_data):
                        raise ValueError("Trailing Darkhorse data")
                    return bytes(result)
                offs = read_distance(length)
                update_dist_mem(3, offs)
            else:
                recency = read_recency(pidx)
                if recency == -1:
                    offs = distancetable[0]
                    length = 1
                else:
                    offs = distancetable[recency]
                    update_dist_mem(recency, offs)
                    length = read_length(pidx) + 2

            distance = offs + 1
            if distance > window_size:
                raise ValueError("Darkhorse match distance exceeds window")
            if length > output_size - pos:
                raise ValueError("Darkhorse match exceeds output capacity")
            next_guess = history(distance - length % distance)
            for _ in range(length):
                result.append(history(distance))
                pos += 1


# ─────────────────────────────────────────────────────────────────────
# Blend Decompressor (multi-algorithm dispatcher)
# ─────────────────────────────────────────────────────────────────────

def decompress_blend(block_data, output_size):
    """Decompress Blend (multi-algorithm) compressed data."""
    result = bytearray()
    pos = 0

    while len(result) < output_size and pos < len(block_data):
        # Find 0x77 marker followed by algo id 0-3
        while pos < len(block_data) - 5:
            if block_data[pos] == 0x77 and block_data[pos + 1] <= 3:
                break
            pos += 1
        if pos >= len(block_data) - 5:
            break

        algo = block_data[pos + 1]
        size = struct.unpack('>I', block_data[pos + 2:pos + 6])[0]
        pos += 6

        chunk = block_data[pos:pos + size]

        if algo == 0:  # Raw/uncompressed
            result.extend(chunk)
            pos += size
        elif algo == 1:  # Darkhorse
            ws_byte = chunk[0] if chunk else 20
            ws = max(1 << ws_byte, 0x100000)
            decompressed = decompress_darkhorse(chunk, output_size - len(result), ws)
            result.extend(decompressed)
            pos += size
        elif algo == 2:  # Cyanide
            decompressed = decompress_cyanide(chunk, output_size - len(result))
            result.extend(decompressed)
            pos += size
        elif algo == 3:  # Brimstone
            alloc_exp = chunk[0] if chunk else 16
            order = chunk[1] if len(chunk) > 1 else 6
            alloc_size = 1 << alloc_exp
            decompressed = decompress_brimstone(chunk[2:], output_size - len(result), order, alloc_size)
            result.extend(decompressed)
            pos += size

    return bytes(result[:output_size])


# ─────────────────────────────────────────────────────────────────────
# x86 Preprocessing Filter
# ─────────────────────────────────────────────────────────────────────

def unfilter_x86(data):
    """Reverse x86 E8/E9 call/jump address preprocessing."""
    data = bytearray(data)
    lasthit = -6
    bitfield = 0

    i = 0
    while i < len(data):
        b = data[i]
        if b == 0xE8 or b == 0xE9:
            dist = i - lasthit
            lasthit = i
            if dist > 5:
                bitfield = 0
            else:
                for _ in range(dist):
                    bitfield = (bitfield & 0x77) << 1

            if i + 4 < len(data):
                buf = data[i + 1:i + 5]
                table = [True, True, True, False, True, False, False, False]
                if buf[3] == 0x00 or buf[3] == 0xFF:
                    idx = (bitfield >> 1) & 0x07
                    if idx < len(table) and table[idx] and (bitfield >> 1) <= 0x0F:
                        absaddr = struct.unpack('<i', bytes(buf))[0]
                        while True:
                            reladdr = absaddr - i - 6
                            if bitfield == 0:
                                break
                            shifts = [24, 16, 8, 8, 0, 0, 0, 0]
                            shift = shifts[bitfield >> 1] if (bitfield >> 1) < len(shifts) else 0
                            something = (reladdr >> shift) & 0xFF
                            if something != 0 and something != 0xFF:
                                break
                            absaddr = reladdr ^ ((1 << (shift + 8)) - 1)
                        reladdr &= 0x1FFFFFF
                        if reladdr >= 0x1000000:
                            reladdr |= 0xFF000000
                        reladdr &= 0xFFFFFFFF
                        data[i + 1:i + 5] = struct.pack('<I', reladdr)
                        bitfield = 0
                        i += 5
                        continue
                    else:
                        bitfield |= 0x11
                else:
                    bitfield |= 0x01
        i += 1

    return bytes(data)


# ─────────────────────────────────────────────────────────────────────
# Catalog Parser
# ─────────────────────────────────────────────────────────────────────

def parse_catalog(catalog_data, entries):
    """Parse catalog metadata for all entries."""
    br = BitReader(catalog_data)

    for entry in entries:
        while True:
            key = read_p2(br)
            if key == 0:
                break

            if key == 1:  # filename
                entry['filename'] = read_sitx_string(br)
            elif key == 2:  # modification time
                entry['mtime'] = br.read_uint64_be_bits()
            elif key == 3:
                _ = br.read_uint32_be_bits()
            elif key == 4 or key == 5:  # finder info
                finfo = br.read_data_bits(32)
                if finfo[:8] == b'slnkrhap':
                    entry['is_link'] = True
                else:
                    entry['finder_info'] = finfo
            elif key == 6:  # POSIX permissions
                hasowner = br.read_bits_le(8)
                entry['permissions'] = br.read_uint32_be_bits()
                if hasowner:
                    entry['uid'] = br.read_uint32_be_bits()
                    entry['gid'] = br.read_uint32_be_bits()
            elif key == 7:
                _ = read_p2(br)
            elif key == 8:  # creation time
                entry['ctime'] = br.read_uint64_be_bits()
            elif key == 9:  # comment
                entry['comment'] = read_sitx_string(br)
            elif key == 10:
                num = read_p2(br)
                for _ in range(num):
                    br.flush()
                    read_sitx_string(br)
            elif key == 11 or key == 12:
                read_sitx_string(br)
            else:
                raise ValueError(f"Unsupported catalog field {key}")

        br.flush()

    if br.offset_in_file() != len(catalog_data):
        raise ValueError("Unconsumed catalog bytes")


def filetime_to_datetime(ft):
    """Convert Windows FILETIME (100ns since 1601-01-01) to datetime."""
    if ft <= 0:
        return None
    epoch = datetime.datetime(1601, 1, 1)
    try:
        return epoch + datetime.timedelta(microseconds=ft // 10)
    except (OverflowError, OSError):
        return None


# ─────────────────────────────────────────────────────────────────────
# Main Decompression Dispatcher
# ─────────────────────────────────────────────────────────────────────

def decompress_element(data, elem, blocks):
    """Decode the entire stream, reverse filters, then validate fork bytes."""
    block_data = extract_block_data(data, blocks)
    comp = elem['alglist'][0]
    preproc = elem['alglist'][2]
    checksum = elem['alglist'][1]
    expected_size = elem['actualsize']
    if expected_size < 0:
        raise ValueError("Missing decompressed size")
    if elem['alglist'][3] >= 0:
        raise ValueError("Encrypted elements are not supported")
    if preproc not in (-1, 0, 2):
        raise ValueError(f"Unsupported preprocessing filter {preproc}")
    if checksum not in (-1, 0):
        raise ValueError(f"Unsupported checksum algorithm {checksum}")

    # English changes the size in either direction. Escaped literals need two
    # bytes; dictionary tokens need <=4 for words of >=3 bytes. Add one sentinel
    # byte beyond the maximum encoded size so a truncated decode cannot pass.
    decode_size = 2 * expected_size + 5 if preproc == 0 else expected_size

    if comp == -1:  # No compression
        result = block_data
    elif comp == 0:  # Brimstone/PPMd
        if len(block_data) < 2:
            raise ValueError("Truncated Brimstone header")
        exp_byte, order_byte = block_data[:2]
        if exp_byte > 30 or not 1 <= order_byte <= 64:
            raise ValueError("Unsupported Brimstone parameters")
        alloc_size = 1 << exp_byte
        result = decompress_brimstone(block_data[2:], decode_size, order_byte, alloc_size)
    elif comp == 1:  # Cyanide
        result = decompress_cyanide(block_data, decode_size)
    elif comp == 2:  # Darkhorse
        if not block_data or block_data[0] > 30:
            raise ValueError("Invalid Darkhorse header")
        ws_byte = block_data[0]
        ws = max(1 << ws_byte, 0x100000)
        result = decompress_darkhorse(block_data, decode_size, ws)
    elif comp == 3:  # Deflate
        result = decompress_deflate(block_data, decode_size)
    elif comp == 4:  # Blend
        result = decompress_blend(block_data, decode_size)
    elif comp == 5:  # RC4
        result = decompress_rc4(block_data)
    else:
        raise ValueError(f"Unsupported compression {COMP_NAMES.get(comp, comp)}")

    # Apply preprocessing filter
    if preproc == 0:  # English
        result = unfilter_english(result, expected_size)
    elif preproc == 2:  # x86
        result = unfilter_x86(result)

    if len(result) != expected_size:
        raise ValueError(f"Decoded size mismatch: expected {expected_size}, got {len(result)}")
    if checksum == 0:
        expected_crc = elem.get('datacrc')
        if expected_crc is None:
            raise ValueError("Missing CRC-32 trailer")
        actual_crc = zlib.crc32(result)
        if actual_crc != expected_crc:
            raise ValueError(f"CRC-32 mismatch: expected {expected_crc:08x}, got {actual_crc:08x}")

    return result


# ─────────────────────────────────────────────────────────────────────
# Archive Parser & Extractor
# ─────────────────────────────────────────────────────────────────────

def parse_archive(data):
    """Return the structure and logical bytes to which its block offsets refer."""
    if data[:8] != b'StuffIt!':
        raise ValueError("Not a StuffIt X file (missing magic)")

    br = BitReader(data)
    br.seek(8)

    entries = []        # file/directory entries (ordered)
    entry_dict = {}     # objid -> entry
    stream_forks = {}   # stream_id -> list of fork info
    forked_set = set()  # entry ids that have forks
    elements = []       # all parsed elements

    while True:
        start = br.offset_in_file()
        elem = read_element(br)
        et = elem['type']
        a = elem['attribs']
        elements.append(elem)

        if et == 0:  # end
            if br.offset_in_file() != len(data):
                raise ValueError("Unparsed bytes after end element (unsupported archive layout)")
            break

        elif et == 1:  # data
            total, blocks = scan_element_data(br, elem)
            elem['blocks'] = blocks
            elem['total_block_data'] = total

            # Calculate actual size from forks
            objid = a[0]
            forks = stream_forks.get(objid, [])
            actual = sum(f.get('length', 0) for f in forks if f is not None)
            elem['actualsize'] = actual

        elif et == 2:  # file
            objid = a[0]
            parent = a[1]
            entry = {
                'objid': objid, 'parent': parent, 'is_dir': False,
                'order': a[6] if a[6] >= 0 else len(entries),
            }
            entries.append(entry)
            entry_dict[objid] = entry

        elif et == 3:  # fork
            entry_id = a[1]
            stream_id = a[2]
            index = a[3]
            length = a[4]
            fork_type = read_p2(br)

            forked_set.add(entry_id)

            if stream_id not in stream_forks:
                stream_forks[stream_id] = []
            forks = stream_forks[stream_id]

            finfo = {'entries': [entry_id], 'type': fork_type, 'length': length}

            while len(forks) <= index:
                forks.append(None)
            if forks[index] is None:
                forks[index] = finfo
            else:
                if forks[index]['length'] != length or forks[index]['type'] != fork_type:
                    raise ValueError("Conflicting shared fork references")
                forks[index]['entries'].append(entry_id)

        elif et == 4:  # directory
            objid = a[0]
            parent = a[1]
            entry = {
                'objid': objid, 'parent': parent, 'is_dir': True,
                'order': a[6] if a[6] >= 0 else len(entries),
            }
            entries.append(entry)
            entry_dict[objid] = entry

        elif et == 5:  # catalog
            total, blocks = scan_element_data(br, elem)
            elem['blocks'] = blocks
            elem['actualsize'] = a[4]
            decompressed = decompress_element(data, elem, blocks)
            parse_catalog(decompressed, entries)

        elif et == 6:  # clue
            size = a[4]
            if size >= 0:
                br.skip_bytes(size)

        elif et == 7:  # root
            _ = read_p2(br)
            if elem['alglist'][3] >= 0:
                raise ValueError("Encrypted archives are not supported")
            redundancy = elem['alglist'][4]
            if redundancy >= 0:
                if redundancy != 0 or start != 8:
                    raise ValueError(f"Unsupported archive redundancy algorithm {redundancy}")
                offset = br.offset_in_file()
                data = data[:offset] + unwrap_redundancy(data[offset:])
                br = BitReader(data)
                br.seek(offset)

        elif et == 8:  # boundary
            pass

        elif et == 9:
            pass

        elif et > 10:
            scan_element_data(br, elem)

        br.flush()

    return entries, entry_dict, stream_forks, forked_set, elements, data


def sanitize_filename(name):
    """Sanitize a filename for safe filesystem use."""
    # Remove null bytes and control characters
    name = name.replace('\x00', '').replace('\r', '').replace('\n', '')
    # Replace path separators that aren't our separator
    name = name.replace('/', '_').replace('\\', '_')
    # Replace other problematic characters
    name = name.replace(':', '_')
    if name in ('.', '..'):
        raise ValueError("Unsafe archive filename")
    return name if name else 'unnamed'


def build_path(entry, entry_dict):
    """Build full path for an entry by walking parent chain."""
    parts = []
    current = entry
    visited = set()
    while current:
        oid = current.get('objid', id(current))
        if oid in visited:
            raise ValueError("Cycle in archive directory hierarchy")
        visited.add(oid)
        fname = current.get('filename', b'')
        if isinstance(fname, bytes):
            fname = fname.decode('utf-8', errors='replace')
        fname = sanitize_filename(fname)
        if fname and fname != 'unnamed':
            parts.append(fname)
        parent_id = current.get('parent', -1)
        if parent_id <= 0 or parent_id not in entry_dict:
            break
        current = entry_dict[parent_id]
    parts.reverse()
    return os.path.join(*parts) if parts else ''


def safe_output_path(output_dir, path, allow_leaf_link=False):
    """Do not write through existing symlinks, including on repeated extraction."""
    root = os.path.realpath(output_dir)
    full_path = os.path.abspath(os.path.join(root, path))
    if os.path.commonpath((root, full_path)) != root or full_path == root:
        raise ValueError(f"Unsafe output path: {path}")
    current = full_path
    while current != root:
        if os.path.islink(current) and not (allow_leaf_link and current == full_path):
            raise ValueError(f"Refusing to write through symlink: {current}")
        current = os.path.dirname(current)
    return full_path


def link_target(path, data, output_dir):
    """StuffIt X stores a link's target as its exact, non-NUL-terminated fork."""
    target = os.fsdecode(data)
    if not target or '\x00' in target or os.path.isabs(target):
        raise ValueError(f"Invalid or absolute symbolic link target: {path}")
    relative = os.path.normpath(os.path.join(os.path.dirname(path), target))
    safe_output_path(output_dir, relative, allow_leaf_link=True)
    return target


# ─────────────────────────────────────────────────────────────────────
# MacBinary II Encoder
# ─────────────────────────────────────────────────────────────────────

def _macbinary_crc16(data):
    """CRC-16/CCITT for MacBinary II header (bytes 0-123)."""
    crc = 0
    for byte in data:
        d = byte << 8
        for _ in range(8):
            if (crc ^ d) & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            d <<= 1
        crc &= 0xFFFF
    return crc


def _filetime_to_mac_epoch(ft):
    """Convert Windows FILETIME to Mac OS classic epoch (seconds since 1904-01-01)."""
    if not ft or ft <= 0:
        return 0
    # Windows epoch: 1601-01-01, Mac epoch: 1904-01-01
    # Difference: 9561628800 seconds
    unix_ts = ft / 10_000_000 - 11644473600  # FILETIME -> Unix
    mac_ts = int(unix_ts + 2082844800)       # Unix -> Mac classic
    if mac_ts < 0:
        mac_ts = 0
    return mac_ts & 0xFFFFFFFF


def build_macbinary(filename, data_fork, resource_fork, entry):
    """Build a MacBinary II file from data fork, resource fork, and metadata.

    Returns the complete MacBinary byte string.
    """
    # Encode filename: Mac Roman, max 63 bytes
    if isinstance(filename, bytes):
        fname = filename
    else:
        fname = filename.encode('mac_roman', errors='replace')
    fname = fname[:63]

    header = bytearray(128)

    # Offset 0: old version = 0
    # Offset 1: filename length
    header[1] = len(fname)
    # Offset 2-64: filename padded with zeros
    header[2:2 + len(fname)] = fname

    # Offset 65-68: file type (4 bytes)
    # Offset 69-72: file creator (4 bytes)
    finder_info = entry.get('finder_info', b'\x00' * 32)
    if len(finder_info) >= 8:
        header[65:69] = finder_info[0:4]   # type
        header[69:73] = finder_info[4:8]   # creator
    if len(finder_info) >= 10:
        header[73] = finder_info[8]         # Finder flags high byte

    # Offset 74: zero (already)
    # Offset 75-80: Finder position/window (from finder_info bytes 10-15)
    if len(finder_info) >= 16:
        header[75:81] = finder_info[10:16]

    # Offset 81: protected flag
    # Offset 82: zero (already)

    # Offset 83-86: data fork length (big-endian)
    dflen = len(data_fork) if data_fork else 0
    struct.pack_into('>I', header, 83, dflen)

    # Offset 87-90: resource fork length (big-endian)
    rflen = len(resource_fork) if resource_fork else 0
    struct.pack_into('>I', header, 87, rflen)

    # Offset 91-94: creation date (Mac epoch)
    ctime = _filetime_to_mac_epoch(entry.get('ctime', 0))
    struct.pack_into('>I', header, 91, ctime)

    # Offset 95-98: modification date (Mac epoch)
    mtime = _filetime_to_mac_epoch(entry.get('mtime', 0))
    struct.pack_into('>I', header, 95, mtime)

    # Offset 99-100: Get Info comment length = 0
    # Offset 101: Finder flags low byte
    if len(finder_info) >= 26:
        header[101] = finder_info[24]  # fdFlags low byte (offset 24 in FInfo+FXInfo)

    # Offset 102-105: leave zero (no mBIN signature = MacBinary II not III)
    # Offset 122: version used to upload = 129 (MacBinary II)
    header[122] = 129
    # Offset 123: minimum version to read = 129
    header[123] = 129

    # Offset 124-125: CRC-16 over bytes 0-123
    crc = _macbinary_crc16(header[:124])
    struct.pack_into('>H', header, 124, crc)

    # Build the full file
    result = bytearray(header)

    # Data fork + pad to 128-byte boundary
    if dflen > 0:
        result.extend(data_fork)
        pad = (128 - (dflen % 128)) % 128
        result.extend(b'\x00' * pad)

    # Resource fork + pad to 128-byte boundary
    if rflen > 0:
        result.extend(resource_fork)
        pad = (128 - (rflen % 128)) % 128
        result.extend(b'\x00' * pad)

    return bytes(result)


# ─────────────────────────────────────────────────────────────────────
# Archive Extractor
# ─────────────────────────────────────────────────────────────────────

def extract_archive(input_path, output_dir):
    """Extract a StuffIt X archive."""
    try:
        return _extract_archive(input_path, output_dir)
    except (OSError, ValueError, EOFError) as exc:
        print(f"  ERROR: {exc}")
        return False


def _extract_archive(input_path, output_dir):
    with open(input_path, 'rb') as f:
        data = f.read()

    print(f"Parsing {os.path.basename(input_path)} ({len(data)} bytes)...")

    try:
        entries, entry_dict, stream_forks, forked_set, elements, data = parse_archive(data)
    except Exception as e:
        print(f"  ERROR: Failed to parse archive: {e}")
        return False

    print(f"  Found {len(entries)} entries")

    # Validate every stream before creating any output files or directories.
    # First pass: collect all fork data per entry
    # entry_id -> {'data': bytes, 'rsrc': bytes}
    entry_forks = {}

    for elem in elements:
        if elem['type'] != 1:  # data
            continue

        objid = elem['attribs'][0]
        forks = stream_forks.get(objid, [])

        try:
            decompressed = decompress_element(data, elem, elem.get('blocks', []))
        except Exception as e:
            print(f"  ERROR decompressing stream {objid}: {e}")
            return False

        # Split decompressed data into fork segments and assign to entries
        offset = 0
        for fork in forks:
            if fork is None:
                print(f"  ERROR: Missing fork index in stream {objid}")
                return False

            fork_type = fork['type']
            fork_len = fork['length']
            fork_data = decompressed[offset:offset + fork_len]
            if fork_type not in (0, 1) or len(fork_data) != fork_len:
                print(f"  ERROR: Unsupported or truncated fork in stream {objid}")
                return False

            for entry_id in fork['entries']:
                if entry_id not in entry_forks:
                    entry_forks[entry_id] = {}
                if fork_type == 0:
                    entry_forks[entry_id]['data'] = fork_data
                elif fork_type == 1:
                    entry_forks[entry_id]['rsrc'] = fork_data

            offset += fork_len

    if forked_set.difference(entry_forks):
        print("  ERROR: Missing data streams for one or more files")
        return False

    for entry in entries:
        path = build_path(entry, entry_dict) or f"file_{entry['objid']}"
        safe_output_path(output_dir, path, allow_leaf_link=entry.get('is_link', False))
        if entry.get('is_link'):
            forks = entry_forks.get(entry['objid'], {})
            if 'data' not in forks or forks.get('rsrc'):
                raise ValueError(f"Invalid symbolic link forks: {path}")
            entry['link_target'] = link_target(path, forks['data'], output_dir)

    os.makedirs(output_dir, exist_ok=True)
    for entry in entries:
        if entry.get('is_dir'):
            path = build_path(entry, entry_dict)
            if path:
                os.makedirs(safe_output_path(output_dir, path), exist_ok=True)

    # Write links last so other archive entries can never traverse a new link.
    extracted = 0
    for entry in sorted(entries, key=lambda item: item.get('is_link', False)):
        if entry.get('is_dir'):
            continue

        entry_id = entry.get('objid')
        fdata = entry_forks.get(entry_id, {})
        data_fork = fdata.get('data')
        rsrc_fork = fdata.get('rsrc')

        if data_fork is None and rsrc_fork is None:
            # No fork data at all
            if entry_id not in forked_set:
                # Truly empty file
                path = build_path(entry, entry_dict)
                if path:
                    full_path = safe_output_path(output_dir, path)
                    pdir = os.path.dirname(full_path)
                    if pdir:
                        os.makedirs(pdir, exist_ok=True)
                    if not os.path.isdir(full_path):
                        with open(full_path, 'wb') as f:
                            pass
                        extracted += 1
            continue

        path = build_path(entry, entry_dict)
        if not path:
            path = f"file_{entry_id}"

        full_path = safe_output_path(output_dir, path, allow_leaf_link=entry.get('is_link', False))
        pdir = os.path.dirname(full_path)
        if pdir:
            os.makedirs(pdir, exist_ok=True)

        # Handle case where path exists as a directory
        if not entry.get('is_link') and os.path.isdir(full_path):
            full_path = safe_output_path(output_dir, path + ".data")

        if entry.get('is_link'):
            if os.path.lexists(full_path):
                os.unlink(full_path)
            os.symlink(entry['link_target'], full_path)
            extracted += 1
            print(f"  Extracted: {path} -> {entry['link_target']}")
        elif rsrc_fork:
            # Has a resource fork -> output as MacBinary (no .bin extension)
            fname_part = os.path.basename(path)
            macbin = build_macbinary(
                fname_part,
                data_fork or b'',
                rsrc_fork,
                entry
            )
            with open(full_path, 'wb') as f:
                f.write(macbin)
            dflen = len(data_fork) if data_fork else 0
            rflen = len(rsrc_fork)
            extracted += 1
            print(f"  Extracted: {path} (MacBinary: data={dflen}, rsrc={rflen})")
        elif data_fork is not None:
            # Data fork only -> output raw
            with open(full_path, 'wb') as f:
                f.write(data_fork)
            extracted += 1
            print(f"  Extracted: {path} ({len(data_fork)} bytes)")

        # Set modification time
        mtime = entry.get('mtime')
        if mtime:
            dt = filetime_to_datetime(mtime)
            if dt:
                try:
                    ts = dt.timestamp()
                    os.utime(full_path, (ts, ts), follow_symlinks=False)
                except (OSError, OverflowError):
                    pass

    print(f"  Done: {extracted} files extracted")
    return True


# ─────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <inputFile> [outputDir]")
        sys.exit(1)

    input_path = sys.argv[1]
    if len(sys.argv) >= 3:
        output_dir = sys.argv[2]
    else:
        base = os.path.splitext(os.path.basename(input_path))[0]
        output_dir = base + "_extracted"

    if not os.path.exists(input_path):
        print(f"Error: File not found: {input_path}")
        sys.exit(1)

    success = extract_archive(input_path, output_dir)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# Vibe coded by Claude
"""
unFIZ.py - Extract files from FIZ archives.

Supports two FIZ format variants used by the Maximus BBS installer:

  Old format (ACOPY011a) - Maximus 1.x
    Global directory header followed by concatenated compressed data.
    Compression: LZW by P. Fitzsimmons and B. Trower (1988).

  New format (FIZ\\x1a) - Maximus 2.x / 3.x
    Streaming per-file headers interleaved with compressed data.
    Compression: LH5 (LZSS + static Huffman) from Okumura's ar002.
"""

import sys
import os
import struct

# ============================================================================
# CRC-16 (polynomial 0xA001 = bit-reversed 0x8005, aka CRC-16/ARC)
# ============================================================================
_CRC_POLY = 0xA001

def _make_crctable():
    table = []
    for i in range(256):
        r = i
        for _ in range(8):
            r = (r >> 1) ^ _CRC_POLY if r & 1 else r >> 1
        table.append(r & 0xFFFF)
    return table

_CRC_TABLE = _make_crctable()

def crc16(data, crc=0):
    for b in data:
        crc = _CRC_TABLE[(crc ^ b) & 0xFF] ^ (crc >> 8)
    return crc & 0xFFFF

def decode_dos_datetime(time_val, date_val):
    """Decode DOS packed date/time into a human-readable string."""
    second = (time_val & 0x1F) * 2
    minute = (time_val >> 5) & 0x3F
    hour   = (time_val >> 11) & 0x1F
    day    = date_val & 0x1F
    month  = (date_val >> 5) & 0x0F
    year   = ((date_val >> 9) & 0x7F) + 1980
    return f'{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}'

# ============================================================================
# LZW Decompressor  (old ACOPY format, LSB-first variable-width codes)
# ============================================================================
LZW_CLEAR      = 256
LZW_END        = 257
LZW_FIRST_CODE = 258
LZW_INIT_BITS  = 9
LZW_MAX_BITS   = 13

class _LZWBitReader:
    __slots__ = ('data', 'pos', 'bit_buf', 'bits_in_buf')
    def __init__(self, data):
        self.data = data; self.pos = 0; self.bit_buf = 0; self.bits_in_buf = 0
    def read_code(self, width):
        while self.bits_in_buf < width:
            if self.pos < len(self.data):
                self.bit_buf |= self.data[self.pos] << self.bits_in_buf
                self.pos += 1
            self.bits_in_buf += 8
        code = self.bit_buf & ((1 << width) - 1)
        self.bit_buf >>= width; self.bits_in_buf -= width
        return code

def decompress_lzw(comp_data, orig_size):
    """Decompress LZW data (old ACOPY format)."""
    reader = _LZWBitReader(comp_data)
    code_size = LZW_INIT_BITS; max_code = 1 << LZW_MAX_BITS
    dictionary = {i: bytes([i]) for i in range(256)}
    next_code = LZW_FIRST_CODE; result = bytearray(); old_code = -1
    while len(result) < orig_size:
        code = reader.read_code(code_size)
        if code == LZW_CLEAR:
            dictionary = {i: bytes([i]) for i in range(256)}
            next_code = LZW_FIRST_CODE; code_size = LZW_INIT_BITS; old_code = -1
            continue
        if code == LZW_END:
            break
        if old_code == -1:
            result.append(code); old_code = code; continue
        if code in dictionary:
            entry = dictionary[code]
        elif code == next_code:
            entry = dictionary[old_code] + bytes([dictionary[old_code][0]])
        else:
            raise ValueError(
                f"Invalid LZW code {code} (next_code={next_code}, "
                f"code_size={code_size}, output_pos={len(result)})")
        result.extend(entry)
        if next_code < max_code:
            dictionary[next_code] = dictionary[old_code] + bytes([entry[0]])
            next_code += 1
        if next_code >= (1 << code_size) and code_size < LZW_MAX_BITS:
            code_size += 1
        old_code = code
    return bytes(result[:orig_size])

# ============================================================================
# LH5 Decompressor  (new FIZ format, LZSS + static Huffman, MSB-first bits)
# ============================================================================
_DICBIT    = 13
_DICSIZ    = 1 << _DICBIT   # 8192
_MAXMATCH  = 256
_THRESHOLD = 3
_UCHAR_MAX = 255
_NC        = _UCHAR_MAX + _MAXMATCH + 2 - _THRESHOLD  # 510
_CBIT      = 9
_CODE_BIT  = 16
_NP        = _DICBIT + 1    # 14
_NTT       = _CODE_BIT + 3  # 19
_NPT       = max(_NTT, _NP) # 19
_BITBUFSIZ = 16
_TBIT      = 5
_PBIT      = 4

class _LH5BitReader:
    """MSB-first 16-bit bit buffer matching Okumura's fillbuf/getbits."""
    __slots__ = ('data', 'pos', 'bitbuf', 'subbitbuf', 'bitcount')
    def __init__(self, data):
        self.data = data; self.pos = 0
        self.bitbuf = 0; self.subbitbuf = 0; self.bitcount = 0
        self._fillbuf(_BITBUFSIZ)
    def _fillbuf(self, n):
        self.bitbuf = (self.bitbuf << n) & 0xFFFF
        while n > self.bitcount:
            n -= self.bitcount
            self.bitbuf |= (self.subbitbuf << n) & 0xFFFF
            if self.pos < len(self.data):
                self.subbitbuf = self.data[self.pos]; self.pos += 1
            else:
                self.subbitbuf = 0
            self.bitcount = 8
        self.bitcount -= n
        self.bitbuf |= (self.subbitbuf >> self.bitcount) & 0xFFFF
        self.bitbuf &= 0xFFFF
    def getbits(self, n):
        x = self.bitbuf >> (_BITBUFSIZ - n); self._fillbuf(n); return x

class _LH5Decoder:
    def __init__(self, compressed_data):
        self.reader = _LH5BitReader(compressed_data)
        self.left = [0] * (2 * _NC); self.right = [0] * (2 * _NC)
        self.c_len = [0] * _NC; self.pt_len = [0] * _NPT
        self.c_table = [0] * 4096; self.pt_table = [0] * 256
        self.blocksize = 0; self._j = 0; self._i = 0

    def _make_table(self, nchar, bitlen, tablebits, table):
        count = [0]*17; weight = [0]*17; start = [0]*18
        for i in range(nchar):
            if bitlen[i] <= 16: count[bitlen[i]] += 1
        start[1] = 0
        for i in range(1, 17): start[i+1] = start[i] + (count[i] << (16-i))
        jutbits = 16 - tablebits
        for i in range(1, tablebits+1):
            start[i] >>= jutbits; weight[i] = 1 << (tablebits - i)
        for i in range(tablebits+1, 17): weight[i] = 1 << (16 - i)
        i = start[tablebits+1] >> jutbits; k = 1 << tablebits
        if i < k:
            for idx in range(i, k): table[idx] = 0
        avail = nchar; mask = 1 << (15 - tablebits)
        for ch in range(nchar):
            le = bitlen[ch]
            if le == 0: continue
            nextcode = start[le] + weight[le]
            if le <= tablebits:
                for ii in range(start[le], min(nextcode, len(table))): table[ii] = ch
            else:
                kk = start[le]; p_arr = table; p_idx = kk >> jutbits
                for _ in range(le - tablebits):
                    if p_arr[p_idx] == 0:
                        self.right[avail] = 0; self.left[avail] = 0
                        p_arr[p_idx] = avail; avail += 1
                    node = p_arr[p_idx]
                    p_arr = self.right if kk & mask else self.left
                    p_idx = node; kk <<= 1
                p_arr[p_idx] = ch
            start[le] = nextcode

    def _read_pt_len(self, nn, nbit, i_special):
        n = self.reader.getbits(nbit)
        if n == 0:
            c = self.reader.getbits(nbit)
            for i in range(nn): self.pt_len[i] = 0
            for i in range(256): self.pt_table[i] = c
        else:
            i = 0
            while i < n:
                c = self.reader.bitbuf >> (_BITBUFSIZ - 3)
                if c == 7:
                    m = 1 << (_BITBUFSIZ - 1 - 3)
                    while m & self.reader.bitbuf: m >>= 1; c += 1
                self.reader._fillbuf(3 if c < 7 else c - 3)
                if i < nn: self.pt_len[i] = c
                i += 1
                if i == i_special:
                    c2 = self.reader.getbits(2)
                    for _ in range(c2):
                        if i < nn: self.pt_len[i] = 0
                        i += 1
            while i < nn: self.pt_len[i] = 0; i += 1
            self._make_table(nn, self.pt_len, 8, self.pt_table)

    def _read_c_len(self):
        n = self.reader.getbits(_CBIT)
        if n == 0:
            c = self.reader.getbits(_CBIT)
            for i in range(_NC): self.c_len[i] = 0
            for i in range(4096): self.c_table[i] = c
        else:
            i = 0
            while i < n:
                c = self.pt_table[self.reader.bitbuf >> (_BITBUFSIZ - 8)]
                if c >= _NTT:
                    m = 1 << (_BITBUFSIZ - 1 - 8)
                    while c >= _NTT:
                        c = self.right[c] if self.reader.bitbuf & m else self.left[c]
                        m >>= 1
                self.reader._fillbuf(self.pt_len[c])
                if c <= 2:
                    if c == 0: c = 1
                    elif c == 1: c = self.reader.getbits(4) + 3
                    else: c = self.reader.getbits(_CBIT) + 20
                    for _ in range(c):
                        if i < _NC: self.c_len[i] = 0
                        i += 1
                else:
                    if i < _NC: self.c_len[i] = c - 2
                    i += 1
            while i < _NC: self.c_len[i] = 0; i += 1
            self._make_table(_NC, self.c_len, 12, self.c_table)

    def _decode_c(self):
        if self.blocksize == 0:
            self.blocksize = self.reader.getbits(16)
            self._read_pt_len(_NTT, _TBIT, 3)
            self._read_c_len()
            self._read_pt_len(_NP, _PBIT, -1)
        self.blocksize -= 1
        j = self.c_table[self.reader.bitbuf >> (_BITBUFSIZ - 12)]
        if j >= _NC:
            m = 1 << (_BITBUFSIZ - 1 - 12)
            while j >= _NC:
                j = self.right[j] if self.reader.bitbuf & m else self.left[j]
                m >>= 1
        self.reader._fillbuf(self.c_len[j]); return j

    def _decode_p(self):
        j = self.pt_table[self.reader.bitbuf >> (_BITBUFSIZ - 8)]
        if j >= _NP:
            m = 1 << (_BITBUFSIZ - 1 - 8)
            while j >= _NP:
                j = self.right[j] if self.reader.bitbuf & m else self.left[j]
                m >>= 1
        self.reader._fillbuf(self.pt_len[j])
        if j != 0: j = (1 << (j - 1)) + self.reader.getbits(j - 1)
        return j

    def decode(self, count, buffer):
        r = 0
        while True:
            self._j -= 1
            if self._j < 0: break
            buffer[r] = buffer[self._i]
            self._i = (self._i + 1) & (_DICSIZ - 1); r += 1
            if r == count: return
        while True:
            c = self._decode_c()
            if c <= _UCHAR_MAX:
                buffer[r] = c; r += 1
                if r == count: return
            else:
                self._j = c - (_UCHAR_MAX + 1 - _THRESHOLD)
                self._i = (r - self._decode_p() - 1) & (_DICSIZ - 1)
                while True:
                    self._j -= 1
                    if self._j < 0: break
                    buffer[r] = buffer[self._i]
                    self._i = (self._i + 1) & (_DICSIZ - 1); r += 1
                    if r == count: return

def decompress_lh5(comp_data, orig_size):
    """Decompress LH5 data (new FIZ format)."""
    decoder = _LH5Decoder(comp_data)
    buffer = bytearray(_DICSIZ); result = bytearray(); remaining = orig_size
    while remaining > 0:
        n = min(remaining, _DICSIZ)
        decoder.decode(n, buffer)
        result.extend(buffer[:n]); remaining -= n
    return bytes(result)

# ============================================================================
# Format detection and archive parsing
# ============================================================================
ACOPY_MAGIC   = b'ACOPY011a'
NEW_FIZ_MAGIC = 0x1A5A4946   # "FIZ\x1a" as uint32 LE

def detect_format(filepath):
    """Return 'acopy' or 'fiz' based on file magic bytes."""
    with open(filepath, 'rb') as f:
        header = f.read(10)
    if len(header) >= 9 and header[:9] == ACOPY_MAGIC:
        return 'acopy'
    if len(header) >= 4 and struct.unpack_from('<I', header, 0)[0] == NEW_FIZ_MAGIC:
        return 'fiz'
    raise ValueError(f"Unrecognized file format (first bytes: {header[:10].hex()})")

# ---- Old ACOPY format parsing ----

_ACOPY_HEADER_SIZE = 128
_ACOPY_NAME_FIELD  = 65
_ACOPY_META_SIZE   = 15

def _parse_acopy(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    if data[9] != 0x1A:
        raise ValueError("Missing DOS EOF marker at offset 9")
    file_count = struct.unpack_from('<H', data, 10)[0]
    pos = _ACOPY_HEADER_SIZE
    entries = []
    for _ in range(file_count):
        if data[pos:pos+2] != b'\r\n':
            raise ValueError(f"Expected CRLF at offset 0x{pos:X}")
        pos += 2
        rec_start = pos; method = data[pos]; pos += 1
        field_end = rec_start + 1 + _ACOPY_NAME_FIELD
        null1 = data.index(b'\x00', pos, field_end)
        filename = data[pos:null1].decode('ascii', errors='replace')
        pos = field_end
        attr      = data[pos]
        time_val  = struct.unpack_from('<H', data, pos+1)[0]
        date_val  = struct.unpack_from('<H', data, pos+3)[0]
        orig_size = struct.unpack_from('<I', data, pos+5)[0]
        comp_size = struct.unpack_from('<I', data, pos+9)[0]
        file_crc  = struct.unpack_from('<H', data, pos+13)[0]
        pos += _ACOPY_META_SIZE
        entries.append({'method': method, 'filename': filename, 'attr': attr,
                        'time': time_val, 'date': date_val,
                        'orig_size': orig_size, 'comp_size': comp_size,
                        'crc': file_crc})
    return data, entries, pos

# ---- New FIZ format parsing ----

_FIZ_HDR_SIZE = 20  # struct _fizhdr

def _parse_new_fiz(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    entries = []; pos = 0
    while pos + _FIZ_HDR_SIZE <= len(data):
        magic = struct.unpack_from('<I', data, pos)[0]
        if magic != NEW_FIZ_MAGIC:
            break
        method    = data[pos + 4]
        fnlen     = data[pos + 5]
        file_crc  = struct.unpack_from('<H', data, pos + 6)[0]
        orig_size = struct.unpack_from('<I', data, pos + 8)[0]
        comp_size = struct.unpack_from('<I', data, pos + 12)[0]
        stamp     = struct.unpack_from('<I', data, pos + 16)[0]
        time_val  = stamp & 0xFFFF
        date_val  = (stamp >> 16) & 0xFFFF
        pos += _FIZ_HDR_SIZE
        filename = data[pos:pos + fnlen].decode('ascii', errors='replace')
        pos += fnlen
        data_offset = pos
        pos += comp_size
        entries.append({'method': method, 'filename': filename, 'attr': 0x20,
                        'time': time_val, 'date': date_val,
                        'orig_size': orig_size, 'comp_size': comp_size,
                        'crc': file_crc, '_data_offset': data_offset})
    return data, entries, pos

# ============================================================================
# Unified extraction
# ============================================================================

def extract_fiz(filepath, output_dir):
    """Extract all files from a FIZ archive (auto-detecting format)."""
    fmt = detect_format(filepath)

    if fmt == 'acopy':
        data, entries, data_offset = _parse_acopy(filepath)
        comp_offset = data_offset
        fmt_label = "ACOPY (old, LZW)"
    else:
        data, entries, data_offset = _parse_new_fiz(filepath)
        fmt_label = "FIZ (new, LH5)"

    os.makedirs(output_dir, exist_ok=True)
    print(f"Archive: {filepath}")
    print(f"Format:  {fmt_label}")
    print(f"Files:   {len(entries)}")
    print()

    errors = 0
    if fmt == 'acopy':
        offset = data_offset

    for entry in entries:
        if fmt == 'acopy':
            comp_data = data[offset:offset + entry['comp_size']]
            offset += entry['comp_size']
        else:
            comp_data = data[entry['_data_offset']:
                             entry['_data_offset'] + entry['comp_size']]

        # Decompress
        if fmt == 'acopy':
            is_stored = (entry['method'] == 0x01)
        else:
            is_stored = (entry['method'] == 0)

        if is_stored:
            file_data = bytes(comp_data)
            method_str = "stored"
        else:
            try:
                if fmt == 'acopy':
                    file_data = decompress_lzw(comp_data, entry['orig_size'])
                    method_str = "LZW"
                else:
                    file_data = decompress_lh5(comp_data, entry['orig_size'])
                    method_str = "LH5"
            except (ValueError, IndexError) as ex:
                print(f"  ERROR: {entry['filename']}: {ex}")
                errors += 1
                continue

        # Verify size
        if len(file_data) != entry['orig_size']:
            print(f"  ERROR: size mismatch for {entry['filename']}: "
                  f"expected {entry['orig_size']}, got {len(file_data)}")
            errors += 1

        # Verify CRC
        actual_crc = crc16(file_data)
        if actual_crc != entry['crc']:
            print(f"  ERROR: CRC mismatch for {entry['filename']}: "
                  f"expected 0x{entry['crc']:04X}, got 0x{actual_crc:04X}")
            errors += 1

        # Write extracted file
        out_path = os.path.join(output_dir, entry['filename'])
        with open(out_path, 'wb') as f:
            f.write(file_data)

        timestamp = decode_dos_datetime(entry['time'], entry['date'])
        ratio = (entry['comp_size'] / entry['orig_size'] * 100
                 if entry['orig_size'] > 0 else 0)
        print(f"  {entry['filename']:<16s} {entry['orig_size']:>8d} -> "
              f"{entry['comp_size']:>8d} ({ratio:5.1f}%) [{method_str}] "
              f"{timestamp}")

    if fmt == 'acopy' and offset != len(data):
        print(f"\n  WARNING: {len(data) - offset} trailing bytes")
        errors += 1
    if fmt == 'fiz' and data_offset != len(data):
        print(f"\n  WARNING: {len(data) - data_offset} trailing bytes")
        errors += 1

    print()
    if errors:
        print(f"Completed with {errors} error(s).")
    else:
        print("All files extracted and verified successfully.")


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>")
        print()
        print("Extract files from a FIZ archive (Maximus BBS installer).")
        print("Supports both old (ACOPY/LZW) and new (FIZ/LH5) formats.")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(input_file):
        print(f"Error: '{input_file}' not found", file=sys.stderr)
        sys.exit(1)

    extract_fiz(input_file, output_dir)


if __name__ == '__main__':
    main()

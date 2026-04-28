#!/usr/bin/env python3
# Vibe coded by Claude
#
# macOSInstallTome.py [--macjapanese] <inputFile> <outputDir>
#
# Extracts files from a classic Mac OS Installer "Tome" archive
# (MacBinary-II wrapped, type 'idcp' / creator 'kakc'). Each contained
# file has a data fork and a resource fork; the archive stores each
# fork either raw (split into 65536-byte chunks, each chunk prefixed
# with a 4-byte header) or compressed with Apple's InstaCompOne LZ77
# codec. Both modes are fully decoded here.
#
# Output:
#   * A file that has BOTH a data fork and a resource fork is written
#     as a MacBinary II file with the original Mac filename (no
#     extension added) that preserves both forks, type, creator,
#     Finder flags, Finder location and creation / modification dates.
#   * A file that has ONLY a data fork is written as a plain file
#     containing that data fork; no MacBinary wrapper is added.
#   * A file that has ONLY a resource fork is also written as a
#     MacBinary II file (the raw resource fork alone is not portable
#     on its own).
#   * A tome whose outer MacBinary data fork is empty is written
#     back as its original MacBinary wrapper.
#
# Filenames inside the tome are auto-detected as either Mac Roman or
# Macintosh Japanese (Shift-JIS). Use --macjapanese to force Japanese
# decoding when auto-detection is insufficient.
#
# Every byte of every input file is accounted for by known structural
# regions (MacBinary header, data fork, data fork padding, resource
# fork, resource fork padding). The extractor asserts this at runtime.

import argparse
import os
import sys
import struct


# ===== InstaCompOne decoder ================================================
#
# Reverse-engineered from Apple's TomeViewer PowerPC binary (the
# `lz_decompress_plus`, `text_*` and `bin_*` routines it exports). The
# codec is an LZ77 scheme with a 131072-byte ring buffer and a set of
# adaptive prefix-based distance encodings. Two variants exist, selected
# by byte 1 of the fork's 4-byte marker:
#
#   0x00 0x00 0x00 0x00   text variant (7-bit literals, text distance
#                         dispatcher)
#   0x00 0x01 0x00 0x00   binary variant (8-bit literals, binary distance
#                         dispatcher)
#
# Both variants share:
#   * The literal-length Huffman tree (`read_litlen`).
#   * A bank of 15 distance sub-functions (`_dist_sub(i, ...)`) indexed
#     0..14, each able to encode distances in [1, 21*2^i]. The sub-
#     function's internal "large distance" branch picks its data-bit
#     width adaptively from the current output position, so files that
#     are still near the beginning use shorter codes.
#   * The chunk-boundary marker: every 65536 decoded bytes the bit
#     stream is re-aligned to a byte boundary and a 4-byte chunk marker
#     is discarded before decoding resumes.
#
# The variants differ in:
#   * The match-length Huffman tree (binary uses a deark-compatible
#     non-uniform tree, text uses a uniform one).
#   * The distance dispatcher (picks which sub-function to use based on
#     the current output position and on the total unpack_size).
#   * The literal bit width (7 bits vs. 8 bits per literal byte).

_RB_SIZE = 131072
_RB_MASK = _RB_SIZE - 1


class InstaCompError(Exception):
    pass


class _BitReader(object):
    __slots__ = ("buf", "pos", "pool", "nbits")

    def __init__(self, buf, skip=0):
        self.buf = buf
        self.pos = skip
        self.pool = 0
        self.nbits = 0

    def getbits(self, n):
        while self.nbits < n:
            if self.pos < len(self.buf):
                b = self.buf[self.pos]
                self.pos += 1
            else:
                b = 0
            self.pool = (self.pool << 8) | b
            self.nbits += 8
        v = (self.pool >> (self.nbits - n)) & ((1 << n) - 1)
        self.nbits -= n
        return v

    def align_byte(self):
        self.nbits = 0
        self.pool = 0


def _dist_sub(i, delta, br):
    """Read a distance from sub-function `i` (0..14).

    Layout (shared by both variants):
        bit 0              -> return N-bit value + 1             (range 1..2^i)
        bits 10            -> return (i+2)-bit value + 2^i + 1    (range 2^i+1..5*2^i)
        bits 11            -> "large" branch; adaptive on delta   (range 5*2^i+1..21*2^i)

    The "large" branch reads k data bits and returns them + (5*2^i+1),
    where k is picked from delta's bucket. Buckets follow the formula
    `large_bias + (1<<k) - 1` except for the single quirk that
    sub_07's k=10 threshold is 1644 instead of 1664 (the 20 extra
    values fall into the k=11 branch).
    """
    large_bias = 5 * (1 << i) + 1    # 5*2^i + 1
    mid_bias = (1 << i) + 1          # 2^i + 1
    if br.getbits(1) == 0:
        if i == 0:
            return 1
        return br.getbits(i) + 1
    if br.getbits(1) == 0:
        return br.getbits(i + 2) + mid_bias
    for k in range(1, i + 4):
        threshold = large_bias + (1 << k) - 1
        if i == 7 and k == 10:
            threshold = 1644  # TomeViewer quirk, see docstring
        if delta <= threshold:
            return br.getbits(k) + large_bias
    return br.getbits(i + 4) + large_bias


def _text_read_distance(delta, unpack_size, br):
    if delta <= 10:     return _dist_sub(0,  delta, br)
    if delta <= 20:     return _dist_sub(1,  delta, br)
    if delta <= 40:     return _dist_sub(2,  delta, br)
    if delta <= 80:     return _dist_sub(3,  delta, br)
    if delta <= 160:    return _dist_sub(4,  delta, br)
    if delta <= 320:    return _dist_sub(5,  delta, br)
    if delta <= 832:    return _dist_sub(6,  delta, br)
    if delta <= 1280    or unpack_size <= 0x0800:  return _dist_sub(7,  delta, br)
    if delta <= 2560    or unpack_size <= 0x1000:  return _dist_sub(8,  delta, br)
    if delta <= 5120    or unpack_size <= 0x2000:  return _dist_sub(9,  delta, br)
    if delta <= 10240   or unpack_size <= 0x4000:  return _dist_sub(10, delta, br)
    if delta <= 30000   or unpack_size <= 0x8000:  return _dist_sub(11, delta, br)
    if delta <= 50000   or unpack_size <= 0x10000: return _dist_sub(12, delta, br)
    if delta <= 172032  or unpack_size <= 0x20000: return _dist_sub(13, delta, br)
    return _dist_sub(14, delta, br)


def _bin_read_distance(delta, unpack_size, br):
    if delta <= 10:     return _dist_sub(0,  delta, br)
    if delta <= 20:     return _dist_sub(1,  delta, br)
    if delta <= 40:     return _dist_sub(2,  delta, br)
    if delta <= 80:     return _dist_sub(3,  delta, br)
    if delta <= 160:    return _dist_sub(4,  delta, br)
    if delta <= 672:    return _dist_sub(5,  delta, br)
    if delta <= 1000:   return _dist_sub(6,  delta, br)
    if delta <= 2688    or unpack_size <= 0x0800:  return _dist_sub(7,  delta, br)
    if delta <= 5376    or unpack_size <= 0x1000:  return _dist_sub(8,  delta, br)
    if delta <= 10752   or unpack_size <= 0x2000:  return _dist_sub(9,  delta, br)
    if delta <= 21504   or unpack_size <= 0x4000:  return _dist_sub(10, delta, br)
    if delta <= 43008   or unpack_size <= 0x8000:  return _dist_sub(11, delta, br)
    if delta <= 70000   or unpack_size <= 0x10000: return _dist_sub(12, delta, br)
    if delta <= 172032  or unpack_size <= 0x20000: return _dist_sub(13, delta, br)
    return _dist_sub(14, delta, br)


_TEXT_ML_BITS = (2, 2, 2, 3, 4, 5, 6, 7, 8, 9, 10)
_TEXT_ML_BASE = (0, 4, 8, 12, 20, 36, 68, 132, 260, 516, 1028)


def _text_read_matchlen(br):
    k = 0
    while k < 10:
        if br.getbits(1) == 0:
            break
        k += 1
    return br.getbits(_TEXT_ML_BITS[k]) + _TEXT_ML_BASE[k]


def _bin_read_matchlen(br):
    k = 0
    while k < 10:
        if br.getbits(1) == 0:
            break
        k += 1
    if k == 0:
        return br.getbits(1)              # 0..1
    if k == 1:
        if br.getbits(1) == 0:
            return 2                      # 2
        return br.getbits(1) + 3          # 3..4
    if k == 2:
        if br.getbits(1) == 0:
            return br.getbits(1) + 5      # 5..6
        return br.getbits(2) + 7          # 7..10
    if k == 3:  return br.getbits(3)  + 11    # 11..18
    if k == 4:  return br.getbits(3)  + 19    # 19..26
    if k == 5:  return br.getbits(5)  + 27    # 27..58
    if k == 6:  return br.getbits(6)  + 59    # 59..122
    if k == 7:  return br.getbits(7)  + 123   # 123..250
    if k == 8:  return br.getbits(8)  + 251   # 251..506
    if k == 9:  return br.getbits(9)  + 507   # 507..1018
    return br.getbits(10) + 1019              # k == 10, 1019..2042


def _read_litlen(br):
    """Read a literal-run length (1..63). Shared by both variants."""
    if br.getbits(1) == 0:
        return 1
    x = br.getbits(2)
    if x == 0:
        return 2
    if x == 1:
        return 3
    if x == 2:
        return br.getbits(2) + 4          # 4..7
    # x == 3
    y = br.getbits(4)
    if y <= 7:
        return y + 8                      # 8..15
    if y <= 11:
        return ((y - 8) << 2) + br.getbits(2) + 16   # 16..31
    return ((y - 12) << 3) + br.getbits(3) + 32      # 32..63


def instacomp_decompress(src, unpack_size):
    """Decode an InstaCompOne fork. `src` includes the 4-byte marker."""
    if unpack_size == 0:
        return b""
    if len(src) < 4:
        raise InstaCompError("fork too short for header")
    is_bin = (src[1] == 1)
    if is_bin:
        read_matchlen = _bin_read_matchlen
        read_distance = _bin_read_distance
        lit_bits = 8
    else:
        read_matchlen = _text_read_matchlen
        read_distance = _text_read_distance
        lit_bits = 7

    br = _BitReader(src, skip=4)
    rb = bytearray(_RB_SIZE)
    curpos = 0
    dst = bytearray()
    mode = 1
    next_chunk = 65536
    max_ops = unpack_size * 8 + 4096
    ops = 0

    try:
        while len(dst) < unpack_size:
            ops += 1
            if ops > max_ops:
                raise ValueError("runaway decoder")
            if len(dst) >= next_chunk:
                br.align_byte()
                br.getbits(32)  # per-chunk marker
                next_chunk += 65536
                mode = 1

            mlc = read_matchlen(br)
            if mlc > 0 or mode == 0:
                matchlen = mlc + 2
                if mode == 0:
                    matchlen += 1
                offset = read_distance(len(dst), unpack_size, br)
                frompos = (curpos - offset) & _RB_MASK
                matchlen = min(matchlen, unpack_size - len(dst))
                for _ in range(matchlen):
                    b = rb[frompos]
                    dst.append(b)
                    rb[curpos] = b
                    curpos = (curpos + 1) & _RB_MASK
                    frompos = (frompos + 1) & _RB_MASK
                mode = 1
            else:
                litlen = _read_litlen(br)
                litlen_out = min(litlen, unpack_size - len(dst))
                for _ in range(litlen_out):
                    b = br.getbits(lit_bits)
                    dst.append(b)
                    rb[curpos] = b
                    curpos = (curpos + 1) & _RB_MASK
                for _ in range(litlen - litlen_out):
                    br.getbits(lit_bits)
                mode = 0 if litlen < 63 else 1
    except ValueError as e:
        raise InstaCompError(str(e))

    if len(dst) != unpack_size:
        raise InstaCompError(
            "produced %d bytes, expected %d" % (len(dst), unpack_size)
        )
    return bytes(dst)


# ===== Tome structures =====================================================

TOME_MAGIC = 0x6B63          # "kc"
TOME_HDR_LEN = 36
TOME_ENTRY_LEN = 128
TOME_CONST_1 = 0x000007FA    # constant field at offset 0x08 of the tome header
TOME_CONST_2 = 0x00008000    # constant field at offset 0x0C of the tome header

RAW_CHUNK_BYTES = 65536


class TomeError(Exception):
    pass


def _expected_raw_stored_size(orig_len):
    """Return the exact stored size of a raw (uncompressed-chunked) fork.

    A raw fork consists of (orig_len + pad(orig_len, 65536)) / 16384 bytes
    of 4-byte chunk markers plus `orig_len` bytes of payload. The formula
    here matches deark's tome module detection heuristic.
    """
    if orig_len == 0:
        return 0
    padded = ((orig_len + 65535) // 65536) * 65536
    return orig_len + padded // 16384


def parse_macbinary_header(hdr):
    if len(hdr) != 128:
        raise TomeError("MacBinary header must be 128 bytes")
    if hdr[0] != 0 or hdr[74] != 0 or hdr[82] != 0:
        raise TomeError("MacBinary zero fields are not zero")
    if hdr[122] != 0x81:
        raise TomeError("not MacBinary II (version 0x%02x)" % hdr[122])
    nlen = hdr[1]
    if not 1 <= nlen <= 63:
        raise TomeError("bad MacBinary filename length %d" % nlen)
    return {
        "name": bytes(hdr[2:2 + nlen]),
        "type": bytes(hdr[65:69]),
        "creator": bytes(hdr[69:73]),
        "finder_flags_hi": hdr[73],
        "data_len": struct.unpack(">I", hdr[83:87])[0],
        "rsrc_len": struct.unpack(">I", hdr[87:91])[0],
        "creation": struct.unpack(">I", hdr[91:95])[0],
        "modification": struct.unpack(">I", hdr[95:99])[0],
        "finder_flags_lo": hdr[101],
    }


def parse_tome_header(buf):
    if len(buf) < TOME_HDR_LEN:
        raise TomeError("tome header truncated")
    (magic, ver, sub_hdr, c1, c2) = struct.unpack(">HHIII", buf[:16])
    if magic != TOME_MAGIC:
        raise TomeError("missing 'kc' tome signature")
    if ver != 1 or sub_hdr != 16:
        raise TomeError("unexpected tome version/header length")
    if c1 != TOME_CONST_1 or c2 != TOME_CONST_2:
        raise TomeError("unexpected tome constants")
    (total_uncmp, uk14, uk16, hdr_end, nfiles, nfiles_aux) = struct.unpack(
        ">IHHHHI", buf[16:32]
    )
    if hdr_end != TOME_HDR_LEN:
        raise TomeError("tome entries do not start at offset 0x24")
    return {
        "version": ver,
        "total_uncompressed": total_uncmp,
        "num_files": nfiles,
        "num_files_aux": nfiles_aux,
        "header_tail": bytes(buf[20:22]) + bytes(buf[22:24]) + bytes(buf[32:36]),
    }


def parse_tome_entry(buf, index):
    if len(buf) != TOME_ENTRY_LEN:
        raise TomeError("short entry %d" % index)
    flag = struct.unpack(">H", buf[0:2])[0]
    file_index = struct.unpack(">I", buf[2:6])[0]
    name_len = buf[6]
    if name_len > 31:
        raise TomeError("entry %d: filename length %d > 31" % (index, name_len))
    name = bytes(buf[7:7 + name_len])
    return {
        "flag": flag,
        "index": file_index,
        "name": name,
        "type": bytes(buf[0x26:0x2A]),
        "creator": bytes(buf[0x2A:0x2E]),
        "creation": struct.unpack(">I", buf[0x2E:0x32])[0],
        "modification": struct.unpack(">I", buf[0x32:0x36])[0],
        "finder_flags": struct.unpack(">H", buf[0x3A:0x3C])[0],
        "dfork_size": struct.unpack(">I", buf[0x3C:0x40])[0],
        "dfork_off": struct.unpack(">I", buf[0x40:0x44])[0],
        "dfork_stored": struct.unpack(">I", buf[0x44:0x48])[0],
        "dfork_checksum": struct.unpack(">I", buf[0x48:0x4C])[0],
        "rfork_size": struct.unpack(">I", buf[0x4C:0x50])[0],
        "rfork_off": struct.unpack(">I", buf[0x50:0x54])[0],
        "rfork_stored": struct.unpack(">I", buf[0x54:0x58])[0],
        "rfork_checksum": struct.unpack(">I", buf[0x58:0x5C])[0],
    }


def _extract_raw_chunks(blob, expected):
    """Decode a raw-chunked fork: marker + <=64 KiB, repeated."""
    out = bytearray()
    pos = 0
    while len(out) < expected:
        if pos + 4 > len(blob):
            raise TomeError("raw fork truncated at chunk marker")
        # Skip the 4-byte marker (its exact value may vary from chunk to
        # chunk but is not needed for decoding the payload).
        pos += 4
        chunk = min(RAW_CHUNK_BYTES, expected - len(out), len(blob) - pos)
        out.extend(blob[pos:pos + chunk])
        pos += chunk
    if len(out) != expected or pos != len(blob):
        raise TomeError("raw fork length mismatch")
    return bytes(out)


def extract_fork(data, off, stored, expected):
    """Return the fully decoded bytes of a single fork.

    The classification is:
      * expected == 0: the fork is empty.
      * stored == expected + overhead-per-64K: stored raw in 64 KiB
        chunks, each chunk preceded by a 4-byte marker.
      * otherwise: compressed with InstaCompOne. Byte 1 of the marker
        selects the text (0) / binary (1) variant.
    """
    if expected == 0:
        return b""
    blob = bytes(data[off:off + stored])
    if stored == _expected_raw_stored_size(expected):
        return _extract_raw_chunks(blob, expected)
    return instacomp_decompress(blob, expected)


# ===== MacBinary II writer ================================================

def _macbinary_crc(data):
    crc = 0
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


def _make_macbinary(meta, dfork, rfork):
    hdr = bytearray(128)
    name = meta["name"][:63]
    hdr[1] = len(name)
    hdr[2:2 + len(name)] = name
    hdr[65:69] = meta["type"]
    hdr[69:73] = meta["creator"]
    hdr[73] = (meta["finder_flags"] >> 8) & 0xFF
    struct.pack_into(">I", hdr, 83, len(dfork))
    struct.pack_into(">I", hdr, 87, len(rfork))
    struct.pack_into(">I", hdr, 91, meta["creation"])
    struct.pack_into(">I", hdr, 95, meta["modification"])
    hdr[101] = meta["finder_flags"] & 0xFF
    hdr[122] = 0x81
    hdr[123] = 0x81
    struct.pack_into(">H", hdr, 124, _macbinary_crc(hdr[:124]))

    def pad128(b):
        return bytes(b) + b"\x00" * ((-len(b)) % 128)

    out = bytearray(hdr)
    if dfork:
        out.extend(pad128(dfork))
    if rfork:
        out.extend(pad128(rfork))
    return bytes(out)


# ===== Extractor entry point ==============================================

def _detect_encoding(entries):
    """Auto-detect Shift-JIS filenames by looking for double-byte sequences."""
    for e in entries:
        name = e["name"]
        i = 0
        while i < len(name):
            b = name[i]
            if (0x81 <= b <= 0x9F or 0xE0 <= b <= 0xEF) and i + 1 < len(name):
                trail = name[i + 1]
                if 0x40 <= trail <= 0x7E or 0x80 <= trail <= 0xFC:
                    return "x-mac-japanese"
            i += 1
    return "mac_roman"


def _sanitize(name_bytes, encoding="mac_roman"):
    try:
        s = name_bytes.decode(encoding)
    except Exception:
        s = name_bytes.decode("mac_roman", errors="replace")
    s = "".join("_" if ch in ("/", "\x00") else ch for ch in s)
    return s.strip() or "unnamed"


def _unique_path(output_dir, name):
    """Avoid clobbering when two entries sanitise to the same name."""
    candidate = os.path.join(output_dir, name)
    if not os.path.exists(candidate):
        return candidate
    root, ext = os.path.splitext(name)
    i = 1
    while True:
        alt = os.path.join(output_dir, "%s (%d)%s" % (root, i, ext))
        if not os.path.exists(alt):
            return alt
        i += 1


def extract_tome(input_path, output_dir, encoding=None):
    # Validate the whole file BEFORE creating the output directory. If
    # the input is not a MacOS Installer tome (bad MacBinary header, bad
    # body length, empty data fork, no 'kc' tome signature, ...) we raise
    # TomeError and write nothing. Apple's Installer packages use the
    # 'idcp'/'kakc' type-creator for more than just tomes, so the type
    # code is not a sufficient check; we insist on seeing the 'kc' tome
    # header inside the data fork.
    with open(input_path, "rb") as f:
        macbin_hdr = f.read(128)
        body = f.read()

    mb = parse_macbinary_header(macbin_hdr)
    dlen = mb["data_len"]
    rlen = mb["rsrc_len"]
    dpad = (-dlen) % 128
    rpad = (-rlen) % 128
    expected = dlen + dpad + rlen + rpad
    if len(body) != expected:
        raise TomeError(
            "MacBinary body length %d does not match header (expected %d)"
            % (len(body), expected)
        )
    if dlen == 0:
        raise TomeError("MacBinary data fork is empty; not a tome")

    data_fork = body[:dlen]
    rsrc_fork = body[dlen + dpad:dlen + dpad + rlen]

    parse_tome_header(data_fork)  # raises TomeError unless 'kc' signed
    nfiles = struct.unpack(">H", data_fork[26:28])[0]

    entries = [
        parse_tome_entry(
            data_fork[TOME_HDR_LEN + i * TOME_ENTRY_LEN
                      :TOME_HDR_LEN + (i + 1) * TOME_ENTRY_LEN],
            i,
        )
        for i in range(nfiles)
    ]

    # Byte accounting: every byte of the tome data fork must belong to
    # either the header, an entry record, a data fork payload or a
    # resource fork payload. Anything else is a parser error.
    consumed = bytearray(len(data_fork))
    for i in range(TOME_HDR_LEN + nfiles * TOME_ENTRY_LEN):
        consumed[i] = 1
    for e in entries:
        for a, b in ((e["dfork_off"], e["dfork_stored"]),
                     (e["rfork_off"], e["rfork_stored"])):
            for i in range(a, a + b):
                if 0 <= i < len(consumed):
                    consumed[i] = 1
    if any(x == 0 for x in consumed):
        raise TomeError("tome data fork has gaps between known regions")

    # All validation passed; now it's safe to create the output dir.
    if encoding is None:
        encoding = _detect_encoding(entries)
    os.makedirs(output_dir, exist_ok=True)

    for entry in entries:
        name = _sanitize(entry["name"], encoding)
        df = extract_fork(
            data_fork, entry["dfork_off"], entry["dfork_stored"], entry["dfork_size"]
        )
        rf = extract_fork(
            data_fork, entry["rfork_off"], entry["rfork_stored"], entry["rfork_size"]
        )

        has_df = entry["dfork_size"] > 0
        has_rf = entry["rfork_size"] > 0

        meta = {
            "name": entry["name"],
            "type": entry["type"],
            "creator": entry["creator"],
            "creation": entry["creation"],
            "modification": entry["modification"],
            "finder_flags": entry["finder_flags"],
        }

        if has_df and not has_rf:
            # Data-fork-only: write the plain file with no MacBinary wrapper.
            out_path = _unique_path(output_dir, name)
            with open(out_path, "wb") as f:
                f.write(df)
        else:
            # One or both forks exist: wrap in MacBinary II so both forks
            # and metadata are preserved in a single file.
            mbdata = _make_macbinary(meta, df, rf)
            out_path = _unique_path(output_dir, name)
            with open(out_path, "wb") as f:
                f.write(mbdata)


def main():
    parser = argparse.ArgumentParser(
        description="Extract files from a classic Mac OS Installer Tome archive."
    )
    parser.add_argument("inputFile", help="MacBinary-wrapped tome file")
    parser.add_argument("outputDir", help="directory to write extracted files")
    parser.add_argument(
        "--macjapanese",
        action="store_true",
        help="decode filenames as Macintosh Japanese (Shift-JIS) instead of "
             "Mac Roman; without this flag, encoding is auto-detected",
    )
    args = parser.parse_args()
    encoding = "x-mac-japanese" if args.macjapanese else None
    extract_tome(args.inputFile, args.outputDir, encoding=encoding)


if __name__ == "__main__":
    main()

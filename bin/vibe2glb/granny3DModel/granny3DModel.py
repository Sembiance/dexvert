#!/usr/bin/env python3
# Vibe coded by Claude
"""Granny 3D Model (.gr2/GR2) → glTF 2.0 GLB converter.

Handles the Granny2 file format magic
``B8 67 B0 CA F8 6D B1 0F  84 72 8C 7E 5E 19 00 1E`` (little-endian, 32-bit
pointers, version 6 GrnFileHeader). It decompresses all sections (including
Oodle0/Oodle1 compressed sections), applies pointer fixups, walks the
embedded type tree, extracts every mesh / skeleton / vertex / triangle
described by the file, and emits a GLB.

If the input file is not in this exact format, the script fails fast and
produces no output.
"""

import argparse
import json
import os
import struct
import sys
from bisect import bisect_right

# ----------------------------------------------------------------------------
# Granny GR2 constants
# ----------------------------------------------------------------------------
GRN_MAGIC_LE32 = bytes.fromhex("b867b0caf86db10f84728c7e5e19001e")

# Member type IDs and their on-disk sizes in 32-bit (version 6) files.
T_END, T_INLINE = 0, 1
T_REFERENCE, T_REFERENCETOARRAY, T_ARRAYOFREFERENCES = 2, 3, 4
T_VARIANTREFERENCE, T_UNUSED6, T_REFERENCETOVARIANTARRAY = 5, 6, 7
T_STRING, T_TRANSFORM = 8, 9
T_REAL32 = 10
T_INT8, T_UINT8, T_BINORMALINT8, T_NORMALUINT8 = 11, 12, 13, 14
T_INT16, T_UINT16, T_BINORMALINT16, T_NORMALUINT16 = 15, 16, 17, 18
T_INT32, T_UINT32 = 19, 20
T_REAL16, T_EMPTYREFERENCE = 21, 22

TYPE_NAMES = {
    0: "End", 1: "Inline", 2: "Reference", 3: "ReferenceToArray",
    4: "ArrayOfReferences", 5: "VariantReference", 6: "Removed",
    7: "ReferenceToVariantArray", 8: "String", 9: "Transform",
    10: "Real32", 11: "Int8", 12: "UInt8", 13: "BinormalInt8",
    14: "NormalUInt8", 15: "Int16", 16: "UInt16", 17: "BinormalInt16",
    18: "NormalUInt16", 19: "Int32", 20: "UInt32", 21: "Real16",
    22: "EmptyReference",
}
TYPE_SIZES = {
    0: 0, 1: 0, 2: 4, 3: 8, 4: 8, 5: 8, 6: 0, 7: 12, 8: 4, 9: 68,
    10: 4, 11: 1, 12: 1, 13: 1, 14: 1, 15: 2, 16: 2, 17: 2, 18: 2,
    19: 4, 20: 4, 21: 2, 22: 4,
}
TYPE_ALIGNS = {
    0: 1, 1: 4, 2: 4, 3: 4, 4: 4, 5: 4, 6: 1, 7: 4, 8: 4, 9: 4,
    10: 4, 11: 1, 12: 1, 13: 1, 14: 1, 15: 2, 16: 2, 17: 2, 18: 2,
    19: 4, 20: 4, 21: 2, 22: 4,
}

# Sizes of a Granny type-definition array entry (32 bytes in 32-bit mode).
TYPE_DEF_ENTRY_SIZE = 32


# ----------------------------------------------------------------------------
# Oodle1 decompression (ports gr2_decompress.cpp from nwn2mdk, Boost License)
# ----------------------------------------------------------------------------
U16 = (1 << 16) - 1
U32 = (1 << 32) - 1


class _Decoder:
    __slots__ = ("numer", "denom", "next_denom", "stream", "pos")

    def __init__(self, stream, pos):
        self.stream = stream
        self.pos = pos
        self.numer = stream[pos] >> 1
        self.denom = 0x80
        self.next_denom = 0

    def decode(self, mx):
        while self.denom <= 0x800000:
            self.denom = (self.denom << 8) & U32
            self.numer = (self.numer << 8) & U32
            self.numer |= (self.stream[self.pos] << 7) & 0x80
            self.numer |= (self.stream[self.pos + 1] >> 1) & 0x7F
            self.pos += 1
        self.next_denom = self.denom // mx
        return min(self.numer // self.next_denom, mx - 1)

    def commit(self, mx, val, err):
        self.numer = (self.numer - self.next_denom * val) & U32
        if val + err < mx:
            self.denom = (self.next_denom * err) & U32
        else:
            self.denom = (self.denom - self.next_denom * val) & U32
        return val

    def decode_and_commit(self, mx):
        return self.commit(mx, self.decode(mx), 1)


class _WeighWindow:
    __slots__ = (
        "count_cap", "ranges", "values", "weights", "weight_total",
        "thresh_increase", "thresh_increase_cap",
        "thresh_range_rebuild", "thresh_weight_rebuild",
    )

    def __init__(self, max_value, count_cap):
        self.weight_total = 4
        self.count_cap = count_cap + 1
        self.ranges = [0, 0x4000]
        self.weights = [4]
        self.values = [0]
        self.thresh_increase = 4
        self.thresh_range_rebuild = 8
        self.thresh_weight_rebuild = max(256, min(32 * max_value, 15160))
        if max_value > 64:
            self.thresh_increase_cap = min(
                2 * max_value, self.thresh_weight_rebuild // 2 - 32
            )
        else:
            self.thresh_increase_cap = 128

    def rebuild_ranges(self):
        n = len(self.weights)
        if len(self.ranges) != n + 1:
            self.ranges = [0] * (n + 1)
        range_weight = 8 * 0x4000 // self.weight_total
        s = 0
        for i in range(n):
            self.ranges[i] = s
            s = (s + (self.weights[i] * range_weight) // 8) & U16
        self.ranges[n] = 0x4000
        if self.thresh_increase > self.thresh_increase_cap // 2:
            self.thresh_range_rebuild = self.weight_total + self.thresh_increase_cap
        else:
            self.thresh_increase = (self.thresh_increase * 2) & U16
            self.thresh_range_rebuild = self.weight_total + self.thresh_increase

    def rebuild_weights(self):
        for i in range(len(self.weights)):
            self.weights[i] //= 2
        self.weight_total = sum(self.weights) & U16
        i = 1
        while i < len(self.weights):
            while i < len(self.weights) and self.weights[i] == 0:
                self.weights[i] = self.weights[-1]
                self.values[i] = self.values[-1]
                self.weights.pop()
                self.values.pop()
            i += 1
        if len(self.weights) > 1:
            it = 1
            mx = self.weights[1]
            for k in range(2, len(self.weights)):
                if self.weights[k] > mx:
                    mx = self.weights[k]
                    it = k
            self.weights[it], self.weights[-1] = self.weights[-1], self.weights[it]
            self.values[it], self.values[-1] = self.values[-1], self.values[it]
        if len(self.weights) < self.count_cap and self.weights[0] == 0:
            self.weights[0] = 1
            self.weight_total = (self.weight_total + 1) & U16

    def try_decode(self, dec):
        if self.weight_total >= self.thresh_range_rebuild:
            if self.thresh_range_rebuild >= self.thresh_weight_rebuild:
                self.rebuild_weights()
            self.rebuild_ranges()
        value = dec.decode(0x4000)
        rangeit = bisect_right(self.ranges, value) - 1
        dec.commit(0x4000, self.ranges[rangeit],
                   self.ranges[rangeit + 1] - self.ranges[rangeit])
        idx = rangeit
        self.weights[idx] = (self.weights[idx] + 1) & U16
        self.weight_total = (self.weight_total + 1) & U16
        if idx > 0:
            return (None, self.values[idx])
        if len(self.weights) >= len(self.ranges) and dec.decode_and_commit(2) == 1:
            idx = (len(self.ranges)
                   + dec.decode_and_commit(
                       len(self.weights) - len(self.ranges) + 1) - 1)
            self.weights[idx] = (self.weights[idx] + 2) & U16
            self.weight_total = (self.weight_total + 2) & U16
            return (None, self.values[idx])
        self.values.append(0)
        self.weights.append(2)
        self.weight_total = (self.weight_total + 2) & U16
        if len(self.weights) == self.count_cap:
            self.weight_total = (self.weight_total - self.weights[0]) & U16
            self.weights[0] = 0
        return (len(self.values) - 1, 0)


class _Dictionary:
    __slots__ = (
        "decoded_size", "backref_size",
        "decoded_value_max", "backref_value_max",
        "lowbit_value_max", "midbit_value_max", "highbit_value_max",
        "lowbit_window", "highbit_window",
        "midbit_windows", "decoded_windows", "size_windows",
    )

    def __init__(self, params):
        dvm, brm, dc, hbc, sc = params
        self.decoded_size = 0
        self.backref_size = 0
        self.decoded_value_max = dvm
        self.backref_value_max = brm
        self.lowbit_value_max = min(brm + 1, 4)
        self.midbit_value_max = min(brm // 4 + 1, 256)
        self.highbit_value_max = brm // 1024 + 1
        self.lowbit_window = _WeighWindow(self.lowbit_value_max - 1, self.lowbit_value_max)
        self.highbit_window = _WeighWindow(self.highbit_value_max - 1, hbc + 1)
        self.midbit_windows = [
            _WeighWindow(self.midbit_value_max - 1, self.midbit_value_max)
            for _ in range(self.highbit_value_max)
        ]
        self.decoded_windows = [
            _WeighWindow(self.decoded_value_max - 1, dc) for _ in range(4)
        ]
        sw = []
        for i in range(4):
            for _ in range(16):
                sw.append(_WeighWindow(64, sc[3 - i]))
        sw.append(_WeighWindow(64, sc[0]))
        self.size_windows = sw

    def decompress_block(self, dec, dbuf, dptr):
        sw = self.size_windows[self.backref_size]
        d1 = sw.try_decode(dec)
        if d1[0] is not None:
            v = dec.decode_and_commit(65)
            sw.values[d1[0]] = v
            d1 = (d1[0], v)
        self.backref_size = d1[1]
        if self.backref_size > 0:
            sizes_tbl = (128, 192, 256, 512)
            br_size = (self.backref_size + 1
                       if self.backref_size < 61
                       else sizes_tbl[self.backref_size - 61])
            br_range = min(self.backref_value_max, self.decoded_size)
            d3 = self.lowbit_window.try_decode(dec)
            if d3[0] is not None:
                v = dec.decode_and_commit(self.lowbit_value_max)
                self.lowbit_window.values[d3[0]] = v
                d3 = (d3[0], v)
            d4 = self.highbit_window.try_decode(dec)
            if d4[0] is not None:
                v = dec.decode_and_commit(br_range // 1024 + 1)
                self.highbit_window.values[d4[0]] = v
                d4 = (d4[0], v)
            mw = self.midbit_windows[d4[1]]
            d5 = mw.try_decode(dec)
            if d5[0] is not None:
                v = dec.decode_and_commit(min(br_range // 4 + 1, 256))
                mw.values[d5[0]] = v
                d5 = (d5[0], v)
            br_off = (d4[1] << 10) + (d5[1] << 2) + d3[1] + 1
            self.decoded_size += br_size
            src = dptr - br_off
            repeat = br_size // br_off
            remain = br_size % br_off
            for i in range(repeat):
                base = dptr + i * br_off
                dbuf[base:base + br_off] = dbuf[src:src + br_off]
            if remain:
                base = dptr + repeat * br_off
                dbuf[base:base + remain] = dbuf[src:src + remain]
            return br_size
        i = dptr % 4
        dw = self.decoded_windows[i]
        d2 = dw.try_decode(dec)
        if d2[0] is not None:
            v = dec.decode_and_commit(self.decoded_value_max)
            dw.values[d2[0]] = v
            d2 = (d2[0], v)
        dbuf[dptr] = d2[1] & 0xFF
        self.decoded_size += 1
        return 1


def _parse_oodle_params(buf, off):
    w0, w1, s0, s1, s2, s3 = struct.unpack_from("<II4B", buf, off)
    return (
        w0 & 0x1FF,
        (w0 >> 9) & 0x7FFFFF,
        w1 & 0x1FF,
        (w1 >> 19) & 0x1FFF,
        (s0, s1, s2, s3),
    )


def oodle1_decompress(cbuf, csize, step1, step2, dsize):
    """Decompress Oodle0/Oodle1 data used by Granny GR2 sections."""
    if csize == 0:
        return b""
    buf = bytearray(cbuf[:csize])
    pad = (4 - csize) % 4
    buf += b"\x00" * pad
    buf += b"\x00" * 4  # safety - decoder reads 2 bytes ahead

    params = [
        _parse_oodle_params(buf, 0),
        _parse_oodle_params(buf, 12),
        _parse_oodle_params(buf, 24),
    ]
    dec = _Decoder(buf, 36)
    # 1 KiB scratch so backrefs near a step boundary don't truncate.
    over = 1024
    dbuf = bytearray(dsize + over)
    steps = (step1, step2, dsize)
    dptr = 0
    for i in range(3):
        dic = _Dictionary(params[i])
        target = steps[i]
        while dptr < target:
            dptr += dic.decompress_block(dec, dbuf, dptr)
    return bytes(dbuf[:dsize])


# ----------------------------------------------------------------------------
# granny2.dll fallback (used for Oodle0 "compression type 1" sections, for
# which no public reference decoder exists). Invokes a small mingw-w64
# wrapper that calls the DLL's exported GrannyDecompressData via wine.
# ----------------------------------------------------------------------------
import subprocess
import tempfile

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DLL_HELPER_DIR = os.path.join(_SCRIPT_DIR, "granny2")
DLL_HELPER_EXE = os.path.join(DLL_HELPER_DIR, "wrap.exe")
DLL_PATH = os.path.join(DLL_HELPER_DIR, "granny2-2004-11.dll")


class GrannyDllUnavailable(RuntimeError):
    """Raised when the wine + granny2.dll fallback can't be invoked."""


def granny_dll_decompress(payload, *, format, stop0, stop1,
                          comp_size, dec_size,
                          dll_path=None, helper_path=None):
    """Decompress a single GR2 section by calling granny2.dll under wine.

    Returns the decompressed bytes (exactly ``dec_size`` long).
    Raises GrannyDllUnavailable if the wrapper or DLL is missing, or
    RuntimeError if the DLL call itself fails.
    """
    dll_path = dll_path or DLL_PATH
    helper_path = helper_path or DLL_HELPER_EXE
    if not os.path.exists(helper_path):
        raise GrannyDllUnavailable(
            f"granny2 wrapper not built at {helper_path} "
            "(needed for Oodle0 sections)")
    if not os.path.exists(dll_path):
        raise GrannyDllUnavailable(
            f"granny2.dll not found at {dll_path} "
            "(needed for Oodle0 sections)")
    with tempfile.TemporaryDirectory(prefix="gr2dec_") as td:
        ip = os.path.join(td, "in.bin")
        op = os.path.join(td, "out.bin")
        with open(ip, "wb") as f:
            f.write(payload[:comp_size])
        env = os.environ.copy()
        # Silence wine: no fixme/err spam, no GUI crash dialog.
        env["WINEDEBUG"] = "-all"
        env["WINEDLLOVERRIDES"] = "winedbg.exe=d"
        cmd = [
            "wine", helper_path, dll_path,
            str(format), str(stop0), str(stop1),
            str(comp_size), str(dec_size),
            ip, op,
        ]
        # 120 s is enough for any sample's biggest section plus wine cold-start.
        r = subprocess.run(cmd, env=env, capture_output=True, timeout=120)
        if r.returncode != 0:
            raise RuntimeError(
                f"granny2.dll decompression failed (rc={r.returncode}): "
                f"{r.stderr.decode('latin-1', errors='replace').strip()}"
            )
        with open(op, "rb") as f:
            out = f.read()
        if len(out) != dec_size:
            raise RuntimeError(
                f"granny2.dll output size {len(out)} != expected {dec_size}"
            )
        return out


# ----------------------------------------------------------------------------
# GR2 file structure parser
# ----------------------------------------------------------------------------
class GrannyFile:
    """Reads a complete Granny GR2 file (version 6, 32-bit, little-endian)."""

    def __init__(self, data):
        self.raw = data
        self._parse_header()
        self._read_sections()
        self._read_fixups()

    @classmethod
    def from_path(cls, path):
        with open(path, "rb") as f:
            return cls(f.read())

    # ---- header -----------------------------------------------------------
    def _parse_header(self):
        data = self.raw
        if len(data) < 88:
            raise ValueError("File too short to be Granny")
        if data[:16] != GRN_MAGIC_LE32:
            raise ValueError("Not a Granny GR2 file (magic mismatch)")
        hsize, hformat, r0, r1 = struct.unpack_from("<4I", data, 16)
        if hformat != 0:
            raise ValueError(f"Unsupported file header format {hformat}")
        if r0 != 0 or r1 != 0:
            raise ValueError("File header reserved bytes not zero")
        (ver, total_size, crc, sao, sac,
         rtd_sec, rtd_off, ro_sec, ro_off, type_tag,
         et0, et1, et2, et3) = struct.unpack_from("<14I", data, 32)
        if ver != 6:
            raise ValueError(f"Unsupported Granny version {ver} (need 6)")
        if total_size != len(data):
            raise ValueError(f"TotalSize {total_size} != file size {len(data)}")
        if sac < 1 or sac > 64:
            raise ValueError(f"Implausible section count {sac}")
        expected_hsize = 32 + 4 * 14 + sac * 44
        if hsize != expected_hsize:
            raise ValueError(f"HeaderSize {hsize} != computed {expected_hsize}")
        self.header_size = hsize
        self.version = ver
        self.crc = crc
        self.section_array_offset = sao
        self.section_count = sac
        self.root_type_ref = (rtd_sec, rtd_off)
        self.root_obj_ref = (ro_sec, ro_off)
        self.type_tag = type_tag
        self.extra_tags = (et0, et1, et2, et3)

    # ---- sections (read + decompress) -------------------------------------
    def _read_sections(self):
        data = self.raw
        sa_start = 32 + self.section_array_offset
        self.sections = []
        self.sec_data = []
        for i in range(self.section_count):
            (comp, doff, dsz, esz, align,
             f16, f8, pfo, pfc, mmo, mmc) = struct.unpack_from(
                "<11I", data, sa_start + i * 44
            )
            self.sections.append(dict(
                compression=comp, data_offset=doff, data_size=dsz,
                expanded_size=esz, alignment=align,
                first16_offset=f16, first8_offset=f8,
                pfo=pfo, pfc=pfc, mmo=mmo, mmc=mmc,
            ))
            if dsz == 0 and esz == 0:
                self.sec_data.append(b"")
                continue
            payload = data[doff:doff + dsz]
            if len(payload) != dsz:
                raise ValueError(f"Section {i} payload truncated")
            if comp == 0:
                if dsz != esz:
                    raise ValueError(
                        f"Section {i}: uncompressed dsz={dsz} esz={esz}")
                self.sec_data.append(bytes(payload))
            elif comp == 2:
                # Granny "Oodle1": fully documented, pure-Python decoder.
                self.sec_data.append(
                    oodle1_decompress(payload, dsz, f16, f8, esz)
                )
            elif comp == 1:
                # Granny "Oodle0": undocumented predecessor of Oodle1.
                # We have no Python decoder for it; delegate to the real
                # granny2.dll via the wine wrapper.
                self.sec_data.append(
                    granny_dll_decompress(payload, format=1,
                                          stop0=f16, stop1=f8,
                                          comp_size=dsz, dec_size=esz)
                )
                self._uses_oodle0 = True
            else:
                raise ValueError(
                    f"Section {i}: unsupported compression type {comp}"
                )
        if not hasattr(self, "_uses_oodle0"):
            self._uses_oodle0 = False

    # ---- fixups -----------------------------------------------------------
    def _read_fixups(self):
        data = self.raw
        self.ptr_fixups = {}
        self.mm_fixups = {}
        for idx, s in enumerate(self.sections):
            for j in range(s["pfc"]):
                fo, ts, to = struct.unpack_from("<3I", data, s["pfo"] + j * 12)
                self.ptr_fixups[(idx, fo)] = (ts, to)
            for j in range(s["mmc"]):
                cnt, fo, ts, to = struct.unpack_from(
                    "<4I", data, s["mmo"] + j * 16
                )
                self.mm_fixups[(idx, fo)] = (cnt, ts, to)

    # ---- low-level accessors ---------------------------------------------
    def get_ptr(self, sec, off):
        return self.ptr_fixups.get((sec, off))

    def get_cstring(self, sec, off):
        d = self.sec_data[sec]
        end = d.find(b"\x00", off)
        if end < 0:
            end = len(d)
        return d[off:end].decode("latin-1", errors="replace")


# ----------------------------------------------------------------------------
# Type tree walker
# ----------------------------------------------------------------------------
class TypeWalker:
    def __init__(self, gr: GrannyFile):
        self.gr = gr
        self._type_cache = {}
        self._struct_size_cache = {}

    def read_type_def_array(self, sec, off):
        key = (sec, off)
        if key in self._type_cache:
            return self._type_cache[key]
        d = self.gr.sec_data[sec]
        members = []
        i = 0
        while True:
            e_off = off + i * TYPE_DEF_ENTRY_SIZE
            if e_off + TYPE_DEF_ENTRY_SIZE > len(d):
                raise ValueError(
                    f"Type def array at sec{sec}:{off} runs past section end")
            t = struct.unpack_from("<I", d, e_off)[0]
            if t == 0:
                break
            if t not in TYPE_SIZES or t == T_UNUSED6:
                raise ValueError(
                    f"Unsupported type id {t} at sec{sec}:{e_off}")
            name_ptr = self.gr.get_ptr(sec, e_off + 4)
            sub_ptr = self.gr.get_ptr(sec, e_off + 8)
            arr_w, e0, e1, e2, ignored = struct.unpack_from(
                "<5I", d, e_off + 12
            )
            name = self.gr.get_cstring(*name_ptr) if name_ptr else ""
            members.append(dict(
                type=t, name=name, subtype=sub_ptr, arr_width=arr_w,
                extra=(e0, e1, e2), ignored=ignored,
            ))
            i += 1
        self._type_cache[key] = members
        return members

    def member_align(self, m):
        t = m["type"]
        if t == T_INLINE and m["subtype"]:
            sub = self.read_type_def_array(*m["subtype"])
            return max((self.member_align(x) for x in sub), default=1)
        return TYPE_ALIGNS[t]

    def member_unit_size(self, m):
        t = m["type"]
        if t == T_INLINE and m["subtype"]:
            return self.struct_size(self.read_type_def_array(*m["subtype"]))
        return TYPE_SIZES[t]

    def member_size(self, m):
        base = self.member_unit_size(m)
        if m["arr_width"] > 0:
            base *= m["arr_width"]
        return base

    def struct_size(self, members):
        key = id(members)
        if key in self._struct_size_cache:
            return self._struct_size_cache[key]
        off = 0
        max_align = 1
        for m in members:
            a = self.member_align(m)
            if a > max_align:
                max_align = a
            off = (off + a - 1) & ~(a - 1)
            off += self.member_size(m)
        if max_align > 1:
            off = (off + max_align - 1) & ~(max_align - 1)
        self._struct_size_cache[key] = off
        return off

    def read_struct(self, members, sec, off):
        cur = off
        result = {}
        for m in members:
            a = self.member_align(m)
            cur = (cur + a - 1) & ~(a - 1)
            result[m["name"]] = self.read_member(m, sec, cur)
            cur += self.member_size(m)
        return result

    def read_member(self, m, sec, off):
        t = m["type"]
        if m["arr_width"] > 0:
            unit = self.member_unit_size(m)
            return [self._read_one(t, sec, off + i * unit, m["subtype"])
                    for i in range(m["arr_width"])]
        return self._read_one(t, sec, off, m["subtype"])

    def _read_one(self, t, sec, off, subtype):
        d = self.gr.sec_data[sec]
        if t == T_INLINE:
            if subtype:
                sub = self.read_type_def_array(*subtype)
                return self.read_struct(sub, sec, off)
            return None
        if t == T_REFERENCE:
            tgt = self.gr.get_ptr(sec, off)
            if not tgt:
                return None
            if subtype:
                return self.read_struct(
                    self.read_type_def_array(*subtype), *tgt
                )
            return tgt
        if t == T_REFERENCETOARRAY:
            count = struct.unpack_from("<I", d, off)[0]
            ptr = self.gr.get_ptr(sec, off + 4)
            if not ptr or count == 0:
                return []
            if subtype:
                sub = self.read_type_def_array(*subtype)
                size = self.struct_size(sub)
                return [
                    self.read_struct(sub, ptr[0], ptr[1] + i * size)
                    for i in range(count)
                ]
            return [(ptr[0], ptr[1] + i * 4) for i in range(count)]
        if t == T_ARRAYOFREFERENCES:
            count = struct.unpack_from("<I", d, off)[0]
            ptr = self.gr.get_ptr(sec, off + 4)
            if not ptr or count == 0:
                return []
            results = []
            sub = self.read_type_def_array(*subtype) if subtype else None
            for i in range(count):
                ep = self.gr.get_ptr(ptr[0], ptr[1] + i * 4)
                if ep is None:
                    results.append(None)
                elif sub is not None:
                    results.append(self.read_struct(sub, *ep))
                else:
                    results.append(ep)
            return results
        if t == T_VARIANTREFERENCE:
            tp = self.gr.get_ptr(sec, off)
            dp = self.gr.get_ptr(sec, off + 4)
            if not tp or not dp:
                return None
            return self.read_struct(self.read_type_def_array(*tp), *dp)
        if t == T_REFERENCETOVARIANTARRAY:
            tp = self.gr.get_ptr(sec, off)
            count = struct.unpack_from("<I", d, off + 4)[0]
            dp = self.gr.get_ptr(sec, off + 8)
            if not tp or not dp or count == 0:
                return []
            sub = self.read_type_def_array(*tp)
            size = self.struct_size(sub)
            return [self.read_struct(sub, dp[0], dp[1] + i * size)
                    for i in range(count)]
        if t == T_STRING:
            sp = self.gr.get_ptr(sec, off)
            return self.gr.get_cstring(*sp) if sp else None
        if t == T_TRANSFORM:
            flags = struct.unpack_from("<I", d, off)[0]
            tx = struct.unpack_from("<3f", d, off + 4)
            rot = struct.unpack_from("<4f", d, off + 16)
            scale = struct.unpack_from("<9f", d, off + 32)
            return dict(flags=flags, translation=tx, rotation=rot,
                        scale_shear=scale)
        if t == T_REAL32:
            return struct.unpack_from("<f", d, off)[0]
        if t in (T_INT8, T_BINORMALINT8):
            return struct.unpack_from("<b", d, off)[0]
        if t in (T_UINT8, T_NORMALUINT8):
            return struct.unpack_from("<B", d, off)[0]
        if t in (T_INT16, T_BINORMALINT16):
            return struct.unpack_from("<h", d, off)[0]
        if t in (T_UINT16, T_NORMALUINT16):
            return struct.unpack_from("<H", d, off)[0]
        if t == T_INT32:
            return struct.unpack_from("<i", d, off)[0]
        if t == T_UINT32:
            return struct.unpack_from("<I", d, off)[0]
        if t == T_REAL16:
            bits = struct.unpack_from("<H", d, off)[0]
            return struct.unpack("<e", struct.pack("<H", bits))[0]
        if t == T_EMPTYREFERENCE:
            return None
        raise ValueError(f"Unhandled type {t}")


# ----------------------------------------------------------------------------
# FileInfo / mesh / skeleton extraction
# ----------------------------------------------------------------------------
class GrannyDocument:
    def __init__(self, gr: GrannyFile):
        self.gr = gr
        self.walker = TypeWalker(gr)
        rt = gr.root_type_ref
        if rt[0] >= gr.section_count:
            raise ValueError("Root type ref points to missing section")
        type_data = gr.sec_data[rt[0]]
        if len(type_data) < TYPE_DEF_ENTRY_SIZE:
            raise ValueError("Root type section too small")
        first = struct.unpack_from("<I", type_data, rt[1])[0]
        if first == 0:
            self.fileinfo = None
            return
        members = self.walker.read_type_def_array(*rt)
        self.root_members = members
        self.fileinfo = self.walker.read_struct(members, *gr.root_obj_ref)

    @property
    def has_content(self):
        if not self.fileinfo:
            return False
        if not isinstance(self.fileinfo, dict):
            return False
        return any(
            self.fileinfo.get(k)
            for k in ("Meshes", "VertexDatas", "TriTopologies",
                      "Skeletons", "Models")
        )


# ----------------------------------------------------------------------------
# Vertex layout interpretation
# ----------------------------------------------------------------------------
def vertex_attribute(name):
    """Map Granny vertex member names to glTF attribute semantics."""
    n = name.lower()
    if n == "position":
        return "POSITION", "VEC3"
    if n == "normal":
        return "NORMAL", "VEC3"
    if n == "tangent":
        return "TANGENT", "VEC3"
    if n in ("binormal", "bitangent"):
        return "BINORMAL", "VEC3"
    if n in ("uv", "uvw", "texturecoordinates", "texturecoordinates0",
             "textcoord", "texcoord", "texcoord0", "texturecoords",
             "texturecoordinates_0"):
        return "TEXCOORD_0", "VEC2"
    if n.startswith("texturecoordinates"):
        # numbered set
        try:
            idx = int(n.replace("texturecoordinates", "") or "0")
        except ValueError:
            idx = 0
        return f"TEXCOORD_{idx}", "VEC2"
    if n in ("color", "colors", "diffusecolor"):
        return "COLOR_0", "VEC4"
    if n == "boneindices":
        return "JOINTS_0", "VEC4"
    if n == "boneweights":
        return "WEIGHTS_0", "VEC4"
    return None, None


def _decode_value(t, raw_bytes):
    """Decode a single primitive value given its granny type and bytes."""
    if t == T_REAL32:
        return struct.unpack("<f", raw_bytes)[0]
    if t == T_REAL16:
        return struct.unpack("<e", raw_bytes)[0]
    if t == T_INT8:
        return struct.unpack("<b", raw_bytes)[0]
    if t == T_UINT8 or t == T_NORMALUINT8:
        return struct.unpack("<B", raw_bytes)[0]
    if t == T_BINORMALINT8:
        return struct.unpack("<b", raw_bytes)[0]
    if t == T_INT16:
        return struct.unpack("<h", raw_bytes)[0]
    if t == T_UINT16 or t == T_NORMALUINT16:
        return struct.unpack("<H", raw_bytes)[0]
    if t == T_BINORMALINT16:
        return struct.unpack("<h", raw_bytes)[0]
    if t == T_INT32:
        return struct.unpack("<i", raw_bytes)[0]
    if t == T_UINT32:
        return struct.unpack("<I", raw_bytes)[0]
    raise ValueError(f"non-primitive vertex element type {t}")


def parse_vertex_layout(walker, vertex_type_members):
    """Build a description of one vertex from the Granny vertex type def.

    Returns (vertex_size, list of fields). Each field is a dict:
        name, type_id, count (arr_width or natural), offset, semantic.
    """
    fields = []
    cur = 0
    max_align = 1
    for m in vertex_type_members:
        t = m["type"]
        a = TYPE_ALIGNS[t]
        if a > max_align:
            max_align = a
        cur = (cur + a - 1) & ~(a - 1)
        count = m["arr_width"] if m["arr_width"] > 0 else 1
        size = TYPE_SIZES[t] * count
        fields.append(dict(
            name=m["name"], type_id=t, count=count,
            offset=cur, byte_size=TYPE_SIZES[t]
        ))
        cur += size
    if max_align > 1:
        cur = (cur + max_align - 1) & ~(max_align - 1)
    return cur, fields


def extract_vertices(walker, vdata):
    """Extract a Granny VertexData entry into raw per-vertex arrays."""
    vt = vdata.get("VertexType")
    verts = vdata.get("Vertices")
    if vt is None or verts is None:
        return None
    if not isinstance(verts, dict):
        # Vertices is the variant ref struct already read - but our walker
        # decodes ReferenceToVariantArray as a list of dicts. Each dict is
        # one vertex.
        pass
    # The walker auto-reads ReferenceToVariantArray as list-of-dicts, so
    # `verts` is already a list of per-vertex dicts. Return them.
    return verts


# ----------------------------------------------------------------------------
# glTF / GLB construction
# ----------------------------------------------------------------------------
GLTF_BYTE = 5120
GLTF_UBYTE = 5121
GLTF_SHORT = 5122
GLTF_USHORT = 5123
GLTF_UINT = 5125
GLTF_FLOAT = 5126
GLTF_TARGET_ARRAY = 34962
GLTF_TARGET_ELEMENT = 34963


def _pad4(b):
    pad = (4 - (len(b) % 4)) % 4
    return b + b"\x00" * pad


class GLBBuilder:
    def __init__(self, generator="granny3DModel.py"):
        self.gltf = {
            "asset": {"version": "2.0", "generator": generator},
            "scenes": [{"nodes": []}],
            "scene": 0,
            "nodes": [],
            "meshes": [],
            "buffers": [],
            "bufferViews": [],
            "accessors": [],
        }
        self.bin = bytearray()

    def add_buffer_view(self, data, target=None, byte_stride=None):
        offset = len(self.bin)
        self.bin += data
        bv = {"buffer": 0, "byteOffset": offset, "byteLength": len(data)}
        if target is not None:
            bv["target"] = target
        if byte_stride is not None:
            bv["byteStride"] = byte_stride
        # pad to 4 bytes
        pad = (4 - (len(self.bin) % 4)) % 4
        self.bin += b"\x00" * pad
        self.gltf["bufferViews"].append(bv)
        return len(self.gltf["bufferViews"]) - 1

    def add_accessor(self, bv_idx, count, component_type, type_, byte_offset=0,
                     mins=None, maxs=None, normalized=False):
        a = {
            "bufferView": bv_idx,
            "byteOffset": byte_offset,
            "componentType": component_type,
            "count": count,
            "type": type_,
        }
        if mins is not None:
            a["min"] = mins
        if maxs is not None:
            a["max"] = maxs
        if normalized:
            a["normalized"] = True
        self.gltf["accessors"].append(a)
        return len(self.gltf["accessors"]) - 1

    def build(self):
        # Finalize buffer
        bin_padded = _pad4(bytes(self.bin))
        self.gltf["buffers"] = [{"byteLength": len(bin_padded)}]
        json_bytes = json.dumps(self.gltf, separators=(",", ":")).encode("utf-8")
        json_padded = json_bytes + b" " * ((4 - (len(json_bytes) % 4)) % 4)
        total = 12 + 8 + len(json_padded) + 8 + len(bin_padded)
        header = struct.pack("<III", 0x46546C67, 2, total)
        json_chunk = (struct.pack("<II", len(json_padded), 0x4E4F534A)
                      + json_padded)
        bin_chunk = (struct.pack("<II", len(bin_padded), 0x004E4942)
                     + bin_padded)
        return header + json_chunk + bin_chunk


# ----------------------------------------------------------------------------
# Granny → glTF main pipeline
# ----------------------------------------------------------------------------
def _granny_color_from_ext(ext):
    """Pull a [r,g,b,a] baseColor from a Granny Material's ExtendedData bag.

    Maya and 3DS Max exporters use different key names; we try the common
    ones and fall back to None if no diffuse/color triple is present.
    """
    if not isinstance(ext, dict):
        return None
    # Maya naming, then 3DS Max naming, then generic.
    triples = [
        ("diffuseColorR", "diffuseColorG", "diffuseColorB"),
        ("defaultColorR", "defaultColorG", "defaultColorB"),
        ("colorR",        "colorG",        "colorB"),
        ("baseColorR",    "baseColorG",    "baseColorB"),
        ("Diffuse Color R", "Diffuse Color G", "Diffuse Color B"),
        ("Ambient Color R", "Ambient Color G", "Ambient Color B"),
    ]
    for r_k, g_k, b_k in triples:
        if r_k in ext and g_k in ext and b_k in ext:
            try:
                r = float(ext[r_k]); g = float(ext[g_k]); b = float(ext[b_k])
            except (TypeError, ValueError):
                continue
            # Granny stores these as 0..1 floats in our samples.
            return (max(0, min(1, r)), max(0, min(1, g)), max(0, min(1, b)), 1.0)
    return None


class GrannyToGltf:
    def __init__(self, doc: GrannyDocument):
        self.doc = doc
        self.walker = doc.walker
        self.fi = doc.fileinfo or {}
        self.glb = GLBBuilder()
        # Cache by both identity and a content key so duplicate pointer
        # targets (the walker materializes each Reference into a fresh dict)
        # collapse to a single glTF entry.
        self._tex_cache_id = {}
        self._tex_cache_key = {}
        self._mat_cache_id = {}
        self._mat_cache_key = {}
        # Compute the basis transform from the file's coord system to glTF
        # (Y-up, right-handed, -Z forward). ArtToolInfo records three basis
        # vectors (Right, Up, Back) expressed in the FILE's coordinate
        # system. To re-express a vertex into glTF's standard frame we
        # project it onto those basis vectors:
        #
        #     gltf.x = vertex . RightVector
        #     gltf.y = vertex . UpVector
        #     gltf.z = vertex . BackVector
        #
        # which is equivalent to M * v with M's rows = (Right, Up, Back).
        at = self.fi.get("ArtToolInfo") or {}
        self.row_x = tuple(at.get("RightVector") or (1.0, 0.0, 0.0))
        self.row_y = tuple(at.get("UpVector") or (0.0, 1.0, 0.0))
        self.row_z = tuple(at.get("BackVector") or (0.0, 0.0, -1.0))
        u_per_m = at.get("UnitsPerMeter") or 0.0
        if u_per_m and abs(u_per_m) > 1e-6 and abs(u_per_m - 1.0) > 1e-6:
            self.scale = 1.0 / float(u_per_m)
        else:
            self.scale = 1.0

    def _transform_vec3(self, v):
        x, y, z = float(v[0]), float(v[1]), float(v[2])
        gx = self.row_x[0] * x + self.row_x[1] * y + self.row_x[2] * z
        gy = self.row_y[0] * x + self.row_y[1] * y + self.row_y[2] * z
        gz = self.row_z[0] * x + self.row_z[1] * y + self.row_z[2] * z
        return (gx * self.scale, gy * self.scale, gz * self.scale)

    def _transform_dir(self, v):
        x, y, z = float(v[0]), float(v[1]), float(v[2])
        gx = self.row_x[0] * x + self.row_x[1] * y + self.row_x[2] * z
        gy = self.row_y[0] * x + self.row_y[1] * y + self.row_y[2] * z
        gz = self.row_z[0] * x + self.row_z[1] * y + self.row_z[2] * z
        return (gx, gy, gz)

    # ---- texture / material -----------------------------------------------
    def _texture_to_gltf(self, gtex):
        """Add a Granny Texture as a glTF image/sampler/texture, returning
        the texture index, or None if the Texture is null."""
        if not gtex:
            return None
        idkey = id(gtex)
        if idkey in self._tex_cache_id:
            return self._tex_cache_id[idkey]
        ckey = (gtex.get("FromFileName"), gtex.get("Width"),
                gtex.get("Height"), gtex.get("Encoding"),
                gtex.get("SubFormat"))
        if ckey in self._tex_cache_key:
            tex_idx = self._tex_cache_key[ckey]
            self._tex_cache_id[idkey] = tex_idx
            return tex_idx

        # Image entry: either an embedded PNG (if we can decode the pixels)
        # or an external URI taken from FromFileName.
        image = None
        w = int(gtex.get("Width") or 0)
        h = int(gtex.get("Height") or 0)
        images = gtex.get("Images") or []
        encoding = int(gtex.get("Encoding") or 0)
        # We can ONLY embed pixel data we know how to decode: raw RGBA / BGRA.
        # Bink-encoded textures (Encoding == 3) need GrannyBinkDecompressTexture,
        # which we don't currently invoke; we fall back to referencing the
        # external file.
        png_b64 = None
        if w > 0 and h > 0 and images and encoding == 0:
            try:
                from PIL import Image  # type: ignore
                mip0 = (images[0] or {}).get("MIPLevels") or []
                if mip0:
                    px = mip0[0].get("Pixels") or []
                    raw = bytes(p["UInt8"] for p in px)
                    layout = gtex.get("Layout") or {}
                    bpp = int(layout.get("BytesPerPixel") or 4)
                    shifts = layout.get("ShiftForComponent") or [0, 8, 16, 24]
                    bits = layout.get("BitsForComponent") or [8, 8, 8, 8]
                    if bpp == 4 and tuple(bits[:4]) == (8, 8, 8, 8) and len(raw) == w * h * 4:
                        # Re-order channels to match RGBA based on shifts.
                        ch_order = [shifts.index(0)//8, shifts.index(8)//8,
                                    shifts.index(16)//8, shifts.index(24)//8]
                        if ch_order == [0, 1, 2, 3]:
                            img = Image.frombytes("RGBA", (w, h), raw)
                        else:
                            # Generic shuffle.
                            import array
                            out = bytearray(len(raw))
                            for i in range(w * h):
                                px_word = int.from_bytes(raw[i*4:i*4+4], "little")
                                r = (px_word >> shifts[0]) & ((1 << bits[0]) - 1)
                                g = (px_word >> shifts[1]) & ((1 << bits[1]) - 1)
                                b = (px_word >> shifts[2]) & ((1 << bits[2]) - 1)
                                a = (px_word >> shifts[3]) & ((1 << bits[3]) - 1)
                                out[i*4:i*4+4] = bytes([r, g, b, a])
                            img = Image.frombytes("RGBA", (w, h), bytes(out))
                        import io, base64
                        bio = io.BytesIO()
                        img.save(bio, format="PNG", optimize=False)
                        png_b64 = base64.b64encode(bio.getvalue()).decode("ascii")
            except Exception:
                png_b64 = None

        from_path = gtex.get("FromFileName") or ""
        if png_b64 is not None:
            image = {"uri": "data:image/png;base64," + png_b64,
                     "name": os.path.basename(from_path) or "texture"}
        else:
            # Reference by basename; viewers will surface a missing-asset
            # warning, but the GLB itself is still valid.
            base = os.path.basename(from_path.replace("\\", "/")) if from_path else None
            image = {"uri": base or "missing.png",
                     "name": base or "texture"}
            if encoding != 0 and w > 0 and h > 0 and images:
                # Mark in the name that the embedded pixels were skipped.
                image["name"] = (base or "texture") + " (Bink-compressed; not embedded)"

        self.glb.gltf.setdefault("images", []).append(image)
        img_idx = len(self.glb.gltf["images"]) - 1

        # Sampler: default linear, repeat.
        if not self.glb.gltf.get("samplers"):
            self.glb.gltf["samplers"] = [{"magFilter": 9729, "minFilter": 9987,
                                           "wrapS": 10497, "wrapT": 10497}]
        sampler_idx = 0

        self.glb.gltf.setdefault("textures", []).append(
            {"sampler": sampler_idx, "source": img_idx}
        )
        tex_idx = len(self.glb.gltf["textures"]) - 1
        self._tex_cache_id[idkey] = tex_idx
        self._tex_cache_key[ckey] = tex_idx
        return tex_idx

    def _material_to_gltf(self, gmat):
        """Add a Granny Material as a glTF material; returns the index."""
        if not gmat:
            return None
        idkey = id(gmat)
        if idkey in self._mat_cache_id:
            return self._mat_cache_id[idkey]
        # Content-key dedupe: same Name + same texture file = same material.
        tex_ref = gmat.get("Texture") or {}
        ckey = (gmat.get("Name"),
                tex_ref.get("FromFileName") if tex_ref else None,
                tuple((s.get("Usage"), (s.get("Map") or {}).get("Name"))
                      for s in (gmat.get("Maps") or []) if s))
        if ckey in self._mat_cache_key:
            mat_idx = self._mat_cache_key[ckey]
            self._mat_cache_id[idkey] = mat_idx
            return mat_idx
        ext = gmat.get("ExtendedData") or {}
        base_color = _granny_color_from_ext(ext) or (0.8, 0.8, 0.8, 1.0)
        # Find a texture: either the Material.Texture direct ref, or look
        # inside Material.Maps for a "Diffuse Color"/"DiffuseMap"-flavoured
        # sub-material that itself has a Texture.
        tex_idx = self._texture_to_gltf(gmat.get("Texture"))
        if tex_idx is None:
            for sub in gmat.get("Maps") or []:
                if not sub: continue
                usage = (sub.get("Usage") or "").lower()
                sm = sub.get("Map")
                if sm and ("diffuse" in usage or "color" in usage or "albedo" in usage):
                    tex_idx = self._material_texture_recursive(sm)
                    if tex_idx is not None: break
            else:
                # last resort: pick any sub-material's texture
                for sub in gmat.get("Maps") or []:
                    if not sub: continue
                    sm = sub.get("Map")
                    if sm:
                        tex_idx = self._material_texture_recursive(sm)
                        if tex_idx is not None: break

        pbr = {"baseColorFactor": list(base_color),
               "metallicFactor": 0.0, "roughnessFactor": 0.9}
        if tex_idx is not None:
            pbr["baseColorTexture"] = {"index": tex_idx}
        mat = {
            "name": gmat.get("Name") or f"mat_{len(self._mat_cache_id)}",
            "pbrMetallicRoughness": pbr,
        }
        if ext.get("Two-sided") in (1, True, "true", "True"):
            mat["doubleSided"] = True
        self.glb.gltf.setdefault("materials", []).append(mat)
        mat_idx = len(self.glb.gltf["materials"]) - 1
        self._mat_cache_id[idkey] = mat_idx
        self._mat_cache_key[ckey] = mat_idx
        return mat_idx

    def _material_texture_recursive(self, gmat, depth=0):
        if depth > 4 or not gmat:
            return None
        if gmat.get("Texture"):
            return self._texture_to_gltf(gmat["Texture"])
        for sub in gmat.get("Maps") or []:
            if not sub: continue
            sm = sub.get("Map")
            if sm:
                t = self._material_texture_recursive(sm, depth + 1)
                if t is not None: return t
        return None

    def _build_materials(self):
        for gmat in self.fi.get("Materials") or []:
            self._material_to_gltf(gmat)

    def convert(self):
        self._build_materials()
        fi = self.fi
        # Build skin per-skeleton.
        skel_to_skin = {}
        skel_to_nodes = {}
        skel_to_inv = {}
        for skel_idx, skel in enumerate(fi.get("Skeletons", []) or []):
            if not skel:
                continue
            nodes, ibm = self._add_skeleton(skel)
            self._maybe_add_skin(skel_idx, nodes, ibm,
                                 skel_to_skin, skel_to_nodes, skel_to_inv,
                                 skel.get("Name", f"skeleton{skel_idx}"))

        # Find mesh -> skeleton mapping via Models -> MeshBindings
        mesh_to_skin = self._build_mesh_skin_map(skel_to_skin)

        # Convert meshes
        for mesh_idx, mesh in enumerate(fi.get("Meshes", []) or []):
            if not mesh:
                continue
            mesh_id = self._add_mesh(mesh, mesh_to_skin.get(mesh_idx))
            if mesh_id is None:
                continue
            node_idx = len(self.glb.gltf["nodes"])
            node = {
                "name": mesh.get("Name") or f"mesh_{mesh_idx}",
                "mesh": mesh_id,
            }
            skin_id = mesh_to_skin.get(mesh_idx)
            if skin_id is not None:
                node["skin"] = skin_id
            self.glb.gltf["nodes"].append(node)
            self.glb.gltf["scenes"][0]["nodes"].append(node_idx)

        # If we built skins but no meshes referenced them, still add the root
        # bone nodes to the scene so the skeleton hierarchy is visible.
        for skel_idx, nodes in skel_to_nodes.items():
            if not nodes:
                continue
            root_node = nodes[0]
            if root_node not in self.glb.gltf["scenes"][0]["nodes"]:
                # only add root if not already part of any skin-bound chain
                # in scene
                already = False
                for n in self.glb.gltf["scenes"][0]["nodes"]:
                    if n == root_node:
                        already = True
                if not already:
                    self.glb.gltf["scenes"][0]["nodes"].append(root_node)

        return self.glb.build()

    # ---- skeleton ---------------------------------------------------------
    def _add_skeleton(self, skel):
        bones = skel.get("Bones") or []
        bone_nodes = []
        inverse_world = []  # 4x4 column-major (glTF)
        # First create node objects
        for i, bone in enumerate(bones):
            name = bone.get("Name") or f"bone_{i}"
            lt = bone.get("LocalTransform") or {}
            tx = lt.get("translation", (0.0, 0.0, 0.0))
            rot = lt.get("rotation", (0.0, 0.0, 0.0, 1.0))
            scale = lt.get("scale_shear", (1, 0, 0, 0, 1, 0, 0, 0, 1))
            flags = lt.get("flags", 0)
            node = {"name": name}
            if flags & 0x1 == 0 and any(abs(v) > 1e-9 for v in tx):
                node["translation"] = list(tx)
            elif any(abs(v) > 1e-9 for v in tx):
                node["translation"] = list(tx)
            # Rotation as quat (x,y,z,w) in both Granny and glTF
            if any(abs(v - (1 if k == 3 else 0)) > 1e-9 for k, v in enumerate(rot)):
                node["rotation"] = list(rot)
            # Scale-shear: only set scale if it's a pure scale matrix
            sx = scale[0]; sy = scale[4]; sz = scale[8]
            is_pure = (
                abs(scale[1]) < 1e-6 and abs(scale[2]) < 1e-6 and
                abs(scale[3]) < 1e-6 and abs(scale[5]) < 1e-6 and
                abs(scale[6]) < 1e-6 and abs(scale[7]) < 1e-6
            )
            if is_pure:
                if abs(sx - 1) > 1e-6 or abs(sy - 1) > 1e-6 or abs(sz - 1) > 1e-6:
                    node["scale"] = [sx, sy, sz]
            bone_nodes.append(node)
        # Parent linkage
        first_node_idx = len(self.glb.gltf["nodes"])
        for i, bone in enumerate(bones):
            self.glb.gltf["nodes"].append(bone_nodes[i])
        for i, bone in enumerate(bones):
            children = []
            for j, b2 in enumerate(bones):
                if b2.get("ParentIndex", -1) == i:
                    children.append(first_node_idx + j)
            if children:
                self.glb.gltf["nodes"][first_node_idx + i]["children"] = children
        node_indices = [first_node_idx + i for i in range(len(bones))]
        # Inverse bind matrices from "InverseWorld4x4" if present
        ibms = []
        for bone in bones:
            iw = bone.get("InverseWorld4x4")
            if iw is None:
                # if not present we will compute identity (glTF tolerates this
                # but the bind will be wrong); some samples don't include it
                ibms.append([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1])
            else:
                # iw is a list of 16 floats already row-major; granny stores it
                # in column-major matching glTF convention so just pass through
                ibms.append(list(iw))
        return node_indices, ibms

    def _maybe_add_skin(self, skel_idx, nodes, ibm, skel_to_skin,
                         skel_to_nodes, skel_to_inv, name):
        skel_to_nodes[skel_idx] = nodes
        skel_to_inv[skel_idx] = ibm
        # Build inverse-bind-matrix buffer
        mat_bytes = bytearray()
        for m in ibm:
            mat_bytes += struct.pack("<16f", *m)
        bv = self.glb.add_buffer_view(bytes(mat_bytes))
        acc = self.glb.add_accessor(bv, len(ibm), GLTF_FLOAT, "MAT4")
        skin = {
            "name": name,
            "inverseBindMatrices": acc,
            "joints": nodes,
        }
        if nodes:
            # find root - bone with no parent inside this skel
            # We don't have easy access to original bones here, use first.
            skin["skeleton"] = nodes[0]
        self.glb.gltf.setdefault("skins", []).append(skin)
        skel_to_skin[skel_idx] = len(self.glb.gltf["skins"]) - 1

    # ---- mesh -------------------------------------------------------------
    def _build_mesh_skin_map(self, skel_to_skin):
        mesh_to_skin = {}
        fi = self.fi
        meshes = fi.get("Meshes") or []
        models = fi.get("Models") or []
        # Build mesh -> mesh_idx by identity match (dict ptrs)
        for model in models:
            if not model:
                continue
            skel = model.get("Skeleton")
            mb = model.get("MeshBindings") or []
            for binding in mb:
                if not binding:
                    continue
                m = binding.get("Mesh")
                if m is None:
                    continue
                for i, mesh in enumerate(meshes):
                    if mesh is m:
                        # find skeleton index by identity in fi.Skeletons
                        skel_list = fi.get("Skeletons") or []
                        for si, s in enumerate(skel_list):
                            if s is skel:
                                if si in skel_to_skin:
                                    mesh_to_skin[i] = skel_to_skin[si]
                                break
                        break
        return mesh_to_skin

    def _add_mesh(self, mesh, skin_idx):
        # Each Granny mesh has PrimaryVertexData + PrimaryTopology
        vdata = mesh.get("PrimaryVertexData")
        topo = mesh.get("PrimaryTopology")
        if not vdata or not topo:
            return None
        verts = vdata.get("Vertices") or []
        if not verts:
            return None
        # Determine layout by inspecting first vertex dict.
        sample = verts[0]
        # We need vertex type information to know binormal/normal/int sizes.
        # Walker decoded each member already, so we can directly use values
        # in sample dict.

        positions = []
        normals = []
        tangents = []
        binormals = []
        uvs = {}
        colors = None
        joints = None
        weights = None

        # Determine if BoneIndices/BoneWeights exist
        has_joints = "BoneIndices" in sample
        has_weights = "BoneWeights" in sample

        for v in verts:
            if "Position" in v:
                p = v["Position"]
                positions.append(self._transform_vec3(p[:3]))
            if "Normal" in v:
                n = v["Normal"]
                normals.append(self._transform_dir(n[:3]))
            if "Tangent" in v:
                t = v["Tangent"]
                tangents.append(self._transform_dir(t[:3]))
            if "Binormal" in v:
                b = v["Binormal"]
                binormals.append(self._transform_dir(b[:3]))
            for key in v:
                if key.startswith("TextureCoordinates"):
                    uv = v[key]
                    uvs.setdefault(key, []).append(
                        tuple(float(x) for x in uv[:2])
                    )
            if "DiffuseColor" in v:
                if colors is None:
                    colors = []
                colors.append(tuple(float(x) / 255.0 if isinstance(x, int)
                                    else float(x)
                                    for x in v["DiffuseColor"][:4]))
            if has_joints:
                ji = v.get("BoneIndices") or []
                if isinstance(ji, list):
                    j = [int(x) for x in ji[:4]]
                else:
                    j = [int(ji)]
                while len(j) < 4:
                    j.append(0)
                if joints is None:
                    joints = []
                joints.append(tuple(j))
            if has_weights:
                bw = v.get("BoneWeights") or []
                if isinstance(bw, list):
                    w = [float(x) for x in bw[:4]]
                else:
                    w = [float(bw)]
                while len(w) < 4:
                    w.append(0.0)
                # Granny stores byte weights 0-255; normalize.
                if any(x > 1.0 for x in w):
                    w = [x / 255.0 for x in w]
                s = sum(w)
                if s > 0 and abs(s - 1.0) > 1e-3:
                    w = [x / s for x in w]
                if weights is None:
                    weights = []
                weights.append(tuple(w))

        if not positions:
            return None

        # Triangle indices
        indices = self._extract_indices(topo)
        if not indices:
            return None

        # Build buffers
        attributes = {}
        # POSITION
        pb = bytearray()
        mins = [float("inf")] * 3
        maxs = [float("-inf")] * 3
        for p in positions:
            for k in range(3):
                if p[k] < mins[k]: mins[k] = p[k]
                if p[k] > maxs[k]: maxs[k] = p[k]
            pb += struct.pack("<3f", *p)
        bv = self.glb.add_buffer_view(bytes(pb), target=GLTF_TARGET_ARRAY)
        acc = self.glb.add_accessor(bv, len(positions), GLTF_FLOAT, "VEC3",
                                     mins=mins, maxs=maxs)
        attributes["POSITION"] = acc

        if normals and len(normals) == len(positions):
            nb = bytearray()
            for n in normals:
                # Normalize (just in case)
                ln = (n[0]*n[0] + n[1]*n[1] + n[2]*n[2]) ** 0.5
                if ln > 1e-9:
                    nb += struct.pack("<3f", n[0]/ln, n[1]/ln, n[2]/ln)
                else:
                    nb += struct.pack("<3f", 0.0, 0.0, 1.0)
            bv = self.glb.add_buffer_view(bytes(nb), target=GLTF_TARGET_ARRAY)
            acc = self.glb.add_accessor(bv, len(normals), GLTF_FLOAT, "VEC3")
            attributes["NORMAL"] = acc

        # UV sets - sort numerically by suffix
        sorted_uvs = sorted(uvs.items())
        uv_acc_map = {}
        for ki, (key, uvlist) in enumerate(sorted_uvs):
            if len(uvlist) != len(positions):
                continue
            ub = bytearray()
            for u in uvlist:
                ub += struct.pack("<2f", u[0], u[1])
            bv = self.glb.add_buffer_view(bytes(ub), target=GLTF_TARGET_ARRAY)
            acc = self.glb.add_accessor(bv, len(uvlist), GLTF_FLOAT, "VEC2")
            uv_acc_map[ki] = acc
            attributes[f"TEXCOORD_{ki}"] = acc

        if joints and weights and skin_idx is not None and len(joints) == len(positions):
            jb = bytearray()
            for j in joints:
                jb += struct.pack("<4H", *(min(65535, x) for x in j))
            bv = self.glb.add_buffer_view(bytes(jb), target=GLTF_TARGET_ARRAY)
            acc = self.glb.add_accessor(bv, len(joints), GLTF_USHORT, "VEC4")
            attributes["JOINTS_0"] = acc

            wb = bytearray()
            for w in weights:
                wb += struct.pack("<4f", *w)
            bv = self.glb.add_buffer_view(bytes(wb), target=GLTF_TARGET_ARRAY)
            acc = self.glb.add_accessor(bv, len(weights), GLTF_FLOAT, "VEC4")
            attributes["WEIGHTS_0"] = acc

        # COLORS (per-vertex DiffuseColor, if present)
        if colors and len(colors) == len(positions):
            cb = bytearray()
            for c in colors:
                cb += struct.pack("<4f", *c)
            bv = self.glb.add_buffer_view(bytes(cb), target=GLTF_TARGET_ARRAY)
            acc = self.glb.add_accessor(bv, len(colors), GLTF_FLOAT, "VEC4")
            attributes["COLOR_0"] = acc

        # Split into one primitive per TriTopology.Group.
        # Each group is a contiguous run of triangles (TriFirst..TriFirst+TriCount-1)
        # using a specific MaterialIndex into mesh.MaterialBindings.
        groups = topo.get("Groups") or []
        # If no groups, treat the whole mesh as a single group.
        if not groups:
            groups = [{"MaterialIndex": 0, "TriFirst": 0,
                       "TriCount": len(indices) // 3}]

        # Resolve MaterialIndex -> glTF material id via MaterialBindings.
        mat_bindings = mesh.get("MaterialBindings") or []
        def resolve_material(mi):
            if mi < 0 or mi >= len(mat_bindings):
                return None
            b = mat_bindings[mi]
            if not b:
                return None
            return self._material_to_gltf(b.get("Material"))

        primitives = []
        for g in groups:
            tri_first = int(g.get("TriFirst") or 0)
            tri_count = int(g.get("TriCount") or 0)
            if tri_count <= 0:
                continue
            seg = indices[tri_first * 3:(tri_first + tri_count) * 3]
            if not seg:
                continue
            if max(seg) < 65536:
                ib = struct.pack(f"<{len(seg)}H", *seg)
                comp = GLTF_USHORT
                if len(ib) % 4 != 0:
                    ib += b"\x00\x00"
            else:
                ib = struct.pack(f"<{len(seg)}I", *seg)
                comp = GLTF_UINT
            bv = self.glb.add_buffer_view(ib, target=GLTF_TARGET_ELEMENT)
            idx_acc = self.glb.add_accessor(bv, len(seg), comp, "SCALAR")

            prim = {"attributes": attributes, "indices": idx_acc, "mode": 4}
            mat_idx = resolve_material(int(g.get("MaterialIndex") or 0))
            if mat_idx is not None:
                prim["material"] = mat_idx
            primitives.append(prim)

        if not primitives:
            return None

        mesh_obj = {
            "name": mesh.get("Name") or "mesh",
            "primitives": primitives,
        }
        self.glb.gltf["meshes"].append(mesh_obj)
        return len(self.glb.gltf["meshes"]) - 1

    def _extract_indices(self, topo):
        """Return a flat list of triangle indices for the topology.

        Granny stores indices as either ``Indices`` (32-bit) or ``Indices16``
        (16-bit). The walker reads each as a list of single-field structs
        (the subtype is a one-member type def), so we unwrap them here.
        """
        for key in ("Indices", "Indices16"):
            lst = topo.get(key)
            if not lst:
                continue
            out = []
            for entry in lst:
                if isinstance(entry, dict):
                    # take the single value
                    for v in entry.values():
                        out.append(int(v))
                        break
                else:
                    out.append(int(entry))
            if out:
                return out
        return []


# ----------------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------------
def convert(input_path, output_path):
    gr = GrannyFile.from_path(input_path)
    doc = GrannyDocument(gr)
    if not doc.has_content:
        raise SystemExit(
            "File contains no mesh / model data (animation-only or "
            "stub Granny file - nothing to convert)."
        )
    g2g = GrannyToGltf(doc)
    glb = g2g.convert()
    with open(output_path, "wb") as f:
        f.write(glb)
    try:
        os.chmod(output_path, 0o664)
    except OSError:
        pass


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Convert a Granny GR2 3D model to glTF GLB"
    )
    p.add_argument("input")
    p.add_argument("output")
    args = p.parse_args(argv)
    convert(args.input, args.output)


if __name__ == "__main__":
    main()

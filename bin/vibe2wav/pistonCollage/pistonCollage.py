#!/usr/bin/env python3
# Vibe coded by Codex

from __future__ import annotations

from pathlib import Path
import struct
import subprocess
import sys
from typing import Iterable


ROOT = Path(__file__).resolve().parent
SUPPORT = ROOT / "pistonCollage_support"
HELPER = ROOT / "pxtone_render"


class FormatError(Exception):
    pass


class Reader:
    def __init__(self, data: bytes, name: str):
        self.data = data
        self.pos = 0
        self.name = name

    def require(self, n: int) -> bytes:
        if n < 0 or self.pos + n > len(self.data):
            raise FormatError(f"{self.name}: unexpected end at byte {self.pos}")
        out = self.data[self.pos : self.pos + n]
        self.pos += n
        return out

    def u8(self) -> int:
        return self.require(1)[0]

    def i8(self) -> int:
        return struct.unpack("<b", self.require(1))[0]

    def u16(self) -> int:
        return struct.unpack("<H", self.require(2))[0]

    def i16(self) -> int:
        return struct.unpack("<h", self.require(2))[0]

    def u32(self) -> int:
        return struct.unpack("<I", self.require(4))[0]

    def i32(self) -> int:
        return struct.unpack("<i", self.require(4))[0]

    def f32(self) -> float:
        return struct.unpack("<f", self.require(4))[0]

    def var(self) -> int:
        raw = []
        for _ in range(5):
            b = self.u8()
            raw.append(b)
            if not b & 0x80:
                break
        else:
            raise FormatError(f"{self.name}: overlong variable integer at byte {self.pos}")
        val = 0
        shift = 0
        for b in raw:
            val |= (b & 0x7F) << shift
            shift += 7
        return val

    def eof(self) -> None:
        if self.pos != len(self.data):
            raise FormatError(f"{self.name}: {len(self.data) - self.pos} trailing byte(s)")


EVENT_KIND_MAX = 16
PTV_VOICEFLAG_UNCOVERED = 0xFFFFFFF8
PTV_DATAFLAG_UNCOVERED = 0xFFFFFFFC
PTV_DATAFLAG_WAVE = 0x00000001
PTV_DATAFLAG_ENVELOPE = 0x00000002
NOISEEDITFLAG_UNCOVERED = 0xFFFFFF83
NOISEEDITFLAG_ENVELOPE = 0x0004
NOISEEDITFLAG_PAN = 0x0008
NOISEEDITFLAG_OSC_MAIN = 0x0010
NOISEEDITFLAG_OSC_FREQ = 0x0020
NOISEEDITFLAG_OSC_VOLU = 0x0040
PX_WAVETYPE_NUM = 16
MAX_NOISE_UNITS = 4
MAX_NOISE_ENVELOPES = 3


def _expect_size(tag: bytes, got: int, want: int) -> None:
    if got != want:
        raise FormatError(f"{tag.decode('latin1')}: size {got}, expected {want}")


def parse_var_event_pair(r: Reader) -> None:
    r.var()
    r.var()


def parse_master_v5(r: Reader) -> None:
    size = r.u32()
    _expect_size(b"MasterV5", size, 15)
    beat_clock = r.i16()
    beat_num = r.i8()
    r.f32()
    r.i32()
    r.i32()
    if beat_clock <= 0 or beat_num <= 0:
        raise FormatError("MasterV5: invalid beat clock/count")


def parse_event_v5(r: Reader) -> None:
    declared = r.i32()
    count = r.i32()
    if declared < 4 or count < 0:
        raise FormatError("Event V5: invalid size or count")
    for _ in range(count):
        r.var()
        r.u8()
        kind = r.u8()
        if kind >= EVENT_KIND_MAX:
            raise FormatError(f"Event V5: event kind {kind} out of range")
        r.var()


def parse_even_mast(r: Reader) -> None:
    size = r.i32()
    start = r.pos
    data_num = r.u16()
    r.u16()
    count = r.u32()
    if data_num != 3:
        raise FormatError("evenMAST: data_num must be 3")
    for _ in range(count):
        status = r.var()
        r.var()
        r.var()
        if status not in {7, 8, 9, 10, 11}:
            raise FormatError(f"evenMAST: invalid master status {status}")


def parse_even_unit(r: Reader, tail_absolute: bool = False, check_rrr: bool = True) -> None:
    size = r.i32()
    start = r.pos
    unit = r.u16()
    kind = r.u16()
    data_num = r.u16()
    rrr = r.u16()
    count = r.u32()
    if data_num != 2 or kind >= EVENT_KIND_MAX:
        raise FormatError("evenUNIT: invalid event header")
    if check_rrr and rrr:
        raise FormatError("evenUNIT: reserved field is non-zero")
    for _ in range(count):
        parse_var_event_pair(r)
    if unit > 255:
        raise FormatError("evenUNIT: unit index out of range")


def parse_ptnoise_bytes(data: bytes, name: str) -> None:
    r = Reader(data, name)
    if r.require(8) != b"PTNOISE-":
        raise FormatError("PTNOISE: bad magic")
    version = r.u32()
    if version > 20120418:
        raise FormatError("PTNOISE: unsupported future version")
    r.var()
    unit_num = r.i8()
    if unit_num < 0 or unit_num > MAX_NOISE_UNITS:
        raise FormatError("PTNOISE: invalid unit count")
    for _ in range(unit_num):
        flags = r.var()
        if flags & NOISEEDITFLAG_UNCOVERED:
            raise FormatError("PTNOISE: unknown unit flags")
        if flags & NOISEEDITFLAG_ENVELOPE:
            env_num = r.var()
            if env_num > MAX_NOISE_ENVELOPES:
                raise FormatError("PTNOISE: too many envelope points")
            for _ in range(env_num):
                r.var()
                r.var()
        if flags & NOISEEDITFLAG_PAN:
            r.i8()
        for mask in (NOISEEDITFLAG_OSC_MAIN, NOISEEDITFLAG_OSC_FREQ, NOISEEDITFLAG_OSC_VOLU):
            if flags & mask:
                wave_type = r.var()
                if wave_type >= PX_WAVETYPE_NUM:
                    raise FormatError("PTNOISE: oscillator wave type out of range")
                r.var()
                r.var()
                r.var()
                r.var()
    r.eof()


def parse_ptvoice_payload(r: Reader, end: int | None = None) -> None:
    start = r.pos
    if r.require(8) != b"PTVOICE-":
        raise FormatError("PTVOICE: bad magic")
    version = r.i32()
    total = r.i32()
    if version > 20060111 or total < 0:
        raise FormatError("PTVOICE: unsupported version or negative size")
    declared_end = start + 16 + total
    limit = end if end is not None else len(r.data)
    if declared_end > limit:
        raise FormatError("PTVOICE: size exceeds file")
    r.var()
    if r.var() or r.var():
        raise FormatError("PTVOICE: reserved fields are non-zero")
    voice_num = r.var()
    if voice_num < 0 or voice_num > 2:
        raise FormatError("PTVOICE: invalid voice count")
    for _ in range(voice_num):
        r.var()
        r.var()
        r.var()
        r.var()
        voice_flags = r.var()
        data_flags = r.var()
        if voice_flags & PTV_VOICEFLAG_UNCOVERED:
            raise FormatError("PTVOICE: unknown voice flags")
        if data_flags & PTV_DATAFLAG_UNCOVERED:
            raise FormatError("PTVOICE: unknown data flags")
        if data_flags & PTV_DATAFLAG_WAVE:
            voice_type = r.var()
            if voice_type == 0:
                n = r.var()
                r.var()
                for _ in range(n):
                    r.u8()
                    r.i8()
            elif voice_type == 1:
                n = r.var()
                for _ in range(n):
                    r.var()
                    r.var()
            else:
                raise FormatError("PTVOICE: unsupported wave type")
        if data_flags & PTV_DATAFLAG_ENVELOPE:
            r.var()
            head = r.var()
            body = r.var()
            tail = r.var()
            if body != 0 or tail != 1:
                raise FormatError("PTVOICE: unsupported envelope layout")
            for _ in range(head + body + tail):
                r.var()
                r.var()
    if r.pos != limit:
        raise FormatError("PTVOICE: parsed byte count does not match container size")


def parse_ptvoice_bytes(data: bytes, name: str) -> None:
    r = Reader(data, name)
    parse_ptvoice_payload(r)
    r.eof()


def parse_mate_pcm(r: Reader) -> None:
    size = r.i32()
    start = r.pos
    r.u16()
    r.u16()
    voice_flags = r.u32()
    ch = r.u16()
    bps = r.u16()
    r.u32()
    r.f32()
    data_size = r.u32()
    if voice_flags & PTV_VOICEFLAG_UNCOVERED:
        raise FormatError("matePCM: unknown voice flags")
    if ch not in (1, 2) or bps not in (8, 16):
        raise FormatError("matePCM: unsupported PCM shape")
    if size != 24 + data_size:
        raise FormatError("matePCM: data size does not match chunk size")
    r.require(data_size)
    if r.pos - start != size:
        raise FormatError("matePCM: parsed byte count does not match chunk size")


def parse_mate_ptn(r: Reader) -> None:
    size = r.i32()
    start = r.pos
    r.u16()
    r.u16()
    voice_flags = r.u32()
    r.f32()
    rrr = r.i32()
    if voice_flags & PTV_VOICEFLAG_UNCOVERED or rrr not in (0, 1):
        raise FormatError("matePTN: unsupported material header")
    end = start + size
    parse_ptnoise_bytes(r.data[r.pos:end], "embedded PTNOISE")
    r.pos = end


def parse_mate_ptv(r: Reader) -> None:
    size = r.i32()
    start = r.pos
    r.u16()
    r.u16()
    r.f32()
    ptv_size = r.i32()
    if size != 12 + ptv_size:
        raise FormatError("matePTV: embedded size mismatch")
    end = start + size
    parse_ptvoice_payload(r, end)
    if r.pos != end:
        raise FormatError("matePTV: parsed byte count does not match chunk size")


def parse_mate_oggv(r: Reader) -> None:
    size = r.i32()
    start = r.pos
    r.u16()
    r.u16()
    voice_flags = r.u32()
    r.f32()
    if voice_flags & PTV_VOICEFLAG_UNCOVERED:
        raise FormatError("mateOGGV: unknown voice flags")
    r.i32()
    r.i32()
    r.i32()
    ogg_size = r.i32()
    if ogg_size <= 0 or size != 28 + ogg_size:
        raise FormatError("mateOGGV: invalid Ogg payload size")
    payload = r.require(ogg_size)
    if not payload.startswith(b"OggS"):
        raise FormatError("mateOGGV: payload is not an Ogg stream")
    if r.pos - start != size:
        raise FormatError("mateOGGV: parsed byte count does not match chunk size")


def parse_fixed_chunk(r: Reader, tag: bytes, allowed_sizes: Iterable[int] | None = None) -> None:
    size = r.i32()
    if allowed_sizes is not None and size not in allowed_sizes:
        raise FormatError(f"{tag.decode('latin1')}: unexpected size {size}")
    r.require(size)


def parse_module_bytes(data: bytes, name: str) -> None:
    r = Reader(data, name)
    version = r.require(16)
    versions_with_exe = {
        b"PTTUNE--20060115",
        b"PTTUNE--20060930",
        b"PTTUNE--20071119",
        b"PTCOLLAGE-060115",
        b"PTCOLLAGE-060930",
        b"PTCOLLAGE-071119",
    }
    if version not in versions_with_exe:
        raise FormatError("module: unsupported magic/version")
    r.u16()
    reserved = r.u16()
    if reserved:
        raise FormatError("module: non-zero version reserved field")
    while True:
        tag = r.require(8)
        if tag == b"pxtoneND":
            if r.u32() != 0:
                raise FormatError("pxtoneND: terminator size must be zero")
            r.eof()
            return
        if tag == b"MasterV5":
            parse_master_v5(r)
        elif tag == b"Event V5":
            parse_event_v5(r)
        elif tag == b"evenMAST":
            parse_even_mast(r)
        elif tag == b"evenUNIT":
            parse_even_unit(r)
        elif tag == b"matePCM ":
            parse_mate_pcm(r)
        elif tag == b"matePTN ":
            parse_mate_ptn(r)
        elif tag == b"matePTV ":
            parse_mate_ptv(r)
        elif tag == b"mateOGGV":
            parse_mate_oggv(r)
        elif tag == b"effeDELA":
            parse_fixed_chunk(r, tag, {12})
        elif tag == b"effeOVER":
            parse_fixed_chunk(r, tag, {16})
        elif tag == b"textNAME" or tag == b"textCOMM":
            parse_fixed_chunk(r, tag)
        elif tag == b"assiWOIC" or tag == b"assiUNIT":
            parse_fixed_chunk(r, tag, {20})
        elif tag == b"num UNIT":
            parse_fixed_chunk(r, tag, {4})
        elif tag == b"pxtnUNIT":
            parse_fixed_chunk(r, tag, {4})
        else:
            raise FormatError(f"module: unknown tag {tag!r} at byte {r.pos - 8}")


def validate_file(path: Path) -> str:
    data = path.read_bytes()
    if data.startswith(b"PTVOICE-"):
        parse_ptvoice_bytes(data, str(path))
        return "voice"
    if data.startswith(b"PTNOISE-"):
        parse_ptnoise_bytes(data, str(path))
        return "noise"
    if data.startswith((b"PTTUNE--", b"PTCOLLAGE-")):
        parse_module_bytes(data, str(path))
        return "module"
    raise FormatError(f"{path}: not a supported Piston/PxTone file")


def chmod_readable(path: Path, executable: bool = False) -> None:
    path.chmod(0o775 if executable else 0o664)


def output_name(input_path: Path) -> str:
    return input_path.stem + ".wav"


def convert(input_path: Path, output_dir: Path) -> Path:
    validate_file(input_path)
    if not HELPER.is_file():
        raise FileNotFoundError(f"{HELPER} is missing; run ./build_pxtone_render.sh")
    if not os_access_executable(HELPER):
        raise PermissionError(f"{HELPER} is not executable; run chmod 775 {HELPER.name}")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_dir.chmod(0o775)
    out = output_dir / output_name(input_path)
    tmp = output_dir / ("." + out.name + ".tmp")
    if tmp.exists():
        tmp.unlink()
    try:
        subprocess.run([str(HELPER), str(input_path), str(tmp)], check=True)
        tmp.replace(out)
        chmod_readable(out)
        return out
    except Exception:
        if tmp.exists():
            tmp.unlink()
        raise


def os_access_executable(path: Path) -> bool:
    return path.stat().st_mode & 0o111 != 0


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: pistonCollage.py <inputFile> <outputDir>", file=sys.stderr)
        return 2
    input_path = Path(argv[1])
    output_dir = Path(argv[2])
    if not input_path.is_file():
        print(f"input is not a file: {input_path}", file=sys.stderr)
        return 2
    try:
        out = convert(input_path, output_dir)
    except (FormatError, subprocess.CalledProcessError, OSError) as exc:
        print(f"pistonCollage: {exc}", file=sys.stderr)
        return 1
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

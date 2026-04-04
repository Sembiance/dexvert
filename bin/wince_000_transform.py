#!/usr/bin/env python3
# Vibe coded by Claude
"""
Windows CE CAB .000 Provision File Extractor

Parses the MSCE header (.000 file) from an extracted Windows CE CAB and
renames the companion .NNN data files in-place into their original filenames
and directory structure.

Usage: wince_cab_extract.py <path-to-.000-file>

Reference: https://www.cabextract.org.uk/wince_cab_format/
"""

import os
import re
import struct
import sys
from dataclasses import dataclass

# %CEn% directory shortcuts (Handheld PC standard)
CE_DIRS = {
    1: r"\Program Files",
    2: r"\Windows",
    3: r"\Windows\Desktop",
    4: r"\Windows\StartUp",
    5: r"\My Documents",
    6: r"\Program Files\Accessories",
    7: r"\Program Files\Communications",
    8: r"\Program Files\Games",
    9: r"\Program Files\Pocket Outlook",
    10: r"\Program Files\Office",
    11: r"\Windows\Programs",
    12: r"\Windows\Programs\Accessories",
    13: r"\Windows\Programs\Communications",
    14: r"\Windows\Programs\Games",
    15: r"\Windows\Fonts",
    16: r"\Windows\Recent",
    17: r"\Windows\Favorites",
}

ARCHITECTURES = {
    0: "Any", 103: "SHx SH3", 104: "SHx SH4", 386: "Intel 386",
    486: "Intel 486", 586: "Intel Pentium", 601: "PowerPC 601",
    603: "PowerPC 603", 604: "PowerPC 604", 620: "PowerPC 620",
    821: "Motorola 821", 1824: "ARM 720", 2080: "ARM 820",
    2336: "ARM 920", 2577: "StrongARM", 4000: "MIPS R4000",
    10003: "Hitachi SH3", 10004: "Hitachi SH3E", 10005: "Hitachi SH4",
    21064: "Alpha 21064", 70001: "ARM 7TDMI",
}


@dataclass
class FileEntry:
    id: int
    dir_id: int
    flags: int
    filename: str


class MSCEParser:
    """Parser for Windows CE .000 provision files."""

    def __init__(self, data: bytes):
        self.data = data
        self.app_name = ""
        self.provider = ""
        self.architecture = 0
        self.strings = {}
        self.dirs = {}
        self.files = []

    def u16(self, off):
        return struct.unpack_from("<H", self.data, off)[0]

    def u32(self, off):
        return struct.unpack_from("<I", self.data, off)[0]

    def cstr(self, off, length):
        return self.data[off:off + length].rstrip(b"\x00").decode("ascii", errors="replace")

    def parse(self):
        if len(self.data) < 100:
            raise ValueError("File too small for MSCE header")
        if self.data[0:4] != b"MSCE":
            raise ValueError(f"Bad magic: expected 'MSCE', got {self.data[0:4]!r}")

        self.architecture = self.u32(20)
        num_strings = self.u16(48)
        num_dirs = self.u16(50)
        num_files = self.u16(52)
        off_strings = self.u32(60)
        off_dirs = self.u32(64)
        off_files = self.u32(68)

        app_off, app_len = self.u16(84), self.u16(86)
        prov_off, prov_len = self.u16(88), self.u16(90)
        if app_len:
            self.app_name = self.cstr(app_off, app_len)
        if prov_len:
            self.provider = self.cstr(prov_off, prov_len)

        # Strings
        off = off_strings
        for _ in range(num_strings):
            sid, slen = self.u16(off), self.u16(off + 2)
            self.strings[sid] = self.cstr(off + 4, slen)
            off += 4 + slen

        # Directories
        off = off_dirs
        for _ in range(num_dirs):
            did, dlen = self.u16(off), self.u16(off + 2)
            ids = []
            pos, end = off + 4, off + 4 + dlen
            while pos < end:
                val = self.u16(pos)
                pos += 2
                if val == 0:
                    break
                ids.append(val)
            self.dirs[did] = ids
            off += 4 + dlen

        # Files
        off = off_files
        for _ in range(num_files):
            fid = self.u16(off)
            did = self.u16(off + 2)
            # off+4: unknown uint16 (typically == fid)
            flags = self.u32(off + 6)
            nlen = self.u16(off + 10)
            name = self.cstr(off + 12, nlen)
            self.files.append(FileEntry(id=fid, dir_id=did, flags=flags, filename=name))
            off += 12 + nlen

    def resolve_dir(self, dir_id):
        if dir_id not in self.dirs:
            return ""
        parts = [self.strings.get(sid, f"str{sid}") for sid in self.dirs[dir_id]]
        return "\\".join(parts)


def sanitize_path(path):
    """Convert a WinCE path to a safe local path."""
    def replace_ce(m):
        n = int(m.group(1))
        return CE_DIRS.get(n, f"CE{n}").replace("\\", "/").lstrip("/")

    path = re.sub(r"%CE(\d+)%", replace_ce, path)
    path = path.replace("\\", "/").lstrip("/")
    parts = [p for p in path.split("/") if p and p not in ("..", ".")]
    return os.path.join(*parts) if parts else ""


def find_nnn_file(source_dir, file_id):
    """Find the .NNN file matching a file_id."""
    ext = f".{file_id:03d}"
    for entry in os.listdir(source_dir):
        if entry.lower().endswith(ext.lower()):
            return os.path.join(source_dir, entry)
    return None


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path-to-.000-file>", file=sys.stderr)
        sys.exit(1)

    provision_file = sys.argv[1]
    if not os.path.isfile(provision_file):
        print(f"Error: {provision_file} not found", file=sys.stderr)
        sys.exit(1)

    source_dir = os.path.dirname(os.path.abspath(provision_file))

    with open(provision_file, "rb") as fh:
        data = fh.read()

    p = MSCEParser(data)
    p.parse()

    arch = ARCHITECTURES.get(p.architecture, f"Unknown ({p.architecture})")
    print(f"{p.app_name} by {p.provider} [{arch}]")
    print(f"{len(p.files)} files")
    print()

    moved = 0
    for f in p.files:
        nnn_path = find_nnn_file(source_dir, f.id)
        if not nnn_path:
            print(f"  MISSING .{f.id:03d} for '{f.filename}'")
            continue

        dir_path = sanitize_path(p.resolve_dir(f.dir_id))
        dest_dir = os.path.join(source_dir, dir_path) if dir_path else source_dir
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, f.filename)

        os.rename(nnn_path, dest_path)
        rel = os.path.relpath(dest_path, source_dir)
        print(f"  {os.path.basename(nnn_path)} -> {rel}")
        moved += 1

    # Handle .999 setup DLL if present
    setup_path = find_nnn_file(source_dir, 999)
    if setup_path:
        dest = os.path.join(source_dir, "_setup.dll")
        os.rename(setup_path, dest)
        print(f"  {os.path.basename(setup_path)} -> _setup.dll")
        moved += 1

    # Remove the .000 manifest itself
    os.remove(provision_file)
    print()
    print(f"Done. {moved} files renamed, manifest removed.")


if __name__ == "__main__":
    main()

#!/usr/bin/python3
import os
import re
from io import BytesIO
from struct import pack, unpack
from sys import argv
from zlib import decompress

imap_pos = 0xC
int_mmap_pos = 0x18
mmap_pos = 0x2C


def read_ident(f):
    sig = f.read(4)
    if sig in [b"XFIR", b"FFIR"]:
        end = "<"
    elif sig in [b"RIFX", b"RIFF"]:
        end = ">"
    else:
        end = None
    return end


def read_tag(f, endian="<"):
    tag = f.read(4)
    if endian == "<":
        tag = tag[::-1]
    return tag.decode("ascii")


def read_i16(f, endian="<"):
    (data,) = unpack(endian + "H", f.read(2))
    return data


def read_i32(f, endian="<"):
    (data,) = unpack(endian + "I", f.read(4))
    return data


def write_i32(f, data, endian="<"):
    data = pack(endian + "I", data)
    f.write(data)
    return


def parse_dict(data, endian="<"):
    d = BytesIO(data[8:])
    (toclen,) = unpack(endian + "I", d.read(4))
    if toclen > 0x10000:
        # Win16 EXEs swap endianness after the tag size
        endian = {">": "<", "<": ">"}[endian]
        d.seek(0)
        (toclen,) = unpack(endian + "I", d.read(4))
    d.seek(0x10)
    (len_names,) = unpack(endian + "I", d.read(4))
    d.seek(0x18)
    d.read(toclen)
    unk1 = read_i16(d, endian)
    d.read(unk1 - 0x12)  # ??????????
    names = []
    for i in range(len_names):
        (lname,) = unpack(endian + "I", d.read(4))
        fname = d.read(lname)
        assert lname == len(fname)
        d.read(-lname % 4)
        try:
            names.append(fname.decode("utf-8"))
        except UnicodeDecodeError:
            names.append(fname.decode("shift-jis"))
    return names


file = argv[1]
f = open(file, "rb").read()
win_file = re.search(rb"XFIR.{4}LPPA", f, re.S)
mac_file = re.search(rb"RIFX.{4}APPL", f, re.S)
if win_file:
    off = win_file.start()
elif mac_file:
    off = mac_file.start()
else:
    print("not a Director application")
    exit(1)

print(f"SW file found at 0x{off:x}")
f = BytesIO(f[off:])
endian = read_ident(f)
f.seek(imap_pos)
assert read_tag(f, endian) == "imap"
f.seek(0x8, 1)
off = unpack(endian + "I", f.read(4))[0] - mmap_pos
f.seek(mmap_pos)
assert read_tag(f, endian) == "mmap"
f.seek(mmap_pos + 0xA)
mmap_res_len = read_i16(f, endian)
f.seek(mmap_pos + 0x10)
mmap_res_count = read_i32(f, endian)
mmap_ress_pos = mmap_pos + 0x20
f.seek(mmap_ress_pos + 0x8)
REL = read_i32(f, endian)
files = []
names = None
for i in range(mmap_res_count):
    f.seek((i * mmap_res_len) + mmap_ress_pos)
    tag = read_tag(f, endian)
    size, off = unpack(endian + "II", f.read(0x8))
    size += 8
    if off:
        off -= REL

    if tag == "File":
        files.append((off, size))
    elif tag == "Dict":
        f.seek(off)
        names = parse_dict(f.read(size), endian)

files = list(zip(names, files))
outfolder, _ = os.path.splitext(argv[1])
if outfolder == argv[1]:
    outfolder += "_out"
try:
    os.mkdir(outfolder)
except FileExistsError:
    pass

for name, file in [f for f in files if not re.search(r"\.x(?:16|32)$", f[0], re.I)]:
    if win_file:
        (oname,) = re.findall(r"([^\\]+)$", name)
    else:
        # Director uses `:` as the path separator on Mac, even Intel/OSX!
        (oname,) = re.findall(r"([^:]+)$", name)
    off, _ = file
    print(f"Original file path: {os.path.join(name)} @ 0x{off:x}")
    # The size indicated in the memory map is sometimes wrong (??),
    # so we need to get the real size from the header of the Director file
    f.seek(off + 4)
    size = read_i32(f, endian) + 8
    f.seek(off)
    temp_file = BytesIO(f.read(size))
    temp_file_endian = read_ident(temp_file)
    temp_file.seek(0x8)
    file_type = read_tag(temp_file, temp_file_endian)
    extension = {".dir": [".dxr", ".dcr"], ".cst": [".cxt", ".cct"]}
    oname_ext = oname.lower()[-4:]
    if oname_ext in extension:
        if file_type == "MV93":
            oname_ext = extension[oname_ext][0]
        elif file_type == "FGDM":
            oname_ext = extension[oname_ext][1]
        if oname[-4:].isupper():
            oname_ext = oname_ext.upper()
        oname = oname[:-4] + oname_ext

    oname = oname.replace("/", "_")

    if file_type in ["FGDM", "FGDC"]:
        temp_file.seek(0)
        open(os.path.join(outfolder, oname), "wb").write(temp_file.read())
        continue
    elif file_type == "Xtra":
        pos = temp_file.tell()
        if temp_file.read(1) != b"\x00":
            temp_file.seek(pos)
        tag = ""
        size = 0
        while tag not in ["XTdf", "FILE"]:
            if tag == "Xinf":
                from binascii import hexlify

                print(hexlify(temp_file.read(size)).decode("ascii"))
                size = 0
            temp_file.read(size)
            tag = read_tag(temp_file, temp_file_endian)
            size = read_i32(temp_file, temp_file_endian)
            size += -size % 2
            if tag == "FILE":
                temp_file.read(0x1C)
        if size:
            d = decompress(temp_file.read(size))
            open(os.path.join(outfolder, oname), "wb").write(d)
        else:
            temp_file.read(size)
        continue

    temp_file.seek(0x36)
    mmap_res_len = read_i16(temp_file, temp_file_endian)
    temp_file.seek(0x3C)
    mmap_res = read_i32(temp_file, temp_file_endian) - 1  # includes RIFX
    temp_file.seek(0x54)
    relative = read_i32(temp_file, temp_file_endian)
    temp_file.seek(int_mmap_pos)
    write_i32(temp_file, mmap_pos, temp_file_endian)
    for i in range(mmap_res):
        pos = 0x68 + (i * mmap_res_len)
        temp_file.seek(pos)
        absolute = read_i32(temp_file, endian)
        if absolute:
            absolute -= relative
            temp_file.seek(pos)
            write_i32(temp_file, absolute, temp_file_endian)
    temp_file.seek(-4, 2)
    if temp_file.read(4) != b"\x00\x00\x00\x00":
        temp_file.seek(-4, 2)
        write_i32(temp_file, 0, temp_file_endian)
    temp_file.seek(0)
    open(os.path.join(outfolder, oname), "wb").write(temp_file.read())

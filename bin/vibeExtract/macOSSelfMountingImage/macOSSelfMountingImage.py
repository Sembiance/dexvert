#!/usr/bin/env python3
# Vibe coded by Claude
"""
unSMI.py - Extract files from MacOS Self Mounting Image (SMI) files.

Usage: unSMI.py <inputFile> <outputDir>

Supports both HFS and HFS+ volumes embedded in NDIF format.
Extracts files as MacBinary II if they have a resource fork, otherwise as plain files.
"""

import struct
import sys
import os


# ---------- CRC-16 (CRC-CCITT) for MacBinary II ----------

def _crc16_table():
    tbl = []
    for i in range(256):
        crc = i << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
        tbl.append(crc)
    return tbl

_CRC_TABLE = _crc16_table()

def crc16(data):
    crc = 0
    for b in data:
        crc = ((crc << 8) & 0xFFFF) ^ _CRC_TABLE[((crc >> 8) ^ b) & 0xFF]
    return crc


# ---------- ADC (Apple Data Compression) decompressor ----------

def adc_decompress(data, expected_size):
    out = bytearray()
    i = 0
    dlen = len(data)
    while i < dlen and len(out) < expected_size:
        ctrl = data[i]; i += 1
        if ctrl & 0x80:  # literal run
            count = (ctrl & 0x7F) + 1
            end = i + count
            if end > dlen:
                out.extend(data[i:dlen])
                break
            out.extend(data[i:end])
            i = end
        elif ctrl & 0x40:  # 3-byte match reference
            count = (ctrl & 0x3F) + 4
            if i + 1 >= dlen:
                break
            offset = (data[i] << 8) | data[i + 1]; i += 2
            for _ in range(count):
                if offset < len(out):
                    out.append(out[-offset - 1])
                else:
                    out.append(0)
        else:  # 2-byte match reference
            count = ((ctrl >> 2) & 0x0F) + 3
            if i >= dlen:
                break
            offset = ((ctrl & 0x03) << 8) | data[i]; i += 1
            for _ in range(count):
                if offset < len(out):
                    out.append(out[-offset - 1])
                else:
                    out.append(0)
    return bytes(out[:expected_size])


# ---------- MacBinary header parsing ----------

def parse_macbinary_header(path):
    """Parse a MacBinary header. Returns (header, dfork_offset, dfork_len, rfork_offset, rfork_len) or None."""
    with open(path, 'rb') as f:
        hdr = f.read(128)
    if len(hdr) < 128:
        return None
    if hdr[0] != 0 or hdr[74] != 0 or hdr[82] != 0:
        return None
    name_len = hdr[1]
    if name_len == 0 or name_len > 63:
        return None
    ftype = hdr[65:69]
    if ftype == b'\x00\x00\x00\x00':
        return None
    dfork_len = struct.unpack('>I', hdr[83:87])[0]
    rfork_len = struct.unpack('>I', hdr[87:91])[0]
    dfork_pad = ((dfork_len + 127) // 128) * 128
    comment_len = struct.unpack('>H', hdr[99:101])[0]
    comment_pad = ((comment_len + 127) // 128) * 128
    file_size = os.path.getsize(path)
    expected = 128 + dfork_pad + rfork_pad(rfork_len)
    # Allow for comment
    expected_with_comment = 128 + dfork_pad + rfork_pad(rfork_len) + comment_pad
    if file_size != expected and file_size != expected_with_comment and abs(file_size - expected) > 128:
        return None
    return hdr, 128, dfork_len, 128 + dfork_pad, rfork_len

def rfork_pad(rfork_len):
    return ((rfork_len + 127) // 128) * 128


# ---------- AppleDouble parsing ----------

def parse_appledouble(path):
    """Parse an AppleDouble file. Returns resource fork data or None."""
    with open(path, 'rb') as f:
        magic = struct.unpack('>I', f.read(4))[0]
        if magic != 0x00051607:
            return None
        version = struct.unpack('>I', f.read(4))[0]
        f.read(16)  # filler
        num_entries = struct.unpack('>H', f.read(2))[0]
        for _ in range(num_entries):
            entry_id = struct.unpack('>I', f.read(4))[0]
            offset = struct.unpack('>I', f.read(4))[0]
            length = struct.unpack('>I', f.read(4))[0]
            if entry_id == 2:  # resource fork
                f.seek(offset)
                return f.read(length)
    return None


# ---------- Resource fork parsing ----------

def parse_resource_fork(rfork_data):
    """Parse a Mac resource fork and return dict of {type_bytes: {id: data}}."""
    if not rfork_data or len(rfork_data) < 16:
        return {}
    data_offset = struct.unpack('>I', rfork_data[0:4])[0]
    map_offset = struct.unpack('>I', rfork_data[4:8])[0]
    if map_offset + 28 > len(rfork_data):
        return {}
    rmap = rfork_data[map_offset:]
    tl_off = struct.unpack('>H', rmap[24:26])[0]
    tlist = rmap[tl_off:]
    nt = struct.unpack('>h', tlist[0:2])[0] + 1
    resources = {}
    for i in range(nt):
        e = tlist[2 + i * 8:2 + (i + 1) * 8]
        rtype = bytes(e[0:4])
        count = struct.unpack('>h', e[4:6])[0] + 1
        ref_off = struct.unpack('>H', e[6:8])[0]
        rd = tlist[ref_off:]
        for j in range(count):
            ref = rd[j * 12:(j + 1) * 12]
            rid = struct.unpack('>h', ref[0:2])[0]
            ao = struct.unpack('>I', ref[4:8])[0] & 0x00FFFFFF
            pos = data_offset + ao
            if pos + 4 > len(rfork_data):
                continue
            rs = struct.unpack('>I', rfork_data[pos:pos + 4])[0]
            rdata = rfork_data[pos + 4:pos + 4 + rs]
            resources.setdefault(rtype, {})[rid] = rdata
    return resources


# ---------- NDIF block map (bcem resource) parsing ----------

def parse_bcem(bcem_data):
    """Parse the bcem resource. Returns (total_sectors, block_entries)."""
    if len(bcem_data) < 132:
        raise ValueError("bcem resource too small")
    total_sectors = struct.unpack('>I', bcem_data[68:72])[0]
    entry_count = struct.unpack('>I', bcem_data[124:128])[0]
    entries = []
    for i in range(entry_count):
        off = 128 + i * 12
        if off + 12 > len(bcem_data):
            break
        e = bcem_data[off:off + 12]
        sector = (e[0] << 16) | (e[1] << 8) | e[2]
        block_type = e[3]
        data_offset = struct.unpack('>I', e[4:8])[0]
        data_length = struct.unpack('>I', e[8:12])[0]
        entries.append((sector, block_type, data_offset, data_length))
    return total_sectors, entries


def rebuild_volume(bcem_data, dfork_data):
    """Rebuild the raw HFS/HFS+ volume from the NDIF block map and data fork."""
    total_sectors, entries = parse_bcem(bcem_data)
    vol_size = total_sectors * 512
    volume = bytearray(vol_size)

    for i, (sector, btype, data_off, data_len) in enumerate(entries):
        if btype == 0xFF:  # end marker
            break
        next_sector = entries[i + 1][0] if i + 1 < len(entries) else total_sectors
        sector_count = next_sector - sector
        out_off = sector * 512
        expected_bytes = sector_count * 512

        if btype == 0x00:  # zero fill (already zeroed)
            pass
        elif btype == 0x02:  # raw copy
            src = dfork_data[data_off:data_off + data_len]
            volume[out_off:out_off + len(src)] = src
        elif btype == 0x83:  # ADC compressed
            dec = adc_decompress(dfork_data[data_off:data_off + data_len], expected_bytes)
            volume[out_off:out_off + len(dec)] = dec

    return bytes(volume)


# ---------- HFS volume parsing ----------

def parse_hfs_volume(volume):
    """Parse an HFS volume and return list of file entries."""
    mdb = volume[1024:]
    if struct.unpack('>H', mdb[0:2])[0] != 0x4244:
        return None

    alBlkSiz = struct.unpack('>I', mdb[20:24])[0]
    alBlSt = struct.unpack('>H', mdb[28:30])[0]

    def ab_off(ab):
        return alBlSt * 512 + ab * alBlkSiz

    def read_fork(extents, logical_size, overflow_list=None):
        data = bytearray()
        all_exts = list(extents)
        if overflow_list:
            for _, exts in sorted(overflow_list):
                all_exts.extend(exts)
        for start, count in all_exts:
            if count > 0:
                o = ab_off(start)
                end = o + count * alBlkSiz
                if end <= len(volume):
                    data.extend(volume[o:end])
                else:
                    data.extend(volume[o:len(volume)])
        return bytes(data[:logical_size])

    # Read Extents Overflow B-tree
    xtFlSize = struct.unpack('>I', mdb[130:134])[0]
    xtExt = [(struct.unpack('>H', mdb[134 + j * 4:136 + j * 4])[0],
              struct.unpack('>H', mdb[136 + j * 4:138 + j * 4])[0]) for j in range(3)]

    xt_data = bytearray()
    for s, c in xtExt:
        if c > 0:
            o = ab_off(s)
            xt_data.extend(volume[o:o + c * alBlkSiz])

    overflow_exts = {}
    if xt_data and xtFlSize > 0:
        try:
            hr_off = struct.unpack('>H', xt_data[510:512])[0]
            hr = xt_data[hr_off:]
            xt_ns = struct.unpack('>H', hr[18:20])[0]
            xt_fl = struct.unpack('>I', hr[10:14])[0]
            nn = xt_fl
            while nn != 0:
                no = nn * xt_ns
                node = xt_data[no:no + xt_ns]
                nfl = struct.unpack('>I', node[0:4])[0]
                ntp = node[8]
                nr = struct.unpack('>H', node[10:12])[0]
                if ntp == 0xFF:
                    for r in range(nr):
                        roff = struct.unpack('>H', node[xt_ns - 2 * (r + 1):xt_ns - 2 * r])[0]
                        kl = node[roff]
                        if kl < 7:
                            continue
                        fork_type = node[roff + 1]
                        fid = struct.unpack('>I', node[roff + 2:roff + 6])[0]
                        start_ab = struct.unpack('>H', node[roff + 6:roff + 8])[0]
                        doff = roff + 1 + kl
                        if doff % 2 == 1:
                            doff += 1
                        exts = [(struct.unpack('>H', node[doff + e * 4:doff + e * 4 + 2])[0],
                                 struct.unpack('>H', node[doff + e * 4 + 2:doff + e * 4 + 4])[0]) for e in range(3)]
                        key = (fid, fork_type)
                        overflow_exts.setdefault(key, []).append((start_ab, exts))
                nn = nfl
        except Exception:
            pass

    # Read Catalog B-tree
    ctFlSize = struct.unpack('>I', mdb[146:150])[0]
    ctExt = [(struct.unpack('>H', mdb[150 + j * 4:152 + j * 4])[0],
              struct.unpack('>H', mdb[152 + j * 4:154 + j * 4])[0]) for j in range(3)]

    cat = bytearray()
    for s, c in ctExt:
        if c > 0:
            o = ab_off(s)
            cat.extend(volume[o:o + c * alBlkSiz])

    if len(cat) < 512:
        return None

    hr_off = struct.unpack('>H', cat[510:512])[0]
    hr = cat[hr_off:]
    bt_ns = struct.unpack('>H', hr[18:20])[0]
    bt_fl = struct.unpack('>I', hr[10:14])[0]

    files = []
    dirs = {1: ('', 1), 2: (mdb[37:37 + mdb[36]].decode('mac_roman', errors='replace'), 1)}

    nn = bt_fl
    while nn != 0:
        no = nn * bt_ns
        if no + bt_ns > len(cat):
            break
        node = cat[no:no + bt_ns]
        nfl = struct.unpack('>I', node[0:4])[0]
        ntp = node[8]
        nr = struct.unpack('>H', node[10:12])[0]
        if ntp != 0xFF:
            nn = nfl
            continue
        for r in range(nr):
            roff = struct.unpack('>H', node[bt_ns - 2 * (r + 1):bt_ns - 2 * r])[0]
            kl = node[roff]
            if kl < 5:
                continue
            pid = struct.unpack('>I', node[roff + 2:roff + 6])[0]
            nl = node[roff + 6]
            name = node[roff + 7:roff + 7 + nl].decode('mac_roman', errors='replace')
            doff = roff + 1 + kl
            if doff % 2 == 1:
                doff += 1
            if doff + 2 > bt_ns:
                continue
            rt = node[doff]

            if rt == 1:  # directory
                if doff + 10 > bt_ns:
                    continue
                did = struct.unpack('>I', node[doff + 6:doff + 10])[0]
                cr_date = struct.unpack('>I', node[doff + 10:doff + 14])[0] if doff + 14 <= bt_ns else 0
                md_date = struct.unpack('>I', node[doff + 14:doff + 18])[0] if doff + 18 <= bt_ns else 0
                dirs[did] = (name, pid)

            elif rt == 2:  # file
                if doff + 102 > bt_ns:
                    continue
                ftype = bytes(node[doff + 4:doff + 8])
                fcreator = bytes(node[doff + 8:doff + 12])
                fflags = struct.unpack('>H', node[doff + 12:doff + 14])[0]
                fid = struct.unpack('>I', node[doff + 20:doff + 24])[0]
                dlg = struct.unpack('>I', node[doff + 26:doff + 30])[0]
                rlg = struct.unpack('>I', node[doff + 36:doff + 40])[0]
                cr_date = struct.unpack('>I', node[doff + 44:doff + 48])[0]
                md_date = struct.unpack('>I', node[doff + 48:doff + 52])[0]

                dexts = [(struct.unpack('>H', node[doff + 74 + e * 4:doff + 76 + e * 4])[0],
                          struct.unpack('>H', node[doff + 76 + e * 4:doff + 78 + e * 4])[0]) for e in range(3)]
                rexts = [(struct.unpack('>H', node[doff + 86 + e * 4:doff + 88 + e * 4])[0],
                          struct.unpack('>H', node[doff + 88 + e * 4:doff + 90 + e * 4])[0]) for e in range(3)]

                d_overflow = overflow_exts.get((fid, 0x00), None)
                r_overflow = overflow_exts.get((fid, 0xFF), None)

                data_fork = read_fork(dexts, dlg, d_overflow)
                rsrc_fork = read_fork(rexts, rlg, r_overflow)

                files.append({
                    'name': name, 'parent': pid, 'type': ftype, 'creator': fcreator,
                    'fflags': fflags, 'fid': fid,
                    'data_fork': data_fork, 'rsrc_fork': rsrc_fork,
                    'cr_date': cr_date, 'md_date': md_date,
                })
        nn = nfl

    return files, dirs


# ---------- HFS+ volume parsing ----------

def parse_hfsplus_volume(volume):
    """Parse an HFS+ volume and return list of file entries."""
    vh = volume[1024:]
    sig = struct.unpack('>H', vh[0:2])[0]
    if sig != 0x482B:
        return None

    blockSize = struct.unpack('>I', vh[40:44])[0]
    totalBlocks = struct.unpack('>I', vh[44:48])[0]

    def ab_off(ab):
        return ab * blockSize

    def read_fork_data(fork_offset, fork_size):
        """Read fork data from volume header fork structure (80 bytes)."""
        logical_size = struct.unpack('>Q', vh[fork_offset:fork_offset + 8])[0]
        total_blocks = struct.unpack('>I', vh[fork_offset + 12:fork_offset + 16])[0]
        extents = []
        for e in range(8):
            start = struct.unpack('>I', vh[fork_offset + 16 + e * 8:fork_offset + 20 + e * 8])[0]
            count = struct.unpack('>I', vh[fork_offset + 20 + e * 8:fork_offset + 24 + e * 8])[0]
            extents.append((start, count))
        data = bytearray()
        for start, count in extents:
            if count > 0:
                o = ab_off(start)
                end = o + count * blockSize
                if end <= len(volume):
                    data.extend(volume[o:end])
                else:
                    data.extend(volume[o:len(volume)])
        return bytes(data[:logical_size]), extents

    # Read catalog file
    cat_data, cat_exts = read_fork_data(272, 80)
    if not cat_data or len(cat_data) < 512:
        return None

    # Read extents overflow file
    ext_data, ext_exts = read_fork_data(192, 80)

    # Parse extents overflow B-tree for additional extents
    overflow_exts = {}
    if ext_data and len(ext_data) >= 512:
        try:
            # B-tree header node
            bt_ns = struct.unpack('>H', ext_data[32:34])[0]  # node size at offset 32 in header record
            if bt_ns == 0:
                hr_off_pos = len(ext_data) - 2 if len(ext_data) >= 514 else 510
                hr_off = struct.unpack('>H', ext_data[510:512])[0]
                hr = ext_data[hr_off:]
                bt_ns = struct.unpack('>H', hr[18:20])[0]

            # HFS+ B-tree header is at node 0
            # Node descriptor: fLink(4), bLink(4), kind(1), height(1), numRecords(2), reserved(2) = 14 bytes
            # The header record starts after the node descriptor
            hdr_node = ext_data[:bt_ns]
            n_recs = struct.unpack('>H', hdr_node[10:12])[0]
            # Record offsets at end of node
            rec0_off = struct.unpack('>H', hdr_node[bt_ns - 2:bt_ns])[0]
            hr = hdr_node[rec0_off:]
            bt_depth = struct.unpack('>H', hr[0:2])[0]
            bt_root = struct.unpack('>I', hr[2:6])[0]
            bt_leaf_recs = struct.unpack('>I', hr[6:10])[0]
            bt_first_leaf = struct.unpack('>I', hr[10:14])[0]
            bt_last_leaf = struct.unpack('>I', hr[14:18])[0]
            bt_ns2 = struct.unpack('>H', hr[18:20])[0]
            if bt_ns2 > 0:
                bt_ns = bt_ns2

            nn = bt_first_leaf
            while nn != 0 and nn * bt_ns + bt_ns <= len(ext_data):
                no = nn * bt_ns
                node = ext_data[no:no + bt_ns]
                nfl = struct.unpack('>I', node[0:4])[0]
                ntp = node[8]
                nr = struct.unpack('>H', node[10:12])[0]
                if ntp == 0xFF:  # leaf
                    for r in range(nr):
                        roff = struct.unpack('>H', node[bt_ns - 2 * (r + 1):bt_ns - 2 * r])[0]
                        # HFS+ extent key: keyLength(2), forkType(1), pad(1), fileID(4), startBlock(4) = 12 bytes
                        kl = struct.unpack('>H', node[roff:roff + 2])[0]
                        if kl < 10:
                            continue
                        fork_type = node[roff + 2]
                        fid = struct.unpack('>I', node[roff + 4:roff + 8])[0]
                        start_block = struct.unpack('>I', node[roff + 8:roff + 12])[0]
                        doff = roff + 2 + kl
                        # Extent record: 8 extents of 8 bytes each
                        exts = []
                        for e in range(8):
                            if doff + e * 8 + 8 <= bt_ns:
                                es = struct.unpack('>I', node[doff + e * 8:doff + e * 8 + 4])[0]
                                ec = struct.unpack('>I', node[doff + e * 8 + 4:doff + e * 8 + 8])[0]
                                exts.append((es, ec))
                        key = (fid, fork_type)
                        overflow_exts.setdefault(key, []).append((start_block, exts))
                nn = nfl
        except Exception:
            pass

    def read_file_fork(extents, logical_size, fid, fork_type):
        """Read file data given catalog extents and any overflow extents."""
        all_exts = list(extents)
        oe = overflow_exts.get((fid, fork_type), [])
        for _, exts in sorted(oe):
            all_exts.extend(exts)
        data = bytearray()
        for start, count in all_exts:
            if count > 0:
                o = ab_off(start)
                end = o + count * blockSize
                if end <= len(volume):
                    data.extend(volume[o:end])
                else:
                    data.extend(volume[o:len(volume)])
        return bytes(data[:logical_size])

    # Parse catalog B-tree
    hdr_node = cat_data[:4096]  # read enough for header
    # Find node size from header record
    rec0_off = struct.unpack('>H', cat_data[510:512])[0]  # try 512-byte node first
    # Actually need to find the node size. Default for HFS+ is 4096 for catalog.
    # Let's read from the header record.
    # Node descriptor at offset 0: fLink(4), bLink(4), kind(1), height(1), numRecords(2), reserved(2)
    # Then records follow. First record offset from end of node...
    # For now, try common node sizes.
    bt_ns = 4096
    # Try to read header properly
    for try_ns in [4096, 8192, 2048, 1024, 512]:
        if try_ns > len(cat_data):
            continue
        try:
            test_node = cat_data[:try_ns]
            test_ntype = test_node[8]
            test_nrecs = struct.unpack('>H', test_node[10:12])[0]
            if test_ntype == 1 and test_nrecs >= 1:  # header node
                r0_off = struct.unpack('>H', test_node[try_ns - 2:try_ns])[0]
                test_hr = test_node[r0_off:]
                ns_check = struct.unpack('>H', test_hr[18:20])[0]
                if ns_check > 0 and ns_check <= len(cat_data):
                    bt_ns = ns_check
                    break
        except Exception:
            continue

    hdr_node = cat_data[:bt_ns]
    rec0_off = struct.unpack('>H', hdr_node[bt_ns - 2:bt_ns])[0]
    hr = hdr_node[rec0_off:]
    bt_first_leaf = struct.unpack('>I', hr[10:14])[0]

    files = []
    dirs = {1: ('', 1), 2: ('', 1)}  # Will be filled from catalog

    # Get volume name from catalog (thread record for CNID 2)
    vol_name = ''

    nn = bt_first_leaf
    while nn != 0:
        no = nn * bt_ns
        if no + bt_ns > len(cat_data):
            break
        node = cat_data[no:no + bt_ns]
        nfl = struct.unpack('>I', node[0:4])[0]
        ntp = node[8]
        nr = struct.unpack('>H', node[10:12])[0]
        if ntp != 0xFF:
            nn = nfl
            continue
        for r in range(nr):
            roff = struct.unpack('>H', node[bt_ns - 2 * (r + 1):bt_ns - 2 * r])[0]
            if roff + 6 > bt_ns:
                continue
            # HFS+ catalog key: keyLength(2), parentID(4), nameLength(2), name(variable UTF-16BE)
            kl = struct.unpack('>H', node[roff:roff + 2])[0]
            if kl < 6:
                continue
            pid = struct.unpack('>I', node[roff + 2:roff + 6])[0]
            name_len = struct.unpack('>H', node[roff + 6:roff + 8])[0]
            name_bytes = node[roff + 8:roff + 8 + name_len * 2]
            try:
                name = name_bytes.decode('utf-16-be', errors='replace')
            except Exception:
                name = ''

            doff = roff + 2 + kl
            # Pad to even? Actually HFS+ keys are already even-aligned by design
            if doff + 2 > bt_ns:
                continue

            rt = struct.unpack('>h', node[doff:doff + 2])[0]

            if rt == 1:  # folder (HFS+ folder record)
                if doff + 88 > bt_ns:
                    continue
                # recordType(2), flags(2), valence(4), folderID(4), createDate(4), contentModDate(4)...
                did = struct.unpack('>I', node[doff + 8:doff + 12])[0]
                cr_date = struct.unpack('>I', node[doff + 12:doff + 16])[0]
                md_date = struct.unpack('>I', node[doff + 16:doff + 20])[0]
                dirs[did] = (name, pid)

            elif rt == 2:  # file (HFS+ file record)
                if doff + 248 > bt_ns:
                    continue
                # recordType(2), flags(2), reserved1(4), fileID(4), createDate(4), contentModDate(4),
                # attrModDate(4), accessDate(4), backupDate(4), permissions(16),
                # userInfo(16: FileInfo), finderInfo(16: ExtFinderInfo),
                # textEncoding(4), reserved2(4)
                # then dataFork(HFSPlusForkData, 80), resourceFork(HFSPlusForkData, 80)
                fid = struct.unpack('>I', node[doff + 8:doff + 12])[0]
                cr_date = struct.unpack('>I', node[doff + 12:doff + 16])[0]
                md_date = struct.unpack('>I', node[doff + 16:doff + 20])[0]
                # UserInfo (FileInfo) at doff+48
                ftype = bytes(node[doff + 48:doff + 52])
                fcreator = bytes(node[doff + 52:doff + 56])
                fflags = struct.unpack('>H', node[doff + 56:doff + 58])[0]

                # Data fork at doff+88
                d_logical = struct.unpack('>Q', node[doff + 88:doff + 96])[0]
                d_exts = []
                for e in range(8):
                    es = struct.unpack('>I', node[doff + 104 + e * 8:doff + 108 + e * 8])[0]
                    ec = struct.unpack('>I', node[doff + 108 + e * 8:doff + 112 + e * 8])[0]
                    d_exts.append((es, ec))

                # Resource fork at doff+168
                r_logical = struct.unpack('>Q', node[doff + 168:doff + 176])[0]
                r_exts = []
                for e in range(8):
                    es = struct.unpack('>I', node[doff + 184 + e * 8:doff + 188 + e * 8])[0]
                    ec = struct.unpack('>I', node[doff + 188 + e * 8:doff + 192 + e * 8])[0]
                    r_exts.append((es, ec))

                data_fork = read_file_fork(d_exts, d_logical, fid, 0x00)
                rsrc_fork = read_file_fork(r_exts, r_logical, fid, 0xFF)

                files.append({
                    'name': name, 'parent': pid, 'type': ftype, 'creator': fcreator,
                    'fflags': fflags, 'fid': fid,
                    'data_fork': data_fork, 'rsrc_fork': rsrc_fork,
                    'cr_date': cr_date, 'md_date': md_date,
                })

            elif rt == 3:  # folder thread
                if doff + 12 > bt_ns:
                    continue
                thread_pid = struct.unpack('>I', node[doff + 4:doff + 8])[0]
                tnl = struct.unpack('>H', node[doff + 8:doff + 10])[0]
                tname_bytes = node[doff + 10:doff + 10 + tnl * 2]
                try:
                    tname = tname_bytes.decode('utf-16-be', errors='replace')
                except Exception:
                    tname = ''
                if pid == 2 and tname:
                    vol_name = tname
                dirs[pid] = (tname, thread_pid)

            elif rt == 4:  # file thread
                pass

        nn = nfl

    # Set volume name
    if vol_name:
        dirs[2] = (vol_name, 1)

    return files, dirs


# ---------- Path building from directory tree ----------

def build_path(dirs, parent_id):
    """Build a relative directory path from the dir tree."""
    parts = []
    seen = set()
    pid = parent_id
    while pid > 1 and pid not in seen:
        seen.add(pid)
        if pid in dirs:
            name, ppid = dirs[pid]
            if name:
                parts.append(name)
            pid = ppid
        else:
            break
    parts.reverse()
    return os.path.join(*parts) if parts else ''


# ---------- MacBinary II writer ----------

def write_macbinary2(filepath, name, ftype, fcreator, fflags, data_fork, rsrc_fork, cr_date, md_date):
    """Write a MacBinary II file."""
    # Encode filename as Mac Roman, truncate to 63 chars
    try:
        name_bytes = name.encode('mac_roman')
    except (UnicodeEncodeError, LookupError):
        name_bytes = name.encode('ascii', errors='replace')
    name_bytes = name_bytes[:63]

    hdr = bytearray(128)
    hdr[0] = 0  # version
    hdr[1] = len(name_bytes)  # filename length
    hdr[2:2 + len(name_bytes)] = name_bytes

    # File type and creator
    hdr[65:69] = ftype[:4] if len(ftype) >= 4 else ftype.ljust(4, b'\x00')
    hdr[69:73] = fcreator[:4] if len(fcreator) >= 4 else fcreator.ljust(4, b'\x00')

    # Finder flags
    hdr[73] = (fflags >> 8) & 0xFF  # high byte
    hdr[101] = fflags & 0xFF  # low byte

    # Fork lengths
    struct.pack_into('>I', hdr, 83, len(data_fork))
    struct.pack_into('>I', hdr, 87, len(rsrc_fork))

    # Dates
    struct.pack_into('>I', hdr, 91, cr_date)
    struct.pack_into('>I', hdr, 95, md_date)

    # MacBinary II version
    hdr[122] = 0x81  # version written
    hdr[123] = 0x81  # min version needed

    # Compute CRC of first 124 bytes
    crc_val = crc16(hdr[:124])
    struct.pack_into('>H', hdr, 124, crc_val)

    # Write file
    with open(filepath, 'wb') as f:
        f.write(hdr)
        f.write(data_fork)
        # Pad data fork to 128-byte boundary
        pad = (128 - (len(data_fork) % 128)) % 128
        if pad:
            f.write(b'\x00' * pad)
        f.write(rsrc_fork)
        # Pad resource fork to 128-byte boundary
        pad = (128 - (len(rsrc_fork) % 128)) % 128
        if pad:
            f.write(b'\x00' * pad)


# ---------- Safe filename ----------

def safe_filename(name):
    """Convert a Mac filename to a safe local filename."""
    # Replace problematic characters
    # Mac uses : as path separator; on Unix/Windows swap with _
    name = name.replace('/', ':')  # Mac OS uses / for display of :
    name = name.replace(':', '_')
    # Remove other problematic characters for common filesystems
    for ch in '<>"|?*':
        name = name.replace(ch, '_')
    # Remove control characters
    name = ''.join(c if ord(c) >= 32 else '_' for c in name)
    # Trim whitespace
    name = name.strip()
    if not name:
        name = 'unnamed'
    return name


# ---------- Main extraction ----------

def extract_smi(input_path, output_dir):
    """Extract all files from an SMI file to the output directory."""
    basename = os.path.basename(input_path)

    # Determine format: MacBinary or AppleDouble
    dfork_data = None
    rfork_data = None

    with open(input_path, 'rb') as f:
        first4 = f.read(4)

    if first4[:4] == b'\x00\x05\x16\x07':
        # AppleDouble format - resource fork only
        rfork_data = parse_appledouble(input_path)
        if rfork_data is None:
            print(f"Error: Could not parse AppleDouble file: {basename}")
            return False
        # AppleDouble .rsrc files contain only the resource fork.
        # The data fork (with NDIF block data) must come from a companion file.
        base = input_path
        if base.endswith('.rsrc'):
            base = base[:-5]
        if os.path.exists(base):
            with open(base, 'rb') as f:
                dfork_data = f.read()
        else:
            print(f"Error: AppleDouble resource-only file; companion data fork not found: {basename}")
            print(f"  Expected data fork at: {base}")
            return False
    else:
        # MacBinary format
        with open(input_path, 'rb') as f:
            hdr = f.read(128)
        dfork_len = struct.unpack('>I', hdr[83:87])[0]
        rfork_len = struct.unpack('>I', hdr[87:91])[0]
        dfork_pad = ((dfork_len + 127) // 128) * 128

        with open(input_path, 'rb') as f:
            f.seek(128)
            dfork_data = f.read(dfork_len)
            f.seek(128 + dfork_pad)
            rfork_data = f.read(rfork_len)

    if rfork_data is None or len(rfork_data) < 16:
        print(f"Error: No resource fork found in: {basename}")
        return False

    # Parse resource fork to get bcem
    resources = parse_resource_fork(rfork_data)
    bcem_data = resources.get(b'bcem', {}).get(128, None)
    if bcem_data is None:
        print(f"Error: No bcem resource found in: {basename}")
        return False

    # Rebuild volume
    if dfork_data is None:
        dfork_data = b''

    try:
        volume = rebuild_volume(bcem_data, dfork_data)
    except Exception as e:
        print(f"Error rebuilding volume from {basename}: {e}")
        return False

    # Detect volume type and parse
    vol_sig = struct.unpack('>H', volume[1024:1026])[0]

    result = None
    if vol_sig == 0x4244:  # HFS
        # Check for embedded HFS+
        embed_sig = struct.unpack('>H', volume[1024 + 124:1024 + 126])[0]
        if embed_sig == 0x482B:
            # HFS wrapper with embedded HFS+
            mdb = volume[1024:]
            alBlkSiz = struct.unpack('>I', mdb[20:24])[0]
            alBlSt = struct.unpack('>H', mdb[28:30])[0]
            embed_start = struct.unpack('>H', mdb[126:128])[0]
            embed_count = struct.unpack('>H', mdb[128:130])[0]
            embed_off = alBlSt * 512 + embed_start * alBlkSiz
            embed_len = embed_count * alBlkSiz
            embedded_vol = volume[embed_off:embed_off + embed_len]
            result = parse_hfsplus_volume(embedded_vol)
        else:
            result = parse_hfs_volume(volume)
    elif vol_sig == 0x482B:  # HFS+
        result = parse_hfsplus_volume(volume)
    else:
        print(f"Error: Unknown volume signature 0x{vol_sig:04X} in {basename}")
        return False

    if result is None:
        print(f"Error: Failed to parse volume in {basename}")
        return False

    all_files, dirs = result

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    extracted = 0
    for f in all_files:
        name = f['name']
        if not name or name.startswith('\x00'):
            continue

        # Build directory path
        dir_path = build_path(dirs, f['parent'])
        full_dir = os.path.join(output_dir, safe_filename(dir_path)) if dir_path else output_dir
        os.makedirs(full_dir, exist_ok=True)

        safe_name = safe_filename(name)
        out_path = os.path.join(full_dir, safe_name)

        # Handle duplicate filenames
        if os.path.exists(out_path):
            base, ext = os.path.splitext(safe_name)
            counter = 1
            while os.path.exists(out_path):
                out_path = os.path.join(full_dir, f"{base}_{counter}{ext}")
                counter += 1

        data_fork = f['data_fork']
        rsrc_fork = f['rsrc_fork']

        if rsrc_fork and len(rsrc_fork) > 0:
            # Has resource fork - write as MacBinary II
            write_macbinary2(
                out_path, name,
                f['type'], f['creator'], f['fflags'],
                data_fork, rsrc_fork,
                f['cr_date'], f['md_date']
            )
        else:
            # Data fork only - write as plain file
            with open(out_path, 'wb') as of:
                of.write(data_fork)

        extracted += 1

    print(f"Extracted {extracted} files from {basename}")
    return True


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(input_path):
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    success = extract_smi(input_path, output_dir)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

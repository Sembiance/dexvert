#!/usr/bin/env python3
# Vibe coded by Claude
"""
unAIXBFF.py - AIX BFF (Backup Format File) extractor
Usage: python3 unAIXBFF.py <inputFile> <outDir>
"""
import struct, sys, os, datetime

MAGIC_BYTE3 = 0xEA
VOL_HEADER_SIZE = 72
S_IFMT, S_IFDIR, S_IFREG, S_IFLNK = 0o170000, 0o040000, 0o100000, 0o120000

def align8(x):
    return (x + 7) & ~7

def is_magic(data, off):
    if off + 4 > len(data): return False
    return data[off + 3] == MAGIC_BYTE3 and 0x60 <= data[off + 2] <= 0x7F

def ftype_str(mode):
    f = mode & S_IFMT
    return {S_IFDIR:'DIR',S_IFREG:'FILE',S_IFLNK:'LINK',0o010000:'FIFO',0o020000:'CDEV',0o060000:'BDEV',0o140000:'SOCK'}.get(f, f'?{oct(f)}')

def perms_str(mode):
    p = ''
    for s in (6,3,0):
        b = (mode >> s) & 7
        p += ('r' if b&4 else '-')+('w' if b&2 else '-')+('x' if b&1 else '-')
    return p

def safe_path(fname, outdir):
    c = fname.lstrip('.').lstrip('/')
    if not c: return None
    full = os.path.normpath(os.path.join(outdir, c))
    return full if full.startswith(os.path.normpath(outdir)) else None

def ts_str(ts):
    try: return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    except: return f'ts={ts}'

def parse_vol(data):
    if len(data) < 72 or not is_magic(data, 0): return None
    dev1 = data[20:36].split(b'\x00')[0]
    return {
        'rec_type':data[0],'rec_sub':data[1],'checksum':data[2],
        'numclust':struct.unpack_from('<I',data,4)[0],
        'date':struct.unpack_from('<I',data,8)[0],
        'date2':struct.unpack_from('<I',data,12)[0],
        'numinodes':struct.unpack_from('<I',data,16)[0],
        'device1':dev1.decode('ascii',errors='replace'),
        'device2':data[36:52].split(b'\x00')[0].decode('ascii',errors='replace'),
        'user':data[52:68].split(b'\x00')[0].decode('ascii',errors='replace'),
        'field2_lo':struct.unpack_from('<H',data,68)[0],
        'field2_hi':struct.unpack_from('<H',data,70)[0],
        'is_byname':dev1==b'by name' or (not dev1.startswith(b'/dev/')),
        'is_byinode':dev1.startswith(b'/dev/'),
        'date_str':ts_str(struct.unpack_from('<I',data,8)[0]),
    }

def parse_records(data):
    """Parse by-name BFF format records.

    Sub=0x0C uses uint32 fields and 72-byte pre-path header.
    Sub=0x09 uses uint16 fields for mode/nlink/uid/gid and 48-byte pre-path header.
    """
    fs = len(data); recs = []; off = 72
    while off < fs - 4:
        if not is_magic(data, off): break
        rt, rs, chk = data[off], data[off+1], data[off+2]
        if rt == 0x01:
            s = off + 4
            while s < fs - 4:
                if is_magic(data, s) and data[s] != 0x01: break
                s += 1
            else: s = fs
            recs.append({'type':'special','rec_type':rt,'rec_sub':rs,'offset':off,'end':s,'size':s-off,'checksum':chk})
            off = s; continue
        if rt > 0x0F or off + 40 > fs: break

        if rs == 0x0c:
            # Sub 0x0C: 32-bit fields, path at +72, no meta2
            mode = struct.unpack_from('<I',data,off+12)[0]
            uid = struct.unpack_from('<I',data,off+16)[0]
            gid = struct.unpack_from('<I',data,off+20)[0]
            sz = struct.unpack_from('<I',data,off+24)[0]
            at = struct.unpack_from('<I',data,off+28)[0]
            mt = struct.unpack_from('<I',data,off+32)[0]
            ct = struct.unpack_from('<I',data,off+36)[0]
            fo = off + 72
            m2 = 0
        elif rs == 0x09:
            # Sub 0x09: 16-bit mode/nlink/uid/gid, path at +48
            mode = struct.unpack_from('<H',data,off+8)[0]
            uid = struct.unpack_from('<H',data,off+12)[0]
            gid = struct.unpack_from('<H',data,off+14)[0]
            sz = struct.unpack_from('<I',data,off+16)[0]
            mt = struct.unpack_from('<I',data,off+20)[0]
            at = struct.unpack_from('<I',data,off+24)[0]
            ct = struct.unpack_from('<I',data,off+28)[0]
            fo = off + 48
            m2 = 0
        else:
            # Sub 0x0B (standard) and all other sub-types: 32-bit fields, path at +64, 40-byte meta2
            mode = struct.unpack_from('<I',data,off+12)[0]
            uid = struct.unpack_from('<I',data,off+16)[0]
            gid = struct.unpack_from('<I',data,off+20)[0]
            sz = struct.unpack_from('<I',data,off+24)[0]
            at = struct.unpack_from('<I',data,off+28)[0]
            mt = struct.unpack_from('<I',data,off+32)[0]
            ct = struct.unpack_from('<I',data,off+36)[0]
            fo = off + 64
            m2 = 40

        isdir = (mode & S_IFMT) == S_IFDIR
        if fo >= fs: break
        try: np = data.index(b'\x00', fo, min(fo+1024, fs))
        except ValueError: break
        fn = data[fo:np].decode('ascii',errors='replace')
        ds = align8(np+1) + m2
        if isdir and sz == 0: end = ds; ad = 0
        else: end = align8(ds+sz); ad = sz
        if ds > fs: ds = fs; ad = 0; end = fs
        elif end > fs: ad = fs - ds; end = fs
        recs.append({'type':'inode','rec_type':rt,'rec_sub':rs,'checksum':chk,'offset':off,'end':end,
            'mode':mode,'uid':uid,'gid':gid,'size':sz,'actual_data_size':ad,
            'atime':at,'mtime':mt,'ctime':ct,'fname':fn,'data_off':ds,
            'ftype':ftype_str(mode),'perms':perms_str(mode&0o7777)})
        if end <= off: break
        off = end
    if off < fs:
        recs.append({'type':'trailing','offset':off,'end':fs,'size':fs-off})
    return recs

def parse_byinode(data):
    """Parse by-inode BFF format (device1 starts with /dev/).

    Structure of volume 1:
      [Volume Header 72 bytes]
      [Bitmap Record: type=0x01 sub=0x03]
      [Inode Offset Table: type=0x3E sub=0x01]
      [Padding to 8-byte alignment]
      [Inode Records: type=0x06 sub=0x08, each 8-byte aligned]
      [Zero padding to end of volume]

    Continuation volumes (2+):
      [Volume Header 72 bytes]
      [Continuation data for file spanning volume boundary]
      [Inode Records: type=0x06 sub=0x08]
      [Zero padding]

    Inode record (sub=0x08) fields use uint16 for mode/nlink/uid/gid:
      +0:  type(1) sub(1) ver(1) magic(1)  -- record header
      +4:  checksum(uint16)
      +6:  inode(uint16)
      +8:  mode(uint16)    -- POSIX file type + permissions
      +10: nlink(uint16)
      +12: uid(uint16)
      +14: gid(uint16)
      +16: size(uint32)    -- data size in bytes
      +20: mtime(uint32)   -- modification time
      +24: gen(uint32)     -- generation or atime (often constant)
      +28: ctime(uint32)   -- change time
      +32: devnum(uint32)  -- source device number
      +36: reserved(uint32)
      +40: alloc_size(uint32)
      +44: reserved2(uint32)
      +48: data[]          -- directory entries (16 bytes each) or file content
    """
    fs = len(data); recs = []; off = 72

    # -- Parse bitmap record (type=0x01, sub=0x03) if present --
    if off < fs - 4 and is_magic(data, off) and data[off] == 0x01 and data[off+1] == 0x03:
        bm_start = off
        # Scan forward to next record header
        s = off + 4
        while s < fs - 4:
            if is_magic(data, s) and data[s] != 0x01: break
            s += 1
        else: s = fs
        recs.append({'type':'bitmap','rec_type':0x01,'rec_sub':0x03,
                      'checksum':data[off+2],'offset':off,'end':s,'size':s-off})
        off = s

    # -- Parse inode offset table (type=0x3E, sub=0x01) if present --
    inode_table = {}  # inode_num -> byte_offset_in_file
    if off < fs - 4 and is_magic(data, off) and data[off] == 0x3E and data[off+1] == 0x01:
        tbl_start = off
        # Table structure: header(4) + checksum(2) + unknown(2) +
        #   80 x uint16 inode numbers + 80 x uint32 offsets (in 8-byte units)
        # Total = 4 + 4 + 160 + 320 = 488 bytes + padding
        inode_arr_off = off + 8
        offset_arr_off = off + 8 + 160
        tbl_end = offset_arr_off + 320
        tbl_end = align8(tbl_end)

        inodes_list = []
        offsets_list = []
        for i in range(80):
            p = inode_arr_off + i * 2
            if p + 2 <= fs:
                v = struct.unpack_from('<H', data, p)[0]
                inodes_list.append(v)
        for i in range(80):
            p = offset_arr_off + i * 4
            if p + 4 <= fs:
                v = struct.unpack_from('<I', data, p)[0]
                offsets_list.append(v)

        for ino_num, off_val in zip(inodes_list, offsets_list):
            if ino_num != 0 and off_val != 0:
                inode_table[ino_num] = off_val * 8

        recs.append({'type':'inode_table','rec_type':0x3E,'rec_sub':0x01,
                      'checksum':data[tbl_start+2],'offset':tbl_start,'end':tbl_end,
                      'size':tbl_end-tbl_start,'entries':len(inode_table)})
        off = tbl_end

    # -- Skip any continuation data (for volumes 2+) --
    # Find the first valid 0x06/0x08 record at 8-byte alignment
    cont_start = off
    found_first = False
    scan = off
    while scan < fs - 48:
        if scan % 8 == 0 and is_magic(data, scan) and data[scan] == 0x06 and data[scan+1] == 0x08:
            # Validate: check mode field for reasonable file type
            mode = struct.unpack_from('<H', data, scan + 8)[0]
            mode_type = (mode >> 12) & 0xF
            if mode_type in (1, 2, 4, 6, 8, 10, 12):
                if scan > cont_start:
                    recs.append({'type':'continuation','offset':cont_start,
                                  'end':scan,'size':scan-cont_start})
                off = scan
                found_first = True
                break
        scan += 8

    if not found_first:
        if off < fs:
            recs.append({'type':'trailing','offset':off,'end':fs,'size':fs-off})
        return recs

    # -- Parse inode records (type=0x06, sub=0x08) --
    # Build directory tree for path resolution
    dir_entries = {}  # inode -> [(child_inode, name), ...]
    inode_records = {}  # inode -> record dict

    while off < fs - 48:
        # Must be 8-byte aligned
        if off % 8 != 0:
            off = align8(off)
            continue

        if not is_magic(data, off) or data[off] != 0x06 or data[off+1] != 0x08:
            # Check if remaining data is all zeros (trailing padding)
            remaining = data[off:off+8]
            if remaining == b'\x00' * 8:
                break
            off += 8
            continue

        ino = struct.unpack_from('<H', data, off + 6)[0]
        mode = struct.unpack_from('<H', data, off + 8)[0]
        nlink = struct.unpack_from('<H', data, off + 10)[0]
        uid = struct.unpack_from('<H', data, off + 12)[0]
        gid = struct.unpack_from('<H', data, off + 14)[0]
        sz = struct.unpack_from('<I', data, off + 16)[0]
        mt = struct.unpack_from('<I', data, off + 20)[0]
        at = struct.unpack_from('<I', data, off + 24)[0]
        ct = struct.unpack_from('<I', data, off + 28)[0]

        mode_type = (mode >> 12) & 0xF
        if mode_type not in (1, 2, 4, 6, 8, 10, 12):
            off += 8; continue

        isdir = (mode & S_IFMT) == S_IFDIR
        data_off = off + 48
        end = align8(data_off + sz)

        rec = {'type':'inode','rec_type':0x06,'rec_sub':0x08,
               'checksum':data[off+2],'offset':off,'end':end,
               'inode':ino,'mode':mode,'nlink':nlink,'uid':uid,'gid':gid,
               'size':sz,'actual_data_size':min(sz, fs - data_off),
               'atime':at,'mtime':mt,'ctime':ct,'data_off':data_off,
               'ftype':ftype_str(mode),'perms':perms_str(mode & 0o7777),
               'fname':''}

        inode_records[ino] = rec

        # Parse directory entries
        if isdir and sz > 0:
            entries = []
            for j in range(0, sz, 16):
                eoff = data_off + j
                if eoff + 16 > fs: break
                child_ino = struct.unpack_from('<H', data, eoff)[0]
                name = data[eoff+2:eoff+16].split(b'\x00')[0].decode('ascii', errors='replace')
                if name and name != '.' and name != '..' and child_ino != 0:
                    entries.append((child_ino, name))
            dir_entries[ino] = entries

        recs.append(rec)
        off = end

    # -- Resolve paths using directory tree --
    # Find root inode (inode 2 is standard, or find the one with .=self)
    root_ino = 2 if 2 in inode_records else (min(inode_records.keys()) if inode_records else None)
    if root_ino is not None:
        paths = {root_ino: '/'}
        queue = [root_ino]
        visited = set()
        while queue:
            parent_ino = queue.pop(0)
            if parent_ino in visited: continue
            visited.add(parent_ino)
            if parent_ino not in dir_entries: continue
            parent_path = paths.get(parent_ino, '/')
            for child_ino, name in dir_entries[parent_ino]:
                if child_ino in inode_records:
                    child_path = parent_path.rstrip('/') + '/' + name
                    if child_ino not in paths:
                        paths[child_ino] = child_path
                    child_mode = inode_records[child_ino]['mode']
                    if (child_mode & S_IFMT) == S_IFDIR:
                        queue.append(child_ino)
                else:
                    # Inode referenced in dir but no record (hardlink target not in this volume,
                    # or inode in another volume)
                    paths[child_ino] = parent_path.rstrip('/') + '/' + name

        # Assign resolved paths to records
        for rec in recs:
            if rec['type'] == 'inode' and 'inode' in rec:
                ino = rec['inode']
                if ino in paths:
                    rec['fname'] = paths[ino]
                else:
                    rec['fname'] = f'<inode:{ino}>'

    # -- Add trailing padding --
    if off < fs:
        recs.append({'type':'trailing','offset':off,'end':fs,'size':fs-off})

    return recs

def extract(data, records, outdir, verbose=False):
    os.makedirs(outdir, exist_ok=True)
    ext = []; seen = set()
    for r in records:
        if r['type'] != 'inode': continue
        fn = r['fname']
        if not fn: continue
        ft, sz = r['ftype'], r.get('actual_data_size', r['size'])
        tgt = safe_path(fn, outdir)
        if tgt is None or tgt in seen: continue
        seen.add(tgt)
        if ft == 'DIR':
            os.makedirs(tgt, exist_ok=True)
            ext.append({'fname':fn,'ftype':'DIR','size':0,'target':tgt,'status':'ok'})
            if verbose: print(f"  DIR:  {fn}")
        elif ft == 'LINK':
            lt = data[r['data_off']:r['data_off']+sz].decode('ascii',errors='replace').rstrip('\x00')
            os.makedirs(os.path.dirname(tgt), exist_ok=True)
            if os.path.lexists(tgt): os.unlink(tgt)
            try: os.symlink(lt, tgt); st='ok'
            except OSError:
                with open(tgt,'w') as f: f.write(lt)
                st='fallback'
            ext.append({'fname':fn,'ftype':'LINK','size':sz,'target':tgt,'link_to':lt,'status':st})
            if verbose: print(f"  LINK: {fn} -> {lt}")
        elif ft == 'FILE':
            os.makedirs(os.path.dirname(tgt), exist_ok=True)
            with open(tgt,'wb') as f: f.write(data[r['data_off']:r['data_off']+sz])
            ext.append({'fname':fn,'ftype':'FILE','size':sz,'target':tgt,'status':'ok'})
            if verbose: print(f"  FILE: {fn} ({sz} bytes)")
        else:
            ext.append({'fname':fn,'ftype':ft,'size':sz,'target':tgt,'status':'skipped'})
    return ext

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outDir>"); sys.exit(1)
    inp, out = sys.argv[1], sys.argv[2]
    if not os.path.isfile(inp): print(f"Error: {inp} not found"); sys.exit(1)
    print(f"Reading {inp}...")
    with open(inp,'rb') as f: data = f.read()
    fs = len(data); print(f"Size: {fs:,} bytes")
    vol = parse_vol(data)
    if vol is None: print("Error: not a valid AIX BFF"); sys.exit(1)
    fmt = 'By-Inode' if vol.get('is_byinode') else 'By-Name'
    print(f"Format: {fmt} | Date: {vol['date_str']} | Device: {vol.get('device1','')} | User: {vol['user']}")
    records = parse_byinode(data) if vol.get('is_byinode') else parse_records(data)
    ir = [r for r in records if r['type']=='inode']
    d=sum(1 for r in ir if r['ftype']=='DIR'); f_=sum(1 for r in ir if r['ftype']=='FILE'); l=sum(1 for r in ir if r['ftype']=='LINK')
    print(f"Found: {len(ir)} entries ({d} dirs, {f_} files, {l} links)")
    print(f"\nExtracting to {out}/...")
    extracted = extract(data, records, out, verbose=True)
    ok = sum(1 for e in extracted if e['status']=='ok')
    print(f"\nExtracted {ok} items")
    print(f"Done.")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# Vibe coded by Claude

"""
unAmigaPFS - Amiga PFS Container/Filesystem Extractor

Extracts files from Amiga PFS container images. Supports four format variants:
  - PFS3 ADF disk images (e.g. .adf files with PFS filesystem)
  - FAT-based PFS archives (e.g. .dat files with *FAT*/*ROOT* markers)
  - PFS MIDI/multi-track containers (flags 0x04040000)
  - PFS data record files (e.g. .DTA financial data)

Usage: python3 unAmigaPFS.py <inputFile> <outputDir>
"""

import sys
import os
import struct
import json
from datetime import datetime, timedelta

AMIGA_EPOCH = datetime(1978, 1, 1)

# ─── Utility ──────────────────────────────────────────────────────────────────

def u8(d, off):
    return d[off]

def s8(d, off):
    return struct.unpack('>b', d[off:off+1])[0]

def u16be(d, off):
    return struct.unpack('>H', d[off:off+2])[0]

def u32be(d, off):
    return struct.unpack('>I', d[off:off+4])[0]

def u32le(d, off):
    return struct.unpack('<I', d[off:off+4])[0]

def u16le(d, off):
    return struct.unpack('<H', d[off:off+2])[0]

def amiga_date(days, mins, ticks):
    """Convert Amiga DateStamp (days since 1978-01-01, minutes, ticks) to string."""
    try:
        dt = AMIGA_EPOCH + timedelta(days=days, minutes=mins, seconds=ticks // 50)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, OverflowError):
        return f"days={days} mins={mins} ticks={ticks}"

def safe_filename(name):
    """Sanitise a filename for the host filesystem."""
    name = name.replace('/', '_').replace('\\', '_').replace('\x00', '')
    name = name.replace(':', '_').replace('*', '_').replace('?', '_')
    name = name.replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
    if not name:
        name = '_unnamed_'
    return name

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

# ─── Format Detection ────────────────────────────────────────────────────────

def detect_format(data):
    """Detect which PFS variant this file uses."""
    if len(data) < 8 or data[0:4] != b'PFS\x00':
        return None

    flags = u32be(data, 4)

    # Check for FAT-based archive (*FAT* marker at offset 0x20)
    if len(data) > 0x60 and data[0x20:0x25] == b'*FAT*' and data[0x50:0x56] == b'*ROOT*':
        return 'fat_archive'

    # Check for MIDI/multi-track container (flags 0x04040000)
    if flags == 0x04040000:
        return 'multitrack'

    # Check for PFS3 ADF (has PFS magic at block 2 = offset 0x400 and DB/AB blocks)
    if len(data) >= 0x800:
        if data[0x400:0x404] == b'PFS\x00':
            # Verify DB or AB blocks exist nearby
            for blk in range(3, min(50, len(data) // 512)):
                off = blk * 512
                if data[off:off+2] in (b'DB', b'AB'):
                    return 'pfs3_adf'

    # Check for data record file (text header followed by structured records)
    # Header has mostly zero/text in first 0x400 bytes, then fixed-size records
    if len(data) >= 0x500:
        header_text = data[8:128]
        if any(32 <= b < 127 for b in header_text[:40]):
            rec_start = 0x400
            # Check if records follow a regular 16-byte pattern
            nonzero_recs = 0
            for off in range(rec_start, min(rec_start + 0x200, len(data)), 16):
                if any(b != 0 for b in data[off:off+16]):
                    nonzero_recs += 1
            if nonzero_recs > 5:
                return 'data_records'

    return 'unknown'

# ─── PFS3 ADF Extractor ──────────────────────────────────────────────────────

class PFS3Extractor:
    """Extract files from a PFS3 filesystem on an ADF disk image."""

    BLOCK_SIZE = 512
    ANODE_ENTRY_SIZE = 6  # clustersize(u16) + blocknr(u16) + next(u16)
    AB_HEADER_SIZE = 16
    DB_HEADER_SIZE = 16
    ANODES_PER_BLOCK = (BLOCK_SIZE - AB_HEADER_SIZE) // ANODE_ENTRY_SIZE  # 82

    def __init__(self, data):
        self.data = data
        self.num_blocks = len(data) // self.BLOCK_SIZE
        self.volume_name = ''
        self.creation_date = ''
        self.root_anode = 5  # default
        self.anodes = {}      # anode_nr -> (clustersize, blocknr, next_anode)
        self.dir_entries = {}  # dir_anode -> list of entries

    def read_block(self, blk):
        off = blk * self.BLOCK_SIZE
        return self.data[off:off + self.BLOCK_SIZE]

    def parse_volume(self):
        """Parse volume/root block at block 2."""
        vblk = self.read_block(2)
        if vblk[0:4] != b'PFS\x00':
            return
        self.vol_date_days = u16be(vblk, 12)
        self.vol_date_mins = u16be(vblk, 14)
        self.vol_date_ticks = u16be(vblk, 16)
        self.creation_date = amiga_date(self.vol_date_days, self.vol_date_mins,
                                        self.vol_date_ticks)
        namelen = u8(vblk, 20)
        if namelen > 0 and namelen < 64:
            self.volume_name = vblk[21:21 + namelen].decode('latin-1', errors='replace').rstrip('\x00 ')

        # Parse configuration pointers
        for off in range(0x60, min(0x80, len(vblk) - 1), 2):
            val = u16be(vblk, off)
            if val != 0:
                break

    def parse_anodes(self):
        """Parse all AB (Anode Block) blocks to build the anode table.
        Uses the latest version of each seqnr AB block."""
        ab_blocks = {}  # seqnr -> highest block number

        for blk in range(self.num_blocks):
            blkdata = self.read_block(blk)
            if blkdata[0:2] == b'AB':
                seqnr = u16be(blkdata, 10)
                if seqnr not in ab_blocks or blk > ab_blocks[seqnr]:
                    ab_blocks[seqnr] = blk

        # Read anodes from the latest AB blocks
        for seqnr in sorted(ab_blocks.keys()):
            blk = ab_blocks[seqnr]
            blkdata = self.read_block(blk)
            base_anode = seqnr * self.ANODES_PER_BLOCK
            for i in range(self.ANODES_PER_BLOCK):
                off = self.AB_HEADER_SIZE + i * self.ANODE_ENTRY_SIZE
                if off + self.ANODE_ENTRY_SIZE > self.BLOCK_SIZE:
                    break
                clustersize = u16be(blkdata, off)
                blocknr = u16be(blkdata, off + 2)
                next_anode = u16be(blkdata, off + 4)
                anode_nr = base_anode + i
                if clustersize > 0 or blocknr > 0 or next_anode > 0:
                    self.anodes[anode_nr] = (clustersize, blocknr, next_anode)

    def resolve_anode_chain(self, anode_nr):
        """Follow an anode chain, returning a list of (blocknr, clustersize) tuples."""
        blocks = []
        visited = set()
        cur = anode_nr
        while cur != 0 and cur not in visited:
            visited.add(cur)
            if cur not in self.anodes:
                break
            clustersize, blocknr, next_anode = self.anodes[cur]
            if clustersize > 0 and blocknr > 0:
                blocks.append((blocknr, clustersize))
            elif clustersize == 0xFFFF:
                pass  # special marker, skip
            cur = next_anode
        return blocks

    def read_file_data(self, anode_nr, file_size):
        """Read file data by following the anode chain."""
        chain = self.resolve_anode_chain(anode_nr)
        result = bytearray()
        for blocknr, clustersize in chain:
            for i in range(clustersize):
                blk = blocknr + i
                if blk < self.num_blocks:
                    result.extend(self.read_block(blk))
        return bytes(result[:file_size])

    def parse_directories(self):
        """Parse all DB (Directory Block) blocks."""
        # Collect all DB blocks grouped by dir_anode
        db_blocks = {}  # dir_anode -> set of block nums

        for blk in range(self.num_blocks):
            blkdata = self.read_block(blk)
            if blkdata[0:2] == b'DB':
                dir_anode = u16be(blkdata, 12)
                if dir_anode not in db_blocks:
                    db_blocks[dir_anode] = set()
                db_blocks[dir_anode].add(blk)

        # Parse entries from each directory's DB blocks
        for dir_anode, blocks in db_blocks.items():
            entries = {}  # anode -> entry dict (dedup by anode)
            for blk in sorted(blocks):
                blkdata = self.read_block(blk)
                pos = self.DB_HEADER_SIZE
                while pos < self.BLOCK_SIZE:
                    entry_size = u8(blkdata, pos)
                    if entry_size == 0:
                        break
                    if pos + entry_size > self.BLOCK_SIZE:
                        break

                    entry_type = s8(blkdata, pos + 1)
                    anode = u16be(blkdata, pos + 2)
                    fsize = u32be(blkdata, pos + 4)
                    date_days = u16be(blkdata, pos + 8)
                    date_mins = u16be(blkdata, pos + 10)
                    date_ticks = u16be(blkdata, pos + 12)
                    protection = u8(blkdata, pos + 14)
                    namelen = u8(blkdata, pos + 15)

                    if namelen > 0 and pos + 16 + namelen <= pos + entry_size:
                        fname = blkdata[pos + 16:pos + 16 + namelen].decode('latin-1', errors='replace')

                        # Check for comment after name
                        comment = ''
                        name_end_pos = 16 + namelen
                        remaining = entry_size - name_end_pos
                        if remaining > 1:
                            comment_len = u8(blkdata, pos + name_end_pos)
                            if comment_len > 0 and comment_len + 1 <= remaining:
                                comment = blkdata[pos + name_end_pos + 1:
                                                   pos + name_end_pos + 1 + comment_len].decode(
                                    'latin-1', errors='replace')

                        type_map = {-3: 'file', 2: 'dir', -4: 'hardlink_file',
                                    4: 'hardlink_dir', 3: 'softlink', -5: 'rollover'}
                        type_str = type_map.get(entry_type, f'unknown({entry_type})')

                        entry = {
                            'name': fname,
                            'type': type_str,
                            'anode': anode,
                            'size': fsize,
                            'date': amiga_date(date_days, date_mins, date_ticks),
                            'protection': protection,
                            'comment': comment,
                        }
                        # Keep the entry with the most info (prefer ones with comments)
                        if anode not in entries or (comment and not entries[anode].get('comment')):
                            entries[anode] = entry

                    pos += entry_size

            if dir_anode not in self.dir_entries:
                self.dir_entries[dir_anode] = list(entries.values())
            else:
                # Merge, preferring entries not already present
                existing_anodes = {e['anode'] for e in self.dir_entries[dir_anode]}
                for e in entries.values():
                    if e['anode'] not in existing_anodes:
                        self.dir_entries[dir_anode].append(e)

    def extract(self, output_dir):
        """Extract all files from the PFS3 filesystem."""
        print(f"  PFS3 ADF filesystem")
        self.parse_volume()
        print(f"  Volume: '{self.volume_name}', Created: {self.creation_date}")

        self.parse_anodes()
        print(f"  Anodes loaded: {len(self.anodes)}")

        self.parse_directories()

        # Find the root directory anode - it's the dir_anode that isn't
        # listed as a child anode in any other directory
        all_dir_anodes = set(self.dir_entries.keys())
        child_anodes = set()
        for entries in self.dir_entries.values():
            for e in entries:
                if e['type'] == 'dir':
                    child_anodes.add(e['anode'])

        root_candidates = all_dir_anodes - child_anodes
        if root_candidates:
            self.root_anode = min(root_candidates)
        elif all_dir_anodes:
            self.root_anode = min(all_dir_anodes)

        # Recursively extract
        file_count = self._extract_dir(self.root_anode, output_dir, '')
        print(f"  Extracted {file_count} files")

        # Write metadata
        self._write_metadata(output_dir)

    def _extract_dir(self, dir_anode, base_path, rel_path):
        """Recursively extract files from a directory."""
        ensure_dir(base_path)
        count = 0
        entries = self.dir_entries.get(dir_anode, [])
        for entry in entries:
            name = safe_filename(entry['name'])
            full_path = os.path.join(base_path, name)
            entry_rel = os.path.join(rel_path, name) if rel_path else name

            if entry['type'] == 'dir':
                count += self._extract_dir(entry['anode'], full_path, entry_rel)
            elif entry['type'] == 'file':
                file_data = self.read_file_data(entry['anode'], entry['size'])
                with open(full_path, 'wb') as f:
                    f.write(file_data)
                count += 1
        return count

    def _write_metadata(self, output_dir):
        """Write filesystem metadata as JSON."""
        meta = {
            'format': 'PFS3_ADF',
            'volume_name': self.volume_name,
            'creation_date': self.creation_date,
            'block_size': self.BLOCK_SIZE,
            'total_blocks': self.num_blocks,
            'files': []
        }
        for dir_anode, entries in sorted(self.dir_entries.items()):
            for e in entries:
                meta['files'].append({
                    'dir_anode': dir_anode,
                    'name': e['name'],
                    'type': e['type'],
                    'anode': e['anode'],
                    'size': e['size'],
                    'date': e['date'],
                    'protection': e['protection'],
                    'comment': e['comment'],
                })

        with open(os.path.join(output_dir, '_pfs3_metadata.json'), 'w') as f:
            json.dump(meta, f, indent=2)

# ─── FAT Archive Extractor ───────────────────────────────────────────────────

class FATArchiveExtractor:
    """Extract files from a FAT-based PFS archive."""

    ENTRY_SIZE = 48  # Each directory entry is 48 bytes

    def __init__(self, data):
        self.data = data
        self.block_size = u32le(data, 8)
        if self.block_size == 0 or self.block_size > len(data):
            self.block_size = 4096
        self.fat_first_block = u32le(data, 0x10)
        self.fat_byte_size = u32le(data, 0x14)
        self.root_block = u32le(data, 0x40)
        self.num_blocks = len(data) // self.block_size
        self.fat = []

    def parse_fat(self):
        """Read the FAT chain table."""
        fat_start = self.fat_first_block * self.block_size
        fat_entries = self.fat_byte_size // 4
        self.fat = []
        for i in range(fat_entries):
            off = fat_start + i * 4
            if off + 4 <= len(self.data):
                self.fat.append(u32le(self.data, off))
            else:
                self.fat.append(0xFFFFFFFF)

    def follow_chain(self, start_block):
        """Follow FAT chain from start_block, return list of block numbers."""
        chain = [start_block]
        cur = start_block
        visited = {cur}
        while cur < len(self.fat) and self.fat[cur] != 0xFFFFFFFF:
            cur = self.fat[cur]
            if cur in visited or cur >= len(self.fat):
                break
            visited.add(cur)
            chain.append(cur)
        return chain

    def read_block(self, blk):
        off = blk * self.block_size
        return self.data[off:off + self.block_size]

    def read_chain_data(self, start_block, size=None):
        """Read data across a FAT chain."""
        chain = self.follow_chain(start_block)
        result = bytearray()
        for blk in chain:
            result.extend(self.read_block(blk))
        if size is not None:
            return bytes(result[:size])
        return bytes(result)

    def parse_dir_entries(self, block_num):
        """Parse directory entries from a block."""
        blkdata = self.read_block(block_num)
        entries = []
        for off in range(0, self.block_size - self.ENTRY_SIZE + 1, self.ENTRY_SIZE):
            entry_data = blkdata[off:off + self.ENTRY_SIZE]
            if all(b == 0 for b in entry_data):
                continue

            first_block = u32le(entry_data, 0)
            size = u32le(entry_data, 4)
            attrs = u32le(entry_data, 8)
            namelen = u8(entry_data, 12)
            flags = entry_data[13:16]

            if namelen == 0 or namelen > 32 or first_block >= self.num_blocks:
                continue

            name = entry_data[16:16 + namelen].decode('latin-1', errors='replace')
            is_dir = (size == self.block_size and attrs == 1)
            is_file = (attrs == 0x20)

            entries.append({
                'name': name,
                'first_block': first_block,
                'size': size,
                'attrs': attrs,
                'flags': flags.hex(),
                'is_dir': is_dir,
                'is_file': is_file,
            })
        return entries

    def extract_file(self, entry, output_path):
        """Extract a single file, handling the 5-byte data header."""
        chain = self.follow_chain(entry['first_block'])
        raw = bytearray()
        for blk in chain:
            raw.extend(self.read_block(blk))

        compressed_size = entry['size']
        if len(raw) < 5:
            with open(output_path, 'wb') as f:
                f.write(bytes(raw[:compressed_size]))
            return

        original_size = u32le(raw, 0)
        compression_type = u8(raw, 4)
        file_data = bytes(raw[5:5 + compressed_size])

        with open(output_path, 'wb') as f:
            f.write(file_data)

        return {
            'original_size': original_size,
            'compressed_size': compressed_size,
            'compression_type': compression_type,
            'actual_written': len(file_data),
        }

    def extract(self, output_dir):
        """Extract all files from the FAT archive."""
        print(f"  FAT-based PFS archive")
        print(f"  Block size: {self.block_size}, Blocks: {self.num_blocks}")

        self.parse_fat()
        print(f"  FAT entries: {len(self.fat)}")

        file_count = self._extract_dir(self.root_block, output_dir, '')
        print(f"  Extracted {file_count} files")

        self._write_metadata(output_dir)

    def _extract_dir(self, block_num, base_path, rel_path):
        """Recursively extract directory tree."""
        ensure_dir(base_path)
        entries = self.parse_dir_entries(block_num)
        count = 0

        for entry in entries:
            name = safe_filename(entry['name'])
            full_path = os.path.join(base_path, name)

            if entry['is_dir']:
                count += self._extract_dir(entry['first_block'], full_path,
                                           os.path.join(rel_path, name))
            elif entry['is_file']:
                info = self.extract_file(entry, full_path)
                count += 1

        return count

    def _write_metadata(self, output_dir):
        """Write archive metadata."""
        meta = {
            'format': 'FAT_Archive',
            'block_size': self.block_size,
            'total_blocks': self.num_blocks,
            'fat_first_block': self.fat_first_block,
            'fat_size': self.fat_byte_size,
            'root_block': self.root_block,
        }
        # Collect all files recursively
        meta['files'] = self._collect_file_info(self.root_block, '')

        with open(os.path.join(output_dir, '_fat_metadata.json'), 'w') as f:
            json.dump(meta, f, indent=2)

    def _collect_file_info(self, block_num, path):
        """Recursively collect file metadata."""
        entries = self.parse_dir_entries(block_num)
        result = []
        for entry in entries:
            rel = os.path.join(path, entry['name']) if path else entry['name']
            info = {
                'path': rel,
                'first_block': entry['first_block'],
                'size': entry['size'],
                'attrs': entry['attrs'],
                'flags': entry['flags'],
                'is_dir': entry['is_dir'],
            }
            result.append(info)
            if entry['is_dir']:
                result.extend(self._collect_file_info(entry['first_block'], rel))
        return result

# ─── Multi-track Container Extractor ─────────────────────────────────────────

class MultitrackExtractor:
    """Extract tracks/chunks from a PFS multi-track container (flags 0x04040000)."""

    ENTRY_TABLE_OFFSET = 0x400
    ENTRY_SIZE = 0x40  # 64 bytes per entry
    HEADER_TABLE_OFFSET = 0x800  # Secondary metadata block

    def __init__(self, data):
        self.data = data
        self.entries = []

    def parse_entries(self):
        """Parse the entry offset/size table."""
        off = self.ENTRY_TABLE_OFFSET
        while off + self.ENTRY_SIZE <= len(self.data) and off < self.HEADER_TABLE_OFFSET:
            flags = u32le(self.data, off)
            offset = u32le(self.data, off + 4)
            size = u32le(self.data, off + 8)

            if offset == 0 and size == 0:
                off += self.ENTRY_SIZE
                continue

            if offset > 0 and size > 0 and offset + size <= len(self.data):
                self.entries.append({
                    'flags': flags,
                    'offset': offset,
                    'size': size,
                })
            off += self.ENTRY_SIZE

    def extract(self, output_dir):
        """Extract all tracks from the container."""
        print(f"  PFS multi-track container")

        self.parse_entries()
        print(f"  Tracks found: {len(self.entries)}")

        ensure_dir(output_dir)

        # Extract header block (0x000-0x1FF)
        with open(os.path.join(output_dir, 'header.bin'), 'wb') as f:
            f.write(self.data[0:0x200])

        # Extract metadata block (0x200-0x3FF)
        with open(os.path.join(output_dir, 'metadata.bin'), 'wb') as f:
            f.write(self.data[0x200:0x400])

        # Extract entry table (0x400-0x7FF)
        with open(os.path.join(output_dir, 'entry_table.bin'), 'wb') as f:
            f.write(self.data[0x400:0x800])

        # Extract secondary header (0x800-0xBFF)
        with open(os.path.join(output_dir, 'track_header.bin'), 'wb') as f:
            f.write(self.data[0x800:0xC00])

        # Extract each track
        for i, entry in enumerate(self.entries):
            track_data = self.data[entry['offset']:entry['offset'] + entry['size']]
            fname = f'track_{i:03d}.bin'
            with open(os.path.join(output_dir, fname), 'wb') as f:
                f.write(track_data)

        # Check for trailing data after last entry
        if self.entries:
            last_end = max(e['offset'] + e['size'] for e in self.entries)
            if last_end < len(self.data):
                trailing = self.data[last_end:]
                if any(b != 0 for b in trailing):
                    with open(os.path.join(output_dir, 'trailing_data.bin'), 'wb') as f:
                        f.write(trailing)

        print(f"  Extracted {len(self.entries)} tracks + structural blocks")

        self._write_metadata(output_dir)

    def _write_metadata(self, output_dir):
        meta = {
            'format': 'Multitrack_Container',
            'file_size': len(self.data),
            'flags': u32be(self.data, 4),
            'tracks': [{
                'index': i,
                'offset': e['offset'],
                'size': e['size'],
                'flags': e['flags'],
            } for i, e in enumerate(self.entries)]
        }
        with open(os.path.join(output_dir, '_multitrack_metadata.json'), 'w') as f:
            json.dump(meta, f, indent=2)

# ─── Data Records Extractor ──────────────────────────────────────────────────

class DataRecordsExtractor:
    """Extract data from a PFS data records file (e.g. PFS.DTA)."""

    HEADER_SIZE = 0x400  # 1024-byte header
    RECORD_SIZE = 16     # 16 bytes per record

    def __init__(self, data):
        self.data = data

    def parse_header(self):
        """Parse the text header fields."""
        header = self.data[:self.HEADER_SIZE]
        fields = {}

        # The header has several null-terminated text strings after byte 8
        pos = 8
        field_names = ['company', 'account_type', 'account_number', 'identifier']
        for fname in field_names:
            end = header.find(b'\x00', pos)
            if end < 0 or end > self.HEADER_SIZE:
                break
            text = header[pos:end].decode('latin-1', errors='replace').strip()
            if text:
                fields[fname] = text
            # Skip to next non-null byte
            while end < self.HEADER_SIZE and header[end] == 0:
                end += 1
            pos = end

        # Extract any remaining non-zero data from header
        remaining_data = header[pos:]
        fields['header_remaining'] = remaining_data.hex() if any(b != 0 for b in remaining_data) else ''

        return fields

    def parse_records(self):
        """Parse the fixed-size records."""
        records = []
        off = self.HEADER_SIZE
        while off + self.RECORD_SIZE <= len(self.data):
            rec = self.data[off:off + self.RECORD_SIZE]
            if all(b == 0 for b in rec):
                records.append(None)  # null record marker
            else:
                # Each record contains 8 u16 big-endian values
                values = []
                for i in range(0, self.RECORD_SIZE, 2):
                    values.append(u16be(rec, i))
                records.append({
                    'offset': off,
                    'raw': rec.hex(),
                    'values': values,
                })
            off += self.RECORD_SIZE
        return records

    def extract(self, output_dir):
        """Extract header and records from the data file."""
        print(f"  PFS data records file")
        ensure_dir(output_dir)

        fields = self.parse_header()
        for k, v in fields.items():
            if v and k != 'header_remaining':
                print(f"    {k}: {v}")

        records = self.parse_records()
        non_null = [r for r in records if r is not None]
        print(f"  Total record slots: {len(records)}, Non-null records: {len(non_null)}")

        # Write raw header
        with open(os.path.join(output_dir, 'header.bin'), 'wb') as f:
            f.write(self.data[:self.HEADER_SIZE])

        # Write raw records
        with open(os.path.join(output_dir, 'records.bin'), 'wb') as f:
            f.write(self.data[self.HEADER_SIZE:])

        # Write records as CSV
        with open(os.path.join(output_dir, 'records.csv'), 'w') as f:
            f.write('offset,v0,v1,v2,v3,v4,v5,v6,v7,raw_hex\n')
            for rec in non_null:
                vals = ','.join(str(v) for v in rec['values'])
                f.write(f"0x{rec['offset']:04x},{vals},{rec['raw']}\n")

        print(f"  Extracted header + {len(non_null)} data records")

        self._write_metadata(output_dir, fields, records)

    def _write_metadata(self, output_dir, fields, records):
        non_null = [r for r in records if r is not None]
        meta = {
            'format': 'Data_Records',
            'file_size': len(self.data),
            'header_size': self.HEADER_SIZE,
            'record_size': self.RECORD_SIZE,
            'header_fields': {k: v for k, v in fields.items() if k != 'header_remaining'},
            'total_record_slots': len(records),
            'non_null_records': len(non_null),
        }
        with open(os.path.join(output_dir, '_data_metadata.json'), 'w') as f:
            json.dump(meta, f, indent=2)

# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(input_file):
        print(f"Error: '{input_file}' not found")
        sys.exit(1)

    with open(input_file, 'rb') as f:
        data = f.read()

    print(f"Processing: {input_file} ({len(data)} bytes)")

    fmt = detect_format(data)
    if fmt is None:
        print("Error: Not a PFS file (missing PFS\\0 magic)")
        sys.exit(1)

    print(f"Detected format: {fmt}")
    ensure_dir(output_dir)

    if fmt == 'pfs3_adf':
        extractor = PFS3Extractor(data)
        extractor.extract(output_dir)
    elif fmt == 'fat_archive':
        extractor = FATArchiveExtractor(data)
        extractor.extract(output_dir)
    elif fmt == 'multitrack':
        extractor = MultitrackExtractor(data)
        extractor.extract(output_dir)
    elif fmt == 'data_records':
        extractor = DataRecordsExtractor(data)
        extractor.extract(output_dir)
    else:
        print(f"Warning: Unknown PFS variant, extracting raw data")
        ensure_dir(output_dir)
        with open(os.path.join(output_dir, 'raw_data.bin'), 'wb') as f:
            f.write(data)

    print("Done.")


if __name__ == '__main__':
    main()

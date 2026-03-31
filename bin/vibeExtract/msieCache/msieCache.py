#!/usr/bin/env python3
# Vibe coded by Claude
"""
unMSIECache - Microsoft Internet Explorer Cache Index File Extractor

Extracts all records (URL entries, redirects, leaked entries, hash tables)
from MSIE cache index.dat files (versions 3.2, 4.7, and 5.2).

Usage: python3 unMSIECache.py <inputFile> <outputDir>
"""

import struct
import sys
import os
import json
import datetime

BLOCK_SIZE = 128

# Record signatures
SIG_URL  = b'URL '
SIG_REDR = b'REDR'
SIG_LEAK = b'LEAK'
SIG_HASH = b'HASH'

# Fill patterns
FILL_BADFOOD  = 0x0BADF00D
FILL_DEADBEEF = 0xDEADBEEF

# Cache entry type flags
CACHE_FLAGS = {
    0x00000001: "NORMAL_CACHE_ENTRY",
    0x00000004: "STABLE_CACHE_ENTRY",
    0x00000010: "TRACK_OFFLINE_CACHE_ENTRY",
    0x00000040: "COOKIE_CACHE_ENTRY",
    0x00000100: "TRACK_OFFLINE",
    0x00000200: "TRACK_ONLINE",
    0x00000800: "SPARSE_CACHE_ENTRY",
    0x00001000: "STICKY_CACHE_ENTRY",
    0x00008000: "INSTALLED_CACHE_ENTRY",
    0x00040000: "POST_RESPONSE",
    0x00200000: "URLHISTORY_CACHE_ENTRY",
    0x04000000: "EDITED_CACHE_ENTRY",
}


def filetime_to_datetime(ft_low, ft_high):
    """Convert Windows FILETIME to datetime string."""
    ft = (ft_high << 32) | ft_low
    if ft == 0 or ft == 0x7FFFFFFFFFFFFFFF:
        return None
    try:
        epoch = datetime.datetime(1601, 1, 1)
        delta = datetime.timedelta(microseconds=ft // 10)
        dt = epoch + delta
        if dt.year < 1970 or dt.year > 2100:
            return None
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except (OverflowError, ValueError, OSError):
        return None


def decode_cache_flags(flags):
    """Decode cache entry type flags into a list of flag names."""
    names = []
    for bit, name in CACHE_FLAGS.items():
        if flags & bit:
            names.append(name)
    return names


def read_cstring(data, offset, max_len=4096):
    """Read a null-terminated string from data at offset."""
    if offset == 0 or offset >= len(data):
        return ""
    end = data.find(b'\x00', offset, min(offset + max_len, len(data)))
    if end < 0:
        end = min(offset + max_len, len(data))
    return data[offset:end].decode('ascii', errors='replace')


def parse_file_header(data):
    """Parse the file header and return a dict of metadata."""
    header = {}

    if len(data) < 0x1C + 4:
        return None

    sig = data[0:28]
    if not sig.startswith(b'Client UrlCache MMF Ver '):
        return None

    version_str = sig[24:27].decode('ascii', errors='replace')
    header['version'] = version_str
    header['signature'] = sig.rstrip(b'\x00').decode('ascii', errors='replace')

    header['file_size'] = struct.unpack_from("<I", data, 0x1C)[0]
    header['hash_table_offset'] = struct.unpack_from("<I", data, 0x20)[0]
    header['num_blocks'] = struct.unpack_from("<I", data, 0x24)[0]
    header['num_allocated_blocks'] = struct.unpack_from("<I", data, 0x28)[0]

    if version_str == '5.2':
        header['padding_2c'] = struct.unpack_from("<I", data, 0x2C)[0]
        header['cache_limit'] = struct.unpack_from("<Q", data, 0x30)[0]
        header['exempt_usage'] = struct.unpack_from("<Q", data, 0x38)[0]
        header['reserved_40'] = struct.unpack_from("<Q", data, 0x40)[0]
        header['num_directories'] = struct.unpack_from("<I", data, 0x48)[0]
        header['reserved_4c'] = struct.unpack_from("<I", data, 0x4C)[0]

        dirs = []
        for i in range(min(header['num_directories'], 32)):
            off = 0x50 + i * 12
            if off + 12 > len(data):
                break
            name_bytes = data[off:off+8]
            count = struct.unpack_from("<I", data, off + 8)[0]
            if name_bytes[0] == 0:
                name = ""
            else:
                name = name_bytes.decode('ascii', errors='replace').rstrip()
            dirs.append({'name': name, 'file_count': count})
        header['directories'] = dirs

        # Parse allocation bitmap
        bitmap_offset = 0x0250
        if header['num_blocks'] > 0:
            bitmap_size = (header['num_blocks'] + 7) // 8
            if bitmap_offset + bitmap_size <= len(data):
                header['bitmap_offset'] = bitmap_offset
                header['bitmap_size'] = bitmap_size

    elif version_str == '4.7':
        header['field_2c'] = struct.unpack_from("<I", data, 0x2C)[0]
        header['cache_limit'] = struct.unpack_from("<I", data, 0x30)[0]

        # Parse inline hash entries at 0x50
        inline_entries = []
        for i in range(32):
            off = 0x50 + i * 12
            if off + 12 > len(data):
                break
            entry_bytes = data[off:off+12]
            flag = entry_bytes[0]
            hash_bytes = entry_bytes[1:4]
            data1 = struct.unpack_from("<I", entry_bytes, 4)[0]
            data2 = struct.unpack_from("<I", entry_bytes, 8)[0]
            if flag != 0 or data1 != 0 or data2 != 0:
                inline_entries.append({
                    'index': i,
                    'flag': flag,
                    'hash_high': hash_bytes.hex(),
                    'data1': data1,
                    'data2': data2,
                })
        header['inline_hash_entries'] = inline_entries

    elif version_str == '3.2':
        header['field_24'] = struct.unpack_from("<I", data, 0x24)[0]
        header['cache_limit'] = struct.unpack_from("<I", data, 0x30)[0]

    return header


def parse_hash_record(data, offset):
    """Parse a HASH record at the given offset."""
    if offset + 16 > len(data):
        return None
    sig = data[offset:offset+4]
    if sig != SIG_HASH:
        return None

    nblocks = struct.unpack_from("<I", data, offset + 4)[0]
    next_hash = struct.unpack_from("<I", data, offset + 8)[0]
    record_size = nblocks * BLOCK_SIZE

    entries = []
    entry_offset = offset + 0x10
    while entry_offset + 8 <= offset + record_size and entry_offset + 8 <= len(data):
        flag = struct.unpack_from("<I", data, entry_offset)[0]
        rec_offset = struct.unpack_from("<I", data, entry_offset + 4)[0]

        if flag == 3 or (flag == 0 and rec_offset == 0):
            status = "free"
        elif flag == 1:
            status = "deleted"
        else:
            status = "occupied"

        entries.append({
            'hash_value': flag,
            'record_offset': rec_offset,
            'status': status,
        })
        entry_offset += 8

    return {
        'offset': offset,
        'num_blocks': nblocks,
        'record_size': record_size,
        'next_hash_offset': next_hash,
        'entries': entries,
        'occupied_count': sum(1 for e in entries if e['status'] == 'occupied'),
        'free_count': sum(1 for e in entries if e['status'] == 'free'),
        'deleted_count': sum(1 for e in entries if e['status'] == 'deleted'),
    }


def parse_url_record_v52(data, offset):
    """Parse a URL record (v5.2) at the given offset."""
    if offset + 0x68 > len(data):
        return None

    nblocks = struct.unpack_from("<I", data, offset + 4)[0]
    record_size = nblocks * BLOCK_SIZE
    if offset + record_size > len(data):
        record_size = len(data) - offset

    rec = {
        'type': 'URL',
        'offset': offset,
        'num_blocks': nblocks,
        'record_size': record_size,
    }

    # Timestamps
    last_mod_lo = struct.unpack_from("<I", data, offset + 0x08)[0]
    last_mod_hi = struct.unpack_from("<I", data, offset + 0x0C)[0]
    last_acc_lo = struct.unpack_from("<I", data, offset + 0x10)[0]
    last_acc_hi = struct.unpack_from("<I", data, offset + 0x14)[0]
    expiry_lo = struct.unpack_from("<I", data, offset + 0x18)[0]
    expiry_hi = struct.unpack_from("<I", data, offset + 0x1C)[0]

    rec['last_modified_time'] = filetime_to_datetime(last_mod_lo, last_mod_hi)
    rec['last_modified_raw'] = (last_mod_hi << 32) | last_mod_lo
    rec['last_accessed_time'] = filetime_to_datetime(last_acc_lo, last_acc_hi)
    rec['last_accessed_raw'] = (last_acc_hi << 32) | last_acc_lo
    rec['expiry_time'] = filetime_to_datetime(expiry_lo, expiry_hi)
    rec['expiry_raw'] = (expiry_hi << 32) | expiry_lo

    rec['cached_file_size'] = struct.unpack_from("<I", data, offset + 0x20)[0]
    rec['cached_file_size_high'] = struct.unpack_from("<I", data, offset + 0x24)[0]
    rec['reserved_28'] = struct.unpack_from("<I", data, offset + 0x28)[0]
    rec['reserved_2c'] = struct.unpack_from("<I", data, offset + 0x2C)[0]
    rec['data_start_offset'] = struct.unpack_from("<I", data, offset + 0x30)[0]

    url_offset = struct.unpack_from("<I", data, offset + 0x34)[0]
    dir_byte = data[offset + 0x38] if offset + 0x38 < len(data) else 0
    sync_bytes = data[offset + 0x39:offset + 0x3C]
    fname_offset = struct.unpack_from("<I", data, offset + 0x3C)[0]
    cache_entry_type = struct.unpack_from("<I", data, offset + 0x40)[0]
    header_offset = struct.unpack_from("<I", data, offset + 0x44)[0]
    header_size = struct.unpack_from("<I", data, offset + 0x48)[0]
    file_ext_offset = struct.unpack_from("<I", data, offset + 0x4C)[0]

    sync_lo = struct.unpack_from("<I", data, offset + 0x50)[0]
    sync_hi = struct.unpack_from("<I", data, offset + 0x54)[0]
    rec['last_sync_time'] = filetime_to_datetime(sync_lo, sync_hi)
    rec['last_sync_raw'] = (sync_hi << 32) | sync_lo
    rec['hit_count'] = struct.unpack_from("<I", data, offset + 0x58)[0]
    rec['use_count'] = struct.unpack_from("<I", data, offset + 0x5C)[0]

    if rec['data_start_offset'] >= 0x60:
        rec['exempt_delta'] = struct.unpack_from("<I", data, offset + 0x60)[0]
        if offset + 0x64 + 4 <= len(data):
            rec['sentinel'] = struct.unpack_from("<I", data, offset + 0x64)[0]

    rec['directory_index'] = dir_byte
    rec['sync_info'] = sync_bytes.hex()
    rec['cache_entry_type'] = cache_entry_type
    rec['cache_entry_flags'] = decode_cache_flags(cache_entry_type)

    # Read strings
    rec['url'] = read_cstring(data, offset + url_offset) if url_offset else ""
    rec['filename'] = read_cstring(data, offset + fname_offset) if fname_offset else ""
    rec['file_extension'] = read_cstring(data, offset + file_ext_offset) if file_ext_offset else ""

    if header_offset and header_offset < record_size:
        header_data_start = offset + header_offset
        header_data_end = min(header_data_start + header_size, offset + record_size, len(data))
        header_raw = data[header_data_start:header_data_end]
        null_pos = header_raw.find(b'\x00')
        if null_pos >= 0:
            header_raw = header_raw[:null_pos]
        rec['http_headers'] = header_raw.decode('ascii', errors='replace')
        rec['header_info_size'] = header_size
    else:
        rec['http_headers'] = ""
        rec['header_info_size'] = 0

    # Store the raw record bytes for completeness
    rec['raw_bytes'] = data[offset:offset + record_size]

    return rec


def parse_url_record_v47(data, offset):
    """Parse a URL record (v4.7) at the given offset."""
    if offset + 0x68 > len(data):
        return None

    nblocks = struct.unpack_from("<I", data, offset + 4)[0]
    record_size = nblocks * BLOCK_SIZE
    if offset + record_size > len(data):
        record_size = len(data) - offset

    rec = {
        'type': 'URL',
        'offset': offset,
        'num_blocks': nblocks,
        'record_size': record_size,
    }

    # Timestamps - v4.7 uses full FILETIMEs including for expiry
    last_mod_lo = struct.unpack_from("<I", data, offset + 0x08)[0]
    last_mod_hi = struct.unpack_from("<I", data, offset + 0x0C)[0]
    last_acc_lo = struct.unpack_from("<I", data, offset + 0x10)[0]
    last_acc_hi = struct.unpack_from("<I", data, offset + 0x14)[0]
    expiry_lo = struct.unpack_from("<I", data, offset + 0x18)[0]
    expiry_hi = struct.unpack_from("<I", data, offset + 0x1C)[0]

    rec['last_modified_time'] = filetime_to_datetime(last_mod_lo, last_mod_hi)
    rec['last_modified_raw'] = (last_mod_hi << 32) | last_mod_lo
    rec['last_accessed_time'] = filetime_to_datetime(last_acc_lo, last_acc_hi)
    rec['last_accessed_raw'] = (last_acc_hi << 32) | last_acc_lo
    rec['expiry_time'] = filetime_to_datetime(expiry_lo, expiry_hi)
    rec['expiry_raw'] = (expiry_hi << 32) | expiry_lo

    rec['cached_file_size'] = struct.unpack_from("<I", data, offset + 0x20)[0]
    rec['cached_file_size_high'] = struct.unpack_from("<I", data, offset + 0x24)[0]
    rec['reserved_28'] = struct.unpack_from("<I", data, offset + 0x28)[0]
    rec['reserved_2c'] = struct.unpack_from("<I", data, offset + 0x2C)[0]
    rec['reserved_30'] = struct.unpack_from("<I", data, offset + 0x30)[0]

    file_ext_offset = struct.unpack_from("<I", data, offset + 0x34)[0]
    url_offset = struct.unpack_from("<I", data, offset + 0x38)[0]
    fname_offset = struct.unpack_from("<I", data, offset + 0x3C)[0]
    dir_index = struct.unpack_from("<I", data, offset + 0x40)[0]
    cache_entry_type = struct.unpack_from("<I", data, offset + 0x44)[0]
    header_offset = struct.unpack_from("<I", data, offset + 0x48)[0]
    header_size = struct.unpack_from("<I", data, offset + 0x4C)[0]

    rec['reserved_50'] = struct.unpack_from("<I", data, offset + 0x50)[0]
    rec['last_sync_raw'] = struct.unpack_from("<I", data, offset + 0x54)[0]
    rec['hit_count'] = struct.unpack_from("<I", data, offset + 0x58)[0]
    rec['use_count'] = struct.unpack_from("<I", data, offset + 0x5C)[0]

    rec['directory_index'] = dir_index & 0xFF
    rec['data_start_offset'] = 0x68  # v4.7 data always starts here
    rec['cache_entry_type'] = cache_entry_type
    rec['cache_entry_flags'] = decode_cache_flags(cache_entry_type)

    rec['url'] = read_cstring(data, offset + url_offset) if url_offset and url_offset < record_size else ""

    if fname_offset and fname_offset != 0xFFFFFFFF and fname_offset < record_size:
        rec['filename'] = read_cstring(data, offset + fname_offset)
    else:
        rec['filename'] = ""

    if file_ext_offset and file_ext_offset < record_size:
        rec['file_extension'] = read_cstring(data, offset + file_ext_offset)
    else:
        rec['file_extension'] = ""

    if header_offset and header_offset < record_size:
        header_data_start = offset + header_offset
        header_data_end = min(header_data_start + header_size, offset + record_size, len(data))
        header_raw = data[header_data_start:header_data_end]
        null_pos = header_raw.find(b'\x00')
        if null_pos >= 0:
            header_raw = header_raw[:null_pos]
        rec['http_headers'] = header_raw.decode('ascii', errors='replace')
        rec['header_info_size'] = header_size
    else:
        rec['http_headers'] = ""
        rec['header_info_size'] = 0

    rec['raw_bytes'] = data[offset:offset + record_size]
    return rec


def parse_leak_record(data, offset, version):
    """Parse a LEAK record. Same structure as URL but with DEADBEEF fields."""
    if version == '4.7':
        rec = parse_url_record_v47(data, offset)
    else:
        rec = parse_url_record_v52(data, offset)

    if rec:
        rec['type'] = 'LEAK'
        # Clean up DEADBEEF-contaminated fields
        deadbeef_qword = 0xDEADBEEFDEADBEEF
        if rec.get('last_modified_raw') == deadbeef_qword:
            rec['last_modified_time'] = None
            rec['last_modified_raw'] = 0
        if rec.get('last_accessed_raw') == deadbeef_qword:
            rec['last_accessed_time'] = None
            rec['last_accessed_raw'] = 0
        if rec.get('expiry_raw') == deadbeef_qword:
            rec['expiry_time'] = None
            rec['expiry_raw'] = 0
        if rec.get('cached_file_size') == FILL_DEADBEEF:
            rec['cached_file_size'] = 0
        if rec.get('cached_file_size_high') == FILL_DEADBEEF:
            rec['cached_file_size_high'] = 0
        if rec.get('cache_entry_type') == FILL_DEADBEEF:
            rec['cache_entry_type'] = 0
            rec['cache_entry_flags'] = []
        if rec.get('hit_count') == FILL_DEADBEEF:
            rec['hit_count'] = 0
        if rec.get('use_count') == FILL_DEADBEEF:
            rec['use_count'] = 0
        # Check if URL/filename/headers contain DEADBEEF bytes
        deadbeef_str = '\xef\xbe\xad\xde'
        if rec.get('url', '').startswith(deadbeef_str):
            rec['url'] = ""
        if rec.get('filename', '').startswith(deadbeef_str):
            rec['filename'] = ""
        if rec.get('http_headers', '').startswith(deadbeef_str):
            rec['http_headers'] = ""

    return rec


def parse_redr_record(data, offset):
    """Parse a REDR (redirect) record."""
    if offset + 0x10 > len(data):
        return None

    nblocks = struct.unpack_from("<I", data, offset + 4)[0]
    record_size = nblocks * BLOCK_SIZE
    if offset + record_size > len(data):
        record_size = len(data) - offset

    hash_entry_offset = struct.unpack_from("<I", data, offset + 0x08)[0]
    hash_value = struct.unpack_from("<I", data, offset + 0x0C)[0]

    url = read_cstring(data, offset + 0x10, record_size - 0x10)

    return {
        'type': 'REDR',
        'offset': offset,
        'num_blocks': nblocks,
        'record_size': record_size,
        'hash_entry_offset': hash_entry_offset,
        'hash_value': hash_value,
        'url': url,
        'raw_bytes': data[offset:offset + record_size],
    }


def parse_v32_record(data, offset, slot_size):
    """Parse a v3.2 record at a fixed-size slot."""
    if offset + 0x70 > len(data):
        return None

    rec = {
        'type': 'URL',
        'offset': offset,
        'num_blocks': slot_size // BLOCK_SIZE,
        'record_size': slot_size,
    }

    rec['hash_value'] = struct.unpack_from("<I", data, offset + 0x00)[0]
    rec['reserved_04'] = struct.unpack_from("<I", data, offset + 0x04)[0]
    rec['next_offset'] = struct.unpack_from("<I", data, offset + 0x08)[0]
    rec['reserved_0c'] = struct.unpack_from("<I", data, offset + 0x0C)[0]
    rec['reserved_10'] = struct.unpack_from("<I", data, offset + 0x10)[0]
    url_offset = struct.unpack_from("<I", data, offset + 0x14)[0]
    rec['filename_offset_raw'] = struct.unpack_from("<I", data, offset + 0x18)[0]
    rec['reserved_1c'] = struct.unpack_from("<I", data, offset + 0x1C)[0]
    rec['reserved_20'] = struct.unpack_from("<I", data, offset + 0x20)[0]
    rec['reserved_24'] = struct.unpack_from("<I", data, offset + 0x24)[0]

    last_mod_lo = struct.unpack_from("<I", data, offset + 0x28)[0]
    last_mod_hi = struct.unpack_from("<I", data, offset + 0x2C)[0]
    last_acc_lo = struct.unpack_from("<I", data, offset + 0x30)[0]
    last_acc_hi = struct.unpack_from("<I", data, offset + 0x34)[0]
    expiry_lo = struct.unpack_from("<I", data, offset + 0x38)[0]
    expiry_hi = struct.unpack_from("<I", data, offset + 0x3C)[0]

    rec['last_modified_time'] = filetime_to_datetime(last_mod_lo, last_mod_hi)
    rec['last_modified_raw'] = (last_mod_hi << 32) | last_mod_lo
    rec['last_accessed_time'] = filetime_to_datetime(last_acc_lo, last_acc_hi)
    rec['last_accessed_raw'] = (last_acc_hi << 32) | last_acc_lo
    rec['expiry_time'] = filetime_to_datetime(expiry_lo, expiry_hi)
    rec['expiry_raw'] = (expiry_hi << 32) | expiry_lo

    rec['cache_entry_type'] = struct.unpack_from("<I", data, offset + 0x40)[0]
    rec['cache_entry_flags'] = decode_cache_flags(rec['cache_entry_type'])
    rec['data_size'] = struct.unpack_from("<I", data, offset + 0x44)[0]
    rec['header_info_size'] = struct.unpack_from("<I", data, offset + 0x48)[0]
    rec['reserved_4c'] = struct.unpack_from("<I", data, offset + 0x4C)[0]
    rec['hash_value2'] = struct.unpack_from("<I", data, offset + 0x50)[0]
    rec['hit_count'] = struct.unpack_from("<I", data, offset + 0x54)[0]

    rec['cached_file_size'] = 0
    rec['cached_file_size_high'] = 0
    rec['directory_index'] = 0
    rec['use_count'] = 0
    rec['data_start_offset'] = 0x70

    if url_offset and url_offset < slot_size:
        rec['url'] = read_cstring(data, offset + url_offset, slot_size - url_offset)
    else:
        rec['url'] = ""

    fname_off = rec['filename_offset_raw']
    if fname_off and fname_off < slot_size:
        rec['filename'] = read_cstring(data, offset + fname_off, slot_size - fname_off)
    else:
        rec['filename'] = ""

    rec['file_extension'] = ""

    # Read header/title info after the URL string
    url_end = offset + url_offset + len(rec['url']) + 1 if rec['url'] else offset + 0x70
    header_info_end = min(offset + slot_size, len(data))
    if url_end < header_info_end and rec['header_info_size'] > 0:
        hdr_data = data[url_end:header_info_end]
        # The header info contains binary metadata followed by a title string
        # Try to extract the readable title
        readable_parts = []
        i = 0
        while i < len(hdr_data):
            if 32 <= hdr_data[i] < 127:
                start = i
                while i < len(hdr_data) and 32 <= hdr_data[i] < 127:
                    i += 1
                if i - start >= 4:
                    readable_parts.append(hdr_data[start:i].decode('ascii', errors='replace'))
            i += 1
        rec['http_headers'] = '\n'.join(readable_parts) if readable_parts else ""
    else:
        rec['http_headers'] = ""

    rec['raw_bytes'] = data[offset:offset + slot_size]
    return rec


def scan_v32_records(data, header):
    """Scan a v3.2 file for records in fixed-size slots."""
    records = {
        'hash': [],
        'url': [],
        'redr': [],
        'leak': [],
    }

    fsize = len(data)

    # Determine slot size from filename or file structure
    # v3.2 files use fixed-size slots: 256 bytes for MM256, 2048 for MM2048
    # The slot size determines the record area layout
    # We detect slot size by looking at the hash table entry size and record spacing
    # The h20 field, when non-zero, points to the first record's data area

    h20 = header['hash_table_offset']
    h24 = header.get('field_24', header.get('num_blocks', 0))
    h28 = header['num_allocated_blocks']

    if h28 == 0:
        return records  # No records

    # Try to figure out slot size
    # h20 is the offset to first record data (e.g. 0x404)
    # The hash table is at 0x40 with h24 entries
    # Each hash entry is 4 bytes (just a DWORD value or offset)
    # Hash table: 0x40 to 0x40 + h24 * 4
    # Then padding, then record slots start

    # The slot size is either 256 or 2048 based on the file
    # We can detect it: if h20 is at 0x400-range, slot_size is 256
    # If h20 is at 0x800-range, slot_size is 2048

    if h20 == 0:
        return records

    # Determine slot size by checking where h20 falls
    # Records start at a slot-aligned boundary
    # 0x400 = 1024, if slot_size=256, first record slot = 4 (1024/256)
    # 0x800 = 2048, if slot_size=2048, first record slot = 1 (2048/2048)
    slot_size = 256  # default
    if h20 >= 0x800:
        slot_size = 2048

    # Calculate record area start (round down h20 to slot boundary)
    rec_area_start = (h20 // slot_size) * slot_size

    # Scan through record slots
    offset = rec_area_start
    while offset + slot_size <= fsize:
        slot_data = data[offset:offset+slot_size]

        # Check if slot is occupied (has non-zero content)
        if any(b != 0 for b in slot_data):
            # Check if this looks like a record
            # v3.2 records have URL offset at +0x14 (typically 0x70)
            url_off_val = struct.unpack_from("<I", slot_data, 0x14)[0] if len(slot_data) > 0x18 else 0
            if url_off_val > 0 and url_off_val < slot_size:
                # Verify there's a readable string at the URL offset
                str_start = offset + url_off_val
                if str_start < fsize and data[str_start] >= 0x20 and data[str_start] < 0x7F:
                    rec = parse_v32_record(data, offset, slot_size)
                    if rec and rec['url']:
                        records['url'].append(rec)

        offset += slot_size

    return records


def scan_records(data, version):
    """Scan the entire file for records on 128-byte boundaries."""
    records = {
        'hash': [],
        'url': [],
        'redr': [],
        'leak': [],
    }

    if version == '3.2':
        header = parse_file_header(data)
        if header:
            return scan_v32_records(data, header)
        return records

    offset = 0
    while offset < len(data):
        if offset + 4 > len(data):
            break

        sig = data[offset:offset+4]

        if sig == SIG_HASH:
            rec = parse_hash_record(data, offset)
            if rec:
                records['hash'].append(rec)
                offset += rec['record_size']
                continue

        elif sig == SIG_URL:
            if version == '4.7':
                rec = parse_url_record_v47(data, offset)
            else:
                rec = parse_url_record_v52(data, offset)
            if rec:
                records['url'].append(rec)
                offset += rec['record_size']
                continue

        elif sig == SIG_REDR:
            rec = parse_redr_record(data, offset)
            if rec:
                records['redr'].append(rec)
                offset += rec['record_size']
                continue

        elif sig == SIG_LEAK:
            rec = parse_leak_record(data, offset, version)
            if rec:
                records['leak'].append(rec)
                offset += rec['record_size']
                continue

        offset += BLOCK_SIZE

    return records


def format_record_text(rec):
    """Format a record as human-readable text."""
    lines = []
    rtype = rec['type']

    lines.append(f"Type: {rtype}")
    lines.append(f"Offset: 0x{rec['offset']:08X}")
    lines.append(f"Blocks: {rec['num_blocks']} ({rec['record_size']} bytes)")

    if rtype in ('URL', 'LEAK'):
        if rec.get('url'):
            lines.append(f"URL: {rec['url']}")
        if rec.get('filename'):
            lines.append(f"Filename: {rec['filename']}")
        if rec.get('directory_index') is not None:
            di = rec['directory_index']
            if di == 0xFE:
                lines.append("Directory: (none)")
            else:
                lines.append(f"Directory Index: {di}")
        if rec.get('cached_file_size'):
            sz = rec['cached_file_size']
            if rec.get('cached_file_size_high'):
                sz |= rec['cached_file_size_high'] << 32
            lines.append(f"Cached File Size: {sz}")
        if rec.get('last_modified_time'):
            lines.append(f"Last Modified: {rec['last_modified_time']}")
        if rec.get('last_accessed_time'):
            lines.append(f"Last Accessed: {rec['last_accessed_time']}")
        if rec.get('expiry_time'):
            lines.append(f"Expiry: {rec['expiry_time']}")
        if rec.get('last_sync_time'):
            lines.append(f"Last Sync: {rec['last_sync_time']}")
        if rec.get('cache_entry_flags'):
            lines.append(f"Entry Type: {' | '.join(rec['cache_entry_flags'])} (0x{rec['cache_entry_type']:08X})")
        if rec.get('hit_count') and rec['hit_count'] < 0x100000:
            lines.append(f"Hit Count: {rec['hit_count']}")
        if rec.get('http_headers'):
            lines.append(f"HTTP Headers:")
            for hdr_line in rec['http_headers'].split('\r\n'):
                if hdr_line:
                    lines.append(f"  {hdr_line}")
        if rec.get('file_extension'):
            lines.append(f"File Extension: {rec['file_extension']}")

    elif rtype == 'REDR':
        if rec.get('url'):
            lines.append(f"Redirect URL: {rec['url']}")
        lines.append(f"Hash Entry Offset: 0x{rec['hash_entry_offset']:08X}")
        lines.append(f"Hash Value: 0x{rec['hash_value']:08X}")

    return '\n'.join(lines)


def extract_domain(rec):
    """Extract a filesystem-safe domain name from a record's URL."""
    url = rec.get('url', '')
    if not url:
        fname = rec.get('filename', '')
        if fname:
            return '_local_files'
        return '_unknown'

    # Strip common prefixes to get to the authority part
    stripped = url
    for prefix in ['Visited: ', 'Cookie:']:
        if stripped.startswith(prefix):
            stripped = stripped[len(prefix):]
            break
    # Strip username@ (e.g. "user@http://...")
    if '@' in stripped:
        at_pos = stripped.index('@')
        rest = stripped[at_pos + 1:]
        if rest.startswith('http://') or rest.startswith('https://') or rest.startswith('ftp://'):
            stripped = rest
        elif '/' in stripped[:at_pos] or ':' in stripped[:at_pos]:
            pass  # the @ is part of the URL path, not a username
        else:
            stripped = rest

    for prefix in ['http://', 'https://', 'ftp://']:
        if stripped.startswith(prefix):
            stripped = stripped[len(prefix):]
            break

    # Handle res:// and other local schemes
    if '://' in stripped:
        scheme_end = stripped.index('://')
        scheme = stripped[:scheme_end].lower()
        if scheme in ('res', 'file', 'about', 'javascript', 'data', 'ms-its', 'mk'):
            return f'_scheme_{scheme}'
        stripped = stripped[scheme_end + 3:]

    # Extract host (everything up to first / or : or ?)
    host = ''
    for ch in stripped:
        if ch in '/:?#':
            break
        host += ch

    host = host.strip().lower()
    if not host:
        return '_unknown'

    # Sanitize for filesystem
    safe = ''.join(c if c.isalnum() or c in '.-_' else '_' for c in host)
    safe = safe.strip('._')
    return safe if safe else '_unknown'


def write_record_file_all(output_dir, index, rec):
    """Write a single record to its own file (--all mode)."""
    rtype = rec['type'].lower()
    fname = f"{index:06d}_{rtype}"
    url = rec.get('url', '')
    if url:
        for prefix in ['http://', 'https://', 'Visited: ', 'Cookie:']:
            if url.startswith(prefix):
                url = url[len(prefix):]
                break
        if '@' in url and url.index('@') < 60:
            url = url[url.index('@') + 1:]
        safe = ''.join(c if c.isalnum() or c in '.-_' else '_' for c in url[:60])
        safe = safe.strip('_')
        if safe:
            fname += f"_{safe}"

    txt_path = os.path.join(output_dir, fname + ".txt")
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(format_record_text(rec))
        f.write('\n')

    if rec.get('raw_bytes'):
        bin_path = os.path.join(output_dir, fname + ".bin")
        with open(bin_path, 'wb') as f:
            f.write(rec['raw_bytes'])


def process_file(input_path, output_dir, write_all=False):
    """Process a single MSIE cache index file."""
    with open(input_path, 'rb') as f:
        data = f.read()

    if len(data) < 28:
        print(f"  ERROR: File too small ({len(data)} bytes)")
        return

    header = parse_file_header(data)
    if not header:
        print(f"  ERROR: Not a valid MSIE cache file")
        return

    version = header['version']
    print(f"  Version: {version}")
    print(f"  File size: {len(data)} bytes")
    print(f"  Hash table offset: 0x{header['hash_table_offset']:X}")
    print(f"  Blocks: {header['num_blocks']} total, {header['num_allocated_blocks']} allocated")

    if header.get('directories'):
        dirs = [d for d in header['directories'] if d['name']]
        if dirs:
            print(f"  Directories: {', '.join(d['name'] for d in dirs)}")

    # Scan for records
    records = scan_records(data, version)

    url_count = len(records['url'])
    redr_count = len(records['redr'])
    leak_count = len(records['leak'])
    hash_count = len(records['hash'])
    total_entries = url_count + redr_count + leak_count

    print(f"  Records: {url_count} URL, {redr_count} REDR, {leak_count} LEAK, {hash_count} HASH")

    os.makedirs(output_dir, exist_ok=True)

    # Write header info
    header_path = os.path.join(output_dir, "000000_header.txt")
    with open(header_path, 'w', encoding='utf-8') as f:
        f.write(f"MSIE Cache Index File\n")
        f.write(f"=====================\n")
        f.write(f"Source: {os.path.basename(input_path)}\n")
        f.write(f"Version: {version}\n")
        f.write(f"Signature: {header['signature']}\n")
        f.write(f"File Size: {header['file_size']} bytes\n")
        f.write(f"Hash Table Offset: 0x{header['hash_table_offset']:08X}\n")
        f.write(f"Total Blocks: {header['num_blocks']}\n")
        f.write(f"Allocated Blocks: {header['num_allocated_blocks']}\n")

        if version == '5.2':
            f.write(f"Padding 0x2C: 0x{header.get('padding_2c', 0):08X}\n")
            f.write(f"Cache Limit: {header.get('cache_limit', 0)}\n")
            f.write(f"Exempt Usage: 0x{header.get('exempt_usage', 0):016X}\n")
            f.write(f"Reserved 0x40: 0x{header.get('reserved_40', 0):016X}\n")
            f.write(f"Num Directories: {header.get('num_directories', 0)}\n")
            f.write(f"Reserved 0x4C: 0x{header.get('reserved_4c', 0):08X}\n")
            if header.get('directories'):
                f.write(f"\nDirectory Table:\n")
                for i, d in enumerate(header['directories']):
                    f.write(f"  [{i}] \"{d['name']}\" files={d['file_count']}\n")
            if header.get('bitmap_offset'):
                f.write(f"\nAllocation Bitmap: offset=0x{header['bitmap_offset']:04X} size={header['bitmap_size']} bytes\n")

        elif version == '4.7':
            f.write(f"Field 0x2C: 0x{header.get('field_2c', 0):08X}\n")
            f.write(f"Cache Limit: {header.get('cache_limit', 0)}\n")
            if header.get('inline_hash_entries'):
                f.write(f"\nInline Hash Entries:\n")
                for e in header['inline_hash_entries']:
                    f.write(f"  [{e['index']}] flag=0x{e['flag']:02X} hash={e['hash_high']} data1=0x{e['data1']:08X} data2=0x{e['data2']:08X}\n")

        elif version == '3.2':
            f.write(f"Field 0x24: 0x{header.get('field_24', 0):08X}\n")
            f.write(f"Cache Limit: {header.get('cache_limit', 0)}\n")

        f.write(f"\nRecord Summary:\n")
        f.write(f"  URL records:  {url_count}\n")
        f.write(f"  REDR records: {redr_count}\n")
        f.write(f"  LEAK records: {leak_count}\n")
        f.write(f"  HASH records: {hash_count}\n")
        f.write(f"  Total entries: {total_entries}\n")

    # --all mode: write per-record files with .bin, plus HASH records
    if write_all:
        header_end = header['hash_table_offset'] if header['hash_table_offset'] > 0 else min(len(data), 0x4000)
        header_bin_path = os.path.join(output_dir, "000000_header.bin")
        with open(header_bin_path, 'wb') as f:
            f.write(data[:header_end])

        for i, h in enumerate(records['hash']):
            hash_txt = os.path.join(output_dir, f"000001_hash_{i:03d}.txt")
            with open(hash_txt, 'w', encoding='utf-8') as f:
                f.write(f"HASH Record #{i}\n")
                f.write(f"Offset: 0x{h['offset']:08X}\n")
                f.write(f"Blocks: {h['num_blocks']} ({h['record_size']} bytes)\n")
                f.write(f"Next Hash: 0x{h['next_hash_offset']:08X}\n")
                f.write(f"Entries: {len(h['entries'])} total\n")
                f.write(f"  Occupied: {h['occupied_count']}\n")
                f.write(f"  Free: {h['free_count']}\n")
                f.write(f"  Deleted: {h['deleted_count']}\n")
                f.write(f"\nOccupied Entries:\n")
                for e in h['entries']:
                    if e['status'] == 'occupied':
                        f.write(f"  hash=0x{e['hash_value']:08X} -> record at 0x{e['record_offset']:08X}\n")
                if h['deleted_count'] > 0:
                    f.write(f"\nDeleted Entries:\n")
                    for e in h['entries']:
                        if e['status'] == 'deleted':
                            f.write(f"  -> record at 0x{e['record_offset']:08X}\n")

            hash_bin = os.path.join(output_dir, f"000001_hash_{i:03d}.bin")
            raw_start = h['offset']
            raw_end = raw_start + h['record_size']
            with open(hash_bin, 'wb') as f:
                f.write(data[raw_start:min(raw_end, len(data))])

        all_entries = records['url'] + records['redr'] + records['leak']
        all_entries.sort(key=lambda r: r['offset'])
        for idx, rec in enumerate(all_entries, start=2):
            write_record_file_all(output_dir, idx, rec)

    # Default mode: group records by domain into subdirectories
    # Each domain gets a subdir with URL.txt, REDR.txt, LEAK.txt as needed
    # Records within each file are separated by 3 blank lines
    else:
        # Bucket every entry by (domain, record_type)
        from collections import defaultdict
        domain_buckets = defaultdict(lambda: defaultdict(list))
        for rec in records['url']:
            domain_buckets[extract_domain(rec)]['URL'].append(rec)
        for rec in records['redr']:
            domain_buckets[extract_domain(rec)]['REDR'].append(rec)
        for rec in records['leak']:
            domain_buckets[extract_domain(rec)]['LEAK'].append(rec)

        for domain, type_map in sorted(domain_buckets.items()):
            domain_dir = os.path.join(output_dir, domain)
            os.makedirs(domain_dir, exist_ok=True)
            for rtype, recs in sorted(type_map.items()):
                txt_path = os.path.join(domain_dir, f"{rtype}.txt")
                with open(txt_path, 'w', encoding='utf-8') as f:
                    for i, rec in enumerate(recs):
                        if i > 0:
                            f.write('\n\n\n')
                        f.write(format_record_text(rec))

    # Write header summary (always)
    header_path = os.path.join(output_dir, "header.txt")
    with open(header_path, 'w', encoding='utf-8') as f:
        f.write(f"MSIE Cache Index File\n")
        f.write(f"=====================\n")
        f.write(f"Source: {os.path.basename(input_path)}\n")
        f.write(f"Version: {version}\n")
        f.write(f"Signature: {header['signature']}\n")
        f.write(f"File Size: {header['file_size']} bytes\n")
        f.write(f"Hash Table Offset: 0x{header['hash_table_offset']:08X}\n")
        f.write(f"Total Blocks: {header['num_blocks']}\n")
        f.write(f"Allocated Blocks: {header['num_allocated_blocks']}\n")

        if version == '5.2':
            f.write(f"Padding 0x2C: 0x{header.get('padding_2c', 0):08X}\n")
            f.write(f"Cache Limit: {header.get('cache_limit', 0)}\n")
            f.write(f"Exempt Usage: 0x{header.get('exempt_usage', 0):016X}\n")
            f.write(f"Reserved 0x40: 0x{header.get('reserved_40', 0):016X}\n")
            f.write(f"Num Directories: {header.get('num_directories', 0)}\n")
            f.write(f"Reserved 0x4C: 0x{header.get('reserved_4c', 0):08X}\n")
            if header.get('directories'):
                f.write(f"\nDirectory Table:\n")
                for i, d in enumerate(header['directories']):
                    f.write(f"  [{i}] \"{d['name']}\" files={d['file_count']}\n")
            if header.get('bitmap_offset'):
                f.write(f"\nAllocation Bitmap: offset=0x{header['bitmap_offset']:04X} size={header['bitmap_size']} bytes\n")
        elif version == '4.7':
            f.write(f"Field 0x2C: 0x{header.get('field_2c', 0):08X}\n")
            f.write(f"Cache Limit: {header.get('cache_limit', 0)}\n")
            if header.get('inline_hash_entries'):
                f.write(f"\nInline Hash Entries:\n")
                for e in header['inline_hash_entries']:
                    f.write(f"  [{e['index']}] flag=0x{e['flag']:02X} hash={e['hash_high']} data1=0x{e['data1']:08X} data2=0x{e['data2']:08X}\n")
        elif version == '3.2':
            f.write(f"Field 0x24: 0x{header.get('field_24', 0):08X}\n")
            f.write(f"Cache Limit: {header.get('cache_limit', 0)}\n")

        f.write(f"\nRecord Summary:\n")
        f.write(f"  URL records:  {url_count}\n")
        f.write(f"  REDR records: {redr_count}\n")
        f.write(f"  LEAK records: {leak_count}\n")
        f.write(f"  HASH records: {hash_count}\n")
        f.write(f"  Total entries: {total_entries}\n")

    # Write JSON summary (always)
    json_path = os.path.join(output_dir, "records.json")
    json_data = {
        'source': input_path,
        'version': version,
        'header': {k: v for k, v in header.items() if k != 'directories' or v},
        'record_counts': {
            'url': url_count,
            'redr': redr_count,
            'leak': leak_count,
            'hash': hash_count,
        },
        'url_records': [],
        'redr_records': [],
        'leak_records': [],
    }
    for rec in records['url']:
        json_data['url_records'].append({k: v for k, v in rec.items() if k != 'raw_bytes'})
    for rec in records['redr']:
        json_data['redr_records'].append({k: v for k, v in rec.items() if k != 'raw_bytes'})
    for rec in records['leak']:
        json_data['leak_records'].append({k: v for k, v in rec.items() if k != 'raw_bytes'})
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, default=str)

    print(f"  Output: {output_dir}/")
    return total_entries


def main():
    write_all = False
    args = [a for a in sys.argv[1:] if a != '--all']
    if '--all' in sys.argv[1:]:
        write_all = True

    if len(args) != 2:
        print(f"Usage: {sys.argv[0]} [--all] <inputFile> <outputDir>")
        print()
        print("Extracts all records from a Microsoft Internet Explorer cache")
        print("index file (index.dat) to the specified output directory.")
        print()
        print("By default, extracts .txt files for URL/REDR/LEAK records,")
        print("plus index.txt, records.json, and a header summary.")
        print()
        print("Options:")
        print("  --all  Also extract raw .bin files for every record, the")
        print("         header .bin, and HASH table record files.")
        print()
        print("Supports versions 3.2, 4.7, and 5.2 of the cache format.")
        sys.exit(1)

    input_path = args[0]
    output_dir = args[1]

    if not os.path.isfile(input_path):
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    print(f"Processing: {input_path}")
    total = process_file(input_path, output_dir, write_all=write_all)

    if total is not None:
        print(f"Done. Extracted {total} entries.")
    else:
        print("Failed to process file.")
        sys.exit(1)


if __name__ == '__main__':
    main()

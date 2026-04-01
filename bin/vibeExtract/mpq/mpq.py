#!/usr/bin/env python3
# Vibe coded by Claude

"""
unmpq - Extract all files from a MoPaQ (MPQ) archive.

Usage: unmpq <inputFile> <outputDir>

Uses StormLib (libstorm.so) via ctypes to handle all MPQ format versions (v1-v4),
compression methods (zlib, bzip2, LZMA, PKWARE DCL, Huffman, ADPCM, sparse),
encryption, and sector-based storage.

For truncated archives where StormLib cannot open the file (hash/block tables
are beyond EOF), the tool parses the header and extracts available raw sector
data into a special __raw_data__ directory.
"""

import ctypes
import ctypes.util
import os
import struct
import sys

# ---------------------------------------------------------------------------
# StormLib ctypes bindings
# ---------------------------------------------------------------------------

MAX_PATH = 1024  # Linux MAX_PATH (not Windows 260)

# Stream/open flags
STREAM_FLAG_READ_ONLY   = 0x00000100
MPQ_OPEN_NO_LISTFILE    = 0x00010000
MPQ_OPEN_NO_ATTRIBUTES  = 0x00020000
MPQ_OPEN_FORCE_MPQ_V1   = 0x00080000
MPQ_OPEN_READ_ONLY      = STREAM_FLAG_READ_ONLY

# File flags (TMPQBlock::dwFlags)
MPQ_FILE_IMPLODE        = 0x00000100
MPQ_FILE_COMPRESS       = 0x00000200
MPQ_FILE_ENCRYPTED      = 0x00010000
MPQ_FILE_KEY_V2         = 0x00020000
MPQ_FILE_PATCH_FILE     = 0x00100000
MPQ_FILE_SINGLE_UNIT    = 0x01000000
MPQ_FILE_DELETE_MARKER  = 0x02000000
MPQ_FILE_SECTOR_CRC     = 0x04000000
MPQ_FILE_EXISTS         = 0x80000000

# Error codes
ERROR_SUCCESS           = 0
ERROR_FAKE_MPQ_HEADER   = 10009

# SFileInfoClass enums we use
SFileMpqSectorSize      = 59
SFileMpqNumberOfFiles   = 60


class SFILE_FIND_DATA(ctypes.Structure):
    """Mirrors StormLib's SFILE_FIND_DATA with Linux MAX_PATH=1024."""
    _fields_ = [
        ('cFileName',    ctypes.c_char * MAX_PATH),
        ('szPlainName',  ctypes.c_char_p),
        ('dwHashIndex',  ctypes.c_uint),
        ('dwBlockIndex', ctypes.c_uint),
        ('dwFileSize',   ctypes.c_uint),
        ('dwFileFlags',  ctypes.c_uint),
        ('dwCompSize',   ctypes.c_uint),
        ('dwFileTimeLo', ctypes.c_uint),
        ('dwFileTimeHi', ctypes.c_uint),
        ('lcLocale',     ctypes.c_uint),
    ]


def load_stormlib():
    """Load and configure StormLib function signatures."""
    lib = ctypes.CDLL('libstorm.so')

    # Archive operations
    lib.SFileOpenArchive.restype = ctypes.c_bool
    lib.SFileOpenArchive.argtypes = [
        ctypes.c_char_p, ctypes.c_uint, ctypes.c_uint,
        ctypes.POINTER(ctypes.c_void_p)
    ]
    lib.SFileCloseArchive.restype = ctypes.c_bool
    lib.SFileCloseArchive.argtypes = [ctypes.c_void_p]

    # File search
    lib.SFileFindFirstFile.restype = ctypes.c_void_p
    lib.SFileFindFirstFile.argtypes = [
        ctypes.c_void_p, ctypes.c_char_p,
        ctypes.POINTER(SFILE_FIND_DATA), ctypes.c_char_p
    ]
    lib.SFileFindNextFile.restype = ctypes.c_bool
    lib.SFileFindNextFile.argtypes = [
        ctypes.c_void_p, ctypes.POINTER(SFILE_FIND_DATA)
    ]
    lib.SFileFindClose.restype = ctypes.c_bool
    lib.SFileFindClose.argtypes = [ctypes.c_void_p]

    # File extraction
    lib.SFileExtractFile.restype = ctypes.c_bool
    lib.SFileExtractFile.argtypes = [
        ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint
    ]

    # File open/read/close (for manual extraction)
    lib.SFileOpenFileEx.restype = ctypes.c_bool
    lib.SFileOpenFileEx.argtypes = [
        ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint,
        ctypes.POINTER(ctypes.c_void_p)
    ]
    lib.SFileGetFileSize.restype = ctypes.c_uint
    lib.SFileGetFileSize.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint)]
    lib.SFileReadFile.restype = ctypes.c_bool
    lib.SFileReadFile.argtypes = [
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint,
        ctypes.POINTER(ctypes.c_uint), ctypes.c_void_p
    ]
    lib.SFileCloseFile.restype = ctypes.c_bool
    lib.SFileCloseFile.argtypes = [ctypes.c_void_p]

    # Locale
    lib.SFileSetLocale.restype = ctypes.c_uint  # Returns LCID
    lib.SFileSetLocale.argtypes = [ctypes.c_uint]

    # Info
    lib.SFileGetFileInfo.restype = ctypes.c_bool
    lib.SFileGetFileInfo.argtypes = [
        ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p,
        ctypes.c_uint, ctypes.POINTER(ctypes.c_uint)
    ]

    # Error
    lib.SErrGetLastError.restype = ctypes.c_uint

    return lib


# ---------------------------------------------------------------------------
# MPQ header parsing (for truncated archives and raw dump)
# ---------------------------------------------------------------------------

MPQ_HEADER_V1_SIZE = 0x20
MPQ_HEADER_V2_SIZE = 0x2C
MPQ_HEADER_V3_SIZE = 0x44
MPQ_HEADER_V4_SIZE = 0xD0

MPQ_MAGIC = b'MPQ\x1a'
MPQ_USERDATA_MAGIC = b'MPQ\x1b'


def parse_mpq_header(filepath):
    """Parse MPQ header from a file. Returns dict with header fields."""
    with open(filepath, 'rb') as f:
        filesize = f.seek(0, 2)
        f.seek(0)

        # Check for user data header (MPQ\x1B)
        magic = f.read(4)
        f.seek(0)

        mpq_offset = 0
        userdata = None

        if magic == MPQ_USERDATA_MAGIC:
            ud_data = f.read(16)
            ud_id, ud_size, ud_header_offs, ud_header_size = struct.unpack_from('<IIII', ud_data, 0)
            userdata = {
                'id': ud_id,
                'user_data_size': ud_size,
                'header_offset': ud_header_offs,
                'user_data_header_size': ud_header_size,
            }
            mpq_offset = ud_header_offs
            f.seek(mpq_offset)
            magic = f.read(4)
            f.seek(mpq_offset)

        if magic != MPQ_MAGIC:
            # Search for MPQ\x1A in first 1MB (512-byte aligned)
            f.seek(0)
            search_data = f.read(min(filesize, 1024 * 1024))
            pos = 0
            while pos < len(search_data):
                idx = search_data.find(MPQ_MAGIC, pos)
                if idx == -1:
                    return None
                if idx % 512 == 0:  # MPQ headers are 512-byte aligned
                    mpq_offset = idx
                    break
                pos = idx + 1
            else:
                return None
            f.seek(mpq_offset)

        # Read v1 header (minimum)
        hdr_data = f.read(MPQ_HEADER_V4_SIZE)
        if len(hdr_data) < MPQ_HEADER_V1_SIZE:
            return None

        result = {
            'mpq_offset': mpq_offset,
            'file_size': filesize,
            'userdata': userdata,
        }

        # V1 fields (0x20 bytes)
        (result['magic_raw'],
         result['header_size'],
         result['archive_size'],
         result['format_version'],
         result['sector_size_shift'],
         result['hash_table_offset'],
         result['block_table_offset'],
         result['hash_table_entries'],
         result['block_table_entries']) = struct.unpack_from('<4sIIHHIIII', hdr_data, 0)

        result['sector_size'] = 512 * (2 ** result['sector_size_shift'])
        result['truncated'] = (mpq_offset + result['archive_size']) > filesize

        # V2 fields (0x2C bytes)
        if result['header_size'] >= MPQ_HEADER_V2_SIZE and len(hdr_data) >= MPQ_HEADER_V2_SIZE:
            (result['hi_block_table_offset64'],
             result['hash_table_offset_hi'],
             result['block_table_offset_hi']) = struct.unpack_from('<QHH', hdr_data, 0x20)

            # Compute full 64-bit offsets
            result['hash_table_offset_full'] = (
                result['hash_table_offset'] | (result['hash_table_offset_hi'] << 32)
            )
            result['block_table_offset_full'] = (
                result['block_table_offset'] | (result['block_table_offset_hi'] << 32)
            )

        # V3 fields (0x44 bytes)
        if result['header_size'] >= MPQ_HEADER_V3_SIZE and len(hdr_data) >= MPQ_HEADER_V3_SIZE:
            (result['archive_size_64'],
             result['bet_table_offset_64'],
             result['het_table_offset_64']) = struct.unpack_from('<QQQ', hdr_data, 0x2C)

        # V4 fields (0xD0 bytes)
        if result['header_size'] >= MPQ_HEADER_V4_SIZE and len(hdr_data) >= MPQ_HEADER_V4_SIZE:
            (result['hash_table_size_64'],
             result['block_table_size_64'],
             result['hi_block_table_size_64'],
             result['het_table_size_64'],
             result['bet_table_size_64'],
             result['raw_chunk_size']) = struct.unpack_from('<QQQQQQ', hdr_data, 0x44)
            # Skipping MD5 hashes at 0x7C - 0xD0 (parsed but not needed for extraction)

        return result


def flag_names(flags):
    """Return human-readable flag string."""
    names = []
    if flags & MPQ_FILE_IMPLODE:       names.append('IMPLODE')
    if flags & MPQ_FILE_COMPRESS:      names.append('COMPRESS')
    if flags & MPQ_FILE_ENCRYPTED:     names.append('ENCRYPTED')
    if flags & MPQ_FILE_KEY_V2:        names.append('KEY_V2')
    if flags & MPQ_FILE_PATCH_FILE:    names.append('PATCH')
    if flags & MPQ_FILE_SINGLE_UNIT:   names.append('SINGLE_UNIT')
    if flags & MPQ_FILE_DELETE_MARKER: names.append('DELETE_MARKER')
    if flags & MPQ_FILE_SECTOR_CRC:    names.append('SECTOR_CRC')
    if flags & MPQ_FILE_EXISTS:        names.append('EXISTS')
    return '|'.join(names) if names else 'NONE'


# ---------------------------------------------------------------------------
# Extraction via StormLib
# ---------------------------------------------------------------------------

def extract_with_stormlib(lib, filepath, output_dir):
    """Extract all files from an MPQ archive using StormLib."""
    hMpq = ctypes.c_void_p()
    filepath_b = filepath.encode() if isinstance(filepath, str) else filepath

    if not lib.SFileOpenArchive(filepath_b, 0, MPQ_OPEN_READ_ONLY, ctypes.byref(hMpq)):
        return False, lib.SErrGetLastError()

    os.makedirs(output_dir, exist_ok=True)

    # Enumerate all files
    fd = SFILE_FIND_DATA()
    hFind = lib.SFileFindFirstFile(hMpq, b'*', ctypes.byref(fd), None)

    extracted = 0
    failed = 0
    skipped = 0
    seen_names = set()

    if hFind:
        while True:
            raw_name = fd.cFileName.decode('utf-8', errors='replace')
            flags = fd.dwFileFlags
            file_size = fd.dwFileSize
            comp_size = fd.dwCompSize
            locale = fd.lcLocale

            # Skip delete markers
            if flags & MPQ_FILE_DELETE_MARKER:
                skipped += 1
                if not lib.SFileFindNextFile(hFind, ctypes.byref(fd)):
                    break
                continue

            # Convert backslashes to forward slashes for output path
            safe_name = raw_name.replace('\\', '/')

            # Sanitize: remove leading slashes, collapse double slashes
            while safe_name.startswith('/'):
                safe_name = safe_name[1:]
            while '//' in safe_name:
                safe_name = safe_name.replace('//', '/')

            if not safe_name:
                safe_name = f'__unnamed_{fd.dwBlockIndex}__'

            out_path = os.path.join(output_dir, safe_name)

            # Handle locale variants - append locale suffix for duplicates
            name_key = (safe_name, locale)
            if safe_name in seen_names or (locale != 0 and os.path.exists(out_path)):
                base, ext = os.path.splitext(out_path)
                out_path = f'{base}.locale_{locale}{ext}'
            seen_names.add(safe_name)

            os.makedirs(os.path.dirname(out_path), exist_ok=True)

            raw_name_b = raw_name.encode() if isinstance(raw_name, str) else raw_name
            out_path_b = out_path.encode() if isinstance(out_path, str) else out_path

            # Set locale before extraction so StormLib finds the right entry
            lib.SFileSetLocale(locale)

            if lib.SFileExtractFile(hMpq, raw_name_b, out_path_b, 0):
                extracted += 1
            else:
                err = lib.SErrGetLastError()
                # Try manual read for files that fail extraction
                if try_manual_extract(lib, hMpq, raw_name_b, out_path, file_size):
                    extracted += 1
                else:
                    print(f'  WARNING: Failed to extract: {raw_name} '
                          f'(locale={locale}, error={err})', file=sys.stderr)
                    failed += 1

            if not lib.SFileFindNextFile(hFind, ctypes.byref(fd)):
                break

        lib.SFileFindClose(hFind)

    # Reset locale to default
    lib.SFileSetLocale(0)
    lib.SFileCloseArchive(hMpq)
    return True, (extracted, failed, skipped)


def try_manual_extract(lib, hMpq, name_b, out_path, expected_size):
    """Try to extract a file by opening and reading it manually."""
    hFile = ctypes.c_void_p()
    if not lib.SFileOpenFileEx(hMpq, name_b, 0, ctypes.byref(hFile)):
        return False

    size = lib.SFileGetFileSize(hFile, None)
    if size == 0xFFFFFFFF:
        lib.SFileCloseFile(hFile)
        return False

    buf = ctypes.create_string_buffer(size)
    bytes_read = ctypes.c_uint(0)
    if lib.SFileReadFile(hFile, buf, size, ctypes.byref(bytes_read), None):
        with open(out_path, 'wb') as f:
            f.write(buf.raw[:bytes_read.value])
        lib.SFileCloseFile(hFile)
        return True

    lib.SFileCloseFile(hFile)
    return False


# ---------------------------------------------------------------------------
# Truncated archive handling
# ---------------------------------------------------------------------------

def extract_truncated(filepath, output_dir):
    """Handle truncated MPQ archives where hash/block tables are beyond EOF.

    Extracts raw data sectors that exist within the file boundaries.
    """
    hdr = parse_mpq_header(filepath)
    if hdr is None:
        print(f'  ERROR: Cannot parse MPQ header', file=sys.stderr)
        return False, 'Cannot parse header'

    filesize = hdr['file_size']
    mpq_offset = hdr['mpq_offset']
    header_size = hdr['header_size']
    archive_size = hdr['archive_size']
    ht_offset = hdr['hash_table_offset']
    bt_offset = hdr['block_table_offset']
    ht_entries = hdr['hash_table_entries']
    bt_entries = hdr['block_table_entries']
    sector_size = hdr['sector_size']

    os.makedirs(output_dir, exist_ok=True)

    # Write header info
    info_path = os.path.join(output_dir, '__archive_info__.txt')
    with open(info_path, 'w') as f:
        f.write(f'MPQ Archive (TRUNCATED)\n')
        f.write(f'File size:           {filesize} bytes\n')
        f.write(f'Archive size:        {archive_size} bytes (declared)\n')
        f.write(f'Format version:      {hdr["format_version"]}\n')
        f.write(f'Header size:         0x{header_size:X}\n')
        f.write(f'Sector size:         {sector_size} bytes (2^{hdr["sector_size_shift"]} * 512)\n')
        f.write(f'MPQ offset in file:  0x{mpq_offset:X}\n')
        f.write(f'Hash table offset:   0x{ht_offset:X} ({ht_entries} entries)\n')
        f.write(f'Block table offset:  0x{bt_offset:X} ({bt_entries} entries)\n')
        f.write(f'Hash table in file:  {"YES" if mpq_offset + ht_offset + ht_entries * 16 <= filesize else "NO (beyond EOF)"}\n')
        f.write(f'Block table in file: {"YES" if mpq_offset + bt_offset + bt_entries * 16 <= filesize else "NO (beyond EOF)"}\n')
        f.write(f'\nThis archive is truncated - the declared archive size exceeds the actual\n')
        f.write(f'file size. The hash and/or block tables are located beyond EOF, making\n')
        f.write(f'it impossible to enumerate or properly extract individual files.\n')
        f.write(f'Raw data from the file body has been saved to __raw_data__.\n')

    # Extract raw data (everything after the header until EOF)
    raw_dir = os.path.join(output_dir, '__raw_data__')
    os.makedirs(raw_dir, exist_ok=True)

    data_start = mpq_offset + header_size
    data_available = filesize - data_start

    if data_available > 0:
        with open(filepath, 'rb') as f:
            f.seek(data_start)
            raw_data = f.read(data_available)

        raw_path = os.path.join(raw_dir, 'file_data.bin')
        with open(raw_path, 'wb') as f:
            f.write(raw_data)

    return True, f'Truncated archive: {data_available} bytes of raw data saved'


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) != 3:
        print(f'Usage: {sys.argv[0]} <inputFile> <outputDir>', file=sys.stderr)
        sys.exit(1)

    input_file = os.path.abspath(sys.argv[1])
    output_dir = os.path.abspath(sys.argv[2])

    if not os.path.isfile(input_file):
        print(f'Error: Input file not found: {input_file}', file=sys.stderr)
        sys.exit(1)

    # Parse header for display
    hdr = parse_mpq_header(input_file)
    if hdr is None:
        print(f'Error: Not a valid MPQ file: {input_file}', file=sys.stderr)
        sys.exit(1)

    filesize = os.path.getsize(input_file)
    fmt_ver = hdr['format_version']
    hdr_size = hdr['header_size']

    print(f'MPQ Archive: {os.path.basename(input_file)}')
    print(f'  File size:      {filesize:,} bytes')
    print(f'  Format version: {fmt_ver} (header size: 0x{hdr_size:X})')
    print(f'  Archive size:   {hdr["archive_size"]:,} bytes')
    print(f'  Sector size:    {hdr["sector_size"]:,} bytes')
    print(f'  Hash table:     {hdr["hash_table_entries"]} entries @ offset 0x{hdr["hash_table_offset"]:X}')
    print(f'  Block table:    {hdr["block_table_entries"]} entries @ offset 0x{hdr["block_table_offset"]:X}')

    # Check for trailing data after the archive
    trailing_bytes = filesize - (hdr['mpq_offset'] + hdr['archive_size'])
    if trailing_bytes > 0:
        print(f'  Trailing data:  {trailing_bytes} bytes after archive')
        with open(input_file, 'rb') as f:
            f.seek(hdr['mpq_offset'] + hdr['archive_size'])
            trail_marker = f.read(4)
        if trail_marker == b'NGIS':
            print(f'                  Weak digital signature (NGIS, 256-byte RSA)')
        elif trail_marker == b'NIKS':
            print(f'                  SKIN marker (Blizzard downloader checksum)')

    if hdr['truncated']:
        print(f'  STATUS:         TRUNCATED (archive extends beyond file)')
        print(f'  Attempting raw data extraction...')
        ok, msg = extract_truncated(input_file, output_dir)
        if ok:
            print(f'  {msg}')
        else:
            print(f'  Error: {msg}', file=sys.stderr)
            sys.exit(1)
        sys.exit(0)

    # Try extraction with StormLib
    lib = load_stormlib()
    print(f'  Extracting files...')

    ok, result = extract_with_stormlib(lib, input_file, output_dir)
    if not ok:
        err_code = result
        print(f'  StormLib error: {err_code}', file=sys.stderr)
        sys.exit(1)

    extracted, failed, skipped = result
    print(f'  Extracted:  {extracted} files')
    if failed > 0:
        print(f'  Failed:     {failed} files')
    if skipped > 0:
        print(f'  Skipped:    {skipped} files (delete markers)')
    print(f'  Done.')


if __name__ == '__main__':
    main()

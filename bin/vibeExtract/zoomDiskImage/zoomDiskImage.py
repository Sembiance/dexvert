#!/usr/bin/env python3
# Vibe coded by Claude

"""
unZoomDiskImage.py - Extract Amiga ZOOM disk image (.zom) files to raw ADF disk images.

Supports both ZOOM (versions 3-4) and ZOM5 (version 5) formats.

Usage: unZoomDiskImage.py <inputFile> <outputDir>

The output directory will contain:
  - <basename>.adf : The raw Amiga disk image (901120 bytes for standard DD)
  - <basename>.txt : Attached text data (if present in the archive)
"""

import struct
import sys
import os

# ============================================================================
# Constants
# ============================================================================

MAGIC_ZOOM = b'ZOOM'
MAGIC_ZOM5 = b'ZOM5'

HEADER_SIZE = 72
BOXSIZE = 5
TRACK_HEADER_SIZE = 38  # On-disk (5 tracks + 1 pad + 20 bits + 12 fields)
TRACKSIZE = 512 * 11 * 2  # 11264 bytes per cylinder
SECTORS_PER_CYL = 22
SECTOR_SIZE = 512
LABEL_SIZE = 16
NUM_CYLINDERS = 80
FLAG_USEHEADER = 1

# LH constants
SEQ_MAX = 60
ANZ_CHAR = 256 + SEQ_MAX + 1   # 317
SIZE_TABLE = ANZ_CHAR * 2 - 1  # 633
ROOT = SIZE_TABLE - 1           # 632
FREQ_LIMIT = 0x8000

D_CODE_LEN = [
    0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,
    0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,
    0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,
    0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,
    0x0101,0x0101,0x0101,0x0101,0x0101,0x0101,0x0101,0x0101,
    0x0101,0x0101,0x0101,0x0101,0x0101,0x0101,0x0101,0x0101,
    0x0201,0x0201,0x0201,0x0201,0x0201,0x0201,0x0201,0x0201,
    0x0201,0x0201,0x0201,0x0201,0x0201,0x0201,0x0201,0x0201,
    0x0301,0x0301,0x0301,0x0301,0x0301,0x0301,0x0301,0x0301,
    0x0301,0x0301,0x0301,0x0301,0x0301,0x0301,0x0301,0x0301,
    0x0402,0x0402,0x0402,0x0402,0x0402,0x0402,0x0402,0x0402,
    0x0502,0x0502,0x0502,0x0502,0x0502,0x0502,0x0502,0x0502,
    0x0602,0x0602,0x0602,0x0602,0x0602,0x0602,0x0602,0x0602,
    0x0702,0x0702,0x0702,0x0702,0x0702,0x0702,0x0702,0x0702,
    0x0802,0x0802,0x0802,0x0802,0x0802,0x0802,0x0802,0x0802,
    0x0902,0x0902,0x0902,0x0902,0x0902,0x0902,0x0902,0x0902,
    0x0A02,0x0A02,0x0A02,0x0A02,0x0A02,0x0A02,0x0A02,0x0A02,
    0x0B02,0x0B02,0x0B02,0x0B02,0x0B02,0x0B02,0x0B02,0x0B02,
    0x0C03,0x0C03,0x0C03,0x0C03,0x0D03,0x0D03,0x0D03,0x0D03,
    0x0E03,0x0E03,0x0E03,0x0E03,0x0F03,0x0F03,0x0F03,0x0F03,
    0x1003,0x1003,0x1003,0x1003,0x1103,0x1103,0x1103,0x1103,
    0x1203,0x1203,0x1203,0x1203,0x1303,0x1303,0x1303,0x1303,
    0x1403,0x1403,0x1403,0x1403,0x1503,0x1503,0x1503,0x1503,
    0x1603,0x1603,0x1603,0x1603,0x1703,0x1703,0x1703,0x1703,
    0x1804,0x1804,0x1904,0x1904,0x1A04,0x1A04,0x1B04,0x1B04,
    0x1C04,0x1C04,0x1D04,0x1D04,0x1E04,0x1E04,0x1F04,0x1F04,
    0x2004,0x2004,0x2104,0x2104,0x2204,0x2204,0x2304,0x2304,
    0x2404,0x2404,0x2504,0x2504,0x2604,0x2604,0x2704,0x2704,
    0x2804,0x2804,0x2904,0x2904,0x2A04,0x2A04,0x2B04,0x2B04,
    0x2C04,0x2C04,0x2D04,0x2D04,0x2E04,0x2E04,0x2F04,0x2F04,
    0x3005,0x3105,0x3205,0x3305,0x3405,0x3505,0x3605,0x3705,
    0x3805,0x3905,0x3A05,0x3B05,0x3C05,0x3D05,0x3E05,0x3F05,
]

# ============================================================================
# CRC functions
# ============================================================================

_crc32_table = []
for _i in range(256):
    _c = _i
    for _ in range(8):
        _c = (_c >> 1) ^ 0xEDB88320 if _c & 1 else _c >> 1
    _crc32_table.append(_c)


def xad_crc32(data):
    crc = 0
    for b in data:
        crc = _crc32_table[(crc ^ b) & 0xFF] ^ (crc >> 8)
    return crc & 0xFFFFFFFF


_crc16_table = [
    0x0000,0x1021,0x2042,0x3063,0x4084,0x50A5,0x60C6,0x70E7,
    0x8108,0x9129,0xA14A,0xB16B,0xC18C,0xD1AD,0xE1CE,0xF1EF,
    0x1231,0x0210,0x3273,0x2252,0x52B5,0x4294,0x72F7,0x62D6,
    0x9339,0x8318,0xB37B,0xA35A,0xD3BD,0xC39C,0xF3FF,0xE3DE,
    0x2462,0x3443,0x0420,0x1401,0x64E6,0x74C7,0x44A4,0x5485,
    0xA56A,0xB54B,0x8528,0x9509,0xE5EE,0xF5CF,0xC5AC,0xD58D,
    0x3653,0x2672,0x1611,0x0630,0x76D7,0x66F6,0x5695,0x46B4,
    0xB75B,0xA77A,0x9719,0x8738,0xF7DF,0xE7FE,0xD79D,0xC7BC,
    0x48C4,0x58E5,0x6886,0x78A7,0x0840,0x1861,0x2802,0x3823,
    0xC9CC,0xD9ED,0xE98E,0xF9AF,0x8948,0x9969,0xA90A,0xB92B,
    0x5AF5,0x4AD4,0x7AB7,0x6A96,0x1A71,0x0A50,0x3A33,0x2A12,
    0xDBFD,0xCBDC,0xFBBF,0xEB9E,0x9B79,0x8B58,0xBB3B,0xAB1A,
    0x6CA6,0x7C87,0x4CE4,0x5CC5,0x2C22,0x3C03,0x0C60,0x1C41,
    0xEDAE,0xFD8F,0xCDEC,0xDDCD,0xAD2A,0xBD0B,0x8D68,0x9D49,
    0x7E97,0x6EB6,0x5ED5,0x4EF4,0x3E13,0x2E32,0x1E51,0x0E70,
    0xFF9F,0xEFBE,0xDFDD,0xCFFC,0xBF1B,0xAF3A,0x9F59,0x8F78,
    0x9188,0x81A9,0xB1CA,0xA1EB,0xD10C,0xC12D,0xF14E,0xE16F,
    0x1080,0x00A1,0x30C2,0x20E3,0x5004,0x4025,0x7046,0x6067,
    0x83B9,0x9398,0xA3FB,0xB3DA,0xC33D,0xD31C,0xE37F,0xF35E,
    0x02B1,0x1290,0x22F3,0x32D2,0x4235,0x5214,0x6277,0x7256,
    0xB5EA,0xA5CB,0x95A8,0x8589,0xF56E,0xE54F,0xD52C,0xC50D,
    0x34E2,0x24C3,0x14A0,0x0481,0x7466,0x6447,0x5424,0x4405,
    0xA7DB,0xB7FA,0x8799,0x97B8,0xE75F,0xF77E,0xC71D,0xD73C,
    0x26D3,0x36F2,0x0691,0x16B0,0x6657,0x7676,0x4615,0x5634,
    0xD94C,0xC96D,0xF90E,0xE92F,0x99C8,0x89E9,0xB98A,0xA9AB,
    0x5844,0x4865,0x7806,0x6827,0x18C0,0x08E1,0x3882,0x28A3,
    0xCB7D,0xDB5C,0xEB3F,0xFB1E,0x8BF9,0x9BD8,0xABBB,0xBB9A,
    0x4A75,0x5A54,0x6A37,0x7A16,0x0AF1,0x1AD0,0x2AB3,0x3A92,
    0xFD2E,0xED0F,0xDD6C,0xCD4D,0xBDAA,0xAD8B,0x9DE8,0x8DC9,
    0x7C26,0x6C07,0x5C64,0x4C45,0x3CA2,0x2C83,0x1CE0,0x0CC1,
    0xEF1F,0xFF3E,0xCF5D,0xDF7C,0xAF9B,0xBFBA,0x8FD9,0x9FF8,
    0x6E17,0x7E36,0x4E55,0x5E74,0x2E93,0x3EB2,0x0ED1,0x1EF0,
]


def crc_1021_2(data):
    crc = 0
    for b in data:
        crc = (_crc16_table[(crc >> 8) & 0xFF] ^ ((crc << 8) ^ b)) & 0xFFFF
    return crc


# ============================================================================
# LH Decompression (Adaptive Huffman + LZSS)
# Faithful translation of xadmaster Zoom.c LhDecode using 32-bit bitbuf.
# ============================================================================

def lh_decode(src_bytes, dest_size):
    words = []
    for off in range(0, len(src_bytes), 2):
        if off + 1 < len(src_bytes):
            words.append((src_bytes[off] << 8) | src_bytes[off + 1])
        else:
            words.append(src_bytes[off] << 8)

    src_idx = [0]

    def next_word():
        if src_idx[0] < len(words):
            w = words[src_idx[0]]
            src_idx[0] += 1
            return w
        return 0

    freq = [0] * (SIZE_TABLE + 1)
    parent = [0] * SIZE_TABLE
    son = [0] * SIZE_TABLE
    par_back = [0] * ANZ_CHAR

    k = 0
    j = -1
    for i in range(ANZ_CHAR):
        freq[i] = 1
        son[i] = j
        par_back[-j - 1] = k
        j -= 1
        k += 1
    k = 0
    j = ANZ_CHAR
    for i in range(ROOT - ANZ_CHAR + 1):
        freq[j] = freq[k] + freq[k + 1]
        son[j] = k
        parent[k] = j
        parent[k + 1] = j
        j += 1
        k += 2
    freq[SIZE_TABLE] = 0xFFFF
    parent[ROOT] = 0

    def update(pos):
        """C code uses do { ... } while(i); -- must execute at least once."""
        i = par_back[-pos - 1] if pos < 0 else parent[pos]
        while True:
            j = freq[i] + 1
            freq[i] = j
            if freq[i + 1] < j:
                scan = i + 2
                while freq[scan] < j:
                    scan += 1
                scan -= 1
                k = scan
                freq[i] = freq[k]
                freq[k] = j
                si = son[i]
                sk = son[k]
                if si >= 0:
                    parent[si + 1] = k
                    parent[si] = k
                else:
                    par_back[-si - 1] = k
                if sk >= 0:
                    parent[sk + 1] = i
                    parent[sk] = i
                else:
                    par_back[-sk - 1] = i
                son[k] = si
                son[i] = sk
                i = parent[k]
            else:
                i = parent[i]
            if i == 0:
                break

    dest = bytearray(dest_size)
    dest_pos = 0
    # 32-bit bitbuf exactly matching the C uint32_t
    bitindex = 15
    bitbuf = next_word()

    while dest_pos < dest_size:
        l = son[ROOT]
        while l >= 0:
            l = son[l + (1 if (bitbuf & 0x8000) else 0)]
            bitbuf = (bitbuf << 1) & 0xFFFFFFFF
            bitindex -= 1
            if bitindex < 0:
                bitindex = 15
                bitbuf = next_word()

        if freq[ROOT] != FREQ_LIMIT:
            update(l)

        if l >= -256:
            dest[dest_pos] = (-l - 1) & 0xFF
            dest_pos += 1
        elif l <= -(255 + SEQ_MAX + 1) - 1:
            break
        else:
            match_len = -(l + 256)
            bitindex -= 7
            if bitindex < 0:
                neg = -bitindex
                bitbuf = ((bitbuf << 8) | (next_word() << neg)) & 0xFFFFFFFF
                bitindex += 15
                i_val = (bitbuf >> 16) & 0xFF
            else:
                i_val = (bitbuf >> 8) & 0xFF
                bitbuf = (bitbuf << 8) & 0xFFFFFFFF
                bitindex -= 1
                if bitindex < 0:
                    bitindex = 15
                    bitbuf = next_word()

            entry = D_CODE_LEN[i_val]
            j_extra = entry & 0xFF
            k_code = (entry & 0xFF00) >> 2

            jj = j_extra
            while True:
                i_val = (i_val << 1) & 0xFFFF
                if bitbuf & 0x8000:
                    i_val |= 1
                bitbuf = (bitbuf << 1) & 0xFFFFFFFF
                bitindex -= 1
                if bitindex < 0:
                    bitindex = 15
                    bitbuf = next_word()
                if jj == 0:
                    break
                jj -= 1

            distance = (i_val & 0x3F) | k_code
            src_pos = dest_pos - distance
            for _ in range(match_len):
                if 0 <= src_pos < dest_size:
                    dest[dest_pos] = dest[src_pos]
                dest_pos += 1
                src_pos += 1

    return bytes(dest[:dest_pos])


# ============================================================================
# RLE Decompression
# ============================================================================

def run_decode_new(src, expected_size):
    if len(src) < 4:
        raise ValueError("RLE source too short")
    out_size = (src[0] << 16) | (src[1] << 8) | src[2]
    pack_byte = src[3]
    dest = bytearray(out_size)
    si = 4
    di = 0
    while di < out_size and si < len(src):
        b = src[si]; si += 1
        if b == pack_byte:
            if si >= len(src):
                break
            count = src[si]; si += 1
            if count == 0:
                dest[di] = pack_byte; di += 1
            else:
                if si >= len(src):
                    break
                fill = src[si]; si += 1
                for _ in range(count + 1):
                    if di < out_size:
                        dest[di] = fill; di += 1
        else:
            dest[di] = b; di += 1
    return bytes(dest[:di])


def run_decode_old(src, dest_size, src_size, rle_bytes):
    b1 = (rle_bytes >> 8) & 0xFF
    b2 = rle_bytes & 0xFF
    dest = bytearray(dest_size)
    si = src_size - 1
    di = dest_size - 1
    while di >= 0 and si >= 0:
        b = src[si]; si -= 1
        if b == b1:
            if si < 0:
                break
            cnt = src[si]; si -= 1
            if cnt == 0:
                cnt = 0x100
            if si < 0:
                break
            fill = src[si]; si -= 1
            for _ in range(cnt):
                if di >= 0:
                    dest[di] = fill; di -= 1
        elif b == b2:
            if si < 0:
                break
            cnt = src[si]; si -= 1
            if cnt == 0:
                cnt = 0x100
            for _ in range(cnt):
                if di >= 0:
                    dest[di] = 0; di -= 1
        else:
            dest[di] = b; di -= 1
    return bytes(dest)


# ============================================================================
# Track unpacking
# ============================================================================

def count_sectors(bits_array, tracks):
    total = 0
    for i in range(BOXSIZE):
        if tracks[i] == -1:
            break
        for k in range(SECTORS_PER_CYL):
            if bits_array[i] & (1 << k):
                total += 1
    return total


def unpack_track(bits_array, tracks, buf, pos, use_header):
    sector_bytes = (SECTOR_SIZE + LABEL_SIZE) if use_header else SECTOR_SIZE
    j = 0
    for i in range(pos):
        if tracks[i] == -1:
            break
        for k in range(SECTORS_PER_CYL):
            if bits_array[i] & (1 << k):
                j += 1
    buf_offset = j * sector_bytes
    result = bytearray(TRACKSIZE)
    bits = bits_array[pos]
    sector_idx = 0
    for i in range(SECTORS_PER_CYL):
        if bits & (1 << i):
            src_off = buf_offset + sector_idx * sector_bytes
            end = src_off + SECTOR_SIZE
            if end <= len(buf):
                result[i * SECTOR_SIZE:(i + 1) * SECTOR_SIZE] = buf[src_off:end]
            sector_idx += 1
    return bytes(result)


# ============================================================================
# Main extraction
# ============================================================================

def parse_header(data):
    if len(data) < HEADER_SIZE:
        raise ValueError("File too short for header")
    magic = data[0:4]
    if magic not in (MAGIC_ZOOM, MAGIC_ZOM5):
        raise ValueError(f"Invalid magic: {magic!r}")
    hdr = {
        'magic': magic,
        'is_old': (magic == MAGIC_ZOOM),
        'from_track': struct.unpack_from('>b', data, 4)[0],
        'to_track': struct.unpack_from('>b', data, 5)[0],
        'version': data[6],
        'only_tracks': data[7],
        'flags': struct.unpack_from('>I', data, 8)[0],
        'date_bytes': data[12:24],
        'text_length': struct.unpack_from('>I', data, 24)[0],
        'packed_length': struct.unpack_from('>I', data, 28)[0],
        'note_offset': struct.unpack_from('>i', data, 32)[0],
        'encrypted': data[36],
        'format': data[37],
        'root': struct.unpack_from('>I', data, 40)[0],
    }
    hdr['use_header'] = bool(hdr['flags'] & FLAG_USEHEADER)
    return hdr


def verify_header_crc(data, is_old):
    hdr_bytes = data[0:HEADER_SIZE]
    if is_old:
        stored = struct.unpack_from('>H', data, HEADER_SIZE)[0]
        if stored != crc_1021_2(hdr_bytes):
            raise ValueError("Header CRC16 mismatch")
        return HEADER_SIZE + 2
    else:
        stored = struct.unpack_from('>I', data, HEADER_SIZE)[0]
        if stored != xad_crc32(hdr_bytes):
            raise ValueError("Header CRC32 mismatch")
        return HEADER_SIZE + 4


def read_track_header(data, offset, is_old):
    th_bytes = data[offset:offset + TRACK_HEADER_SIZE]
    if is_old:
        stored = struct.unpack_from('>H', data, offset + TRACK_HEADER_SIZE)[0]
        if stored != crc_1021_2(th_bytes):
            raise ValueError(f"Track header CRC mismatch at offset {offset}")
        crc_size = 2
    else:
        stored = struct.unpack_from('>I', data, offset + TRACK_HEADER_SIZE)[0]
        if stored != xad_crc32(th_bytes):
            raise ValueError(f"Track header CRC mismatch at offset {offset}")
        crc_size = 4

    th = {}
    th['tracks'] = list(struct.unpack_from('>5b', data, offset))
    th['bits'] = list(struct.unpack_from('>5I', data, offset + 6))
    th['length'] = struct.unpack_from('>H', data, offset + 26)[0]

    if is_old:
        th['rle_bytes'] = struct.unpack_from('>H', data, offset + 28)[0]
        th['squeezed_length'] = struct.unpack_from('>H', data, offset + 30)[0]
        packed_crc = struct.unpack_from('>I', data, offset + 34)[0]
        th['packed'] = (packed_crc >> 16) & 0xFFFF
        th['data_crc'] = packed_crc & 0xFFFF
    else:
        th['squeezed_length'] = struct.unpack_from('>H', data, offset + 28)[0]
        th['packed'] = struct.unpack_from('>H', data, offset + 32)[0]
        th['data_crc'] = struct.unpack_from('>I', data, offset + 34)[0]
        th['rle_bytes'] = 0

    return th, offset + TRACK_HEADER_SIZE + crc_size


def decompress_box(data, offset, th, is_old, use_header):
    comp_data = data[offset:offset + th['length']]

    # Verify data CRC
    if is_old:
        if crc_1021_2(comp_data) != th['data_crc']:
            print(f"  WARNING: Data CRC16 mismatch, data may be corrupted", file=sys.stderr)
    else:
        if xad_crc32(comp_data) != th['data_crc']:
            print(f"  WARNING: Data CRC32 mismatch, data may be corrupted", file=sys.stderr)

    total_sectors = count_sectors(th['bits'], th['tracks'])
    sector_bytes = (SECTOR_SIZE + LABEL_SIZE) if use_header else SECTOR_SIZE
    fat_length = total_sectors * sector_bytes

    result = comp_data

    if th['packed']:
        lh_size = th['squeezed_length'] if th['squeezed_length'] else fat_length
        result = lh_decode(result, lh_size)

    if th['squeezed_length']:
        if is_old:
            result = run_decode_old(result, fat_length, th['squeezed_length'], th['rle_bytes'])
        else:
            result = run_decode_new(result, fat_length)

    return result, offset + th['length']


def extract_zoom(input_path, output_dir):
    with open(input_path, 'rb') as f:
        data = f.read()

    basename = os.path.splitext(os.path.basename(input_path))[0]
    os.makedirs(output_dir, exist_ok=True)

    hdr = parse_header(data)
    offset = verify_header_crc(data, hdr['is_old'])

    fmt_name = "ZOOM" if hdr['is_old'] else "ZOM5"
    print(f"Format: {fmt_name} v{hdr['version']}")
    print(f"Tracks: {hdr['from_track']} to {hdr['to_track']} "
          f"({hdr['to_track'] - hdr['from_track'] + 1} cylinders)")
    if hdr['use_header']:
        print("Sector labels: present")
    if hdr['encrypted']:
        raise ValueError("Encrypted archives are not supported")

    # Date
    days, minutes, ticks = struct.unpack('>III', hdr['date_bytes'])
    if days or minutes or ticks:
        import datetime
        try:
            base = datetime.datetime(1978, 1, 1)
            dt = base + datetime.timedelta(days=days, minutes=minutes, seconds=ticks // 50)
            print(f"Date: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
        except (ValueError, OverflowError):
            pass

    # Text data
    if hdr['text_length'] > 0:
        print(f"Attached text: {hdr['text_length']} bytes (packed: {hdr['packed_length']})")
        text_comp = data[offset:offset + hdr['packed_length']]
        offset += hdr['packed_length']
        if hdr['is_old']:
            offset += 2  # CRC16
        else:
            offset += 4  # CRC32
        try:
            text_data = lh_decode(text_comp, hdr['text_length'])
            text_path = os.path.join(output_dir, basename + '.txt')
            with open(text_path, 'wb') as f:
                f.write(text_data)
            print(f"  Saved text to: {text_path}")
        except Exception as e:
            print(f"  WARNING: Failed to decompress text: {e}", file=sys.stderr)

    # Note
    if hdr['note_offset']:
        note_off = hdr['note_offset']
        if note_off + 92 <= len(data):
            note_data = data[note_off:note_off + 92]
            note_text = bytearray(note_data[12:92])
            root = struct.unpack('>I', note_data[8:12])[0]
            mult = struct.unpack('>I', note_data[4:8])[0]
            add = struct.unpack('>I', note_data[0:4])[0]
            for ni in range(80):
                root = ((root * mult) & 0xFFFFFF + add) & 0xFFFFFF
                note_text[ni] ^= root % 256
            note_path = os.path.join(output_dir, basename + '.note.txt')
            with open(note_path, 'wb') as f:
                f.write(bytes(note_text).rstrip(b'\x00'))
            print(f"  Saved note to: {note_path}")

    # Extract disk image
    disk = bytearray(NUM_CYLINDERS * TRACKSIZE)
    current_cyl = hdr['from_track']
    box_buf = None
    box_th = None
    box_idx = -1

    while current_cyl <= hdr['to_track']:
        if box_idx < 0:
            if offset >= len(data) - 10:
                break
            try:
                th, data_offset = read_track_header(data, offset, hdr['is_old'])
            except ValueError as e:
                print(f"  WARNING: {e}, filling rest with zeros", file=sys.stderr)
                break
            box_th = th
            box_idx = 0
            try:
                box_buf, next_offset = decompress_box(
                    data, data_offset, th, hdr['is_old'], hdr['use_header'])
            except Exception as e:
                print(f"  WARNING: Decompression failed at cyl {current_cyl}: {e}",
                      file=sys.stderr)
                next_offset = data_offset + th['length']
                box_buf = None
            offset = next_offset

        if box_idx >= BOXSIZE or box_th['tracks'][box_idx] == -1:
            current_cyl += 1
            continue

        if box_th['tracks'][box_idx] > current_cyl:
            current_cyl += 1
            continue

        if box_th['tracks'][box_idx] == current_cyl:
            if box_buf is not None:
                try:
                    track_data = unpack_track(
                        box_th['bits'], box_th['tracks'], box_buf,
                        box_idx, hdr['use_header'])
                    disk_off = current_cyl * TRACKSIZE
                    disk[disk_off:disk_off + TRACKSIZE] = track_data
                except Exception as e:
                    print(f"  WARNING: Failed to unpack cyl {current_cyl}: {e}",
                          file=sys.stderr)
            current_cyl += 1
        elif box_th['tracks'][box_idx] < current_cyl:
            pass  # skip

        box_idx += 1
        if box_idx >= BOXSIZE:
            box_idx = -1
            box_buf = None

    adf_path = os.path.join(output_dir, basename + '.adf')
    with open(adf_path, 'wb') as f:
        f.write(bytes(disk))
    print(f"Disk image: {adf_path} ({len(disk)} bytes)")
    print(f"Input: {len(data)} bytes, final offset: {offset} / {len(data)} "
          f"({'OK' if offset == len(data) else f'{len(data) - offset} remaining'})")


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>", file=sys.stderr)
        sys.exit(1)
    input_path = sys.argv[1]
    output_dir = sys.argv[2]
    if not os.path.isfile(input_path):
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    try:
        extract_zoom(input_path, output_dir)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# Vibe coded by Claude

"""
ensoniq2wav.py - Convert Ensoniq Disk Image files to WAV files.

Supports GKH (Goh King Wah), EDE (Giebler EPS DD), EDA (Giebler ASR HD),
EDT (Giebler TS DD/HD), and EDV (Giebler VFX) disk image formats.

Extracts instrument audio data from EPS, EPS-16 Plus, and ASR-10 disk images
and writes each instrument as a 16-bit signed PCM WAV file.

Usage: python3 ensoniq2wav.py <inputFile> <outputDir>
"""

import sys
import os
import struct


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BLOCK_SIZE = 512
MAX_DIR_ENTRIES = 39
DIR_ENTRY_SIZE = 26
FAT_ENTRIES_PER_BLOCK = 170
FAT_ENTRY_SIZE = 3
FAT_START_BLOCK = 5
ROOT_DIR_BLOCK = 3

# File types from directory entries
FILE_TYPE_EMPTY = 0x00
FILE_TYPE_OS = 0x01
FILE_TYPE_DIRECTORY = 0x02
FILE_TYPE_EPS_INSTRUMENT = 0x03
FILE_TYPE_EPS_BANK = 0x04
FILE_TYPE_EPS_SEQUENCE = 0x05
FILE_TYPE_EPS_SONG = 0x06
FILE_TYPE_EPS_SYSEX = 0x07
FILE_TYPE_PARENT_DIR = 0x08
FILE_TYPE_EPS_MACRO = 0x09
FILE_TYPE_EPS16_BANK = 0x17
FILE_TYPE_EPS16_EFFECT = 0x18
FILE_TYPE_EPS16_SEQUENCE = 0x19
FILE_TYPE_EPS16_SONG = 0x1A
FILE_TYPE_EPS16_OS = 0x1B
FILE_TYPE_ASR_SONG = 0x1D
FILE_TYPE_ASR_BANK = 0x1E
FILE_TYPE_ASR_AUDIOTRACK = 0x1F

# Instrument file types that contain audio
INSTRUMENT_TYPES = {FILE_TYPE_EPS_INSTRUMENT}

# Disk types (from byte 0x1FF of Giebler header)
GIEBLER_EDE_DD = 0x03  # EPS double density
GIEBLER_EDT_DD = 0x07  # TS double density
GIEBLER_EDA_HD = 0xCB  # ASR high density
GIEBLER_EDT_HD = 0xCC  # TS high density

# Disk sizes
EPS_DD_BLOCKS = 1600   # 80 tracks * 2 heads * 10 sectors
ASR_HD_BLOCKS = 3200   # 80 tracks * 2 heads * 20 sectors

# Machine type detection from instrument header
MACHINE_EPS = "EPS"
MACHINE_EPS16 = "EPS-16 Plus"
MACHINE_ASR = "ASR-10"

# Default sample rates per machine type (Hz)
DEFAULT_SAMPLE_RATES = {
    MACHINE_EPS: 30000,
    MACHINE_EPS16: 44100,
    MACHINE_ASR: 44100,
}

# EPS-16 Plus sample rate table (index -> Hz)
EPS16_SAMPLE_RATES = {
    0: 44100,
    1: 33000,
    2: 30000,
    3: 27000,
    4: 22050,
    5: 15200,
    6: 11200,
}


# ---------------------------------------------------------------------------
# Disk Image Loading
# ---------------------------------------------------------------------------

def identify_image_format(data):
    """Identify the disk image format and return (format, data_offset, disk_data)."""
    if len(data) < 512:
        raise ValueError("File too small to be a valid disk image")

    # Check for GKH format: starts with "TDDFI"
    if data[0:5] == b'TDDFI':
        return load_gkh(data)

    # Check for Giebler format: starts with 0x0D 0x0A
    if data[0] == 0x0D and data[1] == 0x0A:
        return load_giebler(data)

    # Try as raw image
    if len(data) == EPS_DD_BLOCKS * BLOCK_SIZE:
        return "RAW-DD", 0, data
    if len(data) == ASR_HD_BLOCKS * BLOCK_SIZE:
        return "RAW-HD", 0, data

    raise ValueError("Unrecognized disk image format")


def load_gkh(data):
    """Load a GKH (Goh King Wah / TDDFI) format disk image.

    GKH Header Structure:
      Bytes 0-4:   Magic "TDDFI"
      Byte  5:     Unknown
      Bytes 6-7:   Number of tags (16-bit little-endian)
      Bytes 8+:    Tags, each 10 bytes:
        Bytes 0-1:  Tag type
        Bytes 2-9:  Tag data

    Tag types:
      (0x01, 0x04): Format/version info
      (0x0A, 0x05): Disk geometry (tracks, heads, sectors, bytes/sector)
      (0x0B, 0x0B): Image data location (contains data offset)
      (0x14, 0x0A): Unknown
      (0x15, 0x0A): Unknown

    After the header, raw disk data follows as contiguous 512-byte blocks.
    """
    num_tags = data[6] | (data[7] << 8)
    data_offset = 8 + num_tags * 10  # default: right after tags

    num_blocks = EPS_DD_BLOCKS  # default
    tags = []

    for i in range(num_tags):
        tag_base = 8 + i * 10
        tag_type = (data[tag_base], data[tag_base + 1])
        tag_data = data[tag_base:tag_base + 10]
        tags.append((tag_type, tag_data))

        if tag_type == (0x0B, 0x0B):
            # Image location tag: offset at bytes 6-9 (little-endian 32-bit)
            data_offset = (data[tag_base + 6] | (data[tag_base + 7] << 8) |
                           (data[tag_base + 8] << 16) | (data[tag_base + 9] << 24))

        elif tag_type == (0x0A, 0x05):
            # Disk geometry tag
            tracks = data[tag_base + 2] | (data[tag_base + 3] << 8)
            heads = data[tag_base + 4] | (data[tag_base + 5] << 8)
            sectors = data[tag_base + 6] | (data[tag_base + 7] << 8)
            num_blocks = tracks * heads * sectors

    disk_data = data[data_offset:data_offset + num_blocks * BLOCK_SIZE]
    return "GKH", data_offset, disk_data


def load_giebler(data):
    """Load a Giebler format disk image (EDE, EDA, EDT, EDV).

    Giebler Header Structure (512 bytes):
      Bytes 0x00-0x01:  0x0D 0x0A (CR LF)
      Bytes 0x02-0x4D:  Text label (e.g. "EPS Disk", "ASR-10 Disk")
      Bytes 0x4E-0x4F:  0x0D 0x0A (CR LF)
      ...padding/text...
      3 bytes before bitmap: 0x0D 0x0A 0x1A (CR LF EOF)
      Skip bitmap:         Bitmap indicating which blocks are all-zeros
      Byte  0x1FF:         Disk type indicator

    Disk types (byte 0x1FF):
      0x03: EDE - EPS Double Density (1600 blocks, bitmap at 0xA0, 200 bytes)
      0x07: EDT - TS Double Density  (1600 blocks, bitmap at 0xA0, 200 bytes)
      0xCB: EDA - ASR High Density   (3200 blocks, bitmap at 0x60, 400 bytes)
      0xCC: EDT - TS High Density    (3200 blocks, bitmap at 0x60, 400 bytes)

    Skip Bitmap:
      Each bit represents one block. Bit order is MSB first within each byte.
      Bit = 1 means the block is all zeros (skipped in the file).
      Bit = 0 means the block has actual data (present in the file after header).

    After the 512-byte header, only non-skipped blocks appear sequentially.
    """
    disk_type = data[0x1FF]

    if disk_type in (GIEBLER_EDE_DD, GIEBLER_EDT_DD):
        map_offset = 0xA0
        map_size = 200
        num_blocks = EPS_DD_BLOCKS
        fmt_name = "EDE" if disk_type == GIEBLER_EDE_DD else "EDT-DD"
    elif disk_type in (GIEBLER_EDA_HD, GIEBLER_EDT_HD):
        map_offset = 0x60
        map_size = 400
        num_blocks = ASR_HD_BLOCKS
        fmt_name = "EDA" if disk_type == GIEBLER_EDA_HD else "EDT-HD"
    else:
        # Try to detect by checking signature bytes
        for mo, ms, nb, fn in [(0xA0, 200, 1600, "EDE"), (0x60, 400, 3200, "EDA")]:
            if (mo >= 3 and data[mo - 3] == 0x0D and
                    data[mo - 2] == 0x0A and data[mo - 1] == 0x1A):
                map_offset = mo
                map_size = ms
                num_blocks = nb
                fmt_name = fn
                break
        else:
            raise ValueError(f"Unknown Giebler disk type: 0x{disk_type:02X}")

    # Verify the 0D 0A 1A signature before the bitmap
    if not (data[map_offset - 3] == 0x0D and
            data[map_offset - 2] == 0x0A and
            data[map_offset - 1] == 0x1A):
        raise ValueError("Invalid Giebler header: missing 0D 0A 1A before bitmap")

    # Read the skip bitmap
    skip_bitmap = data[map_offset:map_offset + map_size]

    # Reconstruct the full disk image
    disk_data = bytearray(num_blocks * BLOCK_SIZE)
    file_pos = BLOCK_SIZE  # data starts after the 512-byte header

    for block_num in range(num_blocks):
        byte_idx = block_num // 8
        bit_idx = 7 - (block_num % 8)  # MSB first
        is_skipped = (skip_bitmap[byte_idx] >> bit_idx) & 1

        if is_skipped:
            # Block is all zeros - already zero in bytearray
            pass
        else:
            # Block has data - read from file
            end = file_pos + BLOCK_SIZE
            if end <= len(data):
                disk_data[block_num * BLOCK_SIZE:(block_num + 1) * BLOCK_SIZE] = data[file_pos:end]
            file_pos += BLOCK_SIZE

    return fmt_name, 0, bytes(disk_data)


# ---------------------------------------------------------------------------
# Filesystem Parsing
# ---------------------------------------------------------------------------

def read_block(disk_data, block_num):
    """Read a single 512-byte block from the disk image."""
    offset = block_num * BLOCK_SIZE
    return disk_data[offset:offset + BLOCK_SIZE]


def get_fat_entry(disk_data, block_num):
    """Read a FAT entry for the given block number.

    FAT blocks start at block 5. Each 512-byte FAT block contains 170
    three-byte entries (big-endian 24-bit values), plus a 2-byte signature
    "FB" at bytes 510-511.

    FAT entry values:
      0x000000 = free/unused block
      0x000001 = end of file
      0x000002 = bad block
      Other    = next block number in the file chain
    """
    fat_block_num = block_num // FAT_ENTRIES_PER_BLOCK + FAT_START_BLOCK
    entry_index = block_num % FAT_ENTRIES_PER_BLOCK
    fat_block = read_block(disk_data, fat_block_num)
    offset = entry_index * FAT_ENTRY_SIZE
    return (fat_block[offset] << 16) | (fat_block[offset + 1] << 8) | fat_block[offset + 2]


def read_file_data(disk_data, start_block, num_blocks, contiguous):
    """Read all blocks of a file, following the FAT chain.

    For contiguous files, blocks are sequential starting from start_block.
    For non-contiguous files, the FAT chain is followed after the
    contiguous portion.
    """
    result = bytearray()
    block = start_block

    for i in range(num_blocks):
        result.extend(read_block(disk_data, block))

        if i < num_blocks - 1:
            if i < contiguous - 1:
                block += 1
            else:
                next_block = get_fat_entry(disk_data, block)
                if next_block < 3:
                    break
                block = next_block

    return bytes(result)


def parse_directory(disk_data, dir_block):
    """Parse a directory at the given starting block.

    A directory occupies 2 consecutive blocks (1024 bytes) and holds up to
    39 entries of 26 bytes each.

    Directory Entry Format (26 bytes):
      Byte  0:     Type-dependent info (reserved on EPS)
      Byte  1:     File type
      Bytes 2-13:  File name (12 bytes ASCII, space-padded)
      Bytes 14-15: File size in blocks (big-endian 16-bit)
      Bytes 16-17: Number of contiguous blocks (big-endian 16-bit)
      Bytes 18-21: Starting block number (big-endian 32-bit)
      Byte  22:    Multi-file index (EPS-16) / file number (VFX-SD)
      Bytes 23-25: File size in bytes (VFX-SD) / reserved (EPS)
    """
    dir_data = read_block(disk_data, dir_block) + read_block(disk_data, dir_block + 1)
    entries = []

    for i in range(MAX_DIR_ENTRIES):
        raw = dir_data[i * DIR_ENTRY_SIZE:(i + 1) * DIR_ENTRY_SIZE]
        if len(raw) < DIR_ENTRY_SIZE:
            break
        file_type = raw[1]

        if file_type == FILE_TYPE_EMPTY:
            continue
        if file_type == FILE_TYPE_PARENT_DIR:
            continue

        name = raw[2:14].decode('ascii', errors='replace').rstrip()
        size_blocks = (raw[14] << 8) | raw[15]
        contiguous = (raw[16] << 8) | raw[17]
        start_block = (raw[18] << 24) | (raw[19] << 16) | (raw[20] << 8) | raw[21]
        multi_file_idx = raw[22]

        if size_blocks == 0:
            size_blocks = contiguous

        entries.append({
            'name': name,
            'type': file_type,
            'size': size_blocks,
            'contiguous': contiguous,
            'start': start_block,
            'multi_file_idx': multi_file_idx,
            'raw': raw,
        })

    return entries


def walk_directory(disk_data, dir_block=ROOT_DIR_BLOCK, path=""):
    """Recursively walk the directory tree, yielding all file entries."""
    total_blocks = len(disk_data) // BLOCK_SIZE
    if dir_block < 0 or dir_block + 1 >= total_blocks:
        return
    entries = parse_directory(disk_data, dir_block)
    for entry in entries:
        entry['path'] = path
        if entry['type'] == FILE_TYPE_DIRECTORY:
            if 0 < entry['start'] < total_blocks - 1:
                yield from walk_directory(disk_data, entry['start'],
                                          path + entry['name'].rstrip() + "/")
        else:
            yield entry


# ---------------------------------------------------------------------------
# Machine Type Detection
# ---------------------------------------------------------------------------

def detect_machine_type(disk_data):
    """Detect the Ensoniq machine type from the Device ID block (block 1).

    Block 1 contains a 40-byte device ID pattern. Key fields:
      Bytes 5-6:   Sectors per track (0x000A=10 for EPS/EPS-16, 0x0014=20 for ASR)
      Bytes 9-10:  Tracks/cylinders (0x0050=80)
      Bytes 38-39: "ID" signature

    Also checks the OS block (block 2) for VFX-SD indicator at bytes 8-9.
    """
    dev_id = read_block(disk_data, 1)
    os_block = read_block(disk_data, 2)

    # Check for VFX-SD/SD-1 (bytes 8-9 of OS block are non-zero)
    if os_block[8] != 0 or os_block[9] != 0:
        return "VFX-SD"

    # Check sectors per track to distinguish EPS from ASR
    spt = (dev_id[5] << 8) | dev_id[6]

    # Check for EPS-16 disk label at byte 30 (preceded by 0xFF)
    has_eps16_label = dev_id[30] == 0xFF and any(dev_id[31:38])

    # Look at directory entries for type hints
    entries = list(walk_directory(disk_data))
    eps16_types = {FILE_TYPE_EPS16_BANK, FILE_TYPE_EPS16_EFFECT,
                   FILE_TYPE_EPS16_SEQUENCE, FILE_TYPE_EPS16_SONG, FILE_TYPE_EPS16_OS}
    asr_types = {FILE_TYPE_ASR_SONG, FILE_TYPE_ASR_BANK, FILE_TYPE_ASR_AUDIOTRACK}

    for entry in entries:
        if entry['type'] in eps16_types:
            return MACHINE_EPS16
        if entry['type'] in asr_types:
            return MACHINE_ASR

    # Check instrument data for machine ID
    for entry in entries:
        if entry['type'] == FILE_TYPE_EPS_INSTRUMENT and entry['size'] > 0:
            inst_data = read_file_data(disk_data, entry['start'], min(entry['size'], 2),
                                       entry['contiguous'])
            if len(inst_data) >= 8:
                machine_id = eps_long(inst_data, 4)
                if machine_id & 0x00FF0000 == 0x00FF0000:
                    return MACHINE_EPS
                elif machine_id < 0x00002000 and machine_id > 0:
                    return MACHINE_EPS16

    if has_eps16_label:
        return MACHINE_EPS16

    if spt == 20:
        return MACHINE_ASR

    return MACHINE_EPS


def eps_long(data, offset):
    """Decode an EPSlong value at the given offset.

    EPSlong encoding: two consecutive 16-bit big-endian words,
    each an INTx16 (value stored in upper 12 bits, lower 4 bits unused).
    The first word is the low part, the second is the high part.

    Example: value 0x1234 is stored as 0x2340 0x0010
      low  INTx16: 0x234 -> stored as 0x2340
      high INTx16: 0x001 -> stored as 0x0010
    Decoded: (0x001 << 12) | 0x234 = 0x1234
    """
    w_low = (data[offset] << 8) | data[offset + 1]
    w_high = (data[offset + 2] << 8) | data[offset + 3]
    return ((w_high >> 4) << 12) | (w_low >> 4)


# ---------------------------------------------------------------------------
# Instrument Audio Extraction
# ---------------------------------------------------------------------------

def read_ensoniq_name(data, offset):
    """Read a 12-character Ensoniq name stored as 16-bit words.

    Each character occupies the high byte of a 16-bit big-endian word.
    The low byte may contain parameter data (EPS-16) or be zero (EPS).
    """
    chars = []
    for i in range(12):
        ch = data[offset + i * 2]
        if 32 <= ch < 127:
            chars.append(chr(ch))
        else:
            chars.append(' ')
    return ''.join(chars).rstrip()


def find_audio_regions(inst_data):
    """Find all audio data regions in an instrument file.

    Scans through the instrument in 512-byte blocks, classifying each as
    audio or non-audio based on two criteria:

    1. 13-bit audio (EPS): all 16-bit samples have low 3 bits = 0 (mod 8),
       but the block is not mostly zeros (which would be parameter data
       with INTx16 encoding).

    2. 16-bit audio (EPS-16/ASR): samples do NOT cluster at mod-8 boundaries,
       and the block has very few zero bytes (dense waveform data).

    Returns a list of (start_offset, end_offset) tuples for each audio region.
    Regions smaller than 2048 bytes are discarded as likely parameter fragments.
    """
    MIN_REGION_BYTES = 2048

    if len(inst_data) < BLOCK_SIZE:
        return []

    regions = []
    in_audio = False
    region_start = 0

    for off in range(0, len(inst_data), BLOCK_SIZE):
        chunk = inst_data[off:off + BLOCK_SIZE]
        if len(chunk) < BLOCK_SIZE:
            break

        num_samples = BLOCK_SIZE // 2
        mod8_count = 0
        zero_sample_count = 0
        for i in range(0, BLOCK_SIZE, 2):
            val = struct.unpack('>h', chunk[i:i + 2])[0]
            if val % 8 == 0:
                mod8_count += 1
            if val == 0:
                zero_sample_count += 1
        zero_byte_count = chunk.count(0)

        is_13bit_audio = mod8_count >= num_samples - 6 and zero_sample_count < 25
        is_16bit_audio = mod8_count < 50 and zero_byte_count < 30
        is_audio = is_13bit_audio or is_16bit_audio

        if is_audio and not in_audio:
            region_start = off
            in_audio = True
        elif not is_audio and in_audio:
            if off - region_start >= MIN_REGION_BYTES:
                regions.append((region_start, off))
            in_audio = False

    if in_audio:
        end = (len(inst_data) // 2) * 2
        if end - region_start >= MIN_REGION_BYTES:
            regions.append((region_start, end))

    return regions


def detect_sample_rate_eps16(inst_data):
    """Try to detect the sample rate for an EPS-16 Plus instrument.

    The sample rate info is encoded in the wavesample parameters.
    We look for common sample rate indicator patterns.
    Returns sample rate in Hz or None if not detected.
    """
    # Search for sample rate indicator in instrument header area
    # The EPS-16 stores various config strings - look for rate hints
    header_text = inst_data[:min(4096, len(inst_data))]

    # Look for ASCII rate strings like "44K", "33K", "30K", "22K", "15K", "11K"
    rate_map = {
        b'44K': 44100, b'44k': 44100,
        b'33K': 33000, b'33k': 33000,
        b'30K': 30000, b'30k': 30000,
        b'27K': 27000, b'27k': 27000,
        b'22K': 22050, b'22k': 22050,
        b'15K': 15200, b'15k': 15200,
        b'11K': 11200, b'11k': 11200,
    }

    for pattern, rate in rate_map.items():
        if pattern in header_text:
            return rate

    return None


def extract_instrument_audio(disk_data, entry, machine_type):
    """Extract audio data from an instrument file entry.

    Finds all audio regions within the instrument (multi-wavesample
    instruments have multiple audio blocks separated by parameter data)
    and concatenates them into a single stream.

    Returns a list of (name, sample_rate, audio_bytes) tuples.
    Audio bytes are 16-bit big-endian signed PCM samples.
    """
    inst_data = read_file_data(disk_data, entry['start'], entry['size'],
                                entry['contiguous'])
    if len(inst_data) < 64:
        return []

    inst_name = read_ensoniq_name(inst_data, 10)
    if not inst_name.strip():
        inst_name = entry['name']

    if machine_type == MACHINE_EPS:
        sample_rate = DEFAULT_SAMPLE_RATES[MACHINE_EPS]
    elif machine_type == MACHINE_EPS16:
        detected_rate = detect_sample_rate_eps16(inst_data)
        sample_rate = detected_rate if detected_rate else DEFAULT_SAMPLE_RATES[MACHINE_EPS16]
    else:
        sample_rate = DEFAULT_SAMPLE_RATES.get(machine_type, 44100)

    regions = find_audio_regions(inst_data)
    if not regions:
        return []

    audio_data = bytearray()
    for start, end in regions:
        audio_data.extend(inst_data[start:end])

    if len(audio_data) % 2:
        audio_data = audio_data[:-1]

    if len(audio_data) < 4:
        return []

    return [(inst_name, sample_rate, bytes(audio_data))]


# ---------------------------------------------------------------------------
# WAV Output
# ---------------------------------------------------------------------------

def write_wav(filepath, sample_rate, audio_data_be):
    """Write a WAV file from 16-bit big-endian signed PCM data.

    Converts big-endian samples to little-endian for WAV format.
    """
    num_samples = len(audio_data_be) // 2

    # Convert big-endian to little-endian
    le_data = bytearray(len(audio_data_be))
    for i in range(0, len(audio_data_be), 2):
        le_data[i] = audio_data_be[i + 1]
        le_data[i + 1] = audio_data_be[i]

    # WAV header
    num_channels = 1
    bits_per_sample = 16
    byte_rate = sample_rate * num_channels * (bits_per_sample // 8)
    block_align = num_channels * (bits_per_sample // 8)
    data_size = len(le_data)
    file_size = 36 + data_size

    header = struct.pack('<4sI4s', b'RIFF', file_size, b'WAVE')
    fmt_chunk = struct.pack('<4sIHHIIHH', b'fmt ', 16, 1,
                            num_channels, sample_rate, byte_rate,
                            block_align, bits_per_sample)
    data_header = struct.pack('<4sI', b'data', data_size)

    with open(filepath, 'wb') as f:
        f.write(header)
        f.write(fmt_chunk)
        f.write(data_header)
        f.write(le_data)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def sanitize_filename(name):
    """Make a string safe for use as a filename."""
    safe = name.strip()
    # Replace problematic characters
    for ch in '/\\:*?"<>|':
        safe = safe.replace(ch, '_')
    return safe if safe else "unnamed"


def process_image(input_file, output_dir):
    """Process an Ensoniq disk image and extract all instruments as WAV files."""
    print(f"Reading: {input_file}")
    with open(input_file, 'rb') as f:
        raw_data = f.read()

    # Load disk image
    fmt_name, data_offset, disk_data = identify_image_format(raw_data)
    print(f"Format: {fmt_name}")
    print(f"Disk data: {len(disk_data)} bytes ({len(disk_data) // BLOCK_SIZE} blocks)")

    # Detect machine type
    machine_type = detect_machine_type(disk_data)
    print(f"Machine: {machine_type}")

    # Parse filesystem
    all_entries = list(walk_directory(disk_data))
    instruments = [e for e in all_entries if e['type'] in INSTRUMENT_TYPES]
    print(f"Found {len(instruments)} instrument(s)")

    if not instruments:
        print("No instruments found in this disk image.")
        return 0

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Extract each instrument
    count = 0
    used_names = set()
    for entry in instruments:
        path_prefix = entry.get('path', '')
        results = extract_instrument_audio(disk_data, entry, machine_type)

        for name, sample_rate, audio_data in results:
            num_samples = len(audio_data) // 2
            duration = num_samples / sample_rate

            # Generate unique filename
            base_name = sanitize_filename(f"{path_prefix}{name}")
            filename = base_name + ".wav"
            if filename in used_names:
                idx = 2
                while f"{base_name}_{idx}.wav" in used_names:
                    idx += 1
                filename = f"{base_name}_{idx}.wav"
            used_names.add(filename)

            filepath = os.path.join(output_dir, filename)
            write_wav(filepath, sample_rate, audio_data)
            count += 1
            print(f"  [{count}] {filename} - {sample_rate}Hz, {num_samples} samples, {duration:.2f}s")

    print(f"\nExtracted {count} WAV file(s) to: {output_dir}")
    return count


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>")
        print()
        print("Convert an Ensoniq Disk Image file into WAV files.")
        print()
        print("Supported input formats:")
        print("  .GKH  - Goh King Wah format")
        print("  .EDE  - Giebler EPS Double Density")
        print("  .EDA  - Giebler ASR High Density")
        print("  .EDT  - Giebler TS format")
        print("  .EDV  - Giebler VFX format")
        print("  .EDS  - Giebler SQ/SD format")
        print("  .IMG  - Raw disk image")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(input_file):
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)

    try:
        count = process_image(input_file, output_dir)
        if count == 0:
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

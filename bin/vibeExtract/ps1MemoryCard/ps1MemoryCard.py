# Vibe coded by Claude
# PlayStation 1 Memory Card Extractor
# Extracts all saves and icons from PS1 memory card image files

import struct
import sys
import os
from PIL import Image


CARD_SIZE = 131072       # 128 KB
FRAME_SIZE = 128
BLOCK_SIZE = 8192        # 64 frames
HEADER_MAGIC = b"MC"
SAVE_MAGICS = (b"SC", b"JG")  # SC = standard, JG = alternate (some games)

# Block allocation states
STATE_FIRST_LINK = 0x51
STATE_MIDDLE_LINK = 0x52
STATE_END_LINK = 0x53
STATE_FREE = 0xA0
STATE_DELETED_FIRST = 0xA1
STATE_DELETED_MIDDLE = 0xA2
STATE_DELETED_END = 0xA3
STATE_UNINITIALIZED = 0x00

# Icon display flags
ICON_1_FRAME = 0x11
ICON_2_FRAMES = 0x12
ICON_3_FRAMES = 0x13

ICON_WIDTH = 16
ICON_HEIGHT = 16
ICON_FRAME_BYTES = 128   # 16x16 @ 4bpp
CLUT_ENTRIES = 16
CLUT_BYTES = 32          # 16 colors x 2 bytes


def xor_checksum(data):
    """Compute XOR checksum over a sequence of bytes."""
    result = 0
    for b in data:
        result ^= b
    return result


def bgr555_to_rgba(color16):
    """Convert a 16-bit BGR555 color to (R, G, B, A) tuple."""
    if color16 == 0x0000:
        return (0, 0, 0, 0)  # Fully transparent

    r5 = color16 & 0x1F
    g5 = (color16 >> 5) & 0x1F
    b5 = (color16 >> 10) & 0x1F

    # Scale 5-bit to 8-bit with rounding
    r8 = (r5 << 3) | (r5 >> 2)
    g8 = (g5 << 3) | (g5 >> 2)
    b8 = (b5 << 3) | (b5 >> 2)

    return (r8, g8, b8, 255)


def decode_clut(clut_data):
    """Decode 32-byte CLUT into list of 16 RGBA tuples."""
    colors = []
    for i in range(CLUT_ENTRIES):
        color16 = struct.unpack_from("<H", clut_data, i * 2)[0]
        colors.append(bgr555_to_rgba(color16))
    return colors


def decode_icon_frame(pixel_data, clut):
    """Decode 128-byte 4bpp icon frame into a 16x16 RGBA image."""
    img = Image.new("RGBA", (ICON_WIDTH, ICON_HEIGHT))
    pixels = img.load()
    for y in range(ICON_HEIGHT):
        for x in range(0, ICON_WIDTH, 2):
            byte_index = y * (ICON_WIDTH // 2) + x // 2
            byte_val = pixel_data[byte_index]
            left_index = byte_val & 0x0F
            right_index = (byte_val >> 4) & 0x0F
            pixels[x, y] = clut[left_index]
            pixels[x + 1, y] = clut[right_index]
    return img


def decode_shift_jis(raw_bytes):
    """Decode Shift-JIS bytes to a Python string, stripping trailing nulls."""
    # Find null terminator
    null_pos = raw_bytes.find(b"\x00")
    if null_pos >= 0:
        raw_bytes = raw_bytes[:null_pos]
    try:
        return raw_bytes.decode("shift_jis")
    except (UnicodeDecodeError, ValueError):
        return raw_bytes.decode("ascii", errors="replace")


def sanitize_filename(name):
    """Make a string safe for use as a directory/file name."""
    # Replace characters that are problematic in file paths
    bad_chars = '<>:"/\\|?*'
    result = name
    for c in bad_chars:
        result = result.replace(c, "_")
    # Remove control characters
    result = "".join(c if ord(c) >= 32 else "_" for c in result)
    # Strip trailing dots and spaces (Windows compatibility)
    result = result.rstrip(". ")
    if not result:
        result = "unnamed"
    return result


def state_name(state):
    """Return a human-readable name for a block allocation state."""
    names = {
        STATE_FIRST_LINK: "Used (First)",
        STATE_MIDDLE_LINK: "Used (Middle)",
        STATE_END_LINK: "Used (End)",
        STATE_FREE: "Free",
        STATE_DELETED_FIRST: "Deleted (First)",
        STATE_DELETED_MIDDLE: "Deleted (Middle)",
        STATE_DELETED_END: "Deleted (End)",
        STATE_UNINITIALIZED: "Uninitialized",
    }
    return names.get(state, f"Unknown (0x{state:02X})")


def icon_flag_description(flag):
    """Return description of icon display flag."""
    descs = {
        ICON_1_FRAME: "Static (1 frame)",
        ICON_2_FRAMES: "Animated (2 frames)",
        ICON_3_FRAMES: "Animated (3 frames)",
    }
    return descs.get(flag, f"Unknown (0x{flag:02X})")


def num_icon_frames(flag):
    """Return the number of icon frames from the icon display flag."""
    return {ICON_1_FRAME: 1, ICON_2_FRAMES: 2, ICON_3_FRAMES: 3}.get(flag, 1)


def parse_directory_entry(data, slot_index):
    """Parse a single 128-byte directory entry."""
    offset = 0x80 + slot_index * FRAME_SIZE
    frame = data[offset : offset + FRAME_SIZE]

    state = frame[0]
    reserved = frame[1:4]
    save_size = struct.unpack_from("<I", frame, 4)[0]
    next_block = struct.unpack_from("<H", frame, 8)[0]
    filename_raw = frame[0x0A : 0x0A + 117]
    stored_checksum = frame[0x7F]
    computed_checksum = xor_checksum(frame[:0x7F])

    # Extract null-terminated filename
    null_pos = filename_raw.find(b"\x00")
    if null_pos >= 0:
        filename = filename_raw[:null_pos].decode("ascii", errors="replace")
    else:
        filename = filename_raw.decode("ascii", errors="replace")

    return {
        "slot": slot_index,
        "state": state,
        "reserved": reserved,
        "save_size": save_size,
        "next_block": next_block,
        "filename": filename,
        "filename_raw": filename_raw,
        "checksum_ok": computed_checksum == stored_checksum,
        "stored_checksum": stored_checksum,
        "computed_checksum": computed_checksum,
        "raw_frame": frame,
    }


def collect_block_chain(directory, start_slot):
    """Follow the block chain from start_slot, return list of slot indices."""
    chain = [start_slot]
    current = start_slot
    visited = {start_slot}
    while True:
        entry = directory[current]
        next_blk = entry["next_block"]
        if next_blk == 0xFFFF:
            break
        if next_blk < 0 or next_blk >= 15:
            print(f"  WARNING: Invalid next block pointer {next_blk} in slot {current}")
            break
        if next_blk in visited:
            print(f"  WARNING: Circular block chain detected at slot {next_blk}")
            break
        visited.add(next_blk)
        chain.append(next_blk)
        current = next_blk
    return chain


def extract_save(data, directory, start_slot, output_dir):
    """Extract a single save from the memory card."""
    entry = directory[start_slot]
    filename = entry["filename"]
    save_size = entry["save_size"]

    # Build the block chain
    chain = collect_block_chain(directory, start_slot)

    # Collect raw data from all blocks in the chain
    save_data = bytearray()
    for slot in chain:
        block_offset = (slot + 1) * BLOCK_SIZE
        save_data.extend(data[block_offset : block_offset + BLOCK_SIZE])

    # Truncate to declared save size
    if save_size > 0 and save_size <= len(save_data):
        save_data = save_data[:save_size]

    # Parse save data header
    if len(save_data) < 4 or save_data[:2] not in SAVE_MAGICS:
        print(f"  WARNING: Save data does not start with 'SC'/'JG' magic for '{filename}'"
              f" (got {save_data[:2].hex() if len(save_data) >= 2 else 'N/A'})")
        # Still save the raw data
        safe_name = sanitize_filename(filename) if filename else f"slot_{start_slot}"
        save_dir = os.path.join(output_dir, safe_name)
        os.makedirs(save_dir, exist_ok=True)
        with open(os.path.join(save_dir, "save.bin"), "wb") as f:
            f.write(save_data)
        return

    save_magic = save_data[:2].decode("ascii")
    icon_flag = save_data[2]
    block_count = save_data[3]
    n_frames = num_icon_frames(icon_flag)

    # Decode title (Shift-JIS, 64 bytes at offset 0x04)
    title_raw = bytes(save_data[0x04:0x44])
    title = decode_shift_jis(title_raw)

    # Reserved / game-specific data (28 bytes at offset 0x44)
    reserved_data = bytes(save_data[0x44:0x60])

    # Decode CLUT (32 bytes at offset 0x60)
    clut_data = bytes(save_data[0x60:0x80])
    clut = decode_clut(clut_data)

    # Create output directory
    safe_name = sanitize_filename(filename) if filename else f"slot_{start_slot}"
    # Handle duplicate directory names by appending slot number
    save_dir = os.path.join(output_dir, safe_name)
    if os.path.exists(save_dir):
        save_dir = os.path.join(output_dir, f"{safe_name}_slot{start_slot}")
    os.makedirs(save_dir, exist_ok=True)

    # Extract icon frames
    for frame_idx in range(n_frames):
        pixel_offset = 0x80 + frame_idx * ICON_FRAME_BYTES
        if pixel_offset + ICON_FRAME_BYTES > len(save_data):
            print(f"  WARNING: Insufficient data for icon frame {frame_idx}")
            break
        pixel_data = bytes(save_data[pixel_offset : pixel_offset + ICON_FRAME_BYTES])
        icon_img = decode_icon_frame(pixel_data, clut)
        icon_path = os.path.join(save_dir, f"icon_frame{frame_idx}.png")
        icon_img.save(icon_path)

    # Save the complete raw data block(s) for this save
    with open(os.path.join(save_dir, "save.bin"), "wb") as f:
        f.write(save_data)

    # Write metadata info file
    with open(os.path.join(save_dir, "info.txt"), "w", encoding="utf-8") as f:
        f.write(f"Filename: {filename}\n")
        f.write(f"Title: {title}\n")
        f.write(f"Save Magic: {save_magic}\n")
        f.write(f"Directory Slot: {start_slot}\n")
        f.write(f"Block Count: {block_count}\n")
        f.write(f"Save Size: {save_size} bytes\n")
        f.write(f"Block Chain: {' -> '.join(str(s) for s in chain)}\n")
        f.write(f"Icon: {icon_flag_description(icon_flag)} (0x{icon_flag:02X})\n")
        f.write(f"Directory Checksum Valid: {entry['checksum_ok']}\n")
        if reserved_data != b"\x00" * 28:
            f.write(f"Reserved Data (hex): {reserved_data.hex()}\n")
        f.write(f"\nCLUT (BGR555 hex): ")
        for i in range(CLUT_ENTRIES):
            color16 = struct.unpack_from("<H", clut_data, i * 2)[0]
            f.write(f"0x{color16:04X} ")
        f.write("\n")

    deleted = entry["state"] in (STATE_DELETED_FIRST,)
    status = " [DELETED]" if deleted else ""
    print(f"  Slot {start_slot:2d}: {filename:30s} {title:30s} "
          f"{save_size:6d} bytes, {n_frames} icon frame(s){status}")


def extract_memory_card(input_file, output_dir):
    """Extract all saves from a PS1 memory card image file."""
    with open(input_file, "rb") as f:
        data = f.read()

    file_size = len(data)
    basename = os.path.basename(input_file)

    # Validate file
    if file_size != CARD_SIZE:
        if file_size == BLOCK_SIZE:
            print(f"File is {file_size} bytes (single management block only, no save data)")
            # Parse what we can but there's no data to extract
        else:
            print(f"ERROR: File size {file_size} is not the expected {CARD_SIZE} bytes")
            sys.exit(1)

    if data[:2] != HEADER_MAGIC:
        print(f"ERROR: File does not start with 'MC' magic (got {data[:2]!r})")
        sys.exit(1)

    # Validate header checksum
    header_checksum_ok = xor_checksum(data[:0x7F]) == data[0x7F]
    if not header_checksum_ok:
        print(f"WARNING: Header frame checksum mismatch")

    # Check write test frame
    if file_size == CARD_SIZE:
        write_test = data[0x1F80:0x2000]
        header_frame = data[0x0000:0x0080]
        if write_test != header_frame:
            # Not an error - some emulator formats don't maintain this
            pass

    # Parse all 15 directory entries
    directory = []
    for i in range(15):
        entry = parse_directory_entry(data, i)
        directory.append(entry)

    # Check broken sector list (20 entries of 4 bytes, valid frame range 0-1023)
    # Some emulators format this frame like a directory entry (0xA0 state + checksum)
    bsl_frame = data[0x0800:0x0880]
    broken_sectors = []
    bsl_is_dir_format = bsl_frame[0] in (0xA0, 0xA1, 0xA2, 0xA3, 0x51, 0x52, 0x53)
    if not bsl_is_dir_format:
        for i in range(20):
            sector_val = struct.unpack_from("<I", bsl_frame, i * 4)[0]
            if sector_val not in (0xFFFFFFFF, 0x00000000) and sector_val <= 1023:
                broken_sectors.append(sector_val)

    os.makedirs(output_dir, exist_ok=True)

    print(f"PS1 Memory Card: {basename}")
    print(f"Header Checksum: {'OK' if header_checksum_ok else 'MISMATCH'}")
    if broken_sectors:
        print(f"Broken Sectors: {broken_sectors}")
    print()

    # Extract saves (only from first-link blocks, including deleted)
    save_count = 0
    if file_size == CARD_SIZE:
        for i in range(15):
            entry = directory[i]
            if entry["state"] in (STATE_FIRST_LINK, STATE_DELETED_FIRST):
                extract_save(data, directory, i, output_dir)
                save_count += 1

    # Write card-level metadata
    with open(os.path.join(output_dir, "card_info.txt"), "w", encoding="utf-8") as f:
        f.write(f"Source File: {basename}\n")
        f.write(f"File Size: {file_size} bytes\n")
        f.write(f"Header Checksum: {'OK' if header_checksum_ok else 'MISMATCH'}\n")
        if broken_sectors:
            f.write(f"Broken Sectors: {broken_sectors}\n")
        f.write(f"\nDirectory Listing:\n")
        f.write(f"{'Slot':>4s}  {'State':<20s}  {'Size':>6s}  {'Next':>6s}  {'Chk':>3s}  {'Filename'}\n")
        f.write(f"{'-'*4:>4s}  {'-'*20:<20s}  {'-'*6:>6s}  {'-'*6:>6s}  {'-'*3:>3s}  {'-'*30}\n")
        for entry in directory:
            chk = "OK" if entry["checksum_ok"] else "BAD"
            next_str = f"0x{entry['next_block']:04X}" if entry["next_block"] != 0xFFFF else "  end"
            f.write(f"{entry['slot']:4d}  {state_name(entry['state']):<20s}  "
                    f"{entry['save_size']:6d}  {next_str:>6s}  {chk:>3s}  {entry['filename']}\n")

        # Document management block contents
        f.write(f"\nManagement Block Details:\n")

        # Broken sector list
        f.write(f"  Broken Sector List (0x0800-0x087F):\n")
        bsl_all_ff = all(b == 0xFF for b in bsl_frame[:80])
        bsl_all_zero = all(b == 0x00 for b in bsl_frame[:80])
        if bsl_all_ff or bsl_all_zero:
            f.write(f"    No broken sectors\n")
        else:
            f.write(f"    Raw: {bsl_frame[:80].hex()}\n")

        # Broken sector replacement data
        bsr_data = data[0x0880:0x1180]
        f.write(f"  Broken Sector Replacement Data (0x0880-0x117F):\n")
        bsr_all_zero = all(b == 0x00 for b in bsr_data)
        bsr_all_ff = all(b == 0xFF for b in bsr_data)
        if bsr_all_zero or bsr_all_ff:
            f.write(f"    Empty (all {'0x00' if bsr_all_zero else '0xFF'})\n")
        else:
            f.write(f"    Contains data (non-empty)\n")

        # Unused frames
        if file_size == CARD_SIZE:
            unused_data = data[0x1180:0x1F80]
            f.write(f"  Unused Frames (0x1180-0x1F7F):\n")
            unused_all_zero = all(b == 0x00 for b in unused_data)
            unused_all_ff = all(b == 0xFF for b in unused_data)
            if unused_all_zero or unused_all_ff:
                f.write(f"    Empty (all {'0x00' if unused_all_zero else '0xFF'})\n")
            else:
                f.write(f"    Contains data (non-empty)\n")

            # Write test frame
            write_test = data[0x1F80:0x2000]
            f.write(f"  Write Test Frame (0x1F80-0x1FFF):\n")
            if write_test == data[0x0000:0x0080]:
                f.write(f"    Matches header frame\n")
            else:
                f.write(f"    Does not match header frame\n")

    if save_count == 0:
        print("  No saves found on this card.")
    else:
        print(f"\nExtracted {save_count} save(s) to {output_dir}")


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>")
        print(f"  Extracts all saves and icons from a PS1 memory card image.")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(input_file):
        print(f"ERROR: Input file not found: {input_file}")
        sys.exit(1)

    extract_memory_card(input_file, output_dir)


if __name__ == "__main__":
    main()

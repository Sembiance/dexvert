#!/usr/bin/env python3
# Vibe coded by Claude
"""
unNewtonPackage.py - Extract files from Apple Newton Package (.pkg) files.

Usage: python3 unNewtonPackage.py [--all] <inputFile> <outputDir>

Parses the Newton Package binary format and extracts:
  - Each part's raw binary data as a separate file
  - Package metadata as a JSON file
  - Human-viewable content from within parts:
    * Bitmaps (bits/mask/cbits) -> PNG images
    * Sound samples -> WAV audio files
    * Text strings -> single combined .txt file per part
    * QuickDraw PICT images -> raw .pict files

Options:
  --all   Also output directory.bin (raw package header/directory region)
"""

import struct
import sys
import os
import json
import datetime
import wave
import io

try:
    from PIL import Image
except ImportError:
    Image = None

# Seconds between 1904-01-01 and 1970-01-01
NEWTON_EPOCH_OFFSET = 2082844800

# Newton object tags
TAG_BINARY = 0x40  # Binary object (also used for symbols)
TAG_FRAME = 0x41   # Frame (map) object
TAG_ARRAY = 0x43   # Array object

# Symbol class magic constant (ROM pointer to symbol class)
SYMBOL_CLASS = 0x00055552

# Padding/filler bytes between objects
FILLER_BYTES = frozenset([0xAD, 0xBA, 0xDB, 0xBF])


def decode_utf16be(data):
    """Decode a UTF-16BE byte string, stripping the null terminator."""
    text = data.decode("utf-16-be", errors="replace")
    return text.rstrip("\x00")


def newton_date_to_iso(seconds):
    """Convert Newton timestamp (seconds since 1904-01-01) to ISO string."""
    if seconds == 0:
        return None
    try:
        unix_ts = seconds - NEWTON_EPOCH_OFFSET
        dt = datetime.datetime.fromtimestamp(unix_ts, tz=datetime.timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except (OSError, OverflowError, ValueError):
        return f"0x{seconds:08X} (unparseable)"


# ---------------------------------------------------------------------------
# Newton Object Parser
# ---------------------------------------------------------------------------

def walk_objects(part_data):
    """Walk all Newton objects in part data.

    Yields (offset, size, tag, obj_bytes) for each valid object found.
    Objects are padded to 4-byte alignment with filler bytes.
    """
    pos = 0
    length = len(part_data)
    while pos + 12 <= length:
        header = struct.unpack_from(">I", part_data, pos)[0]
        tag = header & 0xFF
        size = header >> 8

        if tag not in (TAG_BINARY, TAG_FRAME, TAG_ARRAY):
            pos += 4
            continue
        if size < 12 or pos + size > length:
            pos += 4
            continue

        yield pos, size, tag, part_data[pos : pos + size]

        # Advance past object to next 4-byte aligned position
        pos += size
        pos = (pos + 3) & ~3
        # Skip any filler padding bytes
        while pos < length and part_data[pos] in FILLER_BYTES:
            pos += 1


def resolve_class_name(obj_data, part_data, base_offset):
    """Resolve the class name of a binary or array object.

    obj_data: the full object bytes (starting from header)
    part_data: the entire part's raw data
    base_offset: the absolute file offset where part_data begins
                 (dir_size + part's data_offset)

    Returns the class name string, or None if unresolvable.
    """
    if len(obj_data) < 12:
        return None
    class_ref = struct.unpack_from(">I", obj_data, 8)[0]

    if class_ref == SYMBOL_CLASS:
        return "__symbol__"

    # Pointer reference (low 2 bits == 1)
    if class_ref & 0x3 == 1:
        target_abs = class_ref & ~3
        target_pd = target_abs - base_offset
        if 0 <= target_pd < len(part_data) and target_pd + 16 <= len(part_data):
            t_header = struct.unpack_from(">I", part_data, target_pd)[0]
            t_tag = t_header & 0xFF
            if t_tag == TAG_BINARY:
                t_class = struct.unpack_from(">I", part_data, target_pd + 8)[0]
                if t_class == SYMBOL_CLASS:
                    # It's a symbol - extract name after hash
                    name_start = target_pd + 16
                    name_end = part_data.find(0, name_start, target_pd + (t_header >> 8))
                    if name_end > name_start:
                        return part_data[name_start:name_end].decode(
                            "ascii", errors="replace"
                        )
    return None


# ---------------------------------------------------------------------------
# Bitmap Extraction
# ---------------------------------------------------------------------------

def parse_bitmap_header(payload):
    """Parse a Newton bitmap header from the payload (after obj header+gc+class).

    Returns dict with: base_addr, row_bytes, flags, top, left, bottom, right,
                        width, height, bpp, pixel_data
    """
    if len(payload) < 16:
        return None

    base_addr = struct.unpack_from(">I", payload, 0)[0]
    row_bytes = struct.unpack_from(">H", payload, 4)[0]
    flags = struct.unpack_from(">H", payload, 6)[0]
    top, left, bottom, right = struct.unpack_from(">hhhh", payload, 8)

    width = right - left
    height = bottom - top
    if width <= 0 or height <= 0 or row_bytes == 0:
        return None

    bpp = (row_bytes * 8) // width
    # Clamp to valid depths
    if bpp not in (1, 2, 4, 8, 16, 24, 32):
        # Try nearest valid depth
        for valid in (1, 2, 4, 8):
            if row_bytes * 8 >= width * valid and row_bytes * 8 < width * (valid * 2):
                bpp = valid
                break

    pixel_data = payload[16:]
    expected = row_bytes * height
    if len(pixel_data) < expected:
        return None

    pixel_data = pixel_data[:expected]

    return {
        "base_addr": base_addr,
        "row_bytes": row_bytes,
        "flags": flags,
        "top": top,
        "left": left,
        "bottom": bottom,
        "right": right,
        "width": width,
        "height": height,
        "bpp": bpp,
        "pixel_data": pixel_data,
    }


def bitmap_to_image(bmp_info, class_name):
    """Convert a parsed Newton bitmap to a PIL Image.

    Newton grayscale convention: 0 = white, max = black.
    We invert to standard convention (0 = black, 255 = white) for PNG output.
    """
    if Image is None:
        return None

    w = bmp_info["width"]
    h = bmp_info["height"]
    bpp = bmp_info["bpp"]
    rb = bmp_info["row_bytes"]
    px = bmp_info["pixel_data"]

    img = Image.new("L", (w, h))
    pixels = img.load()

    for y in range(h):
        row_start = y * rb
        row_data = px[row_start : row_start + rb]

        if bpp == 1:
            for x in range(w):
                byte_idx = x // 8
                bit_idx = 7 - (x % 8)
                if byte_idx < len(row_data):
                    bit = (row_data[byte_idx] >> bit_idx) & 1
                    # Newton: 1=black, 0=white -> invert for standard
                    pixels[x, y] = 0 if bit else 255

        elif bpp == 2:
            for x in range(w):
                byte_idx = x // 4
                shift = 6 - (x % 4) * 2
                if byte_idx < len(row_data):
                    val = (row_data[byte_idx] >> shift) & 0x3
                    # Newton: 0=white(255), 3=black(0)
                    pixels[x, y] = 255 - val * 85

        elif bpp == 4:
            for x in range(w):
                byte_idx = x // 2
                if byte_idx < len(row_data):
                    if x % 2 == 0:
                        val = (row_data[byte_idx] >> 4) & 0xF
                    else:
                        val = row_data[byte_idx] & 0xF
                    # Newton: 0=white(255), 15=black(0)
                    pixels[x, y] = 255 - val * 17

        elif bpp == 8:
            for x in range(w):
                if x < len(row_data):
                    val = row_data[x]
                    # Newton: 0=white(255), 255=black(0)
                    pixels[x, y] = 255 - val

    return img


# ---------------------------------------------------------------------------
# Sound Extraction
# ---------------------------------------------------------------------------

def samples_to_wav(sample_data, sample_rate=22050):
    """Convert raw 8-bit unsigned PCM samples to a WAV file in memory.

    Returns bytes of the WAV file.
    """
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(1)
        wf.setframerate(sample_rate)
        wf.writeframes(sample_data)
    return buf.getvalue()


def find_sample_rate(part_data, base_offset):
    """Try to find the samplingRate value in Newton object data.

    Strategy: if the part contains a 'samplingRate' symbol, scan for 'real'
    (IEEE 754 double) objects containing a plausible sample rate value
    (common Newton rates: 22254.545, 11127.272, 8012, 5563.636, etc.).

    Returns the rate as an integer, or 22050 as default.
    """
    # First check: does this part even have sound data?
    has_samples_sym = b"samples\x00" in part_data
    has_rate_sym = b"samplingRate\x00" in part_data
    if not has_samples_sym:
        return 22050

    # Known Newton sample rates (hardware rate 22254.5454 / divisors)
    newton_rates = [22254.5454, 11127.2727, 8012.0, 5563.6363]

    # Scan for 'real' objects (tag 0x40, size 20) with plausible rate values
    best_rate = None
    pos = 0
    while pos + 20 <= len(part_data):
        header = struct.unpack_from(">I", part_data, pos)[0]
        tag = header & 0xFF
        size = header >> 8
        if tag == TAG_BINARY and size == 20 and pos + 20 <= len(part_data):
            gc = struct.unpack_from(">I", part_data, pos + 4)[0]
            if gc == 0:
                dbl = struct.unpack_from(">d", part_data, pos + 12)[0]
                # Check if it's close to a known Newton rate
                for nr in newton_rates:
                    if abs(dbl - nr) < 1.0:
                        best_rate = int(round(dbl))
                        break
                if best_rate:
                    break
        pos += 4

    if best_rate and has_rate_sym:
        return best_rate

    # Fallback: check for common rates as immediate integers
    for rate in [22050, 11025, 8000, 8012, 5564]:
        imm = struct.pack(">I", rate << 2)
        if imm in part_data:
            return rate

    return 22050


# ---------------------------------------------------------------------------
# Content Extraction from Part Data
# ---------------------------------------------------------------------------

def extract_content_from_part(part_data, base_offset, output_dir, part_index):
    """Extract human-viewable content (bitmaps, sounds, strings) from part data.

    part_data: raw bytes of the part
    base_offset: absolute file offset where this part starts (dir_size + data_offset)
    output_dir: directory to write extracted files
    part_index: part number for filename prefixing

    Returns a list of extracted file descriptions.
    """
    extracted = []
    prefix = f"p{part_index}"

    bitmap_count = 0
    sound_count = 0
    pict_count = 0
    collected_strings = []

    # Detect sample rate for sound extraction
    sample_rate = find_sample_rate(part_data, base_offset)

    for obj_off, obj_size, tag, obj_bytes in walk_objects(part_data):
        if tag != TAG_BINARY:
            continue

        cls = resolve_class_name(obj_bytes, part_data, base_offset)
        if cls is None or cls == "__symbol__":
            continue

        payload = obj_bytes[12:]  # skip header(4) + gc(4) + class(4)

        # --- Bitmaps: bits, mask, cbits ---
        if cls in ("bits", "mask", "cbits"):
            bmp = parse_bitmap_header(payload)
            if bmp is None:
                continue

            bitmap_count += 1
            desc = (
                f"{cls} {bmp['width']}x{bmp['height']} {bmp['bpp']}bpp"
            )

            if Image is not None:
                img = bitmap_to_image(bmp, cls)
                if img:
                    fname = f"{prefix}_{cls}_{bitmap_count:03d}_{bmp['width']}x{bmp['height']}.png"
                    fpath = os.path.join(output_dir, fname)
                    img.save(fpath, "PNG")
                    extracted.append(f"  {desc} -> {fname}")
            else:
                # No Pillow - save raw pixel data
                fname = f"{prefix}_{cls}_{bitmap_count:03d}_{bmp['width']}x{bmp['height']}.raw"
                fpath = os.path.join(output_dir, fname)
                with open(fpath, "wb") as f:
                    f.write(bmp["pixel_data"])
                extracted.append(f"  {desc} -> {fname} (raw, no Pillow)")

        # --- Sound samples ---
        elif cls == "samples":
            sound_count += 1
            duration_ms = len(payload) * 1000 // sample_rate
            fname = f"{prefix}_sound_{sound_count:03d}_{duration_ms}ms.wav"
            fpath = os.path.join(output_dir, fname)
            wav_data = samples_to_wav(payload, sample_rate=sample_rate)
            with open(fpath, "wb") as f:
                f.write(wav_data)
            extracted.append(
                f"  samples {len(payload)} bytes ({duration_ms}ms) -> {fname}"
            )

        # --- Text strings ---
        elif cls in ("string", "String"):
            if len(payload) < 4:
                continue
            try:
                text = payload.decode("utf-16-be", errors="replace").rstrip("\x00")
            except Exception:
                continue
            if not text or len(text.strip()) == 0:
                continue
            collected_strings.append(text)

        # --- QuickDraw PICT images ---
        elif cls == "picture":
            pict_count += 1
            fname = f"{prefix}_picture_{pict_count:03d}.pict"
            fpath = os.path.join(output_dir, fname)
            with open(fpath, "wb") as f:
                f.write(payload)
            extracted.append(f"  picture {len(payload)} bytes -> {fname}")

    # Write all strings for this part into a single file
    if collected_strings:
        fname = f"{prefix}_strings.txt"
        fpath = os.path.join(output_dir, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write("\n\n---\n\n".join(collected_strings))
        extracted.append(
            f"  {len(collected_strings)} strings -> {fname}"
        )

    return extracted


# ---------------------------------------------------------------------------
# Package Parser
# ---------------------------------------------------------------------------

def parse_package(data, file_size):
    """Parse a Newton Package from raw bytes. Returns a dict with all metadata."""
    if len(data) < 52:
        raise ValueError(f"File too small ({len(data)} bytes, need at least 52)")

    sig = data[0:8]
    if sig not in (b"package0", b"package1"):
        raise ValueError(f"Bad signature: {sig!r} (expected 'package0' or 'package1')")

    pkg = {}
    pkg["signature"] = sig.decode("ascii")
    pkg["format_version"] = chr(sig[7])
    pkg["type"] = data[8:12].decode("ascii", errors="replace")
    pkg["flags"] = struct.unpack_from(">I", data, 12)[0]
    pkg["version"] = struct.unpack_from(">I", data, 16)[0]

    pkg["copyright_offset"] = struct.unpack_from(">H", data, 20)[0]
    pkg["copyright_length"] = struct.unpack_from(">H", data, 22)[0]
    pkg["name_offset"] = struct.unpack_from(">H", data, 24)[0]
    pkg["name_length"] = struct.unpack_from(">H", data, 26)[0]

    pkg["total_size"] = struct.unpack_from(">I", data, 28)[0]
    pkg["creation_date_raw"] = struct.unpack_from(">I", data, 32)[0]
    pkg["modification_date_raw"] = struct.unpack_from(">I", data, 36)[0]
    pkg["reserved"] = struct.unpack_from(">I", data, 40)[0]
    pkg["directory_size"] = struct.unpack_from(">I", data, 44)[0]
    pkg["num_parts"] = struct.unpack_from(">I", data, 48)[0]

    pkg["creation_date"] = newton_date_to_iso(pkg["creation_date_raw"])
    pkg["modification_date"] = newton_date_to_iso(pkg["modification_date_raw"])

    pkg["truncated"] = pkg["total_size"] > file_size

    # String data area starts after header + part entries
    str_area_start = 52 + pkg["num_parts"] * 32

    # Decode copyright string
    cr_abs = str_area_start + pkg["copyright_offset"]
    cr_end = cr_abs + pkg["copyright_length"]
    if cr_end <= len(data):
        pkg["copyright"] = decode_utf16be(data[cr_abs:cr_end])
    else:
        pkg["copyright"] = ""

    # Decode name string
    nm_abs = str_area_start + pkg["name_offset"]
    nm_end = nm_abs + pkg["name_length"]
    if nm_end <= len(data):
        pkg["name"] = decode_utf16be(data[nm_abs:nm_end])
    else:
        pkg["name"] = ""

    # Parse part directory entries
    parts = []
    for i in range(pkg["num_parts"]):
        pe_off = 52 + i * 32
        if pe_off + 32 > len(data):
            break

        part = {}
        part["index"] = i
        part["data_offset"] = struct.unpack_from(">I", data, pe_off)[0]
        part["data_size"] = struct.unpack_from(">I", data, pe_off + 4)[0]
        part["data_size2"] = struct.unpack_from(">I", data, pe_off + 8)[0]
        part["type"] = data[pe_off + 12 : pe_off + 16].decode("ascii", errors="replace")
        part["reserved1"] = struct.unpack_from(">I", data, pe_off + 16)[0]
        part["flags"] = struct.unpack_from(">I", data, pe_off + 20)[0]
        part["info_offset"] = struct.unpack_from(">H", data, pe_off + 24)[0]
        part["info_length"] = struct.unpack_from(">H", data, pe_off + 26)[0]
        part["reserved2"] = struct.unpack_from(">I", data, pe_off + 28)[0]

        # Decode info string (ASCII, not null-terminated)
        info_abs = str_area_start + part["info_offset"]
        info_end = info_abs + part["info_length"]
        if info_end <= len(data):
            raw_info = data[info_abs:info_end]
            part["info"] = raw_info.rstrip(b"\x00").decode("ascii", errors="replace")
            part["info_has_null"] = len(raw_info) > len(raw_info.rstrip(b"\x00"))
        else:
            part["info"] = ""
            part["info_has_null"] = False

        # Absolute position of part data in file
        part["_abs_offset"] = pkg["directory_size"] + part["data_offset"]

        parts.append(part)

    pkg["parts"] = parts

    # Capture the filler/padding area content
    max_str_end = pkg["copyright_offset"] + pkg["copyright_length"]
    candidate = pkg["name_offset"] + pkg["name_length"]
    if candidate > max_str_end:
        max_str_end = candidate
    for part in parts:
        candidate = part["info_offset"] + part["info_length"]
        if candidate > max_str_end:
            max_str_end = candidate

    filler_abs_start = str_area_start + max_str_end
    filler_abs_end = pkg["directory_size"]
    if filler_abs_start < filler_abs_end and filler_abs_end <= len(data):
        pkg["_filler_offset"] = filler_abs_start
        pkg["_filler_size"] = filler_abs_end - filler_abs_start
    else:
        pkg["_filler_offset"] = filler_abs_end
        pkg["_filler_size"] = 0

    return pkg


def flag_descriptions(flags):
    """Return human-readable flag descriptions."""
    descs = []
    if flags & 0x80000000:
        descs.append("auto-remove")
    if flags & 0x40000000:
        descs.append("copy-protect")
    if flags & 0x10000000:
        descs.append("no-compression")
    if flags & 0x08000000:
        descs.append("bit27")
    if flags & 0x04000000:
        descs.append("relocation")
    if flags & 0x02000000:
        descs.append("bit25")
    if not descs:
        descs.append("none")
    return ", ".join(descs)


def extract_package(input_path, output_dir, include_all=False):
    """Extract a Newton Package file to the output directory."""
    with open(input_path, "rb") as f:
        data = f.read()

    file_size = len(data)
    pkg = parse_package(data, file_size)

    os.makedirs(output_dir, exist_ok=True)

    # Print summary
    print(f"Newton Package: {os.path.basename(input_path)}")
    print(f"  Signature:     {pkg['signature']}")
    print(f"  Flags:         0x{pkg['flags']:08X} ({flag_descriptions(pkg['flags'])})")
    print(f"  Version:       {pkg['version']}")
    print(f"  Name:          {pkg['name']}")
    print(f"  Copyright:     {pkg['copyright']}")
    print(f"  Total size:    {pkg['total_size']} bytes", end="")
    if pkg["truncated"]:
        print(f" (TRUNCATED: file is {file_size} bytes)")
    else:
        print()
    print(f"  Created:       {pkg['creation_date'] or 'not set'}")
    print(f"  Modified:      {pkg['modification_date'] or 'not set'}")
    print(f"  Directory:     {pkg['directory_size']} bytes")
    print(f"  Parts:         {pkg['num_parts']}")
    print()

    # Optionally save raw binary data (directory region + part blobs)
    if include_all:
        dir_data = data[: pkg["directory_size"]]
        dir_path = os.path.join(output_dir, "directory.bin")
        with open(dir_path, "wb") as f:
            f.write(dir_data)
        print(f"  Wrote directory region: {dir_path} ({len(dir_data)} bytes)")

    # Extract each part and its content
    all_content = []
    for part in pkg["parts"]:
        i = part["index"]
        abs_off = part["_abs_offset"]
        size = part["data_size"]

        # Determine actual extractable size (handle truncated files)
        available = max(0, file_size - abs_off)
        extract_size = min(size, available)

        part_data = data[abs_off : abs_off + extract_size]

        # Raw part binary only with --all
        if include_all:
            part_filename = f"part{i}.{part['type'].strip()}"
            part_path = os.path.join(output_dir, part_filename)
            with open(part_path, "wb") as f:
                f.write(part_data)

        size2_str = ""
        if part["data_size2"] != 0 and part["data_size2"] != part["data_size"]:
            size2_str = f" (uncompressed: {part['data_size2']})"

        trunc_str = ""
        if extract_size < size:
            trunc_str = f" [TRUNCATED: got {extract_size} of {size}]"

        print(
            f"  Part {i}: type={part['type']!r} flags=0x{part['flags']:08X}"
            f" info={part['info']!r}"
        )
        print(f"    offset=0x{abs_off:X} size={size}{size2_str}{trunc_str}")
        if include_all:
            print(f"    -> {part_path}")

        # Extract human-viewable content from this part
        base_offset = abs_off
        content = extract_content_from_part(
            part_data, base_offset, output_dir, i
        )
        if content:
            all_content.extend(content)

    # Print extracted content summary
    if all_content:
        print(f"\n  Extracted content ({len(all_content)} items):")
        for desc in all_content:
            print(f"    {desc}")

    # Save metadata as JSON
    meta = {
        "source_file": os.path.basename(input_path),
        "source_size": file_size,
        "signature": pkg["signature"],
        "format_version": pkg["format_version"],
        "type": pkg["type"],
        "flags": f"0x{pkg['flags']:08X}",
        "flags_description": flag_descriptions(pkg["flags"]),
        "version": pkg["version"],
        "copyright": pkg["copyright"],
        "copyright_offset": pkg["copyright_offset"],
        "copyright_length": pkg["copyright_length"],
        "name": pkg["name"],
        "name_offset": pkg["name_offset"],
        "name_length": pkg["name_length"],
        "total_size": pkg["total_size"],
        "creation_date_raw": f"0x{pkg['creation_date_raw']:08X}",
        "creation_date": pkg["creation_date"],
        "modification_date_raw": f"0x{pkg['modification_date_raw']:08X}",
        "modification_date": pkg["modification_date"],
        "reserved": pkg["reserved"],
        "directory_size": pkg["directory_size"],
        "num_parts": pkg["num_parts"],
        "truncated": pkg["truncated"],
        "filler_offset": pkg["_filler_offset"],
        "filler_size": pkg["_filler_size"],
        "parts": [],
    }
    for part in pkg["parts"]:
        meta["parts"].append(
            {
                "index": part["index"],
                "type": part["type"],
                "data_offset": part["data_offset"],
                "data_size": part["data_size"],
                "data_size2": part["data_size2"],
                "flags": f"0x{part['flags']:08X}",
                "reserved1": part["reserved1"],
                "reserved2": part["reserved2"],
                "info_offset": part["info_offset"],
                "info_length": part["info_length"],
                "info": part["info"],
            }
        )

    meta_path = os.path.join(output_dir, "metadata.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(f"\n  Wrote metadata: {meta_path}")

    print(f"\nDone. Extracted {len(pkg['parts'])} part(s) to {output_dir}")
    if all_content:
        print(f"  + {len(all_content)} content items (images, sounds, strings)")


def main():
    args = sys.argv[1:]
    include_all = False

    if "--all" in args:
        include_all = True
        args.remove("--all")

    if len(args) != 2:
        print(f"Usage: {sys.argv[0]} [--all] <inputFile> <outputDir>", file=sys.stderr)
        sys.exit(1)

    input_path = args[0]
    output_dir = args[1]

    if not os.path.isfile(input_path):
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    extract_package(input_path, output_dir, include_all=include_all)


if __name__ == "__main__":
    main()

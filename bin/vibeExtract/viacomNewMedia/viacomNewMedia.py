#!/usr/bin/env python3
# Vibe coded by Claude

"""
Viacom New Media Sprite Archive Extractor
Extracts images from VNM sprite archive files (.VNM, .000) and
metadata from VNM game scene files.

Usage: unViacomNewMedia.py [--all] <inputFile> <outputDir>

Options:
  --all   Also output metadata JSON, palette files, unknown tables,
          and raw scene data (by default only images are extracted)
"""

import argparse
import struct
import sys
import os
import json

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow (PIL) is required. Install with: pip install Pillow", file=sys.stderr)
    sys.exit(1)

# Constants
VNM_SIGNATURE = b'VNM\x1a'
VNM_SIGNATURE_LE = 0x1A4D4E56
HEADER_SIZE = 40
IMAGE_HEADER_SIZE = 24
UNKNOWN_TABLE_SIZE = 1024  # 256 * 4 bytes
FLAG_GAME_SCENE = 0x80000000
IMAGE_TYPE_BITMAP = 0
IMAGE_TYPE_SPRITE = 1


def read_header(data):
    """Parse the 40-byte VNM file header."""
    if len(data) < HEADER_SIZE:
        raise ValueError("File too small for VNM header")
    if data[:4] != VNM_SIGNATURE:
        raise ValueError(f"Invalid signature: {data[:4].hex()} (expected {VNM_SIGNATURE.hex()})")

    fields = struct.unpack_from('<10I', data, 0)
    return {
        'signature': fields[0],
        'flags': fields[1],
        'data_size': fields[2],
        'field3': fields[3],  # palette_offset for sprites, canvas_width for games
        'field4': fields[4],  # unknown1_offset for sprites, canvas_height for games
        'field5': fields[5],  # unknown2_offset for sprites, num_layers for games
        'field6': fields[6],  # image_index_offset for both
        'field7': fields[7],  # palette_start for sprites, data_after_index for games
        'field8': fields[8],  # palette_size for sprites, 0 for games
        'field9': fields[9],  # image_count for sprites, varies for games
    }


def is_game_scene(header):
    """Check if the file is a game scene file (vs sprite archive)."""
    return (header['flags'] & FLAG_GAME_SCENE) != 0


def read_palette(data, header):
    """Read the VGA 6-bit palette and convert to 8-bit RGBA."""
    palette_offset = header['field3']
    palette_start = header['field7']
    palette_size = header['field8']

    palette = [(0, 0, 0, 0)] * 256  # default: transparent black

    for i in range(palette_size):
        off = palette_offset + i * 3
        if off + 2 >= len(data):
            break
        r6, g6, b6 = data[off], data[off + 1], data[off + 2]
        # Convert 6-bit VGA (0-63) to 8-bit (0-255)
        r8 = (r6 << 2) | (r6 >> 4)
        g8 = (g6 << 2) | (g6 >> 4)
        b8 = (b6 << 2) | (b6 >> 4)
        palette[palette_start + i] = (r8, g8, b8, 255)

    return palette


def read_unknown_tables(data, header):
    """Read the two 256-entry unknown lookup tables (1024 bytes each)."""
    unk1_offset = header['field4']
    unk2_offset = header['field5']

    unk1 = list(struct.unpack_from('<256I', data, unk1_offset))
    unk2 = list(struct.unpack_from('<256I', data, unk2_offset))

    return unk1, unk2


def read_image_index(data, header):
    """Read the image offset index array."""
    index_offset = header['field6']
    image_count = header['field9']

    offsets = []
    for i in range(image_count):
        off_pos = index_offset + i * 4
        if off_pos + 4 > len(data):
            break
        offsets.append(struct.unpack_from('<I', data, off_pos)[0])

    return offsets


def read_image_header(data, offset):
    """Read a 24-byte image header at the given offset."""
    if offset + IMAGE_HEADER_SIZE > len(data):
        return None

    fields = struct.unpack_from('<II ii ii', data, offset)
    return {
        'data_offset': fields[0],
        'type': fields[1],
        'width': fields[2],
        'height': fields[3],
        'x_pos': fields[4],
        'y_pos': fields[5],
    }


def decode_bitmap(data, img_header, palette):
    """Decode a bitmap image (type 0) - raw uncompressed pixel data."""
    w = img_header['width']
    h = img_header['height']
    data_off = img_header['data_offset']

    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    pixels = img.load()

    for y in range(h):
        for x in range(w):
            off = data_off + y * w + x
            if off >= len(data):
                return img
            pixels[x, y] = palette[data[off]]

    return img


def decode_sprite(data, img_header, palette):
    """Decode a sprite image (type 1) - RLE compressed with transparency.

    For narrow sprites (width < 256), uses escape-code RLE compression
    where byte values >= (0x100 - width) encode transparency runs.

    For wide sprites (width >= 256), the escape mechanism cannot work with
    single bytes, so rows are stored as raw pixel data accessed via the
    per-row offset table (effectively a bitmap with row pointers).
    """
    w = img_header['width']
    h = img_header['height']
    data_off = img_header['data_offset']

    # Read per-row offset table (h uint32 absolute file offsets)
    if data_off + h * 4 > len(data):
        return None
    row_offsets = struct.unpack_from(f'<{h}I', data, data_off)

    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    pixels = img.load()

    if w >= 256:
        # Wide sprite: raw pixel data per row (no RLE compression)
        for y in range(h):
            roff = row_offsets[y]
            if roff >= len(data):
                continue
            for x in range(w):
                if roff + x >= len(data):
                    break
                pixels[x, y] = palette[data[roff + x]]
        return img

    # Narrow sprite: escape-code RLE compression
    escape = 0x100 - w  # threshold: bytes >= escape are transparency run codes

    for y in range(h):
        roff = row_offsets[y]
        if roff >= len(data):
            continue

        j = w   # pixels remaining in this row
        r = 0   # byte read position within row data
        x = 0   # current pixel x position
        first_byte = True

        while j > 0:
            if roff + r >= len(data):
                break

            b = data[roff + r]
            r += 1

            if b >= escape:
                # Transparency run: length = 0x100 - byte_value
                run = 0x100 - b
                run = min(run, j)
                # Transparent pixels are already (0,0,0,0) from Image.new
                x += run
                j -= run
                if j > 0:
                    r += 1  # skip the "transparency color index" byte
                first_byte = False
            elif first_byte:
                # Non-escape byte at row start: row header byte, skip it
                first_byte = False
                continue
            else:
                # Literal pixel value (palette index)
                first_byte = False
                pixels[x, y] = palette[b]
                x += 1
                j -= 1

    return img


def extract_sprite_archive(data, header, output_dir, dump_all=False):
    """Extract all images from a sprite archive file."""
    palette = read_palette(data, header)
    image_offsets = read_image_index(data, header)

    if dump_all:
        # Save palette as raw binary
        pal_offset = header['field3']
        pal_size = header['field8']
        pal_data = data[pal_offset:pal_offset + pal_size * 3]
        with open(os.path.join(output_dir, 'palette.bin'), 'wb') as f:
            f.write(pal_data)

        # Save palette as human-readable text
        with open(os.path.join(output_dir, 'palette.txt'), 'w') as f:
            f.write(f"# VNM Palette: {pal_size} entries starting at index {header['field7']}\n")
            f.write(f"# Format: INDEX  R6 G6 B6  -> R8 G8 B8\n")
            pal_start = header['field7']
            for i in range(pal_size):
                off = pal_offset + i * 3
                if off + 2 >= len(data):
                    break
                r6, g6, b6 = data[off], data[off + 1], data[off + 2]
                r8, g8, b8 = palette[pal_start + i][:3]
                f.write(f"{pal_start + i:3d}  {r6:2d} {g6:2d} {b6:2d}  -> {r8:3d} {g8:3d} {b8:3d}\n")

        # Save unknown tables
        with open(os.path.join(output_dir, 'unknown_table1.bin'), 'wb') as f:
            f.write(data[header['field4']:header['field4'] + UNKNOWN_TABLE_SIZE])
        with open(os.path.join(output_dir, 'unknown_table2.bin'), 'wb') as f:
            f.write(data[header['field5']:header['field5'] + UNKNOWN_TABLE_SIZE])

    # Extract images
    extracted = 0
    skipped = 0
    errors = 0
    images_meta = []

    for i, off in enumerate(image_offsets):
        if off == 0:
            images_meta.append({'index': i, 'header_offset': '0x00000000', 'status': 'null_entry'})
            skipped += 1
            continue

        img_header = read_image_header(data, off)
        if img_header is None:
            images_meta.append({'index': i, 'header_offset': '0x{:08X}'.format(off), 'status': 'header_out_of_bounds'})
            skipped += 1
            continue

        w, h = img_header['width'], img_header['height']

        img_info = {
            'index': i,
            'header_offset': '0x{:08X}'.format(off),
            'data_offset': '0x{:08X}'.format(img_header['data_offset']),
            'type': 'bitmap' if img_header['type'] == IMAGE_TYPE_BITMAP else 'sprite',
            'type_id': img_header['type'],
            'width': w, 'height': h,
            'x_pos': img_header['x_pos'], 'y_pos': img_header['y_pos'],
        }

        if w <= 0 or h <= 0 or w > 4096 or h > 4096:
            img_info['status'] = 'invalid_dimensions'
            images_meta.append(img_info)
            skipped += 1
            continue

        if img_header['data_offset'] >= len(data):
            img_info['status'] = 'data_out_of_bounds'
            images_meta.append(img_info)
            skipped += 1
            continue

        try:
            if img_header['type'] == IMAGE_TYPE_BITMAP:
                img = decode_bitmap(data, img_header, palette)
            elif img_header['type'] == IMAGE_TYPE_SPRITE:
                img = decode_sprite(data, img_header, palette)
                if img is None:
                    img_info['status'] = 'decode_failed_truncated'
                    images_meta.append(img_info)
                    skipped += 1
                    continue
            else:
                img_info['status'] = f'unknown_type_{img_header["type"]}'
                images_meta.append(img_info)
                skipped += 1
                continue

            filename = f'img_{i:04d}.png'
            img.save(os.path.join(output_dir, filename))
            img_info['status'] = 'extracted'
            img_info['filename'] = filename
            images_meta.append(img_info)
            extracted += 1

        except Exception as e:
            img_info['status'] = f'error: {str(e)}'
            images_meta.append(img_info)
            errors += 1

    # Write metadata.json if --all, or if no images were extracted
    if dump_all or extracted == 0:
        metadata = {
            'header': {
                'signature': '0x{:08X}'.format(header['signature']),
                'flags': '0x{:08X}'.format(header['flags']),
                'data_size': header['data_size'],
                'palette_offset': '0x{:04X}'.format(header['field3']),
                'unknown1_offset': '0x{:04X}'.format(header['field4']),
                'unknown2_offset': '0x{:04X}'.format(header['field5']),
                'image_index_offset': '0x{:04X}'.format(header['field6']),
                'palette_start': header['field7'],
                'palette_size': header['field8'],
                'image_count': header['field9'],
            },
            'file_size': len(data),
            'truncated': len(data) < header['data_size'],
            'images': images_meta,
            'summary': {
                'extracted': extracted, 'skipped': skipped,
                'errors': errors, 'total': len(image_offsets),
            },
        }
        with open(os.path.join(output_dir, 'metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)

    return extracted, skipped, errors


def extract_game_scene(data, header, output_dir, dump_all=False):
    """Extract metadata from a game scene file."""
    canvas_width = header['field3']
    canvas_height = header['field4']
    num_layers = header['field5']
    img_idx_offset = header['field6']
    after_idx_offset = header['field7']

    # Read layer sprite indices
    layer_indices = []
    for i in range(num_layers):
        off = img_idx_offset + i * 4
        if off + 4 <= len(data):
            layer_indices.append(struct.unpack_from('<I', data, off)[0])

    # Search for embedded ASCII strings
    strings_found = []
    i = after_idx_offset
    while i < len(data):
        if 32 <= data[i] <= 126:
            start = i
            while i < len(data) and 32 <= data[i] <= 126:
                i += 1
            s = data[start:i].decode('ascii')
            if len(s) >= 3:
                strings_found.append({'offset': '0x{:04X}'.format(start), 'text': s})
        else:
            i += 1

    # Identify sentinel pairs
    sentinel_offsets = []
    for i in range(HEADER_SIZE, min(len(data) - 7, 0x200)):
        if struct.unpack_from('<II', data, i) == (0xFFFFFFFF, 0xFFFFFFFF):
            sentinel_offsets.append('0x{:04X}'.format(i))

    scene_data_size = img_idx_offset - HEADER_SIZE
    post_data_size = len(data) - after_idx_offset

    if dump_all:
        # Extract raw data blocks
        if scene_data_size > 0:
            with open(os.path.join(output_dir, 'scene_data.bin'), 'wb') as f:
                f.write(data[HEADER_SIZE:img_idx_offset])
        if post_data_size > 0:
            with open(os.path.join(output_dir, 'post_index_data.bin'), 'wb') as f:
                f.write(data[after_idx_offset:])

    # Always write metadata.json for game scenes (no images to extract)
    metadata = {
        'file_type': 'game_scene',
        'header': {
            'signature': '0x{:08X}'.format(header['signature']),
            'flags': '0x{:08X}'.format(header['flags']),
            'data_size': header['data_size'],
            'canvas_width': canvas_width,
            'canvas_height': canvas_height,
            'num_layers': num_layers,
            'image_index_offset': '0x{:04X}'.format(img_idx_offset),
            'after_index_offset': '0x{:04X}'.format(after_idx_offset),
            'field8': header['field8'],
            'field9': '0x{:08X}'.format(header['field9']),
        },
        'file_size': len(data),
        'layer_sprite_indices': layer_indices,
        'sentinel_offsets': sentinel_offsets,
        'embedded_strings': strings_found,
        'scene_data_size': scene_data_size,
        'post_index_data_size': post_data_size,
    }
    with open(os.path.join(output_dir, 'metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=2)

    return {
        'layer_sprite_indices': layer_indices,
        'embedded_strings': strings_found,
    }


def main():
    parser = argparse.ArgumentParser(
        description='Viacom New Media Sprite Archive Extractor')
    parser.add_argument('inputFile', help='Input VNM/000 file')
    parser.add_argument('outputDir', help='Output directory')
    parser.add_argument('--all', action='store_true',
                        help='Also output metadata JSON, palette files, '
                             'unknown tables, and raw scene data')
    args = parser.parse_args()

    if not os.path.isfile(args.inputFile):
        print(f"ERROR: Input file not found: {args.inputFile}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(args.outputDir, exist_ok=True)

    with open(args.inputFile, 'rb') as f:
        data = f.read()

    header = read_header(data)
    basename = os.path.basename(args.inputFile)

    if is_game_scene(header):
        print(f"File: {basename} (Game Scene)")
        print(f"  Canvas: {header['field3']}x{header['field4']}")
        print(f"  Layers: {header['field5']}")

        meta = extract_game_scene(data, header, args.outputDir, dump_all=args.all)

        if meta['embedded_strings']:
            print(f"  Strings: {[s['text'] for s in meta['embedded_strings']]}")
        print(f"  Layer sprite indices: {meta['layer_sprite_indices']}")
        if args.all:
            print(f"  Extracted scene data to: {args.outputDir}/")
        else:
            print(f"  (no extractable images; use --all for raw scene data)")
    else:
        print(f"File: {basename} (Sprite Archive)")
        pal_start = header['field7']
        pal_size = header['field8']
        img_count = header['field9']
        print(f"  Palette: {pal_size} colors (indices {pal_start}-{pal_start + pal_size - 1})")
        print(f"  Images: {img_count}")

        if len(data) < header['data_size']:
            print(f"  WARNING: File truncated ({len(data)} bytes, expected {header['data_size']})")

        extracted, skipped, errors = extract_sprite_archive(
            data, header, args.outputDir, dump_all=args.all)

        print(f"  Extracted: {extracted} images")
        if skipped > 0:
            print(f"  Skipped: {skipped}")
        if errors > 0:
            print(f"  Errors: {errors}")
        print(f"  Output: {args.outputDir}/")


if __name__ == '__main__':
    main()

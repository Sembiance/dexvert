#!/usr/bin/env python3
# Vibe coded by Claude

import struct
import sys
import os
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow is required. Install with: pip install Pillow", file=sys.stderr)
    sys.exit(1)

# AoE2 palette (Age of Kings / The Conquerors)
PALETTE_AOE2 = [
    (0,0,0), (0,74,161), (0,97,155), (0,74,187), (0,84,176), (0,90,184), (0,110,176), (0,110,187),
    (180,255,180), (0,98,210), (0,0,0), (47,47,47), (200,216,255), (87,87,87), (37,16,6), (47,26,17),
    (0,0,82), (0,21,130), (19,49,161), (48,93,182), (74,121,208), (110,166,235), (151,206,255), (205,250,255),
    (64,43,23), (67,51,27), (70,32,6), (75,57,42), (84,64,43), (87,69,37), (87,57,27), (94,74,48),
    (65,0,0), (105,11,0), (160,21,0), (230,11,0), (255,0,0), (255,100,100), (255,160,160), (255,220,220),
    (97,77,67), (103,58,21), (113,75,51), (113,75,13), (115,105,84), (125,97,72), (125,74,0), (129,116,95),
    (0,0,0), (0,7,0), (0,32,0), (0,59,0), (0,87,0), (0,114,0), (0,141,0), (0,169,0),
    (134,126,118), (135,64,0), (136,108,79), (144,100,12), (146,125,105), (153,106,55), (159,121,88), (166,74,0),
    (80,51,26), (140,78,9), (191,123,0), (255,199,0), (255,247,37), (255,255,97), (255,255,166), (255,255,227),
    (167,135,102), (172,144,115), (175,126,36), (175,151,128), (185,151,146), (186,166,135), (187,84,0), (187,156,125),
    (110,23,0), (150,36,0), (210,55,0), (255,80,0), (255,130,1), (255,180,21), (255,210,75), (255,235,160),
    (189,150,111), (191,169,115), (195,174,156), (196,170,146), (196,128,88), (196,166,135), (197,187,176), (204,160,36),
    (0,16,16), (0,37,41), (0,80,80), (0,120,115), (0,172,150), (38,223,170), (109,252,191), (186,255,222),
    (206,169,133), (207,105,12), (207,176,156), (228,162,82), (215,186,155), (216,162,121), (217,114,24), (223,234,255),
    (47,0,46), (79,0,75), (133,12,121), (170,47,155), (211,58,201), (241,108,232), (255,169,255), (255,210,255),
    (218,156,105), (222,177,136), (225,177,90), (226,195,170), (232,180,120), (235,202,181), (235,216,190), (237,199,165),
    (28,28,28), (67,67,67), (106,106,106), (145,145,145), (185,185,185), (223,223,223), (247,247,247), (255,255,255),
    (247,211,191), (248,201,138), (255,206,157), (255,225,201), (255,238,217), (255,226,161), (216,223,255), (255,255,243),
    (24,24,0), (37,37,17), (27,47,0), (47,57,17), (67,77,7), (77,77,47), (44,77,3), (94,84,53),
    (95,97,39), (97,97,67), (67,97,29), (106,115,57), (116,115,75), (87,116,7), (118,130,65), (130,136,77),
    (138,139,87), (148,155,100), (156,156,139), (128,157,84), (149,166,97), (175,165,106), (176,176,159), (146,176,67),
    (194,190,148), (165,196,108), (166,196,77), (206,187,128), (206,204,155), (204,217,77), (221,218,166), (196,226,116),
    (243,170,92), (3,28,0), (7,38,0), (7,47,7), (19,48,0), (27,57,17), (47,57,47), (28,62,0),
    (14,68,14), (41,69,28), (33,73,18), (47,87,47), (77,97,57), (67,97,67), (87,116,77), (70,119,48),
    (189,209,253), (106,136,97), (196,236,166), (23,53,33), (43,84,64), (37,116,57), (23,43,53), (2,33,53),
    (2,23,53), (33,64,64), (0,34,97), (0,51,115), (43,64,74), (0,43,74), (4,6,9), (0,123,189),
    (64,84,84), (0,115,207), (23,23,74), (12,23,64), (255,177,98), (0,64,125), (2,23,84), (0,138,186),
    (64,105,105), (0,146,197), (94,105,105), (0,74,125), (0,125,207), (95,133,65), (84,115,125), (64,105,125),
    (0,64,146), (0,53,135), (115,156,156), (84,146,176), (146,176,187), (255,201,121), (105,166,197), (125,197,217),
    (156,197,217), (109,126,33), (113,153,36), (21,118,21), (51,151,39), (70,181,59), (89,223,89), (131,245,120),
    (152,192,240), (0,255,0), (0,0,255), (255,255,0), (255,217,0), (240,240,255), (240,247,255), (247,247,255),
    (247,255,255), (85,119,52), (129,151,49), (0,255,255), (255,0,255), (0,139,210), (0,160,243), (255,255,255),
]

# AoE1 palette 50509 from Interfac.drs (grassland/temperate variant)
PALETTE_AOE1 = [
    (0,0,0), (128,0,0), (0,128,0), (128,128,0), (0,0,128), (128,0,128), (0,128,128), (192,192,192),
    (192,220,192), (166,202,240), (16,8,8), (0,8,0), (0,8,8), (0,16,8), (8,0,0), (8,8,0),
    (8,8,8), (8,16,8), (16,0,0), (16,8,0), (16,8,8), (16,16,0), (16,16,8), (16,16,16),
    (24,0,0), (24,8,0), (24,8,8), (24,16,0), (24,16,8), (33,0,0), (33,8,0), (41,0,0),
    (37,12,0), (41,16,0), (33,16,8), (41,16,8), (24,16,16), (41,16,16), (33,24,0), (41,24,0),
    (10,26,12), (16,24,16), (16,33,16), (24,24,8), (24,24,16), (24,24,24), (24,33,16), (33,24,8),
    (33,33,8), (41,24,8), (41,33,8), (33,24,16), (33,28,20), (41,24,16), (41,33,16), (16,41,24),
    (24,33,24), (33,33,24), (41,41,8), (33,41,16), (33,45,24), (41,41,16), (41,33,24), (33,33,33),
    (41,33,33), (33,41,33), (41,41,28), (41,45,32), (34,57,39), (49,15,5), (49,33,4), (49,41,8),
    (49,33,20), (57,12,2), (49,41,20), (72,25,5), (75,41,12), (57,49,8), (53,49,20), (53,41,32),
    (66,49,8), (61,45,24), (66,49,16), (79,48,10), (49,49,33), (57,57,24), (66,57,16), (71,54,21),
    (74,57,24), (85,56,12), (90,53,24), (49,49,41), (49,49,49), (49,57,33), (57,49,33), (57,51,41),
    (66,53,33), (74,49,33), (49,57,41), (57,57,41), (57,65,47), (70,61,33), (74,66,28), (70,57,41),
    (66,65,43), (87,66,13), (87,68,24), (82,57,33), (82,66,33), (76,68,41), (82,74,33), (88,67,36),
    (90,74,41), (66,57,57), (66,66,49), (66,66,57), (66,66,66), (66,74,49), (74,66,49), (76,66,57),
    (70,78,53), (74,74,57), (74,86,57), (84,76,49), (82,78,57), (82,90,57), (82,74,63), (80,80,72),
    (105,49,11), (107,74,36), (106,82,29), (102,82,43), (103,89,38), (105,86,50), (100,86,57), (92,82,72),
    (90,90,66), (99,94,61), (112,97,51), (107,103,61), (97,92,76), (111,103,66), (108,102,77), (138,66,13),
    (139,85,21), (127,90,28), (154,90,23), (131,95,37), (148,94,32), (168,96,28), (137,104,39), (133,103,55),
    (115,107,74), (125,107,75), (154,107,36), (152,105,51), (176,109,32), (121,115,65), (132,117,68), (123,117,82),
    (145,117,57), (157,123,56), (136,121,76), (150,130,74), (173,119,39), (175,129,40), (174,118,54), (175,133,53),
    (167,124,67), (181,127,61), (171,137,71), (181,137,65), (189,124,43), (188,141,55), (183,142,71), (189,144,70),
    (200,131,41), (218,141,43), (193,144,70), (215,144,63), (198,157,62), (198,152,74), (206,148,74), (206,156,74),
    (214,159,59), (236,161,59), (243,177,68), (96,93,90), (99,99,99), (116,105,93), (142,110,93), (141,126,90),
    (138,134,93), (149,138,91), (161,137,84), (160,144,93), (169,148,91), (181,144,86), (177,154,92), (192,145,82),
    (188,158,92), (202,152,82), (206,156,82), (198,165,82), (200,158,92), (206,165,82), (212,160,86), (214,165,90),
    (225,162,82), (205,171,95), (214,173,94), (218,175,90), (222,173,94), (235,173,86), (230,182,86), (250,193,86),
    (122,118,111), (132,132,123), (140,133,116), (140,140,132), (151,145,124), (170,153,119), (191,162,107), (187,169,126),
    (216,176,104), (209,176,122), (235,181,99), (237,183,107), (216,189,126), (245,194,103), (243,212,129), (176,172,165),
    (189,189,181), (198,189,170), (198,198,189), (204,195,174), (223,209,170), (216,212,209), (232,230,227), (251,219,161),
    (253,233,167), (255,251,164), (251,247,210), (247,247,239), (247,247,247), (255,255,255), (255,251,240), (160,160,164),
    (128,128,128), (255,0,0), (0,255,0), (255,255,0), (0,0,255), (255,0,255), (0,255,255), (255,255,255),
]

PALETTES = {"aoe2": PALETTE_AOE2, "aoe1": PALETTE_AOE1}

# Precompute indices where AoE2 palette produces colors that never appear in natural game art
# (neon magenta, pure green, bright teal) or where AoE2 gives blue but AoE1 gives warm brown
_AOE1_SIGNAL_INDICES = set()
for _i in range(256):
    _r2, _g2, _b2 = PALETTE_AOE2[_i]
    _r1, _g1, _b1 = PALETTE_AOE1[_i]
    _is_neon = ((_r2 > 120 and _b2 > 80 and _g2 < 60 and (_r2 + _b2) > 200) or
                (_g2 > 150 and _r2 < 50 and _b2 < 50) or
                (_g2 > 170 and _b2 > 140 and _r2 < 50))
    _aoe2_blue = (_b2 > 80 and _b2 > _r2 + 30 and _b2 > _g2) or (_g2 > 100 and _b2 > 100 and _r2 < 60)
    _aoe1_warm = _r1 > 60 and _r1 >= _b1 and (_r1 + _g1) > (_b1 * 2 + 40)
    if _is_neon or (_aoe2_blue and _aoe1_warm):
        _AOE1_SIGNAL_INDICES.add(_i)

HEADER_SIZE = 32
FRAME_INFO_SIZE = 32
PLAYER_NUMBER = 0


def read_header(data):
    if len(data) < HEADER_SIZE:
        return None
    version = data[0:4]
    if version != b'2.0N':
        return None
    num_frames = struct.unpack_from('<I', data, 4)[0]
    comment = data[8:32]
    if len(data) < HEADER_SIZE + num_frames * FRAME_INFO_SIZE:
        return None
    return {"version": version, "num_frames": num_frames, "comment": comment}


def read_frame_info(data, frame_index):
    off = HEADER_SIZE + frame_index * FRAME_INFO_SIZE
    fields = struct.unpack_from('<IIIIiiII', data, off)
    return {
        "cmd_table_offset": fields[0],
        "outline_table_offset": fields[1],
        "palette_offset": fields[2],
        "properties": fields[3],
        "width": fields[4],
        "height": fields[5],
        "hotspot_x": fields[6],
        "hotspot_y": fields[7],
    }


def detect_palette(data, header):
    """Auto-detect palette by checking if AoE2 palette would produce unnatural colors.
    Scans palette index usage from color commands and checks what percentage of pixels
    would map to neon/blue colors that indicate an AoE1 file rendered with wrong palette."""
    usage = [0] * 256
    for fi in range(header["num_frames"]):
        frame_info = read_frame_info(data, fi)
        width, height = frame_info["width"], frame_info["height"]
        outline_off = frame_info["outline_table_offset"]
        cmd_table_off = frame_info["cmd_table_offset"]
        for row in range(height):
            left, right = struct.unpack_from('<HH', data, outline_off + row * 4)
            if (left == 0x8000) or (left + right >= width):
                continue
            pos = struct.unpack_from('<I', data, cmd_table_off + row * 4)[0]
            while pos < len(data):
                byte = data[pos]
                if byte == 0x0F: break
                elif byte == 0x4E: pos += 1
                elif byte == 0x5E: pos += 2
                elif byte & 0x0F == 0x0E: pos += 2
                elif byte & 0x0F == 0x02:
                    c = (byte >> 4) * 256 + data[pos + 1]
                    for i in range(c): usage[data[pos + 2 + i]] += 1
                    pos += 2 + c
                elif byte & 0x0F == 0x03: pos += 2
                elif byte & 0x0F == 0x06:
                    c = byte >> 4
                    if c == 0: c = data[pos + 1]; pos += 2 + c
                    else: pos += 1 + c
                elif byte & 0x0F == 0x07:
                    c = byte >> 4
                    if c == 0: usage[data[pos + 2]] += c; pos += 3
                    else: usage[data[pos + 1]] += c; pos += 2
                elif byte & 0x0F == 0x0A:
                    c = byte >> 4
                    if c == 0: pos += 3
                    else: pos += 2
                elif byte & 0x0F == 0x0B:
                    c = byte >> 4
                    if c == 0: pos += 2
                    else: pos += 1
                elif byte & 0x03 == 0x00:
                    c = byte >> 2
                    for i in range(c): usage[data[pos + 1 + i]] += 1
                    pos += 1 + c
                elif byte & 0x03 == 0x01:
                    c = byte >> 2
                    if c == 0: pos += 2
                    else: pos += 1
                else: break
    total = sum(usage)
    if total == 0:
        return PALETTE_AOE2
    signal = sum(usage[i] for i in _AOE1_SIGNAL_INDICES)
    if signal / total > 0.004:
        return PALETTE_AOE1
    return PALETTE_AOE2


def decode_frame(data, frame_info, palette):
    width = frame_info["width"]
    height = frame_info["height"]
    outline_off = frame_info["outline_table_offset"]
    cmd_table_off = frame_info["cmd_table_offset"]

    pixels = [(0, 0, 0, 0)] * (width * height)

    for row in range(height):
        left, right = struct.unpack_from('<HH', data, outline_off + row * 4)

        is_transparent = (left == 0x8000) or (left + right >= width)
        if is_transparent:
            continue

        row_cmd_offset = struct.unpack_from('<I', data, cmd_table_off + row * 4)[0]
        pos = row_cmd_offset
        x = left

        while pos < len(data):
            byte = data[pos]

            if byte == 0x0F:
                pos += 1
                break

            elif byte == 0x4E:
                r, g, b = palette[PLAYER_NUMBER * 16 + 16 + 4]
                pixels[row * width + x] = (r, g, b, 255)
                x += 1
                pos += 1

            elif byte == 0x5E:
                count = data[pos + 1]
                r, g, b = palette[PLAYER_NUMBER * 16 + 16 + 4]
                for i in range(count):
                    pixels[row * width + x] = (r, g, b, 255)
                    x += 1
                pos += 2

            elif byte & 0x0F == 0x0E:
                count = data[pos + 1]
                for i in range(count):
                    pixels[row * width + x] = (0, 0, 0, 128)
                    x += 1
                pos += 2

            elif byte & 0x0F == 0x02:
                count = (byte >> 4) * 256 + data[pos + 1]
                for i in range(count):
                    idx = data[pos + 2 + i]
                    r, g, b = palette[idx]
                    pixels[row * width + x] = (r, g, b, 255)
                    x += 1
                pos += 2 + count

            elif byte & 0x0F == 0x03:
                count = (byte >> 4) * 256 + data[pos + 1]
                x += count
                pos += 2

            elif byte & 0x0F == 0x06:
                count = byte >> 4
                if count == 0:
                    count = data[pos + 1]
                    base = pos + 2
                    pos += 2 + count
                else:
                    base = pos + 1
                    pos += 1 + count
                for i in range(count):
                    pc_idx = data[base + i]
                    pal_idx = PLAYER_NUMBER * 16 + 16 + pc_idx
                    if pal_idx < 256:
                        r, g, b = palette[pal_idx]
                    else:
                        r, g, b = palette[pc_idx]
                    pixels[row * width + x] = (r, g, b, 255)
                    x += 1

            elif byte & 0x0F == 0x07:
                count = byte >> 4
                if count == 0:
                    count = data[pos + 1]
                    color_idx = data[pos + 2]
                    pos += 3
                else:
                    color_idx = data[pos + 1]
                    pos += 2
                r, g, b = palette[color_idx]
                for i in range(count):
                    pixels[row * width + x] = (r, g, b, 255)
                    x += 1

            elif byte & 0x0F == 0x0A:
                count = byte >> 4
                if count == 0:
                    count = data[pos + 1]
                    pc_idx = data[pos + 2]
                    pos += 3
                else:
                    pc_idx = data[pos + 1]
                    pos += 2
                pal_idx = PLAYER_NUMBER * 16 + 16 + pc_idx
                if pal_idx < 256:
                    r, g, b = palette[pal_idx]
                else:
                    r, g, b = palette[pc_idx]
                for i in range(count):
                    pixels[row * width + x] = (r, g, b, 255)
                    x += 1

            elif byte & 0x0F == 0x0B:
                count = byte >> 4
                if count == 0:
                    count = data[pos + 1]
                    pos += 2
                else:
                    pos += 1
                for i in range(count):
                    pixels[row * width + x] = (0, 0, 0, 128)
                    x += 1

            elif byte & 0x03 == 0x00:
                count = byte >> 2
                for i in range(count):
                    idx = data[pos + 1 + i]
                    r, g, b = palette[idx]
                    pixels[row * width + x] = (r, g, b, 255)
                    x += 1
                pos += 1 + count

            elif byte & 0x03 == 0x01:
                count = byte >> 2
                if count == 0:
                    count = data[pos + 1]
                    pos += 2
                else:
                    pos += 1
                x += count

            else:
                raise ValueError(f"Unknown command byte 0x{byte:02x} at offset {pos}")

    return pixels


def convert_slp(input_file, output_dir, palette_name=None):
    with open(input_file, 'rb') as f:
        data = f.read()

    header = read_header(data)
    if header is None:
        print(f"ERROR: {input_file} is not a valid SLP file", file=sys.stderr)
        sys.exit(1)

    if palette_name:
        palette = PALETTES[palette_name]
    else:
        palette = detect_palette(data, header)

    os.makedirs(output_dir, exist_ok=True)
    base_name = Path(input_file).stem

    for fi in range(header["num_frames"]):
        frame_info = read_frame_info(data, fi)
        width = frame_info["width"]
        height = frame_info["height"]

        pixels = decode_frame(data, frame_info, palette)

        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        img.putdata(pixels)

        out_path = os.path.join(output_dir, f"{base_name}_frame{fi:04d}.png")
        img.save(out_path)
        print(f"  Saved {out_path} ({width}x{height})")


def main():
    palette_name = None
    args = sys.argv[1:]

    if args and args[0] == "--palette":
        if len(args) < 2 or args[1] not in PALETTES:
            print(f"ERROR: --palette requires one of: {', '.join(PALETTES.keys())}", file=sys.stderr)
            sys.exit(1)
        palette_name = args[1]
        args = args[2:]

    if len(args) != 2:
        print(f"Usage: {sys.argv[0]} [--palette aoe1|aoe2] <inputFile> <outputDir>", file=sys.stderr)
        sys.exit(1)

    input_file = args[0]
    output_dir = args[1]

    if not os.path.isfile(input_file):
        print(f"ERROR: Input file not found: {input_file}", file=sys.stderr)
        sys.exit(1)

    convert_slp(input_file, output_dir, palette_name)


if __name__ == "__main__":
    main()

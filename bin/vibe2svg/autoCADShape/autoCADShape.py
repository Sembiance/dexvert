#!/usr/bin/env python3
# Vibe coded by Claude

"""AutoCAD compiled shape file (.SHX) to SVG converter.

Supports all four SHX format variants:
  - shapes 1.0 / 1.1  (standard fonts and shape libraries)
  - unifont 1.0        (Unicode fonts)
  - bigfont 1.0        (CJK double-byte fonts)
"""

import sys
import os
import struct
import math

HEADERS = {
    b"AutoCAD-86 shapes 1.0\r\n\x1a": "shapes1.0",
    b"AutoCAD-86 shapes 1.1\r\n\x1a": "shapes1.1",
    b"AutoCAD-86 unifont 1.0\r\n\x1a": "unifont",
    b"AutoCAD-86 bigfont 1.0\r\n\x1a": "bigfont",
}

DIRECTION_VECTORS = [
    (+1.0, 0.0),   # 0: E
    (+1.0, +0.5),  # 1: ENE
    (+1.0, +1.0),  # 2: NE
    (+0.5, +1.0),  # 3: NNE
    (0.0, +1.0),   # 4: N
    (-0.5, +1.0),  # 5: NNW
    (-1.0, +1.0),  # 6: NW
    (-1.0, +0.5),  # 7: WNW
    (-1.0, 0.0),   # 8: W
    (-1.0, -0.5),  # 9: WSW
    (-1.0, -1.0),  # A: SW
    (-0.5, -1.0),  # B: SSW
    (0.0, -1.0),   # C: S
    (+0.5, -1.0),  # D: SSE
    (+1.0, -1.0),  # E: SE
    (+1.0, -0.5),  # F: ESE
]


def signed_byte(b):
    return b if b < 128 else b - 256


class ShapeEntry:
    __slots__ = ("number", "name", "data")

    def __init__(self, number, name, data):
        self.number = number
        self.name = name
        self.data = data


class SHXFile:
    def __init__(self):
        self.format = ""
        self.shapes = {}
        self.font_name = ""
        self.above = 0
        self.below = 0
        self.modes = 0
        self.is_font = False
        self.subshape_bytes = 1


def _detect_header(raw):
    for header_bytes, fmt in HEADERS.items():
        hlen = len(header_bytes)
        if len(raw) >= hlen and raw[:hlen] == header_bytes:
            return fmt, hlen
    return None, 0


def _extract_shape(block):
    null_idx = block.find(b"\x00")
    if null_idx == -1:
        return "", block
    name = block[:null_idx].decode("ascii", errors="replace")
    return name, block[null_idx + 1:]


def _parse_shapes(raw, hdr_len):
    shx = SHXFile()
    shx.subshape_bytes = 1

    if hdr_len + 6 > len(raw):
        return None

    start, max_shape, count = struct.unpack_from("<HHH", raw, hdr_len)

    index_end = hdr_len + 6 + count * 4
    if index_end > len(raw):
        return None

    index = []
    for i in range(count):
        off = hdr_len + 6 + i * 4
        snum, slen = struct.unpack_from("<HH", raw, off)
        index.append((snum, slen))

    pos = index_end
    for snum, slen in index:
        if pos + slen > len(raw):
            break

        block = raw[pos:pos + slen]
        pos += slen

        name, spec = _extract_shape(block)

        if snum == 0 and start == 0:
            shx.font_name = name
            shx.is_font = True
            if len(spec) >= 3:
                shx.above = spec[0]
                shx.below = spec[1]
                shx.modes = spec[2]
        else:
            shx.shapes[snum] = ShapeEntry(snum, name, spec)

    return shx


def _parse_unifont(raw, hdr_len):
    shx = SHXFile()
    shx.subshape_bytes = 2

    if hdr_len + 6 > len(raw):
        return None

    num_shapes, _reserved, defbytes = struct.unpack_from("<HHH", raw, hdr_len)

    pos = hdr_len + 6
    if pos + defbytes > len(raw):
        return None

    desc_block = raw[pos:pos + defbytes]
    null_idx = desc_block.find(b"\x00")
    if null_idx >= 0:
        shx.font_name = desc_block[:null_idx].decode("ascii", errors="replace")
        params = desc_block[null_idx + 1:]
        if len(params) >= 3:
            shx.above = params[0]
            shx.below = params[1]
            shx.modes = params[2]
    shx.is_font = True
    pos += defbytes

    for _ in range(num_shapes - 1):
        if pos + 4 > len(raw):
            break
        snum = struct.unpack_from("<H", raw, pos)[0]
        slen = struct.unpack_from("<H", raw, pos + 2)[0]
        pos += 4
        if pos + slen > len(raw):
            break
        block = raw[pos:pos + slen]
        pos += slen
        name, spec = _extract_shape(block)
        shx.shapes[snum] = ShapeEntry(snum, name, spec)

    return shx


def _parse_bigfont(raw, hdr_len):
    shx = SHXFile()
    shx.subshape_bytes = 2

    if hdr_len + 6 > len(raw):
        return None

    _entry_size, num_entries, num_ranges = struct.unpack_from("<HHH", raw, hdr_len)
    pos = hdr_len + 6

    range_bytes = num_ranges * 4
    if pos + range_bytes > len(raw):
        return None
    pos += range_bytes

    if pos + 2 > len(raw):
        return None
    pos += 2

    if pos + 6 > len(raw):
        return None
    shx.above = raw[pos]
    shx.below = raw[pos + 1]
    shx.modes = struct.unpack_from("<H", raw, pos + 4)[0]
    pos += 6

    index_bytes = num_entries * 8
    if pos + index_bytes > len(raw):
        return None

    entries = []
    for i in range(num_entries):
        off = pos + i * 8
        cb0, cb1 = raw[off], raw[off + 1]
        dlen = struct.unpack_from("<H", raw, off + 2)[0]
        doff = struct.unpack_from("<I", raw, off + 4)[0]

        if cb0 == 0 and cb1 == 0 and dlen == 0 and doff == 0:
            continue
        code = cb0 * 256 + cb1
        entries.append((code, dlen, doff))
    pos += index_bytes

    desc_end = raw.find(b"\x00", pos)
    if desc_end > pos:
        shx.font_name = raw[pos:desc_end].decode("ascii", errors="replace")
    shx.is_font = True

    for code, dlen, doff in entries:
        if doff == 0 or dlen == 0:
            continue
        if doff + dlen > len(raw):
            continue
        block = raw[doff:doff + dlen]
        name, spec = _extract_shape(block)
        shx.shapes[code] = ShapeEntry(code, name, spec)

    return shx


def parse_shx(filepath):
    with open(filepath, "rb") as f:
        raw = f.read()

    fmt, hdr_len = _detect_header(raw)
    if fmt is None:
        return None

    if fmt.startswith("shapes"):
        shx = _parse_shapes(raw, hdr_len)
    elif fmt == "unifont":
        shx = _parse_unifont(raw, hdr_len)
    elif fmt == "bigfont":
        shx = _parse_bigfont(raw, hdr_len)
    else:
        return None

    if shx is not None:
        shx.format = fmt

    return shx


class Renderer:
    def __init__(self, shapes, subshape_bytes=1):
        self.shapes = shapes
        self.subshape_bytes = subshape_bytes

    def render(self, shape_num):
        if shape_num not in self.shapes:
            return None
        self.x = 0.0
        self.y = 0.0
        self.pen_down = True
        self.need_move = True
        self.scale = 1.0
        self.stack = []
        self.path_parts = []
        self.drawn_points = []
        self.arc_radii = []

        self._execute(self.shapes[shape_num].data, 0)

        if not self.drawn_points:
            return None

        return self._svg()

    def _record_point(self, sx, sy):
        self.drawn_points.append((sx, sy))

    def _emit_move(self):
        if self.need_move:
            sx, sy = self.x, -self.y
            self.path_parts.append(f"M{sx:.4g} {sy:.4g}")
            self._record_point(sx, sy)
            self.need_move = False

    def _line_to(self, nx, ny):
        if self.pen_down:
            self._emit_move()
            sx, sy = nx, -ny
            self.path_parts.append(f"L{sx:.4g} {sy:.4g}")
            self._record_point(sx, sy)
        self.x = nx
        self.y = ny

    def _arc_to(self, nx, ny, radius, cw_in_autocad, large_arc=False):
        if self.pen_down:
            self._emit_move()
            sx, sy = nx, -ny
            r = abs(radius)
            la = 1 if large_arc else 0
            sweep = 1 if cw_in_autocad else 0
            self.path_parts.append(
                f"A{r:.4g} {r:.4g} 0 {la} {sweep} {sx:.4g} {sy:.4g}"
            )
            self._record_point(sx, sy)
            self.arc_radii.append(r)
        self.x = nx
        self.y = ny

    def _move_to(self, nx, ny):
        self.x = nx
        self.y = ny

    def _read_subshape_num(self, data, i):
        if self.subshape_bytes == 2:
            if i + 1 < len(data):
                return data[i] * 256 + data[i + 1], i + 2
            return 0, i + 1
        return data[i], i + 1

    def _skip_command(self, data, i):
        if i >= len(data):
            return i
        cmd = data[i]
        if cmd in (0x03, 0x04):
            return i + 1
        if cmd == 0x07:
            return i + self.subshape_bytes
        if cmd == 0x08:
            return i + 2
        if cmd == 0x0A:
            return i + 2
        if cmd == 0x0B:
            return i + 5
        if cmd == 0x0C:
            return i + 3
        if cmd == 0x09:
            i += 1
            while i + 1 < len(data):
                dx, dy = data[i], data[i + 1]
                i += 2
                if dx == 0 and dy == 0:
                    break
            return i - 1
        if cmd == 0x0D:
            i += 1
            while i + 1 < len(data):
                dx, dy = data[i], data[i + 1]
                i += 2
                if dx == 0 and dy == 0:
                    break
                i += 1
            return i - 1
        return i

    def _execute(self, data, depth):
        if depth > 10 or not data:
            return

        i = 0
        end = len(data)
        while i < end:
            b = data[i]

            if b == 0x00:
                break
            elif b == 0x01:
                self.pen_down = True
                self.need_move = True
            elif b == 0x02:
                self.pen_down = False
            elif b == 0x03:
                i += 1
                if i < end and data[i] != 0:
                    self.scale /= data[i]
            elif b == 0x04:
                i += 1
                if i < end:
                    self.scale *= data[i]
            elif b == 0x05:
                self.stack.append((self.x, self.y))
            elif b == 0x06:
                if self.stack:
                    self.x, self.y = self.stack.pop()
                    if self.pen_down:
                        self.need_move = True
            elif b == 0x07:
                i += 1
                sub_num, i = self._read_subshape_num(data, i)
                i -= 1
                if sub_num in self.shapes:
                    saved = (
                        self.x, self.y, self.scale,
                        self.pen_down, self.need_move,
                    )
                    ox, oy = self.x, self.y
                    self.x = 0.0
                    self.y = 0.0

                    old_parts = len(self.path_parts)
                    old_points = len(self.drawn_points)
                    self._execute(self.shapes[sub_num].data, depth + 1)

                    dx, dy = self.x, self.y
                    self._retranslate(old_parts, old_points, ox, oy)

                    self.x = ox + dx
                    self.y = oy + dy
                    _, _, self.scale, self.pen_down, self.need_move = saved
                    if self.pen_down:
                        self.need_move = True
            elif b == 0x08:
                if i + 2 >= end:
                    break
                i += 1
                dx = signed_byte(data[i]) * self.scale
                i += 1
                dy = signed_byte(data[i]) * self.scale
                nx, ny = self.x + dx, self.y + dy
                if self.pen_down:
                    self._line_to(nx, ny)
                else:
                    self._move_to(nx, ny)
            elif b == 0x09:
                while i + 2 < end:
                    i += 1
                    raw_dx = data[i]
                    i += 1
                    raw_dy = data[i]
                    if raw_dx == 0 and raw_dy == 0:
                        break
                    dx = signed_byte(raw_dx) * self.scale
                    dy = signed_byte(raw_dy) * self.scale
                    nx, ny = self.x + dx, self.y + dy
                    if self.pen_down:
                        self._line_to(nx, ny)
                    else:
                        self._move_to(nx, ny)
            elif b == 0x0A:
                if i + 2 >= end:
                    break
                i += 1
                radius = data[i] * self.scale
                i += 1
                self._do_octant_arc(radius, data[i], 0.0, 0.0)
            elif b == 0x0B:
                if i + 5 >= end:
                    break
                i += 1; start_frac = data[i]
                i += 1; end_frac = data[i]
                i += 1; radius_hi = data[i]
                i += 1; radius_lo = data[i]
                i += 1; arc_spec = data[i]
                radius = (radius_hi * 256 + radius_lo) * self.scale
                self._do_octant_arc(radius, arc_spec, start_frac, end_frac)
            elif b == 0x0C:
                if i + 3 >= end:
                    break
                i += 1; dx = signed_byte(data[i]) * self.scale
                i += 1; dy = signed_byte(data[i]) * self.scale
                i += 1; bulge = signed_byte(data[i])
                self._do_bulge(dx, dy, bulge)
            elif b == 0x0D:
                while i + 2 < end:
                    i += 1
                    raw_dx = data[i]
                    i += 1
                    raw_dy = data[i]
                    if raw_dx == 0 and raw_dy == 0:
                        break
                    if i + 1 >= end:
                        break
                    i += 1
                    dx = signed_byte(raw_dx) * self.scale
                    dy = signed_byte(raw_dy) * self.scale
                    bulge = signed_byte(data[i])
                    self._do_bulge(dx, dy, bulge)
            elif b == 0x0E:
                i += 1
                if i < end:
                    i = self._skip_command(data, i)
            else:
                length = (b >> 4) & 0xF
                direction = b & 0xF
                vx, vy = DIRECTION_VECTORS[direction]
                dx = vx * length * self.scale
                dy = vy * length * self.scale
                nx, ny = self.x + dx, self.y + dy
                if self.pen_down:
                    self._line_to(nx, ny)
                else:
                    self._move_to(nx, ny)

            i += 1

    def _do_octant_arc(self, radius, arc_spec_byte, start_frac, end_frac):
        sc = signed_byte(arc_spec_byte)
        ccw = sc >= 0
        val = abs(sc)
        start_octant = (val >> 4) & 0x07
        span = val & 0x07
        if span == 0:
            span = 8

        start_angle = start_octant * 45.0
        frac_start = start_frac * 45.0 / 256.0
        frac_end = end_frac * 45.0 / 256.0

        if ccw:
            actual_start = start_angle + frac_start
            actual_end = start_angle + span * 45.0 - frac_end
        else:
            actual_start = start_angle - frac_start
            actual_end = start_angle - span * 45.0 + frac_end

        start_rad = math.radians(actual_start)
        end_rad = math.radians(actual_end)

        cx = self.x - radius * math.cos(start_rad)
        cy = self.y - radius * math.sin(start_rad)

        ex = cx + radius * math.cos(end_rad)
        ey = cy + radius * math.sin(end_rad)

        total_degrees = abs(actual_end - actual_start)

        if total_degrees >= 359.9:
            mid_rad = start_rad + math.pi if ccw else start_rad - math.pi
            mx = cx + radius * math.cos(mid_rad)
            my = cy + radius * math.sin(mid_rad)
            cw_flag = not ccw
            self._arc_to(mx, my, radius, cw_flag, False)
            self._arc_to(ex, ey, radius, cw_flag, False)
        else:
            large = total_degrees > 180.0
            cw_flag = not ccw
            self._arc_to(ex, ey, radius, cw_flag, large)

        self._add_arc_bbox(cx, cy, radius, actual_start, actual_end, ccw)

    def _do_bulge(self, dx, dy, bulge):
        nx = self.x + dx
        ny = self.y + dy

        if bulge == 0 or (dx == 0 and dy == 0):
            if self.pen_down:
                self._line_to(nx, ny)
            else:
                self._move_to(nx, ny)
            return

        chord = math.hypot(dx, dy)
        if chord < 1e-10:
            self._move_to(nx, ny)
            return

        h = abs(bulge) * chord / (2.0 * 127.0)
        r = (chord * chord + 4.0 * h * h) / (8.0 * h)

        cw_flag = bulge < 0
        self._arc_to(nx, ny, r, cw_flag, False)

    def _add_arc_bbox(self, cx, cy, radius, start_deg, end_deg, ccw):
        scx, scy = cx, -cy
        r = abs(radius)
        mn = min(start_deg, end_deg)
        mx = max(start_deg, end_deg)
        for angle in [0, 90, 180, 270]:
            for fa in [angle, angle + 360, angle - 360]:
                if mn <= fa <= mx:
                    px = scx + r * math.cos(math.radians(angle))
                    py = scy - r * math.sin(math.radians(angle))
                    self._record_point(px, py)

    def _retranslate(self, parts_start, points_start, ox, oy):
        for j in range(parts_start, len(self.path_parts)):
            self.path_parts[j] = _translate_path_part(
                self.path_parts[j], ox, -oy
            )
        for j in range(points_start, len(self.drawn_points)):
            px, py = self.drawn_points[j]
            self.drawn_points[j] = (px + ox, py - oy)

    def _svg(self):
        if not self.drawn_points:
            return None

        xs = [p[0] for p in self.drawn_points]
        ys = [p[1] for p in self.drawn_points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        pad = max(2.0, max(self.arc_radii) * 0.1) if self.arc_radii else 2.0
        pad = max(pad, 1.0)
        min_x -= pad
        min_y -= pad
        max_x += pad
        max_y += pad

        w = max_x - min_x
        h = max_y - min_y
        if w < 0.1:
            w = 4.0
            min_x -= 2.0
        if h < 0.1:
            h = 4.0
            min_y -= 2.0

        stroke_w = max(w, h) * 0.02
        stroke_w = max(0.1, min(stroke_w, 1.0))

        path_d = " ".join(self.path_parts)

        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="{min_x:.4g} {min_y:.4g} {w:.4g} {h:.4g}" '
            f'width="{max(60, int(w * 3))}" height="{max(60, int(h * 3))}">\n'
            f'  <path d="{path_d}" fill="none" stroke="black" '
            f'stroke-width="{stroke_w:.4g}" stroke-linecap="round" '
            f'stroke-linejoin="round"/>\n'
            f"</svg>\n"
        )
        return svg


def _translate_path_part(part, tx, ty):
    tokens = part.replace(",", " ").split()
    cmd = tokens[0][0]
    nums = []
    first = tokens[0][1:]
    if first:
        nums.append(first)
    nums.extend(tokens[1:])

    floats = [float(n) for n in nums]

    if cmd in ("M", "L"):
        floats[0] += tx
        floats[1] += ty
        return f"{cmd}{floats[0]:.4g} {floats[1]:.4g}"
    elif cmd == "A":
        floats[5] += tx
        floats[6] += ty
        return (
            f"A{floats[0]:.4g} {floats[1]:.4g} "
            f"{int(floats[2])} {int(floats[3])} {int(floats[4])} "
            f"{floats[5]:.4g} {floats[6]:.4g}"
        )
    return part


def convert(input_file, output_dir):
    shx = parse_shx(input_file)
    if shx is None:
        print(
            f"Error: '{input_file}' is not a valid AutoCAD shape file.",
            file=sys.stderr,
        )
        return False

    if not shx.shapes:
        print(
            f"Warning: '{input_file}' contains no renderable shapes.",
            file=sys.stderr,
        )
        return True

    os.makedirs(output_dir, exist_ok=True)

    renderer = Renderer(shx.shapes, shx.subshape_bytes)
    count = 0

    for shape_num in sorted(shx.shapes.keys()):
        svg = renderer.render(shape_num)
        if svg is None:
            continue

        fname = f"shape_{shape_num:05d}.svg"
        out_path = os.path.join(output_dir, fname)
        with open(out_path, "w") as f:
            f.write(svg)
        count += 1

    return True


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(input_file):
        print(f"Error: '{input_file}' not found.", file=sys.stderr)
        sys.exit(1)

    if not convert(input_file, output_dir):
        sys.exit(1)


if __name__ == "__main__":
    main()

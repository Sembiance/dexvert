#!/usr/bin/env python3
# Vibe coded by Claude
"""GEM Vector VDI Metafile (.GEM) to SVG converter."""

import struct
import sys
import math

# Default VDI color table (16 standard colors)
# Indices 0-7: standard VDI primaries
# Indices 8-15: dark/muted variants (PC GEM convention)
DEFAULT_COLORS = [
    (255, 255, 255),  # 0: White
    (0, 0, 0),        # 1: Black
    (255, 0, 0),      # 2: Red
    (0, 255, 0),      # 3: Green
    (0, 0, 255),      # 4: Blue
    (0, 255, 255),    # 5: Cyan
    (255, 255, 0),    # 6: Yellow
    (255, 0, 255),    # 7: Magenta
    (191, 191, 191),  # 8: Light Gray
    (127, 127, 127),  # 9: Dark Gray
    (191, 0, 0),      # 10: Dark Red
    (0, 191, 0),      # 11: Dark Green
    (0, 0, 191),      # 12: Dark Blue
    (0, 191, 191),    # 13: Dark Cyan
    (191, 191, 0),    # 14: Dark Yellow / Olive
    (191, 0, 191),    # 15: Dark Magenta
]

# VDI standard fill pattern bitmaps from EmuTOS source.
# Each pattern is a list of 16-bit words, one per scanline row.
# DITHER: 8 halftone patterns (4 rows each, tiled to 16 high)
# Used for fill_interior=2, styles 1-8
VDI_DITHER = [
    [0x0000, 0x4444, 0x0000, 0x1111],
    [0x0000, 0x5555, 0x0000, 0x5555],
    [0x8888, 0x5555, 0x2222, 0x5555],
    [0xAAAA, 0x5555, 0xAAAA, 0x5555],
    [0xAAAA, 0xDDDD, 0xAAAA, 0x7777],
    [0xAAAA, 0xFFFF, 0xAAAA, 0xFFFF],
    [0xEEEE, 0xFFFF, 0xBBBB, 0xFFFF],
    [0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF],
]

# OEMPAT: 16 decorative patterns (8 rows each, tiled to 16 high)
# Used for fill_interior=2, styles 9-24
VDI_OEMPAT = [
    [0xFFFF, 0x8080, 0x8080, 0x8080, 0xFFFF, 0x0808, 0x0808, 0x0808],  # 9: Brick
    [0x2020, 0x4040, 0x8080, 0x4141, 0x2222, 0x1414, 0x0808, 0x1010],  # 10: Diagonal Bricks
    [0x0000, 0x0000, 0x1010, 0x2828, 0x0000, 0x0000, 0x0101, 0x8282],  # 11: Grass
    [0x0202, 0x0202, 0xAAAA, 0x5050, 0x2020, 0x2020, 0xAAAA, 0x0505],  # 12: Trees
    [0x4040, 0x8080, 0x0000, 0x0808, 0x0404, 0x0202, 0x0000, 0x2020],  # 13: Dashed x's
    [0x6606, 0xC6C6, 0xD8D8, 0x1818, 0x8181, 0x8DB1, 0x0C33, 0x6000],  # 14: Cobblestones
    [0x0000, 0x0000, 0x0400, 0x0000, 0x0010, 0x0000, 0x8000, 0x0000],  # 15: Sand
    [0xF8F8, 0x6C6C, 0xC6C6, 0x8F8F, 0x1F1F, 0x3636, 0x6363, 0xF1F1],  # 16: Rough Weave
    [0xAAAA, 0x0000, 0x8888, 0x1414, 0x2222, 0x4141, 0x8888, 0x0000],  # 17: Quilt
    [0x0808, 0x0000, 0xAAAA, 0x0000, 0x0808, 0x0000, 0x8888, 0x0000],  # 18: Patterned Cross
    [0x7777, 0x9898, 0xF8F8, 0xF8F8, 0x7777, 0x8989, 0x8F8F, 0x8F8F],  # 19: Balls
    [0x8080, 0x8080, 0x4141, 0x3E3E, 0x0808, 0x0808, 0x1414, 0xE3E3],  # 20: Vertical Scales
    [0x8181, 0x4242, 0x2424, 0x1818, 0x0606, 0x0101, 0x8080, 0x8080],  # 21: Diagonal Scales
    [0xF0F0, 0xF0F0, 0xF0F0, 0xF0F0, 0x0F0F, 0x0F0F, 0x0F0F, 0x0F0F],  # 22: Checkerboard
    [0x0808, 0x1C1C, 0x3E3E, 0x7F7F, 0xFFFF, 0x7F7F, 0x3E3E, 0x1C1C],  # 23: Filled Diamond
    [0x1111, 0x2222, 0x4444, 0xFFFF, 0x8888, 0x4444, 0x2222, 0xFFFF],  # 24: Herringbone
]

# HATCH0: 6 hatch patterns (8 rows each, tiled to 16 high)
# Used for fill_interior=3, styles 1-6
VDI_HATCH0 = [
    [0x0101, 0x0202, 0x0404, 0x0808, 0x1010, 0x2020, 0x4040, 0x8080],  # 1: +45 narrow
    [0x6060, 0xC0C0, 0x8181, 0x0303, 0x0606, 0x0C0C, 0x1818, 0x3030],  # 2: +45 thick
    [0x4242, 0x8181, 0x8181, 0x4242, 0x2424, 0x1818, 0x1818, 0x2424],  # 3: +-45 medium
    [0x8080, 0x8080, 0x8080, 0x8080, 0x8080, 0x8080, 0x8080, 0x8080],  # 4: Vertical
    [0xFFFF, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000],  # 5: Horizontal
    [0xFFFF, 0x8080, 0x8080, 0x8080, 0x8080, 0x8080, 0x8080, 0x8080],  # 6: Cross
]

# HATCH1: 6 hatch patterns (16 rows each)
# Used for fill_interior=3, styles 7-12
VDI_HATCH1 = [
    [0x0001, 0x0002, 0x0004, 0x0008, 0x0010, 0x0020, 0x0040, 0x0080,
     0x0100, 0x0200, 0x0400, 0x0800, 0x1000, 0x2000, 0x4000, 0x8000],  # 7: +45 wide
    [0x8003, 0x0007, 0x000E, 0x001C, 0x0038, 0x0070, 0x00E0, 0x01C0,
     0x0380, 0x0700, 0x0E00, 0x1C00, 0x3800, 0x7000, 0xE000, 0xC001],  # 8: +45 wide thick
    [0x8001, 0x4002, 0x2004, 0x1008, 0x0810, 0x0420, 0x0240, 0x0180,
     0x0180, 0x0240, 0x0420, 0x0810, 0x1008, 0x2004, 0x4002, 0x8001],  # 9: +-45 wide
    [0x8000, 0x8000, 0x8000, 0x8000, 0x8000, 0x8000, 0x8000, 0x8000,
     0x8000, 0x8000, 0x8000, 0x8000, 0x8000, 0x8000, 0x8000, 0x8000],  # 10: Vertical wide
    [0xFFFF, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000,
     0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000],  # 11: Horizontal wide
    [0xFFFF, 0x8000, 0x8000, 0x8000, 0x8000, 0x8000, 0x8000, 0x8000,
     0xFFFF, 0x8000, 0x8000, 0x8000, 0x8000, 0x8000, 0x8000, 0x8000],  # 12: Cross wide
]


class GemState:
    """Track current VDI drawing state."""
    def __init__(self):
        self.line_type = 1
        self.line_width = 1
        self.line_color = 1
        self.line_ends = (0, 0)
        self.fill_interior = 0
        self.fill_style = 1
        self.fill_color = 1
        self.fill_perimeter = 1
        self.text_font = 1
        self.text_color = 1
        self.text_height = 13
        self.text_rotation = 0
        self.text_h_align = 0
        self.text_v_align = 0
        self.text_effects = 0
        self.char_height = 13
        self.marker_type = 3
        self.marker_height = 11
        self.marker_color = 1
        self.writing_mode = 1
        self.bezier_on = False
        self.udpat_density = 0.5  # user-defined pattern density (0-1)
        self.udpat_bitmap = None  # user-defined pattern bitmap rows (list of ints)
        self.fill_density = None  # opcode 133 fill density (0-1000 permille), None = not set
        self.escape_rgb = None  # RGB override from escape sub=25
        self.clip_on = False
        self.clip_rect = (0, 0, 32767, 32767)
        self.colors = list(DEFAULT_COLORS)


class GemParser:
    """Parse a GEM metafile binary."""

    def __init__(self, data):
        self.data = data
        self.pos = 0
        self.header = {}
        self.records = []

    def read_sword(self):
        if self.pos + 2 > len(self.data):
            return None
        val = struct.unpack_from('<h', self.data, self.pos)[0]
        self.pos += 2
        return val

    def read_uword(self):
        if self.pos + 2 > len(self.data):
            return None
        val = struct.unpack_from('<H', self.data, self.pos)[0]
        self.pos += 2
        return val

    def parse_header(self):
        marker = self.read_sword()
        if marker != -1:
            raise ValueError(f"Not a GEM metafile (marker={marker})")

        hlength = self.read_uword()
        version = self.read_uword()
        ndcrc = self.read_uword()

        self.header = {
            'hlength': hlength,
            'version': version,
            'ndcrc': ndcrc,
        }

        words_read = 4
        field_names = [
            'ext_x1', 'ext_y1', 'ext_x2', 'ext_y2',
            'page_w', 'page_h',
            'coord_x1', 'coord_y1', 'coord_x2', 'coord_y2',
            'imgflag',
        ]
        for name in field_names:
            if words_read >= hlength:
                break
            val = self.read_sword()
            if val is None:
                break
            self.header[name] = val
            words_read += 1

        # Skip remaining reserved header words
        while words_read < hlength:
            self.read_sword()
            words_read += 1

    def parse_records(self):
        while self.pos + 8 <= len(self.data):
            opcode = self.read_sword()
            if opcode is None or opcode == -1:
                break

            n_ptsin = self.read_uword()
            n_intin = self.read_uword()
            sub = self.read_sword()

            if n_ptsin is None or n_intin is None or sub is None:
                break

            # Sanity check: prevent reading absurd amounts of data
            if n_ptsin > 10000 or n_intin > 10000:
                break

            # ptsin: n_ptsin coordinate pairs = n_ptsin * 2 words
            ptsin = []
            for _ in range(n_ptsin * 2):
                v = self.read_sword()
                if v is None:
                    break
                ptsin.append(v)

            # intin: n_intin words
            intin = []
            for _ in range(n_intin):
                v = self.read_sword()
                if v is None:
                    break
                intin.append(v)

            self.records.append({
                'opcode': opcode,
                'n_ptsin': n_ptsin,
                'n_intin': n_intin,
                'sub': sub,
                'ptsin': ptsin,
                'intin': intin,
            })

        return self.records


# Atari ST / CP437 extended character mapping (128-255)
ATARI_CHARS = {
    128: 'Ç', 129: 'ü', 130: 'é', 131: 'â', 132: 'ä', 133: 'à', 134: 'å', 135: 'ç',
    136: 'ê', 137: 'ë', 138: 'è', 139: 'ï', 140: 'î', 141: 'ì', 142: 'Ä', 143: 'Å',
    144: 'É', 145: 'æ', 146: 'Æ', 147: 'ô', 148: 'ö', 149: 'ò', 150: 'û', 151: 'ù',
    152: 'ÿ', 153: 'Ö', 154: 'Ü', 155: '¢', 156: '£', 157: '¥', 158: 'ß', 159: 'ƒ',
    160: 'á', 161: 'í', 162: 'ó', 163: 'ú', 164: 'ñ', 165: 'Ñ', 166: 'ª', 167: 'º',
    168: '¿', 169: '⌐', 170: '¬', 171: '½', 172: '¼', 173: '¡', 174: '«', 175: '»',
    176: 'ã', 177: 'õ', 178: 'Ø', 179: 'ø', 180: 'œ', 181: 'Œ', 182: 'À', 183: 'Ã',
    184: 'Õ', 185: '¨', 186: '´', 187: '†', 188: '¶', 189: '©', 190: '®', 191: '™',
    225: 'ß', 230: 'µ',
}


def gem_char(c):
    """Convert a GEM character code to a Unicode character."""
    c = c & 0xFFFF
    if 32 <= c < 127:
        return chr(c)
    if c in ATARI_CHARS:
        return ATARI_CHARS[c]
    if 127 < c < 256:
        try:
            return bytes([c]).decode('cp437')
        except (UnicodeDecodeError, ValueError):
            pass
    return '?'


def xml_escape(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


class GemToSvg:
    """Convert parsed GEM data to SVG."""

    def __init__(self, header, records):
        self.header = header
        self.records = records
        self.state = GemState()
        self.svg_elements = []
        self.defs_content = []
        self.clip_counter = 0
        self.current_clip_id = None
        self.is_ndc = header.get('ndcrc', 2) == 0
        self.bounds = None
        self.pt_scale = None  # point-to-coordinate scale factor
        self.pattern_cache = {}  # cache of generated SVG pattern IDs
        self.pattern_px_size = 1  # coordinate units per device pixel (set in generate_svg)

    def get_color(self, index):
        if 0 <= index < len(self.state.colors):
            r, g, b = self.state.colors[index]
            return f'rgb({r},{g},{b})'
        return 'rgb(0,0,0)'

    def get_dasharray(self):
        w = max(self.state.line_width, 1)
        dashes = {
            2: (6*w, 3*w),
            3: (w, 2*w),
            4: (6*w, 3*w, w, 3*w),
            5: (4*w, 3*w),
            6: (6*w, 3*w, w, 3*w, w, 3*w),
        }
        d = dashes.get(self.state.line_type)
        if d:
            return ','.join(str(int(v)) for v in d)
        return None

    def _min_stroke_width(self):
        """Compute a minimum visible stroke width based on viewBox scale."""
        if self.bounds:
            bx1, by1, bx2, by2 = self.bounds
            span = max(bx2 - bx1, by2 - by1, 1)
            return max(span / 500, 1)
        return 1

    def line_attrs(self):
        min_sw = self._min_stroke_width()
        attrs = {
            'stroke': self.get_color(self.state.line_color),
            'stroke-width': str(max(self.state.line_width, min_sw)),
            'fill': 'none',
        }
        da = self.get_dasharray()
        if da:
            attrs['stroke-dasharray'] = da
        begin_s, end_s = self.state.line_ends
        cap_style = max(begin_s, end_s)
        if cap_style == 2:
            attrs['stroke-linecap'] = 'round'
        if self.current_clip_id:
            attrs['clip-path'] = f'url(#{self.current_clip_id})'
        return attrs

    def _pattern_gray(self, style, max_style):
        """Convert a VDI pattern/hatch style to an opaque gray color."""
        t = min(style / max_style, 0.94)
        return self._pattern_gray_t(t)

    def _pattern_gray_t(self, t):
        """Blend fill color with white at density t (0=white, 1=solid color)."""
        r, g, b = self.state.colors[self.state.fill_color] if 0 <= self.state.fill_color < len(self.state.colors) else (0, 0, 0)
        t = min(t, 0.94)
        gr = int(255 * (1 - t) + r * t)
        gg = int(255 * (1 - t) + g * t)
        gb = int(255 * (1 - t) + b * t)
        return f'rgb({gr},{gg},{gb})'

    def _get_pattern_bitmap(self, interior, style):
        """Return the bitmap rows for a VDI fill pattern as a list of 16-bit ints.
        Always returns exactly 16 rows (tiled if source is shorter)."""
        if interior == 2:
            style = max(1, min(style, 24))
            if style <= 8:
                rows = VDI_DITHER[style - 1]  # 4 rows
            else:
                rows = VDI_OEMPAT[style - 9]  # 8 rows
        elif interior == 3:
            style = max(1, min(style, 12))
            if style <= 6:
                rows = VDI_HATCH0[style - 1]  # 8 rows
            else:
                rows = VDI_HATCH1[style - 7]  # 16 rows
        elif interior == 4:
            if self.state.udpat_bitmap:
                rows = self.state.udpat_bitmap
            else:
                return None
        else:
            return None
        # Tile to exactly 16 rows
        n = len(rows)
        if n == 0:
            return None
        return [rows[i % n] for i in range(16)]

    def _get_or_create_pattern(self, interior, style, color_rgb, bg_rgb=(255, 255, 255)):
        """Get or create an SVG pattern definition. Returns the pattern ID string."""
        # For user-defined patterns, include bitmap hash in key
        if interior == 4 and self.state.udpat_bitmap:
            bitmap_key = tuple(self.state.udpat_bitmap)
        else:
            bitmap_key = None
        cache_key = (interior, style, color_rgb, bg_rgb, bitmap_key)
        if cache_key in self.pattern_cache:
            return self.pattern_cache[cache_key]

        bitmap = self._get_pattern_bitmap(interior, style)
        if bitmap is None:
            return None

        # Determine pattern tile size in drawing coordinates
        # Each pattern pixel maps to one device pixel in coordinate space
        px_size = max(self.pattern_px_size, 1)
        tile_w = 16 * px_size
        tile_h = 16 * px_size

        pat_id = f'vdipat_{len(self.pattern_cache)}'
        self.pattern_cache[cache_key] = pat_id

        # Build SVG path data for set pixels
        # Background rect + foreground path for set bits
        r, g, b = color_rgb
        br, bg_c, bb = bg_rgb
        lines = []
        lines.append(f'<pattern id="{pat_id}" patternUnits="userSpaceOnUse" '
                      f'width="{tile_w:.4g}" height="{tile_h:.4g}">')
        # Background fill
        lines.append(f'<rect width="{tile_w:.4g}" height="{tile_h:.4g}" fill="rgb({br},{bg_c},{bb})"/>')

        # Build path for foreground pixels
        # Each set bit in the 16-bit word maps to a pixel rectangle
        path_d = []
        for row_idx, word in enumerate(bitmap):
            y = row_idx * px_size
            for bit in range(16):
                if word & (0x8000 >> bit):
                    x = bit * px_size
                    path_d.append(f'M{x:.4g},{y:.4g}h{px_size:.4g}v{px_size:.4g}h{-px_size:.4g}z')

        if path_d:
            lines.append(f'<path d="{"".join(path_d)}" fill="rgb({r},{g},{b})" stroke="none"/>')
        lines.append('</pattern>')
        self.defs_content.extend(lines)

        return pat_id

    def _fill_color_rgb(self):
        """Get the current fill color as an (r,g,b) tuple."""
        if 0 <= self.state.fill_color < len(self.state.colors):
            return self.state.colors[self.state.fill_color]
        return (0, 0, 0)

    def fill_attrs(self, with_perimeter=True):
        attrs = {}
        interior = self.state.fill_interior
        fill_color = self.get_color(self.state.fill_color)

        # Check for escape RGB override (opcode 5, escape sub=25)
        if self.state.escape_rgb:
            r, g, b = self.state.escape_rgb
            self.state.escape_rgb = None
            if interior != 0:
                attrs['fill'] = f'rgb({r},{g},{b})'
            else:
                attrs['fill'] = 'none'
        elif self.state.fill_density is not None:
            # Opcode 133 fill density overrides normal fill logic
            d = self.state.fill_density
            if d == 0:
                attrs['fill'] = 'none'
            else:
                attrs['fill'] = self._pattern_gray_t(d / 1000.0)
        elif interior == 0:  # Hollow
            attrs['fill'] = 'none'
        elif interior == 1:  # Solid
            attrs['fill'] = fill_color
        elif interior in (2, 3, 4):  # Pattern, Hatch, or User-defined
            style = self.state.fill_style
            color_rgb = self._fill_color_rgb()
            pat_id = self._get_or_create_pattern(interior, style, color_rgb)
            if pat_id:
                attrs['fill'] = f'url(#{pat_id})'
            else:
                # Fallback to gray approximation if pattern generation fails
                if interior == 2:
                    style = max(1, min(style, 24))
                    if style <= 8:
                        attrs['fill'] = self._pattern_gray(style, 8)
                    else:
                        attrs['fill'] = self._pattern_gray(style, 24)
                elif interior == 3:
                    style = max(1, min(style, 12))
                    attrs['fill'] = self._pattern_gray(style, 12)
                else:
                    d = self.state.udpat_density
                    attrs['fill'] = self._pattern_gray_t(d)
        else:
            attrs['fill'] = fill_color

        if with_perimeter and self.state.fill_perimeter:
            # VDI fill perimeter uses line attributes per Atari TOS docs
            min_sw = self._min_stroke_width()
            attrs['stroke'] = self.get_color(self.state.line_color)
            attrs['stroke-width'] = str(max(self.state.line_width, min_sw))
        else:
            attrs['stroke'] = 'none'

        if self.current_clip_id:
            attrs['clip-path'] = f'url(#{self.current_clip_id})'
        return attrs

    def emit(self, tag, attrs, text=None):
        self.svg_elements.append((tag, attrs, text))

    def ty(self, y):
        """Transform Y coordinate for NDC mode."""
        if self.is_ndc and self.bounds:
            return self.bounds[3] - (y - self.bounds[1]) + self.bounds[1]
        return y

    def transform_pts(self, ptsin):
        """Transform all coordinates in ptsin for NDC mode."""
        if not self.is_ndc:
            return ptsin
        result = list(ptsin)
        for i in range(1, len(result), 2):
            result[i] = self.ty(result[i])
        return result

    # ---- Bezier support ----

    def _decode_bez_flags(self, intin, n_pts):
        """Decode packed vertex flags from intin array.

        Each int16 word contains two flags: low byte for even index,
        high byte for odd index.  Bit 0 = first point of a 4-point
        Bezier curve; bit 1 = jump (disconnect from previous point).
        """
        flags = []
        for w in intin:
            flags.append(w & 0xFF)
            flags.append((w >> 8) & 0xFF)
        return flags[:n_pts]

    def _build_bez_path(self, ptsin, flags, closed=False):
        """Build an SVG path string from GEM/VDI Bezier vertex data.

        Per the VDI v_bez / v_bez_fill specification, each vertex has a
        flag byte with these bits:

          bit 0 (value 1): This point is the FIRST point of a 4-point
                           cubic Bezier group.  The point itself is the
                           start anchor; the next 3 points are ctrl1,
                           ctrl2, and the end anchor.  The endpoint's
                           own flag determines what happens next.
          bit 1 (value 2): Jump point -- start a new disconnected
                           sub-path (move-to).
          value 0:         Polyline vertex -- draw a straight line from
                           the previous point to this one (line-to).

        After consuming a 4-point bezier group [i, i+1, i+2, i+3], the
        loop advances to i+3 so that the endpoint's flag is processed on
        the next iteration (it may start another bezier group, be a jump,
        or a polyline vertex).

        Flag value 3 (bits 0+1) means move-to AND start of a Bezier
        group: the point is the move target and simultaneously the first
        point of the 4-point cubic.
        """
        n = len(flags)
        if n == 0 or len(ptsin) < 2:
            return None

        def pt(idx):
            """Return (x, y) for point at index idx."""
            return ptsin[idx * 2], ptsin[idx * 2 + 1]

        def has_pt(idx):
            """Check if point index idx is within ptsin bounds."""
            return idx < n and idx * 2 + 1 < len(ptsin)

        parts = []
        i = 0
        started = False

        while has_pt(i):
            x, y = pt(i)
            f = flags[i]

            # --- Handle move-to (bit 1) ---
            if f & 2:
                parts.append(f'M {x},{y}')
                started = True
                # If also bit 0, this point starts a Bezier group too.
                # The M is emitted; consume the next 3 as the cubic
                # (the start anchor of the cubic IS this M point).
                if (f & 1) and has_pt(i + 3):
                    c1x, c1y = pt(i + 1)
                    c2x, c2y = pt(i + 2)
                    ex, ey = pt(i + 3)
                    parts.append(f'C {c1x},{c1y} {c2x},{c2y} {ex},{ey}')
                    # Advance to the endpoint so its flag is checked next
                    i += 3
                else:
                    i += 1
                continue

            if not started:
                # Very first point without jump flag -- implicit move-to
                parts.append(f'M {x},{y}')
                started = True
                if (f & 1) and has_pt(i + 3):
                    c1x, c1y = pt(i + 1)
                    c2x, c2y = pt(i + 2)
                    ex, ey = pt(i + 3)
                    parts.append(f'C {c1x},{c1y} {c2x},{c2y} {ex},{ey}')
                    i += 3
                else:
                    i += 1
                continue

            # --- Bit 0 set: start of a 4-point Bezier group ---
            if (f & 1) and has_pt(i + 3):
                # Line-to the start anchor first (positions pen correctly)
                parts.append(f'L {x},{y}')
                c1x, c1y = pt(i + 1)
                c2x, c2y = pt(i + 2)
                ex, ey = pt(i + 3)
                parts.append(f'C {c1x},{c1y} {c2x},{c2y} {ex},{ey}')
                # Advance to the endpoint so its flag is checked next
                i += 3
                continue

            # --- Flag 0: polyline vertex (line-to) ---
            parts.append(f'L {x},{y}')
            i += 1

        if closed and parts:
            parts.append('Z')

        return ' '.join(parts) if parts else None

    # ---- Output functions ----

    def _has_bezier_data(self, rec):
        """Check if a record carries inline Bezier vertex flags."""
        # sub=13 on the record itself (v_bez / v_bez_fill) always means
        # bezier data.  When bezier_on state is set (via GDP sub=13 toggle),
        # subsequent polyline/fillarea records also carry bezier flags in
        # intin, but only if intin count matches the expected packed flag
        # count: ceil(n_ptsin / 2).  The sub field may be 0, 99, or other
        # application-specific values -- we don't restrict it when bezier_on
        # is already set by a prior GDP sub=13 toggle.
        if rec['sub'] == 13 and rec['intin']:
            return True
        if self.state.bezier_on and rec['intin']:
            expected = (rec['n_ptsin'] + 1) // 2
            return len(rec['intin']) == expected
        return False

    def do_polyline(self, rec):
        ptsin = self.transform_pts(rec['ptsin'])
        if len(ptsin) < 4:
            return

        # Strip trailing (0,0) padding (common in some GEM files)
        trailing = 0
        for i in range(len(ptsin) - 2, 0, -2):
            if ptsin[i] == 0 and ptsin[i + 1] == 0:
                trailing += 1
            else:
                break
        if trailing >= 3:
            ptsin = ptsin[:len(ptsin) - trailing * 2]
        if len(ptsin) < 4:
            return

        # Bezier polyline (v_bez): intin carries packed vertex flags
        if self._has_bezier_data(rec):
            n_pts = rec['n_ptsin']
            flags = self._decode_bez_flags(rec['intin'], n_pts)
            d = self._build_bez_path(ptsin, flags, closed=False)
            if d:
                attrs = self.line_attrs()
                attrs['d'] = d
                self.emit('path', attrs)
                return

        points = ' '.join(f'{ptsin[i]},{ptsin[i+1]}' for i in range(0, len(ptsin), 2))
        attrs = self.line_attrs()
        attrs['points'] = points
        self.emit('polyline', attrs)

    def do_polymarker(self, rec):
        ptsin = self.transform_pts(rec['ptsin'])
        color = self.get_color(self.state.marker_color)
        sz = max(self.state.marker_height // 2, 1)
        for i in range(0, len(ptsin), 2):
            x, y = ptsin[i], ptsin[i+1]
            attrs = {'cx': str(x), 'cy': str(y), 'r': str(sz),
                     'fill': color, 'stroke': 'none'}
            if self.current_clip_id:
                attrs['clip-path'] = f'url(#{self.current_clip_id})'
            self.emit('circle', attrs)

    def do_text(self, rec):
        ptsin = self.transform_pts(rec['ptsin'])
        intin = rec['intin']
        if len(ptsin) < 2 or not intin:
            return
        x, y = ptsin[0], ptsin[1]
        text = ''.join(gem_char(c) for c in intin)

        h = max(self.state.char_height, self.state.text_height, 6)
        attrs = {
            'x': str(x), 'y': str(y),
            'fill': self.get_color(self.state.text_color),
            'font-family': 'sans-serif',
            'font-size': str(h),
        }
        ha = {0: 'start', 1: 'middle', 2: 'end'}
        attrs['text-anchor'] = ha.get(self.state.text_h_align, 'start')

        va = self.state.text_v_align
        if va == 1:
            attrs['dominant-baseline'] = 'hanging'
        elif va in (2, 3):
            attrs['dominant-baseline'] = 'central'
        elif va in (4, 5):
            attrs['dominant-baseline'] = 'auto'

        effects = self.state.text_effects
        if effects & 0x01:
            attrs['font-weight'] = 'bold'
        if effects & 0x04:
            attrs['font-style'] = 'italic'
        if effects & 0x08:
            attrs['text-decoration'] = 'underline'

        if self.state.text_rotation:
            angle = -self.state.text_rotation / 10.0
            if self.is_ndc:
                angle = -angle
            attrs['transform'] = f'rotate({angle},{x},{y})'

        if self.current_clip_id:
            attrs['clip-path'] = f'url(#{self.current_clip_id})'

        self.emit('text', attrs, text)

    def do_fillarea(self, rec):
        ptsin = self.transform_pts(rec['ptsin'])
        if len(ptsin) < 4:
            return

        # Bezier filled area (v_bez_fill): intin carries packed vertex flags
        if self._has_bezier_data(rec):
            n_pts = rec['n_ptsin']
            flags = self._decode_bez_flags(rec['intin'], n_pts)
            d = self._build_bez_path(ptsin, flags, closed=True)
            if d:
                attrs = self.fill_attrs()
                attrs['d'] = d
                attrs['fill-rule'] = 'evenodd'
                self.emit('path', attrs)
                return

        points = ' '.join(f'{ptsin[i]},{ptsin[i+1]}' for i in range(0, len(ptsin), 2))
        attrs = self.fill_attrs()
        attrs['fill-rule'] = 'evenodd'
        attrs['points'] = points
        self.emit('polygon', attrs)

    def do_fill_rect(self, rec):
        ptsin = self.transform_pts(rec['ptsin'])
        if len(ptsin) < 4:
            return
        x1, y1, x2, y2 = ptsin[0], ptsin[1], ptsin[2], ptsin[3]
        x, y = min(x1, x2), min(y1, y2)
        w, h = abs(x2 - x1), abs(y2 - y1)
        attrs = self.fill_attrs(with_perimeter=False)
        attrs.update({'x': str(x), 'y': str(y), 'width': str(w), 'height': str(h)})
        self.emit('rect', attrs)

    # ---- GDP functions (opcode 11) ----

    def _arc_path(self, cx, cy, rx, ry, start_deg, end_deg, close_center=False):
        """Build SVG path data for an arc. Angles in degrees, math convention."""
        sweep_angle = end_deg - start_deg
        if sweep_angle <= 0:
            sweep_angle += 360

        # Full circle: split into two half-arcs (SVG can't draw arc with same start/end)
        if sweep_angle >= 359.9:
            mx = cx - rx  # midpoint at 180°
            my = cy
            sx = cx + rx  # start at 0°
            sy = cy
            if close_center:
                d = (f'M {cx},{cy} L {sx},{sy} '
                     f'A {rx},{ry} 0 0,0 {mx},{my} '
                     f'A {rx},{ry} 0 0,0 {sx},{sy} Z')
            else:
                d = (f'M {sx},{sy} '
                     f'A {rx},{ry} 0 0,0 {mx},{my} '
                     f'A {rx},{ry} 0 0,0 {sx},{sy}')
            return d

        sa_rad = math.radians(start_deg)
        ea_rad = math.radians(end_deg)

        sx = cx + rx * math.cos(sa_rad)
        sy = cy - ry * math.sin(sa_rad)
        ex = cx + rx * math.cos(ea_rad)
        ey = cy - ry * math.sin(ea_rad)

        large_arc = 1 if sweep_angle > 180 else 0
        # VDI arcs go CCW (math) = CCW in SVG screen coords → sweep=0
        sweep = 0

        if close_center:
            d = (f'M {cx},{cy} L {sx:.2f},{sy:.2f} '
                 f'A {rx},{ry} 0 {large_arc},{sweep} {ex:.2f},{ey:.2f} Z')
        else:
            d = (f'M {sx:.2f},{sy:.2f} '
                 f'A {rx},{ry} 0 {large_arc},{sweep} {ex:.2f},{ey:.2f}')
        return d

    def do_gdp(self, rec):
        sub = rec['sub']
        raw_ptsin = rec['ptsin']
        ptsin = self.transform_pts(raw_ptsin)
        intin = rec['intin']

        if sub == 1:  # Bar
            if len(ptsin) >= 4:
                x1, y1, x2, y2 = ptsin[0], ptsin[1], ptsin[2], ptsin[3]
                x, y = min(x1, x2), min(y1, y2)
                w, h = abs(x2 - x1), abs(y2 - y1)
                attrs = self.fill_attrs()
                attrs.update({'x': str(x), 'y': str(y),
                              'width': str(w), 'height': str(h)})
                self.emit('rect', attrs)

        elif sub == 2:  # Arc
            if len(ptsin) >= 8 and len(intin) >= 2:
                cx, cy, radius = ptsin[0], ptsin[1], ptsin[6]
                d = self._arc_path(cx, cy, radius, radius,
                                   intin[0] / 10.0, intin[1] / 10.0)
                attrs = self.line_attrs()
                attrs['d'] = d
                self.emit('path', attrs)

        elif sub == 3:  # Pie slice
            if len(ptsin) >= 8 and len(intin) >= 2:
                cx, cy, radius = ptsin[0], ptsin[1], ptsin[6]
                d = self._arc_path(cx, cy, radius, radius,
                                   intin[0] / 10.0, intin[1] / 10.0,
                                   close_center=True)
                attrs = self.fill_attrs()
                attrs['d'] = d
                self.emit('path', attrs)

        elif sub == 4:  # Circle
            if len(ptsin) >= 6:
                cx, cy, r = ptsin[0], ptsin[1], ptsin[4]
                attrs = self.fill_attrs()
                attrs.update({'cx': str(cx), 'cy': str(cy), 'r': str(r)})
                self.emit('circle', attrs)

        elif sub == 5:  # Ellipse
            if len(ptsin) >= 4:
                cx, cy = ptsin[0], ptsin[1]
                rx, ry = abs(raw_ptsin[2]), abs(raw_ptsin[3])  # radii, not coords
                attrs = self.fill_attrs()
                attrs.update({'cx': str(cx), 'cy': str(cy),
                              'rx': str(rx), 'ry': str(ry)})
                self.emit('ellipse', attrs)

        elif sub == 6:  # Elliptical arc
            if len(ptsin) >= 4 and len(intin) >= 2:
                cx, cy = ptsin[0], ptsin[1]
                rx, ry = abs(raw_ptsin[2]), abs(raw_ptsin[3])  # radii, not coords
                d = self._arc_path(cx, cy, rx, ry,
                                   intin[0] / 10.0, intin[1] / 10.0)
                attrs = self.line_attrs()
                attrs['d'] = d
                self.emit('path', attrs)

        elif sub == 7:  # Elliptical pie
            if len(ptsin) >= 4 and len(intin) >= 2:
                cx, cy = ptsin[0], ptsin[1]
                rx, ry = abs(raw_ptsin[2]), abs(raw_ptsin[3])  # radii, not coords
                d = self._arc_path(cx, cy, rx, ry,
                                   intin[0] / 10.0, intin[1] / 10.0,
                                   close_center=True)
                attrs = self.fill_attrs()
                attrs['d'] = d
                self.emit('path', attrs)

        elif sub == 8:  # Rounded rectangle (outline)
            if len(ptsin) >= 4:
                x1, y1, x2, y2 = ptsin[0], ptsin[1], ptsin[2], ptsin[3]
                x, y = min(x1, x2), min(y1, y2)
                w, h = abs(x2 - x1), abs(y2 - y1)
                r = min(w, h) // 16
                attrs = self.line_attrs()
                attrs.update({'x': str(x), 'y': str(y),
                              'width': str(w), 'height': str(h),
                              'rx': str(r), 'ry': str(r)})
                self.emit('rect', attrs)

        elif sub == 9:  # Filled rounded rectangle
            if len(ptsin) >= 4:
                x1, y1, x2, y2 = ptsin[0], ptsin[1], ptsin[2], ptsin[3]
                x, y = min(x1, x2), min(y1, y2)
                w, h = abs(x2 - x1), abs(y2 - y1)
                r = min(w, h) // 16
                attrs = self.fill_attrs()
                attrs.update({'x': str(x), 'y': str(y),
                              'width': str(w), 'height': str(h),
                              'rx': str(r), 'ry': str(r)})
                self.emit('rect', attrs)

        elif sub == 13:  # v_bez_on / v_bez_off (Bezier spline toggle)
            if rec['n_ptsin'] > 0:
                self.state.bezier_on = True
            else:
                self.state.bezier_on = False

        elif sub == 10:  # Justified text
            if len(ptsin) >= 4 and len(intin) >= 3:
                x, y = ptsin[0], ptsin[1]
                length = ptsin[2]
                text = ''.join(gem_char(c) for c in intin[2:])
                h = max(self.state.char_height, self.state.text_height, 6)
                attrs = {
                    'x': str(x), 'y': str(y),
                    'fill': self.get_color(self.state.text_color),
                    'font-family': 'sans-serif',
                    'font-size': str(h),
                    'textLength': str(length),
                    'lengthAdjust': 'spacingAndGlyphs',
                }
                ha = {0: 'start', 1: 'middle', 2: 'end'}
                attrs['text-anchor'] = ha.get(self.state.text_h_align, 'start')
                va = self.state.text_v_align
                if va == 1:
                    attrs['dominant-baseline'] = 'hanging'
                elif va in (2, 3):
                    attrs['dominant-baseline'] = 'central'
                elif va in (4, 5):
                    attrs['dominant-baseline'] = 'auto'
                effects = self.state.text_effects
                if effects & 0x01:
                    attrs['font-weight'] = 'bold'
                if effects & 0x04:
                    attrs['font-style'] = 'italic'
                if effects & 0x08:
                    attrs['text-decoration'] = 'underline'
                if self.state.text_rotation:
                    angle = -self.state.text_rotation / 10.0
                    if self.is_ndc:
                        angle = -angle
                    attrs['transform'] = f'rotate({angle},{x},{y})'
                if self.current_clip_id:
                    attrs['clip-path'] = f'url(#{self.current_clip_id})'
                self.emit('text', attrs, text)

    # ---- Attribute functions ----

    def do_set_color(self, rec):
        intin = rec['intin']
        if len(intin) < 4:
            return
        index = intin[0]
        r = min(int(intin[1] * 255 / 1000), 255)
        g = min(int(intin[2] * 255 / 1000), 255)
        b = min(int(intin[3] * 255 / 1000), 255)
        while len(self.state.colors) <= index:
            self.state.colors.append((0, 0, 0))
        self.state.colors[index] = (max(r, 0), max(g, 0), max(b, 0))

    def do_set_clip(self, rec):
        intin = rec['intin']
        ptsin = rec['ptsin']
        if self.is_ndc:
            ptsin = self.transform_pts(ptsin)

        if intin:
            self.state.clip_on = bool(intin[0])
        if len(ptsin) >= 4:
            x1, y1, x2, y2 = ptsin[0], ptsin[1], ptsin[2], ptsin[3]
            self.state.clip_rect = (min(x1, x2), min(y1, y2),
                                    max(x1, x2), max(y1, y2))

        if self.state.clip_on:
            self.clip_counter += 1
            cid = f'clip{self.clip_counter}'
            cx1, cy1, cx2, cy2 = self.state.clip_rect
            self.defs_content.append(
                f'<clipPath id="{cid}"><rect x="{cx1}" y="{cy1}" '
                f'width="{cx2-cx1}" height="{cy2-cy1}"/></clipPath>')
            self.current_clip_id = cid
        else:
            self.current_clip_id = None

    # ---- Main processing ----

    def process_record(self, rec):
        op = rec['opcode']
        intin = rec['intin']
        ptsin = rec['ptsin']

        if op == 6:
            self.do_polyline(rec)
        elif op == 7:
            self.do_polymarker(rec)
        elif op == 8:
            self.do_text(rec)
        elif op == 9:
            self.do_fillarea(rec)
        elif op == 11:
            self.do_gdp(rec)
        elif op == 114:
            self.do_fill_rect(rec)
        elif op == 12:  # Set character height (absolute)
            if len(ptsin) >= 2:
                self.state.text_height = max(abs(ptsin[1]), 1)
                self.state.char_height = max(abs(ptsin[1]), 1)
        elif op == 13:  # Set character baseline vector
            if len(ptsin) >= 4:
                dx = ptsin[2] - ptsin[0]
                dy = ptsin[3] - ptsin[1]
                if dx != 0 or dy != 0:
                    self.state.text_rotation = int(
                        math.degrees(math.atan2(-dy, dx)) * 10)
            elif intin:
                # Rotation angle directly in intin[0], tenths of degrees
                self.state.text_rotation = intin[0]
        elif op == 14:
            self.do_set_color(rec)
        elif op == 15:  # Set polyline type
            if intin:
                self.state.line_type = intin[0]
        elif op == 16:  # Set polyline width
            if len(ptsin) >= 2:
                self.state.line_width = max(ptsin[0], 1)
        elif op == 17:  # Set polyline color
            if intin:
                self.state.line_color = intin[0]
        elif op == 18:  # Set polymarker type
            if intin:
                self.state.marker_type = intin[0]
        elif op == 19:  # Set polymarker height
            if len(ptsin) >= 2:
                self.state.marker_height = max(abs(ptsin[1]), 1)
        elif op == 20:  # Set polymarker color
            if intin:
                self.state.marker_color = intin[0]
        elif op == 21:  # Set text face
            if intin:
                self.state.text_font = intin[0]
        elif op == 22:  # Set text color
            if intin:
                self.state.text_color = intin[0]
        elif op == 23:  # Set fill interior style
            if intin:
                self.state.fill_interior = intin[0]
                self.state.fill_density = None  # Reset density override
        elif op == 24:  # Set fill style index
            if intin:
                self.state.fill_style = intin[0]
                self.state.fill_density = None  # Reset density override
        elif op == 25:  # Set fill color
            if intin:
                self.state.fill_color = intin[0]
        elif op == 32:  # Set writing mode
            if intin:
                self.state.writing_mode = intin[0]
        elif op == 39:  # Set text alignment
            if len(intin) >= 2:
                self.state.text_h_align = intin[0]
                self.state.text_v_align = intin[1]
        elif op == 104:  # Set fill perimeter visibility
            if intin:
                self.state.fill_perimeter = intin[0]
        elif op == 106:  # Set text effects
            if intin:
                self.state.text_effects = intin[0]
        elif op == 107:  # Set char cell height (points mode)
            pt_size = None
            if len(ptsin) >= 2:
                pt_size = max(abs(ptsin[1]), 1)
            elif intin:
                pt_size = max(abs(intin[0]), 1)
            if pt_size is not None:
                # Convert point size to coordinate units
                scale = self.pt_scale if self.pt_scale else 1.0
                h = max(int(pt_size * scale), 1)
                self.state.char_height = h
                self.state.text_height = h
        elif op == 108:  # Set polyline end styles
            if len(intin) >= 2:
                self.state.line_ends = (intin[0], intin[1])
        elif op == 5:  # Escape functions
            if len(intin) >= 4 and intin[0] == 25:
                # Escape sub=25: RGB color override (0-1000 permille)
                r = min(int(intin[1] * 255 / 1000), 255)
                g = min(int(intin[2] * 255 / 1000), 255)
                b = min(int(intin[3] * 255 / 1000), 255)
                self.state.escape_rgb = (max(r, 0), max(g, 0), max(b, 0))
        elif op == 112:  # Set user-defined fill pattern (vsf_udpat)
            if intin:
                # Count set bits in pattern bitmap to estimate density
                bits_set = sum(bin(w & 0xFFFF).count('1') for w in intin)
                total_bits = len(intin) * 16
                self.state.udpat_density = bits_set / total_bits if total_bits > 0 else 0.5
                # Store actual bitmap for SVG pattern generation
                self.state.udpat_bitmap = [w & 0xFFFF for w in intin]
        elif op == 129:
            self.do_set_clip(rec)
        elif op == 133:  # Fill density (GEM Draw Plus extension), permille 0-1000
            if intin:
                self.state.fill_density = max(0, min(intin[0], 1000))

    def compute_bounds(self):
        """Compute bounding box from all ptsin data across records."""
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')

        for rec in self.records:
            op = rec['opcode']
            # Only consider drawing opcodes
            if op not in (6, 7, 8, 9, 11, 114):
                continue
            ptsin = rec['ptsin']
            # For GDP sub=10 (justified text), include text position and extend by length
            if op == 11 and rec['sub'] == 10 and len(ptsin) >= 4:
                x, y = ptsin[0], ptsin[1]
                length = ptsin[2]
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x + length)
                max_y = max(max_y, y)
                continue
            for i in range(0, len(ptsin) - 1, 2):
                x, y = ptsin[i], ptsin[i + 1]
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

        if min_x == float('inf'):
            return (0, 0, 1000, 1000)
        return (min_x, min_y, max_x, max_y)

    def determine_viewbox(self):
        """Determine the SVG viewBox from header info or computed bounds."""
        h = self.header
        bx1, by1, bx2, by2 = self.compute_bounds()
        has_data = bx1 < float('inf')

        # Try header extends first
        ext_x1 = h.get('ext_x1', 0)
        ext_y1 = h.get('ext_y1', 0)
        ext_x2 = h.get('ext_x2', 0)
        ext_y2 = h.get('ext_y2', 0)

        if ext_x2 > ext_x1 and ext_y2 > ext_y1:
            ext_w = ext_x2 - ext_x1
            ext_h = ext_y2 - ext_y1

            # Detect full NDC range extends (e.g. -32100..32100) that don't
            # represent the actual drawing area
            if has_data and ext_w >= 60000 and ext_h >= 60000:
                data_w = bx2 - bx1
                data_h = by2 - by1
                if data_w < ext_w * 0.5 or data_h < ext_h * 0.5:
                    margin_x = max(data_w * 0.02, 1)
                    margin_y = max(data_h * 0.02, 1)
                    return (bx1 - margin_x, by1 - margin_y,
                            bx2 + margin_x, by2 + margin_y)

            version = h.get('version', 0)
            if version >= 400:
                # GEM/3+ files: extends define the intended viewport;
                # data beyond extends is page background
                return (ext_x1, ext_y1, ext_x2, ext_y2)
            if has_data:
                if bx1 < ext_x1 or bx2 > ext_x2 or by1 < ext_y1 or by2 > ext_y2:
                    # Data exceeds extends - use union of both
                    return (min(ext_x1, bx1), min(ext_y1, by1),
                            max(ext_x2, bx2), max(ext_y2, by2))
            return (ext_x1, ext_y1, ext_x2, ext_y2)

        # Extends invalid - compute from actual drawing data
        if has_data:
            margin_x = max((bx2 - bx1) * 0.02, 1)
            margin_y = max((by2 - by1) * 0.02, 1)
            return (bx1 - margin_x, by1 - margin_y,
                    bx2 + margin_x, by2 + margin_y)

        # Last resort fallback
        return (0, 0, 1000, 1000)

    def _compute_pt_scale(self):
        """Compute scaling factor from point sizes to coordinate units.

        VDI vst_point (opcode 107) uses typographic points. We need to
        convert those to the coordinate system used by drawing primitives.
        Use page dimensions and coord fields from header when available.
        """
        h = self.header
        page_h = h.get('page_h', 0)
        if page_h <= 0:
            # No page info - estimate from bounds
            if self.bounds:
                return max(self.bounds[3] - self.bounds[1], 1) / 720.0
            return 1.0

        # page_h is in 0.1mm. Convert to points: (page_h/254) inches * 72 pts/inch
        page_pts = page_h * 72.0 / 254.0

        # Use coord fields for the full page coordinate range if available
        coord_y1 = h.get('coord_y1', 0)
        coord_y2 = h.get('coord_y2', 0)
        coord_span = abs(coord_y2 - coord_y1)
        if coord_span > 0:
            return coord_span / page_pts

        # Fall back to viewBox bounds
        if self.bounds:
            coord_h = max(self.bounds[3] - self.bounds[1], 1)
            return coord_h / page_pts
        return 1.0

    def generate_svg(self):
        # Determine bounds for coordinate transforms
        raw_bounds = self.determine_viewbox()
        self.bounds = raw_bounds
        self.pt_scale = self._compute_pt_scale()

        # Compute pattern pixel size: coordinate units per device pixel
        # On the Atari ST, patterns were 16x16 device pixels. We map
        # device pixels to coordinate space using the SVG output dimensions.
        bx1, by1, bx2, by2 = raw_bounds
        vb_w_pre = max(bx2 - bx1, 1)
        page_w = self.header.get('page_w', 0)
        page_h = self.header.get('page_h', 0)
        if page_w > 0 and page_h > 0:
            svg_px_w = page_w * 96 / 254
        else:
            aspect = vb_w_pre / max(by2 - by1, 1)
            svg_px_w = 800 if aspect >= 1 else 800 * aspect
        self.pattern_px_size = vb_w_pre / max(svg_px_w, 1)

        # Process all records to generate SVG elements
        for rec in self.records:
            self.process_record(rec)

        bx1, by1, bx2, by2 = raw_bounds
        vb_x, vb_y = bx1, by1
        vb_w = max(bx2 - bx1, 1)
        vb_h = max(by2 - by1, 1)

        if self.is_ndc:
            # NDC: after y-flip, viewBox stays the same dimensions
            pass

        # Determine SVG pixel dimensions from page size
        page_w = self.header.get('page_w', 0)
        page_h = self.header.get('page_h', 0)
        if page_w > 0 and page_h > 0:
            svg_w = page_w * 96 / 254
            svg_h = page_h * 96 / 254
        else:
            # Fallback: use a reasonable size maintaining aspect ratio
            aspect = vb_w / vb_h if vb_h > 0 else 1
            if aspect >= 1:
                svg_w = 800
                svg_h = 800 / aspect
            else:
                svg_h = 800
                svg_w = 800 * aspect

        lines = ['<?xml version="1.0" encoding="UTF-8"?>']
        lines.append(
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{svg_w:.1f}" height="{svg_h:.1f}" '
            f'viewBox="{vb_x} {vb_y} {vb_w} {vb_h}">')

        # White background
        lines.append(
            f'<rect x="{vb_x}" y="{vb_y}" width="{vb_w}" '
            f'height="{vb_h}" fill="white"/>')

        # Defs (clip paths, etc.)
        if self.defs_content:
            lines.append('<defs>')
            lines.extend(self.defs_content)
            lines.append('</defs>')

        # Render elements
        for tag, attrs, text in self.svg_elements:
            attr_str = ' '.join(f'{k}="{v}"' for k, v in attrs.items())
            if text:
                lines.append(f'<{tag} {attr_str}>{xml_escape(text)}</{tag}>')
            else:
                lines.append(f'<{tag} {attr_str}/>')

        lines.append('</svg>')
        return '\n'.join(lines)


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.gem> <output.svg>", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    with open(input_path, 'rb') as f:
        data = f.read()

    parser = GemParser(data)
    parser.parse_header()
    parser.parse_records()

    converter = GemToSvg(parser.header, parser.records)
    svg = converter.generate_svg()

    if not converter.svg_elements:
        print(f"Skipping {input_path}: no drawing operations found", file=sys.stderr)
        sys.exit(0)

    with open(output_path, 'w') as f:
        f.write(svg)

    h = parser.header
    print(f"Converted {input_path} -> {output_path}")
    print(f"  Version: {h.get('version')}, "
          f"Coord: {'NDC' if h.get('ndcrc') == 0 else 'RC'}, "
          f"Records: {len(parser.records)}")


if __name__ == '__main__':
    main()

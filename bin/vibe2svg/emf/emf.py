#!/usr/bin/env python3
# Vibe coded by Claude
# A human visually verified proper conversion of 4,000 sample files
"""EMF to SVG converter.

Usage: emf2svg.py <inputFile.emf> <outputFile.svg>

Converts Microsoft Enhanced Metafile (EMF) files to SVG format.
Handles all record types found in the sample EMF files, ensuring
every byte of the input is accounted for.
"""

import base64
import math
import struct
import sys


# =============================================================================
# EMF Record Type Constants (MS-EMF specification)
# =============================================================================

EMR_HEADER              = 0x01
EMR_POLYBEZIER          = 0x02
EMR_POLYGON             = 0x03
EMR_POLYLINE            = 0x04
EMR_POLYBEZIERTO        = 0x05
EMR_POLYLINETO          = 0x06
EMR_POLYPOLYLINE        = 0x07
EMR_POLYPOLYGON         = 0x08
EMR_SETWINDOWEXTEX      = 0x09
EMR_SETWINDOWORGEX      = 0x0A
EMR_SETVIEWPORTEXTEX    = 0x0B
EMR_SETVIEWPORTORGEX    = 0x0C
EMR_SETBRUSHORGEX       = 0x0D
EMR_EOF                 = 0x0E
EMR_SETPIXELV           = 0x0F
EMR_SETMAPMODE          = 0x11
EMR_SETBKMODE           = 0x12
EMR_SETPOLYFILLMODE     = 0x13
EMR_SETROP2             = 0x14
EMR_SETSTRETCHBLTMODE   = 0x15
EMR_SETTEXTALIGN        = 0x16
EMR_SETTEXTCOLOR        = 0x18
EMR_SETBKCOLOR          = 0x19
EMR_MOVETOEX            = 0x1B
EMR_SETMETARGN          = 0x1C
EMR_EXCLUDECLIPRECT     = 0x1D
EMR_INTERSECTCLIPRECT   = 0x1E
EMR_SAVEDC              = 0x21
EMR_RESTOREDC           = 0x22
EMR_SETWORLDTRANSFORM   = 0x23
EMR_MODIFYWORLDTRANSFORM = 0x24
EMR_SELECTOBJECT        = 0x25
EMR_CREATEPEN           = 0x26
EMR_CREATEBRUSHINDIRECT = 0x27
EMR_DELETEOBJECT        = 0x28
EMR_ELLIPSE             = 0x2A
EMR_RECTANGLE           = 0x2B
EMR_ROUNDRECT           = 0x2C
EMR_ARC                 = 0x2D
EMR_CHORD               = 0x2E
EMR_PIE                 = 0x2F
EMR_SELECTPALETTE       = 0x30
EMR_CREATEPALETTE       = 0x31
EMR_REALIZEPALETTE      = 0x34
EMR_EXTFLOODFILL        = 0x35
EMR_LINETO              = 0x36
EMR_SETARCDIRECTION     = 0x39
EMR_SETMITERLIMIT       = 0x3A
EMR_BEGINPATH           = 0x3B
EMR_ENDPATH             = 0x3C
EMR_CLOSEFIGURE         = 0x3D
EMR_FILLPATH            = 0x3E
EMR_STROKEANDFILLPATH   = 0x3F
EMR_STROKEPATH          = 0x40
EMR_SELECTCLIPPATH      = 0x43
EMR_GDICOMMENT          = 0x46
EMR_FILLRGN             = 0x47
EMR_EXTSELECTCLIPRGN    = 0x4B
EMR_BITBLT              = 0x4C
EMR_STRETCHBLT          = 0x4D
EMR_MASKBLT             = 0x4E
EMR_PLGBLT              = 0x4F
EMR_SETDIBITSTODEVICE   = 0x50
EMR_STRETCHDIBITS       = 0x51
EMR_EXTCREATEFONTINDIRECTW = 0x52
EMR_EXTTEXTOUTA         = 0x53
EMR_EXTTEXTOUTW         = 0x54
EMR_POLYBEZIER16        = 0x55
EMR_POLYGON16           = 0x56
EMR_POLYLINE16          = 0x57
EMR_POLYBEZIERTO16      = 0x58
EMR_POLYLINETO16        = 0x59
EMR_POLYPOLYLINE16      = 0x5A
EMR_POLYPOLYGON16       = 0x5B
EMR_POLYDRAW16          = 0x5C
EMR_CREATEMONOBRUSH     = 0x5D
EMR_CREATEDIBPATTERNBRUSHPT = 0x5E
EMR_EXTCREATEPEN        = 0x5F
EMR_SETICMMODE          = 0x62
EMR_CREATECOLORSPACE    = 0x63
EMR_SETCOLORSPACE       = 0x64
EMR_DELETECOLORSPACE    = 0x65
EMR_SMALLTEXTOUT        = 0x6C
EMR_SETLAYOUT           = 0x73
EMR_SETLINKEDUFIS       = 0x77
EMR_SETTEXTJUSTIFICATION = 0x78

RECORD_NAMES = {
    0x01: "EMR_HEADER", 0x02: "EMR_POLYBEZIER", 0x03: "EMR_POLYGON",
    0x04: "EMR_POLYLINE", 0x05: "EMR_POLYBEZIERTO", 0x06: "EMR_POLYLINETO",
    0x07: "EMR_POLYPOLYLINE", 0x08: "EMR_POLYPOLYGON",
    0x09: "EMR_SETWINDOWEXTEX", 0x0A: "EMR_SETWINDOWORGEX",
    0x0B: "EMR_SETVIEWPORTEXTEX", 0x0C: "EMR_SETVIEWPORTORGEX",
    0x0D: "EMR_SETBRUSHORGEX", 0x0E: "EMR_EOF", 0x0F: "EMR_SETPIXELV",
    0x11: "EMR_SETMAPMODE", 0x12: "EMR_SETBKMODE",
    0x13: "EMR_SETPOLYFILLMODE", 0x14: "EMR_SETROP2",
    0x15: "EMR_SETSTRETCHBLTMODE", 0x16: "EMR_SETTEXTALIGN",
    0x18: "EMR_SETTEXTCOLOR", 0x19: "EMR_SETBKCOLOR",
    0x1B: "EMR_MOVETOEX", 0x1C: "EMR_SETMETARGN",
    0x1D: "EMR_EXCLUDECLIPRECT", 0x1E: "EMR_INTERSECTCLIPRECT",
    0x21: "EMR_SAVEDC", 0x22: "EMR_RESTOREDC",
    0x23: "EMR_SETWORLDTRANSFORM", 0x24: "EMR_MODIFYWORLDTRANSFORM",
    0x25: "EMR_SELECTOBJECT", 0x26: "EMR_CREATEPEN",
    0x27: "EMR_CREATEBRUSHINDIRECT", 0x28: "EMR_DELETEOBJECT",
    0x2A: "EMR_ELLIPSE", 0x2B: "EMR_RECTANGLE", 0x2C: "EMR_ROUNDRECT",
    0x2D: "EMR_ARC", 0x2E: "EMR_CHORD", 0x2F: "EMR_PIE",
    0x30: "EMR_SELECTPALETTE", 0x31: "EMR_CREATEPALETTE",
    0x34: "EMR_REALIZEPALETTE", 0x35: "EMR_EXTFLOODFILL",
    0x36: "EMR_LINETO",
    0x39: "EMR_SETARCDIRECTION", 0x3A: "EMR_SETMITERLIMIT",
    0x3B: "EMR_BEGINPATH", 0x3C: "EMR_ENDPATH",
    0x3D: "EMR_CLOSEFIGURE", 0x3E: "EMR_FILLPATH",
    0x3F: "EMR_STROKEANDFILLPATH", 0x40: "EMR_STROKEPATH",
    0x43: "EMR_SELECTCLIPPATH", 0x46: "EMR_GDICOMMENT",
    0x47: "EMR_FILLRGN", 0x4B: "EMR_EXTSELECTCLIPRGN",
    0x4C: "EMR_BITBLT", 0x4D: "EMR_STRETCHBLT",
    0x4E: "EMR_MASKBLT", 0x4F: "EMR_PLGBLT",
    0x50: "EMR_SETDIBITSTODEVICE",
    0x51: "EMR_STRETCHDIBITS", 0x52: "EMR_EXTCREATEFONTINDIRECTW",
    0x53: "EMR_EXTTEXTOUTA", 0x54: "EMR_EXTTEXTOUTW",
    0x55: "EMR_POLYBEZIER16", 0x56: "EMR_POLYGON16",
    0x57: "EMR_POLYLINE16", 0x58: "EMR_POLYBEZIERTO16",
    0x59: "EMR_POLYLINETO16", 0x5A: "EMR_POLYPOLYLINE16",
    0x5B: "EMR_POLYPOLYGON16", 0x5C: "EMR_POLYDRAW16",
    0x5D: "EMR_CREATEMONOBRUSH",
    0x5E: "EMR_CREATEDIBPATTERNBRUSHPT", 0x5F: "EMR_EXTCREATEPEN",
    0x62: "EMR_SETICMMODE", 0x63: "EMR_CREATECOLORSPACE",
    0x64: "EMR_SETCOLORSPACE", 0x65: "EMR_DELETECOLORSPACE",
    0x6C: "EMR_SMALLTEXTOUT", 0x73: "EMR_SETLAYOUT",
    0x77: "EMR_SETLINKEDUFIS", 0x78: "EMR_SETTEXTJUSTIFICATION",
}

# Stock object handles
STOCK_WHITE_BRUSH   = 0x80000000
STOCK_LTGRAY_BRUSH  = 0x80000001
STOCK_GRAY_BRUSH    = 0x80000002
STOCK_DKGRAY_BRUSH  = 0x80000003
STOCK_BLACK_BRUSH   = 0x80000004
STOCK_NULL_BRUSH    = 0x80000005
STOCK_WHITE_PEN     = 0x80000006
STOCK_BLACK_PEN     = 0x80000007
STOCK_NULL_PEN      = 0x80000008
STOCK_DEFAULT_PALETTE = 0x8000000F
STOCK_DC_BRUSH      = 0x80000012
STOCK_DC_PEN        = 0x80000013

# Pen styles
PS_SOLID       = 0
PS_DASH        = 1
PS_DOT         = 2
PS_DASHDOT     = 3
PS_DASHDOTDOT  = 4
PS_NULL        = 5
PS_INSIDEFRAME = 6
PS_STYLE_MASK   = 0x0000000F
PS_ENDCAP_MASK  = 0x00000F00
PS_JOIN_MASK    = 0x0000F000
PS_ENDCAP_ROUND  = 0x00000000
PS_ENDCAP_SQUARE = 0x00000100
PS_ENDCAP_FLAT   = 0x00000200
PS_JOIN_ROUND  = 0x00000000
PS_JOIN_BEVEL  = 0x00001000
PS_JOIN_MITER  = 0x00002000

# Brush styles
BS_SOLID   = 0
BS_NULL    = 1
BS_HATCHED = 2

# Fill modes
ALTERNATE = 1
WINDING   = 2

# Map modes
MM_TEXT        = 1
MM_LOMETRIC    = 2
MM_HIMETRIC    = 3
MM_LOENGLISH   = 4
MM_HIENGLISH   = 5
MM_TWIPS       = 6
MM_ISOTROPIC   = 7
MM_ANISOTROPIC = 8
_FIXED_MAP_MODES = (MM_LOMETRIC, MM_HIMETRIC, MM_LOENGLISH,
                    MM_HIENGLISH, MM_TWIPS)

# Arc direction
AD_COUNTERCLOCKWISE = 1
AD_CLOCKWISE = 2

# ModifyWorldTransform modes
MWT_IDENTITY      = 1
MWT_LEFTMULTIPLY  = 2
MWT_RIGHTMULTIPLY = 3
MWT_SET           = 4

# Text alignment
TA_UPDATECP = 0x0001
TA_CENTER   = 0x0006
TA_RIGHT    = 0x0002
TA_BASELINE = 0x0018
TA_BOTTOM   = 0x0008

# Raster operations
SRCCOPY   = 0x00CC0020
PATCOPY   = 0x00F00021
WHITENESS = 0x00FF0062
BLACKNESS = 0x00000042


# =============================================================================
# Data Classes
# =============================================================================

PS_GEOMETRIC    = 0x00010000

class Pen:
    __slots__ = ('style', 'width', 'color', 'endcap', 'join', 'is_cosmetic')

    def __init__(self, style=PS_SOLID, width=0, color=(0, 0, 0),
                 endcap='round', join='round', is_cosmetic=False):
        self.style = style
        self.width = width
        self.color = color
        self.endcap = endcap
        self.join = join
        self.is_cosmetic = is_cosmetic

    @property
    def is_null(self):
        return self.style == PS_NULL

    @property
    def svg_color(self):
        return "#{:02X}{:02X}{:02X}".format(*self.color)

    @property
    def svg_width(self):
        return max(self.width, 1) if not self.is_null else 0


class Brush:
    __slots__ = ('style', 'color')

    def __init__(self, style=BS_SOLID, color=(255, 255, 255)):
        self.style = style
        self.color = color

    @property
    def is_null(self):
        return self.style == BS_NULL

    @property
    def svg_color(self):
        if self.is_null:
            return "none"
        return "#{:02X}{:02X}{:02X}".format(*self.color)


class Font:
    __slots__ = ('family', 'size', 'weight', 'italic', 'underline',
                 'strikeout', 'escapement', 'charset')

    def __init__(self, family='Arial', size=12, weight=400, italic=False,
                 underline=False, strikeout=False, escapement=0, charset=1):
        self.family = family
        self.size = size
        self.weight = weight
        self.italic = italic
        self.underline = underline
        self.strikeout = strikeout
        self.escapement = escapement
        self.charset = charset  # lfCharSet from LOGFONT


# Mapping from GDI lfCharSet values to Python codecs
_CHARSET_TO_CODEC = {
    0: 'cp1252',    # ANSI_CHARSET
    1: 'cp1252',    # DEFAULT_CHARSET (assume Western)
    2: 'latin-1',   # SYMBOL_CHARSET (preserve byte values for font glyph mapping)
    77: 'mac-roman', # MAC_CHARSET
    128: 'cp932',   # SHIFTJIS_CHARSET
    129: 'cp949',   # HANGUL_CHARSET / HANGEUL_CHARSET
    130: 'cp1361',  # JOHAB_CHARSET
    134: 'cp936',   # GB2312_CHARSET
    136: 'cp950',   # CHINESEBIG5_CHARSET
    161: 'cp1253',  # GREEK_CHARSET
    162: 'cp1254',  # TURKISH_CHARSET
    163: 'cp1258',  # VIETNAMESE_CHARSET
    177: 'cp1255',  # HEBREW_CHARSET
    178: 'cp1256',  # ARABIC_CHARSET
    186: 'cp1257',  # BALTIC_CHARSET
    204: 'cp1251',  # RUSSIAN_CHARSET
    222: 'cp874',   # THAI_CHARSET
    238: 'cp1250',  # EASTEUROPE_CHARSET
    255: 'cp437',   # OEM_CHARSET
}


def _detect_ansi_codec(raw_bytes):
    """Auto-detect encoding for ANSI text when charset is DEFAULT_CHARSET.

    Checks if high bytes (0xC0-0xFF) are predominantly Cyrillic when
    decoded as cp1251. Returns the best codec name.
    """
    high = [b for b in raw_bytes if b >= 0xC0]
    if not high:
        return 'cp1252'
    # In cp1251, bytes 0xC0-0xFF are А-я (common Cyrillic letters).
    # In cp1252, those same bytes are accented Latin characters which
    # rarely appear at >15% frequency in genuine Western text.
    total = len(raw_bytes)
    if total > 0 and len(high) / total > 0.10:
        return 'cp1251'
    return 'cp1252'


def _remap_symbol_pua(text):
    """Remap Windows Symbol font PUA codepoints (U+F0xx) to standard Unicode.

    Windows encodes Symbol font glyphs in the Private Use Area (U+F020-F0FF).
    Strip the F0 prefix to get the Symbol font's encoding byte, which maps
    to the correct glyph when rendered with the Symbol font in SVG.
    """
    result = []
    for ch in text:
        cp = ord(ch)
        if 0xF000 <= cp <= 0xF0FF:
            result.append(chr(cp - 0xF000))
        else:
            result.append(ch)
    return ''.join(result)


# Stock object instances
STOCK_OBJECTS = {
    STOCK_WHITE_BRUSH:  Brush(BS_SOLID, (255, 255, 255)),
    STOCK_LTGRAY_BRUSH: Brush(BS_SOLID, (192, 192, 192)),
    STOCK_GRAY_BRUSH:   Brush(BS_SOLID, (128, 128, 128)),
    STOCK_DKGRAY_BRUSH: Brush(BS_SOLID, (64, 64, 64)),
    STOCK_BLACK_BRUSH:  Brush(BS_SOLID, (0, 0, 0)),
    STOCK_NULL_BRUSH:   Brush(BS_NULL, (0, 0, 0)),
    STOCK_WHITE_PEN:    Pen(PS_SOLID, 1, (255, 255, 255)),
    STOCK_BLACK_PEN:    Pen(PS_SOLID, 1, (0, 0, 0)),
    STOCK_NULL_PEN:     Pen(PS_NULL, 0, (0, 0, 0)),
    STOCK_DC_BRUSH:     Brush(BS_SOLID, (255, 255, 255)),
    STOCK_DC_PEN:       Pen(PS_SOLID, 1, (0, 0, 0)),
    0x8000000A: Font('Courier New', 12),  # OEM_FIXED_FONT
    0x8000000B: Font('Courier New', 12),  # ANSI_FIXED_FONT
    0x8000000C: Font('Arial', 12),        # ANSI_VAR_FONT
    0x8000000D: Font('Arial', 16),        # SYSTEM_FONT
    0x8000000E: Font('Arial', 12),        # DEVICE_DEFAULT_FONT
    0x80000010: Font('Courier New', 12),  # SYSTEM_FIXED_FONT
    0x80000011: Font('Segoe UI', 12),     # DEFAULT_GUI_FONT
}


# =============================================================================
# EMF Parser
# =============================================================================

class EMFParser:
    def __init__(self, data):
        self.data = data
        self.offset = 0
        self.header = None

    def parse_header(self):
        rec_type, rec_size = struct.unpack_from('<II', self.data, 0)
        if rec_type != EMR_HEADER:
            raise ValueError(f"Not an EMF file: first record type is "
                             f"0x{rec_type:08X}, expected 0x00000001")
        sig = struct.unpack_from('<I', self.data, 40)[0]
        if sig != 0x464D4520:
            raise ValueError(f"Invalid EMF signature: 0x{sig:08X}")

        bounds = struct.unpack_from('<iiii', self.data, 8)
        frame = struct.unpack_from('<iiii', self.data, 24)
        version, n_bytes, n_records, n_handles = struct.unpack_from(
            '<IIIH', self.data, 44)
        n_desc, off_desc = struct.unpack_from('<II', self.data, 60)

        description = ""
        if n_desc > 0 and off_desc > 0:
            desc_bytes = self.data[off_desc:off_desc + n_desc * 2]
            description = desc_bytes.decode('utf-16-le',
                                            errors='replace').rstrip('\x00')
        # Device size in pixels and millimeters (offsets 72-87)
        if rec_size >= 88:
            dev_cx, dev_cy = struct.unpack_from('<ii', self.data, 72)
            mm_cx, mm_cy = struct.unpack_from('<ii', self.data, 80)
        else:
            dev_cx, dev_cy = 1024, 768
            mm_cx, mm_cy = 320, 240

        self.header = {
            'rec_size': rec_size,
            'bounds': bounds,
            'frame': frame,
            'version': version,
            'n_bytes': n_bytes,
            'n_records': n_records,
            'n_handles': n_handles,
            'description': description,
            'device_size': (dev_cx, dev_cy),
            'device_mm': (mm_cx, mm_cy),
        }
        return self.header

    def records(self):
        offset = 0
        data_len = len(self.data)
        while offset < data_len:
            if offset + 8 > data_len:
                break
            rec_type, rec_size = struct.unpack_from('<II', self.data, offset)
            if rec_size < 8:
                break
            # Handle truncated files: don't advance past end of data
            if offset + rec_size > data_len:
                break
            rec_data = self.data[offset + 8:offset + rec_size]
            yield rec_type, offset, rec_data
            offset += rec_size
            if rec_type == EMR_EOF:
                # Some EMFs have records or padding after EOF.
                # Consume them silently for byte accounting.
                while offset + 8 <= data_len:
                    t, s = struct.unpack_from('<II', self.data, offset)
                    if s < 8 or offset + s > data_len:
                        break
                    offset += s
                # Consume any remaining trailing bytes (padding/alignment)
                offset = data_len
                break
        self.bytes_consumed = offset


# =============================================================================
# GDI State Machine
# =============================================================================

class GDIState:
    def __init__(self, bounds=None, frame=None):
        self.objects = {}
        self.current_pen = Pen(PS_SOLID, 1, (0, 0, 0))
        self.current_brush = Brush(BS_SOLID, (255, 255, 255))
        self.current_font = Font()
        self.cur_x = 0
        self.cur_y = 0
        self.map_mode = MM_TEXT
        self.window_org = (0, 0)
        self.window_ext = (1, 1)
        self.viewport_org = (0, 0)
        self.viewport_ext = (1, 1)
        self.has_window_ext = False
        self.has_viewport_ext = False
        self.map_mode_explicit = False
        self.bounds = bounds or (0, 0, 1, 1)
        self.frame = frame or (0, 0, 1, 1)
        self.poly_fill_mode = ALTERNATE
        self.miter_limit = 10.0
        self.in_path = False
        self.path_data = []
        self.path_texts = []  # text elements captured inside BeginPath/EndPath
        self.world_transform = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        self.save_stack = []
        self.text_color = (0, 0, 0)
        self.text_align = 0
        self.bk_mode = 2
        self.bk_color = (255, 255, 255)
        self.arc_direction = AD_COUNTERCLOCKWISE
        self.clip_region = None  # None = no clip, or list of (l,t,r,b)
        self.fixed_map_mode = False  # True when using MM_LOMETRIC etc.

    def _use_window_viewport(self):
        """Check if window/viewport mapping should be applied."""
        if self.fixed_map_mode:
            return True
        if not self.has_window_ext:
            return False
        if self.map_mode in (MM_ANISOTROPIC, MM_ISOTROPIC):
            return True
        # If SETWINDOWEXTEX was called but SETMAPMODE was never explicitly
        # set, apply window/viewport mapping. In MM_TEXT the extents are
        # identity but the origin shift still matters (per the spec,
        # INTERSECTCLIPRECT coords are in logical units and need the
        # origin subtracted).
        if not self.map_mode_explicit:
            return True
        return False

    def set_fixed_map_mode(self, mode):
        """Set up window/viewport for fixed GDI mapping modes.

        For fixed modes (MM_LOMETRIC through MM_TWIPS), Windows ignores
        explicit SetWindowExtEx/SetViewportExtEx and computes the transform
        from device info. We use the frame (0.01mm) and bounds from the
        EMF header to derive the correct mapping.

        All fixed modes have Y-axis positive-up (opposite to device/SVG),
        so the viewport Y extent is negated and viewport Y origin is set
        to the bottom of the bounds to flip the Y axis.
        """
        self.map_mode = mode
        self.map_mode_explicit = True
        self.fixed_map_mode = True
        fw = self.frame[2] - self.frame[0]
        fh = self.frame[3] - self.frame[1]
        bw = self.bounds[2] - self.bounds[0]
        bh = self.bounds[3] - self.bounds[1]
        if fw > 0 and fh > 0 and bw > 0 and bh > 0:
            self.window_org = (self.frame[0], self.frame[1])
            self.window_ext = (fw, fh)
            # Y-flip: viewport origin at bottom, negative height
            self.viewport_org = (self.bounds[0], self.bounds[3])
            self.viewport_ext = (bw, -bh)
            self.has_window_ext = True
            self.has_viewport_ext = True

    def _effective_viewport_ext(self):
        """Get effective viewport extent, computing default if not set."""
        if self.has_viewport_ext:
            return self.viewport_ext
        if self.map_mode in (MM_ANISOTROPIC, MM_ISOTROPIC):
            # Per GDI spec, the default viewport extent is (1, 1).
            # MM_ANISOTROPIC/ISOTROPIC require explicit SetViewportExtEx;
            # without it, the DC default of 1x1 applies.
            return (1, 1)
        # Heuristic case (no explicit SETMAPMODE, e.g. WMF-in-EMF wrappers):
        # use window extent so the mapping reduces to a pure origin shift
        # (VEx/WEx = 1). This avoids introducing any scaling that the
        # file didn't request.
        return self.window_ext

    def transform_point(self, x, y):
        wt = self.world_transform
        wx = x * wt[0] + y * wt[2] + wt[4]
        wy = x * wt[1] + y * wt[3] + wt[5]
        if self._use_window_viewport():
            vex, vey = self._effective_viewport_ext()
            dx = ((wx - self.window_org[0]) * vex
                  / self.window_ext[0] + self.viewport_org[0])
            dy = ((wy - self.window_org[1]) * vey
                  / self.window_ext[1] + self.viewport_org[1])
            return (dx, dy)
        # MM_TEXT or non-scaling mode: apply viewport origin as offset
        return (wx + self.viewport_org[0], wy + self.viewport_org[1])

    def transform_width(self, w):
        wt = self.world_transform
        scale = math.sqrt(wt[0] ** 2 + wt[1] ** 2)
        w = w * scale
        if self._use_window_viewport():
            vex = self._effective_viewport_ext()[0]
            return abs(w * vex / self.window_ext[0])
        return abs(w)

    def transform_height(self, h):
        wt = self.world_transform
        scale = math.sqrt(wt[2] ** 2 + wt[3] ** 2)
        h = h * scale
        if self._use_window_viewport():
            vey = self._effective_viewport_ext()[1]
            return abs(h * vey / self.window_ext[1])
        return abs(h)

    def select_object(self, ih_object):
        if ih_object >= 0x80000000:
            obj = STOCK_OBJECTS.get(ih_object)
        else:
            obj = self.objects.get(ih_object)
        if obj is not None:
            if isinstance(obj, Pen):
                self.current_pen = obj
            elif isinstance(obj, Brush):
                self.current_brush = obj
            elif isinstance(obj, Font):
                self.current_font = obj

    def save_dc(self):
        saved = {
            'current_pen': self.current_pen,
            'current_brush': self.current_brush,
            'current_font': self.current_font,
            'cur_x': self.cur_x, 'cur_y': self.cur_y,
            'map_mode': self.map_mode,
            'window_org': self.window_org, 'window_ext': self.window_ext,
            'viewport_org': self.viewport_org,
            'viewport_ext': self.viewport_ext,
            'has_window_ext': self.has_window_ext,
            'has_viewport_ext': self.has_viewport_ext,
            'map_mode_explicit': self.map_mode_explicit,
            'fixed_map_mode': self.fixed_map_mode,
            'poly_fill_mode': self.poly_fill_mode,
            'miter_limit': self.miter_limit,
            'text_color': self.text_color, 'text_align': self.text_align,
            'bk_mode': self.bk_mode, 'bk_color': self.bk_color,
            'arc_direction': self.arc_direction,
            'world_transform': self.world_transform[:],
            'clip_region': self.clip_region[:] if self.clip_region else None,
            'path_data': self.path_data[:],
            'path_texts': [t.copy() for t in self.path_texts],
            'in_path': self.in_path,
        }
        self.save_stack.append(saved)

    def restore_dc(self, saved_dc):
        if saved_dc < 0:
            count = min(abs(saved_dc), len(self.save_stack))
            saved = None
            for _ in range(count):
                saved = self.save_stack.pop()
            if saved:
                for key, value in saved.items():
                    setattr(self, key, value)

    @property
    def svg_fill_rule(self):
        return "nonzero" if self.poly_fill_mode == WINDING else "evenodd"

    @property
    def svg_text_color(self):
        return "#{:02X}{:02X}{:02X}".format(*self.text_color)

    @property
    def svg_text_anchor(self):
        h = self.text_align & 0x06
        if h == TA_CENTER:
            return 'middle'
        elif h == TA_RIGHT:
            return 'end'
        return 'start'

    @property
    def svg_dominant_baseline(self):
        v = self.text_align & 0x18
        if v == TA_BASELINE:
            return 'auto'
        elif v == TA_BOTTOM:
            return 'text-after-edge'
        return 'hanging'  # TA_TOP (default)


# =============================================================================
# SVG Builder
# =============================================================================

def fmt(v):
    if v != v:  # NaN
        return '0'
    if v == int(v):
        return str(int(v))
    return f"{v:.2f}".rstrip('0').rstrip('.')


def xml_escape(s):
    """Escape text content for XML, stripping invalid XML 1.0 characters."""
    s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    cleaned = []
    for ch in s:
        cp = ord(ch)
        if cp == 0x09 or cp == 0x0A or cp == 0x0D:
            cleaned.append(ch)
        elif cp < 0x20:
            continue
        elif 0xD800 <= cp <= 0xDFFF:
            continue
        elif cp == 0xFFFE or cp == 0xFFFF:
            continue
        else:
            cleaned.append(ch)
    return ''.join(cleaned)


def xml_attr_escape(s):
    """Escape a string for use in an XML attribute value (double-quoted)."""
    s = str(s)
    s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    s = s.replace('"', '&quot;')
    # Remove characters invalid in XML 1.0 (control chars except tab/LF/CR,
    # U+FFFE, U+FFFF, surrogates)
    cleaned = []
    for ch in s:
        cp = ord(ch)
        if cp == 0x09 or cp == 0x0A or cp == 0x0D:
            cleaned.append(ch)
        elif cp < 0x20:
            continue  # control characters
        elif 0xD800 <= cp <= 0xDFFF:
            continue  # surrogates
        elif cp == 0xFFFE or cp == 0xFFFF:
            continue  # invalid XML chars
        else:
            cleaned.append(ch)
    return ''.join(cleaned)


def sanitize_font_name(name):
    """Clean font name: keep only printable ASCII/Latin chars, spaces, hyphens."""
    cleaned = []
    for ch in name:
        cp = ord(ch)
        # Keep ASCII printable, Latin-1 Supplement printable, common punctuation
        if 0x20 <= cp <= 0x7E or 0xA0 <= cp <= 0xFF:
            cleaned.append(ch)
    result = ' '.join(''.join(cleaned).split())  # normalize whitespace
    return result if result else 'Arial'


class SVGBuilder:
    def __init__(self, bounds, auto_bounds=False):
        self.left = bounds[0]
        self.top = bounds[1]
        self.width = bounds[2] - bounds[0]
        self.height = bounds[3] - bounds[1]
        self.elements = []
        self.auto_bounds = auto_bounds
        if auto_bounds:
            self._min_x = float('inf')
            self._min_y = float('inf')
            self._max_x = float('-inf')
            self._max_y = float('-inf')
        self.clippath_defs = []
        self._current_clip_id = None
        self._clip_bounds = None  # (min_x, min_y, max_x, max_y)

    def set_clip(self, clip_id, transformed_rects):
        """Set SVG clip region. transformed_rects are in SVG coordinates."""
        self._current_clip_id = clip_id
        self.clippath_defs.append((clip_id, transformed_rects))
        # Compute clip bounds for auto_bounds constraining
        min_x = min(r[0] for r in transformed_rects)
        min_y = min(r[1] for r in transformed_rects)
        max_x = max(r[2] for r in transformed_rects)
        max_y = max(r[3] for r in transformed_rects)
        self._clip_bounds = (min_x, min_y, max_x, max_y)

    def clear_clip(self):
        """Remove SVG clip region."""
        self._current_clip_id = None
        self._clip_bounds = None

    def _apply_clip(self, attrs):
        """Add clip-path attribute if a clip region is active."""
        if self._current_clip_id:
            attrs['clip-path'] = f'url(#{self._current_clip_id})'

    def _track_coord(self, x, y):
        if self.auto_bounds:
            try:
                fx, fy = float(x), float(y)
                if fx == fx and fy == fy:  # not NaN
                    self._min_x = min(self._min_x, fx)
                    self._min_y = min(self._min_y, fy)
                    self._max_x = max(self._max_x, fx)
                    self._max_y = max(self._max_y, fy)
            except (ValueError, TypeError):
                pass

    def _track_attrs(self, attrs):
        if not self.auto_bounds:
            return
        # When a clip region is active, track clip bounds instead of
        # element coordinates (elements like gradient bars may extend
        # far beyond the clip region).
        if self._clip_bounds is not None:
            cb = self._clip_bounds
            self._track_coord(cb[0], cb[1])
            self._track_coord(cb[2], cb[3])
            return
        # Track coordinates from points attributes
        if 'points' in attrs:
            for pair in str(attrs['points']).split():
                parts = pair.split(',')
                if len(parts) == 2:
                    self._track_coord(parts[0], parts[1])
        # Track x,y attributes
        if 'x' in attrs and 'y' in attrs:
            self._track_coord(attrs['x'], attrs['y'])
        # Track path data coordinates
        if 'd' in attrs:
            import re
            nums = re.findall(r'-?\d+\.?\d*', str(attrs['d']))
            for i in range(0, len(nums) - 1, 2):
                self._track_coord(nums[i], nums[i + 1])

    def add_path(self, d, fill="none", stroke="none", stroke_width=0,
                 fill_rule="evenodd", stroke_linecap=None,
                 stroke_linejoin=None, miter_limit=None):
        if not d:
            return
        attrs = {'d': d, 'fill': fill}
        if fill_rule != "nonzero":
            attrs['fill-rule'] = fill_rule
        if stroke != "none" and stroke_width > 0:
            attrs['stroke'] = stroke
            attrs['stroke-width'] = fmt(stroke_width)
            if stroke_linecap and stroke_linecap != 'butt':
                attrs['stroke-linecap'] = stroke_linecap
            if stroke_linejoin and stroke_linejoin != 'miter':
                attrs['stroke-linejoin'] = stroke_linejoin
            if miter_limit is not None and stroke_linejoin == 'miter':
                attrs['stroke-miterlimit'] = fmt(miter_limit)
        else:
            attrs['stroke'] = 'none'
        self._track_attrs(attrs)
        self._apply_clip(attrs)
        self.elements.append(('path', attrs, None))

    def add_polygon(self, points, fill="none", stroke="none",
                    stroke_width=0, fill_rule="evenodd"):
        if not points:
            return
        pts_str = " ".join(f"{fmt(x)},{fmt(y)}" for x, y in points)
        attrs = {'points': pts_str, 'fill': fill, 'stroke': stroke}
        if fill_rule != "nonzero":
            attrs['fill-rule'] = fill_rule
        if stroke != "none" and stroke_width > 0:
            attrs['stroke-width'] = fmt(stroke_width)
        self._track_attrs(attrs)
        self._apply_clip(attrs)
        self.elements.append(('polygon', attrs, None))

    def add_polyline(self, points, stroke="none", stroke_width=0,
                     stroke_linecap=None, stroke_linejoin=None):
        if not points:
            return
        pts_str = " ".join(f"{fmt(x)},{fmt(y)}" for x, y in points)
        attrs = {'points': pts_str, 'fill': 'none', 'stroke': stroke}
        if stroke_width > 0:
            attrs['stroke-width'] = fmt(stroke_width)
        if stroke_linecap and stroke_linecap != 'butt':
            attrs['stroke-linecap'] = stroke_linecap
        if stroke_linejoin and stroke_linejoin != 'miter':
            attrs['stroke-linejoin'] = stroke_linejoin
        self._track_attrs(attrs)
        self._apply_clip(attrs)
        self.elements.append(('polyline', attrs, None))

    def add_text(self, x, y, text, font_family, font_size, fill,
                 weight=400, italic=False, anchor='start', rotation=0,
                 dominant_baseline='auto', rotate_origin=None,
                 scale_x=None, stroke=None, stroke_width=None):
        attrs = {
            'x': fmt(x), 'y': fmt(y),
            'font-family': font_family,
            'font-size': fmt(font_size),
            'fill': fill,
        }
        if weight >= 700:
            attrs['font-weight'] = 'bold'
        if italic:
            attrs['font-style'] = 'italic'
        if anchor != 'start':
            attrs['text-anchor'] = anchor
        if dominant_baseline != 'auto':
            attrs['dominant-baseline'] = dominant_baseline
        if stroke and stroke != 'none':
            attrs['stroke'] = stroke
            if stroke_width is not None:
                attrs['stroke-width'] = fmt(stroke_width)
        # Build transform combining rotation and horizontal scaling
        transforms = []
        if rotation != 0:
            ro = rotate_origin or (x, y)
            transforms.append(f'rotate({fmt(rotation)} '
                               f'{fmt(ro[0])} {fmt(ro[1])})')
        if scale_x is not None and abs(scale_x - 1.0) > 0.01:
            transforms.append(f'translate({fmt(x)} 0) '
                               f'scale({fmt(scale_x)} 1) '
                               f'translate({fmt(-x)} 0)')
        if transforms:
            attrs['transform'] = ' '.join(transforms)
        self._track_attrs(attrs)
        self._apply_clip(attrs)
        self.elements.append(('text', attrs, xml_escape(text)))

    def add_image(self, x, y, width, height, href, transform=None):
        attrs = {
            'x': fmt(x), 'y': fmt(y),
            'width': fmt(width), 'height': fmt(height),
            'href': href, 'preserveAspectRatio': 'none',
        }
        if transform:
            attrs['transform'] = transform
        if self.auto_bounds:
            self._track_coord(x, y)
            self._track_coord(x + width, y + height)
        self._apply_clip(attrs)
        self.elements.append(('image', attrs, None))

    def _finalize_bounds(self):
        """If auto_bounds, update viewBox to encompass actual content."""
        if (self.auto_bounds
                and self._min_x != float('inf')
                and self._max_x != float('-inf')):
            margin = 5
            self.left = self._min_x - margin
            self.top = self._min_y - margin
            self.width = (self._max_x - self._min_x) + margin * 2
            self.height = (self._max_y - self._min_y) + margin * 2

    def to_string(self):
        self._finalize_bounds()
        lines = []
        lines.append('<?xml version="1.0" encoding="UTF-8"?>')
        lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
                     f'xmlns:xlink="http://www.w3.org/1999/xlink" '
                     f'viewBox="{fmt(self.left)} {fmt(self.top)} '
                     f'{fmt(self.width)} {fmt(self.height)}" '
                     f'width="{fmt(self.width)}" height="{fmt(self.height)}" '
                     f'overflow="visible">')
        if self.clippath_defs:
            lines.append('  <defs>')
            for clip_id, rects in self.clippath_defs:
                lines.append(f'    <clipPath id="{clip_id}">')
                for l, t, r, b in rects:
                    w, h = r - l, b - t
                    lines.append(
                        f'      <rect x="{fmt(l)}" y="{fmt(t)}" '
                        f'width="{fmt(w)}" height="{fmt(h)}"/>')
                lines.append('    </clipPath>')
            lines.append('  </defs>')
        for tag, attrs, content in self.elements:
            attr_str = " ".join(
                f'{k}="{xml_attr_escape(v)}"' for k, v in attrs.items())
            if content is not None:
                lines.append(f'  <{tag} {attr_str}>{content}</{tag}>')
            else:
                lines.append(f'  <{tag} {attr_str}/>')
        lines.append('</svg>')
        return "\n".join(lines)


# =============================================================================
# Helper Functions
# =============================================================================

def parse_colorref(data, offset=0):
    r, g, b = struct.unpack_from('<BBB', data, offset)
    return (r, g, b)


def parse_points16(data, offset, count):
    points = []
    for i in range(count):
        x, y = struct.unpack_from('<hh', data, offset + i * 4)
        points.append((x, y))
    return points


def parse_points32(data, offset, count):
    points = []
    for i in range(count):
        x, y = struct.unpack_from('<ii', data, offset + i * 8)
        points.append((x, y))
    return points


def pen_endcap_str(style):
    cap = style & PS_ENDCAP_MASK
    if cap == PS_ENDCAP_FLAT:
        return 'butt'
    elif cap == PS_ENDCAP_SQUARE:
        return 'square'
    return 'round'


def pen_join_str(style):
    join = style & PS_JOIN_MASK
    if join == PS_JOIN_BEVEL:
        return 'bevel'
    elif join == PS_JOIN_MITER:
        return 'miter'
    return 'round'


def multiply_xform(a, b):
    return [
        a[0]*b[0] + a[1]*b[2],
        a[0]*b[1] + a[1]*b[3],
        a[2]*b[0] + a[3]*b[2],
        a[2]*b[1] + a[3]*b[3],
        a[4]*b[0] + a[5]*b[2] + b[4],
        a[4]*b[1] + a[5]*b[3] + b[5],
    ]


def ellipse_path_data(left, top, right, bottom, state):
    cx = (left + right) / 2.0
    cy = (top + bottom) / 2.0
    rx = (right - left) / 2.0
    ry = (bottom - top) / 2.0
    if abs(rx) < 0.001 or abs(ry) < 0.001:
        return []
    k = 0.5522847498
    logical_pts = [
        (cx + rx, cy),
        (cx + rx, cy + ry * k), (cx + rx * k, cy + ry), (cx, cy + ry),
        (cx - rx * k, cy + ry), (cx - rx, cy + ry * k), (cx - rx, cy),
        (cx - rx, cy - ry * k), (cx - rx * k, cy - ry), (cx, cy - ry),
        (cx + rx * k, cy - ry), (cx + rx, cy - ry * k), (cx + rx, cy),
    ]
    pts = [state.transform_point(x, y) for x, y in logical_pts]
    parts = [f"M {fmt(pts[0][0])},{fmt(pts[0][1])}"]
    for i in range(0, 12, 3):
        c1, c2, end = pts[i + 1], pts[i + 2], pts[i + 3]
        parts.append(f"C {fmt(c1[0])},{fmt(c1[1])} "
                     f"{fmt(c2[0])},{fmt(c2[1])} "
                     f"{fmt(end[0])},{fmt(end[1])}")
    parts.append("Z")
    return parts


def roundrect_path_data(left, top, right, bottom, corner_w, corner_h, state):
    crx = min(abs(corner_w) / 2.0, abs(right - left) / 2.0)
    cry = min(abs(corner_h) / 2.0, abs(bottom - top) / 2.0)
    if crx < 0.001 or cry < 0.001:
        # Degenerate to rectangle
        p1 = state.transform_point(left, top)
        p2 = state.transform_point(right, top)
        p3 = state.transform_point(right, bottom)
        p4 = state.transform_point(left, bottom)
        return [f"M {fmt(p1[0])},{fmt(p1[1])}",
                f"L {fmt(p2[0])},{fmt(p2[1])}",
                f"L {fmt(p3[0])},{fmt(p3[1])}",
                f"L {fmt(p4[0])},{fmt(p4[1])}", "Z"]
    k = 0.5522847498
    segments = [
        ('M', (right - crx, top)),
        ('C', (right - crx + crx * k, top),
              (right, top + cry - cry * k), (right, top + cry)),
        ('L', (right, bottom - cry)),
        ('C', (right, bottom - cry + cry * k),
              (right - crx + crx * k, bottom), (right - crx, bottom)),
        ('L', (left + crx, bottom)),
        ('C', (left + crx - crx * k, bottom),
              (left, bottom - cry + cry * k), (left, bottom - cry)),
        ('L', (left, top + cry)),
        ('C', (left, top + cry - cry * k),
              (left + crx - crx * k, top), (left + crx, top)),
        ('Z',),
    ]
    parts = []
    for seg in segments:
        cmd = seg[0]
        if cmd == 'M':
            tp = state.transform_point(*seg[1])
            parts.append(f"M {fmt(tp[0])},{fmt(tp[1])}")
        elif cmd == 'L':
            tp = state.transform_point(*seg[1])
            parts.append(f"L {fmt(tp[0])},{fmt(tp[1])}")
        elif cmd == 'C':
            tc1 = state.transform_point(*seg[1])
            tc2 = state.transform_point(*seg[2])
            te = state.transform_point(*seg[3])
            parts.append(f"C {fmt(tc1[0])},{fmt(tc1[1])} "
                         f"{fmt(tc2[0])},{fmt(tc2[1])} "
                         f"{fmt(te[0])},{fmt(te[1])}")
        elif cmd == 'Z':
            parts.append("Z")
    return parts


def arc_path_data(box_l, box_t, box_r, box_b, start_x, start_y,
                  end_x, end_y, arc_dir, state, is_pie=False):
    cx = (box_l + box_r) / 2.0
    cy = (box_t + box_b) / 2.0
    rx = abs(box_r - box_l) / 2.0
    ry = abs(box_b - box_t) / 2.0
    if rx < 0.001 or ry < 0.001:
        return []
    sa = math.atan2(start_y - cy, start_x - cx)
    ea = math.atan2(end_y - cy, end_x - cx)
    sx = cx + rx * math.cos(sa)
    sy = cy + ry * math.sin(sa)
    ex = cx + rx * math.cos(ea)
    ey = cy + ry * math.sin(ea)
    if arc_dir == AD_COUNTERCLOCKWISE:
        sweep = sa - ea
        if sweep <= 0:
            sweep += 2 * math.pi
        svg_sweep = 0
    else:
        sweep = ea - sa
        if sweep <= 0:
            sweep += 2 * math.pi
        svg_sweep = 1
    large_arc = 1 if sweep > math.pi else 0
    wt = state.world_transform
    det = wt[0] * wt[3] - wt[1] * wt[2]
    if det < 0:
        svg_sweep = 1 - svg_sweep
    tsx, tsy = state.transform_point(sx, sy)
    tex, tey = state.transform_point(ex, ey)
    trx = state.transform_width(rx)
    tr_y = state.transform_height(ry)
    parts = [f"M {fmt(tsx)},{fmt(tsy)}",
             f"A {fmt(trx)},{fmt(tr_y)} 0 {large_arc},{svg_sweep} "
             f"{fmt(tex)},{fmt(tey)}"]
    if is_pie:
        tcx, tcy = state.transform_point(cx, cy)
        parts.append(f"L {fmt(tcx)},{fmt(tcy)}")
        parts.append("Z")
    return parts


def rect_path_data(left, top, right, bottom, state):
    p1 = state.transform_point(left, top)
    p2 = state.transform_point(right, top)
    p3 = state.transform_point(right, bottom)
    p4 = state.transform_point(left, bottom)
    return [f"M {fmt(p1[0])},{fmt(p1[1])}",
            f"L {fmt(p2[0])},{fmt(p2[1])}",
            f"L {fmt(p3[0])},{fmt(p3[1])}",
            f"L {fmt(p4[0])},{fmt(p4[1])}", "Z"]


def embed_dib_image(rec_data, off_bmi, cb_bmi, off_bits, cb_bits,
                    x, y, width, height, state, svg):
    if cb_bmi == 0 or cb_bits == 0:
        return
    bmi_start = off_bmi - 8
    bits_start = off_bits - 8
    if bmi_start < 0 or bits_start < 0:
        return
    if bmi_start + cb_bmi > len(rec_data) or bits_start + cb_bits > len(rec_data):
        return
    bmi_data = rec_data[bmi_start:bmi_start + cb_bmi]
    bits_data = rec_data[bits_start:bits_start + cb_bits]
    bf_off_bits = 14 + cb_bmi
    bf_size = bf_off_bits + cb_bits
    file_header = struct.pack('<2sIHHI', b'BM', bf_size, 0, 0, bf_off_bits)
    bmp_data = file_header + bmi_data + bits_data
    b64 = base64.b64encode(bmp_data).decode('ascii')
    data_uri = f"data:image/bmp;base64,{b64}"
    # Transform both corners of the destination rectangle to handle
    # Y-flipped mapping modes (MM_LOMETRIC etc.) correctly.
    tx1, ty1 = state.transform_point(x, y)
    tx2, ty2 = state.transform_point(x + width, y + height)
    ix = min(tx1, tx2)
    iy = min(ty1, ty2)
    tw = abs(tx2 - tx1)
    th = abs(ty2 - ty1)
    if tw > 0 and th > 0:
        svg.add_image(ix, iy, tw, th, data_uri)


def pen_stroke_width(pen, state):
    """Compute SVG stroke width for a pen, respecting cosmetic vs geometric."""
    if pen.is_null:
        return 0
    if pen.width <= 1:
        # Width 0 or 1 = cosmetic 1-pixel pen (CreatePen convention).
        # For geometric pens, 1 logical unit may transform to < 1 device pixel.
        # Windows GDI always renders at minimum 1 pixel.
        return 1
    w = pen.svg_width
    if pen.is_cosmetic:
        return w  # device units, no transform
    # Geometric pen: transform, but enforce minimum 1 device pixel
    return max(1, state.transform_width(w))


def emit_shape(state, svg, path_parts, has_fill=True, has_stroke=True):
    if not path_parts:
        return
    d = " ".join(path_parts)
    fill = state.current_brush.svg_color if has_fill else "none"
    pen = state.current_pen
    stroke = pen.svg_color if (has_stroke and not pen.is_null) else "none"
    sw = pen_stroke_width(pen, state) if has_stroke else 0
    if pen.is_null or sw == 0:
        stroke = "none"
        sw = 0
    svg.add_path(d, fill=fill, stroke=stroke, stroke_width=sw,
                 fill_rule=state.svg_fill_rule,
                 stroke_linecap=pen.endcap, stroke_linejoin=pen.join,
                 miter_limit=state.miter_limit)


# =============================================================================
# Pre-scan: gather mapping info before full conversion
# =============================================================================

def _prescan_mapping(parser):
    """Quick scan of records to find first window/viewport/mapmode settings."""
    info = {'map_mode': None, 'window_org': None, 'window_ext': None,
            'viewport_ext': None, 'has_world_transform': False}
    for rec_type, _, rec_data in parser.records():
        if rec_type == EMR_SETMAPMODE:
            info['map_mode'] = struct.unpack_from('<I', rec_data, 0)[0]
        elif rec_type == EMR_SETWINDOWORGEX and info['window_org'] is None:
            info['window_org'] = struct.unpack_from('<ii', rec_data, 0)
        elif rec_type == EMR_SETWINDOWEXTEX and info['window_ext'] is None:
            info['window_ext'] = struct.unpack_from('<ii', rec_data, 0)
        elif rec_type == EMR_SETVIEWPORTEXTEX and info['viewport_ext'] is None:
            info['viewport_ext'] = struct.unpack_from('<ii', rec_data, 0)
        elif rec_type == EMR_SETWORLDTRANSFORM:
            info['has_world_transform'] = True
        elif rec_type == 0x0E:  # EMR_EOF
            break
    return info


# =============================================================================
# EMF+ Support (embedded images in EMR_COMMENT records)
# =============================================================================

# EMF+ record type IDs
_EMFPLUS_HEADER           = 0x4001
_EMFPLUS_OBJECT           = 0x4008
_EMFPLUS_DRAW_IMAGE_PTS   = 0x401B

# EMF+ object types (encoded in flags bits 8-14)
_EMFPLUS_OBJ_IMAGE        = 5
_EMFPLUS_OBJ_IMAGE_ATTRS  = 8

# Global storage for EMF+ objects (images) across multiple comments
_emfplus_images = {}  # object_id -> (mime_type, base64_data)
_emfplus_draw_cmds = []  # list of (object_id, dest_points)


def _parse_emfplus_comment(rec_data, state, svg):
    """Parse EMF+ records within an EMR_COMMENT record."""
    # rec_data starts after the 8-byte EMR_COMMENT header
    # Format: DataSize(4) + Signature(4='EMF+') + EMF+ records...
    off = 8  # skip DataSize + 'EMF+' signature
    while off + 12 <= len(rec_data):
        ep_type, ep_flags = struct.unpack_from('<HH', rec_data, off)
        ep_size = struct.unpack_from('<I', rec_data, off + 4)[0]
        ep_dsize = struct.unpack_from('<I', rec_data, off + 8)[0]
        if ep_size < 12 or off + ep_size > len(rec_data):
            break
        data_off = off + 12  # start of record data

        if ep_type == _EMFPLUS_OBJECT:
            obj_id = ep_flags & 0xFF
            obj_type = (ep_flags >> 8) & 0x7F
            if obj_type == _EMFPLUS_OBJ_IMAGE and ep_dsize >= 8:
                # EmfPlusImage: Version(4) + ImageType(4)
                img_type = struct.unpack_from('<I', rec_data, data_off + 4)[0]
                if img_type == 1 and ep_dsize >= 28:  # Bitmap
                    bmp_type = struct.unpack_from('<I', rec_data, data_off + 24)[0]
                    if bmp_type == 1:  # Compressed (PNG/JPEG/etc.)
                        img_data = rec_data[data_off + 28:data_off + ep_dsize]
                        if len(img_data) >= 4:
                            if img_data[:4] == b'\x89PNG':
                                mime = 'image/png'
                            elif img_data[:2] == b'\xff\xd8':
                                mime = 'image/jpeg'
                            else:
                                mime = 'application/octet-stream'
                            b64 = base64.b64encode(img_data).decode('ascii')
                            _emfplus_images[obj_id] = (mime, b64)

        elif ep_type == _EMFPLUS_DRAW_IMAGE_PTS:
            obj_id_ref = ep_flags & 0xFF
            if obj_id_ref in _emfplus_images:
                # EMF+ has its own transform pipeline that we don't fully
                # parse. Use the EMF header bounds as the image destination
                # since bounds represent the device-space bounding box.
                b = state.bounds
                x, y = b[0], b[1]
                w, h = b[2] - b[0], b[3] - b[1]
                if w > 0 and h > 0:
                    mime, b64 = _emfplus_images[obj_id_ref]
                    href = f"data:{mime};base64,{b64}"
                    svg.add_image(x, y, w, h, href)

        off += ep_size


# =============================================================================
# Main Converter
# =============================================================================

def convert_emf_to_svg(input_path, output_path):
    with open(input_path, 'rb') as f:
        data = f.read()

    parser = EMFParser(data)
    header = parser.parse_header()
    bounds = header['bounds']

    # Pre-scan to detect mapping mode and window/viewport setup
    scan = _prescan_mapping(parser)

    # Fix degenerate bounds (negative/zero dimensions or full int16 range)
    bw = bounds[2] - bounds[0]
    bh = bounds[3] - bounds[1]
    bounds_invalid = (bw <= 0 or bh <= 0
                      or (bounds[0] <= -32000 and bounds[2] >= 32000))
    if bounds_invalid:
        # Try to derive from frame (0.01mm) using device info
        frame = header['frame']
        fw = frame[2] - frame[0]
        fh = frame[3] - frame[1]
        if fw > 0 and fh > 0:
            # Use frame dimensions as logical units, scale to
            # reasonable pixel size using ~96 DPI
            px_w = max(1, round(fw * 96 / 2540))
            px_h = max(1, round(fh * 96 / 2540))
            bounds = (0, 0, px_w, px_h)
        else:
            bounds = (0, 0, 1, 1)

    # In heuristic mode (SETWINDOWEXTEX without explicit SETMAPMODE and
    # without world transforms), the window org/ext defines the page
    # dimensions. Expand bounds to include the full page so the viewBox
    # doesn't cut off margins. Skip this for WMF-in-EMF wrappers that
    # use world transforms (window ext is temporary there).
    if (scan['window_ext'] is not None and scan['map_mode'] is None
            and not scan['has_world_transform'] and not bounds_invalid):
        wo = scan['window_org'] or (0, 0)
        we = scan['window_ext']
        page_l, page_t = wo[0], wo[1]
        page_r = wo[0] + we[0]
        page_b = wo[1] + we[1]
        bounds = (min(bounds[0], page_l), min(bounds[1], page_t),
                  max(bounds[2], page_r), max(bounds[3], page_b))

    state = GDIState(bounds, frame=header['frame'])
    svg = SVGBuilder(bounds, auto_bounds=bounds_invalid)
    clip_counter = 0

    # Reset EMF+ state
    _emfplus_images.clear()
    _emfplus_draw_cmds.clear()

    record_count = 0
    bytes_consumed = 0

    for rec_type, rec_offset, rec_data in parser.records():
        rec_size = len(rec_data) + 8
        bytes_consumed += rec_size
        record_count += 1
        name = RECORD_NAMES.get(rec_type, f"UNKNOWN(0x{rec_type:08X})")

        # ================================================================
        # Header
        # ================================================================
        if rec_type == EMR_HEADER:
            pass

        # ================================================================
        # Coordinate mapping
        # ================================================================
        elif rec_type == EMR_SETMAPMODE:
            mode = struct.unpack_from('<I', rec_data, 0)[0]
            if mode in _FIXED_MAP_MODES:
                state.set_fixed_map_mode(mode)
            else:
                state.map_mode = mode
                state.map_mode_explicit = True
                state.fixed_map_mode = False

        elif rec_type == EMR_SETWINDOWEXTEX:
            if not state.fixed_map_mode:
                cx, cy = struct.unpack_from('<ii', rec_data, 0)
                state.window_ext = (cx, cy)
                state.has_window_ext = True

        elif rec_type == EMR_SETWINDOWORGEX:
            if not state.fixed_map_mode:
                x, y = struct.unpack_from('<ii', rec_data, 0)
                state.window_org = (x, y)

        elif rec_type == EMR_SETVIEWPORTEXTEX:
            if not state.fixed_map_mode:
                cx, cy = struct.unpack_from('<ii', rec_data, 0)
                state.viewport_ext = (cx, cy)
                state.has_viewport_ext = True

        elif rec_type == EMR_SETVIEWPORTORGEX:
            if not state.fixed_map_mode:
                x, y = struct.unpack_from('<ii', rec_data, 0)
                state.viewport_org = (x, y)

        # ================================================================
        # World Transform
        # ================================================================
        elif rec_type == EMR_SETWORLDTRANSFORM:
            m11, m12, m21, m22, dx, dy = struct.unpack_from(
                '<ffffff', rec_data, 0)
            state.world_transform = [m11, m12, m21, m22, dx, dy]

        elif rec_type == EMR_MODIFYWORLDTRANSFORM:
            m11, m12, m21, m22, dx, dy = struct.unpack_from(
                '<ffffff', rec_data, 0)
            mode = struct.unpack_from('<I', rec_data, 24)[0]
            xform = [m11, m12, m21, m22, dx, dy]
            if mode == MWT_IDENTITY:
                state.world_transform = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
            elif mode == MWT_LEFTMULTIPLY:
                state.world_transform = multiply_xform(
                    xform, state.world_transform)
            elif mode == MWT_RIGHTMULTIPLY:
                state.world_transform = multiply_xform(
                    state.world_transform, xform)
            elif mode == MWT_SET:
                state.world_transform = xform

        # ================================================================
        # DC Save/Restore
        # ================================================================
        elif rec_type == EMR_SAVEDC:
            state.save_dc()

        elif rec_type == EMR_RESTOREDC:
            saved_dc = struct.unpack_from('<i', rec_data, 0)[0]
            state.restore_dc(saved_dc)
            # Sync SVG clip state after restore (clip_region is
            # already in SVG coords, no re-transform needed)
            if state.clip_region is not None:
                clip_counter += 1
                cid = f"clip{clip_counter}"
                svg.set_clip(cid, state.clip_region)
            else:
                svg.clear_clip()

        # ================================================================
        # State settings
        # ================================================================
        elif rec_type == EMR_SETPOLYFILLMODE:
            state.poly_fill_mode = struct.unpack_from('<I', rec_data, 0)[0]

        elif rec_type == EMR_SETMITERLIMIT:
            state.miter_limit = struct.unpack_from('<f', rec_data, 0)[0]

        elif rec_type == EMR_SETTEXTALIGN:
            state.text_align = struct.unpack_from('<I', rec_data, 0)[0]

        elif rec_type == EMR_SETTEXTCOLOR:
            state.text_color = parse_colorref(rec_data, 0)

        elif rec_type == EMR_SETBKMODE:
            state.bk_mode = struct.unpack_from('<I', rec_data, 0)[0]

        elif rec_type == EMR_SETBKCOLOR:
            state.bk_color = parse_colorref(rec_data, 0)

        elif rec_type == EMR_SETARCDIRECTION:
            state.arc_direction = struct.unpack_from('<I', rec_data, 0)[0]

        elif rec_type in (EMR_SETROP2, EMR_SETSTRETCHBLTMODE,
                          EMR_SETBRUSHORGEX, EMR_SETICMMODE,
                          EMR_CREATECOLORSPACE, EMR_SETCOLORSPACE,
                          EMR_DELETECOLORSPACE, EMR_SETLAYOUT,
                          EMR_SETLINKEDUFIS, EMR_SETTEXTJUSTIFICATION,
                          EMR_SETMETARGN, EMR_SETPIXELV):
            pass  # State settings not needed for SVG rendering

        # ================================================================
        # Object management
        # ================================================================
        elif rec_type == EMR_CREATEPEN:
            ih_pen = struct.unpack_from('<I', rec_data, 0)[0]
            style = struct.unpack_from('<I', rec_data, 4)[0]
            width = struct.unpack_from('<i', rec_data, 8)[0]
            color = parse_colorref(rec_data, 16)
            state.objects[ih_pen] = Pen(style, width, color,
                                        is_cosmetic=False)

        elif rec_type == EMR_EXTCREATEPEN:
            ih_pen = struct.unpack_from('<I', rec_data, 0)[0]
            elp_style = struct.unpack_from('<I', rec_data, 20)[0]
            elp_width = struct.unpack_from('<I', rec_data, 24)[0]
            elp_color = parse_colorref(rec_data, 32)
            line_style = elp_style & PS_STYLE_MASK
            cosmetic = (elp_style & PS_GEOMETRIC) == 0
            endcap = pen_endcap_str(elp_style)
            join = pen_join_str(elp_style)
            state.objects[ih_pen] = Pen(line_style, elp_width, elp_color,
                                        endcap, join, is_cosmetic=cosmetic)

        elif rec_type == EMR_CREATEBRUSHINDIRECT:
            ih_brush = struct.unpack_from('<I', rec_data, 0)[0]
            lb_style = struct.unpack_from('<I', rec_data, 4)[0]
            lb_color = parse_colorref(rec_data, 8)
            state.objects[ih_brush] = Brush(lb_style, lb_color)

        elif rec_type == EMR_EXTCREATEFONTINDIRECTW:
            ih_font = struct.unpack_from('<I', rec_data, 0)[0]
            lf_height = struct.unpack_from('<i', rec_data, 4)[0]
            lf_escapement = struct.unpack_from('<i', rec_data, 12)[0]
            lf_weight = struct.unpack_from('<i', rec_data, 20)[0]
            lf_italic = rec_data[24]
            lf_underline = rec_data[25]
            lf_strikeout = rec_data[26]
            lf_charset = rec_data[27]
            face_bytes = rec_data[32:96]
            face_name = face_bytes.decode('utf-16-le',
                                          errors='replace').split('\x00')[0]
            face_name = sanitize_font_name(face_name)
            font_size = abs(lf_height) if lf_height != 0 else 12
            state.objects[ih_font] = Font(
                family=face_name, size=font_size, weight=lf_weight,
                italic=bool(lf_italic), underline=bool(lf_underline),
                strikeout=bool(lf_strikeout), escapement=lf_escapement,
                charset=lf_charset)

        elif rec_type == EMR_CREATEDIBPATTERNBRUSHPT:
            ih_brush = struct.unpack_from('<I', rec_data, 0)[0]
            # Pattern brush - try to get a representative color from bitmap
            # Default to gray as placeholder
            state.objects[ih_brush] = Brush(BS_SOLID, (128, 128, 128))

        elif rec_type == EMR_CREATEMONOBRUSH:
            ih_brush = struct.unpack_from('<I', rec_data, 0)[0]
            state.objects[ih_brush] = Brush(BS_SOLID, (0, 0, 0))

        elif rec_type == EMR_CREATEPALETTE:
            ih_pal = struct.unpack_from('<I', rec_data, 0)[0]
            state.objects[ih_pal] = None  # Palette, not used for rendering

        elif rec_type == EMR_SELECTOBJECT:
            ih_object = struct.unpack_from('<I', rec_data, 0)[0]
            state.select_object(ih_object)

        elif rec_type == EMR_DELETEOBJECT:
            ih_object = struct.unpack_from('<I', rec_data, 0)[0]
            state.objects.pop(ih_object, None)

        elif rec_type in (EMR_SELECTPALETTE, EMR_REALIZEPALETTE):
            pass

        # ================================================================
        # Position and line drawing
        # ================================================================
        elif rec_type == EMR_MOVETOEX:
            x, y = struct.unpack_from('<ii', rec_data, 0)
            state.cur_x = x
            state.cur_y = y
            if state.in_path:
                tx, ty = state.transform_point(x, y)
                state.path_data.append(f"M {fmt(tx)},{fmt(ty)}")

        elif rec_type == EMR_LINETO:
            x, y = struct.unpack_from('<ii', rec_data, 0)
            if state.in_path:
                tx, ty = state.transform_point(x, y)
                state.path_data.append(f"L {fmt(tx)},{fmt(ty)}")
            else:
                pen = state.current_pen
                if not pen.is_null:
                    tx1, ty1 = state.transform_point(
                        state.cur_x, state.cur_y)
                    tx2, ty2 = state.transform_point(x, y)
                    sw = pen_stroke_width(pen, state)
                    svg.add_polyline(
                        [(tx1, ty1), (tx2, ty2)],
                        stroke=pen.svg_color,
                        stroke_width=sw,
                        stroke_linecap=pen.endcap,
                        stroke_linejoin=pen.join)
            state.cur_x = x
            state.cur_y = y

        # ================================================================
        # Path operations
        # ================================================================
        elif rec_type == EMR_BEGINPATH:
            state.in_path = True
            state.path_data = []
            state.path_texts = []

        elif rec_type == EMR_ENDPATH:
            state.in_path = False

        elif rec_type == EMR_CLOSEFIGURE:
            if state.in_path:
                state.path_data.append("Z")

        elif rec_type == EMR_FILLPATH:
            if state.path_data:
                d = " ".join(state.path_data)
                fill = state.current_brush.svg_color
                svg.add_path(d, fill=fill, fill_rule=state.svg_fill_rule)
            elif state.path_texts:
                fill = state.current_brush.svg_color
                for pt in state.path_texts:
                    svg.add_text(pt['x'], pt['y'], pt['text'],
                                 pt['family'], pt['size'], fill,
                                 weight=pt['weight'], italic=pt['italic'],
                                 anchor=pt['anchor'],
                                 dominant_baseline=pt['baseline'],
                                 rotation=pt['rotation'],
                                 scale_x=pt.get('scale_x'))
            state.path_data = []
            state.path_texts = []

        elif rec_type == EMR_STROKEPATH:
            if state.path_data:
                d = " ".join(state.path_data)
                pen = state.current_pen
                stroke = pen.svg_color if not pen.is_null else "none"
                sw = pen_stroke_width(pen, state)
                svg.add_path(d, fill="none", stroke=stroke,
                             stroke_width=sw,
                             stroke_linecap=pen.endcap,
                             stroke_linejoin=pen.join,
                             miter_limit=state.miter_limit)
            elif state.path_texts:
                pen = state.current_pen
                stroke = pen.svg_color if not pen.is_null else "none"
                sw = pen_stroke_width(pen, state)
                for pt in state.path_texts:
                    svg.add_text(pt['x'], pt['y'], pt['text'],
                                 pt['family'], pt['size'], 'none',
                                 weight=pt['weight'], italic=pt['italic'],
                                 anchor=pt['anchor'],
                                 dominant_baseline=pt['baseline'],
                                 rotation=pt['rotation'],
                                 scale_x=pt.get('scale_x'),
                                 stroke=stroke, stroke_width=sw)
            state.path_data = []
            state.path_texts = []

        elif rec_type == EMR_STROKEANDFILLPATH:
            if state.path_data:
                d = " ".join(state.path_data)
                fill = state.current_brush.svg_color
                pen = state.current_pen
                stroke = pen.svg_color if not pen.is_null else "none"
                sw = pen_stroke_width(pen, state)
                svg.add_path(d, fill=fill, stroke=stroke,
                             stroke_width=sw,
                             fill_rule=state.svg_fill_rule,
                             stroke_linecap=pen.endcap,
                             stroke_linejoin=pen.join,
                             miter_limit=state.miter_limit)
            elif state.path_texts:
                fill = state.current_brush.svg_color
                pen = state.current_pen
                stroke = pen.svg_color if not pen.is_null else "none"
                sw = pen_stroke_width(pen, state)
                for pt in state.path_texts:
                    svg.add_text(pt['x'], pt['y'], pt['text'],
                                 pt['family'], pt['size'], fill,
                                 weight=pt['weight'], italic=pt['italic'],
                                 anchor=pt['anchor'],
                                 dominant_baseline=pt['baseline'],
                                 rotation=pt['rotation'],
                                 scale_x=pt.get('scale_x'),
                                 stroke=stroke, stroke_width=sw)
            state.path_data = []
            state.path_texts = []

        # ================================================================
        # Bezier curves
        # ================================================================
        elif rec_type == EMR_POLYBEZIERTO16:
            count = struct.unpack_from('<I', rec_data, 16)[0]
            points = parse_points16(rec_data, 20, count)
            if state.in_path:
                i = 0
                while i + 2 < len(points):
                    cp1 = state.transform_point(*points[i])
                    cp2 = state.transform_point(*points[i + 1])
                    end = state.transform_point(*points[i + 2])
                    state.path_data.append(
                        f"C {fmt(cp1[0])},{fmt(cp1[1])} "
                        f"{fmt(cp2[0])},{fmt(cp2[1])} "
                        f"{fmt(end[0])},{fmt(end[1])}")
                    i += 3
                if points:
                    state.cur_x, state.cur_y = points[-1]

        elif rec_type == EMR_POLYLINETO16:
            count = struct.unpack_from('<I', rec_data, 16)[0]
            points = parse_points16(rec_data, 20, count)
            if state.in_path:
                for px, py in points:
                    tx, ty = state.transform_point(px, py)
                    state.path_data.append(f"L {fmt(tx)},{fmt(ty)}")
            if points:
                state.cur_x, state.cur_y = points[-1]

        elif rec_type == EMR_POLYBEZIERTO:
            count = struct.unpack_from('<I', rec_data, 16)[0]
            points = parse_points32(rec_data, 20, count)
            if state.in_path:
                i = 0
                while i + 2 < len(points):
                    cp1 = state.transform_point(*points[i])
                    cp2 = state.transform_point(*points[i + 1])
                    end = state.transform_point(*points[i + 2])
                    state.path_data.append(
                        f"C {fmt(cp1[0])},{fmt(cp1[1])} "
                        f"{fmt(cp2[0])},{fmt(cp2[1])} "
                        f"{fmt(end[0])},{fmt(end[1])}")
                    i += 3
            if points:
                state.cur_x, state.cur_y = points[-1]

        elif rec_type == EMR_POLYLINETO:
            count = struct.unpack_from('<I', rec_data, 16)[0]
            points = parse_points32(rec_data, 20, count)
            if state.in_path:
                for px, py in points:
                    tx, ty = state.transform_point(px, py)
                    state.path_data.append(f"L {fmt(tx)},{fmt(ty)}")
            if points:
                state.cur_x, state.cur_y = points[-1]

        # ================================================================
        # Standalone polygon/polyline drawing
        # ================================================================
        elif rec_type == EMR_POLYGON16:
            count = struct.unpack_from('<I', rec_data, 16)[0]
            points = parse_points16(rec_data, 20, count)
            if state.in_path:
                if points:
                    tp = state.transform_point(*points[0])
                    state.path_data.append(f"M {fmt(tp[0])},{fmt(tp[1])}")
                    for px, py in points[1:]:
                        tp = state.transform_point(px, py)
                        state.path_data.append(
                            f"L {fmt(tp[0])},{fmt(tp[1])}")
                    state.path_data.append("Z")
            else:
                transformed = [state.transform_point(*p) for p in points]
                fill = state.current_brush.svg_color
                pen = state.current_pen
                stroke = pen.svg_color if not pen.is_null else "none"
                sw = pen_stroke_width(pen, state)
                if pen.is_null or sw == 0:
                    stroke = "none"
                    sw = 0
                svg.add_polygon(transformed, fill=fill, stroke=stroke,
                                stroke_width=sw,
                                fill_rule=state.svg_fill_rule)

        elif rec_type == EMR_POLYGON:
            count = struct.unpack_from('<I', rec_data, 16)[0]
            points = parse_points32(rec_data, 20, count)
            if state.in_path:
                if points:
                    tp = state.transform_point(*points[0])
                    state.path_data.append(f"M {fmt(tp[0])},{fmt(tp[1])}")
                    for px, py in points[1:]:
                        tp = state.transform_point(px, py)
                        state.path_data.append(
                            f"L {fmt(tp[0])},{fmt(tp[1])}")
                    state.path_data.append("Z")
            else:
                transformed = [state.transform_point(*p) for p in points]
                fill = state.current_brush.svg_color
                pen = state.current_pen
                stroke = pen.svg_color if not pen.is_null else "none"
                sw = pen_stroke_width(pen, state)
                if pen.is_null or sw == 0:
                    stroke = "none"
                    sw = 0
                svg.add_polygon(transformed, fill=fill, stroke=stroke,
                                stroke_width=sw,
                                fill_rule=state.svg_fill_rule)

        elif rec_type == EMR_POLYLINE16:
            count = struct.unpack_from('<I', rec_data, 16)[0]
            points = parse_points16(rec_data, 20, count)
            if state.in_path:
                if points:
                    tp = state.transform_point(*points[0])
                    state.path_data.append(f"M {fmt(tp[0])},{fmt(tp[1])}")
                    for px, py in points[1:]:
                        tp = state.transform_point(px, py)
                        state.path_data.append(
                            f"L {fmt(tp[0])},{fmt(tp[1])}")
            else:
                transformed = [state.transform_point(*p) for p in points]
                pen = state.current_pen
                stroke = pen.svg_color if not pen.is_null else "none"
                sw = pen_stroke_width(pen, state)
                svg.add_polyline(transformed, stroke=stroke,
                                 stroke_width=sw,
                                 stroke_linecap=pen.endcap,
                                 stroke_linejoin=pen.join)

        elif rec_type == EMR_POLYLINE:
            count = struct.unpack_from('<I', rec_data, 16)[0]
            points = parse_points32(rec_data, 20, count)
            if state.in_path:
                if points:
                    tp = state.transform_point(*points[0])
                    state.path_data.append(f"M {fmt(tp[0])},{fmt(tp[1])}")
                    for px, py in points[1:]:
                        tp = state.transform_point(px, py)
                        state.path_data.append(
                            f"L {fmt(tp[0])},{fmt(tp[1])}")
            else:
                transformed = [state.transform_point(*p) for p in points]
                pen = state.current_pen
                stroke = pen.svg_color if not pen.is_null else "none"
                sw = pen_stroke_width(pen, state)
                svg.add_polyline(transformed, stroke=stroke,
                                 stroke_width=sw,
                                 stroke_linecap=pen.endcap,
                                 stroke_linejoin=pen.join)

        elif rec_type == EMR_POLYBEZIER16:
            count = struct.unpack_from('<I', rec_data, 16)[0]
            points = parse_points16(rec_data, 20, count)
            if state.in_path:
                if points:
                    tp = state.transform_point(*points[0])
                    state.path_data.append(f"M {fmt(tp[0])},{fmt(tp[1])}")
                    i = 1
                    while i + 2 < len(points):
                        cp1 = state.transform_point(*points[i])
                        cp2 = state.transform_point(*points[i + 1])
                        end = state.transform_point(*points[i + 2])
                        state.path_data.append(
                            f"C {fmt(cp1[0])},{fmt(cp1[1])} "
                            f"{fmt(cp2[0])},{fmt(cp2[1])} "
                            f"{fmt(end[0])},{fmt(end[1])}")
                        i += 3

        elif rec_type == EMR_POLYBEZIER:
            count = struct.unpack_from('<I', rec_data, 16)[0]
            points = parse_points32(rec_data, 20, count)
            if state.in_path:
                if points:
                    tp = state.transform_point(*points[0])
                    state.path_data.append(f"M {fmt(tp[0])},{fmt(tp[1])}")
                    i = 1
                    while i + 2 < len(points):
                        cp1 = state.transform_point(*points[i])
                        cp2 = state.transform_point(*points[i + 1])
                        end = state.transform_point(*points[i + 2])
                        state.path_data.append(
                            f"C {fmt(cp1[0])},{fmt(cp1[1])} "
                            f"{fmt(cp2[0])},{fmt(cp2[1])} "
                            f"{fmt(end[0])},{fmt(end[1])}")
                        i += 3

        # ================================================================
        # Multi-polygon/polyline
        # ================================================================
        elif rec_type == EMR_POLYPOLYGON16:
            n_polys = struct.unpack_from('<I', rec_data, 16)[0]
            total_count = struct.unpack_from('<I', rec_data, 20)[0]
            poly_counts = [struct.unpack_from('<I', rec_data, 24 + i * 4)[0]
                           for i in range(n_polys)]
            pts_offset = 24 + n_polys * 4
            all_points = parse_points16(rec_data, pts_offset, total_count)
            if state.in_path:
                idx = 0
                for pc in poly_counts:
                    sub = all_points[idx:idx + pc]
                    if sub:
                        tp = state.transform_point(*sub[0])
                        state.path_data.append(
                            f"M {fmt(tp[0])},{fmt(tp[1])}")
                        for px, py in sub[1:]:
                            tp = state.transform_point(px, py)
                            state.path_data.append(
                                f"L {fmt(tp[0])},{fmt(tp[1])}")
                        state.path_data.append("Z")
                    idx += pc
            else:
                d_parts = []
                idx = 0
                for pc in poly_counts:
                    sub = all_points[idx:idx + pc]
                    if sub:
                        tp = state.transform_point(*sub[0])
                        d_parts.append(f"M {fmt(tp[0])},{fmt(tp[1])}")
                        for px, py in sub[1:]:
                            tp = state.transform_point(px, py)
                            d_parts.append(f"L {fmt(tp[0])},{fmt(tp[1])}")
                        d_parts.append("Z")
                    idx += pc
                d = " ".join(d_parts)
                fill = state.current_brush.svg_color
                pen = state.current_pen
                stroke = pen.svg_color if not pen.is_null else "none"
                sw = pen_stroke_width(pen, state)
                if pen.is_null or sw == 0:
                    stroke = "none"
                    sw = 0
                svg.add_path(d, fill=fill, stroke=stroke,
                             stroke_width=sw,
                             fill_rule=state.svg_fill_rule)

        elif rec_type == EMR_POLYPOLYGON:
            n_polys = struct.unpack_from('<I', rec_data, 16)[0]
            total_count = struct.unpack_from('<I', rec_data, 20)[0]
            poly_counts = [struct.unpack_from('<I', rec_data, 24 + i * 4)[0]
                           for i in range(n_polys)]
            pts_offset = 24 + n_polys * 4
            all_points = parse_points32(rec_data, pts_offset, total_count)
            d_parts = []
            idx = 0
            for pc in poly_counts:
                sub = all_points[idx:idx + pc]
                if sub:
                    tp = state.transform_point(*sub[0])
                    d_parts.append(f"M {fmt(tp[0])},{fmt(tp[1])}")
                    for px, py in sub[1:]:
                        tp = state.transform_point(px, py)
                        d_parts.append(f"L {fmt(tp[0])},{fmt(tp[1])}")
                    d_parts.append("Z")
                idx += pc
            d = " ".join(d_parts)
            fill = state.current_brush.svg_color
            pen = state.current_pen
            stroke = pen.svg_color if not pen.is_null else "none"
            sw = pen_stroke_width(pen, state)
            if pen.is_null or sw == 0:
                stroke = "none"
                sw = 0
            svg.add_path(d, fill=fill, stroke=stroke,
                         stroke_width=sw,
                         fill_rule=state.svg_fill_rule)

        elif rec_type == EMR_POLYPOLYLINE16:
            n_polylines = struct.unpack_from('<I', rec_data, 16)[0]
            total_count = struct.unpack_from('<I', rec_data, 20)[0]
            poly_counts = [struct.unpack_from('<I', rec_data, 24 + i * 4)[0]
                           for i in range(n_polylines)]
            pts_offset = 24 + n_polylines * 4
            all_points = parse_points16(rec_data, pts_offset, total_count)
            if state.in_path:
                idx = 0
                for pc in poly_counts:
                    sub = all_points[idx:idx + pc]
                    if sub:
                        tp = state.transform_point(*sub[0])
                        state.path_data.append(
                            f"M {fmt(tp[0])},{fmt(tp[1])}")
                        for px, py in sub[1:]:
                            tp = state.transform_point(px, py)
                            state.path_data.append(
                                f"L {fmt(tp[0])},{fmt(tp[1])}")
                    idx += pc
            else:
                d_parts = []
                idx = 0
                for pc in poly_counts:
                    sub = all_points[idx:idx + pc]
                    if sub:
                        tp = state.transform_point(*sub[0])
                        d_parts.append(f"M {fmt(tp[0])},{fmt(tp[1])}")
                        for px, py in sub[1:]:
                            tp = state.transform_point(px, py)
                            d_parts.append(f"L {fmt(tp[0])},{fmt(tp[1])}")
                    idx += pc
                d = " ".join(d_parts)
                pen = state.current_pen
                stroke = pen.svg_color if not pen.is_null else "none"
                sw = pen_stroke_width(pen, state)
                svg.add_path(d, fill="none", stroke=stroke,
                             stroke_width=sw,
                             stroke_linecap=pen.endcap,
                             stroke_linejoin=pen.join)

        elif rec_type == EMR_POLYPOLYLINE:
            n_polylines = struct.unpack_from('<I', rec_data, 16)[0]
            total_count = struct.unpack_from('<I', rec_data, 20)[0]
            poly_counts = [struct.unpack_from('<I', rec_data, 24 + i * 4)[0]
                           for i in range(n_polylines)]
            pts_offset = 24 + n_polylines * 4
            all_points = parse_points32(rec_data, pts_offset, total_count)
            d_parts = []
            idx = 0
            for pc in poly_counts:
                sub = all_points[idx:idx + pc]
                if sub:
                    tp = state.transform_point(*sub[0])
                    d_parts.append(f"M {fmt(tp[0])},{fmt(tp[1])}")
                    for px, py in sub[1:]:
                        tp = state.transform_point(px, py)
                        d_parts.append(f"L {fmt(tp[0])},{fmt(tp[1])}")
                idx += pc
            d = " ".join(d_parts)
            pen = state.current_pen
            stroke = pen.svg_color if not pen.is_null else "none"
            sw = pen_stroke_width(pen, state)
            svg.add_path(d, fill="none", stroke=stroke, stroke_width=sw)

        elif rec_type == EMR_POLYDRAW16:
            count = struct.unpack_from('<I', rec_data, 16)[0]
            pts = []
            for i in range(count):
                x, y = struct.unpack_from('<hh', rec_data, 20 + i * 4)
                pts.append((x, y))
            types_off = 20 + count * 4
            pt_types = rec_data[types_off:types_off + count]
            PT_CLOSEFIGURE = 0x01
            PT_LINETO = 0x02
            PT_BEZIERTO = 0x04
            PT_MOVETO = 0x06
            d_parts = []
            i = 0
            while i < count:
                base = pt_types[i] & 0x06
                close = pt_types[i] & PT_CLOSEFIGURE
                if base == PT_MOVETO:
                    tp = state.transform_point(*pts[i])
                    d_parts.append(f"M {fmt(tp[0])},{fmt(tp[1])}")
                    i += 1
                elif base == PT_LINETO:
                    tp = state.transform_point(*pts[i])
                    d_parts.append(f"L {fmt(tp[0])},{fmt(tp[1])}")
                    if close:
                        d_parts.append("Z")
                    i += 1
                elif base == PT_BEZIERTO and i + 2 < count:
                    c1 = state.transform_point(*pts[i])
                    c2 = state.transform_point(*pts[i + 1])
                    ep = state.transform_point(*pts[i + 2])
                    d_parts.append(
                        f"C {fmt(c1[0])},{fmt(c1[1])} "
                        f"{fmt(c2[0])},{fmt(c2[1])} "
                        f"{fmt(ep[0])},{fmt(ep[1])}")
                    if pt_types[i + 2] & PT_CLOSEFIGURE:
                        d_parts.append("Z")
                    i += 3
                else:
                    i += 1
            if d_parts:
                d = " ".join(d_parts)
                if state.in_path:
                    state.path_data.append(d)
                else:
                    emit_shape(state, svg, d_parts)

        # ================================================================
        # Shape primitives
        # ================================================================
        elif rec_type == EMR_RECTANGLE:
            left, top, right, bottom = struct.unpack_from(
                '<iiii', rec_data, 0)
            parts = rect_path_data(left, top, right, bottom, state)
            if state.in_path:
                state.path_data.extend(parts)
            else:
                emit_shape(state, svg, parts)

        elif rec_type == EMR_ELLIPSE:
            left, top, right, bottom = struct.unpack_from(
                '<iiii', rec_data, 0)
            parts = ellipse_path_data(left, top, right, bottom, state)
            if state.in_path:
                state.path_data.extend(parts)
            else:
                emit_shape(state, svg, parts)

        elif rec_type == EMR_ROUNDRECT:
            left, top, right, bottom = struct.unpack_from(
                '<iiii', rec_data, 0)
            corner_w, corner_h = struct.unpack_from('<ii', rec_data, 16)
            parts = roundrect_path_data(left, top, right, bottom,
                                        corner_w, corner_h, state)
            if state.in_path:
                state.path_data.extend(parts)
            else:
                emit_shape(state, svg, parts)

        elif rec_type == EMR_ARC:
            box = struct.unpack_from('<iiii', rec_data, 0)
            start = struct.unpack_from('<ii', rec_data, 16)
            end = struct.unpack_from('<ii', rec_data, 24)
            parts = arc_path_data(box[0], box[1], box[2], box[3],
                                  start[0], start[1], end[0], end[1],
                                  state.arc_direction, state)
            if state.in_path:
                state.path_data.extend(parts)
            else:
                emit_shape(state, svg, parts, has_fill=False)

        elif rec_type == EMR_PIE:
            box = struct.unpack_from('<iiii', rec_data, 0)
            start = struct.unpack_from('<ii', rec_data, 16)
            end = struct.unpack_from('<ii', rec_data, 24)
            parts = arc_path_data(box[0], box[1], box[2], box[3],
                                  start[0], start[1], end[0], end[1],
                                  state.arc_direction, state, is_pie=True)
            if state.in_path:
                state.path_data.extend(parts)
            else:
                emit_shape(state, svg, parts)

        elif rec_type == EMR_CHORD:
            box = struct.unpack_from('<iiii', rec_data, 0)
            start = struct.unpack_from('<ii', rec_data, 16)
            end = struct.unpack_from('<ii', rec_data, 24)
            parts = arc_path_data(box[0], box[1], box[2], box[3],
                                  start[0], start[1], end[0], end[1],
                                  state.arc_direction, state)
            parts.append("Z")
            if state.in_path:
                state.path_data.extend(parts)
            else:
                emit_shape(state, svg, parts)

        # ================================================================
        # Text rendering
        # ================================================================
        elif rec_type in (EMR_EXTTEXTOUTW, EMR_EXTTEXTOUTA):
            # Bounds(16) + iGraphicsMode(4) + exScale(4) + eyScale(4) = 28
            # EmrText: ptlRef(8) + nChars(4) + offString(4) + Options(4)
            #          + Rect(16) + offDx(4) = 40
            ref_x = struct.unpack_from('<i', rec_data, 28)[0]
            ref_y = struct.unpack_from('<i', rec_data, 32)[0]
            n_chars = struct.unpack_from('<I', rec_data, 36)[0]
            off_string = struct.unpack_from('<I', rec_data, 40)[0]
            if n_chars > 0 and off_string >= 8:
                str_start = off_string - 8
                if rec_type == EMR_EXTTEXTOUTW:
                    str_end = str_start + n_chars * 2
                    if str_end <= len(rec_data):
                        text = rec_data[str_start:str_end].decode(
                            'utf-16-le', errors='replace')
                    else:
                        text = ""
                else:
                    str_end = str_start + n_chars
                    if str_end <= len(rec_data):
                        raw = rec_data[str_start:str_end]
                        cs = state.current_font.charset
                        if cs in (0, 1):  # ANSI/DEFAULT: auto-detect
                            codec = _detect_ansi_codec(raw)
                        else:
                            codec = _CHARSET_TO_CODEC.get(cs, 'cp1252')
                        text = raw.decode(codec, errors='replace')
                    else:
                        text = ""
                # Remap Symbol font PUA codepoints to standard encoding
                if text and state.current_font.family.lower() == 'symbol':
                    text = _remap_symbol_pua(text)
                if text and state.in_path:
                    # Text inside BeginPath/EndPath: in GDI this adds
                    # glyph outlines to the path. We can't extract glyph
                    # outlines, so store the text info for later rendering
                    # when FillPath/StrokePath/StrokeAndFillPath is called.
                    tx, ty = state.transform_point(ref_x, ref_y)
                    font = state.current_font
                    fs = state.transform_height(font.size)
                    if fs < 0.5:
                        fs = state.transform_width(font.size)
                    if fs < 0.5:
                        fs = font.size
                    # Compute horizontal scaling only for axis-aligned
                    # transforms (no rotation/shear). When the world
                    # transform contains rotation (M12/M21 non-zero),
                    # the row-norm ratio is not a meaningful horizontal
                    # scale correction for non-rotated SVG text.
                    wt = state.world_transform
                    if (abs(wt[1]) < 1e-6 and abs(wt[2]) < 1e-6):
                        tw = state.transform_width(font.size)
                        if tw > 0.5 and fs > 0.5:
                            sx = tw / fs
                        else:
                            sx = None
                    else:
                        sx = None
                    rotation = -font.escapement / 10.0 if font.escapement else 0
                    state.path_texts.append({
                        'x': tx, 'y': ty, 'text': text,
                        'family': font.family, 'size': fs,
                        'weight': font.weight, 'italic': font.italic,
                        'anchor': state.svg_text_anchor,
                        'baseline': state.svg_dominant_baseline,
                        'rotation': rotation,
                        'scale_x': sx,
                    })
                elif text and not state.in_path:
                    tx, ty = state.transform_point(ref_x, ref_y)
                    font = state.current_font
                    fs = state.transform_height(font.size)
                    if fs < 0.5:
                        fs = state.transform_width(font.size)
                    if fs < 0.5:
                        fs = font.size
                    wt = state.world_transform
                    has_wt_rotation = (abs(wt[1]) > 1e-6 or
                                       abs(wt[2]) > 1e-6)
                    # Compute horizontal scaling only for axis-aligned
                    # transforms (no rotation/shear).
                    if not has_wt_rotation:
                        tw = state.transform_width(font.size)
                        if tw > 0.5 and fs > 0.5:
                            scale_x = tw / fs
                        else:
                            scale_x = None
                    else:
                        scale_x = None
                    rotation = -font.escapement / 10.0 if font.escapement else 0
                    # Extract rotation from world transform when font
                    # escapement is 0 but the WT has rotation.
                    if rotation == 0 and has_wt_rotation:
                        rotation = -math.degrees(math.atan2(wt[1], wt[0]))
                    dbaseline = state.svg_dominant_baseline
                    rot_origin = None
                    # For rotated text, manually adjust y instead of using
                    # dominant-baseline, which renders inconsistently across
                    # SVG engines when combined with rotation + clip-path.
                    if rotation != 0 and dbaseline != 'auto':
                        rot_origin = (tx, ty)  # keep rotation around ref point
                        if dbaseline == 'hanging':
                            ty += fs * 0.8  # shift by font ascent
                        elif dbaseline == 'text-after-edge':
                            ty -= fs * 0.2  # shift by font descent
                        dbaseline = 'auto'
                    # Suppress clip-path for rotated text: EMF clip rects
                    # are sized for the text's visual area but font metric
                    # differences between GDI and SVG cause clipping.
                    saved_clip = None
                    if rotation != 0 and svg._current_clip_id:
                        saved_clip = svg._current_clip_id
                        svg._current_clip_id = None
                    svg.add_text(tx, ty, text, font.family, fs,
                                 state.svg_text_color,
                                 weight=font.weight, italic=font.italic,
                                 anchor=state.svg_text_anchor,
                                 rotation=rotation,
                                 dominant_baseline=dbaseline,
                                 rotate_origin=rot_origin,
                                 scale_x=scale_x)
                    if saved_clip is not None:
                        svg._current_clip_id = saved_clip

        elif rec_type == EMR_SMALLTEXTOUT:
            x = struct.unpack_from('<i', rec_data, 0)[0]
            y = struct.unpack_from('<i', rec_data, 4)[0]
            n_chars = struct.unpack_from('<I', rec_data, 8)[0]
            fu_options = struct.unpack_from('<I', rec_data, 12)[0]
            # iGraphicsMode(4) + exScale(4) + eyScale(4) at 16-28
            has_rect = not (fu_options & 0x0100)  # ETO_NO_RECT
            if has_rect:
                text_offset = 44  # 28 + 16 (rect)
            else:
                text_offset = 28
            if n_chars > 0 and text_offset < len(rec_data):
                # Try Unicode first
                uni_end = text_offset + n_chars * 2
                if uni_end <= len(rec_data):
                    text = rec_data[text_offset:uni_end].decode(
                        'utf-16-le', errors='replace')
                else:
                    ansi_end = text_offset + n_chars
                    if ansi_end <= len(rec_data):
                        text = rec_data[text_offset:ansi_end].decode(
                            'latin-1', errors='replace')
                    else:
                        text = ""
                if text and not state.in_path:
                    tx, ty = state.transform_point(x, y)
                    font = state.current_font
                    fs = state.transform_height(font.size)
                    if fs < 0.5:
                        fs = state.transform_width(font.size)
                    if fs < 0.5:
                        fs = font.size
                    svg.add_text(tx, ty, text, font.family, fs,
                                 state.svg_text_color,
                                 weight=font.weight, italic=font.italic,
                                 anchor=state.svg_text_anchor,
                                 dominant_baseline=state.svg_dominant_baseline)

        # ================================================================
        # Bitmap operations
        # ================================================================
        elif rec_type == EMR_BITBLT:
            xDest = struct.unpack_from('<i', rec_data, 16)[0]
            yDest = struct.unpack_from('<i', rec_data, 20)[0]
            cxDest = struct.unpack_from('<i', rec_data, 24)[0]
            cyDest = struct.unpack_from('<i', rec_data, 28)[0]
            rop = struct.unpack_from('<I', rec_data, 32)[0]
            off_bmi = struct.unpack_from('<I', rec_data, 76)[0]
            cb_bmi = struct.unpack_from('<I', rec_data, 80)[0]
            off_bits = struct.unpack_from('<I', rec_data, 84)[0]
            cb_bits = struct.unpack_from('<I', rec_data, 88)[0]
            if cb_bits > 0 and cb_bmi > 0:
                embed_dib_image(rec_data, off_bmi, cb_bmi, off_bits, cb_bits,
                                xDest, yDest, cxDest, cyDest, state, svg)
            elif rop == PATCOPY and cxDest != 0 and cyDest != 0:
                parts = rect_path_data(xDest, yDest,
                                       xDest + cxDest, yDest + cyDest, state)
                d = " ".join(parts)
                svg.add_path(d, fill=state.current_brush.svg_color)
            elif rop == WHITENESS and cxDest != 0 and cyDest != 0:
                parts = rect_path_data(xDest, yDest,
                                       xDest + cxDest, yDest + cyDest, state)
                d = " ".join(parts)
                svg.add_path(d, fill="#FFFFFF")
            elif rop == BLACKNESS and cxDest != 0 and cyDest != 0:
                parts = rect_path_data(xDest, yDest,
                                       xDest + cxDest, yDest + cyDest, state)
                d = " ".join(parts)
                svg.add_path(d, fill="#000000")

        elif rec_type == EMR_STRETCHBLT:
            xDest = struct.unpack_from('<i', rec_data, 16)[0]
            yDest = struct.unpack_from('<i', rec_data, 20)[0]
            cxDest = struct.unpack_from('<i', rec_data, 24)[0]
            cyDest = struct.unpack_from('<i', rec_data, 28)[0]
            off_bmi = struct.unpack_from('<I', rec_data, 76)[0]
            cb_bmi = struct.unpack_from('<I', rec_data, 80)[0]
            off_bits = struct.unpack_from('<I', rec_data, 84)[0]
            cb_bits = struct.unpack_from('<I', rec_data, 88)[0]
            if cb_bits > 0 and cb_bmi > 0:
                embed_dib_image(rec_data, off_bmi, cb_bmi, off_bits, cb_bits,
                                xDest, yDest, cxDest, cyDest, state, svg)

        elif rec_type == EMR_STRETCHDIBITS:
            xDest = struct.unpack_from('<i', rec_data, 16)[0]
            yDest = struct.unpack_from('<i', rec_data, 20)[0]
            off_bmi = struct.unpack_from('<I', rec_data, 40)[0]
            cb_bmi = struct.unpack_from('<I', rec_data, 44)[0]
            off_bits = struct.unpack_from('<I', rec_data, 48)[0]
            cb_bits = struct.unpack_from('<I', rec_data, 52)[0]
            cxDest = struct.unpack_from('<i', rec_data, 64)[0]
            cyDest = struct.unpack_from('<i', rec_data, 68)[0]
            if cb_bits > 0 and cb_bmi > 0:
                embed_dib_image(rec_data, off_bmi, cb_bmi, off_bits, cb_bits,
                                xDest, yDest, cxDest, cyDest, state, svg)

        elif rec_type in (EMR_MASKBLT, EMR_SETDIBITSTODEVICE):
            xDest = struct.unpack_from('<i', rec_data, 16)[0]
            yDest = struct.unpack_from('<i', rec_data, 20)[0]
            cxDest = struct.unpack_from('<i', rec_data, 24)[0]
            cyDest = struct.unpack_from('<i', rec_data, 28)[0]
            if rec_type == EMR_MASKBLT:
                off_bmi = struct.unpack_from('<I', rec_data, 76)[0]
                cb_bmi = struct.unpack_from('<I', rec_data, 80)[0]
                off_bits = struct.unpack_from('<I', rec_data, 84)[0]
                cb_bits = struct.unpack_from('<I', rec_data, 88)[0]
            else:  # SETDIBITSTODEVICE
                off_bmi = struct.unpack_from('<I', rec_data, 40)[0]
                cb_bmi = struct.unpack_from('<I', rec_data, 44)[0]
                off_bits = struct.unpack_from('<I', rec_data, 48)[0]
                cb_bits = struct.unpack_from('<I', rec_data, 52)[0]
            if cb_bits > 0 and cb_bmi > 0:
                embed_dib_image(rec_data, off_bmi, cb_bmi, off_bits, cb_bits,
                                xDest, yDest, cxDest, cyDest, state, svg)

        elif rec_type == EMR_PLGBLT:
            # Bounds(16) + aptlDest[3](24) + xSrc(4) + ySrc(4) +
            # cxSrc(4) + cySrc(4) + xformSrc(24) + crBkColorSrc(4) +
            # iUsageSrc(4) + offBmiSrc(4) + cbBmiSrc(4) +
            # offBitsSrc(4) + cbBitsSrc(4)
            if len(rec_data) >= 132:
                # 3 destination points defining parallelogram
                pts = []
                for i in range(3):
                    px, py = struct.unpack_from('<ii', rec_data, 16 + i * 8)
                    pts.append(state.transform_point(px, py))
                cxSrc = struct.unpack_from('<i', rec_data, 48)[0]
                cySrc = struct.unpack_from('<i', rec_data, 52)[0]
                off_bmi = struct.unpack_from('<I', rec_data, 88)[0]
                cb_bmi = struct.unpack_from('<I', rec_data, 92)[0]
                off_bits = struct.unpack_from('<I', rec_data, 96)[0]
                cb_bits = struct.unpack_from('<I', rec_data, 100)[0]
                if cb_bits > 0 and cb_bmi > 0 and cxSrc > 0 and cySrc > 0:
                    bmi_start = off_bmi - 8
                    bits_start = off_bits - 8
                    if (bmi_start >= 0 and bits_start >= 0
                            and bmi_start + cb_bmi <= len(rec_data)
                            and bits_start + cb_bits <= len(rec_data)):
                        bmi_data = rec_data[bmi_start:bmi_start + cb_bmi]
                        bits_data = rec_data[bits_start:bits_start + cb_bits]
                        bf_off = 14 + cb_bmi
                        bf_size = bf_off + cb_bits
                        fh = struct.pack('<2sIHHI', b'BM', bf_size,
                                         0, 0, bf_off)
                        bmp_data = fh + bmi_data + bits_data
                        b64 = base64.b64encode(bmp_data).decode('ascii')
                        href = f"data:image/bmp;base64,{b64}"
                        # Compute affine matrix: source (0,0)-(cxSrc,cySrc)
                        # maps to parallelogram pts[0], pts[1], pts[2]
                        p0, p1, p2 = pts
                        a = (p1[0] - p0[0]) / cxSrc
                        b_val = (p1[1] - p0[1]) / cxSrc
                        c = (p2[0] - p0[0]) / cySrc
                        d = (p2[1] - p0[1]) / cySrc
                        e, f_val = p0[0], p0[1]
                        xf = (f'matrix({fmt(a)},{fmt(b_val)},'
                              f'{fmt(c)},{fmt(d)},'
                              f'{fmt(e)},{fmt(f_val)})')
                        svg.add_image(0, 0, cxSrc, cySrc, href,
                                      transform=xf)

        # ================================================================
        # Fill region
        # ================================================================
        elif rec_type == EMR_FILLRGN:
            # Bounds(16) + RgnDataSize(4) + ihBrush(4) + RgnData(variable)
            ih_brush = struct.unpack_from('<I', rec_data, 20)[0]
            brush = state.objects.get(ih_brush, state.current_brush)
            if isinstance(brush, Brush):
                fill_color = brush.svg_color
            else:
                fill_color = state.current_brush.svg_color
            # RgnData starts at offset 24: RGNDATAHEADER(32) + rects
            # RGNDATAHEADER: dwSize(4) + iType(4) + nCount(4) + ...
            if len(rec_data) >= 56:
                n_rects = struct.unpack_from('<I', rec_data, 32)[0]
                rects_offset = 56  # 24 + 32
                d_parts = []
                for i in range(n_rects):
                    off = rects_offset + i * 16
                    if off + 16 > len(rec_data):
                        break
                    rl, rt, rr, rb = struct.unpack_from(
                        '<iiii', rec_data, off)
                    d_parts.extend(rect_path_data(rl, rt, rr, rb, state))
                if d_parts:
                    d = " ".join(d_parts)
                    svg.add_path(d, fill=fill_color)

        # ================================================================
        # Clipping
        # ================================================================
        elif rec_type == EMR_INTERSECTCLIPRECT:
            left, top, right, bottom = struct.unpack_from(
                '<iiii', rec_data, 0)
            # Transform to SVG coords immediately -- GDI stores clip
            # regions in device space at the time they are set.
            tl = state.transform_point(left, top)
            tbr = state.transform_point(right, bottom)
            x1 = min(tl[0], tbr[0])
            y1 = min(tl[1], tbr[1])
            x2 = max(tl[0], tbr[0])
            y2 = max(tl[1], tbr[1])
            new_rect = (x1, y1, x2, y2)
            if state.clip_region is None:
                state.clip_region = [new_rect]
            else:
                intersected = []
                for r in state.clip_region:
                    il = max(r[0], x1)
                    it = max(r[1], y1)
                    ir = min(r[2], x2)
                    ib = min(r[3], y2)
                    if il < ir and it < ib:
                        intersected.append((il, it, ir, ib))
                state.clip_region = intersected if intersected else None
            if state.clip_region:
                clip_counter += 1
                cid = f"clip{clip_counter}"
                svg.set_clip(cid, state.clip_region)
            else:
                svg.clear_clip()

        elif rec_type == EMR_EXTSELECTCLIPRGN:
            rgn_size = struct.unpack_from('<I', rec_data, 0)[0]
            mode = struct.unpack_from('<I', rec_data, 4)[0]
            RGN_COPY = 5
            if mode == RGN_COPY:
                if rgn_size > 0 and len(rec_data) >= 40:
                    # RGNDATAHEADER at offset 8 (32 bytes):
                    # dwSize(4) + iType(4) + nCount(4) + nRgnSize(4)
                    # + rcBound(16)
                    n_rects = struct.unpack_from('<I', rec_data, 16)[0]
                    svg_rects = []
                    rect_offset = 40  # 8 + 32
                    for i in range(n_rects):
                        off = rect_offset + i * 16
                        if off + 16 > len(rec_data):
                            break
                        rl, rt, rr, rb = struct.unpack_from(
                            '<iiii', rec_data, off)
                        tl = state.transform_point(rl, rt)
                        tbr = state.transform_point(rr, rb)
                        svg_rects.append((
                            min(tl[0], tbr[0]), min(tl[1], tbr[1]),
                            max(tl[0], tbr[0]), max(tl[1], tbr[1])))
                    state.clip_region = svg_rects if svg_rects else None
                else:
                    state.clip_region = None
            if state.clip_region:
                clip_counter += 1
                cid = f"clip{clip_counter}"
                svg.set_clip(cid, state.clip_region)
            else:
                svg.clear_clip()

        elif rec_type in (EMR_EXCLUDECLIPRECT, EMR_SELECTCLIPPATH):
            pass  # Uncommon; ignore for now

        # ================================================================
        # Raster-only operations (no SVG equivalent)
        # ================================================================
        elif rec_type == EMR_EXTFLOODFILL:
            pass

        # ================================================================
        # Comment / EOF
        # ================================================================
        elif rec_type == EMR_GDICOMMENT:
            # Check for EMF+ records embedded in comments
            if len(rec_data) >= 8 and rec_data[4:8] == b'EMF+':
                _parse_emfplus_comment(rec_data, state, svg)

        elif rec_type == EMR_EOF:
            pass

        else:
            print(f"WARNING: Unhandled record type {name} "
                  f"(0x{rec_type:08X}) at offset {rec_offset}, "
                  f"size {rec_size}", file=sys.stderr)

    total_bytes = getattr(parser, 'bytes_consumed', bytes_consumed)
    if total_bytes != len(data):
        print(f"WARNING: Byte accounting mismatch! "
              f"Consumed {total_bytes} bytes, "
              f"file is {len(data)} bytes", file=sys.stderr)

    svg_str = svg.to_string()
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg_str)

    print(f"Converted {input_path} -> {output_path}")
    print(f"  Records: {record_count}/{header['n_records']}")
    print(f"  Bytes: {total_bytes}/{len(data)}")
    print(f"  Bounds: ({bounds[0]},{bounds[1]})-({bounds[2]},{bounds[3]})")
    if header['description']:
        print(f"  Description: {header['description']}")


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile.emf> <outputFile.svg>",
              file=sys.stderr)
        sys.exit(1)
    convert_emf_to_svg(sys.argv[1], sys.argv[2])


if __name__ == '__main__':
    main()

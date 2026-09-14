# Vibe coded by Codex
"""Classic monochrome FONT metrics and MacDraw's Roman TextEdit projection.

Independent implementation; no platform or LibreOffice implementation is used
at runtime. See macDraw.txt for the explicit font/environment profile.
"""
from __future__ import annotations

import base64
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import struct
import zlib

TEXT_ENVIRONMENT = {
    'profile': 'Classic Roman TextEdit with integer monochrome Font Manager metrics',
    'font_selection': 'exact size, twice size, half size, next larger, largest smaller',
    'fractional_widths': False,
    'stock_resources': 'Macintosh System 6.0.8 bitmap fonts, Toronto, New York 36, '
                       'and original LaserWriter font-suitcase bitmap strikes',
    'style_selection': 'size first, exact face, then weighted subset in FOND order; '
                       'synthesize only remaining face bits',
    'application_font_family': 3,
    'missing_family_substitution': 'Geneva (family 3), preserving requested point size and face',
    'limitation': 'The drawing does not identify its original System version or font-resource contents. '
                  'This declared rendering environment cannot certify that missing historical environment.'
}


def text_environment(revision):
    return dict(TEXT_ENVIRONMENT, macdraw_revision=revision,
                first_baseline='top + ascent + leading' if revision == 4 else 'top + ascent',
                unwrapped_width='maximum line advance' if revision == 4 else
                                'max(widest glyph + 5, maximum line advance + 5)',
                family_identity='not stored; installed-font menu index only' if revision == 4 else
                                'family ID from the saved font menu table')


class FontError(ValueError):
    pass


class MissingFont(FontError):
    pass


def is_substituted(family, resolved_family):
    """Family 1 denotes the application font in this declared environment."""
    return family != resolved_family and not (family == 1 and resolved_family == 3)


def trunc(n, d):
    return -(abs(n)//d) if n < 0 else n//d


def s16(n):
    return (n+32768) % 65536-32768


def resize_box(box, width, align):
    """MacDraw's 16-bit rectangle width setter (center rounds to even width)."""
    t, l, b, r = box
    if align & 3 == 1:
        r = s16(l+width)
    elif align & 3 == 2:
        half = trunc(s16(width+1), 2)
        middle = trunc(s16(l+r), 2)
        l, r = s16(middle-half), s16(middle+half)
    else:
        l = s16(r-width)
    return t, l, b, r


# SVG matrix a,b,c,d for the eight actual MacDraw point transformations.
TRANSFORMS = ((1,0,0,1), (0,1,-1,0), (-1,0,0,-1), (0,-1,1,0),
              (-1,0,0,1), (1,0,0,-1), (0,1,1,0), (0,-1,-1,0))


def transform_point(x, y, box, code):
    t, l, b, r = box
    cx, cy = (l+r)/2, (t+b)/2
    a, bb, c, d = TRANSFORMS[code]
    return cx+a*(x-cx)+c*(y-cy), cy+bb*(x-cx)+d*(y-cy)


class Strike:
    """A complete one-bit FONT/NFNT strike, including optional metric tables."""
    def __init__(self, raw, family, size, face=0, name='', source=''):
        self.raw, self.family, self.size, self.face = raw, family, size, face
        self.name, self.source = name, source
        self.digest = hashlib.sha256(raw).hexdigest()
        if len(raw) < 26:
            raise FontError('truncated FONT/NFNT header')
        (self.flags, self.first, self.last, self.widest, self.kern,
         self.ndescent, self.rect_width, self.height, ow,
         self.ascent, self.descent, self.leading, words) = struct.unpack_from('>H7hH4h', raw)
        if (self.flags & ~0x9003 or not 0 <= self.first <= self.last <= 255
                or not 0 < self.height <= 256 or not 0 < words <= 8192
                or not 0 < size <= 127 or not 0 <= face <= 127
                or min(self.ascent, self.descent, self.widest) < 0):
            raise FontError('unsupported FONT/NFNT strike encoding')
        self.row_bytes = words*2
        count = self.last-self.first+3
        loc = 26+self.row_bytes*self.height
        widths = 16+2*ow
        end = widths+(count-1)*2
        expected = (widths+count*2*(1+(self.flags & 1)+bool(self.flags & 2))
                    if self.flags & 3 else end)
        if widths != loc+count*2 or expected > len(raw):
            raise FontError('FONT/NFNT table offsets or resource length disagree')
        self.locations = struct.unpack_from(f'>{count}H', raw, loc)
        self.widths = struct.unpack_from(f'>{count-1}H', raw, widths)
        if (any(a > b for a,b in zip(self.locations, self.locations[1:]))
                or self.locations[-1] > self.row_bytes*8
                or self.widths[-1] & 0x8000):
            raise FontError('invalid FONT/NFNT glyph locations or missing-glyph entry')
        self.fractional_widths = None
        self.heights = None
        end = widths+count*2
        if self.flags & 2:
            self.fractional_widths = struct.unpack_from(f'>{count}H', raw, end)
            end += count*2
        if self.flags & 1:
            self.heights = struct.unpack_from(f'>{count}H', raw, end)
            if any((v >> 8)+(v & 255) > self.height for v in self.heights[:-1]):
                raise FontError('FONT/NFNT height table exceeds the strike bitmap')
        self.resource_tail = raw[expected:]
        # Optional tables are parsed even though the integer-width profile
        # does not use fractional advances or the height-table optimization.

    def index(self, char):
        i = char-self.first
        if not 0 <= i <= self.last-self.first or self.widths[i] & 0x8000:
            return self.last-self.first+1
        return i

    def advance(self, char):
        return 0 if char == 13 else self.widths[self.index(char)] & 255

    @lru_cache(maxsize=4096)
    def glyph(self, char):
        if char in (13,32):
            return ()
        i = self.index(char)
        left, right = self.locations[i:i+2]
        bearing = self.kern+(self.widths[i] >> 8)
        points = []
        top, height = (0,self.height) if self.heights is None else (self.heights[i] >> 8, self.heights[i] & 255)
        for y in range(top, top+height):
            off = 26+y*self.row_bytes
            for x in range(left, right):
                if self.raw[off+x//8] & (128 >> (x % 8)):
                    points.append((x-left+bearing, y-self.ascent))
        return tuple(points)


class FontBook:
    def __init__(self, bundle=None):
        self.strikes = {}
        self.menu = None
        self.menu_metadata = None
        if bundle is None:
            bundle = Path(__file__).with_name('macDraw-fonts.json')
        try:
            obj = json.loads(Path(bundle).read_text())
            if obj['format'] != 'macDraw bitmap font resources 1':
                raise FontError('unrecognized font bundle version')
            for row in obj['fonts']:
                raw = zlib.decompress(base64.b64decode(row['data'], validate=True))
                if hashlib.sha256(raw).hexdigest() != row['sha256']:
                    raise FontError('font bundle resource checksum mismatch')
                self.add(Strike(raw, row['family'], row['size'], row['face'],
                                row['name'], row['source']))
        except (KeyError, TypeError, ValueError, OSError, zlib.error) as exc:
            raise FontError(f'cannot load font bundle {bundle}: {exc}') from exc

    def add(self, strike):
        self.strikes[strike.family, strike.size, strike.face] = strike

    def load_menu(self, path):
        """Load an explicitly supplied original MacDraw 0.9 font-menu order.

        A drawing's menu position cannot identify a System's installed fonts.
        The caller supplies that missing context; no menu is guessed from text.
        """
        try:
            raw = Path(path).read_bytes()
            obj = json.loads(raw)
            menu = obj['families']
            if (obj['format'] != 'macDraw font menu 1' or not isinstance(menu, list)
                    or not 1 <= len(menu) <= 10
                    or any(type(f) is not int or not 0 <= f <= 65535 for f in menu)
                    or len(set(menu)) != len(menu)):
                raise FontError('expected one to ten distinct family IDs in menu order')
            source = obj.get('source', str(path))
            if not isinstance(source, str):
                raise FontError('font-menu source must be a string')
        except (KeyError, TypeError, ValueError, OSError) as exc:
            raise FontError(f'cannot load font menu {path}: {exc}') from exc
        self.menu = tuple(menu)
        self.menu_metadata = dict(families=menu, source=source,
                                  sha256=hashlib.sha256(raw).hexdigest())

    def load_resource(self, path):
        """An explicitly supplied resource fork overrides matching stock strikes."""
        entries = read_resources(Path(path).read_bytes())
        by_id = {(tag, rid): (name, raw) for tag, rid, name, raw in entries}
        found = []
        associated = set()
        for tag, rid, name, raw in entries:
            if tag != b'FOND':
                continue
            if len(raw) < 54:
                raise FontError('truncated FOND header')
            family = struct.unpack_from('>H', raw, 2)[0]
            n = struct.unpack_from('>H', raw, 52)[0]+1
            if 54+6*n > len(raw):
                raise FontError('truncated FOND association table')
            for i in range(n):
                size, face, resource_id = struct.unpack_from('>HHh', raw, 54+6*i)
                if size == 0:
                    continue  # Scalable sfnt entries are not bitmap strikes.
                key = next((k for k in ((b'NFNT', resource_id), (b'FONT', resource_id))
                            if k in by_id), None)
                if key is None:
                    raise FontError(f'FOND references absent bitmap resource {resource_id}')
                associated.add(key)
                found.append(Strike(by_id[key][1], family, size, face, name, str(path)))
        for tag, rid, name, raw in entries:
            if tag == b'FONT' and (tag, rid) not in associated and (rid & 127):
                found.append(Strike(raw, (rid & 65535)//128, rid & 127, 0, name, str(path)))
        if not found:
            raise FontError('font resource file contains no supported bitmap font strikes')
        # Replacing existing dictionary values would retain the old insertion
        # order, changing equal-weight face selection. Give the supplied FOND
        # associations their own order before surviving fallback strikes.
        replacements = {(s.family, s.size, s.face): s for s in found}
        previous = self.strikes
        self.strikes = replacements.copy()
        self.strikes.update((key, strike) for key, strike in previous.items()
                            if key not in replacements)

    def resolve(self, family, size, face):
        if family == 1:
            return self.resolve(TEXT_ENVIRONMENT['application_font_family'], size, face)
        families = [s for (f, _, _), s in self.strikes.items() if f == family]
        if not families:
            # The user-authorized fallback is fixed and independent of names,
            # character content or sample files. Original IDs remain in audits.
            if family == 3:
                raise MissingFont('fallback font Geneva (family 3) is unavailable')
            return self.resolve(3, size, face)
        sizes = {s.size for s in families}
        # Original integer bitmap Font Manager lookup, not a nearest-font guess:
        # exact, twice requested, half requested, next larger, largest smaller.
        if size in sizes:
            actual = size
        elif size*2 in sizes:
            actual = size*2
        elif size % 2 == 0 and size//2 in sizes:
            actual = size//2
        else:
            actual = min((s for s in sizes if s > size), default=max(sizes))
        # Font Manager selects size before face. At that size, an exact face
        # wins; otherwise use the subset with the greatest native style weight.
        # Equal weights keep FOND association order. With no subset, the first
        # strike is the native fallback. QuickDraw synthesizes remaining bits.
        weights = (4, 8, 1, 3, 3, 2, 1)
        candidates = [s for s in families if s.size == actual]
        def score(strike):
            if strike.face == face:
                return 100
            if strike.face & ~face:
                return -1
            return sum(w for bit, w in enumerate(weights) if strike.face & (1 << bit))
        strike = max(candidates, key=score)
        return Metrics(strike, size, face & ~strike.face)


@lru_cache(maxsize=1)
def default_fonts():
    return FontBook()


def read_resources(raw):
    """Bounds-checked raw resource fork or AppleDouble resource-fork entry.

    Used for font suitcases and explicit MacDraw Pro drawing resources.
    Drawing-file wrapper detection is separate; payload decoding is the caller's
    responsibility.
    """
    def need(a, n, limit=None):
        if a < 0 or n < 0 or a+n > (len(raw) if limit is None else limit):
            raise FontError('truncated or out-of-bounds font resource container')
    need(0, 16)
    if raw[:4] == b'\x00\x05\x16\x07':
        need(0, 26)
        if raw[4:8] not in (b'\x00\x01\x00\x00', b'\x00\x02\x00\x00'):
            raise FontError('unsupported AppleDouble version')
        n = struct.unpack_from('>H', raw, 24)[0]
        need(26, n*12)
        fork = None
        for i in range(n):
            kind, off, size = struct.unpack_from('>III', raw, 26+i*12)
            need(off, size)
            if kind == 2:
                if fork is not None:
                    raise FontError('duplicate AppleDouble resource fork')
                fork = raw[off:off+size]
        if fork is None:
            raise FontError('AppleDouble file has no resource fork')
        return read_resources(fork)
    data, mapoff, datalen, maplen = struct.unpack_from('>4I', raw)
    need(data, datalen); need(mapoff, maplen); need(mapoff, 28)
    if (data < 16 or mapoff < 16 or maplen < 28
            or max(data, mapoff) < min(data+datalen, mapoff+maplen)):
        raise FontError('overlapping or invalid resource data/map regions')
    types, names = struct.unpack_from('>2H', raw, mapoff+24)
    types += mapoff; names += mapoff
    limit = mapoff+maplen
    if types < mapoff+28 or names < mapoff+28:
        raise FontError('invalid resource map table offsets')
    need(types, 2, limit); need(names, 0, limit)
    count = struct.unpack_from('>H', raw, types)[0]
    count = 0 if count == 65535 else count+1
    need(types+2, count*8, limit)
    out = []; seen = set()
    for i in range(count):
        tag, n, refs = struct.unpack_from('>4sHH', raw, types+2+i*8)
        ref = types+refs
        need(ref, (n+1)*12, limit)
        for j in range(n+1):
            at = ref+j*12
            rid, name_at = struct.unpack_from('>hH', raw, at)
            off = data+int.from_bytes(raw[at+5:at+8], 'big')
            if off < data:
                raise FontError('invalid resource data offset')
            need(off, 4, data+datalen)
            length = struct.unpack_from('>I', raw, off)[0]
            need(off+4, length, data+datalen)
            name = ''
            if name_at != 65535:
                p = names+name_at; need(p, 1, limit); need(p+1, raw[p], limit)
                name = raw[p+1:p+1+raw[p]].decode('mac_roman')
            if (tag, rid) in seen:
                raise FontError('duplicate resource type and ID')
            seen.add((tag, rid))
            out.append((tag, rid, name, raw[off+4:off+4+length]))
    return out


@dataclass(frozen=True)
class Metrics:
    strike: Strike
    size: int | float
    face: int

    @property
    def extra(self):
        return bool(self.face & 1)+bool(self.face & 8)+2*bool(self.face & 16)-bool(self.face & 32)+bool(self.face & 64)

    @property
    def shadow(self):
        return bool(self.face & 8)+2*bool(self.face & 16)

    @property
    def numer(self):
        # Font Manager represents the size scale as a rounded 8.8 ratio.
        return int((self.size*256+self.strike.size//2)//self.strike.size)

    def ceil_scale(self, value):
        return -((-value*self.numer)//256)

    def round_scale(self, value):
        return (value*self.numer+128)//256

    @property
    def ascent(self):
        return self.ceil_scale(self.strike.ascent+bool(self.shadow))

    @property
    def descent(self):
        return self.ceil_scale(self.strike.descent+self.shadow)

    @property
    def leading(self):
        return self.ceil_scale(self.strike.leading)

    @property
    def widest(self):
        return self.ceil_scale(self.strike.widest+self.extra)

    def advance(self, char):
        return 0 if char == 13 else self.strike.advance(char)+self.extra

    def width(self, chars):
        return self.round_scale(sum(self.advance(c) for c in chars))

    @lru_cache(maxsize=512)
    def pixels(self, chars):
        """Return ink and white-interior masks for one native DrawText chunk.

        Pixel coordinates are relative to the unscaled baseline/pen location.
        Bold, italic, underline, outline and shadow act on the chunk buffer.
        """
        ink = set(); pen = 0
        for c in chars:
            ink.update((pen+x, y) for x,y in self.strike.glyph(c))
            pen += self.advance(c)
        if self.face & 1:
            ink |= {(x+1,y) for x,y in ink}
        if self.face & 2:
            # The bottom row shifts 8/16 pixels, the next 16/16, etc.
            ink = {(x+(self.strike.height-self.strike.ascent-y)//2, y) for x,y in ink}
        if self.face & 4 and self.strike.descent >= 2:
            avoid = {x+d for x,y in ink if 0 <= y <= min(2,self.strike.descent-1)
                     for d in (-1,0,1)}
            ink |= {(x,1) for x in range(max(0,pen)) if x not in avoid}
        if self.shadow:
            original = {(x,y) for x,y in ink if 0 <= x < pen+32}
            ink = {(x+dx,y+dy) for x,y in ink
                   for dx in range(-1,self.shadow+1)
                   for dy in range(-1,self.shadow+1)
                   if -1 <= x+dx < pen+31}-original
            return frozenset(ink), frozenset(original)
        return frozenset((x,y) for x,y in ink if 0 <= x < pen+32), frozenset()


def line_ranges(chars, metrics, width, wrap):
    """Roman TextEdit CR/word boundaries; byte offsets include trailing breaks."""
    if not chars:
        return [(0,0)]
    result = []; start = 0; n = len(chars)
    while start < n:
        i = start; advance = 0
        while i < n:
            c = chars[i]
            if c == 13:
                i += 1
                break
            next_advance = advance+metrics.advance(c)
            if wrap and metrics.round_scale(next_advance) > width-1:
                # Break separators stay on the preceding line, including a CR.
                if c <= 32:
                    while i < n and chars[i] <= 32:
                        c = chars[i]; i += 1
                        if c == 13:
                            break
                else:
                    word = i
                    while word > start and chars[word-1] > 32:
                        word -= 1
                    if word > start:
                        i = word
                    elif i == start:
                        i += 1
                break
            advance = next_advance
            i += 1
        result.append((start,i)); start = i
    if chars[-1] == 13:
        result.append((n,n))
    return result


@dataclass
class Layout:
    metrics: Metrics
    box: tuple
    line_height: int
    lines: list


def layout(fields, wrap, fonts, *, revision=6):
    if revision not in (4, 6):
        raise FontError('unsupported MacDraw text layout revision')
    chars = fields['text_bytes']
    metrics = fonts.resolve(fields['font_id'], (9,10,12,14,18,24,36,48)[fields['size_index']-1], fields['face'])
    if len(chars) > 32767:
        raise FontError('text exceeds the classic TextEdit signed length limit')
    box = fields['box']; align = fields['align'] & 3
    minimum = metrics.widest+5
    if box[3]-box[1] < minimum:
        box = resize_box(box, minimum, align)
    if box[3] <= box[1]:
        raise FontError('text rectangle overflows signed 16-bit coordinates')
    ranges = line_ranges(chars, metrics, max(7,box[3]-box[1]), bool(wrap))
    if not wrap:
        width = max(metrics.width(chars[a:b]) for a,b in ranges)
        # 0.9 recalculates unwrapped width without the extra margin/clamp
        # used by 1.x. Both versions round centered widths to an even value.
        if revision == 6:
            width = max(minimum, width+5)
        if width > 32766:
            raise FontError('text line width exceeds signed 16-bit layout range')
        box = resize_box(box, width, align)
    step = ((fields['spacing']+1)*(metrics.ascent+metrics.descent+metrics.leading))//2
    t,l,b,r = box
    b = t+step*len(ranges)
    if r < l or not -32768 <= b <= 32767 or step <= 0:
        raise FontError('text layout exceeds signed 16-bit rectangle limits')
    lines = []
    for index,(a,end) in enumerate(ranges):
        visible_end = end
        while visible_end > a and chars[visible_end-1] == 13:
            visible_end -= 1
        # Right justification trims trailing break characters (at least the
        # first character survives); centered lines use their full advance.
        measured_end = visible_end
        if align == 3:
            while measured_end > a+1 and chars[measured_end-1] <= 32:
                measured_end -= 1
        width = metrics.width(chars[a:measured_end])
        x = l+1 if align == 1 else (l+1+(r-l-1-width)//2 if align == 2 else r-width)
        ascent = metrics.ascent+(metrics.leading if revision == 4 else 0)
        lines.append((x, t+ascent+index*step, chars[a:visible_end]))
    return Layout(metrics, (t,l,b,r), step, lines)


def pixel_path(points):
    """Join consecutive black pixels into horizontal one-pixel-high rectangles."""
    rows = {}
    for x,y in points:
        rows.setdefault(y, []).append(x)
    parts = []
    for y in sorted(rows):
        xs = sorted(rows[y]); i = 0
        while i < len(xs):
            left = xs[i]; right = left+1; i += 1
            while i < len(xs) and xs[i] == right:
                right += 1; i += 1
            parts.append(f'M{left} {y}h{right-left}v1h{left-right}z')
    return ''.join(parts)

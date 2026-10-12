# Vibe coded by Codex
"""Decode Authorware PIG display lists and reconstruct self-contained SVGs.

This module keeps record parsing, resource resolution and rendering separate.
Unknown records stop parsing; rendering limitations are returned as diagnostics
and embedded in SVG metadata rather than silently declaring a complete picture.
No project scripts, linked files, URLs, or imported code are executed.
"""

import base64
from collections import Counter, defaultdict
from functools import lru_cache
import hashlib
import json
import math
import re
import struct
import zlib
from xml.etree import ElementTree as ET

from authorware_symbol import SYMBOL_CHARACTERS


NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
FIXED = {0x01: 2, 0x02: 2, 0x06: 8, 0x0A: 10, 0x0E: 8,
         0x21: 2, 0x22: 2, 0x23: 6, 0x26: 8, 0x2A: 10, 0x2E: 8,
         0x40: 2, 0x41: 2, 0x42: 2, 0x43: 2, 0x48: 4, 0x49: 2,
         0x50: 4, 0x51: 4, 0x71: 10, 0x75: 10, 0x7D: 10,
         0x81: 14, 0x89: 18}
VARIABLE = {0x54, 0x56, 0x60, 0x65, 0x8D, 0x98, 0x9A}
OP_NAMES = {
    0x01: 'fill on', 0x02: 'fill off', 0x06: 'fill color',
    0x0A: 'fill pattern', 0x0E: 'fill background', 0x21: 'frame on',
    0x22: 'frame off', 0x23: 'pen size', 0x26: 'pen color',
    0x2A: 'pen pattern', 0x2E: 'pen background',
    0x40: 'begin group', 0x41: 'end group', 0x42: 'begin frame',
    0x43: 'end frame', 0x48: 'arrowheads', 0x49: 'end arrowheads',
    0x50: 'transfer mode', 0x51: 'drawing state', 0x54: 'palette mapping',
    0x56: 'palette', 0x60: 'bitmap reference', 0x65: 'embedded bitmap',
    0x71: 'rectangle', 0x75: 'line', 0x7D: 'ellipse',
    0x81: 'rounded rectangle', 0x89: 'arc', 0x8D: 'polygon',
    0x98: 'styled text', 0x9A: 'imported image',
}


def word(data, offset=0, endian='<'):
    return struct.unpack_from(endian + 'H', data, offset)[0]


def longword(data, offset=0, endian='<'):
    return struct.unpack_from(endian + 'I', data, offset)[0]


def rectangle(data, offset=0, endian='<'):
    """Return left/top/right/bottom from Windows RECT or Macintosh Rect."""
    a, b, c, d = struct.unpack_from(endian + '4h', data, offset)
    # Macintosh serialization keeps QuickDraw's vertical-first geometry even
    # when the PIG platform tag is WIN (for example, embedded Windows DIBs).
    return (b, a, d, c) if endian == '>' else (a, b, c, d)


def point(data, offset=0, endian='<'):
    """Normalize Windows x/y and Macintosh v/h points or size pairs."""
    a, b = struct.unpack_from(endian + 'hh', data, offset)
    return (b, a) if endian == '>' else (a, b)


def parse_pig(data):
    """Return bounded records, respecting the count instead of heap padding."""
    result = {'records': [], 'warnings': [], 'bounds': None, 'endian': '<'}
    if len(data) < 42 or data[2:6] != b'PIG\0' or data[6:9] not in (b'WIN', b'MAC'):
        result['warnings'].append('Invalid or truncated PIG header')
        return result
    endian = '>' if longword(data, 14) > 65535 else '<'
    result.update(endian=endian, platform=data[6:9].decode('ascii'),
                  bounds=rectangle(data, 26, endian))
    if data[10:14] != b'001\0':
        result['warnings'].append('Unrecognized PIG version')
        return result
    count = longword(data, 14, endian)
    result['declared_records'] = count - 1
    if not 1 <= count <= (len(data) - 42) // 2 + 1:
        result['warnings'].append('Invalid PIG record count')
        return result
    offset = 42
    for index in range(count - 1):
        if offset + 2 > len(data):
            result['warnings'].append(f'Truncated record {index} at byte {offset}')
            break
        tag = word(data, offset, endian)
        size = FIXED.get(tag)
        if tag in VARIABLE and offset + 6 <= len(data):
            size = longword(data, offset + 2, endian)
        if size is None:
            result['warnings'].append(f'Unknown operation 0x{tag:04X} at byte {offset}')
            break
        if size < (6 if tag in VARIABLE else 2) or offset + size > len(data):
            result['warnings'].append(f'Invalid length for 0x{tag:04X} at byte {offset}')
            break
        result['records'].append((tag, offset, data[offset:offset + size]))
        offset += size
    result['used_bytes'] = offset
    result['padding_bytes'] = len(data) - offset
    return result


def text_layout(record, endian='<', platform='WIN'):
    """Read the style transitions, stored line baselines and character runs."""
    if len(record) < 100:
        raise ValueError('Short styled-text record')
    count = longword(record, 52, endian)
    changes_size = longword(record, 40, endian)
    lines_size = longword(record, 74, endian)
    runs_size = longword(record, 78, endian)
    changes_end = 90 + changes_size
    lines_end = changes_end + lines_size
    runs_end = lines_end + runs_size
    text_end = runs_end + ((count + 1) & ~1)
    if (changes_size < 2 or (changes_size - 2) % 8 or lines_size < 16 or lines_size % 8 or runs_size % 10
            or text_end > len(record) or count > 1_000_000):
        raise ValueError('Unrecognized styled-text layout')
    if word(record, 90, endian) != 8:
        raise ValueError('Unrecognized text style-transition size')
    raw = record[runs_end:runs_end + count]
    encoding = 'mac_roman' if platform == 'MAC' else 'cp1252'
    text = raw.decode(encoding, errors='replace')
    # XML cannot contain the control bytes present in some old text runs.
    text = ''.join(c if ord(c) >= 32 or c in '\t\n\r' else '\ufffd' for c in text)
    changes = [struct.unpack_from(endian + 'HhH', record, i)
               for i in range(92, changes_end, 8)]
    # Eight bytes per line; the final row is a sentinel giving the last
    # character index and bottom edge, with unused cached coordinates.
    lines = [struct.unpack_from(endian + 'HhhhHh', record, i) + (0, 0)
             for i in range(changes_end, lines_end - 8, 8)]
    runs = [struct.unpack_from(endian + 'HHI', record, i)
            for i in range(lines_end, runs_end, 10) if record[i + 8] == 1]
    inline = [longword(record, i + 4, endian) for i in range(lines_end, runs_end, 10)
              if record[i + 8] == 4]
    bad_runs = any(start > end or end > count for start, end, _ in runs)
    runs = [(start, end, style) for start, end, style in runs if start <= end <= count]
    if (any(start > end or end > count for start, _, _, _, end, *_ in lines)
            or any(start > count for start, _, _ in changes)):
        raise ValueError('Text ranges lie outside character data')
    return {'text': text, 'raw': raw, 'changes': changes, 'lines': lines, 'runs': runs,
            'inline_objects': inline, 'invalid_runs': bad_runs,
            'bounds': rectangle(record, 6, endian), 'background': '#' + record[56:59].hex()}


class FontTable:
    """Read cached fonts and sparse character-style overrides from type 0x19.

Style blocks have a fixed 84-byte prefix and may have variable extension
data. Lookups validate the fixed fields and reject ambiguous identifiers.
Font substitution remains a viewer responsibility; fonts are not embedded.
"""

    def __init__(self, data):
        self.styles, self.fonts = {}, {}
        self.valid = False
        if len(data) < 24:
            return
        endian = '<' if data[:2] == b'\x13\0' else '>' if data[:2] == b'\0\x13' else None
        if not endian:
            return
        end, names_size, metrics_size = struct.unpack_from(endian + 'III', data, 6)
        if not 24 <= end <= len(data) or end + metrics_size + names_size > len(data) or metrics_size < 4:
            return
        count, stride = struct.unpack_from(endian + 'HH', data, end)
        if stride not in (62, 64) or 4 + count * stride > metrics_size:
            return
        names = data[end + metrics_size:end + metrics_size + names_size]
        legacy_names = len(names) >= 4 and word(names, 2, endian) == 64
        if not legacy_names and names_size % 128:
            return
        for index in range(count):
            record = data[end + 4 + index * stride:end + 4 + (index + 1) * stride]
            family = word(record, 0, endian)
            native_mac = word(record, 6, endian) == 16
            name_offset = (4 + (family-1)*64 if legacy_names else family*128) + (0 if native_mac else 32)
            name_data = names[max(0, name_offset):max(0, name_offset) + 32]
            name = name_data.split(b'\0')[0].decode('mac_roman' if native_mac else 'cp1252', errors='replace')
            if not name or any(ord(c) < 32 for c in name):
                name = 'serif'
            size = abs(struct.unpack_from(endian + 'h', record, 8 if native_mac else 28)[0])
            if 0 < size <= 512:
                self.fonts[index + 1] = {'family': name, 'size': size}
        candidates = defaultdict(list)
        ordered = []
        for offset in range(24, end - 83, 2):
            record = data[offset:offset + 84]
            style_id, flags = struct.unpack_from(endian + 'HI', record)
            metric = word(record, 40, endian)
            # These validation fields distinguish serialized style records
            # from optional tab stops, coordinates and strings between them.
            if (not style_id or word(record, 14, endian) not in (0x01, 0x09, 0x11, 0x81, 0x89, 0x91)
                    or metric > count or word(record, 16, endian) > 4
                    or word(record, 38, endian) > 1024 or flags & 0xF0000000):
                continue
            item = {
                'mask': flags, 'color': '#' + record[6:9].hex(),
                'attributes': word(record, 20, endian), 'font': metric,
            }
            candidates[style_id].append(item)
            ordered.append((offset, style_id, item))
        self.styles = {key: values[0] for key, values in candidates.items() if len(values) == 1}
        # IDs are ordered and fixed prefixes cannot overlap. Require the
        # declared count before preferring this complete table partition.
        partition, next_offset, last_id = {}, 24, 0
        for offset, style_id, item in ordered:
            if offset >= next_offset and style_id > last_id:
                partition[style_id] = item
                next_offset, last_id = offset + 84, style_id
        if len(partition) == word(data, 2, endian):
            self.styles = partition
        self.valid = bool(self.fonts)

    def apply(self, style, style_id, missing):
        item = self.styles.get(style_id)
        if item is None:
            if style_id:
                missing.add(style_id)
            return
        mask = item['mask']
        if mask & 0x4000:
            style['color'] = item['color']
        if mask & 0x200:
            font = self.fonts.get(item['font'])
            if font:
                style.update(font)
        attributes = mask & 0x7f
        style['attributes'] = (style['attributes'] & ~attributes) | (item['attributes'] & attributes)


def png_rgba(width, height, rows):
    def chunk(kind, payload):
        return struct.pack('>I', len(payload)) + kind + payload + struct.pack('>I', zlib.crc32(kind + payload) & 0xffffffff)
    compressor = zlib.compressobj()
    content = bytearray()
    for row in rows:
        content.extend(compressor.compress(b'\0' + row))
    content.extend(compressor.flush())
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
            + chunk(b'IDAT', content) + chunk(b'IEND', b''))


@lru_cache(maxsize=32)
def dib_png(api, data, palette=None, color_key=None):
    """Normalize DIB compression/palettes, then encode browser-portable PNG."""
    data = api.normalize_dib(data, palette)
    if data is None:
        raise ValueError('Bitmap pixels or palette could not be decoded')
    fields = api.dib_fields(data)
    size, width, height, _, bpp, compression, _, _, _, colors, _ = fields
    height_abs = abs(height)
    if width * height_abs > 40_000_000:
        raise ValueError('Bitmap exceeds the SVG conversion pixel limit')
    # Optional acceleration. The standard-library path below remains available
    # when Pillow is absent; both paths operate on the same normalized DIB.
    try:
        import io
        from PIL import Image, ImageChops
        bmp = api.make_bmp_from_dib(data)
        with Image.open(io.BytesIO(bmp)) as original:
            image = original.convert('RGBA')
            if color_key is not None:
                difference = ImageChops.difference(image.convert('RGB'), Image.new('RGB', image.size, color_key))
                red, green, blue = difference.split()
                alpha = ImageChops.lighter(ImageChops.lighter(red, green), blue).point(lambda x: 255 if x else 0)
                image.putalpha(ImageChops.multiply(image.getchannel('A'), alpha))
            output = io.BytesIO()
            image.save(output, 'PNG')
            return output.getvalue(), width, height_abs
    except (ImportError, OSError, ValueError):
        pass
    masks = (16 if compression == 6 else 12) if size == 40 and compression in (3, 6) else 0
    palette_size = (colors or (1 << bpp)) if bpp <= 8 else 0
    table = data[size + masks:size + masks + palette_size * 4]
    offset = size + masks + len(table)
    stride = ((width * bpp + 31) // 32) * 4
    endian = api.dib_endian(data)
    channels = None
    alpha_mask = 0
    if bpp in (16, 32):
        channels = (0x7c00, 0x03e0, 0x001f) if bpp == 16 else (0xff0000, 0xff00, 0xff)
        if compression in (3, 6):
            channels = struct.unpack_from(endian + 'III', data, 40)
            if compression == 6 or size >= 56:
                alpha_mask = longword(data, 52, endian)
    def component(value, mask):
        if not mask:
            return 0
        shift = (mask & -mask).bit_length() - 1
        maximum = mask >> shift
        return ((value & mask) >> shift) * 255 // maximum
    def rows():
        for y in range(height_abs):
            index = height_abs - 1 - y if height > 0 else y
            source = data[offset + index * stride:offset + (index + 1) * stride]
            row = bytearray(width * 4)
            for x in range(width):
                if bpp <= 8:
                    idx = source[x] if bpp == 8 else (source[x // 2] >> (4 if x % 2 == 0 else 0)) & 15 if bpp == 4 else (source[x // 8] >> (7 - x % 8)) & 1
                    if idx >= palette_size:
                        raise ValueError('Pixel index outside bitmap palette')
                    blue, green, red = table[idx*4:idx*4+3]
                elif bpp == 24:
                    blue, green, red = source[x*3:x*3+3]
                elif bpp in (16, 32):
                    value = int.from_bytes(source[x*(bpp//8):(x+1)*(bpp//8)], 'little')
                    red, green, blue = (component(value, mask) for mask in channels)
                else:
                    raise ValueError(f'Unsupported bitmap depth {bpp}')
                alpha = component(value, alpha_mask) if alpha_mask and bpp in (16,32) else 255
                if color_key == (red, green, blue):
                    alpha = 0
                row[x*4:x*4+4] = bytes((red, green, blue, alpha))
            yield row
    return png_rgba(width, height_abs, rows()), width, height_abs


class Context:
    """Resolve references using actual entry IDs, including ambiguous legacy IDs."""

    def __init__(self, api, data, entries):
        self.api, self.data, self.entries = api, data, entries
        self.by_id = defaultdict(list)
        self.dib_palettes = defaultdict(set)
        self.font_tables = []
        for index, entry in enumerate(entries):
            self.by_id[entry['id']].append(index)
            if entry['icon_type'] == 0x19 or (entry['icon_type'] == 0x06 and 24 <= entry['decomp_size'] <= 2_000_000):
                font_data = api.decompress_entry(data, entry)
                if font_data and font_data[:2] in (b'\x13\0', b'\0\x13'):
                    fonts = FontTable(font_data)
                    if fonts.valid:
                        self.font_tables.append(fonts)
        self.fonts = self.font_tables[0] if self.font_tables else FontTable(b'')

    @lru_cache(maxsize=128)
    def entry(self, index):
        return self.api.decompress_entry(self.data, self.entries[index])

    def reference(self, entry_id):
        candidates = [index for index in self.by_id.get(entry_id, [])
                      if self.entries[index]['icon_type'] in (0x35, 0x3E, 0x3B, 0x06)]
        if len(candidates) != 1:
            raise ValueError(f'Image reference {entry_id} is missing or ambiguous')
        index = candidates[0]
        content = self.entry(index)
        if content is None:
            raise ValueError(f'Image reference {entry_id} could not be decompressed')
        return index, content

    def record_dib_palette(self, index, palette):
        """Remember the palette active at an explicit DIB draw operation."""
        if index is None or self.entries[index]['icon_type'] != 0x35:
            return
        fields = self.api.dib_fields(self.entry(index))
        if fields and fields[4] <= 8:
            size = (fields[9] or (1 << fields[4])) * 4
            self.dib_palettes[index].add(palette[:size] if palette and len(palette) >= size else None)

    def standalone_palette(self, index):
        """Only an unambiguous explicit reference can supply missing colors."""
        candidates = self.dib_palettes.get(index, set())
        if len(candidates) == 1 and None not in candidates:
            return next(iter(candidates)), None
        reason = ('Conflicting or incomplete palettes in referencing PIGs'
                  if candidates else 'No palette established by an explicit PIG reference')
        return None, reason


def svg_element(parent, name, **attributes):
    return ET.SubElement(parent, '{' + NS + '}' + name,
                         {key.replace('_', '-'): str(value) for key, value in attributes.items()})


@lru_cache(maxsize=256)
def installed_font(family, size, attributes):
    try:
        import subprocess
        from PIL import ImageFont
        spec = family + (':style=Bold' if attributes & 1 else ':style=Regular')
        if attributes & 2:
            spec += ' Italic'
        result = subprocess.run(['fc-match', '-f', '%{file}', spec], capture_output=True,
                                text=True, timeout=3, check=True)
        return ImageFont.truetype(result.stdout, max(1, round(size)))
    except (ImportError, OSError, ValueError, subprocess.SubprocessError):
        return None


def text_advance(text, family, size, attributes):
    font = installed_font(family, size, attributes)
    if font:
        return font.getlength(text)
    return sum(size * (0.28 if c.isspace() else 0.55) for c in text)


class Renderer:
    def __init__(self, context, pig, parsed):
        self.context, self.api, self.pig, self.parsed = context, context.api, pig, parsed
        self.endian = parsed['endian']
        self.warnings = list(parsed['warnings'])
        self.notes = []
        self.texts, self.missing_styles = [], set()
        self.drawn = 0
        self.rendered_dibs = set()
        self.bounds = parsed['bounds']
        left, top, right, bottom = self.bounds
        self.root = ET.Element('{' + NS + '}svg', {
            'viewBox': f'{left} {top} {right-left} {bottom-top}',
            'width': str(right-left), 'height': str(bottom-top), 'version': '1.1',
        })
        self.root.append(ET.Comment(' Vibe coded by Codex '))
        self.defs = svg_element(self.root, 'defs')
        self.state = {'fill': True, 'frame': False, 'fill_color': '#000000',
                      'fill_back': '#ffffff', 'pen_color': '#000000', 'pen_back': '#ffffff',
                      'fill_pattern': b'\xff'*8, 'pen_pattern': b'\xff'*8,
                      'width': 1, 'mode': 0, 'arrows': 0}
        self.palette = None
        self.groups = []
        self.patterns = {}

    def warning(self, message):
        if message not in self.warnings:
            self.warnings.append(message)

    def paint(self, part):
        s = self.state
        pattern = s[part + '_pattern']
        fore, back = s[part + '_color'], s[part + '_back']
        if pattern == b'\xff'*8:
            return fore
        if pattern == b'\0'*8:
            return back
        key = (pattern, fore, back)
        if key not in self.patterns:
            name = f'pattern{len(self.patterns)}'
            self.patterns[key] = name
            node = svg_element(self.defs, 'pattern', id=name, width=8, height=8,
                               patternUnits='userSpaceOnUse')
            svg_element(node, 'rect', width=8, height=8, fill=back)
            path = ''.join(f'M{x} {y}h1v1h-1z' for y, byte in enumerate(pattern)
                           for x in range(8) if byte & (128 >> x))
            svg_element(node, 'path', d=path, fill=fore)
        return f'url(#{self.patterns[key]})'

    def attrs(self, line=False):
        s = self.state
        attrs = {'fill': 'none' if line or not s['fill'] else self.paint('fill'),
                 'stroke': self.paint('pen') if line or s['frame'] else 'none',
                 'stroke_width': s['width'], 'stroke_linejoin': 'miter', 'stroke_linecap': 'square'}
        if s['mode'] in (2, 3):
            # Logical raster operations depend on the surrounding stage.
            attrs['style'] = 'mix-blend-mode:difference'
            self.warning(f'Transfer mode {s["mode"]} uses an approximate SVG blend')
        return attrs

    def shape(self, name, **attrs):
        self.drawn += 1
        return svg_element(self.root, name, **attrs)

    def arrows(self, x1, y1, x2, y2):
        flags = self.state['arrows']
        for start in (True, False):
            if not flags & (1 if start else 2):
                continue
            x, y = (x1, y1) if start else (x2, y2)
            dx, dy = (x2-x1, y2-y1) if start else (x1-x2, y1-y2)
            length = math.hypot(dx, dy)
            if not length:
                continue
            dx, dy = dx/length, dy/length
            size = 6 + self.state['width'] * 2
            a = (x + size*dx + size*.45*dy, y + size*dy - size*.45*dx)
            b = (x + size*dx - size*.45*dy, y + size*dy + size*.45*dx)
            self.shape('path', d=f'M{a[0]} {a[1]}L{x} {y}L{b[0]} {b[1]}', **self.attrs(True))

    def font_style(self, base, overlays, fallback_size):
        style = {'family': 'Arial', 'size': fallback_size, 'color': '#000000', 'attributes': 0}
        self.context.fonts.apply(style, base, self.missing_styles)
        for value in overlays:
            self.context.fonts.apply(style, value, self.missing_styles)
        return style

    def text(self, record):
        if longword(record, 14, self.endian) in (0, 5):
            self.legacy_text(record)
            return
        layout = text_layout(record, self.endian, self.parsed['platform'])
        self.texts.append(layout['text'])
        if layout['inline_objects']:
            self.warning('Dynamic/inline text objects retain their stored placeholder text')
        if layout['invalid_runs']:
            self.warning('Invalid stored text-style ranges were ignored')
        if not layout['lines'] and layout['text']:
            raise ValueError('Text has no stored line positions')
        changes = layout['changes']
        for start, top, x, baseline, end, bottom, _, _ in layout['lines']:
            boundaries = {start, end}
            boundaries.update(pos for pos, _, _ in changes if start < pos < end)
            for first, last, _ in layout['runs']:
                if start < first < end:
                    boundaries.add(first)
                if start < last < end:
                    boundaries.add(last)
            node = self.shape('text', x=x, y=baseline)
            node.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            positions = sorted(boundaries)
            for first, last in zip(positions, positions[1:]):
                applicable = [item for item in changes if item[0] <= first]
                _, delta, base = applicable[-1] if applicable else (0, 0, 0)
                overlays = [style for begin, finish, style in layout['runs'] if begin <= first < finish]
                style = self.font_style(base, overlays, max(8, baseline-top))
                part = layout['text'][first:last].replace('\r', '').replace('\n', '')
                if not part:
                    continue
                if style['family'].lower() == 'symbol':
                    part = ''.join(SYMBOL_CHARACTERS.get(byte, '\ufffd')
                                   for byte in layout['raw'][first:last] if byte not in (10,13))
                    if any(0xe000 <= ord(c) <= 0xf8ff or c == '\ufffd' for c in part):
                        self.warning('Symbol font contains private-use or unmapped glyphs')
                    style['family'] = 'serif'
                attrs = {'font_family': style['family'], 'font_size': style['size'],
                         'fill': style['color'], 'y': baseline-delta}
                bits = style['attributes']
                if bits & 1:
                    attrs['font_weight'] = 'bold'
                if bits & 2:
                    attrs['font_style'] = 'italic'
                if bits & 4:
                    attrs['text_decoration'] = 'underline'
                span = svg_element(node, 'tspan', **attrs)
                span.text = part

    def legacy_text(self, record):
        """Older text objects store inline font runs but no cached line layout."""
        en = self.endian
        version = longword(record, 14, en)
        header = 56 if version == 0 else 72
        style_size, extra1, extra2, count = struct.unpack_from(en + 'IIII', record, 40)
        start = header + style_size + extra1 + extra2
        if style_size % 58 or not style_size or start + count > len(record):
            raise ValueError('Invalid legacy text bounds')
        text = record[start:start + count].decode('cp1252', errors='replace')
        text = ''.join(c if ord(c) >= 32 or c in '\r\n\t' else '\ufffd' for c in text).rstrip('\0')
        if not text:
            return
        self.texts.append(text)
        styles = []
        for offset in range(header, header + style_size, 58):
            run = record[offset:offset + 58]
            family = run[20:52].split(b'\0')[0].decode('cp1252', errors='replace')
            family = {'Helv': 'Arial', 'Helvetica': 'Arial', 'Tms Rmn': 'Times New Roman'}.get(family, family)
            size = abs(struct.unpack_from(en+'h', run, 12)[0])
            attrs = word(run, 14, en)
            if not 1 <= size <= 512 or not family or any(ord(c) < 32 for c in family):
                raise ValueError('Invalid legacy text font')
            styles.append((word(run, 0, en), {'family': family, 'size': size,
                'attributes': attrs, 'color': '#' + run[8:11].hex(),
                'ascent': word(run, 54, en), 'descent': word(run, 56, en)}))
        left, top, right, bottom = rectangle(record, 6, en)
        x = struct.unpack_from(en+'h', record, 26)[0]
        y = top
        line = None
        # Browser-independent wrapping uses installed font advances when Pillow
        # and fontconfig are available. Original OS font metrics may differ.
        self.warning('Legacy text wrapping uses substituted font metrics')
        for match in re.finditer(r'\r\n|\r|\n|[^\S\r\n]+|[^\s]+', text):
            part = match.group()
            applicable = [item for item in styles if item[0] <= match.start()]
            style = (applicable[-1] if applicable else styles[0])[1]
            size = style['size']
            advance = text_advance(part, style['family'], size, style['attributes'])
            if line is None or part in ('\r', '\n', '\r\n') or (x + advance > right-5 and x > left+5):
                x = left + 5
                y += max(size, style['ascent'] + style['descent'])
                line = self.shape('text', x=x, y=y-style['descent'])
                line.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
                if part in ('\r', '\n', '\r\n'):
                    continue
            attrs = {'font_family': style['family'], 'font_size': size, 'fill': style['color']}
            if style['attributes'] & 1:
                attrs['font_weight'] = 'bold'
            if style['attributes'] & 2:
                attrs['font_style'] = 'italic'
            if style['attributes'] & 4:
                attrs['text_decoration'] = 'underline'
            svg_element(line, 'tspan', **attrs).text = part
            x += advance

    def image(self, tag, record):
        en, api = self.endian, self.api
        source = None
        index = None
        palette = self.palette
        if tag == 0x60:
            if len(record) < 30:
                raise ValueError('Short bitmap-reference record')
            entry_id = longword(record, 10, en)
            index, content = self.context.reference(entry_id)
            source, dest = rectangle(record, 14, en), rectangle(record, 22, en)
        elif tag == 0x65:
            if len(record) < 98:
                raise ValueError('Short embedded-bitmap record')
            source, dest = rectangle(record, 10, en), rectangle(record, 18, en)
            # A bitmap record can contain both a monochrome preview and the
            # full-color pixels. Select within THIS record, not the whole PIG.
            wrapper = self.pig[:42]
            if palette:
                wrapper += struct.pack(en+'HII', 0x56, 10+len(palette), len(palette)//4) + palette
            content = api.find_best_dib_in_pig(wrapper + record)
            if content is None:
                raise ValueError('Embedded bitmap could not be decoded')
            palette = None  # the normalized result now includes its palette
        else:
            if len(record) < 86:
                raise ValueError('Short imported-image record')
            dest = rectangle(record, 6, en)
            flags = word(record, 82, en)
            if flags == 1:
                raise ValueError('Imported media is a link/handle without embedded pixels')
            if flags == 2 and len(record) >= 368:
                index, content = self.context.reference(word(record, len(record)-4, en))
            else:
                # The inline variant stores the original payload with a size
                # at +368. The preceding bytes are preview/handle metadata.
                content = b''
                if flags == 6 and len(record) >= 372:
                    size = longword(record, 368, en)
                    if size <= len(record)-372:
                        content = record[372:372+size]
                if not content:
                    found = api.find_embedded_image_in_pig(record)
                    if not found:
                        raise ValueError('Imported image encoding is not supported for SVG')
                    _, content = found
        self.context.record_dib_palette(index, palette)
        left, top, right, bottom = dest
        if right <= left or bottom <= top:
            raise ValueError('Invalid image destination rectangle')
        width, height = right-left, bottom-top
        kind = None
        if content[:2] == b'BM':
            content = content[14:]
        if api.dib_fields(content):
            content, iw, ih = dib_png(api, content, palette)
            kind = 'png'
        else:
            found = api.find_embedded_image_in_pig(content)
            if found is None:
                # Only image formats relevant to this record are passed to
                # Pillow. Never invoke external media applications or Xtras.
                if content[:4] not in (b'II*\0', b'MM\0*', b'8BPS') and b'kMoaCfFormat_TGA\0' not in record:
                    raise ValueError('Referenced image encoding is not supported for SVG')
                try:
                    import io
                    from PIL import Image
                    with Image.open(io.BytesIO(content)) as bitmap:
                        if bitmap.width * bitmap.height > 40_000_000:
                            raise ValueError('Imported bitmap exceeds the pixel limit')
                        iw, ih = bitmap.size
                        output = io.BytesIO()
                        bitmap.convert('RGBA').save(output, 'PNG')
                        content, kind = output.getvalue(), 'png'
                except ImportError:
                    raise ValueError('Pillow is required for this imported bitmap format') from None
                except OSError as exc:
                    raise ValueError(f'Imported bitmap decoding failed: {exc}') from None
            else:
                kind, content = found
                iw, ih = (source[2]-source[0], source[3]-source[1]) if source else (width, height)
        container = self.root
        if source and source != (0, 0, iw, ih):
            sx, sy, sr, sb = source
            if sr <= sx or sb <= sy:
                raise ValueError('Invalid bitmap source rectangle')
            container = svg_element(self.root, 'svg', x=left, y=top, width=width, height=height,
                                    viewBox=f'{sx} {sy} {sr-sx} {sb-sy}', preserveAspectRatio='none', overflow='hidden')
            left, top, width, height = 0, 0, iw, ih
        node = svg_element(container, 'image', x=left, y=top, width=width, height=height,
                           preserveAspectRatio='none')
        node.set('href', 'data:image/' + kind + ';base64,' + base64.b64encode(content).decode('ascii'))
        # SVG 1.1 renderers (including some desktop viewers) require xlink.
        node.set('{http://www.w3.org/1999/xlink}href', node.get('href'))
        self.drawn += 1
        if index is not None and self.context.entries[index]['icon_type'] == 0x35:
            self.rendered_dibs.add(index)

    def operation(self, tag, record):
        s, en = self.state, self.endian
        if tag in (1, 2):
            s['fill'] = tag == 1
        elif tag in (0x21, 0x22):
            s['frame'] = tag == 0x21
        elif tag in (6, 0x0E, 0x26, 0x2E):
            s[{6: 'fill_color', 0x0E: 'fill_back', 0x26: 'pen_color', 0x2E: 'pen_back'}[tag]] = '#' + record[2:5].hex()
        elif tag in (0x0A, 0x2A):
            s['fill_pattern' if tag == 0x0A else 'pen_pattern'] = record[2:10]
        elif tag == 0x23:
            x, y = point(record, 2, en)
            s['width'] = max(1, abs(x))
            if x != y:
                self.warning('Anisotropic pen width approximated with horizontal width')
        elif tag in (0x40, 0x42):
            self.groups.append((tag, s.copy()))
            if tag == 0x42:
                s['frame'] = True
        elif tag in (0x41, 0x43):
            expected = 0x40 if tag == 0x41 else 0x42
            if self.groups and self.groups[-1][0] == expected:
                _, previous = self.groups.pop()
                self.state = previous
            elif tag == 0x43:
                s['frame'] = False
        elif tag == 0x48:
            # The unused high byte contains heap residue in some files.
            s['arrows'] = record[2] & 3
        elif tag == 0x49:
            s['arrows'] = 0
        elif tag == 0x50:
            s['mode'] = record[2]
            if s['mode'] not in (0, 1, 2, 3, 4, 7):
                self.warning(f'Unknown transfer mode {s["mode"]}')
        elif tag == 0x51:
            self.warning(f'Drawing-state operation 0x0051 value {word(record, 2, en)} is not decoded')
        elif tag == 0x54:
            pass  # Color-index ramp; RGB values come from the actual palette.
        elif tag == 0x56:
            count = longword(record, 6, en)
            if not 1 <= count <= 256 or len(record) != 10 + 4*count:
                raise ValueError('Invalid palette record')
            self.palette = record[10:]
        elif tag == 0x75:
            x1, y1, x2, y2 = rectangle(record, 2, en)
            self.shape('line', x1=x1, y1=y1, x2=x2, y2=y2, **self.attrs(True))
            self.arrows(x1, y1, x2, y2)
        elif tag in (0x71, 0x7D, 0x81):
            left, top, right, bottom = rectangle(record, 2, en)
            if right < left or bottom < top:
                raise ValueError('Inverted shape bounds')
            attrs = self.attrs()
            if tag == 0x7D:
                self.shape('ellipse', cx=(left+right)/2, cy=(top+bottom)/2,
                           rx=(right-left)/2, ry=(bottom-top)/2, **attrs)
            else:
                if tag == 0x81:
                    rx, ry = point(record, 10, en)
                    attrs.update(rx=abs(rx)/2, ry=abs(ry)/2)
                self.shape('rect', x=left, y=top, width=right-left, height=bottom-top, **attrs)
        elif tag == 0x89:
            left, top, right, bottom = rectangle(record, 2, en)
            ax, ay, bx, by = rectangle(record, 10, en)
            rx, ry = (right-left)/2, (bottom-top)/2
            if rx <= 0 or ry <= 0:
                raise ValueError('Invalid arc bounds')
            cx, cy = (left+right)/2, (top+bottom)/2
            a, b = math.atan2((ay-cy)/ry, (ax-cx)/rx), math.atan2((by-cy)/ry, (bx-cx)/rx)
            x1, y1 = cx+rx*math.cos(a), cy+ry*math.sin(a)
            x2, y2 = cx+rx*math.cos(b), cy+ry*math.sin(b)
            large = int((a-b) % (2*math.pi) > math.pi)
            self.shape('path', d=f'M{x1} {y1}A{rx} {ry} 0 {large} 0 {x2} {y2}', **self.attrs(True))
        elif tag == 0x8D:
            if len(record) < 16:
                raise ValueError('Short polygon record')
            count = word(record, 14, en)
            if len(record) != 16 + count*4:
                raise ValueError('Invalid polygon point count')
            points = [point(record, offset, en) for offset in range(16, len(record), 4)]
            self.shape('polygon', points=' '.join(f'{x},{y}' for x,y in points), **self.attrs())
        elif tag == 0x98:
            self.text(record)
        elif tag in (0x60, 0x65, 0x9A):
            self.image(tag, record)

    def render(self):
        rendered_image_records = []
        for tag, offset, record in self.parsed['records']:
            try:
                self.operation(tag, record)
                if tag in (0x60, 0x65, 0x9A):
                    rendered_image_records.append({'operation': f'0x{tag:04X}',
                                                   'offset': offset, 'length': len(record)})
            except (ValueError, struct.error, IndexError, OverflowError) as exc:
                self.warning(f'{OP_NAMES[tag]} at byte {offset}: {exc}')
        if self.missing_styles:
            self.warning('Unresolved text styles: ' + ', '.join(map(str, sorted(self.missing_styles))))
        if self.texts:
            self.notes.append('Uses installed fonts; unavailable original fonts are substituted by the viewer')
        result = {'bounds': list(self.bounds), 'platform': self.parsed['platform'],
                  'operations': dict(Counter(f'0x{tag:04X}' for tag, _, _ in self.parsed['records'])),
                  'record_count': len(self.parsed['records']), 'drawn_objects': self.drawn,
                  'rendered_dibs': sorted(self.rendered_dibs),
                  'rendered_image_records': rendered_image_records,
                  'warnings': self.warnings, 'notes': self.notes, 'text': '\n'.join(self.texts),
                  'status': 'partial' if self.warnings else 'converted',
                  'padding_bytes': self.parsed.get('padding_bytes', 0)}
        if not self.drawn:
            result['status'] = 'unrendered'
            result['svg'] = None
        else:
            svg_element(self.root, 'title').text = 'Authorware PIG picture'
            svg_element(self.root, 'metadata').text = json.dumps(result, ensure_ascii=False)
            result['svg'] = ET.tostring(self.root, encoding='utf-8', xml_declaration=True)
        return result


def render_pig(data, context):
    parsed = parse_pig(data)
    bounds = parsed['bounds']
    if not bounds or not (0 < bounds[2]-bounds[0] <= 32768 and 0 < bounds[3]-bounds[1] <= 32768):
        return {'status': 'unrendered', 'svg': None, 'warnings': parsed['warnings'] + ['Invalid picture bounds'],
                'text': '', 'operations': {}, 'drawn_objects': 0, 'record_count': len(parsed['records'])}
    return Renderer(context, data, parsed).render()

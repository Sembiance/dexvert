#!/usr/bin/env python3
# Vibe coded by Claude

"""IRIS Showcase (.sc/.showcase/.shw/.sho) to PDF converter."""

import struct
import sys
import math
import io
import cairo
from PIL import Image

MAGIC = b'SCFM'
PAGE_SEPARATOR = b'\x00\x09\x05\x54'
END_MARKER = 0xFFFFFFFF

TOKEN_PATTERN = 0
TOKEN_PARAGRAPH_STYLE = 2
TOKEN_DEFAULT_TAB = 3
TOKEN_MAX_PAGE_SIZE = 4
TOKEN_ARROW_SIZE = 5
TOKEN_SLIDE_SHOW_SCRIPT = 6
TOKEN_TEMPLATE_NAME = 7
TOKEN_CIRCLE = 8
TOKEN_OLD_ARC = 9
TOKEN_RECTANGLE = 10
TOKEN_OLD_TEXT_BLOCK = 11
TOKEN_3D_VIEWER = 12
TOKEN_POLYGON = 13
TOKEN_OLD_GROUP = 14
TOKEN_ROUNDED_RECT = 15
TOKEN_NEW_PAGE = 16
TOKEN_IMAGE = 17
TOKEN_TEXT_BLOCK = 18
TOKEN_ARC = 19
TOKEN_NOTE_PAGE = 20
TOKEN_TAB_COUNT = 21
TOKEN_TOKEN_TABLE = 22
TOKEN_CURRENT_ITEM_NUM = 23
TOKEN_AUDIO_CLIP = 24
TOKEN_OLD_TEMPLATES = 25
TOKEN_ENCAPSULATED_PS = 26
TOKEN_CURRENT_PAGE_NUM = 27
TOKEN_TEMPLATES = 28
TOKEN_VERSION_STRING = 29
TOKEN_PAGE_IMAGE = 30
TOKEN_BACK_POINTER = 31
TOKEN_FONT_NAME = 32
TOKEN_INVENTOR_3D = 33
TOKEN_LIVE_VIDEO = 34
TOKEN_JAPANESE_TEXT = 35
TOKEN_VERSION_CODE = 36
TOKEN_GROUP = 37
TOKEN_STARTING_SCRIPT = 38
TOKEN_ENDING_SCRIPT = 39
TOKEN_I18N_TEXT_BLOCK = 40
TOKEN_PAGE_TABLE = 41
TOKEN_LINKED_TEXT_TABLE = 42
TOKEN_ITEM_ID_TABLE = 43


def ri(d, o):
    return struct.unpack('>I', d[o:o + 4])[0]


def rh(d, o):
    return struct.unpack('>H', d[o:o + 2])[0]


def rf(d, o):
    return struct.unpack('>f', d[o:o + 4])[0]


def decode_color(raw):
    r = (raw >> 16) & 0xFF
    g = (raw >> 8) & 0xFF
    b = raw & 0xFF
    return (r / 255.0, g / 255.0, b / 255.0)


class Record:
    __slots__ = ('token_id', 'token_name', 'offset', 'length', 'data')

    def __init__(self, token_id, token_name, offset, length, data):
        self.token_id = token_id
        self.token_name = token_name
        self.offset = offset
        self.length = length
        self.data = data


class ObjectHeader:
    __slots__ = ('line_color_raw', 'fill_color_raw', 'item_num', 'flags0',
                 'flags1', 'x1', 'y1', 'x2', 'y2', 'x3', 'y3',
                 'line_byte0', 'line_byte1', 'line_byte2', 'line_byte3',
                 'flags2', 'line_style_raw', 'line_width', 'extra_float')

    def __init__(self, data):
        self.line_color_raw = ri(data, 0x00)
        self.fill_color_raw = ri(data, 0x04)
        self.item_num = ri(data, 0x08)
        self.flags0 = ri(data, 0x0C)
        self.flags1 = ri(data, 0x10)
        self.x1 = rf(data, 0x14)
        self.y1 = rf(data, 0x18)
        self.x2 = rf(data, 0x1C)
        self.y2 = rf(data, 0x20)
        self.x3 = rf(data, 0x24)
        self.y3 = rf(data, 0x28)
        self.line_byte0 = data[0x2C]
        self.line_byte1 = data[0x2D]
        self.line_byte2 = data[0x2E]
        self.line_byte3 = data[0x2F]
        self.flags2 = ri(data, 0x30)
        self.line_style_raw = ri(data, 0x34)
        self.line_width = rf(data, 0x38)
        self.extra_float = rf(data, 0x3C)

    @property
    def fill_color(self):
        return decode_color(self.fill_color_raw)

    @property
    def line_color(self):
        return decode_color(self.line_color_raw)

    @property
    def has_fill(self):
        return self.fill_color_raw != 0

    @property
    def has_stroke(self):
        b = self.line_byte0
        return b in (4, 6) and self.line_width > 0

    @property
    def stroke_width(self):
        w = self.line_width
        if w <= 0:
            w = 1.0
        return w

    def bbox(self):
        xs = [self.x1, self.x2, self.x3]
        ys = [self.y1, self.y2, self.y3]
        x4 = self.x2 + (self.x3 - self.x1)
        y4 = self.y2 + (self.y3 - self.y1)
        xs.append(x4)
        ys.append(y4)
        return min(xs), min(ys), max(xs), max(ys)


class Page:
    __slots__ = ('width', 'height', 'page_num', 'objects', 'raw_data')

    def __init__(self):
        self.width = 612
        self.height = 792
        self.page_num = 0
        self.objects = []
        self.raw_data = None


class SCFMDocument:
    def __init__(self):
        self.version = (0, 0)
        self.tokens = {}
        self.version_string = ""
        self.page_width = 612
        self.page_height = 792
        self.pages = []
        self.fonts = []
        self.paragraph_styles = []


def parse_token_table(data):
    tok_table_size = ri(data, 12)
    pos = 16
    tokens = {}
    entry_count = tok_table_size // 24
    for _ in range(entry_count):
        if pos + 24 > len(data):
            break
        tok_id = ri(data, pos)
        name = data[pos + 4:pos + 24].decode('ascii', errors='replace').rstrip(' \x00')
        tokens[tok_id] = name
        pos += 24
    return tokens, 16 + tok_table_size


def parse_records(data, tokens, start, end):
    pos = start
    records = []
    while pos + 4 <= end:
        if data[pos:pos + 4] == PAGE_SEPARATOR:
            pos += 4
            continue
        tok_id = ri(data, pos)
        if tok_id >= 0xFFFFFFF0:
            break
        if pos + 8 > end:
            break
        length = ri(data, pos + 4)
        if length > end - pos - 8:
            break
        tok_name = tokens.get(tok_id, f"unknown_{tok_id}")
        rec_data = data[pos + 8:pos + 8 + length]
        records.append(Record(tok_id, tok_name, pos, length, rec_data))
        pos += 8 + length
    return records


def parse_group_children(data, tokens, group_data):
    return parse_records(data, tokens, 0, len(group_data))


def parse_font_name(rec_data):
    if len(rec_data) < 8:
        return None, None, None
    font_idx = ri(rec_data, 0)
    name_len = ri(rec_data, 4)
    if 8 + name_len > len(rec_data):
        name_len = min(name_len, len(rec_data) - 8)
    name = rec_data[8:8 + name_len].decode('ascii', errors='replace').rstrip('\x00')
    fallback_start = 8 + name_len
    fallback = ""
    if fallback_start + 4 <= len(rec_data):
        fb_len = ri(rec_data, fallback_start)
        fb_start = fallback_start + 4
        if fb_start + fb_len <= len(rec_data):
            fallback = rec_data[fb_start:fb_start + fb_len].decode('ascii', errors='replace').rstrip('\x00')
    return font_idx, name, fallback


def extract_text_content(text_data, header_size=0x90):
    if len(text_data) <= header_size:
        return ""
    stream = text_data[header_size:]
    result = []
    i = 0
    while i < len(stream):
        b = stream[i]
        if b == 0xFF:
            if i + 3 < len(stream) and stream[i + 1] == 0x01:
                cmd = stream[i + 2]
                cmd_len = stream[i + 3] if i + 3 < len(stream) else 0
                if cmd == 0x05:
                    result.append('\n')
                i += 4 + cmd_len
                continue
            i += 1
        elif b == 0x00:
            i += 1
        elif b == 0x09:
            result.append('    ')
            i += 1
        elif 0x20 <= b <= 0x7E or b == 0x0A or b == 0x0D or b >= 0x80:
            if b == 0x0D:
                result.append('\n')
            elif b == 0x0A:
                result.append('\n')
            elif b >= 0x80:
                result.append('?')
            else:
                result.append(chr(b))
            i += 1
        else:
            i += 1
    return ''.join(result)


def extract_text_with_formatting(text_data, header_size=0x90):
    if len(text_data) <= header_size:
        return []
    stream = text_data[header_size:]
    segments = []
    current_text = []
    current_font = 0
    current_size = 12.0
    current_color = (0, 0, 0)
    i = 0
    while i < len(stream):
        b = stream[i]
        if b == 0xFF:
            if i + 3 < len(stream) and stream[i + 1] == 0x01:
                if current_text:
                    segments.append({
                        'text': ''.join(current_text),
                        'font': current_font,
                        'size': current_size,
                        'color': current_color
                    })
                    current_text = []
                cmd = stream[i + 2]
                if i + 3 >= len(stream):
                    break
                cmd_len = stream[i + 3]
                cmd_data = stream[i + 4:i + 4 + cmd_len]
                if cmd == 0x01 and cmd_len >= 1:
                    current_font = cmd_data[0] if len(cmd_data) > 0 else 0
                elif cmd == 0x06 and cmd_len >= 12:
                    if len(cmd_data) >= 12:
                        r_f = struct.unpack('<f', cmd_data[0:4])[0]
                        g_f = struct.unpack('<f', cmd_data[4:8])[0]
                        b_f = struct.unpack('<f', cmd_data[8:12])[0]
                        current_color = (
                            max(0, min(1, r_f)),
                            max(0, min(1, g_f)),
                            max(0, min(1, b_f))
                        )
                elif cmd == 0x0D and cmd_len >= 1:
                    current_font = cmd_data[0] if len(cmd_data) > 0 else current_font
                elif cmd == 0x05:
                    current_text.append('\n')
                i += 4 + cmd_len
                continue
            i += 1
        elif b == 0x00:
            i += 1
        elif b == 0x09:
            current_text.append('    ')
            i += 1
        elif 0x20 <= b <= 0x7E or b == 0x0A or b == 0x0D:
            if b == 0x0D or b == 0x0A:
                current_text.append('\n')
            else:
                current_text.append(chr(b))
            i += 1
        elif b >= 0x80:
            current_text.append('?')
            i += 1
        else:
            i += 1
    if current_text:
        segments.append({
            'text': ''.join(current_text),
            'font': current_font,
            'size': current_size,
            'color': current_color
        })
    return segments


def decode_sgi_image(sgi_data):
    if len(sgi_data) < 12 or sgi_data[0:2] != b'\x01\xda':
        return None
    storage = sgi_data[2]
    bpc = sgi_data[3]
    dimension = rh(sgi_data, 4)
    xsize = rh(sgi_data, 6)
    ysize = rh(sgi_data, 8)
    zsize = rh(sgi_data, 10)
    if xsize == 0 or ysize == 0 or xsize > 8192 or ysize > 8192:
        return None
    channels = min(zsize, 4)
    if storage == 0:
        pixel_start = 512
        if pixel_start + xsize * ysize * channels > len(sgi_data):
            return None
        img = Image.new('RGBA', (xsize, ysize), (255, 255, 255, 255))
        pixels = img.load()
        for c in range(channels):
            for row in range(ysize):
                y = ysize - 1 - row
                for x in range(xsize):
                    offset = pixel_start + (c * ysize + row) * xsize + x
                    if offset < len(sgi_data):
                        val = sgi_data[offset]
                        p = list(pixels[x, y])
                        if channels == 1:
                            p[0] = p[1] = p[2] = val
                        elif c < 3:
                            p[c] = val
                        elif c == 3:
                            p[3] = val
                        pixels[x, y] = tuple(p)
        return img
    elif storage == 1:
        if 512 + ysize * channels * 8 > len(sgi_data):
            return None
        start_tab = []
        length_tab = []
        tab_entries = ysize * channels
        for i in range(tab_entries):
            start_tab.append(ri(sgi_data, 512 + i * 4))
            length_tab.append(ri(sgi_data, 512 + tab_entries * 4 + i * 4))
        img = Image.new('RGBA', (xsize, ysize), (255, 255, 255, 255))
        pixels = img.load()
        for c in range(channels):
            for row in range(ysize):
                y = ysize - 1 - row
                idx = c * ysize + row
                if idx >= len(start_tab):
                    continue
                offset = start_tab[idx]
                rle_len = length_tab[idx]
                if offset >= len(sgi_data):
                    continue
                x = 0
                pos = offset
                end_pos = min(offset + rle_len, len(sgi_data))
                while pos < end_pos and x < xsize:
                    if bpc == 1:
                        if pos >= len(sgi_data):
                            break
                        pixel_byte = sgi_data[pos]
                        pos += 1
                        count = pixel_byte & 0x7F
                        if count == 0:
                            break
                        if pixel_byte & 0x80:
                            for _ in range(count):
                                if pos < len(sgi_data) and x < xsize:
                                    val = sgi_data[pos]
                                    pos += 1
                                    p = list(pixels[x, y])
                                    if channels == 1:
                                        p[0] = p[1] = p[2] = val
                                    elif c < 3:
                                        p[c] = val
                                    elif c == 3:
                                        p[3] = val
                                    pixels[x, y] = tuple(p)
                                    x += 1
                        else:
                            if pos < len(sgi_data):
                                val = sgi_data[pos]
                                pos += 1
                                for _ in range(count):
                                    if x < xsize:
                                        p = list(pixels[x, y])
                                        if channels == 1:
                                            p[0] = p[1] = p[2] = val
                                        elif c < 3:
                                            p[c] = val
                                        elif c == 3:
                                            p[3] = val
                                        pixels[x, y] = tuple(p)
                                        x += 1
                    else:
                        break
        return img
    return None


def parse_showcase(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    if len(data) < 16 or data[:4] != MAGIC:
        raise ValueError("Not an IRIS Showcase file (missing SCFM magic)")
    bom = rh(data, 6)
    if bom not in (0xFFFE, 0xD8DF):
        raise ValueError(f"Unexpected byte order mark: 0x{bom:04X}")
    doc = SCFMDocument()
    doc.version = (data[4], data[5])
    doc.tokens, data_start = parse_token_table(data)
    if data_start >= len(data):
        return doc
    records = parse_records(data, doc.tokens, data_start, len(data))
    current_page = None
    pages_started = False
    for rec in records:
        if rec.token_id == TOKEN_VERSION_CODE:
            pass
        elif rec.token_id == TOKEN_VERSION_STRING:
            doc.version_string = rec.data.decode('ascii', errors='replace').rstrip('\x00')
        elif rec.token_id == TOKEN_MAX_PAGE_SIZE and rec.length >= 8:
            doc.page_width = ri(rec.data, 0)
            doc.page_height = ri(rec.data, 4)
        elif rec.token_id == TOKEN_FONT_NAME:
            info = parse_font_name(rec.data)
            if info[0] is not None:
                doc.fonts.append(info)
        elif rec.token_id == TOKEN_PARAGRAPH_STYLE:
            doc.paragraph_styles.append(rec.data)
        elif rec.token_id == TOKEN_NEW_PAGE:
            pages_started = True
            page = Page()
            if rec.length >= 4:
                page.width = rh(rec.data, 0)
                page.height = rh(rec.data, 2)
            if page.width == 0:
                page.width = doc.page_width
            if page.height == 0:
                page.height = doc.page_height
            if rec.length >= 16:
                page.page_num = ri(rec.data, 12)
            page.raw_data = rec.data
            if current_page is not None:
                doc.pages.append(current_page)
            current_page = page
        elif rec.token_id == TOKEN_NOTE_PAGE:
            pages_started = True
            page = Page()
            if rec.length >= 4:
                page.width = rh(rec.data, 0)
                page.height = rh(rec.data, 2)
            if page.width == 0:
                page.width = doc.page_width
            if page.height == 0:
                page.height = doc.page_height
            page.raw_data = rec.data
            if current_page is not None:
                doc.pages.append(current_page)
            current_page = page
        elif pages_started and current_page is not None:
            if rec.token_id in (TOKEN_RECTANGLE, TOKEN_CIRCLE, TOKEN_POLYGON,
                                TOKEN_ARC, TOKEN_OLD_ARC, TOKEN_ROUNDED_RECT,
                                TOKEN_TEXT_BLOCK, TOKEN_I18N_TEXT_BLOCK,
                                TOKEN_OLD_TEXT_BLOCK, TOKEN_JAPANESE_TEXT,
                                TOKEN_IMAGE, TOKEN_GROUP, TOKEN_OLD_GROUP,
                                TOKEN_ENCAPSULATED_PS, TOKEN_PAGE_IMAGE):
                current_page.objects.append(rec)
        elif rec.token_id in (TOKEN_PAGE_TABLE, TOKEN_BACK_POINTER,
                              TOKEN_LINKED_TEXT_TABLE, TOKEN_ITEM_ID_TABLE):
            pass
    if current_page is not None:
        doc.pages.append(current_page)
    return doc


def render_object(ctx, rec, doc, page):
    if rec.length < 0x40:
        return
    hdr = ObjectHeader(rec.data)
    tid = rec.token_id
    if tid == TOKEN_RECTANGLE:
        render_rect(ctx, hdr, rec.data, page)
    elif tid == TOKEN_CIRCLE:
        render_circle(ctx, hdr, rec.data, page)
    elif tid == TOKEN_POLYGON:
        render_polygon(ctx, hdr, rec.data, page)
    elif tid in (TOKEN_ARC, TOKEN_OLD_ARC):
        render_arc(ctx, hdr, rec.data, page)
    elif tid == TOKEN_ROUNDED_RECT:
        render_rounded_rect(ctx, hdr, rec.data, page)
    elif tid in (TOKEN_TEXT_BLOCK, TOKEN_I18N_TEXT_BLOCK,
                 TOKEN_OLD_TEXT_BLOCK, TOKEN_JAPANESE_TEXT):
        render_text_block(ctx, hdr, rec.data, doc, page)
    elif tid == TOKEN_IMAGE:
        render_image(ctx, hdr, rec.data, page)
    elif tid in (TOKEN_GROUP, TOKEN_OLD_GROUP):
        render_group(ctx, hdr, rec.data, doc, page)
    elif tid == TOKEN_ENCAPSULATED_PS:
        render_eps_placeholder(ctx, hdr, page)
    elif tid == TOKEN_PAGE_IMAGE:
        pass


def apply_fill_and_stroke(ctx, hdr):
    if hdr.has_fill:
        r, g, b = hdr.fill_color
        ctx.set_source_rgb(r, g, b)
        if hdr.has_stroke:
            ctx.fill_preserve()
        else:
            ctx.fill()
    if hdr.has_stroke:
        lr, lg, lb = hdr.line_color
        ctx.set_source_rgb(lr, lg, lb)
        ctx.set_line_width(hdr.stroke_width)
        ctx.stroke()
    elif not hdr.has_fill:
        ctx.set_source_rgb(0, 0, 0)
        ctx.set_line_width(max(hdr.stroke_width, 1.0))
        ctx.stroke()
    else:
        ctx.new_path()


def flip_y(y, page_height):
    return page_height - y


def render_rect(ctx, hdr, data, page):
    ph = page.height
    x1, y1 = hdr.x1, flip_y(hdr.y1, ph)
    x2, y2 = hdr.x2, flip_y(hdr.y2, ph)
    x3, y3 = hdr.x3, flip_y(hdr.y3, ph)
    x4 = x2 + (x3 - x1)
    y4 = y2 + (y3 - y1)
    ctx.move_to(x1, y1)
    ctx.line_to(x2, y2)
    ctx.line_to(x4, y4)
    ctx.line_to(x3, y3)
    ctx.close_path()
    apply_fill_and_stroke(ctx, hdr)


def render_circle(ctx, hdr, data, page):
    ph = page.height
    x1, y1 = hdr.x1, flip_y(hdr.y1, ph)
    x2, y2 = hdr.x2, flip_y(hdr.y2, ph)
    x3, y3 = hdr.x3, flip_y(hdr.y3, ph)
    cx = (x1 + x2 + x3 + (x2 + x3 - x1)) / 4.0
    cy = (y1 + y2 + y3 + (y2 + y3 - y1)) / 4.0
    rx = math.sqrt((x3 - x1) ** 2 + (y3 - y1) ** 2) / 2.0
    ry = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) / 2.0
    if rx < 0.1 or ry < 0.1:
        return
    ctx.save()
    ctx.translate(cx, cy)
    angle = math.atan2(y3 - y1, x3 - x1)
    ctx.rotate(angle)
    ctx.scale(rx, ry)
    ctx.arc(0, 0, 1.0, 0, 2 * math.pi)
    ctx.restore()
    apply_fill_and_stroke(ctx, hdr)


def extract_polygon_vertices(data, vertex_count, page_height):
    ph = page_height
    min_x, min_y, max_x, max_y = 1e9, 1e9, -1e9, -1e9
    for off in (0x14, 0x1C, 0x24):
        if off + 8 <= len(data):
            bx = rf(data, off)
            by = rf(data, off + 4)
            min_x = min(min_x, bx)
            min_y = min(min_y, by)
            max_x = max(max_x, bx)
            max_y = max(max_y, by)
    x4 = rf(data, 0x1C) + rf(data, 0x24) - rf(data, 0x14)
    y4 = rf(data, 0x20) + rf(data, 0x28) - rf(data, 0x18)
    min_x = min(min_x, x4)
    min_y = min(min_y, y4)
    max_x = max(max_x, x4)
    max_y = max(max_y, y4)
    margin = max(max_x - min_x, max_y - min_y) * 0.15 + 10
    def is_valid_coord(x, y):
        return (min_x - margin <= x <= max_x + margin and
                min_y - margin <= y <= max_y + margin and
                x == x and y == y and abs(x) > 0.1 and abs(y) > 0.1)
    if len(data) < 0x54:
        return []
    v0x = rf(data, 0x4C)
    v0y = rf(data, 0x50)
    vertices = [(v0x, flip_y(v0y, ph))]
    v0_off = 0x4C
    stride = 0
    for scan in range(v0_off + 8, min(v0_off + 200, len(data) - 4), 4):
        cx = rf(data, scan)
        cy = rf(data, scan + 4)
        if is_valid_coord(cx, cy) and (abs(cx - v0x) > 0.01 or abs(cy - v0y) > 0.01):
            stride = scan - v0_off
            vertices.append((cx, flip_y(cy, ph)))
            break
    if stride < 8:
        return vertices
    for i in range(2, vertex_count):
        off = v0_off + stride * i
        if off + 8 > len(data):
            break
        cx = rf(data, off)
        cy = rf(data, off + 4)
        if is_valid_coord(cx, cy):
            vertices.append((cx, flip_y(cy, ph)))
        else:
            for try_off in (off - 4, off + 4, off - 8, off + 8):
                if 0x48 <= try_off and try_off + 8 <= len(data):
                    cx = rf(data, try_off)
                    cy = rf(data, try_off + 4)
                    if is_valid_coord(cx, cy):
                        vertices.append((cx, flip_y(cy, ph)))
                        break
    return vertices


def render_polygon(ctx, hdr, data, page):
    ph = page.height
    if len(data) < 0x44:
        return
    vertex_count = ri(data, 0x40) if len(data) >= 0x44 else 0
    if vertex_count > 10000:
        return
    if vertex_count < 2:
        vertex_count = 0
    vertices = []
    if vertex_count >= 2 and len(data) >= 0x54:
        vertices = extract_polygon_vertices(data, vertex_count, ph)
    if len(vertices) < 2:
        x1, y1 = hdr.x1, flip_y(hdr.y1, ph)
        x2, y2 = hdr.x2, flip_y(hdr.y2, ph)
        x3, y3 = hdr.x3, flip_y(hdr.y3, ph)
        fh_check = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        if fh_check < 2.0:
            if vertex_count <= 3:
                if abs(x1 - x2) < 0.01 and abs(y1 - y2) < 0.01:
                    vertices = [(x1, y1), (x3, y3)]
                else:
                    vertices = [(x1, y1), (x2, y2)]
            else:
                return
        else:
            x4 = x2 + (x3 - x1)
            y4 = y2 + (y3 - y1)
            vertices = [(x1, y1), (x2, y2), (x4, y4), (x3, y3)]
    if len(vertices) < 2:
        return
    ctx.move_to(vertices[0][0], vertices[0][1])
    for vx_pt, vy_pt in vertices[1:]:
        ctx.line_to(vx_pt, vy_pt)
    if len(vertices) > 2:
        ctx.close_path()
    apply_fill_and_stroke(ctx, hdr)


def render_arc(ctx, hdr, data, page):
    ph = page.height
    x1, y1 = hdr.x1, flip_y(hdr.y1, ph)
    x2, y2 = hdr.x2, flip_y(hdr.y2, ph)
    x3, y3 = hdr.x3, flip_y(hdr.y3, ph)
    cx = (x1 + x2 + x3) / 3.0
    cy = (y1 + y2 + y3) / 3.0
    r = max(
        math.sqrt((x1 - cx) ** 2 + (y1 - cy) ** 2),
        math.sqrt((x2 - cx) ** 2 + (y2 - cy) ** 2),
        math.sqrt((x3 - cx) ** 2 + (y3 - cy) ** 2)
    )
    if r < 0.1:
        return
    if len(data) >= 0x88:
        start_angle = rf(data, 0x80)
        end_angle = rf(data, 0x84)
    else:
        start_angle = 0
        end_angle = 2 * math.pi
    ctx.arc(cx, cy, r, start_angle, end_angle)
    if hdr.has_fill:
        r_c, g_c, b_c = hdr.fill_color
        ctx.set_source_rgb(r_c, g_c, b_c)
        ctx.fill_preserve()
    lr, lg, lb = hdr.line_color
    if hdr.has_stroke or not hdr.has_fill:
        ctx.set_source_rgb(lr, lg, lb)
        ctx.set_line_width(hdr.stroke_width)
        ctx.stroke()
    else:
        ctx.new_path()


def render_rounded_rect(ctx, hdr, data, page):
    ph = page.height
    min_x, min_y, max_x, max_y = hdr.bbox()
    min_y_f = flip_y(max_y, ph)
    max_y_f = flip_y(min_y, ph)
    w = max_x - min_x
    h = max_y_f - min_y_f
    if w <= 0 or h <= 0:
        return
    corner_r = min(w, h) * 0.15
    if len(data) >= 0x84:
        cr_val = rf(data, 0x80)
        if 0 < cr_val < min(w, h) / 2:
            corner_r = cr_val
    x, y = min_x, min_y_f
    ctx.move_to(x + corner_r, y)
    ctx.line_to(x + w - corner_r, y)
    ctx.arc(x + w - corner_r, y + corner_r, corner_r, -math.pi / 2, 0)
    ctx.line_to(x + w, y + h - corner_r)
    ctx.arc(x + w - corner_r, y + h - corner_r, corner_r, 0, math.pi / 2)
    ctx.line_to(x + corner_r, y + h)
    ctx.arc(x + corner_r, y + h - corner_r, corner_r, math.pi / 2, math.pi)
    ctx.line_to(x, y + corner_r)
    ctx.arc(x + corner_r, y + corner_r, corner_r, math.pi, 3 * math.pi / 2)
    ctx.close_path()
    apply_fill_and_stroke(ctx, hdr)


def wrap_text_lines(ctx, text, max_width):
    words = text.split(' ')
    lines = []
    current = []
    for word in words:
        if not word:
            continue
        test = ' '.join(current + [word])
        ext = ctx.text_extents(test)
        if ext.width > max_width and current:
            lines.append(' '.join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(' '.join(current))
    return lines


def compute_auto_font_size(ctx, all_lines, frame_w, frame_h):
    while all_lines and not all_lines[-1].strip():
        all_lines = all_lines[:-1]
    if not all_lines:
        return 12.0
    margin = 4.0
    usable_w = frame_w - margin * 2
    usable_h = frame_h - margin
    if usable_w < 5 or usable_h < 5:
        return max(4.0, min(frame_h * 0.7, frame_w * 0.3))
    max_size = min(72.0, usable_h * 0.9)
    min_size = 4.0
    best_size = min_size
    for trial in range(20):
        sz = (max_size + min_size) / 2.0
        ctx.set_font_size(sz)
        wrapped = []
        for line in all_lines:
            if not line.strip():
                wrapped.append('')
                continue
            wl = wrap_text_lines(ctx, line, usable_w)
            wrapped.extend(wl)
        total_h = len(wrapped) * sz * 1.25
        fits_w = True
        for wl in wrapped:
            if wl:
                ext = ctx.text_extents(wl)
                if ext.width > usable_w:
                    fits_w = False
                    break
        if total_h <= usable_h and fits_w:
            best_size = sz
            min_size = sz
        else:
            max_size = sz
    return max(4.0, best_size)


def render_text_block(ctx, hdr, data, doc, page):
    ph = page.height
    p1x, p1y = hdr.x1, flip_y(hdr.y1, ph)
    p2x, p2y = hdr.x2, flip_y(hdr.y2, ph)
    p3x, p3y = hdr.x3, flip_y(hdr.y3, ph)
    p4x = p2x + (p3x - p1x)
    p4y = p2y + (p3y - p1y)
    edge_w_dx = p3x - p1x
    edge_w_dy = p3y - p1y
    edge_h_dx = p2x - p1x
    edge_h_dy = p2y - p1y
    frame_w = math.sqrt(edge_w_dx ** 2 + edge_w_dy ** 2)
    frame_h = math.sqrt(edge_h_dx ** 2 + edge_h_dy ** 2)
    if frame_w < 1 or frame_h < 1:
        return
    raw_angle = math.atan2(edge_w_dy, edge_w_dx)
    raw_deg = math.degrees(raw_angle)
    snap_deg = round(raw_deg / 90.0) * 90.0
    snapped = abs(raw_deg - snap_deg) < 10
    clip_path = [(p1x, p1y), (p2x, p2y), (p4x, p4y), (p3x, p3y)]
    if hdr.has_fill:
        r, g, b = hdr.fill_color
        ctx.set_source_rgb(r, g, b)
        ctx.move_to(*clip_path[0])
        for pt in clip_path[1:]:
            ctx.line_to(*pt)
        ctx.close_path()
        ctx.fill()
    text = extract_text_content(data, 0x90)
    if not text.strip():
        return
    segments = extract_text_with_formatting(data, 0x90)
    seg_colors = [s.get('color', (0, 0, 0)) for s in segments]
    non_black = [c for c in seg_colors if c != (0, 0, 0)]
    if not hdr.has_fill and non_black and all(all(v > 0.95 for v in c) for c in non_black):
        return
    fill_rgb = hdr.fill_color if hdr.has_fill else (1, 1, 1)
    def color_contrast(c):
        return abs(c[0] - fill_rgb[0]) + abs(c[1] - fill_rgb[1]) + abs(c[2] - fill_rgb[2])
    has_colors = False
    text_color = (0, 0, 0)
    best_contrast = color_contrast(text_color)
    for seg in segments:
        c = seg.get('color', (0, 0, 0))
        cc = color_contrast(c)
        if cc > best_contrast:
            best_contrast = cc
            text_color = c
            has_colors = True
    ctx.save()
    ctx.move_to(*clip_path[0])
    for pt in clip_path[1:]:
        ctx.line_to(*pt)
    ctx.close_path()
    ctx.clip()
    wdx = (p3x - p1x) / frame_w if frame_w > 0 else 1
    wdy = (p3y - p1y) / frame_w if frame_w > 0 else 0
    hdx = (p2x - p1x) / frame_h if frame_h > 0 else 0
    hdy = (p2y - p1y) / frame_h if frame_h > 0 else 1
    baseline_angle = math.atan2(wdy, wdx)
    if snapped:
        baseline_angle = math.radians(snap_deg)
    font_slant = cairo.FONT_SLANT_NORMAL
    font_weight = cairo.FONT_WEIGHT_NORMAL
    ctx.select_font_face("sans-serif", font_slant, font_weight)
    all_lines = text.split('\n')
    while all_lines and not all_lines[-1].strip():
        all_lines.pop()
    if not all_lines:
        ctx.restore()
        return
    angle_sin = abs(math.sin(baseline_angle))
    margin = 2.0
    font_size = compute_auto_font_size(ctx, all_lines, frame_w - margin * 2, frame_h - margin)
    ctx.set_font_size(font_size)
    glyph_margin = font_size * 0.85 * angle_sin if angle_sin > 0.05 else 0
    margin = 2.0 + glyph_margin
    font_size = compute_auto_font_size(ctx, all_lines, frame_w - margin * 2, frame_h - margin)
    ctx.set_font_size(font_size)
    usable_w = frame_w - margin * 2
    wrapped_lines = []
    for line in all_lines:
        if not line.strip():
            wrapped_lines.append('')
        else:
            wl = wrap_text_lines(ctx, line, usable_w)
            wrapped_lines.extend(wl)
    line_h = font_size * 1.25
    if has_colors:
        ctx.set_source_rgb(*text_color)
    else:
        ctx.set_source_rgb(0, 0, 0)
    y_pos = margin + font_size
    for wl in wrapped_lines:
        if y_pos > frame_h:
            break
        if wl.strip():
            lx = margin
            ly = y_pos
            gx = p1x + lx * wdx + ly * hdx
            gy = p1y + lx * wdy + ly * hdy
            ctx.save()
            ctx.translate(gx, gy)
            ctx.rotate(baseline_angle)
            ctx.move_to(0, 0)
            try:
                ctx.show_text(wl)
            except:
                pass
            ctx.restore()
        y_pos += line_h
    ctx.restore()


def render_image(ctx, hdr, data, page):
    ph = page.height
    if len(data) < 0x68:
        return
    sgi_offset = 0x64
    if sgi_offset + 2 > len(data):
        return
    if data[sgi_offset:sgi_offset + 2] != b'\x01\xda':
        for off in range(0x40, min(0x200, len(data) - 2)):
            if data[off:off + 2] == b'\x01\xda':
                sgi_offset = off
                break
        else:
            return
    sgi_data = data[sgi_offset:]
    pil_img = decode_sgi_image(sgi_data)
    if pil_img is None:
        return
    min_x, min_y_raw, max_x, max_y_raw = hdr.bbox()
    min_y = flip_y(max_y_raw, ph)
    max_y = flip_y(min_y_raw, ph)
    w = max_x - min_x
    h = max_y - min_y
    if w <= 0 or h <= 0:
        return
    img_w, img_h = pil_img.size
    if pil_img.mode != 'RGBA':
        pil_img = pil_img.convert('RGBA')
    img_data = pil_img.tobytes()
    surface = cairo.ImageSurface.create_for_data(
        bytearray(b'\x00' * img_w * img_h * 4),
        cairo.FORMAT_ARGB32, img_w, img_h
    )
    buf = surface.get_data()
    for i in range(img_w * img_h):
        r_v = img_data[i * 4]
        g_v = img_data[i * 4 + 1]
        b_v = img_data[i * 4 + 2]
        a_v = img_data[i * 4 + 3]
        buf[i * 4 + 0] = b_v
        buf[i * 4 + 1] = g_v
        buf[i * 4 + 2] = r_v
        buf[i * 4 + 3] = a_v
    surface.mark_dirty()
    ctx.save()
    ctx.translate(min_x, min_y)
    ctx.scale(w / img_w, h / img_h)
    ctx.set_source_surface(surface, 0, 0)
    ctx.paint()
    ctx.restore()


def render_group(ctx, hdr, data, doc, page):
    if len(data) < 0x48:
        return
    sub_start = 0x40
    sub_data = data[sub_start:]
    sub_records = parse_records(sub_data, doc.tokens, 0, len(sub_data))
    for sub_rec in sub_records:
        if sub_rec.length >= 0x40:
            render_object(ctx, sub_rec, doc, page)


def render_eps_placeholder(ctx, hdr, page):
    ph = page.height
    min_x, min_y_raw, max_x, max_y_raw = hdr.bbox()
    min_y = flip_y(max_y_raw, ph)
    max_y = flip_y(min_y_raw, ph)
    w = max_x - min_x
    h = max_y - min_y
    if w > 0 and h > 0:
        ctx.set_source_rgb(0.9, 0.9, 0.9)
        ctx.rectangle(min_x, min_y, w, h)
        ctx.fill()
        ctx.set_source_rgb(0.5, 0.5, 0.5)
        ctx.set_line_width(0.5)
        ctx.rectangle(min_x, min_y, w, h)
        ctx.stroke()


def render_to_pdf(doc, output_path):
    if not doc.pages:
        first_page = Page()
        first_page.width = doc.page_width
        first_page.height = doc.page_height
        doc.pages.append(first_page)
    first = doc.pages[0]
    surface = cairo.PDFSurface(output_path, first.width, first.height)
    for page_idx, page in enumerate(doc.pages):
        surface.set_size(page.width, page.height)
        ctx = cairo.Context(surface)
        ctx.set_source_rgb(1, 1, 1)
        ctx.rectangle(0, 0, page.width, page.height)
        ctx.fill()
        for obj in page.objects:
            try:
                render_object(ctx, obj, doc, page)
            except Exception:
                pass
        surface.show_page()
    surface.finish()


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputFile>", file=sys.stderr)
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    try:
        doc = parse_showcase(input_file)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: File not found: {input_file}", file=sys.stderr)
        sys.exit(1)
    except IsADirectoryError:
        print(f"Error: Is a directory: {input_file}", file=sys.stderr)
        sys.exit(1)
    render_to_pdf(doc, output_file)


if __name__ == '__main__':
    main()

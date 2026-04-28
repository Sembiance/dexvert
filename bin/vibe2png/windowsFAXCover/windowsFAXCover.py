#!/usr/bin/env python3
# Vibe coded by Claude

import sys
import os
import struct
import io
import tempfile
import subprocess
from PIL import Image, ImageDraw, ImageFont
import olefile

RENDER_DPI = 150
SCALE = RENDER_DPI / 100.0

CHARSET_TO_CODEPAGE = {
    0: 'cp1252', 1: 'cp1252', 2: 'cp1252',
    77: 'mac_roman', 128: 'cp932', 129: 'cp949',
    130: 'johab', 134: 'cp936', 136: 'cp950',
    161: 'cp1253', 162: 'cp1254', 163: 'cp1258',
    177: 'cp1255', 178: 'cp1256', 186: 'cp1257',
    204: 'cp1251', 222: 'cp874', 238: 'cp1250',
    255: 'cp437',
}

PAPER_SIZES = {
    1: (850, 1100),
    5: (850, 1400),
    8: (1169, 827),
    9: (827, 1169),
}

FONT_MAP = {}

def _build_font_map():
    core = '/usr/share/fonts/corefonts'
    dv = '/usr/share/fonts/dejavu'
    fallback = os.path.join(dv, 'DejaVuSans.ttf')
    families = {
        'arial':          (f'{core}/arial.ttf', f'{core}/arialbd.ttf', f'{core}/ariali.ttf', f'{core}/arialbi.ttf'),
        'arial black':    (f'{core}/ariblk.ttf', f'{core}/ariblk.ttf', f'{core}/ariblk.ttf', f'{core}/ariblk.ttf'),
        'times new roman':(f'{core}/times.ttf', f'{core}/timesbd.ttf', f'{core}/timesi.ttf', f'{core}/timesbi.ttf'),
        'courier new':    (f'{core}/cour.ttf', f'{core}/courbd.ttf', f'{core}/couri.ttf', f'{core}/courbi.ttf'),
        'georgia':        (f'{core}/georgia.ttf', f'{core}/georgiab.ttf', f'{core}/georgiai.ttf', f'{core}/georgiaz.ttf'),
        'verdana':        (f'{core}/verdana.ttf', f'{core}/verdanab.ttf', f'{core}/verdanai.ttf', f'{core}/verdanaz.ttf'),
        'trebuchet ms':   (f'{core}/trebuc.ttf', f'{core}/trebucbd.ttf', f'{core}/trebucit.ttf', f'{core}/trebucbi.ttf'),
        'comic sans ms':  (f'{core}/comic.ttf', f'{core}/comicbd.ttf', f'{core}/comic.ttf', f'{core}/comicbd.ttf'),
        'impact':         (f'{core}/impact.ttf', f'{core}/impact.ttf', f'{core}/impact.ttf', f'{core}/impact.ttf'),
        'tahoma':         (fallback, f'{dv}/DejaVuSans-Bold.ttf', f'{dv}/DejaVuSans-Oblique.ttf', f'{dv}/DejaVuSans-BoldOblique.ttf'),
        'ms sans serif':  (fallback, f'{dv}/DejaVuSans-Bold.ttf', f'{dv}/DejaVuSans-Oblique.ttf', f'{dv}/DejaVuSans-BoldOblique.ttf'),
        'ms serif':       (f'{core}/times.ttf', f'{core}/timesbd.ttf', f'{core}/timesi.ttf', f'{core}/timesbi.ttf'),
        'marlett':        (fallback, fallback, fallback, fallback),
    }
    FONT_MAP['_fallback'] = (fallback, fallback, fallback, fallback)
    for name, paths in families.items():
        resolved = []
        for p in paths:
            resolved.append(p if os.path.exists(p) else fallback)
        FONT_MAP[name] = tuple(resolved)


def get_font(face_name, height_hundredths, weight=400, italic=False):
    if not FONT_MAP:
        _build_font_map()
    pixel_height = max(6, int(abs(height_hundredths) * SCALE))
    key = face_name.lower().strip('\x00')
    family = FONT_MAP.get(key, FONT_MAP['_fallback'])
    idx = (1 if weight >= 600 else 0) + (2 if italic else 0)
    path = family[idx]
    try:
        return ImageFont.truetype(path, pixel_height)
    except Exception:
        return ImageFont.load_default()


def colorref_to_rgb(c):
    return (c & 0xFF, (c >> 8) & 0xFF, (c >> 16) & 0xFF)


def coord_to_px(x, y, pw, ph):
    return (x + pw / 2.0) * SCALE, (ph / 2.0 - y) * SCALE


def rect_to_px(left, top, right, bottom, pw, ph):
    x1, y1 = coord_to_px(left, top, pw, ph)
    x2, y2 = coord_to_px(right, bottom, pw, ph)
    return min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)


def read_mfc_string(data, pos):
    b = data[pos]
    pos += 1
    if b == 0xFF:
        length = struct.unpack_from('<H', data, pos)[0]
        pos += 2
        if length == 0xFFFF:
            length = struct.unpack_from('<I', data, pos)[0]
            pos += 4
    else:
        length = b
    text = data[pos:pos + length]
    return text, pos + length


def parse_ver004_objects(data, start_pos, obj_count):
    objects = []
    pos = start_pos
    class_registry = {}
    next_class_idx = 1

    for obj_idx in range(obj_count):
        if pos + 2 > len(data):
            break

        tag = struct.unpack_from('<H', data, pos)[0]
        pos += 2

        if tag == 0xFFFF:
            if pos + 4 > len(data):
                break
            schema = struct.unpack_from('<H', data, pos)[0]
            pos += 2
            namelen = struct.unpack_from('<H', data, pos)[0]
            pos += 2
            if pos + namelen > len(data) or namelen > 30:
                break
            classname = data[pos:pos + namelen].decode('ascii', errors='replace')
            pos += namelen
            class_registry[next_class_idx] = classname
            next_class_idx += 2
        else:
            ref = tag & 0x7FFF
            if ref not in class_registry:
                break
            classname = class_registry[ref]
            next_class_idx += 1

        if pos + 52 > len(data):
            break

        obj = {'class': classname}
        left, top, right, bottom = struct.unpack_from('<iiii', data, pos)
        obj['rect'] = (left, top, right, bottom)
        obj['bPen'] = struct.unpack_from('<H', data, pos + 16)[0]
        ps, pwx, pwy, pc = struct.unpack_from('<IiiI', data, pos + 18)
        obj['pen'] = {'style': ps, 'width': pwx, 'color': pc}
        obj['bBrush'] = struct.unpack_from('<H', data, pos + 34)[0]
        bs, bc, bh = struct.unpack_from('<III', data, pos + 36)
        obj['brush'] = {'style': bs, 'color': bc, 'hatch': bh}
        obj['layer'] = struct.unpack_from('<I', data, pos + 48)[0]
        pos += 52

        if classname in ('CDrawText', 'CFaxProp'):
            lf = {}
            lf['height'] = struct.unpack_from('<i', data, pos)[0]
            lf['width'] = struct.unpack_from('<i', data, pos + 4)[0]
            lf['escapement'] = struct.unpack_from('<i', data, pos + 8)[0]
            lf['orientation'] = struct.unpack_from('<i', data, pos + 12)[0]
            lf['weight'] = struct.unpack_from('<i', data, pos + 16)[0]
            lf['italic'] = data[pos + 20]
            lf['underline'] = data[pos + 21]
            lf['strikeout'] = data[pos + 22]
            lf['charset'] = data[pos + 23]
            lf['out_prec'] = data[pos + 24]
            lf['clip_prec'] = data[pos + 25]
            lf['quality'] = data[pos + 26]
            lf['pitch_family'] = data[pos + 27]
            face_raw = data[pos + 28:pos + 60]
            lf['face'] = face_raw.split(b'\x00')[0].decode('ascii', errors='replace')
            obj['logfont'] = lf
            pos += 60

            obj['alignment'] = struct.unpack_from('<I', data, pos)[0]
            pos += 4

            text1, pos = read_mfc_string(data, pos)
            obj['text_display'] = text1
            obj['_pad'] = struct.unpack_from('<I', data, pos)[0]
            pos += 4
            text2, pos = read_mfc_string(data, pos)
            obj['text'] = text2

            if classname == 'CFaxProp':
                obj['prop_id'] = struct.unpack_from('<H', data, pos)[0]
                pos += 2

        elif classname == 'CDrawRoundRect':
            obj['corner_w'] = struct.unpack_from('<I', data, pos)[0]
            obj['corner_h'] = struct.unpack_from('<I', data, pos + 4)[0]
            pos += 8

        elif classname == 'CDrawOleObj':
            obj['extent_cx'] = struct.unpack_from('<I', data, pos)[0]
            obj['extent_cy'] = struct.unpack_from('<I', data, pos + 4)[0]
            pos += 8

            sub_tag = struct.unpack_from('<H', data, pos)[0]
            pos += 2
            if sub_tag == 0xFFFF:
                pos += 2
                snl = struct.unpack_from('<H', data, pos)[0]
                pos += 2
                pos += snl
                class_registry[next_class_idx] = 'CDrawItem'
                next_class_idx += 2
            else:
                next_class_idx += 1

            pos += 18
            ole_size = struct.unpack_from('<I', data, pos)[0]
            pos += 4
            usable_size = min(ole_size, len(data) - pos)
            obj['ole_data'] = data[pos:pos + usable_size]
            pos += usable_size

            if pos < len(data) and obj_idx + 1 < obj_count:
                next_tag = struct.unpack_from('<H', data, pos)[0] if pos + 2 <= len(data) else 0
                if next_tag != 0xFFFF and (next_tag & 0x8000) == 0:
                    scan = pos
                    found = False
                    while scan + 6 < len(data):
                        w = struct.unpack_from('<H', data, scan)[0]
                        if w == 0xFFFF:
                            s2 = struct.unpack_from('<H', data, scan + 2)[0]
                            nl2 = struct.unpack_from('<H', data, scan + 4)[0]
                            if s2 == 0 and 5 <= nl2 <= 20 and scan + 6 + nl2 <= len(data):
                                try:
                                    cn2 = data[scan + 6:scan + 6 + nl2].decode('ascii')
                                    if cn2.startswith('CDraw') or cn2.startswith('CFax'):
                                        found = True
                                        break
                                except Exception:
                                    pass
                        elif (w & 0x8000) and (w & 0x7FFF) in class_registry:
                            found = True
                            break
                        scan += 1
                    if found:
                        pos = scan

        objects.append(obj)

    return objects, pos


def _extract_dib_from_wmf(mf_data):
    if len(mf_data) < 18:
        return None
    pos = 18
    while pos + 6 < len(mf_data):
        rec_size = struct.unpack_from('<I', mf_data, pos)[0]
        rec_func = struct.unpack_from('<H', mf_data, pos + 4)[0]
        if rec_func == 0 or rec_size == 0:
            break
        rec_bytes = rec_size * 2
        if rec_func == 0x0F43:
            dib_off = pos + 6 + 22
        elif rec_func in (0x0B41, 0x0940):
            dib_off = pos + 6 + 20
        else:
            pos += rec_bytes
            continue
        if dib_off + 40 > len(mf_data):
            pos += rec_bytes
            continue
        bih_size = struct.unpack_from('<I', mf_data, dib_off)[0]
        if bih_size not in (12, 40, 108, 124):
            pos += rec_bytes
            continue
        w = struct.unpack_from('<i', mf_data, dib_off + 4)[0]
        h = struct.unpack_from('<i', mf_data, dib_off + 8)[0]
        bpp = struct.unpack_from('<H', mf_data, dib_off + 14)[0]
        if w <= 0 or abs(h) <= 0 or bpp not in (1, 4, 8, 16, 24, 32):
            pos += rec_bytes
            continue
        dib_data = mf_data[dib_off:pos + rec_bytes]
        if bpp <= 8:
            palette_size = (1 << bpp) * 4
        else:
            palette_size = 0
        pixel_offset = 14 + bih_size + palette_size
        file_size = 14 + len(dib_data)
        bmp = b'BM'
        bmp += struct.pack('<I', file_size)
        bmp += struct.pack('<HH', 0, 0)
        bmp += struct.pack('<I', pixel_offset)
        bmp += dib_data
        try:
            img = Image.open(io.BytesIO(bmp))
            return img.convert('RGBA')
        except Exception:
            pass
        pos += rec_bytes
    return None


def extract_ole_image(ole_data, obj_rect, page_w, page_h):
    try:
        ole = olefile.OleFileIO(io.BytesIO(ole_data))
    except Exception:
        return None

    mf_data = None
    try:
        if ole.exists('Ole10Native'):
            native = ole.openstream('Ole10Native').read()
            if len(native) > 4:
                native_size = struct.unpack_from('<I', native, 0)[0]
                payload = native[4:4 + native_size] if native_size < len(native) else native[4:]
                try:
                    img = Image.open(io.BytesIO(payload))
                    result = img.convert('RGBA')
                    ole.close()
                    return result
                except Exception:
                    mf_data = payload

        for pres_name in ['\x02OlePres000', '\x02OlePres001']:
            if ole.exists(pres_name):
                pres = ole.openstream(pres_name).read()
                if len(pres) >= 40:
                    data_size = struct.unpack_from('<I', pres, 36)[0]
                    if 40 + data_size > len(pres):
                        data_size = len(pres) - 40
                    mf_data = pres[40:40 + data_size]
                break
    except Exception:
        pass
    ole.close()

    if mf_data is None or len(mf_data) < 4:
        return None

    dib_img = _extract_dib_from_wmf(mf_data)
    if dib_img is not None:
        return dib_img

    with tempfile.NamedTemporaryFile(suffix='.wmf', delete=False) as tmp:
        tmp.write(mf_data)
        tmp_path = tmp.name
    out_path = tmp_path + '.png'
    try:
        subprocess.run(
            ['magick', tmp_path, '-density', str(RENDER_DPI), '-background', 'white',
             '-alpha', 'remove', out_path],
            capture_output=True, timeout=30
        )
        if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
            img = Image.open(out_path).convert('RGBA')
            result = img.copy()
            img.close()
            os.unlink(out_path)
            os.unlink(tmp_path)
            return result
    except Exception:
        pass
    for p in [tmp_path, out_path]:
        if os.path.exists(p):
            os.unlink(p)
    return None


def render_ver004(data, version):
    if version == 3:
        paper = struct.unpack_from('<H', data, 0x14)[0]
        bg_color = struct.unpack_from('<I', data, 0x18)[0]
        obj_count = struct.unpack_from('<H', data, 0x1C)[0]
        obj_start = 0x1E
    else:
        paper = struct.unpack_from('<H', data, 0x16)[0]
        bg_color = struct.unpack_from('<I', data, 0x1A)[0]
        obj_count = struct.unpack_from('<H', data, 0x1E)[0]
        obj_start = 0x20

    page_w, page_h = PAPER_SIZES.get(paper, PAPER_SIZES[1])
    objects, _ = parse_ver004_objects(data, obj_start, obj_count)

    img_w = int(page_w * SCALE)
    img_h = int(page_h * SCALE)
    img = Image.new('RGB', (img_w, img_h), colorref_to_rgb(bg_color))
    draw = ImageDraw.Draw(img)

    objects.sort(key=lambda o: o['layer'])

    for obj in objects:
        cls = obj['class']
        left, top, right, bottom = obj['rect']
        px_rect = rect_to_px(left, top, right, bottom, page_w, page_h)

        if cls in ('CDrawRect', 'CDrawRoundRect'):
            outline_color = None
            fill_color = None
            pen_width = 1
            if obj['bPen']:
                outline_color = colorref_to_rgb(obj['pen']['color'])
                pen_width = max(1, int(obj['pen']['width'] * SCALE))
                if obj['pen']['style'] == 5:
                    outline_color = None
            if obj['bBrush'] and obj['brush']['style'] == 0:
                fill_color = colorref_to_rgb(obj['brush']['color'])

            if cls == 'CDrawRoundRect':
                rw = int(obj.get('corner_w', 20) * SCALE)
                rh = int(obj.get('corner_h', 20) * SCALE)
                radius = max(rw, rh) // 2
                draw.rounded_rectangle(px_rect, radius=radius, fill=fill_color,
                                       outline=outline_color, width=pen_width)
            else:
                draw.rectangle(px_rect, fill=fill_color, outline=outline_color, width=pen_width)

        elif cls == 'CDrawEllipse':
            outline_color = None
            fill_color = None
            pen_width = 1
            if obj['bPen']:
                outline_color = colorref_to_rgb(obj['pen']['color'])
                pen_width = max(1, int(obj['pen']['width'] * SCALE))
                if obj['pen']['style'] == 5:
                    outline_color = None
            if obj['bBrush'] and obj['brush']['style'] == 0:
                fill_color = colorref_to_rgb(obj['brush']['color'])
            draw.ellipse(px_rect, fill=fill_color, outline=outline_color, width=pen_width)

        elif cls == 'CDrawLine':
            pen_color = colorref_to_rgb(obj['pen']['color'])
            pen_width = max(1, int(obj['pen']['width'] * SCALE))
            x1, y1 = coord_to_px(left, top, page_w, page_h)
            x2, y2 = coord_to_px(right, bottom, page_w, page_h)
            draw.line([(x1, y1), (x2, y2)], fill=pen_color, width=pen_width)

        elif cls in ('CDrawText', 'CFaxProp'):
            lf = obj['logfont']
            text_raw = obj.get('text', b'')
            if isinstance(text_raw, bytes):
                codec = CHARSET_TO_CODEPAGE.get(lf.get('charset', 0), 'cp1252')
                try:
                    text = text_raw.decode(codec)
                except Exception:
                    text = text_raw.decode('cp1252', errors='replace')
            else:
                text = text_raw
            text = text.rstrip('\n').rstrip('\r')

            if not text:
                continue

            if lf['face'].lower() == 'marlett':
                text = '■' * len(text)

            font = get_font(lf['face'], lf['height'], lf['weight'], bool(lf['italic']))
            text_color = (0, 0, 0)
            if obj['bPen']:
                text_color = colorref_to_rgb(obj['pen']['color'])

            x1, y1 = px_rect[0], px_rect[1]
            x2 = px_rect[2]
            box_w = px_rect[2] - px_rect[0]
            box_h = px_rect[3] - px_rect[1]
            alignment = obj.get('alignment', 0)

            if alignment == 1:
                bbox = font.getbbox(text)
                tw = bbox[2] - bbox[0]
                x1 = x1 + (box_w - tw) / 2
            elif alignment == 2:
                bbox = font.getbbox(text)
                tw = bbox[2] - bbox[0]
                x1 = x1 + box_w - tw

            draw.text((x1, y1), text, fill=text_color, font=font)

        elif cls == 'CDrawOleObj':
            ole_img = extract_ole_image(obj.get('ole_data', b''), obj['rect'], page_w, page_h)
            if ole_img is not None:
                x1, y1, x2, y2 = [int(v) for v in px_rect]
                target_w = max(1, x2 - x1)
                target_h = max(1, y2 - y1)
                ole_img = ole_img.resize((target_w, target_h), Image.LANCZOS)
                if ole_img.mode == 'RGBA':
                    img.paste(ole_img, (x1, y1), ole_img)
                else:
                    img.paste(ole_img, (x1, y1))

    return [img]


EMR_HEADER = 1
EMR_SETWINDOWEXTEX = 9
EMR_SETWINDOWORGEX = 10
EMR_EOF = 14
EMR_SETMAPMODE = 17
EMR_MOVETOEX = 27
EMR_SELECTOBJECT = 37
EMR_CREATEPEN = 38
EMR_CREATEBRUSHINDIRECT = 39
EMR_DELETEOBJECT = 40
EMR_ELLIPSE = 42
EMR_RECTANGLE = 43
EMR_ROUNDRECT = 44
EMR_LINETO = 54
EMR_SETARCDIRECTION = 57


def parse_emf_shapes(emf_data, page_w, page_h):
    shapes = []
    gdi_table = {}
    cur_pen = {'style': 0, 'width': 0, 'color': 0x000000}
    cur_brush = {'style': 1, 'color': 0xFFFFFF}
    cur_x, cur_y = 0, 0

    pos = 0
    while pos + 8 <= len(emf_data):
        rt, rs = struct.unpack_from('<II', emf_data, pos)
        if rs < 8 or rs > len(emf_data) - pos:
            break

        if rt == EMR_CREATEPEN:
            idx = struct.unpack_from('<I', emf_data, pos + 8)[0]
            style = struct.unpack_from('<I', emf_data, pos + 12)[0]
            width = struct.unpack_from('<I', emf_data, pos + 16)[0]
            color = struct.unpack_from('<I', emf_data, pos + 24)[0]
            gdi_table[idx] = {'type': 'pen', 'style': style, 'width': width, 'color': color}

        elif rt == EMR_CREATEBRUSHINDIRECT:
            idx = struct.unpack_from('<I', emf_data, pos + 8)[0]
            style = struct.unpack_from('<I', emf_data, pos + 12)[0]
            color = struct.unpack_from('<I', emf_data, pos + 16)[0]
            gdi_table[idx] = {'type': 'brush', 'style': style, 'color': color}

        elif rt == EMR_SELECTOBJECT:
            idx = struct.unpack_from('<I', emf_data, pos + 8)[0]
            if idx >= 0x80000000:
                stock = idx - 0x80000000
                if stock == 0:
                    cur_brush = {'style': 0, 'color': 0xFFFFFF}
                elif stock == 4:
                    cur_brush = {'style': 0, 'color': 0x000000}
                elif stock == 5:
                    cur_brush = {'style': 1, 'color': 0}
                elif stock == 7:
                    cur_pen = {'style': 0, 'width': 1, 'color': 0x000000}
                elif stock == 8:
                    cur_pen = {'style': 5, 'width': 0, 'color': 0}
            else:
                obj = gdi_table.get(idx)
                if obj:
                    if obj['type'] == 'pen':
                        cur_pen = obj
                    elif obj['type'] == 'brush':
                        cur_brush = obj

        elif rt == EMR_DELETEOBJECT:
            idx = struct.unpack_from('<I', emf_data, pos + 8)[0]
            gdi_table.pop(idx, None)

        elif rt == EMR_RECTANGLE:
            l, t, r, b = struct.unpack_from('<iiii', emf_data, pos + 8)
            shapes.append({
                'type': 'rect', 'rect': (l, t, r, b),
                'pen': dict(cur_pen), 'brush': dict(cur_brush)
            })

        elif rt == EMR_ELLIPSE:
            l, t, r, b = struct.unpack_from('<iiii', emf_data, pos + 8)
            shapes.append({
                'type': 'ellipse', 'rect': (l, t, r, b),
                'pen': dict(cur_pen), 'brush': dict(cur_brush)
            })

        elif rt == EMR_ROUNDRECT:
            l, t, r, b = struct.unpack_from('<iiii', emf_data, pos + 8)
            cw, ch = struct.unpack_from('<ii', emf_data, pos + 24)
            shapes.append({
                'type': 'roundrect', 'rect': (l, t, r, b),
                'corner': (cw, ch),
                'pen': dict(cur_pen), 'brush': dict(cur_brush)
            })

        elif rt == EMR_MOVETOEX:
            cur_x, cur_y = struct.unpack_from('<ii', emf_data, pos + 8)

        elif rt == EMR_LINETO:
            x2, y2 = struct.unpack_from('<ii', emf_data, pos + 8)
            shapes.append({
                'type': 'line', 'from': (cur_x, cur_y), 'to': (x2, y2),
                'pen': dict(cur_pen)
            })
            cur_x, cur_y = x2, y2

        elif rt == EMR_EOF:
            break

        pos += rs

    return shapes


def parse_cov_section1(data, pos, obj_count):
    objects = []
    for _ in range(obj_count):
        obj = {}
        left, top, right, bottom = struct.unpack_from('<iiii', data, pos)
        obj['rect'] = (left, top, right, bottom)
        pos += 16

        obj['flags'] = struct.unpack_from('<II', data, pos)
        pos += 8

        lf = {}
        lf['height'] = struct.unpack_from('<i', data, pos)[0]
        lf['width'] = struct.unpack_from('<i', data, pos + 4)[0]
        lf['escapement'] = struct.unpack_from('<i', data, pos + 8)[0]
        lf['orientation'] = struct.unpack_from('<i', data, pos + 12)[0]
        lf['weight'] = struct.unpack_from('<i', data, pos + 16)[0]
        lf['italic'] = data[pos + 20]
        lf['underline'] = data[pos + 21]
        lf['strikeout'] = data[pos + 22]
        lf['charset'] = data[pos + 23]
        lf['out_prec'] = data[pos + 24]
        lf['clip_prec'] = data[pos + 25]
        lf['quality'] = data[pos + 26]
        lf['pitch_family'] = data[pos + 27]
        face_raw = data[pos + 28:pos + 92]
        lf['face'] = face_raw.decode('utf-16-le', errors='replace').split('\x00')[0]
        obj['logfont'] = lf
        pos += 92

        word0 = struct.unpack_from('<H', data, pos)[0]
        if word0 == 0:
            pos += 4
            text_len = struct.unpack_from('<I', data, pos)[0]
            pos += 4
            obj['text'] = data[pos:pos + text_len].decode('utf-16-le', errors='replace')
            pos += text_len
            obj['is_text'] = True
        else:
            obj['prop_id'] = word0
            pos += 8
            obj['is_text'] = False

        objects.append(obj)
    return objects, pos


PROP_NAMES = {
    0x07D1: '{Recipient Name}',
    0x07D3: '{Recipient Fax Number}',
    0x07D5: "{Recipient's Company}",
    0x07D7: "{Recipient's Street Address}",
    0x07D9: "{Recipient's Mailing Address}",
    0x07DB: "{Recipient's Department}",
    0x07E1: "{Recipient's Office Telephone #}",
    0x07E3: "{Recipient's Home Telephone #}",
    0x07E7: '{Sender Name}',
    0x07E9: '{Sender Fax #}',
    0x07EB: "{Sender's Company}",
    0x07ED: "{Sender's Address}",
    0x07EF: "{Sender's Title}",
    0x07F1: "{Sender's Department}",
    0x07F3: "{Sender's Billing Code}",
    0x07F5: "{Sender's Home Telephone #}",
    0x07F7: "{Sender's Office Telephone #}",
    0x07F9: '{Subject}',
    0x07FB: '{Time Sent}',
    0x07FD: '{# of Pages}',
    0x07FF: '{# of Attachments}',
    0x0801: '{Recipient Name}',
    0x0803: "{Recipient's Fax Number}",
    0x0805: "{Recipient's City}",
    0x0807: "{Recipient's State}",
    0x0809: "{Recipient's Zip Code}",
    0x080B: "{Recipient's Country}",
    0x080D: "{Recipient's Title}",
    0x080F: '{Note}',
    0x0811: "{Sender's E-mail}",
}


def render_ver005(data):
    emf_size = struct.unpack_from('<I', data, 0x14)[0]
    obj_count = struct.unpack_from('<I', data, 0x18)[0]
    page_w = struct.unpack_from('<I', data, 0x1C)[0]
    page_h = struct.unpack_from('<I', data, 0x20)[0]

    emf_data = data[0x24:0x24 + emf_size]
    shapes = parse_emf_shapes(emf_data, page_w, page_h)

    sec1_start = 0x24 + emf_size
    text_objects, _ = parse_cov_section1(data, sec1_start, obj_count)

    img_w = int(page_w * SCALE)
    img_h = int(page_h * SCALE)
    img = Image.new('RGB', (img_w, img_h), 'white')
    draw = ImageDraw.Draw(img)

    for shape in shapes:
        if shape['type'] == 'rect':
            l, t, r, b = shape['rect']
            px = rect_to_px(l, t, r, b, page_w, page_h)
            outline = None
            fill = None
            pen_w = 1
            pen = shape['pen']
            brush = shape['brush']
            if pen['style'] != 5:
                outline = colorref_to_rgb(pen['color'])
                pen_w = max(1, int(pen.get('width', 1) * SCALE))
            if brush['style'] == 0:
                fill = colorref_to_rgb(brush['color'])
            draw.rectangle(px, fill=fill, outline=outline, width=pen_w)

        elif shape['type'] == 'ellipse':
            l, t, r, b = shape['rect']
            px = rect_to_px(l, t, r, b, page_w, page_h)
            outline = None
            fill = None
            pen_w = 1
            pen = shape['pen']
            brush = shape['brush']
            if pen['style'] != 5:
                outline = colorref_to_rgb(pen['color'])
                pen_w = max(1, int(pen.get('width', 1) * SCALE))
            if brush['style'] == 0:
                fill = colorref_to_rgb(brush['color'])
            draw.ellipse(px, fill=fill, outline=outline, width=pen_w)

        elif shape['type'] == 'roundrect':
            l, t, r, b = shape['rect']
            px = rect_to_px(l, t, r, b, page_w, page_h)
            outline = None
            fill = None
            pen_w = 1
            pen = shape['pen']
            brush = shape['brush']
            if pen['style'] != 5:
                outline = colorref_to_rgb(pen['color'])
                pen_w = max(1, int(pen.get('width', 1) * SCALE))
            if brush['style'] == 0:
                fill = colorref_to_rgb(brush['color'])
            cw, ch = shape['corner']
            radius = max(1, int(max(cw, ch) * SCALE / 2))
            draw.rounded_rectangle(px, radius=radius, fill=fill, outline=outline, width=pen_w)

        elif shape['type'] == 'line':
            fx, fy = coord_to_px(*shape['from'], page_w, page_h)
            tx, ty = coord_to_px(*shape['to'], page_w, page_h)
            pen = shape['pen']
            color = colorref_to_rgb(pen['color'])
            pen_w = max(1, int(pen.get('width', 1) * SCALE))
            draw.line([(fx, fy), (tx, ty)], fill=color, width=pen_w)

    for obj in text_objects:
        lf = obj['logfont']
        if obj['is_text']:
            text = obj['text'].rstrip('\n').rstrip('\r')
        else:
            text = PROP_NAMES.get(obj['prop_id'], f'{{Prop 0x{obj["prop_id"]:04X}}}')

        if not text:
            continue

        font = get_font(lf['face'], lf['height'], lf['weight'], bool(lf['italic']))
        left, top, right, bottom = obj['rect']
        px = rect_to_px(left, top, right, bottom, page_w, page_h)
        draw.text((px[0], px[1]), text, fill=(0, 0, 0), font=font)

    return [img]


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    with open(input_file, 'rb') as f:
        data = f.read()

    if len(data) < 16:
        print("Error: File too small", file=sys.stderr)
        sys.exit(1)

    magic = data[:15]

    if magic == b'FAXCOVER-VER003':
        pages = render_ver004(data, version=3)
    elif magic == b'FAXCOVER-VER004':
        pages = render_ver004(data, version=4)
    elif magic == b'FAXCOVER-VER005':
        pages = render_ver005(data)
    else:
        print("Error: Not a Windows FAX Cover Page file", file=sys.stderr)
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    base = os.path.splitext(os.path.basename(input_file))[0]
    for i, page in enumerate(pages):
        out_path = os.path.join(output_dir, f"{base}_page{i + 1:03d}.png")
        page.save(out_path, 'PNG')
        print(out_path)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""ATTENTION: This program was vibe coded by claude code"""
"""Convert Paint.NET PDN3 files to PNG."""

import struct
import gzip
import re
import sys
import numpy as np
from PIL import Image


class BinaryFormatterParser:
    """Minimal .NET BinaryFormatter parser for PDN files."""

    def __init__(self, data):
        self.data = data
        self.pos = 0
        self.classes = {}
        self.objects = {}

    def read_byte(self):
        v = self.data[self.pos]; self.pos += 1; return v

    def read_int32(self):
        v = struct.unpack_from('<i', self.data, self.pos)[0]; self.pos += 4; return v

    def read_int64(self):
        v = struct.unpack_from('<q', self.data, self.pos)[0]; self.pos += 8; return v

    def read_7bit_int(self):
        val = 0; shift = 0
        while True:
            b = self.read_byte()
            val |= (b & 0x7F) << shift; shift += 7
            if (b & 0x80) == 0: break
        return val

    def read_string(self):
        n = self.read_7bit_int()
        s = self.data[self.pos:self.pos + n].decode('utf-8', errors='replace')
        self.pos += n
        return s

    def read_primitive(self, pt):
        if pt == 1: return bool(self.read_byte())
        elif pt == 2: return self.read_byte()
        elif pt == 8: return self.read_int32()
        elif pt == 9: return self.read_int64()
        elif pt == 7:
            v = struct.unpack_from('<h', self.data, self.pos)[0]; self.pos += 2; return v
        elif pt == 15:
            v = struct.unpack_from('<I', self.data, self.pos)[0]; self.pos += 4; return v
        elif pt == 6:
            v = struct.unpack_from('<d', self.data, self.pos)[0]; self.pos += 8; return v
        elif pt == 11:
            v = struct.unpack_from('<f', self.data, self.pos)[0]; self.pos += 4; return v
        else:
            raise ValueError(f"Unknown primitive type {pt}")

    def read_class_def(self, with_types, is_system):
        obj_id = self.read_int32()
        cn = self.read_string()
        mc = self.read_int32()
        names = [self.read_string() for _ in range(mc)]
        if with_types:
            bts = [self.read_byte() for _ in range(mc)]
            adds = []
            for bt in bts:
                if bt == 0: adds.append(self.read_byte())
                elif bt == 3: adds.append(self.read_string())
                elif bt == 4:
                    c = self.read_string(); a = self.read_int32(); adds.append((c, a))
                elif bt == 7: adds.append(self.read_byte())
                else: adds.append(None)
        else:
            bts = None; adds = None
        lib = self.read_int32() if not is_system else None
        cdef = {'name': cn, 'members': names, 'btypes': bts, 'addtl': adds}
        self.classes[obj_id] = cdef
        return obj_id, cdef

    def read_values(self, obj_id, cdef):
        vals = {}
        for i, name in enumerate(cdef['members']):
            bt = cdef['btypes'][i] if cdef['btypes'] else 2
            add = cdef['addtl'][i] if cdef['addtl'] else None
            if bt == 0:
                vals[name] = self.read_primitive(add)
            else:
                vals[name] = self.read_record()
        self.objects[obj_id] = {'_type': cdef['name'], **vals}
        return vals

    def read_array_items(self, length):
        items = []
        while len(items) < length:
            item = self.read_record()
            if isinstance(item, list):
                items.extend(item)
            else:
                items.append(item)
        return items

    def read_record(self):
        if self.pos >= len(self.data):
            return None
        rt = self.read_byte()
        if rt == 0x00:  # SerializedStreamHeader
            self.pos += 16; return self.read_record()
        elif rt == 0x0C:  # BinaryLibrary
            self.read_int32(); self.read_string(); return self.read_record()
        elif rt == 0x05:  # ClassWithMembersAndTypes
            oid, cdef = self.read_class_def(True, False)
            return {'_type': cdef['name'], '_id': oid, **self.read_values(oid, cdef)}
        elif rt == 0x04:  # SystemClassWithMembersAndTypes
            oid, cdef = self.read_class_def(True, True)
            return {'_type': cdef['name'], '_id': oid, **self.read_values(oid, cdef)}
        elif rt == 0x01:  # ClassWithId
            oid = self.read_int32(); rid = self.read_int32()
            cdef = self.classes[rid]; self.classes[oid] = cdef
            return {'_type': cdef['name'], '_id': oid, **self.read_values(oid, cdef)}
        elif rt == 0x06:  # BinaryObjectString
            oid = self.read_int32(); s = self.read_string()
            self.objects[oid] = s; return s
        elif rt == 0x09:  # MemberReference
            return {'_ref': self.read_int32()}
        elif rt == 0x0A:  # ObjectNull
            return None
        elif rt == 0x0D:  # ObjectNullMultiple256
            return [None] * self.read_byte()
        elif rt == 0x0E:  # ObjectNullMultiple
            return [None] * self.read_int32()
        elif rt == 0x10:  # ArraySingleObject
            oid = self.read_int32(); length = self.read_int32()
            items = self.read_array_items(length)
            self.objects[oid] = items; return items
        elif rt == 0x11:  # ArraySingleString
            oid = self.read_int32(); length = self.read_int32()
            items = self.read_array_items(length)
            self.objects[oid] = items; return items
        elif rt == 0x0F:  # ArraySinglePrimitive
            oid = self.read_int32(); length = self.read_int32()
            pt = self.read_byte()
            items = [self.read_primitive(pt) for _ in range(length)]
            self.objects[oid] = items; return items
        elif rt == 0x0B:  # MessageEnd
            return {'_end': True}
        elif rt == 0x15:  # MemberPrimitiveTyped
            pt = self.read_byte(); return self.read_primitive(pt)
        elif rt == 0x07:  # BinaryArray
            oid = self.read_int32()
            at = self.read_byte(); rank = self.read_int32()
            lens = [self.read_int32() for _ in range(rank)]
            if at in (3, 4, 5):
                for _ in range(rank): self.read_int32()
            te = self.read_byte()
            if te == 0: self.read_byte()
            elif te == 3: self.read_string()
            elif te == 4: self.read_string(); self.read_int32()
            elif te == 7: self.read_byte()
            total = 1
            for l in lens: total *= l
            items = self.read_array_items(total)
            self.objects[oid] = items; return items
        else:
            raise ValueError(f"Unknown record type 0x{rt:02x} at offset {self.pos - 1}")


def resolve(obj, objects):
    if isinstance(obj, dict) and '_ref' in obj:
        return objects.get(obj['_ref'])
    return obj


def parse_pdn(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()

    if data[:4] != b'PDN3':
        raise ValueError("Not a PDN3 file")

    xml_len = struct.unpack_from('<I', data, 4)[0] & 0xFFFFFF
    xml_str = data[7:7 + xml_len].decode('utf-8')

    width = int(re.search(r'width="(\d+)"', xml_str).group(1))
    height = int(re.search(r'height="(\d+)"', xml_str).group(1))
    num_layers = int(re.search(r'layers="(\d+)"', xml_str).group(1))

    bin_start = 7 + xml_len + 2
    parser = BinaryFormatterParser(data[bin_start:])

    while True:
        rec = parser.read_record()
        if rec is None or (isinstance(rec, dict) and rec.get('_end')):
            break

    deferred_start = bin_start + parser.pos

    objs = parser.objects
    layers_meta = []

    layer_list = None
    for oid, obj in objs.items():
        if isinstance(obj, dict) and obj.get('_type') == 'PaintDotNet.LayerList':
            layer_list = obj
            break

    if layer_list:
        items = resolve(layer_list.get('ArrayList+_items'), objs)
        if not isinstance(items, list):
            items = []
        size = layer_list.get('ArrayList+_size', num_layers)

        for i in range(size):
            item = items[i] if i < len(items) else None
            item = resolve(item, objs)
            if not isinstance(item, dict):
                layers_meta.append({'visible': True, 'opacity': 255, 'blend': 'Normal'})
                continue

            lp = resolve(item.get('Layer+properties'), objs)
            if not isinstance(lp, dict):
                lp = {}

            blp = resolve(item.get('properties'), objs)
            blend = 'Normal'
            if isinstance(blp, dict):
                bo = resolve(blp.get('blendOp'), objs)
                if isinstance(bo, dict):
                    t = bo.get('_type', '')
                    for mode in ['Multiply', 'Additive', 'ColorBurn', 'ColorDodge',
                                 'Reflect', 'Glow', 'Overlay', 'Difference',
                                 'Negation', 'Lighten', 'Darken', 'Screen', 'Xor']:
                        if mode in t:
                            blend = mode
                            break

            layers_meta.append({
                'visible': lp.get('visible', True),
                'opacity': lp.get('opacity', 255),
                'blend': blend,
            })
    else:
        for _ in range(num_layers):
            layers_meta.append({'visible': True, 'opacity': 255, 'blend': 'Normal'})

    offset = deferred_start
    pixel_size = width * height * 4
    layer_pixels = []

    for layer_idx in range(num_layers):
        header = data[offset:offset + 13]
        fmt_byte = header[2]
        chunk_order = header[8]
        comp_size = struct.unpack('>I', header[9:13])[0]
        max_chunk = fmt_byte * 65536
        offset += 13

        gz_data = data[offset:offset + comp_size]
        offset += comp_size
        chunks = [gzip.decompress(gz_data)]

        num_full = pixel_size // max_chunk
        remainder = pixel_size % max_chunk
        total_chunks = num_full + (1 if remainder > 0 else 0)

        for ci in range(1, total_chunks):
            ch_header = data[offset:offset + 8]
            ch_comp_size = struct.unpack('>I', ch_header[4:8])[0]
            offset += 8
            gz_data = data[offset:offset + ch_comp_size]
            offset += ch_comp_size
            chunks.append(gzip.decompress(gz_data))

        if chunk_order == 1 and remainder > 0 and len(chunks) > 1:
            chunks = chunks[1:] + [chunks[0]]

        pixel_data = b''.join(chunks)
        if len(pixel_data) != pixel_size:
            raise ValueError(
                f"Layer {layer_idx}: expected {pixel_size} bytes, got {len(pixel_data)}")
        layer_pixels.append(pixel_data)

    return width, height, layers_meta, layer_pixels


def blend_np(src, dst, mode):
    """Apply blend mode using numpy. src and dst are float64 arrays [0,1]."""
    if mode == 'Multiply':
        return src * dst
    elif mode == 'Additive':
        return np.minimum(src + dst, 1.0)
    elif mode == 'ColorBurn':
        with np.errstate(divide='ignore', invalid='ignore'):
            r = np.where(src == 0, 0.0, np.maximum(0.0, 1.0 - (1.0 - dst) / src))
        return r
    elif mode == 'ColorDodge':
        with np.errstate(divide='ignore', invalid='ignore'):
            r = np.where(src >= 1.0, 1.0, np.minimum(1.0, dst / (1.0 - src)))
        return r
    elif mode == 'Overlay':
        return np.where(dst < 0.5,
                        2.0 * src * dst,
                        1.0 - 2.0 * (1.0 - src) * (1.0 - dst))
    elif mode == 'Difference':
        return np.abs(src - dst)
    elif mode == 'Lighten':
        return np.maximum(src, dst)
    elif mode == 'Darken':
        return np.minimum(src, dst)
    elif mode == 'Screen':
        return src + dst - src * dst
    elif mode == 'Negation':
        return 1.0 - np.abs(1.0 - src - dst)
    elif mode == 'Reflect':
        with np.errstate(divide='ignore', invalid='ignore'):
            return np.where(src >= 1.0, 1.0, np.minimum(1.0, dst * dst / (1.0 - src)))
    elif mode == 'Glow':
        with np.errstate(divide='ignore', invalid='ignore'):
            return np.where(dst >= 1.0, 1.0, np.minimum(1.0, src * src / (1.0 - dst)))
    elif mode == 'Xor':
        s = np.round(src * 255).astype(np.int32)
        d = np.round(dst * 255).astype(np.int32)
        return (s ^ d).astype(np.float64) / 255.0
    return src


def composite_layers(width, height, layers_meta, layer_pixels):
    """Composite visible layers using W3C compositing model with numpy."""
    # Work in float64 for precision
    # Canvas: RGBA float [0, 1], starts transparent
    canvas = np.zeros((height, width, 4), dtype=np.float64)

    for meta, pixels in zip(layers_meta, layer_pixels):
        if not meta['visible']:
            continue

        opacity = meta['opacity'] / 255.0
        mode = meta['blend']

        # Parse BGRA pixel data into RGBA float array
        raw = np.frombuffer(pixels, dtype=np.uint8).reshape(height, width, 4)
        src = np.zeros((height, width, 4), dtype=np.float64)
        src[:, :, 0] = raw[:, :, 2] / 255.0  # R
        src[:, :, 1] = raw[:, :, 1] / 255.0  # G
        src[:, :, 2] = raw[:, :, 0] / 255.0  # B
        src[:, :, 3] = raw[:, :, 3] / 255.0 * opacity  # A with opacity

        src_a = src[:, :, 3:4]
        dst_a = canvas[:, :, 3:4]
        src_rgb = src[:, :, :3]
        dst_rgb = canvas[:, :, :3]

        if mode == 'Normal':
            mixed_rgb = src_rgb
        else:
            blended = blend_np(src_rgb, dst_rgb, mode)
            # W3C: Cs = (1 - αb) * Cs + αb * B(Cb, Cs)
            mixed_rgb = (1.0 - dst_a) * src_rgb + dst_a * blended

        # Standard source-over compositing with the mixed color
        # result_a = src_a + dst_a * (1 - src_a)
        result_a = src_a + dst_a * (1.0 - src_a)
        # result_rgb = (src_a * mixed_rgb + dst_a * (1 - src_a) * dst_rgb) / result_a
        safe_a = np.where(result_a > 0, result_a, 1.0)
        result_rgb = (src_a * mixed_rgb + dst_a * (1.0 - src_a) * dst_rgb) / safe_a

        canvas[:, :, :3] = np.where(result_a > 0, result_rgb, 0.0)
        canvas[:, :, 3:4] = result_a

    # Convert to uint8 RGBA
    canvas_u8 = np.clip(np.round(canvas * 255), 0, 255).astype(np.uint8)
    return canvas_u8.tobytes()


def convert_pdn_to_png(input_path, output_path):
    width, height, layers_meta, layer_pixels = parse_pdn(input_path)
    rgba_data = composite_layers(width, height, layers_meta, layer_pixels)
    img = Image.frombytes('RGBA', (width, height), rgba_data)
    img.save(output_path, 'PNG')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} inputFile outputFile", file=sys.stderr)
        sys.exit(1)
    convert_pdn_to_png(sys.argv[1], sys.argv[2])

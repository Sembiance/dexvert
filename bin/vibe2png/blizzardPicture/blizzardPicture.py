#!/usr/bin/env python3
# Vibe coded by Codex
"""Decode BLP1/BLP2 to PNG. Pillow is required for JPEG decoding and PNG writing.

Usage: python blizzardPicture.py input.blp output.png
Optional: --all-mipmaps, --mip LEVEL, --audit audit.json
Every declared mipmap is examined, even when only one PNG is requested.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import hashlib
import io
import json
import os
from pathlib import Path
import struct
import sys
import tempfile

from PIL import Image, ImageFile


class BLPError(ValueError):
    """Recognized but unrecoverable BLP data."""


class UnsupportedBLP(BLPError):
    """Not BLP1/BLP2, or an encoding with no defined supported interpretation."""


MAX_PIXELS = 64 * 1024 * 1024


def rgb565(value):
    r, g, b = value >> 11, (value >> 5) & 63, value & 31
    return ((r << 3) | (r >> 2), (g << 2) | (g >> 4), (b << 3) | (b >> 2))


def decode_blocks(data, width, height, kind, use_alpha=True):
    """BC1/2/3, including edge blocks. Incomplete blocks stay transparent."""
    stride = 8 if kind == 1 else 16
    result = bytearray(width * height * 4)
    transparent_selectors = 0
    blocks_x = (width + 3) // 4
    count = min(len(data) // stride, blocks_x * ((height + 3) // 4))
    for block in range(count):
        start = block * stride
        color_start = start if kind == 1 else start + 8
        c0, c1, selectors = struct.unpack_from('<HHI', data, color_start)
        p0, p1 = rgb565(c0), rgb565(c1)
        colors = [p0, p1]
        if kind != 1 or c0 > c1:
            colors += [tuple((2*a+b)//3 for a, b in zip(p0, p1)),
                       tuple((a+2*b)//3 for a, b in zip(p0, p1))]
        else:
            colors += [tuple((a+b)//2 for a, b in zip(p0, p1)), (0, 0, 0)]
        alpha_bits = int.from_bytes(data[start:start+8], 'little')
        if kind == 3:
            a0, a1 = data[start:start+2]
            alpha_table = [a0, a1]
            if a0 > a1:
                alpha_table += [((7-i)*a0+i*a1)//7 for i in range(1, 7)]
            else:
                alpha_table += [((5-i)*a0+i*a1)//5 for i in range(1, 5)] + [0, 255]
            alpha_bits >>= 16
        bx, by = (block % blocks_x)*4, (block // blocks_x)*4
        for p in range(16):
            x, y = bx + p % 4, by + p // 4
            if x >= width or y >= height:
                continue
            selector = (selectors >> (2*p)) & 3
            if kind == 1 and c0 <= c1 and selector == 3:
                transparent_selectors += 1
            a = 255
            if use_alpha:
                if kind == 1 and c0 <= c1 and selector == 3:
                    a = 0
                elif kind == 2:
                    a = ((alpha_bits >> (4*p)) & 15)*17
                elif kind == 3:
                    a = alpha_table[(alpha_bits >> (3*p)) & 7]
            pos = (y*width+x)*4
            result[pos:pos+4] = bytes((*colors[selector], a))
    image = Image.frombytes('RGBA', (width, height), bytes(result))
    if kind == 1:
        image.info['bc1_transparent_pixels'] = transparent_selectors
    return image


def inspect_jpeg(data):
    """Walk JPEG marker lengths and byte stuffing, without guessing boundaries.

    Offsets are into shared-prefix + mip-payload, not the BLP file. Entropy
    coefficients are decoded by libjpeg through Pillow, not by this walker.
    """
    records = []
    if not data.startswith(b'\xff\xd8'):
        raise BLPError('reassembled JPEG has no SOI marker')
    records.append({'offset': 0, 'length': 2, 'kind': 'SOI'})
    pos = 2
    frame = None
    while pos < len(data):
        start = pos
        if data[pos] != 255:
            raise BLPError(f'expected JPEG marker at logical offset {pos}')
        while pos < len(data) and data[pos] == 255:
            pos += 1
        if pos == len(data):
            break
        code = data[pos]
        pos += 1
        if code == 0xD9:
            records.append({'offset': start, 'length': pos-start, 'kind': 'EOI'})
            return {'segments': records, 'frame': frame, 'end': pos, 'complete': True}
        if code == 0 or code == 0xD8:
            raise BLPError(f'invalid JPEG marker FF{code:02X} at {start}')
        if code == 1 or 0xD0 <= code <= 0xD7:
            records.append({'offset': start, 'length': pos-start, 'kind': f'FF{code:02X}'})
            continue
        if pos+2 > len(data):
            break
        length = int.from_bytes(data[pos:pos+2], 'big')
        if length < 2:
            raise BLPError(f'invalid JPEG segment length at {start}')
        end = pos + length
        payload = data[pos+2:min(end, len(data))]
        kind = {0xC0: 'SOF0', 0xC1: 'SOF1', 0xC2: 'SOF2', 0xC4: 'DHT',
                0xDB: 'DQT', 0xDA: 'SOS', 0xDD: 'DRI', 0xFE: 'COM'}.get(code, f'FF{code:02X}')
        rec = {'offset': start, 'length': min(end, len(data))-start, 'kind': kind}
        if code in (0xC0, 0xC1, 0xC2) and len(payload) >= 6:
            precision, h, w, nc = struct.unpack_from('>BHHB', payload)
            frame = {'precision': precision, 'width': w, 'height': h,
                     'components': nc, 'process': kind,
                     'component_descriptors': list(payload[6:])}
        if code == 0xFE:
            rec['comment'] = payload.decode('latin1')
        records.append(rec)
        pos = end
        if end > len(data):
            break
        if code == 0xDA:
            scan = pos
            while pos < len(data):
                marker = data.find(b'\xff', pos)
                if marker < 0:
                    pos = len(data)
                    break
                p = marker+1
                while p < len(data) and data[p] == 255:
                    p += 1
                if p >= len(data):
                    pos = len(data)
                    break
                if data[p] == 0 or 0xD0 <= data[p] <= 0xD7:
                    pos = p+1
                    continue
                pos = marker
                break
            records.append({'offset': scan, 'length': pos-scan,
                            'kind': 'entropy-coded scan (including stuffing/restarts)'})
    return {'segments': records, 'frame': frame, 'end': len(data), 'complete': False}


@dataclass
class BLP:
    data: bytes
    metadata: dict = field(default_factory=dict)
    regions: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    levels: list = field(default_factory=list)
    images: dict = field(default_factory=dict)
    unresolved: list = field(default_factory=list)

    def warn(self, message, level=None):
        entry = {'message': message}
        if level is not None:
            entry['level'] = level
        self.warnings.append(entry)

    def region(self, start, length, kind, understood=True):
        end = min(len(self.data), start+length)
        if start >= end:
            return
        raw = self.data[start:end]
        item = {'offset': start, 'length': end-start, 'kind': kind,
                'sha256': hashlib.sha256(raw).hexdigest(), 'understood': understood}
        self.regions.append(item)
        if not understood:
            self.unresolved.append(item)

    def opaque(self, start, length, kind):
        raw = self.data[start:start+length]
        zero = not any(raw)
        self.region(start, length, kind + (' (all zero)' if zero else ' (opaque bytes)'), zero)
        if not zero:
            self.warn(f'{len(raw)} uninterpreted bytes at offset {start}: {kind}')

    def parse(self):
        b = self.data
        if b[:4] not in (b'BLP1', b'BLP2'):
            raise UnsupportedBLP('not BLP1 or BLP2 (exact signature required)')
        v = b[:4].decode('ascii')
        header_size = 156 if v == 'BLP1' else 148
        if len(b) < header_size:
            raise BLPError(f'truncated {v} header: {len(b)} of {header_size} bytes')
        content, = struct.unpack_from('<I', b, 4)
        if content not in (0, 1):
            raise UnsupportedBLP(f'unsupported {v} content type {content}')
        w, h = struct.unpack_from('<II', b, 12)
        if not w or not h or w*h > MAX_PIXELS:
            raise BLPError(f'invalid or excessive dimensions {w} x {h}; limit {MAX_PIXELS} pixels')
        if v == 'BLP1':
            alpha, = struct.unpack_from('<I', b, 8)
            extra, mips = struct.unpack_from('<II', b, 20)
            encoding, alpha_encoding, base = (0 if content == 0 else 1), None, 28
        else:
            encoding, alpha, alpha_encoding, mips = b[8:12]
            extra, base = None, 20
            if content == 0:
                raise UnsupportedBLP('BLP2 JPEG content has no verified implementation here')
            if encoding not in (1, 2, 3):
                raise UnsupportedBLP(f'unsupported BLP2 encoding {encoding}')
        if encoding == 1 and alpha not in (0, 1, 4, 8):
            raise UnsupportedBLP(f'indexed alpha depth {alpha} has no supported packing')
        if encoding == 2 and alpha_encoding not in (0, 1, 7):
            raise UnsupportedBLP(f'unsupported BC alpha encoding {alpha_encoding}')
        if encoding == 2 and ((alpha_encoding == 0 and alpha not in (0, 1)) or
                              (alpha_encoding != 0 and alpha not in (0, 4, 8))):
            raise UnsupportedBLP(f'unsupported BC alpha depth/encoding {alpha}/{alpha_encoding}')
        if encoding == 3 and alpha not in (0, 8):
            raise UnsupportedBLP(f'unsupported BGRA alpha depth {alpha}')
        self.metadata = dict(version=v, content=content, encoding=encoding, alpha_depth=alpha,
                             alpha_encoding=alpha_encoding, extra=extra, has_mipmaps=mips,
                             width=w, height=h, file_size=len(b))
        if encoding == 0 and alpha not in (0, 8):
            self.warn(f'noncanonical JPEG alpha depth {alpha}; recovering the explicit 8-bit fourth JPEG component')
        if mips not in (0, 1):
            self.warn(f'noncanonical mipmap flag {mips}; following explicit table entries')
        offsets = struct.unpack_from('<16I', b, base)
        sizes = struct.unpack_from('<16I', b, base+64)
        self.metadata.update(mip_offsets=list(offsets), mip_sizes=list(sizes))
        fields = [(0, 4, 'signature'), (4, 4, 'content'), (12, 4, 'width'), (16, 4, 'height')]
        if v == 'BLP1':
            fields += [(8, 4, 'alpha depth'), (20, 4, 'legacy extra field'), (24, 4, 'mipmap flag')]
        else:
            fields += [(8, 1, 'encoding'), (9, 1, 'alpha depth'), (10, 1, 'alpha encoding'), (11, 1, 'mipmap flag')]
        for start, length, kind in fields:
            # The legacy extra field is deliberately not given a speculative meaning.
            self.region(start, length, kind, kind != 'legacy extra field')
        for i in range(16):
            self.region(base+4*i, 4, f'mip {i} offset')
            self.region(base+64+4*i, 4, f'mip {i} length')
        shared, palette = b'', b''
        meta_end = header_size
        if encoding == 0:
            if len(b) < header_size+4:
                raise BLPError('missing JPEG shared-header length')
            shared_len, = struct.unpack_from('<I', b, header_size)
            self.region(header_size, 4, 'JPEG shared-header length')
            meta_end = header_size+4+shared_len
            shared = b[header_size+4:meta_end]
            self.region(header_size+4, shared_len, 'shared JPEG stream prefix')
            self.metadata['jpeg_shared_length'] = shared_len
            if meta_end > len(b):
                self.warn('shared JPEG header extends past EOF')
        else:
            meta_end += 1024
            palette = b[header_size:meta_end]
            self.region(header_size, 1024, '256 BGRX palette entries' if encoding == 1 else 'unused 1024-byte palette area')
            if len(palette) < 1024:
                self.warn('palette area is truncated; unavailable indexed colors stay transparent')
        coverage = [(0, min(meta_end, len(b)))]
        for level, (offset, length) in enumerate(zip(offsets, sizes)):
            shared_only = level == 0 and encoding == 0 and not mips and length == 0
            if not offset and not length and not shared_only:
                continue
            wi, hi = max(1, w >> level), max(1, h >> level)
            info = dict(level=level, offset=offset, declared_length=length, width=wi, height=hi)
            self.levels.append(info)
            if length == 0 and not shared_only:
                info['status'] = 'empty table entry'
                self.warn('nonzero offset with zero length; no mip payload declared', level)
                continue
            if offset < meta_end and not shared_only:
                info['status'] = 'invalid offset into metadata'
                self.warn('mip points into header or palette; not decoded', level)
                continue
            payload = b'' if shared_only else b[offset:offset+length]
            info['available_length'] = len(payload)
            coverage.append((min(offset, len(b)), min(offset+length, len(b))))
            if offset+length > len(b):
                self.warn(f'mipmap extends beyond EOF; {len(payload)} of {length} bytes available', level)
            if level and not mips:
                self.warn('mip entry exists despite false mipmap flag; decoded from table', level)
            if level >= max(w, h).bit_length():
                self.warn('redundant level beyond the first 1x1 mipmap', level)
            try:
                if encoding == 0:
                    if not payload and not shared_only:
                        raise BLPError('no JPEG mip payload available at the declared offset')
                    image = self.jpeg(shared, payload, wi, hi, alpha, level, offset, info)
                else:
                    if encoding == 1:
                        needed = wi*hi + (wi*hi*alpha+7)//8
                    elif encoding == 3:
                        needed = wi*hi*4
                    else:
                        needed = ((wi+3)//4)*((hi+3)//4)*(8 if alpha_encoding == 0 else 16)
                    self.region(offset, min(needed, len(payload)), f'mip {level} {self.encoding_name()} pixels')
                    if len(payload) > needed:
                        self.opaque(offset+needed, len(payload)-needed, f'mip {level} excess payload')
                        self.warn(f'payload declares {length} bytes; encoding requires {needed}; excess is not another encoding', level)
                    if len(payload) < needed:
                        self.warn(f'incomplete pixel data: {len(payload)} of {needed} bytes; missing pixels/blocks transparent', level)
                    if not payload:
                        raise BLPError('no pixel data available')
                    if encoding == 1:
                        image = self.indexed(payload[:needed], palette, wi, hi, alpha)
                    elif encoding == 3:
                        count = min(wi*hi, len(payload)//4)
                        raw = bytearray(wi*hi*4)
                        for p in range(count):
                            blue, green, red, a = payload[4*p:4*p+4]
                            raw[4*p:4*p+4] = bytes((red, green, blue, a if alpha else 255))
                        image = Image.frombytes('RGBA', (wi, hi), bytes(raw))
                    else:
                        # BC1 carries a transparent selector in each block.
                        # Preserve it even when the container declares alpha=0;
                        # that declaration is not permission to erase stored alpha.
                        image = decode_blocks(payload[:needed], wi, hi,
                                              {0: 1, 1: 2, 7: 3}[alpha_encoding],
                                              alpha_encoding == 0 or bool(alpha))
                        if alpha_encoding == 0:
                            transparent = image.info['bc1_transparent_pixels']
                            info['bc1_transparent_pixels'] = transparent
                            if alpha == 0 and transparent:
                                self.warn(f'header declares no alpha, but {transparent} pixels use the BC1 transparent selector; preserving encoded transparency', level)
                self.images[level] = image
                info['status'] = 'decoded'
            except (BLPError, OSError, ValueError, SyntaxError) as exc:
                info['status'] = 'unrecoverable mipmap'
                info['error'] = str(exc)
                self.warn(str(exc), level)
        cursor = 0
        for start, end in sorted(coverage):
            if start > cursor:
                self.opaque(cursor, start-cursor, 'unreferenced file gap')
            cursor = max(cursor, end)
        if cursor < len(b):
            self.opaque(cursor, len(b)-cursor, 'unreferenced file trailer')
        return self

    def encoding_name(self):
        enc = self.metadata['encoding']
        return {0: 'JPEG BGRA', 1: 'indexed BGR + packed alpha', 3: 'raw BGRA'}.get(
            enc, {0: 'BC1 / DXT1', 1: 'BC2 / DXT3', 7: 'BC3 / DXT5'}.get(self.metadata['alpha_encoding'], 'unknown'))

    @staticmethod
    def indexed(data, palette, w, h, alpha):
        count = w*h
        out = bytearray(count*4)
        mask = (1 << alpha)-1
        for p in range(min(count, len(data))):
            index = data[p]*4
            if index+3 > len(palette):
                continue
            blue, green, red = palette[index:index+3]
            a = 255
            if alpha:
                bit = p*alpha
                pos = count + bit//8
                a = (((data[pos] >> (bit % 8)) & mask)*255)//mask if pos < len(data) else 0
            out[p*4:p*4+4] = bytes((red, green, blue, a))
        return Image.frombytes('RGBA', (w, h), bytes(out))

    def jpeg(self, shared, payload, w, h, alpha, level, offset, info):
        data = shared+payload
        try:
            inspection = inspect_jpeg(data)
            info['jpeg'] = inspection
        except BLPError as exc:
            self.region(offset, len(payload), f'mip {level} malformed JPEG payload', False)
            raise exc
        used = max(0, inspection['end']-len(shared))
        self.region(offset, min(used, len(payload)), f'mip {level} JPEG stream suffix')
        if inspection['complete'] and used < len(payload):
            self.opaque(offset+used, len(payload)-used, f'mip {level} bytes after JPEG EOI')
        if not inspection['complete']:
            self.warn('JPEG is truncated or lacks EOI; requesting libjpeg recovery', level)
        frame = inspection['frame']
        if frame is None or frame['components'] not in (3, 4) or frame['precision'] != 8:
            raise BLPError('JPEG requires an 8-bit frame with three BGR or four BGRA components')
        if frame['width']*frame['height'] > MAX_PIXELS:
            raise BLPError('JPEG frame exceeds pixel limit')
        previous = ImageFile.LOAD_TRUNCATED_IMAGES
        try:
            ImageFile.LOAD_TRUNCATED_IMAGES = not inspection['complete']
            image = Image.open(io.BytesIO(data), formats=['JPEG'])
            # Request the stored components themselves. Never convert CMYK ink
            # values to RGB or permit libjpeg's ordinary YCbCr color conversion.
            mode = 'CMYK' if frame['components'] == 4 else 'RGB'
            tile = image.tile[0]
            image.tile = [tile._replace(args=(mode, mode))]
            image.load()
            bands = image.split()
            opacity = bands[3] if len(bands) == 4 and alpha != 0 else Image.new('L', image.size, 255)
            result = Image.merge('RGBA', (bands[2], bands[1], bands[0], opacity))
        finally:
            ImageFile.LOAD_TRUNCATED_IMAGES = previous
        if result.size != (w, h):
            self.warn(f'JPEG frame {result.width}x{result.height} differs from mip size {w}x{h}; crop/pad at bottom/right', level)
            result = result.crop((0, 0, w, h))
        return result

    def audit(self):
        spans = sorted((r['offset'], r['offset']+r['length']) for r in self.regions)
        cursor = covered = 0
        for start, end in spans:
            covered += max(0, end-max(start, cursor))
            cursor = max(cursor, end)
        return dict(metadata=self.metadata, encoding=self.encoding_name(), levels=self.levels,
                    warnings=self.warnings, regions=sorted(self.regions, key=lambda r:r['offset']),
                    covered_bytes=covered, unaccounted_bytes=len(self.data)-covered,
                    unresolved_regions=self.unresolved,
                    completeness='unresolved byte semantics' if self.unresolved else 'all bytes classified')


def atomic_write(path, data):
    """No destination is opened until decoding/serialization has succeeded."""
    path = Path(path)
    fd, temporary = tempfile.mkstemp(prefix='.'+path.name+'.', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            os.fchmod(stream.fileno(), 0o664)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def save_png(image, path):
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    atomic_write(path, buffer.getvalue())


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('inputFile', type=Path)
    parser.add_argument('outputFile', type=Path)
    parser.add_argument('--mip', type=int, default=None, help='select a particular mip instead of the largest available')
    parser.add_argument('--all-mipmaps', action='store_true', help='also write output.mipNN.png for every other decoded level')
    parser.add_argument('--audit', type=Path, help='write JSON byte map and diagnostics')
    args = parser.parse_args(argv)
    try:
        if args.inputFile.resolve() == args.outputFile.resolve():
            raise BLPError('input and output must be different files')
        # Read only the signature before committing to reading a potentially unrelated file.
        with args.inputFile.open('rb') as stream:
            signature = stream.read(4)
            if signature not in (b'BLP1', b'BLP2'):
                raise UnsupportedBLP('not BLP1 or BLP2 (exact signature required)')
            picture = BLP(signature+stream.read()).parse()
        if not picture.images:
            raise BLPError('no recoverable mipmap')
        selected = args.mip if args.mip is not None else min(picture.images)
        if selected not in picture.images:
            raise BLPError(f'mipmap {selected} cannot be recovered')
        outputs = [(args.outputFile, picture.images[selected])]
        if args.all_mipmaps:
            outputs += [(args.outputFile.with_name(args.outputFile.stem+f'.mip{i:02d}.png'), im)
                        for i, im in sorted(picture.images.items()) if i != selected]
        all_paths = [p.resolve() for p, _ in outputs] + ([args.audit.resolve()] if args.audit else [])
        if len(set(all_paths)) != len(all_paths) or args.inputFile.resolve() in all_paths:
            raise BLPError('output paths must be distinct and must not overwrite the input')
        for path, im in outputs:
            save_png(im, path)
        if args.audit:
            atomic_write(args.audit, (json.dumps(picture.audit(), indent=2)+'\n').encode())
        for warning in picture.warnings:
            prefix = f"mip {warning['level']}: " if 'level' in warning else ''
            print('warning: '+prefix+warning['message'], file=sys.stderr)
        if selected != 0 and args.mip is None:
            print(f'warning: full-size mip unavailable; wrote mip {selected}', file=sys.stderr)
        return 0
    except (BLPError, OSError, ValueError, Image.DecompressionBombError) as exc:
        print(f'blizzardPicture: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())

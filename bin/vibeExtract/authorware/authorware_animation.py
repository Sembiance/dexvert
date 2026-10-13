# Vibe coded by Codex
"""Recover root-referenced Authorware bitmap animations as lossless APNGs.

The established layout is little-endian: 0x33 directories, 0x38 storage
blocks, and Display properties identifying the owner, resource IDs and rate.
No image library is needed. Unknown layouts raise ValueError so callers can
retain the original resources instead of exporting an incomplete animation.
"""

import hashlib
import struct
import zlib

from authorware_pig import legacy_project_root


MAX_CANVAS_PIXELS = 16_000_000
MAX_FRAME_PIXELS = 250_000_000
MAX_OUTPUT_BYTES = 256 * 1024 * 1024


def _constant_frame_rate(body):
    """Read a single integer expression, never a variable or partial formula.

    Compiled expressions omit their source text; editable projects retain it
    after the same 16-byte constant program. Other encodings use the cache.
    """
    if len(body) < 16:
        return None
    size, kind, source, reserved = struct.unpack_from('<4H', body)
    if (size != len(body) or kind != 2 or reserved != 0
            or source != (16 if len(body) > 16 else 0)
            or body[8:10] != b'\x03\0' or body[14:16] != b'\0\0'):
        return None
    rate = struct.unpack_from('<i', body, 10)[0]
    return rate if 1 <= rate <= 65535 else None


def referenced_animations(context, endian):
    """Map directory entry indices to candidate owners, without adjacency guesses.

    Keep conflicting/invalid candidates so their storage blocks cannot be
    suppressed merely because another animation also references those blocks.
    """
    if endian != '<' or len(context.by_id.get(1, [])) != 1:
        return {}
    root = context.entry(context.by_id[1][0]) or b''
    parsed = legacy_project_root(root, endian)
    if parsed is None:
        return {}
    found = {}
    for group, resources in enumerate(parsed['resource_groups']):
        table_indices = context.by_id.get(resources[1], [])
        if len(table_indices) != 1:
            continue
        table_index = table_indices[0]
        if context.entries[table_index]['icon_type'] != 0x25:
            continue
        data = context.entry(table_index) or b''
        if len(data) < 1028:
            continue
        offsets = struct.unpack_from('<257I', data)
        if offsets[0] != 1028 or tuple(sorted(offsets)) != offsets or offsets[-1] > len(data):
            continue
        for slot, (start, end) in enumerate(zip(offsets, offsets[1:])):
            pos, lists, configs, rates = start, [], [], []
            valid = True
            while pos + 4 <= end:
                tag, length = struct.unpack_from('<HH', data, pos)
                if pos + 4 + length > end:
                    valid = False
                    break
                body = data[pos + 4:pos + 4 + length]
                if tag == 0x23 and length >= 12:
                    count = struct.unpack_from('<I', body)[0]
                    if length == 4 + count * 4:
                        refs = struct.unpack_from('<' + 'I' * count, body, 4)
                        if refs[0] == (25 << 16 | group * 256 + slot):
                            lists.append(list(refs[1:]))
                elif tag == 0x1C and length >= 46:
                    configs.append({'logical_frames': struct.unpack_from('<I', body, 2)[0],
                                    'width': struct.unpack_from('<H', body, 12)[0],
                                    'height': struct.unpack_from('<H', body, 14)[0],
                                    'stored_rate': struct.unpack_from('<H', body, 34)[0]})
                elif tag == 0x3F8:
                    rates.append(_constant_frame_rate(body))
                # Properties are word-aligned. The pad byte is not necessarily
                # zero (A4P/A5P expression properties retain old buffer bytes).
                pos += 4 + length + (length & 1)
                if pos > end:
                    valid = False
            for refs in lists:
                for index in context.by_id.get(refs[0], []):
                    if context.entries[index]['icon_type'] != 0x33:
                        continue
                    candidate = dict(resources=refs, table_id=resources[1], object_id=group * 256 + slot)
                    if valid and len(configs) == 1:
                        candidate.update(configs[0])
                        if len(rates) == 1 and rates[0] is not None:
                            candidate['authored_rate'] = rates[0]
                    else:
                        candidate['error'] = 'Animation owner has incomplete or ambiguous settings'
                    found.setdefault(index, []).append(candidate)
    return found


def referenced_indices(context, candidates):
    """Resources to preserve if any candidate cannot be decoded completely."""
    return {index for owner in candidates for resource_id in owner['resources']
            for index in context.by_id.get(resource_id, [])}


def patch_rle(data, pixels, width, height):
    """Apply a bottom-up RLE8 delta; skipped pixels keep their previous values."""
    stride = (width + 3) & ~3
    x = y = pos = 0
    while pos + 2 <= len(data):
        count, value = data[pos:pos + 2]
        pos += 2
        if count:
            values = bytes([value]) * count
        elif value == 0:
            x, y = 0, y + 1
            if y > height:
                raise ValueError('Animation RLE row exceeds the canvas')
            continue
        elif value == 1:
            if pos != len(data):
                raise ValueError('Unexpected trailing animation RLE data')
            return
        elif value == 2:
            if pos + 2 > len(data):
                raise ValueError('Truncated animation RLE skip')
            dx, dy = data[pos:pos + 2]
            pos += 2
            x, y = x + dx, y + dy
            if x > stride or y >= height:
                raise ValueError('Animation RLE skip exceeds the canvas')
            continue
        else:
            end = pos + value + (value & 1)
            if end > len(data):
                raise ValueError('Truncated animation RLE literal')
            values = data[pos:pos + value]
            pos = end
        if y >= height or x + len(values) > stride:
            raise ValueError('Animation RLE pixels exceed the canvas')
        offset = y * stride + x
        pixels[offset:offset + len(values)] = values
        x += len(values)
    raise ValueError('Missing animation RLE end marker')


def _chunk(tag, content):
    return (struct.pack('>I', len(content)) + tag + content
            + struct.pack('>I', zlib.crc32(tag + content) & 0xffffffff))


def _rgba(pixels, mask, width, height, palette):
    stride = (width + 3) & ~3
    indices = b''.join(pixels[y * stride:y * stride + width] for y in reversed(range(height)))
    rgba = bytearray(width * height * 4)
    rgba[0::4], rgba[1::4], rgba[2::4] = (indices.translate(palette[c::4]) for c in (2, 1, 0))
    rgba[3::4] = (b''.join(mask[y * stride:y * stride + width] for y in reversed(range(height)))
                   if mask is not None else b'\xff' * (width * height))
    return rgba


def _rgb_digest(rgba):
    """Compare colors independently of a sequence's transparency mask."""
    digest = hashlib.sha256()
    for channel in range(3):
        digest.update(rgba[channel::4])
    return digest.digest()


def render_animation(context, index, candidates):
    """Validate and encode the entire animation before permitting raw suppression."""
    if len(candidates) != 1:
        raise ValueError('Missing or ambiguous animation owner')
    owner = candidates[0]
    if owner.get('error'):
        raise ValueError(owner['error'])
    indices = []
    for position, resource_id in enumerate(owner['resources']):
        matches = context.by_id.get(resource_id, [])
        expected = 0x33 if position == 0 else 0x38
        if len(matches) != 1 or context.entries[matches[0]]['icon_type'] != expected:
            raise ValueError('Missing, ambiguous or unsupported animation resource reference')
        indices.append(matches[0])
    if not indices or indices[0] != index:
        raise ValueError('Animation owner references a different directory')
    desc = context.entry(index) or b''
    if len(desc) < 48:
        raise ValueError('Truncated animation directory')
    count, npal, palstride, records, info, info2, colors = struct.unpack_from('<IHH4I', desc)
    if (not 1 <= count <= 10000 or not 1 <= npal <= 256 or palstride != 1024
            or records != 48 or info != records + count * 32 or info2 != info
            or colors != info + 40 or len(desc) != colors + npal * 1536):
        raise ValueError('Unsupported or incomplete animation directory layout')
    size, width, height, planes, bpp, _, _, _, _, ncolors, _ = struct.unpack_from('<IiiHHIIiiII', desc, info)
    if size != 40 or planes != 1 or bpp != 8 or ncolors != 256 or width <= 0 or height <= 0:
        raise ValueError('Unsupported animation bitmap format')
    if width * height > MAX_CANVAS_PIXELS or width * height * count > MAX_FRAME_PIXELS:
        raise ValueError('Animation exceeds decoding size limits')
    frames = [struct.unpack_from('<H4hHHIIHII', desc, records + frame * 32) for frame in range(count)]
    loop_back = bool(frames[-1][0] & 0x10)
    display_count = count - int(loop_back)
    if (not display_count or
            (owner['logical_frames'], owner['width'], owner['height']) != (display_count, width, height)):
        raise ValueError('Animation dimensions or frame count disagree with its owner')
    rate = owner.get('authored_rate', owner['stored_rate'])
    rate_source = 'authored' if 'authored_rate' in owner else 'cached'
    if not 1 <= rate <= 65535:
        raise ValueError('Animation has no usable stored playback rate')
    masked = bool(frames[0][0] & 2)
    for frame, record in enumerate(frames):
        flags = record[0]
        if (flags & ~0x73 or (frame == 0 and not flags & 0x40)
                or (flags & 0x10 and frame != count - 1) or bool(flags & 2) != masked):
            raise ValueError('Unsupported animation frame flags or sequence')
    missing_masks = masked and all(record[9:] == (0, 0, 0) for record in frames)
    warnings = (['Transparency flag is set but no masks are stored; frames exported as opaque.']
                if missing_masks else [])
    palettes = [desc[colors + p * 1024:colors + (p + 1) * 1024] for p in range(npal)]
    pixels = bytearray(((width + 3) & ~3) * height)
    mask = bytearray(len(pixels)) if masked and not missing_masks else None
    cache, consumed = {}, {index}

    def payload(number, start, length):
        if not 2 <= number <= len(indices) or not length:
            raise ValueError('Invalid animation data block number or length')
        resource_index = indices[number - 1]
        if resource_index not in cache:
            cache[resource_index] = context.entry(resource_index)
        content = cache[resource_index]
        if content is None or start + length > len(content):
            raise ValueError('Animation data range is missing or truncated')
        consumed.add(resource_index)
        return content[start:start + length]

    result = bytearray(b'\x89PNG\r\n\x1a\n')
    result += _chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
    result += _chunk(b'acTL', struct.pack('>II', display_count, 0))
    rate_note = ('the authored constant rate' if rate_source == 'authored' else
                 'the cached rate as a fallback (no supported constant playback rate)')
    note = (f'Playback uses {rate_note}, {rate} frames per second, and repeats the full sequence; '
            'runtime scripts are not replayed.')
    result += _chunk(b'tEXt', b'Comment\0' + (' '.join([note] + warnings)).encode('ascii'))
    palette_index, sequence, first, first_colors = 0, 0, None, None
    for frame, record in enumerate(frames):
        flags, _, _, _, _, palindex, block, off, length, mblock, moff, mlength = record
        if flags & 0x20:
            palette_index = palindex
        if palette_index >= npal:
            raise ValueError('Animation palette reference is outside the directory')
        if flags & 0x40:
            # This marks an independent/key frame, not just the first frame.
            # Some sequences have only key frames and no loop-back record.
            pixels[:] = b'\0' * len(pixels)
            if mask is not None:
                mask[:] = b'\0' * len(mask)
        content = payload(block, off, length)
        if flags & 1:
            patch_rle(content, pixels, width, height)
        else:
            if len(content) != len(pixels):
                raise ValueError('Incomplete raw animation pixel plane')
            pixels[:] = content
        if mask is not None:
            patch_rle(payload(mblock, moff, mlength), mask, width, height)
            if mask.count(0) + mask.count(255) != len(mask):
                raise ValueError('Unsupported non-binary animation mask')
        elif (mblock, moff, mlength) != (0, 0, 0):
            raise ValueError('Unexpected animation mask reference without mask flag')
        rgba = _rgba(pixels, mask, width, height, palettes[palette_index])
        digest = hashlib.sha256(rgba).digest()
        if frame == 0:
            first = digest
            if loop_back and mask is not None:
                first_colors = _rgb_digest(rgba)
        if loop_back and frame == count - 1:
            if digest != first:
                if mask is None or _rgb_digest(rgba) != first_colors:
                    raise ValueError('Animation loop-back does not restore its first frame')
                # Some A5R sequences restore every color but leave a different
                # mask after the first pass. All display frames are recoverable;
                # an APNG repeats that first pass rather than inventing a mask.
                warning = ('Stored loop-back changes transparency; APNG repeats the recovered first-pass frames.')
                warnings.append(warning)
                result += _chunk(b'tEXt', b'Warning\0' + warning.encode('ascii'))
            break  # Restoration record, not an extra display frame/dwell.
        result += _chunk(b'fcTL', struct.pack('>IIIIIHHBB', sequence, width, height, 0, 0, 1, rate, 0, 0))
        sequence += 1
        rowbytes = width * 4
        filtered = b''.join(b'\0' + rgba[y * rowbytes:(y + 1) * rowbytes] for y in range(height))
        compressed = zlib.compress(filtered)
        if frame:
            result += _chunk(b'fdAT', struct.pack('>I', sequence) + compressed)
            sequence += 1
        else:
            result += _chunk(b'IDAT', compressed)
        if len(result) > MAX_OUTPUT_BYTES:
            raise ValueError('Animation exceeds encoded size limit')
    result += _chunk(b'IEND', b'')
    return {'apng': bytes(result), 'width': width, 'height': height, 'frames': display_count,
            'stored_rate': owner['stored_rate'], 'playback_rate': rate, 'rate_source': rate_source,
            'warnings': warnings, 'timing_note': note,
            'status': 'partial' if warnings else 'converted', 'consumed_indices': sorted(consumed),
            'owner': owner, 'transparency': mask is not None}

#!/usr/bin/env python3
# Vibe coded by Codex
"""Extract the complete stored PCM waveform from CAT/REX2 files.

Python 3.9+; standard library only. See rex2AudioSampleLoop.txt for the
verified format, byte-level interpretation, and explicit remaining unknowns.
This extracts source audio; it does not emulate ReCycle's playback effects.
"""

import argparse
import array
import hashlib
import json
from pathlib import Path
import struct
import sys


class RexError(Exception):
    """A file cannot safely be converted."""


class Unsupported(RexError):
    """Not REX2, or an unsupported REX2 encoding/version."""


def u32(data, offset=0):
    return struct.unpack_from('>I', data, offset)[0]


def read_version(data, offset):
    """Read the five-byte version record, or its explicit 29-byte extension."""
    if offset+5 > len(data) or data[offset] != 0xbc:
        raise RexError('missing or truncated version record')
    if data[offset+1:offset+5] == b'\xff'*4:
        if offset+29 > len(data):
            raise RexError('truncated extended version record')
        fields = struct.unpack_from('>6I', data, offset+5)
        version = dict(zip(('major', 'minor', 'revision', 'stage',
                            'stage_number', 'build'), fields))
        if version['stage'] not in (1, 2, 3, 4):
            raise RexError('invalid extended version stage')
        end = offset+29
    else:
        version = dict(major=data[offset+1], minor=data[offset+2],
                       revision=data[offset+3], reserved=data[offset+4],
                       stage=4, stage_number=0, build=0)
        end = offset+5
    version['raw_hex'] = data[offset:end].hex()
    return version, end


def read_string(data, offset):
    """Length-prefixed Windows-1252, or explicitly marked versioned UTF-8."""
    if offset+4 > len(data):
        raise RexError('truncated cross-platform string length')
    length = u32(data, offset)
    pos = offset+4
    encoding = 'cp1252'
    version = None
    if length == 0xffffffff:
        version, pos = read_version(data, pos)
        if version['major'] != 1 or version['minor'] != 0:
            raise RexError('unsupported cross-platform string version')
        if pos+4 > len(data):
            raise RexError('truncated UTF-8 string length')
        length = u32(data, pos)
        pos += 4
        encoding = 'utf-8'
    raw = data[pos:pos+length]
    if len(raw) != length:
        raise RexError('truncated cross-platform string content')
    # Backslash escapes preserve undefined Windows-1252 bytes diagnostically.
    record = dict(byte_length=length, encoding=encoding, raw_hex=raw.hex(),
                  text=raw.decode(encoding, errors='backslashreplace'))
    if version is not None:
        record['version'] = version
    return record, pos+length


def inspect_rex(data):
    """Parse declared chunk boundaries, never scan for plausible signatures.

    Return an audit dictionary and SDAT bytes. Every physical byte belongs to
    a header, type, payload, alignment byte, or explicitly reported remainder.
    Metadata damage is nonfatal when unambiguous audio parameters survive.
    """
    data = bytes(data)
    if len(data) < 12 or data[:4] != b'CAT ' or data[8:12] != b'REX2':
        raise Unsupported('not a CAT / REX2 file (extension is irrelevant)')
    result = {'input_bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
              'chunks': [], 'warnings': [], 'metadata': {}, 'slices': []}
    warnings = result['warnings']
    chunks = {}
    known = {b'HEAD', b'CREI', b'GLOB', b'RECY', b'RCYX', b'TRSH',
             b'EQ  ', b'COMP', b'SLCE', b'SINF', b'SDAT'}

    def walk(start, end, parent, depth=0):
        if depth > 32:
            raise RexError('container nesting exceeds the supported limit of 32')
        pos = start
        while pos < end:
            if end - pos < 8:
                result['chunks'].append({'offset': pos, 'length': end-pos,
                                         'kind': 'incomplete_header',
                                         'raw_hex': data[pos:end].hex()})
                warnings.append(f'incomplete chunk header at {pos}')
                return
            tag = data[pos:pos+4]
            size = u32(data, pos+4)
            body = pos+8
            stop = min(body+size, end)
            raw = data[body:stop]
            item = {'tag': tag.decode('latin1'), 'parent': parent,
                    'offset': pos, 'payload_offset': body,
                    'declared_size': size, 'available_size': len(raw)}
            result['chunks'].append(item)
            if body+size > end:
                warnings.append(f'{tag!r} at {pos}: payload truncated by {body+size-end} bytes')
            if tag == b'CAT ':
                if len(raw) < 4:
                    warnings.append(f'truncated container type at {body}')
                    item['raw_hex'] = raw.hex()
                else:
                    kind = raw[:4].decode('latin1')
                    item['container_type'] = kind
                    if kind not in ('REX2', 'DEVL', 'SLCL'):
                        raise Unsupported(f'unsupported REX2 container type {kind!r}')
                    if depth and kind == 'REX2':
                        raise Unsupported('multiple nested REX2 waveforms are unsupported')
                    walk(body+4, stop, kind, depth+1)
            else:
                if tag not in known:
                    raise Unsupported(f'unsupported REX2 chunk {tag!r} at {pos}')
                chunks.setdefault(tag, []).append(raw)
                if tag != b'SDAT':
                    item['raw_hex'] = raw.hex()
                else:
                    item['sha256'] = hashlib.sha256(raw).hexdigest()
            pos = stop
            if size & 1 and body+size <= end:
                if pos < end:
                    item['padding_offset'] = pos
                    item['padding_hex'] = data[pos:pos+1].hex()
                    if data[pos]:
                        warnings.append(f'nonzero IFF alignment byte at {pos}')
                    pos += 1
                else:
                    warnings.append(f'missing IFF alignment byte after {tag!r}')

    declared_end = 8 + u32(data, 4)
    if declared_end < 12:
        raise RexError('REX2 root size does not include its type')
    walk(0, min(declared_end, len(data)), '')
    if declared_end > len(data):
        warnings.append(f'root truncated by {declared_end-len(data)} bytes')
    elif declared_end < len(data):
        result['trailing_bytes'] = {'offset': declared_end,
                                    'raw_hex': data[declared_end:].hex()}
        warnings.append('bytes after the root container are uninterpreted')

    def one(tag, required=False):
        items = chunks.get(tag, [])
        if len(items) > 1:
            raise RexError(f'ambiguous duplicate {tag!r} chunks')
        if not items and required:
            raise RexError(f'missing required {tag!r} chunk')
        return items[0] if items else None

    head = one(b'HEAD', True)
    if len(head) < 9:
        raise RexError('truncated HEAD: cannot establish the encoding version')
    if head[:4] != bytes.fromhex('490cf18d'):
        warnings.append('damaged HEAD magic; using the REX2 root, version, and SINF for recovery')
    version, uuid_pos = read_version(head, 4)
    if (version['major'] not in (1, 2, 3) or version['minor'] != 0
            or version['revision'] != 0 or version['stage'] != 4):
        raise Unsupported(f'unsupported REX2 version record {version["raw_hex"]}')
    meta = result['metadata']
    meta['HEAD'] = {'magic': head[:4].hex(), 'version_record': version['raw_hex'],
                    'version': version, 'uuid_hex': head[uuid_pos:uuid_pos+16].hex()}
    if len(head) < uuid_pos+20:
        warnings.append('truncated HEAD UUID/obsolete filename; audio remains decodable')
    else:
        try:
            name, pos = read_string(head, uuid_pos+16)
            meta['HEAD']['obsolete_filename'] = name
            if pos != len(head):
                warnings.append('HEAD has bytes after its obsolete filename')
        except RexError as error:
            warnings.append(f'HEAD filename: {error}')
    if any(head[uuid_pos:uuid_pos+16]):
        raise Unsupported('nonzero HEAD UUID: alternate header semantics are unverified')

    sinf = one(b'SINF', True)
    if len(sinf) < 10:
        raise RexError('SINF is too short to recover audio parameters')
    channels, code, rate, frames = struct.unpack_from('>BBII', sinf)
    if channels not in (1, 2) or code not in (3, 5):
        raise Unsupported(f'unsupported SINF channels={channels}, sample format={code}')
    width = {3: 2, 5: 3}[code]
    if not rate or rate * channels * width > 0xffffffff:
        raise RexError('invalid sample rate; refusing to guess a replacement')
    loop_start, loop_end = (struct.unpack_from('>II', sinf, 10)
                            if len(sinf) >= 18 else (None, None))
    meta['SINF'] = dict(channels=channels, format_code=code, sample_rate=rate,
                        frames=frames, loop_start=loop_start, loop_end=loop_end)
    result.update(channels=channels, sample_width=width, sample_rate=rate,
                  declared_frames=frames)
    if len(sinf) != 18:
        warnings.append('SINF payload is not 18 bytes; loop metadata may be incomplete')
    if loop_start is not None and not 0 <= loop_start <= loop_end <= frames:
        warnings.append('invalid loop bounds; extracting the stored waveform')

    formats = {
        b'GLOB': ('>IHBBBBHHhIBB', ('slice_count', 'bars', 'extra_beats',
            'time_signature_numerator', 'time_signature_denominator',
            'sensitivity', 'gate', 'gain', 'pitch', 'tempo_millibpm',
            'transmit_as_slices', 'silence_selected')),
        b'TRSH': ('>BHHH', ('enabled', 'attack', 'decay', 'stretch')),
        b'EQ  ': ('>BHHhHHhHH', ('enabled', 'low_cut_hz', 'low_frequency_hz',
            'low_gain', 'low_q', 'high_frequency_hz', 'high_gain',
            'high_q', 'high_cut_hz')),
        b'COMP': ('>BHHHH', ('enabled', 'threshold', 'ratio', 'attack', 'release')),
    }
    for tag, (fmt, names) in formats.items():
        raw = one(tag)
        if raw is None:
            continue
        size = struct.calcsize(fmt)
        if len(raw) >= size:
            meta[tag.decode('ascii').strip()] = dict(zip(names, struct.unpack_from(fmt, raw)))
        if len(raw) != size:
            warnings.append(f'{tag!r} size {len(raw)} differs from {size}; raw bytes retained in audit')

    raw = one(b'RECY')
    if raw is not None:
        try:
            version, pos = read_version(raw, 0)
            if len(raw) != pos+10:
                raise RexError('unexpected payload length')
            meta['RECY'] = {'version': version, 'preview_play': raw[pos],
                'ruler_unit': raw[pos+1], 'exported_bytes': u32(raw, pos+2),
                'exported_slice_count': u32(raw, pos+6)}
        except RexError as error:
            warnings.append(f'RECY: {error}; raw bytes retained in audit')
    raw = one(b'RCYX')
    if raw is not None:
        try:
            version, pos = read_version(raw, 0)
            if (version['major'], version['minor']) != (1, 0) or len(raw) != pos+16:
                raise RexError('unrecognized editor extension version/length')
            values = struct.unpack_from('>IBBBIIB', raw, pos)
            fields = dict(zip(('editor_enum', 'editor_bool_1', 'editor_bool_2',
                               'editor_bool_3', 'editor_u32_1', 'editor_u32_2',
                               'editor_bool_4'), values))
            meta['RCYX'] = dict(version=version, **fields)
            meta['RCYX']['interpretation'] = 'field types verified; editor meanings unresolved'
        except RexError as error:
            warnings.append(f'RCYX: {error}; raw bytes retained in audit')

    raw = one(b'CREI')
    if raw is not None:
        pos = 0
        creator = {}
        for name in ('name', 'copyright', 'url', 'email', 'free_text'):
            try:
                creator[name], pos = read_string(raw, pos)
            except RexError as error:
                warnings.append(f'CREI {name}: {error}')
                break
        if pos != len(raw):
            warnings.append('CREI length-prefixed strings do not consume the payload')
        meta['CREI'] = creator

    for i, raw in enumerate(chunks.get(b'SLCE', [])):
        if len(raw) == 11:
            start, length, points, flags = struct.unpack('>IIHB', raw)
            result['slices'].append(dict(start=start, length=length, points=points,
                flags=flags, muted=bool(flags & 1), locked=bool(flags & 2),
                selected=bool(flags & 4)))
            if start > frames or length > frames-start:
                warnings.append(f'SLCE {i} extends beyond the stored waveform')
            if flags & 0xf8:
                warnings.append(f'SLCE {i} contains unrecognized flag bits')
        else:
            warnings.append(f'SLCE {i} has unsupported length {len(raw)}')
    if 'GLOB' in meta and meta['GLOB']['slice_count'] != len(chunks.get(b'SLCE', [])):
        warnings.append('GLOB slice count disagrees with the SLCE record count')
    payload = one(b'SDAT', True)
    return result, payload


class BitReader:
    """MSB-first bit reader with exact consumption and real EOF detection."""
    def __init__(self, data):
        self.data = data
        self.pos = 0
        self.buffer = 0
        self.left = 0

    def read(self, count):
        if count == 0:
            return 0
        while self.left < count:
            if self.pos >= len(self.data):
                raise RexError('compressed audio ends inside a coded sample')
            part = self.data[self.pos:self.pos+4]
            self.pos += len(part)
            self.buffer = (self.buffer << (len(part)*8)) | int.from_bytes(part, 'big')
            self.left += len(part)*8
        self.left -= count
        value = self.buffer >> self.left
        self.buffer &= (1 << self.left)-1
        return value

    @property
    def consumed(self):
        return self.pos*8-self.left


def decode_dwop(payload, frames, channels, width):
    """Return PCM bytes and a bit audit, salvaging only complete frames.

    Predictor equations agree with the public-domain VelociLoops implementation
    and independently published DWOP descriptions. All state arithmetic is
    explicitly 32-bit. The range width is computed directly from the step;
    this is algebraically identical to the adaptive j/rbits state machine.
    """
    reader = BitReader(payload)
    read = reader.read
    states = [[0]*5 for _ in range(channels)]
    energies = [[2560]*5 for _ in range(channels)]
    pcm = array.array('i')
    low, high = -(1 << (width*8-1)), (1 << (width*8-1))-1
    completed_bits = 0
    problem = None
    clipped = 0
    try:
        for frame in range(frames):
            outputs = []
            for channel in range(channels):
                energy = energies[channel]
                order = 0
                best = energy[0]
                for i in range(1, 5):
                    if energy[i] < best:
                        best, order = energy[i], i
                step = ((best*3+36) & 0xffffffff) >> 7
                if not step:
                    raise RexError('invalid zero entropy step')
                acc = 0
                zeros = 0
                while read(1) == 0:
                    acc += step
                    zeros += 1
                    if acc > 0xffffffff:
                        raise RexError('compressed residual prefix overflows 32 bits')
                    if zeros % 7 == 0:
                        step <<= 2
                        if step > 0x7fffffff:
                            raise RexError('compressed residual step overflows supported range')
                bits = step.bit_length()-1
                remainder = read(bits)
                threshold = (1 << (bits+1))-step
                if remainder >= threshold:
                    remainder = 2*remainder-threshold+read(1)
                code = acc+remainder
                if code > 0xffffffff:
                    raise RexError('compressed residual exceeds 32 bits')
                delta = code ^ -(code & 1)
                delta = ((delta+0x80000000) & 0xffffffff)-0x80000000
                old = states[channel]
                new = [0]*5
                new[order] = delta
                for i in range(order-1, -1, -1):
                    new[i] = ((old[i]+new[i+1]+0x80000000) & 0xffffffff)-0x80000000
                for i in range(order+1, 5):
                    new[i] = ((new[i-1]-old[i-1]+0x80000000) & 0xffffffff)-0x80000000
                states[channel] = new
                for i in range(5):
                    energy[i] = (energy[i]+(new[i] ^ (new[i] >> 31))-(energy[i] >> 5)) & 0xffffffff
                outputs.append(new[0] >> 1)
            if channels == 2:
                outputs[1] += outputs[0]
            for value in outputs:
                if value < low or value > high:
                    clipped += 1
                    value = max(low, min(high, value))
                pcm.append(value)
            completed_bits = reader.consumed
    except RexError as error:
        problem = str(error)
    decoded = len(pcm)//channels
    audit = {'decoded_frames': decoded, 'coded_bits': completed_bits,
             'attempted_bits': reader.consumed, 'sdat_bytes': len(payload),
             'clipped_samples': clipped, 'error': problem}
    if problem is None:
        remaining = len(payload)*8-completed_bits
        byte_pos, bit_pos = divmod(completed_bits, 8)
        nonzero = bool(bit_pos and payload[byte_pos] & ((1 << (8-bit_pos))-1))
        nonzero = nonzero or any(payload[byte_pos+bool(bit_pos):])
        audit.update(tail_bits=remaining, tail_zero=not nonzero,
                     word_padding_bits=(-completed_bits) % 32,
                     word_aligned=(len(payload) % 4 == 0),
                     extra_zero_words=(remaining-(-completed_bits) % 32)//32,
                     tail_offset=byte_pos, tail_hex=payload[byte_pos:].hex())
    if sys.byteorder != 'little':
        pcm.byteswap()
    packed = pcm.tobytes()
    # Strided byte copies retain the low 16 or 24 bits without float conversion.
    output = bytearray(len(pcm)*width)
    for i in range(width):
        output[i::width] = packed[i::4]
    return bytes(output), audit


def decode_file(input_file):
    source = Path(input_file)
    # Check the signature before allocating or reading a foreign file in full.
    with source.open('rb') as stream:
        signature = stream.read(12)
        if len(signature) < 12 or signature[:4] != b'CAT ' or signature[8:] != b'REX2':
            raise Unsupported('not a CAT / REX2 file (extension is irrelevant)')
        data = signature + stream.read()
    info, payload = inspect_rex(data)
    pcm, codec = decode_dwop(payload, info['declared_frames'],
                              info['channels'], info['sample_width'])
    info['codec'] = codec
    if codec['error']:
        info['warnings'].append(f"salvaged {codec['decoded_frames']} complete frames: {codec['error']}")
    if codec['clipped_samples']:
        info['warnings'].append(f"{codec['clipped_samples']} out-of-range samples clipped (damaged stream)")
    if not codec['error'] and (not codec['tail_zero'] or not codec['word_aligned']
                              or codec['extra_zero_words'] not in (0, 1)):
        info['warnings'].append('unexpected SDAT suffix; audio count decoded, suffix is uninterpreted')
    if not pcm:
        raise RexError('no complete audio frames could be recovered')
    return info, pcm


def write_outputs(input_file, output_dir, info, pcm, verbose=False):
    """Write only after identification and decoding; preserve existing files."""
    size = len(pcm)
    riff_size = 36+size+(size & 1)
    if riff_size > 0xffffffff:
        raise RexError('decoded waveform exceeds the 32-bit RIFF/WAV size limit')
    block = info['channels']*info['sample_width']
    header = struct.pack('<4sI4s4sIHHIIHH4sI', b'RIFF', riff_size, b'WAVE',
                         b'fmt ', 16, 1, info['channels'], info['sample_rate'],
                         info['sample_rate']*block, block, info['sample_width']*8,
                         b'data', size)
    directory = Path(output_dir)
    new_parents = []
    ancestor = directory
    while not ancestor.exists():
        new_parents.append(ancestor)
        ancestor = ancestor.parent
    directory.mkdir(parents=True, exist_ok=True)
    for parent in new_parents:
        parent.chmod(parent.stat().st_mode | 0o550)
    stem = Path(input_file).stem or 'audio'
    number = 0
    while True:
        suffix = '' if number == 0 else f'.{number}'
        target = directory / (stem+suffix+'.wav')
        if verbose and target.with_name(target.name+'.json').exists():
            number += 1
            continue
        try:
            stream = target.open('xb')
            break
        except FileExistsError:
            number += 1
    try:
        with stream:
            stream.write(header)
            stream.write(pcm)
            if size & 1:
                stream.write(b'\0')
        target.chmod(target.stat().st_mode | 0o440)
    except BaseException:
        target.unlink(missing_ok=True)
        raise
    if verbose:
        sidecar = target.with_name(target.name+'.json')
        # Never overwrite a pre-existing user sidecar.
        with sidecar.open('x', encoding='utf-8') as out:
            json.dump(info, out, ensure_ascii=True, indent=2)
            out.write('\n')
        sidecar.chmod(sidecar.stat().st_mode | 0o440)
    return target


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('inputFile', type=Path)
    parser.add_argument('outputDir', type=Path)
    parser.add_argument('-verbose', '--verbose', action='store_true',
                        help='also write a byte/chunk/codec audit as WAV-name.json')
    args = parser.parse_args(argv)
    try:
        info, pcm = decode_file(args.inputFile)
        target = write_outputs(args.inputFile, args.outputDir, info, pcm, args.verbose)
    except (RexError, OSError, ValueError, struct.error, OverflowError) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 1
    for warning in info['warnings']:
        print(f'Warning: {warning}', file=sys.stderr)
    print(target)
    return 0


if __name__ == '__main__':
    sys.exit(main())

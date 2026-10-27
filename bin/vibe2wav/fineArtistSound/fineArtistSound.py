#!/usr/bin/env python3
# Vibe coded by Codex
"""Extract CHNK v4 Fine Artist / Creative Writer sound libraries to PCM WAV.

Usage: fineArtistSound.py [-verbose] inputFile outputDir
Only WAV files are written unless -verbose requests a JSON byte/structure audit.
See fineArtistSound.txt for the supported profile and unresolved metadata.
"""
from __future__ import annotations

import argparse
import array
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import sys
from dataclasses import dataclass, field


class FormatError(ValueError):
    """The input cannot be identified or decoded as the supported sound format."""


ADAPTATION = (230, 230, 230, 230, 307, 409, 512, 614,
              768, 614, 512, 409, 307, 230, 230, 230)
END = 0xFFFFFFFF


@dataclass
class Sound:
    resource: dict
    sample_rate: int
    channels: int
    pcm: bytes
    loop: bytes | None
    metadata: dict
    filename: str = ""

    @property
    def frames(self):
        return len(self.pcm) // (2 * self.channels)


@dataclass
class Library:
    data: bytes
    endian: str
    header: dict = field(default_factory=dict)
    records: list = field(default_factory=list)
    resources: list = field(default_factory=list)
    sounds: list = field(default_factory=list)
    categories: list = field(default_factory=list)
    spans: list = field(default_factory=list)
    issues: list = field(default_factory=list)
    skipped: list = field(default_factory=list)

    def issue(self, message):
        self.issues.append(message)

    def span(self, start, end, kind, **detail):
        start, end = max(0, start), min(len(self.data), end)
        if end > start:
            self.spans.append(dict(offset=start, length=end-start,
                                   kind=kind, **detail))

    def audit(self):
        """Partition the entire input; overlapping ownership is explicit."""
        events = {}
        for i, span in enumerate(self.spans):
            start, end = span['offset'], span['offset'] + span['length']
            events.setdefault(start, []).append((i, True))
            events.setdefault(end, []).append((i, False))
        events.setdefault(0, [])
        events.setdefault(len(self.data), [])
        active, ranges, previous = set(), [], 0
        for point in sorted(events):
            if point > previous:
                raw = self.data[previous:point]
                owners = [self.spans[i] for i in sorted(active)]
                item = dict(offset=previous, length=point-previous,
                            owners=owners or [{'kind': 'unreferenced_storage'}],
                            sha256=hashlib.sha256(raw).hexdigest())
                # Unallocated bytes and metadata are kept byte-exact in verbose
                # output, including nonzero alignment bytes and stale storage.
                if not owners or all(s['kind'] != 'encoded_audio' for s in owners):
                    item['hex'] = raw.hex()
                ranges.append(item)
            for i, adding in events[point]:
                if adding:
                    active.add(i)
                else:
                    active.discard(i)
            previous = point
        return ranges


def unpack(fmt, data, offset=0, endian='<'):
    size = struct.calcsize(endian + fmt)
    if offset < 0 or offset + size > len(data):
        raise FormatError(f'truncated {fmt} field at offset 0x{offset:x}')
    return struct.unpack_from(endian + fmt, data, offset)


def decode_adpcm(data, channels, block_align, samples_per_block, coefficients):
    """MS ADPCM: LE block headers, high nibble first, C division semantics.

    Return PCM and diagnostics. A damaged block does not invalidate subsequent
    blocks, whose boundaries and predictor histories are independently known.
    """
    header_size = 7 * channels
    if channels not in (1, 2) or block_align < header_size:
        raise FormatError('invalid ADPCM channel count or block alignment')
    capacity = 2 + (block_align - header_size) * 2 // channels
    if not (2 <= samples_per_block <= capacity):
        raise FormatError('ADPCM samples-per-block exceeds block capacity')
    if not coefficients:
        raise FormatError('ADPCM coefficient table is empty')
    output, diagnostics = array.array('h'), []
    for offset in range(0, len(data), block_align):
        block = data[offset:offset + block_align]
        if len(block) < header_size:
            diagnostics.append(f'ADPCM block +0x{offset:x}: discarded '
                               f'{len(block)} bytes of incomplete header')
            continue
        predictors = list(block[:channels])
        if any(p >= len(coefficients) for p in predictors):
            diagnostics.append(f'ADPCM block +0x{offset:x}: invalid predictor; '
                               'block skipped')
            continue
        delta = list(unpack('h' * channels, block, channels))
        recent = list(unpack('h' * channels, block, 3 * channels))
        older = list(unpack('h' * channels, block, 5 * channels))
        if any(d < 0 for d in delta):
            diagnostics.append(f'ADPCM block +0x{offset:x}: negative step size; '
                               'block skipped')
            continue
        output.extend(older)
        output.extend(recent)
        available_frames = 2 + 2 * (len(block) - header_size) // channels
        count = (min(available_frames, samples_per_block) - 2) * channels
        for n in range(count):
            channel = n % channels
            packed = block[header_size + n // 2]
            nibble = packed >> 4 if n % 2 == 0 else packed & 15
            c1, c2 = coefficients[predictors[channel]]
            numerator = recent[channel] * c1 + older[channel] * c2
            prediction = (abs(numerator) // 256) * (-1 if numerator < 0 else 1)
            signed = nibble - 16 if nibble & 8 else nibble
            sample = max(-32768, min(32767, prediction + signed * delta[channel]))
            older[channel], recent[channel] = recent[channel], sample
            delta[channel] = max(16, ADAPTATION[nibble] * delta[channel] // 256)
            output.append(sample)
    if sys.byteorder != 'little':
        output.byteswap()
    return output.tobytes(), diagnostics


def parse_sound(lib, resource, data):
    base, e = resource['offset'], lib.endian
    if len(data) < 12:
        raise FormatError('sound is missing its RIFF/WAVE header')
    expected = (b'RIFF', b'WAVE') if e == '<' else (b'FFIR', b'EVAW')
    if (data[:4], data[8:12]) != expected:
        raise FormatError('SND / PCM resource is not the expected RIFF/WAVE variant')
    declared = unpack('I', data, 4, e)[0] + 8
    if declared != len(data):
        lib.issue(f"sound {resource['id']}: RIFF length {declared}, available {len(data)}")
    limit = min(declared, len(data))
    if limit < 12:
        raise FormatError('RIFF length excludes its WAVE type')
    lib.span(base, base+12, 'wave_header', resource=resource['index'])
    pos, parts, part_info = 12, {}, []
    while pos < limit:
        if limit-pos < 8:
            lib.span(base+pos, base+limit, 'truncated_wave_chunk_header')
            lib.issue(f"sound {resource['id']}: incomplete final RIFF chunk header")
            break
        raw_tag = data[pos:pos+4]
        tag = raw_tag if e == '<' else raw_tag[::-1]
        size = unpack('I', data, pos+4, e)[0]
        stop = min(pos+8+size, limit)
        payload = data[pos+8:stop]
        lib.span(base+pos, base+pos+8, 'wave_chunk_header',
                 tag=tag.decode('latin1'), declared_length=size)
        lib.span(base+pos+8, base+stop,
                 'encoded_audio' if tag == b'data' else 'wave_chunk_payload',
                 tag=tag.decode('latin1'), resource=resource['index'])
        part_info.append(dict(tag=tag.decode('latin1'), offset=pos,
                              declared_length=size, available_length=len(payload)))
        if tag in parts:
            raise FormatError(f'duplicate {tag!r} WAVE chunk')
        parts[tag] = payload
        if stop < pos+8+size:
            lib.issue(f"sound {resource['id']}: truncated {tag!r} chunk")
            break
        # This legacy serialization uses packed chunk lengths, without the
        # conventional RIFF pad byte after an odd payload length.
        pos = stop
    if limit < len(data):
        lib.span(base+limit, base+len(data), 'sound_bytes_outside_riff')
        lib.issue(f"sound {resource['id']}: bytes outside declared RIFF boundary")
    if b'fmt ' not in parts or b'data' not in parts:
        raise FormatError('sound is missing a fmt or data chunk')
    fmt = parts[b'fmt ']
    tag, channels, rate, average, align, bits = unpack('HHIIHH', fmt, 0, e)
    if channels not in (1, 2) or (tag, bits) not in ((2, 4), (1, 8), (1, 16)):
        raise FormatError(f'unsupported audio format: tag={tag}, '
                          f'bits={bits}, channels={channels}')
    if rate == 0 or rate > 0xffffffff // (2 * channels):
        raise FormatError('invalid sample rate')
    cb_size, samples, coefficients = None, None, []
    diagnostics = []
    if tag == 2:
        cb_size, samples, count = unpack('HHH', fmt, 16, e)
        if len(fmt) < 22 + 4*count:
            raise FormatError('truncated ADPCM coefficient table')
        coefficients = [unpack('hh', fmt, 22+4*i, e) for i in range(count)]
        if len(fmt) != 22+4*count:
            lib.issue(f"sound {resource['id']}: extra fmt bytes retained in audit")
        # The legacy writer uses 60 despite storing 32 extension bytes.
        if cb_size not in (len(fmt)-18, 60):
            lib.issue(f"sound {resource['id']}: inconsistent fmt extension size {cb_size}")
        pcm, diagnostics = decode_adpcm(parts[b'data'], channels, align, samples, coefficients)
    else:
        frame_size = channels * bits // 8
        if align != frame_size:
            raise FormatError('PCM block alignment disagrees with sample format')
        raw = parts[b'data']
        if len(raw) % frame_size:
            diagnostics.append('incomplete final PCM frame discarded')
        raw = raw[:len(raw)//frame_size*frame_size]
        # Like ADPCM, waveform bytes stay Windows-compatible on both platforms.
        if bits == 16:
            pcm = raw
        else:
            values = array.array('h', ((value-128)*256 for value in raw))
            if sys.byteorder != 'little':
                values.byteswap()
            pcm = values.tobytes()
    for message in diagnostics:
        lib.issue(f"sound {resource['id']}: {message}")
    if not pcm:
        raise FormatError('no complete decodable audio frames')
    fact = None
    if b'fact' in parts:
        fact = unpack('I', parts[b'fact'], 0, e)[0]
        if fact <= len(pcm) // (2*channels):
            pcm = pcm[:fact*2*channels]
        else:
            lib.issue(f"sound {resource['id']}: fact count exceeds recoverable audio")
    loop, loop_fields = None, None
    if b'loop' in parts:
        raw = parts[b'loop']
        if len(raw) != 10:
            lib.issue(f"sound {resource['id']}: unsupported loop metadata length; "
                      'audio retained, metadata available in verbose audit')
        else:
            loop_fields = unpack('IIH', raw, 0, e)
            loop = struct.pack('<IIH', *loop_fields)
            if loop_fields[2] > 127:
                lib.issue(f"sound {resource['id']}: base MIDI note outside 0..127; retained")
    unknown = [t.decode('latin1') for t in parts if t not in (b'fmt ', b'loop', b'data', b'fact')]
    if unknown:
        lib.issue(f"sound {resource['id']}: uninterpreted WAVE chunks: {unknown}")
    info = dict(codec='Microsoft ADPCM' if tag == 2 else 'PCM', format_tag=tag, bits=bits,
                average_bytes_per_second=average, block_align=align,
                extension_size=cb_size, samples_per_block=samples,
                coefficients=coefficients, loop_fields=loop_fields,
                loop_start=loop_fields[0] if loop_fields else None,
                loop_end=loop_fields[1] if loop_fields else None,
                base_midi_note=loop_fields[2] if loop_fields else None,
                fact_frames=fact, chunks=part_info,
                encoded_bytes=len(parts[b'data']),
                blocks=(len(parts[b'data'])+align-1)//align,
                final_block_bytes=len(parts[b'data']) % align or align)
    return Sound(resource, rate, channels, pcm, loop, info)


def parse_library(data):
    """Parse only explicit directory pointers; never scan for audio signatures."""
    if len(data) < 32 or data[:4] != b'CHNK':
        raise FormatError('not a CHNK v4 Fine Artist sound library')
    if data[8:12] == b'\x04\x00\x04\x00':
        e = '<'
    elif data[8:12] == b'\x00\x04\x00\x04':
        e = '>'
    else:
        raise FormatError('unsupported CHNK version (only the 4/4 profile is implemented)')
    lib = Library(data, e)
    version_a, version_b, count = unpack('3H', data, 8, e)
    directory_bytes, logical_end = unpack('2I', data, 16, e)
    platform = data[15]
    lib.header = dict(magic='CHNK', creator=data[4:8].decode('latin1'),
                      version_a=version_a, version_b=version_b,
                      resource_count=count, reserved_byte=data[14], platform_byte=platform,
                      directory_record_bytes=directory_bytes, logical_end=logical_end,
                      byte_order='little' if e == '<' else 'big')
    lib.span(0, 24, 'container_header', **lib.header)
    if logical_end != len(data):
        lib.issue(f'header logical end {logical_end} differs from physical size {len(data)}')
    if platform != (0x03 if e == '<' else 0x54):
        lib.issue(f'unrecognized native platform descriptor 0x{platform:02x}')
    if data[14]:
        lib.issue('nonzero reserved header byte 14; retained in audit')
    location, visited, record_total = 24, set(), 0
    while location != END:
        if location in visited:
            lib.issue(f'directory cycle at 0x{location:x}; traversal stopped')
            break
        visited.add(location)
        if location+8 > len(data):
            lib.issue(f'directory header at 0x{location:x} is truncated')
            break
        length, entries, next_block = unpack('HHI', data, location, e)
        block_start = 0 if location == 24 else location
        block_end = block_start + length
        lib.span(location, location+8, 'directory_block_header',
                 block_length=length, entry_count=entries, next_block=next_block)
        minimum = 32 if location == 24 else 8
        if length < minimum:
            lib.issue(f'directory at 0x{location:x} has impossible length {length}')
            break
        limit = min(len(data), block_end)
        if block_end > len(data):
            lib.issue(f'directory at 0x{location:x} extends past physical EOF')
        pos = location+8
        for _ in range(entries):
            if pos+12 > limit:
                lib.issue(f'truncated directory record at 0x{pos:x}')
                break
            size, kind, ident, representations = unpack('H4s2H', data, pos, e)
            flags_hex = data[pos+10:pos+12].hex()
            flags_byte = data[pos+10]
            storage_control = flags_byte & 3 if e == '<' else flags_byte >> 6
            nested = bool(flags_byte & (4 if e == '<' else 32))
            name_offset = 12 + 12*representations
            if size < 12 or size % 2 or pos+size > limit:
                lib.issue(f'invalid directory record length {size} at 0x{pos:x}; '
                          'remaining records in this block cannot be located')
                break
            name, name_hex, padding = '', '', ''
            if name_offset > size:
                lib.issue(f'directory representation count exceeds record at 0x{pos:x}')
                lib.span(pos, pos+size, 'malformed_directory_record')
                lib.records.append(dict(directory_offset=pos, record_size=size,
                                        representation_count=representations, malformed=True))
                record_total += size
                pos += size
                continue
            if size > name_offset:
                name_length = data[pos+name_offset]
                if name_offset+1+name_length > size:
                    lib.issue(f'directory name at 0x{pos:x} exceeds its record')
                    name_length = size-name_offset-1
                raw_name = data[pos+name_offset+1:pos+name_offset+1+name_length]
                name_hex = raw_name.hex()
                name = raw_name.decode('cp1252' if e == '<' else 'mac_roman', errors='replace')
                padding = data[pos+name_offset+1+name_length:pos+size].hex()
            record = dict(record_index=len(lib.records), directory_offset=pos,
                            record_size=size, kind=kind.decode('latin1'), id=ident,
                            representation_count=representations, flags_hex=flags_hex,
                            storage_control=storage_control, nested_container=nested,
                            name=name, name_hex=name_hex,
                            name_padding_hex=padding)
            lib.records.append(record)
            for rep in range(representations):
                encoding, offset, length_data = unpack('4sII', data, pos+12+12*rep, e)
                lib.resources.append(dict(record, index=len(lib.resources),
                                          representation_index=rep,
                                          encoding=encoding.decode('latin1'),
                                          offset=offset, length=length_data))
            lib.span(pos, pos+size, 'directory_record', record=record)
            record_total += size
            pos += size
        lib.span(pos, limit, 'directory_unused_bytes')
        location = next_block
    if len(lib.records) != count:
        lib.issue(f"header declares {count} records; recovered {len(lib.records)}")
    if record_total != directory_bytes:
        lib.issue(f'header declares {directory_bytes} record bytes; recovered {record_total}')

    # Positive identification needs an indexed SND/PCM RIFF/WAVE resource.
    # Header magic alone also occurs in non-sound documents.
    expected = (b'RIFF', b'WAVE') if e == '<' else (b'FFIR', b'EVAW')
    candidates = [r for r in lib.resources if r['kind'] == 'SND ' and r['encoding'] == 'PCM ']
    identified = any(r['offset']+12 <= len(data) and
                     (data[r['offset']:r['offset']+4],
                      data[r['offset']+8:r['offset']+12]) == expected
                     for r in candidates)
    if not identified:
        raise FormatError('no indexed SND / PCM RIFF/WAVE resource; target format not established')

    # Explicit allocations bound corrupt sizes without recovering by signature.
    boundaries = sorted(set([len(data), 0] + list(visited) +
                            [r['offset'] for r in lib.resources if r['length']]))
    for r in lib.resources:
        start, length_data = r['offset'], r['length']
        end = start+length_data
        if start < 32 or start >= len(data):
            why = 'resource offset outside usable file data'
            lib.issue(f"resource {r['index']}: {why}")
            lib.skipped.append(dict(resource=r, reason=why))
            continue
        next_boundary = next((b for b in boundaries if b > start), len(data))
        safe_end = min(end, len(data), next_boundary)
        if safe_end < end:
            lib.issue(f"resource {r['index']}: truncated at next allocation or EOF")
        payload = data[start:safe_end]
        if r['flags_hex'] != '0000':
            lib.issue(f"resource {r['index']}: unsupported nonzero record flags; "
                      'resource skipped rather than assuming storage semantics')
            lib.span(start, safe_end, 'unsupported_resource_controls')
            lib.skipped.append(dict(resource=r, reason='unsupported nonzero record flags'))
            continue
        if r['kind'] == 'SND ' and r['encoding'] == 'PCM ':
            try:
                sound = parse_sound(lib, r, payload)
            except FormatError as exc:
                lib.span(start, safe_end, 'undecoded_sound')
                lib.skipped.append(dict(resource=r, reason=str(exc)))
                lib.issue(f"sound {r['id']} ({r['name']}): {exc}")
            else:
                lib.sounds.append(sound)
        elif r['kind'] == 'CSRO' and r['encoding'] == 'CSRO':
            lib.span(start, safe_end, 'category_list', resource=r['index'])
            if len(payload) < 6:
                lib.issue(f"category {r['id']}: truncated header")
                continue
            declared = unpack('H', payload, 0, e)[0]
            target = payload[2:6].decode('latin1')
            physical = (len(payload)-6)//2
            ids = list(unpack('H'*physical, payload, 6, e))
            lib.categories.append(dict(resource=r['index'], id=r['id'], name=r['name'],
                                       declared_count=declared, target_kind=target, ids=ids))
            if declared != physical or len(payload) % 2:
                lib.issue(f"category {r['id']} ({r['name']}): count {declared}, "
                          f'{physical} complete IDs stored; all stored IDs retained')
        elif r['kind'] == 'FREE' and r['encoding'] == 'FREE':
            lib.span(start, safe_end, 'free_storage', resource=r['index'])
        else:
            lib.span(start, safe_end, 'uninterpreted_resource', resource=r['index'])
            lib.issue(f"resource {r['index']}: unsupported {r['kind']!r}/{r['encoding']!r}")
            lib.skipped.append(dict(resource=r, reason='unsupported resource type or encoding'))
    for category in lib.categories:
        available = {r['id'] for r in lib.resources if r['kind'] == category['target_kind']}
        missing = [ident for ident in category['ids'] if ident not in available]
        if missing:
            lib.issue(f"category {category['id']}: references absent resource IDs {missing}")
    if not lib.sounds:
        raise FormatError('recognized sound library, but no supported audio could be recovered; '
                          + '; '.join(lib.issues[-3:]))
    return lib


def slug(text):
    # One ASCII basename component, never a path provided by the input file.
    clean = re.sub(r'[^A-Za-z0-9._-]+', '_', text).strip('._-')
    return clean[:72] or 'sound'


def wav_bytes(sound):
    fmt = struct.pack('<HHIIHH', 1, sound.channels, sound.sample_rate,
                      sound.sample_rate*sound.channels*2, sound.channels*2, 16)
    chunks = [(b'fmt ', fmt)]
    # Retain the private metadata in its own original chunk, normalized to LE.
    # Loop start/end and the MIDI base note are metadata: playback repetition
    # requires a separate application flag and must not duplicate the waveform.
    if sound.loop is not None:
        chunks.append((b'loop', sound.loop))
    chunks.append((b'data', sound.pcm))
    body = b'WAVE' + b''.join(tag + struct.pack('<I', len(payload)) + payload +
                            (b'\0' if len(payload) % 2 else b'')
                            for tag, payload in chunks)
    if len(body) > 0xffffffff:
        raise FormatError('output exceeds the RIFF/WAV size limit')
    return b'RIFF' + struct.pack('<I', len(body)) + body


def readable_directory(path):
    missing = []
    current = path
    while not current.exists():
        missing.append(current)
        current = current.parent
    path.mkdir(parents=True, exist_ok=True)
    for created in reversed(missing):
        created.chmod(created.stat().st_mode | 0o550)


def write_exclusive(directory, basename, content):
    """Avoid overwriting existing files and symlinks; use deterministic suffixes."""
    stem, suffix = os.path.splitext(basename)
    number = 1
    while True:
        candidate = directory / (basename if number == 1 else f'{stem}_{number}{suffix}')
        try:
            fd = os.open(candidate, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o664)
            break
        except FileExistsError:
            number += 1
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(content)
            os.fchmod(stream.fileno(), 0o664)
    except BaseException:
        candidate.unlink(missing_ok=True)
        raise
    return candidate.name


def convert(input_file, output_dir, verbose=False):
    input_file, output_dir = Path(input_file), Path(output_dir)
    lib = parse_library(input_file.read_bytes())
    # Complete parsing and decoding before making outputDir or writing anything.
    ready = [(sound, wav_bytes(sound)) for sound in lib.sounds]
    readable_directory(output_dir)
    prefix = slug(input_file.name)
    for sound, content in ready:
        r = sound.resource
        basename = f"{prefix}__{r['id']:05d}_{slug(r['name'])}.wav"
        sound.filename = write_exclusive(output_dir, basename, content)
    if verbose:
        audit = lib.audit()
        report = dict(input=str(input_file), input_bytes=len(lib.data),
                      input_sha256=hashlib.sha256(lib.data).hexdigest(),
                      header=lib.header, records=lib.records, resources=lib.resources,
                      categories=lib.categories, issues=lib.issues, skipped=lib.skipped,
                      semantic_completeness=False,
                      unresolved=['native platform descriptor subfields',
                                  'directory storage-control enum semantics',
                                  'nested containers and external backing-store references '
                                  'are outside the implemented sound-library profile'],
                      covered_bytes=sum(r['length'] for r in audit), ranges=audit,
                      sounds=[dict(resource_index=s.resource['index'], file=s.filename,
                                   sample_rate=s.sample_rate, channels=s.channels,
                                   frames=s.frames, pcm_sha256=hashlib.sha256(s.pcm).hexdigest(),
                                   **s.metadata) for s in lib.sounds])
        write_exclusive(output_dir, prefix+'__audit.json',
                        (json.dumps(report, ensure_ascii=True, indent=2)+'\n').encode('utf-8'))
    return lib


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-verbose', '--verbose', action='store_true',
                        help='also write a JSON structure and byte-range audit')
    parser.add_argument('inputFile', type=Path)
    parser.add_argument('outputDir', type=Path)
    args = parser.parse_args(argv)
    try:
        lib = convert(args.inputFile, args.outputDir, args.verbose)
    except (FormatError, OSError, OverflowError) as exc:
        print(f'fineArtistSound: {exc}', file=sys.stderr)
        return 1
    for issue in lib.issues:
        print('warning: '+issue, file=sys.stderr)
    print(f'Wrote {len(lib.sounds)} WAV files to {args.outputDir}')
    return 0


if __name__ == '__main__':
    sys.exit(main())

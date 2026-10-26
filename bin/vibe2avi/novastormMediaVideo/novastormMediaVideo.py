#!/usr/bin/env python3
# Vibe coded by Codex
"""Decode the DOS Novastorm PCFM video format. See novastormMediaVideo.txt."""

import argparse
import collections
import json
import os
from pathlib import Path
import struct
import sys
from fractions import Fraction


class FormatError(ValueError):
    """An input does not have the supported format."""


class DamageError(ValueError):
    """A recognized stream is damaged."""


class Reader:
    def __init__(self, data, pos=0):
        self.data = data
        self.pos = pos

    def take(self, n):
        if self.pos + n > len(self.data):
            raise DamageError(f"truncated payload at byte {self.pos}: need {n} bytes")
        value = self.data[self.pos:self.pos + n]
        self.pos += n
        return value

    def byte(self):
        if self.pos >= len(self.data):
            raise DamageError(f"truncated payload at byte {self.pos}")
        value = self.data[self.pos]
        self.pos += 1
        return value

    def word(self):
        return int.from_bytes(self.take(2), 'little')


class VideoDecoder:
    """Persistent 16-entry color tables and eight packed rows per 8x8 block."""
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.count = width * height // 64
        self.colors = [bytearray(16) for _ in range(self.count)]
        self.rows = [[0] * 8 for _ in range(self.count)]
        self.opcodes = collections.Counter()

    @staticmethod
    def rle(r, count, bits):
        """Expand pairs of runs; the last pair may extend beyond the output."""
        pixels = []
        while len(pixels) < count:
            control = r.byte()
            values = r.byte()
            for half in (0, 1):
                descriptor = (control >> (4 if half == 0 else 0)) & 15
                if bits == 2:
                    pair = (values >> (4 if half == 0 else 0)) & 15
                else:
                    pair = values if half == 0 else r.byte()
                pixels.extend([pair >> bits] * ((descriptor >> 2) + 1))
                pixels.extend([pair & ((1 << bits) - 1)] * ((descriptor & 3) + 1))
                if len(pixels) >= count:
                    break
        return pixels[:count]

    def block(self, r, index):
        op = r.byte()
        self.opcodes[op] += 1
        colors, rows = self.colors[index], self.rows[index]
        bits = 0
        mode = 0
        if op in (0x00, 0x20):
            if op == 0x20:
                colors[0] = r.byte()
            rows[:] = [0] * 8
            return
        if op in (0x08, 0x09, 0x0A, 0x30, 0x70, 0xB0, 0x0C, 0x0D, 0x0E):
            offset = r.byte()
            source = index + offset
            if source >= self.count:
                raise DamageError(f"color reference {source} beyond {self.count} blocks")
            if op in (0x08, 0x09, 0x0A):
                n, bits, mode = 2, 1, op - 8
            elif op in (0x30, 0x70, 0xB0):
                n, bits, mode = 4, 2, (op - 0x30) // 0x40
            else:
                n, bits, mode = 16, 4, op - 0x0C
            colors[:n] = self.colors[source][:n]
        elif op in (0x40, 0x44, 0x48, 0x4C, 0x50, 0x54, 0x58, 0x5C,
                    0x60, 0x64, 0x68, 0x6C):
            bits, mode = 1, (op >> 4) - 4
            for i, flag in ((0, 8), (1, 4)):
                if op & flag:
                    colors[i] = r.byte()
        elif 0x80 <= op <= 0xAF or 0xC0 <= op <= 0xEF:
            bits = 2 if op < 0xB0 else 4
            mode = (op >> 4) - (8 if bits == 2 else 12)
            mask = op & 15
            if bits == 4 and mask == 0:
                mask, n = r.word(), 16
            else:
                n = 4
            for i in range(n):
                if mask & (1 << (n - 1 - i)):
                    colors[i] = r.byte()
        else:
            raise DamageError(f"invalid video opcode 0x{op:02x} at payload byte {r.pos - 1}")
        if mode == 0:
            return
        row_mask = r.byte() if mode == 1 else 255
        if row_mask == 0:
            raise DamageError("zero row mask in a pattern update")
        # The original codec stores full 4-bit patterns in top-to-bottom order;
        # all other pattern variants arrive in bottom-to-top order.
        order = list(range(8)) if bits == 4 and mode == 2 else [
            i for i in range(7, -1, -1) if row_mask & (1 << i)]
        if bits == 1:
            pixels = [(b >> s) & 1 for b in r.take(len(order)) for s in range(7, -1, -1)]
        else:
            pixels = self.rle(r, len(order) * 8, bits)
        for row, start in zip(order, range(0, len(pixels), 8)):
            word = 0
            for pixel in pixels[start:start + 8]:
                word = (word << 4) | pixel
            rows[row] = word

    def decode(self, data):
        r = Reader(data)
        number = r.word()
        flags = r.take(self.count // 8)
        for i in range(self.count):
            if flags[i // 8] & (128 >> (i & 7)):
                self.block(r, i)
        if r.pos != len(data):
            raise DamageError(f"{len(data) - r.pos} unconsumed frame bytes at {r.pos}")
        return number

    def image(self):
        image = bytearray(self.width * self.height)
        block_height = self.height // 8
        for i, (colors, rows) in enumerate(zip(self.colors, self.rows)):
            x, y = (i // block_height) * 8, (i % block_height) * 8
            for j, word in enumerate(rows):
                start = (y + j) * self.width + x
                image[start:start + 8] = bytes(colors[(word >> s) & 15] for s in range(28, -1, -4))
        return image


def decode_mask(data, width=256, height=144):
    """Decode HMSK into (initial bit, horizontal toggle coordinates) rows."""
    if width != 256 or height != 144:
        raise DamageError("HMSK uses the fixed 256x144 game coordinate system")
    r, rows = Reader(data), []
    while len(rows) < height:
        op = r.byte()
        if op < 16:
            edges = list(r.take(op & 7))
            rows.append((op >> 3, edges))
        else:
            run = op - 16
            bit = int(run > 144)
            if bit:
                run -= 144
            if run == 0 or len(rows) + run > height:
                raise DamageError("HMSK row run exceeds the image or has zero length")
            rows.extend((bit, []) for _ in range(run))
    if r.pos != len(data):
        raise DamageError(f"HMSK has {len(data) - r.pos} trailing bytes")
    return rows


def mask_hit(rows, x, y):
    """Evaluate HMSK exactly as the game does, including unsorted edge lists."""
    if not 0 <= x < 256 or not 0 <= y < 144:
        raise ValueError("mask coordinate is outside 256x144")
    value, edges = rows[y]
    for edge in edges:
        if x < edge:
            break
        value ^= 1
    return value


def decode_depth(data):
    """ZBUF is a row-major 32x18 array of 4-bit depth codes, high nibble first."""
    if len(data) != 288:
        raise DamageError(f"ZBUF needs 288 bytes, got {len(data)}")
    return [n for b in data for n in (b >> 4, b & 15)]


def read_palette(data, palette):
    r = Reader(data)
    start, count = r.word(), r.word()
    if not 0 < count <= 256 or start + count > 256 or len(data) != 4 + count * 3:
        raise DamageError("invalid SPAL palette range or length")
    rgb = r.take(count * 3)
    if any(value > 63 for value in rgb):
        raise DamageError("SPAL component is outside the VGA six-bit range")
    # Replicate the high bits to map the six-bit DAC endpoints to 0..255.
    palette[start * 3:(start + count) * 3] = bytes((v << 2) | (v >> 4) for v in rgb)
    return start, count


def probe(data):
    """Require the complete identifying header combination before any output."""
    p, tc, block = 0, None, None
    if data[:4] == b'SHED':
        if len(data) < 16 or data[4:8] != b'\x08\0\0\0':
            raise FormatError("not the supported SHED/PCFM stream: invalid sound header")
        tc, block = struct.unpack_from('<II', data, 8)
        if tc > 255 or not 0 < block <= 65535:
            raise FormatError("unsupported SHED time constant or audio block length")
        p = 16
    if len(data) < p + 14 or data[p:p + 8] != b'PCFM\x06\0\0\0':
        raise FormatError("not a Novastorm PCFM video stream")
    frames, width, height = struct.unpack_from('<HHH', data, p + 8)
    if (not frames or not width or not height or width % 8 or height % 8
            or width // 8 > 255 or height // 8 > 255 or width * height // 64 % 8):
        raise FormatError("unsupported PCFM geometry or frame count")
    p += 14
    if len(data) < p + 12 or data[p:p + 4] != b'SPAL':
        raise FormatError("PCFM stream has no complete initial SPAL header")
    size = struct.unpack_from('<I', data, p + 4)[0]
    if p + 8 + size > len(data):
        raise FormatError("initial palette is truncated; cannot establish video profile")
    palette = bytearray(768)
    try:
        start, count = read_palette(data[p + 8:p + 8 + size], palette)
    except DamageError as exc:
        raise FormatError(str(exc)) from exc
    return dict(frames=frames, width=width, height=height, time_constant=tc,
                audio_block=block, palette=palette, palette_start=start,
                palette_count=count, body=p + 8 + size)


def chunk(tag, payload):
    return tag + struct.pack('<I', len(payload)) + payload + b'\0' * (len(payload) & 1)


def list_chunk(kind, payload):
    return chunk(b'LIST', kind + payload)


class AVIWriter:
    """Standard-library RIFF AVI muxer: uncompressed BGR24 and mono PCM U8."""
    def __init__(self, path, width, height, fps, rate=None):
        self.width, self.height, self.fps, self.rate = width, height, fps, rate
        self.frames = self.samples = 0
        self.index = []
        self.frame_size = ((width * 3 + 3) & ~3) * height
        self.file = open(path, 'w+b')
        os.chmod(path, 0o664)
        self.file.write(self.header())
        self.movi = self.file.tell()
        self.file.write(b'LIST\0\0\0\0movi')

    def header(self):
        width, height, fps, rate = self.width, self.height, self.fps, self.rate
        avih = struct.pack('<14I', round(1000000 / fps),
                           round(self.frame_size * fps) + (rate or 0), 0, 0x10,
                           self.frames, 0, 2 if rate else 1, self.frame_size,
                           width, height, 0, 0, 0, 0)
        strh = struct.pack('<4s4sIHH8I4h', b'vids', b'DIB ', 0, 0, 0, 0,
                           fps.denominator, fps.numerator, 0, self.frames,
                           self.frame_size, 0xFFFFFFFF, 0, 0, 0, width, height)
        strf = struct.pack('<IiiHH6I', 40, width, height, 1, 24, 0,
                           self.frame_size, 0, 0, 0, 0)
        streams = list_chunk(b'strl', chunk(b'strh', strh) + chunk(b'strf', strf))
        if rate:
            ash = struct.pack('<4s4sIHH8I4h', b'auds', b'\0' * 4, 0, 0, 0, 0,
                              1, rate, 0, self.samples, rate, 0xFFFFFFFF, 1,
                              0, 0, 0, 0)
            asf = struct.pack('<HHIIHH', 1, 1, rate, rate, 1, 8)
            streams += list_chunk(b'strl', chunk(b'strh', ash) + chunk(b'strf', asf))
        return b'RIFF\0\0\0\0AVI ' + list_chunk(b'hdrl', chunk(b'avih', avih) + streams)

    def packet(self, tag, payload):
        offset = self.file.tell() - (self.movi + 8)
        if self.file.tell() + len(payload) + 16 * (len(self.index) + 1) >= 0xFFFFFF00:
            raise FormatError("output exceeds classic AVI's 4 GiB limit")
        self.index.append(struct.pack('<4sIII', tag, 0x10, offset, len(payload)))
        self.file.write(chunk(tag, payload))

    def video(self, pixels, palette):
        # bytes.translate performs the palette lookup without external libraries.
        red, green, blue = (bytes(palette[k::3]) for k in range(3))
        pixels = bytes(pixels)
        row_size = self.width * 3
        rgb = bytearray(len(pixels) * 3)
        rgb[0::3], rgb[1::3], rgb[2::3] = (pixels.translate(t) for t in (blue, green, red))
        pad = b'\0' * (-row_size % 4)
        dib = b''.join(rgb[i:i + row_size] + pad
                       for i in range(len(rgb) - row_size, -1, -row_size))
        self.packet(b'00db', dib)
        self.frames += 1

    def audio(self, data):
        if data and self.rate:
            self.packet(b'01wb', data)
            self.samples += len(data)

    def finish(self):
        movi_end = self.file.tell()
        self.file.write(chunk(b'idx1', b''.join(self.index)))
        end = self.file.tell()
        self.file.seek(0)
        self.file.write(self.header())
        self.file.seek(4)
        self.file.write(struct.pack('<I', end - 8))
        self.file.seek(self.movi + 4)
        self.file.write(struct.pack('<I', movi_end - self.movi - 8))
        self.file.close()


def convert(input_file, output_file, verbose=False, fps=None):
    source, target = Path(input_file), Path(output_file)
    if (source.resolve() == target.resolve()
            or target.exists() and os.path.samefile(source, target)):
        raise FormatError("input and output must be different files")
    data = source.read_bytes()
    info = probe(data)
    tc, block = info['time_constant'], info['audio_block']
    rate = round(1000000 / (256 - tc)) if tc is not None else None
    # PCFM has no timestamp or frame-duration field. Default to one audio block
    # per video frame; the optional override accommodates external game timing.
    timing = Fraction(fps) if fps is not None else Fraction(rate, block) if rate else Fraction(14)
    if timing <= 0 or timing.numerator > 0xFFFFFFFF or timing.denominator > 0xFFFFFFFF:
        raise FormatError("frame rate must be positive and fit AVI's rational fields")
    palette = info.pop('palette')
    report = dict(input=str(source), input_bytes=len(data), **info,
                  sample_rate=rate, fps=str(timing), warnings=[], chunks=[],
                  good_frames=0, concealed_frames=0, skipped_frames=0,
                  inserted_silence_samples=0, decoded_payload_bytes=0,
                  damaged_payload_bytes=0, unparsed_bytes=0)
    decoder = VideoDecoder(info['width'], info['height'])
    writer = None
    pending_audio = bytearray()
    have_audio = False
    next_number = 0
    ended = False
    p = 0

    def warn(offset, reason):
        report['warnings'].append(dict(offset=offset, reason=reason))

    def ensure_writer():
        nonlocal writer
        if writer is None:
            writer = AVIWriter(target, info['width'], info['height'], timing, rate)

    try:
        while p < len(data):
            if p + 8 > len(data):
                warn(p, "incomplete chunk header; remaining bytes cannot be parsed")
                report['unparsed_bytes'] = len(data) - p
                break
            tag, length = struct.unpack_from('<4sI', data, p)
            if tag not in (b'SHED', b'PCFM', b'SPAL', b'SAMP', b'FRAM', b'HMSK', b'ZBUF', b'EOFL'):
                warn(p, f"lost chunk boundary ({tag.hex()}); stopping without guessing a new boundary")
                report['unparsed_bytes'] = len(data) - p
                break
            end = min(p + 8 + length, len(data))
            payload = data[p + 8:end]
            entry = dict(offset=p, type=tag.decode('ascii'), size=length,
                         available=len(payload), status='decoded')
            report['chunks'].append(entry)
            problem = None
            if len(payload) != length:
                problem = f"truncated {tag.decode()}: expected {length} bytes, have {len(payload)}"
            try:
                if tag == b'FRAM':
                    if len(payload) < 2:
                        raise DamageError("frame number is truncated")
                    number = int.from_bytes(payload[:2], 'little')
                    entry['frame'] = number
                    if number != next_number:
                        warn(p, f"frame number {number}, expected {next_number}; retaining physical stream order")
                    next_number = number + 1
                    colors = [c[:] for c in decoder.colors]
                    rows = [r[:] for r in decoder.rows]
                    try:
                        if problem:
                            raise DamageError(problem)
                        decoder.decode(payload)
                    except DamageError as exc:
                        decoder.colors, decoder.rows = colors, rows
                        problem = str(exc)
                        if writer is None:
                            report['skipped_frames'] += 1
                        else:
                            report['concealed_frames'] += 1
                    else:
                        report['good_frames'] += 1
                    # Never manufacture a picture before the first good frame.
                    if writer is not None or problem is None:
                        ensure_writer()
                        if rate is not None and not have_audio:
                            pending_audio.extend(b'\x80' * block)
                            report['inserted_silence_samples'] += block
                        writer.audio(pending_audio)
                        pending_audio.clear()
                        writer.video(decoder.image(), palette)
                    else:
                        pending_audio.clear()
                    have_audio = False
                elif tag == b'SAMP':
                    if rate is None:
                        raise DamageError("SAMP has no SHED audio parameters")
                    pending_audio.extend(payload)
                    have_audio = True
                    if length != block:
                        warn(p, f"audio block has {length} samples; SHED specifies {block}; preserving available samples")
                elif tag == b'SPAL':
                    entry['first_color'], entry['color_count'] = read_palette(payload, palette)
                elif tag == b'HMSK':
                    mask = decode_mask(payload)
                    if verbose:
                        entry['mask_rows'] = mask
                elif tag == b'ZBUF':
                    depth = decode_depth(payload)
                    if verbose:
                        entry['depth_rows'] = [depth[i:i + 32] for i in range(0, 576, 32)]
                elif tag in (b'SHED', b'PCFM'):
                    expected = 8 if tag == b'SHED' else 6
                    if length != expected or p >= info['body']:
                        raise DamageError("invalid or repeated stream header")
                elif tag == b'EOFL':
                    ended = True
                    if length:
                        raise DamageError("EOFL must have an empty payload")
            except DamageError as exc:
                problem = str(exc)
            if problem:
                entry['status'] = 'damaged'
                entry['reason'] = problem
                warn(p, problem)
                report['damaged_payload_bytes'] += len(payload)
            else:
                report['decoded_payload_bytes'] += len(payload)
            p = end
            if ended:
                if p != len(data):
                    warn(p, "bytes after EOFL are not part of the video stream")
                    report['unparsed_bytes'] = len(data) - p
                break
        if not ended:
            warn(p, "EOFL is missing or inaccessible after damage")
        if writer is None:
            raise DamageError("no complete decodable video frame; no AVI was written")
        writer.audio(pending_audio)
        report['output_frames'] = writer.frames
        report['audio_samples'] = writer.samples
        if writer.frames != info['frames']:
            warn(p, f"recovered {writer.frames} of {info['frames']} declared frames")
        report['chunk_header_bytes'] = len(report['chunks']) * 8
        report['accounted_bytes'] = (report['chunk_header_bytes'] + report['decoded_payload_bytes']
                                     + report['damaged_payload_bytes'] + report['unparsed_bytes'])
        report['opcodes'] = {f'{k:02X}': v for k, v in sorted(decoder.opcodes.items())}
        report['status'] = 'recovered with damage' if report['warnings'] else 'complete'
        writer.finish()
        writer = None
    except BaseException:
        if writer is not None:
            writer.file.close()
            target.unlink(missing_ok=True)
        raise
    if verbose:
        sidecar = Path(str(target) + '.json')
        sidecar.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        os.chmod(sidecar, 0o664)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('inputFile')
    parser.add_argument('outputFile')
    parser.add_argument('-verbose', '--verbose', action='store_true',
                        help='also write OUTPUT.json with chunk audit and decoded game metadata')
    parser.add_argument('--fps', type=Fraction,
                        help='explicit playback-rate override; PCFM has no timestamps')
    args = parser.parse_args(argv)
    try:
        report = convert(args.inputFile, args.outputFile, args.verbose, args.fps)
    except (OSError, ValueError, struct.error) as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 1
    for warning in report['warnings']:
        print(f"warning at 0x{warning['offset']:x}: {warning['reason']}", file=sys.stderr)
    print(f"{report['output_frames']} frames, {report['audio_samples']} audio samples -> {args.outputFile}")
    return 0


if __name__ == '__main__':
    sys.exit(main())

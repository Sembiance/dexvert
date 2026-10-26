#!/usr/bin/env python3
# Vibe coded by Codex
"""Decode Imperium Galactica SpidyAni2 with VGA or direct-RGB palettes to AVI.

Usage: imperiumGalacticaAnimation.py inputFile outputFile [-verbose]
Only outputFile is written. FFmpeg is required; no third-party Python modules.
Timing is external to this format: --fps and --audio-delay select playback policy.
Palettes default to VGA6 unless any component exceeds 63, then direct RGB8.
Use --palette-mode to override this file-wide compatibility policy.
See imperiumGalacticaAnimation.txt for the binary format and scope limitations.
"""

import argparse
import collections
import dataclasses
from fractions import Fraction
import hashlib
import math
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import threading

MAGIC = b'SpidyAni2'
SOUND_BYTES = 1270
SAMPLE_RATE = 22050
DEFAULT_FPS = Fraction(1789, 100)
U16 = struct.Struct('<H')
SIGNED_TO_UNSIGNED = bytes(i ^ 128 for i in range(256))
PALETTE_MODES = ('auto', 'vga6', 'rgb8', 'rgb8-to-vga6', 'bgr8', 'vga6-lowbits')


class FormatError(Exception):
    """A recognized file is malformed, or cannot be decoded safely."""


class UnsupportedFormat(FormatError):
    """Not the supported SpidyAni2 profile; never create an output."""


@dataclasses.dataclass
class Block:
    offset: int
    tag: bytes
    payload: int
    size: int
    expected_size: int = 0
    width: int = 0
    height: int = 0
    lzss: bool = False
    truncated: bool = False


@dataclasses.dataclass
class Animation:
    data: bytes
    flags: int
    declared_frames: int
    width: int
    height: int
    language: int
    blocks: list
    issues: list
    accounted_bytes: int
    palette_max: int
    palette_mode: str

    @property
    def audio_bytes(self):
        return sum(b.size for b in self.blocks if b.tag == b'Hang')

    def describe(self):
        return dict(bytes=len(self.data), accounted_bytes=self.accounted_bytes,
                    flags=f'0x{self.flags:04x}', width=self.width, height=self.height,
                    declared_frames=self.declared_frames, language=self.language,
                    blocks=dict(collections.Counter(b.tag.decode('ascii') for b in self.blocks)),
                    audio_bytes=self.audio_bytes, palette_max=self.palette_max,
                    palette_mode=self.palette_mode,
                    issues=self.issues)


def inspect(data, *, audit_palette=False, palette_mode='auto'):
    """Parse by lengths, never scan for guessed block signatures.

    Auto chooses direct RGB8 if any palette component in the file exceeds 63;
    otherwise it chooses VGA6. Resolve once for the whole file, including dark
    palettes preceding brighter ones. Explicit modes override this policy.
    """
    if palette_mode not in PALETTE_MODES:
        raise UnsupportedFormat(f'unknown palette mode: {palette_mode}')
    if data[:9] != MAGIC:
        raise UnsupportedFormat('not SpidyAni version 2 (exact signature required)')
    if len(data) < 19:
        raise FormatError('SpidyAni2 header is truncated; dimensions unavailable')
    flags, count, width, height, language = struct.unpack_from('<5H', data, 9)
    if flags & ~0x25 or not flags & 1:
        raise UnsupportedFormat(f'unsupported SpidyAni2 flags 0x{flags:04x}; '
                                'only RLE1/RLE2 with optional LZSS are defined')
    if not width or not height:
        raise FormatError('zero image dimension; cannot recover a frame size')
    # The original 16-bit coordinates are accepted. Reject impossible memory use
    # explicitly instead of letting a damaged header exhaust the host.
    if width * height > 100_000_000:
        raise FormatError('image exceeds the decoder safety limit of 100 million pixels')
    issues = []
    blocks = []
    pos = 19
    palette_max = 0
    while pos < len(data):
        start = pos
        tag = data[pos:pos + 4]
        if len(tag) != 4:
            issues.append(f'0x{pos:x}: truncated block tag ({len(tag)} bytes); stopped')
            break
        pos += 4
        raw_size = 0
        bw = bh = 0
        lzss = False
        if tag == b'Pal ':
            size = 768
        elif tag == b'Hang':
            size = SOUND_BYTES
        elif tag == b'Data':
            header_size = 8 if flags & 0x20 else 6
            if pos + header_size > len(data):
                issues.append(f'0x{start:x}: truncated Data header; stopped')
                pos = start
                break
            if flags & 0x20:
                raw_size, stored, bw, bh = struct.unpack_from('<4H', data, pos)
                size = raw_size if stored == 65535 else stored
                lzss = stored != 65535
            else:
                size, bw, bh = struct.unpack_from('<3H', data, pos)
                raw_size = size
            pos += header_size
            if bw != width or not bh or bh > height:
                issues.append(f'0x{start:x}: invalid strip dimensions {bw}x{bh}; '
                              'block retained but not painted')
        else:
            issues.append(f'0x{start:x}: unknown block {tag!r}; no length rule, stopped')
            pos = start
            break
        actual = min(size, len(data) - pos)
        truncated = actual != size
        if truncated:
            issues.append(f'0x{start:x}: truncated {tag.decode()} payload '
                          f'({actual}/{size} bytes)')
        if tag == b'Pal ':
            palette_max = max(palette_max, max(data[pos:pos + actual], default=0))
            if palette_max > 63 and not audit_palette and palette_mode == 'vga6':
                raise UnsupportedFormat(f'0x{start:x}: palette components exceed 63; '
                    'not the explicitly requested six-bit VGA profile; use auto '
                    'or rgb8 for a direct-RGB palette variant')
        blocks.append(Block(start, tag, pos, actual, raw_size, bw, bh, lzss, truncated))
        pos += actual
    selected_mode = ('rgb8' if palette_max > 63 else 'vga6') if palette_mode == 'auto' else palette_mode
    return Animation(data, flags, count, width, height, language,
                     blocks, issues, pos, palette_max, selected_mode)


def unpack_lzss(data, expected, *, recover=False, stats=None):
    """4096-byte zero dictionary, write cursor 0xFEE, LSB-first flag bytes."""
    window = bytearray(4096)
    write = 0xFEE
    out = bytearray()
    src = 0
    error = None
    try:
        while src < len(data):
            flag = data[src]
            src += 1
            if stats is not None:
                stats['lzss_flag_bytes'] += 1
            tokens = 0
            for bit in range(8):
                if src == len(data):
                    break
                tokens += 1
                if flag & (1 << bit):
                    value = data[src]
                    src += 1
                    out.append(value)
                    window[write] = value
                    write = (write + 1) & 4095
                    if stats is not None:
                        stats['lzss_literals'] += 1
                else:
                    if src + 2 > len(data):
                        raise FormatError('truncated LZSS match')
                    lo, hi = data[src:src + 2]
                    src += 2
                    offset = lo | ((hi & 0xF0) << 4)
                    length = (hi & 15) + 3
                    # Sequential copying is essential for overlapping matches.
                    for i in range(length):
                        value = window[(offset + i) & 4095]
                        out.append(value)
                        window[write] = value
                        write = (write + 1) & 4095
                    if stats is not None:
                        stats['lzss_matches'] += 1
                if len(out) > expected:
                    raise FormatError(f'LZSS expands beyond its {expected}-byte declaration')
            if stats is not None:
                stats['lzss_unused_flag_bits'] += 8 - tokens
        if len(out) != expected:
            raise FormatError(f'LZSS size mismatch: {len(out)} decoded, {expected} declared')
    except FormatError as exc:
        if not recover:
            raise
        error = str(exc)
    if stats is not None:
        stats['lzss_input_bytes'] += src
        stats['lzss_output_bytes'] += min(len(out), expected)
    return bytes(out[:expected]), error


def apply_rle(data, image, start, end, method, *, recover=False, stats=None):
    """Decode exactly one strip, retaining skipped palette indices."""
    src = 0
    dst = start
    error = None
    try:
        while src < len(data):
            command = data[src]
            src += 1
            if command < 128 and method == 1:
                count = 1
                kind = 'literal'
                literal = bytes((command,))
            else:
                if command in (0, 128, 192):
                    if src + 2 > len(data):
                        raise FormatError('truncated RLE 16-bit count')
                    count = U16.unpack_from(data, src)[0]
                    src += 2
                else:
                    count = command if command < 128 else command & 63
                if command < 128:
                    kind = 'copy_long' if command == 0 else 'copy_short'
                    if src + count > len(data):
                        if recover:
                            n = min(len(data) - src, max(0, end - dst))
                            image[dst:dst + n] = data[src:src + n]
                        raise FormatError('truncated RLE literal span')
                    literal = data[src:src + count]
                    src += count
                elif command < 192:
                    kind = 'skip_long' if command == 128 else 'skip_short'
                else:
                    kind = 'fill_long' if command == 192 else 'fill_short'
                    if src == len(data):
                        raise FormatError('truncated RLE fill value')
                    value = data[src]
                    src += 1
            if dst + count > end:
                # Recovery never writes beyond this strip or changes image length.
                if recover and dst < end:
                    if kind.startswith('fill'):
                        image[dst:end] = bytes((value,)) * (end - dst)
                    elif not kind.startswith('skip'):
                        image[dst:end] = literal[:end - dst]
                raise FormatError(f'RLE command overruns strip by {dst + count - end} pixels')
            if kind.startswith('fill'):
                image[dst:dst + count] = bytes((value,)) * count
            elif not kind.startswith('skip'):
                image[dst:dst + count] = literal
            dst += count
            if stats is not None:
                stats['rle_' + kind] += 1
                stats['rle_pixels_' + kind] += count
                stats['rle_zero_count'] += count == 0
        if dst != end:
            raise FormatError(f'RLE covers {dst - start} of {end - start} strip pixels')
    except FormatError as exc:
        if not recover:
            raise
        error = str(exc)
    if stats is not None:
        stats['rle_input_bytes'] += src
    return error


def frames(animation, *, recover=True, stats=None, issues=None):
    """Yield (indexed image, RGB VGA palette) after each complete image."""
    a = animation
    image = bytearray(a.width * a.height)
    palette = bytes(768)
    have_palette = False
    y = 0
    produced = 0
    method = 2 if a.flags & 4 else 1
    issues = [] if issues is None else issues
    for block in a.blocks:
        payload = a.data[block.payload:block.payload + block.size]
        if block.tag == b'Pal ':
            palette = payload + palette[len(payload):]
            have_palette = True
            continue
        if block.tag != b'Data':
            continue
        if block.width != a.width or not 0 < block.height <= a.height:
            if not recover:
                raise FormatError(f'0x{block.offset:x}: invalid strip dimensions')
            continue
        if y + block.height > a.height:
            if not recover:
                raise FormatError(f'0x{block.offset:x}: strips exceed frame height')
            issues.append(f'0x{block.offset:x}: incomplete prior frame preserved')
            produced += 1
            yield image, palette
            y = 0
        if not have_palette:
            if not recover:
                raise FormatError('image data precedes the first palette')
            issues.append(f'0x{block.offset:x}: missing palette; using black until one arrives')
            have_palette = True
        if block.lzss:
            payload, error = unpack_lzss(payload, block.expected_size,
                                         recover=recover, stats=stats)
            if error:
                issues.append(f'0x{block.offset:x}: {error}')
        error = apply_rle(payload, image, y * a.width,
                          (y + block.height) * a.width, method,
                          recover=recover, stats=stats)
        if error:
            issues.append(f'0x{block.offset:x}: {error}; remaining pixels retained')
        y += block.height
        if stats is not None:
            stats['data_blocks_decoded'] += 1
        if y == a.height:
            produced += 1
            yield image, palette
            y = 0
    if y:
        if not recover:
            raise FormatError('EOF inside a frame')
        issues.append('EOF inside a frame; undecoded rows retained from previous image')
        produced += 1
        yield image, palette
    if produced != a.declared_frames:
        message = f'{produced} actual frames; header declares {a.declared_frames}'
        if not recover:
            raise FormatError(message)
        issues.append(message)


def chunk(tag, data):
    return tag + struct.pack('<I', len(data)) + data + (b'\0' if len(data) & 1 else b'')


def list_chunk(tag, data):
    return chunk(b'LIST', tag + data)


def avi_stream_header(width, height, fps, audio_size):
    """A streaming raw-BGR AVI fed to FFmpeg; never written to disk.

    Zero RIFF/movi sizes are the conventional unseekable AVI representation.
    FFmpeg reads chunks through EOF. The final AVI is seekable and indexed.
    """
    stride = (width * 3 + 3) & ~3
    frame_size = stride * height
    main = struct.pack('<14I', round(1_000_000 / fps), 0, 0, 0, 0, 0,
                       2 if audio_size else 1, frame_size, width, height, 0, 0, 0, 0)
    video_header = struct.pack('<4s4sIHH8I4h', b'vids', b'DIB ', 0, 0, 0, 0,
                               fps.denominator, fps.numerator, 0, 0, frame_size,
                               0xFFFFFFFF, 0, 0, 0, 0, 0)
    bitmap = struct.pack('<IiiHHIIiiII', 40, width, height, 1, 24, 0,
                         frame_size, 0, 0, 0, 0)
    header = chunk(b'avih', main) + list_chunk(b'strl', chunk(b'strh', video_header)
                                             + chunk(b'strf', bitmap))
    if audio_size:
        sound_header = struct.pack('<4s4sIHH8I4h', b'auds', b'\0' * 4, 0, 0, 0, 0,
                                   1, SAMPLE_RATE, 0, audio_size, 4096,
                                   0xFFFFFFFF, 1, 0, 0, 0, 0)
        wave = struct.pack('<HHIIHH', 1, 1, SAMPLE_RATE, SAMPLE_RATE, 1, 8)
        header += list_chunk(b'strl', chunk(b'strh', sound_header) + chunk(b'strf', wave))
    return b'RIFF\0\0\0\0AVI ' + list_chunk(b'hdrl', header) + b'LIST\0\0\0\0movi'


def display_palette(palette, mode='vga6'):
    """Return RGB888 entries using an already resolved, file-wide mode."""
    if mode == 'vga6':
        return bytes(v << 2 for v in palette)
    if mode == 'rgb8':
        return bytes(palette)
    if mode == 'rgb8-to-vga6':
        return bytes(v & 0xFC for v in palette)
    if mode == 'bgr8':
        out = bytearray(palette)
        out[0::3], out[2::3] = palette[2::3], palette[0::3]
        return bytes(out)
    if mode == 'vga6-lowbits':
        return bytes((v & 63) << 2 for v in palette)
    raise UnsupportedFormat(f'unknown palette mode: {mode}')


def bgr_frame(indices, palette, width, height, palette_mode='vga6'):
    """Convert palette indices to BGR, with bottom-up padded DIB rows."""
    pixels = bytes(indices)
    rgb = display_palette(palette, palette_mode)
    table_r = rgb[0::3]
    table_g = rgb[1::3]
    table_b = rgb[2::3]
    packed = bytearray(len(pixels) * 3)
    packed[0::3] = pixels.translate(table_b)
    packed[1::3] = pixels.translate(table_g)
    packed[2::3] = pixels.translate(table_r)
    row = width * 3
    padding = b'\0' * ((-row) & 3)
    return b''.join(packed[y * row:(y + 1) * row] + padding
                    for y in range(height - 1, -1, -1))


def audit(animation):
    """Strictly consume every instruction and byte; no error recovery."""
    if animation.issues or animation.accounted_bytes != len(animation.data):
        raise FormatError('; '.join(animation.issues) or 'unaccounted trailing bytes')
    stats = collections.Counter()
    image_hash = hashlib.sha256()
    count = 0
    for image, palette in frames(animation, recover=False, stats=stats):
        image_hash.update(image)
        image_hash.update(palette)
        count += 1
    stats['frames'] = count
    return dict(stats), image_hash.hexdigest()


def convert(input_file, output_file, *, fps=DEFAULT_FPS, audio_delay=Fraction(0),
            verbose=False, ffmpeg='ffmpeg', palette_mode='auto'):
    input_file = Path(input_file)
    output_file = Path(output_file)
    if input_file.resolve() == output_file.resolve():
        raise FormatError('input and output paths must differ')
    # Read and classify before invoking FFmpeg or opening an output path.
    with input_file.open('rb') as source:
        prefix = source.read(19)
        inspect(prefix, palette_mode=palette_mode)
        a = inspect(prefix + source.read(), palette_mode=palette_mode)
    if not any(b.tag == b'Data' and b.width == a.width and 0 < b.height <= a.height
               for b in a.blocks):
        raise FormatError('no recoverable image data')
    if fps <= 0 or fps.numerator > 0x7FFFFFFF or fps.denominator > 0x7FFFFFFF:
        raise FormatError('frame rate must be positive and fit signed 32-bit AVI fields')
    if audio_delay < 0:
        raise FormatError('audio delay must be nonnegative (seconds)')
    if output_file.exists():
        raise FormatError(f'output already exists: {output_file}; choose a new path')
    executable = shutil.which(ffmpeg)
    if executable is None:
        raise FormatError(f'FFmpeg executable not found: {ffmpeg}')
    audio = b''.join(a.data[b.payload:b.payload + b.size] for b in a.blocks
                     if b.tag == b'Hang').translate(SIGNED_TO_UNSIGNED)
    delay_samples = round(audio_delay * SAMPLE_RATE) if audio else 0
    audio_size = len(audio) + delay_samples if audio else 0
    if audio_size > 0xFFFFFFFF:
        raise FormatError('audio plus requested delay exceeds the AVI stream length limit')
    issues = list(a.issues)
    source_frames = frames(a, issues=issues)
    try:
        first = next(source_frames)
    except StopIteration:
        raise FormatError('no recoverable video frame') from None
    command = [executable, '-hide_banner', '-loglevel', 'error', '-nostdin',
               '-probesize', '32', '-analyzeduration', '0', '-f', 'avi', '-i', 'pipe:0',
               '-map', '0:v:0', '-map', '0:a:0?', '-c:v', 'ffv1', '-level', '3',
               '-coder', '1', '-context', '1', '-g', '1', '-pix_fmt', 'bgr0',
               '-threads', '1', '-c:a', 'pcm_u8', '-f', 'avi', '-y',
               str(output_file.absolute())]
    stderr = bytearray()
    # Reserve only the requested output, atomically, so a competing conversion
    # cannot cause -y or error cleanup to overwrite/delete an existing result.
    fd = os.open(output_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o664)
    owned_stat = os.fstat(fd)
    os.close(fd)

    def remove_own_output():
        try:
            current = output_file.stat()
            if (current.st_dev, current.st_ino) == (owned_stat.st_dev, owned_stat.st_ino):
                output_file.unlink()
        except FileNotFoundError:
            pass

    try:
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                                   stderr=subprocess.PIPE)
    except BaseException:
        remove_own_output()
        raise

    def collect_errors():
        for part in iter(lambda: process.stderr.read(8192), b''):
            if len(stderr) < 131072:
                stderr.extend(part[:131072 - len(stderr)])
        process.stderr.close()

    reader = threading.Thread(target=collect_errors, daemon=True)
    reader.start()
    frame_count = 0
    audio_pos = 0
    last = None
    video_hash = hashlib.sha256()
    success = False
    try:
        process.stdin.write(avi_stream_header(a.width, a.height, fps, audio_size))

        def send_audio(end):
            nonlocal audio_pos
            end = min(end, audio_size)
            while audio_pos < end:
                next_pos = min(end, audio_pos + 65536)
                silence = min(next_pos, delay_samples) - audio_pos
                sound = b'\x80' * max(0, silence)
                real_start = max(audio_pos, delay_samples)
                if next_pos > real_start:
                    sound += audio[real_start - delay_samples:next_pos - delay_samples]
                process.stdin.write(chunk(b'01wb', sound))
                audio_pos = next_pos

        def send_frame(frame):
            nonlocal frame_count
            # Audio boundaries are exactly derived from the chosen rational FPS.
            process.stdin.write(chunk(b'00db', frame))
            row_bytes = a.width * 3
            stride = (row_bytes + 3) & ~3
            for y in range(a.height - 1, -1, -1):
                video_hash.update(frame[y * stride:y * stride + row_bytes])
            frame_count += 1
            send_audio((frame_count * SAMPLE_RATE * fps.denominator) // fps.numerator)

        last = bgr_frame(*first, a.width, a.height, a.palette_mode)
        send_frame(last)
        for raw, palette in source_frames:
            last = bgr_frame(raw, palette, a.width, a.height, a.palette_mode)
            send_frame(last)
        decoded_frames = frame_count
        # Keep every audio sample, holding the final image when the sound is longer.
        total_frames = max(frame_count, math.ceil(Fraction(audio_size, SAMPLE_RATE) * fps))
        while frame_count < total_frames:
            send_frame(last)
        send_audio(audio_size)
        process.stdin.close()
        returncode = process.wait()
        reader.join()
        if returncode:
            raise FormatError('FFmpeg failed: ' + stderr.decode('utf-8', 'replace').strip())
        if not output_file.exists() or not output_file.stat().st_size:
            raise FormatError('FFmpeg produced no output')
        output_file.chmod(output_file.stat().st_mode | 0o440)
        success = True
    except BrokenPipeError:
        process.wait()
        reader.join()
        raise FormatError('FFmpeg failed: ' + stderr.decode('utf-8', 'replace').strip()) from None
    finally:
        if not process.stdin.closed:
            try:
                process.stdin.close()
            except BrokenPipeError:
                pass
        if process.poll() is None:
            process.terminate()
            process.wait()
        reader.join()
        if not success:
            remove_own_output()
    result = a.describe()
    result.update(decoded_frames=decoded_frames, avi_frames=frame_count,
                  fps=str(fps), audio_delay_seconds=str(audio_delay), issues=issues,
                  palette_mode_requested=palette_mode,
                  video_bgr24_sha256=video_hash.hexdigest())
    audio_hash = hashlib.sha256()
    # Do not allocate a potentially large silent lead-in just to hash it.
    for pos in range(0, delay_samples, 65536):
        audio_hash.update(b'\x80' * min(65536, delay_samples - pos))
    audio_hash.update(audio)
    result['audio_u8_sha256'] = audio_hash.hexdigest() if audio else None
    for issue in issues:
        print('warning: ' + issue, file=sys.stderr)
    if verbose:
        import json
        print(json.dumps(result, indent=2), file=sys.stderr)
    return result


def positive_fraction(value):
    try:
        return Fraction(value)
    except (ValueError, ZeroDivisionError):
        raise argparse.ArgumentTypeError('expected a number or numerator/denominator') from None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('inputFile')
    parser.add_argument('outputFile')
    parser.add_argument('-verbose', '--verbose', action='store_true',
                        help='print structural diagnostics to stderr; no sidecar files')
    parser.add_argument('--fps', type=positive_fraction, default=DEFAULT_FPS,
                        help='external playback rate (default 17.89; not stored in ANI)')
    parser.add_argument('--audio-delay', type=positive_fraction, default=Fraction(0),
                        help='external audio delay in seconds (default 0)')
    parser.add_argument('--ffmpeg', default='ffmpeg', help='FFmpeg executable path')
    parser.add_argument('--palette-mode', choices=PALETTE_MODES, default='auto',
                        help='default auto: direct RGB8 if any palette component '
                             'in the file exceeds 63, otherwise VGA6; explicit '
                             'modes override this policy')
    args = parser.parse_args(argv)
    try:
        convert(args.inputFile, args.outputFile, fps=args.fps,
                audio_delay=args.audio_delay, verbose=args.verbose, ffmpeg=args.ffmpeg,
                palette_mode=args.palette_mode)
    except (FormatError, OSError, ValueError) as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print('error: interrupted', file=sys.stderr)
        return 130
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

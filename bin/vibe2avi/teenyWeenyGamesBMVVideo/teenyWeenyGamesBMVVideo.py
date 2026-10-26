#!/usr/bin/env python3
# Vibe coded by Codex
"""Decode headerless Discworld II BMV to lossless AVI with stereo PCM.

Python 3.10+ standard library only; the ffmpeg executable packages the AVI.
The BMV demultiplexer, video decoder and DPCM audio decoder are implemented here.
See teenyWeenyGamesBMVVideo.txt for the bitstream and recovery rules.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib

WIDTH, HEIGHT, FPS, RATE = 640, 429, 12, 22050
PIXELS = WIDTH * HEIGHT
SLOT = 25 * 1024
MULTIPLIERS = (16512, 8256, 4128, 2064, 1032, 516, 258, 192,
               129, 88, 64, 56, 48, 40, 36, 32)
# Each byte is a signed difference. Tables include arithmetic rounding toward -inf.
DELTAS = tuple(tuple(((x if x < 128 else x - 256) * m) >> 5
                     for x in range(256)) for m in MULTIPLIERS)


class BMVError(ValueError):
    """Unrecognized, unsupported, or undecodable input; no output is committed."""


class Damaged(BMVError):
    """A syntactically invalid field in an otherwise recognized stream."""


def decode_picture(encoded: bytes, screen: bytearray, displacement: int) -> dict:
    """Update an indexed framebuffer including its two zero guard scanlines.

    Byte reads and literal reads share one cursor. The cached high nibble survives
    literal reads. This is essential: the controls are not a separate bitstream.
    Reverse decoding traverses both compressed bytes and output pixels backwards.
    """
    forward = displacement <= -WIDTH or displacement >= 0
    step = 1 if forward else -1
    src = 0 if forward else len(encoded) - 1
    dst = WIDTH if forward else WIDTH + PIXELS - 1
    remaining = PIXELS
    cached = None
    mode = 2  # DELTA=0, RAW=1, RUN=2; first instruction becomes DELTA or RAW.
    controls = literals = operations = 0
    counts = [0, 0, 0]
    while remaining:
        value = shift = 0
        while True:
            if cached is None:
                if not 0 <= src < len(encoded):
                    raise Damaged("truncated video length code")
                byte = encoded[src]
                src += step
                controls += 1
                nibble, cached = byte & 15, byte >> 4
            else:
                nibble, cached = cached, None
            value |= nibble << shift
            if nibble & 12:
                break
            shift += 2
            if shift > 18:
                # The smallest terminated code at this shift exceeds a frame.
                raise Damaged("video length code exceeds the framebuffer")
        length = (value >> 1) - 1
        if not 0 < length <= remaining:
            raise Damaged(f"video run of {length} pixels exceeds {remaining} remaining")
        mode = (mode + 1 + (value & 1)) % 3
        lo = dst if forward else dst - length + 1
        hi = lo + length
        if mode == 0:
            a, b = lo + displacement, hi + displacement
            if a < 0 or b > len(screen):
                raise Damaged("video delta reads outside framebuffer and guard rows")
            if displacement:
                if forward and displacement < 0 and length > -displacement:
                    seed = bytes(screen[a:lo])
                    screen[lo:hi] = (seed * ((length + len(seed) - 1) // len(seed)))[:length]
                else:
                    screen[lo:hi] = screen[a:b]
        elif mode == 1:
            a = src if forward else src - length + 1
            b = a + length
            if a < 0 or b > len(encoded):
                raise Damaged("truncated video literal run")
            screen[lo:hi] = encoded[a:b]
            src += step * length
            literals += length
        else:
            screen[lo:hi] = bytes((screen[dst - step],)) * length
        dst += step * length
        remaining -= length
        operations += 1
        counts[mode] += 1
    if controls + literals != len(encoded):
        raise Damaged(f"{len(encoded) - controls - literals} unconsumed video bytes")
    return {"control_bytes": controls, "literal_bytes": literals,
            "unused_high_nibbles": int(cached is not None),
            "unused_high_nibble_value": cached,
            "operations": operations, "operation_counts": dict(zip(("delta", "raw", "run"), counts)),
            "direction": "forward" if forward else "reverse"}


def decode_audio(blobs: bytes, predictors: list[int]) -> bytes:
    """Decode 65-byte DPCM blocks to interleaved, little-endian signed PCM16."""
    if len(blobs) % 65:
        raise Damaged("incomplete audio block")
    out = bytearray(len(blobs) // 65 * 128)
    pos = 0
    left, right = predictors
    for p in range(0, len(blobs), 65):
        header = blobs[p]
        dl = DELTAS[(header >> 1) & 15]
        dr = DELTAS[((header >> 5) | (header << 3)) & 15]
        for q in range(p + 1, p + 65, 2):
            left = (left + dl[blobs[q]]) & 65535
            right = (right + dr[blobs[q + 1]]) & 65535
            struct.pack_into("<HH", out, pos, left, right)
            pos += 4
    predictors[:] = left, right
    return bytes(out)


def rgb_frame(screen: bytearray, palette: bytes) -> bytes:
    pixels = bytes(screen[WIDTH:WIDTH + PIXELS])
    rgb = bytearray(PIXELS * 3)
    for channel in range(3):
        rgb[channel::3] = pixels.translate(palette[channel::3])
    return bytes(rgb)


def png_frame(screen: bytearray, palette: bytes) -> bytes:
    """Lossless, indexed PNG used only as an internal pipe/spool interchange."""
    def chunk(kind: bytes, payload: bytes) -> bytes:
        return (struct.pack(">I", len(payload)) + kind + payload +
                struct.pack(">I", zlib.crc32(kind + payload)))
    rows = b"".join(b"\0" + screen[y:y + WIDTH]
                    for y in range(WIDTH, WIDTH + PIXELS, WIDTH))
    return (b"\x89PNG\r\n\x1a\n" +
            chunk(b"IHDR", struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 3, 0, 0, 0)) +
            chunk(b"PLTE", palette) + chunk(b"IDAT", zlib.compress(rows, 1)) +
            chunk(b"IEND", b""))


def decode(data: bytes, sink=None, *, salvage: bool = True) -> dict:
    """Decode and audit the complete input. sink receives (screen, palette, PCM).

    No filename-based detection, signature guesses, or scanning for resync points.
    Recovery is only enabled after a fully valid frame establishes the grammar.
    """
    if data.startswith(b"BMVi"):
        raise BMVError("headered Discworld Noir BMV is a different, unsupported format")
    if not data:
        raise BMVError("empty input")
    screen = bytearray(PIXELS + 2 * WIDTH)
    palette = bytes(768)
    predictors = [0, 0]
    p = frames = audio_samples = 0
    confirmed = ended = has_audio = False
    totals = Counter()
    packets, regions, warnings, commands = [], [], [], []
    video_hash, audio_hash = hashlib.sha256(), hashlib.sha256()

    def region(start, end, kind):
        if end > start:
            regions.append({"start": start, "end": end, "kind": kind})
            totals[kind] += end - start

    def damage(message):
        if not confirmed or not salvage:
            raise BMVError(f"offset {p:#x}: {message}; cannot safely recover")
        warnings.append(f"offset {p:#x}: {message}")

    while p < len(data):
        flag = data[p]
        if flag == 0:
            end = min((p // SLOT + 1) * SLOT, len(data))
            region(p, p + 1, "slot_skip_opcode")
            region(p + 1, end, "slot_padding")
            if any(data[p + 1:end]):
                # Slot remainder is explicitly skipped, not parsed as packets.
                warnings.append(f"offset {p:#x}: slot fill contains nonzero ignored bytes")
            p = end
            continue
        if flag == 1:
            region(p, p + 1, "end_opcode")
            p += 1
            ended = True
            if p < len(data):
                region(p, len(data), "after_end")
                if any(data[p:]):
                    damage("nonzero data after the end marker; preserved only in the audit")
                p = len(data)
            break
        if flag & 3 not in (2, 3):
            damage(f"invalid packet type {flag:#04x}; stopping at the last known boundary")
            region(p, len(data), "unrecoverable_tail")
            p = len(data)
            break
        if flag & 0x40:
            raise BMVError(f"offset {p:#x}: extended-mode flag 0x40 is unsupported")
        if flag & 0x80 and not flag & 0x10:
            damage("PRINT flag without a command")
        if p + 4 > len(data):
            damage("truncated packet header")
            region(p, len(data), "truncated_header")
            p = len(data)
            break
        length = int.from_bytes(data[p + 1:p + 4], "little")
        declared_end = p + 4 + length
        end = min(declared_end, len(data))
        region(p, p + 1, "packet_flags")
        region(p + 1, p + 4, "packet_length")
        q = p + 4
        packet = {"offset": p, "flags": flag, "payload_length": length,
                  "available_end": end, "frame": frames, "fields": []}
        pcm = b""
        new_palette = palette
        new_screen = bytearray(screen)
        decoded_ok = False

        def field(count, kind):
            nonlocal q
            if count > end - q:
                raise Damaged(f"truncated {kind}: need {count}, have {end - q} bytes")
            value = data[q:q + count]
            packet["fields"].append({"start": q, "end": q + count, "kind": kind})
            region(q, q + count, kind)
            q += count
            return value

        try:
            if not length:
                raise Damaged("empty frame packet")
            if flag & 0x20:
                has_audio = True
                blocks = field(1, "audio_block_count")[0]
                packet["audio_blocks"] = blocks
                # Salvage whole blocks when the final audio field is truncated.
                available = min(blocks, (end - q) // 65)
                pcm = decode_audio(field(available * 65, "audio_blocks"), predictors)
                if available != blocks:
                    raise Damaged(f"truncated audio: {available} of {blocks} blocks available")
            else:
                # Original player emits 57 silent blocks for an audio-less frame.
                pcm = bytes(57 * 128)
                packet["silent_audio_samples"] = 57 * 32
            if flag & 0x10:
                raw = field(8 if flag & 0x80 else 10, "command")
                x, y, string_id, duration = struct.unpack_from("<hhhB", raw)
                command = {"frame": frames, "x": x, "y": y, "string_id": string_id,
                           "duration_frames": duration, "kind": "print" if flag & 0x80 else "talk"}
                if flag & 0x80:
                    command["font_id"] = raw[7]
                else:
                    command["rgb"] = list(raw[7:10])
                commands.append(command)
            if flag & 8:
                new_palette = field(768, "palette_rgb")
            displacement = struct.unpack("<h", field(2, "scroll_displacement"))[0] if flag & 4 else (-WIDTH if flag & 1 else 0)
            packet["displacement"] = displacement
            encoded = field(end - q, "video_codes_and_literals")
            packet["video"] = decode_picture(encoded, new_screen, displacement)
            if declared_end > len(data):
                raise Damaged("packet payload extends past end of file")
            decoded_ok = True
        except Damaged as exc:
            damage(str(exc))
            packet["recovery"] = str(exc)
            # Keep the old image; partial writes from the bad frame never leak.
            region(q, end, "damaged_packet_remainder")
        if decoded_ok:
            confirmed = True
            screen = new_screen
        palette = new_palette
        video_hash.update(rgb_frame(screen, palette))
        audio_hash.update(pcm)
        audio_samples += len(pcm) // 4
        if sink is not None:
            sink(screen, palette, pcm)
        frames += 1
        packets.append(packet)
        p = end
    if not confirmed:
        raise BMVError("no complete BMV frame: format cannot be established")
    if not ended:
        damage("missing end-of-movie opcode")
    if commands:
        warnings.append("Text commands are preserved in AVI comment metadata; rendering requires external game strings and fonts.")
    previous = 0
    for item in regions:
        if item["start"] != previous:
            raise AssertionError("byte coverage is not contiguous")
        previous = item["end"]
    if previous != len(data):
        raise AssertionError("byte coverage is incomplete")
    return {"format": "Discworld II headerless BMV", "input_bytes": len(data),
            "input_sha256": hashlib.sha256(data).hexdigest(), "frames": frames,
            "width": WIDTH, "height": HEIGHT, "fps": FPS,
            "video_duration": frames / FPS, "has_audio": has_audio,
            "audio_samples_per_channel": audio_samples if has_audio else 0,
            "audio_duration": audio_samples / RATE if has_audio else 0,
            "video_rgb24_sha256": video_hash.hexdigest(),
            "audio_s16le_sha256": audio_hash.hexdigest() if has_audio else None,
            "byte_totals": dict(totals), "covered_bytes": previous,
            "warnings": warnings, "commands": commands, "packets": packets,
            "regions": regions, "end_marker_present": ended}


def convert(input_file: Path, output_file: Path) -> dict:
    if input_file.resolve() == output_file.resolve():
        raise BMVError("input and output must be different files")
    if output_file.exists() and os.path.samefile(input_file, output_file):
        raise BMVError("input and output refer to the same inode")
    data = input_file.read_bytes()
    # Decode before even creating an output file, and retain only temporary spools.
    with tempfile.TemporaryDirectory(prefix="teeny-bmv-") as directory:
        video_path = Path(directory) / "frames.pngs"
        audio_path = Path(directory) / "audio.pcm"
        with video_path.open("wb") as video, audio_path.open("wb") as audio:
            def sink(screen, palette, pcm):
                video.write(png_frame(screen, palette))
                audio.write(pcm)
            audit = decode(data, sink)
        executable = shutil.which("ffmpeg")
        if not executable:
            raise BMVError("ffmpeg executable is required on PATH to mux the AVI")
        if not output_file.parent.is_dir():
            raise BMVError(f"output directory does not exist: {output_file.parent}")
        fd, temporary = tempfile.mkstemp(prefix="." + output_file.name + ".", suffix=".avi",
                                         dir=output_file.parent)
        os.close(fd)
        try:
            args = [executable, "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
                    "-f", "image2pipe", "-framerate", str(FPS), "-vcodec", "png", "-i", str(video_path)]
            if audit["has_audio"]:
                args += ["-f", "s16le", "-ar", str(RATE), "-ac", "2", "-i", str(audio_path)]
            args += ["-map", "0:v:0", "-c:v", "ffv1", "-level", "3", "-pix_fmt", "bgr0"]
            if audit["has_audio"]:
                args += ["-map", "1:a:0", "-c:a", "pcm_s16le"]
            if audit["commands"]:
                args += ["-metadata", "comment=" + json.dumps({"bmv_commands": audit["commands"]}, separators=(",", ":"))]
            args += ["-f", "avi", temporary]
            result = subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
            if result.returncode:
                raise BMVError("AVI muxing failed: " + result.stderr.strip())
            os.chmod(temporary, 0o664)
            os.replace(temporary, output_file)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    return audit


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputFile", type=Path)
    args = parser.parse_args()
    try:
        audit = convert(args.inputFile, args.outputFile)
    except (BMVError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    for warning in audit["warnings"]:
        print(f"warning: {warning}", file=sys.stderr)
    print(f"{args.outputFile}: {audit['frames']} frames, {audit['video_duration']:.3f}s, "
          f"{audit['audio_samples_per_channel']} stereo samples; "
          f"{audit['covered_bytes']}/{audit['input_bytes']} input bytes accounted for")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# Vibe coded by Codex
"""Convert GEO/Emblaze audio-only files to 8 kHz mono, 16-bit PCM WAV.

Usage: emblazeAudio.py <inputFile> <outputDirectory>
Requires Python 3.9+ and ffmpeg on PATH; no third-party Python modules or
supporting files are needed.

The output directory must already exist. This format has no title metadata,
so the output filename is always audio.wav.

The format is the exact 28-byte vendor signature below followed immediately
by GSM 06.10 full-rate frames. Each frame has 33 bytes, a 0xD high nibble,
and 160 decoded samples. There are no timestamps or additional headers.
Decoder state continues across frames. File extensions are not significant.

Recognition requires the signature and a complete first GSM frame with the
correct marker. Other formats, including Emblaze Video 2, are rejected.
Once recognized, damaged later frame markers are replaced with a defined
silent GSM frame, preserving duration. An incomplete final frame is omitted.
Both cases produce warnings. The format has no checksum, so corruption of
otherwise legal audio bits cannot be detected. Byte insertion/deletion cannot
be reliably repaired; this converter never guesses new frame boundaries.

Output is installed atomically only after decoding and WAV validation succeed.
On failure, an existing destination is preserved and no new WAV is created.
"""

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import wave


MAGIC = b"GEO INTERACTIVE MEDIA GROUP\x1a"
FRAME_BYTES = 33
SAMPLES_PER_FRAME = 160
SAMPLE_RATE = 8000
# One LAR block followed by four RPE subframes with zero amplitude codes. Decoder
# history can leave a short residual, so this is encoded silence, not a reset.
SILENT_FRAME = bytes.fromhex("d820a2e15a" + "50004924924924" * 4)


class AudioError(ValueError):
    """Unsupported input, unrecoverable damage, or decoder failure."""


def extract_gsm(data):
    """Validate the wrapper; return complete GSM frames and recovery warnings."""
    if not data.startswith(MAGIC):
        raise AudioError("not an Emblaze audio-only file: vendor signature mismatch")
    payload = data[len(MAGIC):]
    if payload.startswith(b"\x02\x00\x00\x00"):
        raise AudioError("Emblaze Video 2 input; use emblazeVideo2.py for video files")
    if not payload or payload[0] >> 4 != 0xD:
        raise AudioError("not the supported Emblaze audio-only format: first GSM marker missing")
    if len(payload) < FRAME_BYTES:
        raise AudioError("no complete first GSM frame; cannot establish the audio-only format")

    count, trailing = divmod(len(payload), FRAME_BYTES)
    frames = bytearray(payload[:count * FRAME_BYTES])
    warnings = []
    damaged_count = 0
    first_damaged_offset = None
    for offset in range(FRAME_BYTES, len(frames), FRAME_BYTES):
        if frames[offset] >> 4 != 0xD:
            if first_damaged_offset is None:
                first_damaged_offset = len(MAGIC) + offset
            damaged_count += 1
            frames[offset:offset + FRAME_BYTES] = SILENT_FRAME
    if damaged_count:
        warnings.append(
            f"replaced {damaged_count} frame(s) with invalid GSM markers with "
            f"encoded silence; first damaged frame at byte {first_damaged_offset}"
        )
    if trailing:
        warnings.append(
            f"omitted {trailing} byte(s) of an incomplete final GSM frame "
            f"at byte {len(MAGIC) + count * FRAME_BYTES}"
        )
    return bytes(frames), warnings


def convert(input_file, output_directory):
    """Write a validated WAV; return (PCM sample count, recovery warnings)."""
    source = Path(input_file)
    directory = Path(output_directory)
    if not directory.is_dir():
        raise AudioError(f"output directory must already exist and be a directory: {directory}")
    destination = directory / "audio.wav"
    if source.resolve() == destination.resolve() or (
        destination.exists() and os.path.samefile(source, destination)
    ):
        raise AudioError("input and output must be different files")

    gsm, warnings = extract_gsm(source.read_bytes())
    samples = len(gsm) // FRAME_BYTES * SAMPLES_PER_FRAME
    # Keep the result within classic RIFF/WAVE's unsigned 32-bit chunk sizes.
    if samples * 2 > 0xFFFFFFFF - 4096:
        raise AudioError("decoded audio is too large for a classic RIFF/WAVE file")
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise AudioError("ffmpeg is required but was not found on PATH")
    with tempfile.TemporaryDirectory(prefix=".emblazeAudio-", dir=destination.parent) as work:
        raw = Path(work) / "audio.gsm"
        wav = Path(work) / "audio.wav"
        raw.write_bytes(gsm)
        result = subprocess.run(
            [ffmpeg, "-nostdin", "-hide_banner", "-v", "error", "-xerror",
             "-f", "gsm", "-c:a", "gsm", "-i", str(raw),
             "-map", "0:a:0", "-c:a", "pcm_s16le", "-ar", str(SAMPLE_RATE),
             "-ac", "1", "-map_metadata", "-1", "-fflags", "+bitexact",
             "-flags:a", "+bitexact", "-rf64", "never", "-f", "wav", str(wav)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        if result.returncode or result.stderr.strip():
            detail = result.stderr.strip() or f"exit status {result.returncode}"
            raise AudioError(f"ffmpeg failed: {detail}")
        try:
            with wave.open(str(wav), "rb") as audio:
                if (audio.getnchannels(), audio.getsampwidth(), audio.getframerate(),
                    audio.getnframes(), audio.getcomptype()) != (1, 2, SAMPLE_RATE, samples, "NONE"):
                    raise AudioError("decoder output does not have the expected PCM format/duration")
                remaining = samples
                while remaining:
                    count = min(remaining, 65536)
                    if len(audio.readframes(count)) != count * 2:
                        raise AudioError("decoder produced truncated WAV audio")
                    remaining -= count
        except (wave.Error, EOFError) as exc:
            raise AudioError(f"decoder produced an invalid WAV: {exc}") from exc
        wav.chmod(0o664)
        os.replace(wav, destination)
    return samples, warnings


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Convert Emblaze audio-only GSM files to mono 8 kHz, 16-bit PCM WAV. "
                    "Requires ffmpeg on PATH."
    )
    parser.add_argument("inputFile", help="Emblaze audio-only input file")
    parser.add_argument("outputDirectory", help="existing output directory; writes audio.wav (no title metadata)")
    args = parser.parse_args(argv)
    try:
        samples, warnings = convert(args.inputFile, args.outputDirectory)
    except (AudioError, OSError) as exc:
        print(f"emblazeAudio: {exc}", file=sys.stderr)
        return 1
    for message in warnings:
        print(f"emblazeAudio: warning: {message}", file=sys.stderr)
    destination = Path(args.outputDirectory) / "audio.wav"
    print(f"Wrote {destination}: {samples} samples, {samples / SAMPLE_RATE:.3f} s, "
          "8000 Hz mono PCM16")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# Vibe coded by Codex
"""Decode the mono Outcast SFX/GSM format to a single 16-bit PCM WAV.

Usage: outcastSoundEffects.py inputFile outputDir [-verbose]
Python 3.9+; no required third-party dependencies. An installed libgsm is an
optional accelerator; --decoder python selects the self-contained decoder.

The fixed-point GSM decoder is adapted from the algorithm and implementation
by Jutta Degener and Carsten Bormann (https://www.quut.com/gsm/).
Their permission notice is retained here:

Copyright 1992, 1993, 1994 by Jutta Degener and Carsten Bormann,
Technische Universitaet Berlin

Any use of this software is permitted provided that this notice is not
removed and that neither the authors nor the Technische Universitaet Berlin
are deemed to have made any representations as to the suitability of this
software for any purpose nor are held responsible for any defects of
this software. THERE IS ABSOLUTELY NO WARRANTY FOR THIS SOFTWARE.

As a matter of courtesy, the authors request to be informed about uses
this software has found, about bugs in this software, and about any
improvements that may be of general interest.

Berlin, 28.11.1994
Jutta Degener
Carsten Bormann

Since the original terms of 15 years ago maybe do not make our
intentions completely clear given today's refined usage of the legal
terms, we append this additional permission:

Permission to use, copy, modify, and distribute this software
for any purpose with or without fee is hereby granted,
provided that this notice is not removed and that neither
the authors nor the Technische Universitaet Berlin are
deemed to have made any representations as to the suitability
of this software for any purpose nor are held responsible
for any defects of this software. THERE IS ABSOLUTELY NO
WARRANTY FOR THIS SOFTWARE.

Berkeley/Bremen, 05.04.2009
Jutta Degener
Carsten Bormann
"""

import argparse
import ctypes
import ctypes.util
import json
import os
from pathlib import Path
import struct
import sys
import tempfile


MAGIC = 0x98765432
PROFILE = 1
FACTOR_BITS = 0x3F800000
HEADER = struct.Struct("<5I")
FRAME_BYTES = 33
FRAME_SAMPLES = 160
LAR_WIDTHS = (6, 6, 5, 5, 4, 4, 3, 3)
LAR_MIC = (-32, -32, -16, -16, -8, -8, -4, -4)
LAR_B2 = (0, 0, 4096, -5120, 188, -3584, -682, -2288)
LAR_INVA = (13107, 13107, 13107, 13107, 19223, 17476, 31454, 29708)
LTP_GAIN = (3277, 11469, 21299, 32767)
FAC = (18431, 20479, 22527, 24575, 26623, 28671, 30719, 32767)


class FormatError(ValueError):
    """Unrecognized, unsupported, or unrecoverable input; write no output."""


def saturate(x):
    return -32768 if x < -32768 else 32767 if x > 32767 else x


def multiply_round(a, b):
    return saturate((a * b + 16384) >> 15)


def unpack_frame(frame):
    """Consume all 264 bits, returning eight LARs and four subframe records.

    Each subframe is (pitch_lag, gain_index, grid, amplitude, 13 pulse_codes).
    Invalid lags are legal decoder inputs: GSM specifies previous-lag reuse.
    """
    if len(frame) != FRAME_BYTES or frame[0] >> 4 != 13:
        raise FormatError("GSM frame must be 33 bytes with a 0xD high nibble")
    bits = int.from_bytes(frame, "big")
    remaining = 260  # The upper four bits are the already checked signature.

    def take(width):
        nonlocal remaining
        remaining -= width
        return (bits >> remaining) & ((1 << width) - 1)

    lar = tuple(take(width) for width in LAR_WIDTHS)
    subframes = []
    for _ in range(4):
        lag, gain, grid, amplitude = (take(n) for n in (7, 2, 2, 6))
        pulses = tuple(take(3) for _ in range(13))
        subframes.append((lag, gain, grid, amplitude, pulses))
    assert remaining == 0
    return lar, subframes


class PythonGSMDecoder:
    """Stateful, integer GSM 06.10 RPE-LTP synthesis; ordinary 33-byte packing."""

    name = "python"

    def __init__(self):
        self.history = [0] * 120
        self.previous_lar = [0] * 8
        self.filter_memory = [0] * 9
        self.previous_lag = 40
        self.deemphasis = 0

    def close(self):
        pass

    def decode(self, frame, parameters=None):
        lar, subframes = parameters if parameters is not None else unpack_frame(frame)
        sat = saturate
        mul = multiply_round
        residual = []

        # Four RPE inverse-quantization and long-term synthesis subframes.
        for lag, gain, grid, amplitude, pulses in subframes:
            exponent = (amplitude >> 3) - 1 if amplitude > 15 else 0
            mantissa = amplitude - (exponent << 3)
            if mantissa == 0:
                exponent, mantissa = -4, 7
            else:
                while mantissa <= 7:
                    mantissa = (mantissa << 1) | 1
                    exponent -= 1
                mantissa -= 8
            shift = 6 - exponent
            rounding = (1 << (shift - 1)) if shift else 0
            excitation = [0] * 40
            for i, pulse in enumerate(pulses):
                pulse = mul(FAC[mantissa], ((pulse << 1) - 7) << 12)
                excitation[grid + 3 * i] = sat(pulse + rounding) >> shift
            if not 40 <= lag <= 120:
                lag = self.previous_lag
            self.previous_lag = lag
            history = self.history
            reconstructed = [
                sat(excitation[i] + mul(LTP_GAIN[gain], history[120 + i - lag]))
                for i in range(40)
            ]
            self.history = history[40:] + reconstructed
            residual.extend(reconstructed)

        current_lar = []
        for code, mic, bias, inverse in zip(lar, LAR_MIC, LAR_B2, LAR_INVA):
            value = mul(inverse, sat(((code + mic) << 10) - bias))
            current_lar.append(sat(value + value))
        previous = self.previous_lar
        self.previous_lar = current_lar
        memory = self.filter_memory
        deemphasis = self.deemphasis
        samples = []

        # These 13/14/13/120 regions are independent of the 40-sample RPE groups.
        for region, (start, end) in enumerate(((0, 13), (13, 27), (27, 40), (40, 160))):
            coefficients = []
            for old, new in zip(previous, current_lar):
                if region == 0:
                    value = sat(sat((old >> 2) + (new >> 2)) + (old >> 1))
                elif region == 1:
                    value = sat((old >> 1) + (new >> 1))
                elif region == 2:
                    value = sat(sat((old >> 2) + (new >> 2)) + (new >> 1))
                else:
                    value = new
                magnitude = min(abs(value), 32767)
                if magnitude < 11059:
                    reflection = magnitude << 1
                elif magnitude < 20070:
                    reflection = magnitude + 11059
                else:
                    reflection = sat((magnitude >> 2) + 26112)
                coefficients.append(-reflection if value < 0 else reflection)

            for sample in residual[start:end]:
                for i in range(7, -1, -1):
                    reflection = coefficients[i]
                    sample = sat(sample - mul(reflection, memory[i]))
                    memory[i + 1] = sat(memory[i] + mul(reflection, sample))
                memory[0] = sample
                deemphasis = sat(sample + mul(deemphasis, 28180))
                samples.append(sat(deemphasis + deemphasis) & ~7)

        self.deemphasis = deemphasis
        return struct.pack("<160h", *samples)


class NativeGSMDecoder:
    """Optional libgsm acceleration through the Python standard-library FFI."""

    name = "libgsm"
    _library = None

    def __init__(self):
        if self.__class__._library is None:
            path = ctypes.util.find_library("gsm")
            if not path:
                raise OSError("libgsm was not found")
            library = ctypes.CDLL(path)
            library.gsm_create.argtypes = []
            library.gsm_create.restype = ctypes.c_void_p
            library.gsm_destroy.argtypes = [ctypes.c_void_p]
            library.gsm_destroy.restype = None
            library.gsm_decode.argtypes = [
                ctypes.c_void_p, ctypes.POINTER(ctypes.c_ubyte),
                ctypes.POINTER(ctypes.c_int16),
            ]
            library.gsm_decode.restype = ctypes.c_int
            self.__class__._library = library
        self.library = self.__class__._library
        self.state = self.library.gsm_create()
        if not self.state:
            raise MemoryError("libgsm could not allocate decoder state")
        self.output = (ctypes.c_int16 * FRAME_SAMPLES)()

    def close(self):
        if self.state:
            self.library.gsm_destroy(self.state)
            self.state = None

    def decode(self, frame, parameters=None):
        if len(frame) != FRAME_BYTES or frame[0] >> 4 != 13:
            raise FormatError("invalid GSM frame")
        packed = (ctypes.c_ubyte * FRAME_BYTES).from_buffer_copy(frame)
        if self.library.gsm_decode(self.state, packed, self.output) != 0:
            raise FormatError("libgsm rejected the GSM frame")
        if sys.byteorder == "little":
            return bytes(self.output)
        return struct.pack("<160h", *self.output)


def make_decoder(choice):
    if choice not in ("auto", "python", "libgsm"):
        raise ValueError("decoder must be auto, python, or libgsm")
    if choice != "python":
        try:
            return NativeGSMDecoder()
        except (OSError, AttributeError):
            if choice == "libgsm":
                raise OSError("libgsm is unavailable; use --decoder python") from None
    return PythonGSMDecoder()


def parse_header(header):
    """Recognize the supported profile before reading or writing audio data."""
    if len(header) < 4 or header[:4] != b"\x32\x54\x76\x98":
        raise FormatError("not Outcast SFX: missing 0x98765432 signature")
    if len(header) != HEADER.size:
        raise FormatError("truncated Outcast SFX header; length/rate cannot be recovered")
    magic, profile, factor, size, rate = HEADER.unpack(header)
    if profile != PROFILE or factor != FACTOR_BITS:
        raise FormatError(
            "unsupported Outcast SFX profile: expected words 0x00000001 and "
            f"0x3f800000 at offsets 4 and 8; got 0x{profile:08x}, 0x{factor:08x}"
        )
    if not 1 <= rate <= 0x7FFFFFFF:
        raise FormatError("invalid/unrepresentable PCM sample rate; cannot infer a replacement")
    return {"magic": f"0x{magic:08x}", "profile_word": profile,
            "factor_bits": f"0x{factor:08x}", "factor_float": 1.0,
            "declared_data_bytes": size, "sample_rate": rate}


def decode_payload(header, payload, decoder="auto", verbose=False):
    """Decode the declared data region with deterministic corruption recovery.

    Return PCM bytes and a byte-accounting dictionary. Trailing data is never
    scanned for audio. Damaged complete frame slots become silence and reset
    decoder state. A partial final frame is omitted rather than fabricated.
    """
    metadata = dict(header)
    declared = header["declared_data_bytes"]
    available = len(payload)
    usable = min(declared, available)
    frames, partial = divmod(usable, FRAME_BYTES)
    if frames * FRAME_SAMPLES * 2 > 0xFFFFFFFF - 36:
        raise FormatError("decoded audio exceeds the RIFF/WAV 32-bit size limit")
    warnings = []
    regions = [{"offset": 0, "length": 20, "kind": "header"}]
    if declared > available:
        warnings.append(f"payload truncated: header declares {declared} bytes, found {available}")
    if declared % FRAME_BYTES:
        warnings.append(f"declared payload length {declared} is not a multiple of 33")
    if partial:
        warnings.append(f"discarded {partial} bytes of an incomplete final GSM frame")
    if available > declared:
        warnings.append(f"ignored {available - declared} bytes beyond the declared payload")

    pcm = bytearray()
    codec = None
    backend = None
    valid_frames = 0
    invalid_lags = 0
    damaged_frames = []
    frame_records = [] if verbose else None
    try:
        for i in range(frames):
            offset = i * FRAME_BYTES
            frame = payload[offset:offset + FRAME_BYTES]
            if frame[0] >> 4 != 13:
                damaged_frames.append(i)
                pcm.extend(bytes(FRAME_SAMPLES * 2))
                if codec is not None:
                    codec.close()
                    codec = None
                if verbose:
                    frame_records.append({"frame": i, "offset": 20 + offset,
                                          "status": "silence; invalid signature",
                                          "raw_hex": frame.hex()})
                continue
            parameters = unpack_frame(frame)
            invalid_lags += sum(not 40 <= sf[0] <= 120 for sf in parameters[1])
            if codec is None:
                codec = make_decoder(decoder)
                backend = codec.name
            pcm.extend(codec.decode(frame, parameters))
            valid_frames += 1
            if verbose:
                frame_records.append({"frame": i, "offset": 20 + offset,
                                      "status": "decoded", "LARc": parameters[0],
                                      "subframes": [dict(zip(
                                          ("Nc", "bc", "Mc", "xmaxc", "xmc"), sf))
                                          for sf in parameters[1]]})
    finally:
        if codec is not None:
            codec.close()
    if not valid_frames and (declared or available):
        raise FormatError("recognized Outcast SFX profile, but no complete valid GSM frames remain")
    if damaged_frames:
        warnings.append(f"replaced {len(damaged_frames)} damaged frame slots with silence; "
                        "decoder state reset after each damaged slot")
    if invalid_lags:
        warnings.append(f"{invalid_lags} out-of-range pitch lags used GSM's previous-lag rule")
    if frames:
        regions.append({"offset": 20, "length": frames * 33,
                        "kind": "GSM frame slots", "frame_count": frames,
                        "damaged_frame_indexes": damaged_frames})
    for offset, length, kind in (
        (20 + frames * 33, partial, "incomplete final GSM frame"),
        (20 + declared, max(0, available - declared), "trailing bytes outside payload"),
    ):
        if length:
            region = {"offset": offset, "length": length, "kind": kind}
            if verbose:
                region["raw_hex"] = payload[offset - 20:offset - 20 + length].hex()
            regions.append(region)
    assert sum(region["length"] for region in regions) == 20 + available
    metadata.update({"input_bytes": 20 + available, "available_data_bytes": available,
                     "decoder": backend or "none (empty stream)", "frame_slots": frames,
                     "decoded_frames": valid_frames, "damaged_frame_indexes": damaged_frames,
                     "invalid_pitch_lags": invalid_lags, "pcm_samples": frames * FRAME_SAMPLES,
                     "duration_seconds": frames * FRAME_SAMPLES / header["sample_rate"],
                     "byte_regions": regions, "warnings": warnings})
    if verbose:
        metadata["frames"] = frame_records
    return bytes(pcm), metadata


def make_wav(pcm, rate):
    """Canonical PCM WAV: exactly RIFF, fmt, and data; no metadata chunks."""
    return (struct.pack("<4sI4s4sIHHIIHH4sI", b"RIFF", 36 + len(pcm), b"WAVE",
                        b"fmt ", 16, 1, 1, rate, rate * 2, 2, 16, b"data", len(pcm))
            + pcm)


def ensure_directory(path):
    missing = []
    current = path
    while not current.exists():
        missing.append(current)
        current = current.parent
    path.mkdir(parents=True, exist_ok=True)
    for directory in reversed(missing):
        directory.chmod(directory.stat().st_mode | 0o550)


def atomic_write(path, data):
    """Publish only a complete file; remove the transient staging file on error."""
    fd, temporary = tempfile.mkstemp(prefix="." + path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fchmod(stream.fileno(), 0o644)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def convert_file(input_file, output_dir, verbose=False, decoder="auto"):
    """Convert one SFX; no destination is created before recognition and decoding."""
    source = Path(input_file)
    destination = Path(output_dir)
    with source.open("rb") as stream:
        header = parse_header(stream.read(HEADER.size))
        payload = stream.read()
    output = destination / (source.stem + ".wav")
    audit_path = destination / (source.stem + ".json")
    for target in (output, audit_path) if verbose else (output,):
        if target.resolve() == source.resolve() or (target.exists() and os.path.samefile(target, source)):
            raise FormatError("output path aliases the input file; refusing to overwrite the input")
    pcm, metadata = decode_payload(header, payload, decoder=decoder, verbose=verbose)
    metadata.update({"input_file": str(source), "output_file": str(output)})
    wav = make_wav(pcm, header["sample_rate"])
    audit = (json.dumps(metadata, indent=2) + "\n").encode("utf-8") if verbose else None
    ensure_directory(destination)
    atomic_write(output, wav)
    if verbose:
        atomic_write(audit_path, audit)
    return output, metadata


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputDir", type=Path)
    parser.add_argument("-verbose", "--verbose", action="store_true",
                        help="also write a JSON byte/bit audit and print conversion details")
    parser.add_argument("--decoder", choices=("auto", "python", "libgsm"), default="auto",
                        help="auto uses optional libgsm when installed, otherwise Python")
    args = parser.parse_args(argv)
    try:
        output, metadata = convert_file(args.inputFile, args.outputDir, args.verbose, args.decoder)
    except (OSError, ValueError, MemoryError, struct.error) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    for warning in metadata["warnings"]:
        print(f"warning: {warning}", file=sys.stderr)
    if args.verbose:
        print(f"{output}: {metadata['pcm_samples']} samples, {metadata['sample_rate']} Hz, "
              f"{metadata['duration_seconds']:.3f} s ({metadata['decoder']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# Vibe coded by Claude
"""
ZyXEL Voice Data to WAV converter.

Converts ZyXEL voice data files (.ZVD, .ZAD, .PVF, .VOX, .MSG, .AD2, .DAT,
.BIN, .zyxel, .zv, and extensionless) to standard WAV format.

Usage: zyxelVoice.py <inputFile> <outputDir>

Supports the following compression types found in the 16-byte ZyXEL header:
  Type 0:  Auto-detect (ZyXEL 4-bit or 2-bit ADPCM, or G.726 4-bit fallback)
  Type 1:  ZyXEL 2-bit ADPCM
  Type 2:  ZyXEL 3-bit ADPCM (auto-falls back to 2-bit for modem files)
  Type 3:  ZyXEL 4-bit ADPCM
  Type 5:  ZyXEL 4-bit ADPCM (alternate device numbering)
  Type 20: G.726 16kbps (2-bit) ADPCM with XOR 0x55 inversion, via ffmpeg
  Type 256: ZyXEL 2-bit ADPCM
  Type 257: ZyXEL 2-bit ADPCM
"""

import sys
import os
import struct
import wave
import subprocess
import tempfile

HEADER_SIZE = 16
MAGIC = b'ZyXEL'
SAMPLE_RATE = 8000

# ---------------------------------------------------------------------------
# ZyXEL ADPCM adaptation multiplier table  Mx[nbits-2][magnitude]
# From mgetty/vgetty voice/libpvf/zyxel.c (reverse-engineered from ZyXEL vcnvt)
# ---------------------------------------------------------------------------
Mx = [
    # 2-bit: magnitudes 0..1
    [0x3800, 0x5600, 0, 0, 0, 0, 0, 0],
    # 3-bit: magnitudes 0..3
    [0x399A, 0x3A9F, 0x4D14, 0x6607, 0, 0, 0, 0],
    # 4-bit: magnitudes 0..7
    [0x3556, 0x3556, 0x399A, 0x3A9F, 0x4200, 0x4D14, 0x6607, 0x6607],
]


def zyxel_adpcm_decode(data, nbits):
    """
    Decode ZyXEL ADPCM data (2, 3, or 4 bits per sample).

    Algorithm from mgetty/vgetty zyxel.c and Linux kernel isdn_audio.c:
      - Leaky integrator predictor:  a = (a * 4093 + 2048) >> 12
      - Delta reconstruction:        a += sign * ((mag<<1)+1) * d >> 1
      - Step-size adaptation via Mx table
      - Bits packed MSB-first (big-endian bit order)

    Returns list of signed integer samples (typically ±10000 range).
    """
    if nbits not in (2, 3, 4):
        raise ValueError(f"nbits must be 2, 3, or 4, got {nbits}")

    bitmask_n = (1 << nbits) - 1       # mask for full code
    bitmask_mag = (1 << (nbits - 1)) - 1  # mask for magnitude only

    a = 0   # accumulator / predictor
    d = 5   # step size (initial)
    samples = []

    # Bit-reader state (MSB-first, matching mgetty read_bits)
    buf = 0
    nleft = 0
    pos = 0

    while True:
        # Feed bytes into bit buffer
        while nleft < nbits:
            if pos >= len(data):
                return samples
            buf = (buf << 8) | data[pos]
            pos += 1
            nleft += 8

        # Extract next code (MSB-first)
        nleft -= nbits
        e = (buf >> nleft) & bitmask_n

        # 4-bit special: code 0 forces step to 4 (silence handling)
        if nbits == 4 and e == 0:
            d = 4

        # Split into sign and magnitude
        sign = -1 if (e >> (nbits - 1)) else 1
        mag = e & bitmask_mag

        # Leaky integrator (decay factor ≈ 4093/4096 ≈ 0.99927)
        a = (a * 4093 + 2048) >> 12

        # Reconstruct delta and accumulate
        # C code: a += sign * ((e << 1) + 1) * d >> 1;
        # Operator precedence: (sign * ((mag<<1)+1) * d) >> 1
        a += (sign * ((mag << 1) + 1) * d) >> 1

        # Rounding correction when step is odd
        if d & 1:
            a += 1

        samples.append(a)

        # Adapt step size
        d = (d * Mx[nbits - 2][mag] + 0x2000) >> 14
        if d < 5:
            d = 5

    return samples


def alaw_to_linear(alaw_byte):
    """Decode one ITU-T G.711 A-law byte to signed 16-bit linear PCM."""
    alaw_byte ^= 0x55
    sign = alaw_byte & 0x80
    exponent = (alaw_byte >> 4) & 0x07
    mantissa = alaw_byte & 0x0F
    if exponent == 0:
        sample = (mantissa << 4) + 8
    else:
        sample = ((mantissa << 4) + 0x108) << (exponent - 1)
    return -sample if sign == 0 else sample


def decode_alaw(data):
    """Decode A-law encoded byte stream to list of signed 16-bit samples."""
    return [alaw_to_linear(b) for b in data]


def zyxel_adpcm_decode_type20(data):
    """
    Decode type 20 ZyXEL 4-bit ADPCM variant.

    Uses the standard ZyXEL ADPCM algorithm (leaky integrator predictor,
    Mx adaptation table) at 4 bits per sample, with the step size (d) reset
    to its initial value every 32 samples to prevent accumulator divergence.
    The predictor (a) remains continuous across resets.

    High nibble is decoded first within each byte (MSB-first packing).
    """
    STEP_RESET_INTERVAL = 32

    a = 0   # accumulator / predictor (continuous)
    d = 5   # step size (reset periodically)
    samples = []
    sample_count = 0

    for byte in data:
        for shift in (4, 0):
            e = (byte >> shift) & 0xF

            # 4-bit special: code 0 forces step to 4
            if e == 0:
                d = 4

            sign = -1 if (e >> 3) else 1
            mag = e & 7

            a = (a * 4093 + 2048) >> 12
            a += (sign * ((mag << 1) + 1) * d) >> 1
            if d & 1:
                a += 1

            samples.append(a)

            d = (d * Mx[2][mag] + 0x2000) >> 14
            if d < 5:
                d = 5

            sample_count += 1
            if sample_count % STEP_RESET_INTERVAL == 0:
                d = 5

    return samples


def decode_g726_via_ffmpeg(data, code_size=2):
    """
    Decode G.726 ADPCM using ffmpeg.
    code_size: bits per sample (2=16kbps, 3=24kbps, 4=32kbps).
    Falls back to raw ZyXEL 4-bit ADPCM if ffmpeg is not available.
    """
    with tempfile.NamedTemporaryFile(suffix='.raw', delete=False) as tmp_in:
        tmp_in.write(data)
        tmp_in_path = tmp_in.name

    tmp_out_path = tmp_in_path + '.wav'

    try:
        result = subprocess.run(
            ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
             '-f', 'g726', '-code_size', str(code_size),
             '-ar', str(SAMPLE_RATE),
             '-i', tmp_in_path, tmp_out_path],
            capture_output=True, timeout=30
        )
        if result.returncode == 0 and os.path.exists(tmp_out_path):
            with wave.open(tmp_out_path, 'r') as wf:
                frames = wf.readframes(wf.getnframes())
                return list(struct.unpack(f'<{wf.getnframes()}h', frames))
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    finally:
        try:
            os.unlink(tmp_in_path)
        except OSError:
            pass
        try:
            os.unlink(tmp_out_path)
        except OSError:
            pass

    # Fallback: decode as ZyXEL 4-bit (may not be perfect)
    return zyxel_adpcm_decode(data, 4)


def decode_is_valid(samples, max_threshold=100000, check_count=500):
    """
    Check whether an ADPCM decode produced reasonable (non-explosive) output.
    The ZyXEL ADPCM accumulator explodes to astronomical values when given
    data encoded with a different bit depth.
    """
    if not samples:
        return False
    check = samples[:check_count]
    return max(abs(s) for s in check) < max_threshold


def parse_header(header_bytes):
    """
    Parse the 16-byte ZyXEL voice data header.

    Returns dict with:
      magic:      b'ZyXEL'
      version:    int (always 2)
      flags:      int (byte 6: 0x00 or 0x20 for ZAD files)
      subtype:    int (byte 7: 0x00 or 0x03 for AD2/ZAD files)
      comp_type:  int (16-bit LE at offset 10-11: compression/codec ID)
      reserved:   bytes (bytes 8-9 and 12-15, always zero)
    """
    if len(header_bytes) < HEADER_SIZE:
        raise ValueError("File too small for ZyXEL header")
    if header_bytes[:5] != MAGIC:
        raise ValueError(f"Bad magic: expected 'ZyXEL', got {header_bytes[:5]!r}")

    version = header_bytes[5]
    flags = header_bytes[6]
    subtype = header_bytes[7]
    comp_type = struct.unpack_from('<H', header_bytes, 10)[0]

    return {
        'magic': header_bytes[:5],
        'version': version,
        'flags': flags,
        'subtype': subtype,
        'comp_type': comp_type,
    }


def decode_audio(data, comp_type):
    """
    Decode audio data based on compression type.
    Returns (samples_list, codec_description_string).
    """

    # Type 1: ZyXEL 2-bit ADPCM (most common)
    if comp_type == 1:
        return zyxel_adpcm_decode(data, 2), "ZyXEL 2-bit ADPCM"

    # Type 3: ZyXEL 4-bit ADPCM (PBX/DECT devices)
    if comp_type == 3:
        return zyxel_adpcm_decode(data, 4), "ZyXEL 4-bit ADPCM"

    # Type 5: ZyXEL 4-bit ADPCM (ISDN devices, alternate numbering)
    if comp_type == 5:
        return zyxel_adpcm_decode(data, 4), "ZyXEL 4-bit ADPCM (type 5)"

    # Type 2: 3-bit on PBX devices, 2-bit on modem devices
    if comp_type == 2:
        samples_3 = zyxel_adpcm_decode(data, 3)
        if decode_is_valid(samples_3):
            return samples_3, "ZyXEL 3-bit ADPCM"
        return zyxel_adpcm_decode(data, 2), "ZyXEL 2-bit ADPCM (modem)"

    # Type 20 (0x14): Unknown proprietary 4-bit codec from ZyXEL modems.
    # Best available decode: G.726 2-bit with XOR 0x55 byte inversion.
    # This produces recognizable but noisy output - the exact codec has
    # not been fully identified.
    if comp_type == 20:
        xored = bytes(b ^ 0x55 for b in data)
        return decode_g726_via_ffmpeg(xored, code_size=2), "ZyXEL type 20 (G.726 2-bit approx)"

    # Type 256 (byte10=0x00, byte11=0x01): 2-bit ADPCM with flag
    if comp_type == 256:
        return zyxel_adpcm_decode(data, 2), "ZyXEL 2-bit ADPCM (variant)"

    # Type 257 (byte10=0x01, byte11=0x01): 2-bit ADPCM with flag
    if comp_type == 257:
        return zyxel_adpcm_decode(data, 2), "ZyXEL 2-bit ADPCM (variant)"

    # Type 0: auto-detect (try ZyXEL 4-bit, then 2-bit, then G.726 fallback)
    if comp_type == 0:
        for nbits in [4, 2]:
            samples = zyxel_adpcm_decode(data, nbits)
            if decode_is_valid(samples):
                return samples, f"ZyXEL {nbits}-bit ADPCM (auto-detected)"
        xored = bytes(b ^ 0x55 for b in data)
        return decode_g726_via_ffmpeg(xored, code_size=2), "G.726 2-bit approx (fallback)"

    # Unknown type: try all ZyXEL bit depths, then G.726
    for nbits in [2, 3, 4]:
        samples = zyxel_adpcm_decode(data, nbits)
        if decode_is_valid(samples):
            return samples, f"ZyXEL {nbits}-bit ADPCM (guessed for type {comp_type})"
    xored = bytes(b ^ 0x55 for b in data)
    return decode_g726_via_ffmpeg(xored, code_size=2), f"G.726 2-bit approx (guessed for type {comp_type})"


def samples_to_wav(samples, wav_path, sample_rate=SAMPLE_RATE):
    """
    Write samples to a 16-bit mono WAV file.
    Applies automatic peak normalization to ~90% of full scale.
    """
    if not samples:
        raise ValueError("No samples to write")

    max_abs = max(abs(s) for s in samples)
    if max_abs == 0:
        max_abs = 1

    # Normalize: target peak at 90% of int16 max (29491)
    target_peak = 29491
    scale = target_peak / max_abs

    with wave.open(wav_path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        pcm = b''
        for s in samples:
            s16 = max(-32768, min(32767, int(s * scale)))
            pcm += struct.pack('<h', s16)
        wf.writeframes(pcm)


def convert_file(input_path, output_dir):
    """
    Convert a ZyXEL voice data file to WAV.
    Returns (wav_filename, codec_description, duration_seconds, num_samples).
    """
    with open(input_path, 'rb') as f:
        header_bytes = f.read(HEADER_SIZE)
        audio_data = f.read()

    hdr = parse_header(header_bytes)
    samples, codec_desc = decode_audio(audio_data, hdr['comp_type'])
    duration = len(samples) / SAMPLE_RATE

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    # Sanitize filename
    safe_name = "".join(c if c.isalnum() or c in '-_.' else '_' for c in base_name)
    wav_filename = f"{safe_name}.wav"
    wav_path = os.path.join(output_dir, wav_filename)

    samples_to_wav(samples, wav_path)

    return wav_filename, codec_desc, duration, len(samples), hdr


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(input_path):
        print(f"Error: '{input_path}' is not a file", file=sys.stderr)
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    wav_name, codec, duration, num_samples, hdr = convert_file(input_path, output_dir)
    wav_path = os.path.join(output_dir, wav_name)

    print(f"Input:       {input_path}")
    print(f"Compression: type {hdr['comp_type']} -> {codec}")
    print(f"Flags:       0x{hdr['flags']:02X}, Subtype: 0x{hdr['subtype']:02X}")
    print(f"Samples:     {num_samples} @ {SAMPLE_RATE} Hz")
    print(f"Duration:    {duration:.2f}s")
    print(f"Output:      {wav_path}")


if __name__ == '__main__':
    main()

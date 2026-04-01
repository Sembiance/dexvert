#!/usr/bin/env python3
# Vibe coded by Claude
"""dvsm.py - Convert WinRec DVSM (.DVS/.SND) sound files to WAV format.

Usage: dvsm.py <inputFile> <outputDir>

Supports all DVSM pack types found in practice:
  - Pack 0: Unpacked 8-bit signed PCM (mono/stereo)
  - Pack 2: Delta-packed 16-bit signed PCM (mono/stereo)
  - Pack 4: Voice-packed 16-bit signed PCM (mono/stereo)
"""

import sys
import os
import struct
import math
import wave
import array

# Atari Falcon CODEC sample rates (Hz), indexed 0-7
# Derived from 25.175 MHz master clock: rate = 25175000 / ((prescale+1) * 256)
# WinRec indices 0-7 map to hardware prescale values 11,9,7,5,4,3,2,1:
#   Divisors: 3072, 2560, 2048, 1536, 1280, 1024, 768, 512
CODEC_RATES = [8195, 9834, 12293, 16390, 19668, 24585, 32780, 49170]

# Delta pack exponential base constant (from WinRec documentation)
DELTA_BASE = 1.084618362

# Voice pack 4-bit delta table (16 entries for nibble values 0-15)
VOICE_TABLE = [
    -8192, -4096, -2048, -1024, -512, -256, -64, 0,
    64, 256, 512, 1024, 2048, 4096, 8192, 16384
]


def build_delta_table():
    """Build the standard 256-entry delta pack lookup table.

    Maps unsigned byte values (0-255, interpreted as signed -128..127)
    to signed 16-bit delta values using the exponential formula:
      f(x) = 0               for x == 0
      f(x) = round(BASE^x)   for x > 0  (indices 1..127)
      f(x) = -round(BASE^-x) for x < 0  (indices 128..255 as signed -128..-1)

    Values are clamped to the signed 16-bit range [-32768, 32767].
    """
    table = [0] * 256
    for i in range(1, 128):
        val = int(round(DELTA_BASE ** i))
        table[i] = min(val, 32767)
    for i in range(128, 256):
        exp = 256 - i  # convert unsigned to positive exponent
        val = int(round(DELTA_BASE ** exp))
        table[i] = max(-min(val, 32768), -32768)
    return table


def build_delta_table_from_pack(pack_data):
    """Build a delta table from a PACK extension block.

    The PACK extension provides 128 bytes: 64 big-endian signed 16-bit values
    for positive indices 1-64. The table is symmetric: table[-x] = -table[x].
    Indices beyond the provided range use the standard exponential formula.
    """
    table = build_delta_table()  # start with standard
    n_entries = len(pack_data) // 2
    for i in range(min(n_entries, 127)):
        val = struct.unpack('>h', pack_data[i * 2:i * 2 + 2])[0]
        table[i + 1] = val
        table[255 - i] = -val
    return table


def parse_extensions(data, headlen):
    """Parse extension blocks between offset 16 and headlen.

    Extension block format:
      4 bytes: cookie (ASCII identifier)
      2 bytes: block length (big-endian uint16, includes cookie + length fields)
      N bytes: data (length - 6 bytes)
    """
    extensions = {}
    offset = 16
    while offset + 6 <= headlen:
        cookie = data[offset:offset + 4]
        block_len = struct.unpack('>H', data[offset + 4:offset + 6])[0]
        if block_len < 6 or offset + block_len > headlen:
            break
        ext_data = data[offset + 6:offset + block_len]
        try:
            cookie_str = cookie.decode('ascii')
        except UnicodeDecodeError:
            cookie_str = cookie.hex()
        extensions[cookie_str] = ext_data
        offset += block_len
    return extensions


def clamp16(val):
    """Clamp an integer to signed 16-bit range [-32768, 32767]."""
    if val > 32767:
        return 32767
    if val < -32768:
        return -32768
    return val


def decode_delta_mono(audio_data, blocklen, delta_table):
    """Decode delta-packed mono 16-bit audio data into sample array.

    Mono delta data is a single continuous stream: one initial 16-bit sample
    followed by all delta bytes.  The blocklen header field reflects the
    recording buffer size but does NOT insert new initial samples into the
    stream (unlike stereo, where each block carries fresh L/R seed values).
    """
    samples = array.array('h')
    if len(audio_data) < 2:
        return samples

    acc = struct.unpack('>h', audio_data[0:2])[0]
    samples.append(acc)

    chunk = audio_data[2:]
    for byte_val in chunk:
        acc = clamp16(acc + delta_table[byte_val])
        samples.append(acc)

    return samples


def decode_delta_stereo(audio_data, blocklen, delta_table):
    """Decode delta-packed stereo 16-bit audio data into L/R sample arrays."""
    left_arr = array.array('h')
    right_arr = array.array('h')
    offset = 0
    data_len = len(audio_data)

    while offset < data_len:
        if offset + 4 > data_len:
            break
        l_acc = struct.unpack('>h', audio_data[offset:offset + 2])[0]
        r_acc = struct.unpack('>h', audio_data[offset + 2:offset + 4])[0]
        left_arr.append(l_acc)
        right_arr.append(r_acc)
        offset += 4

        block_pairs = (blocklen - 4) // 2 if blocklen > 4 else (data_len - offset) // 2
        count = min(block_pairs, (data_len - offset) // 2)
        chunk = audio_data[offset:offset + count * 2]
        for j in range(0, len(chunk), 2):
            l_acc = clamp16(l_acc + delta_table[chunk[j]])
            r_acc = clamp16(r_acc + delta_table[chunk[j + 1]])
            left_arr.append(l_acc)
            right_arr.append(r_acc)
        offset += count * 2

    return left_arr, right_arr


def decode_voice_mono(audio_data, blocklen):
    """Decode voice-packed mono 16-bit audio data.

    Each byte after the initial sample contains two 4-bit delta indices
    (high nibble first, low nibble second), each producing one sample.
    Mono data is a single continuous stream (see decode_delta_mono).
    """
    samples = array.array('h')
    if len(audio_data) < 2:
        return samples

    acc = struct.unpack('>h', audio_data[0:2])[0]
    samples.append(acc)

    for byte_val in audio_data[2:]:
        hi = (byte_val >> 4) & 0x0F
        lo = byte_val & 0x0F
        acc = clamp16(acc + VOICE_TABLE[hi])
        samples.append(acc)
        acc = clamp16(acc + VOICE_TABLE[lo])
        samples.append(acc)

    return samples


def decode_voice_stereo(audio_data, blocklen):
    """Decode voice-packed stereo 16-bit audio data.

    Each byte after the initial samples contains a 4-bit left delta (high
    nibble) and a 4-bit right delta (low nibble), producing one stereo pair.
    """
    left_arr = array.array('h')
    right_arr = array.array('h')
    offset = 0
    data_len = len(audio_data)

    while offset < data_len:
        if offset + 4 > data_len:
            break
        l_acc = struct.unpack('>h', audio_data[offset:offset + 2])[0]
        r_acc = struct.unpack('>h', audio_data[offset + 2:offset + 4])[0]
        left_arr.append(l_acc)
        right_arr.append(r_acc)
        offset += 4

        block_bytes = blocklen - 4 if blocklen > 4 else data_len - offset
        count = min(block_bytes, data_len - offset)
        chunk = audio_data[offset:offset + count]
        for byte_val in chunk:
            hi = (byte_val >> 4) & 0x0F
            lo = byte_val & 0x0F
            l_acc = clamp16(l_acc + VOICE_TABLE[hi])
            r_acc = clamp16(r_acc + VOICE_TABLE[lo])
            left_arr.append(l_acc)
            right_arr.append(r_acc)
        offset += count

    return left_arr, right_arr


def interleave_stereo(left_arr, right_arr):
    """Interleave separate L/R arrays into a single stereo sample array."""
    n = len(left_arr)
    out = array.array('h', bytes(n * 4))
    out[0::2] = left_arr
    out[1::2] = right_arr
    return out


def apply_fade_out(out, channels, sample_rate):
    """Apply a short fade-out to prevent end-of-file clicks.

    Without this, samples that end at a non-zero DC offset cause an audible
    pop when playback stops (abrupt jump to silence).  A 5ms linear ramp to
    zero eliminates this artifact.
    """
    fade_samples = max(1, int(sample_rate * 0.005))  # 5ms
    total_samples = len(out)
    frame_count = total_samples // channels

    if frame_count < fade_samples * 2:
        return  # too short to fade

    for i in range(fade_samples):
        scale = (fade_samples - 1 - i) / fade_samples
        frame_idx = frame_count - fade_samples + i
        for ch in range(channels):
            idx = frame_idx * channels + ch
            out[idx] = int(out[idx] * scale)



def convert_dvsm(input_path, output_dir):
    """Convert a single DVSM file to WAV format."""
    with open(input_path, 'rb') as f:
        data = f.read()

    file_size = len(data)
    basename = os.path.basename(input_path)

    if file_size < 16:
        print(f"Error: {basename} too small ({file_size} bytes)", file=sys.stderr)
        return False
    if data[:4] != b'DVSM' or data[4:6] != b'\x00\x00':
        print(f"Error: {basename} invalid DVSM magic", file=sys.stderr)
        return False

    # Parse 16-byte base header (big-endian, Motorola 68000 byte order)
    headlen = struct.unpack('>H', data[6:8])[0]
    freq = struct.unpack('>H', data[8:10])[0]
    pack = data[10]
    mode = data[11]
    blocklen = struct.unpack('>I', data[12:16])[0]

    if headlen < 16 or headlen > file_size:
        print(f"Error: {basename} invalid header length {headlen}", file=sys.stderr)
        return False

    # Sample rate: 0-7 = CODEC index, >256 = direct Hz
    if freq <= 7:
        sample_rate = CODEC_RATES[freq]
        freq_desc = f"CODEC index {freq} -> {sample_rate} Hz"
    elif freq > 256:
        sample_rate = freq
        freq_desc = f"{freq} Hz"
    else:
        sample_rate = freq
        freq_desc = f"{freq} Hz (unusual)"

    # Mode bits: bit 0 = 0:8-bit/1:16-bit, bit 1 = 0:stereo/1:mono
    is_16bit = (mode & 0x01) != 0
    is_mono = (mode & 0x02) != 0
    channels = 1 if is_mono else 2
    bits = 16 if is_16bit else 8
    ch_str = "mono" if is_mono else "stereo"
    pack_names = {0: "unpacked", 2: "delta", 4: "voice", 5: "ADPCM"}

    # Parse any extension blocks (between base header and audio data)
    extensions = {}
    if headlen > 16:
        extensions = parse_extensions(data, headlen)

    # Build delta table (possibly customized by PACK extension)
    delta_table = build_delta_table()
    if 'PACK' in extensions:
        delta_table = build_delta_table_from_pack(extensions['PACK'])

    audio_data = data[headlen:]
    audio_len = len(audio_data)

    print(f"{basename}: {file_size} bytes, {freq_desc}, "
          f"pack={pack} ({pack_names.get(pack, '?')}), {bits}-bit {ch_str}, "
          f"blocklen={blocklen}, audio={audio_len} bytes")
    for cookie, ext_data in extensions.items():
        print(f"  Extension '{cookie}': {len(ext_data)} data bytes")

    # Decode audio based on pack type
    out = None  # array.array('h') for 16-bit formats
    if pack == 0:
        # Unpacked PCM
        if is_16bit:
            frame_size = 2 * channels
            n_frames = audio_len // frame_size
            consumed = n_frames * frame_size
            out = array.array('h')
            for i in range(0, consumed, 2):
                out.append(struct.unpack('>h', audio_data[i:i + 2])[0])
            wav_bps = 16
        else:
            # Signed 8-bit -> unsigned 8-bit for WAV (XOR 0x80)
            n_frames = audio_len // channels
            consumed = n_frames * channels
            wav_data = bytes((b ^ 0x80) for b in audio_data[:consumed])
            wav_bps = 8

    elif pack == 2:
        # Delta packed (16-bit only per WinRec spec)
        if is_mono:
            out = decode_delta_mono(audio_data, blocklen, delta_table)
        else:
            left, right = decode_delta_stereo(audio_data, blocklen, delta_table)
            out = interleave_stereo(left, right)
        n_frames = len(out) // channels
        wav_bps = 16

    elif pack == 4:
        # Voice packed (16-bit only per WinRec spec)
        if is_mono:
            out = decode_voice_mono(audio_data, blocklen)
        else:
            left, right = decode_voice_stereo(audio_data, blocklen)
            out = interleave_stereo(left, right)
        n_frames = len(out) // channels
        wav_bps = 16

    elif pack == 5:
        print(f"  Error: ADPCM (pack=5) not implemented", file=sys.stderr)
        return False
    else:
        print(f"  Error: unknown pack type {pack}", file=sys.stderr)
        return False

    # For 16-bit formats: apply fade-out then convert to WAV byte order
    if out is not None:
        apply_fade_out(out, channels, sample_rate)
        if sys.byteorder == 'big':
            out.byteswap()
        wav_data = out.tobytes()

    # Write output WAV
    stem = os.path.splitext(basename)[0] or basename
    output_name = stem + '.wav'
    output_path = os.path.join(output_dir, output_name)

    with wave.open(output_path, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(wav_bps // 8)
        wf.setframerate(sample_rate)
        wf.writeframes(wav_data)

    duration = n_frames / sample_rate if sample_rate > 0 else 0
    print(f"  -> {output_name}: {n_frames} frames, {duration:.3f}s, "
          f"{wav_bps}-bit {ch_str} @ {sample_rate} Hz")
    return True


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(input_path):
        print(f"Error: '{input_path}' not found", file=sys.stderr)
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    if not convert_dvsm(input_path, output_dir):
        sys.exit(1)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# Vibe coded by Claude
"""
sonixInstrument.py - Aegis Sonix Instrument Converter

Converts Aegis Sonix .instr and .ss files to WAV format.

Usage: sonixInstrument.py <inputFile> <outputDir>

Supports:
  - SampledSound .instr files (128 bytes) referencing .ss sample files
  - Synthesis .instr files (502 bytes) with embedded waveform data
  - Standalone .ss sampled sound files

The Aegis Sonix was a music composition program for the Amiga (1987-91)
by Mark Riley / Aegis Development.
"""

import sys
import os
import struct
import wave

# The sample rate is not stored in the file format. It is determined by the
# Sonix playback engine's period calculation. The EaglePlayer Sonix driver
# uses base period constant $1AB9 (6841) which, after /16 modulation scaling,
# yields hardware period ~428 → ~8363 Hz (NTSC). However, testing against
# known samples suggests the native recording rate is approximately 12060 Hz
# (Amiga PAL period ~294). This is used as the default for conversion.
DEFAULT_SAMPLE_RATE = 12060

# Header sizes
SS_HEADER_SIZE = 62       # .ss file header is 62 bytes
SS_FOOTER_SIZE = 4        # .ss file footer (4 bytes: "AMII" or zeros)
INSTR_SAMPLED_SIZE = 128  # SampledSound .instr file size
INSTR_SYNTH_SIZE = 502    # Synthesis .instr file size
MAGIC_SAMPLED = b'SampledSound'
MAGIC_SYNTH = b'Synthesis\x00\x00\x00'


def parse_ss(filepath):
    """Parse an Aegis Sonix .ss sampled sound file.

    File layout:
      [0x00-0x01] uint16 BE: w1 - base waveform unit length
      [0x02-0x03] uint16 BE: w2 - loop control (0=one-shot, =w1 means no loop,
                                   other: loop starts at w2*2^oct offset)
      [0x04]      uint8:     min_octave
      [0x05]      uint8:     max_octave
      [0x06]      uint8:     reserved (always 0x00)
      [0x07]      uint8:     volume/flags (0xFF typical, varies)
      [0x08-0x3D] 54 bytes:  reserved/padding (may contain runtime data)
      [0x3E-...]  audio:     signed 8-bit PCM, organized by octave
      [last 4]    footer:    "AMII" or 4 zero bytes

    Audio data for each octave n (from min_octave to max_octave) is
    w1 * 2^n bytes of signed 8-bit PCM, stored sequentially.
    """
    with open(filepath, 'rb') as f:
        data = f.read()

    if len(data) < SS_HEADER_SIZE:
        raise ValueError(f"File too small for .ss format: {len(data)} bytes")

    # Parse header
    w1 = struct.unpack('>H', data[0:2])[0]
    w2 = struct.unpack('>H', data[2:4])[0]
    min_octave = data[4]
    max_octave = data[5]
    reserved1 = data[6]
    flags = data[7]
    padding = data[8:SS_HEADER_SIZE]

    # Validate
    if w1 == 0:
        raise ValueError("Invalid .ss file: w1 (base unit) is 0")
    if min_octave > max_octave:
        raise ValueError(f"Invalid octave range: min={min_octave} > max={max_octave}")

    # Calculate expected audio data size
    total_audio = sum(w1 * (1 << n) for n in range(min_octave, max_octave + 1))
    expected_with_footer = SS_HEADER_SIZE + total_audio + SS_FOOTER_SIZE
    expected_no_footer = SS_HEADER_SIZE + total_audio

    # Determine actual audio size - handle files with or without footer,
    # and truncated files
    footer = b''
    if len(data) == expected_with_footer:
        footer = data[-SS_FOOTER_SIZE:]
        audio_end = len(data) - SS_FOOTER_SIZE
    elif len(data) == expected_no_footer:
        audio_end = len(data)
    elif len(data) < expected_no_footer:
        # Truncated file - extract whatever audio is available
        audio_end = len(data)
        total_audio = audio_end - SS_HEADER_SIZE
    else:
        # File is larger than expected - assume 4-byte footer
        footer = data[-SS_FOOTER_SIZE:]
        audio_end = len(data) - SS_FOOTER_SIZE
        total_audio = audio_end - SS_HEADER_SIZE

    # Determine loop type
    if w2 == 0:
        loop_type = 'one-shot'
    elif w2 == w1:
        loop_type = 'no-loop'
    else:
        loop_type = 'loop'

    # Extract per-octave audio data
    octaves = {}
    offset = SS_HEADER_SIZE
    for n in range(min_octave, max_octave + 1):
        octave_size = w1 * (1 << n)
        available = audio_end - offset
        if available <= 0:
            break
        actual_size = min(octave_size, available)
        raw = data[offset:offset + actual_size]
        samples = [b if b < 128 else b - 256 for b in raw]
        octaves[n] = samples
        offset += actual_size

    return {
        'w1': w1,
        'w2': w2,
        'min_octave': min_octave,
        'max_octave': max_octave,
        'reserved1': reserved1,
        'flags': flags,
        'padding': padding,
        'loop_type': loop_type,
        'footer': footer,
        'octaves': octaves,
        'total_audio_bytes': total_audio,
    }


def parse_instr(filepath):
    """Parse an Aegis Sonix .instr instrument file.

    Detects type from file size and 12-byte magic at offset 0:
      "SampledSound" (128 bytes) → references a .ss sample
      "Synthesis" (502 bytes)    → embedded waveform data
      502 bytes with no magic    → treated as Synthesis (e.g. Silence)
      "FORM" magic               → IFF/8SVX format (not supported, returns None)
    """
    with open(filepath, 'rb') as f:
        data = f.read()

    magic = data[0:12]

    # Skip IFF/8SVX files (Amiga IFF format, not native Sonix)
    if data[0:4] == b'FORM':
        return None

    if len(data) == INSTR_SAMPLED_SIZE and magic == MAGIC_SAMPLED:
        return parse_instr_sampled(data, filepath)
    elif len(data) == INSTR_SYNTH_SIZE:
        # 502-byte files: Synthesis (with or without magic)
        return parse_instr_synthesis(data, filepath)
    elif magic == MAGIC_SAMPLED:
        return parse_instr_sampled(data, filepath)
    else:
        raise ValueError(f"Unknown .instr format: size={len(data)}, magic={magic[:12]!r}")


def parse_instr_sampled(data, filepath):
    """Parse a SampledSound .instr file (128 bytes).

    Layout (all multi-byte values are big-endian):
      [0x00-0x0B] 12 bytes:  Magic "SampledSound"
      [0x0C-0x1F] 20 bytes:  Zero padding
      [0x20-0x23]  4 bytes:  Runtime SSTech pointer (stale in saved files;
                              overwritten by EaglePlayer at load time)
      [0x24-0x43] 32 bytes:  Instrument name (null-terminated, trailing ghost data)
      [0x44-0x63] 32 bytes:  Sample .ss reference name (null-terminated, trailing ghost data)
      [0x64-0x67]  4 bytes:  Runtime .ss data pointer (stale in saved files)
      [0x68-0x7F] 24 bytes:  Playback parameters (12 x uint16 BE)
    """
    if len(data) != INSTR_SAMPLED_SIZE:
        raise ValueError(f"SampledSound .instr must be {INSTR_SAMPLED_SIZE} bytes, got {len(data)}")

    header_padding = data[0x0C:0x20]
    runtime_ptr1 = struct.unpack('>I', data[0x20:0x24])[0]

    instr_name_raw = data[0x24:0x44]
    instr_name = instr_name_raw.split(b'\x00')[0].decode('ascii', errors='replace')

    sample_name_raw = data[0x44:0x64]
    sample_name = sample_name_raw.split(b'\x00')[0].decode('ascii', errors='replace')

    runtime_ptr2 = struct.unpack('>I', data[0x64:0x68])[0]

    params = []
    for i in range(12):
        offset = 0x68 + i * 2
        val = struct.unpack('>H', data[offset:offset + 2])[0]
        params.append(val)

    volume = params[0] & 0xFF

    return {
        'type': 'SampledSound',
        'magic': MAGIC_SAMPLED,
        'header_padding': header_padding,
        'runtime_ptr1': runtime_ptr1,
        'instr_name': instr_name,
        'instr_name_raw': instr_name_raw,
        'sample_name': sample_name,
        'sample_name_raw': sample_name_raw,
        'runtime_ptr2': runtime_ptr2,
        'params': params,
        'volume': volume,
        'filepath': filepath,
    }


def parse_instr_synthesis(data, filepath):
    """Parse a Synthesis .instr file (502 bytes).

    Layout:
      [0x00-0x0B]   12 bytes:  Magic "Synthesis\\x00\\x00\\x00" (or zeros)
      [0x0C-0x1F]   20 bytes:  Zero padding
      [0x20-0x23]    4 bytes:  Runtime pointer (stale)
      [0x24-0x43]   32 bytes:  Instrument name (null-terminated, trailing ghost data)
      [0x44-0xC3]  128 bytes:  Waveform 1 (one cycle, signed 8-bit samples)
      [0xC4-0x143] 128 bytes:  Waveform 2 / modulation data
      [0x144-0x1C3] 128 bytes: Waveform 3 / LFO data
      [0x1C4-0x1F5]  50 bytes: Synthesis parameters (envelope, filter, etc.)
    """
    if len(data) != INSTR_SYNTH_SIZE:
        raise ValueError(f"Synthesis .instr must be {INSTR_SYNTH_SIZE} bytes, got {len(data)}")

    header_padding = data[0x0C:0x20]
    runtime_ptr = struct.unpack('>I', data[0x20:0x24])[0]

    instr_name_raw = data[0x24:0x44]
    instr_name = instr_name_raw.split(b'\x00')[0].decode('ascii', errors='replace')

    waveform1_raw = data[0x44:0xC4]
    waveform2_raw = data[0xC4:0x144]
    waveform3_raw = data[0x144:0x1C4]
    synth_params = data[0x1C4:0x1F6]

    def to_signed(raw):
        return [b if b < 128 else b - 256 for b in raw]

    return {
        'type': 'Synthesis',
        'magic': data[0:12],
        'header_padding': header_padding,
        'runtime_ptr': runtime_ptr,
        'instr_name': instr_name,
        'instr_name_raw': instr_name_raw,
        'waveform1': to_signed(waveform1_raw),
        'waveform1_raw': waveform1_raw,
        'waveform2': to_signed(waveform2_raw),
        'waveform2_raw': waveform2_raw,
        'waveform3': to_signed(waveform3_raw),
        'waveform3_raw': waveform3_raw,
        'synth_params': synth_params,
        'filepath': filepath,
    }


def samples_to_wav(samples, filepath, sample_rate=DEFAULT_SAMPLE_RATE):
    """Write signed 8-bit PCM samples to a 16-bit WAV file."""
    with wave.open(filepath, 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        pcm16 = bytearray(len(samples) * 2)
        for i, s in enumerate(samples):
            val = max(-32768, min(32767, s * 256))
            struct.pack_into('<h', pcm16, i * 2, val)
        w.writeframes(bytes(pcm16))


def convert_ss(filepath, output_dir):
    """Convert a .ss sampled sound file to WAV(s)."""
    ss = parse_ss(filepath)
    basename = os.path.splitext(os.path.basename(filepath))[0]
    sample_rate = DEFAULT_SAMPLE_RATE
    wavs = []

    for octave in sorted(ss['octaves'].keys()):
        samples = ss['octaves'][octave]
        if not samples:
            continue
        if len(ss['octaves']) == 1:
            wav_name = f"{basename}.wav"
        else:
            wav_name = f"{basename}_oct{octave}.wav"
        wav_path = os.path.join(output_dir, wav_name)
        samples_to_wav(samples, wav_path, sample_rate)
        wavs.append(wav_path)
        duration = len(samples) / sample_rate
        print(f"  {wav_name}: {len(samples)} samples, {duration:.2f}s "
              f"(octave {octave}, rate={sample_rate}Hz, loop={ss['loop_type']})")

    return wavs


def find_ss_file(instr_dir, sample_name):
    """Find .ss file with case-insensitive matching (Amiga is case-insensitive)."""
    ss_name = sample_name + '.ss'
    ss_path = os.path.join(instr_dir, ss_name)
    if os.path.exists(ss_path):
        return ss_path
    # Case-insensitive fallback
    target = ss_name.lower()
    for entry in os.listdir(instr_dir):
        if entry.lower() == target:
            return os.path.join(instr_dir, entry)
    return None


def convert_instr_sampled(instr, output_dir):
    """Convert a SampledSound .instr file to WAV(s)."""
    instr_dir = os.path.dirname(os.path.abspath(instr['filepath']))
    ss_path = find_ss_file(instr_dir, instr['sample_name'])

    if ss_path is None:
        print(f"  WARNING: Referenced .ss file not found: {instr['sample_name']}.ss")
        return []

    ss = parse_ss(ss_path)
    basename = os.path.splitext(os.path.basename(instr['filepath']))[0]
    sample_rate = DEFAULT_SAMPLE_RATE
    wavs = []

    for octave in sorted(ss['octaves'].keys()):
        samples = list(ss['octaves'][octave])
        if not samples:
            continue

        vol = instr['volume']
        if vol < 255:
            samples = [int(s * vol / 255) for s in samples]

        if len(ss['octaves']) == 1:
            wav_name = f"{basename}.wav"
        else:
            wav_name = f"{basename}_oct{octave}.wav"
        wav_path = os.path.join(output_dir, wav_name)
        samples_to_wav(samples, wav_path, sample_rate)
        wavs.append(wav_path)
        duration = len(samples) / sample_rate
        vol_pct = vol * 100 // 255
        print(f"  {wav_name}: {len(samples)} samples, {duration:.2f}s "
              f"(octave {octave}, rate={sample_rate}Hz, vol={vol_pct}%, "
              f"loop={ss['loop_type']}, ss={os.path.basename(ss_path)})")

    return wavs


def convert_instr_synthesis(instr, output_dir):
    """Convert a Synthesis .instr file to WAV."""
    basename = os.path.splitext(os.path.basename(instr['filepath']))[0]
    waveform = instr['waveform1']
    sample_rate = DEFAULT_SAMPLE_RATE

    # Check if waveform is silent (all zeros)
    if all(s == 0 for s in waveform):
        print(f"  {basename}: silent waveform, skipping")
        return []

    cycles_needed = (sample_rate * 2) // len(waveform) + 1
    samples = waveform * cycles_needed

    wav_name = f"{basename}.wav"
    wav_path = os.path.join(output_dir, wav_name)
    samples_to_wav(samples, wav_path, sample_rate)

    duration = len(samples) / sample_rate
    freq = sample_rate / len(waveform)
    print(f"  {wav_name}: {len(samples)} samples, {duration:.2f}s "
          f"(synthesis, {cycles_needed} cycles, ~{freq:.1f} Hz fundamental)")

    return [wav_path]


def convert_file(input_file, output_dir):
    """Convert a Sonix instrument or sample file to WAV."""
    os.makedirs(output_dir, exist_ok=True)

    ext = os.path.splitext(input_file)[1].lower()
    basename = os.path.basename(input_file)
    print(f"Converting: {basename}")

    if ext == '.ss':
        return convert_ss(input_file, output_dir)
    elif ext == '.instr':
        instr = parse_instr(input_file)
        if instr is None:
            print(f"  Skipping: IFF/8SVX format (not native Sonix)")
            return []
        if instr['type'] == 'SampledSound':
            return convert_instr_sampled(instr, output_dir)
        elif instr['type'] == 'Synthesis':
            return convert_instr_synthesis(instr, output_dir)
        else:
            print(f"  Unknown instrument type: {instr['type']}")
            return []
    else:
        print(f"  Unknown file extension: {ext}")
        return []


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>")
        print()
        print("Converts Aegis Sonix .instr and .ss files to WAV format.")
        print()
        print("Examples:")
        print(f"  {sys.argv[0]} love-me.instr output/")
        print(f"  {sys.argv[0]} love-me.ss output/")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)

    wavs = convert_file(input_file, output_dir)

    if not wavs:
        print("No WAV files produced.")
        sys.exit(0)

    print(f"\nDone. Produced {len(wavs)} WAV file(s) in {output_dir}/")


if __name__ == '__main__':
    main()

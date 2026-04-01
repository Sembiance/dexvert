#!/usr/bin/env python3
# Vibe coded by Claude

"""
Music Studio Sound File Converter

Converts Activision's "The Music Studio" (1986/1988, Atari ST) files to WAV.

Handles three file types:
  - Waveform samples (.SND, magic 0x1A00): 8-bit unsigned PCM -> WAV
  - Instrument banks (.sound, magic 0xCE "Mstudio"): Synthesizes instrument previews -> WAV
  - Song settings (.snd, magic 0xCD "Mstudio"): Parses and reports contents (no audio)

Usage: musicStudioSound.py <inputFile> <outputDir>
"""

import sys
import os
import struct
import math


# =============================================================================
# WAV writing
# =============================================================================

def write_wav(filepath, sample_rate, samples_u8):
    """Write 8-bit unsigned mono PCM data as a WAV file."""
    num_samples = len(samples_u8)
    data_size = num_samples
    # WAV header: 44 bytes
    # RIFF header (12) + fmt chunk (24) + data chunk header (8) = 44
    file_size = 36 + data_size

    with open(filepath, "wb") as f:
        # RIFF header
        f.write(b"RIFF")
        f.write(struct.pack("<I", file_size))
        f.write(b"WAVE")
        # fmt sub-chunk
        f.write(b"fmt ")
        f.write(struct.pack("<I", 16))       # sub-chunk size
        f.write(struct.pack("<H", 1))        # audio format: PCM
        f.write(struct.pack("<H", 1))        # num channels: mono
        f.write(struct.pack("<I", sample_rate))
        f.write(struct.pack("<I", sample_rate))  # byte rate (8-bit mono)
        f.write(struct.pack("<H", 1))        # block align
        f.write(struct.pack("<H", 8))        # bits per sample
        # data sub-chunk
        f.write(b"data")
        f.write(struct.pack("<I", data_size))
        f.write(samples_u8)


# =============================================================================
# Instrument name parsing
# =============================================================================

def parse_instrument_name(data):
    """Parse a 10-byte null-terminated instrument name."""
    null_idx = data.find(b"\x00")
    if null_idx >= 0:
        return data[:null_idx].decode("ascii", errors="replace")
    return data.decode("ascii", errors="replace")


# =============================================================================
# Waveform sample file (.SND, magic 0x1A)
# =============================================================================

def parse_waveform(data):
    """Parse a waveform sample file (magic 0x1A 0x00)."""
    if len(data) < 44:
        raise ValueError(f"File too small for waveform header: {len(data)} bytes (need 44)")

    magic = struct.unpack_from("<H", data, 0x00)[0]
    version = struct.unpack_from("<H", data, 0x02)[0]
    name = parse_instrument_name(data[0x04:0x0E])
    sample_rate = struct.unpack_from("<H", data, 0x0E)[0]
    unknown1 = data[0x10]
    unknown2 = data[0x11]
    unknown3 = struct.unpack_from("<H", data, 0x12)[0]
    data_offset = struct.unpack_from("<I", data, 0x14)[0]
    reserved1 = struct.unpack_from("<I", data, 0x18)[0]
    reserved2 = struct.unpack_from("<I", data, 0x1C)[0]
    declared_len = struct.unpack_from("<I", data, 0x20)[0]
    reserved3 = struct.unpack_from("<I", data, 0x24)[0]
    reserved4 = struct.unpack_from("<I", data, 0x28)[0]

    actual_audio_len = len(data) - data_offset
    effective_len = min(declared_len, actual_audio_len)
    audio_data = data[data_offset:data_offset + effective_len]

    info = {
        "type": "waveform",
        "magic": magic,
        "version": version,
        "name": name,
        "sample_rate": sample_rate,
        "unknown_0x10": unknown1,
        "unknown_0x11": unknown2,
        "unknown_0x12": unknown3,
        "data_offset": data_offset,
        "reserved_0x18": reserved1,
        "reserved_0x1C": reserved2,
        "declared_length": declared_len,
        "reserved_0x24": reserved3,
        "reserved_0x28": reserved4,
        "actual_audio_length": actual_audio_len,
        "effective_length": effective_len,
        "truncated": declared_len > actual_audio_len,
        "audio_data": audio_data,
    }
    return info


def convert_waveform(data, output_dir, input_basename):
    """Convert a waveform sample file to WAV."""
    info = parse_waveform(data)

    print(f"  Type:        Waveform Sample")
    print(f"  Name:        {info['name']}")
    print(f"  Sample Rate: {info['sample_rate']} Hz")
    print(f"  Data Offset: {info['data_offset']} bytes")
    print(f"  Declared:    {info['declared_length']} bytes")
    print(f"  Actual:      {info['actual_audio_length']} bytes")
    if info["truncated"]:
        print(f"  WARNING:     File truncated (declared {info['declared_length']}, have {info['actual_audio_length']})")
    print(f"  Duration:    {info['effective_length'] / info['sample_rate']:.3f} seconds")
    print(f"  Header 0x10: 0x{info['unknown_0x10']:02X}")
    print(f"  Header 0x11: 0x{info['unknown_0x11']:02X}")
    print(f"  Header 0x12: 0x{info['unknown_0x12']:04X}")

    wav_name = os.path.splitext(input_basename)[0] + ".wav"
    wav_path = os.path.join(output_dir, wav_name)
    write_wav(wav_path, info["sample_rate"], info["audio_data"])
    print(f"  Output:      {wav_path}")
    return [wav_path]


# =============================================================================
# Song settings file (.snd, magic 0xCD)
# =============================================================================

def parse_song_settings(data):
    """Parse a song settings file (magic 0xCD 'Mstudio' 0xCD)."""
    if len(data) != 460:
        raise ValueError(f"Unexpected song settings file size: {len(data)} (expected 460)")

    info = {
        "type": "song_settings",
        "magic": data[0],
        "identifier": data[1:8].decode("ascii", errors="replace"),
        "magic2": data[8],
        "version": data[9],
        "atari_names": [],
        "atari_settings": [],
        "midi_names": [],
        "midi_octave_channel": [],
        "midi_presets": [],
    }

    # Parse 15 Atari instrument names (offset 0x0A, 10 bytes each)
    for i in range(15):
        offset = 0x0A + i * 10
        name = parse_instrument_name(data[offset:offset + 10])
        info["atari_names"].append(name)

    # Parse 15 instrument settings (offset 0xA0, 8 bytes each)
    for i in range(15):
        offset = 0xA0 + i * 8
        raw = data[offset:offset + 8]
        byte0 = raw[0]
        noise_off = (byte0 >> 7) & 1
        tone_off = (byte0 >> 4) & 1
        adsr = [b & 0x0F for b in raw]
        octave = (raw[1] >> 4) & 0x0F

        setting = {
            "raw": raw,
            "noise_enabled": not bool(noise_off),
            "tone_enabled": not bool(tone_off),
            "octave": octave,
            "adsr_attack_v": adsr[0],
            "adsr_attack_h": adsr[1],
            "adsr_decay_v": adsr[2],
            "adsr_decay_h": adsr[3],
            "adsr_sustain_v": adsr[4],
            "adsr_sustain_h": adsr[5],
            "adsr_release_v": adsr[6],
            "adsr_release_h": adsr[7],
        }
        info["atari_settings"].append(setting)

    # Parse 15 MIDI instrument names (offset 0x118, 10 bytes each)
    for i in range(15):
        offset = 0x118 + i * 10
        name = parse_instrument_name(data[offset:offset + 10])
        info["midi_names"].append(name)

    # Parse MIDI octave+channel (offset 0x1AE, 1 byte each)
    for i in range(15):
        b = data[0x1AE + i]
        info["midi_octave_channel"].append({
            "raw": b,
            "octave": (b >> 4) & 0x0F,
            "channel": b & 0x0F,
        })

    # Parse MIDI presets (offset 0x1BD, 1 byte each)
    for i in range(15):
        info["midi_presets"].append(data[0x1BD + i])

    return info


def convert_song_settings(data, output_dir, input_basename):
    """Process a song settings file (no audio to convert)."""
    info = parse_song_settings(data)

    print(f"  Type:        Song Settings")
    print(f"  Version:     {info['version']}")
    print()
    print(f"  {'#':>3s}  {'Atari Instrument':<15s}  {'Mode':<8s}  {'Oct':>3s}  {'ADSR':<25s}  {'MIDI Instrument':<15s}  {'MCh':>3s}  {'MOc':>3s}  {'MPr':>3s}")
    print(f"  {'---':>3s}  {'-'*15:<15s}  {'-'*8:<8s}  {'---':>3s}  {'-'*25:<25s}  {'-'*15:<15s}  {'---':>3s}  {'---':>3s}  {'---':>3s}")

    for i in range(15):
        s = info["atari_settings"][i]
        mode = "Tone" if s["tone_enabled"] and not s["noise_enabled"] else \
               "Noise" if s["noise_enabled"] and not s["tone_enabled"] else \
               "Both" if s["tone_enabled"] and s["noise_enabled"] else "Off"
        adsr_str = f"A({s['adsr_attack_v']:2d},{s['adsr_attack_h']:2d}) D({s['adsr_decay_v']:2d},{s['adsr_decay_h']:2d}) S({s['adsr_sustain_v']:2d},{s['adsr_sustain_h']:2d}) R({s['adsr_release_v']:2d},{s['adsr_release_h']:2d})"
        mc = info["midi_octave_channel"][i]
        print(f"  {i:3d}  {info['atari_names'][i]:<15s}  {mode:<8s}  {s['octave']:3d}  "
              f"{adsr_str}  {info['midi_names'][i]:<15s}  {mc['channel']:3d}  {mc['octave']:3d}  {info['midi_presets'][i]:3d}")

    print()
    print("  No audio data in song settings files (instrument config only).")
    return []


# =============================================================================
# Instrument bank file (.sound, magic 0xCE)
# =============================================================================

def parse_instrument_bank(data):
    """Parse an instrument bank file (magic 0xCE 'Mstudio' 0xCE)."""
    if len(data) != 1540:
        raise ValueError(f"Unexpected instrument bank file size: {len(data)} (expected 1540)")

    info = {
        "type": "instrument_bank",
        "magic": data[0],
        "identifier": data[1:8].decode("ascii", errors="replace"),
        "magic2": data[8],
        "version": data[9],
        "names": [],
        "instruments": [],
        "midi_names": [],
        "midi_octave_channel": [],
        "midi_presets": [],
    }

    # Parse 15 instrument names (offset 0x0A)
    for i in range(15):
        offset = 0x0A + i * 10
        name = parse_instrument_name(data[offset:offset + 10])
        info["names"].append(name)

    # Parse 15 instrument definitions (offset 0xA0, 80 bytes each)
    for i in range(15):
        offset = 0xA0 + i * 80

        # Harmonic amplitude envelope: 7 rows of 8 bytes
        envelope = []
        for row in range(7):
            row_offset = offset + row * 8
            amplitudes = list(data[row_offset:row_offset + 7])
            control = data[row_offset + 7]
            envelope.append({"amplitudes": amplitudes, "control": control})

        volume = envelope[0]["control"]  # Row 0 control byte = volume

        # Harmonic level parameters: 7 x 2-byte values (offset +56)
        harm_params = []
        for h in range(7):
            h_offset = offset + 56 + h * 2
            hi = data[h_offset]
            lo = data[h_offset + 1]
            flags = (hi >> 6) & 0x03
            value = ((hi & 0x3F) << 8) | lo
            harm_params.append({"raw_hi": hi, "raw_lo": lo, "flags": flags, "value": value})

        # Harmonic selection indices (offset +70, 7 bytes)
        harm_indices = list(data[offset + 70:offset + 77])

        # Additional parameters (offset +77, 3 bytes)
        waveform_mod = data[offset + 77]
        loop_param1 = data[offset + 78]
        loop_param2 = data[offset + 79]

        inst = {
            "envelope": envelope,
            "volume": volume,
            "harmonic_params": harm_params,
            "harmonic_indices": harm_indices,
            "waveform_modifier": waveform_mod,
            "loop_param1": loop_param1,
            "loop_param2": loop_param2,
        }
        info["instruments"].append(inst)

    # Parse 15 MIDI instrument names (offset 0x550)
    for i in range(15):
        offset = 0x550 + i * 10
        name = parse_instrument_name(data[offset:offset + 10])
        info["midi_names"].append(name)

    # Parse MIDI octave+channel (offset 0x5E6)
    for i in range(15):
        b = data[0x5E6 + i]
        info["midi_octave_channel"].append({
            "raw": b,
            "octave": (b >> 4) & 0x0F,
            "channel": b & 0x0F,
        })

    # Parse MIDI presets (offset 0x5F5)
    for i in range(15):
        info["midi_presets"].append(data[0x5F5 + i])

    return info


def synthesize_instrument(inst, sample_rate=11000, duration=1.0, base_freq=261.63):
    """
    Synthesize a WAV preview of an instrument definition using additive synthesis.

    Uses the harmonic selection indices, amplitude envelope, and volume to build
    a time-varying waveform by summing sine waves at the specified harmonic
    frequencies.
    """
    num_samples = int(sample_rate * duration)
    samples = [0.0] * num_samples

    envelope = inst["envelope"]
    volume = inst["volume"]
    harm_indices = inst["harmonic_indices"]

    if volume == 0:
        # Silent instrument
        return bytes([128] * num_samples)

    # Build time-varying waveform using additive synthesis
    # The envelope has 7 time steps; we interpolate across the duration
    num_steps = 7
    step_duration = num_samples / num_steps

    for h_slot in range(7):
        harm_num = harm_indices[h_slot]
        if harm_num == 0:
            continue  # Skip disabled harmonics

        freq = base_freq * harm_num

        for sample_idx in range(num_samples):
            t = sample_idx / sample_rate

            # Determine envelope position (interpolate between time steps)
            env_pos = sample_idx / step_duration
            step_lo = min(int(env_pos), num_steps - 1)
            step_hi = min(step_lo + 1, num_steps - 1)
            frac = env_pos - step_lo

            amp_lo = envelope[step_lo]["amplitudes"][h_slot]
            amp_hi = envelope[step_hi]["amplitudes"][h_slot]
            amplitude = amp_lo + (amp_hi - amp_lo) * frac

            # Normalize amplitude: envelope values are 0-63
            norm_amp = amplitude / 63.0

            # Generate sine wave for this harmonic
            samples[sample_idx] += norm_amp * math.sin(2.0 * math.pi * freq * t)

    # Normalize and convert to 8-bit unsigned
    if not samples:
        return bytes([128] * num_samples)

    max_val = max(abs(s) for s in samples)
    if max_val == 0:
        return bytes([128] * num_samples)

    # Scale by volume (0-127) and normalize
    vol_scale = volume / 127.0
    result = bytearray(num_samples)
    for i in range(num_samples):
        # Normalize to -1..1, apply volume, convert to 0..255
        normalized = (samples[i] / max_val) * vol_scale
        result[i] = max(0, min(255, int(128 + normalized * 127)))

    return bytes(result)


def convert_instrument_bank(data, output_dir, input_basename):
    """Convert an instrument bank file: synthesize each instrument as WAV."""
    info = parse_instrument_bank(data)

    print(f"  Type:        Instrument Bank")
    print(f"  Version:     {info['version']}")
    print()

    base_name = os.path.splitext(input_basename)[0]
    output_files = []

    for i in range(15):
        inst = info["instruments"][i]
        name = info["names"][i]
        vol = inst["volume"]
        indices = inst["harmonic_indices"]

        # Check if instrument has any harmonic content
        has_content = vol > 0 and any(
            any(row["amplitudes"][h] > 0 for row in inst["envelope"])
            for h in range(7)
            if indices[h] > 0
        )

        mc = info["midi_octave_channel"][i]
        print(f"  [{i:2d}] {name:<15s}  vol={vol:3d}  harmonics={indices}  "
              f"MIDI: {info['midi_names'][i]:<15s} ch={mc['channel']} oct={mc['octave']} preset={info['midi_presets'][i]}")

        if has_content:
            samples = synthesize_instrument(inst, sample_rate=11000, duration=1.0)
            safe_name = name.replace(" ", "_").replace(".", "_").replace("/", "_")
            if not safe_name:
                safe_name = f"inst{i}"
            wav_name = f"{base_name}_{i:02d}_{safe_name}.wav"
            wav_path = os.path.join(output_dir, wav_name)
            write_wav(wav_path, 11000, samples)
            output_files.append(wav_path)

    print()
    if output_files:
        print(f"  Synthesized {len(output_files)} instrument preview(s):")
        for f in output_files:
            print(f"    {f}")
    else:
        print("  No instruments with audio content to synthesize.")

    return output_files


# =============================================================================
# File type detection and main entry point
# =============================================================================

def detect_file_type(data):
    """Detect the Music Studio file type from magic bytes."""
    if len(data) < 10:
        return "unknown"

    # Check for Mstudio magic (0xCD or 0xCE + "Mstudio" + same byte)
    if data[1:8] == b"Mstudio":
        if data[0] == 0xCD and data[8] == 0xCD:
            return "song_settings"
        if data[0] == 0xCE and data[8] == 0xCE:
            return "instrument_bank"

    # Check for waveform sample magic
    if data[0] == 0x1A and data[1] == 0x00 and data[2] == 0x01 and data[3] == 0x00:
        return "waveform"

    return "unknown"


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>")
        print()
        print("Converts Activision's 'The Music Studio' files to WAV format.")
        print()
        print("Supported file types:")
        print("  .SND (waveform)  - 8-bit PCM samples -> WAV")
        print("  .sound           - Instrument banks -> synthesized WAV previews")
        print("  .snd (song)      - Song settings -> info display (no audio)")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(input_file):
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    with open(input_file, "rb") as f:
        data = f.read()

    input_basename = os.path.basename(input_file)
    file_type = detect_file_type(data)

    print(f"File:          {input_file}")
    print(f"Size:          {len(data)} bytes")
    print()

    if file_type == "waveform":
        convert_waveform(data, output_dir, input_basename)
    elif file_type == "song_settings":
        convert_song_settings(data, output_dir, input_basename)
    elif file_type == "instrument_bank":
        convert_instrument_bank(data, output_dir, input_basename)
    else:
        print(f"Error: Unrecognized file format (first bytes: {data[:10].hex()})")
        sys.exit(1)


if __name__ == "__main__":
    main()

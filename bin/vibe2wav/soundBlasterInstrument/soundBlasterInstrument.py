#!/usr/bin/env python3
# Vibe coded by Claude
"""
Sound Blaster Instrument (SBI) File Converter
Reads SBI-family files and converts OPL FM instrument patches to WAV audio.

Usage: python3 soundBlasterInstrument.py <inputFile> <outputDir>
"""

import sys
import os
import struct
import math
import wave
import json

# ==============================================================================
# Constants
# ==============================================================================

SAMPLE_RATE = 44100
NOTE_ON_DURATION = 1.0    # seconds of sustained note
RELEASE_DURATION = 0.5    # seconds of release after key-off
BASE_NOTE = 60            # MIDI note 60 = Middle C (C4)
BASE_FREQ = 261.63        # Hz for middle C

# OPL2 frequency multiplier table (indexed by MULTI field, 4 bits)
MULTI_TABLE = [0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 12, 12, 15, 15]

# OPL2 attack time table in seconds (indexed by rate 0-15)
# Rate 0 = no attack, rate 15 = instant
# Based on OPL2 chip timing at typical clock rate
ATTACK_TIMES = [
    float('inf'),  # 0: never attacks
    10.92, 5.46, 3.64, 2.73, 2.19, 1.82, 1.56,
    1.37, 1.09, 0.91, 0.78, 0.68, 0.55, 0.46,
    0.0,           # 15: instant
]

# OPL2 decay/release time table in seconds (time for full 48dB attenuation)
# Rate 0 = infinite sustain, rate 15 = fastest decay
DECAY_TIMES = [
    float('inf'),  # 0: no decay
    39.28, 19.64, 13.09, 9.82, 7.86, 6.55, 5.61,
    4.91, 3.93, 3.27, 2.80, 2.46, 1.96, 1.64,
    0.82,          # 15: fastest
]


# ==============================================================================
# OPL Waveform generators
# ==============================================================================

def opl_waveform(phase, waveform_type):
    """Generate OPL2/OPL3 waveform sample for a given phase (0 to 2*pi range).

    Args:
        phase: Current oscillator phase (radians, any value - will be wrapped)
        waveform_type: 0-7 waveform selector

    Returns:
        Sample value in range [-1.0, 1.0]
    """
    # Normalize phase to [0, 2*pi)
    p = phase % (2.0 * math.pi)

    if waveform_type == 0:
        # Sine
        return math.sin(p)
    elif waveform_type == 1:
        # Half-sine (positive half only)
        return math.sin(p) if p < math.pi else 0.0
    elif waveform_type == 2:
        # Absolute sine (full-wave rectified)
        return abs(math.sin(p))
    elif waveform_type == 3:
        # Quarter sine (first and third quarter periods only)
        q = p % math.pi
        return math.sin(q) if q < (math.pi / 2.0) else 0.0
    elif waveform_type == 4:
        # Alternating sine - double frequency, positive half only (OPL3)
        if p < math.pi:
            return math.sin(2.0 * p)
        return 0.0
    elif waveform_type == 5:
        # Camel sine - |sin| at double frequency, positive half only (OPL3)
        if p < math.pi:
            return abs(math.sin(2.0 * p))
        return 0.0
    elif waveform_type == 6:
        # Square wave (OPL3)
        return 1.0 if p < math.pi else -1.0
    elif waveform_type == 7:
        # Derived logarithmic sawtooth (OPL3)
        # Approximation: rising sawtooth-like waveform
        if p < math.pi:
            return (p / math.pi) * 2.0 - 1.0
        else:
            return (1.0 - ((p - math.pi) / math.pi)) * 2.0 - 1.0
    return 0.0


# ==============================================================================
# ADSR Envelope Generator
# ==============================================================================

class EnvelopeGenerator:
    """OPL2-style ADSR envelope generator."""

    def __init__(self, attack_rate, decay_rate, sustain_level, release_rate, egt):
        """
        Args:
            attack_rate: 0-15 (AR field)
            decay_rate: 0-15 (DR field)
            sustain_level: 0-15 (SL field, 0=max, 15=silence)
            release_rate: 0-15 (RR field)
            egt: Envelope Generator Type (1=sustained, 0=percussive)
        """
        self.ar = attack_rate
        self.dr = decay_rate
        self.sl = sustain_level
        self.rr = release_rate
        self.egt = egt

        # Compute sustain attenuation (0.0 = max volume, 1.0 = silence)
        # Each SL step = 3 dB attenuation
        if sustain_level == 0:
            self.sustain_atten = 0.0
        elif sustain_level >= 15:
            self.sustain_atten = 1.0
        else:
            self.sustain_atten = 1.0 - 10.0 ** (-sustain_level * 3.0 / 20.0)

        self.sustain_level_linear = 1.0 - self.sustain_atten

    def get_level(self, t, key_on_duration):
        """Get envelope level at time t.

        Args:
            t: Time in seconds from note start
            key_on_duration: Duration the key is held (seconds)

        Returns:
            Envelope level 0.0 to 1.0
        """
        if t < 0:
            return 0.0

        # Attack phase
        if self.ar == 0:
            return 0.0  # Never attacks
        if self.ar >= 15:
            attack_time = 0.0
        else:
            attack_time = ATTACK_TIMES[self.ar] * 0.05  # Scale for playability

        if t < attack_time and attack_time > 0:
            # Exponential attack (concave curve like real OPL)
            progress = t / attack_time
            level = 1.0 - (1.0 - progress) ** 3
            return level

        # After attack: t_after_attack is time since attack completed
        t_after_attack = t - attack_time

        # Decay phase - exponential decay from 1.0 to sustain level
        if self.dr == 0:
            decay_time = float('inf')
        else:
            decay_time = DECAY_TIMES[self.dr] * 0.08

        if t < key_on_duration:
            # Key is still held
            if decay_time == float('inf'):
                return 1.0
            decay_progress = t_after_attack / decay_time
            if decay_progress >= 1.0:
                if self.egt:
                    return self.sustain_level_linear  # Sustained
                else:
                    return 0.0  # Percussive - decay to silence
            # Exponential decay
            level = 1.0 - (1.0 - self.sustain_level_linear) * (1.0 - math.exp(-3.0 * decay_progress))
            return max(level, self.sustain_level_linear if self.egt else 0.0)

        # Release phase
        if self.rr == 0:
            release_time = float('inf')
        else:
            release_time = DECAY_TIMES[self.rr] * 0.08

        t_release = t - key_on_duration

        # Get level at the moment of key-off
        if decay_time == float('inf'):
            level_at_release = 1.0
        else:
            t_aa = key_on_duration - attack_time
            dp = t_aa / decay_time if decay_time > 0 else 1.0
            if dp >= 1.0:
                level_at_release = self.sustain_level_linear if self.egt else 0.0
            else:
                level_at_release = 1.0 - (1.0 - self.sustain_level_linear) * (1.0 - math.exp(-3.0 * dp))
                level_at_release = max(level_at_release, self.sustain_level_linear if self.egt else 0.0)

        if release_time == float('inf'):
            return level_at_release

        release_progress = t_release / release_time
        if release_progress >= 1.0:
            return 0.0

        level = level_at_release * math.exp(-4.0 * release_progress)
        return level


# ==============================================================================
# OPL FM Synthesizer
# ==============================================================================

def synthesize_instrument(opl_regs, sample_rate=SAMPLE_RATE,
                          note_on=NOTE_ON_DURATION, release=RELEASE_DURATION):
    """Synthesize audio for one OPL2 instrument patch.

    Args:
        opl_regs: 16-byte OPL register data
        sample_rate: Output sample rate
        note_on: Key-on duration in seconds
        release: Release duration in seconds

    Returns:
        List of float samples normalized to [-1.0, 1.0]
    """
    # Parse OPL registers
    mod_char = opl_regs[0]
    car_char = opl_regs[1]
    mod_ksl_tl = opl_regs[2]
    car_ksl_tl = opl_regs[3]
    mod_ad = opl_regs[4]
    car_ad = opl_regs[5]
    mod_sr = opl_regs[6]
    car_sr = opl_regs[7]
    mod_ws = opl_regs[8] & 0x07
    car_ws = opl_regs[9] & 0x07
    fb_cnt = opl_regs[10]

    # Decode modulator characteristics
    mod_am = (mod_char >> 7) & 1
    mod_vib = (mod_char >> 6) & 1
    mod_egt = (mod_char >> 5) & 1
    mod_ksr = (mod_char >> 4) & 1
    mod_multi = mod_char & 0x0F

    # Decode carrier characteristics
    car_am = (car_char >> 7) & 1
    car_vib = (car_char >> 6) & 1
    car_egt = (car_char >> 5) & 1
    car_ksr = (car_char >> 4) & 1
    car_multi = car_char & 0x0F

    # Decode levels
    mod_ksl = (mod_ksl_tl >> 6) & 0x03
    mod_tl = mod_ksl_tl & 0x3F
    car_ksl = (car_ksl_tl >> 6) & 0x03
    car_tl = car_ksl_tl & 0x3F

    # Decode ADSR
    mod_ar = (mod_ad >> 4) & 0x0F
    mod_dr = mod_ad & 0x0F
    car_ar = (car_ad >> 4) & 0x0F
    car_dr = car_ad & 0x0F
    mod_sl = (mod_sr >> 4) & 0x0F
    mod_rr = mod_sr & 0x0F
    car_sl = (car_sr >> 4) & 0x0F
    car_rr = car_sr & 0x0F

    # Decode feedback/connection
    fb = (fb_cnt >> 1) & 0x07
    cnt = fb_cnt & 0x01

    # Calculate frequencies
    mod_freq = BASE_FREQ * MULTI_TABLE[mod_multi]
    car_freq = BASE_FREQ * MULTI_TABLE[car_multi]

    # Calculate volume levels (TL: 0=max, 63=silent, each step = 0.75 dB)
    mod_vol = 10.0 ** (-mod_tl * 0.75 / 20.0) if mod_tl < 63 else 0.0
    car_vol = 10.0 ** (-car_tl * 0.75 / 20.0) if car_tl < 63 else 0.0

    # Feedback scaling factor
    # OPL2 feedback: phase_offset = (out[n-1] + out[n-2]) * 2^(FB-7) * 2*pi
    # where out includes envelope and TL attenuation (normalized to [-1, 1])
    if fb == 0:
        fb_factor = 0.0
    else:
        fb_factor = 2.0 * math.pi * (2.0 ** (fb - 7))

    # Create envelope generators
    mod_env = EnvelopeGenerator(mod_ar, mod_dr, mod_sl, mod_rr, mod_egt)
    car_env = EnvelopeGenerator(car_ar, car_dr, car_sl, car_rr, car_egt)

    # Phase increments per sample
    mod_phase_inc = 2.0 * math.pi * mod_freq / sample_rate
    car_phase_inc = 2.0 * math.pi * car_freq / sample_rate

    # Synthesis
    total_duration = note_on + release
    num_samples = int(total_duration * sample_rate)
    samples = []

    mod_phase = 0.0
    car_phase = 0.0
    prev_mod_out = 0.0
    prev_prev_mod_out = 0.0

    # Vibrato and tremolo parameters
    vib_freq = 6.4  # Hz (OPL2 vibrato rate)
    vib_depth = 0.007  # ~14 cents vibrato depth
    trem_freq = 3.7  # Hz (OPL2 tremolo rate)
    trem_depth = 0.1  # ~1 dB tremolo depth

    for i in range(num_samples):
        t = i / sample_rate

        # Calculate envelopes
        mod_level = mod_env.get_level(t, note_on)
        car_level = car_env.get_level(t, note_on)

        # Apply tremolo if enabled
        if mod_am:
            trem_mod = 1.0 - trem_depth * (1.0 + math.sin(2.0 * math.pi * trem_freq * t)) / 2.0
            mod_level *= trem_mod
        if car_am:
            trem_car = 1.0 - trem_depth * (1.0 + math.sin(2.0 * math.pi * trem_freq * t)) / 2.0
            car_level *= trem_car

        # Vibrato frequency modulation
        vib_mod_factor = 1.0
        vib_car_factor = 1.0
        if mod_vib:
            vib_mod_factor = 1.0 + vib_depth * math.sin(2.0 * math.pi * vib_freq * t)
        if car_vib:
            vib_car_factor = 1.0 + vib_depth * math.sin(2.0 * math.pi * vib_freq * t)

        # Modulator with feedback
        # OPL2: feedback uses fully-attenuated output (envelope + TL applied)
        if fb_factor > 0:
            feedback = (prev_mod_out + prev_prev_mod_out) * fb_factor
        else:
            feedback = 0.0

        mod_phase += mod_phase_inc * vib_mod_factor
        mod_out_raw = opl_waveform(mod_phase + feedback, mod_ws)
        mod_out = mod_out_raw * mod_level * mod_vol

        prev_prev_mod_out = prev_mod_out
        prev_mod_out = mod_out_raw * mod_level * mod_vol

        # Carrier
        car_phase += car_phase_inc * vib_car_factor

        if cnt == 0:
            # FM mode: modulator output phase-shifts the carrier
            # OPL2: modulator output into 10-bit phase, ~2 cycle max deviation
            fm_depth = mod_out * 4.0 * math.pi
            car_out = opl_waveform(car_phase + fm_depth, car_ws)
        else:
            # Additive mode: both operators output independently
            car_out = opl_waveform(car_phase, car_ws)

        # Final output
        if cnt == 0:
            output = car_out * car_level * car_vol
        else:
            output = (car_out * car_level * car_vol + mod_out) * 0.5

        samples.append(output)

    return samples


def normalize_and_convert(samples, target_peak=0.85):
    """Normalize samples and convert to 16-bit PCM.

    Args:
        samples: List of float samples
        target_peak: Target peak amplitude (0.0 to 1.0)

    Returns:
        bytes: 16-bit PCM audio data
    """
    if not samples:
        return b''

    peak = max(abs(s) for s in samples)
    if peak < 1e-10:
        # Silent instrument - generate a very quiet click so the WAV isn't empty
        return struct.pack('<' + 'h' * len(samples), *([0] * len(samples)))

    scale = target_peak / peak
    pcm_data = bytearray()
    for s in samples:
        val = int(s * scale * 32767)
        val = max(-32768, min(32767, val))
        pcm_data.extend(struct.pack('<h', val))

    return bytes(pcm_data)


def write_wav(filename, pcm_data, sample_rate=SAMPLE_RATE, channels=1, sample_width=2):
    """Write PCM data to a WAV file."""
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_data)


# ==============================================================================
# File Format Parsers
# ==============================================================================

def parse_sbi_instrument_bank(data, fallback_name=None):
    """Parse an SBI/2OP instrument bank file.

    Args:
        data: Raw file bytes
        fallback_name: Name to use for instruments with blank name fields

    Returns:
        List of (name, opl_registers, magic) tuples
    """
    record_size = 52
    num_records = len(data) // record_size

    instruments = []
    for i in range(num_records):
        offset = i * record_size
        magic = data[offset:offset + 4]

        # Skip empty/zero-filled slots (common in 256-entry banks)
        if magic == b'\x00\x00\x00\x00':
            continue

        # Verify magic
        if magic not in (b'SBI\x1a', b'2OP\x1a', b'4OP\x1a'):
            print(f"  Warning: record {i} has unexpected magic {magic.hex()}, skipping")
            continue

        # Extract name (32 bytes, null-terminated)
        name_raw = data[offset + 4:offset + 36]
        name = name_raw.split(b'\x00')[0].decode('ascii', errors='replace').strip()
        if not name:
            name = fallback_name if fallback_name else f"Instrument_{i:03d}"

        # Extract OPL register data (16 bytes)
        opl_regs = data[offset + 36:offset + 52]

        instruments.append((name, opl_regs, magic))

    return instruments


def is_sbi_instrument_file(data):
    """Check if data is a valid SBI instrument file.

    Accepts:
      - Multi-instrument banks: file size is exact multiple of 52, first
        record has SBI\\x1a or 2OP\\x1a magic
      - Single-instrument files: file size is 53 bytes (52-byte record + 1
        trailing byte), with SBI\\x1a or 2OP\\x1a magic

    Returns:
        True if the file is a valid SBI instrument file
    """
    if len(data) < 52:
        return False
    magic = data[0:4]
    if magic not in (b'SBI\x1a', b'2OP\x1a'):
        return False
    # Accept exact multiples of 52, or 53 (single instrument + trailing byte)
    return len(data) % 52 == 0 or len(data) == 53


# ==============================================================================
# Main Converter
# ==============================================================================

def convert_file(input_path, output_dir):
    """Convert an SBI instrument bank file to WAV files.

    Args:
        input_path: Path to input file
        output_dir: Directory to write WAV files

    Returns:
        dict with conversion results for the HTML report
    """
    os.makedirs(output_dir, exist_ok=True)

    with open(input_path, 'rb') as f:
        data = f.read()

    basename = os.path.splitext(os.path.basename(input_path))[0]
    file_size = len(data)

    result = {
        'input_file': input_path,
        'file_size': file_size,
        'wav_files': [],
        'info': {},
    }

    print(f"\nProcessing: {input_path}")
    print(f"  File size: {file_size} bytes")

    if not is_sbi_instrument_file(data):
        print("  Skipping: not a valid SBI instrument file")
        print("  (requires SBI\\x1a or 2OP\\x1a magic and file size multiple of 52, or 53 for single instrument)")
        return result

    # Use filename as fallback name for single-instrument files with blank names
    fallback_name = os.path.splitext(os.path.basename(input_path))[0]
    instruments = parse_sbi_instrument_bank(data, fallback_name=fallback_name)
    print(f"  Instruments found: {len(instruments)}")
    result['info']['num_instruments'] = len(instruments)
    result['info']['instruments'] = []

    for idx, (name, opl_regs, magic) in enumerate(instruments):
        magic_str = magic.decode('ascii', errors='replace').rstrip('\x1a')
        safe_name = "".join(c if c.isalnum() or c in '-_ ' else '_' for c in name)
        safe_name = safe_name.strip().replace(' ', '_')
        if not safe_name:
            safe_name = f"inst_{idx:03d}"

        wav_filename = f"{idx:03d}_{safe_name}.wav"
        wav_path = os.path.join(output_dir, wav_filename)

        print(f"  [{idx:3d}] {magic_str}: {name}")

        # Synthesize audio
        samples = synthesize_instrument(opl_regs)
        pcm_data = normalize_and_convert(samples)
        write_wav(wav_path, pcm_data)

        result['wav_files'].append(wav_filename)
        result['info']['instruments'].append({
            'index': idx,
            'name': name,
            'magic': magic.hex(),
            'opl_hex': opl_regs.hex(),
        })

    print(f"  Generated {len(result['wav_files'])} WAV files")
    return result


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>")
        print()
        print("Converts Sound Blaster Instrument (SBI) bank files to WAV audio")
        print("using OPL2/OPL3 FM synthesis emulation.")
        print()
        print("Accepts files with SBI\\x1a or 2OP\\x1a record magic and")
        print("file size that is an exact multiple of 52 bytes.")
        sys.exit(1)

    input_path = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(input_path):
        print(f"Error: input file not found: {input_path}")
        sys.exit(1)

    result = convert_file(input_path, output_dir)

    # Write result metadata as JSON for the HTML report generator
    meta_path = os.path.join(output_dir, f"{os.path.basename(input_path)}.meta.json")
    result_copy = dict(result)
    result_copy['input_file'] = os.path.basename(input_path)
    with open(meta_path, 'w') as f:
        json.dump(result_copy, f, indent=2, default=str)

    return result


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# Vibe coded by Claude
"""
medSynthSound.py - MED Synth Sound (MSH) to WAV converter

Converts OctaMED synthetic instrument files (.SYN / MSH format) into
WAV audio files by simulating the volume and waveform sequence engine.

Usage: medSynthSound.py <inputFile> <outputDir>
"""

import struct
import sys
import os
import math
import wave

# --- Constants ---

AMIGA_PAL_CLOCK = 3546895      # PAL clock frequency in Hz
DEFAULT_PERIOD = 428            # Amiga period for C-3
TICK_RATE = 50                  # PAL vertical blank rate (ticks/sec)
OUTPUT_RATE = 22050             # Output WAV sample rate
SAMPLES_PER_TICK = OUTPUT_RATE // TICK_RATE  # 441 samples per tick
MAX_TICKS = 500                 # Maximum render duration (10 seconds)
HLT_SUSTAIN_TICKS = 100        # Ticks to sustain on HLT before key-off
FADE_SAMPLES = 200             # Fade-out length at end to avoid clicks

# Sequence command opcodes (0xF0-0xFF)
CMD_SPD = 0xF0   # Set speed (param: new speed)
CMD_WAI = 0xF1   # Wait (param: tick count)
CMD_CHD = 0xF2   # Change down (param: rate) - vol slide down / period up
CMD_CHU = 0xF3   # Change up (param: rate) - vol slide up / period down
CMD_EN1_VBD = 0xF4  # Vol: envelope one-shot / Wf: vibrato depth
CMD_EN2_VBS = 0xF5  # Vol: envelope looping / Wf: vibrato speed
CMD_EST_RES = 0xF6  # Vol: unknown / Wf: reset pitch (no param)
CMD_VWF = 0xF7   # Wf only: vibrato waveform (param: wf index)
CMD_JWS_JVS = 0xFA  # Vol: jump wf seq / Wf: jump vol seq (param: pos)
CMD_HLT = 0xFB   # Halt (no param) - wait for key-off
CMD_ARP = 0xFC   # Wf only: begin arpeggio (variable inline data)
CMD_ARE = 0xFD   # Wf only: end arpeggio (no param)
CMD_JMP = 0xFE   # Jump (param: target position)
CMD_END = 0xFF   # End sequence (no param)

# Commands that take a parameter byte (next byte consumed)
VOL_PARAM_CMDS = {CMD_SPD, CMD_WAI, CMD_CHD, CMD_CHU, CMD_EN1_VBD,
                  CMD_EN2_VBS, CMD_JWS_JVS, CMD_JMP}
WF_PARAM_CMDS = {CMD_SPD, CMD_WAI, CMD_CHD, CMD_CHU, CMD_EN1_VBD,
                 CMD_EN2_VBS, CMD_VWF, CMD_JWS_JVS, CMD_JMP}

# Commands with no parameter byte
NO_PARAM_CMDS = {CMD_EST_RES, CMD_HLT, CMD_ARE, CMD_END}


# --- File Parser ---

class MSHFile:
    """Parses a MED Synth Sound (MSH) file."""

    def __init__(self, filepath):
        with open(filepath, 'rb') as f:
            self.data = f.read()
        self.filepath = filepath
        self._parse()

    def _parse(self):
        d = self.data
        if len(d) < 22:
            raise ValueError(f"File too small ({len(d)} bytes, need >= 22)")
        if d[0:4] != b'MSH\x00':
            raise ValueError(f"Bad magic: {d[0:4]!r} (expected b'MSH\\x00')")

        # Header fields (22 bytes)
        self.magic = d[0:4]                                    # 0x00: "MSH\0"
        self.type = struct.unpack('>h', d[4:6])[0]            # 0x04: -1=synth
        self.default_decay = d[6]                              # 0x06
        self.reserved = d[7:10]                                # 0x07
        self.rep = struct.unpack('>H', d[10:12])[0]           # 0x0A
        self.replen = struct.unpack('>H', d[12:14])[0]        # 0x0C
        self.vol_tbl_len = struct.unpack('>H', d[14:16])[0]   # 0x0E
        self.wf_tbl_len = struct.unpack('>H', d[16:18])[0]    # 0x10
        self.vol_speed = d[18]                                 # 0x12
        self.wf_speed = d[19]                                  # 0x13
        self.num_wf = struct.unpack('>H', d[20:22])[0]        # 0x14

        # Variable-length sections
        pos = 22
        self.vol_tbl = list(d[pos:pos + self.vol_tbl_len])
        pos += self.vol_tbl_len

        self.wf_tbl = list(d[pos:pos + self.wf_tbl_len])
        pos += self.wf_tbl_len

        # Waveform offset table (NumWF x 4-byte big-endian offsets)
        self.wf_offsets = []
        for _ in range(self.num_wf):
            off = struct.unpack('>I', d[pos:pos + 4])[0]
            self.wf_offsets.append(off)
            pos += 4

        # Parse waveform data blocks
        self.waveforms = []
        self.wf_sizes_words = []
        for off in self.wf_offsets:
            sz_words = struct.unpack('>H', d[off:off + 2])[0]
            sz_bytes = sz_words * 2
            raw = d[off + 2:off + 2 + sz_bytes]
            # Convert unsigned bytes to signed 8-bit values
            signed = []
            for b in raw:
                signed.append(b - 256 if b >= 128 else b)
            self.waveforms.append(signed)
            self.wf_sizes_words.append(sz_words)

    def validate(self):
        """Verify every byte of the file is accounted for."""
        d = self.data
        expected_pos = 22 + self.vol_tbl_len + self.wf_tbl_len + self.num_wf * 4
        for i, off in enumerate(self.wf_offsets):
            if off != expected_pos:
                return False, f"Waveform {i} offset mismatch: expected {expected_pos}, got {off}"
            sz = self.wf_sizes_words[i]
            expected_pos = off + 2 + sz * 2
        if expected_pos != len(d):
            return False, f"File size mismatch: expected {expected_pos}, got {len(d)}"
        return True, "OK"

    def info(self):
        """Return a summary string."""
        lines = [
            f"File: {self.filepath} ({len(self.data)} bytes)",
            f"Type: {'synth' if self.type == -1 else 'hybrid' if self.type == -2 else f'unknown({self.type})'}",
            f"Vol sequence: {self.vol_tbl_len} bytes, speed={self.vol_speed}",
            f"Wf sequence: {self.wf_tbl_len} bytes, speed={self.wf_speed}",
            f"Waveforms: {self.num_wf} (sizes: {[s*2 for s in self.wf_sizes_words]} samples)",
        ]
        return "\n".join(lines)


# --- Synth Engine ---

class SynthEngine:
    """Simulates the OctaMED synth sound playback engine."""

    def __init__(self, msh):
        self.msh = msh

    def _reset(self):
        m = self.msh

        # Volume sequence state
        self.vol = 0                  # Current volume level
        self.vol_slide = 0            # Volume slide per tick
        self.vol_pos = 0              # Position in vol table
        self.vol_spd = max(1, m.vol_speed)
        self.vol_ctr = self.vol_spd   # Countdown to next step
        self.vol_wait = 0             # WAI counter
        self.vol_halt = False
        self.vol_end = False

        # Volume envelope state (EN1/EN2)
        self.vol_env_wf = -1          # Envelope waveform index (-1 = none)
        self.vol_env_pos = 0          # Position in envelope waveform
        self.vol_env_loop = False     # EN2 loops, EN1 does not

        # Waveform sequence state
        self.cur_wf = 0               # Current waveform index
        self.wf_slide = 0             # Period slide per tick
        self.wf_pos = 0               # Position in wf table
        self.wf_spd = max(1, m.wf_speed)
        self.wf_ctr = self.wf_spd
        self.wf_wait = 0
        self.wf_halt = False
        self.wf_end = False

        # Vibrato state
        self.vib_depth = 0
        self.vib_speed = 0
        self.vib_phase = 0

        # Arpeggio state
        self.arp = []
        self.arp_idx = 0

        # Period (pitch) state
        self.period = DEFAULT_PERIOD
        self.base_period = DEFAULT_PERIOD
        self.eff_period = DEFAULT_PERIOD

        # Waveform sample position (fractional)
        self.sample_pos = 0.0

        # Cross-sequence jump requests (deferred)
        self.jws_pending = -1         # Jump wf seq (from vol seq)
        self.jvs_pending = -1         # Jump vol seq (from wf seq)

        # HLT sustain timer
        self.halt_timer = 0

    def _step_vol(self):
        """Process one step of the volume sequence."""
        m = self.msh
        if self.vol_halt or self.vol_end or not m.vol_tbl:
            return

        # Guard against runaway loops within a single step
        for _ in range(len(m.vol_tbl) + 10):
            if self.vol_pos >= len(m.vol_tbl):
                self.vol_end = True
                return

            b = m.vol_tbl[self.vol_pos]

            # Direct volume value (0x00-0xEF)
            if b < 0xF0:
                self.vol = b
                self.vol_slide = 0
                self.vol_pos += 1
                return

            # END
            if b == CMD_END:
                self.vol_end = True
                return

            # HLT
            if b == CMD_HLT:
                self.vol_halt = True
                self.halt_timer = 0
                return

            # All remaining commands need bounds check for param
            if b in VOL_PARAM_CMDS:
                if self.vol_pos + 1 >= len(m.vol_tbl):
                    self.vol_end = True
                    return
                param = m.vol_tbl[self.vol_pos + 1]

            if b == CMD_JMP:
                target = param
                if target < len(m.vol_tbl):
                    self.vol_pos = target
                    continue
                self.vol_end = True
                return

            elif b == CMD_SPD:
                self.vol_spd = max(1, param)
                self.vol_pos += 2
                continue

            elif b == CMD_WAI:
                self.vol_wait = param
                self.vol_pos += 2
                return

            elif b == CMD_CHD:
                self.vol_slide = -param
                self.vol_pos += 2
                continue

            elif b == CMD_CHU:
                self.vol_slide = param
                self.vol_pos += 2
                continue

            elif b == CMD_EN1_VBD:
                self.vol_env_wf = param
                self.vol_env_pos = 0
                self.vol_env_loop = False
                self.vol_pos += 2
                continue

            elif b == CMD_EN2_VBS:
                self.vol_env_wf = param
                self.vol_env_pos = 0
                self.vol_env_loop = True
                self.vol_pos += 2
                continue

            elif b == CMD_EST_RES:
                # Unknown in vol context, no param, skip
                self.vol_pos += 1
                continue

            elif b == CMD_JWS_JVS:
                self.jws_pending = param
                self.vol_pos += 2
                continue

            else:
                # Unknown command, skip byte
                self.vol_pos += 1
                continue

        # Exhausted iteration guard
        self.vol_end = True

    def _step_wf(self):
        """Process one step of the waveform sequence."""
        m = self.msh
        if self.wf_halt or self.wf_end or not m.wf_tbl:
            return

        for _ in range(len(m.wf_tbl) + 10):
            if self.wf_pos >= len(m.wf_tbl):
                self.wf_end = True
                return

            b = m.wf_tbl[self.wf_pos]

            # Direct waveform index (0x00-0xEF)
            if b < 0xF0:
                if b < len(m.waveforms):
                    self.cur_wf = b
                self.wf_pos += 1
                return

            # END
            if b == CMD_END:
                self.wf_end = True
                return

            # HLT
            if b == CMD_HLT:
                self.wf_halt = True
                self.halt_timer = 0
                return

            # ARP (special: variable-length inline data)
            if b == CMD_ARP:
                self.arp = []
                self.arp_idx = 0
                self.wf_pos += 1
                while self.wf_pos < len(m.wf_tbl):
                    ab = m.wf_tbl[self.wf_pos]
                    if ab == CMD_ARE:
                        self.wf_pos += 1
                        break
                    if ab == CMD_END:
                        break
                    self.arp.append(ab)
                    self.wf_pos += 1
                continue

            # ARE (should only appear after ARP, skip if encountered alone)
            if b == CMD_ARE:
                self.wf_pos += 1
                continue

            # Param commands bounds check
            if b in WF_PARAM_CMDS:
                if self.wf_pos + 1 >= len(m.wf_tbl):
                    self.wf_end = True
                    return
                param = m.wf_tbl[self.wf_pos + 1]

            if b == CMD_JMP:
                target = param
                if target < len(m.wf_tbl):
                    # If jump target is END, halt instead
                    if m.wf_tbl[target] == CMD_END:
                        self.wf_end = True
                        return
                    self.wf_pos = target
                    continue
                self.wf_end = True
                return

            elif b == CMD_SPD:
                self.wf_spd = max(1, param)
                self.wf_pos += 2
                continue

            elif b == CMD_WAI:
                self.wf_wait = param
                self.wf_pos += 2
                return

            elif b == CMD_CHD:
                self.wf_slide = param    # Period up = pitch down
                self.wf_pos += 2
                continue

            elif b == CMD_CHU:
                self.wf_slide = -param   # Period down = pitch up
                self.wf_pos += 2
                continue

            elif b == CMD_EN1_VBD:
                self.vib_depth = param
                self.wf_pos += 2
                continue

            elif b == CMD_EN2_VBS:
                self.vib_speed = param
                self.wf_pos += 2
                continue

            elif b == CMD_EST_RES:
                # RES: reset pitch to base, cancel slide
                self.period = self.base_period
                self.wf_slide = 0
                self.wf_pos += 1
                continue

            elif b == CMD_VWF:
                # Vibrato waveform selection (store but use sine)
                self.wf_pos += 2
                continue

            elif b == CMD_JWS_JVS:
                self.jvs_pending = param
                self.wf_pos += 2
                continue

            else:
                self.wf_pos += 1
                continue

        self.wf_end = True

    def _tick(self):
        """Process one tick of the synth engine."""

        # --- Volume sequence ---
        if not self.vol_halt and not self.vol_end:
            if self.vol_wait > 0:
                self.vol_wait -= 1
            else:
                self.vol_ctr -= 1
                if self.vol_ctr <= 0:
                    self.vol_ctr = self.vol_spd
                    self._step_vol()

        # Apply volume slide
        if self.vol_slide != 0:
            self.vol += self.vol_slide
            if self.vol < 0:
                self.vol = 0
            elif self.vol > 128:
                self.vol = 128

        # Apply volume envelope (EN1/EN2)
        if 0 <= self.vol_env_wf < len(self.msh.waveforms):
            env = self.msh.waveforms[self.vol_env_wf]
            if env and self.vol_env_pos < len(env):
                # Map signed byte (-128..127) to volume (0..64)
                self.vol = max(0, min(64, (env[self.vol_env_pos] + 128) * 64 // 256))
                self.vol_env_pos += 1
                if self.vol_env_pos >= len(env):
                    if self.vol_env_loop:
                        self.vol_env_pos = 0
                    else:
                        self.vol_env_wf = -1

        # --- Waveform sequence ---
        if not self.wf_halt and not self.wf_end:
            if self.wf_wait > 0:
                self.wf_wait -= 1
            else:
                self.wf_ctr -= 1
                if self.wf_ctr <= 0:
                    self.wf_ctr = self.wf_spd
                    self._step_wf()

        # Apply period slide
        if self.wf_slide != 0:
            self.period += self.wf_slide
            if self.period < 113:
                self.period = 113
            elif self.period > 6848:
                self.period = 6848

        # Compute effective period with arpeggio
        self.eff_period = self.period
        if self.arp:
            note_offset = self.arp[self.arp_idx % len(self.arp)]
            if note_offset > 0:
                self.eff_period = int(self.period * (2.0 ** (-note_offset / 12.0)))
            self.arp_idx += 1

        # Vibrato modulation
        self.vib_val = 0
        if self.vib_depth > 0 and self.vib_speed > 0:
            self.vib_val = int(math.sin(2.0 * math.pi * self.vib_phase / 64.0) * self.vib_depth)
            self.vib_phase = (self.vib_phase + self.vib_speed) % 64

        # --- Cross-sequence jumps (deferred) ---
        if self.jws_pending >= 0:
            if self.jws_pending < len(self.msh.wf_tbl):
                self.wf_pos = self.jws_pending
                self.wf_halt = False
                self.wf_end = False
            self.jws_pending = -1

        if self.jvs_pending >= 0:
            if self.jvs_pending < len(self.msh.vol_tbl):
                self.vol_pos = self.jvs_pending
                self.vol_halt = False
                self.vol_end = False
            self.jvs_pending = -1

        # --- HLT sustain / key-off simulation ---
        if self.vol_halt or self.wf_halt:
            self.halt_timer += 1
            if self.halt_timer >= HLT_SUSTAIN_TICKS:
                if self.vol_halt:
                    self.vol_halt = False
                    self.vol_pos += 1  # Advance past HLT byte
                if self.wf_halt:
                    self.wf_halt = False
                    self.wf_pos += 1

    def _gen_samples(self, num_samples):
        """Generate audio samples for the current tick state."""
        m = self.msh

        # Get current waveform
        if self.cur_wf < len(m.waveforms):
            wf = m.waveforms[self.cur_wf]
        else:
            wf = [0]
        wf_len = len(wf) if wf else 1
        if wf_len == 0:
            wf = [0]
            wf_len = 1

        # Effective period with vibrato
        eff_p = self.eff_period + self.vib_val
        if eff_p < 113:
            eff_p = 113

        # Sample increment per output sample
        increment = AMIGA_PAL_CLOCK / (eff_p * OUTPUT_RATE)

        # Volume scaling (0-64 range maps to 0.0-1.0)
        vol_frac = self.vol / 64.0
        if vol_frac < 0.0:
            vol_frac = 0.0
        elif vol_frac > 2.0:
            vol_frac = 2.0

        samples = []
        pos = self.sample_pos

        for _ in range(num_samples):
            # Linear interpolation between adjacent waveform samples
            idx = int(pos)
            frac = pos - idx
            idx0 = idx % wf_len
            idx1 = (idx + 1) % wf_len
            sample = wf[idx0] * (1.0 - frac) + wf[idx1] * frac

            # Scale by volume and convert to 16-bit
            out = int(sample * 256.0 * vol_frac)
            if out > 32767:
                out = 32767
            elif out < -32768:
                out = -32768
            samples.append(out)

            pos += increment
            # Wrap within waveform length
            if pos >= wf_len:
                pos -= wf_len * int(pos / wf_len)
                if pos >= wf_len:
                    pos = math.fmod(pos, wf_len)

        self.sample_pos = pos
        return samples

    def render(self, max_ticks=MAX_TICKS):
        """Render the synth sound to an array of 16-bit signed samples."""
        self._reset()
        output = []
        silence_ticks = 0

        for _ in range(max_ticks):
            self._tick()
            output.extend(self._gen_samples(SAMPLES_PER_TICK))

            # Early termination: volume at zero and not going to recover
            vol_dead = (self.vol <= 0 and self.vol_slide <= 0 and
                        self.vol_env_wf < 0 and
                        (self.vol_end or
                         (self.vol_halt and self.halt_timer >= HLT_SUSTAIN_TICKS)))
            if vol_dead:
                silence_ticks += 1
                if silence_ticks > 5:
                    break
            else:
                silence_ticks = 0

        # Apply fade-out at the end to avoid clicks
        fade_len = min(FADE_SAMPLES, len(output))
        if fade_len > 0:
            for i in range(fade_len):
                idx = len(output) - fade_len + i
                factor = (fade_len - i) / fade_len
                output[idx] = int(output[idx] * factor)

        return output


# --- WAV Writer ---

def write_wav(filepath, samples, sample_rate=OUTPUT_RATE):
    """Write 16-bit mono PCM samples to a WAV file."""
    with wave.open(filepath, 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)  # 16-bit
        w.setframerate(sample_rate)
        w.writeframes(struct.pack(f'<{len(samples)}h', *samples))


# --- Main ---

def convert(input_path, output_dir):
    """Convert one MSH file to WAV."""
    msh = MSHFile(input_path)

    # Validate file integrity
    ok, msg = msh.validate()
    if not ok:
        print(f"WARNING: {msg}", file=sys.stderr)

    # Print file info
    print(msh.info())

    # Render
    engine = SynthEngine(msh)
    samples = engine.render()

    # Write WAV
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.basename(input_path)
    # Remove common extensions
    for ext in ('.syn', '.SYN', '.Syn'):
        if base_name.endswith(ext):
            base_name = base_name[:-len(ext)]
            break
    wav_path = os.path.join(output_dir, base_name + '.wav')
    write_wav(wav_path, samples)

    duration = len(samples) / OUTPUT_RATE
    print(f"Output: {wav_path} ({duration:.2f}s, {len(samples)} samples)")
    return wav_path


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(input_path):
        print(f"Error: {input_path} not found", file=sys.stderr)
        sys.exit(1)

    convert(input_path, output_dir)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# Vibe coded by Claude

"""mml2wav.py - Convert BASIC PLAY MML .MUS files to WAV (PC speaker square wave)

Reproduces the authentic sound of DOS-era PC speaker music by using
MUS.COM's exact frequency table and timing formula with square wave synthesis.

Usage:
    mml2wav.py <input.mus> <output.wav>     Convert MML to WAV
    mml2wav.py --detect <input.mus>          Detect if file is valid MML
"""

import sys
import struct
import argparse
import os
import re
import array
import math

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SAMPLE_RATE = 44100
AMPLITUDE = 8000       # ~24% of 16-bit signed max (32767), comfortable level

# MUS.COM PIT (Programmable Interval Timer) constants
PIT_CLOCK = 1193182              # PIT base clock Hz
PIT_FREQ_CONSTANT = 1179648     # MUS.COM uses this for divisor calc
TICK_RATE = 72.826              # PIT ch0 at divisor 16384 (~4x normal)

# MUS.COM frequency table: 12 chromatic semitones (C through B), octave 8 base
# Right-shifted by (8 - octave) for lower octaves
FREQ_TABLE = [
    0x4168, 0x4548, 0x4968, 0x4DC8,  # C,  C#, D,  D#
    0x5268, 0x5750, 0x5C80, 0x6200,  # E,  F,  F#, G
    0x67D0, 0x6E00, 0x7410, 0x7B80,  # G#, A,  A#, B
]

NOTE_MAP = {
    'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11,
    'H': 11,  # German notation: H = B natural
}

NON_MML_CHARS = set('()=_{}[]\\/@$^&|~!?:')


# ---------------------------------------------------------------------------
# File I/O helpers
# ---------------------------------------------------------------------------

def read_mus_file(filepath):
    """Read a .MUS file, handling BASIC tokenized format and encodings."""
    with open(filepath, 'rb') as f:
        raw = f.read()

    high_bit_count = sum(1 for b in raw if b & 0x80 and b != 0x1A)
    if high_bit_count > len(raw) * 0.3 and len(raw) > 10:
        cleaned = []
        skip_to_lf = False
        for b in raw:
            b &= 0x7F
            if skip_to_lf:
                if b == 0x0A:
                    skip_to_lf = False
                continue
            if b == ord(':'):
                skip_to_lf = True
                continue
            if b >= 0x20:
                cleaned.append(chr(b))
            elif b in (0x0A, 0x0D):
                cleaned.append('\n')
        text = ''.join(cleaned)
    else:
        try:
            text = raw.decode('utf-8', errors='replace')
        except Exception:
            text = raw.decode('latin-1', errors='replace')

    if '\x1a' in text:
        text = text[:text.index('\x1a')]
    return text


def preprocess_mml(text):
    """Remove comments, normalize, and uppercase MML text."""
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped[0] in (':', "'", ';', '%', '*', '$'):
            continue
        if ':' in stripped:
            stripped = stripped[:stripped.index(':')].rstrip()
            if not stripped:
                continue
        cleaned.append(stripped)
    return ' '.join(cleaned).upper()


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------

def detect_mml(text):
    """Return True if text appears to be valid MML / BASIC PLAY data."""
    processed = preprocess_mml(text)
    if not processed:
        return False

    non_mml = sum(1 for c in processed if c in NON_MML_CHARS)
    if len(processed) > 0 and non_mml / len(processed) > 0.05:
        return False

    NON_MML_LETTERS = set('IJQUVWXYZ')
    runs = re.findall(r'[A-Z]{3,}', processed)
    english_chars = sum(len(w) for w in runs
                        if any(c in NON_MML_LETTERS for c in w))
    alpha_count = sum(1 for c in processed if c.isalpha())
    if alpha_count > 0 and english_chars / alpha_count > 0.10:
        return False

    parser = MMLParser()
    try:
        parser.parse(text)
    except Exception:
        return False
    return parser.note_count >= 1


# ---------------------------------------------------------------------------
# MML Parser -> audio events
# ---------------------------------------------------------------------------

class MMLParser:
    """Parse MML text into a list of (frequency, note_on_secs, rest_secs) tuples."""

    def __init__(self):
        self.pos = 0
        self.text = ""
        self.octave = 4
        self.default_length = 4
        self.tempo = 120
        self.style = 'N'
        self.staccato_level = None
        self.octave_shift = 0  # one-shot octave modifier (" = +1, ' = -1)
        self.audio_events = []
        self.note_count = 0
        self.command_count = 0

    def parse(self, text):
        self.text = preprocess_mml(text)
        self.pos = 0
        while self.pos < len(self.text):
            self._dispatch()
        return self.audio_events

    # -- helpers --

    def _peek(self):
        return self.text[self.pos] if self.pos < len(self.text) else None

    def _advance(self):
        if self.pos < len(self.text):
            ch = self.text[self.pos]
            self.pos += 1
            return ch
        return None

    def _try_number(self):
        if self.pos >= len(self.text) or not self.text[self.pos].isdigit():
            return None
        n = 0
        while self.pos < len(self.text) and self.text[self.pos].isdigit():
            n = n * 10 + int(self.text[self.pos])
            self.pos += 1
        return n

    def _note_frequency(self, semitone, octave):
        """Compute frequency exactly as MUS.COM does via PIT frequency table."""
        idx = semitone % 12
        # Handle accidentals wrapping across octave boundaries
        if semitone < 0:
            idx = (semitone % 12)
            octave -= 1
        elif semitone >= 12:
            idx = semitone % 12
            octave += 1

        base = FREQ_TABLE[idx]
        shift = 8 - octave
        if shift > 0:
            shifted = base >> shift
        elif shift < 0:
            shifted = base << (-shift)
        else:
            shifted = base
        if shifted <= 0:
            return 0.0
        pit_divisor = PIT_FREQ_CONSTANT // shifted
        if pit_divisor <= 0:
            return 0.0
        return PIT_CLOCK / pit_divisor

    def _raw_duration(self, length):
        """Compute raw duration units: 256 / L (integer division, MUS.COM style)."""
        if length is None or length <= 0:
            length = self.default_length
        if length <= 0:
            length = 4
        return 256 // length if length > 0 else 256

    def _parse_dots(self, raw):
        """Consume '.' characters and extend duration (1.5x, 1.75x, ...)."""
        total = raw
        add = raw // 2
        while self._peek() == '.' and add > 0:
            total += add
            add //= 2
            self.pos += 1
        # Consume any remaining dots that would add 0
        while self._peek() == '.':
            self.pos += 1
        return total

    def _gate_split(self, duration):
        """Split total duration into (note_on, rest) using MUS.COM style rules."""
        if self.staccato_level is not None:
            if self.staccato_level == 0:
                return duration, 0
            elif self.staccato_level == 1:
                rest = duration >> 3
                return duration - rest, rest
            else:
                rest = duration >> 2
                return duration - rest, rest

        if self.style == 'L':
            return duration, 0
        elif self.style == 'S':
            rest = duration >> 2
            return duration - rest, rest
        else:  # Normal
            rest = duration >> 3
            return duration - rest, rest

    def _to_seconds(self, raw_duration):
        """Convert raw duration units to seconds using MUS.COM timing formula.

        MUS.COM: delay_ticks = (tempo_value * raw_duration) / 200 + 1
        where tempo_value = 256 - T, tick_rate = 72.826 Hz

        The +1 ensures a minimum of 1 tick (~13.7ms) per wait_ticks call,
        even when raw_duration is 0 (e.g. 256 // 1280 = 0 for L1280).
        """
        tempo_val = max(1, 256 - self.tempo)
        delay_ticks = (tempo_val * raw_duration) // 200 + 1
        return delay_ticks / TICK_RATE

    def _is_legato(self):
        """Check if current style skips the rest portion (ML or S0)."""
        if self.staccato_level is not None:
            return self.staccato_level == 0
        return self.style == 'L'

    # -- event emitters --

    def _emit_note(self, frequency, length=None):
        raw = self._raw_duration(length)
        total = self._parse_dots(raw)
        note_on_raw, rest_raw = self._gate_split(total)
        note_on_secs = self._to_seconds(note_on_raw)
        # MUS.COM calls wait_ticks for both note-on and rest in MN/MS modes
        # (each getting the +1 tick floor), but skips rest entirely for legato
        if self._is_legato():
            rest_secs = 0.0
        else:
            rest_secs = self._to_seconds(rest_raw)
        self.audio_events.append((frequency, note_on_secs, rest_secs))
        self.note_count += 1

    def _emit_rest(self, length=None):
        raw = self._raw_duration(length)
        total = self._parse_dots(raw)
        rest_secs = self._to_seconds(total)
        self.audio_events.append((0.0, 0.0, rest_secs))

    # -- command dispatch --

    def _dispatch(self):
        ch = self._peek()
        if ch is None:
            return
        if ch in ' \t\r\n,;':
            self._advance()
            return
        if ch in NOTE_MAP:
            self._cmd_note()
            return

        handler = {
            'O': self._cmd_octave,
            '>': self._cmd_octave_up,
            '<': self._cmd_octave_down,
            '"': self._cmd_oneshot_up,
            "'": self._cmd_oneshot_down,
            'L': self._cmd_length,
            'T': self._cmd_tempo,
            'N': self._cmd_note_number,
            'P': self._cmd_rest,
            'R': self._cmd_rest,
            'M': self._cmd_music_mode,
            'S': self._cmd_staccato,
            'V': self._cmd_skip,
            'K': self._cmd_skip,
        }.get(ch)
        if handler:
            handler()
        else:
            self._advance()

    # -- individual commands --

    def _cmd_note(self):
        ch = self._advance()
        semitone = NOTE_MAP[ch]
        acc = self._peek()
        if acc in ('+', '#'):
            semitone += 1
            self._advance()
        elif acc == '-':
            semitone -= 1
            self._advance()
        octave = max(0, min(8, self.octave + self.octave_shift))
        self.octave_shift = 0
        freq = self._note_frequency(semitone, octave)
        length = self._try_number()
        self._emit_note(freq, length)
        self.command_count += 1

    def _cmd_oneshot_up(self):
        self._advance()
        self.octave_shift += 1

    def _cmd_oneshot_down(self):
        self._advance()
        self.octave_shift -= 1

    def _cmd_octave(self):
        self._advance()
        n = self._try_number()
        self.octave = max(0, min(8, n)) if n is not None else 0
        self.command_count += 1

    def _cmd_octave_up(self):
        self._advance()
        self.octave = min(self.octave + 1, 8)
        self.command_count += 1

    def _cmd_octave_down(self):
        self._advance()
        self.octave = max(self.octave - 1, 0)
        self.command_count += 1

    def _cmd_length(self):
        self._advance()
        n = self._try_number()
        if n is not None and n > 0:
            self.default_length = n
        self.command_count += 1

    def _cmd_tempo(self):
        self._advance()
        n = self._try_number()
        if n is not None and n > 0:
            self.tempo = n
        self.command_count += 1

    def _cmd_note_number(self):
        self._advance()
        n = self._try_number()
        if n is None or n == 0:
            self._emit_rest()
        else:
            octave = (n - 1) // 12
            semitone = (n - 1) % 12
            freq = self._note_frequency(semitone, octave)
            self._emit_note(freq)
        self.command_count += 1

    def _cmd_rest(self):
        self._advance()
        n = self._try_number()
        self._emit_rest(n)
        self.command_count += 1

    def _cmd_music_mode(self):
        self._advance()
        mode = self._peek()
        if mode == 'N':
            self.style = 'N'; self.staccato_level = None; self._advance()
        elif mode == 'L':
            self.style = 'L'; self.staccato_level = None; self._advance()
        elif mode == 'S':
            self.style = 'S'; self.staccato_level = None; self._advance()
        elif mode in ('B', 'F'):
            self._advance()
        self.command_count += 1

    def _cmd_staccato(self):
        self._advance()
        n = self._try_number()
        if n is not None:
            self.staccato_level = n
        self.command_count += 1

    def _cmd_skip(self):
        self._advance()
        self._try_number()
        self.command_count += 1


# ---------------------------------------------------------------------------
# WAV synthesis and file writer
# ---------------------------------------------------------------------------

def synthesize_wav(audio_events):
    """Convert audio events to 16-bit signed PCM samples (square wave)."""
    samples = array.array('h')
    for freq, note_on_secs, rest_secs in audio_events:
        if freq > 20.0 and note_on_secs > 0:
            num = int(SAMPLE_RATE * note_on_secs)
            period = SAMPLE_RATE / freq
            for i in range(num):
                phase = (i / period) % 1.0
                samples.append(AMPLITUDE if phase < 0.5 else -AMPLITUDE)
        elif note_on_secs > 0:
            num = int(SAMPLE_RATE * note_on_secs)
            samples.extend(array.array('h', [0] * num))

        if rest_secs > 0:
            num = int(SAMPLE_RATE * rest_secs)
            samples.extend(array.array('h', [0] * num))

    return samples


def write_wav(filepath, samples):
    """Write 16-bit mono PCM WAV file."""
    data_size = len(samples) * 2
    with open(filepath, 'wb') as f:
        # RIFF header
        f.write(b'RIFF')
        f.write(struct.pack('<I', 36 + data_size))
        f.write(b'WAVE')
        # fmt chunk
        f.write(b'fmt ')
        f.write(struct.pack('<IHHIIHH',
                            16,             # chunk size
                            1,              # PCM format
                            1,              # mono
                            SAMPLE_RATE,    # sample rate
                            SAMPLE_RATE * 2,  # byte rate
                            2,              # block align
                            16))            # bits per sample
        # data chunk
        f.write(b'data')
        f.write(struct.pack('<I', data_size))
        f.write(samples.tobytes())


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description='Convert BASIC PLAY MML .MUS files to WAV (PC speaker)')
    ap.add_argument('input', help='Input .MUS file')
    ap.add_argument('output', nargs='?', help='Output .WAV file')
    ap.add_argument('--detect', action='store_true',
                    help='Detect format and print identifier (no conversion)')
    args = ap.parse_args()

    if not os.path.isfile(args.input):
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    text = read_mus_file(args.input)

    if args.detect:
        if detect_mml(text):
            print("PLAY/Music Macro Language")
        sys.exit(0)

    if not args.output:
        print("Error: Output file required for conversion", file=sys.stderr)
        sys.exit(1)

    parser = MMLParser()
    audio_events = parser.parse(text)

    if parser.note_count == 0:
        print(f"Warning: No notes found in {args.input}", file=sys.stderr)

    samples = synthesize_wav(audio_events)
    write_wav(args.output, samples)

    duration = len(samples) / SAMPLE_RATE
    print(f"Converted {parser.note_count} notes to {args.output} "
          f"({duration:.1f}s, {len(samples)*2} bytes)", file=sys.stderr)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# Vibe coded by Codex
# Format/algorithm reference: miniBAE (c) 2009 Beatnik, Inc.; BSD notice in
# richMusicFormat.txt, section 17.
"""Render Beatnik Rich Music Format to WAV. See richMusicFormat.txt for details.

Requires Python 3.10+, TiMidity++, ./eaw/gravis.cfg, and FFmpeg for compressed
samples. No Python packages, network access, or native build are required.
"""

from __future__ import annotations

import argparse
from array import array
from dataclasses import dataclass, field
import math
import os
from pathlib import Path
import re
import shlex
import shutil
import struct
import subprocess
import sys
import tempfile
import unicodedata
import wave


MAX_FILE = 256 * 1024 * 1024
MAX_PCM = 256 * 1024 * 1024
MAX_SECONDS = 14400
MIDI_TYPES = (b"ecmi", b"emid", b"cmid", b"Midi", b"MIDI")
SOUND_TYPES = (b"csnd", b"esnd", b"snd ")
TEXT_TAGS = set(b"TITL PERF COMP COPD COPL LICC LUSE LDOM LTRM EXPD NOTE INDX "
                b"GENR SUBG TMPO OSRC MANU MSC1 MSC2 MSC3 MSC4 MSC5 MSC6 MSC7 MSC8".split())


class FormatError(Exception):
    """Invalid, unsupported, or incomplete input."""


def need(data: bytes, offset: int, size: int, label: str = "data") -> bytes:
    if offset < 0 or size < 0 or offset + size > len(data):
        raise FormatError(f"Truncated {label} at byte {offset} (need {size} bytes)")
    return data[offset:offset + size]


def u16(data: bytes, offset: int = 0) -> int:
    return int.from_bytes(need(data, offset, 2), "big")


def s16(data: bytes, offset: int = 0) -> int:
    return int.from_bytes(need(data, offset, 2), "big", signed=True)


def u32(data: bytes, offset: int = 0) -> int:
    return int.from_bytes(need(data, offset, 4), "big")


def text(data: bytes) -> str:
    return data.decode("mac_roman").strip().strip("\x00")


def decrypt(data: bytes) -> bytes:
    state = 56549
    result = bytearray(len(data))
    for i, cipher in enumerate(data):
        result[i] = (cipher ^ (state >> 8)) & 255
        state = ((cipher + state) * 52845 + 22719) & 0xFFFFFFFF
    return bytes(result)


def cstring(data: bytes, offset: int, encrypted: bool) -> tuple[str, int]:
    state = 56549
    result = bytearray()
    while offset < len(data):
        cipher = data[offset]
        value = (cipher ^ (state >> 8)) & 255 if encrypted else cipher
        state = ((cipher + state) * 52845 + 22719) & 0xFFFFFFFF
        offset += 1
        if not value:
            return text(bytes(result)), offset
        result.append(value)
    raise FormatError("Unterminated SONG metadata string")


def decompress(data: bytes, ignore_type: bool = False) -> bytes:
    """Beatnik LZSS, with the optional sample delta transform."""
    size = u32(data) & 0xFFFFFF
    kind = 255 if ignore_type else data[0]
    output = bytearray()
    pos = 4
    while len(output) < size:
        flags = need(data, pos, 1)[0]
        pos += 1
        for bit in range(8):
            if len(output) >= size:
                break
            if flags & (1 << bit):
                output.extend(need(data, pos, 1))
                pos += 1
            else:
                token = u16(data, pos)
                pos += 2
                distance = 4096 - (token & 4095)
                count = min((token >> 12) + 3, size - len(output))
                if distance > len(output):
                    raise FormatError("Invalid LZSS back-reference")
                for _ in range(count):
                    output.append(output[-distance])
    if kind == 255:
        return bytes(output)
    if kind not in (0, 1, 2, 3):
        raise FormatError(f"Unknown LZSS delta transform {kind}")
    # The delta transforms run over the entire decompressed byte stream.
    channels = 2 if kind in (1, 3) else 1
    width = 2 if kind in (2, 3) else 1
    if len(output) % (channels * width):
        raise FormatError("Misaligned delta-compressed data")
    previous = [0] * channels
    for i in range(0, len(output), width):
        ch = (i // width) % channels
        value = int.from_bytes(output[i:i + width], "big")
        previous[ch] = (previous[ch] + value) & ((1 << (8 * width)) - 1)
        output[i:i + width] = previous[ch].to_bytes(width, "big")
    return bytes(output)


@dataclass
class Resource:
    kind: bytes
    id: int
    name: str
    data: bytes
    offset: int


def read_resources(path: Path) -> list[Resource]:
    if path.stat().st_size > MAX_FILE:
        raise FormatError("Input exceeds the 256 MiB safety limit")
    data = path.read_bytes()
    if need(data, 0, 4) != b"IREZ":
        raise FormatError("Not an IREZ/Beatnik resource file")
    if u32(data, 4) != 1:
        raise FormatError(f"Unsupported IREZ version {u32(data, 4)}")
    count = u32(data, 8)
    if count > (len(data) - 12) // 17:
        raise FormatError("Impossible resource count")
    result = []
    offset = 12
    for _ in range(count):
        header = need(data, offset, 13, "resource header")
        nxt, kind, rid, name_len = struct.unpack(">I4siB", header)
        name = text(need(data, offset + 13, name_len, "resource name"))
        start = offset + 17 + name_len
        size = u32(data, start - 4)
        payload = need(data, start, size, f"{kind!r} resource")
        if nxt < start + size or nxt > len(data):
            raise FormatError("Invalid next-resource offset")
        result.append(Resource(kind, rid, name, payload, start))
        offset = nxt
    return result


def find_resource(resources: list[Resource], kinds: tuple[bytes, ...],
                  rid: int) -> Resource:
    for kind in kinds:
        for resource in resources:
            if resource.kind == kind and resource.id == rid:
                return resource
    # Old writers sometimes zero-extended a signed 16-bit ID.
    for kind in kinds:
        for resource in resources:
            if resource.kind == kind and (resource.id & 65535) == (rid & 65535):
                return resource
    raise FormatError(f"Missing {kinds[0].decode().strip()} resource ID {rid}")


@dataclass
class Song:
    id: int
    kind: int = 1
    title: str = ""
    tempo: float = 1.0
    pitch: int = 0
    volume: int = 127
    reverb: int = 0
    percussion: int = -1
    remaps: dict[int, int] = field(default_factory=dict)
    velocity: list[int] | None = None


def parse_song(resource: Resource) -> Song:
    data = resource.data
    need(data, 0, 18, "SONG header")
    song = Song(s16(data), data[6], reverb=data[3])
    raw_tempo = u16(data, 4) or 16667
    song.tempo = min(300, max(25, (100 * raw_tempo) // 16667)) / 100
    if song.kind == 0:
        song.pitch = struct.unpack("b", data[7:8])[0]
        song.percussion = struct.unpack("b", data[14:15])[0]
        offset = 18
        for _ in range(u16(data, 16)):
            song.remaps[u16(data, offset)] = s16(data, offset + 2)
            offset += 4
        for tag in (b"COPD", b"COMP", b"TITL", b"LICC"):
            if offset == len(data):
                break
            length = need(data, offset, 1)[0]
            value = text(need(data, offset + 1, length))
            offset += 1 + length
            if tag == b"TITL":
                song.title = value
        return song
    if song.kind not in (1, 2):
        raise FormatError(f"Unsupported SONG type {song.kind}")
    need(data, 0, 50, "RMF SONG header")
    if song.kind == 1:
        song.pitch = s16(data, 8)
        song.volume = u16(data, 16) or 127
    else:
        song.volume = u16(data, 14) or 100
    offset = 50
    for _ in range(u16(data, 48)):
        tag = need(data, offset, 4, "SONG metadata tag")
        offset += 4
        if tag in TEXT_TAGS:
            value, offset = cstring(data, offset, bool(data[7]))
            if tag == b"TITL":
                song.title = value
        elif tag == b"VELC":
            song.velocity = list(struct.unpack(">128H", need(data, offset, 256)))
            offset += 256
        elif tag == b"RMAP":
            words = u16(data, offset)
            offset += 2
            if words % 2:
                raise FormatError("Odd word count in RMAP")
            for _ in range(words // 2):
                song.remaps[u16(data, offset)] = s16(data, offset + 2)
                offset += 4
        else:
            raise FormatError(f"Unknown SONG metadata tag {tag!r}; no length to skip it")
    return song


def midi_bytes(resource: Resource) -> bytes:
    data = resource.data
    if resource.kind in (b"emid", b"ecmi"):
        data = decrypt(data)
    if resource.kind in (b"cmid", b"ecmi"):
        data = decompress(data, True)
    if not data.startswith(b"MThd"):
        raise FormatError("Decoded music resource is not a Standard MIDI File")
    return data


@dataclass
class Sample:
    id: int
    name: str
    pcm: bytes                    # Interleaved signed 16-bit little endian.
    rate: int
    channels: int
    root: int
    loop_start: int
    loop_end: int

    @property
    def frames(self) -> int:
        return len(self.pcm) // (2 * self.channels)


def run(command: list[str], *, input_data: bytes | None = None,
        timeout: int = 120) -> bytes:
    try:
        result = subprocess.run(command, input=input_data, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, timeout=timeout)
    except FileNotFoundError:
        raise FormatError(f"Required program is not installed: {command[0]}") from None
    except subprocess.TimeoutExpired:
        raise FormatError(f"{command[0]} exceeded its {timeout}-second time limit") from None
    if result.returncode:
        error = result.stderr.decode("utf-8", "replace")[-4000:]
        raise FormatError(f"{command[0]} failed ({result.returncode}): {error.strip()}")
    if Path(command[0]).name == "timidity":
        messages = (result.stdout + result.stderr).decode("utf-8", "replace")
        if re.search(r"couldn't load instrument|no instrument mapped|illegal bags",
                     messages, re.IGNORECASE):
            raise FormatError("TiMidity could not load a required instrument:\n" + messages[-4000:])
    return result.stdout


def chunk(tag: bytes, data: bytes, endian: str = "<") -> bytes:
    return tag + struct.pack(endian + "I", len(data)) + data + b"\0" * (len(data) & 1)


def extended80(rate: int) -> bytes:
    exponent = rate.bit_length() - 1
    return struct.pack(">HQ", exponent + 16383, rate << (63 - exponent))


def decode_sample(resource: Resource) -> Sample:
    data = resource.data
    if resource.kind == b"esnd":
        data = decrypt(data)
    elif resource.kind == b"csnd":
        data = decompress(data)
    fmt = u16(data)
    start_skip = 0
    codec = b"NONE"
    intel = False
    if fmt == 3:
        header = need(data, 2, 124, "type-3 sound header")
        codec = header[:4]
        rate = round(u32(header, 4) / 65536)
        decoded_size, frames, encoded_size = struct.unpack_from(">III", header, 8)
        start_skip = u32(header, 24)
        loop_start, loop_end = u32(header, 28), u32(header, 52)
        root, channels, bits, embedded, encrypted, intel = header[84:90]
        payload = need(data, 126, encoded_size, "type-3 sample data")
        if encrypted:
            raise FormatError("Inner type-3 sample encryption is unsupported")
        if codec.startswith(b"mpg"):
            frames = decoded_size // max(1, channels * 2)
            start_skip //= max(1, channels)
            bits = 16
    elif fmt in (1, 2):
        synths = u16(data, 2) if fmt == 1 else 0
        commands = u16(data, 4 + synths * 6)
        offset = 6 + synths * 6 + commands * 8
        header = need(data, offset, 22, "sound header")
        rate = round(u32(header, 8) / 65536)
        loop_start, loop_end = u32(header, 12), u32(header, 16)
        encoding, root = header[20:22]
        if encoding == 0:
            frames, channels, bits = u32(header, 4), 1, 8
            payload = need(data, offset + 22, frames, "8-bit PCM")
        elif encoding in (254, 255):
            header = need(data, offset, 64, "extended/compressed sound header")
            channels = u32(header, 4)
            frames = u32(header, 22)
            bits = u16(header, 48 if encoding == 255 else 62)
            if encoding == 255:
                intel = bool(header[51])
                payload = need(data, offset + 64, frames * channels * (bits // 8), "PCM")
            else:
                compression = s16(header, 56)
                codec = header[40:44]
                if codec in (b"mac3", b"mac6"):
                    codec = codec.upper()
                if compression == 3:
                    codec = b"MAC3"
                elif compression == 4:
                    codec = b"MAC6"
                elif compression != -1:
                    raise FormatError(f"Unsupported Sound Manager compression ID {compression}")
                if codec == b"ima4":
                    payload = need(data, offset + 64, frames * 34 * channels, "IMA packets")
                    frames *= 64
                    bits = 16
                elif codec in (b"ulaw", b"alaw"):
                    payload = need(data, offset + 64, frames * channels, "G.711 samples")
                    bits = 16
                elif codec in (b"MAC3", b"MAC6"):
                    payload = data[offset + 64:]
                    frames = len(payload) * (3 if codec == b"MAC3" else 6) // max(channels, 1)
                    bits = 16
                else:
                    raise FormatError(f"Unsupported sound codec {codec!r}")
        else:
            raise FormatError(f"Unsupported sound header encoding 0x{encoding:02x}")
    else:
        raise FormatError(f"Unsupported snd resource format {fmt}")
    if not 1 <= channels <= 2 or not 1000 <= rate <= 192000 or bits not in (8, 16):
        raise FormatError(f"Unsupported sample layout: {channels} channels, {rate} Hz, {bits} bits")
    if frames <= 0 or (frames + start_skip) * channels * 2 > MAX_PCM:
        raise FormatError("Empty sample or decoded sample exceeds 256 MiB")
    if codec in (b"NONE", b"none", b"\0\0\0\0"):
        if bits == 8:
            samples = array("h", ((x - 128) << 8 for x in payload))
            if sys.byteorder != "little":
                samples.byteswap()
            pcm = samples.tobytes()
        else:
            samples = array("h")
            samples.frombytes(payload)
            if not intel:
                samples.byteswap()
            pcm = samples.tobytes()
    else:
        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            raise FormatError(f"FFmpeg is required to decode embedded {codec.decode()} samples")
        if codec.startswith(b"mpg"):
            input_format = "mp3"
            encoded = payload
        elif codec in (b"ima4", b"MAC3", b"MAC6", b"ulaw", b"alaw"):
            # Wrapping Sound Manager packets in AIFF-C lets FFmpeg decode them.
            comm = struct.pack(">hIh", channels, frames, 16) + extended80(rate) + codec + b"\0\0"
            encoded = chunk(b"FORM", b"AIFC" + chunk(b"FVER", struct.pack(">I", 0xA2805140), ">")
                            + chunk(b"COMM", comm, ">")
                            + chunk(b"SSND", b"\0" * 8 + payload, ">"), ">")
            input_format = "aiff"
        else:
            raise FormatError(f"Unsupported type-3 codec {codec!r}")
        pcm = run([ffmpeg, "-v", "error", "-nostdin", "-threads", "1", "-f", input_format,
                   "-i", "pipe:0", "-fs", str(MAX_PCM),
                   "-f", "s16le", "-acodec", "pcm_s16le", "-ac", str(channels),
                   "pipe:1"], input_data=encoded)
    pcm = pcm[start_skip * channels * 2:(start_skip + frames) * channels * 2]
    if not pcm:
        raise FormatError(f"Sample {resource.id} decoded to no audio")
    if len(pcm) < frames * channels * 2:
        # MPEG frame padding / encoder delay can leave a short final packet.
        missing = frames * channels * 2 - len(pcm)
        if missing > 2304 * channels * 2:
            raise FormatError(f"Sample {resource.id} is truncated after decoding")
        pcm += b"\0" * missing
    return Sample(resource.id, resource.name, pcm, rate, channels,
                  min(root, 127), loop_start, loop_end)


@dataclass
class Zone:
    low: int
    high: int
    sample_id: int
    root: int | None
    volume: int


@dataclass
class Instrument:
    id: int
    name: str
    flags1: int
    flags2: int
    master_root: int
    pan: int
    zones: list[Zone]
    envelope: list[tuple[int, int, bytes]] = field(default_factory=list)
    extra_units: set[bytes] = field(default_factory=set)


def parse_instrument(resource: Resource) -> Instrument:
    data = resource.data
    need(data, 0, 14, "instrument header")
    flags1, flags2 = data[5:7]
    root = s16(data, 2)
    split_count = u16(data, 12)
    need(data, 14, 8 * split_count, "instrument key splits")
    zones = []
    if split_count < 2:
        zones.append(Zone(0, 127, s16(data), s16(data, 8) if flags2 & 8 else None,
                          (s16(data, 10) or 100) if flags2 & 8 else 100))
    else:
        shift = root - 60 if root else 0
        for i in range(split_count):
            offset = 14 + 8 * i
            low, high = data[offset:offset + 2]
            zones.append(Zone(max(0, low + shift), min(127, high + shift), s16(data, offset + 2),
                              s16(data, offset + 4) if flags2 & 8 else None,
                              (s16(data, offset + 6) or 100) if flags2 & 8 else 100))
    instrument = Instrument(resource.id, resource.name, flags1, flags2, root,
                            struct.unpack("b", data[4:5])[0], zones)
    if flags1 & 2:
        # Historical format has variable tremolo data before the sentinel.
        offset = data.find(b"\x80\x00", 14 + 8 * split_count)
        if offset < 0:
            raise FormatError("Missing instrument tremolo terminator")
        offset += 4
        for _ in range(2):
            length = need(data, offset, 1)[0]
            need(data, offset + 1, length)
            offset += 1 + length
        need(data, offset, 13, "instrument extension")
        offset += 12
        count = data[offset]
        offset += 1
        for _ in range(count):
            raw_tag = need(data, offset, 4)
            # Beatnik Editor left an overstated unit count and this terminal
            # filler in several otherwise valid files (e.g. FreshPotato).
            if raw_tag == b"\xf1" * 4 and offset + 4 == len(data):
                break
            tag = bytes(v & 0x5F for v in raw_tag)
            offset += 4
            if tag in (b"ADSR", b"VOLU", b"PITC", b"SPAN", b"PAN\x00", b"LPFR", b"LPRE", b"LPAM"):
                stages = need(data, offset, 1)[0]
                offset += 1
                if stages > 8:
                    raise FormatError("Too many instrument envelope stages")
                envelope = []
                for _ in range(stages):
                    level, duration, flag = struct.unpack(">iI4s", need(data, offset, 12))
                    envelope.append((level, duration, flag.upper()))
                    offset += 12
                if tag == b"ADSR":
                    instrument.envelope = envelope
                else:
                    instrument.extra_units.add(tag)
                    need(data, offset, 16, "LFO parameters")
                    offset += 16
            elif tag == b"CURV":
                points = need(data, offset + 8, 1)[0]
                need(data, offset, 9 + 3 * points, "curve parameters")
                offset += 9 + 3 * points
                instrument.extra_units.add(tag)
            elif tag == b"LPGF":
                need(data, offset, 12, "filter parameters")
                offset += 12
                instrument.extra_units.add(tag)
            elif tag == b"DMOD":
                pass
            else:
                raise FormatError(f"Unknown instrument extension {tag!r}")
    return instrument


def timecents(seconds: float) -> int:
    return max(-12000, min(8000, round(1200 * math.log2(max(seconds, 0.000001)))))


def envelope_generators(instrument: Instrument) -> list[tuple[int, int]]:
    """Approximate Beatnik's multistage envelope with a SoundFont ADSR."""
    stages = instrument.envelope
    attack, hold, decay, release, sustain = 0.0, 0.0, 0.0, 0.06, 0
    if not stages:
        # Legacy one-shots play their sample through unless sampleAndHold is set.
        release = 0.06 if instrument.flags1 & 4 else 100.0
    else:
        peak = max(1, max(x[0] for x in stages))
        peak_index = next((i for i, x in enumerate(stages) if x[0] == peak), 0)
        attack = sum(x[1] for x in stages[:peak_index + 1]) / 1e6
        sustain_index = next((i for i, x in enumerate(stages) if x[2] == b"SUST"), None)
        if sustain_index is not None:
            held = max(0, stages[sustain_index][0])
            sustain = min(1440, round(-200 * math.log10(max(held / peak, 1e-8))))
            for level, duration, flag in stages[peak_index + 1:sustain_index]:
                if level == peak:
                    hold += duration / 1e6
                else:
                    decay += duration / 1e6
            release = sum(x[1] for x in stages[sustain_index + 1:]) / 1e6 or 0.06
        elif len(stages) > 1:
            decay = sum(x[1] for x in stages[peak_index + 1:]) / 1e6
            if stages[-1][0] <= 0:
                sustain = 1440
            release = decay or 0.06
    return [(33, -12000), (34, timecents(attack)), (35, timecents(hold)),
            (36, timecents(decay)), (37, sustain), (38, timecents(release))]


def instrument_gain(instrument: Instrument) -> float:
    peak = max((s[0] for s in instrument.envelope), default=4096)
    return max(0.0, peak / 4096) * max((z.volume for z in instrument.zones), default=100) / 100


def sf_name(name: str) -> bytes:
    return name.encode("ascii", "replace")[:19].ljust(20, b"\0")


def write_soundfont(path: Path, instruments: dict[int, Instrument],
                    samples: dict[int, Sample]) -> None:
    pcm = bytearray()
    shdr = bytearray()
    sample_indices = {}
    for sid, sample in sorted(samples.items()):
        values = array("h")
        values.frombytes(sample.pcm)
        for ch in range(sample.channels):
            index = len(shdr) // 46
            sample_indices[sid, ch] = index
            start = len(pcm) // 2
            pcm.extend(values[ch::sample.channels].tobytes())
            end = len(pcm) // 2
            pcm.extend(b"\0" * 92)
            good_loop = 0 <= sample.loop_start < sample.loop_end <= sample.frames
            ls = sample.loop_start if good_loop else 0
            le = sample.loop_end if good_loop else sample.frames
            link = index + (1 if ch == 0 else -1) if sample.channels == 2 else 0
            kind = (4 if ch == 0 else 2) if sample.channels == 2 else 1
            shdr.extend(struct.pack("<20sIIIIIBbHH", sf_name(sample.name), start, end,
                                    start + ls, start + le, sample.rate, sample.root, 0, link, kind))
    shdr.extend(struct.pack("<20sIIIIIBbHH", sf_name("EOS"), 0, 0, 0, 0, 0, 0, 0, 0, 1))
    phdr, pbag, pgen, inst, ibag, igen = (bytearray() for _ in range(6))
    for index, (iid, instrument) in enumerate(sorted(instruments.items())):
        phdr.extend(struct.pack("<20sHHHIII", sf_name(instrument.name), iid % 128,
                                iid // 128, len(pbag) // 4, 0, 0, 0))
        pbag.extend(struct.pack("<HH", len(pgen) // 4, 0))
        pgen.extend(struct.pack("<HH", 41, index))
        inst.extend(struct.pack("<20sH", sf_name(instrument.name), len(ibag) // 4))
        for zone in instrument.zones:
            if zone.low > zone.high:
                continue
            sample = samples[zone.sample_id]
            root = zone.root if zone.root is not None else sample.root
            root += instrument.master_root - 60 if instrument.master_root else 0
            clamped_root = max(0, min(127, root))
            for ch in range(sample.channels):
                ibag.extend(struct.pack("<HH", len(igen) // 4, 0))
                generators = [(43, zone.low | zone.high << 8)]
                generators += envelope_generators(instrument)
                pan = max(-500, min(500, round(instrument.pan * 500 / 63)))
                if sample.channels == 2:
                    pan = -500 if ch == 0 else 500
                generators += [(17, pan), (58, clamped_root)]
                tune = clamped_root - root
                if not instrument.flags1 & 8:
                    tune += 12 * math.log2(22050 / sample.rate)
                if instrument.flags2 & 64:
                    generators.append((56, 0))
                if tune:
                    coarse = max(-120, min(120, int(tune)))
                    generators += [(51, coarse), (52, max(-99, min(99, round((tune - coarse) * 100))))]
                maximum_volume = max(1, max(z.volume for z in instrument.zones))
                attenuation = round(-200 * math.log10(max(zone.volume / maximum_volume, 1e-8)))
                generators.append((48, max(0, min(1440, attenuation))))
                good_loop = (not instrument.flags1 & 32 and
                             0 <= sample.loop_start < sample.loop_end <= sample.frames and
                             sample.loop_end - sample.loop_start >= 2)
                generators.append((54, 3 if good_loop else 0))
                if instrument.flags1 & 1:
                    generators += [(15, 0), (16, 0)]
                # SoundFont requires sampleID to be the last generator in a zone.
                generators.append((53, sample_indices[zone.sample_id, ch]))
                for op, value in generators:
                    igen.extend(struct.pack("<HH", op, value & 65535))
    phdr.extend(struct.pack("<20sHHHIII", sf_name("EOP"), 0, 0, len(pbag) // 4, 0, 0, 0))
    pbag.extend(struct.pack("<HH", len(pgen) // 4, 0))
    pgen.extend(b"\0" * 4)
    inst.extend(struct.pack("<20sH", sf_name("EOI"), len(ibag) // 4))
    ibag.extend(struct.pack("<HH", len(igen) // 4, 0))
    igen.extend(b"\0" * 4)
    info = chunk(b"LIST", b"INFO" + chunk(b"ifil", struct.pack("<HH", 2, 1))
                 + chunk(b"isng", b"EMU8000\0") + chunk(b"INAM", b"RMF embedded instruments\0\0"))
    sdta = chunk(b"LIST", b"sdta" + chunk(b"smpl", bytes(pcm)))
    pdta = chunk(b"LIST", b"pdta" + b"".join(chunk(tag, bytes(data)) for tag, data in (
        (b"phdr", phdr), (b"pbag", pbag), (b"pmod", b"\0" * 10), (b"pgen", pgen),
        (b"inst", inst), (b"ibag", ibag), (b"imod", b"\0" * 10), (b"igen", igen), (b"shdr", shdr))))
    path.write_bytes(chunk(b"RIFF", b"sfbk" + info + sdta + pdta))


@dataclass
class Event:
    tick: int
    track: int
    order: int
    status: int
    data: bytes
    meta: int = -1


def read_vlq(data: bytes, pos: int) -> tuple[int, int]:
    value = 0
    for _ in range(4):
        byte = need(data, pos, 1, "MIDI variable-length integer")[0]
        pos += 1
        value = (value << 7) | (byte & 127)
        if byte < 128:
            return value, pos
    raise FormatError("Overlong MIDI variable-length integer")


def vlq(value: int) -> bytes:
    if not 0 <= value <= 0x0FFFFFFF:
        raise FormatError("MIDI delta time is out of range")
    result = [value & 127]
    while value > 127:
        value >>= 7
        result.append((value & 127) | 128)
    return bytes(reversed(result))


def parse_midi(data: bytes) -> tuple[int, list[Event]]:
    if need(data, 0, 4) != b"MThd" or u32(data, 4) < 6:
        raise FormatError("Invalid MIDI header")
    fmt, tracks, division = struct.unpack(">HHH", need(data, 8, 6))
    if fmt not in (0, 1) or not tracks or not division:
        raise FormatError(f"Unsupported MIDI format {fmt} / track count / division")
    offset = 8 + u32(data, 4)
    events = []
    for track in range(tracks):
        if need(data, offset, 4) != b"MTrk":
            raise FormatError(f"Missing MIDI track {track}")
        size = u32(data, offset + 4)
        payload = need(data, offset + 8, size, "MIDI track")
        offset += 8 + size
        pos, tick, running, order = 0, 0, 0, 0
        while pos < len(payload):
            delta, pos = read_vlq(payload, pos)
            tick += delta
            status = need(payload, pos, 1, "MIDI event")[0]
            if status < 128:
                if not running:
                    raise FormatError(f"MIDI running status without status in track {track}")
                status = running
            else:
                pos += 1
            if status == 255:
                meta = need(payload, pos, 1)[0]
                length, pos = read_vlq(payload, pos + 1)
                event = Event(tick, track, order, status, need(payload, pos, length), meta)
                pos += length
            elif status in (240, 247):
                length, pos = read_vlq(payload, pos)
                event = Event(tick, track, order, status, need(payload, pos, length))
                pos += length
                running = 0
            elif 128 <= status < 240:
                running = status
                length = 1 if status >> 4 in (12, 13) else 2
                values = need(payload, pos, length, "MIDI channel message")
                if any(x > 127 for x in values):
                    raise FormatError(f"Invalid MIDI data byte in track {track}, offset {pos}")
                event = Event(tick, track, order, status, values)
                pos += length
            else:
                raise FormatError(f"Unsupported MIDI system event 0x{status:02x}")
            events.append(event)
            order += 1
            if len(events) > 2000000:
                raise FormatError("MIDI exceeds the two-million-event safety limit")
            if event.meta == 47:
                break
    return division, sorted(events, key=lambda e: (e.tick, e.track, e.order))


def midi_seconds(division: int, events: list[Event], tempo_factor: float = 1.0) -> float:
    if division & 32768:
        fps = -(division >> 8) + 256
        if fps not in (24, 25, 29, 30) or not division & 255:
            raise FormatError("Invalid SMPTE MIDI time division")
        fps = 30000 / 1001 if fps == 29 else fps
        return max((e.tick for e in events), default=0) / (fps * (division & 255)) / tempo_factor
    last, seconds, tempo = 0, 0.0, 500000
    for event in events:
        seconds += (event.tick - last) * tempo / (division * 1e6 * tempo_factor)
        last = event.tick
        if event.meta == 81:
            if len(event.data) != 3 or not int.from_bytes(event.data, "big"):
                raise FormatError("Invalid MIDI tempo event")
            tempo = int.from_bytes(event.data, "big")
    return seconds


def translate_midi(division: int, events: list[Event], song: Song
                   ) -> tuple[bytes, set[int], float, list[str]]:
    """Resolve Beatnik patch selection, including percussion, before synthesis.

    Each resource ID occupies a melodic TiMidity bank/program slot. Selecting
    a different patch before each drum note permits simultaneous drum voices
    without relying on TiMidity's different drum-bank conventions.
    """
    duration = midi_seconds(division, events, song.tempo)
    if duration > MAX_SECONDS:
        raise FormatError(f"Sequence exceeds the {MAX_SECONDS // 3600}-hour duration limit")
    banks, programs, modes = [0] * 16, [0] * 16, [0] * 16
    # BAE initializes channels from their first bank/program even when a file
    # places the first note before those messages at the same initial tick.
    for channel in range(16):
        for event in events:
            if event.status == 0xC0 + channel:
                programs[channel] = event.data[0]
                break
        for event in events:
            if event.status == 0xB0 + channel and event.data[0] == 0:
                banks[channel] = event.data[1] if event.data[1] <= 3 else 0
                break
    if song.percussion > 0:
        programs[9] = song.percussion
    nrpn_msb, nrpn_lsb = [-1] * 16, [-1] * 16
    current = [None] * 16
    used = set()
    warnings = []
    output = bytearray(b"\0\xff\x51\x03\x0f\x42\x40")  # 1,000,000 us/qn.
    last_output = 0
    seconds, previous_tick, tempo = 0.0, 0, 500000
    smpte_rate = None
    if division & 32768:
        fps = 256 - (division >> 8)
        smpte_rate = (30000 / 1001 if fps == 29 else fps) * (division & 255)

    def emit(tick: int, message: bytes) -> None:
        nonlocal last_output
        output.extend(vlq(tick - last_output) + message)
        last_output = tick

    for event in events:
        if smpte_rate:
            seconds = event.tick / smpte_rate / song.tempo
        else:
            seconds += (event.tick - previous_tick) * tempo / (division * 1e6 * song.tempo)
        previous_tick = event.tick
        tick = round(seconds * 1000)
        if event.status == 255:
            if event.meta == 81:
                tempo = int.from_bytes(event.data, "big")
            elif event.meta not in (47, 33):  # Ignore MIDI port switching.
                emit(tick, bytes((255, event.meta)) + vlq(len(event.data)) + event.data)
            continue
        if event.status in (240, 247):
            raise FormatError("MIDI SysEx is not supported by the Beatnik-to-TiMidity translation")
        channel = event.status & 15
        kind = event.status >> 4
        values = event.data
        if kind == 12:
            programs[channel] = values[0]
            continue
        if kind == 11:
            controller, value = values
            if controller == 0:
                banks[channel] = value if value <= 3 else 0
                continue
            if controller == 32:
                continue
            if controller == 99:
                nrpn_msb[channel] = value
                continue
            if controller == 98:
                nrpn_lsb[channel] = value
                continue
            if controller in (100, 101):
                nrpn_msb[channel] = nrpn_lsb[channel] = -1
            if controller == 6 and nrpn_msb[channel] >= 0:
                if (nrpn_msb[channel], nrpn_lsb[channel]) == (5, 0) and value <= 3:
                    modes[channel] = value
                elif (nrpn_msb[channel], nrpn_lsb[channel]) == (4, 0):
                    warnings.append("Beatnik velocity-curve selection is approximated by TiMidity")
                # Other Beatnik NRPNs are not implemented by the source engine.
                nrpn_msb[channel] = nrpn_lsb[channel] = -1
                continue
            if controller == 121:
                nrpn_msb[channel] = nrpn_lsb[channel] = -1
            emit(tick, bytes((event.status,)) + values)
            continue
        if kind in (8, 9, 10):
            note = values[0]
            if channel != 9:
                note = max(0, min(127, note + song.pitch))
            if kind == 9 and values[1]:
                mode = modes[channel]
                percussion_bank = mode in (1, 2) or (mode == 0 and channel == 9)
                select_by_note = mode == 2 or (mode == 0 and channel == 9)
                patch = note if select_by_note else programs[channel]
                bank = banks[channel] * 2 + int(percussion_bank)
                iid = bank * 128 + patch if bank < 6 else patch
                if song.percussion >= 0:
                    iid = programs[channel]
                iid = song.remaps.get(iid, iid)
                if not 0 <= iid < 8192:
                    raise FormatError(f"Instrument ID {iid} cannot be mapped to a MIDI bank")
                used.add(iid)
                if current[channel] != iid:
                    emit(tick, bytes((0xB0 + channel, 0, 64 + iid // 128)))
                    emit(tick, bytes((0xB0 + channel, 32, 0)))
                    emit(tick, bytes((0xC0 + channel, iid % 128)))
                    current[channel] = iid
                velocity = values[1]
                if song.velocity:
                    warnings.append("Custom SONG VELC curve is not reproduced by TiMidity")
                emit(tick, bytes((event.status, note, velocity)))
            else:
                emit(tick, bytes((event.status, note, values[1])))
        else:
            emit(tick, bytes((event.status,)) + values)
    end_tick = max(last_output, round(duration * 1000))
    # TiMidity discards the delta before End Of Track when no later channel
    # event exists. A timed release preserves RMF one-shots with no Note Off.
    for channel in range(16):
        if current[channel] is not None:
            emit(end_tick, bytes((0xB0 + channel, 123, 0)))
    emit(end_tick, b"\xff\x2f\0")
    midi = b"MThd" + struct.pack(">IHHH", 6, 0, 1, 1000)
    midi += b"MTrk" + struct.pack(">I", len(output)) + output
    return midi, used, duration, sorted(set(warnings))


def locate_eaw() -> Path:
    candidates = [Path.cwd() / "eaw", Path(__file__).resolve().parent / "eaw"]
    for candidate in candidates:
        if (candidate / "gravis.cfg").is_file():
            return candidate.resolve()
    raise FormatError("Cannot find eaw/gravis.cfg beside the script or in the current directory")


def eaw_patches(directory: Path) -> dict[int, list[str]]:
    patches = {}
    bank = None
    for line in (directory / "gravis.cfg").read_text(encoding="latin1").splitlines():
        words = shlex.split(line, comments=True)
        if not words:
            continue
        if words[0] in ("bank", "drumset"):
            bank = (0 if words[0] == "bank" else 128) if words[1] == "0" else None
        elif bank is not None and words[0].isdigit() and len(words) >= 2:
            note = int(words[0])
            patch = directory / words[1]
            if patch.suffix != ".pat":
                patch = patch.with_suffix(".pat")
            if not patch.is_file():
                raise FormatError(f"EAW patch does not exist: {patch}")
            options = words[2:]
            if bank == 128:
                if not any(x.startswith("note=") for x in options):
                    options.append(f"note={note}")
                if "keep=loop" not in options and "strip=loop" not in options:
                    options.append("strip=loop")
                if "keep=env" not in options and "strip=env" not in options:
                    options.append("strip=env")
            patches[bank + note] = [str(patch)] + options
    return patches


def quote_config(value: str) -> str:
    if any(c in value for c in '\n\r\0"'):
        raise FormatError("TiMidity configuration paths cannot contain quotes or newlines")
    return '"' + value + '"'


def prepare_bank(resources: list[Resource], used: set[int], temporary: Path
                 ) -> tuple[Path, list[str]]:
    instrument_resources = {r.id: r for r in resources if r.kind == b"INST"}
    instruments = {}
    samples = {}
    warnings = []
    for iid in sorted(used & instrument_resources.keys()):
        instrument = parse_instrument(instrument_resources[iid])
        instruments[iid] = instrument
        if instrument.extra_units:
            warnings.append("Embedded instrument LFOs, modulation curves, and filters are not reproduced")
        if any(x[2] in (b"GOTO", b"GOST", b"RELS") for x in instrument.envelope):
            warnings.append("Complex Beatnik envelopes are approximated with SoundFont ADSR")
        for zone in instrument.zones:
            if zone.sample_id not in samples:
                sample_resource = find_resource(resources, SOUND_TYPES, zone.sample_id)
                sample = decode_sample(sample_resource)
                # Preserve the signed reference used as a dictionary key.
                sample.id = zone.sample_id
                samples[zone.sample_id] = sample
    font = temporary / "embedded.sf2"
    if instruments:
        write_soundfont(font, instruments, samples)
    patches = eaw_patches(locate_eaw()) if used - instruments.keys() else {}
    cfg = ["# Vibe coded by Codex", "# Generated RMF instrument mappings", "progbase 0"]
    substitutes = []
    missing_drums = []
    for iid in sorted(used):
        cfg.append(f"bank {64 + iid // 128}")
        if iid in instruments:
            gain = min(800, round(100 * instrument_gain(instruments[iid])))
            cfg.append(f"{iid % 128} %font {quote_config(str(font))} {iid // 128} {iid % 128} amp={gain}")
        else:
            fallback = iid % 256
            if iid >= 256:
                substitutes.append(iid)
            if fallback not in patches:
                # Undefined low/high GM drum notes have no EAW equivalent.
                # Use a silent patch, never an unrelated piano or drum.
                blank = locate_eaw() / "blank.pat"
                if not blank.is_file():
                    raise FormatError(f"No EAW patch for instrument {iid}")
                entry = [str(blank), "amp=0"]
                missing_drums.append(iid)
            else:
                entry = patches[fallback]
            cfg.append(f"{iid % 128} {quote_config(entry[0])} " + " ".join(entry[1:]))
    if substitutes:
        warnings.append("Using EAW General MIDI substitutes for unavailable Beatnik bank instruments: "
                        + ", ".join(map(str, substitutes)))
    if missing_drums:
        warnings.append("No EAW equivalent for these undefined GM drum notes; rendered silent: "
                        + ", ".join(map(str, missing_drums)))
    config = temporary / "timidity.cfg"
    config.write_text("\n".join(cfg) + "\n", encoding="utf-8")
    return config, sorted(set(warnings))


def safe_name(title: str) -> str:
    title = unicodedata.normalize("NFC", title)
    title = "".join("_" if c in '/\\:*?"<>|' or unicodedata.category(c).startswith("C")
                    else c for c in title)
    title = re.sub(r"\s+", " ", title).strip(" .")
    if title in ("", ".", ".."):
        return "out"
    # Leave space for .wav and a collision suffix on common filesystems.
    while len(title.encode("utf-8")) > 200:
        title = title[:-1]
    if title.split(".")[0].upper() in {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)),
                                      *(f"LPT{i}" for i in range(1, 10))}:
        title = "_" + title
    return title


def write_silence(path: Path, duration: float) -> None:
    frames = max(1, round(duration * 44100))
    with wave.open(str(path), "wb") as output:
        output.setparams((2, 2, 44100, 0, "NONE", "not compressed"))
        silence = b"\0" * (44100 * 4)
        while frames:
            count = min(frames, 44100)
            output.writeframesraw(silence[:count * 4])
            frames -= count


def clipped_wav(path: Path) -> bool:
    with wave.open(str(path), "rb") as audio:
        while data := audio.readframes(65536):
            values = array("h")
            values.frombytes(data)
            if sys.byteorder != "little":
                values.byteswap()
            if min(values, default=0) <= -32768 or max(values, default=0) >= 32767:
                return True
    return False


def preserve_end_silence(path: Path, minimum_frames: int) -> None:
    """TiMidity may trim silent events after the last sounding voice."""
    with wave.open(str(path), "rb") as source:
        if source.getnframes() >= minimum_frames:
            return
        padded = path.with_suffix(".padded.wav")
        with wave.open(str(padded), "wb") as output:
            output.setparams(source.getparams())
            while block := source.readframes(65536):
                output.writeframesraw(block)
            remaining = minimum_frames - source.getnframes()
            zeroes = b"\0" * 262144
            while remaining:
                count = min(remaining, 65536)
                output.writeframesraw(zeroes[:count * 4])
                remaining -= count
    os.replace(padded, path)


def publish_wav(source: Path, output_dir: Path, title: str) -> Path:
    stem = safe_name(title)
    # The temporary directory is inside outputDir, so link is atomic and never
    # overwrites an existing file (including symlinks).
    suffix = 1
    while True:
        name = f"{stem}.wav" if suffix == 1 else f"{stem}-{suffix}.wav"
        target = output_dir / name
        try:
            os.link(source, target)
            return target
        except FileExistsError:
            suffix += 1


def convert(input_file: Path, output_dir: Path) -> tuple[Path, list[str]]:
    input_file = input_file.resolve(strict=True)
    output_dir = output_dir.resolve(strict=True)
    if not input_file.is_file():
        raise FormatError("inputFile must be a regular file")
    if not output_dir.is_dir():
        raise FormatError("outputDir must be an existing directory")
    resources = read_resources(input_file)
    songs = [r for r in resources if r.kind == b"SONG"]
    if len(songs) > 1:
        raise FormatError(f"File contains {len(songs)} SONG resources; a soundbank is not a single song")
    if not songs:
        raise FormatError("No SONG resource; this is not a playable RMF song")
    song = parse_song(songs[0])
    if song.kind == 2:
        raise FormatError("Linear RMF SONG type 2 is documented but not supported by this converter")
    source_midi = midi_bytes(find_resource(resources, MIDI_TYPES, song.id))
    division, events = parse_midi(source_midi)
    if not song.title:
        # SMF sequence-name metadata belongs to the first track, not every
        # track-name event, which may simply say 'Bass' or 'Drums'.
        song.title = next((text(e.data) for e in events if e.meta == 3 and e.track == 0), "")
    midi, used, duration, warnings = translate_midi(division, events, song)
    with tempfile.TemporaryDirectory(prefix=".rmf-", dir=output_dir) as temporary_name:
        temporary = Path(temporary_name)
        rendered = temporary / "render.wav"
        if not used:
            write_silence(rendered, duration)
        else:
            config, bank_warnings = prepare_bank(resources, used, temporary)
            warnings.extend(bank_warnings)
            midi_path = temporary / "sequence.mid"
            midi_path.write_bytes(midi)
            timidity = shutil.which("timidity")
            if not timidity:
                raise FormatError("TiMidity++ is required (the 'timidity' program)")
            amplification = min(800, max(1, round(70 * song.volume / 127)))
            # Explicit channel numbers work consistently across TiMidity builds;
            # the installed build treats -D 0 differently from its man page.
            drum_options = [value for ch in range(1, 17) for value in ("-D", str(-ch))]
            while True:
                run([timidity, "-c", str(config), *drum_options, "-Ow1S", "-s", "44100",
                     "-A", str(amplification), "-p", "256", "--preserve-silence",
                     "--reverb=" + ("d" if not song.reverb else "n"), "--chorus=n", "-o", str(rendered),
                     str(midi_path)], timeout=600)
                if not clipped_wav(rendered) or amplification <= 1:
                    break
                amplification = max(1, amplification // 2)
        try:
            with wave.open(str(rendered), "rb") as check:
                if check.getnchannels() != 2 or check.getsampwidth() != 2 or check.getframerate() != 44100:
                    raise FormatError("Renderer did not produce 44.1 kHz stereo 16-bit PCM")
                if not check.getnframes():
                    raise FormatError("Renderer produced an empty WAV")
        except (wave.Error, EOFError) as error:
            raise FormatError(f"Invalid output WAV: {error}") from error
        preserve_end_silence(rendered, max(1, round(duration * 44100)))
        result = publish_wav(rendered, output_dir, song.title)
    return result, sorted(set(warnings))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("inputFile", type=Path, help="Beatnik .rmf input file")
    parser.add_argument("outputDir", type=Path, help="pre-existing directory for the WAV")
    args = parser.parse_args()
    try:
        output, warnings = convert(args.inputFile, args.outputDir)
    except (FormatError, OSError, ValueError, struct.error) as error:
        print(f"richMusicFormat: {error}", file=sys.stderr)
        return 1
    for warning in warnings:
        print(f"Warning: {warning}", file=sys.stderr)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

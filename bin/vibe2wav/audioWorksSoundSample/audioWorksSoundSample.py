#!/usr/bin/env python3
# Vibe coded by Codex
"""Decode Computer Concepts AudioWorks Sound Sample files, using only stdlib.

Usage: audioWorksSoundSample.py inputFile outputDir [-verbose]
See audioWorksSoundSample.txt for the format, recovery rules and limitations.
"""

from __future__ import annotations

import argparse
from array import array
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
import tempfile


MAGIC = b"\xc5\xc6\xcb\xc3"
KNOWN_CHUNKS = {b"SND_HEAD", b"SND_INFO", b"SND_CHAN", b"SND_LOOP"}
ENCODINGS = {0: "VIDC logarithmic", 1: "unsigned linear PCM",
             2: "signed linear PCM", 3: "mu-law (AudioWorks playback curve)"}


class FormatError(ValueError):
    """No files should be written if parsing raises this exception."""

    def __init__(self, message: str, *, recognized: bool = False):
        super().__init__(message)
        self.recognized = recognized


@dataclass
class Chunk:
    slot: int
    tag: bytes
    offset: int
    size: int
    payload: bytes


@dataclass
class Track:
    channel_ids: tuple[int, ...]
    pcm: bytes
    frames: int


@dataclass
class Sound:
    rate: int
    tracks: list[Track]
    metadata: dict
    warnings: list[str]


def vidc_sample(code: int) -> int:
    """AudioWorks/AudioManager's exact 16-bit VIDC expansion, including +/-0."""
    exponent = code >> 5
    mantissa = (code >> 1) & 15
    magnitude = (((16 + mantissa) << exponent) - 16) * 8
    return -magnitude if code & 1 else magnitude


VIDC = tuple(vidc_sample(i) for i in range(256))
# The original editor rotates/complements mu-law into its VIDC lookup table.
# Its reconstruction levels differ slightly from the usual G.711 decoder.
MULAW = tuple(VIDC[(((i << 1) | (i >> 7)) & 255) ^ 255] for i in range(256))


def decode_pcm(payload: bytes, encoding: int, bits: int) -> tuple[array, bytes, int]:
    """Return signed 16-bit samples, discarded bytes and unused low nibble.

    The nibble is -1 unless a final complete 12-bit sample shares a byte with
    four bits of a truncated next sample. No missing bits are fabricated.
    """
    samples = array("h")
    unused_nibble = -1
    if bits == 8:
        if encoding in (0, 3):
            table = VIDC if encoding == 0 else MULAW
            samples.extend(table[b] for b in payload)
        elif encoding == 1:
            samples.extend((b - 128) * 256 for b in payload)
        else:
            samples.extend((b if b < 128 else b - 256) * 256 for b in payload)
        return samples, b"", unused_nibble
    if bits == 16:
        complete = len(payload) & ~1
        samples.frombytes(payload[:complete])
        if sys.byteorder != "big":
            samples.byteswap()
        if encoding == 1:
            samples = array("h", ((s & 65535) - 32768 for s in samples))
        return samples, payload[complete:], unused_nibble
    complete = len(payload) // 3 * 3
    for i in range(0, complete, 3):
        a, b, c = payload[i:i + 3]
        x, y = (a << 4) | (b >> 4), ((b & 15) << 8) | c
        if encoding == 1:
            x, y = x - 2048, y - 2048
        else:
            x = x if x < 2048 else x - 4096
            y = y if y < 2048 else y - 4096
        samples.extend((x * 16, y * 16))
    remainder = payload[complete:]
    if len(remainder) == 2:
        x = (remainder[0] << 4) | (remainder[1] >> 4)
        x = x - 2048 if encoding == 1 else (x if x < 2048 else x - 4096)
        samples.append(x * 16)
        unused_nibble = remainder[1] & 15
        remainder = b""
    return samples, remainder, unused_nibble


def _little_endian(samples: array) -> bytes:
    copy = array("h", samples)
    if sys.byteorder != "little":
        copy.byteswap()
    return copy.tobytes()


def _coverage(data: bytes, directory_end: int, chunks: list[Chunk]) -> tuple[list, list]:
    """Describe every unreferenced byte and every overlap, without scanning data."""
    spans = [(0, min(directory_end, len(data)), "directory")]
    spans.extend((c.offset, c.offset + len(c.payload), f"slot {c.slot} {c.tag.decode('ascii', 'replace')}")
                 for c in chunks if c.payload)
    gaps, overlaps = [], []
    end = 0
    previous = ""
    for start, stop, label in sorted(spans):
        if start > end:
            gaps.append({"offset": end, "length": start - end,
                         "raw_hex": data[end:start].hex(), "kind": "unreferenced gap"})
        elif start < end:
            overlaps.append({"offset": start, "length": min(stop, end) - start,
                             "regions": [previous, label]})
        if stop > end:
            end, previous = stop, label
    if end < len(data):
        gaps.append({"offset": end, "length": len(data) - end,
                     "raw_hex": data[end:].hex(), "kind": "unreferenced suffix"})
    return gaps, overlaps


def _parse_loops(chunk: Chunk, warnings: list[str]) -> dict:
    raw = chunk.payload
    records = []
    pos = 0
    terminated = False
    while pos + 4 <= len(raw):
        start = struct.unpack_from("<I", raw, pos)[0]
        if start == 0xffffffff:
            pos += 4
            terminated = True
            break
        if pos + 16 > len(raw):
            break
        start, length, auxiliary, control = struct.unpack_from("<4I", raw, pos)
        records.append({"start": start, "length": length, "auxiliary": auxiliary,
                        "control": control, "repeat_selector": control & 255})
        pos += 16
    if not terminated:
        warnings.append(f"SND_LOOP slot {chunk.slot}: missing complete terminator; retaining raw metadata")
    if pos < len(raw):
        warnings.append(f"SND_LOOP slot {chunk.slot}: {len(raw) - pos} bytes after parsed records/terminator")
    return {"slot": chunk.slot, "records": records, "terminated": terminated,
            "tail_hex": raw[pos:].hex()}


def parse(data: bytes) -> Sound:
    """Parse and decode fully in memory; this function never creates files."""
    if len(data) < 12 or data[:4] != MAGIC:
        raise FormatError("not an AudioWorks chunk file: missing complete chunk-file header")
    maximum, declared_used = struct.unpack_from("<II", data, 4)
    available_slots = (len(data) - 12) // 16
    entries = [struct.unpack_from("<8sII", data, 12 + i * 16)
               for i in range(min(maximum, available_slots))]
    active_tags = {tag for tag, offset, _ in entries if offset}
    # Chunk-file magic alone also identifies unrelated object and envelope files.
    if b"SND_HEAD" not in active_tags or b"SND_CHAN" not in active_tags:
        raise FormatError("not an identifiable AudioWorks sample: active SND_HEAD and SND_CHAN required")

    def fail(message: str) -> None:
        raise FormatError(message, recognized=True)

    if maximum > available_slots:
        fail("truncated chunk directory; declared chunk locations cannot be trusted")
    directory_end = 12 + 16 * maximum
    warnings: list[str] = []
    chunks = []
    directory = []
    for slot, (tag, offset, size) in enumerate(entries):
        record = {"slot": slot, "tag_hex": tag.hex(), "offset": offset, "size": size,
                  "active": bool(offset)}
        directory.append(record)
        if not offset:
            # An inactive slot's ID and size are undefined and may contain heap residue.
            continue
        if offset < directory_end:
            fail(f"slot {slot}: chunk overlaps the directory; ambiguous structure")
        if offset > len(data):
            warnings.append(f"slot {slot}: chunk begins beyond EOF; no bytes available")
            payload = b""
        else:
            payload = data[offset:min(offset + size, len(data))]
        if len(payload) != size:
            warnings.append(f"slot {slot}: truncated chunk, {len(payload)} of {size} bytes available")
        if tag not in KNOWN_CHUNKS:
            fail(f"unsupported active chunk {tag!r}; refusing an unknown AudioWorks extension")
        chunks.append(Chunk(slot, tag, offset, size, payload))
    if len(chunks) != declared_used:
        warnings.append(f"directory says {declared_used} active chunks, but {len(chunks)} offsets are nonzero")
    headers = [c for c in chunks if c.tag == b"SND_HEAD"]
    if len(headers) != 1:
        fail("exactly one active SND_HEAD is required")
    head = headers[0]
    if head.size != 9 or len(head.payload) != 9:
        fail("SND_HEAD must contain exactly nine bytes; no rate/encoding guesses are made")
    rate, encoding, bits, channels, auxiliary, flags = struct.unpack("<I5B", head.payload)
    if not rate:
        fail("zero sample rate; playback timing is undefined")
    if encoding not in ENCODINGS:
        fail(f"unsupported sample encoding {encoding}")
    if bits not in (8, 12, 16):
        fail(f"unsupported/invalid precision {bits} bits per sample; intended precision cannot be established")
    if encoding in (0, 3) and bits != 8:
        fail(f"{ENCODINGS[encoding]} requires 8 bits per sample")
    if channels not in (1, 2):
        fail(f"unsupported channel count {channels}; only mono and stereo are established")
    if auxiliary:
        fail(f"unsupported nonzero SND_HEAD auxiliary byte {auxiliary}")
    if flags & ~1:
        fail(f"unsupported SND_HEAD flags 0x{flags:02x}")
    if rate * channels * 2 > 0xffffffff:
        fail("sample rate cannot be represented by a PCM RIFF/WAVE byte rate")

    # The standard directory explicitly owns bytes; neither alignment nor EOF
    # is used to enlarge a chunk or locate audio.
    covered = [c for c in chunks if c.offset <= len(data)]
    gaps, overlaps = _coverage(data, directory_end, covered)
    for overlap in overlaps:
        warnings.append(f"overlapping declared ranges at {overlap['offset']} ({overlap['length']} bytes): "
                        + " / ".join(overlap["regions"]))
    for gap in gaps:
        # Three or fewer unreferenced bytes up to an aligned chunk are ordinary
        # padding. They are still retained verbatim, including nonzero bytes.
        is_alignment = (gap["kind"] == "unreferenced gap" and gap["length"] <= 3
                        and (gap["offset"] + gap["length"]) % 4 == 0)
        if is_alignment:
            gap["kind"] = "unreferenced alignment space"
        else:
            warnings.append(f"{gap['length']} unreferenced bytes at offset {gap['offset']}; excluded from audio")
    channel_chunks = [c for c in chunks if c.tag == b"SND_CHAN"]
    for i, a in enumerate(channel_chunks):
        for b in channel_chunks[i + 1:]:
            if max(a.offset, b.offset) < min(a.offset + len(a.payload), b.offset + len(b.payload)):
                fail("overlapping audio chunks; channel ownership is ambiguous")
        if max(a.offset, head.offset) < min(a.offset + len(a.payload), head.offset + 9):
            fail("audio overlaps SND_HEAD; ambiguous sample parameters")
    if channels == 2 and flags & 1 and len(channel_chunks) != 1:
        fail("interleaved stereo requires exactly one SND_CHAN")

    metadata = {"format": "AudioWorks Sound Sample", "metadata_version": 1,
                "source_size": len(data), "source_sha256": hashlib.sha256(data).hexdigest(),
                "directory_header_hex": data[:12].hex(), "directory": directory,
                "header": {"rate": rate, "encoding": encoding, "encoding_name": ENCODINGS[encoding],
                           "bits": bits, "channels": channels, "auxiliary": auxiliary, "flags": flags},
                "non_audio_chunks": [{"slot": c.slot, "tag": c.tag.decode("ascii"), "offset": c.offset,
                                      "declared_size": c.size, "raw_hex": c.payload.hex()}
                                     for c in chunks if c.tag != b"SND_CHAN"],
                "unreferenced_regions": gaps, "overlaps": overlaps, "channels": [], "loops": []}
    for chunk in chunks:
        if chunk.tag == b"SND_LOOP":
            metadata["loops"].append(_parse_loops(chunk, warnings))
        if chunk.tag == b"SND_INFO" and b"\0" not in chunk.payload:
            warnings.append(f"SND_INFO slot {chunk.slot}: missing NUL terminator; retained verbatim")
    decoded: dict[int, array] = {}
    for chunk in channel_chunks:
        if not chunk.payload:
            warnings.append(f"SND_CHAN slot {chunk.slot}: missing channel byte; no audio recovered")
            continue
        channel_id = chunk.payload[0]
        payload = chunk.payload[1:]
        channel_meta = {"slot": chunk.slot, "offset": chunk.offset, "declared_size": chunk.size,
                        "available_size": len(chunk.payload), "channel_byte": channel_id,
                        "encoded_audio_bytes": len(payload), "streams": []}
        metadata["channels"].append(channel_meta)
        if channels == 2 and flags & 1:
            if channel_id != 0:
                warnings.append(f"slot {chunk.slot}: interleaved stereo channel byte is {channel_id}, expected 0; "
                                "using the explicit header layout")
            # Eight samples take exactly 'bits' bytes, even for packed 12-bit.
            blocks = [bytearray(), bytearray()]
            for start in range(0, len(payload), bits * 2):
                blocks[0].extend(payload[start:start + bits])
                blocks[1].extend(payload[start + bits:start + bits * 2])
            streams = [(1, bytes(blocks[0])), (2, bytes(blocks[1]))]
            if len(payload) % (bits * 2):
                warnings.append(f"slot {chunk.slot}: incomplete final eight-sample stereo block; retaining available samples")
        else:
            if channels == 1:
                effective_id = 1
                if channel_id not in (0, 1):
                    warnings.append(f"slot {chunk.slot}: invalid mono channel byte {channel_id}; "
                                    "following the native reader: consume it as the channel byte and use channel 1. "
                                    "If the writer omitted this byte, the first audio sample cannot be distinguished from it")
            elif channel_id in (1, 2):
                effective_id = channel_id
            else:
                fail(f"slot {chunk.slot}: invalid separate-stereo channel identifier {channel_id}")
            streams = [(effective_id, payload)]
        for identifier, stream in streams:
            if identifier in decoded:
                fail(f"duplicate channel {identifier}; not a defined multi-sample archive")
            pcm, discarded, nibble = decode_pcm(stream, encoding, bits)
            stream_meta = {"channel": identifier, "samples": len(pcm),
                           "discarded_tail_hex": discarded.hex(), "unused_low_nibble": nibble}
            channel_meta["streams"].append(stream_meta)
            if discarded or nibble != -1:
                warnings.append(f"channel {identifier}: incomplete final {bits}-bit sample; "
                                "only complete samples decoded, residual bits retained in WAV metadata")
            decoded[identifier] = pcm
    populated = {key: value for key, value in decoded.items() if value}
    if not populated:
        fail("no complete audio samples can be recovered")
    if len(populated) != channels:
        warnings.append(f"only {len(populated)} of {channels} channels have complete samples; exporting available channels separately")
    tracks = []
    if set(populated) == {1, 2} and len(populated[1]) == len(populated[2]):
        left, right = populated[1], populated[2]
        interleaved = array("h", [0]) * (len(left) * 2)
        interleaved[0::2], interleaved[1::2] = left, right
        tracks.append(Track((1, 2), _little_endian(interleaved), len(left)))
    else:
        if len(populated) > 1:
            warnings.append("channel lengths differ; exporting separate mono WAVs without padding or discarding samples")
        for identifier, pcm in sorted(populated.items()):
            tracks.append(Track((identifier,), _little_endian(pcm), len(pcm)))
    # Check loop ranges against the actual decoded frames, not encoded byte counts.
    for loop in metadata["loops"]:
        for i, record in enumerate(loop["records"]):
            end = record["start"] + record["length"]
            if record["length"] >= 0x80000000 or end > max(t.frames for t in tracks):
                action = ("loop end clamped to available audio" if record["repeat_selector"] == 0
                          and 0 < record["length"] < 0x80000000
                          and record["start"] < max(t.frames for t in tracks)
                          else "omitted from playable WAV loops")
                warnings.append(f"SND_LOOP slot {loop['slot']} record {i}: range exceeds decoded audio; "
                                f"retained as source metadata, {action}")
    metadata["warnings"] = warnings
    metadata["output_tracks"] = [{"channel_ids": list(t.channel_ids), "frames": t.frames,
                                  "pcm_sha256": hashlib.sha256(t.pcm).hexdigest()} for t in tracks]
    return Sound(rate, tracks, metadata, warnings)


def _riff_chunk(tag: bytes, payload: bytes) -> bytes:
    if len(payload) > 0xffffffff:
        raise FormatError("output chunk exceeds the RIFF/WAVE size limit", recognized=True)
    return tag + struct.pack("<I", len(payload)) + payload + (b"\0" if len(payload) & 1 else b"")


def make_wav(sound: Sound, track: Track) -> bytes:
    """PCM audio plus standard loop markers and lossless source metadata."""
    channels = len(track.channel_ids)
    fmt = struct.pack("<HHIIHH", 1, channels, sound.rate, sound.rate * channels * 2, channels * 2, 16)
    chunks = [_riff_chunk(b"fmt ", fmt), _riff_chunk(b"data", track.pcm)]
    loops = []
    for group in sound.metadata["loops"]:
        # The native reader only examines the first three loop records.
        for record in group["records"][:3]:
            end = record["start"] + record["length"]
            if (record["repeat_selector"] == 0 and 0 < record["length"] < 0x80000000
                    and record["start"] < track.frames):
                loops.append((record["start"], min(end, track.frames) - 1))
    if loops:
        # smpl loop end is inclusive, unlike start+length in AudioWorks.
        sample_period = min(0xffffffff, (1_000_000_000 + sound.rate // 2) // sound.rate)
        smpl = struct.pack("<9I", 0, 0, sample_period, 60, 0, 0, 0, len(loops), 0)
        smpl += b"".join(struct.pack("<6I", i, 0, start, end, 0, 0)
                         for i, (start, end) in enumerate(loops))
        chunks.append(_riff_chunk(b"smpl", smpl))
    # No sidecar is needed to preserve unused slots, ignored loop words,
    # metadata overlaps, alignment bytes, or malformed source suffixes.
    archive = json.dumps(sound.metadata, ensure_ascii=True, separators=(",", ":")).encode("utf-8")
    chunks.append(_riff_chunk(b"awss", archive))
    body = b"WAVE" + b"".join(chunks)
    if len(body) > 0xffffffff:
        raise FormatError("output exceeds the RIFF/WAVE size limit", recognized=True)
    return b"RIFF" + struct.pack("<I", len(body)) + body


def _make_output_dir(path: Path) -> None:
    missing = []
    current = path
    while not current.exists():
        missing.append(current)
        current = current.parent
    path.mkdir(parents=True, exist_ok=True)
    for directory in missing:
        directory.chmod(directory.stat().st_mode | 0o770)


def _atomic_write(path: Path, data: bytes) -> None:
    fd, temporary = tempfile.mkstemp(prefix=".audioworks-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fchmod(stream.fileno(), 0o664)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def convert(input_file: str | Path, output_dir: str | Path, verbose: bool = False) -> tuple[Sound, list[Path]]:
    source, destination = Path(input_file), Path(output_dir)
    sound = parse(source.read_bytes())
    prepared = []
    paths = []
    for track in sound.tracks:
        suffix = "" if len(sound.tracks) == 1 else f".channel-{track.channel_ids[0]}"
        output = destination / (source.name + suffix + ".wav")
        if output.resolve() == source.resolve():
            raise OSError("output path would overwrite the input file")
        prepared.append((output, make_wav(sound, track)))
        paths.append(output)
    if verbose:
        detail = json.dumps(sound.metadata, indent=2, ensure_ascii=True) + "\n"
        prepared.append((destination / (source.name + ".json"), detail.encode("utf-8")))
    # Identification, all decoding and all RIFF construction precede disk writes.
    # Rejection therefore leaves even a nonexistent output directory nonexistent.
    _make_output_dir(destination)
    for output, payload in prepared:
        _atomic_write(output, payload)
    return sound, paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputDir", type=Path)
    parser.add_argument("-verbose", "--verbose", action="store_true", help="also write a JSON byte/metadata audit")
    args = parser.parse_args(argv)
    try:
        sound, outputs = convert(args.inputFile, args.outputDir, args.verbose)
    except FormatError as error:
        category = "AudioWorks input cannot be decoded" if error.recognized else "Unsupported input"
        print(f"{category}: {error}", file=sys.stderr)
        return 2
    except (OSError, OverflowError) as error:
        print(f"Conversion failed: {error}", file=sys.stderr)
        return 1
    for warning in sound.warnings:
        print(f"Warning: {warning}", file=sys.stderr)
    for output in outputs:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

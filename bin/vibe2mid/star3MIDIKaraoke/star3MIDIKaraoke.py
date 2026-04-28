#!/usr/bin/env python3
# Vibe coded by Codex
"""Convert supported Star 3 MIDI Karaoke files to Standard MIDI files."""

from __future__ import annotations

import os
import struct
import sys
from dataclasses import dataclass
from pathlib import Path


class Star3Error(Exception):
    pass


STAR3_XOR_KEY = bytes.fromhex(
    "cb 78 16 22 4f 8c 7b e8 91 32 9c 68 b4 a7 5e 14 50 e6 98 bd 44 0a 98 08"
)

STAR3_V300_XOR_KEY = bytes.fromhex(
    "ee 7a 16 2b 7c 44 70 5d 1c 20 fe fb ea 7a f1 ad 84 a4 c2 2f"
)


@dataclass(frozen=True)
class CEventHeader:
    offset: int
    reserved0: int
    prefix_length_field: int
    division: int
    track_count: int
    melody_track: int
    second_track_hint: int
    unpacked_length: int
    stored_length: int
    lyrics_offset: int


def read_vlq(data: bytes, pos: int, end: int) -> tuple[int, int]:
    value = 0
    for _ in range(4):
        if pos >= end:
            raise Star3Error("truncated variable-length integer")
        byte = data[pos]
        pos += 1
        value = (value << 7) | (byte & 0x7F)
        if (byte & 0x80) == 0:
            return value, pos
    raise Star3Error("oversized variable-length integer")


def write_vlq(value: int) -> bytes:
    if value < 0:
        raise Star3Error("negative MIDI delta")
    out = [value & 0x7F]
    value >>= 7
    while value:
        out.append((value & 0x7F) | 0x80)
        value >>= 7
    return bytes(reversed(out))


def decompress_lzss_xor(data: bytes, expected_length: int, key: bytes) -> bytes:
    encrypted = bytes(byte ^ key[index % len(key)]
                      for index, byte in enumerate(data))
    window = bytearray(4096)
    window_pos = 0xFEE
    flags = 0
    source_pos = 0
    output = bytearray()

    while len(output) < expected_length:
        flags >>= 1
        if (flags & 0x100) == 0:
            if source_pos >= len(encrypted):
                raise Star3Error("truncated compressed CEVENT flags")
            flags = encrypted[source_pos] | 0xFF00
            source_pos += 1

        if flags & 1:
            if source_pos >= len(encrypted):
                raise Star3Error("truncated compressed CEVENT literal")
            value = encrypted[source_pos]
            source_pos += 1
            output.append(value)
            window[window_pos] = value
            window_pos = (window_pos + 1) & 0xFFF
            continue

        if source_pos + 2 > len(encrypted):
            raise Star3Error("truncated compressed CEVENT reference")
        low = encrypted[source_pos]
        high = encrypted[source_pos + 1]
        source_pos += 2
        offset = low | ((high & 0xF0) << 4)
        length = (high & 0x0F) + 3
        for index in range(length):
            value = window[(offset + index) & 0xFFF]
            output.append(value)
            window[window_pos] = value
            window_pos = (window_pos + 1) & 0xFFF
            if len(output) == expected_length:
                break

    if source_pos != len(encrypted):
        raise Star3Error("compressed stream has trailing bytes")
    return bytes(output)


def midi_event_data_length(status: int) -> int:
    high = status & 0xF0
    if high in (0xC0, 0xD0):
        return 1
    if high in (0x80, 0x90, 0xA0, 0xB0, 0xE0):
        return 2
    raise Star3Error(f"unsupported MIDI status 0x{status:02x}")


def parse_star3_event(data: bytes, pos: int, end: int):
    start = pos
    delta, pos = read_vlq(data, pos, end)
    duration, pos = read_vlq(data, pos, end)
    if pos >= end:
        raise Star3Error("truncated Star3 event opcode")
    opcode = data[pos]
    pos += 1

    if opcode == 0x00:
        if pos >= end:
            raise Star3Error("truncated MIDI event")
        status = data[pos]
        if status < 0x80:
            raise Star3Error("running status is not used in Star3 event streams")
        need = 1 + midi_event_data_length(status)
        if pos + need > end:
            raise Star3Error("truncated MIDI event payload")
        payload = data[pos:pos + need]
        return pos + need, ("midi", delta, duration, payload, start)

    if opcode == 0x01:
        if pos + 4 > end:
            raise Star3Error("truncated time-signature event")
        payload = data[pos:pos + 4]
        return pos + 4, ("time_signature", delta, duration, payload, start)

    if opcode == 0x02:
        if pos + 3 > end:
            raise Star3Error("truncated tempo event")
        tempo = int.from_bytes(data[pos:pos + 3], "little")
        return pos + 3, ("tempo", delta, duration, tempo, start)

    if opcode == 0x03:
        if pos + 2 > end:
            raise Star3Error("truncated key-signature event")
        payload = data[pos:pos + 2]
        return pos + 2, ("key_signature", delta, duration, payload, start)

    if opcode in (0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47):
        if pos + 2 > end:
            raise Star3Error("truncated text event length")
        length = int.from_bytes(data[pos:pos + 2], "little")
        pos += 2
        if pos + length > end:
            raise Star3Error("truncated text event")
        payload = data[pos:pos + length]
        kind = "track_name" if opcode == 0x43 else "text"
        return pos + length, (kind, delta, duration, payload, start)

    if opcode == 0x0C:
        if pos + 6 > end:
            raise Star3Error("truncated extended event")
        return pos + 6, ("ignored", delta, duration, data[pos:pos + 6], start)

    raise Star3Error(f"unsupported Star3 event opcode 0x{opcode:02x}")


def parse_event_sequences(block: bytes) -> list[tuple[int, object]]:
    events: list[tuple[int, object]] = []
    end = len(block)
    consumed_until = 0
    scan = 0
    while scan < end:
        if scan < consumed_until:
            scan += 1
            continue
        pos = scan
        current_time = 0
        seq: list[tuple[int, object]] = []
        try:
            while pos < end:
                new_pos, event = parse_star3_event(block, pos, end)
                current_time += event[1]
                seq.append((current_time, event))
                pos = new_pos
        except Star3Error:
            pass
        if len(seq) >= 2 and pos - scan >= 8:
            events.extend(seq)
            consumed_until = max(consumed_until, pos)
            scan = pos
        else:
            scan += 1
    if not events:
        raise Star3Error("no supported Star3 events found")
    return events


def validate_midi_track(body: bytes) -> bool:
    pos = 0
    running_status: int | None = None
    saw_end = False
    while pos < len(body):
        _, pos = read_vlq(body, pos, len(body))
        if pos >= len(body):
            raise Star3Error("truncated MIDI track event")
        status = body[pos]
        if status == 0xFF:
            pos += 1
            if pos >= len(body):
                raise Star3Error("truncated MIDI meta event")
            meta_type = body[pos]
            pos += 1
            length, pos = read_vlq(body, pos, len(body))
            if pos + length > len(body):
                raise Star3Error("truncated MIDI meta payload")
            if meta_type == 0x2F:
                saw_end = True
            pos += length
            running_status = None
        elif status in (0xF0, 0xF7):
            pos += 1
            length, pos = read_vlq(body, pos, len(body))
            if pos + length > len(body):
                raise Star3Error("truncated MIDI sysex payload")
            pos += length
            running_status = None
        elif status >= 0x80:
            running_status = status
            pos += 1 + midi_event_data_length(status)
            if pos > len(body):
                raise Star3Error("truncated MIDI channel event")
        else:
            if running_status is None:
                raise Star3Error("MIDI running status without prior status")
            pos += midi_event_data_length(running_status)
            if pos > len(body):
                raise Star3Error("truncated MIDI running-status event")
    return saw_end


def normalize_midi_file(data: bytes) -> bytes:
    if len(data) < 14 or data[:4] != b"MThd":
        raise Star3Error("decompressed V3.00 music block is not MIDI")
    header_length = int.from_bytes(data[4:8], "big")
    if header_length != 6 or 8 + header_length > len(data):
        raise Star3Error("unsupported MIDI header in V3.00 music block")
    track_count = int.from_bytes(data[10:12], "big")
    pos = 8 + header_length
    track_offsets: list[int] = []
    for _ in range(track_count):
        if pos + 8 > len(data) or data[pos:pos + 4] != b"MTrk":
            raise Star3Error("invalid MIDI track chunk in V3.00 music block")
        length = int.from_bytes(data[pos + 4:pos + 8], "big")
        if pos + 8 + length > len(data):
            raise Star3Error("MIDI track chunk exceeds V3.00 music block")
        track_offsets.append(pos)
        pos += 8 + length
    if pos == len(data):
        return data

    found_offsets: list[int] = []
    scan = 8 + header_length
    while True:
        found = data.find(b"MTrk", scan)
        if found < 0:
            break
        found_offsets.append(found)
        scan = found + 1

    if len(found_offsets) > len(track_offsets):
        try:
            for index, offset in enumerate(found_offsets):
                end = found_offsets[index + 1] if index + 1 < len(found_offsets) else len(data)
                validate_midi_track(data[offset + 8:end])
            return rewrite_midi_chunks(data, found_offsets)
        except Star3Error:
            pass

    return rewrite_midi_chunks(data, track_offsets[:-1] + [track_offsets[-1]], extend_last=True)


def rewrite_midi_chunks(data: bytes, offsets: list[int], extend_last: bool = False) -> bytes:
    if not offsets:
        raise Star3Error("MIDI file has no track chunks")
    header = bytearray(data[:14])
    header[10:12] = len(offsets).to_bytes(2, "big")
    out = bytearray(header)
    for index, offset in enumerate(offsets):
        end = offsets[index + 1] if index + 1 < len(offsets) else len(data)
        if not extend_last and index + 1 == len(offsets):
            end = len(data)
        if data[offset:offset + 4] != b"MTrk" or offset + 8 > end:
            raise Star3Error("invalid MIDI track offset")
        body = data[offset + 8:end]
        out += b"MTrk" + len(body).to_bytes(4, "big") + body
    return bytes(out)


def add_midi_event(track_events: list[tuple[int, bytes]], tick: int, payload: bytes) -> None:
    track_events.append((tick, payload))


def build_midi(events: list[tuple[int, object]], division: int) -> bytes:
    track_events: list[tuple[int, bytes]] = []
    for tick, event in events:
        kind = event[0]
        if kind == "midi":
            payload = event[3]
            add_midi_event(track_events, tick, payload)
            status = payload[0]
            if (status & 0xF0) == 0x90 and len(payload) == 3 and payload[2] != 0 and event[2] > 0:
                add_midi_event(track_events, tick + event[2], bytes([0x80 | (status & 0x0F), payload[1], 0]))
        elif kind == "tempo":
            tempo = event[3]
            add_midi_event(track_events, tick, b"\xff\x51\x03" + int(tempo).to_bytes(3, "big"))
        elif kind == "time_signature":
            payload = event[3]
            add_midi_event(track_events, tick, b"\xff\x58\x04" + payload)
        elif kind == "key_signature":
            payload = event[3]
            add_midi_event(track_events, tick, b"\xff\x59\x02" + payload[:2])
        elif kind == "track_name":
            text = event[3]
            add_midi_event(track_events, tick, b"\xff\x03" + write_vlq(len(text)) + text)
        elif kind == "text":
            text = event[3]
            add_midi_event(track_events, tick, b"\xff\x01" + write_vlq(len(text)) + text)

    track_events.sort(key=lambda item: (item[0], 0 if item[1].startswith(b"\xff") else 1))
    body = bytearray()
    last_tick = 0
    for tick, payload in track_events:
        if tick < last_tick:
            raise Star3Error("non-monotonic MIDI event ordering")
        body += write_vlq(tick - last_tick)
        body += payload
        last_tick = tick
    body += b"\x00\xff\x2f\x00"

    header = b"MThd" + struct.pack(">IHHH", 6, 0, 1, division)
    track = b"MTrk" + struct.pack(">I", len(body)) + bytes(body)
    return header + track


def parse_cevent_header(data: bytes) -> CEventHeader:
    cpos = data.find(b"CEVENT\x00\x00")
    lpos = data.find(b"LYRICS\x00\x00")
    if cpos < 0 or lpos < 0 or lpos <= cpos:
        raise Star3Error("missing CEVENT/LYRICS chunks")
    if cpos + 28 > len(data):
        raise Star3Error("truncated CEVENT header")
    fields = struct.unpack_from("<HHHHHHII", data, cpos + 8)
    return CEventHeader(cpos, fields[0], fields[1], fields[2], fields[3],
                        fields[4], fields[5], fields[6], fields[7], lpos)


def convert_v350(data: bytes) -> bytes:
    header = parse_cevent_header(data)
    if header.reserved0 != 0:
        raise Star3Error("unsupported CEVENT reserved value")
    prefix_len = header.prefix_length_field - 12
    if prefix_len < 0:
        raise Star3Error("invalid CEVENT prefix length")
    if header.stored_length == header.unpacked_length:
        block_start = header.offset + 28 + prefix_len
        block_end = block_start + header.unpacked_length
        if block_end != header.lyrics_offset:
            raise Star3Error("CEVENT length does not end at LYRICS")
        block = data[block_start:block_end]
    elif header.stored_length < header.unpacked_length:
        if prefix_len < 4:
            raise Star3Error("compressed CEVENT prefix is too short")
        block_start = header.offset + 28 + prefix_len - 4
        block_end = block_start + header.stored_length
        if block_end + 4 != header.lyrics_offset:
            raise Star3Error("compressed CEVENT length does not end before trailer/LYRICS")
        block = decompress_lzss_xor(data[block_start:block_end], header.unpacked_length, STAR3_XOR_KEY)
    else:
        raise Star3Error("CEVENT stored length is larger than unpacked length")
    events = parse_event_sequences(block)
    return build_midi(events, header.division)


def convert_v300(data: bytes) -> bytes:
    if len(data) < 0x126:
        raise Star3Error("truncated V3.00 header")
    lyric_length = struct.unpack_from("<H", data, 0x106)[0]
    constant = struct.unpack_from("<H", data, 0x108)[0]
    intro_length = struct.unpack_from("<I", data, 0x122)[0]
    if constant != 0x000B:
        raise Star3Error("unsupported V3.00 header fields")
    pos = 0x126 + intro_length
    if pos + 8 > len(data):
        raise Star3Error("truncated V3.00 lyric-sync block header")
    sync_stored_length, sync_unpacked_length = struct.unpack_from("<II", data, pos)
    pos += 8
    if sync_unpacked_length < sync_stored_length:
        raise Star3Error("invalid V3.00 lyric-sync block lengths")
    pos += sync_stored_length
    if pos + lyric_length + 8 > len(data):
        raise Star3Error("truncated V3.00 lyric/music blocks")
    pos += lyric_length

    music_total_length = struct.unpack_from("<I", data, pos)[0]
    music_header = pos + 4
    if music_total_length < 9 or pos + music_total_length + 4 > len(data):
        raise Star3Error("invalid V3.00 music block length")
    if data[music_header] != 0:
        raise Star3Error("unsupported V3.00 music reserved byte")
    unpacked_length = int.from_bytes(data[music_header + 1:music_header + 4], "little")
    if data[music_header + 4] != 0:
        raise Star3Error("unsupported V3.00 music compression marker")
    compressed = data[music_header + 5:pos + music_total_length + 4]
    midi = decompress_lzss_xor(compressed, unpacked_length, STAR3_V300_XOR_KEY)
    return normalize_midi_file(midi)


def convert(data: bytes) -> bytes:
    if data.startswith(b"STAR DATA V3.50\x1a\x11\x01\x00\x00"):
        return convert_v350(data)
    if data.startswith(b"STAR DATA V3.00\x1a\x0e\x01\x00\x00"):
        return convert_v300(data)
    raise Star3Error("not a supported Star3 MIDI Karaoke file")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(f"usage: {Path(argv[0]).name} <inputFile> <outputFile>", file=sys.stderr)
        return 2
    src = Path(argv[1])
    dst = Path(argv[2])
    try:
        midi = convert(src.read_bytes())
        tmp = dst.with_name(dst.name + ".tmp")
        tmp.write_bytes(midi)
        os.chmod(tmp, 0o664)
        os.replace(tmp, dst)
        os.chmod(dst, 0o664)
    except Exception as exc:
        try:
            if dst.exists():
                dst.unlink()
            tmp = dst.with_name(dst.name + ".tmp")
            if tmp.exists():
                tmp.unlink()
        finally:
            print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

#!/usr/bin/env python3
# Vibe coded by Codex
import os
import struct
import sys
from dataclasses import dataclass
from pathlib import Path


CONTAINER_ATOMS = {b"moov", b"trak", b"mdia", b"minf", b"stbl"}
KNOWN_LEAF_ATOMS = {
    b"mvhd",
    b"tkhd",
    b"mdhd",
    b"hdlr",
    b"stsd",
    b"stts",
    b"stss",
    b"stsc",
    b"stsz",
    b"stco",
}


class TwvError(Exception):
    pass


def u32(data, offset):
    return struct.unpack_from("<I", data, offset)[0]


def pack_u32(value):
    return struct.pack("<I", value)


def fourcc(value):
    if len(value) != 4:
        raise ValueError("fourcc must be four bytes")
    return value


@dataclass
class Atom:
    offset: int
    size: int
    kind: bytes
    payload_offset: int
    payload_end: int
    children: list


@dataclass
class Track:
    handler_class: str
    handler_subtype: str
    handler_extra: bytes
    timescale: int
    duration: int
    stsd_count: int
    stsd_body: bytes
    stts: list
    stss: list
    stsc: list
    sizes: list
    offsets: list


@dataclass
class TwvFile:
    data: bytes
    palette: bytes
    tflp_track: Track
    raw_track: Track
    tflp_records: list
    audio_data: bytes
    audio_bits: int
    audio_rate: int


def parse_children(data, start, end):
    pos = start
    atoms = []
    while pos < end:
        if pos + 8 > end:
            raise TwvError(f"truncated atom header at 0x{pos:x}")
        size = u32(data, pos)
        kind = data[pos + 4 : pos + 8]
        if size < 8:
            raise TwvError(f"invalid atom size {size} for {kind!r} at 0x{pos:x}")
        atom_end = pos + size
        if atom_end > end:
            raise TwvError(f"atom {kind!r} at 0x{pos:x} extends past parent")
        if kind in CONTAINER_ATOMS:
            if size < 12:
                raise TwvError(f"container atom {kind!r} is too small")
            reserved = data[pos + 8 : pos + 12]
            if reserved != b"\x00\x00\x00\x00":
                raise TwvError(f"container atom {kind!r} has non-zero reserved bytes")
            children = parse_children(data, pos + 12, atom_end)
            payload_offset = pos + 12
        else:
            if kind not in KNOWN_LEAF_ATOMS and kind != b"mdat":
                raise TwvError(f"unsupported atom {kind!r} at 0x{pos:x}")
            children = []
            payload_offset = pos + 8
        atoms.append(Atom(pos, size, kind, payload_offset, atom_end, children))
        pos = atom_end
    if pos != end:
        raise TwvError("atom parser ended off boundary")
    return atoms


def only_child_atoms(atom, kind):
    return [child for child in atom.children if child.kind == kind]


def find_leaf(atom, kind):
    found = []
    stack = [atom]
    while stack:
        cur = stack.pop()
        for child in cur.children:
            if child.kind == kind:
                found.append(child)
            stack.append(child)
    if len(found) != 1:
        raise TwvError(f"expected one {kind.decode('ascii')} atom, found {len(found)}")
    return found[0]


def leaf_payload(data, atom):
    return data[atom.payload_offset : atom.payload_end]


def parse_full_atom_entries(payload, entry_size, label):
    if len(payload) < 8:
        raise TwvError(f"{label} payload is too short")
    flags = u32(payload, 0)
    if flags != 0:
        raise TwvError(f"{label} has unsupported flags 0x{flags:08x}")
    count = u32(payload, 4)
    expected = 8 + count * entry_size
    if len(payload) != expected:
        raise TwvError(f"{label} size does not match entry count")
    return count


def parse_track(data, trak):
    mdhd = find_leaf(trak, b"mdhd")
    mdhd_payload = leaf_payload(data, mdhd)
    if len(mdhd_payload) != 20 or u32(mdhd_payload, 0) != 0:
        raise TwvError("unsupported mdhd payload")
    timescale = u32(mdhd_payload, 12)
    duration = u32(mdhd_payload, 16)
    if timescale == 0:
        raise TwvError("track timescale is zero")

    hdlr = find_leaf(trak, b"hdlr")
    hdlr_payload = leaf_payload(data, hdlr)
    if len(hdlr_payload) != 16 or u32(hdlr_payload, 0) != 0:
        raise TwvError("unsupported hdlr payload")
    handler_class = hdlr_payload[4:8].decode("ascii")
    handler_subtype = hdlr_payload[8:12].decode("ascii")
    handler_extra = hdlr_payload[12:16]

    stsd_payload = leaf_payload(data, find_leaf(trak, b"stsd"))
    if len(stsd_payload) < 8 or u32(stsd_payload, 0) != 0:
        raise TwvError("unsupported stsd payload")
    stsd_count = u32(stsd_payload, 4)
    stsd_body = stsd_payload[8:]

    stts_payload = leaf_payload(data, find_leaf(trak, b"stts"))
    count = parse_full_atom_entries(stts_payload, 8, "stts")
    stts = [(u32(stts_payload, 8 + i * 8), u32(stts_payload, 12 + i * 8)) for i in range(count)]

    stss_payload = leaf_payload(data, find_leaf(trak, b"stss"))
    count = parse_full_atom_entries(stss_payload, 4, "stss")
    stss = [u32(stss_payload, 8 + i * 4) for i in range(count)]

    stsc_payload = leaf_payload(data, find_leaf(trak, b"stsc"))
    count = parse_full_atom_entries(stsc_payload, 12, "stsc")
    stsc = [
        (u32(stsc_payload, 8 + i * 12), u32(stsc_payload, 12 + i * 12), u32(stsc_payload, 16 + i * 12))
        for i in range(count)
    ]
    if not stsc or stsc[0][0] != 1:
        raise TwvError("stsc must start at chunk 1")

    stsz_payload = leaf_payload(data, find_leaf(trak, b"stsz"))
    if len(stsz_payload) < 12 or u32(stsz_payload, 0) != 0:
        raise TwvError("unsupported stsz payload")
    default_size = u32(stsz_payload, 4)
    sample_count = u32(stsz_payload, 8)
    if default_size:
        if len(stsz_payload) != 12:
            raise TwvError("stsz default-size table has trailing bytes")
        sizes = [default_size] * sample_count
    else:
        expected = 12 + sample_count * 4
        if len(stsz_payload) != expected:
            raise TwvError("stsz size table length mismatch")
        sizes = [u32(stsz_payload, 12 + i * 4) for i in range(sample_count)]

    stco_payload = leaf_payload(data, find_leaf(trak, b"stco"))
    count = parse_full_atom_entries(stco_payload, 4, "stco")
    offsets = [u32(stco_payload, 8 + i * 4) for i in range(count)]
    if not offsets:
        raise TwvError("track has no chunk offsets")

    return Track(
        handler_class,
        handler_subtype,
        handler_extra,
        timescale,
        duration,
        stsd_count,
        stsd_body,
        stts,
        stss,
        stsc,
        sizes,
        offsets,
    )


def sample_references(track):
    refs = []
    sample_index = 0
    for entry_index, (first_chunk, samples_per_chunk, sample_description_id) in enumerate(track.stsc):
        if samples_per_chunk == 0:
            raise TwvError("stsc samples-per-chunk is zero")
        next_first_chunk = (
            track.stsc[entry_index + 1][0] if entry_index + 1 < len(track.stsc) else len(track.offsets) + 1
        )
        if next_first_chunk <= first_chunk:
            raise TwvError("stsc chunk ranges are not increasing")
        for chunk_number in range(first_chunk, next_first_chunk):
            if chunk_number < 1 or chunk_number > len(track.offsets):
                raise TwvError("stsc references a missing chunk")
            offset = track.offsets[chunk_number - 1]
            for _ in range(samples_per_chunk):
                if sample_index >= len(track.sizes):
                    break
                size = track.sizes[sample_index]
                refs.append((offset, size, sample_index + 1, chunk_number, sample_description_id))
                offset += size
                sample_index += 1
    if sample_index != len(track.sizes):
        raise TwvError("sample table does not describe every sample")
    return refs


def validate_palette(palette):
    if len(palette) % 4:
        raise TwvError("palette prefix is not composed of 4-byte entries")
    for i in range(0, len(palette), 4):
        if palette[i + 3] != 0:
            raise TwvError("palette entry has non-zero reserved byte")


def parse_tflp_record(record):
    if len(record) != 17:
        raise TwvError("tflp record is not 17 bytes")
    if record[0] != 17:
        raise TwvError("tflp record length marker is not 17")
    if record[1:8] != b"\x00" * 7:
        raise TwvError("tflp reserved bytes are non-zero")
    opcode = record[8]
    values = struct.unpack_from("<hhhh", record, 9)
    return (opcode, values)


def parse_twv(path):
    data = Path(path).read_bytes()
    atoms = parse_children(data, 0, len(data))
    if len(atoms) != 2 or atoms[0].kind != b"moov" or atoms[1].kind != b"mdat":
        raise TwvError("TWV must contain moov followed by mdat")
    moov, mdat = atoms
    if mdat.size < 12:
        raise TwvError("mdat is too small")
    if data[mdat.offset + 8 : mdat.offset + 12] != b"\x00\x00\x00\x00":
        raise TwvError("mdat reserved bytes are non-zero")

    mvhd = only_child_atoms(moov, b"mvhd")
    if len(mvhd) != 1:
        raise TwvError("movie header missing or duplicated")
    if len(leaf_payload(data, mvhd[0])) != 88:
        raise TwvError("unsupported mvhd length")

    trak_atoms = only_child_atoms(moov, b"trak")
    if len(trak_atoms) != 2:
        raise TwvError("TWV converter expects exactly two tracks")
    tracks = [parse_track(data, atom) for atom in trak_atoms]
    tflp_tracks = [track for track in tracks if track.handler_class == "mhlr" and track.handler_subtype == "tflp"]
    raw_tracks = [track for track in tracks if track.handler_class == "shlr" and track.handler_subtype == "raw "]
    if len(tflp_tracks) != 1 or len(raw_tracks) != 1:
        raise TwvError("TWV must contain one tflp track and one raw audio track")
    tflp_track = tflp_tracks[0]
    raw_track = raw_tracks[0]

    if tflp_track.timescale != 10 or tflp_track.duration != len(tflp_track.sizes):
        raise TwvError("unsupported tflp timing")
    if any(size != 17 for size in tflp_track.sizes):
        raise TwvError("unsupported tflp sample size")
    if raw_track.timescale != 22050:
        raise TwvError("unsupported raw audio sample rate")

    if raw_track.handler_extra == b"\x04\x04\x22\x56":
        audio_bits = 16
        expected_duration = sum(raw_track.sizes) // 2
        if sum(raw_track.sizes) % 2:
            raise TwvError("16-bit audio has odd byte count")
    elif raw_track.handler_extra == b"\x02\x02\x22\x56":
        audio_bits = 8
        expected_duration = sum(raw_track.sizes)
    else:
        raise TwvError(f"unsupported raw audio descriptor {raw_track.handler_extra.hex()}")
    if raw_track.duration != expected_duration:
        raise TwvError("raw audio duration does not match byte count")

    mdat_base = mdat.offset + 12
    mdat_end = mdat.offset + mdat.size
    coverage = []
    tflp_records = []
    audio_parts = []
    for track in tracks:
        for offset, size, sample_index, _chunk_number, _sample_description_id in sample_references(track):
            start = mdat_base + offset
            end = start + size
            if start < mdat_base or end > mdat_end:
                raise TwvError("sample reference points outside mdat")
            coverage.append((start, end))
            payload = data[start:end]
            if track is tflp_track:
                tflp_records.append(parse_tflp_record(payload))
            elif track is raw_track:
                audio_parts.append(payload)

    coverage.sort()
    cursor = mdat_base
    gaps = []
    for start, end in coverage:
        if start < cursor:
            raise TwvError("sample references overlap")
        if start > cursor:
            gaps.append((cursor, start))
        cursor = end
    if cursor != mdat_end:
        raise TwvError("sample references do not consume the end of mdat")
    if len(gaps) != 1 or gaps[0][0] != mdat_base:
        raise TwvError("unsupported mdat gap layout")
    palette = data[gaps[0][0] : gaps[0][1]]
    validate_palette(palette)

    return TwvFile(data, palette, tflp_track, raw_track, tflp_records, b"".join(audio_parts), audio_bits, raw_track.timescale)


def riff_chunk(chunk_id, payload):
    pad = b"\x00" if len(payload) % 2 else b""
    return fourcc(chunk_id) + pack_u32(len(payload)) + payload + pad


def make_wav(twv):
    block_align = 1 if twv.audio_bits == 8 else 2
    byte_rate = twv.audio_rate * block_align
    fmt = struct.pack("<HHIIHH", 1, 1, twv.audio_rate, byte_rate, block_align, twv.audio_bits)
    body = b"WAVE" + riff_chunk(b"fmt ", fmt) + riff_chunk(b"data", twv.audio_data)
    return b"RIFF" + pack_u32(len(body)) + body


def convert(input_path, output_path):
    twv = parse_twv(input_path)
    wav = make_wav(twv)
    out = Path(output_path)
    tmp = out.with_name(out.name + ".tmp")
    try:
        tmp.write_bytes(wav)
        os.chmod(tmp, 0o664)
        tmp.replace(out)
        os.chmod(out, 0o664)
    except Exception:
        try:
            tmp.unlink()
        except FileNotFoundError:
            pass
        raise


def main(argv):
    if len(argv) != 3:
        print("usage: twvAudio.py <inputFile> <outputFile.wav>", file=sys.stderr)
        return 2
    output_path = Path(argv[2])
    try:
        convert(argv[1], output_path)
    except Exception as exc:
        try:
            output_path.unlink()
        except FileNotFoundError:
            pass
        print(f"twvAudio: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

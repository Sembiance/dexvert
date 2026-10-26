#!/usr/bin/env python3
# Vibe coded by Codex
"""Convert clear CRI USM MPEG-1/Sofdec + ADX movies to lossless AVI.

Only Python's standard library and the ffmpeg/ffprobe executables are required.
See criwareSofdec2Movie.txt for the supported profile and research limitations.
"""

from __future__ import annotations

import argparse
import array
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from fractions import Fraction
import hashlib
import json
import math
import mmap
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import wave


class FormatError(Exception):
    """Input cannot be interpreted safely."""


class Unsupported(FormatError):
    """Recognized container, unsupported codec or feature."""


def require(condition, message):
    if not condition:
        raise FormatError(message)


def u32(data, offset=0):
    return struct.unpack_from(">I", data, offset)[0]


def readable(path):
    path.chmod(path.stat().st_mode | 0o440)


def utf_table(data):
    """Bounds-checked @UTF; offsets are relative to byte 8, except strings/blobs."""
    require(len(data) >= 32 and data[:4] == b"@UTF", "missing @UTF table")
    size, rows, strings, blobs, name, ncols, rowlen, nrows = struct.unpack_from(
        ">IIIIIHHI", data, 4)
    end = size + 8
    rows += 8
    strings += 8
    blobs += 8
    require(32 <= rows <= strings <= blobs <= end <= len(data), "invalid @UTF offsets")
    require(ncols <= (rows - 32) // 5, "@UTF column definitions do not fit")
    require(rows + nrows * rowlen <= strings, "@UTF rows overlap string pool")
    require(nrows <= 1000000, "@UTF row count exceeds resource limit")
    covered = bytearray(end)
    covered[:32] = b"\1" * 32
    string_values = {}
    blob_values = {}

    def mark(a, b):
        require(0 <= a <= b <= end, "@UTF value out of bounds")
        covered[a:b] = b"\1" * (b - a)

    def string(offset):
        p = strings + offset
        require(strings <= p < blobs, "@UTF string pointer out of bounds")
        q = data.find(b"\0", p, blobs)
        require(q >= 0, "unterminated @UTF string")
        # Keep arbitrary original name bytes losslessly; do not guess a charset.
        raw = data[p:q]
        value = raw.decode("utf-8", "surrogateescape")
        mark(p, q + 1)
        string_values[str(offset)] = {"text": value, "raw_hex": raw.hex()}
        return value

    formats = {0: "B", 1: "b", 2: "H", 3: "h", 4: "I", 5: "i",
               6: "Q", 7: "q", 8: "f", 9: "d", 10: "I", 11: "II"}

    def value(typ, p, limit):
        require(typ in formats, f"unsupported @UTF type {typ}")
        fmt = ">" + formats[typ]
        length = struct.calcsize(fmt)
        require(p + length <= limit, "truncated @UTF value")
        parts = struct.unpack_from(fmt, data, p)
        mark(p, p + length)
        v = parts[0]
        if typ == 10:
            v = string(v)
        elif typ == 11:
            start, count = parts
            require(blobs + start + count <= end, "@UTF blob pointer out of bounds")
            mark(blobs + start, blobs + start + count)
            v = {"offset": start, "size": count,
                 "hex": data[blobs + start:blobs + start + count].hex()}
            blob_values[str(start)] = v
        return v, length

    columns = []
    p = 32
    for _ in range(ncols):
        require(p + 5 <= rows, "truncated @UTF column")
        flag, ptr = struct.unpack_from(">BI", data, p)
        mark(p, p + 5)
        p += 5
        storage, typ = flag >> 4, flag & 15
        require(storage in (1, 3, 5) and typ in formats, f"unsupported @UTF flag 0x{flag:02x}")
        constant = 0
        if storage == 3:
            constant, length = value(typ, p, rows)
            p += length
        elif storage == 1 and typ == 10:
            constant = string(0)
        elif storage == 1 and typ == 11:
            constant = {"offset": 0, "size": 0, "hex": ""}
        columns.append({"name": string(ptr), "flag": flag, "constant": constant})
    require(len({c["name"] for c in columns}) == ncols, "duplicate @UTF column names")
    result = []
    for row in range(nrows):
        p = rows + row * rowlen
        stop = p + rowlen
        record = {}
        for col in columns:
            v = col["constant"]
            if col["flag"] >> 4 == 5:
                v, length = value(col["flag"] & 15, p, stop)
                p += length
            record[col["name"]] = v
        require(p == stop, "@UTF row length disagrees with schema")
        result.append(record)
    table_name = string(name)
    # Enumerate even unused strings. Remaining zero bytes are table alignment.
    p = strings
    while p < blobs:
        q = data.find(b"\0", p, blobs)
        require(q >= 0, "unterminated string pool")
        string(p - strings)
        p = q + 1
    unclaimed = []
    p = 0
    while p < end:
        if covered[p]:
            p += 1
            continue
        q = p + 1
        while q < end and not covered[q]:
            q += 1
        raw = data[p:q]
        unclaimed.append({"offset": p, "size": q - p, "zero": not any(raw),
                          "hex": raw.hex() if any(raw) else ""})
        p = q
    return {"name": table_name, "size": end, "columns": columns, "rows": result,
            "strings": string_values, "blobs": blob_values, "unclaimed": unclaimed,
            "trailing_hex": data[end:].hex()}


@dataclass
class Chunk:
    offset: int
    size: int
    tag: str
    channel: int
    kind: int
    payload: int
    length: int
    padding: int
    time: int
    rate: int
    truncated: bool = False

    def ledger(self):
        return [self.offset, self.size, self.tag, self.channel, self.kind,
                self.payload, self.length, self.padding, self.time, self.rate,
                self.truncated]


@dataclass
class Stream:
    tag: str
    channel: int
    header: dict = field(default_factory=dict)
    directory: dict = field(default_factory=dict)
    chunks: list = field(default_factory=list)
    controls: list = field(default_factory=list)
    metadata: list = field(default_factory=list)
    details: dict = field(default_factory=dict)

    @property
    def key(self):
        return f"{self.tag}:{self.channel}"


class Movie:
    def __init__(self, path):
        self.path = Path(path)
        self.file = self.path.open("rb")
        try:
            require(os.fstat(self.file.fileno()).st_size >= 32, "not a CRI USM: file too small")
            self.data = mmap.mmap(self.file.fileno(), 0, access=mmap.ACCESS_READ)
        except BaseException:
            self.file.close()
            raise
        self.chunks = []
        self.tables = []
        self.streams = {}
        self.warnings = []
        self.unresolved = []
        self.directory = []
        self.coverage = Counter()
        self.identified = False

    def close(self):
        self.data.close()
        self.file.close()

    def warn(self, message):
        if message not in self.warnings:
            self.warnings.append(message)

    def stream(self, tag, channel):
        key = (tag, channel)
        if key not in self.streams:
            self.streams[key] = Stream(tag, channel)
        return self.streams[key]

    def payload(self, c):
        return self.data[c.payload:c.payload + c.length]

    def parse(self):
        data, length = self.data, len(self.data)
        require(data[:4] == b"CRID", "not a CRI USM: missing CRID signature")
        pos = 0
        while pos < length:
            if pos + 32 > length:
                require(self.identified, "not an identifiable CRI USM")
                self.warn(f"truncated chunk header at {pos}; stopped at last certain boundary")
                self.coverage["unparsed_truncated_tail"] += length - pos
                break
            tag = data[pos:pos + 4].decode("ascii", "replace")
            body = u32(data, pos + 4)
            offset = data[pos + 9]
            padding = int.from_bytes(data[pos + 10:pos + 12], "big")
            channel, kind = data[pos + 12], data[pos + 15]
            if body < 24 or offset < 24 or offset + padding > body:
                require(self.identified, "not an identifiable CRI USM: invalid root chunk")
                self.warn(f"invalid chunk sizes at {pos}; cannot safely locate next chunk")
                self.coverage["unparsed_malformed_tail"] += length - pos
                break
            end = pos + 8 + body
            start = pos + 8 + offset
            stop = end - padding
            truncated = end > length
            if start > length:
                self.warn(f"truncated extended header at {pos}")
                self.coverage["unparsed_truncated_tail"] += length - pos
                break
            actual_stop = min(stop, length)
            c = Chunk(pos, min(end, length) - pos, tag, channel, kind, start,
                      actual_stop - start, max(0, min(end, length) - actual_stop),
                      u32(data, pos + 16), u32(data, pos + 20), truncated)
            payload = self.payload(c)
            if pos == 0:
                require(tag == "CRID" and kind == 1 and payload[:4] == b"@UTF",
                        "not an identifiable CRI USM directory")
                root = utf_table(payload)
                require(root["name"] == "CRIUSF_DIR_STREAM", "not a CRI USM directory table")
                require(all(k in {x['name'] for x in root['columns']}
                            for k in ("stmid", "chno", "filesize")), "incomplete USM directory schema")
                self.identified = True
                self.directory = root["rows"]
            if tag not in ("CRID", "@SFV", "@SFA", "@SBT"):
                raise Unsupported(f"USM stream {tag!r} at {pos} is outside the supported profile")
            if kind not in (0, 1, 2, 3):
                raise Unsupported(f"USM payload type {kind} at {pos} is unsupported")
            self.chunks.append(c)
            self.coverage["chunk_headers"] += 32
            self.coverage["extended_headers"] += offset - 24
            self.coverage["chunk_padding"] += c.padding
            self.coverage[f"payload_{tag}_{kind}"] += c.length
            reserved = data[pos + 8:pos + 9] + data[pos + 13:pos + 15] + data[pos + 24:pos + 32]
            extra = data[pos + 32:start]
            if any(reserved) or any(extra):
                self.unresolved.append({"chunk": pos, "reserved_hex": reserved.hex(),
                                        "extended_header_hex": extra.hex()})
                self.warn("nonzero reserved/extended chunk header bytes retained in audit")
            if any(data[actual_stop:min(end, length)]):
                self.warn(f"nonzero declared padding at {actual_stop}")
                self.unresolved.append({"offset": actual_stop,
                                        "padding_hex": data[actual_stop:min(end, length)].hex()})
            stream = self.stream(tag, channel) if tag != "CRID" else None
            if kind in (1, 3):
                try:
                    table = root if pos == 0 else utf_table(payload)
                    self.tables.append({"chunk_offset": pos, "payload_offset": start, **table})
                    if any(not r["zero"] for r in table["unclaimed"]) or any(bytes.fromhex(table["trailing_hex"])):
                        self.warn(f"uninterpreted nonzero table bytes at {start}; retained in audit")
                    if stream:
                        expected = {"@SFV": "VIDEO_HDRINFO", "@SFA": "AUDIO_HDRINFO",
                                    "@SBT": "SUBTITLE_HDRINFO"}[tag]
                        if kind == 1:
                            if table["name"] != expected:
                                raise Unsupported(f"unsupported stream table {table['name']}")
                            require(len(table["rows"]) == 1, "stream header must have one row")
                            stream.header = table["rows"][0]
                        else:
                            stream.metadata.append(table)
                except Unsupported:
                    raise
                except FormatError as e:
                    self.warn(f"malformed metadata at {pos}: {e}; skipped using declared chunk size")
                    self.unresolved.append({"chunk": pos, "payload_hex": payload.hex()})
            elif kind == 2:
                known = (b"#HEADER END     ===============\0", b"#METADATA END   ===============\0",
                         b"#CONTENTS END   ===============\0")
                if payload not in known:
                    self.warn(f"unknown control at {pos}; retained in audit")
                if stream:
                    stream.controls.append({"offset": pos, "hex": payload.hex(),
                                            "text": payload.decode("ascii", "backslashreplace")})
            elif stream:
                stream.chunks.append(c)
            else:
                raise Unsupported("CRID content payload is unsupported")
            if truncated:
                self.warn(f"truncated final chunk at {pos}; retained {c.length} payload bytes")
                break
            pos = end
        require(self.identified, "not an identifiable CRI USM")
        for row in self.directory:
            ident = row.get("stmid", 0)
            if ident == 0:
                if row.get("filesize") != length:
                    self.warn(f"directory file size {row.get('filesize')} differs from actual {length}")
                continue
            tag = int(ident).to_bytes(4, "big").decode("ascii", "replace")
            if tag not in ("@SFV", "@SFA", "@SBT"):
                raise Unsupported(f"directory declares unsupported stream {tag!r}")
            stream = self.stream(tag, row["chno"])
            stream.directory = row
            payload_size = sum(c.length for c in stream.chunks)
            # MPEG permits zero bytes before its start code. USM's directory
            # elementary size excludes these per-packet transport prefixes.
            if tag == "@SFV":
                for c in stream.chunks:
                    packet = self.payload(c)
                    prefix = packet.find(b"\x00\x00\x01")
                    if prefix >= 0 and not any(packet[:prefix]):
                        payload_size -= prefix
            if payload_size != row.get("filesize"):
                self.warn(f"{stream.key}: declared stream size {row.get('filesize')} vs {payload_size}")
        for stream in self.streams.values():
            if not stream.chunks:
                self.warn(f"{stream.key}: no content recovered")
            if stream.chunks and not stream.header:
                self.warn(f"{stream.key}: missing stream metadata; use elementary header where possible")
            if stream.tag == "@SFV":
                if stream.header.get("mpeg_codec", 1) != 1 or stream.header.get("alpha_type", 0):
                    raise Unsupported(f"{stream.key}: only clear MPEG-1/Sofdec without alpha is implemented")
                if stream.header.get("mpeg_dcprec", 8) not in (8, 11):
                    raise Unsupported(f"{stream.key}: unsupported DC precision")
            if stream.tag == "@SFA" and stream.header.get("audio_codec", 2) != 2:
                raise Unsupported(f"{stream.key}: only ADX audio is implemented")
        self.check_seek_tables()
        require(sum(self.coverage.values()) == length, "internal byte accounting error")
        return self

    def check_seek_tables(self):
        offsets = {c.offset: c for c in self.chunks}
        for s in self.streams.values():
            if s.chunks and not any(x["text"].startswith("#CONTENTS END") for x in s.controls):
                self.warn(f"{s.key}: missing contents-end control")
            if s.header and not any(x["text"].startswith("#HEADER END") for x in s.controls):
                self.warn(f"{s.key}: missing header-end control")
            metadata_chunks = [c for c in self.chunks if c.tag == s.tag and c.channel == s.channel and c.kind == 3]
            if s.header.get("metadata_count", len(metadata_chunks)) != len(metadata_chunks):
                self.warn(f"{s.key}: metadata count mismatch")
            if s.header.get("metadata_size", sum(c.size for c in metadata_chunks)) != sum(c.size for c in metadata_chunks):
                self.warn(f"{s.key}: allocated metadata size mismatch")
            if s.tag == "@SFV" and s.chunks:
                sizes = []
                for c in s.chunks:
                    packet = self.payload(c)
                    prefix = packet.find(b"\x00\x00\x01")
                    sizes.append(c.length - prefix if prefix >= 0 and not any(packet[:prefix]) else c.length)
                maximum = max(sizes)
                if s.header.get("ixsize", maximum) != maximum or s.directory.get("minbuf", maximum) != maximum:
                    self.warn(f"{s.key}: video buffer hint differs from largest recovered picture")
            frame_ids = {c.offset: i for i, c in enumerate(s.chunks)}
            for table in s.metadata:
                if table["name"] != "VIDEO_SEEKINFO":
                    self.warn(f"{s.key}: metadata table {table['name']} retained but not semantically implemented")
                    continue
                for row in table["rows"]:
                    target = row.get("ofs_byte")
                    c = offsets.get(target)
                    if not c or c.tag != s.tag or c.channel != s.channel or c.kind != 0:
                        self.warn(f"{s.key}: seek entry points outside known stream chunks: {target}")
                    elif frame_ids[target] != row.get("ofs_frmid"):
                        self.warn(f"{s.key}: seek frame index mismatch at {target}")
                    if row.get("num_skip", 0) or row.get("resv", 0):
                        self.warn(f"{s.key}: nonzero seek preroll/reserved fields retained; linear decode used")

    def extract(self, stream, path):
        with path.open("wb") as out:
            for c in stream.chunks:
                out.write(self.payload(c))

    def audit(self):
        uncertain = {"datasize", "minchk", "minbuf", "ixsize", "scrn_width",
                     "mat_width", "mat_height", "disp_width", "disp_height", "total_time"}
        semantic_fields = []
        for table in self.tables:
            for i, row in enumerate(table["rows"]):
                for key, val in row.items():
                    if key in uncertain:
                        semantic_fields.append({"table_offset": table["payload_offset"],
                                                "table": table["name"], "row": i,
                                                "field": key, "value": val})
        return {"format": "CRI USM / supported MPEG-1 Sofdec + ADX profile",
                "input_bytes": len(self.data), "sha256": hashlib.sha256(self.data).hexdigest(),
                "structurally_accounted_bytes": sum(self.coverage.values()),
                "complete_semantic_reverse_engineering": False,
                "limitations": ["Proprietary prefix in MPEG user data is opaque.",
                                "Some encoder buffer/screen/subtitle header semantics remain unresolved.",
                                "MPEG entropy decoding and IDCT are delegated to FFmpeg.",
                                "Other USM codecs, encryption, alpha, and unknown streams are unsupported."],
                "coverage": dict(self.coverage), "warnings": self.warnings,
                "unresolved_bytes": self.unresolved, "tables": self.tables,
                "metadata_fields_with_incomplete_semantics": semantic_fields,
                "chunk_columns": ["offset", "size", "tag", "channel", "kind", "payload_offset",
                                  "payload_size", "padding", "time", "rate", "truncated"],
                "chunks": [c.ledger() for c in self.chunks],
                "streams": [{"id": s.key, "header": s.header, "directory": s.directory,
                             "controls": s.controls, "details": s.details}
                            for s in self.streams.values()]}


MPEG_RATES = {1: Fraction(24000, 1001), 2: Fraction(24), 3: Fraction(25),
              4: Fraction(30000, 1001), 5: Fraction(30), 6: Fraction(50),
              7: Fraction(60000, 1001), 8: Fraction(60)}


def inspect_video(movie, stream, path):
    """Account for start-code units; use the codec implementation for their bit syntax."""
    with path.open("rb") as file, mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as data:
        code_counts, code_bytes, userdata = Counter(), Counter(), Counter()
        positions = list(re.finditer(b"\x00\x00\x01", data))
        require(positions, f"{stream.key}: no recoverable MPEG start codes (possibly encrypted)")
        prefix = data[:positions[0].start()]
        if any(prefix):
            raise Unsupported(f"{stream.key}: nonzero prefix before MPEG sequence; encryption/variant unsupported")
        width = height = 0
        bit_rate = vbv = 0
        rate = None
        precision_extension = False
        for i, match in enumerate(positions):
            pos = match.start()
            if pos + 4 > len(data):
                movie.warn(f"{stream.key}: incomplete final MPEG start code")
                continue
            code = data[pos + 3]
            stop = positions[i + 1].start() if i + 1 < len(positions) else len(data)
            code_counts[f"{code:02x}"] += 1
            code_bytes[f"{code:02x}"] += stop - pos
            if code == 0xB3 and stop - pos >= 12:
                head = int.from_bytes(data[pos + 4:pos + 12], "big")
                w, h, rc = head >> 52, (head >> 40) & 4095, (head >> 32) & 15
                require(w > 0 and h > 0 and rc in MPEG_RATES, "invalid MPEG sequence header")
                if width and (width != w or height != h):
                    raise Unsupported("changing video dimensions cannot be represented by this AVI conversion")
                width, height, rate = w, h, MPEG_RATES[rc]
                bit_rate, vbv = (head >> 14) & 0x3FFFF, (head >> 3) & 0x3FF
            elif code == 0xB2:
                raw = data[pos + 4:stop]
                userdata[raw.hex()] += 1
                # Exact extension syntax, not an offset or filename guess.
                marker = b"TMPGEXS\0" + b"00000028IDCPREC\0" + b"0000000800000003TMPGEXE\0" + b"00000000"
                if raw.endswith(marker):
                    precision_extension = True
            elif code == 0xB5:
                raise Unsupported("MPEG-2 extension encountered; this converter targets MPEG-1/Sofdec")
        require(width and rate, "no complete MPEG sequence header recovered")
        header = stream.header
        if header.get("mpeg_dcprec") == 11 and not precision_extension:
            raise Unsupported("11-bit Sofdec video lacks the supported TMPGEXS DC extension")
        if header.get("width", width) != width or header.get("height", height) != height:
            movie.warn(f"{stream.key}: container dimensions disagree with MPEG; using MPEG dimensions")
        if header.get("framerate_n") and header.get("framerate_d"):
            # USM values such as 29970/1000 are intentional, not rounded to NTSC.
            rate = Fraction(header["framerate_n"], header["framerate_d"])
        require(rate > 0, "invalid video rate")
        frames = code_counts["00"]
        if header.get("total_frames", frames) != frames:
            movie.warn(f"{stream.key}: declared {header.get('total_frames')} frames, recovered {frames} picture headers")
        prefix_counts = Counter()
        for i, c in enumerate(stream.chunks):
            packet = movie.payload(c)
            start = packet.find(b"\x00\x00\x01")
            if start >= 0 and not any(packet[:start]):
                prefix_counts[start] += 1
                if "pre_padding" in header and start != header["pre_padding"]:
                    movie.warn(f"{stream.key}: zero prefix differs from pre_padding metadata")
            if c.rate and i and Fraction(c.time, c.rate) - Fraction(stream.chunks[0].time, stream.chunks[0].rate or c.rate) != i / rate:
                movie.warn(f"{stream.key}: nonuniform packet clock; AVI uses declared constant frame rate")
                break
        stream.details = {"codec": "MPEG-1/Sofdec", "width": width, "height": height,
                          "frame_rate": str(rate), "picture_headers": frames,
                          "leading_zero_bytes": len(prefix), "start_code_counts": dict(code_counts),
                          "start_code_bytes": dict(code_bytes), "user_data_hex_counts": dict(userdata),
                          "sequence_bitrate_field": bit_rate, "vbv_buffer_units": vbv,
                          "dc_extension_11_bit": precision_extension}
        stream.details["packet_zero_prefix_counts"] = dict(prefix_counts)
        if stream.chunks[0].time:
            movie.warn(f"{stream.key}: nonzero initial video clock; conversion normalizes video start to zero")
        return rate


def adx_header(data):
    require(len(data) >= 24 and data[:2] == b"\x80\0", "missing ADX header; unsupported or damaged audio")
    start = int.from_bytes(data[2:4], "big") + 4
    encoding, block, bits, channels = data[4:8]
    rate, samples = struct.unpack_from(">II", data, 8)
    cutoff = int.from_bytes(data[16:18], "big")
    version, flags = data[18:20]
    if (encoding, block, bits) != (3, 18, 4) or version not in (3, 4) or flags:
        raise Unsupported(f"ADX encoding={encoding}, block={block}, bits={bits}, version={version}, flags={flags} unsupported")
    require(1 <= channels <= 8 and rate > 0 and cutoff < rate // 2,
            "invalid ADX channel count, rate or high-pass cutoff")
    require(24 <= start <= len(data), "truncated ADX header")
    require(data[start - 6:start] == b"(c)CRI", "ADX copyright signature missing")
    history = [(0, 0)] * channels
    base = 20
    if version == 4:
        base = 24 + max(channels, 2) * 4
        require(base <= start - 6, "ADX predictor history is truncated")
        history = [struct.unpack_from(">hh", data, 24 + 4 * ch) for ch in range(channels)]
    loop = None
    if base + 24 <= start - 6:
        loop = dict(zip(("alignment_samples", "loop_type", "loop_count", "start_sample",
                         "start_byte", "end_sample", "end_byte"), struct.unpack_from(">HHIIIII", data, base)))
    a = math.sqrt(2) - math.cos(2 * math.pi * cutoff / rate)
    b = math.sqrt(2) - 1
    c = (a - math.sqrt((a + b) * (a - b))) / b
    return {"data_offset": start, "encoding": encoding, "block_bytes": block,
            "bits": bits, "channels": channels, "sample_rate": rate, "samples": samples,
            "cutoff_hz": cutoff, "version": version, "flags": flags,
            "history": history, "coefficients": [int(c * 8192), int(-c * c * 4096)],
            "loop": loop, "header_hex": data[:start].hex()}


NIBBLES = tuple(tuple((v if v < 8 else v - 16) for v in (b >> 4, b & 15)) for b in range(256))


def decode_adx(movie, stream, source, target):
    """ADX type-3 ADPCM, including v4 initial history, +1 scale, and final sample trim."""
    with source.open("rb") as file, mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as data:
        h = adx_header(data)
        nch, count, rate = h["channels"], h["samples"], h["sample_rate"]
        for fieldname, val in (("sampling_rate", rate), ("num_channels", nch), ("total_samples", count)):
            if stream.header.get(fieldname, val) != val:
                movie.warn(f"{stream.key}: {fieldname} mismatch; using ADX header")
        history = [list(pair) for pair in h["history"]]
        c1, c2 = h["coefficients"]
        pos, written, groups = h["data_offset"], 0, 0
        pcm = array.array("h")
        eof = None
        with wave.open(str(target), "wb") as wav:
            wav.setnchannels(nch)
            wav.setsampwidth(2)
            wav.setframerate(rate)
            while pos + 2 <= len(data):
                if data[pos] & 128:
                    if pos + 4 > len(data):
                        movie.warn(f"{stream.key}: truncated ADX end marker")
                        break
                    code, extra = struct.unpack_from(">HH", data, pos)
                    eof = {"offset": pos, "code": code, "following_bytes": extra,
                           "hex": data[pos:min(pos + 4 + extra, len(data))].hex()}
                    if code != 0x8001 or pos + 4 + extra != len(data):
                        movie.warn(f"{stream.key}: unusual ADX end marker/trailing bytes")
                    pos = min(pos + 4 + extra, len(data))
                    break
                if pos + 18 * nch > len(data):
                    movie.warn(f"{stream.key}: incomplete ADX channel group at {pos}; stopped")
                    break
                decoded = []
                for ch in range(nch):
                    offset = pos + ch * 18
                    rawscale = int.from_bytes(data[offset:offset + 2], "big")
                    if rawscale >= 0x8000:
                        movie.warn(f"{stream.key}: invalid ADX scale at {offset}; zero residuals used for this damaged block")
                        rawscale = 0
                        block_data = bytes(16)
                    else:
                        block_data = data[offset + 2:offset + 18]
                    scale = rawscale + 1
                    s1, s2 = history[ch]
                    channel = []
                    for byte in block_data:
                        for nibble in NIBBLES[byte]:
                            predictor = ((c1 * s1) >> 12) + ((c2 * s2) >> 12) if h["version"] == 3 else (c1 * s1 + c2 * s2) >> 12
                            sample = nibble * scale + predictor
                            sample = -32768 if sample < -32768 else 32767 if sample > 32767 else sample
                            s2, s1 = s1, sample
                            channel.append(sample)
                    history[ch] = [s1, s2]
                    decoded.append(channel)
                take = min(32, max(0, count - written))
                for i in range(take):
                    pcm.extend(channel[i] for channel in decoded)
                written += take
                groups += 1
                pos += 18 * nch
                if len(pcm) >= 65536:
                    if sys.byteorder != "little":
                        pcm.byteswap()
                    wav.writeframesraw(pcm.tobytes())
                    pcm = array.array("h")
            if sys.byteorder != "little":
                pcm.byteswap()
            wav.writeframesraw(pcm.tobytes())
        if written != count:
            movie.warn(f"{stream.key}: recovered {written} of {count} ADX samples")
        if eof is None:
            movie.warn(f"{stream.key}: no complete ADX end marker")
        if pos < len(data):
            h["unparsed_tail_hex"] = data[pos:].hex()
        h.update({"decoded_samples": written, "decoded_block_groups": groups,
                  "discarded_final_block_samples": groups * 32 - written, "end_marker": eof})
        stream.details = {"codec": "ADX", **h}
        return written


def subtitles(movie, stream):
    cues = []
    for chunk in stream.chunks:
        data = movie.payload(chunk)
        pos = 0
        while pos < len(data):
            if pos + 20 > len(data):
                movie.warn(f"truncated subtitle record at {chunk.payload + pos}")
                movie.unresolved.append({"offset": chunk.payload + pos, "subtitle_hex": data[pos:].hex()})
                break
            language, unit, start, duration, size = struct.unpack_from("<5I", data, pos)
            if not unit or pos + 20 + size > len(data):
                movie.warn(f"malformed subtitle at {chunk.payload + pos}; remaining chunk retained in audit")
                movie.unresolved.append({"offset": chunk.payload + pos, "subtitle_hex": data[pos:].hex()})
                break
            raw = data[pos + 20:pos + 20 + size]
            text_bytes = raw.rstrip(b"\0")
            try:
                text = text_bytes.decode("utf-8")
            except UnicodeDecodeError:
                text = text_bytes.decode("utf-8", "replace")
                movie.warn(f"non-UTF-8 subtitle at {chunk.payload + pos}; original bytes retained")
            cues.append({"language_id": language, "time_unit": unit, "start": start,
                         "duration": duration, "text": text, "raw_hex": raw.hex(),
                         "terminator_bytes": len(raw) - len(text_bytes), "offset": chunk.payload + pos})
            pos += 20 + size
    stream.details = {"codec": "SBT UTF-8", "cues": cues,
                      "languages": sorted({c["language_id"] for c in cues})}
    return cues


def subtitle_clock(ticks, unit):
    ms = (ticks * 1000 + unit // 2) // unit
    hours, ms = divmod(ms, 3600000)
    minutes, ms = divmod(ms, 60000)
    seconds, ms = divmod(ms, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{ms:03}"


def command(args):
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                            encoding="utf-8", errors="replace")
    if result.returncode:
        raise FormatError(f"{Path(args[0]).name} failed ({result.returncode}): {result.stderr[-6000:]}")
    return result


def convert(input_file, output_file, ffmpeg="ffmpeg", ffprobe="ffprobe", *, verbose=False):
    source, output = Path(input_file), Path(output_file)
    require(source.resolve() != output.resolve(), "input and output paths must differ")
    require(not output.exists() or not os.path.samefile(source, output), "output aliases input")
    movie = Movie(source)
    try:
        # No output or temporary file is created until format identification succeeds.
        movie.parse()
        require(any(s.tag == "@SFV" and s.chunks for s in movie.streams.values()), "no recoverable video stream")
        for program in (ffmpeg, ffprobe):
            require(shutil.which(program), f"required executable is missing: {program}")
        require(output.parent.is_dir(), "output parent directory does not exist")
        with tempfile.TemporaryDirectory(prefix=".cri-usm-", dir=output.parent) as temp:
            tmp = Path(temp)
            videos, audios, caption_files = [], [], []
            for s in sorted(movie.streams.values(), key=lambda x: (x.tag, x.channel)):
                if not s.chunks:
                    continue
                if s.tag == "@SFV":
                    path = tmp / f"video-{s.channel}.m1v"
                    movie.extract(s, path)
                    try:
                        rate = inspect_video(movie, s, path)
                    except Unsupported:
                        raise
                    except (FormatError, ValueError) as exc:
                        movie.warn(f"{s.key}: damaged video stream cannot be decoded: {exc}")
                        continue
                    videos.append((s, path, rate))
                elif s.tag == "@SFA":
                    path = tmp / f"audio-{s.channel}.adx"
                    movie.extract(s, path)
                    # Check all audio formats before spending time decoding video.
                    try:
                        with path.open("rb") as file:
                            adx_header(file.read(65540))
                    except Unsupported:
                        raise
                    except FormatError as exc:
                        movie.warn(f"{s.key}: damaged audio stream cannot be decoded: {exc}")
                        continue
                    audios.append((s, path, tmp / f"audio-{s.channel}.wav"))
                elif s.tag == "@SBT":
                    cues = subtitles(movie, s)
                    if not verbose:
                        continue
                    by_language = defaultdict(list)
                    for cue in cues:
                        by_language[cue["language_id"]].append(cue)
                    for language, cues in sorted(by_language.items()):
                        name = f"sbt{s.channel}.language{language}.srt"
                        path = tmp / name
                        entries = []
                        for i, cue in enumerate(sorted(cues, key=lambda c: Fraction(c["start"], c["time_unit"])), 1):
                            start = subtitle_clock(cue["start"], cue["time_unit"])
                            stop = subtitle_clock(cue["start"] + cue["duration"], cue["time_unit"])
                            entries.append(f"{i}\n{start} --> {stop}\n{cue['text']}\n")
                        path.write_text("\n".join(entries), encoding="utf-8")
                        caption_files.append((path, output.with_name(output.name + "." + name)))
            require(videos, "no video stream with recoverable decoder parameters")
            recovered_audio = []
            for s, adx, wav in audios:
                print(f"Decoding {s.key} ADX audio...", file=sys.stderr, flush=True)
                if decode_adx(movie, s, adx, wav):
                    recovered_audio.append((s, adx, wav))
                else:
                    movie.warn(f"{s.key}: no decoded audio samples; omitted empty track")
            audios = recovered_audio
            args = [ffmpeg, "-hide_banner", "-v", "error", "-nostdin", "-y"]
            for s, path, rate in videos:
                args += ["-threads", "4", "-f", "mpegvideo", "-r", str(rate), "-i", str(path)]
            for s, _, path in audios:
                args += ["-f", "wav", "-i", str(path)]
            for i in range(len(videos)):
                args += ["-map", f"{i}:v:0"]
            for i in range(len(audios)):
                args += ["-map", f"{len(videos) + i}:a:0"]
            for i, (s, _, _) in enumerate(audios):
                title = s.directory.get("filename", s.key)
                args += [f"-metadata:s:a:{i}", f"title={title}"]
            result_path = tmp / "result.avi"
            args += ["-c:v", "ffv1", "-level", "3", "-slicecrc", "1", "-threads", "4",
                     "-fps_mode", "passthrough", "-c:a", "pcm_s16le", "-f", "avi", str(result_path)]
            print("Encoding lossless FFV1 video and PCM audio to AVI...", file=sys.stderr, flush=True)
            result = command(args)
            if result.stderr.strip():
                movie.warn("FFmpeg diagnostics: " + result.stderr.strip())
            info = json.loads(command([ffprobe, "-v", "error", "-count_frames", "-show_streams",
                                       "-show_format", "-of", "json", str(result_path)]).stdout)
            actual_video = [s for s in info["streams"] if s["codec_type"] == "video"]
            actual_audio = [s for s in info["streams"] if s["codec_type"] == "audio"]
            require(len(actual_video) == len(videos) and len(actual_audio) == len(audios), "output lost streams")
            for (s, _, _), got in zip(videos, actual_video):
                n = int(got.get("nb_read_frames", 0))
                require(n > 0, "output has no decoded frames")
                if n != s.details["picture_headers"]:
                    movie.warn(f"{s.key}: FFmpeg recovered {n} of {s.details['picture_headers']} pictures")
            for (s, _, _), got in zip(audios, actual_audio):
                require(int(got.get("sample_rate", 0)) == s.details["sample_rate"] and
                        got.get("channels") == s.details["channels"], "output changed audio format")
                require(int(got.get("nb_frames", 0)) == s.details["decoded_samples"],
                        f"output audio sample count mismatch for {s.key}")
            audit = movie.audit()
            info["format"]["filename"] = str(output)
            audit["output"] = info
            audit["subtitle_sidecars"] = [dst.name for _, dst in caption_files]
            artifacts = []
            if verbose:
                report = tmp / "audit.json"
                report.write_text(json.dumps(audit, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
                artifacts = caption_files + [(report, output.with_name(output.name + ".json"))]
            # Commit only finalized, readable artifacts. Failures before this point leave the destination untouched.
            artifacts.append((result_path, output))
            for _, dst in artifacts:
                require(dst.resolve() != source.resolve() and
                        (not dst.exists() or not os.path.samefile(source, dst)),
                        "an output sidecar would overwrite the input")
            for src, dst in artifacts:
                readable(src)
                os.replace(src, dst)
            for warning in movie.warnings:
                print("Warning: " + warning, file=sys.stderr)
            extras = f", {len(caption_files)} subtitle sidecars" if verbose else ""
            print(f"Created {output} ({len(videos)} video, {len(audios)} audio{extras})")
            return audit
    finally:
        movie.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputFile", type=Path)
    parser.add_argument("--ffmpeg", default="ffmpeg", help="FFmpeg executable")
    parser.add_argument("--ffprobe", default="ffprobe", help="ffprobe executable")
    parser.add_argument("-verbose", "--verbose", action="store_true",
                        help="also write audit JSON and subtitle SRT sidecars (default: AVI only)")
    args = parser.parse_args()
    try:
        convert(args.inputFile, args.outputFile, args.ffmpeg, args.ffprobe, verbose=args.verbose)
    except (FormatError, OSError, ValueError, struct.error) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

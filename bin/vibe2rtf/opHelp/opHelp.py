#!/usr/bin/env python3
# Vibe coded by Codex
"""Convert OPHelp OPH1 help files to RTF."""

from __future__ import annotations

import os
import struct
import sys
from dataclasses import dataclass
from pathlib import Path


class OPHelpError(ValueError):
    pass


CP437_C0 = {
    0x01: "\u263a",
    0x02: "\u263b",
    0x03: "\u2665",
    0x04: "\u2666",
    0x05: "\u2663",
    0x06: "\u2660",
    0x07: "\u2022",
    0x08: "\u25d8",
    0x0B: "\u2642",
    0x0C: "\u2640",
    0x0E: "\u266b",
    0x0F: "\u263c",
    0x10: "\u25ba",
    0x11: "\u25c4",
    0x12: "\u2195",
    0x13: "\u203c",
    0x14: "\u00b6",
    0x15: "\u00a7",
    0x16: "\u25ac",
    0x17: "\u21a8",
    0x18: "\u2191",
    0x19: "\u2193",
    0x1A: "\u2192",
    0x1B: "\u2190",
    0x1C: "\u221f",
    0x1D: "\u2194",
    0x1E: "\u25b2",
    0x1F: "\u25bc",
}


@dataclass
class Topic:
    context_id: int
    title: str
    title_flag: int
    compressed_offset: int
    compressed_length: int
    body: bytes


@dataclass
class OPHelpFile:
    path: Path
    variant: str
    context_count: int
    index_values: tuple[int, int, int]
    char_table: bytes
    contents_ids: list[int]
    title_flags: dict[int, int]
    titles: dict[int, str]
    topics: dict[int, Topic]
    repaired_spans: list[str]


def u16(data: bytes, off: int) -> int:
    return struct.unpack_from("<H", data, off)[0]


def u32(data: bytes, off: int) -> int:
    return struct.unpack_from("<I", data, off)[0]


def decode_inverted_text(raw: bytes) -> str:
    return bytes((0xFF - b) for b in raw).decode("cp437")


def parse_titles(
    data: bytes,
    count: int,
    table_offset: int,
    entry_size: int,
    blob_offset: int,
    blob_length: int,
) -> tuple[dict[int, str], dict[int, int]]:
    if blob_offset + blob_length > len(data):
        raise OPHelpError("title string blob extends past end of file")

    titles: dict[int, str] = {}
    flags: dict[int, int] = {}
    sentinel = 0xFFFF

    for index in range(count):
        off = u16(data, table_offset + index * entry_size) if entry_size == 2 else u32(data, table_offset + index * entry_size)
        if off == sentinel:
            continue
        if off >= blob_length:
            raise OPHelpError(f"title offset for context {index + 1} is outside the title blob")
        pos = blob_offset + off
        marker = data[pos]
        length = 0x7F - (marker & 0x7F)
        flag = marker >> 7
        if length < 0 or pos + 1 + length > blob_offset + blob_length:
            raise OPHelpError(f"title for context {index + 1} extends outside the title blob")
        titles[index + 1] = decode_inverted_text(data[pos + 1 : pos + 1 + length])
        flags[index + 1] = flag

    return titles, flags


def decode_topic(data: bytes, char_table: bytes) -> bytes:
    nibbles: list[int] = []
    for byte in data:
        nibbles.append(byte & 0x0F)
        nibbles.append(byte >> 4)

    out = bytearray()
    i = 0
    while i < len(nibbles):
        code = nibbles[i]
        i += 1
        if code == 0x0F:
            if i + 1 >= len(nibbles):
                raise OPHelpError("literal escape at end of compressed topic")
            lo = nibbles[i]
            hi = nibbles[i + 1]
            i += 2
            out.append((hi << 4) | lo)
        else:
            out.append(char_table[code])

    last_nul = out.rfind(0)
    if last_nul < 0:
        raise OPHelpError("decompressed topic has no terminating NUL")
    if len(out) - last_nul > 2:
        raise OPHelpError("decompressed topic has more than one padding byte after terminator")
    return bytes(out[:last_nul])


def read_entries(
    data: bytes,
    count: int,
    offset: int,
    entry_size: int,
) -> tuple[list[tuple[int, int]], int]:
    entries: list[tuple[int, int]] = []
    end = offset + count * entry_size
    if end > len(data):
        raise OPHelpError("topic record table extends past end of file")
    for i in range(count):
        pos = offset + i * entry_size
        if entry_size == 6:
            start, length = struct.unpack_from("<IH", data, pos)
            sentinel = (0xFFFFFFFF, 0xFFFF)
        else:
            start, length = struct.unpack_from("<II", data, pos)
            sentinel = (0xFFFFFFFF, 0xFFFFFFFF)
        if (start, length) == sentinel:
            entries.append((start, length))
            continue
        if length == 0 or start >= len(data) or start + length > len(data):
            raise OPHelpError(f"topic record {i + 1} points outside the file")
        entries.append((start, length))
    return entries, end


def adjust_spans(entries: list[tuple[int, int]], table_end: int, file_size: int) -> tuple[dict[int, tuple[int, int]], list[str]]:
    spans = [
        {"context": i + 1, "start": start, "length": length}
        for i, (start, length) in enumerate(entries)
        if start != 0xFFFFFFFF
    ]
    spans.sort(key=lambda item: (item["start"], item["context"]))
    repaired: list[str] = []

    if not spans:
        if table_end != file_size:
            raise OPHelpError("file has no topics but has trailing bytes")
        return {}, repaired

    if spans[0]["start"] != table_end:
        raise OPHelpError("first topic does not start immediately after the record table")

    for idx in range(1, len(spans)):
        prev_end = spans[idx - 1]["start"] + spans[idx - 1]["length"]
        cur_start = spans[idx]["start"]
        if prev_end == cur_start:
            continue

        next_start = spans[idx + 1]["start"] if idx + 1 < len(spans) else file_size
        cur_end = spans[idx]["start"] + spans[idx]["length"]
        gap = cur_start - prev_end
        overlap = cur_end - next_start
        if gap > 0 and overlap == gap:
            spans[idx]["start"] -= gap
            repaired.append(
                f"context {spans[idx]['context']}: shifted compressed start back {gap} bytes "
                f"to balance preceding gap and following overlap"
            )
            continue

        raise OPHelpError(
            f"topic data is not contiguous near context {spans[idx]['context']}"
        )

    for idx in range(1, len(spans)):
        if spans[idx - 1]["start"] + spans[idx - 1]["length"] != spans[idx]["start"]:
            raise OPHelpError("topic data remains non-contiguous after span adjustment")
    if spans[-1]["start"] + spans[-1]["length"] != file_size:
        raise OPHelpError("last topic does not end at end of file")

    return {
        item["context"]: (item["start"], item["length"])
        for item in spans
    }, repaired


def parse_ophelp(path: Path) -> OPHelpFile:
    data = path.read_bytes()
    if len(data) < 0x22 or data[:4] != b"OPH1":
        raise OPHelpError("missing OPH1 signature")

    repaired: list[str] = []

    # Standard OPH1 files use 16-bit counts and title offsets.
    count16, index0, contents16, title_len16, meta0, meta1, meta2 = struct.unpack_from("<7H", data, 4)
    normal_title_table = 0x22
    normal_title_blob = normal_title_table + count16 * 2
    normal_ids = normal_title_blob + title_len16
    normal_records = normal_ids + contents16 * 2

    if (
        count16 > 0
        and not (index0 == 0 and title_len16 == 0)
        and normal_title_blob <= len(data)
        and normal_records <= len(data)
        and normal_records + count16 * 6 <= len(data)
    ):
        variant = "16-bit tables"
        context_count = count16
        contents_count = contents16
        title_table_offset = normal_title_table
        title_entry_size = 2
        title_blob_offset = normal_title_blob
        title_blob_length = title_len16
        ids_offset = normal_ids
        id_size = 2
        records_offset = normal_records
        record_size = 6
        char_table = data[0x12:0x22]
        index_values = (index0, meta0, meta1 << 16 | meta2)
    else:
        if len(data) < 0x2A:
            raise OPHelpError("file is too short for the 32-bit OPH1 header")
        context_count = u32(data, 4)
        index0 = u32(data, 8)
        contents_count = u32(data, 12)
        title_blob_length = u32(data, 16)
        meta0, meta1, meta2 = struct.unpack_from("<HHH", data, 20)
        if context_count <= 0 or context_count > 100000:
            raise OPHelpError("invalid 32-bit context count")
        variant = "32-bit tables"
        title_table_offset = 0x2A
        title_entry_size = 4
        title_blob_offset = title_table_offset + context_count * 4
        ids_offset = title_blob_offset + title_blob_length
        id_size = 4
        records_offset = ids_offset + contents_count * 4
        record_size = 8
        char_table = data[0x1A:0x2A]
        index_values = (index0, meta0, meta1 << 16 | meta2)
        if records_offset + context_count * record_size > len(data):
            raise OPHelpError("32-bit OPH1 tables extend past end of file")

    if len(char_table) != 16:
        raise OPHelpError("character table is not 16 bytes")

    titles, flags = parse_titles(
        data,
        context_count,
        title_table_offset,
        title_entry_size,
        title_blob_offset,
        title_blob_length,
    )

    ids_end = ids_offset + contents_count * id_size
    if ids_end > len(data):
        raise OPHelpError("contents id table extends past end of file")
    contents_ids = [
        u16(data, ids_offset + i * id_size) if id_size == 2 else u32(data, ids_offset + i * id_size)
        for i in range(contents_count)
    ]
    for cid in contents_ids:
        if cid < 1 or cid > context_count:
            raise OPHelpError(f"contents id {cid} is outside the context range")

    entries, table_end = read_entries(data, context_count, records_offset, record_size)
    adjusted_spans, repaired = adjust_spans(entries, table_end, len(data))

    topics: dict[int, Topic] = {}
    for context_id, (start, length) in adjusted_spans.items():
        body = decode_topic(data[start : start + length], char_table)
        topics[context_id] = Topic(
            context_id=context_id,
            title=titles.get(context_id, f"Topic {context_id}"),
            title_flag=flags.get(context_id, 0),
            compressed_offset=start,
            compressed_length=length,
            body=body,
        )

    return OPHelpFile(
        path=path,
        variant=variant,
        context_count=context_count,
        index_values=index_values,
        char_table=char_table,
        contents_ids=contents_ids,
        title_flags=flags,
        titles=titles,
        topics=topics,
        repaired_spans=repaired,
    )


def rtf_text(text: str) -> str:
    parts: list[str] = []
    for ch in text:
        code = ord(ch)
        if ch == "\\":
            parts.append(r"\\")
        elif ch == "{":
            parts.append(r"\{")
        elif ch == "}":
            parts.append(r"\}")
        elif ch == "\t":
            parts.append(r"\tab ")
        elif 0x20 <= code <= 0x7E:
            parts.append(ch)
        else:
            signed = code if code < 0x8000 else code - 0x10000
            parts.append(rf"\u{signed}?")
    return "".join(parts)


def byte_to_text(byte: int) -> str:
    if byte in CP437_C0:
        return CP437_C0[byte]
    if byte < 32:
        return ""
    return bytes([byte]).decode("cp437")


def bookmark(context_id: int) -> str:
    return "toc" if context_id == 0 else f"topic_{context_id}"


def rtf_hyperlink(target: int, text: str) -> str:
    return (
        r'{\field{\*\fldinst HYPERLINK \\l "'
        + bookmark(target)
        + r'"}{\fldrslt{\ul\cf1 '
        + rtf_text(text)
        + r"}}}"
    )


def render_body(body: bytes) -> str:
    out: list[str] = []
    active: dict[int, bool] = {1: False, 2: False, 3: False, 5: False}
    i = 0
    while i < len(body):
        byte = body[i]

        if byte in (1, 2, 3, 5):
            if active[byte]:
                if byte in (1, 2):
                    out.append(r"\b0 ")
                elif byte == 3:
                    out.append(r"\i0 ")
                else:
                    out.append(r"\ul0 ")
            else:
                if byte in (1, 2):
                    out.append(r"\b ")
                elif byte == 3:
                    out.append(r"\i ")
                else:
                    out.append(r"\ul ")
            active[byte] = not active[byte]
            i += 1
            continue

        if byte == 4:
            if i + 3 >= len(body):
                raise OPHelpError("malformed hyperlink control")
            target = body[i + 1] | (body[i + 2] << 8)
            j = i + 3
            prefix = bytearray()
            while j < len(body) and body[j] != 5:
                prefix.append(body[j])
                j += 1
            if j >= len(body):
                raise OPHelpError("hyperlink control has no text delimiter")
            if prefix:
                out.append("".join(rtf_text(byte_to_text(b)) for b in prefix))
            j += 1
            link_bytes = bytearray()
            while j < len(body) and body[j] != 5:
                link_bytes.append(body[j])
                j += 1
            if j >= len(body):
                raise OPHelpError("unterminated hyperlink text")
            text = "".join(byte_to_text(b) for b in link_bytes)
            out.append(rtf_hyperlink(target, text))
            i = j + 1
            continue

        if byte == 0:
            raise OPHelpError(f"unexpected control byte 0x{byte:02x}")

        if byte == 13:
            out.append(r"\line " + "\n")
        elif byte == 10:
            pass
        elif byte == 9:
            out.append(r"\tab ")
        elif byte in (11, 12):
            out.append(r"\line " + "\n")
        else:
            out.append(rtf_text(byte_to_text(byte)))
        i += 1

    for byte, is_active in active.items():
        if is_active:
            if byte in (1, 2):
                out.append(r"\b0 ")
            elif byte == 3:
                out.append(r"\i0 ")
            else:
                out.append(r"\ul0 ")
    return "".join(out)


def ordered_topics(doc: OPHelpFile) -> list[Topic]:
    seen: set[int] = set()
    ordered: list[Topic] = []
    for cid in doc.contents_ids:
        topic = doc.topics.get(cid)
        if topic and cid not in seen:
            ordered.append(topic)
            seen.add(cid)
    for cid in sorted(doc.topics):
        if cid not in seen:
            ordered.append(doc.topics[cid])
            seen.add(cid)
    return ordered


def render_rtf(doc: OPHelpFile) -> str:
    parts: list[str] = [
        r"{\rtf1\ansi\ansicpg437\uc1\deff0",
        r"{\fonttbl{\f0\fmodern Courier New;}{\f1\fswiss Arial;}}",
        r"{\colortbl;\red0\green0\blue180;}",
        r"{\*\generator opHelp.py;}",
        "\n",
        r"{\*\bkmkstart toc}",
        r"\f1\fs32\b Table of Contents\b0",
        r"{\*\bkmkend toc}",
        r"\par",
        r"\fs20",
    ]

    topics = ordered_topics(doc)
    for topic in topics:
        parts.append(rtf_hyperlink(topic.context_id, topic.title))
        parts.append(r"\par" + "\n")

    parts.append(r"\page" + "\n")

    for topic in topics:
        name = bookmark(topic.context_id)
        parts.append(rf"{{\*\bkmkstart {name}}}")
        parts.append(r"\f1\fs28\b ")
        parts.append(rtf_text(topic.title))
        parts.append(rf"{{\*\bkmkend {name}}}")
        parts.append(r"\b0\par" + "\n")
        parts.append(r"\f0\fs20 ")
        parts.append(render_body(topic.body))
        parts.append(r"\par\page" + "\n")

    parts.append("}\n")
    return "".join(parts)


def convert(input_file: Path, output_file: Path) -> None:
    doc = parse_ophelp(input_file)
    rtf = render_rtf(doc)
    tmp = output_file.with_name(output_file.name + ".tmp")
    tmp.write_text(rtf, encoding="ascii")
    os.chmod(tmp, 0o664)
    os.replace(tmp, output_file)
    os.chmod(output_file, 0o664)


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: opHelp.py <inputFile> <outputFile>", file=sys.stderr)
        return 2

    input_file = Path(argv[1])
    output_file = Path(argv[2])
    tmp = output_file.with_name(output_file.name + ".tmp")
    if tmp.exists():
        tmp.unlink()
    try:
        convert(input_file, output_file)
    except Exception as exc:
        if tmp.exists():
            tmp.unlink()
        if output_file.exists():
            output_file.unlink()
        print(f"opHelp.py: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

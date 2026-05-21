#!/usr/bin/env python3
# Vibe coded by Codex
"""Convert Microsoft Advisor / QuickHelp databases to RTF."""

from __future__ import annotations

import os
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path


class AdvisorError(Exception):
    pass


def u16(data: bytes, off: int) -> int:
    return struct.unpack_from("<H", data, off)[0]


def u32(data: bytes, off: int) -> int:
    return struct.unpack_from("<I", data, off)[0]


def rtf_escape_text(raw: bytes) -> str:
    text = raw.decode("cp437", errors="replace")
    out: list[str] = []
    for ch in text:
        cp = ord(ch)
        if ch == "\\":
            out.append(r"\\")
        elif ch == "{":
            out.append(r"\{")
        elif ch == "}":
            out.append(r"\}")
        elif ch == "\t":
            out.append(r"\tab ")
        elif ch in "\r\n":
            out.append(r"\line ")
        elif cp < 32:
            pass
        elif cp < 128:
            out.append(ch)
        else:
            signed = cp if cp < 32768 else cp - 65536
            out.append(rf"\u{signed}?")
    return "".join(out)


def rtf_escape_ascii(text: str) -> str:
    return rtf_escape_text(text.encode("ascii", errors="replace"))


def clean_visible(raw: bytes) -> bytes:
    result = bytearray()
    for byte in raw:
        if byte in (0x10, 0x11):
            continue
        if byte == 0x09 or byte >= 0x20:
            result.append(byte)
    return bytes(result).rstrip()


@dataclass
class LineRecord:
    text: bytes
    attrs: bytes


@dataclass
class Topic:
    index: int
    start: int
    end: int
    decompressed_length: int
    compact_length: int
    huffman_bits_consumed: int
    lines: list[LineRecord]
    commands: list[tuple[bytes, bytes]] = field(default_factory=list)

    def title(self, contexts: list[str]) -> str:
        for key, value in self.commands:
            if key == b"n" and value:
                return value.decode("cp437", errors="replace")
        for ctx in contexts:
            if not ctx.startswith((".", ":", "h.")):
                return ctx
        return f"Topic {self.index + 1}"


@dataclass
class Segment:
    base: int
    size: int
    database_name: str
    attributes: int
    control_char: int
    topic_count: int
    context_count: int
    display_width: int
    topic_index_offset: int
    context_strings_offset: int
    context_map_offset: int
    keywords_offset: int
    huffman_tree_offset: int
    topic_text_offset: int
    declared_size: int
    pre_index_words: tuple[int, int, int]
    contexts: list[str]
    context_map: list[int]
    keywords: list[bytes]
    huffman_tree: list[int]
    topic_offsets: list[int]
    topics: list[Topic]


class BitReader:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.bit_pos = 0

    def read_bit(self) -> int | None:
        if self.bit_pos >= len(self.data) * 8:
            return None
        byte = self.data[self.bit_pos // 8]
        bit = (byte >> (7 - (self.bit_pos & 7))) & 1
        self.bit_pos += 1
        return bit


class AdvisorParser:
    def __init__(self, data: bytes) -> None:
        self.data = data

    def parse(self) -> list[Segment]:
        if not self.data.startswith(b"LN\x02\x00"):
            raise AdvisorError("not a Microsoft Advisor/QuickHelp database")
        segments: list[Segment] = []
        base = 0
        while base < len(self.data):
            seg = self.parse_segment(base)
            segments.append(seg)
            base += seg.size
            if base == len(self.data):
                break
            if self.data[base : base + 4] != b"LN\x02\x00":
                raise AdvisorError(
                    f"unparsed trailing bytes at 0x{base:x}; next segment signature missing"
                )
        return segments

    def parse_segment(self, base: int) -> Segment:
        data = self.data
        if base + 70 > len(data):
            raise AdvisorError(f"segment at 0x{base:x} is shorter than the fixed header")
        if data[base : base + 2] != b"LN":
            raise AdvisorError(f"segment at 0x{base:x} has no LN signature")
        if u16(data, base + 2) != 2:
            raise AdvisorError(f"segment at 0x{base:x} has unsupported version")
        if u16(data, base + 6) != 0x3A:
            raise AdvisorError(f"segment at 0x{base:x} has unexpected header data offset")

        attributes = u16(data, base + 4)
        control_char = data[base + 6]
        topic_count = u16(data, base + 8)
        context_count = u16(data, base + 10)
        display_width = data[base + 12]
        name = data[base + 16 : base + 32].split(b"\0", 1)[0].decode(
            "ascii", errors="replace"
        )
        topic_index_offset = u32(data, base + 0x22)
        context_strings_offset = u32(data, base + 0x26)
        context_map_offset = u32(data, base + 0x2A)
        keywords_offset = u32(data, base + 0x2E)
        huffman_tree_offset = u32(data, base + 0x32)
        topic_text_offset = u32(data, base + 0x36)
        declared_size = u32(data, base + 0x42)

        offsets = [
            topic_index_offset,
            context_strings_offset,
            context_map_offset,
            topic_text_offset,
        ]
        if keywords_offset:
            offsets.append(keywords_offset)
        if huffman_tree_offset:
            offsets.append(huffman_tree_offset)
        if min(offsets) < 0x46:
            raise AdvisorError(f"{name}: section offset before fixed header")
        if max(offsets) > len(data) - base:
            raise AdvisorError(f"{name}: section offset beyond available file bytes")
        ordered = [topic_index_offset, context_strings_offset, context_map_offset]
        if keywords_offset:
            ordered.append(keywords_offset)
        if huffman_tree_offset:
            ordered.append(huffman_tree_offset)
        ordered.append(topic_text_offset)
        if ordered != sorted(ordered):
            raise AdvisorError(f"{name}: section offsets are not monotonic")

        index_bytes = (topic_count + 1) * 4
        if topic_index_offset + index_bytes != context_strings_offset:
            raise AdvisorError(f"{name}: topic index size does not match topic count")
        topic_offsets = list(
            struct.unpack_from(
                f"<{topic_count + 1}I", data, base + topic_index_offset
            )
        )
        if topic_offsets != sorted(topic_offsets):
            raise AdvisorError(f"{name}: topic offsets are not monotonic")
        if topic_offsets[0] != topic_text_offset:
            raise AdvisorError(f"{name}: first topic offset does not match topic text")
        segment_size = topic_offsets[-1]
        if segment_size > len(data) - base:
            raise AdvisorError(
                f"{name}: topic data declares {segment_size} bytes, "
                f"but only {len(data) - base} are present"
            )
        if declared_size and declared_size != segment_size:
            raise AdvisorError(
                f"{name}: declared database size {declared_size} != topic end {segment_size}"
            )

        raw_contexts = data[base + context_strings_offset : base + context_map_offset]
        contexts_b = raw_contexts.split(b"\0")
        if contexts_b and contexts_b[-1] == b"":
            contexts_b.pop()
        if len(contexts_b) != context_count:
            raise AdvisorError(
                f"{name}: context string count {len(contexts_b)} != {context_count}"
            )
        contexts = [c.decode("cp437", errors="replace") for c in contexts_b]
        map_size = context_count * 2
        if context_map_offset + map_size > segment_size:
            raise AdvisorError(f"{name}: context map extends beyond segment")
        context_map = list(struct.unpack_from(f"<{context_count}H", data, base + context_map_offset))
        for idx in context_map:
            if idx >= topic_count:
                raise AdvisorError(f"{name}: context map topic index {idx} out of range")

        next_after_map = keywords_offset or huffman_tree_offset or topic_text_offset
        if context_map_offset + map_size > next_after_map:
            raise AdvisorError(f"{name}: context map overlaps the next section")

        keywords: list[bytes] = []
        if keywords_offset:
            end = huffman_tree_offset or topic_text_offset
            pos = base + keywords_offset
            while pos < base + end:
                length = data[pos]
                pos += 1
                if length == 0:
                    if any(data[pos : base + end]):
                        raise AdvisorError(f"{name}: nonzero bytes after keyword terminator")
                    break
                if pos + length > base + end:
                    raise AdvisorError(f"{name}: keyword overruns dictionary section")
                keywords.append(data[pos : pos + length])
                pos += length

        huffman_tree: list[int] = []
        if huffman_tree_offset:
            if (topic_text_offset - huffman_tree_offset) % 2:
                raise AdvisorError(f"{name}: odd-sized Huffman section")
            vals = list(
                struct.unpack_from(
                    f"<{(topic_text_offset - huffman_tree_offset) // 2}H",
                    data,
                    base + huffman_tree_offset,
                )
            )
            if not vals or vals[-1] != 0:
                raise AdvisorError(f"{name}: Huffman tree is not zero-terminated")
            huffman_tree = vals[:-1]
            if len(huffman_tree) % 2 != 1:
                raise AdvisorError(f"{name}: Huffman tree has an even node count")
            self.validate_huffman(name, huffman_tree)

        topics: list[Topic] = []
        for i in range(topic_count):
            start = topic_offsets[i]
            end = topic_offsets[i + 1]
            topics.append(
                self.parse_topic(
                    name,
                    i,
                    data[base + start : base + end],
                    start,
                    end,
                    keywords,
                    huffman_tree,
                )
            )

        pre = (u32(data, base + 0x3A), u32(data, base + 0x3E), u32(data, base + 0x42))
        return Segment(
            base=base,
            size=segment_size,
            database_name=name,
            attributes=attributes,
            control_char=control_char,
            topic_count=topic_count,
            context_count=context_count,
            display_width=display_width,
            topic_index_offset=topic_index_offset,
            context_strings_offset=context_strings_offset,
            context_map_offset=context_map_offset,
            keywords_offset=keywords_offset,
            huffman_tree_offset=huffman_tree_offset,
            topic_text_offset=topic_text_offset,
            declared_size=declared_size,
            pre_index_words=pre,
            contexts=contexts,
            context_map=context_map,
            keywords=keywords,
            huffman_tree=huffman_tree,
            topic_offsets=topic_offsets,
            topics=topics,
        )

    def validate_huffman(self, name: str, tree: list[int]) -> None:
        for i, value in enumerate(tree):
            if value & 0x8000:
                continue
            child0 = value // 2
            child1 = i + 1
            if child0 >= len(tree) or child1 >= len(tree):
                raise AdvisorError(f"{name}: Huffman node {i} points outside the tree")

    def huffman_decode(self, name: str, encoded: bytes, tree: list[int]) -> tuple[bytes, int]:
        reader = BitReader(encoded)
        out = bytearray()
        while True:
            node = 0
            while not (tree[node] & 0x8000):
                bit = reader.read_bit()
                if bit is None:
                    return bytes(out), reader.bit_pos
                node = node + 1 if bit else tree[node] // 2
                if node >= len(tree):
                    raise AdvisorError(f"{name}: Huffman bitstream walked outside tree")
            out.append(tree[node] & 0xFF)

    def expand_keywords(
        self, name: str, compact: bytes, expected_len: int, keywords: list[bytes]
    ) -> tuple[bytes, int]:
        out = bytearray()
        pos = 0
        while len(out) < expected_len:
            if pos >= len(compact):
                raise AdvisorError(f"{name}: compact topic stream ended early")
            byte = compact[pos]
            pos += 1
            if byte < 0x10 or byte > 0x1A:
                out.append(byte)
            elif byte == 0x1A:
                if pos >= len(compact):
                    raise AdvisorError(f"{name}: escape byte at end of compact stream")
                out.append(compact[pos])
                pos += 1
            elif byte == 0x18:
                if pos >= len(compact):
                    raise AdvisorError(f"{name}: space run without count")
                out.extend(b" " * compact[pos])
                pos += 1
            elif byte == 0x19:
                if pos + 1 >= len(compact):
                    raise AdvisorError(f"{name}: byte run without byte/count")
                out.extend(bytes([compact[pos]]) * compact[pos + 1])
                pos += 2
            else:
                if pos >= len(compact):
                    raise AdvisorError(f"{name}: dictionary code without low byte")
                idx = ((byte & 0x03) << 8) | compact[pos]
                pos += 1
                if idx >= len(keywords):
                    raise AdvisorError(f"{name}: dictionary index {idx} out of range")
                out.extend(keywords[idx])
                if byte & 0x04:
                    out.append(0x20)
        return bytes(out[:expected_len]), pos

    def parse_topic(
        self,
        name: str,
        index: int,
        stored: bytes,
        start: int,
        end: int,
        keywords: list[bytes],
        huffman_tree: list[int],
    ) -> Topic:
        if len(stored) < 2:
            raise AdvisorError(f"{name}: topic {index} has no length word")
        expected_len = u16(stored, 0)
        encoded = stored[2:]
        bits = 0
        if huffman_tree:
            compact, bits = self.huffman_decode(name, encoded, huffman_tree)
        else:
            compact = encoded
        expanded, used = self.expand_keywords(
            f"{name} topic {index}", compact, expected_len, keywords
        )
        if not huffman_tree and used != len(compact):
            raise AdvisorError(f"{name}: topic {index} has unused compact bytes")
        lines = self.parse_lines(name, index, expanded)
        commands: list[tuple[bytes, bytes]] = []
        for line in lines:
            if line.text.startswith(b":") and len(line.text) >= 2:
                commands.append((line.text[1:2], line.text[2:]))
        return Topic(index, start, end, expected_len, len(compact), bits, lines, commands)

    def parse_lines(self, name: str, topic_index: int, data: bytes) -> list[LineRecord]:
        lines: list[LineRecord] = []
        pos = 0
        while pos < len(data):
            text_len = data[pos]
            if text_len == 0:
                raise AdvisorError(f"{name}: topic {topic_index} has zero text length")
            if pos + text_len > len(data):
                raise AdvisorError(f"{name}: topic {topic_index} text record overruns")
            text = data[pos + 1 : pos + text_len]
            pos += text_len
            if pos >= len(data):
                raise AdvisorError(f"{name}: topic {topic_index} missing attr length")
            attr_len = data[pos]
            if attr_len == 0:
                raise AdvisorError(f"{name}: topic {topic_index} has zero attr length")
            if pos + attr_len > len(data):
                raise AdvisorError(f"{name}: topic {topic_index} attr record overruns")
            attrs = data[pos + 1 : pos + attr_len]
            pos += attr_len
            lines.append(LineRecord(text=text, attrs=attrs))
        return lines


def contexts_for_topic(seg: Segment, topic_index: int) -> list[str]:
    return [ctx for ctx, mapped in zip(seg.contexts, seg.context_map) if mapped == topic_index]


def build_rtf(segments: list[Segment], source_name: str) -> str:
    out: list[str] = [
        r"{\rtf1\ansi\deff0",
        r"{\fonttbl{\f0 Courier New;}}",
        r"{\colortbl;\red0\green0\blue255;}",
        r"\fs20",
        r"\par\b Table of Contents\b0\par",
    ]
    for si, seg in enumerate(segments):
        out.append(rf"\par\b {rtf_escape_text(seg.database_name.encode('cp437', errors='replace'))}\b0\par")
        for topic in seg.topics:
            bookmark = f"s{si}_t{topic.index}"
            title = topic.title(contexts_for_topic(seg, topic.index))
            out.append(
                r"{\field{\*\fldinst{HYPERLINK \\l "
                + f'"{bookmark}"'
                + r"}}{\fldrslt{\cf1 "
                + rtf_escape_text(title.encode("cp437", errors="replace"))
                + r"}}}\par"
            )
    out.append(r"\page")

    for si, seg in enumerate(segments):
        out.append(rf"\b Database: {rtf_escape_text(seg.database_name.encode('cp437', errors='replace'))}\b0\par")
        for topic in seg.topics:
            bookmark = f"s{si}_t{topic.index}"
            contexts = contexts_for_topic(seg, topic.index)
            title = topic.title(contexts)
            out.append(rf"{{\*\bkmkstart {bookmark}}}{{\*\bkmkend {bookmark}}}")
            out.append(rf"\par\b {rtf_escape_text(title.encode('cp437', errors='replace'))}\b0\par")
            if contexts:
                out.append(r"\i Contexts: " + rtf_escape_text(", ".join(contexts).encode("cp437", errors="replace")) + r"\i0\par")
            for line in topic.lines:
                if line.text.startswith(b":"):
                    continue
                visible = clean_visible(line.text)
                out.append(rtf_escape_text(visible) + r"\par")
            out.append(r"\par")
    out.append("}")
    return "\n".join(out)


def convert(input_file: str, output_file: str) -> None:
    in_path = Path(input_file)
    out_path = Path(output_file)
    data = in_path.read_bytes()
    parser = AdvisorParser(data)
    segments = parser.parse()
    rtf = build_rtf(segments, in_path.name)
    tmp = out_path.with_suffix(out_path.suffix + ".tmp")
    tmp.write_text(rtf, encoding="ascii")
    os.chmod(tmp, 0o664)
    tmp.replace(out_path)
    os.chmod(out_path, 0o664)


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: microsoftAdvisorHelp.py <inputFile> <outputFile>", file=sys.stderr)
        return 2
    try:
        convert(argv[1], argv[2])
        return 0
    except Exception as exc:
        out = Path(argv[2])
        tmp = out.with_suffix(out.suffix + ".tmp")
        try:
            if tmp.exists():
                tmp.unlink()
            if out.exists():
                out.unlink()
        except OSError:
            pass
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

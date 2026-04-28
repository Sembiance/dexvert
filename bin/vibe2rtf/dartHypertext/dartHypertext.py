#!/usr/bin/env python3
# Vibe coded by Codex
"""Convert Dart Hypertext documents to RTF."""

from __future__ import annotations

import os
import sys
import tempfile
from dataclasses import dataclass
from hashlib import sha1
from pathlib import Path


SIGNATURE = b"Compressed file. Use Dart to view.\x1a"
INITIAL_PREFIXES = {
    b"\x15\x00\x01\x00\x00\x00\x00\x00",
    b"\x15\x09\x00\x00\x00\x00\x00\x00",
}
INITIAL_STORED = b"\x00\x80\xf0\x00\x00\x00\x00"
INITIAL_DISTILLED = b"\x00\x83\xf0\x00\x00\x00\x00"
NEXT_STORED = b"\x80\xf0\x00\x00\x00\x00"
NEXT_DISTILLED = b"\x83\xf0\x00\x00\x00\x00"
WINDOW_SIZE = 8192
SCREEN_STYLE_BYTES = set(b"01234567:")
SCREEN_ROW_START_BYTES = {
    0xB3,
    0xB4,
    0xBA,
    0xBB,
    0xBC,
    0xBF,
    0xC0,
    0xC1,
    0xC2,
    0xC3,
    0xC4,
    0xC5,
    0xC8,
    0xC9,
    0xCA,
    0xCB,
    0xCC,
    0xCD,
    0xCE,
    0xD9,
    0xDA,
    0xDB,
    0xDC,
    0xDF,
}


class DartError(ValueError):
    """Raised when the input is not a Dart Hypertext file this converter handles."""


@dataclass(frozen=True)
class BlockInfo:
    offset: int
    method: str
    uncompressed_size: int
    compressed_size: int


class BitReader:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.bit_pos = 0

    def read(self, count: int) -> int:
        if count < 0:
            raise DartError("negative bit count")
        value = 0
        for shift in range(count):
            byte_pos = self.bit_pos >> 3
            if byte_pos >= len(self.data):
                raise DartError("compressed stream ended inside a bit field")
            bit = (self.data[byte_pos] >> (self.bit_pos & 7)) & 1
            value |= bit << shift
            self.bit_pos += 1
        return value


OFFSET_CODES = {
    "000": 0,
    "0100": 1,
    "0010": 2,
    "0011": 3,
    "10000": 4,
    "01100": 5,
    "01010": 6,
    "01110": 7,
    "10001": 8,
    "01101": 9,
    "01011": 10,
    "01111": 11,
    "101000": 12,
    "100100": 13,
    "101100": 14,
    "101010": 15,
    "100110": 16,
    "101110": 17,
    "101001": 18,
    "100101": 19,
    "101101": 20,
    "101011": 21,
    "100111": 22,
    "101111": 23,
    "1100000": 24,
    "1110000": 25,
    "1101000": 26,
    "1100100": 27,
    "1110100": 28,
    "1101100": 29,
    "1100010": 30,
    "1110010": 31,
    "1101010": 32,
    "1100110": 33,
    "1110110": 34,
    "1101110": 35,
    "1100001": 36,
    "1110001": 37,
    "1101001": 38,
    "1100101": 39,
    "1110101": 40,
    "1101101": 41,
    "1100011": 42,
    "1110011": 43,
    "1101011": 44,
    "1100111": 45,
    "1110111": 46,
    "1101111": 47,
    "11110000": 48,
    "11111000": 49,
    "11110100": 50,
    "11111100": 51,
    "11110010": 52,
    "11111010": 53,
    "11110110": 54,
    "11111110": 55,
    "11110001": 56,
    "11111001": 57,
    "11110101": 58,
    "11111101": 59,
    "11110011": 60,
    "11111011": 61,
    "11110111": 62,
    "11111111": 63,
}


def build_offset_trie() -> dict[int, object]:
    root: dict[int, object] = {}
    for bits, value in OFFSET_CODES.items():
        node = root
        for i, ch in enumerate(bits):
            bit = int(ch)
            if i == len(bits) - 1:
                if bit in node:
                    raise AssertionError("duplicate offset prefix")
                node[bit] = value
            else:
                child = node.setdefault(bit, {})
                if not isinstance(child, dict):
                    raise AssertionError("offset prefix collision")
                node = child
    return root


OFFSET_TRIE = build_offset_trie()


def read_offset_high(reader: BitReader) -> int:
    node: object = OFFSET_TRIE
    while isinstance(node, dict):
        bit = reader.read(1)
        if bit not in node:
            raise DartError("invalid copy-offset prefix")
        node = node[bit]
    return int(node)


def low_offset_bit_count(output_len: int) -> int:
    history = 60 + output_len
    if history < 64:
        return 0
    if history < 128:
        return 1
    if history < 256:
        return 2
    if history < 512:
        return 3
    if history < 1024:
        return 4
    if history < 2048:
        return 5
    if history < 4096:
        return 6
    return 7


def decompress_distilled(payload: bytes, expected_size: int) -> bytes:
    reader = BitReader(payload)
    node_count = reader.read(16)
    node_bits = reader.read(8)
    if node_count < 2:
        raise DartError("compressed block has too few Huffman nodes")
    if node_bits < 1 or node_bits > 16:
        raise DartError("compressed block has an invalid Huffman node width")

    table = [reader.read(node_bits) for _ in range(node_count)]
    for value in table:
        if value >= node_count + 315:
            raise DartError("Huffman node references an unsupported code")

    output = bytearray()
    history = bytearray(b" " * WINDOW_SIZE)
    history_pos = 0

    def emit(byte: int) -> None:
        nonlocal history_pos
        if len(output) >= expected_size:
            raise DartError("compressed block expands past its declared size")
        output.append(byte)
        history[history_pos] = byte
        history_pos = (history_pos + 1) & (WINDOW_SIZE - 1)

    def read_code() -> int:
        node_index = node_count - 2
        while True:
            if node_index < 0 or node_index + 1 >= node_count:
                raise DartError("Huffman walk left the node table")
            selected = table[node_index + reader.read(1)]
            if selected < node_count:
                node_index = selected
                continue
            return selected - node_count

    while len(output) < expected_size:
        code = read_code()
        if code <= 0xFF:
            emit(code)
        elif code == 0x100:
            if len(output) != expected_size:
                raise DartError("compressed block ended before its declared size")
            break
        elif 0x101 <= code <= 0x13A:
            copy_len = code - 0xFE
            if len(output) + copy_len > expected_size:
                raise DartError("compressed copy expands past declared block size")
            high = read_offset_high(reader)
            low_bits = low_offset_bit_count(len(output))
            low = reader.read(low_bits) if low_bits else 0
            offset = (high << low_bits) | low
            for _ in range(copy_len):
                byte = history[(history_pos - offset - 1) & (WINDOW_SIZE - 1)]
                emit(byte)
        else:
            raise DartError(f"unsupported compressed data code {code}")

    return bytes(output)


def read_u16le(data: bytes, offset: int) -> int:
    if offset + 2 > len(data):
        raise DartError("truncated 16-bit field")
    return data[offset] | (data[offset + 1] << 8)


def decode_block(method: str, payload: bytes, expected_size: int) -> bytes:
    if method == "stored":
        if len(payload) != expected_size:
            raise DartError("stored block size does not match declared size")
        return payload
    if method == "distilled":
        return decompress_distilled(payload, expected_size)
    raise DartError(f"unsupported block method {method}")


def parse_dart_file(data: bytes) -> tuple[bytes, list[BlockInfo]]:
    if not data.startswith(SIGNATURE):
        raise DartError("missing Dart Hypertext signature")

    pos = len(SIGNATURE)
    if data[pos : pos + 8] not in INITIAL_PREFIXES:
        raise DartError("invalid initial Dart wrapper prefix")
    pos += 8

    blocks: list[BlockInfo] = []
    document = bytearray()
    first = True

    while True:
        if first:
            if pos + 11 > len(data):
                raise DartError("truncated initial block header")
            method_bytes = data[pos : pos + 7]
            pos += 7
            if method_bytes == INITIAL_STORED:
                method = "stored"
            elif method_bytes == INITIAL_DISTILLED:
                method = "distilled"
            else:
                raise DartError("unsupported initial block method")
        else:
            if pos == len(data):
                break
            if pos == len(data) - 2 and data[pos:] == b"\x00\x00":
                break
            if pos + 10 > len(data):
                raise DartError("truncated continuation block header")
            method_bytes = data[pos : pos + 6]
            pos += 6
            if method_bytes == NEXT_STORED:
                method = "stored"
            elif method_bytes == NEXT_DISTILLED:
                method = "distilled"
            else:
                raise DartError("unsupported continuation block method")

        uncompressed_size = read_u16le(data, pos)
        compressed_size = read_u16le(data, pos + 2)
        pos += 4
        if compressed_size == 0 and uncompressed_size == 0:
            break
        if pos + compressed_size > len(data):
            raise DartError("block payload extends beyond end of file")
        payload = data[pos : pos + compressed_size]
        block_offset = pos - (11 if first else 10)
        pos += compressed_size
        decoded = decode_block(method, payload, uncompressed_size)
        if len(decoded) != uncompressed_size:
            raise DartError("decoded block size does not match declared size")
        document.extend(decoded)
        blocks.append(BlockInfo(block_offset, method, uncompressed_size, compressed_size))
        first = False

    if pos != len(data) and not (pos == len(data) - 2 and data[pos:] == b"\x00\x00"):
        raise DartError("unconsumed bytes after final block")
    if not blocks:
        raise DartError("file contains no Dart document blocks")
    return bytes(document), blocks


def rtf_escape_char(ch: str) -> str:
    if ch == "\\":
        return r"\\"
    if ch == "{":
        return r"\{"
    if ch == "}":
        return r"\}"
    code = ord(ch)
    if 0x20 <= code <= 0x7E:
        return ch
    if code > 32767:
        code -= 65536
    return rf"\u{code}?"


def document_to_rtf_body(document: bytes, source_name: str) -> str:
    lines = extract_document_lines(document)
    labels = build_label_map(lines)
    parts: list[str] = []

    for line in lines:
        label = label_for_line(line)
        if label:
            parts.append(rtf_bookmark(labels[label]))
        if line:
            parts.append(render_markup_line(line, labels, source_name))
        parts.append("\\line\n")

    while parts and parts[-1] == "\\line\n":
        parts.pop()
    return "".join(parts)


def extract_document_lines(document: bytes) -> list[bytes]:
    lines: list[bytes] = []
    screen_mode = first_screen_record_offset(document) is not None

    def append_payload(payload: bytes) -> None:
        current = bytearray()
        for byte in payload:
            if byte in (0x00, 0x0A, 0x0D):
                lines.append(bytes(current))
                current.clear()
            elif byte != 0x1A:
                current.append(byte)
        lines.append(bytes(current))

    i = 0
    if screen_mode:
        current = bytearray()
        while i < len(document):
            byte = document[i]
            if is_screen_style_at(document, i, screen_mode):
                if current:
                    lines.append(bytes(current))
                    current.clear()
                i += 1
                continue
            if byte == 0x1A:
                i += 1
                continue
            if byte in (0x00, 0x0A, 0x0D):
                lines.append(bytes(current))
                current.clear()
                i += 1
                continue
            if 0x01 <= byte <= 0x1F:
                if current:
                    lines.append(bytes(current))
                    current.clear()
                i += 1
                continue
            current.append(byte)
            i += 1
        if current:
            lines.append(bytes(current))
    else:
        current = bytearray()
        while i < len(document):
            byte = document[i]
            if byte == 0x1A:
                i += 1
                continue
            if byte == 0x00:
                if current:
                    lines.append(bytes(current))
                    current.clear()
                lines.append(b"")
                i += 1
                continue
            record_len = byte
            if not current and is_length_record_at(document, i):
                if current:
                    lines.append(bytes(current))
                    current.clear()
                i += 1
                append_payload(document[i : i + record_len])
                i += record_len
                continue
            if 0x01 <= byte <= 0x1F:
                if current:
                    lines.append(bytes(current))
                    current.clear()
                i += 1
                continue
            current.append(byte)
            i += 1
        if current:
            lines.append(bytes(current))

    return lines


def render_markup_line(line: bytes, labels: dict[str, str], source_name: str) -> str:
    parts: list[str] = []
    bold = False
    underline = False

    def emit_byte(byte: int, output: list[str]) -> None:
        nonlocal bold, underline
        if byte == 0x09:
            output.append("    ")
        elif 0x01 <= byte <= 0x1F:
            return
        elif byte == 0x60:
            bold = not bold
            output.append(r"\b " if bold else r"\b0 ")
        elif byte == 0x7E:
            underline = not underline
            output.append(r"\ul " if underline else r"\ul0 ")
        elif byte == 0xFF:
            output.append(" ")
        else:
            output.append(rtf_escape_char(bytes([byte]).decode("cp437")))

    def render_span(span: bytes) -> str:
        output: list[str] = []
        for item in span:
            emit_byte(item, output)
        return "".join(output)

    i = 0
    while i < len(line):
        link = find_link_at(line, i, labels, source_name)
        if link:
            end, target_file, bookmark = link
            result = render_span(line[i:end])
            parts.append(rtf_hyperlink(target_file, bookmark, result))
            i = end
            continue
        emit_byte(line[i], parts)
        i += 1

    if underline:
        parts.append(r"\ul0 ")
    if bold:
        parts.append(r"\b0 ")
    return "".join(parts)


def visible_text(data: bytes) -> str:
    chars: list[str] = []
    for byte in data:
        if byte in (0x60, 0x7E, 0x1A) or 0x01 <= byte <= 0x1F:
            continue
        if byte == 0xFF:
            chars.append(" ")
        else:
            chars.append(bytes([byte]).decode("cp437"))
    return "".join(chars)


def label_for_line(line: bytes) -> str | None:
    text = visible_text(line).strip()
    if len(text) > 1 and text.startswith(":"):
        return normalize_label(text[1:])
    return None


def build_label_map(lines: list[bytes]) -> dict[str, str]:
    labels: dict[str, str] = {}
    for line in lines:
        label = label_for_line(line)
        if label and label not in labels:
            labels[label] = bookmark_name(label)
    return labels


def normalize_label(label: str) -> str:
    return " ".join(label.strip().lstrip(":").split()).casefold()


def bookmark_name(label: str) -> str:
    readable = "".join(ch if ch.isalnum() else "_" for ch in label.strip())[:28]
    readable = readable.strip("_") or "label"
    digest = sha1(label.encode("utf-8")).hexdigest()[:10]
    return f"DART_{readable}_{digest}"


def rtf_bookmark(name: str) -> str:
    return r"{\*\bkmkstart " + name + r"}{\*\bkmkend " + name + r"}"


def find_link_at(
    line: bytes, offset: int, labels: dict[str, str], source_name: str
) -> tuple[int, str | None, str | None] | None:
    byte = line[offset]
    if byte == ord('"'):
        end_quote = line.find(b'"', offset + 1)
        if end_quote == -1 or end_quote + 1 >= len(line) or line[end_quote + 1] != ord("*"):
            return None
        target = visible_text(line[offset + 1 : end_quote]).strip()
        target_file, bookmark = classify_link_target(target, labels, source_name, True)
        return end_quote + 2, target_file, bookmark

    if byte == ord("<"):
        end_angle = line.find(b">", offset + 1)
        if end_angle == -1:
            return None
        has_star = end_angle + 1 < len(line) and line[end_angle + 1] == ord("*")
        target = visible_text(line[offset + 1 : end_angle]).strip()
        target_file, bookmark = classify_link_target(target, labels, source_name, has_star)
        if target_file is None and bookmark is None:
            return None
        return end_angle + (2 if has_star else 1), target_file, bookmark

    return None


def classify_link_target(
    target: str, labels: dict[str, str], source_name: str, forced: bool
) -> tuple[str | None, str | None]:
    normalized = normalize_label(target)
    if normalized in labels:
        return None, labels[normalized]

    file_part, label_part = split_file_label(target)
    if file_part:
        if same_dart_name(file_part, source_name):
            if label_part:
                return None, labels.get(normalize_label(label_part), bookmark_name(label_part))
            return None, None
        bookmark = bookmark_name(label_part) if label_part else None
        return file_part, bookmark

    if forced and target:
        return None, labels.get(normalized, bookmark_name(target))
    return None, None


def split_file_label(target: str) -> tuple[str | None, str | None]:
    target = target.strip()
    if not target:
        return None, None
    pieces = target.split(None, 1)
    first = pieces[0]
    if "#" in first or "." in first:
        return first, pieces[1].strip() if len(pieces) > 1 else None
    return None, target


def same_dart_name(left: str, right: str) -> bool:
    return left.casefold() == right.casefold()


def rtf_hyperlink(target_file: str | None, bookmark: str | None, result: str) -> str:
    if target_file:
        instruction = f'HYPERLINK "{rtf_field_escape(target_file)}"'
        if bookmark:
            instruction += f' \\\\l "{rtf_field_escape(bookmark)}"'
    elif bookmark:
        instruction = f'HYPERLINK \\\\l "{rtf_field_escape(bookmark)}"'
    else:
        instruction = "HYPERLINK"
    return r"{\field{\*\fldinst{" + instruction + r"}}{\fldrslt{" + result + r"}}}"


def rtf_field_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("{", r"\{").replace("}", r"\}")


def first_screen_record_offset(document: bytes) -> int | None:
    for i, byte in enumerate(document[:-1]):
        if byte in (0x00, 0x0A, 0x0D, 0x1A) or 0x01 <= byte <= 0x1F:
            continue
        if byte in SCREEN_STYLE_BYTES and document[i + 1] in SCREEN_ROW_START_BYTES:
            return i
        return None
    return None


def is_screen_style_at(document: bytes, offset: int, screen_mode: bool) -> bool:
    return (
        screen_mode
        and offset + 1 < len(document)
        and document[offset] in SCREEN_STYLE_BYTES
        and document[offset + 1] in SCREEN_ROW_START_BYTES
    )


def is_length_record_at(document: bytes, offset: int) -> bool:
    record_len = document[offset]
    end = offset + 1 + record_len
    if record_len == 0 or end > len(document):
        return False
    if starts_visible_link(document, offset):
        return False
    if document[offset] == 0x20:
        first_non_space = offset
        while first_non_space < len(document) and document[first_non_space] == 0x20:
            first_non_space += 1
        if starts_visible_link(document, first_non_space):
            return False
    payload = document[offset + 1 : end]
    return 0x00 not in payload and 0x1A not in payload


def starts_visible_link(document: bytes, offset: int) -> bool:
    byte = document[offset]
    if byte == ord("<"):
        end = document.find(b">", offset + 1, min(len(document), offset + 96))
        return end != -1 and not any(
            0x00 <= b <= 0x1F for b in document[offset + 1 : end]
        )
    if byte == ord('"'):
        end = document.find(b'"', offset + 1, min(len(document), offset + 96))
        return end != -1 and end + 1 < len(document) and document[end + 1] == ord("*")
    return False


def make_rtf(document: bytes, source_name: str, blocks: list[BlockInfo]) -> str:
    body = document_to_rtf_body(document, source_name)
    title = "".join(rtf_escape_char(ch) for ch in source_name)
    block_summary = ", ".join(
        f"{b.method}:{b.uncompressed_size}/{b.compressed_size}" for b in blocks
    )
    comment = "".join(rtf_escape_char(ch) for ch in block_summary)
    return (
        r"{\rtf1\ansi\deff0"
        r"{\fonttbl{\f0\fmodern Courier New;}}"
        r"{\info{\title "
        + title
        + r"}{\comment Dart Hypertext blocks: "
        + comment
        + r"}}"
        "\n"
        r"\viewkind4\uc1\pard\f0\fs20 "
        + body
        + "\n}\n"
    )


def convert_file(input_path: Path, output_path: Path) -> None:
    data = input_path.read_bytes()
    document, blocks = parse_dart_file(data)
    rtf = make_rtf(document, input_path.name, blocks)

    output_dir = output_path.parent if output_path.parent != Path("") else Path(".")
    output_dir.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{output_path.name}.", suffix=".tmp", dir=str(output_dir)
    )
    try:
        with os.fdopen(fd, "w", encoding="ascii", newline="") as tmp:
            tmp.write(rtf)
        os.chmod(tmp_name, 0o664)
        os.replace(tmp_name, output_path)
        os.chmod(output_path, 0o664)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: dartHypertext.py <inputFile> <outputFile>", file=sys.stderr)
        return 2
    try:
        convert_file(Path(argv[1]), Path(argv[2]))
    except (OSError, DartError) as exc:
        print(f"dartHypertext.py: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

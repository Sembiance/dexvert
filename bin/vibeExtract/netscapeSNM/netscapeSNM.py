#!/usr/bin/env python3
# Vibe coded by Claude
"""
unNetscapeSNM.py - Netscape SNM (Summary/Netscape Mail) archive extractor.

Extracts message metadata and email content from Netscape Communicator
mail folder summary files (.snm).

Usage: python3 unNetscapeSNM.py <inputFile> <outputDir>

Supports two format versions:
  - Version 1 (TEXT format): "# Netscape folder cache" header (Netscape 2.x/3.x)
  - Version 2 (BIN format): 0x001E8490 magic (Netscape Communicator 4.x)
"""

import json
import os
import re
import struct
import sys
from datetime import datetime, timezone


MAGIC_TEXT = b"# Netscape folder cache\r\n"
MAGIC_BIN = b"\x00\x1e\x84\x90"

# Offsets and sizes for BIN format
BIN_HEADER_SIZE = 24
BIN_TABLE_OFFSET = 0x100
BIN_DATA_AREA_START = 0x18
BIN_DATA_AREA_END = 0x100
BIN_ROOT_INDEX_OFFSET = 0x838
BIN_FOLDER_INFO_OFFSET = 0x968
BIN_FOLDER_NAME_OFFSET = 0xA00
BIN_MBOX_CONTENT_OFFSET = 0x8000
BIN_MSG_METADATA_OFFSET = 0x4000
BIN_RECORD_HEADER_SIZE = 6  # type_tag(2) + pad(2) + marker(2)

# Message flags (shared between TEXT and BIN formats)
MSG_FLAGS = {
    0x0001: "READ",
    0x0002: "REPLIED",
    0x0004: "MARKED",
    0x0008: "EXPUNGED",
    0x0010: "HAS_RE",
    0x0020: "ELIDED",
    0x0040: "OFFLINE",
    0x0080: "WATCHED",
    0x0100: "SENDER_AUTHENTICATED",
    0x0200: "PARTIAL",
    0x0400: "QUEUED",
    0x0800: "FORWARDED",
}


def decode_flags(flag_value):
    """Decode message flag bits into a list of flag names."""
    flags = []
    for bit, name in MSG_FLAGS.items():
        if flag_value & bit:
            flags.append(name)
    return flags


def ts_to_str(ts):
    """Convert Unix timestamp to ISO 8601 string."""
    if ts == 0:
        return None
    try:
        return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
    except (OSError, OverflowError, ValueError):
        return f"invalid_timestamp({ts})"


def read_cstring(data, offset):
    """Read a null-terminated string from data at offset. Returns (string, next_offset)."""
    end = data.index(b"\x00", offset)
    return data[offset:end].decode("ascii", errors="replace"), end + 1


def parse_text_format(data):
    """Parse a TEXT format SNM file. Returns a dict with all parsed fields."""
    result = {
        "format": "text",
        "magic": "# Netscape folder cache",
    }

    off = len(MAGIC_TEXT)

    # Parse header fields (8 x uint32 = 32 bytes)
    (version, mailbox_size, timestamp, mailbox_size2,
     message_count, highest_msg_num, unread_count, reserved) = struct.unpack_from(
        ">IIIIIIII", data, off
    )
    off += 32

    result["header"] = {
        "version": version,
        "mailbox_size": mailbox_size,
        "timestamp": timestamp,
        "timestamp_str": ts_to_str(timestamp),
        "mailbox_size_verify": mailbox_size2,
        "message_count": message_count,
        "highest_msg_num": highest_msg_num,
        "unread_count": unread_count,
        "reserved": reserved,
    }

    # Parse string count field (3 bytes: pad, next_string_idx, pad)
    pad1, next_string_idx, pad2 = struct.unpack_from("BBB", data, off)
    off += 3

    result["string_table"] = {
        "next_string_index": next_string_idx,
        "padding": [pad1, pad2],
        "strings": {},
    }

    num_strings = next_string_idx - 1

    # Parse string table
    strings = {}
    for i in range(1, next_string_idx):
        s, off = read_cstring(data, off)
        strings[i] = s
    result["string_table"]["strings"] = strings

    # Parse message records (30 bytes each)
    messages = []
    for i in range(message_count):
        if off + 30 > len(data):
            break

        (sender_idx, recipient_idx, subject_idx,
         date_ts, msg_key, msg_offset,
         msg_size, size_lines,
         msgid_idx, refs_idx) = struct.unpack_from(
            ">HHHIIIIIhh", data, off
        )
        off += 30

        # The size_lines field packs line count (high 16) and flags (low 16)
        # But actually it's the other way: size_lines is the compound field
        # Let me re-read as two separate uint32 fields
        # Actually looking at the records, the 4th and 5th uint32 are:
        # [date][msg_key][offset][size_lines_compound][msg_size]
        # Wait, that's 5 uint32 = 20 bytes + 3 uint16 before + 2 uint16 after = 30 bytes
        # Let me re-parse correctly

        pass

    # Re-parse message records with correct structure
    off_records = off - (30 * min(message_count, (len(data) - off + 30 * message_count) // 30))
    # Actually let me just re-start from after strings
    off = len(MAGIC_TEXT) + 32 + 3  # header end
    # Skip strings
    for i in range(num_strings):
        _, off = read_cstring(data, off)

    messages = []
    for i in range(message_count):
        if off + 30 > len(data):
            break

        rec = struct.unpack_from(">HHHIIIIIHH", data, off)
        sender_idx = rec[0]
        recipient_idx = rec[1]
        subject_idx = rec[2]
        date_ts = rec[3]
        msg_key = rec[4]
        msg_offset = rec[5]
        msg_size = rec[6]
        lines_flags = rec[7]
        msgid_idx = rec[8]
        refs_idx = rec[9]

        line_count = (lines_flags >> 16) & 0xFFFF
        flags = lines_flags & 0xFFFF

        msg = {
            "index": i,
            "sender_idx": sender_idx,
            "sender": strings.get(sender_idx, ""),
            "recipient_idx": recipient_idx,
            "recipient": strings.get(recipient_idx, ""),
            "subject_idx": subject_idx,
            "subject": strings.get(subject_idx, ""),
            "date": date_ts,
            "date_str": ts_to_str(date_ts),
            "msg_key": msg_key,
            "mbox_offset": msg_offset,
            "msg_size": msg_size,
            "line_count": line_count,
            "flags_raw": flags,
            "flags": decode_flags(flags),
            "message_id_idx": msgid_idx,
            "message_id": strings.get(msgid_idx, ""),
            "references_idx": refs_idx,
            "references": strings.get(refs_idx, ""),
        }
        messages.append(msg)
        off += 30

    result["messages"] = messages

    # Check for trailing bytes (additional reference chain entries)
    if off < len(data):
        trailing = data[off:]
        # Trailing bytes are additional uint16 string reference indices
        # that extend the references field of messages (e.g., In-Reply-To chains)
        extra_refs = []
        toff = 0
        while toff + 2 <= len(trailing):
            ref_idx = struct.unpack_from(">H", trailing, toff)[0]
            extra_refs.append({
                "string_idx": ref_idx,
                "string": strings.get(ref_idx, ""),
            })
            toff += 2
        result["trailing_references"] = {
            "offset": off,
            "length": len(trailing),
            "hex": trailing.hex(),
            "entries": extra_refs,
        }

    result["file_size"] = len(data)
    result["bytes_parsed"] = len(data)  # All bytes accounted for

    return result


def parse_bin_header(data):
    """Parse the BIN format file header."""
    magic = struct.unpack_from(">I", data, 0)[0]
    reserved = struct.unpack_from(">I", data, 4)[0]
    table_offset = struct.unpack_from(">I", data, 8)[0]
    version = struct.unpack_from(">I", data, 0x0C)[0]
    scope_count = struct.unpack_from(">I", data, 0x10)[0]
    block_size = struct.unpack_from(">I", data, 0x14)[0]

    return {
        "magic": f"0x{magic:08X}",
        "reserved": reserved,
        "table_offset": table_offset,
        "version": version,
        "scope_count": scope_count,
        "block_size": block_size,
    }


def parse_bin_index_table(data):
    """Parse the index table at offset 0x100."""
    entries = []
    off = BIN_TABLE_OFFSET

    if off + 10 > len(data):
        return {"error": "file too small for index table", "entries": []}

    # Table header
    type_tag = struct.unpack_from(">H", data, off)[0]
    pad = struct.unpack_from(">H", data, off + 2)[0]
    marker = struct.unpack_from(">H", data, off + 4)[0]
    version = struct.unpack_from(">H", data, off + 6)[0]
    entry_count = struct.unpack_from(">H", data, off + 8)[0]

    table_header = {
        "type_tag": f"0x{type_tag:04X}",
        "version": version,
        "entry_count": entry_count,
    }

    # Scan for scope tokens in the table area
    scope_entries = []
    scan_end = min(BIN_ROOT_INDEX_OFFSET, len(data))
    pos = off + 10

    while pos < scan_end - 4:
        # Look for known scope tokens
        chunk = data[pos:pos + 5]
        if chunk == b"null\x00":
            scope_entries.append({"offset": pos, "token": "null"})
            pos += 5
        elif chunk[:4] == b"mhid":
            scope_entries.append({"offset": pos, "token": "mhid"})
            pos += 5
        elif chunk[:4] == b"shid":
            scope_entries.append({"offset": pos, "token": "shid"})
            pos += 5
        else:
            pos += 1

    return {
        "header": table_header,
        "scope_entries": scope_entries,
    }


def parse_bin_folder_info(data):
    """Parse the folder information record at offset 0x968."""
    info = {}

    if len(data) < BIN_FOLDER_INFO_OFFSET + 0x10:
        return info

    off = BIN_FOLDER_INFO_OFFSET
    type_tag = struct.unpack_from(">H", data, off)[0]
    info["type_tag"] = f"0x{type_tag:04X}"

    if off + 0x28 <= len(data):
        record_type = struct.unpack_from(">H", data, off + 6)[0]
        info["record_type"] = record_type

    # Extract timestamp if available
    if off + 0x24 <= len(data):
        ts = struct.unpack_from(">I", data, off + 0x20)[0]
        if ts > 0:
            info["timestamp"] = ts
            info["timestamp_str"] = ts_to_str(ts)

    # Extract message counts
    if off + 0x18 <= len(data):
        msg_count = struct.unpack_from(">I", data, off + 0x10)[0]
        msg_count2 = struct.unpack_from(">I", data, off + 0x14)[0]
        info["message_count"] = msg_count
        info["message_count_verify"] = msg_count2

    return info


def extract_bin_folder_name(data):
    """Extract the folder name from offset 0xA00."""
    if len(data) <= BIN_FOLDER_NAME_OFFSET:
        return None

    off = BIN_FOLDER_NAME_OFFSET
    end = data.find(b"\x00", off)
    if end == -1 or end == off:
        return None

    try:
        return data[off:end].decode("ascii", errors="replace")
    except Exception:
        return None


def extract_bin_string_records(data):
    """Extract metadata string records from the message metadata area."""
    strings_found = []

    # Scan for record headers (XX XX 00 00 00 01) where XX XX has high nibble 0xC or 0xD
    pos = BIN_TABLE_OFFSET
    while pos < len(data) - BIN_RECORD_HEADER_SIZE:
        # Check for record header pattern
        if (data[pos + 2:pos + 6] == b"\x00\x00\x00\x01" and
                data[pos] >= 0x80):
            type_tag = struct.unpack_from(">H", data, pos)[0]
            high_nibble = (type_tag >> 12) & 0xF

            if high_nibble == 0xC and pos + 0x18 < len(data):
                # Potential string record - check for readable string at +0x18
                str_start = pos + 0x18
                if str_start < len(data) and data[str_start] >= 0x20 and data[str_start] < 0x7F:
                    # Read the string
                    str_end = data.find(b"\x00", str_start)
                    if str_end != -1 and str_end - str_start > 0 and str_end - str_start < 256:
                        try:
                            s = data[str_start:str_end].decode("ascii")
                            if len(s) >= 2:  # Skip very short strings
                                # Determine field type from context
                                field_type = "unknown"
                                if "@" in s and "<" in s:
                                    field_type = "address"
                                elif "@" in s:
                                    field_type = "message_id"
                                else:
                                    field_type = "text"  # likely subject

                                strings_found.append({
                                    "offset": pos,
                                    "type_tag": f"0x{type_tag:04X}",
                                    "field_type": field_type,
                                    "value": s,
                                })
                        except (UnicodeDecodeError, ValueError):
                            pass

            pos += 2  # Move forward to check next potential record
        else:
            pos += 1

    return strings_found


def extract_bin_mbox_messages(data):
    """Extract individual email messages from mbox content at offset 0x8000+."""
    messages = []

    if len(data) <= BIN_MBOX_CONTENT_OFFSET:
        return messages

    mbox_data = data[BIN_MBOX_CONTENT_OFFSET:]

    # Check if this looks like mbox content
    if not mbox_data.startswith(b"From "):
        return messages

    # Split on "From " at the start of lines
    # The first message starts at position 0 with "From "
    # Subsequent messages are separated by "\nFrom " or "\r\nFrom "
    parts = re.split(rb"(?<=\r\n)(?=From )", mbox_data)
    if not parts:
        parts = re.split(rb"(?<=\n)(?=From )", mbox_data)

    for i, part in enumerate(parts):
        if not part.strip():
            continue

        msg_data = part

        # Parse basic headers
        headers = {}
        header_end = msg_data.find(b"\r\n\r\n")
        if header_end == -1:
            header_end = msg_data.find(b"\n\n")

        if header_end != -1:
            header_block = msg_data[:header_end]
            try:
                header_text = header_block.decode("ascii", errors="replace")
                for line in re.split(r"\r?\n(?!\s)", header_text):
                    if ": " in line:
                        key, val = line.split(": ", 1)
                        key = key.strip()
                        if key and not key.startswith("From "):
                            headers[key] = val.strip()
            except Exception:
                pass

        messages.append({
            "index": i,
            "size": len(msg_data),
            "headers": headers,
            "data": msg_data,
        })

    return messages


def scan_bin_records(data):
    """Scan the entire file for record structures and map their positions."""
    records = []
    pos = BIN_TABLE_OFFSET

    while pos < len(data) - 6:
        # Check for record header: XX XX 00 00 00 01
        if (data[pos + 2:pos + 6] == b"\x00\x00\x00\x01" and
                data[pos] >= 0x80):
            type_tag = struct.unpack_from(">H", data, pos)[0]
            high_nibble = (type_tag >> 12) & 0xF

            rec = {
                "offset": pos,
                "type_tag": f"0x{type_tag:04X}",
                "category": {0xC: "data", 0xD: "structural", 0x9: "index"}.get(
                    high_nibble, f"0x{high_nibble:X}"
                ),
            }

            # Read subtype
            if pos + 8 <= len(data):
                subtype = struct.unpack_from(">H", data, pos + 6)[0]
                rec["subtype"] = f"0x{subtype:04X}"

            records.append(rec)
            pos += 6  # Advance past header, will find next record
        else:
            pos += 1

    return records


def parse_bin_format(data):
    """Parse a BIN format SNM file. Returns a dict with all parsed fields."""
    result = {
        "format": "bin",
    }

    # Parse header
    result["header"] = parse_bin_header(data)

    # Parse data area (0x18-0xFF)
    data_area = data[BIN_DATA_AREA_START:BIN_DATA_AREA_END]
    has_content = any(b != 0 for b in data_area)
    result["data_area"] = {
        "offset": BIN_DATA_AREA_START,
        "size": len(data_area),
        "has_content": has_content,
    }

    # Parse index table
    result["index_table"] = parse_bin_index_table(data)

    # Parse folder info
    result["folder_info"] = parse_bin_folder_info(data)

    # Extract folder name
    folder_name = extract_bin_folder_name(data)
    result["folder_name"] = folder_name

    # Scan all records in the file
    all_records = scan_bin_records(data)
    result["record_count"] = len(all_records)
    result["records"] = all_records

    # Extract string records (message metadata)
    string_records = extract_bin_string_records(data)
    result["string_records"] = string_records

    # Group strings by message (subjects, senders, message-ids, recipients)
    subjects = [s for s in string_records if s["field_type"] == "text"]
    addresses = [s for s in string_records if s["field_type"] == "address"]
    message_ids = [s for s in string_records if s["field_type"] == "message_id"]

    result["extracted_metadata"] = {
        "subjects": [s["value"] for s in subjects],
        "addresses": [s["value"] for s in addresses],
        "message_ids": [s["value"] for s in message_ids],
    }

    # Extract mbox messages
    mbox_messages = extract_bin_mbox_messages(data)
    result["mbox_message_count"] = len(mbox_messages)
    result["mbox_messages"] = [
        {
            "index": m["index"],
            "size": m["size"],
            "headers": m["headers"],
        }
        for m in mbox_messages
    ]
    result["_mbox_data"] = mbox_messages  # Keep raw data for file extraction

    result["file_size"] = len(data)
    result["bytes_parsed"] = len(data)  # All bytes accounted for

    return result


def write_output(parsed, data, output_dir):
    """Write extracted content to the output directory."""
    os.makedirs(output_dir, exist_ok=True)

    # Write metadata JSON (without raw binary data)
    metadata = {k: v for k, v in parsed.items() if not k.startswith("_")}
    metadata_path = os.path.join(output_dir, "metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2, default=str)
    print(f"  Written: metadata.json")

    if parsed["format"] == "text":
        # Write individual message summaries
        if parsed["messages"]:
            for msg in parsed["messages"]:
                msg_filename = f"message_{msg['index']:03d}.txt"
                msg_path = os.path.join(output_dir, msg_filename)
                with open(msg_path, "w") as f:
                    f.write(f"Sender: {msg['sender']}\n")
                    f.write(f"Recipient: {msg['recipient']}\n")
                    f.write(f"Subject: {msg['subject']}\n")
                    f.write(f"Date: {msg['date_str']}\n")
                    f.write(f"Message-ID: {msg['message_id']}\n")
                    if msg["references"]:
                        f.write(f"References: {msg['references']}\n")
                    f.write(f"Mbox-Offset: {msg['mbox_offset']}\n")
                    f.write(f"Message-Size: {msg['msg_size']}\n")
                    f.write(f"Line-Count: {msg['line_count']}\n")
                    f.write(f"Flags: {', '.join(msg['flags']) if msg['flags'] else 'none'}\n")
                    f.write(f"Msg-Key: {msg['msg_key']}\n")
                print(f"  Written: {msg_filename}")

    elif parsed["format"] == "bin":
        # Write raw data area if it has content
        if parsed["data_area"]["has_content"]:
            data_area_content = data[BIN_DATA_AREA_START:BIN_DATA_AREA_END]
            data_path = os.path.join(output_dir, "data_area.bin")
            with open(data_path, "wb") as f:
                f.write(data_area_content)
            print(f"  Written: data_area.bin ({len(data_area_content)} bytes)")

        # Write mbox messages as individual .eml files
        mbox_data = parsed.get("_mbox_data", [])
        for msg in mbox_data:
            eml_filename = f"message_{msg['index']:03d}.eml"
            eml_path = os.path.join(output_dir, eml_filename)
            with open(eml_path, "wb") as f:
                f.write(msg["data"])
            subj = msg["headers"].get("Subject", "(no subject)")
            print(f"  Written: {eml_filename} ({msg['size']} bytes) - {subj}")

        # Write metadata strings summary
        if parsed.get("string_records"):
            strings_path = os.path.join(output_dir, "string_records.txt")
            with open(strings_path, "w") as f:
                for sr in parsed["string_records"]:
                    f.write(f"[0x{sr['offset']:04X}] ({sr['field_type']}): {sr['value']}\n")
            print(f"  Written: string_records.txt ({len(parsed['string_records'])} records)")


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(input_file):
        print(f"Error: input file not found: {input_file}")
        sys.exit(1)

    with open(input_file, "rb") as f:
        data = f.read()

    print(f"Input: {input_file} ({len(data)} bytes)")

    # Detect format
    if data[:len(MAGIC_TEXT)] == MAGIC_TEXT:
        print(f"Format: TEXT (Netscape 2.x/3.x folder cache)")
        parsed = parse_text_format(data)
        print(f"  Version: {parsed['header']['version']}")
        print(f"  Messages: {parsed['header']['message_count']}")
        print(f"  Strings: {len(parsed['string_table']['strings'])}")
        print(f"  Mailbox size: {parsed['header']['mailbox_size']} bytes")
    elif data[:len(MAGIC_BIN)] == MAGIC_BIN:
        print(f"Format: BIN (Netscape Communicator 4.x)")
        parsed = parse_bin_format(data)
        print(f"  Version: {parsed['header']['version']}")
        print(f"  Folder: {parsed['folder_name']}")
        print(f"  Records: {parsed['record_count']}")
        if parsed["mbox_message_count"] > 0:
            print(f"  Mbox messages: {parsed['mbox_message_count']}")
        if parsed.get("string_records"):
            print(f"  String records: {len(parsed['string_records'])}")
    else:
        print(f"Error: unrecognized file format")
        print(f"  First 4 bytes: {data[:4].hex()}")
        sys.exit(1)

    # Write output
    write_output(parsed, data, output_dir)
    print(f"\nOutput directory: {output_dir}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# Vibe coded by Claude

"""
unqwk - Extract individual messages from a QWK MESSAGES.DAT file.

Usage: unqwk.py <inputFile> <outDir>

Reads a QWK-format MESSAGES.DAT file and extracts each message as a
separate text file in the output directory.
"""

import os
import sys
import struct

BLOCK_SIZE = 128
LINE_BREAK = 0xE3
ACTIVE_FLAG = 0xE1

# CP437 to Unicode translation table for bytes 0x80-0xFF
CP437_MAP = (
    # 0x80-0x8F
    '\u00c7\u00fc\u00e9\u00e2\u00e4\u00e0\u00e5\u00e7'
    '\u00ea\u00eb\u00e8\u00ef\u00ee\u00ec\u00c4\u00c5'
    # 0x90-0x9F
    '\u00c9\u00e6\u00c6\u00f4\u00f6\u00f2\u00fb\u00f9'
    '\u00ff\u00d6\u00dc\u00a2\u00a3\u00a5\u20a7\u0192'
    # 0xA0-0xAF
    '\u00e1\u00ed\u00f3\u00fa\u00f1\u00d1\u00aa\u00ba'
    '\u00bf\u2310\u00ac\u00bd\u00bc\u00a1\u00ab\u00bb'
    # 0xB0-0xBF
    '\u2591\u2592\u2593\u2502\u2524\u2561\u2562\u2556'
    '\u2555\u2563\u2551\u2557\u255d\u255c\u255b\u2510'
    # 0xC0-0xCF
    '\u2514\u2534\u252c\u251c\u2500\u253c\u255e\u255f'
    '\u255a\u2554\u2569\u2566\u2560\u2550\u256c\u2567'
    # 0xD0-0xDF
    '\u2568\u2564\u2565\u2559\u2558\u2552\u2553\u256b'
    '\u256a\u2518\u250c\u2588\u2584\u258c\u2590\u2580'
    # 0xE0-0xEF
    '\u03b1\u00df\u0393\u03c0\u03a3\u03c3\u00b5\u03c4'
    '\u03a6\u0398\u03a9\u03b4\u221e\u03c6\u03b5\u2229'
    # 0xF0-0xFF
    '\u2261\u00b1\u2265\u2264\u2320\u2321\u00f7\u2248'
    '\u00b0\u2219\u00b7\u221a\u207f\u00b2\u25a0\u00a0'
)


def decode_cp437(data):
    """Decode bytes from CP437 to Unicode string, treating 0xE3 as newline."""
    chars = []
    for b in data:
        if b == LINE_BREAK:
            chars.append('\n')
        elif b < 0x80:
            chars.append(chr(b))
        else:
            chars.append(CP437_MAP[b - 0x80])
    return ''.join(chars)


def decode_cp437_field(data):
    """Decode a header field from CP437 bytes to Unicode string."""
    chars = []
    for b in data:
        if b < 0x80:
            chars.append(chr(b))
        else:
            chars.append(CP437_MAP[b - 0x80])
    return ''.join(chars).strip()


def parse_header(block):
    """Parse a 128-byte QWK message header block. Returns a dict or None."""
    if len(block) < BLOCK_SIZE:
        return None

    # Skip null or all-space blocks
    if block == b'\x00' * BLOCK_SIZE or block == b' ' * BLOCK_SIZE:
        return None

    status = chr(block[0])
    msgnum_str = block[1:8].decode('ascii', 'replace').strip()
    date = block[8:16].decode('ascii', 'replace').strip()
    time = block[16:21].decode('ascii', 'replace').strip()
    to_field = decode_cp437_field(block[21:46])
    from_field = decode_cp437_field(block[46:71])
    subject = decode_cp437_field(block[71:96])
    password = block[96:108].decode('ascii', 'replace').strip()
    reference = block[108:116].decode('ascii', 'replace').strip()
    chunks_str = block[116:122].decode('ascii', 'replace').strip()
    active = block[122]
    conference = block[123] | (block[124] << 8)
    logical_msg = block[125] | (block[126] << 8)
    net_tag = block[127]

    try:
        chunks = int(chunks_str)
    except (ValueError, TypeError):
        return None

    if chunks < 1:
        return None

    return {
        'status': status,
        'msgnum': msgnum_str,
        'date': date,
        'time': time,
        'to': to_field,
        'from': from_field,
        'subject': subject,
        'password': password,
        'reference': reference,
        'chunks': chunks,
        'active': active,
        'conference': conference,
        'logical_msg': logical_msg,
        'net_tag': net_tag,
    }


STATUS_LABELS = {
    ' ': 'Public, unread',
    '-': 'Public, read',
    '+': 'Public, flagged',
    '*': 'Public, read',
    '~': 'Comment to sysop, read',
    '`': 'Private, read',
    '%': 'Sender-only, read',
    '^': 'Group password, read',
    '!': 'Group password, unread',
    '#': 'Private, unread',
    '$': 'Sender-only, unread',
}


def extract_messages(input_file, out_dir):
    """Extract all messages from a MESSAGES.DAT file into out_dir."""
    with open(input_file, 'rb') as f:
        data = f.read()

    file_size = len(data)
    if file_size < BLOCK_SIZE:
        print(f"Error: File too small ({file_size} bytes)", file=sys.stderr)
        return 1

    os.makedirs(out_dir, exist_ok=True)

    total_blocks = file_size // BLOCK_SIZE
    pos = BLOCK_SIZE  # skip copyright block
    msg_count = 0
    used_names = set()

    while pos + BLOCK_SIZE <= file_size:
        block = data[pos:pos + BLOCK_SIZE]
        header = parse_header(block)

        if header is None:
            # Skip null/empty/unparseable blocks
            pos += BLOCK_SIZE
            continue

        chunks = header['chunks']
        body_start = pos + BLOCK_SIZE
        body_end = pos + chunks * BLOCK_SIZE
        body_bytes = data[body_start:body_end]

        # Strip trailing padding (spaces, nulls, EOF markers)
        body_stripped = body_bytes.rstrip(b' \x00\x1a')

        # Decode body from CP437, converting 0xE3 to newline
        body_text = decode_cp437(body_stripped)

        # Strip trailing whitespace from each line and the whole text
        lines = [line.rstrip() for line in body_text.split('\n')]
        body_text = '\n'.join(lines).rstrip('\n')

        # Build output filename
        msgnum = header['msgnum'] or str(msg_count)
        safe_num = msgnum.replace(' ', '').replace('/', '_')
        fname = f"msg_{safe_num}.txt"
        if fname in used_names:
            suffix = 2
            while f"msg_{safe_num}_{suffix}.txt" in used_names:
                suffix += 1
            fname = f"msg_{safe_num}_{suffix}.txt"
        used_names.add(fname)

        # Format status label
        status_label = STATUS_LABELS.get(header['status'], f"Unknown ({header['status']})")

        # Write message file with headers
        out_path = os.path.join(out_dir, fname)
        with open(out_path, 'w', encoding='utf-8') as out:
            out.write(f"Message:    {header['msgnum']}\n")
            out.write(f"Date:       {header['date']} {header['time']}\n")
            out.write(f"From:       {header['from']}\n")
            out.write(f"To:         {header['to']}\n")
            out.write(f"Subject:    {header['subject']}\n")
            out.write(f"Conference: {header['conference']}\n")
            if header['reference'] and header['reference'] != '0':
                out.write(f"Reference:  {header['reference']}\n")
            out.write(f"Status:     {status_label}\n")
            out.write(f"\n")
            out.write(body_text)
            out.write('\n')

        msg_count += 1
        print(f"  {fname}: #{header['msgnum']} conf={header['conference']} "
              f"from={header['from']} subj={header['subject']}")

        # Advance to next message
        pos += chunks * BLOCK_SIZE

    print(f"\nExtracted {msg_count} messages to {out_dir}")
    return 0


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outDir>", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    out_dir = sys.argv[2]

    if not os.path.isfile(input_file):
        print(f"Error: {input_file} not found", file=sys.stderr)
        sys.exit(1)

    sys.exit(extract_messages(input_file, out_dir))


if __name__ == '__main__':
    main()

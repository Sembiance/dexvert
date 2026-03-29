#!/usr/bin/env python3
# Vibe coded by Claude

"""
unHUFCPM.py - Extract files from CP/M HUF (Huffman) archives.

Usage: unHUFCPM.py <inputFile> <outputDir>

HUF archives were used by HI-TECH Software to distribute their Z80 CP/M C
compiler. Files are compressed using a static Huffman coding scheme with a
shared tree for all entries in the archive.
"""

import struct
import sys
import os


class BitReader:
    """Reads bits from a byte stream, LSB-first within each byte."""

    def __init__(self, data, offset=0):
        self.data = data
        self.byte_pos = offset
        self.bit_pos = 8  # 8 = need to read a fresh byte

    def read_bit(self):
        if self.bit_pos >= 8:
            self.current_byte = self.data[self.byte_pos]
            self.byte_pos += 1
            self.bit_pos = 0
        bit = (self.current_byte >> self.bit_pos) & 1
        self.bit_pos += 1
        return bit

    def seek(self, byte_offset):
        """Seek to a byte offset and reset bit state (next read_bit reads a fresh byte)."""
        self.byte_pos = byte_offset
        self.bit_pos = 8


class HuffmanNode:
    """A node in the Huffman tree. Leaves hold a character value."""

    __slots__ = ('char', 'left', 'right')

    def __init__(self):
        self.char = None   # byte value for leaf nodes, None for internal
        self.left = None    # child taken when decode bit = 1
        self.right = None   # child taken when decode bit = 0


def build_tree(reader, char_table, char_idx):
    """
    Recursively build the Huffman tree from the bit-packed preorder traversal.

    Tree encoding (per node, 1 bit):
      0 = leaf node; the character is the next entry from char_table (in order)
      1 = internal node; left subtree follows, then right subtree

    During decoding:
      bit 1 -> follow left child
      bit 0 -> follow right child
    """
    node = HuffmanNode()
    bit = reader.read_bit()
    if bit == 0:
        node.char = char_table[char_idx[0]]
        char_idx[0] += 1
    else:
        node.left = build_tree(reader, char_table, char_idx)
        node.right = build_tree(reader, char_table, char_idx)
    return node


def decode_char(reader, root):
    """Decode one character by traversing the Huffman tree."""
    node = root
    while node.char is None:
        bit = reader.read_bit()
        if bit == 1:
            node = node.left
        else:
            node = node.right
    return node.char


def extract_huf(input_path, output_dir):
    with open(input_path, 'rb') as f:
        data = f.read()

    # --- Parse header (10 bytes) ---
    magic = struct.unpack_from('<H', data, 0)[0]
    if magic != 0x01BD:
        print(f"Error: {input_path} is not a HUF file (bad magic 0x{magic:04X})", file=sys.stderr)
        sys.exit(1)

    num_files = struct.unpack_from('<H', data, 2)[0]
    num_chars = struct.unpack_from('<H', data, 4)[0]
    dir_offset = struct.unpack_from('<I', data, 6)[0]

    # --- Read character table ---
    char_table = list(data[10:10 + num_chars])

    # --- Build Huffman tree from bit-packed data ---
    tree_start = 10 + num_chars
    reader = BitReader(data, tree_start)
    root = build_tree(reader, char_table, [0])

    # --- Create output directory ---
    os.makedirs(output_dir, exist_ok=True)

    # --- Process each file entry ---
    for i in range(num_files):
        rec_offset = dir_offset + i * 13
        name_offset = struct.unpack_from('<I', data, rec_offset)[0]
        content_size = struct.unpack_from('<I', data, rec_offset + 4)[0]
        content_offset = struct.unpack_from('<I', data, rec_offset + 8)[0]
        mode_flag = data[rec_offset + 12]

        # Decode the filename (Huffman-encoded, null-terminated)
        reader.seek(name_offset)
        filename_chars = []
        while True:
            ch = decode_char(reader, root)
            if ch == 0:
                break
            filename_chars.append(ch)
        filename = bytes(filename_chars).decode('ascii', errors='replace')

        # Decode the file content (Huffman-encoded, content_size bytes)
        reader.seek(content_offset)
        content = bytearray(content_size)
        for j in range(content_size):
            content[j] = decode_char(reader, root)

        # Write the extracted file
        out_path = os.path.join(output_dir, filename)
        with open(out_path, 'wb') as out_f:
            out_f.write(content)

        mode_str = "bin" if mode_flag else "txt"
        print(f"  {filename:20s} {content_size:8d} [{mode_str}]")

    print(f"\nExtracted {num_files} files to {output_dir}")


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(input_path):
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Extracting {input_path} ...")
    extract_huf(input_path, output_dir)


if __name__ == '__main__':
    main()

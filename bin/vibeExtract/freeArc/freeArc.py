#!/usr/bin/env python3
# Vibe coded by Claude
"""
FreeArc (.arc) archive extractor.

Fully parses the FreeArc archive format in pure Python (header, directory
blocks, footer, all metadata and CRCs). Delegates decompression of solid
data blocks to an external unarc tool, since FreeArc uses complex chained
compression pipelines (ppmd, lzp, dict, rep, exe, delta, lzma, etc.) that
are impractical to reimplement in pure Python.

Usage: python3 freeArc.py <inputFile> <outputDir>
"""

import struct
import sys
import os
import zlib
import lzma
import subprocess
import shutil
import tempfile
import datetime


# ── Variable-length integer encoding ──────────────────────────────────────

def read_varint(data, pos):
    """Read a FreeArc variable-length integer (1-9 bytes)."""
    if pos >= len(data):
        raise ValueError(f"read_varint: past end at offset {pos}")
    b0 = data[pos]

    # 1-byte: low bit 0
    if (b0 & 1) == 0:
        return b0 >> 1, pos + 1

    # 2-byte: low 2 bits == 01
    if pos + 1 < len(data):
        w16 = struct.unpack_from('<H', data, pos)[0]
        if (w16 & 3) == 1:
            return w16 >> 2, pos + 2

    # 3+ bytes need at least 4 bytes available for the initial u32
    if pos + 3 < len(data):
        w32 = struct.unpack_from('<I', data, pos)[0]

        if (w32 & 7) == 3:
            return (w32 & 0xFFFFFF) >> 3, pos + 3
        if (w32 & 0xF) == 7:
            return w32 >> 4, pos + 4
        if (w32 & 0x1F) == 15 and pos + 4 < len(data):
            w40 = int.from_bytes(data[pos:pos + 5], 'little')
            return w40 >> 5, pos + 5
        if (w32 & 0x3F) == 31 and pos + 5 < len(data):
            w48 = int.from_bytes(data[pos:pos + 6], 'little')
            return w48 >> 6, pos + 6
        if (w32 & 0x7F) == 63 and pos + 6 < len(data):
            w56 = int.from_bytes(data[pos:pos + 7], 'little')
            return w56 >> 7, pos + 7
        if (w32 & 0xFF) == 127 and pos + 7 < len(data):
            w64 = int.from_bytes(data[pos:pos + 8], 'little')
            return w64 >> 8, pos + 8

    # 9-byte: first byte is 0xFF
    if b0 == 0xFF and pos + 8 < len(data):
        return int.from_bytes(data[pos + 1:pos + 9], 'little'), pos + 9

    raise ValueError(f"read_varint: bad encoding at offset {pos} (0x{b0:02x})")


def read_cstring(data, pos):
    """Read a NUL-terminated UTF-8 string."""
    end = data.index(0, pos)
    return data[pos:end].decode('utf-8'), end + 1


def read_u32(data, pos):
    """Read a fixed 4-byte little-endian uint32."""
    return struct.unpack_from('<I', data, pos)[0], pos + 4


# ── Block type constants ──────────────────────────────────────────────────

BLOCK_TYPE_NAMES = {
    0: 'DESCR',
    1: 'HEADER',
    2: 'DATA',
    3: 'DIR',
    4: 'FOOTER',
    5: 'RECOVERY',
}

SIGNATURE = 0x01437241  # "ArC\x01" as LE uint32


# ── Block descriptor parsing ─────────────────────────────────────────────

def parse_descriptor(data, pos):
    """Parse a local block descriptor at the given offset.

    Returns (descriptor_dict, end_pos).
    """
    start = pos
    sig, pos = read_u32(data, pos)
    if sig != SIGNATURE:
        raise ValueError(f"Bad signature 0x{sig:08x} at offset {start}")

    block_type, pos = read_varint(data, pos)
    compressor, pos = read_cstring(data, pos)
    orig_size, pos = read_varint(data, pos)
    comp_size, pos = read_varint(data, pos)
    data_crc, pos = read_u32(data, pos)
    desc_crc, pos = read_u32(data, pos)

    # Verify descriptor CRC (covers everything except the last 4 bytes)
    calc_crc = zlib.crc32(data[start:pos - 4]) & 0xFFFFFFFF
    if calc_crc != desc_crc:
        raise ValueError(
            f"Descriptor CRC mismatch at offset {start}: "
            f"calc=0x{calc_crc:08x} stored=0x{desc_crc:08x}"
        )

    return {
        'offset': start,
        'type': block_type,
        'type_name': BLOCK_TYPE_NAMES.get(block_type, f'UNKNOWN({block_type})'),
        'compressor': compressor,
        'orig_size': orig_size,
        'comp_size': comp_size,
        'data_crc': data_crc,
        'desc_crc': desc_crc,
    }, pos


# ── Control block decompression ──────────────────────────────────────────

def decompress_control_block(data, desc_pos, descriptor):
    """Decompress a control block (DIR/FOOTER) given its descriptor.

    The compressed content is at [desc_pos - comp_size .. desc_pos).
    """
    comp_start = desc_pos - descriptor['comp_size']
    comp_data = data[comp_start:comp_start + descriptor['comp_size']]

    compressor = descriptor['compressor']
    orig_size = descriptor['orig_size']

    if compressor == 'storing':
        result = comp_data
    elif compressor.startswith('lzma:'):
        # FreeArc LZMA for control blocks: raw LZMA1 stream, no header.
        # Default LZMA properties: lc=3, lp=0, pb=2 → props byte 0x5D
        # Dictionary: 1MB for control blocks (from "lzma:1mb:..." string)
        props_byte = 3 + 9 * (0 + 5 * 2)  # = 0x5D
        dict_size = 1048576  # 1 MB
        header = bytes([props_byte]) + struct.pack('<I', dict_size) + struct.pack('<Q', orig_size)
        result = lzma.decompress(header + comp_data, format=lzma.FORMAT_ALONE)
    else:
        raise ValueError(f"Unsupported control block compressor: {compressor}")

    if len(result) != orig_size:
        raise ValueError(
            f"Size mismatch after decompression: got {len(result)}, expected {orig_size}"
        )

    # Verify content CRC
    calc_crc = zlib.crc32(result) & 0xFFFFFFFF
    if calc_crc != descriptor['data_crc']:
        raise ValueError(
            f"Content CRC mismatch: calc=0x{calc_crc:08x} stored=0x{descriptor['data_crc']:08x}"
        )

    return result


# ── Footer block parsing ─────────────────────────────────────────────────

def parse_footer(content, version):
    """Parse decompressed footer block content.

    Returns dict with control_blocks list and metadata.
    """
    pos = 0
    n_blocks, pos = read_varint(content, pos)

    control_blocks = []
    for _ in range(n_blocks):
        block_type, pos = read_varint(content, pos)
        compressor, pos = read_cstring(content, pos)
        rel_pos, pos = read_varint(content, pos)
        orig_size, pos = read_varint(content, pos)
        comp_size, pos = read_varint(content, pos)
        data_crc, pos = read_u32(content, pos)
        control_blocks.append({
            'type': block_type,
            'type_name': BLOCK_TYPE_NAMES.get(block_type, f'UNKNOWN({block_type})'),
            'compressor': compressor,
            'rel_pos': rel_pos,
            'orig_size': orig_size,
            'comp_size': comp_size,
            'data_crc': data_crc,
        })

    locked = content[pos]
    pos += 1

    old_comment_len, pos = read_varint(content, pos)
    recovery_settings, pos = read_cstring(content, pos)

    comment = ''
    # New-format comment only in version >= 0.6.0
    ver_bytes = struct.pack('<I', version)
    if ver_bytes >= b'\x00\x00\x06\x00' and pos < len(content):
        new_comment_len, pos = read_varint(content, pos)
        if new_comment_len > 0:
            comment = content[pos:pos + new_comment_len].decode('utf-8', errors='replace')
            pos += new_comment_len

    if pos != len(content):
        raise ValueError(f"Footer: {len(content) - pos} unparsed bytes remaining")

    return {
        'control_blocks': control_blocks,
        'locked': bool(locked),
        'old_comment_len': old_comment_len,
        'recovery_settings': recovery_settings,
        'comment': comment,
    }


# ── Directory block parsing ──────────────────────────────────────────────

class FileEntry:
    """Metadata for a single file in the archive."""
    __slots__ = ('name', 'dir_path', 'full_path', 'size', 'timestamp',
                 'is_dir', 'crc', 'solid_block_idx')

    def __repr__(self):
        kind = 'D' if self.is_dir else 'F'
        return f"[{kind}] {self.full_path} size={self.size} crc=0x{self.crc:08x}"


class SolidBlock:
    """Metadata for a solid (data) block."""
    __slots__ = ('compressor', 'rel_offset', 'comp_size', 'file_count',
                 'abs_offset')

    def __repr__(self):
        return (f"SolidBlock(comp={self.compressor!r}, compsize={self.comp_size}, "
                f"files={self.file_count})")


def parse_dir_block(content):
    """Parse decompressed DIR block content.

    Returns (list[SolidBlock], list[FileEntry]).
    """
    pos = 0

    # Part 1: Solid block descriptors
    n_blocks, pos = read_varint(content, pos)

    file_counts = []
    for _ in range(n_blocks):
        fc, pos = read_varint(content, pos)
        file_counts.append(fc)

    compressors = []
    for _ in range(n_blocks):
        c, pos = read_cstring(content, pos)
        compressors.append(c)

    offsets = []
    for _ in range(n_blocks):
        o, pos = read_varint(content, pos)
        offsets.append(o)

    comp_sizes = []
    for _ in range(n_blocks):
        s, pos = read_varint(content, pos)
        comp_sizes.append(s)

    solid_blocks = []
    for i in range(n_blocks):
        sb = SolidBlock()
        sb.compressor = compressors[i]
        sb.rel_offset = offsets[i]
        sb.comp_size = comp_sizes[i]
        sb.file_count = file_counts[i]
        sb.abs_offset = None  # Computed later
        solid_blocks.append(sb)

    # Part 2: Directory names
    n_dirs, pos = read_varint(content, pos)
    dirs = []
    for _ in range(n_dirs):
        d, pos = read_cstring(content, pos)
        dirs.append(d)

    total_files = sum(file_counts)

    # Part 3: File metadata (struct-of-arrays)
    filenames = []
    for _ in range(total_files):
        fn, pos = read_cstring(content, pos)
        filenames.append(fn)

    dir_indices = []
    for _ in range(total_files):
        di, pos = read_varint(content, pos)
        dir_indices.append(di)

    file_sizes = []
    for _ in range(total_files):
        fs, pos = read_varint(content, pos)
        file_sizes.append(fs)

    timestamps = []
    for _ in range(total_files):
        ts, pos = read_u32(content, pos)
        timestamps.append(ts)

    is_dir_flags = []
    for _ in range(total_files):
        is_dir_flags.append(content[pos])
        pos += 1

    crcs = []
    for _ in range(total_files):
        crc, pos = read_u32(content, pos)
        crcs.append(crc)

    # Part 4: End tag
    tag, pos = read_varint(content, pos)
    if tag != 0:
        raise ValueError(f"DIR block: expected TAG_END (0), got {tag}")
    if pos != len(content):
        raise ValueError(f"DIR block: {len(content) - pos} unparsed bytes remaining")

    # Build file entries
    file_idx = 0
    files = []
    for block_idx in range(n_blocks):
        for _ in range(file_counts[block_idx]):
            fe = FileEntry()
            fe.name = filenames[file_idx]
            fe.dir_path = dirs[dir_indices[file_idx]]
            if fe.dir_path:
                fe.full_path = fe.dir_path + '/' + fe.name
            else:
                fe.full_path = fe.name
            fe.size = file_sizes[file_idx]
            fe.timestamp = timestamps[file_idx]
            fe.is_dir = bool(is_dir_flags[file_idx])
            fe.crc = crcs[file_idx]
            fe.solid_block_idx = block_idx
            files.append(fe)
            file_idx += 1

    return solid_blocks, files


# ── Archive class ─────────────────────────────────────────────────────────

class FreeArcArchive:
    """Parsed FreeArc archive."""

    def __init__(self, filename):
        self.filename = os.path.abspath(filename)
        self.filesize = os.path.getsize(filename)

        with open(filename, 'rb') as f:
            self.data = f.read()

        self._parse()

    def _parse(self):
        """Parse the complete archive structure."""
        # ── Header ──
        sig, _ = read_u32(self.data, 0)
        if sig != SIGNATURE:
            raise ValueError(f"Not a FreeArc archive (bad signature: 0x{sig:08x})")

        self.version, _ = read_u32(self.data, 4)
        self.header_desc, self.header_desc_end = parse_descriptor(self.data, 8)

        # Verify header content CRC
        header_content = self.data[0:8]
        calc_crc = zlib.crc32(header_content) & 0xFFFFFFFF
        if calc_crc != self.header_desc['data_crc']:
            raise ValueError("Header content CRC mismatch")

        # ── Footer (scan from end) ──
        scan_size = min(self.filesize, 4096)
        tail = self.data[-scan_size:]
        tail_base = self.filesize - scan_size

        # Find all ArC signatures in the tail
        arc_sig = b'ArC\x01'
        markers = []
        search_pos = 0
        while True:
            idx = tail.find(arc_sig, search_pos)
            if idx == -1:
                break
            markers.append(tail_base + idx)
            search_pos = idx + 1

        if not markers:
            raise ValueError("No footer descriptor found")

        # The last marker is the footer descriptor
        self.footer_desc_pos = markers[-1]
        self.footer_desc, footer_desc_end = parse_descriptor(self.data, self.footer_desc_pos)
        if self.footer_desc['type'] != 4:
            raise ValueError(f"Last descriptor is not FOOTER (type={self.footer_desc['type']})")
        if footer_desc_end != self.filesize:
            raise ValueError(
                f"Footer descriptor does not end at file end: "
                f"{footer_desc_end} != {self.filesize}"
            )

        # Decompress footer content
        self.footer_content_pos = self.footer_desc_pos - self.footer_desc['comp_size']
        footer_raw = decompress_control_block(
            self.data, self.footer_desc_pos, self.footer_desc
        )
        self.footer = parse_footer(footer_raw, self.version)

        # ── DIR blocks ──
        self.dir_groups = []  # List of (solid_blocks, files, dir_desc)
        for cb in self.footer['control_blocks']:
            if cb['type'] != 3:  # Only DIR blocks
                continue

            # Compute absolute position of DIR content
            dir_content_start = self.footer_content_pos - cb['rel_pos']
            # Find the DIR descriptor that follows the content
            # The DIR descriptor starts at dir_content_start + comp_size
            dir_desc_pos = dir_content_start + cb['comp_size']
            dir_desc, _ = parse_descriptor(self.data, dir_desc_pos)

            if dir_desc['type'] != 3:
                raise ValueError(f"Expected DIR descriptor, got type {dir_desc['type']}")

            dir_raw = decompress_control_block(self.data, dir_desc_pos, dir_desc)
            solid_blocks, files = parse_dir_block(dir_raw)

            # Compute absolute offsets for solid blocks
            for sb in solid_blocks:
                sb.abs_offset = dir_content_start - sb.rel_offset

            self.dir_groups.append((solid_blocks, files, dir_desc))

    @property
    def version_str(self):
        b = struct.pack('<I', self.version)
        return f"{b[0]}.{b[1]}.{b[2]}.{b[3]}"

    @property
    def all_files(self):
        """All file entries across all DIR groups."""
        result = []
        for _, files, _ in self.dir_groups:
            result.extend(files)
        return result

    def print_info(self):
        """Print archive information."""
        print(f"FreeArc archive: {self.filename}")
        print(f"  Size: {self.filesize:,} bytes")
        print(f"  Version: {self.version_str}")
        print(f"  Locked: {self.footer['locked']}")
        if self.footer['comment']:
            print(f"  Comment: {self.footer['comment']}")
        if self.footer['recovery_settings']:
            print(f"  Recovery: {self.footer['recovery_settings']}")
        print(f"  Control blocks: {len(self.footer['control_blocks'])}")
        for cb in self.footer['control_blocks']:
            print(f"    [{cb['type_name']}] comp={cb['compressor']!r} "
                  f"orig={cb['orig_size']} comp={cb['comp_size']}")
        print()

        total_files = 0
        total_dirs = 0
        total_size = 0
        total_comp = 0
        for solid_blocks, files, _ in self.dir_groups:
            for f in files:
                if f.is_dir:
                    total_dirs += 1
                else:
                    total_files += 1
                    total_size += f.size
            for sb in solid_blocks:
                total_comp += sb.comp_size

        print(f"  Directories: {total_dirs}")
        print(f"  Files: {total_files}")
        print(f"  Total uncompressed: {total_size:,} bytes")
        print(f"  Total compressed: {total_comp:,} bytes")
        if total_size > 0:
            ratio = total_comp / total_size * 100
            print(f"  Ratio: {ratio:.1f}%")
        print()

        print("Date/time                  Size  Filename")
        print("-" * 60)
        for _, files, _ in self.dir_groups:
            for f in files:
                if f.is_dir:
                    ts = datetime.datetime.fromtimestamp(f.timestamp).strftime('%Y-%m-%d %H:%M:%S') if f.timestamp else '                   '
                    print(f"{ts}           {f.full_path}/")
                else:
                    ts = datetime.datetime.fromtimestamp(f.timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    print(f"{ts}  {f.size:>10}  {f.full_path}")
        print("-" * 60)

    def extract(self, outdir):
        """Extract all files to the given output directory."""
        os.makedirs(outdir, exist_ok=True)

        all_files = self.all_files
        if not all_files:
            print("Archive is empty, nothing to extract.")
            return True

        # Find working unarc tool(s)
        candidates = _find_unarc_candidates()
        if not candidates:
            print("ERROR: Cannot find a working unarc decompressor.", file=sys.stderr)
            print("Looked for:", file=sys.stderr)
            print("  - UNARC_PATH environment variable", file=sys.stderr)
            print("  - wine + unarc.exe (in script dir or /tmp/unarc/)", file=sys.stderr)
            print("  - native 'unarc' in PATH or common locations", file=sys.stderr)
            return False

        abs_outdir = os.path.abspath(outdir)
        abs_archive = self.filename

        # Try each candidate until one succeeds
        success = False
        for unarc_cmd in candidates:
            # Clean output dir before each attempt
            if os.path.exists(abs_outdir):
                for item in os.listdir(abs_outdir):
                    item_path = os.path.join(abs_outdir, item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)

            if unarc_cmd[0].endswith('wine') or 'wine' in unarc_cmd[0]:
                success = _extract_wine(unarc_cmd, abs_archive, abs_outdir)
            else:
                success = _extract_native(unarc_cmd, abs_archive, abs_outdir)

            if success:
                break
            print(f"  (Trying next decompressor...)\n")

        if not success:
            return False

        # Verify extracted files
        print("\nVerifying extracted files...")
        ok_count = 0
        fail_count = 0
        for f in all_files:
            if f.is_dir:
                continue
            # Normalize path separators
            rel_path = f.full_path.replace('\\', '/')
            extracted_path = os.path.join(abs_outdir, rel_path)
            if not os.path.exists(extracted_path):
                print(f"  MISSING: {rel_path}")
                fail_count += 1
                continue

            with open(extracted_path, 'rb') as fh:
                file_data = fh.read()

            if len(file_data) != f.size:
                print(f"  SIZE MISMATCH: {rel_path} "
                      f"(expected {f.size}, got {len(file_data)})")
                fail_count += 1
                continue

            calc_crc = zlib.crc32(file_data) & 0xFFFFFFFF
            if calc_crc != f.crc:
                print(f"  CRC MISMATCH: {rel_path} "
                      f"(expected 0x{f.crc:08x}, got 0x{calc_crc:08x})")
                fail_count += 1
            else:
                ok_count += 1

            # Restore timestamp
            if f.timestamp > 0:
                os.utime(extracted_path, (f.timestamp, f.timestamp))

        print(f"\nVerification: {ok_count} OK, {fail_count} failed")
        return fail_count == 0


# ── External unarc tool handling ─────────────────────────────────────────

def _find_unarc_candidates():
    """Find all candidate unarc decompressors. Returns list of command lists.

    Returns candidates in order of preference: wine+unarc.exe first (more
    reliable), then native unarc binaries.
    """
    candidates = []

    # 1. Check UNARC_PATH environment variable (highest priority)
    env_path = os.environ.get('UNARC_PATH')
    if env_path and os.path.isfile(env_path):
        if env_path.endswith('.exe'):
            wine = shutil.which('wine')
            if wine:
                candidates.append([wine, env_path])
        else:
            candidates.append([env_path])

    # 2. Native unarc binary (32-bit build) in script dir or common locations
    #    Must be compiled as 32-bit (-m32) due to PPMD 32-bit pointer assumptions
    script_dir = os.path.dirname(os.path.abspath(__file__))
    native_paths = [
        os.path.join(script_dir, 'unarc_bin'),
        os.path.join(script_dir, 'unarc'),
        '/tmp/unarc/unarc',
        '/usr/local/bin/unarc',
    ]
    for path in native_paths:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            cmd = [path]
            if cmd not in candidates:
                candidates.append(cmd)

    # 3. Native unarc in PATH
    native = shutil.which('unarc')
    if native:
        cmd = [native]
        if cmd not in candidates:
            candidates.append(cmd)

    # 4. Fallback: wine + unarc.exe
    wine = shutil.which('wine')
    if wine:
        exe_candidates = [
            os.path.join(script_dir, 'unarc.exe'),
            '/tmp/unarc/unarc.exe',
        ]
        for exe in exe_candidates:
            if os.path.isfile(exe):
                cmd = [wine, exe]
                if cmd not in candidates:
                    candidates.append(cmd)

    return candidates


def _extract_native(unarc_cmd, archive, outdir):
    """Extract using native unarc binary."""
    cmd = unarc_cmd + ['x', '-o+', f'-dp{outdir}', archive]
    print(f"Extracting with: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"unarc failed (exit {result.returncode}):", file=sys.stderr)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        if result.stdout:
            print(result.stdout, file=sys.stderr)
        return False
    return True


def _extract_wine(unarc_cmd, archive, outdir):
    """Extract using wine + unarc.exe."""
    # Wine unarc.exe doesn't handle -dp well with Unix paths.
    # Instead, run from the output directory and use relative paths.
    os.makedirs(outdir, exist_ok=True)
    cmd = unarc_cmd + ['x', '-o+', archive]
    print(f"Extracting with: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        cwd=outdir,
        capture_output=True,
        text=True,
    )
    # Filter out wine debug messages
    stdout_lines = [
        line for line in (result.stdout or '').splitlines()
        if not line.startswith(('0', '  ')) or 'Extracting' in line or 'All OK' in line
    ]
    if stdout_lines:
        for line in stdout_lines:
            print(f"  {line}")

    if result.returncode != 0:
        # Wine may return non-zero even on success due to debug messages
        # Check if "All OK" appeared in output
        all_output = (result.stdout or '') + (result.stderr or '')
        if 'All OK' not in all_output:
            print(f"unarc.exe failed (exit {result.returncode}):", file=sys.stderr)
            stderr_clean = '\n'.join(
                line for line in (result.stderr or '').splitlines()
                if not line.startswith(('0', '  '))
            )
            if stderr_clean.strip():
                print(stderr_clean, file=sys.stderr)
            return False
    return True


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inputFile> <outputDir>", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(input_file):
        print(f"Error: '{input_file}' not found", file=sys.stderr)
        sys.exit(1)

    try:
        arc = FreeArcArchive(input_file)
    except Exception as e:
        print(f"Error parsing archive: {e}", file=sys.stderr)
        sys.exit(1)

    arc.print_info()

    success = arc.extract(output_dir)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

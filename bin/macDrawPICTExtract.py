#!/usr/bin/env python3
# Vibe coded by Codex
"""Extract a MacDraw-wrapped PICT into a standalone .pict file.

Usage: python3 macDrawPICTExtract.py inputFile output.pict

Only Python's standard library is required. The MacDraw wrapper is replaced
with the standard 512 zero-byte PICT file header; everything from input offset
512 onward is copied unchanged. In particular, the unreliable 16-bit picture
size is never used to truncate the data. Both PICT v1 and v2 are recognized.
This checks the wrapper and version marker, not the internal picture opcodes;
damaged picture data is preserved rather than repaired or interpreted.

PICT file header reference:
https://developer.apple.com/documentation/appkit/nspictimagerep/pictrepresentation
"""

import argparse
import os
from pathlib import Path
import sys
import tempfile


class FormatError(ValueError):
    """The input does not have a supported MacDraw PICT-export prefix."""


def extract_pict(data):
    """Return a PICT file, preserving the complete embedded picture stream."""
    signature = data[:8]
    if signature not in (b"DRWGD2\x00\x06", b"DRWG\x00\x00\x00\x00",
                         b"DRWGMD\x00\x06"):
        raise FormatError("expected a MacDraw PICT-export wrapper")
    if not (data[522:524] == b"\x11\x01" or
            data[522:526] == b"\x00\x11\x02\xff"):
        raise FormatError("missing PICT v1/v2 version marker at offset 522")
    # The unversioned signature is also used by native documents. Exports
    # have no native layer counts or storage zones; other preferences can
    # be nonzero and are deliberately not used as identification criteria.
    if signature == b"DRWG\x00\x00\x00\x00" and any(data[256:500]):
        raise FormatError("unversioned DRWG header contains native document state")
    return bytes(512) + data[512:]


def write_atomic(path, data):
    """Commit only after extraction succeeds; leave an existing file on error."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
                prefix=".macDrawPICTExtract-", dir=path.parent, delete=False) as out:
            temporary = out.name
            out.write(data)
            out.flush()
            os.fsync(out.fileno())
            os.fchmod(out.fileno(), 0o664)
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            os.unlink(temporary)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputFile", type=Path)
    parser.add_argument("outputFile", type=Path, metavar="output.pict")
    args = parser.parse_args(argv)
    try:
        if args.inputFile.resolve() == args.outputFile.resolve():
            raise FormatError("input and output must be different files")
        if args.outputFile.exists() and os.path.samefile(args.inputFile, args.outputFile):
            raise FormatError("input and output are aliases of the same file")
        result = extract_pict(args.inputFile.read_bytes())
        write_atomic(args.outputFile, result)
    except (FormatError, OSError, MemoryError) as error:
        print(f"macDrawPICTExtract: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

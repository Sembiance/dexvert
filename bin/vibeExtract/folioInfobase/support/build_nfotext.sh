#!/usr/bin/env bash
# Vibe coded by Claude
# Build the headless Folio .NFO -> text + embedded-object driver (nfotext.exe)
# with 32-bit MinGW.  The exe must live next to the Folio32 engine DLLs so its
# dependencies (nfomgr4.dll et al.) resolve at load time.
set -eu
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FOLIO32="${FOLIO32_DIR:-$HERE/folio32}"
i686-w64-mingw32-gcc -O2 -o "$FOLIO32/nfotext.exe" "$HERE/nfotext.c" -lgdi32 -lole32
echo "built $FOLIO32/nfotext.exe"

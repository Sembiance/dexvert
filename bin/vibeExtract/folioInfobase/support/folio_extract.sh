#!/usr/bin/env bash
# Vibe coded by Claude
#
# folio_extract.sh <infobase.nfo> [output.txt] [objdir]
#
# Emit PERFECT plain body text from any Folio .NFO infobase by driving the real
# 32-bit Folio Views 4.2 engine (nfomgr4.dll + fcsrv4b/fcsrv3b servers) under
# wine, fully headless (no window, no dialog).  If <output.txt> is omitted the
# text is written to stdout.  If <objdir> is given, embedded objects (images:
# BMP/GIF/WMF/OLE/... as-is, no conversion) are also written there.
#
# The heavy lifting is in nfotext.exe (see nfotext.c): it opens the infobase,
# builds a "[Include:[universe] [fulltext]]" binder (all records, reading order)
# and streams every record's FIF text through a callback -- handling native 4.x,
# 3.1 and (with a version-binding shim) 3.0 infobases.
#
# ---- ISOLATION / PARALLEL SAFETY -------------------------------------------
# Every run executes inside a PRIVATE, self-deleting sandbox created under $TMPDIR:
# its own HOME, its own wine prefix, its own XDG_*/TMP dirs.  Consequences:
#   * Your real home (~/.wine, ~/.config, ~/.cache) is NEVER read or written.
#   * On exit it kills ONLY its own wine server (wineserver -k is scoped to this
#     run's WINEPREFIX) and deletes ONLY its own sandbox -- it never touches other
#     wine/dosbox/Xvfb processes or prefixes.
#   * Any number of copies may run concurrently against different infobases with
#     zero shared mutable state; they cannot interfere with each other.
# A fresh prefix bootstrap (wineboot + engine regsvr32) costs only ~3 s, so this
# isolation is cheap.  (The engine DLLs in $FOLIO32 are shared READ-ONLY at
# run time; the one-time rights-gate self-heal is serialised with a lock.)
#
# Env overrides:
#   FOLIO32_DIR   engine dir (default: <this script's dir>/folio32)
#   TMPDIR        where the private sandbox is created (default /tmp); must be a
#                 user-owned location (wine refuses a prefix under a non-owned dir).
set -u

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FOLIO32="${FOLIO32_DIR:-$HERE/folio32}"
DRIVER="$FOLIO32/nfotext.exe"

WINE="$(command -v wine || true)"
[ -z "$WINE" ] && { echo "folio_extract: wine not found" >&2; exit 127; }
[ -f "$DRIVER" ] || { echo "folio_extract: driver missing ($DRIVER)" >&2; exit 127; }

usage() { echo "usage: folio_extract.sh <infobase.nfo> [output.txt] [objdir]" >&2; exit 2; }
[ $# -ge 1 ] || usage
IN="$1"; OUT="${2:-}"; OBJDIR="${3:-}"
[ -f "$IN" ] || { echo "folio_extract: no such file: $IN" >&2; exit 2; }

# ---- private, self-cleaning sandbox (no $HOME reliance; parallel-safe) -------
TMPROOT="${TMPDIR:-/tmp}"
RUN="$(mktemp -d "$TMPROOT/folio_run.XXXXXX")" || { echo "folio_extract: mktemp failed" >&2; exit 1; }
export HOME="$RUN/home"
export WINEPREFIX="$RUN/prefix"     # ignores any inherited WINEPREFIX on purpose
export XDG_CONFIG_HOME="$HOME/.config" XDG_CACHE_HOME="$HOME/.cache" \
       XDG_DATA_HOME="$HOME/.local/share" XDG_STATE_HOME="$HOME/.local/state" \
       XDG_RUNTIME_DIR="$RUN/run"
export TMPDIR="$RUN/tmp"
mkdir -p "$HOME" "$XDG_RUNTIME_DIR" "$TMPDIR"
export WINEDEBUG="${WINEDEBUG:--all}"
export DISPLAY=                     # hard no-GUI constraint: never open a window
export WINEDLLOVERRIDES="mscoree,mshtml=d"

cleanup() {
    "$WINE"server -k >/dev/null 2>&1     # WINEPREFIX-scoped: only THIS run's server
    rm -rf "$RUN" 2>/dev/null
}
trap cleanup EXIT INT TERM

NOISE='libEGL|pci id for fd|kmsro:|dri2 screen|DRI2:|/dev/dri|MESA|failed to (open|create)'

# ---- rights-gate bypass: stub rights server + patched servers ---------------
# Folio "DRM" is a rights GATE, never content encryption (see folioDatabase.txt
# section 5).  The engine DLLs ship pre-patched; this block is an idempotent
# self-heal that re-applies the (reversible) force-grants if an original is
# restored.  It writes to the SHARED $FOLIO32, so it is serialised with a lock so
# parallel first-runs cannot race.  Each original is preserved as <dll>.orig.
#   fcsrv3b.dll @0x36B7B 75 05->90 90   riassv3 token memcmp -> always pass  (gate A)
#   fcsrv3b.dll @0x36FE9 74 27->EB 27   access-control "Guest" gate           (gate C)
#   fcsrv3b.dll @0x3BACE 75 19->EB 19   3.0 server-binding accept-any         (gate D)
#   rmsrv4.dll  @0xB948  -> xor eax,eax; jmp   4.x .LCF force-grant           (gate B)
#   fcsrv4b.dll @0x49AF6 74 16->EB 16   skip empty-level raise after grant    (gate B)
ensure_rights_bypass() {
    local stub="$FOLIO32/riassv3.dll" src="$HERE/riassv3_stub.c" def="$HERE/riassv3_stub.def"
    if [ ! -f "$stub" ] && [ -f "$src" ]; then
        command -v i686-w64-mingw32-gcc >/dev/null 2>&1 && \
          i686-w64-mingw32-gcc -O2 -shared -o "$stub" "$src" "$def" \
              -Wl,--enable-stdcall-fixup 2>/dev/null || true
    fi
    if command -v python3 >/dev/null 2>&1; then
        python3 - "$FOLIO32" <<'PY' 2>/dev/null || true
import sys, os, shutil
d=sys.argv[1]
patches=[
    ("fcsrv3b.dll", 0x36b7b, bytes([0x75,0x05]),                  bytes([0x90,0x90])),
    ("fcsrv3b.dll", 0x36FE9, bytes([0x74,0x27]),                  bytes([0xEB,0x27])),
    ("fcsrv3b.dll", 0x3BACE, bytes([0x75,0x19]),                  bytes([0xEB,0x19])),
    ("rmsrv4.dll",  0xB948,  bytes.fromhex("6681bd50ffffff1104"), bytes.fromhex("31c0e9600300009090")),
    ("fcsrv4b.dll", 0x49AF6, bytes([0x74,0x16]),                  bytes([0xEB,0x16])),
]
for name, off, before, after in patches:
    fn=os.path.join(d, name)
    if not os.path.exists(fn): continue
    b=bytearray(open(fn,'rb').read())
    if b[off:off+len(before)]==before:
        if not os.path.exists(fn+'.orig'): shutil.copy(fn, fn+'.orig')
        b[off:off+len(after)]=after; open(fn,'wb').write(b)
PY
    fi
}
( flock 8; ensure_rights_bypass ) 8>"$TMPROOT/.folio_patch.$(id -u).lock" 2>/dev/null || ensure_rights_bypass

# ---- bootstrap the private prefix + register the Folio server plug-ins (~3s) -
"$WINE"boot --init >/dev/null 2>&1 || wineboot --init >/dev/null 2>&1
"$WINE" reg add "HKCU\\Software\\Wine\\WineDbg" /v ShowCrashDialog \
        /t REG_DWORD /d 0 /f >/dev/null 2>&1
for dll in fcsrv4b nfoeng4 nfosrv4 nfoenu4 nfomgr4 fcsrv3b \
           NFOFLT4 FrToText tortf rmsrv4 \
           FcShell4 FcBmp4 FcPict4 FcWmf4 FcHgx4 FcNet4; do
    ( cd "$FOLIO32" && "$WINE" regsvr32 /s "$dll.dll" ) >/dev/null 2>&1
done

# ---- resolve paths to Windows form + run ------------------------------------
IN_ABS="$(cd "$(dirname "$IN")" && pwd)/$(basename "$IN")"
WIN_IN="$("$WINE" winepath -w "$IN_ABS" 2>/dev/null)"

WIN_OBJ=""
if [ -n "$OBJDIR" ]; then
    mkdir -p "$OBJDIR"
    OBJ_ABS="$(cd "$OBJDIR" && pwd)"
    WIN_OBJ="$("$WINE" winepath -w "$OBJ_ABS" 2>/dev/null)"
fi

if [ -n "$OUT" ]; then
    : > "$OUT" || { echo "folio_extract: cannot write $OUT" >&2; exit 2; }
    OUT_ABS="$(cd "$(dirname "$OUT")" && pwd)/$(basename "$OUT")"
    WIN_OUT="$("$WINE" winepath -w "$OUT_ABS" 2>/dev/null)"
    ( cd "$FOLIO32" && "$WINE" nfotext.exe "$WIN_IN" "$WIN_OUT" ${WIN_OBJ:+"$WIN_OBJ"} ) \
        2> >(grep -avE "$NOISE" >&2)
    rc=$?
else
    ( cd "$FOLIO32" && "$WINE" nfotext.exe "$WIN_IN" ) 2> >(grep -avE "$NOISE" >&2)
    rc=$?
fi

# Convert Folio-native headerless bitmaps in the object dir to standard .bmp so they
# open in ordinary image viewers (real JPEG/GIF/WMF objects are left untouched).
if [ -n "$OBJDIR" ] && command -v python3 >/dev/null 2>&1; then
    python3 "$HERE/folio_objconv.py" "$OBJDIR" >/dev/null 2>&1 || true
fi
exit $rc

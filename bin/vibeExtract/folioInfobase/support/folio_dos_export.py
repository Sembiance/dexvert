#!/usr/bin/env python3
# Vibe coded by Claude
"""
folio_dos_export.py - extract PERFECT text from the OLDER, DOS-era Folio VIEWS 2.0
(.NFO) infobases that the 32-bit Folio Views 4.2 engine rejects.

These files carry the header signature "Copyright Folio Corp 1987-1990 v200.001" and use
2048-byte pages plus a proprietary character entropy coder.  Rather than reverse that
codec, this driver runs the ACTUAL period viewer -- Folio "PreVIEWS v2.1"
(support/dos20/flrules.exe, a 16-bit real-mode DOS binary that IS the 2.0 engine) --
fully headless under dosbox + its OWN Xvfb, and drives its File > Save As... > (scope)
Active view export to a text file.  The output is byte-for-byte what the real engine
renders (perfect), post-processed CP437+CRLF -> UTF-8 by the caller.

flrules.exe auto-opens the .nfo matching its basename ("flrules.nfo"), so to export ANY
2.0 infobase we copy it into a private work dir renamed to flrules.nfo.  Scope
"Active view" dumps every record in reading order.  Four Folio tutorial infobases are
export-password protected; pass a patched engine via exe=flrules_patched.exe for those.

ISOLATION / PARALLEL SAFETY:
  Every export runs in its OWN private, self-deleting work dir (mkdtemp), starts its OWN
  Xvfb on an auto-allocated free display (X -displayfd, never a fixed :99), gives dosbox a
  private HOME, and on finish kills ONLY the dosbox and Xvfb PROCESS GROUPS it launched --
  never `pkill dosbox`, never a shared display.  Any number of exports can run in parallel
  against different infobases without interfering, and nothing in your $HOME is used.

HARD REQUIREMENTS on PATH: dosbox, xdotool, ImageMagick `import`, Xvfb.
Usage:
  python3 folio_dos_export.py OUT_RAW_DIR NFO [NFO ...]         # export listed .nfo
  python3 folio_dos_export.py OUT_RAW_DIR --all                # export the standard set
  optional: --exe /path/to/flrules_patched.exe  (engine to use, default support/dos20/flrules.exe)
Each NFO -> OUT_RAW_DIR/<basename>.raw.txt (CP437/CRLF, raw as the engine writes it).
"""
import subprocess, os, sys, time, shutil, tempfile, select, signal

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # (only for the --all dev self-test below)
# The DOS 2.0 engine ships in the bundle next to this script so it relocates as a pair.
DEFAULT_EXE = os.path.join(HERE, "dos20", "flrules.exe")

# ---------------------------------------------------------------------------------------
# ORIGINAL / PRODUCT-BUNDLED viewers, archived in dos20/ for provenance and as fallbacks.
# A few very large 2.0 infobases in the dataset arrived WITH the exact retail viewer they
# shipped under; those viewers are byte-preserved here and mapped to their infobase (by
# basename) below.  Confirmed:
#   * Es7I6k87... ("Business", 344 MB)         <- p8 PREVIEWS.exe  (a GENERAL Folio VIEWS
#                                                  2.0 file-browser viewer; previews.cfg)
#   * nF7Ke...    ("General-Interest", 147 MB) <- p8 PREVIEWS.exe  (same browser opens it)
#   * 1uRzvy6A... ("HamCall", 113 MB)          <- p9 ham.exe (== manual.exe; opens straight
#                                                  into the Buckmaster HamCall search UI)
# In PRACTICE the extraction path (extract_body_via_dos_engine) uses flrules_compat.exe for
# ALL 2.0 infobases including these three: it is the SAME VIEWS 2.0 engine generation, was
# verified to open and export each of them byte-for-byte identically to its original viewer
# (HamCall: 158,612,156 B, matching ham.exe to within 1 byte), AND has the product-binding
# + save-privilege gates bypassed -- whereas the stock previews.exe/ham.exe do NOT (stock
# PREVIEWS raises "Privilege Denied" on some gated infobases).  flrules_compat is therefore
# strictly the better, more general engine.  This map is kept for provenance / manual use.
ORIGINAL_VIEWERS = {
    "Es7I6k87FDhHJ9idu8B9rngO3bMg78qR": os.path.join(HERE, "dos20", "previews.exe"),
    "nF7KeXeuVuUVBUc0whlmYELZI7JhHvpl": os.path.join(HERE, "dos20", "previews.exe"),
    "1uRzvy6AFAVKOC80mvqZVYB1bg2CBJSV": os.path.join(HERE, "dos20", "ham.exe"),
}


def viewer_for(nfo_path):
    """Return the archived ORIGINAL retail viewer bundled for this specific infobase, or
    None if there is no special mapping (caller then uses the default/compat engine)."""
    base = os.path.splitext(os.path.basename(nfo_path))[0]
    exe = ORIGINAL_VIEWERS.get(base)
    return exe if exe and os.path.exists(exe) else None

# The standard DOS-era 2.0 target set (relative to ROOT/p; dev self-test only).
ALL_TARGETS = [
    "p4/bible.nfo", "p4/compdict.nfo", "p4/comdex92.nfo", "p4/quotes.nfo",
    "p4/networld.nfo", "p4/sic.nfo", "p4/buyers.nfo", "p4/firmr.nfo",
    "p4/93sigcat.nfo", "p4/wp51.nfo", "p4/america.nfo", "p4/0__nfoq.nfo",
    "p4/pvmanual.nfo", "p4/concepts.nfo", "p4/tour.nfo", "p4/tour1.nfo",
    "p0/flrules.nfo", "p0/rtmanual.nfo",
]


def _start_xvfb():
    """Launch a private Xvfb on a free display (X picks it via -displayfd).
    Returns (":N", proc) or (None, None)."""
    r, w = os.pipe()
    os.set_inheritable(w, True)
    proc = subprocess.Popen(
        ["Xvfb", "-displayfd", str(w), "-screen", "0", "1024x768x24", "-nolisten", "tcp"],
        pass_fds=(w,), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True)
    os.close(w)
    buf, t0 = b"", time.time()
    while time.time() - t0 < 20 and b"\n" not in buf:
        if select.select([r], [], [], 1.0)[0]:
            chunk = os.read(r, 64)
            if not chunk:
                break
            buf += chunk
    os.close(r)
    num = buf.decode("ascii", "ignore").split()
    if not num:
        _killpg(proc)
        return None, None
    return ":" + num[0], proc


def _killpg(proc):
    """Kill only the process group we started (scoped; never global)."""
    if proc is None:
        return
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    except Exception:
        try: proc.kill()
        except Exception: pass
    try: proc.wait(timeout=5)
    except Exception: pass


def _xdo(env, *a):
    subprocess.run(["xdotool", *a], env=env, capture_output=True)


def _shot(env, p):
    subprocess.run(["import", "-window", "root", p], env=env, capture_output=True)


def _ncolors(p):
    try:
        from PIL import Image
        return len(Image.open(p).getcolors(999999) or [])
    except Exception:
        return 0


def _imgsig(p):
    """Coarse 32x32 grayscale signature of a screenshot (robust to a blinking cursor)."""
    try:
        from PIL import Image
        return Image.open(p).convert("L").resize((32, 32)).tobytes()
    except Exception:
        return None


def _wait_stable(env, shot, maxwait=45, need=2):
    """Poll the screen until it stops changing (loading/redraw finished), tolerating
    tiny changes like a blinking cursor.  Adapts to CPU load and slow-loading big
    infobases, replacing fragile fixed sleeps.  Returns True if it settled."""
    prev, stable, t0 = None, 0, time.time()
    while time.time() - t0 < maxwait:
        _shot(env, shot)
        sig = _imgsig(shot)
        if sig is not None and _ncolors(shot) > 4:
            if prev is not None:
                diff = sum(1 for a, b in zip(sig, prev) if abs(a - b) > 24)
                if diff <= 6:
                    stable += 1
                    if stable >= need:
                        return True
                else:
                    stable = 0
            prev = sig
        time.sleep(0.6)
    return False


def _wid(env, timeout=30):
    """Find our dosbox window -- on OUR private display only ours exists."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        r = subprocess.run(["xdotool", "search", "--class", "dosbox"],
                           env=env, capture_output=True, text=True)
        w = [x for x in r.stdout.split() if x]
        if w:
            return w[-1]
        time.sleep(0.3)
    return None


# The 16-bit real-mode DOS engine reads the infobase from disk ON DEMAND (it never loads
# the whole file into RAM), so file SIZE is not a blocker -- a 344 MB infobase opens and
# exports just like a small one, only slower.  For big infobases we therefore SYMLINK the
# .nfo into the sandbox instead of copying it (dosbox follows the host symlink on open),
# which avoids duplicating hundreds of MB per run.  Small ones are copied (cheap, and keeps
# the sandbox fully self-contained).  Verified: HamCall (113 MB) and Business (344 MB)
# export byte-perfectly via this path.
SYMLINK_THRESHOLD = int(os.environ.get("FOLIO_DOS_SYMLINK_MB", "32")) * 1024 * 1024


def export_one(nfo_path, out_raw, exe=DEFAULT_EXE, maxwait=300):
    """Export one 2.0 infobase to raw text via a fully private dosbox+Xvfb sandbox.
    Returns the byte size written, or None on failure.  Parallel-safe.  Large infobases
    are symlinked (not copied) into the sandbox and get a generous, size-scaled export
    timeout so very large ones (hundreds of MB) can finish."""
    insize = os.path.getsize(nfo_path) if os.path.exists(nfo_path) else 0
    # The export streams at roughly 0.5 MB/s of OUTPUT text; output runs ~1.5x the input
    # size, so allow ~8 s per input-MB (plus a floor) before giving up.  The loop below
    # still returns early the instant the output file stops growing, so this is only a cap.
    maxwait = max(maxwait, 600 + (insize // (1024 * 1024)) * 8)
    work = tempfile.mkdtemp(prefix="folio_dos_")
    home = os.path.join(work, "home"); os.makedirs(home, exist_ok=True)
    display, xvfb = _start_xvfb()
    dbx = None
    try:
        if not display:
            return None
        env = dict(os.environ, DISPLAY=display, HOME=home, SDL_AUDIODRIVER="dummy",
                   XDG_CONFIG_HOME=os.path.join(home, ".config"),
                   XDG_CACHE_HOME=os.path.join(home, ".cache"))
        shutil.copy(exe, os.path.join(work, "flrules.exe"))
        dst_nfo = os.path.join(work, "flrules.nfo")
        if insize and insize >= SYMLINK_THRESHOLD:
            os.symlink(os.path.abspath(nfo_path), dst_nfo)   # huge: don't duplicate
        else:
            shutil.copy(nfo_path, dst_nfo)
        conf = os.path.join(work, "dbx.conf")
        with open(conf, "w") as f:
            f.write("[sdl]\noutput=surface\nautolock=false\n[cpu]\ncore=auto\ncycles=max\n"
                    "[render]\naspect=false\n[autoexec]\nmount c %s\nc:\nflrules.exe\n" % work)
        dbx = subprocess.Popen(["dosbox", "-conf", conf], env=env,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                               start_new_session=True)
        wid = _wid(env)
        if not wid:
            return None
        shot = os.path.join(work, "render.png")
        _wait_stable(env, shot, maxwait=60)                            # dosbox booted + infobase opened
        _xdo(env, "key", "--window", wid, "space")                     # dismiss title record
        _wait_stable(env, shot, maxwait=30)                            # main view drawn
        _xdo(env, "key", "--window", wid, "alt+f"); time.sleep(1.2)    # File menu
        _xdo(env, "key", "--window", wid, "Down"); time.sleep(0.5)
        _xdo(env, "key", "--window", wid, "Down"); time.sleep(0.5)     # -> Save as...
        _xdo(env, "key", "--window", wid, "Return")
        _wait_stable(env, shot, maxwait=20)                            # Save As dialog open
        subprocess.run(["xdotool", "type", "--window", wid, "--delay", "80", "C:\\OUT.TXT"],
                       env=env, capture_output=True); time.sleep(0.9)
        _xdo(env, "key", "--window", wid, "Tab"); time.sleep(0.7)      # -> Scope group
        _xdo(env, "key", "--window", wid, "Down"); time.sleep(0.7)     # -> Active view
        _xdo(env, "key", "--window", wid, "space"); time.sleep(0.7)    # select it
        _xdo(env, "key", "--window", wid, "Return")                    # save
        outf = os.path.join(work, "OUT.TXT")
        prev, stable, t0 = -1, 0, time.time()
        while time.time() - t0 < maxwait:
            time.sleep(1.0)
            sz = os.path.getsize(outf) if os.path.exists(outf) else 0
            stable = stable + 1 if (sz == prev and sz > 0) else 0
            prev = sz
            if stable >= 4:
                break
        sz = os.path.getsize(outf) if os.path.exists(outf) else 0
        if sz > 0:
            os.makedirs(os.path.dirname(out_raw) or ".", exist_ok=True)
            shutil.copy(outf, out_raw)
            return sz
        return None
    finally:
        _killpg(dbx)          # only our dosbox process group
        _killpg(xvfb)         # only our Xvfb
        shutil.rmtree(work, ignore_errors=True)


def main(argv):
    if len(argv) < 2:
        print(__doc__); return 2
    out_dir = argv[1]
    exe = DEFAULT_EXE
    args = argv[2:]
    if "--exe" in args:
        i = args.index("--exe"); exe = args[i + 1]; del args[i:i + 2]
    if args == ["--all"]:
        nfos = [os.path.join(ROOT, "p", t) for t in ALL_TARGETS]
    else:
        nfos = args
    for nfo in nfos:
        base = os.path.splitext(os.path.basename(nfo))[0]
        out_raw = os.path.join(out_dir, base + ".raw.txt")
        t0 = time.time()
        sz = export_one(nfo, out_raw, exe=exe)
        print("%-16s -> %s (%s bytes, %.0fs)" % (base, out_raw, sz, time.time() - t0), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

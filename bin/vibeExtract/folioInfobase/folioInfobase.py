#!/usr/bin/env python3
# Vibe coded by Claude
"""
folioDatabase.py [--all] <input.nfo> <outputDir>

Extract content -- above all the rendered BODY TEXT -- from ANY Folio Infobase (.NFO):
Folio VIEWS 2.0, 3.0, 3.1 and 4.x, headlessly (never opens a window).

The .NFO body is compressed by a proprietary character entropy coder that lives only
inside Folio's own engines.  Rather than re-implement it, this tool DRIVES THE REAL
FOLIO ENGINES (shipped in the ./support/ bundle beside this script) and takes their
byte-perfect rendered output.  Three body-text paths are tried in order and the first
that yields text wins:
  1. Folio Views 4.2 engine (32-bit nfomgr4.dll) under wine, via support/folio_extract.sh
     -- handles 4.x, 3.1 and (with a version-binding shim) 3.0 infobases.
  2. Folio "PreVIEWS" 2.1 DOS engine (support/dos20/flrules.exe) under dosbox+Xvfb, via
     support/folio_dos_export.py -- handles the DOS-era 2.0 format the 4.2 engine rejects.
  3. Pure-Python 3.1 record-content decompressor (support/folio_codec.py) -- a no-deps
     fallback used only when wine/the engines are unavailable.
See folioDatabase.txt for the full .NFO format spec, the version map, the rights-gate
bypasses, and what these files contain (including embedded images/objects).

Requirements: the ./support/ bundle must sit next to this script.  Path 1 needs `wine`;
path 2 needs `dosbox`, `xdotool`, ImageMagick `import` and an Xvfb display (:99 default).
The support bundle + this script are self-contained and relocate together to any system.

Outputs written to <outputDir>:
  DEFAULT -- the extracted CONTENT only:
    * body.txt      -- the rendered record body text (the main deliverable)
    * <images>      -- embedded objects (BMP/GIF/WMF/JPEG/OLE...) written at the TOP
                       LEVEL alongside body.txt, as-is (Folio's headerless bitmaps
                       converted to viewable .bmp); engine path only
  With --all -- additionally the auxiliary / metadata files:
    * metadata.txt  -- copyright, infobase name, format signature
    * vocabulary.txt-- the infobase word list (search index), negation-decoded
    * references.txt / topical_guide.txt -- search-index apparatus (index-heavy infobases)
    * title.txt/.ans-- CP437 title screen (DOS-era infobases only)
    * MANIFEST.txt  -- extraction summary
"""
import sys, os, struct, subprocess, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
# Relocatable engine bundle (folio32/ wine engine, dos20/ DOS engine, helper scripts).
# Keep support/ next to this script; the pair moves to any system together.
SUPPORT = os.path.join(HERE, 'support')
sys.path.insert(0, SUPPORT)
try:
    import folio_codec
except Exception:
    folio_codec = None
try:
    import folio_dos_export
except Exception:
    folio_dos_export = None


def extract_body_via_engine(inp, outdir):
    """PRIMARY body-text path: drive the real 32-bit Folio Views 4.2 engine
    (nfomgr4.dll) under wine via folio_engine/folio_extract.sh, which emits
    byte-perfect rendered prose for every record (native 4.x AND older 3.1
    infobases such as the LDS Basic Library).  Returns the body.txt path on
    success, or None if wine/the engine is unavailable or produced nothing
    (caller then falls back to the pure-Python folio_codec decoder)."""
    script = os.path.join(SUPPORT, 'folio_extract.sh')
    if not os.path.exists(script) or shutil.which('wine') is None:
        return None
    body = os.path.join(outdir, 'body.txt')
    objdir = os.path.join(outdir, 'objects')   # embedded objects (images) extracted as-is
    # Pin the engine to the bundled copy.  folio_extract.sh runs each call in a PRIVATE,
    # self-deleting wine sandbox (its own HOME/prefix/temp dirs) so parallel invocations
    # against different infobases never interfere and nothing in your $HOME is touched.
    env = dict(os.environ, FOLIO32_DIR=os.path.join(SUPPORT, 'folio32'))
    try:
        subprocess.run(['bash', script, os.path.abspath(inp), body, objdir],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       timeout=3600, env=env)
    except Exception:
        return None
    if os.path.isdir(objdir) and not os.listdir(objdir):
        try: os.rmdir(objdir)     # infobase had no embedded objects
        except OSError: pass
    if os.path.exists(body) and os.path.getsize(body) > 0:
        return body
    if os.path.exists(body):
        try: os.remove(body)      # drop empty file so fallback can write
        except OSError: pass
    return None


def flatten_objects(objdir, outdir):
    """Move extracted embedded objects from the temp objdir UP into outdir, so they land
    at the top level alongside body.txt (no objects/ subdirectory).  Renames on any
    collision with an existing output file, removes objdir, and returns the count."""
    if not os.path.isdir(objdir):
        return 0
    reserved = {'body.txt', 'metadata.txt', 'vocabulary.txt', 'references.txt',
                'topical_guide.txt', 'title.txt', 'title.ans', 'MANIFEST.txt'}
    n = 0
    for name in sorted(os.listdir(objdir)):
        src = os.path.join(objdir, name)
        if not os.path.isfile(src):
            continue
        stem, ext = os.path.splitext(name)
        dest = name
        k = 1
        while dest in reserved or os.path.exists(os.path.join(outdir, dest)):
            dest = '%s_%d%s' % (stem, k, ext); k += 1
        os.replace(src, os.path.join(outdir, dest))
        n += 1
    try: os.rmdir(objdir)
    except OSError: pass
    return n


def extract_body_via_dos_engine(inp, outdir):
    """OLDER-FORMAT body-text path for the DOS-era Folio VIEWS 2.0 infobases
    ("Copyright Folio Corp 1987-1990 v200.001").  The 4.2 wine engine REJECTS these
    (different, older on-disk format) and folio_codec (the 3.1 codec) mis-decodes them,
    so we run the ACTUAL period viewer -- Folio PreVIEWS v2.1 (p/p0/flrules.exe, the
    real 16-bit real-mode 2.0 engine) -- fully headless under dosbox+Xvfb and drive its
    File>Save As > Active view export.  The result is byte-perfect engine-rendered text.
    See folio_engine/folio_dos_export.py.  Returns body.txt path or None if the headless
    stack (Xvfb/dosbox/xdotool/ImageMagick) is unavailable or nothing was produced
    (caller then falls back to folio_codec).  A password-protected infobase needs a
    patched engine at p/p0/flrules_patched.exe (auto-used when present)."""
    if folio_dos_export is None:
        return None
    # folio_dos_export starts its OWN private Xvfb + dosbox (parallel-safe); all four
    # must be on PATH.  Nothing in $HOME is used and only launched processes are killed.
    if not all(shutil.which(t) for t in ('dosbox', 'xdotool', 'import', 'Xvfb')):
        return None
    # Prefer flrules_compat.exe: the DOS runtime with the product-binding gate bypassed
    # (opens "foreign" 2.0 infobases) AND the save-privilege gate bypassed; fall back to
    # the save-privilege-only build, then the stock viewer.
    exe = os.path.join(SUPPORT, 'dos20', 'flrules_compat.exe')
    for alt in ('flrules_patched.exe',):
        if not os.path.exists(exe):
            exe = os.path.join(SUPPORT, 'dos20', alt)
    if not os.path.exists(exe):
        exe = folio_dos_export.DEFAULT_EXE   # -> support/dos20/flrules.exe
    raw = os.path.join(outdir, '_dos_raw.txt')
    try:
        sz = folio_dos_export.export_one(os.path.abspath(inp), raw, exe=exe)
    except Exception:
        return None
    if not sz:
        return None
    # CP437 + CRLF -> UTF-8 body.txt
    txt = open(raw, 'rb').read().decode('cp437', 'replace').replace('\r\n', '\n').replace('\r', '\n')
    txt = '\n'.join(ln.rstrip() for ln in txt.split('\n'))
    while '\n\n\n\n' in txt:
        txt = txt.replace('\n\n\n\n', '\n\n\n')
    body = os.path.join(outdir, 'body.txt')
    with open(body, 'w') as f:
        f.write(txt.strip('\n') + '\n')
    try: os.remove(raw)
    except OSError: pass
    return body

def read(path):
    with open(path, 'rb') as f:
        return f.read()

def u16(d, o): return struct.unpack_from('<H', d, o)[0] if o+2 <= len(d) else 0
def u32(d, o): return struct.unpack_from('<I', d, o)[0] if o+4 <= len(d) else 0

CP437 = ''.join(chr(c) for c in range(256))  # replaced below with a proper CP437 map

def cp437(b):
    return b.decode('cp437', 'replace')

def is_folio(d):
    # Windows-era: "(c) Folio Corporation ... (Infobase)" ; DOS-era: "Copyright Folio Corp" @1292
    head = d[:0x60]
    if b'Folio Corporation' in head and b'Infobase' in head:
        return True
    if len(d) > 1292+20 and d[1292:1292+20] == b'Copyright Folio Corp':
        return True
    return False

def extract_metadata(d):
    lines = []
    # copyright string is the first CRLF-terminated line
    cr = d.find(b'\r\n')
    copyright = d[:cr].decode('latin1', 'replace') if 0 < cr < 0x60 else ''
    # infobase title/name follows the second CRLF (around 0x52)
    title = ''
    m = d.find(b'\r\n', cr+2)
    if 0 < m < 0x60:
        title = d[m+2:m+2+80].split(b'\x00')[0].decode('latin1', 'replace').strip()
    lines.append('Copyright: %s' % copyright)
    lines.append('Infobase name: %s' % title)
    # version byte / structural signature near 0xd4 (0x1a 0x20 0xef 0xcd 0xab 0x89)
    sig_off = d.find(b'\x1a\x20\xef\xcd\xab\x89')
    if sig_off >= 0:
        lines.append('Structure signature at offset: 0x%x' % sig_off)
        lines.append('Format code: %d' % d[sig_off+8] if sig_off+8 < len(d) else '')
    lines.append('File size: %d bytes (%d blocks of 2048)' % (len(d), (len(d)+2047)//2048))
    return '\n'.join(str(x) for x in lines) + '\n', title

def extract_title_screen(d):
    """Block 0 (first 0x50c bytes) is a DOS text-mode title image: char/attr byte pairs."""
    region = d[:0x50c]
    # decode as 80-col char/attr pairs; only chars (even bytes)
    text_rows = []
    ans_rows = []
    cols = 80
    chars = region[0::2]
    attrs = region[1::2]
    if not any(chars):
        return None, None
    for r in range(0, len(chars), cols):
        row_c = chars[r:r+cols]
        row_a = attrs[r:r+cols]
        line = cp437(bytes(b if b >= 0x20 else 0x20 for b in row_c)).rstrip()
        text_rows.append(line)
        # ANSI colored row
        ans = ''
        last = None
        for i, ch in enumerate(row_c):
            a = row_a[i] if i < len(row_a) else 0x07
            if a != last:
                fg = a & 0x0f; bg = (a >> 4) & 0x07
                fg_ansi = 30 + ((fg & 1) << 2 | (fg & 2) | (fg & 4) >> 2)
                bg_ansi = 40 + ((bg & 1) << 2 | (bg & 2) | (bg & 4) >> 2)
                bold = '1;' if fg & 8 else ''
                ans += '\x1b[%s%d;%dm' % (bold, fg_ansi, bg_ansi)
                last = a
            ans += cp437(bytes([ch if ch >= 0x20 else 0x20]))
        ans_rows.append(ans + '\x1b[0m')
    # trim trailing empty rows
    while text_rows and not text_rows[-1].strip():
        text_rows.pop(); ans_rows.pop()
    if not any(r.strip() for r in text_rows):
        return None, None
    return '\n'.join(text_rows) + '\n', '\n'.join(ans_rows) + '\n'

def extract_vocabulary(d):
    """Extract the infobase's word vocabulary from its dictionary/word-index blocks.

    In the Folio VIEWS 3.1 (Windows) .NFO format the per-infobase word tables are stored
    byte-negated (real = (-b) & 0xFF), NOT XOR-0xFF.  Blocks that decode to many word-like
    tokens are the dictionary / search index; their tokens are the infobase's vocabulary.
    This is real textual content, though not the rendered body (see the manifest)."""
    import re
    BLOCK = 0x800
    nblocks = len(d) // BLOCK
    words = set()
    wordblocks = 0
    for i in range(1, nblocks):
        neg = bytes((-b) & 0xFF for b in d[i*BLOCK:(i+1)*BLOCK])
        toks = re.findall(rb'[a-z]{3,}', neg)
        if len(toks) < 20:
            continue
        wordblocks += 1
        for t in re.split(rb'[^a-z]+', neg):
            if len(t) >= 3:
                words.add(t.decode('ascii'))
    # keep word-like tokens (must contain a vowel, reasonable length) to drop index-pointer noise
    real = sorted(w for w in words if len(w) <= 18 and re.search('[aeiou]', w))
    return real, wordblocks

def extract_references(d):
    """Extract scripture references and topical-guide phrases from the search index.

    Rights-managed / compiled infobases (e.g. the LDS Basic Library) store the bulk of
    their content through a full-text SEARCH INDEX whose headwords are plain ASCII in the
    byte-negated index blocks: verse references ("1 nephi 11:2", "isaiah 16:5") and Topical
    Guide entries (prefixed "md="). These are the verbatim reference apparatus of the work
    -- real recoverable content -- decoded straight out of the negated blocks with no key.
    """
    import re
    neg = d.translate(_NEG)
    refpat = re.compile(rb'\b(?:[1-3] )?[a-z][a-z ]{2,14} \d{1,3}:\d{1,3}\b')
    refs = set()
    for m in refpat.finditer(neg):
        s = m.group().decode('latin1').strip()
        if 5 <= len(s) <= 28:
            refs.add(s)
    phrases = set(m.group()[3:].decode('latin1').strip()
                  for m in re.finditer(rb'md=[a-z][a-z ]{3,30}', neg))
    return sorted(refs), sorted(p for p in phrases if len(p) >= 4)


_NEG = bytes((256 - x) & 0xff for x in range(256))


def extract_structure(d):
    """Map the 2048-byte block types (first byte of each block after block 0)."""
    lines = ['block  offset    type']
    BLOCK = 0x800
    types = {0x01:'index-hdr',0x02:'index-root',0x03:'index-leaf',0x04:'btree-int',
             0x05:'posting',0x06:'btree-int2',0x07:'posting-pos',0x08:'record-fmt',
             0x09:'metadata',0x0a:'record-dir',0x0b:'content'}
    for i in range(1, min(len(d)//BLOCK, 4000)):
        t = d[i*BLOCK]
        lines.append('%5d  0x%06x  %02x %s' % (i, i*BLOCK, t, types.get(t, '')))
    return '\n'.join(lines) + '\n'

ENGINE_NOTE = """\
Body-text extraction
====================
The .NFO record body is decompressed in pure Python by folio_engine/folio_codec.py --
a reimplementation of Folio's own engine (FOLIOSERV / seg51) record-content codec,
verified byte-for-byte against the real engine under emulation.

The codec is NOT the lexicon/dictionary scheme long assumed; it is a 4-layer LZ:
base-8 nibble token reader -> adaptive order-0 rank model (301 symbols) -> 1 KB LZ77
window (min match 4) -> RLE (0xAC escape), over 4096-byte pages whose payload is
byte-negated with a CRC-16/ARC header.  A record's compressed bytes are scattered
across linked fragments (2-byte big-endian directory entries from page offset 0x14;
0x40 = chained via a trailing [u32 page][u16 offset] link, 0x20 = 6-byte header) and
reassembled before decoding.  The codec output is an interleaved [char][attribute]
pair stream; body.txt keeps the character bytes.  No external lexicon is required.

Some records (the search word-index / command reference) are stored plain rather than
LZ-compressed; the decoder tries both and keeps whichever reads as text, so those
come through with minor residual attribute-byte noise.  The full engine analysis
(SLR-OLOADER crack, the FEMETHOD API, the wine loadability of the rebuilt engine)
is in RE_NOTES.md and folio_engine/.

Rights management / "DRM":
Commercial infobases (e.g. the LDS Basic Library, ldsbl.nfo) ship a rights lock
(ldsbl.l00) and rightsmn.dll ("Folio Rights Management Runtime 3.1").  This was fully
reverse-engineered: rightsmn.dll is only a *rights-validation gate* (expiry dates +
permission bits), NOT a content cipher, and the engine's one block cipher (a CRC-16/ARC
keystream) is file-derivable -- so NO key or license data is needed to read the content.
These infobases store the bulk of their text as a full-text SEARCH INDEX whose reference
apparatus is recovered here (references.txt / topical_guide.txt / vocabulary.txt).  The
running reading-order prose is compressed by a separate proprietary character entropy
coder (model in .nfo blocks 3/4); reversing that last codec is the remaining step to
formatted verse text and is documented in folio_engine/ (a decoding problem, no crypto).
"""

def main():
    argv = sys.argv[1:]
    want_all = '--all' in argv                 # --all adds the auxiliary/metadata outputs
    pos = [a for a in argv if a != '--all']
    if len(pos) != 2:
        print(__doc__); sys.exit(2)
    inp, outdir = pos
    d = read(inp)
    os.makedirs(outdir, exist_ok=True)
    if not is_folio(d):
        print('Warning: %s does not look like a Folio Infobase NFO' % inp, file=sys.stderr)

    written = []
    meta, name = extract_metadata(d)           # computed for the manifest even without --all
    if want_all:
        with open(os.path.join(outdir, 'metadata.txt'), 'w') as f: f.write(meta)
        written.append('metadata.txt')

    # BODY TEXT + embedded OBJECTS are the primary content -- ALWAYS written.
    # Primary path: the real Folio engine under wine (byte-perfect, 3.1 + 4.x); then the
    # real DOS 2.0 engine (dosbox); then the pure-Python decompressor fallback.
    nbody = 0
    nobj = 0
    body_via = None
    dos_era = d[1292:1292+20] == b'Copyright Folio Corp'
    engine_body = extract_body_via_engine(inp, outdir)
    if engine_body:
        body_via = 'engine'
        nbody = -1  # record-count not tracked on the engine path (streamed)
        written.append('body.txt')
        # embedded objects are written at the top level alongside body.txt (not a subdir)
        nobj = flatten_objects(os.path.join(outdir, 'objects'), outdir)
        if nobj:
            written.append('%d object(s)' % nobj)
    elif dos_era and extract_body_via_dos_engine(inp, outdir):
        body_via = 'dos-engine'
        nbody = -1
        written.append('body.txt')
    elif folio_codec is not None:
        try:
            records = folio_codec.extract_records(d)
        except Exception as e:
            records = []
            print('body decode failed: %s' % e, file=sys.stderr)
        if records:
            with open(os.path.join(outdir, 'body.txt'), 'w') as f:
                for pg, off, nw, text in records:
                    f.write('----- record page %d @0x%x -----\n%s\n\n' % (pg, off, text))
            nbody = len(records)
            body_via = 'codec'
            written.append('body.txt')

    # ---- auxiliary / metadata outputs: ONLY with --all --------------------------
    vocab, wordblocks, nref, nphr = [], 0, 0, 0
    if want_all:
        # DOS-era CP437 title screen (block 0); Windows-era block 0 is compressed data.
        if dos_era:
            txt, ans = extract_title_screen(d)
            if txt and sum(ch.isalpha() for ch in txt) >= 12:
                with open(os.path.join(outdir, 'title.txt'), 'w') as f: f.write(txt)
                with open(os.path.join(outdir, 'title.ans'), 'w') as f: f.write(ans)
                written += ['title.txt', 'title.ans']

        vocab, wordblocks = extract_vocabulary(d)
        if vocab:
            with open(os.path.join(outdir, 'vocabulary.txt'), 'w') as f:
                f.write('\n'.join(vocab) + '\n')
            written.append('vocabulary.txt')

        # Search-index apparatus: verse references + Topical Guide phrases.
        refs, phrases = extract_references(d)
        if len(refs) >= 50:
            with open(os.path.join(outdir, 'references.txt'), 'w') as f:
                f.write('\n'.join(refs) + '\n')
            written.append('references.txt'); nref = len(refs)
        if len(phrases) >= 50:
            with open(os.path.join(outdir, 'topical_guide.txt'), 'w') as f:
                f.write('\n'.join(phrases) + '\n')
            written.append('topical_guide.txt'); nphr = len(phrases)

        with open(os.path.join(outdir, 'MANIFEST.txt'), 'w') as f:
            f.write('Folio Infobase extraction: %s\n' % os.path.basename(inp))
            f.write('=' * 60 + '\n\n')
            f.write(meta + '\n')
            if body_via == 'engine':
                f.write('Body text: extracted via the real Folio Views 4.2 engine under wine '
                        '(nfomgr4.dll, byte-perfect) -> body.txt\n')
                if nobj:
                    f.write('Embedded objects: %d written at top level alongside body.txt '
                            '(as-is by stored magic; Folio headerless bitmaps -> .bmp)\n' % nobj)
            elif body_via == 'dos-engine':
                f.write('Body text: extracted via the real Folio PreVIEWS 2.1 DOS engine '
                        '(dosbox, byte-perfect) -> body.txt\n')
            elif body_via == 'codec':
                f.write('Body text: %d records decoded (pure-Python record-content '
                        'decompressor fallback) -> body.txt\n' % nbody)
            if vocab:
                f.write('Vocabulary: %d unique words from %d word-index blocks '
                        '(negation-decoded) -> vocabulary.txt\n' % (len(vocab), wordblocks))
            if nref:
                f.write('Verse references: %d verbatim scripture references from the search '
                        'index -> references.txt\n' % nref)
            if nphr:
                f.write('Topical Guide: %d topical phrases from the search index '
                        '-> topical_guide.txt\n' % nphr)
            f.write('Files written: %s\n\n' % ', '.join(written))
            f.write(ENGINE_NOTE)
        written.append('MANIFEST.txt')

    print('Extracted %d file(s) to %s: %s' % (len(written), outdir, ', '.join(written) or '(none)'))
    print('Infobase: %s' % name)

if __name__ == '__main__':
    main()

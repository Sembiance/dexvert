#!/usr/bin/env python3
# Vibe coded by Claude
"""
folio_objconv.py <objdir> [<objdir> ...]

Post-process an extracted objects/ directory: convert Folio-native bitmap objects
into standard .BMP files so they open in ordinary image viewers.

A Folio bitmap object is a 2-byte type word followed by a HEADERLESS Windows DIB
(a BITMAPINFOHEADER + optional palette + pixel data, with NO 14-byte
BITMAPFILEHEADER), so `file` calls it "data" and no viewer opens it.  nfotext.exe
writes these verbatim (as .bin) because inventing a header at extraction time would
be a conversion.  This step performs that conversion explicitly and losslessly:
it strips the 2-byte type word and prepends a correct BITMAPFILEHEADER -- the pixel
data is untouched, only the standard file wrapper is added -- yielding a real .bmp.

Real images already in a normal container (JPEG/GIF/WMF/PNG/TIFF/...) are left
exactly as they are.  Idempotent and safe to re-run.
"""
import os, sys, struct

_IMGEXT = ('.jpg', '.jpeg', '.gif', '.png', '.bmp', '.wmf', '.emf', '.tif', '.tiff', '.pdf', '.ole')
_VALID_BPP = (1, 4, 8, 16, 24, 32)


def dib_to_bmp(d):
    """If d is a Folio DIB (2-byte type + BITMAPINFOHEADER), return standard BMP
    bytes; otherwise None.  Only the 14-byte file header is added (lossless)."""
    if len(d) < 2 + 40 + 4:
        return None
    biSize = struct.unpack_from('<I', d, 2)[0]
    if biSize != 40:                       # BITMAPINFOHEADER
        return None
    planes = struct.unpack_from('<H', d, 14)[0]
    bpp    = struct.unpack_from('<H', d, 16)[0]
    comp   = struct.unpack_from('<I', d, 22)[0]
    clrused = struct.unpack_from('<I', d, 34)[0]
    if planes != 1 or bpp not in _VALID_BPP:
        return None
    dib = d[2:]                            # BITMAPINFOHEADER + palette + pixels
    palette = clrused * 4 if clrused else ((1 << bpp) * 4 if bpp <= 8 else 0)
    extra = 12 if comp == 3 else 0         # BI_BITFIELDS stores 3 DWORD masks
    offbits = 14 + biSize + palette + extra
    filesize = 14 + len(dib)
    return b'BM' + struct.pack('<IHHI', filesize, 0, 0, offbits) + dib


def convert_dir(objdir):
    """Convert every Folio-DIB file in objdir to .bmp in place.  Returns #converted."""
    if not os.path.isdir(objdir):
        return 0
    n = 0
    for name in sorted(os.listdir(objdir)):
        p = os.path.join(objdir, name)
        if not os.path.isfile(p):
            continue
        try:
            with open(p, 'rb') as f:
                d = f.read()
        except OSError:
            continue
        bmp = dib_to_bmp(d)
        if bmp is None:                    # a real image or non-bitmap object: leave it
            continue
        base = name[:-4] if name.lower().endswith('.bin') else name
        stem, ext = os.path.splitext(base)
        if ext.lower() in _IMGEXT:         # drop a misleading original extension
            base = stem
        out = os.path.join(objdir, base + '.bmp')
        k = 1
        while os.path.exists(out) and os.path.abspath(out) != os.path.abspath(p):
            out = os.path.join(objdir, '%s_%d.bmp' % (base, k)); k += 1
        with open(out, 'wb') as f:
            f.write(bmp)
        if os.path.abspath(out) != os.path.abspath(p):
            os.remove(p)
        n += 1
    return n


if __name__ == '__main__':
    total = 0
    for d in sys.argv[1:]:
        total += convert_dir(d)
    print('%d Folio bitmap(s) -> BMP' % total)

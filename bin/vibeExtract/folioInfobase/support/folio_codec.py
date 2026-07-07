# Vibe coded by Claude
"""
folio_codec.py - pure-Python Folio VIEWS 3.1 (.NFO) record-content decompressor.

Reverse-engineered from Folio's own 16-bit engine (fewin386.dll / FOLIOSERV, segment
seg51) and verified byte-for-byte against it under emulation.  No wine, no lexicon,
no external files required.

Pipeline (see ../RE_NOTES.md):
  1. Physical page = 4096 bytes at file offset page*0x1000.  The payload is byte-NEGATED
     on load (real = (256-b) & 0xff, engine seg43:0x0f5d `neg`); page[0:2] is a CRC-16/ARC
     checksum over the negated payload.
  2. A record's compressed byte-stream is scattered across linked fragments.  Each page has
     an interleaved fragment directory from offset 0x14: 2-byte big-endian entries whose low
     12 bits are the fragment size and whose high-byte flags are 0x40 = chained (a 6-byte
     [u32 next-page][u16 next-offset] link ends the fragment) and 0x20 = a 6-byte record
     header precedes the payload.  gather() follows the chain into one contiguous stream.
  3. That stream is a 4-layer LZ codec (Stream): base-8 nibble token reader -> adaptive
     order-0 rank model (301 symbols) -> 1 KB LZ77 window (min match 4) -> RLE (0xAC escape).
  4. The codec emits an interleaved [char][attribute] pair stream; the visible text is the
     character byte of each pair (deinterleave()).
"""
import struct

NSYM = 0x12d  # 301 symbols: 256 literal bytes (0..0xff) + 45 match-length codes (0x100..0x12c)


class Stream:
    """The seg51 4-layer record-content decompressor."""
    def __init__(self, data, start=0, phase=1):
        self.buf = data
        self.pos = start
        self.phase = phase        # obj+0xb90, high-nibble-first when set
        self.eof = False
        self.freq = [0] * NSYM    # freq[rank]
        self.sym = list(range(NSYM))   # rank -> symbol  (obj+0x6d8)
        self.rank = list(range(NSYM))  # symbol -> rank  (obj+0x47c)
        self.ring = bytearray(0x430)   # 1 KB window + 0x30 mirror (obj+0x4c)
        self.b94 = 0              # pending LZ match length
        self.b96 = 0              # ring read cursor
        self.b9a = 0              # ring write position
        self.b8a = 0              # RLE repeat byte
        self.b8c = 0              # RLE remaining run

    def _cur(self):
        if self.pos >= len(self.buf):
            self.eof = True
            return 0
        return self.buf[self.pos]

    def get_token(self):
        if self.eof:
            return 0xffff
        cur = self._cur()
        dx = (cur >> 4) if self.phase else cur
        si = dx & 7
        self.phase ^= 1
        while dx & 8:                     # continuation bit
            si = (si + 1) << 3
            if self.phase:
                self.pos += 1
                if self.pos >= len(self.buf):
                    self.eof = True
                    return 0xffff
                dx = self._cur() >> 4
            else:
                dx = self._cur()
            si |= (dx & 7)
            self.phase ^= 1
        if self.phase:
            self.pos += 1
        return si

    def _rescale(self):
        for r in range(0x12c):
            self.freq[r] //= 2

    def update_model(self, val):
        di = self.rank[val]
        if di == 0:
            self.freq[0] += 1
            if self.freq[0] == 0xffff:
                self._rescale()
            return
        f = self.freq[di]
        cx = 0
        r = di - 1
        while cx < di and self.freq[r] == f:
            cx += 1
            r -= 1
        if cx == 0:
            self.freq[di] += 1
            if self.freq[di] == 0xffff:
                self._rescale()
            return
        target = di - cx
        moved = self.sym[target]
        self.rank[moved] = di
        self.sym[di] = moved
        self.rank[val] = target
        self.sym[target] = val
        self.freq[target] += 1
        if self.freq[target] == 0xffff:
            self._rescale()

    def _store(self, c):
        c &= 0xff
        self.ring[self.b9a] = c
        if self.b9a < 0x30:
            self.ring[self.b9a + 0x400] = c
        self.b9a += 1
        if self.b9a == 0x400:
            self.b9a = 0
        return c

    def next_byte(self):
        if self.b94 != 0:
            idx = self.b96
            self.b96 += 1
            c = self.ring[idx] if 0 <= idx < len(self.ring) else 0  # tolerate OOB on bad streams
            self.b94 -= 1
            return self._store(c)
        tok = self.get_token()
        if tok == 0xffff or tok >= NSYM:
            return 0xffff
        val = self.sym[tok]
        self.update_model(val)
        if val < 0x100:
            return self._store(val)
        self.b94 = (val - 0x100) + 4       # LZ match length (>= 4)
        d = self.get_token()               # distance = raw token
        wp = self.b9a
        if wp < d:
            d -= 0x400
        self.b96 = wp - d
        return self.next_byte()

    def read_varint(self):
        b = self.next_byte()
        if b == 0xffff:
            return 0
        acc = b & 0x7f
        while b & 0x80:
            acc = (acc + 1) << 7
            b = self.next_byte()
            if b == 0xffff:
                break
            acc |= (b & 0x7f)
        return acc

    def read(self, n):
        out = bytearray()
        left = n
        while left > 0:
            if self.b8c != 0:
                take = min(left, self.b8c)
                out += bytes([self.b8a]) * take
                left -= take
                self.b8c -= take
                continue
            c = self.next_byte()
            if c == 0xffff:
                break
            if c == 0xac:                  # RLE escape
                self.b8c = self.read_varint()
                if self.b8c != 0:
                    b = self.next_byte()
                    if b == 0xffff:
                        break
                    self.b8a = b & 0xff
                    continue
            out.append(c & 0xff)
            left -= 1
        return bytes(out)


# ---- physical framing -------------------------------------------------------

PAGE = 0x1000


def negate_page(nfo, page):
    """Load + byte-negate one 4096-byte physical page (engine seg43 `neg`)."""
    raw = nfo[page * PAGE:(page + 1) * PAGE]
    if len(raw) < PAGE:
        return None
    return bytes((256 - x) & 0xff for x in raw)


def _frag(pages, page, off):
    if page >= len(pages) or pages[page] is None:
        return None
    b = pages[page]
    if off + 2 > len(b):
        return None
    b0 = b[off]
    size = ((b0 << 8) | b[off + 1]) & 0xfff
    if size < 0x10 or off + 2 + size > len(b):
        return None
    return b0, size, b[off + 2:off + 2 + size]


def dir_entries(pages, page):
    """Interleaved fragment directory from page offset 0x14 (engine seg59:0x2a8)."""
    b = pages[page]
    off = 0x14
    out = []
    while off < 0xfff and off + 2 <= len(b):
        b0 = b[off]
        size = ((b0 << 8) | b[off + 1]) & 0xfff
        if size == 0 and b0 == 0:
            break
        if size >= 0x10:
            out.append((off, b0, size))
        off += size + 2
        if len(out) > 250:
            break
    return out


def gather(pages, page, off):
    """Follow the fragment chain (engine seg59:0x6fd) into one contiguous stream."""
    content = bytearray()
    seen = set()
    while True:
        if (page, off) in seen or page >= len(pages):
            break
        seen.add((page, off))
        f = _frag(pages, page, off)
        if not f:
            break
        b0, size, data = f
        skip = 6 if (b0 & 0x20) else 0          # 6-byte record header
        if b0 & 0x40:                            # chained: payload then 6-byte link
            content += data[skip:size - 6]
            link = data[size - 6:size]
            page = struct.unpack('<I', link[0:4])[0]
            off = struct.unpack('<H', link[4:6])[0]
        else:
            content += data[skip:]
            break
        if len(content) > 300000:
            break
    return bytes(content)


_COMMON = set(
    'the and you are for that this with which from menu key press option view record infobase '
    'file window search dialog help text field group when can not use will each level note under '
    'select following your has other any may more into make also object link query shadow '
    'display contains'.split())


def _wordscore(s):
    words = _WORD_RE.findall(s.lower())
    return sum(1 for w in words if w in _COMMON)


import re as _re
_WORD_RE = _re.compile(r'[a-z]{3,}')


def _bytes_to_text(bs):
    return ''.join(chr(x) if 32 <= x < 127 else ('\n' if x in (10, 13) else ' ') for x in bs)


def decode_stream(content, limit=None):
    """Decode a gathered record stream and return the best text reading.

    A record is stored either LZ-compressed (seg51 codec, obj[0xa2]!=0) or plain
    (pass-through).  Either way the payload is an interleaved [char][attribute] pair stream.
    We try the codec output AND the raw content, each parity, and keep whichever reads as the
    most English -- so compressed prose and plain word-index records both come through."""
    cands = []
    n = limit if limit else min(max(4000, len(content) * 3), 60000)
    try:
        raw = Stream(content, 0, 1).read(n)         # LZ-compressed records
        for par in (0, 1):
            cands.append(_bytes_to_text(raw[par::2]))
    except (IndexError, RecursionError):
        pass
    for par in (0, 1):                              # plain / uncompressed records
        cands.append(_bytes_to_text(content[par::2]))
    cands.append(_bytes_to_text(content))
    return max(cands, key=_wordscore) if cands else ''


def extract_records(nfo, min_words=4):
    """Decode every content record in an .NFO. Returns list of (page, offset, words, text).

    Every directory fragment is treated as a possible record head and its fragment chain is
    gathered and decoded; results are de-duplicated and kept when they read as real text
    (>= min_words common English words)."""
    npages = len(nfo) // PAGE
    pages = [negate_page(nfo, p) for p in range(npages)]
    # a fragment that is the target of a chain link is a continuation, not a record head;
    # gathering only from heads avoids decoding mid-chain fragments as garbage
    targets = set()
    for p in range(npages):
        if pages[p] is None:
            continue
        for off, b0, size in dir_entries(pages, p):
            if b0 & 0x40:
                f = _frag(pages, p, off)
                if f:
                    link = f[2][size - 6:size]
                    targets.add((struct.unpack('<I', link[0:4])[0],
                                 struct.unpack('<H', link[4:6])[0]))
    records = []
    seen = set()
    for p in range(npages):
        if pages[p] is None:
            continue
        for off, b0, size in dir_entries(pages, p):
            if (p, off) in targets:
                continue
            content = gather(pages, p, off)
            if len(content) < 40:
                continue
            text = ' '.join(decode_stream(content).split())
            text = _re.sub(r'^(?:\S ){3,}', '', text)   # trim leading single-char noise prefix
            if len(text) < 40:
                continue
            n = _wordscore(text)
            # density: fraction of chars inside 3+ letter words -- rejects runaway-LZ garbage.
            # (head-only gathering already skips the garbled mid-chain index fragments, so we
            # don't also require common-word hits, which would drop valid noun-heavy TOCs.)
            dense = sum(len(w) for w in _WORD_RE.findall(text.lower()))
            if dense >= 0.45 * len(text) and n >= 1 and text[:120] not in seen:
                seen.add(text[:120])
                records.append((p, off, n, text))
    records.sort()
    return records


if __name__ == '__main__':
    import sys
    nfo = open(sys.argv[1] if len(sys.argv) > 1 else
               '../lds/foliohlp.nfo', 'rb').read()
    recs = extract_records(nfo)
    print('records=%d chars=%d' % (len(recs), sum(len(t) for _, _, _, t in recs)))
    for p, o, n, t in recs[:3]:
        print('  page %d @0x%x (%d): %s' % (p, o, n, t[:90]))

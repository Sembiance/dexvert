#!/usr/bin/env python3
# Vibe coded by Claude

"""
HyperWriter 3 (.hw3) to RTF converter.

Usage: hw2rtf.py <input.hw3> <output.rtf>

Converts HyperWriter 3 document files to Rich Text Format.
Handles both v0B (version 11) and v0C (version 12) files.
"""

import struct
import sys
import os


# ---------------------------------------------------------------------------
# Low-level sector / chain helpers
# ---------------------------------------------------------------------------

SECTOR_SIZE = 64
SECTOR_DATA = 60
TRAILER_SIZE = 4


def read_sectors(data):
    """Split raw file data into (payload, trailer) tuples per sector."""
    sectors = []
    for i in range(0, len(data), SECTOR_SIZE):
        if i + SECTOR_SIZE > len(data):
            break
        payload = data[i : i + SECTOR_DATA]
        trailer = struct.unpack_from("<I", data, i + SECTOR_DATA)[0]
        sectors.append((payload, trailer))
    return sectors


def follow_chain(sectors, start, max_bytes=500000):
    """Read a byte stream by following sector chains.

    Chain rules:
      trailer == 0          -> continue to next consecutive sector
      trailer == 0xFFFFFFFF -> continue to next consecutive sector
      other                 -> jump to that sector number
    Reading stops when we exceed *max_bytes* or run out of sectors.
    """
    stream = bytearray()
    si = start
    visited = set()
    while 0 <= si < len(sectors) and len(stream) < max_bytes:
        if si in visited:
            break
        visited.add(si)
        payload, trailer = sectors[si]
        stream.extend(payload)
        if trailer == 0 or trailer == 0xFFFFFFFF:
            si += 1
        else:
            si = trailer
    return bytes(stream)


# ---------------------------------------------------------------------------
# Compression dictionaries (built into HyperWriter runtime)
# ---------------------------------------------------------------------------
# HW3 nodes have a compression flag byte (nd[0]):
#   0x00 = no compression (plain ASCII / CP437)
#   0x01 or 0x02 = compressed
# NOTE: nd[0] does NOT reliably indicate which table to use.
# Table selection is auto-detected per node by scoring body text.
# Table 1: word-ending fragments with trailing spaces
# Table 2: BPE bigram/trigram merges

COMPRESSION_TABLE = {
    0x80: "which ", 0x81: "be ",   0x82: "wh",    0x83: "com",
    0x84: "ments ", 0x85: "ities ", 0x86: "ility ", 0x87: "ction ",
    0x88: "tions ", 0x89: "ation ", 0x8A: "tic",  0x8B: "ated ",
    0x8C: "tory ", 0x8D: "ible ", 0x8E: "sion ",  0x8F: "ding ",
    0x90: "ting ", 0x91: "ment",  0x92: "ther ",  0x93: "this ",
    0x94: "ould ", 0x95: "ment ", 0x96: "able ",  0x97: "with ",
    0x98: " that ", 0x99: "tion ", 0x9A: "nder",  0x9B: "ure ",
    0x9C: "ven ",  0x9D: "ost ",  0x9E: "ory ",   0x9F: "ple ",
    0xA0: "der ",  0xA1: "uch ",  0xA2: "ork ",   0xA3: "ast ",
    0xA4: "now ",  0xA5: "ons ",  0xA6: "ood ",   0xA7: "ame ",
    0xA8: "ike ",  0xA9: "ether ", 0xAA: "ght ",  0xAB: "est ",
    0xAC: "sed ",  0xAD: "ess",   0xAE: "ooks ",  0xAF: "han ",
    0xB0: "ick ",  0xB1: "enu",   0xB2: "ugh ",   0xB3: "ess ",
    0xB4: "cal ",  0xB5: "ery ",  0xB6: "ust ",   0xB7: "hey ",
    0xB8: "ish ",  0xB9: "ers ",  0xBA: "had ",   0xBB: "een ",
    0xBC: "lly ",  0xBD: "nto ",  0xBE: "ver ",   0xBF: "ore ",
    0xC0: "ine ",  0xC1: "wit",   0xC2: "any ",   0xC3: "not ",
    0xC4: "and",   0xC5: " th",   0xC6: "nce ",   0xC7: "ted ",
    0xC8: "ome ",   0xC9: "ive ", 0xCA: "o ",     0xCB: "has ",
    0xCC: "ard ",  0xCD: "ite ",  0xCE: "can ",   0xCF: " back",
    0xD0: "ere ",  0xD1: "use ",  0xD2: "ill ",   0xD3: "ter ",
    0xD4: "all ",  0xD5: "was ",  0xD6: "one ",   0xD7: "his ",
    0xD8: "out ", 0xD9: "are ",   0xDA: "ful ",   0xDB: "ave ",
    0xDC: "for ",  0xDD: "ies ",  0xDE: "ous ",   0xDF: "hat ",
    0xE0: "ing ",  0xE1: "and ",  0xE2: "end ",   0xE3: "the ",
    0xE4: "ce ",   0xE5: "ot ",   0xE6: "ve ",    0xE7: "te ",
    0xE8: "th ",   0xE9: "li",    0xEA: "as ",    0xEB: "ts ",
    0xEC: "n ",    0xED: "ou ",   0xEE: "an ",    0xEF: "se ",
    0xF0: "ly ",   0xF1: "nt ",   0xF2: "al ",    0xF3: "in ",
    0xF4: "at ",   0xF5: "is ",   0xF6: "er ",    0xF7: "of ",
    0xF8: "or ",   0xF9: "es ",   0xFA: "to ",    0xFB: "ed ",
    0xFC: "on ",   0xFD: "he ",   0xFE: "it ",
}

COMPRESSION_TABLE2 = {
    0x80: "ation", 0x81: "which", 0x82: "other", 0x83: "that",
    0x84: "cial",  0x85: "with",  0x86: "ther",  0x87: "have",
    0x88: "here",  0x89: "ough",  0x8A: "ting",  0x8B: "ever",
    0x8C: "ould",  0x8D: "will",  0x8E: "able",  0x8F: "ding ",
    0x90: "very",  0x91: "ment",  0x92: "ther ", 0x93: "bout",
    0x94: "from",  0x95: "sion",  0x96: "able",  0x97: " with",
    0x98: "ound",  0x99: "read",  0x9A: "nder",  0x9B: "ure",
    0x9C: "than",  0x9D: "ost ",  0x9E: "file",  0x9F: "more",
    0xA0: "der ",  0xA1: "them",  0xA2: "good",  0xA3: "ding",
    0xA4: "tion",  0xA5: "ight",  0xA6: "also",  0xA7: "thou",
    0xA8: "cont",  0xA9: "king",  0xAA: "ght ",  0xAB: "est ",
    0xAC: "over",  0xAD: "just",  0xAE: "your",  0xAF: "han ",
    0xB0: "back",  0xB1: "when",  0xB2: "ugh ",  0xB3: "ess",
    0xB4: "cal ",  0xB5: "ette",  0xB6: "sing",  0xB7: "hey",
    0xB8: "need",  0xB9: "cess",  0xBA: "ture",  0xBB: "part",
    0xBC: "lly ",  0xBD: "been",  0xBE: "ver ",  0xBF: "ore ",
    0xC0: "mple",  0xC1: "on ",   0xC2: "ork",   0xC3: "the",
    0xC4: "and",   0xC5: "ing",   0xC6: "ion",   0xC7: "you",
    0xC8: "ter",   0xC9: "all",   0xCA: "her ",   0xCB: "for",
    0xCC: "ver",   0xCD: "hin",   0xCE: "ent",   0xCF: "are",
    0xD0: "pro",   0xD1: "ere",   0xD2: "ill ",   0xD3: "ive",
    0xD4: "all ",  0xD5: "com",   0xD6: "one",   0xD7: "his ",
    0xD8: "but",   0xD9: "out",   0xDA: "his",   0xDB: "ers ",
    0xDC: "ted ",  0xDD: "bly",   0xDE: "int",   0xDF: "was",
    0xE0: "ing ",  0xE1: "and ",  0xE2: "can",   0xE3: "ite",
    0xE4: "ort",   0xE5: "ar",    0xE6: "se",    0xE7: "of",
    0xE8: "di",    0xE9: "li",    0xEA: "nd",    0xEB: "ed",
    0xEC: "nt",    0xED: "te",    0xEE: "en",    0xEF: "al",
    0xF0: "es",    0xF1: "is",    0xF2: "or",    0xF3: "it",
    0xF4: "an",    0xF5: "io",    0xF6: "re",    0xF7: "at",
    0xF8: "er",    0xF9: "in",    0xFA: "he",    0xFB: "ti",
    0xFC: "on",    0xFD: "th",    0xFE: "st",
}


# ---------------------------------------------------------------------------
# HW3 file parser
# ---------------------------------------------------------------------------

# CP437 to Unicode mapping for bytes 0x80-0xFF
CP437_MAP = (
    "\u00C7\u00FC\u00E9\u00E2\u00E4\u00E0\u00E5\u00E7"  # 80-87
    "\u00EA\u00EB\u00E8\u00EF\u00EE\u00EC\u00C4\u00C5"  # 88-8F
    "\u00C9\u00E6\u00C6\u00F4\u00F6\u00F2\u00FB\u00F9"  # 90-97
    "\u00FF\u00D6\u00DC\u00A2\u00A3\u00A5\u20A7\u0192"  # 98-9F
    "\u00E1\u00ED\u00F3\u00FA\u00F1\u00D1\u00AA\u00BA"  # A0-A7
    "\u00BF\u2310\u00AC\u00BD\u00BC\u00A1\u00AB\u00BB"  # A8-AF
    "\u2591\u2592\u2593\u2502\u2524\u2561\u2562\u2556"  # B0-B7
    "\u2555\u2563\u2551\u2557\u255D\u255C\u255B\u2510"  # B8-BF
    "\u2514\u2534\u252C\u251C\u2500\u253C\u255E\u255F"  # C0-C7
    "\u255A\u2554\u2569\u2566\u2560\u2550\u256C\u2567"  # C8-CF
    "\u2568\u2564\u2565\u2559\u2558\u2552\u2553\u256B"  # D0-D7
    "\u256A\u2518\u250C\u2588\u2584\u258C\u2590\u2580"  # D8-DF
    "\u03B1\u00DF\u0393\u03C0\u03A3\u03C3\u00B5\u03C4"  # E0-E7
    "\u03A6\u0398\u03A9\u03B4\u221E\u03C6\u03B5\u2229"  # E8-EF
    "\u2261\u00B1\u2265\u2264\u2320\u2321\u00F7\u2248"  # F0-F7
    "\u00B0\u2219\u00B7\u221A\u207F\u00B2\u25A0\u00A0"  # F8-FF
)


def cp437_to_unicode(b):
    """Convert a single CP437 byte to a Unicode character."""
    if b < 0x80:
        return chr(b)
    return CP437_MAP[b - 0x80]



class HW3Style:
    """Represents a parsed style definition."""

    def __init__(self):
        self.name = ""
        self.font_name = ""
        self.font_size = 10
        self.bold = False
        self.italic = False
        self.centered = False


class HW3Node:
    """Represents a parsed text node."""

    def __init__(self):
        self.node_type = 0  # 1=Article, 3=Card, 4=Action
        self.title = ""
        self.tag_08 = -1  # Node ID from 0x08 header tag
        self.paragraphs = []  # list of (style_idx, content_elements)
        self.raw_content = b""


class HW3Document:
    """Parsed HyperWriter 3 document."""

    def __init__(self, filepath):
        self.filepath = filepath
        self.data = open(filepath, "rb").read()
        if len(self.data) < SECTOR_SIZE or self.data[:12] != b"HyperWriter!":
            raise ValueError(f"Not a HyperWriter file: {filepath}")

        self.sectors = read_sectors(self.data)
        self.version = self.data[13]  # 0x0B=v11, 0x0C=v12
        self.header = struct.unpack_from("<8H", self.data, 0x20)

        self._parse_indices()
        self._parse_styles()
        self._parse_nodes()

    def _parse_indices(self):
        """Parse the primary and node index tables."""
        pdata = follow_chain(self.sectors, 1)
        self.primary_index = []
        for j in range(0, min(self.header[0] * 6, len(pdata)), 6):
            s, m, c = struct.unpack_from("<HHH", pdata, j)
            self.primary_index.append((s, m, c))

        ndata = follow_chain(self.sectors, 2)
        self.node_index = []
        for j in range(0, min(self.header[1] * 6, len(ndata)), 6):
            s, m, c = struct.unpack_from("<HHH", ndata, j)
            self.node_index.append((s, m, c))

    def _parse_styles(self):
        """Parse style definitions from the style block."""
        self.styles = []
        if len(self.primary_index) <= 5:
            return
        style_sector = self.primary_index[5][0]
        if style_sector == 0:
            return

        style_data = follow_chain(self.sectors, style_sector)
        if not style_data:
            return

        pos = 0
        if self.version == 0x0C and len(style_data) >= 2:
            pos = 2

        rec_size = 60 if self.version == 0x0B else 72
        max_styles = self.primary_index[5][2] if len(self.primary_index) > 5 else 200

        while pos + rec_size <= len(style_data) and len(self.styles) < max_styles:
            rec = style_data[pos : pos + rec_size]
            style = HW3Style()

            flen = rec[0]
            if flen > 0 and flen < 20:
                style.font_name = rec[1 : 1 + flen].decode("ascii", errors="replace")

            if 34 < rec_size:
                slen = rec[34]
                if slen > 0 and slen < rec_size - 35:
                    style.name = rec[35 : 35 + slen].decode("ascii", errors="replace")

            self.styles.append(style)
            pos += rec_size

    def _find_body_start(self, content, is_compressed):
        """Find the true body start in node content.

        For nodes with embedded graphics/fonts, the first 0xFF may be
        inside binary data. We need to find the 0xFF that actually marks
        the start of text paragraphs.
        """
        # Find all 0xFF positions in the first portion of content
        ff_positions = []
        search_limit = min(len(content), 2000)
        for j in range(search_limit):
            if content[j] == 0xFF:
                ff_positions.append(j)

        if not ff_positions:
            return -1

        # Pass 1: Find 0xFF with strong text evidence (alpha chars in body)
        for ff_pos in ff_positions:
            after = content[ff_pos + 1:]
            if len(after) < 3:
                continue
            ps = struct.unpack_from("<H", after, 0)[0]
            if ps < 1 or ps > 10000:
                continue
            if 2 + ps > len(after):
                continue

            # Check up to 3 paragraphs at this position for text evidence
            scan_pos = 0
            found_text = False
            for _ in range(3):
                if scan_pos + 2 >= len(after):
                    break
                p_sz = struct.unpack_from("<H", after, scan_pos)[0]
                if p_sz < 1 or p_sz > 10000 or scan_pos + 2 + p_sz > len(after):
                    break
                p_data = after[scan_pos + 3 : scan_pos + 2 + min(p_sz, 200)]
                if len(p_data) > 5:
                    alpha = sum(1 for b in p_data
                                if (0x41 <= b <= 0x5A)
                                or (0x61 <= b <= 0x7A))
                    if alpha > len(p_data) * 0.15:
                        found_text = True
                        break
                scan_pos += 2 + p_sz

            if found_text:
                return ff_pos

        # Pass 2: Accept any 0xFF with a valid size prefix (less strict)
        for ff_pos in ff_positions:
            after = content[ff_pos + 1:]
            if len(after) < 3:
                continue
            ps = struct.unpack_from("<H", after, 0)[0]
            if 1 <= ps <= 5000 and 2 + ps <= len(after):
                return ff_pos

        # Fallback: use first 0xFF in header region
        for ff_pos in ff_positions:
            if ff_pos < 80:
                return ff_pos

        return ff_positions[0] if ff_positions else -1

    @staticmethod
    def _detect_comp_table(body):
        """Auto-detect which compression table a node body uses.

        Decodes a sample of the body with both tables and scores the
        resulting text for English word quality.
        Returns COMPRESSION_TABLE or COMPRESSION_TABLE2.
        """
        # Decode a chunk with each table
        sample = body[:min(len(body), 2000)]

        def decode_sample(table):
            out = []
            for b in sample:
                if b in table:
                    out.append(table[b])
                elif 0x20 <= b < 0x7F:
                    out.append(chr(b))
                elif b == 0xFF:
                    out.append(" ")
                elif b < 0x20:
                    pass  # control codes
                else:
                    out.append("?")
            return "".join(out)

        t1_text = decode_sample(COMPRESSION_TABLE)
        t2_text = decode_sample(COMPRESSION_TABLE2)

        # Score based on English word quality.
        # Key insight: Table 1 entries end with spaces, creating artificial
        # word boundaries. Table 2 entries don't, causing words to run
        # together. We score based on average word length (should be 3-7
        # for English) and common word recognition.
        common_words = {
            "the", "of", "and", "to", "in", "is", "it", "for",
            "that", "was", "on", "are", "as", "with", "his", "they",
            "be", "at", "one", "have", "this", "from", "or", "had",
            "by", "not", "but", "what", "all", "were", "we", "when",
            "your", "can", "said", "there", "each", "which", "their",
            "an", "will", "other", "about", "out", "many", "then",
            "them", "would", "like", "so", "these", "her", "more",
            "has", "no", "its", "than", "been", "who", "may", "after",
            "also", "made", "did", "most", "into", "over", "such",
            "our", "some", "very", "time", "you", "could", "use",
            "first", "how", "new", "now", "any", "way", "data",
            "network", "frame", "relay", "packet", "protocol",
            "services", "technology", "between",
        }

        def word_score(text):
            # Split on non-alpha and count recognized words
            words = []
            cur = []
            for ch in text.lower():
                if ch.isalpha():
                    cur.append(ch)
                else:
                    if cur:
                        words.append("".join(cur))
                        cur = []
            if cur:
                words.append("".join(cur))

            if not words:
                return 0

            score = 0
            # Common word matches (strong signal)
            for w in words:
                if w in common_words:
                    score += 5

            # Average word length penalty: English averages ~4.7 chars
            avg_len = sum(len(w) for w in words) / len(words)
            if avg_len < 2.5:
                # Too many short fragments (Table 1 applied to Table 2 data)
                score -= len(words) * 0.5
            elif avg_len > 8:
                # Words running together (Table 2 applied to Table 1 data)
                score -= len(words) * 0.5

            # Penalize words with no vowels (>3 chars)
            for w in words:
                if len(w) > 3:
                    vowels = sum(1 for c in w if c in "aeiou")
                    if vowels == 0:
                        score -= 3

            return score

        s1 = word_score(t1_text)
        s2 = word_score(t2_text)

        if s1 > s2:
            return COMPRESSION_TABLE
        else:
            return COMPRESSION_TABLE2

    def _parse_nodes(self):
        """Parse all text nodes."""
        self.nodes = []
        for i, (ns, nm, nc) in enumerate(self.node_index):
            node = HW3Node()
            if ns == 0:
                self.nodes.append(node)
                continue

            nd = follow_chain(self.sectors, ns)
            if len(nd) < 4:
                self.nodes.append(node)
                continue

            node.node_type = nd[1]
            content_size = struct.unpack_from("<H", nd, 2)[0]

            # Compression flag: nd[0] selects the compression table
            # 0x00 = no compression
            # 0x01 = compressed with Table 1 (word-ending fragments + spaces)
            # 0x02 = compressed with Table 2 (BPE bigram/trigram merges)
            comp_flag = nd[0]
            is_compressed = comp_flag in (0x01, 0x02)
            if comp_flag == 0x02:
                node_comp_table = COMPRESSION_TABLE2
            elif comp_flag == 0x01:
                node_comp_table = COMPRESSION_TABLE
            else:
                node_comp_table = None

            # Limit content to content_size to avoid reading into adjacent data
            content = nd[4 : 4 + content_size]

            # Truncate at first run of 8+ null bytes — this marks the end
            # of text content and start of trailing metadata/index data.
            if is_compressed:
                null_run = 0
                for ci in range(len(content)):
                    if content[ci] == 0x00:
                        null_run += 1
                        if null_run >= 8:
                            content = content[: ci - null_run + 1]
                            break
                    else:
                        null_run = 0

            node.raw_content = content

            # Find body start
            body_start = self._find_body_start(content, is_compressed)

            # Parse header tags (0x08 = node ID, 0x0D = title)
            for j in range(min(len(content) - 1, 60)):
                if content[j] == 0x08 and j + 1 < len(content):
                    node.tag_08 = content[j + 1]
                elif content[j] == 0x0D:
                    tlen = content[j + 1]
                    if j + 2 + tlen <= len(content) and 0 < tlen < 60:
                        raw_title = content[j + 2 : j + 2 + tlen]
                        if is_compressed:
                            node.title = self._decompress_text(
                                raw_title, node_comp_table)
                        else:
                            node.title = raw_title.decode(
                                "cp437", errors="replace")
                    break

            if body_start >= 0:
                body = content[body_start + 1:]
                node.paragraphs = self._parse_body(
                    body, is_compressed, node_comp_table)

            self.nodes.append(node)

    def _decompress_text(self, data, comp_table=None):
        """Decompress a byte sequence using the compression dictionary."""
        if comp_table is None:
            comp_table = COMPRESSION_TABLE
        result = []
        for b in data:
            if b in comp_table:
                result.append(comp_table[b])
            elif 0x20 <= b < 0x7F:
                result.append(chr(b))
            elif b >= 0x80:
                result.append(cp437_to_unicode(b))
            else:
                result.append(chr(b) if b >= 0x20 else "")
        return "".join(result)

    def _truncate_stale_data(self, content):
        """Find and remove stale circular buffer data from compressed content.

        Walks through the byte stream respecting multi-byte control sequences
        to find the first run of 3+ standalone null bytes, which marks the
        boundary between real text and stale buffer data.
        """
        ci = 0
        while ci < len(content):
            b = content[ci]
            if b == 0x00:
                # Count consecutive null bytes
                j = ci
                while j < len(content) and content[j] == 0x00:
                    j += 1
                if j - ci >= 3:
                    return content[:ci]
                ci = j
            elif b == 0x01 or b == 0x03:
                # link_start / action_start: 01/03 TT TT [echo|extended]
                if ci + 3 < len(content):
                    if content[ci + 3] == b:
                        ci += 4  # echo
                    else:
                        ci += 6  # extended operand
                else:
                    ci += 1
            elif b == 0x09:
                # Section marker: 09 XX ?? 00 00 00 00 09
                if (ci + 7 < len(content) and
                        content[ci + 3] == 0 and content[ci + 4] == 0 and
                        content[ci + 5] == 0 and content[ci + 6] == 0 and
                        content[ci + 7] == 0x09):
                    ci += 8
                else:
                    ci += 1
            elif b == 0x0B:
                # highlight_start: 0B XX [0B]
                if ci + 2 < len(content) and content[ci + 2] == 0x0B:
                    ci += 3
                else:
                    ci += 2
            elif b == 0x0F:
                # Skip 0F-delimited block
                j = ci + 1
                if j < len(content) and content[j] in (0x02, 0x04, 0x0D):
                    k = j + 1
                    while k < len(content):
                        if content[k] == 0x0F:
                            break
                        k += 1
                    ci = k + 1 if k < len(content) else ci + 1
                else:
                    ci += 1
            else:
                ci += 1
        return content

    def _parse_text_compressed(self, data, comp_table=None):
        """Parse compressed text with inline control codes into elements."""
        elements = []
        i = 0
        text_buf = ""

        def flush_text():
            nonlocal text_buf
            if text_buf:
                elements.append(("text", text_buf))
                text_buf = ""

        while i < len(data):
            b = data[i]

            if b == 0x00:
                # Count consecutive null bytes; 3+ marks end of real text
                # (stale circular buffer data follows)
                j = i
                while j < len(data) and data[j] == 0x00:
                    j += 1
                if j - i >= 3:
                    flush_text()
                    break
                i = j
                continue

            elif b == 0xFF:
                # 0xFF + style_byte: sentence/paragraph boundary.
                # If followed by a control code (< 0x20), it's a paragraph
                # break (e.g., before link_start or section marker).
                # If followed by printable text (>= 0x20), it's a
                # double-space sentence join within the same paragraph.
                flush_text()
                i += 1
                if i < len(data):
                    i += 1  # skip style byte
                if i < len(data) and data[i] >= 0x20:
                    elements.append(("text", "  "))
                else:
                    elements.append(("soft_return",))
                continue

            elif b == 0x01:
                flush_text()
                if i + 3 <= len(data):
                    target = struct.unpack_from("<H", data, i + 1)[0]
                    i += 3
                    # After 01 TT TT: if next byte echoes opcode (0x01),
                    # skip 1 more (4 total). Otherwise skip 3 more (6 total).
                    if i < len(data) and data[i] == 0x01:
                        i += 1  # echo byte
                    elif i + 3 <= len(data):
                        # Extended operand: 3 bytes. If all three are 0x00,
                        # this marks end of text (stale buffer boundary).
                        if data[i] == 0 and data[i+1] == 0 and data[i+2] == 0:
                            break
                        i += 3  # extended operand
                    else:
                        # Operand overflows buffer - skip remaining bytes
                        i = min(i + 3, len(data))
                    if target > 0:
                        elements.append(("link_start", target))
                    else:
                        # Null links (target=0) act as paragraph separators
                        elements.append(("soft_return",))
                else:
                    i += 1

            elif b == 0x03:
                flush_text()
                if i + 3 <= len(data):
                    target = struct.unpack_from("<H", data, i + 1)[0]
                    elements.append(("action_start", target))
                    i += 3
                    # Same echo rule: 03 echoes to 03
                    if i < len(data) and data[i] == 0x03:
                        i += 1
                    elif i + 3 <= len(data):
                        i += 3
                    else:
                        i = min(i + 3, len(data))
                else:
                    i += 1

            elif b == 0x05:
                flush_text()
                elements.append(("italic_toggle",))
                i += 1

            elif b == 0x06:
                flush_text()
                elements.append(("bold_toggle",))
                i += 1

            elif b == 0x07:
                flush_text()
                elements.append(("underline_toggle",))
                i += 1

            elif b == 0x09:
                flush_text()
                # Section/category marker: 09 XX 01 00 00 00 00 09
                # or image embed: 09 XX 00 00 00 00 00 09
                if (i + 7 < len(data) and
                        data[i + 3] == 0 and data[i + 4] == 0 and
                        data[i + 5] == 0 and data[i + 6] == 0 and
                        data[i + 7] == 0x09):
                    i += 8
                    # Some section markers have trailing object ref: YY 00 00
                    if (i + 2 < len(data) and
                            data[i] >= 0x20 and
                            data[i + 1] == 0 and data[i + 2] == 0):
                        i += 3
                else:
                    elements.append(("tab",))
                    i += 1

            elif b == 0x0B:
                flush_text()
                if i + 2 < len(data) and data[i + 2] == 0x0B:
                    elements.append(("highlight_start", data[i + 1]))
                    i += 3
                elif i + 1 < len(data):
                    elements.append(("highlight_start", data[i + 1]))
                    i += 2
                else:
                    i += 1

            elif b == 0x0C:
                flush_text()
                elements.append(("highlight_end",))
                i += 1

            elif b == 0x0F:
                flush_text()
                j = i + 1
                if j < len(data) and data[j] in (0x02, 0x04, 0x0D):
                    k = j + 1
                    while k < len(data):
                        if data[k] == 0x0F:
                            break
                        k += 1
                    if k < len(data):
                        i = k + 1
                    else:
                        i += 1
                else:
                    i += 1
                    while i < len(data) and data[i] < 0x20 and data[i] != 0x0F:
                        i += 1

            elif b == 0x10:
                flush_text()
                # Count consecutive 0x10 bytes
                count = 0
                while i < len(data) and data[i] == 0x10:
                    count += 1
                    i += 1
                if count > 1:
                    # Multiple 0x10s = field delimiter, render as tab
                    elements.append(("tab",))
                else:
                    # Single 0x10 has a parameter byte (column position)
                    if i < len(data) and data[i] >= 0x20:
                        i += 1  # skip parameter byte
                    text_buf += " "

            elif b == 0x12:
                flush_text()
                elements.append(("link_end",))
                i += 1

            elif b == 0x14:
                flush_text()
                elements.append(("action_end",))
                i += 1

            elif b == 0x02 or b == 0x04 or b == 0x08:
                i += 1

            elif b >= 0x20 and b < 0x7F:
                text_buf += chr(b)
                i += 1

            elif b >= 0x80:
                # Decompress using dictionary
                tbl = comp_table or COMPRESSION_TABLE
                if b in tbl:
                    text_buf += tbl[b]
                else:
                    text_buf += cp437_to_unicode(b)
                i += 1

            else:
                i += 1

        flush_text()
        return elements

    def _parse_body(self, body, is_compressed=False, comp_table=None):
        """Parse body content into a list of paragraphs.

        Each paragraph is (style_index, elements) where elements is a list
        of tuples: ('text', string), ('bold_on',), ('bold_off',), etc.

        Non-compressed nodes use size-prefixed paragraphs throughout.
        Compressed nodes start with a few size-prefixed paragraphs (headings),
        then transition to a continuous stream where 0xFF + style byte marks
        paragraph boundaries.
        """
        paragraphs = []
        pos = 0

        # Phase 1: Parse size-prefixed paragraphs
        while pos + 2 <= len(body):
            psize = struct.unpack_from("<H", body, pos)[0]
            if psize == 0:
                break
            if psize > 30000:
                break
            if pos + 2 + psize > len(body):
                if not is_compressed:
                    psize = len(body) - pos - 2
                    if psize <= 0:
                        break
                else:
                    break

            # For compressed nodes, validate that the paragraph content
            # starts with plausible data (not null/link opcode leaks)
            if is_compressed and pos + 3 < len(body):
                first_content = body[pos + 3]  # first byte after size + style
                if first_content in (0x00, 0x01, 0x03):
                    break  # likely stream data, not a real paragraph

            pos += 2
            pdata = body[pos : pos + psize]
            pos += psize

            if len(pdata) == 0:
                continue

            style_idx = pdata[0]
            text_data = pdata[1:]
            if is_compressed:
                # A link_start (0x01) in Phase 1 paragraphs marks the end
                # of the paragraph's own text; remaining bytes after the
                # link operand are subsequent content that belong in Phase 2.
                body_leak_start = -1
                for ti in range(len(text_data) - 2):
                    if text_data[ti] == 0x01 and text_data[ti + 1] < 0x20:
                        skip = ti + 3
                        if skip < len(text_data) and text_data[skip] == 0x01:
                            skip += 1  # echo byte
                        elif skip + 3 <= len(text_data):
                            skip += 3  # extended operand
                        else:
                            # Operand overflows paragraph boundary;
                            # consume all remaining bytes so partial
                            # operand doesn't leak into Phase 2.
                            skip = len(text_data)
                        if skip < len(text_data):
                            body_leak_start = skip
                            text_data = text_data[:ti]
                        break
                if body_leak_start >= 0:
                    pos -= len(pdata) - 1 - body_leak_start
                elements = self._parse_text_compressed(text_data, comp_table)
                if body_leak_start >= 0:
                    paragraphs.append((style_idx, elements))
                    break  # remaining bytes belong to Phase 2
            else:
                elements = self._parse_text(text_data)
            paragraphs.append((style_idx, elements))

        # Phase 2: For compressed nodes, parse remaining data as stream.
        # Pass entire stream to _parse_text_compressed which handles 0xFF
        # paragraph breaks internally. This ensures the 3-null stale data
        # detection works across FF boundaries.
        if is_compressed and pos < len(body):
            stream = body[pos:]
            # Skip orphaned link/action operand bytes that leaked from
            # the last Phase 1 paragraph's incomplete control sequence.
            # Pattern: 1-2 non-text bytes + 00 00 before real text.
            if (len(stream) > 4 and
                    stream[2] == 0x00 and stream[3] == 0x00 and
                    (stream[0] < 0x20 or stream[0] >= 0x80)):
                stream = stream[4:]
            elements = self._parse_text_compressed(stream, comp_table)
            # Split at soft_return into separate paragraphs so each
            # gets its own \par in RTF output.
            phase2_start = len(paragraphs)
            if elements:
                current_elems = []
                for elem in elements:
                    if elem[0] == "soft_return":
                        if current_elems:
                            paragraphs.append((0, current_elems))
                        current_elems = []
                    else:
                        current_elems.append(elem)
                if current_elems:
                    paragraphs.append((0, current_elems))

            # Post-process: move leading "Summary" links from paragraph
            # starts to the end of the previous paragraph.
            # Pattern: link_start, text("Summary"), link_end at para start.
            i = len(paragraphs) - 1
            while i > phase2_start:
                style, elems = paragraphs[i]
                if (len(elems) >= 3 and
                        elems[0][0] == "link_start" and
                        elems[1] == ("text", "Summary") and
                        elems[2][0] == "link_end"):
                    prev_style, prev_elems = paragraphs[i - 1]
                    prev_elems.append(("text", "  "))
                    prev_elems.extend(elems[:3])
                    paragraphs[i] = (style, elems[3:])
                    if not elems[3:]:
                        paragraphs.pop(i)
                i -= 1

            # Merge text-only paragraphs with the next when the text
            # has unclosed parentheses (continuation across FF break).
            def _para_text(elems):
                return "".join(e[1] for e in elems if e[0] == "text")

            def _has_links(elems):
                return any(e[0] in ("link_start", "link_end",
                                    "action_start", "action_end")
                           for e in elems)

            i = max(phase2_start + 1, 1)
            while i < len(paragraphs):
                _, prev_elems = paragraphs[i - 1]
                _, cur_elems = paragraphs[i]
                pt = _para_text(prev_elems)
                if (not _has_links(prev_elems) and
                        not _has_links(cur_elems) and
                        pt.count('(') > pt.count(')')):
                    prev_elems.append(("text", "  "))
                    prev_elems.extend(cur_elems)
                    paragraphs.pop(i)
                else:
                    i += 1

        return paragraphs


    def _parse_text(self, data):
        """Parse text content with inline control codes into elements."""
        elements = []
        i = 0
        text_buf = ""

        def flush_text():
            nonlocal text_buf
            if text_buf:
                elements.append(("text", text_buf))
                text_buf = ""

        while i < len(data):
            b = data[i]

            if b == 0x00:
                i += 1
                continue

            elif b == 0x01:
                flush_text()
                if i + 3 <= len(data):
                    target = struct.unpack_from("<H", data, i + 1)[0]
                    elements.append(("link_start", target))
                    i += 3
                    # Skip echo/operand byte after link target
                    if i < len(data) and data[i] < 0x20 and data[i] != 0x12:
                        i += 1
                else:
                    i += 1

            elif b == 0x03:
                flush_text()
                if i + 3 <= len(data):
                    target = struct.unpack_from("<H", data, i + 1)[0]
                    elements.append(("action_start", target))
                    i += 3
                    if i < len(data) and data[i] < 0x20 and data[i] != 0x14:
                        i += 1
                else:
                    i += 1

            elif b == 0x05:
                flush_text()
                elements.append(("italic_toggle",))
                i += 1

            elif b == 0x06:
                flush_text()
                elements.append(("bold_toggle",))
                i += 1

            elif b == 0x07:
                flush_text()
                elements.append(("underline_toggle",))
                i += 1

            elif b == 0x09:
                flush_text()
                # Section/category marker: 09 XX 01 00 00 00 00 09
                # or image embed: 09 XX 00 00 00 00 00 09
                if (i + 7 < len(data) and
                        data[i + 3] == 0 and data[i + 4] == 0 and
                        data[i + 5] == 0 and data[i + 6] == 0 and
                        data[i + 7] == 0x09):
                    i += 8
                    # Some section markers have trailing object ref: YY 00 00
                    if (i + 2 < len(data) and
                            data[i] >= 0x20 and
                            data[i + 1] == 0 and data[i + 2] == 0):
                        i += 3
                else:
                    elements.append(("tab",))
                    i += 1

            elif b == 0x0B:
                flush_text()
                if i + 2 < len(data) and data[i + 2] == 0x0B:
                    color = data[i + 1]
                    elements.append(("highlight_start", color))
                    i += 3
                elif i + 1 < len(data):
                    color = data[i + 1]
                    elements.append(("highlight_start", color))
                    i += 2
                else:
                    i += 1

            elif b == 0x0C:
                flush_text()
                elements.append(("highlight_end",))
                i += 1

            elif b == 0x0F:
                flush_text()
                j = i + 1
                if j < len(data) and data[j] in (0x02, 0x04, 0x0D):
                    k = j + 1
                    while k < len(data):
                        if data[k] == 0x0F:
                            break
                        k += 1
                    if k < len(data):
                        i = k + 1
                    else:
                        i += 1
                else:
                    i += 1
                    while i < len(data) and data[i] < 0x20 and data[i] != 0x0F:
                        i += 1

            elif b == 0x10:
                flush_text()
                # Count consecutive 0x10 bytes
                count = 0
                while i < len(data) and data[i] == 0x10:
                    count += 1
                    i += 1
                if count > 1:
                    # Multiple 0x10s = field delimiter, render as tab
                    elements.append(("tab",))
                else:
                    # Single 0x10 has a parameter byte (column position)
                    if i < len(data) and data[i] >= 0x20:
                        i += 1  # skip parameter byte
                    text_buf += " "

            elif b == 0x12:
                flush_text()
                elements.append(("link_end",))
                i += 1

            elif b == 0x14:
                flush_text()
                elements.append(("action_end",))
                i += 1

            elif b == 0x02 or b == 0x04 or b == 0x08:
                i += 1

            elif b >= 0x20 and b < 0x7F:
                text_buf += chr(b)
                i += 1

            elif b >= 0x80:
                text_buf += cp437_to_unicode(b)
                i += 1

            else:
                i += 1

        flush_text()
        return elements


# ---------------------------------------------------------------------------
# RTF generator
# ---------------------------------------------------------------------------


def rtf_escape(text):
    """Escape text for RTF output."""
    out = []
    for ch in text:
        cp = ord(ch)
        if ch == "\\":
            out.append("\\\\")
        elif ch == "{":
            out.append("\\{")
        elif ch == "}":
            out.append("\\}")
        elif cp > 127:
            out.append(f"\\u{cp}\\'3f")
        else:
            out.append(ch)
    return "".join(out)


def _build_action_bookmark_map(doc):
    """Build a mapping from link targets to (node_index, para_index) positions.

    HyperWriter documents use primary index entries as link targets. Each
    primary index entry points to a sector containing an action record with
    a DOS path like \\UTI\\PGM2501. Full description nodes contain action
    paragraphs like "Load PGM2501" at style=4. We match these to create
    internal bookmarks.

    Returns: dict mapping link_target_id -> (node_index, title_para_index)
    """
    import re as _re

    # Step 1: Build primary_index_id -> path mapping
    primary_path_map = {}  # primary_index_id -> path_basename
    for idx in range(6, len(doc.primary_index)):
        s = doc.primary_index[idx][0]
        if s == 0 or s >= len(doc.sectors):
            continue
        sd = follow_chain(doc.sectors, s)
        if len(sd) < 10:
            continue
        # Find path pattern: \XXX\PGMnnnn or similar
        for i in range(min(len(sd) - 5, 40)):
            if sd[i] == 0x5C and i + 4 < len(sd):  # backslash
                end = i + 1
                while end < min(len(sd), i + 30) and sd[end] != 0:
                    end += 1
                try:
                    path = sd[i:end].decode('ascii', errors='ignore')
                except Exception:
                    continue
                # Extract basename (e.g., PGM2501 from \UTI\PGM2501.ZIP)
                parts = path.split('\\')
                if len(parts) >= 2 and parts[-1]:
                    basename = parts[-1].upper()
                    # Strip file extension if present
                    if '.' in basename:
                        basename = basename[:basename.index('.')]
                    if basename:
                        primary_path_map[idx] = basename
                break

    if not primary_path_map:
        return {}

    # Step 2: Find action paragraphs in nodes and extract their Load targets
    action_para_map = {}  # path_basename -> (node_index, title_para_index)
    for ni, node in enumerate(doc.nodes):
        for pi, (style_idx, elements) in enumerate(node.paragraphs):
            # Check for action_start in elements
            has_action = False
            text = ""
            for elem in elements:
                if elem[0] == "action_start":
                    has_action = True
                elif elem[0] == "text":
                    text += elem[1]
            if not has_action:
                continue
            # Extract basename from "Load PGMxxxx" or just "PGMxxxx"
            m = _re.search(r'(?:Load\s+)?(\w+\d+)', text.strip())
            if m:
                basename = m.group(1).upper()
                # The title paragraph is usually 1 before the action
                title_pi = max(0, pi - 1)
                action_para_map[basename] = (ni, title_pi)

    # Step 3: Build final mapping: link_target_id -> (node_index, title_para_index)
    result = {}
    for idx, basename in primary_path_map.items():
        if basename in action_para_map:
            result[idx] = action_para_map[basename]

    return result


def _build_heading_link_map(doc):
    """Build a mapping from link targets to heading paragraph positions.

    For documents where multiple sections live in a single node, links
    can't resolve by node index alone. This function matches link text
    against heading paragraphs to create internal bookmark targets.

    Returns: dict mapping link_target_id -> (node_index, para_index)
    """
    # Step 1: Collect all heading paragraphs from text nodes.
    # A "heading" is any paragraph whose text exactly matches a link label.
    # We index by normalized text for matching, storing all locations.
    heading_locs = {}  # normalized_text -> list of (node_index, para_index)
    for ni, node in enumerate(doc.nodes):
        if node.node_type in (2, 4, 0x0A, 0x0B):
            continue
        if not node.paragraphs:
            continue
        for pi, (style_idx, elements) in enumerate(node.paragraphs):
            text = "".join(
                e[1] for e in elements if e[0] == "text"
            ).strip()
            if text and len(text) >= 2:
                key = text.lower()
                if key not in heading_locs:
                    heading_locs[key] = []
                heading_locs[key].append((ni, pi))

    # Find the node that contains the most links (likely the TOC/index).
    link_source_counts = {}
    for ni, node in enumerate(doc.nodes):
        if not node.paragraphs:
            continue
        count = 0
        for pi, (style_idx, elements) in enumerate(node.paragraphs):
            for elem in elements:
                if elem[0] == "link_start":
                    count += 1
        if count > 0:
            link_source_counts[ni] = count
    toc_node = max(link_source_counts, key=link_source_counts.get) \
        if link_source_counts else -1

    # Build heading_index preferring non-TOC nodes.
    heading_index = {}
    for key, locs in heading_locs.items():
        non_toc = [(ni, pi) for ni, pi in locs if ni != toc_node]
        heading_index[key] = non_toc[0] if non_toc else locs[0]

    # Step 2: Collect all link targets and their display text.
    link_targets = {}  # target_id -> link_text
    for ni, node in enumerate(doc.nodes):
        if not node.paragraphs:
            continue
        for pi, (style_idx, elements) in enumerate(node.paragraphs):
            for ei, elem in enumerate(elements):
                if elem[0] != "link_start":
                    continue
                target = elem[1]
                if target in link_targets:
                    continue
                text = ""
                for e2 in elements[ei + 1:]:
                    if e2[0] == "link_end":
                        break
                    if e2[0] == "text":
                        text += e2[1]
                if text.strip():
                    link_targets[target] = text.strip()

    # Step 3: Match link texts to headings in other nodes.
    result = {}
    for target, link_text in link_targets.items():
        key = link_text.lower()
        if key in heading_index:
            hni, hpi = heading_index[key]
            result[target] = (hni, hpi)
            continue
        # Try prefix match for truncated link text (>= 20 chars).
        # Collect all matches and prefer non-TOC nodes.
        if len(key) >= 20:
            candidates = []
            for h_key, (hni, hpi) in heading_index.items():
                if h_key.startswith(key):
                    candidates.append((hni, hpi))
            if candidates:
                non_toc = [(ni, pi) for ni, pi in candidates
                           if ni != toc_node]
                result[target] = non_toc[0] if non_toc else candidates[0]

    return result


def _is_action_command(elements):
    """Check if a paragraph's elements represent a DOS/HyperWriter action command.

    Action commands like 'copy \\path\\file prn' and '@RESTART' appear in
    Article and Card nodes but should not be rendered as visible text.
    """
    # Extract plain text from elements
    text = ""
    for elem in elements:
        if elem[0] == "text":
            text += elem[1]
    text = text.strip()
    if not text:
        return False
    # Common HyperWriter action commands
    low = text.lower()
    if low.startswith("copy ") and ("prn" in low or "\\" in text):
        return True
    if low.startswith("@"):
        return True
    if low.startswith("run ") or low.startswith("exec "):
        return True
    if low.startswith("del ") and "\\" in text:
        return True
    return False


def generate_rtf(doc, no_links=False):
    """Generate RTF content from a parsed HW3 document."""
    lines = []

    # RTF header - use monospace font as default (DOS was monospace)
    lines.append("{\\rtf1\\ansi\\deff0")

    # Font table
    lines.append("{\\fonttbl")
    lines.append("{\\f0\\fmodern\\fcharset0 Courier New;}")
    lines.append("{\\f1\\froman\\fcharset0 Times New Roman;}")
    lines.append("{\\f2\\fswiss\\fcharset0 Arial;}")
    lines.append("}")

    # Color table (basic colors for highlights)
    lines.append("{\\colortbl;")
    lines.append("\\red0\\green0\\blue0;")       # 1: black
    lines.append("\\red0\\green0\\blue255;")      # 2: blue
    lines.append("\\red0\\green128\\blue0;")      # 3: green
    lines.append("\\red255\\green0\\blue0;")      # 4: red
    lines.append("\\red128\\green0\\blue128;")    # 5: purple
    lines.append("\\red255\\green255\\blue0;")    # 6: yellow
    lines.append("\\red255\\green255\\blue255;")  # 7: white
    lines.append("}")

    # Document formatting
    lines.append("\\paperw12240\\paperh15840")
    lines.append("\\margl180\\margr180\\margt180\\margb180")

    # Default right-aligned tab stop at right margin (for field delimiters)
    lines.append("\\deftab720")

    # Compute global record offset for link target resolution.
    # The primary and node index chains share a sector sequence.
    # Primary index has header[0] entries at 6 bytes each, 10 per sector.
    # Node records start after the primary index sectors.
    primary_count = doc.header[0] if len(doc.header) > 0 else 0
    records_per_sector = SECTOR_DATA // 6  # 60 / 6 = 10
    if primary_count > 0:
        import math
        primary_sectors = math.ceil(primary_count / records_per_sector)
        node_offset = primary_sectors * records_per_sector
    else:
        node_offset = 0

    # Build action bookmark map: link_target -> (node_index, para_index)
    action_bkmk_map = _build_action_bookmark_map(doc)
    # Invert to find which (node, para) needs a bookmark anchor
    para_bookmarks = {}  # (node_index, para_index) -> set of bookmark IDs
    for target_id, (ni, pi) in action_bkmk_map.items():
        key = (ni, pi)
        if key not in para_bookmarks:
            para_bookmarks[key] = set()
        para_bookmarks[key].add(target_id)

    # Build text-based heading bookmark map for intra-document links.
    # Collects all link texts and matches them to heading paragraphs.
    heading_link_map = _build_heading_link_map(doc)
    for target_id, (hni, hpi) in heading_link_map.items():
        key = (hni, hpi)
        if key not in para_bookmarks:
            para_bookmarks[key] = set()
        para_bookmarks[key].add(target_id)

    # Pre-compute set of valid bookmark IDs so we only create HYPERLINK
    # fields for targets that actually have bookmark anchors.
    valid_bkmk_ids = set()
    for ni, node in enumerate(doc.nodes):
        if node.node_type in (2, 4, 0x0A, 0x0B):
            continue
        if not node.paragraphs and not node.title:
            continue
        if node.title:
            valid_bkmk_ids.add(ni)
            if node.tag_08 >= 0:
                valid_bkmk_ids.add(node.tag_08)
            if node_offset > 0:
                valid_bkmk_ids.add(ni + node_offset)
    # Add action bookmark targets
    valid_bkmk_ids.update(action_bkmk_map.keys())
    # Add heading-based link targets
    valid_bkmk_ids.update(heading_link_map.keys())

    # Emit nodes
    first_content = True
    for ni, node in enumerate(doc.nodes):
        if node.node_type in (2, 4, 0x0A, 0x0B):
            # Skip Action, Script, Diagram overlay, Diagram description nodes
            continue
        if not node.paragraphs and not node.title:
            continue

        # Node separator (page break between nodes, except before first)
        if not first_content:
            lines.append("\\page")
        first_content = False

        # Emit bookmark anchors for node (invisible, links resolve here).
        # Body paragraphs provide the visible title text.
        if node.title:
            bkmk_ids = {ni}
            if node.tag_08 >= 0:
                bkmk_ids.add(node.tag_08)
            if node_offset > 0:
                bkmk_ids.add(ni + node_offset)
            # Don't place node-level bookmarks for IDs that have
            # more specific heading-level placement via para_bookmarks.
            bkmk_ids -= set(heading_link_map.keys())
            node_bkmk_ids = bkmk_ids  # saved for first paragraph
        else:
            node_bkmk_ids = set()

        # Paragraphs
        for pi, (style_idx, elements) in enumerate(node.paragraphs):
            if not elements:
                lines.append("{\\pard\\par}")
                continue

            # Skip DOS/HyperWriter action commands
            if _is_action_command(elements):
                continue

            para_parts = []

            # Insert node bookmark anchors into the first real paragraph
            if node_bkmk_ids:
                for bid in sorted(node_bkmk_ids):
                    bname = f"node{bid}"
                    para_parts.append(
                        "{\\*\\bkmkstart " + bname + "}"
                        "{\\*\\bkmkend " + bname + "}"
                    )
                node_bkmk_ids = set()  # only add once

            # Insert bookmark anchors for action-mapped paragraphs
            bkmk_key = (ni, pi)
            if bkmk_key in para_bookmarks:
                for bid in sorted(para_bookmarks[bkmk_key]):
                    bname = f"node{bid}"
                    para_parts.append(
                        "{\\*\\bkmkstart " + bname + "}"
                        "{\\*\\bkmkend " + bname + "}"
                    )
            bold = False
            italic = False
            underline = False
            in_link = False
            link_is_field = False
            open_groups = 0

            for elem in elements:
                etype = elem[0]

                if etype == "text":
                    para_parts.append(rtf_escape(elem[1]))

                elif etype == "bold_toggle":
                    bold = not bold
                    para_parts.append("\\b " if bold else "\\b0 ")

                elif etype == "italic_toggle":
                    italic = not italic
                    para_parts.append("\\i " if italic else "\\i0 ")

                elif etype == "underline_toggle":
                    underline = not underline
                    para_parts.append("\\ul " if underline else "\\ulnone ")

                elif etype == "tab":
                    para_parts.append("\\tab ")

                elif etype == "soft_return":
                    para_parts.append("\\line ")

                elif etype == "link_start":
                    target = elem[1]
                    can_link = (not no_links and not in_link
                                and target in valid_bkmk_ids)
                    if not can_link:
                        # No clickable hyperlink - just style as blue
                        para_parts.append("{\\cf2\\ul ")
                        open_groups += 1
                        if not in_link:
                            in_link = True
                            link_is_field = False
                    else:
                        bkmk = f"node{target}"
                        para_parts.append(
                            "{\\field{\\*\\fldinst HYPERLINK \\\\l \""
                            + bkmk
                            + "\"}{\\fldrslt\\cf2\\ul "
                        )
                        open_groups += 1
                        in_link = True
                        link_is_field = True

                elif etype == "link_end":
                    if open_groups > 0:
                        if in_link:
                            if link_is_field:
                                para_parts.append("\\ulnone\\cf0}}")
                            else:
                                para_parts.append("\\ulnone\\cf0}")
                            in_link = False
                            link_is_field = False
                        else:
                            para_parts.append("\\ulnone\\cf0}")
                        open_groups -= 1

                elif etype == "action_start":
                    para_parts.append("{\\cf5\\ul ")
                    open_groups += 1

                elif etype == "action_end":
                    if open_groups > 0:
                        para_parts.append("\\ulnone\\cf0}")
                        open_groups -= 1

                elif etype == "highlight_start":
                    para_parts.append("{\\highlight6 ")
                    open_groups += 1

                elif etype == "highlight_end":
                    if open_groups > 0:
                        para_parts.append("}")
                        open_groups -= 1

                elif etype == "image_embed":
                    para_parts.append("[IMAGE]")

            # Close any unclosed groups
            if in_link and link_is_field:
                # HYPERLINK field opened 2 braces, close both
                para_parts.append("\\ulnone\\cf0}}")
                in_link = False
                link_is_field = False
                open_groups -= 1
            elif in_link:
                para_parts.append("\\ulnone\\cf0}")
                in_link = False
                open_groups -= 1
            while open_groups > 0:
                para_parts.append("}")
                open_groups -= 1

            content = "".join(para_parts)
            if content.strip():
                lines.append("{\\pard\\sa60 " + content + "\\par}")
            else:
                lines.append("{\\pard\\par}")

    lines.append("}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    no_links = "--no-links" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--no-links"]

    if len(args) != 2:
        print(f"Usage: {sys.argv[0]} [--no-links] <input.hw3> <output.rtf>",
              file=sys.stderr)
        sys.exit(1)

    infile = args[0]
    outfile = args[1]

    if not os.path.exists(infile):
        print(f"Error: input file not found: {infile}", file=sys.stderr)
        sys.exit(1)

    doc = HW3Document(infile)
    rtf = generate_rtf(doc, no_links=no_links)

    with open(outfile, "w", encoding="ascii", errors="replace") as f:
        f.write(rtf)

    node_count = sum(1 for n in doc.nodes if n.paragraphs or n.title)
    print(f"Converted {os.path.basename(infile)}: "
          f"v{'0B' if doc.version == 0x0B else '0C'}, "
          f"{len(doc.nodes)} nodes ({node_count} with content), "
          f"{len(doc.styles)} styles -> {outfile}")


if __name__ == "__main__":
    main()

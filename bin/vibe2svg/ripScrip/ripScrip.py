#!/usr/bin/env python3
# Vibe coded by Codex
"""Independent RIPscrip 1.54 scene interpreter; see ripScrip.txt for scope."""
from __future__ import annotations

import argparse
import base64
import collections
import copy
import dataclasses
import hashlib
import html
import json
import math
import os
from pathlib import Path
import re
import struct
import sys
import tempfile
import zlib

WIDTH, HEIGHT = 640, 350
# PabloDraw-compatible circle aspect: 350/480 * 1.06 = 371/480.
# Truncate the derived radius; rounding changes boundaries used by flood fill.
CIRCLE_ASPECT_NUM, CIRCLE_ASPECT_DEN = 371, 480
# Each digit describes a base-36 field's padded width. Text is always last;
# general syntax rule 10 permits fewer digits in the final numeric parameter.
FIELDS = {
    'w': '222211', 'v': '2222', '*': '', 'e': '', 'E': '', 'g': '22',
    'H': '', '>': '', 'c': '2', 'Q': '2'*16, 'a': '22', 'W': '2',
    'm': '22', 'T': '', '@': '22', 'Y': '2222', 'X': '22',
    'L': '2222', 'R': '2222', 'B': '2222', 'C': '222', 'O': '222222',
    'o': '2222', 'A': '22222', 'V': '222222', 'I': '22222',
    'i': '222222', 'Z': '2'*9, 'P': '2', 'p': '2', 'l': '2',
    'F': '222', '=': '242', 'S': '22', 's': '2'*9,
    '1M': '22222115', '1K': '', '1T': '22222', '1t': '1', '1E': '',
    '1C': '22221', '1P': '2221', '1W': '1', '1I': '22212',
    '1B': '2224'+'2'*10+'6', '1U': '2222211', '1D': '32',
    '1\x1b': '13', '1G': '222222', '1R': '8', '1F': '24',
    '9\x1b': '1124', '#': '',
}
STRINGS = {'T', '@', '1M', '1t', '1W', '1I', '1U', '1D', '1\x1b',
           '1R', '1F', '9\x1b'}
DIGITS = b'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'


class NotRIP(ValueError):
    pass


@dataclasses.dataclass
class Event:
    start: int
    end: int
    kind: str
    op: str = ''
    args: list = dataclasses.field(default_factory=list)
    text: bytes = b''
    problem: str = ''
    recovered_linebreaks: list = dataclasses.field(default_factory=list)


class Parser:
    """Byte-oriented grammar. Every input byte belongs to exactly one event."""
    def __init__(self, data: bytes, *, strict_framing=False):
        self.data = data
        self.strict_framing = strict_framing
        self.bare_command_lines = []
        self.blank_separator_offsets = []
        self.recovered_polygons = []
        self.recovered_sauce = []
        self.events = []
        self.sauce = None
        self.end = len(data)
        self._metadata()
        self.body_end = self.end
        self.events = []
        self._parse()
        self._recover_sauce_trailer()
        if not strict_framing:
            self._blank_separators()
        self.events.extend(self.trailer)
        pos = 0
        for e in self.events:
            if e.start != pos or e.end <= e.start:
                raise AssertionError('Noncontiguous byte accounting')
            pos = e.end
        assert pos == len(data)
        if not any(e.kind in ('command', 'malformed') for e in self.events):
            raise NotRIP('No recognized command in a RIPscrip command line')

    def _blank_separators(self):
        """Treat bounded empty lines in graphics-only streams as separators.

        Literal terminal replay remains available through strict_framing.
        Any non-newline terminal payload disables the extension for this input,
        preserving text placement in mixed streams. Neither leading/trailing
        blank lines qualify. The next line must begin with a successfully
        decoded command; terminal controls and unknown/malformed first commands
        break the run. RIP enable/disable controls keep their parsing behavior.
        """
        events = self.events
        if any(e.kind == 'tty' and e.text.strip(b'\r\n') for e in events):
            return
        for i, event in enumerate(events):
            if event.kind != 'newline':
                continue
            j = i+1
            while (j < len(events) and events[j].kind == 'tty'
                   and events[j].text in (b'\r', b'\n', b'\r\n')):
                j += 1
            k = j
            if k < len(events) and events[k].kind == 'introducer':
                k += 1
            if j > i+1 and k < len(events) and events[k].kind == 'command':
                for blank in events[i+1:j]:
                    blank.kind = 'separator'
                    self.blank_separator_offsets.append(blank.start)

    def _metadata(self):
        b = self.data
        self.trailer = []
        if len(b) >= 128 and b[-128:-121] == b'SAUCE00':
            s = b[-128:]
            self.sauce = {
                'title': s[7:42].decode('cp437').rstrip(),
                'author': s[42:62].decode('cp437').rstrip(),
                'group': s[62:82].decode('cp437').rstrip(),
                'date': s[82:90].decode('ascii', 'replace'),
                'file_size': int.from_bytes(s[90:94], 'little'),
                'data_type': s[94], 'file_type': s[95],
                'tinfo': list(struct.unpack_from('<4H', s, 96)),
                'comment_count': s[104], 'flags': s[105],
                'tinfo_s': s[106:128].decode('cp437').rstrip('\0 '),
            }
            self.end -= 128
            if s[104]:
                n = 5 + 64*s[104]
                if self.end >= n and b[self.end-n:self.end-n+5] == b'COMNT':
                    self.end -= n
                    self.sauce['comments'] = [
                        b[i:i+64].decode('cp437').rstrip()
                        for i in range(self.end+5, len(b)-128, 64)]
                    self.trailer.append(Event(self.end, len(b)-128, 'sauce-comments'))
            self.trailer.append(Event(len(b)-128, len(b), 'sauce'))
        # DOS text EOF may precede metadata or padding. Never scan inside a command.

    def _recover_sauce_trailer(self):
        """Recover a structurally verified stale record before the real footer.

        The final standard record supplies an exact binary-layout witness.
        The older record must point to its own start and match that layout,
        allowing a lost signature prefix and removal of all NUL bytes. No
        approximate text matching, filename rules, or clipping at # is used.
        """
        if (not self.sauce or self.sauce['data_type'] != 1
                or self.sauce['file_type'] != 3 or self.sauce['comment_count']
                or not self.end or self.data[self.end-1] != 26):
            return
        stop = self.end-1
        witness = self.data[-128:]
        matches = []
        for i, event in enumerate(self.events):
            start = event.start
            if (event.kind != 'tty' or not 84 < stop-start <= 128 or i < 2
                    or self.events[i-1].kind != 'newline'
                    or self.events[i-2].kind != 'command'
                    or self.events[i-2].op != '#'):
                continue
            fragment = self.data[start:stop]
            for missing in range(7):
                marker = b'SAUCE00'[missing:]
                if not fragment.startswith(marker):
                    continue
                fields = fragment[len(marker):len(marker)+83]
                if (len(fields) != 83 or any(c < 32 for c in fields[:75])
                        or not re.fullmatch(rb'[0-9]{8}', fields[75:])):
                    continue
                record = b'SAUCE00'+fields+struct.pack('<I', start)+witness[94:]
                normal = record[missing:]
                if fragment not in (normal, normal.replace(b'\0', b'')):
                    continue
                metadata = dict(self.sauce, title=fields[:35].decode('cp437').rstrip(),
                                author=fields[35:55].decode('cp437').rstrip(),
                                group=fields[55:75].decode('cp437').rstrip(),
                                date=fields[75:].decode('ascii'), file_size=start)
                recovered = dict(start=start, end=stop, metadata=metadata,
                                 missing_signature_bytes=missing,
                                 nul_bytes_removed=len(normal)-len(fragment))
                matches.append((i, recovered))
        if len(matches) != 1:
            return  # Ambiguous or unverified bytes retain their original meaning.
        i, recovered = matches[0]
        self.recovered_sauce.append(recovered)
        start = recovered['start']
        message = (f'Recovered SAUCE trailer: {recovered["missing_signature_bytes"]} '
                   f'missing signature bytes, {recovered["nul_bytes_removed"]} '
                   'removed NUL bytes; excluded from terminal display')
        self.events[i:] = [Event(start, stop, 'sauce-recovered',
                                 text=self.data[start:stop], problem=message),
                           Event(stop, self.end, 'dos-eof', text=b'\x1a')]

    def _parse(self):
        b, end = self.data, self.end
        p = 0
        active = False
        enabled = True
        established = False
        bol = True
        while p < end:
            start = p
            if b[p] == 26:
                self.events.append(Event(p, end, 'dos-eof', text=b[p:end]))
                break
            if b[p] in (13, 10):
                p += 1
                if b[start] == 13 and p < end and b[p] == 10:
                    p += 1
                self.events.append(Event(start, p, 'newline' if active else 'tty', text=b[start:p]))
                bol, active = True, False
                continue
            if b[p:p+2] in (b'\x01|', b'\x02|') or (enabled and bol and b[p:p+2] == b'!|'):
                self.events.append(Event(p, p+1, 'introducer'))
                p += 1
                active, bol = True, False
                continue
            bare = (not self.strict_framing and enabled and bol and established
                    and b[p] == 124)
            if (active and b[p] == 124) or bare:
                event = self._read_command(p)
                # A bare line is an explicit compatibility grammar, not a
                # search for commands inside arbitrary text. Its first command
                # must decode completely before the line enters command mode.
                if active or event.kind == 'command':
                    if bare:
                        self.bare_command_lines.append(p)
                    self.events.append(event)
                    if event.recovered_linebreaks:
                        self.recovered_polygons.append(dict(
                            start=event.start, end=event.end, opcode=event.op,
                            vertex_count=event.args[0],
                            line_break_offsets=event.recovered_linebreaks))
                    p = event.end
                    active, bol = True, False
                    if event.kind in ('command', 'malformed'):
                        established = True
                    continue
            if active:
                p = self._boundary(p)
                if p == start:
                    p += 1
                self.events.append(Event(start, p, 'ignored', text=b[start:p]))
                continue
            # ANSI auto-sensing/control is parsed separately from the TTY stream.
            q = re.match(rb'\x1b\[([012]?)!', b[p:end])
            if q:
                p += q.end()
                if q[1] == b'1': enabled = False
                if q[1] == b'2': enabled = True
                self.events.append(Event(start, p, 'rip-control', text=q[0]))
                bol = False
                continue
            p += 1
            while p < end and b[p] not in (10, 13, 26, 1, 2, 27):
                p += 1
            self.events.append(Event(start, p, 'tty', text=b[start:p]))
            bol = False

    def _read_command(self, start):
        """Decode one command without mutating stream state, including lookahead."""
        b, end = self.data, self.end
        p = start
        p += 1
        op_start = p
        op_bytes = bytearray()
        p = self._continuation(p)
        if p < end and b[p] in b'123456789':
            while p < end and b[p] in b'0123456789':
                op_bytes.append(b[p])
                p = self._continuation(p+1)
        if p < end and b[p] not in (10, 13, 124):
            op_bytes.append(b[p])
            p += 1
        op = op_bytes.decode('latin1')
        vals, text, issue = [], b'', ''
        if op not in FIELDS:
            p = self._boundary(p)
            return Event(start, p, 'unknown', op, text=b[op_start:p],
                         problem='Unsupported opcode '+repr(op))
        def field(n, final=False):
            nonlocal p
            digits = bytearray()
            while len(digits) < n:
                p = self._continuation(p)
                if (final and digits and
                        (p >= end or b[p] in (10, 13, 124, 26))):
                    break
                if p >= end or b[p] not in DIGITS:
                    raise ValueError(f'Expected {n} base-36 digits; got {bytes(digits)!r} at byte {p}')
                digits.append(b[p])
                p += 1
            return int(digits, 36)
        coords_start = None
        try:
            polygon = op in ('p', 'P', 'l')
            widths = FIELDS[op]
            for index, n in enumerate(widths):
                final = index == len(widths)-1 and op not in STRINGS and not polygon
                vals.append(field(int(n), final=final))
            if polygon:
                coords_start = p
                count = vals[0]*2
                for index in range(count):
                    vals.append(field(2, final=index == count-1))
            if op in STRINGS:
                buf = bytearray()
                while p < end and b[p] not in (10, 13, 124, 26):
                    q = self._continuation(p)
                    if q != p:
                        p = q
                        continue
                    if b[p] == 92 and p+1 < end:
                        # Quote protocol punctuation; legacy parsers quote any byte.
                        p += 1
                    buf.append(b[p])
                    p += 1
                text = bytes(buf)
        except ValueError as ex:
            if (not self.strict_framing and coords_start is not None
                    and p < end and b[p] in (10, 13)):
                recovered = self._wrapped_polygon(start, op, vals[0], coords_start)
                if recovered is not None:
                    return recovered
            issue = str(ex)
            p = self._boundary(p)
        return Event(start, p, 'malformed' if issue else 'command', op, vals, text, issue)

    def _wrapped_polygon(self, start, op, count, p):
        """Recover a complete counted coordinate list with missing backslashes.

        Only retry a polygon already rejected at an unescaped line ending.
        Require every declared coordinate digit and an exact end boundary;
        never pad, truncate, or consume partially matching terminal content.
        """
        b, end = self.data, self.end
        digits, breaks = bytearray(), []
        while len(digits) < count*4:
            p = self._continuation(p)
            if p < end and b[p] in (10, 13):
                if not digits:
                    return None
                breaks.append(p)
                p += 1
                if b[p-1] == 13 and p < end and b[p] == 10:
                    p += 1
            if p >= end or b[p] not in DIGITS:
                return None
            digits.append(b[p])
            p += 1
        p = self._continuation(p)
        if not breaks or (p < end and b[p] not in (10, 13, 124, 26)):
            return None
        args = [count]+[int(digits[i:i+2], 36) for i in range(0, len(digits), 2)]
        message = (f'Recovered {count}-vertex {op!r} command across '
                   f'{len(breaks)} unescaped line ending(s); all declared '
                   'coordinate digits present, missing continuation backslashes')
        return Event(start, p, 'command', op, args, problem=message,
                     recovered_linebreaks=breaks)

    def _continuation(self, p):
        b = self.data
        while p+1 < self.end and b[p] == 92 and b[p+1] in (10, 13):
            p += 2
            if b[p-1] == 13 and p < self.end and b[p] == 10:
                p += 1
        return p

    def _boundary(self, p):
        b = self.data
        while p < self.end and b[p] not in (10, 13, 124, 26):
            q = self._continuation(p)
            if q != p:
                p = q
            elif b[p] == 92 and p+1 < self.end:
                p += 2
            else:
                p += 1
        return p


# Original font DATA, not renderer code. Sources and SHA-256 in ripScrip.txt.
_FONT_DATA = (
    'c-p+ZTX&<n(l+{E)-B)IPP;Lk>^mV27TCrZ+eF-vG?v7{f@BiMbN~5WC7kZe!&<A?JKpupF+AzmfKGLIs#I0_|NfDYP4@rL<?bK<'
    '?>`RyE2Dn2%rbZXeHp!#^JByO;_d02iev4M>x}%y{Qk?6B41XNyeE6H@Y3FU`syy8yY^fzQxS*jo_YQv@t$AT`^HYFOP{_*uRLGC'
    'yV~)4c)UJ!!Cjd@j6A<=s2m6hHtxPno;SoNBqhJ{-^)zE|5NP|w;|TAJ@ffLXh;wbTXRzq67ozaArT>(&<j};az{Ktw#0=yQ~WU@'
    'F@r|}xKp@aiN7ZGg`P;v2~61?SzYjTd$DQA!uGzAHFX2#zmt9L1|qnML+Cbkn3LkpJ=@_z6q!4}EZ@j8%y-J3gi2{5m`9ptdPt*^'
    'bcB{7x{`*|M#sH)QM4ATgBU4Y=+#BMRdjY)Ey?BLdG`7s-aBuZt`+%x?YU%gAoGLw{jzbzLU}z&-pDuYiOY6L9<;aM+ppqY`5{l0'
    '>j{5*Nn;sMKi4}c!^VG3cfMq$--)bq<BPAvzLs0tzY~XdH`M_b#|QTq2d|fWBP$Xt?8iIzxeG(WwG^-6(Jp?IjS~*Mv|T-hcKYPI'
    '@6K{Vo_+b{vV0=nALN&EsV|k~F2bclPPV+iu%(T?y=N|yxe62Zbdh&-*{~{AcPfpecYco4vlHFfXHLIgBU_(4RgKX-JAa|4E}Et1'
    'nR;HwuGWzfW9(_2DOtv$)|FC895el!s%gBj^*2>pF|qrlYF^{L?laovanAZ@)xnDDeoh+|H<#hNdLgmkFI)9n9)A@tt$GvjJAd7('
    'YquilZ;xtzS?$Rvm2+K<=}6W6W%VV6#j&c@efs9r?zmpD%NNhPu8IA=^@3)-yZkDRrqm?|Up{m9a<}o`c^(MO0}0oUj}R=_@uM#_'
    'eA2zY^AG-oZ~b@w=)WJbV8`~pTpz>tHGF^Jp38Fgon`)x?L7EUB6hC4;Cg4?J6Xf?kMP-1afpL=c-PL)@HhO<-;phqhoir<pFX||'
    'cI$oMibwc+<xBrDcwd|QgWZ9dXIv3@>D@8F&+dTN4U8%M_`vVncL{#r--Ma($Q{FfLwoo=j7b~<m%;O_f^qGqabMPfe9mavJo@Qn'
    'bH>?X_&;hUPW*5D9htw~fQL(=E4ao-yb_yI!9rKCm<T)cgpNJI6PIZCPKOjfYI<KH`pj)PJqYHwEz?I;WKpfhgX;4*U|rIf`@~V4'
    'x+LJIg-D03(!{TIcEF#c?7|s4-NSX+@zcF}k2eiIALT*I<AaD|(y%ZQdLAo2vYM4^$$$)57(kz(FUiW+!(K&M(6V?hir8&foG3l4'
    '6`O}O&(=bZu3|KR@xYki8T;ZX9%k5nBXc6y;V2i$vf<@cGKbchrqC{oCppR@U$$)6*F}=HQGBdLwU&DHl^t&cvp{-<nOMXDFmWOm'
    '&p4lZuMd;jo+rw_2Fgxip_MC{nKxhX68fG*id|!vr&KNCxMd33hw-v3lMxMSUd1)bwxS40W8?dhO~dEgIwG6e9ygL-J*7h?SVn|d'
    '6Y2|A!Wfen#tid6q^gf2SPz^R=zqSKG7B1=r&7<E(sRGI<DDoH5ZRO)df4TpWgww<8L72@gms0h8P780`J-55Ft2naSOx8EEqNN3'
    '7Oxlby<;6OA7zwLSf`cX6^wIl$+wYN{Lau@$YcCHggIJCy9)7l@ir2RFBih?+>R%YvdBOXs+D3D(Bh*dW}|z1J_vYrka`Fdhjro|'
    '{9PU-!@o%e>mAi>SPM6XIfK8WFs?bQy^Nzqhid`z>}!gD$DnCo&8}M<uX1B1c;~_u?(1AZhMnre2(CmGVbmgnu;>BkA9;b8k49cd'
    ';Io~Hw>g<Hp9&7Y^Voa{+s>xv{J7CW1~e84KICS8(*&NUAPtbW5?9#p4DwbAG|Azk@uP9PS;)Nw@JkjJNdZ?r@k#ErEZjl=3B1>b'
    'XG6ghQFgcinuRsL0*x5H30s~XL?5~}gZ6a>G`FS_>4gK|h!FS(XoO$a4Id8bJz*^?4`Pv+ekwv)W0yOiLm&7dQ$-$$XiaY8a%&B|'
    '$SCw-Siw7hCc{-@cL!KMuR)sXDbNY@vrnMEImm;2)v_z_PYASo-2h*@BElijb-;kX`+U>#a$UQ5P&2hwK;MdS_{>)|n*)ykU+K9A'
    ';{<xof6_b8fX;HDd7wEx4^(<x16?m`c$cs{R}#2yVcKzB4r`&2cE=;UV=K880w0?3)@i;n{K;?p$uhGRl2d4JbZeeK`wpx52;)_W'
    '<RBk-a;T$h-J-nYR|>rP(ceg=a~Q*%{Y^hW9*$WZ#Vf<_{m=E3NC##;E25BQZIoNp8fBO?|4!CGM=Re}2ifC1|5#t(l?3FV9{@eU'
    'm?~H4crCebLGFN@x-OMHfXuuA&yP!#ox(<0cmSC=xN_>(CSV}HqdaLj$P=4x+JfKs4%X);PoYn+KHUo5w^khI8RcsCbKZdO6;EQx'
    'N8rbCQ!{7NusMu3i&~x^#e0S@FBP@}@~xZJnLA6+0~?{QuHrZO%wr-MT>@{yn&;To3TQi>=Iycv{W8h<G=VlXuFtfNWCZ<CF{u^G'
    'c35kN)HcfI4EUissy<scdY)k0AUj-Xf3%1CAaPY1t|Yrc-yImEifRJ-Mpu#49m?8`OgjoRm<VpcIP!zoQCJ6%LyIhK>?`2RY}M#%'
    'qC^aR&yj|1d=LHLbZvMK)&%B}8XijLuzoSjAzZod8C}a!#!&C3*FZ-6LB6nGf8W|QvWDR&Mp@(GXJ)S+#P<3JJuU==@8SNpxp{x%'
    '#vuPFY12u+H{99P9P~V!<23}Cu#<2FKHABNPKe*r2--TD{<#!&;vVz|=x=pY3z&BspS9M&L$ID>2>L%21;_~=??G;W{2BKkN7l8W'
    'iEF5AAM{`r1?-yD#9_+jE2*m`=#G^XK<~i!QUi@J1+)zFZI_-D6a7o%gC2)Mw;p#uKG6vD&K7tWba4*!Q8J)WpusXxtVyNqKzr~V'
    'e)xS_YvA#oqOOFs&Eu9|5A`D1HAS)oIfn8q1U<bs{Aa^DFyH|l10=-uJ5n=>dK+jYNquIq+AdRB7`e^@4rmnQN}~ZcFv?oK2Hq~I'
    '%bnmh-$z`t0I`>w!|x-=8Ke7?nq84DW6;k(=S#zUf{dcJ`V(IoyaPJR2RtyWU`~PeGb8834foXVGy!@=oCf@nfjmJzNBxMhF!lhi'
    'z#0!Q9-uAT3e5e6pOYB%g^Uu^_Zz_#l^}~jzr;osqP*l*(2~E5XW4?j0X_z~;A~)?KXA+v^$Cp2;4HvHYiMT!vKHjn2)`pgfoXa9'
    '%lkn7`Zqc31FjgCO8c?22SD3b;03_BAX}S1&MU#T0)9P0duv=zk-~F!6$36^s@^wr<1+{47OZ`FG`L2GDbPPLm{X(NDM3yn4?13L'
    '=UdQ)(cjFEXXG89BaMQ5hUYY3G?ee4&uX0m{S6?OyTimch(n>DMUH$+YKeMr4j7CAZgzn0fj4X)vCaPH{UKffe}_aG{oEWC&l$FJ'
    '!<!)E@+jcLQEAZQsOJn;yvbR9Z}|5{mv9Y1pJ97*xFTK;nIzW@%2JtL6T|^O?w{IqMGE8LSFk5wJ|h3;?>i%Z@XBypfKAhYD-Y%g'
    '{sum?5o42M^Fwanc>E0efmaweya(oKmv4l9cdYyTqx~@W1$qT6nS#to>pq5c9#G#d1H-oz<Rf4So%?9(fUbb`0G(v3ZOt9fGYR14'
    '>d^iz-E^PinX?8x2fQ`Fn)(OOOMru}JJcVjCqX`EH{9lfz5<*|QEmeU%R%2{xDGMse!x@7Ru&)=*nHc3rn~pd2R!wIek95{z^fqR'
    'k-r$)7Y*PlXczdV@#;5cJJSvDOR}ByhfnK}P3!Q_<O%dYVCtY23E;si+AJV%K^F?Z)Ijs{GHgU-<Z0rgyeR%+m-#T>SlQjp-by}j'
    '!DKhG1fR>`{V=bfH+!%-ke{^UgDyt71=z_6VII~fKPBR04!YIwJ3pYD4*(a*i5`x1k>R)waLqpGM(PjzG~r>u7$MNhjh;)???3Qw'
    '&5{k^Nu;L_K4Le%V`4#$^<uiJpL7}Ceh-EHdX&cA1pa@AwPCM7zeyex`Rz(ccau}F*2(QTxZ2Qfq;LCZ==%pBp*=)@w6E-Y?AH>n'
    'AlI3Q(g~k&BM)4>ZyJ{wKgc=9MLr?GpEvnfh;8SFlU)V&w7ZbAZf*4XSG2Qe(Y$qgs}P2dLjHvI8`yEAkc*B~V4v5M+y>h)1ib+C'
    'j8{!}^@UFMa!PkF2BfLo4ad8|WdBpZv&YGPyaT$y_gsL^kVoOl9lWjpqcfC!fLj2g;@C?U@z;d62cYj{4f+gp1MohJfsasT8T=C9'
    'zv1`n@8loIN3Z56Qyq|zSH$YD&L4Jij(!ZpQ!98cGxnj4x)ZU+%|1t2wlH)K?Hig5fF?n|jUe|a=ytICc#i)@J?8=5T-|&O!9??@'
    'bAbkpeQ4|wc<%_jk?f4V1$~A51lLKf175w^6VPwOtLlS}14GBg4uJXk=kH(N`s=zj>UXfm*uU?$NYTaytgNpv4=7u&)Yw)Ze1fu('
    '5AYq}h=qT{Ek+M|4Nnl8!{5dZ0r_+QJ%=_ENdQMJZ#WUI#%|wufQRd?wVJV)Z)!V)mfn98v#UE}cS(J+*6_Wfwq0QHts_p?U!C`V'
    '(eJC*h@W!%r#=N-fU-$<Am6|~)1a@?0oJBOyDhG9KI|X*Yog}}<rK*61=_K(c@O9T&>soX`2leF<R44XUj&%h@Qr^IQAQfHJNg*x'
    'g9Pnc7jcRx0592SPi3yBfj{3mxPo2v*0H~%XTZH+_k=!Nfo{{K!5i!VwjAC4bN!F=Z^jLFiu3E^W|z1|oz`bbtLKlZub}+_ZTk)A'
    'x?>%cG01>N5nYVj^7MokJhVGN7ErL^0AHiuZ)1Ehrrm3ZJP2(9pN!<A-!lDI^p5%ieE=VHaQGMWY3y5&nZQTP$csrX5NGl$5tNN^'
    '{a=&|p8kDNpE|gL{)FrQBE8<$4Sg$)OF{1aSU3LR!vvhc3|?DdyTETg(8mUS6kvBV#Y(Wf8?ddi82t{D9h$kuFNM08CHNfRm3i#3'
    'Y6I^FS;{uXj^sW*12)hA;|4pyHukYU`G6C%^CaGL&-feP0nebHfS~POZE(J8UTx|Re=zz_P)=yXI-@_W1IP%lkznkIWngTt$wYUr'
    'pdXwcxX}Z>I^AE=iT=$s{P}x+`#twm>Hwy0VBKg$ZNTO!=$8dUd(~V)|32R6VTC@H>ACBTuP8Bm1-R&DA0&t`ke)%;!1|7Or53;7'
    '_nyU9i|IZM^Nn->_?ZCy(?;F_T`}~<z<9_{I^T6($Kpqn8^$lTpy>0)b@W0O=K}pWI@_VG1nUcZ?0jkCmIvAw2@!7&oiUJ$LirMX'
    'c<3+W%b7UMsby~+dFtXx4s<~8hYvq17mEtlXD=2ZHTcZfSPZ@|y$OecY_Tb>d!W$o|G@(=&Y9lci?_j}sAr6S4fOKX@@IVe4ZeqV'
    'j2%ndX>CD2=WDRLP)99myV|KJjs*dm9552tZcF2HLZ5mcF3}%aN6*vqHpO{@XG_3PRp{E~vJtpBd9%N`1NJT0-nz_Xl!M$vKbeDm'
    '&(QcYf7nsL19pl2LDaLruO*etV7&<BA8pWY+}~{YA_3a4cJdM~XZCrfW)A3|-@mC-x2kl#fcf-cUcX7yM}V%?tlL=j*ZX?wtY&tH'
    '{LDm=e#k#qBjl+PZ9<@Dg>CwipC&_0mZ-}_cg7w7`vCL_0o=P2eF*EG?9ILj^Krid{bF!UBEaE$n8T>y!w&3VuqOtzD<a?SGS$a%'
    'V|RPNUmx@IAL)JI>koN$+s{E>96^2#AM*19Z><77pr3=aT0N>l#T^?T!S0C~UGCJbidsG7pd+Fd@B!F;6TSg{F!%=TBK=D^j~PGN'
    '<OdJYk6>iFk;B)ObhEIv)j{kKe~!C}K0f5|6>X_ajrii1aMYj24db-00qO$Kfz;@ATnC=)WEA_8-p;6Rqy9%d9`BWe@tbuBS70Zh'
    'oxcLR@}OiAH+n?-CT>7az<gx?jrkDorH_78*_SXcIhT?0TIi=NV%G4(qb%Teox!!raG!6|D<AlKZshE*=&MirYOb-FwBd8a3!odH'
    'fuEAF(a7r|?wj29m!9`>0sYVluF0qN362TYBBwCtu`v5#pr@GfK+b{9ZZQ3)aiabmKI#9De#&q1G*C+~@6ms0=@s%Tv-HcodYeZx'
    '+pKwjwzWJD(TtrR)Yb}7UrEH@*dHUmec%`LtB>nnSP$Uqf&O_u6#Cl!g8NgLmx=*D?_hmaP4Sa2L|TEIy8_O-{sNtjzS8lZ>EQ42'
    'y3E`OXM#N8xNm51>Osf^eUFG+L2hc09|^1z%9C*2=<6Q%I5zu&J;)b5!u9{g{IFas5I5vG(5K(Agp0nSX1{Y0`hlJ0MnBov<0ttR'
    'puPwF8=8LX5LeU8_*VHeK7+$|H=K@s1-m(@C;>X`c7{*Q__C;F&0ZBT?#aP5*_!bhymEl`03KkaS(kw2k8+U_ANmQ;Z}7g_*s*CM'
    '&Hix?SBC@|>|ETx(aEFemD@4I#^@)^cS6FrbeM|*uC_orh^PI=39o~E--?LBHTPUS4~2kt^0X8S#0!Rh!;Y1OEC#>RX#sp5bS#H!'
    'w+i)8s9vpF`}$ZHYSZy+sTRX3<Rh;mweI*>v}XPe|JL6u-^Z}i(9S}!j&+492G-ftlYAeR9S5l&!L>hN|0h2P`uErs{l|a}(HD=t'
    '_t3}{z!O`*MNwd@TrN;Pm0T`xUl`w%FB==y`CTnRo<FKcExYKyr#I?UC2B!8jdqT8U%?y=1=^;KK;Kcd?%2RVwt$8oaZhQ}lKG+L'
    'Hndr80i&U>_lRo;Yf%7}!q|ok)(ib~8`;~~@5-#F%wrLi1lAgTeX-Hmh=mqe-bUpS*7sw*f$nrD0iU}(3C<=6>-9$8|H5wIXro<!'
    '%!f?>-X8+;0(Dtfv)dkk;k!S}qn~=|zi5Afz6>Y+1e*c<0u#<jsIL+KBJPPZ(3jD~pLEr*>kjwz0O#zd{rM4bPu%qXSNiJ(I>Y!5'
    'z!xR(okF>UaSj3Kv7Ovi0q9e}pK$%8*U{dQXcyTiH(>tl?6bceFd*1N`oq3Kf2!jLtOUBxT%VUY$l*`&_OJGmGW$rkJ?P0ETzQlI'
    'jQc&we}Du2(9VY)1GHoCsT9-u@b7@pJ;u8<9M{R<9pk6)CqD+_@4eb(tg%(5iV)Yy;GLFr2emW$1#l5uKjFduJAUuGr#c!y?#+4K'
    't8K@vvhK%CXWx}|(Ip*s;5yLI4ogvV6!i|sQIM<2ljuhp>bNj+SI6ZixrzSO8$Tkxr@(W#UsEP6`k&3dzKK5yKk2=r06XPZ+EH?h'
    'I^7vL-mz-|{a<zV@TBArqx=SW9(Vm3=W+jErhjr`tNXeKT)@5idKbF0$uI2@l*e|6u~31r@fg@wI!SP!9%#~USe^k6WX(^z<mL}d'
    'Qs4_R`5Dmmp{v&5c4Id!1D+p%zCP_60tPfTD9|?#QT_%ESG&5PX}tj1%tnlhVxX7zD4S~z*vQ5ZL6m#&4*hALr$BmChenRXvX|eQ'
    '#h7&qqrdoV-yHo@xE~C<0exE43iY0dy2+0Q8V~IpusZ=Kjj7_6TiY7<L_n^?c=Q$Uz&x#c^y|+_JMB+w<eL-B*dFZT(Va05@aYKn'
    'bnnQwaXG`-mCJl7^s|Tf82II=7WukmpmPei>JIc}4tN^YN+{gRjfC!~`tR5||AAfiN#1?<IW_uEIN&$LaY>GT2EZj8^bGEYque(*'
    '4&+aOI8LFSWB+YEr*ktNUco$8h+{bPAL$^IMaU43sG^JzcYLxR{|EMalY>5Af_%zhyvvR$z%>=_69VoImw{cu?<H&P>N9@zVBF|0'
    'H@qXsu&jB9cqsvTjR7;EY`^&=yA9X~fc?o1{mzIhL4Gg6?%mf#ylwh$-}HIb+63%W#GN_P4dC1Pt_FS5^zpH|V7tb@;sukR-iPN%'
    'Q{-t|P!I688#0hj{oFt6vQp7}-D#(2qAu(D<hfZmF37288O_5pSI>0>@-w2m>AU@Tdha^GI09a6T7Es&?k#SyFmX&7#zF#Jf{mvF'
    'z=lhufu1#3ZXDxr!1e=qUK@Kl36M`g?<a&IZQ<UkL#Fka_QgCKX&K}D04;(oQ8SEv{7ZYTXU8au184{Aqj6QU>(<~0jFXz;(K5lU'
    '4FOqa_CTQzpXeZ@Akz^WDxKZ-#*LqHqBnTAWXL=D2Cnok@n<I9GLFCoTB<3Y)Hi<Cw1WOTXK052ec--xVB#<Pc-d&QlQZC#@~?I>'
    '!??gWocICs;?I6=D8?SxbcMDM@cIVj!v}vhF2-$9j2lW@6CXKxAnT2vubJ=-BVcbd7z@ZzUX~!+9GI^mQoMt)S24<+T6bH;tPuEt'
    'iRdTp|AqJCI>r)pc28j*04LifZsCaIoA%KG7w~DH1osPkjd%m&hT|jPt!bT#81aVjyBNG-<j1s6>2er5=qZ<%t2+9OpE&5JF>E*q'
    'Bw(aJ*xdx<@__D4On{H^bHvp#`VWyeLXje7BRDQP)1HO?cfyvIaN{XX4d+bzh+hKFuC@~6-*~>2!h$tAMAGiS2FjO`cOm8FQl`mL'
    '*cHm(K-k<ve?-75j4KWr8}OP0IS={-XcXi6(4Jp;XxEDp^|FtCd#PX1{~lx9O1*XBnI4F`(A7+9j2m1x%*6Gse9%wz#X{cS03O=b'
    '3$jHVMT;<MIQG?w8q%fGzQ;YgoiMsANy!52nD>0w7U8~LB-^$i$0kbr6W@OWeHG65{y{#@1IvDRXioE;WzW9Vvw3<dyl*!g3HChj'
    '!VSZDxW`FKit$gz*P?yIu5e$B{%bPBeWH}QGfgHO$)>n!ANT)-<<~aG{>^D^ueTV-MtKJOR8gR%NL)Hk+RT#-{oxoJn|K85Kq2$V'
    'zm5BFd=2!I_#VcD>jCF*Ez>LTUm8kXh8V&Rc30r)+?ND-=gE>=2l{#-^5powE&<1YoJ2pw4r91E@&LweZlt!Bu<jcvjI>`$U4@E2'
    'M;O0MY~@Y(uk_>v)}3>-_b_gDZ{kdN1@wCboHbzl6{}gZR(xQt9&mq#fxZb<TEbWb#u33f*B0=6MA+F<uJKc(Dnh%x0lZCP&%SO='
    'EG!?k>SBSu&{560wX{L@=x#;P*Df#?@QSzyWbiA-%f=Yzgz-pVUmevu=nMO@Ml1oe2YtJ4JbWiX|GDGW4CYSXnY|{AC#c_?^$hVx'
    'N;flo$?85v+-+=TUjq&jfVmckP3B2$-)|9@)565sp-heHO9ymlduR&^6Q_`Di4AlpjXv7feFAdj{s?qPPki-FZbyH{R}bRr+_UWB'
    '!NiZ-HC*S*6F+@Z=Xq?|zkjQ@^LWO8dr-46z3qbn9mIR|ueaPk;y!D@K`upRzx9awR={^hgX_@F?DJK?L9ZIQhWiZ3y5)CAz>kNZ'
    'D35KQ9GXRTY<KywS@2^Q<-A#x`?k*?gQD6?Hw>pd0m}z_3-@nAA22J*&Kl#U-@|2X3-mw57*m9PQlEEQLFR~GR}<Ft&Ayw*vyI7R'
    'z+8e0#yD%hY3OG~yg6Ta7;{W8W))+K#&yl_HZ>m)UQupZ%#m1Rn>L*TrsSKB&AD2XE8M^JifUDhE(O}bJ-S5k`>3|7lolB4UZrvY'
    '>y&moxnL36aDYvh=*y)A&@#y>##0Ff7y{#p!NzfU7D$sf0lM*m{#<SB0?^T(()r58y&#fL*p#6!<_>*-2N$uRP7Y{Ow`mT%%F&lK'
    '?M3PQ(Jd-Z5{w&snc+T@;0ITptR>;6nM%WGX1fpK4fngeZ(=)lPki}JoaaC%25-|D-#m!f7@zp>5A}8g`gnOzU*{{!et)Rn=E;p-'
    'HYfh|Tf3a+v*PJnyB!a+;`q>>#{5*&58Zamt;N$r`*r?k+1!<H79+f#H8MOjMYe6Ul{LkB*Vxv<FUno3twX)YcI_?%+U2`03VFRK'
    'w{0Ij`b7on4EUXc&5E(y+>bCW`mb^=#kk^7+SyXFE}%SLHX`JrfOg+3&^c?jnOR3tJkHun_&8gnZo9Q|QasJNkGRTh$50Q-bjq&*'
    '>z9F^3~Iy;?C$3Os~3vou#O~BtV@hP^XL6(P<RViZzhY+e!e`F@I5@otUr8TGO260ALW<vgKcj3AhkgMDhBsY?XdRKbIQf{fS%cQ'
    'pYQ+yInn)m?l0}rBg`Yp-Q#Dw+{hP@v-Hp3GsV!~Mga$Y8b5KF@?o5x$8GRH%f<8@;>IXX@jCf~iLY3O{l)8td?6qG{MkS9V}2W)'
    '-|25s@sEBB^cAxo<L73*QkScsnewjicLMtNHecrXlyVw<+=uIPYmdtx^D4}|wZ*OfV6&R_gMM_kb^AmgKi)$TN5eRO^q)`jfBV}!'
    '|1saVp6LB;mVh4$72Mtjx)J8Lr!kI4_2kETAg)o|J_3Hcy$|FLC#X|d#g*Uud_Jsr8Pw-4k)OwVThCjb7(-hY)(6*Vnm<wku0VQ3'
    '+-Am|BAp9E?>PTI=^4NO^WUaFxAnQL_h))AxW&5BLjZKwn7C<J#~sEEu_Nw_8+*#leUm4~G5!?#bfI7m3XBts0^UvjVD@@Mzh8j9'
    '4~$#IxIay|0k>dYFxP7uH!*GC--wS!Y-fe-P#fAIBesKa4I#C$oe^Y-SYbO9_o2mz?X0jJYNLK0u^o(Q*izfN?Q6g~L}(W)V&YdZ'
    'K2GLfUjSaRsSo;*$XyOJ$d4FbNx)8-;+Gl%_B7%{kX;n;1K>}<4T4>cxQ`fM+?vFAM$p?fj3a{iN)0_vd}Zcu!1iKnPibs#!1iKn'
    'Pibs#KzuaOk;ZuC0o#eO9i_3I0o#eO9i_3IA)WRKFvb*P!f`JfY?;6A3+xf2e2Uxo@PmBhrI@{LWp^231;9^_I8PIO`>x3u(IePD'
    '74ElToQ!MoEYP20hnRZ+?-<aQ1uW{ry_hS4dK&nKnb^{a{sHeopSP&LL020)LQL{<`u$>g)4n9&IQ!<;wViF<qm4!Z2V0YU^ASfH'
    'p}#0TK%c0%#kGTOS;6{#vV#s&UJw6U{|aJH7!%mCtipJ%J^C`yZl-3gy1(_az&wGCqA-qQ@}FHCz~aV#8=1T)jrj!dEc%}`;%w0U'
    '+D?!T!8V7h1NQL#L708p#|K!C!^F=cn`ywg+{9aNzy^(sKT_lK7)w4-%wf9uHdj*~!2#yQ!LdgMbF<vTT*oQKtOJ{BNC1BYwS7oT'
    'K8(qGgZp@navaw_#F*@#aT3p4iP(wF(QivkyuJp#54axj{7iqf>eHOexM#^XClr%k`+qN<+s3v3?8o;1HXhwzd612t?C6a^d&RCW'
    'E(GwblcN2Hc~r^<KAr4*jK>cU?*abX07m~Oc^<fSi0eWV%LjZENPhFRbCkrN+x=DgI$-P=o#J%<5C;pmu*6t-^fd&4b62AHJpXFl'
    'kRSezz+=hE#Df2wznlG#1HVeYI}dpc^S&_e0%M7y4EOB-hjwAdy4=L{^Xm@eXAF95qD7M*o4KuyAH_n2tqu3}*{b2=cbu2AnD&qV'
    '#Xcp*nKO*By!mYd@1MsB<NU0R-1*q&UtZ~qIlDRv$&B6Y#OXT4tEcdc23dsbVTXIb)>9tKBFFu4pvBuht%>OhgHQfQ=r86b#U9W*'
    '+N-M;^HsE!O#83a+U%D{=%2!UyBOq{$$Qv;l1EX)yPb)JVjXb{ct1D(6wtGCj1^xSpXr3>ru;V&Vl4U1|AzV!v2bVhN4+B4G}Au8'
    'X4)s1^2taMx{b*Lp_u2htGUU`1bG4a1^B0h>!<s7<VQR@Jh#iCeav0WDD>wDV*|Vte!d^`-#+qFF`i|K{ABVmK}Nwlrub2?)eKHB'
    '@`ta%4h<}O?})d-o$L{~^8G@-4a*rfem<bhSF=xk!+pTl)fCT#aR(TOfcbDP?xS_c_pD_CYyspsW%R9)eLP{p7P!9zvaZ9p8A2Br'
    'b2Ol@VD)*PsL4UHz{UnlhcX3oQ0)=-RFekuiT9DaWrGcfxpmqydv~=apo5V1l1QQtkYPStwv`dAr>-)<Z@^2HhnUyo+%e=E6C1T`'
    'fBKmNz(trJihD)>%3m7<Kj`US`fJml{?OFW%jCbIu8T5CWQbpU++QLZ*4EH7q8;i_cq;bMw`cOH8Ka1&h)#(5c^?aK&jg;wdBk~d'
    'i}={|untj*>-P8~4}Mw;jN9H}-g^6y_ro!cXTY_%@kzD^+Wzd1%%=GF%EVv8H8cKR^m7&%uM_XZ<p0eS&Lg{g@a4+nd$3={gLgmd'
    'uYdfXfB1)8@*h>V`68=~yl<`-VXD`pcX2v@xKxi(U(Dqlqq2@OQ~BoW%2c@#BJCcoPhl_?)Qz6byY{(T$nRnM_S6NhUaCt$+~9bO'
    'w%@O&oXjs(xA}TON8ufi@f~>(pQ_floNR;}lO-oT@eU;6#1bSSnRYiK2+6^AAHkp?T)Qm^@5p!V+G1&eVM<p>nwrp##CPPyrdP2#'
    'khcp=)rOKe_moH)@-6i)VynqaU~!z>rNUo}9dZ4O|12`*u9$yE_O?sXU`Y<0yHA6Z9257bgF+lf_fZFu<ZHJ`gE#S5xhEZfTC_2('
    '=~<M_?bEO)<=lO-Lt8xApc0lF@jZ9v8m#<kaPP_TDo)(B(&dAArqoT@l8BLdnq@*!8ec#ji;x~zRFTf66^lTW+q6q#L5745Y5Xo;'
    'UV+3{d-9v6_GR@3Vu@b(dL`Zu9<$e@`2E@2Ue>Yra_}C-=0$w<y%X64#J-|S_*poa_o9<`@-6Y+Qdr`9;r*U&cjQ6)@g-Zx$1ynR'
    'Bb8vXsY{-^#Q{vg{Mju@pzU1C@-=wj`9(e@!EbiHkWW`o(~rJ<R>AM=aVNi*!B_Tpl2sWv`ti*@t%C>q@tb?P4=xuTN->0<<~vs='
    'xEK5=yC$r3@$3%ka1iBh?u#G(#>)q(^YD6k%H7|b(BV&4`F0<^+W_C*^JU1Nzssw?jM($wUajRuKYx>#c$tasJNf0X%=LHa-hHR!'
    '{)zq0H5K>UFvBFvW<MEuw+|8PrF(f^%KH`+TfLNbHB0#ub6*Fh0KmWBgEIE(O$LH3wfCMBB9Qtil&??0?iJMjD|eMB!*}@m9o^2C'
    'HhkBGC!Uk#yH;>tIk}@>pTf&!@6$uOtjRmxkKaese~PlSjo<Yeo;xvk_Y%L)4s5x*D?*wcgI(H0E_|rD9=&(F^4{<9b6Q^Qaru6a'
    'p9(%(&-^>x;=f@`a_KhJGE1K$SJ&`)3wO4h`qLE4-Tf21vJQ8L?Ri3&1MbuiHhJ`M=XbIU*&yP9^g8auFu0KpD@Dtw*WDnUVcBcd'
    'smPfsYp4OV%PVP|;jm=%S?oY-PZ3YgY%%IC9{fRvTEq!C>ky-?inh3BXYPELi>udhlX(E|sFF4N_MlNnMt)Zh106K&Or#xi(x%9E'
    'eg8Uuv>wTd`ma$nc24|sUQ{O;S-#eE6f2`Czx(|>>g<H$jxV4z)V3L-x~|ZtZpe!vQhi$vY|wcx9Od;qsbt?N5gX3{jWvbwm$cU~'
    '4+DjMn@IR5)=4kQoSd<83Ros41AIbCgB&{6^X?hYIcA+BLfK9pC2M)MFQ;Z<g|Svj$txh?yFm>xTY@FhO&+qWjj*26;OS}pZyFKS'
    '1uLh-<d%7#XMgz}EHq;=X9JlPW=Az5SaF1xxGM)DD)$E74b3n-4n@~?{k5$74iGNxswy(Qk3YfhnV8yfnU2r091cUT&RrQ7=SV%a'
    'Q3mKQPH@Z^MKL``YEf4H(C0%}Rz+9jkE*DS!J<2KJUJSg;xPZydrN8qqH%`DTRX(HL$K~BSOuNe72Wa7@@LU^sFC4)gV7RQ78m^@'
    'A7nhZy-gKHVSxpP_h6LGu|=;HW^6Ib+%M=*4!WB97p0F~fsuVVqE?LJT4Hn`AVC;U#i7lrD-+%?vH`|RdpoQ};m}U!kGJuG#h3VK'
    'wZM4(*pFxg#E{{-@wVumZufH$UFn&{a8<;e)(6+hSAYE-CK_oUcY@ip&J#k&nWkB*ljn(k)Ujg(vk0fZX`DBJ7H$=yo`J8RKl#wc'
    '!(+ctbr)S9yC}oVS+rgfKu%ae$)7UbY?E=ZWY<bXBOqb50i+1l`+Wr#JfbtS5+2*4IyFwY9rPUdy`*OiYs4H1=n!|N0eN@+d7^t#'
    'JHtst8c^fd-XcfI2R-OT_Z`=@)iiH+Wzj5#q|?f*2aMaS*V(n6`l9Qh|G<yPU)hbnau1O*2<bu;V|Zqx`uYA0-rqd~fO!Tv@+^Bm'
    'Zz$YjL;u_$#CYIC|D21ctbRUM4XrFm+Z&JZa}*7q+WpMerrlB$*AV4Y%bbJ0jThx&(2sd{9iBw|!_pdV8F`zJ=YjV!K!G7fkq!Op'
    'kNdi8ShhBOl<!sf!3Q93ke;7@_A@4ZJT@ZMKc0iWJrBl7`uF?|<0yw>-kkeuRrm9-(_r0z)z*_A{f2&YAi<N;tO+3bW+4CWeeIv$'
    '*MK$=<@1kzfgA<C=xTT;$n`uEQGE3KF2(3J5#9fl&v{jV{K;C3?7#@R$RXMe&%jqVd6RtbaWUw-0j$8&?Qe`Y2?a)GL<#9wSW1lk'
    'a|U_)JrU7-xUJIwRwf6LMqcCL%WYnt2kj4MPV0~Rn|?mj5@gy$H*VYy1JLEiy0Vo`-^6y#X57B5)7OWaW&EaM3%>Ur>dAsRDW}TL'
    'i^;Qm>R+szJb0_)sqzr;G4Op3bLnK~DC0n12d{{?^&$l8HQt)+dxlY<V6~fSWLf!x9yB?Mehkh%t=ecjwwNu2JFO-{1?20bZx2C{'
    'Jk<*)IP3Tcy&g)(9#|6aKD2(7d0)HB58Z-R66KtYncM>vc8=c21MnqlvjNs=qE|n{-P`Q%@8|R&Z;{P}<*jtO)u5e0xZ@Th@o+vX'
    '{y1;8<=!eDt+sHE*uN(F)IU4+B@a{J6Tjud(_hA`ovP`_1N4D(;=|MJkVt><n>!b?3M}=!l35uH`X`?Wm-<Z<R?@|YZt-V6HSY;{'
    '`~>4#pSAVW6gkK>|JW?X{M^qg9gV6jV=|Dx+`m2d$rG%>0p#9o{J4XPJ5A>I^xS7p&}Xbd1lBqYKIZegrWNjBchFy$hkdum4_GBd'
    'Ea+4T!KRU^C=eZBjmPw?^9tqxWl?M@KSdxXSaMX+p=wX%kNG;|d@VpmYT(tyxNAQ$@21LDTN7o*GOYTL)EITiV&fI-c>H`D&vP41'
    '^dVelf7XW%Oo1gv@%@lvZ2b5g@RXq|;5YOxsl&4Wu|5^(2bjOf(p_qhgA3<TL{`;LIES>6<1YLBqjEw8*7*VPmD&!$gWk@k_xM$_'
    'aERgaY3JrF9Q4>gU$h1KvbH9^b1f08<;2e_=y?uv6Pw*Dv2_yjeHJhKg32z=jT~uH^ePQCdVY*v$M-}R**R4)EV5S>U%kN&J6!Ju'
    'D{k2d!zd-t|4%BqZU7{rCzLc>E1MN78|d46&`VpKuIgXSk5nZC+>C+0VXy73iOW=LN7X}ln^(lmKo5Vr?jig;+s1s}*X4Zs!mS>R'
    '_NBh*m5`ZrOwN6b>j-q2ZW?WE8=md{My_~(Gl!;(%YQGI&~uz&lq6=6A|3eh8V6eE9pHkc*7vF|<4v!vu6F)s?-SQ97<m4haOR+Q'
    '%0@Z=(|)P-z^t~8W9U}~@<>IIR;?<t7;t$vt#g_*#v=_fKl;IkhtAfxv$IwaT{aqZm}iNZiB|M)bd6Cgz?0b@<<}%%k(Yc);}z&_'
    'b))Nld%vPs$F=NKTr%Agpo2K+dkS<BKm8&-crnj=S<bx|p7e6aRyTS;d0Ytq-5Twup`=;^;emP4>!Aa?WBpP2@2q|Je%R{X=s!Ta'
    'suHxL1CM_b@th1iY2dlrPA}aKy#@S&Sn@Ke!HHk>^;*ZyVTEAjB|g0N+4#ZdpKxKi=GL`-3Ae8ieXo_Ze&x>Z%__-W3;I?Mmcfl3'
    'F*v#EfbYD8+BURH2JZaU#Pf9EbL>a;KcS1(&GK&1Rej{>&gl+AK@Uxo#(=L25$9xJ+2!Z>Mx3Bw=vm*O4H&U}C`z9KE`FVMMkalW'
    'c=(^_<3G~DzrSD6B-D0!R&mAjg4FepB>jS(n>cxzG6IZVi2p#Zf7Ba6%&T5Hb9B-4D$X_^a$$+PcStW7ajTPqiqZ<^>redu_wq`p'
    '&L4R8n;7Om4|xN0^K>fS9)8IAKgsQXCl^$TmF}==j{`V6Y=zTB2FDNGcUYTe(DmPMI6e~W@}>qWezmW^*Rge2E#kN4B{{q<vbP(a'
    '1)Mf_rB1N&*&b{ux6|cQU5taO<2BIbM4vsowyXH?GSR2}#rfPtdcT<Tu;^O=k%Mi$C<p8WUII=HZ}uSIPevZ=sA~W7@tvIZcbdPj'
    '^XxVr#5hH}7@mxOqR(GNd<Ff~96O$Y9Ws)$O@$~!U-R<l$6;#tEN;5qsX%m4-Ie8IALUic^ZjhGd{A%W(z3Vr;xym+i}`-I-0aW('
    'dc#%MLx($KWS-TwwUZ!IYV^gJs+bmLuOB3{LC<vS7vRHs=vF-|)h8SVR%{7!XU<-@0y&g{yt(`$9`gIz>9#LL_*+wUNzb|uxmkgY'
    'VeqBF9gB>$t^=6!9`s(f0loJdJh$#y^|>E^#bu1tawtKrRo(fg-S!N&_aM}jy)43)uCyk7O>?C0mwFhpp~zay)(An50&ela?gjfK'
    'q*%4Gwqc%n(5D3Lm<jg<b__OL2;+{mEXNe^gKo?4(Df7}`hk9KI42TG$EruMNPhYunB!tZwOW*$4s83H4(ndeySg0KLvMfJRg@JI'
    'ZU=miJ7G6H1{g2N+y0uL7s;uP=BthkIqoil+yc3K|AM<|Ojj>*ksJCvU&qs6Q-g;FyE>jPC00IU=cs%Z@r2h23!jA=Xped$M*o|^'
    '&1(jju4bxW_B`*nLRUaN`48{F?!yRnkXum+cE}Wo#WZaZuYvwiLgk=;{8j*#4$%f&<X#81nb;|}<qYUCC)7?>!d6rEmB4H(A2UM8'
    'NpG<-FtKdV$B&L{*%4L}UdF6?QNsw9d!<!2MgtQs3UJ_3S5K-R<Fl?R<vOghn@Sbq(#LE~Z7P`T)Gmx_4Xrb0=`xHW28_omUy+On'
    '-uQ}#Tc)kH8S+ePOEp=(1O42BUfzbxI$~x<$1L8s3Us{B!EV^1erUA9XyR3qjyn~RRm0Tw)UT}OZQNS+%xacSYAph*IgNQ7l|X-E'
    'F+`>A=*WlY`K5JKzU<4Vt{97RUsmnA^Vlr}=)*Dhi*DC(C$IZ*hxNYd{(0BhPVQpX8OQA7(r+)>qbP(Ac5!j@6Oo=Lunvd=SSyCu'
    'jd-X)e*#}7unr1rXrGHBry=^!h>7%PQ&lx)sz*|^wU-W73i&3sBbn*I5~q=#^y-_qD!|F*iyYv}4llA)er#u2ygOcJmrt^Hyt7U#'
    '8I8eG=TG9@MA9b0cDyN)*71FwCE}7{wk+;ody=KTWMP0s-K7GY%saquh?7JM`hOYmN=d1v9lAn=9ed`OF&5&^qZlKFRc*8im5mWp'
    'YDw*i$+Hv9^m&SS*WWEU8`(+M-&Cfe!M?uKF<jXz$aiSL9<<syQD<MD>d1-CSZKc=S4%xU0o_a$^SBc={B@^nCkDDoRGMMt2u5;5'
    'l4+!;m5UKGG+y@{@Te27wYFOj(wm6SRqd*E%dKO*Q0tD}@w&*9kU7Vij9X<}Y^sWk5ngITv9j<IEB(#B)!T7B(_gImG$tqg?OS~X'
    '&AW(SngOnn|I(ByjTcnc?+)1C@l(^IJS3ps#@(_HpX&E8Yl=9*=%c3acMW$^zo1Ed!D<3#_kSxRjN}V<F7B)Ykm!rN1sgciecHBh'
    'ypM`RHBzDP2K}yC7p-{%x-*QjV<Se)cEhR=nOdY+^>|Mg32V;Ian?V613t)R{l;o$<KfirzqOe<4h!|t#c;jRf4nGlyK|1+LOlTv'
    'Jf3@Awf*?G?5n4C7Xq&-jN(2v#YF#pQ6_DgVOA_w#X8D}`>hTi-KcVJk&I`MW8R<>xK=dQ@mXZ(zg>epIfR2Q;aUZ;&d-t#esA*z'
    '?1cz)tOPvGA_nAk1v`uLN&^1I-8rCZx<ov`bKK58RI(WTrOuuvy2qXN(vukN!4m3Xq)Ljk4YO8eptr7Y4ObBxrBYd}`TZGiat3%2'
    'uGKE?!*fH2v|q4uGoZgNhii3+`|R9Yhkb8faI<#XGYhU^5-~^C8Q?t*dVQhLK0cyf+3>TGub44`d{Uy^4MLV5rK|jw^P}uB1G2+N'
    'hKYYLW1kbW5wT(oMs;B(_g3tXHuzfcYovG?VOFWfR3tCgrQ!{Icf~9h%r3$Vmq>|gtoS9u-Ts<cn7NR6Sg||>+nE!rIPIa|4E^4O'
    'tsYFq2u60B4C|){F`EN^czlqA`ZHcUOc7{j%nShgq<+9i%o$&A#UjQ`N{pZje4THl8~e4r_JnP=-{6{HCWt3V>5IjoYKw8(*%n+K'
    '!w-$?q}?J#JicE7ZfK-~8KfET<`(b}(0IJ_`*7R1aau3ZtYy~T?~`pK<E&mBKn5k)HeAb{i&Z&DnTkbfqG{Yd@fuMAezE)WpqhBd'
    '&gY@35K5w1(J$_YGvKy(NX}Xfs&{-K#p)@FoaQ`)Pr4YJbC!MA#icpNVZ{ok!Q>TPI1*uzF7AP?P;7=xA7>5j?&)h*>k`;+2%F`Q'
    'J)QfpIuBW;T}O0_`|7+H>*bI<X)ugC$FHyrf5^6HZB@;XW!jBJy|~ZLwpIH>vehzHwc}@+TTfnuKC<o!bm{t>Ucam2vOcq}qJ^{8'
    '9B8_501;h<D(=^3yOXrUBXh36OJSrh*IJbfWMJ30Lk2n_serdaO-dma_u<)2YIjIHElMREKh&U`LZqe$WlYZ7clFp7oVR_>g95$>'
    '*#NTV*a0WCMZ>!ye+r6`pL>OCd_3>e_qMq3Gdxcs&~e-OaaQD{z0k*5!Abiz=chs;FF(yNBS6q{Ry3qL&B49_oULg!13TxO((kk4'
    'LeATHb8<{Z^EL)Oev4?wY^=|JW9<F*q^%d>0?phiNBP{^)z@)5>+fIAGpCvCt?<+oGYjM~$aQx%188vje%tVw1^Rgl_+p144ztBa'
    'yO!BcGVhx?r+6{5CcEMO<&S?){hDdQ&kJ>$4S#qZ?z1pz>eik*b&>T_zk~jm#s~P!;<YnQ?JVlq33}Ile(zLi7H|;Yw|KnmZ>p+e'
    '_xRk+J`byg-(x?ksq%D48ctrs)*<-5+kWZpya-R9?tl4tKjISf>y2BVV<l3=yZ5^$3PHaC4y1rXdb6)^3Nd3f9#425+;84@eh<^8'
    '@T{|W4_q%l*JrTF?xhdMFtYgB8OJ}(``E>{>DO#9_#5@9nMcr*y9W9nBMx0!?rbsbYxo7sr<uq5f3i*%f9chT_rdy)f0{4z{COH5'
    'H#J%8hAY5@IKStQc>)>aPyK^-OutSB51yRJ=Vz<iVb<?$KBjd^VP0OQ=kHB_2Kye@9p>ZyR&fpHYwJww7=_#0yumtoR^x{0ZGMSg'
    'I-lv+^xyog&H52DkCz)ABA%Qw{{gpCLoX8!1-oNmnf>a)W-pjc3pkNTHG;ec+|DTCE>hDGD@nd!HQ*Q{p|UX$?D<97G>S12{yMG%'
    'yL$l}HH#N9Y3X<n5r1hl<uSIcMzGZ`FK0%pc;S#H8)3}rm&T^Ycme!>9UsA-e(5-UiWk7=+4x;B`voJIV~nJy7`=UunPn3lU5r0!'
    'kM@<o%59utg)k!CQMadijDqyRPL+a&js3jG%Dz6@FuMfwmEL32nU4|QU_UkX-5x6h`?dr04SFLYd$5DSE)OviI%^gfnMDu&0_^b}'
    'VDpIYu>z;RsL(G47^~Ssze|5HknTNsf^qI)oZrE&Cuf;dANy=zFTMa>ZB3wy8Y%Si1+!mc8*DR*5oh`ZD~rbV73@HaJX^nj-VI_L'
    '#}y;Znis|CD#m_iCey&ok6HH%1-$9JoH61X@g}GH80^_L8==2|-)vgMi;i^H5&B17V0`~>oxaD|e=*U&q0@!+0{rI2cF3{+9rkZw'
    '><W(b&@s;C0QR3<aU4&F{Vfb`=SUwNyYM<5H?ckEwHm?ZHgswD80n#l7;lCV`^~XmU37Q>U4poiBYkujgBg!F4vzioqSqJDH_!3n'
    '%8_1x|6V}PO!PtM9`VGV_r+?P?#1F->7Q{OxSw9O(UqK;_qBE7$9iF^C=eO_hzL}GuMg+QL@pjklnI$(1u7!Ca;iYo5sYV{!0RO$'
    'dNp)$^?j;5snQO80mUr~ayt2lV(dlBVz3#V(|OVZUT9;b#+->hq%F@MRsa0dg3Uy9eJ{7=^2AQ}x442Qu|S>gJYi;CP*l~qfcKOW'
    'e*-_g;C!Ep!=YvKROvhxdXDXtvY4mmA_Lu=99!nzx2Nms#Kw5?*J#`?uJposKHE+Owj26JvHEBtqN}UzVGwS9YRmO)UN8z4Pk}<7'
    'N&eoi*5jUMxo#QKnRDCkJ|Hs1EY8D}J$&0=!%Y4tqpi--eg}HXUnYOb;g9>NI!<Mgq|G8rjjh>NY1b!h<8<kuy8&k3>pA*{D!|;s'
    '+kfO&G#NBvsGW}WcC4_^buTcgmI*s%7*Ty@BySf#;}*_5Y+&4M=o47?uIwYAMVrc-{yJbrJgg^KM)~uHUktPO!$tO_)EL*3zv^h>'
    'B9QKFy8d+E5%}$?<=4s2L^}Yf4%oxva?n{XhKgvw>(f4*I}>kCIOFGs8bHx(f%{3-VK8}FbQRg%8T8j`u*b8yAa3t`Q(+dzQ<UGQ'
    'h}&U#E@;t3bI_CJp<d9(c9LI5*5iJOiRXC|aZCr6zkq%}3{ft@4xRQz1jfu@6(&WefIfv$)4sSUkjp*;IUU{ZGjTT<RXkNR$)?ES'
    'O9uDBIJTC#4?0|-e;4?cbk6#QgXoK(Q~MxK_d}GaHk$IvL{=eKf2q;mS5UC;lUVCYim2Om#o>dWO~(CnB0_=@zI%-D^--_62}bzt'
    'F~XN%Wr+6#Grsni@#UkQlL=;g?J-`5;7Llm1m*DlLk|Dr|NLX0(cOO(0UUfOuH^Us-SaJX`}9k+N-w{DzU7YyU{??;W!{enV4sna'
    'xE4t;+$ww}&&-88EsX3vi&ad1yU-b^G6L51nQZULSME1tKe!<av^cKa*A$lZd+dJU%kQKj?u;xSg~BX>s1)an?scq*K2V#lF61@y'
    'mSTM&KrT7k{4VZB@0Gw(S-EGW+l}iE{+gto3`)NsyIzKK|M{}}>MmdXoyfk+Rqji@m+m(7-|d5v`wY+WD`b8jRF`8eOC1RE_}x9_'
    '!8_rlRC$=Bd?{Ny1bc2H`}^?qQhvdN;4k9o*?qIaua{?AzQ@b&_V-8mEnl|ebe8wroF7R^#U6?LO8t?&rYZv>U{}_>(sYP8YwuO='
    'gRulg=5rh~rXQ4?$5q-Fbiic)7foN|Rd{*5Q<v+iWWW8UzQ(JAJ+}1Qdi9$<-qUaM)l9sDd49L?+1=6Gb(<x>lXdpIiS^x^w@)@3'
    '`|ex4zuyq?CG-w@v*%w@@0e_I^5wbC{Y}BYym*gv^Id#d)CYef1r{%`u-G2=ipxfmdE=F8^ODXl-qU&`FJDWqN;lucSJ#tevL^Pd'
    'mg^)Zi#M>FlTJ8ay*^34>2Hzud$OhW!>*oZ+b8}oufN`JceeFdJJogsnC)55+izla=iQUkkH~XFQjm)~|2^fdxZis2dhcHj-~D&E'
    'eta%~U*tOT-k%S_`x@5idB1eYA$(s~;XC8Ld_D&5^C5I~9*E{UP45q`OcM`2!EOyxMD{dWbKm7VU)--lmpuo&L+W1GGH}U0B=#Y2'
    '(}O4MExIAR9kjE1J>i*<p(~E?{xsO})6z{hcwS`qen`E`Jx1`x_#U9IkX~M)pRc$6zOLwddYC>qhRZXI?>TVS2lyR+TR#Wnbp@g>'
    '@^|bQyo<`)2@ZY9{2h7r$=&16@k2k;!!aPuEeHDfR<kBq%6F3sgx4iV0l4N2y?9vX<X6s!tkbFXrFhS&Ia}}@&xTmzSps-Q#1V7j'
    ';CfKn*#z9d>;85oB@6g+QOkU3aX+rX8gQB8x3}6ZN_KR{?h84)!V*uG1%8?WEIr#g)F$`U)Ee`!#)vfMBz>HtmTo1Vo3oPSF7q3m'
    'rIO>BUwCd}l}L8WAN*sjpQ*+P&s;q7%0zrc49^(A8ZUdf2t#Nm5gH>z%r3KMYV?`2!RGrW%CeT*c>Wshe$(1S;Dj#LX_ZrrhR0it'
    'w4)d0m=|}r)p9suP5wp$qOwPCs@I)O=Y-+;Wq9Tq%YfZ6mu8+|Z8EqQp3Nhyfu)!QznPlu8^Q6cN@~s}0AvDG#<1?7YjXZ<6)4`U'
    'lvY?%&6NaqE@RA3^Q4_I5KZuYu~nG=g1LoQ9|v=^G-%){lFBn@#WAd*itCIyk~C2%Xf(7Gb{!ybl>>tEOnxF$(ElYMhpTUKzLycD'
    '<}ACDwF&uvHCQpPY-?)SF}N?SDDF7OZI_YBVvRyR=6IG(ZR0rxC7{iECQnytX>U=x3D)rsu@1w`ZVEtacn0ALzQ@|Mp~<o0Pt#6P'
    '!EO=T2c*jo&q*@5%2?~D&wO)kk{iQVJ9B=5ugzJLFqZ?KZ4mpq%Y?~c)7f;^<X|FfYUt;bJ0`LzmkX{%3|BJM3gwtH-R;x|J>glC'
    'Gwb6VIM?u#IWr2@d*;v?_wI$j`ee7WBYTdP=9Clom$NHx-~ZB?lVYkN5ovRFj8*8OTfh~t-?XFGn0aW>^9$oN=crC~(uncIV(kw+'
    'OAW-k$u+fa^vA1%EJDA=GwKkTVQwT?p1z&!gl*w^v#G{>W6m0p8u@RYG<?2?abe9uK#G`KI^Wa<p5ZiN4&UxpBWxY;&eZOi@?3F;'
    'x+GXLz5&$Rq_^6M5-f3E?WD<p%XgUThi5_6SQ9P6-4B}9+F48FZ#;ABJxiM&zOx-X$0DwGdD1c~!*SL6iuZwh!?UKqqSp?Ev27)@'
    'r@UmAA%EiefZoUa%N^D;EO%0yT1Pve{}5{cLO-`{1Xg}Tx6uB^c*{+F=q@qmI&f3}?sgVZNT=FLrgjz9Ukqw#>XM}9S$@IDZs2<-'
    'o$AEg&S+#;Jfk)?@44Vk*d@Z+ZCJ|;`j_42apPm|p{ecV08P>qYhO03%rO^tqRZ!_(Bm>FLd;>_wv6u;){ct8qYx%<bpva(Ho1qo'
    '`#7s}`KPmKf67mOnd;q5XK+LwA2EL$&(xjdTlB#X_O9;nEZ{lT8G`XTDA$3m@NBi1nw&$-=lgMP=Z~{915*=IV-7#o3(TgRWQ;(t'
    '@xDX$NBVm;=NOn8+dItJ1Ug|B)*xgOEf!NdGhdk;XMW8wmv-tO%6|*wT?zCahoB#^hP;ot-tafp9|pvqWA61<u_2Upj=7A;hgg#e'
    'WYBdh@oWc{kWX|SnX_$+1oKxD$<6tl(>bdJ%s~`yF=u+Jsf=_rUz&OcxW?w(NF1NSGtf5XYy@3xjLg<J$G}J0O3ZmK@7c=CqfCH4'
    'b6ktSV+!YKO;OhKYvSRq$07#$Pvcu{JP+5CU{pBBaDrzp;2EX-d1dM%VBK2W<pQ~&2<A`XSzFmOuX_AMPaJD5#-Il=mwSWt4`Gbc'
    'P7;InU@fGcdU*b#$x-I>LyfyE4CIT+%{FurVtt|?dQj(+T;rKfZLp3O6y(+2zQ%KyImi{%4>pgWpIGNAo%m2;O{}%af#&m1>zZOt'
    'w}*5y)eR^&xHDbrbYtoPvfP}V@=IrAUnslPaP_gS7QRo})pVxoRO>P@=UHo{+4W6U<Fhc2c7`&^n`v`qCnYGWr*^2gP;-`NO(x6s'
    '=b4>9Y7_(Sgwxq91zv$x`Vh>Jl7LJOe&`1`PJ!otKDVP&4Pb4d*9y;vrnfVEr+F$&&0wUd>0E15>#;;!2*1A`rW$o)VrqHfS%jD`'
    'kF`|sY#^Rvy?9@-d?^X$z8ifIVBWmMnu~VkNrEyWM@-`58J?3~zDK%UW4#)X<2Y}yE-I8-;d!2ztIyO9F%)1cjdj|TIja)Slrwc|'
    'vAzNy5NmE5td%+8!<!sQXoGcUr!$p*o-KlPKbVDck%<LKu@(cK3EGJ%N4UnbaQNL0>xBAP)9gKmcT@DVfr;RR!ql33C76{%kVY?9'
    '!@%f?1o(zD1f#8=$+VNwU`>`7Yq9`6nwl(4fl;1$))siqTY_`C4-i8}6zhSmn;rZXB^k7dYqC;gI!C;*71o)&VJtk`X2?_ovI%!4'
    '3$nu8eHh17X9MK=|4-e!bti6YU7-KvymH3Cp(Wb=s5>PALI{vcZ?uC;B_Rvi!I=E|v*s${OQ&<$+1Y!4=OM$f+ZIx(YF+1=lim--'
    '*)6!x=x=ZEJvb~KdJnX>*B-PY9l3Mfo*NagXhUZ)Yvh2=7qmCq--!?2b3_zB^81^Qab9A$9$xMLZ`XzFDV}>p>i``?!GGJ0@V*?%'
    ';MUC{rC6KRtJ4|lxW5$3#!fP_!Qf{LOkDpjJa=X|49G7~T-I%9zfMDXuKGLx$K|x9{Rr(piV@a(smTAGxJ*GdmG0}}(78z1Ub{uy'
    'SmzD27Q!-LH&wB2?Ac}?CuC=t|26dm^repzhxx$i^SgxX2H8~6p%S?5XYONg5$OtCL{H!%TKE>_F%>$a`GWRAsx1fWJ_(`i{r0(Y'
    'd{6s^_LbOR4e37ey<4oAyHB3zc`R@Q)7iF+HglJKcOMz5ve)}q1h%&Vw=DT)%D>X|oi;8I`Pl2=OTB7oPkK%aif<6_M?P}_fa6yr'
    'WG7Q_Oi#Y|zs8>wj`73L(%Z$Z9Zj?%8`?cV({|yKzi%9hYYxA&Z{jt$iddU*Py2!Q(V@u0^0=Y6Xw|RR%%Pmrye~!1ky3nlTv7a&'
    '>|=UQhkQ-%dDXf_(bx^X|KWaV9I~~s<B?rhI)?<`uh5Bk{GD?SEk_42%#S`-{BZrR`7ymuiXFgtBCHMNZE?lgsuZUP@XNv8yz`F|'
    '@mC5P+sFTfYbHfuYdav=rpUjcP1ryK6Z@3D-=DqpkM{q*$|qVrLHA+i#}qebqa`>np{W^`?S||hz56rxNPf5vY2Ow5SpDug)@SIN'
    '-C`XxtmC6HlW^bP2krZGFCF$(RrlA=wN{jWOS(VWk4_v#SAWRYm(5yt;EnAz6pPU3TzuL$;I}aQhwhu~dKs1}K7YC|?>CPz-Xq0D'
    '$}8Bul;%F#3fz%Tn>Nnh{6H+A8=X7gdpbi$Re;Z=a!e-|=i8<G$ng1ee^ZLPeOm7&cMSORW}CJ&pZB_N4$NJ-#{S%k8TJi*Uh#h2'
    'eta&)yK~tM;zo=zvh8nneVKfJPL0l=HCi-sy!!EZ&EK6@<OY<Z9Khv%*<9m{AG}8($kzKqQZzB`LF=>t$Iaf&u{Sfs9@-Y0#wOc&'
    'pd8H_EwwdB%s%@U?D^Sn!T(=b52e6=UqnWey!G|-csc}^<-<66kk7aE;u1U7<E?%^%?1`YsRo;#Bk6lT5FtO?$FJ+Ps$=F9`NO!O'
    'hQGjbLQjWvEmPPn=n5@7)@Ns)W*?o&f6-1|{lqe`lT|~0n{o+gsAqlt!s}mwvrF!#%#YMDuYKrS+qubuB{VI-SDn^~Ddk{dYHZ~1'
    'nFl+)YGg#r6GU-wd*z(`ZhxtYd^Yxv9C%@w^!90n{4ES+lviAzv^L=Tq;*_1F2xOp0KfmkeRQ>pm0P^s3+(!vRz$uR>kTv;E0YUE'
    '^uAc1j_Wx~#Gki7GkL6u@KOYgb-$s!MBsb+e0onAxM{BINWYh?lm!(1Yz<Ci`n`biI3F6Pm0isExt7q%Lmex{=dJ1eP@W!8+>~GI'
    'i{LU`aqUNBYfOUB_W}7M=w~~IBN+Up-YleCjQ)OF#j~}x@|ZQeWB7>?I3f#h?Lr$J*8?Y7L-v=xr}!pa@0SI|Xiq)2o&pDA3=Txv'
    'uNnE{HFSIUI%FSVziC~kPMlzWk)L>iJ)3d7@<MS<e2>`XhjDa$MjU<9Pa291aznh=$^vIj1`TCQ7JxesTFaZdLid&Zy^Hm!mRNTQ'
    '4syJAeBSbR_H)^DF6GcvqTh2By&uZg)~t<7F&}F%i!J#(io@I@Y`P9{aRQEe%F`&uy}`d<uj540x7D(BKWZ=coyukVbx?k@RouGm'
    'YaLFO)pI+E==VNoI~#7JDCj7krP$xM^tz_pov$-F=7Yo3R*Tjd9IpAsELY}?uUW$i8i_!73QQc2y-<LosMivEp`XiS@mj~t##35b'
    'pX&=8=O%Q9trVJJln(((3>^bspLeLUUUj|a;9jq+4|PMq+*Tds*j6^@b7C>~e&j<V(>j7HH{g2BYo0{sRgUrQg74~&0c)1Yt7h3Y'
    'WxgtKzsnt+6EIX9VXs}CC8#@0jOL-kS^|^{O}O6JwE=VCcP;MQWsUi&@S$mACQF|ZXs4i70q$*%k>&3`AK#ZcgDV}=1ju(J-4|+J'
    '$%JeG`-LX+(mtO=y$YJMw2mW_dmoa3&KYXV5$Y|l@2IyZ>&e{zo6Ss6`+BQ`v8F|=z=v+_eBZ1C`>RTgd!5W3bTZ-Z<{@&-3i<1G'
    'orAEF<d3XVTysv+{{H8HGt-*Q{`mblX8mHZB73&vx-0nv%6%}+h`fP(yNB9mOlueo<=tmR`#O;DO)c5!hcD0|fX{~(hnB6Y7vsrL'
    '+>Pn?==}I&)JKM5I#v(hW|Po>l|47`0@_LXc_aqiSG!@Yv2VBac}%(c$kD?~jGyy$I_8-6hI0B@JwVIlW&%CJ8i;;yM#_HOWa=58'
    '!<>ZR0Yx1w^aXTxci_nMv_tzs6tvfNL50bMj`B!T--|+{r7&SmR`k;(*%@a??;cvo&_JX30Pzp@uo^-Cmp(g6J=Q+KUh8{Ihcu{|'
    'V-9_a^!mJpd%jFje@EUa$ghAa(($-93hv7-ol!aif^5DTMOs30Hi|q8Qx|F2YaX$7dDC-@LA$)M#uNt?SFUvO594*^9Kk7y2?%<B'
    'rzt%H?fZIA4KLxKTiEJ>>`v$3s%P|NCiH$zi7$`fOPvh6ueVyAz^CsRZoP%woDD}R`4eUys$gg7+>_t&XdlhMsY$jCEGEzh0>>!5'
    'AIg0?9e83(*WJ<oqwa`0yo#6$Qc7^xp^gil!Bmyr`*pj%mw-8InH}g|&DzSzKjQps$tMKpi_*_1f2z<QMIST0+TS0oufyw$+Pyl3'
    '6_6g32YXzf?`yFVacv@i{PW95;M{vQYFW@p5MnP*MP2H&?Z)?YIhsC7{Z-lL`J-sRR^`ckbWYpqaP(U%x@Xo5kyKS8ou2W+)Lu|$'
    '<T~+AAWrmgwgtH4iV5e2;$Cq7P=d#w&PB<SOPR8Rc_YCAO>tm$T2MTUy3*3{>?cL_>ffc|!0Zq^zvlabIbu=6h86%O0(v|0-X7_5'
    '!g)WRGx5EBEKD7_>+L(&9bfyyp4WkA9ur)2ZsaM}g7V>qR`^oW`_6-bRODNB{y;Vp@<repq%|LB+*7bFYo3flO$vH#T&E)YFL$}m'
    'dI_xS<24SiM*_W5?ooE&_^$100`AA<XZ75MJL@aHpA5>z*|VRxNy#s#eplP%FBf(9X#Z>e@K5ZiSlacX6}#@v){|2-ko(X28Q(wK'
    '`&aFgK8JySqWGHD0rdvTRd)3Ea$3n9_#Y{Lx-bWC-7y#Socmt9&ZkLbudf=iSi7m=F+HMJ_2&0j3nZm|MSH6|q9*M7I4|cm#I%*}'
    'wo{jUuTprg1>O;OOHJ*V;%J_H<lZD|-B^o+wbo7DS8n*ZyKCPDb_ser6lYRwib-Fx6J$SgFfurPcTDTE;oki1^J{3b(DS!s>&PCf'
    '6EwAZ?XlL;7R58xAZqA+{dS*=6q-4z49EwKmzC}L*F5rXe~vh2IRBJ4(z;*Q`A6q9#d(eCTC`W_y@@UDfdcWU;b4~Z*#{>ze9nVD'
    'Un|_bm6l`|66ibChj!j}r={OPpCZb9*74XalzpvBk<nnSd5yX~*(N$m4$f>FqgId4BRk<5eR|e_a7}-@qchopKh$f~C9j#w^@QHw'
    'oO_Yn*F+DF_67W;P$Bq6nLz~jhcXJ<SI+;xwT_bpn(yM*FZ%f?2BiS^^lTXOd!ktO)2$xT&*dHY_oFwkreCVXh&8^|@N)H+bWT}s'
    '!)N_QiigOL8;)N2gg#9G%!oc;$j;=ff2U<|<);qS8QiT$Xhr!>hyJ5Se>)0a{n&p)176%;wFgQdPJ2ywXb|32G4h*~VoB(iGDoWy'
    '323)Ls}`E-tl35O09?@U1;}F);0=6^r_QgMSY(e^Ls~zd){)|^x6k#tPxOj+A>YjXTFUhkXqGvFWRBvHxp3LW3>HlZg!?t#bm*P3'
    '7MiH+h-=r?c}Mm~^j!A0>xS~m{Q=a6=zoqkb-a!D-L^+JBNyqpqPtfPX!w<=s?e86Gt(mgPk9=L-HzgZimee#b*<5hm(gq|KaJ~$'
    '({zaV<r&)1<fDdzWN7_5sE4P;p!;m=XPpi(X}K81!|q^J&pH@%tJ~`N5)HaLdLO52Jn?7o)(3k4Z6?;!vcL+l4c_hd%(0^h><-xr'
    'Kz_4|-X%R3G^O(DK>sE&w+dVX_j94momVz}wQkWjO`C3jNtq>U$i?X2->z!(L=KEdz2bLVR~Cl*p8K)DVr+lw*P)vwDE@|>|Kq$O'
    '30R+|NcOTVbh(4ppseE^#gEWrMo+4{(+6OjPIo|4JA&(<GsmKM!1$rb_xVt*#?aDs|Iz$Xtk;zdEk8lFeLHK)>%Kfw&a+zplR~x_'
    'oZ@be+oH3RlieVjAfl;@oUqS3f4p9_AEn7VD`)hF`QTsE^nP0F18dHM8yxtERUPNkJrKfn(rbLD*Lu(YVm;};^B-x{;=G2?{{5(}'
    '`@dUn;2Rrj3k`BXv2IRz6EyqQKw$IKGM%e8I~7wNb0Yh<_(JyAMZQ9D-gMAGW9SkOEskdb!|RURq1PvPT~DkR@Latfg(!#mVLTm*'
    '=g<1#2<@U<%4@?R#WK8(-D@0(zVy@so~1hhfA>Bwk9XaJeXS#?jBHCsahLU%>J$E-)hDWDKG|C>?Z0TU?=DNq2md3V^AGO(tj7ob'
    ')AlR~SjXxI8uqAv#?W5Q$lq>R6Q1_<)t<Q?`y#B*ZVrxbjcM>R#dmT`Yk2ho_#NPAwiNeJuKAa=?z=Ve{H8lDwH@`(pC@}vnjMhC'
    '!Oo`t-hI4~-?nyZ<wkT~k8kh)&*HU?H4uR7dskNwIqNB~<|D0>l}J@;XAhrO;yrJds-pGmz+ORL?OvmY@;%fh8*8xP++4ijE-D4>'
    'y0`lA4{;Wv+v>87TXDS8HuT>wMq|0_dJX0ieQj6KAt{@KUhVDtj;D#seB0Q^RaB-D3~FtemaO^vZ{LsgwJwkIR*o@&nzg03t?g6V'
    'S{7J%dkyR3)qWd10j8aRCpfci?fZTN#bLnfqBes(bsYN0hpjQ$Wy+b=Sk&T{@xv7N&nRBbwKa2qF?57ZDPE*=al?I3))0brn>C(N'
    '{6#U#P0Uy&c_Va(e)}1is5D^xGxS|YMP2SvW<H_)zGplLG~BJb`mkN>y8(UOZTmQT>WIq+`~KJc4fZACbo!k?vFEiyOjJyu>#S`('
    '-vfhpfJWhQ<wNIM9HEUFyykb%0I^W#D^m0VDSx_m3^U_0q&%gmikXUM8}dVUz774~(_L*@o5!-aukFjGaZZJ{6!vggVb8LLXzCiA'
    'O0nTSl8ru2T88Ci-B!gt`oWKJQurk>cx~awDSbU+h=XxQ4n1d`fsIbkbtCTM8a$DNHmq{YWK`t;X5ETw|0yt<e~ihDO+EZ$UFD-a'
    'egaMpcot|v3dfvV#0815n{usVXe!T^I^NEka@NP?|5DxOqdk@0AJl=MiJ4HY3x9uPKlcy%him=lzqo!GSgX)y+4S1jVCL}l(5AFg'
    '%1`vNa(4mw4c64&+t>B|vw8sZ1^a%ZwS{*2HUB3Y`p)i_4z1bFU?C~i@ejcFMsWzO^D>VDc`7JBxaI->(Y!@3p@FW^|4qoBK!aR>'
    '1q+Nl(2}o9x-aPLu$Fdv_m}G|Z}kv5-*0siJwbf-=@t{X1`F!VhVt83FWPV*DX(S?$<>!?!ExO!-6z?>UvK|fT<EMZ(MNd{<+@Sc'
    '94Ox{^K6ev?l|f5t=GD|!S((jZke9VYO@-c^fx@!kMRV5f<yQ{yg|J@&D!o#a!pwb${Ot3*63@!WPenW-<h}F`fC**gH}S@omNop'
    'z^WX!)_Pl&ZPdyweLY@r2p{U^mAIaN)TI*2+l#mQIqXAK;2cpr3w412&$j@6&eYTO=3O6r9hM2L_bF<-ZCTmaC(MT+T5I>UdO6a4'
    'L8Xws9-OcA91HTJU<1nAGTAoeDQj(K+r;g%EhGARy!O%mi|77^eBHnuTK=#m-}s8#5}f}cf0<Mg)4h!EW9@8Ox4Ee?fibU5*=|{5'
    'u75N(`erGx9Kcy6I4@*l!^+BgtZ-yzcAzhtMet`H`ZIJdz*n2O7EIqB7$@mDUFxbc@)2k(N3VW5lzLquH|*y&-uhjw!+jMSGZi?i'
    'NoMdI<Bgd&+F{Niq%{%OK2r6PgtdkIP;+0b&QjoL<3^6?%y=uEUDtiPfL7VHzSF#H*ZXdQiQLs5eQU0dD#T%Tdz)gjIK4yfumQHa'
    'l=QRWuCcecmvs~ucl!fydPT<eM>eQCELzb)A2*G}rKp#hp64vd4^1P?DP*u8%A84xtH3;jdfxt=%E~@r5202OA+|@%+JY7RFbdi#'
    'lKQZNa>B|xjFQeV%;eSMMGWQRfa2)|*;ZQbf}Y39XfKIj_wc29xS+oFg*CF}<W>z&;lO(QqMyezg*w+EU+v2R6W@|z(RF($%Kc#n'
    ')_^5rf)D76#9(rqIrRIjyDj%+5I4|46~`EM1p34Dp2)7B|3`IzE~k71u??N`ZM+8~gRN(Ki|m>WKfPV*isFinVkn!wzSRT&#P7ZJ'
    'C*S!S5p*r(L+A(Wipt)>Uf|uJ{saxKppoiMbKS6|ugK4C{>%2D$@KwRfY3f;|0a=t?5z{<E|kX=OTFCD{T&Os@A$tI2h0P^)f|fX'
    'UedXUck@;tFWD_v8ykAj@`mDsZA!5;eck<0oWNMq%Gyp}`<`bVqdrhe=vyKtJCX17{3aVM>AZ&@`z*oqdjHijGV>V+I^)0@<2=B>'
    'Lf5Q2uA#lvSjF-h9~fL@1SZjVkNG%gmzJJyaHjP07dk%%XLQA*CXLPbQ;x5}AlP=hpLIE&K6ay@oAS77%L44H@-f!Csya>{Mf<b1'
    'NAt%xDjT*zJIX3AyFOo-dC)<(v5vrCWBv-~ZAZ_UOl!&`>h2=+c?|6^%(Z|mY>n8dW(_y!yyeiCr}Nv!tc})XYl?SKw};MV6oR$F'
    '2J<NN4T1f25O;xv2ECcPs}{1)zu#-ISx2lr=0f|P=ljo{t@`WJIX+E2>w@2f9-qN;p>Kd0H`Y!CKj#s36g<b0&UMVV+Yag&{P|b^'
    'Hgn~L86Ie_vX;EjJ7h&4*Jz5<dFgaO_lLP4gJYrC$HBj=$mJP;j<x6F@8?iq+qA{_oM}MuJjeHJU-G!Ij_9R>VP}nV)>x-iqk6?1'
    'T9*p;Pv)52b9lW>ooMdRdtzJ*Gk<z>;EhcG@eFO+iAKE=eH&|=Y0M#Fc2gWDWdEEt#=c@D8D}Uax8zT9C(bE$+TQDUlsw84<@zno'
    'j+x`IaJIorLhr(!0dHwoH{nmpk@qO`pPj?WZAFBiLlx#{WjE=gINfWCy{a?j$n=EnOHw{rK0;vw_^`M86+Dk)9qHWeGKw4NjFYeC'
    'xk&V0cYzaY%0G<?OT|h{KKYRg6bWX?V^ut&GnW5c#b>ew-ZkHxFy2^3z&66>(>qL4jhK||k6I?!i)%24^8P|T)=|E;gvtQrX<V<m'
    'aWwn!hJ5cOZVoewNiKA@?|Y5Wj?VOj{DOnoIOpx>8EY#xR=%n@o-9_CgWO|_IV^fFYs_;89y1Z{=v?G+l~G<`W#|z{Jab6)&p{v4'
    'P3XQ7*5qxvfHhnx4@I5T^zJh9f%N%YzvVr<bzQ{h4tmtn0T|0DZgtednEVaxw*z!uDIZvpofHc5!3k>{()0PyDRs6<1soP)qOPIm'
    '$^|pnJdY_3&|rv;htNERowKl?3uqs&YG;s|8B{uN7R8a|gFHFLd^-F|TxTuW+%vt4G&P#Q>74w#t3IJWclWt^82LlFL|!v{kiUMe'
    'pHC^{iXTVx^`|dj4DHXW6L3AzGnk?!v|*i@>FXOkTOazQPCviNbEpB<6vQ14$1hMb0%Kz*Hm2X0tbi+IoT=iuSF$f7%6n!DX!Cj!'
    '`ky<*39&k3Rsr!R`kk0XPJIV+!Y(s8W>t(izBOj#1E1&Qa7M|eW|vTRnGrE#jmRyS9fOMNBwq*BVvIh7Q$38yZjv8~(GP<LFXkpC'
    'Sb0S)Y5#PCiEr)Z+S$>$+Oo!aW!(dlBpivkG-z>Bj&)AS$9He<`;f#GZ)D7DY2G*a{02I>iTnD#Ddx^F)7ZVeZzyvKiVG{?s4l3_'
    'Qatd)@sMwU9TPMe$AvyaueM{HA)RH|ps6Rx$0~~35T`*G*m}a8?Tq|)PWFA)h)Z5ClX)Y~u+b^@BCr}huIX(18Vu&FZ`dvauUb>Q'
    'IqaYz?#+jt1w3BX<Gi3*zN*y#z1%r!c04C!jZ$d7H)3b%JLi`2ZHxSFnz7zxmo6M@;HpRTr&pgV#?#HeP<%UikYB%4&nGdk>MzxB'
    'G#OaGP`o=z1{V4!qv=pSf381ae}4YlEKb=_4!_jH)BHhx`qK2;%TP+$0|(79L%?<8Q1&cWsHeOXeq(j4nN7Bq))#o?6XpU^j%VWZ'
    'ieJOL1o{7T-PrkNzbrP5Ey<^2USkWEsJpP-ttyupiWg)@1H(`}hytlGO9uP1tX?AW@d~r|3F|e-Q5?v2p&Z)pnBhh)CWAR<VSP!l'
    'p*VRw-+IQ3bjRl#^S!`b_`qN}w9Y)keVWzshWznq?U&p6o_neJe4mYIuSl}XBiZvq-1+5hS}SPWGmiwttG6*`;yuJ}9r*y8-d6@6'
    'CMZX1*Oi@2nyy`WCGBaap!^OwBm8nev1IDG5}MGA^9a?spxm;<%qwDhV0fl3=KY-lwHTl4#qtK&$hC{w7WYW<aGz05Z_BV1h2&a)'
    'SKPVf&aWKkS$`W=ivgYYwOc(5CXRd<>MV+fmP`2%_6_4O-3K}OO#3Jp%GGC6r{R5+Jjl;q$ey8J_C<dhO$Qd+v-Ja*I~S+*z+QdX'
    '-;Fi{`{ytFp|OAa$5An`z@s^c9Qk$FRFspIJVT#1<&0-SgL1pvb8S0c?w8S~w&k*oBZ`H$i~S+G3(6h6S7754ju*5HV(@SL)}CcC'
    'sC>u|O(@?EJxMl4MN*aZuz4Pk&zZT+aIkU8yW##E-3@K&?w<#1r(6wN$Lkds3TGfQ%r*p=mqz_)Coxw=F_9!c+RwS^2XFzl@yDN2'
    'hFlhoE8DQSYbjq`U$vVt>%APvCZxaHyy6sq^P%hD_sI@SO}vEbJ=*;D(qZn^x9jlrmpjaxWLN$P@K{Xj>)*ZoyjWJyV5UfkuJPUP'
    'M;q|ey}v&#F&Dv~M{$`^tiXNI{jnBv|J+~^qx0YN-(T-f;A?*EoAiH|^ExOquc0RVccG%#^7Z<dG3ozZ-?jMs5Q;C?>x9xrmxkW='
    'hrbg$@+(bNP%h@$lxtn*_m{4OnnAJj5P!e>xhK6?En50_9cub|U4OSchS&9JmXrgQ$GBDAeZNjyXfb1524!f|``cD!XK-6_5JI1M'
    '(0~4SpU2Ndf1m48T=Qyko!9q?`4+nV_t*Wno*&kS-<!POR8|ZB5I1k{+3XjEuMXLrckiK$!s=5yspJ<M92_6kBQ7Yfz&iHxcUb|9'
    '?51Du5AS>MasACYFIwT!34Q(h{{6L`*`L>SeD_`*wu^7i!|Q(C_vZ8QzWa0FLha1R#InDUJck3^HW)uKUj${H4dqJ_=Fq_S8G=t^'
    'S%C4=>HQDmr<J%tA1MuiH+?A<it>8k0Q)*>W;Cpi8O0bBPaVM!m#_wO2My>W;+dpph)XCB07F~?hB&XIwNghg#3emLTvBI8FvKNb'
    'i1WIE^XfkxJjV|Ai8%Jpo`=?h>u!z)UkT=S1nSseq$}`w8+=|UP5iKz)`l7BjMjVxWlzOwarAXrxY`on5kXuyt=xig#PtSz2woqT'
    'X$#u$CtQDu>ubybS*IE0rJH(L%(aE<pRn(y*XOBNVFh!nTc2WU<ea{l@!nqR>tWxom{sTrS)*%xwdWmax&Ba_|DWUUJ=k%?ej@Q|'
    '=aegPrkr7P&9BLy_+P3|<d?e17wrrJ@GxjK2#40!FFK>|<r-WS%leR`7O(~{59OlhZKRbNPz--rRA<DWPYX@4zR#+h?aI_NDCefn'
    'uFuiZu$k|c$m1LJI@d4zI=1WJxg4%pVNQwFaw}_4)HY%t$|b<{qTs7kO7AuHJIqm|)`R=HY<$!z9Q4SV9>*P^jzswhdU>=Du<wwU'
    'cRMrJO3zO@-9p6zJO>;9fW8knpWd#&SL2-WXUb(Lud*+T)*2bCr!)RqA05N&DxN3?VwOhik16nA_1VlBkRAC^A5px2KX31MhPucV'
    'pEz~Q90s^4rgR@M*QErwLYOz_w|H{Q3&~OW5BI&op<LM2LpvGrJa|fRSBiO*MRn+L#Pa9cYIunr#MfIe1yg)ulbteisp^z)o_59e'
    'fWrW_J;8AYdZICUqOcFzO2NA`)z<SDbw+Q!qcd`uQG5<ApjmYY(pu=HFE5k*tG(lXtIvIh?#kPQ*$vcnTE;$ey$Ss(Yc@Bv8-qV`'
    'fn_4UOrJsfY5-j9l=}l+%GYzcD_;}vHt0n;8x`j%>iP7Zk!P(T&OMaw7cj^UQFmC3@;(p!KhYmkXVmUy$iddVUG{yEFDQnY?8Q5t'
    '3!bq@T{UvZhN7+*ajw|4bRSRP8bSYg&Rk4FN7~?9Id7}F(*$c>OUkVd=^VUPsLS>I7-XA@r~+fDXtCbN2bPqtta`gjan04PY2J^t'
    'N6ZWay?fdZJ;xpJuw)y~ly897<YRpr__4?b-q>nQUeA01@B8lHdu!(^?(?P+_nEFS2jGinL;f@SC(kRLGuk`g)Y@M00q^VQ;Kqt;'
    'd8RxgNpbG>!n;#t8?@bSt7CA>k&h^od2L}f0drEt!ejgaY{1ytpA%Wdn3-%TZxWOvpB4tQmM{2v4%xQ@FkKYYmB6Tuc75OEf88$>'
    '#*e0y_nx50<Ivgx53}g|7nC31y!Pr`%zJoR*HCq_QOjZFExOkM@aJo?H{e%VV0Mh+8QA*;6seTLvuV0t;1}=dT_v>t6PL1!yAS+w'
    'uz{TuF{hbi?jDEy0QzvS^XXfBPyUP6mDz43{5o<Z^gRm4=Q#oJ<x$M=!{0|-idjFL{TzxRbDn9q<_U2C6-Ec_^^J_cS4OeUB_sbH'
    'pl(He7IlnkelraP_kZxNCzxFrNX9<_H;4K$_}x}Kn{K18hPn*-T00>>kfO#(ap%-lwBBLtt*-Z5Js!mXbNQA>?{hpuFB149y|_#U'
    '7UmLp-hk}e$;BL81ziQ}+bwWl<fErhh@x|qs>h={uwU~Zo@+C8x6_2};i1PHV4e?(EOs#ofuoOmJi<9etrGYL!8k_Pb<800T!JRs'
    'O<xb!>q9|nM7}!*7nEpt9_o_SG3KELs|Iz74%nz|ro~`}SxY)6c^#(<l`&7Gpm#|APzyR=sj1Bsv{rO(Gt9-I=7rfSI@iG5+ey$^'
    'ySKgsZ~`6A1qsyf>H3Qw_a*3kzA!HnYMXR^p16)xWB!xp+F$!1<P&f`vV>;7Yf;D16n6T}KE2laok|1&;$0VYO9wp#X?PFC%<Q`k'
    'H4hK`T@LdsitE4Muj$!PyPH&C^A^WdW2Y;QqwSndDA{3fEQn?W9wN$TT$Qx~{ESy+5LKpTKH>m1w%r0fA@CqjthU_8kZT!ay1QR6'
    '2ZStuorpq#x>LIh<0zwdm1#Lhum%mTYvy)%PMhoOZ}S&WD_t_LMVF*J*CRPDocQ#;$|(1cPkmhPAm5<1(|CT@<L5robI%f5hrsK|'
    'k7mb^*P%O3Jj8*H;dA|e{@?#6N>`JAiE;Yy(^u{M^p7%52R|=1fm$rp-(j3?oWa}Q1diW1cgnpuspCvk6ggYr{-lBgEpiHdM@}cb'
    'M<;o5PG>Jt^Tzqy`2#hN+{6h!sU>B(=kUe3ySNYMFmh-MJf5SmQzm52C$w%CPh|1LIbOWBn|@Niq`uS5_v)v_|3#&xGu--?$`;i`'
    '2ZfUl-1sJVan=uRmW6lDhO(tuxOFz)z$pE*+RUqM5IzYya`%JK%I?PQ{UDlH@}*Mu(OQ<zRg*!4=ogp5k{kK;=ss_wi*^6C`Zb^U'
    '^5@R|q$asV>A^Ud9MtYu*>ZB*Jp|evi3J6=dXkH^(n?PYI?nZ1O@Zq`(brWQi)`=cugAE~9$W9>9N(z!n^rf;&*wv}zezf(-_G7I'
    '_tR<jH1&QuPw&+)Q$41z!g^MEm`*R*IrZJyY}TFAI((YlonLA{qHopBv;Q@i|Kf}+|Lb}FY>j;XUd=D(PYeI&+5D&O)7Jm_GXHe`'
    'r0boWkF!tT{GBzwMbG1*n-A3|-v^&chQ7~z8d=sut+O<7tZ%ixO=lfA{h(rHIdwBj?}Yu6-y~_{jJvuE(ogd9um00z5j(eIr04g}'
    'm&hMy3+)V5JsdA?mQL3=dA3@*n<hMFceZ<ICTW(rUL3?t_Go+iAW_*bwl@uCnU`64uw37H&Qszq*PD=zLWr-||1u>)cfIys)HbZ>'
    'dlzZOEDx*fYsf6rl73HaBKqAx-7h_Nwsz0-XwL1-cb$yv)xsk?0|sf|u_!jYy$hDk!aK`2bgVLPKx%KL!Hbyr^#9&Vv!&0d@%usL'
    'WOV&Jd};2(vz5@#R^bcX%h^gPjE#dzEXl_P^mlZhPyPMU>%`~se`vXMTmH{wfj%fpZUg5@P^vTqeL%33GIXEvi93^#yZ%ZcrZm^F'
    'Qu?}dDa{4-WpibAH~{gU<nUfW2MeEjWCi$pFfouP#3a{5ozdOrE;2pd%wz~M^^8Reka3U)3BW|`_Kd_yDBCr%oDhgAAO+~FVRTR%'
    '_0Xmv7&Wrvf+8DC=jHw6UN{s@sUI$snVfoNLyp8}oC%c7Xq|&45R-eX75&OEeFIPB`c?wQ$V7LDUU!~@dj*oUi!x^Clm^|}GrpRr'
    '{f+U}ROXoxFL-4hsg~$q?F^$VEIM~GBTOcQVB7`679yGEP^7MPiCAl)>ybVsbli%JK5xRFDGuh1>7tWCLsvhYHV#D~Kyh1$A_K}Q'
    'c8Lqd8d1=-?q}NeCVMb~h!z={%Uwg(l25^u6Y7foUCh9EifIE(=dDobr`MhM)^@F4yjX)d6cK`995NB68hDIaIiQ1+8V1UatPoEI'
    'Bx`M$$$_%=_kz|>oG?-2so^*rSoHp0coJ|1rZd$ohShRM5iac?iU=!IG8SMM=(W*hatEg8M(|`bMNlhfh@#@Ys!9)xpAi@+hnBd*'
    '#0Ra}3|m@>#TWWL_JEZF1Lh8s4)ptU9cCmAD1&Lqd!8uzr)W$-7dxGL@(9gkS7EXi-9!=jb@o@7p*eE$9^`bWFr8}AHHL#L6SSGs'
    '?2^q78KC+4!sovOqhJTbAEPTgWi(uKW}ta!^QcTqg^mE8>&)4{-*?n}){Oz{Fc|zO8pEFB$-zT9Gnp%p7MGl|Z#uWBkL)h6=)6^&'
    '0sH1YW|)u(8-Z>TSL;l~3T9nqAK$Gie(#tZOT)c@upLFR=J^F8-ir4wCQ13<DU-;jU{<f0QMG5l#rZ%L01P$gvWX+zH?oTL3X`dU'
    'b(+?0LXqtZjH7fe#_s+a;a#tf%t-W;tbBb;zUwJE&jIaU{gTr6XL{aI<XJjlGzvx4V2ac73|*QDBZ{!@9rR^VGJTi^11cw@y%-sW'
    'sw$%EAJ;rdEXSr>XaTv7jxZ`dKr=j{%a}1kytRe)>O`p#U85m;hU`RpX0rOyKSzL$GMHL7m^e1<yOdd?(uMWtfF?kP@sff)4OIiO'
    'M`RDX6rD(A-MfqkL6(d64n|gFv-0FsP7?L+gPxDGbkphYz%ZTwAsS+0mi7Ty@F{cPZZ@KPFiX&X>AU@**Qks$OW6TzonR@=fk<Cf'
    '4%h)ORW^!!foXu#O!XRb=;T(&Dmu0kv=5Fvi9-92GL}nZDkmu>0BOC83FR4Nm&p%^9E>QmF84{*?V^hAvqzT9P;qK_G78lbR1JX!'
    'xy0&)&Zx|gc}*EPjc%cheNUOS024S@<bHEL^fK+w!-X<W?4ObE3G>{Zysqbsp!Mj_8#1aq>CanYvbdBotz8H<6GoDCv)p7l89fIO'
    'PZvz~qEnyu_nQMjNbeDu|6Ezh<?0XlMMh6qKu-awL$)xZ&+qMu&(rFtg3&uuBcMnyz3w@f_V0Kf_{PpK)0!}L8f+O{B_dlO=8Q}f'
    '^qG$%Z^(a#3fy9-o=47*!UE&V5|8b7?2x}~Gu3y7u9XA2k2$`&2XxyDhr(8LDmNb(ik;U?$}{H^%yTF5T@meR!&sraU`gjUp>v)?'
    'i?@~zCf_k3Lg$+@XT$;I+v<){6_M95QYzH=s(?UY=A?*16^|>vw9o&~F%TOqtGr?a-U-(v+nW2_d5=?vr}}|>z-Q8aAfJxu7@)9d'
    '53Rv!DDWI${qwCB9SKpB4P%58>^@iFc4nF$Ohu?9blTM~biS>7`d!_3s8Nw(J4yF3qxdX$0#ukV8DW7b5s0~T&QrXCE7-2?z!;qe'
    'ewRlogKu1CmD~kjJJ1!7rqIjY#(`)BeV=IA(iz?+!NCI)-m1Z#N3}L~)+}-=taTHon6v;gW#NOl#%jq&1XFY%D|&Bahu{}|u5fkQ'
    'XWg(4jBYqLW0!s&k$p3h#+WXmd-lP+l%dmkgGyIn5T<#+3=VSOFk_?y<9Ok6B@nvpw7y{7Q<X>8f^HW*W7pEN)4T2Dm0=Bx1AfKb'
    'Dt!I`(@d+1wZ{t}M<)E-sIrJc1oD{Is1z9lIT)8PQ9^!fWY`q#WK+K+3uUkSPW5=hlLC0&Do<HqK;-mu#D^)_$w5x<Bnm{aVB{Q-'
    'Z}QYnOCRYy(Eb3T!J_?LdAJ9%m0%i85kn<FZz%<I<`E1_4w#CW0St;Mh}kSuK+@RnfcPCP>aG#SKMq7+34z@PLp~#5f#@@FKkc6~'
    '4+8-vXs#H~5Z`H3jF_2&(jvK|_#sQ7z~E6#tDRKPIi`1;UMne>jL6xa00~+~SSLnvG?pS8+k(Aq1}1&3wu&Q|-eP?|VOlaV`=dpM'
    '$Y{8ltL9+l0@87eGio|0FBE?OQO1m*5-dV~U={1iX1l*3J3way)01F|&!<3ufK`tCk?>&~vJ<UIlc9=6z9_8S$RK1p*qs~<77kC8'
    '%5?78(Nt$(%iaQwlLp-wdgDv4Biq&iRoC`aY3PZ0vp|mXrUdgMm{f}_jKQ*&E&`q$Nj8nW-89Q&Ss4bx2!4?fz!q!`D)R}YWaQ^5'
    '525pralT*`sGd?>dRlOdaNXZsfxjo);vsgS{azr>ahoj7%{26Jj>%No^YnSBHXgC=Gwnv?+ZsAsTPUSW$Y;~{Ku{&~y&M3QlkerZ'
    '_is-?pf7lm>QF2LppT_D_vm_c24sn0QY5>Be2hCZiWQ5n&v0JBgjW2)zIxkFQ0f5N7ba;OQFvOUQ|x#1{&~OC&$qAp{SWO`2mg%D'
    'cd~|}2%X<m?e^#Kkdu8GkiQ#XuTH@<1!mu#X==(-&=&002vgnUKfp*s=j%Ir^tum$3d24;n0=^YTywOcJS?ukC?~iZ0*05!AQcNb'
    'pDp=2<RV?h%+chp8W&wk#D>UU!CIOcwi)52ffxtx_F)!SgJo?MsX-!Mr$14V=Zd=*Sb6WCFXRVuFl)d^O@PRQ-wOo!GN7>q<yFX$'
    'WRU>nSV=`ba~D!vJ*9I5wkW7(ECR#)NAW4y>7_?G^({{^RFaiOM6cBJk?ES1QXG1pMgE`gS66?6E-d>KFh+Nm-k*R`z@wjcutV^f'
    'k$E2a9*jx&zJj6+>^0e~p5dmku<xNjL;EJXWVIcE^>E=I7`d?WOGX(|ym3qCYuEerXz7-TTc34S*-&I+#$FfN>Zm~f$IgdLQ)MUK'
    'JNwAzgKPuEcgeqVK2q{?zKQqlp;i!5yftHm03b6sUL(Jx2IQY+Q*=`U3D&<|h{=1NEVQ;zBLM@ZPw`8H_=V#eGbt+icT0aq@sk}b'
    '!0bkG7RBqBR>k`qlTD<U*m?q^e;i=nmL3#=W?Dh@iP=R{!%RZ<6}qN&bXUdNYh|(uV;~7rsmdAHZI}UhUwRv^A*my#T0BPDchCe*'
    'bNY9`H65TF?}Zg)V#=%KAY%3hp1=med_cKR<dNM)J&bJXD5U#@orW?4`TaECm(YDhe3Y&m>vr|d9|ZnKfA8VFevJEO9_QV(ZNSiL'
    'CX14QKF^27y%JC41I8)VqUpwgYi-dzm{s<D&up2mnORn#BlpptV1i$jh{Y-1Ilv}B6^&vzbl~I&arvZ?0&INfT7~Z?P{<YokxKce'
    '2%&I6XP^EqO`X!C_^E)xMcP0ehx|Pdx$IA{?|8oz^!?46_T}8~2C%D?Gu;TDkSi0hKlgP*X5xbFyWn2I7U^qrgai;q=-{1vbm*(a'
    'iO+*t7GT9*K}}^qc7g6;wudIT05c}+Bj+JtAE10#!A_(`>55`Nsa!@haD6NlL08{u2l)y!6jF4_46~^=dD0)OtG+T?{-0Y{?eH4H'
    'mSzKcI&Ox?*@N}@wpkpPgRX;pOa}+wZl2o}n2G;`emv>@c=WIPam0_W9l9l}-ym+3y}d^MDn@g9-z#X*BS(ad@EB>Ld)Ag@;o8V6'
    'BK%w+Phh=a!>pK7eioyiRWA|8TBwVdPADd3B*peXy<jQ}d5j&A4cK}C<uH_U_7io;{mBP{2|=b=1ywLR;b{_mKy4BeE)gp`X(+5o'
    'I<H+oYtn)lM<@sTJtDixQw&fjH1WRmKHhKN$NRMQ7V6>Ti<&v-(E_;+lq9gmecoPO<4W!F1TkVppy5&b2D35hS=f)*f3JB`zfZe_'
    '_7+{!!sjBtiSYYQVCvix>}!e>S9__T0z+{k*-dm<#TNHv;zhfdLWxhuo~R_^?OhUpc^2%a@)mi}<}EJBe;XH+CN5AfkwGL$o`m+l'
    'dk*MZdmheFhx#q~fBZfs-YvuloaeEcRlU6KGsHj0^P+2>HxIf2>@?*s$Z<K3#J*VuJ);0melu(PEzWkPtec!ZWA4KzWjJr_=S{x@'
    'ikIJ=53c#Xu%ejX$1zabNr1FaHqIBt(v-Ks$EpnV*`29BaDJN7dA}f5C4WtMsLlDd-?%+u!cM^?7t~b>G`+8v*h@{y47YNS>WpGJ'
    'Ole!%toIUq6ZCbykF!u?LY+7w{~bUjGjzHg&`XA?J!YjcpU-m_fGrdV2OyS!$ny*%GX1*?HWk#}7=hsFmmFwF{2V=voNL7g2k}Z4'
    '*yOiMOyJGdlqb>JIV)BWI-skbh``eHoOB&aQI0qgo;<}35R;`7)7~ii`V>7+jtMogTey!XS8@&i%#1RWhohdn0)z8wug1FF@cxbS'
    '4J!^(e8B5>;0b?bsDG{7b&2P6=mp{Y_0y5!b^}C|hdQ%^eDVoMjlZ$JTtEJ}zKH){*B2B2utCkThA*%^zHi=-52I{geYWcbkT8qS'
    '-|YwQx*r<pEq2|f&-(e4?W|8gKKcU-`QIPa2`tnxfigiIh4SHZRtd^yB~(8~bcVsO7WMujpMnuVEy0M`(!0U=&EdP4If3j~(ARx3'
    'dVbV>ru<$QIZOEjn3lU4SnU(f8c%yB)|FZe+yDxtF0G5@4tY|=Ai~pO$^Ez>uvWurnTA8lp*SFQ9;~~e?iCN{%nOR|DK02hJrn<O'
    'aG3N={8uFg+6!^wG=^2d<-M_l-DGuD^Lgj@%$(?ZBG-0IZI^N!mF<AcAs?8Koet1LAe#?HWK0oZvIr<mI@es^&1cmaQ(;(ZoPSLE'
    'f!Uqa4+W+m>3x&GC?=*q8lXM^RE!6^MsWk}T})I4n8dvHH5}(%{h#|8T{h(@MKGsZ+ygLm{H_5?k?!#x>Xcy8_e}p+%uF8vp9R#{'
    'Y{t_^GMgFy0M>Q<TtF!gbst7M*5ZC{Chs!-IV&ZK%gof(!PuVk*Twa4-}gZ1{lR@xo>~?W`Bb`g5(XWZ-DqDyJ=jVquf=*MW}^5^'
    'v9CN*-pW%@K)|v(Cwd_qlQEldiarq8jRFGLvF_+OtzU=EaNrwd*xAaQ%j<n)D-+j23*Pj1Dn@$F5Zj48>en{vTldKG$)2tG=jfl1'
    'A9VaKO{)w&jI*il3+_+2uS$DR3+__iv)CU~KG63g=)M^BDO)fA&#v!lXg%NRhvQ@*zm6&H^#*JQPt&1QjjLxcR+#mtb$9g;Oosch'
    'UYw$#Sb-_gAh4E*OFrC(A7FydMy;!G>E9{e;roDM$M5W$qoW_jjM!&IQ}MQc@biK7&DO&<9@x(HT+#ItI=3m}NRR7`^m#sfh2T8W'
    'W9C1cduAmAlI-O3`#Yl-zva3F*<a3wdIf72c!Y|PTr<RH0iTC6BeYS&V`Z1>VNB}_CJd-ZqlSd%ni(V(*8`Jq*s;QaJCGA77>K{O'
    'PC$&Fp!OA19laOIgMHLEG0`GUrYF-;^hI$G>WkGG$h_7wbqT|e7@(g0@!X+*LU9!D50~pWAI_ga%KIWR&kMVNdj^A}LR`*&hl%R9'
    'b0)mNvw*fAB{iQb_(h62vk|5oY3-tkFIcS=F{!5+{e7O+)&=!2qgEPYV*Z5K&)av&(&tHfign~IPrYgzJ{SnzfA{|2k1nZUJLfup'
    '_j;e=-F;$WwoA<ZRu}U*XWBm$(^k$O+Ls@mGu4@MrQXg{Zx@4<Z8xq@*BVHH`jkKDR<wUcKF0;*zkyJGXV(JmKU+XsUXb?$tf=wa'
    '{?2nI{kcltp6}qiw;w;S7tZUt8a4-tG1UcA6>~F9aKQvJUGrC4J3OH<CjUPj%Ioue`=TFCvq9<n{`<;)=Y6qXpwD$KKkx%`&T6yx'
    'nOQ%??LO`MiMF;=tUuXQOlZ@(@b$r5KXEPeU{Uu7W<3)+YCO}rTLY~f_+$_G`tr%+{vhKifGa@1Ji??n>Z0`h6Q-^ap9H9znmi~)'
    '4DEAI-SmlrfEhzgpO5}M+{?Z{3tWWsu6CTBuleoz{QkPoe!HGy)VYv@bRX>~Y*Kf9->3!AzxVr%eb&LbGKkQ>rL2IVG38+ebF&Z0'
    '4mr#SGDBSypR2R}ee=}E$*1>C@8KBG&v}Y~{=R467$e8?jooc24}pEeBnmwT$M6^Qd9c4?X0D`In|_9Kwgk$xzb;g0=-*j|0G}7I'
    'JvjuddT*w_Ph>M4&Wo!!NMT1PZ}$5-4|?U4{}hRdfB5>okNAgi7=f7p!u#&>X}?~=6DQy!QqE`2jP{>th5b$IYK<q1j{*}Y@F$K@'
    '=;etliy7s8*V;~WwwqOU@Q=RF-}+}0U%mO~*Z2Fo{<(I*Xn{BoxC;%N<oXgUpqKuBDBdDlLGg0HtSqRJb!(nRLY=T;HCK)sJ=Z!;'
    'Ouu|x8ivEjFuS5IA;3OB&+wvQ!`F-smjyF-pxy?&LnT>-%x9*JXV|$r`}dgd`^n!swHQVJCC2;MOlS=zl+$Dt#bGt&L9||zro2uZ'
    'd#J}zEV@n2#EWI>cU`_Q^&G^7V9ZLu@Q(>B4>-6A3cZ%TvZuvhvrv}ycv6GbX)m^gsuIczkk5nhqUAnzh5mk=!mk4X52e|=+TJer'
    'hvbeY48$PR%QV*VTyVWzJ~57EFMhVGhhsqdfYuq$w;ET7pXBqnUR-9wj<I!Q*A?s?z2{HE`gt@TSig?-L+d}t)#rLLm=D3MxS+f<'
    'ZVWESOz#*xi9r5|T<d*&aoxuOpLfJHS}{JT_ZJ+CnfRbf66{APN59#t4EYEq6qb~)f{_{1<w1iwdK@LD*PkW<`ocDSZ|s@xcA8>u'
    '+MC$B7J5UtPvEl>)L_vwfWk$fq>5=jMu?-JSVDdUIE!%K?IbgH3GUTRLTg)K5@T<1oE>@`s~3#VV;m6s!@{ugbrGHazRpT<6vYXl'
    'c`o>u(R;f*W5#4mhq1yq*;%oh7(Ye!D1)CvuNv!cPv;6a%MtCvzQ6Sk<%t>$Z=I&|(Z36E2`h_nKJ;GiX9mj(2Dr!%EKI2atCOzO'
    'OG4)yDy2yrFzc0PrdpTW3kC~T`aio*#{X=g#L+8m>@xMjjH?@E@BUZ!#S?!O7-i&kRaKO)$Q^xe)=4{C^8d#L`yD7<fei>aH>kLP'
    '^~M65;|aYmQFWBpQheiE7bs$duG|GsTB(E#n3Y0&8|Y^!ojut4`8cI>{6!B3%wB=KwSu32Jb{Uxes2)&m>Kor4LkpfdLX|-c9`sg'
    '`yi*E%_Px%#QllxM4x+^aNN#)BlKP|{loiyg4%CQ`3NRcDW{8kOx?PL*9Z*;L$NQ#zj;2zihFP(N8aKEu<tf{a%yEJoKXKoe+B!I'
    'zBhUCzwvp2nY00Gbi8%;A_6m!8(OrlN~rD_d*CxRgIUl#W=ur>)TK~(L!Ba|xN=JC1jUzGB~M`=2SQCTW7R1OOzB`cPIB$0Q6n|j'
    '97SU(Fw&xqoSXPo(fW@<#vk*0KH)vYT-)b7TBq89ik}7^MQHdGidRGW93AH=y@!pdcdg;)y*@wf@ssqG_7vj>Fp-pDzr!v8_grw^'
    'Ve0W)w?*z11J_<;YRL@lWS@3ZgQHKlpQG(!wvU0WWnX+{xAzThaR<Ecw6TFVfhr}PvkcR|8mu<xGw`&g4~88%!T=Ba4DUNA2KM+D'
    'pX<fsuL8soXVlu&*Xq!URvb$mpG4H{N?p?To%OYj+q8|nvOb*Bs2i2FP2V5bkA<{fFp<VM%f`yr%wQwXS5L@?qwWG0ojd_vwdu(A'
    'm541;dhgqXj=_#}T<8pw{>(H*@8Q~)-uZ?-W{Wy5#a%Pc;4+_3f1h|@rK;#Y<kMHW&uJ@0rM6Ggs5_Q5rd$sl=VkBv@7xn)c3oDc'
    '^*COZO~j1t)+k~O2-MLG&coNjumWnfCxZnmH3?=KLtSvn%tcm?{*ve!);ylbLp`l~dS!CdXJAXl<exOAVbLo_57~!u08jE-I&fv4'
    '=n8mdeWwrYmFW`7FPO3g1GMawJ!4h_ljyY~{^PzKCY^m=HyKO}-i~J?T*^mregx;yJUx5FRO=Ma(TMR1ikUyCcTPFp2i6j-h9aHu'
    '@5?rH(WiP}2L*nEl`C4eQAbutGyS>`xJ%TR4Ss`Fml=<XeiZKuusmRL6-*FK43?;TK|Vh*%Au4$^!vW1>ua$Sjfxmgu$Spp*<<ff'
    'c%>?n9(VcoahvrE6gO|&wgW30*vq!L>Tb|4D8ur!c|7Fz&EdFe<Fo+AYJW)Y_Hnz}zog|pKCK_ibQ6@Al1<m{p@^Z@Lwj-7S|>V7'
    '8t-tU%lm07Pg{L(FlC(i#-}Z-G2?-R!+s_W8DGrxPR@6XQj5W*quw*;_y+q<vZ~0G>&Q6ga?Ln)pRxGqNBd=PBCeTY&u8!IC4qWZ'
    '2dO!SyO<s*D`1$s_g&p)Qp;-{X1(V6q1@$+OSJNw{Bp<)^T24aY9r<eP<N&8P2KSo7tgrL?{M*^{zLcAHLxS%h6#GHrk*sLn)-Bx'
    'Gb?;n(nNd<oW~YQBL(;AI-ON6E9Y!jVT9uZyl1j^%n*yb@&c^E`+5U#0v_tuKKu>Wm!C{Niz#1uqF9{H1J6r<os3mqQ>_r2UQnO='
    'fxo!--qss<@ZZ*NUh6_{`EBC=puWb+i`{X`^_6RX0640bgluk6a2{#$#YrP(Mqx#!cl~?+JNGetK%CP>*ZksL{_*S3D8fG2)$=i+'
    'yzg_hxKO@aL!rmyA;W>#bzeVM52pb2(<%lVcD|}yC?yy4eUb!}%V{w3$>Yl43wWl=D8iv1#W9CQ?uR@k+W*_Q8N_=O4_fV#`|cg%'
    'Gjq301sJe-UPnb4#YQ2f$;p0$L1RwWav6`=-LMiNvj$`uOx!X3-XyXLFt5k0WXAOfjO&$soJVx_>ryXT$;|OHW{xk9cfakYV{Qk%'
    'Z1SCq=a`wvWWo36e~+IAE&?-vw1%uwzmLJf#{ERZ(qM<6_?v5Gv}Z=N-U7JOSNs5Q(LLTS1in-w{#$x+Wd}LgXR?Fdswugi<bo-Y'
    '>>zL}b1)iKFQ<^6lb*1hwATHW;|96g*2@#wwvnXxVBT6cTaFv#XlwkzKW%sB1H}3b^77%B^Sb&BhVIC(kt+a0-Wd$K>R3hC=llc{'
    '?2M5B4jGDT7oGzFRv7k)<1e>}(1*s<z7p#>=h*D`P~QPI<Yd%d#OUt-XZzHDI7D~NVHXU$#h^8FP^CI(%tT~hc&*X%09zs0U{Pa~'
    'i!ar~Af)HHBm3gEa>jL|p%sAXF${$+=sknE3Nsz#`&glF7Ky>8wsyj`z~F)&(Gd)6vD=*xBa09WpDwV{wC;yQ_yToGva_-D_lIaz'
    '1FMVPJmwx{L^1P@K0A@>KsGI7tWma?P>T$by*L)$p-l`UTjS{xaTL^mciG-fipEACJ~4{gP}-?>GxE()fKP^Ck|(>xN|z58hw`|g'
    'dKkFFZhBiSPT|gaxYdgh*gP_=dJHx&Pl!*fmf{hp2DPy^xGdje_M^hoI4y&FW#$*|qeZUEjLlFIpcpMX`OE^uj3}qRuY>*x`gY`p'
    'C}-_$KiTVI^5ed=!aP{C@3ds*c%jKAcp|iRg$BckWf^9k-}Lhe_P_XiR)GIOe~<EPItO_HWs5z<`Q+CrhL(3#xy8u*o&JxUYcR*='
    '0`V@hc8Vj#6JEkfCkHyO*ZAQ-UO)Rw_wmDi%tt>fUO&HbP_Js|AN}ZW?*o0^xBIw<k`M6UbjE>m-Q~@n<6jqK|9U*lc13yCyplcM'
    'hV0Bo{A&SL*CiCG8aK~zR_J}8hd1rj3n-rl4(bo`GOlN2YkD7jUB%cPR%#bVIv=|vveHr?E{itKzt;9HX$=lG3`~#ns*DV_?!+h{'
    '=bVH2P_7ooNXuPJaSm+Vir$OCEyYQ{r+7v!X1fWy9v9>rcWLG3lq1vgFVO=%t$9{bP~0t1+XkyzKVRz5xweWK`qd4qJ>XmxN!6iN'
    '40f?o_+bu{ReLEfS>{kmnrSzW4PNSkI28BdIAw$yHnWBF`0OjjjAvbp8U$)+W;U76q}0qBTcKV?Uro;5&$WxEKr_AxISX=kNqOBk'
    '3OXo|6amixS5P)BfTvoR`g;K^6a78k2j#ijq_4B1{*F9|-Xqw&x6FXWIF@+5X>6k?PkSTu*$=WJFY38I?~9K10~AuaqkuXY;_0B{'
    '{yW9pU=}>4{QS)LhFLDyFvbDS9qdEIs9;v1wXV1}yIX^ezUg)=4_Iw=%FHb6k<TRA*`>A}$_I|?P)1Js&)p|quW?S`7;w$`Ky4|a'
    '&x3E$V5nymLB^2C3$5QVU<_NynC6*F?_8g^(<<(IJKN(9WNPLtSdn|o^=&gxPVeI-0S5r^SQMko7`IE`uM984J=v}!`Tv_G-QT=2'
    '%xaM<MoD#uoB$XFk>^)D-9N<89)`@&1N@d@v~0i>Zw;XK2HO$&sBdKC_vnmbzD!HWa|8|;l(0WhM^ebky4>(TfSog$22e{^$m786'
    'a3sI=1QzGS?J#STCw#WCeo*!i-fY-?qkIDjc+Z3Sg>vi?u|T@mm(He%(}izGiv~D2Iaq*|rk1yqGqg*-SF6oD#3APtwN3PZ7Rq+O'
    '1Q|Ybcfiw4hTYwudK^=p@?}sDFUw&(p|9iY;o#pk+10Lctq8LjsM}?V?IC<JdUxoPA03yKnR0V(GcaJnK6<DF4-_lgO$MsM{2u1U'
    '5W~!%VCMO#7YSy(Ua0ecY`<WoAv)(1^m@5Jg85pD`{uM~W~}HQbX)kJprLnPEx``}9M>g+eMX&;_J2}2+lZ+~m~vztRWc7)iQsum'
    '@g5k8yl~h_FpCM;Mc^<)<Q-fe!K@5wVE33eikKl+7^e5?+)gS>0#7QGVS1m?dv`g0>*zgGywO0hrSuTT(V1nYB=lio-6>;tgbsik'
    'ce^%VW=Yi97h|DB1H4ia%FCu^oYrxpUy5mCbqkYoV}@ive&saRss&@>1T%tKJ|PBA9QaSL?qdewoRZHv=QXRg8@8?hzQ{oyJw{KQ'
    '_Tde#IdeN^w41T&Y=+w1nH4&Q-LC_%tvTY;pstva6?69#m)|14N`2c~G~C}FFY5Dv_MsJ<S?4h`6?&5Pp#q+kd#b6jZYdv$z)L~-'
    '@hKR}=@+9sP`)v|KaVC4^5L_7d}Vk~hVqv$dU#47UK!p$f2lu>7Cmmu384&nNDZsz5_a#miUL1i&YuNfh`lN(EQ>i57mWfGFt)`e'
    '#0*STKuKw}KOjE1-|X#F2DaY(U559+%^<FzD4+Mt@Ch?)`j|!dJw|v1wM^7Y@P7U}BYf+eB+en%1i8Q7pGRgW|Lyy2m?;`HmR+Wy'
    'Bt<cqS0aytns^d7=XO<D%y|9-r412MUXC6;VnS2L?NXQPxBoDMeCwpLk{L5;4uQWVJLt%}VReosL#uK1!ytD`%IOw^d<X`_bF>=T'
    'Yj^)JxO2*fA?3Bv&@jO><N97j#b0Nh|Mg3~c+Wil!c3<9{)SS)=lx_<49l;d_lwhdSZ==TA5KNjOkWJ_uV40`Mt1{Sy)uheJziKZ'
    'TE``OV){C$x)hGr=|nkDQ#%_T6xvDreJnQ3bKCR2Kn-(hYx?=X@H+6{U9Z>UBv_GRQ1ah_p&EAI#EEWk{rQzghH`|d`5aN({oFQU'
    'i+nE~)KtX&`Z?eUIuwFFZ*%=Ud`|y+J(Ik-j=2xT{$?*#|2%vj8Sb~aJ~tFbV!lrH#)PlH1S$IKWmV6N*{{d-duIpcaPZ%BZ@&*F'
    'X?i}WhVXiG{W2D;WU?;>`|rLFnR{SfT(r3h{L*uqU)KkWj7?S0x*YL7wtZX#u25Vj-<3(w()B(1_qM-2eAqxb8@e9(fg^lM&%k}$'
    'f@g|;fBRv5zWbc!vCUb9vFEAMh-nYJu8s@l#a<bVt_vOuD9uuABHrIuhWAgOM?W{~<Hku)sXQ8#uHE$UR--ts+JHg4UkBkLt^zYV'
    '-A|8a=lAyhJv0h&f^Tb;V}0Mhk8Qs{`T6vu<^9lnxNl|zrN4i=zBk@i{re{Sy!{R1IvB&10Ao1j;kHmhp6r=fv}YtI|Ek1!13wpn'
    'jZ}HYzgb=uQVfZ8g_18+io%lK{gUhpc*iUc@5cf2z7h`RHF>^zuQ<Qp?-es=dY%W2AM$(PZ-p0n7TG#=0#o`FbEOXWX0j8Q-=~Q8'
    'Jd13+a{}}G6zr&;MY;3&v{0-deOh`p#p&vV`<mjuJe%$-J8hJi&!=_r&^MiOUPt~=2{5QbaT5&31(+E(P&9MI4)s069UCoye@?Fq'
    '?Y;8yiTxq_oHr(VFsVD(H!23>DwL~|P4iN$R80O;7^Zq&Cv!gqpO2W|Pr{7u9q#9d&r6umy~F!C;{7Dd=-#P>>=@op!i?@67~PLx'
    'j8B-+y#u5B5%)po|Ckv?f@2<*WLM}u^a1yAg#S)Vy;aV*-);Kq&Rc!tt<TceDbOEe_2Gsw)W8k1$~fkum#UL<t_Pt`qj+wMat^Q@'
    '7f_5w%r>RGXzd(W#cJ)x;3yiI^LnN{j1}9C?occ!{y9bi>+TkKT*KIpdKSgi&)^%I%}gKlnCh-goDSGB6BAR;!5klzVjn!$V7-^D'
    'lsChgAnvTK25Nr>hsg6<E%<2?7c-BF8B7KJ-O@1OLkWvn$vsx{w&;vN^^fay#hl`D#2qf}U(8-6+<W7huaobQFRhp9gnM?VF<)^h'
    'Vhm+l%r@p+AHW<CR6osJIdGai?ilNz^z*`~>27^q|86~FoLiXzpNZJl=N#d{bL#6J8@L1uuXaYWI);i7&$$6}9kCiJ&*Or19qTj#'
    'PY~u*!TFQw-jA|k6l&Qq;#1&oC@<w1M$}uNo&-ETX4LNyvm=)UuTjX#S#+iu9|U{?D{F#7Cg)y%&HQ~QiuExUlFz^ttd?M&4QTDR'
    '%m-3AP-ANo!~ci6=?=LnaM*@NjccCY^F+-irr+0jnic<cG2;Bn(v+7_%opdV<w~e7)?8QHfoXl_V}DwguV%g_>8}qSChSM9gZ^mV'
    'gYleZp5}*m;4AKo?w$7O8{R$KiMvnLViyj?oz44O3YYeEFt9SirzereCB~0ryEX2&73c*)dHs@eeEB?B3=jUGeg>`(c@A<g^cask'
    '@6|ws-VzhTnZPRGG1o|VUNxJ)&SP7JnOU?@KW>qaVXjcr594%L3b7Yl8=sqc`8oj(+_30_*AdqQwgp&laLE*AZWuESJS)5f-argR'
    'MsadM@8&7c7E~C?p3~WPCFOkblz{=7m8W8F-Apc-i5D-~(C}VF4(2P(eWv})D&;SXJI$0Bz2kS{x$Wy5EI4Gq*_by6W}v3L=D0R|'
    'V^KzSDW{wx<TL$lj=NFdWl7Tp=h0gCxMq!fFhgEYGyhDBIv<@cb>(}x^0k0Dnd0|t$k;D|{R95RoUX~|VAYs@#f*E-9b=*w6)=_b'
    'Uh9(XD^8e!Un%arVa7ENV%UfaW^O07)1Pz9n22j{_6GH+xeGNoRivuBhu!etTcJ3?_S;Hm9clkUkqtGTY#a7-9f5~)A~Amr>_69('
    'J!V_)`|jE(0DSNV>bzq+uT_%J`2tqfL652~dEOE|mkIZ^;)LEe6xHZF%4k_FnU7*sJNQg5@A=~J_y6waXAXLzl<PvJ7Hs3_W7Sgk'
    'bF7qKqu&KQS9j{~=LXm<@&o4y^H-HK)Pk|j@!o;$iekeb@t^NU!v2{aUy8Xi*v;^5ULE*mR+#WieV3IRgqgEROb_D>JB0b-q~}dS'
    'ojE}5I52f$@Z7PI0&@gVzRJB^Q^(Edv%So$59XK#?4Q*kKwV<#GL9NEpiriUk~Awspx=Y~fzw#g+dN}ua7N5y*zHyt{8&(4mSfBl'
    '3By|?<_(@7b@n*-9jku^)H^A+++USLz;7fu&lVK_g73&EstJernlu>v>0bUdW_*tC-`DjWiet%Eo4NHSGs+XR=5#&8$(Lo%0~UtY'
    '_aV%@X@hw<?yKw!Unl0`%Lu(w)Y%ztTHUpiK?j_}IA%rF=TSVc>T&hl`aGw$xIn4;i+Z?tgKlM;`Oqt0Db%x%6#s7xSCpkG9tGbI'
    'tJ(+$`yV(D^a7m3*m_}jOSPi?)_L>F_Q?N76eFOw+D&jy$uE*GqJ7?7BKqF&CAz7>6CN0U#r+c0)95TltUh6Q6jSCTGx$n6GvH4g'
    'N44nYP+q6Avt}h;dj96hgl>7hsV94`3v~g77{b9^Pt+?X;hloZkluxWy<(>L%B;f_?|5JCHYQ)A{D2i3$X^)#TFhH}Az~Zr6a?6B'
    'C6u7Su?t={@I_*72|SqK9cVD;N!P@@=*936EAHE%KMT$UvLo<iTd3itS|FY{1~vK8+8Qq?*2<y!8+7BeUM2~x7kD!xX6uLYFnSX)'
    '_?e)r$~*_y->(W$IQvGS=WpdbY0nTp_0rk@oFV?jU)_v;o&GI``141GcnUP<jw_%S^pkQ%&RV!z73E-x|E4C6bFbW=ATYNQbR?5|'
    '=Q;B{XP!7?<$qH1)J@L8i?dR0+67-!=C~^>JgU3MU8<;Xwwe1ai+*y*G~UQbp>~ctR+F>y@Z_G)LMmO*exp3BZM=IY9;?Q~2+mR+'
    'TCWq79UWWmTbEp%Z<%+Zw8;6T^Ty89a-Qz}Ae;T-{HlGr{i*t?@QZH#q&_J>muacS+J6Gg&28uZBo|-RAoo9u#mE`n_%|ZUD-SbK'
    '*~oRHfTE9I-9QD8R{j&hep{|SxwEHmBG->@ZiRETcB}O%ES$~QU2nry6=#S^-eh;XYIhU9NV##fjuvNm=eFl)DYo0{m_)yvw?XyG'
    'ePqk8miyFBqU?U>US^ZDyPvo>)?}@IF5I6ar6=lM$79hc-Rk5?eCzbZo8F6)(gRNj@gk8xoW!rHUh4T8gG*aI9}DYTKkD=(K3nyT'
    'UbJG^)vnHT?8{~ep|(giKYO_s$4>L8^GiIF&5gI(#=f(E&_x&jOu;2&kq=$_<b9pR&rZAWem=#v^Y}^Mj}vk3J|Vr`W``I3cuunH'
    '7^0+AJIBI1I?3UD9DuU#r|jES|6(Qf`P;~Q%H8wrI(WI4^nPdl%l%z=R%M8<*Z<D<lW=*z36|YmSY<`HT;E06Ig8wE8@X%x{(cp@'
    '&0R#-2+rrPzPrA2U$RY5ttl;--TBT_;d|mPcv)`@<NNw6nAbhEPQn*w9lnTl=w@qft*CSEyY!h$>uc~bqw8jyaM`RQx1+zwX2DBF'
    '8#P-6U~hlHeXUbwh|g|{P~AWv3tt^?DRTO6g|9*N^p&pt)wFIzOs@7mP&aX~3`F1tcfPvWgsxiod>^xi&~@&Z_5O@;8A?^pa!vO&'
    'H;6+pyCch^Y`!eq02yIMRtfCRV72b<dj=GW7^=dlyM{a~Ixu7r&%ev`zW$EseI9g}I`*K~l~WcLgE5X7DiL)sOLLCQ15Cja<x(Ww'
    '<(Ry_MpK3nPxc*fjsPNNqEq(lpJ#AqEgXS}Avdf5BOs>0NCc+Eh*8*xO30%rROG>W#JXo=RO51Hh?PJVP!<AYKV@9Z=q?STJ9*K-'
    '5r+L2Xb3Qb2BH8%AZsS|nsFPjSYh3(^B*&`SIeCbbTC*qDnwGl0sZ{^Cyeakj+sdWn00rwma8HC+%P<37g}d02D^zz&u89qld}d('
    'nZ*6Xr^CAQnCN&OxL{7-_nM(i*BZp)hke8m-73IDpzt>E=#+((h5;7caYSRx)Eh8E+M5O!bp7aEoS4~^GYXrTeZlIFC=(e$WHh$W'
    '#fSD4G;o-8KY_N7xvvZpK(y~D`f+nX9v4iUcdwB*Sdy?`OhiZfr8Qb(7MSY>n6jC&h75lebZ;6kL}G6&Yl+Tdi+^_*abcnJ3Fccc'
    '-Hk(artbwK<SBbK=ZV%K1KO~GOY51JDWV3$c-~(R9otuh1jEFP$y{?D%v1?<ql$igJ%eKEc#3=Gb)yN+6f>aq&xwfv6+3kQTWABK'
    '(o1KA?}s9&9j1IeW=Q8r8qF0A4b8D`i>e+X&G!ft!w5<5t7ll7BGamXl164?t~(1lWXa4zjdP!{w$E$kele)}cki2{Nn}qr`{Mcx'
    'K)>Ag2nej(1<&cfd+(^YK##}RkREA?4o7XhX#`P(ifZGEJDMGxWw2IZI@SVX118xJ!QVh(0W4)<)tPmxnE40nLj#W|8F(stw4iM0'
    's#xJO3p6zT=-&<NEZ7k9tA<<5s56PF-?2f38YXsnudp$&hif3|JYGB2G~<cK*n#$&K(%Zncp8rW&g|!#lp|ZY6FhywtZQR>Ub;^^'
    'kFE@+4cN>&ifkpnmkGKv%BU3tjBdxIxYB`{;$U{h9QJ}c0LTPTUBq4l$_Z%2ULzCC;;dSLJ^cfJ@$ui0k+HU(H?%0zSzMTbr*RX9'
    'GW4sK6VOqPdq|?*j^vGK9c47GesEs$-!hdm!eKk9UW#}xj+A*u(;5>w;uJYR)PYfz_N>WF{tq#aE2BA0XE;VjMK7U)n9+U)W84<n'
    'P<g-Z+<`D18wXnK3xm9lmaHWYokHupsSnJkzib2$2V9X1JaoFPV@BC2g?o8s(BjBM&eOgsK54)L2!>AKai^xPl0|I|=z9G=w}Bi>'
    '7&%nSD^qul3bEPWUAm~``*S+tiW;Mx$zSfTiZqt#w9xrXfMBleBx|4{D|J>$oS`T|X3mHNLGgm^L7P&%W5(^7dSA756W=;cdQIU)'
    'P50?pM=)>#?G%xJ-~4~XeO-6rNV4sJIj_2FQA0^8*Ta1f0z^uH02yTIO}2%U`XHrpV@&`08#_`|xw@)*s%PfhS+i<++6H}OMn>+4'
    'jM)1ZKff64jUqf_!wLwBHPja0S7^(jV^wRHR>&-wfBxQ8At`FUqvv;*u76|3{5B5nPKq2<R#m%r-y~af64B>!XaMgE-3k8P{L_5s'
    'zkfUVTd+2wdBY`N_XAY!%rxWC7AIfZKa9tYo<qp(mG<C**2LH6xCdhz&F|Xr!vU9kH-8KKo!$#wZGV{GeoEI5@Ln`uyE!ynaZ-rq'
    '_G9{Q!heoS{@ZkD&&l3DPc4Gk49v|K7ybG59Bgv<yv__Q-Z6J-hV38b!<b`jR{~m~U+tH^7w>g<-+&)9^WcIji}e08N2PWpY*eLk'
    'h5w+m^8US7%%}~9{1mtl%;#5Br>*9Rt(n@mv-rwgblR?x|L@OTI>=a32w`TlNA&0(T#dxXPu1wW9i>x4Ug*EgkDsg8>t^InKmU{W'
    'L?zP(9Y&=%zkkmSE1%Hs`8`Fw<P!#6K@42&$_w^n>@DQGSrtSp6IHta8mJrnyz-m!6Q4G{Q+QIjGt-P2V4w*GWv8$Dr$hC;hYZsY'
    '55V3XeR2yNZIF$j!@!{XZE@<czu6mW3oBe_V4egscpBsVJ!T3cOsDPKJT!i+nF&j1kgpCh3Ac0ociJy62Z}2mhU+ePU764*&vAmj'
    ';S+Q-zQ@ThUoUlVa{M@4Z-eWhijXzKzg_Q-{@>*jUp|Qj%Rbg^AL!42K!vO4i1DyaKO71^Y4&i!jWvo&F8V!T1mL+r%bt~rc3{kM'
    '($Z?3oZ>j`PqsT+mk)&ZpfNnFQ$F$byyVd;-`d5GpLf8>w?zj!&7bzS4{c<mPeVlxcOTzyHtm5=HzuSdV`auTz?!|*+f}G^N5&o%'
    'ps2D2wjuwidcTDK{mLj1aTOM-uuBKs)!v}a68*5>lnzcl3D+tc44UL$aRPJOZ=}QQBql5NK*a}Ly0`s?o<AD=z-6%SG1=juCCweK'
    'gSPVzcs60I&TQ(;W)uO3=nkZB6$2}maSE_6PG-+T=P$Yqp`3yY@0D;GtC=lXd-*H=tq&E&4UT`qQ8NJ?F1cGkYv&R+Mpj?wDtyG8'
    'H%;Mi<ucpP*wdZ$H%)4-*rM|T1r!(r#dOH53Um-a6{UvqR|%z{C@R5(OYwqU|K_0W8?6g{ii1-MFt(!dD1a_~rP;6$+Y8qAbx@%f'
    'E=myx6R6FYXD~voxH3<12laHq`xrC&Ipxs^$Zr|d>v-a5d`<JmOe!JyH(S28vv-;G5k24iAND)i?=#IXf$N*+4H%{f)6=}$Sbwu&'
    '-&;C<;C$V$!EnJ{>oGbF$ewKM!@%_K_Tl}3nGMYh$~ZI*k9Xy<N2cE@Hoaq*3oryt47Cr-<8=lN+oHg{zx-i;H|e^O?~?B#OA3d5'
    'a0z7}J<cyUq4*;XVmsA;zYG=Tx98jvj^)lFbX?GWMc2Jx9bgRHjca*p!dh|Fwd+=$Gup30-6h|GVQN;XcjHmG&qW~q&h^PYqHoWA'
    'i>r#iS~s?43j?m_b@9`61g&SNE3KKm5+~ENzIDgTDlA6rY^v_9e`nqEb1%r>>B_v-RQ+yMTYGIJm*vfVf4;u>xqiB?<U_k1uJ?ZY'
    '1fQrtmmI7CtbKh3>*o61_(#LZ4%qW=>W9cNOqeN=?g@n}Fl^JcW`%<|G(=@Kw9)6x@CY?G@l^>CIh=tJFF{8yQi=!IH~swj9<(-j'
    'eGiI~A;d3rMG8*0?I}OM$qE4B6kSXgdo!$y<y0AAReamOrqIN_*rHG-#ZnmGER+RdmhLtlImQE(0wL^e3bjIqu4k<XPvP@9ghk0t'
    'Uxw?AalH`hrBLs#hw)Nw@Xap@+>fp=-Ksz(Ijzf0?+)v7!c0^S>`W1!v-Jtu1sxBUkgzo3S+W&W5ILHOitvJtBmYy3TtbwBg*y=^'
    'PdH9~Ju_36?woT{dd~U(Cq}M7pID8Dd;&T>@`%<3V&)JED|O;*m`O#&U`_$!lGc&#0(6UMd`IhrY;lJ*hFDnJk9kk=+@?WQ7~*A>'
    '$GQW{<7$R)@p7&i(V^yPW{bIs4@2HBWc*8OsYGWP82^R49GSlx)$zJA)T<>oa&8FntFNde!#L9WCd)gyrO&C~@8qZtjHEJ~g`sia'
    'g*$HE$FaQbxyp;<H?lACdt?vLk#}@QdbHIHSs$Vbu`4T>27_N46y6f#g>@G&GcY87y1zp|d|EjY><sI7`@BCVTrATJl`Hopx_5Pl'
    '4;Uktti}l4dsZ#FG6R4F7BQg|;yJ8TqLoC~F8K=NiJ0Y44fjp-eUbku5v!WoKNS-&2)SS;aB8iT@C!H%{vHg(7{9-V(=@{s*xF!E'
    'tn3n?ic@yM{>B6<q4LQ2qzE|}U@uk#fbYfr^&Tfuyg?W_67QH#W?V6Wy~f;vHE6;rx3GP&#XdbSR%u3{<|}hDD*9l9P*uhLfeJ2k'
    '(_#)a9-T5HEaOyEsu9Nd*3nCTcEK#+G_EeQesgCpe(%rBc3`H;wx#8=>P$JjFFIaE=BrU{u1iCGvC5J3jpU0hN7rDauwTJ;B3<<c'
    'g#l)U$~L?Y2-q+xMW8H(y%J2Y(c~zWpNpgIu)^sPe(&C->#nA}$6zke9f9t-Y%?%X3`)SP@-mD$@}B)oRrfs(eHXt%fe~t8PlJjO'
    ';lJ<fNq49@S~(T|=ikJu+lVW|1T#cvWdaKf5$8z1N1_!&S#<@>I$(;q{sL}?;wbR_H{4O~kQa?(?RS}pO;-?XZL)EJ>(TcG*41Q&'
    'YFKpbCtf5c=+Fn_(pRP|D3&>zQMyH^746;M#ZUUWj0<My=9r`Nj{L-Aj(9B19Ik+XKhQXD>p<B<kzK(*IoZ0@``-$9t=zS<R>Tiw'
    'C+BT)AxtM%jX6##U!T*|j_WtHFZ?v`i1RzYU9>_zfLW*&ZTiRjl`M>)G|_PvZ;>w~ycM7W81XFOEQ){opf%4=m49BfN&8S*+2Nn9'
    '>k>*p*n7xkXm3qvKD^ty8_o=A?g+#CV3X+SUGjB<vqe6u!P&vT>JP|%)tNhzn+rOBq^Pz57#N(B?j&^@mBp}ku7FAgoFRIy1h1_4'
    'AdB->TF#~x`D~(EuY8LMYbl)X3>Bt-wSLeYg|nBdX0kzrG0p{01w7;vv5)b70jwj&!<o=`_H+OD@%2w|s-xph9%rmO#=C#9-q<dZ'
    'zgoW`S8a3LEb;$;63@Or&%u7kaq)aEDDF%%?vP}rHl4o!e*VMwG4A{hkCMG;97_0c2BsY!3Igun=YPbr8gEBKe$AwK2J7I3D}V}-'
    'pfb;E2#=It*GT%?egS+523WgzMLuO}Ylgp7h^ke_z2ETVYzD@2RG+HoUcQAv&F5rbJQ_NHl7ac*-E&oDyp@Te&n=QRV#QumeJ7}Z'
    'eToQ=Xm#d4&krKT-LTq?+QW~r;xmowYOa`hi`LLJ9`b+@;&!gEOm0jv;jZkwi15#>#Mu${9$`j}k4kUaze+GD(e<p%Ys?Q1m7ifv'
    'qIx*}U$gtpVcbv8hjHEimzZ6Wp(6?%^<dOM_Z=#p2~&Zg>UQqKEcZUD(sboNlrDQPGI(5jAg)mCn-jLx%)bsZzi7p%G+5QNht>*A'
    'XvpJH98SKb(X0W3a_ryCOTWt-Ab(L`45**dm{2T(PIfaQtWN$8ifU;;tqYvRI6nFCM;(XS!6-R>lIYY(2yY*IXC%OEIi4WCC^zjq'
    'PmW+l_D8A>Y5sg>ZbElu`c-*$$LcJ)VmO@BJmB0OT}`qW)UXnC0<hA}hAZE}w0Bcl{$IqUsI+Vn8I#|pIYS4B`z>A&gP#!`moL~q'
    'Ss7OyV;v6rvN!!Jy#LLPbsp>&^Bc0nd2t`3gNfOVyCJ{zH{+O}T<0h6_t$wH*p0lvKd!dSWF)|R5wb!|Wo2A}sVhUXdtQt0&M`U9'
    'Mi{At5|HnHJ8vR<yAaVM#nrP`Wsj0^gPqoXzdNPwW7YMmR>`NbyC%OFAH2iq#^1vOgHqhzn#bao_qBVSXSn4>S+!Hw0DM>1fjBat'
    '_zg@Sdq*=vc-W&|&Z#n!2mCnsk%0*vjM=*Kmem7T%~n?yU*<YSXt`4pEVFc9t}Lxf;1t(k=0z|lq_Hzg0`gh$Tq-cO^sb9;`U1>y'
    '7|#&QiVher2%k;)`~>Gc#jTqJu?;G?p->Cl-m@|qvk<C_hddm*^@n<^1N&zmej(n@Q}RI*RK&;Ve1lSAP=HZMePI0O_%7iQ<eu-y'
    'FAQ}&s53wpJ!+D~%*FW6OmstW{l>knqbhc&s4o54P9{CAY4#)jjABl*33^|2&PInnW6byolf!CYCl0XYreGKNkuigCa)ydv@~zPU'
    '9fq~JrTHXmXhsVt8M_JjIfpyr*Q_87MvY`VbIgnt?h7cCY_X0Dtfzp-&JPIhw_E9CL5V7V5s6aOP`&>dvjVzNDSoUBbap!8WK@$F'
    '=Wq9wAFgnIRHYPOC5TCKW)-TosEEG6SA?vfD2(+KT~1D@bB;KRG(W)4&W_0=7z$>FdH=b5K!@HNI=Vx{{Pg+O!97&A|Aa9k(`<vV'
    'M>Rui`!i;eUt-K~6IA`@F0=M>N4{VN0?i0uOs7zl{WZo6bjf(S#4?*tR6Hvku#jY|=v@hP;Pt=Am_gA~f*O*X=H|&q9Ue38LJ<Sq'
    'KNm2k{2F7%MD<|t5VVJRa+}e+7TD_otw4PBrvgefzr>gUB}}jn(VA+PF3w#F1NBI2%~tk;TE|~x%*ZsB2iutXfNp`+lyjx9!Rrcn'
    'C|d8o#FzobK#H4?WALj>OZ&Y^aTJ(aY~bF_6gkMBFlOZD{ikv>c1Owb(~U7hZpOkeA3yyCW5%r$9$iDa0}Y+gY3Sk{W$1V~04LFS'
    '9kdDt;g=5Qy65|!te^cn%_t5G!IE`Ahi`2qht`ji+RE-JK75#`WDox$GX^sVV_#v0iy8JKFpsWz&j9ZKGo}lN8A#B5xcWOx7gYfT'
    'MASg#p-kXs^DXK>!SY^OG*8=hS6ad+tV|d>Sm2D%O~Xau#9$NFojS>k@f6C{Ik%1c<A0dBqI6)NUq<D|AV0aEu%cXY9LcTcgMotV'
    'V)h*a1=~kAFid>;BwxqNWAgf`dKj+_YxlW%9mj@s|EbxG56AT3Q*#<8qqO?eyq@Dx`uw>Woma=?cQ9GFhM7#tS3@{SHTsvCOPto#'
    'ENQ?X%mnfiKlbB(Q5RlPq;%g`gZ8G?q#hXuCw&+-7w=(YZ70pfh@JFtr0W5gF=3|j`mtXo6yI!P-$*_T@n-AGW9!q;gZ}%60Y|iR'
    ';NMAdvcR0s49f76lzilC%fHth<c=>BC|x*niec8@?lXKZ(SIMl@8@)%_t#^)dTsUnj%_@ApRfn5KPYd}=Wq8RJEQB>6a&QZ`}fhG'
    '`|f?X!GzuuIPahtv-tVwIRt(VojLd(J!e5bHRA%k7sUq@XHAl+b^9L9I^N%}E{6Bh_0hmo4!yrm-{bG|_k5x6m(+MKX3`j#GUmW|'
    '^c=&u3``lQ6$Mj<9*5ig9?P%e_oCll*JIGQo&DQ5w-=1p(rPc??rS6yi=HRq@kqZue}wDdI`8M{HqOkHLDyxbjPyJo6twaFJWput'
    'kjFd3owxCecwe((Flr4<#(aIY6Zz2krG7vD@A48ajFhgoX$Pi^7C8=@pReO^8-E|;p~wF=zBR@z(BH$nVt(j7Z`arM`gj|^oa{$;'
    'E`K-gu+u-he|xCDzmKk4Asjj|^BvwXMZ7zw*UT9X@Hf}}ykpMLOc4j<3><Mqe6ubDm>GUxh;Ur;^?aV_&$xpTzMp<Salr~#^vG8P'
    '$hW$TGkP#o1gK{vJPt-e?DMD#3S3~OOAp45pyG2MFn08)KMcUw;dZX`wKETlpNVAFL9P>G{Qs_AMl)eJ1CDV9#u5j4#s+n&KY7nN'
    'x-9j3I#n0z_jLHZc;9MxJkPk_68DoP?svxhmbjlZ!Mt(C{g%w!VuE?&3?`8!a0}PBiZhr<mV_TdX@ZI53?`DLey?}=ew@dc*@|n|'
    'lON-@hT^a4R<F)D>b#OEVE`I838rwced&1BIb#1fqQ62CUZVE}c0~O^g1r~ayT}EhHq8Tbsxv}|AI|4l!G!Q1t2v#+TPGm1!J^Ba'
    ';(63v7aPOT_P3?yH*mIuT+I$SM|5#IVodRXF(2wvHxAgbp`Z?B0qa{GE5->5hjUs_+*#=l3Q9lA|AHBVl{3I>&b4$NpDU{N=W#2r'
    'C4C-BJE%LL@!Qi+;E&`_@(;Qmz@%qW=kWWy>UL6YuCBof@Ygx*Upmefk48DN7g8|WDHsG-j0qIx>^x<LL3JIJ&sYI_%8a6l|Mp!R'
    'e#=9@i^mC<Fyo?dR6m94#<#q-gZenwU07a%g<(!URj+4#4)gY|?isQ3&+48Tw_XXW-uj#J@A?&_X@H3zJw!vj|Mzv9VBPvIZ>#5R'
    ';^GXvb8*hT|E~U;pF^UKV1f>2R>cBqZSr(rg$?wPbS{`de70A_u*}j*bEnlmR+Z)6>YH`m$N5>leoS@^28(a&=-s)%N+!%OPq^78'
    'Y!ij7Xpj0Z^SmqzFeiWo=4(Fd(ecmDz)1VEJj%Cq2Zc}aEv5R={(f@Z^+efVZoJ2y-3l)&th3juHi0@y4Rs&H6BL6x%nTiZh1`c~'
    'M&++?cEKtr6>2GH{hxHd)sOkO_w%g`oD;2vT2x@wrB;>wA@Ba}oF%chQ^oyHA<a#w&ka88xgUnly2z)hJgBzF`F!oOp>>lv1Jl&h'
    'fjXHFre#)s0h2;hC&sSOeuMUCR#?&XXa(xVpT6R&!a+B*<JBsAJX)`#q0a*O6!`He|NX|0<Z~VBmh5cWXdJ`){X9VrO?c~zLEp<g'
    '*(1(72xl-W1sHV~tf-4TMbbi{N+3U_<Nt$Ij-YIPG9=iC5>~7fhI+JExm8W?fYV0_>g4*Fp&4lD`Q)CNy7AsyFbKD>3%^jz)HUEh'
    'j2DePSn5T-kS1ynp_I)k6JQYF*c!~iCHo6z(xA1KIW9B3&}RjD01dDL(t15>b?%Oto4GcdVxW-cQW*ixyeiGu<4jGizoGbEtH4y^'
    'U0rj>{cTY}@!hTdyJAKbe7=BU5^5bcbT95#!+e*Tam;bhLaZ5ik+YZ<O3ct9k4}1>&*Dz{sb(?=xO2WJ0vG!>&%4Rzl=n><M%v!C'
    '5wplcX{F;>1+`?X@<{f?^@HTkQI9#`IC0N)H_E$bg{CBi0>Oe6iBOxxXH(1wu*AO2`x%%Rk;^p4^BGtM(DNYT!%!zo&)L&Ew~RY}'
    '9p3=gJOB58{?GqR!sYb8-u>=x?q~O5==^&3JM362VJiC{y5GaXb)E3yYzptrc~X;6F?+!g|FaX!oKCo8<Y$n=EsOP-py|{tcKKu_'
    'X8$O5+2pC1o5h1M*<NTlBp)WHi)TBDhnD$Q=Xf`HyHFf1_wG`Fwe;*d7h21W;~td%TAZ%*GiV*<x^HTEU;HLrQ!JHpw%yO$rCq$5'
    '?!{a!oJ&8Q7OU3z{W6^;>r?UZ4qfib`IJmwop4^<p{spU7o%W$RokMRX0y#@8<*Z}mYKUtxsbE16M3chFl)Eba~ZU=FPCTx;ykms'
    'zbn^I^R?J-%Gj9i%(yHcO$zfL%1Qn-|CBt~lc(033&O*-?Pc54oAfj9OObsl)sts!X*z$KErfWoCl_Op6wk)wL$o-V`EQd?2Enys'
    'gL=9TPO+DhS}aW(?O84MTiUd}y*L;3y<29%!cmo!XXG7CS!`*a?e5*?5+s+dldTy%sm_!qJJ^8$T-`ySCzpL5yoml2NNYb7UlRA6'
    '2Y2F&DPO#$o4jo0+tYH9ywvX1SZ>72#Ql&g)8x0gYh}ycIWOeryXBpD9m|oq{C#_Qu3WWRZ!eq5+pmt|?Qtr?)yLxZ^K|pFdUHO6'
    ')7{g0p+2<JXuMuuK1`+ucYSdF@lYM?byoc2AJcudF88zr-8}{_8P9H(Ab~lJ3Z2Mw^}p$El`eL5=E*Gq!r5`*&hqKoMJ}SG5IeJ6'
    'ly~$wVK1($a!#;fvHK7#Cg$^^q;cJuA<D&q$qW6rdGOxE<02}Ki^<ELuKSGENv|}Y7L!Zrl`l`Tx9!Gvx5w3Vl`VFcN3SGnC_kJ<'
    'wC}y*<(dBb2;yMSTl!lw^`toY+Ye9PH92|L;wg}XwF~D!5c>A->;L?#IEiw903D-O?rYzn`$n@Tf%)CN$i?oZUPO1#UgSK|^F0P{'
    'ch8H76Sy)-=etA=m7&O<3niFU&rzt{+`8!K7U&EeD%u@ic~3>3O?u(Bj&SF`%AQI)^Li1tdS^?JDc`b|i!$ae_=<!(oD3K^y-$m@'
    'ot#vb%RnxB(dKn(-}io|8sAP%olI-1-Bnh;Y0#-h$QfKbKyMn6h=dUxDqOf)s$FVsmJC`P6Rxx}(dCuROB0bOMSiF{O+9F!a;A^F'
    '0?q8P?5>Mb(&m+Kho{7NtgLq5rqOe4yE~<fs>;H3FLG7dp{LA97PjXq;XN1W*=>E!JOm;+SJKV`dXG*9z1OR_D+4+0R9KaPH&-G%'
    'O5X_77L_wmUZ&$kYqrp~5{;S1(2Z<NFBw@UqaE4Lg>SnjwWX-^L$9)aHZrH9Q`RfpDG{zvl`hksCR`q6@2yp0mzC{qPnMfEmi=(D'
    'va$)HsO#KQm0^74sqC{^N7GxR#)MXIT3D>1x5ufKWF1znG<D?22uJ8RGlN6vXA2tthbnE?Z5nQA%+S3I-627{{~D)o;58?t#+lh#'
    'p#wE67=gH%a}r@&WYX!B<}!6~l8tU@@aI!>T%)Tdy-rmUH)IC^pV3IU=#scBtgG9A*UN;qB{YFu<{&I2_Q0?yGjDN1C6*s7SmVRw'
    '3T~%F_a08w2yr!LOLpnayChILB7TZX+x3-b<Jv#(+N9qTV%!pPjc_U<p}h)TPcx@+X=$ADSZ55M=ovT?MW@d~nPeAM8@FkOuFws5'
    '-IcBsaSCv0p~7X;Pm5sCVy5pkT^l3%Q@4x*PAvp;km?NK!g%h<bV`bTNA|$oi<2Ro#_I|b9l4+)!OA^oq1Aq$wCVUkb#YVM`L-85'
    '*=bJi8_FUb6Z&`eWf^&O0uHV|;5DLf5()mKF*39dwRMh8om*CYuu`forEimMW)Fmnm^N5m<+4j!DcOz*&{%TWqT<_h?|X4p`h94Y'
    '{jq;i=VRp?;Yk@!l?8r2AR}Z7a0*Cs?Sp4b?g(u~O&Z0Gl|46^yH}mpR(8JP=kK$rGGV9VNvmY0uRnV#En25a7G&?CO5J1ak2kG3'
    '#yarnUGBMa7M*#?d5fx<f%A~wc|76DubURs$XJbNF13B<0-65W&-YE29q4(|#=1V7I$A$jcu(s`Rav|26G_jN&&ZBwT<yt8&+B?7'
    '#z)#X*EJ!shQ^vJ@KTqYZ$#gd_#Ibt7J=4Y@shS^dN=Mxq>7YJ34k=$T&aQ#hwthWN4>7zKYvhw3mZIo=q5+km_l@+*Jo|fv-@(}'
    'n%74fk42l!bcdSCo@L+$DjC!K0_8-q?&D2oUX|>n*D1V@;k1dn(Us)Td;}9h;5JDX%P!kBe!goJ`9=R4oJ5w%9W+F)x6bM<SJotB'
    'aESV}4dHng6jg)ygYBo`_39SnpJwpG{Qi184s$Cb8;FuRmCMFN*JC)<+;nGW=mtgf4JL{`>lc~cBaOeSlBgy-5uJI)IBz>EXvyEj'
    'D$U9Noez!q5>dpl;VPlTMpd5AJpCrYjD(&t0RxB)twZQlEIrjelKqO4*_P4{*5vog+BdemAEf=V?Rh+RQw!DYsQShHWZ=gV9O)*J'
    '<~P(G?cl!>jk-cFitOrqI9Xv;2idwa+nXOQX#bcrU>Lwj7x}9yxl)wmZ7OJ^pduQ~1=yb~o1UvLs=&p%qWwv-*42-G1pnXJlHVfV'
    'km00$JyhTmq(G&%J2MojSzT`?GH89SYLRX0%Mj7}QABpRrwBN`bv)Ev7B$G4qMBfmIjxmF(mHXP?!zrI-V;vPkexeP6U)iUuJ>9K'
    '`;xm-!ai2kmG*F)47x$3dggMgx^Ub0Ax;CIo4|`YVVtT!`oIqbBrb$Ydti@BQc;t?057y=2Dpo>PNH%ansGEf@g94+u9idh8Z(rj'
    'TNv2@bb(@B+_#-a{%E{9sWvaW@$4jmtVkuoih;?3HBEe(T**#Q#Tl&RuBEk=?aK})km&fa;p=y`-)>s6Dg8X;A8ono{V^)T4gg{$'
    'SKz6zHVIFtKJ0WykynB>hwagTZ3f)oZ`wFncN{)#^`H|r2WFyo+%;BsXi}^X+RZFkHg>cpJ7-)*5h3l#`KI;V$J)0yw7w-st{U4J'
    'wBWNHtwW#rR+D@~{$7CNxJqO4nQYVKsi1oZ{ytPRBFjloRuSGqSDOm*G6+2K`zLz8ZSRMtrjHY4^~csaKelO{HtBhP>H=EVz#r#A'
    'rnh}V(|K1i*r_f&HvSdWz)>Tv_Y!lZSZhPleiH^1&J|#>@S{ni!i4tLpzYkO_1nA+ya#3RzP9UyJ?t|M?Wr=MnbPlTWe-iqC&*qa'
    'vP4Jz;ZfUf=x}UJ@1Ybvm&eRK%=6<;`6L8fkLEkxR5S8WX+disE;@Tg-)m%+uY2E9O_n99Ym2r!XKfc{^j?wjY2OSypTaA`k-6Sy'
    '!4P7(i$QN`-GF(*G!AVSXI#Ne80?n$X1wErF3eDkEg!f`2^|pJCFJJceU9Jlj{T<F#mFLnWd&6sU@~zvtA@8`|BI?XRJ)-1%N%cd'
    'KUPiBKYhC%;aLlI+bgoQN3MiRJ)CaizEb12n0$gH48ilocGsmJZk*xRKQ=X8_hic>f6kBZnZ?Ee-gcdCSReGgMehf@y2nlpUR0OX'
    '72ikW#7U&Hv1WFw5Z!_q3i_L62R&l8hv&u)4qY0aYQ~BAsm$W3QiQ{O?6ZkprwO4*-ao-il1E^<YJ6``Yw5A>>@DGBSp@;@hcYj%'
    'GyLn|M_*7Sx+i~qz_}moBXtwN?$|!T60`$@${hCH2OGjGW!)JO`IUrXlx1UaT(ot4S8Mix4_fr}JY;WOPU}Kac<d3rvSm&F?$m{k'
    'w6D^h4{lv=U7-q_0CP$4z%SyupW#C6k&e2Z{B(qcQqAqF=h1$sk^Qn_oPQ4f#2frc=E%1k;~^`G>Qx#X>#pCCT|P)F&$UKDyJ!*T'
    'b@qbd!%{L{9O917eQLUEto*pD`z(aLmO<urG{=RHeJ(r@PTxY)nPP;9nO6jb=Lxh8GYXw^)<GV$9(}CGS~1R@qo<+rb5sbB50R;k'
    '|7sN0Ik4Zh54NgvxuQ#{Rt|n5V7n7}C<Xg<aOrNjn~KJR>`>7-lfQw^YrvSF;>*R*N#w|0`%(BO$xIDntj|!=I$-iH|4Gqa=Jj9y'
    '-seh@tt=z;rI(HD`17`A^osQOCjAQQtm1u^@K<W{_X%gSzp4uO;q#83n|^OUG`)Nxzq4b$+hBEDcMBSCipyPkZ^FjO8E=wdy?w<4'
    'v>*4vC@Jn)Xl*A{5^@Ig-U05UzoWWm*iW6xW_&h$9=?RIp#HqONXA|3kJp69pHH{zZ}RxF#c|8?pTv2asWJu}+k2dSW)0#oVH_i@'
    '-^PeH5GM$V|DQ|$j5zP0H5Vx+w)%Ce?381Ft|&s4O-6B`G5Hp!-YW5F?}m<#AHyHtpHi+gUbu+m6gq#51u!1rD%!W>4LW^f$1(ST'
    ')(2R!{PJxaoYXj{cp^Ia<kwRfH)+13&&C6<Z^T`t+*!}u{~qr%JWsS9tTC^Tri{sVL|NTk2{(>&N$cd4#7~9QyRASKxrYwao4%~e'
    '>lSv7Y`E4VjG3dE<LcYE(L0b|)7s{8jrCZwHo^z(Z=jh39R#p4nXSkE#=<!E3AA$?i!cxvk#Hh68LtVCkl!26X}+?eljLK`cENL;'
    'ptB&FbEoMoz5wy3pF0iX8}Et6N5AKr2kpb8@p~FC_qj@K8o&Ixq&U7+K~khK;`;UXovA&t<6IHTY*k$bZ6MamqInWn|D_rO)9lK('
    'KR!P=W%Gl!zZb?0h&#1EjLOotos)7OD3+VCCSR9_gf}t%<mb;)SC}{lvL_lpisby9#uGSTypTV)lZT1_Xf((3-bj}p>rJ-)oP7C5'
    'Im+grO?1+pCnI$<<mMU}CKzO{+fm1?d28Ii{HjyRHoC@1Py_u{tEX|#pXs^QWdF}~dflBmidW3&S#vFqX%BLL@|=uUDE^e*ci-=>'
    'd%_e6D(UJpXO8A7HE(``aIUTG)FnSDGWvetD8+xD9M!@q8FhTQ1E=sw#d(>yvyr(pplKJ-_);7+S1MNZ`+Z#Ggdy#i)=SiYH(Ma4'
    '>UqCEeg8Q=+0!S+h}(m_V4RZQOFs)*aZRc&+td_?BW@;~4xF2|{y9GR;ZqTKj!Hv{!QJF!_0K2&`rLNN3sSs5xC?lm>=F1nr?_o#'
    '3JM*c{mDA#aqw;Lq<Fpl$$Ez$_tv^%C?V`EX?z3R=kKi>j?2*%)v`U){QRwTs_p!V{2@9Fp$VOD8@yLCM#t07uCs7{vc6~x$S$&<'
    'y$9J*meY7R1{iF>EwAlnJ5LOHW*MNv5uIH%{Eykv`s{UeE-D=pZKt*KFWUR4-5IPO;^n#%imNKO(hvPcoLOV->%59QN4^EsfI2^2'
    '<FtQMq#<-WaSFPk_+GFELYFO&eUZ@67B(1)DE1Chy6@(su1A>~H2=|a(e)E%D1a^kv@*38vB#Aw3G@Icp5_XK9E_Tp5lQEHms<M{'
    '`wqGykou31(<1*9QM?ofUDD@OXNSni5Dr}qCzqki`4QGL6Ugn5zsf1*x}Df#AHe>yr}%)sFLg!R#z7q5Q~VE3ZVT(qaM(V4C#n+O'
    't7$&b@owj}Wj|CM;gHnMaPnXKff_mi1jd^1#;P$5<cGI4;X$x&NmM)~F5?gRv3;O<$|c1Qcs{VU8Of_vZLTz@mz!T91eQ^(=HY(#'
    'Wa9!|E?8f>GHxH0iM^ox%VpMC(K=vvsFHA~C`M=bd9KV>RlN*5)wd=2nO4QaiL7(mSGn?QuH0;>M2jR}HyXInW5QE0bSH+2>GMHa'
    'XJ47Ij#E^G>jE1MotT2~YD@7b{l?CAWM56`8?GASnOWje%<EEoc$Q?p-i+c&&W!*gc7vUk*%05M$^$vB9Qx5<?IWLk9&(Wq6}qSb'
    'aO%x?Wzg!CoAYvnZka!iFPFXVD#H13m&&T`j7N&GDZXwGtrg{U?;^f0rA@v;4RPk{oij3ZoK_X+OyGPJj+@Blct7;NcCIq}<e2^J'
    'iR=Vj);{oF=FJJ8*VQ%Js5HWP!KTxiV-K^R`;EWr|9<pWX})eOZ!!NK&+KY+99Z$%H^=Atix+ifUshS3>5gpscAaIZ&;{4}sCui&'
    'A6DJ=ne1?PGRH^c9|&(fQp_*~V=Z@RC)bSD#HLMM+-C#!VyzJmcE>Yeuy^=`wNkVl(7yWA_~Yrqw7;~e5mMZB)cf0Ah|W>u(Qmi~'
    '+7{dqV%qnMG@yOOSe+=|L!PNMgNLHy%EAZQ-IlEy)AO{nKY>XSdQWXsa(5=Gk>GD4_bUUN8EmkQo3!84p7>lwgm*+=%btE(qHg*q'
    'rugktXHnGY_4(h!-HAHM-k!fC@u|wZptJt#&jbIm>pHKlGK%+AUYC46r`oE|HeE8Vr5*X?uUnl5a{k(Gf3jcGzWy)Z{V$)((Rsms'
    'bu?!7H_n^-PrHBZdjC9rU>uPAfG1D|MEG*{Tm|I!lWSF^T6^rjh3~)fLt<4IwkK2~(P;bl-+V3^<^C5Hy_G?}Qb~I{-58=edqubc'
    '9h%?!(<oZ2G$`vnT6elLAKDeXuQU74#8~!Lc9eGPoGh+voKalP@d|f+(K`R4+_xgg>HTRvU4AXkOdEvPoBbDBhu)WNb*}C6LvQ8u'
    ')2@fS-x7Ju6V6;|jnOq27s~>bzZ5Sid$mg4x7s%Dza++&DmeRJlJ>P)daI@7zSfz&`I3x(leWG3Vs8gcG*^Lxk@hi3`x4Ic&=v2M'
    'o%C9v^Q_I(UG>ViRG+;4Z)tSV`J2D=qX*aGb^O2KAC^tgg8gGgHuHqDFQwe3$a1$&qQ30U<P%!*6@hm$>7Lfrr+xjU%C5WKiu*Qb'
    'v(CCUr!2@%mi=@}`={3LA6lRGOVvKj)A7T}lClk=hc1oVx;vAt#uwhlBDqsEPkbKrb^gw(&TvxQ%Ek^J8asa=pN@FW>yxZQzNqeH'
    '*Du+Q;`x8T{%>(X?fkF~fN%aJ?wB3P9v)8SwV^S~{&V>b#sjpjonOg&AV<5V^*i&ENXj4(6#qAM6cetCWs}9bAwT_J9H-(W1AF?C'
    'geO{#;<gXEU~v$<p9q{mo(Mk|s4~^e9Ly+DDYnm?aQ;RnP9g1Uti-u30{8J>#Cc2KJfF)ip4XW+xd)A>{u1YlSzTnFr;?0*Mmyj4'
    '%BJ_?&iCq}a|DbkU~w84VSB_8P|KJ$W`;GnZ9AEs(j4<~-&uT4u;|RVDePcEz9*p=$D0d2pAu5_7?-f@a9+~iS80Uv=KIzn92Iz>'
    'QdcQ^Puy^CBa+v$zXo4KPd|<Or4_z3_VwY56~6vQ^1f<zF0wQE(TslD_scH)(gx?`OBbFs{`>GJ_6vJ!lam!5Dc<~r^)NNcqkXfx'
    '-Avo{&Ca&a#Uoqyrr+ZZiYvihIDQ`diReXCl$_glQ8_&;{IdhnuquUblrgWTE}~dCL_Q=?$+fBbc(2m7Y_sTr;|^LsWzX?H=Mny7'
    'KC9X~?;9)HX$<}DoFk!qM6m{)gZ-=R&xhXn`8myS&J&71%q!w5o^O559<9>&(gx$S@8~&wo8q7#D=p-iJg0c{?q8CpFLiK^`Yxon'
    'DU4L=7NzYjdg~=Vby*I-+nV`P*-^}Ix=(a(oG*esI;y)M0y`1m>c_S_$DPJsD|$D={MV$hB>CX>%gH{|63b7WeQjR+>{4ghj`LPN'
    'Y}E7WU9>}Y3hgh8QUo)w5R8(?Pxb5hp-l6AbB$?Vn2|l`(*!U<%5Q!ExDqM`Yp!<gR?j$}BL8}n$WtZJW6|X<D;M~=k24{f)38N;'
    '#)>tQ1n>z|Qnb>^OlzaIu;&fV1t~^5v|aR6TjPyy8s}!|?K|^YRyKvR3E|FLzE0=GuvgE0Gd{~Ngx}48@Jzn^FZ=n>H|=x%$-D2&'
    'b6NHI^S|f^1K;e=gg-W&nU@qlWxtSb<^1VC&9^2_EraW(OY<*n)>51<RnZ4d_bp$dN?S&RB~_cr6#IE;<(w~Vt6<xk@>29y=Zlgb'
    '2w!Et`TcdkM>NlYX01`sFGa2)4jOfh>3Q${F2MR)y{qdhiVk@qS;#C{Dsx;_IHwc_;m+%-HCtL|{gmcw4<@#6^$uqrjKAn=ZL)CR'
    'r6HLGy1ir0zYH4W&RlsnMUQ1^f-z+5v$_vDrV}Hsf&IGva7v?N-FsW5#+B^Dg;J>FGu%_+Wrd$@XQ<6c40Lj%2908^Jd>y^O2*HX'
    'btPZp#kC(C9LA0ja{91ieeSTeb-gD#wFGjKEf@&kAN^LGGilkglZtNn2`B?iIKJn2`bzc~+?O3#o6m<zy(nqBGbJMWDF?=&_OVUR'
    '=mzq2zPROc`u43weH8g*Ft?ta)@tQ|r!&IiN_Qk|kA+WI(hMq!S7x1}>(ZMwCf>n#cC2`MO8RG-i*1|IJEjrplD3uaE*k+=8))vb'
    'rtOk&<gNtM5!b+sr;S6;gcdBqsr)=rKKHD;L-+s7`;N{|ZaZz^#x(ZG!L4cE+qIVWSX#9AC*fmZ(fcSjo><wk2K%V3nS>Uo%O#Ae'
    '>nWsrQZrR#^lOpRPpR|z6EEP;_?~E0pOwD1nWbQRkjpv^GxD#SI_1vM-7G;JiaZcTqIv2GD<xn;b!i9N6<trykPY=TGg$_~>|}b!'
    'A`4uhf@5(FrYCb2mwq;5ZOt@u=PI}_-m+<J&XA`?9u}+&u8UmurJt7O+$cBp%rF<9ilglw6_^n0sbON?<FHF?%=@xa7gYuEIuPSV'
    'zFotUu#rDrp2X#;^4s+Stj}-mk{K5|cUg<emi#s9{?_sWHX$3a#<CQb8T4r<VmxVGk8nVIY_cFxojf)XekQW%j0e%>$7Yw250U6X'
    'IW%2D>n41dclmv@?P-64l6`-WT|#R;e{ehUNe^~1>Z(u8@q8F{snO8>a_o+uXq!LwzR{>YmOYoa#6>{x_4Ia?ryxjAR(m`J&XXcL'
    'UIboxdZSn>3)YHasycACN{q`{;H^)W2xC6Mn3o_g6J9w9ya^1c%Q$~M5yJa!UetelUJ_OIF=8)1=jzlG`OR1aLN;Z2^-rQr%dRDV'
    '{Pa{>tyl<|mZgijxizg<uNF^R;K>=zqYBnK1)HV^F*w?f!~{Cz*I;=v?IZccrBdgja)Z^${6JXASk4t#l*46hp5tngt!nc_T&3aC'
    'MHdekACP}{`c-Lu2%wXFRG*CM^}IB|OuDdFhWQVpI-a+I?>4m^-!rZXvR&YNO)X{Ar4H@G*ZVeg)7ro87QUC(<uz(kXIqOgbb`0F'
    'PwNEixuqLbsWW4J@YJ2uBHB&RO;$uvk?v)a8VO=dvaf^k|MPZ5{w3?uF~zu&{9E6)SNYhb7j+8aY~hb7=B1quaqrue{N?58<hR+('
    '@7M6*wNH5Q&3&xW%l0J3*~A~u*!QRXti2GXNiVaL@Q$K0j;b>x{+(<W(%?rG1?9=Qi&dA&+A{7>R#wb=_g?L?vbOGmlbK73%LCLx'
    'x;^=#ZC{qwXG6W((y&IKP9wWG_R~-5!7dGZtGa-pApMke*YD}FaT^3#(@n0YQ;?^f-`1yK|J0>zy9lzho49qA<!g#r>N?nOyJXzX'
    'P_yYor!vSVo$%^1*w4DeYbQZA>9q1&hxVOLd2NxkZjc0Rac!ranmw2F?ybVRkKIKQWX0Q<;?EhhwbA(teO`A4RkSy6TB+Hbu+vO;'
    'QpfHj30!6dQQNMx+XbIz1noRX;<l76t&i<9e0WRy9o=WXNaCz4$6l+pgh{~|m_r|UK1<@TEKzf})qM~ua>2wmp?j1?Ot}3C`*c8l'
    'o$zxggh}`z3Vp?zt6<UT>E~IvCVBep*_T3bKZFu}LEl>n6YD5kDb{3VMp^oKUb^U#b-+COp{j!rzNVn>g~GIp>KYO*`2f~Su=(H&'
    'Cv>5#b|D<%J6&zJsJm|Kpxp(j*VeL)y3Tnf9D9#iu-YH*7O9uj<v40PXIG<h9n5*Yhd3&%OE0QAXI`7}ebKot*f}RSZ!BWMqpPmz'
    '+qmn(mhQ6;(x`2s_RtajZn|;Yc40>M*)P&4Yj$J8&tNWrZ^(AF<?Ux_6f$#3x0*L9j={DB*2GB~xy;DYrK9#}q$B_Fu6Z>cj@I!G'
    '`XD2}8J#x9)5t&F(ciP9_2sVpXgrSmx6x^297q1|cl7t?qxJFbbTaahe}|(n*>y&HvfCoa+!iL#b$8FI8_TvcvXeC~7MYu=-MDPK'
    'yB+y9)JE)1mRHO&H&i>Xthzg#;me{U3}(i~BqLY6B}~?fuFG12YyoZEghaEj#gKQsc*fdq`yiwHREsRky2-e1d$Ci>ZmJ%+7O$Go'
    'Ty_($u6i+tt0Bxwdjec%=ypzA7u}^g+2K+7*Wwg}&w`%yB*R?!ca`eNo%%*`LORq&*d3w?orXAUP<~2(uLS+ALqoQhaa~8lxHWg@'
    'X0R{bp!~Rf0FG`%L~(CEpQ8@AM1J6j;)pze_AqqM=jip><$mKQ4{e&Kji2qCE`OL?`M#ax6tmY4CqJjS4?RD5Hn;kH`<6d8{@ue#'
    '$Ak1Uf1Z;~oXR|J{L7MiZhV7&o}XQ7EKbEam;N2?EfP5?`gtx~o1n|~T*^SuULzYB#MpBxm)2P4oNFoO%+NCui@V}zxJPq&S9~<4'
    'Be5HmBV#cV_jmO7`O$p1D^G?u63-*~Y6K&3yraL1qgma_2g4r)njtkneds24KAW!6=cON1lgYzp^W(<~?A*%TS825FbzHIzP!D>{'
    '*PqQXCV^t5G5wwM2ziy-^tqQm{~YZLD4|rZdG^`r)llb24mOgXtuG&2Wz+h2_*l{Rz;adi(MjWL`*8aH_iMTydVZagRxo&cf8ExW'
    'Yfm6wMDdpz^ZOv*);zp>9-Q$XbA8SYG%2c&1&u@h{{1t_b+4)%p0CsIsXALW{yzNf{cyd+?lsQNGsKYed#o$2x9iLg4UG@t&7?`?'
    'p%-ISWwHADd3-;UYx+IT@*UJFsh;=IQ-8~!35-vSzJ)c{0r-e}`SU{@f_%+)<KztS59X1%&4%Y>X1;36&$n;VNIy@C8e<o1T>5-?'
    '7s)1Ib*Y1)KH4{XpwIK)35C;mO+S+T2-IFQP_`j^8k7imUWez<*Nf=A>HhqCeEvuK_^a#kxKW&nzCV8cCc=1q{7Bb1@OW{)Dpv2m'
    '-)n^x;nRBl`aIa3DE@7t_;Bh2nok}_p7#N_I`iTCwDA)L=Xu*hvE;M$@DbyKal^VGKZeiC`M3GrHxs$<{i{0pwxsKmuaKUf=(?F!'
    '*h$rMokGL)pn=eKte;~)_wPTRHu=-=KKn)_3#h{JI_#qGv-$Y3R5_1Rd42bu6kjzvoF4>vliI_4!tVd^etc-%eEg`2ALhsLzP)Fn'
    '>r}T%6QGXt%J$y+QBum-8|*Hm_t1Dd-R>KD-p|%GM2&LelV2_V_`KSl$UfPg^m^GN#*wEk&Ih~K<D;KL{`tDd!_MOC=yhdlW`_6A'
    '-@LQi_kN7uSI<|LTm27zr|X`0oY;?i`J{0gZ9m%Iuzk>V_ey<RPn|7vKawBwd+EA-_^TKk270}5o^a3a_t~sIO1+MuX)nNPhxr=('
    '46TE~?$tP?b$s}2#d=(Wn_Xsm8uzdlHrVkfUO21P!r7-6wx<2~+1h->xn89{eJo#dZ<t@sM^uY;HT?Ig5m#+@>Y7&p>@}i2)-Ev5'
    'G>1hKxXeuR+5G)uwHdD*bzQNu^7pFwZeNI%j=v{1T^H*Q%(3FLIVFGEABKDf@)2*v(sK&`@^%vL<0?HnZH3%U{njRKvO-VI@7_b<'
    'CvS~%534kGnkjlrS8uh6yl&vs_uj7Xowr)Jn^j^sRfT@94{u;kSS43S{tlLQ^(K|;uaM82q6h5htu$S4m1ItN&&rK&VD?#oIk$p('
    '&+M&8w0KW3k<YC^=KNJFW(ob?^-wePCc*HWK&{sku~U{f|9nd5y21k!&`$aVPMnpy^iY2>kx(Q{=(#qY07I1oLsbIhY7ggfZ}Pst'
    '`V#KJL!AaKtipdv8q-ZY<m7kA_bG~K-AB(qJEw_!DukKPnCs`9df`iA^K-r={QT|;iZs7N35VZrzDnphD`p;g1H%-LM}_?A%NrP`'
    'FkaO?>hR1ry6$4d%*L!N^LAQ#PppFb#p7|Vr%*zfz2W(J9)1Ty%=V3*KVCsaf#<DwqrEX*rR^}UFK?~sKCRNL)7&H1tMi(xbo_Qo'
    'IWP8B+<TKY5pPA;Vm{Jx>do3@|5m0g<|{3K_ZDqJ&+oT*{uIyOCiMJPi|0@A{B3ggR$1+Kh4`54qfNzI-L?0tG)!SXZMuJJ(iYE|'
    ';yK%tp3`sfoGG5OP3bwU7SEZ&o?3klNb~aV<gN3BeVOm(r%sYTmRnc-v$~LAQ;WXTjBH-a{aom~@?EgMgQt&T^E_%3^uNawX5>U}'
    'HAy^*&$cDk9JE_dD1dQwF7g925Tk#FS+27Ea1Iv_eJR}U-CE<vQx-bPbPr1Zy=v|75dm<+{WNYaEqjT&xl-eoYB(>;5nRCkoU-hh'
    'u<o(3y;#xSRQ8^y*cXJJ?$O9%^s+Q&`z$G@ZFNsCf_L&mZm#>>Ot4$A%J8@Re6-N#^(}Io`$`#43zg>-x59qD=ItxR=dV*RXp%oo'
    'PhCsnPWu)=r$Wsf#Q@n9{UE0<$ZO<D!IYn5OT?)(zq1pR+ehb#ksK}gI;Qzdt#YIp+N)i*HoAMe@x2^%s5Rz+`vUFxNd@RPbXd_3'
    '{W>`3!I_2LXSR+Npx*Q#{cPEoM$GlfzKjU#(jM<VC_itCAa;~!3z=T$tqPN(%O*9>V!(<fa9$eGyPlW{*+`F8GqS^xvMD|dx2|dU'
    '+`A+s*wehqM4dG9{bQ(TY$^66yE;E>g_UqhK8xlwo3v(FlvyM?%RSY0bfD*WZ2c^$(|kqtdtX@Y&~IPYs7C`vth@216BJgvs3!~2'
    'hw3z{o`N;G?xLtx{iZP6X)_7vzZsWrg|Lw)5K7Q`PUAUxchH5W^TQz1pm)>#{4rf`szhANAP;(Bs2`pS45_}HwW#A2MgSG^+7Icu'
    '+O6`v=kje#_c3w5dgzP!NnLfeqj%x@Ui2S!eqJ{=aA~5-Os+T|ZMC%aLW<F&$)BC~|5%p|h8{30jR%DQK8IR*>Y5QAiR;wa(eDXI'
    '^tA7Xi+ZRZo&NLlFRv9io48I+CP=~KNoNLK39bmUeW|kZuJ59*>GPyZTOHr~ZPxk{{n2z^!XJJXkuOTC6hV7V^B||JsFso+``Nh~'
    '*v8Es`@2@aMtwrI_d7vr8|R`){v^}$`b1-1TLy4dUEA@lQ{zTv+-JCUeqPUx^T4$Ak)!i|r9RXdsR!fhxa@SD`|Wva_%_Sim6xCR'
    'Q`3AX&3@>Q_`a`>zH{H8AI~}qx_?;(!M*CjpVS-tp<cms?@^=F-uxdcQ{f!S_D|-up!K|^_agt$M}<#&Tslrvnl(+9MV&duxdB~2'
    'YKuN{bWrCy!pf?q8#{Ers_8>#qI4Z8*!!CSM>kz`Q|gQL`4;>s;h9Un;5gH#{YmAjvgL;Tb{B0L0W~4rx7ieYF6n8-9cP7JF~Sx&'
    'UyNIe)}?uNr0H}N7d;Mm4d*@{s{;GUvP}CJ>ygi}5@Xq@Gk@-Mm2vL}Mg2;@O=a2kv}9;W;P|r(Vs+}}m!WRtp8h^*0~z(eKbvbX'
    'LOq-5PDjauRc+eiaE`{j80clCeZL^D2AoSjT`(}OCB<=))hS$2_`H7HS<<I<8gTzdo!CKx`rOWQCrQ7q6ZEQ|gE|SoN<S@B{G=5|'
    'z*+~zyv$`)B-&3@Lc`tXGsICc%Y!aCm(m&&-Y6=Wx&A4U<QK3fM`_WGT_sQ_o(W|+xAR(N7S?rfy3UW!L7_$nWh2BhTQ}|P=u5Zs'
    'b}y;7l6)rU(YsEYJb(CI=R?f<s?S#32ia#HY_15#-j^i%B7^bzOX|MVeZTLzh;x@SiUEpA=+%~HTJ_A}N!r1x6K7hB@uCy4EV5wQ'
    '!9Kuu(78CbnCX0Ij+($n9k1Udm1amo<@v-zy+kR&D3*Xx%tL+QPJ&S^0i&1)mgNb~`RW9WsUG^L-Xs`P6ELQF;LRyzIP?QDwD_O@'
    '^FNWh6aQ`2vH5zsubVGH@$0N(A1{!K`QSQ}+WG9fV;!5Aw45d$Ma#~I!ZDnKGszvVa2}n>tFs85=VW3zix+1nT;cc*(npU)uqW8='
    'esDzSd~l|*v;N?GG^er%_s-{Jx-E7ulchPkbGGK>LCkySp`P43Ug~7Y<h=ES^K4E&6^qZ#(+77!@Y$&hck1|0Mf<_c1+7Oi&zB<j'
    '=zOW&*CLn{FQI#Nz)EJg)@Av-^LlZwVigzH{dBoqeRM8Q)4f<1#rQJKo%OV^X47^XmX0l_FGXk<W(HQWC&wtJhPnA%e4fobb9*eO'
    'PqT@++mo%#p2coj`rDZ@qu0suZYIt9WD+_vdwXw}D>e7j{$;Y=&iCrjln?v)b{mJ2%$@(H=;!mx{L|%OG<l9ZvaU;6wVt~rjN7)}'
    '_L6PNu0Xovx5*dJJJYjFURv+><Z)O2<}GF-Pu<CjSdh1H-9!XQ@tZppVhw70dTK|MGk2DWXj`u2+!6ard4Oci1Cv{9LHGHayAa~}'
    'QrhlpCQ1(4O;HyppQ%BURJy@l^jk^G&lH8K_U_t-JiIMeE8i{ZH4fkANqvNKTblJ9B>E1bIlA$ke{`A&$P6n168NnTS|OL*NoTfq'
    'GTHlA^R#oHBj0pRt^0Ivw;!U}+di3WFPrHkiRVR~fSmN}zoHK2lVm@AEB5orESc?A5A!!CoWHG(I0mB6?7dxb@Je-<U7qgU$!a&*'
    'IidUJ1k>%^W^%csB~p_syxUB-FaGp$cbGZ!yJG9lcFt~kQM=j1+2ZqV@f1xb+x=|!l+PS9oYD6Q0@1xhM)zFMHKKXBUrsNV)%@*='
    ';=@%qn-o)5m(Mb^qo2;?VurXc{o736l9>M$cOl(-LBD$-x4fYLFK~VLQm>|Ot90gEqS^LxpwI2*yZvEK&pY4EmXm_UVEYmb+FF8{'
    'PLg<En9^&YRU*8}!1?J9n((xPt_~E<F6Yn$p2U8oc;^uFWMNfhyfBhkP?^0m5%x@XEUL74y>7hZcvnvdJ^L=$U{LXMueGM+z)8y*'
    'wet$hA1a^DL>#gPB<pTL2kwdr;`uuc(m6O#p$}Z&v|8wQtZiX|i6jaO=&T7hddCq7wk1NjQPd<RD!`V|DL`g{c|sMmu(%6OXGFJS'
    'RD>+K+9!>X!HEblEeXZ=tkWZ0dKT~<qk1$DrD(xRyQ&h_{i4r;p{L!0YqB!wZwh?1tbIy|1}9eG%;EP5Cya(o@N^a%LiAvWnpNQG'
    'O#|?kYA)k4oHWo{w7_K>KudS7naEnvsQ8}sCm2PAlMznzN3EEvIHG%kGuDH?@<?nf&3Rd;vdfo^xNe{+NxQ9Ej&Kq(wdAg)i08ax'
    'oi4MTQItc!XCzAF8~ep12r8kXLR?pj0Cr#sVD56wd0Jpx0`OgHE#b{I{>sU&x%DTG;<01RXU$1ZcCu*`-QmUDq&rj#N$4QG<A^33'
    '@u4eQCubU0Lc{ucvsscwsGchPm7_WNXIq@?(ilTa72KjUmmyfw=zYflbhHWi#DiV08+4SRBL*C+3Oaz$t@vK^NMBbuvZLtTG#2{5'
    'FNdOwwboYxG=+|+bIAII;NOL|b@El)I@a^`9S1AFXKCKJu=97COgZ#&z*&lGt$><KOLM5s6B`<7@xXcOGM6hV%4n@ftw)M=#C*Y('
    'K;_kY?I!3LhcxG0=^s{L&eELA^I<&KQw0ucba`chqEK*Fhs>&^XgoV`=~6`F2kQztT+l(%x>b13sUDXtxURvuiaCSJb4!5^)o7}@'
    '^Y?f*=rLj3=Fna(5v3rrc!U--SG>_42oCE(1MC}Da6D)sZ6!Je*`8-wbDAUaf%BK=ebCSo(3cy}Y3&BI&d8>-h1`LY8vMfUk~P}I'
    'b?!jFmU-D@S9g5eX>CK=ayZMO;w5cs=uV|;f%n@Ma>rG;OO9UY_tl%r^It=EFNIzkGEa#9Jl5Y}jp-!YvzANZZ3a8{-gQdc7_6eg'
    'a<;57*SYid)|sh1+McASgt2Lmxm6(|GIR&erHTeEZ!q<FYi1GR@2Pt*Y*nmxg{}ug$*@UJv-Jtq?48p4QRIgX;On8X;$7nhQQf(_'
    's&m2cNOq;@AKAAupov31+i+Ru8y%*wU)@RLPt7*e9cFe2ZS6rLaCq;)t-wRgU8#d^7&CLAD)~Cs41p%bY+2)&8qZ7b!}@2#^Fkkq'
    'J08vV9giXS$X5-R->h(7!)GVgduU<P94_kwnlPEC$MJ<VLYd2ccs^;tt|MrpL#L7K@+xSKmxY3cJ+u2vpyNgM@r{c-oel4sgKvEX'
    'PIQSq159!_aZ2v?RWe?ZADwcCHYx_8Yhd#J1?HH!bja6QH)avKzKX%Wyav+^*rI4%ibmuS*`L<!R#)hHhqdM2%MN<Ys6M{x3={av'
    'RqU45)1VPY5u61+>1bHD0|z$iEM@2zN9QsAP0OO)V5}(Gjq5bON5-Q`p%)bHDrCkK?WxFM^PUQQt5|EQZ&8ifLhI?)jjOqw{fPVu'
    '{4MQg$)CT!)?jZwLl3S*MXc}5>3t8(#SP7E)24`%{L8VQeKt4$D2@@J{YR7;QN%lvtoddB?e}fof`<kjLtx{9_N6)K^d{Hk^m|S1'
    'o$g4{?^`;phdr8^;yQO*`{9PWkF~w7|Jq(9eCf?zZyJdczK0*s{vIAU%Y*s0Ty(=PFjf<2E_ER|^l{p?#q)y2OoCa4@XN#sHehmV'
    'd@v`WYwH}fmYYfF6$(V<y>kLvYG=%KW%EkUWpcwu=(YieHmzxOo|k6ml-rze%b<;!7>7EIP_>V4Z0JM*$LyFPN(6B^Xz0xU>G~dn'
    'dmb79+X}2u;*5D-)Mmbwyf0q`>rH9xlwf9_BYMX`n$WArJgt!i23-7$kl6yJqBW4;%argWv^=Z`OcuKa`l5bF>mH>p@Ld{*R9j=E'
    '=lKja0L?n0TKK0;!|YQ*RCONtN=f(-{P}-6kD=ac!dPcQ=w9l)VGUM+Jpvi^;AU?#WImx!Sb}xQ<oj)#G#GqUq`L_$m+Y#i_dS#S'
    'Nv#$6&He@)g?%=fa<?8dFnw>u<JggZ6_VB;*elP_I-}qTtZWf@(SZ$tXP~D5Ev$v!7wQf9l{st7r9)M=Mfli{4%J(P^{|kfv4ej6'
    'JG`rq$&1r}X1}!m`&?0{JFI;6n<5CAg^%WF+R^)(v}Vz%5B+ddaH-)vf91L=9<)+{m&t}Kx-L3PeDA;vB*5WdC{Dd4bmso@y0pI+'
    'zH=xQ7&vU_G{HK`ceLhqrD+dLO;6A~nGNH$;0||+V+cQOa9RXCitpnI#3ETd>#{xjnG~9`gquw0W<fjgn?KUm|EqO*olC7*HXk%9'
    'wC07%!1^23Z}F~z=H12)jHLQU`5MhXCl4RX*It16fZ~b!Qft&Mr_lOLt_$pMTHBGZigjaAh)`u8R^}P3GBehCd}sd@iqbmF!L&)&'
    'J=*1~oPAD~ABtl<`D{XCcf3F;Dd8XO-zK3mGH3V2(Qsy{23#2Pk@+;>*iWA|GsN~Dl~yzJVML#w*XCqY9u1+_>s8buTuJQXx|7$*'
    ')2XF#!V21W7_TiDBx}OcrDm$|um&Zc_Pp2Dh5j2l%_QNYmMfGcGl@WxHQ1J^GiWwZJeQ1d0u<@Em~jEH&O&2(T!(cXJTM_Zcad;#'
    'SZZyE#l!@|NIN6{^j_0-s{LR<81hAHN}&_+r=NpeQ~Y7t2U+~-b5a}yt?>wi=!ie3<YNVAnoYv`{LVRaT511fJUyQz&?_NaW{we`'
    'LhG4uf3P6jIDuC3XLE}Eb^1BEH_K#*yA)V^39J9wxVrSbqEPoAixJs_pzCe&iJ|U4Q+$aI5ZW8!K`SRF8;S@2n`6J8(Rz$1Zl5sA'
    'BE289`B+yHsU-SG_<AZio&i&Y2mQ=>b=%JnZzK_PKrw&*SFC}U2bH$8muhWWd#SZUp%+{bW^Vt8D`q2T^#O-}y}m=(fv`QZ?*v-g'
    ')@Lo9uwcC^dY=S-6?&)8*2KSTQDVJ1u~+guyz_tBPJY$SJltD4U!Mb-+`t&*SLyFg2)vJbYAsul(>@E$Eoc@pyDr7XA=r5+o<KeU'
    'ryLnrZ_`qDhUn)I?VPo(MTp7=!Y?tie9+#zg8mJ~PS7)U*uPP%dDEUF-1z7A%eI|i@1`{($xgGGgpLm8O2y$fJD|8sJ>Gp5!egzJ'
    'B*%Pf4OzZ6*>o{zA|u}TIxqjs9+i)ID3W`-80E0*59MpTFvL&imwZAf^eH68P+*vY#u)oq<cYp&2<qoGp>;H9;R*-11nXt;Zha5q'
    'dR@#hCOQY;l$cx9&WkOyw!V(P|2;OQ_$|o-H~BMr$Md$6QgBQ^)q2b!PEEi+4ee&E1=_1PZ!>jS|0hE1`0e`JcERzJ&^p0`h7dGP'
    '$-j777g+BXH~U~VY@S!a`^mOUJ_y!8B6}}cvl@8E+kPD<#tX<J-uxw9qxj|Z2HWvj^+4lk8oztm7shkr=l+HKls#xl@6*DPE;CG}'
    'h_gArNIp6UiZ}W_PHdqo4>f{hJR>YO#LY3{Vx6~oy-p1!1fM!VCscXR?D$-~p6T}wmOhzs;$qX!h7&ip72yNn2^zal=OZ|m)4Lu{'
    'z^w?HH9KaPB`jQmY4fYS(zuO~_gLD+1sdHnmMS2dq4(WD8<c*(Y5jo_ntW)qMYlHCv=OgB%bIgJ3Yw~{@3w^24fM`v&)5y~;V?5F'
    '#ay(8hq$Z8_XGYuVVHrnSu<ZVGgrVG<0WvfW*2igcSP8scsRQwLF2KxI)=HhidQ-RY@R+=8@V>r$2-Cy%MrAGM)qnXez)aF`k&3M'
    'Tfz_ev%hWk#Ra*n06E(^?X_$2A^sFhHsTDt3`QHj()Rv0_Qj_ScfF$vLLin3mwH~6$E<|Ncbd}W*p>V{bf8&_jN)1Hi_l$09I#^M'
    '05jOp^>!7lcN(`<X?Z)X^*Q)I(URZ5I*kAD93j>Z**Z?<p`+`e?Ecr@SL1+Rz!B&&MRiEe3LX^K0-sH%WJeS))Bg`Pbp3_2{;lgR'
    'rqG%focBY=3XW=^DZi++R@g7#q7~MGH&WGSx#>M<@fEMVYnYq6a&v};vQdt%3utpm&2$F#sKGZeqdfK*!mKw<KXhVazp!aMfg{Jj'
    'k<-fmyZC9w8j8{kkfU;;saRg1|Awk3yeAkK$AM;g3!phTqrHLlQyL@WPq|9$4>(E1lc|XuzlWU4rbv*VR6nkZZ}??0<=i0j9YcC2'
    'u+=?5dyw{KIq2BuYpubxrx>307{p!7_z3(+HkqvG{awO75{e#LYqW?lAJc;4-1qyF#?xRmMm$e@%IaJEN#CLP6pY#x;$UWw(K?hg'
    'jx%~z<PZXMfJ4j8OMu?;pfS&h>{`D~?!c}dHkSKPr?e9#M%w&~`OT^X%fdO8mRvQa{ZRXSJur@O-dH+g>`_ZTn?W8J%-#t)zxWIQ'
    'ntt>yWRD`(I-Lr6s;`=qb2&jJnuJP>&*}(%_&3*eFyIG@{aH_2hUna;IRn0#@_kU*nsBAk{HB5T_r@V~+Bfg9_QA4f9Bbc*PF?ia'
    'r1^nj`TM#HH=H~2<&t9jNOqpi-};`*49}>PHNEEoRe0?G3ZK`hpx9qQTM}nfU+oA!3G*#99>{3z^yqBfls>(C0snV}|8s|R=DB|r'
    'FF;pX`y1d-kJc{v7ii%jo)T-VRY`k}fWBj}rukd|<3fW~`<HR}Z{pA&{h-b#LL(fNk?yzWh2PIsF0|(n7m-h(Jswpu+P@_5FE06)'
    'e`S9|UV(7~?e8Jj6*m74j`|z><$o@3mn2!4qT(;7_0CM?SvBdGV0!^`N}G(c%I~B9rMyw#CD3iimyLN%BvcGiCk6Lo12(5l?$G(G'
    '&!>{VShs=C`w7Pt|Bt;lYffa@vIhT4y+&K3Lk37{v+u!U#3O(p80EYnC5nm2fTM#D`RjYH?H&l_bcTCxRask~sx+=3Mj!UP*Mgt5'
    'A^)ua{~&T%0gb!p==Cx2_u-ULV)hCBo2Bn@V8kmCyG6XMjaSkhlBj%4z`JXZjzVLbTC@%m-)%M{tmks=jw*>*VmH?Eph6tTCx3Io'
    'XgSD*Bgd-kkx28<ZW6L#G>59q+=<|Pozr+CZ-96r**alRO;@7R)A7~7KCX&hLStEvpffe9XG}g1tpm;Ry3BjqsFvq-wXWxNG<)Ej'
    '0KIEvTZlI$v?hjClqRU4WnBh@ul0s(;nl?LZHHxsctsrP_}26;dj*#!I5m%Cw@-TcYfbvRyek^$QgFo1CcAYExdrAB#PWc`GpjQ4'
    '2Q+u+KebP!;eL!NRnxj9e;^XS(zl_9YVbW!^0(w0fqV7oUzBGV(0e7{Um>3}8)|=r{ke}ZRvZ2t`L8lD+@glp(q2gq`wmQB5~#WG'
    'U+(@DKi(&~0ECk<&!sdRqs=h|r)a5;L&GWSmpU%*d60Qg2zCJSqgFoW^?EVb1cuN_nOx94t+=v}3$UHEarG)fT>ZO!D?|J6nVH`j'
    '>oYTg?UVH`s+aYC^R(Ne5<OA0{($cKRP@fW)_L&AZwehZQmDY?IN*eNdo|Z5@)t`+V^jxlH;=hCgPvQEzBQe7Q*f*z7J>X4$4VlO'
    '!z{UC8S+U${;)qka#)rkXAK)S*7^N!>OjEoRoHFqN~-hjjLuB5pX6HcmY8@w$q6%WVDHnu2JA3Y4swS_Bxo+ReA;?i4)XW2VC^os'
    '>OYE?nG-uz1CG@5&;e3{B>MtL^9{*Tur@U==dG%IMe@nT`kw8Sm}Tpj#%(sLGP2WpoM(T~a=AO;JUs0uk||C$1^;+x#)IP(WapE='
    'Y|j#}*&;7E*9g*mvTL?}Ci>(zxxV34CYvUvy@$MfEIbJ=%Y$CaV&j5oLff3McU-sAcot-(--KzFlHPCpkYt=A<iN@u(hq7gC;N+@'
    'J4LJ_r2R97>~s~QIs@q<%0&`p_6D&L(jN=3Sp^<)^=VBu=>mR%^qT|Fv%v5&D+F?V2kv7mWfpSRha_1eH<~H$wJ$qO!F4W`tiUf#'
    '@`q$k>PDUB#7NndjXd*e<S{pTSF=coI?+f|TRP|Du`f=x4DyPB>dwm)`No?FHoLI9PCn@R+==qqB|W~p&!3N@XZ01F-$_S(y)PfS'
    'V@vBD;Wyv{b#*RQoL!D<uq`1%_~@Y2gzgrQ=dXRy!J3-VI*~r=NE`>cJ$0Q<BbPc}5zn*z$|XB!!Zjn{A!d7OM)u#9WSaD#yGZ9a'
    'WDj`(kfcvQA{s?ln*#QsgRYqk*_6nGrz7@D04E{OzQb%oT*emW0>02ABamc3s$RQ+C&_O}H)QWFQ2!AIjJTDAj3}OwoCIrFgE*;*'
    'H0sc1fC^z@vmF(3F8K}i$P>`p1}^xNPsm$kGoAkh%0VnWc|c8#WL6%r(eXuzm~F<)CFFNnh|~J${z=bK(Nr8;6!MEz<f{?t35tCZ'
    '?^FX@i01jgyvr`?)|e%Z^iD>;nT@qe{=EINB>g({z|VX_Oy&jl{>X1QFGV{3JS)W+t@c=h<e!|t%#>ivz;7<lIriEgbsCb_Q`E8C'
    '@I9S|<WK63JB^Jz7wKZ4FRT&|wG6Ny6s^MyWs<H&PEoeU`dRfk&KD?aUY@K8*?;H&m<Zc)vM*iov*)+@r0aIn_&)0#!)FCQ{20=@'
    'yw5*%2bR6RFJ6x$%l=BA-Qlx(y)D0V6RYRlR+BER)BF3fbJX!aXXTPyHi+Xs$KjaEnQPxjZoRF%%5Ij}Hx=^C`_(W2lDLDq4Iqh<'
    'oK!c<a-A#!AYtzlbZIVkQ`96V<hfPV+suIk7Oct6ahQP$xoN*r3$jJ6&{v0P0XYHN^bHJR)s*z^%wHE^)tQyOcv`)M^Rl;?l8^P^'
    'ueTG9uc>&bV=+GBU#`b;27Y%uCizHn2z?E|NXvZ(wg>sqIakIb4=@6|W+-T{6|a`xVTAcG?AQw@f3^k!c6u5{9lHVY9O)*+?7FDT'
    'Cwriqa6FFZ@di2AmABq#gsL^Vt6{Tk#=EpjYYVn+H*q2F<rX>`@msPnxE^oD3|O+By2v?a^`cmFE^$_@M-kcXv7^qU&k)NdpYpUK'
    'JO30w7t;EL4jnrR$X6@Pj4Dw}w+MDBSvl)MclGo(<gczCGTXT)yN=e6cMGocXEnH`^+a-Pew)1>+w~MbLyk?3v1R{$UwrBgE&J`h'
    'e5LhclboA$$It51?QYOrb=Hr!yUB6USugK*&&SpCy1cI^$CcH4yx)E5K3I0<6cbDOWVh@b<W$vk*I2@Z9oKAiPB=w;RYp1<5hJGI'
    'xhfgx`VEpFa_ggPnCz8>Ku5*Inss{cMZ!g=H*%_uwG``z&h8XGbb89!y;{nwYhfwQLk<G<+#~;NVDf8&t=cX#QIq}?KzfNa^9Jf-'
    '`ES~Hot|Ox2#^P})Kidm>Y1sJr1L&pkL<ZEe&_S_?_0xx{<LhrZ?A{^7TqTTlY*t~G#Za>l=oJ29V;k%tM)z<+5^k{R1bFMIKB@Z'
    'hvSQn*E38$h}r7=S^FF$U+B}me$E7+#-3eflX~EgpJF)SgEsHij>jecGpI>EJdtg4eSEeoCiTQ2UtN#)ok4Idq9R&Na2!3)L?b%F'
    'M=N`@?#VCmdM1BB_6fZo-G}T;$h&CQ)~E9LVw~$$q3(P1Ty6ad-;eGq0=^D%c*U~49-S|oHLdq=##`U#Zb{?*?e*I6Pw+|iz2yB|'
    'dY*E+A{&wH6ID;HpR3I9N%Pp$ZGLQ$tKWL1S_NDBXX+9$UNmkQkB7FuR`5YEuQU!%@ALLy9`4wlv{Xj#`K2Q!meAMZ^~CR2zR|i|'
    'KV7fqq`00hGyi&>JeljY`FxHCqVr{$P09C_a*6y@0RPBYLEkS?Um3u@d;>!r&9g-Ofu1>Ep`&_<czOW;gvKXB9bn^P{zQ=>w<(6D'
    'iHnpcz7PMMNq>lXV%H{n=X8YMGenKJYp=LDf&8{1I?P?0?6~xZ4)Y=M>8?#Op6vR<1`?7B1SHWSeFL3)$GKhC3E&szD|GNI(ZLhI'
    '@1CyE!Gn4ck^@_z^RtyG)~hM`JMhut0RHFO3Y|Plbn*mXHO_%<fc4_00sJ7{F~s)Uj>qqS`^C6lfqHxUfcwR`U(u)-b!~LNxNufv'
    '$5czyq6MfKqWcuhDF%um-6zI<iiY<M*%5!@FVk<OH0yBCC0mHDuk9>!t^tOQd`fg|x=zuKk3490UtNbmI>ZGJ8?6s|mgc1IOLj{J'
    'wi4Sldj9V3_|Ih5Z-*7x1ZI7cPY*u`F?x=hCFHk+Ra#GgHvXX=O+C5!^Vzi`_E(~3g?by#v7iPja%4Z!`L9KiuUE8g4`gQo5e)gR'
    'Gi*W0HYHj`5Z^@oKBFg+Z6;QJr*W*}xo_&<4LccXtgzouV}&|Vj`^c@I^jCu(mqcZB}?}OEVJ~O6gm!*2;?a+$MD}281DKb)GU2l'
    'Cr&n{VN{2$0d!3N?~EtSgp0Tx>HgE-IgjM7iC5b-`KgHOpG~JY;>R<vXQ0Pn`7g#{$&U6qWm{KI`iT5*<X1+5kv3yt;v6(yKOUbf'
    '-dTs|{`Asspag1ANv_3#@%K3&5difY_2ki_WzdCQpOrw$PYn|<`Bs4<8@<u>ec1qvG2DgQ_7iA1<g7*=_4{oxIe1n>cF*KIG3!F^'
    'WDWLFI=*sEychKW!tKRF^E`<C`e3=y^}Y3oW3#ByY5K4O5lf)4-=a>Qd`NeUcrf|7rcMF160;%OYlts3bPVDW4eD)a?Kb2K%T*xA'
    'R@HJw!QVr_z?_j6IL84S5X|KL=so_y@eWVG=R@59#y<n=kME;iO~A%&k&9siHyVXNG%@mDB==kWS3@2G4RLPt=2UlMgE2VqOFJ3m'
    '!b1Hf`VWR&uOFdK{YZ8(YILkIdTA<Mhd}b%9p*sdRmGg=9gNiEUsTOY8%IIjk&%6Ae?k8Yp?_SilQ}~F455Dn@^;L7`hWfpIw|F7'
    '@;~268O@i@Z&Lh|PRf(8((6u2B@&d~MYi}P#GP2!&gU%LijD0Yv%lO)*%h|%N<pjtPIyC+_MI^ED=|AcBjMkOx#b8u2(rb|ncKlE'
    'TW+0|9efe1uCvVoSEw7O65&d$E9Xl_UjJt19Ax-Mwy~T)WN2rP2j}&K4ou(arh`IkkItQ-?epZjj-qMHEZ0|ZlNG{^l{{zV5&JaC'
    'P`_kHt88}!;saTsTX%bk?#0f9TdA@`;l7;6@_sqGT{W!5YwUKiVJzMXFH)nI?5ppMn^8xcls8x7XVG1FPwBXm-JId#e9rn??<f*a'
    '+;zR*<Rs6mqjzUdghOKAZ_>xy9r>|H&yIKWoopKC{+++Hr=RnXmPs}}IAP--(#4JQsDfj<x_6WxyvYaYJlVlb`ml69SHUOwkU85p'
    '=%o)$zCEF1^UZlq14}&IIZq;Vgo+R|^iOK#<TvQ#+~u5aQg3;=2otI9oJ@pMu@3X93Ln(^<a{}VQ@MF?_Exw*Z4S=C4quwh9Ynxc'
    'Ju2ro3vcbmzVp%y0{OIY&SDUWr^Y!S2gB3T*ZgZXn4F$`=cYSYoIbCe-_8S-eg2Z)j2xu1rwgdHp*Q8u$>d`vr3y_a<=mf+rrwE;'
    '&(g$CZx((&n)+}4)O(ZDAor(!`jl`dWiBS(o0z!t>71&u<1`ar+@)@6$8`Q2U5)6Z^l~xtPIohOQqnah-szM&e7(~K-*G49n@of0'
    'Xc^>UK-ZZ1IgX{@-bSJ6qzt_DW*Ok0v%n{E|7rV=ephrY#n*F4hTwmT8;SqzPX*FYGe6G|zFG!TNekAW2X9Xgp}0W@=gc`h(KEh`'
    'b!VNwB+d7s!%a&{`W~2DjSp-yvhZSjlI2ETxuQ==R(6h#q&m?WFk5ENb;2HIdYBZA0A8uCxSQ5N2OWIR=dsV-ATIb!NSi^^0RM6Z'
    'Er)0iFvhuy43WspF&$!!$^JFlgd<gLXC<<Wx=YK+dYS`(G$1TpWcsEgd41-S1JALJ{0BQo?tL<@dhVjyuM!890QL+OqiyE|vPj@q'
    '9~jL#t`sWWlMy%!N@Vn8cT#|J;k(XCRJ9>`+K(CMoGY$Z$W)TXT%kHycT_6ws6^M-dq-u1Ovu6KPEvHpkVS4f1Lw?hj`80kBI-``'
    '{5-AmH83r~L(UaXZr14smi^qzr(1MfrUv7mzPIRm?V*P%e#l8<R&q<4XB%eC+{#{$<Pk~wJ_$G@(rjr==N<ZfXgc;tYl~UYoMXRn'
    'NAKKvq%qfVq@Pndx-y(Iu`XAh{gqBi>D(g{_^)?TrvHB@<^PIKN<ZPMZ?44a|46P}|4wR`EA`m}$zCnawC0+7cShbwig{(MoG3;H'
    'hAekI4*s6;_I0PFgX|nxh-|49CR0UnMp{E;(tsC}+sf4y;>^WtJo0WrUXG4B+vF*!BY4Hb0@YxOD+nSVQOf2Bd>ni~@fm|;gAB3m'
    '`r5BXJ82=~YdXYho%u$`Gpb-vJ&4Zl3rF7>RxDYSBxf9VQb-G(mr8RMx{@<qC$gSRhaKb@S^B0kG=bcllnU#$9%kYg!Q#GTJJDT4'
    '7A%bmdlcyG<oVsNbfvbIA7fPg<|;<zXn65V(N%LYkuY#*B4V;fr${#i9$~@VuL;lh<@(bVcovYE6|P+j%Ma&wm-KwHXe$pS%lnwI'
    'vLdc5O@ZrENW%lGIXLL~$s@2=G%gLYD6=+#X(B6hpZ>7QF8A?uC({ZYdoE{Ibk#7{JE|j+>+|XFz>|Fw!O+hsFdymla~Gm=RuY{x'
    'mrh<jU*P@;I&Jj*)n9p!l&jZzSM#ve^9lwu=A)GTg!%1l-iJJ%@1D;;xW20VveTbmKQ~>M)@XMQ-BsFMcq$S2oAc8#F&=s1w{ie_'
    '1~@%f6Uf@ggQ;2qhi$^^OYe8rs|@EbdE+dX-sgYga0OO#)p^?Vm+ib25*<s$Wgc>lJgqQ~6WZ^HG?|WRM4m8jdc9?cAlZ6;3a#%G'
    'vp<p@?I4<;>0jyK(e}#EJ9r8wCeO8)m*_@l3d05K^r}fcHG0F@F)9K&xVa)S<ozJ}qfDNV8Id|G(S`h!m+|0E+ygSI>DBxUd7L@x'
    ')kS5rM3p9FFOUq3oulQIIL3&!uxE`bC(@1F?Pr?`K-M2Rg2oZazjD06FmfgCdl)i`1&}S8ge$4J5)@s!n4h+T%S60Q2h0>)CLW$&'
    '>%|0>)Rz5wznIj4r6&Eq^Bg>%0@ZnpC5mc}7~Di=+&%EDWxb8NQ|O>^2bxoa)-5_*)*F)lizI*U`c^aST`JIdoSOugb1t%E=|}mI'
    '3E*jpIO7U*M6(!=UKFQ8!nUeSYkR$kca6LG)$w{<7QdQzWQA#*FXNH6*R#~$SqJ@*rT)e`)6Xk))fJCxq&ti799!liDHT_idWB?e'
    'dsN|}Vo-Nsa5W&yaYV*_tv3)kMa77=D?P44GL_L1+$Jx{W!?lh<xeC7ToaK;COxD3x{~Y-aP^Kd(<$fixZ`;>=RB<|U{%v|JltiS'
    'gJWGXCNBx(H65RTqtYB7gbEmnTe6p74}@NYE;o5bWE$9tE;_c*v0b9VLV{m;Hei<!ow_zEI)=E9>mu_nksYORe}-KGgpvcT=jO6b'
    'b6o+v&h~}3vpG}jRVvn5Yv{@xSbK@qyQuU5ww=9-t|E<O8&0gOb9Sv}gb1#aOGYB`JN6tINc!IEX**ev&5=YED$cYVMbwDo&3TaT'
    '=~-+Q=46-r6TJ^?wT}JVp>^gx%Sk_<)Ukz14q&x4Wyi?vgb@W0aph?9(MM-mCgmL6zLiR5**=MVyGFI{ka_vEK9J}PHa^^+t=Bkc'
    'YT#u?JNvLA`y;4yCXMV;^3PIJ+10SE0~;H*oOz$xR6vhNC$7d7_{Dqf>~G3t*SAsCjE?+xUgR|1&0$*f;<(cCX@vFq*W~bMl}99('
    'n%P4J-auJQbp)T}Bh8y@|GAvarwI@mri{thZ09up>0j3aO60Fr)M*gut$mWiw|YLLG%^c5Pt3l8g3l96U{RV1*0#fn{Ly+@lC4d0'
    'H#O_v@64y?+du^geV_*vZ%JG=T&;JhB>OvhC(FUVI9p}CEq6rGxadq`+Nbx1pB!rx651y|*^ZjOv7YNVM@Dkb^?dTbNTy4Y1L-BB'
    'qL`~}3GCIK4g5o_yC;p|O2>nb*0H;T+^M}9{9^0Euhq#^@OM=iX}jQq{cb;P@_ju3?ksl@G~11~cW%JfDPYrS`?z^5)(2VJ^;5Aw'
    '#<g0l^gR9bbyB7MMY#uO^BH`Nn4fWBTjcZhM-KV3>~BOfv1>w=X>QR6R4mbZamJ6{IYxw^o;%KaO^Zx1&YGjcHg#)vvX1DYgF9i)'
    '7WOqaN%n^K?$W-Sd6lkE4ZL634{D=*)pq^7C1mF&(>x-d$bJDz$k4=GQZv85Sm*GOi&1eIC%NJZ&n9`$@_uXfolJn{^Zp#DNa~YJ'
    '{2(u;t-j<=McZ^p+Or|_QZ|L%0c=>(FHK1PuwH-JxB7|y9?jXuQ!`rs$<VjKdl!;Fbu@DEpW657ChOIHEm!M2I*h{RxGup3q0XD?'
    'PwemP?cmm=AM=RTar3gFbvZ<(bkWll?tgEbo%?dFJ15I2{5nQPLnmRH*%}duY-8cc?P&Ke`7^<N_G+cO-k<wTrJy}8??!Bs!-ug$'
    'jiB&w_E4!<K%d!%NuH7XlZ``qiu@w-OBhi_{Z0AatQhI0sUM0x*@kju)|s|TgNE(Vkg-P5NvY+@-`W?&8(mk`D@HzRj#zK$uhwTV'
    '-OxVVuE70C&$R%z-mmP{%mH#uJuTO|Lr7=(xl&hzaz%29*419N{=}ek;+W%CYmQ&dOlPR>EVf}cLN5r!Jj`=itkZMuE{7ipo^IOL'
    '%%`{lGMrO2WETk_%xL}UsIyPHC^nVK?o}5uvaw--I8C1Dj`sB|ysAiMy#$a#=2kS<BmZ9V{3&FDX`Pu0dcWZg4)SkNF^TRRgAk=G'
    'zhEB7yCwO!#*dCQvV}ZPP+3u;QWLVT{XIqJ>{Xn0orJn_C?uO?8<cM$$@w<El1)qdD03yIz~0SuJireaLp;%4%+nS5qaP}Ubw%*^'
    'm0-TGO-DBnR#G5se5hd7mB}9}Zn>gXIOrB{W`eW+DeTUV70sw%CO??;Cs0{jvOg-)r|!p!RIWJvP=Tx~jRow7->qWO2S%(w<pIYB'
    '_K2aMm#CDf>=U|o6OC+OjXlIAK2#ucrSVAE$Rg8z!~RIIcepYyu<Qr=?E24Yep?Q@Bg?+MEnmB%j{5Dsd_J1E4~+v*2|51nBTo9U'
    'qMIwWKU5&=N@H{kG7=#6jW57C_<bd)<jPHSc!A^8v+3DBR3LMuu`BGEMlM6g;tBgbo#p#DtN=?I#et7pgE)uG?<;}Iu^0iJ<3j~9'
    'R~o0VyTeX1w@@i0<b##xT=6rfbwhIUX_@zu&;#<4gsk37@)J6QKU5&=O5-e%Km<aCXJ$Wfh02EtbFLiEMu_(p%ye>&Jao-}s6ggQ'
    '<Bt{RTw(rwg=~>oB$LmGv&W_Vg51f+3S_P{Zak6|T<u*n$xr~9#z9vH^PQ63yaAf!$U`Ls@<YveRHnG*hYDm}X)F-4zO~8;?EV{3'
    'KKB!JAXHJJefhW5q_XWvh3+tLbT-z+1De){3S_P{PDBr!s^lj@7o31x7NMiwx8R?>cD-k^tMf12(6UR?FWs=CKHukDIr=;KPe)W*'
    'n99-KeffG!t)7Pp(#f;x+-iLxkVkMC>p5DXl4_pi=n$FB!4tPrBa)Nk7b)5|5!uh^5P4gX{rsVlpDXlt4*01zq|1`UZoOFU*2yXW'
    '4^Wh>s@`U~ds{t_T$uvL99=Dj>u-|hAu1GD-jJRGKY}!s$cVvCi)lz>fyxhb6lqi!4|*|U1d}1ziEgPz<a-@skN5LYca)r9Bc8?_'
    'Kh_n(V^4L5JJDU0mkQy<c*hmPSCzu2?n7bQkw!5@i~$ur)}Z1%61sM_G*5n1sqM^N&m!H0M{D*}&-1@l>HKf3Bu=?<p8WL=a*;wk'
    'bn;U;=-8E0JX_*f4evR>W_$P9L)WqF=susIb7FYguAkxyD$#Fmi`Qe^QGeVQonu>BtUBxRy0ZA;dHsA_kaq6a$|3)bJ1%x#x+|+E'
    '!7mQ9rU^Ry{B?p#<5jiZ01tjqt+`@+Wh%*6Wp6Xxy@d}nuTcgxRa<w<GV;dva_nQr3OZAI(y3*rI=x|sY`VEvPdd9aTy}a-&aPuE'
    '#CqP@W#I~Sz&c*y^)%8ESIP=huIe~k-Xr^4pi(vysEln9ddnXFy%x)AQX4KIaGiL)g1)y5(g#=Aez=}MHyQoT=Lu7R%iQI=_xq;-'
    'UB`5A^EyL?uRhNph^*b9GS5ZloBOkTSb_;|cR?B{g7*18++SBBOH+v~&G}rRTjBG9+{6{UDLyaqU{Xs|z_tiFm0YDdF3s1y{H-gI'
    'GgQ`I9k1W-Qi-hZlbQ<T)Vxos{Z(CoTnSx~Z0=9%`|{qX_>ADgn&(%=Wt^NI@>cmeGuMBwM6NFHc^O|lp5nv!uwL3>p5P;Yyx!&h'
    'W?fv6uFyF^dXIDu@<DZr++v;|pL#wo>qV`5IqmDM>g)SQ;<^%9kE_s?$OVr__C9ad^AL%vO62;(e9(CDdaA|M`lk2Q>qT6@&-nd*'
    'SjT)_<_gf2w9L5!BvVuf!~P_@0~}N<R0t#Q3q)h&$-zN|yo*F0rI@ZzA-qI|aDYx-X9c~tM1?T&RT;Rzb^I#T91{2&C<!j<;$KxF'
    'A90^wR3aa7pGzfjCI00~<iA#dJY7vq-YRt)vNai*5FOTs33u+O1I8`JxD^e??SOHMdEGP^w*$s4#<&#?#_fP{i!p9RgK;}x++w|6'
    'q+rA#8@|OEwE@u&;#{**`;P)0G|ZW9*JQtvpGx*K_;kv~yDw5y7s}ROfvp>v{HW)tL_lAXpEfR4SH~?=vMs?WA&-JPwbzO1i1<-n'
    '0k-&2qLUP;e&oZD-AFdpewNg~j(<30M+<A;c3@n`c+O<kWk3lhU%UMsHX|cS(%8;MIoAQ4V|3f++?mSgx~Q0+pkki%3qAKLd`5Nh'
    'r|tlqH|4W_zZ`asjM*+P@h%E_8=Xg22v2L+q}@q%l|Rk|`6T;=S<m1vA^VRzLO&k&A>N?k0T51juW32`BmW!Sl0zUXm#FeZuCr-|'
    'w7$qj>CR02^Dmxv3NLj$68uJmSE~)lIoLgIZ9+ZD_cwn(UN-2CD=k-Oe<Vv(lmbzO_PGFJERCg!V=)rSEMug$0?3bJvZu-KGJdPB'
    'I1Z|2CA@V!Zjn4bRvbTlUvYf;uHsnfJUrJswVlW*$<MK=MD{H8&?_c~$g;^VH1$5kbS5j#7XZPz@_=N3y<5;;aQCr65)i|j_epn5'
    '>z;gg@co#&fWH`D=$r<ftnC~^g|P1U@UwJ=id&!jUehUrZsvsLF?~9^GFZCp@0Am$JdW6tW<SvT$C(q7jksDe_ZA}nA9UPhsuA$H'
    'Zboi_P$kg4_}-Cl<a{>dq-&F$%#M(gL&!<jCOMfNAt#5Bldiqhc}raZJe2eK->(3E(-pwg*MCa|u>Te<gW1qO{euc%@gzFgbp@~x'
    'fe;7bH)5T+3seFhGPf&6jrc9|Uc`iMkomEg31=h%SFDutl!dX_NasZiR^nMWE~^j*x%EMN^f`;AI5h5SHcV+_xOXH1#argZV$>Hm'
    'jkgqlX0g2-6~njEJBvvrI>MuuNgU^dqS?OVH>6IcTNKHD7SlUNrhYAEFV67ff6eBVGs%1}TV&2W4W?qbAcG*-idE>WPr>imgK$2J'
    'peM-ePg4NuWe%y2saU5@t-{A_<2!p1HsaBB{>Z|+OpTm#Hb}+it@G(bw%xYt+>1d^Ja?Uwk}}IlPNZ_16$^JL<kt+HMkncI)r-4m'
    'B9-m#+_i`f*_RMpFjiK@ZUGgtAGx)Nx8g8!4=R2Uhratq6W@zQxNl-8#UH-=Ne&xvY~0&)_$FQ#t|f<e;>GtIF_PkR@;rMq7o<)@'
    'F?!72?mU@|Dsg`D;?w9=d>wh?)96l|d~ceKBk`NS;41Ok$y21wvhI_&X~swKNqV2Nv7LQ-@zN%Vgx&S3EKymn@9kysCF>t)rju@V'
    'd-Ae$5@+|)>!y<|vl{PCPJYWewbxM-Cl?FfmFdV4mLG71v+qYTZ5;RL4^Qb=M}*?E2%YRHbi^WXGDZJ84fSXHkG~JT`R<!zuD(yN'
    '{!Xv{>F=(tGy2i_fj+j1ufKQ2lcag|KOB2{Lb)8`RgNRltLMi0PkoUoAD@m;q5hXLWsAUZ?*+mGCtVEq{ZD*<`TlNrmPH^=c+S)}'
    'JrN$N4+UqgI3uPjHIex_ZRj_l3yP(1a~X$PQig5yEpYZc&I-#GBb}^+Y~!{)6+)4<DmJKe)Hn@Is;hQk$x2hfA&?EfU{AYO*8}?='
    'vhyC@+he>5mEzM8^uJ9-;Xq%DD+NgmAbN*tyG4sp?{cKGX+5?XYSDf26o3)n3Ka+KIN)zb#g6_v=y0D1PYtd~TI9hJoyNQuo~i9A'
    'kvzQOy`sdW@lxh~u$VT8KwM$#tU?nxrt8Mc-+)F2eZ7>g1DrR;g=pON`7Yy|YxYE+D-<v$Hn0xgudk0E2|8b7m*-41tD7D3e42`f'
    'tK;eS<{CG9=IAkZ+xH9^TT<~kW*r!8ZMg#GB<9G!!iavK$CTEH-L415mO{k(@_t-d@IIdS&CwB@8IISL#dyxNU9WgHRGTE1-#fOi'
    'HMd%rULZQ(-k9f%K}W>VR5L$#uh3lYdR%F(NXACh*dk`l0oxK7eRAb-)D%^<D&**SYiVI`FzpfML?-6@jrg!n(3iyTm1xX8z8*b?'
    '9{;QHxa_a*u9K^TdmQz?!G6NMu^!`Z=ULxRuS4I#d5n{CJ-><D&Wpo1F0hVJ`O>}@_8;&nT<&Mn<ArsC@k%b(_U-!6meULttl#c`'
    'M?c^DI5n}4b###r^c$k@x!zZvb2YwK>*VTuz21NepBZ_S3o|Ys-cKT`?=e@)WuLb5oai2~EcSmeK0aIE_RQ65j4PDe@$eaEw{hR+'
    '<^4Is_i>1|43e9x`HS7F_oQ)|@%&wl6K6z8PJ~&OxbNR%K32S^F5_re9cdl{BR@rc8Bda<&E_KS1Y=U0^*8{wLo1gq^0So(qOIV6'
    'm-E-_7qVv7-p6<Foxz}LpNrn-JM4A6kG{ba!#bn!H}|J&tn_}znqurB{a)FZzSn6GS;bmyG393B!+O&k2mJh(dFFMA=bJeWWAd2m'
    '4f^1kBDp?ukpa6}7w8f6*#o#9M_Nm~KhyR&BNMT9Z1W!P>-d}J@Y{9au~&O}etrCN<6g_*%RYSuua26va`=58apWd;jQoC=V=Oyk'
    'jjOC?t=>W8+t+Il*+FDc7wvV-b!YxX-ZoeIO12gIM&4Y$M`bnkt}8C*wevBtXr6{vey#Ud7G9p;<BTKv!zAl^jUjAb?ISrd>m3y*'
    'D_8GPV8*dt{YKwxTe&Xy{@7cpT~8_S{!zsgW^H#3{Vo`@*m66~z{)0;$UeR=j|XQ$?GeuZ<+`Qgyxcb9+<q_HP6pB;BsUA$%7Y*7'
    'FUPS%bQ$`;yiU6HjJ){q?-_S9Kt8(WI^JbpY8<bhy*J6l4;&%*2YHIju)N5vpS}MH?~i@;XXA8ve!=%c^p7hSH?CvHW?%W7dFFN6'
    'j@x(NZ?Eh*7r4&a_M!U-jB5%U^AS2$zSqaFUj)WYM(7g<{w^vBw7lXBxYnOoYd@OTCUh_B9Js4ZLC3JIK-Wb@$W|2Z^1;<v+l|Z{'
    '0Uap?pEomDyBEFd<yZ3aoAvS&xdA(O<2hg@{<GsQ`f}FFXV~w+<$u>dAJ+Z*JiUJpR`fot8`$eJUa#5da@^1KG%`psJE4;JqSvnM'
    'jqiSUM5|w5!@kQsdcRgajgZlUy=Qy^0X-p&zJYxbT&hG=7_j~nB(s~RcD)QV2EmN^2Qqu%>rS9l&yUuN&<hsr6WFQ1$@jJ2LHmdH'
    'nZ_dd$v$q9!9|ZiUtoRWx$N{;?{|IPyBuYGb#*<gG5*JLk>8{E&TbN#A4JX~vo2bH!__jD^{@~Zz3F>ecYSMriz_{T#UTXDyNu-V'
    'Wgoj2`vCI(U5~RJjq6~3JdIV2G30D4-D3fLJ$RSnbPoahlfMrH{4SPnPsToRh4vez!M25c5c-a(U~aLXS@#LP$GaUm0Velmz!=HR'
    'Xh7?j)^$zu5|Rv1z=Mf8&7)=Z?Eskl9oy^Rc+Q*&R7eO^Ka!k+UfcTQ_YLybzIe7hu59VpI#cD?^`LlW%(?;XH<AstgX7p=R^(SR'
    'v--+qOuIop%I&FDs3dCj9{d&_SI8gon>%{lusxrFinWnp_G%fw^8IfIc9DKx%m>+Z(xvaszQ?$dox{hc@7Fiy>EB!X=ez4Mc3#I8'
    'F7$6}FY-Qsoy7i7D_^v~0DJYaK5(B#A7?7$IrHAJh4#-Gdtu|gzYjgf^>gC-c;CzU(&#0cpZ0y5_{y)l8lMdN``hDFeh&wBACEWR'
    '$2ZU6oA>ecddB%)M?cT7W1b)PgT2W5#(^K$wEi8i8zZtOVRI`p56WDh$D5xcZ^!%ndV(vr%=_qZ*5i~nX$X5gv!@;Gv#fa^e?8uk'
    'D{|k*-{*{hgZ(Bh^QVvhVqMKY{rzB(-7xOJhJ1ft*UVq~aeiQr>-E8YWJiyytIxyxVtnKG_1bLO^&65s`0f1Yc!_v_-^=}QpNZwZ'
    '`&To~p3Zi=i*Xkw4#n%T^><K}t>wiCzC2wASRUj*$n+u~QQ4)jH8zOkoA^*1YX7snu2~Q4m-GES{$7tWD#FZjlipw-?n-aNh6ktD'
    '$&8cs2{=>Su}3;)r7m#`BhP7`Qln24{HPi9G}#kR`Z*N8zsvCnj<*;+X}c}Qv0$!R=Gy>I>B=|y$-8jyu)gupx$+*b(*A+At4Ys^'
    'rah12I#>2i;+S{i;~lKQ3?1E0=Q6M9w{Zj$7ZK1S%u&$VVerG=d4aTE(lM25eWZC<%ss(f0zVMzj^hl08LyulH*(l6kQ-wQ^Y!Jg'
    '?X8QS@~s`C<<@1s-s4*rKM&Uz@Tt<^632rclpJ5edc9!HXuS<T=%O#_nuyPUJJsC3<&jmMrSI!>P;uC4CbUnD-wMA(#qf*id1zi6'
    '!-Y!EEbMkY37#*uGlc1=Cg0zj-^Ni5&oSFdtzYZ1Kc@Xl?-JkDeiz+iWVpCi?S69K<HnbGO6#8q9Uob7{3&lM0yxeTa|}<|q3)d0'
    'nXLI#{?B9COlPyDyG#EOmQD5%%f>qiC7c^Ew#7h%mG~?iG68MzC3ANow#19=-eyBf>>3)K$&L7A`+G$1RTg~BmMdg}0`d9D>8b&F'
    'cO%DY2Ft97QPI2*^^H4A<3jv?a%%ysn999LM`iZ4CbwXmi%*%ivXk4a=X<?$@=4q!eqg7E+&lU1X_`8L^p~gUCJ)ZON~e9t@B3d)'
    'v)>$<`CU18oM|1zYH{mK-QYnioqXK{zuPP6e7+0r!~?CnZa6rpLtegwo>)IQ^-K8NtVO<0!#dk+^WU4WR*%0qf4GCO{j_#IRf9#g'
    '{et4~o_M~`?~Za{XT3t4<x`e#U2=|ov&()l&Z42HLU)x!v!*@(7Sonr?%dC(I8n``Ti?ZVd8msfjenEBAB&fC7}_tHd!7x2{A1yE'
    '<#3(-ad5lM@Q|KvyrCK$)APM2{n4BJD!tLo=tg{9c;jr;wZA@lNjU0>uV2dKWptZ;J$aMS=>GKe)|=doPNy5`r8i?gyIFeE(^$%z'
    's+?8hVR~~a=jnKC-`slhyRkU^7L<!@yt02gdJn}oJ$0Am<}iM3x}o<u9RHSm`n`OL6aQqtc-d33&U$y{&PtA=e_u9t$#3>;<{h)-'
    'PTby>FHe(D-j(Io)np>>obu*wvd-?mmN%($GFUdJm)M&E3#M8I_-y~BPlLc&ENE`#fkP_lO)d~d3>-mj%!vL@rzCRc!P{v0j%DM|'
    'N$sSb<1fjTU$})>8XTNSF!diuj7>C_jXw*fV(w4r|B(6=H>5rmbN}t;2^cwa|C#@$rhzm1Oy|Wuo(GsY4*m8<&y_1++4!C~Edl{7'
    '8=ZRkb1a)vi)Ewe-z;#dRWPOZa^%*ZrVjyQ`q)W8&rGK;gY0EwdVFHAAv5cIg9uQ_7&aA<je(V+ex^Zu-DkiI1+n%}fNdb%B%3k@'
    '4rA1ms1;hzBKp)AIKU!N{lwIQIhL}4O6j<b6_X}R@<^JV)Q7ubT1Opula}jnR4HbzN-Cggf5gB68oUn#HD>5R?-pr%&yL5rL@o9i'
    'HSun6jrq|W4RSmBwXU#n$n(pM1*9W@tEoX%7mRAzO9mQ!xbHGDUdw8+My<kOUapgL7sbnxWKiB5eMS;)Szmf_!05d_j>ycsC<eaD'
    '6v)v(!^nBhD*YTIr?i2BUk}lb%t+x}Z;uQelIMt!BvFylc}<hjc|m|0`m{TsF$lo!hRhE<c39dOiJVfVGhnmOxCLOl%GO{Lj5W3Z'
    '_nd_@Mtf$oc=WU+)2y*H=FysK{TD#|_Z#}2jxRNaz#vqs2d*uVsD<8=rkz;%^KoD)^nAHa$vtzi*RdC1S3@u9h<hvL94P6-mVIq!'
    'gZ0@R6!vz2tVpLB-e!~9_rc=OoWmSZP_m2z8@(!VP=cL-tX}jY>t6c>YMjENSw$M7XTjJb_*<jw*Qk>hesdVn-!ykX{|1InJ!3>f'
    '*~~JDzYkN?NR?98-uexqY3K<+eNZUeeHd4&7B1NBm8r%3()~7L>vBd0kw&m(q`U^T71BsVAWaSJVG1@M`V_@FjCQ}Y>^|(vNUz^o'
    'SZdIt&v{LsZEqRR2eVCqW$?Q9ZH79#YxG6K+S$c=GQGo?w~&rSj}hv`UtBQI6tX)mBQWu1npKp0^1JA5UbHpAd5&z{(;PTHzFN)b'
    'dkIgYL?i{#&Wx-!nSl{U3Uv@w=IU{nhO~ZY&C-1<<<E4lV4|6ixegRe&9T8S`hfisa}PQ9Z(u*UBj4^$O9gcIO0)Ztd_iv}A17kA'
    '$P4a!=`(W#(EByJGQJO)rNhj_lo>W8_Dbk5YCqV?!7`+o)Thj(j#?*;DKgXdWfaI?$)W2^K3ky0n_(fgyD|W)YY!-j=q)@OHffSO'
    'Qr9thvL2P924fjmEOcfA(Fhe9luX8=ihcXwRGbk#0+lxe8hw!h!vJWO?hxp%#R=?FEVoFG0?P<`!PShh=#8_x<HBZ)pE1`_%3r@n'
    'De&HmjUzp<soQ5TvIlJsTb3en2``vFl|-*jywmp|`rHf6J)yJGf$Ti!-g$Y3o*0`R$iY<)|L7;Zor6-LhnjVU&ozim?fEPd&)g$V'
    'GI1o(|A!t<)WGUq%_;Ul-n9F`taHdqSqw=Jf!$}>VrZ0hGt1YBSD~g*Gl@fAkUT!mus(OdbW>IYrmftbF;fwuv1I<m^u6TXBV>nx'
    '8PJ;nKWVP#Z=q`j!P0_xz<guxL6;c)sM%{1ussBt$>f0gNMFl_mEhh!u+20x^d_T6G~%9e+tT}Wz48Lonl@m8ctOt@#(j}x2SoY6'
    'UO5sNJ070}YG`TAAk&5jf5ohPq=RJvmO!(99IlSgRS%^=edd9g)S;)CF$wy74SQsR+Q1?27t;G?y~GAPj<K`YGgnEVGZqO)NL=6<'
    'Fyqb3oH4i1b12cPqBQ#-(0{>t#Cl}a?j!VC(R0pXW?Z$6yh;103mt(SfZ6zLj8&LqDPwUNcD}!1AN{54jV=`eCUeQ2f5#pI8_p4o'
    ')1>j@vW)Z^dGgt7x2?4#{oo4IqXF4RGEOi%D1CxCVVWysfLGI&_4NZL*wh6UfY#@BE4OB59?o;@FYZaR&japXY_?$0jlp(9>pA%#'
    'ml%)m7z%sUVu+!CS%M*lBZ2VBQQbtgmbOFh&{H<j{YzFzGIyA(g7kSoa$%*>mH$l`V#O5wYQXF(2Dp9&^mQQ4Mqt+HOI`b2kv$B3'
    '-Ulnpgw`{#t$c@Em5kX<USNA_EH-8>wxJ&q0nCjPJ%h$(F{tRsPBSXH;GQ(FulK@frO-=9x<DQ$e$Sm&5^NplQJYOF^m#TU7wyFm'
    'zZZMh5!-1VfjJKK;;vv8-=0f0U_5f|eq7qc1XzhB_YfotVE<IM0z1wiAbT-8Ardx1ZEhe??EpEivEmZHK`(`s{6KzQW1tMKF;KEM'
    '^vu$JLxxZ#U}p)mJ;-)~&n$M@p8vr(9G2yp-gED!YzIef07g8>D0(+MPfGSM7+ZnkfL^`@*~k;fM3PtBk4ydr$q9*GzmVQ<uJ1o$'
    'n;9s@c}g~|Twp)z^{snC7O12{PYB6p^gv9?-YRhI<FGhc!yGIfwj~7W3FSujl=NmU*l_Y3J;tmDhQZohlvA*>fSn~CdSK=zJKO_n'
    'p?&apU7S$SvT%_t66o1D0k89ht{W$GeNXo`n;s8D+_=X>FxyK>^G<RTtTF>yZ}Klb$Atc#(0jlh7!)ViGsmbn(S9ZS;K%bX|JnRw'
    'kJ*LMmt8RG!M)V$46Kkq2S?8Xy*K$oN!Hv*jkVVRA8hE#?w}N;d-sA_1zl+kwA}i3JWLNuM6wAzEWkpGR-<4&TjnY43tK>^jRg6u'
    'KVA<v*l!8gaLA9FR=v@(TF-tsKPBuOdFL`F+MaCx6bRbtC+oLZ{$gH!JpV1L2eLoVzs^iDYy1>Uh#2D!43N5FOquAi?FTv%9is}='
    'ha3TB>kd6Z-0ND;i#M`+rTwGlO#`r!39u+sWGlImw+<N_4(vNskK8+1fF)u6llQ^8S}?oVkN4Na$i117CqEl6y1y0vjeQ#nU}E6B'
    '=7!c=k_ccwUe-zIq4z0wRxwz>NT*Kmx9)Y43-nk9>jdu^?AHErx5s;KXg#_s^PY<UsO8hu{BnPq7n=7;7Wu#fm<z-hPKb$Q?Rz;S'
    'N2cg4t7H-cYqIsHGhUZu*Ckk&T0ijhY23m^MaN%Xf7h;qORo)Mw;F7Zt+C4tw#V8XU9de6XHcUV`^)Tikvy|+;GX~!b6oC$O{&*l'
    '#Xa@~sxO&cQ?!1a?2olyS1*4if5^U{>>?MsbqWTnl9@zTaru^{)!GIAC$I^)Z?;s-M$YT!@5*EP{k@lo^|k3`VivqhFH=OeecPi1'
    'w#((WdZ$duo`+tryNIF8eyE4EJqk=*(jQ%oiMw9;!Zz#=%^`qI)={5s!EV)Ad!2G%jXUc0uI!wL!v18T2c5pR{?fShT-ZvazgI&u'
    'ZWDUG_i+RJ1KHay`)x%6n~O1y_hc7mvkB(7QsK}={0jImd$2Gh|7e`cX$(JOQmze_?iv`l?u_wf)C}0QBaMFmECGLVjbWMFa=|em'
    'FtY*+_&coJ3zK%pHmk;%M32wJu)i$8iU9VP%7I>E{pJHh6!F5+ruT?q+E?y8=lJ0Z{XQF$yqT9IZ>r{w_8Hi;kTJx2kzd--dL~~%'
    '_m*KEHa@B{7;A~+U<vy57mz=>T6vhC9JV0$A+r9^`}Bw7cnAG3$G$Zf%}X%zqPGi-ha_LT%9-(X@*eb1%-5;FLKxvXvjv`e7x{RP'
    'xv@J2+>2`CljM{H#slzQ(0gj3_Y{4Az=kFJcC@G@dRh57hroobfKi})mKSvWYq>ln`L$sArF+g??p=Mu`H)ZUBmm=w1G#ZpR!07j'
    '9WsM_0(P~zo^SLd$xo}b6QPe1ftXi@IHv7ZEp|(e9?%;1iOGL+Nd7W54#`3K<Z<Eg%`;$1upHFm0y!A5{*724reNeo+{hgY)ipha'
    'He-F2_6e9eW5$l*URcH|CBL1nCoOtUdWSc#hb$1UCi&KP=)Gtkoxq|!roTgjl{(KRmgC!lYs}I?i<R2ZY)!roEP`ngbZi04IPq*h'
    'bWAUKQbb8wHU*8D!H6ByskQdac!w?atJ$+`FQ7LV41pdq1S+t}&suEG5m*3$|3>c<dyM;leV4(<1qKBAWq}_}_Cig*@l1Dsa0Mv*'
    '4Cn{o2gy)Z{Krm_Vl5>hS2rTg(PF={z00h0kW((}K~$5b$Ivj)jLDuJf;ll~AD^zPahu4Nvxi_A1D;cnk*orKa#I8M4*Nd7wiC2G'
    'JRyECWM5y^V-wp7zsFz$)}`*3%`(KQSnp}<H2drp$k?J<myXkVp4p;EN1hgRUy1zy+)ab=_Ot7Qjr~urPj(l{!v^e)V?lmi$$DQ`'
    'Jdk|~MrFw8U)@Ld{fe5g{jTmu_U+O1o+`*nFt$XjuN&^w)xGd}5|bV#JroZSSJ8Gi;`#}g90g+;V*cL1KD3&_j`C;@wB7kbc|X!U'
    '&|NS#lRpidmLuZV@9*EhE=NTHSb1h~PCoiaY(lUfVcjOEXpNl){g%)L3UlulHe-K=xy<|m{o(MJ6wVtVgU!{mh=X+ON2_@4v;NFZ'
    'ZrHJZ@08ELHjg1!X#ITZfEBPKKlO`OU@Z>%+2kxbYS2N2-c}9!+4C6~qMeWHnf*7?FDuxU0ob&2)=6jbm%EcPVwT&)lU4*j*&|(F'
    'HircAgX5V|a;-mq><47<uWc9X-C`foIz;Sl(b|8I55P59g6*ubM+?|nUIX@-F0Cs8479-9&*2{B42(TLv2S%xcUalQoH6<hCQ%@Z'
    'MV|G;j(PyL=)hCYR{naV`_R6f^aqyxi0^@&hjDW|661AnEIS1rf8f!$l;8MMX8+Usb%R`15`KU~zHTANKa(%O4PyJE)er6dE=4~n'
    '*FMJgC*u_Z(*XKm@soM_)^7QQf5cdDzQ-MBz|14PpB_SHFG5ZNYg*&a(|yliIVAr8a*Sjv?JIYW*l>4I?ze`C{utG^yY`|(R5#&+'
    'w+HUuVST+GcA2})fU$3PT@QHOKk}2W;yaZ<d`F;9dM(ylQKzxWq8ImzbRWgKD;n`HzehU{^MCkUhNbH}EWQgjL}o*#6<SWSe3R(G'
    'XFtCb3D~bAl6^mxn}X%53*3Z48M(3d4Qu$Mhkal*dLLM7F=YH^+JmG+CIy($5my2JX`}H^$%ao{8~YVlLQTSPZ04?5>AVPy#}?Q&'
    'jI}5kZ)n>LdfBI=YpLaJ{#pmy=DDZ!(95{!)FV%R?H3tXnn@Nu*Z&@U0llyO=ofUot^Iqid^jeS`mJAf495AXk99xBy7#~~u7JIT'
    'cq!w44z&(FAl4p|Um#8V;7{h4vHD;qBw7x`CTD!N@fBN~@n2%cgKSOTF{vGOp!J6_Ob}-$d3_9igcXR2GmVk_#QLB7M&746$Jp^4'
    'j1^3FOFHK&XqsPI$CLKG-;d+?5Y1cP$2y?vxMuzPIb&nn39uA0#Cz><=<Uh3y_S=afE-E1IyUy8WDHu8du}fJq(kj7GtZG-M&l6U'
    'd|DSi>nGVIc~5)j#PZ6l$1Ta_{vfj#30UYn?nH3u(*njZt-}{EDW_R)G$x%3yBl^|>g_lBy6OpfZ|d!n@h%0kpSH7sc}ee0bCBYF'
    '#vbAV8rz%Rr?2ho6m|>GFR!QKg#CSoePHAt@+2p$@3BCx(8xdd86NPZ(teyZccj1LK}SCHv(As?y^rUmaU`2Dqj8q}ykmO5aV6mM'
    'Nxgn(57GS{V2acFqH%(4e$ZSFq#Hcohh%-4W0G6)O!~te=O@G=DghisI?f|`G|KgQ{Qod!_}#K-tbk<bl=F1TS{8ek{04VgzIV_8'
    'LtK)N$#O*d8TP#FZ8ZBMFfE!bu&mt*IS1raIi80K#;wCxsKDd4H^6$H;ynsfG?Hx<G}w2sTQ+1b+B9CM$>~_KV>7Gr&}zQ)iq3J^'
    'QNLRn(`?rxJHWN<p}|O-(D<Ea|H*xsPmyPt&GI$axPc>=z&>5Tf2tbr&A`t(Ex5LYxvN6h7GT93?c|B`a-^fd{;l(DSuxi6$McXe'
    'WSd{<ty842uiy1mapJry%l9A3?R*n4)^2Yz*x7|D)<wLt55R_%fnBVMHL%l*2l5BvoyIx^mI$zm0+O5LYn^?tf-+;Lk>M9MQh8#w'
    'cH~{iPon1sW?wSqn3kxAh1?9d(~R?;7tD3Y(NI_2&d6^C%j3#)UZHx{6}~D~RTKgnd#d#sSPp@+haBiZb0~2v%jD1Tn`-?=<W-NT'
    'gOVgiQ128YFAsmyRW-+)bLKWe)$&X;X{!V2zm4t?Z^FoxtLx`RCm8B`$hM&M%Gl&H<fCbyOO4swB*0#b$ZjP&HjXOA81Tr?gONPa'
    '8252p+4WrSm;dSaF<A3zv&#3|pq4Y0^}r3bo#xXmFzD%b`m|Hn!CJp(uz8TTJ(xWV?g@<z%y>?ichyJk^cQ}86VVFvbKCIl*dhFN'
    '#u22o<}#Kla>%NZIhb(KNyKOo^j`Ul_SFhZtb<Awvm#<l-v#Pv!1#`RSn2p1FcR<b$=T-)t=BWzV_*73=RE8*zjxU7ksH^b4=`&w'
    'YIm;oox}M&_=*klUm&jzc}lY6XMX;^1MJX_e7!B64;oAERG65@d343Mbj?A)c7@I-0=pLe_Grl1iiqoq;!-0+_7v**yn^%nG3S*s'
    'hxW(bodQd+TK~8B?H+Ub?MeTD5f^?SbE}|Eg8afLL7mj1$dQMsH70ultWmH5AC^TvqxFBB7rj|4Xa3XA>qDO~mQu5Q$oIhEoPo<u'
    'R!Y&|8!)FoVErRLr{gUtI7R{w-Q_8sXM>J_i1t5U-vfS`fIdyR+d{y;%E0~R8<tk&*h3=^X3h>A18c?<rq4tMz;x=xbpLv4<iVn#'
    '=h55)Bsa(p)|ilF$Jnm)uvP?off}6vq<0rd&i2%Hl(YTx1phG-z$Z?zb_K16O<Ez}6os>&*yY+Ez49l1<d0^~2H4a~=Ar=Y=(+&z'
    'KQO}Gz>Zhh8r%o*gRXmR47OUm<St^F%}72)KG~VM*wEe*K%E#eCfJYa1?1u}j}CsVR*L3nP^;}G-yeh8UTpGp9oA|?pNCOsA2&s>'
    '9@Vm|%6*;GP4|&}+)>z^*X6n%*UfpOIT!`70l5>raAJ}>)r{oQ59$|Y*YS=C;vI!^9MsKr4fMrY9@fR4d}q6OES!U^RlR2Jh5g82'
    'oFPx1BtMBq(fhhi2|Jkl1+tA&vaOP<ai@7)(L9nJqF#`@8GFb#WptbkB$hrpdy+hLgK{r?w$CHi&r|R)zK{$`;Li+;QysBi!+P`>'
    '8Vq=FqR5>ME{S5evyb4uhyokf@btS~KQI@kuG9Fd@mgBrTc=jZe?-1l88|7nW9Apw*P3%gp(ciFpum+lDxx&mHQk4zx0SoB`%p$j'
    'T+5>6teDX}0wYf|NoT<0w~#AK1lc2BcwJ=6T3KsmC+BsV0{5Ez6}>J`0`@EFEs8f_Qr|3~hmlt(-+-NLGX}BOn+-^oEy`XRSHL8W'
    'M$FSt>;>vq7QveKb?UCOsP@YY^)oit;t62xXS9#kKt^4yX|3aPA)?yZo#^<UqQBz@I)ApySL;f1Zw$WY*0|1-ZYJ=7N@;RaitG7c'
    'KkFJo8|=_VF6w-#=8H-pS25Qs(lN-@;rtKsWB&K!DBs(kSMu7_6QcI>x^A#;xm-|h*K%M?QR{>{HL^d*Pk=uaqyBJCdL*h^&L9Q6'
    '!Gz|7?5v!*V!#0s8#^HMex*;|IZ1Tf_j~<e^gi;kC(n%2@Q3lACS8%g6oN}3?`^{xxU|vM2Zv9dZ$r{E^gDfWo@_S#Px>bx?Sh4g'
    '1H9V}nmdE*9uc4O$%im{0d*OOXZ925vhviOWGt8Z>2;juD$W)#XGIU37R5u}EAZYAIoZ3FdZNEK^xm5Xj0fssbUfo*|Ni+de+Jg$'
    'pqEV!g8cfs?Dc>arrR<_?ef7Tc}e5@f_gspA}`khyo9LdpQFy5Yx{aJ?a2+|(Sgr)VjPmaI4>P=dmd?>gk$CqMl3^~7o~%`y)Nod'
    'M^%sQr$O+cZnnOv`>EeKFJ+yUz=7Y#Bh(S(y&vV<|Ex~o$NBisPFk)O(u1V;nic8AqaQZ2HR-{iZf2X}?HJe1fw_c850c(HjB5M%'
    'SiBvEwIV$j(dYhBf2TWx!BP*P!?o*Staj2`{-gY`&R>S1z0!JFZWXj7>B~pb*J0Rf)_Jcc{khqc)8nXSy<8-<wAN+skkmHm>*--!'
    'tNyy&)2HTU{cqf-r)f#{Sw{`-u^xOiyx0ENmECjV4s-7v5e0buWbf{0x*m58xkGY>>|Y^QDXlYFcd3&{F8u#F^FEW`pJlPm2id40'
    '>!Y57WN0I}*41X2Dm)!~9TavE7wQlJGZ?iWf;%xo>DqOy>%#tNz0CLZXn$5eqV<CI?Mm*^LEXuns-gm1yZ2?UFdQdXf7U}4ZGa=M'
    '>o=P-V&{`!?=HxHpOp5A?6mD<hgwgLANcSy-B2d0JTJ)pep2A14!P#bCHp*mfY17FM{%Bl?NeQ^=aX()fj5q9Qx`tDU-jZ?6*XS1'
    '!UyEetK6M|ccaXXWG8TcO1N#F!L>lXMl&v6yAe3Av)39J`y_A9u4T{rMcR!zs=UoR2N&`udp=8{iYd+Wa0f1keKM=|?hKp|JIw_&'
    'WG<nU{eAc~DUHLtTE}CD>#kAPjoP-_r_VvDw&aJ`gF=AAVu5<><^Kl1+He4opTyilj5<#CA<5Bj5ZK@bf*rYiD8MNkwQ=Qtl<y1K'
    'AB$FqSCStFe~k3Q9$ZH>?~(DxBKTvQh0cem@44bW_A$_$9^1H?&ow;Se|B|$!VmL0;2@!E#)xqlK4cp2zZEC*|C4%k6rdkvzlt<h'
    'Q~}N{vUTCNHsFo|x6=bSo?xf8di8%W-!=*C1KDe2!`mx*u4F>vHY0mTRJz|!*8$Rc*db4VIwI0Tx-K#F%A9Ni#r`4JZMXG;BoAhT'
    'rc3Mb=+#ZJB|SI$(sao$J9|cNxIX;q9^&EQb-g|?mFMV_(K3HK$?b;rXE-dHv*dM*KEek0+x<b2yHRP+5}G^cNaTiS9|3`dWO5^+'
    'mmJg$6se^-^_rur>jQw)Vzr#a6X0$a%?2C=L*`0E4x%yK^QcE(1It;W-j8%aJSxQ*JSS-x#atgm?}0ul8vmou*AX?{pVqeQlMe*n'
    '0vOfroW-SBq2I|b?2YN+iHGl8%inTf!Dr-n#?a`cLDm$czktY?0O5+{)M4N^h+m?=lDV?T{@#EmW#HRe+6Umy+RiVS{ph!{&pyX-'
    'Wy?WL{u2;%Xe}0M#(f9+`_Y`_oA6bPbrBTJ2>m#NqFD{I6Y?etaIX8lJ&UX9%HeuN1)T0P$JmP~j!Eaj&mfssk5M;Bau;z>4|NLM'
    'Thx$`u$CT=A>ww>mFv*0vU*y`b6Dzkk!4CY#Gdn5@GF4DO?nl1`UCk%A!<4T^1s3P6nNlRauS-48<G)jB%+YU9rZsa@Y>Kmun<3>'
    '`}^QINea7<xc4ZFB-fi|rY_C3fewi|iNOnWK|U*NMl5rD*!G$W4DnX40te<gc6>V|dvu08%3LFFR8#U5qCApQvKL6t@ji(Bbxiid'
    'jK;U7XPd45&0JRhMy|0;$H8egAx`c$by^7MxI<jXgDhnQTzu&?hp=c+A5J<n-O$>EzvzNn)*?L<3Hik;nZq0TreuUVZrJgj4Xk?P'
    'z0Z>}Ma<w7aov`E9w2w@D%9O4iS83Y9^wXenE$LE?{mY^ls|L>%YFmrQexTQwCystj>&)h+qlwxz}e(_;8;R!sfs7r2{mbw?T6gf'
    'acWm3gDgul0wj8%>=DQFea<_%KHI5N^jfDQ^aIlv#yRqtauw$S{9qf60^BS@(n~(#9{FqE@8DTeH|R79@>9~jpCfJ>sO>z@n9~U|'
    'hW60Y1o21aCXw4Pw`p!p^&q#EN4}5FEjGzO*jwk{$OZQUE~{pOe!P<VlP&a#jEk&BA0^3@E$xLD((Bt;FgFuoT4X1kz_V~7|1VCs'
    'UowivKIE@BCnaKC5^?AoTyx|!9LqreUP$tS*7%9*FFVaw3mhXtezLgE6?M9M^fBHo%U+UrJ@im@kyD?PC-gIY&q-Bg3HUu6?tQcG'
    '5Vvxl6|K9;k@J|@r><w&>wDO%;GoQ3yMt%-49=%fM}58Kd`h0z-hDMW(mK7pFF$oB)`b(D<j6iDeeA-Ib1GXhcOl7@Ir`R7*Hq*y'
    '+Bav?D@nXlFQ^0jo^!94qHkbT^=9*3v|0w>z06l?w=U+peX`oEpO(8`;`{Kw8_Op>I?boZd#h;?h3IXWAYbFF?WAzf6MldXOm<8~'
    '^2-t)*Xe_ggM6eEcAliMMx9-Z{#tOH40Rm~=fGn0VUi9QdCb8^KAlZEH0_RyUOL`2-4)s3@X?mudNtf-T}8epY^7DXej4xWW8!i>'
    '{T8{Hs65q^yeFcnsYx%m1DdC)OExd*3*_tu$SD=;QA9cq$hQIWJOGt0MV+4vG@>w&z*e3^epHdIG~Y`Dz4gNN^p0X4Uc^>|GF^?c'
    'UJ4s`1sRW?Xa~HQ890nMhri0#Pr=Skd~m`PuRz`<|27SSj{Sr@cqG)9PB!SeTqiI&iVnC=pN~ISKYJs;ey8=)9X_kq+w!41wtCb1'
    'deT)^Z+^R*beGTThuht!?!*5wE->=D%1)kzVW*cmyNR_D>&FgrmO(C0j;if1wiNf<APTX}1oXw}iVF;KMxf4<>q3h`4f_dyr(5#p'
    'OrI!ZW@@R-FDCWE;0@4uI3L%$F$k9he&_S_@5OTW&P8^8Jz!LT8;m&*t+hrLb0U(>;QRtNVzg@SlNNh$NFC&^Jr4IV$Cc*!_&Q3z'
    'm*Fmw@6QR&Ec)Dw56_8DZKpXs9Pf~RFRtGAdOX^{^>}8`V^_!P_rvv=JFMjfgS`N*E&V=*8w_>@xV$iK7j7`WCOfn}j_m%pmIuQP'
    'c2H)13^&+J<&ohA)9)d+%GK}JT)4sTyu#hParI$*1ltdq8;q{I|8Tv_{qafjn&yVn71z-mPv8bKdE3kL<5SP4`994hxWQ)N2J;O!'
    '80-BVjoUjn80&q^D~(6?K5yU#YsWPLg6B+_b@yRDYO_ACxxw(9AD&yk&*=Srh8xWEPcjOZ=7#*9ON;dUPF-<nIl!N&(B~18U%dPU'
    'mzHpQ?y$PzAS>|qU*w`G#1Z!y;yy0<0>$Zw`wVd(*QWbqN8D$Ke#aJ(x8=_H8Mm1r8G6la#^aH?5&4zN3Vduo;W!ggb9$2hiawF)'
    '`}%cx{EFt^#|eh}nEe?FjlAvV3iVC8uI3l<4d~*etye6B&d0G%zlw)m<yRI$o`*ZpA7+{p&lT#Zxy8WqMYa;@%rx6Gw^%28wUFnV'
    'ko{!zYfbW+#(e@LxnU>En8!8L*buRsy}@Q7yEUV=FJC6`OWo!eRTtzt=4@pSSj};Zd4s-2>@yTsT-QLsLp@Q<ed*xkZu;z}kgiNJ'
    'VI`XL)%86f=bperD0P0h$0&{i`i<wQ+Na-)EBtcuLz*M$d(!{SneNA!1_84yT;j@oAN934`hz8WjfCt)#7W-sQaUC}@&bt2m-x|n'
    'P+#ILm;9RM9#iNML!MpNhaxTpltlVH@tQttv5BWFr#SV~a_?T}-{0%(W$NaWv#{jECVwQ%)WXS0zgu#8o4wX6Eho+-4>u#uv)M6o'
    'RhQ^bQ~ikjsMoXXNIz<Gd*u7j`uuX2WjMZ(+)LQN_b#So(}Y#i|E6BLrZGx_oc*t(#yC+wh`+ae6r$~;xa9G4JighEbR6`EI>rTf'
    '<#r^`^S2q<!cTtQ>5J#)7JY?e$9Pti{cnhKOIibGdj9@U>vJh#hgRrI>3!R;Szyk|mWLlfb82@d=mkNqXr^8S<2Kl2>wcdv8j7`x'
    '920mYft!L_;!9s@c_JHG`M~QTAC1-z$?F_`pDF^OnN)yMOlzxf3vD-qZj-e2p8i#SmgWkz1>h<#G!L^%<W=6}Dh_(2=dLB>Upr6V'
    'uKOZAxMW)|ic{_EbiL8P@xF3!mA@I0eHfQEYQ2#ko&ggD*lG{i`ry~iYMuACI)=AL?Cz51=l<(m6Fy}7g6wF-Y-e$qZMhzx7Rj3I'
    '?7^4+=D2d{gh{0)WT$sWmAaW`uU)Ng9J2itVy?#lxHg&5fpnF@0ieGvziKvE-@~2iFRCb>mc0;IPpAuFED)W4LLFRf`tfaylf!Yn'
    '4CvR2<|ZD{aZYstrpc4xL=B?~It6P`^pO)AGoBaOW5~T5CLM#nh1hC~>`C?rP{SqaOTYn$oGN6vJJ$W8!r@pf>+H}8^zV#t&OSHR'
    ')q2HptV%=10wX<5*B48^KkQ^RLu_VTt>Is5WMtHrp$FJfUa!RwLY$ZJkD?gyibeKN1HT1znUd?z)-mJk<zEg1%P#LZE(~sM#$6ls'
    '*ni@D^U=2&vVWf8Z$I}r|7;KLOuPrVzG=byl1I|_Tap8bgwM!+vmOV@b)Rc+5*CX>Bm=H<=KYPF4rFEF6@p|Ftr@Q0*IbknpX7B8'
    '8%x6GK%e&k+=cY_9m#CSVC?;xjsZr}3_Y`fu7_1ES0Twsi{$ZUSV)c)Pjr5{jXSq-<plMEVPR*8ful}0MV$otp|f1~HzOZFb2Kyh'
    '{1Vq?Mid~&W?*{|jFo2?91QAk>>18O;PbRhAJ8MvO^AcGc{9ux)*R^-^ePupknRMBBl@F@>1?)(eDXD8*tdpznQ;Y37nA=u4H17{'
    'Fpe1aktb;tk^QOa#J5Sl+VzO+Rp6umizmA7w+a;FTcHmu(wxdKs3Gy(CM189bfL1*TavoupU~Wz_$hNS>hZh6{o{HEn(w^Fbpnae'
    '{XD*q<#~hnosYQQu(e~swQ20wzrvl%cKv_-U;pKY;_m+rezX7U|M{;UV#*Hs&R&Ji>$-NH4L9QRYv-}k>3F@)z11G}IJvbtuf4m('
    'xty6MgRj=JmtAmZL+^Cgv!1_%PIhO$Qj@`Lr}N2H^xOMA>Gz3aZZ_%gf4#d2-B16=-+OO0O-((~fAIIGUVZ<%{$l>1M<?@P^rakq'
    '9lhD+%6IE}T~D0c3ft>@cV8!8#c4F~PVGU@-El{CNm*LYwRtKPj$iJ2U%x(H&Xb<7C#7X2p14p(W-6Jy+Lp&e5$*fYyV3nF?-Sw)'
    '=>IaOUbo|U|N7Yd^zs<Ky*%nM{~9VUe|dXZza-*o_<TJd80Yp<-W%RSJ(nkC=EmHQ+2Pu;)PE1`yYT%g%A44u@cO!*lXYrw`Y`t+'
    'Pn;(9^*7Dqr1uhEeF4^nXPW1C-b~Nxe0jS|uIBv*|EUSB1w3Q>oEVenn}Z(1uNDTSQ@_3N`#SmE+sjZqi%t0U<)qr@KfS0?=sES9'
    'd4`0}Nd}KkH1A#gNMIKH_7P4BuSfrs*S@Zk>93sZeH=n{*ZKNZU!NIXub&U!YgFp?zfSh!cMsp!3!XbW$;-m0_q*NRA0P34?fltW'
    'Gl!S`H&T3>8a-N<^XQNXUHWpKI6Y0mucJ;zOWT~+dBJ?1Lg!`O?mruY&>3CbZ*m**r7;lge&FA~(x|rQ;W;0}XF$XavXAdY&v~_v'
    'l^K`QMFimDJm%_3#@PDbWpVQV^Vq!KPmQkE3--v{AGh02e|#0sm$isJ^JwAO+Rcr1^^86DY94{)#tGvvYGsEIR`{m(Wc}4{*D$Td'
    'W*g?k`qg|j>D8*v?ah_&nuL!ot(NUuP3lyihb<g-cq^Ot^G+8c&GvqS?8L+SE|)yI_uI=BBYZUHP1=nc)$KZZJJR0&gT+MqeqrzR'
    '(fagqdv!k^gHX#3Gw*o+FIXY1kk#||_Q&J)S)BA?6CQ)RM>@8bz0bSyveDJNThF^jKURCGk$xUt59WUD-;Wm=pvUF6KOU{;@cq0;'
    ';1q^5kLG?n2PKc!T{{nN%?S&^eQW2zJDtqFJ+<RWyEc2`|G&uHJ9Eg$)6bdWKEK3HpWH#*sUPdWZ1haC_1Qcpz*x3=&D>onEgDl#'
    'yzg7w`|aiH)p=%2t<&gz|2>i+dw0D!_<oOA8+V>rAGqJ+0HgC*U+p#f!#rGlwXW4&dmgPTy2s@_`$Fn^t#6aB7R}A-?dmx{89nv!'
    '{jTH${u}EtxW3qDyzu}swB66%(`V9jAK&k5_~g9nH9&E9c(T;fl|mX}?7j}Jri7nKUF$KdwbgI0y_c)=cwIe?uFm5%y0)C`>qW?P'
    'Ua+oO`AI5+#^j0F1?+3RX&49ef97}S^LCQEpMJ1hS~(;>$_ba&_Q>J!qj&q}{aEMFxR8u)$A#AHNo>X2-9?Y_d5-N3-p^w}`f+{Q'
    '^#0$Rr{$g^T}FrBwa@s?{lwSN>Erqg#VN$RzuvyDYnlTvI$SMTH3^kS^mtvJ_i=raeBwPw*V6l)?w{aUM_OLC%7NwV;4QnzT|C!7'
    'b)Wwz)njWC*7W|9Ta2ETT@GF6+x1D;WgT&mOQhWC^3QrL+?heQznupjPyNkh-$J(PYuj4i(KYy8w2b?B%)1<<cgL7J^`zB_^v>&0'
    'D}>(b|6AADHm7YwQTPXGS~Y-!__$;pL1%<E=`=2UvusvaDWnNDQZ>{6-gEE1N)S&p3W$~V<=(sJIi4|LK3R{FZZjX6;n}mU==V71'
    'zD&^mf1o*TI7xV}hU<<pDTeDnd+lgmxZP-c&#&zu-|2PtR!!2^dFl2Qg^{UxnM7fZPC+uS29l991GJVL)(O;cs>Z{5%i-a5CMqS>'
    '`KJTAtZKT6%==B<?#}P`%BG;rN02}pl3VW1lf0e8x2D(C#z}{d_xFE(`usUMe|h}p%lE$@zK8RV=jX+{>GUrh&fU!~-8P51ex3Nb'
    'O5{LCWzXA5G-mgneSO_-QHORn4nKE`(KWR5YvbP!ITZSNRjuUgdW_ky9geiUYM0(<H)Id0v#l6%$g&x?(^0!HrhYW`UZkTAq=kGM'
    'e&+Hd#{EoNIUUX6G-~Jfe&5cmL)6aon?C14%w4<jJU_ljTU@QB8qEtzo*s=)-<nS~o|mRd$NkJzb``VN>rVH#YkTz*WKDPvz@~=B'
    '^*iCy<A*)JQpcnHi1r?;{mA`KmOHw$Rc%q-aO%?QK`<)SurAsk#A?nH5X8gsXmo!Ba^S(iT%z8p+~`g1xzX-VM{fo2{?tL6SEbVh'
    'Gwf|`!ahPgnXi{h*AY#h<|v?>!~@~7ZB2rRb`{Nm+cRQjbcfGDyEnL4D|jn|ei6PNGb_>ifum5Ke^SFHn?oBht3bcE`CzSDJ_dFE'
    '#?MU#jw-xa&Hh};)-28D5SbiSQ*CG<&FKEiOs_f|?a$OYeMgfl|M=yDnoZ}we*7&P*jLM>eta;N)oGqitX0Jp)v2W~HVoF3JY*%_'
    'e|HcwNTQ4^tb5whodu<W^%N{88LXx@TgmB^QO<|cp-ziFGnUe7(P*}kD!~>~@{~=w7i%36t*otOw6=B*Sw#nL5s6jmtRcvr`;6r8'
    '!EUYkbeB*+^?}+T?X4Y@+p<lz(7@`6EuLWQeBE6Z#(JT9T}<kxm@hS2-rQL>lwL2E?AV?mo2JF}yIP4I%k$32>zrjCSuv1TQ8toP'
    'X*paO^;?!MvDGrRSX^5jcZo}Euuv#{-x=)P8X0s*D8-=GTauGxn<&BZ%vmFQlpVH2NUoH*u|hPJ8Eb)XijwtlVrfj4N3nOIZ%RC;'
    '4)u>y(x}W}X|NQgxnSF-u=AI(b#VqG5h`2^z7wXCRgscSNu?0;ArvGdfgdzcYAuPhmWi<<psmTyC}g>7z6ozV)FR8B3|!7A1tD*1'
    'ad+I2#Q?mwp2QK7p{U-{%lv`m>l=j{$#W|iNhXsmK-Ph>HV_J-7W2$l1;9!?pT>;1r+9ocSRixXzVKFna27yC*HL1rv<jOuG?euG'
    'h_z(9BeRH~*;<ExYoRRCtD874Q;w$rvSYg`NnhX@T+SHLdHoroEFLlPpwu9L>%?hiLU3SgQd;zW+X{y?imMz6du#!vMeNcekijC0'
    ')B&Zp!8UW~jCsv0GHZcYWK?#~p9?LjOjtBF6<Y?`&fAhH%N?GRvQbUwi+FO^fh&~E`YYn^M4@I7SJpw+iIp%&yApB94+x9+Cn>H)'
    '=TQmIFLFjl=)~2(9~d=}--sJVQ(SLzH~*3bX0B6RM$#t|b+$g)_P}&E{{`8*7aI4{Atv9yv=~W=RoeKX^=E8EKdC*%Z!Uousxez9'
    'woLts{FirUgNn%i_3w86rA5OX&F@xQ`*XkkB+U2_NQI4$!eE`QtE_9BC6D$FBdN|JR|(C^y!(p8L;fN%n$94dYJjRg@;<9p=;~G('
    'eA^aoeoz~Dtdz=ZZ*zQX{qs>fjm@&<^|`xL`yTm$dYf>4!A&W*w6H-bmyN0&a>b~Hi^=Y+o6WHoi{|dwz26*vX!>sA-0gJ|*Ya)8'
    '$c^*v+|u8*TCcy=FE2Pp*c4Fd^H0#op^XeE6d_PRA9)jb28iR(CPJDK%ESnhd29*NJVuqwOF+IpL=q>thX@kTBOphF8WCbRv<OHc'
    '14={)F+c~03}aMKwto>C=(zs@1q=d=rGGM#`eS)Nmi1#9A4&K16#2VHL{5r6?`eOuQl0NZ@;ImZy{ifRP5#Zj%w#Qd>VpJF9UyCj'
    'wNhjDKZ;?N-?-PD{>u{ESXEA1L-Z$;#VbkbJvPz=!eQ@i$uq}{puI6jX2@gG7i_J~*kZ$dNkh<Yh^{5EmBIrFZ1d}e<h6L0d5K#|'
    'hm@#;c$W4$7?V1dumAlIcMAH@'
)

PALETTE = [0, 1, 2, 3, 4, 5, 20, 7, 56, 57, 58, 59, 60, 61, 62, 63]
PATTERNS = [
    bytes(8), bytes([255]*8), bytes.fromhex('ffff0000ffff0000'),
    bytes.fromhex('0102040810204080'), bytes.fromhex('e0c183070e1c3870'),
    bytes.fromhex('f0783c1e0f87c3e1'), bytes.fromhex('a5d269b45a2d964b'),
    bytes.fromhex('ff888888ff888888'), bytes.fromhex('8142241818244281'),
    bytes.fromhex('cc33cc33cc33cc33'), bytes.fromhex('8000080080000800'),
    bytes.fromhex('8800220088002200'),
]
SCALE = [(1, 1), (3, 5), (2, 3), (3, 4), (1, 1), (4, 3),
         (5, 3), (2, 1), (5, 2), (3, 1), (4, 1)]
FONT_NAMES = ['', 'TRIP', 'LITT', 'SANS', 'GOTH', 'SCRI', 'SIMP', 'TSCR', 'LCOM', 'EURO', 'BOLD']


def truncdiv(n, d):
    return n//d if n >= 0 else -((-n)//d)


def nearest(n):
    return math.floor(n + 0.5)


def xml_text(value):
    """Represent non-XML metadata controls visibly without losing their value."""
    safe = ''.join(ch if (ch in '\t\r\n' or 32 <= ord(ch) <= 0xd7ff or
                         0xe000 <= ord(ch) <= 0xfffd or 0x10000 <= ord(ch) <= 0x10ffff)
                   else '\\x%02x' % ord(ch) for ch in value)
    return html.escape(safe)


class Fonts:
    def __init__(self):
        self.raw = {k: base64.b64decode(v) for k, v in
                    json.loads(zlib.decompress(base64.b85decode(_FONT_DATA))).items()}
        self.faces = {}
        for number, name in enumerate(FONT_NAMES[1:], 1):
            b = self.raw[name+'.CHR']
            head = struct.unpack_from('<H', b, b.index(26)+1)[0]
            count = struct.unpack_from('<H', b, head+1)[0]
            first = b[head+4]
            offset = struct.unpack_from('<H', b, head+5)[0]
            cap, base, desc = struct.unpack_from('<bbb', b, head+8)
            glyphs = {}
            for i in range(count):
                pos = head+offset+struct.unpack_from('<H', b, head+16+2*i)[0]
                width = b[head+16+2*count+i]
                segments = []
                old = None
                while pos+1 < len(b):
                    a, c = b[pos:pos+2]
                    pos += 2
                    if not a & 128:
                        break
                    x, y = a & 127, c & 127
                    x = x-128 if x & 64 else x
                    y = y-128 if y & 64 else y
                    point = (x, y)
                    if c & 128 and old is not None:
                        segments.append((*old, *point))
                    old = point
                glyphs[first+i] = (width, segments)
            self.faces[number] = (cap, base, desc, glyphs)

    def metrics(self, text, font, size):
        if not font:
            return len(text)*8*size, 8*size
        cap, base, desc, glyphs = self.faces[font]
        n, d = SCALE[size]
        return sum(glyphs.get(c, (0, []))[0]*n//d for c in text), (cap-2*desc+1)*n//d


_FONTS = None


def fonts():
    global _FONTS
    if _FONTS is None:
        _FONTS = Fonts()
    return _FONTS


class Canvas:
    """Integer indexed framebuffer, serialized as lossless SVG geometry."""
    def __init__(self):
        self.pixels = bytearray(WIDTH*HEIGHT)
        self.palette = PALETTE.copy()
        self.viewport = (0, 0, 639, 349)
        self.color = 7
        self.fill_color = 0
        self.pattern = PATTERNS[1]
        self.line_pattern = 0xffff
        self.thickness = 1
        self.write_mode = 0
        self.font, self.direction, self.font_size = 0, 0, 1
        self.cursor = (0, 0)

    def point(self, x, y, color=None, mode=0, absolute=False):
        x0, y0, x1, y1 = self.viewport
        if absolute:
            x0, y0, x1, y1 = 0, 0, 639, 349
        else:
            x += x0
            y += y0
        if self.viewport == (0, 0, 0, 0) and not absolute:
            return
        if max(0, x0) <= x <= min(639, x1) and max(0, y0) <= y <= min(349, y1):
            c = self.color if color is None else color
            p = y*WIDTH+x
            self.pixels[p] = (self.pixels[p] ^ c) if mode else c

    def limits(self):
        x0, y0, x1, y1 = self.viewport
        return max(0, -x0), max(0, -y0), min(639, x1)-x0, min(349, y1)-y0

    def span(self, y, left, right, color=None):
        if self.viewport == (0, 0, 0, 0):
            return
        lo, top, hi, bottom = self.limits()
        if not top <= y <= bottom:
            return
        left, right = max(lo, left), min(hi, right)
        if left > right:
            return
        ox, oy = self.viewport[:2]
        start = (y+oy)*WIDTH+left+ox
        count = right-left+1
        if color is not None:
            self.pixels[start:start+count] = bytes([color])*count
        else:
            row = self.pattern[(y+oy) & 7]
            tile = bytes(self.fill_color if row & (128 >> ((x+ox) & 7)) else 0
                         for x in range(left, left+8))
            self.pixels[start:start+count] = (tile*((count+7)//8))[:count]

    def bar(self, x0, y0, x1, y1, color=None):
        x0, x1 = sorted((x0, x1))
        y0, y1 = sorted((y0, y1))
        _, top, _, bottom = self.limits()
        for y in range(max(top, y0), min(bottom, y1)+1):
            self.span(y, x0, x1, color)

    def line(self, x0, y0, x1, y1, color=None, mode=None, pattern=None, thick=None):
        color = self.color if color is None else color
        mode = self.write_mode if mode is None else mode
        pattern = self.line_pattern if pattern is None else pattern
        thick = self.thickness if thick is None else thick
        # Use a stable upper endpoint (left endpoint for horizontal lines).
        # Half-pixel ties advance toward the other endpoint, so reversing a
        # segment cannot shift its outline away from the polygon beneath it.
        if (y0, x0) > (y1, x1):
            x0, y0, x1, y1 = x1, y1, x0, y0
        dx, dy = abs(x1-x0), abs(y1-y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx-dy
        step = 0
        while True:
            if pattern & (0x8000 >> (step & 15)):
                self.point(x0, y0, color, mode)
                if thick == 3:
                    if dx >= dy and dx:
                        self.point(x0, y0-1, color, mode)
                        self.point(x0, y0+1, color, mode)
                    else:
                        self.point(x0-1, y0, color, mode)
                        self.point(x0+1, y0, color, mode)
            if x0 == x1 and y0 == y1:
                break
            twice = 2*err
            if twice >= -dy:
                err -= dy
                x0 += sx
            if twice <= dx:
                err += dx
                y0 += sy
            step += 1

    def polygon(self, pts, fill=False, closed=True, **style):
        if not pts:
            return
        if fill and len(pts) > 1:
            _, low, _, high = self.limits()
            edges = []
            for a, b in zip(pts, pts[1:]+pts[:1]):
                if a[1] > b[1]:
                    a, b = b, a
                if a[1] != b[1]:
                    edges.append((a[0], a[1], b[0]-a[0], b[1]-a[1]))
            for y in range(max(low, min(p[1] for p in pts)), min(high, max(p[1] for p in pts))+1):
                crossings = []
                for x, top, dx, height in edges:
                    if top <= y < top+height:
                        # Quantize each edge from its upper endpoint, truncating
                        # the signed displacement toward zero. Both endpoints
                        # of the resulting integer span belong to the fill.
                        # Rounding a floating left/right crossing inward leaves
                        # background cracks between the fill and later strokes.
                        offset = abs(dx)*(y-top)//height
                        crossings.append(x+(offset if dx >= 0 else -offset))
                crossings.sort()
                for a, b in zip(crossings[::2], crossings[1::2]):
                    self.span(y, a, b)
        # PabloDraw's filled-polygon convention: color index 0 disables the
        # outline. Keep genuine black lines, rectangles and unfilled polygons.
        # Test the index, not its palette RGB; remapping does not change this.
        if fill and style.get('color', self.color) == 0:
            return
        for a, b in zip(pts, pts[1:]):
            self.line(*a, *b, **style)
        if closed and len(pts) > 1:
            self.line(*pts[-1], *pts[0], **style)

    def rectangle(self, x0, y0, x1, y1, **style):
        if x0 == x1 or y0 == y1:
            self.line(x0, y0, x1, y1, **style)
        else:
            self.polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], **style)

    @staticmethod
    def ellipse_points(rx, ry):
        # Integer midpoint ellipse, including all four symmetric quadrants.
        if not rx:
            return {(0, y) for y in range(-ry, ry+1)}
        if not ry:
            return {(x, 0) for x in range(-rx, rx+1)}
        points = set()
        x, y = 0, ry
        a, b = rx*rx, ry*ry
        px, py = 0, 2*a*y
        decision = 4*b-4*a*ry+a
        while px < py:
            points.update(((x,y),(-x,y),(x,-y),(-x,-y)))
            x += 1
            px += 2*b
            if decision < 0:
                decision += 4*(b+px)
            else:
                y -= 1
                py -= 2*a
                decision += 4*(b+px-py)
        decision = b*(2*x+1)**2 + 4*a*(y-1)**2 - 4*a*b
        while y >= 0:
            points.update(((x,y),(-x,y),(x,-y),(-x,-y)))
            y -= 1
            py -= 2*a
            if decision > 0:
                decision += 4*(a-py)
            else:
                x += 1
                px += 2*b
                decision += 4*(a-py+px)
        return points

    def ellipse(self, cx, cy, start, end, rx, ry, fill=False, pie=False):
        if start == end:
            return
        full = abs(end-start) >= 360
        angle0, sweep = start % 360, (end-start) % 360
        points = self.ellipse_points(rx, ry)
        def inside(x, y):
            ang = math.degrees(math.atan2(-y*rx, x*ry)) % 360
            return full or (ang-angle0) % 360 <= sweep+1e-10
        if fill:
            rows = collections.defaultdict(list)
            for x, y in points:
                rows[y].append(x)
            for y, xs in rows.items():
                left, right = min(xs), max(xs)
                if not pie or full:
                    self.span(cy+y, cx+left, cx+right)
                else:
                    run = None
                    for x in range(left, right+2):
                        yes = x <= right and ((x == 0 and y == 0) or inside(x, y))
                        if yes and run is None:
                            run = x
                        if not yes and run is not None:
                            self.span(cy+y, cx+run, cx+x-1)
                            run = None
        for x, y in points:
            if inside(x, y):
                self.point(cx+x, cy+y)
                if self.thickness == 3:
                    if abs(x)*ry*ry > abs(y)*rx*rx:
                        self.point(cx+x-1, cy+y)
                        self.point(cx+x+1, cy+y)
                    else:
                        self.point(cx+x, cy+y-1)
                        self.point(cx+x, cy+y+1)
        if pie and not full:
            for ang in (start, end):
                rad = math.radians(ang)
                self.line(cx, cy, cx+nearest(rx*math.cos(rad)), cy-nearest(ry*math.sin(rad)), mode=0, pattern=65535)

    def flood(self, x, y, border):
        if self.viewport == (0, 0, 0, 0):
            return
        ox, oy = self.viewport[:2]
        x, y = x+ox, y+oy
        x0, y0, x1, y1 = self.viewport
        x0, y0, x1, y1 = max(0, x0), max(0, y0), min(639, x1), min(349, y1)
        if not (x0 <= x <= x1 and y0 <= y <= y1) or self.pixels[y*640+x] == border:
            return
        visited = bytearray(WIDTH*HEIGHT)
        stack = [(x, y, 0)]
        while stack:
            x, y, direction = stack.pop()
            idx = y*640+x
            if visited[idx] or self.pixels[idx] == border:
                continue
            left, right = x, x
            while left > x0 and not visited[y*640+left-1] and self.pixels[y*640+left-1] != border:
                left -= 1
            while right < x1 and not visited[y*640+right+1] and self.pixels[y*640+right+1] != border:
                right += 1
            # Legacy edge-fill compatibility: a one-pixel horizontal run at
            # either physical screen edge is neither painted nor traversed.
            # Wider edge runs and one-pixel interior passages remain fillable.
            if left == right and left in (0, WIDTH-1):
                visited[idx] = 1
                continue
            visited[y*640+left:y*640+right+1] = b'\1'*(right-left+1)
            for step in (-1, 1):
                # Color index zero uses the directional fill behavior observed
                # in PabloDraw: branches keep moving away from the seed row,
                # without reversing around an overhang. This is an index rule,
                # independent of the palette RGB or selected fill pattern.
                if self.fill_color == 0 and direction and step != direction:
                    continue
                ny = y+step
                if not y0 <= ny <= y1:
                    continue
                run = False
                for nx in range(left, right+1):
                    p = ny*640+nx
                    good = not visited[p] and self.pixels[p] != border
                    if good and not run:
                        stack.append((nx, ny, step))
                    run = good
            self.span(y-oy, left-ox, right-ox)

    def text(self, x, y, text, color=None, font=None, size=None, direction=None, mode=None):
        color = self.color if color is None else color
        font = self.font if font is None else font
        size = self.font_size if size is None else size
        direction = self.direction if direction is None else direction
        mode = self.write_mode if mode is None else mode
        f = fonts()
        width, height = f.metrics(text, font, size)
        advance = 0
        if font:
            cap, base, desc, glyphs = f.faces[font]
            n, d = SCALE[size]
            baseline = (cap-desc)*n//d
            # Rotation is anchored by the scaled extent of the whole string.
            # Individual pen advances still truncate separately; summing those
            # advances here shifts fractional-scale text and its fill borders.
            rotated_extent = sum(glyphs.get(c, (0, []))[0] for c in text)*n//d
            for char in text:
                gw, lines = glyphs.get(char, (0, []))
                def transform(a, b):
                    a, b = truncdiv(a*n, d)+advance, baseline-truncdiv(b*n, d)
                    return (x+a, y+b) if not direction else (x+b, y+rotated_extent-a)
                for ax, ay, bx, by in lines:
                    self.line(*transform(ax, ay), *transform(bx, by), color=color, mode=mode, pattern=65535, thick=1)
                advance += gw*n//d
        else:
            raw = f.raw['DOS-CP437.F08']
            for char in text:
                for row, bits in enumerate(raw[char*8:char*8+8]):
                    for col in range(8):
                        if bits & (128 >> col):
                            for sy in range(size):
                                for sx in range(size):
                                    a, b = advance+col*size+sx, row*size+sy
                                    px, py = (x+a, y+b) if not direction else (x+b, y+width-1-a)
                                    self.point(px, py, color, mode)
                advance += 8*size
        self.cursor = (x+width, y) if not direction else (x, y-width)
        return width, height

    def get_image(self, x0, y0, x1, y1, absolute=False):
        if not absolute:
            ox, oy = self.viewport[:2]
            x0, x1, y0, y1 = x0+ox, x1+ox, y0+oy, y1+oy
        if not (0 <= x0 <= x1 < WIDTH and 0 <= y0 <= y1 < HEIGHT):
            return None
        return (x1-x0+1, y1-y0+1, b''.join(self.pixels[y*640+x0:y*640+x1+1] for y in range(y0, y1+1)))

    def put_image(self, x, y, im, mode, absolute=False):
        if im is None:
            return
        w, h, data = im
        ox, oy = (0, 0) if absolute else self.viewport[:2]
        if x+ox < 0 or x+ox+w > 640 or y+oy < 0 or y+oy+h > 350:
            return
        old_view = self.viewport
        if absolute:
            self.viewport = (0, 0, 639, 349)
        for iy in range(h):
            for ix in range(w):
                src = data[iy*w+ix]
                dst = self.pixels[(y+oy+iy)*640+x+ox+ix]
                value = (src, src ^ dst, src | dst, src & dst, src ^ 15)[mode]
                self.point(x+ix, y+iy, value)
        self.viewport = old_view

    def svg(self, title, issues=()):
        # Merge equal horizontal runs vertically, then group rectangles by index.
        groups = [[] for _ in range(16)]
        active = {}
        for y in range(HEIGHT+1):
            runs = {}
            if y < HEIGHT:
                row = self.pixels[y*WIDTH:(y+1)*WIDTH]
                x = 0
                while x < WIDTH:
                    color = row[x]
                    right = x+1
                    while right < WIDTH and row[right] == color:
                        right += 1
                    key = (color, x, right)
                    runs[key] = active.pop(key, y)
                    x = right
            for (color, left, right), top in active.items():
                groups[color].append(f'M{left} {top}h{right-left}v{y-top}h{left-right}z')
            active = runs
        lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<!-- Vibe coded by Codex -->',
                 # One source pixel per CSS pixel at normal zoom. Fractional
                 # vertical stretching unevenly thickens small glyph strokes.
                 '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="350" viewBox="0 0 640 350" preserveAspectRatio="xMidYMid meet" shape-rendering="crispEdges">',
                 '<title>'+xml_text(title)+'</title>',
                 '<desc>RIPscrip 1.54 final framebuffer at its native 640 by 350 pixel size.'+
                 xml_text((' Conversion notes: '+'; '.join(issues)) if issues else '')+'</desc>']
        for c, paths in enumerate(groups):
            if paths:
                ega = self.palette[c]
                rgb = (170*((ega >> 2) & 1)+85*((ega >> 5) & 1),
                       170*((ega >> 1) & 1)+85*((ega >> 4) & 1),
                       170*(ega & 1)+85*((ega >> 3) & 1))
                lines.append('<path fill="#%02x%02x%02x" d="%s"/>' % (*rgb, ''.join(paths)))
        lines.append('</svg>')
        return '\n'.join(lines)+'\n'


class Interpreter:
    def __init__(self, source=None, *, strict_framing=False):
        self.canvas = Canvas()
        self.strict_framing = strict_framing
        self.source = Path(source) if source else None
        self.issues = []
        self.context = 0
        self.clipboard = None
        self.icons = {}
        self.mouse = []
        self.variables = {}
        self.queries = []
        self.region = None
        self.region_y = 0
        self.button_style = [0, 0, 2, 256, 0, 15, 0, 15, 8, 7, 0, 0, 15, 7, 0]
        self.window = (0, 0, 79, 42, 1, 0)
        self.tx = self.ty = 0
        self.tty_fg, self.tty_bg = 7, 0
        self.tty_bold = self.tty_reverse = False
        self.tty_saved = (0, 0)
        self.tty_pending = b''
        self.depth = 0
        self.saved = {}
        self.clip_location = (0, 0, self.canvas.viewport)
        self.cursor_visible = True
        self.last_clipboard_location = None
        self.commands = collections.Counter()
        self.ignored_bytes = 0

    def warn(self, message, category='malformed'):
        record = {'offset': self.context, 'category': category, 'message': message}
        if record not in self.issues:
            self.issues.append(record)

    def valid(self, value, low, high, label):
        if low <= value <= high:
            return True
        self.warn(f'{label} {value} outside {low}..{high}; command ignored')
        return False

    @staticmethod
    def validate_parser(parser):
        # Version-specific opcodes are positive evidence of another dialect.
        extensions = sorted({e.op for e in parser.events if e.kind == 'unknown' and e.op in {'k', 'y', '1b', '1w'}})
        if extensions:
            raise NotRIP('RIPscrip 2.x extensions are outside the 1.54 target: '+', '.join(extensions))

    def execute(self, parser):
        self.validate_parser(parser)
        for e in parser.events:
            self.event(e)
        self.finish()
        return self

    def event(self, e):
        self.context = e.start
        if e.kind == 'command':
            self.commands[e.op] += 1
            if e.problem:
                self.warn(e.problem, 'recovery')
            self.command(e.op, e.args, e.text)
        elif e.kind in ('malformed', 'unknown'):
            self.warn(e.problem+'; skipped to the next protocol delimiter', e.kind)
        elif e.kind == 'tty':
            self.tty(e.text)
        elif e.kind == 'ignored':
            self.ignored_bytes += e.end-e.start
        elif e.kind == 'sauce-recovered':
            self.warn(e.problem, 'metadata')
        elif e.kind == 'dos-eof':
            tail = e.text[1:]
            if tail and tail.strip(b'\x00\x1a\r\n '):
                self.warn(f'{len(tail)} bytes after DOS EOF retained only in the byte audit', 'trailer')

    def finish(self):
        if self.tty_pending:
            self.warn('Incomplete terminal escape sequence at end of input', 'malformed')

    def command(self, op, a, text):
        c = self.canvas
        if c.viewport == (0, 0, 0, 0) and op in {
                'm', 'T', '@', 'X', 'L', 'R', 'B', 'p', 'P', 'l', 'C', 'A',
                'I', 'O', 'V', 'i', 'o', 'Z', 'F', '1C', '1P', '1I', '1U',
                '1M', '1T', '1t', '1E'}:
            return
        if op == '*':
            c.pixels[:] = bytes(WIDTH*HEIGHT)
            c.palette = PALETTE.copy()
            c.viewport = (0, 0, 639, 349)
            c.cursor = (0, 0)
            self.window = (0, 0, 79, 42, 1, 0)
            self.tx = self.ty = 0
            self.mouse.clear()
            self.clipboard = None
        elif op == 'w':
            if not 0 <= a[5] <= 4:
                if any(a[:4]):
                    self.valid(a[5], 0, 4, 'Text window font')
                    return
                # A closed window needs no new font. Preserve the last valid
                # metrics for terminal state while honoring its zero bounds.
                self.warn(f'Text window font {a[5]} outside 0..4; '
                          'zero-coordinate text window disabled, previous font retained')
                a = a[:5]+[self.window[5]]
            if tuple(a[:4]+a[5:]) != self.window[:4]+self.window[5:]:
                self.tx = self.ty = 0
            self.window = tuple(a)
        elif op == 'v':
            if any(a) and not (0 <= a[0] < a[2] < 640 and 0 <= a[1] < a[3] < 350):
                self.warn('Invalid graphics viewport; previous viewport retained')
            else:
                c.viewport = tuple(a)
                c.cursor = (0, 0)
        elif op == 'E':
            x0, y0, x1, y1 = c.viewport
            c.bar(0, 0, x1-x0, y1-y0, 0)
            c.cursor = (0, 0)
        elif op == 'e':
            self.tty_clear(0)
            self.tx = self.ty = 0
        elif op == 'g':
            self.tx, self.ty = a
        elif op == 'H':
            self.tx = self.ty = 0
        elif op == '>':
            self.tty_erase_line(0, 0)
        elif op == 'c':
            if self.valid(a[0], 0, 15, 'Drawing color'): c.color = a[0]
        elif op == 'Q':
            if all(self.valid(v, 0, 63, 'EGA palette entry') for v in a): c.palette = a.copy()
        elif op == 'a':
            if self.valid(a[0], 0, 15, 'Palette index') and self.valid(a[1], 0, 63, 'EGA palette entry'):
                c.palette[a[0]] = a[1]
        elif op == 'W':
            if self.valid(a[0], 0, 1, 'Write mode'): c.write_mode = a[0]
        elif op == '=':
            if self.valid(a[0], 0, 4, 'Line style') and a[2] in (1, 3):
                c.line_pattern = [65535, 0x3333, 0x1e3f, 0x1f1f, a[1] & 65535][a[0]]
                c.thickness = a[2]
                if a[1] > 65535: self.warn('Line pattern exceeds 16 bits; low 16 bits used')
            elif a[2] not in (1, 3): self.warn('Line thickness must be 1 or 3; command ignored')
        elif op == 'S':
            if self.valid(a[0], 0, 11, 'Fill style') and self.valid(a[1], 0, 15, 'Fill color'):
                c.pattern, c.fill_color = PATTERNS[a[0]], a[1]
        elif op == 's':
            if all(self.valid(v, 0, 255, 'Pattern row') for v in a[:8]) and self.valid(a[8], 0, 15, 'Fill color'):
                c.pattern, c.fill_color = bytes(a[:8]), a[8]
        elif op == 'Y':
            if self.valid(a[0], 0, 10, 'Font') and self.valid(a[1], 0, 1, 'Font direction'):
                size = a[2]
                if size == 0:
                    # Recover the minimum supported size without discarding the
                    # requested font/direction or changing the source arguments.
                    self.warn('Font size 0 outside 1..10; using minimum size 1')
                    size = 1
                if self.valid(size, 1, 10, 'Font size'):
                    c.font, c.direction, c.font_size = a[0], a[1], size
            if a[3]: self.warn('Nonzero reserved font field', 'reserved')
        elif op == 'm': c.cursor = tuple(a)
        elif op in ('T', '@'):
            c.text(*(a if op == '@' else c.cursor), text)
        elif op == 'X': c.point(*a)
        elif op == 'L': c.line(*a)
        elif op == 'R': c.rectangle(*a)
        elif op == 'B': c.bar(*a)
        elif op in ('p', 'P', 'l'):
            if a[0] < 2 or a[0] > 512:
                self.warn('Polygon point count outside the documented 2..512 range')
            c.polygon(list(zip(a[1::2], a[2::2])), fill=op == 'p', closed=op != 'l')
        elif op == 'C':
            c.ellipse(a[0], a[1], 0, 360, a[2],
                      a[2]*CIRCLE_ASPECT_NUM//CIRCLE_ASPECT_DEN)
        elif op in ('A', 'I'):
            c.ellipse(*a[:4], a[4], a[4]*CIRCLE_ASPECT_NUM//CIRCLE_ASPECT_DEN,
                      fill=op == 'I', pie=op == 'I')
        elif op in ('O', 'V', 'i'): c.ellipse(*a, fill=op == 'i', pie=op == 'i')
        elif op == 'o': c.ellipse(*a[:2], 0, 360, *a[2:], fill=True)
        elif op == 'Z':
            points = list(zip(a[:8:2], a[1:8:2]))
            count = a[8]
            if count == 0:
                self.warn('Zero Bezier segment count; curve ignored')
                return
            prev = points[0]
            for i in range(1, count+1):
                t = i/count
                u = 1-t
                weights = (u*u*u, 3*u*u*t, 3*u*t*t, t*t*t)
                point = tuple(nearest(sum(p[axis]*w for p, w in zip(points, weights))) for axis in (0, 1))
                c.line(*prev, *point)
                prev = point
        elif op == 'F':
            if self.valid(a[2], 0, 15, 'Flood border'): c.flood(*a)
        elif op == '1C':
            im = c.get_image(*a[:4])
            if im is not None:
                self.clipboard = im
                self.clip_location = (*a[:2], c.viewport)
            else: self.warn('Invalid clipboard rectangle; copy ignored')
        elif op == '1P':
            if self.valid(a[2], 0, 4, 'Image write mode'): c.put_image(*a[:2], self.clipboard, a[2])
        elif op == '1G':
            x0, y0, x1, y1, reserved, dest = a
            x0, x1 = x0//8*8, (x1+7)//8*8
            im = c.get_image(x0, y0, x1, y1, absolute=True)
            c.put_image(x0, dest, im, 0, absolute=True)
        elif op == '1W':
            if self.clipboard is not None:
                self.icons[self.asset_name(text, '.ICN').upper()] = self.clipboard
        elif op == '1I':
            if not self.valid(a[2], 0, 4, 'Image write mode'): return
            im = self.load_icon(text)
            if im is not None:
                c.put_image(*a[:2], im, a[2])
                if a[3]:
                    self.clipboard = im
                    self.clip_location = (*a[:2], c.viewport)
        elif op == '1R':
            path = self.asset_path(text, '.RIP')
            if path is not None:
                if self.depth >= 16:
                    self.warn('Scene recursion exceeds 16 nested includes', 'resource')
                    return
                parent = self.source
                try:
                    self.depth += 1
                    self.source = path
                    self.execute(Parser(path.read_bytes(), strict_framing=self.strict_framing))
                except (OSError, ValueError) as ex:
                    self.warn('Included scene failed: '+str(ex), 'resource')
                finally:
                    self.depth -= 1
                    self.source = parent
        elif op == '1K': self.mouse.clear()
        elif op == '1M':
            if len(self.mouse) < 128:
                self.mouse.append({'type': 'region', 'args': a, 'host': text.decode('cp437')})
            else: self.warn('More than 128 mouse fields/buttons; new region ignored')
        elif op == '1B':
            if all(self.valid(a[i], 0, 15, 'Button color') for i in (5, 6, 7, 8, 9, 12, 13)) and self.valid(a[2], 0, 4, 'Label orientation'):
                self.button_style = a.copy()
        elif op == '1U': self.button(a, text)
        elif op == '1T':
            self.region = a[:4]
            self.region_y = a[1]
        elif op == '1t': self.region_text(a[0], text)
        elif op == '1E': self.region = None
        elif op == '1D':
            # Definition grammar is independent of the host-command language.
            m = re.fullmatch(rb'([A-Za-z][A-Za-z0-9_]{0,11})(?:,([0-9]+))?:(?:\?([^?]*)\?)?(.*)', text)
            if not m:
                self.warn('Malformed variable definition')
            else:
                name, width, question, default = m.groups()
                if default:
                    self.variables[name.decode('ascii').upper()] = default.decode('cp437')
                else:
                    self.warn('Variable '+name.decode('ascii')+' requires interactive input', 'interactive')
        elif op in ('1\x1b', '1F'):
            self.queries.append({'op': op, 'args': a, 'text': text.decode('cp437')})
            if op == '1\x1b' and a[0] == 0:
                self.host_actions(text)
        elif op == '9\x1b':
            self.warn('Live file-transfer payload cannot be replayed by a static image converter', 'unsupported')
        elif op == '#':
            pass  # End-of-scene notification, NOT end-of-file.
        else:
            raise AssertionError('Recognized command has no implementation: '+repr(op))

    @staticmethod
    def asset_name(text, extension):
        name = text.decode('cp437').strip()
        return name if '.' in name else name+extension

    def asset_path(self, text, extension):
        name = self.asset_name(text, extension)
        if any(ch in name for ch in '/\\:\0') or name in ('.', '..'):
            self.warn('Invalid external asset filename '+repr(name), 'resource')
            return None
        if self.source:
            try:
                matches = [p for p in self.source.parent.iterdir() if p.name.upper() == name.upper() and p.is_file()]
                if len(matches) == 1:
                    return matches[0]
                if len(matches) > 1:
                    self.warn('Ambiguous case-insensitive asset name '+name, 'resource')
                    return None
            except OSError:
                pass
        self.warn('Missing external asset '+name, 'resource')
        return None

    def load_icon(self, text):
        name = self.asset_name(text, '.ICN').upper()
        if name in self.icons:
            return self.icons[name]
        path = self.asset_path(text, '.ICN')
        if path is None:
            return None
        try:
            data = path.read_bytes()
            if len(data) < 4: raise ValueError('truncated header')
            w, h = (x+1 for x in struct.unpack_from('<HH', data))
            stride = (w+7)//8
            expected = 4+stride*4*h
            # The bitmap has an exact length. BGI icon files also occur with
            # one or two unused trailing buffer bytes; neither is pixel data.
            if not (1 <= w <= 640 and 1 <= h <= 350 and expected <= len(data) <= expected+2):
                raise ValueError('not an uncompressed four-plane BGI EGA icon')
            pixels = bytearray(w*h)
            for y in range(h):
                for plane in range(4):
                    row = data[4+(y*4+plane)*stride:4+(y*4+plane+1)*stride]
                    for x in range(w):
                        if row[x//8] & (128 >> (x & 7)):
                            pixels[y*w+x] |= 1 << (3-plane)
            im = (w, h, bytes(pixels))
            self.icons[name] = im
            return im
        except (OSError, ValueError) as ex:
            self.warn('Cannot decode '+name+': '+str(ex), 'resource')
            return None

    def button(self, a, text):
        c = self.canvas
        width, height, orient, flags, bevel, fore, shadow, bright, dark, surface, group, flags2, underline, corner, reserved = self.button_style
        x0, y0, x1, y1, hotkey, state, res = a
        parts = (text.split(b'<>', 2)+[b'', b''])[:3]
        icon, label, host = parts
        if flags & 128:
            im = self.load_icon(icon)
            if im is None:
                # Icon dimensions define the entire button. x1/y1 belong to
                # dynamic plain buttons and cannot substitute for a missing image.
                return
            x1, y1 = x0+im[0]-1, y0+im[1]-1
            c.put_image(x0, y0, im, 0)
        elif flags & 1:
            if self.clipboard is None:
                self.warn('Clipboard button has no clipboard image', 'resource')
                return
            x1, y1 = x0+self.clipboard[0]-1, y0+self.clipboard[1]-1
            c.put_image(x0, y0, self.clipboard, 0)
        elif flags & 256:
            if width and height:
                x1, y1 = x0+width-1, y0+height-1
            if x1 < x0 or y1 < y0:
                self.warn('Invalid dynamic button rectangle')
                return
            c.bar(x0, y0, x1, y1, surface)
        def edge(left, top, right, bottom, top_color, bottom_color):
            style = dict(mode=0, pattern=65535, thick=1)
            c.line(left, bottom, left, top, color=top_color, **style)
            c.line(left, top, right, top, color=top_color, **style)
            c.line(right, top, right, bottom, color=bottom_color, **style)
            c.line(right, bottom, left, bottom, color=bottom_color, **style)
            c.point(left, bottom, corner)
            c.point(right, top, corner)
        bx0, by0, bx1, by1 = x0, y0, x1, y1
        if flags & 512:
            if bevel > 640:
                self.warn('Oversized button bevel clipped to display dimensions')
            for k in range(1, min(bevel, 640)+1):
                edge(x0-k, y0-k, x1+k, y1+k, bright, dark)
            bx0, by0, bx1, by1 = x0-bevel, y0-bevel, x1+bevel, y1+bevel
        if flags & 16:
            c.rectangle(bx0-1, by0-1, bx1+1, by1+1, color=0, mode=0, pattern=65535, thick=1)
            edge(bx0-2, by0-2, bx1+2, by1+2, dark, bright)
        if flags & 32768:
            edge(x0+1, y0+1, x1-1, y1-1, dark, bright)
        if flags & 8:
            table = [(12,1,1), (25,3,2), (40,4,3), (75,6,5), (150,7,5),
                     (200,8,6), (250,10,7), (300,11,8), (10**9,13,9)]
            _, ix, iy = next(row for row in table if y1-y0+1 < row[0])
            edge(x0+ix, y0+iy, x1-ix, y1-iy, dark, bright)
            edge(x0+ix+1, y0+iy+1, x1-ix-1, y1-iy-1, bright, dark)
        if flags & 64:
            self.clipboard = c.get_image(bx0, by0, bx1, by1)
            self.clip_location = (bx0, by0, c.viewport)
            self.button_style[3] = (flags & ~(128|256|8|512|64|32768)) | 1
        if label:
            tw, th = fonts().metrics(label, c.font, c.font_size)
            # Center the visible capital body; flag 8192 includes descenders.
            if c.font:
                cap, base, desc, glyphs = fonts().faces[c.font]
                n, d = SCALE[c.font_size]
                baseline = (cap-desc)*n//d
                ys = [line[j] for line in glyphs.get(69, (0, []))[1] for j in (1, 3)]
                top = baseline-truncdiv(max(ys, default=cap)*n, d)
                bottom = baseline
                if flags & 8192:
                    all_y = [line[j] for ch in label for line in glyphs.get(ch, (0, []))[1] for j in (1,3)]
                    bottom = baseline-truncdiv(min(all_y, default=0)*n, d)
            else:
                top, bottom = 0, (8 if flags & 8192 else 7)*c.font_size-1
            tx = (x0+x1+1-tw)//2
            ty = (y0+y1-top-bottom)//2
            if orient == 0: ty = by0-bottom-3
            if orient == 4: ty = by1+3-top
            if orient == 1: tx = bx0-tw-2
            if orient == 3: tx = bx1+3
            if orient in (0, 2, 4):
                if flags2 & 8: tx = x0+(20 if flags & 8 else 10)
                elif flags2 & 16: tx = x1-tw-(20 if flags & 8 else 10)
            if flags & 32:
                c.text(tx+1, ty+1, label, color=shadow, direction=0, mode=0)
            c.text(tx, ty, label, color=fore, direction=0, mode=0)
            if hotkey < 256 and flags & 1024:
                idx = label.upper().find(bytes([hotkey]).upper())
                if idx >= 0:
                    dx = fonts().metrics(label[:idx], c.font, c.font_size)[0]
                    cw = fonts().metrics(label[idx:idx+1], c.font, c.font_size)[0]
                    if flags2 & 2:
                        c.text(tx+dx, ty, label[idx:idx+1], color=underline, direction=0, mode=0)
                    if flags & 2048:
                        line_y = ty+bottom+1
                        if c.font:
                            ys = [seg[j] for seg in glyphs.get(label[idx], (0, []))[1] for j in (1,3)]
                            line_y = ty+baseline-truncdiv(min([0]+ys)*n, d)+1
                        c.line(tx+dx, line_y, tx+dx+cw-1, line_y, color=underline, mode=0, pattern=65535, thick=1)
        if flags & 1024 and len(self.mouse) < 128:
            self.mouse.append({'type': 'button', 'args': a, 'style': self.button_style.copy(), 'host': host.decode('cp437')})
        if state & 1 and (flags & 16384 or flags2 & 1):
            im = c.get_image(bx0, by0, bx1, by1)
            c.put_image(bx0, by0, im, 4)

    def host_actions(self, text):
        """Replay immediate, defined visual actions; never send host traffic."""
        if b'((' in text or text.startswith(b'['):
            self.warn('Immediate query uses a pick list or template requiring session input', 'interactive')
            return
        c = self.canvas
        passive = set(('RIPVER DATE MONTH MONTHNUM DAY DOY YEAR FYEAR TIME HOUR MHOUR MIN SEC '
                       'AMPM DATETIME TIMEZONE DOW ADOW WDAY WOY WOYM X Y XY XYM M MSTAT '
                       'TWIN TWFONT TWH TWW TWX0 TWY0 TWX1 TWY1 CURX CURY CURSOR STATBAR '
                       'BEEP BLIP MUSIC ALARM PHASER REVPHASER SBARON SBAROFF VT102ON VT102OFF '
                       'DWAYON DWAYOFF HKEYON HKEYOFF TABON TABOFF OFF').split())
        for match in re.finditer(rb'\$([^$]*)\$', text):
            key = match[1].decode('cp437').upper()
            if key in passive or key in self.variables:
                continue
            if key == 'RESET': self.command('*', [], b'')
            elif key == 'EGW': self.command('E', [], b'')
            elif key == 'ETW': self.command('e', [], b'')
            elif key == 'DTW': self.window = (0,0,0,0,0,0)
            elif key == 'MKILL': self.mouse.clear()
            elif key == 'CON': self.cursor_visible = True
            elif key == 'COFF': self.cursor_visible = False
            elif key in ('SAVEALL', 'RESTOREALL'):
                self.host_actions(b'$STW$$SCB$$SMF$$SAVE$' if key == 'SAVEALL' else b'$RTW$$RCB$$RMF$$RESTORE$')
            elif key == 'SCB': self.saved['clipboard'] = (self.clipboard, self.clip_location)
            elif key == 'RCB':
                self.clipboard, self.clip_location = self.saved.get('clipboard', (None, self.clip_location))
            elif key == 'PCB':
                x, y, viewport = self.clip_location
                old = c.viewport
                c.viewport = viewport
                c.put_image(x, y, self.clipboard, 0)
                c.viewport = old
            elif key == 'SMF': self.saved['mouse'] = copy.deepcopy(self.mouse)
            elif key == 'RMF': self.mouse = copy.deepcopy(self.saved.get('mouse', []))
            elif key == 'STW':
                names = ('window', 'tx', 'ty', 'tty_fg', 'tty_bg', 'tty_bold', 'tty_reverse', 'cursor_visible')
                self.saved['text'] = {name: getattr(self, name) for name in names}
            elif key == 'RTW':
                for name, value in self.saved.get('text', {}).items(): setattr(self, name, value)
            elif re.fullmatch(r'SAVE[0-9]?', key):
                self.saved['screen'+key[4:]] = (bytes(c.pixels), c.viewport)
            elif re.fullmatch(r'RESTORE[0-9]?', key):
                name = 'screen'+key[7:]
                if name in self.saved:
                    data, c.viewport = self.saved[name]
                    c.pixels[:] = data
                    if key[7:]: del self.saved[name]
                else:
                    self.warn('Screen restore has no matching saved screen', 'resource')
            else:
                self.warn('Immediate query variable $'+key+'$ needs terminal-session state', 'interactive')

    def region_text(self, justify, text):
        if self.region is None:
            self.warn('REGION_TEXT outside BEGIN_TEXT/END_TEXT')
            return
        c = self.canvas
        x0, y0, x1, y1 = self.region
        w, h = fonts().metrics(text, c.font, c.font_size)
        y = self.region_y
        self.region_y += h
        if y+h-1 > y1:
            return
        saved = c.viewport
        ox, oy = saved[:2]
        # Region is clipped without changing the existing coordinate origin.
        c.viewport = (ox, oy, min(saved[2], ox+x1), min(saved[3], oy+y1))
        if justify and b' ' in text:
            words = text.split(b' ')
            width = sum(fonts().metrics(word, c.font, c.font_size)[0] for word in words)
            extra = max(0, x1-x0+1-width)
            used = 0
            for i, word in enumerate(words):
                x = x0+used+(extra*i//(len(words)-1))
                used += c.text(x, y, word, direction=0)[0]
        else:
            c.text(x0, y, text, direction=0)
        c.viewport = saved

    def tty_geometry(self):
        x0, y0, x1, y1, wrap, size = self.window
        cw, ch = [(8,8), (7,8), (8,14), (7,14), (16,14)][size]
        return x0*cw, y0*ch, (x1-x0+1), (y1-y0+1), cw, ch

    def tty_clear(self, color):
        if not any(self.window[:4]): return
        x, y, cols, rows, cw, ch = self.tty_geometry()
        c = self.canvas
        saved = c.viewport
        c.viewport = (0,0,639,349)
        c.bar(x, y, x+cols*cw-1, y+rows*ch-1, color)
        c.viewport = saved

    def tty_erase_line(self, mode, color):
        if not any(self.window[:4]): return
        x, y, cols, rows, cw, ch = self.tty_geometry()
        left = self.tx if mode == 0 else 0
        right = self.tx if mode == 1 else cols-1
        c = self.canvas
        saved = c.viewport
        c.viewport = (0,0,639,349)
        c.bar(x+left*cw, y+self.ty*ch, x+(right+1)*cw-1, y+(self.ty+1)*ch-1, color)
        c.viewport = saved

    def tty_newline(self):
        x, y, cols, rows, cw, ch = self.tty_geometry()
        self.ty += 1
        if self.ty < rows: return
        self.ty = max(0, rows-1)
        if not self.window[4]: return
        c = self.canvas
        saved = c.viewport
        c.viewport = (0,0,639,349)
        im = c.get_image(x, y+ch, min(639, x+cols*cw-1), min(349, y+rows*ch-1), absolute=True)
        c.put_image(x, y, im, 0, absolute=True)
        c.bar(x, y+self.ty*ch, x+cols*cw-1, y+(self.ty+1)*ch-1, self.tty_bg)
        c.viewport = saved

    def tty(self, data):
        data = self.tty_pending+data
        self.tty_pending = b''
        p = 0
        while p < len(data):
            ch = data[p]
            if ch == 27:
                m = re.match(rb'\x1b\[([0-9;?]*)([ -/]*)([@-~])', data[p:])
                if m:
                    params, intermediates, final = m.groups()
                    p += m.end()
                    self.ansi(params, final)
                    continue
                if data[p:] in (b'\x1b', b'\x1b[') or re.fullmatch(rb'\x1b\[[0-9;?]*', data[p:]):
                    self.tty_pending = data[p:]
                    return
                if p+1 < len(data) and data[p+1] in b'78c':
                    if data[p+1] == 55: self.tty_saved = self.tx, self.ty
                    if data[p+1] == 56: self.tx, self.ty = self.tty_saved
                    if data[p+1] == 99:
                        self.tty_clear(0)
                        self.tx = self.ty = 0
                    p += 2
                    continue
                self.warn('Unsupported terminal escape '+repr(data[p:p+16]), 'terminal')
                p += 1
                continue
            p += 1
            if ch == 13: self.tx = 0; continue
            if ch == 10:
                if any(self.window[:4]): self.tty_newline()
                continue
            if ch == 12:
                self.tty_clear(self.tty_bg)
                self.tx = self.ty = 0
                continue
            if ch == 8: self.tx = max(0, self.tx-1); continue
            if ch == 9: self.tx = (self.tx//8+1)*8; continue
            if ch in (0, 7, 26): continue
            if not any(self.window[:4]): continue
            x, y, cols, rows, cw, cheight = self.tty_geometry()
            if cols <= 0 or rows <= 0: continue
            if self.tx >= cols:
                if self.window[4]: self.tx = 0; self.tty_newline()
                else: self.tx = cols-1
            self.ty = min(max(0, self.ty), rows-1)
            self.tx = max(0, self.tx)
            raw = fonts().raw['DOS-CP437.F08' if cheight == 8 else 'EGA8.F14']
            fg = self.tty_fg | (8 if self.tty_bold else 0)
            bg = self.tty_bg
            if self.tty_reverse: fg, bg = bg, fg
            px, py = x+self.tx*cw, y+self.ty*cheight
            for yy, bits in enumerate(raw[ch*cheight:(ch+1)*cheight]):
                for xx in range(cw):
                    bit = xx//2 if cw == 16 else xx
                    color = fg if bits & (128 >> bit) else bg
                    self.canvas.point(px+xx, py+yy, color, absolute=True)
            self.tx += 1

    def ansi(self, param, final):
        if param.startswith(b'?'):
            # Cursor visibility and wrap mode do not add visible pixels.
            if param == b'?7' and final in (b'h', b'l'):
                self.window = (*self.window[:4], int(final == b'h'), self.window[5])
            elif param != b'?25': self.warn('Unsupported private ANSI sequence', 'terminal')
            return
        a = [int(x) if x else 0 for x in param.split(b';')]
        n = a[0] or 1
        if final in (b'H', b'f'):
            self.ty = (a[0] or 1)-1
            self.tx = ((a[1] if len(a)>1 else 1) or 1)-1
        elif final == b'A': self.ty = max(0, self.ty-n)
        elif final == b'B': self.ty += n
        elif final == b'C': self.tx += n
        elif final == b'D': self.tx = max(0, self.tx-n)
        elif final == b'G': self.tx = n-1
        elif final == b'd': self.ty = n-1
        elif final == b'E': self.tx = 0; self.ty += n
        elif final == b'F': self.tx = 0; self.ty = max(0, self.ty-n)
        elif final == b's': self.tty_saved = self.tx, self.ty
        elif final == b'u': self.tx, self.ty = self.tty_saved
        elif final == b'K': self.tty_erase_line(a[0], self.tty_bg)
        elif final == b'J':
            if a[0] == 2:
                self.tty_clear(self.tty_bg)
                self.tx = self.ty = 0
            else:
                old = self.tx, self.ty
                self.tty_erase_line(a[0], self.tty_bg)
                rows = self.tty_geometry()[3]
                rng = range(self.ty+1, rows) if a[0] == 0 else range(0, self.ty)
                for row in rng:
                    self.ty, self.tx = row, 0
                    self.tty_erase_line(2, self.tty_bg)
                self.tx, self.ty = old
        elif final == b'm':
            mapping = [0,4,2,6,1,5,3,7]
            for value in a:
                if value == 0:
                    self.tty_fg, self.tty_bg = 7, 0
                    self.tty_bold = self.tty_reverse = False
                elif value == 1: self.tty_bold = True
                elif value == 22: self.tty_bold = False
                elif value == 7: self.tty_reverse = True
                elif value == 27: self.tty_reverse = False
                elif 30 <= value <= 37: self.tty_fg = mapping[value-30]
                elif 40 <= value <= 47: self.tty_bg = mapping[value-40]
                elif 90 <= value <= 97: self.tty_fg = mapping[value-90]+8
                elif 100 <= value <= 107: self.tty_bg = mapping[value-100]+8
                elif value == 39: self.tty_fg = 7
                elif value == 49: self.tty_bg = 0
                elif value not in (5,25): self.warn('Unsupported ANSI SGR '+str(value), 'terminal')
        elif final in (b'n', b'c', b'h', b'l'):
            pass  # Terminal queries/mode changes have no static graphics output.
        else:
            self.warn('Unsupported ANSI CSI '+param.decode('ascii')+final.decode('ascii'), 'terminal')


def convert(data, source=None, *, strict_framing=False):
    """Legacy in-memory API: replay the entire stream into one framebuffer."""
    parser = Parser(data, strict_framing=strict_framing)
    interpreter = Interpreter(source, strict_framing=strict_framing).execute(parser)
    title = parser.sauce.get('title') if parser.sauce else ''
    title = title or (Path(source).name if source else 'RIPscrip image')
    messages = list(dict.fromkeys(i['message'] for i in interpreter.issues))
    svg = interpreter.canvas.svg(title, messages)
    return svg, parser, interpreter


@dataclasses.dataclass
class Screen:
    canvas: Canvas
    start: int
    end: int
    reference_start: int
    label: str = ''
    svg: str = ''


# Commands that write graphics or text, including local scene invocation.
PAINT_COMMANDS = {'T', '@', 'X', 'L', 'R', 'B', 'C', 'O', 'o', 'A', 'V',
                  'I', 'i', 'Z', 'P', 'p', 'l', 'F', '1P', '1I', '1U',
                  '1G', '1t', '1R'}


def screen_plan(parser):
    """Return event ranges and capture points; never split on # alone.

    @NAME followed by $RIP$ is an explicit host resource-record wrapper,
    separate from the RIP grammar. Only complete outside-command lines count.
    """
    events = parser.events
    lines = [(i, e.text) for i, e in enumerate(events)
             if e.kind == 'tty' and e.text.strip(b'\r\n')
             and (e.start == 0 or parser.data[e.start-1] in (10, 13))
             and (e.end == len(parser.data) or parser.data[e.end] in (10, 13))]
    labels = [(j, i, text[1:].decode('ascii')) for j, (i, text) in enumerate(lines)
              if re.fullmatch(rb'@[A-Za-z_][A-Za-z0-9_]*', text)]
    records = []
    for n, (j, index, label) in enumerate(labels):
        if (j+1 < len(lines) and lines[j+1][1] == b'$RIP$'
                and all(e.kind in ('tty', 'newline') and not e.text.strip(b'\r\n')
                        for e in events[index+1:lines[j+1][0]])):
            start = lines[j+1][0]+1
            end = labels[n+1][1] if n+1 < len(labels) else len(events)
            if any(e.kind == 'command' for e in events[start:end]):
                records.append((start, end, label))
    wrapped = bool(records)
    if not wrapped:
        records = [(0, len(events), '')]
    else:
        # Mixed containers must not silently discard unwrapped RIP commands.
        complete = []
        cursor = 0
        for start, end, label in records+[(len(events), len(events), '')]:
            if any(e.kind in ('command', 'malformed', 'unknown') for e in events[cursor:start]):
                complete.append((cursor, start, ''))
            if end > start:
                complete.append((start, end, label))
            cursor = end
        records = complete
    plan = []
    for record_start, record_end, label in records:
        start = record_start
        viewport = (0, 0, 639, 349)
        painted = False
        ranges = []
        for i in range(record_start, record_end):
            e = events[i]
            if e.kind != 'command':
                continue
            clears_screen = e.op == '*' or (e.op == 'E' and viewport == (0, 0, 639, 349))
            if clears_screen and painted:
                ranges.append((start, i))
                start, painted = i, False
            if e.op == '*':
                viewport = (0, 0, 639, 349)
            elif e.op == 'v':
                a = e.args
                if not any(a) or (0 <= a[0] < a[2] < 640 and 0 <= a[1] < a[3] < 350):
                    viewport = tuple(a)
            elif e.op in PAINT_COMMANDS and viewport != (0, 0, 0, 0):
                painted = True
        ranges.append((start, record_end))
        for start, end in ranges:
            # Setup commands after an end marker can prepare the next screen.
            # Capture before intervening BBS text but still execute all bytes.
            visible = [i for i in range(start, end) if events[i].kind == 'command'
                       and events[i].op in PAINT_COMMANDS | {'#', '*', 'E', 'e', '>', 'a', 'Q', '1\x1b'}]
            capture = visible[-1] if visible else end-1
            plan.append((start, end, capture, record_start, label))
    return plan, wrapped


def convert_screens(data, source=None, *, strict_framing=False):
    """Render all explicit screens, retaining normal single-screen behavior."""
    parser = Parser(data, strict_framing=strict_framing)
    Interpreter.validate_parser(parser)  # Validate the whole input before output.
    plan, wrapped = screen_plan(parser)
    if len(plan) == 1 and not wrapped:
        renderer = Interpreter(source, strict_framing=strict_framing).execute(parser)
        screens = [Screen(copy.deepcopy(renderer.canvas), 0, parser.body_end, 0)]
    else:
        screens = []
        renderer = Interpreter(source, strict_framing=strict_framing)
        aggregate_commands, aggregate_issues = collections.Counter(), []
        ignored = 0
        previous_record = None
        for start, end, capture, record, label in plan:
            if wrapped and record != previous_record:
                if previous_record is not None:
                    renderer.finish()
                    aggregate_commands.update(renderer.commands)
                    aggregate_issues.extend(renderer.issues)
                    ignored += renderer.ignored_bytes
                renderer = Interpreter(source, strict_framing=strict_framing)
            previous_record = record
            for i in range(start, end):
                renderer.event(parser.events[i])
                if i == capture:
                    screens.append(Screen(copy.deepcopy(renderer.canvas),
                                          parser.events[start].start,
                                          parser.events[i].end,
                                          parser.events[record].start, label))
        renderer.finish()
        renderer.commands.update(aggregate_commands)
        renderer.issues = aggregate_issues + renderer.issues
        renderer.ignored_bytes += ignored
    title = (parser.sauce or {}).get('title') or (Path(source).name if source else 'RIPscrip image')
    messages = list(dict.fromkeys(i['message'] for i in renderer.issues))
    for n, screen in enumerate(screens, 1):
        suffix = f' — screen {n} of {len(screens)}' if len(screens) > 1 else ''
        if screen.label:
            suffix += ' — '+screen.label
        screen.svg = screen.canvas.svg(title+suffix, messages)
    return screens, parser, renderer


def screen_names(count):
    width = len(str(count))
    return [f'{n:0{width}d}.svg' for n in range(1, count+1)]


def write_screens(directory, screens, source=None):
    """Write numbered screens and remove stale current or legacy screen names."""
    directory = Path(directory)
    names = screen_names(len(screens))
    previous = list(directory.glob('*.svg')) if directory.is_dir() else []
    stale = [p for p in previous if re.fullmatch(r'(?:out_)?[0-9]+\.svg', p.name) and p.name not in names]
    destinations = [directory/name for name in names]
    for path in destinations+stale:
        if source is not None and path.resolve() == Path(source).resolve():
            raise ValueError('An output or stale screen path would overwrite the input')
        if path.is_dir():
            raise ValueError('Screen output path is a directory: '+str(path))
    directory.mkdir(parents=True, exist_ok=True, mode=0o775)
    for path, screen in zip(destinations, screens):
        atomic_write(path, screen.svg.encode('utf-8'))
    for path in stale:
        path.unlink()
    return names


def atomic_write(path, data):
    path = Path(path)
    # Write only after recognition and rendering succeed; replace atomically.
    fd, temp = tempfile.mkstemp(prefix='.'+path.name+'.', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(data)
            os.fchmod(f.fileno(), 0o664)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp): os.unlink(temp)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('inputFile', type=Path)
    ap.add_argument('outputDirectory', type=Path,
                    help='directory for 1.svg, 2.svg, ... (padding follows screen count)')
    ap.add_argument('-verbose', '--verbose', action='store_true',
                    help='also write audit.json in the output directory with byte spans and diagnostics')
    ap.add_argument('--strict-framing', action='store_true',
                    help='require published introducers and continuations; replay blank lines as terminal text')
    args = ap.parse_args(argv)
    try:
        if args.inputFile.resolve() == args.outputDirectory.resolve():
            raise ValueError('Input and output paths must differ')
        if args.verbose and args.inputFile.resolve() == (args.outputDirectory/'audit.json').resolve():
            raise ValueError('Verbose audit path would overwrite the input')
        data = args.inputFile.read_bytes()
        screens, parser, renderer = convert_screens(data, args.inputFile, strict_framing=args.strict_framing)
        names = write_screens(args.outputDirectory, screens, args.inputFile)
        if args.verbose:
            counts = collections.Counter()
            spans = []
            for e in parser.events:
                counts[e.kind] += e.end-e.start
                entry = dataclasses.asdict(e)
                entry['text'] = e.text.decode('cp437')
                entry['raw_base64'] = base64.b64encode(data[e.start:e.end]).decode('ascii')
                spans.append(entry)
            report = {'input_size': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
                      'byte_counts': dict(counts), 'sauce': parser.sauce,
                      'recovered_sauce': parser.recovered_sauce,
                      'commands': dict(renderer.commands), 'issues': renderer.issues,
                      'strict_framing': parser.strict_framing,
                      'bare_command_line_offsets': parser.bare_command_lines,
                      'blank_separator_offsets': parser.blank_separator_offsets,
                      'recovered_polygons': parser.recovered_polygons,
                      'screens': [dict(file=name, start=s.start, end=s.end,
                                       reference_start=s.reference_start, label=s.label)
                                  for name, s in zip(names, screens)],
                      'spans': spans, 'mouse_fields': renderer.mouse,
                      'queries': renderer.queries, 'variables': renderer.variables}
            atomic_write(args.outputDirectory/'audit.json', (json.dumps(report, indent=2)+'\n').encode('utf-8'))
        if renderer.issues:
            print(f'{args.inputFile}: converted with {len(renderer.issues)} diagnostic(s).', file=sys.stderr)
            for msg in dict.fromkeys(i['message'] for i in renderer.issues):
                print('  '+msg, file=sys.stderr)
        return 0
    except (OSError, ValueError) as ex:
        print('ripScrip: '+str(ex), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())

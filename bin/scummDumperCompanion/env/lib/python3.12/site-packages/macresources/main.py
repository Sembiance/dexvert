# Copyright (c) 2018-2020 Elliot Nunn

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import collections
import struct
import enum
import re


# The allowed token sequence when parsing Rez code (quite restrictive)
rez_tokens = [
    ((),         r'(\s|//.*?\n|/\*.*?\*/)+'),                                   # 0 whitespace/comment (gets ignored)
    ((1,11),     r'\$"\s*((?:[0-9A-Fa-f]{2}\s*)*)"'),                           # 1 hex data
    ((3,),       r'(data)'),                                                    # 2 start of raw resource
    ((4,),       r"('(?:[^'\\]|\\0x[0-9A-Fa-f]{2}|\\[\\'\\?btrvfn])*')"),       # 3 type
    ((5,),       r'(\()'),                                                      # 4 start of bracketed resource info
    ((6,7,8,9),  r'(-?\d+)'),                                                   # 5 ID
    ((7,8,9),    r',gap("(?:[^"\\]|\\0x[0-9A-Fa-f]{2}|\\[\\"\\?btrvfn])*")'),   # 6 name
    ((9,),       r',gap\$([0-9a-fA-F]{1,2})'),                                  # 7 attribs (hex)
    ((8,9),      r',gap(sysheap|purgeable|locked|protected|preload)'),          # 8 attribs (specific)
    ((10,),      r'(\))'),                                                      # 9 end of bracketed resource info
    ((1,11),     r'(\{)'),                                                      # 10 start of hex block
    ((12,),      r'(\})'),                                                      # 11 end of hex block
    ((2,-1),     r'(;)'),                                                       # 12 the end for real
    ((),         r'(.)'),                                                       # 13 unexpected character (always errors)
]

allowed_to_follow_kind, token_regexen = zip(*rez_tokens)

# The 'gap' hack turns ', sysheap' etc into a single token
gap = r'(?:\s|//.*?\n|/\*.*?\*/)*'
rez_tokenizer = '|'.join(token_regexen).replace('gap', gap).encode('ascii')
rez_tokenizer = re.compile(rez_tokenizer)


class RezSyntaxError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
       return self.msg


MAP = bytearray(range(256))
for i in range(32): MAP[i] = ord('.')
MAP[127] = ord('.')
MAP[9] = 0xC6 # tab -> greek delta
MAP[10] = 0xC2 # lf -> logical not

CLEANMAP = bytearray(MAP)
for i in range(256):
    if CLEANMAP[i] >= 128:
        CLEANMAP[i] = ord('.')


def _rez_escape(src, singlequote=False, ascii_clean=False):
    if singlequote:
        the_quote = b"'"
    else:
        the_quote = b'"'

    chars = [the_quote]
    for ch in src:
        if 8 <= ch <= 13:
            nu = b'\\' + b'btrvfn'[ch-8:][:1]
        elif ch < 32 or (ascii_clean and ch >= 128):
            nu = b'\\0x%02X' % ch
        elif ch == ord('\\'):
            nu = b'\\\\' # two backslashes
        elif ch == 127: # DEL character
            nu = b'\\?'
        elif ch == ord("'") and singlequote:
            nu = b"\\'"
        elif ch == ord('"') and not singlequote:
            nu = b'\\"'
        else:
            nu = bytes([ch])
        chars.append(nu)
    chars.append(the_quote)

    return b''.join(chars)


def attribs_for_derez(attribs):
    if attribs & ~0x7C:
        yield '$%02X' % attribs
    else:
        if attribs & 0x40: yield 'sysheap'
        if attribs & 0x20: yield 'purgeable'
        if attribs & 0x10: yield 'locked'
        if attribs & 0x08: yield 'protected'
        if attribs & 0x04: yield 'preload'


class Resource(bytearray):
    """
    A single Mac resource. A four-byte type, a numeric id and some
    binary data are essential. Extra attributes and a name string are
    optional.
    """

    def __init__(self, type, id, name=None, attribs=0, data=b''):
        self.type = type
        self.id = id
        self.data = data
        self.name = name
        self.attribs = attribs

    def __repr__(self):
        datarep = repr(bytes(self.data[:4]))
        if len(self.data) > len(datarep): datarep += '...%sb' % len(self.data)
        return '%s(type=%r, id=%r, name=%r, attribs=%r, data=%s)' % (self.__class__.__name__, self.type, self.id, self.name, self.attribs, datarep)

    @property
    def data(self):
        return self

    @data.setter
    def data(self, set_to):
        self[:] = set_to


def parse_file(from_resfile):
    """Get an iterator of Resource objects from a binary resource file."""

    if not from_resfile: # empty resource forks are fine
        return

    data_offset, map_offset, data_len, map_len = struct.unpack_from('>4L', from_resfile)

    typelist_offset, namelist_offset, numtypes = struct.unpack_from('>24xHHH', from_resfile, map_offset)
    typelist_offset += map_offset # something is definitely fishy here
    namelist_offset += map_offset

    if numtypes == 0xFFFF: return
    numtypes += 1

    typelist = []
    for i in range(numtypes):
        rtype, rtypen, reflist_offset = struct.unpack_from('>4sHH', from_resfile, typelist_offset + 2 + 8*i)
        rtypen += 1
        reflist_offset += typelist_offset
        typelist.append((rtype, rtypen, reflist_offset))

    for rtype, rtypen, reflist_offset in typelist:
        for i in range(rtypen):
            rid, name_offset, mixedfield = struct.unpack_from('>hHL', from_resfile, reflist_offset + 12*i)
            rdata_offset = mixedfield & 0xFFFFFF
            rattribs = mixedfield >> 24

            rdata_offset += data_offset

            rdata_len, = struct.unpack_from('>L', from_resfile, rdata_offset)
            rdata = from_resfile[rdata_offset+4:rdata_offset+4+rdata_len]

            if name_offset == 0xFFFF:
                name = None
            else:
                name_offset += namelist_offset
                name_len = from_resfile[name_offset]
                name = from_resfile[name_offset+1:name_offset+1+name_len].decode('mac_roman')

            yield Resource(type=rtype, id=rid, name=name, attribs=rattribs, data=bytearray(rdata))


def string_surrogate(m):
    m = m.group(0)

    if len(m) == 5: # \0xFF is the most common
        return bytes([int(m[3:], 16)])
    elif m == b'\\"':
        return b'"'
    elif m == b"\\'":
        return b"'"
    elif m == b'\\b':
        return b'\x08' # backspace
    elif m == b'\\t':
        return b'\t'
    elif m == b'\\r':
        return b'\n'
    elif m == b'\\v':
        return b'\x0b' # vertical tab
    elif m == b'\\f':
        return b'\x0c' # form feed
    elif m == b'\\n':
        return b'\r'
    elif m == b'\\?':
        return b'\x7f' # del


def string_literal(string):
    return re.sub(rb'(\\0x..|\\.)', string_surrogate, string[1:-1])


def parse_rez_code(from_rezcode, original_file='<string>'):
    """Get an iterator of Resource objects from code in a subset of the Rez language (bytes or str)."""

    try:
        from_rezcode = from_rezcode.encode('mac_roman')
    except AttributeError:
        pass

    from_rezcode = from_rezcode.replace(b'\r\n', b'\n').replace(b'\r', b'\n')

    # Slightly faster than finditer
    all_tokens = rez_tokenizer.findall(from_rezcode)
    def line_no_for_error(token_idx):
        # Redo all the lexing with finditer, which is slower but
        # gives us Match objects with a byte offset
        work_redoer = rez_tokenizer.finditer(from_rezcode)
        match_obj = next(m for i, m in enumerate(work_redoer) if i == token_idx)
        line_no = from_rezcode[:match_obj.start()].count(ord('\n')) + 1

    allowed_token_kinds = (2,-1)
    for token_idx, token_captures in enumerate(all_tokens):
        # Which single capture is non-empty?
        for token_kind, payload in enumerate(token_captures):
            if payload: break

        # Ignore whitespace
        if not token_kind: continue

        # Unexpected token!
        if token_kind not in allowed_token_kinds:
            raise RezSyntaxError('File %r, line %r' % (original_file, line_no_for_error(token_idx)))

        elif token_kind == 1:
            hex_accum.append(payload)

        elif token_kind == 2:
            res = Resource(b'', 0)
            hex_accum = []

        elif token_kind == 3:
            res.type = string_literal(payload)
            if len(res.type) != 4:
                raise RezSyntaxError('File %r, line %r, type not 4 chars' % (original_file, line_no_for_error(token_idx)))

        elif token_kind == 5:
            res.id = int(payload)
            if not (-65536 <= res.id < 65536):
                raise RezSyntaxError('File %r, line %r, ID out of 16-bit range' % (original_file, line_no_for_error(token_idx)))

        elif token_kind == 6:
            res.name = string_literal(payload).decode('mac_roman')
            if len(res.name) > 255:
                raise RezSyntaxError('File %r, line %r, name > 255 chars' % (original_file, line_no_for_error(token_idx)))

        elif token_kind == 7:
            res.attribs = int(payload, 16)

        elif token_kind == 8:
            if payload == b'sysheap':
                res.attribs |= 0x40
            elif payload == b'purgeable':
                res.attribs |= 0x20
            elif payload == b'locked':
                res.attribs |= 0x10
            elif payload == b'protected':
                res.attribs |= 0x08
            elif payload == b'preload':
                res.attribs |= 0x04

        elif token_kind == 12:
            res[:] = bytes.fromhex(b''.join(hex_accum).decode('ascii'))
            yield res

        allowed_token_kinds = allowed_to_follow_kind[token_kind]

    # Premature EOF
    if -1 not in allowed_token_kinds:
        raise RezSyntaxError('File %r, unexpected end of file' % original_file)


def make_file(from_iter, align=1):
    """Pack an iterator of Resource objects into a binary resource file."""

    class wrap:
        def __init__(self, from_obj):
            self.obj = from_obj

    accum = bytearray(256) # defer header

    data_offset = len(accum)
    bigdict = collections.OrderedDict() # maintain order of types, but manually order IDs
    for r in from_iter:
        wrapped = wrap(r)

        while len(accum) % align:
            accum.extend(b'\x00')

        wrapped.data_offset = len(accum)
        accum.extend(struct.pack('>L', len(r.data)))
        accum.extend(r.data)

        if r.type not in bigdict:
            bigdict[r.type] = []
        bigdict[r.type].append(wrapped)

    map_offset = len(accum)
    accum.extend(bytes(28))

    typelist_offset = len(accum)
    accum.extend(bytes(2 + 8 * len(bigdict)))

    reflist_offset = len(accum)
    resource_count = sum(len(idlist) for idlist in bigdict.values())
    accum.extend(bytes(12 * resource_count))

    namelist_offset = len(accum)
    for rtype, idlist in bigdict.items():
        for res in idlist:
            if res.obj.name is not None:
                res.name_offset = len(accum)
                as_bytes = res.obj.name.encode('mac_roman')
                accum.append(len(as_bytes))
                accum.extend(as_bytes)

    # all right, now populate the reference lists...
    counter = reflist_offset
    for rtype, idlist in bigdict.items():
        for res in idlist:
            res.ref_offset = counter
            if res.obj.name is None:
                this_name_offset = 0xFFFF
            else:
                this_name_offset = res.name_offset - namelist_offset
            attribs = int(res.obj.attribs)
            this_data_offset = res.data_offset - data_offset
            mixedfield = (attribs << 24) | this_data_offset
            struct.pack_into('>hHL', accum, counter, res.obj.id, this_name_offset, mixedfield)

            counter += 12

    # all right, now populate the type list
    struct.pack_into('>H', accum, typelist_offset, (len(bigdict) - 1) & 0xFFFF)
    counter = typelist_offset + 2
    for rtype, idlist in bigdict.items():
        this_type = idlist[0].obj.type
        ref_count = len(idlist)
        firstref_offset = idlist[0].ref_offset - typelist_offset
        struct.pack_into('>4sHH', accum, counter, this_type, ref_count - 1, firstref_offset)

        counter += 8

    # all right, now populate the map
    struct.pack_into('>24xHH', accum, map_offset, typelist_offset - map_offset, namelist_offset - map_offset)

    # all right, now populate the header
    data_len = map_offset - data_offset
    map_len = len(accum) - map_offset
    struct.pack_into('>LLLL', accum, 0, data_offset, map_offset, data_len, map_len)

    return bytes(accum)


def make_rez_code(from_iter, ascii_clean=False):
    """Express an iterator of Resource objects as Rez code (bytes).

    This will match the output of the deprecated Rez utility, unless the
    `ascii_clean` argument is used to get a 7-bit-only code block.
    """

    if ascii_clean:
        themap = CLEANMAP
    else:
        themap = MAP

    lines = []
    for resource in from_iter:
        args = []
        args.append(str(resource.id).encode('ascii'))
        if resource.name is not None:
            args.append(_rez_escape(resource.name.encode('mac_roman'), singlequote=False, ascii_clean=ascii_clean))
        args.extend(x.encode('ascii') for x in attribs_for_derez(resource.attribs))
        args = b', '.join(args)

        fourcc = _rez_escape(resource.type, singlequote=True, ascii_clean=ascii_clean)

        lines.append(b'data %s (%s) {' % (fourcc, args))

        # Create a template bytearray
        numlines = (len(resource) + 15) // 16
        overhang = numlines * 16 - len(resource)
        fulllines = numlines - bool(overhang)
        fl_bytes = fulllines * 78
        guts = numlines * bytearray(b'\t$"                                                    /*                    \n')
        del guts[-1:] # no trailing newline

        # The hex inside the $"" literals
        hex_column = resource.hex().upper().encode('ascii')
        if overhang:
            hex_column += (2 * overhang) * b' '

        # Insert the hex column
        for i in range(8):
            for j in range(4):
                guts[3+i*5+j::78] = hex_column[i*4+j::32]

        # Close the hex literal
        guts[42:fl_bytes:78] = b'"' * fulllines
        if overhang: # slightly hacky -- searches for spaces!
            guts[fl_bytes+guts[fl_bytes:].index(b'  ')] = ord('"')

        # Prevent star-slash from ending the comment column prematurely
        def comment_end_fixer(m):
            start, stop = m.span()
            stop -= 1
            if start & -16 == stop & -16:
                return m.group()[:-1] + b'.'
            else:
                return m.group()
        comment_column = re.sub(rb'\*[\x00-\x1F]{0,14}/', comment_end_fixer, resource)
        comment_column = comment_column.translate(themap)
        if overhang:
            comment_column += overhang * b' '

        # Insert the comment column
        for i in range(16):
            guts[58+i::78] = comment_column[i::16]

        # Close the comment
        guts[75:fl_bytes:78] = b'*' * fulllines
        guts[76:fl_bytes:78] = b'/' * fulllines
        if overhang:
            del guts[-overhang-2:]
            guts.extend(b'*/')

        if guts: lines.append(guts)

        lines.append(b'};')
        lines.append(b'')
    if lines: lines.append(b'') # hack, because all posix lines end with a newline

    return b'\n'.join(lines)

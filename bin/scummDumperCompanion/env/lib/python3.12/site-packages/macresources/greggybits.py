# Copyright (c) 2018-2020 Maxim Poliakovski, Elliot Nunn

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


import struct


class WrongFormatError(ValueError):
    pass


# predefined lookup table of the most frequent words
TABLE = (
    0x0000, 0x0008, 0x4EBA, 0x206E, 0x4E75, 0x000C, 0x0004, 0x7000,
    0x0010, 0x0002, 0x486E, 0xFFFC, 0x6000, 0x0001, 0x48E7, 0x2F2E,
    0x4E56, 0x0006, 0x4E5E, 0x2F00, 0x6100, 0xFFF8, 0x2F0B, 0xFFFF,
    0x0014, 0x000A, 0x0018, 0x205F, 0x000E, 0x2050, 0x3F3C, 0xFFF4,
    0x4CEE, 0x302E, 0x6700, 0x4CDF, 0x266E, 0x0012, 0x001C, 0x4267,
    0xFFF0, 0x303C, 0x2F0C, 0x0003, 0x4ED0, 0x0020, 0x7001, 0x0016,
    0x2D40, 0x48C0, 0x2078, 0x7200, 0x588F, 0x6600, 0x4FEF, 0x42A7,
    0x6706, 0xFFFA, 0x558F, 0x286E, 0x3F00, 0xFFFE, 0x2F3C, 0x6704,
    0x598F, 0x206B, 0x0024, 0x201F, 0x41FA, 0x81E1, 0x6604, 0x6708,
    0x001A, 0x4EB9, 0x508F, 0x202E, 0x0007, 0x4EB0, 0xFFF2, 0x3D40,
    0x001E, 0x2068, 0x6606, 0xFFF6, 0x4EF9, 0x0800, 0x0C40, 0x3D7C,
    0xFFEC, 0x0005, 0x203C, 0xFFE8, 0xDEFC, 0x4A2E, 0x0030, 0x0028,
    0x2F08, 0x200B, 0x6002, 0x426E, 0x2D48, 0x2053, 0x2040, 0x1800,
    0x6004, 0x41EE, 0x2F28, 0x2F01, 0x670A, 0x4840, 0x2007, 0x6608,
    0x0118, 0x2F07, 0x3028, 0x3F2E, 0x302B, 0x226E, 0x2F2B, 0x002C,
    0x670C, 0x225F, 0x6006, 0x00FF, 0x3007, 0xFFEE, 0x5340, 0x0040,
    0xFFE4, 0x4A40, 0x660A, 0x000F, 0x4EAD, 0x70FF, 0x22D8, 0x486B,
    0x0022, 0x204B, 0x670E, 0x4AAE, 0x4E90, 0xFFE0, 0xFFC0, 0x002A,
    0x2740, 0x6702, 0x51C8, 0x02B6, 0x487A, 0x2278, 0xB06E, 0xFFE6,
    0x0009, 0x322E, 0x3E00, 0x4841, 0xFFEA, 0x43EE, 0x4E71, 0x7400,
    0x2F2C, 0x206C, 0x003C, 0x0026, 0x0050, 0x1880, 0x301F, 0x2200,
    0x660C, 0xFFDA, 0x0038, 0x6602, 0x302C, 0x200C, 0x2D6E, 0x4240,
    0xFFE2, 0xA9F0, 0xFF00, 0x377C, 0xE580, 0xFFDC, 0x4868, 0x594F,
    0x0034, 0x3E1F, 0x6008, 0x2F06, 0xFFDE, 0x600A, 0x7002, 0x0032,
    0xFFCC, 0x0080, 0x2251, 0x101F, 0x317C, 0xA029, 0xFFD8, 0x5240,
    0x0100, 0x6710, 0xA023, 0xFFCE, 0xFFD4, 0x2006, 0x4878, 0x002E,
    0x504F, 0x43FA, 0x6712, 0x7600, 0x41E8, 0x4A6E, 0x20D9, 0x005A,
    0x7FFF, 0x51CA, 0x005C, 0x2E00, 0x0240, 0x48C7, 0x6714, 0x0C80,
    0x2E9F, 0xFFD6, 0x8000, 0x1000, 0x4842, 0x4A6B, 0xFFD2, 0x0048,
    0x4A47, 0x4ED1, 0x206F, 0x0041, 0x600C, 0x2A78, 0x422E, 0x3200,
    0x6574, 0x6716, 0x0044, 0x486D, 0x2008, 0x486C, 0x0B7C, 0x2640,
    0x0400, 0x0068, 0x206D, 0x000D, 0x2A40, 0x000B, 0x003E, 0x0220
)

TABLE_DICT = {word: idx for (idx, word) in enumerate(TABLE)}


def unpack(src, _calculate_slop=False):
    if len(src) < 18: raise WrongFormatError

    dst = bytearray()

    pos = 0
    magic, hdrLen, vers, iscmp, unpackSize, _dcmp, _slop, tabSize, comprFlags = struct.unpack_from(">LHBBLHHBB", src, pos)
    pos += 18

    if magic != 0xA89F6572 or hdrLen != 18 or vers != 9 or iscmp != 1 or _dcmp != 2:
        raise WrongFormatError

    hasDynamicTab = comprFlags & 1
    isBitmapped   = comprFlags & 2

    if hasDynamicTab:
        nEntries = tabSize + 1
        dynamicLUT = struct.unpack_from(">" + str(nEntries) + "H", src, pos)
        pos += nEntries * 2
        # dump dynamic LUT
        if 0:
            for idx, elem in enumerate(dynamicLUT):
                if idx and not idx & 3:
                    print(",")
                else:
                    print(", ", end="")
                print("0x%04X" % elem, end="")
            print("")

    LUT = dynamicLUT if hasDynamicTab else TABLE
    nWords = unpackSize >> 1
    hasExtraByte = unpackSize & 1

    LUT = [word.to_bytes(2, 'big') for word in LUT]

    slop = 0
    slop = max(slop, len(dst) + (len(src) - pos) - unpackSize)

    if isBitmapped:
        evenUnpackLen = unpackSize - (unpackSize % 2)
        while len(dst) < evenUnpackLen:
            if not len(dst) & 0xF:
                mask = src[pos]; pos += 1

            if mask & 0x80:
                dst.extend(LUT[src[pos]]); pos += 1
            else:
                dst.append(src[pos]); pos += 1
                dst.append(src[pos]); pos += 1

            mask <<= 1

            slop = max(slop, len(dst) + (len(src) - pos) - unpackSize)
    else:
        while len(dst) < unpackSize & ~1:
            dst.extend(LUT[src[pos]]); pos += 1

            slop = max(slop, len(dst) + (len(src) - pos) - unpackSize)

    if hasExtraByte: # have a got an extra byte at the end?
        dst.append(src[pos]) # copy it over
        pos += 1

    if _calculate_slop: return slop

    return(dst)


def pack_with_flags(src, flags, _defer_slop=False):
    nWords = len(src) >> 1
    inWords = struct.unpack(">" + str(nWords) + "H", src[:nWords*2])

    dst = bytearray(b'\xA8\x9Fer')
    dst.extend(struct.pack('>HBBLH', 0x12, 9, 1, len(src), 2)) # magic, hdrlen, 9=gregg, 1=compressed, size, 2=dcmp
    dst.extend(bytes(4)) # to fill in later
    dst[17] = flags

    # Create a custom lookup table instead of the one at the beginning of the file
    LUT = TABLE_DICT
    if flags & 1:
        import collections
        wordsCounts = collections.Counter(inWords)
        customTab = sorted(wordsCounts, reverse=True, key=lambda word: (wordsCounts[word], word))

        if len(customTab) > 256:
            # The table has 8-bit indices. The Apple compressor short circuits inappropriately in this case.
            del customTab[256:]
        elif flags & 2:
            # If we are able to encode words not in the table, then save space
            # by removing remove rarely used entries from the table
            while customTab and wordsCounts[customTab[-1]] <= 2:
                del customTab[-1]

        # Put the table after the header
        dst[16] = len(customTab) - 1
        dst.extend(struct.pack('>' + str(len(customTab)) + 'H', *customTab))

        # Use our custom function for looking up words
        LUT = {word: idx for (idx, word) in enumerate(customTab)}

    if flags & 2:
        # Use bitmaps to distinguish between verbatim copies and table lookupss
        LUT = LUT.get
        for pos, word in enumerate(inWords):
            if not (pos & 7):
                mask = len(dst)
                dst.append(0)

            result = LUT(word, None)
            if result is None:
                dst.append(word >> 8)
                dst.append(word & 0xFF)
            else:
                dst.append(result)
                dst[mask] |= 0x80 >> (pos & 7)

    else:
        # Table lookups only
        dst.extend(LUT[word] for word in inWords) # triggers https://bugs.python.org/issue37417

    if len(src) & 1: # copy over last byte in the case of odd length
        dst.append(src[-1])

    if not _defer_slop:
        slop = unpack(dst, _calculate_slop=True)
        struct.pack_into('>H', dst, 14, slop)

    return dst


def pack(src):
    if len(src) < 18: return src

    bestCompress = src
    bestSize = len(src)
    for flags in (0, 1, 2, 3):
        try:
            thisCompress = pack_with_flags(src, flags, _defer_slop=True)
        except:
            continue

        thisSize = len(thisCompress)
        # thisSize += struct.unpack_from('>H', thisCompress, 14)[0]
        if thisSize < bestSize:
            bestCompress = thisCompress
            bestSize = thisSize

    if bestCompress is not src:
        slop = unpack(bestCompress, _calculate_slop=True)
        struct.pack_into('>H', bestCompress, 14, slop)

    return bestCompress

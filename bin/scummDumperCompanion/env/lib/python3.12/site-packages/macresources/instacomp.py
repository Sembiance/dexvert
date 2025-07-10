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


'''
    InstaCompOne is an older compression scheme used in the installer SDK
    of the classic Mac OS. Like the famous Deflate algorithm, InstaCompOne
    combines LZ77 with Huffman coding but uses a different bitstream format.

    Author: Max Poliakovski 2018
'''

import struct
from math import ceil, log2


LIT_MAX_LEN = 63 # maximal length of the literal block


''' Huffman codes for copy length.
'''
lenHuffTab = {
    0b00 : 0,
    0b01 : 1,
    0b100 : 2,
    0b1010 : 3,
    0b1011 : 4,
    0b11000 : 5,
    0b11001 : 6,
    0b110100 : 7,
    0b110101 : 8,
    0b110110 : 9,
    0b110111 : 10,

    # for large trees, use compact Huffman table representation in the form
    # prefix_bits : (num_of_val_bits, offset)
    0b1110 : (3, 11),
    0b11110 : (3, 19),
    0b111110 : (5, 27),
    0b1111110 : (6, 59),
    0b11111110 : (7, 123),
    0b111111110 : (8, 251),
    0b1111111110 : (9, 507),
    0b11111111110 : (10, 1019)
}

''' Huffman codes for literal length.
'''
litHuffTab = {
    0b0 : 1,
    0b100 : 2,
    0b101 : 3,
    0b11000 : 4,
    0b11001 : 5,
    0b11010 : 6,
    0b11011 : 7,
    0b1110000 : 8,
    0b1110001 : 9,
    0b1110010 : 10,
    0b1110011 : 11,
    0b1110100 : 12,
    0b1110101 : 13,
    0b1110110 : 14,
    0b1110111 : 15,

    0b11110 : (4, 16),
    0b11111 : (5, 32)
}

# TODO: can that be done more quickly?
next_pow2 = lambda x: 1 if x < 2 else int(ceil(log2(x)))


class BitStreamReader():
    ''' Convenient methods for bitwise access to the input data.
    '''
    def __init__(self, input, size, pos):
        self.inBuf  = input
        self.inSize = size
        self.inPos  = pos
        self.bPool  = 0
        self.bitsInPool = 0

    def showbits(self, nb):
        ''' Return nb bits from the bitstream without advancing the bit position
        '''
        while nb > self.bitsInPool:
            self.bPool = (self.bPool << 8) | self.inBuf[self.inPos]
            self.inPos += 1
            self.bitsInPool += 8

        return (self.bPool >> (self.bitsInPool - nb)) & (0xFFFFFFFF >> (32 - nb))

    def flushbits(self, nb):
        ''' Advance bit position by nb
        '''
        if nb <= self.bitsInPool:
            self.bitsInPool -= nb
        else:
            self.bitsInPool = 0

    def getbits(self, nb):
        ''' Same as showbits with advancing the bit position
        '''
        res = self.showbits(nb)
        self.flushbits(nb)
        return res

    def decodehuff(self, tab, minlen, maxlen):
        ''' Decode Huffman code from bitstream
        '''
        for w in range(minlen, maxlen+1):
            cw = self.showbits(w)
            if cw in tab:
                val = tab[cw]
                if isinstance(val, tuple): # compact format used?
                    self.flushbits(w) # flush prefix bits
                    nbits, start = val
                    val = self.getbits(nbits) + start
                    return val
                self.flushbits(w)
                return val

        raise ValueError('Error decoding Huffman length')


def DecodeDistance(bs, mag):
    ''' Decode backward distance for reference copying. Because this values
        can be large, the magnitude derived from the output position will be
        used to switch between variable-length codes.
        Large values will be further divided into sub-ranges; for each sub-range,
        an additional bit indicating used/skipped sub-range, will be coded.

        Below an example of decoding the bit string 10.0000111 and magnitude of 675:
            1 -> skip sub-range 1...32
            0 -> use sub-range 33...161
                 getbits(7) -> 7 + 33 = 40
    '''
    if mag <= 10:
        raise ValueError('Anon9 unimplemented')

    elif mag <= 20:
        raise ValueError('Anon10 unimplemented')

    elif mag <= 40:
        if bs.getbits(1):
            if bs.getbits(1) == 0:
                return bs.getbits(4) + 5
        raise ValueError('Unimplemented Anon11 distance encoding')

    elif mag <= 80:
        if bs.getbits(1):
            if bs.getbits(1) == 0:
                return bs.getbits(5) + 9
        raise ValueError('Unimplemented Anon12 distance encoding')

    elif mag <= 160:
        if bs.getbits(1):
            if bs.getbits(1) == 0:
                return bs.getbits(6) + 17
        raise ValueError('Unimplemented Anon13 distance encoding')

    elif mag <= 672: # 161...672
        if bs.getbits(1):
            if bs.getbits(1) == 0: # 33...160
                return bs.getbits(7) + 33
            else:
                return bs.getbits(next_pow2(mag - 160)) + 161
        else: # 1...32
            return bs.getbits(5) + 1

    elif mag <= 1000:
        if bs.getbits(1):
            if bs.getbits(1) == 0:
                return bs.getbits(8) + 65
            else:
                return bs.getbits(next_pow2(mag - 320)) + 321
        else:
            return bs.getbits(6) + 1

    elif mag <= 2688:
        if bs.getbits(1):
            if bs.getbits(1) == 0:
                return bs.getbits(9) + 129
            else:
                return bs.getbits(next_pow2(mag - 640)) + 641
        else:
            return bs.getbits(7) + 1

    elif mag <= 5376:
        if bs.getbits(1):
            if bs.getbits(1) == 0:
                return bs.getbits(10) + 257
            else:
                return bs.getbits(next_pow2(mag - 1280)) + 1281
        else:
            return bs.getbits(8) + 1

    elif mag <= 10752:
        if bs.getbits(1):
            if bs.getbits(1):
                return bs.getbits(next_pow2(mag - 2560)) + 2561
            else:
                return bs.getbits(11) + 513
        else:
            return bs.getbits(9) + 1

    raise ValueError('Unimplemented distance encoding, current dst mag: %d' % mag)


def InstaCompDecompress(src, dst, unpackSize, pos=0):
    # skip unused algo specific fields
    word, word2 = struct.unpack_from(">HH", src, pos)
    pos += 4

    bs = BitStreamReader(src, len(src), pos)

    dstPos = 0
    mode = 1 # 1 - literal decoding, 0 - reference copying

    while dstPos < unpackSize:
        copyCount = bs.decodehuff(lenHuffTab, 2, 11)
        if copyCount > 0 or mode == 0:
            copyCount += 2
            if mode == 0:
                copyCount += 1

            distance = DecodeDistance(bs, dstPos)
            refPos = dstPos - distance
            #print("Distance: %d, ref pos: %d" % (distance, refPos))

            for i in range(copyCount):
                dst.append(dst[refPos+i])

            dstPos += copyCount
            mode = 1

        else:
            litLen = bs.decodehuff(litHuffTab, 1, 7)

            for i in range(litLen):
                dst.append(bs.getbits(8))

            dstPos += litLen
            mode = 0 if litLen < LIT_MAX_LEN else 1

    #print(hex(bs.getbits(3)))
    #print(hex(bs.getbits(1)))
    #print(hex(bs.getbits(7)))
    #print(hex(bs.getbits(3)))

    #print(hex(bs.getbits(1)))
    #print(hex(bs.getbits(2)))
    #print(hex(bs.getbits(4)))
    #print(hex(bs.getbits(2)))

    print("current src pos: %d, current dst pos: %d" % (bs.inPos, dstPos))


# End of Max's unchanged code. Here is a simple wrapper...
class WrongFormatError(ValueError):
    pass


def unpack(src):
    try:
        magic, hdrLen, vers, iscmp, unpackSize, dcmp = struct.unpack_from(">LHBBLH", src)
    except struct.error:
        raise WrongFormatError

    if magic != 0xA89F6572 or hdrLen != 18 or vers != 9 or iscmp != 1 or dcmp != 3:
        raise WrongFormatError

    dst = bytearray()
    InstaCompDecompress(src, dst, unpackSize, 14)
    return dst

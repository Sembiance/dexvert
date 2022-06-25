# a decompressor for the 'hammer' compression format
# used in the Acorn Archimedes game 'OddBall'

def hammer_decompress(src):
	src = bytearray(src)

	assert src[0:4] == b'Hmr\0'
	decomp_size = src[4] | (src[5] << 8) | (src[6] << 16) | (src[7] << 24)

	dst = bytearray(decomp_size)

	srcpos = 8
	dstpos = 0
	amount = 0

	while True:
		amount += 1

		control = src[srcpos]
		srcpos += 1
		if control < 0x10:
			repeat = src[srcpos]
			srcpos += 1
			if control == 0xF:
				blocksize = 0x100
			else:
				blocksize = control + 2
			print('(%05x -> %05x) Repeat %02x for %d' % (srcpos - 2, dstpos, repeat, blocksize))

			for i in range(blocksize):
				dst[dstpos] = repeat
				dstpos += 1
		elif control < 0x20:
			blocksize = (control & 0xF) + 1
			print('(%05x -> %05x) Copy %d' % (srcpos - 1, dstpos, blocksize))
			for i in range(blocksize):
				dst[dstpos] = src[srcpos]
				srcpos += 1
				dstpos += 1
		elif control < 0x40:
			secondbyte = src[srcpos]
			srcpos += 1
			blocksize = ((control & 0x1C) >> 2) + 2
			offset = ((control & 3) << 8) + secondbyte
			copyfrom = dstpos - offset - 1
			print('(%05x -> %05x) Reverse copy %d from %d' % (srcpos - 2, dstpos, blocksize, offset))
			for i in range(blocksize):
				dst[dstpos] = dst[copyfrom - i]
				dstpos += 1
		elif control < 0x80:
			secondbyte = src[srcpos]
			srcpos += 1
			blocksize = ((control & 0x38) >> 3) + 2
			offset = ((control & 1) << 8) + secondbyte
			copyfrom = dstpos - offset - 1
			increment = (control & 6) >> 1
			if increment >= 2:
				increment += 1
			increment = 1 << increment
			pos = 0
			print('(%05x -> %05x) Staggered copy %d from offset %d, incr %d' % (srcpos - 2, dstpos, blocksize, offset, increment))
			for i in range(blocksize):
				dst[dstpos] = dst[copyfrom + (pos >> 2)]
				dstpos += 1
				pos += increment
		elif control == 0xFF:
			raise ValueError('overrun')
		else:
			secondbyte = src[srcpos]
			srcpos += 1
			blocksize = ((control & 0x78) >> 3) + 2
			offset = ((control & 7) << 8) + secondbyte
			print('(%05x -> %05x) Copy %d from offset %d' % (srcpos - 2, dstpos, blocksize, offset))
			copyfrom = dstpos - offset - 1
			for i in range(blocksize):
				dst[dstpos] = dst[copyfrom + i]
				dstpos += 1

		if dstpos >= decomp_size:
			break

	return dst




import sys

#infile = 'Oddball/!OddBall/Sounds/MUSIC'
#outfile = 'music_decomp.bin'

if len(sys.argv) != 3:
	print('usage: python %s [infile] [outfile]' % sys.argv[0])
	sys.exit()

infile = sys.argv[1]
outfile = sys.argv[2]

with open(infile, 'rb') as f:
	src = f.read()

with open(outfile, 'wb') as f:
	f.write(hammer_decompress(src))


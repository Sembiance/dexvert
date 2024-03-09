from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.base.basic import Uint


class HeaderFlags(BasicBitfield):

	__name__ = 'HeaderFlags'
	_storage = Uint
	caps = BitfieldMember(pos=0, mask=0x1, return_type=int)
	height = BitfieldMember(pos=1, mask=0x2, return_type=int)
	width = BitfieldMember(pos=2, mask=0x4, return_type=int)
	pitch = BitfieldMember(pos=3, mask=0x8, return_type=int)
	reserved_1 = BitfieldMember(pos=4, mask=0xff0, return_type=int)
	pixel_format = BitfieldMember(pos=12, mask=0x1000, return_type=int)
	reserved_2 = BitfieldMember(pos=13, mask=0x1e000, return_type=int)
	mipmap_count = BitfieldMember(pos=17, mask=0x20000, return_type=int)
	reserved_3 = BitfieldMember(pos=18, mask=0x40000, return_type=int)
	linear_size = BitfieldMember(pos=19, mask=0x80000, return_type=int)
	reserved_4 = BitfieldMember(pos=20, mask=0x700000, return_type=int)
	depth = BitfieldMember(pos=23, mask=0x800000, return_type=int)

	def set_defaults(self):
		self.caps = 1
		self.pixel_format = 1

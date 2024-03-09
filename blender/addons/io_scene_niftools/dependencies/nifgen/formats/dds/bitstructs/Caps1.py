from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.base.basic import Uint


class Caps1(BasicBitfield):

	__name__ = 'Caps1'
	_storage = Uint
	reserved_1 = BitfieldMember(pos=0, mask=0x7, return_type=int)
	complex = BitfieldMember(pos=3, mask=0x8, return_type=int)
	reserved_2 = BitfieldMember(pos=4, mask=0xff0, return_type=int)
	texture = BitfieldMember(pos=12, mask=0x1000, return_type=int)
	reserved_3 = BitfieldMember(pos=13, mask=0x3fe000, return_type=int)
	mipmap = BitfieldMember(pos=22, mask=0x400000, return_type=int)

	def set_defaults(self):
		self.texture = 1

from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.base.basic import Int
from nifgen.formats.manis.basic import Int48


class PosBaseKey(BasicBitfield):

	__name__ = 'PosBaseKey'
	_storage = Int48
	x = BitfieldMember(pos=0, mask=0x7fff, return_type=Int.from_value)
	y = BitfieldMember(pos=15, mask=0x3fff8000, return_type=Int.from_value)
	z = BitfieldMember(pos=30, mask=0x1fffc0000000, return_type=Int.from_value)

	def set_defaults(self):
		pass

from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.base.basic import Ubyte


class TurnFlags(BasicBitfield):

	__name__ = 'TurnFlags'
	_storage = Ubyte
	looping = BitfieldMember(pos=0, mask=0x1, return_type=int)
	clockwise = BitfieldMember(pos=1, mask=0x2, return_type=int)
	use_midpoint = BitfieldMember(pos=2, mask=0x4, return_type=int)

	def set_defaults(self):
		pass

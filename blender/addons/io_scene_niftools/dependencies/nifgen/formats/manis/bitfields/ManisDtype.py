from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.base.basic import Int
from nifgen.formats.base.basic import Uint


class ManisDtype(BasicBitfield):

	"""
	# PZ dtypes: 0, 1, 4, 5, 6, 32, 34, 36, 37, 38
	# JWE2 dev dtypes: 0, 4, 5, 6, 32, 34, 36, 37, 38
	# JWE2 dtypes: 0, 4, 5, 6, 64, 66, 68, 69, 70
	ManisDtype: 0 0b0 ['compression = 0', 'use_ushort = 0', 'has_list = 0']
	ManisDtype: 1 0b1 ['compression = 1', 'use_ushort = 0', 'has_list = 0']
	ManisDtype: 4 0b100 ['compression = 4', 'use_ushort = 0', 'has_list = 0']
	ManisDtype: 5 0b101 ['compression = 5', 'use_ushort = 0', 'has_list = 0']
	ManisDtype: 6 0b110 ['compression = 6', 'use_ushort = 0', 'has_list = 0']
	ManisDtype: 32 0b100000 ['compression = 0', 'use_ushort = 0', 'has_list = 1']
	ManisDtype: 34 0b100010 ['compression = 2', 'use_ushort = 0', 'has_list = 1']
	ManisDtype: 36 0b100100 ['compression = 4', 'use_ushort = 0', 'has_list = 1']
	ManisDtype: 37 0b100101 ['compression = 5', 'use_ushort = 0', 'has_list = 1']
	ManisDtype: 38 0b100110 ['compression = 6', 'use_ushort = 0', 'has_list = 1']
	ManisDtype: 64 0b1000000 ['compression = 0', 'use_ushort = 0', 'has_list = 2']
	ManisDtype: 66 0b1000010 ['compression = 2', 'use_ushort = 0', 'has_list = 2']
	ManisDtype: 68 0b1000100 ['compression = 4', 'use_ushort = 0', 'has_list = 2']
	ManisDtype: 69 0b1000101 ['compression = 5', 'use_ushort = 0', 'has_list = 2']
	ManisDtype: 70 0b1000110 ['compression = 6', 'use_ushort = 0', 'has_list = 2']
	ManisDtype: 82 0b1010010 ['compression = 2', 'use_ushort = 1', 'has_list = 2']
	"""

	__name__ = 'ManisDtype'
	_storage = Uint
	compression = BitfieldMember(pos=0, mask=0xf, return_type=Int.from_value)
	use_ushort = BitfieldMember(pos=4, mask=0x10, return_type=Int.from_value)
	has_list = BitfieldMember(pos=5, mask=0x60, return_type=Int.from_value)

	def set_defaults(self):
		pass

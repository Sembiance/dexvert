from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.nif.basic import Ushort


class PathFlags(BasicBitfield):

	__name__ = 'PathFlags'
	_storage = Ushort
	C_V_DATA_NEEDS_UPDATE = 2 ** 0
	CURVE_TYPE_OPEN = 2 ** 1
	ALLOW_FLIP = 2 ** 2
	BANK = 2 ** 3
	CONSTANT_VELOCITY = 2 ** 4
	FOLLOW = 2 ** 5
	FLIP = 2 ** 6
	c_v_data_needs_update = BitfieldMember(pos=0, mask=0x1, return_type=bool)
	curve_type_open = BitfieldMember(pos=1, mask=0x2, return_type=bool)
	allow_flip = BitfieldMember(pos=2, mask=0x4, return_type=bool)
	bank = BitfieldMember(pos=3, mask=0x8, return_type=bool)
	constant_velocity = BitfieldMember(pos=4, mask=0x10, return_type=bool)
	follow = BitfieldMember(pos=5, mask=0x20, return_type=bool)
	flip = BitfieldMember(pos=6, mask=0x40, return_type=bool)

	def set_defaults(self):
		pass

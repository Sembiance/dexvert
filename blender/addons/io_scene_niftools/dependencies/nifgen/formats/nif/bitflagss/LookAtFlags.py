from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.nif.basic import Ushort


class LookAtFlags(BasicBitfield):

	__name__ = 'LookAtFlags'
	_storage = Ushort
	LOOK_FLIP = 2 ** 0
	LOOK_Y_AXIS = 2 ** 1
	LOOK_Z_AXIS = 2 ** 2
	look_flip = BitfieldMember(pos=0, mask=0x1, return_type=bool)
	look_y_axis = BitfieldMember(pos=1, mask=0x2, return_type=bool)
	look_z_axis = BitfieldMember(pos=2, mask=0x4, return_type=bool)

	def set_defaults(self):
		pass

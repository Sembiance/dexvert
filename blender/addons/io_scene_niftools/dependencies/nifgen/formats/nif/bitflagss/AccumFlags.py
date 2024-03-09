from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.nif.basic import Uint


class AccumFlags(BasicBitfield):

	"""
	Describes the options for the accum root on NiControllerSequence.
	"""

	__name__ = 'AccumFlags'
	_storage = Uint
	ACCUM_X_TRANS = 2 ** 0
	ACCUM_Y_TRANS = 2 ** 1
	ACCUM_Z_TRANS = 2 ** 2
	ACCUM_X_ROT = 2 ** 3
	ACCUM_Y_ROT = 2 ** 4
	ACCUM_Z_ROT = 2 ** 5
	ACCUM_X_FRONT = 2 ** 6
	ACCUM_Y_FRONT = 2 ** 7
	ACCUM_Z_FRONT = 2 ** 8
	ACCUM_NEG_FRONT = 2 ** 9
	accum_x_trans = BitfieldMember(pos=0, mask=0x1, return_type=bool)
	accum_y_trans = BitfieldMember(pos=1, mask=0x2, return_type=bool)
	accum_z_trans = BitfieldMember(pos=2, mask=0x4, return_type=bool)
	accum_x_rot = BitfieldMember(pos=3, mask=0x8, return_type=bool)
	accum_y_rot = BitfieldMember(pos=4, mask=0x10, return_type=bool)
	accum_z_rot = BitfieldMember(pos=5, mask=0x20, return_type=bool)
	accum_x_front = BitfieldMember(pos=6, mask=0x40, return_type=bool)
	accum_y_front = BitfieldMember(pos=7, mask=0x80, return_type=bool)
	accum_z_front = BitfieldMember(pos=8, mask=0x100, return_type=bool)
	accum_neg_front = BitfieldMember(pos=9, mask=0x200, return_type=bool)

	def set_defaults(self):
		pass

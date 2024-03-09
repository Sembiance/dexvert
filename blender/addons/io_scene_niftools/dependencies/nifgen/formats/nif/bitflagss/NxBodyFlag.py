from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.nif.basic import Uint


class NxBodyFlag(BasicBitfield):

	__name__ = 'NxBodyFlag'
	_storage = Uint
	DISABLE_GRAVITY = 2 ** 0
	FROZEN_POS_X = 2 ** 1
	FROZEN_POS_Y = 2 ** 2
	FROZEN_POS_Z = 2 ** 3
	FROZEN_ROT_X = 2 ** 4
	FROZEN_ROT_Y = 2 ** 5
	FROZEN_ROT_Z = 2 ** 6
	KINEMATIC = 2 ** 7
	VISUALIZATION = 2 ** 8
	POSE_SLEEP_TEST = 2 ** 9
	FILTER_SLEEP_VEL = 2 ** 10
	ENERGY_SLEEP_TEST = 2 ** 11
	disable_gravity = BitfieldMember(pos=0, mask=0x1, return_type=bool)
	frozen_pos_x = BitfieldMember(pos=1, mask=0x2, return_type=bool)
	frozen_pos_y = BitfieldMember(pos=2, mask=0x4, return_type=bool)
	frozen_pos_z = BitfieldMember(pos=3, mask=0x8, return_type=bool)
	frozen_rot_x = BitfieldMember(pos=4, mask=0x10, return_type=bool)
	frozen_rot_y = BitfieldMember(pos=5, mask=0x20, return_type=bool)
	frozen_rot_z = BitfieldMember(pos=6, mask=0x40, return_type=bool)
	kinematic = BitfieldMember(pos=7, mask=0x80, return_type=bool)
	visualization = BitfieldMember(pos=8, mask=0x100, return_type=bool)
	pose_sleep_test = BitfieldMember(pos=9, mask=0x200, return_type=bool)
	filter_sleep_vel = BitfieldMember(pos=10, mask=0x400, return_type=bool)
	energy_sleep_test = BitfieldMember(pos=11, mask=0x800, return_type=bool)

	def set_defaults(self):
		pass

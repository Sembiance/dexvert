from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.nif.basic import Ushort


class AspectFlags(BasicBitfield):

	__name__ = 'AspectFlags'
	_storage = Ushort
	VELOCITY_ORIENTATION = 2 ** 0
	INITIAL_ROTATION_FROM_VELOCITY = 2 ** 1
	SPEED_TO_ASPECT_ENABLED = 2 ** 8
	velocity_orientation = BitfieldMember(pos=0, mask=0x1, return_type=bool)
	initial_rotation_from_velocity = BitfieldMember(pos=1, mask=0x2, return_type=bool)
	speed_to_aspect_enabled = BitfieldMember(pos=8, mask=0x100, return_type=bool)

	def set_defaults(self):
		pass

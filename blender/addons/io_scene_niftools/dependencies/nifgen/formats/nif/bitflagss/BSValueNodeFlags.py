from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.nif.basic import Byte


class BSValueNodeFlags(BasicBitfield):

	"""
	Flags for BSValueNode.
	"""

	__name__ = 'BSValueNodeFlags'
	_storage = Byte
	BILLBOARD_WORLD_Z = 2 ** 0
	USE_PLAYER_ADJUST = 2 ** 1
	billboard_world_z = BitfieldMember(pos=0, mask=0x1, return_type=bool)
	use_player_adjust = BitfieldMember(pos=1, mask=0x2, return_type=bool)

	def set_defaults(self):
		pass

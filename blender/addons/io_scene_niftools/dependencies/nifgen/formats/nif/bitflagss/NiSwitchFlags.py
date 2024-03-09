from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.nif.basic import Ushort


class NiSwitchFlags(BasicBitfield):

	"""
	Flags for NiSwitchNode.
	"""

	__name__ = 'NiSwitchFlags'
	_storage = Ushort
	UPDATE_ONLY_ACTIVE_CHILD = 2 ** 0
	UPDATE_CONTROLLERS = 2 ** 1
	update_only_active_child = BitfieldMember(pos=0, mask=0x1, return_type=bool)
	update_controllers = BitfieldMember(pos=1, mask=0x2, return_type=bool)

	def set_defaults(self):
		pass

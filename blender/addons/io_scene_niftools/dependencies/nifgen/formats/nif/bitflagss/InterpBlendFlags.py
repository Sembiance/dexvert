from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.nif.basic import Byte


class InterpBlendFlags(BasicBitfield):

	"""
	Flags for NiBlendInterpolator
	"""

	__name__ = 'InterpBlendFlags'
	_storage = Byte
	MANAGER_CONTROLLED = 2 ** 0
	USE_ONLY_HIGHEST_WEIGHT = 2 ** 1
	manager_controlled = BitfieldMember(pos=0, mask=0x1, return_type=bool)
	use_only_highest_weight = BitfieldMember(pos=1, mask=0x2, return_type=bool)

	def set_defaults(self):
		pass

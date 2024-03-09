from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.base.basic import Uint
from nifgen.formats.ovl_base.basic import Bool


class ModelFlagZT(BasicBitfield):

	"""
	Determines the data held by a mesh.
	"""

	__name__ = 'ModelFlagZT'
	_storage = Uint
	stripify = BitfieldMember(pos=6, mask=0x40, return_type=Bool.from_value)
	repeat_tris = BitfieldMember(pos=9, mask=0x200, return_type=Bool.from_value)

	def set_defaults(self):
		pass

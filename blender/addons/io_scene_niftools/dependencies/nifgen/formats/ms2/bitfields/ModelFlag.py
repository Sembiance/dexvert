from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.base.basic import Uint
from nifgen.formats.ovl_base.basic import Bool


class ModelFlag(BasicBitfield):

	"""
	Determines the data held by a mesh.
	"""

	__name__ = 'ModelFlag'
	_storage = Uint
	stripify = BitfieldMember(pos=3, mask=0x8, return_type=Bool.from_value)
	weights = BitfieldMember(pos=4, mask=0x10, return_type=Bool.from_value)
	repeat_tris = BitfieldMember(pos=5, mask=0x20, return_type=Bool.from_value)
	fur_shells = BitfieldMember(pos=8, mask=0x100, return_type=Bool.from_value)
	basic_info = BitfieldMember(pos=9, mask=0x200, return_type=Bool.from_value)

	def set_defaults(self):
		pass

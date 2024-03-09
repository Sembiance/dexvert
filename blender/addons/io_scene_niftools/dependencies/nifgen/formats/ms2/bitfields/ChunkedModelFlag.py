from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.base.basic import Uint
from nifgen.formats.ovl_base.basic import Bool


class ChunkedModelFlag(BasicBitfield):

	"""
	Determines the data held by a mesh.
	"""

	__name__ = 'ChunkedModelFlag'
	_storage = Uint
	flat_arrays = BitfieldMember(pos=0, mask=0x1, return_type=Bool.from_value)
	fur_shells = BitfieldMember(pos=2, mask=0x4, return_type=Bool.from_value)
	fur_shells_2 = BitfieldMember(pos=3, mask=0x8, return_type=Bool.from_value)

	def set_defaults(self):
		pass

from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.nif.basic import Bool
from nifgen.formats.nif.basic import Ushort
from nifgen.formats.nif.enums.AlphaFunction import AlphaFunction
from nifgen.formats.nif.enums.TestFunction import TestFunction


class AlphaFlags(BasicBitfield):

	"""
	Flags for NiAlphaProperty
	"""

	__name__ = 'AlphaFlags'
	_storage = Ushort
	alpha_blend = BitfieldMember(pos=0, mask=0x0001, return_type=Bool.from_value)
	source_blend_mode = BitfieldMember(pos=1, mask=0x001E, return_type=AlphaFunction.from_value)
	destination_blend_mode = BitfieldMember(pos=5, mask=0x01E0, return_type=AlphaFunction.from_value)
	alpha_test = BitfieldMember(pos=9, mask=0x0200, return_type=Bool.from_value)
	test_func = BitfieldMember(pos=10, mask=0x1C00, return_type=TestFunction.from_value)
	no_sorter = BitfieldMember(pos=13, mask=0x2000, return_type=Bool.from_value)
	clone_unique = BitfieldMember(pos=14, mask=0x4000, return_type=Bool.from_value)
	editor_alpha_threshold = BitfieldMember(pos=15, mask=0x8000, return_type=Bool.from_value)

	def set_defaults(self):
		self.source_blend_mode = AlphaFunction.SRC_ALPHA
		self.destination_blend_mode = AlphaFunction.INV_SRC_ALPHA
		self.alpha_test = True
		self.test_func = TestFunction.TEST_GREATER

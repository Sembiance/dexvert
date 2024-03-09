from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.nif.basic import Bool
from nifgen.formats.nif.basic import Ushort
from nifgen.formats.nif.enums.StencilAction import StencilAction
from nifgen.formats.nif.enums.StencilDrawMode import StencilDrawMode
from nifgen.formats.nif.enums.StencilTestFunc import StencilTestFunc


class StencilFlags(BasicBitfield):

	"""
	Flags for NiStencilProperty
	"""

	__name__ = 'StencilFlags'
	_storage = Ushort
	enable = BitfieldMember(pos=0, mask=0x0001, return_type=Bool.from_value)
	fail_action = BitfieldMember(pos=1, mask=0x000E, return_type=StencilAction.from_value)
	z_fail_action = BitfieldMember(pos=4, mask=0x0070, return_type=StencilAction.from_value)
	pass_action = BitfieldMember(pos=7, mask=0x0380, return_type=StencilAction.from_value)
	draw_mode = BitfieldMember(pos=10, mask=0x0C00, return_type=StencilDrawMode.from_value)
	test_func = BitfieldMember(pos=12, mask=0xF000, return_type=StencilTestFunc.from_value)

	def set_defaults(self):
		self.fail_action = StencilAction.ACTION_KEEP
		self.z_fail_action = StencilAction.ACTION_KEEP
		self.pass_action = StencilAction.ACTION_INCREMENT
		self.draw_mode = StencilDrawMode.DRAW_BOTH
		self.test_func = StencilTestFunc.TEST_GREATER

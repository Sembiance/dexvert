from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.nif.basic import Ushort


class NiShadowGeneratorFlags(BasicBitfield):

	"""
	Flags for NiShadowGenerator.
	Bit Patterns:
	AUTO_CALC_NEARFAR = (AUTO_NEAR_DIST | AUTO_FAR_DIST) = 0xC0
	AUTO_CALC_FULL = (AUTO_NEAR_DIST | AUTO_FAR_DIST | AUTO_DIR_LIGHT_FRUSTUM_WIDTH | AUTO_DIR_LIGHT_FRUSTUM_POSITION) = 0x3C0
	"""

	__name__ = 'NiShadowGeneratorFlags'
	_storage = Ushort
	DIRTY_SHADOWMAP = 2 ** 0
	DIRTY_RENDERVIEWS = 2 ** 1
	GEN_STATIC = 2 ** 2
	GEN_ACTIVE = 2 ** 3
	RENDER_BACKFACES = 2 ** 4
	STRICTLY_OBSERVE_SIZE_HINT = 2 ** 5
	AUTO_NEAR_DIST = 2 ** 6
	AUTO_FAR_DIST = 2 ** 7
	AUTO_DIR_LIGHT_FRUSTUM_WIDTH = 2 ** 8
	AUTO_DIR_LIGHT_FRUSTUM_POSITION = 2 ** 9
	dirty_shadowmap = BitfieldMember(pos=0, mask=0x1, return_type=bool)
	dirty_renderviews = BitfieldMember(pos=1, mask=0x2, return_type=bool)
	gen_static = BitfieldMember(pos=2, mask=0x4, return_type=bool)
	gen_active = BitfieldMember(pos=3, mask=0x8, return_type=bool)
	render_backfaces = BitfieldMember(pos=4, mask=0x10, return_type=bool)
	strictly_observe_size_hint = BitfieldMember(pos=5, mask=0x20, return_type=bool)
	auto_near_dist = BitfieldMember(pos=6, mask=0x40, return_type=bool)
	auto_far_dist = BitfieldMember(pos=7, mask=0x80, return_type=bool)
	auto_dir_light_frustum_width = BitfieldMember(pos=8, mask=0x100, return_type=bool)
	auto_dir_light_frustum_position = BitfieldMember(pos=9, mask=0x200, return_type=bool)

	def set_defaults(self):
		pass

from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.nif.basic import Uint


class WaterShaderPropertyFlags(BasicBitfield):

	"""
	Skyrim water shader property flags
	"""

	__name__ = 'WaterShaderPropertyFlags'
	_storage = Uint
	DISPLACEMENT = 2 ** 0
	LOD = 2 ** 1
	DEPTH = 2 ** 2
	ACTOR_IN_WATER = 2 ** 3
	ACTOR_IN_WATER_IS_MOVING = 2 ** 4
	UNDERWATER = 2 ** 5
	REFLECTIONS = 2 ** 6
	REFRACTIONS = 2 ** 7
	VERTEX_UV = 2 ** 8
	VERTEX_ALPHA_DEPTH = 2 ** 9
	PROCEDURAL = 2 ** 10
	FOG = 2 ** 11
	UPDATE_CONSTANTS = 2 ** 12
	CUBEMAP = 2 ** 13
	displacement = BitfieldMember(pos=0, mask=0x1, return_type=bool)
	lod = BitfieldMember(pos=1, mask=0x2, return_type=bool)
	depth = BitfieldMember(pos=2, mask=0x4, return_type=bool)
	actor_in_water = BitfieldMember(pos=3, mask=0x8, return_type=bool)
	actor_in_water_is_moving = BitfieldMember(pos=4, mask=0x10, return_type=bool)
	underwater = BitfieldMember(pos=5, mask=0x20, return_type=bool)
	reflections = BitfieldMember(pos=6, mask=0x40, return_type=bool)
	refractions = BitfieldMember(pos=7, mask=0x80, return_type=bool)
	vertex_uv = BitfieldMember(pos=8, mask=0x100, return_type=bool)
	vertex_alpha_depth = BitfieldMember(pos=9, mask=0x200, return_type=bool)
	procedural = BitfieldMember(pos=10, mask=0x400, return_type=bool)
	fog = BitfieldMember(pos=11, mask=0x800, return_type=bool)
	update_constants = BitfieldMember(pos=12, mask=0x1000, return_type=bool)
	cubemap = BitfieldMember(pos=13, mask=0x2000, return_type=bool)

	def set_defaults(self):
		pass

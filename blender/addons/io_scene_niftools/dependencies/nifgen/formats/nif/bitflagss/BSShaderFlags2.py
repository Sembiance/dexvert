from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.nif.basic import Uint


class BSShaderFlags2(BasicBitfield):

	"""
	Shader Property Flags 2
	"""

	__name__ = 'BSShaderFlags2'
	_storage = Uint
	Z_BUFFER_WRITE = 2 ** 0
	LOD_LANDSCAPE = 2 ** 1
	LOD_BUILDING = 2 ** 2
	NO_FADE = 2 ** 3
	REFRACTION_TINT = 2 ** 4
	VERTEX_COLORS = 2 ** 5
	UNKNOWN_1 = 2 ** 6
	FIRST_LIGHT_IS_POINT_LIGHT = 2 ** 7
	SECOND_LIGHT = 2 ** 8
	THIRD_LIGHT = 2 ** 9
	VERTEX_LIGHTING = 2 ** 10
	UNIFORM_SCALE = 2 ** 11
	FIT_SLOPE = 2 ** 12
	BILLBOARD_AND_ENVMAP_LIGHT_FADE = 2 ** 13
	NO_LOD_LAND_BLEND = 2 ** 14
	ENVMAP_LIGHT_FADE = 2 ** 15
	WIREFRAME = 2 ** 16
	VATS_SELECTION = 2 ** 17
	SHOW_IN_LOCAL_MAP = 2 ** 18
	PREMULT_ALPHA = 2 ** 19
	SKIP_NORMAL_MAPS = 2 ** 20
	ALPHA_DECAL = 2 ** 21
	NO_TRANSPARECNY_MULTISAMPLING = 2 ** 22
	UNKNOWN_2 = 2 ** 23
	UNKNOWN_3 = 2 ** 24
	UNKNOWN_4 = 2 ** 25
	UNKNOWN_5 = 2 ** 26
	UNKNOWN_6 = 2 ** 27
	UNKNOWN_7 = 2 ** 28
	UNKNOWN_8 = 2 ** 29
	UNKNOWN_9 = 2 ** 30
	UNKNOWN_10 = 2 ** 31
	z_buffer_write = BitfieldMember(pos=0, mask=0x1, return_type=bool)
	lod_landscape = BitfieldMember(pos=1, mask=0x2, return_type=bool)
	lod_building = BitfieldMember(pos=2, mask=0x4, return_type=bool)
	no_fade = BitfieldMember(pos=3, mask=0x8, return_type=bool)
	refraction_tint = BitfieldMember(pos=4, mask=0x10, return_type=bool)
	vertex_colors = BitfieldMember(pos=5, mask=0x20, return_type=bool)
	unknown_1 = BitfieldMember(pos=6, mask=0x40, return_type=bool)
	first_light_is_point_light = BitfieldMember(pos=7, mask=0x80, return_type=bool)
	second_light = BitfieldMember(pos=8, mask=0x100, return_type=bool)
	third_light = BitfieldMember(pos=9, mask=0x200, return_type=bool)
	vertex_lighting = BitfieldMember(pos=10, mask=0x400, return_type=bool)
	uniform_scale = BitfieldMember(pos=11, mask=0x800, return_type=bool)
	fit_slope = BitfieldMember(pos=12, mask=0x1000, return_type=bool)
	billboard_and_envmap_light_fade = BitfieldMember(pos=13, mask=0x2000, return_type=bool)
	no_lod_land_blend = BitfieldMember(pos=14, mask=0x4000, return_type=bool)
	envmap_light_fade = BitfieldMember(pos=15, mask=0x8000, return_type=bool)
	wireframe = BitfieldMember(pos=16, mask=0x10000, return_type=bool)
	vats_selection = BitfieldMember(pos=17, mask=0x20000, return_type=bool)
	show_in_local_map = BitfieldMember(pos=18, mask=0x40000, return_type=bool)
	premult_alpha = BitfieldMember(pos=19, mask=0x80000, return_type=bool)
	skip_normal_maps = BitfieldMember(pos=20, mask=0x100000, return_type=bool)
	alpha_decal = BitfieldMember(pos=21, mask=0x200000, return_type=bool)
	no_transparecny_multisampling = BitfieldMember(pos=22, mask=0x400000, return_type=bool)
	unknown_2 = BitfieldMember(pos=23, mask=0x800000, return_type=bool)
	unknown_3 = BitfieldMember(pos=24, mask=0x1000000, return_type=bool)
	unknown_4 = BitfieldMember(pos=25, mask=0x2000000, return_type=bool)
	unknown_5 = BitfieldMember(pos=26, mask=0x4000000, return_type=bool)
	unknown_6 = BitfieldMember(pos=27, mask=0x8000000, return_type=bool)
	unknown_7 = BitfieldMember(pos=28, mask=0x10000000, return_type=bool)
	unknown_8 = BitfieldMember(pos=29, mask=0x20000000, return_type=bool)
	unknown_9 = BitfieldMember(pos=30, mask=0x40000000, return_type=bool)
	unknown_10 = BitfieldMember(pos=31, mask=0x80000000, return_type=bool)

	def set_defaults(self):
		pass

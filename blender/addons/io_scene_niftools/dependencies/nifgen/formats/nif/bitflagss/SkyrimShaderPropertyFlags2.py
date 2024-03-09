from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.nif.basic import Uint


class SkyrimShaderPropertyFlags2(BasicBitfield):

	"""
	Skyrim Shader Property Flags 2
	"""

	__name__ = 'SkyrimShaderPropertyFlags2'
	_storage = Uint
	Z_BUFFER_WRITE = 2 ** 0
	LOD_LANDSCAPE = 2 ** 1
	LOD_OBJECTS = 2 ** 2
	NO_FADE = 2 ** 3
	DOUBLE_SIDED = 2 ** 4
	VERTEX_COLORS = 2 ** 5
	GLOW_MAP = 2 ** 6
	ASSUME_SHADOWMASK = 2 ** 7
	PACKED_TANGENT = 2 ** 8
	MULTI_INDEX_SNOW = 2 ** 9
	VERTEX_LIGHTING = 2 ** 10
	UNIFORM_SCALE = 2 ** 11
	FIT_SLOPE = 2 ** 12
	BILLBOARD = 2 ** 13
	NO_LOD_LAND_BLEND = 2 ** 14
	ENV_MAP_LIGHT_FADE = 2 ** 15
	WIREFRAME = 2 ** 16
	WEAPON_BLOOD = 2 ** 17
	HIDE_ON_LOCAL_MAP = 2 ** 18
	PREMULT_ALPHA = 2 ** 19
	CLOUD_LOD = 2 ** 20
	ANISOTROPIC_LIGHTING = 2 ** 21
	NO_TRANSPARENCY_MULTISAMPLING = 2 ** 22
	UNUSED_01 = 2 ** 23
	MULTI_LAYER_PARALLAX = 2 ** 24
	SOFT_LIGHTING = 2 ** 25
	RIM_LIGHTING = 2 ** 26
	BACK_LIGHTING = 2 ** 27
	UNUSED_02 = 2 ** 28
	TREE_ANIM = 2 ** 29
	EFFECT_LIGHTING = 2 ** 30
	HD_LOD_OBJECTS = 2 ** 31
	z_buffer_write = BitfieldMember(pos=0, mask=0x1, return_type=bool)
	lod_landscape = BitfieldMember(pos=1, mask=0x2, return_type=bool)
	lod_objects = BitfieldMember(pos=2, mask=0x4, return_type=bool)
	no_fade = BitfieldMember(pos=3, mask=0x8, return_type=bool)
	double_sided = BitfieldMember(pos=4, mask=0x10, return_type=bool)
	vertex_colors = BitfieldMember(pos=5, mask=0x20, return_type=bool)
	glow_map = BitfieldMember(pos=6, mask=0x40, return_type=bool)
	assume_shadowmask = BitfieldMember(pos=7, mask=0x80, return_type=bool)
	packed_tangent = BitfieldMember(pos=8, mask=0x100, return_type=bool)
	multi_index_snow = BitfieldMember(pos=9, mask=0x200, return_type=bool)
	vertex_lighting = BitfieldMember(pos=10, mask=0x400, return_type=bool)
	uniform_scale = BitfieldMember(pos=11, mask=0x800, return_type=bool)
	fit_slope = BitfieldMember(pos=12, mask=0x1000, return_type=bool)
	billboard = BitfieldMember(pos=13, mask=0x2000, return_type=bool)
	no_lod_land_blend = BitfieldMember(pos=14, mask=0x4000, return_type=bool)
	env_map_light_fade = BitfieldMember(pos=15, mask=0x8000, return_type=bool)
	wireframe = BitfieldMember(pos=16, mask=0x10000, return_type=bool)
	weapon_blood = BitfieldMember(pos=17, mask=0x20000, return_type=bool)
	hide_on_local_map = BitfieldMember(pos=18, mask=0x40000, return_type=bool)
	premult_alpha = BitfieldMember(pos=19, mask=0x80000, return_type=bool)
	cloud_lod = BitfieldMember(pos=20, mask=0x100000, return_type=bool)
	anisotropic_lighting = BitfieldMember(pos=21, mask=0x200000, return_type=bool)
	no_transparency_multisampling = BitfieldMember(pos=22, mask=0x400000, return_type=bool)
	unused_01 = BitfieldMember(pos=23, mask=0x800000, return_type=bool)
	multi_layer_parallax = BitfieldMember(pos=24, mask=0x1000000, return_type=bool)
	soft_lighting = BitfieldMember(pos=25, mask=0x2000000, return_type=bool)
	rim_lighting = BitfieldMember(pos=26, mask=0x4000000, return_type=bool)
	back_lighting = BitfieldMember(pos=27, mask=0x8000000, return_type=bool)
	unused_02 = BitfieldMember(pos=28, mask=0x10000000, return_type=bool)
	tree_anim = BitfieldMember(pos=29, mask=0x20000000, return_type=bool)
	effect_lighting = BitfieldMember(pos=30, mask=0x40000000, return_type=bool)
	hd_lod_objects = BitfieldMember(pos=31, mask=0x80000000, return_type=bool)

	def set_defaults(self):
		pass

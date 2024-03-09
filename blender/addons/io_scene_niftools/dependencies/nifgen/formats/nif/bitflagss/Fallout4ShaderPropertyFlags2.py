from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.nif.basic import Uint


class Fallout4ShaderPropertyFlags2(BasicBitfield):

	"""
	Fallout 4 Shader Property Flags 2
	"""

	__name__ = 'Fallout4ShaderPropertyFlags2'
	_storage = Uint
	Z_BUFFER_WRITE = 2 ** 0
	LOD_LANDSCAPE = 2 ** 1
	LOD_OBJECTS = 2 ** 2
	NO_FADE = 2 ** 3
	DOUBLE_SIDED = 2 ** 4
	VERTEX_COLORS = 2 ** 5
	GLOW_MAP = 2 ** 6
	TRANSFORM_CHANGED = 2 ** 7
	DISMEMBERMENT_MEATCUFF = 2 ** 8
	TINT = 2 ** 9
	GRASS_VERTEX_LIGHTING = 2 ** 10
	GRASS_UNIFORM_SCALE = 2 ** 11
	GRASS_FIT_SLOPE = 2 ** 12
	GRASS_BILLBOARD = 2 ** 13
	NO_LOD_LAND_BLEND = 2 ** 14
	DISMEMBERMENT = 2 ** 15
	WIREFRAME = 2 ** 16
	WEAPON_BLOOD = 2 ** 17
	HIDE_ON_LOCAL_MAP = 2 ** 18
	PREMULT_ALPHA = 2 ** 19
	VATS_TARGET = 2 ** 20
	ANISOTROPIC_LIGHTING = 2 ** 21
	SKEW_SPECULAR_ALPHA = 2 ** 22
	MENU_SCREEN = 2 ** 23
	MULTI_LAYER_PARALLAX = 2 ** 24
	ALPHA_TEST = 2 ** 25
	GRADIENT_REMAP = 2 ** 26
	VATS_TARGET_DRAW_ALL = 2 ** 27
	PIPBOY_SCREEN = 2 ** 28
	TREE_ANIM = 2 ** 29
	EFFECT_LIGHTING = 2 ** 30
	REFRACTION_WRITES_DEPTH = 2 ** 31
	z_buffer_write = BitfieldMember(pos=0, mask=0x1, return_type=bool)
	lod_landscape = BitfieldMember(pos=1, mask=0x2, return_type=bool)
	lod_objects = BitfieldMember(pos=2, mask=0x4, return_type=bool)
	no_fade = BitfieldMember(pos=3, mask=0x8, return_type=bool)
	double_sided = BitfieldMember(pos=4, mask=0x10, return_type=bool)
	vertex_colors = BitfieldMember(pos=5, mask=0x20, return_type=bool)
	glow_map = BitfieldMember(pos=6, mask=0x40, return_type=bool)
	transform_changed = BitfieldMember(pos=7, mask=0x80, return_type=bool)
	dismemberment_meatcuff = BitfieldMember(pos=8, mask=0x100, return_type=bool)
	tint = BitfieldMember(pos=9, mask=0x200, return_type=bool)
	grass_vertex_lighting = BitfieldMember(pos=10, mask=0x400, return_type=bool)
	grass_uniform_scale = BitfieldMember(pos=11, mask=0x800, return_type=bool)
	grass_fit_slope = BitfieldMember(pos=12, mask=0x1000, return_type=bool)
	grass_billboard = BitfieldMember(pos=13, mask=0x2000, return_type=bool)
	no_lod_land_blend = BitfieldMember(pos=14, mask=0x4000, return_type=bool)
	dismemberment = BitfieldMember(pos=15, mask=0x8000, return_type=bool)
	wireframe = BitfieldMember(pos=16, mask=0x10000, return_type=bool)
	weapon_blood = BitfieldMember(pos=17, mask=0x20000, return_type=bool)
	hide_on_local_map = BitfieldMember(pos=18, mask=0x40000, return_type=bool)
	premult_alpha = BitfieldMember(pos=19, mask=0x80000, return_type=bool)
	vats_target = BitfieldMember(pos=20, mask=0x100000, return_type=bool)
	anisotropic_lighting = BitfieldMember(pos=21, mask=0x200000, return_type=bool)
	skew_specular_alpha = BitfieldMember(pos=22, mask=0x400000, return_type=bool)
	menu_screen = BitfieldMember(pos=23, mask=0x800000, return_type=bool)
	multi_layer_parallax = BitfieldMember(pos=24, mask=0x1000000, return_type=bool)
	alpha_test = BitfieldMember(pos=25, mask=0x2000000, return_type=bool)
	gradient_remap = BitfieldMember(pos=26, mask=0x4000000, return_type=bool)
	vats_target_draw_all = BitfieldMember(pos=27, mask=0x8000000, return_type=bool)
	pipboy_screen = BitfieldMember(pos=28, mask=0x10000000, return_type=bool)
	tree_anim = BitfieldMember(pos=29, mask=0x20000000, return_type=bool)
	effect_lighting = BitfieldMember(pos=30, mask=0x40000000, return_type=bool)
	refraction_writes_depth = BitfieldMember(pos=31, mask=0x80000000, return_type=bool)

	def set_defaults(self):
		pass

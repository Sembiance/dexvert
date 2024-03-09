from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.nif.basic import Uint


class BSShaderFlags(BasicBitfield):

	"""
	Shader Property Flags
	"""

	__name__ = 'BSShaderFlags'
	_storage = Uint
	SPECULAR = 2 ** 0
	SKINNED = 2 ** 1
	LOW_DETAIL = 2 ** 2
	VERTEX_ALPHA = 2 ** 3
	UNKNOWN_1 = 2 ** 4
	SINGLE_PASS = 2 ** 5
	EMPTY = 2 ** 6
	ENVIRONMENT_MAPPING = 2 ** 7
	ALPHA_TEXTURE = 2 ** 8
	UNKNOWN_2 = 2 ** 9
	FACE_GEN = 2 ** 10
	PARALLAX_SHADER_INDEX_15 = 2 ** 11
	UNKNOWN_3 = 2 ** 12
	NON_PROJECTIVE_SHADOWS = 2 ** 13
	UNKNOWN_4 = 2 ** 14
	REFRACTION = 2 ** 15
	FIRE_REFRACTION = 2 ** 16
	EYE_ENVIRONMENT_MAPPING = 2 ** 17
	HAIR = 2 ** 18
	DYNAMIC_ALPHA = 2 ** 19
	LOCALMAP_HIDE_SECRET = 2 ** 20
	WINDOW_ENVIRONMENT_MAPPING = 2 ** 21
	TREE_BILLBOARD = 2 ** 22
	SHADOW_FRUSTUM = 2 ** 23
	MULTIPLE_TEXTURES = 2 ** 24
	REMAPPABLE_TEXTURES = 2 ** 25
	DECAL_SINGLE_PASS = 2 ** 26
	DYNAMIC_DECAL_SINGLE_PASS = 2 ** 27
	PARALLAX_OCCULSION = 2 ** 28
	EXTERNAL_EMITTANCE = 2 ** 29
	SHADOW_MAP = 2 ** 30
	Z_BUFFER_TEST = 2 ** 31
	specular = BitfieldMember(pos=0, mask=0x1, return_type=bool)
	skinned = BitfieldMember(pos=1, mask=0x2, return_type=bool)
	low_detail = BitfieldMember(pos=2, mask=0x4, return_type=bool)
	vertex_alpha = BitfieldMember(pos=3, mask=0x8, return_type=bool)
	unknown_1 = BitfieldMember(pos=4, mask=0x10, return_type=bool)
	single_pass = BitfieldMember(pos=5, mask=0x20, return_type=bool)
	empty = BitfieldMember(pos=6, mask=0x40, return_type=bool)
	environment_mapping = BitfieldMember(pos=7, mask=0x80, return_type=bool)
	alpha_texture = BitfieldMember(pos=8, mask=0x100, return_type=bool)
	unknown_2 = BitfieldMember(pos=9, mask=0x200, return_type=bool)
	face_gen = BitfieldMember(pos=10, mask=0x400, return_type=bool)
	parallax_shader_index_15 = BitfieldMember(pos=11, mask=0x800, return_type=bool)
	unknown_3 = BitfieldMember(pos=12, mask=0x1000, return_type=bool)
	non_projective_shadows = BitfieldMember(pos=13, mask=0x2000, return_type=bool)
	unknown_4 = BitfieldMember(pos=14, mask=0x4000, return_type=bool)
	refraction = BitfieldMember(pos=15, mask=0x8000, return_type=bool)
	fire_refraction = BitfieldMember(pos=16, mask=0x10000, return_type=bool)
	eye_environment_mapping = BitfieldMember(pos=17, mask=0x20000, return_type=bool)
	hair = BitfieldMember(pos=18, mask=0x40000, return_type=bool)
	dynamic_alpha = BitfieldMember(pos=19, mask=0x80000, return_type=bool)
	localmap_hide_secret = BitfieldMember(pos=20, mask=0x100000, return_type=bool)
	window_environment_mapping = BitfieldMember(pos=21, mask=0x200000, return_type=bool)
	tree_billboard = BitfieldMember(pos=22, mask=0x400000, return_type=bool)
	shadow_frustum = BitfieldMember(pos=23, mask=0x800000, return_type=bool)
	multiple_textures = BitfieldMember(pos=24, mask=0x1000000, return_type=bool)
	remappable_textures = BitfieldMember(pos=25, mask=0x2000000, return_type=bool)
	decal_single_pass = BitfieldMember(pos=26, mask=0x4000000, return_type=bool)
	dynamic_decal_single_pass = BitfieldMember(pos=27, mask=0x8000000, return_type=bool)
	parallax_occulsion = BitfieldMember(pos=28, mask=0x10000000, return_type=bool)
	external_emittance = BitfieldMember(pos=29, mask=0x20000000, return_type=bool)
	shadow_map = BitfieldMember(pos=30, mask=0x40000000, return_type=bool)
	z_buffer_test = BitfieldMember(pos=31, mask=0x80000000, return_type=bool)

	def set_defaults(self):
		pass

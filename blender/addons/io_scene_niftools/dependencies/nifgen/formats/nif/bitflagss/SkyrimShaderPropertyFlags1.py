from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.nif.basic import Uint


class SkyrimShaderPropertyFlags1(BasicBitfield):

	"""
	Skyrim Shader Property Flags 1
	"""

	__name__ = 'SkyrimShaderPropertyFlags1'
	_storage = Uint
	SPECULAR = 2 ** 0
	SKINNED = 2 ** 1
	TEMP_REFRACTION = 2 ** 2
	VERTEX_ALPHA = 2 ** 3
	GREYSCALE_TO_PALETTE_COLOR = 2 ** 4
	GREYSCALE_TO_PALETTE_ALPHA = 2 ** 5
	USE_FALLOFF = 2 ** 6
	ENVIRONMENT_MAPPING = 2 ** 7
	RECIEVE_SHADOWS = 2 ** 8
	CAST_SHADOWS = 2 ** 9
	FACEGEN_DETAIL_MAP = 2 ** 10
	PARALLAX = 2 ** 11
	MODEL_SPACE_NORMALS = 2 ** 12
	NON_PROJECTIVE_SHADOWS = 2 ** 13
	LANDSCAPE = 2 ** 14
	REFRACTION = 2 ** 15
	FIRE_REFRACTION = 2 ** 16
	EYE_ENVIRONMENT_MAPPING = 2 ** 17
	HAIR_SOFT_LIGHTING = 2 ** 18
	SCREENDOOR_ALPHA_FADE = 2 ** 19
	LOCALMAP_HIDE_SECRET = 2 ** 20
	FACE_GEN_RGB_TINT = 2 ** 21
	OWN_EMIT = 2 ** 22
	PROJECTED_UV = 2 ** 23
	MULTIPLE_TEXTURES = 2 ** 24
	REMAPPABLE_TEXTURES = 2 ** 25
	DECAL = 2 ** 26
	DYNAMIC_DECAL = 2 ** 27
	PARALLAX_OCCLUSION = 2 ** 28
	EXTERNAL_EMITTANCE = 2 ** 29
	SOFT_EFFECT = 2 ** 30
	Z_BUFFER_TEST = 2 ** 31
	specular = BitfieldMember(pos=0, mask=0x1, return_type=bool)
	skinned = BitfieldMember(pos=1, mask=0x2, return_type=bool)
	temp_refraction = BitfieldMember(pos=2, mask=0x4, return_type=bool)
	vertex_alpha = BitfieldMember(pos=3, mask=0x8, return_type=bool)
	greyscale_to_palette_color = BitfieldMember(pos=4, mask=0x10, return_type=bool)
	greyscale_to_palette_alpha = BitfieldMember(pos=5, mask=0x20, return_type=bool)
	use_falloff = BitfieldMember(pos=6, mask=0x40, return_type=bool)
	environment_mapping = BitfieldMember(pos=7, mask=0x80, return_type=bool)
	recieve_shadows = BitfieldMember(pos=8, mask=0x100, return_type=bool)
	cast_shadows = BitfieldMember(pos=9, mask=0x200, return_type=bool)
	facegen_detail_map = BitfieldMember(pos=10, mask=0x400, return_type=bool)
	parallax = BitfieldMember(pos=11, mask=0x800, return_type=bool)
	model_space_normals = BitfieldMember(pos=12, mask=0x1000, return_type=bool)
	non_projective_shadows = BitfieldMember(pos=13, mask=0x2000, return_type=bool)
	landscape = BitfieldMember(pos=14, mask=0x4000, return_type=bool)
	refraction = BitfieldMember(pos=15, mask=0x8000, return_type=bool)
	fire_refraction = BitfieldMember(pos=16, mask=0x10000, return_type=bool)
	eye_environment_mapping = BitfieldMember(pos=17, mask=0x20000, return_type=bool)
	hair_soft_lighting = BitfieldMember(pos=18, mask=0x40000, return_type=bool)
	screendoor_alpha_fade = BitfieldMember(pos=19, mask=0x80000, return_type=bool)
	localmap_hide_secret = BitfieldMember(pos=20, mask=0x100000, return_type=bool)
	face_gen_rgb_tint = BitfieldMember(pos=21, mask=0x200000, return_type=bool)
	own_emit = BitfieldMember(pos=22, mask=0x400000, return_type=bool)
	projected_uv = BitfieldMember(pos=23, mask=0x800000, return_type=bool)
	multiple_textures = BitfieldMember(pos=24, mask=0x1000000, return_type=bool)
	remappable_textures = BitfieldMember(pos=25, mask=0x2000000, return_type=bool)
	decal = BitfieldMember(pos=26, mask=0x4000000, return_type=bool)
	dynamic_decal = BitfieldMember(pos=27, mask=0x8000000, return_type=bool)
	parallax_occlusion = BitfieldMember(pos=28, mask=0x10000000, return_type=bool)
	external_emittance = BitfieldMember(pos=29, mask=0x20000000, return_type=bool)
	soft_effect = BitfieldMember(pos=30, mask=0x40000000, return_type=bool)
	z_buffer_test = BitfieldMember(pos=31, mask=0x80000000, return_type=bool)

	def set_defaults(self):
		pass

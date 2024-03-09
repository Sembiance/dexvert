from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class BSLightingShaderType(BaseEnum):

	"""
	Values for configuring the shader type in a BSLightingShaderProperty
	"""

	__name__ = 'BSLightingShaderType'
	_storage = Uint

	DEFAULT = 0

	# Enables EnvMap Mask(TS6), EnvMap Scale
	ENVIRONMENT_MAP = 1

	# Enables Glow(TS3)
	GLOW_SHADER = 2

	# Enables Height(TS4)
	PARALLAX = 3

	# Enables Detail(TS4), Tint(TS7)
	FACE_TINT = 4

	# Enables Skin Tint Color
	SKIN_TINT = 5

	# Enables Hair Tint Color
	HAIR_TINT = 6

	# Enables Height(TS4), Max Passes, Scale. Unimplemented.
	PARALLAX_OCC = 7
	MULTITEXTURE_LANDSCAPE = 8
	LOD_LANDSCAPE = 9
	SNOW = 10

	# Enables EnvMap Mask(TS6), Layer(TS7), Parallax Layer Thickness, Parallax Refraction Scale, Parallax Inner Layer U Scale, Parallax Inner Layer V Scale, EnvMap Scale
	MULTI_LAYER_PARALLAX = 11
	TREE_ANIM = 12
	LOD_OBJECTS = 13

	# Enables SparkleParams
	SPARKLE_SNOW = 14
	LOD_OBJECTS_HD = 15

	# Enables EnvMap Mask(TS6), Eye EnvMap Scale
	EYE_ENVMAP = 16
	CLOUD = 17
	LOD_LANDSCAPE_NOISE = 18
	MULTITEXTURE_LANDSCAPE_LOD_BLEND = 19
	FO_4_DISMEMBERMENT = 20

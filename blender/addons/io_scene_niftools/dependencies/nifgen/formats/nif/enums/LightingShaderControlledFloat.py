from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class LightingShaderControlledFloat(BaseEnum):

	"""
	An unsigned 32-bit integer, describing which float variable in BSLightingShaderProperty to animate.
	"""

	__name__ = 'LightingShaderControlledFloat'
	_storage = Uint


	# The amount of distortion.
	REFRACTION_STRENGTH = 0
	UNKNOWN_3 = 3
	UNKNOWN_4 = 4

	# Environment Map Scale.
	ENVIRONMENT_MAP_SCALE = 8

	# Glossiness.
	GLOSSINESS = 9

	# Specular Strength.
	SPECULAR_STRENGTH = 10

	# Emissive Multiple.
	EMISSIVE_MULTIPLE = 11

	# Alpha.
	ALPHA = 12
	UNKNOWN_13 = 13
	UNKNOWN_14 = 14

	# U Offset.
	U_OFFSET = 20

	# U Scale.
	U_SCALE = 21

	# V Offset.
	V_OFFSET = 22

	# V Scale.
	V_SCALE = 23

from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class EffectShaderControlledVariable(BaseEnum):

	"""
	An unsigned 32-bit integer, describing which float variable in BSEffectShaderProperty to animate.
	"""

	__name__ = 'EffectShaderControlledVariable'
	_storage = Uint


	# EmissiveMultiple.
	EMISSIVE_MULTIPLE = 0

	# Falloff Start Angle (degrees).
	FALLOFF_START_ANGLE = 1

	# Falloff Stop Angle (degrees).
	FALLOFF_STOP_ANGLE = 2

	# Falloff Start Opacity.
	FALLOFF_START_OPACITY = 3

	# Falloff Stop Opacity.
	FALLOFF_STOP_OPACITY = 4

	# Alpha Transparency (Emissive alpha?).
	ALPHA_TRANSPARENCY = 5

	# U Offset.
	U_OFFSET = 6

	# U Scale.
	U_SCALE = 7

	# V Offset.
	V_OFFSET = 8

	# V Scale.
	V_SCALE = 9
	UNKNOWN_11 = 11
	UNKNOWN_12 = 12
	UNKNOWN_13 = 13
	UNKNOWN_14 = 14

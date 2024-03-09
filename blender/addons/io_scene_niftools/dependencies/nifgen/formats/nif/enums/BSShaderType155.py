from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class BSShaderType155(BaseEnum):

	"""
	Values for configuring the shader type in a BSLightingShaderProperty
	"""

	__name__ = 'BSShaderType155'
	_storage = Uint

	DEFAULT = 0
	GLOW = 2
	FACE_TINT = 3
	SKIN_TINT = 4
	HAIR_TINT = 5

	# Enables EnvMap Mask, Eye EnvMap Scale
	EYE_ENVMAP = 12
	TERRAIN = 17

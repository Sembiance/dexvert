from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class BSShaderType(BaseEnum):

	"""
	FO3 Shader Type
	"""

	__name__ = 'BSShaderType'
	_storage = Uint


	# Tall Grass Shader
	SHADER_TALL_GRASS = 0

	# Standard Lighting Shader
	SHADER_DEFAULT = 1

	# Sky Shader
	SHADER_SKY = 10

	# Skin Shader
	SHADER_SKIN = 14

	# scolbld06georgetown01
	SHADER_UNKNOWN = 15

	# Water Shader
	SHADER_WATER = 17

	# Lighting 3.0 Shader
	SHADER_LIGHTING30 = 29

	# Tiled Shader
	SHADER_TILE = 32

	# No Lighting Shader
	SHADER_NOLIGHTING = 33

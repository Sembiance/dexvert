from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class LightingShaderControlledColor(BaseEnum):

	"""
	An unsigned 32-bit integer, describing which color in BSLightingShaderProperty to animate.
	"""

	__name__ = 'LightingShaderControlledColor'
	_storage = Uint


	# Specular Color.
	SPECULAR_COLOR = 0

	# Emissive Color.
	EMISSIVE_COLOR = 1

from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class LightingShaderControlledUShort(BaseEnum):

	"""
	An unsigned 32-bit integer, describing which integral value in BSLightingShaderProperty to animate.
	"""

	__name__ = 'LightingShaderControlledUShort'
	_storage = Uint

	UNKNOWN_1 = 0
	UNKNOWN_2 = 1

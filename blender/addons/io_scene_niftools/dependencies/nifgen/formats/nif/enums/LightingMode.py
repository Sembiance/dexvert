from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class LightingMode(BaseEnum):

	"""
	Describes which lighting equation components influence the final vertex color for NiVertexColorProperty.
	"""

	__name__ = 'LightingMode'
	_storage = Uint


	# Emissive.
	LIGHT_MODE_EMISSIVE = 0

	# Emissive + Ambient + Diffuse. (Default)
	LIGHT_MODE_EMI_AMB_DIF = 1

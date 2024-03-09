from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class SourceVertexMode(BaseEnum):

	"""
	Describes how to apply vertex colors for NiVertexColorProperty.
	"""

	__name__ = 'SourceVertexMode'
	_storage = Uint


	# Emissive, ambient, and diffuse colors are all specified by the NiMaterialProperty.
	VERT_MODE_SRC_IGNORE = 0

	# Emissive colors are specified by the source vertex colors. Ambient+Diffuse are specified by the NiMaterialProperty.
	VERT_MODE_SRC_EMISSIVE = 1

	# Ambient+Diffuse colors are specified by the source vertex colors. Emissive is specified by the NiMaterialProperty. (Default)
	VERT_MODE_SRC_AMB_DIF = 2

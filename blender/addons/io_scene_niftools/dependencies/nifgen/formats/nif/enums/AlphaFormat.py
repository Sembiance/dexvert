from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class AlphaFormat(BaseEnum):

	"""
	Describes how transparency is handled in an NiTexture.
	"""

	__name__ = 'AlphaFormat'
	_storage = Uint


	# No alpha.
	ALPHA_NONE = 0

	# 1-bit alpha.
	ALPHA_BINARY = 1

	# Interpolated 4- or 8-bit alpha.
	ALPHA_SMOOTH = 2

	# Use default setting.
	ALPHA_DEFAULT = 3

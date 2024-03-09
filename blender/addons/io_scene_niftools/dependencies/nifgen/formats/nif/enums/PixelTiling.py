from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class PixelTiling(BaseEnum):

	"""
	Describes whether pixels have been tiled from their standard row-major format to a format optimized for a particular platform.
	"""

	__name__ = 'PixelTiling'
	_storage = Uint

	TILE_NONE = 0
	TILE_XENON = 1
	TILE_WII = 2
	TILE_NV_SWIZZLED = 3

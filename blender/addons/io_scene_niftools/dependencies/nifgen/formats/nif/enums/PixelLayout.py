from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class PixelLayout(BaseEnum):

	"""
	Describes the color depth in an NiTexture.
	"""

	__name__ = 'PixelLayout'
	_storage = Uint


	# Texture is in 8-bit palettized format.
	LAY_PALETTIZED_8 = 0

	# Texture is in 16-bit high color format.
	LAY_HIGH_COLOR_16 = 1

	# Texture is in 32-bit true color format.
	LAY_TRUE_COLOR_32 = 2

	# Texture is compressed.
	LAY_COMPRESSED = 3

	# Texture is a grayscale bump map.
	LAY_BUMPMAP = 4

	# Texture is in 4-bit palettized format.
	LAY_PALETTIZED_4 = 5

	# Use default setting.
	LAY_DEFAULT = 6
	LAY_SINGLE_COLOR_8 = 7
	LAY_SINGLE_COLOR_16 = 8
	LAY_SINGLE_COLOR_32 = 9
	LAY_DOUBLE_COLOR_32 = 10
	LAY_DOUBLE_COLOR_64 = 11
	LAY_FLOAT_COLOR_32 = 12
	LAY_FLOAT_COLOR_64 = 13
	LAY_FLOAT_COLOR_128 = 14
	LAY_SINGLE_COLOR_4 = 15
	LAY_DEPTH_24_X8 = 16

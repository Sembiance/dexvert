from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class PixelFormat(BaseEnum):

	"""
	Describes the pixel format used by the NiPixelData object to store a texture.
	"""

	__name__ = 'PixelFormat'
	_storage = Uint


	# 24-bit RGB. 8 bits per red, blue, and green component.
	FMT_RGB = 0

	# 32-bit RGB with alpha. 8 bits per red, blue, green, and alpha component.
	FMT_RGBA = 1

	# 8-bit palette index.
	FMT_PAL = 2

	# 8-bit palette index with alpha.
	FMT_PALA = 3

	# DXT1 compressed texture.
	FMT_DXT1 = 4

	# DXT3 compressed texture.
	FMT_DXT3 = 5

	# DXT5 compressed texture.
	FMT_DXT5 = 6

	# (Deprecated) 24-bit noninterleaved texture, an old PS2 format.
	FMT_RGB24NONINT = 7

	# Uncompressed dU/dV gradient bump map.
	FMT_BUMP = 8

	# Uncompressed dU/dV gradient bump map with luma channel representing shininess.
	FMT_BUMPLUMA = 9

	# Generic descriptor for any renderer-specific format not described by other formats.
	FMT_RENDERSPEC = 10

	# Generic descriptor for formats with 1 component.
	FMT_1CH = 11

	# Generic descriptor for formats with 2 components.
	FMT_2CH = 12

	# Generic descriptor for formats with 3 components.
	FMT_3CH = 13

	# Generic descriptor for formats with 4 components.
	FMT_4CH = 14

	# Indicates the NiPixelFormat is meant to be used on a depth/stencil surface.
	FMT_DEPTH_STENCIL = 15
	FMT_UNKNOWN = 16

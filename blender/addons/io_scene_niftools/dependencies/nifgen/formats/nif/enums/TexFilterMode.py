from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class TexFilterMode(BaseEnum):

	"""
	Describes the availiable texture filter modes, i.e. the way the pixels in a texture are displayed on screen.
	"""

	__name__ = 'TexFilterMode'
	_storage = Uint


	# Nearest neighbor. Uses nearest texel with no mipmapping.
	FILTER_NEAREST = 0

	# Bilinear. Linear interpolation with no mipmapping.
	FILTER_BILERP = 1

	# Trilinear. Linear intepolation between 8 texels (4 nearest texels between 2 nearest mip levels).
	FILTER_TRILERP = 2

	# Nearest texel on nearest mip level.
	FILTER_NEAREST_MIPNEAREST = 3

	# Linear interpolates nearest texel between two nearest mip levels.
	FILTER_NEAREST_MIPLERP = 4

	# Linear interpolates on nearest mip level.
	FILTER_BILERP_MIPNEAREST = 5

	# Anisotropic filtering. One or many trilinear samples depending on anisotropy.
	FILTER_ANISOTROPIC = 6

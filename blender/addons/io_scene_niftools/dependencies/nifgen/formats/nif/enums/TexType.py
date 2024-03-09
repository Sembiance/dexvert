from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class TexType(BaseEnum):

	"""
	The type of texture.
	"""

	__name__ = 'TexType'
	_storage = Uint


	# The basic texture used by most meshes.
	BASE_MAP = 0

	# Used to darken the model with false lighting.
	DARK_MAP = 1

	# Combined with base map for added detail.  Usually tiled over the mesh many times for close-up view.
	DETAIL_MAP = 2

	# Allows the specularity (glossyness) of an object to differ across its surface.
	GLOSS_MAP = 3

	# Creates a glowing effect.  Basically an incandescence map.
	GLOW_MAP = 4

	# Used to make the object appear to have more detail than it really does.
	BUMP_MAP = 5

	# Used to make the object appear to have more detail than it really does.
	NORMAL_MAP = 6

	# Parallax map.
	PARALLAX_MAP = 7

	# For placing images on the object like stickers.
	DECAL_0_MAP = 8

	# For placing images on the object like stickers.
	DECAL_1_MAP = 9

	# For placing images on the object like stickers.
	DECAL_2_MAP = 10

	# For placing images on the object like stickers.
	DECAL_3_MAP = 11

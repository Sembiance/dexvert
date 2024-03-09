from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class PixelComponent(BaseEnum):

	"""
	Describes the pixel format used by the NiPixelData object to store a texture.
	"""

	__name__ = 'PixelComponent'
	_storage = Uint

	COMP_RED = 0
	COMP_GREEN = 1
	COMP_BLUE = 2
	COMP_ALPHA = 3
	COMP_COMPRESSED = 4
	COMP_OFFSET_U = 5
	COMP_OFFSET_V = 6
	COMP_OFFSET_W = 7
	COMP_OFFSET_Q = 8
	COMP_LUMA = 9
	COMP_HEIGHT = 10
	COMP_VECTOR_X = 11
	COMP_VECTOR_Y = 12
	COMP_VECTOR_Z = 13
	COMP_PADDING = 14
	COMP_INTENSITY = 15
	COMP_INDEX = 16
	COMP_DEPTH = 17
	COMP_STENCIL = 18
	COMP_EMPTY = 19

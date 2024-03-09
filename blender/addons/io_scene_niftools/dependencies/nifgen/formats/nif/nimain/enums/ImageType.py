from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class ImageType(BaseEnum):

	"""
	Determines how the raw image data is stored in NiRawImageData.
	"""

	__name__ = 'ImageType'
	_storage = Uint


	# Colors store red, blue, and green components.
	RGB = 1

	# Colors store red, blue, green, and alpha components.
	RGBA = 2

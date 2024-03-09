from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Ushort


class AlphaFunction(BaseEnum):

	"""
	Describes alpha blend modes for NiAlphaProperty.
	"""

	__name__ = 'AlphaFunction'
	_storage = Ushort

	ONE = 0
	ZERO = 1
	SRC_COLOR = 2
	INV_SRC_COLOR = 3
	DEST_COLOR = 4
	INV_DEST_COLOR = 5
	SRC_ALPHA = 6
	INV_SRC_ALPHA = 7
	DEST_ALPHA = 8
	INV_DEST_ALPHA = 9
	SRC_ALPHA_SATURATE = 10

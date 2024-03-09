from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class PixelRepresentation(BaseEnum):

	"""
	Describes how each pixel should be accessed on NiPixelFormat.
	"""

	__name__ = 'PixelRepresentation'
	_storage = Uint

	REP_NORM_INT = 0
	REP_HALF = 1
	REP_FLOAT = 2
	REP_INDEX = 3
	REP_COMPRESSED = 4
	REP_UNKNOWN = 5
	REP_INT = 6

from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Ushort


class DitherFlags(BaseEnum):

	"""
	Flags for NiDitherProperty
	"""

	__name__ = 'DitherFlags'
	_storage = Ushort

	DITHER_DISABLED = 0
	DITHER_ENABLED = 1

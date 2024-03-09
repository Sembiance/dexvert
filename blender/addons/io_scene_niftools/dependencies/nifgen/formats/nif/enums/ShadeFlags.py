from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Ushort


class ShadeFlags(BaseEnum):

	"""
	Flags for NiShadeProperty
	"""

	__name__ = 'ShadeFlags'
	_storage = Ushort

	SHADING_HARD = 0
	SHADING_SMOOTH = 1

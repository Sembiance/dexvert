from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Ushort


class SpecularFlags(BaseEnum):

	"""
	Flags for NiSpecularProperty
	"""

	__name__ = 'SpecularFlags'
	_storage = Ushort

	SPECULAR_DISABLED = 0
	SPECULAR_ENABLED = 1

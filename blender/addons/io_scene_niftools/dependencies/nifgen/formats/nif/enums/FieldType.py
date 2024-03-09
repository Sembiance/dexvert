from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class FieldType(BaseEnum):

	"""
	The force field type.
	"""

	__name__ = 'FieldType'
	_storage = Uint


	# Wind (fixed direction)
	FIELD_WIND = 0

	# Point (fixed origin)
	FIELD_POINT = 1

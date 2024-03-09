from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Byte


class HkResponseType(BaseEnum):

	"""
	hkpMaterial::ResponseType
	"""

	__name__ = 'hkResponseType'
	_storage = Byte


	# Invalid Response
	RESPONSE_INVALID = 0

	# Do normal collision resolution
	RESPONSE_SIMPLE_CONTACT = 1

	# No collision resolution is performed but listeners are called
	RESPONSE_REPORTING = 2

	# Do nothing, ignore all the results.
	RESPONSE_NONE = 3

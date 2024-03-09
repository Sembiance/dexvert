from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Byte


class HkWeldingType(BaseEnum):

	"""
	hkpWeldingUtility::WeldingType
	"""

	__name__ = 'hkWeldingType'
	_storage = Byte

	ANTICLOCKWISE = 0

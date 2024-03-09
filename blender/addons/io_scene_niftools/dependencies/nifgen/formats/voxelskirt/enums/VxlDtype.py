from nifgen.base_enum import BaseEnum
from nifgen.formats.base.basic import Uint64


class VxlDtype(BaseEnum):

	__name__ = 'VxlDtype'
	_storage = Uint64

	UBYTE = 0
	FLOAT = 2

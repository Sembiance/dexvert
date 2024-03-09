from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class NxCombineMode(BaseEnum):

	__name__ = 'NxCombineMode'
	_storage = Uint

	AVERAGE = 0
	MIN = 1
	MULTIPLY = 2
	MAX = 3

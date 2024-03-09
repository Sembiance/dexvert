from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class NxThreadPriority(BaseEnum):

	__name__ = 'NxThreadPriority'
	_storage = Uint

	TP_HIGH = 0
	TP_ABOVE_NORMAL = 1
	TP_NORMAL = 2
	TP_BELOW_NORMAL = 3
	TP_LOW = 4

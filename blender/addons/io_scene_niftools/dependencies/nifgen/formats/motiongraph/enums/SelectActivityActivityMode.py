from nifgen.base_enum import BaseEnum
from nifgen.formats.base.basic import Uint


class SelectActivityActivityMode(BaseEnum):

	__name__ = 'SelectActivityActivityMode'
	_storage = Uint

	ADVANCE_CHILDREN_TOGETHER = 0
	RESTART_CHILDREN_ON_SELECTION = 1
	CHOOSE_ONCE_AT_START = 2

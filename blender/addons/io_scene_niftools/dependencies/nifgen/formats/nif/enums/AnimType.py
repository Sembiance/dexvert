from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Ushort


class AnimType(BaseEnum):

	__name__ = 'AnimType'
	_storage = Ushort

	APP_TIME = 0
	APP_INIT = 1

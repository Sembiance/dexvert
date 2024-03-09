from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Ushort


class NiNBTMethod(BaseEnum):

	__name__ = 'NiNBTMethod'
	_storage = Ushort

	NBT_METHOD_NONE = 0
	NBT_METHOD_NDL = 1
	NBT_METHOD_MAX = 2
	NBT_METHOD_ATI = 3

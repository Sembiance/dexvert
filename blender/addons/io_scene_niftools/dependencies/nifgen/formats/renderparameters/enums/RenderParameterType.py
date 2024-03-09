from nifgen.base_enum import BaseEnum
from nifgen.formats.base.basic import Uint64


class RenderParameterType(BaseEnum):

	__name__ = 'RenderParameterType'
	_storage = Uint64

	BOOL = 0
	FLOAT = 1
	INT = 2
	U_INT = 3
	FLOAT_2 = 4
	FLOAT_3 = 5
	FLOAT_4 = 6
	COLOUR = 7
	COLOUR_H_D_R = 8
	STRING = 9

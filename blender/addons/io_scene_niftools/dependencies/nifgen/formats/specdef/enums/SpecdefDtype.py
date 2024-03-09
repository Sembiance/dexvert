from nifgen.base_enum import BaseEnum
from nifgen.formats.base.basic import Uint


class SpecdefDtype(BaseEnum):

	__name__ = 'SpecdefDtype'
	_storage = Uint

	BOOLEAN = 0
	INT_8 = 1
	INT_16 = 2
	INT_32 = 3
	INT_64 = 4
	U_INT_8 = 5
	U_INT_16 = 6
	U_INT_32 = 7
	U_INT_64 = 8
	FLOAT = 9
	STRING = 10
	VECTOR_2 = 11
	VECTOR_3 = 12
	ARRAY = 13
	CHILD_ITEM = 14
	REFERENCE_TO_OBJECT = 15

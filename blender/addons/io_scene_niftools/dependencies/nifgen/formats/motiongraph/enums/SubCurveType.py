from nifgen.base_enum import BaseEnum
from nifgen.formats.base.basic import Ushort


class SubCurveType(BaseEnum):

	__name__ = 'SubCurveType'
	_storage = Ushort

	CONSTANT = 0
	LINEAR = 1
	POLYNOMIAL = 2
	EXPONENTIAL = 3
	S_CURVE = 4
	BEZIER = 5

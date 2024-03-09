from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class NxFilterOp(BaseEnum):

	__name__ = 'NxFilterOp'
	_storage = Uint

	FILTEROP_AND = 0
	FILTEROP_OR = 1
	FILTEROP_XOR = 2
	FILTEROP_NAND = 3
	FILTEROP_NOR = 4
	FILTEROP_NXOR = 5
	FILTEROP_SWAP_AND = 6

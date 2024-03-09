from nifgen.base_enum import BaseEnum
from nifgen.formats.base.basic import Ubyte


class MeshFormat(BaseEnum):

	__name__ = 'MeshFormat'
	_storage = Ubyte

	SEPARATE = 0
	INTERLEAVED_32 = 1
	INTERLEAVED_48 = 2
	UNK_FMT = 3

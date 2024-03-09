from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Ushort


class FogFunction(BaseEnum):

	__name__ = 'FogFunction'
	_storage = Ushort

	FOG_Z_LINEAR = 0
	FOG_RANGE_SQ = 1
	FOG_VERTEX_ALPHA = 2

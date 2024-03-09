from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Ushort


class ConsistencyType(BaseEnum):

	"""
	Used by NiGeometryData to control the volatility of the mesh.
	Consistency Type is masked to only the upper 4 bits (0xF000). Dirty mask is the lower 12 (0x0FFF) but only used at runtime.
	"""

	__name__ = 'ConsistencyType'
	_storage = Ushort


	# Mutable Mesh
	CT_MUTABLE = 0x0000

	# Static Mesh
	CT_STATIC = 0x4000

	# Volatile Mesh
	CT_VOLATILE = 0x8000

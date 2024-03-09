from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Ushort


class GeomMorpherFlags(BaseEnum):

	"""
	Flags for NiGeomMorpherController
	"""

	__name__ = 'GeomMorpherFlags'
	_storage = Ushort

	UPDATE_NORMALS_DISABLED = 0
	UPDATE_NORMALS_ENABLED = 1

from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class NxShapeType(BaseEnum):

	__name__ = 'NxShapeType'
	_storage = Uint

	SHAPE_PLANE = 0
	SHAPE_SPHERE = 1
	SHAPE_BOX = 2
	SHAPE_CAPSULE = 3
	SHAPE_WHEEL = 4
	SHAPE_CONVEX = 5
	SHAPE_MESH = 6
	SHAPE_HEIGHTFIELD = 7
	SHAPE_RAW_MESH = 8
	SHAPE_COMPOUND = 9

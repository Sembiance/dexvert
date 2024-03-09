from nifgen.base_enum import BaseEnum
from nifgen.formats.base.basic import Uint


class CollisionType(BaseEnum):

	__name__ = 'CollisionType'
	_storage = Uint

	SPHERE = 0
	BOUNDING_BOX = 1
	CAPSULE = 2
	CYLINDER = 3
	CONVEX_HULL = 7
	CONVEX_HULL_P_C = 8
	MESH_COLLISION = 10

	# ?
	UNK_RHINO = 11

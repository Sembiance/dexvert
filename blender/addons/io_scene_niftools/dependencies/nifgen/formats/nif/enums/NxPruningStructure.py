from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class NxPruningStructure(BaseEnum):

	__name__ = 'NxPruningStructure'
	_storage = Uint

	PRUNING_NONE = 0
	PRUNING_OCTREE = 1
	PRUNING_QUADTREE = 2
	PRUNING_DYNAMIC_AABB_TREE = 3
	PRUNING_STATIC_AABB_TREE = 4

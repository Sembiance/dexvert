from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class CollisionMode(BaseEnum):

	"""
	The collision mode controls the type of collision operation that is to take place for NiCollisionData.
	"""

	__name__ = 'CollisionMode'
	_storage = Uint


	# Use Bounding Box
	USE_OBB = 0

	# Use Triangles
	USE_TRI = 1

	# Use Alternate Bounding Volumes
	USE_ABV = 2

	# Indicates that no collision test should be made.
	NOTEST = 3

	# Use NiBound
	USE_NIBOUND = 4

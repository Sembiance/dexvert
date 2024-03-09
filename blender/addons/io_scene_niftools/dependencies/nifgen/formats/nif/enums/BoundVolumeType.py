from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class BoundVolumeType(BaseEnum):

	__name__ = 'BoundVolumeType'
	_storage = Uint


	# Default
	BASE_BV = 0xffffffff

	# Sphere
	SPHERE_BV = 0

	# Box
	BOX_BV = 1

	# Capsule
	CAPSULE_BV = 2

	# Union
	UNION_BV = 4

	# Half Space
	HALFSPACE_BV = 5

from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class NxJointType(BaseEnum):

	__name__ = 'NxJointType'
	_storage = Uint

	PRISMATIC = 0
	REVOLUTE = 1
	CYLINDRICAL = 2
	SPHERICAL = 3
	POINT_ON_LINE = 4
	POINT_IN_PLANE = 5
	DISTANCE = 6
	PULLEY = 7
	FIXED = 8
	D6 = 9

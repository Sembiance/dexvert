from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class NxJointProjectionMode(BaseEnum):

	__name__ = 'NxJointProjectionMode'
	_storage = Uint

	JPM_NONE = 0
	JPM_POINT_MINDIST = 1
	JPM_LINEAR_MINDIST = 2

from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class NxD6JointMotion(BaseEnum):

	__name__ = 'NxD6JointMotion'
	_storage = Uint

	MOTION_LOCKED = 0
	MOTION_LIMITED = 1
	MOTION_FREE = 2

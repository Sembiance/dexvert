from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class NxD6JointDriveType(BaseEnum):

	__name__ = 'NxD6JointDriveType'
	_storage = Uint

	DRIVE_POSITION = 1
	DRIVE_VELOCITY = 2

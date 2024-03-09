from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Byte


class HkMotorType(BaseEnum):

	__name__ = 'hkMotorType'
	_storage = Byte

	MOTOR_NONE = 0
	MOTOR_POSITION = 1
	MOTOR_VELOCITY = 2
	MOTOR_SPRING = 3

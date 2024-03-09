from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Ushort


class AnimationType(BaseEnum):

	"""
	Bethesda Animation. Animation type used on this position. This specifies the function of this position.
	"""

	__name__ = 'AnimationType'
	_storage = Ushort


	# Actor use sit animation.
	SIT = 1

	# Actor use sleep animation.
	SLEEP = 2

	# Used for lean animations?
	LEAN = 4

from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class AlignMethod(BaseEnum):

	"""
	Describes the various methods that may be used to specify the orientation of the particles.
	"""

	__name__ = 'AlignMethod'
	_storage = Uint

	ALIGN_INVALID = 0
	ALIGN_PER_PARTICLE = 1
	ALIGN_LOCAL_FIXED = 2
	ALIGN_LOCAL_POSITION = 5
	ALIGN_LOCAL_VELOCITY = 9
	ALIGN_CAMERA = 16

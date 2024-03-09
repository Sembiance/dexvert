from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class ForceType(BaseEnum):

	"""
	Describes the type of gravitational force.
	"""

	__name__ = 'ForceType'
	_storage = Uint

	FORCE_PLANAR = 0
	FORCE_SPHERICAL = 1
	FORCE_UNKNOWN = 2

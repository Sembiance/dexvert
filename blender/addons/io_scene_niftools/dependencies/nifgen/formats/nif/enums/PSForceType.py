from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class PSForceType(BaseEnum):

	"""
	This is used by the Floodgate kernel to determine which NiPSForceHelpers functions to call.
	"""

	__name__ = 'PSForceType'
	_storage = Uint

	FORCE_BOMB = 0
	FORCE_DRAG = 1
	FORCE_AIR_FIELD = 2
	FORCE_DRAG_FIELD = 3
	FORCE_GRAVITY_FIELD = 4
	FORCE_RADIAL_FIELD = 5
	FORCE_TURBULENCE_FIELD = 6
	FORCE_VORTEX_FIELD = 7
	FORCE_GRAVITY = 8

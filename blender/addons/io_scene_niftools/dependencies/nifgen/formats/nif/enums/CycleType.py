from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class CycleType(BaseEnum):

	"""
	The animation cyle behavior.
	"""

	__name__ = 'CycleType'
	_storage = Uint


	# Loop
	CYCLE_LOOP = 0

	# Reverse
	CYCLE_REVERSE = 1

	# Clamp
	CYCLE_CLAMP = 2

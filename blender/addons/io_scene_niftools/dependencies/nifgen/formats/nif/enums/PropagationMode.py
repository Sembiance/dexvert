from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class PropagationMode(BaseEnum):

	"""
	The propagation mode controls scene graph traversal during collision detection operations for NiCollisionData.
	"""

	__name__ = 'PropagationMode'
	_storage = Uint


	# Propagation only occurs as a result of a successful collision.
	PROPAGATE_ON_SUCCESS = 0

	# (Deprecated) Propagation only occurs as a result of a failed collision.
	PROPAGATE_ON_FAILURE = 1

	# Propagation always occurs regardless of collision result.
	PROPAGATE_ALWAYS = 2

	# Propagation never occurs regardless of collision result.
	PROPAGATE_NEVER = 3

	# Propagation mode found in Civ IV Chariot_Celtic.
	PROPAGATE_UNKNOWN_6 = 6

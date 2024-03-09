from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Byte


class HkSolverDeactivation(BaseEnum):

	"""
	hkpRigidBodyCinfo::SolverDeactivation.
	A list of possible solver deactivation settings. This value defines how aggressively the solver deactivates objects.
	Note: Solver deactivation does not save CPU, but reduces creeping of movable objects in a pile quite dramatically.
	"""

	__name__ = 'hkSolverDeactivation'
	_storage = Byte


	# Invalid
	SOLVER_DEACTIVATION_INVALID = 0

	# No solver deactivation.
	SOLVER_DEACTIVATION_OFF = 1

	# Very conservative deactivation, typically no visible artifacts.
	SOLVER_DEACTIVATION_LOW = 2

	# Normal deactivation, no serious visible artifacts in most cases.
	SOLVER_DEACTIVATION_MEDIUM = 3

	# Fast deactivation, visible artifacts.
	SOLVER_DEACTIVATION_HIGH = 4

	# Very fast deactivation, visible artifacts.
	SOLVER_DEACTIVATION_MAX = 5

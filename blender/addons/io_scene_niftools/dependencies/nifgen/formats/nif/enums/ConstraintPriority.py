from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class ConstraintPriority(BaseEnum):

	"""
	hkpConstraintInstance::ConstraintPriority. Priority used for the constraint.
	Values 2, 4, and 5 are unused or internal use only.
	"""

	__name__ = 'ConstraintPriority'
	_storage = Uint

	PRIORITY_INVALID = 0

	# Constraint is only solved at regular physics time steps.
	PRIORITY_PSI = 1

	# Constraint is also solved at time of impact events.
	PRIORITY_TOI = 3

from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class HkConstraintType(BaseEnum):

	"""
	hkpConstraintData::ConstraintType. Describes the type of bhkConstraint.
	"""

	__name__ = 'hkConstraintType'
	_storage = Uint


	# A ball and socket constraint.
	BALL_AND_SOCKET = 0

	# A hinge constraint.
	HINGE = 1

	# A limited hinge constraint.
	LIMITED_HINGE = 2

	# A prismatic constraint.
	PRISMATIC = 6

	# A ragdoll constraint.
	RAGDOLL = 7

	# A stiff spring constraint.
	STIFF_SPRING = 8

	# A malleable constraint.
	MALLEABLE = 13

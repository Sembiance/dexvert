from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Byte


class HkDeactivatorType(BaseEnum):

	"""
	hkpRigidBodyDeactivator::DeactivatorType. Deactivator Type determines which mechanism Havok will use to classify the body as deactivated.
	"""

	__name__ = 'hkDeactivatorType'
	_storage = Byte


	# Invalid
	DEACTIVATOR_INVALID = 0

	# This will force the rigid body to never deactivate.
	DEACTIVATOR_NEVER = 1

	# Tells Havok to use a spatial deactivation scheme. This makes use of high and low frequencies of positional motion to determine when deactivation should occur.
	DEACTIVATOR_SPATIAL = 2

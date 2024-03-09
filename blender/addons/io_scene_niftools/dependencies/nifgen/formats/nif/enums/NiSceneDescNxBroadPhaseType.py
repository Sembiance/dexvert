from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class NiSceneDescNxBroadPhaseType(BaseEnum):

	__name__ = 'NiSceneDescNxBroadPhaseType'
	_storage = Uint

	BROADPHASE_QUADRATIC = 0
	BROADPHASE_FULL = 1
	BROADPHASE_COHERENT = 2

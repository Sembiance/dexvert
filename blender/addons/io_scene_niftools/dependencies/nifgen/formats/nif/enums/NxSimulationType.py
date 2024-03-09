from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class NxSimulationType(BaseEnum):

	__name__ = 'NxSimulationType'
	_storage = Uint

	SIMULATION_SW = 0
	SIMULATION_HW = 1

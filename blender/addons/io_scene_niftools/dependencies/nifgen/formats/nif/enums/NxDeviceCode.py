from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class NxDeviceCode(BaseEnum):

	__name__ = 'NxDeviceCode'
	_storage = Uint

	PPU_0 = 0
	PPU_1 = 1
	PPU_2 = 2
	PPU_3 = 3
	PPU_4 = 4
	PPU_5 = 5
	PPU_6 = 6
	PPU_7 = 7
	PPU_8 = 8
	CPU = 4294901760
	PPU_AUTO_ASSIGN = 4294901761

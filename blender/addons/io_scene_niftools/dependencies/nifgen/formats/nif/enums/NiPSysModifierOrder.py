from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class NiPSysModifierOrder(BaseEnum):

	"""
	The set order for each derived class of NiPSysModifier.
	Note: For Skyrim, BSPSysStripUpdateModifier is 8000 and for FO3 it is 2500.
	"""

	__name__ = 'NiPSysModifierOrder'
	_storage = Uint

	ORDER_KILLOLDPARTICLES = 0
	ORDER_BSLOD = 1
	ORDER_EMITTER = 1000
	ORDER_SPAWN = 2000
	ORDER_FO3_BSSTRIPUPDATE = 2500
	ORDER_GENERAL = 3000
	ORDER_FORCE = 4000
	ORDER_COLLIDER = 5000
	ORDER_POS_UPDATE = 6000
	ORDER_POSTPOS_UPDATE = 6500
	ORDER_WORLDSHIFT_PARTSPAWN = 6600
	ORDER_BOUND_UPDATE = 7000
	ORDER_SK_BSSTRIPUPDATE = 8000

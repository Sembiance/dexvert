from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class PlatformID(BaseEnum):

	"""
	Target platform for NiPersistentSrcTextureRendererData (later than 30.1).
	"""

	__name__ = 'PlatformID'
	_storage = Uint

	ANY = 0
	XENON = 1
	PS3 = 2
	DX9 = 3
	WII = 4
	D3D10 = 5
	UNKNOWN_6 = 6
	UNKNOWN_7 = 7
	UNKNOWN_8 = 8

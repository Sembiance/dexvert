from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class RendererID(BaseEnum):

	"""
	Target renderer for NiPersistentSrcTextureRendererData (until 30.1).
	"""

	__name__ = 'RendererID'
	_storage = Uint

	XBOX360 = 0
	PS3 = 1
	DX9 = 2
	D3D10 = 3
	WII = 4
	GENERIC = 5
	D3D11 = 6

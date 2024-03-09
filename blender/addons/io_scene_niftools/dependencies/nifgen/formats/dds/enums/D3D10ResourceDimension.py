from nifgen.base_enum import BaseEnum
from nifgen.formats.base.basic import Uint


class D3D10ResourceDimension(BaseEnum):

	"""
	An unsigned 32-bit integer. Identifies the type of resource being used.
	"""

	__name__ = 'D3D10 RESOURCE DIMENSION'
	_storage = Uint

	D3D10_RESOURCE_DIMENSION_UNKNOWN = 0
	D3D10_RESOURCE_DIMENSION_BUFFER = 1
	D3D10_RESOURCE_DIMENSION_TEXTURE1D = 2
	D3D10_RESOURCE_DIMENSION_TEXTURE2D = 3
	D3D10_RESOURCE_DIMENSION_TEXTURE3D = 4

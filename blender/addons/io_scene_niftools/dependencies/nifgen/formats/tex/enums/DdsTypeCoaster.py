from nifgen.base_enum import BaseEnum
from nifgen.formats.base.basic import Ubyte


class DdsTypeCoaster(BaseEnum):

	"""
	maps the OVL's dds type to name of compression format
	"""

	__name__ = 'DdsTypeCoaster'
	_storage = Ubyte


	# ZTUAC ele heights textures
	D24_UNORM_S8_UINT = 74

	# ?
	D24_UNORM_S8_UINT_B = 76
	BC1_UNORM = 97
	BC1_UNORM_SRGB = 98
	BC2_UNORM = 99
	BC2_UNORM_SRGB = 100
	BC3_UNORM = 101
	BC3_UNORM_SRGB = 102
	BC4_UNORM = 103
	BC4_SNORM = 104
	BC5_UNORM = 105
	BC5_SNORM = 106
	BC4_UNORM_B = 121
	BC7_UNORM = 126
	BC7_UNORM_SRGB = 127
	ALL = 250

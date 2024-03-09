from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class MipMapFormat(BaseEnum):

	"""
	Describes how mipmaps are handled in an NiTexture.
	"""

	__name__ = 'MipMapFormat'
	_storage = Uint


	# Texture does not use mip maps.
	MIP_FMT_NO = 0

	# Texture uses mip maps.
	MIP_FMT_YES = 1

	# Use default setting.
	MIP_FMT_DEFAULT = 2

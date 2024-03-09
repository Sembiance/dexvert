from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class SkyObjectType(BaseEnum):

	"""
	Sets what sky function this object fulfills in BSSkyShaderProperty or SkyShaderProperty.
	"""

	__name__ = 'SkyObjectType'
	_storage = Uint


	# BSSM_Sky_Texture
	BSSM_SKY_TEXTURE = 0

	# BSSM_Sky_Sunglare
	BSSM_SKY_SUNGLARE = 1

	# BSSM_Sky
	BSSM_SKY = 2

	# BSSM_Sky_Clouds
	BSSM_SKY_CLOUDS = 3

	# BSSM_Sky_Stars
	BSSM_SKY_STARS = 5

	# BSSM_Sky_Moon_Stars_Mask
	BSSM_SKY_MOON_STARS_MASK = 7

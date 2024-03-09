from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Ushort


class LightColor(BaseEnum):

	"""
	Used by NiLightColorControllers to select which type of color in the controlled object that will be animated.
	"""

	__name__ = 'LightColor'
	_storage = Ushort


	# Control the diffuse color.
	LC_DIFFUSE = 0

	# Control the ambient color.
	LC_AMBIENT = 1

from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Ushort


class MaterialColor(BaseEnum):

	"""
	Used by NiMaterialColorControllers to select which type of color in the controlled object that will be animated.
	"""

	__name__ = 'MaterialColor'
	_storage = Ushort


	# Control the ambient color.
	TC_AMBIENT = 0

	# Control the diffuse color.
	TC_DIFFUSE = 1

	# Control the specular color.
	TC_SPECULAR = 2

	# Control the self illumination color.
	TC_SELF_ILLUM = 3

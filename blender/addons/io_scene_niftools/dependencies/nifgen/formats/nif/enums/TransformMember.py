from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class TransformMember(BaseEnum):

	"""
	Describes which aspect of the NiTextureTransform the NiTextureTransformController will modify.
	"""

	__name__ = 'TransformMember'
	_storage = Uint


	# Control the translation of the U coordinates.
	TT_TRANSLATE_U = 0

	# Control the translation of the V coordinates.
	TT_TRANSLATE_V = 1

	# Control the rotation of the coordinates.
	TT_ROTATE = 2

	# Control the scale of the U coordinates.
	TT_SCALE_U = 3

	# Control the scale of the V coordinates.
	TT_SCALE_V = 4

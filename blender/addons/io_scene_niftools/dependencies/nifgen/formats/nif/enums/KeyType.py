from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class KeyType(BaseEnum):

	"""
	The type of animation interpolation (blending) that will be used on the associated key frames.
	"""

	__name__ = 'KeyType'
	_storage = Uint


	# Use linear interpolation.
	LINEAR_KEY = 1

	# Use quadratic interpolation.  Forward and back tangents will be stored.
	QUADRATIC_KEY = 2

	# Use Tension Bias Continuity interpolation.  Tension, bias, and continuity will be stored.
	TBC_KEY = 3

	# For use only with rotation data.  Separate X, Y, and Z keys will be stored instead of using quaternions.
	XYZ_ROTATION_KEY = 4

	# Step function. Used for visibility keys in NiBoolData.
	CONST_KEY = 5

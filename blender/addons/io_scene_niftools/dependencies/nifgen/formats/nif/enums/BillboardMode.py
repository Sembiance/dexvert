from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Ushort


class BillboardMode(BaseEnum):

	"""
	Determines the way the billboard will react to the camera.
	Billboard mode is stored in lowest 3 bits although Oblivion vanilla nifs uses values higher than 7.
	"""

	__name__ = 'BillboardMode'
	_storage = Ushort


	# Align billboard and camera forward vector. Minimized rotation.
	ALWAYS_FACE_CAMERA = 0

	# Align billboard and camera forward vector while allowing rotation around the up axis.
	ROTATE_ABOUT_UP = 1

	# Align billboard and camera forward vector. Non-minimized rotation.
	RIGID_FACE_CAMERA = 2

	# Billboard forward vector always faces camera ceneter. Minimized rotation.
	ALWAYS_FACE_CENTER = 3

	# Billboard forward vector always faces camera ceneter. Non-minimized rotation.
	RIGID_FACE_CENTER = 4

	# The billboard will only rotate around its local Z axis (it always stays in its local X-Y plane).
	BSROTATE_ABOUT_UP = 5

	# The billboard will only rotate around the up axis (same as ROTATE_ABOUT_UP?).
	ROTATE_ABOUT_UP2 = 9

	# Found in Civ IV Gravebringer and Gravebringer_FX
	UNKNOWN_8 = 8

	# Found in FO3 dlc04lighthouselightmech01
	UNKNOWN_10 = 10

	# Found in Civ IV Afterworld_Boss_FX
	UNKNOWN_11 = 11

	# Found in IRIS Online etc.
	UNKNOWN_12 = 12

from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class ApplyMode(BaseEnum):

	"""
	Describes how the vertex colors are blended with the filtered texture color.
	"""

	__name__ = 'ApplyMode'
	_storage = Uint


	# Replaces existing color
	APPLY_REPLACE = 0

	# For placing images on the object like stickers.
	APPLY_DECAL = 1

	# Modulates existing color. (Default)
	APPLY_MODULATE = 2

	# PS2 Only.  Function Unknown.
	APPLY_HILIGHT = 3

	# Parallax Flag in some Oblivion meshes.
	APPLY_HILIGHT2 = 4

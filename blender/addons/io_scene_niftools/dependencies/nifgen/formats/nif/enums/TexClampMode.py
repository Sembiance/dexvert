from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class TexClampMode(BaseEnum):

	"""
	Describes the availiable texture clamp modes, i.e. the behavior of UV mapping outside the [0,1] range.
	"""

	__name__ = 'TexClampMode'
	_storage = Uint


	# Clamp in both directions.
	CLAMP_S_CLAMP_T = 0

	# Clamp in the S(U) direction but wrap in the T(V) direction.
	CLAMP_S_WRAP_T = 1

	# Wrap in the S(U) direction but clamp in the T(V) direction.
	WRAP_S_CLAMP_T = 2

	# Wrap in both directions.
	WRAP_S_WRAP_T = 3

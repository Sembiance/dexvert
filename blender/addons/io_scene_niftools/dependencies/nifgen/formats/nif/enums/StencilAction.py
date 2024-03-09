from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class StencilAction(BaseEnum):

	"""
	Describes the actions which can occur as a result of tests for NiStencilProperty.
	"""

	__name__ = 'StencilAction'
	_storage = Uint


	# Keep the current value in the stencil buffer.
	ACTION_KEEP = 0

	# Write zero to the stencil buffer.
	ACTION_ZERO = 1

	# Write the reference value to the stencil buffer.
	ACTION_REPLACE = 2

	# Increment the value in the stencil buffer.
	ACTION_INCREMENT = 3

	# Decrement the value in the stencil buffer.
	ACTION_DECREMENT = 4

	# Bitwise invert the value in the stencil buffer.
	ACTION_INVERT = 5

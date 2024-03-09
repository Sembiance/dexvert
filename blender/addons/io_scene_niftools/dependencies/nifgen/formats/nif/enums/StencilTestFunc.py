from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class StencilTestFunc(BaseEnum):

	"""
	Describes stencil buffer test modes for NiStencilProperty.
	"""

	__name__ = 'StencilTestFunc'
	_storage = Uint


	# Always false. Ref value is ignored.
	TEST_NEVER = 0

	# VRef ‹ VBuf
	TEST_LESS = 1

	# VRef = VBuf
	TEST_EQUAL = 2

	# VRef ≤ VBuf
	TEST_LESS_EQUAL = 3

	# VRef › VBuf
	TEST_GREATER = 4

	# VRef ≠ VBuf
	TEST_NOT_EQUAL = 5

	# VRef ≥ VBuf
	TEST_GREATER_EQUAL = 6

	# Always true. Buffer is ignored.
	TEST_ALWAYS = 7

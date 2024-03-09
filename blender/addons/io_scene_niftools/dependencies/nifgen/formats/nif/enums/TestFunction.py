from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class TestFunction(BaseEnum):

	"""
	Describes Z-buffer test modes for NiZBufferProperty.
	"Less than" = closer to camera, "Greater than" = further from camera.
	"""

	__name__ = 'TestFunction'
	_storage = Uint


	# Always true. Buffer is ignored.
	TEST_ALWAYS = 0

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

	# Always false. Ref value is ignored.
	TEST_NEVER = 7

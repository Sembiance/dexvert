from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class CloningBehavior(BaseEnum):

	"""
	Sets how objects are to be cloned.
	"""

	__name__ = 'CloningBehavior'
	_storage = Uint


	# Share this object pointer with the newly cloned scene.
	CLONING_SHARE = 0

	# Create an exact duplicate of this object for use with the newly cloned scene.
	CLONING_COPY = 1

	# Create a copy of this object for use with the newly cloned stream, leaving some of the data to be written later.
	CLONING_BLANK_COPY = 2

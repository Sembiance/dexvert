from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class DataStreamUsage(BaseEnum):

	"""
	Determines how a data stream is used?
	"""

	__name__ = 'DataStreamUsage'
	_storage = Uint

	USAGE_VERTEX_INDEX = 0
	USAGE_VERTEX = 1
	USAGE_SHADER_CONSTANT = 2
	USAGE_USER = 3

	# Seems to be associated with DISPLAYLIST component semantics.
	USAGE_UNKNOWN = 4

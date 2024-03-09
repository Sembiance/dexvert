from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class BSCPCullingType(BaseEnum):

	"""
	Culling modes for multi bound nodes.
	"""

	__name__ = 'BSCPCullingType'
	_storage = Uint


	# Normal
	CULL_NORMAL = 0

	# All Pass
	CULL_ALLPASS = 1

	# All Fail
	CULL_ALLFAIL = 2

	# Ignore Multi Bounds
	CULL_IGNOREMULTIBOUNDS = 3

	# Force Multi Bounds No Update
	CULL_FORCEMULTIBOUNDSNOUPDATE = 4

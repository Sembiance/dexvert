from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class SortingMode(BaseEnum):

	"""
	Describes the way that NiSortAdjustNode modifies the sorting behavior for the subtree below it.
	"""

	__name__ = 'SortingMode'
	_storage = Uint


	# Inherit. Acts identical to NiNode.
	SORTING_INHERIT = 0

	# Disables sort on all geometry under this node.
	SORTING_OFF = 1

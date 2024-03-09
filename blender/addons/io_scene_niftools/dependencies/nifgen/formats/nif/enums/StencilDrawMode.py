from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class StencilDrawMode(BaseEnum):

	"""
	Describes the face culling options for NiStencilProperty.
	"""

	__name__ = 'StencilDrawMode'
	_storage = Uint


	# Application default, chooses between DRAW_CCW or DRAW_BOTH.
	DRAW_CCW_OR_BOTH = 0

	# Draw only the triangles whose vertices are ordered CCW with respect to the viewer. (Standard behavior)
	DRAW_CCW = 1

	# Draw only the triangles whose vertices are ordered CW with respect to the viewer. (Effectively flips faces)
	DRAW_CW = 2

	# Draw all triangles, regardless of orientation. (Effectively force double-sided)
	DRAW_BOTH = 3

from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class MeshPrimitiveType(BaseEnum):

	"""
	Describes the type of primitives stored in a mesh object.
	"""

	__name__ = 'MeshPrimitiveType'
	_storage = Uint


	# Triangle primitive type.
	MESH_PRIMITIVE_TRIANGLES = 0

	# Triangle strip primitive type.
	MESH_PRIMITIVE_TRISTRIPS = 1

	# Lines primitive type.
	MESH_PRIMITIVE_LINES = 2

	# Line strip primitive type.
	MESH_PRIMITIVE_LINESTRIPS = 3

	# Quadrilateral primitive type.
	MESH_PRIMITIVE_QUADS = 4

	# Point primitive type.
	MESH_PRIMITIVE_POINTS = 5

from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class CoordGenType(BaseEnum):

	"""
	Determines the way that UV texture coordinates are generated.
	"""

	__name__ = 'CoordGenType'
	_storage = Uint


	# Use planar mapping.
	CG_WORLD_PARALLEL = 0

	# Use perspective mapping.
	CG_WORLD_PERSPECTIVE = 1

	# Use spherical mapping.
	CG_SPHERE_MAP = 2

	# Use specular cube mapping. For NiSourceCubeMap only.
	CG_SPECULAR_CUBE_MAP = 3

	# Use diffuse cube mapping. For NiSourceCubeMap only.
	CG_DIFFUSE_CUBE_MAP = 4

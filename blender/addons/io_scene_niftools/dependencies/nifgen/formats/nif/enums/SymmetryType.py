from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class SymmetryType(BaseEnum):

	"""
	Describes the symmetry type of bomb forces.
	"""

	__name__ = 'SymmetryType'
	_storage = Uint


	# Spherical Symmetry.
	SPHERICAL_SYMMETRY = 0

	# Cylindrical Symmetry.
	CYLINDRICAL_SYMMETRY = 1

	# Planar Symmetry.
	PLANAR_SYMMETRY = 2

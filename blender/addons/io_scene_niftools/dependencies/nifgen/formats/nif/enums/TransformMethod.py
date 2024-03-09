from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class TransformMethod(BaseEnum):

	"""
	Describes the order of scaling and rotation matrices. Translate, Scale, Rotation, Center are from TexDesc.
	Back = inverse of Center. FromMaya = inverse of the V axis with a positive translation along V of 1 unit.
	"""

	__name__ = 'TransformMethod'
	_storage = Uint


	# Center * Rotation * Back * Translate * Scale
	MAYA_DEPRECATED = 0

	# Center * Scale * Rotation * Translate * Back
	MAX = 1

	# Center * Rotation * Back * FromMaya * Translate * Scale
	MAYA = 2

from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiExtraData import NiExtraData


class BSBound(NiExtraData):

	"""
	Bethesda-specific collision bounding box for skeletons.
	"""

	__name__ = 'BSBound'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Center of the bounding box.
		self.center = name_type_map['Vector3'](self.context, 0, None)

		# Dimensions of the bounding box from center.
		self.dimensions = name_type_map['Vector3'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'center', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'dimensions', name_type_map['Vector3'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'center', name_type_map['Vector3'], (0, None), (False, None)
		yield 'dimensions', name_type_map['Vector3'], (0, None), (False, None)

	def apply_scale(self, scale):
		"""Scale data."""
		super().apply_scale(scale)
		self.center.x *= scale
		self.center.y *= scale
		self.center.z *= scale
		self.dimensions.x *= scale
		self.dimensions.y *= scale
		self.dimensions.z *= scale


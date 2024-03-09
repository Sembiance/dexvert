from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class HkAabb(BaseStruct):

	"""
	Havok AABB using min/max coordinates instead of center/half extents.
	"""

	__name__ = 'hkAabb'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Coordinates of the corner with the lowest numerical values.
		self.min = name_type_map['Vector4'](self.context, 0, None)

		# Coordinates of the corner with the highest numerical values.
		self.max = name_type_map['Vector4'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'min', name_type_map['Vector4'], (0, None), (False, None), (None, None)
		yield 'max', name_type_map['Vector4'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'min', name_type_map['Vector4'], (0, None), (False, None)
		yield 'max', name_type_map['Vector4'], (0, None), (False, None)

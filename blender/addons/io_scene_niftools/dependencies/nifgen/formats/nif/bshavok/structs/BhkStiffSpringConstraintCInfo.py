from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BhkStiffSpringConstraintCInfo(BaseStruct):

	"""
	bhkStiffSpringConstraint serialization data. Holds two bodies at a specified distance from one another.
	"""

	__name__ = 'bhkStiffSpringConstraintCInfo'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.pivot_a = name_type_map['Vector4'](self.context, 0, None)
		self.pivot_b = name_type_map['Vector4'](self.context, 0, None)
		self.length = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'pivot_a', name_type_map['Vector4'], (0, None), (False, None), (None, None)
		yield 'pivot_b', name_type_map['Vector4'], (0, None), (False, None), (None, None)
		yield 'length', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'pivot_a', name_type_map['Vector4'], (0, None), (False, None)
		yield 'pivot_b', name_type_map['Vector4'], (0, None), (False, None)
		yield 'length', name_type_map['Float'], (0, None), (False, None)

	def apply_scale(self, scale):
		"""Scale data."""
		# apply scale on transform
		self.pivot_a.x *= scale
		self.pivot_a.y *= scale
		self.pivot_a.z *= scale
		self.pivot_b.x *= scale
		self.pivot_b.y *= scale
		self.pivot_b.z *= scale
		self.length *= scale

	def update_a_b(self, transform):
		"""Update B pivot and axes from A using the given transform."""
		# pivot point
		pivot_b = ((self.context.havok_scale * self.pivot_a.get_vector_3()) * transform) / self.context.havok_scale
		self.pivot_b.x = pivot_b.x
		self.pivot_b.y = pivot_b.y
		self.pivot_b.z = pivot_b.z


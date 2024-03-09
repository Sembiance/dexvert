from nifgen.array import Array
from nifgen.formats.nif.bshavok.niobjects.BhkHeightFieldShape import BhkHeightFieldShape
from nifgen.formats.nif.imports import name_type_map


class BhkPlaneShape(BhkHeightFieldShape):

	"""
	Contains a normal and distance from the origin, bounded by a given AABB.
	"""

	__name__ = 'bhkPlaneShape'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unused_01 = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		self.plane_normal = name_type_map['Vector3'](self.context, 0, None)

		# Distance from the origin to the plane.
		self.plane_constant = name_type_map['Float'](self.context, 0, None)
		self.aabb_half_extents = name_type_map['Vector4'](self.context, 0, None)
		self.aabb_center = name_type_map['Vector4'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unused_01', Array, (0, None, (12,), name_type_map['Byte']), (False, None), (None, None)
		yield 'plane_normal', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'plane_constant', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'aabb_half_extents', name_type_map['Vector4'], (0, None), (False, None), (None, None)
		yield 'aabb_center', name_type_map['Vector4'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unused_01', Array, (0, None, (12,), name_type_map['Byte']), (False, None)
		yield 'plane_normal', name_type_map['Vector3'], (0, None), (False, None)
		yield 'plane_constant', name_type_map['Float'], (0, None), (False, None)
		yield 'aabb_half_extents', name_type_map['Vector4'], (0, None), (False, None)
		yield 'aabb_center', name_type_map['Vector4'], (0, None), (False, None)

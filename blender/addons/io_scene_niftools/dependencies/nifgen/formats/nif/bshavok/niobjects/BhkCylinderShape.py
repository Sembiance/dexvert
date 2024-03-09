from nifgen.array import Array
from nifgen.formats.nif.bshavok.niobjects.BhkConvexShape import BhkConvexShape
from nifgen.formats.nif.imports import name_type_map


class BhkCylinderShape(BhkConvexShape):

	"""
	A cylinder.
	"""

	__name__ = 'bhkCylinderShape'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unused_01 = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		self.vertex_a = name_type_map['Vector4'](self.context, 0, None)
		self.vertex_b = name_type_map['Vector4'](self.context, 0, None)
		self.cylinder_radius = name_type_map['Float'](self.context, 0, None)
		self.unused_02 = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unused_01', Array, (0, None, (8,), name_type_map['Byte']), (False, None), (None, None)
		yield 'vertex_a', name_type_map['Vector4'], (0, None), (False, None), (None, None)
		yield 'vertex_b', name_type_map['Vector4'], (0, None), (False, None), (None, None)
		yield 'cylinder_radius', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'unused_02', Array, (0, None, (12,), name_type_map['Byte']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unused_01', Array, (0, None, (8,), name_type_map['Byte']), (False, None)
		yield 'vertex_a', name_type_map['Vector4'], (0, None), (False, None)
		yield 'vertex_b', name_type_map['Vector4'], (0, None), (False, None)
		yield 'cylinder_radius', name_type_map['Float'], (0, None), (False, None)
		yield 'unused_02', Array, (0, None, (12,), name_type_map['Byte']), (False, None)

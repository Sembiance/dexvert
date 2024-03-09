from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class Polygon(BaseStruct):

	"""
	Two dimensional screen elements.
	"""

	__name__ = 'Polygon'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_vertices = name_type_map['Ushort'](self.context, 0, None)

		# Offset in vertex array.
		self.vertex_offset = name_type_map['Ushort'](self.context, 0, None)
		self.num_triangles = name_type_map['Ushort'](self.context, 0, None)

		# Offset in indices array.
		self.triangle_offset = name_type_map['Ushort'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_vertices', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'vertex_offset', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'num_triangles', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'triangle_offset', name_type_map['Ushort'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_vertices', name_type_map['Ushort'], (0, None), (False, None)
		yield 'vertex_offset', name_type_map['Ushort'], (0, None), (False, None)
		yield 'num_triangles', name_type_map['Ushort'], (0, None), (False, None)
		yield 'triangle_offset', name_type_map['Ushort'], (0, None), (False, None)

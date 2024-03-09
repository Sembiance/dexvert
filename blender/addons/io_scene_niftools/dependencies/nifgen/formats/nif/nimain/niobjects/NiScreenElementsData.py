from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiTriShapeData import NiTriShapeData


class NiScreenElementsData(NiTriShapeData):

	"""
	DEPRECATED (20.5), functionality included in NiMeshScreenElements.
	Two dimensional screen elements.
	"""

	__name__ = 'NiScreenElementsData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.max_polygons = name_type_map['Ushort'](self.context, 0, None)
		self.polygons = Array(self.context, 0, None, (0,), name_type_map['Polygon'])
		self.polygon_indices = Array(self.context, 0, None, (0,), name_type_map['Ushort'])
		self.polygon_grow_by = name_type_map['Ushort'].from_value(1)
		self.num_polygons = name_type_map['Ushort'](self.context, 0, None)
		self.max_vertices = name_type_map['Ushort'](self.context, 0, None)
		self.vertices_grow_by = name_type_map['Ushort'].from_value(1)
		self.max_indices = name_type_map['Ushort'](self.context, 0, None)
		self.indices_grow_by = name_type_map['Ushort'].from_value(1)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'max_polygons', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'polygons', Array, (0, None, (None,), name_type_map['Polygon']), (False, None), (None, None)
		yield 'polygon_indices', Array, (0, None, (None,), name_type_map['Ushort']), (False, None), (None, None)
		yield 'polygon_grow_by', name_type_map['Ushort'], (0, None), (False, 1), (None, None)
		yield 'num_polygons', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'max_vertices', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'vertices_grow_by', name_type_map['Ushort'], (0, None), (False, 1), (None, None)
		yield 'max_indices', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'indices_grow_by', name_type_map['Ushort'], (0, None), (False, 1), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'max_polygons', name_type_map['Ushort'], (0, None), (False, None)
		yield 'polygons', Array, (0, None, (instance.max_polygons,), name_type_map['Polygon']), (False, None)
		yield 'polygon_indices', Array, (0, None, (instance.max_polygons,), name_type_map['Ushort']), (False, None)
		yield 'polygon_grow_by', name_type_map['Ushort'], (0, None), (False, 1)
		yield 'num_polygons', name_type_map['Ushort'], (0, None), (False, None)
		yield 'max_vertices', name_type_map['Ushort'], (0, None), (False, None)
		yield 'vertices_grow_by', name_type_map['Ushort'], (0, None), (False, 1)
		yield 'max_indices', name_type_map['Ushort'], (0, None), (False, None)
		yield 'indices_grow_by', name_type_map['Ushort'], (0, None), (False, 1)

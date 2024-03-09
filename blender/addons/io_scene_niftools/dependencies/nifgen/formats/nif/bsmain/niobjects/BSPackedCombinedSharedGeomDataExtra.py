from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiExtraData import NiExtraData


class BSPackedCombinedSharedGeomDataExtra(NiExtraData):

	"""
	Fallout 4 Packed Combined Shared Geometry Data.
	Geometry is NOT baked into the file. It is instead a reference to the geometry via a CSG filename hash and data offset.
	"""

	__name__ = 'BSPackedCombinedSharedGeomDataExtra'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.vertex_desc = name_type_map['BSVertexDesc'](self.context, 0, None)
		self.num_vertices = name_type_map['Uint'](self.context, 0, None)
		self.num_triangles = name_type_map['Uint'](self.context, 0, None)
		self.unknown_flags_1 = name_type_map['Uint'](self.context, 0, None)
		self.unknown_flags_2 = name_type_map['Uint'](self.context, 0, None)
		self.num_data = name_type_map['Uint'](self.context, 0, None)
		self.object = Array(self.context, 0, None, (0,), name_type_map['BSPackedGeomObject'])
		self.object_data = Array(self.context, 0, None, (0,), name_type_map['BSPackedSharedGeomData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'vertex_desc', name_type_map['BSVertexDesc'], (0, None), (False, None), (None, None)
		yield 'num_vertices', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_triangles', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unknown_flags_1', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unknown_flags_2', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_data', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'object', Array, (0, None, (None,), name_type_map['BSPackedGeomObject']), (False, None), (None, None)
		yield 'object_data', Array, (0, None, (None,), name_type_map['BSPackedSharedGeomData']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'vertex_desc', name_type_map['BSVertexDesc'], (0, None), (False, None)
		yield 'num_vertices', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_triangles', name_type_map['Uint'], (0, None), (False, None)
		yield 'unknown_flags_1', name_type_map['Uint'], (0, None), (False, None)
		yield 'unknown_flags_2', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_data', name_type_map['Uint'], (0, None), (False, None)
		yield 'object', Array, (0, None, (instance.num_data,), name_type_map['BSPackedGeomObject']), (False, None)
		yield 'object_data', Array, (0, None, (instance.num_data,), name_type_map['BSPackedSharedGeomData']), (False, None)

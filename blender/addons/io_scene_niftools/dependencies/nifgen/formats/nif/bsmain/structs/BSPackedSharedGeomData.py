from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BSPackedSharedGeomData(BaseStruct):

	__name__ = 'BSPackedSharedGeomData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_verts = name_type_map['Uint'](self.context, 0, None)
		self.lod_levels = name_type_map['Uint'](self.context, 0, None)
		self.tri_count_lod_0 = name_type_map['Uint'](self.context, 0, None)
		self.tri_offset_lod_0 = name_type_map['Uint'](self.context, 0, None)
		self.tri_count_lod_1 = name_type_map['Uint'](self.context, 0, None)
		self.tri_offset_lod_1 = name_type_map['Uint'](self.context, 0, None)
		self.tri_count_lod_2 = name_type_map['Uint'](self.context, 0, None)
		self.tri_offset_lod_2 = name_type_map['Uint'](self.context, 0, None)
		self.num_combined = name_type_map['Uint'](self.context, 0, None)
		self.combined = Array(self.context, 0, None, (0,), name_type_map['BSPackedGeomDataCombined'])
		self.vertex_desc = name_type_map['BSVertexDesc'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_verts', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'lod_levels', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'tri_count_lod_0', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'tri_offset_lod_0', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'tri_count_lod_1', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'tri_offset_lod_1', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'tri_count_lod_2', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'tri_offset_lod_2', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_combined', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'combined', Array, (0, None, (None,), name_type_map['BSPackedGeomDataCombined']), (False, None), (None, None)
		yield 'vertex_desc', name_type_map['BSVertexDesc'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_verts', name_type_map['Uint'], (0, None), (False, None)
		yield 'lod_levels', name_type_map['Uint'], (0, None), (False, None)
		yield 'tri_count_lod_0', name_type_map['Uint'], (0, None), (False, None)
		yield 'tri_offset_lod_0', name_type_map['Uint'], (0, None), (False, None)
		yield 'tri_count_lod_1', name_type_map['Uint'], (0, None), (False, None)
		yield 'tri_offset_lod_1', name_type_map['Uint'], (0, None), (False, None)
		yield 'tri_count_lod_2', name_type_map['Uint'], (0, None), (False, None)
		yield 'tri_offset_lod_2', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_combined', name_type_map['Uint'], (0, None), (False, None)
		yield 'combined', Array, (0, None, (instance.num_combined,), name_type_map['BSPackedGeomDataCombined']), (False, None)
		yield 'vertex_desc', name_type_map['BSVertexDesc'], (0, None), (False, None)

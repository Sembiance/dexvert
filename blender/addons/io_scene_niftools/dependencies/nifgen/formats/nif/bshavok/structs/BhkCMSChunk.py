from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BhkCMSChunk(BaseStruct):

	"""
	Bethesda extension of hkpCompressedMeshShape::Chunk. A compressed chunk of hkpCompressedMeshShape geometry.
	"""

	__name__ = 'bhkCMSChunk'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.translation = name_type_map['Vector4'](self.context, 0, None)

		# Index of material in bhkCompressedMeshShapeData::Chunk Materials
		self.material_index = name_type_map['Uint'](self.context, 0, None)

		# Index of another chunk in the chunks list.
		self.reference = name_type_map['Ushort'].from_value(65535)

		# Index of transformation in bhkCompressedMeshShapeData::Chunk Transforms
		self.transform_index = name_type_map['Ushort'](self.context, 0, None)

		# Number of vertices, multiplied by 3.
		self.num_vertices = name_type_map['Uint'](self.context, 0, None)

		# Vertex positions in havok coordinates*1000.
		self.vertices = Array(self.context, 0, None, (0,), name_type_map['UshortVector3'])
		self.num_indices = name_type_map['Uint'](self.context, 0, None)

		# Vertex indices as used by strips.
		self.indices = Array(self.context, 0, None, (0,), name_type_map['Ushort'])
		self.num_strips = name_type_map['Uint'](self.context, 0, None)

		# Length of strips longer than one triangle.
		self.strips = Array(self.context, 0, None, (0,), name_type_map['Ushort'])

		# Generally the same as Num Indices field.
		self.num_welding_info = name_type_map['Uint'](self.context, 0, None)
		self.welding_info = Array(self.context, 0, None, (0,), name_type_map['BhkWeldInfo'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'translation', name_type_map['Vector4'], (0, None), (False, None), (None, None)
		yield 'material_index', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'reference', name_type_map['Ushort'], (0, None), (False, 65535), (None, None)
		yield 'transform_index', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'num_vertices', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'vertices', Array, (0, None, (None,), name_type_map['UshortVector3']), (False, None), (None, None)
		yield 'num_indices', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'indices', Array, (0, None, (None,), name_type_map['Ushort']), (False, None), (None, None)
		yield 'num_strips', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'strips', Array, (0, None, (None,), name_type_map['Ushort']), (False, None), (None, None)
		yield 'num_welding_info', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'welding_info', Array, (0, None, (None,), name_type_map['BhkWeldInfo']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'translation', name_type_map['Vector4'], (0, None), (False, None)
		yield 'material_index', name_type_map['Uint'], (0, None), (False, None)
		yield 'reference', name_type_map['Ushort'], (0, None), (False, 65535)
		yield 'transform_index', name_type_map['Ushort'], (0, None), (False, None)
		yield 'num_vertices', name_type_map['Uint'], (0, None), (False, None)
		yield 'vertices', Array, (0, None, (int(instance.num_vertices / 3),), name_type_map['UshortVector3']), (False, None)
		yield 'num_indices', name_type_map['Uint'], (0, None), (False, None)
		yield 'indices', Array, (0, None, (instance.num_indices,), name_type_map['Ushort']), (False, None)
		yield 'num_strips', name_type_map['Uint'], (0, None), (False, None)
		yield 'strips', Array, (0, None, (instance.num_strips,), name_type_map['Ushort']), (False, None)
		yield 'num_welding_info', name_type_map['Uint'], (0, None), (False, None)
		yield 'welding_info', Array, (0, None, (instance.num_welding_info,), name_type_map['BhkWeldInfo']), (False, None)

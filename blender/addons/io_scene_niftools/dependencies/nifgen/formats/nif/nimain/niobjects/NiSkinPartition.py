from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiSkinPartition(NiObject):

	"""
	Skinning data, optimized for hardware skinning. The mesh is partitioned in submeshes such that each vertex of a submesh is influenced only by a limited and fixed number of bones.
	"""

	__name__ = 'NiSkinPartition'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_partitions = name_type_map['Uint'](self.context, 0, None)
		self.data_size = name_type_map['Uint'](self.context, 0, None)
		self.vertex_size = name_type_map['Uint'](self.context, 0, None)
		self.vertex_desc = name_type_map['BSVertexDesc'](self.context, 0, None)
		self.vertex_data = Array(self.context, self.vertex_desc >> 44, None, (0,), name_type_map['BSVertexDataSSE'])
		self.partitions = Array(self.context, 0, None, (0,), name_type_map['SkinPartition'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_partitions', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'data_size', name_type_map['Uint'], (0, None), (False, None), (lambda context: 335675399 <= context.version <= 335675399 and context.bs_header.bs_version == 100, None)
		yield 'vertex_size', name_type_map['Uint'], (0, None), (False, None), (lambda context: 335675399 <= context.version <= 335675399 and context.bs_header.bs_version == 100, None)
		yield 'vertex_desc', name_type_map['BSVertexDesc'], (0, None), (False, None), (lambda context: 335675399 <= context.version <= 335675399 and context.bs_header.bs_version == 100, None)
		yield 'vertex_data', Array, (None, None, (None,), name_type_map['BSVertexDataSSE']), (False, None), (lambda context: 335675399 <= context.version <= 335675399 and context.bs_header.bs_version == 100, True)
		yield 'partitions', Array, (0, None, (None,), name_type_map['SkinPartition']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_partitions', name_type_map['Uint'], (0, None), (False, None)
		if 335675399 <= instance.context.version <= 335675399 and instance.context.bs_header.bs_version == 100:
			yield 'data_size', name_type_map['Uint'], (0, None), (False, None)
			yield 'vertex_size', name_type_map['Uint'], (0, None), (False, None)
			yield 'vertex_desc', name_type_map['BSVertexDesc'], (0, None), (False, None)
		if 335675399 <= instance.context.version <= 335675399 and instance.context.bs_header.bs_version == 100 and instance.data_size > 0:
			yield 'vertex_data', Array, (instance.vertex_desc >> 44, None, (int(instance.data_size / instance.vertex_size),), name_type_map['BSVertexDataSSE']), (False, None)
		yield 'partitions', Array, (0, None, (instance.num_partitions,), name_type_map['SkinPartition']), (False, None)

	def apply_scale(self, scale):
		for v_data in self.vertex_data:
			v = v_data.vertex
			v.x *= scale
			v.y *= scale
			v.z *= scale

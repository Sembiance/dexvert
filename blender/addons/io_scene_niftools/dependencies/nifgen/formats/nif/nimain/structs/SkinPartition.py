from nifgen.utils.tristrip import triangulate
from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class SkinPartition(BaseStruct):

	"""
	Skinning data for a submesh, optimized for hardware skinning. Part of NiSkinPartition.
	"""

	__name__ = 'SkinPartition'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Number of vertices in this submesh.
		self.num_vertices = name_type_map['Ushort'](self.context, 0, None)

		# Number of triangles in this submesh.
		self.num_triangles = name_type_map['Ushort'](self.context, 0, None)

		# Number of bones influencing this submesh.
		self.num_bones = name_type_map['Ushort'](self.context, 0, None)

		# Number of strips in this submesh (zero if not stripped).
		self.num_strips = name_type_map['Ushort'](self.context, 0, None)

		# Number of weight coefficients per vertex. The Gamebryo engine seems to work well only if this number is equal to 4, even if there are less than 4 influences per vertex.
		self.num_weights_per_vertex = name_type_map['Ushort'].from_value(4)

		# List of bones.
		self.bones = Array(self.context, 0, None, (0,), name_type_map['Ushort'])

		# Do we have a vertex map?
		self.has_vertex_map = name_type_map['Bool'](self.context, 0, None)

		# Maps the weight/influence lists in this submesh to the vertices in the shape being skinned.
		self.vertex_map = Array(self.context, 0, None, (0,), name_type_map['Ushort'])

		# Do we have vertex weights?
		# 1 (default): vertex weights are stored in floats.
		# 15 (compression): vertex weights are stored in half floats (found in 20.3.1.1 Fantasy Frontier Online).
		self.has_vertex_weights = name_type_map['Bool'](self.context, 0, None)

		# The vertex weights.
		self.vertex_weights = Array(self.context, 0, None, (0,), name_type_map['Hfloat'])

		# The strip lengths.
		self.strip_lengths = Array(self.context, 0, None, (0,), name_type_map['Ushort'])

		# Do we have triangle or strip data?
		self.has_faces = name_type_map['Bool'](self.context, 0, None)

		# The strips.
		self.strips = Array(self.context, 0, None, (0,), name_type_map['Ushort'])

		# The triangles.
		self.triangles = Array(self.context, 0, None, (0,), name_type_map['Triangle'])

		# Do we have bone indices?
		self.has_bone_indices = name_type_map['Bool'](self.context, 0, None)

		# Bone indices, they index into 'Bones'.
		self.bone_indices = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		self.lod_level = name_type_map['Byte'](self.context, 0, None)
		self.global_vb = name_type_map['Bool'](self.context, 0, None)
		self.vertex_desc = name_type_map['BSVertexDesc'](self.context, 0, None)
		self.triangles_copy = Array(self.context, 0, None, (0,), name_type_map['Triangle'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_vertices', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'num_triangles', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'num_bones', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'num_strips', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'num_weights_per_vertex', name_type_map['Ushort'], (0, None), (False, 4), (None, None)
		yield 'bones', Array, (0, None, (None,), name_type_map['Ushort']), (False, None), (None, None)
		yield 'has_vertex_map', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version >= 167837696, None)
		yield 'vertex_map', Array, (0, None, (None,), name_type_map['Ushort']), (False, None), (lambda context: context.version <= 167772418, None)
		yield 'vertex_map', Array, (0, None, (None,), name_type_map['Ushort']), (False, None), (lambda context: context.version >= 167837696, True)
		yield 'has_vertex_weights', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version >= 167837696, None)
		yield 'vertex_weights', Array, (0, None, (None, None,), name_type_map['Float']), (False, None), (lambda context: context.version <= 167772418, None)
		yield 'vertex_weights', Array, (0, None, (None, None,), name_type_map['Float']), (False, None), (lambda context: context.version >= 167837696, True)
		yield 'vertex_weights', Array, (0, None, (None, None,), name_type_map['Hfloat']), (False, None), (lambda context: context.version >= 335741185, True)
		yield 'strip_lengths', Array, (0, None, (None,), name_type_map['Ushort']), (False, None), (None, None)
		yield 'has_faces', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version >= 167837696, None)
		yield 'strips', Array, (0, None, (None, None,), name_type_map['Ushort']), (False, None), (lambda context: context.version <= 167772418, True)
		yield 'strips', Array, (0, None, (None, None,), name_type_map['Ushort']), (False, None), (lambda context: context.version >= 167837696, True)
		yield 'triangles', Array, (0, None, (None,), name_type_map['Triangle']), (False, None), (lambda context: context.version <= 167772418, True)
		yield 'triangles', Array, (0, None, (None,), name_type_map['Triangle']), (False, None), (lambda context: context.version >= 167837696, True)
		yield 'has_bone_indices', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'bone_indices', Array, (0, None, (None, None,), name_type_map['Byte']), (False, None), (None, True)
		yield 'lod_level', name_type_map['Byte'], (0, None), (False, None), (lambda context: 335675399 <= context.version <= 335675399 and context.bs_header.bs_version > 34, None)
		yield 'global_vb', name_type_map['Bool'], (0, None), (False, None), (lambda context: 335675399 <= context.version <= 335675399 and context.bs_header.bs_version > 34, None)
		yield 'vertex_desc', name_type_map['BSVertexDesc'], (0, None), (False, None), (lambda context: 335675399 <= context.version <= 335675399 and context.bs_header.bs_version == 100, None)
		yield 'triangles_copy', Array, (0, None, (None,), name_type_map['Triangle']), (False, None), (lambda context: 335675399 <= context.version <= 335675399 and context.bs_header.bs_version == 100, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_vertices', name_type_map['Ushort'], (0, None), (False, None)
		yield 'num_triangles', name_type_map['Ushort'], (0, None), (False, None)
		yield 'num_bones', name_type_map['Ushort'], (0, None), (False, None)
		yield 'num_strips', name_type_map['Ushort'], (0, None), (False, None)
		yield 'num_weights_per_vertex', name_type_map['Ushort'], (0, None), (False, 4)
		yield 'bones', Array, (0, None, (instance.num_bones,), name_type_map['Ushort']), (False, None)
		if instance.context.version >= 167837696:
			yield 'has_vertex_map', name_type_map['Bool'], (0, None), (False, None)
		if instance.context.version <= 167772418:
			yield 'vertex_map', Array, (0, None, (instance.num_vertices,), name_type_map['Ushort']), (False, None)
		if instance.context.version >= 167837696 and instance.has_vertex_map:
			yield 'vertex_map', Array, (0, None, (instance.num_vertices,), name_type_map['Ushort']), (False, None)
		if instance.context.version >= 167837696:
			yield 'has_vertex_weights', name_type_map['Bool'], (0, None), (False, None)
		if instance.context.version <= 167772418:
			yield 'vertex_weights', Array, (0, None, (instance.num_vertices, instance.num_weights_per_vertex,), name_type_map['Float']), (False, None)
		if instance.context.version >= 167837696 and (instance.has_vertex_weights > 0) and (instance.has_vertex_weights != 15):
			yield 'vertex_weights', Array, (0, None, (instance.num_vertices, instance.num_weights_per_vertex,), name_type_map['Float']), (False, None)
		if instance.context.version >= 335741185 and instance.has_vertex_weights == 15:
			yield 'vertex_weights', Array, (0, None, (instance.num_vertices, instance.num_weights_per_vertex,), name_type_map['Hfloat']), (False, None)
		yield 'strip_lengths', Array, (0, None, (instance.num_strips,), name_type_map['Ushort']), (False, None)
		if instance.context.version >= 167837696:
			yield 'has_faces', name_type_map['Bool'], (0, None), (False, None)
		if instance.context.version <= 167772418 and instance.num_strips != 0:
			yield 'strips', Array, (0, None, (instance.num_strips, instance.strip_lengths,), name_type_map['Ushort']), (False, None)
		if instance.context.version >= 167837696 and instance.has_faces and (instance.num_strips != 0):
			yield 'strips', Array, (0, None, (instance.num_strips, instance.strip_lengths,), name_type_map['Ushort']), (False, None)
		if instance.context.version <= 167772418 and instance.num_strips == 0:
			yield 'triangles', Array, (0, None, (instance.num_triangles,), name_type_map['Triangle']), (False, None)
		if instance.context.version >= 167837696 and instance.has_faces and (instance.num_strips == 0):
			yield 'triangles', Array, (0, None, (instance.num_triangles,), name_type_map['Triangle']), (False, None)
		yield 'has_bone_indices', name_type_map['Bool'], (0, None), (False, None)
		if instance.has_bone_indices:
			yield 'bone_indices', Array, (0, None, (instance.num_vertices, instance.num_weights_per_vertex,), name_type_map['Byte']), (False, None)
		if 335675399 <= instance.context.version <= 335675399 and instance.context.bs_header.bs_version > 34:
			yield 'lod_level', name_type_map['Byte'], (0, None), (False, None)
			yield 'global_vb', name_type_map['Bool'], (0, None), (False, None)
		if 335675399 <= instance.context.version <= 335675399 and instance.context.bs_header.bs_version == 100:
			yield 'vertex_desc', name_type_map['BSVertexDesc'], (0, None), (False, None)
			yield 'triangles_copy', Array, (0, None, (instance.num_triangles,), name_type_map['Triangle']), (False, None)
	
	def get_triangles(self):
		"""Get list of triangles of this partition.
		"""
		# strips?
		if self.num_strips:
			for tri in triangulate(self.strips):
				yield tri
		# no strips, do triangles
		else:
			for tri in self.triangles:
				yield (tri.v_1, tri.v_2, tri.v_3)

	def get_mapped_triangles(self):
		"""Get list of triangles of this partition (mapping into the
		geometry data vertex list).
		"""
		for tri in self.get_triangles():
			yield tuple(self.vertex_map[v_index] for v_index in tri)

